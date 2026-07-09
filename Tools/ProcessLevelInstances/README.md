# ProcessLevelInstances

Windows batch script (`process_li.bat`) that runs the
`WorldPartitionBuilderCommandlet` (using the `WorldPartitionRuleBuilder` builder)
on a list of Level Instances, one after another.

For each Level Instance in the list, the script launches the Unreal editor in
command-line mode with the build rules (DataLayer, HLOD, RuntimeGrid) and prints
an `[OK]` / `[ERROR]` status for each run.

## Configuration

Adjust these at the top of `process_li.bat`:

| Variable | Description | Current value |
| --- | --- | --- |
| `EDITOR_CMD` | Path to the Unreal editor executable | `D:\Sun\Engine\Binaries\Win64\UnrealEditor-Win64-DebugGame.exe` |
| `UPROJECT` | Path to the `.uproject` file | `D:\Sun\Sundance\Sundance.uproject` |
| `ARGS` | Arguments passed to the commandlet (contains the `<LI_NAME>` placeholder) | see the file |
| `LI_LIST` | List of Level Instances to process (one name per line) | see the file |

The `<LI_NAME>` placeholder in `ARGS` is automatically replaced, on every
iteration, with the name of the current Level Instance.

## Usage

1. Check / adjust `EDITOR_CMD`, `UPROJECT` and `LI_LIST`.
2. Double-click `process_li.bat`, or run it from a command prompt:

```bat
process_li.bat
```

The script processes all Level Instances, then waits for a key press (`pause`)
before closing the window.

## Related documentation

- [World Partition Rules](../../Docs/WorldPartitionRules/README.md)
- [Outliner management](../../Docs/Outliner/README.md)
