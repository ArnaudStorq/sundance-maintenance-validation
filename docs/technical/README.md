# Technical documentation (Sundance / UE5)

General technical documentation for the Sundance maintenance and validation
workflow.

## Commandlet setup

Most batch operations (rule building, HLOD, validation) run through the Unreal
**editor commandlet** interface rather than the editor UI.

### Prerequisites

- A built editor executable (`UnrealEditor-Cmd.exe`, or a configuration such as
  `UnrealEditor-Win64-DebugGame.exe`).
- The `Sundance.uproject` file.
- A synced, up-to-date workspace (assets referenced by the maps must be present
  locally, and ideally submitted to source control).

### General invocation

```bat
UnrealEditor-Cmd.exe "<path>\Sundance.uproject" -run=<CommandletName> [options]
```

Useful shared switches:

| Switch | Purpose |
| --- | --- |
| `-run=<Commandlet>` | Selects the commandlet to run |
| `-BuildMachine` | Marks the run as automated (affects prompts/telemetry) |
| `-Unattended` | Never blocks on a modal dialog; required for CI/batch |
| `-LogCmds="..."` | Filters log categories/verbosity to reduce noise |
| `-nosplash -nullrhi` | Optional: skip splash / run without a rendering device |

### Filtering logs

Batch runs are far easier to read when log output is scoped. Example used by the
rule builder:

```
-LogCmds="Global none,LogWorldPartitionRules display,LogWorldPartitionRuleBuilder display,LogWorldPartitionBuilder warning,LogCommandletPackageHelper error"
```

This silences everything (`Global none`) except the categories relevant to the
task. See [World Partition Rules > Reading the logs](../world-partition-rules/README.md#reading-the-logs).

## Conventions

- **Language**: everything published (docs, code, comments, commit messages) is
  written in English.
- **Tools** live under `tools/<ToolName>/` with their own `README.md`.
- **Docs** live under `docs/<topic>/` and are linked from the
  [documentation index](../README.md).
- **Paths**: absolute paths in scripts (editor, `.uproject`) are environment
  specific — document the expected values and keep them at the top of each
  script.

## Validation checklist (before submitting)

1. Apply the [World Partition rules](../world-partition-rules/README.md) to the
   changed Level Instances / maps.
2. Run **Build > Map Check** and resolve entries
   ([catalog](../map-check/README.md)) — errors first, then warnings.
3. Confirm the [Outliner](../outliner/README.md) paths match the intended rule
   filters.
4. Rebuild HLOD / lighting if geometry or assignments changed.
5. Verify streaming in-editor (World Partition minimap, Data Layer toggles).
6. Submit assets **and** their dependencies together.

## Troubleshooting

| Symptom | Likely cause | First check |
| --- | --- | --- |
| Commandlet exits immediately with an error | Wrong editor/`.uproject` path | Verify `EDITOR_CMD` and `UPROJECT` |
| `LogCommandletPackageHelper` errors | Missing/locked packages | Sync workspace, ensure files are checked out |
| Rules don't affect an actor | Outliner path not matched | Review `Contain`/`Discard` substrings |
| Stale proxies at distance | HLOD not rebuilt | Run the HLOD builder |

## See also

- [World Partition Rules](../world-partition-rules/README.md)
- [MapCheck warnings & errors](../map-check/README.md)
- [Outliner management](../outliner/README.md)
