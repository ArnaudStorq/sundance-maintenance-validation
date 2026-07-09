Parent: [Perforce changelist history](README.md)

# CL 1689769 — Outliner: rename LI_Hogsmeade folder to Hogsmeade and update Data Layer rules

| Field | Value |
|-------|-------|
| Changelist | 1689769 |
| Date | 2026-01-26 12:36 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MAJOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41837](https://jira/browse/SUNDANCE-41837) |
| Review | Corey Kruitbosch (Avalanche); Jaume Bea (ActIIIStudios); Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
Renamed the Hogsmeade folder and relocated its root actor, updating Data Layer rules to match.

## What was done
- Renamed the existing folder `LI_Hogsmeade/...` to `Hogsmeade/...`.
- Moved the `LI_Hogsmeade` root-level actor into `Hogsmeade/`.
- Updated Data Layer rules to match the new structure.

## Why
Part of the systematic LV_Overland Outliner restructure — normalizing folder naming (dropping the `LI_` prefix) and keeping the Data Layer rules in sync with the new paths.

## Scope & impacted files
- **Total files:** 14 (`edit`)
- Includes `__ExternalActors__`/`__ExternalObjects__` for `LV_Overland` plus multiple `Data/WorldPartition/HLOD` and `RuntimeGrid` rule assets.

## Notes
This is the successful version; an earlier equivalent attempt (CL 1686904) had caused an editor freeze and was reverted (CL 1686967).
