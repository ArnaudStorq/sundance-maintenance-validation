Parent: [Reference Docs](README.md)

# Development Plan — Manual runtime Data Layer cleanup

*Finding and removing the runtime Data Layers that were assigned by hand — mostly
`DL_Overland` inside Hogwarts — so streaming generation stops splitting geometry that
belongs in a single cell.*

Scoped for **2026-09-17**, from the [morning sync with Phil](../SyncWithPhil_2026-09-17_StreamingCells_ManualRuntimeDataLayers_transcript.md),
and rewritten after reading the code actually shipped in **CL 2049874** and **CL 2071000**.

## Contents

- [Goal](#goal)
- [What the code review changed about this plan](#what-the-code-review-changed-about-this-plan)
  - [A — The nightly log will not find the population we are after](#a--the-nightly-log-will-not-find-the-population-we-are-after)
  - [B — CL 2049874 silently dropped runtime layers off the dashboard](#b--cl-2049874-silently-dropped-runtime-layers-off-the-dashboard)
  - [C — `-ReportOnly` already does what Phil asked for at the end of the call](#c---reportonly-already-does-what-phil-asked-for-at-the-end-of-the-call)
- [Plan for the day](#plan-for-the-day)
  - [Step 1 — Detect with `-ReportOnly` (no code change needed)](#step-1--detect-with--reportonly-no-code-change-needed)
  - [Step 2 — Answer Phil's exclusivity question from the report](#step-2--answer-phils-exclusivity-question-from-the-report)
  - [Step 3 — Fix the two reporting gaps](#step-3--fix-the-two-reporting-gaps)
  - [Step 4 — Remove the redundant layers](#step-4--remove-the-redundant-layers)
  - [Step 5 — Report back to Phil](#step-5--report-back-to-phil)
- [Deferred](#deferred)
- [See also](#see-also)

---

## Goal

Inside Hogwarts, some Level Instances carry a hand-assigned **`DL_Overland`** on top of the
**`DL_HW_Exterior`** that the rules assign. Data Layer assignment is additive and nothing
cleans up the manual entries, so streaming generation — which groups actors into cells by
the **exact set of runtime Data Layers** — emits two cells where one would do. More cells
means more draw calls.

The three exterior Data Layers (`DL_Overland`, `DL_HW_Exterior`, `DL_Hogsmeade_Exterior`)
are all disabled together when the player enters an interior, so carrying two of them buys
nothing. Removing the redundant one is safe in the Hogwarts scope.

Expected volume: **30–40 Level Instances**, plus an unknown number of static meshes tagged
directly.

---

## What the code review changed about this plan

The plan coming out of the call was "run the warning from CL 2049874, read the log". Reading
the code invalidates that, for the specific population we are hunting.

### A — The nightly log will not find the population we are after

`UDataLayerRuleSubsystem::OnMatchingRulesFound` is reached from
`UWorldPartitionRuleSubsystem::GetMatchingRulesForActor`, which has three callers:

| Caller | Logging | Reached for |
|---|---|---|
| `UWorldPartitionRuleBuilder::ShouldProcessActor` | **muted** (`FScopedMatchingRulesLogMute`, CL 2071000) | every actor in scope |
| `UWorldPartitionRuleSubsystem::EvaluateActor` | **muted** (`WorldPartitionRuleSubsystem.cpp:821`) | every actor queried by the toolsets / report |
| `UWorldPartitionRuleSubsystem::ApplyRulesOnActor` | active | **only** actors `ShouldProcessActor` accepted |

`ShouldProcessActor` accepts an actor only when `bMatchesRules && bLocalShouldApplyRules`,
i.e. when a rule match implies **something to apply**. An actor that is already compliant
but carries an *extra* `DL_Overland` has nothing to apply, so it is rejected, never loaded,
and `ApplyRulesOnActor` never runs on it.

> **The warning therefore never fires for a compliant actor carrying a spurious runtime
> Data Layer — exactly the case CL 2049874 was written for.** It fires only for actors the
> pass was going to modify anyway. This is an unintended interaction between CL 2049874 and
> the duplicate-logging mute added by CL 2071000.

### B — CL 2049874 silently dropped runtime layers off the dashboard

`CurateWorldPartitionRulesData.py` recognises findings by regex. One of its patterns is:

```python
(re.compile(r"Actor '([^']+)' should not be assigned to DataLayer '([^']*)'"),
 'Invalid DataLayer assignment', 1, 2),
```

CL 2049874 added `if (!NonCompliantDataLayerAsset->IsRuntime())` around that exact message
and routed runtime layers to the new, longer message instead — which matches **no** pattern
in the curator. Net effect: runtime Data Layers **left** the *Invalid DataLayer assignment*
category of `WorldPartitionRulesSnapshot.html` and landed nowhere.

This is the contract [TeamCityJobs.md](TeamCityJobs.md#the-reporting-pipeline) spells out:
a message that does not match a curator pattern shows up in the log but **not** in the
dashboard.

### C — `-ReportOnly` already does what Phil asked for at the end of the call

Phil closed the call wishing for a run that loads everything and only validates, saying he
did not have the solution. It exists: **`-ReportOnly`** on `WorldPartitionRuleBuilder`.

And it does **not** have problem A. `ShouldProcessActor` calls `GatherReportFindings` and
returns `false` *before* the mute scope, so:

- nothing is loaded, checked out or saved;
- `AttributeActor(ERuleType::DataLayer, …)` calls `ValidateNonCompliantActorDataLayers`,
  whose `OutNonCompliantDataLayers` is filled for **runtime and editor-only layers alike**
  (the `IsRuntime()` guard only skips the *logging*, not the output array);
- a non-empty result sets `bMismatch = true`, so a JSON finding is written with the actor's
  **Outliner path**, `CurrentValue`, `ExpectedValue`, the candidate rule assets, and a
  `Non-compliant DataLayers: …` note.

Two known blind spots to keep in mind: `AttributeActor` returns early when
`bIsIgnoredByRules` or `bForcedSettingsApply`, and the note does not say **which** of the
listed layers are runtime.

---

## Plan for the day

### Step 1 — Detect with `-ReportOnly` (no code change needed)

Run the rule builder locally, Data Layer rules only, over the Hogwarts scope:

```bat
UnrealEditor-Cmd.exe Sundance ^
 -stdout -FullStdOutLogOutput -SCCProvider=Perforce ^
 -run=WorldPartitionBuilderCommandlet ^
 -Builder=WorldPartitionRuleBuilder ^
 -DataLayerRules ^
 -ReportOnly ^
 -ReportFile=D:\Sun\Sundance\Saved\Logs\WorldPartition\ManualRuntimeDataLayers-Hogwarts.json ^
 -Verbose ^
 <LV_Overland path>
```

- `-DataLayerRules` alone: the HLOD and RuntimeGrid families are irrelevant today and only
  add findings to wade through.
- No scoping switch on the first run — the point is to learn **where** the cases are, and
  Phil explicitly wants to know whether there are any outside Hogwarts.
- If the full run is too long, scope with `-ContainOutlinerPathSubstrings=Hogwarts`
  (**OR** semantics, confirmed in [TeamCityJobs.md](TeamCityJobs.md#parameters)) and widen
  afterwards. Remember the builder still has to open every Level Instance, so the filter
  cuts processing time, not opening time.

Then triage the JSON: keep the `DataLayer` findings whose note lists a **runtime** layer,
and split them by whether the offending layer is on a **Level Instance** or on a plain
**static mesh** — Phil specifically wants to know if people tagged meshes directly.

### Step 2 — Answer Phil's exclusivity question from the report

Phil could not say whether `DL_Overland` is mutually exclusive with `DL_HW_Exterior` /
`DL_Hogsmeade_Exterior` (Hogwarts vs. Hogsmeade obviously are). The report answers it
without guessing: each finding carries its **candidate rule assets**, so the pairs that
appear together, and the rules that produced them, are in the data.

Pay attention to the edge case Phil raised: actors treated as Hogsmeade through their
**Outliner path** while sitting in a Level Instance at the root of `LI_Overland`. And to his
trap: if a matching rule **does** target the manual layer, the actor is compliant and
produces **no finding at all** — that is a rule to fix, not an actor.

### Step 3 — Fix the two reporting gaps

Small changelist, worth doing today because everything after this depends on the detection
being trustworthy:

1. **Make the new warning match a curator pattern** (problem B). Either give the runtime
   message the `Actor '…' should not be assigned to DataLayer '…'` prefix and append the
   streaming explanation, or add a pattern to `CurateWorldPartitionRulesData.py` and to the
   `warningPatterns` array in `WorldPartitionRulesSnapshot.html`. Prefer the first: one
   category, no divergence between the Python and the JS copies.
2. **Stamp the runtime flag on the report findings** (blind spot in C) so triage does not
   need a cross-reference — the note already lists the layer names, it just needs to say
   which are runtime.

Optionally, and only if it stays small: give `OnMatchingRulesFound` a call site that is not
gated on "something to apply", so problem A is fixed at the source rather than worked around
with `-ReportOnly`. If it is not small, log it and move on — `-ReportOnly` unblocks the day.

### Step 4 — Remove the redundant layers

- Scope: **Hogwarts only**. Phil was explicit that the "remove `DL_Overland`" conclusion is
  not to be generalised.
- `DL_HW_Exterior` alone is the correct end state for castle exterior geometry.
- The WP Rules Reviewer is **read-only**, so the edits happen in the editor.
- Re-run Step 1 afterwards and diff the findings to confirm the population is gone.

### Step 5 — Report back to Phil

He asked to be kept posted. Three things he does not know yet and will want: the actual
count, the answer on `DL_Overland` exclusivity, and that `-ReportOnly` already covers the
validation-only run he was asking for.

---

## Deferred

- **A scheduled validation-only pass.** `-ReportOnly` exists but nothing runs it on a
  cadence. Phil's framing: less frequent than the nightly, loads everything, assigns
  nothing. Either a scheduled `-ReportOnly` build or the separate validation commandlet he
  floated, applying the map checks and the rule warnings.
- **Phil's caveat stands regardless**: the pass only covers what it was told to process, and
  exclusions make it silent. Absence of findings is not proof of correctness.

---

## See also

- [Sync with Phil — 2026-09-17](../SyncWithPhil_2026-09-17_StreamingCells_ManualRuntimeDataLayers_transcript.md)
  — the session this plan comes from, and the CL 2049874 breakdown
- [Sync with Phil — 2026-08-27](../SyncWithPhil_2026-08-27_RuntimeDataLayers_transcript.md)
  — where the warning was requested, with the Hogsmeade examples
- [TeamCity jobs](TeamCityJobs.md) — the rule pass, its switches and the reporting pipeline
- [World Partition rules](WorldPartitionRules.md) — the rule families the pass applies
- [Rule engine mechanics](WorldPartitionRulesAnalysis/RuleEngineMechanics.md) — matching,
  exclusions and application order
