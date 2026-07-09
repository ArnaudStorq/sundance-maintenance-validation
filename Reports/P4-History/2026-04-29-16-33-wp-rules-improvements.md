# CL 1857281 — World Partition Rules improvements

| Field | Value |
|-------|-------|
| Changelist | 1857281 |
| Date | 2026-04-29 16:33 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-52910](https://jira/browse/SUNDANCE-52910) |
| Review | Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
Several robustness improvements to the World Partition rule builder.

## What was done
- Added support for **Discard OutlinerPath**.
- Made **DiscardCommit** only trigger when no file was actually modified.
- Skip processing for Level Instances with **non-uniform scaling**.

## Why
The rule builder needed to avoid committing empty/no-op changes and to skip cases (non-uniform scaled Level Instances) where transforms cannot be safely recomputed, preventing incorrect relative transforms.

## Scope & impacted files
- **Total files:** 2 (`edit`)
- `//sun/Dev/Sundance/Source/WorldBuildingEditor/WorldPartition/WorldPartitionRuleBuilder.cpp#16`
- `//sun/Dev/Sundance/Source/WorldBuildingEditor/WorldPartition/WorldPartitionRuleBuilder.h#9`

## Notes
Part of the WorldPartitionRuleBuilder hardening series (SUNDANCE-52910).
