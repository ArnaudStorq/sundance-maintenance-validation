# CL 1729621 — BUILDFIX: undo Outliner column utils change (1729587)

| Field | Value |
|-------|-------|
| Changelist | 1729621 |
| Date | 2026-02-19 11:54 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@BUILDFIX` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-48603](https://jira/browse/SUNDANCE-48603) |
| Review | Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
Reverted CL 1729587 to fix a broken build.

## What was done
Undid `//sun/Dev/Sundance/Source/WorldBuildingEditor/WorldPartition/...` from changelist **1729587** (including deleting the newly added `WorldPartitionOutlinerColumnUtils` files).

## Why
CL 1729587 broke the build, so it was rolled back immediately as a build fix. The feature was later re-landed correctly in CL 1731394.

## Scope & impacted files
- **Total files:** 6 (`4 integrate`, `2 delete`)
- **Area:** `//sun/Dev/Sundance/Source/WorldBuildingEditor/WorldPartition/...`

## Notes
Build-stabilizing revert.
