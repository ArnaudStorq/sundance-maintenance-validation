# World Partition builders & commandlets — full catalog

A complete, programmer-facing reference for **every** builder and commandlet available to
process World Partition worlds in this project (Unreal Engine 5.7, WB Games Montréal),
covering both **engine** classes (Epic, some `@third party code - AVA` patched) and the
project's **custom** classes in the `WorldBuildingEditor` module.

This document is the wide catalog. For the narrower, task-focused write-up of the four/five
maintenance builders used on `LV_Overland`, see
[builders & commandlets](BuildersAndCommandlets.md).

- Engine builders: `D:\Sun\Engine\Source\Editor\UnrealEd\Public\WorldPartition\`
- Engine commandlets: `D:\Sun\Engine\Source\Editor\UnrealEd\Classes\Commandlets\`
- Custom builders: `D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\`

---

## 1. Architecture

There are two distinct things that people loosely call "commandlets":

1. **Commandlets** (`UCommandlet` subclasses) — top-level entry points invoked with
   `-run=<CommandletName>`. Each has its own `Main(const FString& Params)`.
2. **Builders** (`UWorldPartitionBuilder` subclasses) — *not* commandlets. They are driven
   by the generic `UWorldPartitionBuilderCommandlet` and selected with `-Builder=<Name>`.

So `WorldPartitionBuilderCommandlet` is the **host**; builders are **plugins** it loads and
runs against one world.

### 1.1 `UWorldPartitionBuilder` base class

`D:\Sun\Engine\Source\Editor\UnrealEd\Public\WorldPartition\WorldPartitionBuilder.h`

```39:60:D:\Sun\Engine\Source\Editor\UnrealEd\Public\WorldPartition\WorldPartitionBuilder.h
UCLASS(Abstract, Config=Engine, MinimalAPI)
class UWorldPartitionBuilder : public UObject
{
	GENERATED_UCLASS_BODY()

public:
	enum ELoadingMode
	{
		Custom,
		EntireWorld,
		IterativeCells,
		IterativeCells2D,
	};
```

**Loading mode** (`GetLoadingMode()`) controls how the host loads actors before calling the
builder:

| Mode | Behaviour |
|------|-----------|
| `Custom` | Builder loads/streams actors itself (most maintenance builders). `RunInternal` is called once. |
| `EntireWorld` | Host loads the whole world into memory, then calls `RunInternal` once. |
| `IterativeCells` | Host walks the world in 3D cells of `IterativeCellSize` (default `102400`), calls `RunInternal` per cell — bounds memory. |
| `IterativeCells2D` | Same but 2D (X/Y) columns — used by minimap/navigation. |

**Lifecycle hooks** (override points, called in this order by `RunBuilder` → `Run`):

1. `PreWorldInitialization(World, Helper)`
2. `PreRun(World, Helper)`
3. `RunInternal(World, CellInfo, Helper)` — once for `Custom`/`EntireWorld`, per cell otherwise (**pure virtual**, the actual work)
4. `PostRun(World, Helper, bRunSuccess)`
5. `PostWorldTeardown(Helper)`

Other override points: `RequiresCommandletRendering()`, `CanProcessNonPartitionedWorlds()`
(default `false`), `ShouldProcessWorld()`, `ShouldProcessAdditionalWorlds()`,
`ShouldSkipCell()`, `GetWorldInitializationValues()`.

**Argument access** (inside a builder): `HasParam("Foo")`, `GetParamValue("Foo=", Value)`,
`GetBuilderArgs()`. Args are injected via `FWorldPartitionBuilderArgsScope` from the whole
command line, so builders read their own switches directly.

**Data-layer loading** (common to all builders): `LoadDataLayers()` honours
`IncludedDataLayers` / `ExcludedDataLayers`, `bLoadNonDynamicDataLayers`,
`bIncludeInitiallyActivatedRuntimeDataLayers`, `bExcludeNonInitiallyActivatedRuntimeDataLayers`.

**Source control / saving**: static helpers `SavePackages()`, `DeletePackages()` take a
`FPackageSourceControlHelper` and do the P4 checkout/add/delete. `OnFilesModified()` /
`OnPackagesModified()` feed the commandlet's auto-submit path.

> ⚠ AVA patch: `Run()` was made `virtual` and `FCellInfo` got `UNREALED_API` so custom
> builders can override the run loop and construct cell info — see the
> `@third party code - AVA` markers at lines 16-18 and 58-60 of the header.

### 1.2 `UWorldPartitionBuilderCommandlet` (the host)

`D:\Sun\Engine\Source\Editor\UnrealEd\Classes\Commandlets\WorldPartitionBuilderCommandlet.h`

Its `Main()` resolves the builder UClass from `-Builder=`, gathers the map(s), and calls
`RunBuilder()` per world. Commandlet-level switches (parsed in `.cpp`):

| Switch | Effect |
|--------|--------|
| `-Builder=<ClassNameWithoutU>` | **required** — resolves via `FindFirstObject<UClass>` |
| `-AutoSubmit` | submit modified files to P4 after the run |
| `-AutoSubmitTags=<tags>` | tags appended to the submit description |
| `-StayPending` | *(AVA)* keep changes in a pending changelist, do not submit |
| `-Verbose` | verbose logging |
| `-RunningFromUnrealEd` | in-editor invocation flag |
| positional map token | exactly one: short name (`LV_Overland`), `/Game/...` path, collection, or `*` |

Common **engine/base** switches valid for any builder (handled by base/engine, not the host):

| Switch | Effect |
|--------|--------|
| `-AllowCommandletRendering` | **required** when `RequiresCommandletRendering()==true` (HLOD, minimap, RVT, landscape, static lighting) |
| `-IterativeCellSize=<n>` | override the iterative cell size |
| `-CellsPerGC=<n>` | force a GC every N cells |
| `-SCCProvider=Perforce` | override the ini SCC provider at startup |
| `-Unattended -NoShaderCompile` | pass-through engine switches used by every batch run |

### 1.3 Canonical invocation shape

```bat
UnrealEditor-Cmd.exe "D:\Sun\Sundance\Sundance.uproject" ^
  -run=WorldPartitionBuilderCommandlet ^
  -Builder=<BuilderClassNameWithoutU> ^
  -SCCProvider=Perforce ^
  -Unattended -NoShaderCompile ^
  <MapPackageOrShortName> <builder-specific switches>
```

---

## 2. Engine builders (`UWorldPartitionBuilder` subclasses)

Registration name for `-Builder=` is the class name **without the `U` prefix**.

| Builder | Loading mode | Rendering | Non-partitioned | Purpose |
|---------|-------------|-----------|-----------------|---------|
| `WorldPartitionHLODsBuilder` | Custom | **yes** | yes | build/setup/delete HLOD actors |
| `WorldPartitionNavigationDataBuilder` | IterativeCells2D | no | no | generate navmesh data actors |
| `WorldPartitionMiniMapBuilder` | IterativeCells2D | **yes** | no | render the world minimap texture |
| `WorldPartitionResaveActorsBuilder` | Custom | no | yes | resave/repair actor packages |
| `WorldPartitionFoliageBuilder` | Custom | no | no | re-grid instanced foliage |
| `WorldPartitionLandscapeBuilder` | (see cpp) | **yes** | — | landscape processing |
| `WorldPartitionLandscapeSplineMeshesBuilder` | Custom | no | — | bake spline meshes into partition actors |
| `WorldPartitionRuntimeVirtualTextureBuilder` | Custom | **yes** | yes | build Runtime Virtual Texture |
| `WorldPartitionStaticLightingBuilder` | (see cpp) | **yes** | — | build static lighting / VLM / lightmaps |
| `WorldPartitionRenameDuplicateBuilder` | Custom | no | — | rename or duplicate a WP world |

### 2.1 `WorldPartitionHLODsBuilder`

Full HLOD lifecycle. Step flags are combinable (`EHLODBuildStep` bit flags):

| Switch | Step |
|--------|------|
| `-SetupHLODs` | create/delete HLOD actors to populate the world |
| `-BuildHLODs` | build components / merged meshes |
| `-RebuildHLODs` | build + force rebuild (`bForceBuild`) |
| `-FinalizeHLODs` | gather distributed-build results, optionally submit |
| `-DeleteHLODs` | delete all HLOD actors |
| `-DumpStats` | print HLOD actor stats |

Distributed-build & control switches: `-DistributedBuild`, `-BuildManifest=<file>`,
`-BuilderIdx=<n>`, `-BuilderCount=<n>`, `-BuildHLODLayer=<name>`, `-BuildSingleHLOD=<name>`,
`-ResumeBuild=<index>`, `-ReportOnly`, `-ReuseParentBranchHLODs`.
AVA additions: `-AllowFailedSave`, `-AllowFailedWorkloadValidation`,
`-ModifyFilesWithoutCheckout`, `-ForceDistributeHLODs`.
`RequiresCommandletRendering()==true`, `CanProcessNonPartitionedWorlds()==true`.

### 2.2 `WorldPartitionNavigationDataBuilder`

`IterativeCells2D`, no rendering, `bCleanBuilderPackages` option. Generates navmesh data
per 2D cell (`GenerateNavigationData`), saving/deleting the nav-data actor packages and
tracking added/deleted packages for submit.

### 2.3 `WorldPartitionMiniMapBuilder`

`IterativeCells2D`, `RequiresCommandletRendering()==true`. Renders the world into an
`AWorldPartitionMiniMap` texture (`WorldUnitsPerPixel`, `MinimapImageSizeX/Y`,
`-DebugCapture`). Exposes an `OnWarmupTick` delegate so callers can pump rendering warmup.

### 2.4 `WorldPartitionResaveActorsBuilder`

The engine's general resave/repair tool. Example line in the header:
`ProjectName MapName -run=WorldPartitionBuilderCommandlet -SCCProvider=Perforce -Builder=WorldPartitionResaveActorsBuilder [-ActorClassName=StaticMeshActor] [-SwitchActorPackagingSchemeToReduced] [-ActorTags=(...)] [-ActorProperties=((P,V),...)]`

Options (UPROPERTY-backed): `-ActorClassName=`, `-ActorClassesFromFile=`, `-ReportOnly`,
`-ResaveDirtyActorDescsOnly`, `-DiffDirtyActorDescs`, `-SwitchActorPackagingSchemeToReduced`,
`-EnableActorFolders`, `-ResaveBlueprints`, `-ActorTags=(...)`, `-ActorProperties=(...)`.
AVA/philippe.st-jean additions: `-MinVerMajor/-MinVerMinor/-MinVerPatch`, `-SkipEngineContent`,
`-InvokeAvaSavePackageDelegates`, `-RecurseIntoLevelInstances`.
`CanProcessNonPartitionedWorlds()==true`. This is the engine base for the project's custom
`WorldPartitionResaveActorsRecursiveBuilder` (§4.4).

### 2.5 `WorldPartitionFoliageBuilder`

Re-grids partitioned foliage. `-NewGridSize=<value>` (required for re-grid), `-Repair`
(`bRepair`) to fix up broken instances. `Custom` mode, no rendering.

### 2.6 `WorldPartitionLandscapeBuilder`

Landscape data processing; `RequiresCommandletRendering()` returns true (see cpp).
Header example: `... -Builder=WorldPartitionLandscapeBuilder -AllowCommandletRendering (-IterativeCellSize=Value)`.

### 2.7 `WorldPartitionLandscapeSplineMeshesBuilder`

Bakes landscape-spline static meshes into `ALandscapeSplineMeshesActor` partition actors.
`-NewGridSize=<value>` optional. Also callable in-editor via
`RunOnInitializedWorld(World)` on an already-loaded world.

### 2.8 `WorldPartitionRuntimeVirtualTextureBuilder`

Builds RVT; `RequiresCommandletRendering()==true`, `CanProcessNonPartitionedWorlds()==true`.
Header example: `... -Builder=WorldPartitionRuntimeVirtualTextureBuilder -AllowCommandletRendering [-AutoSubmit]`.
Exposes `LoadRuntimeVirtualTextureActors()` to load contributing actors. Subclassed by the
project (§4.7).

### 2.9 `WorldPartitionStaticLightingBuilder`

Builds static lighting / Volumetric Lightmaps / lightmaps. Combinable step flags
(`EWPStaticLightingBuildStep`) parsed from `FCommandLine`:

| Switch | Step / effect |
|--------|---------------|
| `-Build` | build **and** finalize (`WPSL_Build | WPSL_Finalize`) |
| `-Finalize` | finalize only (VLM & lightmaps passes) |
| `-Submit` | submit results to source control |
| `-Delete` | delete all static lighting data for the map |
| `-BuildVLMOnly` | build only the Volumetric Lightmap |
| `-SinglePass` | force single pass |
| `-SaveAllDirtyPackages` | save all dirty packages |
| `-QualityLevel=<n>` | lighting build quality |
| `-MappingDirectory=<dir>` | mappings directory |

`RequiresCommandletRendering()==true`.

### 2.10 `WorldPartitionRenameDuplicateBuilder`

Renames or duplicates a WP world to a new package.
Header example: `... -Builder=WorldPartitionRenameDuplicateBuilder -NewPackage=NewPackage [-Rename]`.
Without `-Rename` it duplicates; with it, it renames.

---

## 3. Engine commandlets (not builders)

### 3.1 `WorldPartitionConvertCommandlet`

`-run=WorldPartitionConvertCommandlet` — converts a **non-partitioned** level (with
streaming sub-levels) into a World Partition world. It creates the `UWorldPartition`,
merges sub-levels, sets up HLOD layers/minimap, remaps soft-object paths, and optionally
generates an ini. Key switches / config: `-OnlyMergeSubLevels`, `-DeleteSourceLevels`,
`-GenerateIni`, `-ReportOnly`, `-Verbose`, `-ConversionSuffix`, `-DisableStreaming`;
config-driven `EditorHashClass`, `RuntimeHashClass`, `ExcludedLevels`, `WorldOrigin/Extent`,
`DefaultHLODLayerAsset`, `LandscapeGridSize`, `DataLayerAssetFolder`. Subclassable via
`ReadAdditionalTokensAndSwitches`, `ShouldDeleteActor`, `PerformAdditionalActorChanges`, etc.
See [converting levels to World Partition](ConvertingLevelsToWorldPartition.md).

### 3.2 `WorldPartitionDataLayerToAssetCommandlet` (`DataLayerToAssetCommandlet`)

`-run=DataLayerToAssetCommandlet <Level> -DestinationFolder=<Folder>` — migrates legacy
(deprecated) data layers into `UDataLayerAsset` + `UDataLayerInstanceWithAsset`, and remaps
all actors to reference the new assets. Switches: `-DestinationFolder=` (required),
`-NoSave`, `-IgnoreActorLoadingErrors`, `-Verbose`. Return codes in
`UDataLayerToAssetCommandlet::EReturnCode`. Subclass and override
`PerformAdditionalActorConversions` / `PerformProjectSpecificConversions` for project
extras.

---

## 4. Custom builders (`WorldBuildingEditor` module)

These are the WB Games / AVA builders written for the Sundance maintenance work.

| Builder | `-Builder=` value | Purpose |
|---------|-------------------|---------|
| `UWorldPartitionRuleBuilder` | `WorldPartitionRuleBuilder` | apply DataLayer/HLOD/RuntimeGrid rules |
| `UWorldPartitionFixupNonPartitionedActorsBuilder` | `WorldPartitionFixupNonPartitionedActorsBuilder` | clean streaming props off non-partitioned LI inner actors |
| `UWorldPartitionFixupActorFoldersBuilder` | `WorldPartitionFixupActorFoldersBuilder` | repair orphaned/duplicated `UActorFolder` assets |
| `UWorldPartitionResaveActorsRecursiveBuilder` | `WorldPartitionResaveActorsRecursiveBuilder` | recursively resave external actors/objects/folders |
| `UForceHLODExcludeFromLogBuilder` | `ForceHLODExcludeFromLogBuilder` | force-disable HLOD on actors listed in a log |
| `UWorldPartitionInvalidNativeClassBuilder` | `WorldPartitionInvalidNativeClassBuilder` | find unresolved native classes, propose CoreRedirects |
| `UWorldPartitionLandscapeProxyDataBuilder` | `WorldPartitionLandscapeProxyDataBuilder` | rebuild Landscape Proxy Nanite/GrassMaps/PhysicalMaterial |
| `UAvaWorldPartitionRuntimeVirtualTextureBuilder` | `AvaWorldPartitionRuntimeVirtualTextureBuilder` | RVT build with explicit data-layer loading |

### 4.1 `UWorldPartitionRuleBuilder`

Applies the World Partition rules (DataLayer / HLOD / RuntimeGrid) to actors and saves dirty
packages — the batch equivalent of the on-save rule reapplication. `Custom` loading mode.
Switches: `-DataLayerRules`, `-HLODLayerRules`, `-RuntimeGridRules` (each opt-in),
`-ContainOutlinerPathSubstrings=a,b`, `-DiscardOutlinerPathSubstrings=a,b`. **No `-DryRun`.**
Full detail in [builders & commandlets](BuildersAndCommandlets.md#uworldpartitionrulebuilder).

### 4.2 `UWorldPartitionFixupNonPartitionedActorsBuilder`

Cleans `HLODLayer` / `RuntimeGrid` / `DataLayers` off inner actors of **non-partitioned**
Level Instances (and optionally the parent `ALevelInstance` actors). Switches:
`-ForceResave`, `-SaveActorPackages`, `-SkipLevelPackage`, `-FixLevelInstanceActors`,
`-DryRun`. Three phases: discover → fix inner actors → (optional) fix LI actors. Writes a
dry-run report under `<ProjectSaved>/WorldBuildingEditor/`. Full detail in
[builders & commandlets](BuildersAndCommandlets.md).

### 4.3 `UWorldPartitionFixupActorFoldersBuilder`

Repairs orphaned/duplicated `UActorFolder` assets via `ULevel::FixupActorFolders()`.
Switches: `-bOrphans`, `-bDuplicates`, `-bReportOnly`. Full detail in
[builders & commandlets](BuildersAndCommandlets.md).

### 4.4 `UWorldPartitionResaveActorsRecursiveBuilder`

Recursively resaves `__ExternalActors__` (and optionally `__ExternalObjects__`) packages,
descending into Level Instances via an `FLevelInstanceEditScope`. Rich filtering
(`FBuildOptions`):

| Switch | Field | Logic |
|--------|-------|-------|
| `-IncludeOutlinerPathSubstrings=a,b` | `IncludeOutlinerPathSubstrings` | AND (all must match) |
| `-ExcludeOutlinerPathSubstrings=x,y` | `ExcludeOutlinerPathSubstrings` | OR (any excludes) |
| `-ActorClassNames=A,B` | `ActorClassNames` | OR |
| `-DataLayerNames=D1,D2` | `DataLayerNames` | OR |
| `-MinVerMajor/-MinVerMinor/-MinVerPatch` | version gate | resave only packages below min version |
| `-bReportOnly` | `bReportOnly` | detect only |
| `-bIncludeExternalObjects` | `bIncludeExternalObjects` | also process ActorFolder / DataLayerInstance under `__ExternalObjects__` |

Tracks per-category stats (`FResaveStats` for Actor / ActorFolder / DataLayerInstance,
including a version histogram). `PackagesToSave` is `UPROPERTY(Transient)`.
`CanProcessNonPartitionedWorlds()==true`. Derives conceptually from the engine
`WorldPartitionResaveActorsBuilder` (§2.4) but with recursion + rule-subsystem awareness.

### 4.5 `UForceHLODExcludeFromLogBuilder`

Parses a `HLODLayerWarnings_*.txt` log (`for actor '...' in level '...'`) and for each
matched actor sets `bEnableAutoLODGeneration = false` + `SetHLODLayer(nullptr)`. Switches:
`-DryRun`, `-Recurse`, `-LogFile=<path>`. Skips non-partitioned LI inner actors.

### 4.6 `UWorldPartitionInvalidNativeClassBuilder`

Scans WP levels for external actors whose **native class no longer resolves**, then proposes
`+ClassRedirects` lines for `DefaultEngine.ini [CoreRedirects]`. `Custom` mode,
`CanProcessNonPartitionedWorlds()==false`.

| Switch | Effect |
|--------|--------|
| *(none)* | log + write report under `Saved/InvalidNativeClasses/` |
| `-bApplyRedirects` | checkout and patch `DefaultEngine.ini` with the resolved redirects |
| `-bRepairDeletedActors` | delete external actor packages whose class is gone (DELETED only) |
| `-ReportPath=<path>` | override report location |
| `-IncludeOutlinerPathSubstrings=a,b` | scope in |
| `-ExcludeOutlinerPathSubstrings=x,y` | scope out |

Resolution status is `Resolved` / `Deleted` / `Ambiguous` (`EResolutionStatus`); it builds a
native-class short-name index to find rename candidates.

### 4.7 `UWorldPartitionLandscapeProxyDataBuilder`

Rebuilds **Landscape Proxy** data (Nanite by default; optionally GrassMaps and
PhysicalMaterial) for proxies with outdated data. `RequiresCommandletRendering()==true`,
`CanProcessNonPartitionedWorlds()==true`.

| Switch | Effect |
|--------|--------|
| `-ForceRebuild` | rebuild all proxies (Nanite + GrassMaps + PhysicalMaterial) regardless of state |
| `-BuildGrassMaps` | also rebuild GrassMaps |
| `-BuildPhysicalMaterial` | also rebuild PhysicalMaterial |
| `-ForceOnlyLoadIncludeDataLayer` | load only the `-IncludeDataLayers` layers |
| `-IncludeDataLayers="DL_1,...,DL_N"` | data layers to load |

Requires `-AllowCommandletRendering`.

### 4.8 `UAvaWorldPartitionRuntimeVirtualTextureBuilder`

Subclass of the engine `WorldPartitionRuntimeVirtualTextureBuilder` (§2.8) that loads a
chosen set of data layers before building. Switches: `-ForceLoadAllLayers`,
`-ForceOnlyLoadIncludeDataLayer`, `-IncludeDataLayers="..."`, `-ExcludeDataLayers="..."`,
plus the base `-AllowCommandletRendering [-AutoSubmit]`.

> Note: the module also contains custom **HLOD mesh builders** under
> `WorldPartition\HLOD\Builders\` (`FoliageHLODBuilder`, `FarFoliageHLODBuilder`,
> `SparseMergedHLODBuilder`, `HLODBuilderMeshMerge*`, `HLODBuilderFilteredInstancing`, …).
> Those are **`UHLODBuilder` subclasses** (how a single HLOD actor's geometry is generated),
> **not** `UWorldPartitionBuilder` commandlet builders, so they are not invoked with
> `-Builder=`. They are selected per-`UHLODLayer` and run *inside* the HLOD build step of
> §2.1. `LevelInstanceTraversalBuilder` is likewise a helper, not a commandlet builder.

---

## 5. Quick decision guide

| I want to… | Use |
|------------|-----|
| Convert a legacy streamed level to WP | `WorldPartitionConvertCommandlet` (§3.1) |
| Migrate deprecated data layers to assets | `DataLayerToAssetCommandlet` (§3.2) |
| Apply DataLayer/HLOD/Grid rules to actors | `WorldPartitionRuleBuilder` (§4.1) |
| Build / rebuild / delete HLODs | `WorldPartitionHLODsBuilder` (§2.1) |
| Render the world minimap | `WorldPartitionMiniMapBuilder` (§2.3) |
| Generate navmesh | `WorldPartitionNavigationDataBuilder` (§2.2) |
| Build RVT | `WorldPartitionRuntimeVirtualTextureBuilder` / `AvaWorldPartitionRuntimeVirtualTextureBuilder` (§2.8/§4.8) |
| Build static lighting / VLM | `WorldPartitionStaticLightingBuilder` (§2.9) |
| Re-grid foliage | `WorldPartitionFoliageBuilder` (§2.5) |
| Rebuild landscape proxy Nanite/grass/physmat | `WorldPartitionLandscapeProxyDataBuilder` (§4.7) |
| Resave stale actor packages | `WorldPartitionResaveActorsBuilder` / `...RecursiveBuilder` (§2.4/§4.4) |
| Fix non-partitioned LI streaming props | `WorldPartitionFixupNonPartitionedActorsBuilder` (§4.2) |
| Repair actor folder assets | `WorldPartitionFixupActorFoldersBuilder` (§4.3) |
| Force-exclude HLOD from a warning log | `ForceHLODExcludeFromLogBuilder` (§4.5) |
| Fix unresolved native classes (CoreRedirects) | `WorldPartitionInvalidNativeClassBuilder` (§4.6) |
| Rename / duplicate a WP world | `WorldPartitionRenameDuplicateBuilder` (§2.10) |

---

## 6. Operating principles (observed across all custom builders)

1. **Only modify if necessary** — every setter is equality-guarded; empty changelists avoided.
2. **Reuse engine behaviour** — call `ULevel::FixupActorFolders`, use
   `FWorldPartitionReference` / `FLevelInstanceEditScope` instead of re-implementing.
3. **Prefix and scope logs** — dedicated `LogFixup...` / `LogWorldPartitionRule...` categories.
4. **Report-only / dry-run first**, then run for real.
5. **Iterate with Live Coding** during development to avoid full editor restarts.

## 7. See also

- [Builders & commandlets](BuildersAndCommandlets.md) (the maintenance subset, with line-level code)
- [World Partition streaming properties](WorldPartitionStreamingProperties.md)
- [Converting levels to World Partition](ConvertingLevelsToWorldPartition.md)
- [Perforce source control](PerforceSourceControl.md)
- [Auxiliary tools & workflow](AuxiliaryToolsAndWorkflow.md)

*Generated 2026-07-09. Grounded in `D:\Sun` engine + `Sundance/WorldBuildingEditor` sources.*
