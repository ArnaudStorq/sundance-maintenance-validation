# CL 1714709 — Improve icon-path robustness in BaseScriptableToolsEditorModeToolkit

| Field | Value |
|-------|-------|
| Changelist | 1714709 |
| Date | 2026-02-06 11:34 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-46349](https://jira/browse/SUNDANCE-46349) — approved |
| Review | Philippe St-Jean (WBGMontreal) |

## Summary
Hardened icon-path resolution for the scriptable tools editor mode.

## What was done
Improved robustness when resolving the icon path in `BaseScriptableToolsEditorModeToolkit`: validate the plugin lookup, and fall back to the project content directory when the plugin cannot be found.

## Why
If the plugin lookup failed, icon resolution could break. Validating the lookup and providing a project-content fallback makes the toolkit resilient regardless of how the tool is packaged/located.

## Scope & impacted files
- **Total files:** 1 (`edit`)
- `//sun/Dev/Sundance/Plugins/EditorToolExtensions/Source/BaseScriptableToolsEditorMode/Private/BaseScriptableToolsEditorModeToolkit.cpp#8`

## Notes
Small robustness fix in the editor tool extensions plugin.
