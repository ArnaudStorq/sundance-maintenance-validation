# CL 1804673 — Fix relative transforms broken by TeamCity WP rules automation

| Field | Value |
|-------|-------|
| Changelist | 1804673 |
| Date | 2026-03-27 14:28 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-52910](https://jira/browse/SUNDANCE-52910) |
| Review | Mark Lento (WBGMontreal); Philippe St-Jean (WBGMontreal); William Delisle (WBGMontreal) |
| Tested | Editor |

## Summary
Corrected relative locations/rotations of Level Instance maps that were wrongly modified by the automated WorldPartition rules on TeamCity.

## What was done
Fixed relative locations/rotations for Level Instance `.umap` assets that had been incorrectly modified by the `slc-svc-teamcity` WorldPartition rules automation.

## Why
The CI-side WorldPartition rules automation applied incorrect relative transforms to Level Instance maps. This is the first corrective pass restoring the proper values (the underlying builder bug is fixed in CL 1841026 / CL 1857281).

## Scope & impacted files
- **Total files:** 71 (`edit`)
- **Area:** `//sun/Dev/Sundance/Content`

## Notes
Start of the relative-transform recovery series (SUNDANCE-52910).
