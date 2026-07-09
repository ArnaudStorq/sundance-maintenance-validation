# CL 1920591 — Fix World Partition rules naming (Dungeon / Mission)

| Field | Value |
|-------|-------|
| Changelist | 1920591 |
| Date | 2026-06-10 14:19 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41838](https://jira/browse/SUNDANCE-41838) |
| Review | Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
Corrected the singular/plural naming used by the World Partition rules.

## What was done
Updated the World Partition rules so they now use `"Dungeon"` (not `"Dungeons"`) and `"Mission"` (not `"Missions"`).

## Why
The rules referenced folder/category names that did not match the actual naming convention, so the rules were not matching the intended actors. Aligning the names makes the rules apply correctly.

## Scope & impacted files
- **Total files:** 10 (`edit`) — all HLOD / RuntimeGrid rule data assets under `//sun/Dev/Sundance/Content/Data/WorldPartition/`, including the Overland, Hogsmeade and Hogwarts HLOD rules and `DA_SmallGrid_Rules`.

## Notes
Data-asset naming fix affecting the whole WP rule set.
