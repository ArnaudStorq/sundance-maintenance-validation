# CL 1949614 — Add partitioned streaming support to 6 non-partitioned levels

| Field | Value |
|-------|-------|
| Changelist | 1949614 |
| Date | 2026-06-29 15:10 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-62658](https://jira/browse/SUNDANCE-62658) |
| Review | Philippe St-Jean (WBGMontreal) — approved |
| Tested | Editor |

## Summary
Converted six more non-partitioned levels to partitioned streaming.

## What was done
Added Partitioned Streaming Support to:
- `/Game/Levels/Overland/Hogwarts/QuidditchPitch/LI_HW_QP_Entrance_A`
- `/Game/Levels/Overland/Ruins/Castle_Saints/LI_Castle_Brath_Walls_B`
- `/Game/Experimental/Levels/Overland/COG_Mission/LI_COG_Manor_Blockout`
- `/Game/Environment/Population/Camp/LI_Camp_Storage_G`
- `/Game/Environment/Population/Camp/LI_Camp_Storage_B`
- `/Game/Environment/Population/Camp/LI_Camp_Furnace_A`

## Why
Enables a fix for World Partition rule processing where the owning Level Instance is set to `LV_Overland_HLODLayer_Near` while an actor is being assigned to `SmallGrid` — two mutually exclusive settings.

## Scope & impacted files
- **Total files:** 290 (`81 add`, `209 edit`)
- **Area:** `//sun/Dev/Sundance/Content`

## Notes
Part of the SUNDANCE-62658 partitioned-streaming migration.
