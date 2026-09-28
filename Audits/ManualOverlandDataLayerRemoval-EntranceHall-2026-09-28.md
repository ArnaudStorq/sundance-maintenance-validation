Parent: [Audits](README.md)

# `DL_OVERLAND` removal — `LI_EntranceHall_EXT` — 2026-09-28

Data: [`ManualOverlandDataLayerRemoval-EntranceHall-2026-09-28.csv`](ManualOverlandDataLayerRemoval-EntranceHall-2026-09-28.csv) — 775 rows, one per actor.

The first fix pass on the findings of
[Hand-placed `DL_OVERLAND` under Hogwarts and Hogsmeade](ManualOverlandDataLayer-Hogwarts-Hogsmeade-2026-09-23.md).
It covers exactly one cluster: the 775 `StaticMeshActor`s under `LI_EntranceHall_EXT`,
the Hogwarts exterior Level Instance that is the single largest offender in that audit.

Submitted as Perforce changelist **2086955** on 2026-09-24 — 770 of the 775 actors.
Five are still outstanding, see [Actors that were skipped](#actors-that-were-skipped).

## Contents

- [Why this cluster and only this cluster](#why-this-cluster-and-only-this-cluster)
- [What was changed](#what-was-changed)
- [How it was done](#how-it-was-done)
- [Actors that were skipped](#actors-that-were-skipped)
- [What was deliberately left alone](#what-was-deliberately-left-alone)
- [Follow-up](#follow-up)

---

## Why this cluster and only this cluster

`LI_EntranceHall_EXT` is already tagged `DL_HW_EXT`, which every actor inside it inherits.
The extra `DL_OVERLAND` written by hand on each actor descriptor puts them in a
`DL_HW_EXT + DL_OVERLAND` streaming cell instead of the `DL_HW_EXT` one, so the building
ships as two cells for no gain. No rule can reassert the layer here — `DA_OVERLAND_Rules`
excludes `LI_Hogwarts` from its `OutlinerPathsToExclude` — so removing it is stable.

The cluster is exterior-only, contains no Level Instance and no foliage, and every actor is a
plain `StaticMeshActor`. That is the whole reason it was picked first: it is the one group
where the call needs no further judgement.

## What was changed

`DL_OVERLAND` was removed from the `DataLayerAssets` of 770 actors. Nothing else on those
actors was touched, and no other data layer was removed.

| Data layers on the actor | Before | After | Actors |
|---|---|---|---:|
| | `DL_OVERLAND`, `DL_RENDER` | `DL_RENDER` | 770 |

`DL_RENDER` is an Editor data layer and drives editor loading, not streaming. It was present on
every actor in the cluster and was preserved. The audit's *Runtime layers on the actor* column
lists only `DL_OVERLAND` because it reports runtime layers; the descriptors carry both.

One external actor package per actor was dirtied and saved — 770 files, all in changelist
**2086955**. No level, no `WorldDataLayers` actor and no rule asset was modified.

The submitted description:

```
@MINOR $TOOLS
Remove hand-placed DL_OVERLAND from LI_EntranceHall_EXT static meshes
&TESTED Editor
@REVIEW Philippe St-Jean (WBGMontreal)
[jira:SUNDANCE-77683]
```

## How it was done

1. The 775 target rows were taken from the 2026-09-23 audit CSV, filtered on
   `ContainingLevelInstance = LI_EntranceHall_EXT`.
2. Each row was matched to a live descriptor through `GetActorDescInfo`, on the actor's soft
   object path, which yielded the external actor package and its file on disk. All 775 matched.
3. Perforce state was checked before any edit: `p4 fstat` and `p4 opened -a` over the whole
   `__ExternalActors__/.../LI_EntranceHall_EXT/...` path reported **no file open or locked by
   anyone**, and every file at head revision.
4. A changelist was created and all 775 files checked out into it.
5. In the editor, each external actor package was loaded directly, `DL_OVERLAND` was dropped
   from `DataLayerAssets`, and the package was saved, in batches of 100.
6. Files that ended up identical to the depot were reverted out of the changelist, so it held
   only genuinely modified actors — 770 of them.
7. A random sample of saved packages was reloaded from disk and re-read to confirm the layer
   set on disk, not merely in memory.
8. The changelist was submitted, and renumbered to 2086955 on submit.

The actors live inside a partitioned Level Instance, which is why they are edited through their
external actor packages rather than through the `LV_Overland` editor world: `LoadActors` and
`PinActors` resolve nothing for these GUIDs from the outer world.

## Actors that were skipped

Five actors could not be written. The editor process held a file handle that `SavePackage`
could not release, so every save attempt failed with `MoveFile ... Error Code 32` — a sharing
violation, not a source-control lock and not a content problem.

They are **not** in changelist 2086955, and `p4 filelog` confirms none of them has had a new
revision since the automation passes of July and August, so they still carry `DL_OVERLAND`
at head.

| Actor | Data layers | Head revision | External actor package |
|---|---|---|---|
| `SM_HW_EH_DoorFrame_Arch_A_1` | `DL_OVERLAND`, `DL_RENDER` | #13, CL 1981692 | `.../D/DZ/3FM2THXCHD2DBCVKCV4LSR` |
| `SM_HW_EH_DoorFrame_BaseColumn_A_1` | `DL_OVERLAND`, `DL_RENDER` | #14, CL 1981692 | `.../E/5P/9SUPKCZXAN7JNO7XSXL06L` |
| `SM_HW_EH_DoorFrame_BaseColumn_A_10` | `DL_OVERLAND`, `DL_RENDER` | #13, CL 1981692 | `.../C/IH/Z6WQWO394DO9EJFBNJ7BU5` |
| `SM_WallMount_B` | `DL_OVERLAND`, `DL_RENDER`, `DL_LIGHTING` | #7, CL 2010843 | `.../7/SF/CLZY1TTMAHFY8NI1OXQ02S` |
| `SM_WallMount_B2` | `DL_OVERLAND`, `DL_RENDER`, `DL_LIGHTING` | #7, CL 2010843 | `.../8/UZ/J1WEER0WX3AOV0U6Z0HCYX` |

Paths continue from `/Game/__ExternalActors__/Levels/Overland/Hogwarts/EntranceHall/LI_EntranceHall_EXT/`.

These are the only two actors in the cluster that also carry `DL_LIGHTING`, plus three door-frame
meshes. Re-running the same pass after an editor restart clears the handle and finishes them.

## What was deliberately left alone

Everything else in the 2026-09-23 audit. In particular:

- **Hogwarts interiors** (177 actors, including two Level Instances carrying the layer by hand).
  They wait on a check of whether the meshes are visible from the outside — through windows, or
  from the Viaduct Entrance — which would explain why someone set `DL_OVERLAND` on them.
- **Hogsmeade** (1730 actors). The rule is expected to be simple, anything already tagged
  `DL_HM_EXT` can lose the `DL_OVERLAND`, but it has not been run.
- **Foliage** (365 `PlacedFoliageSkinnedNaniteAssembly` actors). No rule processes them, so
  stripping the layer would only send them back to the same fallback. They need a rule.

## Follow-up

- Finish the five skipped actors — restart the editor first, then re-run the same pass.
- Reopen the area and confirm nothing disappeared from the Overland view.
- Re-run the streaming generation snapshot and check that the
  `DL_HW_EXT + DL_OVERLAND` cell for the Entrance Hall is gone. It will not disappear entirely
  until the five remaining actors are done.
