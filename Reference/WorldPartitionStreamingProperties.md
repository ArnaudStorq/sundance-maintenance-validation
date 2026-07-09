# 1. World Partition streaming properties

The three per-actor properties World Partition uses to decide **how** an actor
streams and how it is represented at distance.

| Property | Accessor | Meaning |
|----------|----------|---------|
| **RuntimeGrid** | `AActor::GetRuntimeGrid()` / `SetRuntimeGrid(FName)` | Which runtime streaming grid the actor belongs to (`SmallGrid`, `HogsmeadeGrid`, …). |
| **HLODLayer** | `AActor::GetHLODLayer()` / `SetHLODLayer(UHLODLayer*)` | Which HLOD proxy represents the actor when far away (or `nullptr` = none). |
| **DataLayers** | `AActor::GetDataLayerAssets()` / `RemoveAllDataLayers()` + `FixupDataLayers()` | Which logical Data Layers (season/state variants) the actor is assigned to. |

On unloaded actors these same values are read from the actor descriptor:
`FWorldPartitionActorDescInstance::GetRuntimeGrid()`, `GetHLODLayer()` (returns a
`FSoftObjectPath`), `GetActorIsHLODRelevant()`, `GetDataLayerAssets(bIncludeExternalDataLayerAsset)`.

---

## The HLOD-relevance rule (the heart of the "invalid HLOD layer" warning)

An actor is validated for HLOD-layer/grid compatibility **only if ALL** of these hold
(engine, `ValidateContainerInstanceDescriptor()` in
`D:\Sun\Engine\Source\Runtime\Engine\Private\WorldPartition\WorldPartitionStreamingGeneration.cpp:1821`):

1. `ActorDescView.GetActorIsHLODRelevant()` — the actor participates in HLOD.
2. `ActorDescView.GetIsSpatiallyLoaded()` — the actor is spatially loaded.
3. `ActorDescView.GetHLODLayer().IsValid()` — it has an explicit HLOD layer.
4. `!IsValidHLODLayer(RuntimeGrid, HLODLayer)` — that layer is **not** registered for
   the actor's runtime grid in the map's runtime hash.

```1821:1839:D:\Sun\Engine\Source\Runtime\Engine\Private\WorldPartition\WorldPartitionStreamingGeneration.cpp
	//@third party code - AVA BEGIN [philippe.st-jean] Skip non-HLODRelevant actors from HLOD validation
	if (ActorDescView.GetActorIsHLODRelevant() && ActorDescView.GetIsSpatiallyLoaded() && ActorDescView.GetHLODLayer().IsValid() && !IsValidHLODLayer(PerInstanceData.RuntimeGrid, ActorDescView.GetHLODLayer()))
	//@third party code - AVA BEGIN [philippe.st-jean] Skip non-HLODRelevant actors from HLOD validation
	{
		if (PassType == EPassType::ErrorReporting)  { ErrorHandler->OnInvalidHLODLayer(ActorDescView); }
		else                                        { ActorDescView.SetForcedNoHLODLayer(); }
		NbErrorsDetected++;
	}
```

So an actor being HLOD-relevant is a **derived** state, not just a flag: see
`AActor::IsHLODRelevant()` (`Level`? no — `Actor.cpp:6988`): not transient (with Level
Instance exceptions), not hidden, not editor-only, `bEnableAutoLODGeneration == true`,
**and in a partitioned world it must be spatially loaded**, and must own at least one
HLOD-relevant component.

### The gate: "require explicit HLOD layer partition assignation"

The whole block above only runs when
`IWorldPartitionEditorModule::Get().GetRequireExplicitHLODLayerPartitionAssignation()`
is `true`. Sundance forces this on at module startup:

```276:276:D:\Sun\Engine\Source\Editor\WorldPartitionEditor\Private\WorldPartitionEditorModule.cpp
	bRequireExplicitHLODLayerPartitionAssignation = true;
```

`IsValidHLODLayer` resolves through the map's runtime hash. For a hash-set world:

```414:417:D:\Sun\Engine\Source\Runtime\Engine\Private\WorldPartition\RuntimeHashSet\WorldPartitionRuntimeHashSet.cpp
bool UWorldPartitionRuntimeHashSet::IsValidHLODLayer(FName GridName, const FSoftObjectPath& HLODLayerPath) const
{
	return ResolveRuntimePartitionForHLODLayer(GridName, HLODLayerPath) != nullptr;
}
```

This is why the fix is either (a) give the actor a layer that **is** allowed on its
grid, or (b) clear the layer / make it non-HLOD-relevant. The grid↔layer allowlists
live on the map (see [Topic 7](RulesSmallGridIncludeInHLOD.md)) and partly in
`DefaultPlugins.ini` (`AllowedRuntimeGrids`).

---

## Parent inheritance & "Include In HLOD without an explicit layer"

- A parent HLOD layer is only inherited when the actor has **no** valid HLOD layer,
  **is** spatially loaded, **and** is HLOD-relevant (`ResolveHLODLayer`,
  `WorldPartitionStreamingGeneration.cpp:804`).
- An actor can therefore be **Include In HLOD = true with no explicit `HLODLayer`**:
  `bEnableAutoLODGeneration` is what makes it HLOD-relevant; the layer itself can be
  inherited or `None`. Clearing HLOD = `SetHLODLayer(nullptr)` **and**
  `bEnableAutoLODGeneration = false` (this is exactly what the force-exclude path does,
  see [Topic 7](RulesSmallGridIncludeInHLOD.md)).

---

## The MapCheck / streaming-generation warning strings (verbatim)

Emitted by `ITokenizedMessageErrorHandler`
(`D:\Sun\Engine\Source\Runtime\Engine\Private\WorldPartition\ErrorHandling\WorldPartitionStreamingGenerationTokenizedMessageErrorHandler.cpp`):

| Handler | Severity | Rendered message | MapCheck token |
|---------|----------|------------------|----------------|
| `OnInvalidHLODLayer` (`:280`) | **Warning** | `Actor <name> has an invalid HLOD layer <HLODLayerPath>` | `WorldPartition_InvalidActorHLODLayer_CheckForErrors` |
| `OnInvalidRuntimeGrid` (`:16`) | **Error** | `Actor <name> has an invalid runtime grid <GridName>` | `WorldPartition_InvalidRuntimeGrid_CheckForErrors` |
| `OnInvalidReference` (`:28`) | **Error** | `Actor <name> has an invalid reference to <other>` | `WorldPartition_MissingActorReference_CheckForErrors` |

The log-only variants (`FStreamingGenerationLogErrorHandler`) print the same text via
`UE_LOG`, e.g. `Actor %s has an invalid HLOD layer %s`.

> ⚠ Note: there is **no** function named `FixupInvalidHLODLayerOnAsset`. The in-memory
> streaming-generation fix is `FStreamingGenerationActorDescView::SetForcedNoHLODLayer()`
> (`WorldPartitionStreamingGeneration.cpp:420`). A disk-writing MapCheck auto-fixer
> exists (`FWorldPartitionHLODFixupHelper::EnqueueInvalidStreamingPropertiesFixup` →
> `WorldPartitionHLODFixup::FixupOne`, `.../Editor/UnrealEd/Private/WorldPartition/WorldPartitionHLODFixupHelper.cpp`)
> but its call is **commented out / disabled** (`// @astorq Comment this call to
> deactivate the mapcheck fixer.`). The bulk cleanup was done with the custom builder
> instead (see [Topic 3](BuildersAndCommandlets.md)).

---

## Two-pass validation model

Streaming generation validates in passes (`WorldPartitionStreamingGeneration.cpp:1788`):

- **Pass 0 = `ErrorReporting`** → emit `OnInvalid*` messages (MapCheck / log).
- **Pass 1+ = `Fixup`** → apply the in-memory fix (`SetForcedNoHLODLayer()` etc.) so
  cooked/runtime data is consistent even if the source asset still has the bad value.

This is why a warning can appear at edit-time yet the cooked data is still valid: the
fixup pass silently corrects the runtime view; the **source package** keeps the stale
value until a builder resaves it.

---

## Related changelists

- [Fix MapCheck invalid HLOD layer (CL 1738687)](../WorkDoneByChangelists/P4-History/2026-02-25-13-59-fix-mapcheck-invalid-hlod-layer.md)
- [Fix 644 MapCheck HLOD warnings (CL 1904278)](../WorkDoneByChangelists/P4-History/2026-06-01-15-19-fix-644-mapcheck-hlod-warnings.md)
- [Remove HLOD from non-partitioned levels (CL 1918257)](../WorkDoneByChangelists/P4-History/2026-06-09-09-31-remove-hlod-nonpartitioned-levels.md)

## See also

- [Topic 7 — Rules, SmallGrid & IncludeInHLOD](RulesSmallGridIncludeInHLOD.md)
- [Topic 2 — Level Instances & OFPA](LevelInstancesAndOFPA.md)
- How-to: [MapCheck fix playbook](../Docs/MapCheck/FixingMapCheckIssues.md) (cause → solution per warning)
- Plain-language: [`WorkDoneByTopic/HLOD.md`](../WorkDoneByTopic/HLOD.md)
