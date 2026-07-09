Parent: [World Partition rules — data-asset analysis](../WorldPartitionRulesAnalysis.md)

# Data asset inventory (appendix)

Complete list of every asset under `/Game/Data/WorldPartition/` with the fields
extracted from the packages, plus the project config arrays that bind them. Use this
as the lookup table behind [Runtime Grid rules](RuntimeGridRules.md),
[HLOD Layer rules](HLODLayerRules.md) and [HLOD Layer target assets](HLODLayerTargetAssets.md).

Local root: `D:\Sun\Sundance\Content\Data\WorldPartition\`
(Perforce: `//sun/Dev/Sundance/Content/Data/WorldPartition/`).

## File tree (45 assets)

```
WorldPartition/
├── RuntimeGrid/                                     5 URuntimeGridRuleAsset
│   ├── DA_HogsmeadeGrid_Rules.uasset
│   ├── DA_HogwartsGrid_Rules.uasset
│   ├── DA_HogwartsInteriorGrid_Rules.uasset
│   ├── DA_NoneGrid_Rules.uasset
│   └── DA_SmallGrid_Rules.uasset
└── HLOD/
    ├── LV_Overland_HLODLayer_Dummy.uasset           UHLODLayer (Dummy)
    ├── Overland/                                    7 rules + 10 layer assets
    │   ├── DA_Overland_HLODLayer_Near_Rules.uasset
    │   ├── DA_Overland_HLODLayer_Foliage_Near_Rules.uasset
    │   ├── DA_Overland_HLODLayer_Landscape_Near_Rules.uasset
    │   ├── DA_Overland_HLODLayer_Water_Near_Rules.uasset
    │   ├── DA_Overland_HLODLayer_Road_Near_Rules.uasset
    │   ├── DA_Overland_HLODLayer_NoneInclude_Rules.uasset
    │   ├── DA_Overland_HLODLayer_NoneExclude_Rules.uasset
    │   ├── LV_Overland_HLODLayer_Near.uasset
    │   ├── LV_Overland_HLODLayer_Far.uasset
    │   ├── LV_Overland_HLODLayer_BLK_Far.uasset
    │   ├── LV_Overland_HLODLayer_Foliage_Near.uasset
    │   ├── LV_Overland_HLODLayer_Foliage_Far.uasset
    │   ├── LV_Overland_HLODLayer_Landscape_Near.uasset
    │   ├── LV_Overland_HLODLayer_Landscape_Far2.uasset
    │   ├── LV_Overland_HLODLayer_Landscape_Far.uasset   (ObjectRedirector → Landscape_Near)
    │   ├── LV_Overland_HLODLayer_Road_Near.uasset
    │   └── LV_Overland_HLODLayer_Water_Near.uasset
    ├── Hogsmeade/                                   4 rules + 5 layer assets
    │   ├── DA_HM_HLODLayer_Near_Rules.uasset
    │   ├── DA_HM_HLODLayer_Foliage_Near_Rules.uasset
    │   ├── DA_HM_HLODLayer_NoneInclude_Rules.uasset
    │   ├── DA_HM_HLODLayer_NoneExclude_Rules.uasset
    │   ├── LV_HM_HLODLayer_Near.uasset
    │   ├── LV_HM_HLODLayer_Mid.uasset
    │   ├── LV_HM_HLODLayer_Far.uasset
    │   ├── LV_HM_HLODLayer_Foliage_Near.uasset
    │   └── LV_HM_HLODLayer_Foliage_Far.uasset
    ├── Hogwarts/                                    3 rules + 3 layer assets
    │   ├── DA_HW_HLODLayer_Near_Rules.uasset
    │   ├── DA_HW_HLODLayer_NoneInclude_Rules.uasset
    │   ├── DA_HW_HLODLayer_NoneExclude_Rules.uasset
    │   ├── LV_HW_HLODLayer_Near.uasset
    │   ├── LV_HW_HLODLayer_Mid.uasset
    │   └── LV_HW_HLODLayer_Far.uasset
    └── FarFoliage/                                  2 layer assets + 1 config
        ├── DA_FarFoliage_Config.uasset              UFarFoliageImposterConfig
        ├── LV_FarFoliage_HLODLayer_Foliage_Mid.uasset
        └── LV_FarFoliage_HLODLayer_Foliage_Far.uasset
```

Counts: **5** grid rules + **12** HLOD rules + **20** HLOD layer assets (incl. 1
redirector, 3 dummy) + **1** FarFoliage imposter config + **the root Dummy** = 45
`.uasset` files (2 duplicated names between the tree above and the flat listing are
the same files).

## RuntimeGrid rules

| Asset | `TargetRuntimeGrid` | Match type | Match path | `*RulesToExclude` | `TypesToExclude` | Path excludes | Slot |
|-------|--------------------|-----------|-----------|-------------------|------------------|---------------|------|
| `DA_HogsmeadeGrid_Rules` | `HogsmeadeGrid` | `LevelInstance` | Hogsmeade LI (`_EXT/_INT/_POP/_Bridge/_Doors/_Lighting_EXT`) | DataLayer: `DA_AUDIO` | — | `LI_Overland_Global_Sky` | save |
| `DA_HogwartsGrid_Rules` | `HogwartsGrid` | `LevelInstance` | Hogwarts LI | Grid: `HogwartsInterior`; DataLayer: `DA_AUDIO` | — | `LI_Overland_Global_Sky` | save |
| `DA_HogwartsInteriorGrid_Rules` | `SmallGrid` | `LevelInstance` | Hogwarts LI + `_INT` | — | — | — | save |
| `DA_NoneGrid_Rules` | `None` | `Actor` | (all) | Grid: `Hogsmeade`, `Hogwarts`, `HogwartsInterior` | — | — | save |
| `DA_SmallGrid_Rules` | `SmallGrid` | `Actor` (AND+OR) | (all) | DataLayer: `DA_AUDIO`, `DA_AUTOMATION`, `DA_DEGUG`, `DA_WORLD_EVENTS`, `DA_MISSIONS` | `LandscapeSplineActor`, `PCGPartitionActor`, `WorldPartitionHLOD`, `ForageableBlueprint` | `Dungeon`, `Mission`, `LI_Sanctuary`, Hogsmeade LI, Hogwarts LI | **streaming-gen** |

## HLOD Layer rules

| Asset | `TargetHLODLayer` | `IncludeInHLOD` | Match type | `HLODLayerRulesToExclude` | Other defers | Path excludes |
|-------|-------------------|-----------------|-----------|---------------------------|--------------|---------------|
| `DA_Overland_HLODLayer_NoneInclude_Rules` | None | true | `LevelInstance` | Near, Foliage_Near, Landscape_Near, Road_Near, Water_Near | Grid: SmallGrid | HW LI, HM LI, Sanctuary, WE, Dungeon, Mission |
| `DA_Overland_HLODLayer_NoneExclude_Rules` | None | **false** | `Actor` | Near, Foliage_Near, Landscape_Near, Road_Near, Water_Near, NoneInclude | — | HW LI, HM LI |
| `DA_Overland_HLODLayer_Near_Rules` | `LV_Overland_HLODLayer_Near` | true | `LevelInstance` | Foliage_Near | Grid: SmallGrid | `_BLK`/Blockout, HW LI, HM LI, Sanctuary, WE, Dungeon, Mission |
| `DA_Overland_HLODLayer_Foliage_Near_Rules` | **unset (None)** | true | `InstancedFoliageActor` + 11 tree SM_* | — | — | HW LI, HM LI, Sanctuary |
| `DA_Overland_HLODLayer_Landscape_Near_Rules` | `LV_Overland_HLODLayer_Landscape_Near` | true | `LandscapeStreamingProxy` | — | — | HW LI, HM LI, Dungeon, Sanctuary |
| `DA_Overland_HLODLayer_Water_Near_Rules` | `LV_Overland_HLODLayer_Water_Near` | true | 5× WaterBody* (`OR`) | — | — | HW LI, HM LI, Dungeon, Sanctuary |
| `DA_Overland_HLODLayer_Road_Near_Rules` | `LV_Overland_HLODLayer_Road_Near` | true | `RoadActor` | — | — | HW LI, HM LI, Dungeon, Sanctuary |
| `DA_HW_HLODLayer_NoneInclude_Rules` | None | true | `LevelInstance` | HW Near | — | `_INT`, `LI_WE`, `LI_DUN`, Dungeon, Mission |
| `DA_HW_HLODLayer_NoneExclude_Rules` | None | **false** | `Actor` | HW Near, HW NoneInclude | — | — |
| `DA_HW_HLODLayer_Near_Rules` | `LV_HW_HLODLayer_Near` | true | `LevelInstance` | — | — | `_INT`, `LI_WE`, `LI_DUN`, Dungeon, Mission |
| `DA_HM_HLODLayer_NoneInclude_Rules` | None | true | `LevelInstance` | HM Near, HM Foliage_Near | — | `_INT`, `_POP`, `LI_WE`, Mission *(+2 m min bounds, CL 1950932)* |
| `DA_HM_HLODLayer_NoneExclude_Rules` | None | **false** | (all) | HM Foliage_Near, HM Near, HM NoneInclude | — | — |
| `DA_HM_HLODLayer_Near_Rules` | `LV_HM_HLODLayer_Near` | true | `LevelInstance` | HM Foliage_Near | — | `Misc`, `_BLK`, `_EXT`, `_INT`, `_POP`, `LI_WE`, Dungeon, Mission |
| `DA_HM_HLODLayer_Foliage_Near_Rules` | **unset (None)** | true | `InstancedFoliageActor` + 11 tree SM_* | — | — | (scoped to HM LI) |

**Tree species matched by the two `Foliage_Near` rules:** `SM_Birch`, `SM_FF_Tree`,
`SM_Hawthorn`, `SM_HM_HeroBeech`, `SM_Juniper_Manicured`, `SM_Larch`, `SM_Oak`,
`SM_Pine`, `SM_ScotsPine`, `SM_Spruce`, `SM_WildCherry`.

## HLOD Layer target assets

| Asset | Class | `LayerType` | Builder | `ParentLayer` |
|-------|-------|-------------|---------|---------------|
| `LV_Overland_HLODLayer_Near` | HLODLayer | Custom | MeshMergeWithAutoInstancing | Overland_Far |
| `LV_Overland_HLODLayer_Far` | HLODLayer | Custom | MeshApproximateWithAutoInstancing | (root) |
| `LV_Overland_HLODLayer_BLK_Far` | HLODLayer | MeshApproximate | MeshApproximate | Overland_Far |
| `LV_Overland_HLODLayer_Foliage_Near` | HLODLayer | Custom | **Dummy** | (none) |
| `LV_Overland_HLODLayer_Foliage_Far` | HLODLayer | Custom | FoliageHLODBuilder (imposter: `DA_Overland_FoliageImposter_Config`) | (none) |
| `LV_Overland_HLODLayer_Landscape_Near` | HLODLayer | MeshMerge | FilteredInstancing/MeshMerge | Landscape_Far2 |
| `LV_Overland_HLODLayer_Landscape_Far2` | HLODLayer | MeshMerge | FilteredInstancing/MeshMerge | (root) |
| `LV_Overland_HLODLayer_Landscape_Far` | **ObjectRedirector** | — | — | → Landscape_Near |
| `LV_Overland_HLODLayer_Road_Near` | HLODLayer | MeshSimplify | MeshSimplify (AreaWeighted normals) | (root) |
| `LV_Overland_HLODLayer_Water_Near` | HLODLayer | MeshApproximate | MeshApproximate/FilteredInstancing | (root) |
| `LV_Overland_HLODLayer_Dummy` | HLODLayer | Custom | **Dummy** | (none) |
| `LV_HM_HLODLayer_Near` | HLODLayer | Custom | Instancing (FilterMinimumExtent) | HM_Mid |
| `LV_HM_HLODLayer_Mid` | HLODLayer | Custom | MeshMergeWithAutoInstancing | HM_Far |
| `LV_HM_HLODLayer_Far` | HLODLayer | Custom | MeshApproximateWithAutoInstancing | (root) |
| `LV_HM_HLODLayer_Foliage_Near` | HLODLayer | Custom | **Dummy** | (none) |
| `LV_HM_HLODLayer_Foliage_Far` | HLODLayer | Custom | FoliageHLODBuilder (imposter: `DA_Overland_FoliageImposter_Config`) | (none) |
| `LV_HW_HLODLayer_Near` | HLODLayer | Custom | Instancing (FilterMinimumExtent) | HW_Mid |
| `LV_HW_HLODLayer_Mid` | HLODLayer | Custom | MeshApproximateWithAutoInstancing | HW_Far |
| `LV_HW_HLODLayer_Far` | HLODLayer | Custom | MeshApproximateWithAutoInstancing | (root) |
| `LV_FarFoliage_HLODLayer_Foliage_Mid` | HLODLayer | Custom | FarFoliageHLODBuilder | FarFoliage_Foliage_Far |
| `LV_FarFoliage_HLODLayer_Foliage_Far` | HLODLayer | Custom | MeshMergeFromSource | (root) |
| `DA_FarFoliage_Config` | FarFoliageImposterConfig | — | — | — |

## Config arrays

Verbatim from `DefaultEditor.ini`, section
`[/Script/WorldBuildingEditor.WorldPartitionRuleSettings]`:

```156:174:D:\Sun\Sundance\Config\DefaultEditor.ini
+HLODLayerRulesForActorSave=/Game/Data/WorldPartition/HLOD/Overland/DA_Overland_HLODLayer_NoneInclude_Rules.DA_Overland_HLODLayer_NoneInclude_Rules
+HLODLayerRulesForActorSave=/Game/Data/WorldPartition/HLOD/Overland/DA_Overland_HLODLayer_NoneExclude_Rules.DA_Overland_HLODLayer_NoneExclude_Rules
+HLODLayerRulesForActorSave=/Game/Data/WorldPartition/HLOD/Overland/DA_Overland_HLODLayer_Near_Rules.DA_Overland_HLODLayer_Near_Rules
+HLODLayerRulesForActorSave=/Game/Data/WorldPartition/HLOD/Overland/DA_Overland_HLODLayer_Foliage_Near_Rules.DA_Overland_HLODLayer_Foliage_Near_Rules
+HLODLayerRulesForActorSave=/Game/Data/WorldPartition/HLOD/Overland/DA_Overland_HLODLayer_Landscape_Near_Rules.DA_Overland_HLODLayer_Landscape_Near_Rules
+HLODLayerRulesForActorSave=/Game/Data/WorldPartition/HLOD/Overland/DA_Overland_HLODLayer_Water_Near_Rules.DA_Overland_HLODLayer_Water_Near_Rules
+HLODLayerRulesForActorSave=/Game/Data/WorldPartition/HLOD/Overland/DA_Overland_HLODLayer_Road_Near_Rules.DA_Overland_HLODLayer_Road_Near_Rules
+HLODLayerRulesForActorSave=/Game/Data/WorldPartition/HLOD/Hogwarts/DA_HW_HLODLayer_NoneInclude_Rules.DA_HW_HLODLayer_NoneInclude_Rules
+HLODLayerRulesForActorSave=/Game/Data/WorldPartition/HLOD/Hogwarts/DA_HW_HLODLayer_NoneExclude_Rules.DA_HW_HLODLayer_NoneExclude_Rules
+HLODLayerRulesForActorSave=/Game/Data/WorldPartition/HLOD/Hogwarts/DA_HW_HLODLayer_Near_Rules.DA_HW_HLODLayer_Near_Rules
+HLODLayerRulesForActorSave=/Game/Data/WorldPartition/HLOD/Hogsmeade/DA_HM_HLODLayer_NoneInclude_Rules.DA_HM_HLODLayer_NoneInclude_Rules
+HLODLayerRulesForActorSave=/Game/Data/WorldPartition/HLOD/Hogsmeade/DA_HM_HLODLayer_NoneExclude_Rules.DA_HM_HLODLayer_NoneExclude_Rules
+HLODLayerRulesForActorSave=/Game/Data/WorldPartition/HLOD/Hogsmeade/DA_HM_HLODLayer_Near_Rules.DA_HM_HLODLayer_Near_Rules
+HLODLayerRulesForActorSave=/Game/Data/WorldPartition/HLOD/Hogsmeade/DA_HM_HLODLayer_Foliage_Near_Rules.DA_HM_HLODLayer_Foliage_Near_Rules
+RuntimeGridRulesForActorSave=/Game/Data/WorldPartition/RuntimeGrid/DA_HogsmeadeGrid_Rules.DA_HogsmeadeGrid_Rules
+RuntimeGridRulesForActorSave=/Game/Data/WorldPartition/RuntimeGrid/DA_HogwartsGrid_Rules.DA_HogwartsGrid_Rules
+RuntimeGridRulesForActorSave=/Game/Data/WorldPartition/RuntimeGrid/DA_HogwartsInteriorGrid_Rules.DA_HogwartsInteriorGrid_Rules
+RuntimeGridRulesForActorSave=/Game/Data/WorldPartition/RuntimeGrid/DA_NoneGrid_Rules.DA_NoneGrid_Rules
+RuntimeGridRulesForStreamingGeneration=/Game/Data/WorldPartition/RuntimeGrid/DA_SmallGrid_Rules.DA_SmallGrid_Rules
```

Force / clear / ignore lists (same section): `ActorTypesIgnoredBy*Rules`,
`ActorTypesToForceExcludeFromHLOD`, `OutlinerPathsToForceExcludeFromHLOD`,
`ActorTypesToClearRuntimeGrid` — see [processing order & priority](ProcessingOrderAndPriority.md)
for the resolved contents, and `DefaultEditor.ini:175–236` for the raw lines.

## Grid ↔ HLOD allowlist (`DefaultPlugins.ini`)

```43:44:D:\Sun\Sundance\Config\DefaultPlugins.ini
+AllowedRuntimeGrids=(RuntimeGrid="MainGrid",AllowedHLODLayers=("/Game/Data/WorldPartition/HLOD/Overland/LV_Overland_HLODLayer_Near.LV_Overland_HLODLayer_Near",None))
+AllowedRuntimeGrids=(RuntimeGrid="FarFoliageGrid",AllowedHLODLayers=("/Game/Data/WorldPartition/HLOD/FarFoliage/LV_FarFoliage_HLODLayer_Foliage_Mid.LV_FarFoliage_HLODLayer_Foliage_Mid"))
```

Grids `SmallGrid`, `HogsmeadeGrid`, `HogwartsGrid` and their allowed HLOD layers are
defined on the `LV_Overland` runtime hash set, not in the `.ini`.

## Notes on provenance & confidence

| Fact category | Source | Confidence |
|---------------|--------|------------|
| Asset class, target grid/layer, matched actor types, outliner substrings, `*RulesToExclude`, `LogicOperator`, `IncludeInHLOD=false` on NoneExclude | Package name/import/export tables | High (read directly) |
| Config array order, force/ignore/clear lists, AllowedRuntimeGrids | `DefaultEditor.ini` / `DefaultPlugins.ini` | High (verbatim) |
| Rule application effects, evaluation model, "Skipped RuntimeGrid override" | Engine source cited in the [reference topics](../README.md) | High (source-cited) |
| Foliage_Near "handled by imposter pipeline" intent | Inferred from unset target + Dummy target layer | Medium (interpretation) |
| Numeric bounds (2 m), grid cell sizes / loading ranges | Changelist history + `ReferenceDocs/` + map hash | Medium (not re-derived from binary) |

---

**In this series:** [Rule engine mechanics](RuleEngineMechanics.md) | [Runtime Grid rules](RuntimeGridRules.md) | [HLOD Layer rules](HLODLayerRules.md) | [HLOD Layer target assets](HLODLayerTargetAssets.md) | [Processing order & priority](ProcessingOrderAndPriority.md) | **Data asset inventory**

Back to the [analysis overview](../WorldPartitionRulesAnalysis.md).
