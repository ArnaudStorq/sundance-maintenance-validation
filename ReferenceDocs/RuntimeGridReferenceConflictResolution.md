Parent: [Reference Docs](README.md)

# RuntimeGrid reference conflict resolution

A new pass of the World Partition rule system. While the RuntimeGrid rules run, it reads each
actor's descriptor references, compares the **resolved** RuntimeGrid of the actors a reference
connects, and when they disagree it moves the whole reference cluster onto `MainGrid`.

It exists because the
    10|[D5 MapCheck error](FixingMapCheckIssues.md#d5--actor-references-an-actor-in-a-different-runtime-grid)
— *"actor references an actor in a different runtime grid"* — is produced **by the rules
themselves**: they assign grids per actor, from size and Outliner path, while references ignore
both. Repairing it actor by actor, as the
[Vault audit](../Audits/MapCheckRuntimeGridReferences-Vault-2026-10-05.md) did, treats the symptom
and the nightly builder puts the divergence back. This pass makes the rule pass itself close the
hole it opens.

- **Changelist**: **2112721** (pending, `//sun/Dev`), description
  `WP Rules: force reference clusters with diverging resolved RuntimeGrid onto MainGrid`.
    20|- **Module**: `WorldBuildingEditor` — `D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\`.
- **Status**: compiles clean against the module's own options (shared PCH, MSVC 14.50, `/W4 /WX`).
  Not yet run through the builder: see [Verification](#verification).

## Contents

- [The problem](#the-problem)
- [The rule](#the-rule)
  - [Resolved grids, not authored names](#resolved-grids-not-authored-names)
  - [Clusters, not reference edges](#clusters-not-reference-edges)
    30|  - [Why `MainGrid`](#why-maingrid)
- [Where the pass runs](#where-the-pass-runs)
- [Implementation](#implementation)
- [Settings](#settings)
- [Hogwarts and Hogsmeade](#hogwarts-and-hogsmeade)
  - [The grids `LV_Overland` declares](#the-grids-lv_overland-declares)
  - [Who carries `HogwartsGrid` and `HogsmeadeGrid`](#who-carries-hogwartsgrid-and-hogsmeadegrid)
  - [Inside the sub-worlds the pass is inert](#inside-the-sub-worlds-the-pass-is-inert)
  - [At the `LV_Overland` level the blast radius is the whole sub-world](#at-the-lv_overland-level-the-blast-radius-is-the-whole-sub-world)
  - [The HLOD tier allowlist turns a demotion into a second error](#the-hlod-tier-allowlist-turns-a-demotion-into-a-second-error)
    40|  - [Verdict and the protected-grid list](#verdict-and-the-protected-grid-list)
- [Interaction with the rest of the system](#interaction-with-the-rest-of-the-system)
- [Limitations and follow-ups](#limitations-and-follow-ups)
- [Verification](#verification)
- [See also](#see-also)

## The problem

Streaming generation requires both actors of a runtime reference to stream on the same
`RuntimeGrid`; otherwise one cell could load without the other and leave a dangling reference. When
    50|the grids differ, the generator does not keep the authored values: outside the error-reporting
pass it calls `SetForcedNoRuntimeGrid()` on **both** actors, so the pair ends up on the default
grid whatever the data says.

Two things therefore happen at once when this error appears: MapCheck and the submit-time
`WorldPartitionChangelistValidator` complain, **and** the grid someone authored is already being
ignored.

The cause is almost always a rule boundary. `DA_SmallGrid_Rules` assigns `SmallGrid` to any actor
whose largest bounds dimension is under 100 uu; larger actors in the same Level Instance fall
through to `DA_NoneGrid_Rules` and are cleared to `None`. The boundary is drawn **by actor size**,
    60|and a reference between a sub-metre actor and a larger one crosses it. That is exactly the shape
of the three errors on `LV_Overland` on 2026-10-05, all inside two Vault blockout Level Instances.

The existing answers are both partial:

- Tagging the actors `ExcludeFromRuntimeGridRules`, as changelist 2111842 did, freezes six actors
  and leaves the rule free to reproduce the family on the next actor someone places.
- [CL 2102948](EffectiveRuntimeGridReferenceValidation.md) stopped the *false positives* (`None`
  against the default grid) from being reported. It deliberately changed nothing about the real
  divergences, which is what is left.

    70|## The rule

For every actor descriptor in a container, read `FWorldPartitionActorDesc::References`
(`TArray<FGuid>`). Group the actors those references connect. For each group, compute the resolved
RuntimeGrid of every member. If the group holds **more than one** resolved grid, write `MainGrid`
on every member that is not already on it.

### Resolved grids, not authored names

The authored `RuntimeGrid` name is not what an actor streams on. Three things sit between them, and
all three are applied before the comparison:

    80|| Input | Resolution |
|-------|-----------|
| `None` | Not a grid of its own. The runtime hash streams the actor on its **first runtime partition** (`UWorldPartitionRuntimeHashSet::GetDefaultGrid()`), which is `MainGrid` on `LV_Overland` |
| An actor inside a container that has a grid | Takes the **container's** grid. The override that would let it keep its own (`wp.RuntimeGrid.AllowUnreferencedActorOverride`) is granted only to actors that share no reference cluster, and every actor this pass looks at is in one |
| An attached actor | Follows its **attach parent**: `GetRuntimeGrid()` returns the parent's grid. The pass resolves the chain to its root and writes on the root, since writing on the child would be inert |

This is the same resolution CL 2102948 taught the engine validation, which is what makes the two
consistent: the pass only ever fires on divergences MapCheck still reports.

One consequence is worth stating because it bounds the whole feature: **a cluster can only diverge
inside a container whose own resolved grid is `None`** — the main world, or a Level Instance with
    90|no grid. Any container that carries a grid hands the same grid to all of its actors, so the scan
over it finds nothing and is skipped outright.

### Clusters, not reference edges

MapCheck reports this error **per reference edge**, and the first Vault fix pass took the log at
face value: it aligned each referee onto its referencer. MapCheck then returned **8 errors instead
of 3**, because `BP_AstronomyPuzzle6` was also referenced both ways by four sibling puzzle actors.
Moving one actor out of a group only moves the boundary.

Forcing both endpoints of every diverging edge onto one fixed grid does not have that failure mode,
   100|but only if it is iterated to a fixpoint: if `A` moves to `MainGrid` and `A` also references `B`
on `SmallGrid`, that edge now diverges and `B` must move too. The fixpoint of the per-edge rule is
therefore exactly *"every connected set holding more than one resolved grid becomes entirely
`MainGrid`"*. The pass computes that directly, with a union-find over the reference graph, instead
of iterating. Same result, one pass, and no intermediate state that a crash could leave behind.

A cluster is also realigned **whole or not at all**. A partial write is the 8-error state.

### Why `MainGrid`

`MainGrid` is `RuntimePartitions(0)` on `LV_Overland`, so it is the grid the hash already resolves
`None` to, and it is the grid `SetForcedNoRuntimeGrid()` already puts the diverging pair on. For
   110|the `None` ↔ `SmallGrid` conflicts that make up the whole current population of this error, the
pass therefore writes down what the generated streaming already does: the cells, the actor sets and
the HLODs do not change, and **no HLOD rebuild is needed**.

It is not a free choice for every conflict, though — `MainGrid` cells are 190.5 m against
`SmallGrid`'s 38.1 m, and coarser still against the sub-world grids. That is the whole subject of
[Hogwarts and Hogsmeade](#hogwarts-and-hogsmeade) below, and the reason for the protected-grid
list.

## Where the pass runs

It is part of `UWorldPartitionRuleBuilder` — the builder TeamCity runs nightly as
   120|[Apply World Partition Rules](TeamCityJobs.md) — and runs **after** the per-actor rules of each
container, because it reads the grids those rules just wrote.

| Builder step | What the pass does |
|---|---|
| Main world, after pass 1 | Scans the map's own container. `InheritedRuntimeGrid` is `None`, so conflicts are possible |
| Each Level Instance, after its inner actors are processed | Scans the inner container with the grid the container inherits. `LI_Hogwarts` hands down `HogwartsGrid`, so the scan is skipped; `LI_Vault_Potion_01` hands down `None`, so it is scanned |
| `-ReportOnly` / `-ValidateOnly` | Conflicts are logged, nothing is checked out or saved |

The container grid is combined the way streaming generation inherits it: the outermost container
that declares a grid decides, and a container with none passes down what it was given.

   130|`None` is always resolved against the **map being built**, never against the level a Level Instance
happens to live in. A Level Instance with no grid of its own streams in the map's grids, so reading
the default grid from its own level would resolve `None` to the wrong partition — see
[Limitations](#limitations-and-follow-ups) for the case where that distinction bites.

It deliberately does **not** run on the on-save path (`AutoApplyRulesOnActorSave`). Deciding one
actor's grid needs the whole container's reference graph and the grids of actors that are not
loaded, which is not work a save can do.

## Implementation

| File | Change |
   140||------|--------|
| `RuntimeGridReferenceConflictResolver.h/.cpp` | **New.** The detection, descriptor-only: nothing is loaded, checked out or saved |
| `WorldPartitionRuleBuilder.h/.cpp` | The new pass, its call sites and its counters |
| `RuntimeGridRuleSubsystem.h/.cpp` | `ApplyReferenceConflictRuntimeGrid` writes the grid; `IsExcludedFromRuntimeGridRules` exposes the ignore check so the pass can answer from a descriptor |
| `WorldPartitionRuleSettings.h` | The three settings below |

Detection reads descriptors and returns one `FRuntimeGridReferenceConflict` per diverging cluster,
carrying the cluster, the distinct resolved grids, the actors to realign, and — when it refuses to
write — the reason. The builder then loads only the actors to realign, through
`ForEachActorWithLoading` with `Params.ActorGuids`, writes the grid and saves.

   150|Four things are kept out of the graph or out of the write:

- **Generated and custom HLOD actors** (`AWorldPartitionHLOD`, `AWorldPartitionCustomHLOD`). Their
  grid comes from their HLOD layer, written `Grid:Tier`, and is not rule-driven. This is the same
  carve-out CL 2102948 made in the engine check.
- **Editor-only references** (`GetEditorOnlyReferences`). They do not force two actors into the
  same cell.
- **Actors frozen against the RuntimeGrid rules** — the `ExcludeFromRuntimeGridRules` tag, the
  ignored type list, the ignored Outliner path list. A reference conflict does not get to overrule
  a human's freeze; the cluster is logged instead.
- **Targets the map would reject.** Before writing, the pass asks the runtime hash
   160|  `IsValidGrid(MainGrid, ActorClass)` and `IsValidHLODLayer(MainGrid, ActorHLODLayer)`. A grid the
  map does not declare, or one whose HLOD tiers do not accept the actor's layer, would trade this
  error for a different streaming-generation error, so the cluster is logged and left alone.

The whole scan is bounded by the reference graph of one container: a `TMap` of GUIDs with path
compression, no asset load, no HLOD layer load, no string work on the common path. Containers that
carry a grid cost nothing at all.

## Settings

On `UWorldPartitionRuleSettings` (`config = Editor`). The defaults are compiled in, so **no
`Config/DefaultEditor.ini` edit is needed** — which matters, because that file usually has several
   170|people's pending edits in it.

| Setting | Default | Meaning |
|---|---|---|
| `bResolveRuntimeGridReferenceConflicts` | `true` | Run the pass at all |
| `ReferenceConflictTargetRuntimeGrid` | `MainGrid` | Grid a diverging cluster is moved to |
| `RuntimeGridsProtectedFromReferenceConflicts` | `HogwartsGrid`, `HogsmeadeGrid`, `FarFoliageGrid`, `FarWorldBitmap` | Grids a cluster is never moved **off**. The conflict is logged for a human instead |

## Hogwarts and Hogsmeade

Short answer: **the pass is inert inside Hogwarts and Hogsmeade, and without the protected-grid
list it would be catastrophic at the `LV_Overland` level** — a single reference is enough to demote
   180|an entire sub-world onto `MainGrid`. The numbers below were measured live on the open
`LV_Overland` on 2026-10-05, from the World Partition descriptors and the level's runtime hash.

### The grids `LV_Overland` declares

`LV_Overland` uses a `UWorldPartitionRuntimeHashSet` with six runtime partitions, and
`bRequiresExplicitHLODLayerAssignment` is **true**:

| # | Partition | Cell size | Loading range |
|---|-----------|-----------|---------------|
| 0 | `MainGrid` | 190.5 m | 256 m |
| 1 | `SmallGrid` | 38.1 m | 128 m |
   190|| 2 | `HogsmeadeGrid` | 32 m | 64 m |
| 3 | `HogwartsGrid` | 128 m | 256 m |
| 4 | `FarFoliageGrid` | 190.5 m | 1312 m |
| 5 | `FarWorldBitmap` | 762 m | 3048 m |

Partition 0 is `MainGrid`, which is what makes it the default grid and the target of this pass.

### Who carries `HogwartsGrid` and `HogsmeadeGrid`

Of the 666 556 descriptors in `LV_Overland`, only 177 carry `HogwartsGrid` and 9 carry
`HogsmeadeGrid` (ignoring the generated HLOD actors, whose grid reads `HogwartsGrid:HW_Near` and
the like). They are all Level Instance or World Event Instance actors, and they sit at two levels:
   200|
- **One at the top of `LV_Overland` each**: `LI_Hogwarts` on `HogwartsGrid`, `LI_Hogsmeade` on
  `HogsmeadeGrid`. Those two actors are the whole sub-worlds.
- **The rest nested inside those two levels**: 157 Level Instances and 29 World Event Instances —
  `LI_SuspensionBridge_EXT`, `LI_DADATower_EXT`, `LI_QuadCourtyard_EXT`, the Hogsmeade
  `LI_WE_HM_*` events, and so on.

The top level of `LV_Overland` holds 104 974 actors on `None`, 4 563 on `MainGrid`, 2 812 on
`FarFoliageGrid`, 842 on `SmallGrid`, 15 on `FarWorldBitmap`, and exactly **one** on `HogwartsGrid`
and **one** on `HogsmeadeGrid`.

   210|### Inside the sub-worlds the pass is inert

The containers of the two sub-worlds hold a mix of raw grid names that looks alarming:

| Container | Authored grids of its actors |
|---|---|
| `LI_Hogwarts` | `SmallGrid` 80, `HogwartsGrid` 37, `None` 31, `MainGrid` 2 |
| `LI_Hogsmeade` | `None` 810, `HogsmeadeGrid` 8 |

Four different names in one container, and `DA_HogwartsInteriorGrid_Rules` adds a deliberate split:
Hogwarts `_INT` content targets `SmallGrid` while the exterior targets `HogwartsGrid`.

   220|None of it is a conflict, because `LI_Hogwarts` itself carries `HogwartsGrid` and `LI_Hogsmeade`
carries `HogsmeadeGrid`. Every actor in those containers resolves to the container's grid, so the
cluster of a reference holds one resolved grid however the names read. The pass skips both
containers without even building the graph. The same is true of every container nested inside them,
since the inherited grid is passed down.

This is confirmed from the other end: the 2026-10-05 MapCheck on `LV_Overland` reports three D5
errors and all three are in Vault Level Instances. If any reference inside Hogwarts or Hogsmeade
diverged after resolution, the engine check — which resolves the same way since CL 2102948 — would
already be reporting it.

   230|### At the `LV_Overland` level the blast radius is the whole sub-world

The top-level container is where the danger is. `LI_Hogwarts` is one actor on `HogwartsGrid` in a
container of 105 000 actors that are on `None`, `MainGrid`, `SmallGrid`, `FarFoliageGrid` or
`FarWorldBitmap`. **Any** runtime reference between `LI_Hogwarts` and any of its neighbours is a
divergence by this rule's definition, and the repair would write `MainGrid` on `LI_Hogwarts`.

Because a container's grid is inherited by everything inside it, that single write moves the entire
Hogwarts — all 157 nested Level Instances and every actor under them — from 128 m cells to 190.5 m
cells. For Hogsmeade it is worse: 32 m cells and a 64 m loading range become 190.5 m and 256 m, a
six-fold coarsening of a dense town. And `LI_Hogsmeade_River` sits right next to `LI_Hogsmeade` at
   240|the top level on `None`, so the two are one reference apart from exactly this.

No such reference exists today — again, MapCheck would be reporting it. The exposure is that
nothing prevents one from being authored, and when it is, the rule pass would silently rewrite the
streaming of a whole district in a nightly build.

### The HLOD tier allowlist turns a demotion into a second error

`bRequiresExplicitHLODLayerAssignment` is true on `LV_Overland`, so an HLOD layer that is not
assigned to a tier of the target grid is rejected at streaming generation. The layers are
partitioned strictly:

   250|| Grid | HLOD layers its tiers accept |
|---|---|
| `MainGrid` | `LV_Overland_HLODLayer_Near`, `_Landscape_Near`, `_Far`, `_Water_Near`, `_Road_Near`, `_Landscape_Far2`, `_Water_Far`, `_Dummy` |
| `HogwartsGrid` | `LV_HW_HLODLayer_Near`, `_Mid`, `_Far`, `_Dummy` |
| `HogsmeadeGrid` | `LV_HM_HLODLayer_Near`, `_Far`, `_Foliage_Near`, `_Dummy` |
| `FarFoliageGrid` | `LV_FarFoliage_HLODLayer_Foliage_Mid`, `_Foliage_Far`, `_Dummy` |

So moving a Hogwarts, Hogsmeade or far-foliage actor to `MainGrid` does not only change its cells:
its HLOD layer stops being valid on the grid it lands on. The repair would trade a D5 error for an
invalid-HLOD-layer error and a `Skipped RuntimeGrid override` warning — and this time an HLOD
rebuild would be required.

   260|The pass refuses that trade on its own, per actor, through `IsValidHLODLayer`. The protected-grid
list is the coarser guard that stops the question from being asked at all.

### Verdict and the protected-grid list

| Case | What happens |
|---|---|
| A reference inside Hogwarts or Hogsmeade | Nothing. The container's grid makes the cluster uniform |
| A reference between `LI_Hogwarts` / `LI_Hogsmeade` and anything else at the top of `LV_Overland` | Logged as a conflict on a protected grid, and **left alone**. This is the decision the pass refuses to take |
| A `None` ↔ `SmallGrid` reference anywhere else — the Vault family | Realigned onto `MainGrid`, which is what streaming generation already forces |

`HogwartsGrid` and `HogsmeadeGrid` are protected because demoting them is a streaming design
   270|decision with a six-fold cell change and an HLOD rebuild behind it, not a repair a nightly builder
may take. `FarFoliageGrid` and `FarWorldBitmap` are protected for the same reason: their content
exists precisely to stream at very long range, and their HLOD layers live only on their own tiers.

That leaves `None`, `MainGrid` and `SmallGrid` as the grids the pass actually arbitrates — which is
the entire population of the error family seen so far.

## Interaction with the rest of the system

- **The rules and the pass run in the same build.** The RuntimeGrid rules write `SmallGrid` on a
  small actor, then the pass writes `MainGrid` on it because of its references. The end state on
  disk is stable, so the next nightly run produces the same bytes and submits nothing. What it does
   280|  cost is reloading and resaving those actors each night; if that shows up, the durable fix is a
  rule-level exclusion, as the Vault audit
  [proposed for the Vault blockout content](../Audits/MapCheckRuntimeGridReferences-Vault-2026-10-05.md#follow-up-exclude-the-vault-blockout-content-from-da_smallgrid_rules).
- **Saving one actor in the editor can reopen a conflict.** The on-save rules will put `SmallGrid`
  back on an actor the pass had moved, because they look at one actor. MapCheck will report it
  again until the next builder run.
- **`ExcludeFromRuntimeGridRules` wins.** An actor carrying the tag is never rewritten, and its
  cluster is reported instead. The six actors tagged by changelist 2111842 are therefore left
  exactly as they are, and the pass reports their clusters rather than quietly disagreeing with
  them.
   290|- **CL 2102948 is a prerequisite in spirit.** Without the effective-grid resolution the engine
  check reports `None` against `MainGrid`; this pass resolves the same way, so the two agree about
  what a real divergence is.
- **No HLOD rebuild** for the conflicts the pass actually fixes: forcing the cluster onto the
  default grid is what generation already does for it.

## Limitations and follow-ups

- **A level opened as its own world resolves differently.** `None` resolves against the world being
  processed. Running the builder directly on `/Game/Levels/Overland/Hogwarts/LI_Hogwarts` makes it
  a main world: its container grid becomes `None`, its four authored grid names start to diverge,
   300|  and the pass would want to rewrite around 150 actors. The protected-grid list stops the Hogwarts
  and Hogsmeade cases, and the `IsValidGrid` check stops a `MainGrid` write into a world that does
  not declare that partition — but **the builder should only be pointed at the top-level map**, and
  this is the reason why. The same caveat applies to the isolated per-level phase of
  [`Editor.ScanRuntimeGridReferenceErrors`](CustomTools/RuntimeGridReferenceTools.md).
- **Cross-container references are out of scope.** A reference is resolved in the referencer's own
  container; one that points elsewhere is handled by the container's grid and never produces a
  mismatch here. This matches the engine check.
- **Custom HLOD actors keep the raw behaviour**, as in CL 2102948: their grid comes from an HLOD
  layer that is not resolved at this point, and loading it to find out is too expensive.
   310|- **A protected cluster stays broken.** The MapCheck error remains and a human has to decide:
  align the neighbour onto the sub-world grid, exclude the content from the rule that split it, or
  accept the demotion. The log line names the cluster, its grids and the reason.
- **Rule conditions still read the raw grid.** A WorldPartition rule condition on RuntimeGrid
  (`bUseRuntimeGrid`) compares the authored name, so a `None` actor does not match a `MainGrid`
  condition even though it streams there.
- **Worth measuring**: how many clusters the pass finds across a full `LV_Overland` run, and how
  many it refuses. A `-ReportOnly` run answers both without writing anything.

## Verification

   320|The changelist compiles; it has not been exercised yet. The order to test it in:

1. **Report first.** Run the builder with `-RuntimeGridRules -ReportOnly` on `LV_Overland` and read
   the `RuntimeGrid references:` summary line and the per-cluster log lines. Nothing is written.
   Expected: the three Vault clusters, and whatever else the level is hiding.
2. **Check the refusals.** Every line that says *left as is* should name a protected grid, an
   excluded actor or an HLOD layer — never something unexplained.
3. **Then a real run**, scoped with `-ContainOutlinerPathSubstrings=LI_Vault` so the first write
   touches only the known population, and read the changelist it produces before submitting.
4. **MapCheck on `LV_Overland`**: 3 errors → 0, with the warning list unchanged against the
   baseline. The generated streaming should be identical, so no HLOD rebuild.
   330|5. **Run it twice.** The second run must find the same clusters and save nothing, which is what
   proves the end state is a fixpoint rather than a ping-pong with the rules.

## See also

- [Fixing MapCheck issues — D5](FixingMapCheckIssues.md#d5--actor-references-an-actor-in-a-different-runtime-grid)
  — the playbook entry for the message this pass removes
- [MapCheck runtime-grid references — Vault, 2026-10-05](../Audits/MapCheckRuntimeGridReferences-Vault-2026-10-05.md)
  — the audit that established the cluster-not-edge rule, and the manual fix this replaces
- [Effective RuntimeGrid reference validation](EffectiveRuntimeGridReferenceValidation.md) — CL
  2102948, the engine-side resolution this pass mirrors
   340|- [Runtime Grid rules](WorldPartitionRulesAnalysis/RuntimeGridRules.md) — the rules that draw the
  boundary, `DA_SmallGrid_Rules` in particular
- [Exclude From Rules tag](CustomTools/ExcludeFromRulesTag.md) — the per-actor freeze the pass obeys
- [TeamCity jobs](TeamCityJobs.md) — the nightly builder this pass runs inside
- [World Partition streaming properties](WorldPartitionStreamingProperties.md) — RuntimeGrid and
  its inheritance
