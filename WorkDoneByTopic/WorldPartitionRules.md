# World Partition Rules

*A plain-language guide to the World Partition rule system, the rule builder, and
the fixes made to it in 2026.*

---

## 1. Background: what is World Partition?

A modern open world is far too big to keep entirely in memory. **World Partition**
is Unreal's system that automatically splits the world into a grid of cells and
**streams** them in/out as the player moves. Each actor needs to know:

- **RuntimeGrid** — which streaming grid it belongs to (e.g. a big grid for large
  landmarks, a `SmallGrid` for small props).
- **HLOD layer** — which "Hierarchical Level of Detail" proxy represents it when it
  is far away (see `HLOD.md`).
- **Data Layer** — which logical layer (e.g. season/state variant) it belongs to.

Setting these by hand on tens of thousands of actors is impossible. So the project
uses **rules**.

## 2. What are "World Partition Rules" here?

They are two things working together:

1. **Rule data assets** — configuration assets (e.g.
   `DA_Overland_HLODLayer_Near_Rules`, `DA_SmallGrid_Rules`) that say *"actors
   matching condition X should get setting Y"*.
2. **The rule builder** (`WorldPartitionRuleBuilder`) — the C++ code/commandlet that
   reads those rules and **applies** them to actors, then saves the changed packages.

Analogy: the **rule assets are the recipe**, the **rule builder is the cook**.

## 3. Why work was needed

Two kinds of problems showed up:

- **The cook made mistakes.** An automated run of the builder (on the TeamCity CI
  server) modified actors' **relative location/rotation** incorrectly, subtly moving
  content. This had to be found, reverted, and the builder hardened so it couldn't
  happen again.
- **The recipe needed tuning.** Rule assets referenced wrong names, missed some
  actor types, or lacked sensible limits.

Main Jira references: **SUNDANCE-52910** (builder), **SUNDANCE-41838** (HLOD rules),
**SUNDANCE-54425** (folder/streaming), **SUNDANCE-62658** (streaming migration).

## 4. Fixing the "cook" (the rule builder)

Several fixes made the builder correct and safe, in order:

1. **Skip non-partitioned Level Instances.** Actors inside a *non-partitioned* Level
   Instance inherit their settings from the parent, so applying per-actor rules to
   them is wrong. The builder now skips them.
   *Simple analogy: don't repaint a room that inherits its color from the whole house.*
2. **Release kept references.** The builder held onto loaded packages longer than
   needed, bloating memory. It now releases them, keeping large runs stable.
3. **Make `PackagesToSave` transient + keep Level Instance references.** The
   "to-save" working list was accidentally being **serialized** (saved into the
   asset) instead of being purely in-memory. Marking it `transient` fixes that, and
   references needed during Level Instance processing are now retained so they aren't
   collected too early. **This was the root cause** of the bad transform run.
4. **General robustness.** Support "Discard OutlinerPath"; only commit when a file
   actually changed (no more empty/no-op commits); and skip Level Instances with
   **non-uniform scaling** (their transforms can't be safely recomputed).

### The revert
When the bad CI run was discovered, the safest immediate action was to **revert**
it — undoing a changelist that had touched **~8,700 files**. Only after the builder
fixes above were in place was rule processing trusted again.

## 5. Repairing the damage (relative transforms)

Because the bad run had shifted actors, follow-up passes restored correct
`RelativeLocation` / `RelativeRotation` values:

- First on Level Instance `.umap` assets wrongly modified by the CI automation.
- Then on additional level maps.
- Then specifically on **Book** actors that were still off.

> Why "relative"? An actor inside a Level Instance stores its position *relative to*
> the instance, not in absolute world space. A bug in how the builder recomputed
> these relative values is exactly what caused the drift.

## 6. Tuning the "recipe" (rule data assets)

Concrete examples of rule-asset changes:

- **Naming fix:** rules used `"Dungeons"`/`"Missions"` but the real categories are
  singular `"Dungeon"`/`"Mission"` — so the rules matched nothing until corrected.
- **`WorldBitmapStreamingProxy` reclassified:** removed from *"Actor Types Ignored by
  Runtime Grid Rules"*, and added to *"Force Exclude from HLOD"* and *"Clear Runtime
  Grid"* — i.e. handle it explicitly instead of ignoring it.
- **Minimum size guard:** forced a **2 m** minimum bounds for HLOD *NoneInclude* in
  Hogsmeade, so tiny meshes (like a single cobble stone) stop being treated as HLOD
  candidates.
- **New exclusions:** added `Overland_Road_Near` to the road HLOD include/exclude
  rules for consistent handling.

## 7. A helpful diagnostic tool

A console command **`Editor.LogNonPartitionedLevelInstances`** was added to list all
Level Instances that are still non-partitioned. This directly feeds the
**Partitioned Streaming** migration (see `PartitionedStreaming.md`), because a level
must be partitioned before the builder can assign per-actor rules to it.

## 8. Mental model / cheat-sheet

```
Rule assets (recipe)  ──►  WorldPartitionRuleBuilder (cook)  ──►  actors get
  DA_*_Rules                 - skip non-partitioned LI            RuntimeGrid,
                             - keep transforms correct            HLOD layer,
                             - save only real changes             Data Layer
```

## 9. Related changelists

In `WorkDoneByChangelists/P4-History/`: files named `*wp-rules-*`, `*fix-relative-transform*`,
`*fix-wp-rules-packagestosave*`, `*release-references-wp-rules*`,
`*revert-wp-rules-processing*`, `*skip-nonpartitioned-li*`,
`*add-lognonpartitioned-command*`, and the HLOD rule tweaks.

## See also
- `PartitionedStreaming.md` — making levels eligible for these rules.
- `HLOD.md` — the HLOD side of the rules.
