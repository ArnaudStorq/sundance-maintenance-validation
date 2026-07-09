Parent: [Perforce changelist history](README.md)

# CL 1946247 — Add partitioned streaming support to 88 non-partitioned levels

| Field | Value |
|-------|-------|
| Changelist | 1946247 |
| Date | 2026-06-26 15:57 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-62658](https://jira/browse/SUNDANCE-62658) |
| Review | Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
Large batch conversion of 88 non-partitioned levels to partitioned streaming.

## What was done
Added Partitioned Streaming Support to **88 non-partitioned levels**, spanning Level Assemblies (Rocks, Trees, Debris), Population/Camp Level Instances, Road scatter meshes, Poacher camp meshes, CastleKit meshes, Ruins, and several Experimental/Vault levels. (Full list captured in the changelist description.)

## Why
This unblocks a later fix for World Partition rule processing, where the owning Level Instance is set to `LV_Overland_HLODLayer_Near` while an actor is being assigned to `SmallGrid` — two mutually exclusive settings. Converting these levels to partitioned streaming allows per-actor rule assignment.

## Scope & impacted files
- **Total files:** 1408 (`871 add`, `537 edit`)
- **Area:** `//sun/Dev/Sundance/Content`

## Notes
One of the largest single conversion batches in the SUNDANCE-62658 effort.
