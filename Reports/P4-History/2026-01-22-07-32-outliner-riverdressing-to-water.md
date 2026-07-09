# CL 1684180 — Outliner: consolidate river dressing and references under Water

| Field | Value |
|-------|-------|
| Changelist | 1684180 |
| Date | 2026-01-22 07:32 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MAJOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41837](https://jira/browse/SUNDANCE-41837) |
| Review | Federico Leites (Globant); Philippe St-Jean (WBGMontreal); William Delisle (WBGMontreal) |
| Tested | Editor |

## Summary
Renamed Rivers to RiverDressing and moved water-related folders under Water.

## What was done
- Renamed `Rivers` to `RiverDressing`.
- Moved `RiverDressing` to `Water/`.
- Moved `Reference_WaterBodies` to `Water/`.

## Why
Part of the systematic LV_Overland Outliner restructure — consolidating all water-related content under the `Water` folder with clearer names.

## Scope & impacted files
- **Total files:** 2 (`edit`)
- **Area:** `//sun/Dev/Sundance/Content/__ExternalObjects__/Levels/Overland/LV_Overland/...`

## Notes
Part of the LV_Overland Outliner restructure series (SUNDANCE-41837).
