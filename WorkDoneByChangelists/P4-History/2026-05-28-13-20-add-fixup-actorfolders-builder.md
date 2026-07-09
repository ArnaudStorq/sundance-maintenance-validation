# CL 1900064 — Add UWorldPartitionFixupActorFoldersBuilder

| Field | Value |
|-------|-------|
| Changelist | 1900064 |
| Date | 2026-05-28 13:20 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41837](https://jira/browse/SUNDANCE-41837) |
| Review | Philippe St-Jean (WBGMontreal); Pierre-Luc Boulet (WBGMontreal) |
| Tested | Editor |

## Summary
New World Partition builder to detect and repair orphaned and duplicated Actor Folder assets.

## What was done
Added a new `UWorldPartitionFixupActorFoldersBuilder` that:
- Uses the **Asset Registry** to detect **orphaned** and **duplicated** Actor Folder assets.
- Repairs them via `ULevel::FixupActorFolders` and saves the dirtied packages, matching the behavior an end-user gets in the Editor.
- Provides a report-only mode (`-bReportOnly`) and detailed logging of the top offenders for diagnostics.

## Why
Manually cleaning up orphaned/duplicated Actor Folders across a huge level is impractical. An automated, auditable commandlet makes the fix repeatable and safe.

## Scope & impacted files
- **Total files:** 2 (`add`)
- `//sun/Dev/Sundance/Source/WorldBuildingEditor/WorldPartition/WorldPartitionFixupActorFoldersBuilder.cpp`
- `//sun/Dev/Sundance/Source/WorldBuildingEditor/WorldPartition/WorldPartitionFixupActorFoldersBuilder.h`

## Notes
Consumed later by CL 1901233 to fix `LV_Overland`. Requires the `ULevel::FixupActorFolders` exposure from CL 1896115.
