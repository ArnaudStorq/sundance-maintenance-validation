# CL 1844356 — Fix editor startup warnings for LevelViewportToolBar extensions

| Field | Value |
|-------|-------|
| Changelist | 1844356 |
| Date | 2026-04-22 11:04 (Perforce server time) |
| Author | arnaud.storq |
| Client / Branch | arnaud.storq-sun-2 (`//sun/Dev`) |
| Type | `@MINOR` |
| Category | `$TOOLS` |
| Jira | [SUNDANCE-54425](https://jira/browse/SUNDANCE-54425) |
| Review | Philippe St-Jean (WBGMontreal); Pierre-Luc Boulet (WBGMontreal) |
| Tested | Editor |

## Summary
Migrated deprecated viewport toolbar extension points to the new Tool Menus API to silence startup warnings.

## What was done
Fixed editor startup warnings related to `LevelViewportToolBar`:

```
LogPanelExtensions: Warning: Extension panel id "LevelViewportToolBar.LeftExtension" has been deprecated. Please extend the "LevelEditor.ViewportToolbar" Tool Menus menu instead.
... (Middle/Right extensions, same warning)
```

Updated the extension registrations across several plugins to use `LevelEditor.ViewportToolbar` instead.

## Why
The old extension panel ids were deprecated; each one logged a warning at startup. Moving to the Tool Menus API removes the warnings and future-proofs the toolbar extensions.

## Scope & impacted files
- **Total files:** 8 (`edit`) across DayNight, EditorImprovements, PlatformAssetOverrides, Seasons and Weather plugins, plus `WorldBuildingEditorModule.cpp`.

## Notes
Startup log cleanup spanning multiple editor plugins.
