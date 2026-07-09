Parent: [Perforce changelist history](README.md)

# CL 1954875 — Add partitioned streaming support to 4 non-partitioned levels

| Field | Value |
|-------|-------|
| Changelist | 1954875 |
| Date | 2026-07-02 11:52 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-62658](https://jira/browse/SUNDANCE-62658) |
| Review | Philippe St-Jean (WBGMontreal) — approved |
| Tested | Editor |

## Summary
Converted four non-partitioned levels to partitioned streaming.

## What was done
Added Partitioned Streaming Support to:
- `/Game/Levels/Overland/Camps/Poacher/Meshes/LI_Poachers_Crate_PuffskeinFur`
- `/Game/Environment/LevelAssemblies/Rocks/Cluster/LA_Rock_Cluster_Pine_Small_A`
- `/Game/Experimental/Levels/Vault/Vault_Resource_Cave_MoonStone_01/LI_Vault_Resource_Cave_Moon_A`
- `/Game/Experimental/Levels/Vault/Vault_Academic_Rune_01/LI_Vault_Academic_Rune_01`

## Why
Enables a fix for World Partition rule processing where the owning Level Instance is set to `LV_Overland_HLODLayer_Near` while an actor is being assigned to `SmallGrid` — two mutually exclusive settings.

## Scope & impacted files
- **Total files:** 21 (`11 add`, `10 edit`)
- **Area:** `//sun/Dev/Sundance/Content` (`__ExternalActors__`, `__ExternalObjects__`, `.umap`)

## Notes
Part of the SUNDANCE-62658 partitioned-streaming migration.
