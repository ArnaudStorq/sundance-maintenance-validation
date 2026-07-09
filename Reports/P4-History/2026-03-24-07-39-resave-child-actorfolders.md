# CL 1770358 — Resave child ActorFolders

| Field | Value |
|-------|-------|
| Changelist | 1770358 |
| Date | 2026-03-24 07:39 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-53209](https://jira/browse/SUNDANCE-53209) |
| Review | Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
Force-resaved 699 child ActorFolder packages left dirty after earlier parent-folder renames.

## What was done
Resaved child `ActorFolder` external objects (699 of them).

## Why
Parent folders were renamed/moved in earlier CLs (Jan–Feb 2026, "LV_Overland Outliner structure"), but their child `ActorFolder` packages were not resaved at the time. As a result they appeared dirty on every editor session. Force-resaving them stops the unwanted checkouts.

## Scope & impacted files
- **Total files:** 699 (`edit`)
- **Area:** `//sun/Dev/Sundance/Content`

## Notes
Closes the loop on the Outliner restructure series.
