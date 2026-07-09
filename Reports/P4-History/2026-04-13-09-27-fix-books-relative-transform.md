# CL 1827113 — Additional RelativeLocation/RelativeRotation fixes for Books

| Field | Value |
|-------|-------|
| Changelist | 1827113 |
| Date | 2026-04-13 09:27 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-52910](https://jira/browse/SUNDANCE-52910) |
| Review | Philippe St-Jean (WBGMontreal) |

## Summary
Corrected relative transforms for Book actors that had been mangled by the WP rules automation.

## What was done
Additional fixes for `RelativeLocation` and `RelativeRotation` on Book actors.

## Why
The earlier automated World Partition rule pass had altered relative transforms on certain actors. Books were among the remaining assets still showing wrong relative location/rotation; this change repairs them.

## Scope & impacted files
- **Total files:** 20 (`edit`)
- **Area:** `//sun/Dev/Sundance/Content/__ExternalActors__/Environment/Population/Books/LI_HW_Book_Row_I/...`

## Notes
Follow-up to the relative-transform corrections in CL 1804673 / CL 1812627.
