Parent: [Reference Docs](README.md)

# Custom Tools

In-editor **tools** written for the Sundance maintenance work. Unlike the
[builders & commandlets](BuildersAndCommandlets.md) (which run headless through
`WorldPartitionBuilderCommandlet`), these are **interactive** and act on the currently
loaded editor world. These kinds live here:

- **Console commands** — interactive `FAutoConsoleCommand`s you type into the editor
  console (`~`) with the target level already open.
- **Editor-mode UI tools** — buttons and dialogs surfaced inside a dedicated editor mode.
- **Outliner columns & actor tags** — annotations and audit columns that steer or expose
  the World Partition rule system.

## Index

Each tool has its own document in the [`CustomTools/`](CustomTools/) folder. They are
independent — read them in any order.

| Tool | Kind | Purpose |
|------|------|---------|
| [Runtime Grid Reference Tools](CustomTools/RuntimeGridReferenceTools.md) | Console commands | Find (`Editor.ScanRuntimeGridReferenceErrors`) and fix (`Editor.FixRuntimeGridReferenceErrors`) `WorldPartitionChangelistValidator` "different runtime grid" reference errors |
| [Delete World Event](CustomTools/DeleteWorldEvent.md) | Editor-mode UI | Fully delete a World Event (locator + level instances + data layers) from the Overland with live progress and rollback |
| [Exclude From Rules tag](CustomTools/ExcludeFromRulesTag.md) | Actor tag + Outliner column | Freeze an actor against the WorldPartition rule system with the `ExcludeFromRules` tag, and audit excluded actors via the "Rule Exclusion" outliner column |
| [World Partition Batch Converter](CustomTools/WorldPartitionBatchConverter.md) | Editor-mode UI | Batch-convert non-partitioned Content Browser levels to World Partition, with per-level changelists and post-conversion validation |

## See also

- [World Partition rules](WorldPartitionRules.md) — why `ExcludeFromRules` freezes a value
- [Runtime Grid rules](WorldPartitionRulesAnalysis/RuntimeGridRules.md) — how `RuntimeGrid` is normally applied
- [Builders & commandlets](BuildersAndCommandlets.md) — the headless counterpart tools
- [Perforce source control](PerforceSourceControl.md) — checkout-before-save, changelists
- [Level Instances & OFPA](LevelInstancesAndOFPA.md) — external actor packages & Level Instance editing
