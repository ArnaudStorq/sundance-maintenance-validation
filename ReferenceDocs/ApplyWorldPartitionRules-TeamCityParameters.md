Parent: [TeamCity jobs](TeamCityJobs.md)

# Apply World Partition Rules - TeamCity parameters

The five `wp-rules.*` parameters of the
[Apply World Partition Rules](https://slc-teamcity.wbiegames.com/buildConfiguration/Sundance_Dev_Tools_ApplyWorldPartitionRules#all-projects)
job pick the map and the slice of actors `WorldPartitionRuleBuilder` processes.

Source of truth: the constructor and the `DoesActor*Match` filters of
`D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionRuleBuilder.cpp`,
and the job's build step on the TeamCity server.

## Contents

- [How the parameters reach the builder](#how-the-parameters-reach-the-builder)
- [Summary](#summary)
- [Matching rules](#matching-rules)
- [The Outliner path](#the-outliner-path)
- [Parameters in detail](#parameters-in-detail)
  - [`wp-rules.currentMap`](#wp-rulescurrentmap)
  - [`wp-rules.contain_outliner_path_substrings`](#wp-rulescontain_outliner_path_substrings)
  - [`wp-rules.discard_outliner_path_substrings`](#wp-rulesdiscard_outliner_path_substrings)
  - [`wp-rules.actor_class_names`](#wp-rulesactor_class_names)
  - [`wp-rules.label`](#wp-ruleslabel)
- [Examples](#examples)
- [See also](#see-also)

## How the parameters reach the builder

The job's build step writes the `wp-rules.*` values straight into the commandlet line
(abridged):

```
UnrealEditor-Cmd.exe Sundance -SCCProvider=Perforce
    -run=WorldPartitionBuilderCommandlet -Builder=WorldPartitionRuleBuilder
    -DataLayerRules -HLODLayerRules -RuntimeGridRules
    -ContainOutlinerPathSubstrings="%wp-rules.contain_outliner_path_substrings%"
    -DiscardOutlinerPathSubstrings="%wp-rules.discard_outliner_path_substrings%"
    -ActorClassNames="%wp-rules.actor_class_names%"
    %project.ddc_override% -BuildMachine -Unattended %wp-rules.currentMap%
```

The local script `ApplyWorldPartitionRules.bat` passes none of these three filters. Only the
TeamCity step does.

To change them for one run, use **Run > ... (Run Custom Build) > Parameters**.

## Summary

| Parameter | Commandlet argument | Default | Purpose |
|-----------|---------------------|---------|---------|
| `wp-rules.currentMap` | map name (positional, last) | `LV_Overland` | Map to process |
| `wp-rules.contain_outliner_path_substrings` | `-ContainOutlinerPathSubstrings=` | empty | Keep only actors whose Outliner path contains one of these |
| `wp-rules.discard_outliner_path_substrings` | `-DiscardOutlinerPathSubstrings=` | empty | Skip actors and Level Instances whose Outliner path contains one of these |
| `wp-rules.actor_class_names` | `-ActorClassNames=` | empty | Keep only actors whose class name contains one of these |
| `wp-rules.label` | none | `LV_Overland` | Display name of the run in TeamCity |

## Matching rules

The three filter parameters share the same parsing and matching:

- **Comma-separated list.** Whitespace around each entry is trimmed and empty entries are
  dropped (`ParseIntoArray(..., TEXT(","), true)` then `TrimStartAndEnd`).
- **Empty value = no filter.** Every actor passes.
- **Case-insensitive substring match** (`FString::Contains`). `mission` matches `Missions` and
  `LI_Mission_Intro`.
- **OR inside one parameter.** One matching entry is enough.
- **AND between parameters.** In `ShouldProcessActor` an actor must pass the class filter, not
  be discarded, and pass the contain filter, in that order.
- **Discard wins over contain.** An actor matching both is skipped.
- **No double quotes in the values.** The step already wraps each value in quotes.

The same filters also scope the RuntimeGrid reference-conflict pass (`IsActorInScope`).

## The Outliner path

The contain and discard filters test the actor's **Outliner path**, built by
`UWorldPartitionOutlinerPathRegistry::GetOutlinerFullPath`: the label of every node from the
root down to the actor (folders, Level Instances, then the actor label), joined with `/`:

```
LV_Overland/LI_Hogsmeade/LI_HM_StreetDressing_EXT/LI_HW_Book_Row_I
```

Use the labels shown in the World Outliner, not asset or package paths.

## Parameters in detail

### `wp-rules.currentMap`

The map the commandlet loads, e.g. `LV_Overland`. It is the positional argument at the end of
the command line. The clean and revert steps also print it, and it appears in the description of
the submitted changelist.

### `wp-rules.contain_outliner_path_substrings`

Restricts the run to actors whose Outliner path contains at least one of the substrings.

- **Typical use:** split the nightly load into one run per area, e.g. `Hogwarts`,
  `Hogsmeade`, `Missions`, `Dungeons`.
- **Level Instances:** a Level Instance is opened only if one of its own actors matches,
  or if it contains a nested Level Instance (which may hold matching actors).
  See `ShouldProcessLevelInstance`.
- **Submit message:** the value is copied into the submitted changelist:
  `Applied WorldPartition rules to <map> (Filter used: '<value>')`.

### `wp-rules.discard_outliner_path_substrings`

Skips actors whose Outliner path contains at least one of the substrings.

- It is tested before the contain filter, so it always wins.
- **Level Instances:** a discarded Level Instance is never opened, so its whole subtree is
  skipped (`ProcessLevelInstancesInWorldPartition`).
- **Typical use:** cover "the rest of the map" after the per-area runs, e.g.
  `mission,dungeon,hogwarts,hogsmeade` with the label `Overland Only`.

### `wp-rules.actor_class_names`

Restricts the run to actors whose class name contains at least one of the entries.

- The value is compared with the **short class name**, `UClass::GetName()`: no C++ `A` prefix
  and no package path.

  | Value | Result |
  |-------|--------|
  | `LevelInstance` | matches `ALevelInstance` |
  | `StaticMeshActor` | matches `AStaticMeshActor` |
  | `ALevelInstance` | never matches (the `A` prefix is not part of the name) |
  | `/Script/CoreUObject.Class'/Script/Engine.LevelInstance'` | never matches (a full path is never a substring of a short name) |

- Actors are filtered from their descriptor, which gives the **native** class
  (`GetActorNativeClass()`). So a Blueprint deriving from `ALevelInstance` matches
  `LevelInstance`.
- **Substring match:** an entry also catches every class whose name contains it. For example,
  `PlacedFoliage` matches the `PlacedFoliage*` classes.
- The class filter decides which actors the rules are written on. It **does not limit the
  Level Instance traversal**: Level Instances are still opened (subject to the contain and
  discard filters) so their inner actors can be tested. A class filter cuts processing time,
  not opening time.

Example: `LevelInstance` applies the rules only to Level Instance actors, both at the map level
and nested inside other Level Instances.

### `wp-rules.label`

Free text, **not passed to the commandlet**. It only names the run in TeamCity, next to the
build number (e.g. `#2150062 ('Hogwarts')`), so you can tell which slice a build processed.
Make it describe the filters: `Hogwarts`, `Overland Only`, `LevelInstance`.

## Examples

Values taken from past runs of the job, plus the class-filter case:

| Goal | contain | discard | actor_class_names | label |
|------|---------|---------|-------------------|-------|
| Whole map | | | | `LV_Overland` |
| Hogwarts only | `Hogwarts` | | | `Hogwarts` |
| Missions only | `Missions` | | | `Missions` |
| Dungeons only | `Dungeons` | | | `Dungeons` |
| Everything outside the per-area runs | | `mission,dungeon,hogwarts,hogsmeade` | | `Overland Only` |
| World bitmap proxies outside the areas | | `hogsmeade,hogwarts,mission,worldevent,dungeon` | | `WorldBitmapStreamingProxy` |
| Level Instance actors only | | | `LevelInstance` | `LevelInstance` |

## See also

- [TeamCity jobs](TeamCityJobs.md#apply-world-partition-rules) - schedule, outputs and the
  validation build
- [Builders & commandlets](BuildersAndCommandlets.md#uworldpartitionrulebuilder) - the
  builder's other switches
- [`-ReportOnly` vs `-ValidateOnly`](ReportOnlyVsValidateOnly.md) - the read-only modes
- [Outliner management](OutlinerManagement.md) - how the Outliner tree is organized

Back to [TeamCity jobs](TeamCityJobs.md).
