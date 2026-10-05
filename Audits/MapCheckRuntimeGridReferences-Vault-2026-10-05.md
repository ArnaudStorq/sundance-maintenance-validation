Parent: [Audits](README.md)

# MapCheck runtime-grid references — Vault Level Instances, 2026-10-05

The 2026-10-05 MapCheck on `LV_Overland` reported
`Map check complete: 3 Error(s), 13 Warning(s)`. All three errors were
[D5 — *actor references an actor in a different runtime grid*](../ReferenceDocs/FixingMapCheckIssues.md#d5--actor-references-an-actor-in-a-different-runtime-grid),
and all three sat inside two Vault blockout Level Instances. They were fixed the same day as
changelist **2111842**; this document records the diagnosis, the trap met on the way, and the
rule-level follow-up that would stop the family from coming back.

## Contents

- [The problem](#the-problem)
- [The three errors](#the-three-errors)
- [Why they appeared](#why-they-appeared)
- [The trap: a reference cluster, not three couples](#the-trap-a-reference-cluster-not-three-couples)
- [The fix applied — CL 2111842](#the-fix-applied--cl-2111842)
- [How the audit was run](#how-the-audit-was-run)
- [Checked and found clean](#checked-and-found-clean)
- [Follow-up: exclude the Vault blockout content from `DA_SmallGrid_Rules`](#follow-up-exclude-the-vault-blockout-content-from-da_smallgrid_rules)
- [See also](#see-also)

---

## The problem

Streaming generation requires the two actors of a runtime reference to stream on the same
`RuntimeGrid`, otherwise one could load without the other and leave a dangling reference. When the
grids differ the generator does not keep the authored values: outside the error-reporting pass it
calls `SetForcedNoRuntimeGrid()` on **both** actors, so the pair ends up on the default grid
whatever the data says. An error of this family therefore means two things at once — MapCheck and
the submit-time `WorldPartitionChangelistValidator` will complain, and the `SmallGrid` someone
authored is already being ignored.

Since [CL 2102948](../ReferenceDocs/EffectiveRuntimeGridReferenceValidation.md) the check compares
the **effective** grids, so `None` vs the default grid is no longer reported. Anything still
reported is a real divergence.

## The three errors

| # | Referencer (grid) | Referee (grid) | Level Instance |
|---|---|---|---|
| 1 | `BP_Constellation` (`None`) | `BP_AstronomyPuzzle6` (`SmallGrid`) | `LI_VaultAstronomy_MooncalfRefuge_Blockout` |
| 2 | `BP_AstronomyPuzzle6` (`SmallGrid`) | `BP_Ceiling` (`None`) | `LI_VaultAstronomy_MooncalfRefuge_Blockout` |
| 3 | `BP_Lever_PotionVault` (`None`) | `SM_Vault_Grate_BLK` (`SmallGrid`) | `LI_Vault_Potion_01` |

Both Level Instance actors are themselves on `RuntimeGrid = None` in `LV_Overland`, which is why
the inner actors keep their own grid instead of inheriting the container's — and therefore why the
divergence survives the effective-grid resolution.

## Why they appeared

`DA_SmallGrid_Rules` assigns `SmallGrid` to **any actor whose largest bounds dimension is under
100 uu (1 m)**, plus every `ForageableBlueprint`. Its path exclusions are `Dungeon`, `Mission`,
`LV_Overland/Hogsmeade/LI_Hogsmeade`, `LV_Overland/Hogwarts/LI_Hogwarts`,
`LV_Overland/QuidditchPitch`, `LI_Sanctuary` and `LOC_OL_` — none of which covers a Vault blockout
Level Instance under `/Game/Experimental/Levels/Vault/`. Larger actors in the same Level Instance
fall through to `DA_NoneGrid_Rules` and are cleared to `None`.

So the grid boundary inside these Level Instances is drawn **by actor size**, while references
ignore size entirely. Any reference between a sub-metre actor and a larger one becomes an error.

The values were written by two changelists:

| Changelist | Date | Author | What it wrote |
|---|---|---|---|
| 2109903 | 2026-10-02 | `daustin` | Added the Mooncalf refuge blockout; the on-save rules stamped `SmallGrid` on the small puzzle actors as they were created |
| 2110649 | 2026-10-03 | `slc-svc-teamcity` | Nightly `WorldPartitionRuleBuilder` pass (`@AUTOMATION $OVERLAND Applied WorldPartition rules to LV_Overland`), which touched the other actors of both Level Instances |

> `DA_SmallGrid_Rules` is registered in **`RuntimeGridRulesForActorSave`** (index 4), not in the
> streaming-generation array, so it is baked onto disk. See
> [Runtime Grid rules](../ReferenceDocs/WorldPartitionRulesAnalysis/RuntimeGridRules.md).

## The trap: a reference cluster, not three couples

The first fix pass treated the log at face value and aligned each referee onto its referencer's
grid — which for error 1 means putting `BP_AstronomyPuzzle6` on `None`. MapCheck then returned
**8 errors instead of 3**: `BP_AstronomyPuzzle6` is also referenced both ways by
`BP_AstronomyPuzzle`, `BP_AstronomyPuzzle2`, `BP_AstronomyPuzzle3` and `BP_AstronomyPuzzle5`, all
on `SmallGrid`. Moving one actor out of the group simply moved the boundary.

The lesson is that this error is reported **per reference edge** but has to be fixed **per
reference cluster**: list every actor connected by references, pick one grid for the whole set, and
only then write. MapCheck only shows the edges that currently diverge, so the cluster has to be
reconstructed from the actor data, not from the log.

Here the cluster was `BP_AstronomyPuzzle`, `…2`, `…3`, `…5`, `…6`, `BP_Constellation` and
`BP_Ceiling`. `None` was chosen for all of them because it is what the generator forces for the
pair anyway, because the five puzzle actors carry no HLOD layer (so nothing argues for the
`SmallGrid` partition), and because the sibling Level Instance
`LI_VaultAstronomy_01_Blockout` holds the same content with all 184 actors on `None`.

## The fix applied — CL 2111842

Six actors set to `RuntimeGrid = None` and tagged `ExcludeFromRuntimeGridRules` so the nightly rule
builder stops re-assigning `SmallGrid`:

| Level Instance | Actors |
|---|---|
| `LI_VaultAstronomy_MooncalfRefuge_Blockout` | `BP_AstronomyPuzzle`, `BP_AstronomyPuzzle2`, `BP_AstronomyPuzzle3`, `BP_AstronomyPuzzle5`, `BP_AstronomyPuzzle6` |
| `LI_Vault_Potion_01` | `SM_Vault_Grate_BLK` |

The tag is the RuntimeGrid-only one (`ActorTagExcludedFromRuntimeGridRules`), not the blanket
`ExcludeFromRules`, so the DataLayer and HLOD rules keep working on these actors —
see [Exclude From Rules tag](../ReferenceDocs/CustomTools/ExcludeFromRulesTag.md).

Result on `LV_Overland`: `3 Error(s)` → **`0 Error(s)`**. Because the generated streaming already
forced the whole cluster to `None`, the generated cells and HLODs are unchanged and **no HLOD
rebuild is needed**.

## How the audit was run

1. Read the MapCheck errors from `Saved/Logs/Sundance.log` (`MapCheck: Error:` lines) rather than
   the Message Log panel, so the full actor paths are readable.
2. Read each actor's authored `RuntimeGrid` from the World Partition descriptors —
   `unreal.WorldPartitionBlueprintLibrary.get_actor_descs()` on the open `LV_Overland`, which
   returns Level Instance children too (666 556 descriptors) and needs nothing loaded.
3. Read `DA_SmallGrid_Rules` and `DA_LOC_VAULT_Rules` live (`matchingConditions`,
   `exclusionCriteria`) to attribute the `SmallGrid` values, and
   `Config/DefaultEditor.ini` for the rule order, `AutoApplyRulesOnActorSave` and the exclusion
   tag names.
4. `p4 filelog` on the six external actor packages to date the values and identify the two
   changelists that wrote them.
5. Edit: open each Level Instance level on its own (neither is in `MapsWithAutoApplyRules`, so
   saving does not re-run the rules), pin the actors by descriptor GUID, set the grid, add the
   tag, check out and save.
6. Re-open `LV_Overland`, run `MAP CHECK`, and diff the warning list against the baseline run.

> **The documented scan/fix commands were not available.**
> [`Editor.ScanRuntimeGridReferenceErrors` and `Editor.FixRuntimeGridReferenceErrors`](../ReferenceDocs/CustomTools/RuntimeGridReferenceTools.md)
> are absent from the current editor build — the console accepts the line and does nothing, the
> source file is not in the workspace, and the strings are not in
> `Binaries/Win64/UnrealEditor-WorldBuildingEditor.dll`. Worth re-checking before planning any
> work around them. Note also that the fixer aligns referee → referencer per log line, which is
> exactly the per-edge reasoning that produced the 8-error state above.

## Checked and found clean

- **`LI_Vault_Potion_01` keeps 10 other actors on `SmallGrid`** (`BP_BRK_Crate_7`, `…13`,
  `SM_Cav_MiningLamp_01`, `SM_GobMine_Barrel_BLK2`, five `SM_HM_PotionBottle1_Empty_BLK*`,
  `SM_Wall_Ruin_C_BLK3`). None of them shares a reference with a `None` actor, so none is reported
  and none was touched.
- **`LI_VaultAstronomy_01_Blockout`**, the sibling Level Instance holding the same puzzle content,
  has all 184 actors on `None` and reports nothing.
- **Warnings**: 13 before, 14 after. The extra one is
  `WaterBodyOcean_UAID_7C10C9223BD82D1702_1717506711 Static mesh actor has NULL StaticMesh property`,
  a generic [G1](../ReferenceDocs/FixingMapCheckIssues.md#g1--static-mesh-actor-has-null-staticmesh-property)
  on an unrelated ocean actor that depends on what is resident when the pass runs. Every other
  warning is identical before and after.
- **`RunStreamingValidation`** (the programmatic MapCheck of the rule system) reports nothing for
  this family: it covers `InvalidRuntimeGrid`, `InvalidHLODLayer`, `UnsupportedHLODLayer`,
  `InvalidReferenceDataLayers` and `RejectedMutator`, but **not** the reference checks. Do not read
  its empty result as "no reference conflicts".

## Follow-up: exclude the Vault blockout content from `DA_SmallGrid_Rules`

The six tags fix today's errors but not the cause: the next sub-metre actor placed in a Vault
blockout Level Instance next to a larger one it references will reproduce the family. The durable
fix is to treat this content the way dungeons, missions and the Sanctuary are already treated — as
gameplay-scoped content the broad `SmallGrid` sweep should not touch.

**Proposed change** — add the Vault blockout Level Instances to
`DA_SmallGrid_Rules.ExclusionCriteria.OutlinerPathsToExclude`, which today reads:

```
Dungeon, Mission, LV_Overland/Hogsmeade/LI_Hogsmeade, LV_Overland/Hogwarts/LI_Hogwarts,
LV_Overland/QuidditchPitch, LI_Sanctuary, LOC_OL_
```

Open questions to settle before writing it:

- **Which substring.** The Level Instance actors are labelled `LI_Vault…` /
  `LI_VaultAstronomy…` and their content lives under `/Game/Experimental/Levels/Vault/`, but the
  rule matches the **Outliner path**, not the asset path, so it has to be a label/folder
  substring. `LI_Vault` catches `LI_Vault_Potion_01`, `LI_VaultAstronomy_*`,
  `LI_Vault_Entrance_Shimmy01` and the `LI_Vault_BLK` blockout family; it does **not** catch a
  Vault Level Instance named otherwise. Verify with `FindActorsByOutlinerPath` and
  `PreviewRuleMatches` before and after.
- **Why not the DataLayer route.** Excluding `DA_LOC_VAULT_Rules` through
  `DataLayerRulesToExclude` would be more in keeping with how missions and world events are
  carved out, but that rule matches `LOC_OL_Vault`, `_Vault_` and `_Vault-` in the Outliner path,
  and these two Level Instances are not placed under a `LOC_OL_Vault…` locator — which is also
  why the existing `LOC_OL_` path exclusion misses them. Fixing the placement to follow the
  `LOC_OL_` convention would close both holes at once and is worth raising with the Vault owners.
- **Scope of the side effect.** The exclusion also drops `SmallGrid` from the Vault actors that
  carry it legitimately today (10 in `LI_Vault_Potion_01` alone), moving them to the default grid.
  That needs a `WorldPartitionRuleBuilder` pass over the affected levels and a look at the
  streaming cost before it is submitted.
- **Shared file.** `UWorldPartitionRuleSettings` is `config=Editor`, so the edit lands in
  `Config/DefaultEditor.ini`, which several people have pending edits in. Read the returned ini
  diff and never submit the file blind.

Once the rule excludes the content, the six `ExcludeFromRuntimeGridRules` tags from CL 2111842
become redundant and can be removed — the rule then leaves the actors on `None` by itself.

## See also

- [Fixing MapCheck issues — D5](../ReferenceDocs/FixingMapCheckIssues.md#d5--actor-references-an-actor-in-a-different-runtime-grid)
  — the playbook entry for this message
- [Effective RuntimeGrid reference validation](../ReferenceDocs/EffectiveRuntimeGridReferenceValidation.md)
  — CL 2102948, why `None` vs `MainGrid` is no longer reported
- [Runtime Grid rules](../ReferenceDocs/WorldPartitionRulesAnalysis/RuntimeGridRules.md) — the rule
  that writes `SmallGrid`
- [Runtime Grid Reference Tools](../ReferenceDocs/CustomTools/RuntimeGridReferenceTools.md) — the
  scan/fix commands this audit could not use
- [Exclude From Rules tag](../ReferenceDocs/CustomTools/ExcludeFromRulesTag.md) — the per-actor
  freeze used here
