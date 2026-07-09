# Sundance Maintenance & Validation

Tools and documentation for the maintenance and validation of the **Sundance**
project (Unreal Engine 5), covering World Partition rules, Map Check
warnings/errors, Outliner organization, and related technical workflows.

> All content published in this repository is written in **English**.

## Repository structure

```
.
├── docs/                     Documentation (Markdown)
│   ├── world-partition-rules/  Applying World Partition rules
│   ├── map-check/              Fixing MapCheck warnings & errors
│   ├── outliner/               Outliner organization
│   ├── technical/              Setup, conventions, troubleshooting
│   └── images/                 Shared images for the docs
└── tools/                    Source code / scripts
    └── ProcessLevelInstances/  Batch rule builder for Level Instances
```

## Documentation

Start at the [documentation index](docs/README.md), or jump to a section:

- [World Partition Rules](docs/world-partition-rules/README.md)
- [MapCheck warnings & errors](docs/map-check/README.md)
- [Outliner management](docs/outliner/README.md)
- [Technical documentation](docs/technical/README.md)

## Tools

- [ProcessLevelInstances](tools/ProcessLevelInstances/README.md) — runs the
  `WorldPartitionRuleBuilder` commandlet over a list of Level Instances.

## Contributing

- Write everything (docs, code comments, commit messages) in English.
- Put new tools under `tools/<ToolName>/` with their own `README.md`.
- Put new documentation under `docs/<topic>/` and link it from
  [`docs/README.md`](docs/README.md).
