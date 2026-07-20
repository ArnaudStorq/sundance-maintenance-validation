Parent: [Reference Docs](README.md)

# Custom Tools

In-editor **tools** written for the Sundance maintenance work. Unlike the
[builders & commandlets](BuildersAndCommandlets.md) (which run headless through
`WorldPartitionBuilderCommandlet`), these are **interactive** and act on the currently
loaded editor world. Two kinds live here:

- **Console commands** — interactive `FAutoConsoleCommand`s you type into the editor
  console (`~`) with the target level already open.
- **Editor-mode UI tools** — buttons and dialogs surfaced inside a dedicated editor mode.

## Index

Each tool has its own document in the [`CustomTools/`](CustomTools/) folder. They are
independent — read them in any order.

| Tool | Kind | Purpose |
|------|------|---------|
| [`Editor.FixRuntimeGridReferenceErrors`](CustomTools/FixRuntimeGridReferenceErrors.md) | Console command | Fix `WorldPartitionChangelistValidator` "different runtime grid" reference errors from a log file |
| [Delete World Event](CustomTools/DeleteWorldEvent.md) | Editor-mode UI | Fully delete a World Event (locator + level instances + data layers) from the Overland with live progress and rollback |

## See also

- [World Partition rules](WorldPartitionRules.md) — why `ExcludeFromRules` freezes a value
- [Runtime Grid rules](WorldPartitionRulesAnalysis/RuntimeGridRules.md) — how `RuntimeGrid` is normally applied
- [Builders & commandlets](BuildersAndCommandlets.md) — the headless counterpart tools
- [Perforce source control](PerforceSourceControl.md) — checkout-before-save, changelists
- [Level Instances & OFPA](LevelInstancesAndOFPA.md) — external actor packages & Level Instance editing
