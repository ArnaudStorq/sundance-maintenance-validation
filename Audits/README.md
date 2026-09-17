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
