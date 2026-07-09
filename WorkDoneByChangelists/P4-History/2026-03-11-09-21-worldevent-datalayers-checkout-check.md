Parent: [Perforce changelist history](README.md)

# CL 1758012 — Verify WorldDataLayers is checkout-ready when updating a Possible World Event

| Field | Value |
|-------|-------|
| Changelist | 1758012 |
| Date | 2026-03-11 09:21 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-51436](https://jira/browse/SUNDANCE-51436) |
| Review | Philippe Gourdeau-Bedard (WBGMontreal); Philippe St-Jean (WBGMontreal); Pierre-Luc Boulet (WBGMontreal) — approved |
| Tested | Editor |

## Summary
Added a guard ensuring the WorldDataLayers instance can be checked out and is up to date before updating a Possible World Event.

## What was done
When updating the content of a Possible World Event, the code now checks that the `WorldDataLayers` instance is available for check out and up to date.

## Why
Updating a world event modifies the `WorldDataLayers` instance. If that asset was not checked out or was stale, the operation could fail or corrupt data. The check prevents that.

## Scope & impacted files
- **Total files:** 2 (`edit`)
- `//sun/Dev/Sundance/Source/Sundance/WorldEvents/WorldEventLocator.cpp#39`
- `//sun/Dev/Sundance/Source/Sundance/WorldEvents/WorldEventLocator.h#27`

## Notes
Robustness fix in the World Events system.
