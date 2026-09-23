Parent: [Sundance Maintenance & Validation](../README.md)

# Audits

Point-in-time sweeps of `LV_Overland` content: what was scanned, what was found, and the exact
list of actors to fix.

An audit is dated and **does not age well** — it describes the level as it was on that day. Read
the *problem* sections for lasting knowledge, and treat the actor lists as a work order that is
only valid until someone fixes them.

## Contents

- [How an audit differs from a reference doc](#how-an-audit-differs-from-a-reference-doc)
- [The audits](#the-audits)
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
| [Hand-placed `DL_OVERLAND` under Hogwarts and Hogsmeade](ManualOverlandDataLayer-Hogwarts-Hogsmeade-2026-09-23.md) | Whole world, 667 859 actor descriptors, kept under `LI_Hogwarts` and `LI_Hogsmeade` | 3047 actors carrying a `DL_OVERLAND` that no rule can assign, in 13 Level Instances | [Actor list](ManualOverlandDataLayer-Hogwarts-Hogsmeade-2026-09-23.csv) |

## Writing a new audit

- Name the file `<Topic>-<YYYY-MM-DD>.md` and add a row to [The audits](#the-audits).
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
