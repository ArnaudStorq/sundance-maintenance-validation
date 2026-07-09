# Reference

A precise, **programmer-facing technical reference** for the Sundance / `LV_Overland`
maintenance work (Unreal Engine 5.7, WB Games Montréal).

This folder is the "when someone brings up a topic I already worked on, I can answer
with confidence" knowledge base. It is deliberately different from the two other
documentation folders:

| Folder | Audience | Style |
|--------|----------|-------|
| [`WorkByTopic/`](../WorkByTopic/README.md) | Anyone | Plain-language story, *why* it was done |
| [`Docs/`](../Docs/README.md) | Practitioner | Task-oriented how-to |
| **`Reference/`** (this folder) | **Me / engineers** | **Exact classes, methods, files, log strings, command lines, gotchas** |

Each file is one topic. Every claim is grounded in the actual implementation under
`D:\Sun` (engine + `Sundance` game modules) and cross-linked to the exact
changelists in [`Reports/P4-History/`](../Reports/P4-History/README.md).

> Source of truth: code paths point into `D:\Sun\...`. The custom editor logic lives
> in the `WorldBuildingEditor` module
> (`D:\Sun\Sundance\Source\WorldBuildingEditor\`); engine modifications are tagged
> `@third party code - AVA` in `D:\Sun\Engine\Source\`.

## Topics

| # | Topic | Read when… |
|---|-------|------------|
| 1 | [World Partition streaming properties](WorldPartitionStreamingProperties.md) | someone mentions HLODLayer / DataLayers / RuntimeGrid or "invalid HLOD layer" |
| 2 | [Level Instances & OFPA](LevelInstancesAndOFPA.md) | partitioned vs non-partitioned, `__ExternalActors__`, the `Level` property |
| 3 | [Builders & commandlets](BuildersAndCommandlets.md) | any `WorldPartitionBuilderCommandlet` run or a custom builder |
| 4 | [Transform drift](TransformDrift.md) | resave changed `RelativeLocation/Rotation/Scale3D` |
| 5 | [Perforce source control](PerforceSourceControl.md) | checkout-before-save, locked files, changelist validation |
| 6 | [Converting levels to World Partition](ConvertingLevelsToWorldPartition.md) | migrating a non-partitioned level, headless conversion, Nanite crash |
| 7 | [Rules, SmallGrid & IncludeInHLOD](RulesSmallGridIncludeInHLOD.md) | the rule system, grid sizes, the "Skipped RuntimeGrid override" warning |
| 8 | [Peeves submit validation](PeevesSubmitValidation.md) | validation at submit, the WB Peeves system |
| 9 | [Auxiliary tools & workflow](AuxiliaryToolsAndWorkflow.md) | Outliner columns, `process_li.bat`, Blueprint utilities, log extraction |
| 10 | [Environment & infrastructure](EnvironmentAndInfra.md) | WSL2/Mercury TURN, advanced git, GameLift, ActorFolders format |
| 11 | [Transcription & research](TranscriptionAndResearch.md) | Unreal Fest notes, Phil/William video transcripts, image retouch |
| 12 | [Cursor & Miro tooling](CursorAndMiroTooling.md) | AI skills workflow, Miro MCP access |
| 13 | [World Partition builders catalog](WorldPartitionBuildersCatalog.md) | the full list of every engine + custom WP builder/commandlet and its switches |

## The one-sentence goal

Cleanly eliminate the `mapcheck` "invalid HLOD layer / RuntimeGrid" warnings on
`LV_Overland` by converting levels to World Partition and correcting actors' streaming
properties — **without ever introducing transform drift** — all integrated with
Perforce, Peeves validation, and tooled by builders/commandlets, Blueprint, and batch
scripts.

## Conventions used in these files

- **Code identifiers** are exact (`UWorldPartitionRuleBuilder`, `bIsPartitioned`, …).
- **File references** use `path:line` where a specific line matters.
- **Log/message strings** are quoted verbatim so they are searchable.
- Corrections to earlier informal notes are flagged with a **⚠ Note** callout.

*Generated 2026-07-09.*
