# CL 1729587 — Show "Non Partitioned Parent" in Outliner WP columns (first attempt)

| Field | Value |
|-------|-------|
| Changelist | 1729587 |
| Date | 2026-02-19 11:28 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-48603](https://jira/browse/SUNDANCE-48603) |
| Review | Philippe St-Jean (WBGMontreal); Pierre-Luc Boulet (WBGMontreal) |
| Tested | Editor |

## Summary
First implementation of the "Non Partitioned Parent" Outliner hint (later reverted for a build break).

## What was done
Added the message **"Non Partitioned Parent"** to the Outliner columns **"DL Rules"**, **"HLOD Layer"**, **"DataLayerRule"** and **"RuntimeGrid"** when the actor belongs to a non-partitioned level instance. Added new `WorldPartitionOutlinerColumnUtils.{cpp,h}`.

## Why
To make WP setting inheritance from a non-partitioned Level Instance parent explicit in the Outliner (see CL 1731394 for the rationale).

## Scope & impacted files
- **Total files:** 6 (`4 edit`, `2 add`)
- **Area:** `//sun/Dev/Sundance/Source/WorldBuildingEditor/WorldPartition/...`

## Notes
Reverted the same day by CL 1729621 (build break); re-landed cleanly in CL 1731394.
