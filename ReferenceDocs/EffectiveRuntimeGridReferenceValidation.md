Parent: [Reference Docs](README.md)

# Effective RuntimeGrid reference validation

An engine change that stops World Partition streaming generation from reporting
**"references an actor in a different runtime grid"** when two actors only differ by the
*name* of their RuntimeGrid but really stream on the same grid — the `None` vs `MainGrid`
false positive of the 2026-09-30 MapCheck. Before comparing, each `None` is resolved to
the grid the actor really inherits ("Resolve None"). The validation is **always on**:
there is no switch.

- **Changelist**: **2102948** (pending, `//sun/Dev`), review Philippe St-Jean, jira
  **SUNDANCE-77683**.
- **Source**: `D:\Sun\Engine\Source\Runtime\Engine\Private\WorldPartition\WorldPartitionStreamingGeneration.cpp`,
  tagged `//@third party code - AVA BEGIN/END [arnaud.storq]`.
- **Origin**: sync with Phil on 2026-09-30 — fix the validation rather than tagging the
  actor, then A/B test the cost of the fix.
- **History**: the first version of the CL was gated by a
  `wp.RuntimeGrid.ValidateReferencesOnEffectiveGrid` CVar and added a
  `ValidateContainerDescriptor` trace scope. Both were removed the same day, so the CL
  now only touches the reference check.

## Contents

- [The problem](#the-problem)
- [The effective-grid rule](#the-effective-grid-rule)
  - [Why the rule is exact](#why-the-rule-is-exact)
  - [What does not change](#what-does-not-change)
- [Implementation](#implementation)
- [Performance](#performance)
- [A/B test procedure](#ab-test-procedure)
- [Limitations and follow-ups](#limitations-and-follow-ups)
- [See also](#see-also)

## The problem

The 2026-09-30 MapCheck on `LV_Overland`
(`Map check complete: 2 Error(s), 14 Warning(s), took 25,136.694ms to complete.`) reported
the same couple twice:

```text
Actor /Game/Levels/Dungeons/Merlin/Block_01/LI_DUN_Merlin_Block_01.BP_ReassembleToTarget3 references an actor in a different runtime grid /Game/Levels/Dungeons/Merlin/Block_01/LI_DUN_Merlin_Block_01.SK_CherryTree_Small_A_Nanite
```

| Role | Actor | RuntimeGrid |
|------|-------|-------------|
| Referencer | `BP_ReassembleToTarget3` | `None` |
| Referee | `SK_CherryTree_Small_A_Nanite` | `MainGrid`, written on save by `DA_MainGrid_Rules` (it matches `PlacedFoliageSkinnedNaniteAssembly`) |

The check, `IsReferenceRuntimeGridValid`, compares the two RuntimeGrid **names**. But
`None` is not a grid of its own: the runtime hash streams a `None` actor on its **first
partition** (`UWorldPartitionRuntimeHashSet::GetDefaultGrid()`,
`WorldPartitionRuntimeHashSet.cpp:352`), and on `LV_Overland` that partition is `MainGrid`
(`RuntimePartitions(0)`, read with `obj dump` on 2026-09-30). Both actors stream on
`MainGrid`, so there is no real error.

Two more reasons the raw names mislead:

- The check runs **before** the Level Instance inheritance is applied.
  `ValidateContainerDescriptor` (line 1373) runs before the container grid is pushed onto
  the actors (`SetRuntimeGrid(CombinedData.RuntimeGrid)`, line 1485). Inside a Level
  Instance that has a grid, both actors end up on that grid whatever their own names say.
- Fixing the data does not stick. The next save puts `MainGrid` back on the referee, and
  the `ExcludeFromRuntimeGridRules` tag is a one-off fix, which Phil considers dangerous.

The same false positive also reaches the `WorldPartitionChangelistValidator` at submit
time and [`Editor.ScanRuntimeGridReferenceErrors`](CustomTools/RuntimeGridReferenceTools.md),
because they run the same streaming-generation validation. The change fixes all three.

## The effective-grid rule

A mismatch is now reported only when the **effective** grids differ: the grids the two
actors really stream on. The referee is looked up in the referencer's own container, so
both actors of a validated reference always belong to the **same container**. The rule
therefore only depends on that container:

| Where the two actors are | Effective grid of each actor | Different names, same effective grid when… |
|--------------------------|------------------------------|--------------------------------------------|
| Level Instance whose resolved RuntimeGrid is `G` (not `None`) | `G` | always |
| Main world, or Level Instance whose resolved RuntimeGrid is `None` | its own grid, `None` → default grid (first runtime partition) | one side is `None` and the other is the default grid — `None` vs `MainGrid` on `LV_Overland` |
| Custom HLOD actor (`AWorldPartitionCustomHLOD`) on either side | comes from its HLOD layer | never: the raw rule is kept |

Phil's **both-`None`** case needs nothing new. Two `None` actors in the same container
always resolve the same way: both take `G`, or both fall back to the default grid.
Identical names are therefore still valid, as before.

### Why the rule is exact

- **Level Instance with a grid.** An actor inside a Level Instance takes the container's
  grid, unless `wp.RuntimeGrid.AllowUnreferencedActorOverride` lets it keep its own
  (line 1323). That override is only allowed for actors that share **no reference
  cluster** (`GatherClusteredActorGuids`, line 1469). A validated reference is a runtime
  reference, so both of its actors are clustered and neither can override: both stream on
  `G`. Attached actors already follow their parent (`GetRuntimeGrid()` returns the
  parent's grid, line 236).
- **Main world.** `InheritParentContainerData` keeps each actor's own grid (line 1324),
  and the runtime hash maps `None` to its first partition.
- **Custom HLOD actors.** Their grid comes from `GetResolvedRuntimeGridForHLODLayer` at
  inheritance time (line 1329), which needs the HLOD layer to be loaded. That is too costly
  for a validation, so these actors keep the raw rule.

### What does not change

- **Only the report is skipped.** The fixup pass still runs for the pair and forces both
  actors to `None` (`SetForcedNoRuntimeGrid`, line 1900), which streams on the same
  effective grid. The generated streaming (cells, actor sets, HLODs) is the same as before
  the CL, so it needs **no HLOD rebuild**.
- The other reference checks (spatial loading, Data Layers, External Data Layer) are
  untouched.
- When the two names match, no new code runs.

## Implementation

Two hunks in `WorldPartitionStreamingGeneration.cpp`. Each one is wrapped in AVA markers,
and the replaced line is kept commented out:

| Lines | Hunk |
|-------|------|
| 1723–1740 | `IsReferenceEffectiveRuntimeGridValid`, next to the unchanged `IsReferenceRuntimeGridValid` |
| 1889–1896 | The report call, now conditioned on the effective grids |

The resolution, which is only called when the names differ:

```cpp
auto IsReferenceEffectiveRuntimeGridValid = [this, &ContainerCollectionInstanceDescriptor](const FStreamingGenerationActorDescView& RefererActorDescView, const FStreamingGenerationActorDescView& ReferenceActorDescView)
{
	const FName RefererRuntimeGrid = RefererActorDescView.GetRuntimeGrid();
	const FName ReferenceRuntimeGrid = ReferenceActorDescView.GetRuntimeGrid();

	// Inside a Level Instance with a RuntimeGrid, the reference clusters both actors so neither may override the inherited grid
	const bool bIsSameEffectiveRuntimeGrid = (!ContainerCollectionInstanceDescriptor.ID.IsMainContainer() && !ContainerCollectionInstanceDescriptor.ContainerCombinedData.RuntimeGrid.IsNone())
		|| (RefererRuntimeGrid.IsNone() && ReferenceRuntimeGrid == DefaultGrid)
		|| (ReferenceRuntimeGrid.IsNone() && RefererRuntimeGrid == DefaultGrid);

	// A Custom HLOD actor takes its grid from its HLOD layer, which is not resolved yet
	return bIsSameEffectiveRuntimeGrid
		&& !RefererActorDescView.GetActorNativeClass()->IsChildOf<AWorldPartitionCustomHLOD>()
		&& !ReferenceActorDescView.GetActorNativeClass()->IsChildOf<AWorldPartitionCustomHLOD>();
};
```

The call site. Only the reporting branch changes:

```cpp
if (!IsReferenceRuntimeGridValid(*RefererActorDescView, *ReferenceActorDescView))
{
	if (PassType == EPassType::ErrorReporting)
	{
		if (!IsReferenceEffectiveRuntimeGridValid(*RefererActorDescView, *ReferenceActorDescView))
		{
			ErrorHandler->OnInvalidReferenceRuntimeGrid(*RefererActorDescView, *ReferenceActorDescView);
		}
	}
	else
	{
		RefererActorDescView->SetForcedNoRuntimeGrid();
		ReferenceActorDescView->SetForcedNoRuntimeGrid();
	}

	NbErrorsDetected++;
}
```

`DefaultGrid` is the generator member that every streaming generation already fills from
`RuntimeHash->GetDefaultGrid()`. That includes the static `CheckForErrors` used by
MapCheck and by the changelist validator.

**Compile check (2026-09-30)**: the file was compiled on its own with the Engine module's
exact options (`Engine.Shared.rsp`, shared PCH, MSVC 14.50, `/W4 /WX`). It builds clean.
It has not been run in the editor yet: see the [A/B test](#ab-test-procedure).

## Performance

Phil's concern: the MapCheck runs this validation on **every actor descriptor**. The design
keeps the cost of a valid reference at **zero**:

1. **The hot path is untouched.** A valid reference still costs one `FName` comparison.
   The new code only runs when the names differ **and** the pass is the reporting pass.
2. **Each mismatch costs O(1), with no hierarchy walk.** The container grid is already on
   the container descriptor (`ContainerCombinedData`, set before recursing). Attach
   parents are already followed by `GetRuntimeGrid()`. There is no map lookup, no
   allocation and no string.
3. **The cheapest tests run first.** The order is: the container ID and grid, then two
   `FName` comparisons. The class check runs last, and only when the pair is about to be
   skipped.
4. **No new pass, no new state.** The fixup passes are unchanged, so the number of
   validation passes is the same as before, and there is no per-actor data.
5. **A skipped error is cheaper than a reported one.** It avoids creating an
   `FTokenizedMessage` and adding it to the Message Log.

On `LV_Overland` the extra work is two evaluations per Map Check, one per mismatch. The
A/B test should show no difference beyond noise.

## A/B test procedure

Without a switch, the A/B test compares two builds:

1. **Before**: the current editor build, without CL 2102948. Open `LV_Overland`, run
   `MAP CHECK` three times, and read the summary line in *Message Log → Map Check*
   (`took …ms to complete`).
2. **After**: close the editor, build with CL 2102948, reopen `LV_Overland` and run
   `MAP CHECK` three times.
3. *(Optional, finer timer)* Record an Unreal Insights trace with the `cpu` channel around
   one Map Check in each build. Compare the total time of
   `FWorldPartitionStreamingGenerator::CreateActorContainers`, which contains the
   validation and exists in both builds.
4. Expected result: errors go from 2 to 0, warnings stay at 14, and the time stays within
   noise of the baseline.

| Run | Build | Map Check time | Errors | Warnings |
|-----|-------|----------------|--------|----------|
| Baseline (2026-09-30) | before | 25,136.694 ms | 2 | 14 |
| A1 / A2 / A3 | before | *to fill* | | |
| B1 / B2 / B3 | after (CL 2102948) | *to fill* | | |

## Limitations and follow-ups

- **It depends on which world is validated.** `None` is resolved against the world being
  checked. A Level Instance level opened on its own is its own main world:
  `LI_DUN_Merlin_Block_01`'s first runtime partition is `MainPartition`, so the same couple
  is still reported there. The isolated per-level phase of
  `Editor.ScanRuntimeGridReferenceErrors` behaves the same way.
- **Custom HLOD actors** keep the raw rule (see [above](#why-the-rule-is-exact)).
- **Rule conditions are untouched.** A WorldPartition rule condition on RuntimeGrid
  (`bUseRuntimeGrid`, `WorldPartitionRuleSubsystem.cpp:1178`) still compares the actor's
  raw grid, so a `None` actor does not match a `MainGrid` condition.
- **The mutator cluster-divergence check** (`RejectClusterDivergentMutators`) still
  compares raw names. It has no effect today because `RuntimeGridRulesForStreamingGeneration`
  is empty.
- **No runtime switch.** Getting the raw comparison back means backing out the CL.
- **Where to submit.** Phil's RuntimeGrid engine CLs (2028633, 2051632) went through
  `//sun/Dev-Engine` and were robomerged to `//sun/Dev`. CL 2102948 is in `//sun/Dev`.
- The CL description says `&TESTED Compile`. Switch it to `Editor` after the A/B test.

## See also

- [Fixing MapCheck issues — D5](FixingMapCheckIssues.md#d5--actor-references-an-actor-in-a-different-runtime-grid)
  — the playbook entry for this message
- [Runtime Grid Reference Tools](CustomTools/RuntimeGridReferenceTools.md) — scan and fix
  the real conflicts that remain
- [Exclude From Rules tag](CustomTools/ExcludeFromRulesTag.md) — the per-actor alternative
  that was not chosen
- [Runtime Grid rules](WorldPartitionRulesAnalysis/RuntimeGridRules.md) — the on-save rules
  that write `MainGrid`
- [World Partition streaming properties](WorldPartitionStreamingProperties.md) — RuntimeGrid
  and its inheritance
