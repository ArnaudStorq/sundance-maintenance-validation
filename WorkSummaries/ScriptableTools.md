# Scriptable Tools

*A plain-language guide to the Scriptable Tools editor mode work in 2026.*

---

## 1. What are Scriptable Tools?

Unreal's **Scriptable Tools** framework lets a team build custom editor tools
(buttons, brushes, actions) that appear in a dedicated **editor mode** — without
writing a full C++ editor module for each one. The project's tooling (including some
of the Outliner/World Partition helpers) is surfaced through this mode via the
`EditorToolExtensions` plugin.

Each tool typically has an **icon** shown in the toolbar. To display that icon, the
code has to **resolve the icon's file path** at runtime.

## 2. The problem

The icon path was being resolved by looking the tool up inside its **plugin**. If
that plugin lookup failed for any reason (e.g. the tool is packaged/located
differently than expected), icon resolution could break.

> Simple version: the code assumed "the icon always lives in my plugin folder". When
> that assumption didn't hold, it had nowhere to look.

## 3. The fix

`BaseScriptableToolsEditorModeToolkit` was made **more robust** when resolving the
icon path:

1. **Validate the plugin lookup** first (don't assume it succeeded).
2. **Fall back to the project content directory** when the plugin can't be found.

So there are now two places to find the icon, and the code checks that the first one
actually worked before using it.

## 4. Why it matters

This is a small **robustness / defensive-programming** fix. It doesn't add a feature;
it prevents a failure. The payoff is that the tool's icon (and the tool) keep working
regardless of how or where the plugin is loaded — no broken toolbar, no error spam.

> General lesson visible throughout this codebase's 2026 work: *validate your
> assumptions and provide a sensible fallback.* The same philosophy appears in the
> crash and startup-warning fixes (see `EditorStabilityAndWarnings.md`).

## 5. Related changelists

In `Reports/P4-History/`: `*scriptabletools-icon-path-robustness*`.

Jira: **SUNDANCE-46349**.

## See also
- `EditorStabilityAndWarnings.md` — other robustness fixes.
- `Outliner.md` — tools surfaced through this editor mode.
