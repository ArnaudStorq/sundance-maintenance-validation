# CL 1714561 — Outliner cleanup: delete 156 empty folders

| Field | Value |
|-------|-------|
| Changelist | 1714561 |
| Date | 2026-02-06 10:02 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41837](https://jira/browse/SUNDANCE-41837) — approved |
| Review | Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
Bulk removal of 156 empty Outliner folders across `LV_Overland`.

## What was done
Deleted 156 empty folders spanning many areas (Hogwarts Valley regions, Magical Creatures, LevelInstances, Lighting, Render, Astronomy Tower, etc.). Full list captured in the changelist description.

## Why
The Outliner had accumulated a very large number of empty folders over years of production, making navigation painful. Removing them is a major step in the structure cleanup.

## Scope & impacted files
- **Total files:** 156 (`delete`)
- **Area:** `//sun/Dev/Sundance/Content`

## Notes
The single largest folder-deletion pass in the Outliner restructure series (SUNDANCE-41837).
