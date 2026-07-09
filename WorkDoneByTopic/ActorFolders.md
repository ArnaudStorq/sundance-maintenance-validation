Parent: [Work Done By Topic](README.md)

# Actor Folders

*A plain-language guide to what Actor Folders are, the problems they caused, and the
tooling built to fix them in 2026.*

---

## What is an Actor Folder?

In a World Partition level, the Outliner folders you see (see `Outliner.md`) are not
just labels in the UI. Each folder is backed by a real asset on disk called a
**`UActorFolder`**, stored as a tiny package under
`Content/__ExternalObjects__/…`.

So there are two things:
- The **folder asset** (`UActorFolder`) — the folder itself.
- The **actors** that reference the folder to say "I live here".

This design lets a huge world be edited by many people at once (each folder/actor is
its own file, so two people rarely touch the same file). But it also means the folder
*assets* can get out of sync with reality.

## The two problems

### Problem A — Orphaned and duplicated folders
Over time the level accumulated:
- **Orphans** — folder assets that no actor points to anymore (dead folders).
- **Duplicates** — two folder assets representing the same logical folder.

These cause confusing Outliner behavior and spurious checkouts.

### Problem B — "Ghost" folders being created
The engine's *world folders rebuild* was **spawning brand-new `UActorFolder` assets**
for Level Instance folders that shouldn't have existed — actively *feeding* the
orphan problem. This is a root-cause leak, not just accumulated cruft.

### Problem C — Stale folders nagging everyone
When parent folders were renamed/moved during the Outliner restructure, their
**child folder packages were not re-saved**. Result: they appeared **dirty on every
editor session**, constantly asking to be checked out.

## How each problem was solved

### Fix the leak at the source (engine)
The engine's `WorldFolders.cpp` was changed so the world-folders rebuild **no longer
creates ghost `UActorFolder` assets** for Level Instance actor folders. Stopping the
leak means the cleanup won't just refill later.

> This was an **engine-level** change (on the `Dev-Engine` branch), i.e. a fix in
> Unreal itself, approved by an engine owner.

### Build a repeatable repair tool
Instead of hand-cleaning thousands of folders, a dedicated builder was written:
**`UWorldPartitionFixupActorFoldersBuilder`**. It:

1. Uses the **Asset Registry** to *detect* orphaned and duplicated Actor Folders.
2. Repairs them by calling the engine's own `ULevel::FixupActorFolders` and saving
   the changed packages — i.e. **exactly the same fix a user gets in the editor**,
   just automated and unattended.
3. Offers a **report-only mode** (`-bReportOnly`) and logs the "top offenders" for
   diagnostics.

To make the builder possible, one small engine change was needed first: the method
`ULevel::FixupActorFolders` was **exposed publicly** so an external commandlet could
call it (rather than duplicating engine logic).

Example invocation used on the real world:
```
-run=WorldPartitionBuilderCommandlet
-Builder=WorldPartitionFixupActorFoldersBuilder
-SCCProvider=Perforce -Unattended
-bDuplicates -bOrphans -NoShaderCompile
LV_Overland
```

### Clean up the stale folders
- A pass **force-resaved 699 child `ActorFolder` packages** left over from the
  restructure renames, so they stopped nagging on every session.
- A broader pass **resaved many Actor Folder assets** to bring them to the current
  format.

## Why build a commandlet instead of clicking in the editor?

- **Scale:** thousands of folders across a massive world — manual is impractical.
- **Safety:** report-only mode lets you preview before changing anything.
- **Repeatability:** it can be re-run any time (e.g. on CI) and produces an auditable
  log.
- **Correctness:** by calling the engine's own `FixupActorFolders`, the result is
  identical to the editor's behavior — no risk of a divergent custom implementation.

## The order of operations (why it matters)

```
1. Expose ULevel::FixupActorFolders        (engine: enable reuse)
2. Add the FixupActorFolders builder        (tool: detect + repair)
3. Run it on LV_Overland                     (fix existing orphans/duplicates)
4. Stop ghost folder creation (engine)       (prevent the problem returning)
5. Resave stale child folders                (silence per-session checkouts)
```
Fixing the existing mess *and* stopping the source is what makes the fix stick.

## Related changelists

In `WorkDoneByChangelists/P4-History/`: `*expose-fixupactorfolders*`,
`*add-fixup-actorfolders-builder*`, `*fix-orphan-duplicate-actor-folders*`,
`*stop-ghost-actorfolder-assets*`, `*resave-child-actorfolders*`,
`*resave-actor-folders*`.

Jira: **SUNDANCE-41837**, **SUNDANCE-54425**.

## See also
- `Outliner.md` — the user-facing folders these assets back.
