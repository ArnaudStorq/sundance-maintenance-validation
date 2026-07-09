# CL 1960226 — Remove DA_SmallGrid_Rules from "Runtime Grid Rules for Actor Save"

| Field | Value |
|-------|-------|
| Changelist | 1960226 |
| Date | 2026-07-07 12:03 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-62658](https://jira/browse/SUNDANCE-62658) |
| Review | Philippe St-Jean (WBGMontreal) — approved |
| Tested | Editor |

## Summary
Removed the `DA_SmallGrid_Rules` entry from the "Runtime Grid Rules for Actor Save" configuration.

## What was done
Edited `DefaultEditor.ini` to drop `DA_SmallGrid_Rules` from the list of Runtime Grid Rules applied on actor save.

## Why
This reverts / walks back the SmallGrid rule that had been added in CL 1959020. After validating the actor pass, keeping SmallGrid in the automatic on-save rules produced unwanted grid reassignments, so it was removed from the save-time rule set.

## Scope & impacted files
- **Total files:** 1 (`integrate`)
- `//sun/Dev/Sundance/Config/DefaultEditor.ini#111`

## Notes
Configuration-only change; pairs with the earlier addition in CL 1959020.
