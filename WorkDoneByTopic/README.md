# Work Summaries

Plain-language, example-driven explanations of the engineering work done on the
**Sundance** project in 2026 — the *what*, the *why*, and the *how*.

Where `WorkDoneByChangelists/P4-History/` is a factual, one-file-per-changelist log, **this folder
tells the story by topic**: it groups the ~80 changelists into themes and explains
each theme so that someone new to the project can understand it.

## How to read this folder

- Start here for the big picture.
- Jump to a topic file for a deep, beginner-friendly explanation.
- Each topic file ends with the matching changelist file-name patterns in
  `WorkDoneByChangelists/P4-History/`, so you can drill down to the exact commits.

## The topics

| Topic | What it covers | Start here if… |
|-------|----------------|----------------|
| [Outliner](Outliner.md) | Cleaning up and reorganizing the `LV_Overland` Outliner folder structure, plus the tooling built for it | you want to understand the level's folder organization |
| [World Partition Rules](WorldPartitionRules.md) | The rule system that assigns streaming grids/HLOD to actors, and the fixes to its builder | you want to understand how actors get their streaming settings |
| [Partitioned Streaming](PartitionedStreaming.md) | Converting non-partitioned levels so their actors can be streamed and rule-managed | you're wondering what "partitioned streaming support" means |
| [Actor Folders](ActorFolders.md) | The folder *assets* behind the Outliner, and the tooling to fix orphaned/duplicated/ghost folders | you hit dirty folders or spurious checkouts |
| [HLOD](HLOD.md) | Hierarchical Level of Detail layers and the MapCheck warning cleanup | you see "invalid HLOD layer" warnings |
| [Scriptable Tools](ScriptableTools.md) | Robustness fix in the custom editor-tools mode | you work on custom editor tools |
| [World Events](WorldEvents.md) | Safe editing of Possible World Events + a Python warning fix | you touch the World Events system |
| [Editor Stability & Warnings](EditorStabilityAndWarnings.md) | Crash fixes, startup-warning cleanups, and small robustness improvements | you want the "misc but important" fixes |

## The one-paragraph summary

Most of 2026 was a large, careful **cleanup and hardening of `LV_Overland`** and the
World Partition pipeline. The Outliner was reorganized into a clean folder structure;
the machinery that backs those folders (Actor Folders) was repaired and its leaks
stopped; the World Partition rule builder was fixed after a bad automated run drifted
actor transforms, then non-partitioned levels were migrated to partitioned streaming
so their actors could get correct streaming/HLOD settings; hundreds of HLOD/MapCheck
warnings were cleared; and a steady stream of crash fixes and startup-warning
cleanups kept the editor healthy.

## Recurring engineering principles (visible across every topic)

1. **Work in small, reversible steps.** Big changes were split into many changelists;
   several were reverted and re-landed cleanly rather than hot-patched.
2. **Build tooling before mass edits.** Export/inspect first (hierarchy export, new
   Outliner columns, `LogNonPartitionedLevelInstances`, report-only modes).
3. **Fix the mess *and* the source.** e.g. repair orphaned Actor Folders *and* stop
   the engine from creating ghost ones.
4. **Reuse engine behavior.** Expose and call the engine's own routines instead of
   duplicating logic, so results match the editor exactly.
5. **Keep the signal clean.** Remove startup warnings so real problems are visible.

## Provenance

Derived from `WorkDoneByChangelists/P4-History/` (generated from `p4 changes` / `p4 describe` of
all non-ROBOMERGE changelists submitted since 2026-01-01). Written 2026-07-09.
