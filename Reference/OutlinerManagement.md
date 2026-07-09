# Outliner management (Sundance / UE5)

This section documents how the **World Outliner** is organized in Sundance and
why that organization matters for World Partition and automated tooling.

## Why the Outliner matters

Beyond being a convenience for artists, the Outliner **path** of an actor is
used as an input by the [World Partition rules](WorldPartitionRules.md).
The rule builder can target or exclude actors based on substrings of their
Outliner path:

- `-ContainOutlinerPathSubstrings="..."` — only process matching actors.
- `-DiscardOutlinerPathSubstrings="..."` — skip matching actors.

This means a well-structured, consistent Outliner is a prerequisite for reliable
rule application. Actors placed under an unexpected folder may silently miss the
rules meant for them.

## Naming and folder conventions

Keep folder structure predictable so rules and filters stay stable:

- Use consistent, descriptive folder names (avoid ad-hoc or temporary names).
- Group actors by function/area in a way that matches how rules are written.
- Avoid moving actors between folders without checking the impact on rule
  targeting.

> Document the project's concrete folder taxonomy here as it stabilizes (top
> level folders, naming prefixes, and which folders map to which rules).

## Common problems

| Problem | Consequence | Fix |
| --- | --- | --- |
| Actor in the wrong folder | Misses its intended World Partition rule | Move it to the correct path, re-run the rule builder |
| Inconsistent folder naming | Rule substring filters miss actors | Standardize names, update filters |
| Flat / unorganized Outliner | Hard to target subsets in batch tooling | Introduce a consistent folder hierarchy |
| Actors at the root of a Level Instance | Ambiguous rule matching | Nest them under a named folder |

## Workflow

1. Organize actors under consistent, rule-aware folders.
2. Verify that the intended `Contain` / `Discard` substrings match the paths.
3. Apply [World Partition rules](WorldPartitionRules.md).
4. Run a [Map Check](MapCheckCatalog.md) to catch actors that fell through.

## See also

- [World Partition Rules](WorldPartitionRules.md)
- [MapCheck warnings & errors](MapCheckCatalog.md)
- [ProcessLevelInstances tool](../Tools/ProcessLevelInstances/README.md)
