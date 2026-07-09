# Transcripts — Analysis & Summary

This document synthesizes **48 working sessions** captured between **May 4 and July 9, 2026**.
The individual conversations, converted to Markdown, live in [`Content/`](./Content) and are named
`YYYY-MM-DD-HH-MM-<short-topic>.md`.

The overwhelming majority of the work revolves around one production problem in the **Sundance**
(Unreal Engine 5.7) open world: **World Partition streaming rules, HLOD layers, and the
`Actor has an invalid HLOD layer` / `rule 'DA_SmallGrid_Rules' cannot use HLOD layer` map-check
warnings** — how to understand them, fix the underlying data, and validate the fix without breaking
anything else. The rest is supporting tooling, knowledge capture, and unrelated one-offs.

---

## 1. Executive summary

- The core issue: **inner actors of non-partitioned Level Instances** carry `HLODLayer`,
  `DataLayers`, and/or `RuntimeGrid` values that are **invalid for the partition they end up in**.
  These inherited/stale values trigger map-check warnings and streaming-generation errors on
  `LV_Overland`.
- Two complementary strategies were explored and iterated on for weeks:
  1. **Data cleanup** — clear the offending `HLODLayer` / `DataLayers` / `RuntimeGrid` on the guilty
     actors, check the packages out of Perforce, and re-save them (via a Map-Check auto-fix hook and
     via dedicated World Partition builder commandlets).
  2. **Convert the levels to World Partition** — so streaming rules operate at per-actor granularity
     (`Add Partitioned Streaming Support`), which is the "proper" long-term fix.
- The single most painful recurring trap: **re-saving an actor package silently drifts
  `RelativeLocation` / `RelativeRotation` / `RelativeScale3D`** (and sometimes
  `EditorOnlySeasonsDefaultMesh`). A large part of the effort went into detecting this drift with a
  Perforce diff and **reverting** any package that changed only transforms.
- A parallel track hardened the **submit-time validation** (Peeves): raise a **blocking error** when
  a changelist touches a Level that is *not* World Partition-enabled and *is* referenced by
  `LV_Overland`.
- Everything is glued together by a family of **log-parsing and reporting utilities** (unique-level
  extraction, map-check reports, Perforce changelist → PDF reports) and by **knowledge capture**
  (video transcriptions of colleague explanations, Miro boards, OneNote pages).

---

## 2. The central technical thread — "invalid HLOD layer"

### 2.1 Root cause (as finally understood)

- In `LV_Overland`, geometry is assembled through **Level Instances**. A *partitioned* Level Instance
  can host **non-partitioned** sub-levels (`.umap`) and other nested Level Instances.
- Inner actors of those non-partitioned sub-levels still reference streaming properties
  (`HLODLayer` = `LV_Overland_HLODLayer_Near`, `DataLayers`, `RuntimeGrid`). Historically they were
  processed by the `WorldPartitionRuleBuilder`; once that processing was narrowed to partitioned Level
  Instances only, the **old values were left behind** on the inner actors.
- At streaming generation / map check, those leftover values are **invalid for the actor's effective
  partition**, so Unreal reports `... has an invalid HLOD layer ...`.
- The related warning `rule 'DA_SmallGrid_Rules' cannot use HLOD layer 'LV_Overland_HLODLayer_Near'
  on that partition` comes from the same family: the `DA_SmallGrid_Rules` runtime-grid rule cannot
  legally apply `LV_Overland_HLODLayer_Near` on the `SmallGrid`/`HogsmeadeGrid` partition
  (`HogsmeadeGrid` = 32 m cell / 64 m range; `SmallGrid` = 76.2 m cell / 128 m range).

### 2.2 What actually fixes it

- Clear `HLODLayer` (and, when set, `DataLayers` and `RuntimeGrid`) on the **inner actors** of the
  affected Level Instances — never on the Level Instance actor itself.
- Only touch an actor if the property was actually set (skip → no checkout, no re-save).
- Check the package out of Perforce (auto-checkout, handling read-only files and files locked by
  other users), then save.
- For non-partitioned sub-levels, the inner actors live inside the **sub-world `.umap`** (not in
  `__ExternalActors__`), so the actor descriptor must be regenerated on save.

### 2.3 The recurring hazard: transform drift on save

- Re-saving packages frequently rewrote `RelativeLocation` / `RelativeRotation` / `RelativeScale3D`
  (Brush components were one identified source), producing unacceptable diffs.
- Mitigation that stuck: after saving, **diff against the checked-out Perforce revision**; if only
  transform-related fields changed, **revert the package entirely**. Simpler and more reliable than
  trying to prevent the drift during serialization.

### 2.4 Operational learnings

- **Files locked by other users** (e.g. `jprice @ //sun/Dev`) cannot be checked out — the tooling
  must produce an actionable report (owner, full Perforce path, outliner path, affected actor list)
  so the right person can release the file.
- **Live Coding** was used heavily for fast iteration; implementations had to be Live-Coding-safe.
- Loading full actors is expensive; batch runs over `LV_Overland` can take a very long time, which
  repeatedly pushed the work toward narrower, targeted fixes driven by the map-check warning list.

### 2.5 Key sessions for this thread

| Date | Session |
| --- | --- |
| 2026-05-27 | [Fixup non-partitioned actors builder — clear HLOD/DataLayers/Grid](./Content/2026-05-27-10-48-fixup-nonpartitioned-actors-builder-clear-hlod-datalayers-grid.md) |
| 2026-05-28 | [Invalid-HLODLayer map-check auto-fix, checkout & locked-file report](./Content/2026-05-28-09-06-invalid-hlodlayer-mapcheck-autofix-checkout-locked-report.md) |
| 2026-06-05 | [Streaming-generation inline HLOD fixup + sanity-check revert](./Content/2026-06-05-11-10-streaminggeneration-inline-hlod-fixup-sanity-check-revert.md) |
| 2026-06-05 | [Rewrite of the non-partitioned levels builder + DryRun report](./Content/2026-06-05-14-56-rewrite-fixup-nonpartitioned-levels-builder-dryrun-report.md) |
| (undated) | [RuleBuilder RelativeLocation drift diagnosis](./Content/2026-04-17-09-57-worldpartitionrulebuilder-relativelocation-drift-diagnosis.md) |
| (undated) | [RuleBuilder — log transforms before/after save](./Content/2026-04-27-17-48-rulebuilder-log-relativelocation-rotation-before-after-save.md) |

---

## 3. Converting Levels to World Partition (the long-term fix)

- Non-partitioned levels can be upgraded with **`Add Partitioned Streaming Support`** (Content Browser
  right-click) / `Tools → Convert Level`, which gives per-actor streaming granularity.
- Automating this at scale hit real friction:
  - `WorldPartitionEditorModule.ConvertMap` spawns a dialog per level → needed a **dialog-free,
    auto-checkout** variant with default settings + `In Place = true`.
  - Some conversions failed **only in headless/commandlet mode**, traced to **Nanite assembly
    builds** crashing; workaround was to disable the Nanite build via cvar since conversion only needs
    load + re-save.
  - After conversion, warnings can persist because actors still have `IncludeInHLOD = true` /
    `HLODLayer` set; the **mutator only overrides `RuntimeGrid`**, it does not clear actor attributes.
- Related understanding: an actor can be **HLOD-relevant without an HLODLayer**; `SmallGrid` semantics;
  why a partitioned `LI_GEN_Bridge_B` still warns.

Key sessions:
[Convert level to WP (how-to)](./Content/2026-06-23-13-11-how-to-convert-level-to-world-partition-ue5.md) ·
[IncludeInHLOD + batch conversion commandlet](./Content/2026-06-25-09-25-includeinhlod-convert-levels-wp-commandlet-batch.md) ·
[SmallGrid warning / IncludeInHLOD / conversion](./Content/2026-07-02-14-25-smallgrid-hlod-warning-includeinhlod-levels-conversion.md) ·
[AddPartitionedStreamingSupport converts too few actors + BP_Mirror bug](./Content/2026-06-29-16-36-addpartitionedstreamingsupport-few-actors-bpmirror-bug.md) ·
[HLOD actor without HLODLayer — use case](./Content/2026-06-30-09-18-hlod-actor-without-hlodlayer-usecase.md) ·
[RuntimeGrid/DataLayer conflict — solution options + Miro board](./Content/2026-07-07-14-00-runtimegrid-datalayer-conflict-solutions-miro-board.md)

---

## 4. Submit-time validation (Peeves)

- Goal: when an artist submits a changelist that modifies a Level (the `.umap` **or** any of its inner
  actors, including the non-OFPA case) that is **not** World Partition-enabled, Peeves should raise a
  **blocking error** guiding them to `Add Partitioned Streaming Support`.
- Important design decisions from the plan:
  - **Skip validation entirely** if the Level is *not* referenced by `LV_Overland` (test this first —
    it also bounds the cost of the reference check through nested Level Instances).
  - Exclude `Developers/` and `Plugins/` folders.
  - Concern raised: validating only at submit time is late — the artist may have already invested work
    and a conversion can risk data loss.

Key sessions:
[Peeves non-partitioned level validation — plan + flowchart](./Content/2026-07-06-14-21-peeves-validation-nonpartitioned-level-plan-flowchart.md) ·
[Peeves validation message review (to David)](./Content/2026-07-08-15-46-peeves-nonpartitioned-level-validation-message-review.md)

---

## 5. Perforce changelist reporting & validation

- **Changelist → PDF reports**: from a set of submitted + pending changelists, generate a PDF listing
  impacted level paths and impacted assets, sorted by date and CL number, most recent first, grouped
  as *Dungeons* / *Missions* / *LV_Overland* (with sub-categories), preceded by a work summary.
- **Changelist validation failures**: `WorldPartitionChangelistValidator` errors such as *"both actors
  are using a different set of runtime data layers"* when referenced actors are split across
  changelists; strategy of submitting the large CL first and moving the few problematic actors to a
  smaller CL.
- **SSK / UserEdits** validation errors decoded (missing `AutoDbAuthoring` / UserEdits SQL for actors).

Key sessions:
[Changelists → PDF (impacted levels & assets)](./Content/2026-07-08-10-18-perforce-changelists-pdf-impacted-levels-assets.md) ·
[Single CL 1959854 → PDF](./Content/2026-07-08-10-14-perforce-changelist-1959854-pdf-levels-assets.md) ·
[CL validation — runtime data layers / referenced actors](./Content/2026-07-06-17-40-changelist-validation-runtime-datalayers-referenced-actors.md) ·
[SSK / UserEdits validation error explained](./Content/2026-07-02-13-42-ssk-useredits-validation-error-explanation.md)

---

## 6. Log-parsing & reporting utilities

Repeated need to turn raw editor logs into actionable lists:

- Extract the **unique Levels (+ occurrence counts)** referenced by `HLODLayerWarnings*.txt` and by
  the "levels left to convert" logs.
- Turn an editor **Map-Check** export into a structured report.

Key sessions:
[Unique levels — Monday log](./Content/2026-07-06-10-13-unique-levels-hlod-warnings-monday-log.md) ·
[Unique levels — Tuesday log](./Content/2026-07-07-08-53-unique-levels-hlod-warnings-tuesday-log.md) ·
[Unique levels — Thursday log](./Content/2026-07-02-09-07-unique-levels-count-from-hlod-warnings-log.md) ·
[Unique levels — convert list](./Content/2026-06-30-13-30-unique-levels-from-convert-list-log.md) ·
[Map-Check editor report](./Content/2026-07-09-08-30-mapchecks-editor-report.md)

---

## 7. Knowledge capture & workflow tooling

- **Video transcriptions + point-by-point summaries** of colleague (Phil / William) explanations about
  HLOD, `IncludeInHLOD`, World Partition rules, and status updates — used to translate verbal domain
  knowledge into actionable notes.
- **Miro**: connecting the plugin, building an English board with side-by-side diagram + text per
  solution for the RuntimeGrid/DataLayer conflict.
- **OneNote**: consolidating a topic-by-topic recap of the essential knowledge gathered across sessions.
- **Batch `.bat`** to run the World Partition Rule Builder per Level Instance; documented in an English
  README and committed to `D:\CustomGitRepos`.
- **UnrealFest 2026** notes synthesized (own notes + a colleague's Confluence page).
- Guidance on improving the workflow with **Cursor AI Skills**.

Key sessions:
[Video — IncludeInHLOD action items](./Content/2026-06-29-16-26-video-transcript-includeinhlod-action-items.md) ·
[Video — HLOD talk (Phil & William)](./Content/2026-06-30-15-18-video-transcript-hlod-talk-phil-william.md) ·
[Video — Phil status](./Content/2026-07-08-08-44-video-transcript-phil-status.md) ·
[Video — status: level WP / HLOD warnings](./Content/2026-07-06-09-40-video-summary-phil-status-level-wp-hlod-warnings.md) ·
[Video — HLOD warnings, final check](./Content/2026-07-06-16-45-video-summary-phil-status-hlod-warnings-final.md) ·
[Knowledge recap → OneNote](./Content/2026-07-07-11-10-knowledge-recap-export-to-onenote.md) ·
[Miro plugin usage & board invite](./Content/2026-07-07-11-03-miro-plugin-usage-and-board-invite.md) ·
[Batch .bat + README + commit](./Content/2026-07-06-15-08-batch-bat-process-level-instances-readme-commit.md) ·
[UnrealFest 2026 notes synthesis](./Content/2026-06-22-15-08-unrealfest-2026-notes-synthesis-confluence.md) ·
[Improve workflow with Cursor AI Skills](./Content/2026-06-29-16-36-improve-workflow-with-cursor-ai-skills.md)

---

## 8. Unrelated / one-off tasks

Smaller, self-contained requests not tied to the World Partition effort:

- [Fix `DataLayer 'DL_M_VAR_01' doesn't exist` map-check warning](./Content/2026-06-10-09-45-fix-datalayer-does-not-exist-mapcheck-warning.md)
- [Mutator: add a condition to detect a specific Merlin dungeon asset](./Content/2026-06-10-13-56-mutator-add-condition-detect-merlin-dungeon-asset.md)
- [Replace `GetActorFolderDesc` with `GetPath` in the ActorFolders builder](./Content/2026-05-26-13-08-replace-getactorfolderdesc-with-getpath.md)
- [Periodically re-save `ActorFolder` actors (UE5)](./Content/2026-05-04-14-59-resave-actorfolder-actors-ue5.md)
- [Transcribe handwritten notes (JPG → Markdown)](./Content/2026-06-22-13-25-transcribe-handwritten-notes-jpg-to-markdown.md)
- [Date photos from EXIF and rename to .jpg](./Content/2026-06-22-14-21-date-photos-from-exif-rename-jpg.md)
- [Trim the last seconds of a video](./Content/2026-07-08-14-16-trim-last-seconds-of-video.md)
- [Replace the Ubisoft logo with WB Games Montreal](./Content/2026-05-13-15-08-replace-ubisoft-logo-with-wb-games-montreal.md)
- [GameLift Server SDK minimum version for Amazon Linux 2023](./Content/2026-05-29-13-19-gamelift-server-sdk-min-version-amazon-linux-2023.md)
- [Git: pulling the TurnServer branch](./Content/2026-06-01-14-15-git-commands-pull-turnserver-branch.md)
- [WSL2: clone & work on the TURN server repo (SSH / PAT)](./Content/2026-05-07-14-15-wsl2-clone-turn-server-git-repo-ssh-pat.md)
- [Miro access check](./Content/2026-07-07-10-44-miro-access-check.md)
- [Quick help request](./Content/2026-07-07-16-33-quick-help-request.md)

---

## 9. Glossary

- **HLOD / HLODLayer** — Hierarchical Level of Detail and the layer asset that governs it
  (e.g. `LV_Overland_HLODLayer_Near`).
- **World Partition (WP)** — UE5's grid-based streaming system; levels can be partitioned or not.
- **Level Instance** — a Level embedded as an actor inside another Level; can be partitioned or
  non-partitioned and can nest.
- **OFPA (One File Per Actor)** — actors stored as individual files under `__ExternalActors__`.
  Non-partitioned Level Instance inner actors are instead stored inside the sub-world `.umap`.
- **RuntimeGrid / DataLayer** — partition placement and data-layer membership; `SmallGrid`,
  `HogsmeadeGrid` are runtime grids.
- **Mutator / RuleBuilder** — `AvaStreamingGenerationMutator` applies runtime-grid rules
  (`DA_SmallGrid_Rules`); `WorldPartitionRuleBuilder` re-applies HLOD/DataLayer/RuntimeGrid rules.
- **Peeves** — the studio's pre-submit validation system.
- **SSK / UserEdits / AutoDbAuthoring** — changelist/authoring validation layer.
- **Map Check** — the editor's validation pass that surfaces the warnings this work targets.

---

*Generated from the agent transcript archive. Individual sessions are available in [`Content/`](./Content).*
