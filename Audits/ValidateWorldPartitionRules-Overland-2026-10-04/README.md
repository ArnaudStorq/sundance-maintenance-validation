Parent: [Audits](../README.md)

# Validate World Partition Rules — Overland only, 2026-10-04

One audit from one build. This folder analyses the **`Runtime DataLayer without rule`** family of a
single *validate Overland Only* pass — the run that **discards** Hogsmeade, Hogwarts, Mission and
Dungeon, so what remains is the Overland region proper plus the Sanctuary content under it.

It is the **complement** of the [2026-09-27 audit tree](../ValidateWorldPartitionRules-LV_Overland-2026-09-27/README.md),
which scoped Hogsmeade. The two cover the level from opposite sides; neither supersedes the other.

## Contents

- [The source build](#the-source-build)
- [The audit](#the-audit)
- [Supporting data](#supporting-data)

---

## The source build

| | |
|---|---|
| TeamCity job | `#2111348` — *validate Overland Only* |
| Run time | October 4, 2026, 06:00 (log opened `10/04/26 08:48:27`) |
| Log artifact | `Sundance.log` — 73.5 MB, 345 215 lines |
| Build version | `++sun+Dev-TeamCity-Code-CL-2110752` |
| World | `LV_Overland` |
| Builder | `WorldPartitionRuleBuilder` ([Builders & commandlets](../../ReferenceDocs/BuildersAndCommandlets.md)) |

The command line, read from the `commandline=` metadata:

```text
-run=WorldPartitionBuilderCommandlet -Builder=WorldPartitionRuleBuilder
    -DataLayerRules -HLODLayerRules -RuntimeGridRules -ValidateOnly
    -ContainOutlinerPathSubstrings="" -DiscardOutlinerPathSubstrings="mission,dungeon,hogwarts,hogsmeade"
    -BuildMachine -Unattended LV_Overland
```

`-ValidateOnly` and the `Discard` filter are the two facts that shape the whole report: nothing is
checked out or saved, and everything Hogsmeade/Hogwarts/Mission/Dungeon is filtered out by outliner
path. What the pass reported:

| Metric | Value |
|---|---:|
| Actors loaded | 216 636 |
| Rules would have modified | 63 557 |
| Warnings (all families) | 54 892 |
| `Runtime DataLayer without rule` | 1 054 |

## The audit

| Audit | Rows | Verdict |
|---|---:|---|
| [Runtime DataLayer without rule](RuntimeDataLayerWithoutRule.md) | 1 054 | Author 2 rules (Sanctuary ConversationHub variants, `POI_` automation), clear two residue populations (`DL_OVERLAND`, ConversationHub child meshes), refer World Event and cross-region layers to their owners. |

The audit is a **proposal**: it quantifies the family, names a root cause per population, and costs a
correction. Nothing has been applied.

## Supporting data

| File | Shape |
|---|---|
| [`data/runtime-datalayer-without-rule-inventory.csv`](data/runtime-datalayer-without-rule-inventory.csv) | 1 054 rows, one per warning, columns `Family`, `DataLayer`, `ActorKind`, `CandidateRule`, `Container`, `ActorPath`, `DataLayerAsset` |

Code references of the form `Source/WorldBuildingEditor/…` point into the game module under
`D:\Sun\Sundance`; references into `ReferenceDocs/…` and `Tools/…` point into this repository.
