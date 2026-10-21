Parent: [Audits](README.md)

# `DL_OVERLAND` removal — Hogsmeade & Hogwarts — 2026-10-21

The runtime data layer `DL_OVERLAND` was carried, on their own descriptors, by exterior
actors nested inside the recursive Level Instance trees of **Hogwarts** and **Hogsmeade**
in `LV_Overland`. Stacked on top of the district's own exterior layer (`DL_HW_EXT` /
`DL_HM_EXT`), it splits streaming cells for no gameplay reason. This pass strips the own
`DL_OVERLAND` assignment from those actors, leaving every inherited assignment untouched.

The work went out as three pending Perforce changelists — one per sweep — and every
modified actor was resaved inside its owning Level Instance edit and re-scanned to confirm
the layer does not come back.

## Contents

- [Overview](#overview)
- [How it was done](#how-it-was-done)
- [Hogsmeade](#hogsmeade)
  - [River (CL 2144767)](#river-cl-2144767)
  - [Village (CL 2144946)](#village-cl-2144946)
- [Hogwarts (CL 2144671)](#hogwarts-cl-2144671)
- [What was left alone](#what-was-left-alone)

---

## Overview

| Zone | Changelist | Actors removed | Packages | Skipped (locked) | Data |
|---|---|---:|---:|---:|---|
| Hogsmeade — River | 2144767 | 288 | 288 | 0 | [CSV](OverlandDataLayerRemoval-HogsmeadeRiver-2026-10-21.csv) |
| Hogsmeade — Village | 2144946 | 904 | 606 | 5 | [CSV](OverlandDataLayerRemoval-HogsmeadeVillage-2026-10-21.csv) |
| Hogwarts | 2144671 | 159 | 129 | 0 | [CSV](OverlandDataLayerRemoval-Hogwarts-2026-10-21.csv) |
| **Total** | | **1351** | **1023** | **5** | |

All three changelists are **pending** — they are checked in through Submit Sidekick, not by
this pass.

## How it was done

The sweep ran live against the open editor through Unreal MCP, not from a commandlet:

1. **Load the zone.** The top Level Instance (`LI_Hogwarts`, `LI_Hogsmeade_River`,
   `LI_Hogsmeade`) was loaded; for the Hogsmeade zones the gating editor data layers
   (`DL_HOGSMEADE`, `DL_HM_EXT`) were enabled in the editor first so the actors resolve.
2. **Scan read-only.** The tree was walked with `level_instance_get_actors`, and an actor
   was a target only when its own `data_layer_assets` contained `DL_OVERLAND` — inherited-only
   actors were skipped.
3. **Remove per owning container.** Each Level Instance directly holding a target was put
   into edit mode, its target actors had `DL_OVERLAND` removed via
   `DataLayerEditorSubsystem`, and the edit was committed (saved). The source external-actor
   packages were checked out silently from the editor so the pass stayed autonomous.
4. **Resave and verify.** Every modified container was re-entered, its changed actors
   re-dirtied and resaved, then the whole tree was re-scanned: `DL_OVERLAND` did **not**
   reappear on any processed actor, and no Level Instance was left in edit mode.

The Village and Hogwarts trees share sub-level packages across placements, so a single
package edit covers every placement of that container — which is why the package counts are
lower than the actor counts.

## Hogsmeade

### River (CL 2144767)

288 actors stripped of their own `DL_OVERLAND`, across 288 dedicated external-actor
packages — mostly `PlacedFoliageSkinnedNaniteAssembly` foliage along the river. Full list:
[`OverlandDataLayerRemoval-HogsmeadeRiver-2026-10-21.csv`](OverlandDataLayerRemoval-HogsmeadeRiver-2026-10-21.csv).

### Village (CL 2144946)

904 actors stripped across 606 shared external-actor packages, inside the recursive
`LI_Hogsmeade` tree (`LI_HM_StreetDressing_EXT`, `LI_HM_Rocks_EXT`, `LI_HM_Streets_EXT`,
the camp crate/cart containers and the grassy stairs). Five actors were locked by another
user and skipped — see [What was left alone](#what-was-left-alone). Full list, removed and
skipped: [`OverlandDataLayerRemoval-HogsmeadeVillage-2026-10-21.csv`](OverlandDataLayerRemoval-HogsmeadeVillage-2026-10-21.csv).

## Hogwarts (CL 2144671)

159 actors stripped across 129 external-actor packages inside the `LI_Hogwarts` tree. The
32 window placements share 2 packages (`LI_Window_A_StainedGlass` / `...EXT`), so editing
those two covers all of them. Full list:
[`OverlandDataLayerRemoval-Hogwarts-2026-10-21.csv`](OverlandDataLayerRemoval-Hogwarts-2026-10-21.csv).

## What was left alone

- **Inherited `DL_OVERLAND`.** Only the actor's own assignment was removed; a `DL_OVERLAND`
  inherited from a parent Level Instance was never touched.
- **5 actors locked by another user (`dhawthorn`).** All in `LI_Camp_Cart_B` under the
  village. They carry an exclusive lock, so they were skipped rather than forced, and are
  listed with status `Skipped` in the village CSV. They should be retaken once the lock is
  released.

| Outliner path | Class |
|---|---|
| LI_Hogsmeade > LI_Brood_POP > LI_Camp_Cart_B > SM_Bottle_Liquor_B | StaticMeshActor |
| LI_Hogsmeade > LI_Brood_POP > LI_Camp_Cart_B > SM_Bottle_Liquor_C | StaticMeshActor |
| LI_Hogsmeade > LI_Brood_POP > LI_Camp_Cart_B > SM_Bottle_Liquor_D | StaticMeshActor |
| LI_Hogsmeade > LI_Brood_POP > LI_Camp_Cart_B > SM_Bottle_Wine_B | StaticMeshActor |
| LI_Hogsmeade > LI_Brood_POP > LI_Camp_Cart_B > SM_Tool_Clippers_B | StaticMeshActor |
