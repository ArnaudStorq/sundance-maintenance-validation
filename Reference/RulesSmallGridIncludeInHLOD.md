# 7. Rules, SmallGrid & IncludeInHLOD

The rule system that assigns streaming properties to actors automatically, plus the
grid/HLOD compatibility that produces the "Skipped RuntimeGrid override" warning.

---

## The two places rules run

| Path | Trigger | Config field | Notable rule |
|------|---------|--------------|--------------|
| **On actor save** | manual save of a partitioned actor in an allowed map | `*RulesForActorSave` | e.g. `DA_HogsmeadeGrid_Rules` |
| **Streaming generation** | WP streaming build / cook | `RuntimeGridRulesForStreamingGeneration` | `DA_SmallGrid_Rules` only |
| **Batch commandlet** | `WorldPartitionRuleBuilder` | `*RulesForActorSave` (same subsystems) | all three switches |

Config lives in `D:\Sun\Sundance\Config\DefaultEditor.ini` under
`[/Script/WorldBuildingEditor.WorldPartitionRuleSettings]` (class
`UWorldPartitionRuleSettings`, display name *"WorldPartition Rules"*).

Key settings fields (`WorldPartitionRuleSettings.h`):

- `AutoApplyRulesOnActorSave` (master toggle), `MapsWithAutoApplyRules` (allowlist:
  `LV_Overland`, `LI_Hogwarts`, `LI_Hogsmeade`, …).
- `DataLayerRulesForActorSave`, `HLODLayerRulesForActorSave`, `RuntimeGridRulesForActorSave`.
- `RuntimeGridRulesForStreamingGeneration`.
- `ActorTypesIgnoredByRuntimeGridRules` / `OutlinerPathsIgnoredBy…` (and DataLayer/HLOD equivalents).
- `ActorTypesToForceExcludeFromHLOD` / `OutlinerPathsToForceExcludeFromHLOD`.
- `ActorTypesToClearRuntimeGrid` / `OutlinerPathsToClearRuntimeGrid`.
- `ActorTypesToClearDataLayers` / `OutlinerPathsToClearDataLayers`.

### On-save reapplication

Each rule subsystem registers `UPackage::PreSavePackageWithContextEvent` and, on a
**manual** save (not procedural, not autosave), reapplies its `*RulesForActorSave`
rules:

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

Base `UWorldPartitionRuleAsset`: `bIsEnabled`, `MatchingConditions[]`,
`ExclusionCriteria`.

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

---

## IncludeInHLOD & TargetHLODLayer application

`UHLODLayerRuleSubsystem::OnApplyRuleOnActor` (`HLODLayerRuleSubsystem.cpp:125`):

- Normal rule: `SetHLODLayer(TargetHLODLayer)` if different;
  `bEnableAutoLODGeneration = IncludeInHLOD` on the actor **and every**
  `UPrimitiveComponent` child.
- Force-exclude (`RuleAsset == nullptr`, from the `*ForceExcludeFromHLOD` lists):
  `SetHLODLayer(nullptr)` + `bEnableAutoLODGeneration = false` on actor + components.

This is the concrete meaning of "IncludeInHLOD=false + TargetHLODLayer=None" as a way
to make an actor stop being HLOD-relevant (and thus stop tripping the invalid-HLOD-layer
check — see [Topic 1](WorldPartitionStreamingProperties.md)).

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

---

## Ways to resolve a grid/HLOD conflict

1. **Convert the owning level to World Partition** so each actor gets per-actor
   granularity ([Topic 6](ConvertingLevelsToWorldPartition.md)).
2. **Force-exclude from HLOD** (`IncludeInHLOD=false`, `TargetHLODLayer=None`) for actor
   types/paths that shouldn't participate.
3. **Align the HLOD layer rule** (`UHLODLayerRuleAsset`) to the bounds/partitions that
   `DA_SmallGrid_Rules` targets, and add min-bounds guards so tiny meshes are excluded.

---

## The SmallGrid on-save toggle (one-shot migration pattern)

To assign `SmallGrid` during a migration pass, `DA_SmallGrid_Rules` was **added** to
`RuntimeGridRulesForActorSave`, actors were processed, then it was **removed** again —
keeping it permanently in the on-save rules would reassign grids on every future save.

## Rule-tuning changes made (examples)

- **Naming fix**: rules used `Dungeons`/`Missions`; real categories are singular
  `Dungeon`/`Mission` — they matched nothing until corrected.
- **`WorldBitmapStreamingProxy`**: removed from *ignored* types, added to
  *ForceExcludeFromHLOD* and *ClearRuntimeGrid* (handle explicitly, don't ignore).
- **Min bounds 2 m** for HLOD *NoneInclude* in Hogsmeade (exclude single cobble stones).
- **`Overland_Road_Near`** added to the road include/exclude rules.

## Related changelists

- [Apply WP rules to 404 actors — SmallGrid (CL 1959722)](../Reports/P4-History/2026-07-07-06-46-wp-rules-404-actors-smallgrid.md)
- [Add `DA_SmallGrid_Rules` to save rules (CL 1959020)](../Reports/P4-History/2026-07-06-16-14-add-smallgrid-to-runtime-grid-rules.md)
- [Remove `DA_SmallGrid_Rules` from save rules (CL 1960226)](../Reports/P4-History/2026-07-07-12-03-remove-smallgrid-from-runtime-grid-rules.md)
- [WP rules Dungeon/Mission naming (CL 1920591)](../Reports/P4-History/2026-06-10-14-19-wp-rules-dungeon-mission-naming.md)
- [WP rules `WorldBitmapStreamingProxy` (CL 1916537)](../Reports/P4-History/2026-06-08-13-02-wp-rules-worldbitmapstreamingproxy.md)
- [HLOD NoneInclude min bounds — Hogsmeade (CL 1950932)](../Reports/P4-History/2026-06-30-09-13-hlod-noneinclude-min-bounds.md)
- [Set Parent Layer None (Foliage Near) (CL 1753959)](../Reports/P4-History/2026-03-09-09-07-set-parent-layer-none-foliage-near.md)
- [Add `Overland_Road_Near` exclusions (CL 1893933)](../Reports/P4-History/2026-05-25-09-11-add-overland-road-near-exclusions.md)

## See also

- [Topic 1 — Streaming properties](WorldPartitionStreamingProperties.md)
- [Topic 3 — Builders (`WorldPartitionRuleBuilder`)](BuildersAndCommandlets.md)
- Plain-language: [`WorkByTopic/WorldPartitionRules.md`](../WorkByTopic/WorldPartitionRules.md)
