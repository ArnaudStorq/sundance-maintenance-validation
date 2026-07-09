Parent: [Work Done By Topic](README.md)

# The Outliner Restructure

*A plain-language guide to the work done on the `LV_Overland` Outliner in 2026.*

---

## What is the Outliner? (the basics)

In Unreal Engine, the **World Outliner** is the panel that lists every actor placed
in a level, organized in a tree of **folders**. Think of it exactly like the file
explorer on your computer: folders inside folders, with items (actors) sitting in
them.

```
LV_Overland
├── Landscape
│   └── MerlinDungeon
├── Water
│   ├── Rivers
│   └── Lakes
├── Roads
└── #_TO_CLASSIFY   <- "I don't know where this goes yet"
```

Important detail for World Partition levels like `LV_Overland`: folders are **not**
just a cosmetic view. Each actor and each folder is stored on disk as its own tiny
file (an "external actor" or "external object" package, under
`Content/__ExternalActors__/…` and `Content/__ExternalObjects__/…`). So **moving an
actor into a folder actually rewrites files on disk**, which is why these changes
touch hundreds or thousands of packages at a time.

## Why did this work need to happen?

`LV_Overland` is the huge open world of the game. After years of production by many
teams, its Outliner had become a mess:

- Hundreds of **empty folders** left behind by deleted content.
- Actors dumped at the **root** with no category.
- Inconsistent naming (`Region Coast`, `LI_Hogsmeade`, `TO_CLASSIFY`, …).
- Temporary/debug junk mixed with real content (`AAA_Temp_Cylinders`,
  `Cameras_FORDELETE`).

A messy Outliner slows everyone down: designers can't find things, and it makes
World Partition rules (which often key off folder paths) unreliable. The goal was a
**clean, predictable, categorized folder structure**.

This effort is tracked mostly under Jira **SUNDANCE-41837** (and 41854).

## How the work was carried out

The restructure was done **incrementally**, in many small changelists, rather than
one giant risky commit. This is a deliberate strategy:

- Each step is easy to review and easy to revert.
- Perforce checkouts stay a manageable size.
- If something breaks the editor, you know exactly which step did it.

### 3a. Custom tooling first

Before moving anything, tooling was built to *see* and *measure* the structure:

- **Export the whole hierarchy** — a console command `Outliner.ExportAllHierarchy`
  plus a commandlet that dumps the full folder/actor tree to CSV and an HTML report.
  *Why:* you can't safely reorganize what you can't see. This let the structure be
  reviewed offline and planned with stakeholders.
- **New Outliner columns** — `OutlinerPath` and `IncludeInHLOD` (hidden by default).
  *Why:* to inspect, per actor, where it lives and whether it participates in HLOD,
  directly in the editor.

### 3b. Cleanup passes

1. **Delete empty folders.** Multiple passes removed empty folders — including one
   pass of **156 folders** and another of **442** at the root. (Example categories
   cleaned: `LIGHTING`, `RENDER_*`, `LevelInstances/*`, `Magical Creatures/*`.)
2. **Stage the unknowns.** A `TO_CLASSIFY` folder was created and all loose
   root-level actors were moved into it (in batches of ~40 to ~700 actors). It was
   then renamed `#_TO_CLASSIFY` — the `#_` prefix forces it to **sort first** so
   designers immediately see what still needs triage.
3. **Categorize.** Actors were moved into meaningful subfolders, for example:
   - `Water/Rivers`, `Water/Lakes`, `Water/RiverDressing`
   - `Landscape/MerlinDungeon/…`, `Landscape/RegionVolumes/…`
   - `Roads`, `Roads/DressingBlockout/…`
   - `PCG/ExclusionVolumes`, PCG grid actors → `PCG`
   - `Environment/Foliage`, `Environment/Blockout`, `Environment/Rocks`
   - `Nav` (Mercuna navigation assets), `Debug`, `WorldEvents`, `Automation`
4. **Normalize names.** e.g. `Region Coast → Region/Coast`, `LI_Hogsmeade → Hogsmeade`,
   `LI_Hogwarts → Hogwarts`, keeping Data Layer rules in sync with the new paths.

## Real examples from the work

**Example — renaming was risky.** Renaming the Hogsmeade folder was first attempted
in one changelist, but it **froze the editor** when loading `LV_Overland`. It was
reverted the same day, investigated, and re-done correctly a few days later — this
time also updating the associated **Data Layer rules** so nothing dangled.

> Takeaway: in a World Partition world, a folder rename can ripple into Data Layer
> rules and streaming. The safe recipe is *rename + update the rules that reference
> the old path + test load*.

**Example — one move, then undo minutes later.** `WaterBodyExclusionVolumes` were
moved into `Landscape`, then reverted ~4 minutes later because they logically belong
with `Water`. The history intentionally keeps both the move and its undo, so the
reasoning is traceable.

## The loose end that had to be cleaned up

Renaming/moving parent folders early in the year left **699 child `ActorFolder`
packages** that were never re-saved. The symptom: they showed up as "dirty" and
asked to be checked out **on every editor session**. A dedicated pass force-resaved
them so they stopped nagging everyone. (See also `ActorFolders.md`.)

## Cheat-sheet of the folder categories created

| Folder | Holds |
|--------|-------|
| `Environment/Foliage`, `/Blockout`, `/Rocks` | Environment static meshes by type |
| `Water/Rivers`, `/Lakes`, `/RiverDressing` | Water bodies and their dressing |
| `Landscape/…` | Landscape, region volumes, world bitmap |
| `Roads`, `Roads/DressingBlockout` | Road actors and blockouts |
| `PCG`, `PCG/ExclusionVolumes` | Procedural generation actors/volumes |
| `Nav` | Mercuna navigation data |
| `Debug` | Notes and debug helpers |
| `WorldEvents`, `Automation` | Gameplay/world-event and automation actors |
| `#_TO_CLASSIFY` | Not-yet-sorted actors (sorts to the top) |

## Related changelists

See `WorkDoneByChangelists/P4-History/` — files named `*outliner*`, `*to-classify*`,
`*landscape*`, `*hogsmeade*`, `*region*`, `*nav*`, `*add-outliner-columns*`,
`*export-hierarchy*`. Roughly 40 changelists contributed to this topic.

## See also
- `ActorFolders.md` — the folder *assets* behind the scenes.
- `WorldPartitionRules.md` — how folder paths feed streaming rules.
