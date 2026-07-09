# Editor Stability & Startup Warnings

*A plain-language guide to the crash fixes, startup-warning cleanups, and robustness
improvements made in 2026.*

---

## 1. Why this topic exists

Beyond the big feature efforts (Outliner, World Partition, Actor Folders), a steady
stream of smaller fixes kept the **editor healthy**: it shouldn't crash, and it
shouldn't spam warnings at startup. This file groups those fixes because they share a
philosophy: **validate assumptions, handle edge cases, keep the log clean.**

Two categories:
- **Crashes / correctness** — the editor breaks; must be fixed.
- **Startup warnings** — noise in the log that hides real problems.

## 2. Crash & correctness fixes

### Crash on "Update Redirector References"
**What:** the editor crashed when running *Update Redirector References* if actors got
loaded **outside the main Editor world**.

**Why it happened:** the underlying `FAssetFixUpRedirectors` uses `LoadPackage`
internally. When no world is specified, Unreal spins up a *separate* world of type
`EWorldType::Inactive` during `UWorld::PostLoad`. The code didn't account for that
inactive world and crashed.

**Fix:** handle the inactive-world case so the operation completes safely.

> Lesson: "there's always exactly one world" is a tempting assumption — and a wrong
> one. (Fixed in the `AutoDbAuthoring` plugin.)

## 3. Startup-warning cleanups

Every warning printed at editor launch trains people to ignore the log. These fixes
removed recurring noise.

### Deprecated viewport toolbar extensions
**What:** the log warned that `LevelViewportToolBar.LeftExtension` /
`MiddleExtension` / `RightExtension` were deprecated:
```
Extension panel id "LevelViewportToolBar.LeftExtension" has been deprecated.
Please extend the "LevelEditor.ViewportToolbar" Tool Menus menu instead.
```
**Fix:** migrated the toolbar extensions across several plugins (DayNight,
EditorImprovements, PlatformAssetOverrides, Seasons, Weather, and WorldBuilding) to
the new **Tool Menus** API. Removes the warnings *and* future-proofs the toolbars.

### Python name-collision (World Events)
Covered in detail in `WorldEvents.md`: two `WorldEventActorComponent` members
generated the same Python name; the exposed name was disambiguated with `ScriptName`
meta-data.

## 4. Non-partitioned parent hints in the Outliner (usability)

Not a crash or warning, but a clarity fix worth noting here. Actors inside a
**non-partitioned Level Instance** inherit their World Partition settings from the
parent, so the per-actor Outliner columns looked empty/misleading. A message
**"Non Partitioned Parent"** now appears in the `DL Rules`, `HLOD Layer`,
`DataLayerRule` and `RuntimeGrid` columns for such actors.

This shipped in an instructive sequence:
1. First attempt introduced a shared `WorldPartitionOutlinerColumnUtils` helper —
   but it **broke the build**.
2. A `@BUILDFIX` immediately reverted it to unblock everyone.
3. It was re-landed cleanly a day later.

> Lesson visible in the history: when a change breaks the build, the priority is to
> **revert fast** (unblock the team), then re-land properly — not to hot-patch under
> pressure.

## 5. The common thread

| Fix | Assumption that was wrong / noise removed |
|-----|-------------------------------------------|
| Redirector crash | "there is always one main world" |
| Scriptable Tools icon (see its file) | "the icon is always in the plugin" |
| Toolbar warnings | old extension API still fine |
| Python name clash | two members can't collide in Python |

## 6. Related changelists

In `Reports/P4-History/`: `*fix-crash-update-redirector-references*`,
`*fix-levelviewporttoolbar-warnings*`,
`*fix-python-name-clash-warning*`, `*outliner-nonpartitioned-parent-message*`,
`*buildfix-undo-outliner-columns*`.

Jira: **SUNDANCE-58039**, **SUNDANCE-54425**,
**SUNDANCE-56129**, **SUNDANCE-48603**.

## See also
- `ScriptableTools.md`, `WorldEvents.md` — related robustness/warning fixes.
