Parent: [Audits](README.md)

# `DL_OVERLAND` removal — `LI_Hogsmeade_River` — 2026-09-28

Data: [`ManualOverlandDataLayerRemoval-HogsmeadeRiver-2026-09-28.csv`](ManualOverlandDataLayerRemoval-HogsmeadeRiver-2026-09-28.csv) — 417 rows, one per actor.

The second fix pass on the findings of
[Hand-placed `DL_OVERLAND` under Hogwarts and Hogsmeade](ManualOverlandDataLayer-Hogwarts-Hogsmeade-2026-09-23.md),
after [`LI_EntranceHall_EXT`](ManualOverlandDataLayerRemoval-EntranceHall-2026-09-28.md). It covers
the Hogsmeade river cluster: the 439 findings under `LI_Hogsmeade_River`, which resolve to 417
distinct actors.

Pending in Perforce changelist **2097633**, not submitted. All 417 actors were written.

## Contents

- [Confirming the layer is hand-placed](#confirming-the-layer-is-hand-placed)
- [439 findings, 417 actors](#439-findings-417-actors)
- [What was changed](#what-was-changed)
- [How it was done](#how-it-was-done)
- [What was deliberately left alone](#what-was-deliberately-left-alone)
- [Follow-up](#follow-up)

---

## Confirming the layer is hand-placed

The 2026-09-23 audit could not pin and probe this cluster, so it classified the 439 actors from
the rule definitions rather than from a live verdict. That classification was re-checked here by
reading the rule assets directly, and it holds.

**No rule can assign `DL_OVERLAND` under this path.** Of the 57 registered DataLayer rules,
`DA_OVERLAND_Rules` (index 28) is the only one whose target is `DL_OVERLAND`. The six
name-pattern rules cannot produce it either: their replacements yield `DL_DUN*`, `DL_HM_*`,
`DL_HW_*`, `DL_M_*`, `DL_SANCTUARY_VIVARIUM_*` and `DL_WE_*`. And `DA_OVERLAND_Rules` carries
`LI_Hogsmeade` in its `ExclusionCriteria.OutlinerPathsToExclude`, which is matched as a
case-insensitive substring of the full Outliner path and short-circuits the rule before any
condition is evaluated. All 439 Outliner paths contain `LI_Hogsmeade_River`, so all 439 are
excluded. `PreviewRuleMatches` on the rule returns 33 matches in the open level, none of them
under `LI_Hogsmeade`.

**The rules actively want something else here, so these are findings and not fallback.**
`DA_HM_EXT_Rules` (index 21) has a condition that reads `ActorTypes = [LevelInstance]` AND
`OutlinerPathContains = ["LI_Hogsmeade_River"]`, excluding only paths containing `River_COL`.
The 391 Level Instances of this cluster are squarely inside it and the rules expect `DL_HM_EXT`
on them, not `DL_OVERLAND`. This is the opposite of the foliage case, where no rule matches at
all and the layer is the legitimate fallback.

**Perforce agrees.** The nightly job `@AUTOMATION $OVERLAND Applied WorldPartition rules to
LV_Overland (Filter used: 'LI_Hogsmeade')` has run against these files more than fifteen times
since June, and `DL_OVERLAND` survived every pass. The rules neither write it nor remove it.

The parent `LI_Hogsmeade_River` itself carries `DL_HM_EXT` and `DL_HOGSMEADE`, and **not**
`DL_OVERLAND`, so the layer was not inherited from above either. Removing it genuinely takes
these actors out of the Overland streaming set.

## 439 findings, 417 actors

The audit reports 439 rows but there are 417 distinct actors behind them. Two of them live in a
shared Level Actor asset, `LA_RiverBank_SmallSharpRocks_A01`, which is instanced twelve times
under `LI_Hogsmeade_River`, so the sweep saw each of the two once per placement:

| Actor | Rows in the audit | Actor packages |
|---|---:|---:|
| `RiverBank_LargeStones_A92` | 12 | 1 |
| `SM_RockPile_LI_A01` | 12 | 1 |

Editing those two packages changes all twelve placements at once. That is in scope: the asset
registry reports eighteen referencers and every one of them is under `LI_Hogsmeade_River`, so
nothing outside the river is affected.

The audit also shows 48 `StaticMeshActor` rows, which collapse to 26 actors for the same reason.

## What was changed

`DL_OVERLAND` was removed from the `DataLayerAssets` of all 417 actors. Nothing else on those
actors was touched, and no other data layer was removed.

| Before | After | Actors |
|---|---|---:|
| `DL_OVERLAND`, `DL_HOGSMEADE` | `DL_HOGSMEADE` | 391 |
| `DL_OVERLAND`, `DL_RENDER` | `DL_RENDER` | 26 |

The audit's *Runtime layers on the actor* column lists only `DL_OVERLAND` for all of them, which
no longer matches the descriptors. The 391 Level Instances have carried `DL_HOGSMEADE` since
CL 2086801 on 2026-09-24, a rule pass that ran after the audit was taken. `DL_RENDER` is an
Editor data layer and drives editor loading rather than streaming; it was preserved.

One external actor package per actor was dirtied and saved — 417 files, all in changelist
**2097633**. No level, no `WorldDataLayers` actor and no rule asset was modified.

The changelist description:

```
@MINOR $TOOLS
Remove hand-placed DL_OVERLAND from LI_Hogsmeade_River actors
&TESTED Editor
@REVIEW Philippe St-Jean (WBGMontreal)
[jira:SUNDANCE-77683]
```

## How it was done

1. The 439 target rows were taken from the 2026-09-23 audit CSV, filtered on
   `ContainingLevelInstance = LI_Hogsmeade_River` and `Verdict = RuleMismatch`. The 288
   `OutsideRuleProcessing` foliage rows of the same cluster were left out.
2. Every rule asset involved was read directly rather than trusted from the audit — see
   [Confirming the layer is hand-placed](#confirming-the-layer-is-hand-placed).
3. Each row was matched to a live descriptor on its soft object path, which yielded the external
   actor package and its file on disk. The 439 rows resolved to 417 descriptors, and the current
   data layer set was read from each one rather than reused from the audit.
4. Perforce state was checked before any edit: `p4 fstat` over the 417 files reported **no file
   open or locked by anyone**.
5. A changelist was created and all 417 files checked out into it.
6. In the editor, each external actor package was loaded directly, `DL_OVERLAND` was dropped from
   `DataLayerAssets`, and the package was saved, in batches of 60. No save failed.
7. `p4 diff -sr` reported no opened file identical to the depot, so all 417 are genuinely
   modified.
8. A random sample of saved packages was reloaded from disk and re-read to confirm the layer set
   on disk, not merely in memory.

The actors live in `/Game/Environment/River/LI_Hogsmeade_River`, a partitioned level referenced
as a Level Instance from `LV_Overland`. The editor cannot stream them in from the outer world —
`LoadActors`, `PinActors` and `LoadActorsInBounds` all resolve nothing for these GUIDs — which is
why they are edited through their external actor packages and why the rule audit tools, which
only see loaded actors, could not give a per-actor live verdict.

## What was deliberately left alone

- **The 288 foliage actors of the same cluster** (`PlacedFoliageSkinnedNaniteAssembly`). No rule
  processes them, so `DL_OVERLAND` is their fallback and stripping it would send them straight
  back to it. They need a rule, not an edit.
- **The rest of Hogsmeade** — `LI_HM_Streets_EXT` (1114), `LI_Camp_Crate_Food_A` (149),
  `LI_HM_StreetDressing_EXT` (13), `LI_HM_StreetDressing_WPV_Trashed_EXT` (14), `LI_Tomes_POP` (1).
- **Hogwarts interiors** (177 actors), still waiting on the visible-from-outside check.
- **The five `LI_EntranceHall_EXT` actors** left outstanding by the
  [first pass](ManualOverlandDataLayerRemoval-EntranceHall-2026-09-28.md#actors-that-were-skipped).

## Follow-up

- Review and submit changelist 2097633.
- Reopen the river area and confirm nothing disappeared from the Overland view.
- Re-run the streaming generation snapshot and check that the
  `DL_HM_EXT + DL_OVERLAND` cell for the river is gone.
- The 391 Level Instances now have `DL_HOGSMEADE` but not `DL_HM_EXT`, which is what
  `DA_HM_EXT_Rules` expects on them. The next rule pass will add it; worth confirming it does.
