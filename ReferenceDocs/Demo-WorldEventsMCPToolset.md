Parent: [Reference Docs](README.md)

# Demo Script — World Events MCP Toolset (2 minutes)

*A two-minute read-only live demo, built on real data from `LV_Overland` and rehearsed
against the Bell Tower house-elf event. Four prompts, one arc.*

Reference: [World Events MCP Toolsets](CustomTools/WorldEventsMCPToolsets.md) ·
[Development plan](DevelopmentPlan-WorldEventsMCPToolset.md)
## Contents

- [The arc](#the-arc)
- [Setup](#setup)
- [The run](#the-run)
  - [Prompt 1 — where you already are](#prompt-1--where-you-already-are)
  - [Prompt 2 — zoom in, and show the web](#prompt-2--zoom-in-and-show-the-web)
  - [Prompt 3 — the thing that looks wrong](#prompt-3--the-thing-that-looks-wrong)
  - [Prompt 4 — the verdict](#prompt-4--the-verdict)
- [Optional fifth beat, if you have another minute](#optional-fifth-beat-if-you-have-another-minute)
- [If the orphan does not appear](#if-the-orphan-does-not-appear)
- [Adding a visual beat](#adding-a-visual-beat)
- [What to keep out of a live run](#what-to-keep-out-of-a-live-run)

---


---

## The arc

**Suspicion, verification, verdict.** The demo opens on an inventory, finds something that
looks like a content bug, and then proves in one prompt that it is a false positive caused
by streaming. That arc beats any "look how much it can write" demo, for three reasons:

- It is **entirely read-only**. Nothing is checked out, nothing is dirtied, nothing can
  refuse mid-run. No `WorldDataLayers` precondition to prepare.
- It shows the tool's **documented limits being crossed by the agent**, which is more
  convincing than a tool that claims to be always right.
- It ends on a fact nobody in the room can get to any other way in under an hour.

---

## Setup

Far lighter than a write demo, because nothing here writes.

- [ ] `LV_Overland` open, World Partition settled, camera anywhere near the Bell Towers.
- [ ] `LI_BellTowers_INT` loaded, so `WEL_HW_BellTower_CornerDisplay` comes back
      `bIsLoaded: true`. It is the only locator the script needs loaded.
- [ ] **Rehearse prompt 3 the morning of.** The orphan it surfaces depends on what is
      loaded, and the loaded set changes. See *If the orphan does not appear* below.
- [ ] Chat panel and viewport both visible.

---

## The run

### Prompt 1 — where you already are

> At the current location in the editor, using Unreal MCP, describe me the current world
> events in place.

Comes back with the locators around you, `WEL_HW_BellTower_CornerDisplay` among them.

**Say while it runs:** this is reading World Partition actor descriptors, not loading
actors — so it sees locators that are not even in memory. On this level that is 273
locators, of which 219 are loaded.

### Prompt 2 — zoom in, and show the web

> Tell me everything about WEL_HW_BellTower_CornerDisplay, including its data layers.

**What comes back, and what to point at:**

- One possible event: `WEDA_HouseElfActivity_Sweeping`, tag
  `WorldEvent.Definition.HouseElfActivity.Sweeping`. A house elf sweeping the corner of
  the Bell Tower. Good demo material because everyone in the room can picture it.
- It lives **inside a Level Instance** (`LI_BellTowers_INT`), which is why the same
  `DL_WE_*` asset has **two** `UDataLayerInstance`: one in the Level Instance's own
  `WorldDataLayers`, one under `DL_WORLD_EVENTS` in the persistent one.
- 8 actors assigned to that data layer.

**Say:** that's the point about this system — one World Event is not one asset. Here it is
a locator, a level instance actor, a definition asset, a data layer asset, two data layer
instances, and 8 actors. Answering "is this consistent?" by hand means four editors.

### Prompt 3 — the thing that looks wrong

> List the World Event data layers whose name contains CornerDisplay.

Three rows come back. Two are the pair you just discussed. The third is
`DL_WE_HW_DADA4_INT_CornerDisplay_WE_DedicatedKnitting1_Fall`, flagged
**`bIsOrphan: true`, 0 actors, no owning locator**.

**Say:** so that looks like dead weight — a data layer left behind by a World Event
someone deleted by hand. Which is exactly the kind of thing this audit is for. Let's check.

Do not oversell it. The next prompt is the payoff, and it works better if you sounded
mildly suspicious rather than triumphant.

### Prompt 4 — the verdict

> Is that really an orphan? Check whether a locator owns it.

**What comes back:** `WEL_HW_DADA4_INT_CornerDisplay` exists, carries
`WorldEvent.Definition.DedicatedKnitting.Fall`, and sits in `LI_DADA4_INT` — with
`bIsLoaded: false`. It is not an orphan. It is a live World Event whose Level Instance
simply is not streamed in right now.

**Close on this:** the orphan check can only see loaded content, and that limitation is
written into the tool's own documentation. But the locator list is descriptor-first, so it
sees unloaded actors. The agent crossed from one to the other in one step and settled the
question — without loading the Level Instance, without opening a second editor, and
without writing anything.

**Stop there.**

---

## Optional fifth beat, if you have another minute

> Give me the inventory stats for World Events in this level.

273 locators, 297 possible events, 107 definition assets on disk, and a condition
histogram: `SunWorldEventCondition_MissionStatus` 41 times, `WEC_Cooldown_1Day_C` 15,
`WEC_NightTimeOnly_C` 11 — and `WEC_HasBroom_C` exactly once. That last one usually gets a
laugh, and it makes the point that this is a real sweep across real content.

There is also **one empty locator** in that level — a locator with no possible event, which
can therefore never spawn anything. If you want a genuine defect to end on, that is the
honest one, and `numEmptyLocators` finds it in a single call.

**Do not** present `numUnreferencedDefinitions: 67` as a delete list. It counts loaded
locators only, so it has exactly the same false-positive problem you just demonstrated in
prompt 4 — the tool's own description says so. Mentioning that you know that is a better
look than quoting the number.

---

## If the orphan does not appear

The orphan in prompt 3 exists because `LI_DADA4_INT` is unloaded, and that depends on the
editor's streaming state on the day. Rehearse it. If the row does not show up:

- Run `ListWorldEventDataLayers` with no filter and pick any other row with
  `bIsOrphan: true` and 0 actors — on this level there are usually several, and the
  verification prompt works identically on any of them.
- Or invert the arc: ask for the inventory stats first, point at `numEmptyLocators`, and
  ask which locator it is. Same shape — a suspicious number, then a specific answer.

---

## Adding a visual beat

If the audience needs something moving rather than something true, insert between prompts
2 and 3:

> Focus the viewport on that locator and preview its possible event.

`WorldEventViewportToolset.FocusOnWorldEventLocator` then
`SetPreviewedPossibleWorldEvent` — the camera moves and the sweeping elf's data layer
streams in. Two caveats: it changes editor state, so clear the preview afterwards with
`ClearWorldEventPreview`, and it is the one beat in this script that is not read-only in
spirit. Rehearse it or drop it.

---

## What to keep out of a live run

**Authoring and deletion.** Creating a possible event writes to `WorldDataLayers` and can
be legitimately refused if the file is not checked out and up to date; deleting inside a
Level Instance — which is exactly where this Bell Tower event lives — enters an in-context
edit that reloads the level. Both are correct behaviours and neither is worth watching.
`PlanWorldEventDeletion` also pins actors, so an abandoned plan leaves the editor holding
them.

Show the deletion plan on a slide instead, and let the read-only demo above earn the
question "can it also write?" — which is a much better position to answer it from.

---

**In this section:** [Reference Docs index](README.md)

Back to [repository root](../README.md).
