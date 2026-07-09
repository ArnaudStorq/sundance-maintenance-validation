Parent: [Reference Docs](README.md)

# Level Instances & OFPA

A **Level Instance** (`ALevelInstance`) places the contents of another level (a
`.umap`) into a parent world at a transform. `LV_Overland` is a deep tree of nested
Level Instances. Whether an instance is *partitioned* decides where its inner actors
are stored and whether they can be given per-actor streaming properties.

---

## Partitioned vs non-partitioned

| | Partitioned Level Instance | Non-partitioned Level Instance |
|-|----------------------------|--------------------------------|
| Inner actor storage | OFPA packages under `Content/__ExternalActors__/…` | Inside the sub-world `.umap` asset itself |
| Per-actor streaming settings | **Yes** — each actor can have its own RuntimeGrid / HLODLayer / DataLayers | **No** — inner actors inherit from the parent |
| Detection API | `PersistentLevel->bIsPartitioned == true` | `bIsPartitioned == false` |
| Checkout granularity | one `.uasset` per actor | the whole `.umap` |

Detection helpers actually used in the code:

| API | Where |
|-----|-------|
| `PersistentLevel->bIsPartitioned` | fixup builder walk, resave builder |
| `ULevel::GetIsLevelPartitionedFromPackage(FName)` | `ULevelInstanceFunctionLibrary::GetNonPartitionedLevelInstances` |
| `ULevel::GetIsLevelUsingExternalActorsFromPackage(FName)` | OFPA branch of the same |
| `AWorldSettings::IsPartitionedWorld()` | Outliner "Non-Partitioned Parent" column util |

The classification check in the fixup builder:

```388:396:D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp
			const bool bIsRoot = CurrentLevelPackageName.IsNone();
			if (!bIsRoot && !PersistentLevel->bIsPartitioned)
			{
				const FSoftObjectPath LevelAssetPath = MakeLevelAssetPath(CurrentLevelPackageName);
				NonPartitionedLevels.Add(LevelAssetPath);
				NonPartitionedLevelPackages.Add(CurrentLevelPackageName);
```

---

## OFPA (One File Per Actor)

With OFPA, each actor lives in its **own** `.uasset` under `__ExternalActors__`, so
checkout/save happens per actor and many people can edit the same level without
colliding. Outliner **folders** are also externalized as `UActorFolder` packages under
`__ExternalObjects__` (see [environment & infrastructure](EnvironmentAndInfra.md)).

Practical consequences:

- Moving an actor into a folder **rewrites files on disk** → large changelists.
- A partitioned Level Instance's actors can be resaved individually
  (`Actor->GetExternalPackage()`), which the fixup builder does when
  `-SaveActorPackages` is set:

```814:838:D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp
	if (BuildOptions.bSaveActorPackages && !ActorsToFix.IsEmpty())
	{
		UPackage* ActorPackage = Actor->GetExternalPackage();
		if (!ActorPackage) { ActorPackage = Actor->GetPackage(); }
		if (!ActorPackage || ActorPackage == LevelPackagePtr) { continue; }
		ActorPackagesToSave.Add(ActorPackage);
```

- **Non-OFPA levels**: there is no external actor file; you scan
  `WorldAsset->PersistentLevel->Actors` after loading the `UWorld`.

---

## The `Level` property of an `ALevelInstance`

In the Details panel it is labelled **Level**; in code it is the `WorldAsset`
(`TSoftObjectPtr<UWorld>`). Read it depending on context:

| Context | API |
|---------|-----|
| Loaded actor | `LevelInstance->GetWorldAsset()` / `GetWorldAssetPackage()` |
| From a partitioned parent's actor descriptor (no instantiation) | `ActorDescInstance->GetChildContainerPackage()` |

```477:479:D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp
				// GetWorldAsset() returns the exact TSoftObjectPtr<UWorld> stored in the LI's "Level" property.
				const FName ChildPackage = *NestedLI->GetWorldAssetPackage();
```

> Note: `RuntimeGrid` and `HLODLayer` on an `ALevelInstance` are sometimes **hidden**
> in the Details UI, but they are real `AActor` properties and can be read/written in
> code exactly like any other actor (the fixup builder's Phase 3 does this on the
> parent instance).

---

## Traversing the hierarchy recursively from `LV_Overland`

There are several traversal strategies in the codebase, chosen by cost:

1. **Descriptor walk (fast, no instantiation)** — when the parent is partitioned,
   iterate `ALevelInstance` descriptors and follow `GetChildContainerPackage()`
   without entering edit mode:

```399:420:D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp
			if (UWorldPartition* WorldPartition = CurrentWorld->GetWorldPartition())
			{
				FWorldPartitionHelpers::ForEachActorDescInstance(WorldPartition, ALevelInstance::StaticClass(),
					[&](const FWorldPartitionActorDescInstance* ActorDescInstance) -> bool
					{
						// IMPORTANT: do NOT filter on IsChildContainerInstance() here.
						const FName ChildPackage = ActorDescInstance->GetChildContainerPackage();
```

2. **Actor walk (slow path)** — when the parent is non-partitioned, iterate
   `PersistentLevel->Actors` and cast to `ALevelInstance` (`:467`).

3. **Edit-scope recursion** — builders that must *mutate* inner actors enter
   `FLevelInstanceEditScope` (edit → process → commit-with-discard), e.g.
   `UWorldPartitionResaveActorsRecursiveBuilder` and `UForceHLODExcludeFromLogBuilder`.

4. **`ULevelInstanceTraversalBuilder`** — an abstract base that enqueues every child
   container package in `PreRun` and, in `PostWorldTeardown`, loads each unique package
   and calls `RunBuilder(PackageWorld)` recursively
   (`LevelInstanceTraversalBuilder.cpp:137`).

Sub-levels are loaded dynamically on demand (`LoadPackage` → `FullyLoad` →
`FindWorldInPackage`) and memoized so each `.umap` is opened once.

### Listing what is still non-partitioned

`Editor.LogNonPartitionedLevelInstances` (→
`ULevelInstanceFunctionLibrary::LogNonPartitionedLevelInstances`) prints every
non-partitioned Level Instance with its Outliner path and label. This is the worklist
that drives the migration ([converting levels to World Partition](ConvertingLevelsToWorldPartition.md)).

```148:152:D:\Sun\Sundance\Source\WorldBuildingEditor\WorldBuildingEditorConsoleCommands.cpp
static FAutoConsoleCommand LogNonPartitionedLevelInstancesCmd(
	TEXT("Editor.LogNonPartitionedLevelInstances"),
	TEXT("Log all non-partitioned LevelInstances."),
	FConsoleCommandWithArgsDelegate::CreateStatic(&WorldBuildingEditor::LogNonPartitionedLevelInstances)
);
```

---

## Related changelists

- [Add `LogNonPartitionedLevelInstances` command (CL 1751748)](../WorkDoneByChangelists/P4-History/2026-03-06-08-06-add-lognonpartitioned-command.md)
- [Skip non-partitioned LI in RuleBuilder (CL 1727387)](../WorkDoneByChangelists/P4-History/2026-02-18-08-03-skip-nonpartitioned-li-rulebuilder.md)

## See also

- [Converting levels to World Partition](ConvertingLevelsToWorldPartition.md)
- [Builders & commandlets](BuildersAndCommandlets.md)
- Plain-language: [`WorkDoneByTopic/PartitionedStreaming.md`](../WorkDoneByTopic/PartitionedStreaming.md)
