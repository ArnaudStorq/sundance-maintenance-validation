# CL 1959722 — Apply World Partition rules to 404 actors (SmallGrid)

| Field | Value |
|-------|-------|
| Changelist | 1959722 |
| Date | 2026-07-07 06:46 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-62658](https://jira/browse/SUNDANCE-62658) |
| Review | Philippe St-Jean (WBGMontreal) — approved |
| Tested | Editor |

## Summary
Ran the World Partition rule pass over 404 actors, assigning them to the SmallGrid and clearing an HLOD-related warning.

## What was done
Applied World Partition rules to 404 actors, assigning them to the **SmallGrid** runtime grid and resolving an HLOD-related warning that was raised for those actors.

## Why
These actors needed to stream on the SmallGrid; the rule pass also fixed an HLOD layer mismatch that was surfacing as a MapCheck/log warning.

## Scope & impacted files
- **Total files:** 404 (`edit`)
- **Area:** `//sun/Dev/Sundance/Content` (external actor packages)

## Notes
Follows the SmallGrid rule addition in CL 1959020.
