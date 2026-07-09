Parent: [Perforce changelist history](README.md)

# CL 1709611 — Undo move of WaterBodyExclusionVolumes to Landscape

| Field | Value |
|-------|-------|
| Changelist | 1709611 |
| Date | 2026-02-04 11:50 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41837](https://jira/browse/SUNDANCE-41837) — approved |
| Review | Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
Reverted the WaterBodyExclusionVolumes move done minutes earlier in CL 1709608.

## What was done
Undid "moved WaterBodyExclusionVolumes to Landscape subfolder" — reverted `__ExternalActors__/Levels/Overland/LV_Overland/...` from changelist **1709608**.

## Why
The move in CL 1709608 was reconsidered (WaterBodyExclusionVolumes belong with Water, not Landscape), so it was rolled back.

## Scope & impacted files
- **Total files:** 4 (`integrate` — revert)
- **Area:** `//sun/Dev/Sundance/Content/__ExternalActors__/Levels/Overland/LV_Overland/...`

## Notes
Part of the LV_Overland Outliner restructure series (SUNDANCE-41837).
