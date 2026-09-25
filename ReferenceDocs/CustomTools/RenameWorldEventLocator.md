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
- [Testing it from Python or MCP](#testing-it-from-python-or-mcp)
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
   in the database, the asset registry must be done discovering assets and still list the
   referencers the plan was built with, the level must have no unsaved changes, and no data
   layer asset may already exist at a target path. Every impacted file must exist on disk,
   be at the latest revision, be neither checked out by someone else, unresolved nor
   already marked for delete, be openable for edit, and not be open in one of your numbered
   changelists, unless it is the changelist of an earlier rename (see
   [Source control](#source-control)). No rename target may exist in Perforce. Nothing is
   modified.
2. **Check out every impacted file** — the Locator, its Level Instances, the data layer
   assets and every package referencing them, so the rename is one revertable set. Files
   you already have open are copied aside first (see [Source control](#source-control)).
3. **Rename the Locator & reset its database identity** — clears the Auto DB identifier
   *before* `SetActorLabel`, so that the save in step 6 registers the new name instead of
   carrying the old row forward.
4. **Rename the World Event Level Instances** — each to the name the creation flow would
   have given it under the new Locator name.
5. **Rename the Data Layer assets & repoint their actors** — re-asks the rule subsystem for
   the expected name, renames through `IAssetTools::RenameAssets`, then fixes up and deletes
   the redirectors the move leaves behind. It fails if one of them cannot be deleted.
6. **Save the renamed actors & assets** — plain package save, or commit of the in-context
   edit followed by a separate save of the root world's share.
7. **Deprecate the previous database identifier** — marks the old `DEV_AutoDbAuthIds` row
   `DEPRECATED`. If that fails, the rename fails and is undone like at any other step: both
   identifiers would otherwise stay live.
8. **Move changes to a described changelist** — every impacted file still open moves into a
   new Perforce changelist describing exactly what was renamed, or into the changelist of an
   earlier rename that is not submitted yet (see [Source control](#source-control)). It is
   **not** submitted.

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
before the tool ran. This covers every actor on the layer, not just the Level Instances: an
actor added to a World Event's data layer by hand, such as a Trigger Volume, is repointed and
saved the same way, and ends up in the same changelist.

**A World Event Level Instance can be unloaded too.** Turning its data layer on is not
enough when it lies outside the loaded region. Renaming its data layer without it would
leave the Locator, the Level Instance and the data layer out of sync, so the plan pins the
unloaded Level Instances before resolving them, and refuses to run if one still cannot be
loaded. Step 4 does not trust the pointers taken by the plan either: it looks each resolved
Level Instance up again by GUID, and fails, which undoes the rename, if one is gone. A Level
Instance whose actor no longer exists in the level only gets a warning, since there is
nothing left to rename. Inside a Level Instance, the check waits for the in-context edit of
step 0, which loads its actors.

**`IAssetTools::RenameAssets` checks out and saves referencing packages behind your back.**
A file it touched but the plan did not know about would survive a rollback. The plan
therefore pre-computes exactly the same set with
`AssetRegistry.GetReferencers(..., EDependencyCategory::Package)`, which also covers soft
references, so AssetTools can never reach outside the plan.

**Source controlled assets are always moved with a redirector.** `LoadReferencingPackages()`
flags every source controlled asset as "not local", and `RenameAssets` never moves a
non-local asset without leaving a redirector, however well it fixed the referencers. Step 5
therefore does what the Content Browser's **Fix Up Redirectors** does afterwards: resave the
referencers against the new path, then delete the redirectors and their now empty packages.
It reimplements that sequence rather than calling `IAssetTools::FixupReferencers`, which
ends on a modal report where every answer except the delete button leaves the redirectors
behind. A redirector that cannot be deleted means a referencer still points at the old
path — the half-renamed state this tool exists to prevent — so the step fails and the
rename rolls back. An old file the cleanup skipped is marked for delete, so the changelist
stays complete.

**The asset registry must be done discovering assets.** The referencers come from the
registry, and the editor silently skips deleting redirectors while discovery is running.
With an incomplete list, the asset rename would rewrite files the tool never checked out,
copied aside or reverted. The analysis therefore refuses to build a plan until discovery is
finished. Step 1 checks it again, and queries the referencers again: if a package started
referencing a data layer since the plan was built, the plan is out of date and step 1 asks
you to run the rename again.

**The Auto DB identifier is keyed by the label, and clearing it takes three calls.**
`RemoveUserDataOfClass(UDbPersistentIdUserData::StaticClass())` on the root component,
`UAutoDbAuthoringMetadata::Reset`, and `ResetDbPersistentIdProperty()` on each Auto DB
component — all *before* `SetActorLabel`. The save path then reassigns from the new label
on its own. The old row is retired separately in step 7.

**The deprecation marker must not contain the Locator's package name.** PEEVES submit
validation (`AutoDbAuthoringUserDataConsistent`) scans `UserEdits.sql` for lines mentioning
the actor's package and requires the *last* one to be a `Version <N>` line matching the
actor's `UAutoDbAuthoringMetadata::VersionNumber`. A `DEPRECATED` line naming the package
would fail the submit. The markers are written with the *identifiers* only. OFPA package
names are GUID-based, so a label can never appear in one — this is safe by construction,
not by luck.

**A rollback leaves the journal ahead of the disk.** Saving the renamed Locator journals its
new identity under its package, with the version count restarted by the identity reset
(`Version 2` where the Locator on disk is at `Version 6`, for instance). Once the files are
reverted, that last entry no longer matches the Locator on disk, and PEEVES would reject the
next submit. The rollback therefore appends the block that saving the reverted Locator
would write: its old identifier, live again, under the same package and with the version it
has on disk. This also brings the old identifier back if step 7 had already deprecated it.

**Reverting through `USourceControlHelpers` skips deleted files.** `RevertFiles()` and
`RevertFile()` only revert files that pass `CanRevert()`, and the Perforce provider excludes
files marked for delete unless `RevisionControl.Perforce.AllowRevertingDeletedFiles` is on.
The asset move marks each data layer asset at its old path for delete, so a rollback built
on those helpers left the assets deleted, and the reverted actors pointed at missing
packages (MapCheck: *"Data layer … Does not have Data Layer Asset"*). The rollback runs
`FRevert` through the provider instead.

**World Partition reads the actors back from the asset registry, not from the disk.** The
actor descriptors are built from the registry, which keeps describing a loaded asset as it
was last saved and ignores its file. Reverting the files and reloading the map is not
enough: the reopened level would still show the renamed labels and data layers. The
rollback closes the level, reverts, rescans the touched files
(`IAssetRegistry::ScanModifiedAssetFiles`), and only then reopens the level.

**The undo reloads the level, so unsaved work has to be saved first.** Closing the level
without a save prompt is what makes the undo exact, and it would silently throw away any
unsaved change, including changes unrelated to the rename. Step 1 therefore refuses to start
while the level has dirty packages, or while a file of the plan has unsaved changes, and
lists them (by actor label for OFPA packages). For a Locator inside a Level Instance, step 0
runs the check instead, before entering the edit, since a failure from that point on already
reloads the level.

**A failed validation must not undo anything.** The dialog offers the undo as soon as a step
has failed, step 1 included, and step 1 fails precisely when something already sits at a
target path. The files at the new asset paths are therefore only reverted and deleted once
the asset move has started: before that, they are not the tool's.

**Undoing from the dialog ends the editor mode that opened it.** Reopening the level exits
the World Events editor mode, and the dialog is opened from that mode's button handler.
Undoing from inside that handler would destroy the mode under its own call stack, so the
dialog runs the undo on the next editor tick, once its window is closed.

**The database identifier prefix is not ours to guess.** The new identifier is derived as
`OldId.LeftChop(OldLabel.Len()) + NewLabel`, which preserves whatever prefix the Auto DB
system used. If the old identifier does not end with the old label, the step warns and
skips instead of inventing a name.

**A shared data layer blocks the rename.** If the asset is also listed by a World Event of
another Locator, renaming it would silently rename someone else's layer, and keeping it
would leave this World Event half renamed, with a data layer named after the old Locator
name. The analysis therefore refuses the rename and names the other Locator: give each
Locator its own data layer first. A loaded Locator is checked directly. An unloaded one is
found among the layer's referencers, since listing a data layer references its asset: once
the actors assigned to the layer are loaded, an unloaded Locator still referencing it is
taken for one that lists it. For the same reason, the analysis refuses the rename when the
data layer rules cannot derive the new data layer name (their rule asset is missing or not
name pattern based).

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
- On failure the dialog turns red, names the failing step and the reason, and offers
  **"Undo everything"**. Closing the window after a failure undoes the rename as well, so a
  half-renamed Locator is never left behind.
- The undo runs once the dialog is closed (see the traps above). It reports through a
  notification, or through a message box when part of it could not be undone.
- The MCP `RenameWorldEventLocator` tool rolls back on its own when a step fails.

When the in-editor world was already modified, the rollback runs in this order:

1. **Close the level**, without a save prompt — step 1 made sure nothing unsaved is lost.
2. **Revert the Perforce files this run opened** — both ends of each asset move — through
   the provider's `FRevert`, and delete the files the move wrote at the new asset paths. The
   engine's `USourceControlHelpers::ApplyOperationAndReloadPackages` wraps this, so the data
   layer assets still in memory are reloaded from disk and the ones left without a file are
   unloaded.
3. **Put back the files you already had open**, from the copies taken before the checkout,
   in the changelist they were in (see [Source control](#source-control)).
4. **Rescan the touched files** in the asset registry, then **reopen the level**, so World
   Partition rebuilds its actor descriptors from what is on disk.
5. **Release the new database identifier** registered by the aborted save (marked
   `DEPRECATED`), and **journal the old identity again** (see the traps above).

When nothing had been modified in memory yet, only the Perforce part runs: the revert and
the files put back.

Pinned actors are unpinned and force-loaded data layers restored even when the user simply
cancels the wizard (the renamer's destructor handles it), so the editor is never left with
actors loaded that were not.

## Source control

- Checkout is automatic and silent (`USourceControlHelpers::CheckOutOrAddFiles`).
- The data layer rename produces both a *delete* at the old path and an *add* at the new
  one; both are tracked in the plan and both end up in the changelist.
- Success moves the files into a new **described** changelist (`FNewChangelist`), leaving
  out the ones that are no longer open: deleting a data layer asset that an earlier rename
  created, and so is only marked for add, just reverts the add.
- **A rename joins the changelist of an earlier rename that is not submitted yet.** The two
  share files, at least the level's World Data Layers, and a file can only be in one
  changelist. A new changelist would leave part of the earlier rename behind, and neither
  could then be submitted without the other. Step 8 recognises such a changelist by its
  description, which starts with `[World Events] Renamed World Event Locator`, moves the
  files there with `FMoveToChangelist`, and appends this rename to the description with
  `FEditChangelist`.
- **Nothing is ever submitted automatically** — you review and submit the changelist
  yourself.
- **A file already open in one of your numbered changelists blocks the rename.** It holds
  work of yours, and step 8 would mix that work with the rename. Step 1 lists each such file
  with its changelist: submit or shelve that changelist, or move the file to the default
  changelist, then run the rename again. The changelist of an earlier rename is the
  exception, since this rename joins it.
- **Files you already have open in the default changelist are accepted.** Step 8 moves
  them into the rename's changelist with the rest, and its message lists them, as does the
  result of the MCP tool, so you can review those changes before submitting.
- **The pending work in files you already have open is protected.** A plain revert would
  throw that work away, so step 2 copies each of them to
  `Saved/WorldEventRename/<timestamp>/` before touching anything, and a rollback only
  reverts the files the run opened itself. The others are opened again, get their content
  back from the copy, and are moved back to the changelist they were in: the cleanup of an
  old data layer asset reverts its file, and opening it again would land it in the default
  changelist. The copies are deleted with the renamer, unless one could not be put back: the
  rollback summary then gives their location.

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
  warning** — the rename still succeeded and the files stay in the changelist they were in.
- **Renaming a Locator again before submitting logs an asset registry warning** for each of
  its old data layer assets: `package was marked as deleted in editor, but has been modified
  on disk`. Those assets were only marked for add, and the registry sees their file change
  after the editor deleted the package. The warning is harmless: the files are gone and the
  registry no longer lists them.
- **The View Changes window keeps the old names** for the files it listed before the rename.
  It names each file once, when it first lists it (here at the checkout, before the rename),
  and **Refresh** does not update that name. The changelist itself is right; close and
  reopen the window to see the new labels.
- **A rollback reopens the level with no region loaded**, because Sundance sets
  `bDisableLoadingOfLastLoadedRegions`. Load the region again in the World Partition editor.
- The rollback of a Locator placed inside a Level Instance (the step 0 path) has not been
  exercised end to end yet.
- Two paths have not been exercised end to end either: the pin of a World Event Level
  Instance outside the loaded region, and a rollback moving a file back to the changelist of
  an earlier rename.

## Testing it from Python or MCP

- **Load the Locator first.** The MCP tool resolves it among the loaded actors, so pin it:
  find its GUID in `unreal.WorldPartitionBlueprintLibrary.get_actor_descs()` and pass it to
  `pin_actors()`.
- **Hold no world reference across a rename.** A failing rename reloads the level, and a
  `UWorld` or actor reference still held by the script trips the fatal
  `CheckForWorldGCLeaks` error. Keep each script inside a function.
- **Give `MAP CHECK` a world.** `unreal.SystemLibrary.execute_console_command(None, "MAP CHECK")`
  crashes the editor, since `Map_Check` then runs on a null world. Pass the editor world, or
  read the map check that loading the map already runs.
- **What a clean rollback looks like.** After a failed rename:
  - nothing is left open in the default changelist;
  - `p4 diff -se` and `p4 diff -sd` report nothing on the data layer and external actor
    folders;
  - the actor descriptors and data layer assets carry their old names, and none of the
    assets is a redirector;
  - the new identifier is `DEPRECATED` and the old one is live;
  - the last journal block for the Locator's package carries its on-disk version;
  - the map check reports 0 errors.

  These checks all passed on 2026-09-24 for a failure forced after step 7, both with
  nothing open beforehand and with the Locator and one data layer asset already open for
  edit. Those two files came back open, byte-identical to their state before the rename.
- **An actor added to a data layer by hand follows the rename.** On 2026-09-25, a Trigger
  Volume was added to one of the Locator's data layers, saved, and unloaded. The plan
  listed its file (15 files instead of 14) and counted it among the layer's referencers.
  After the rename, its actor descriptor and its file on disk referenced the renamed
  asset, it was in the rename's changelist, and the map check reported 0 errors. Renaming
  the same Locator again before submitting joined that changelist, with no Perforce error.
- **Unloading a freshly placed actor takes a pin and an unpin.** Turning its data layer off
  in the editor left it loaded; `pin_actors()` then `unpin_actors()` unloaded it, once its
  data layer was off.
- **A file open in another numbered changelist blocks the rename.** On 2026-09-25, one file
  of the rename's changelist was moved to a new changelist: step 1 failed, listed only that
  file, and nothing was modified. With the Trigger Volume moved to the default changelist
  instead, the next rename succeeded, joined the earlier rename's changelist, listed the
  Trigger Volume among the files taken from the default changelist, and the map check
  reported 0 errors.
- **Dry runs resolve the unloaded Level Instances.** On 2026-09-25, a dry run (`bApply`
  false) on each of the 7 other Locators of `Holo_WorldEvent_EnemyEncounter`, whose Level
  Instances were all unloaded, built a valid plan. Each Level Instance loaded as soon as its
  data layer was on, so none needed a pin.

## See also

- [Delete World Event](DeleteWorldEvent.md) — the sibling tool whose structure this mirrors
- [World Events MCP Toolsets](WorldEventsMCPToolsets.md) — the agent-facing entry point
- [World Events (work-done narrative)](../../WorkDoneByTopic/WorldEvents.md) — the World Events system context
- [Perforce source control](../PerforceSourceControl.md) — checkout-before-save, changelists
- [Level Instances & OFPA](../LevelInstancesAndOFPA.md) — external actor packages & Level Instance editing

---

**In this section:** [Runtime Grid Reference Tools](RuntimeGridReferenceTools.md) | [Delete World Event](DeleteWorldEvent.md) | **Rename World Event Locator** | [Exclude From Rules tag](ExcludeFromRulesTag.md) | [World Partition Batch Converter](WorldPartitionBatchConverter.md)

Back to [Custom Tools](../CustomTools.md).
