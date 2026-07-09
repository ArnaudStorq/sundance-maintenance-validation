# CL 1704979 — Outliner: delete temp/camera actors and relocate notes to Debug

| Field | Value |
|-------|-------|
| Changelist | 1704979 |
| Date | 2026-02-02 09:32 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MAJOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41837](https://jira/browse/SUNDANCE-41837) |
| Review | Jim Russell (ActIIIStudios); Kalee McCollaum (Avalanche); Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
Removed obsolete temp/camera actors and moved Jim's notes into a Debug subfolder.

## What was done
- Deleted `Cameras_FORDELETE` (approved by Kalee).
- Deleted `AAA_Temp_Cylinders` (approved by Jim).
- Moved `Ava_Notes_JimR` to the `Debug` subfolder (approved by Jim).

## Why
Part of the LV_Overland Outliner restructure — clearing out temporary/obsolete actors after getting owner sign-off.

## Scope & impacted files
- **Total files:** 8 (`7 delete`, `1 edit`)
- **Area:** `//sun/Dev/Sundance/Content/__ExternalActors__` / `__ExternalObjects__` for `LV_Overland`.

## Notes
Part of the LV_Overland Outliner restructure series (SUNDANCE-41837).
