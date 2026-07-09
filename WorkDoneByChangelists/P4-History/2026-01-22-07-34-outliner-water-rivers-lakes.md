Parent: [Perforce changelist history](README.md)

# CL 1684185 — Outliner: create Water/Rivers and Water/Lakes and sort water bodies

| Field | Value |
|-------|-------|
| Changelist | 1684185 |
| Date | 2026-01-22 07:34 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MAJOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41837](https://jira/browse/SUNDANCE-41837) |
| Review | William Delisle (WBGMontreal) |
| Tested | Editor |

## Summary
Split water bodies into Water/Rivers and Water/Lakes folders.

## What was done
- Created `Water/Rivers` and `Water/Lakes`.
- Moved `WaterBodyLake` / `WaterBodyRiver` actors into their respective folders.

## Why
Part of the systematic LV_Overland Outliner restructure — separating rivers and lakes for clarity.

## Scope & impacted files
- **Total files:** 22 (`20 edit`, `2 add`)
- **Area:** `//sun/Dev/Sundance/Content/__ExternalActors__` / `__ExternalObjects__` for `LV_Overland`.

## Notes
Part of the LV_Overland Outliner restructure series (SUNDANCE-41837).
