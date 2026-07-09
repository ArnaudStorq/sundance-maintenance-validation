# CL 1727387 — Skip non-partitioned Level Instances in WorldPartitionRuleBuilder

| Field | Value |
|-------|-------|
| Changelist | 1727387 |
| Date | 2026-02-18 08:03 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-48603](https://jira/browse/SUNDANCE-48603) |
| Review | Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
The rule builder no longer processes actors inside non-partitioned Level Instances.

## What was done
Non-partitioned Level Instances are now skipped by `WorldPartitionRuleBuilder`.

## Why
The inner actors of a non-partitioned Level Instance inherit their DataLayer, RuntimeGrid and HLOD settings from the parent, so applying per-actor rules to them is both wrong and wasteful. Skipping them keeps the data correct.

## Scope & impacted files
- **Total files:** 2 (`edit`)
- `//sun/Dev/Sundance/Source/WorldBuildingEditor/WorldPartition/WorldPartitionRuleBuilder.cpp#13`
- `//sun/Dev/Sundance/Source/WorldBuildingEditor/WorldPartition/WorldPartitionRuleBuilder.h#6`

## Notes
Conceptually related to the later partitioned-streaming migration (a level must be partitioned before its actors can get rules).
