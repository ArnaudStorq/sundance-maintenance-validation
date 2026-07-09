# CL 1684179 — Outliner: restructure Roads and dressing blockout folders

| Field | Value |
|-------|-------|
| Changelist | 1684179 |
| Date | 2026-01-22 07:31 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MAJOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41837](https://jira/browse/SUNDANCE-41837) |
| Review | Philippe St-Jean (WBGMontreal); William Delisle (WBGMontreal) |
| Tested | Editor |

## Summary
Promoted Roads to the root and reorganized road dressing blockout folders.

## What was done
- Moved `_Render/Roads` to the root.
- Deleted the now-empty `_Render` folder.
- Moved `HV_A04/...` → `Roads/DressingBlockout/HV_A04/...`.
- Moved `HV_B03/...` → `Roads/DressingBlockout/HV_B03/...`.

## Why
Part of the systematic LV_Overland Outliner restructure — surfacing Roads at the top level and grouping road dressing blockouts.

## Scope & impacted files
- **Total files:** 5 (`3 edit`, `1 delete`, `1 add`)
- **Area:** `//sun/Dev/Sundance/Content/__ExternalObjects__/Levels/Overland/LV_Overland/...`

## Notes
Part of the LV_Overland Outliner restructure series (SUNDANCE-41837).
