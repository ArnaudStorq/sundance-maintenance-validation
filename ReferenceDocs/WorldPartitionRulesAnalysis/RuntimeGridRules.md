Parent: [World Partition rules — data-asset analysis](../WorldPartitionRulesAnalysis.md)

# Runtime Grid rules

The five `URuntimeGridRuleAsset` assets in
`/Game/Data/WorldPartition/RuntimeGrid/` and the two-stage grid assignment they
implement.

Runtime grids decide **which streaming cell** an actor belongs to (and therefore its
cell size, loading range and HLOD behaviour). The rule only ever stores a grid
**name** (`TargetRuntimeGrid`); the physical numbers live on the map's runtime hash.

---

## The two-stage grid architecture

The single most important structural fact about grids in Sundance is that grid
assignment happens in **two stages with different rule sets**:

| Stage | Config field | Rules used | Writes to disk? |
|-------|--------------|-----------|-----------------|
| **On save / builder** | `RuntimeGridRulesForActorSave` | `DA_HogsmeadeGrid_Rules`, `DA_HogwartsGrid_Rules`, `DA_HogwartsInteriorGrid_Rules`, `DA_NoneGrid_Rules` | **Yes** — serialized onto the actor. |
| **Streaming generation** | `RuntimeGridRulesForStreamingGeneration` | `DA_SmallGrid_Rules` | **No** — view-only override at generation time. |

Read together, the intent is:

1. **On save**, actors inside the sub-worlds get an explicit grid
   (`HogsmeadeGrid`, `HogwartsGrid`, or `SmallGrid` for Hogwarts interiors), and
   everything else in Overland is **cleared to `None`** by `DA_NoneGrid_Rules`.
2. **At streaming generation**, `DA_SmallGrid_Rules` sweeps the broad population of
   Overland actors onto `SmallGrid` — but only as a generation-time view, and only
   where the actor's HLOD layer is valid on the SmallGrid partition (otherwise the
   override is skipped and warned, see [rule engine mechanics](RuleEngineMechanics.md#b-during-streaming-generation--the-mutator)).

This is deliberate: baking `SmallGrid` onto thousands of Overland actors on every
save would be destructive and noisy, so it is kept off the on-save path. During the
migration passes `DA_SmallGrid_Rules` was *temporarily* added to
`RuntimeGridRulesForActorSave`, actors were processed once, and it was removed again
(the "on-save toggle", CLs 1959020 → 1960226).

---

## On-save grid rules (order as configured)

`RuntimeGridRulesForActorSave` is evaluated top to bottom; first match wins.

### 1. `DA_HogsmeadeGrid_Rules` → `HogsmeadeGrid`

| Aspect | Value |
|--------|-------|
| Class | `URuntimeGridRuleAsset` |
| `TargetRuntimeGrid` | `HogsmeadeGrid` |
| Matches (type) | `LevelInstance` |
| Matches (outliner) | path contains `LV_Overland/Hogsmeade/LI_Hogsmeade` (with variant substrings `_Lighting_EXT`, `_EXT`, `_INT`, `_POP`, `_Bridge`, `_Doors`) |
| Excludes (path) | `LI_Overland_Global_Sky` |
| Excludes (defer to Data Layer rule) | `DA_AUDIO_Rules` |

Assigns the Hogsmeade sub-world content to the finer `HogsmeadeGrid`. Audio-data-layer
actors are excluded so they are not pulled onto the spatial grid.

### 2. `DA_HogwartsGrid_Rules` → `HogwartsGrid`

| Aspect | Value |
|--------|-------|
| `TargetRuntimeGrid` | `HogwartsGrid` |
| Matches (type) | `LevelInstance` |
| Matches (outliner) | path contains `LV_Overland/Hogwarts/LI_Hogwarts` |
| Excludes (defer to grid rule) | `DA_HogwartsInteriorGrid_Rules` |
| Excludes (path) | `LI_Overland_Global_Sky` |
| Excludes (defer to Data Layer rule) | `DA_AUDIO_Rules` |

Assigns the **exterior** Hogwarts content to `HogwartsGrid`. Because it defers to
`DA_HogwartsInteriorGrid_Rules`, any actor that the interior rule would claim is left
for that rule (next).

### 3. `DA_HogwartsInteriorGrid_Rules` → `SmallGrid`

| Aspect | Value |
|--------|-------|
| `TargetRuntimeGrid` | **`SmallGrid`** (despite the asset name) |
| Matches (type) | `LevelInstance` |
| Matches (outliner) | path contains `LV_Overland/Hogwarts/LI_Hogwarts` **and** `_INT` |

> **Note the naming vs behaviour mismatch.** The asset is called
> `HogwartsInteriorGrid` but its `TargetRuntimeGrid` is `SmallGrid`, not a grid named
> "HogwartsInterior". Hogwarts **interior** (`_INT`) content is therefore streamed on
> the same fine `SmallGrid` as the general small-object population. Keep this in mind
> when reasoning about interiors — searching for a "HogwartsInteriorGrid" grid on the
> map will not find one.

### 4. `DA_NoneGrid_Rules` → `None` (catch-all)

| Aspect | Value |
|--------|-------|
| `TargetRuntimeGrid` | `None` (clears the grid) |
| Matches (type) | `Actor` (everything) |
| Excludes (defer to grid rules) | `DA_HogsmeadeGrid_Rules`, `DA_HogwartsGrid_Rules`, `DA_HogwartsInteriorGrid_Rules` |
| Bounds fields present | only `MaxBounds*` (no min gate) |

The terminal rule: any actor **not** claimed by the three sub-world grid rules has
its grid cleared to `None` on save. That is what makes the general Overland
population eligible for the streaming-generation `SmallGrid` sweep (a cleared grid is
exactly the state `DA_SmallGrid_Rules` then overrides at generation time).

---

## Streaming-generation grid rule

### 5. `DA_SmallGrid_Rules` → `SmallGrid` (generation-time, view-only)

| Aspect | Value |
|--------|-------|
| Class | `URuntimeGridRuleAsset` |
| `TargetRuntimeGrid` | `SmallGrid` |
| Config slot | `RuntimeGridRulesForStreamingGeneration` (**not** on save) |
| Matches (type) | `Actor` (broad), conditions use both `AND` and `OR` operators |
| Excludes (types) | `LandscapeSplineActor`, `PCGPartitionActor`, `WorldPartitionHLOD`, `ForageableBlueprint` |
| Excludes (paths) | `Dungeon`, `Mission`, `LI_Sanctuary`, `LV_Overland/Hogsmeade/LI_Hogsmeade`, `LV_Overland/Hogwarts/LI_Hogwarts` |
| Excludes (defer to Data Layer rules) | `DA_AUDIO_Rules`, `DA_AUTOMATION_Rules`, `DA_DEGUG_Rules`, `DA_WORLD_EVENTS_Rules`, `DA_MISSIONS_Rules` |

This is the rule that puts the bulk of Overland's small objects onto `SmallGrid` at
generation time. Its exclusions carve out everything that is handled elsewhere:

- **Sub-worlds** (`Hogsmeade`, `Hogwarts`) — they already got explicit grids on save.
- **Special systems** — landscape splines, PCG partition actors, generated HLOD
  actors, and foraging blueprints are excluded because they must stay on their own
  grids / not be spatially re-bucketed.
- **Gameplay-scoped content** — dungeons, missions, sanctuary, world-events and
  automation/audio/debug data layers are excluded so streaming of those systems is
  driven by their own logic.

The excluded actor **types** here mirror the `ActorTypesIgnoredByRuntimeGridRules`
philosophy but are applied specifically to the SmallGrid sweep.

> **Why this can be "Skipped".** When the mutator tries to move an actor to
> `SmallGrid` but the actor carries an HLOD layer that is not valid on the SmallGrid
> partition (e.g. an LI still tagged `LV_Overland_HLODLayer_Near`), it refuses the
> move and logs `Skipped RuntimeGrid override`. The fix is to align the actor's HLOD
> layer (via the HLOD rules) or to exclude it — see
> [HLOD Layer rules](HLODLayerRules.md) and
> [World Partition rules](../WorldPartitionRules.md).

---

## Grid physical parameters (not stored in the rules)

The rules carry only names. The cell size / loading range for each grid are
serialized on the map's `UWorldPartitionRuntimeSpatialHash` /
`FSpatialHashStreamingGrid`, and the grid ↔ HLOD-layer compatibility allowlist comes
from the map's runtime hash plus `DefaultPlugins.ini`:

```43:44:D:\Sun\Sundance\Config\DefaultPlugins.ini
+AllowedRuntimeGrids=(RuntimeGrid="MainGrid",AllowedHLODLayers=("/Game/Data/WorldPartition/HLOD/Overland/LV_Overland_HLODLayer_Near.LV_Overland_HLODLayer_Near",None))
+AllowedRuntimeGrids=(RuntimeGrid="FarFoliageGrid",AllowedHLODLayers=("/Game/Data/WorldPartition/HLOD/FarFoliage/LV_FarFoliage_HLODLayer_Foliage_Mid.LV_FarFoliage_HLODLayer_Foliage_Mid"))
```

Only `MainGrid` and `FarFoliageGrid` are declared in `DefaultPlugins.ini`; the
`SmallGrid`, `HogsmeadeGrid` and `HogwartsGrid` partitions (and their allowed HLOD
layers) are defined **on the map's runtime hash set**, which is the authoritative
compatibility source consulted by `IsValidHLODLayer`
([streaming properties](../WorldPartitionStreamingProperties.md)).

Approximate, **documented** values (confirm against the map hash before quoting):

| Grid | Cell size | Loading range | Notes |
|------|-----------|---------------|-------|
| `SmallGrid` | ~76.2 m | ~128 m | General small-object grid; the migration target. |
| `HogsmeadeGrid` | ~32 m | ~64 m | Finer than SmallGrid; Hogsmeade sub-world. |
| `HogwartsGrid` | *(on map hash)* | *(on map hash)* | Hogwarts exterior. |

> These distances are **not** in the rule assets; they are quoted from
> [World Partition rules](../WorldPartitionRules.md) and must be verified against
> `LV_Overland`'s runtime hash. They are included only for context.

---

## Summary table

| Asset | Target grid | Matches | Key exclusions | Path |
|-------|-------------|---------|----------------|------|
| `DA_HogsmeadeGrid_Rules` | `HogsmeadeGrid` | `LevelInstance` in Hogsmeade LI | Global Sky; audio DL | on-save |
| `DA_HogwartsGrid_Rules` | `HogwartsGrid` | `LevelInstance` in Hogwarts LI | interior rule; Global Sky; audio DL | on-save |
| `DA_HogwartsInteriorGrid_Rules` | `SmallGrid` | `LevelInstance` in Hogwarts LI `_INT` | — | on-save |
| `DA_NoneGrid_Rules` | `None` | any `Actor` | the 3 sub-world grid rules | on-save (catch-all) |
| `DA_SmallGrid_Rules` | `SmallGrid` | any `Actor` (AND/OR) | splines, PCG, HLOD, forage; sub-worlds; dungeon/mission/sanctuary; audio/automation/debug/WE/missions DL | streaming-gen only |

---

**In this series:** [Rule engine mechanics](RuleEngineMechanics.md) | **Runtime Grid rules** | [HLOD Layer rules](HLODLayerRules.md) | [HLOD Layer target assets](HLODLayerTargetAssets.md) | [Processing order & priority](ProcessingOrderAndPriority.md) | [Data asset inventory](DataAssetInventory.md)

Back to the [analysis overview](../WorldPartitionRulesAnalysis.md).
