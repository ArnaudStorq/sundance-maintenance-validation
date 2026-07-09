Parent: [Reference Docs](README.md)

# Converting a non-partitioned level to World Partition

To give a Level Instance's inner actors their own streaming properties, the level must
first be partitioned. This is the "open the box" step; applying rules
([World Partition rules](WorldPartitionRules.md)) is the "label each item" step.

---

## The manual paths (editor UI)

- **Tools → Convert Level** (opens the Convert Settings dialog).
- **Right-click a level asset → Add Partitioned Streaming Support**, or
  **Setup Level Instance for World Partition**.
- The **In Place** option overwrites the source `.umap` (no `_WP` suffix map).

The engine entry point is `FWorldPartitionEditorModule::ConvertMap`
(`D:\Sun\Engine\Source\Editor\WorldPartitionEditor\Private\WorldPartitionEditorModule.cpp:763`).
It shows a modal `SWorldPartitionConvertDialog`, asks to save dirty packages, unloads
the map, then runs `UWorldPartitionConvertCommandlet` as an external process.

Default `bInPlace = false` → produces a `_WP` map unless the user changes the option.

---

## The headless / batch path (built for this project)

Converting ~100 levels through the UI means ~100 modal Convert Settings dialogs plus
save prompts. To avoid that, the team added a Blueprint-callable headless converter in
the **EditorImprovements** plugin:

```28:29:D:\Sun\Sundance\Plugins\EditorImprovements\Source\WEditorImprovements\Public\BlueprintFunctionLibrary\WEditorImprovementsBlueprintFunctionLibrary.h
	UFUNCTION(BlueprintCallable, Category = "WEditorImprovements|WorldPartition")
	static int32 ConvertLevelsToWorldPartition(const TArray<FAssetData>& SelectedAssets, const FString& LogFilePath);
```

It launches a **child editor process per map** with no dialog, mirroring
`FWorldPartitionEditorModule::RunCommandletAsExternalProcess` +
`UWorldPartitionConvertOptions::ToCommandletArgs()`, defaulting **In Place = true**:

```72:74:D:\Sun\Sundance\Plugins\EditorImprovements\Source\WEditorImprovements\Private\BlueprintFunctionLibrary\WEditorImprovementsBlueprintFunctionLibrary.cpp
		const FString CommandletArgs = FString::Printf(
			TEXT("-run=WorldPartitionConvertCommandlet %s -AllowCommandletRendering -FoliageTypePath=/Game/FoliageTypes"),
			*LongPackageName);
```

- Child-process flags include `-Unattended`, `-RunningFromUnrealEd`, `-NoZenLoader`,
  `-AbsLog=...`.
- **The convert commandlet does its own Perforce checkout/add** of the affected
  packages (`WorldPartitionConvertCommandlet.cpp:1539`) — no separate `-SCCProvider`
  needed on this path.
- If `LogFilePath` is provided, only levels whose package appears in lines matching the
  token `in level '` are converted (drive the batch from a warnings log).

---

## The Nanite crash gotcha (important)

Running conversion headless can crash during a **cold Nanite build** of a Nanite
Assembly skeletal mesh (e.g. `SK_HardFern_*_Nanite`): the assembly part source LODs
aren't resolvable in the headless/no-assets context and `SkeletalMeshBuilder` asserts
on an `LODModels.IsValidIndex` check.

Conversion only **loads + re-saves** the level and its external actors — the referenced
meshes are **not** in the packages being saved — so Nanite assembly support can be
turned off in the child process without affecting the result. Both cvars matter
(`NaniteAssembliesSupported() == (r.Nanite.Foliage || r.Nanite.AllowAssemblies)`):

```99:100:D:\Sun\Sundance\Plugins\EditorImprovements\Source\WEditorImprovements\Private\BlueprintFunctionLibrary\WEditorImprovementsBlueprintFunctionLibrary.cpp
		Arguments += TEXT(" -ini:Engine:[/Script/Engine.RendererSettings]:r.Nanite.AllowAssemblies=0");
		Arguments += TEXT(" -ini:Engine:[/Script/Engine.RendererSettings]:r.Nanite.Foliage=0");
```

Passed as `-ini:Engine:[/Script/Engine.RendererSettings]:<cvar>=0` so the value is 0 by
the time the first skeletal-mesh build runs. With assemblies unsupported,
`BuildNaniteAssemblyData` bails with a warning instead of crashing.

---

## Rollout & practical notes

- Conversions were done in **batches** to keep changelists and checkouts sane. Sizes
  seen in history: **88 levels** (~1,400 files, mostly adds), then 6, 6, 4, 1–2.
- A level **already converted** reprocesses much faster the second time.
- Migration is always **two changelists in spirit**: (1) enable partitioned streaming
  (adds external-actor packages), (2) apply WP rules to the now-exposed actors (edits
  packages).
- The worklist of what still needs converting comes from
  `Editor.LogNonPartitionedLevelInstances` ([Level Instances & OFPA](LevelInstancesAndOFPA.md)).
- Post-conversion, `FixupActorFolders` can dirty folder packages — hence the Actor
  Folders cleanup ([environment & infrastructure](EnvironmentAndInfra.md)).

---

## Related changelists

- [Partitioned streaming — 88 levels (CL 1946247)](../WorkDoneByChangelists/P4-History/2026-06-26-15-57-partitioned-streaming-88-levels.md)
- [Partitioned streaming — 6 levels (CL 1949614)](../WorkDoneByChangelists/P4-History/2026-06-29-15-10-partitioned-streaming-6-levels.md)
- [Partitioned streaming — 6 levels (CL 1957917)](../WorkDoneByChangelists/P4-History/2026-07-06-09-52-partitioned-streaming-6-levels.md)
- [Partitioned streaming — 4 levels (CL 1954875)](../WorkDoneByChangelists/P4-History/2026-07-02-11-52-partitioned-streaming-4-levels.md)
- [Partitioned streaming — 1 level (CL 1958172)](../WorkDoneByChangelists/P4-History/2026-07-06-12-12-partitioned-streaming-1-level.md)
- [Apply WP rules to Level Instances (CL 1959005)](../WorkDoneByChangelists/P4-History/2026-07-06-16-12-wp-rules-level-instances.md)

## See also

- [World Partition rules](WorldPartitionRules.md) (step 2)
- Plain-language: [`WorkDoneByTopic/PartitionedStreaming.md`](../WorkDoneByTopic/PartitionedStreaming.md)
