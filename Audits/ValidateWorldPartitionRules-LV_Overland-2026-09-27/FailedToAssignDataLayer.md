Parent: [Validate World Partition Rules — LV_Overland, 2026-09-27](README.md)

# Audit — "Failed to assign DataLayer" warnings on `LV_Overland`

Status: proposal (no change applied)
Scope: every `Failed to assign DataLayer` warning of one *Validate WP Rules* pass
Source: `Sundance_Validate_27September_validate-LV_Overland.log` (log of September 27, 2026 8:44 AM,
`LV_Overland`, UE 5.8.2, CL 2095946), reviewed in `WPRulesReviewer` and exported as `report.txt` on
October 1, 2026. Figures are measured on the **log**, not on the export — see §2 and §9 for why.
Control runs: `Sundance_Apply_22September_'LI_Hogsmeade'.log`, `Sundance_Apply_25September_'Missions'.log`,
`Sundance_Validate_23September_validate-LV_Overland.log`
Raw data: [`data/failed-to-assign-datalayer-inventory.csv`](data/failed-to-assign-datalayer-inventory.csv) (331 rows)

Companion audits: [Failed to retrieve Data Asset](FailedToRetrieveDataLayerAsset.md)
and [Missing DataLayer](MissingDataLayer.md) — same pass, same `DataLayer`
pipeline, but **real** findings. This audit is the opposite case: the largest family of the run is
not a content defect at all.

## Contents

- [1. Executive summary](#1-executive-summary)
- [2. What the warning means](#2-what-the-warning-means)
- [3. Measured facts](#3-measured-facts)
  - [3.1 Volume](#31-volume)
  - [3.2 One DataLayer accounts for almost everything](#32-one-datalayer-accounts-for-almost-everything)
  - [3.3 The same run assigns everything except DataLayers](#33-the-same-run-assigns-everything-except-datalayers)
  - [3.4 Apply versus Validate — the decisive comparison](#34-apply-versus-validate--the-decisive-comparison)
  - [3.5 Localisation — no content signal](#35-localisation--no-content-signal)
  - [3.6 Two hypotheses the measurements kill](#36-two-hypotheses-the-measurements-kill)
- [4. Root cause](#4-root-cause)
  - [Why the engine-side defect matters beyond the noise](#why-the-engine-side-defect-matters-beyond-the-noise)
- [5. Proposed corrections](#5-proposed-corrections)
  - [Option A — give the `-ValidateOnly` DataLayer path a dry-run branch (recommended)](#option-a--give-the--validateonly-datalayer-path-a-dry-run-branch-recommended)
  - [Option B — stop reporting the family as a review item (ship independently)](#option-b--stop-reporting-the-family-as-a-review-item-ship-independently)
  - [Option C — treat the 84 785 actors as content to fix](#option-c--treat-the-84-785-actors-as-content-to-fix)
  - [Recommendation](#recommendation)
- [6. The test that identifies the mechanism](#6-the-test-that-identifies-the-mechanism)
- [7. What this fix does not solve](#7-what-this-fix-does-not-solve)
- [8. Verification plan](#8-verification-plan)
- [9. Appendix — reproducing the figures](#9-appendix--reproducing-the-figures)

---

## 1. Executive summary

The run reports **85 490 `Failed to assign DataLayer` warnings** across **84 785 distinct actors** —
**92.5 % of every warning the pass emits**. Taken at face value it reads as a catastrophic content
failure: two thirds of the actors the builder touched were unable to receive their DataLayer.

It is not a content failure. **It is an artefact of the `-ValidateOnly` flag.**

**Root cause.** `-ValidateOnly` is meant to report what the builder *would* change without writing
anything. On the `HLODLayer`, `RuntimeGrid` and `IncludeInHLOD` paths it does exactly that: the same
run logs 9 504 successful `Applied …` lines and **zero** `Failed to assign …`. The DataLayer path
behaves differently — it runs the real assignment call, the call cannot complete because nothing may
be mutated, and the generic failure branch logs a `Warning`. The log therefore reports a dry-run
outcome using the vocabulary of a hard failure.

**Evidence that settles it.** The *Apply* pass of September 22 processed 7 715 Hogsmeade actors with
the same rules and the same DataLayers and produced **0** `Failed to assign DataLayer` warnings.
**1 449 of those actors — provably clean under Apply — are reported as failures by the Validate
pass.** Same actors, same rules, same world; the only difference is `-ValidateOnly`.

**Recommendation.** Do **not** touch content, and do **not** chase these 84 785 actors. Fix the
builder's `-ValidateOnly` DataLayer path so it reports a planned assignment instead of a failure
(option A), and have `WPRulesReviewer` stop counting the family as an anomaly until it does
(option B, shippable immediately and independent of the engine fix).

| | Before | After (option A) |
| --- | ---: | ---: |
| `Failed to assign DataLayer` warnings | 85 490 | 0 |
| Share of all warnings in the pass | 92.5 % | 0 % |
| Actors to touch | 0 | 0 |
| Assets to author | 0 | 0 |
| Code paths to change | — | 1 (`-ValidateOnly` DataLayer branch) |

What the audit does **not** clear is listed in §7: 730 `Failed to retrieve DataLayerAsset`, 1 460
`Missing DataLayer` and 2 606 untargeted runtime DataLayers are real findings that survive this fix.

---

## 2. What the warning means

```
LogWorldPartitionRules: Warning: Failed to assign DataLayer 'DL_RENDER'
    to actor 'LV_Overland/Hogsmeade/.../SM_CobbleStreet_Block_B1238'
    using rule 'DA_RENDER_Rules'.
```

The rule matched the actor **and** resolved its target `DataLayerAsset` — resolution failures are a
different, separately logged family (`Failed to retrieve DataLayerAsset`, §7). What failed is the
assignment itself: the builder asked the world to put the actor in the layer and the operation did
not take effect.

`WPRulesReviewer` leaves this shape as `WarningKind.Other` and recovers the family from the message
wording:

```33:36:Tools/WPRulesReviewer/src/WPRulesReviewer.Core/Models/IssueTypes.cs
    private static string OfMessage(string message)
    {
        if (message.StartsWith("Failed to assign DataLayer '", StringComparison.Ordinal))
            return "Failed to assign DataLayer";
```

Because the kind stays `Other`, the oracle falls through to its default branch:

```129:131:Tools/WPRulesReviewer/src/WPRulesReviewer.Core/Oracle/OracleEvaluator.cs
            default:
                Set(r, ReviewStatus.NeedsReview, AnomalySeverity.Low, "Rule warning");
                break;
```

So all 85 490 rows land in *Needs review* with the flattened reason `Rule warning`. That is why the
family is invisible in the exported `report.txt`: the specific message is replaced by the generic
status reason, and the 90 529-row *Needs review* section gives the reviewer no way to tell this
family apart. The figures below were therefore measured on the **source log**, not on the export
(see §9).

---

## 3. Measured facts

### 3.1 Volume

| Metric | Value |
| --- | ---: |
| `Failed to assign DataLayer` warnings | 85 490 |
| Distinct actors | 84 785 |
| Distinct (actor, DataLayer) pairs | 84 943 |
| Actors processed by the pass | 122 234 |
| **Failure rate over processed actors** | **69.4 %** |
| Warnings in the whole pass | 92 452 |
| **Share of all warnings** | **92.5 %** |
| Distinct DataLayers requested | 69 |
| Distinct rules involved | 11 |

Rows per actor are essentially 1:1 — 85 490 rows for 84 943 distinct (actor, DataLayer) pairs and
84 785 distinct actors. The 158 extra pairs are actors matched by two or three different DataLayer
rules. Unlike the *Missing DataLayer* family, **there is no 2× log duplication here** — the row count
is the occurrence count.

### 3.2 One DataLayer accounts for almost everything

| DataLayer | Rule | Warnings | Share |
| --- | --- | ---: | ---: |
| `DL_RENDER` | `DA_RENDER_Rules` | 82 857 | 96.9 % |
| `DL_LIGHTING` | `DA_LIGHTHING_Rules` | 1 050 | 1.2 % |
| `DL_HOGSMEADE` | `DA_HOGSMEADE_Rules` | 652 | 0.8 % |
| `DL_TECH` | `DA_TECH_Rules` | 604 | 0.7 % |
| `DL_HM_EXT` | `DA_HM_EXT_Rules` | 181 | 0.2 % |
| `DL_AUDIO` | `DA_AUDIO_Rules` | 50 | < 0.1 % |
| `DL_NAV`, `DL_SKY`, `DL_ANIMATION` | respective rules | 9 | < 0.1 % |
| 60 × `DL_HM_*` / `DL_WE_*` | `DA_HM_INT_Rules`, `DA_WORLD_EVENTS_Rules` | 87 | 0.1 % |

The shape matters: `DL_RENDER` is a **project-wide, broad-match layer** applied to essentially every
renderable actor. A real per-actor assignment bug would not concentrate 96.9 % of its volume on the
single rule with the widest match set — but a *systemic* failure of the DataLayer path would, because
that rule simply evaluates the most actors. The distribution is a volume profile of the rules, not a
map of defects.

### 3.3 The same run assigns everything *except* DataLayers

Counted in the one `-ValidateOnly` log:

| Assignment type | `Applied …` | `Failed to assign …` |
| --- | ---: | ---: |
| `RuntimeGrid` | 7 217 | **0** |
| `IncludeInHLOD` | 1 213 | **0** |
| `HLODLayer` | 1 074 | **0** |
| **`DataLayer`** | **2** | **85 490** |

This is the core anomaly. Three of the four assignment paths complete normally under
`-ValidateOnly` and report what they would do. The fourth fails 85 490 times out of 85 492 attempts
— a 99.998 % failure rate confined to one code path. No content defect distributes itself that way.

The two exceptions are worth recording, because they prove the validate path *does* exercise the
real mutation code for DataLayers rather than short-circuiting it:

```
LogWorldPartitionRules: Display: Applied DataLayer 'DL_SKY' to actor
    'LV_Overland/Hogsmeade/.../LI_Scrivenshafts_EXT/DayNightSkyRigActor' using rule 'DA_SKY_Rules'
LogWorldPartitionRules: Display: Applied DataLayer 'DL_SKY' to actor
    'LV_Overland/Hogsmeade/.../LI_Scrivenshafts_EXT/GlobalLightRigActor' using rule 'DA_SKY_Rules'
```

A pass invoked with `-ValidateOnly` should not be reporting *applied* DataLayers at all. Whatever
makes those two succeed is the same mechanism that makes the other 85 490 "fail", and §4 proposes
the test that identifies it.

### 3.4 Apply versus Validate — the decisive comparison

Four runs of the same builder on the same world, differing only in `-ValidateOnly` and in the
`-ContainOutlinerPathSubstrings` filter:

| Run | `-ValidateOnly` | Filter | Actors processed | `Applied DataLayer` | `Failed to assign DataLayer` |
| --- | :---: | --- | ---: | ---: | ---: |
| Apply, Sep 22 | no | `LI_Hogsmeade` | 7 715 | 63 | **0** |
| Apply, Sep 25 | no | `Missions` | — | 60 | **0** |
| Validate, Sep 23 | **yes** | `mission` | 31 788 | 29 | **9 227** |
| Validate, Sep 27 | **yes** | `Hogsmeade` | 122 234 | 2 | **85 490** |

`-ValidateOnly` is the only variable that tracks the outcome. With it, tens of thousands of
failures; without it, none — on overlapping actor sets, with the same rules, the same DataLayers and
the same engine binary.

The intersection closes the argument. Of the 84 785 actors the Validate pass reports as failures,
**1 449 were processed by the Apply pass without a single warning**:

```
LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade/Stations/Site Locations/Area_HM_ErnieLocation
LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade/Lighting/GI Lighting-EDITORONLY/GlobalLightRigActor
LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade/Tech/AI Paths/ai_westToHH
LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade/Gameplay/Climbables_Ledges/SM_Climbable14
LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade/Stations/Vendors/Teasdale/BP_StationEventResponse_GreetLong_Watering
```

(18.8 % of the Apply run's actor set; the remaining 81.2 % are outside the `Hogsmeade` filter of the
Validate run, so they were never compared.)

**One actor cannot be simultaneously broken and healthy.** These 1 449 are healthy, and the Validate
pass misreports them.

### 3.5 Localisation — no content signal

| Outliner area | Warnings | Share |
| --- | ---: | ---: |
| `Hogsmeade` | 80 583 | 94.3 % |
| `Region` | 4 893 | 5.7 % |
| `Missions` | 14 | < 0.1 % |

| Owning Level Instance (top 10) | Warnings |
| --- | ---: |
| `LI_HM_Streets_EXT` | 12 842 |
| `LI_HM_Plaza_EXT` | 5 877 |
| `LI_HM_StreetDressing_EXT` | 4 942 |
| `LI_Hogsmeade_River` | 4 155 |
| `LI_Building_K_EXT` | 2 745 |
| `LI_Building_K_Two_EXT` | 2 745 |
| `LI_Honeydukes_EXT` | 2 349 |
| `LI_Tomes_EXT` | 1 798 |
| `LI_ThreeBroom_EXT` | 1 777 |
| `LI_Puddifoots_EXT` | 1 543 |

The ranking is an actor-density ranking: streets, plaza and street dressing hold the most props, so
they hold the most warnings. The distribution follows `-ContainOutlinerPathSubstrings="Hogsmeade"`
exactly. No container, no prop family and no asset type is over-represented relative to its actor
count — the hallmark of a systemic failure rather than a content one.

### 3.6 Two hypotheses the measurements kill

| Hypothesis | Why it fails |
| --- | --- |
| *The `DataLayerAsset`s do not exist* | The 69 requested layers resolve fine: `DL_RENDER` is successfully applied 63 times in the Apply run. Unresolvable assets are reported separately as `Failed to retrieve DataLayerAsset` (730 rows, §7) and never reach the assign call. |
| *Actors inside Level Instances cannot receive a DataLayer* | 100 % of the 84 785 failing actors sit inside a Level Instance, which is suggestive — but the Apply run successfully assigns `DL_RENDER` to actors nested **two** Level Instances deep (`…/LI_Graveyard_EXT/LI_Graveyard_Pillar_D2/SM_Graveyard_Pillar_D_Body`). Nesting is not the discriminator; `-ValidateOnly` is. The 100 % figure is an artefact of the filter: all Hogsmeade content lives under `LI_Hogsmeade`. |

Depth distribution, for completeness: depth 7 — 62 090; depth 8 — 14 436; depth 9 — 8 285;
depth ≤ 6 — 550; depth 10 — 129. Spread across every nesting level, as a volume profile should be.

---

## 4. Root cause

```
WorldPartitionRuleBuilder, -ValidateOnly
  ├─ HLODLayer     → evaluate, log "Applied …"            (Display)   ✔ dry-run reported correctly
  ├─ RuntimeGrid   → evaluate, log "Applied …"            (Display)   ✔
  ├─ IncludeInHLOD → evaluate, log "Applied …"            (Display)   ✔
  └─ DataLayer     → evaluate, call the real assignment,
                     which cannot commit under -ValidateOnly,
                     fall into the generic failure branch,
                     log "Failed to assign DataLayer …"   (Warning)   ✘ dry-run reported as a failure
```

The three single-property paths write a `UPROPERTY` on the actor and can describe the intended value
without committing it. The DataLayer path goes through the data-layer editor API, and the validate
mode does not have a "would assign" branch for it: the call is made, it does not take effect, and the
error path logs a warning. The payload of that warning (`DataLayer`, `actor`, `rule`) is in fact the
**diff the builder would have applied** — correct information, wrong severity and wrong wording.

Two mechanisms remain consistent with the evidence, and they are **not** distinguishable from the
log alone:

- **(M1) No dry-run branch.** The assignment is attempted and reports failure because the actor's
  package is not checked out / the world is loaded read-only under `-BuildMachine -Unattended
  -ValidateOnly`.
- **(M2) Return value misread.** The API returns `false` for "nothing changed" as well as for
  "error", and the builder treats both as a failure. The Apply run supports this reading: it
  processed 7 715 actors and logged only 63 assignments, i.e. **99.2 % of actors were already in
  their target layer** — so "nothing changed" is by far the common case, and under `-ValidateOnly`
  it becomes the only case.

§6 gives the one-line test that separates them. Either way the conclusion for content is the same,
which is why this audit does not wait on that answer.

### Why the engine-side defect matters beyond the noise

- **It masks the real findings.** The pass has three genuine DataLayer-family problems totalling
  4 796 rows (§7). They are buried under 85 490 false positives — an 18:1 noise ratio.
- **It makes `-ValidateOnly` untrustworthy for DataLayers.** The flag exists so content can be
  checked without a submit. For the DataLayer half of the pipeline it currently reports nothing
  usable, so DataLayer regressions can only be caught by an Apply run, after the fact.
- **The two stray `Applied DataLayer` lines (§3.3) mean a validate pass is mutating state.** A
  read-only verification pass that sometimes succeeds in writing is a correctness problem in its own
  right, independently of the logging.

---

## 5. Proposed corrections

Option A fixes the engine; option B fixes the reviewer. They are **complementary** — B is shippable
today and does not depend on A. Option C is the trap to avoid.

### Option A — give the `-ValidateOnly` DataLayer path a dry-run branch (recommended)

| # | Action | Target | Reversible |
| --- | --- | --- | --- |
| 1 | Run the test in §6 to establish whether the cause is M1 or M2 | — | — |
| 2 | Under `-ValidateOnly`, resolve the target layer and log the planned assignment as `Display` (e.g. `Would assign DataLayer 'X' to actor 'Y' using rule 'Z'`) instead of calling the mutating API | `WorldPartitionRuleBuilder`, DataLayer branch | yes |
| 3 | Distinguish "already assigned" (no log) from "genuine failure" (`Warning`), so the family keeps its diagnostic value in Apply mode | same | yes |
| 4 | Make the three stray `Applied DataLayer` / 2-success cases impossible: assert that no mutation occurs under `-ValidateOnly` | same | yes |
| 5 | Re-run *Validate WP Rules* on `LV_Overland` and confirm the count | TeamCity | — |

**Cost:** one builder code path. **No content change, no asset authored, no actor touched.**
**Residual after the fix:** 0 rows of this family; the pass drops from 92 452 warnings to ≈ 6 962,
and the 5 259 real findings of §7 become visible.

**Risk to check before committing.** Step 3 must not silence a real failure. Once the dry-run branch
exists, run one Apply pass on a scratch stream and confirm that deliberately breaking one
assignment (e.g. by removing a `DataLayerInstance` from the level) still produces exactly one
`Failed to assign DataLayer` warning. A fix that reaches zero by making the warning unreachable is
worse than the current state.

### Option B — stop reporting the family as a review item (ship independently)

`WPRulesReviewer` currently flattens all 85 490 rows into `NeedsReview / Low` with the reason
`Rule warning` (§2), which is both wrong and unactionable. Three changes, in the order they pay off:

| # | Change | Where |
| --- | --- | --- |
| 1 | Add `WarningKind.FailedToAssignDataLayer`, parsed from the message, so the family is addressable instead of falling into `Other` | `LogParser.ParseWarning` |
| 2 | Classify it as `KnownNoise` **when the source log was produced with `-ValidateOnly`**, with the reason "reported by the validate pass; not a content defect" | `OracleEvaluator.ClassifyWarning` |
| 3 | Parse the `commandline=` metadata line of the log into `SessionReport` so rule 2 can be conditional, and surface the mode as a badge on the session tab | `LogParser.ParseStream`, `SessionReport` |

Step 3 is the one that makes this safe: the same message in an **Apply** log is a genuine failure and
must stay an anomaly. Suppressing the family unconditionally would hide real regressions. The flag
is already in the log, 24 lines in:

```
commandline="" Sundance … -Builder=WorldPartitionRuleBuilder -DataLayerRules -HLODLayerRules
    -RuntimeGridRules -ValidateOnly -ContainOutlinerPathSubstrings="Hogsmeade" … LV_Overland""
```

**Effect:** the September 27 session goes from 90 529 *Needs review* rows to ≈ 5 039, and the
*Needs review* tab becomes usable again.

### Option C — treat the 84 785 actors as content to fix

**Not recommended.** Any per-actor remediation (checking out 84 785 actor packages, re-running an
Apply pass over them, authoring layers) addresses a defect that is not in the content. It would
produce the largest changelist in the project's history, touch every Hogsmeade actor package, and
leave the next `-ValidateOnly` pass reporting exactly the same 85 490 warnings. Recorded here so
that the option is explicitly rejected rather than silently available.

### Recommendation

Land **option B** now — it is contained in the reviewer, needs no engine change, and immediately
restores the signal-to-noise ratio of the *Needs review* tab. Open **option A** against the builder
with §6 as the reproduction. Reject option C.

---

## 6. The test that identifies the mechanism

One run separates M1 from M2 (§4). On a scratch stream, pick an actor that the Apply pass is known
to modify — one of the 63 from the September 22 run, e.g.

```
LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade/Streets/LI_Graveyard_EXT/LI_Graveyard_Pillar_D2/SM_Graveyard_Pillar_D_Body
```

and run the builder twice with `-ValidateOnly`, before and after an Apply pass has put it in
`DL_RENDER`:

```powershell
# -ActorClassNames / -ContainOutlinerPathSubstrings narrowed to the single actor
UnrealEditor-Cmd.exe Sundance -run=WorldPartitionBuilderCommandlet `
    -Builder=WorldPartitionRuleBuilder -DataLayerRules -ValidateOnly `
    -ContainOutlinerPathSubstrings="LI_Graveyard_Pillar_D2" LV_Overland
```

| Observation | Mechanism | Consequence for option A |
| --- | --- | --- |
| Warning appears **both** before and after the actor is correctly assigned | **M1** — no dry-run branch; the call can never commit | Step 2 is sufficient |
| Warning appears **only after** the actor is already in the layer | **M2** — "nothing changed" misread as failure | Step 3 is the actual fix, and the same bug is latent in Apply mode |

Record the outcome in this document before touching the builder.

---

## 7. What this fix does **not** solve

Removing 85 490 false positives leaves the pass with 6 962 warnings, of which **4 796 are real
DataLayer-family findings**. They are independent of this audit and each has its own remediation:

| Family | Rows | Status |
| --- | ---: | --- |
| `Failed to retrieve DataLayerAsset` | 730 | **Real — and reproduces in Apply mode.** 705 distinct `DataLayerAsset`s fail to resolve, and **703 of them fail in the September 22 Apply run too**, so unlike this audit's family it is not a validate artefact. Root cause and remediation: [Failed to retrieve Data Asset](FailedToRetrieveDataLayerAsset.md) — `DA_HM_INT_Rules` leaking down the outliner path, 724 of 730 rows noise. |
| `Missing DataLayer` | 1 460 | **Real.** Covered by [Missing DataLayer](MissingDataLayer.md) — one rule targeting nested prop Level Instances. |
| Runtime DataLayer assigned but targeted by no rule | 2 606 | **Real.** Covered by [Runtime DataLayer without rule](RuntimeDataLayerWithoutRule.md). |
| Multiple DataLayer rule matches | 0 | Not present in this pass. All 463 multiple-match warnings are `HLODLayer` — see [Multiple HLODLayer rule matches](MultipleHLODLayerRules.md). |

The cross-run check is the contribution this audit makes to the others: **the only DataLayer family
of the pass that reproduces on both the Apply and the Validate path is
`Failed to retrieve DataLayerAsset`**. That makes it the one certain to affect shipped streaming
behaviour, and the one to prioritise once the noise of the present family is gone.

---

## 8. Verification plan

1. Run the §6 test and record whether the mechanism is M1 or M2.
2. Confirm in the editor that `DL_RENDER` exists as a `DataLayerInstance` on `LV_Overland` and that a
   spot-check of 5 actors from [the inventory](data/failed-to-assign-datalayer-inventory.csv),
   drawn from 3 different Level Instances, are **already** in it. This closes M2 by observation.
3. Land option B steps 1–3 and re-import `Sundance_Validate_27September_validate-LV_Overland.log`.
   Expect: *Needs review* ≈ 5 039, `Failed to assign DataLayer` reclassified as known noise, and the
   session tab showing a `ValidateOnly` badge.
4. Re-import `Sundance_Apply_22September_'LI_Hogsmeade'.log` and confirm the suppression did **not**
   apply: the mode badge must read `Apply`, and the family must still be eligible for `Anomaly`.
5. After the engine fix (option A), re-run *Validate WP Rules* on `LV_Overland` and confirm:
   `Failed to assign DataLayer` = 0, `Applied DataLayer` = 0 (nothing is written under
   `-ValidateOnly`), and the counts of the families in §7 are **unchanged** — the fix must be purely
   a logging change.
6. Confirm `Applied HLODLayer` (1 074), `Applied RuntimeGrid` (7 217) and `Applied IncludeInHLOD`
   (1 213) are unchanged; a regression there would mean the dry-run branch was applied too broadly.

---

## 9. Appendix — reproducing the figures

The exported `report.txt` **cannot** be used for this family: the oracle replaces the message with
the generic status reason `Rule warning` before the export is written (§2), so the 85 490 rows are
indistinguishable from any other unmodelled warning. Every figure below is measured on the source
logs in `%APPDATA%\WPRulesReviewer\Logs`.

```powershell
$val = "$env:APPDATA\WPRulesReviewer\Logs\Sundance_Validate_27September_validate-LV_Overland.log"
$app = "$env:APPDATA\WPRulesReviewer\Logs\Sundance_Apply_22September_'LI_Hogsmeade'.log"

# 85 490 — the family, and 0 in the Apply control run
rg -c "Failed to assign DataLayer" $val
rg -c "Failed to assign DataLayer" $app

# §3.3 — only the DataLayer path fails
foreach ($p in @("Applied DataLayer", "Applied HLODLayer", "Applied RuntimeGrid",
                 "Applied IncludeInHLOD", "Failed to assign HLODLayer",
                 "Failed to assign RuntimeGrid", "Failed to assign IncludeInHLOD")) {
    "{0,-32} {1}" -f $p, (rg -c $p $val)
}

# the -ValidateOnly flag, line 24 of the log
(Get-Content $val -TotalCount 40 | Select-String -SimpleMatch 'commandline=').Line

# §3.1 / §3.2 / §3.5 — distinct actors, layers, rules and containers
$rx = [regex]"Failed to assign DataLayer '([^']*)' to actor '([^']+)'(?: using rule '([^']+)')?"
$actors = [System.Collections.Generic.HashSet[string]]::new()
$byDL = @{}
foreach ($line in [System.IO.File]::ReadLines($val)) {
    if (-not $line.Contains("Failed to assign DataLayer")) { continue }
    $m = $rx.Match($line); if (-not $m.Success) { continue }
    [void]$actors.Add($m.Groups[2].Value)
    $k = $m.Groups[1].Value
    if ($byDL.ContainsKey($k)) { $byDL[$k]++ } else { $byDL[$k] = 1 }
}
"distinct actors = $($actors.Count)"        # 84 785
$byDL.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 10

# §3.4 — the 1 449 actors clean under Apply yet failing under Validate
$rxProc = [regex]"Applying rules on actor:\s*(.+?)\s*$"
$clean = [System.Collections.Generic.HashSet[string]]::new()
foreach ($line in [System.IO.File]::ReadLines($app)) {
    if ($line.Contains("Applying rules on actor:")) {
        $m = $rxProc.Match($line); if ($m.Success) { [void]$clean.Add($m.Groups[1].Value) }
    }
}
($actors | Where-Object { $clean.Contains($_) }).Count   # 1 449
```

[`data/failed-to-assign-datalayer-inventory.csv`](data/failed-to-assign-datalayer-inventory.csv)
holds the aggregated inventory — 331 rows, one per
`(DataLayer, Rule, Area, OwningLevelInstance)` tuple, with a `Warnings` count summing to 85 490. It
is aggregated rather than per-actor on purpose: a per-actor export of 84 785 rows would weigh ~12 MB
and carry no information the aggregate does not, since the family has no per-actor signal (§3.5). It
is the working set for the spot-checks of §8 step 2.
