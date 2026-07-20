Parent: [Custom Tools](../CustomTools.md)

# Delete World Event (World Events Editor Mode)

An editor-mode UI tool: buttons and dialogs surfaced inside a dedicated editor mode.

**A one-click, guided dialog that fully deletes a World Event and every asset it created
(locator, level instance(s), data layer instance(s) and data layer asset(s)) from the
Overland, with live per-step progress and a full rollback on failure.**

Source: `D:\Sun\Sundance\Source\SundanceEditor\WorldEvents\EditorMode\Deletion\`
(`WorldEventDeleter.h/.cpp`, `SWorldEventDeleteDialog.h/.cpp`) · entry point in
`WorldEventEditorModeToolkit.cpp` · log category `LogWorldEventEditorMode`
(lines prefixed `[WE Delete]`). Jira: **SUNDANCE-40173**.

## Why it exists

Deleting a World Event by hand is tedious and error-prone because placing one creates a
web of references: a `WorldEventLocator` actor, one `WorldEventInstance` (Level Instance)
per definition, a `DataLayerAsset` in the Content Browser, and the matching data layer
**instance(s)** registered in `WorldDataLayers` (and, when the event sits inside a Level
Instance such as Hogwarts/Hogsmeade, a second instance in that hierarchy). The manual
procedure — documented in confluence *"Deleting World Events from the Overland"* — is a
strict ordered sequence of deletions ending with 4–5 files in a changelist. Missing a
step leaves dangling references. This tool automates the whole procedure safely.

## How to open it

1. Enter the **World Events** editor mode.
2. In the **Manage** tab, select the target Locator (or one of its entries) in the tree.
3. Click the red **"Delete World Event..."** button. The guided dialog opens.

Nothing is modified until you press **Begin deletion**.

## The dialog

A polished, self-explanatory modal wizard:

- **Header** — warning icon, the World Event name, and a plain-language summary.
- **"What will be deleted"** — a transparent, up-front inventory of every actor, data
  layer instance, data layer asset, and the number of Perforce files that will be touched.
- **Steps** — the ordered list below; each row shows a live **spinner → green tick ✓ /
  red cross ✗** plus a status message.
- **Detailed log** — a collapsible, scrollable log of everything that happened.
- **Buttons** — `Begin deletion` (explicit confirmation), `Cancel`, and — only after a
  failure — `Undo everything`.

## What it does (steps)

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

## Error handling & rollback

The design is **atomic**: if any step fails, nothing is left half-done.

- All fallible preconditions are checked in step 1, **before** any change.
- On failure the dialog turns red, names the failing step and the reason, and offers a
  single **"Undo everything"** button.
- Rollback reverts **every** touched Perforce file (`USourceControlHelpers::RevertFiles`)
  and — if the in-editor world was already mutated — **reloads the level** so the editor
  returns exactly to its pre-deletion state.

## Source control

- Checkout is automatic and silent (`USourceControlHelpers::CheckOutOrAddFiles`).
- Success moves all files into a new **described** changelist (`FNewChangelist`).
- **Nothing is ever submitted automatically** — you review and submit the changelist
  yourself.

## Scope & notes

- Granularity is the **whole Locator**: it deletes the locator and everything it created.
- The reusable `WorldEventDefinition` data asset is **not** deleted (it is shared).
- Failure to move files to the described changelist (step 7) is treated as a **non-fatal
  warning** — the deletion still succeeded and the files remain in the default changelist.

## See also

- [World Events (work-done narrative)](../../WorkDoneByTopic/WorldEvents.md) — the World Events system context
- [Perforce source control](../PerforceSourceControl.md) — checkout-before-save, changelists
- [Level Instances & OFPA](../LevelInstancesAndOFPA.md) — external actor packages & Level Instance editing

---

**In this section:** [Runtime Grid Reference Tools](RuntimeGridReferenceTools.md) | **Delete World Event** | [Exclude From Rules tag](ExcludeFromRulesTag.md) | [World Partition Batch Converter](WorldPartitionBatchConverter.md)

Back to [Custom Tools](../CustomTools.md).
