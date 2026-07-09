# CL 1957917 — Add partitioned streaming support to 6 non-partitioned levels

| Field | Value |
|-------|-------|
| Changelist | 1957917 |
| Date | 2026-07-06 09:52 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-62658](https://jira/browse/SUNDANCE-62658) |
| Review | Philippe St-Jean (WBGMontreal) — approved |
| Tested | Editor |

## Summary
Converted six non-partitioned levels to partitioned streaming.

## What was done
Added Partitioned Streaming Support to:
- `/Game/Levels/Overland/Hamlets/GransHouse/LI_Hamlets_GransHouse_EXT_Rock_A`
- `/Game/Levels/Overland/Hamlets/GransHouse/LI_Hamlets_GransHouse_EXT_Rock_B`
- `/Game/Levels/Overland/Hamlets/GransHouse/LI_Hamlets_GransHouse_EXT_Rock_C`
- `/Game/Environment/Population/Camp/LI_Camp_StorageLarge_E`
- `/Game/Environment/Population/Camp/LI_Camp_WoodenBox_A`
- `/Game/Experimental/Levels/Overland/COG_Mission/LI_COG_Cottage_Blockout`

## Why
Enables a fix for World Partition rule processing where the owning Level Instance is set to `LV_Overland_HLODLayer_Near` while an actor is being assigned to `SmallGrid` — two mutually exclusive settings.

## Scope & impacted files
- **Total files:** 60 (`52 add`, `8 edit`)
- **Area:** `//sun/Dev/Sundance/Content`

## Notes
The rule assignment for these levels was done in CL 1959005.
