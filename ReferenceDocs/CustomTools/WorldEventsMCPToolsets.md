Parent: [Custom Tools](../CustomTools.md)

# World Events MCP Toolsets

An MCP toolset family: C++ functions exposed to AI agents through the
`ToolsetRegistry` / `ModelContextProtocol` pipeline.

**Nine toolsets and 81 tools that make the whole World Events system — locators, possible
world events, definitions, conditions, data layers, deletion, runtime state and cross-map
export — discoverable, auditable, authorable and debuggable from an agent, without opening
the World Events editor mode.**

Source: `D:\Sun\Sundance\Source\SundanceEditor\WorldEvents\Toolset\`.
Implemented from
[Development Plan — World Events MCP Toolsets](../DevelopmentPlan-WorldEventsMCPToolset.md).
## Contents

- [Why it exists](#why-it-exists)
- [The toolsets](#the-toolsets)
- [The three things an agent has to be told](#the-three-things-an-agent-has-to-be-told)
- [Conventions](#conventions)
- [Notable design decisions](#notable-design-decisions)
- [Known limitations](#known-limitations)
- [See also](#see-also)

---


## Why it exists

Before this, the World Events system was reachable only through Slate: a dedicated editor
mode, a drag-and-drop widget, two viewport context menus, a details panel customization, a
deletion wizard and an ImGui runtime debugger. None of it was callable by an agent and
almost none of it by a script.

That matters more here than for most systems, because a World Event is not one asset. It is
a web: placing one creates a locator actor, one `AWorldEventInstance` per possible
definition, a `UDataLayerAsset`, and one or two `UDataLayerInstance`. Answering "what exists
and is it consistent?" by hand means walking four different editors, and the consistency
rules are implicit — validation existed but only wrote to the log.

## The toolsets

| Toolset | Access | Tools | Purpose |
|---------|--------|-------|---------|
| `WorldEventDiscoveryToolset` | Read | 12 | What exists: locators, possible events, definitions, data layers, reverse lookups, spatial queries, inventory stats, pinning |
| `WorldEventValidationToolset` | Read | 5 | Structured audit: 12 checks plus `IsDataValid`, spawnability analysis, Markdown report |
| `WorldEventDefinitionToolset` | Read/Write | 6 | The `WEDA_*` data assets: read, create, patch, duplicate, tag audit |
| `WorldEventLocatorAuthoringToolset` | Write | 11 | Place locators, add/remove/reorder possible events, move, bounds, tags, repair data layers, assign actors |
| `WorldEventConditionToolset` | Read/Write | 9 | The instanced condition arrays, with a reflection-driven schema so an agent can author a condition class it has never seen |
| `WorldEventDeletionToolset` | Write/Execute | 6 | Drives `FWorldEventDeleter`: plan, execute, abort, rollback, changelist |
| `WorldEventViewportToolset` | Write | 7 | Editor mode, active locator, preview, overlays, camera focus |
| `WorldEventRuntimeToolset` | Execute | 14 | PIE only, non-shipping: progress states, force spawn, reroll, teleport, counters |
| `WorldEventExportJobToolset` | Execute | 6 | Async `WorldEventExportCommandlet` jobs for cross-map inventory, plus a build-to-build diff |

Plus `UWorldEventAuthoringSkill`, a `UAgentSkill` carrying what a tool schema cannot: the
vocabulary, the object graph, and the selection algorithm.

## The three things an agent has to be told

These are in the skill because getting them wrong makes every answer wrong.

**The vocabulary.** A "Possible World Event Definition" is `FLocalizedWorldEventDefinition`,
an entry inside `AWorldEventLocator::PossibleWorldEvents`. It is a *pairing* of a locator
with a definition, and it has no file. The asset is a `UWorldEventDefinition` (`WEDA_`).
Confusing them makes every sentence about this system wrong.

**The selection algorithm.** Locator conditions must all pass, then `PossibleWorldEvents` is
**shuffled**, then the first definition whose conditions pass wins. There are no weights and
array order is not priority. A definition can have every condition passing and still never
appear because another one was reached first — which looks identical to a broken condition
unless you read the per-definition results.

**What is shared.** Definitions are shared, so editing one changes every locator listing it.
`WorldEventTag` is shared too: the runtime database counts spawned/seen/interacted per tag,
so two definitions with the same tag share their counters.

## Conventions

Inherited from the existing `WorldBuildingEditor` toolsets, deliberately:

- **Dry run by default.** Every mutating tool takes `bApply = false` last and writes nothing
  until it is true. The dry run still does all the resolution and reports what would happen.
- **Refusals are not errors.** A change the engine legitimately declines returns
  `bApplied = false` with the reason — usually the answer the caller wanted.
- **Checkout is automatic, submitting is not.** No tool submits, and no tool takes a
  free-form command line. Writes leave packages dirty and report them.
- **Addressing.** Locators are addressed by `GuidString`, the only identity stable across a
  rename, a level reload and a Level Instance in-context edit. Labels are accepted, and an
  ambiguous label is an error rather than a guess.
- **Descriptor-first reads.** List tools read World Partition actor descriptors, so they see
  unloaded locators and cost nothing. `bIsLoaded` says which kind of row you have.
- **Class comments stay short, on purpose.** `list_toolsets` serves every toolset's class comment
  to every `unreal-mcp` session, whether or not the caller cares about World Events, so a long
  class comment is a token cost imposed on everybody. Each class comment here is one or two
  sentences plus a pointer to the skill. Anything tool-specific lives on the function, paid for
  only by a caller who ran `describe_toolset` on this toolset; anything conceptual lives in the
  skill, paid for only by a caller who reads it.

## Notable design decisions

**No refactoring of the existing UI was needed.** The plan budgeted for extracting headless
entry points out of Slate code. In the event, `FWorldEventEditorHelpers::SetDataLayerToSelectedActors`
already takes a plain actor array, `FWorldEventEditorMode::SetActiveLocator` and the overlay
setters are already public, and `FWorldEventDeleter` was already Slate-free. The authoring
tools reproduce the ~20 lines of the "Add World Event Definition" menu handler rather than
forking it, and the data layer pipeline is driven through `PostEditChangeProperty`, which is
the exact path the details panel takes. **The editor mode is therefore untouched and cannot
have regressed.**

**Three one-line changes to existing files**, all of them the minimum needed to link:
`WorldEventDefinition.h` was missing `#include "Engine/DataAsset.h"` and so was not
self-sufficient; `FWorldEventLocatorDesc::FillWorldEventInfo` and
`WorldPartitionToolset::ValidateTargetLevelOrFail` gained `SUNDANCE_API` and
`WORLDBUILDINGEDITOR_API` respectively, since both are now called across a module boundary.
No behaviour changed.

**The WorldDataLayers precondition is asked, not reimplemented.** `AWorldEventLocator::CanEditChange`
already decides whether that shared file is safe to write to. `AddPossibleWorldEvent` and
`RepairWorldEventDataLayers` call it and report the refusal.

**Deletion sessions.** `FWorldEventDeleter` pins actors in `Analyze()` and unpins in its
destructor, but MCP calls do not share a stack frame. A session registry keyed by GUID holds
the deleter between `PlanWorldEventDeletion` and `DeleteWorldEvent`, expires after 30
minutes, and is cleared on map change — a stale deleter holds weak pointers into a level
that may be gone.

**Level Instances are refused by default.** Deleting a World Event inside a Level Instance
needs an in-context edit, which reloads the level and invalidates everything the caller
holds. `bAllowLevelInstanceEdit` defaults to false and the refusal explains why.

## Known limitations

- The audit's `MissingSocket` check only sees loaded content, so it under-reports on a
  mostly-unloaded Overland.
- `AnalyzeLocatorSpawnability` is static analysis. It can prove a condition never passes but
  not that it will, because most conditions depend on runtime or persisted state. Use
  `WorldEventRuntimeToolset.ExplainLocatorSpawn` in PIE for the real evaluation.
- `UsedByLocatorCount` counts the open level only.
- Automation tests (`Sundance.WorldEvents.Toolset.*`) are specified in the plan but not yet
  written.

## See also

- [Delete World Event](DeleteWorldEvent.md) — the editor-mode dialog the deletion toolset drives
- [World Events (work done)](../../WorkDoneByTopic/WorldEvents.md) — the system and the data-safety fix
- [Development plan](../DevelopmentPlan-WorldEventsMCPToolset.md) — the full design and phasing
- [Demo script](../Demo-WorldEventsMCPToolset.md) — a two-minute live run of the toolsets
- [Perforce source control](../PerforceSourceControl.md) — checkout-before-save, changelists

---

**In this section:** [Custom Tools index](../CustomTools.md)

Back to [repository root](../../README.md).
