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
  [`tools/ProcessLevelInstances`](../../tools/ProcessLevelInstances/README.md)).

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
> [Outliner](../outliner/README.md) is organized. Consistent Outliner naming is
> what makes rule targeting reliable.

## Recommended workflow

1. **Organize the Outliner** so actors sit under predictable, rule-friendly
   paths (see [Outliner management](../outliner/README.md)).
2. **Apply the rules**, either interactively or via the batch tool for many
   Level Instances at once.
3. **Run a Map Check** and resolve any warnings/errors that the rule pass
   surfaced (see [MapCheck](../map-check/README.md)).
4. **Validate streaming** in-editor (World Partition minimap, data layer
   toggles) before submitting.

## Common pitfalls

- Actors left on the **default** grid/layer because their Outliner path did not
  match any rule.
- **HLOD** not regenerated after a rule change, leaving stale proxy meshes.
- Data Layer assignments that conflict between a Level Instance and its parent
  world.

## See also

- [MapCheck warnings & errors](../map-check/README.md)
- [Outliner management](../outliner/README.md)
- [ProcessLevelInstances tool](../../tools/ProcessLevelInstances/README.md)
