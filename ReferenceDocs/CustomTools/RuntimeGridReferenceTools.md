Parent: [Custom Tools](../CustomTools.md)

# Runtime Grid Reference Tools

Two **linked** interactive console commands (`FAutoConsoleCommand`, typed into the editor
console `~`) that together find and repair `WorldPartitionChangelistValidator`
"different runtime grid" reference errors:

| Command | Role | Source · log category |
|---------|------|-----------------------|
| [`Editor.ScanRuntimeGridReferenceErrors`](#editorscanruntimegridreferenceerrors--find-the-conflicts) | **Find** — scans the open World Partition world for the conflicts and writes them to a text file | `RuntimeGridConflictScanner.cpp` / `.h` · `LogRuntimeGridScan` |
| [`Editor.FixRuntimeGridReferenceErrors`](#editorfixruntimegridreferenceerrors--fix-the-conflicts) | **Fix** — reads that file, aligns grids, freezes both actors, saves + checks out into a Perforce changelist | `RuntimeGridReferenceFixup.cpp` · `LogRuntimeGridRefFix` |

Both live in `D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\`.

## Typical workflow (scan → fix)

1. Open the target World Partition world (e.g. `LV_Overland`).
2. Run **`Editor.ScanRuntimeGridReferenceErrors`** — it produces
   `<ProjectSaved>/RuntimeGridConflicts.txt` (one line per conflict).
3. Feed that file to **`Editor.FixRuntimeGridReferenceErrors <file>`** to apply the fixes.

The scanner writes its findings in the exact line shape the fixer parses, so the two
tools chain directly. You can also skip the scanner and feed the fixer a log copied
straight from the submit-time validator (see [Accepted log formats](#accepted-log-formats)).

## Why they exist

The validator flags an actor that references another actor sitting on a *different*
`RuntimeGrid`. World Partition streaming could then load one without the other → dangling
reference. The desired resolution is to bring the referee onto the referencer's grid and
then freeze both actors so the [World Partition rule system](../WorldPartitionRules.md)
does not overwrite the value on the next save. Freezing is done with the
`ExcludeFromRules` actor tag — the same tag the rule subsystems honor
(`UWorldPartitionRuleSettings::ActorTagExcludedFromRules`, defaulting to
`"ExcludeFromRules"`). Doing this by hand across dozens of couples, some nested inside
Level Instances, is error-prone; these commands batch the whole find-and-fix loop.

## Reproducing the error

The error is raised by the `WorldPartitionChangelistValidator`, more precisely by the
`IStreamingGenerationErrorHandler::OnInvalidReferenceRuntimeGrid` handler: one actor (the
**referencer**, e.g. `BP_PerformTasks`) holds a **hard reference** to another actor (the
**referee**, e.g. `STN_OL_..._Stand_1P_FS`), but the two actors sit on **different runtime
grids**.

Starting from an empty partitioned level:

### Step 1 — Define a second runtime grid

1. `Window > World Settings`.
2. Section **World Partition Setup** → **Runtime Hash** (`WorldPartitionRuntimeSpatialHash`).
3. Expand the **Grids** array. By default it only has `MainGrid`.
4. Add an element and give it a **Grid Name**, e.g. `SecondGrid` (leave Cell Size /
   Loading Range at their defaults).

> You need two **valid** and **different** grids. Assigning a grid that does not exist
> triggers a *different* error (`OnInvalidRuntimeGrid`), not this one.

### Step 2 — Create the referenced actor (the `STN_...`)

Place an actor in the level (a Static Mesh Actor or a Blueprint is enough). Rename it so
you can find it (e.g. `STN_Target`). In **Details**, category **World Partition**:

- `Is Spatially Loaded` = **true**
- `Runtime Grid` = **`MainGrid`**

### Step 3 — Create the referencing Blueprint (`BP_PerformTasks`)

1. Create an Actor Blueprint, name it `BP_PerformTasks`.
2. Add a variable of type **Actor (Object Reference)** and tick **Instance Editable**.
   Compile / Save.
3. Place `BP_PerformTasks` in the level.
4. In its **Details**, assign that variable to the `STN_Target` actor placed in step 2 —
   this creates the hard actor→actor reference that WP detects.
5. Still in **Details**, category **World Partition**:
   - `Is Spatially Loaded` = **true**
   - `Runtime Grid` = **`SecondGrid`** ← different from the `STN_`'s grid

### Step 4 — Save

`Ctrl+Shift+S`. Because the level is partitioned, each actor is serialized into its own
external package under `__ExternalActors__/...` (this is what appears in the error message).

### Step 5 — Trigger the validation

Two ways:

- **Like your CL (Perforce):** put both actors' external packages into a changelist, then
  right-click the changelist → **Validate**. This is exactly the path that runs
  `WorldPartitionChangelistValidator`.
- **In-editor, without P4:** run `Editor.ScanRuntimeGridReferenceErrors` on the open world
  (see below) — it replays the same streaming-generation validation and reports the same
  conflict.

---

## `Editor.ScanRuntimeGridReferenceErrors` — find the conflicts

Scans the currently-open World Partition world (and its nested Level Instances) for every
"an actor references an actor in a different runtime grid" conflict and writes the result
to a text file in the exact format consumed by the fixer.

### Usage

```
Editor.ScanRuntimeGridReferenceErrors [OutputFilePath]
```

| Argument | Meaning |
|----------|---------|
| `[OutputFilePath]` | Optional, positional. Where to write the conflict file. Defaults to `<ProjectSaved>/RuntimeGridConflicts.txt`. |

- The command must run **in the editor** with a **World Partition world open** (e.g.
  `LV_Overland`); otherwise it aborts with a warning.
- It **aborts** if a Level Instance is currently open in **edit mode** (that state would
  make the engine validation assert). Commit/exit the Level Instance first.
- The conflict file is always **(re)written**, even when empty, so a stale file from a
  previous run cannot be mistaken for current results.

Example:

```
Editor.ScanRuntimeGridReferenceErrors D:/Sandbox/AI/RuntimeGridConflicts.txt
```

### How detection works

The scan reuses the engine's streaming-generation validation
(`UWorldPartition::CheckForErrors`) — the **very same code path** the
`WorldPartitionChangelistValidator` runs. Streaming generation works on lightweight actor
**descriptors**, so **no actor packages are loaded** (fast).

Every level — the open world, then each nested Level Instance sublevel — is validated as
its **own standalone base container**:

- created **fresh** so it holds no live child hierarchy → streaming generation never
  recurses into the live editor container tree (that recursion is what trips an internal
  container-ID assertion when a Level Instance is loaded in a partially-registered/edited
  state);
- but **outered to the live world partition** so the AVA runtime-grid mutator (bound on
  that WP) fires and the **resolved** grids are computed. Without the mutator every actor
  resolves to grid `None` and no conflict would ever be reported.

Level Instances are **never opened in edit mode**. The scan descends into nested Level
Instance sublevels recursively, and each distinct sublevel asset is scanned **once**.

### Mutator-gate diagnostics

A runtime-grid conflict can only surface if the AVA runtime-grid mutator actually runs and
assigns divergent grids. The command therefore logs — and folds into the report header —
the state of every gate the mutator checks:

- RuntimeGrid mutator delegate bound on the live WP
- `WorldPartition->IsStreamingEnabled()`
- `WorldPartition->IsMainWorldPartition()`
- `AutoApplyRulesOnActorSave` (project setting)
- `UWorldPartitionRuleSubsystem::IsWorldInAutoApplyList(World)`

If **any** gate is closed, the mutator does not assign grids, so **0 conflicts is expected
regardless of authoring** — the report says so explicitly. Fix the gate and re-run.

> **Already fixed?** The mutator **skips** any actor carrying `ExcludeFromRules`. Once the
> fixer has neutralised a conflict (aligned + tagged), the scanner will correctly no
> longer report it. The report prints `Descriptors scanned` and how many are
> `tagged ExcludeFromRules`, so a high excluded count explains a low/zero conflict count.

### Performance

The dominant cost is the single streaming-generation pass over the **main world**'s actor
set — the same work the engine does at submit time, so it is essentially irreducible
(≈18 s on `LV_Overland`; the nested Level Instance passes add well under a second). Two
cheap prunes avoid needless work: non-partitioned levels are skipped, and any level whose
descriptors contain **no actor references at all** skips the streaming-generation pass
entirely (a reference conflict is impossible there).

### Output

- **Conflict file** (`OutputFilePath`): one line per conflict, in the shape the fixer
  parses:
  `Actor <Referencer> references an actor in a different runtime grid <Referee>`
- **Report** (logged and written to `<OutputFilePath>.report.txt`): the mutator-gate
  diagnostics, the descriptor / excluded counts, then the conflicts split into two blocks —
  **(1)** both actors in partitioned levels, **(2)** at least one actor in a
  non-partitioned level — followed by a numeric summary (conflicts, distinct problematic
  actors, and how many sit in partitioned vs non-partitioned levels).

### Registration

```502:515:D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\RuntimeGridConflictScanner.cpp
static FAutoConsoleCommand ScanRuntimeGridReferenceErrorsCmd(
	TEXT("Editor.ScanRuntimeGridReferenceErrors"),
	TEXT("Scan the currently-open World Partition world (e.g. LV_Overland) for every 'an actor references an actor ")
	...
	FConsoleCommandWithArgsDelegate::CreateStatic(&WorldBuildingEditor::RuntimeGridConflictScanner::ScanFromOpenWorld)
);
```

---

## `Editor.FixRuntimeGridReferenceErrors` — fix the conflicts

Reads a file containing runtime-grid reference errors and, for every **referencer /
referee couple**, aligns the referee's `RuntimeGrid` to the referencer's, tags **both**
actors with `ExcludeFromRules`, saves the packages, and checks them out into a single
descriptive Perforce changelist. Processing is **atomic per couple**: if either side
fails, that couple's files are reverted.

### Usage

```
Editor.FixRuntimeGridReferenceErrors <LogFilePath> [-DryRun]
```

| Argument | Meaning |
|----------|---------|
| `<LogFilePath>` | Path to a text file containing the error lines (required, positional). Typically the file produced by `Editor.ScanRuntimeGridReferenceErrors`. |
| `-DryRun` | Parse + resolve + report **only**; no `Modify`, no save, no checkout, no changelist. |

- The command must run **in the editor** (`GEditor` present). It **opens the right level
  itself**: couples are grouped by the level package derived from the referencer path,
  and each distinct map is loaded in turn (`FEditorFileUtils::LoadMap`). The already-open
  map is reused as-is.
- Duplicate couples in the log are de-duplicated on `(ReferencerPath, RefereePath)`.

Example:

```
Editor.FixRuntimeGridReferenceErrors D:/Sandbox/AI/RuntimeGridConflicts.txt -DryRun
```

### Automatic level opening

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
in-progress work first**. Levels that cannot be opened as a World Partition world (missing
package, non-partitioned) are **skipped** with a warning and their couples are reported
`UNRESOLVED`. A couple whose referencer and referee live in different maps is only
resolvable when both sit in the level opened for its referencer (otherwise →
`UNRESOLVED`, handle manually).

### Accepted log formats

Two line shapes are parsed; any other line is ignored:

| Format | Source | Example line | Referencer / Referee |
|--------|--------|--------------|----------------------|
| **A** | **`WorldPartitionChangelistValidator`** — raised at Perforce **submit / changelist validation** time (copy the lines straight from the validator output). | `<Referencer> (<pkg>) is referencing <Referee> (<pkg>) but both actors are using a different runtime grid.` | first `/Game/...` token / token after `is referencing ` |
| **B** | **`Editor.ScanRuntimeGridReferenceErrors`** (`RuntimeGridConflictScanner`) — the companion **in-editor scan** described above, which writes its findings in this shape. | `Actor /Game/Developers/.../LevelA.NewBlueprint references an actor in a different runtime grid /Game/Developers/.../LevelA.BlockingVolume` | first `/Game/...` token / token after the marker |

Both sources describe the **same** underlying conflict; Format A comes from the submit-time
validator, Format B from the in-editor scanner. Mixing both formats in one file is fine —
each line is parsed independently.

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

Within each opened level, couples whose actors are **not** both present in the top-level
world are retried inside child Level Instances. The command opens each partitioned Level
Instance in an edit scope (`FLevelInstanceEditScope`), fixes any couple that resolves
there, then recurses deeper. The edit scope commits with `bDiscardEdits=true` — the
changes are persisted by saving the external-actor packages directly, not through the
transient Level Instance edit.

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

**In this section:** **Runtime Grid Reference Tools** | [Delete World Event](DeleteWorldEvent.md) | [Exclude From Rules tag](ExcludeFromRulesTag.md) | [World Partition Batch Converter](WorldPartitionBatchConverter.md)

Back to [Custom Tools](../CustomTools.md).
