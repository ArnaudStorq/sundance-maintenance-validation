Parent: [Validate World Partition Rules — LV_Overland, 2026-09-27](README.md)

# Audit — "Missing DataLayer" warnings on `LV_Overland`

Status: proposal (no change applied)
Scope: every `Missing DataLayer` warning of one *Validate WP Rules* pass
Source: `Sundance_Validate_27September_validate-LV_Overland.log` (log of September 27, 2026 8:44 AM),
exported by `WPRulesReviewer` as `report.txt` on October 1, 2026
Raw data: [`data/missing-datalayer-inventory.csv`](data/missing-datalayer-inventory.csv) (725 rows)

## Contents

- [1. Executive summary](#1-executive-summary)
- [2. What the warning means](#2-what-the-warning-means)
- [3. Measured facts](#3-measured-facts)
  - [3.1 Volume and shape](#31-volume-and-shape)
  - [3.2 Localisation — one container, one defect](#32-localisation--one-container-one-defect)
  - [3.3 Distribution per owning Level Instance](#33-distribution-per-owning-level-instance)
  - [3.4 Distribution per prop family](#34-distribution-per-prop-family)
  - [3.5 Nesting depth — the discriminator](#35-nesting-depth--the-discriminator)
  - [3.6 Name derivation — verified on 100 % of rows](#36-name-derivation--verified-on-100--of-rows)
  - [3.7 Cross-check against the DataLayers that really exist](#37-cross-check-against-the-datalayers-that-really-exist)
- [4. Root cause](#4-root-cause)
  - [Why "create the missing DataLayers" is the wrong fix](#why-create-the-missing-datalayers-is-the-wrong-fix)
- [5. Proposed corrections](#5-proposed-corrections)
  - [Option A — narrow the rule (recommended)](#option-a--narrow-the-rule-recommended)
  - [Option B — exclude the actors instead of narrowing the rule](#option-b--exclude-the-actors-instead-of-narrowing-the-rule)
  - [Option C — author the 704 missing DataLayers](#option-c--author-the-704-missing-datalayers)
  - [Recommendation](#recommendation)
- [6. Findings for `WPRulesReviewer` itself](#6-findings-for-wprulesreviewer-itself)
- [7. Verification plan](#7-verification-plan)
- [8. Appendix — reproducing the figures](#8-appendix--reproducing-the-figures)

---

## 1. Executive summary

The run reports **1 450 `Missing DataLayer` warnings**, all classified `Anomaly / Medium`. They are
**not 1 450 independent defects**: they are one single authoring defect, observed 725 times and
logged twice per occurrence.

**Root cause.** The Hogsmeade DataLayer rule derives the expected DataLayer name from the actor's
*own* name, with the mapping `LI_<X>` → `DL_HM_<X>`. That mapping is correct for a *top-level*
Level Instance (a shop, a building), which does own a streaming layer. It is applied unchanged to
**nested prop-group Level Instances** (book stacks, cauldrons, chopped wood, key rings …), which
never had a DataLayer authored for them and must not have one — they already stream with their
owning shop.

**Evidence that settles it.** Inside `LI_Pippens_POP`, 323 child actors already carry the runtime
DataLayer `DL_HM_PIPPENS_POP` (reported separately as *"assigned to the actor but targeted by no
rule"*), while the rule simultaneously asks each of those children for a private
`DL_HM_HW_Book_Stack_Small_*` layer. The level is right; the rule's targeting is wrong.

**Recommendation.** Do **not** create the 704 missing DataLayer assets. Narrow the rule so it only
targets top-level Level Instances, then fix the one genuine gap (`LI_Water_Mill_POP`). Expected
result: 1 450 warnings → **2** (option A below).

| | Before | After (option A) |
| --- | ---: | ---: |
| `Missing DataLayer` warnings | 1 450 | 2 |
| DataLayer assets to author | 704 | 1 |
| Actors to touch | 725 | 1 |

---

## 2. What the warning means

`LogWorldPartitionRules: Warning: Missing DataLayer <Name> for actor '<Path>'.`

The rule matched the actor and resolved a target DataLayer name, but **no `DataLayerInstance` with
that name exists in the level**, so the assignment was dropped. The actor therefore keeps whatever
DataLayer it already had (or none), silently diverging from the rules.

In `WPRulesReviewer` this is `WarningKind.MissingDataLayerNamed`, surfaced in the *Filter by Type*
dropdown as **Missing DataLayer**, and triaged by the oracle as:

```115:118:Tools/WPRulesReviewer/src/WPRulesReviewer.Core/Oracle/OracleEvaluator.cs
            case WarningKind.MissingDataLayerNamed:
                Set(r, ReviewStatus.Anomaly, AnomalySeverity.Medium,
                    $"Expected DataLayer '{r.Value}' does not exist / was not assigned");
                break;
```

The sibling kind `MissingDataLayerEmpty` (actor matched no DataLayer rule at all) is treated as
known noise and is **out of scope** here.

---

## 3. Measured facts

### 3.1 Volume and shape

| Metric | Value |
| --- | ---: |
| `Missing DataLayer` warning rows | 1 450 |
| Distinct actors | 725 |
| Rows per actor | exactly 2 |
| Distinct expected DataLayer names | 704 |
| Severity | 100 % `Medium` |
| Rule column populated | 0 rows |

Two observations that matter for triage:

- **Every warning is logged exactly twice.** The ratio is uniform (725 × 2 = 1 450), so the real
  defect count is 725. This is consistent with the validate pass evaluating the registered
  DataLayer rule list twice (or running twice); it must be confirmed in the engine before the
  reviewer starts collapsing rows, because collapsing on an unverified assumption would hide real
  duplicates elsewhere. Until then, read every count in this document as "rows", and halve it.
- **704 names for 725 actors.** 16 prop groups are instanced in more than one shop and ask for the
  same layer name (`DL_HM_HW_Book_Stack_Small_D` is requested by 5 different actors). That is
  further proof the name is derived from the *prop asset* name, not from a streaming decision.

### 3.2 Localisation — one container, one defect

All 1 450 rows live under the same parent:

```
LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade/{Shops|Buildings}/...
```

| Area | Rows |
| --- | ---: |
| `Shops` | 1 438 |
| `Buildings` | 12 |

Nothing outside Hogsmeade is affected: no other region, no other world partition area.

### 3.3 Distribution per owning Level Instance

| Owning Level Instance | Actors | Share |
| --- | ---: | ---: |
| `LI_Tomes_POP` | 552 | 76.1 % |
| `LI_Scrivenshafts_INT` | 33 | 4.6 % |
| `LI_Pippens_POP` | 30 | 4.1 % |
| `LI_Flutes_POP` | 21 | 2.9 % |
| `LI_Honeydukes_POP` | 19 | 2.6 % |
| `LI_Dervish_POP` | 16 | 2.2 % |
| `LI_PostOffice_POP` | 14 | 1.9 % |
| `LI_Cauldron_POP` | 10 | 1.4 % |
| `LI_Ollivanders_INT` | 7 | 1.0 % |
| `LI_PostOffice_INT` | 7 | 1.0 % |
| `LI_Water_Mill_POP` | 6 | 0.8 % |
| `LI_Emporium_INT` | 3 | 0.4 % |
| `LI_Zonkos_INT` | 2 | 0.3 % |
| `LI_BingleBlatch_INT` | 2 | 0.3 % |
| `LI_Ollivanders_POP` | 1 | 0.1 % |
| `LI_ThreeBroom_POP` | 1 | 0.1 % |
| `LI_Hogshead_INT` | 1 | 0.1 % |
| **Total** | **725** | |

`LI_Tomes_POP` alone drives three quarters of the noise: it is the bookshop, densely filled with
individually-instanced book props.

### 3.4 Distribution per prop family

| Prop family | Actors |
| --- | ---: |
| `HW_Book_*` (book rows and stacks) | 636 |
| `HW_Generic_Book_Row_*` | 18 |
| `HM_*` | 14 |
| `Cauldron_*` | 9 |
| `Wood_Chopped_*` | 8 |
| `SM_*` | 7 |
| `KeyRing_*` | 6 |
| `FoodBags_*` | 4 |
| `BellSpiral_*`, `BellBar_*`, `Ingredient_*` | 3 each |
| `DAO_*`, `WallCollage_*`, `GEN_*`, `Lens_*` | 2 each |
| `Ollivanders`, `Water`, `Tool`, `WE`, `Chandelier`, `Spoons` | 1 each |

**90 % of the volume is book props.** This is dressing geometry, not gameplay content: no designer
ever intended to stream a single book stack independently.

### 3.5 Nesting depth — the discriminator

| Outliner depth | Actors | What it is |
| --- | ---: | --- |
| 6 | 1 | the building Level Instance itself (`LI_Water_Mill_POP`) |
| 7 | 676 | prop group nested directly in a shop |
| 8 | 11 | prop group nested one level deeper |
| 9 | 37 | prop group under `.../Mesh/LA_INT_Props/` |

**724 of 725 actors (99.9 %) are nested prop groups. Exactly one is a legitimate top-level Level
Instance.** This single number is the whole audit: the rule's target set is wrong by a factor of
724, and only one entry of it is a real missing asset.

### 3.6 Name derivation — verified on 100 % of rows

For every one of the 1 450 rows:

```
expected DataLayer == "DL_HM_" + (actor leaf name without its "LI_" prefix)
```

Examples:

| Actor leaf | Expected DataLayer | Verdict |
| --- | --- | --- |
| `LI_Water_Mill_POP` | `DL_HM_Water_Mill_POP` | legitimate — top-level building, layer genuinely absent |
| `LI_HW_Book_Stack_Small_C167` | `DL_HM_HW_Book_Stack_Small_C167` | spurious — book prop inside `LI_Pippens_POP` |
| `LI_Cauldron_F` | `DL_HM_Cauldron_F` | spurious — prop inside `LI_Cauldron_POP` |
| `LI_WE_HM_ThreeBroom_POP_Bar_ComingRightUp` | `DL_HM_WE_HM_ThreeBroom_POP_Bar_ComingRightUp` | prefix bug — the authored asset is `DL_WE_HM_ThreeBroom_POP_Bar_ComingRightUp` |

No exception, no counter-example. The derivation is mechanical, which is exactly why it
over-reaches.

### 3.7 Cross-check against the DataLayers that really exist

The same run reports 2 606 rows of *"Runtime DataLayer 'X' assigned to the actor but targeted by no
rule"*. They expose the level's actual, authored layers — only **7 distinct names**:

| Existing runtime DataLayer | Rows |
| --- | ---: |
| `DL_OVERLAND` | 2 264 |
| `DL_HM_PIPPENS_POP` | 323 |
| `DL_AUTOMATION` | 12 |
| `DL_WE_HM_ThreeBroom_POP_Bar_ComingRightUp` | 4 |
| `DL_SANCTUARY_ConversationHub_Bertram_03_A` | 1 |
| `DL_HM_WPV_Trashed_EXT` | 1 |
| `DL_SEASON_Fall` | 1 |

Three conclusions:

1. **The rule asks for 704 layers while the level owns 7.** A level is not authored with 704
   streaming layers for one village; the request itself is the anomaly.
2. **`LI_Pippens_POP` is the control case.** The shop resolves its own layer (`DL_HM_Pippens_POP`
   matches the authored `DL_HM_PIPPENS_POP` — name resolution is case-insensitive) and is therefore
   *absent* from the missing list. Yet its 30 nested prop groups are *present* in the missing list,
   while 323 of its children already stream through `DL_HM_PIPPENS_POP`. The level is correct; the
   rule's granularity is not.
3. **`DL_WE_HM_ThreeBroom_POP_Bar_ComingRightUp` is a second, smaller bug.** The derivation blindly
   prepends `DL_HM_` to the stripped name, producing `DL_HM_WE_HM_...` where the convention for
   World Event layers is `DL_WE_HM_...`. One actor is affected, but the same mistake will reappear
   on every future `LI_WE_*` Level Instance.

Also worth noting: **not one DataLayer assignment succeeded in this run.** The `Expected` section
contains exactly 2 DataLayer rows (`DA_SKY_Rules`, *"DataLayer is a known rule target"*) and zero
`Applied DataLayer` rows. The DataLayer half of the rule pipeline is effectively inert on
`LV_Overland`, which is why this defect went unnoticed.

---

## 4. Root cause

```
DataLayer rule for Hogsmeade
  └─ target name = "DL_HM_" + Trim("LI_", <actor name>)
       ├─ correct   for top-level Level Instances  (shops, buildings)  → ~20 actors
       └─ incorrect for nested prop-group LIs      (books, cauldrons)  → 724 actors
```

The rule has **no condition restricting it to top-level Level Instances**, and no exclusion for
prop-group Level Instances. Two aggravating factors:

- The `Rule` column is empty on all 1 450 rows (see §6), so the responsible rule asset is not named
  in the log — the defect is hard to attribute from the report alone.
- Prop dressing is authored as nested Level Instances (a sound content decision for reuse), which
  means the actor count in this family grows with every dressing pass. The warning count will keep
  climbing until the rule is narrowed.

### Why "create the missing DataLayers" is the wrong fix

Authoring the 704 requested assets would silence the warnings and make things materially worse:

- **Runtime cost.** 704 extra `DataLayerInstance` entries in the world partition, 704 extra
  streaming cells to evaluate, for props that are already covered by their shop's layer.
- **Semantics.** A DataLayer is a *streaming/state decision*. Giving one to `SM_Book_Stack_Small_D`
  asserts that a single book stack can be streamed or toggled independently. Nobody wants that.
- **Unbounded maintenance.** The set is derived from asset names, so it grows with every new prop
  group. The fix would need to be redone after every dressing change.

---

## 5. Proposed corrections

Three options, from the one to adopt to the one to avoid. They are mutually exclusive for the bulk
of the defect; **step 3 of option A is required regardless**.

### Option A — narrow the rule (recommended)

Restrict the Hogsmeade DataLayer rule to top-level Level Instances, then close the real gap.

| # | Action | Target | Tool | Reversible |
| --- | --- | --- | --- | --- |
| 1 | Add an `OutlinerPath` exclusion for nested prop groups, or a condition `parent == LI_Hogsmeade/{Shops,Buildings}` | the Hogsmeade DataLayer rule asset | `WorldPartitionRuleAuthoringToolset.AddRuleExclusion` / `AddRuleCondition` | yes (`RemoveRuleExclusion`) |
| 2 | Fix the `DL_HM_` prefix derivation so `LI_WE_*` resolves to `DL_WE_HM_*` | same rule asset | `SetRuleSettingsList` (or a C++ change if the prefix is hardcoded) | yes |
| 3 | Author the one genuinely missing layer `DL_HM_Water_Mill_POP` and assign it | `LI_Water_Mill_POP` | manual authoring + `ApplyRulesOnActors` | yes |
| 4 | Re-run *Validate WP Rules* on `LV_Overland` and confirm the count | — | TeamCity | — |

**Cost:** one rule asset edited, one DataLayer asset created, one actor touched.
**Residual after the fix:** 2 rows (the `LI_Water_Mill_POP` pair), dropping to 0 once step 3 lands.

**Risks to check before committing.** The exclusion must be expressed on a *stable* criterion.
Matching on the `LI_HW_Book_*` name pattern is tempting and wrong — it will not cover
`LI_Cauldron_F`, `LI_KeyRing_B2`, or tomorrow's prop family. Prefer the structural criterion
(nesting depth / required ancestor), which the measurement in §3.5 shows cleanly separates the two
populations. If the rule engine cannot express "direct child of `{Shops,Buildings}`", fall back to
an explicit `OutlinerPath` exclusion list seeded from
[`data/missing-datalayer-inventory.csv`](data/missing-datalayer-inventory.csv) and open a follow-up
to make the condition structural.

### Option B — exclude the actors instead of narrowing the rule

Tag the 724 prop groups with `ExcludeFromDataLayerRules`, or add their paths to
`OutlinerPathsToClearDataLayers` in `DefaultEditor.ini`.

Use this **only** if option A's condition proves inexpressible. It silences the same warnings but:

- it touches 724 actor packages instead of 1 rule asset — a large Perforce changelist for a defect
  that lives in one asset;
- `DefaultEditor.ini` is shared, and a 724-entry path list is unreadable and unmaintainable;
- it does not prevent the 725th prop group from reintroducing the warning.

### Option C — author the 704 missing DataLayers

**Not recommended.** See §4. Listed only to document that it was considered and rejected: it is
what `WorldPartitionRuleFixToolset.ResolveMissingDataLayerInstances` would do if run unguarded on
this level, so the operator must be warned off it explicitly.

### Recommendation

Adopt **option A**. Step 1 alone is a single rule-asset edit and removes 1 448 of the 1 450 rows;
step 2 is the same asset and prevents the prefix bug from recurring; step 3 is one actor. Option B
is the documented fallback; option C must be actively avoided.

---

## 6. Findings for `WPRulesReviewer` itself

The audit surfaced four gaps in the reviewer, independent of the content fix:

1. **The `Rule` column is empty for `Missing DataLayer` rows.** The parser's regex captures the
   layer and the actor but not the rule that asked for the layer:

   ```37:38:Tools/WPRulesReviewer/src/WPRulesReviewer.Core/Parsing/LogParser.cs
    [GeneratedRegex(@"Missing DataLayer\s+(?:(\S+)\s+)?for actor '([^']+)'\.")]
    private static partial Regex MissingDataLayer();
   ```

   If the engine log carries the rule name (even on a neighbouring line), capturing it would let the
   reviewer attribute this entire family to one asset automatically, instead of requiring the
   manual cross-check done in §3.7.

2. **1 450 rows for 725 defects.** Each warning is logged twice (§3.1). Either confirm the engine
   duplication and collapse it at parse time, or surface the multiplier in the UI. Today the
   severity of the issue is inflated 2× in every count and chart.

3. **No "derived name" grouping.** The reviewer groups by reason text, which yields 704 singleton
   groups here. A grouping on the *shape* of the expected name (`DL_HM_<ActorName>`) or on the
   owning Level Instance would have collapsed this to one actionable node — exactly the kind of
   insight the Warning Explorer is meant to provide.

4. **The oracle cannot tell "layer genuinely absent" from "rule over-reaching".** Both are
   `Anomaly / Medium`, so `LI_Water_Mill_POP` — the only real defect — is buried under 724
   false positives. Comparing the expected name against the set of layers observed in the
   *untargeted runtime DataLayer* rows (§3.7) would separate the two populations cheaply, without
   needing to read the level.

---

## 7. Verification plan

1. Confirm in the Unreal editor that `DL_HM_Water_Mill_POP` does not exist and that the 724 nested
   prop groups have no DataLayer of their own (spot-check 5 actors across 3 different shops).
2. Confirm which rule asset owns the `DL_HM_` derivation, and whether the prefix is data-driven
   (`SetRuleSettingsList`) or hardcoded in C++. This decides whether step 2 of option A is a data
   edit or a code change.
3. Apply option A step 1 on a scratch stream, re-run *Validate WP Rules* on `LV_Overland`, and
   check: `Missing DataLayer` ≤ 2, and **no new** `Failed to assign DataLayer` or
   `Multiple DataLayer rule matches` rows (the run currently has 0 and 0).
4. Confirm the 2 264 `DL_OVERLAND` and 323 `DL_HM_PIPPENS_POP` *untargeted* rows are unchanged —
   narrowing the rule must not start clearing layers the level legitimately uses.
5. Only then land steps 2 and 3 and submit.

---

## 8. Appendix — reproducing the figures

Every number above comes from `report.txt`, the markdown export of the reviewer session. The
`Missing DataLayer` rows are the ones whose oracle reason starts with `Expected DataLayer '`:

```powershell
# 1 450 rows
rg "Expected DataLayer '" report.txt | Measure-Object -Line

# 725 distinct actors, 704 distinct expected layer names
rg "Expected DataLayer '" report.txt |
    ForEach-Object { $c = $_ -split '\|'; [pscustomobject]@{ Value = $c[3].Trim(); Actor = $c[6].Trim(' ', '`') } } |
    Select-Object -Unique Value, Actor

# the 7 DataLayers the level really owns
rg "assigned to the actor but targeted by no rule" report.txt |
    ForEach-Object { ($_ -split '\|')[3].Trim() } | Group-Object | Sort-Object Count -Descending
```

[`data/missing-datalayer-inventory.csv`](data/missing-datalayer-inventory.csv) holds the
deduplicated inventory — one row per actor, with columns `ExpectedDataLayer`,
`OwningLevelInstance`, `Area`, `Depth`, `ActorPath`. It is the working set for option A step 1 and
for the verification spot-checks.
