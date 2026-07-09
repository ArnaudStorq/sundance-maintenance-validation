Parent: [Perforce changelist history](README.md)

# CL 1822824 — Resave many Actor Folders (Outliner)

| Field | Value |
|-------|-------|
| Changelist | 1822824 |
| Date | 2026-04-09 11:21 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41837](https://jira/browse/SUNDANCE-41837) |
| Review | Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
Force-resaved a large set of Actor Folder assets to stabilize the Outliner.

## What was done
Resaved many Actor Folders (Outliner).

## Why
Actor Folder packages that had drifted out of date were dirtying on every editor session. Resaving them brings them to the current format so they stop triggering unwanted checkouts.

## Scope & impacted files
- **Total files:** 2163 (`edit`)
- **Area:** `//sun/Dev/Sundance/Content`

## Notes
Part of the Outliner / Actor Folder maintenance effort (see also CL 1770358).
