# Mutator Add Condition Detect Merlin Dungeon Asset

- Date: 2026-06-10 13:56
- Source transcript: `2667d130-4a79-4087-8e13-e438a1361d00`

---

### User

dans ce code specifiquement,

je veux rajouter une condition pour trouver quand on tombe sur cet asset (un IF) lors du mutator
/Game/Experimental/Levels/Dungeons/Merlin_Dungeon/Dun_MT_Depulso_02.BPP_MerlinRock_2x2x2_A_Dense_B20

// Copyright 2025 WB Games Inc. All Rights Reserved
#include "AvaStreamingGenerationMutator.h"

#include "LandscapeStreamingProxy.h"
#include "RuntimeGridRuleAsset.h"
#include "RuntimeGridRuleSubsystem.h"
#include "WorldPartition/WorldPartition.h"
#include "WorldPartition/WorldPartitionStreamingGenerationContext.h"
#include "WorldPartitionRuleSettings.h"
#include "WorldPartition/WorldPartitionStreamingGeneration.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "StreamingDependencyGroup.h"
#include "WorldPartition/DataLayer/DataLayerAsset.h"
#include "WorldPartition/DataLayer/DataLayerManager.h"
#include "WorldPartition/ActorDescContainerInstance.h"
#include "WorldPartition/IWorldPartitionEditorModule.h"
#include "WorldPartition/WorldPartitionRuntimeHash.h"
#include "Engine/Level.h"

DEFINE_LOG_CATEGORY(LogAvaStreamingGeneration);

static bool bApplyNonSpatiallyLoaded = true;
static FAutoConsoleVariableRef CVarApplyNonSpatiallyLoadedToInterior(
	TEXT("AvaApplyNonSpatiallyLoadedToInteriorStreaming"),
	bApplyNonSpatiallyLoaded,
	TEXT("Apply none-spatially loaded setting to interior streaming cells, cannot modify during runtime.")
);

static bool bApplyNonSpatiallyLoadedToLandscape = false;
static FAutoConsoleVariableRef CVarApplyNonSpatiallyLoadedToLandscape(
	TEXT("AvaApplyNonSpatiallyLoadedToLandscape"),
	bApplyNonSpatiallyLoadedToLandscape,
	TEXT("Apply none-spatially loaded setting to landscape cells, cannot modify during runtime.")
);

bool UAvaStreamingGenerationMutator::DoesSupportWorldType(const EWorldType::Type WorldType) const
{
	return WorldType == EWorldType::Editor || WorldType == EWorldType::Inactive;
}

void UAvaStreamingGenerationMutator::Initialize(FSubsystemCollectionBase& Collection)
{
	GetWorld()->OnWorldPartitionInitialized().AddUObject(this, &UAvaStreamingGenerationMutator::OnWorldPartitionInitialized);
	GetWorld()->OnWorldPartitionUninitialized().AddUObject(this, &UAvaStreamingGenerationMutator::OnWorldPartitionUninitialized);
}

void UAvaStreamingGenerationMutator::Deinitialize()
{
	GetWorld()->OnWorldPartitionInitialized().RemoveAll(this);
	GetWorld()->OnWorldPartitionUninitialized().RemoveAll(this);
}

void UAvaStreamingGenerationMutator::OnWorldPartitionInitialized(UWorldPartition* WorldPartition)
{
	WorldPartition->OnGenerateStreamingActorDescsMutatePhase.AddUObject(this, &UAvaStreamingGenerationMutator::HandleStreamingGenerationMutatorPhase);
}

void UAvaStreamingGenerationMutator::OnWorldPartitionUninitialized(UWorldPartition* WorldPartition)
{
	WorldPartition->OnGenerateStreamingActorDescsMutatePhase.RemoveAll(this);
}

FActorDescViewMutatorInstance& UAvaStreamingGenerationMutator::FindOrAddMutator(TMap<FActorMutatorKey, FActorDescViewMutatorInstance>& Mutators, const FActorContainerID& ContainerId, const FGuid& ActorGuid)
{
	FActorDescViewMutatorInstance& Mutator = Mutators.FindOrAdd(FActorMutatorKey(ContainerId, ActorGuid));
	Mutator.ContainerId = ContainerId;
	Mutator.ActorGuid = ActorGuid;
	return Mutator;
}

namespace AvaStreamingGenerationMutatorLogging
{
	static FString GetActorDescLabel(const FStreamingGenerationActorDescView& ActorDescView, const FGuid& ActorGuid)
	{
		return ActorDescView.GetActorDescInstance() ? ActorDescView.GetActorDescInstance()->GetActorLabelOrName().ToString() : ActorGuid.ToString();
	}

	static void AppendSourceName(FString& Names, const FString& SourceName)
	{
		if (!Names.IsEmpty())
		{
			Names += TEXT(", ");
		}
		Names += SourceName;
	}

	// Who in the cluster had Apply-pass overrides that forced this propagation
	static FString BuildPropagationSourceSuffix(const TArray<FGuid>& OverrideSourceGuids, const FGuid& PropagatedActorGuid, const FStreamingGenerationActorDescView& PropagatedActorDescView, const FStreamingGenerationActorDescViewMap& ActorDescViewMap)
	{
		FString DirectSourceNames;
		FString IndirectSourceNames;
		for (const FGuid& SourceGuid : OverrideSourceGuids)
		{
			if (SourceGuid == PropagatedActorGuid)
			{
				continue;
			}

			const FStreamingGenerationActorDescView& SourceActorDescView = ActorDescViewMap.FindByGuidChecked(SourceGuid);
			const FString SourceName = GetActorDescLabel(SourceActorDescView, SourceGuid);
			const bool bDirectRef = PropagatedActorDescView.GetReferences().Contains(SourceGuid) || SourceActorDescView.GetReferences().Contains(PropagatedActorGuid);
			if (bDirectRef)
			{
				AppendSourceName(DirectSourceNames, SourceName);
			}
			else
			{
				AppendSourceName(IndirectSourceNames, SourceName);
			}
		}

		if (!DirectSourceNames.IsEmpty())
		{
			return FString::Printf(TEXT("following ref-cluster; rule override from '%s' [direct ref]"), *DirectSourceNames);
		}
		if (!IndirectSourceNames.IsEmpty())
		{
			return FString::Printf(TEXT("following ref-cluster; rule override from '%s' [same cluster, indirect]"), *IndirectSourceNames);
		}
		return TEXT("following ref-cluster");
	}
}

void UAvaStreamingGenerationMutator::PropagateMutatorsAcrossActorSets(const IStreamingGenerationContext* Context, TMap<FActorMutatorKey, FActorDescViewMutatorInstance>& Mutators)
{
	using namespace AvaStreamingGenerationMutatorLogging;
	const bool bLogPropagationVerbose = UE_LOG_ACTIVE(LogAvaStreamingGeneration, Verbose); // Optim: We only run some costy code when LogAvaStreamingGeneration is set to Verbose

	Context->ForEachActorSetContainerInstance([&](const IStreamingGenerationContext::FActorSetContainerInstance& Container)
		{
			const FActorContainerID ContainerId = Container.ContainerInstanceCollection->GetBaseContainerInstance()->GetContainerID();
			check(Container.ActorDescViewMap);

			for (const TUniquePtr<IStreamingGenerationContext::FActorSet>& ActorSetPtr : Container.ActorSets)
			{
				const IStreamingGenerationContext::FActorSet& ActorSet = *ActorSetPtr;

				// An ActorSet == a Cluster: a group of actors that reference each other, so every member must end
				// up on the same RuntimeGrid and bIsSpatiallyLoaded or the engine asserts. The ApplyXxx passes set
				// overrides per-actor; this pass makes each override uniform across the whole set.
				// e.g. if Chair goes from RuntimeGrid Overland->Interior, the Table/Lamp it references follow to
				// Interior RuntimGrid even if no rule touched them.
				if (ActorSet.Actors.Num() <= 1)
				{
					// A single actor can't disagree with itself
					continue;
				}

				// RuntimeGrid:
				// If any member was moved to a grid, move the whole set there
				// First override in member order wins; a second, different override means rules disagree within one set
				FName UnifiedRuntimeGrid = NAME_None;
				bool bHasConflictingGridOverrides = false;
				TArray<FGuid> GridOverrideSourceGuids;
				if (bLogPropagationVerbose)
				{
					GridOverrideSourceGuids.Reserve(ActorSet.Actors.Num());
				}
				for (const FGuid& ActorGuid : ActorSet.Actors)
				{
					if (const FActorDescViewMutatorInstance* Mutator = Mutators.Find(FActorMutatorKey(ContainerId, ActorGuid)))
					{
						if (Mutator->RuntimeGrid.IsSet())
						{
							if (bLogPropagationVerbose)
							{
								GridOverrideSourceGuids.Add(ActorGuid);
							}
							if (UnifiedRuntimeGrid == NAME_None)
							{
								UnifiedRuntimeGrid = Mutator->RuntimeGrid.GetValue();
							}
							else if (UnifiedRuntimeGrid != Mutator->RuntimeGrid.GetValue())
							{
								bHasConflictingGridOverrides = true;
							}
						}
					}
				}

				if (UnifiedRuntimeGrid != NAME_None)
				{
					for (const FGuid& ActorGuid : ActorSet.Actors)
					{
						const FStreamingGenerationActorDescView& ActorDescView = Container.ActorDescViewMap->FindByGuidChecked(ActorGuid);
						if (ActorDescView.GetRuntimeGrid() != UnifiedRuntimeGrid)
						{
							if (bLogPropagationVerbose)
							{
								const FString ActorName = GetActorDescLabel(ActorDescView, ActorGuid);
								const FString SourceSuffix = BuildPropagationSourceSuffix(GridOverrideSourceGuids, ActorGuid, ActorDescView, *Container.ActorDescViewMap);
								UE_LOG(LogAvaStreamingGeneration, Verbose, TEXT("Propagating RuntimeGrid '%s' -> '%s' to actor '%s' (%s)"), *ActorDescView.GetRuntimeGrid().ToString(), *UnifiedRuntimeGrid.ToString(), *ActorName, *SourceSuffix);
							}

							FindOrAddMutator(Mutators, ContainerId, ActorGuid).RuntimeGrid = UnifiedRuntimeGrid;
						}
					}

					if (bHasConflictingGridOverrides)
					{
						// Authoring issue worth surfacing: two rules want different grids for one ref-cluster
						UE_LOG(LogAvaStreamingGeneration, Warning, TEXT("Ref-cluster had conflicting RuntimeGrid rule overrides; forced all %d members to '%s'"), ActorSet.Actors.Num(), *UnifiedRuntimeGrid.ToString());
					}
				}

				// bIsSpatiallyLoaded:
				// If any member became non-spatial, the whole set becomes non-spatial
				TOptional<bool> UnifiedSpatiallyLoaded;
				bool bHasConflictingSpatialOverrides = false;
				TArray<FGuid> SpatialOverrideSourceGuids;
				if (bLogPropagationVerbose)
				{
					SpatialOverrideSourceGuids.Reserve(ActorSet.Actors.Num());
				}
				for (const FGuid& ActorGuid : ActorSet.Actors)
				{
					if (const FActorDescViewMutatorInstance* Mutator = Mutators.Find(FActorMutatorKey(ContainerId, ActorGuid)))
					{
						if (Mutator->bIsSpatiallyLoaded.IsSet())
						{
							if (bLogPropagationVerbose)
							{
								SpatialOverrideSourceGuids.Add(ActorGuid);
							}
							if (!UnifiedSpatiallyLoaded.IsSet())
							{
								UnifiedSpatiallyLoaded = Mutator->bIsSpatiallyLoaded.GetValue();
							}
							else if (UnifiedSpatiallyLoaded.GetValue() != Mutator->bIsSpatiallyLoaded.GetValue())
							{
								// Non-spatially loaded wins — refs must load together
								UnifiedSpatiallyLoaded = false;
								bHasConflictingSpatialOverrides = true;
							}
						}
					}
				}

				if (UnifiedSpatiallyLoaded.IsSet())
				{
					for (const FGuid& ActorGuid : ActorSet.Actors)
					{
						const FStreamingGenerationActorDescView& ActorDescView = Container.ActorDescViewMap->FindByGuidChecked(ActorGuid);
						if (ActorDescView.GetIsSpatiallyLoaded() != UnifiedSpatiallyLoaded.GetValue())
						{
							if (bLogPropagationVerbose)
							{
								const FString ActorName = GetActorDescLabel(ActorDescView, ActorGuid);
								const FString SourceSuffix = BuildPropagationSourceSuffix(SpatialOverrideSourceGuids, ActorGuid, ActorDescView, *Container.ActorDescViewMap);
								UE_LOG(LogAvaStreamingGeneration, Verbose, TEXT("Propagating bIsSpatiallyLoaded '%s' -> '%s' to actor '%s' (%s)"), ActorDescView.GetIsSpatiallyLoaded() ? TEXT("true") : TEXT("false"), UnifiedSpatiallyLoaded.GetValue() ? TEXT("true") : TEXT("false"), *ActorName, *SourceSuffix);
							}

							FindOrAddMutator(Mutators, ContainerId, ActorGuid).bIsSpatiallyLoaded = UnifiedSpatiallyLoaded.GetValue();
						}
					}

					if (bHasConflictingSpatialOverrides)
					{
						// Authoring issue worth surfacing: members disagree, so the whole ref-cluster is forced non-spatial
						UE_LOG(LogAvaStreamingGeneration, Warning, TEXT("Ref-cluster had conflicting bIsSpatiallyLoaded overrides; forced all %d members to 'false'"), ActorSet.Actors.Num());
					}
				}
			}
		});
}

void UAvaStreamingGenerationMutator::HandleStreamingGenerationMutatorPhase(const IStreamingGenerationContext* Context, TArray<FActorDescViewMutatorInstance>& OutMutatorInstances) const
{
	int32 EstimatedMutators = 0;
	Context->ForEachActorSetContainerInstance([&EstimatedMutators](const IStreamingGenerationContext::FActorSetContainerInstance& Container)
		{
			EstimatedMutators += Container.ActorDescViewMap->Num();
		});

	TMap<FActorMutatorKey, FActorDescViewMutatorInstance> Mutators;
	Mutators.Reserve(EstimatedMutators);

	ApplyRuntimeGridRules(Context, Mutators);
	ApplyInteriorStreamingSetting(Context, Mutators);
	ApplyIsSpatiallyLoadedRules(Context, Mutators);
	PropagateMutatorsAcrossActorSets(Context, Mutators);

	OutMutatorInstances.Reserve(Mutators.Num());
	for (TPair<FActorMutatorKey, FActorDescViewMutatorInstance>& MutatorPair : Mutators)
	{
		OutMutatorInstances.Add(MoveTemp(MutatorPair.Value));
	}
}

void UAvaStreamingGenerationMutator::ApplyRuntimeGridRules(const IStreamingGenerationContext* Context, TMap<FActorMutatorKey, FActorDescViewMutatorInstance>& OutMutators) const
{
	const UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}

	const UWorldPartition* WorldPartition = World->GetWorldPartition();
	if (!WorldPartition || !WorldPartition->IsStreamingEnabled())
	{
		return;
	}

	if (!UWorldPartitionRuleSubsystem::IsWorldInAutoApplyList(World))
	{
		return;
	}

	const UWorldPartitionRuleSettings* WorldPartitionRuleSettings = GetDefault<UWorldPartitionRuleSettings>();
	if (!WorldPartitionRuleSettings)
	{
		UE_LOG(LogAvaStreamingGeneration, Error, TEXT("Failed to retrieve UWorldPartitionRuleSettings"));
		return;
	}

	const URuntimeGridRuleSubsystem* RuntimeGridRuleSubsystem = GEditor->GetEditorSubsystem<URuntimeGridRuleSubsystem>();
	if (!RuntimeGridRuleSubsystem)
	{
		UE_LOG(LogAvaStreamingGeneration, Error, TEXT("Failed to retrieve URuntimeGridRuleSubsystem"));
		return;
	}

	TArray<URuntimeGridRuleAsset*> EnabledGridRules;
	EnabledGridRules.Reserve(WorldPartitionRuleSettings->RuntimeGridRulesForStreamingGeneration.Num());
	for (const TSoftObjectPtr<URuntimeGridRuleAsset>& RuleAssetPtr : WorldPartitionRuleSettings->RuntimeGridRulesForStreamingGeneration)
	{
		URuntimeGridRuleAsset* RuleAsset = RuleAssetPtr.IsValid() ? RuleAssetPtr.Get() : RuleAssetPtr.LoadSynchronous();
		if (RuleAsset && RuleAsset->bIsEnabled)
		{
			EnabledGridRules.Add(RuleAsset);
		}
	}

	const UWorldPartitionRuntimeHash* RuntimeHash = WorldPartition->RuntimeHash;
	const bool bValidateHLODLayer = IWorldPartitionEditorModule::Get().GetRequireExplicitHLODLayerPartitionAssignation();
	Context->ForEachActorSetContainerInstance([&](const IStreamingGenerationContext::FActorSetContainerInstance& Container)
		{
			const FActorContainerID ContainerId = Container.ContainerInstanceCollection->GetBaseContainerInstance()->GetContainerID();
			const bool bIsOwningLevelPartitioned = ULevel::GetIsLevelPartitionedFromPackage(Container.ContainerInstanceCollection->GetBaseContainerInstancePackageName());

			// Set the grid per-actor; PropagateMutatorsAcrossActorSets makes it uniform across ref-connected sets afterward
			Container.ActorDescViewMap->ForEachActorDescView([&](const FStreamingGenerationActorDescView& ActorDescView)
				{
					const FWorldPartitionActorDescInstance* ActorDescInstance = ActorDescView.GetActorDescInstance();
					if (!ActorDescInstance)
					{
						return;
					}

					WorldPartitionRules::FActorOrDesc ActorOrDesc(ActorDescInstance);
					for (URuntimeGridRuleAsset* RuleAsset : EnabledGridRules)
					{
						const WorldPartitionRules::EMatchRuleResult MatchRuleResult = RuntimeGridRuleSubsystem->Get()->IsActorMatchingRule(ActorOrDesc, *RuleAsset);
						if (MatchRuleResult == WorldPartitionRules::EMatchRuleResult::Match || MatchRuleResult == WorldPartitionRules::EMatchRuleResult::MatchButRuleAssetMissing)
						{
							const FName TargetGridName = FName(RuleAsset->TargetRuntimeGrid);
							const FName CurrentGridName = ActorDescView.GetRuntimeGrid();
							if (CurrentGridName != TargetGridName)
							{
								if (bValidateHLODLayer && RuntimeHash
									&& ActorDescView.GetActorIsHLODRelevant()
									&& ActorDescView.GetIsSpatiallyLoaded()
									&& ActorDescView.GetHLODLayer().IsValid()
									&& !RuntimeHash->IsValidHLODLayer(TargetGridName, ActorDescView.GetHLODLayer()))
								{
									if (bIsOwningLevelPartitioned)
									{
										UE_LOG(LogAvaStreamingGeneration, Warning, TEXT("Skipped RuntimeGrid override ('%s' -> '%s') for actor '%s': rule '%s' cannot use HLOD layer '%s' on that partition"), *CurrentGridName.ToString(), *TargetGridName.ToString(), *ActorDescInstance->GetActorLabelOrName().ToString(), *RuleAsset->GetName(), *ActorDescView.GetHLODLayer().GetAssetName());
									}
									else
									{
										UE_LOG(LogAvaStreamingGeneration, Verbose, TEXT("Skipped RuntimeGrid override ('%s' -> '%s') for actor '%s': rule '%s' cannot use HLOD layer '%s' on that partition"), *CurrentGridName.ToString(), *TargetGridName.ToString(), *ActorDescInstance->GetActorLabelOrName().ToString(), *RuleAsset->GetName(), *ActorDescView.GetHLODLayer().GetAssetName());
									}
								}
								else
								{
									UE_LOG(LogAvaStreamingGeneration, Verbose, TEXT("Overriding RuntimeGrid '%s' -> '%s' for actor '%s'"), *CurrentGridName.ToString(), *TargetGridName.ToString(), *ActorDescInstance->GetActorLabelOrName().ToString());
									FindOrAddMutator(OutMutators, ContainerId, ActorDescInstance->GetGuid()).RuntimeGrid = TargetGridName;
								}
							}

							// First matching rule wins (priority order).
							break;
						}
					}
				});
		});
}

void UAvaStreamingGenerationMutator::ApplyInteriorStreamingSetting(const IStreamingGenerationContext* Context, TMap<FActorMutatorKey, FActorDescViewMutatorInstance>& OutMutators) const
{
	if (!bApplyNonSpatiallyLoaded)
	{
		return;
	}

	UWorld* CurrentWorld = GetWorld();
	if (!CurrentWorld)
	{
		return;
	}
	UDataLayerManager* DataLayerManager = UDataLayerManager::GetDataLayerManager(CurrentWorld);
	if (!DataLayerManager)
	{
		return;
	}
	const IAssetRegistry& AssetRegistry = FModuleManager::GetModuleChecked<FAssetRegistryModule>(TEXT("AssetRegistry")).Get();
	TArray<FAssetData> AssetData;
	AssetRegistry.GetAssetsByClass(UStreamingDependencyGroup::StaticClass()->GetClassPathName(), AssetData, false);
	TSet<FName> InteriorDataLayerNames;
	for (FAssetData Asset : AssetData)
	{
		FSoftObjectPath SoftObjectPath(Asset.GetSoftObjectPath());
		TSoftObjectPtr<UStreamingDependencyGroup> SoftDataLayerAsset(SoftObjectPath);
		if (const UStreamingDependencyGroup* SDG = Cast<UStreamingDependencyGroup>(Asset.GetAsset()))
		{
			for (FDataLayerStreamingDependencyEntries DepEntries : SDG->Dependencies.DataLayerDeps)
			{
				for (FSoftObjectPath DataLayerDependency : DepEntries.Dependencies)
				{
					TSoftObjectPtr<UDataLayerAsset> DataLayerAsset(DataLayerDependency);
					if (const UDataLayerInstance* DataLayerInstance = DataLayerManager->GetDataLayerInstanceFromAsset(DataLayerAsset.Get()))
					{
						if (DataLayerInstance->IsRuntime())
						{
							InteriorDataLayerNames.Add(DataLayerInstance->GetDataLayerFName());
						}
					}
				}
			}
		}
	}
	if (InteriorDataLayerNames.Num() <= 0)
	{
		return;
	}
	Context->ForEachActorSetContainerInstance([&](const IStreamingGenerationContext::FActorSetContainerInstance& Container)
		{
			const FActorContainerID ContainerId = Container.ContainerInstanceCollection->GetBaseContainerInstance()->GetContainerID();

			bool bIsInterior = false;
			auto CheckDataLayers = [&](const UActorDescContainerInstance* ContainerInstance, auto& RecursiveFunc) -> void
				{
					if (const UActorDescContainerInstance* parentCon = ContainerInstance->GetParentContainerInstance())
					{
						if (FWorldPartitionActorDescInstance* parentActorDescIns = parentCon->GetActorDescInstance(ContainerInstance->GetContainerActorGuid()))
						{
							TArray<FName> DLs = parentActorDescIns->GetDataLayerInstanceNames().ToArray();
							bool bHasInteriorDL = false;
							for (const FName& DL : DLs)
							{
								if (InteriorDataLayerNames.Contains(DL))
								{
									bHasInteriorDL = true;
									break;
								}
							}
							if (DLs.Num() > 0 && bHasInteriorDL)
							{
								bIsInterior = true;
							}
							else
							{
								RecursiveFunc(parentCon, RecursiveFunc);
							}
						}
					}
				};
			CheckDataLayers(Container.ContainerInstanceCollection->GetBaseContainerInstance(), CheckDataLayers);

			if (bIsInterior)
			{
				Container.ActorDescViewMap->ForEachActorDescView([&](const FStreamingGenerationActorDescView& ActorDescView)
					{
						const FWorldPartitionActorDescInstance* ActorDescInstance = ActorDescView.GetActorDescInstance();
						if (!ActorDescInstance)
						{
							return;
						}
						FindOrAddMutator(OutMutators, ContainerId, ActorDescInstance->GetGuid()).bIsSpatiallyLoaded = false;
						UE_LOG(LogAvaStreamingGeneration, Verbose, TEXT("Overriding spatially loaded for actor '%s'"), *ActorDescInstance->GetActorLabelOrName().ToString());
					});
			}
		});
}

void UAvaStreamingGenerationMutator::ApplyIsSpatiallyLoadedRules(const IStreamingGenerationContext* Context, TMap<FActorMutatorKey, FActorDescViewMutatorInstance>& OutMutators) const
{
	if (!bApplyNonSpatiallyLoadedToLandscape)
	{
		return;
	}
	const UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}

	if (!World->GetMapName().Contains(TEXT("LV_Overland")))
	{
		return;
	}

	const UWorldPartition* WorldPartition = World->GetWorldPartition();
	if (!WorldPartition || !WorldPartition->IsStreamingEnabled())
	{
		return;
	}

	UWorldPartitionRuleSettings* WorldPartitionRuleSettings = GetMutableDefault<UWorldPartitionRuleSettings>();
	if (!WorldPartitionRuleSettings)
	{
		UE_LOG(LogAvaStreamingGeneration, Error, TEXT("Failed to retrieve UWorldPartitionRuleSettings"));
		return;
	}

	Context->ForEachActorSetContainerInstance([&](const IStreamingGenerationContext::FActorSetContainerInstance& Container)
		{
			const FActorContainerID ContainerId = Container.ContainerInstanceCollection->GetBaseContainerInstance()->GetContainerID();

			Container.ActorDescViewMap->ForEachActorDescView([&](const FStreamingGenerationActorDescView& ActorDescView)
				{
					const FWorldPartitionActorDescInstance* ActorDescInstance = ActorDescView.GetActorDescInstance();
					if (!ActorDescInstance)
					{
						return;
					}

					if (ActorDescInstance->GetActorNativeClass()->IsChildOf(ALandscapeStreamingProxy::StaticClass()))
					{
						FindOrAddMutator(OutMutators, ContainerId, ActorDescInstance->GetGuid()).bIsSpatiallyLoaded = false;
						UE_LOG(LogAvaStreamingGeneration, Verbose, TEXT("Overriding spatially loaded for actor '%s'"), *ActorDescInstance->GetActorLabelOrName().ToString());
					}
				});
		});
}

**Assistant:** Je vais regarder le fichier pour ajouter la condition au bon endroit.

<details><summary>Tools used</summary>

- `Glob` **/AvaStreamingGenerationMutator.cpp
- `Shell` List workspace contents
- `Shell` List workspace folder contents
- `Shell` List workspace folder contents
- `Shell` List workspace contents via cmd

</details>

**Assistant:** Le workspace est vide — le fichier `AvaStreamingGenerationMutator.cpp` n'est pas présent localement. Je vais quand même te proposer la modification basée sur le code que tu as collé.

Avant ça, j'ai une question pour bien cibler ton intention : tu veux un `if` qui *match* spécifiquement cet asset path pour pouvoir y poser un breakpoint / log de debug, ou tu veux *modifier le comportement* (forcer un override) sur cet asset précis ?

Vu ton phrasing « trouver quand on tombe sur cet asset », je pars du principe que tu veux **un point de debug** : un `if` qui se déclenche pile sur cet asset pour pouvoir y mettre un breakpoint. Tu pourras facilement le transformer en override si besoin.

L'asset `BPP_MerlinRock_2x2x2_A_Dense_B20` est un Blueprint (préfixe `BPP_`). Lors du streaming generation, on n'a pas l'instance d'acteur — on a un `FWorldPartitionActorDescInstance`. Le bon champ à comparer, c'est la **classe de l'acteur** (`GetBaseClass()` ou `GetNativeClass()`) qui retourne le path du BP, *pas* le nom de l'acteur (qui serait une instance placée).

Voici la modif. Je l'ajoute dans `ApplyRuntimeGridRules` puisque c'est la passe principale qui itère sur tous les `ActorDescView` avec accès à l'`ActorDescInstance`.

```277:286:Source/.../AvaStreamingGenerationMutator.cpp
			Container.ActorDescViewMap->ForEachActorDescView([&](const FStreamingGenerationActorDescView& ActorDescView)
				{
					const FWorldPartitionActorDescInstance* ActorDescInstance = ActorDescView.GetActorDescInstance();
					if (!ActorDescInstance)
					{
						return;
					}

					// DEBUG: breakpoint hook for a specific asset
					static const FName DebugAssetPath(TEXT("/Game/Experimental/Levels/Dungeons/Merlin_Dungeon/Dun_MT_Depulso_02.BPP_MerlinRock_2x2x2_A_Dense_B20"));
					if (ActorDescInstance->GetBaseClass() == DebugAssetPath)
					{
						UE_LOG(LogAvaStreamingGeneration, Warning, TEXT("[DEBUG] Hit target asset for actor '%s' (Guid=%s)"), *ActorDescInstance->GetActorLabelOrName().ToString(), *ActorDescInstance->GetGuid().ToString());
					}

					WorldPartitionRules::FActorOrDesc ActorOrDesc(ActorDescInstance);
```

Quelques notes importantes :

- **Quel champ comparer ?** Pour un Blueprint, l'`ActorDescInstance` expose typiquement :
  - `GetBaseClass()` → renvoie le `FTopLevelAssetPath` du BP générant l'acteur (c'est ce que tu veux pour `BPP_...`)
  - `GetNativeClass()` → la classe C++ parente (genre `AStaticMeshActor`), pas utile ici
  - `GetActorSoftPath()` → le path de l'**instance** placée, pas du BP
  
  Si `GetBaseClass()` ne compile pas ou renvoie autre chose dans ta version d'UE, dis-le moi et je t'adapte (les API ont varié entre 5.3 / 5.4 / 5.5).

- **Forme du path** : un `FTopLevelAssetPath` se compare bien avec `FName` ou `FString`. La string que tu m'as donnée (`/Game/.../Dun_MT_Depulso_02.BPP_MerlinRock_2x2x2_A_Dense_B20`) est exactement le format `Package.Object` qu'utilise `FTopLevelAssetPath::ToString()`. Si la comparaison directe `FName` foire, utilise plutôt :

```cpp
if (ActorDescInstance->GetBaseClass().ToString() == TEXT("/Game/Experimental/Levels/Dungeons/Merlin_Dungeon/Dun_MT_Depulso_02.BPP_MerlinRock_2x2x2_A_Dense_B20"))
```

- **Où poser le breakpoint** : le `UE_LOG` te confirme déjà le hit, mais tu peux mettre le breakpoint directement sur la ligne du `UE_LOG` ou la ligne du `if`.

Tu veux que je :
1. Le mette dans une autre passe aussi (`ApplyInteriorStreamingSetting`, `ApplyIsSpatiallyLoadedRules`, `PropagateMutatorsAcrossActorSets`) ?
2. Le transforme en *override* (forcer un `RuntimeGrid` ou `bIsSpatiallyLoaded` sur cet asset précis) plutôt qu'un simple log ?
3. Étende le match à *tous* les acteurs dérivés de ce BP (children) avec `IsChildOf` ?
