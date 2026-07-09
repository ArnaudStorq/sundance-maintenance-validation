# CL 1950932 — Force minimum bounds for HLOD NoneInclude in Hogsmeade

| Field | Value |
|-------|-------|
| Changelist | 1950932 |
| Date | 2026-06-30 09:13 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41838](https://jira/browse/SUNDANCE-41838) |
| Review | Philippe St-Jean (WBGMontreal) — approved |
| Tested | Editor |

## Summary
Updated the HLOD NoneInclude rules so tiny meshes are no longer picked up as HLOD candidates in Hogsmeade.

## What was done
Updated `DA_HW_HLODLayer_NoneInclude_Rules` to force the minimum bounds dimension to **2 m** for NoneInclude in Hogsmeade.

## Why
Without a minimum bound, small objects such as `SM_Single_Stone_CobbleWall_E8` were incorrectly treated as HLOD "None Include" candidates. Enforcing a 2 m minimum excludes such tiny meshes from the rule.

## Scope & impacted files
- **Total files:** 1 (`edit`)
- `//sun/Dev/Sundance/Content/Data/WorldPartition/HLOD/Hogsmeade/DA_HM_HLODLayer_NoneInclude_Rules.uasset#9`

## Notes
Data-asset tuning for the HLOD rule system.
