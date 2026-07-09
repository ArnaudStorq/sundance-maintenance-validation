# World Events

*A plain-language guide to the World Events system changes made in 2026.*

---

## 1. What are World Events?

**World Events** are scripted things that happen in the world — triggered by
conditions such as the player getting within a certain distance, time of day, or
game state. In this project they are driven by components like
`WorldEventActorComponent` and located/resolved by `WorldEventLocator`.

A "**Possible World Event**" is an event that may be placed/activated in the world;
editing its content can touch shared World Partition data (specifically the
`WorldDataLayers` instance, which describes the level's Data Layers).

## 2. The two changes

### A. Safe check-out before editing a Possible World Event
**Problem:** when updating the content of a Possible World Event, the code modified
the `WorldDataLayers` instance. If that asset was **not checked out** or was **out of
date**, the operation could fail or corrupt data.

**Fix:** before making the change, verify that the `WorldDataLayers` instance is
**available for check out and up to date**. Only proceed when it's safe.

> Analogy: don't start editing a shared document until you've confirmed you have the
> latest copy and the right to write to it.

### B. Fix a Python name-collision startup warning
**Problem:** two members of `WorldEventActorComponent` mapped to the **same
auto-generated Python name**:

```
LogPython: Warning: 'WorldEventActorComponent.bTriggerEventOnCameraDistanceToPlayer'
and 'WorldEventActorComponent.TriggerEventOnCameraDistanceToPlayer' have the same
name (trigger_event_on_camera_distance_to_player) when exposed to Python.
```

When Unreal exposes C++ properties to Python, it converts names to `snake_case`. A
boolean `bTrigger...` and a non-boolean `Trigger...` both collapsed to the *same*
Python name, producing a warning at **every editor startup**.

**Fix:** disambiguate the exposed name (via `ScriptName` meta-data) so the two
members no longer clash.

## 3. Why these matter

- Change **A** is a **data-safety** fix: it prevents a failed/corrupting edit on
  shared World Partition data.
- Change **B** is a **cleanliness** fix: removing constant startup warning noise so
  the log stays readable and real issues stand out. (This is the same motivation as
  the other startup-warning cleanups — see `EditorStabilityAndWarnings.md`.)

## 4. Related changelists

In `WorkDoneByChangelists/P4-History/`: `*worldevent-datalayers-checkout-check*`,
`*fix-python-name-clash-warning*`.

Jira: **SUNDANCE-51436**, **SUNDANCE-56129**.

## See also
- `EditorStabilityAndWarnings.md` — related startup-warning and robustness fixes.
