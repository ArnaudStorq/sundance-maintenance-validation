Parent: [Reference Docs](README.md)

# RuntimeGrid reference conflict resolution

A new pass of the World Partition rule system. While the RuntimeGrid rules run, it reads each
actor's descriptor references, compares the **resolved** RuntimeGrid of the actors a reference
connects, and when they disagree it moves the whole reference cluster onto the **largest grid of
the cluster** — the grid with the biggest cell size — so every actor streams together.

It exists because the
[D5 MapCheck error](FixingMapCheckIssues.md#d5--actor-references-an-actor-in-a-different-runtime-grid)
— *"actor references an actor in a different runtime grid"* — is produced **by the rules
themselves**: they assign grids per actor, from size and Outliner path, while references ignore
both. Repairing it actor by actor, as the
[Vault audit](../Audits/MapCheckRuntimeGridReferences-Vault-2026-10-05.md) did, treats the symptom
and the nightly builder puts the divergence back. This pass makes the rule pass itself close the
hole it opens.

- **Changelist**: **2112721** (pending, `//sun/Dev`), description
  `WP Rules: move reference clusters with diverging resolved RuntimeGrid onto the largest grid of the cluster (resolve None via attach parents)`.
- **Module**: `WorldBuildingEditor` — `D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\`.
- **Status**: compiles clean against the module's own options (shared PCH, MSVC 14.50, `/W4 /WX`).
  Not yet run through the builder: see [Verification](#verification).

## Contents

- [The problem](#the-problem)
- [The rule](#the-rule)
  - [Resolved grids, not authored names](#resolved-grids-not-authored-names)
  - [Resolving `None` through attach parents](#resolving-none-through-attach-parents)
  - [Why the largest grid](#why-the-largest-grid)
  - [Clusters, not reference edges](#clusters-not-reference-edges)
- [Where the pass runs](#where-the-pass-runs)
- [Implementation](#implementation)
- [Settings](#settings)
- [Hogwarts and Hogsmeade](#hogwarts-and-hogsmeade)
  - [The grids `LV_Overland` declares](#the-grids-lv_overland-declares)
  - [Who carries `HogwartsGrid` and `HogsmeadeGrid`](#who-carries-hogwartsgrid-and-hogsmeadegrid)
  - [Inside the sub-worlds the pass is inert](#inside-the-sub-worlds-the-pass-is-inert)
  - [At the `LV_Overland` level the largest grid cuts both ways](#at-the-lv_overland-level-the-largest-grid-cuts-both-ways)
  - [The HLOD tier allowlist is a partial net](#the-hlod-tier-allowlist-is-a-partial-net)
  - [Verdict](#verdict)
- [Interaction with the rest of the system](#interaction-with-the-rest-of-the-system)
- [Limitations and follow-ups](#limitations-and-follow-ups)
- [Verification](#verification)
- [See also](#see-also)

## The problem

Streaming generation requires both actors of a runtime reference to stream on the same
`RuntimeGrid`; otherwise one cell could load without the other and leave a dangling reference. When
the grids differ, the generator does not keep the authored values: outside the error-reporting
pass it calls `SetForcedNoRuntimeGrid()` on **both** actors, so the pair ends up on the grid they
inherit — whatever the data says — and MapCheck plus the submit-time
`WorldPartitionChangelistValidator` complain in the meantime.

The cause is almost always a rule boundary. `DA_SmallGrid_Rules` assigns `SmallGrid` to any actor
whose largest bounds dimension is under 100 uu; larger actors in the same Level Instance fall
through to `DA_NoneGrid_Rules` and are cleared to `None`. The boundary is drawn **by actor size**,
and a reference between a sub-metre actor and a larger one crosses it. That is exactly the shape
of the three errors on `LV_Overland` on 2026-10-05, all inside two Vault blockout Level Instances.

The existing answers are both partial:

- Tagging the actors `ExcludeFromRuntimeGridRules`, as changelist 2111842 did, freezes six actors
  and leaves the rule free to reproduce the family on the next actor someone places.
- [CL 2102948](EffectiveRuntimeGridReferenceValidation.md) stopped the *false positives* (`None`
  against the default grid) from being reported. It deliberately changed nothing about the real
  divergences, which is what is left.

## The rule

For every actor descriptor in a container, read `FWorldPartitionActorDesc::References`
(`TArray<FGuid>`). Group the actors those references connect. For each group, compute the resolved
RuntimeGrid of every member. If the group holds **more than one** resolved grid, pick the member
grid with the **largest cell size** and set it on every member that is not already on it — so the
whole cluster streams on one grid, the coarsest one it already contains.

A referencer with N references pulls all N referees into the same group, so acting on *both* actors
of every diverging reference, iterated, is the same as acting on the whole connected set at once —
which is what the pass does directly.

### Resolved grids, not authored names

The authored `RuntimeGrid` name is not what an actor streams on. Two things sit between them, and
both are applied before the comparison:

| Input | Resolution |
|-------|-----------|
| An actor inside a container that has a grid | Takes the **container's** grid. Every actor of such a container therefore resolves to one grid, so no cluster can diverge and the container is skipped outright |
| An attached actor, or an actor authored `None` | Follows its **attach parents**: the grid is the first non-`None` grid found walking up the attach chain. `None` when no parent has one — see below |

This is the same resolution CL 2102948 taught the engine validation, which is what makes the two
consistent: the pass only ever fires on divergences MapCheck still reports.

One consequence bounds the whole feature: **a cluster can only diverge inside a container whose own
resolved grid is `None`** — the main world, or a Level Instance with no grid. Any container that
carries a grid hands the same grid to all of its actors, so the scan over it finds nothing.

### Resolving `None` through attach parents

`None` is not a grid of its own. To compare it against a real grid the pass resolves it by walking
the actor's **attach parent chain**: an attached actor streams with its parent, so a `None` child
inherits the grid of the first parent that has one. The walk is bounded by the container's
descriptor count so a corrupted, cyclic chain cannot loop forever.

If no parent has a grid either, the actor resolves to `None`, and `None` is treated as **smaller
than any real grid** (cell size 0). So in a pairing of `None` against a named grid, the named grid
is always the larger one and the `None` actor is pulled onto it. A cluster whose only resolved grid
is `None` has no divergence and is left alone — every one of its actors already streams on the
default grid.

### Why the largest grid

The point of a runtime reference is that the referee must be resident whenever the referencer is.
The grid with the **largest cell size** also has the widest cells and, on this map, the longest
loading range, so putting both actors on it is the choice that guarantees co-residency: the finer
actor is pulled up to load as early and as widely as the coarser one, never the other way around.

It also keeps sub-worlds together in the common case. A reference from a sub-world Level Instance
(`HogwartsGrid`, `HogsmeadeGrid`) to a neighbour on `None` resolves to `None` = size 0, so the
sub-world grid wins and the neighbour is **pulled into the sub-world** rather than the sub-world
being dropped to the default grid. The reverse — a sub-world referencing a neighbour on a *coarser*
grid — is the one case that demotes it; see [Hogwarts and Hogsmeade](#hogwarts-and-hogsmeade).

### Clusters, not reference edges

MapCheck reports this error **per reference edge**, and the first Vault fix pass took the log at
face value: it aligned each referee onto its referencer. MapCheck then returned **8 errors instead
of 3**, because `BP_AstronomyPuzzle6` was also referenced both ways by four sibling puzzle actors.
Moving one actor out of a group only moves the boundary.

Taking the largest grid of *both* endpoints of every diverging edge does not have that failure
mode, but only if it is iterated to a fixpoint: aligning `A` and `B` onto their larger grid, then
`A` and `C`, propagates the largest grid of the whole connected set to every member. The pass
computes that directly, with a union-find over the reference graph, instead of iterating: **every
connected set holding more than one resolved grid is moved onto its single largest grid.** Same
result, one pass, and no intermediate state that a crash could leave behind.

A cluster is moved **whole or not at all**. A partial write is the 8-error state.

## Where the pass runs

It is part of `UWorldPartitionRuleBuilder` — the builder TeamCity runs nightly as
[Apply World Partition Rules](TeamCityJobs.md) — and runs **after** the per-actor rules of each
container, because it reads the grids those rules just wrote.

| Builder step | What the pass does |
|---|---|
| Main world, after pass 1 | Scans the map's own container. `InheritedRuntimeGrid` is `None`, so conflicts are possible |
| Each Level Instance, after its inner actors are processed | Scans the inner container with the grid the container inherits. `LI_Hogwarts` hands down `HogwartsGrid`, so the scan is skipped; `LI_Vault_Potion_01` hands down `None`, so it is scanned |
| `-ReportOnly` / `-ValidateOnly` | Conflicts are logged, nothing is checked out or saved |

The container grid is combined the way streaming generation inherits it: the outermost container
that declares a grid decides, and a container with none passes down what it was given.

Grids are ranked by cell size against the **map being built**, never against the level a Level
Instance happens to live in. A Level Instance with no grid of its own streams in the map's grids,
so its runtime hash is the top-level one throughout — see
[Limitations](#limitations-and-follow-ups) for the case where that distinction bites.

It deliberately does **not** run on the on-save path (`AutoApplyRulesOnActorSave`). Deciding one
actor's grid needs the whole container's reference graph and the grids of actors that are not
loaded, which is not work a save can do.

## Implementation

| File | Change |
|------|--------|
| `RuntimeGridReferenceConflictResolver.h/.cpp` | **New.** The detection, descriptor-only: nothing is loaded, checked out or saved |
| `WorldPartitionRuleBuilder.h/.cpp` | The new pass, its call sites and its counters |
| `RuntimeGridRuleSubsystem.h/.cpp` | `ApplyReferenceConflictRuntimeGrid` sets the actor's grid to the cluster's target grid; `IsExcludedFromRuntimeGridRules` exposes the ignore check so the pass can answer from a descriptor |
| `WorldPartitionRuleSettings.h` | The setting below |

Detection reads descriptors and returns one `FRuntimeGridReferenceConflict` per diverging cluster,
carrying the cluster, its distinct resolved grids, its **target grid** (the largest), the actors to
move, and — when it refuses to write — the reason. The grid of each actor is ranked by
`UWorldPartitionRuntimeHash::GetFixedGridInfo(GridName).CellSize`. The builder then loads only the
actors to move, through `ForEachActorWithLoading` with `Params.ActorGuids`, sets each one to its
cluster's target grid and saves.

Four things are kept out of the graph or out of the write:

- **Generated and custom HLOD actors** (`AWorldPartitionHLOD`, `AWorldPartitionCustomHLOD`). Their
  grid comes from their HLOD layer, written `Grid:Tier`, and is not rule-driven. This is the same
  carve-out CL 2102948 made in the engine check.
- **Editor-only references** (`GetEditorOnlyReferences`). They do not force two actors into the
  same cell.
- **Actors frozen against the RuntimeGrid rules** — the `ExcludeFromRuntimeGridRules` tag, the
  ignored type list, the ignored Outliner path list. A reference conflict does not get to overrule
  a human's freeze; the cluster is logged instead.
- **Moves that would strand an actor's HLOD layer.** When a member *carries* an HLOD layer, the
  pass asks the runtime hash `IsValidHLODLayer(TargetGrid, ActorHLODLayer)` before moving it; a
  layer the target grid's tiers do not accept would trade this error for an invalid-HLOD-layer
  error, so the cluster is logged and left alone. An actor with **no** HLOD layer has nothing to
  strand and is moved freely — which is what lets the current `None` ↔ `SmallGrid` population be
  fixed.

The whole scan is bounded by the reference graph of one container: a `TMap` of GUIDs with path
compression, no asset load, no HLOD layer load, no string work on the common path. Containers that
carry a grid cost nothing at all.

## Settings

On `UWorldPartitionRuleSettings` (`config = Editor`). The default is compiled in, so **no
`Config/DefaultEditor.ini` edit is needed** — which matters, because that file usually has several
people's pending edits in it.

| Setting | Default | Meaning |
|---|---|---|
| `bResolveRuntimeGridReferenceConflicts` | `true` | Run the pass at all |

The grid to write is not a setting: it is always the largest grid of the cluster, computed from the
runtime hash. There is no protected-grid list — see [Hogwarts and Hogsmeade](#hogwarts-and-hogsmeade)
for why the largest-grid rule removes the need for one in the common case, and where a residual risk
remains.

## Hogwarts and Hogsmeade

Short answer: **the pass is inert inside Hogwarts and Hogsmeade, and at the `LV_Overland` level the
largest-grid rule is safe in the common case but can still demote a sub-world** if it references a
neighbour on a coarser grid. The numbers below were measured live on the open `LV_Overland` on
2026-10-05, from the World Partition descriptors and the level's runtime hash.

### The grids `LV_Overland` declares

`LV_Overland` uses a `UWorldPartitionRuntimeHashSet` with six runtime partitions, and
`bRequiresExplicitHLODLayerAssignment` is **true**. Ranked by cell size — the metric the pass uses
to pick the largest grid:

| Rank | Partition | Cell size | Loading range |
|---|-----------|-----------|---------------|
| 1 | `FarWorldBitmap` | 762 m | 3048 m |
| 2 | `MainGrid` | 190.5 m | 256 m |
| 2 | `FarFoliageGrid` | 190.5 m | 1312 m |
| 4 | `HogwartsGrid` | 128 m | 256 m |
| 5 | `SmallGrid` | 38.1 m | 128 m |
| 6 | `HogsmeadeGrid` | 32 m | 64 m |
| — | `None` | 0 (not a grid) | resolves to the default grid, `MainGrid` |

`MainGrid` and `FarFoliageGrid` tie on cell size; the pass breaks the tie by name so the choice is
stable. `None` ranks below every real grid, so a `None` actor is always pulled onto its referee's
grid rather than the other way round.

### Who carries `HogwartsGrid` and `HogsmeadeGrid`

Of the 666 556 descriptors in `LV_Overland`, only 177 carry `HogwartsGrid` and 9 carry
`HogsmeadeGrid` (ignoring the generated HLOD actors, whose grid reads `HogwartsGrid:HW_Near` and
the like). They are all Level Instance or World Event Instance actors, and they sit at two levels:

- **One at the top of `LV_Overland` each**: `LI_Hogwarts` on `HogwartsGrid`, `LI_Hogsmeade` on
  `HogsmeadeGrid`. Those two actors are the whole sub-worlds.
- **The rest nested inside those two levels**: 157 Level Instances and 29 World Event Instances —
  `LI_SuspensionBridge_EXT`, `LI_DADATower_EXT`, `LI_QuadCourtyard_EXT`, the Hogsmeade
  `LI_WE_HM_*` events, and so on.

The top level of `LV_Overland` holds 104 974 actors on `None`, 4 563 on `MainGrid`, 2 812 on
`FarFoliageGrid`, 842 on `SmallGrid`, 15 on `FarWorldBitmap`, and exactly **one** on `HogwartsGrid`
and **one** on `HogsmeadeGrid`.

### Inside the sub-worlds the pass is inert

The containers of the two sub-worlds hold a mix of raw grid names that looks alarming:

| Container | Authored grids of its actors |
|---|---|
| `LI_Hogwarts` | `SmallGrid` 80, `HogwartsGrid` 37, `None` 31, `MainGrid` 2 |
| `LI_Hogsmeade` | `None` 810, `HogsmeadeGrid` 8 |

Four different names in one container, and `DA_HogwartsInteriorGrid_Rules` adds a deliberate split:
Hogwarts `_INT` content targets `SmallGrid` while the exterior targets `HogwartsGrid`.

None of it is a conflict, because `LI_Hogwarts` itself carries `HogwartsGrid` and `LI_Hogsmeade`
carries `HogsmeadeGrid`. Every actor in those containers resolves to the container's grid, so the
cluster of a reference holds one resolved grid however the names read. The pass skips both
containers without even building the graph. The same is true of every container nested inside them,
since the inherited grid is passed down.

This is confirmed from the other end: the 2026-10-05 MapCheck on `LV_Overland` reports three D5
errors and all three are in Vault Level Instances. If any reference inside Hogwarts or Hogsmeade
diverged after resolution, the engine check — which resolves the same way since CL 2102948 — would
already be reporting it.

### At the `LV_Overland` level the largest grid cuts both ways

The top-level container is where the only movement happens. `LI_Hogwarts` is one actor on
`HogwartsGrid` (rank 4) in a container of 105 000 actors that are on `None`, `MainGrid`,
`SmallGrid`, `FarFoliageGrid` or `FarWorldBitmap`. What a reference to it does now depends on the
neighbour's grid:

| Neighbour of `LI_Hogwarts` / `LI_Hogsmeade` | Largest grid | Effect |
|---|---|---|
| `None` (the common case: e.g. `LI_Hogsmeade_River` sits next to `LI_Hogsmeade` on `None`) | the sub-world grid | The neighbour is **pulled into the sub-world**. Hogwarts / Hogsmeade are left intact — the safe outcome |
| `SmallGrid` (for Hogwarts only) | `HogwartsGrid` | The neighbour joins Hogwarts. Hogwarts intact |
| `MainGrid`, `FarFoliageGrid`, `FarWorldBitmap` | the coarser grid | **The sub-world is demoted** onto the coarser grid, and with it all 157 nested Level Instances |
| Any named grid (for Hogsmeade, which is rank 6, the finest) | that grid | **Hogsmeade is demoted** — 32 m cells become the neighbour's, up to a six-fold coarsening |

So the largest-grid rule is the *right* default for the overwhelming majority of top-level
references, which are against `None`: it keeps the sub-world and absorbs the stray neighbour. The
residual danger is the reverse reference — a sub-world Level Instance referencing a neighbour that
is already on a coarser grid. `HogsmeadeGrid`, being the finest grid on the map, loses to every
named grid, so it is the most exposed.

No such reference exists today — again, MapCheck would be reporting it. The exposure is that nothing
in the pass prevents one from being authored, and when it is, a nightly build would silently move
the sub-world. There is no longer a protected-grid list standing in the way; if that guarantee is
wanted, re-adding a "never demote these grids" guard is the follow-up to make (see
[Limitations](#limitations-and-follow-ups)).

### The HLOD tier allowlist is a partial net

`bRequiresExplicitHLODLayerAssignment` is true on `LV_Overland`, so an HLOD layer that is not
assigned to a tier of the grid an actor resolves to is rejected at streaming generation. The layers
are partitioned strictly:

| Grid | HLOD layers its tiers accept |
|---|---|
| `MainGrid` | `LV_Overland_HLODLayer_Near`, `_Landscape_Near`, `_Far`, `_Water_Near`, `_Road_Near`, `_Landscape_Far2`, `_Water_Far`, `_Dummy` |
| `HogwartsGrid` | `LV_HW_HLODLayer_Near`, `_Mid`, `_Far`, `_Dummy` |
| `HogsmeadeGrid` | `LV_HM_HLODLayer_Near`, `_Far`, `_Foliage_Near`, `_Dummy` |
| `FarFoliageGrid` | `LV_FarFoliage_HLODLayer_Foliage_Mid`, `_Foliage_Far`, `_Dummy` |

When a member **carries** one of these layers, the pass refuses to move it onto a grid whose tiers
do not accept that layer: `IsValidHLODLayer(TargetGrid, ActorHLODLayer)` blocks the whole cluster
and logs it. That stops the pass from trading a D5 error for an invalid-HLOD-layer error whenever a
move would strand a layer — which catches most of the sub-world demotion cases, since sub-world
content carries sub-world layers.

It is **not** a complete net. A Level Instance actor often carries no HLOD layer of its own, and an
actor with no layer is moved freely by design (it is how the `None` ↔ `SmallGrid` Vault family gets
fixed). So the check does not, on its own, prevent a bare `LI_Hogsmeade` from being demoted — only
the absence of the offending reference does.

### Verdict

| Case | What happens |
|---|---|
| A reference inside Hogwarts or Hogsmeade | Nothing. The container's grid makes the cluster uniform |
| A top-level reference between `LI_Hogwarts` / `LI_Hogsmeade` and a `None` neighbour | The neighbour is pulled into the sub-world. Sub-world intact — the safe, common outcome |
| A top-level reference from a sub-world to a neighbour on a **coarser** grid | The sub-world is moved onto that grid. Caught only if the sub-world actor carries a strand-able HLOD layer; otherwise silent |
| A `None` ↔ `SmallGrid` reference anywhere else — the Vault family | Moved onto `SmallGrid`, the larger of the two. The `None` actors carry no HLOD layer, so nothing blocks it |

## Interaction with the rest of the system

- **The rules and the pass run in the same build.** The RuntimeGrid rules write `SmallGrid` on a
  small actor and `None` on its larger neighbour; the pass then moves the neighbour onto `SmallGrid`
  because of the reference. The end state on disk is stable, so the next nightly run produces the
  same bytes and submits nothing. What it does cost is reloading and resaving those actors each
  night; if that shows up, the durable fix is a rule-level exclusion, as the Vault audit
  [proposed for the Vault blockout content](../Audits/MapCheckRuntimeGridReferences-Vault-2026-10-05.md#follow-up-exclude-the-vault-blockout-content-from-da_smallgrid_rules).
- **Saving one actor in the editor can reopen a conflict.** The on-save rules will put `None` back
  on a neighbour the pass had moved, because they look at one actor. MapCheck will report it again
  until the next builder run.
- **`ExcludeFromRuntimeGridRules` wins.** An actor carrying the tag is never rewritten, and its
  cluster is reported instead. The six actors tagged by changelist 2111842 are therefore left
  exactly as they are.
- **CL 2102948 is a prerequisite in spirit.** Without the effective-grid resolution the engine
  check reports `None` against `MainGrid`; this pass resolves the same way, so the two agree about
  what a real divergence is.
- **An HLOD rebuild may be needed.** Unlike the previous clear-to-`None` design, moving a cluster
  onto a named grid can change which cells and HLODs its actors land in. For the `None` ↔ `SmallGrid`
  population the actors are tiny and carry no HLOD layer, so the impact is small, but this should be
  confirmed on the first real run.

## Limitations and follow-ups

- **No protected-grid guard.** The largest-grid rule keeps sub-worlds in the common case, but a
  sub-world referencing a coarser-grid neighbour is demoted with no block unless an HLOD layer
  happens to catch it. If a hard guarantee is wanted, re-add a configurable "grids that are never
  demoted" list (`HogwartsGrid`, `HogsmeadeGrid`, `FarFoliageGrid`, `FarWorldBitmap`) and log those
  clusters instead of moving them. This was in an earlier revision and was removed with this logic
  change; it can come back as a pure safety net.
- **A level opened as its own world resolves differently.** Grids are ranked against the world being
  processed. Running the builder directly on `/Game/Levels/Overland/Hogwarts/LI_Hogwarts` makes it
  a main world: its container grid becomes `None`, its four authored grid names start to diverge,
  and the pass would move clusters around inside it. The `IsValidHLODLayer` check stops moves that
  would strand a layer, but **the builder should only be pointed at the top-level map**, and this is
  the reason why. The same caveat applies to the isolated per-level phase of
  [`Editor.ScanRuntimeGridReferenceErrors`](CustomTools/RuntimeGridReferenceTools.md).
- **Cross-container references are out of scope.** A reference is resolved in the referencer's own
  container; one that points elsewhere is handled by the container's grid and never produces a
  mismatch here. This matches the engine check.
- **Custom HLOD actors keep the raw behaviour**, as in CL 2102948: their grid comes from an HLOD
  layer that is not resolved at this point, and loading it to find out is too expensive.
- **Cell size, not loading range, ranks the grids.** The two orderings mostly agree, but
  `FarFoliageGrid` has a far longer loading range than `MainGrid` at the same cell size. The tie is
  broken by name; a cluster mixing those two is not expected, but worth knowing.
- **Rule conditions still read the raw grid.** A WorldPartition rule condition on RuntimeGrid
  (`bUseRuntimeGrid`) compares the authored name, so a `None` actor does not match a `MainGrid`
  condition even though it streams there.
- **Worth measuring**: how many clusters the pass finds across a full `LV_Overland` run, which grid
  each lands on, and how many it refuses. A `-ReportOnly` run answers all three without writing.

## Verification

The changelist compiles; it has not been exercised yet. The order to test it in:

1. **Report first.** Run the builder with `-RuntimeGridRules -ReportOnly` on `LV_Overland` and read
   the `RuntimeGrid references:` summary line and the per-cluster log lines. Nothing is written.
   Expected: the three Vault clusters moved onto `SmallGrid`, and whatever else the level is hiding.
2. **Check the refusals.** Every line that says *left as is* should name an excluded actor or an
   HLOD layer — never something unexplained. Watch in particular for any sub-world being named as a
   target's *source*: a `HogwartsGrid` or `HogsmeadeGrid` cluster being moved is the demotion case.
3. **Then a real run**, scoped with `-ContainOutlinerPathSubstrings=LI_Vault` so the first write
   touches only the known population, and read the changelist it produces before submitting.
4. **MapCheck on `LV_Overland`**: 3 errors → 0. Compare the generated streaming and HLODs against
   the baseline to see whether a rebuild is needed.
5. **Run it twice.** The second run must find the same clusters and save nothing, which is what
   proves the end state is a fixpoint rather than a ping-pong with the rules.

## See also

- [Fixing MapCheck issues — D5](FixingMapCheckIssues.md#d5--actor-references-an-actor-in-a-different-runtime-grid)
  — the playbook entry for the message this pass removes
- [MapCheck runtime-grid references — Vault, 2026-10-05](../Audits/MapCheckRuntimeGridReferences-Vault-2026-10-05.md)
  — the audit that established the cluster-not-edge rule and the manual fix this replaces
- [Effective RuntimeGrid reference validation](EffectiveRuntimeGridReferenceValidation.md) — CL
  2102948, the engine-side resolution this pass mirrors
- [Runtime Grid rules](WorldPartitionRulesAnalysis/RuntimeGridRules.md) — the rules that draw the
  boundary, `DA_SmallGrid_Rules` in particular
- [Exclude From Rules tag](CustomTools/ExcludeFromRulesTag.md) — the per-actor freeze the pass obeys
- [TeamCity jobs](TeamCityJobs.md) — the nightly builder this pass runs inside
- [World Partition streaming properties](WorldPartitionStreamingProperties.md) — RuntimeGrid and
  its inheritance
