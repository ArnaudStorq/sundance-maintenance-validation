Parent: [Perforce changelist history](README.md)

# CL 1820555 — Fix editor startup warning for bTriggerEventOnCameraDistanceToPlayer

| Field | Value |
|-------|-------|
| Changelist | 1820555 |
| Date | 2026-04-08 07:24 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-56129](https://jira/browse/SUNDANCE-56129) |
| Review | Pierre-Luc Boulet (WBGMontreal) |
| Tested | Editor |

## Summary
Resolved a Python name-collision warning between two members of `WorldEventActorComponent`.

## What was done
Fixed the editor startup warning:

```
LogPython: Warning: 'WorldEventActorComponent.bTriggerEventOnCameraDistanceToPlayer' and
'WorldEventActorComponent.TriggerEventOnCameraDistanceToPlayer' have the same name
(trigger_event_on_camera_distance_to_player) when exposed to Python.
```

by disambiguating the exposed Python name (via `ScriptName` meta-data).

## Why
Two members mapped to the same generated Python name, which produced a warning at every editor startup. Renaming one of the exposures via meta-data removes the clash.

Ref: Slack thread `p1775247802545249`.

## Scope & impacted files
- **Total files:** 1 (`edit`)
- `//sun/Dev/Sundance/Source/Sundance/WorldEvents/WorldEventActorComponent.h#11`

## Notes
Startup log cleanup.
