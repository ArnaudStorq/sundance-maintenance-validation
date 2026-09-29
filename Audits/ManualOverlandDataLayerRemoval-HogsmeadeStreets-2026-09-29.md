Parent: [Audits](README.md)

# `DL_OVERLAND` removal — `LI_HM_Streets_EXT` — 2026-09-29

Data: [`ManualOverlandDataLayerRemoval-HogsmeadeStreets-2026-09-29.csv`](ManualOverlandDataLayerRemoval-HogsmeadeStreets-2026-09-29.csv) — 1114 rows, one per audit finding.

The third fix pass on the findings of
[Hand-placed `DL_OVERLAND` under Hogwarts and Hogsmeade](ManualOverlandDataLayer-Hogwarts-Hogsmeade-2026-09-23.md),
after [`LI_EntranceHall_EXT`](ManualOverlandDataLayerRemoval-EntranceHall-2026-09-28.md) and
[`LI_Hogsmeade_River`](ManualOverlandDataLayerRemoval-HogsmeadeRiver-2026-09-28.md). It covers the
Hogsmeade streets exterior: the 1114 static meshes the audit found under
`LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade/Streets/LI_HM_Streets_EXT/`.

**Pending** as Perforce changelist **2099933**, not submitted yet — 1109 actors. Two actors are
locked by another user and three no longer exist, see
[1114 findings, 1109 actors changed](#1114-findings-1109-actors-changed).

## Contents

- [Confirming the layer is hand-placed](#confirming-the-layer-is-hand-placed)
- [1114 findings, 1109 actors changed](#1114-findings-1109-actors-changed)
- [What was changed](#what-was-changed)
- [How it was done](#how-it-was-done)
- [The file-handle conflict](#the-file-handle-conflict)
- [What was deliberately left alone](#what-was-deliberately-left-alone)
- [Follow-up](#follow-up)

---

## Confirming the layer is hand-placed

Every one of the 1111 actors that still exist was checked individually. The per-actor evidence is
in the CSV: `OverlandRuleVerdict` and `MatchingRules` for the live verdict,
`OverlandSinceRevision`, `IntroducedInCL`, `IntroducedBy` and `AutomationRevisions` for the
history.

**The rules exclude every one of them, live.** Unlike the river cluster, `LI_HM_Streets_EXT` is
loaded in the editor, so `ExplainActorAssignment` gave a verdict per actor instead of one inferred
from the rule definitions. For all 1111, `DA_OVERLAND_Rules` — index 28, the only one of the 57
DataLayer rules that targets `DL_OVERLAND` — reports *excluded by OutlinerPathsToExclude entry
'LI_Hogsmeade'*. The only rule that matches is `DA_RENDER_Rules` (index 11), which yields
`DL_RENDER`, already on the actors. None is ignored by the rules, and every one is flagged
*Non-compliant DataLayers: DL_OVERLAND*: the rules do not merely fail to assign the layer, they
say it should not be there.

**No automated pass ever wrote it.** All 1653 revisions of the 1111 external actor files were read
from the depot and searched for the layer. `DL_OVERLAND` is in revision #1 of every file — the
add — and in every revision since; it was never removed and put back. Automation has rewritten
only six of these files, 14 revisions in all: three nightly rule passes
(`@AUTOMATION $OVERLAND Applied WorldPartition rules to LV_Overland (Filter used: 'LI_Hogsmeade')`,
CLs 1764871, 1769671 and 1954169) and one resave (CL 1981772). The layer was there before and
after each of them.

**The same artist added far more meshes without it, in the same changelists.** All 1111 were
added by jprice in eleven `@MINOR $ENVIRONMENTART` changelists. A rule gives the same answer to
every `StaticMeshActor` under the same path, yet each of those changelists also added meshes to
the same Level Instance that do not carry the layer:

| Changelist | Date | Added with `DL_OVERLAND` | Added without it |
|---|---|---:|---:|
| 1761133 | 2026-03-12 | 2 | 95 |
| 1769092 | 2026-03-23 | 4 | 146 |
| 2054200 | 2026-09-02 | 872 | 32 |
| 2064180 | 2026-09-10 | 2 | 129 |
| 2067334 | 2026-09-11 | 34 | 9 |
| 2071650 | 2026-09-15 | 28 | 42 |
| 2072097 | 2026-09-15 | 47 | 4 |
| 2074186 | 2026-09-16 | 23 | 113 |
| 2076233 | 2026-09-17 | 39 | 117 |
| 2079781 | 2026-09-21 | 7 | 283 |
| 2081733 | 2026-09-22 | 53 | 211 |

Counts are static meshes still alive at head. Across the whole Level Instance, 11 658 of its
12 877 static meshes do not carry `DL_OVERLAND`. The layer follows individual editor actions —
placing while `DL_OVERLAND` is the current data layer, duplicating or copying meshes that already
have it — not a rule.

**The exclusion predates every one of these actors.** `DA_OVERLAND_Rules` has excluded
`LI_Hogsmeade` since revision #6 (CL 1323897, 2025-01-10), before it matched `StaticMeshActor` at
all (#11, CL 1367735, 2025-03-19), and still does at head (#19, CL 1982481). The oldest of these
actors was added on 2026-03-12. No other rule targeting `DL_OVERLAND` was ever registered.

**The layer is not inherited either.** `LI_HM_Streets_EXT` carries `DL_HM_EXT` and `DL_HOGSMEADE`,
`LI_Hogsmeade` carries `DL_HOGSMEADE`; neither carries `DL_OVERLAND`. Removing it genuinely takes
these actors out of the Overland streaming set.

**One rule path cannot be ruled out from the data.** Rules also run in the artist's editor: on a
manual save, `UWorldPartitionRuleSubsystem::OnPackageSaved` reapplies `DataLayerRulesForActorSave`
when the actor's world is in `MapsWithAutoApplyRules` (`LV_Overland`, `LI_Hogwarts`,
`LI_Hogsmeade`). Opening `LI_HM_Streets_EXT` on its own never triggers it. Editing it in context
from `LV_Overland` or `LI_Hogsmeade` does, and then the Outliner path contains `LI_Hogsmeade` and
the exclusion fires, as the live verdict shows. The exception is an actor the Outliner path
registry does not know yet: `GetOutlinerFullPath` returns an empty string, no path exclusion can
match, and `DA_OVERLAND_Rules` — whose conditions only test the actor class — adds `DL_OVERLAND`.
The registry is rebuilt after place, drop, duplicate, copy, delete and folder moves, but it has no
hook on paste, so a mesh pasted after the last rebuild is unknown to it. Saving such a mesh in
context would produce the layer, and it would land in the artist's changelist exactly like a
manual assignment. The removal is right either way: the layer is not what the rules intend, they
flag it as non-compliant, and a save with a resolved path will not put it back.

## 1114 findings, 1109 actors changed

| Outcome | Actors |
|---|---:|
| `DL_OVERLAND` removed, in changelist 2099933 | 1109 |
| Skipped — opened for edit by jprice | 2 |
| No longer exist — deleted after the audit | 3 |

**Two actors are locked.** Their files are `binary+l`, and jprice has them opened for edit on
`jprice-sun-3`, so they could not be checked out. They still carry the layer at head.

| Actor | Data layers | Head revision | External actor package |
|---|---|---|---|
| `SM_HW_VC_Balustrade_A168` | `DL_RENDER`, `DL_OVERLAND` | #1, CL 2081733 | `.../C/V1/0NNX0KVWSXRB492YGVBJAS` |
| `SM_HW_VC_Balustrade_A169` | `DL_RENDER`, `DL_OVERLAND` | #1, CL 2081733 | `.../A/ZY/5FUS6CJJOYM1OQ7ASNDZOY` |

**Three actors are gone.** jprice deleted them in CL 2086034 (*Lower Hogsmeade terrain update*),
submitted on 2026-09-23 after the audit snapshot. They had carried `DL_OVERLAND` since their add in
CL 2067334.

| Actor | External actor package |
|---|---|
| `SM_HW_VC_NewelPost_B104` | `.../A/CH/K2F15JHJK09TNF3S0ATGJ3` |
| `SM_HW_VC_NewelPost_B105` | `.../7/WR/PP8WS6964RF5YEPRKA33IH` |
| `SM_HW_VC_NewelPost_Boss_A96` | `.../4/KW/2RZQ908BF8QH0Q8BRZEDU3` |

Paths continue from `/Game/__ExternalActors__/Levels/Overland/Hogsmeade/Streets/LI_HM_Streets_EXT/`.

## What was changed

`DL_OVERLAND` was removed from the `DataLayerAssets` of 1109 actors. Nothing else on those actors
was touched, and no other data layer was removed.

| Before | After | Actors |
|---|---|---:|
| `DL_RENDER`, `DL_OVERLAND` | `DL_RENDER` | 1109 |

The audit's *Runtime layers on the actor* column lists only `DL_OVERLAND` because `DL_RENDER` is an
Editor data layer: it drives editor loading rather than streaming, and it was preserved.

One external actor package per actor was saved — 1109 files, all in changelist **2099933**. No
level, no `WorldDataLayers` actor and no rule asset was modified.

After the change, `ExplainActorAssignment` was run again on all 1111 actors. The verdict is
identical — same matching rule, same exclusion — and the 1109 are no longer flagged non-compliant.
The two locked actors still are.

The pending description:

```
@MINOR $TOOLS
Remove hand-placed DL_OVERLAND from LI_HM_Streets_EXT static meshes
&TESTED Editor
@REVIEW Philippe St-Jean (WBGMontreal)
[jira:SUNDANCE-77683]
```

## How it was done

1. The 1114 target rows were taken from the 2026-09-23 audit CSV, filtered on
   `ContainingLevelInstance = LI_HM_Streets_EXT`. All are `StaticMeshActor` and `RuleMismatch`,
   carrying `DL_OVERLAND` on the actor and inheriting `DL_HM_EXT`.
2. Each row was matched on its GUID to a live actor descriptor, which yielded the external actor
   package and its file on disk. 1111 matched; the other three no longer exist.
3. The checks of [Confirming the layer is hand-placed](#confirming-the-layer-is-hand-placed) were
   run on all 1111. `ExplainActorAssignment` was queried with the actor's object name, which
   carries its UAID: an Outliner path is matched as a substring, so `…_A2` also hits `…_A20`.
4. Perforce state was checked before any edit: all 1111 files at head revision, two opened by
   jprice. `p4 opened -a` does not show those two — this workspace sits on an edge server, and the
   command only lists opens made on that server — whereas `p4 fstat` and `p4 edit` see the lock.
5. Changelist 2099933 was created and the 1109 free files checked out into it.
6. In the editor, each external actor package was loaded directly, `DL_OVERLAND` was dropped from
   `DataLayerAssets`, and the package was saved. The first batch failed, see
   [The file-handle conflict](#the-file-handle-conflict); once it was fixed, the 1109 saved in four
   batches, in under a minute.
7. The result was verified on disk, not in memory. All 1111 files were re-read: the 1109 saved ones
   no longer contain `DL_OVERLAND` and still contain `DL_RENDER`, and the two locked ones are
   untouched. `p4 diff` reports 1109 modified files and no opened file identical to the depot,
   `p4 reconcile -n` over the Level Instance's external actor folder finds nothing else changed,
   and the editor log shows no save error.
8. The live verdict was taken again after the change, and the changelist was left pending.

## The file-handle conflict

The first 50 saves all failed with `MoveFile was unable to move ... (Error Code 32)` — the same
sharing violation that left five actors behind in the
[`LI_EntranceHall_EXT` pass](ManualOverlandDataLayerRemoval-EntranceHall-2026-09-28.md#actors-that-were-skipped).
Nothing was damaged: the files on disk were still identical to the depot.

The cause is the editor's own copy of the Level Instance. `LI_HM_Streets_EXT` was loaded in
`LV_Overland` as an instance inside `LI_Hogsmeade`, which loads every external actor a second time
under a `/Temp/.../LI_HM_Streets_EXT_LevelInstance_<id>_InstanceOf_/Game/__ExternalActors__/...`
package. Those packages keep the source `.uasset` files open, and `SavePackage` writes a temporary
file and then moves it over the original, which Windows refuses while the file is open.

It does not take an editor restart:

1. Find the Level Instance actor. A nested one is not returned by `get_all_level_actors()`;
   iterate `unreal.ObjectIterator(unreal.LevelInstance)` and match on the label.
2. Call `unload_level_instance()` on it. The unload happens on the next editor tick, not during
   the call.
3. Run `unreal.SystemLibrary.collect_garbage()`. The instance packages went from 13 001 to 0 and
   the handles were released.
4. Save, then call `load_level_instance()` to restore the editor state.

Two traps for the next script. External actor packages are reported by `get_dirty_map_packages()`,
not `get_dirty_content_packages()`, so checking the content list after a save reports success even
when every save failed: the file on disk is the only reliable verdict. And each failed save leaves
an orphan `<package><hash>.tmp` in `Saved/`; the 50 from this pass were deleted.

## What was deliberately left alone

- **The two locked actors**, `SM_HW_VC_Balustrade_A168` and `SM_HW_VC_Balustrade_A169`.
- **108 static meshes added since the audit that carry the layer too**, all in
  `LI_HM_Streets_EXT`: 26 from jprice's CL 2086034 (2026-09-23) and 82 from parker.miltsch's
  CL 2091753 (2026-09-25, *Replaced single sidewalk pavers in hosmeade with updated ones*). They
  are not audit findings, so they are out of this pass — but the layer keeps arriving on new
  actors.
- **The rest of Hogsmeade** — `LI_Camp_Crate_Food_A` (149, nested inside `LI_HM_Streets_EXT` but
  with its own actor packages), `LI_HM_StreetDressing_EXT` (13),
  `LI_HM_StreetDressing_WPV_Trashed_EXT` (14), `LI_Tomes_POP` (1).
- **Hogwarts interiors** (177 actors), still waiting on the visible-from-outside check.
- **Foliage** (`PlacedFoliageSkinnedNaniteAssembly`), where `DL_OVERLAND` is the legitimate
  fallback and a rule is needed rather than an edit.

## Follow-up

- **Submit changelist 2099933 soon.** It holds exclusive locks on 1109 files of a Level Instance
  jprice is actively working on: he has two of its files open and has submitted three changelists
  there since 2026-09-21.
- Finish the two balustrades once jprice releases them, or ask him to drop `DL_OVERLAND` in his
  own change.
- Treat the 108 new carriers the same way, and find out how the layer is being set — a current
  data layer left on in the artists' editors, or copies of tagged meshes — or it will keep coming
  back.
- Rule side: close the unresolved-path case described in
  [Confirming the layer is hand-placed](#confirming-the-layer-is-hand-placed). Rebuilding
  `UWorldPartitionOutlinerPathRegistry` on paste, or refusing to apply path-excluded rules when the
  path is empty, would do it.
- The five `LI_EntranceHall_EXT` actors skipped on the same `Error Code 32` can most likely be
  finished by unloading their Level Instance, without a restart.
- Reopen the streets in the Overland view and confirm nothing disappeared, then re-run the
  streaming generation snapshot and check that the `DL_HM_EXT + DL_OVERLAND` cells of the streets
  are gone.
