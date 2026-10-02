Parent: [Reference Docs](README.md)

# Launching the game standalone

How to run a cooked PC build of Sundance outside the editor — from picking the build in
UnrealGameSync to reaching `LV_Overland` and turning on the in-game debug UI (ImGui debug
menu, World Partition runtime grid display). This is the path to use when a streaming or
runtime-grid question cannot be answered in the editor, because only the cooked build
exercises the real runtime hash.

## Contents

- [Getting a packaged PC build from UnrealGameSync](#getting-a-packaged-pc-build-from-unrealgamesync)
- [Launching the executable](#launching-the-executable)
  - [Intro-related switches](#intro-related-switches)
- [Reaching the world from the frontend](#reaching-the-world-from-the-frontend)
  - [What the developer menu offers](#what-the-developer-menu-offers)
- [The ImGui debug menu](#the-imgui-debug-menu)
  - [Debug panels](#debug-panels)
  - [Driving the debug UI from another machine (NetImgui)](#driving-the-debug-ui-from-another-machine-netimgui)
- [World Partition runtime debug display](#world-partition-runtime-debug-display)
- [Streaming overrides and dumps](#streaming-overrides-and-dumps)
- [What is not available](#what-is-not-available)
- [See also](#see-also)

---

## Getting a packaged PC build from UnrealGameSync

UnrealGameSync shows one badge column per build job. The **Package** column holds the
staged builds; a green badge means that changelist has a usable PC package. Click the
**Package** badge of the changelist you want — that is the build you are going to run,
independently of whatever your workspace is synced to.

Pick a changelist whose Package badge is green rather than the latest one: an unbuilt
changelist has no package to launch.

## Launching the executable

Run the game executable from the staged build:

```
HogwartsLegacy2.exe -skipintro
```

No project file or map argument is needed — the cooked build boots into the frontend
(`SunFrontend`), and the world is chosen from there (see below).

### Intro-related switches

The intro sequence is gated by `USundanceGlobalConfig::HasCompletedIntro()`, which reads
the command line before the saved flag:

| Switch | Effect |
|--------|--------|
| `-skipintro`, `-nointro` | Always skip the intro |
| `-intro`, `-showintro` | Always play the intro, even once it has been completed |
| *(none)* | Fall back to the saved `bCompletedIntro` flag |

```40:60:D:\Sun\Sundance\Source\Sundance\Config\SundanceGlobalConfig.cpp
bool USundanceGlobalConfig::HasCompletedIntro()
{
#if !UE_BUILD_SHIPPING
	if (GSunSkipIntro > INDEX_NONE)
	{
		return GSunSkipIntro >= 1;
	}

	static const bool bAlwaysSkip =
		FParse::Param(FCommandLine::Get(), TEXT("NoIntro")) ||
		FParse::Param(FCommandLine::Get(), TEXT("SkipIntro"));
```

The same thing is reachable at runtime through two console variables, both of which
persist to the config file:

- `Sun.SkipIntro` — `0` never skip, `1` always skip, `-1` use the default behaviour
- `Sun.HasCompletedIntro` — the saved "intro already seen" flag itself

## Reaching the world from the frontend

In the frontend main menu, the row of submenu icons contains a **DEV** icon with a **CD
(disc) icon immediately to its right**. Use the **CD icon on the right**, not the DEV icon.

The main menu wires those icons to separate widgets (`UI_W_MainMenu`): `btn_DevMenu` opens
the developer menu (`UI_W_DevMenu`), and its neighbours open the save/load and additional
content screens (`UI_W_LoadSaveMenu`, `UI_W_AdditionalContent`).

### What the developer menu offers

The developer menu is backed by `UUIDeveloperMenu`
(`D:\Sun\Sundance\Source\Sundance\UI\Frontend\UIDeveloperMenu.cpp`) and has three tabs:

| Tab | What it lists | Where the list comes from |
|-----|---------------|---------------------------|
| **DEV Levels** | the cooked levels | `[DeveloperUI] Levels` in the editor ini, plus `MapsToCook` from `[/Script/UnrealEd.ProjectPackagingSettings]`, minus `SunFrontend` |
| **DEV Overland Start Points** | named spawn points | rows of the `SunLocations` database whose `LocationID` starts with `POI_` or `DEVMENU_` |
| **DEV Mission Data** | missions, with their shortcuts and stat choices | the mission definitions, filtered by `EForceDevMenu` |

Useful facts about that path:

- Launching with no location falls back to `LV_Overland`.
- A start point is passed to the level as `<WorldId>#name=<LocationId>`, so the player
  spawns at the database location rather than at the level's default player start.
- If no profile exists yet, the menu creates one using the profile id in
  `Sun.Dev.ProfileId` (default `42`) with the name, house, pronoun and voice fields of the
  Avatar tab.

## The ImGui debug menu

Debug UI in the game is Dear ImGui, through the `WImguiPlugin` engine plugin. Two ways to
bring up the menu bar:

- console command `ImGui.ToggleMenu`;
- on a controller, the **Start / Menu** button (`Gamepad_Special_Right`), as long as
  `ImGui.UseController` is `1`.

Related CVars:

| CVar | Default | Effect |
|------|---------|--------|
| `ImGui.UseController` | `1` | Let the controller drive ImGui instead of the game |
| `ImGui.UseTrackpad` | `1` | Let trackpad movement drive the ImGui cursor |
| `ImGui.VirtualCursor` | `-1` | `-1` auto (off when a hardware mouse is attached), `0` off, `1` on |

Each system registers its own entries into that menu bar — the `WImgui*` plugins under
`D:\Sun\Sundance\Plugins\` — including the ones relevant to streaming work:

- `WImguiStreamingProfiler` — the streaming profiler
- `WImguiOverlandMap` — a floating window plotting the `LV_Overland` database locations
  over the overland map image
- `WImguiSunWorldEventsDebugger`, `WImguiSunSanctuaryDebugger`, `WImguiFriendlyStats`,
  `WImguiVRAMIndicatorPlugin`, …

### Debug panels

The `DebugPanel` plugin adds dockable ImGui panels, driven by console commands:

| Command | Effect |
|---------|--------|
| `debugPanel.List` | list the available panels |
| `debugPanel.Open <name>` | open one panel |
| `debugPanel.OpenExclusive <name>` | open one panel and close the others |
| `debugPanel.Close <name>` / `debugPanel.CloseAll` | close one / all panels |
| `debugPanel.SaveLayout` / `debugPanel.RestoreLayout` / `debugPanel.Layouts` | manage window layouts |

### Driving the debug UI from another machine (NetImgui)

NetImgui is on by default and the game listens for `NetImguiServer.exe` at boot, so the
debug UI can be driven from a second machine — handy when the game is running fullscreen
or on a devkit. Default listen ports: **8889** game, **8890** editor, **8891** dedicated
server; the server tool itself defaults to **8888**.

Console commands: `ImGui.NetImgui.Connect [host[:port]]`, `ImGui.NetImgui.Listen [port]`,
`ImGui.NetImgui.Disconnect`, `ImGui.NetImgui.Status`. Full setup, including building the
server tool, is documented in `D:\Sun\Engine\Plugins\WImgui\README.md`.

## World Partition runtime debug display

These are the stock engine toggles, and they are the reason to run standalone in the first
place: they show the **runtime** hash — the cells the cooked grids actually produced —
rather than the editor preview.

| Command | What it shows |
|---------|---------------|
| `wp.Runtime.ToggleDrawRuntimeHash2D` | the 2D runtime grid overlay (cells, loading state) |
| `wp.Runtime.ToggleDrawRuntimeHash3D` | the same hash drawn in the world |
| `wp.Runtime.ToggleDrawRuntimeCellsDetails` | per-cell detail of the streaming cells |
| `wp.Runtime.ToggleDrawStreamingSources` | the active streaming sources |
| `wp.Runtime.ToggleDrawStreamingPerfs` | streaming performance counters |
| `wp.Runtime.ToggleDrawDataLayers` | the currently active data layers |
| `wp.Runtime.ToggleDrawDataLayersLoadTime` | data layer load times |
| `wp.Runtime.ToggleDrawLegends` | the legend for the overlays above |

Two helpers when the overlay is unreadable:

- `wp.Runtime.DrawRuntimeHash2DScaleFactor <0.1..1>` — shrink the 2D overlay
- `wp.Runtime.DrawWorldPartitionIndex <n>` — restrict the debug draw to one partitioned
  world (`< 0` draws them all)

## Streaming overrides and dumps

| Command | Effect |
|---------|--------|
| `wp.Runtime.OverrideRuntimeLoadingRange -grid=<Name> -range=<Range>` | override a grid's loading range live (also forwarded to the server) |
| `AvaOverrideMinLoadingRange -grid=<Name> -range=<Range>` | AVA addition: minimum loading range used when the player is in an interior |
| `AvaOverrideLoadingRangeScale <0..1>` | AVA addition: scale all cell loading ranges |
| `wp.Runtime.DumpStreamingSources` | dump the active streaming sources to the log |
| `wp.Runtime.DumpWorldPartitions` | dump the active partitioned worlds to the log |

## What is not available

- The ImGui plugin blacklists the **Shipping** configuration, and the intro CVars are
  compiled out there too (`#if !UE_BUILD_SHIPPING`). Use a Development or Test package.
- The developer menu only lists **cooked** levels, so a level missing from `MapsToCook`
  cannot be reached this way.

## See also

- [World Partition streaming properties](WorldPartitionStreamingProperties.md) — what the
  runtime grid overlay is actually showing
- [World Partition rules](WorldPartitionRules.md) — how actors got their grid in the first
  place
- [Environment & infrastructure](EnvironmentAndInfra.md)
