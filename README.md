# Sundance Maintenance & Validation

Tools and documentation for the maintenance and validation of the **Sundance**
project (Unreal Engine 5), covering World Partition rules, Map Check
warnings/errors, Outliner organization, and related technical workflows.

> All content published in this repository is written in **English**.

## Repository structure

```
.
├── Reference/                  Technical knowledge base (flat, one file per topic)
├── WorkDoneByTopic/            Plain-language, why-it-was-done narratives
├── WorkDoneByChangelists/      Per-changelist history (P4-History/)
└── Tools/                      Source code / scripts
    └── ProcessLevelInstances/  Batch rule builder for Level Instances
```

## Documentation

Start at the [Reference index](Reference/README.md), or jump to a topic:

- [World Partition rules](Reference/WorldPartitionRules.md)
- [Fixing MapCheck issues](Reference/FixingMapCheckIssues.md)
- [Outliner management](Reference/OutlinerManagement.md)
- [Builders & commandlets](Reference/BuildersAndCommandlets.md)

## Tools

- [ProcessLevelInstances](Tools/ProcessLevelInstances/README.md) — runs the
  `WorldPartitionRuleBuilder` commandlet over a list of Level Instances.

## Contributing

- Write everything (docs, code comments, commit messages) in English.
- Put new tools under `Tools/<ToolName>/` with their own `README.md`.
- Put new documentation in `Reference/` as a single flat topic file and link it from
  [`Reference/README.md`](Reference/README.md).
