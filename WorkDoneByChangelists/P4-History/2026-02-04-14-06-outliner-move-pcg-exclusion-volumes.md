Parent: [Perforce changelist history](README.md)

# CL 1710528 — Outliner: move PCG cliff exclusion volumes to PCG/ExclusionVolumes

| Field | Value |
|-------|-------|
| Changelist | 1710528 |
| Date | 2026-02-04 14:06 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41837](https://jira/browse/SUNDANCE-41837) — approved |
| Review | David Foss (ActIIIStudios); Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
Moved `BP_PCGCliffExclusionVolume` actors into a new `PCG/ExclusionVolumes` folder.

## What was done
Moved the root-level `BP_PCGCliffExclusionVolume` actors into a new folder `PCG/ExclusionVolumes`.

## Why
Part of the systematic LV_Overland Outliner restructure — grouping PCG-related exclusion volumes.

## Scope & impacted files
- **Total files:** 12 (`11 edit`, `1 add`)
- **Area:** `//sun/Dev/Sundance/Content/__ExternalActors__` / `__ExternalObjects__` for `LV_Overland`.

## Notes
Part of the LV_Overland Outliner restructure series (SUNDANCE-41837).
