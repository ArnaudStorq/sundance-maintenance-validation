Parent: [Perforce changelist history](README.md)

# CL 1709604 — Outliner: create Environment subfolders and sort static meshes

| Field | Value |
|-------|-------|
| Changelist | 1709604 |
| Date | 2026-02-04 11:40 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MAJOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41837](https://jira/browse/SUNDANCE-41837) — approved |
| Review | Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
Created Environment sub-categories and moved root-level static meshes into them.

## What was done
- Created `Environment/Foliage`, `Environment/Blockout` and `Environment/Rocks`.
- Moved the appropriate root-level static meshes into the matching subfolder.

## Why
Part of the systematic LV_Overland Outliner restructure — organizing the large pool of loose environment static meshes into clear categories.

## Scope & impacted files
- **Total files:** 204 (`201 edit`, `3 add`)
- **Area:** `//sun/Dev/Sundance/Content`

## Notes
Part of the LV_Overland Outliner restructure series (SUNDANCE-41837).
