Parent: [Reference Docs](README.md)

# Environment & infrastructure

Cross-cutting environment, build-infra, and engine-format notes that surfaced during
the work but aren't specific to World Partition rules.

---

## Actor Folders — the format & the engine patches

Outliner folders in a WP level are backed by `UActorFolder` assets (under
`Content/__ExternalObjects__/…`). Three engine-level things matter:

1. **`ULevel::FixupActorFolders` was exposed publicly** (AVA patch, `arnaud.storq`) so
   external commandlets can call it instead of duplicating engine logic:

```1581:1586:D:\Sun\Engine\Source\Runtime\Engine\Classes\Engine\Level.h
// @third party code - AVA BEGIN [arnaud.storq] - Expose FixupActorFolders publicly so external commandlets can use it
public:
	/** Prepares/fixes actor folder objects once level is fully loaded. */
	ENGINE_API void FixupActorFolders();
private:
// @third party code - AVA END [arnaud.storq] - Expose FixupActorFolders publicly so external commandlets can use it
```

2. **Ghost `UActorFolder` creation was stopped** (engine `WorldFolders.cpp`): the
   world-folders rebuild used to spawn a *second* `UActorFolder` asset when the folder's
   logical owner level differed from its physical storage level — a "ghost" with no
   serialized counterpart. The rebuild now skips that entry (`WorldFolders.cpp:132`).

3. **Folder path is read via `FActorFolderDesc::GetPath()`** (walks parent descs),
   used by the fixup builder's `BuildFolderPath` rather than manually iterating
   `FActorFolderDescsContext::GetActorFolderDesc`. (Both APIs still exist in
   `ActorFolderDesc.cpp`; the high-level one is preferred.)

`UActorFolder` assets are also **periodically resaved** to bring stale packages to the
current serialization version (many were left dirty after Outliner renames — the "699
child folders" cleanup). See [builders & commandlets](BuildersAndCommandlets.md) for
`UWorldPartitionFixupActorFoldersBuilder`.

---

## Related changelists

- [Expose `ULevel::FixupActorFolders` (CL 1896115)](../WorkDoneByChangelists/P4-History/2026-05-26-14-39-expose-fixupactorfolders.md)
- [Stop ghost `UActorFolder` assets (CL 1890839)](../WorkDoneByChangelists/P4-History/2026-05-22-09-04-stop-ghost-actorfolder-assets.md)
- [Fix orphan/duplicate Actor Folders (CL 1901233)](../WorkDoneByChangelists/P4-History/2026-05-29-07-49-fix-orphan-duplicate-actor-folders.md)
- [Resave child ActorFolders (CL 1770358)](../WorkDoneByChangelists/P4-History/2026-03-24-07-39-resave-child-actorfolders.md)
- [Resave many Actor Folders (CL 1822824)](../WorkDoneByChangelists/P4-History/2026-04-09-11-21-resave-actor-folders.md)

## See also

- [Builders & commandlets](BuildersAndCommandlets.md)
- Plain-language: [`WorkDoneByTopic/ActorFolders.md`](../WorkDoneByTopic/ActorFolders.md)
