# Sundance Maintenance & Validation

Tools and documentation for the maintenance and validation of the **Sundance**
project (Unreal Engine 5), covering World Partition rules, Map Check
warnings/errors, Outliner organization, and related technical workflows.

> All content published in this repository is written in **English**.

## Repository structure

```
.
├── Docs/                       Documentation (Markdown)
│   ├── WorldPartitionRules/    Applying World Partition rules
│   ├── MapCheck/               Fixing MapCheck warnings & errors
│   ├── Outliner/               Outliner organization
│   └── Technical/              Setup, conventions, troubleshooting
└── Tools/                      Source code / scripts
    └── ProcessLevelInstances/  Batch rule builder for Level Instances
```

## Documentation

Start at the [documentation index](Docs/README.md), or jump to a section:

- [World Partition Rules](Docs/WorldPartitionRules/README.md)
- [MapCheck warnings & errors](Docs/MapCheck/README.md)
- [Outliner management](Docs/Outliner/README.md)
- [Technical documentation](Docs/Technical/README.md)

## Tools

- [ProcessLevelInstances](Tools/ProcessLevelInstances/README.md) — runs the
  `WorldPartitionRuleBuilder` commandlet over a list of Level Instances.

## Contributing

- Write everything (docs, code comments, commit messages) in English.
- Put new tools under `Tools/<ToolName>/` with their own `README.md`.
- Put new documentation under `Docs/<Topic>/` and link it from
  [`Docs/README.md`](Docs/README.md).
