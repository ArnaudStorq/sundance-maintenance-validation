Parent: [Perforce changelist history](README.md)

# CL 1668632 — Outliner: delete empty root-level folders (batch 1)

| Field | Value |
|-------|-------|
| Changelist | 1668632 |
| Date | 2026-01-12 08:05 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MAJOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41837](https://jira/browse/SUNDANCE-41837) |
| Review | Corey Kruitbosch (Avalanche); Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
Deleted empty root-level folders in LV_Overland (first large batch).

## What was done
Deleted empty folders at the root level in `LV_Overland`.

## Why
Part of the systematic LV_Overland Outliner restructure — removing empty root folders that cluttered the Outliner.

## Scope & impacted files
- **Total files:** 442 (`delete`)
- **Area:** `//sun/Dev/Sundance/Content`

## Notes
First batch, paired with CL 1668736 the same day.
