Parent: [Audits](README.md)

# Overland exterior data layer overlap — `DL_OVERLAND` on `_EXT` content

Actors in `LV_Overland` that carry the runtime data layer **`DL_OVERLAND`** on top of an
exterior area layer (**`DL_HW_EXT`** for Hogwarts, **`DL_HM_EXT`** for Hogsmeade). The extra
layer is redundant at runtime and splits streaming cells in two, which costs performance.

- **Date**: 2026-09-17
- **Level**: `LV_Overland`
- **Scope**: `LI_Hogwarts` and `LI_Hogsmeade_River`, both recursive
- **Verdict**: **1480 actors** to fix, spread over **3 level assets**, causing **23 split
  streaming cells**
- **Actor lists**: [Hogwarts CSV](https://github.com/ArnaudStorq/sundance-maintenance-validation/raw/main/Audits/OverlandExteriorDataLayerOverlap-Hogwarts-2026-09-17.csv) and
  [Hogsmeade River CSV](https://github.com/ArnaudStorq/sundance-maintenance-validation/raw/main/Audits/OverlandExteriorDataLayerOverlap-HogsmeadeRiver-2026-09-17.csv)

## Contents

- [The problem](#the-problem)
  - [Runtime data layers are additive](#runtime-data-layers-are-additive)
  - [The exterior layers are shut down together](#the-exterior-layers-are-shut-down-together)
  - [The cost: one streaming cell per data layer set](#the-cost-one-streaming-cell-per-data-layer-set)
  - [What the rule system says](#what-the-rule-system-says)
- [How this audit was run](#how-this-audit-was-run)
  - [Counting actors, not placements](#counting-actors-not-placements)
- [Overview — Hogwarts](#overview--hogwarts)
- [Overview — Hogsmeade River](#overview--hogsmeade-river)
- [Combined impact](#combined-impact)
- [The actor lists](#the-actor-lists)
- [Suggested fix](#suggested-fix)
- [Coverage and caveats](#coverage-and-caveats)
- [Open questions](#open-questions)

---

## The problem

### Runtime data layers are additive

A runtime data layer can reach an actor two ways: the **World Partition rule system** assigns
it automatically, or a **person assigns it by hand** in the editor. Nothing ever reconciles the
two. Assignment is purely **additive**, so a hand-placed layer stays on the actor forever, even
once a rule assigns the layer that actor should really be on.

An actor also inherits every runtime data layer carried by the **Level Instances above it**, so
a single hand-placed layer on a container silently propagates to all of its children.

The pattern this audit looks for is the result of both: content that the rules correctly put on
`DL_HW_EXT` or `DL_HM_EXT`, and that *also* still carries a hand-placed `DL_OVERLAND`.

### The exterior layers are shut down together

There are only three exterior runtime data layers in `LV_Overland`:

| Data layer | Parent | Covers |
| --- | --- | --- |
| `DL_OVERLAND` | *(root)* | The open world |
| `DL_HW_EXT` | `DL_HOGWARTS` | Hogwarts exteriors |
| `DL_HM_EXT` | `DL_HOGSMEADE` | Hogsmeade exteriors |

When the player enters an interior from which the outside cannot be seen, the game **offloads
the exterior as a whole** — `DL_OVERLAND`, `DL_HW_EXT` and `DL_HM_EXT` are all deactivated
together. A castle wall therefore gains nothing from being on `DL_OVERLAND` as well as
`DL_HW_EXT`: the layer that already covers it is unloaded at exactly the same moment. **One of
the three is always sufficient.**

### The cost: one streaming cell per data layer set

Streaming generation groups actors into cells **by their data layer set**. Two actors sitting
side by side, in the same runtime grid, in the same cell footprint, still land in **two
different cells** if their data layer sets differ.

So geometry that should have been bundled into a single cell gets split:

```
cell A : { DL_OVERLAND, DL_HW_EXT }   <- the actors carrying the redundant layer
cell B : { DL_HW_EXT }                <- the actors that are correct
```

Both cells load and unload at the same time, since the layers are shut down together. The split
buys nothing and costs an extra cell, extra HLOD actors, and extra streaming work. This is the
concrete reason the redundant layer has to go — it is a performance issue, not a tidiness one.

### What the rule system says

The rule system already knows these actors are wrong. `DA_OVERLAND_Rules` carries
`OutlinerPathsToExclude` entries for both areas:

> `[28] /Game/Levels/Overland/DataLayers/DA_OVERLAND_Rules: excluded by OutlinerPathsToExclude entry 'LI_Hogwarts'.`

> `[28] /Game/Levels/Overland/DataLayers/DA_OVERLAND_Rules: excluded by OutlinerPathsToExclude entry 'LI_Hogsmeade'.`

No rule assigns `DL_OVERLAND` anywhere in either subtree, and `ExplainActorAssignment` reports
every affected actor as `bMismatch: true`, several of them with an explicit
`Non-compliant DataLayers: DL_OVERLAND` note. Every occurrence found by this audit is therefore
a **manual** assignment.

> **Warning:** the absence of a warning proves nothing. The rule pass only processes what it
> was told to process, and an actor caught by an exclusion emits no warning at all. This audit
> reads actor descriptors directly rather than trusting the warning stream.

## How this audit was run

Through the Unreal editor MCP toolsets, against the open `LV_Overland`:

| Step | Tool |
| --- | --- |
| Enumerate actors without loading them | `WorldPartitionToolset.GetActorDescInfo` (reads on-disk descriptors) |
| Resolve the data layers of each area | `WorldPartitionToolset.ListDataLayers` |
| Walk the Level Instance tree | `GetActorDescInfo` with `nativeClassName = LevelInstance` |
| Resolve Outliner paths | `WorldPartitionRuleAuditToolset.FindActorsByOutlinerPath` |
| Confirm an assignment is manual | `WorldPartitionRuleAuditToolset.ExplainActorAssignment` |

A descriptor lists only the layers assigned **on that actor**, so inherited layers were resolved
by walking each actor's Level Instance chain. Nothing was modified; four actors were loaded and
unloaded again so the rule audit could see them.

### Counting actors, not placements

`GetActorDescInfo` returns one row **per placement**. When a level asset is instanced several
times, its actors come back once per instance even though there is a single actor descriptor
behind them — same GUID, same package, same data layers.

This matters in the river:
`/Game/Environment/River/LevelActors/RiverBanks_Large_Stones/LA_RiverBank_SmallSharpRocks_A01`
is instanced **12 times**, and the two offending actors inside it therefore appear as 24 rows.
Every number in this document counts **unique actors** (deduplicated by GUID), because that is
what has to be edited. The distinction is worth keeping in mind two ways:

- **Fixing is cheaper than it looks** — editing those 2 actors once repairs all 12 placements.
- **The runtime cost is not** — streaming still sees 24 instances, so the cell split is paid
  per placement.

The CSVs keep **one row per placement**, so they are the longer of the two counts.

## Overview — Hogwarts

All offending actors trace back to **one** Level Instance.

```
LV_Overland
  └─ LI_Hogwarts                      DL_HOGWARTS
       └─ LI_EntranceHall_EXT         DL_HW_EXT      <- correct, assigned by DA_HW_EXT_Rules
            └─ 775 StaticMeshActor    DL_OVERLAND    <- added by hand
```

| | |
| --- | --- |
| Actors to fix | **775** (`StaticMeshActor`) |
| Actors affected in total | 783 |
| Container | `LI_Hogwarts > LI_EntranceHall_EXT` |
| Level asset | `/Game/Levels/Overland/Hogwarts/EntranceHall/LI_EntranceHall_EXT` |
| Split HLOD cells | 8 |

> **[Download the Hogwarts CSV](https://github.com/ArnaudStorq/sundance-maintenance-validation/raw/main/Audits/OverlandExteriorDataLayerOverlap-Hogwarts-2026-09-17.csv)** — `OverlandExteriorDataLayerOverlap-Hogwarts-2026-09-17.csv`, next to this
> document ([view it on GitHub](OverlandExteriorDataLayerOverlap-Hogwarts-2026-09-17.csv)).
> 775 rows for 775 unique actors, one row per placement.

Own data layers: `DL_OVERLAND` + `DL_RENDER` on 773 actors, plus `DL_LIGHTING` on 2
(`SM_WallMount_B` and `SM_WallMount_B2`). Nothing here is instanced more
than once, so placements and actors are the same 775.

The Level Instance holds 1467 descriptors; the other 692 are clean. This is the case of
`DL_OVERLAND` placed **directly on static meshes** rather than on a Level Instance. They sit in
four Outliner folders under the container:

| Folder | Actors |
| --- | --- |
| *(container root)* | 270 |
| `RENDER/` | 225 |
| `RENDER/Porch/` | 197 |
| `RENDER/Tower/` | 81 |
| `Lighting/` | 2 |

The 8 generated `WorldPartitionHLOD` actors are the visible symptom — cells whose data layer set
is exactly `{DL_OVERLAND, DL_HW_EXT}`:

| HLOD layer | Cells |
| --- | --- |
| `LV_HW_HLODLayer_Near` | 5 |
| `LV_HW_HLODLayer_Mid` | 2 |
| `LV_HW_HLODLayer_Far` | 1 |

The rest of the Hogwarts subtree is clean: of 3706 Level Instances under `LI_Hogwarts`, the 41
carrying `DL_HW_EXT` were swept individually and only `LI_EntranceHall_EXT` has offending
children. None carries `DL_HM_EXT`. Four carry `DL_OVERLAND`
(`LI_GryffindorMaleDormsUpper_INT`, `LI_GryffindorMaleDormsLower_INT`,
`LI_QuidditchPitch_SplineTech`, `LI_HW_Book_Stack_Small_C`) but none of them has an exterior
ancestor or descendant, so they are out of scope here.

## Overview — Hogsmeade River

Same root cause, different shape: the manual layer sits on **nested Level Instances**, so their
children inherit it.

```
LV_Overland
  └─ LI_Hogsmeade_River                  DL_HM_EXT + DL_HOGSMEADE   <- correct, rule-assigned
       ├─ 391 nested LevelInstance       DL_HOGSMEADE + DL_OVERLAND <- added by hand
       │    └─ inherited by their children
       └─ 314 leaf actors                DL_OVERLAND + DL_RENDER    <- added by hand
```

| | |
| --- | --- |
| Actors to fix | **705** |
| Actors affected in total | 800 (3352 placements) |
| Container | `LI_Hogsmeade_River` (top-level, `bMismatch: false` — it is correct) |
| Split HLOD cells | 15, across **two** runtime grids |

> **[Download the Hogsmeade River CSV](https://github.com/ArnaudStorq/sundance-maintenance-validation/raw/main/Audits/OverlandExteriorDataLayerOverlap-HogsmeadeRiver-2026-09-17.csv)** — `OverlandExteriorDataLayerOverlap-HogsmeadeRiver-2026-09-17.csv`, next to this
> document ([view it on GitHub](OverlandExteriorDataLayerOverlap-HogsmeadeRiver-2026-09-17.csv)).
> 727 rows for 705 unique actors, one row per placement.

Breakdown of the 705:

| Class | Count | Own data layers |
| --- | --- | --- |
| `LevelInstance` (nested) | 391 | `DL_HOGSMEADE`, `DL_OVERLAND` |
| `PlacedFoliageSkinnedNaniteAssembly` | 288 | `DL_OVERLAND`, `DL_RENDER` |
| `StaticMeshActor` | 26 | `DL_OVERLAND`, `DL_RENDER` |

Level assets to check out:

| Level asset | Actors |
| --- | --- |
| `/Game/Environment/River/LI_Hogsmeade_River` | 703 |
| `.../RiverBanks_Large_Stones/LA_RiverBank_SmallSharpRocks_A01` | 2 (instanced 12×) |

Split cells, spanning both the Hogsmeade grid and the main grid:

| Grid / HLOD layer | Cells |
| --- | --- |
| `LV_HM_HLODLayer_Near` (`HogsmeadeGrid`) | 8 |
| `LV_Overland_HLODLayer_Near` (`MainGrid`) | 3 |
| `LV_Overland_HLODLayer_Far` | 2 |
| `LV_HM_HLODLayer_Far` | 1 |

For scale: the same footprint holds 31 HLOD actors on `DL_OVERLAND` alone, so roughly a third of
the river's Overland HLOD cells are split by this.

## Combined impact

| | Hogwarts | Hogsmeade River | Total |
| --- | --- | --- | --- |
| Actors to fix | 775 | 705 | **1480** |
| Actors affected in total | 783 | 800 | 1583 |
| Level assets to check out | 1 | 2 | **3** |
| Split HLOD cells | 8 | 15 | **23** |
| Runtime grids touched | 1 | 2 | 3 |
| Manual layer sits on | leaf static meshes | 391 nested Level Instances + 314 leaves | |

The river is the more intricate of the two despite having fewer actors to touch, because the
manual layer sits on containers whose children all inherit it, and because part of its content
is a shared asset instanced twelve times.

## The actor lists

One CSV per area, both next to this document. They are the work order — the document itself
carries no actor list, because 1480 rows read far better in a spreadsheet than in a markdown
table.

| Area | File | Rows | Actors |
| --- | --- | --- | --- |
| Hogwarts | [`OverlandExteriorDataLayerOverlap-Hogwarts-2026-09-17.csv`](OverlandExteriorDataLayerOverlap-Hogwarts-2026-09-17.csv) ([download](https://github.com/ArnaudStorq/sundance-maintenance-validation/raw/main/Audits/OverlandExteriorDataLayerOverlap-Hogwarts-2026-09-17.csv)) | 775 | 775 |
| Hogsmeade River | [`OverlandExteriorDataLayerOverlap-HogsmeadeRiver-2026-09-17.csv`](OverlandExteriorDataLayerOverlap-HogsmeadeRiver-2026-09-17.csv) ([download](https://github.com/ArnaudStorq/sundance-maintenance-validation/raw/main/Audits/OverlandExteriorDataLayerOverlap-HogsmeadeRiver-2026-09-17.csv)) | 727 | 705 |

Both share the same columns:

| Column | Meaning |
| --- | --- |
| `ActorLabel` | Label shown in the Outliner |
| `Class` | Native class of the actor descriptor |
| `OutlinerPath` | Full path of this placement, from the level root |
| `Guid` | Actor Guid — the stable identity, shared by every placement |
| `PlacementCount` | How many rows share this Guid; `1` for everything but the shared river asset |
| `OwnDataLayers` | Layers assigned **on** the actor, the ones to edit |
| `InheritedDataLayers` | Layers coming down from the containing Level Instances |
| `LevelInstanceChain` | Level Instance ancestry, outermost first |
| `OwningLevelAsset` | Level asset holding the actor — what to check out |
| `ReferencedLevelAsset` | For a `LevelInstance`, the asset it points at |
| `CenterX/Y/Z` | Centre of the descriptor bounds, to locate the actor in the editor |

`OwnDataLayers` is the column that matters for the fix: `InheritedDataLayers` cannot be edited
on the actor, it has to be changed on the container that provides it.

## Suggested fix

1. **Remove `DL_OVERLAND`** from the 1480 actors in the two CSVs. They live in three level
   assets, so this is three checkouts rather than 1480.
2. On the 391 nested Level Instances of the river, consider also **adding `DL_HM_EXT`** so they
   match the `expectedValue` the rules report. At runtime this changes nothing — the container
   already provides the layer — it only makes the rule audit report them as compliant.
3. **Rebuild HLODs** for the affected cells. The 23 split HLOD actors are generated output and
   disappear on their own once the source actors are fixed.

## Coverage and caveats

- `GetActorDescInfo` is bounds-based, and the Hogwarts `LocationVolume` does **not** contain
  every Level Instance of its own subtree. Each of the 41 exterior Level Instances was therefore
  queried with **its own descriptor bounds** rather than relying on a single region query.
- `LI_DefensiveWall_01_EXT` and `LI_DefensiveWall_02_EXT` have world-sized descriptor bounds
  (roughly −459 000 to +491 000 units), so a bounds query on them would dump the whole Overland.
  Their children were read from the castle-region query instead: 544 and 50 descendants, none
  carrying `DL_OVERLAND`.
- Outliner paths were resolved by matching each descriptor's Level Instance chain against the
  path segments, because labels repeat across the river's nested Level Instances — several
  `SM_OL_BeachErosion_A13` exist, one per `RiverBank_*` container. All 1480 actors resolved to
  exactly one path, except the 2 in the twelve-times-instanced asset.
- Only `LI_Hogwarts` and `LI_Hogsmeade_River` were audited. The **rest of Hogsmeade** — the
  village itself, under `LI_Hogsmeade` — has not been checked and may hold more of the same.

## Open questions

- Are `DL_OVERLAND`, `DL_HW_EXT` and `DL_HM_EXT` meant to be **strictly mutually exclusive**?
  Hogwarts and Hogsmeade obviously are, but nothing in the rule configuration enforces the
  exclusion against `DL_OVERLAND` — it is only kept out by `OutlinerPathsToExclude` entries.
- Should the four `DL_OVERLAND` Level Instances under `LI_Hogwarts` (three of them `_INT`
  interiors) be on `DL_OVERLAND` at all?
- A pair that **matches** the rules produces no warning, so this class of problem is invisible
  to the nightly pass. A periodic **validation-only run** — a dry run of the rules, or a
  separate commandlet that applies the map checks and rule warnings without assigning anything
  — would catch it.
