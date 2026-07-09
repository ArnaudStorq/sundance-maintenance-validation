# CL 1707391 — Add Outliner.ExportAllHierarchy console command + commandlet

| Field | Value |
|-------|-------|
| Changelist | 1707391 |
| Date | 2026-02-03 07:43 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MAJOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41837](https://jira/browse/SUNDANCE-41837) — approved |
| Review | Philippe St-Jean (WBGMontreal); Pierre-Luc Boulet (WBGMontreal) |
| Tested | Editor |

## Summary
New tooling to export the full Outliner hierarchy (console command + commandlet + web report).

## What was done
Added an `Outliner.ExportAllHierarchy` console command plus a dedicated commandlet in `EditorToolExtensions` (Editor-only), including CSV export and an HTML report (`OutlinerReport.html`). Introduced a new `OutlinerExtensions` module.

## Why
Auditing and planning the Outliner restructure required a way to dump the complete folder/actor hierarchy. This tool exports it to CSV/HTML so the structure can be reviewed offline.

## Scope & impacted files
- **Total files:** 11 (`2 edit`, `9 add`)
- **Area:** `//sun/Dev/Sundance/Plugins/EditorToolExtensions/Source/OutlinerExtensions/...` plus one edit in `WorldPartitionOutlinerPathRegistry.h`.

## Notes
Enabling tooling for the whole Outliner restructure effort (SUNDANCE-41837).
