Parent: [Reference Docs](README.md)

# World Partition rules

How the Sundance project assigns per-actor streaming properties **automatically** from
a set of rule Data Assets, how the rules are applied (on save, at streaming generation,
and in batch), and the grid/HLOD compatibility that produces the "Skipped RuntimeGrid
override" warning.

This is the entry point for the rule system. For the **exact content of every rule
asset** and the precise precedence model, see the
[data-asset analysis](WorldPartitionRulesAnalysis.md) series:
[rule engine mechanics](WorldPartitionRulesAnalysis/RuleEngineMechanics.md), [Runtime Grid rules](WorldPartitionRulesAnalysis/RuntimeGridRules.md),
[HLOD Layer rules](WorldPartitionRulesAnalysis/HLODLayerRules.md), [HLOD Layer target assets](WorldPartitionRulesAnalysis/HLODLayerTargetAssets.md),
[processing order & priority](WorldPartitionRulesAnalysis/ProcessingOrderAndPriority.md) and the
[data asset inventory](WorldPartitionRulesAnalysis/DataAssetInventory.md).

For a flat, exhaustive `if … then …` decision table of **every** registered rule as it matches
today (RuntimeGrid, HLOD and all 56 DataLayer rules), see the
[rule decision flow charts](WorldPartitionRulesFlowCharts.md).

---

## Overview

World Partition is Unreal Engine 5's automatic streaming and data-management system for
large worlds. Instead of a single monolithic level, the world is split into a grid of
streaming cells loaded/unloaded around the player. Which cell, Data Layer and HLOD layer
an actor belongs to is driven by **rules** rather than by hand-tagging every actor.

Three per-actor properties are governed (see [streaming properties](WorldPartitionStreamingProperties.md)):

### Runtime Grid

The Runtime Grid controls which streaming cell an actor belongs to (cell size, loading
range, HLOD behaviour). Assigning an actor to the correct grid is what keeps streaming
performant: cells that are too large stream too much content, cells that are too small
multiply overhead.

### Data Layers

Data Layers group actors so they can be enabled/disabled independently (gameplay states,
quest variants, editor-only content). Rules assign actors to the appropriate Data Layer
automatically instead of relying on manual tagging. (Data Layer rule assets live outside
`/Game/Data/WorldPartition/`, under `/Game/Data/DataLayers/`.)

### HLOD Layers

Hierarchical Level of Detail (HLOD) generates simplified proxy meshes that represent
unloaded cells at a distance. HLOD rules define which HLOD layer an actor contributes to,
and whether it is included in HLOD generation at all.

---

## Where and how rules run

A rule asset is just data; it is executed by one of three drivers:

| Path | Trigger | Config field | Notable rule |
|------|---------|--------------|--------------|
| **On actor save** | manual save of a partitioned actor in an allowed map | `*RulesForActorSave` | e.g. `DA_HogsmeadeGrid_Rules` |
| **Streaming generation** | WP streaming build / cook | `RuntimeGridRulesForStreamingGeneration` | `DA_SmallGrid_Rules` only |
| **Batch commandlet** | `WorldPartitionRuleBuilder` | `*RulesForActorSave` (same subsystems) | all three rule families |

> The builder and manual save share the **same** rule set (the `*ForActorSave` arrays).
> The mutator uses a **different, deliberately smaller** set (`*ForStreamingGeneration`)
> and is view-only. Full detail: [rule engine mechanics](WorldPartitionRulesAnalysis/RuleEngineMechanics.md).

### Config location & key settings

Config lives in `D:\Sun\Sundance\Config\DefaultEditor.ini` under
`[/Script/WorldBuildingEditor.WorldPartitionRuleSettings]` (class
`UWorldPartitionRuleSettings`, display name *"WorldPartition Rules"*).

Key fields (`WorldPartitionRuleSettings.h`):

- `AutoApplyRulesOnActorSave` (master toggle), `MapsWithAutoApplyRules` (allowlist:
  `LV_Overland`, `LI_Hogwarts`, `LI_Hogsmeade`, …).
- `DataLayerRulesForActorSave`, `HLODLayerRulesForActorSave`, `RuntimeGridRulesForActorSave`.
- `RuntimeGridRulesForStreamingGeneration`.
- `ActorTypesIgnoredByRuntimeGridRules` / `OutlinerPathsIgnoredBy…` (and DataLayer/HLOD equivalents).
- `ActorTypesToForceExcludeFromHLOD` / `OutlinerPathsToForceExcludeFromHLOD`.
- `ActorTypesToClearRuntimeGrid` / `OutlinerPathsToClearRuntimeGrid`.
- `ActorTypesToClearDataLayers` / `OutlinerPathsToClearDataLayers`.

The exact arrays as configured today are reproduced in the
[data asset inventory](WorldPartitionRulesAnalysis/DataAssetInventory.md#config-arrays).

### On-save reapplication

Each rule subsystem registers `UPackage::PreSavePackageWithContextEvent` and, on a
**manual** save (not procedural, not autosave), reapplies its `*RulesForActorSave` rules:

```810:816:D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionRuleSubsystem.cpp
	if (!SaveContext.IsProceduralSave() && !SaveContext.IsFromAutoSave())
	{
		for (AActor* Actor : Actors)
			OnActorSaved(Cast<AActor>(Actor));
	}
```

Practical consequence: **just resaving an actor in an allowed map re-applies the
rules** — often that alone fixes stale properties, no builder needed. A re-entrancy
guard (`bIsApplyingRules`) prevents recursion, and fixup builders use
`SAVE_FromAutosave` precisely to *bypass* this hook.

---

## Rule data assets (the "recipe")

Base `UWorldPartitionRuleAsset`: `bIsEnabled`, `MatchingConditions[]`, `ExclusionCriteria`.

- `FWorldPartitionRuleCondition`: `LogicOperator` (OR/AND), `ActorTypes`, `ActorTags`,
  `OutlinerPathContains`, min/max **bounds dimension**/**volume** guards, optional
  `RuntimeGrid` match.
- `FWorldPartitionRuleExclusion`: `TypesToExclude`, `*RulesToExclude`,
  `ExcludeIfNotSpatiallyLoaded` (default `true`), `ActorTagsToExclude`,
  `OutlinerPathsToExclude`.

Specialized assets:

- `URuntimeGridRuleAsset.TargetRuntimeGrid` (`FString` → assigned via
  `Actor->SetRuntimeGrid(FName)`).
- `UHLODLayerRuleAsset.TargetHLODLayer` (`TSoftObjectPtr<UHLODLayer>`) +
  `IncludeInHLOD` (`bool`, default `true`).

The full struct anatomy and per-actor evaluation model are documented in
[rule engine mechanics](WorldPartitionRulesAnalysis/RuleEngineMechanics.md).

### IncludeInHLOD & TargetHLODLayer application

`UHLODLayerRuleSubsystem::OnApplyRuleOnActor` (`HLODLayerRuleSubsystem.cpp:125`):

- Normal rule: `SetHLODLayer(TargetHLODLayer)` if different;
  `bEnableAutoLODGeneration = IncludeInHLOD` on the actor **and every**
  `UPrimitiveComponent` child.
- Force-exclude (`RuleAsset == nullptr`, from the `*ForceExcludeFromHLOD` lists):
  `SetHLODLayer(nullptr)` + `bEnableAutoLODGeneration = false` on actor + components.

This is the concrete meaning of "IncludeInHLOD=false + TargetHLODLayer=None" as a way
to make an actor stop being HLOD-relevant (and thus stop tripping the
invalid-HLOD-layer check — see [streaming properties](WorldPartitionStreamingProperties.md)).

---

## The rule builder (batch)

The `WorldPartitionRuleBuilder` applies the project's rule set to a target (a Level
Instance, a set of actors, or a whole map) in a headless commandlet — the batch
equivalent of the on-save reapplication. It runs through the
`WorldPartitionBuilderCommandlet` (see [builders & commandlets](BuildersAndCommandlets.md)).

| Switch | Effect |
| --- | --- |
| `-DataLayerRules` | Apply Data Layer assignment rules |
| `-HLODLayerRules` | Apply HLOD layer assignment rules |
| `-RuntimeGridRules` | Apply Runtime Grid assignment rules |
| `-ContainOutlinerPathSubstrings="..."` | Restrict processing to actors whose Outliner path contains the given substrings |
| `-DiscardOutlinerPathSubstrings="..."` | Exclude actors whose Outliner path contains the given substrings |
| `-BuildMachine -Unattended` | Non-interactive mode, suitable for automation |

> The Outliner path filters tie directly into how the [Outliner](OutlinerManagement.md)
> is organized. Consistent Outliner naming is what makes rule targeting reliable. This
> builder has **no `-DryRun`**; rule categories are opt-in.

### Running the rule builder in batch

```bat
UnrealEditor-Cmd.exe "Sundance.uproject" ^
  -run=WorldPartitionBuilderCommandlet ^
  -Builder=WorldPartitionRuleBuilder ^
  -DataLayerRules -HLODLayerRules -RuntimeGridRules ^
  -ContainOutlinerPathSubstrings="" -DiscardOutlinerPathSubstrings="" ^
  -BuildMachine -Unattended ^
  <TargetLevelInstance>
```

To process many Level Instances in one pass, use the
[`ProcessLevelInstances`](../Tools/ProcessLevelInstances/README.md) script
([`process_li.bat`](AuxiliaryToolsAndWorkflow.md)), which loops over a list and reports
`[OK]` / `[ERROR]` per entry.

### Reading the logs

The builder narrows engine logging to the categories that matter for a rule pass:

| Log category | What it tells you |
| --- | --- |
| `LogWorldPartitionRules` | Which rules matched and what they assigned (`Applied RuntimeGrid '%s' to actor '%s'.`) |
| `LogWorldPartitionRuleBuilder` | High-level builder progress per target |
| `LogWorldPartitionBuilder` | Streaming/build-level warnings |
| `LogCommandletPackageHelper` | Package load/save errors (blockers) |

A run that finishes without `LogCommandletPackageHelper` errors and with the expected
rule assignments in `LogWorldPartitionRules` is considered successful.

---

## SmallGrid vs HogsmeadeGrid (and where the sizes live)

> ⚠ Note: grid **cell size** and **loading range** are **not** stored in the rule
> assets. Rules only carry a grid **name** (`TargetRuntimeGrid`). The physical numbers
> live on the map's runtime hash (`UWorldPartitionRuntimeSpatialHash` →
> `FSpatialHashStreamingGrid::CellSize` / `GetLoadingRange()`), serialized into the
> level asset (e.g. `LV_Overland`).

The editor reads them here (values are in UE units; UI divides by 100 for metres):

```94:100:D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\HLOD\HLODViewerSubsystem.cpp
if (const FSpatialHashStreamingGrid* Grid = SpatialHash->GetStreamingGridByName(HLODActorDesc.GetRuntimeGrid()))
{
	LayerInfo.LoadingRange = Grid->GetLoadingRange();
	LayerInfo.CellSize = Grid->CellSize;
}
```

Approximate values from the project (confirm against the map's hash):

| Grid | Cell size | Loading range |
|------|-----------|---------------|
| `SmallGrid` | ~76.2 m (7620) | ~128 m (12800) |
| `HogsmeadeGrid` | ~32 m (3200) | ~64 m (6400) |

So `HogsmeadeGrid` is **finer** than `SmallGrid`. Grid↔HLOD-layer compatibility
allowlists live partly in `DefaultPlugins.ini` (`AllowedRuntimeGrids`) and in the map's
runtime hash.

---

## The mutator & the "Skipped RuntimeGrid override" warning

`UAvaStreamingGenerationMutator` (`UWorldSubsystem`) hooks
`UWorldPartition::OnGenerateStreamingActorDescsMutatePhase`. `ApplyRuntimeGridRules`
runs during streaming generation for maps in the auto-apply list, using
`RuntimeGridRulesForStreamingGeneration`.

For each actor, if the rule would change its grid (`CurrentGridName != TargetGridName`)
it checks that the actor's HLOD layer is valid on the **target** grid
(`RuntimeHash->IsValidHLODLayer`). If not, it **skips** the override and warns:

```375:375:D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\AvaStreamingGenerationMutator.cpp
UE_LOG(LogAvaStreamingGeneration, Warning, TEXT("Skipped RuntimeGrid override ('%s' -> '%s') for actor '%s' in level '%s': rule '%s' cannot use HLOD layer '%s' on that partition"), ...);
```

Read literally: rule `DA_SmallGrid_Rules` wants to move an actor to `SmallGrid`, but the
actor's HLOD layer (e.g. `LV_Overland_HLODLayer_Near`) is not allowed on the `SmallGrid`
partition, so the move is refused. This is the **same conflict** at the root of the
whole effort: a Level Instance on `HLODLayer_Near` while an actor is pushed to
`SmallGrid` — two mutually exclusive settings. The mutator also propagates
grid/spatially-loaded decisions across reference clusters, warning on conflicts
(`:202`, `:260`).

Important behavioral facts:

- The mutator changes the **streaming-generation view**, not the actors' stored
  attributes. Actor attributes are changed by the rule **subsystems** (save / builder).
- Rules are **reapplied on save**, so re-saving the affected actors after a rule/config
  change is often enough to converge.
- **First matching rule wins** (the per-actor loop `break`s on first match).

### Ways to resolve a grid/HLOD conflict

1. **Convert the owning level to World Partition** so each actor gets per-actor
   granularity ([converting levels to World Partition](ConvertingLevelsToWorldPartition.md)).
2. **Force-exclude from HLOD** (`IncludeInHLOD=false`, `TargetHLODLayer=None`) for actor
   types/paths that shouldn't participate.
3. **Align the HLOD layer rule** (`UHLODLayerRuleAsset`) to the bounds/partitions that
   `DA_SmallGrid_Rules` targets, and add min-bounds guards so tiny meshes are excluded.

### The SmallGrid on-save toggle (one-shot migration pattern)

To assign `SmallGrid` during a migration pass, `DA_SmallGrid_Rules` was **added** to
`RuntimeGridRulesForActorSave`, actors were processed, then it was **removed** again —
keeping it permanently in the on-save rules would reassign grids on every future save.

---

## Recommended workflow

1. **Organize the Outliner** so actors sit under predictable, rule-friendly paths
   (see [Outliner management](OutlinerManagement.md)).
2. **Apply the rules**, either interactively (resave) or via the batch tool for many
   Level Instances at once.
3. **Run a Map Check** and resolve any warnings/errors the rule pass surfaced (see the
   [MapCheck fix playbook](FixingMapCheckIssues.md)).
4. **Validate streaming** in-editor (World Partition minimap, data layer toggles) before
   submitting.

### Common pitfalls

- Actors left on the **default** grid/layer because their Outliner path did not match
  any rule.
- **HLOD** not regenerated after a rule change, leaving stale proxy meshes.
- Data Layer assignments that conflict between a Level Instance and its parent world.

---

## Rule-tuning changes made (examples)

- **Naming fix**: rules used `Dungeons`/`Missions`; real categories are singular
  `Dungeon`/`Mission` — they matched nothing until corrected.
- **`WorldBitmapStreamingProxy`**: removed from *ignored* types, added to
  *ForceExcludeFromHLOD* and *ClearRuntimeGrid* (handle explicitly, don't ignore).
- **Min bounds 2 m** for HLOD *NoneInclude* in Hogsmeade (exclude single cobble stones).
- **`Overland_Road_Near`** added to the road include/exclude rules.

## Related changelists

- [Apply WP rules to 404 actors — SmallGrid (CL 1959722)](../WorkDoneByChangelists/P4-History/2026-07-07-06-46-wp-rules-404-actors-smallgrid.md)
- [Add `DA_SmallGrid_Rules` to save rules (CL 1959020)](../WorkDoneByChangelists/P4-History/2026-07-06-16-14-add-smallgrid-to-runtime-grid-rules.md)
- [Remove `DA_SmallGrid_Rules` from save rules (CL 1960226)](../WorkDoneByChangelists/P4-History/2026-07-07-12-03-remove-smallgrid-from-runtime-grid-rules.md)
- [WP rules Dungeon/Mission naming (CL 1920591)](../WorkDoneByChangelists/P4-History/2026-06-10-14-19-wp-rules-dungeon-mission-naming.md)
- [WP rules `WorldBitmapStreamingProxy` (CL 1916537)](../WorkDoneByChangelists/P4-History/2026-06-08-13-02-wp-rules-worldbitmapstreamingproxy.md)
- [HLOD NoneInclude min bounds — Hogsmeade (CL 1950932)](../WorkDoneByChangelists/P4-History/2026-06-30-09-13-hlod-noneinclude-min-bounds.md)
- [Set Parent Layer None (Foliage Near) (CL 1753959)](../WorkDoneByChangelists/P4-History/2026-03-09-09-07-set-parent-layer-none-foliage-near.md)
- [Add `Overland_Road_Near` exclusions (CL 1893933)](../WorkDoneByChangelists/P4-History/2026-05-25-09-11-add-overland-road-near-exclusions.md)

## See also

- [World Partition rule data-asset analysis](WorldPartitionRulesAnalysis.md) — the deep, per-asset breakdown.
- [World Partition rules decision flow charts](WorldPartitionRulesFlowCharts.md) — flat `if … then …` decision tables for every registered rule (live-read from the editor).
- [Streaming properties](WorldPartitionStreamingProperties.md) — the three properties and the invalid-HLOD-layer gate.
- [Builders & commandlets](BuildersAndCommandlets.md) — the `WorldPartitionRuleBuilder`.
- [Fixing MapCheck issues](FixingMapCheckIssues.md) — cause → fix playbook these rules feed into.
- **Plain-language narrative:** [`WorkDoneByTopic/WorldPartitionRules.md`](../WorkDoneByTopic/WorldPartitionRules.md)
  — the why-it-was-done story that this reference backs.
