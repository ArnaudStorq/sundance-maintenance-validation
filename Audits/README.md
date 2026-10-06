Parent: [Sundance Maintenance & Validation](../README.md)

# Audits

Point-in-time sweeps of `LV_Overland` content: what was scanned, what was found, and the exact
list of actors to fix.

An audit is dated and **does not age well** — it describes the level as it was on that day. Read
the *problem* sections for lasting knowledge, and treat the actor lists as a work order that is
only valid until someone fixes them.

Some audits read the level directly, others read the log of an automated pass over it. When one
run yields several unrelated findings, they are kept together as an [audit tree](#audit-trees)
rather than scattered across this folder.

## Contents

- [How an audit differs from a reference doc](#how-an-audit-differs-from-a-reference-doc)
- [The audits](#the-audits)
- [Audit trees](#audit-trees)
- [Writing a new audit](#writing-a-new-audit)

## How an audit differs from a reference doc

| | [Reference Docs](../ReferenceDocs/README.md) | Audits |
|---|---|---|
| Describes | How a system works | What the content looks like right now |
| Lifetime | Until the system changes | Until the listed actors are fixed |
| Naming | `<Topic>.md` | `<Topic>-<YYYY-MM-DD>.md` |

## The audits

| Audit | Scope | Found | Data |
|---|---|---|---|
| [Overland exterior data layer overlap](OverlandExteriorDataLayerOverlap-2026-09-17.md) | `LI_Hogwarts` and `LI_Hogsmeade_River`, recursive | 1480 actors carrying `DL_OVERLAND` on top of `DL_HW_EXT` / `DL_HM_EXT`, splitting 23 streaming cells | [Hogwarts](OverlandExteriorDataLayerOverlap-Hogwarts-2026-09-17.csv), [Hogsmeade River](OverlandExteriorDataLayerOverlap-HogsmeadeRiver-2026-09-17.csv) |
| [Pass 1 — `DL_OVERLAND` + exterior layer](DataLayerOverlap-Overland-Pass1-2026-09-22.md) | Whole world, 658 837 actor descriptors | 6741 actors whose effective layer set combines both, of which 2865 carriers in 5 Level Instances | [Carriers](DataLayerOverlap-Overland-Pass1-2026-09-22.csv) |
| [Pass 2 — interior actors hidden from the exterior](DataLayerOverlap-Overland-Pass2-2026-09-22.md) | The Pass 1 carriers, where geometry is resident; calibrated on `LI_EntranceHall_EXT` (775 carriers) | 25 actors fully enclosed by collision geometry yet tagged exterior, plus 5 with empty bounds; Hogsmeade still provisional | [Hidden](DataLayerOverlap-Overland-Pass2-Hidden-2026-09-22.csv) |
| [`DL_OVERLAND` removal candidates](OverlandDataLayerRemoval-2026-09-22.md) | The Pass 2 enclosed actors that assign `DL_OVERLAND` themselves, Hogwarts and Hogsmeade | 69 actors to strip the layer from — 25 confirmed, 5 with no geometry, 39 provisional | [Removal list](OverlandDataLayerRemoval-2026-09-22.csv) |
| [`DL_OVERLAND` removal candidates — visual verification](OverlandDataLayerRemoval-Captures-2026-09-22.md) | The same 69 candidates, with an editor capture per actor | 30 Hogwarts actors shown selected, walled in, next to their Outliner Data Layer row; the 39 Hogsmeade ones await the region reload | [Removal list](OverlandDataLayerRemoval-2026-09-22.csv) |
| [Hand-placed `DL_OVERLAND` under Hogwarts and Hogsmeade](ManualOverlandDataLayer-Hogwarts-Hogsmeade-2026-09-23.md) | Whole world, 667 859 actor descriptors, kept under `LI_Hogwarts` and `LI_Hogsmeade` | 3047 actors carrying a `DL_OVERLAND` that no rule can assign, in 13 Level Instances — 2682 that a rule actively disagrees with, and 365 the rules never process, where the layer is only the level-wide fallback | [Actor list](ManualOverlandDataLayer-Hogwarts-Hogsmeade-2026-09-23.csv) |
| [`DL_OVERLAND` removal — `LI_EntranceHall_EXT`](ManualOverlandDataLayerRemoval-EntranceHall-2026-09-28.md) | The 775 hand-tagged static meshes of the Hogwarts Entrance Hall exterior | 770 actors stripped of `DL_OVERLAND`, submitted as changelist 2086955; 5 still outstanding after a file-handle conflict | [Removed and skipped](ManualOverlandDataLayerRemoval-EntranceHall-2026-09-28.csv) |
| [`DL_OVERLAND` removal — `LI_Hogsmeade_River`](ManualOverlandDataLayerRemoval-HogsmeadeRiver-2026-09-28.md) | The 439 hand-tagged findings of the Hogsmeade river cluster, which resolve to 417 distinct actors | All 417 stripped of `DL_OVERLAND`, submitted as changelist 2097647; the hand-placed verdict re-checked against the rule assets first | [Removed actors](ManualOverlandDataLayerRemoval-HogsmeadeRiver-2026-09-28.csv) |
| [`DL_OVERLAND` removal — `LI_HM_Streets_EXT`](ManualOverlandDataLayerRemoval-HogsmeadeStreets-2026-09-29.md) | The 1114 hand-tagged static meshes of the Hogsmeade streets exterior | 1109 stripped of `DL_OVERLAND`, pending as changelist 2099933; 2 locked by another user, 3 deleted since the audit; the hand-placed verdict checked live and in Perforce history for every actor | [Removed, skipped and missing](ManualOverlandDataLayerRemoval-HogsmeadeStreets-2026-09-29.csv) |
| [MapCheck runtime-grid references — Vault Level Instances](MapCheckRuntimeGridReferences-Vault-2026-10-05.md) | The 3 "different runtime grid" errors of the 2026-10-05 MapCheck on `LV_Overland`, read from the actor descriptors | One reference cluster of 7 actors split between `None` and `SmallGrid` by the 1 m bounds condition of `DA_SmallGrid_Rules`; 6 actors realigned and frozen as changelist 2111842, `3 Error(s)` → `0 Error(s)` | in-document tables (6 actors) |

## Audit trees

Most audits above stand alone: one sweep, one question, one document. Some work splits the other
way — a **single automated run** produces one log, and that log holds several unrelated warning
families, each deserving its own deep dive. Writing those as six sibling files in this folder would
lose the one fact that matters most about them: they share a source, so their counts are slices of
the same total and their root causes cross-reference each other.

Such work goes in a **sub-folder named after the run**, with a `README.md` at its root that carries
the source build, the totals, and the tree of families below it. One folder is one run; one file
inside it is one warning family.

```
Audits/
└── <Pass>-<World>-<YYYY-MM-DD>/     the run
    ├── README.md                    the build, the totals, the tree, the reading order
    ├── <WarningFamily>.md           one deep dive per family
    └── data/                        one inventory CSV per family
```

| Tree | Source run | Families | Rows |
|---|---|---:|---:|
| [Validate World Partition Rules — `LV_Overland`, 2026-09-27](ValidateWorldPartitionRules-LV_Overland-2026-09-27/README.md) | [Validate WP Rules build `#18264425`](https://slc-teamcity.wbiegames.com/buildConfiguration/Sundance_Dev_Tools_ContentTools_ValidateWorldPartitionRules/18264425), `-ValidateOnly`, September 27, 2026 | 6 | 90 761 of the 92 452 warnings |
| [Validate World Partition Rules — Overland only, 2026-10-04](ValidateWorldPartitionRules-Overland-2026-10-04/README.md) | TeamCity job `#2111348` *validate Overland Only*, `-ValidateOnly` discarding Hogsmeade/Hogwarts/Mission/Dungeon, October 4, 2026 | 1 | 1 054 `Runtime DataLayer without rule` of 54 892 warnings |

## Writing a new audit

- Name the file `<Topic>-<YYYY-MM-DD>.md` and add a row to [The audits](#the-audits). When the work
  is several warning families of one automated run, make it an
  [audit tree](#audit-trees) instead: a `<Pass>-<World>-<YYYY-MM-DD>/` folder whose `README.md`
  holds the source build and the tree, one document per family, and a shared `data/`.
- Open with **the problem** — why the finding matters — before any numbers. The explanation
  outlives the data.
- State **how the audit was run** (tools, queries, what was loaded) so it can be re-run and
  compared later.
- Record **what was checked and found clean**, not only the failures: a later reader needs to
  know the boundary of the sweep.
- Keep the document **readable end to end** — overview, counts and reasoning only. A list of a
  thousand actors belongs in a spreadsheet, not in a markdown table.
- Ship the actor list as **`<Topic>-<Area>-<YYYY-MM-DD>.csv`** next to the document, one file per
  area and one row per placement, and link it from the matching overview section. That is what
  whoever writes the fix script will consume.
