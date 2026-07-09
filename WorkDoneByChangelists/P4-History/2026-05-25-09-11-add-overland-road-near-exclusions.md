# CL 1893933 — Add Overland_Road_Near to HLOD exclusion rules

| Field | Value |
|-------|-------|
| Changelist | 1893933 |
| Date | 2026-05-25 09:11 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-62658](https://jira/browse/SUNDANCE-62658) |
| Review | Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
Extended the Overland HLOD None-Include / None-Exclude rules to cover `Overland_Road_Near`.

## What was done
Added `Overland_Road_Near` to the existing exclusion rules in `Overland_NoneInclude` and `Overland_NoneExclude`.

## Why
Road-near HLOD content needed the same include/exclude treatment as the other Overland HLOD layers so that road actors are handled consistently by the HLOD build.

## Scope & impacted files
- **Total files:** 2 (`edit`)
- `//sun/Dev/Sundance/Content/Data/WorldPartition/HLOD/Overland/DA_Overland_HLODLayer_NoneExclude_Rules.uasset#9`
- `//sun/Dev/Sundance/Content/Data/WorldPartition/HLOD/Overland/DA_Overland_HLODLayer_NoneInclude_Rules.uasset#13`

## Notes
Data-asset rule tuning.
