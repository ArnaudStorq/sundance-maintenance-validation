Parent: [Perforce changelist history](README.md)

# CL 1959005 — Apply World Partition rules to actors in several Level Instances

| Field | Value |
|-------|-------|
| Changelist | 1959005 |
| Date | 2026-07-06 16:12 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-62658](https://jira/browse/SUNDANCE-62658) |
| Review | Philippe St-Jean (WBGMontreal) — approved |
| Tested | Editor |

## Summary
Applied World Partition rules to the actors contained in a set of Level Instances.

## What was done
Ran the World Partition rule pass over the actors of the following Level Instances:
- `/Game/Levels/Dungeons/COG_01_Dungeon/LI_Dun_COG_01_Entrance`
- `/Game/Levels/Overland/Hamlets/GransHouse/LI_Hamlets_GransHouse_EXT_Rock_A`
- `/Game/Levels/Overland/Hamlets/GransHouse/LI_Hamlets_GransHouse_EXT_Rock_B`
- `/Game/Levels/Overland/Hamlets/GransHouse/LI_Hamlets_GransHouse_EXT_Rock_C`
- `/Game/Environment/Population/Camp/LI_Camp_StorageLarge_E`
- `/Game/Environment/Population/Camp/LI_Camp_WoodenBox_A`
- `/Game/Experimental/Levels/Overland/COG_Mission/LI_COG_Cottage_Blockout`

## Why
These Level Instances were converted to partitioned streaming in CL 1958172 / CL 1957917; this change performs the actual rule assignment (RuntimeGrid / HLOD) on their inner actors.

## Scope & impacted files
- **Total files:** 2270 (`edit`)
- **Area:** `//sun/Dev/Sundance/Content` (external actor packages)

## Notes
Large content-only pass; no source code touched.
