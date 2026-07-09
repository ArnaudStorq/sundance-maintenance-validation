# CL 1686904 — Outliner: rename LI_Hogsmeade folder to Hogsmeade (reverted)

| Field | Value |
|-------|-------|
| Changelist | 1686904 |
| Date | 2026-01-23 07:43 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MAJOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41837](https://jira/browse/SUNDANCE-41837) |
| Review | Corey Kruitbosch (Avalanche); Jaume Bea (ActIIIStudios); Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
First attempt at the Hogsmeade folder rename; reverted after it froze the editor.

## What was done
- Renamed the existing folder `LI_Hogsmeade/...` to `Hogsmeade/...`.
- Moved the `LI_Hogsmeade` root-level actor into `Hogsmeade/`.

## Why
Part of the LV_Overland Outliner restructure. However, this change froze the editor when loading `LV_Overland`.

## Scope & impacted files
- **Total files:** 2 (`edit`)
- **Area:** `//sun/Dev/Sundance/Content/__ExternalActors__` / `__ExternalObjects__` for `LV_Overland`.

## Notes
Reverted by CL 1686967; successfully re-done in CL 1689769 (with Data Layer rule updates).
