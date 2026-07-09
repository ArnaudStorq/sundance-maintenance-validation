Parent: [World Partition rules — data-asset analysis](../WorldPartitionRulesAnalysis.md)

# HLOD Layer rules

The twelve `UHLODLayerRuleAsset` assets (the `*_Rules` files under
`/Game/Data/WorldPartition/HLOD/`). They decide, per actor, **which HLOD layer** it
contributes to and **whether** it participates in HLOD at all.

Recall the two "None" patterns from
[rule engine mechanics](RuleEngineMechanics.md#what-applying-a-rule-does-to-the-data):

- `*_NoneInclude_Rules`: `TargetHLODLayer = None`, `IncludeInHLOD = true` → HLOD-relevant, no explicit layer (inherits parent).
- `*_NoneExclude_Rules`: `TargetHLODLayer = None`, `IncludeInHLOD = false` → dropped from HLOD entirely.

Only the `NoneExclude` rules carry a serialized `IncludeInHLOD = false`; every other
HLOD rule leaves it at its default of `true`.

---

## Overland HLOD rules

Config order in `HLODLayerRulesForActorSave` (Overland block):
`NoneInclude → NoneExclude → Near → Foliage_Near → Landscape_Near → Water_Near → Road_Near`.

The two generic "None" rules appear **first** but defer to the specific layer rules
via `HLODLayerRulesToExclude`, so in practice the specific rules win (see
[processing order & priority](ProcessingOrderAndPriority.md)).

### `DA_Overland_HLODLayer_NoneInclude_Rules`

| Aspect | Value |
|--------|-------|
| `TargetHLODLayer` | `None` |
| `IncludeInHLOD` | `true` (default) |
| Matches (type) | `LevelInstance` |
| Defers to (HLOD rules) | `Near`, `Foliage_Near`, `Landscape_Near`, `Road_Near`, `Water_Near` |
| Defers to (grid rule) | `SmallGrid` |
| Excludes (paths) | Hogwarts LI, Hogsmeade LI, `LI_Sanctuary`, `LI_WE`, `Dungeon`, `Mission` |

Level Instances in Overland that are not claimed by a specific layer rule stay
HLOD-relevant but with no explicit layer (they inherit the partition's parent HLOD
layer). Sub-worlds and gameplay scopes are excluded (they have their own rule sets).

### `DA_Overland_HLODLayer_NoneExclude_Rules`

| Aspect | Value |
|--------|-------|
| `TargetHLODLayer` | `None` |
| `IncludeInHLOD` | **`false`** |
| Matches (type) | `Actor` (everything) |
| Defers to (HLOD rules) | `Foliage_Near`, `Landscape_Near`, `Near`, `NoneInclude`, `Road_Near`, `Water_Near` |
| Excludes (paths) | Hogwarts LI, Hogsmeade LI |

The terminal HLOD rule for Overland: any actor not claimed by a specific layer rule
**or** by `NoneInclude` is dropped from HLOD (`SetHLODLayer(None)` +
`bEnableAutoLODGeneration=false`). This is what keeps stray actors from tripping the
invalid-HLOD-layer MapCheck warning.

### `DA_Overland_HLODLayer_Near_Rules`

| Aspect | Value |
|--------|-------|
| `TargetHLODLayer` | `LV_Overland_HLODLayer_Near` |
| Matches (type) | `LevelInstance` |
| Defers to (HLOD rules) | `Foliage_Near` |
| Defers to (grid rule) | `SmallGrid` |
| Excludes (paths) | `_BLK` / `Blockout`, Hogwarts LI, Hogsmeade LI, `LI_Sanctuary`, `LI_WE`, `Dungeon`, `Mission` |

The main Overland near-range HLOD assignment for Level Instances. Blockout geometry
(`_BLK`/`Blockout`) is excluded so it does not enter the shipping near HLOD. It
defers to `Foliage_Near` so foliage inside those LIs is not swept into the mesh-merge
near layer.

### `DA_Overland_HLODLayer_Foliage_Near_Rules`

| Aspect | Value |
|--------|-------|
| `TargetHLODLayer` | **unset (`None`)** |
| `IncludeInHLOD` | `true` (default) |
| Matches (type) | `InstancedFoliageActor` |
| Matches (species) | `SM_Birch`, `SM_FF_Tree`, `SM_Hawthorn`, `SM_HM_HeroBeech`, `SM_Juniper_Manicured`, `SM_Larch`, `SM_Oak`, `SM_Pine`, `SM_ScotsPine`, `SM_Spruce`, `SM_WildCherry` |
| Excludes (paths) | Hogwarts LI, Hogsmeade LI, `LI_Sanctuary` |

> **Interpretation (data-supported).** This rule matches the listed **tree** foliage
> in Overland and assigns **no explicit HLOD layer** while keeping them HLOD-relevant.
> The net data effect is identical to `NoneInclude`, but it is a *dedicated* rule so
> that tree foliage is claimed **before** any generic layer rule can grab it and is
> instead represented by the foliage/imposter HLOD pipeline (`Foliage_Far`,
> `FarFoliage`, and the imposter config), rather than by the Level-Instance
> mesh-merge near layer. The per-region `LV_*_HLODLayer_Foliage_Near` target assets
> use the **Dummy** builder (no near-range proxy), consistent with this reading — see
> [HLOD Layer target assets](HLODLayerTargetAssets.md). The intent is inferred from the matched
> types + the target being unset; the *values* (type filter, unset target, include
> = true) are read directly from the asset.

### `DA_Overland_HLODLayer_Landscape_Near_Rules`

| Aspect | Value |
|--------|-------|
| `TargetHLODLayer` | `LV_Overland_HLODLayer_Landscape_Near` |
| Matches (type) | `LandscapeStreamingProxy` |
| Excludes (paths) | Hogwarts LI, Hogsmeade LI, `Dungeon`, `Sanctuary` |

### `DA_Overland_HLODLayer_Water_Near_Rules`

| Aspect | Value |
|--------|-------|
| `TargetHLODLayer` | `LV_Overland_HLODLayer_Water_Near` |
| Matches (types) | `WaterBodyCustom`, `WaterBodyIsland`, `WaterBodyLake`, `WaterBodyOcean`, `WaterBodyRiver` |
| `LogicOperator` | **`OR`** (any water body type matches) |
| Excludes (paths) | Hogwarts LI, Hogsmeade LI, `Dungeon`, `Sanctuary` |

The only Overland HLOD rule whose condition uses `OR` — it matches if the actor is
**any** of the five water body classes.

### `DA_Overland_HLODLayer_Road_Near_Rules`

| Aspect | Value |
|--------|-------|
| `TargetHLODLayer` | `LV_Overland_HLODLayer_Road_Near` |
| Matches (type) | `RoadActor` (`/Script/RoadsRuntime`) |
| Excludes (paths) | Hogwarts LI, Hogsmeade LI, `Dungeon`, `Sanctuary` |

`Overland_Road_Near` was added specifically to route road actors to their own HLOD
layer (CL 1893933).

---

## Hogwarts HLOD rules

Config order: `NoneInclude → NoneExclude → Near`. Path scope for all three is
`LV_Overland/Hogwarts/LI_Hogwarts`.

| Asset | `TargetHLODLayer` | `IncludeInHLOD` | Matches | Defers to | Excludes (paths) |
|-------|-------------------|-----------------|---------|-----------|------------------|
| `DA_HW_HLODLayer_NoneInclude_Rules` | `None` | `true` | `LevelInstance` | `DA_HW_..._Near` | `_INT`, `LI_WE`, `LI_DUN`, `Dungeon`, `Mission` |
| `DA_HW_HLODLayer_NoneExclude_Rules` | `None` | **`false`** | `Actor` | `Near`, `NoneInclude` | — |
| `DA_HW_HLODLayer_Near_Rules` | `LV_HW_HLODLayer_Near` | `true` | `LevelInstance` | — | `_INT`, `LI_WE`, `LI_DUN`, `Dungeon`, `Mission` |

Hogwarts **interiors** (`_INT`), world-events (`LI_WE`), dungeons (`LI_DUN`,
`Dungeon`) and missions are excluded from the exterior `Near` HLOD and from
`NoneInclude`, so they are handled by their own systems / cleared.

---

## Hogsmeade HLOD rules

Config order: `NoneInclude → NoneExclude → Near → Foliage_Near`. Path scope is
`LV_Overland/Hogsmeade/LI_Hogsmeade`.

| Asset | `TargetHLODLayer` | `IncludeInHLOD` | Matches | Defers to | Excludes (paths) |
|-------|-------------------|-----------------|---------|-----------|------------------|
| `DA_HM_HLODLayer_NoneInclude_Rules` | `None` | `true` | `LevelInstance` | `Near`, `Foliage_Near` | `_INT`, `_POP`, `LI_WE`, `Mission` |
| `DA_HM_HLODLayer_NoneExclude_Rules` | `None` | **`false`** | (all) | `Foliage_Near`, `Near`, `NoneInclude` | — |
| `DA_HM_HLODLayer_Near_Rules` | `LV_HM_HLODLayer_Near` | `true` | `LevelInstance` | `Foliage_Near` | `Misc`, `_BLK`, `_EXT`, `_INT`, `_POP`, `LI_WE`, `Dungeon`, `Mission` |
| `DA_HM_HLODLayer_Foliage_Near_Rules` | **unset (`None`)** | `true` | `InstancedFoliageActor` + the 11 tree species | — | — (scoped to Hogsmeade LI) |

> **Documented bounds guard.** The Hogsmeade `NoneInclude` rule was given a **2 m
> minimum bounds dimension** (CL 1950932) so that single tiny meshes — cobble
> stones, debris — do not get pulled into HLOD. This numeric threshold is not
> readable from the package text; it is attributed to the changelist and recorded
> here for completeness. See
> [World Partition rules](../WorldPartitionRules.md).

The Hogsmeade `Foliage_Near` rule mirrors the Overland one: it claims the listed tree
species (as an `InstancedFoliageActor` within the Hogsmeade LI) with **no** explicit
target layer, keeping them HLOD-relevant but out of the `Near` mesh-merge layer.

---

## Cross-region observations

- **`NoneInclude`/`NoneExclude` are per-region.** Each region (Overland, Hogwarts,
  Hogsmeade) has its own pair, scoped by the region's Outliner path and registered
  separately in the config array. There is no single global "none" rule.
- **`Near` rules target region-specific layers.** `LV_Overland_HLODLayer_Near`,
  `LV_HW_HLODLayer_Near`, `LV_HM_HLODLayer_Near`. Their build settings differ (see
  [HLOD Layer target assets](HLODLayerTargetAssets.md)).
- **Only Overland has dedicated `Landscape/Water/Road` HLOD rules.** Hogwarts and
  Hogsmeade collapse everything into `Near`/`None`.
- **`Foliage_Near` exists only for Overland and Hogsmeade**, not Hogwarts (Hogwarts
  is largely interiors/architecture, not open foliage).
- **Every specific rule excludes the sub-worlds it doesn't own**, so a Level Instance
  is only ever claimed by the rule set of its own region.

See [processing order & priority](ProcessingOrderAndPriority.md) for exactly how these rules'
ordering + `*RulesToExclude` produce a single deterministic outcome per actor.

---

**In this series:** [Rule engine mechanics](RuleEngineMechanics.md) | [Runtime Grid rules](RuntimeGridRules.md) | **HLOD Layer rules** | [HLOD Layer target assets](HLODLayerTargetAssets.md) | [Processing order & priority](ProcessingOrderAndPriority.md) | [Data asset inventory](DataAssetInventory.md)

Back to the [analysis overview](../WorldPartitionRulesAnalysis.md).
