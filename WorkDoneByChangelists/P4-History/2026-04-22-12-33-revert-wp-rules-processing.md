Parent: [Perforce changelist history](README.md)

# CL 1844521 — Revert last World Partition Rules processing

| Field | Value |
|-------|-------|
| Changelist | 1844521 |
| Date | 2026-04-22 12:33 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-54425](https://jira/browse/SUNDANCE-54425) |
| Review | Jeremie Pomerleau (WBGMontreal); Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
Reverted a bad World Partition rule processing pass by undoing changelist 1842189.

## What was done
Reverted the last World Partition Rules processing — undid `//sun/Dev/Sundance/Content/__ExternalActors__/...` from changelist **1842189**.

## Why
The previous automated rule pass (CL 1842189) produced incorrect results and had to be rolled back while the underlying rule-builder issues were fixed.

## Scope & impacted files
- **Total files:** 8698 (`integrate` — revert)
- **Area:** `//sun/Dev/Sundance/Content`

## Notes
Large revert; one of the biggest changelists in the range. Motivated the transient-property and reference-handling fixes (CL 1841026, CL 1837219).
