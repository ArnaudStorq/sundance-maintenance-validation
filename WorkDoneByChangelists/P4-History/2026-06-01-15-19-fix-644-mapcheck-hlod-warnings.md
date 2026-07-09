# CL 1904278 — Fix 644 MapCheck "invalid HLOD layer" warnings

| Field | Value |
|-------|-------|
| Changelist | 1904278 |
| Date | 2026-06-01 15:19 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41838](https://jira/browse/SUNDANCE-41838) |
| Review | Philippe St-Jean (WBGMontreal); Pierre-Luc Boulet (WBGMontreal) |
| Tested | Editor |

## Summary
Cleared 644 MapCheck warnings about invalid HLOD layers in `LI_HM_Rocks_EXT`.

## What was done
Fixed 644 MapCheck warnings of the form *"<actor> has an invalid HLOD layer <layer>"* in `LI_HM_Rocks_EXT.umap`.

## Why
These actors referenced HLOD layers that were no longer valid, producing hundreds of MapCheck warnings that cluttered validation. Reassigning/clearing the HLOD layer resolves them.

## Scope & impacted files
- **Total files:** 1 (`edit`)
- `//sun/Dev/Sundance/Content/Levels/Overland/Hogsmeade/Streets/LI_HM_Rocks_EXT.umap#30`

## Notes
Directly related to the MapCheck cleanup tracked under SUNDANCE-41838.
