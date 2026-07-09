# Partitioned Streaming Migration

*A plain-language guide to converting non-partitioned levels so their actors can be
streamed and rule-managed.*

---

## 1. The core idea

For World Partition to stream a level's actors individually — and for the rule
builder to assign each actor a **RuntimeGrid** and **HLOD layer** — the level must
have **partitioned streaming** enabled.

A **non-partitioned** level behaves as a single block: its inner actors simply
**inherit** streaming/HLOD/DataLayer settings from the parent. You cannot give those
inner actors their own per-actor settings.

> Analogy: a non-partitioned level is a *sealed box*. You can move the whole box, but
> you can't tell each item inside the box to behave differently. "Partitioning" the
> level opens the box so each item can be addressed individually.

## 2. Why this matters (the concrete bug it fixes)

There was a real conflict in the data:

> The owning Level Instance was set to `LV_Overland_HLODLayer_Near`, while an actor
> inside it was being assigned to `SmallGrid` — **two mutually exclusive settings.**

While the level stayed non-partitioned, this contradiction couldn't be resolved
cleanly and surfaced as HLOD warnings. **Converting the level to partitioned
streaming** lets the rule pass give each actor consistent settings and clears the
conflict.

Jira: **SUNDANCE-62658**.

## 3. The two-step recipe (important!)

The migration always happens in **two distinct steps**, often in separate
changelists:

1. **Enable partitioned streaming** on the level ("open the box"). This mostly
   **adds** new external-actor packages.
2. **Apply World Partition rules** to the now-exposed actors ("label each item"):
   assign RuntimeGrid (often `SmallGrid`) and fix the HLOD layer. This mostly
   **edits** packages.

You can see this pattern directly in the history — e.g. six levels were *converted*
in one changelist, and their actors were *rule-processed* in a later one.

## 4. How it was rolled out

Because there are many levels, conversions were done in **batches** to keep each
change reviewable and each Perforce checkout sane. Example batch sizes from the work:

| Batch | Levels converted | Notes |
|-------|------------------|-------|
| Large sweep | **88 levels** | ~1,400 files (many adds) |
| Medium | 6 levels | Camps, Ruins, Quidditch, COG mission |
| Medium | 6 levels | GransHouse rocks, Camp props, COG cottage |
| Small | 4 levels | Rocks, Vault, Poacher crate |
| Small | 1–2 levels | targeted conversions |

Types of content converted include Level Assemblies (Rocks/Trees/Debris), Camp/
Population props, Road scatter meshes, Poacher camp meshes, CastleKit meshes, Ruins,
and Experimental/Vault levels.

## 5. The on/off switch for the SmallGrid rule

A small but instructive detail: to make the automatic assignment work during a
migration pass, `DA_SmallGrid_Rules` was **added** to the *"Runtime Grid Rules for
Actor Save"* config, the actors were processed, and then it was **removed** again.

> Why add-then-remove? Keeping SmallGrid permanently in the *on-save* rules would
> keep reassigning grids on every future save. It was only wanted for the one-off
> pass, so it was toggled on, used, and toggled off. This is a common, safe pattern
> for one-shot data migrations.

## 6. How levels to migrate were found

The `Editor.LogNonPartitionedLevelInstances` console command (see
`WorldPartitionRules.md`) lists every level still non-partitioned. That list drives
the migration batches instead of hunting by hand.

## 7. Cheat-sheet

```
Non-partitioned level ("sealed box")
        │  step 1: enable partitioned streaming (adds packages)
        ▼
Partitioned level ("open box")
        │  step 2: apply WP rules (edits packages) → RuntimeGrid + HLOD per actor
        ▼
Conflict resolved, no more HLOD warnings
```

## 8. Related changelists

In `WorkDoneByChangelists/P4-History/`: files named `*partitioned-streaming-*`,
`*wp-rules-level-instances*`, `*wp-rules-404-actors-smallgrid*`,
`*add-smallgrid-to-runtime-grid-rules*`,
`*remove-smallgrid-from-runtime-grid-rules*`,
`*remove-hlod-nonpartitioned-levels*`.

## See also
- `WorldPartitionRules.md` — the rules applied in step 2.
- `HLOD.md` — the HLOD conflict this migration resolves.
