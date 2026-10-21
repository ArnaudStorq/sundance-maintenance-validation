Parent: [Reference Docs](README.md)

# `-ReportOnly` vs `-ValidateOnly` on `WorldPartitionRuleBuilder`

Both switches put [`UWorldPartitionRuleBuilder`](BuildersAndCommandlets.md#uworldpartitionrulebuilder)
into a **read-only (dry) run** — nothing is checked out, saved or submitted. But they get there
two completely different ways, answer two different questions, and cost two very different amounts
of time. This page is the exact difference.

Source: `D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionRuleBuilder.cpp`.

## Contents

- [The short version](#the-short-version)
- [What they share](#what-they-share)
- [`-ReportOnly` — answer from the descriptor](#-reportonly--answer-from-the-descriptor)
- [`-ValidateOnly` — load and exercise the apply path](#-validateonly--load-and-exercise-the-apply-path)
- [Side by side](#side-by-side)
- [Which one do I want](#which-one-do-i-want)
- [Caveats](#caveats)
- [See also](#see-also)

---

## The short version

| | `-ReportOnly` | `-ValidateOnly` |
|---|---|---|
| Question it answers | *What would the rules change?* | *What does the real apply path do / warn about?* |
| Loads the actor | **No** — reads the actor **descriptor** only | **Yes** — loads every actor into memory |
| Runs the real assignment code | No (attribution query only) | **Yes** (`ApplyRulesOnActor`), then throws the edits away |
| Output | a **JSON report** on disk | **log lines** only |
| Cost | cheap (no actor loading) | expensive (loads everything, like a real run) |
| Writes / checks out / submits | never | never |

They are **mutually exclusive**. If you pass both, `-ValidateOnly` is dropped with a warning and
`-ReportOnly` wins:

```124:128:D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionRuleBuilder.cpp
if (BuildOptions.bReportOnly && BuildOptions.bValidateOnly)
{
	UE_LOG(LogWorldPartitionRuleBuilder, Warning, TEXT("-ReportOnly and -ValidateOnly are mutually exclusive, ignoring -ValidateOnly"));
	BuildOptions.bValidateOnly = false;
}
```

## What they share

Both set `IsDryRun()`, which is the single gate that keeps the run from touching source control:

```85:85:D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionRuleBuilder.h
bool IsDryRun() const { return BuildOptions.bReportOnly || BuildOptions.bValidateOnly; }
```

In a dry run, `SaveModifiedPackages` empties the save list instead of saving it, and
`FinalizeRunInternal` clears the dirty flag on any package that slipped in, so **nothing ever
reaches Perforce** — no checkout, no saved package, no changelist, no submit.

Both also honour the same opt-in rule-family switches (`-DataLayerRules`, `-HLODLayerRules`,
`-RuntimeGridRules`) and the same scoping switches
(`-ContainOutlinerPathSubstrings=`, `-DiscardOutlinerPathSubstrings=`, `-ActorClassNames=`).

> The builder has **no `-DryRun` switch**. These two are the only read-only modes.

## `-ReportOnly` — answer from the descriptor

`-ReportOnly` never loads an actor. In `ShouldProcessActor`, once the class/path filters pass, it
gathers its findings straight from the actor descriptor and then **rejects the actor**, so the
loading path is never entered:

```453:459:D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionRuleBuilder.cpp
// -ReportOnly answers from the descriptor and then rejects the actor, so nothing is ever loaded, checked out or saved.
// The report deliberately includes actors whose package cannot be checked out, which a real run skips.
if (BuildOptions.bReportOnly)
{
	GatherReportFindings(ActorOrDesc);
	return false;
}
```

`GatherReportFindings` runs the rule **attribution query** for each enabled rule type and records
a *finding* for every actor/rule-type pair whose **current value disagrees with what the rules
expect** (a mismatch). Each finding carries the actor name/path, the rule type, the current vs
expected value, the winning rule asset, and every candidate rule that matched (more than one on a
single-valued type is a conflict). It also counts matches per rule asset across the whole run, so a
rule whose reach suddenly explodes is obvious.

At `PostRun`, `WriteReport` serialises all of that to **JSON**:

- Default path: `Saved/Logs/WorldPartition/WorldPartitionRulesReport-<Level>.json`
- Override with `-ReportFile=<path>`.

The report deliberately **includes actors whose package cannot be checked out** (a real run skips
those). Because nothing is loaded, this mode is cheap and is the right tool for *"how many actors
would change, and how"* — e.g. the [manual runtime Data Layer cleanup](DevelopmentPlan-ManualRuntimeDataLayerCleanup.md)
detection pass.

## `-ValidateOnly` — load and exercise the apply path

`-ValidateOnly` is the opposite: it **loads every candidate actor and runs the real assignment
code on it**, even on actors the rules already agree with — that is the whole point. In
`ShouldProcessActor` it overrides the two early-outs a real run would take:

```509:519:D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionRuleBuilder.cpp
// If no rules matched, early out. -ValidateOnly deliberately keeps going: exercising the apply path on actors
// the rules already agree with is the whole point of that pass.
if (!bShouldApplyRules && !BuildOptions.bValidateOnly)
{
	return false;
}

// -ValidateOnly never writes, so an actor whose package could not be checked out is still worth loading
if (BuildOptions.bValidateOnly)
{
	return true;
}
```

Then `OnProcessActor` calls the same `ApplyRulesOnActor` as a real run (so every `Applied …` /
warning / error the apply path emits lands in the log), counts the actors, and **discards the
in-memory edits** so nothing downstream can save them:

```328:338:D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionRuleBuilder.cpp
if (BuildOptions.bValidateOnly)
{
	ValidateActorsLoaded++;
	ValidateActorsModified += bModified ? 1 : 0;

	// Drop the in-memory edits so nothing downstream can save or submit them
	if (UPackage* Package = Actor->IsPackageExternal() ? Actor->GetExternalPackage() : Actor->GetOutermost())
	{
		Package->SetDirtyFlag(false);
	}
	return;
}
```

There is **no JSON report** — the output is the log, summarised at `PostRun`:

```207:207:D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionRuleBuilder.cpp
UE_LOG(LogWorldPartitionRuleBuilder, Display, TEXT("Validation pass: loaded %d actor(s), the rules would have modified %d of them. Nothing was checked out or saved."), ValidateActorsLoaded, ValidateActorsModified);
```

Because it actually loads actors, it is the mode that drives the
[Validate World Partition Rules](TeamCityJobs.md#the-validation-build) build. It is also the only
one of the two that runs the per-actor HLOD-layer/grid consistency check (`ValidateHLODLayerGridConsistency`
lives in `OnProcessActor`, which `-ReportOnly` never reaches).

## Side by side

| Aspect | `-ReportOnly` | `-ValidateOnly` |
|--------|---------------|-----------------|
| Data source | actor **descriptor** (`FActorOrDesc`) | the **loaded actor** |
| Where it acts | `ShouldProcessActor` → `GatherReportFindings`, returns `false` | `ShouldProcessActor` returns `true` → `OnProcessActor` → `ApplyRulesOnActor` |
| Runs the real assignment code | no | **yes** (edits then dropped) |
| Processes actors the rules already agree with | no (only records mismatches) | **yes** (loads them all) |
| Includes non-checkout-able actors | **yes**, by design | yes (never writes anyway) |
| HLOD-layer/grid consistency warning | no (actor not loaded) | yes |
| Output | JSON report (`-ReportFile=` to redirect) | log lines + a summary count |
| Relative cost | cheap | expensive (loads like a real run) |
| Touches Perforce | never | never |

## Which one do I want

- *"How many actors would change and what would each change to?"* — **`-ReportOnly`**. You get a
  machine-readable diff of current vs expected, cheaply, without loading the world.
- *"Does the apply path throw warnings/errors on this content, and how many actors would it
  touch?"* — **`-ValidateOnly`**. You pay the loading cost to exercise the real code and read its
  log, which is what you want before committing a rule change.

## Caveats

- **`-ValidateOnly` over-reports the DataLayer path.** `HLODLayer`, `RuntimeGrid` and
  `IncludeInHLOD` report their dry run correctly, but the **DataLayer** apply calls the real
  assignment, which cannot commit in a dry run and logs `Failed to assign DataLayer` instead. On one
  measured build that was 85 490 warnings (92.5 % of the log) for **zero** content defects — read
  those rows as the diff the builder *would* have applied. See
  [the validation build note](TeamCityJobs.md#the-validation-build) and the
  [Failed to assign DataLayer audit](../Audits/ValidateWorldPartitionRules-LV_Overland-2026-09-27/FailedToAssignDataLayer.md).
- **`-ReportOnly` only records mismatches**, not every match, so its finding count is not the
  number of actors a rule touches — the per-rule match counts in the report cover that.
- Both modes only cover **what they were told to process** — the opt-in rule families and the
  Outliner/class scoping still apply.

## See also

- [Builders & commandlets](BuildersAndCommandlets.md#uworldpartitionrulebuilder) — the rule builder in context
- [World Partition builders catalog](WorldPartitionBuildersCatalog.md#uworldpartitionrulebuilder) — the full switch list
- [TeamCity jobs](TeamCityJobs.md) — the nightly apply pass and the `-ValidateOnly` validation build
- [Manual runtime Data Layer cleanup](DevelopmentPlan-ManualRuntimeDataLayerCleanup.md) — a worked `-ReportOnly` detection pass
