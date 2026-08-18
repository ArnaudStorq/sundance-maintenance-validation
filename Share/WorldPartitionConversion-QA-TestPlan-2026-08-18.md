# QA test plan — World Partition batch conversion (650 levels, 15 changelists)

QA guidance for a batch of 15 changelists that converted 650 levels to World Partition;
because ~95 % of them are reusable Level Instances and kits, the testing effort belongs in
the **parent maps that instance them**, not in the converted levels themselves.

| Field | Value |
|-------|-------|
| Date | 2026-08-18 |
| Author | arnaud.storq |
| Branch | `//sun/Dev` |
| Jira | SUNDANCE-69603 (parent: SUNDANCE-62658) |
| Review | Mark Lento (WBGMontreal); Philippe St-Jean (WBGMontreal) |
| Status | All 15 changelists still **pending** at the time of writing |
| Levels converted | **650** |
| Tool used | [World Partition Batch Converter](../ReferenceDocs/CustomTools/WorldPartitionBatchConverter.md) |

## What changed and why it matters for QA

Every changelist is an automated batch run of the World Partition Batch Converter, the
equivalent of the editor's **Add Partitioned Streaming Support**. Conversion does two
things that QA can observe:

1. Each level's actors move into **external actor packages** (OFPA), so the level is
   streamed **per actor** instead of as a single monolithic block.
2. Because the actors now have their own descriptors, the **World Partition rule system**
   can assign them a `RuntimeGrid`, HLOD layer and Data Layers on save
   ([rules reference](../ReferenceDocs/WorldPartitionRules.md)).

The practical consequence: content that used to appear all at once may now stream in
independently. Regressions therefore surface as **missing or late-appearing content**,
**HLOD proxies not matching**, or **collision/navmesh gaps** — not as editor errors.

> **Key reading of the scope.** Only a handful of the 650 levels are playable maps. The
> rest are Level Instances (`LI_*`) and Level Assemblies (`LA_*`) instanced across the
> game. A single converted kit such as `LA_FF_TreeA_Cluster_C` can appear thousands of
> times in `LV_Overland`.

## Scope — dominant area per changelist

| CL | Levels | Dominant area |
|----|--------|---------------|
| 2023319 | 18 | **London / Diagon Alley** — Knockturn Alley, Gringotts, Shops Block A–F, Borgin & Burkes; plus Beast Lab |
| 2024228 | 50 | **Hogwarts** — Quidditch Pitch, Ravenclaw Tower, DADA Tower, Library, Potions; plus Blockout Cavern / Castle |
| 2024229 | 50 | Level Assemblies — Islands, Mounds, Climbing Walls, Flora, POI |
| 2024230 | 50 | Level Assemblies — Trees, Rocks; plus Lighting assets |
| 2024232 | 50 | Lighting assets, Nature Banks, PBR validation scenes |
| 2024234 | 26 | Nature — Forbidden Forest, Caledonian Forest, Beach, Banks |
| 2025332 | 50 | Nature — Forbidden Forest, Heathland, Grassland, MFF |
| 2025333 | 50 | Population props — Chests, Camp, Books, GeoSpheres, Cauldrons, Gravestones |
| 2025335 | 50 | River banks; plus Population props (Papers, Wood, Food) |
| 2025336 | 50 | **Road** — gravel scatter; plus River embankments and stones |
| 2025337 | 50 | **Road** — embankments, stone scatter, road sides |
| 2025339 | 50 | **Cairn dungeon kit** — hallways, large/medium rooms; plus Mirror World DADA, Poacher camps, Breakables |
| 2025340 | 6 | **Cairn dungeon kit** — Medium Room F/G, Small Room A, room dressups |
| 2025672 | 50 | **London / Diagon Alley** — Shop Blocks A–P, Alley Blocks, Streets, Gringotts; plus Cinematics and editor scenes |
| 2025675 | 50 | **Cairn dungeon kit** — small rooms, stairs, meshes; plus Goblin Mine pipes, COG_01 / CSM_01 / CNA_03 dungeons |

## Area rollup

| Levels | Area | Changelists |
|--------|------|-------------|
| 100 | Env kit — Level Assemblies | 2024228, 2024229, 2024230, 2025332 |
| 90 | Env kit — Nature / Foliage | 2024228, 2024232, 2024234, 2025332, 2025333 |
| 86 | Env kit — Population props | 2025333, 2025335 |
| 80 | Env kit — Road | 2025336, 2025337 |
| 53 | Dungeons — Cairn kit | 2025339, 2025340, 2025675 |
| 45 | Env kit — Lighting assets | 2024230, 2024232, 2025332 |
| 44 | London — Diagon Alley | 2023319, 2025672 |
| 29 | Env kit — River | 2025335, 2025336 |
| 19 | Overland — Hogwarts castle | 2024228 |
| 16 | Editor tool scenes | 2025672, 2025675 |
| 15 | Dungeons — Goblin Mine | 2025675 |
| 12 | PBR validation scenes | 2024232 |
| 10 | Gameplay — Breakables, Knowledge Cards, Quiz System | 2025339 |
| 9 | Env kit — Blockout | 2024228 |
| 6 | Overland — other (Poacher camps, Castle Kit) | 2025339, 2025672 |
| 5 | Character lineups | 2025339 |
| 5 | Cinematics | 2025672 |
| 5 | Env kit — Structural | 2025337, 2025339 |
| 4 | London — Beast Lab | 2023319, 2025672 |
| 4 | Dungeons — other (BPR_01, CNA_03, COG_01, CSM_01) | 2025339, 2025675 |
| 4 | Env kit — other (Forageables, Mini Games) | 2024228 |
| 2 | Overland — Hogsmeade (demo props) | 2025672 |
| 2 | Sanctuary | 2025672 |
| 3 | Animation scenes, Data prototypes, misc | 2025332, 2025339, 2025672 |

## Test priorities

### P1 — `LV_Overland`

**Why**: roughly 350 of the 650 converted levels are generic environment kits (Nature,
Level Assemblies, River, Road, Population, Lighting) instanced throughout the open world.
This is by far the largest surface and the only place where a per-actor streaming
regression can be seen at scale.

**What to check**

- Traverse on foot **and** on broom at high speed along rivers, roads and forest edges;
  watch for banks, rocks, tree clusters or gravel scatter appearing late or not at all.
- Compare HLOD proxies at distance against the loaded geometry — a converted kit whose
  actors received a new HLOD layer can produce a proxy that no longer matches.
- Verify collision on river banks, embankments and climbing walls (the Climbing Wall
  assemblies in CL 2024229 are traversal-critical).
- Confirm foliage and hero trees around the Forbidden Forest still read correctly by day
  and by night.

### P2 — London / Diagon Alley

**Why**: 44 levels across CL 2023319 and CL 2025672, covering the shop interiors and
exteriors, the alley blocks, the streets and Gringotts. Note that both the legacy
`LI_Shops_Block_*` naming and the newer `LI_LON_DA_ShopBlock_*` naming were converted.

**What to check**

- Enter and exit every shop that is reachable; interiors are separate levels from
  exteriors and each was converted independently.
- Walk the full length of the main street and Knockturn Alley, checking street population
  (`LI_Main_Street_POP`) and shop-front dressing.
- Gringotts interior and exterior transitions.
- Traversal gyms and the Charing Cross blockout (CL 2023319) still load as expected.

### P3 — Cairn dungeon kit

**Why**: 53 levels across CL 2025339, CL 2025340 and CL 2025675 — hallways, small/medium/
large rooms, stairs, pillars, coffins, statues, broken walls and room dressups. This is a
**procedurally assembled** kit, so a single playthrough exercises only a fraction of it.

**What to check**

- Generate and play **several** different Cairn layouts, not one, so that most room and
  hallway variants are seen at least once.
- Navmesh and AI pathing through hallways and stairs (`LI_Cairn_Stairs_*`).
- Room dressup props (coffins, statues, rock assemblies, broken walls) present and
  correctly placed.
- Two-storey room `LI_CairnLargeRoom_2Story_A` — vertical streaming is the most likely
  place for a per-actor regression.

### P4 — Hogwarts castle

**Why**: 19 levels in CL 2024228.

**What to check**

- Quidditch Pitch, including the blockout, the obstacle kit and the four house tower tarps.
- Ravenclaw Tower interior with the **Winter** common room population
  (`LI_HW_RT_CRB_Population_Winter`).
- DADA Tower (Charms game exterior, DADA3 classroom lighting), Library study tables,
  Potions classroom tables, Architect Chamber.

### P5 — Secondary areas

- **Goblin Mine** — 15 pipe Level Instances (CL 2025675); check collision and navmesh.
- **Dungeons COG_01, CSM_01, CNA_03, BPR_01** — one entrance/main level each.
- **Poacher camps** — tents, tanning rack (CL 2025339).
- **Sanctuary** — bookcase and display case props (CL 2025672).
- **Hogsmeade** — two Teasdale vendor demo props (CL 2025672).
- **Breakables and Knowledge Cards** — Owl Post packages, moonstones, logs, yew trees,
  potion dumping docks (CL 2025339).

### P6 — Non-gameplay scenes (smoke test only)

16 editor tool scenes and 12 PBR validation scenes were included in the batch
(`/Game/Editors/...`, `/Game/Environment/MasterMaterials/Validation/...`, Character 360
backgrounds, Physical Reaction Editor, Scene Rig preview). These are not gameplay content —
just confirm each **opens in the editor without errors**.

## Pass criteria

For every area tested:

1. **No missing content** — everything present before the conversion is still visible.
2. **No streaming pop-in** regression at normal traversal speed, on foot and on broom.
3. **Map Check clean** on the parent map — run **Build → Map Check** and triage with the
   [MapCheck playbook](../ReferenceDocs/FixingMapCheckIssues.md). Watch in particular for
   invalid HLOD layer (A1), invalid runtime grid (A2) and different-runtime-grid reference
   errors, which per-actor conversion can newly expose.
4. **Collision and navmesh intact** — no falling through, no blocked AI paths.
5. **Lighting unchanged** — 45 lighting Level Instances were converted and are instanced
   widely; verify no unlit or double-lit areas.

## Appendix A — London / Diagon Alley levels (44)

CL 2023319:

```
/Game/Levels/London/BeastLab/LI_LabMain_FightNavmeshGen
/Game/Levels/London/BeastLab/LI_LabStructureWLBookCase01
/Game/Levels/London/BeastLab/LI_LabStructureWLBookCase02
/Game/Levels/London/DiagonAlley/LI_KnockturnAlley
/Game/Levels/London/DiagonAlley/LI_KnockturnAlley_TraversalArea
/Game/Levels/London/DiagonAlley/LV_NLC_01_Asset_Gym
/Game/Levels/London/DiagonAlley/LV_NLC_01_CharingCross_Start_Blockout
/Game/Levels/London/DiagonAlley/LV_NLC_01_Traversal_Gym
/Game/Levels/London/DiagonAlley/Shops/Gringotts/LI_Gringotts_EXT
/Game/Levels/London/DiagonAlley/Shops/Gringotts/LI_Gringotts_INT
/Game/Levels/London/DiagonAlley/Shops/Shops_Block_A/LI_Shops_Block_A_EXT
/Game/Levels/London/DiagonAlley/Shops/Shops_Block_C/LI_Shops_Block_C_EXT
/Game/Levels/London/DiagonAlley/Shops/Shops_Block_C/LI_Shops_Block_C_INT
/Game/Levels/London/DiagonAlley/Shops/Shops_Block_D/LI_Shops_Block_D_EXT
/Game/Levels/London/DiagonAlley/Shops/Shops_Block_E/LI_Shops_Block_E_EXT
/Game/Levels/London/DiagonAlley/Shops/Shops_Block_E/LI_Shops_Block_E_INT
/Game/Levels/London/DiagonAlley/Shops/Shops_Block_F/LI_Shops_Block_F_EXT
/Game/Levels/London/TraversalAlley/BorginBurkes/LI_BorginBurkes_Ext
```

CL 2025672:

```
/Game/Levels/London/DiagonAlley/AlleyBlocks/AlleyBlock_A/LI_LON_DA_AlleyBlock_A
/Game/Levels/London/DiagonAlley/AlleyBlocks/AlleyBlock_B/LI_LON_DA_AlleyBlock_B
/Game/Levels/London/DiagonAlley/AlleyBlocks/AlleyBlock_C/LI_LON_DA_AlleyBlock_C
/Game/Levels/London/DiagonAlley/AlleyBlocks/AlleyBlock_D/LI_LON_DA_AlleyBlock_D
/Game/Levels/London/DiagonAlley/AlleyBlocks/AlleyBlock_E/LI_LON_DA_AlleyBlock_E
/Game/Levels/London/DiagonAlley/LI_DiagonAlley
/Game/Levels/London/DiagonAlley/Shops/Gringotts/LI_LON_DA_Gringotts_EXT
/Game/Levels/London/DiagonAlley/Shops/Gringotts/LI_LON_DA_Gringotts_INT
/Game/Levels/London/DiagonAlley/Shops/ShopBlock_A/LI_LON_DA_ShopBlock_A_EXT
/Game/Levels/London/DiagonAlley/Shops/ShopBlock_B/LI_LON_DA_ShopBlock_B_EXT
/Game/Levels/London/DiagonAlley/Shops/ShopBlock_C/LI_LON_DA_ShopBlock_C_EXT
/Game/Levels/London/DiagonAlley/Shops/ShopBlock_C/LI_LON_DA_ShopBlock_C_INT
/Game/Levels/London/DiagonAlley/Shops/ShopBlock_D/LI_LON_DA_ShopBlock_D_EXT
/Game/Levels/London/DiagonAlley/Shops/ShopBlock_D/LI_LON_DA_ShopBlock_D_INT
/Game/Levels/London/DiagonAlley/Shops/ShopBlock_E/LI_LON_DA_ShopBlock_E_EXT
/Game/Levels/London/DiagonAlley/Shops/ShopBlock_E/LI_LON_DA_ShopBlock_E_INT
/Game/Levels/London/DiagonAlley/Shops/ShopBlock_F/LI_LON_DA_ShopBlock_F_EXT
/Game/Levels/London/DiagonAlley/Shops/ShopBlock_F/LI_LON_DA_ShopBlock_F_INT
/Game/Levels/London/DiagonAlley/Shops/ShopBlock_G/LI_LON_DA_ShopBlock_G_EXT
/Game/Levels/London/DiagonAlley/Shops/ShopBlock_H/LI_LON_DA_ShopBlock_H_EXT
/Game/Levels/London/DiagonAlley/Shops/ShopBlock_I/LI_LON_DA_ShopBlock_I_EXT
/Game/Levels/London/DiagonAlley/Shops/ShopBlock_J/LI_LON_DA_ShopBlock_J_EXT
/Game/Levels/London/DiagonAlley/Shops/ShopBlock_K/LI_LON_DA_ShopBlock_K_EXT
/Game/Levels/London/DiagonAlley/Shops/ShopBlock_L/LI_LON_DA_ShopBlock_L_EXT
/Game/Levels/London/DiagonAlley/Shops/ShopBlock_M/LI_LON_DA_ShopBlock_M_EXT
/Game/Levels/London/DiagonAlley/Shops/ShopBlock_N/LI_LON_DA_ShopBlock_N_EXT
/Game/Levels/London/DiagonAlley/Shops/ShopBlock_O/LI_LON_DA_ShopBlock_O_EXT
/Game/Levels/London/DiagonAlley/Shops/ShopBlock_P/LI_LON_DA_ShopBlock_P_EXT
/Game/Levels/London/DiagonAlley/Streets/LI_LON_DA_Street_01
/Game/Levels/London/DiagonAlley/Streets/LI_Main_Street_POP
/Game/Levels/London/Lab/Blockout/Knockturne_Beast_Lab_Layout
```

## Appendix B — Dungeon levels (72)

Cairn kit — CL 2025339:

```
LI_Cairn_Entrance_A
LI_Cairn_Hallway_A .. LI_Cairn_Hallway_M          (13 variants)
LI_Cairn_LargeRoom_B, _C, _D, _E
LI_Cairn_LargeRoom_Pillar_A
LI_Cairn_MediumRoom_A, _B, _C, _D, _E
```

Cairn kit — CL 2025340:

```
LI_Cairn_MediumRoom_F, _G
LI_Cairn_Room_Dressup_A, _B, _C
LI_Cairn_SmallRoom_A
```

Cairn kit — CL 2025675:

```
LI_Cairn_SmallRoom_B, _C, _E, _F, _G, _H, _I
LI_Cairn_Stairs_4m_A, _4m_B, _90DegLeft_3m_A, _90DegRight_2m_A, _100DegLeft_4m_A
LI_CairnLargeRoom_2Story_A
LI_DUN_CSM_03_SmallRoom_A
LI_Cairn_Coffin_A, LI_Cairn_Statue_A, LI_Cairn_Rocks_Assembly_A
LI_Cairn_Wall_Broken_4x4m_A, _4x6m_A, _4x6m_B, _4x6m_C, _4x6m_D, _Pile_A
```

Other dungeons:

```
/Game/Levels/Dungeons/Goblin/Pipes/LI_Mine_Pipe_A .. _O        (15, CL 2025675)
/Game/Levels/Dungeons/BPR_01_Dungeon/LI_DUN_BPR_01_Main_Cavern  (CL 2025339)
/Game/Levels/Dungeons/CNA_03/LI_DUN_CNA_03_Container            (CL 2025675)
/Game/Levels/Dungeons/COG_01_Dungeon/LI_Dun_COG_01_Main         (CL 2025675)
/Game/Levels/Dungeons/CSM_01_Dungeon/LI_DUN_CSM_01_OLEntrance   (CL 2025675)
```

## Appendix C — Hogwarts levels (19, CL 2024228)

```
/Game/Levels/Overland/Hogwarts/ArchitectChamber/LI_ArchitectChamber_REF
/Game/Levels/Overland/Hogwarts/DADATower/LI_CharmsGame_EXT
/Game/Levels/Overland/Hogwarts/DADATower/LI_DADA3_Classroom_LIGHTING
/Game/Levels/Overland/Hogwarts/Library/INT/LI_HW_L_LongStudyTable_A
/Game/Levels/Overland/Hogwarts/PotionsClassroom/INT/LI_HW_PC_Table_A
/Game/Levels/Overland/Hogwarts/QuidditchPitch/Blockout/LI_HW_Quidditch_Pitch_BLK_v1
/Game/Levels/Overland/Hogwarts/QuidditchPitch/Blockout/Obstacle/LI_BLK_QuiddPitch_Obstacle_Kit
/Game/Levels/Overland/Hogwarts/QuidditchPitch/LI_HW_QP_TowerTarpGRY_A
/Game/Levels/Overland/Hogwarts/QuidditchPitch/LI_HW_QP_TowerTarpHUF_A
/Game/Levels/Overland/Hogwarts/QuidditchPitch/LI_HW_QP_TowerTarpRAV_A
/Game/Levels/Overland/Hogwarts/QuidditchPitch/LI_HW_QP_TowerTarpSLY_A
/Game/Levels/Overland/Hogwarts/QuidditchPitch/LI_QuidditchPitch_Blockout
/Game/Levels/Overland/Hogwarts/RavenclawTower/INT/LI_HW_RT_CRB_Population_Winter
/Game/Levels/Overland/Hogwarts/Shared/StaticMesh/Bathrooms/SM_HW_Toilet_Set_A
/Game/Levels/Overland/Hogwarts/Shared/StaticMesh/Bathrooms/SM_HW_Toilet_Set_B
/Game/Levels/Overland/Hogwarts/Shared/StaticMesh/Bathrooms/SM_HW_Toilet_Set_C
/Game/Levels/Overland/Hogwarts/Shared/StaticMesh/Bathrooms/SM_HW_Toilet_Set_D
/Game/Levels/Overland/Hogwarts/Shared/StaticMesh/Population/LI_HW_DisplayCabinet_SortingHat
/Game/Levels/Overland/Hogwarts/Shared/StaticMesh/Population/LI_HW_FrogChoir_Stand
```

## Appendix D — Environment kit families

These are the generic kits behind the P1 `LV_Overland` priority. Counts are converted
levels per family, not instance counts in the world.

| Levels | Family | Changelists |
|--------|--------|-------------|
| 80 | `Road/LevelActors` — gravel, stone scatter, embankments, road sides | 2025336, 2025337 |
| 51 | `Nature/Forbidden_Forest` — tree clusters, terrain mounds, slopes, islands, MFF | 2024234, 2025332 |
| 45 | `LightingAssets/StaticMesh` — chandeliers, lamp posts, wall/table lights | 2024230, 2024232, 2025332 |
| 29 | `LevelAssemblies/Banks` — islands, embankments, ditches | 2024228, 2024229 |
| 28 | `River/LevelActors` — river banks, stones, weeds, stone walls | 2025335, 2025336 |
| 26 | `LevelAssemblies/Trees` — hero trees, stumps, groups, roots, MFF | 2024230, 2025332 |
| 19 | `Nature/Banks` — mossy banks and islands | 2024232, 2024234 |
| 12 | `LevelAssemblies/Rocks` — clusters, insets, population | 2024229, 2024230, 2025332 |
| 12 | `Population/GeoSpheres` — globes, armillary spheres | 2025333 |
| 11 | `LevelAssemblies/Mounds` | 2024229 |
| 11 | `Population/Papers` — wall collages | 2025335 |
| 11 | `Population/Props` — food bags, tribal masks, cash register | 2025335 |
| 9 | `Population/Gravestones` | 2025333, 2025335 |
| 8 | `LevelAssemblies/ClimbingWall` — **traversal-critical** | 2024229 |
| 8 | `Population/Furniture` — benches, shelves, display cases | 2025333 |
| 6 | `Blockout/Cavern` | 2024228 |
| 6 | `LevelAssemblies/Flora` — ferns, hanging moss, grass | 2024229 |
| 6 | `Nature/Heathland` | 2025332 |
| 6 | `Population/HourGlass` | 2025335 |
| 5 | `Population/Bottles_and_Cups` | 2025333 |
| 5 | `Population/Cauldrons` | 2025333 |
| ≤4 | Debris, POI, Foliage/HeroTree, Camp, Wood, Chests, Containers, Structural, Beach, Grassland, Caledonian Forest, Woodland, Forageables, Mini Games, Blockout Castle/Gobmine/London, River palette, Merchandise, Food, Books | various |

## See also

- [World Partition Batch Converter](../ReferenceDocs/CustomTools/WorldPartitionBatchConverter.md) — the tool that produced these changelists
- [Converting levels to World Partition](../ReferenceDocs/ConvertingLevelsToWorldPartition.md) — what conversion changes
- [Fixing MapCheck issues](../ReferenceDocs/FixingMapCheckIssues.md) — triage playbook for the errors this can expose
- [World Partition rules](../ReferenceDocs/WorldPartitionRules.md) — how `RuntimeGrid`, HLOD and Data Layers get assigned after conversion
- [Level Instances & OFPA](../ReferenceDocs/LevelInstancesAndOFPA.md) — external actor packages
