# Test Plan: World Partition Level Conversion Validation

**Assigned to:** Mark Lento
**Jira:** SUNDANCE-69603
**Build:** Latest build including changelists listed below
**Related changelists:** 2011901, 2011902, 2011903, 2011904, 2011905, 2011906, 2011907, 2011909, 2011910, 2011911

## Context

An automated batch conversion (World Partition Batch Converter, equivalent to "Add Partitioned Streaming Support") was run on 92 levels across 10 changelists. This conversion changes how the levels stream, so we need to confirm that nothing shifted, broke, or became unplayable.

## Goal

For every level listed below, validate:

1. **Placement** — All actors, geometry, and sub-levels remain at their correct world position (no offset, no drift, no missing content compared to the pre-conversion state).
2. **Playability** — The level loads, streams correctly, and can be played through without blockers, crashes, or broken navigation.

## General Test Steps (apply to each level)

1. Open the level in the editor and confirm it loads without errors or warnings in the Message Log.
2. Verify World Partition streaming is enabled and the grid loads correctly.
3. Visually compare geometry and actor placement against the previous build / reference (no position, rotation, or scale drift; nothing missing).
4. Launch Play-In-Editor (PIE) and confirm the level is playable:
   - No crashes on load or during play.
   - Streaming cells load/unload correctly while moving through the level.
   - Navmesh / navigation works (no fall-through, no blocked traversal).
   - No visible holes, missing collision, or broken lighting.
5. Log any issue in Jira (SUNDANCE-69603) with the level path, changelist, and a screenshot.

## Pass / Fail Criteria

- **Pass:** Level loads, all content is correctly placed, and the level is fully playable.
- **Fail:** Any misplaced/missing content, streaming failure, crash, or navigation/playability blocker.

## Levels to Test

### Batch 1/10 — CL 2011901
- [ ] `/Game/Levels/London/BeastLab/LI_LabMain_FightNavmeshGen`
- [ ] `/Game/Levels/London/BeastLab/LI_LabStructureWLBookCase01`
- [ ] `/Game/Levels/London/BeastLab/LI_LabStructureWLBookCase02`
- [ ] `/Game/Levels/London/BeastLab/LI_LabWraithLairGeo`
- [ ] `/Game/Levels/London/CartAlley/Buildings/Building_A/LI_LON_CA_BLDG_A`
- [ ] `/Game/Levels/London/CartAlley/Buildings/Building_B/LI_LON_CA_BLDG_B`
- [ ] `/Game/Levels/London/CartAlley/Buildings/Building_C/LI_LON_CA_BLDG_C`
- [ ] `/Game/Levels/London/CartAlley/Buildings/Building_D/LI_LON_CA_BLDG_D`
- [ ] `/Game/Levels/London/CartAlley/Buildings/Building_E/LI_LON_CA_BLDG_E`
- [ ] `/Game/Levels/London/CartAlley/Buildings/Building_F/LI_LON_CA_BLDG_F`

### Batch 2/10 — CL 2011902
- [ ] `/Game/Levels/London/CartAlley/Buildings/Building_G/LI_LON_CA_BLDG_G`
- [ ] `/Game/Levels/London/CartAlley/Ground/LI_LON_CA_GRND_A`
- [ ] `/Game/Levels/London/DiagonAlley/AlleyBlocks/AlleyBlock_A/LI_LON_DA_AlleyBlock_A`
- [ ] `/Game/Levels/London/DiagonAlley/AlleyBlocks/AlleyBlock_B/LI_LON_DA_AlleyBlock_B`
- [ ] `/Game/Levels/London/DiagonAlley/AlleyBlocks/AlleyBlock_C/LI_LON_DA_AlleyBlock_C`
- [ ] `/Game/Levels/London/DiagonAlley/AlleyBlocks/AlleyBlock_D/LI_LON_DA_AlleyBlock_D`
- [ ] `/Game/Levels/London/DiagonAlley/AlleyBlocks/AlleyBlock_E/LI_LON_DA_AlleyBlock_E`
- [ ] `/Game/Levels/London/DiagonAlley/LI_CharingCross`
- [ ] `/Game/Levels/London/DiagonAlley/LI_DiagonAlley`
- [ ] `/Game/Levels/London/DiagonAlley/LI_GringottsFight`

### Batch 3/10 — CL 2011903
- [ ] `/Game/Levels/London/DiagonAlley/LI_KnockturnAlley`
- [ ] `/Game/Levels/London/DiagonAlley/LI_KnockturnAlley_TraversalArea`
- [ ] `/Game/Levels/London/DiagonAlley/LI_LeakyCauldron`
- [ ] `/Game/Levels/London/DiagonAlley/LI_TraversalAlley`
- [ ] `/Game/Levels/London/DiagonAlley/LV_NLC_01_Asset_Gym`
- [ ] `/Game/Levels/London/DiagonAlley/LV_NLC_01_CharingCross_Start_Blockout`
- [ ] `/Game/Levels/London/DiagonAlley/LV_NLC_01_Traversal_Gym`
- [ ] `/Game/Levels/London/DiagonAlley/LV_OwlFlight`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/Gringotts/LI_Gringotts_EXT`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/Gringotts/LI_Gringotts_INT`

### Batch 4/10 — CL 2011904
- [ ] `/Game/Levels/London/DiagonAlley/Shops/Gringotts/LI_LON_DA_Gringotts_EXT`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/Gringotts/LI_LON_DA_Gringotts_INT`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/LeakyCauldron/LI_LON_DA_LeakyCauldron_EXT`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/LeakyCauldron/LI_LON_DA_LexkyCauldron_INT`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/ShopBlock_A/LI_LON_DA_ShopBlock_A_EXT`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/ShopBlock_B/LI_LON_DA_ShopBlock_B_EXT`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/ShopBlock_C/LI_LON_DA_ShopBlock_C_EXT`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/ShopBlock_C/LI_LON_DA_ShopBlock_C_INT`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/ShopBlock_D/LI_LON_DA_ShopBlock_D_EXT`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/ShopBlock_D/LI_LON_DA_ShopBlock_D_INT`

### Batch 5/10 — CL 2011905
- [ ] `/Game/Levels/London/DiagonAlley/Shops/ShopBlock_E/LI_LON_DA_ShopBlock_E_EXT`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/ShopBlock_E/LI_LON_DA_ShopBlock_E_INT`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/ShopBlock_F/LI_LON_DA_ShopBlock_F_EXT`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/ShopBlock_F/LI_LON_DA_ShopBlock_F_INT`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/ShopBlock_G/LI_LON_DA_ShopBlock_G_EXT`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/ShopBlock_H/LI_LON_DA_ShopBlock_H_EXT`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/ShopBlock_I/LI_LON_DA_ShopBlock_I_EXT`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/ShopBlock_J/LI_LON_DA_ShopBlock_J_EXT`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/ShopBlock_K/LI_LON_DA_ShopBlock_K_EXT`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/ShopBlock_L/LI_LON_DA_ShopBlock_L_EXT`

### Batch 6/10 — CL 2011906
- [ ] `/Game/Levels/London/DiagonAlley/Shops/ShopBlock_M/LI_LON_DA_ShopBlock_M_EXT`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/ShopBlock_N/LI_LON_DA_ShopBlock_N_EXT`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/ShopBlock_O/LI_LON_DA_ShopBlock_O_EXT`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/ShopBlock_P/LI_LON_DA_ShopBlock_P_EXT`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/Shops_Block_A/LI_Shops_Block_A_EXT`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/Shops_Block_C/LI_Shops_Block_C_EXT`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/Shops_Block_C/LI_Shops_Block_C_INT`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/Shops_Block_D/LI_Shops_Block_D_EXT`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/Shops_Block_D/LI_Shops_Block_D_INT`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/Shops_Block_E/LI_Shops_Block_E_EXT`

### Batch 7/10 — CL 2011907
- [ ] `/Game/Levels/London/DiagonAlley/Shops/Shops_Block_E/LI_Shops_Block_E_INT`
- [ ] `/Game/Levels/London/DiagonAlley/Shops/Shops_Block_F/LI_Shops_Block_F_EXT`
- [ ] `/Game/Levels/London/DiagonAlley/Streets/LI_LON_DA_Street_01`
- [ ] `/Game/Levels/London/DiagonAlley/Streets/LI_Main_Street_EXT`
- [ ] `/Game/Levels/London/DiagonAlley/Streets/LI_Main_Street_POP`
- [ ] `/Game/Levels/London/KnockturnAlley/Shops/BorginBurkes/LI_LON_KA_BorginBurkes_EXT`
- [ ] `/Game/Levels/London/KnockturnAlley/Shops/BorginBurkes/LI_LON_KA_BorginBurkes_INT`
- [ ] `/Game/Levels/London/Lab/Blockout/Knockturne_Beast_Lab_Layout`
- [ ] `/Game/Levels/London/Muggle/Buildings/Modular/LI_LON_MU_OwlFlight_Block_01`
- [ ] `/Game/Levels/London/Muggle/Buildings/Modular/LI_LON_MU_OwlFlight_Block_02`

### Batch 8/10 — CL 2011909
- [ ] `/Game/Levels/London/Muggle/Buildings/Modular/LI_LON_MU_OwlFlight_Block_03`
- [ ] `/Game/Levels/London/Muggle/Buildings/Modular/LI_LON_MU_OwlFlight_Block_04`
- [ ] `/Game/Levels/London/Muggle/Buildings/Modular/LI_LON_MU_OwlFlight_Block_05`
- [ ] `/Game/Levels/London/TraversalAlley/AlleyBlocks/LI_Traversal_Alley_Block_A`
- [ ] `/Game/Levels/London/TraversalAlley/AlleyBlocks/LI_Traversal_Alley_Block_B`
- [ ] `/Game/Levels/London/TraversalAlley/AlleyBlocks/LI_Traversal_Alley_Block_C`
- [ ] `/Game/Levels/London/TraversalAlley/AlleyBlocks/LI_Traversal_Alley_Block_D`
- [ ] `/Game/Levels/London/TraversalAlley/AlleyBlocks/LI_Traversal_Alley_Block_E`
- [ ] `/Game/Levels/London/TraversalAlley/AlleyBlocks/LI_Traversal_Alley_Block_F`
- [ ] `/Game/Levels/London/TraversalAlley/AlleyBlocks/LI_Traversal_Alley_Block_G`

### Batch 9/10 — CL 2011910
- [ ] `/Game/Levels/London/TraversalAlley/AlleyBlocks/LI_Traversal_Alley_Block_H`
- [ ] `/Game/Levels/London/TraversalAlley/AlleyBlocks/LI_Traversal_Alley_Block_I`
- [ ] `/Game/Levels/London/TraversalAlley/AlleyBlocks/LI_Traversal_Alley_Block_J`
- [ ] `/Game/Levels/London/TraversalAlley/AlleyBlocks/LI_Traversal_Alley_Block_K`
- [ ] `/Game/Levels/London/TraversalAlley/AlleyBlocks/LI_Traversal_Alley_Rooftop_A`
- [ ] `/Game/Levels/London/TraversalAlley/AlleyBlocks/LI_Traversal_Alley_Rooftop_B`
- [ ] `/Game/Levels/London/TraversalAlley/AlleyBlocks/LI_Traversal_Alley_Rooftop_C`
- [ ] `/Game/Levels/London/TraversalAlley/AlleyBlocks/LI_Traversal_Alley_Rooftop_D`
- [ ] `/Game/Levels/London/TraversalAlley/AlleyBlocks/LI_Traversal_Alley_Rooftop_E`
- [ ] `/Game/Levels/London/TraversalAlley/AlleyBlocks/LI_Traversal_Alley_Rooftop_F`

### Batch 10/10 — CL 2011911
- [ ] `/Game/Levels/London/TraversalAlley/BorginBurkes/LI_BorginBurkes_Ext`
- [ ] `/Game/Levels/London/TraversalAlley/BorginBurkes/LI_BorginBurkes_Int`

## Summary

- **Total levels to validate:** 92
- **Sign-off:** All levels must be `Pass` before the build is approved.
