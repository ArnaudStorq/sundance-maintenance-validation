# CL 1661126 — Improve robustness of RoadSplineComponent::GetRoadJunctions

| Field | Value |
|-------|-------|
| Changelist | 1661126 |
| Date | 2026-01-06 07:03 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-42530](https://jira/browse/SUNDANCE-42530) |
| Review | Philippe St-Jean (WBGMontreal); Pierre-Luc Boulet (WBGMontreal) |
| Tested | Editor |

## Summary
Hardened `RoadSplineComponent::GetRoadJunctions` against invalid input/state.

## What was done
Improved robustness of `RoadSplineComponent::GetRoadJunctions`.

## Why
The method could misbehave on edge-case road spline data; adding robustness prevents errors when querying road junctions.

## Scope & impacted files
- **Total files:** 1 (`edit`)
- `//sun/Dev/Sundance/Plugins/Roads/Source/RoadsRuntime/Private/RoadSplineComponent.cpp#44`

## Notes
First documented changelist of 2026 in this range. Roads plugin robustness fix.
