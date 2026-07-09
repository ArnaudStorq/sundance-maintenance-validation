Parent: [Reference Docs](README.md)

# Auxiliary tools & workflow

The supporting tools, editor extensions, scripts and dev-workflow details that make
the World Partition cleanup practical.

---

## Outliner columns (inspection)

Custom columns registered in
`FWorldBuildingEditorModule::RegisterOutlinerColumns()`
(`WorldBuildingEditorModule.cpp:105`). All work for both loaded actors
(`FActorTreeItem`) and unloaded WP actor descriptors (`FActorDescTreeItem`).

| Column class | ID | Header | Shows |
|--------------|----|--------|-------|
| `FActorPathOutlinerColumn` | `ActorPathColumn` | "Actor Path Outliner" | full Outliner path via `UWorldPartitionOutlinerPathRegistry::GetOutlinerFullPath()` |
| `FIncludeInHLODColumn` | `IncludeInHLODColumn` | "Include in HLOD" | `"Yes"` from `IsHLODRelevant()` / `GetActorIsHLODRelevant()` |
| `FRuntimeGridOutlinerColumn` | `RuntimeGridColumn` | "Runtime Grid" | `GetRuntimeGrid()` (loaded actors resolved on a background `AsyncTask`) |
| `FHLODLayerOutlinerColumn` | `HLODLayerColumn` | "HLOD Layer" | `GetHLODLayer()` name |

For actors under a **non-partitioned parent** Level Instance, the columns show
**"Non-Partitioned Parent"** instead of a value — because those actors inherit their
settings and per-actor values are meaningless. Logic:
`FWorldPartitionOutlinerColumnUtils::ShouldShowNonPartitionedParent(actor)` (true when
the parent `ILevelInstanceInterface`'s loaded level is not a partitioned world) +
`MakeNonPartitionedParentWidget()`.

The hierarchy-export command/commandlet (`Outliner.ExportAllHierarchy`) dumped the full
folder/actor tree to CSV + HTML so the structure could be reviewed offline before the
Outliner restructure.

---

## `process_li.bat` (batch rule runner)

`D:\CustomGitRepos\sundance-maintenance-validation\Tools\ProcessLevelInstances\process_li.bat`
runs `WorldPartitionRuleBuilder` over a list of Level Instances, one editor launch per
name.

```10:14:D:\CustomGitRepos\sundance-maintenance-validation\Tools\ProcessLevelInstances\process_li.bat
set "EDITOR_CMD=D:\Sun\Engine\Binaries\Win64\UnrealEditor-Win64-DebugGame.exe"
set "UPROJECT=D:\Sun\Sundance\Sundance.uproject"
set "ARGS=-LogCmds="Global none,LogWorldPartitionRules display,LogWorldPartitionRuleBuilder display,LogWorldPartitionBuilder warning,LogCommandletPackageHelper error" -run=WorldPartitionBuilderCommandlet -Builder=WorldPartitionRuleBuilder -DataLayerRules -HLODLayerRules -RuntimeGridRules -ContainOutlinerPathSubstrings="" -DiscardOutlinerPathSubstrings="" -BuildMachine -Unattended <LI_NAME>"
```

- `<LI_NAME>` is substituted per iteration via delayed expansion
  `set "CURRENT_ARGS=!ARGS:<LI_NAME>=%%L!"` (`:41`), where `%%L` comes from `LI_LIST`.
- Final invocation: `"%EDITOR_CMD%" "%UPROJECT%" !CURRENT_ARGS!`.

> ⚠ Gotcha: if the `<LI_NAME>` placeholder is not substituted (e.g. list read wrong,
> `enabledelayedexpansion` missing), the literal token `<LI_NAME>` is passed as the map
> and every run fails. Verify the echoed command line before trusting a batch.

---

## Blueprint / Editor Utility surfaces

- **Scriptable Tools** editor mode (via `EditorToolExtensions`) surfaces custom tools
  with toolbar icons; the icon-path resolution was hardened to fall back to the project
  content dir when the plugin lookup fails (see
  [`WorkDoneByTopic/ScriptableTools.md`](../WorkDoneByTopic/ScriptableTools.md)).
- **Asset Action Utility** vs **Scripted Asset Actions**: an *Asset Action Utility*
  Blueprint adds entries to the content-browser right-click submenu — a known pitfall is
  it appearing in an unexpected submenu; *Scripted Asset Actions* is the newer,
  more predictable mechanism. `ConvertLevelsToWorldPartition`
  ([converting levels to World Partition](ConvertingLevelsToWorldPartition.md)) is a
  `BlueprintCallable` that can be driven from such a utility.

---

## Recurring log extraction

The invalid-HLOD-layer warnings were captured to `HLODLayerWarnings_*.txt` and the
**unique list of levels (with occurrence counts)** was extracted from those logs to
drive fixes. `UForceHLODExcludeFromLogBuilder` consumes exactly this format
(lines `for actor '...' in level '...'`).

---

## Commandlet setup

Most batch operations (rule building, HLOD, validation) run through the Unreal
**editor commandlet** interface rather than the editor UI.

Prerequisites:

- A built editor executable (`UnrealEditor-Cmd.exe`, or a configuration such as
  `UnrealEditor-Win64-DebugGame.exe`).
- The `Sundance.uproject` file.
- A synced, up-to-date workspace (assets referenced by the maps must be present locally,
  and ideally submitted to source control).

The canonical invocation shape and the full switch list are documented in the
[World Partition builders catalog](WorldPartitionBuildersCatalog.md); the maintenance
subset is in [builders & commandlets](BuildersAndCommandlets.md).

### Filtering logs

Batch runs are far easier to read when log output is scoped. Example used by the rule
builder:

```
-LogCmds="Global none,LogWorldPartitionRules display,LogWorldPartitionRuleBuilder display,LogWorldPartitionBuilder warning,LogCommandletPackageHelper error"
```

This silences everything (`Global none`) except the categories relevant to the task.

---

## Validation checklist (before submitting)

1. Apply the [World Partition rules](WorldPartitionRules.md) to the changed Level
   Instances / maps.
2. Run **Build > Map Check** and resolve entries (see the
   [MapCheck fix playbook](FixingMapCheckIssues.md)) — errors first, then warnings.
3. Confirm the [Outliner](OutlinerManagement.md) paths match the intended rule filters.
4. Rebuild HLOD / lighting if geometry or assignments changed.
5. Verify streaming in-editor (World Partition minimap, Data Layer toggles).
6. **Diff before submit** — a resave must not change `RelativeLocation/Rotation/Scale3D`
   ([transform drift](TransformDrift.md)); revert any package that drifted.
7. Submit assets **and** their dependencies together (the changelist/Peeves validators
   enforce this — see [Perforce source control](PerforceSourceControl.md) and
   [Peeves submit validation](PeevesSubmitValidation.md)).

---

## Troubleshooting

| Symptom | Likely cause | First check |
| --- | --- | --- |
| Commandlet exits immediately with an error | Wrong editor/`.uproject` path | Verify `EDITOR_CMD` and `UPROJECT` |
| `LogCommandletPackageHelper` errors | Missing/locked packages | Sync workspace, ensure files are checked out |
| Rules don't affect an actor | Outliner path not matched | Review `Contain`/`Discard` substrings |
| Stale proxies at distance | HLOD not rebuilt | Run the HLOD builder |
| `<LI_NAME>` passed as the map | placeholder not substituted in `process_li.bat` | Verify the echoed command line |

---

## The documentation repo itself

`D:\CustomGitRepos\sundance-maintenance-validation` (this repo) is a **git** repo
(separate from the Perforce game depot). Structure: `ReferenceDocs/` (this knowledge base),
`WorkDoneByTopic/`, `WorkDoneByChangelists/P4-History/`, and `Tools/`. Conventions:
**everything in English**; commit messages in English; one tool per `Tools/<Name>/` with
its own README.

---

## UE compilation errors resolved (reference)

Common build errors hit while developing the builders and their fixes:

| Error | Meaning | Fix |
|-------|---------|-----|
| **C2665** on `GetNameSafe` | no overload matched the argument type | pass a `const UObject*` (or the right overload); include the header that declares it |
| **C2338** with `TWeakObjectPtr` | static_assert: `TWeakObjectPtr` requires a `UObject`-derived type | use the correct pointer/handle type for the object |
| **C2065** `LogWorldPartition` undeclared | log category not visible in this TU | include the header that `DECLARE`s it, or use the module's own log category |
| Circular dependency in `Engine.Build.cs` | two modules depend on each other | move the shared code, or use a public/private dependency split / interface to break the cycle |

---

## Related changelists

- [Add Outliner columns (CL 1690531)](../WorkDoneByChangelists/P4-History/2026-01-27-08-13-add-outliner-columns.md)
- [Add `Outliner.ExportAllHierarchy` (CL 1707391)](../WorkDoneByChangelists/P4-History/2026-02-03-07-43-add-outliner-export-hierarchy.md)
- [Outliner "Non Partitioned Parent" (CL 1731394)](../WorkDoneByChangelists/P4-History/2026-02-20-05-36-outliner-nonpartitioned-parent-message.md)
- [`@BUILDFIX` undo Outliner column utils (CL 1729621)](../WorkDoneByChangelists/P4-History/2026-02-19-11-54-buildfix-undo-outliner-columns.md)
- [ScriptableTools icon path robustness (CL 1714709)](../WorkDoneByChangelists/P4-History/2026-02-06-11-34-scriptabletools-icon-path-robustness.md)

## See also

- [Builders & commandlets](BuildersAndCommandlets.md)
- [Outliner management](OutlinerManagement.md)
- Plain-language: [`WorkDoneByTopic/Outliner.md`](../WorkDoneByTopic/Outliner.md), [`WorkDoneByTopic/EditorStabilityAndWarnings.md`](../WorkDoneByTopic/EditorStabilityAndWarnings.md)
