Parent: [Reference Docs](README.md)

# World Partition Rules — Consistency Audit (`LV_Overland`)

This report documents an audit of the WorldPartitionRule system as registered **right now** in
`UWorldPartitionRuleSettings` (`Config/DefaultEditor.ini`). The goal was to answer one question:

> Are there inconsistencies in the rules — circular loops, contradictory exclusions, or
> mishandled use cases?

**Bottom line: the rule set is healthy.** The engine's own configuration validator reports
**no errors, no warnings, and no exclusion cycles**. The level-wide streaming validation reports
**zero** rule-caused findings. Everything below is either "by design" or a low-risk item worth
knowing about.

Source: read live from the editor via Unreal MCP (`WorldPartitionRuleAuditToolset`).

> Companion to the [decision flow charts](WorldPartitionRulesFlowCharts.md) (the flat `if … then …`
> catalog), the [rule how-to](WorldPartitionRules.md), and the
> [data-asset analysis](WorldPartitionRulesAnalysis.md).

---

## 1. Method

The audit combined the engine's built-in validators with a manual cross-reference analysis.

| Step | Tool | What it checks |
|------|------|----------------|
| 1 | `GetRuleSystemOverview` | The full registered array (all three rule types), plus whether auto-apply is on. Confirms every entry resolves and is enabled. |
| 2 | `AuditRuleSetup` | The **configuration itself**, no actors: unresolved entries, rules that can never match, conditions that match everything, invalid targets, **mutually excluding rules (`ExclusionCycle`)**, and rules that shadow each other (`RuleOverlap`). |
| 3 | `RunStreamingValidation` | The programmatic equivalent of Map Check's World Partition section. Reads actor descriptors for the **whole** level (regardless of what is loaded) and reports rule-caused streaming errors. |
| 4 | Manual review | Cross-reference graph of every `matched_by(...)` exclusion, forward references, and naming. |

### System snapshot (step 1)

- Level: `LV_Overland`, `bAutoApplyRulesOnActorSave = true`, enabled for this level.
- **57** DataLayer rules, **5** RuntimeGrid rules, **14** HLOD Layer rules.
- Every registered rule: `bResolves = true`, `bIsEnabled = true`.
- Ignore / force lists: `ActorTypesIgnoredByDataLayerRules` 6, `ActorTypesIgnoredByRuntimeGridRules`
  6, `ActorTypesIgnoredByHLODLayerRules` 4, `ActorTypesToForceExcludeFromHLOD` 7,
  `ActorTypesToClearRuntimeGrid` 1, `OutlinerPathsToForceExcludeFromHLOD` 38.
- `RuntimeGridRulesForStreamingGeneration` is **empty** — deliberate (see §4.5).

---

## 2. Results overview

| Validator | Errors | Warnings | Info |
|-----------|:------:|:--------:|:----:|
| `AuditRuleSetup` | **0** | **0** | 8 |
| `RunStreamingValidation` | **0** | **0** | 0 |

No `ExclusionCycle`, no `UnresolvedRule`, no `EmptyAndCondition` (a condition that matches every
actor), no `InvalidGrid` / invalid target. In other words: **no circular loops and no broken
rules.** The eight `Info` findings are detailed below.

---

## 3. Findings from `AuditRuleSetup` (all `Info`)

`Info` severity means "a deliberate choice worth stating, not a problem".

### 3.1 `RuleOverlap` — DataLayer: `DA_MISSIONS_CHILD` vs `DA_MISSIONS`

Both rules have the same matching conditions (`LevelInstance` AND `path ~ 'Missions'`). Because
**DataLayers are additive**, a matching actor ends up in **both** layers:

- `DA_MISSIONS_Rules` → fixed `DL_MISSIONS`
- `DA_MISSIONS_CHILD_Rules` → name pattern `LI_ → DL_M_<name>`

**Assessment: by design.** The parent gets the shared `DL_MISSIONS` layer and, additionally, its
own per-mission child layer. No action needed.

### 3.2 `RuleOverlap` — HLOD: `NoneExclude` vs `NoneInclude` (Hogwarts and Hogsmeade)

Two occurrences, same shape:

- `DA_HW_HLODLayer_NoneExclude_Rules` (idx 8) shares conditions with
  `DA_HW_HLODLayer_NoneInclude_Rules` (idx 7).
- `DA_HM_HLODLayer_NoneExclude_Rules` (idx 11) shares conditions with
  `DA_HM_HLODLayer_NoneInclude_Rules` (idx 10).

HLOD is **single-valued (last match wins)**, so on its own the later `NoneExclude` rule would win
and push *every* matching actor **out** of HLOD, making the earlier `NoneInclude` rule dead. It
does **not**, because `NoneExclude` carries an exclusion for the `NoneInclude` set (and for the
`Near` set). So the disambiguation works — but it is entirely load-bearing.

**Assessment: works today, but fragile.** This is the one spot to watch. If someone removes the
`HW_NoneInclude` / `HM_NoneInclude` exclusion from the `NoneExclude` rule, or reorders the array,
all those actors silently flip to `Excluded` from HLOD. See §5.

### 3.3 `NoTargetLayer` — HLOD (5 rules)

`DA_Overland_HLODLayer_NoneInclude_Rules`, `DA_Overland_HLODLayer_Foliage_Near_Rules`,
`DA_HW_HLODLayer_NoneInclude_Rules`, `DA_HM_HLODLayer_NoneInclude_Rules`,
`DA_HM_HLODLayer_Foliage_Near_Rules`.

These have `IncludeInHLOD = true` but no `TargetHLODLayer`. A matching actor keeps taking part in
HLOD generation but has its layer **cleared**, falling back to the **world default** HLOD layer.

**Assessment: by design.** This is exactly the "Include / None" outcome described in the flow
charts. The validator surfaces it because internally it reads as "matched but target asset is
missing"; the intent here is deliberate.

---

## 4. Manual cross-reference analysis

Beyond the validator, every rule that references another rule via a `matched_by(...)` exclusion was
mapped to confirm the dependency graph is acyclic.

### 4.1 DataLayer exclusion graph

```text
DA_SKY(13)    --excludes--> DA_TECH(14)
DA_TECH(14)   --excludes--> DA_LIGHTHING(8), DA_PROCEDURAL(10), DA_RENDER(11), DA_AUDIO(3)
DA_RENDER(11) --excludes--> DA_CLIFF(5), DA_PROCEDURAL(10), DA_ROAD(12), DA_WATER(16)
```

Leaf rules (`CLIFF`, `PROCEDURAL`, `ROAD`, `WATER`, `LIGHTHING`, `AUDIO`) hold **no** rule-to-rule
exclusions, so there is **no back edge**. The graph is a DAG → **no cycle**.

### 4.2 RuntimeGrid exclusion graph

```text
DA_HogsmeadeGrid(0)      --excludes--> matched_by(DA_AUDIO)                       [cross-type: DataLayer rule]
DA_HogwartsGrid(1)       --excludes--> matched_by(DA_AUDIO), DA_HogwartsInteriorGrid(2)
DA_NoneGrid(3)           --excludes--> matched_by(rule 0, 1, 2, 4)
DA_SmallGrid(4)          --excludes--> matched_by(DA_AUDIO, DA_AUTOMATION, DA_DEGUG, DA_WORLD_EVENTS, DA_MISSIONS)
```

Again acyclic. Two things are worth stating explicitly:

- **Cross-type references.** RuntimeGrid rules exclude actors matched by *DataLayer* rules
  (`DA_AUDIO`, `DA_MISSIONS`, …). This is legitimate — `matched_by` evaluates the other rule's
  **conditions**, not its assignment — but it means the grid outcome silently depends on DataLayer
  conditions. A change to `DA_AUDIO`'s conditions can move actors between grids.
- **Forward reference.** `DA_NoneGrid` (idx 3) excludes `matched_by(DA_SmallGrid)` (idx **4**),
  which sits *after* it in the array. It resolves correctly because `matched_by` is condition-based,
  not order-based — but reading the array top-to-bottom, this is a non-obvious dependency.

### 4.3 "Match nothing" / "match everything"

`AuditRuleSetup` did not flag any `EmptyAndCondition` (an `AND` condition with no criteria set,
which would match every actor). All 76 registered rules have at least one effective criterion.

### 4.4 Unhandled use cases

- **Actors matching no rule.** For single-valued types (RuntimeGrid / HLOD) an unmatched actor
  keeps its existing value; for DataLayers it gets no layer. This is the intended fallback, not a
  gap — but note there is no "catch-all" DataLayer, so an actor that matches none of the 57 rules
  carries **no** DataLayer. That is expected for helper/editor-only actors covered by the ignore
  lists.
- **Naming typos (cosmetic, not functional).** Three asset names carry spelling mistakes that do
  not affect behaviour but can mislead a human:
  - `DA_LIGHTHING_Rules` → intended "LIGHTING" (targets `DL_LIGHTING`).
  - `DA_DEGUG_Rules` → intended "DEBUG"; it targets `DL_DEBUG`, while `DA_DEBUG_RUNTIME_Rules`
    targets `DL_DEBUG_RUNTIME`. Two distinct debug layers — easy to confuse.
  - `DA_SANTUARY*` → intended "SANCTUARY" (the target layers are correctly named `DL_SANCTUARY*`).

### 4.5 `StreamingGenerationRules` empty

`RuntimeGridRulesForStreamingGeneration` is empty, so `AvaStreamingGenerationMutator` assigns no
grids and RuntimeGrid comes purely from what is baked into actors on save. This is **deliberate**:
CL 1988317 moved `DA_SmallGrid_Rules` out of this array and into `RuntimeGridRulesForActorSave`. An
empty array here is not a misconfiguration.

---

## 5. Risk summary and recommendations

| Item | Severity | Recommendation |
|------|----------|----------------|
| HLOD `NoneInclude` / `NoneExclude` overlap (§3.2) | Low–Medium | Keep the `*_NoneInclude` exclusion on each `*_NoneExclude` rule. Treat the idx 7/8 and idx 10/11 ordering as load-bearing; re-run `AuditRuleSetup` after any HLOD reorder. |
| Cross-type & forward references (§4.2) | Low | Document them (done here + flow charts). When editing `DA_AUDIO`, `DA_MISSIONS`, or `DA_SmallGrid`, re-preview grid assignments. |
| Naming typos (§4.4) | Cosmetic | Optional rename for clarity; behaviour is unaffected. Rename touches the ini registration, so batch it with a settings edit. |
| `DA_MISSIONS` / `DA_MISSIONS_CHILD` double layer (§3.1) | None | Confirm the double membership is intended (parent + child). No change needed. |

**No circular loops. No broken or unreachable rules. No rule-caused streaming errors.**

---

## 6. How to reproduce this audit

Run these read-only tools (they do not write anything):

- `WorldPartitionRuleAuditToolset.AuditRuleSetup` — validates the configuration itself; this is the
  finder for cycles, overlaps, unreachable rules and invalid targets.
- `WorldPartitionRuleAuditToolset.RunStreamingValidation` — the Map Check equivalent, level-wide.
- `WorldPartitionRuleAuditToolset.GetRuleSystemOverview` — the ordered registered array.
- `WorldPartitionRuleAuditToolset.ExplainActorAssignment` — for drilling into a single actor: which
  rules matched, which won, and why each other rule was skipped.

## See also

- [World Partition rule decision flow charts](WorldPartitionRulesFlowCharts.md) — the exhaustive
  `if … then …` catalog of every rule.
- [World Partition rules](WorldPartitionRules.md) — practitioner how-to and subsystem internals.
- [World Partition rule data-asset analysis](WorldPartitionRulesAnalysis.md) — deep per-asset
  breakdown.
