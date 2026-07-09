Parent: [Sundance Maintenance & Validation](../../README.md)

# Perforce Changelist History — 2026

This folder documents every changelist **submitted by `arnaud.storq` since 2026-01-01**, one Markdown report per changelist.

- **Scope:** original (human-authored) changelists only. Automated `#ROBOMERGE` re-integrations across branches are intentionally excluded.
- **Total changelists documented:** 79
- **File naming:** `YYYY-MM-DD-HH-MM-<short-summary>.md` (timestamp is Perforce server time).
- **Source data:** generated from `p4 changes` / `p4 describe -s`.

## Main themes

| Theme | Description | Related Jira |
|-------|-------------|--------------|
| **LV_Overland Outliner restructure** | Large, incremental cleanup of the `LV_Overland` Outliner: deleting empty folders, moving loose root actors into categorized subfolders (Water, Landscape, Roads, PCG, Environment, Nav, Debug, WorldEvents…), renaming folders. | SUNDANCE-41837, 41854 |
| **World Partition rules & builder** | Hardening the `WorldPartitionRuleBuilder`, fixing relative-transform regressions from CI automation, and reference/lifetime fixes. | SUNDANCE-52910, 54425 |
| **Partitioned streaming migration** | Converting non-partitioned levels to partitioned streaming, then applying WP rules (RuntimeGrid/HLOD) to their actors. | SUNDANCE-62658 |
| **HLOD / MapCheck cleanup** | Fixing invalid-HLOD-layer MapCheck warnings and tuning HLOD rule data assets. | SUNDANCE-41838 |
| **Actor Folders** | New fixup builder for orphaned/duplicated Actor Folders, resaving stale folders, and an engine fix to stop ghost `UActorFolder` creation. | SUNDANCE-41837, 54425 |
| **Outliner tooling & columns** | New Outliner columns (OutlinerPath, IncludeInHLOD), hierarchy export command/commandlet, and non-partitioned-parent hints. | SUNDANCE-41837, 48603 |
| **Misc. editor robustness** | Startup-warning cleanups, Python name-clash fix, crash fixes. | various |

## Index (most recent first)

| Date (server) | CL | Type | Summary | Report |
|---------------|----|------|---------|--------|
| 2026-07-08 09:01 | 1961639 | @MINOR | Add partitioned streaming + WP rules (5 levels) | [link](2026-07-08-09-01-partitioned-streaming-and-wp-rules.md) |
| 2026-07-07 12:03 | 1960226 | @MINOR | Remove DA_SmallGrid_Rules from save rules | [link](2026-07-07-12-03-remove-smallgrid-from-runtime-grid-rules.md) |
| 2026-07-07 06:46 | 1959722 | @MINOR | Apply WP rules to 404 actors (SmallGrid) | [link](2026-07-07-06-46-wp-rules-404-actors-smallgrid.md) |
| 2026-07-06 16:14 | 1959020 | @MINOR | Add DA_SmallGrid_Rules to save rules | [link](2026-07-06-16-14-add-smallgrid-to-runtime-grid-rules.md) |
| 2026-07-06 16:12 | 1959005 | @MINOR | Apply WP rules to Level Instances | [link](2026-07-06-16-12-wp-rules-level-instances.md) |
| 2026-07-06 12:12 | 1958172 | @MINOR | Partitioned streaming (1 level) | [link](2026-07-06-12-12-partitioned-streaming-1-level.md) |
| 2026-07-06 09:52 | 1957917 | @MINOR | Partitioned streaming (6 levels) | [link](2026-07-06-09-52-partitioned-streaming-6-levels.md) |
| 2026-07-02 11:52 | 1954875 | @MINOR | Partitioned streaming (4 levels) | [link](2026-07-02-11-52-partitioned-streaming-4-levels.md) |
| 2026-06-30 09:13 | 1950932 | @MINOR | HLOD NoneInclude min bounds (Hogsmeade) | [link](2026-06-30-09-13-hlod-noneinclude-min-bounds.md) |
| 2026-06-29 15:10 | 1949614 | @MINOR | Partitioned streaming (6 levels) | [link](2026-06-29-15-10-partitioned-streaming-6-levels.md) |
| 2026-06-26 15:57 | 1946247 | @MINOR | Partitioned streaming (88 levels) | [link](2026-06-26-15-57-partitioned-streaming-88-levels.md) |
| 2026-06-10 14:19 | 1920591 | @MINOR | WP rules Dungeon/Mission naming | [link](2026-06-10-14-19-wp-rules-dungeon-mission-naming.md) |
| 2026-06-09 09:31 | 1918257 | @MINOR | Remove HLOD from non-partitioned levels | [link](2026-06-09-09-31-remove-hlod-nonpartitioned-levels.md) |
| 2026-06-08 13:02 | 1916537 | @MINOR | WP rules WorldBitmapStreamingProxy | [link](2026-06-08-13-02-wp-rules-worldbitmapstreamingproxy.md) |
| 2026-06-01 15:19 | 1904278 | @MINOR | Fix 644 MapCheck HLOD warnings | [link](2026-06-01-15-19-fix-644-mapcheck-hlod-warnings.md) |
| 2026-05-29 07:49 | 1901233 | @MINOR | Fix orphan/duplicate Actor Folders | [link](2026-05-29-07-49-fix-orphan-duplicate-actor-folders.md) |
| 2026-05-28 13:20 | 1900064 | @MINOR | Add FixupActorFolders builder | [link](2026-05-28-13-20-add-fixup-actorfolders-builder.md) |
| 2026-05-26 14:39 | 1896115 | @MINOR | Expose ULevel::FixupActorFolders | [link](2026-05-26-14-39-expose-fixupactorfolders.md) |
| 2026-05-25 09:11 | 1893933 | @MINOR | Add Overland_Road_Near exclusions | [link](2026-05-25-09-11-add-overland-road-near-exclusions.md) |
| 2026-05-22 09:04 | 1890839 | @MINOR | Stop ghost UActorFolder assets | [link](2026-05-22-09-04-stop-ghost-actorfolder-assets.md) |
| 2026-05-07 07:14 | 1869530 | @MINOR | Fix crash "Update Redirector References" | [link](2026-05-07-07-14-fix-crash-update-redirector-references.md) |
| 2026-04-29 16:33 | 1857281 | @MINOR | WP Rules improvements | [link](2026-04-29-16-33-wp-rules-improvements.md) |
| 2026-04-22 12:33 | 1844521 | @MINOR | Revert last WP Rules processing | [link](2026-04-22-12-33-revert-wp-rules-processing.md) |
| 2026-04-22 11:04 | 1844356 | @MINOR | Fix LevelViewportToolBar warnings | [link](2026-04-22-11-04-fix-levelviewporttoolbar-warnings.md) |
| 2026-04-21 06:18 | 1841026 | @MINOR | Fix WP rules PackagesToSave transient | [link](2026-04-21-06-18-fix-wp-rules-packagestosave.md) |
| 2026-04-17 14:07 | 1837219 | @MINOR | Release kept references (WP rules) | [link](2026-04-17-14-07-release-references-wp-rules.md) |
| 2026-04-13 09:27 | 1827113 | @MINOR | Fix Books relative transform | [link](2026-04-13-09-27-fix-books-relative-transform.md) |
| 2026-04-09 11:21 | 1822824 | @MINOR | Resave many Actor Folders | [link](2026-04-09-11-21-resave-actor-folders.md) |
| 2026-04-08 07:24 | 1820555 | @MINOR | Fix Python name-clash warning | [link](2026-04-08-07-24-fix-python-name-clash-warning.md) |
| 2026-04-02 09:49 | 1812627 | @MINOR | Fix relative transform (more levels) | [link](2026-04-02-09-49-fix-relative-transform-levels.md) |
| 2026-03-27 14:28 | 1804673 | @MINOR | Fix relative transform (TeamCity) | [link](2026-03-27-14-28-fix-relative-transform-teamcity.md) |
| 2026-03-24 07:39 | 1770358 | @MINOR | Resave child ActorFolders | [link](2026-03-24-07-39-resave-child-actorfolders.md) |
| 2026-03-11 09:21 | 1758012 | @MINOR | WorldEvent DataLayers checkout check | [link](2026-03-11-09-21-worldevent-datalayers-checkout-check.md) |
| 2026-03-09 09:07 | 1753959 | @MINOR | Set Parent Layer None (Foliage Near) | [link](2026-03-09-09-07-set-parent-layer-none-foliage-near.md) |
| 2026-03-06 08:06 | 1751748 | @MINOR | Add LogNonPartitionedLevelInstances cmd | [link](2026-03-06-08-06-add-lognonpartitioned-command.md) |
| 2026-02-25 13:59 | 1738687 | @MINOR | Fix MapCheck invalid HLOD layer | [link](2026-02-25-13-59-fix-mapcheck-invalid-hlod-layer.md) |
| 2026-02-20 05:36 | 1731394 | @MINOR | Outliner "Non Partitioned Parent" | [link](2026-02-20-05-36-outliner-nonpartitioned-parent-message.md) |
| 2026-02-19 11:54 | 1729621 | @BUILDFIX | Undo Outliner column utils (1729587) | [link](2026-02-19-11-54-buildfix-undo-outliner-columns.md) |
| 2026-02-19 11:28 | 1729587 | @MINOR | Outliner "Non Partitioned Parent" (1st) | [link](2026-02-19-11-28-outliner-nonpartitioned-parent-message.md) |
| 2026-02-18 08:03 | 1727387 | @MINOR | Skip non-partitioned LI in RuleBuilder | [link](2026-02-18-08-03-skip-nonpartitioned-li-rulebuilder.md) |
| 2026-02-06 13:30 | 1715232 | @MINOR | Outliner: move Automation actors | [link](2026-02-06-13-30-outliner-move-automation-actors.md) |
| 2026-02-06 13:18 | 1715128 | @MINOR | Outliner: delete 7 empty folders | [link](2026-02-06-13-18-outliner-delete-7-empty-folders.md) |
| 2026-02-06 12:56 | 1715089 | @MINOR | Outliner: move WorldEvents actors | [link](2026-02-06-12-56-outliner-move-worldevents-actors.md) |
| 2026-02-06 11:34 | 1714709 | @MINOR | ScriptableTools icon path robustness | [link](2026-02-06-11-34-scriptabletools-icon-path-robustness.md) |
| 2026-02-06 10:02 | 1714561 | @MINOR | Outliner: delete 156 empty folders | [link](2026-02-06-10-02-outliner-delete-156-empty-folders.md) |
| 2026-02-05 13:50 | 1713064 | @MINOR | Outliner: move Road actors | [link](2026-02-05-13-50-outliner-move-road-actors.md) |
| 2026-02-05 13:48 | 1713060 | @MINOR | Outliner: move blockout actors | [link](2026-02-05-13-48-outliner-move-blockout-actors.md) |
| 2026-02-05 13:46 | 1713057 | @MINOR | Outliner: move Water actors | [link](2026-02-05-13-46-outliner-move-water-actors.md) |
| 2026-02-04 14:06 | 1710528 | @MINOR | Outliner: move PCG exclusion volumes | [link](2026-02-04-14-06-outliner-move-pcg-exclusion-volumes.md) |
| 2026-02-04 11:53 | 1709614 | @MINOR | Outliner: move RVT volumes | [link](2026-02-04-11-53-outliner-move-rvt-volumes.md) |
| 2026-02-04 11:50 | 1709611 | @MINOR | Undo water-exclusion move (1709608) | [link](2026-02-04-11-50-undo-water-exclusion-move.md) |
| 2026-02-04 11:46 | 1709608 | @MINOR | Outliner: move water exclusion volumes | [link](2026-02-04-11-46-outliner-move-water-exclusion.md) |
| 2026-02-04 11:40 | 1709604 | @MAJOR | Outliner: Environment subfolders | [link](2026-02-04-11-40-outliner-environment-subfolders.md) |
| 2026-02-04 07:00 | 1709345 | @MAJOR | Outliner: move PCG grid actors | [link](2026-02-04-07-00-outliner-move-pcg-grid-actors.md) |
| 2026-02-03 13:53 | 1707892 | @MAJOR | Outliner: remove root empty folders | [link](2026-02-03-13-53-outliner-remove-root-empty-folders.md) |
| 2026-02-03 07:43 | 1707391 | @MAJOR | Add Outliner.ExportAllHierarchy | [link](2026-02-03-07-43-add-outliner-export-hierarchy.md) |
| 2026-02-02 09:32 | 1704979 | @MAJOR | Outliner: cleanup debug actors | [link](2026-02-02-09-32-outliner-cleanup-debug-actors.md) |
| 2026-01-29 09:32 | 1697772 | @MAJOR | Outliner: move Landscape actor | [link](2026-01-29-09-32-outliner-move-landscape-actor.md) |
| 2026-01-27 08:13 | 1690531 | @MAJOR | Add Outliner columns | [link](2026-01-27-08-13-add-outliner-columns.md) |
| 2026-01-26 12:36 | 1689769 | @MAJOR | Outliner: rename Hogsmeade | [link](2026-01-26-12-36-outliner-rename-hogsmeade.md) |
| 2026-01-23 08:55 | 1686967 | @MAJOR | Undo Hogsmeade freeze (1686904) | [link](2026-01-23-08-55-undo-hogsmeade-freeze.md) |
| 2026-01-23 07:48 | 1686913 | @MAJOR | Outliner: Hogwarts folder | [link](2026-01-23-07-48-outliner-hogwarts-folder.md) |
| 2026-01-23 07:43 | 1686904 | @MAJOR | Outliner: rename Hogsmeade (reverted) | [link](2026-01-23-07-43-outliner-rename-hogsmeade.md) |
| 2026-01-23 07:26 | 1686885 | @MAJOR | Outliner: Landscape structure | [link](2026-01-23-07-26-outliner-landscape-structure.md) |
| 2026-01-22 07:34 | 1684185 | @MAJOR | Outliner: Water Rivers/Lakes | [link](2026-01-22-07-34-outliner-water-rivers-lakes.md) |
| 2026-01-22 07:32 | 1684180 | @MAJOR | Outliner: RiverDressing to Water | [link](2026-01-22-07-32-outliner-riverdressing-to-water.md) |
| 2026-01-22 07:31 | 1684179 | @MAJOR | Outliner: Roads restructure | [link](2026-01-22-07-31-outliner-roads-restructure.md) |
| 2026-01-22 07:01 | 1684160 | @MAJOR | Outliner: rename Region folders | [link](2026-01-22-07-01-outliner-rename-region-folders.md) |
| 2026-01-21 08:33 | 1682124 | @MAJOR | Outliner: rename TO_CLASSIFY | [link](2026-01-21-08-33-outliner-rename-to-classify.md) |
| 2026-01-21 08:09 | 1682099 | @MAJOR | Outliner: move to TO_CLASSIFY (4) | [link](2026-01-21-08-09-outliner-move-to-classify-4.md) |
| 2026-01-21 07:40 | 1682070 | @MAJOR | Outliner: move to TO_CLASSIFY (3) | [link](2026-01-21-07-40-outliner-move-to-classify-3.md) |
| 2026-01-21 07:32 | 1682066 | @MAJOR | Outliner: move to TO_CLASSIFY (2) | [link](2026-01-21-07-32-outliner-move-to-classify-2.md) |
| 2026-01-21 07:20 | 1682056 | @MAJOR | Outliner: move to TO_CLASSIFY (1) | [link](2026-01-21-07-20-outliner-move-to-classify-1.md) |
| 2026-01-21 06:48 | 1681994 | @MAJOR | Outliner: add TO_CLASSIFY folder | [link](2026-01-21-06-48-outliner-add-to-classify.md) |
| 2026-01-13 11:13 | 1670949 | @MAJOR | Outliner: move assets to Debug | [link](2026-01-13-11-13-outliner-move-assets-debug.md) |
| 2026-01-12 14:17 | 1669945 | @MAJOR | Outliner: add Nav folder | [link](2026-01-12-14-17-outliner-add-nav-folder.md) |
| 2026-01-12 13:30 | 1669784 | @MAJOR | Outliner: move Mercuna to Nav | [link](2026-01-12-13-30-outliner-move-mercuna-nav.md) |
| 2026-01-12 09:57 | 1668736 | @MAJOR | Outliner: delete root empty folders (2) | [link](2026-01-12-09-57-outliner-delete-root-empty-folders-2.md) |
| 2026-01-12 08:05 | 1668632 | @MAJOR | Outliner: delete root empty folders (1) | [link](2026-01-12-08-05-outliner-delete-root-empty-folders-1.md) |

---

*Generated on 2026-07-09. Regenerate by re-running `p4 changes -u Arnaud.Storq -s submitted "@2026/01/01,@now"` (excluding `#ROBOMERGE`) and `p4 describe -s <CL>` for each result.*
