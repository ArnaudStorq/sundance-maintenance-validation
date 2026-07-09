Parent: [Perforce changelist history](README.md)

# CL 1686885 — Outliner: build Landscape folder structure

| Field | Value |
|-------|-------|
| Changelist | 1686885 |
| Date | 2026-01-23 07:26 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MAJOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41837](https://jira/browse/SUNDANCE-41837) |
| Review | Corey Kruitbosch (Avalanche); Jaume Bea (ActIIIStudios); Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
Created a structured Landscape folder hierarchy and moved the relevant actors into it.

## What was done
- Created a new `Landscape` folder.
- Moved/renamed `Landscape_MerlinDungeon_RegionVolumes_Features/...` → `Landscape/MerlinDungeon/RegionVolumes/Features`.
- Moved/renamed `Landscape_MerlinDungeon_WorldBitmap/...` → `Landscape/MerlinDungeon/WorldBitmap`.
- Moved/renamed `Landscape_RegionVolumes_Features/...` → `Landscape/RegionVolumes/Features/...`.
- Moved/renamed `Landscape_RegionVolumes_Tiled/...` → `Landscape/RegionVolumes/Tiled/...`.
- Moved the `Landscape_MerlinDungeon` root-level actor into `Landscape/MerlinDungeon/`.

## Why
Part of the systematic LV_Overland Outliner restructure — converting flat underscore-delimited names into a proper nested folder hierarchy for landscape data.

## Scope & impacted files
- **Total files:** 10 (`6 edit`, `4 add`)
- **Area:** `//sun/Dev/Sundance/Content/__ExternalActors__` / `__ExternalObjects__` for `LV_Overland`.

## Notes
Part of the LV_Overland Outliner restructure series (SUNDANCE-41837).
