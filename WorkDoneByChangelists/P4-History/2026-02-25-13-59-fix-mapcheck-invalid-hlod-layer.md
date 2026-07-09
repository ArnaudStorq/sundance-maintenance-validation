Parent: [Perforce changelist history](README.md)

# CL 1738687 — MapChecks: fix "invalid HLOD layer" for several actors

| Field | Value |
|-------|-------|
| Changelist | 1738687 |
| Date | 2026-02-25 13:59 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41838](https://jira/browse/SUNDANCE-41838) |
| Review | Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
Fixed MapCheck "invalid HLOD layer" messages for a handful of actors.

## What was done
Fixed the MapCheck messages *"<actor> has an invalid HLOD layer"* for a few actors.

## Why
These actors referenced HLOD layers that were no longer valid; correcting/clearing the assignment removes the MapCheck warnings.

## Scope & impacted files
- **Total files:** 21 (`edit`)
- **Area:** `//sun/Dev/Sundance/Content/__ExternalActors__/...` (Mounds_Woodland level assemblies, QAR_Mission and Vault_Potion Level Instances) plus `LI_Dun_COG_01_Entrance.umap`.

## Notes
Early entry in the MapCheck HLOD cleanup (predecessor to the 644-warning fix in CL 1904278).
