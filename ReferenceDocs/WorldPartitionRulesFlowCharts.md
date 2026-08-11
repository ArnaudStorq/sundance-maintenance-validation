Parent: [Reference Docs](README.md)

# World Partition Rules — Full Decision Reference (`LV_Overland`)

This document unrolls the **complete** WorldPartitionRule logic as it is registered **right now**
in `UWorldPartitionRuleSettings` (`Config/DefaultEditor.ini`). It lists **every** rule Data Asset,
its attributes, and the decision logic that assigns **RuntimeGrid**, **HLOD Layer** and
**DataLayers** to an actor on save (and during the `WorldPartitionRuleBuilder` commandlet).

Source: read live from the editor via Unreal MCP (`WorldPartitionRuleAuditToolset` /
`WorldPartitionRuleAuthoringToolset`).

> Companion to the [rule data-asset analysis](WorldPartitionRulesAnalysis.md) and the
> [World Partition rules how-to](WorldPartitionRules.md). Those explain the engine and the *why*;
> this doc is the flat, exhaustive decision table for *what actually matches today*.

---

## How to read this document

The logic is written as plain `if … then …` pseudo-code. Notation used in every rule:

| Notation | Meaning |
|----------|---------|
| `type = X` | the actor's class **is** `X` (C++ or Blueprint). Short names are used, e.g. `LevelInstance`, `LandscapeStreamingProxy`, `RoadActor`, `WaterBodyOcean`. |
| `path ~ 'X'` | the actor's full **World Outliner path** (folders + Level Instance names) **contains** the substring `X`. |
| `Max <= N` / `Min >= N` | `MaxBoundsDimension` / `MinBoundsDimension`: largest / smallest side of the actor's bounding box, in **world units (cm)**. |
| `grid == X` | the actor's **already-assigned RuntimeGrid** (grid rules run before HLOD rules). |
| `tag = X` | the actor carries editor/gameplay tag `X`. |
| `A AND B` / `A OR B` | how the criteria inside one condition are combined. |

**Matching model**

- A rule has one or more **conditions**. The rule **matches** if **any** of its conditions is
  satisfied (conditions are OR-ed together).
- A rule can **opt out** through its **exclusions** (`exclude if …`). If any exclusion matches,
  the rule is skipped for that actor.
- **`RuntimeGrid` and `HLODLayer` are single-valued**: the rules are applied **in array order**
  and the **LAST matching rule silently wins**.
- **`DataLayers` is multi-valued**: **every** matching rule **adds** its layer. The result is the
  **union**; order does not matter.
- **Global gates** (ignore / force lists) can stop the whole system for an actor **before** any
  rule runs.

> Note: this replaces the earlier flowcharts whose nodes were labelled `RG0`, `H1`, … — those were
> just internal diagram ids. Everything below names the actual rule assets instead.

---

## 0. Global gates (evaluated first, per type)

These come from `UWorldPartitionRuleSettings`. If a gate catches the actor, **no rule of that type
is evaluated**.

| Setting | Count | Effect |
|---------|-------|--------|
| `ActorTypesIgnoredByDataLayerRules` | 6 | DataLayer rules skipped; DataLayers left unchanged. |
| `ActorTypesIgnoredByRuntimeGridRules` | 6 | RuntimeGrid rules skipped; grid left unchanged. |
| `ActorTypesToClearRuntimeGrid` | 1 | RuntimeGrid forced to `None`. |
| `ActorTypesIgnoredByHLODLayerRules` | 4 | HLOD rules skipped; HLOD setting left unchanged. |
| `ActorTypesToForceExcludeFromHLOD` | 7 | Actor forced **out** of HLOD. |
| `OutlinerPathsToForceExcludeFromHLOD` | 38 | Actors under these paths forced **out** of HLOD. |

---

## 1. RuntimeGrid assignment (single-valued — last match wins)

### 1.1 Catalog (5 rules, in precedence order)

| Idx | Rule asset | Assigns | Matches when | Excluded when |
|-----|-----------|---------|--------------|---------------|
| 0 | `DA_HogsmeadeGrid_Rules` | `HogsmeadeGrid` | `type = LevelInstance` AND `path ~ 'LV_Overland/Hogsmeade/LI_Hogsmeade'` | `path ~` any of `_Lighting_EXT`, `LI_Overland_Global_Sky`, `_EXT`, `_INT`, `_POP`, `_Bridge`, `_Doors`; or actor matched by `DA_AUDIO` |
| 1 | `DA_HogwartsGrid_Rules` | `HogwartsGrid` | `type = LevelInstance` AND `path ~ 'LV_Overland/Hogwarts/LI_Hogwarts'` | `path ~ 'LI_Overland_Global_Sky'`; matched by `DA_AUDIO`; matched by `DA_HogwartsInteriorGrid_Rules` |
| 2 | `DA_HogwartsInteriorGrid_Rules` | `SmallGrid` | `type = LevelInstance` AND `path ~ 'LV_Overland/Hogwarts/LI_Hogwarts'` AND `path ~ '_INT'` | (none) |
| 3 | `DA_NoneGrid_Rules` | `None` | `type = Actor` (everything) | matched by rules 0, 1, 2 **or** 4 |
| 4 | `DA_SmallGrid_Rules` | `SmallGrid` | (`type = Actor` AND `Max <= 100.0`) **OR** `type = ForageableBlueprint` | see full exclusion list below |

**Rule 4 (`DA_SmallGrid_Rules`) exclusions** — skip when actor is:
- **type** = one of `WorldPartitionHLOD`, `PCGPartitionActor`, `PCGFeaturesSplineInstancer`,
  `BP_PCGBiomeSetup`, `LandscapeSplineActor`, `AvaSpawnGraphSpawnLocation`, `MercunaNavSeed`,
  `MercunaNavOctree`, `AvaNoteActor`, `POINamedPoint`, `Station`, `NiagaraParticleLocator`,
  `StreamingDependencyGroupVolumeAggregateActor`;
- **`path ~`** one of `Dungeon`, `Mission`, `LV_Overland/Hogsmeade/LI_Hogsmeade`,
  `LV_Overland/Hogwarts/LI_Hogwarts`, `LI_Sanctuary`, `LOC_OL_`;
- **matched by a DataLayer rule**: `DA_AUDIO`, `DA_AUTOMATION`, `DA_DEGUG`, `DA_WORLD_EVENTS`,
  `DA_MISSIONS`.

### 1.2 Decision logic

```text
grid = (unchanged)

# --- Global gates ---
if type in ActorTypesIgnoredByRuntimeGridRules:   STOP        # grid left unchanged
if type in ActorTypesToClearRuntimeGrid:          grid = None ; STOP

# --- Rules in order; each match OVERWRITES the previous (last wins) ---
if (type = LevelInstance AND path ~ 'LV_Overland/Hogsmeade/LI_Hogsmeade')
        AND NOT path ~ any('_Lighting_EXT','LI_Overland_Global_Sky','_EXT','_INT','_POP','_Bridge','_Doors')
        AND NOT matched_by(DA_AUDIO):
    grid = HogsmeadeGrid

if (type = LevelInstance AND path ~ 'LV_Overland/Hogwarts/LI_Hogwarts')
        AND NOT path ~ 'LI_Overland_Global_Sky'
        AND NOT matched_by(DA_AUDIO)
        AND NOT matched_by(DA_HogwartsInteriorGrid_Rules):
    grid = HogwartsGrid

if (type = LevelInstance AND path ~ 'LV_Overland/Hogwarts/LI_Hogwarts' AND path ~ '_INT'):
    grid = SmallGrid                       # <-- path A to SmallGrid

if (type = Actor) AND NOT matched_by(rule0, rule1, rule2, rule4):
    grid = None

if ((type = Actor AND Max <= 100.0) OR type = ForageableBlueprint)
        AND NOT excluded_by_rule4(...):
    grid = SmallGrid                       # <-- path B to SmallGrid (LAST, so it overrides)

FINAL RuntimeGrid = grid
```

### 1.3 So how does an actor get `SmallGrid`?

- **Path A — `DA_HogwartsInteriorGrid_Rules` (idx 2):** the actor is a `LevelInstance` whose
  Outliner path contains **both** `LV_Overland/Hogwarts/LI_Hogwarts` **and** `_INT`.
- **Path B — `DA_SmallGrid_Rules` (idx 4):** the actor is **small** (`Max <= 100.0`) **or** a
  `ForageableBlueprint`, and is **not** caught by any Rule 4 exclusion.

Because idx 4 is **last**, when Path B matches it overrides `None` (idx 3) and the named grids —
except where its exclusions protect the Hogwarts/Hogsmeade Level Instances, Missions, Dungeons,
Sanctuary and `LOC_OL_` actors, so inside those areas the earlier named grid stays.

---

## 2. HLOD Layer assignment (single-valued — last match wins)

All 14 HLOD rules live in **one ordered array**, grouped by area. Almost every rule also excludes
the other areas' paths, and the Overland rules require `grid == None`, so in practice each actor is
handled by its own area group; the later (Hogwarts/Hogsmeade) groups override Overland for their
actors. Two special targets: **`Include/None`** = built into HLOD with the grid's default layer;
**`Excluded`** = left out of HLOD entirely.

### 2.1 Catalog (14 rules, in precedence order)

| Idx | Rule asset | Result | Matches when | Notable exclusions |
|-----|-----------|--------|--------------|--------------------|
| 0 | `DA_Overland_HLODLayer_NoneInclude_Rules` | Include / None | `Min >= 200.0` AND `grid == None` | not `LevelInstance`; not area paths; the other Overland rules; `DA_SmallGrid` |
| 1 | `DA_Overland_HLODLayer_NoneExclude_Rules` | Excluded | `type = Actor` AND `Max <= 200.0` AND `grid == None` | Hogwarts/Hogsmeade LI; the other Overland rules |
| 2 | `DA_Overland_HLODLayer_Near_Rules` | `LV_Overland_HLODLayer_Near` | (`LevelInstance` AND `grid == None`) OR (`path ~ '_BLK'` AND `Min >= 200` AND `grid == None`) OR (`path ~ 'Blockout'` AND `Min >= 200` AND `grid == None`) | area paths; `Foliage_Near`; `DA_SmallGrid` |
| 3 | `DA_Overland_HLODLayer_Foliage_Near_Rules` | Include / None | `type = InstancedFoliageActor` (`grid == None`) OR `path ~` a tree mesh name (`SM_Birch`, `SM_FF_Tree`, `SM_Hawthorn`, `SM_HM_HeroBeech`, `SM_Juniper_Manicured`, `SM_Larch`, `SM_Oak`, `SM_Pine`, `SM_ScotsPine`, `SM_Spruce`, `SM_WildCherry`) with `grid == None` | Hogwarts/Hogsmeade/Sanctuary LI |
| 4 | `DA_Overland_HLODLayer_Landscape_Near_Rules` | `LV_Overland_HLODLayer_Landscape_Near` | `type = LandscapeStreamingProxy` AND `grid == None` | Hogwarts/Hogsmeade LI; `Dungeon`; `Sanctuary` |
| 5 | `DA_Overland_HLODLayer_Water_Near_Rules` | `LV_Overland_HLODLayer_Water_Near` | `type =` any WaterBody (`River`, `Ocean`, `Lake`, `Island`, `Custom`) | Hogwarts/Hogsmeade LI; `Dungeon`; `Sanctuary` |
| 6 | `DA_Overland_HLODLayer_Road_Near_Rules` | `LV_Overland_HLODLayer_Road_Near` | `type = RoadActor` AND `grid == None` | Hogwarts/Hogsmeade LI; `Dungeon`; `Sanctuary` |
| 7 | `DA_HW_HLODLayer_NoneInclude_Rules` | Include / None | `grid == HogwartsGrid` OR `path ~ 'LI_Hogwarts'` | `LevelInstance`; `_INT`; `LI_WE`; `LI_DUN`; `Dungeon`; `Mission`; `HW_Near` |
| 8 | `DA_HW_HLODLayer_NoneExclude_Rules` | Excluded | `grid == HogwartsGrid` OR `path ~ 'LI_Hogwarts'` | `HW_Near`; `HW_NoneInclude` |
| 9 | `DA_HW_HLODLayer_Near_Rules` | `LV_HW_HLODLayer_Near` | `LevelInstance` AND (`grid == HogwartsGrid` OR `path ~ 'LI_Hogwarts'`) | `_INT`; `LI_WE`; `LI_DUN`; `Dungeon`; `Mission` |
| 10 | `DA_HM_HLODLayer_NoneInclude_Rules` | Include / None | (`Min >= 200` AND `grid == HogsmeadeGrid`) OR (`path ~ 'LI_Hogsmeade'` AND `Min >= 200`) | `LevelInstance`; `_INT`; `_POP`; `LI_WE`; `Mission`; `HM_Near`; `HM_Foliage` |
| 11 | `DA_HM_HLODLayer_NoneExclude_Rules` | Excluded | `grid == HogsmeadeGrid` OR `path ~ 'LI_Hogsmeade'` | `HM_NoneInclude`; `HM_Near`; `HM_Foliage` |
| 12 | `DA_HM_HLODLayer_Near_Rules` | `LV_HM_HLODLayer_Near` | (`LevelInstance` AND `path ~ 'LI_Hogsmeade'`) OR (`path ~ 'LI_Hogsmeade'` AND `path ~ 'Misc'` AND `path ~ '_BLK'` AND `Min >= 200`) OR (`path ~ '/LI_Hogsmeade/LI_Hogsmeade'` AND `path ~ 'Misc'` AND `path ~ '_EXT'`) | `_INT`; `_POP`; `LI_WE`; `Dungeon`; `Mission`; `HM_Foliage` |
| 13 | `DA_HM_HLODLayer_Foliage_Near_Rules` | Include / None | `type = InstancedFoliageActor` OR `path ~` a tree mesh name (12 conditions, same tree list as idx 3) | — |

### 2.2 Decision logic

```text
hlod = (unchanged)

# --- Global gates ---
if type in ActorTypesIgnoredByHLODLayerRules:                         STOP
if type in ActorTypesToForceExcludeFromHLOD
   OR path in OutlinerPathsToForceExcludeFromHLOD:                    hlod = Excluded ; STOP

# --- Overland group (only bites when grid == None) ---
if Min >= 200 AND grid == None AND not LevelInstance AND not area:    hlod = Include/None      # 0
if type = Actor AND Max <= 200 AND grid == None:                     hlod = Excluded          # 1
if (LevelInstance AND grid==None)
   OR (path ~ '_BLK'/'Blockout' AND Min >= 200 AND grid==None):       hlod = Overland_Near     # 2
if InstancedFoliageActor OR path ~ tree_mesh_name (grid==None):       hlod = Include/None      # 3
if LandscapeStreamingProxy AND grid==None:                            hlod = Overland_Landscape_Near   # 4
if type = WaterBody*:                                                 hlod = Overland_Water_Near       # 5
if RoadActor AND grid==None:                                          hlod = Overland_Road_Near        # 6

# --- Hogwarts group (grid == HogwartsGrid or under LI_Hogwarts) ---
if (grid==HogwartsGrid OR path~'LI_Hogwarts') AND not(_INT/LI_WE/LI_DUN/Dungeon/Mission/LevelInstance):  hlod = Include/None   # 7
if (grid==HogwartsGrid OR path~'LI_Hogwarts'):                        hlod = Excluded          # 8  (unless 7/9 excluded it)
if LevelInstance AND (grid==HogwartsGrid OR path~'LI_Hogwarts') AND not(_INT/LI_WE/LI_DUN/Dungeon/Mission): hlod = HW_Near     # 9

# --- Hogsmeade group (grid == HogsmeadeGrid or under LI_Hogsmeade) ---
if (Min>=200 AND grid==HogsmeadeGrid) OR (path~'LI_Hogsmeade' AND Min>=200):  hlod = Include/None          # 10
if (grid==HogsmeadeGrid OR path~'LI_Hogsmeade'):                     hlod = Excluded                       # 11
if (LevelInstance AND path~'LI_Hogsmeade')
   OR (path~'LI_Hogsmeade' AND 'Misc' AND '_BLK' AND Min>=200)
   OR (path~'/LI_Hogsmeade/LI_Hogsmeade' AND 'Misc' AND '_EXT'):      hlod = HM_Near                        # 12
if InstancedFoliageActor OR path ~ tree_mesh_name:                    hlod = Include/None                   # 13

FINAL HLOD = last value set
```

Reading it: the **type-specific** rules (Landscape / Water / Road, and the area `Near` rules) sit
**after** the generic size/None rules, so they win. Interiors (`_INT`) are pushed out of HLOD by
the `_INT` exclusions.

---

## 3. DataLayers assignment (multi-valued — union of all matches)

The system walks **all 57** rules; **every** matching rule **adds** its layer. No "last wins".
`target = name pattern` means the layer name is derived from the actor name by string
substitution (e.g. `LI_DUN` → `DL_DUN`).

### 3.1 Decision logic

```text
layers = {}

if type in ActorTypesIgnoredByDataLayerRules:   STOP        # DataLayers left unchanged

for each rule in DataLayerRules[0..56]:
    if rule matches (any condition) AND not caught by rule exclusions:
        if rule.target is a fixed layer:   layers.add(that layer)
        else (name pattern):               layers.add(layer derived from actor name)

FINAL DataLayers = layers          # the union
```

### 3.2 Full catalog (57 rules)

`~` = path contains. Types shown with short names.

| Idx | Rule asset | Adds layer | Matches when | Excluded when |
|-----|-----------|-----------|--------------|---------------|
| 0 | `DA_AUTOMATION_Rules` | `DL_AUTOMATION` | `type = AutomatedCaptureFlightPath` | — |
| 1 | `DA_DEBUG_RUNTIME_Rules` | `DL_DEBUG_RUNTIME` | `type = BP_OL_Util_Footprint` | — |
| 2 | `DA_ANIMATION_Rules` | `DL_ANIMATION` | `type = SceneRigActor` | — |
| 3 | `DA_AUDIO_Rules` | `DL_AUDIO` | `type =` any `Ak*` audio (`AkAcousticPortal`, `AkAmbientSound`, `AkReverbVolume`, `AkSpatialAudioVolume`, `AkSpotReflector`) or `BP_TempLoadAudioBanks`, **or** `path ~ 'AUDIO'`; **or** `LerpVolume*` AND `path ~ 'AUDIO'` | — |
| 4 | `DA_AVA_NOTES_Rules` | `DL_AVA_NOTES` | `type = AvaNoteActor` or `BP_OL_Util_Footprint`, or `path ~ 'SM_CIN_Markup'` | — |
| 5 | `DA_CLIFF_Rules` | `DL_CLIFF` | `type = LevelInstance` AND `path ~ 'CliffRocks'` | — |
| 6 | `DA_DEGUG_Rules` | `DL_DEBUG` | `path ~ 'Debug-Reference_Actors'` | — |
| 7 | `DA_LANDSCAPE_Rules` | `DL_LANDSCAPE` | `type = LandscapeStreamingProxy` or `LandscapeSplineActor` | — |
| 8 | `DA_LIGHTHING_Rules` | `DL_LIGHTING` | `type =` a light (`DirectionalLight`, `PointLight`, `SpotLight`, `RectLight`, `SkyLight`), `HDRIBackdrop` or `BP_Light_Fixture_Master`, **or** `path ~ 'LIGHTING'` | `type = DayNightSkyRigActor`/`GlobalLightRigActor`; `path ~ '0_GlobalLighting'` |
| 9 | `DA_NAV_Rules` | `DL_NAV` | `type =` any `Odc*`/`Mercuna*` navmesh type; **or** `LevelInstance` AND `path ~ '_Nav'` | — |
| 10 | `DA_PROCEDURAL_Rules` | `DL_PROCEDURAL` | `type = BP_PCGBiomeSetup` or `PCGVolume`, or `path ~ 'BP_PCG'` | `type = PCGPartitionActor` |
| 11 | `DA_RENDER_Rules` | `DL_RENDER` | `type = StaticMeshActor` or `BP_SunDoorTemplate` | matched by `DA_CLIFF`, `DA_PROCEDURAL`, `DA_ROAD`, `DA_WATER` |
| 12 | `DA_ROAD_Rules` | `DL_ROAD` | `type = RoadActor` or `RoadBrushManager` | — |
| 13 | `DA_SKY_Rules` | `DL_SKY` | (`LevelInstance` AND `path ~ 'LI_Overland_Global_Sky'`); **or** `type = DayNightSkyRigActor`/`GlobalLightRigActor`/`GlobalHeightActor`, or `path ~ '0_GlobalLighting'` | matched by `DA_TECH` |
| 14 | `DA_TECH_Rules` | `DL_TECH` | `type =` one of `StreamingDependencyGroupLocationVolume`, `SunAIPath`, `BP_TEMP_ClassText`, `PlayerStart`, `StationBase`, `NamedPoint`, `AvaSpawnGraphSpawnLocation`, `BP_SunWorldEventLocator`; **or** `path ~ 'BP_'` | `path ~ 'BP_DayNight'`; matched by `DA_LIGHTHING`, `DA_PROCEDURAL`, `DA_RENDER`, `DA_AUDIO` |
| 15 | `DA_UI_Rules` | `DL_UI` | `LerpVolume*` AND `path ~ 'RegionNames'` | — |
| 16 | `DA_WATER_Rules` | `DL_WATER` | `type =` any WaterBody (`Custom`, `ExclusionVolume`, `Island`, `Lake`, `Ocean`, `River`), `WaterZone`, `WaterBody_Niagara_ShoreFoam`, or `NiagaraWaterfall` | — |
| 17 | `DA_TEST_01_Light_Blendable` | `DL_TEST_01_Light_Blendable` | `type = Actor` AND `path ~ '0_GlobalLighting/01_GlobalLighting_PartlyCloudy'` | — |
| 18 | `DA_TEST_02_Light_Blendable` | `DL_TEST_02_Light_Blendable` | `type = Actor` AND `path ~ '0_GlobalLighting/02_GlobalLighting_Moody'` | — |
| 19 | `DA_DUNGEONS_Rules` | pattern `LI_DUN` → `DL_DUN` | `LevelInstance` AND `path ~ 'Dungeons'` | `path ~ 'LI_Overland_Global_Sky'` |
| 20 | `DA_HOGSMEADE_Rules` | `DL_HOGSMEADE` | `LevelInstance` AND `path ~ 'LI_Hogsmeade'` | `path ~ 'River_COL'` |
| 21 | `DA_HM_EXT_Rules` | `DL_HM_EXT` | `LevelInstance` AND `path ~ 'LI_Hogsmeade'` AND `path ~ '_EXT'`; **or** `path ~ 'LI_Hogsmeade/Bridges'`; **or** `path ~ 'LI_Hogsmeade_River'` | `path ~ 'River_COL'` |
| 22 | `DA_HM_INT_Rules` | pattern `LI_` → `DL_HM_` (strip `_One_`…`_Nine_`) | `LevelInstance` AND `path ~ 'LI_Hogsmeade'` AND (`path ~ '_INT'` OR `path ~ '_POP'`) | `path ~ '_EXT'`; `path ~ '_Bridge'` |
| 23 | `DA_HOGWARTS_Rules` | `DL_HOGWARTS` | `LevelInstance` AND `path ~ 'LI_Hogwarts'` | `path ~ 'LI_Hogwarts/LevelInstances'` |
| 24 | `DA_HW_EXT_Rules` | `DL_HW_EXT` | `LevelInstance` AND `path ~ 'LI_Hogwarts/LevelInstances'` AND `path ~ '_EXT'` | — |
| 25 | `DA_HW_INT_Rules` | pattern `LI_` → `DL_HW_` | `LevelInstance` AND `path ~ 'LI_Hogwarts/LevelInstances'` AND `path ~ '_INT'` | — |
| 26 | `DA_MISSIONS_Rules` | `DL_MISSIONS` | `LevelInstance` AND `path ~ 'Missions'` | — |
| 27 | `DA_MISSIONS_CHILD_Rules` | pattern `LI_` → `DL_M_` | `LevelInstance` AND `path ~ 'Missions'` | — |
| 28 | `DA_OVERLAND_Rules` | `DL_OVERLAND` | `type =` one of `LevelInstance`, `LandscapeStreamingProxy`, `WorldBitmapStreamingProxy`, `PCGVolume`, `RoadActor`, `BP_PCGBiomeSetup`, `StaticMeshActor`, `NiagaraWaterfall`, `ForageableBlueprint`; **or** any WaterBody | `type = WorldEventInstance`/`PCGPartitionActor`; `tag = ExcludeFrom_DL_OVERLAND`; `path ~` `Missions`, `Dungeons`, `LI_Hogsmeade`, `LI_Hogwarts`, `LI_Sanctuary`, `LI_ArchitectChamber`, `LI_Overland_Global_Sky` |
| 29 | `DA_SANTUARY_Rules` | `DL_SANCTUARY` | `LevelInstance` AND `path ~ 'LI_Sanctuary'` | — |
| 30 | `DA_SANTUARY_ArchitectChamber_Rules` | `DL_SANCTUARY_ArchitectChamber` | `LevelInstance` AND `path ~ 'LI_Sanctuary_ArchitectChamber'` | — |
| 31 | `DA_SANTUARY_ConversationHub_Rules` | `DL_SANCTUARY_ConversationHub` | `LevelInstance` AND `path ~ 'LI_Sanctuary_ConversationHub'` | — |
| 32 | `DA_SANTUARY_Vivarium_Rules` | pattern `LI_Sanctuary_Vivarium_` → `DL_SANCTUARY_VIVARIUM_` | `LevelInstance` AND `path ~ 'LI_Sanctuary_Vivarium'` | — |
| 33 | `DA_WORLD_EVENTS_Rules` | pattern `LI_WE_` → `DL_WE_` | `type = WorldEventInstance` | — |
| 34 | `DA_LOC_VISTA_Rules` | `DL_LOC_VISTA` | `type = BP_OL_Vista`, or `path ~ 'LOC_OL_Vista'` | — |
| 35 | `DA_LOC_VAULT_Rules` | `DL_LOC_VAULT` | `LevelInstance` AND `path ~ 'LI_OL_Vault'`; **or** `path ~` `LOC_OL_Vault`/`LOC_OL_Vault_EXP_`/`_Vault_`/`_Vault-` | — |
| 36 | `DA_LOC_RUIN_Rules` | `DL_LOC_RUIN` | `type = BP_Location_Ruin`, or `path ~ 'LOC_OL_Ruin_'` | — |
| 37 | `DA_LOC_NAMED_ENEMY_Rules` | `DL_LOC_NAMED_ENEMY` | `type = BP_Location_NamedEnemy`, or `path ~ 'LOC_OL_NamedEnemy'` | — |
| 38 | `DA_LOC_MERLIN_PUZZLE_Rules` | `DL_LOC_MERLIN_PUZZLE` | `path ~ 'LOC_OL_MP-'` | — |
| 39 | `DA_LOC_KNOWLEDGE_CARD_Rules` | `DL_LOC_KNOWLEDGE_CARD` | `type = BP_OL_KnowledgeCard`, or `path ~ 'LOC_OL_KC-'` | — |
| 40 | `DA_LOC_HAMLET_Rules` | `DL_LOC_HAMLET` | `type = BP_Location_Hamlet`, or `path ~ 'LOC_OL_Hamlet'` | — |
| 41 | `DA_LOC_HAG_Rules` | `DL_LOC_HAG` | `type = BP_Location_Hag`, or `path ~ 'LOC_OL_Hag_'` | — |
| 42 | `DA_LOC_GRAVEYARD_Rules` | `DL_LOC_GRAVEYARD` | `type = BP_Location_Graveyard`, or `path ~ 'LOC_OL_Grave'` | — |
| 43 | `DA_LOC_GOBSTONES_Rules` | `DL_LOC_GOBSTONES` | `type = BP_Location_GobStones`, or `path ~` `LOC_OL_GobStones`/`LOC_HM_Gobstones_` | — |
| 44 | `DA_LOC_FAST_TRAVEL_Rules` | `DL_LOC_FAST_TRAVEL` | `type =` `BP_FastTravel_Wall`/`_Overland`/`_Pillar`, or `path ~` `FastTravel`/`LOC_HW_FT`/`LOC_HM_FT` | — |
| 45 | `DA_LOC_ENEMY_LAIR_Rules` | `DL_LOC_ENEMY_LAIR` | `type = BP_Location_EnemyLair`, or `path ~ 'LOC_OL_EnemyLair'` | — |
| 46 | `DA_LOC_ENEMY_CAMP_Rules` | `DL_LOC_ENEMY_CAMP` | `type =` `BP_Location_BanditCampSmall`/`Medium`, or `path ~` `LOC_OL_EnemyCamp-`/`LOC_OL_EnemyStronghold` | — |
| 47 | `DA_LOC_DUNGEON_MERLIN_Rules` | `DL_LOC_DUNGEON_MERLIN` | `type = BP_Location_DungeonMerlin`, or `path ~` `LOC_OL_DungeonMerlin`/`LOC_DUN_Merlin` | — |
| 48 | `DA_LOC_DUEL_Rules` | `DL_LOC_DUEL` | `type = BP_Location_Duel`, or `path ~ 'LOC_OL_Duel_'` | — |
| 49 | `DA_LOC_DEAD_NPC_Rules` | `DL_LOC_DEAD_NPC` | `path ~` `LOC_OL_DeadNPC`/`LI_DeadNPC` | — |
| 50 | `DA_LOC_DE_GNOME_Rules` | `DL_LOC_DE_GNOME` | `path ~ 'LOC_OL_De-Gnome'` | — |
| 51 | `DA_LOC_COMMUNITY_BOARD_Rules` | `DL_LOC_COMMUNITY_BOARD` | `type = BP_JobBoard`, or `path ~ 'LOC_OL_CB'` | — |
| 52 | `DA_LOC_BOTHY_Rules` | `DL_LOC_BOTHY` | `type = BP_Location_Bothy`, or `path ~` `LOC_OL_Bothy`/`LI_Bothy` | — |
| 53 | `DA_LOC_BEASTIE_Rules` | `DL_LOC_BEASTIE` | `type = BP_OL_Beastie`, or `path ~ 'LOC_OL_Beastie'` | — |
| 54 | `DA_LOC_BEAST_REFUGE_Rules` | `DL_LOC_BEAST_REFUGE` | `type = BP_Location_BeastRefuge`, or `path ~ 'LOC_OL_BeastRefuge'` | — |
| 55 | `DA_LOC_ASTRONOMY_Rules` | `DL_LOC_ASTRONOMY` | `path ~ 'LOC_OL_AT'` | — |
| 56 | `DA_LOC_ACTIVITY_Rules` | `DL_LOC_ACTIVITY` | `path ~ 'LOC_OL_Activity'` | — |

---

## How to verify on a real actor

- `WorldPartitionRuleAuditToolset.ExplainActorAssignment` — for one actor: which rules matched,
  which condition fired, which wins, and **why** each other rule was skipped.
- `WorldPartitionRuleAuditToolset.GetRuleSystemOverview` — the full ordered list of registered
  rules plus the ignore/force list counts.
- `WorldPartitionRuleAuthoringToolset.GetRuleAsset` — full conditions and exclusions of one rule.

## See also

- [World Partition rules consistency audit](WorldPartitionRulesConsistencyAudit.md) — validator + manual audit for cycles, overlaps and mishandled cases.
- [World Partition rules](WorldPartitionRules.md) — practitioner how-to, rule subsystem internals, the SmallGrid toggle.
- [World Partition rule data-asset analysis](WorldPartitionRulesAnalysis.md) — the deep, per-asset breakdown.
- [Runtime Grid rules](WorldPartitionRulesAnalysis/RuntimeGridRules.md) · [HLOD Layer rules](WorldPartitionRulesAnalysis/HLODLayerRules.md) · [Processing order & priority](WorldPartitionRulesAnalysis/ProcessingOrderAndPriority.md) · [Data asset inventory](WorldPartitionRulesAnalysis/DataAssetInventory.md).
