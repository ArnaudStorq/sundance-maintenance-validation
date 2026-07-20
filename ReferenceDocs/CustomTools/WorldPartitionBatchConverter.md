Parent: [Custom Tools](../CustomTools.md)

# World Partition Batch Converter

An editor-mode UI tool: a standalone Slate window opened from the main menu.

**A grid-driven dialog that batch-converts many non-partitioned Content Browser levels to
World Partition in one pass — the equivalent of running the right-click *"Add Partitioned
Streaming Support"* on each level — then runs data validation on the results and organises
every converted level's files into descriptive Perforce changelists.**

Source: `D:\Sun\Sundance\Plugins\EditorImprovements\Source\WEditorImprovements\...\WorldPartitionConverter\`
(`SWWorldPartitionConverterWindow.h/.cpp` — the Slate window; `WWorldPartitionConverterProcessor.h/.cpp`
— the UI-independent backend; `WWorldPartitionConverterSettings.h/.cpp` — persistent settings;
`WWorldPartitionConverterTypes.h` — the row model; `WWorldPartitionConverterSubModule.h/.cpp`
— menu & settings registration). Log category `LogWPBatchConverter`. Jira: **SUNDANCE-69603**.
Implemented in changelist **1972620**.

## Why it exists

Converting a level to World Partition by hand means opening it, running *"Add Partitioned
Streaming Support"*, saving, then hand-managing the resulting `.umap` and external actor
(OFPA) packages in Perforce — repeated once per level. Across a project with hundreds of
levels that is slow and error-prone. This tool discovers every candidate level, lets you
pick which ones to convert, and performs the conversion + save + source-control bookkeeping
+ post-conversion validation automatically, one level at a time, with a clear audit trail.

## How to open it

**Tools** menu → **World Partition** section → **"Convert Levels to World Partition
(Batch)..."** (placed immediately below the engine's stock *"Convert Level..."* entry). This
opens the **World Partition Batch Converter** window.

Nothing is modified until you select levels and press **Process Selected Levels**.

## The window

- **Header** — title and a short plain-language explanation of what the tool does.
- **Toolbar** — `Refresh` (re-scan), `Settings` (toggles the inline settings panel), and a
  search box that filters by level name, folder or depot path.
- **Grid** — one row per discovered `.umap`, with columns:
  | Column | Meaning |
  |--------|---------|
  | *(checkbox)* | Selection for processing (kept in sync with the row highlight). |
  | **Level** | Short level name. |
  | **Partitioned** | Whether the level already uses World Partition (read from asset registry tags — no package load). |
  | **External Actors** | Whether actors are already stored in external (OFPA) packages. |
  | **Content Folder** | The `/Game/...` folder the level lives in. |
  | **Perforce Path** | Depot path, resolved via source control. |
  | **Source Control** | Human-readable status (checked out, up to date, not in depot, ...). |
  | **Conversion** | `-` / green **Converted** / red **Failed** (hover for the reason). |
  | **Validation** | Tri-state icon: green tick ✓ / amber warning / red error. |
  | **Errors** / **Warnings** | Validation counts. |
  | **Details** | The last operation's message (also surfaced as tooltips). |
- **Operation Log** — a scrollable, read-only text log of the major operations performed
  during processing (with timestamps); a `Clear` button hides it. Appears only once there
  is something to show.
- **Status bar** — counts of shown / partitioned / non-partitioned / selected / total
  levels, plus the **Process Selected Levels** button.

By default the grid lists **only non-partitioned levels** (the conversion candidates).
Right-clicking a row offers **Show in Content Browser** and **Copy Package Path**.

## Settings

Persistent per-user settings (stored in `EditorPerProjectUserSettings`; also reachable via
**Editor Preferences → Plugins → World Partition Batch Converter**):

| Setting | Default | Effect |
|---------|---------|--------|
| **Show Partitioned Levels** | off | When on, the grid also lists levels that are already World Partition. |
| **Excluded Folders** | `Developers`, `Plugins`, `Experimental` | Folders under `/Game` skipped while scanning (sub-folders too). |
| **Root Content Path** | `/Game` | Root virtual path the scan starts from. |
| **Resolve Perforce Info On Scan** | on | Query source control during the scan to fill the depot path / status columns (disable for a faster scan). |
| **Merge Successfully Converted Levels Into One Changelist** | on | Post-process: combine all successfully-converted, error-free levels into one changelist and delete their individual ones (see below). |

## What it does (per run)

1. **Pre-flight** — processing is refused if the Perforce **Default** changelist already
   contains files, so each converted level can be isolated in its own changelist. A message
   explains the problem.
2. **Per level** (each selected non-partitioned level, one at a time):
   - Load the world as an inactive world and check its preconditions (not currently loaded
     in the editor, no sublevels).
   - Convert with `FWorldPartitionConverter::Convert` using the same parameters as *"Add
     Partitioned Streaming Support"* (`bConvertSubLevels=false`, `bEnableStreaming=false`,
     `bUseActorFolders=true`).
   - Save only the affected packages (the map plus its external object packages), check
     them out / mark for add, and **move that level's files into a dedicated new changelist**
     whose description names the level and cites the Jira.
3. **Validation** — every level that converted successfully is validated via the
   `UEditorValidatorSubsystem`; the error/warning counts and the tri-state icon are recorded
   on its row.
4. **Merge** *(optional, on by default)* — see below.

Rows update live (green **Converted**, validation icon, counts) and the Operation Log gains
one line per major step. When a level fails, its **Conversion** cell turns red with the
reason in the tooltip, the reason is written to the Operation Log, and full details go to the
Output Log under `LogWPBatchConverter`.

## Source control

- Checkout/add is automatic and silent (`USourceControlHelpers::CheckOutOrAddFiles`).
- Each level's converted files are moved into their **own described changelist**
  (`FNewChangelist`). The tool moves an **explicit file list** (the map + its external
  packages) rather than trusting the Default-changelist enumeration, which the provider
  often reports as empty.
- **Merge step** — when *Merge Successfully Converted Levels Into One Changelist* is on and
  at least two levels converted **without validation errors**, all of their files are moved
  into a **single combined changelist** whose description lists every included level, and
  each now-empty per-level changelist is **deleted** (`FDeleteChangelist`). Levels that
  failed validation (or failed to convert) are **left untouched** in their own separate
  changelist, independent of the merge.
- **Nothing is ever submitted automatically** — you review and submit the changelists
  yourself.

## Threading & responsiveness

- **Scanning** runs on a background thread (asset-registry query with
  `bIncludeOnlyOnDiskAssets=true` for thread safety), streams rows into the grid
  progressively, and resolves source-control status / depot paths asynchronously so the
  window stays responsive.
- **Conversion** necessarily runs on the game thread (it loads `UWorld`s and uses
  `GEditor`), so the window is briefly busy while each level is processed; the grid and log
  update between levels.

## Backend & commandlet reuse

The UI is a thin shell — all the heavy lifting lives in the Slate-free
`FWWorldPartitionConverterProcessor` (discovery, conversion, validation, Perforce). The same
backend can therefore be driven headless from a future commandlet without any UI dependency.

## See also

- [Builders & commandlets](../BuildersAndCommandlets.md) — the headless counterpart tools
- [Perforce source control](../PerforceSourceControl.md) — checkout-before-save, changelists
- [Level Instances & OFPA](../LevelInstancesAndOFPA.md) — external actor packages & Level Instance editing
- [World Partition rules](../WorldPartitionRules.md) — how converted worlds are governed afterwards

---

**In this section:** [`Editor.FixRuntimeGridReferenceErrors`](FixRuntimeGridReferenceErrors.md) | [Delete World Event](DeleteWorldEvent.md) | **World Partition Batch Converter**

Back to [Custom Tools](../CustomTools.md).
