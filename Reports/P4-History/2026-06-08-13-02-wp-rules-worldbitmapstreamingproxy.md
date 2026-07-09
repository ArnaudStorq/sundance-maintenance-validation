# CL 1916537 — Update World Partition rules for WorldBitmapStreamingProxy

| Field | Value |
|-------|-------|
| Changelist | 1916537 |
| Date | 2026-06-08 13:02 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41838](https://jira/browse/SUNDANCE-41838) |
| Review | Philippe St-Jean (WBGMontreal) |
| Tested | Editor |

## Summary
Reclassified `WorldBitmapStreamingProxy` in the World Partition rules configuration.

## What was done
Updated the World Partition rules (`DefaultEditor.ini`):
- Removed `WorldBitmapStreamingProxy` from **"Actor Types Ignored by Runtime Grid Rules"**
- Added `WorldBitmapStreamingProxy` to **"Actor Types to Force Exclude from HLOD"**
- Added `WorldBitmapStreamingProxy` to **"Actor Types to Clear Runtime Grid"**

## Why
`WorldBitmapStreamingProxy` actors should not participate in HLOD and should have their runtime grid cleared rather than simply being ignored, ensuring they are handled correctly by the rule pipeline.

## Scope & impacted files
- **Total files:** 1 (`edit`)
- `//sun/Dev/Sundance/Config/DefaultEditor.ini#108`

## Notes
Configuration-only change.
