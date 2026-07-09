# 1. Rule engine mechanics

How the World Partition rule system is declared, evaluated and applied — the
common machinery shared by every asset in `/Game/Data/WorldPartition/`.

All rule classes live in the editor-only module `WorldBuildingEditor`
(`/Script/WorldBuildingEditor`). Every asset analysed here is one of:

| Class | Purpose | Assets |
|-------|---------|--------|
| `URuntimeGridRuleAsset` | Assign an actor's **RuntimeGrid** | 5 (`RuntimeGrid/*`) |
| `UHLODLayerRuleAsset` | Assign an actor's **HLODLayer** + `IncludeInHLOD` | 12 (`HLOD/*_Rules`) |
| `UDataLayerRuleAsset` | Assign **Data Layers** | *(outside this folder, `/Game/Data/DataLayers/`)* |

---

## 1.1 Where the settings live

The rule set is bound to the project through
`[/Script/WorldBuildingEditor.WorldPartitionRuleSettings]` in
`D:\Sun\Sundance\Config\DefaultEditor.ini` (class `UWorldPartitionRuleSettings`,
display name *"WorldPartition Rules"*). The fields that matter:

| Field | Role |
|-------|------|
| `AutoApplyRulesOnActorSave` | Master on/off for the on-save path (currently `True`). |
| `MapsWithAutoApplyRules` | Allowlist of maps where rules auto-apply: `LV_Overland`, `LI_Hogwarts`, `LI_Hogsmeade`. |
| `DataLayerRulesForActorSave` | Ordered list of Data Layer rule assets applied on save. |
| `HLODLayerRulesForActorSave` | Ordered list of **HLOD** rule assets applied on save. |
| `RuntimeGridRulesForActorSave` | Ordered list of **grid** rule assets applied on save. |
| `RuntimeGridRulesForStreamingGeneration` | Grid rules applied **only** during streaming generation (here: `DA_SmallGrid_Rules`). |
| `ActorTypesIgnoredBy{DataLayer,RuntimeGrid,HLODLayer}Rules` | Types never touched by that rule family. |
| `ActorTypesToForceExcludeFromHLOD` / `OutlinerPathsToForceExcludeFromHLOD` | Hard HLOD exclusion (bypasses the rule assets). |
| `ActorTypesToClearRuntimeGrid` / `…ClearDataLayers` | Types whose grid / data layers are forcibly cleared. |

The **ordering** of the `*ForActorSave` arrays is a first-class part of the
behaviour — see [document 5](ProcessingOrderAndPriority.md). The exact arrays
as configured today are reproduced in [the inventory](DataAssetInventory.md#config-arrays).

---

## 1.2 The two (three) execution paths

A rule asset is just data. It is executed by one of three drivers:

### A. On manual actor save — the rule subsystems

Each rule family registers a `UPackage::PreSavePackageWithContextEvent` handler.
On a **manual** save (not a procedural save, not an autosave) of an actor that
belongs to an allowed map, the subsystem reapplies its `*RulesForActorSave` list to
that actor:

```810:816:D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionRuleSubsystem.cpp
	if (!SaveContext.IsProceduralSave() && !SaveContext.IsFromAutoSave())
	{
		for (AActor* Actor : Actors)
			OnActorSaved(Cast<AActor>(Actor));
	}
```

Consequences:

- **Re-saving an actor re-applies the rules.** That alone often fixes stale
  streaming properties — no builder run required.
- A re-entrancy guard (`bIsApplyingRules`) stops the save-triggered mutation from
  recursing.
- Fixup builders deliberately save with `SAVE_FromAutosave` to **bypass** this hook
  when they must write without re-triggering rules.

### B. During streaming generation — the mutator

`UAvaStreamingGenerationMutator` (a `UWorldSubsystem`) hooks
`UWorldPartition::OnGenerateStreamingActorDescsMutatePhase` and runs
`ApplyRuntimeGridRules` using `RuntimeGridRulesForStreamingGeneration` for maps in
the auto-apply list. Two properties of this path are essential:

- It changes the **streaming-generation view** of an actor, **not** the actor's
  serialized attributes. The bytes on disk are untouched.
- Before it moves an actor to a target grid it verifies the actor's HLOD layer is
  valid on that grid's partition; if not, it **skips** the move and warns:

```375:375:D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\AvaStreamingGenerationMutator.cpp
UE_LOG(LogAvaStreamingGeneration, Warning, TEXT("Skipped RuntimeGrid override ('%s' -> '%s') for actor '%s' in level '%s': rule '%s' cannot use HLOD layer '%s' on that partition"), ...);
```

This is why `DA_SmallGrid_Rules` is on the streaming-generation path only: SmallGrid
membership is computed at generation time and never written back onto thousands of
actors (see [document 2](RuntimeGridRules.md)).

### C. In batch — the builder

`WorldPartitionRuleBuilder` (run via `WorldPartitionBuilderCommandlet`) applies the
same **on-save** subsystems to a target (a Level Instance, a set of actors, or a
whole map) in a headless commandlet. Switches: `-DataLayerRules`, `-HLODLayerRules`,
`-RuntimeGridRules`, plus `-ContainOutlinerPathSubstrings` /
`-DiscardOutlinerPathSubstrings` to scope the pass. See
[`Docs/WorldPartitionRules/README.md`](../WorldPartitionRules/README.md) and
[`Reference/BuildersAndCommandlets.md`](../../Reference/BuildersAndCommandlets.md).

> **Takeaway:** the builder and manual save share the *same* rule set (the
> `*ForActorSave` arrays). The mutator uses a *different, deliberately smaller* set
> (`*ForStreamingGeneration`) and is view-only.

---

## 1.3 Anatomy of a rule asset

Every rule derives from `UWorldPartitionRuleAsset` and shares this structure
(field names below are the ones actually serialized in the assets):

```
UWorldPartitionRuleAsset
├── bIsEnabled : bool = true            # (not overridden in any Sundance asset → all enabled)
├── MatchingConditions : FWorldPartitionRuleCondition[]   # OR-ed together (actor matches if ANY condition matches)
└── ExclusionCriteria : FWorldPartitionRuleExclusion      # if it fires, the rule does NOT apply
```

### `FWorldPartitionRuleCondition` (a matching condition)

A condition is satisfied when its sub-tests agree per its `LogicOperator`:

| Field | Meaning |
|-------|---------|
| `LogicOperator` | `AND` or `OR` — how the sub-tests inside this one condition combine. |
| `ActorTypes` | Class filter (stored as class **imports**, e.g. `LevelInstance`, `WaterBodyRiver`, `RoadActor`, `InstancedFoliageActor`, `LandscapeStreamingProxy`). |
| `ActorTags` | Gameplay-tag / name filter. |
| `OutlinerPathContains` | Substring(s) the actor's Outliner path must contain. |
| `bUseMinBoundsDimension` / `MinBoundsDimension` | Optional minimum bounding-box dimension gate. |
| `bUseMaxBoundsDimension` / `MaxBoundsDimension` | Optional maximum dimension gate. |
| `bUseMinBoundsVolume` / `MinBoundsVolume` | Optional minimum volume gate. |
| `bUseMaxBoundsVolume` / `MaxBoundsVolume` | Optional maximum volume gate. |
| `bUseRuntimeGrid` / `RuntimeGrid` | Optional "actor is currently on grid X" gate. |

`MatchingConditions` is an **array**; the actor matches the rule if **any** entry
matches (the entries are OR-ed). Within one entry, `LogicOperator` decides how the
sub-tests combine.

> **Bounds values are numeric and do not appear as text in the package.** The
> presence of the `bUse*`/`*Bounds*` field names in every asset only reflects the
> struct layout, not that a gate is enabled. Where a specific threshold is known
> (e.g. the *2 m* minimum on the Hogsmeade `NoneInclude` rule, added in CL 1950932),
> it is called out and attributed in [document 3](HLODLayerRules.md); it was
> confirmed from the changelist history, not re-derived from the binary.

### `FWorldPartitionRuleExclusion` (the exclusion criteria)

If the exclusion fires for an actor, the rule is skipped for that actor:

| Field | Meaning |
|-------|---------|
| `TypesToExclude` | Actor classes the rule must not touch. |
| `HLODLayerRulesToExclude` | Defer to these **HLOD** rules — "if the actor would match one of these, don't apply me". |
| `RuntimeGridRulesToExclude` | Defer to these **grid** rules. |
| `DataLayerRulesToExclude` | Defer to these **Data Layer** rules. |
| `ExcludeIfNotSpatiallyLoaded` | Default **true** — non-spatially-loaded actors are excluded. |
| `ActorTagsToExclude` | Tags that veto the rule. |
| `OutlinerPathsToExclude` | Outliner substrings that veto the rule. |

The `*RulesToExclude` fields are how **precedence** is expressed without a numeric
priority — see [document 5](ProcessingOrderAndPriority.md).

### Specialised fields

| Class | Extra field | Serialized value / default |
|-------|-------------|----------------------------|
| `URuntimeGridRuleAsset` | `TargetRuntimeGrid : FString` | Grid **name** (`SmallGrid`, `HogsmeadeGrid`, `HogwartsGrid`, or `None`). Applied via `Actor->SetRuntimeGrid(FName)`. |
| `UHLODLayerRuleAsset` | `TargetHLODLayer : TSoftObjectPtr<UHLODLayer>` | Soft path to a `UHLODLayer` (or unset = `None`). |
| `UHLODLayerRuleAsset` | `IncludeInHLOD : bool` | **Default `true`**. Only serialized when overridden to `false` (the `NoneExclude` rules). |

---

## 1.4 What "applying a rule" does to the data

### Grid rule application

`URuntimeGridRuleSubsystem` calls `Actor->SetRuntimeGrid(FName(TargetRuntimeGrid))`.
`TargetRuntimeGrid = "None"` clears the grid (actor falls back to the map's default
partition). The grid **name** is all that is stored; the physical cell size and
loading range live on the map's runtime hash, **not** in the rule.

### HLOD rule application

`UHLODLayerRuleSubsystem::OnApplyRuleOnActor`
(`HLODLayerRuleSubsystem.cpp:125`) does, per matched actor:

- **Normal rule** (has a `TargetHLODLayer`): `SetHLODLayer(TargetHLODLayer)` if it
  differs, and sets `bEnableAutoLODGeneration = IncludeInHLOD` on the actor **and on
  every child `UPrimitiveComponent`**.
- **Force-exclude** (the config's `*ForceExcludeFromHLOD` path, `RuleAsset == nullptr`):
  `SetHLODLayer(nullptr)` **and** `bEnableAutoLODGeneration = false` on actor +
  components.

This is the concrete meaning of the two "None" HLOD rules:

| Rule pattern | `TargetHLODLayer` | `IncludeInHLOD` | Net effect on the actor |
|--------------|-------------------|-----------------|-------------------------|
| `*_NoneInclude_Rules` | `None` | `true` (default) | No explicit layer, but stays HLOD-relevant → **inherits** the partition's parent HLOD layer. |
| `*_NoneExclude_Rules` | `None` | `false` | No layer **and** `bEnableAutoLODGeneration=false` → actor stops being HLOD-relevant entirely. |

The difference matters because the engine's invalid-HLOD-layer check only fires for
actors that are HLOD-relevant, spatially loaded, and carry an explicit layer that is
not valid on their grid ([Reference topic 1](../../Reference/WorldPartitionStreamingProperties.md)).
`NoneExclude` makes an actor drop out of that check; `NoneInclude` keeps it in HLOD
but with no explicit (and therefore no *invalid*) layer.

---

## 1.5 Evaluation model (per actor)

For a given rule family and a given actor:

1. Skip immediately if the actor's class is in `ActorTypesIgnoredBy<Family>Rules`.
2. Walk the configured rule array **in order**.
3. For each rule: it **claims** the actor when **any** `MatchingConditions` entry
   passes **and** the `ExclusionCriteria` does **not** fire (type/tag/path excludes,
   `*RulesToExclude` deferrals, and — by default — the "not spatially loaded" veto).
4. **The first rule that claims the actor is applied, and evaluation stops**
   (the per-actor loop `break`s on first match).
5. The global `*ForceExcludeFromHLOD` / `*ClearRuntimeGrid` lists are applied
   independently of the rule assets and win over "keep in HLOD / keep grid" outcomes.

The remaining documents apply this model to the concrete assets:
[grid rules](RuntimeGridRules.md), [HLOD rules](HLODLayerRules.md),
[targets](HLODLayerTargetAssets.md), and
[a full worked precedence walk-through](ProcessingOrderAndPriority.md).
