# CL 1841026 — Fix WP Rules: make PackagesToSave transient + keep Level Instance references

| Field | Value |
|-------|-------|
| Changelist | 1841026 |
| Date | 2026-04-21 06:18 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-52910](https://jira/browse/SUNDANCE-52910) |
| Review | Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
Fixed the WorldPartition rule processing so it doesn't serialize its working set and keeps references alive during Level Instance processing.

## What was done
- Made `PackagesToSave` a **transient** `UPROPERTY`.
- Kept **references** for Level Instance processing.

## Why
`PackagesToSave` was being treated as a serialized property, which is incorrect for a transient working list. In addition, references needed during Level Instance processing were being garbage-collected/released too early. Both issues caused incorrect rule processing (the failure that led to the revert in CL 1844521).

## Scope & impacted files
- **Total files:** 2 (`edit`)
- `//sun/Dev/Sundance/Source/WorldBuildingEditor/WorldPartition/WorldPartitionRuleBuilder.cpp#15`
- `//sun/Dev/Sundance/Source/WorldBuildingEditor/WorldPartition/WorldPartitionRuleBuilder.h#8`

## Notes
Part of the WorldPartitionRuleBuilder hardening series.
