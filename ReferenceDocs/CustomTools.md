Parent: [Reference Docs](README.md)

# Custom Tools

In-editor **console commands** written for the Sundance maintenance work. Unlike the
[builders & commandlets](BuildersAndCommandlets.md) (which run headless through
`WorldPartitionBuilderCommandlet`), these are interactive `FAutoConsoleCommand`s: you
type them into the editor console (`~`) with the target level already open, and they act
on the currently loaded editor world.

They live in the `WorldBuildingEditor` module
(`D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\`).

| Command | Purpose |
|---------|---------|
| [`Editor.FixRuntimeGridReferenceErrors`](#editorfixruntimegridreferenceerrors) | Fix `WorldPartitionChangelistValidator` "different runtime grid" reference errors from a log file |

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

## See also

- [World Partition rules](WorldPartitionRules.md) — why `ExcludeFromRules` freezes a value
- [Runtime Grid rules](WorldPartitionRulesAnalysis/RuntimeGridRules.md) — how `RuntimeGrid` is normally applied
- [Builders & commandlets](BuildersAndCommandlets.md) — the headless counterpart tools
- [Perforce source control](PerforceSourceControl.md) — checkout-before-save, changelists
