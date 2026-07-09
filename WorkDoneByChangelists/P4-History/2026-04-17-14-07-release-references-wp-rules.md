Parent: [Perforce changelist history](README.md)

# CL 1837219 — Release kept references while processing World Partition Rules

| Field | Value |
|-------|-------|
| Changelist | 1837219 |
| Date | 2026-04-17 14:07 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-52910](https://jira/browse/SUNDANCE-52910) |
| Review | Philippe St-Jean (WBGMontreal); Pierre-Luc Boulet (WBGMontreal) |
| Tested | Editor |

## Summary
Ensured references held during World Partition rule processing are released afterwards.

## What was done
Made sure the kept references are released while processing World Partition Rules.

## Why
Holding references beyond their needed lifetime kept packages loaded and prevented proper GC, causing memory growth and potential inconsistency during large rule passes. Releasing them keeps memory bounded.

## Scope & impacted files
- **Total files:** 2 (`edit`)
- `//sun/Dev/Sundance/Source/WorldBuildingEditor/WorldPartition/WorldPartitionRuleBuilder.cpp#14`
- `//sun/Dev/Sundance/Source/WorldBuildingEditor/WorldPartition/WorldPartitionRuleBuilder.h#7`

## Notes
Part of the WorldPartitionRuleBuilder hardening series.
