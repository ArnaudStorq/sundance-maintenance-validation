Parent: [Perforce changelist history](README.md)

# CL 1715128 — Outliner cleanup: delete 7 empty folders

| Field | Value |
|-------|-------|
| Changelist | 1715128 |
| Date | 2026-02-06 13:18 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41837](https://jira/browse/SUNDANCE-41837) — approved |
| Review | Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
Removed 7 empty Outliner folders.

## What was done
Deleted 7 empty folders: `DormStairs`, `LI_Puddifoots_EXT_StaticMesh`, `shelves`, `STREAM`, `WitchSide`, `WizardSide`, `Archive`.

## Why
Empty folders clutter the Outliner and confuse designers. Removing them is part of the LV_Overland structure cleanup.

## Scope & impacted files
- **Total files:** 7 (`delete`)
- **Area:** `//sun/Dev/Sundance/Content/__ExternalObjects__/Levels/Overland/LV_Overland/...`

## Notes
Part of the LV_Overland Outliner restructure series (SUNDANCE-41837).
