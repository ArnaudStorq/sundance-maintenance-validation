Parent: [Perforce changelist history](README.md)

# CL 1959020 — Add DA_SmallGrid_Rules to "Runtime Grid Rules for Actor Save"

| Field | Value |
|-------|-------|
| Changelist | 1959020 |
| Date | 2026-07-06 16:14 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-62658](https://jira/browse/SUNDANCE-62658) |
| Review | Philippe St-Jean (WBGMontreal) — approved |
| Tested | Editor |

## Summary
Added `DA_SmallGrid_Rules` to the "Runtime Grid Rules for Actor Save" configuration.

## What was done
Edited `DefaultEditor.ini` to register `DA_SmallGrid_Rules` in the Runtime Grid Rules that are evaluated when actors are saved.

## Why
Needed so that the following actor pass (CL 1959722) could automatically assign eligible actors to the SmallGrid on save.

## Scope & impacted files
- **Total files:** 1 (`edit`)
- `//sun/Dev/Sundance/Config/DefaultEditor.ini#110`

## Notes
Later reverted in CL 1960226 once the one-off actor pass was complete.
