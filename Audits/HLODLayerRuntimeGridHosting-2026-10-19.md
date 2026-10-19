Parent: [Audits](README.md)

# HLOD layer ↔ RuntimeGrid hosting warnings — threshold-hypothesis audit (`LV_Overland`)

A batch of `WorldPartitionRuleBuilder` / HLOD-generation warnings of the form
*"HLOD layer `X` is (still) not hosted by RuntimeGrid `Y` … Their HLOD actors can end
up always loaded; fix the RuntimeGrid or HLODLayer rules"* was brought in with a
standing hypothesis: that this is a **size-threshold mismatch** — a runtime-grid rule
that sends actors under *200 units* to a small grid while the HLOD rule uses *250
units*, so the actors in the 200–250 band land in the wrong place.

This audit tests that hypothesis against the **live** rule system and partition setup
read from the editor (Unreal MCP, `LV_Overland` open). **The hypothesis does not
hold.** These warnings are a **categorical HLOD-layer ↔ RuntimeGrid tier-hosting**
problem, not a numeric size-threshold problem, and **changing a size threshold would
not clear a single one of them.** The reasoning and the per-warning evidence are below.

## Contents

- [The question asked](#the-question-asked)
- [Method](#method)
- [What the warning actually means](#what-the-warning-actually-means)
- [Live grid → hosted-HLOD-layer map](#live-grid--hosted-hlod-layer-map)
- [The log, line by line, against the live setup](#the-log-line-by-line-against-the-live-setup)
- [Verdict 1 — is this the "rules don't match" case?](#verdict-1--is-this-the-rules-dont-match-case)
- [Verdict 2 — would a different threshold fix the warnings?](#verdict-2--would-a-different-threshold-fix-the-warnings)
- [What actually fixes them](#what-actually-fixes-them)
- [How to reproduce this audit](#how-to-reproduce-this-audit)
- [See also](#see-also)

---

## The question asked

Two questions, quoted from the request:

1. Are we really in the case of **rules that do not match** (see the "root cause"
   below)?
2. Would **changing the rules with a different threshold** correct the warnings?

The "root cause" under test:

> The runtime grid says: actors `< 200 units` → small grid.
> The HLOD layer says: actors `< 250 units`.
> Every actor between 200 and 250 units lands in the wrong target (expected small
> grid, ends up in main grid / HLOD). The real fix = align the thresholds of the two
> rules, not move actors by hand.

---

## Method

Read-only, live, against the open `LV_Overland` editor world via Unreal MCP. Nothing
was written.

| Step | Tool | What it answers |
|------|------|-----------------|
| 1 | `HLODPartitionConfigToolset.GetRuntimePartitionSetup` | Which HLOD layer sits on which grid/tier — the authoritative hosting allowlist. |
| 2 | `HLODPartitionConfigToolset.WhereIsHLODLayer` | For a single layer, which grid/tier hosts it (or "unassigned"). |
| 3 | `HLODPartitionConfigToolset.AuditHLODPartitionSetup` | Drift / unassigned-layer / empty-tier problems in the partition setup. |
| 4 | `WorldPartitionRuleAuditToolset.AuditRuleSetup` | The rule configuration itself: unreachable rules, invalid targets, **any threshold/condition misconfiguration**. |
| 5 | `WorldPartitionRuleAuditToolset.RunStreamingValidation` | The Map Check equivalent, level-wide, with the responsible rule per finding. |

The static rule definitions were cross-checked against
[Runtime Grid rules](../ReferenceDocs/WorldPartitionRulesAnalysis/RuntimeGridRules.md)
and [HLOD Layer rules](../ReferenceDocs/WorldPartitionRulesAnalysis/HLODLayerRules.md).

---

## What the warning actually means

`LV_Overland` runs on a `WorldPartitionRuntimeHashSet` with
**`bRequiresExplicitHLODLayerAssignment = true`**. That flag is the whole story: an
actor's HLOD layer must be **explicitly assigned to an HLOD tier on the very grid the
actor streams on**. If the actor's RuntimeGrid carries no tier for its HLOD layer, the
generated HLOD has nowhere to live — it falls back to an always-loaded proxy — and the
builder emits exactly this warning.

Reading the two message shapes:

- *"… is **not** hosted by RuntimeGrid `Y`; **moved** N actor(s) to `Z`"* — the actor
  sat on grid `Y`, which does not host the layer; the builder's mutator **auto-moved**
  it to `Z`, a grid that does. Mitigated at generation time.
- *"… is **still not** hosted by RuntimeGrid `Y` for N actor(s); **hosted by:** `W`"* —
  the actor sits on grid `Y`, still not a host; `W` is where the layer is actually
  hosted (`none` = no grid hosts it at all). **Unresolved** — these are the real
  always-loaded risks.

Nowhere in this mechanism is there an actor-size comparison. The decision is "is this
`(RuntimeGrid, HLODLayer)` pair in the tier allowlist?" — a name match, not a measurement.

---

## Live grid → hosted-HLOD-layer map

Read live via `GetRuntimePartitionSetup`. `LV_Overland_HLODLayer_Dummy` is the shared
no-op layer present on every grid; it is omitted below for clarity.

| RuntimeGrid | Tier | HLOD layers hosted |
|---|---|---|
| **MainGrid** | Overland_Near | `LV_Overland_HLODLayer_Near`, `LV_Overland_HLODLayer_Landscape_Near` |
| | Overland_Far | `LV_Overland_HLODLayer_Far`, `LV_Overland_HLODLayer_Water_Near`, `LV_Overland_HLODLayer_Road_Near` |
| | *(persistent)* | `LV_Overland_HLODLayer_Landscape_Far2`, `LV_Overland_HLODLayer_Water_Far` |
| **SmallGrid** | HLOD_SmallGrid_Dummy | *(only Dummy)* |
| **HogsmeadeGrid** | HM_Near | `LV_HM_HLODLayer_Near` |
| | HM_Far | `LV_HM_HLODLayer_Far`, `LV_HM_HLODLayer_Foliage_Near` |
| **HogwartsGrid** | HW_Near | `LV_HW_HLODLayer_Near` |
| | HW_Mid | `LV_HW_HLODLayer_Mid` |
| | *(persistent)* | `LV_HW_HLODLayer_Far` |
| **FarFoliageGrid** | FarFoliage_Mid | `LV_FarFoliage_HLODLayer_Foliage_Mid` |
| | FarFoliage_Far | `LV_FarFoliage_HLODLayer_Foliage_Far` |
| **FarWorldBitmap** | *(persistent)* | *(none)* |

The key fact: **each near/region HLOD layer is hosted by exactly one grid.**
`LV_HM_HLODLayer_Near` lives only on `HogsmeadeGrid`; `LV_HW_HLODLayer_Near` only on
`HogwartsGrid`; `LV_Overland_HLODLayer_Near` and `…_Landscape_Near` only on `MainGrid`;
`LV_FarFoliage_HLODLayer_Foliage_Mid` only on `FarFoliageGrid`. `SmallGrid` hosts
**no** near layer at all — only the Dummy.

---

## The log, line by line, against the live setup

Every "moved to `Z`" destination in the log equals the single grid that hosts that
layer in the table above. That exact agreement is what proves the warnings are a
hosting problem and nothing else.

### Auto-mitigated (builder moved the actor to the hosting grid)

| HLOD layer | On grid `Y` | Moved to `Z` | `Z` hosts the layer? | Actors |
|---|---|---|:--:|--:|
| `LV_FarFoliage_HLODLayer_Foliage_Mid` | None | FarFoliageGrid | ✅ | 9 |
| `LV_HM_HLODLayer_Near` | MainGrid | HogsmeadeGrid | ✅ | 1160 |
| `LV_HW_HLODLayer_Near` | MainGrid | HogwartsGrid | ✅ | 77 |
| `LV_HW_HLODLayer_Near` | None | HogwartsGrid | ✅ | 3341 |
| `LV_Overland_HLODLayer_Landscape_Near` | SmallGrid | MainGrid | ✅ | 141 |
| `LV_Overland_HLODLayer_Near` | FarFoliageGrid | MainGrid | ✅ | 183 |
| `LV_Overland_HLODLayer_Near` | HogsmeadeGrid | MainGrid | ✅ | 463 |
| `LV_Overland_HLODLayer_Near` | HogwartsGrid | MainGrid | ✅ | 4 |
| `LV_Overland_HLODLayer_Near` | SmallGrid | MainGrid | ✅ | 1390 |

### Unresolved (`hosted by:` …, HLOD can end up always loaded)

| HLOD layer | On grid `Y` | hosted by | Actors | Why |
|---|---|---|--:|---|
| `CM_ArchitectChamber_HLODLayer_Instanced` | MainGrid | none | 1 | Custom layer **assigned to no tier anywhere** (see below). |
| `CM_ArchitectChamber_HLODLayer_Instanced` | None | none | 53 | Same unassigned layer; actors also on grid `None`. |
| `LV_FarFoliage_HLODLayer_Foliage_Mid` | FarFoliageGrid | none | 63 | `SK_Spruce…` inside `LI_LabForestBiome`; the Level-Instance **effective** grid resolves away from `FarFoliageGrid` at generation, so no tier hosts them. |
| `LV_FarFoliage_HLODLayer_Foliage_Mid` | MainGrid | FarFoliageGrid | 1 | `SK_Holly_B` on `MainGrid`; layer lives on `FarFoliageGrid`. Should be re-gridded, not resized. |
| `LV_Overland_HLODLayer_Near` | HogwartsGrid | MainGrid | 12 | Quidditch Pitch blockout kept on `HogwartsGrid`; near layer lives on `MainGrid`. |
| `LV_Overland_HLODLayer_Near` | None | none | 32 + 9 | Level-assembly actors on grid `None`; `None` hosts no Overland near layer. |

`WhereIsHLODLayer("CM_ArchitectChamber_HLODLayer_Instanced")` returns, verbatim:

> `…/CM_ArchitectChamber_HLODLayer_Instanced` is not assigned to any HLOD tier in this
> level. This level requires explicit assignment, so streaming generation will error
> on actors using it.

That is the entire cause of the 54 `ArchitectChamber` warnings — a custom HLOD layer
shipped on actors but never added to a tier. No size, no threshold.

---

## Verdict 1 — is this the "rules don't match" case?

**Partly — but not in the way the hypothesis describes.** There *is* a mismatch, and it
*is* between the RuntimeGrid side and the HLOD side. But the mismatch is **categorical
tier hosting**, not a numeric threshold:

- The actor's **RuntimeGrid** (set by the on-save grid rules, or left `None`, or
  carried by a Level Instance) does not carry a **tier** for the actor's **HLOD layer**
  (set by the HLOD rules / the asset). The two sides name **different grids**.
- `AuditRuleSetup` returns **0 Error, 0 Warning** — only 8 deliberate `Info` findings
  (the known `NoneInclude`/`NoneExclude` overlaps and unset-target rules). There is **no
  rule carrying a 200- or 250-unit threshold**, and no `InvalidGrid` / unreachable rule.
- `RunStreamingValidation` returns **0 findings** on the open level: the currently
  loaded `LV_Overland` descriptors produce no rule-caused streaming error. The warnings
  in the log come from the **builder/HLOD pass over the whole content** (Level Instances
  and sub-levels such as `SANCTUARY/ArchitectChamber`, `Dungeons/Merlin`,
  `London/BeastLab`), where the effective grid of LI children and unassigned custom
  layers surface.

The only actor-**size** gate that exists anywhere in the rule set is the **1 m
(100 uu) `MaxBoundsDimension`** condition on `DA_SmallGrid_Rules` — and it governs
*SmallGrid eligibility*, not HLOD-layer hosting. There is no "200 vs 250" pair.

## Verdict 2 — would a different threshold fix the warnings?

**No.** Changing a size threshold cannot clear any of these warnings, because:

- No warning is produced by a size comparison. Each is produced by the
  `(RuntimeGrid, HLODLayer)` pair being absent from the tier allowlist.
- The 54 `ArchitectChamber` warnings are an **unassigned HLOD layer** — unaffected by
  any rule threshold.
- The `SmallGrid → MainGrid` moves (the lines most likely to be mistaken for a
  size-band bug) happen because **`SmallGrid` hosts no near HLOD layer at all**, so
  *any* actor on `SmallGrid` that carries a near layer is relocated regardless of its
  size. Lowering or raising a threshold changes *which* actors are on `SmallGrid`; it
  never gives `SmallGrid` a near tier, so the warning persists for whoever remains.

---

## What actually fixes them

Three independent levers, matching the warning's own advice ("fix the RuntimeGrid or
HLODLayer rules") plus a partition-setup lever:

1. **Assign the layer to a tier** (partition setup / RuntimeHashSet). The fix for
   `CM_ArchitectChamber_HLODLayer_Instanced`: add it to a tier on the grid its actors
   stream on, or stop shipping that custom layer. Tool: `MoveHLODLayerToTier`.
2. **Re-grid the actor** (RuntimeGrid rules). Make the actor land on the grid that
   already hosts its HLOD layer — which is exactly what the builder's mutator does for
   the auto-moved rows; persist it on save so the proxy is not regenerated always-loaded
   (e.g. `SK_Holly_B` → `FarFoliageGrid`).
3. **Re-layer the actor** (HLOD rules). Give the actor an HLOD layer that its current
   grid hosts — e.g. an actor that must stay on `HogwartsGrid` should carry
   `LV_HW_HLODLayer_Near`, not `LV_Overland_HLODLayer_Near`.

For the Level-Instance `None`/effective-grid residuals (the 63 `LI_LabForestBiome`
foliage, the 32 + 9 level-assembly actors), the mechanism and remedy are the ones
documented in
[SUNDANCE-83330 — HLOD layer with no grid tier](../SUNDANCE-83330_HLODLayerNoGridTier_2026-10-14_transcript.md)
and
[RuntimeGrid reference conflict resolution](../ReferenceDocs/RuntimeGridReferenceConflictResolution.md):
resolve the actor's effective grid first, then host the layer on it.

---

## How to reproduce this audit

With `LV_Overland` open in the editor, run these read-only MCP tools:

- `HLODPartitionConfigToolset.GetRuntimePartitionSetup` — the grid → tier → HLOD-layer
  table (the hosting allowlist).
- `HLODPartitionConfigToolset.WhereIsHLODLayer` — for any layer named in a warning, to
  see its host grid or confirm it is unassigned.
- `WorldPartitionRuleAuditToolset.AuditRuleSetup` — confirms there is no threshold or
  invalid-target misconfiguration in the rules.
- `WorldPartitionRuleAuditToolset.RunStreamingValidation` — the level-wide Map Check
  equivalent; an empty result means the open level has no rule-caused streaming error.

## See also

- [SUNDANCE-83330 — HLOD layer with no grid tier](../SUNDANCE-83330_HLODLayerNoGridTier_2026-10-14_transcript.md)
- [Runtime Grid rules](../ReferenceDocs/WorldPartitionRulesAnalysis/RuntimeGridRules.md)
- [HLOD Layer rules](../ReferenceDocs/WorldPartitionRulesAnalysis/HLODLayerRules.md)
- [World Partition rules — consistency audit](../ReferenceDocs/WorldPartitionRulesConsistencyAudit.md)
- [RuntimeGrid reference conflict resolution](../ReferenceDocs/RuntimeGridReferenceConflictResolution.md)
