Parent: [Perforce changelist history](README.md)

# CL 1918257 — Remove HLOD layer information from non-partitioned levels

| Field | Value |
|-------|-------|
| Changelist | 1918257 |
| Date | 2026-06-09 09:31 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-62658](https://jira/browse/SUNDANCE-62658) |
| Review | Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
Stripped HLOD layer assignments from actors living in non-partitioned levels.

## What was done
Removed HLOD layer information from non-partitioned levels.

## Why
Non-partitioned levels inherit their streaming/HLOD behavior from the parent; carrying explicit HLOD layer data on their actors is meaningless and was generating MapCheck warnings ("invalid HLOD layer"). Clearing it removes those warnings and keeps the data consistent.

## Scope & impacted files
- **Total files:** 857 (`edit`)
- **Area:** `//sun/Dev/Sundance/Content` (external actor packages)

## Notes
Content-only cleanup pass.
