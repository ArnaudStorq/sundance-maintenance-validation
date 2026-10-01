Parent: [Validate World Partition Rules — LV_Overland, 2026-09-27](README.md)

# Audit — "Failed to retrieve Data Asset" warnings on `LV_Overland`

Status: proposal (no change applied)
Scope: every `Failed to retrieve DataLayerAsset` warning of one *Validate WP Rules* pass
Source: `Sundance_Validate_27September_validate-LV_Overland.log` (log of September 27, 2026 8:44 AM),
exported by `WPRulesReviewer` as `report.txt` on October 1, 2026
Raw data: [`data/failed-to-retrieve-datalayerasset-inventory.csv`](data/failed-to-retrieve-datalayerasset-inventory.csv) (730 rows)

Companion audit: [Missing DataLayer](MissingDataLayer.md) — same root
cause, different warning family. This audit **closes the two open questions** that one left in its
verification plan: which rule asset owns the `DL_HM_` derivation, and whether the rule engine can
express "direct child of `{Shops,Buildings}`".

## Contents

- [1. Executive summary](#1-executive-summary)
- [2. What the warning means](#2-what-the-warning-means)
- [3. Measured facts](#3-measured-facts)
  - [3.1 Volume and shape](#31-volume-and-shape)
  - [3.2 Localisation — one container, one defect](#32-localisation--one-container-one-defect)
  - [3.3 Nesting depth — the discriminator](#33-nesting-depth--the-discriminator)
  - [3.4 Distribution per owning Level Instance](#34-distribution-per-owning-level-instance)
  - [3.5 Ground truth — the DataLayers that really exist](#35-ground-truth--the-datalayers-that-really-exist)
- [4. The rule under audit](#4-the-rule-under-audit)
  - [4.1 The name transform is correct — for containers](#41-the-name-transform-is-correct--for-containers)
- [5. Root cause](#5-root-cause)
  - [5.1 The leak](#51-the-leak)
  - [5.2 No notion of hierarchy in the name derivation](#52-no-notion-of-hierarchy-in-the-name-derivation)
  - [5.3 The 5 empty-name rows](#53-the-5-empty-name-rows)
  - [5.4 The one true positive](#54-the-one-true-positive)
- [6. The twin symptom — why silencing the warnings is not enough](#6-the-twin-symptom--why-silencing-the-warnings-is-not-enough)
- [7. Proposed corrections](#7-proposed-corrections)
  - [Option 1 — Parent-anchored matching (recommended, structural)](#option-1--parent-anchored-matching-recommended-structural)
  - [Option 2 — Gate the match on an actor tag (immediate, data-only)](#option-2--gate-the-match-on-an-actor-tag-immediate-data-only)
  - [Option 3 — Filter by bounds (partial, not recommended alone)](#option-3--filter-by-bounds-partial-not-recommended-alone)
  - [Option 4 — Author the 704 missing DataLayerAssets (rejected)](#option-4--author-the-704-missing-datalayerassets-rejected)
  - [Recommended sequence](#recommended-sequence)
- [8. Acceptance criteria](#8-acceptance-criteria)
- [9. Risks](#9-risks)
- [10. Findings for `WPRulesReviewer` itself](#10-findings-for-wprulesreviewer-itself)
- [11. Verification plan](#11-verification-plan)
- [12. Appendix — reproducing the figures](#12-appendix--reproducing-the-figures)

---

## 1. Executive summary

The run reports **730 `Failed to retrieve DataLayerAsset` warnings**. All 730 come from a **single
rule asset**, `/Game/Levels/Overland/Hogsmeade/DataLayers/DA_HM_INT_Rules`, and 724 of them are
noise produced by an over-broad matching condition — not by missing content.

**Root cause.** `DA_HM_INT_Rules` matches on "outliner path contains `LI_Hogsmeade` **and** `_POP`"
(resp. `_INT`). `OutlinerPathContains` is a plain substring test against the **full** outliner path,
so every descendant of a `_POP` / `_INT` container inherits the match, because the container's name
is part of every descendant's path. The rule then derives a DataLayer name from the *descendant's
own* name and asks for `DL_HM_HW_Book_Stack_Small_B12` — a layer that does not exist and must not.

**Verdict.**

| Class | Rows | Nature | Owner |
| --- | ---: | --- | --- |
| Descendant actors matched by path leakage | **724** | False positive — rule scope defect | Tools / rule configuration |
| Matched actors whose name carries no `LI_` prefix | **5** | Authoring defect — naming convention | Content (Hogsmeade) |
| Container with a genuinely missing DataLayerAsset | **1** | True positive | Content (Hogsmeade) |

**Recommendation.** Do **not** author the 704 requested DataLayer assets. Gate the rule on an actor
tag immediately (data-only, no code), then make the match structurally parent-anchored in the engine.
Expected result: 730 warnings → **6** after the first step, → **0** after the content fixes.

| | Before | After step 1 | After step 3 |
| --- | ---: | ---: | ---: |
| `Failed to retrieve DataLayerAsset` rows | 730 | 6 | 0 |
| DataLayer assets to author | 704 | 1 | 1 |
| Rule assets to edit | — | 1 | 1 |

**The rule is currently inert.** For `DA_HM_INT_Rules` this run produced 730 warnings and
**0 `Applied DataLayer` rows**. The whole DataLayer half of the pipeline reports 2 `Applied
DataLayer` rows on the entire world, both `DL_SKY` — which is why the defect went unnoticed.

---

## 2. What the warning means

```
LogWorldPartitionRules: Warning: Failed to retrieve DataLayerAsset '<Name>' for actor '<Path>'
```

The rule **matched** the actor, resolved an expected DataLayer *name*, but no `UDataLayerAsset` with
that name exists anywhere in the project, so the assignment was dropped:

`Source/WorldBuildingEditor/WorldPartition/DataLayer/DataLayerRuleSubsystem.cpp:847-851`:

```cpp
if (!DataLayerAsset)
{
    UE_LOG(LogWorldPartitionRules, Warning, TEXT("Failed to retrieve DataLayerAsset '%s' for actor '%s'"), *TargetDataLayerResult.ExpectedDataLayerName, *ActorOrDesc.GetOutlinerFullPath());
    return false;
}
```

It is a **post-match** failure: every occurrence implies the rule considered the actor in scope. That
distinction is what makes this family diagnostic — it indicts the rule's *targeting*, not the level.

Distinguish it from its two neighbours:

| Family | Meaning |
| --- | --- |
| **Failed to retrieve DataLayerAsset** (this audit) | the `UDataLayerAsset` does not exist in the project |
| [Missing DataLayer](MissingDataLayer.md) | the asset exists but has no `DataLayerInstance` in the level |
| [Runtime DataLayer without rule](RuntimeDataLayerWithoutRule.md) | the actor carries a layer that no matching rule targets |

In `WPRulesReviewer` this family is `IssueTypes.OfMessage`, surfaced in the *Filter by Type*
dropdown as **Failed to retrieve DataLayerAsset**:

```37:38:Tools/WPRulesReviewer/src/WPRulesReviewer.Core/Models/IssueTypes.cs
        if (message.StartsWith("Failed to retrieve DataLayerAsset '", StringComparison.Ordinal))
            return "Failed to retrieve DataLayerAsset";
```

> **Reviewer gap.** The oracle classifies these rows as `WarningKind.Other` and overwrites their
> reason with the generic `"Rule warning"`, so the exported `report.txt` keeps none of the raw
> message: the expected layer name and the actor path are both lost. All 730 rows are buried in the
> 87 923-row `Rule warning` bucket, and this audit had to go back to the engine log to recover them.
> See §7.1.

---

## 3. Measured facts

### 3.1 Volume and shape

| Metric | Value |
| --- | ---: |
| Warning rows | 730 |
| Distinct actors | 730 (no duplication) |
| Distinct expected DataLayer names | 704 |
| Rows with an **empty** expected name | 5 |
| Expected names prefixed `DL_HM_` | 725 / 725 (100 % of non-empty) |
| Rule assets responsible | **1** |

Unlike the `Missing DataLayer` family — logged exactly twice per defect — this family is logged
**once per actor**. Read the counts here as defects, not rows.

704 names for 725 actors: 21 prop groups are instanced in more than one shop and ask for the same
name (`DL_HM_HW_Book_Stack_Small_D` is requested by 5 different actors). Further proof the name is
derived from the *prop asset* name, not from a streaming decision.

### 3.2 Localisation — one container, one defect

All 730 rows live under the same parent:

```
LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade/{Shops|Buildings}/...
```

| Area | Rows |
| --- | ---: |
| `Shops` | 723 |
| `Buildings` | 7 |

Nothing outside Hogsmeade is affected.

### 3.3 Nesting depth — the discriminator

Containers sit at outliner depth 6.

| Depth | Rows | What it is |
| ---: | ---: | --- |
| 6 | 1 | the building Level Instance itself (`LI_Water_Mill_POP`) |
| 7 | 681 | prop group nested directly in a shop |
| 8 | 11 | prop group nested one level deeper |
| 9 | 37 | prop group under `.../Mesh/LA_INT_Props/` |

**729 of 730 rows (99.9 %) are below the container level.** Exactly one is a legitimate container.

### 3.4 Distribution per owning Level Instance

| Owning Level Instance | Rows |
| --- | ---: |
| `LI_Tomes_POP` | 552 |
| `LI_Scrivenshafts_INT` | 33 |
| `LI_Pippens_POP` | 32 |
| `LI_Flutes_POP` | 23 |
| `LI_Honeydukes_POP` | 19 |
| `LI_Dervish_POP` | 16 |
| `LI_PostOffice_POP` | 14 |
| `LI_Cauldron_POP` | 10 |
| `LI_PostOffice_INT` | 7 |
| `LI_Ollivanders_INT` | 7 |
| `LI_Water_Mill_POP` | 7 |
| `LI_Emporium_INT` | 3 |
| `LI_Zonkos_INT` | 2 |
| `LI_BingleBlatch_INT` | 2 |
| `LI_Ollivanders_POP`, `LI_ThreeBroom_POP`, `LI_Hogshead_INT` | 1 each |
| **Total** | **730** |

`LI_Tomes_POP` alone drives 76 % of the noise: it is the bookshop, densely filled with
individually-instanced book props. The volume tracks **prop density**, not container count — so the
warning count is **unbounded** and grows with every dressing pass until the scope is fixed.

### 3.5 Ground truth — the DataLayers that really exist

A filesystem inventory of `Content/**/DL_*.uasset` gives the authoritative answer the report cannot:

| Set | Count |
| --- | ---: |
| `DL_*` DataLayerAssets in the project | 1 580 |
| `DL_HM_*` DataLayerAssets | **66** |
| `DL_HM_*` names the rule requested | 704 |

The 66 that exist follow one convention — `DL_HM_<CONTAINER>_<INT\|POP>`, uppercase — and map
one-to-one onto shops and buildings: `DL_HM_TOMES_POP`, `DL_HM_PIPPENS_INT`, `DL_HM_BUILDING_B_POP`,
`DL_HM_SCRIVENSHAFTS_INT`, … **The rule asks for 704 layers while Hogsmeade owns 66, one per
container.** The request itself is the anomaly.

---

## 4. The rule under audit

Configuration read directly from the binary of `DA_HM_INT_Rules.uasset`:

| Property | Value |
| --- | --- |
| `TargetDataLayerMode` | `NamePatternBased` |
| `TargetDataLayerNamePatterns` | `LI_` → `DL_HM_`, then `_One_` → `_`, `_Two_` → `_`, … `_Nine_` → `_` |
| `MatchingConditions[0]` | `LogicOperator = AND`, `ActorTypes = [LevelInstance]`, `OutlinerPathContains = [LI_Hogsmeade, _INT]` |
| `MatchingConditions[1]` | `LogicOperator = AND`, `ActorTypes = [LevelInstance]`, `OutlinerPathContains = [LI_Hogsmeade, _POP]` |
| `ExclusionCriteria.OutlinerPathsToExclude` | `[_EXT, _Bridge]` |

This **answers open question 2 of the companion audit**: the `DL_HM_` prefix is *data-driven*
(`TargetDataLayerNamePatterns`), not hardcoded in C++. Narrowing the rule is a `.uasset` edit, not a
code change.

The two sibling rules in the same folder, `DA_HM_EXT_Rules` and `DA_HOGSMEADE_Rules`, use
`ETargetDataLayerMode::Manual` with an explicit `TargetDataLayer` and emit none of these warnings.
`DA_HM_INT_Rules` is the only `NamePatternBased` DataLayer rule producing `DL_HM_*` names — which is
why 100 % of the 730 rows expect a `DL_HM_*` name, and why this audit names a single culprit where
the companion audit could not.

### 4.1 The name transform is correct — for containers

Replaying the transform offline against the 82 `_POP` / `_INT` containers that actually exist under
`LI_Hogsmeade/{Shops,Buildings}`, and resolving each result against the 66 real assets:

| Container set | Count | Resolves to an existing asset |
| --- | ---: | ---: |
| All `Shops` / `Buildings` containers | 82 | **81** |
| Unresolved | 1 | `LI_Water_Mill_POP` → `DL_HM_Water_Mill_POP` |

The `_One_` … `_Nine_` patterns exist precisely to collapse variants onto a shared layer:
`LI_Building_B_Five_POP` → `DL_HM_Building_B_POP` → asset `DL_HM_BUILDING_B_POP`. Resolution goes
through a `TMap<FName, …>`, so it is **case-insensitive** and `DL_HM_Tomes_POP` correctly finds
`DL_HM_TOMES_POP`.

**The design is sound at 99 %. The defect is scope, not naming.**

---

## 5. Root cause

### 5.1 The leak

`Source/WorldBuildingEditor/WorldPartition/WorldPartitionRuleSubsystem.cpp:1190-1208`:

```cpp
//Check Outliner Path
if (!RuleCondition.OutlinerPathContains.IsEmpty())
{
    FString ActorOutlinerFullPath = ActorOrDesc.GetOutlinerFullPath();

    for (const FString& PathSubstring : RuleCondition.OutlinerPathContains)
    {
        if (ActorOutlinerFullPath.Contains(PathSubstring))
        {
            bOutlinerPathMatches = true;
            if (RuleCondition.LogicOperator == EDataLayerRuleOperator::OR) break;
        }
        else if (RuleCondition.LogicOperator == EDataLayerRuleOperator::AND)
        {
            bOutlinerPathMatches = false;
            break;
        }
    }
}
```

`_POP` is satisfied by the container *and* by everything underneath it:

```
…/LI_Hogsmeade/Shops/LI_Tomes_POP                             <- intended match
…/LI_Hogsmeade/Shops/LI_Tomes_POP/LI_HW_Book_Stack_Small_B12  <- unintended match, same substring
```

With `ActorTypes = [LevelInstance]`, the nested prop groups satisfy the type condition too — prop
dressing is authored as nested Level Instances, a sound content decision for reuse — so the `AND`
evaluates to a match.

This **answers open question 1 of the companion audit**: the rule engine **cannot** express "direct
child of `{Shops,Buildings}`". `OutlinerPathContains` has no notion of position, and
`OutlinerPathsToExclude` is the same substring test inverted, so no exclusion string can separate a
container from its own descendants. A structural fix needs a new condition (§6, option 1).

### 5.2 No notion of hierarchy in the name derivation

`Source/WorldBuildingEditor/WorldPartition/DataLayer/DataLayerRuleSubsystem.cpp:119-137`:

```cpp
//Resolve the DataLayer name based on the ActorName
FString DataLayerName = ActorOrDesc.GetActorNameOrLabel();
for (auto& [MatchSubstring, ReplacementSubstring] : RuleAsset.TargetDataLayerNamePatterns)
{
    if (!MatchSubstring.IsEmpty())
    {
        DataLayerName.ReplaceInline(*MatchSubstring, *ReplacementSubstring);
    }
}

// Skip if DataLayer doesn't start with 'DL_'. No need to search further if this is not the case
if (!DataLayerName.StartsWith(TEXT("DL_")))
{
    return UDataLayerRuleSubsystem::FTargetDataLayerResult();
}

//Retrieve the DataLayerAsset by name
const TSoftObjectPtr<UDataLayerAsset> DataLayerAsset = FDataLayerAssetsCache::GetDataLayerAssetByName(FName(DataLayerName));
return UDataLayerRuleSubsystem::FTargetDataLayerResult(DataLayerAsset, DataLayerName);
```

A nested actor is named after **itself**, never after its owning container. Two consequences:

- A matched descendant can only ever ask for a private per-prop layer.
- When the composed name does not start with `DL_`, the result is a default-constructed
  `FTargetDataLayerResult` whose `ExpectedDataLayerName` is **empty** — the 5 rows that log
  `Failed to retrieve DataLayerAsset ''`.

### 5.3 The 5 empty-name rows

These actors match the rule (Level Instances under a `_POP` path) but their name has no `LI_` prefix,
so the transform yields a name that never reaches the `DL_` test:

| Actor |
| --- |
| `…/Buildings/LI_Water_Mill_POP/SM_ToolStand_A` |
| `…/Shops/LI_Flutes_POP/SM_Tool_Rack_A2` |
| `…/Shops/LI_Flutes_POP/SM_HW_Book_L_Medium_C9` |
| `…/Shops/LI_Pippens_POP/SM_CashRegister_A3` |
| `…/Shops/LI_Pippens_POP/SM_INT_Pippens_Fireplace_A2` |

An `SM_` prefix on a Level Instance is a naming-convention violation. These 5 rows disappear with the
scope fix anyway, but the mis-naming is worth correcting on its own: it makes every name-pattern rule
in the project silently skip these actors.

### 5.4 The one true positive

`LI_Water_Mill_POP` expects `DL_HM_Water_Mill_POP`. The 66 existing `DL_HM_*` assets contain no
`WATER_MILL` entry: this is the only row in the family that reflects missing content, and it is the
same single gap the companion audit identified.

---

## 6. The twin symptom — why silencing the warnings is not enough

The same run reports 324 rows of *"Runtime DataLayer 'X' assigned to the actor but targeted by no
rule"* naming a `DL_HM_*` layer, 323 of them `DL_HM_PIPPENS_POP`:

```
| Low | Warning | DL_HM_PIPPENS_POP | … | `…/Shops/LI_Pippens_POP/SM_HW_Book_L_Medium_A2` |
  Runtime DataLayer 'DL_HM_PIPPENS_POP' assigned to the actor but targeted by no rule | 1 |
```

Those props **already carry the correct layer** — their container's. The compliance check compares
each assigned layer against `GetTargetDataLayer()` for every matching rule
(`DataLayerRuleSubsystem.cpp:148-193`); since the rule computes `DL_HM_<prop name>`, the correct
assignment never matches and is reported as non-compliant.

This settles the **intended semantics**: nested props belong to their container's DataLayer, and the
content already reflects that. It also makes the two families one defect — so a fix that only stops
the 730 warnings, without teaching the rule that a descendant inherits its container's layer, leaves
324 false non-compliance rows behind.

---

## 7. Proposed corrections

### Option 1 — Parent-anchored matching *(recommended, structural)*

Give `FWorldPartitionRuleCondition` the ability to match a path **position** rather than any
substring, then re-express `DA_HM_INT_Rules` with it.

`OutlinerPathContains = [LI_Hogsmeade, _POP]` becomes a parent-anchored form such as
`OutlinerParentPathContains = [LI_Hogsmeade/Shops, LI_Hogsmeade/Buildings]`: the substring is tested
against the actor's path **minus its own leaf**, so only direct children of `Shops` / `Buildings`
match and descendants are excluded *structurally*. `FActorOrDesc::GetOutlinerFullPath()` already
provides everything needed — no actor-hierarchy traversal, no new engine data.

| | |
| --- | --- |
| Removes | 724 false positives, and the 324 non-compliance rows once paired with inheritance |
| Scope | `WorldPartitionRuleAsset.h`, `WorldPartitionRuleSubsystem.cpp`, one `.uasset` re-save |
| Side effects | New opt-in property; existing `OutlinerPathContains` semantics unchanged |
| Durability | Structural — future prop additions cannot reintroduce the warnings |

Pair it with **container DataLayer inheritance**: when an actor sits inside a Level Instance the rule
targets, its expected layer is the container's, not its own. That is what clears §6 and what the
content already assumes.

### Option 2 — Gate the match on an actor tag *(immediate, data-only)*

Tag the 82 container Level Instances (e.g. `WPRules.DataLayerRoot`) and add that tag to both
`MatchingConditions`, which already use `AND`. `ActorTags` is evaluated per actor and does **not**
propagate down the path, so descendants stop matching immediately.

| | |
| --- | --- |
| Removes | 724 false positives |
| Scope | 82 container actors tagged + one `.uasset` edit — **no code change** |
| Drawback | Correctness depends on a manual tag: a new container added untagged is silently skipped |
| Use as | Mitigation while option 1 is implemented |

This is the concrete, expressible form of the companion audit's option A step 1, now that §5.1 has
established the structural condition does not exist yet.

### Option 3 — Filter by bounds *(partial, not recommended alone)*

`bUseMinBoundsDimension` / `bUseMinBoundsVolume` would reject most props, since containers are orders
of magnitude larger. It is approximate: a large prop (a bookshelf, a cart) still matches and a small
container is skipped. Acceptable only as a temporary volume reduction, never as the fix.

### Option 4 — Author the 704 missing DataLayerAssets *(rejected)*

`ResolveMissingDataLayerAsset()` and the outliner's *Create Missing DataLayer Assets* action
(`DataLayerRuleOutlinerColumn.cpp:326-351`) would silence the warnings by creating the assets. Here
that means **704 new per-prop DataLayerAssets**: 704 extra `DataLayerInstance` entries and streaming
cells for props already covered by their shop's layer, asserting that a single book stack can be
streamed independently. The set is derived from asset names, so it would have to be redone after
every dressing pass. Documented because it is one menu click away, and the operator must be warned
off it explicitly.

### Recommended sequence

| Phase | Action | Owner | Removes |
| --- | --- | --- | ---: |
| **1 — immediate** | Option 2: tag the 82 containers, add the tag to both `MatchingConditions` | Tools + Content | 724 |
| **2 — content** | Rename the 5 `SM_`-prefixed Level Instances to the `LI_` convention (§5.3) | Content | 5 |
| **3 — content** | Author `DL_HM_WATER_MILL_POP` and assign it to `LI_Water_Mill_POP` | Content | 1 |
| **4 — tools** | Option 1: parent-anchored condition + container inheritance; drop the tag gate | Tools | structural + 324 |
| **5 — tools** | Static authoring check (below) | Tools | prevention |

Phase 5 extends the existing setup-audit framework, which already flags `NamePatternBased` rules
whose patterns can never produce a `DL_` prefix:

`Source/WorldBuildingEditor/WorldPartition/Toolsets/WorldPartitionRuleSetupAudit.cpp:200-209`:

```cpp
// The patterns are applied in sequence to one string, so only the composed result has to start with
// DL_ - GetTargetDataLayer bails out when it does not. Later entries are usually cleanup
// substitutions, so judging them one by one reports a warning per entry on a perfectly good rule.
const bool bAnyPatternProducesPrefix = DataLayerRule->TargetDataLayerNamePatterns.ContainsByPredicate(
    [](const FDataLayerNamePattern& Pattern) { return Pattern.ReplacementSubstring.StartsWith(TEXT("DL_")); });
if (!DataLayerRule->TargetDataLayerNamePatterns.IsEmpty() && !bAnyPatternProducesPrefix)
{
    OutFindings.Add(MakeFinding(TEXT("Warning"), TEXT("DataLayerNaming"), RuleType, Rule.AssetPath,
        TEXT("No name pattern replaces anything with a DL_ prefix, so the composed name never starts with DL_ and GetTargetDataLayer discards every match.")));
}
```

The new finding: a `NamePatternBased` rule whose `OutlinerPathContains` entries contain no `/`
separator is **unanchored** and will match descendants. Report that at authoring time instead of
discovering it in a 92 000-warning log.

---

## 8. Acceptance criteria

After phase 1:

- `Failed to retrieve DataLayerAsset` rows naming a `DL_HM_*` layer drop from 730 to **6**.
- `DA_HM_INT_Rules` matches exactly the 82 `Shops` / `Buildings` containers.
- The 2 264 `DL_OVERLAND` untargeted rows are **unchanged** — narrowing the rule must not start
  clearing layers the level legitimately uses.

After phase 3:

- `Failed to retrieve DataLayerAsset` rows naming a `DL_HM_*` layer drop to **0**.
- `Applied DataLayer 'DL_HM_*'` becomes non-zero — it was **0** in the audited run.

After phase 4:

- The 324 `Runtime DataLayer 'DL_HM_*' … targeted by no rule` rows disappear.
- Removing the `WPRules.DataLayerRoot` tag from a container does not change the match set.

## 9. Risks

| Risk | Mitigation |
| --- | --- |
| A prop legitimately needs its own DataLayer | None found: all 704 requested names are per-prop. Re-validate before phase 4 |
| Anchored matching silently narrows other rules | New property is opt-in; `OutlinerPathContains` semantics unchanged |
| Tag drift in phase 1 | Phase 5 check reports containers under `Shops` / `Buildings` without the tag |
| `_EXT` / `_Bridge` exclusions interact with the new condition | Exclusions are evaluated before conditions (`DataLayerRuleSubsystem.cpp:1226-1229`); order unchanged |
| Renaming the 5 `SM_` actors breaks references | Level Instance references are by package, not actor label; verify in the editor first |

---

## 10. Findings for `WPRulesReviewer` itself

1. **This family is unreadable in the export.** `OracleEvaluator.ClassifyWarning` falls through to
   `"Rule warning"` for `WarningKind.Other`, replacing the raw message:

   ```129:131:Tools/WPRulesReviewer/src/WPRulesReviewer.Core/Oracle/OracleEvaluator.cs
               default:
                   Set(r, ReviewStatus.NeedsReview, AnomalySeverity.Low, "Rule warning");
                   break;
   ```

   All 730 rows land in the 87 923-row `Rule warning` bucket with an empty `Value` column, losing
   both the expected layer name and the distinction from every other unmodelled warning. The parser
   should give this family its own `WarningKind` and capture the expected name into `Value`, the way
   `MissingDataLayerNamed` already does.

2. **Severity is wrong.** These rows are `NeedsReview / Low`, yet they mean a rule matched and
   silently dropped its assignment. The companion `Missing DataLayer` family — a strictly *later*
   failure in the same pipeline — is `Anomaly / Medium`.

3. **No cross-family correlation.** `Failed to retrieve DataLayerAsset`, `Missing DataLayer` and
   `Runtime DataLayer without rule` are three views of this one defect, and the reviewer presents
   them as three unrelated buckets. Grouping by *owning Level Instance* would have collapsed all
   three to one actionable node per shop.

4. **The oracle cannot tell "asset genuinely absent" from "rule over-reaching".** Comparing the
   expected name against the project's real `DL_*` inventory — which §3.5 shows is cheap to
   enumerate — separates the 724 false positives from the 1 true positive without reading the level.

---

## 11. Verification plan

1. Confirm in the editor that `DL_HM_WATER_MILL_POP` does not exist, and spot-check 5 nested prop
   groups across 3 shops to confirm they carry their container's layer and none of their own.
2. Apply phase 1 on a scratch stream, re-run *Validate WP Rules* on `LV_Overland`, and check the
   §8 criteria — including that no new `Failed to assign DataLayer` or `Multiple DataLayer rule
   matches` row appears (the run currently has 0 and 0).
3. Land phases 2 and 3, re-run, confirm 0.
4. Only then schedule phase 4, and re-validate the full 730 → 0 and 324 → 0 progression.

---

## 12. Appendix — reproducing the figures

The curated `report.txt` collapses this family into `Rule warning` (§2), so the raw engine log is the
source for every count below.

```powershell
$log = "$env:APPDATA\WPRulesReviewer\Logs\Sundance_Validate_27September_validate-LV_Overland.log"
$rx  = [regex]"Failed to retrieve DataLayerAsset '([^']*)' for actor '([^']*)'"

# 730 rows, 704 distinct names, 5 empty
$rows = Select-String -Path $log -Pattern $rx -AllMatches |
    ForEach-Object { $m = $rx.Match($_.Line)
        [pscustomobject]@{ DL = $m.Groups[1].Value; Actor = $m.Groups[2].Value } }

# 1 container-level row, 724 descendants, 5 empty names
$rows | Group-Object { if ($_.DL -eq '') { 'EmptyName' }
                       elseif ($_.Actor -match '/(Shops|Buildings)/[^/]+$') { 'ContainerLevel' }
                       else { 'Descendant' } }

# ground truth: 66 DL_HM_* assets exist, against 704 requested
Get-ChildItem 'D:\Sun\Sundance\Content' -Recurse -Filter 'DL_HM_*.uasset' -File | Select-Object -Expand BaseName
```

[`data/failed-to-retrieve-datalayerasset-inventory.csv`](data/failed-to-retrieve-datalayerasset-inventory.csv)
holds all 730 rows with columns `ExpectedDataLayer`, `ActorLeaf`, `Classification`
(`Descendant` / `EmptyName` / `ContainerLevel`) and `OutlinerPath`. It is the working set for phase 1
and for the verification spot-checks.
