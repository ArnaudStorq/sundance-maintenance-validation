Parent: [Reference Docs](README.md)

# MapCheck validation CVars

The Sundance MapCheck validations (`UWorldPartitionMapCheckValidator`) are each gated
behind a console variable. **Two of them are off by default**, which is why loading
`LV_Overland` no longer reports the Data Layer warnings it used to.

This page documents what each CVar controls, how to turn one back on for a single
investigation, and how to make a value permanent in Unreal Editor.

Source: `D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionMapCheckValidator.cpp`
(CVars declared in the `WorldPartitionMapCheckValidatorUtilities` namespace, read in
`PerformMapCheckValidation`). Introduced by changelist **2064105**
(jira **SUNDANCE-77766**).

## Contents

- [Why the gating exists](#why-the-gating-exists)
- [The CVars](#the-cvars)
- [Reproducing the pre-2064105 warnings](#reproducing-the-pre-2064105-warnings)
- [Making a value permanent](#making-a-value-permanent)
  - [1. Your machine only — `ConsoleVariables.ini`](#1-your-machine-only--consolevariablesini)
  - [2. Per-session — command line](#2-per-session--command-line)
  - [3. Whole project — `DefaultEngine.ini`](#3-whole-project--defaultengineini)
- [See also](#see-also)

## Why the gating exists

`PerformMapCheckValidation` is bound to `FEditorDelegates::OnGameMapChecked`, so the
whole set of validations runs **every time a level is loaded**, on the game thread,
before the editor becomes responsive. On `LV_Overland` two costs dominated:

- **~13 s** blocking on `FAssetRegistryModule::Get().WaitForCompletion()` on a cold
  editor. Only the two Data Layer checks need the asset registry, so the wait is now
  itself conditional — it is skipped entirely unless `CheckForMissingDataLayers` or
  `CheckForNonRelevantDataLayers` is enabled.
- **~25 s** for `CheckForNonRelevantDataLayers`, which iterates every actor of the world
  and evaluates the DataLayer rules on each one.

Both disabled checks are **redundant with the nightly `WorldPartitionRuleBuilder`**,
which creates the rule-targeted DataLayer instances and reports the non-compliant ones
in its own log. Nothing is lost in the normal workflow — the information just moves from
the per-load MapCheck to the nightly build report
([builders & commandlets](BuildersAndCommandlets.md)).

## The CVars

All seven are `bool`, `ECVF_Default` (settable from the console and from `.ini`), and
read with `GetValueOnGameThread()` at the start of every MapCheck run — so a change
takes effect at the **next** Map Check, no editor restart needed.

| CVar (`wp.editor.MapCheck.` + …) | Default | Reports | MapCheck message |
|---|---|---|---|
| `CheckForMissingDataLayers` | **`false`** | Actors assigned to a DataLayer absent from the `AWorldDataLayers` | [B1](FixingMapCheckIssues.md#b1--actor-assigned-to-a-data-layer-that-doesnt-exist) |
| `CheckDataLayersHierarchy` | `true` | Sub-level DataLayer hierarchies that disagree with the persistent level | [B3](FixingMapCheckIssues.md#b3--data-layer-hierarchy-mismatch) |
| `CheckForNonRelevantDataLayers` | **`false`** | Actor DataLayer assignments that no WorldPartition rule justifies | [B2](FixingMapCheckIssues.md#b2--actor-has-a-data-layer-that-violates-the-rules) |
| `CheckActorStreamingBounds` | `true` | LevelInstance descriptors whose editor or runtime bounds are oversized | [D2](FixingMapCheckIssues.md#d2--oversized-streaming-bounds) |
| `CheckWorldPartitionLevelInstance` | `true` | LevelInstances whose level is not a WorldPartition world | [C1](FixingMapCheckIssues.md#c1--levelinstance-is-not-using-world-partition) |
| `CheckForStaleMaterialOverrides` | `true` | `StaticMeshComponent`s carrying more material overrides than their mesh has slots | [E1](FixingMapCheckIssues.md#e1--stale-material-overrides) |
| `CheckWorldPartitionLevelInstanceBrushLocation` | `true` | Brushes sitting more than 200 000 units from their LevelInstance pivot | [D3](FixingMapCheckIssues.md#d3--brush-far-from-the-level-instance-pivot) |

> The CVars gate only the **MapCheck** path. The data validation path
> (`UWorldPartitionMapCheckValidator::ValidateLoadedAsset`, used on submit /
> *Validate Assets*) still calls `CheckForMissingDataLayers` and
> `CheckDataLayersHierarchy` **unconditionally**, so a missing DataLayer is still caught
> at [Peeves submit validation](PeevesSubmitValidation.md) time even with the CVar off.

## Reproducing the pre-2064105 warnings

The two checks turned off are exactly the ones you used to see when loading a level. To
get them back:

1. Open the target level (e.g. `LV_Overland`).
2. Open the editor console with `` ` `` or `~` and enable the checks:

   ```
   wp.editor.MapCheck.CheckForMissingDataLayers 1
   wp.editor.MapCheck.CheckForNonRelevantDataLayers 1
   ```

3. Re-run the validation **without reloading the level** — the **Build → Map Check**
   menu entry, or the console command:

   ```
   MAP CHECK
   ```

4. Read the results in the **Map Check** window (*Window → Developer Tools →
   Message Log → Map Check*). Both checks publish warnings with a **"Fix It!"** action.

Expect the run to take roughly **25–40 s longer** on `LV_Overland`, and the first run
after a cold start to additionally block on the asset registry.

Typing the CVar with no value prints its current state, which is the quickest way to
confirm what a session is running with:

```
wp.editor.MapCheck.CheckForNonRelevantDataLayers
```

> Both checks early-out when the world is **not in the rule auto-apply list**
> (`UWorldPartitionRuleSubsystem::IsWorldInAutoApplyList`) and, for
> `CheckForMissingDataLayers`, when the world is not partitioned. If you enable the CVar
> and still get nothing, verify the level is in the auto-apply list before assuming the
> data is clean — see [World Partition rules](WorldPartitionRules.md).

## Making a value permanent

Console values are lost when the editor closes. Three ways to persist them, from most
local to most global.

### 1. Your machine only — `ConsoleVariables.ini`

Edit `D:\Sun\Engine\Config\ConsoleVariables.ini` and add, under the existing
`[Startup]` section:

```ini
[Startup]
wp.editor.MapCheck.CheckForMissingDataLayers=1
wp.editor.MapCheck.CheckForNonRelevantDataLayers=1
```

Applied at editor startup, before any level loads. This is the right choice for a
personal investigation: it affects nobody else and needs no Perforce checkout.

### 2. Per-session — command line

Useful for a one-shot editor run or for a commandlet, with no file to edit or revert:

```
UnrealEditor.exe Sundance -ExecCmds="wp.editor.MapCheck.CheckForNonRelevantDataLayers 1"
```

The `-ini:` form also works and is applied earlier:

```
UnrealEditor.exe Sundance -ini:Engine:[ConsoleVariables]:wp.editor.MapCheck.CheckForNonRelevantDataLayers=1
```

### 3. Whole project — `DefaultEngine.ini`

To change the default **for the whole team**, edit the `[ConsoleVariables]` section of
`D:\Sun\Sundance\Config\DefaultEngine.ini`:

```ini
[ConsoleVariables]
wp.editor.MapCheck.CheckForNonRelevantDataLayers=1
```

This file is read-only in the workspace — check it out in Perforce first
([Perforce source control](PerforceSourceControl.md)). Given that CL 2064105 disabled
these checks specifically to cut ~38 s off every level load, re-enabling them
project-wide should be a deliberate, reviewed decision rather than a convenience.

> `[ConsoleVariables]` in `DefaultEngine.ini` is applied at startup and can still be
> overridden from the console afterwards. `[SystemSettings]` is the stronger, scalability
> oriented equivalent; for these editor-only checks, `[ConsoleVariables]` is the correct
> section.

## See also

- [Fixing MapCheck issues](FixingMapCheckIssues.md) — the cause → solution playbook for
  every message these checks emit
- [World Partition rules](WorldPartitionRules.md) — the auto-apply list and the DataLayer
  rules the disabled checks validate against
- [Builders & commandlets](BuildersAndCommandlets.md) — the nightly
  `WorldPartitionRuleBuilder` that reports the same non-compliant DataLayers
- [Peeves submit validation](PeevesSubmitValidation.md) — the validation path that is
  **not** gated by these CVars
- [Custom Tools](CustomTools.md) — the other in-editor console commands of this project
