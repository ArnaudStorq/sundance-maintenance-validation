Parent: [Validate World Partition Rules — LV_Overland, 2026-09-27](README.md)

# Audit — "Runtime DataLayer without rule" warnings on `LV_Overland`

Status: proposal (no change applied)
Scope: every `Runtime DataLayer without rule` warning of one *Validate WP Rules* pass
Source: `Sundance_Validate_27September_validate-LV_Overland.log` (log of September 27, 2026 8:44 AM),
exported by `WPRulesReviewer` as `report.txt` on October 1, 2026
Raw data: [`data/runtime-datalayer-without-rule-inventory.csv`](data/runtime-datalayer-without-rule-inventory.csv) (2 606 rows)
Companion: [Missing DataLayer audit](MissingDataLayer.md) — same run, opposite symptom

## Contents

- [1. Executive summary](#1-executive-summary)
- [2. What the warning means](#2-what-the-warning-means)
- [3. Measured facts](#3-measured-facts)
  - [3.1 Volume and shape](#31-volume-and-shape)
  - [3.2 Per DataLayer](#32-per-datalayer)
  - [3.3 The registry is the root cause](#33-the-registry-is-the-root-cause)
  - [3.4 Coverage per container — the discriminator](#34-coverage-per-container--the-discriminator)
  - [3.5 Coverage per actor family](#35-coverage-per-actor-family)
  - [3.6 Cross-check against the Missing DataLayer family](#36-cross-check-against-the-missing-datalayer-family)
- [4. Proposal](#4-proposal)
  - [Bucket A — Promote deliberate assignments to rules (888 rows)](#bucket-a--promote-deliberate-assignments-to-rules-888-rows)
  - [Bucket B1 — Clear the street residue (1 384 rows)](#bucket-b1--clear-the-street-residue-1-384-rows)
  - [Bucket B2 — Settle the shop POP question (323 rows, 115 actors)](#bucket-b2--settle-the-shop-pop-question-323-rows-115-actors)
  - [Bucket C — Manual triage (11 rows)](#bucket-c--manual-triage-11-rows)
- [5. Verification plan](#5-verification-plan)
- [6. Findings for `WPRulesReviewer` itself](#6-findings-for-wprulesreviewer-itself)
- [7. Appendix — reproducing the figures](#7-appendix--reproducing-the-figures)

---

## 1. Executive summary

The run reports **2 606 `Runtime DataLayer without rule` warnings** on **2 398 distinct actors**
(2.5 % of the 95 188 actors in the pass), all classified `Needs review / Low`.

**Root cause.** The DataLayer rule registry is empty for everything this world actually streams.
Across the whole pass, the only DataLayer rule that applied anything is `DA_SKY_Rules`, on 2 actors.
Every other `DL_*` assignment in Hogsmeade and the Overland region was placed by hand in the editor,
so by construction no rule targets it. This is not 2 606 defects; it is **one missing registry**,
observed 2 606 times.

**The discriminator is coverage**, not volume: for each container, how many of its actors carry the
layer. At 100 % the authoring intent is unambiguous and belongs in a rule. At 4–12 % the layer is
copy/paste residue and belongs nowhere. Treating both the same way is what has kept this backlog
alive, because any single fix is obviously wrong for half the rows.

**Recommendation.** Split by coverage and apply three different fixes: author 3 rule assets (888
rows), strip the residue from the street containers (1 384 rows), settle one open content question
on `LI_Pippens_POP` (323 rows), triage 11 one-offs by hand. Expected result: **2 606 → 0**.

| Bucket | Fix | Rows | Actors |
| --- | --- | ---: | ---: |
| A — coverage ≥ 79 % | Author 3 DataLayer rules | 888 | 888 |
| B1 — coverage 4–33 % | Clear the layer | 1 384 | 1 384 |
| B2 — shop POP layer | Content decision required | 323 | 115 |
| C — one-offs | Manual triage, 5 owners | 11 | 11 |

---

## 2. What the warning means

```
LogWorldPartitionRules: Warning: Actor '<Path>' is assigned to runtime DataLayer '<DL_*>'
but no DataLayer rule targets it. An unjustified runtime DataLayer creates an extra streaming cell.
```

The actor carries a **runtime** DataLayer assignment in its own package, and no asset registered
under `DataLayerRulesForActorSave` claims that layer for that actor. The engine does not undo the
assignment — it warns and moves on.

In `WPRulesReviewer` this is `WarningKind.UntargetedRuntimeDataLayer`, surfaced in the *Filter by
Type* dropdown as **Runtime DataLayer without rule**, parsed by:

```41:42:Tools/WPRulesReviewer/src/WPRulesReviewer.Core/Parsing/LogParser.cs
[GeneratedRegex(@"Actor '([^']+)' is assigned to runtime DataLayer '([^']*)' but no DataLayer rule targets it")]
private static partial Regex UntargetedRuntimeDataLayer();
```

and triaged by the oracle as:

```125:128:Tools/WPRulesReviewer/src/WPRulesReviewer.Core/Oracle/OracleEvaluator.cs
            case WarningKind.UntargetedRuntimeDataLayer:
                Set(r, ReviewStatus.NeedsReview, AnomalySeverity.Low,
                    $"Runtime DataLayer '{r.Value}' assigned to the actor but targeted by no rule");
                break;
```

Why it is worth fixing despite the `Low` severity: the assignment exists **only** in the actor
packages. Re-running the rules pass will never recreate it on a fresh actor, and will never clean it
off a stale one. Every one of these 2 398 actors is content that the rule system cannot reproduce,
and each untargeted layer still costs a streaming cell per grid cell at cook time.

---

## 3. Measured facts

### 3.1 Volume and shape

| Metric | Value |
| --- | ---: |
| Warning rows | 2 606 |
| Distinct actors | 2 398 |
| Distinct DataLayers | 7 |
| Severity | 100 % `Low` |
| Section | 100 % *Needs review* |
| `Rule` column populated | 0 rows (by definition) |

### 3.2 Per DataLayer

| DataLayer | Rows | Actors |
| --- | ---: | ---: |
| `DL_OVERLAND` | 2 264 | 2 264 |
| `DL_HM_PIPPENS_POP` | 323 | 115 |
| `DL_AUTOMATION` | 12 | 12 |
| `DL_WE_HM_ThreeBroom_POP_Bar_ComingRightUp` | 4 | 4 |
| `DL_SANCTUARY_ConversationHub_Bertram_03_A` | 1 | 1 |
| `DL_HM_WPV_Trashed_EXT` | 1 | 1 |
| `DL_SEASON_Fall` | 1 | 1 |

Two layers carry 99 % of the family. `DL_HM_PIPPENS_POP` is the only one where rows exceed actors
(323 for 115): those actor names appear in several actor packages, which is a duplication bug of its
own — see §6.

### 3.3 The registry is the root cause

Every rule asset named anywhere in the pass, with what it actually applied:

| Rule asset | Kind | Applied to |
| --- | --- | ---: |
| `DA_SKY_Rules` | DataLayer | 2 actors (`DL_SKY`) |
| `DA_MainGrid_Rules`, `DA_SmallGrid_Rules`, `DA_NoneGrid_Rules` | RuntimeGrid | 7 217 actors |
| `DA_HM_HLODLayer_*`, `DA_Overland_HLODLayer_*`, `DA_FarFoliage_HLODLayer_*` | HLODLayer | 1 979 actors |

There is **no** DataLayer rule for `DL_OVERLAND`, none for `DL_AUTOMATION`, none for any `DL_HM_*`
shop layer. The oracle's naming heuristic (`DA_{X}_Rules` → `DL_{X}`, see `OracleEvaluator`) has
nothing to match. That is the whole story: the HLOD and grid pipelines were migrated to rules, the
DataLayer pipeline never was.

### 3.4 Coverage per container — the discriminator

Coverage = flagged actors ÷ all actors seen in that container during the pass.

| DataLayer | Container | Flagged | In container | Coverage |
| --- | --- | ---: | ---: | ---: |
| `DL_OVERLAND` | `.../LI_Hogsmeade_River/Hogsmeade_RiverBlockout` | 337 | 337 | 100 % |
| `DL_OVERLAND` | `.../LI_HM_Streets_EXT/LI_Camp_Crate_Food_A` | 149 | 149 | 100 % |
| `DL_OVERLAND` | `.../Hogsmeade_RiverBlockout/LI_Hogsmeade_River` | 366 | 465 | 79 % |
| `DL_OVERLAND` | `.../Streets/LI_HM_StreetDressing_WPV_Trashed_EXT` | 14 | 43 | 33 % |
| `DL_OVERLAND` | `.../HM_StreetDressing_General/HM_StreetDressing_Foliage` | 38 | 324 | 12 % |
| `DL_HM_PIPPENS_POP` | `.../Shops/LI_Pippens_POP` | 115 | 1 065 | 11 % |
| `DL_OVERLAND` | `.../Streets/LI_HM_Streets_EXT` | 1 220 | 12 352 | 10 % |
| `DL_OVERLAND` | `.../Streets/LI_HM_StreetDressing_EXT` | 112 | 2 631 | 4 % |

The gap between 79 % and 33 % is clean — there is nothing in between — which is what makes the
bucket split defensible rather than arbitrary.

### 3.5 Coverage per actor family

The same bimodality shows on asset families, and it is what decides whether a path rule or a name
rule is the right tool.

| Actor family | Flagged | Total | Coverage |
| --- | ---: | ---: | ---: |
| `POI_*` (all `DL_AUTOMATION`) | 12 | 12 | 100 % |
| `LI_Camp_Crate_Food_A/*` | 149 | 149 | 100 % |
| `SM_Bulrush_Reeds_*` | 108 | 108 | 100 % |
| `SM_HW_Apple_*` | 148 | 154 | 96 % |
| `SM_HW_VC_Balustrade_A*` | 133 | 165 | 81 % |
| `WaterFall_A*` | 52 | 120 | 43 % |
| `SM_CobbleStreet_Block_*` (in `LI_HM_Streets_EXT`) | 850 | 4 804 | 18 % |
| `RiverBank_*` | 302 | 4 229 | 7 % |

`SM_CobbleStreet_Block_*` is the decisive measurement. 850 cobblestone blocks carry `DL_OVERLAND`
while 3 954 identical blocks in the same folder do not. No streaming design produces that split;
duplication of a tagged source actor does.

### 3.6 Cross-check against the Missing DataLayer family

The [companion audit](MissingDataLayer.md) covers the mirror-image warning:
a rule asks for a DataLayer that does not exist. Inside `LI_Pippens_POP` both families fire at once,
and the overlap is worth stating precisely:

| Set | Actors |
| --- | ---: |
| Carry `DL_HM_PIPPENS_POP` untargeted | 115 |
| Asked for a private `DL_HM_HW_Book_*` layer that does not exist | 30 |
| **In both sets** | **0** |

The two populations are **disjoint**. The shop contains actors that already stream with the shop and
actors the rule wants to give a private layer to, and no actor is in both states. So the rule is not
"fighting" an existing assignment — it simply never looks at the 115 actors that already carry the
shop layer. Both audits point at the same hole from opposite sides: nothing describes, in data, what
`LI_Pippens_POP` is supposed to stream.

---

## 4. Proposal

### Bucket A — Promote deliberate assignments to rules (888 rows)

Coverage ≥ 79 %: the layer is meant for the whole container. Encode it so the assignment becomes
reproducible, then let the pass re-apply it.

| New rule asset | Target layer | Match criteria | Rows cleared |
| --- | --- | --- | ---: |
| `DA_OVERLAND_River_Rules` | `DL_OVERLAND` | `OutlinerPath` = `LV_Overland/Region/Hogwarts Valley/Hogsmeade_RiverBlockout` (recursive) | 727 |
| `DA_OVERLAND_CampDressing_Rules` | `DL_OVERLAND` | `OutlinerPath` = `.../LI_HM_Streets_EXT/LI_Camp_Crate_Food_A` (recursive) | 149 |
| `DA_AUTOMATION_Rules` | `DL_AUTOMATION` | Actor name prefix `POI_` | 12 |

Registration in `DefaultEditor.ini`, under
`[/Script/WorldBuildingEditor.WorldPartitionRuleSettings]`:

```ini
+DataLayerRulesForActorSave=/Game/Data/DataLayers/DA_OVERLAND_River_Rules.DA_OVERLAND_River_Rules
+DataLayerRulesForActorSave=/Game/Data/DataLayers/DA_OVERLAND_CampDressing_Rules.DA_OVERLAND_CampDressing_Rules
+DataLayerRulesForActorSave=/Game/Data/DataLayers/DA_AUTOMATION_Rules.DA_AUTOMATION_Rules
```

Side effects to accept **before** landing this, not after:

- `LI_Hogsmeade_River` sits at 79 %, so the rule adds `DL_OVERLAND` to the 99 blockout actors that
  do not have it today. That is almost certainly the intent — they were skipped during authoring —
  but it changes shipped streaming and needs the environment owner's sign-off.
- `SM_HW_Apple_*` (96 %) and `SM_HW_VC_Balustrade_A*` (81 %) are equally good candidates, but they
  live inside low-coverage containers, so they need a name-based criterion rather than a path one.
  Hold them until the three rules above are validated; adding them now would couple two unrelated
  risks in one changelist.
- The `DA_AUTOMATION_Rules` prefix match must be verified against POI actors in **other** worlds
  before it is registered globally — the ini is not per-world.

### Bucket B1 — Clear the street residue (1 384 rows)

Coverage 4–33 % on `DL_OVERLAND`, all under Hogsmeade `Streets`. The layer was never meant to apply
to these actors; the assignment travelled with duplicated source actors.

| Container | Rows |
| --- | ---: |
| `.../Streets/LI_HM_Streets_EXT` (incl. 149 in `LI_Camp_Crate_Food_A`, excluded) | 1 220 |
| `.../Streets/LI_HM_StreetDressing_EXT` | 112 |
| `.../HM_StreetDressing_General/HM_StreetDressing_Foliage` | 38 |
| `.../Streets/LI_HM_StreetDressing_WPV_Trashed_EXT` | 14 |

The declarative route needs no script:

```ini
+OutlinerPathsToClearDataLayers=LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade/Streets/LI_HM_Streets_EXT
+OutlinerPathsToClearDataLayers=LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade/Streets/LI_HM_StreetDressing_EXT
+OutlinerPathsToClearDataLayers=LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade/Streets/LI_HM_StreetDressing_WPV_Trashed_EXT
```

Two constraints, both blocking:

1. `OutlinerPathsToClearDataLayers` clears **all** DataLayers under the path, not the named one. The
   pass gives a strong hint that these containers carry nothing else — no DataLayer rule applied
   anything there, and the only other layer observed is the single `DL_HM_WPV_Trashed_EXT` in
   bucket C — but it must be verified against the actor packages first. If anything else turns up,
   fall back to a commandlet that removes only `DL_OVERLAND`.
2. `LI_Camp_Crate_Food_A` is **nested inside** `LI_HM_Streets_EXT`, so the clear entry would undo
   the bucket A rule. Either sequence B1 before A and let the rule re-apply, or carve the sub-path
   out explicitly. Sequencing is the safer of the two because it leaves one source of truth.

### Bucket B2 — Settle the shop POP question (323 rows, 115 actors)

`DL_HM_PIPPENS_POP` on 11 % of `LI_Pippens_POP`. Unlike B1 this is **not** obviously residue: a shop
layer on shop content is plausible intent, and §3.6 shows the rule system has no opinion about this
shop at all. Two coherent outcomes, and the content owner has to pick:

- **Promote** — author `DA_HM_PIPPENS_POP_Rules` targeting the `LI_Pippens_POP` outliner path. Clears
  all 323 rows and, per the companion audit, removes the reason the Hogsmeade rule tries to invent
  per-prop layers for the other 30 actors. Cost: `DL_HM_PIPPENS_POP` goes from 115 to ~1 065 actors,
  a real streaming change that must be profiled.
- **Clear** — strip the layer and let the shop stream with its parent Level Instance. Clears the
  same 323 rows at no streaming cost, but discards whatever intent put the layer there.

Do not guess. This single decision also sets the pattern for every other `LI_*_POP` shop in
Hogsmeade, so it is worth one meeting rather than one changelist.

### Bucket C — Manual triage (11 rows)

| Actor | DataLayer | Owner |
| --- | --- | --- |
| `LV_Overland/Water/ShallowWaterRiver_Hogsmeade_{North,West,South}` | `DL_OVERLAND` | Water / Env |
| `.../Shops/LI_ThreeBroom_POP/World Events/BP_WE_WaypointSpline{,2,3,4}` | `DL_WE_HM_ThreeBroom_POP_Bar_ComingRightUp` | World Events |
| `.../Shops/LI_Neep_EXT/SM_HM_Neep_SF_Windows_Halloween_1` | `DL_SEASON_Fall` | Seasonal content |
| `.../Shops/LI_Tomes_INT/Mesh/SM_HM_Tomes_Shelfing_Drawer_B67` | `DL_SANCTUARY_ConversationHub_Bertram_03_A` | Narrative / Sanctuary |
| `.../Streets/LI_HM_StreetDressing_WPV_Trashed_EXT` (the container actor) | `DL_HM_WPV_Trashed_EXT` | Hogsmeade streets |

The World Events and Sanctuary cases are the instructive ones. A gameplay DataLayer on a waypoint
spline or a shelf drawer is almost certainly correct, and no path- or name-based rule can express
it — the actor is picked by a designer, not by a convention. These argue for a fourth rule family
keyed on **actor tags**, which `WorldPartitionRuleSettings` already supports via
`ActorTagExcludedFromDataLayerRules` but which nothing in this project currently uses positively.

---

## 5. Verification plan

1. Confirm in the editor that the three B1 containers carry no DataLayer other than `DL_OVERLAND`
   (spot-check 5 actors per container). This gates the use of `OutlinerPathsToClearDataLayers`.
2. Get the environment owner's sign-off on adding `DL_OVERLAND` to the 99 uncovered
   `LI_Hogsmeade_River` actors.
3. Get the Hogsmeade content owner's decision on B2 (promote vs clear).
4. On a scratch stream, land B1, re-run *Validate WP Rules* on `LV_Overland`, and check:
   `Runtime DataLayer without rule` drops to 1 222, and **no new** `Missing DataLayer` or
   `Failed to assign DataLayer` rows appear.
5. Land the three bucket A rule assets, re-run, and check the 888 rows move from *Warning* to
   *Applied* with a populated `Rule` column — not merely that they disappear. A row that vanishes
   without reappearing as applied means the rule did not match and the layer was simply lost.
6. Confirm the 1 450 `Missing DataLayer` rows are unchanged by steps 4–5; the two families must be
   fixed independently or neither result can be attributed.
7. Land B2 and C, re-run, expect zero.

---

## 6. Findings for `WPRulesReviewer` itself

Independent of the content fix, this audit surfaced three gaps:

1. **Every warning is duplicated into a second, empty row.** The engine's second sentence ("An
   unjustified runtime DataLayer creates an extra streaming cell") is parsed as its own record with
   no value and the generic reason `Rule warning`, adding 2 606 rows to *Needs review*. Folding the
   continuation line into the parent record in `LogParser` would make the counts honest, here and
   for any other multi-sentence engine warning.

2. **The oracle never cross-checks this warning against what it knows.**
   `OracleEvaluator.ClassifyWarning` returns `Low` unconditionally, without consulting
   `OracleKnowledge.KnownDataLayers`. Yet the distinction matters a lot for triage: "the layer has a
   rule but it missed this actor" is a rule bug (Medium), while "no rule mentions this layer at all"
   is a registry gap (Low). The knowledge set is already built — it is simply not read on this path.

3. **No coverage metric.** Everything actionable in this audit came from one number the tool does
   not compute: flagged actors ÷ actors in the same container. It turned 2 606 undifferentiated
   `Low` rows into four buckets with four different fixes. Surfacing coverage per container in the
   Warning Explorer would generalise to every warning family, not just this one.

---

## 7. Appendix — reproducing the figures

Every number comes from `report.txt`, the markdown export of the reviewer session. Rows of this
family are the ones whose oracle reason matches `but targeted by no rule`.

```powershell
# 2 606 rows, 2 398 distinct actors, 7 distinct DataLayers
$rows = [System.IO.File]::ReadLines('report.txt') |
    Where-Object { $_ -like '|*' -and $_ -match 'but targeted by no rule' } |
    ForEach-Object {
        $c = $_ -split '\|'
        [pscustomobject]@{ DataLayer = $c[3].Trim(); Actor = $c[6].Trim(' ', '`') }
    }
$rows.Count
($rows | Select-Object -Expand Actor -Unique).Count
$rows | Group-Object DataLayer | Sort-Object Count -Descending

# coverage per container: flagged actors vs every actor seen in that container
$all = [System.IO.File]::ReadLines('report.txt') |
    Where-Object { $_ -like '|*' } |
    ForEach-Object { ($_ -split '\|')[6].Trim(' ', '`') } |
    Where-Object { $_ -and $_ -ne 'Actor' } | Select-Object -Unique
$byContainer = $all | Group-Object { $_.Substring(0, $_.LastIndexOf('/')) } -AsHashTable -AsString
$rows | Group-Object { $_.Actor.Substring(0, $_.Actor.LastIndexOf('/')) } |
    Sort-Object Count -Descending |
    Select-Object Count, Name, @{ n = 'InContainer'; e = { $byContainer[$_.Name].Count } }

# the only DataLayer rule that applied anything in the whole pass
rg "^\| DataLayer \|" report.txt | ForEach-Object { ($_ -split '\|')[5].Trim() } |
    Group-Object | Sort-Object Count -Descending
```

[`data/runtime-datalayer-without-rule-inventory.csv`](data/runtime-datalayer-without-rule-inventory.csv)
holds the full inventory — one row per warning, with columns `DataLayer`, `Bucket`, `Container`,
`ActorPath`. The `Bucket` column is the §4 classification, so the file is directly usable as the
work list for each of the four fixes.
