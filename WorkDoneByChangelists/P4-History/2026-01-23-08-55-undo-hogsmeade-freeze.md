Parent: [Perforce changelist history](README.md)

# CL 1686967 — Undo Hogsmeade changes causing an editor freeze

| Field | Value |
|-------|-------|
| Changelist | 1686967 |
| Date | 2026-01-23 08:55 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MAJOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41837](https://jira/browse/SUNDANCE-41837) |
| Review | Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
Reverted the Hogsmeade folder change (CL 1686904) that froze the editor.

## What was done
Undid `//sun/Dev/Sundance/Content/...` from changelist **1686904**.

## Why
The Hogsmeade-related changes in CL 1686904 caused the editor to freeze when loading `LV_Overland`, so they were reverted. The change was later re-done safely in CL 1689769.

## Scope & impacted files
- **Total files:** 2 (`integrate` — revert)
- **Area:** `//sun/Dev/Sundance/Content/__ExternalActors__` / `__ExternalObjects__` for `LV_Overland`.

## Notes
Part of the LV_Overland Outliner restructure series (SUNDANCE-41837).
