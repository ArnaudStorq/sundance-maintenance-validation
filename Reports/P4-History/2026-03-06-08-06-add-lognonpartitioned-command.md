# CL 1751748 — Add Editor.LogNonPartitionedLevelInstances console command

| Field | Value |
|-------|-------|
| Changelist | 1751748 |
| Date | 2026-03-06 08:06 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41837](https://jira/browse/SUNDANCE-41837) |
| Review | Philippe St-Jean (WBGMontreal); Pierre-Luc Boulet (WBGMontreal) |
| Tested | Editor |

## Summary
New console command to list non-partitioned Level Instances.

## What was done
Added a new `Editor.LogNonPartitionedLevelInstances` console command (with supporting function-library helpers).

## Why
Finding which Level Instances are still non-partitioned was a manual, error-prone process. This command enumerates them, which drives the partitioned-streaming migration (SUNDANCE-62658) and Outliner cleanup.

## Scope & impacted files
- **Total files:** 3 (`edit`)
- `//sun/Dev/Sundance/Source/WorldBuildingEditor/WorldBuildingEditorConsoleCommands.cpp#4`
- `//sun/Dev/Sundance/Source/WorldBuildingEditor/WorldPartition/LevelInstance/LevelInstanceFunctionLibrary.cpp#8`
- `//sun/Dev/Sundance/Source/WorldBuildingEditor/WorldPartition/LevelInstance/LevelInstanceFunctionLibrary.h#6`

## Notes
Diagnostic tooling that underpins later migration work.
