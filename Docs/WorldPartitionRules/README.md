# World Partition Rules (Sundance / UE5)

This section documents how **World Partition Rules** are applied and maintained
in the Sundance project.

## Overview

World Partition is Unreal Engine 5's automatic streaming and data-management
system for large worlds. Instead of a single monolithic level, the world is
split into a grid of streaming cells that are loaded and unloaded around the
player. The way actors are assigned to those cells, to data layers, and to HLOD
layers is driven by a set of **rules**.

In Sundance, these rules are applied both:

- **Interactively**, from the editor, and
- **In batch**, through the `WorldPartitionBuilderCommandlet` with the
  `WorldPartitionRuleBuilder` builder (see
  [`Tools/ProcessLevelInstances`](../../Tools/ProcessLevelInstances/README.md)).

## Key concepts

### Runtime Grid

The Runtime Grid controls which streaming cell an actor belongs to (cell size,
loading range, HLOD behavior). Assigning an actor to the correct grid is what
keeps streaming performant: cells that are too large stream too much content,
cells that are too small multiply overhead.

### Data Layers

Data Layers let you group actors so they can be enabled/disabled independently
(for example, gameplay states, quest variants, editor-only content). Rules
assign actors to the appropriate Data Layer automatically instead of relying on
manual tagging.

### HLOD Layers

Hierarchical Level of Detail (HLOD) generates simplified proxy meshes that
represent unloaded cells at a distance. HLOD rules define which HLOD layer an
actor contributes to, and whether it is included in HLOD generation at all.

## The rule builder

The `WorldPartitionRuleBuilder` applies the project's rule set to a target
(a Level Instance, a set of actors, or a whole map). The relevant switches are:

| Switch | Effect |
| --- | --- |
| `-DataLayerRules` | Apply Data Layer assignment rules |
| `-HLODLayerRules` | Apply HLOD layer assignment rules |
| `-RuntimeGridRules` | Apply Runtime Grid assignment rules |
| `-ContainOutlinerPathSubstrings="..."` | Restrict processing to actors whose Outliner path contains the given substrings |
| `-DiscardOutlinerPathSubstrings="..."` | Exclude actors whose Outliner path contains the given substrings |
| `-BuildMachine -Unattended` | Non-interactive mode, suitable for automation |

> The Outliner path filters tie directly into how the
> [Outliner](../Outliner/README.md) is organized. Consistent Outliner naming is
> what makes rule targeting reliable.

### Running the rule builder in batch

The builder runs through the `WorldPartitionBuilderCommandlet`. A single
invocation looks like:

```bat
UnrealEditor-Cmd.exe "Sundance.uproject" ^
  -run=WorldPartitionBuilderCommandlet ^
  -Builder=WorldPartitionRuleBuilder ^
  -DataLayerRules -HLODLayerRules -RuntimeGridRules ^
  -ContainOutlinerPathSubstrings="" -DiscardOutlinerPathSubstrings="" ^
  -BuildMachine -Unattended ^
  <TargetLevelInstance>
```

To process many Level Instances in one pass, use the
[`ProcessLevelInstances`](../../Tools/ProcessLevelInstances/README.md) script,
which loops over a list and reports `[OK]` / `[ERROR]` per entry.

### Reading the logs

The builder narrows engine logging to the categories that matter for a rule
pass. Watch these in the output:

| Log category | What it tells you |
| --- | --- |
| `LogWorldPartitionRules` | Which rules matched and what they assigned |
| `LogWorldPartitionRuleBuilder` | High-level builder progress per target |
| `LogWorldPartitionBuilder` | Streaming/build-level warnings |
| `LogCommandletPackageHelper` | Package load/save errors (blockers) |

A run that finishes without `LogCommandletPackageHelper` errors and with the
expected rule assignments in `LogWorldPartitionRules` is considered successful.

## Recommended workflow

1. **Organize the Outliner** so actors sit under predictable, rule-friendly
   paths (see [Outliner management](../Outliner/README.md)).
2. **Apply the rules**, either interactively or via the batch tool for many
   Level Instances at once.
3. **Run a Map Check** and resolve any warnings/errors that the rule pass
   surfaced (see [MapCheck](../MapCheck/README.md)).
4. **Validate streaming** in-editor (World Partition minimap, data layer
   toggles) before submitting.

## Common pitfalls

- Actors left on the **default** grid/layer because their Outliner path did not
  match any rule.
- **HLOD** not regenerated after a rule change, leaving stale proxy meshes.
- Data Layer assignments that conflict between a Level Instance and its parent
  world.

## See also

- [MapCheck warnings & errors](../MapCheck/README.md)
- [Outliner management](../Outliner/README.md)
- [ProcessLevelInstances tool](../../Tools/ProcessLevelInstances/README.md)
