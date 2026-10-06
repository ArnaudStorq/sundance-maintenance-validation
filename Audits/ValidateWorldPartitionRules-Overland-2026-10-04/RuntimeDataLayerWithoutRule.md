Parent: [Validate World Partition Rules — Overland only, 2026-10-04](README.md)

# Audit — "Runtime DataLayer without rule" warnings on `LV_Overland` (Overland only)

Status: proposal (no change applied)
Scope: every `Runtime DataLayer without rule` warning of the *validate Overland Only* pass
Source: TeamCity job [`#2111348`](https://slc-teamcity.wbiegames.com/) *validate Overland Only*,
run of October 4, 2026 06:00 — log opened `10/04/26 08:48:27`, 73.5 MB, 345 215 lines
Build version: `++sun+Dev-TeamCity-Code-CL-2110752`
Raw data: [`data/runtime-datalayer-without-rule-inventory.csv`](data/runtime-datalayer-without-rule-inventory.csv) (1 054 rows)
Companion: [Runtime DataLayer without rule — Hogsmeade, 2026-09-27](../ValidateWorldPartitionRules-LV_Overland-2026-09-27/RuntimeDataLayerWithoutRule.md)
— same warning family, **complementary scope** (that run was Hogsmeade; this one *discards* Hogsmeade)

## Contents

- [1. Executive summary](#1-executive-summary)
- [2. What the warning means](#2-what-the-warning-means)
- [3. Measured facts](#3-measured-facts)
  - [3.1 Volume and shape](#31-volume-and-shape)
  - [3.2 Per family](#32-per-family)
  - [3.3 The new `Matching DataLayer rules` field](#33-the-new-matching-datalayer-rules-field)
  - [3.4 The two populations that carry 91 % of the rows](#34-the-two-populations-that-carry-91--of-the-rows)
- [4. Proposal](#4-proposal)
  - [Bucket A — Author the per-conversation Sanctuary rule (105 rows)](#bucket-a--author-the-per-conversation-sanctuary-rule-105-rows)
  - [Bucket B — Author the Automation rule (11 rows)](#bucket-b--author-the-automation-rule-11-rows)
  - [Bucket C — Clear the ConversationHub child-mesh residue (296 rows)](#bucket-c--clear-the-conversationhub-child-mesh-residue-296-rows)
  - [Bucket D — Clear the `DL_OVERLAND` residue (557 rows)](#bucket-d--clear-the-dl_overland-residue-557-rows)
  - [Bucket E — Settle the World Event gameplay layers (64 rows)](#bucket-e--settle-the-world-event-gameplay-layers-64-rows)
  - [Bucket F — Cross-region leaks and one-offs (21 rows)](#bucket-f--cross-region-leaks-and-one-offs-21-rows)
- [5. Verification plan](#5-verification-plan)
- [6. Why this run differs from 2026-09-27](#6-why-this-run-differs-from-2026-09-27)
- [7. Appendix — reproducing the figures](#7-appendix--reproducing-the-figures)

---

## 1. Executive summary

The *validate Overland Only* pass reports **1 054 `Runtime DataLayer without rule` warnings** on
**977 distinct actors** across **136 distinct DataLayers**. It is a validation-only run
(`-ValidateOnly`): it loaded 216 636 actors and changed nothing.

Unlike the [2026-09-27 run](../ValidateWorldPartitionRules-LV_Overland-2026-09-27/RuntimeDataLayerWithoutRule.md),
this one **discards `hogsmeade`, `hogwarts`, `mission` and `dungeon`**, so what remains is almost
entirely the Overland region proper plus the **Sanctuary** content that lives under it. Two
populations carry 91 % of the rows:

- **`DL_OVERLAND` residue (557 rows)** — the same hand-assigned `DL_OVERLAND` the companion audit
  describes, now seen from the Overland side. 255 of these sit under `LV_Overland/Sanctuary`, which
  `DA_OVERLAND_Rules` explicitly **excludes**, so no rule will ever reproduce them.
- **Sanctuary ConversationHub layers (401 rows)** — per-conversation DataLayers
  (`DL_SANCTUARY_ConversationHub_<Name>_<variant>`) that are hand-assigned. The existing
  `DA_SANTUARY_ConversationHub_Rules` only assigns the **generic** parent layer, not the
  per-conversation variant.

**The split that matters here is not coverage (as in 2026-09-27) but *reproducibility*.** The new
`Matching DataLayer rules` field in the log says, per actor, whether any rule even looks at it. 105
of the Sanctuary rows map a Level Instance name **1:1** onto its DataLayer name — a textbook
pattern-rule case, already solved once for `DA_SANTUARY_Vivarium_Rules`. The rest is residue to clear
or gameplay layers to confirm.

**Recommendation.** Author 2 rule assets (116 rows become reproducible), clear two residue
populations (853 rows), and refer 85 rows to their content owners.

| Bucket | Fix | Rows |
| --- | --- | ---: |
| A — ConversationHub Level Instances | Author `DA_SANTUARY_ConversationHub_PerConversation_Rules` | 105 |
| B — `POI_*` automation | Author `DA_AUTOMATION_Rules` | 11 |
| C — ConversationHub child meshes | Clear the redundant sub-layer | 296 |
| D — `DL_OVERLAND` residue | Clear the layer | 557 |
| E — World Event gameplay layers | Content decision required | 64 |
| F — Cross-region leaks / one-offs | Manual triage | 21 |

---

## 2. What the warning means

```
LogWorldPartitionRules: Warning: Actor '<Path>' is assigned to runtime DataLayer '<DL_*>' but no
DataLayer rule targets it. An unjustified runtime DataLayer places the actor in its own streaming
cell, which adds draw calls. Remove the DataLayer from the actor, or extend a rule to cover it.
DataLayer asset: '<asset>'. Matching DataLayer rules: [<candidate rules>].
```

The actor carries a **runtime** DataLayer in its own package, and no asset registered under
`DataLayerRulesForActorSave` assigns that layer to that actor. DataLayer assignment is **additive**
and nothing cleans up manual entries, so the orphan layer survives every rules pass and still costs a
streaming cell. See [World Partition rules](../../ReferenceDocs/WorldPartitionRules.md) and the
[manual runtime Data Layer cleanup plan](../../ReferenceDocs/DevelopmentPlan-ManualRuntimeDataLayerCleanup.md).

---

## 3. Measured facts

### 3.1 Volume and shape

| Metric | Value |
| --- | ---: |
| Warning rows | 1 054 |
| Distinct actors | 977 |
| Distinct DataLayers | 136 |
| Actors loaded by the pass | 216 636 |
| All-family warnings in the run | 54 892 |
| Severity | 100 % `Low` / *Needs review* |

### 3.2 Per family

| Family | Rows | Dominant actor kind |
| --- | ---: | --- |
| `DL_OVERLAND` | 557 | 519 meshes |
| Sanctuary ConversationHub | 401 | 289 meshes, 105 Level Instances |
| World Event (`DL_WE_*`) | 64 | 55 Blueprints |
| Automation (`DL_AUTOMATION`) | 11 | `POI_*` |
| Quidditch | 5 | Level Instances |
| Mission (leak) | 5 | mixed |
| Sanctuary Pensieve | 4 | Level Instances |
| London (leak) | 4 | mixed |
| Expansion Tent | 2 | Level Instances |
| Dungeon (leak) | 1 | — |

### 3.3 The new `Matching DataLayer rules` field

This run's log carries a field the 2026-09-27 log did not: for each warning it lists the rule assets
whose **conditions match the actor** — the candidate rules that *could* be extended to cover it. It
is the detection improvement the
[cleanup plan asked for](../../ReferenceDocs/DevelopmentPlan-ManualRuntimeDataLayerCleanup.md#step-2--answer-phils-exclusivity-question-from-the-report),
now in the log instead of only the JSON report.

| `Matching DataLayer rules` | Rows | Reading |
| --- | ---: | --- |
| `[DA_RENDER_Rules]` | 529 | a `StaticMeshActor` rule matches; it would assign `DL_RENDER`, not the manual layer |
| `[none]` | 306 | **no** rule looks at the actor at all — pure residue, nothing will reproduce it |
| `[DA_SANTUARY_Rules, DA_SANTUARY_ConversationHub_Rules]` | 105 | the ConversationHub Level Instances — the rule assigns the generic layer, not the variant |
| `[DA_TECH_Rules]` | 75 | a `BP_*` path rule matches; it would assign `DL_TECH` |
| `[DA_SANTUARY_Rules]` | 20 | Sanctuary Level Instance matched by the generic rule only |
| `[DA_OVERLAND_Rules]` | 10 | an Overland rule matches but targets `DL_OVERLAND`, not the manual layer |
| others | 9 | `DA_PROCEDURAL`, `DA_NAV`, `DA_AUDIO`, `DA_WORLD_EVENTS`, … |

The rules referenced above are catalogued in the
[rule decision flow charts](../../ReferenceDocs/WorldPartitionRulesFlowCharts.md): `DA_RENDER_Rules`
(row 11, `StaticMeshActor` → `DL_RENDER`), `DA_OVERLAND_Rules` (row 28, which **excludes**
`LI_Sanctuary`), `DA_SANTUARY_ConversationHub_Rules` (row 31, generic layer only) and the model to
copy, `DA_SANTUARY_Vivarium_Rules` (row 32, pattern `LI_Sanctuary_Vivarium_` → `DL_SANCTUARY_VIVARIUM_`).

### 3.4 The two populations that carry 91 % of the rows

**`DL_OVERLAND` (557).** Split by region of the actor path:

| Region | Rows | Note |
| --- | ---: | --- |
| `LV_Overland/Sanctuary/…` | 255 | `DA_OVERLAND_Rules` excludes `LI_Sanctuary` — **no rule can reproduce these** |
| `LV_Overland/Region/…` | 164 | mountain blockout, world-event dressing |
| `LV_Overland/Trees/…` | 49 | Nanite tree/foliage meshes |
| `MFF_Dressing`, `Environment`, `HandDressing`, loose foliage | 89 | scattered dressing |

**Sanctuary ConversationHub (401).** Split by actor kind:

| Actor kind | Rows | Candidate rule | Meaning |
| --- | ---: | --- | --- |
| Level Instance | 105 | `DA_SANTUARY_Rules, DA_SANTUARY_ConversationHub_Rules` | LI name maps **1:1** to the layer, e.g. `LI_Sanctuary_ConversationHub_Bertram_01_C` ⇒ `DL_SANCTUARY_ConversationHub_Bertram_01_C` |
| Mesh | 289 | `DA_RENDER_Rules` | a `SM_*` **inside** one of those LIs, carrying the **same** layer as its container — redundant |
| Blueprint | 7 | mixed | props inside the hubs |

---

## 4. Proposal

### Bucket A — Author the per-conversation Sanctuary rule (105 rows)

The 105 Level Instances each carry exactly the DataLayer named after them. This is the same shape
`DA_SANTUARY_Vivarium_Rules` already solves with a name pattern. Author one asset:

| New rule asset | Target | Match criteria |
| --- | --- | --- |
| `DA_SANTUARY_ConversationHub_PerConversation_Rules` | pattern `LI_Sanctuary_ConversationHub_` → `DL_SANCTUARY_ConversationHub_` | `LevelInstance` AND `path ~ 'LI_Sanctuary_ConversationHub_'` |

Registration in `DefaultEditor.ini`, under
`[/Script/WorldBuildingEditor.WorldPartitionRuleSettings]`:

```ini
+DataLayerRulesForActorSave=/Game/Levels/Sanctuary/DataAssets/DA_SANTUARY_ConversationHub_PerConversation_Rules.DA_SANTUARY_ConversationHub_PerConversation_Rules
```

This is **behaviour-preserving**: the rule re-creates precisely the assignment the Level Instances
already carry, so a validate pass turns these 105 rows from *Warning* into *Applied* with no
streaming change. Order it **before** the generic `DA_SANTUARY_ConversationHub_Rules` so the specific
layer wins (first matching rule wins — see
[rule engine mechanics](../../ReferenceDocs/WorldPartitionRulesAnalysis/RuleEngineMechanics.md)), and
confirm with the narrative owner that the variant layer, not the generic one, is the intended target.

### Bucket B — Author the Automation rule (11 rows)

11 `POI_*` actors carry `DL_AUTOMATION` with no rule. Identical to the
[2026-09-27 proposal](../ValidateWorldPartitionRules-LV_Overland-2026-09-27/RuntimeDataLayerWithoutRule.md#bucket-a--promote-deliberate-assignments-to-rules-888-rows);
author `DA_AUTOMATION_Rules` (actor name prefix `POI_` → `DL_AUTOMATION`). The two audits agree on
this population, so it should be landed once, globally — after verifying `POI_` actors in other
worlds, since the ini is not per-world.

### Bucket C — Clear the ConversationHub child-mesh residue (296 rows)

289 static meshes (and 7 Blueprints) carry the **same** per-conversation layer as the Level Instance
that already contains them. Once Bucket A reproduces the layer on the Level Instance, the per-mesh
copy is redundant: it only ever splits the hub into extra cells. Clear it.

Caveat before landing: confirm with the narrative owner that sub-conversation streaming is driven at
the **Level Instance** level, not per prop. If it is per-LI (the Vivarium precedent says it is), the
child-mesh layers are pure authoring residue. Clear with a targeted commandlet rather than
`OutlinerPathsToClearDataLayers`, because the meshes are **nested inside** the LIs that Bucket A must
keep layered — a path clear would strip both.

### Bucket D — Clear the `DL_OVERLAND` residue (557 rows)

The same hand-assigned `DL_OVERLAND` the companion audit tracks. 255 rows under
`LV_Overland/Sanctuary` are the clearest case: `DA_OVERLAND_Rules` **excludes** `LI_Sanctuary`, so no
rule reproduces them and they are unambiguously removable. The other 302 are Overland dressing/foliage.

**Coverage caveat — do not blanket-clear yet.** The 2026-09-27 audit showed this family splits into
*whole-container intent* (promote to a rule) versus *copy/paste residue* (clear), and the
discriminator is **coverage** = flagged actors ÷ all actors in the container. That number needs the
full actor inventory, which this raw log does not enumerate (only warned and applied actors are
logged). Produce the `WPRulesReviewer` export for this run and split bucket D by container coverage
exactly as the companion audit did before clearing. The 255 Sanctuary-excluded rows can proceed
independently, since no rule targets them under any coverage.

### Bucket E — Settle the World Event gameplay layers (64 rows)

55 Blueprints (`BP_WE_*`, `BP_AMT_*`, `BP_BRK_*`, `BP_WE_AvaSpawner_*`) and a few Level Instances
carry `DL_WE_*` gameplay layers, matched only by `DA_TECH_Rules`/`DA_OVERLAND_Rules` (which assign
`DL_TECH`/`DL_OVERLAND`, never the World Event layer). These are **designer-assigned gameplay layers**,
not residue — the same case as bucket C of the companion audit. `DA_WORLD_EVENTS_Rules` only catches
`WorldEventInstance` actors and `LI_WE_` paths, which these are not.

Do not auto-clear. Two coherent outcomes for the World Events owner to pick:

- **Keep as authored** and accept the warnings as known-noise (they describe correct content).
- **Author a tag-based rule family** keyed on a World Event actor tag — the only criterion that can
  express "this specific prop belongs to this specific event", which no path or name pattern can.

### Bucket F — Cross-region leaks and one-offs (21 rows)

Actors physically in Overland whose DataLayer belongs to a region the pass *discards* (their outliner
path did not contain the discarded substring, so they were not filtered out):

| Family | DataLayers | Rows | Owner |
| --- | --- | ---: | --- |
| Quidditch | `DL_QUIDDITCHPITCH`, `DL_HW_QP_TowerEntrance12_{INT,EXT}` | 5 | Quidditch |
| Sanctuary Pensieve | `DL_SANCTUARY_Pensieve_{MHP,MRR,MRE,COG_Conv}_01` | 4 | Narrative / Sanctuary |
| Mission (leak) | `DL_M_NEX_01_*`, `DL_M_MFF_01_*`, `DL_M_DEV_NurtureBeast` | 5 | Missions |
| London (leak) | `DL_LON_LabMain{Fight,PreFight}` | 4 | London |
| Expansion Tent | `DL_ExpansionTent_*` | 2 | Gameplay |
| Dungeon (leak) | `DL_DUN_Merlin_Ball_02` | 1 | Dungeons |

Each is a handful of actors; triage by region owner. The leaks also hint that the discard filter
keys on the **outliner path**, not the DataLayer, so content moved between regions keeps a stale
layer the filter cannot catch.

---

## 5. Verification plan

1. Land Bucket A, order it before the generic ConversationHub rule, re-run *validate Overland Only*,
   and check the 105 rows move to **Applied** with a populated rule — not merely vanish.
2. Land Bucket B after the cross-world `POI_` check; expect 11 → 0.
3. With narrative sign-off, clear Bucket C via a `DL_SANCTUARY_ConversationHub_*`-scoped commandlet;
   confirm the Level Instances **keep** their layer (Bucket A) and only the child meshes lose it.
4. Produce the `WPRulesReviewer` export, split Bucket D by container coverage, clear the Sanctuary-
   excluded 255 immediately and the rest per coverage.
5. Refer Buckets E and F to their owners; do not clear without a decision.
6. Re-run and confirm no **new** `Missing DataLayer` / `Failed to assign DataLayer` rows appear — the
   two families must move independently or neither result can be attributed.

---

## 6. Why this run differs from 2026-09-27

| | 2026-09-27 | 2026-10-04 (this) |
| --- | --- | --- |
| Scope | `-ContainOutlinerPathSubstrings="Hogsmeade"` | `-DiscardOutlinerPathSubstrings="mission,dungeon,hogwarts,hogsmeade"` |
| Rows | 2 606 | 1 054 |
| Dominant family | `DL_OVERLAND` street residue (Hogsmeade) | `DL_OVERLAND` + Sanctuary ConversationHub |
| `Matching DataLayer rules` field | absent | **present** (per-actor candidate rules) |
| Discriminator | container **coverage** | rule **reproducibility** (the new field) |

The two runs are **complementary, not a re-measurement**: one keeps only Hogsmeade, the other throws
Hogsmeade away. Together they cover the level; neither supersedes the other. The `DL_OVERLAND` story
is the one thread common to both, which is why bucket D here defers to the companion audit's coverage
method rather than re-deriving it.

---

## 7. Appendix — reproducing the figures

Every number comes from the raw build log. A warning of this family is any line matching
`assigned to runtime DataLayer`.

```powershell
$log = 'Sundance.log'
$pattern = "Actor '([^']+)' is assigned to runtime DataLayer '([^']*)' but no DataLayer rule " +
           "targets it.*DataLayer asset: '([^']+)'\. Matching DataLayer rules: \[([^\]]*)\]"

$rows = foreach ($l in [System.IO.File]::ReadLines($log)) {
    if ($l.Contains('assigned to runtime DataLayer') -and $l -match $pattern) {
        [pscustomobject]@{ Actor = $Matches[1]; DataLayer = $Matches[2]; Candidate = $Matches[4] }
    }
}

$rows.Count                                              # 1 054
($rows.Actor | Select-Object -Unique).Count              # 977
($rows.DataLayer | Select-Object -Unique).Count          # 136
$rows | Group-Object Candidate | Sort-Object Count -Descending   # the §3.3 table
```

[`data/runtime-datalayer-without-rule-inventory.csv`](data/runtime-datalayer-without-rule-inventory.csv)
holds the full inventory — one row per warning, columns `Family`, `DataLayer`, `ActorKind`,
`CandidateRule`, `Container`, `ActorPath`, `DataLayerAsset`. `Family` and `ActorKind` are the §3.2 and
§3.4 classifications, so the file is directly usable as the per-bucket work list.
