Parent: [Work Summaries](README.md)

# HLOD & MapCheck Cleanup

*A plain-language guide to HLOD layers, the warnings they produced, and the cleanup
done in 2026.*

---

## 1. What is HLOD?

**HLOD** = **Hierarchical Level of Detail**. When objects are far from the camera,
rendering each one individually is wasteful. HLOD replaces groups of distant objects
with a single, cheaper, merged proxy mesh. As you get closer, the real objects come
back.

> Analogy: from an airplane a city looks like one grey blur (the HLOD proxy). As you
> descend, individual buildings appear (the real actors).

An **HLOD layer** is a named bucket that tells the system *how* an actor should be
represented at distance (or that it should be excluded from HLOD entirely). Examples
in this project: `LV_Overland_HLODLayer_Near`, `..._Foliage_Near`, `Road_Near`, and
"NoneInclude"/"NoneExclude" rule sets.

## 2. What is MapCheck?

**MapCheck** is Unreal's built-in level validation. It scans a level and reports
problems as warnings/errors — for example, an actor pointing at an HLOD layer that no
longer exists:

```
<Actor> has an invalid HLOD layer <Layer>
```

Hundreds of these warnings drown out the *real* problems, so keeping MapCheck clean
matters for everyone's validation workflow.

## 3. The problems that were fixed

### Invalid HLOD layer warnings
Many actors referenced HLOD layers that were no longer valid. Two notable cleanups:
- A first pass fixed the warning for a handful of actors across several levels.
- A big pass cleared **644 warnings** of the "invalid HLOD layer" type in a single
  Hogsmeade rocks level (`LI_HM_Rocks_EXT`).

### HLOD data on levels that shouldn't have it
Non-partitioned levels inherit HLOD behavior from their parent, so storing explicit
HLOD data on their actors is meaningless — and it generated warnings. A pass
**removed HLOD layer information from non-partitioned levels** (~857 packages).

### Tuning the HLOD rules
- **Minimum size guard:** forced a **2 m** minimum bounds for HLOD *NoneInclude* in
  Hogsmeade, so tiny meshes (e.g. a single cobble stone `SM_Single_Stone_...`) are no
  longer wrongly treated as HLOD "none-include" candidates.
- **Parent layer cleared:** set the **Parent Layer to `None`** on
  `HLODLayer_Foliage_Near` so the foliage-near layer doesn't chain to a parent,
  giving the intended HLOD hierarchy.
- **Road handling:** added `Overland_Road_Near` to the include/exclude rules so road
  content is treated consistently.

## 4. Why this connects to the bigger picture

The recurring theme across topics is the conflict:

> A Level Instance set to `HLODLayer_Near` while one of its actors is pushed onto
> `SmallGrid` — settings that can't both be true.

The HLOD cleanup here and the **Partitioned Streaming** migration
(`PartitionedStreaming.md`) are two sides of resolving that conflict: partition the
level so each actor can be given a *consistent* grid + HLOD, and remove the stale
HLOD data that never applied.

## 5. Cheat-sheet

| Symptom | Cause | Fix |
|---------|-------|-----|
| "invalid HLOD layer" MapCheck warnings | actor points to a removed/renamed layer | reassign or clear the layer |
| Tiny props showing up as HLOD candidates | no minimum size in NoneInclude rule | enforce 2 m minimum bounds |
| HLOD warnings on inherited content | explicit HLOD data on non-partitioned levels | remove that data |
| Unexpected HLOD chaining | Foliage_Near had a Parent Layer | set Parent Layer to None |

## 6. Related changelists

In `WorkDoneByChangelists/P4-History/`: `*fix-mapcheck-invalid-hlod-layer*`,
`*fix-644-mapcheck-hlod-warnings*`, `*remove-hlod-nonpartitioned-levels*`,
`*hlod-noneinclude-min-bounds*`, `*set-parent-layer-none-foliage-near*`,
`*add-overland-road-near-exclusions*`.

Jira: **SUNDANCE-41838** (and related 62658).

## See also
- `WorldPartitionRules.md` — HLOD rules are part of the WP rule set.
- `PartitionedStreaming.md` — resolves the HLOD/SmallGrid conflict.
