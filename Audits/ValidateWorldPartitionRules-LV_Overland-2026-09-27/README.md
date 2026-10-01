Parent: [Audits](../README.md)

# Validate World Partition Rules — `LV_Overland`, 2026-09-27

Six audits, one source. Every document in this folder is a deep dive into **one warning family**
of a **single** *Validate World Partition Rules* build, triaged in
[`WPRulesReviewer`](../../Tools/WPRulesReviewer/) from the log that build produced. Nothing here is
a separate sweep of the level: the counts all come out of the same 92 452 warnings, which is why
the families cross-reference each other and why they have to be read as a tree rather than as six
independent findings.

## Contents

- [The source build](#the-source-build)
- [The tree](#the-tree)
- [The audits](#the-audits)
- [How the families relate](#how-the-families-relate)
- [Reading order](#reading-order)
- [Supporting data](#supporting-data)

---

## The source build

| | |
|---|---|
| Build configuration | [`Sundance_Dev_Tools_ContentTools_ValidateWorldPartitionRules`](https://slc-teamcity.wbiegames.com/buildConfiguration/Sundance_Dev_Tools_ContentTools_ValidateWorldPartitionRules) |
| Build | [`#18264425`](https://slc-teamcity.wbiegames.com/buildConfiguration/Sundance_Dev_Tools_ContentTools_ValidateWorldPartitionRules/18264425) |
| Log artifact | `Sundance_Validate_27September_validate-LV_Overland.log` — 56.3 MB, 269 968 lines |
| Log time | September 27, 2026, 8:44 AM |
| World | `LV_Overland`, UE 5.8.2, CL 2095946 |
| Builder | `WorldPartitionRuleBuilder` ([Builders & commandlets](../../ReferenceDocs/BuildersAndCommandlets.md)) |
| Reviewed with | `WPRulesReviewer`, exported as `report.txt` on October 1, 2026 |

The command line, read from the `commandline=` line 24 of the log:

```text
-Builder=WorldPartitionRuleBuilder -DataLayerRules -HLODLayerRules -RuntimeGridRules
    -ValidateOnly -ContainOutlinerPathSubstrings="Hogsmeade" … LV_Overland
```

`-ValidateOnly` and the `Hogsmeade` scope are not incidental — they explain both the largest family
of the run (a dry run reported as a failure) and the Hogsmeade concentration of every other one.

What the pass reported:

| Metric | Value |
|---|---:|
| Actors processed | 122 234 |
| `Applied …` assignments | 9 506 |
| Warnings | 92 452 |
| Errors | 0 |
| Anomalies (litigious) | 1 935 |
| Needs review | 90 529 |

## The tree

```
TeamCity build #18264425 — Validate World Partition Rules (LV_Overland, -ValidateOnly)
└── Sundance_Validate_27September_validate-LV_Overland.log — 92 452 warnings
    │
    ├── DataLayer pipeline ─────────────────────────── 90 276 rows
    │   ├── Failed to assign DataLayer ........ 85 490  → FailedToAssignDataLayer.md
    │   │     a dry run reported as a failure — read this one first, it is 92.5 % of the noise
    │   ├── Runtime DataLayer without rule .....  2 606  → RuntimeDataLayerWithoutRule.md
    │   │     no DataLayer rule exists for what the world actually streams
    │   ├── Missing DataLayer ..................  1 450  → MissingDataLayer.md
    │   │     725 defects, logged twice — one rule reaching into nested prop Level Instances
    │   └── Failed to retrieve DataLayerAsset ..    730  → FailedToRetrieveDataLayerAsset.md
    │         names the culprit of the family above: DA_HM_INT_Rules, unanchored path match
    │
    ├── HLODLayer pipeline ──────────────────────────── 463 rows
    │   └── Multiple HLODLayer rule matches ....    463  → MultipleHLODLayerRules.md
    │         DA_FarFoliage_…_Foliage_Mid_Rules leaking into LI_Hogsmeade, overwritten to None
    │
    └── Level loading ─────────────────────────────────── 22 rows
        └── Failed import .......................    22  → FailedImport.md
              11 unique, logged twice — 6 legacy GroupActors in one Sanctuary level

    data/  ── the per-family inventories, one CSV per audit
```

## The audits

| Audit | Rows | Verdict |
|---|---:|---|
| [Failed to assign DataLayer](FailedToAssignDataLayer.md) | 85 490 | **Not a content defect.** The builder's `-ValidateOnly` DataLayer path reports a dry run as a failure; 1 449 of the actors are assigned without a warning by an Apply pass. Fix the builder's logging; touch no content. |
| [Runtime DataLayer without rule](RuntimeDataLayerWithoutRule.md) | 2 606 | No DataLayer rule exists for what the world streams. Split by container coverage: author 3 rules, clear the street residue, settle one shop decision. |
| [Missing DataLayer](MissingDataLayer.md) | 1 450 | One rule targets nested prop Level Instances it should not. Narrow the rule; do **not** author the 704 requested DataLayers. |
| [Failed to retrieve Data Asset](FailedToRetrieveDataLayerAsset.md) | 730 | `DA_HM_INT_Rules` matches on a substring of the *full* outliner path, so every descendant of a `_POP` / `_INT` container inherits the match. Anchor the condition to the container level; 724 of the 730 rows are noise. |
| [Multiple HLODLayer rule matches](MultipleHLODLayerRules.md) | 463 | `DA_FarFoliage_HLODLayer_Foliage_Mid_Rules` leaks into the Hogsmeade Level Instance and is immediately overwritten back to `None`. Exclude that Level Instance; the fix is provably behaviour-neutral. |
| [Failed import](FailedImport.md) | 22 | 6 legacy `GroupActor`s in `LI_Sanctuary_ConversationHub_Props` still reference 11 deleted `StaticMeshActor`s. Delete the groups; `AGroupActor` has no place in a World Partition level. |

Every audit is a **proposal**: it quantifies its family, names a root cause, and costs a correction.
None of them has been applied.

## How the families relate

The four DataLayer families are not four problems. They are four views of the same pipeline, taken
at four different points, and the order in which they are read decides whether they make sense:

- **`Failed to assign DataLayer` is an artefact of the run itself**, not of the level. Until it is
  discounted, every other count in the report is read against a 92.5 % noise floor.
- **`Failed to retrieve DataLayerAsset` and `Missing DataLayer` are the same defect caught one step
  apart** — the asset does not exist at all, versus the asset exists but has no instance in the
  level. The first names the rule (`DA_HM_INT_Rules`); the second could not, which is why reading
  them in that order answers both.
- **`Runtime DataLayer without rule` is the mirror image**: layers the content carries that no rule
  claims. Inside `LI_Pippens_POP` it fires on 115 actors while `Missing DataLayer` fires on 30
  others, and the two sets are **disjoint** — proof that the level is right and the rule's
  granularity is wrong.
- **`Multiple HLODLayer rule matches` and `Failed import` are independent** of all of the above and
  of each other. They can be fixed in any order, by different owners.

## Reading order

1. [Failed to assign DataLayer](FailedToAssignDataLayer.md) — removes 92.5 % of the warnings from
   consideration before anything else is judged.
2. [Failed to retrieve Data Asset](FailedToRetrieveDataLayerAsset.md) — names the single rule asset
   behind the Hogsmeade DataLayer noise, and settles the two questions the next audit leaves open.
3. [Missing DataLayer](MissingDataLayer.md) — the later failure of the same rule.
4. [Runtime DataLayer without rule](RuntimeDataLayerWithoutRule.md) — what the content streams that
   no rule describes.
5. [Multiple HLODLayer rule matches](MultipleHLODLayerRules.md) — the best value per effort of the
   whole run: one condition on one asset, 463 warnings, zero behaviour change.
6. [Failed import](FailedImport.md) — one level, 6 actors, unrelated to the rules.

## Supporting data

Each audit ships the working set its fix needs, in [`data/`](data):

| File | Audit | Shape |
|---|---|---|
| [`failed-to-assign-datalayer-inventory.csv`](data/failed-to-assign-datalayer-inventory.csv) | Failed to assign DataLayer | 331 rows, aggregated per `(DataLayer, Rule, Area, OwningLevelInstance)` |
| [`runtime-datalayer-without-rule-inventory.csv`](data/runtime-datalayer-without-rule-inventory.csv) | Runtime DataLayer without rule | 2 606 rows, one per warning, with the remediation bucket |
| [`missing-datalayer-inventory.csv`](data/missing-datalayer-inventory.csv) | Missing DataLayer | 725 rows, deduplicated to one per actor |
| [`failed-to-retrieve-datalayerasset-inventory.csv`](data/failed-to-retrieve-datalayerasset-inventory.csv) | Failed to retrieve Data Asset | 730 rows, classified container / descendant / empty name |
| [`failed-import-inventory.csv`](data/failed-import-inventory.csv) | Failed import | 22 rows, one per log line |

Code references of the form `Tools/WPRulesReviewer/src/…` point into the reviewer's sources in this
repository; references into `Source/WorldBuildingEditor/…` point into the game module under
`D:\Sun\Sundance`.
