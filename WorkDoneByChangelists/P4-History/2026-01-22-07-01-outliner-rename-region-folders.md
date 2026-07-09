Parent: [Perforce changelist history](README.md)

# CL 1684160 — Outliner: rename Region_* folders and nest under Region

| Field | Value |
|-------|-------|
| Changelist | 1684160 |
| Date | 2026-01-22 07:01 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MAJOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41837](https://jira/browse/SUNDANCE-41837) |
| Review | Corey Kruitbosch (Avalanche); Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
Renamed the "Region *" folders and nested them under a single Region folder.

## What was done
Renamed and moved into the `Region` folder:
- `Region Coast` → `Coast`
- `Region Forbidden Forest` → `Forbidden Forest`
- `Region Hogwarts Valley` → `Hogwarts Valley`
- `Region Mountain` → `Mountain`
- `Region OOB` → `OOB`

## Why
Part of the systematic LV_Overland Outliner restructure — replacing the "Region " prefix with a proper parent `Region` folder.

## Scope & impacted files
- **Total files:** 5 (`edit`)
- **Area:** `//sun/Dev/Sundance/Content/__ExternalObjects__/Levels/Overland/LV_Overland/...`

## Notes
Part of the LV_Overland Outliner restructure series (SUNDANCE-41837).
