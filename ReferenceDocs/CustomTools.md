Parent: [Reference Docs](README.md)

# Custom Tools

In-editor **tools** written for the Sundance maintenance work. Unlike the
[builders & commandlets](BuildersAndCommandlets.md) (which run headless through
`WorldPartitionBuilderCommandlet`), these are **interactive** and act on the currently
loaded editor world. Two kinds live here:

- **Console commands** — interactive `FAutoConsoleCommand`s you type into the editor
  console (`~`) with the target level already open.
- **Editor-mode UI tools** — buttons and dialogs surfaced inside a dedicated editor mode.

| Tool | Kind | Purpose |
|------|------|---------|
| [`Editor.FixRuntimeGridReferenceErrors`](#editorfixruntimegridreferenceerrors) | Console command | Fix `WorldPartitionChangelistValidator` "different runtime grid" reference errors from a log file |
| [Delete World Event](#delete-world-event-world-events-editor-mode) | Editor-mode UI | Fully delete a World Event (locator + level instances + data layers) from the Overland with live progress and rollback |

---

## `Editor.FixRuntimeGridReferenceErrors`

Source: `D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\RuntimeGridReferenceFixup.cpp`
· log category `LogRuntimeGridRefFix`.

Reads a log file containing `WorldPartitionChangelistValidator` runtime-grid reference
errors and, for every **referencer / referee couple**, aligns the referee's `RuntimeGrid`
to the referencer's, tags **both** actors with `ExcludeFromRules`, saves the packages,
and checks them out into a single descriptive Perforce changelist. Processing is
**atomic per couple**: if either side fails, that couple's files are reverted.

### Why it exists

The validator flags an actor that references another actor sitting on a *different*
`RuntimeGrid`. The desired resolution is to bring the referee onto the referencer's grid
and then freeze both actors so the [World Partition rule system](WorldPartitionRules.md)
does not overwrite the value on the next save. Freezing is done with the
`ExcludeFromRules` actor tag — the same tag the rule subsystems honor
(`UWorldPartitionRuleSettings::ActorTagExcludedFromRules`, defaulting to
`"ExcludeFromRules"`). Doing this by hand across dozens of couples, some nested inside
Level Instances, is error-prone; this command batches it from the validator log.

### Usage

```
Editor.FixRuntimeGridReferenceErrors <LogFilePath> [-DryRun]
```

| Argument | Meaning |
|----------|---------|
| `<LogFilePath>` | Path to a text file containing the validator error lines (required, positional). |
| `-DryRun` | Parse + resolve + report **only**; no `Modify`, no save, no checkout, no changelist. |

- The command must run **in the editor** (`GEditor` present) with the level that
  contains the actors **already open**; it operates on
  `GEditor->GetEditorWorldContext().World()`, which must be a World Partition world.
- Duplicate couples in the log are de-duplicated on `(ReferencerPath, RefereePath)`.

Example:

```
Editor.FixRuntimeGridReferenceErrors D:/Logs/RuntimeGridErrors.txt -DryRun
```

### Accepted log formats

Two line shapes are parsed; any other line is ignored
(`RuntimeGridReferenceFixup.cpp:110`):

| Format | Example line | Referencer / Referee |
|--------|--------------|----------------------|
| **A** | `<Referencer> (<pkg>) is referencing <Referee> (<pkg>) but both actors are using a different runtime grid.` | first `/Game/...` token / token after `is referencing ` |
| **B** | `Actor /Game/Developers/.../LevelA.NewBlueprint references an actor in a different runtime grid /Game/Developers/.../LevelA.BlockingVolume` | first `/Game/...` token / token after the marker |

```112:114:D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\RuntimeGridReferenceFixup.cpp
		static const FString FormatA_Marker = TEXT("but both actors are using a different runtime grid");
		static const FString FormatA_Referencing = TEXT("is referencing ");
		static const FString FormatB_Marker = TEXT("references an actor in a different runtime grid");
```

Actor tokens are extracted as the first `/Game/...` substring stopping at the first
whitespace or parenthesis, and matched against loaded actors by their reconstructed path
`"<SoftPathLongPackageName>.<ActorLabelOrName>"` (exactly what the validator prints), with
a fallback match on the label alone.

### What it does per couple

For each couple whose **both** endpoints are found together in a loaded container:

1. `Referee->SetRuntimeGrid(Referencer->GetRuntimeGrid())` — only if they actually differ.
2. `Referencer->Tags.AddUnique("ExcludeFromRules")` — if not already tagged.
3. `Referee->Tags.AddUnique("ExcludeFromRules")` — if not already tagged.
4. Each modified package is checked out silently and saved.

Every setter is guarded by an equality/`Contains` check, so already-compliant actors
produce **no** dirty package and never enter the changelist.

### Level Instance recursion

Couples whose actors are **not** both present in the top-level world are retried inside
child Level Instances. The command opens each partitioned Level Instance in an edit scope
(`FLevelInstanceEditScope`, mirroring the pattern in
[`UForceHLODExcludeFromLogBuilder`](BuildersAndCommandlets.md)), fixes any couple that
resolves there, then recurses deeper. The edit scope commits with
`bDiscardEdits=true` — the changes are persisted by saving the external-actor packages
directly, not through the transient Level Instance edit.

### Atomic per-couple processing (revert on failure)

The two actors go together as a couple. If **either or both** sides hit a problem during
processing, that couple's files are rolled back so a half-fixed reference is never left
behind. This is implemented per container in phases:

1. **Apply in memory** — all resolvable couples get their grid/tag changes, and each
   touched file's original state is recorded (original grid, whether the tag was added).
2. **Check out + save** each modified file once. Per-file status: unchanged / saved / failed.
3. **Couple verdict** — a couple **succeeds only if both of its files are OK**; otherwise
   it is marked failed.
4. **Revert** — any modified file **not committed by at least one successful couple** is
   reverted on disk (`USourceControlHelpers::RevertFiles`, silent) and restored in memory
   (grid reset, tag removed, dirty flag cleared).

> ⚠ Shared referencer: one referencer often appears in several couples (it only ever
> receives the idempotent `ExcludeFromRules` tag). A file is **kept if at least one couple
> using it succeeds**, and **reverted only if every couple using it fails**. So a failing
> couple reverts its own referee (unique to it) without breaking sibling couples that
> share the same referencer.

### Source control

Checkout is fully **automatic and silent** — no "Check Out Assets" dialog:

- `USourceControlHelpers::CheckOutOrAddFiles(..., bSilent=true)` before saving.
- The save uses `FEditorFileUtils::PromptForCheckoutAndSave` with `bPromptToSave=false`
  and `bAlreadyCheckedOut=true` to suppress the interactive checkout prompt.
- All committed files are then moved into a **new changelist** (`FNewChangelist`) whose
  description states exactly what was done, couple by couple (successful couples only).
- If source control is disabled, saved files are simply left in the default changelist
  (a warning is logged).

### Report

After the run a full report is both logged (`LogRuntimeGridRefFix`, `Display`) and written
to disk next to the input log as `<LogFilePath>.report.txt`. Per couple it lists the
container, referencer/referee labels, the `RuntimeGrid` **old → new** transition, which
side got the tag, and the status: `OK`, `FAILED - ROLLED BACK (files reverted)`, or
`UNRESOLVED` (both actors never found together — handle manually). The summary reports
couples succeeded / failed-reverted / unresolved, grids aligned, tags added, actors
modified, files committed, and files reverted.

### Registration

```896:904:D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\RuntimeGridReferenceFixup.cpp
static FAutoConsoleCommand FixRuntimeGridReferenceErrorsCmd(
	TEXT("Editor.FixRuntimeGridReferenceErrors"),
	TEXT("Fix WorldPartitionChangelistValidator 'different runtime grid' reference errors listed in a log file. ")
	TEXT("For each referencer/referee couple it aligns the referee's RuntimeGrid to the referencer's, tags both actors ")
	TEXT("with the ExcludeFromRules tag, saves them, and checks them out into a described Perforce changelist. If either ")
	TEXT("actor of a couple fails, that couple's files are reverted. A full report is logged and written next to the log ")
	TEXT("file. Params: <LogFilePath> [-DryRun]. The level containing the actors must be open."),
	FConsoleCommandWithArgsDelegate::CreateStatic(&WorldBuildingEditor::RuntimeGridReferenceFixup::FixFromLog)
);
```

## Delete World Event (World Events Editor Mode)

**A one-click, guided dialog that fully deletes a World Event and every asset it created
(locator, level instance(s), data layer instance(s) and data layer asset(s)) from the
Overland, with live per-step progress and a full rollback on failure.**

Source: `D:\Sun\Sundance\Source\SundanceEditor\WorldEvents\EditorMode\Deletion\`
(`WorldEventDeleter.h/.cpp`, `SWorldEventDeleteDialog.h/.cpp`) · entry point in
`WorldEventEditorModeToolkit.cpp` · log category `LogWorldEventEditorMode`
(lines prefixed `[WE Delete]`). Jira: **SUNDANCE-40173**.

### Why it exists

Deleting a World Event by hand is tedious and error-prone because placing one creates a
web of references: a `WorldEventLocator` actor, one `WorldEventInstance` (Level Instance)
per definition, a `DataLayerAsset` in the Content Browser, and the matching data layer
**instance(s)** registered in `WorldDataLayers` (and, when the event sits inside a Level
Instance such as Hogwarts/Hogsmeade, a second instance in that hierarchy). The manual
procedure — documented in confluence *"Deleting World Events from the Overland"* — is a
strict ordered sequence of deletions ending with 4–5 files in a changelist. Missing a
step leaves dangling references. This tool automates the whole procedure safely.

### How to open it

1. Enter the **World Events** editor mode.
2. In the **Manage** tab, select the target Locator (or one of its entries) in the tree.
3. Click the red **"Delete World Event..."** button. The guided dialog opens.

Nothing is modified until you press **Begin deletion**.

### The dialog

A polished, self-explanatory modal wizard:

- **Header** — warning icon, the World Event name, and a plain-language summary.
- **"What will be deleted"** — a transparent, up-front inventory of every actor, data
  layer instance, data layer asset, and the number of Perforce files that will be touched.
- **Steps** — the ordered list below; each row shows a live **spinner → green tick ✓ /
  red cross ✗** plus a status message.
- **Detailed log** — a collapsible, scrollable log of everything that happened.
- **Buttons** — `Begin deletion` (explicit confirmation), `Cancel`, and — only after a
  failure — `Undo everything`.

### What it does (steps)

The steps map 1:1 onto the manual confluence procedure:

1. **Validate references & Perforce state** — every impacted file must be source
   controlled, up to date, and not checked out by someone else. Nothing is modified.
2. **Check out the World Data Layers** (and level).
3. **Remove the World Event data layers** — deletes the data layer instance(s) from the
   `DL_World_Events` hierarchy (and the Level Instance hierarchy when applicable).
4. **Delete the World Event actors** — the Level Instance(s) and the Locator.
5. **Save & mark deletions in Perforce** — saves the modified `WorldDataLayers` and marks
   the deleted actor packages for delete.
6. **Delete the Data Layer assets** — from the Content Browser, now unreferenced.
7. **Move changes to a described changelist** — all impacted files are moved into a new
   Perforce changelist whose description lists exactly what was deleted and why.

### Error handling & rollback

The design is **atomic**: if any step fails, nothing is left half-done.

- All fallible preconditions are checked in step 1, **before** any change.
- On failure the dialog turns red, names the failing step and the reason, and offers a
  single **"Undo everything"** button.
- Rollback reverts **every** touched Perforce file (`USourceControlHelpers::RevertFiles`)
  and — if the in-editor world was already mutated — **reloads the level** so the editor
  returns exactly to its pre-deletion state.

### Source control

- Checkout is automatic and silent (`USourceControlHelpers::CheckOutOrAddFiles`).
- Success moves all files into a new **described** changelist (`FNewChangelist`).
- **Nothing is ever submitted automatically** — you review and submit the changelist
  yourself.

### Scope & notes

- Granularity is the **whole Locator**: it deletes the locator and everything it created.
- The reusable `WorldEventDefinition` data asset is **not** deleted (it is shared).
- Failure to move files to the described changelist (step 7) is treated as a **non-fatal
  warning** — the deletion still succeeded and the files remain in the default changelist.

---

## See also

- [World Events (work-done narrative)](../WorkDoneByTopic/WorldEvents.md) — the World Events system context
- [World Partition rules](WorldPartitionRules.md) — why `ExcludeFromRules` freezes a value
- [Runtime Grid rules](WorldPartitionRulesAnalysis/RuntimeGridRules.md) — how `RuntimeGrid` is normally applied
- [Builders & commandlets](BuildersAndCommandlets.md) — the headless counterpart tools
- [Perforce source control](PerforceSourceControl.md) — checkout-before-save, changelists
- [Level Instances & OFPA](LevelInstancesAndOFPA.md) — external actor packages & Level Instance editing
