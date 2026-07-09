# CL 1682070 — Outliner: move root actors into TO_CLASSIFY (batch 3)

| Field | Value |
|-------|-------|
| Changelist | 1682070 |
| Date | 2026-01-21 07:40 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MAJOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41837](https://jira/browse/SUNDANCE-41837) |
| Review | Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
Continued moving unclassified root-level actors into the TO_CLASSIFY folder.

## What was done
Moved actors that were previously in the root into the `TO_CLASSIFY` folder in `LV_Overland`.

## Why
Part of the LV_Overland Outliner restructure — staging loose root actors into a triage folder. Split across changelists to keep each checkout manageable.

## Scope & impacted files
- **Total files:** 77 (`edit`)
- **Area:** `//sun/Dev/Sundance/Content`

## Notes
One of a series of TO_CLASSIFY batches (CL 1681994, 1682056, 1682066, 1682070, 1682099).
