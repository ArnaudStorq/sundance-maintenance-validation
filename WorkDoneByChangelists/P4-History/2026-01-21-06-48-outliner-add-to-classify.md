Parent: [Perforce changelist history](README.md)

# CL 1681994 — Outliner: add TO_CLASSIFY folder and begin moving actors

| Field | Value |
|-------|-------|
| Changelist | 1681994 |
| Date | 2026-01-21 06:48 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MAJOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41837](https://jira/browse/SUNDANCE-41837) |
| Review | Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
Introduced the TO_CLASSIFY triage folder and started moving root actors into it.

## What was done
Added a new `TO_CLASSIFY` folder in `LV_Overland` and started moving actors into it.

## Why
Part of the LV_Overland Outliner restructure — the first step of collecting all loose root-level actors into a single triage folder before categorizing them.

## Scope & impacted files
- **Total files:** 419 (`418 edit`, `1 add`)
- **Area:** `//sun/Dev/Sundance/Content`

## Notes
Kicks off the TO_CLASSIFY batches (CL 1682056, 1682066, 1682070, 1682099).
