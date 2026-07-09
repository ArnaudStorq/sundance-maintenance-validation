# 3. Builders & commandlets

All custom builders derive from `UWorldPartitionBuilder` and run through the engine's
`UWorldPartitionBuilderCommandlet`. They live in the `WorldBuildingEditor` module
(`D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\`).

## Invocation shape

```bat
UnrealEditor-Cmd.exe "D:\Sun\Sundance\Sundance.uproject" ^
  -run=WorldPartitionBuilderCommandlet ^
  -Builder=<BuilderClassNameWithoutU> ^
  -SCCProvider=Perforce ^
  -Unattended -NoShaderCompile ^
  <MapPackageOrShortName>
```

- `-Builder=` value is the UClass name **without the `U` prefix** (resolved via
  `FindFirstObject<UClass>`, `WorldPartitionBuilderCommandlet.cpp:182`).
- Exactly **one** positional map token is allowed (short name `LV_Overland`, a
  `/Game/...` path, a collection, or `*`).
- `-SCCProvider=Perforce` overrides the ini SCC provider at startup
  (`SourceControlSettings.cpp:58`); builders then checkout via
  `FPackageSourceControlHelper`.
- `-NoShaderCompile` is a pass-through engine switch (no custom handler).

`-Builder=` registration names:

| Class | `-Builder=` value |
|-------|-------------------|
| `UWorldPartitionRuleBuilder` | `WorldPartitionRuleBuilder` |
| `UWorldPartitionFixupNonPartitionedActorsBuilder` | `WorldPartitionFixupNonPartitionedActorsBuilder` |
| `UWorldPartitionFixupActorFoldersBuilder` | `WorldPartitionFixupActorFoldersBuilder` |
| `UWorldPartitionResaveActorsRecursiveBuilder` | `WorldPartitionResaveActorsRecursiveBuilder` |
| `UForceHLODExcludeFromLogBuilder` | `ForceHLODExcludeFromLogBuilder` |

---

## `UWorldPartitionRuleBuilder`

Applies the World Partition rules (DataLayer / HLOD / RuntimeGrid) to actors and saves
the dirty packages. This is the batch equivalent of the on-save rule reapplication.

- Base: `UWorldPartitionBuilder`; `GetLoadingMode() == ELoadingMode::Custom`;
  `RequiresCommandletRendering() == false`.
- Switches (parsed in the constructor, `WorldPartitionRuleBuilder.cpp:69`):

| Switch | Effect |
|--------|--------|
| `-DataLayerRules` | apply DataLayer rules (`BuildOptions.ApplyDataLayerRules`) |
| `-HLODLayerRules` | apply HLOD rules |
| `-RuntimeGridRules` | apply RuntimeGrid rules |
| `-ContainOutlinerPathSubstrings=a,b` | only actors whose Outliner path contains one of these |
| `-DiscardOutlinerPathSubstrings=a,b` | skip actors whose Outliner path contains one of these |

> ⚠ Note: this builder has **no `-DryRun`**. Rule categories are opt-in — omit a switch
> and that category is skipped. (The recap's "generic `-DryRun`" belongs to the *fixup*
> builders below, not this one.)

- Iterates via `FWorldPartitionHelpers::ForEachActorWithLoading`; main-world pass with
  `bRecurseIntoLevelInstances=false`, plus a recursive Level Instance pass under
  `FLevelInstanceEditScope`.
- `ShouldProcessActor` pre-checks `WorldPartitionRules::FPackageUtility::CanCheckoutPackage`
  and **skips** (does not force-checkout) actors whose package can't be checked out:

```420:428:D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionRuleBuilder.cpp
		if (!WorldPartitionRules::FPackageUtility::CanCheckoutPackage(PackageName, false, &CheckoutFailureReason))
		{
			const FString OutlinerPath = ActorOrDesc.GetOutlinerFullPath();
			UE_LOG(LogWorldPartitionRuleBuilder, Display, TEXT("Skipping rule application for actor [%s]: package cannot be checked out (%s)"), *OutlinerPath, *CheckoutFailureReason);
			return false;
		}
```

- Applies rules per actor (order: DataLayer → RuntimeGrid → HLOD) via each rule
  subsystem's `ApplyRulesOnActor` (`:237`), with `bAutoCheckout=false`,
  `bAutoSave=false` — checkout happens at **save** time.
- `PackagesToSave` is `UPROPERTY(Transient)` (must not be serialized — see
  [Topic 4](TransformDrift.md)); flushed every 100 dirty packages, on GC, per pass,
  and in `FinalizeRunInternal`.
- Log categories: `LogWorldPartitionRuleBuilder` (builder) and
  `LogWorldPartitionRules` (rule subsystems, e.g. `Applied RuntimeGrid '%s' to actor '%s'.`).

The real-world batch runner is [`process_li.bat`](AuxiliaryToolsAndWorkflow.md),
which calls this builder with all three rule switches.

---

## `UWorldPartitionFixupNonPartitionedActorsBuilder`

Cleans the three streaming properties off inner actors of **non-partitioned** Level
Instances (where they are meaningless and cause warnings), and optionally the parent
`ALevelInstance` actors.

- Base: `UWorldPartitionBuilder`; `ELoadingMode::Custom`; log
  `LogFixupNonPartitionedActors`.
- Switches (`.cpp:75`):

| Switch | Field | Effect |
|--------|-------|--------|
| `-ForceResave` | `bForceResaveAll` | checkout/save every non-partitioned sub-level regardless of state; clears stale serialized refs |
| `-SaveActorPackages` | `bSaveActorPackages` | checkout + save per-actor OFPA packages |
| `-SkipLevelPackage` | `bSkipLevelPackage` | Phase 2 skips the `.umap` checkout/save (only with `-SaveActorPackages`) |
| `-FixLevelInstanceActors` | `bFixLevelInstanceActors` | enables Phase 3 (fix parent `ALevelInstance` actors) |
| `-DryRun` | `bDryRun` | discovery + detection only; no checkout, no save, writes a report |

- **Three phases**:
  1. **Discover** — `GetNonPartitionedLevels(World)` walks the hierarchy from the root
     and returns the set of non-partitioned sub-levels (+ collects the LI actors that
     target them).
  2. **Fix inner actors** — per level, `FixActorsInNonPartitionedLevel` clears:
     `SetHLODLayer(nullptr)`, `SetRuntimeGrid(NAME_None)`,
     `RemoveAllDataLayers()` + `FixupDataLayers(false)`:

```694:710:D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp
		if (Actor->GetHLODLayer() != nullptr) { Actor->SetHLODLayer(nullptr); ... }
		if (!Actor->GetRuntimeGrid().IsNone()) { Actor->SetRuntimeGrid(NAME_None); ... }
		if (PreviousDataLayerAssets.Num() > 0) {
			Actor->RemoveAllDataLayers();
			Actor->FixupDataLayers(/*bRevertChangesOnLockedDataLayer=*/false);
		}
```
  3. **Fix LI actors** (optional) — same three properties on the parent
     `ALevelInstance`, resolved through `FWorldPartitionReference`.

- Saves use `SAVE_FromAutosave` so the rule subsystem's `OnPackageSaved` hook does
  **not** re-tag the actors during the fixup save (`.cpp:799`).
- **Dry-run report**: `<ProjectSaved>/WorldBuildingEditor/NonPartitionedLI_InnerActors_Report.txt`
  — header (timestamp/world/counts) then, per level, each inner actor line
  `Actor 'Label' (Class): HLODLayer=..., RuntimeGrid=..., DataLayerAssets=N` (`.cpp:1092`).

Example (full fix):

```29:34:D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.h
 *   -run=WorldPartitionBuilderCommandlet
 *   -Builder=WorldPartitionFixupNonPartitionedActorsBuilder
 *   -SCCProvider=Perforce
 *   -ForceResave -SaveActorPackages -FixLevelInstanceActors
 *   -Unattended -NoShaderCompile
 *   LV_Overland
```

> ⚠ Note on `FWorldPartitionHLODFixupHelper`: this is **not** a class the team wrote.
> It is an Epic engine helper referenced only as the *reference implementation* in
> comments ("Same trick as `FWorldPartitionHLODFixupHelper`"). The team's fixup logic
> lives in `UWorldPartitionFixupNonPartitionedActorsBuilder`. The patterns borrowed
> from Epic's helper: `SAVE_FromAutosave`, `MarkPackageDirty()` before OFPA save,
> `FWorldPartitionReference` to pin/load, `Modify(false)` before mutation.

---

## `UWorldPartitionFixupActorFoldersBuilder`

Repairs orphaned/duplicated `UActorFolder` assets by calling the engine's own
`ULevel::FixupActorFolders()` (exposed publicly by an AVA engine patch — see
[Topic 10](EnvironmentAndInfra.md)).

- Switches: `-bOrphans`, `-bDuplicates`, `-bReportOnly`.
- `PreRun` scans the Asset Registry (`FindOrphans` / `FindDuplicatePaths`).
- Temporarily sets `PRIVATE_GIsRunningCommandlet = false` so the duplicate-folder
  branch of `ULevel::FixupActorFolders` runs (it is normally skipped under a
  commandlet, `Level.cpp:3448`).
- Saves through `UWorldPartitionBuilder::SavePackages()` (handles P4 checkout/add).

```42:42:D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupActorFoldersBuilder.h
-LogCmds="LogFixupActorFolders Verbose" -run=WorldPartitionBuilderCommandlet -Builder=WorldPartitionFixupActorFoldersBuilder -SCCProvider=Perforce -Unattended -bDuplicates -bOrphans -NoShaderCompile LV_Overland
```

---

## Supporting builders

- **`UWorldPartitionResaveActorsRecursiveBuilder`** — recursively resaves
  `__ExternalActors__` (and optionally `__ExternalObjects__`) packages, with filters
  `IncludeOutlinerPathSubstrings=`, `ExcludeOutlinerPathSubstrings=`, `ActorClassNames=`,
  `DataLayerNames=`, `MinVerMajor/Minor/Patch=`, `-bReportOnly`,
  `-bIncludeExternalObjects`. `CanProcessNonPartitionedWorlds() == true`. Used to bring
  stale packages up to the current serialization version.
- **`UForceHLODExcludeFromLogBuilder`** — parses a log file of
  `HLODLayerWarnings_*.txt` lines (`for actor '...' in level '...'`), and for each
  matched actor sets `bEnableAutoLODGeneration = false` + `SetHLODLayer(nullptr)`.
  Switches: `-DryRun`, `-Recurse`, `-LogFile=<path>`. Skips non-partitioned LI inner
  actors.

---

## Engine hooks (context, not custom builders)

The MapCheck/streaming-generation error path is engine code with AVA modifications:
`ITokenizedMessageErrorHandler::OnInvalidHLODLayer/OnInvalidRuntimeGrid/OnInvalidReference`
(message strings in [Topic 1](WorldPartitionStreamingProperties.md)) and the
in-memory fixup `FStreamingGenerationActorDescView::SetForcedNoHLODLayer()`. The
disk-writing MapCheck auto-fixer (`WorldPartitionHLODFixup::FixupOne`) is **disabled**.

---

## Operating principles (observed across every builder)

1. **Only modify if necessary.** Every setter is guarded by an equality check; only
   real changes dirty a package; empty changelists are avoided.
2. **Reuse engine behavior.** Call `ULevel::FixupActorFolders`, use
   `FWorldPartitionReference` / `FLevelInstanceEditScope` rather than re-implementing.
3. **Prefix and scope logs.** Dedicated `LogFixup...` / `LogWorldPartitionRule...`
   categories; `-LogCmds="Global none, <cat> display"` keeps output readable.
4. **Report-only / dry-run first**, then run for real.
5. **Iterate with Live Coding** during development to avoid full editor restarts.

## Related changelists

- [Skip non-partitioned LI in RuleBuilder (CL 1727387)](../Reports/P4-History/2026-02-18-08-03-skip-nonpartitioned-li-rulebuilder.md)
- [Add FixupActorFolders builder (CL 1900064)](../Reports/P4-History/2026-05-28-13-20-add-fixup-actorfolders-builder.md)
- [Expose `ULevel::FixupActorFolders` (CL 1896115)](../Reports/P4-History/2026-05-26-14-39-expose-fixupactorfolders.md)
- [WP Rules improvements (CL 1857281)](../Reports/P4-History/2026-04-29-16-33-wp-rules-improvements.md)

## See also

- [Topic 4 — Transform drift](TransformDrift.md) (why `PackagesToSave` is transient)
- [Topic 5 — Perforce source control](PerforceSourceControl.md)
- [Topic 9 — Auxiliary tools (`process_li.bat`)](AuxiliaryToolsAndWorkflow.md)
