# CL 1961639 — Add partitioned streaming support and apply World Partition rules

| Field | Value |
|-------|-------|
| Changelist | 1961639 |
| Date | 2026-07-08 09:01 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-62658](https://jira/browse/SUNDANCE-62658) |
| Review | Philippe St-Jean (WBGMontreal) — approved |
| Tested | Editor |

## Summary
Enabled partitioned streaming on two previously non-partitioned levels and re-ran World Partition rules on a set of Level Instances.

## What was done
- Added **Partitioned Streaming Support** to 2 non-partitioned levels:
  - `LI_Crate_Poachers_UnicornHorn_B`
  - `LA_Road_Roots_Medium_A01`
- Applied World Partition rules to the actors of the following levels:
  - `LI_Crate_Poachers_DragonClaw`
  - `LI_Crate_Poachers_UnicornHorn_B`
  - `LI_Crate_Poachers_UnicornHorn_A`
  - `LI_Castle_Brath_Annex_A`
  - `LA_Road_Roots_Medium_A01`

## Why
Non-partitioned levels cannot carry per-actor World Partition assignments (RuntimeGrid / HLOD). Converting them to partitioned streaming unblocks the rule pass that assigns actors to the proper grid and resolves the conflicting HLOD/SmallGrid configuration.

## Scope & impacted files
- **Total files:** 330 (`326 edit`, `4 add`)
- **Area:** `//sun/Dev/Sundance/Content` (level `.umap` files plus external actor/object packages)

## Notes
Part of the ongoing SUNDANCE-62658 effort to migrate remaining non-partitioned levels to partitioned streaming.
