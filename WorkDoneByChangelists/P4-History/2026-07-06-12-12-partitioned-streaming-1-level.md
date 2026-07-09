Parent: [Perforce changelist history](README.md)

# CL 1958172 — Add partitioned streaming support to 1 non-partitioned level

| Field | Value |
|-------|-------|
| Changelist | 1958172 |
| Date | 2026-07-06 12:12 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-62658](https://jira/browse/SUNDANCE-62658) |
| Review | Philippe St-Jean (WBGMontreal) — approved |
| Tested | Editor |

## Summary
Converted one non-partitioned level to partitioned streaming to unblock a World Partition rule fix.

## What was done
Added Partitioned Streaming Support to:
- `/Game/Levels/Dungeons/COG_01_Dungeon/LI_Dun_COG_01_Entrance`

## Why
Enables a fix for World Partition rule processing where the owning Level Instance is set to `LV_Overland_HLODLayer_Near` while an actor is being assigned to `SmallGrid` — two mutually exclusive settings. Making the level partitioned lets the rule pass resolve the conflict.

## Scope & impacted files
- **Total files:** 461 (`460 add`, `1 edit`)
- **Area:** `//sun/Dev/Sundance/Content`

## Notes
Part of the SUNDANCE-62658 partitioned-streaming migration.
