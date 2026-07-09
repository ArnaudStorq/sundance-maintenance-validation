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

### Template

```
### <Short title>

- Message: `<exact or pattern text>`
- Severity: Error | Warning
- Cause: <why it happens>
- Consequence: <impact if unresolved>
- Fix: <step-by-step resolution>
```

### Actor has invalid / missing references

- **Message**: e.g. `... references invalid mesh` / `Static mesh actor has NULL StaticMesh property`.
- **Severity**: Error.
- **Cause**: An actor points to an asset that was deleted, renamed, or not
  submitted.
- **Consequence**: Cook failures, missing geometry, or crashes at runtime.
- **Fix**: Reassign a valid asset, or delete the actor if it is obsolete. Verify
  the referenced asset is submitted to source control.

### Actor not assigned to a Runtime Grid / Data Layer

- **Message**: pattern indicating an actor is on the default grid or has no data
  layer.
- **Severity**: Warning.
- **Cause**: The [World Partition rules](../world-partition-rules/README.md) did
  not match the actor, often due to its Outliner path.
- **Consequence**: The actor streams incorrectly (always loaded, or loaded in
  the wrong cell), hurting memory and performance.
- **Fix**: Correct the actor's [Outliner path](../outliner/README.md) and re-run
  the rule builder.

### Overlapping / duplicated actors

- **Message**: e.g. `Actor is coincident with ...`.
- **Severity**: Warning.
- **Cause**: Two actors occupy the same transform, often from copy/paste or
  merge mistakes.
- **Consequence**: Z-fighting, doubled draw calls, ambiguous collision.
- **Fix**: Delete the duplicate, or offset it if both are intentional.

### Lighting needs to be rebuilt

- **Message**: `Lighting needs to be rebuilt`.
- **Severity**: Warning.
- **Cause**: Static geometry or lights changed after the last lighting build.
- **Consequence**: Incorrect lightmaps, visual artifacts.
- **Fix**: Rebuild lighting (**Build > Build Lighting Only**) or confirm the
  level is fully dynamic if that is intended.

## Workflow

1. Run **Build > Map Check** on the map or Level Instance.
2. Triage: fix all **Errors** first, then review **Warnings**.
3. For streaming/rule-related entries, cross-check the
   [World Partition rules](../world-partition-rules/README.md) and
   [Outliner](../outliner/README.md).
4. Re-run Map Check until it is clean before submitting.

## See also

- [World Partition Rules](../world-partition-rules/README.md)
- [Outliner management](../outliner/README.md)
