Parent: [Audits](README.md)

# Pass 2 — Interior actors hidden from the exterior

Filters the [Pass 1](DataLayerOverlap-Overland-Pass1-2026-09-22.md) carriers down to the ones that are **geometrically enclosed**: actors tagged for an exterior data layer that no line of sight reaches from outside. Carrying `DL_OVERLAND` together with `DL_HW_EXT` or `DL_HM_EXT` is legitimate for anything genuinely visible from the Overland — towers, roofs, facades. The defect is the opposite case: geometry sealed inside a building that still advertises itself as exterior.

**Result for the Entrance Hall, the one cluster measured with the calibrated metric: 25 sealed actors and 5 actors with empty bounds, out of 775 carriers.**

## Contents

- [Method](#method)
- [Why the metadata was not used](#why-the-metadata-was-not-used)
- [Calibration](#calibration)
- [Results — Entrance Hall](#results--entrance-hall)
- [Results — Hogsmeade (provisional)](#results--hogsmeade-provisional)
- [Worked example](#worked-example--the-walled-up-doorway)
- [Caveats](#caveats)

---

## Method

The test is purely geometric and runs against **real collision geometry**, not against descriptor bounding boxes.

`WorldBookmarkToolset.LoadWorldBookmark` is what unblocks the whole pass. Partitioned Level Instance content cannot be made resident through `LoadActors`, `PinActors` or `LoadActorsInBounds`, and the descriptor `bLoaded` flag reports it as loaded when it is not — an empty world reports 347 resident actors, almost all `LocationVolume`. A bookmark brings an area in with its surroundings: `BMK_HW_EXT_EntranceHall` yields 32 191 resident static meshes, `BMK_HOGSMEADE_EXTERIOR` 81 160.

For each carrier, rays are cast from **15 origins on its bounding box** — the centre, the six face centres and the eight corners, at 99%% of the extent — in **98 directions** spread evenly over the sphere by a Fibonacci lattice, 20 km each, with the actor itself ignored. That is 1 470 rays per actor. The measure kept is **openness**: the percentage of rays that reach open space without hitting anything.

Two earlier, cheaper variants were tried and both proved unreliable. Casting 26 rays from the bounds centre alone reports an actor as sealed whenever that centre happens to sit inside a neighbouring wall. Adding the six face centres, for 182 rays, fixes that but still misses escape routes that only the box corners find: of the 67 actors it called sealed, 38 turned out to have escapes once the corners were sampled. Only the corner-inclusive measure is stable.

## Why the metadata was not used

The obvious shortcut would be to trust the project's own notion of interior — the `_INT` data layers, the `LI_*_INT` naming, or `DA_HogwartsInteriorGrid_Rules`. That shortcut is invalid here, because the actors being looked for are precisely the ones whose metadata is wrong. An actor mis-tagged as exterior will not be matched by an interior rule, so the rules would hide exactly the defects they were asked to find.

`PreviewRuleMatches` is unusable for a second reason as well: it evaluates only loaded actors, and returned `matchCount: 0` on all six data layer and runtime grid rules against an empty world.

## Calibration

Openness is a continuum, so the threshold has to be set against families whose real-world position is not in doubt — roof ridges, finials, crenellations and tower dormers all sit on the outside of the castle and must never be flagged.

| Control family (known exterior) | n | Min openness | Median |
| --- | ---: | ---: | ---: |
| `SM_SlateRoofRidge_Single_A` | 120 | 12.11% | 46.19% |
| `SM_HW_Finial_A` | 7 | 34.29% | 54.69% |
| `SM_HW_EH_Tower_WindowDormer_A` | 6 | 18.98% | 23.33% |
| `SM_HW_EH_Roof_A` | 3 | 4.76% | 12.65% |
| `SM_HW_GH_WindowFrame_Lower_A` | 17 | 0.41% | 9.52% |
| `SM_HW_EH_Column_LG_A` | 14 | 1.43% | 7.62% |
| `SM_HW_CrocketDetail_A` | 12 | 2.11% | 7.31% |
| `SM_HW_EH_Crenels_A_End_A` | 17 | 1.97% | 6.74% |
| `SM_HW_EH_TrimSection_A` | 39 | 1.29% | 6.26% |

The lowest any control reaches is **0.41%**, so the only threshold with no false positive is openness exactly **0**.

| Threshold | Actors flagged | Control false positives |
| --- | ---: | ---: |
| `<= 0.00%` | 25 | 0 |
| `<= 0.25%` | 30 | 0 |
| `<= 0.50%` | 49 | 2 |
| `<= 1.00%` | 68 | 2 |
| `<= 2.00%` | 176 | 6 |

Everything below uses openness = 0.

## Results — Entrance Hall

25 of the 775 carriers are sealed, and a further 5 have **empty bounding boxes** — static mesh actors with no geometry at all, which is a separate defect worth its own fix.

The sealed set is not scattered. Eighteen of the 25 are `SM_HW_EH_DoorFrame_ColumnDecor_B_*` stacked vertically over **two ground positions only**, which points at one walled-up or duplicated doorway rather than eighteen independent mistakes.

| Actor | Centre (x, y, z) |
| --- | --- |
| `SM_HW_EH_ColumnBase_Large_PartA5` | -10967, -28076, 7315 |
| `SM_HW_EH_ColumnBase_Large_PartB7` | -10967, -28076, 7366 |
| `SM_HW_EH_ColumnBase_Large_PartC7` | -10967, -28076, 7406 |
| `SM_HW_EH_DoorFrame_BaseColumn_A_12` | -10161, -29106, 7437 |
| `SM_HW_EH_DoorFrame_ColumnDecor_B_114` | -10186, -29230, 9348 |
| `SM_HW_EH_DoorFrame_ColumnDecor_B_115` | -10165, -29108, 9348 |
| `SM_HW_EH_DoorFrame_ColumnDecor_B_34` | -10186, -29230, 7784 |
| `SM_HW_EH_DoorFrame_ColumnDecor_B_35` | -10165, -29108, 7784 |
| `SM_HW_EH_DoorFrame_ColumnDecor_B_36` | -10165, -29108, 7964 |
| `SM_HW_EH_DoorFrame_ColumnDecor_B_37` | -10186, -29230, 7964 |
| `SM_HW_EH_DoorFrame_ColumnDecor_B_39` | -10165, -29108, 8150 |
| `SM_HW_EH_DoorFrame_ColumnDecor_B_40` | -10186, -29230, 8150 |
| `SM_HW_EH_DoorFrame_ColumnDecor_B_42` | -10165, -29108, 8396 |
| `SM_HW_EH_DoorFrame_ColumnDecor_B_43` | -10186, -29230, 8396 |
| `SM_HW_EH_DoorFrame_ColumnDecor_B_45` | -10165, -29108, 8603 |
| `SM_HW_EH_DoorFrame_ColumnDecor_B_46` | -10186, -29230, 8603 |
| `SM_HW_EH_DoorFrame_ColumnDecor_B_48` | -10165, -29108, 8803 |
| `SM_HW_EH_DoorFrame_ColumnDecor_B_49` | -10186, -29230, 8803 |
| `SM_HW_EH_DoorFrame_ColumnDecor_B_51` | -10165, -29108, 9001 |
| `SM_HW_EH_DoorFrame_ColumnDecor_B_52` | -10186, -29230, 9001 |
| `SM_HW_EH_DoorFrame_ColumnDecor_B_79` | -10186, -29230, 9223 |
| `SM_HW_EH_DoorFrame_ColumnDecor_B_80` | -10165, -29108, 9223 |
| `SM_HW_EH_JambKit_Column_Base_A7` | -8201, -26533, 9843 |
| `SM_HW_EH_JambKit_Column_Base_A8` | -8073, -25847, 9840 |
| `SM_HW_EH_Trim_Small_B47` | -10848, -27459, 7700 |

**Empty bounds (no geometry):**

| Actor | Centre (x, y, z) |
| --- | --- |
| `SM_HW_EH_ColumnBase_Large_PartD` | -10515, -29830, 7300 |
| `SM_HW_EH_ColumnBase_Large_PartD2` | -8446, -29326, 7300 |
| `SM_HW_EH_ColumnBase_Large_PartE` | -9333, -30038, 7300 |
| `SM_HW_EH_ColumnBase_Large_PartF` | -10515, -29830, 7300 |
| `SM_HW_EH_ColumnBase_Large_PartG` | -9333, -30038, 7300 |

Both lists are in [`DataLayerOverlap-Overland-Pass2-Hidden-2026-09-22.csv`](DataLayerOverlap-Overland-Pass2-Hidden-2026-09-22.csv) with GUIDs and soft paths.

## Results — Hogsmeade (provisional)

Hogsmeade was measured with the **182-ray variant only**, before the corner sampling showed that variant to be over-inclusive. These counts are therefore an upper bound and will shrink when re-measured; treat them as a shortlist, not a work order.

| Containing Level Instance | Carriers tested | Flagged (provisional) |
| --- | ---: | ---: |
| `LI_HM_Streets_EXT` | 1280 | 36 |
| `LI_Hogsmeade_River` | 705 | 3 |

The pattern there differs from the castle: paving stones (`SM_CobbleStreet_Block_*`) and fruit props (`SM_HW_Apple_*`) that ended up under building footprints, at 2–3%% of each family.

`LI_Hogsmeade_River` is barely covered — it stretches far beyond the Hogsmeade bookmark, so only 26 of its 705 carriers were resident. Covering it needs the river walked with further bookmarks.

## Worked example — the walled-up doorway

`SM_HW_EH_DoorFrame_ColumnDecor_B_34`, `_35`, `_36`, `_37`, `_39`, `_40`, `_42`, `_43`, `_45`, `_46`, `_48`, `_49`, `_51`, `_52`, `_79`, `_80`, `_114` and `_115` all carry `DL_OVERLAND` + `DL_HW_EXT`. They occupy two ground positions, `(-10165, -29108)` and `(-10186, -29230)`, and climb in z from 7 784 to 9 348 — two column stacks flanking a doorway. Not one of the 1 470 rays cast from each of them reaches open space.

The attic dormers are the clearest single case. `SM_HW_GH_Window_Dormer_SM_A4` sits at z = 10 931 with the roof directly above and the attic ceiling directly below:

```
up     SM_HW_EH_Roof_A            @0
down   SM_HW_EH_Attic_Ceiling_A_1 @0
+x     SM_HW_EH_Attic_Ceiling_A_1 @0
+y     SM_HW_EH_Roof_A            @83
-y     SM_HW_EH_Attic_Ceiling_A_1 @327
```

It measures 3.2%% openness once the box corners are sampled, so it falls outside the zero-openness cut — but the same mesh used correctly on the Great Hall roof at z = 15 847 escapes in every direction. It is a real defect that the strict threshold declines to claim, which is the trade the threshold makes.

## Caveats

- **Only the Entrance Hall is measured with the calibrated metric.** Hogsmeade is provisional and the river is largely untested.
- **The threshold is deliberately strict.** Zero openness is the only cut with no control false positive, and it drops genuine defects that sit at 1–3% — the attic dormers among them. A review pass at `openness <= 1%` would surface 68 actors instead of 25, at the cost of 2 known-exterior false positives.
- **Openness is measured from the bounding box, not the mesh surface.** A box corner can sit in free space outside a thin wall that the mesh itself is buried in, which makes the measure err towards calling things visible.
- **Collision, not render geometry.** A mesh with no collision cannot occlude a neighbour, which again biases towards under-reporting.
- **Being sealed is evidence, not a verdict.** Enclosed geometry that is deliberately streamed with the exterior would land here too. Each row still needs an author's eye.
