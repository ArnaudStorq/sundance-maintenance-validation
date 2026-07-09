# CL 1869530 — Fix crash on "Update Redirector References"

| Field | Value |
|-------|-------|
| Changelist | 1869530 |
| Date | 2026-05-07 07:14 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-58039](https://jira/browse/SUNDANCE-58039) |
| Review | Philippe St-Jean (WBGMontreal); Todd Blackburn (Avalanche) — approved |
| Tested | Editor |

## Summary
Fixed a crash triggered by "Update Redirector References" when actors are loaded outside the main Editor world.

## What was done
Fixed the crash occurring on **"Update Redirector References"** when actors get loaded outside the main Editor World.

## Why
`FAssetFixUpRedirectors` internally relies on `LoadPackage`, which — when no world is specified — uses a separate world of type `EWorldType::Inactive` in `UWorld::PostLoad`. The code did not account for this inactive world, leading to a crash. The fix handles that case.

## Scope & impacted files
- **Total files:** 2 (`edit`)
- `//sun/Dev/Sundance/Plugins/Systems/AutoDbAuthoring/Source/AutoDbAuthoringEditor/Private/AutoDbAuthoringSubsystem.cpp#15`
- `//sun/Dev/Sundance/Plugins/Systems/AutoDbAuthoring/Source/AutoDbAuthoringEditor/Private/AutoDbAuthoringSubsystem.h#11`

## Notes
Crash fix in the AutoDbAuthoring plugin.
