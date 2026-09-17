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
  scanned, and the exact list of actors to fix.
- [**Work Done By Topic**](WorkDoneByTopic/README.md) — plain-language, per-topic
  explanations of the 2026 engineering work.
- [**Work Done By Changelists**](WorkDoneByChangelists/README.md) — one factual report
  per submitted Perforce changelist.

## Documentation — jump to a topic

- [World Partition rules](ReferenceDocs/WorldPartitionRules.md)
- [World Partition streaming properties](ReferenceDocs/WorldPartitionStreamingProperties.md)
- [Fixing MapCheck issues](ReferenceDocs/FixingMapCheckIssues.md)
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
| 2026-09-17 | Put the full Outliner path back under every actor of the [exterior data layer overlap audit](Audits/OverlandExteriorDataLayerOverlap-2026-09-17.md), in parentheses beneath the label and soft-wrapped so the cell breaks across lines rather than overflowing | [`59ca795`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/59ca795) |
| 2026-09-17 | Made the actor tables of the [exterior data layer overlap audit](Audits/OverlandExteriorDataLayerOverlap-2026-09-17.md) readable by stating the shared Outliner prefix once per list, and added a [Reading the actor lists](Audits/OverlandExteriorDataLayerOverlap-2026-09-17.md#reading-the-actor-lists) section explaining how to rebuild a full path | [`5e1301b`](https://github.com/ArnaudStorq/sundance-maintenance-validation/commit/5e1301b) |
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
