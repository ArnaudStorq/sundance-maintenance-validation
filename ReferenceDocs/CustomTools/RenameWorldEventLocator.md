Parent: [Custom Tools](../CustomTools.md)

# Rename World Event Locator (World Events Editor Mode)

An editor-mode UI tool: buttons and dialogs surfaced inside a dedicated editor mode.

**A guided dialog that renames a World Event Locator and everything its name produced —
the Auto DB row, the World Event Level Instances, the `DL_WE_*` data layer assets and every
actor referencing them — in one atomic, Perforce-tracked, reversible operation. Direct
label editing on the Locator is disabled so this tool is the only way in.**

Source: `D:\Sun\Sundance\Source\SundanceEditor\WorldEvents\EditorMode\Renaming\`
(`WorldEventLocatorRenamer.h/.cpp`, `SWorldEventRenameDialog.h/.cpp`) · entry point in
`WorldEventEditorModeToolkit.cpp` · log category `LogWorldEventEditorMode`
(lines prefixed `[WE Rename]`). Jira: **SUNDANCE-77888**.

## Contents

- [Why it exists](#why-it-exists)
- [What a Locator name actually controls](#what-a-locator-name-actually-controls)
- [How to open it](#how-to-open-it)
- [The dialog](#the-dialog)
- [What it does (steps)](#what-it-does-steps)
- [The traps, and how each one is handled](#the-traps-and-how-each-one-is-handled)
- [Error handling & rollback](#error-handling--rollback)
- [Source control](#source-control)
- [Preventing direct label renames](#preventing-direct-label-renames)
- [Scope & known limitations](#scope--known-limitations)
- [See also](#see-also)

## Why it exists

Renaming a World Event Locator in the Outliner changes exactly one thing: the actor's
label. But the name a Locator carries is not cosmetic — the creation flow derives three
other names from it, and none of them follow. A hand-renamed Locator therefore ends up
with a database row, Level Instances and data layer assets all still named after the
previous name, which is both confusing and, for the database row, actively wrong: the old
identifier stays live and keeps the old name reserved.

The manual alternative is the delete-and-recreate procedure, which loses the Locator's
conditions, bounds, tags and placement. This tool does the rename properly instead.

## What a Locator name actually controls

Placing a World Event builds a naming cascade. Each level is derived from the one above it
at creation time and then frozen into saved data:

| Derived from the name | What it becomes | Where it is stored |
|---|---|---|
| Locator label | `WEL_<Name>` | The actor's label, in its OFPA package |
| Locator label | The Auto DB identifier | One row of `DEV_AutoDbAuthIds` |
| Locator label | `LI_WE_<Name>_<Definition>` | The label of each `AWorldEventInstance` |
| Level Instance label | `DL_WE_<Name>_<Definition>` | The `UDataLayerAsset` package name |
| Data layer asset path | A hard reference | `WorldDataLayers` + every actor on the layer |

The order matters: the data layer name is not derived from the Locator directly, it is
derived from the **Level Instance** label through the `NamePatternBased` data layer rule.
So the rename has to walk the cascade top-down — Locator, then instances, then data layers
— or the rule resolves the wrong name.

## How to open it

1. Enter the **World Events** editor mode.
2. In the **Manage** tab, select the target Locator (or one of its entries) in the tree.
3. Click the blue **"Rename Locator..."** button, above the delete button.
4. Type the new name in the **same prompt the creation flow uses**, pre-filled with the
   current name. The `WEL_` prefix is added and validated for you.

Nothing is modified until you press **Begin rename** in the wizard that follows.

## The dialog

The naming prompt and the wizard are two distinct stages, and the prompt loops: if the
name you typed cannot be used (syntax, already taken in the level, or already live in the
database), the reason is shown and the prompt reopens with your text still in it. The
wizard only opens once a valid plan exists.

The wizard itself mirrors the [Delete World Event](DeleteWorldEvent.md) dialog:

- **Header** — the Locator's current name, the new name, and a plain-language summary.
- **"What will be renamed"** — the full cascade, one row per name that changes: the
  Locator, its database identifier, each Level Instance, each data layer asset, and the
  count of referencing packages and Perforce files that will be touched.
- **Steps** — the ordered list below; each row shows a live **spinner → green tick ✓ /
  red cross ✗** plus a status message.
- **Detailed log** — a collapsible, scrollable log of everything that happened.
- **Buttons** — `Begin rename`, `Cancel`, and — only after a failure — `Undo everything`
  and `Copy error`.

## What it does (steps)

Step 0 is only present when the Locator lives inside a Level Instance.

0. **Edit the Level Instance in-context** — opens the containing Level Instance for
   in-context editing, then re-resolves the whole plan (the reload invalidates every
   pointer resolved before it).
1. **Validate the new name & the Perforce state** — the name must be free in the level and
   in the database; every impacted file must be source controlled, up to date, and not
   checked out by someone else. Nothing is modified.
2. **Check out every impacted file** — the Locator, its Level Instances, the data layer
   assets and every package referencing them, so the rename is one revertable set.
3. **Rename the Locator & reset its database identity** — clears the Auto DB identifier
   *before* `SetActorLabel`, so that the save in step 6 registers the new name instead of
   carrying the old row forward.
4. **Rename the World Event Level Instances** — each to the name the creation flow would
   have given it under the new Locator name.
5. **Rename the Data Layer assets & repoint their actors** — re-asks the rule subsystem for
   the expected name, renames through `IAssetTools::RenameAssets`, and fails if a
   redirector was left behind.
6. **Save the renamed actors & assets** — plain package save, or commit of the in-context
   edit followed by a separate save of the root world's share.
7. **Deprecate the previous database identifier** — marks the old `DEV_AutoDbAuthIds` row
   `DEPRECATED`.
8. **Move changes to a described changelist** — every impacted file moves into a new
   Perforce changelist describing exactly what was renamed. It is **not** submitted.

## The traps, and how each one is handled

This is the part that makes the tool worth having. Each of these silently corrupts data if
you do the rename by hand.

**The data layer name is derived from the *renamed* Level Instance.** The plan predicts it
by applying the rule asset's public `TargetDataLayerNamePatterns` to the future instance
label, but the rename step does not trust that prediction: it re-asks
`UDataLayerRuleSubsystem::GetTargetDataLayer` on the actually-renamed instance and aborts if
the two disagree. The prediction is for the preview; the rule subsystem stays authoritative.

**Data layer *instances* must not be renamed.** `UDataLayerInstanceWithAsset::MakeName`
returns `DataLayer_<GUID>`, so the instance objects carry no name to fix. Only the assets
move.

**The actors referencing a data layer are usually unloaded.** In World Partition, an actor
that is not loaded cannot have its reference fixed in memory, and the asset rename would
leave it pointing at a package that no longer exists. The plan finds them through the actor
descriptors (`GetDataLayerInstanceNames()`), force-loads their data layers in the editor,
pins the actors, and restores both afterwards — including for actors that were `(Unloaded)`
before the tool ran.

**`IAssetTools::RenameAssets` checks out and saves referencing packages behind your back.**
A file it touched but the plan did not know about would survive a rollback. The plan
therefore pre-computes exactly the same set with
`AssetRegistry.GetReferencers(..., EDependencyCategory::Package)`, which also covers soft
references, so AssetTools can never reach outside the plan.

**A leftover redirector is a failure, not a warning.** `RenameAssets` creates a redirector
when it cannot fix a referencer — which is precisely the "one actor stayed unloaded" case.
The step checks `FPackageName::DoesPackageExist(OldPackageName)` afterwards and fails hard
rather than shipping a half-renamed layer.

**The Auto DB identifier is keyed by the label, and clearing it takes three calls.**
`RemoveUserDataOfClass(UDbPersistentIdUserData::StaticClass())` on the root component,
`UAutoDbAuthoringMetadata::Reset`, and `ResetDbPersistentIdProperty()` on each Auto DB
component — all *before* `SetActorLabel`. The save path then reassigns from the new label
on its own. The old row is retired separately in step 7.

**The deprecation marker must not contain the Locator's package name.** PEEVES submit
validation (`AutoDbAuthoringUserDataConsistent`) scans `UserEdits.sql` for lines mentioning
the actor's package and requires the *last* one to be a `Version <N>` line. A `DEPRECATED`
line naming the package would fail the submit. The markers are written with the
*identifiers* only. OFPA package names are GUID-based, so a label can never appear in one —
this is safe by construction, not by luck.

**The database identifier prefix is not ours to guess.** The new identifier is derived as
`OldId.LeftChop(OldLabel.Len()) + NewLabel`, which preserves whatever prefix the Auto DB
system used. If the old identifier does not end with the old label, the step warns and
skips instead of inventing a name.

**A shared data layer is left alone.** If the asset is also listed by a World Event of
another Locator, renaming it would silently rename someone else's layer. It is skipped and
reported in the plan.

**Inside a Level Instance, a plain save writes to the wrong file.** Actors of a Level
Instance belong to its level, which only persists through an in-context edit commit. The
plan splits its packages into the Level Instance's share and the root world's share (the
data layer assets, the root `WorldDataLayers`, overland actors on the layer) and saves each
through the right path.

**No transaction.** `FScopedTransaction` is deliberately *not* used: the operation writes to
Perforce and to the database, neither of which undo can roll back. A partial undo would be
worse than none. Rollback is explicit instead.

## Error handling & rollback

The design is **atomic**: if any step fails, nothing is left half-done.

- All fallible preconditions are checked in step 1, **before** any change.
- On failure the dialog turns red, names the failing step and the reason, and offers a
  single **"Undo everything"** button.
- Rollback reverts **every** touched Perforce file (`USourceControlHelpers::RevertFiles`)
  and — if the in-editor world was already mutated — **reloads the level** so the editor
  returns exactly to its pre-rename state.
- Pinned actors are unpinned and force-loaded data layers restored even when the user
  simply cancels the wizard (the renamer's destructor handles it), so the editor is never
  left with actors loaded that were not.

## Source control

- Checkout is automatic and silent (`USourceControlHelpers::CheckOutOrAddFiles`).
- The data layer rename produces both a *delete* at the old path and an *add* at the new
  one; both are tracked in the plan and both end up in the changelist.
- Success moves all files into a new **described** changelist (`FNewChangelist`).
- **Nothing is ever submitted automatically** — you review and submit the changelist
  yourself.

## Preventing direct label renames

The Jira asked to investigate enforcing tool-only renaming. `AWorldEventLocator` now
overrides `IsActorLabelEditable()` to return `false`, which the Scene Outliner and the
Details panel name widget both honour: the label becomes read-only in the UI and this tool
is the only supported way to change it.

This is a UI-level guard, not a hard lock — `SetActorLabel` itself does not consult
`IsActorLabelEditable`, so C++ and Python can still rename the actor. That is intentional:
the engine's own rename paths need it. The MCP toolset's
`RenameWorldEventLocator` was routed through the renamer for the same reason, so the agent
path gets the full cascade too.

## Scope & known limitations

- The tool renames a **Locator**. Renaming a `WorldEventDefinition` (shared across
  Locators) is out of scope.
- `UserEdits.sql` is **not** added to the tool's changelist, because
  `UDbEditsManager::GetEditsFile` is protected and exposing it would mean touching the
  `DbGateway` plugin. The file follows the standard AutoDbAuthoring flow instead; the
  success message in the dialog says so explicitly.
- Failure to move files to the described changelist (step 8) is treated as a **non-fatal
  warning** — the rename still succeeded and the files remain in the default changelist.

## See also

- [Delete World Event](DeleteWorldEvent.md) — the sibling tool whose structure this mirrors
- [World Events MCP Toolsets](WorldEventsMCPToolsets.md) — the agent-facing entry point
- [World Events (work-done narrative)](../../WorkDoneByTopic/WorldEvents.md) — the World Events system context
- [Perforce source control](../PerforceSourceControl.md) — checkout-before-save, changelists
- [Level Instances & OFPA](../LevelInstancesAndOFPA.md) — external actor packages & Level Instance editing

---

**In this section:** [Runtime Grid Reference Tools](RuntimeGridReferenceTools.md) | [Delete World Event](DeleteWorldEvent.md) | **Rename World Event Locator** | [Exclude From Rules tag](ExcludeFromRulesTag.md) | [World Partition Batch Converter](WorldPartitionBatchConverter.md)

Back to [Custom Tools](../CustomTools.md).
