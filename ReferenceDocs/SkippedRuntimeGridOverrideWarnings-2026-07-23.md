Parent: [Fixing MapCheck errors & warnings](FixingMapCheckIssues.md)

# "Skipped RuntimeGrid override" warnings — snapshot 2026-07-23

## Context

This document is a **point-in-time snapshot** of the
`Skipped RuntimeGrid override` warnings captured from an **AVA streaming generation**
run on **July 23, 2026** (log timestamps are from `2026.07.22-17.30`). It complements
[section A3 of the MapCheck playbook](FixingMapCheckIssues.md#a3--skipped-runtimegrid-override-the-conflict-signal),
which explains the cause and the fixes.

Every entry below is the **same root conflict**: the rule `DA_SmallGrid_Rules` wants to
move an actor's `RuntimeGrid` from `None` to `SmallGrid`, but the actor's HLOD layer
`LV_Overland_HLODLayer_Near` is **not allowed on the SmallGrid partition**, so the
mutator refuses the override and leaves the grid untouched.

```
LogAvaStreamingGeneration: Warning: Skipped RuntimeGrid override ('None' -> 'SmallGrid') for actor '<actor>' in level '<level>': rule 'DA_SmallGrid_Rules' cannot use HLOD layer 'LV_Overland_HLODLayer_Near' on that partition
```

**How to fix**: follow
[A3](FixingMapCheckIssues.md#a3--skipped-runtimegrid-override-the-conflict-signal) —
e.g. add the `ExcludeFromRuntimeGridRules` actor tag to keep the actor's current grid,
align the HLOD layer rule, force-exclude from HLOD, or convert the owning level.

This is a snapshot for tracking; it is **not** kept in sync with the project. Re-run the
generation to get a fresh list.

## Summary

- **Total warnings**: 52
- **Distinct levels**: 6
- **Rule**: `DA_SmallGrid_Rules` · **HLOD layer**: `LV_Overland_HLODLayer_Near` ·
  **Override**: `None -> SmallGrid`

| Level | Warnings |
| --- | ---: |
| `/Game/Experimental/Levels/Overland/Ruins/LI_HV_A02_Ruins_Redcaps` | 3 |
| `/Game/Experimental/Levels/Vault/Vault_Resource_Platforming_01/LI_Resource_Horklump_01` | 10 |
| `/Game/Experimental/Levels/Vault/Vault_Resource_Cave_MoonStone_01/LI_Vault_Resource_Cave_Moon_A` | 1 |
| `/Game/Levels/Overland/Ruins/Castle_Saints/LI_Castle_Saints_A` | 7 |
| `/Game/Experimental/Levels/Overland/EnemyLair/LI_EnemyLair_Cusith_A` | 3 |
| `/Game/Experimental/Levels/Vault/Vault_UnderwaterTunnel/LI_Vault_UnderwaterTunnel` | 28 |

## Warnings by level

### `/Game/Experimental/Levels/Overland/Ruins/LI_HV_A02_Ruins_Redcaps` (3)

- `BP_Forageable_Horklump`
- `BP_Forageable_Horklump2`
- `BP_Forageable_Horklump3`

### `/Game/Experimental/Levels/Vault/Vault_Resource_Platforming_01/LI_Resource_Horklump_01` (10)

- `BP_Horklump15`
- `BP_Horklump3`
- `BP_Horklump13`
- `BP_Horklump2`
- `BP_Horklump16`
- `BP_Horklump5`
- `BP_Horklump11`
- `BP_Horklump12`
- `BP_Horklump9`
- `BP_Horklump17`

### `/Game/Experimental/Levels/Vault/Vault_Resource_Cave_MoonStone_01/LI_Vault_Resource_Cave_Moon_A` (1)

- `BP_Loot_Moonstone-Blue-LG_HVA05_H`

### `/Game/Levels/Overland/Ruins/Castle_Saints/LI_Castle_Saints_A` (7)

- `BP_Moonstone_Barrel_MD_A4`
- `BP_Moonstone_Barrel_MD_A5`
- `BP_Moonstone_Barrel_MD_A3`
- `BP_Moonstone_Crate_SM_A`
- `BP_Moonstone_Crate_SM_A3`
- `BP_Moonstone_Barrel_MD_A2`
- `BP_Moonstone_Crate_SM_A2`

### `/Game/Experimental/Levels/Overland/EnemyLair/LI_EnemyLair_Cusith_A` (3)

- `BP_Forageable_Horklump2`
- `BP_Forageable_Horklump3`
- `BP_Forageable_Horklump`

### `/Game/Experimental/Levels/Vault/Vault_UnderwaterTunnel/LI_Vault_UnderwaterTunnel` (28)

- `BP_Lantern_D`
- `SM_InkBottle_Quills_D`
- `SM_Stool_Short_B`
- `BP_BRK_Crate_7`
- `SM_Rolled_Parchment_Pile_D`
- `BP_AMT_Crate_01`
- `SM_HM_OwlPost_Package_G`
- `BP_AMT_OilTorch_01`
- `BP_BRK_Pot_5`
- `SM_HW_Book_JournalOpen_C`
- `BP_AMT_Barrel`
- `BP_AMT_ExplosiveBarrel2`
- `SM_PictureFrame_Trim_1X1_A`
- `BP_Lantern_D3`
- `BP_Light_GEN_Table_Lamp_F`
- `SM_HM_OwlPost_Package_D`
- `BP_Horklump3`
- `SM_PictureFrame_Trim_4X3_G`
- `BP_Horklump2`
- `BP_Horklump`
- `BP_AMT_OilTorch_2`
- `BP_AMT_Rock_01`
- `SM_HM_OwlPost_Package_N`
- `BP_Lantern_D2`
- `BP_BRK_Pot_03`
- `BP_AMT_ExplosiveBarrel`
- `BP_BRK_Crate_13`
- `BP_AMT_Crate_3`

## Manual fix walkthrough

### Warning context

- **Actor**: `BP_Forageable_Horklump`
- **Level**: `LI_HV_A02_Ruins_Redcaps`
- **What happens**: the rule `DA_SmallGrid_Rules` wanted to change the `RuntimeGrid` from
  `None` to `SmallGrid`, but this is refused because the HLOD layer
  `LV_Overland_HLODLayer_Near` is incompatible with that partition. The
  `ExcludeFromRuntimeGridRules` tag prevents the rule system from re-assigning the
  RuntimeGrid, so the actor keeps its current grid.

### Steps

1. **Open the level** containing the actor: in the Content Browser, go to
   `/Game/Experimental/Levels/Overland/Ruins/` and double-click `LI_HV_A02_Ruins_Redcaps`
   to open it.
2. **Select the actor**: in the World Outliner, type `BP_Forageable_Horklump` in the
   search bar, then click it.
3. **Add the tag** in the Details panel:
   - Section **Actor** (expand the **Advanced** properties with the small ⌄ chevron on the
     right of the category if needed).
   - Property **Tags** (`AActor::Tags` array).
   - Click the `+` to add an element.
   - Enter exactly: `ExcludeFromRuntimeGridRules`
4. *(Optional but recommended)* If you want a specific RuntimeGrid rather than `None`: in
   **World Partition → Runtime Grid**, set the desired value **before** saving. The tag
   will lock that value.
5. **Save**: `Ctrl+S`. Since it is an external actor (World Partition), UE will mark the
   actor's file for checkout/add in Perforce — accept it.

### Verification

- Reopen the level and re-run your validation / the AVA process: the
  `Skipped RuntimeGrid override ... for actor 'BP_Forageable_Horklump'` warning must no
  longer appear (the actor is now ignored by the RuntimeGrid rules).
- In the World Outliner, the **WP Rule Exclusion** column must show
  `ExcludeFromRuntimeGridRules` for this actor.

> **Caution**: the tag must be exactly `ExcludeFromRuntimeGridRules` (the default value of
> `ActorTagExcludedFromRuntimeGridRules` in the WorldPartition Rule Settings). If it was
> changed in the project settings, use the configured value instead.

## See also

- [A3 — "Skipped RuntimeGrid override" (the conflict signal)](FixingMapCheckIssues.md#a3--skipped-runtimegrid-override-the-conflict-signal)
- [World Partition Rules (how-to)](WorldPartitionRules.md)
