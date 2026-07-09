Parent: [Sundance Maintenance & Validation](../README.md)

# Reference Docs

The single knowledge base for the Sundance / `LV_Overland` maintenance work
(Unreal Engine 5.7, WB Games Montréal). This folder merges what used to be split
between `Docs/` (task-oriented how-to) and `ReferenceDocs/` (exact classes, methods, log
strings) into **one flat set of topic files**, plus the
[`WorldPartitionRulesAnalysis/`](WorldPartitionRulesAnalysis/) sub-folder that holds the
deep, per-asset rule-system analysis series.

It answers "when someone brings up a topic I already worked on, I can respond with
confidence": every claim is grounded in the actual implementation under `D:\Sun`
(engine + `Sundance` game modules) and cross-linked to the exact changelists in
[`WorkDoneByChangelists/P4-History/`](../WorkDoneByChangelists/P4-History/README.md).

For plain-language, *why-it-was-done* narratives, see
[`WorkDoneByTopic/`](../WorkDoneByTopic/README.md).

> Source of truth: code paths point into `D:\Sun\...`. The custom editor logic lives
> in the `WorldBuildingEditor` module
> (`D:\Sun\Sundance\Source\WorldBuildingEditor\`); engine modifications are tagged
> `@third party code - AVA` in `D:\Sun\Engine\Source\`.

## The one-sentence goal

Cleanly eliminate the `mapcheck` "invalid HLOD layer / RuntimeGrid" warnings on
`LV_Overland` by converting levels to World Partition and correcting actors' streaming
properties — **without ever introducing transform drift** — all integrated with
Perforce, Peeves validation, and tooled by builders/commandlets, Blueprint, and batch
scripts.

## Topics

### MapCheck

| Topic | Read when… |
|-------|------------|
| [Fixing MapCheck issues](FixingMapCheckIssues.md) | the project playbook (cause → solution per warning actually hit on `LV_Overland`), plus a generic stock-engine MapCheck catalog in appendix G |

### World Partition streaming

| Topic | Read when… |
|-------|------------|
| [World Partition streaming properties](WorldPartitionStreamingProperties.md) | someone mentions HLODLayer / DataLayers / RuntimeGrid or "invalid HLOD layer" |
| [Level Instances & OFPA](LevelInstancesAndOFPA.md) | partitioned vs non-partitioned, `__ExternalActors__`, the `Level` property |
| [Converting levels to World Partition](ConvertingLevelsToWorldPartition.md) | migrating a non-partitioned level, headless conversion, Nanite crash |
| [Transform drift](TransformDrift.md) | resave changed `RelativeLocation/Rotation/Scale3D` |

### The rule system

| Topic | Read when… |
|-------|------------|
| [World Partition rules](WorldPartitionRules.md) | applying rules, grid sizes, the "Skipped RuntimeGrid override" warning, `IncludeInHLOD` — the practitioner + reference entry point |
| [World Partition rule data-asset analysis](WorldPartitionRulesAnalysis.md) | the deep, per-asset breakdown (index to the analysis documents below) |

The analysis lives in [`WorldPartitionRulesAnalysis/`](WorldPartitionRulesAnalysis/) as a
set of independent documents:
[rule engine mechanics](WorldPartitionRulesAnalysis/RuleEngineMechanics.md) ·
[Runtime Grid rules](WorldPartitionRulesAnalysis/RuntimeGridRules.md) ·
[HLOD Layer rules](WorldPartitionRulesAnalysis/HLODLayerRules.md) ·
[HLOD Layer target assets](WorldPartitionRulesAnalysis/HLODLayerTargetAssets.md) ·
[processing order & priority](WorldPartitionRulesAnalysis/ProcessingOrderAndPriority.md) ·
[data asset inventory](WorldPartitionRulesAnalysis/DataAssetInventory.md).

### Builders & commandlets

| Topic | Read when… |
|-------|------------|
| [Builders & commandlets](BuildersAndCommandlets.md) | the maintenance builders used on `LV_Overland`, with line-level code |
| [World Partition builders catalog](WorldPartitionBuildersCatalog.md) | the full list of every engine + custom WP builder/commandlet and its switches |

### Organization, source control & tooling

| Topic | Read when… |
|-------|------------|
| [Outliner management](OutlinerManagement.md) | organizing the Outliner so rules and tooling target the right actors |
| [Perforce source control](PerforceSourceControl.md) | checkout-before-save, locked files, changelist validation |
| [Peeves submit validation](PeevesSubmitValidation.md) | validation at submit, the WB Peeves system |
| [Auxiliary tools & workflow](AuxiliaryToolsAndWorkflow.md) | Outliner columns, `process_li.bat`, commandlet setup, validation checklist, log extraction |
| [Environment & infrastructure](EnvironmentAndInfra.md) | advanced git, ActorFolders format |
| [Transcription & research](TranscriptionAndResearch.md) | Unreal Fest notes, Phil/William video transcripts, image retouch |

## Conventions

- All content published in this repository is written in **English**.
- **Code identifiers** are exact (`UWorldPartitionRuleBuilder`, `bIsPartitioned`, …).
- **File references** use `path:line` where a specific line matters.
- **Log/message strings** are quoted verbatim so they are searchable.
- Corrections to earlier informal notes are flagged with a **⚠ Note** callout.

*Last reorganized 2026-07-09: merged `Docs/` into `ReferenceDocs/`, then split the
deep rule-system analysis into the [`WorldPartitionRulesAnalysis/`](WorldPartitionRulesAnalysis/)
sub-folder.*
