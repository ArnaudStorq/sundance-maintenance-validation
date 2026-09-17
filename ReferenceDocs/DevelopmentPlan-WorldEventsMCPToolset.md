Parent: [Reference Docs](README.md)

# Development Plan — World Events MCP Toolsets

*Exposing the whole World Events system (Locators, Possible World Event Definitions,
Definitions, Conditions, Data Layers, deletion, runtime state) to AI agents through the
`ToolsetRegistry` / `ModelContextProtocol` pipeline.*
## Contents

- [1. Goal](#1-goal)
  - [Why this system is a good MCP candidate](#why-this-system-is-a-good-mcp-candidate)
- [2. System recap (grounded in the code)](#2-system-recap-grounded-in-the-code)
  - [Runtime — module `Sundance`, folder `Source/Sundance/WorldEvents/`](#runtime--module-sundance-folder-sourcesundanceworldevents)
  - [Editor — module `SundanceEditor`, folder `Source/SundanceEditor/WorldEvents/`](#editor--module-sundanceeditor-folder-sourcesundanceeditorworldevents)
  - [The authoring pipeline that a tool must reproduce](#the-authoring-pipeline-that-a-tool-must-reproduce)
- [3. Architecture](#3-architecture)
  - [3.1 One family, nine toolsets](#31-one-family-nine-toolsets)
  - [3.2 Layout](#32-layout)
  - [3.3 Addressing: the hardest design decision](#33-addressing-the-hardest-design-decision)
  - [3.4 Conventions inherited from the codebase](#34-conventions-inherited-from-the-codebase)
- [4. Tool catalogue](#4-tool-catalogue)
  - [4.1 `WorldEventDiscoveryToolset` (Read)](#41-worldeventdiscoverytoolset-read)
  - [4.2 `WorldEventValidationToolset` (Read)](#42-worldeventvalidationtoolset-read)
  - [4.3 `WorldEventDefinitionToolset` (Read/Write)](#43-worldeventdefinitiontoolset-readwrite)
  - [4.4 `WorldEventLocatorAuthoringToolset` (Write)](#44-worldeventlocatorauthoringtoolset-write)
  - [4.5 `WorldEventConditionToolset` (Read/Write)](#45-worldeventconditiontoolset-readwrite)
  - [4.6 `WorldEventDeletionToolset` (Write/Execute)](#46-worldeventdeletiontoolset-writeexecute)
  - [4.7 `WorldEventViewportToolset` (Write)](#47-worldeventviewporttoolset-write)
  - [4.8 `WorldEventRuntimeToolset` (Execute, PIE, non-shipping)](#48-worldeventruntimetoolset-execute-pie-non-shipping)
  - [4.9 `WorldEventExportJobToolset` (Execute, async)](#49-worldeventexportjobtoolset-execute-async)
  - [4.10 `UWorldEventAuthoringSkill`](#410-uworldeventauthoringskill)
- [5. Refactoring required in the existing code](#5-refactoring-required-in-the-existing-code)
  - [5.1 Extract headless entry points](#51-extract-headless-entry-points)
  - [5.2 Preview and mode state](#52-preview-and-mode-state)
  - [5.3 Deletion session lifetime](#53-deletion-session-lifetime)
  - [5.4 Saving policy, and the one place it bends](#54-saving-policy-and-the-one-place-it-bends)
  - [5.5 Runtime subsystem access](#55-runtime-subsystem-access)
- [6. Shared types](#6-shared-types)
- [7. Phasing](#7-phasing)
- [8. Testing](#8-testing)
- [9. Risks and guard-rails](#9-risks-and-guard-rails)
- [10. Deliverables](#10-deliverables)
  - [New files — `D:\Sun\Sundance\Source\SundanceEditor\WorldEvents\Toolset\`](#new-files--dsunsundancesourcesundanceeditorworldeventstoolset)
  - [Modified files](#modified-files)
  - [Documentation in this repo](#documentation-in-this-repo)
- [11. Open questions](#11-open-questions)

---


---

## 1. Goal

Today the World Events system is only reachable through Slate: a dedicated editor mode
(`EM_WorldEventEditorMode`), a drag-and-drop widget, two viewport context menus, a details
panel customization, a deletion wizard, and an ImGui runtime debugger. None of it is
callable by an agent, and almost none of it is callable by a script.

This plan adds a family of MCP toolsets that make the system fully **discoverable**,
**auditable**, **authorable**, and **debuggable** from an agent, following the conventions
already established by `WorldBuildingEditor.WorldPartitionDataLayerInstanceToolset`,
`WorldBuildingEditor.HLODBuildToolset`, `SundanceEditor.MissionToolset` and
`LevelLogicEditor.LevelLogicToolset`.

### Why this system is a good MCP candidate

- **It is a web of references, not one asset.** Placing one World Event creates a locator
  actor, one `AWorldEventInstance` (Level Instance) per possible definition, a
  `UDataLayerAsset`, and one or two `UDataLayerInstance`. Answering "what exists and is it
  consistent?" by hand means walking four different editors.
- **The consistency rules are implicit.** Naming prefixes live in
  `UWorldEventEditorSettings`, data layer placement is decided by the DataLayer rule
  subsystem, and validation exists (`AWorldEventLocator::IsDataValid`) but only writes to
  the log.
- **The expensive operations are already headless.** `FWorldEventDeleter` is a step-based,
  Slate-free orchestrator with a plan, a rollback and Perforce handling — it was written
  to be driven by a UI, but nothing stops a tool from driving it.
- **Selection at runtime is opaque.** A locator shuffles `PossibleWorldEvents` and takes
  the first definition whose conditions pass. "Why did this event not spawn?" currently
  requires reading `DEBUG_*` arrays in an ImGui window.

---

## 2. System recap (grounded in the code)

Source of truth for the plan below.

### Runtime — module `Sundance`, folder `Source/Sundance/WorldEvents/`

| Type | Header | Role |
| --- | --- | --- |
| `UWorldEventDefinition` | `WorldEventDefinition.h` | `UDataAsset`. `WorldEventTag`, `FriendlyName`, `WorldEventLevel`, `Conditions`, `WorldEventActorComponentsNeededTags`, `bActivatesOnPlayerProximity`, `PlayerDistanceToActivate`, private `GuidString`. |
| `AWorldEventLocator` | `WorldEventLocator.h` | **Abstract** actor. `PossibleWorldEvents`, `Conditions`, `LocatorTags`, `LocationBounds`, `DebugPlayerTeleportLocation`, `GuidString`, `WorldEventInstanceActorGuids`. |
| `FLocalizedWorldEventDefinition` | `WorldEventLocator.h` | **This is the "Possible World Event Definition"**: `WorldEventDefinition`, `DataLayer`, `DisplayedName`, private `WorldEventInstanceActorGuid`. |
| `AWorldEventInstance` | `WorldEventInstance.h` | `ALevelInstance` spawned per possible definition, named `LI_WE_<locator>_<definition>`. |
| `UWorldEventSubsystem` | `WorldEventSubsystem.h` | Spawn queue, active/inactive locators, persisted `FWorldEventRuntimeData` per tag. |
| `UWorldEventActorComponent` | `WorldEventActorComponent.h` | Socket component inside the World Event level: proximity, camera trigger, seen/interacted. |
| `AWorldEventAggregateActor` | `WorldEventAggregateActor.h` | Builds `FWorldEventInfo[]` from World Partition actor descriptors (sees unloaded locators). |
| `FWorldEventLocatorDesc` | `WorldEventLocatorDesc.h` | The actor descriptor that makes the above possible. |
| `USunWorldEventCondition` + 12 subclasses | `Conditions/` | Instanced gating: `Cooldown`, `GroupCooldown`, `OnlyOnce`, `RandomChance`, `DistanceToActiveEvents`, `RuntimeData`, `MultipleRuntimeData`, `MissionStatus`, `MissionStatusAnyOf`, `GameTimeSinceMissionCompletion`, `SpellLearned`. |
| `EWorldEventProgressState` | `WorldEventTypes.h` | `Invalid` → `Spawned` → `Initialized` → `Activated` → `Ended`/`Canceled`/`AutomatedTest`. |

### Editor — module `SundanceEditor`, folder `Source/SundanceEditor/WorldEvents/`

| Type | Header | Role |
| --- | --- | --- |
| `UWorldEventEditorSettings` | `WorldEventEditorSettings.h` | `DataLayerRuleAsset`, `WorldEventParentDataLayerName`, prefixes (`WEL_`, `LI_WE_`, `DL_WE_`, `WEDA_`), `LevelDataLayerPaths`, `DefaultLocatorActorSoftPath`, `LinkedActorClassesToIgnore`. |
| `FWorldEventEditorMode` / `FWorldEventEditorModeToolkit` | `EditorMode/` | The mode, its Locators / Tools tabs, overlay toggles, `ValidateAllLocators`. |
| `FWorldEventEditorHelpers` | `EditorMode/WorldEventEditorHelpers.h` | Data layer resolution, `GetAllWorldEventDefinitionAssets`. |
| `FWorldEventEditorMenuExtender` | `EditorMode/WorldEventEditorMenuExtender.h` | `AddWorldEventDefinitionToSelectedLocators`, `SetDataLayerToSelectedActors`. |
| `FWorldEventDeleter` / `FWorldEventDeletionPlan` | `EditorMode/Deletion/WorldEventDeleter.h` | Plan + 9 ordered steps + `Rollback` + changelist. Slate-free. |
| `UWorldEventExportCommandlet` | `Commandlets/` | JSON inventory of locators for a map, recursing into Level Instances. |

### The authoring pipeline that a tool must reproduce

Assigning a `UWorldEventDefinition` into `PossibleWorldEvents` triggers
`FLocalizedWorldEventDefinition::UpdateDataLayerWorldInstance`, which:

1. destroys the previous `AWorldEventInstance` if any;
2. spawns a new one at the locator, labelled by `FWorldEventHelpers::CreateLevelInstanceName`;
3. `SetWorldAsset(Definition->WorldEventLevel)`;
4. resolves the target data layer name through `UDataLayerRuleSubsystem::GetTargetDataLayer`
   using `UWorldEventEditorSettings::DataLayerRuleAsset`;
5. creates or finds the `UDataLayerAsset` (`ResolveMissingDataLayerAsset`);
6. creates or finds the `UDataLayerInstance` under `DL_WORLD_EVENTS`
   (`ResolveMissingDataLayerInstance`);
7. applies the World Partition rules on the instance;
8. writes `DataLayer` back and saves the locator.

`AWorldEventLocator::CanEditChange` gates step 1 on the `WorldDataLayers` being
checkout-able — the data-safety fix described in
[World Events (work done)](../WorkDoneByTopic/WorldEvents.md).

---

## 3. Architecture

### 3.1 One family, nine toolsets

A single monolithic toolset would be unusable: the registry advertises every tool of a
loaded toolset, and mixing a read-only inventory with a destructive Perforce operation in
one description makes both harder for an agent to reason about. The codebase already
splits by intent (`RuleAudit` / `RuleAuthoring` / `RuleFix` / `RuleBuild`), so mirror that.

| # | Toolset | Access | Purpose |
| --- | --- | --- | --- |
| 1 | `SundanceEditor.WorldEventDiscoveryToolset` | Read | What exists: locators, possible events, definitions, instances, data layers, reverse lookups, spatial queries. |
| 2 | `SundanceEditor.WorldEventValidationToolset` | Read | Audit: data validity, naming conventions, dangling references, orphan data layers, unreachable definitions, socket coverage. |
| 3 | `SundanceEditor.WorldEventDefinitionToolset` | Read/Write | The `WEDA_*` data assets: read, create, edit, duplicate, validate. |
| 4 | `SundanceEditor.WorldEventLocatorAuthoringToolset` | Write | Locators and their possible events: create, rename, move, bounds, tags, add/remove possible definition, repair data layer wiring. |
| 5 | `SundanceEditor.WorldEventConditionToolset` | Read/Write | The instanced condition arrays on locators and definitions, plus a schema so an agent can author a condition it has never seen. |
| 6 | `SundanceEditor.WorldEventDeletionToolset` | Write/Execute | Drives `FWorldEventDeleter`: plan, execute, rollback, changelist. |
| 7 | `SundanceEditor.WorldEventViewportToolset` | Write | Editor mode, active locator, definition preview, data layer context, overlays, camera focus. |
| 8 | `SundanceEditor.WorldEventRuntimeToolset` | Execute | PIE only, non-shipping: progress states, why a locator did or did not spawn, force spawn, reroll, teleport, runtime counters. |
| 9 | `SundanceEditor.WorldEventExportJobToolset` | Execute | Async `WorldEventExportCommandlet` jobs for cross-map inventory without opening a map. |

Plus one `UAgentSkill`: **`UWorldEventAuthoringSkill`**.

> Toolsets 7 and 8 could be folded into 1 and 6 if nine entries prove too many in
> `list_toolsets`. Keep them separate through Phase 8 and revisit; the cost of splitting
> later is a rename, the cost of merging later is a behavioural surprise.

### 3.2 Layout

```
D:\Sun\Sundance\Source\SundanceEditor\WorldEvents\Toolset\
├── WorldEventToolsetTypes.h                   Shared USTRUCTs (no .cpp)
├── WorldEventToolsetCommon.h / .cpp            Fail(), IsUnset(), resolvers, formatters
├── WorldEventAuthoringSkill.h                  UAgentSkill
├── WorldEventDiscoveryToolset.h / .cpp
├── WorldEventValidationToolset.h / .cpp
├── WorldEventDefinitionToolset.h / .cpp
├── WorldEventLocatorAuthoringToolset.h / .cpp
├── WorldEventConditionToolset.h / .cpp
├── WorldEventDeletionToolset.h / .cpp
├── WorldEventViewportToolset.h / .cpp
├── WorldEventRuntimeToolset.h / .cpp
└── WorldEventExportJobToolset.h / .cpp
```

**No `.Build.cs` change is required.** `SundanceEditor.Build.cs` already declares
`AvaCoreEditor` (line 59), `ToolsetRegistry` and `ToolsetRegistryEditor` (lines 186–187),
and `Sundance.uproject` already enables `ToolsetRegistry`, `ModelContextProtocol` and
`AIAssistant`.

Each `.cpp` carries, exactly as `MissionToolset.cpp` does:

```cpp
#include "Registration/ToolsetRegistration.h"
AUTO_REGISTER_TOOLSET(UWorldEventDiscoveryToolset, UE_MODULE_NAME)
```

### 3.3 Addressing: the hardest design decision

A locator has three candidate identities and none is sufficient alone:

| Identity | Stable across | Problem |
| --- | --- | --- |
| Actor label (`WEL_Foo`) | Nothing | Renameable, not guaranteed unique. |
| `GuidString` | Renames, reloads, Level Instance in-context edit | Opaque to a human; not visible in the Outliner. |
| Actor `FGuid` (World Partition) | Renames | Changes meaning inside a Level Instance. |

`FWorldEventDeleter` already solved this: it stores `LocatorGuid` because entering a Level
Instance edit reloads the level and invalidates every pointer. Adopt the same rule.

```cpp
/**
 * Identifies one AWorldEventLocator. Pass whichever field you have.
 *
 * GuidString is the only identity stable across a level reload or a Level Instance
 * in-context edit, so every tool that returns a locator returns it, and every tool that
 * takes a locator prefers it. Label is accepted for convenience and rejected as ambiguous
 * when more than one locator carries it.
 */
USTRUCT(BlueprintType)
struct FWorldEventLocatorRef
{
    GENERATED_BODY()

    /** AWorldEventLocator::GetGuidString(). Preferred. */
    UPROPERTY(BlueprintReadWrite, Category = "WorldEvent")
    FString GuidString;

    /** Actor label, e.g. WEL_ForestAmbush_01. Used only when GuidString is empty. */
    UPROPERTY(BlueprintReadWrite, Category = "WorldEvent")
    FString Label;
};
```

A **possible world event** is addressed by `FWorldEventLocatorRef` + one of:
- `DefinitionAssetPath` (unambiguous unless the same definition is listed twice), or
- `Index` into `PossibleWorldEvents` (stable within one call chain, not across edits).

Tools accept both and report which they resolved. Ambiguity is a `Fail()`, never a guess.

### 3.4 Conventions inherited from the codebase

| Convention | Rule |
| --- | --- |
| Base class | `UToolsetDefinition`, `UCLASS(BlueprintType, MinimalAPI)`. |
| Tools | `static` `UFUNCTION(meta = (AICallable, AIAccessMode = "Read"\|"Write"\|"Execute"))`. |
| Descriptions | Doc comments. Multi-paragraph on the class, `@param` per argument. |
| Dry run | `bool bApply = false` last, on every mutating tool. Nothing is written until true. |
| Errors | `UKismetSystemLibrary::RaiseScriptError` via a local `Fail()`. Never exceptions. |
| Refusals | A change the engine legitimately declines returns `bApplied = false` + `Detail`, **not** an error — the reason is usually the answer. |
| Undo | One `FScopedTransaction` per mutating tool. |
| Saving | Leave packages dirty; report `ModifiedPackage`. Exceptions documented in §5.4. |
| Submitting | Never. No tool takes a free-form command line or passes `-AutoSubmit`. |
| Sentinels | `"All"` for "no filter", `"Convention"` for "use the declared default" — empty strings get dropped from the JSON schema. |
| Caps | `MaxResults` with a documented default on every list tool. |

---

## 4. Tool catalogue

Signatures are the deliverable contract. Bodies are described where the work is not
obvious.

### 4.1 `WorldEventDiscoveryToolset` (Read)

Answers "what World Events exist here?" without loading anything it does not have to.

```cpp
/**
 * Every AWorldEventLocator in the open level, one row per locator.
 *
 * Reads World Partition actor descriptors first (FWorldEventLocatorDesc), so unloaded
 * locators are reported without being loaded. Fields that only exist on a loaded actor -
 * the resolved DataLayer of each possible event, the LocationBounds extent - come back
 * empty for an unloaded locator, and bIsLoaded tells you which case you are in. Call
 * LoadLocators when you need them.
 *
 * @param NameFilter Substring of the locator label, case-insensitive. Empty or "All" returns everything.
 * @param TagFilter GameplayTag under WorldEvent that must be present on the locator or one of its definitions. "All" for no filter.
 * @param MaxResults Cap on returned rows. 0 means no cap.
 */
static TArray<FWorldEventLocatorSummary> ListWorldEventLocators(
    const FString& NameFilter = TEXT("All"),
    const FString& TagFilter = TEXT("All"),
    int32 MaxResults = 200);

/** Full detail for one locator: possible events, conditions, bounds, instances, data layers, validity. */
static FWorldEventLocatorDetail GetWorldEventLocator(const FWorldEventLocatorRef& Locator);

/**
 * The locator -> possible event -> level instance tree, parents before children, the same
 * shape as the Locators tab of the World Events editor mode.
 */
static TArray<FWorldEventTreeNode> GetWorldEventTree(
    const FString& NameFilter = TEXT("All"),
    int32 MaxResults = 500);

/** The possible world events of one locator, in array order, with their resolved data layer and level instance. */
static TArray<FWorldEventPossibleEvent> ListPossibleWorldEvents(const FWorldEventLocatorRef& Locator);

/**
 * Every UWorldEventDefinition asset in the project, from the asset registry.
 *
 * WorldEventTag is an AssetRegistrySearchable tag, so filtering by tag costs nothing and
 * loads no asset.
 */
static TArray<FWorldEventDefinitionSummary> ListWorldEventDefinitions(
    const FString& NameFilter = TEXT("All"),
    const FString& TagFilter = TEXT("All"),
    int32 MaxResults = 200);

/**
 * Which locators list a given definition. The reverse of ListPossibleWorldEvents, and the
 * question to ask before editing or deleting a definition: they are shared.
 */
static TArray<FWorldEventLocatorSummary> FindLocatorsUsingDefinition(const FString& DefinitionAssetPath);

/**
 * Locators within Radius of a world-space point, nearest first.
 *
 * Descriptor-based, so it covers unloaded locators. This is how you answer "what is
 * around here" for a bug report that only carries coordinates.
 */
static TArray<FWorldEventLocatorSummary> FindWorldEventLocatorsNearLocation(
    FVector Location, float Radius, int32 MaxResults = 50);

/** Locators whose position falls inside a named World Partition region, e.g. MFF_05. */
static TArray<FWorldEventLocatorSummary> FindWorldEventLocatorsInRegion(const FString& RegionName);

/** Every DL_WE_* data layer asset and instance the system created, with the locator and definition that own it. */
static TArray<FWorldEventDataLayerBinding> ListWorldEventDataLayers(const FString& NameFilter = TEXT("All"));

/**
 * Counts, not rows: locators, possible events, definitions in use versus on disk,
 * definitions per locator distribution, condition-class histogram, locators with no
 * possible event, definitions no locator references.
 *
 * Start here to size a problem before listing it.
 */
static FWorldEventInventoryStats GetWorldEventInventoryStats();

/**
 * Force-load a set of locators and their World Event Instances so loaded-only fields and
 * the actors inside the World Event level become readable.
 *
 * Uses World Partition pinning, the same mechanism FWorldEventDeleter::Analyze uses, and
 * pairs with UnloadLocators. Leaving locators pinned leaves the editor holding them.
 */
static FWorldEventLoadResult LoadLocators(const TArray<FWorldEventLocatorRef>& Locators);
static FWorldEventLoadResult UnloadLocators(const TArray<FWorldEventLocatorRef>& Locators);
```

### 4.2 `WorldEventValidationToolset` (Read)

Turns `IsDataValid` and the naming conventions from log output into structured findings.
This is the toolset that pays for itself on day one.

```cpp
/**
 * Every World Event problem in the open level, one row per finding.
 *
 * Aggregates AWorldEventLocator::IsDataValid (the same checks the editor mode's
 * "Validate All Locators" button logs), UWorldEventDefinition::IsDataValid for every
 * referenced definition, and the structural checks below that nothing currently performs:
 *
 *   MissingDefinition        a possible event with no WorldEventDefinition set
 *   MissingDataLayer         a possible event whose DataLayer never resolved
 *   DanglingInstance         WorldEventInstanceActorGuids points at an actor that is gone
 *   OrphanInstance           an LI_WE_* actor no locator claims
 *   OrphanDataLayerAsset     a DL_WE_* asset no possible event references
 *   MisplacedDataLayer       a WE data layer instance outside WorldEventParentDataLayerName
 *   DuplicateCooldown        two cooldown conditions on one definition (also an IsDataValid error)
 *   DuplicateDefinition      the same definition listed twice on one locator
 *   EmptyLocator             a locator with no possible events - it can never spawn
 *   UnreachableDefinition    every possible event gated by a condition that cannot pass
 *   MissingSocket            WorldEventActorComponentsNeededTags no component in the level provides
 *   NamingConvention         a label or asset name that breaks the prefixes in UWorldEventEditorSettings
 *   InvalidBounds            zero-extent LocationBounds, which silently disables bounds-based socket registration
 *
 * Severity is Error for anything that stops the event working and Warning for anything
 * that only makes it wrong. Silence means these checks passed, not that the content is
 * good.
 *
 * @param LocatorFilter Substring of the locator label. Empty or "All" audits everything.
 * @param CheckFilter One check name from the list above, or "All".
 */
static TArray<FWorldEventFinding> AuditWorldEvents(
    const FString& LocatorFilter = TEXT("All"),
    const FString& CheckFilter = TEXT("All"));

/** The findings for one locator, including the ones AuditWorldEvents caps away. */
static TArray<FWorldEventFinding> ValidateWorldEventLocator(const FWorldEventLocatorRef& Locator);

/** IsDataValid plus the reachability analysis for one definition asset. */
static TArray<FWorldEventFinding> ValidateWorldEventDefinition(const FString& DefinitionAssetPath);

/**
 * Whether one locator could ever spawn one of its possible events, and what would stop it.
 *
 * Static analysis of the condition arrays, not a runtime evaluation: it reports conditions
 * that can never pass (RandomChance of 0, OnlyOnce already consumed in the persisted data
 * when that data is available, a MissionStatus naming a mission that does not exist) and
 * the order in which they are evaluated. For an actual evaluation use
 * WorldEventRuntimeToolset.ExplainLocatorSpawn during PIE.
 */
static FWorldEventSpawnabilityReport AnalyzeLocatorSpawnability(const FWorldEventLocatorRef& Locator);

/** The same audit rendered as Markdown, for chat display. Never a payload for a wiki page write. */
static FString GetWorldEventAuditAsMarkdown(const FString& LocatorFilter = TEXT("All"));
```

### 4.3 `WorldEventDefinitionToolset` (Read/Write)

```cpp
/** Every property of one UWorldEventDefinition, including its conditions and its GuidString. */
static FWorldEventDefinitionDetail GetWorldEventDefinition(const FString& DefinitionAssetPath);

/**
 * Create a UWorldEventDefinition asset.
 *
 * The asset is saved and marked for add, not left dirty: an unsaved definition cannot be
 * referenced by a locator, so the usual "leave it dirty" rule would produce a definition
 * that appears to exist and cannot be used. This mirrors MissionToolset's create path.
 * Submitting is still a human step.
 *
 * @param PackagePath Content folder, e.g. /Game/WorldEvents/Definitions.
 * @param AssetName Name without prefix; WorldEventDataAssetPrefix from UWorldEventEditorSettings is prepended when absent.
 * @param WorldEventTag GameplayTag under WorldEvent. Required: IsDataValid rejects a definition without one.
 * @param WorldEventLevelPath The UWorld this event streams in. May be empty and set later.
 * @param bApply Nothing is created until this is true.
 */
static FWorldEventDefinitionChange CreateWorldEventDefinition(
    const FString& PackagePath, const FString& AssetName, const FString& WorldEventTag,
    const FString& WorldEventLevelPath, bool bApply = false);

/**
 * Patch the scalar properties of a definition. Only the fields you name are touched.
 *
 * Editing a definition changes every locator that lists it. Call
 * WorldEventDiscoveryToolset.FindLocatorsUsingDefinition first and say how many locators
 * are affected before applying.
 */
static FWorldEventDefinitionChange SetWorldEventDefinitionProperties(
    const FString& DefinitionAssetPath, const FWorldEventDefinitionPatch& Patch, bool bApply = false);

/** Add or remove a required socket tag in WorldEventActorComponentsNeededTags. */
static FWorldEventDefinitionChange SetWorldEventDefinitionNeededTags(
    const FString& DefinitionAssetPath, const TArray<FString>& NeededTags, bool bApply = false);

/**
 * Copy a definition, including its instanced conditions, under a new name.
 *
 * The copy gets an empty GuidString, which PreSave regenerates, so the two assets do not
 * share an identity in the runtime database.
 */
static FWorldEventDefinitionChange DuplicateWorldEventDefinition(
    const FString& SourceAssetPath, const FString& NewAssetName, bool bApply = false);

/** GameplayTags under the WorldEvent category that no definition uses, and tags used by more than one definition. */
static FWorldEventTagReport AuditWorldEventTags();
```

### 4.4 `WorldEventLocatorAuthoringToolset` (Write)

The toolset that needs the most refactoring behind it (§5).

```cpp
/**
 * Place a new World Event Locator.
 *
 * Spawns the Blueprint named by UWorldEventEditorSettings::DefaultLocatorActorSoftPath,
 * because AWorldEventLocator is abstract, and labels it with WorldEventLocatorPrefix. This
 * is the drag-and-drop path of the editor mode's Tools tab without the modal name prompt.
 *
 * The locator's package is left dirty. A locator with no possible events can never spawn,
 * so follow this with AddPossibleWorldEvent.
 *
 * @param Location World-space position.
 * @param Name Name without prefix. WorldEventLocatorPrefix is prepended when absent.
 * @param bApply Nothing is spawned until this is true.
 */
static FWorldEventLocatorChange CreateWorldEventLocator(
    FVector Location, const FString& Name, bool bApply = false);

/**
 * Add a possible world event to a locator: the operation the "Add New Possible World Event
 * Definition" context menu performs.
 *
 * This is not a simple array append. Assigning the definition runs the data layer pipeline:
 * an AWorldEventInstance is spawned and pointed at the definition's level, the target data
 * layer name is resolved through the DataLayer rule asset, the UDataLayerAsset and its
 * UDataLayerInstance are created under WorldEventParentDataLayerName if missing, and the
 * World Partition rules are applied. Expect four to five dirty packages, listed in the
 * result.
 *
 * PRECONDITION, enforced and reported rather than assumed: the level's WorldDataLayers must
 * be available for check out and up to date. The pipeline writes to it, and the check exists
 * because a stale WorldDataLayers used to corrupt on write. Checkout is automatic; nothing
 * is submitted.
 *
 * @param bApply Nothing is created until this is true. The dry run reports every asset that would be created.
 */
static FWorldEventPossibleEventChange AddPossibleWorldEvent(
    const FWorldEventLocatorRef& Locator, const FString& DefinitionAssetPath, bool bApply = false);

/**
 * Remove one possible world event from a locator, and the AWorldEventInstance it created.
 *
 * The DataLayerAsset and its instance are deliberately left alone: they may be shared, and
 * removing them is what WorldEventDeletionToolset does under Perforce supervision. Run
 * WorldEventValidationToolset.AuditWorldEvents afterwards to see whether one became an
 * OrphanDataLayerAsset.
 *
 * To remove the whole locator use WorldEventDeletionToolset.DeleteWorldEvent - deleting a
 * locator by hand leaves dangling data layers.
 */
static FWorldEventPossibleEventChange RemovePossibleWorldEvent(
    const FWorldEventLocatorRef& Locator, const FString& DefinitionAssetPath,
    int32 Index = -1, bool bApply = false);

/**
 * Reorder PossibleWorldEvents.
 *
 * Order is not cosmetic but it is not priority either: the locator shuffles this array
 * before evaluating it, so reordering changes nothing at runtime. It changes the editor
 * tree and the details panel. Said explicitly because "move it to the top so it wins" is
 * the obvious wrong assumption.
 */
static FWorldEventPossibleEventChange ReorderPossibleWorldEvents(
    const FWorldEventLocatorRef& Locator, const TArray<FString>& DefinitionAssetPathsInOrder,
    bool bApply = false);

/** Rename a locator, keeping the prefix. GuidString is unaffected, so held references stay valid. */
static FWorldEventLocatorChange RenameWorldEventLocator(
    const FWorldEventLocatorRef& Locator, const FString& NewName, bool bApply = false);

/**
 * Move a locator, and its World Event Instances with it.
 *
 * The instances are placed at the locator, so moving the locator alone desynchronises them.
 * This moves the set. Sockets that register through LocationBounds change membership as a
 * result; the result lists which ones.
 */
static FWorldEventLocatorChange SetWorldEventLocatorTransform(
    const FWorldEventLocatorRef& Locator, FVector NewLocation, FRotator NewRotation,
    bool bMoveInstances = true, bool bApply = false);

/**
 * Set the LocationBounds extent.
 *
 * LocationBounds decides which UWorldEventActorComponent registers with this locator by
 * position rather than by data layer. A zero extent silently disables that path, which is
 * the InvalidBounds finding.
 */
static FWorldEventLocatorChange SetWorldEventLocatorBounds(
    const FWorldEventLocatorRef& Locator, FVector BoxExtent, bool bApply = false);

/** Replace LocatorTags. Tags must be under the WorldEvent category. */
static FWorldEventLocatorChange SetWorldEventLocatorTags(
    const FWorldEventLocatorRef& Locator, const TArray<FString>& Tags, bool bApply = false);

/** Set DebugPlayerTeleportLocation, the point the runtime debugger teleports the player to. */
static FWorldEventLocatorChange SetWorldEventLocatorTeleportLocation(
    const FWorldEventLocatorRef& Locator, FVector TeleportLocation, bool bApply = false);

/**
 * Re-run the data layer pipeline for possible events whose DataLayer or WorldEventInstance
 * did not resolve - the MissingDataLayer and DanglingInstance findings.
 *
 * Idempotent: a possible event that is already correct is skipped and reported as such. Fix
 * the cause first when the cause is a missing DataLayerRuleAsset, or this will keep failing
 * the same way.
 */
static TArray<FWorldEventPossibleEventChange> RepairWorldEventDataLayers(
    const FWorldEventLocatorRef& Locator, bool bApply = false);

/**
 * Assign the World Event data layer of a possible event to actors, the "Set World Event Data
 * Layer" context menu without needing a viewport selection.
 *
 * Removes any other DL_WE_* layer from each actor first, which is what the menu does and
 * what stops an actor belonging to two World Events.
 */
static TArray<FWorldEventActorDataLayerChange> SetWorldEventDataLayerOnActors(
    const FWorldEventLocatorRef& Locator, const FString& DefinitionAssetPath,
    const TArray<FString>& ActorPaths, bool bApply = false);
```

### 4.5 `WorldEventConditionToolset` (Read/Write)

Conditions are `Instanced` `UObject` arrays with per-class properties, so a fixed schema
cannot describe them. Expose the schema as data — the same problem
`SceneRigToolset` solves by telling agents to call `list_properties` first.

```cpp
/**
 * Every USunWorldEventCondition subclass that can be added, with its editable properties,
 * types, defaults, and what it gates on.
 *
 * Call this before AddCondition: property names vary per class and cannot be guessed. There
 * are eleven concrete classes today and the list is discovered from the class hierarchy, so
 * a new one appears here without this toolset changing.
 */
static TArray<FWorldEventConditionSchema> ListConditionTypes();

/** The conditions on a locator (gate the whole locator) or on a definition (gate one possible event). */
static TArray<FWorldEventConditionDetail> GetLocatorConditions(const FWorldEventLocatorRef& Locator);
static TArray<FWorldEventConditionDetail> GetDefinitionConditions(const FString& DefinitionAssetPath);

/**
 * Add a condition instance.
 *
 * Locator conditions gate every possible event; definition conditions gate that definition
 * everywhere it is listed. Choosing the wrong one is the most common authoring mistake in
 * this system, so the result restates which array was written and how many locators the
 * change reaches.
 *
 * Two cooldown conditions on one definition is an IsDataValid error; adding a second one is
 * refused with that reason.
 *
 * @param ConditionClass Class name from ListConditionTypes, e.g. SunWorldEventCondition_RandomChance.
 * @param Properties Property name to value, as reported by ListConditionTypes.
 * @param bApply Nothing is created until this is true.
 */
static FWorldEventConditionChange AddLocatorCondition(
    const FWorldEventLocatorRef& Locator, const FString& ConditionClass,
    const TMap<FString, FString>& Properties, bool bApply = false);

static FWorldEventConditionChange AddDefinitionCondition(
    const FString& DefinitionAssetPath, const FString& ConditionClass,
    const TMap<FString, FString>& Properties, bool bApply = false);

/** Patch properties on an existing condition, addressed by index. */
static FWorldEventConditionChange SetConditionProperties(
    const FWorldEventConditionOwnerRef& Owner, int32 ConditionIndex,
    const TMap<FString, FString>& Properties, bool bApply = false);

static FWorldEventConditionChange RemoveCondition(
    const FWorldEventConditionOwnerRef& Owner, int32 ConditionIndex, bool bApply = false);

/**
 * Copy the whole condition array from one owner to another, replacing or appending.
 *
 * The reason this exists: "make this event behave like that one" is the request, and doing
 * it property by property across eleven classes is where mistakes happen.
 */
static TArray<FWorldEventConditionChange> CopyConditions(
    const FWorldEventConditionOwnerRef& Source, const FWorldEventConditionOwnerRef& Destination,
    bool bReplace = true, bool bApply = false);

/**
 * Every locator and definition using a given condition class, with its property values.
 *
 * The question this answers: "which events are on a cooldown longer than a day?" - a sweep
 * no existing UI performs.
 */
static TArray<FWorldEventConditionUsage> FindConditionUsage(
    const FString& ConditionClass, int32 MaxResults = 200);
```

### 4.6 `WorldEventDeletionToolset` (Write/Execute)

A thin, honest wrapper over `FWorldEventDeleter`. The value is that the plan becomes
readable and the execution stays auditable.

```cpp
/**
 * What deleting a World Event would touch: actors, data layer instances, data layer assets,
 * and every Perforce file, plus the ordered steps that would run.
 *
 * Nothing is modified. This is FWorldEventDeleter::Analyze and the "What will be deleted"
 * section of the deletion dialog. Always show this to the human before DeleteWorldEvent.
 *
 * Analyze pins unloaded World Event Instances so they can be inspected. AbortDeletion
 * releases them; so does DeleteWorldEvent. A plan left neither executed nor aborted leaves
 * actors force-loaded.
 */
static FWorldEventDeletionPlanReport PlanWorldEventDeletion(const FWorldEventLocatorRef& Locator);

/**
 * Delete a World Event and every asset it created: the locator, its Level Instances, its
 * data layer instances, and its data layer assets.
 *
 * This is the guided deletion wizard, driven step by step, and it is the only correct way
 * to remove a World Event - deleting the locator by hand leaves dangling data layers in
 * WorldDataLayers.
 *
 * WHAT IT DOES TO YOUR EDITOR AND YOUR WORKSPACE:
 *  - It checks out files. Automatically, silently, as the dialog does.
 *  - It saves packages and marks packages for delete.
 *  - When the World Event lives inside a Level Instance it enters an in-context edit, which
 *    RELOADS THE LEVEL and invalidates every actor reference you were holding.
 *  - On failure it rolls back: every touched file is reverted, and the level is reloaded if
 *    the world was already mutated.
 *  - On success the files land in a new described changelist. IT NEVER SUBMITS.
 *
 * The reusable UWorldEventDefinition asset is not deleted; it is shared.
 *
 * @param bApply Nothing is deleted until this is true. Without it you get the plan.
 * @param bAllowLevelInstanceEdit Permit the level-reloading in-context edit path. Defaults
 *        to false, so a World Event inside a Level Instance is refused with an explanation
 *        rather than silently reloading the level under an agent.
 */
static FWorldEventDeletionResult DeleteWorldEvent(
    const FWorldEventLocatorRef& Locator, bool bAllowLevelInstanceEdit = false, bool bApply = false);

/** Release the actors PlanWorldEventDeletion pinned, without deleting anything. */
static FWorldEventDeletionResult AbortDeletion(const FWorldEventLocatorRef& Locator);

/**
 * Roll back a deletion that failed part way: revert every touched file and reload the level.
 *
 * DeleteWorldEvent already does this on failure. This is the manual escape hatch for a
 * process interrupted between steps.
 */
static FWorldEventDeletionResult RollbackDeletion(const FString& DeletionSessionId);

/** The step-by-step log of the last deletion in this session, including the changelist number. */
static FWorldEventDeletionResult GetLastDeletionReport();
```

### 4.7 `WorldEventViewportToolset` (Write)

Editor state, not content. Small, and disproportionately useful: it is how an agent shows
its work.

```cpp
/** Enter or leave the World Events editor mode. Overlays and context menus only work inside it. */
static FWorldEventViewportChange SetWorldEventEditorModeActive(bool bActive);

/** Set the active locator, which is what the "Set World Event Data Layer" menu keys off. */
static FWorldEventViewportChange SetActiveLocator(const FWorldEventLocatorRef& Locator);

/**
 * Load one possible event's data layer for preview and unload the others, the "Possible
 * Event in Preview" combo of the locator details panel.
 *
 * Preview state is editor-only and transient, but it changes what you see - clear it before
 * measuring or screenshotting anything else.
 */
static FWorldEventViewportChange SetPreviewedPossibleWorldEvent(
    const FWorldEventLocatorRef& Locator, const FString& DefinitionAssetPath);
static FWorldEventViewportChange ClearWorldEventPreview();

/** Toggle the mode's overlays: locator links, data layer labels, validation badges. */
static FWorldEventViewportChange SetWorldEventOverlays(
    bool bShowLinks, bool bShowDataLayerLabels, bool bShowValidation);

/** Point the viewport camera at a locator and select it, so a screenshot shows what is being discussed. */
static FWorldEventViewportChange FocusOnWorldEventLocator(
    const FWorldEventLocatorRef& Locator, bool bSelect = true);
```

### 4.8 `WorldEventRuntimeToolset` (Execute, PIE, non-shipping)

Guarded by `#if !UE_BUILD_SHIPPING`, and every tool fails cleanly with "no PIE session"
outside one. This is the ImGui debugger, made callable.

```cpp
/** Whether a PIE session with a UWorldEventSubsystem exists, the global enable state, and the counts. */
static FWorldEventRuntimeStatus GetWorldEventRuntimeStatus();

/**
 * Locators the subsystem is tracking, with progress state, the definition that won, and the
 * registered socket components.
 *
 * @param StateFilter One EWorldEventProgressState name, "Active" for anything past Spawned, or "All".
 */
static TArray<FWorldEventRuntimeLocator> ListRuntimeLocators(const FString& StateFilter = TEXT("All"));

/**
 * Why a locator did or did not spawn: every locator condition and every definition
 * condition, in evaluation order, with its pass/fail result and the reason string.
 *
 * These are the DEBUG_LocatorConditionResults and DEBUG_DefinitionConditionResults arrays
 * the ImGui debugger shows. This is the single most useful tool here: it turns "the event
 * never appears" from a guess into a read.
 *
 * Remember the selection order: locator conditions must all pass, then PossibleWorldEvents
 * is SHUFFLED and the first definition whose conditions pass wins. A definition can fail to
 * appear purely because another one won the shuffle.
 */
static FWorldEventSpawnExplanation ExplainLocatorSpawn(const FWorldEventLocatorRef& Locator);

/** Persisted counters for a WorldEventTag: times spawned, seen, interacted. Backed by the runtime database. */
static FWorldEventRuntimeData GetWorldEventRuntimeData(const FString& WorldEventTag);

/** Active events within Radius of a point, the subsystem's own proximity query. */
static TArray<FWorldEventRuntimeLocator> GetActiveWorldEventsNearLocation(FVector Location, float Radius);

/**
 * Force a specific definition to spawn at a locator, optionally skipping the conditions.
 *
 * Skipping conditions produces a state the game cannot reach on its own. Useful for testing
 * the content, misleading for diagnosing selection. Say which one you did.
 */
static FWorldEventRuntimeActionResult ForceSpawnWorldEvent(
    const FWorldEventLocatorRef& Locator, const FString& DefinitionAssetPath,
    bool bSkipLocatorConditions = false, bool bSkipDefinitionConditions = false);

/** Remove the active event at a locator, or at every locator, and let selection run again. */
static FWorldEventRuntimeActionResult RemoveActiveWorldEvent(const FWorldEventLocatorRef& Locator);
static FWorldEventRuntimeActionResult RerollAllWorldEvents();

/** Teleport the player to a locator's DebugPlayerTeleportLocation. */
static FWorldEventRuntimeActionResult TeleportPlayerToLocator(const FWorldEventLocatorRef& Locator);

/** Drive the progress state machine, or fire a test event at the sockets. */
static FWorldEventRuntimeActionResult SetWorldEventProgressState(
    const FWorldEventLocatorRef& Locator, const FString& ProgressState);
static FWorldEventRuntimeActionResult SendTestEventToComponents(
    const FWorldEventLocatorRef& Locator, int32 TestEventNumber);

/** The WorldEvent.ToggleWorldEvents console command. Disabling removes every active event. */
static FWorldEventRuntimeActionResult SetWorldEventsEnabled(bool bEnabled);
```

### 4.9 `WorldEventExportJobToolset` (Execute, async)

Cross-map inventory without opening a map, reusing the async job infrastructure in
`WorldPartitionCommandletJob.cpp` that `HLODBuildToolset` already uses.

```cpp
/**
 * Run WorldEventExportCommandlet over a map as a detached child process and return a job id
 * immediately. Poll GetWorldEventExportJobStatus.
 *
 * This is the only way to inventory a map that is not open, and the only path that recurses
 * into Level Instances the way the cook does. The in-editor tools see the open level; this
 * sees the map as built.
 *
 * The command line is constructed here. No tool takes free-form arguments, so this cannot be
 * talked into running a different commandlet or submitting anything.
 *
 * @param MapPackageName e.g. /Game/Maps/LV_Overland.
 */
static FString ExportWorldEvents(const FString& MapPackageName);

static FWorldEventExportJobStatus GetWorldEventExportJobStatus(const FString& JobId);
static TArray<FWorldEventExportJobStatus> ListWorldEventExportJobs();
static FWorldEventExportJobStatus CancelWorldEventExportJob(const FString& JobId);

/** Parse a finished export into rows, so the JSON never enters the conversation. */
static TArray<FWorldEventLocatorSummary> ReadWorldEventExport(
    const FString& JobIdOrFilePath, const FString& NameFilter = TEXT("All"), int32 MaxResults = 500);

/**
 * Diff two exports, or an export against the open level: locators added, removed, moved, and
 * possible events changed.
 *
 * The question this answers: "what changed in the Overland's World Events between these two
 * builds?" - currently unanswerable without diffing two JSON files by hand.
 */
static TArray<FWorldEventExportDiffEntry> DiffWorldEventExports(
    const FString& BaselineJobIdOrPath, const FString& CurrentJobIdOrPath);
```

### 4.10 `UWorldEventAuthoringSkill`

A `UAgentSkill` in `WorldEventAuthoringSkill.h`, text in the constructor, referenced from
every toolset's class comment ("Read `UWorldEventAuthoringSkill` first"). It must carry
what a schema cannot:

1. **The vocabulary.** "Possible World Event Definition" is a `FLocalizedWorldEventDefinition`
   inside `AWorldEventLocator::PossibleWorldEvents`, not an asset. The asset is a
   `UWorldEventDefinition`. Confusing them makes every sentence about this system wrong.
2. **The object graph**, drawn: locator → N possible events → N level instances +
   N data layer assets + N data layer instances (2 when inside a Level Instance).
3. **The selection algorithm**, stated plainly: locator conditions all pass, then
   `PossibleWorldEvents` is *shuffled*, then first-match wins. No weights. No priority.
   Array order is not priority.
4. **Locator conditions versus definition conditions** and who is affected by each.
5. **Why deletion is a tool and not a sequence of edits**, and that submitting is human-only.
6. **The order of operations for authoring**: definition asset exists and is saved →
   `WorldDataLayers` is checkout-able → create locator → add possible event → validate →
   assign sockets → hand the changelist to a human.
7. **What is shared**: definitions, and sometimes data layer assets. Editing one definition
   changes every locator listing it.
8. **The abstract locator class**, and that creation goes through the settings Blueprint.

---

## 5. Refactoring required in the existing code

The read-only toolsets need nothing. The authoring ones do, because the operations are
currently entangled with Slate and with the editor selection.

### 5.1 Extract headless entry points

| Operation | Today | Needed |
| --- | --- | --- |
| Create locator | `FEditorDelegates::OnNewActorsDropped` → `HandleNewActorsDropped` → modal `PromptForLocatorName` → save prompt | `FWorldEventEditorHelpers::CreateLocator(UWorld*, FVector, const FString& Name, FText& OutError)` returning the actor. The toolkit calls it after its prompt; the toolset calls it directly. No modal, no save prompt. |
| Add possible definition | `FWorldEventEditorMenuExtender::AddWorldEventDefinitionToSelectedLocators` (reads editor selection) | `AddWorldEventDefinitionToLocator(AWorldEventLocator*, UWorldEventDefinition*, FText& OutError)`. The selection version becomes a loop over it. |
| Set data layer on actors | `SetDataLayerToSelectedActors` (reads editor selection) | `SetDataLayerOnActors(const TArray<AActor*>&, UDataLayerAsset*, FText& OutError)`. |
| Validate all locators | `FWorldEventEditorMode::ValidateAllLocators` logs only | Return `TArray<FWorldEventFinding>`; the button formats it into the log. |
| Data layer pipeline | `FLocalizedWorldEventDefinition::UpdateDataLayerWorldInstance` is `WITH_EDITOR` public but reached via `PostEditChangeProperty` | Callable as-is. Add an `FText& OutError` out-param and a dry-run mode that resolves names and reports what it would create without creating it — this is what makes `bApply = false` truthful rather than decorative. |

**Rule for all of these: no behaviour change for the existing UI.** Each is a pure
extraction — the Slate path keeps calling the same logic through the new function. Any
observable change in the editor mode means the extraction was done wrong.

### 5.2 Preview and mode state

`FWorldEventLocatorCustomDetail` owns the preview combo and the data layer context toggle
as widget state. `WorldEventViewportToolset` needs to set them without a widget. Move the
state onto `FWorldEventEditorMode` (or a small `FWorldEventPreviewState` it owns), with the
details panel reading and writing it. This is the only refactor in the plan that touches a
details customization, and it is the one most likely to produce a visual regression —
schedule it with time to verify by hand.

### 5.3 Deletion session lifetime

`FWorldEventDeleter` is constructed per operation, holds pinned actors, and unpins in its
destructor. MCP calls are independent, so `PlanWorldEventDeletion` and `DeleteWorldEvent`
cannot share a stack frame.

Add a small session registry, keyed by GUID, in `WorldEventDeletionToolset.cpp`:

- `PlanWorldEventDeletion` creates a deleter, runs `Analyze`, stores it, returns a
  `DeletionSessionId` alongside the plan.
- `DeleteWorldEvent` reuses the session for that locator when one exists, otherwise creates
  and analyses one.
- `AbortDeletion` and a session timeout destroy it, which unpins.
- **Sessions are cleared on map change and on editor shutdown.** A stale deleter holds weak
  pointers into a level that may be gone; `ResolvePlanObjects` exists precisely because those
  pointers cannot be trusted, so re-analyse rather than trust a session across a reload.

Model the registry on the session-wide job registry in
`WorldPartitionCommandletJob.cpp` — same lifetime problem, already solved once.

### 5.4 Saving policy, and the one place it bends

The convention is to leave packages dirty. Two operations cannot:

- **`CreateWorldEventDefinition`** — an unsaved data asset cannot be referenced by a
  locator, so leaving it dirty produces something that looks created and cannot be used.
  Save + mark for add, as `MissionToolset` does, and say so in the tool description.
- **`AddPossibleWorldEvent`** — `UpdateDataLayerWorldInstance` currently calls
  `WorldEventLocator->Save()`. Options: keep the save (consistent with the existing UI,
  inconsistent with toolset convention), or add a `bSave` parameter defaulting to the
  existing behaviour. **Recommendation: keep the save, document it loudly.** The data layer
  instance lives in `WorldDataLayers` and a half-saved graph here is exactly the corruption
  the checkout precondition was added to prevent.

Everything else: dirty only, `ModifiedPackage` reported, human saves and submits.

### 5.5 Runtime subsystem access

`UWorldEventSubsystem` getters are public C++ but not `BlueprintCallable`. `SundanceEditor`
depends on `Sundance` and the classes are `SUNDANCE_API`, so the toolset can call them
directly. **No Blueprint exposure needed** — and none should be added, since these are
debug affordances, not gameplay API.

`DEBUG_*` functions are `#if !UE_BUILD_SHIPPING`. `WorldEventRuntimeToolset` must be
compiled out identically, not merely fail at runtime.

---

## 6. Shared types

`WorldEventToolsetTypes.h`, all `USTRUCT(BlueprintType)` with `BlueprintReadOnly` members
and a doc comment per field, following `FWorldPartitionDataLayerNode`.

| Struct | Key fields |
| --- | --- |
| `FWorldEventLocatorRef` | `GuidString`, `Label` (input) |
| `FWorldEventConditionOwnerRef` | `Locator`, `DefinitionAssetPath` — exactly one set |
| `FWorldEventLocatorSummary` | `Label`, `GuidString`, `Location`, `LocatorTags`, `NumPossibleEvents`, `WorldEventTags`, `PackageName`, `bIsLoaded`, `bIsValid` |
| `FWorldEventLocatorDetail` | Summary + `PossibleEvents`, `Conditions`, `BoundsExtent`, `TeleportLocation`, `InstanceActorPaths`, `Findings` |
| `FWorldEventPossibleEvent` | `Index`, `DefinitionAssetPath`, `WorldEventTag`, `FriendlyName`, `DisplayedName`, `DataLayerAssetPath`, `DataLayerInstanceName`, `LevelInstanceActorPath`, `WorldEventLevelPath`, `bResolved`, `Detail` |
| `FWorldEventTreeNode` | `NodeType` (`Locator`/`PossibleEvent`/`LevelInstance`), `Label`, `Depth`, `ParentLabel`, `LocatorGuidString` |
| `FWorldEventDefinitionSummary` / `FWorldEventDefinitionDetail` | `AssetPath`, `WorldEventTag`, `FriendlyName`, `WorldEventLevelPath`, `NeededComponentTags`, `bActivatesOnPlayerProximity`, `PlayerDistanceToActivate`, `GuidString`, `Conditions`, `UsedByLocatorCount` |
| `FWorldEventDefinitionPatch` | Optional-per-field patch (empty/`INDEX_NONE` sentinels documented per field) |
| `FWorldEventConditionSchema` | `ClassName`, `DisplayName`, `Description`, `Properties[]` (`Name`, `Type`, `DefaultValue`, `Description`), `bPersisted` |
| `FWorldEventConditionDetail` | `Index`, `ClassName`, `PropertyValues` (`TMap`), `Summary` |
| `FWorldEventConditionUsage` | `ConditionClass`, `OwnerKind`, `OwnerLabel`, `PropertyValues` |
| `FWorldEventFinding` | `Severity`, `Check`, `LocatorLabel`, `LocatorGuidString`, `DefinitionAssetPath`, `Detail`, `bFixable`, `FixTool` |
| `FWorldEventSpawnabilityReport` | `bCanEverSpawn`, `EvaluationOrder[]`, `BlockingConditions[]`, `Detail` |
| `FWorldEvent*Change` (locator / possible event / definition / condition / data layer / viewport) | `Action`, `bApplied`, `Detail`, `ModifiedPackages[]`, `CreatedAssets[]` |
| `FWorldEventDeletionPlanReport` | `DeletionSessionId`, `bValid`, `InvalidReason`, `LocatorLabel`, `ActorsToDelete[]`, `DataLayerInstances[]`, `DataLayerAssets[]`, `ModifiedFiles[]`, `DeletedFiles[]`, `bIsInsideLevelInstance`, `Steps[]` |
| `FWorldEventDeletionResult` | `bSucceeded`, `FailedStep`, `ChangelistId`, `StepStatuses[]`, `LogLines[]`, `bRolledBack`, `bLevelReloaded` |
| `FWorldEventRuntimeStatus` / `FWorldEventRuntimeLocator` / `FWorldEventRuntimeData` | Session state, progress state, current definition, socket components, counters |
| `FWorldEventSpawnExplanation` | `bSpawned`, `WinningDefinition`, `LocatorConditionResults[]`, `PerDefinitionResults[]` (`DefinitionAssetPath`, `ConditionResults[]`) |
| `FWorldEventExportJobStatus` | `JobId`, `State`, `MapPackageName`, `OutputPath`, `ExitCode`, `LocatorCount`, `Elapsed`, `LastLogLine` |
| `FWorldEventExportDiffEntry` | `ChangeKind`, `LocatorLabel`, `GuidString`, `Field`, `BaselineValue`, `CurrentValue` |
| `FWorldEventInventoryStats` / `FWorldEventTagReport` / `FWorldEventLoadResult` | Aggregates |

---

## 7. Phasing

Ordered so that every phase ships something usable and the risky work happens after the
foundations are proven. Estimates are engineer-days for one developer familiar with the
codebase, excluding review.

| Phase | Contents | Days | Ships |
| --- | --- | --- | --- |
| **0. Foundations** | Folder, `WorldEventToolsetTypes.h`, `WorldEventToolsetCommon` (`Fail`, `IsUnset`, locator/definition resolvers, formatters), `FWorldEventLocatorRef` resolution incl. descriptor path, skill skeleton, one trivial registered tool to prove the wiring end to end. | 2–3 | A toolset visible in `list_toolsets`. |
| **1. Discovery** | All of §4.1. Descriptor-first reads, pinning for `LoadLocators`. | 4–5 | An agent can answer any "what exists" question. Highest value per day in the plan. |
| **2. Validation** | All of §4.2, including the checks that do not exist yet (orphans, dangling, conventions, socket coverage, reachability). Extract `ValidateAllLocators` (§5.1). | 4–5 | A real audit of the Overland's World Events. Expect it to find genuine content bugs. |
| **3. Definitions** | All of §4.3. First write path, on assets, which is the least dangerous place to prove the write conventions. | 3–4 | Definition authoring and the tag audit. |
| **4. Locator authoring** | §5.1 extractions, dry-run mode on the data layer pipeline, all of §4.4. **The core of the plan and the riskiest part**: touches the pipeline that writes `WorldDataLayers`. | 7–9 | Full authoring without the editor mode. |
| **5. Conditions** | §4.5, including reflection-driven `ListConditionTypes` and the property marshalling. | 4–5 | Condition authoring across eleven classes. |
| **6. Deletion** | Session registry (§5.3), §4.6. Behaviour parity with the dialog verified case by case, including the Level Instance path. | 4–5 | Scripted deletion with plan and rollback. |
| **7. Viewport** | §5.2 preview-state refactor, §4.7. | 3–4 | An agent can show what it is talking about. |
| **8. Runtime** | §4.8, non-shipping guarded, PIE-gated. `ExplainLocatorSpawn` is the payload. | 4–5 | "Why did this not spawn" answered from a read. |
| **9. Export jobs** | §4.9 on top of `WorldPartitionCommandletJob`, plus the diff. | 3–4 | Cross-map inventory and build-to-build diffs. |
| **10. Hardening** | Skill text written properly, automation tests (§8), doc page in this repo, description pass over every tool with a fresh reader. | 3–4 | The thing someone else can use. |

**Total: 41–53 days.** Phases 0–2 (10–13 days) are worth shipping alone: they are
read-only, carry no risk to content, and cover the questions asked most often.

Sensible cut lines if the scope has to shrink: drop phase 9 (the commandlet already works
from a command line), then phase 7 (nice, not necessary), then phase 5 (conditions can be
edited in the details panel).

---

## 8. Testing

Follow the engine's own harness: `AIAssistant.ToolsetRegistry.*` and
`AIAssistant.ModelContextProtocol.*` in
`Engine/Plugins/Experimental/ToolsetRegistry/Source/ToolsetRegistryEditor/Private/Tests/`.
There are no toolset tests in Sundance today, so this plan sets the precedent — keep it
small enough to be maintained.

New: `Source/SundanceEditor/WorldEvents/Toolset/Tests/WorldEventToolsetTests.cpp`,
prefix `Sundance.WorldEvents.Toolset.*`.

| Test | Asserts |
| --- | --- |
| `Registration` | All nine toolsets resolve from `UToolsetRegistry` and every tool bakes a valid JSON schema. Catches a bad `UPROPERTY` type immediately. |
| `LocatorRefResolution` | GUID resolves; label resolves; ambiguous label fails; unknown fails; empty fails. All through `Fail`, none through a crash. |
| `DiscoveryOnFixture` | On a small test map: counts and fields match the placed content, unloaded locators appear, `MaxResults` caps. |
| `ValidationFindsSeededProblems` | A fixture map with one of each seeded defect produces exactly the expected `Check` values, and a clean fixture produces none. |
| `DryRunWritesNothing` | Every mutating tool with `bApply = false`: package dirty flags and asset registry unchanged before and after. **The single most valuable test here.** |
| `ApplyThenUndo` | Each mutating tool with `bApply = true` followed by `GEditor->UndoTransaction()` restores the prior state — verifies the `FScopedTransaction` scopes are right. |
| `ConditionSchemaRoundTrip` | For every `USunWorldEventCondition` subclass: `ListConditionTypes` → `AddCondition` → `GetConditions` returns what went in. Fails automatically when a new condition class is added without support. |
| `DeletionPlanParity` | The plan for a fixture World Event matches the file and object lists `FWorldEventDeleter` produces for the dialog. |
| `RuntimeToolsOutsidePIE` | Every runtime tool fails cleanly with "no PIE session" rather than dereferencing null. |

Manual verification, per phase, because automation cannot cover it: run the editor mode
UI through its normal flow and confirm nothing changed. Specifically after phase 4
(context menus, details panel) and phase 7 (preview combo, overlays).

---

## 9. Risks and guard-rails

| Risk | Why it matters here | Guard-rail |
| --- | --- | --- |
| **Corrupting `WorldDataLayers`** | The whole reason the checkout precondition exists. Every possible-event write touches it. | Precondition checked and *reported* on every write, not assumed. Dry run resolves names without writing. Never bypass `CanEditChange`. |
| **An agent submitting to Perforce** | Irreversible, and visible to the whole team. | No tool submits. No tool takes a free-form command line. Checkout and described changelists only, exactly as the deletion dialog behaves. State it in every relevant tool description. |
| **Silent level reload** | The Level Instance deletion path reloads the level and invalidates everything an agent holds. | `bAllowLevelInstanceEdit` defaults to false and the refusal explains why. Deletion sessions are dropped on map change. |
| **Dry run that is not a dry run** | A `bApply = false` that still resolves by creating a data layer asset is worse than no dry run. | The dry-run mode of the data layer pipeline is a phase-4 deliverable, tested by `DryRunWritesNothing`, not an afterthought. |
| **Leaving actors pinned** | `Analyze` pins unloaded instances; an abandoned plan leaves the editor holding them. | Session timeout, `AbortDeletion`, cleanup on map change. `LoadLocators`/`UnloadLocators` documented as a pair. |
| **Tool sprawl** | Nine toolsets and roughly seventy tools. | Split by access mode so an agent loads only what it needs; cross-reference in descriptions instead of duplicating tools; revisit merging 7 and 8 after phase 8. |
| **Descriptions that assume context** | An agent reading `AddPossibleWorldEvent` has no idea five assets appear. | Every description states what it creates, what it dirties, and what a human must do next. Review descriptions with a reader who has never seen this system. |
| **Drift from the Slate UI** | Two paths to the same operation diverge. | The extractions in §5.1 are pure: the UI calls the same function. Reject any patch that forks the logic. |
| **The shuffle misunderstood as priority** | Leads to authoring changes that do nothing. | Stated in the skill, in `ReorderPossibleWorldEvents`, and in `ExplainLocatorSpawn`. Three times, deliberately. |

---

## 10. Deliverables

### New files — `D:\Sun\Sundance\Source\SundanceEditor\WorldEvents\Toolset\`

`WorldEventToolsetTypes.h` · `WorldEventToolsetCommon.h/.cpp` ·
`WorldEventAuthoringSkill.h` · `WorldEventDiscoveryToolset.h/.cpp` ·
`WorldEventValidationToolset.h/.cpp` · `WorldEventDefinitionToolset.h/.cpp` ·
`WorldEventLocatorAuthoringToolset.h/.cpp` · `WorldEventConditionToolset.h/.cpp` ·
`WorldEventDeletionToolset.h/.cpp` · `WorldEventViewportToolset.h/.cpp` ·
`WorldEventRuntimeToolset.h/.cpp` · `WorldEventExportJobToolset.h/.cpp` ·
`Tests/WorldEventToolsetTests.cpp`

### Modified files

| File | Change |
| --- | --- |
| `SundanceEditor/WorldEvents/EditorMode/WorldEventEditorHelpers.h/.cpp` | Add `CreateLocator`, `AddWorldEventDefinitionToLocator`, `SetDataLayerOnActors`. |
| `SundanceEditor/WorldEvents/EditorMode/WorldEventEditorMenuExtender.cpp` | Selection handlers delegate to the new helpers. |
| `SundanceEditor/WorldEvents/EditorMode/WorldEventEditorModeToolkit.cpp` | Drop handler delegates to `CreateLocator`. |
| `SundanceEditor/WorldEvents/EditorMode/WorldEventEditorMode.h/.cpp` | `ValidateAllLocators` returns findings; owns preview state. |
| `SundanceEditor/WorldEvents/WorldEventLocatorCustomDetail.cpp` | Preview combo reads/writes mode state. |
| `Sundance/WorldEvents/WorldEventLocator.h/.cpp` | `UpdateDataLayerWorldInstance`: `FText& OutError` + dry-run mode. |
| `SundanceEditor/SundanceEditor.Build.cs` | **No change needed** — dependencies already present. |
| `Sundance.uproject` | **No change needed** — plugins already enabled. |

### Documentation in this repo

- `ReferenceDocs/CustomTools/WorldEventsMCPToolsets.md` — the user-facing page, linked from
  [Custom Tools](CustomTools.md), following the shape of
  [Delete World Event](CustomTools/DeleteWorldEvent.md).
- Update [World Events (work done)](../WorkDoneByTopic/WorldEvents.md) once phases ship.

---

## 11. Open questions

1. **Nine toolsets or fewer?** Worth a look at how many entries `list_toolsets` already
   returns before adding nine more. Merging Viewport into Discovery and Runtime into
   Deletion would give seven.
2. **Should `AddPossibleWorldEvent` keep saving the locator?** §5.4 recommends yes. It
   breaks the toolset convention and it is the safer of the two failure modes. Needs a
   decision from whoever owns the data-safety fix.
3. **Does a fixture map exist, or must one be authored?** Phases 1, 2 and 6 depend on a
   small map with known content, including one World Event inside a Level Instance. If
   none exists, add a day to phase 1.
4. **Locator creation and the settings Blueprint.** `DefaultLocatorActorSoftPath` names one
   Blueprint. Do teams place other locator subclasses? If so `CreateWorldEventLocator`
   needs a class parameter.
5. **Is there appetite for weights?** Several tools have to explain that the shuffle is not
   priority. If designers actually want priority, that is a runtime change to
   `TrySpawnWorldEvent`, out of scope here, but this plan will surface the request.
6. **Should the audit ever write to Confluence?** `HLODPartitionConfigToolset` carries an
   explicit prohibition on wiki writes. Recommend the same stance: reporting drift is
   useful, writing the page is not.

---

**In this section:** [Reference Docs index](README.md)

Back to [repository root](../README.md).
