# Sundance Maintenance & Validation

Tools and documentation for the maintenance and validation of the **Sundance**
project (Unreal Engine 5), covering World Partition rules, Map Check
warnings/errors, Outliner organization, and related technical workflows.

This file is the root of the documentation. Every other Markdown file links back to
its parent (a `Parent:` line at the top), so you can always walk up the hierarchy to
here, and down again through the section indexes below.

## Repository structure

```
.
├── ReferenceDocs/              Technical knowledge base (one file per topic)
│   └── WorldPartitionRulesAnalysis/   Deep, per-asset rule-system analysis series
├── WorkDoneByTopic/            Plain-language, why-it-was-done narratives
├── WorkDoneByChangelists/      Per-changelist history
│   └── P4-History/             One report per submitted Perforce changelist
└── Tools/                      Source code / scripts
    └── ProcessLevelInstances/  Batch rule builder for Level Instances
```

## Section indexes

- [**Reference Docs**](ReferenceDocs/README.md) — the technical knowledge base
  (exact classes, methods, log strings) plus the
  [World Partition rule data-asset analysis](ReferenceDocs/WorldPartitionRulesAnalysis.md).
- [**Work Done By Topic**](WorkDoneByTopic/README.md) — plain-language, per-topic
  explanations of the 2026 engineering work.
- [**Work Done By Changelists**](WorkDoneByChangelists/README.md) — one factual report
  per submitted Perforce changelist.

## Documentation — jump to a topic

- [World Partition rules](ReferenceDocs/WorldPartitionRules.md)
- [World Partition streaming properties](ReferenceDocs/WorldPartitionStreamingProperties.md)
- [Fixing MapCheck issues](ReferenceDocs/FixingMapCheckIssues.md)
- [Outliner management](ReferenceDocs/OutlinerManagement.md)
- [Builders & commandlets](ReferenceDocs/BuildersAndCommandlets.md)
- [Custom Tools (editor console commands)](ReferenceDocs/CustomTools.md)

## Custom Tools

In-editor console commands (`FAutoConsoleCommand`) run from the editor console with the
target level open. See [Custom Tools](ReferenceDocs/CustomTools.md) for the full list.

- [`Editor.FixRuntimeGridReferenceErrors`](ReferenceDocs/CustomTools.md#editorfixruntimegridreferenceerrors)
  — fixes `WorldPartitionChangelistValidator` "different runtime grid" reference errors
  from a log file: aligns each referee's `RuntimeGrid` to its referencer, tags both with
  `ExcludeFromRules`, saves + checks out into a described Perforce changelist, and reverts
  a couple's files if either actor fails.

## Tools

- [ProcessLevelInstances](Tools/ProcessLevelInstances/README.md) — runs the
  `WorldPartitionRuleBuilder` commandlet over a list of Level Instances.

## Contributing

- Write everything (docs, code comments, commit messages) in English.
- Put new tools under `Tools/<ToolName>/` with their own `README.md`.
- Put new documentation in `ReferenceDocs/` and link it from
  [`ReferenceDocs/README.md`](ReferenceDocs/README.md).
- Every Markdown file should start with a `Parent:` link to the index (or document)
  one level up, so the documentation hierarchy stays traversable.
