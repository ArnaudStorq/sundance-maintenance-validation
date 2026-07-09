# CL 1901233 — Fix orphaned / duplicated Actor Folders

| Field | Value |
|-------|-------|
| Changelist | 1901233 |
| Date | 2026-05-29 07:49 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-41837](https://jira/browse/SUNDANCE-41837) |
| Review | Philippe St-Jean (WBGMontreal); Pierre-Luc Boulet (WBGMontreal) |
| Tested | Editor |

## Summary
Regenerated Actor Folders for `LV_Overland` to remove orphaned and duplicated folder assets.

## What was done
Fixed orphaned / duplicated Actor Folders by running the new fixup builder:

```
-LogCmds="LogFixupActorFolders Verbose" -run=WorldPartitionBuilderCommandlet
-Builder=WorldPartitionFixupActorFoldersBuilder -SCCProvider=Perforce
-Unattended -bDuplicates -bOrphans -NoShaderCompile LV_Overland
```

## Why
`LV_Overland` accumulated orphaned and duplicated `UActorFolder` assets over time. These cause spurious checkouts and Outliner inconsistencies. The commandlet detects and repairs them using the same `ULevel::FixupActorFolders` path as the Editor.

## Scope & impacted files
- **Total files:** 522 (`521 edit`, `1 add`)
- **Area:** `//sun/Dev/Sundance/Content`

## Notes
Uses the builder introduced in CL 1900064. Part of the Outliner / Actor Folder cleanup effort.
