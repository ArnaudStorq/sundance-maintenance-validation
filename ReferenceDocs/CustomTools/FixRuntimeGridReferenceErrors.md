Parent: [Custom Tools](../CustomTools.md)

# `Editor.FixRuntimeGridReferenceErrors`

An interactive console command (`FAutoConsoleCommand`) you type into the editor
console (`~`). It fixes `WorldPartitionChangelistValidator` "different runtime grid"
reference errors from a log file.

Source: `D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\RuntimeGridReferenceFixup.cpp`
· log category `LogRuntimeGridRefFix`.

Reads a log file containing `WorldPartitionChangelistValidator` runtime-grid reference
errors and, for every **referencer / referee couple**, aligns the referee's `RuntimeGrid`
to the referencer's, tags **both** actors with `ExcludeFromRules`, saves the packages,
and checks them out into a single descriptive Perforce changelist. Processing is
**atomic per couple**: if either side fails, that couple's files are reverted.

## Why it exists

The validator flags an actor that references another actor sitting on a *different*
`RuntimeGrid`. The desired resolution is to bring the referee onto the referencer's grid
and then freeze both actors so the [World Partition rule system](../WorldPartitionRules.md)
does not overwrite the value on the next save. Freezing is done with the
`ExcludeFromRules` actor tag — the same tag the rule subsystems honor
(`UWorldPartitionRuleSettings::ActorTagExcludedFromRules`, defaulting to
`"ExcludeFromRules"`). Doing this by hand across dozens of couples, some nested inside
Level Instances, is error-prone; this command batches it from the validator log.

## Usage

```
Editor.FixRuntimeGridReferenceErrors <LogFilePath> [-DryRun]
```

| Argument | Meaning |
|----------|---------|
| `<LogFilePath>` | Path to a text file containing the validator error lines (required, positional). |
| `-DryRun` | Parse + resolve + report **only**; no `Modify`, no save, no checkout, no changelist. |

- The command must run **in the editor** (`GEditor` present). It **opens the right level
  itself**: couples are grouped by the level package derived from the referencer path,
  and each distinct map is loaded in turn (`FEditorFileUtils::LoadMap`) — the user no
  longer has to open levels by hand. The already-open map is reused as-is.
- Duplicate couples in the log are de-duplicated on `(ReferencerPath, RefereePath)`.

Example:

```
Editor.FixRuntimeGridReferenceErrors D:/Logs/RuntimeGridErrors.txt -DryRun
```

## Automatic level opening

The command drives level navigation itself — a single log can span **many maps** and it
will visit each one in turn:

1. **Parse** every couple from the log.
2. **Group by level** — each couple's owning map is derived from the referencer path
   (`PackageFromActorPath`, e.g. `/Game/Developers/ArnaudStorq/LevelA.NewBlueprint` →
   `/Game/Developers/ArnaudStorq/LevelA`). Distinct levels are kept in first-seen order.
3. **Open + process each level** — for every distinct level package, the map is loaded
   (`FEditorFileUtils::LoadMap`; the already-open map is reused), then couples are
   resolved in the top-level world and, for anything still unresolved, inside its Level
   Instances.

Because opening a map derived from the log replaces the current editor world, **save any
in-progress work first** — loading a map may prompt to save a dirty world. Levels that
cannot be opened as a World Partition world (missing package, non-partitioned) are
**skipped** with a warning and their couples are reported `UNRESOLVED`. A couple whose
referencer and referee live in different maps is only resolvable when both sit in the
level opened for its referencer (otherwise → `UNRESOLVED`, handle manually).

## Accepted log formats

Two line shapes are parsed; any other line is ignored
(`RuntimeGridReferenceFixup.cpp:110`):

| Format | Source | Example line | Referencer / Referee |
|--------|--------|--------------|----------------------|
| **A** | **`WorldPartitionChangelistValidator`** — raised at Perforce **submit / changelist validation** time (copy the lines straight from the validator output). | `<Referencer> (<pkg>) is referencing <Referee> (<pkg>) but both actors are using a different runtime grid.` | first `/Game/...` token / token after `is referencing ` |
| **B** | **`Editor.ScanRuntimeGridReferenceErrors`** (`RuntimeGridConflictScanner`) — the companion **in-editor scan** that replays the same streaming-generation validation on the open world and writes its findings in this shape. | `Actor /Game/Developers/.../LevelA.NewBlueprint references an actor in a different runtime grid /Game/Developers/.../LevelA.BlockingVolume` | first `/Game/...` token / token after the marker |

Both sources describe the **same** underlying conflict (a reference across two different
runtime grids); Format A comes from the submit-time validator, Format B from the
in-editor scanner. Mixing both formats in one log file is fine — each line is parsed
independently.

```112:114:D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\RuntimeGridReferenceFixup.cpp
		static const FString FormatA_Marker = TEXT("but both actors are using a different runtime grid");
		static const FString FormatA_Referencing = TEXT("is referencing ");
		static const FString FormatB_Marker = TEXT("references an actor in a different runtime grid");
```

Actor tokens are extracted as the first `/Game/...` substring stopping at the first
whitespace or parenthesis, and matched against loaded actors by their reconstructed path
`"<SoftPathLongPackageName>.<ActorLabelOrName>"` (exactly what the validator prints), with
a fallback match on the label alone.

## What it does per couple

For each couple whose **both** endpoints are found together in a loaded container:

1. `Referee->SetRuntimeGrid(Referencer->GetRuntimeGrid())` — only if they actually differ.
2. `Referencer->Tags.AddUnique("ExcludeFromRules")` — if not already tagged.
3. `Referee->Tags.AddUnique("ExcludeFromRules")` — if not already tagged.
4. Each modified package is checked out silently and saved.

Every setter is guarded by an equality/`Contains` check, so already-compliant actors
produce **no** dirty package and never enter the changelist.

## Level Instance recursion

Within each opened level, couples whose actors are **not** both present in the top-level
world are retried inside child Level Instances. The command opens each partitioned Level Instance in an edit scope
(`FLevelInstanceEditScope`, mirroring the pattern in
[`UForceHLODExcludeFromLogBuilder`](../BuildersAndCommandlets.md)), fixes any couple that
resolves there, then recurses deeper. The edit scope commits with
`bDiscardEdits=true` — the changes are persisted by saving the external-actor packages
directly, not through the transient Level Instance edit.

## Atomic per-couple processing (revert on failure)

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

## Source control

Checkout is fully **automatic and silent** — no "Check Out Assets" dialog:

- `USourceControlHelpers::CheckOutOrAddFiles(..., bSilent=true)` before saving.
- The save uses `FEditorFileUtils::PromptForCheckoutAndSave` with `bPromptToSave=false`
  and `bAlreadyCheckedOut=true` to suppress the interactive checkout prompt.
- All committed files are then moved into a **new changelist** (`FNewChangelist`) whose
  description states exactly what was done, couple by couple (successful couples only).
- If source control is disabled, saved files are simply left in the default changelist
  (a warning is logged).

## Report

After the run a full report is both logged (`LogRuntimeGridRefFix`, `Display`) and written
to disk next to the input log as `<LogFilePath>.report.txt`. Per couple it lists the
container, referencer/referee labels, the `RuntimeGrid` **old → new** transition, which
side got the tag, and the status: `OK`, `FAILED - ROLLED BACK (files reverted)`, or
`UNRESOLVED` (both actors never found together — handle manually). The summary reports
couples succeeded / failed-reverted / unresolved, grids aligned, tags added, actors
modified, files committed, and files reverted.

## Registration

```896:904:D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\RuntimeGridReferenceFixup.cpp
static FAutoConsoleCommand FixRuntimeGridReferenceErrorsCmd(
	TEXT("Editor.FixRuntimeGridReferenceErrors"),
	TEXT("Fix WorldPartitionChangelistValidator 'different runtime grid' reference errors listed in a log file. ")
	TEXT("For each referencer/referee couple it aligns the referee's RuntimeGrid to the referencer's, tags both actors ")
	TEXT("with the ExcludeFromRules tag, saves them, and checks them out into a described Perforce changelist. If either ")
	TEXT("actor of a couple fails, that couple's files are reverted. A full report is logged and written next to the log ")
	TEXT("file. The command opens each level referenced in the log automatically. Params: <LogFilePath> [-DryRun]."),
	FConsoleCommandWithArgsDelegate::CreateStatic(&WorldBuildingEditor::RuntimeGridReferenceFixup::FixFromLog)
);
```

## See also

- [World Partition rules](../WorldPartitionRules.md) — why `ExcludeFromRules` freezes a value
- [Runtime Grid rules](../WorldPartitionRulesAnalysis/RuntimeGridRules.md) — how `RuntimeGrid` is normally applied
- [Builders & commandlets](../BuildersAndCommandlets.md) — the headless counterpart tools
- [Perforce source control](../PerforceSourceControl.md) — checkout-before-save, changelists
- [Level Instances & OFPA](../LevelInstancesAndOFPA.md) — external actor packages & Level Instance editing

---

**In this section:** **`Editor.FixRuntimeGridReferenceErrors`** | [Delete World Event](DeleteWorldEvent.md) | [Exclude From Rules tag](ExcludeFromRulesTag.md) | [World Partition Batch Converter](WorldPartitionBatchConverter.md)

Back to [Custom Tools](../CustomTools.md).
