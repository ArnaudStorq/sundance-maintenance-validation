Parent: [Perforce changelist history](README.md)

# CL 1731394 — Show "Non Partitioned Parent" in Outliner WP columns

| Field | Value |
|-------|-------|
| Changelist | 1731394 |
| Date | 2026-02-20 05:36 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-48603](https://jira/browse/SUNDANCE-48603) |
| Review | Philippe St-Jean (WBGMontreal); Pierre-Luc Boulet (WBGMontreal) |
| Tested | Editor |

## Summary
Outliner now shows a "Non Partitioned Parent" hint for actors inside non-partitioned Level Instances.

## What was done
Added the message **"Non Partitioned Parent"** to the Outliner columns **"DL Rules"**, **"HLOD Layer"**, **"DataLayerRule"** and **"RuntimeGrid"** when the actor belongs to a non-partitioned level instance. Introduced a shared `WorldPartitionOutlinerColumnUtils` helper.

## Why
Actors inside a non-partitioned Level Instance inherit their WP settings from the parent, so the per-actor columns were misleading (they looked unset). Displaying "Non Partitioned Parent" makes the inheritance explicit to level designers.

## Scope & impacted files
- **Total files:** 7 (`4 integrate`, `1 edit`, `2 add`)
- **Area:** `//sun/Dev/Sundance/Source/WorldBuildingEditor/WorldPartition/...` (DataLayer/HLOD/RuntimeGrid Outliner columns + new `WorldPartitionOutlinerColumnUtils`).

## Notes
Re-lands the functionality first attempted in CL 1729587 (which was reverted by the buildfix CL 1729621).
