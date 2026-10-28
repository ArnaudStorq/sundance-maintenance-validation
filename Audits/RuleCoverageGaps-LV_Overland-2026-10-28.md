Parent: [Audits](README.md)

# World Partition rule coverage gaps on `LV_Overland` (2026-10-28)

The World Partition rules are meant to be the single source of truth for every actor's DataLayers,
RuntimeGrid and HLOD layer: re-running them must reproduce the level. An actor that **no rule of a
family ever matches** breaks that contract silently. The builder leaves its current value alone, so
whatever the actor carries today, hand-set or left over from an older rule, survives every pass and
can never be recreated on a fresh actor. Nothing in the log flags it: there is no warning for "no
rule matched".

This audit answers one question: **with the current rule set, which actors and outliner paths are
never visited by a rule?** It found no gap in RuntimeGrid, a class-coverage gap in DataLayer and two
structural gaps in HLOD, plus 55 outliner-path entries in the rules that match no actor at all.

## Contents

- [TL;DR](#tldr)
- [What "never visited" means](#what-never-visited-means)
- [Population and method in one paragraph](#population-and-method-in-one-paragraph)
- [Results by family](#results-by-family)
  - [RuntimeGrid — fully covered](#runtimegrid--fully-covered)
  - [DataLayer — classes that no rule lists](#datalayer--classes-that-no-rule-lists)
  - [HLOD — `SmallGrid` actors outside Hogwarts and Hogsmeade](#hlod--smallgrid-actors-outside-hogwarts-and-hogsmeade)
  - [HLOD — large actors in Dungeons, Missions and Sanctuary](#hlod--large-actors-in-dungeons-missions-and-sanctuary)
  - [HLOD — transient gaps, not counted](#hlod--transient-gaps-not-counted)
- [Rule-side: outliner path entries that match nothing](#rule-side-outliner-path-entries-that-match-nothing)
- [Side finding: `_INT` and `_POP` force-exclude more than intended](#side-finding-_int-and-_pop-force-exclude-more-than-intended)
- [What was checked and found clean](#what-was-checked-and-found-clean)
- [Recommendations and open questions](#recommendations-and-open-questions)
- [How this audit was run](#how-this-audit-was-run)
- [Data](#data)

---

## TL;DR

| Family | Never visited (engine sample, 726 actors) | Extrapolated to the 61 079 processed actors | Structural cause |
|---|---:|---:|---|
| RuntimeGrid | **0 %** | 0 | `DA_NoneGrid_Rules` (`Types=Actor`) catches whatever the other grid rules leave |
| DataLayer | **12.7 %** (92) | ~7 700 (6 300 – 9 200) | Every DataLayer rule is a class list or an outliner-path list; classes in no list get nothing |
| HLOD — `SmallGrid` | **13.1 %** (95) | ~8 000 | The Overland HLOD rules exclude `DA_SmallGrid_Rules` matches, and `NoneExclude` only accepts `None` / `MainGrid` |
| HLOD — large actors in Dungeons / Missions / Sanctuary | **4.5 %** (33) | ~2 800 | `NoneInclude` excludes those paths, `NoneExclude` only takes actors of 200 or less |
| All three families at once | **0** | 0 | RuntimeGrid always matches |

Ranges are 95 % confidence intervals. **The percentages apply to the actors the 2026-10-24 Apply pass
processed, not to the whole level.** The gaps themselves are structural and hold everywhere. Their
size across the 622 307 descriptors of the full level was not measured (see
[open questions](#recommendations-and-open-questions)).

## What "never visited" means

For each actor and each family, the engine's own verdict (`GetActorRuleFacts`, `engineVerdicts`) puts
the actor in exactly one bucket:

| Bucket | Meaning | Counts as visited? |
|---|---|---|
| Matched | At least one registered rule of the family matches | Yes |
| Forced | `ActorTypesToClear*` / `OutlinerPathsToClear*` / `*ForceExcludeFromHLOD` applies; the rules are bypassed | Yes, by a setting |
| Ignored | `ActorTypesIgnoredBy*Rules`, `OutlinerPathsIgnoredBy*Rules` or the exclusion tag stops the family | Yes, deliberately |
| **Unvisited** | None of the above: no rule matches, so the builder keeps the current value | **No** |

## Population and method in one paragraph

The population is the **61 079 distinct outliner paths** of the `Applying rules on actor:` lines in
the log of the [Apply WP Rules build `#2154625`](https://slc-teamcity.wbiegames.com/buildConfiguration/Sundance_Dev_Tools_ApplyWorldPartitionRules/18499250)
(processed 2026-10-24). The builder only processes actors that need a write in at least one family
(see the [parallel builder plan](../ReferenceDocs/DevelopmentPlan-ParallelWorldPartitionRuleBuilder.md)),
so this is ~10 % of the level, biased towards actors that were already out of date. Replaying the
rules offline from the outliner path alone decides nothing, because almost every rule also reads the
class, the bounds, the grid or the Level Instance flag. So a **random sample of 840 paths** was
evaluated by the editor itself through Unreal MCP, on the rule set registered on 2026-10-28. 726 of
them resolved to an actor. Details are in [How this audit was run](#how-this-audit-was-run).

## Results by family

### RuntimeGrid — fully covered

726 / 726 actors match a RuntimeGrid rule. `DA_NoneGrid_Rules` (`Types=Actor`, excluded only when
another grid rule matches) guarantees it, so **no actor is ever left with an unexplained grid**. That
is also why no actor is unvisited in all three families at once.

### DataLayer — classes that no rule lists

**92 / 726 actors (12.7 %) match no DataLayer rule.** The DataLayer rules come in three shapes, and
each leaves a hole:

- **Class lists** (`DA_RENDER_Rules` for `StaticMeshActor` / `BP_SunDoorTemplate`, `DA_NAV_Rules`,
  `DA_AUDIO_Rules`, `DA_WATER_Rules`, `DA_TECH_Rules`…). A class in none of them is not covered.
- **`DA_OVERLAND_Rules`**, the broadest list. It excludes everything inside a Level Instance
  (`IsInsideLevelInstance`) and the `Missions`, `Dungeons`, `LI_Hogsmeade`, `LI_Hogwarts` and
  `LI_Sanctuary` subtrees.
- **Zone rules** (`DA_HOGSMEADE_Rules`, `DA_HM_*`, `DA_HOGWARTS_Rules`, `DA_HW_*`,
  `DA_DUNGEONS_Rules`, `DA_MISSIONS_*`, `DA_SANTUARY_*`). They all require `Types=LevelInstance`, so
  they tag the Level Instance and never its content.

So any actor that is **not** a static mesh, **not** a Level Instance and **not** in a listed class
gets nothing, wherever it sits:

| Class | Unvisited |
|---|---:|
| `PlacedFoliageSkinnedNaniteAssembly` | 49 |
| `DecalActor` | 17 |
| `SundancePerceptionPointBox`, `LocationVolume` | 3 each |
| `GroupActor`, `SpawnTriggerVolume`, `AvaSpawner`, `BP_WE_EnemyEncounterSpawner`, `OdcNavmeshBuildVolume` | 2 each |
| 10 other classes (`SkeletalMeshActor`, `TriggerBox`, `InsideVolume`, gameplay-prop Blueprints…) | 1 each |

They are spread across the level: Region 34 / 403, Hogsmeade 15 / 36, Dungeons 14 / 140,
Hogwarts 9 / 30, Sanctuary 7 / 15. 77 of the 92 carry no DataLayer today. **15 carry one that no
current rule produces** (`DL_RENDER` on 12 non-static-mesh actors, `DL_TECH` on 2, `DL_OVERLAND` on
1). Those are leftovers of older rules, and the pass will never clean them.

Whether this is a defect depends on the class. A decal or a skinned foliage assembly may well be
meant to stream with its cell and no DataLayer. The point is that nothing *states* it: the empty
value is accidental, not ruled.

### HLOD — `SmallGrid` actors outside Hogwarts and Hogsmeade

**95 / 726 actors (13.1 %)**, all in `SmallGrid`, almost all under `Region/`, none force-excluded by
path. No Overland HLOD rule can take them:

- `DA_Overland_HLODLayer_NoneInclude_Rules` and `DA_Overland_HLODLayer_Near_Rules` exclude every
  actor that matches `DA_SmallGrid_Rules` (`RuntimeGridRulesToExclude`).
- `DA_Overland_HLODLayer_NoneExclude_Rules`, the rule that would naturally take small actors out of
  HLOD, only accepts `Grid=None` or `Grid=MainGrid` (or 100 below the landscape).
- The Hogwarts and Hogsmeade HLOD rules require their own grid or their own path.

87 of the 95 are already `(excluded from HLOD)`, which is very likely the intent for actors under
1 m. But that value comes from an earlier pass or a hand edit, not from a rule. The 8 others are
still in HLOD.

### HLOD — large actors in Dungeons, Missions and Sanctuary

**33 / 726 actors (4.5 %)**: grid `None` (one `MainGrid`), largest bounds axis over 200, under
`Dungeons` (21), `Missions` (8) or `Sanctuary` (4). `DA_Overland_HLODLayer_NoneInclude_Rules`
excludes the `Dungeon`, `Mission` and `LI_Sanctuary` paths, and `NoneExclude` only matches actors
of 200 or less. No dedicated HLOD rule exists for these zones, so their large actors fall through.

### HLOD — transient gaps, not counted

45 more actors showed no HLOD match, but only because their **current** grid differs from the grid
the RuntimeGrid pass assigns (typically `SmallGrid` today, `None` after the pass). The engine verdict
evaluates HLOD against the current grid, while the builder runs HLOD after RuntimeGrid. Once the
grid is applied, `NoneExclude` matches them, so they are excluded from the counts above. They are
flagged `Stable=False` in the [sample CSV](RuleCoverageGaps-LV_Overland-Sample-2026-10-28.csv).

## Rule-side: outliner path entries that match nothing

The other reading of "outliner paths never visited": entries of the rules whose substring is
contained in **none** of the 61 079 processed paths. Every entry was replayed offline against the
full path list. The result is **55 entries**, listed in
[`RuleCoverageGaps-LV_Overland-ZeroHitPathEntries-2026-10-28.csv`](RuleCoverageGaps-LV_Overland-ZeroHitPathEntries-2026-10-28.csv).

**Seven rules are dead on this level**, because every one of their conditions requires a path entry
with zero hits:

| Rule | Dead condition |
|---|---|
| `DA_CLIFF_Rules` | `LevelInstance` AND `CliffRocks` |
| `DA_TEST_01_Light_Blendable` | `0_GlobalLighting/01_GlobalLighting_PartlyCloudy` |
| `DA_TEST_02_Light_Blendable` | `0_GlobalLighting/02_GlobalLighting_Moody` |
| `DA_SANTUARY_ArchitectChamber_Rules` | `LevelInstance` AND `LI_Sanctuary_ArchitectChamber` |
| `DA_LOC_DEAD_NPC_Rules` | `LOC_OL_DeadNPC` OR `LI_DeadNPC` |
| `DA_LOC_DE_GNOME_Rules` | `LOC_OL_De-Gnome` |
| `DA_LOC_ASTRONOMY_Rules` | `LOC_OL_AT` |

The other zero-hit entries sit in rules that stay alive through another criterion. Examples: the
`LOC_OL_*` paths of the `DA_LOC_*` rules, whose `BP_Location_*` class branch still matches;
`SM_HM_HeroBeech` and `SM_WildCherry` in the foliage HLOD rules; `LI_Overland_Global_Sky` in five
exclusions; and 14 entries of `OutlinerPathsToForceExcludeFromHLOD` (`SM_ClimbingRose`, `SM_Holly_`,
`SM_Bracken`…).

Two caveats. The path list only holds actors this pass processed, so an entry can still match an
actor that was already up to date. And the ini is shared by every world, so a rule can be dead here
and alive in another level. Read the list as "to confirm", not "to delete".

## Side finding: `_INT` and `_POP` force-exclude more than intended

`OutlinerPathsToForceExcludeFromHLOD` matches case-insensitive substrings. In the sample, **41 of the
54** actors force-excluded by `_INT` owe it to `_Interior`, mostly the
`LI_Poacher_Tent_*_Interior_*` camp tents, not to an `_INT` interior Level Instance. Likewise, **5 of
the 16** `_POP` hits are `SM_OL_POP_Rock_*` meshes. Those exterior actors are pulled out of HLOD by
accident. The safer entries would be `_INT/` and `_POP/` (the Level Instance segment followed by its
separator).

## What was checked and found clean

- **RuntimeGrid**: every sampled actor matches a rule.
- **No actor is unvisited in all three families.**
- **Ignore lists**: no sampled actor was stopped by `ActorTypesIgnoredBy*Rules` or the exclusion
  tags, so they hide nothing here.
- **Rule setup**: `AuditRuleSetup` reports no unresolved entry and no "can never match" rule. It only
  reports informational overlaps (`DA_MISSIONS_CHILD_Rules` / `DA_MISSIONS_Rules`,
  `HW` and `HM` `NoneExclude` / `NoneInclude`) and HLOD rules with no target layer. The seven dead
  rules above are invisible to it, because it does not look at actors.

## Recommendations and open questions

1. **HLOD, `SmallGrid`**: add `SmallGrid` to `DA_Overland_HLODLayer_NoneExclude_Rules` (a third
   condition, `Types=Actor` AND `Grid=SmallGrid`), so the "small actors out of HLOD" intent is ruled
   rather than inherited. Run `PreviewRuleMatches` before and after: in the sample, 87 of the 95
   (12 % of the processed actors) would move to *Matched* with no value change, and 8 (1.1 %) would
   leave HLOD.
2. **HLOD, Dungeons / Missions / Sanctuary**: decide whether large actors there should be in HLOD,
   then either drop those paths from `NoneInclude`'s exclusions or author per-zone HLOD rules like
   the Hogwarts and Hogsmeade ones.
3. **DataLayer**: decide per class. For the ones that should stay layer-less, say so with an ignore
   list (`ActorTypesIgnoredByDataLayerRules`), so "no DataLayer" becomes a ruled outcome. Clear the
   15 leftover layers.
4. **Force-exclude substrings**: replace `_INT` and `_POP` with `_INT/` and `_POP/` after checking
   what each variant catches with `FindActorsByOutlinerPath`.
5. **Dead rules**: confirm with the owners that the seven rules target other worlds, otherwise
   unregister them.
6. **Open**: the gap sizes across the **whole level** (622 307 descriptors, not only the actors that
   needed a write). That needs a sample drawn from the descriptors rather than from the log.

## How this audit was run

1. **Population**: every `LogWorldPartitionRuleBuilder: Display: Applying rules on actor: <path>`
   line of the 2026-10-24 Apply log (61 079 distinct paths; 1 005 more paths only appear as
   checkout-skipped). Rule snapshot captured from the editor on 2026-10-26 (57 DataLayer, 8
   RuntimeGrid, 15 HLOD rules); the rule definitions were re-read live on 2026-10-28.
2. **Offline replay**: the `RuleEvaluator` of `WPRulesReviewer` replayed every path with the outliner
   path as the only known fact. It decides very little (every actor stays *possible* in every family,
   because the rules read the class, the bounds or the grid), but it is exact for the
   [path entries that match nothing](#rule-side-outliner-path-entries-that-match-nothing).
3. **Engine sample**: 840 random paths (seeds 1 and 42) were passed to
   `WorldPartitionRuleAuditToolset.GetActorRuleFacts` over Unreal MCP
   (`http://unrealmcp.internal:8000/mcp`, `LV_Overland` open). It reads the descriptor, so unloaded
   actors work. It returns the facts and the engine verdict for all three families. The rate is about
   1.6 s per actor, and the editor serializes calls, so the full 61 079 would take over 27 hours.
4. **Unresolved paths**: 114 of the 840 paths (13.6 %) did not resolve. 68 are no longer found,
   mostly Mercuna nav chunks regenerated since the build. 35 are ambiguous (two actors share label
   and folder), and 11 failed otherwise. The nav chunks match `DA_NAV_Rules`, so dropping them
   slightly overstates the DataLayer gap.
5. **Scripts**: [`scripts/RuleCoverageGaps-2026-10-28/`](scripts/RuleCoverageGaps-2026-10-28/) is a
   .NET 9 console project that references `WPRulesReviewer.Core` from the
   `world-partition-rules-processing-reviewer` repo. Its modes:
   - `<snapshot> <log> <outDir>` runs the offline replay and the zero-hit path entries;
   - `facts <paths.txt> <out.jsonl> 1` runs the engine sample, resumable;
   - `aggregate <out.jsonl> <outDir>` produces the per-family buckets.

## Data

| File | Content |
|---|---|
| [`RuleCoverageGaps-LV_Overland-Sample-2026-10-28.csv`](RuleCoverageGaps-LV_Overland-Sample-2026-10-28.csv) | The 265 unvisited (family, actor) pairs of the engine sample: family, stable or transient, gap type, class, assigned RuntimeGrid, largest bounds axis, current value, outliner path |
| [`RuleCoverageGaps-LV_Overland-ZeroHitPathEntries-2026-10-28.csv`](RuleCoverageGaps-LV_Overland-ZeroHitPathEntries-2026-10-28.csv) | The 55 rule and settings outliner-path entries that match none of the 61 079 processed paths |
