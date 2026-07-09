Parent: [Perforce changelist history](README.md)

# CL 1896115 — Expose ULevel::FixupActorFolders publicly

| Field | Value |
|-------|-------|
| Changelist | 1896115 |
| Date | 2026-05-26 14:39 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | MTLWKS20850_SunDevEngine (`//sun/Dev-Engine`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-62658](https://jira/browse/SUNDANCE-62658); [SUNDANCE-41837](https://jira/browse/SUNDANCE-41837) |
| Review | Philippe St-Jean (WBGMontreal); Pierre-Luc Boulet (WBGMontreal) |
| Tested | Editor |

## Summary
Engine change to make `ULevel::FixupActorFolders` callable from external commandlets.

## What was done
Changed the access of `ULevel::FixupActorFolders` so external commandlets can call it.

## Why
The new `WorldPartitionFixupActorFoldersBuilder` (CL 1900064) needs to invoke the engine's `FixupActorFolders` logic directly instead of reimplementing it. Exposing the method avoids code duplication and keeps behavior identical to the Editor.

## Scope & impacted files
- **Total files:** 1 (`edit`)
- `//sun/Dev-Engine/Engine/Source/Runtime/Engine/Classes/Engine/Level.h#7`

## Notes
Engine-side prerequisite for the Actor Folder fixup builder. Committed on the `Dev-Engine` branch.
