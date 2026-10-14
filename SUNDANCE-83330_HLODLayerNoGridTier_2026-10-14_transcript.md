# SUNDANCE-83330 — HLOD layer with no tier on its effective runtime grid (investigation + action)

- **Ticket**: [SUNDANCE-83330](https://wbg-avalanche.atlassian.net/browse/SUNDANCE-83330) —
  *Warn when an actor's HLOD layer has no tier on its effective runtime grid*
- **Date**: 2026-10-14
- **Sources**: a Cursor investigation session (reproduction + how to read the source
  actors of an orphan HLOD actor) and Phil's screen-share
  `Phil_Explique_HWGrid_VS_MainGrid.mp4` (HogwartsGrid vs MainGrid, where to add the
  warning).
- **Participants**: Arnaud; Philippe St-Jean (World Partition rules owner) in the video.
- **Related**:
  [World Partition streaming properties](ReferenceDocs/WorldPartitionStreamingProperties.md),
  [HLOD Layer rules](ReferenceDocs/WorldPartitionRulesAnalysis/HLODLayerRules.md),
  [HLOD Layer target assets](ReferenceDocs/WorldPartitionRulesAnalysis/HLODLayerTargetAssets.md),
  [Builders & commandlets](ReferenceDocs/BuildersAndCommandlets.md),
  [Quidditch runtime-grid sync (2026-09-21)](SyncWithPierreLuc_2026-09-21_QuidditchRuntimeGridIssue_transcript.md).

## Contents

- [The bug in one paragraph](#the-bug-in-one-paragraph)
- [What a "tier" is](#what-a-tier-is)
- [Reproduction from the editor / PIE](#reproduction-from-the-editor--pie)
- [Where the tier to grid mapping actually lives](#where-the-tier-to-grid-mapping-actually-lives)
- [The Streaming List View (ImGui tool)](#the-streaming-list-view-imgui-tool)
- [How the four names relate](#how-the-four-names-relate)
- [Reading the source actors of an HLOD actor](#reading-the-source-actors-of-an-hlod-actor)
- [Phil's video — HogwartsGrid vs MainGrid](#phils-video--hogwartsgrid-vs-maingrid)
- [Action: implement the warning in WorldPartitionRuleBuilder.cpp](#action-implement-the-warning-in-worldpartitionrulebuildercpp)

---

## The bug in one paragraph

A spatially loaded, HLOD-relevant actor uses an HLOD layer that has **no tier on its
effective runtime grid** (the grid it ends up on after Level Instance inheritance and
RuntimeGrid rules). When that happens the HLOD builder gives the HLOD actor
`RuntimeGrid = None` and `SpatiallyLoaded = false`, so the proxy streams in **everywhere,
all the time**, in a cell marked `IsHLOD = F`. Nothing reports it today: the engine check
for `bRequireExplicitHLODLayerPartitionAssignation` is compiled out
(`ValidateContainerInstanceDescriptor` is only called under `#if 0` in
`WorldPartitionStreamingGeneration.cpp`).

Real example from the ticket: `LI_QuidditchPitch_Section_A`'s source actors stream on
**MainGrid** but carry **`LV_HW_HLODLayer_Near`**, which only has a tier under
**HogwartsGrid**. Result: the HLOD actor
`LV_HW_HLODLayer_Near/MainGrid_L1_X-2_Y-1_Z0_d8F1A3152` with no grid, loaded all the time.
On `LV_Overland` this is behind the **182** unexpected `None`-grid HLOD actors (13 HW_Near,
12 HM_Near, 157 Dummy).

## What a "tier" is

A **tier** is one level of an HLOD Layer chain (near → mid → far). Each tier is attached to
a **runtime grid** and a **loading range** inside the map's runtime hash. A tier with no
matching grid means the HLOD builder has nowhere to place the proxy, so the HLOD becomes an
orphan (`RuntimeGrid = None`).

## Reproduction from the editor / PIE

1. Open `LV_Overland` in the editor.
2. In the Outliner find `LI_QuidditchPitch_Section_A` (source actors, e.g.
   `StaticMeshActor_50`). In **Details → World Partition**: effective `RuntimeGrid =
   MainGrid` (authored `None`, inherited to `MainGrid`), `HLODLayer =
   LV_HW_HLODLayer_Near`.
3. **Build → Build HLODs** to run streaming generation.
4. In the Outliner find the HLOD actor
   `LV_HW_HLODLayer_Near/MainGrid_L1_X-2_Y-1_Z0_d8F1A3152`: `RuntimeGrid = None`,
   `SpatiallyLoaded = false`.
5. Confirm in PIE: the proxy never unloads (its cell is always loaded).
6. **Build → Map Check** emits **no** warning for this case.

## Where the tier to grid mapping actually lives

**Not** on the `UHLODLayer` asset. Opening `LV_HW_HLODLayer_Near` only shows how the proxy
is built (`Layer Type`, `Parent Layer`, `HLOD Actor Class`, `Minimum Extent`, …). The
tier ↔ grid link lives in the map's **RuntimeHashSet**:

```414:417:D:\Sun\Engine\Source\Runtime\Engine\Private\WorldPartition\RuntimeHashSet\WorldPartitionRuntimeHashSet.cpp
bool UWorldPartitionRuntimeHashSet::IsValidHLODLayer(FName GridName, const FSoftObjectPath& HLODLayerPath) const
{
	return ResolveRuntimePartitionForHLODLayer(GridName, HLODLayerPath) != nullptr;
}
```

To see it in the editor: **Window → World Settings → World Partition → World Partition
Setup (RuntimeHashSet) → Runtime Partitions**. Expand `HogwartsGrid` (its HLOD Setups list
`LV_HW_HLODLayer_Near`) and `MainGrid` (it does **not**). `AllowedRuntimeGrids` in
`DefaultPlugins.ini` carries part of the same allow-list.

## The Streaming List View (ImGui tool)

The "Streaming List View" from the ticket screenshot is the ImGui **Streaming Profiler**
(plugin `WImguiStreamingProfiler`), not an engine overlay.

- Open it in PIE: **Ctrl + Middle Mouse → System → Streaming Profiler…**.
- In the `Streaming Profiler` window check **List View** (the table) and **Streaming
  Map** (the 2D view).
- The `GridLevel = -` / `IsHLOD = F` rows are the orphan HLOD cells. Filter them with
  **Show Filters → Level Streaming Behavior → NoneSpatiallyLoaded** plus a **keyword**
  filter (`HLODLayer_Near` / `MainGrid_L`).
- The **Package** column (right-click the header to un-hide it, then **Expand all
  package**) lists the source actors of the cell. **Dump .CSV** writes the filtered
  result under `Saved/Profiling/StreamingProfiler/`.

## How the four names relate

`LV_HW_HLODLayer_Near`, `LI_QuidditchPitch_Section_A`, `MainGrid_L1_X-2_Y-1_Z0_d8F1A3152`
and `StaticMeshActor_50` are joined like this:

```
StaticMeshActor_50                         source actor (OFPA)
   | container / Outliner path
   v
LI_QuidditchPitch_Section_A                level instance
   | RuntimeGrid = None  --(inheritance)-->  MainGrid   (effective grid)
   | HLODLayer  = LV_HW_HLODLayer_Near
   v
streaming generation groups HLOD-relevant source actors by
(effective grid, HLOD layer, cell)
   v
HLOD actor:  LV_HW_HLODLayer_Near / MainGrid_L1_X-2_Y-1_Z0_d8F1A3152
   | LV_HW_HLODLayer_Near has no tier on MainGrid
   v
builder -> RuntimeGrid = None, SpatiallyLoaded = false   (orphan HLOD)
```

The HLOD actor name decodes as: `<HLODLayer>/<effectiveGrid>_L<gridLevel>_X_Y_Z_d<hash>`,
where `<hash>` is `GetSourceActorsHash()` of the cell's source actors.

## Reading the source actors of an HLOD actor

`AWorldPartitionHLOD::SourceActors` is a `UPROPERTY()` without `VisibleAnywhere`, so the
Details panel does **not** list it (it only shows a **Tools** category: Build HLOD, Force
Build HLOD, Export HLOD Assets, Compare Against Source). Three ways to get the list:

1. **Streaming Profiler → Package column** (runtime labels only — `StaticMeshActor_50`'s
   internal name does not appear there).
2. **`wp.Editor.DumpStreamingGenerationLog`** — the authoritative source. Run it in the
   editor (**not** during PIE — the command refuses a PIE session) on `LV_Overland`. It
   writes `<Project>/Saved/Logs/WorldPartition/StreamingGeneration-<pid>-<timestamp>.log`
   and prints the exact path to the Output Log (`LogWorldPartition`). The
   `Containers: → ActorDescs:` section lists each actor by internal name with its
   container and (AVA patch) its `ExpectedRuntimeGrid`, e.g. `StaticMeshActor_50 …
   HLODLayer:LV_HW_HLODLayer_Near … ExpectedRuntimeGrid:MainGrid`.
3. **`wp.Editor.DumpActorDescs <abs path>`** — a flat CSV of every actor descriptor
   (name, label, package, RuntimeGrid, HLODLayer, container). A **relative** path lands
   next to the editor executable (`D:\Sun\Engine\Binaries\Win64\`), so pass an absolute
   path, e.g. `wp.Editor.DumpActorDescs D:/Sun/Sundance/Saved/MonDump.csv`.

---

## Phil's video — HogwartsGrid vs MainGrid

> Source: `Phil_Explique_HWGrid_VS_MainGrid.mp4` (21 min, FR; auto-transcribed with
> faster-whisper, model `medium`). Verbatim:
> [Phil_Explique_HWGrid_VS_MainGrid_2026-10-14_verbatim.txt](Phil_Explique_HWGrid_VS_MainGrid_2026-10-14_verbatim.txt).
>
> Known mis-transcriptions: `HLOD acteur` / `HL`/`H-layer`/`hashtag layer` = **HLOD
> actor / HLOD layer**, `node`/`None` = **`None`**, `oxwart`/`Hogwarts grid`/`HW` =
> **`HogwartsGrid` / HW layer**, `main grid` = **`MainGrid`**, `selle` = **cell**,
> `le paye`/`paye sur paye` = **PIE**, `Road Builder`/`World Partition Rule Command Let
> Builder` = **`WorldPartitionRuleBuilder`**, `own processator` = **`OnProcessActor`**,
> `mutateur` = **mutator**, `acteur descripteur` = **actor descriptor**, `Yuri` /
> `Sam Seyrol` = streaming colleagues who reported always-loaded HLODs.

**Point by point:**

1. **Why the Level Instance is not in the profiler's package list.** Arnaud asks how to
   tie the HLOD cell (442 packages) back to `LI_QuidditchPitch_Section_A`, which he does
   not see listed. Phil: **Level Instances are editor-only; they do not exist in a
   runtime/build package.** Once built, there are only actors placed in the grid — no
   Level Instance concept. So the profiler package list cannot show the LI.

2. **The mismatch, restated.** The Quidditch source actor has RuntimeGrid `None` →
   inherits the Quidditch container → resolves to **MainGrid**; its HLOD layer is the
   **HW near** layer. So it is on MainGrid but in a Hogwarts layer → that is the problem,
   and the generated HLOD actor ends up **always loaded**.

3. **Forget the runtime, go to the editor.** Stop PIE. In **World Settings** every grid /
   partition is defined; open **MainGrid → HLOD partition → near/far/always-loaded** and
   you see the HLOD layers included per tier (for Overland). Same pattern for every grid:
   each grid declares the HLOD layers available to it.

4. **The diagnosis in one sentence.** "I have an HLOD layer that says HW but my grid is
   MainGrid" → mismatch → the generated HLOD actor is always loaded. The cell /
   coordinates in the Jira screenshot are "just the result at the end of the pipe" — you
   do not even need to understand the cell to fix the cause.

5. **Three ways to fix (Phil's framing).**
   - **The real fix (data):** change the rules so the Quidditch Pitch is assigned to the
     correct grid (`HogwartsGrid`) instead of `MainGrid`. Phil is doing this last-minute,
     in parallel.
   - **The safety net (engine):** Phil's own last-minute override lives in the streaming
     generation **mutator** step (step 1: mutators; step 2: place actors into cells = the
     streaming generation proper; step 3: cell transformers / FastGeo). The mutator is the
     last chance to override an actor's RuntimeGrid or spatial status: it loops over all
     actor descriptors and, on a grid↔HLOD-layer mismatch, overrides the grid to the one
     the HLOD layer actually belongs to (`HogwartsGrid`).
   - **The validation (Arnaud's task):** add a warning that **catches every actor** where
     RuntimeGrid and HLOD layer disagree, so the broken data can be tracked and fixed.

6. **The approach is generic, rule-agnostic.** For each actor descriptor: read its
   RuntimeGrid and its HLOD layer; does the HLOD layer belong to that grid? If yes, fine;
   if no, it is a mismatch (and Phil's mutator overrides it). No dependency on which rule
   or which actor. Phil found a console command to **dump all actor descriptors** and
   searched it for `StaticMeshActor_50` (the Jira's example).

7. **Where to look up which layer belongs to which grid.** The **World Settings**
   breakdown, or the **Confluence page** that mirrors it exactly: a breakdown per grid,
   and within each grid a breakdown per HLOD layer. A layer listed under `HogwartsGrid`
   but used on `MainGrid` "does not work — that's the problem."

## Action: implement the warning in WorldPartitionRuleBuilder.cpp

Per Phil's call in the video, the warning does **not** re-enable the compiled-out engine
check (`ValidateContainerInstanceDescriptor`). Phil's own last-minute safety net is in the
streaming generation **mutator** step (engine); the **data fix** goes through the rules; and
the **validation Arnaud owns** goes in the custom **`UWorldPartitionRuleBuilder`**
(`D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionRuleBuilder.cpp`),
which already applies DataLayer / RuntimeGrid / HLOD rules per actor and holds the top-level
runtime hash (`TopLevelRuntimeHash = WorldPartition->RuntimeHash`). Phil notes the builder
can run **any time** (it checks out no actor), unlike the weekend validate job.

**Where**: in `OnProcessActor`, **after** the RuntimeGrid and HLOD rules have been applied
to the actor, so the effective RuntimeGrid and HLOD layer are both known. The check is
**generic and rule-agnostic**: it loops over actor descriptors, reads each actor's grid +
HLOD layer, and only logs — it does not depend on which rule or which actor.

**Condition** (mirror of the engine check in
[streaming properties](ReferenceDocs/WorldPartitionStreamingProperties.md)):

1. the actor is HLOD-relevant,
2. the actor is spatially loaded,
3. it has an explicit HLOD layer,
4. `!TopLevelRuntimeHash->IsValidHLODLayer(EffectiveGrid, HLODLayer)` — the layer has no
   tier on the **effective** grid (after Level Instance inheritance), not the grid authored
   on the actor.

**Warning text** (per the ticket's acceptance), naming the actor, its Level Instance, the
layer and the effective grid, e.g.:

```
Actor 'StaticMeshActor_50' (LI_QuidditchPitch_Section_A) uses HLOD layer
'LV_HW_HLODLayer_Near', which has no tier on its effective runtime grid 'MainGrid'
```

**Acceptance criteria** (from the ticket):

- names the actor, its Level Instance (if any), the HLOD layer and the effective grid;
- uses the **effective** grid, not the authored grid;
- does **not** fire for layers deliberately placed in a non-spatially-loaded tier (e.g.
  `HW_Far`);
- on `LV_Overland` it flags the source actors behind the 182 unexpected `None`-grid HLOD
  actors: 13 HW_Near, 12 HM_Near, 157 Dummy.

Log through the builder's existing category `LogWorldPartitionRuleBuilder`. Follow the
builder's operating principles: guard with equality checks, dry-run / report-only first,
iterate with Live Coding.
