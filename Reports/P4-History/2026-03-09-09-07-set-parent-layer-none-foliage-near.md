# CL 1753959 — Set Parent Layer to None on LV_Overland_HLODLayer_Foliage_Near

| Field | Value |
|-------|-------|
| Changelist | 1753959 |
| Date | 2026-03-09 09:07 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41838](https://jira/browse/SUNDANCE-41838) |
| Review | Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
Cleared the Parent Layer on the Foliage Near HLOD layer.

## What was done
Set **Parent Layer** to `None` on `LV_Overland_HLODLayer_Foliage_Near` (the `LV_HM_HLODLayer_Foliage_Near` asset).

## Why
The foliage-near HLOD layer should not chain to a parent layer; setting the parent to None gives the intended HLOD hierarchy behavior.

## Scope & impacted files
- **Total files:** 1 (`edit`)
- `//sun/Dev/Sundance/Content/Data/WorldPartition/HLOD/Hogsmeade/LV_HM_HLODLayer_Foliage_Near.uasset#3`

## Notes
HLOD data-asset configuration.
