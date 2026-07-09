# CL 1890839 — Stop spawning ghost UActorFolder assets during world folders rebuild

| Field | Value |
|-------|-------|
| Changelist | 1890839 |
| Date | 2026-05-22 09:04 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | MTLWKS20850_SunDevEngine (`//sun/Dev-Engine`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-54425](https://jira/browse/SUNDANCE-54425); [SUNDANCE-41837](https://jira/browse/SUNDANCE-41837) |
| Review | Philippe St-Jean (WBGMontreal); Pierre-Luc Boulet (WBGMontreal) — approved (jnelson) |
| Tested | Editor |

## Summary
Engine fix preventing creation of stray `UActorFolder` assets for Level Instance folders when rebuilding world folders.

## What was done
Modified `WorldFolders.cpp` so the world folders rebuild no longer spawns "ghost" `UActorFolder` assets for Level Instance actor folders.

## Why
Rebuilding world folders was creating spurious `UActorFolder` assets tied to Level Instances, polluting the level with orphaned folders (feeding the orphan/duplicate problem addressed elsewhere). Preventing their creation at the source stops the leak.

## Scope & impacted files
- **Total files:** 1 (`edit`)
- `//sun/Dev-Engine/Engine/Source/Editor/UnrealEd/Private/WorldFolders.cpp#4`

## Notes
Engine-side root-cause fix (approved by jnelson). Complements the Actor Folder fixup tooling.
