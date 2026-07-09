Parent: [Reference Docs](README.md)

# Fixing MapCheck errors & warnings — Sundance playbook

A **cause → solution** playbook for the MapCheck warnings/errors actually hit and
fixed on `LV_Overland`, grounded in the changelist history
([`WorkDoneByChangelists/P4-History/`](../WorkDoneByChangelists/P4-History/README.md)), the topic write-ups
([`WorkDoneByTopic/`](../WorkDoneByTopic/README.md)), and the technical reference
([`ReferenceDocs/`](README.md)).

> This file focuses on **what we resolved on the project and *how it connects to the
> World Partition rules*** — because most of these were fixed
> not by hand-editing actors, but by assigning/tuning rules or by resolving
> conflicting properties that rule processing produced. For the other stock-engine
> Map Check messages (assets, lighting, collision, navigation, foliage…), see the
> generic catalog in [appendix G](#g-generic-engine-mapcheck-messages-catalog).

---

## The mental model: MapCheck ⇄ World Partition rules

Most streaming MapChecks are **symptoms of inconsistent per-actor streaming
properties** (`HLODLayer`, `RuntimeGrid`, `DataLayers`). Those properties are set, in
practice, by the **rule system** ([Reference: rules](WorldPartitionRules.md)):

- Rules run **on save** (allowed maps), during **streaming generation** (the
  `AvaStreamingGenerationMutator`), and in the batch **`WorldPartitionRuleBuilder`**.
- So a MapCheck warning is usually cleared by one of:
  1. **Assign the right rule** → the actor gets a consistent grid/HLOD/DataLayer.
  2. **Resolve a conflict the rules exposed** → e.g. a Level Instance on
     `LV_Overland_HLODLayer_Near` while an inner actor is pushed to `SmallGrid`
     (mutually exclusive) — see the "Skipped RuntimeGrid override" warning below.
  3. **Convert the level to World Partition** → so per-actor rules can even apply
     ([Reference: conversion](ConvertingLevelsToWorldPartition.md)).
  4. **Remove meaningless data** → strip HLOD/grid/DataLayers from non-partitioned
     inner actors that only inherit from their parent.

Key engine rule (why "invalid HLOD layer" fires): an actor is validated for HLOD/grid
compatibility **only if** it is HLOD-relevant **and** spatially loaded **and** has an
explicit HLOD layer **and** that layer is not allowed on its runtime grid. Full
detail: [Reference: streaming properties](WorldPartitionStreamingProperties.md).

---

## A. HLOD layer & runtime grid (the core streaming MapChecks)

### A1 — Actor has an invalid HLOD layer

- **Message**: `Actor <name> has an invalid HLOD layer <HLODLayerPath>`
  (MapCheck token `WorldPartition_InvalidActorHLODLayer_CheckForErrors`).
- **Severity**: Warning.
- **Cause**: The actor is HLOD-relevant, spatially loaded, and points at an HLOD layer
  that is **not registered for its runtime grid** in the map's runtime hash — often a
  removed/renamed layer, or a layer that is valid on a different grid than the one the
  actor now sits on. On `LV_Overland` this appeared in the **hundreds/thousands**.
- **Solution** (in order of preference):
  1. **Give the actor a grid+layer that are compatible** by (re)running the rules —
     assign the correct `TargetHLODLayer` via `UHLODLayerRuleAsset`, or the correct
     `TargetRuntimeGrid` via `URuntimeGridRuleAsset`. Often **just re-saving** the
     actor in an allowed map reapplies rules and fixes it.
  2. **Force-exclude** actor types/paths that should not be in HLOD:
     `ActorTypesToForceExcludeFromHLOD` / `OutlinerPathsToForceExcludeFromHLOD`
     → sets `HLODLayer = None` **and** `IncludeInHLOD = false` (actor stops being
     HLOD-relevant, so the check no longer applies).
  3. **Remove stale HLOD data** on non-partitioned inner actors (see A4).
- **Rules link**: direct — this is the flagship case that the HLOD rules and the
  `WorldPartitionRuleBuilder`/fixup builders were built to clear.
- **History**:
  [Fix MapCheck invalid HLOD layer (CL 1738687)](../WorkDoneByChangelists/P4-History/2026-02-25-13-59-fix-mapcheck-invalid-hlod-layer.md) ·
  [Fix 644 HLOD warnings in `LI_HM_Rocks_EXT` (CL 1904278)](../WorkDoneByChangelists/P4-History/2026-06-01-15-19-fix-644-mapcheck-hlod-warnings.md)

> Note: an in-editor "Fix It" MapCheck auto-fixer exists in the engine
> (`WorldPartitionHLODFixup::FixupOne`) but is **disabled** on this project; the bulk
> cleanup was done with the custom builders instead
> ([Reference: builders](BuildersAndCommandlets.md)).

### A2 — Actor has an invalid runtime grid

- **Message**: `Actor <name> has an invalid runtime grid <GridName>`
  (token `WorldPartition_InvalidRuntimeGrid_CheckForErrors`).
- **Severity**: **Error**.
- **Cause**: The actor references a runtime grid that does not exist in the map's
  runtime hash (typo, removed grid, or a grid name from a different map).
- **Solution**: Assign a valid grid via the RuntimeGrid rules, or clear it
  (`ActorTypesToClearRuntimeGrid` / `OutlinerPathsToClearRuntimeGrid`) so the actor
  falls back to the default grid. Re-save / re-run the rule builder.
- **Rules link**: direct — grid assignment is exactly what `URuntimeGridRuleSubsystem`
  does.

### A3 — "Skipped RuntimeGrid override" (the conflict signal)

- **Message**: `Skipped RuntimeGrid override ('<from>' -> '<to>') for actor '<actor>' in level '<level>': rule '<rule>' cannot use HLOD layer '<layer>' on that partition`
  (log `LogAvaStreamingGeneration`, Warning).
- **Severity**: Warning (streaming generation, not a MapCheck token, but shows the same
  root conflict).
- **Cause**: A rule (e.g. `DA_SmallGrid_Rules`) wants to move an actor to `SmallGrid`,
  but the actor's HLOD layer (e.g. `LV_Overland_HLODLayer_Near`) is **not allowed on
  the SmallGrid partition** — so the mutator refuses the grid change. This is the
  canonical "two mutually exclusive settings" conflict behind many invalid-HLOD-layer
  warnings.
- **Solution**:
  1. **Convert the owning level to World Partition** so the actor gets per-actor
     granularity and can hold a consistent grid+layer.
  2. **Align the HLOD layer rule** to the bounds/partitions `DA_SmallGrid_Rules`
     targets, and add **min-bounds guards** so tiny meshes are excluded.
  3. **Force-exclude from HLOD** where the actor should never have had a layer.
- **Rules link**: this warning *is* rule processing telling you the data is
  contradictory. Full detail:
  [Reference: rules/SmallGrid](WorldPartitionRules.md).
- **History**:
  [Apply WP rules to 404 actors — SmallGrid (CL 1959722)](../WorkDoneByChangelists/P4-History/2026-07-07-06-46-wp-rules-404-actors-smallgrid.md) ·
  [Add `DA_SmallGrid_Rules` on save (CL 1959020)](../WorkDoneByChangelists/P4-History/2026-07-06-16-14-add-smallgrid-to-runtime-grid-rules.md) ·
  [Remove it after the pass (CL 1960226)](../WorkDoneByChangelists/P4-History/2026-07-07-12-03-remove-smallgrid-from-runtime-grid-rules.md)

### A4 — Invalid HLOD layer on non-partitioned inner actors

- **Message**: same as A1, but on actors **inside a non-partitioned Level Instance**.
- **Severity**: Warning.
- **Cause**: Non-partitioned inner actors **inherit** streaming settings from the
  parent, so storing explicit `HLODLayer`/`RuntimeGrid`/`DataLayers` on them is
  meaningless and generates warnings.
- **Solution**: **Strip** the three properties from those inner actors
  (`SetHLODLayer(nullptr)`, `SetRuntimeGrid(NAME_None)`, `RemoveAllDataLayers()`), via
  the `WorldPartitionFixupNonPartitionedActorsBuilder`. A pass removed HLOD data from
  ~857 packages of non-partitioned levels.
- **Rules link**: indirect — the fixup builder is the "anti-rule" cleanup; it also
  skips non-partitioned Level Instances in the `RuleBuilder` so rules aren't wrongly
  applied to inherited content.
- **History**:
  [Remove HLOD from non-partitioned levels (CL 1918257)](../WorkDoneByChangelists/P4-History/2026-06-09-09-31-remove-hlod-nonpartitioned-levels.md)

### A5 — Tiny meshes wrongly treated as HLOD candidates

- **Symptom**: single small props (e.g. `SM_Single_Stone_*`) showing up as HLOD
  "NoneInclude", producing noise/warnings in Hogsmeade.
- **Cause**: no minimum size guard in the HLOD NoneInclude rule.
- **Solution**: enforce a **2 m minimum bounds** on the HLOD *NoneInclude* rule so
  sub-threshold meshes are excluded.
- **Rules link**: direct — `FWorldPartitionRuleCondition` min-bounds guard on the HLOD
  rule asset.
- **History**:
  [HLOD NoneInclude min bounds — Hogsmeade (CL 1950932)](../WorkDoneByChangelists/P4-History/2026-06-30-09-13-hlod-noneinclude-min-bounds.md)

### A6 — Unexpected HLOD chaining (Foliage Near)

- **Symptom**: foliage-near content chained to a parent HLOD layer it shouldn't.
- **Cause**: `HLODLayer_Foliage_Near` had a **Parent Layer** set.
- **Solution**: set the **Parent Layer to `None`** on `HLODLayer_Foliage_Near`.
- **History**:
  [Set Parent Layer None — Foliage Near (CL 1753959)](../WorkDoneByChangelists/P4-History/2026-03-09-09-07-set-parent-layer-none-foliage-near.md)

### A7 — Rule matched nothing (naming) / wrong actor class handling

- **Symptom A**: expected actors never got their grid/HLOD, so warnings persisted.
  **Cause**: rules used plural `Dungeons`/`Missions` but the real categories are
  singular `Dungeon`/`Mission` → matched nothing.
  **Solution**: fix the rule naming.
  [WP rules Dungeon/Mission naming (CL 1920591)](../WorkDoneByChangelists/P4-History/2026-06-10-14-19-wp-rules-dungeon-mission-naming.md)
- **Symptom B**: `WorldBitmapStreamingProxy` was silently *ignored* by the grid rules.
  **Cause**: it sat in *"Actor Types Ignored by Runtime Grid Rules"*.
  **Solution**: remove it from the ignore list and handle it **explicitly** —
  add to *Force Exclude from HLOD* and *Clear Runtime Grid*.
  [WP rules `WorldBitmapStreamingProxy` (CL 1916537)](../WorkDoneByChangelists/P4-History/2026-06-08-13-02-wp-rules-worldbitmapstreamingproxy.md)
- **Symptom C**: road content handled inconsistently.
  **Solution**: add `Overland_Road_Near` to the road HLOD include/exclude rules.
  [Add `Overland_Road_Near` exclusions (CL 1893933)](../WorkDoneByChangelists/P4-History/2026-05-25-09-11-add-overland-road-near-exclusions.md)
- **Rules link**: direct — all three are rule-asset/config edits.

---

## B. Data Layers

These are raised by the Sundance `UWorldPartitionMapCheckValidator` (runs on
`FEditorDelegates::OnGameMapChecked`), most with an in-editor **"Fix It!"** action.

### B1 — Actor assigned to a Data Layer that doesn't exist

- **Message**: `<actor> is assigned to DataLayer '<dl>' that doesn't exist in the AWorldDataLayers. Please add this DataLayer to your level or remove it from the actor to avoid unexpected behavior.`
- **Severity**: Warning · **Fix It** → `ResolveMissingDataLayerInstance`.
- **Cause**: a Data Layer asset was deleted/renamed while actors still reference it.
- **Solution**: use Fix It (resolve the instance) or remove the DataLayer from the
  actor; only valid when the world is in the auto-apply list.
- **Rules link**: the DataLayer rules can re-resolve/clear these
  (`ActorTypesToClearDataLayers`).

### B2 — Actor has a Data Layer that violates the rules

- **Message**: `DataLayer '<dl>' is assigned to actor '<actor>' but does not comply with the rules. It must not be assigned to this actor. Please remove it from the actor.`
- **Severity**: Warning · **Fix It** → `RemoveNonCompliantDataLayersFromActor`.
- **Cause**: an actor carries a DataLayer the DataLayer rules say it shouldn't.
- **Solution**: Fix It removes the non-compliant DataLayer; or re-run the DataLayer
  rules.
- **Rules link**: **direct** — the validator literally checks against the DataLayer
  rule set.

### B3 — Data Layer hierarchy mismatch

- **Message**: `Data Layer hierarchy '<a>' of level '<lvl>' doesn't match '<b>' of world '<world>'`
- **Severity**: Warning.
- **Cause**: a sub-level's DataLayer hierarchy diverged from the world's.
- **Solution**: reconcile the level's DataLayer hierarchy with the world's
  `AWorldDataLayers`.

### B4 — Editing shared Data Layers safely (prevention)

- **Context**: editing a Possible World Event modifies the `WorldDataLayers` instance.
- **Cause**: doing so while that asset is **not checked out / out of date** can fail or
  corrupt data.
- **Solution**: verify `WorldDataLayers` is checkoutable and up to date **before**
  editing. Prevents a class of DataLayer breakage that would later show up in MapCheck.
- **History**:
  [WorldEvent DataLayers checkout check (CL 1758012)](../WorkDoneByChangelists/P4-History/2026-03-11-09-21-worldevent-datalayers-checkout-check.md) ·
  see [`WorkDoneByTopic/WorldEvents.md`](../WorkDoneByTopic/WorldEvents.md).

---

## C. Level Instances & partitioning

### C1 — LevelInstance is not using World Partition

- **Message**: `LevelInstance '<name>' is not using World Partition. Please convert it to a World Partition level.`
- **Severity**: Warning · **Fix It** → `ConvertLevelToWorldPartition`.
- **Cause**: a Level Instance under a partitioned world is still non-partitioned, so its
  inner actors can't receive per-actor rules (and inherited settings cause A4-style
  warnings).
- **Solution**: **convert the level to World Partition**, then apply rules. Batch/headless
  conversion (with the Nanite-assembly cvar workaround) is the project workflow.
- **Rules link**: prerequisite — conversion is step 1, rule application is step 2.
- **History**:
  [Partitioned streaming — 88 levels (CL 1946247)](../WorkDoneByChangelists/P4-History/2026-06-26-15-57-partitioned-streaming-88-levels.md) ·
  [Apply WP rules to Level Instances (CL 1959005)](../WorkDoneByChangelists/P4-History/2026-07-06-16-12-wp-rules-level-instances.md) ·
  full detail [Reference: conversion](ConvertingLevelsToWorldPartition.md).

### C2 — LevelInstance world does not support World Partition streaming

- **Message** (engine, WB rephrase): a Level Instance world asset without external
  actors *"does not support World Partition streaming"* (was Epic's *"is not using
  external actors, resave level to add compatibility"*).
- **Severity**: Warning.
- **Cause**: the referenced world isn't OFPA/partitioned.
- **Solution**: same as C1 — convert / add partitioned streaming support.

---

## D. Placement, bounds & references

### D1 — Actor has an invalid reference

- **Message**: `Actor <name> has an invalid reference to <other>`
  (token `WorldPartition_MissingActorReference_CheckForErrors`).
- **Severity**: **Error** (HLOD actors are downgraded to Warning by the changelist
  validator).
- **Cause**: an actor references another actor that is missing from the loaded set /
  changelist. In OFPA worlds, referenced external actors must be **in the same
  changelist** — this is enforced at submit by the changelist validators
  ([Reference: Perforce](PerforceSourceControl.md)).
- **Solution**: include the referenced package(s) in the changelist, or fix/remove the
  dangling reference.

### D2 — Oversized streaming bounds

- **Message**: `<n> Streaming Bounds of '<li>' are oversized and might cause issues with Minimap zooming and other functionalities. (<info>)`
- **Severity**: Warning.
- **Cause**: a Level Instance's streaming bounds are far larger than expected, usually
  from an actor placed at an extreme coordinate inside it.
- **Solution**: find and reposition/remove the far-flung actor so the bounds shrink.

### D3 — Brush far from the Level Instance pivot

- **Message**: `Brush <b> in LevelInstance '<li>' location (<x>) is too far from level's pivot point (<p>) and might cause issues with Minimap zooming and other functionalities.`
- **Severity**: Warning.
- **Cause**: a brush ≥ 200000 units from the LI pivot.
- **Solution**: move the brush near the pivot, or rebuild the LI pivot.

### D4 — Spatially loaded actor references a non-spatially loaded actor

- **Message**: `Spatially loaded actor <actor> references Non-spatially loaded actor <other>`
  (token `WorldPartition_StreamedActorReferenceAlwaysLoadedActor_CheckForErrors`).
- **Severity**: Warning (it is an **Error** in the mirror case — a non-spatial actor
  referencing a spatial one — but the streamed→always-loaded direction is the one that
  shows up on the project).
- **Cause**: streaming generation requires a reference to link actors that share the
  **same `Is Spatially Loaded` state** — the check is literally
  `bIsActorDescSpatiallyLoaded == bIsActorDescRefSpatiallyLoaded`
  (`WorldPartitionStreamingGeneration.cpp:1404`, `IsReferenceGridPlacementValid`). A
  spatially-loaded (streamed) actor hard-references a non-spatially-loaded
  (always-loaded) actor. On the project this is overwhelmingly **mission/staging
  content**: a streamed manager/spline/trigger BP (`BP_*Manager`, `BP_PerformTasks_*`,
  `BP_*Spline*`) referencing an always-loaded scene-rig / cinematic / volume actor
  (`*_SR`, `CIV_*`, `VOM_*`, `SceneRig`, `*PreloadVolume`, `*TriggerBox`).
- **Consequence**: this is not cosmetic. When it isn't the error-reporting pass, the
  generator calls `SetForcedNonSpatiallyLoaded()` on **both** actors
  (`WorldPartitionStreamingGeneration.cpp:1575`) — i.e. it silently **demotes the
  streamed actor to always-loaded** so the pair stays together. The actor then never
  streams out, bloating the always-loaded set (and dragging along everything it chains
  to).
- **Solution** (make the two sides consistent):
  1. **Editor-only reference** — if the link is only needed in the editor, expose it
     through an editor-only property; the check explicitly skips editor-only references
     (`IsEditorOnlyReference`, `WorldPartitionStreamingGeneration.cpp:1564`).
  2. **Align the streamed side** — set the referencing actor's **Is Spatially Loaded =
     false** when it genuinely belongs with its always-loaded staging (the common fix
     for mission scene-rig setups), so the demotion becomes intentional rather than
     silent.
  3. **Align the referenced side** — set the target's **Is Spatially Loaded = true** if
     it can actually stream, so both end up spatially loaded.
  4. Keep tightly-coupled staging actors in the **same streaming state / Data Layer** at
     level-setup time so the generator never has to force-demote them.
- **Rules link**: indirect — the rules set grids/HLOD/DataLayers, but the spatial state
  behind this warning is an authored per-actor property; the fix is a level/mission
  data cleanup, not a rule assignment.

---

## E. Components & references

### E1 — Stale material overrides

- **Message**: `StaticMeshComponent '<c>' has more material overrides (<n>) than its static mesh asset (<m>). This will pull on useless references. Please cleanup the components material overrides array.`
- **Severity**: Warning · **Fix It** (trims `OverrideMaterials`).
- **Cause**: the component's override array is longer than the mesh's material slots
  (usually after a mesh's slots were reduced).
- **Solution**: Fix It trims the extra overrides, dropping the useless references.

---

## F. Actor descriptor maintenance

### F1 — Actor needs resave

- **Message**: `Actor needs resave <actor>`
  (token `WorldPartition_ActorNeedsResave_CheckForErrors`).
- **Severity**: **Info** (a notice, not counted in the Warning/Error totals) — but it
  points at real stale data.
- **Cause**: the actor's World Partition descriptor is out of date. `IsResaveNeeded()`
  returns true when the actor is **spatially loaded but its cached `RuntimeBounds` are
  invalid** (`WorldPartitionActorDesc.h:381` —
  `bIsSpatiallyLoaded && !RuntimeBounds.IsValid`). This is the classic "saved before the
  descriptor format added runtime bounds" case: the package predates the current
  actor-desc version.
- **Consequence**: without valid runtime bounds the actor can't be placed accurately in
  the streaming grid (cell/bounds computation falls back), which can feed the oversized
  streaming-bounds (D2) and inconsistent-streaming symptoms.
- **Solution**: **re-save the actor's package** in an allowed map — the resave
  regenerates the descriptor with valid `RuntimeBounds` and clears the notice. Diff
  before submit so nothing but the descriptor changed (see the transform-drift guard in
  the Workflow below).
- **Rules link**: indirect — same "resave reapplies everything" mechanism the A/B fixes
  rely on; here it is refreshing the descriptor rather than reassigning a rule.

---

## Workflow (triage order)

1. Run **Build → Map Check** on the map / Level Instance.
2. Fix **Errors** first (invalid runtime grid A2, invalid reference D1), then Warnings.
3. For streaming warnings (A-series), ask **"is this a rules problem?"**:
   - Is the level partitioned? If not → convert (C1) then apply rules.
   - Does a rule match this actor? If not → fix the rule (naming/ignore lists, A7).
   - Is there a grid↔HLOD conflict (A3)? → align rules / force-exclude / convert.
   - Is the data just inherited junk (A4)? → strip it with the fixup builder.
4. For most A/B cases, **re-saving the actor in an allowed map reapplies the rules** and
   clears the warning — try that before manual edits.
5. **Diff before submit** — a resave must not change `RelativeLocation/Rotation/Scale3D`
   ([Reference: transform drift](TransformDrift.md)). Revert any package
   that drifted.
6. Re-run Map Check until clean; the changelist/Peeves validators
   ([Reference: Peeves](PeevesSubmitValidation.md)) run the same checks
   at submit.

---

## G. Generic engine MapCheck messages (catalog)

The sections above cover what was actually resolved on `LV_Overland` and how it maps
to the World Partition rules. This appendix is the **generic reference** for the other
stock **Map Check** messages Unreal Engine 5 can raise — what they mean and how to fix
them — so a clean triage has a single home.

> **Map Check** is Unreal's map-validation pass (**Build → Map Check**, or a commandlet
> pass; results in **Message Log → Map Check**). **Errors** must be fixed (they break
> cooking, streaming, lighting, or gameplay); **Warnings** should be reviewed. Each
> entry below lists the *(exact or pattern)* message, severity, cause, consequence, and
> fix. When you hit a new one, paste the **exact** log line so this stays searchable.
>
> Streaming/rule messages that we hit are documented above, not here:
> "actor left on the default grid / not assigned to a Data Layer" → **A1/A2/A7**;
> "actor references a missing / unloaded Data Layer asset" → **B1**.

### References & assets

#### G1 — Static mesh actor has NULL StaticMesh property

- **Message**: `Static mesh actor has NULL StaticMesh property`
- **Severity**: Error.
- **Cause**: a `StaticMeshActor` exists with no mesh assigned, usually after the
  referenced mesh was deleted or a placeholder was left behind.
- **Consequence**: nothing renders for the actor; can indicate a broken reference that
  also fails to cook.
- **Fix**: assign a valid Static Mesh, or delete the actor if it is obsolete.

#### G2 — Brush has NULL BrushComponent property

- **Message**: `Brush has NULL BrushComponent property`
- **Severity**: Error.
- **Cause**: a BSP brush actor lost its `BrushComponent`.
- **Consequence**: invalid geometry; potential cook/build failures.
- **Fix**: delete and recreate the brush, or remove it if unused.

#### G3 — Actor references a missing / invalid asset

- **Message**: *(pattern)* — references to a mesh, material, or Blueprint that no
  longer exists (distinct from the actor→actor **invalid reference** in D1).
- **Severity**: Error.
- **Cause**: an asset was deleted, renamed, or not submitted to source control.
- **Consequence**: cook failures, missing content, or runtime crashes.
- **Fix**: reassign a valid asset, or delete the actor. Confirm the referenced asset is
  submitted.

### Placement & duplicates

#### G4 — Coincident / duplicated actors

- **Message**: *(pattern)* — an actor is reported at the same location as another actor.
- **Severity**: Warning.
- **Cause**: two actors share the same transform, typically from copy/paste, merges, or
  import mistakes.
- **Consequence**: Z-fighting, doubled draw calls, ambiguous collision.
- **Fix**: delete the duplicate, or offset it if both are intentional.

#### G5 — Actor is far outside the world bounds

- **Message**: *(pattern)* — an actor is placed at an extreme coordinate (distinct from
  the Level-Instance bounds/pivot warnings D2/D3).
- **Severity**: Warning.
- **Cause**: an actor accidentally dragged/typed to a huge coordinate.
- **Consequence**: bloats the World Partition grid and streaming bounds; precision
  issues far from origin.
- **Fix**: move the actor back into the intended playable area, or delete it.

### Lighting

#### G6 — Maps need lighting rebuilt

- **Message**: `Maps need lighting rebuilt`
- **Severity**: Warning.
- **Cause**: static geometry or static/stationary lights changed since the last lighting
  build.
- **Consequence**: stale or incorrect lightmaps, visual artifacts.
- **Fix**: **Build → Build Lighting Only**, or confirm the level is intended to be fully
  dynamic (Lumen / movable lights).

#### G7 — Multiple lights with the same GUID

- **Message**: *(pattern)* — lights sharing the same lighting GUID.
- **Severity**: Warning.
- **Cause**: a light was duplicated via copy/paste, carrying the original GUID.
- **Consequence**: lightmap allocation conflicts; incorrect baked lighting.
- **Fix**: select the affected lights and use **Choose New Light GUID**, then rebuild
  lighting.

### World Partition & streaming

#### G8 — HLOD needs to be rebuilt

- **Message**: *(pattern)* — HLOD is out of date for the world (distinct from the
  *invalid* HLOD-layer warnings in A1/A3, which are about wrong assignments rather than a
  stale build).
- **Severity**: Warning.
- **Cause**: actors or HLOD layer assignments changed after the last HLOD build.
- **Consequence**: stale or missing proxy meshes at distance; visible pop-in.
- **Fix**: rebuild HLOD (`-Builder=WorldPartitionHLODsBuilder` commandlet, or the
  editor's Build HLODs action — see [builders](BuildersAndCommandlets.md)).

### Collision, physics & navigation

#### G9 — Actor has collision disabled

- **Message**: *(pattern)* — a collidable actor has collision turned off.
- **Severity**: Warning.
- **Cause**: `Collision Enabled` set to `NoCollision` on geometry players are expected
  to interact with.
- **Consequence**: players/AI clip through the geometry.
- **Fix**: enable the appropriate collision, or confirm it is intentionally
  non-colliding.

#### G10 — Navigation data needs to be rebuilt

- **Message**: *(pattern)* — navmesh out of date.
- **Severity**: Warning.
- **Cause**: navigation-relevant geometry changed since the last navmesh build.
- **Consequence**: AI pathing errors.
- **Fix**: rebuild navigation (**Build → Build Paths**) or confirm dynamic runtime
  navmesh generation is enabled.

### Foliage & landscape

#### G11 — Foliage instances for a missing static mesh removed

- **Message**: `Foliage instances for a missing static mesh have been removed.`
- **Severity**: Warning.
- **Cause**: a foliage type's mesh was deleted; the editor pruned its instances.
- **Consequence**: missing foliage; unintended content loss if it was a mistake.
- **Fix**: reassign a valid mesh to the foliage type before saving, or accept the
  removal if intentional.

---

## See also

- [Reference — streaming properties](WorldPartitionStreamingProperties.md),
  [rules/SmallGrid/IncludeInHLOD](WorldPartitionRules.md),
  [builders](BuildersAndCommandlets.md)
- [World Partition Rules (how-to)](WorldPartitionRules.md)
- Plain-language: [`WorkDoneByTopic/HLOD.md`](../WorkDoneByTopic/HLOD.md)
