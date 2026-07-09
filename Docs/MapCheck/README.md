# Map Check warnings & errors (Sundance / UE5)

This section documents the **Map Check** warnings and errors reported by Unreal
Engine 5 for the Sundance project: what they mean, why they matter, and how to
fix them.

## What is Map Check?

Map Check is Unreal's map-validation pass. It inspects the level for actors and
settings that are invalid, unsafe, or performance-hostile, and reports them as:

- **Errors** — must be fixed; they can break cooking, streaming, lighting, or
  gameplay.
- **Warnings** — should be reviewed; they usually indicate performance or
  correctness risks.

You can run it from the editor via **Build > Map Check**, or as part of an
automated/commandlet pass. Results appear in the **Message Log > Map Check**
panel, where each entry usually links to the offending actor.

## How to use this section

Each documented issue below follows the same template so fixes stay consistent:

- **Message** — the text (or pattern) as it appears in the Message Log.
- **Severity** — Error or Warning.
- **Cause** — what triggers it.
- **Consequence** — what breaks or degrades if it is left unfixed.
- **Fix** — the recommended resolution.

> Add new entries as they are encountered on the project. Prefer copying the
> exact log text so entries are searchable.

## Issue catalog

Entries are grouped by category. Messages shown as `exact` are stock engine
strings; messages shown as *(pattern)* are described because the exact wording
varies with the actor/asset name. When you hit a new one on the project, paste
the **exact** log line so the catalog stays searchable.

### Template

```
### <Short title>

- Message: `<exact or pattern text>`
- Severity: Error | Warning
- Cause: <why it happens>
- Consequence: <impact if unresolved>
- Fix: <step-by-step resolution>
```

---

## References & assets

### Static mesh actor has NULL StaticMesh property

- **Message**: `Static mesh actor has NULL StaticMesh property`
- **Severity**: Error.
- **Cause**: A `StaticMeshActor` exists with no mesh assigned, usually after the
  referenced mesh was deleted or a placeholder was left behind.
- **Consequence**: Nothing renders for the actor; can indicate a broken
  reference that also fails to cook.
- **Fix**: Assign a valid Static Mesh, or delete the actor if it is obsolete.

### Brush has NULL BrushComponent property

- **Message**: `Brush has NULL BrushComponent property`
- **Severity**: Error.
- **Cause**: A BSP brush actor lost its `BrushComponent`.
- **Consequence**: Invalid geometry; potential cook/build failures.
- **Fix**: Delete and recreate the brush, or remove it if unused.

### Actor references a missing / invalid asset

- **Message**: *(pattern)* — references to a mesh, material, or Blueprint that no
  longer exists.
- **Severity**: Error.
- **Cause**: An asset was deleted, renamed, or not submitted to source control.
- **Consequence**: Cook failures, missing content, or runtime crashes.
- **Fix**: Reassign a valid asset, or delete the actor. Confirm the referenced
  asset is submitted.

---

## Placement & duplicates

### Coincident / duplicated actors

- **Message**: *(pattern)* — an actor is reported at the same location as
  another actor.
- **Severity**: Warning.
- **Cause**: Two actors share the same transform, typically from copy/paste,
  merges, or import mistakes.
- **Consequence**: Z-fighting, doubled draw calls, ambiguous collision.
- **Fix**: Delete the duplicate, or offset it if both are intentional.

### Actor is far outside the world bounds

- **Message**: *(pattern)* — an actor is placed at an extreme coordinate.
- **Severity**: Warning.
- **Cause**: An actor accidentally dragged/typed to a huge coordinate.
- **Consequence**: Bloats the World Partition grid and streaming bounds;
  precision issues far from origin.
- **Fix**: Move the actor back into the intended playable area, or delete it.

---

## Lighting

### Maps need lighting rebuilt

- **Message**: `Maps need lighting rebuilt`
- **Severity**: Warning.
- **Cause**: Static geometry or static/stationary lights changed since the last
  lighting build.
- **Consequence**: Stale or incorrect lightmaps, visual artifacts.
- **Fix**: **Build > Build Lighting Only**, or confirm the level is intended to
  be fully dynamic (Lumen / movable lights).

### Multiple lights with the same GUID

- **Message**: *(pattern)* — lights sharing the same lighting GUID.
- **Severity**: Warning.
- **Cause**: A light was duplicated via copy/paste, carrying the original GUID.
- **Consequence**: Lightmap allocation conflicts; incorrect baked lighting.
- **Fix**: Select the affected lights and use **Choose New Light GUID**, then
  rebuild lighting.

---

## World Partition & streaming

### Actor not assigned to a Runtime Grid / Data Layer

- **Message**: *(pattern)* — actor left on the default grid or with no Data
  Layer.
- **Severity**: Warning.
- **Cause**: The [World Partition rules](../WorldPartitionRules/README.md) did
  not match the actor, often because of its [Outliner path](../Outliner/README.md).
- **Consequence**: The actor streams incorrectly (always loaded, or in the wrong
  cell), hurting memory and performance.
- **Fix**: Correct the actor's Outliner path and re-run the rule builder.

### Actor references an unloaded / missing Data Layer asset

- **Message**: *(pattern)* — reference to a Data Layer asset that is missing or
  not loaded.
- **Severity**: Error / Warning.
- **Cause**: A Data Layer asset was deleted/renamed while actors still reference
  it.
- **Consequence**: The actor cannot be assigned to its layer; streaming behavior
  is undefined.
- **Fix**: Repoint the actor to a valid Data Layer, or restore the asset.

### HLOD needs to be rebuilt

- **Message**: *(pattern)* — HLOD is out of date for the world.
- **Severity**: Warning.
- **Cause**: Actors or HLOD layer assignments changed after the last HLOD build.
- **Consequence**: Stale or missing proxy meshes at distance; visible pop-in.
- **Fix**: Rebuild HLOD (`-Builder=WorldPartitionHLODsBuilder` commandlet, or the
  editor's Build HLODs action).

---

## Collision, physics & navigation

### Actor has collision disabled

- **Message**: *(pattern)* — a collidable actor has collision turned off.
- **Severity**: Warning.
- **Cause**: `Collision Enabled` set to `NoCollision` on geometry that players
  are expected to interact with.
- **Consequence**: Players/AI clip through the geometry.
- **Fix**: Enable the appropriate collision, or confirm it is intentionally
  non-colliding.

### Navigation data needs to be rebuilt

- **Message**: *(pattern)* — navmesh out of date.
- **Severity**: Warning.
- **Cause**: Navigation-relevant geometry changed since the last navmesh build.
- **Consequence**: AI pathing errors.
- **Fix**: Rebuild navigation (**Build > Build Paths**) or confirm dynamic
  runtime navmesh generation is enabled.

---

## Foliage & landscape

### Foliage instances for a missing static mesh removed

- **Message**: `Foliage instances for a missing static mesh have been removed.`
- **Severity**: Warning.
- **Cause**: A foliage type's mesh was deleted; the editor pruned its instances.
- **Consequence**: Missing foliage; unintended content loss if it was a mistake.
- **Fix**: Reassign a valid mesh to the foliage type before saving, or accept the
  removal if intentional.

## Workflow

1. Run **Build > Map Check** on the map or Level Instance.
2. Triage: fix all **Errors** first, then review **Warnings**.
3. For streaming/rule-related entries, cross-check the
   [World Partition rules](../WorldPartitionRules/README.md) and
   [Outliner](../Outliner/README.md).
4. Re-run Map Check until it is clean before submitting.

## See also

- [World Partition Rules](../WorldPartitionRules/README.md)
- [Outliner management](../Outliner/README.md)
