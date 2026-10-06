# Sundance Maintenance & Validation

Tools and documentation for the maintenance and validation of the **Sundance**
project (Unreal Engine 5), covering World Partition rules, Map Check
warnings/errors, Outliner organization, and related technical workflows.

This file is the root of the documentation. Every other Markdown file links back to
its parent (a `Parent:` line at the top), so you can always walk up the hierarchy to
here, and down again through the section indexes below.

## Contents

- [Repository structure](#repository-structure)
- [Section indexes](#section-indexes)
- [Documentation — jump to a topic](#documentation--jump-to-a-topic)
- [Custom Tools](#custom-tools)
- [Tools](#tools)
- [Changelog](#changelog)
- [Contributing](#contributing)

## Repository structure

```
.
├── ReferenceDocs/              Technical knowledge base (one file per topic)
│   └── WorldPartitionRulesAnalysis/   Deep, per-asset rule-system analysis series
├── Audits/                     Dated content sweeps of LV_Overland, with actor lists
│   └── ValidateWorldPartitionRules-LV_Overland-2026-09-27/
│                               Audit tree: the six warning families of one Validate WP Rules build
├── WorkDoneByTopic/            Plain-language, why-it-was-done narratives
├── WorkDoneByChangelists/      Per-changelist history
│   └── P4-History/             One report per submitted Perforce changelist
└── Tools/                      Source code / scripts
    └── ProcessLevelInstances/  Batch rule builder for Level Instances
```

## Section indexes

- [**Reference Docs**](ReferenceDocs/README.md) — the technical knowledge base
  (exact classes, methods, log strings) plus the
  [World Partition rule data-asset analysis](ReferenceDocs/WorldPartitionRulesAnalysis.md).
- [**Audits**](Audits/README.md) — dated sweeps of the level's content: the problem, what was
  scanned, and the exact list of actors to fix, plus the
  [audit trees](Audits/README.md#audit-trees) that group the warning families of a single
  automated run — currently the
  [Validate World Partition Rules build of 2026-09-27](Audits/ValidateWorldPartitionRules-LV_Overland-2026-09-27/README.md).
- [**Work Done By Topic**](WorkDoneByTopic/README.md) — plain-language, per-topic
  explanations of the 2026 engineering work.
- [**Work Done By Changelists**](WorkDoneByChangelists/README.md) — one factual report
  per submitted Perforce changelist.

## Documentation — jump to a topic

- [World Partition rules](ReferenceDocs/WorldPartitionRules.md)
- [World Partition streaming properties](ReferenceDocs/WorldPartitionStreamingProperties.md)
- [Fixing MapCheck issues](ReferenceDocs/FixingMapCheckIssues.md)
- [Launching the game standalone](ReferenceDocs/LaunchingTheGameStandalone.md) — the cooked
  build, the frontend developer menu, the ImGui debug menu and the runtime grid overlays
- [Outliner management](ReferenceDocs/OutlinerManagement.md)
- [Builders & commandlets](ReferenceDocs/BuildersAndCommandlets.md)
- [TeamCity jobs](ReferenceDocs/TeamCityJobs.md) — the nightly
  [Apply World Partition Rules](https://slc-teamcity.wbiegames.com/buildConfiguration/Sundance_Dev_Tools_ApplyWorldPartitionRules#all-projects)
  and [Generate HLODs (distributed)](https://slc-teamcity.wbiegames.com/buildConfiguration/Sundance_Dev_Tools_HLODs_Distributed_GenerateHLODs#all-projects)
  build configurations
- [Custom Tools (editor console commands)](ReferenceDocs/CustomTools.md)

## Custom Tools

In-editor tools (console commands and editor-mode UI) run interactively with the target
level open. See [Custom Tools](ReferenceDocs/CustomTools.md) for the full list.

- [Runtime Grid Reference Tools](ReferenceDocs/CustomTools/RuntimeGridReferenceTools.md)
  — two linked console commands for `WorldPartitionChangelistValidator` "different runtime
  grid" reference errors: `Editor.ScanRuntimeGridReferenceErrors` scans the open world and
  writes the conflicts to a file, then `Editor.FixRuntimeGridReferenceErrors` aligns each
  referee's `RuntimeGrid` to its referencer, tags both with `ExcludeFromRules`, saves +
  checks out into a described Perforce changelist, and reverts a couple's files if either
  actor fails.
- [Delete World Event](ReferenceDocs/CustomTools/DeleteWorldEvent.md)
  — a guided World Events Editor Mode dialog that fully deletes a World Event (locator,
  level instance(s), data layer instance(s) and data layer asset(s)) from the Overland,
  with live per-step progress, a detailed log, an up-front plan, and a one-click rollback
  on failure. Moves changes to a described Perforce changelist; never submits.
- [Exclude From Rules tag](ReferenceDocs/CustomTools/ExcludeFromRulesTag.md)
  — the `ExcludeFromRules` actor tag that freezes an actor against the World Partition
  rule system, plus the "Rule Exclusion" outliner column to audit which actors are
  excluded.
- [World Partition Batch Converter](ReferenceDocs/CustomTools/WorldPartitionBatchConverter.md)
  — an editor-mode UI that batch-converts non-partitioned Content Browser levels to World
  Partition, with per-level changelists and post-conversion validation.

## Tools

- [ProcessLevelInstances](Tools/ProcessLevelInstances/README.md) — runs the
  `WorldPartitionRuleBuilder` commandlet over a list of Level Instances.

## Changelog

Newest first, one entry per commit that changes what the documentation says. Pure
housekeeping (renames, folder moves, typo passes) is left out.

| Date | Change | Commit |
|------|--------|--------|
| 2026-10-06 | Reworked [RuntimeGrid reference conflict resolution](ReferenceDocs/RuntimeGridReferenceConflictResolution.md) for the revised CL 2112721: a diverging reference cluster is now **cleared to `None`** so it inherits its grid (the default grid in the main world, the sub-world grid inside a Level Instance) instead of being pinned to a named `MainGrid` — matching `SetForcedNoRuntimeGrid` and the manual Vault fix — with the top-level Hogwarts/Hogsmeade demotion trap re-explained (clearing `LI_Hogwarts` drops it to the default grid) and the per-actor guard narrowed to the `IsValidHLODLayer` check against the resolved grid; updated the [MapCheck D5](ReferenceDocs/FixingMapCheckIssues.md#d5--actor-references-an-actor-in-a-different-runtime-grid) entry and the [Reference Docs index](ReferenceDocs/README.md), and cleaned stray line-number artifacts from the design page | [`2587219`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/2587219) |
| 2026-10-06 | Added the [Validate World Partition Rules — Overland only, 2026-10-04 audit](Audits/ValidateWorldPartitionRules-Overland-2026-10-04/README.md) — the [1 054 `Runtime DataLayer without rule` warnings](Audits/ValidateWorldPartitionRules-Overland-2026-10-04/RuntimeDataLayerWithoutRule.md) of TeamCity job `#2111348` *validate Overland Only* (the complement of the [2026-09-27 Hogsmeade tree](Audits/ValidateWorldPartitionRules-LV_Overland-2026-09-27/RuntimeDataLayerWithoutRule.md), discarding Hogsmeade/Hogwarts/Mission/Dungeon), read through the run's new per-actor `Matching DataLayer rules` field into six remediation buckets — author `DA_SANTUARY_ConversationHub_PerConversation_Rules` for the 105 one-to-one conversation Level Instances (the `DA_SANTUARY_Vivarium_Rules` pattern) and `DA_AUTOMATION_Rules` for the 11 `POI_*`, clear the 296 redundant ConversationHub child-mesh layers and the 557 `DL_OVERLAND` residue (255 of them under the `LI_Sanctuary` exclusion), and refer the 64 World Event gameplay layers and 21 cross-region leaks to their owners; shipped the 1 054-row inventory CSV and linked the tree from the [Audits index](Audits/README.md#audit-trees) | [`230f64d`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/230f64d) |
| 2026-10-05 | Added [RuntimeGrid reference conflict resolution](ReferenceDocs/RuntimeGridReferenceConflictResolution.md) — the design of CL 2112721, the rule-builder pass that reads `FWorldPartitionActorDesc::References`, compares the resolved RuntimeGrids and moves a whole diverging reference cluster onto `MainGrid` instead of the reported edge, with the measured `LV_Overland` partition table and descriptor counts behind the Hogwarts/Hogsmeade verdict: inert inside the sub-worlds, because their containers hand their own grid down, but one top-level reference away from demoting a whole district, which is why `HogwartsGrid`, `HogsmeadeGrid`, `FarFoliageGrid` and `FarWorldBitmap` are protected; added the fourth solution to [MapCheck D5](ReferenceDocs/FixingMapCheckIssues.md#d5--actor-references-an-actor-in-a-different-runtime-grid) and cross-links from [Effective RuntimeGrid reference validation](ReferenceDocs/EffectiveRuntimeGridReferenceValidation.md) and the [Vault audit](Audits/MapCheckRuntimeGridReferences-Vault-2026-10-05.md) | [`6a9191b`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/6a9191b) |
| 2026-10-05 | Added the [Vault runtime-grid reference audit](Audits/MapCheckRuntimeGridReferences-Vault-2026-10-05.md) — the 3 "different runtime grid" errors of the 2026-10-05 MapCheck on `LV_Overland`, the 1 m bounds condition of `DA_SmallGrid_Rules` that splits a 7-actor reference cluster between `None` and `SmallGrid`, the 6 actors realigned and frozen as changelist 2111842, and the `DA_SmallGrid_Rules` path exclusion proposed as the durable follow-up; added the fix-the-cluster-not-the-edge rule to [MapCheck D5](ReferenceDocs/FixingMapCheckIssues.md#d5--actor-references-an-actor-in-a-different-runtime-grid), corrected [Runtime Grid rules](ReferenceDocs/WorldPartitionRulesAnalysis/RuntimeGridRules.md) to put `DA_SmallGrid_Rules` in its on-save slot with its real conditions, and recorded that the [Runtime Grid Reference Tools](ReferenceDocs/CustomTools/RuntimeGridReferenceTools.md) console commands are absent from the editor build | [`91b009d`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/91b009d) |
| 2026-10-02 | Added [Launching the game standalone](ReferenceDocs/LaunchingTheGameStandalone.md) — picking a green Package badge in UnrealGameSync, `HogwartsLegacy2.exe -skipintro` and the other intro switches behind `USundanceGlobalConfig::HasCompletedIntro()`, the frontend CD icon to the right of the DEV icon, the three developer menu tabs and where their lists come from, `ImGui.ToggleMenu` / the controller Start button / the `debugPanel.*` commands / NetImgui, and the `wp.Runtime.*` runtime hash overlays, loading range overrides and dumps; linked from the [Reference Docs index](ReferenceDocs/README.md) | [`8175f65`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/8175f65) |
| 2026-10-01 | Added [Submitting an engine changelist](ReferenceDocs/SubmittingEngineChangelists.md) — the `//sun/Dev-Engine` stream and its two robomerge bots, the `MTLWKS20850_SunDevEngine` workspace rooted at `D:\SunDevEng`, the two ways to get the change into a Dev-Engine changelist, the Submit Sidekick fields and the robomerge back to `//sun/Dev`, with CL 2102948 as the worked example; linked from the [Reference Docs index](ReferenceDocs/README.md), [Perforce source control](ReferenceDocs/PerforceSourceControl.md) and [Effective RuntimeGrid reference validation](ReferenceDocs/EffectiveRuntimeGridReferenceValidation.md) | [`c3e0c49`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/c3e0c49) |
| 2026-10-01 | Added the [Validate World Partition Rules audit tree](Audits/ValidateWorldPartitionRules-LV_Overland-2026-09-27/README.md) — the six warning families of build [`#18264425`](https://slc-teamcity.wbiegames.com/buildConfiguration/Sundance_Dev_Tools_ContentTools_ValidateWorldPartitionRules/18264425) read as one run: the 85 490 [`Failed to assign DataLayer`](Audits/ValidateWorldPartitionRules-LV_Overland-2026-09-27/FailedToAssignDataLayer.md) rows that are a `-ValidateOnly` artefact rather than a content defect, the [`DA_HM_INT_Rules`](Audits/ValidateWorldPartitionRules-LV_Overland-2026-09-27/FailedToRetrieveDataLayerAsset.md) path match leaking onto 724 nested prop groups and its [later `Missing DataLayer` symptom](Audits/ValidateWorldPartitionRules-LV_Overland-2026-09-27/MissingDataLayer.md), the [2606 runtime layers no rule claims](Audits/ValidateWorldPartitionRules-LV_Overland-2026-09-27/RuntimeDataLayerWithoutRule.md), the [463 provably no-op HLOD overlaps](Audits/ValidateWorldPartitionRules-LV_Overland-2026-09-27/MultipleHLODLayerRules.md), and the [6 legacy `GroupActor`s](Audits/ValidateWorldPartitionRules-LV_Overland-2026-09-27/FailedImport.md) breaking a Sanctuary level; opened the [Audit trees](Audits/README.md#audit-trees) section for this shape of work and documented the [validation build](ReferenceDocs/TeamCityJobs.md#the-validation-build) and its `-ValidateOnly` reporting defect | [`fafe143`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/fafe143) |
| 2026-09-30 | Updated [Effective RuntimeGrid reference validation](ReferenceDocs/EffectiveRuntimeGridReferenceValidation.md) for the final CL 2102948 call site, which keeps the stock `OnInvalidReferenceRuntimeGrid` call inside the new condition instead of a commented-out copy | [`fa0403c`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/fa0403c) |
| 2026-09-30 | Updated [Effective RuntimeGrid reference validation](ReferenceDocs/EffectiveRuntimeGridReferenceValidation.md) — the validation is now always on: the `wp.RuntimeGrid.ValidateReferencesOnEffectiveGrid` switch and the `ValidateContainerDescriptor` trace scope were removed from CL 2102948, and the A/B test now compares the builds before and after the CL; updated the [D5 playbook entry](ReferenceDocs/FixingMapCheckIssues.md#d5--actor-references-an-actor-in-a-different-runtime-grid) and cross-links | [`278b1e6`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/278b1e6) |
| 2026-09-30 | Added [Effective RuntimeGrid reference validation](ReferenceDocs/EffectiveRuntimeGridReferenceValidation.md) — the `wp.RuntimeGrid.ValidateReferencesOnEffectiveGrid` engine switch (pending CL 2102948) that resolves `None` to the inherited grid before reporting "different runtime grid" references, with its exactness argument, performance design and A/B test procedure; added the matching [D5 playbook entry](ReferenceDocs/FixingMapCheckIssues.md#d5--actor-references-an-actor-in-a-different-runtime-grid) and cross-links | [`05a4beb`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/05a4beb) |
| 2026-09-29 | Added the [`DL_OVERLAND` removal pass on `LI_HM_Streets_EXT`](Audits/ManualOverlandDataLayerRemoval-HogsmeadeStreets-2026-09-29.md) — 1109 of the 1114 static meshes of the [2026-09-23 audit](Audits/ManualOverlandDataLayer-Hogwarts-Hogsmeade-2026-09-23.md) stripped and pending in CL 2099933, with the hand-placed verdict checked live and in Perforce history for every actor, and the cause of the `Error Code 32` save failures | [`ad0c627`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/ad0c627) |
| 2026-09-28 | Recorded that the [`LI_Hogsmeade_River` removal pass](Audits/ManualOverlandDataLayerRemoval-HogsmeadeRiver-2026-09-28.md) went out as CL 2097647 — all 417 actors submitted, nothing outstanding | [`4bfba67`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/4bfba67) |
| 2026-09-28 | Added the [`DL_OVERLAND` removal pass on `LI_Hogsmeade_River`](Audits/ManualOverlandDataLayerRemoval-HogsmeadeRiver-2026-09-28.md) — the 439 findings of the [2026-09-23 audit](Audits/ManualOverlandDataLayer-Hogwarts-Hogsmeade-2026-09-23.md) resolved to 417 actors, all stripped and pending in CL 2097633, with the hand-placed verdict re-checked against the rule assets | [`3f8a89c`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/3f8a89c) |
| 2026-09-28 | Added the [`DL_OVERLAND` removal pass on `LI_EntranceHall_EXT`](Audits/ManualOverlandDataLayerRemoval-EntranceHall-2026-09-28.md) — 770 of the 775 actors of the [2026-09-23 audit](Audits/ManualOverlandDataLayer-Hogwarts-Hogsmeade-2026-09-23.md) stripped and submitted as CL 2086955, and the 5 still outstanding | [`2ff85c4`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/2ff85c4) |
| 2026-09-28 | Removed `AddUniqueFile` from the `FWorldEventEditorHelpers` entry of the [editor types inventory](ReferenceDocs/DevelopmentPlan-WorldEventsMCPToolset.md): each tool keeps its own `AddUnique` | [`4a2e1ed`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/4a2e1ed) |
| 2026-09-28 | Documented that [Delete World Event](ReferenceDocs/CustomTools/DeleteWorldEvent.md) and [Rename World Event Locator](ReferenceDocs/CustomTools/RenameWorldEventLocator.md) now share their actor and package helpers in `FWorldEventEditorHelpers` (see the [editor types inventory](ReferenceDocs/DevelopmentPlan-WorldEventsMCPToolset.md)) | [`7463e70`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/7463e70) |
| 2026-09-25 | Documented that [Rename World Event Locator](ReferenceDocs/CustomTools/RenameWorldEventLocator.md) refuses the rename when the Auto DB database cannot be queried, and that its undo only releases the new database identifier when step 1 found it free, so it can no longer deprecate another actor's identifier | [`420902d`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/420902d) |
| 2026-09-25 | Documented that [Rename World Event Locator](ReferenceDocs/CustomTools/RenameWorldEventLocator.md) now refuses the rename when a data layer is shared with another Locator, loaded or not, or when the data layer rules cannot derive its new name, instead of leaving the data layer with the old name | [`ebd21e2`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/ebd21e2) |
| 2026-09-25 | Documented that step 4 of [Rename World Event Locator](ReferenceDocs/CustomTools/RenameWorldEventLocator.md) looks each World Event Level Instance up again by GUID and fails, undoing the rename, if one is gone, instead of renaming its data layer alone | [`452e24b`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/452e24b) |
| 2026-09-25 | Documented the fixes from the CL 2085203 audit in [Rename World Event Locator](ReferenceDocs/CustomTools/RenameWorldEventLocator.md): unloaded World Event Level Instances are pinned (or the rename is refused), the plan is refused while the asset registry is discovering assets and checked again in step 1, a file open in another numbered changelist [blocks the rename](ReferenceDocs/CustomTools/RenameWorldEventLocator.md#source-control), and a failed Auto DB deprecation now rolls back | [`c1110a4`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/c1110a4) |
| 2026-09-25 | Documented that the [Rename World Event Locator](ReferenceDocs/CustomTools/RenameWorldEventLocator.md) tool also repoints actors added to a World Event's data layers by hand, such as a Trigger Volume (verified with an unloaded one), and that renaming a Locator again before submitting now [joins the earlier rename's changelist](ReferenceDocs/CustomTools/RenameWorldEventLocator.md#source-control) and only moves files still open | [`7c60143`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/7c60143) |
| 2026-09-24 | Documented the [Rename World Event Locator](ReferenceDocs/CustomTools/RenameWorldEventLocator.md) safeguards added after testing — step 1 now refuses to start while the level has unsaved changes the undo would discard, a failed validation no longer lets the undo revert or delete files sitting at the target paths, and the View Changes window keeps showing pre-rename labels until reopened | [`987892d`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/987892d) |
| 2026-09-24 | Brought the [Rename World Event Locator design](ReferenceDocs/CustomTools/RenameWorldEventLocator.md) in line with the tested tool — the redirector fixup after the data layer move, the [rollback sequence](ReferenceDocs/CustomTools/RenameWorldEventLocator.md#error-handling--rollback) that closes the level, reverts through the provider (the `USourceControlHelpers` revert skips deleted files), rescans the asset registry and reopens the level, the protection of files already open, the journal re-assert that keeps PEEVES passing, and [Python/MCP testing notes](ReferenceDocs/CustomTools/RenameWorldEventLocator.md#testing-it-from-python-or-mcp) | [`f7921ef`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/f7921ef) |
| 2026-09-23 | Added the [Rename World Event Locator tool](ReferenceDocs/CustomTools/RenameWorldEventLocator.md) design — the naming cascade a Locator name drives (Auto DB row, Level Instance labels, `DL_WE_*` assets, referencing actors), the ordered steps, and [every trap](ReferenceDocs/CustomTools/RenameWorldEventLocator.md#the-traps-and-how-each-one-is-handled) the implementation had to solve, from unloaded referencing actors to PEEVES marker ordering | [`c49cfe6`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/c49cfe6) |
| 2026-09-23 | Made the [`DL_OVERLAND` audit](Audits/ManualOverlandDataLayer-Hogwarts-Hogsmeade-2026-09-23.md) say what it means — every listed actor carries the layer on its own descriptor, and each row now shows the runtime layers written on the actor next to the ones inherited from its Level Instance, with the reasoning cut to the two questions that decide a finding | [`df9fbeb`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/df9fbeb) |
| 2026-09-23 | Split the [Hogwarts and Hogsmeade `DL_OVERLAND` list](Audits/ManualOverlandDataLayer-Hogwarts-Hogsmeade-2026-09-23.md#the-criterion-no-rule-and-a-rule-that-disagrees) on whether the rules process the actor at all — 2682 findings a rule disagrees with, against 365 `PlacedFoliageSkinnedNaniteAssembly` actors that match no rule, for which `DL_OVERLAND` is only the level-wide fallback and the fix is a missing rule rather than an actor edit | [`14d7a04`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/14d7a04) |
| 2026-09-23 | Listed the [hand-placed `DL_OVERLAND` actors under Hogwarts and Hogsmeade](Audits/ManualOverlandDataLayer-Hogwarts-Hogsmeade-2026-09-23.md) — 3047 actors in 13 Level Instances, established as rule-less by the fact that `DA_OVERLAND_Rules` is the only rule targeting the layer and excludes both Outliner paths, with the [full actor list](Audits/ManualOverlandDataLayer-Hogwarts-Hogsmeade-2026-09-23.csv) as a CSV | [`17ed1e8`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/17ed1e8) |
| 2026-09-22 | Explained in the [visual verification page](Audits/OverlandDataLayerRemoval-Captures-2026-09-22.md#why-a-capture-can-look-like-an-open-exterior-view) why an enclosed actor can look exposed in its capture — it is buried in the thickness of a single-sided wall mesh, which vanishes when seen from within — and backed the verdict with an inward 600-direction test and an exterior capture where the highlighted actor does not appear | [`8b93aad`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/8b93aad) |
| 2026-09-22 | Published the `DL_OVERLAND` overlap audit — [Pass 1](Audits/DataLayerOverlap-Overland-Pass1-2026-09-22.md) finding 2865 carriers, [Pass 2](Audits/DataLayerOverlap-Overland-Pass2-2026-09-22.md) narrowing them to the enclosed ones with a calibrated 1470-ray test, the [69 removal candidates](Audits/OverlandDataLayerRemoval-2026-09-22.md), and a [visual verification page](Audits/OverlandDataLayerRemoval-Captures-2026-09-22.md) carrying an editor capture of each of the 30 Hogwarts actors beside its Outliner Data Layer row | [`8d3c6b6`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/8d3c6b6) |
| 2026-09-17 | Explained [the 391 nested Level Instances](Audits/OverlandExteriorDataLayerOverlap-2026-09-17.md#the-391-nested-level-instances) of the river audit — 391 placements of only 10 shared assets, cascading `DL_OVERLAND` onto 97 child actors — and corrected the affected placement count to 3376 | [`e1c5a41`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/e1c5a41) |
| 2026-09-17 | Added [Which actor actually carries the layer](Audits/OverlandExteriorDataLayerOverlap-2026-09-17.md#which-actor-actually-carries-the-layer) to the [exterior data layer overlap audit](Audits/OverlandExteriorDataLayerOverlap-2026-09-17.md) — `DL_OVERLAND` sits on all 1480 actors themselves while `DL_HW_EXT` is inherited from `LI_EntranceHall_EXT` — and completed the Hogwarts inherited layers with `DL_HOGWARTS` | [`ac05ca2`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/ac05ca2) |
| 2026-09-17 | Removed the 1480-row actor tables from the [exterior data layer overlap audit](Audits/OverlandExteriorDataLayerOverlap-2026-09-17.md), leaving the reasoning and the counts, and split the export into a [Hogwarts](Audits/OverlandExteriorDataLayerOverlap-Hogwarts-2026-09-17.csv) and a [Hogsmeade River](Audits/OverlandExteriorDataLayerOverlap-HogsmeadeRiver-2026-09-17.csv) CSV | [`0c8ce3c`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/0c8ce3c) |
| 2026-09-17 | Shortened the [exterior data layer overlap audit](Audits/OverlandExteriorDataLayerOverlap-2026-09-17.md) paths to their last four Outliner segments, added an inherited data layers column, and corrected the inherited layers of the two actors nested inside a river container | [`c174900`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/c174900) |
| 2026-09-17 | Reduced the [exterior data layer overlap audit](Audits/OverlandExteriorDataLayerOverlap-2026-09-17.md) lists to one line per actor — label and full Outliner path — and moved the class, Guid, data layers, level assets and bounds into a downloadable CSV of 1502 placements, since split [per area](Audits/README.md#the-audits) | [`123c843`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/123c843) |
| 2026-09-17 | Put the full Outliner path back under every actor of the [exterior data layer overlap audit](Audits/OverlandExteriorDataLayerOverlap-2026-09-17.md), in parentheses beneath the label and soft-wrapped so the cell breaks across lines rather than overflowing | [`59ca795`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/59ca795) |
| 2026-09-17 | Made the actor tables of the [exterior data layer overlap audit](Audits/OverlandExteriorDataLayerOverlap-2026-09-17.md) readable by stating the shared Outliner prefix once per list, and added a section explaining how to rebuild a full path from it | [`5e1301b`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/5e1301b) |
| 2026-09-17 | Documented the [World Events MCP toolsets](ReferenceDocs/CustomTools/WorldEventsMCPToolsets.md) with their [development plan](ReferenceDocs/DevelopmentPlan-WorldEventsMCPToolset.md) and [demo script](ReferenceDocs/Demo-WorldEventsMCPToolset.md), opened a Development plans section holding also the [manual runtime Data Layer cleanup](ReferenceDocs/DevelopmentPlan-ManualRuntimeDataLayerCleanup.md) plan, and refreshed the [Delete World Event](ReferenceDocs/CustomTools/DeleteWorldEvent.md) and [Batch Converter](ReferenceDocs/CustomTools/WorldPartitionBatchConverter.md) pages | [`595ea4d`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/595ea4d) |
| 2026-09-17 | Gave every actor in the [exterior data layer overlap audit](Audits/OverlandExteriorDataLayerOverlap-2026-09-17.md) its Outliner path, and corrected the totals to count unique actors rather than Level Instance placements (1502 → 1480) | [`8abb2e5`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/8abb2e5) |
| 2026-09-17 | Opened the [Audits](Audits/README.md) section with the [Overland exterior data layer overlap](Audits/OverlandExteriorDataLayerOverlap-2026-09-17.md) audit — why `DL_OVERLAND` on top of `DL_HW_EXT` / `DL_HM_EXT` splits streaming cells, and the actors carrying it | [`a527465`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/a527465) |
| 2026-09-16 | Gave every document a `## Contents` navigation list of its own sections, and the rule that keeps it in sync with the headings | [`b984b00`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/b984b00) |
| 2026-09-16 | Added this Changelog section, populated from the relevant history, and the rule that keeps it updated on every commit | [`a4383be`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/a4383be) |
| 2026-09-16 | Grounded the TeamCity jobs page in the shipped `WorldGeneration` scripts: real commandlet command lines, the `@AUTOMATION $OVERLAND` submit tag, and the reporting pipeline that feeds the HTML hub | [`af4f33c`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/af4f33c) |
| 2026-09-16 | Added [TeamCity jobs](ReferenceDocs/TeamCityJobs.md) — the nightly rule pass and the distributed HLOD generation, their parameters and their schedule | [`ee39f69`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/ee39f69) |
| 2026-09-14 | Documented the [MapCheck validation CVars](ReferenceDocs/MapCheckValidationCVars.md) (`wp.editor.MapCheck.*`) disabled for load-time performance (CL 2064105) | [`3dfaff9`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/3dfaff9) |
| 2026-08-18 | Added the [QA test plan](Share/WorldPartitionConversion-QA-TestPlan-2026-08-18.md) for the 650-level World Partition conversion batch | [`261b578`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/261b578) |
| 2026-08-11 | Added the World Partition conversion test plan written for Mark Lento | [`c37c763`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/c37c763) |
| 2026-08-11 | Added the [rules consistency audit](ReferenceDocs/WorldPartitionRulesConsistencyAudit.md) — every registered rule checked against the configured arrays | [`bfacb9d`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/bfacb9d) |
| 2026-08-10 | Added the [rule decision flow charts](ReferenceDocs/WorldPartitionRulesFlowCharts.md) for Data Layer, HLOD and RuntimeGrid resolution | [`21d12b7`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/21d12b7) |
| 2026-07-27 | Refreshed the [skipped RuntimeGrid override warnings](ReferenceDocs/SkippedRuntimeGridOverrideWarnings-2026-07-27.md) snapshot | [`5f87a40`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/5f87a40) |
| 2026-07-24 | Documented `ExcludeFromRuntimeGridRules` with a worked example, plus the manual fix walkthrough for the warning snapshot | [`d474699`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/d474699) |
| 2026-07-20 | Documented the [Runtime Grid Reference Tools](ReferenceDocs/CustomTools/RuntimeGridReferenceTools.md) — the scan and fix console commands, with repro steps | [`ef2772e`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/ef2772e) |
| 2026-07-20 | Documented the [World Partition Batch Converter](ReferenceDocs/CustomTools/WorldPartitionBatchConverter.md) editor-mode tool | [`23e9d60`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/23e9d60) |
| 2026-07-20 | Documented the [`ExcludeFromRules` tag](ReferenceDocs/CustomTools/ExcludeFromRulesTag.md) and the "Rule Exclusion" outliner column | [`5fe796c`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/5fe796c) |
| 2026-07-16 | Documented the [Delete World Event](ReferenceDocs/CustomTools/DeleteWorldEvent.md) editor-mode dialog | [`1cb592a`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/1cb592a) |
| 2026-07-15 | Opened the [Custom Tools](ReferenceDocs/CustomTools.md) section for in-editor console commands | [`d7ba823`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/d7ba823) |
| 2026-07-09 | Reorganized the documentation into the current hierarchy: `Docs/` merged into `ReferenceDocs/`, `Parent:` breadcrumbs everywhere, harmonized naming | [`e2962a2`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/e2962a2) |
| 2026-07-09 | Added the [rule data-asset analysis series](ReferenceDocs/WorldPartitionRulesAnalysis.md) — per-asset breakdown of the rule system | [`a74cfa3`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/a74cfa3) |
| 2026-07-09 | Added the [World Partition builders catalog](ReferenceDocs/WorldPartitionBuildersCatalog.md) — every engine and custom builder with its switches | [`1376cf0`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/1376cf0) |
| 2026-07-09 | Added the [MapCheck fix playbook](ReferenceDocs/FixingMapCheckIssues.md) linking each warning to its World Partition rule cause | [`956b6e9`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/956b6e9) |

## Contributing

- Write everything (docs, code comments, commit messages) in English.
- Put new tools under `Tools/<ToolName>/` with their own `README.md`.
- Put new documentation in `ReferenceDocs/` and link it from
  [`ReferenceDocs/README.md`](ReferenceDocs/README.md).
- Every Markdown file should start with a `Parent:` link to the index (or document)
  one level up, so the documentation hierarchy stays traversable.
- Give each document a `## Contents` navigation list of its own sections, kept in sync with
  its headings (see [`.cursor/rules/markdown-contents.mdc`](.cursor/rules/markdown-contents.mdc)).
- Add an entry at the top of the [Changelog](#changelog) in the same commit that changes
  the documentation (see [`.cursor/rules/readme-changelog.mdc`](.cursor/rules/readme-changelog.mdc)).
