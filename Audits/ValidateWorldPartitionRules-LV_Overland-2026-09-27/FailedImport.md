Parent: [Validate World Partition Rules — LV_Overland, 2026-09-27](README.md)

# Audit — "Failed import" warnings on `LV_Overland`

**Status:** proposal, awaiting content-owner confirmation
**Date:** October 1, 2026
**Scope:** every `Failed import` row raised by the World Partition rules pass on `LV_Overland`

| Item | Value |
| --- | --- |
| Reviewed report | `report.txt` (WPRulesReviewer export) |
| Source log | `Sundance_Validate_27September_validate-LV_Overland.log` (56.3 MB, 269,968 lines) |
| World | `LV_Overland` |
| Log time | September 27, 2026 |
| Pass | `Validate WP Rules` |
| Raw inventory | [`data/failed-import-inventory.csv`](data/failed-import-inventory.csv) |

## Contents

- [1. Executive summary](#1-executive-summary)
- [2. Anatomy of the warning](#2-anatomy-of-the-warning)
- [3. Inventory](#3-inventory)
  - [3.1 By referencing `GroupActor`](#31-by-referencing-groupactor)
  - [3.2 Missing actors](#32-missing-actors)
  - [3.3 Why every failure is logged twice](#33-why-every-failure-is-logged-twice)
- [4. Root cause](#4-root-cause)
  - [4.1 `AGroupActor` is incompatible with One File Per Actor](#41-agroupactor-is-incompatible-with-one-file-per-actor)
  - [4.2 Supporting evidence](#42-supporting-evidence)
  - [4.3 Ruled out](#43-ruled-out)
- [5. Impact](#5-impact)
- [6. Remediation proposal](#6-remediation-proposal)
  - [6.1 Options](#61-options)
  - [6.2 Recommended plan (Option A)](#62-recommended-plan-option-a)
  - [6.3 Scripted alternative for step 3](#63-scripted-alternative-for-step-3)
- [7. Tool-side improvements (WPRulesReviewer)](#7-tool-side-improvements-wprulesreviewer)
  - [7.1 The parser merges two paths into `ActorPath`](#71-the-parser-merges-two-paths-into-actorpath)
  - [7.2 `ImportError` rows are never de-duplicated](#72-importerror-rows-are-never-de-duplicated)
  - [7.3 No grouping by referencing export](#73-no-grouping-by-referencing-export)
  - [7.4 Fix Advisor has no actionable path](#74-fix-advisor-has-no-actionable-path)
- [8. Prevention](#8-prevention)
- [9. Acceptance criteria](#9-acceptance-criteria)
- [Appendix A — Reproducing the inventory](#appendix-a--reproducing-the-inventory)
- [Appendix B — Figures quoted in this audit](#appendix-b--figures-quoted-in-this-audit)

---

## 1. Executive summary

The report lists **22 `Failed import` rows**, all classified `High / Anomaly`
("Asset import failure (blocker)"). They are not 22 distinct problems:

- **11 unique failing imports**, each logged **twice** because the level is loaded twice during the
  pass (once as a nested level instance, once directly).
- All 11 belong to **a single level**: `/Game/Levels/Sanctuary/ConversationHub/LI_Sanctuary_ConversationHub_Props`.
- All 11 are triggered by **6 legacy `AGroupActor` actors** whose member lists still point at
  `StaticMeshActor`s that no longer exist in the depot.
- These 22 lines are **100 % of the `LoadErrors` emitted by the whole run** — fixing this one level
  clears the entire `Failed import` category.

**Proposed fix:** delete the 6 stale `GroupActor`s (`AGroupActor` is an editor-only UE4 grouping
construct that World Partition / One File Per Actor does not support) and replace the grouping
intent with Actor Folders or a Level Instance. Expected result: 22 → 0 `Failed import` rows, with no
runtime or HLOD behaviour change.

---

## 2. Anatomy of the warning

Raw log line (line 263897, wrapped for readability):

```text
[2026.09.27-18.54.07:643][  0]LoadErrors: Error:
  /Temp/Game/Levels/Sanctuary/ConversationHub/LI_Sanctuary_ConversationHub_Props_LevelInstance_6be3b98da1e5cf9f_0_InstanceOf_/Game/__ExternalActors__/Levels/Sanctuary/ConversationHub/LI_Sanctuary_ConversationHub_Props/0/H3/NLCY0Y7WPYLXDGITAG3R7W
  : Failed import for StaticMeshActor
  /Game/Levels/Sanctuary/ConversationHub/LI_Sanctuary_ConversationHub_Props.LI_Sanctuary_ConversationHub_Props:PersistentLevel.StaticMeshActor_UAID_047BCBA9AF330DB302_2121370891
  Referenced by export GroupActor
  /Game/Levels/Sanctuary/ConversationHub/LI_Sanctuary_ConversationHub_Props.LI_Sanctuary_ConversationHub_Props:PersistentLevel.GroupActor_UAID_047BCBA9AF330DB302_2121373892
```

Four distinct pieces of information are packed into one line:

| Field | Meaning |
| --- | --- |
| `__ExternalActors__/.../0/H3/NLCY0Y7WPYLXDGITAG3R7W` | The One File Per Actor package being loaded — i.e. the **file to check out in Perforce** |
| `Failed import for StaticMeshActor …_2121370891` | The object the package expected to resolve and could **not** find |
| `Referenced by export GroupActor …_2121373892` | The object **inside** that package holding the dangling reference |
| `/Temp/…_LevelInstance_<hash>_0_InstanceOf_` prefix | The load happened through a Level Instance, in a temp package |

The key structural detail: the failing import targets an object in the **same level package** as the
export that references it. That self-package reference shape only occurs with OFPA, where every
actor lives in its own file and sibling actors are reached through import stubs. A missing sibling
file therefore surfaces as a *failed import*, not as a "missing asset".

---

## 3. Inventory

### 3.1 By referencing `GroupActor`

Level: `/Game/Levels/Sanctuary/ConversationHub/LI_Sanctuary_ConversationHub_Props`

| `GroupActor` (export) | External actor package | Missing `StaticMeshActor`s |
| --- | --- | ---: |
| `GroupActor_UAID_047BCBA9AF33FCB802_1361645163` | `__ExternalActors__/…/E/A6/4V6R5EKMI3VFC98J6I2MTB` | 6 |
| `GroupActor_UAID_047BCBA9AF330DB302_2121373892` | `__ExternalActors__/…/0/H3/NLCY0Y7WPYLXDGITAG3R7W` | 1 |
| `GroupActor_UAID_047BCBA9AF330CB302_2061962692` | `__ExternalActors__/…/1/QR/2TQKY1OIITMBPD25INPJN4` | 1 |
| `GroupActor_UAID_047BCBA9AF33DFB602_1360801125` | `__ExternalActors__/…/2/TU/OTDQEFBNF50PHDBMCG1ZXP` | 1 |
| `GroupActor_UAID_047BCBA9AF330DB302_2119742890` | `__ExternalActors__/…/7/27/8921SDNM1MOPO4DMRGN603` | 1 |
| `GroupActor_UAID_047BCBA9AF3314B302_1398919469` | `__ExternalActors__/…/7/O5/92CFDFA2MG4U979KROJWZ8` | 1 |
| **Total** | **6 packages** | **11** |

The mapping is strictly one package per `GroupActor`, which confirms each broken group is a single
external actor file to fix.

### 3.2 Missing actors

| # | Missing object |
| --- | --- |
| 1 | `StaticMeshActor_UAID_047BCBA9AF3308B302_1564870971` |
| 2 | `StaticMeshActor_UAID_047BCBA9AF330DB302_1867635882` |
| 3 | `StaticMeshActor_UAID_047BCBA9AF330DB302_2121370891` |
| 4 | `StaticMeshActor_UAID_047BCBA9AF330EB302_1117400075` |
| 5 | `StaticMeshActor_UAID_047BCBA9AF3373B202_2079038755` |
| 6 | `StaticMeshActor_UAID_047BCBA9AF33B9AC02_1586404751` |
| 7 | `StaticMeshActor_UAID_047BCBA9AF33B9AC02_1586440789` |
| 8 | `StaticMeshActor_UAID_047BCBA9AF33C8AC02_1496447341` |
| 9 | `StaticMeshActor_UAID_047BCBA9AF33CAAC02_1536015752` |
| 10 | `StaticMeshActor_UAID_047BCBA9AF33CBAC02_1790731932` |
| 11 | `StaticMeshActor_UAID_047BCBA9AF33CCAC02_1770764131` |

All 11 share the `047BCBA9` package-GUID prefix of `LI_Sanctuary_ConversationHub_Props`, so they
were originally authored in that level — they were not moved in from elsewhere.

### 3.3 Why every failure is logged twice

| Pass | Timestamp | Trigger | Loaded package |
| --- | --- | --- | --- |
| 1 | 18:54:07 | `Loading LevelInstance: LV_Overland/Sanctuary/LI_Sanctuary` | `/Temp/…_LevelInstance_6be3b98da1e5cf9f_0_InstanceOf_/Game/__ExternalActors__/…` |
| 2 | 18:57:41 | `Loading LevelInstance: LV_Overland/Sanctuary/LI_Sanctuary/LI_Sanctuary_ConversationHub_Props` | `/Game/__ExternalActors__/…` (source package) |

The builder walks the level-instance tree and loads `LI_Sanctuary_ConversationHub_Props` both as a
child of `LI_Sanctuary` and on its own. Both loads hit the same 11 unresolvable imports. This is
expected builder behaviour, not a second defect — but see §7.2: the review tool should collapse the
pair instead of reporting 22 anomalies.

---

## 4. Root cause

### 4.1 `AGroupActor` is incompatible with One File Per Actor

`AGroupActor` is a UE4-era, **editor-only** convenience: it owns a hard
`TArray<AActor*> GroupActors` member list and exists purely so artists can move a set of actors
together in the Outliner. It has no runtime representation, no effect on HLOD, streaming, data
layers or runtime grids.

Under World Partition with OFPA:

1. Each actor — including the `GroupActor` itself — is serialised into its own
   `__ExternalActors__/<bucket>/<hash>` package.
2. The `GroupActor` package stores its members as **imports** into the level's `PersistentLevel`.
3. When a member actor's external package is deleted, nothing updates the group's member list: the
   group's own package is a separate file and is not touched by the deletion.
4. On the next load, the group's import cannot be resolved → `LoadErrors: Error: … Failed import`.

So the defect is **stale group membership**, and the enabling condition is that groups were kept
after the World Partition conversion.

### 4.2 Supporting evidence

- The missing UAIDs appear **nowhere else** in the 270k-line log — not as `Applying rules on actor`,
  not as a warning, not as a skip. Their packages are genuinely absent from the workspace, they are
  not merely failing to deserialise.
- The 6 `GroupActor`s themselves load fine (they are the *exports* doing the referencing), so the
  group assets are intact; only their member lists are wrong.
- `LoadErrors` fires exactly 22 times in the entire run, all of them this shape. There is no broader
  content-loading problem in `LV_Overland`.

### 4.3 Ruled out

| Hypothesis | Verdict |
| --- | --- |
| Missing `StaticMesh` / material asset | **No** — the failing import is a `StaticMeshActor` (a level actor), not a content asset |
| Incomplete Perforce sync on the build agent | **Unlikely** — a partial sync would produce load errors spread across many levels; the failures are confined to one level and one actor class |
| Parser misreading the log | **No** — the raw log lines match the report one-for-one (§2) |
| Rule-configuration problem | **No** — no `DA_*` rule is involved; the failure happens at level load, before rule evaluation |

---

## 5. Impact

| Dimension | Assessment |
| --- | --- |
| Runtime / shipping | **None.** `AGroupActor` is editor-only; a null member resolves to an ignored entry. |
| Build log hygiene | **Medium.** 22 `LoadErrors: Error:` lines on every run. Any CI step that treats load errors as fatal (`-FatalLoadErrors` and similar) would fail the build. |
| Review cost | **Medium.** 22 `High` anomalies to triage on every single pass, for 11 real items that never change. |
| Rule coverage | **To confirm.** No actor under `LV_Overland/Sanctuary` is processed in this run (0 of 122,234 `Applying rules on actor` lines), and only 1 of 92,452 rule warnings mentions Sanctuary. This is *consistent* with the rule set being Hogsmeade-centric (114,925 actors) rather than caused by the failed imports, but it should be verified explicitly — see §8. |
| Editor authoring | **Low but real.** Opening the level, selecting the group, or ungrouping will resave a `GroupActor` with a corrupt member list and can silently drop the surviving members from the group. |

---

## 6. Remediation proposal

### 6.1 Options

| Option | Action | Pros | Cons | Verdict |
| --- | --- | --- | --- | --- |
| **A** | Delete the 6 stale `GroupActor`s and re-express the grouping with Actor Folders / a Level Instance | Removes the root cause; aligns the level with World Partition conventions; no runtime change | Artists lose the group selection shortcut until folders are created | **Recommended** |
| **B** | Restore the 11 deleted `StaticMeshActor` packages from Perforce history | Keeps the groups intact | Only valid if the deletion was accidental; re-adds props and changes the level visually; must be signed off by the level owner | Conditional — only for actors a content owner confirms were deleted by mistake |
| **C** | Strip the null entries from each `AGroupActor::GroupActors` and resave | Minimal diff; fast | Leaves `AGroupActor` in a World Partition level, so the same class of breakage will recur | Stopgap only |
| **D** | Downgrade / suppress `LoadErrors` for group actors | Zero content churn | Hides a real data error and makes the next occurrence invisible | **Rejected** |

### 6.2 Recommended plan (Option A)

| Step | Action | Owner |
| --- | --- | --- |
| 1 | Confirm with the Sanctuary level owner that the 11 `StaticMeshActor`s (§3.2) were deliberately deleted. If any were not, handle those via Option B **first**. | Level art |
| 2 | `p4 edit` the level package `/Game/Levels/Sanctuary/ConversationHub/LI_Sanctuary_ConversationHub_Props.umap` and `p4 edit` the 6 external actor packages listed in §3.1. | Fixer |
| 3 | Open the level with load errors tolerated, select each of the 6 broken groups, `Ungroup` (Ctrl+Shift+G), then delete the now-empty `GroupActor`. | Fixer |
| 4 | Recreate the authoring intent with **Actor Folders** in the WP Outliner (or a Level Instance if the set is reused elsewhere). | Level art |
| 5 | Save the level → the 6 external actor packages are marked for delete. `p4 revert -a` to drop untouched files, then submit one changelist describing the audit. | Fixer |
| 6 | Re-run the `Validate WP Rules` pass on `LV_Overland` and confirm 0 `LoadErrors`. | CI |

### 6.3 Scripted alternative for step 3

For a repeatable fix (and to handle other levels found by §8), a small commandlet or Editor Utility
Blueprint is preferable to manual edits:

```text
for each AGroupActor in the world:
    members = group.GroupActors
    if any member is null or unresolved:
        log  group package path, member count, null count
        if -fix was passed:
            checkout the group's external actor package
            group.Destroy()            # or: remove null entries only
            mark the package dirty
save dirty packages
```

Run it read-only first across all `LV_*` worlds to size the problem before fixing anything.

---

## 7. Tool-side improvements (WPRulesReviewer)

The audit surfaced four concrete defects in how the reviewer handles this warning family. They do
not fix the content, but they make this category correctly counted and actionable.

### 7.1 The parser merges two paths into `ActorPath`

`LogParser.FailedImport()` (`Tools/WPRulesReviewer/src/WPRulesReviewer.Core/Parsing/LogParser.cs`, lines 187–189) ends with
a greedy `(.+)$`, so the `Referenced by export <Class> <Path>` tail is swallowed into the object
path:

```csharp
[GeneratedRegex(@"^(.*?)\s*:\s*Failed import for\s+(\S+)\s+(.+)$")]
private static partial Regex FailedImport();
```

Consequences in `ParseError` (lines 203–212):

- `ActorPath` holds **two** concatenated object paths, so the grid's *Actor* column is unreadable and
  cannot be copied into the editor.
- `ActorName` is computed with `LeafOf(ActorPath)`, which returns the **referencing `GroupActor`**,
  not the missing actor — the column silently names the wrong object.
- The external actor package (group 1) is discarded, even though it is the only field that tells the
  fixer which Perforce file to check out.

**Proposed shape:** capture the three parts separately and keep the package path.

```csharp
// LoadErrors: "<package> : Failed import for <Class> <object path> [Referenced by export <Class> <object path>]"
[GeneratedRegex(@"^(?<pkg>.*?)\s*:\s*Failed import for\s+(?<cls>\S+)\s+(?<obj>\S+?)(?:\s+Referenced by export\s+(?<refCls>\S+)\s+(?<ref>\S+))?\s*$")]
private static partial Regex FailedImport();
```

Then set `ActorPath` to the missing object, `ActorName` to its leaf, and put the referencing export
and the owning package into `Reason` (or dedicated fields) so both are visible and copyable.

### 7.2 `ImportError` rows are never de-duplicated

`LogParser.Add()` (lines 360–374) only collapses `Warning` and `Skipped`:

```csharp
var dedupable = options.DeduplicateWarnings &&
                rec.Category is RecordCategory.Warning or RecordCategory.Skipped;
```

Because the builder loads each level twice (§3.3), every import failure is counted twice. Adding
`RecordCategory.ImportError` to that list makes the report show **11 rows with `x2`** instead of 22
rows with `x1`. `RuleRecord.Key` (`Tools/WPRulesReviewer/src/WPRulesReviewer.Core/Models/RuleRecord.cs`, line 86) already
excludes `LineNumber`, so no other change is needed — but it depends on §7.1, since today the two
copies differ only by line number and would collapse correctly only once `ActorPath` is clean.

### 7.3 No grouping by referencing export

A single `GroupActor` accounts for 6 of the 11 failures, yet the reviewer shows 6 independent
anomalies. Grouping `ImportError` records by the referencing export would collapse them into one row
("`GroupActor_…1361645163` — 6 unresolved members"), which matches the unit of work: one external
actor package to check out and fix.

`SessionViewModel.ImportErrorGroups` already exists; it needs a dimension keyed on the referencing
export, which §7.1 makes available.

### 7.4 Fix Advisor has no actionable path

`IssueTypes.Of()` (`Tools/WPRulesReviewer/src/WPRulesReviewer.Core/Models/IssueTypes.cs`, lines 15–17) correctly labels the
family `"Failed import"`, and `OracleEvaluator` (line 78) marks it `High / "Asset import failure
(blocker)"`. But the AI advisor only receives the mangled `ActorPath`, so it cannot propose a
concrete fix. Once §7.1 lands, the prompt should include the external actor package path and the
referencing export class, which is enough for the advisor to name the exact Perforce files and the
`Ungroup` remedy.

---

## 8. Prevention

| Measure | Description |
| --- | --- |
| **Content validator** | An `UEditorValidatorBase` on `UWorld` that fails validation when a World Partition level contains an `AGroupActor` with unresolved members — and, as a stricter policy, when it contains any `AGroupActor` at all. Wired into changelist validation, this blocks the defect at submit time. |
| **Project-wide sweep** | Run the read-only pass of §6.3 across every `LV_*` world. This audit only covers `LV_Overland`; other worlds very likely carry the same legacy groups. |
| **CI gate** | The rules-processing step currently reports `Errors: 0` while the log contains 22 `LoadErrors: Error:` lines, because the tally deliberately counts only `LogWorldPartitionRules` output. Add a separate `LoadErrors` threshold (fail above 0) so import failures cannot sit unnoticed between runs. |
| **Rule-coverage check** | Confirm that `LV_Overland/Sanctuary` having 0 processed actors is intentional. If Sanctuary is meant to be covered, the missing coverage is a second, larger finding that this audit did not scope. |

---

## 9. Acceptance criteria

1. The `Validate WP Rules` pass on `LV_Overland` reports **0** `LoadErrors: Error:` lines.
2. The WPRulesReviewer report shows **0** rows of type `Failed import`.
3. `LI_Sanctuary_ConversationHub_Props` contains no `AGroupActor`, and the grouping intent is
   preserved as Actor Folders or a Level Instance.
4. The level loads with no `LoadErrors` both standalone and as a child of `LI_Sanctuary`.
5. A content validator rejects any new `AGroupActor` with unresolved members.

---

## Appendix A — Reproducing the inventory

Extract every failed import from a `Sundance.log` into the structured form used in §3:

```powershell
$log = "Sundance_Validate_27September_validate-LV_Overland.log"
$i = 0
foreach ($line in [System.IO.File]::ReadLines($log)) {
    $i++
    if ($line -notmatch 'Failed import') { continue }
    $m = [regex]::Match($line, 'LoadErrors: Error: (?<pkg>\S+) : Failed import for (?<cls>\S+) (?<obj>\S+) Referenced by export (?<refCls>\S+) (?<ref>\S+)$')
    [pscustomobject]@{
        LogLine      = $i
        Package      = $m.Groups['pkg'].Value
        MissingClass = $m.Groups['cls'].Value
        Missing      = $m.Groups['obj'].Value -replace '^.*PersistentLevel\.', ''
        ReferencedBy = $m.Groups['ref'].Value -replace '^.*PersistentLevel\.', ''
    }
}
```

The result for the September 27 run is committed as
[`data/failed-import-inventory.csv`](data/failed-import-inventory.csv) (22 rows, one per log line).

## Appendix B — Figures quoted in this audit

| Metric | Value | Source |
| --- | ---: | --- |
| Log lines | 269,968 | source log |
| `Applied` assignments | 9,506 | report summary |
| Rule warnings | 92,452 | report summary |
| Anomalies | 1,935 | report summary |
| `Failed import` rows | 22 | report, `ImportError` category |
| Unique failed imports | 11 | §3.2 |
| Referencing `GroupActor`s | 6 | §3.1 |
| Affected levels | 1 | §3.1 |
| `LoadErrors` lines in the log | 22 | all `Failed import` |
| `Applying rules on actor` lines | 122,234 | source log |
| … under `LV_Overland/Sanctuary` | 0 | §5 |
| `Loading LevelInstance` lines | 8,222 | source log |
