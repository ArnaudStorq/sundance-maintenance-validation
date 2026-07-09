Parent: [Perforce changelist history](README.md)

# CL 1812627 — Fix RelativeLocation/RelativeRotation for more Level .umap assets

| Field | Value |
|-------|-------|
| Changelist | 1812627 |
| Date | 2026-04-02 09:49 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-52910](https://jira/browse/SUNDANCE-52910) |
| Review | Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
Repaired relative transforms on additional Level `.umap` assets.

## What was done
Fixed `RelativeLocation` / `RelativeRotation` for a few more Level `.umap` assets.

## Why
Continuation of the cleanup after the WorldPartition rules automation altered relative transforms; this pass covers additional level maps that were still affected.

## Scope & impacted files
- **Total files:** 244 (`edit`)
- **Area:** `//sun/Dev/Sundance/Content`

## Notes
Follow-up to CL 1804673.
