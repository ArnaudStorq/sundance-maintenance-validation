Parent: [Perforce changelist history](README.md)

# CL 1690531 — Add Outliner columns: OutlinerPath and IncludeInHLOD

| Field | Value |
|-------|-------|
| Changelist | 1690531 |
| Date | 2026-01-27 08:13 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MAJOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41837](https://jira/browse/SUNDANCE-41837) |
| Review | Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
Added two new (default-hidden) Outliner columns.

## What was done
Added two new columns to the Outliner: **OutlinerPath** and **IncludeInHLOD** (both defaulted to invisible).

## Why
The restructure work needs to see each actor's outliner path and its HLOD inclusion state directly in the Outliner. Columns are hidden by default to avoid cluttering the default view.

## Scope & impacted files
- **Total files:** 5 (`1 edit`, `4 add`)
- `//sun/Dev/Sundance/Source/WorldBuildingEditor/WorldBuildingEditorModule.cpp#13`
- `.../WorldPartition/IncludeInHLODColumn.{cpp,h}` (new)
- `.../WorldPartition/OutlinerPathColumn.{cpp,h}` (new)

## Notes
Tooling supporting the Outliner restructure (SUNDANCE-41837).
