Parent: [Perforce changelist history](README.md)

# CL 1682124 — Outliner: rename TO_CLASSIFY to #_TO_CLASSIFY

| Field | Value |
|-------|-------|
| Changelist | 1682124 |
| Date | 2026-01-21 08:33 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MAJOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41837](https://jira/browse/SUNDANCE-41837) |
| Review | Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
Prefixed the TO_CLASSIFY folder so it sorts first in the Outliner.

## What was done
Renamed the `TO_CLASSIFY` folder to `#_TO_CLASSIFY` so it appears as the first item in the list.

## Why
The unclassified-actors folder should be at the top of the Outliner where designers will notice and triage it; a `#_` prefix forces it to sort first.

## Scope & impacted files
- **Total files:** 1 (`edit`)
- `//sun/Dev/Sundance/Content/__ExternalObjects__/Levels/Overland/LV_Overland/1/MT/YTTKLKFJSVU9OVB8HK85EA.uasset#2`

## Notes
Part of the LV_Overland Outliner restructure series (SUNDANCE-41837).
