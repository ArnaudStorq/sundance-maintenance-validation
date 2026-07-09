# 5. Processing order & priority

How a single, deterministic outcome is produced for each actor. There is **no
numeric priority field** on any rule asset. Precedence emerges from four layers,
applied in this order of authority:

1. **Ignore lists** (`ActorTypesIgnoredBy…`) — the rule family never runs.
2. **Config array order** (`*RulesForActorSave` / `*ForStreamingGeneration`) — the
   sequence the engine walks, **first match wins**.
3. **`*RulesToExclude` deferrals** inside each rule — let earlier/generic rules yield
   to specific ones regardless of array position.
4. **Global force lists** (`*ForceExcludeFromHLOD`, `*ClearRuntimeGrid`,
   `*ClearDataLayers`) — applied outside the rule assets and override "keep" outcomes.

---

## 5.1 Layer 1 — ignore lists (hard skip)

Before any rule runs, the actor's class is checked against the family's ignore list.
These types are simply never processed by that rule family:

| Family | Ignored types |
|--------|---------------|
| `…IgnoredByDataLayerRules` | `PCGPartitionActor`, `PCGStreamingActor`, `PCGVolume`, `WorldPartitionHLOD`, `WorldDataLayers`, `WorldPartitionMiniMap` |
| `…IgnoredByRuntimeGridRules` | `PCGPartitionActor`, `PCGStreamingActor`, `PCGVolume`, `WorldPartitionHLOD`, `WorldDataLayers`, `WorldPartitionMiniMap` |
| `…IgnoredByHLODLayerRules` | `PCGPartitionActor`, `PCGStreamingActor`, `PCGVolume`, `WorldPartitionHLOD` |

Rationale: procedurally-generated (PCG) actors, generated HLOD actors, and world
infrastructure actors must keep the streaming settings their own systems give them.

---

## 5.2 Layer 2 — config array order (first match wins)

The engine walks the configured array top to bottom and applies the **first** rule
that claims the actor, then stops. The order as configured today:

### HLOD (`HLODLayerRulesForActorSave`)

```
1  Overland  NoneInclude
2  Overland  NoneExclude
3  Overland  Near
4  Overland  Foliage_Near
5  Overland  Landscape_Near
6  Overland  Water_Near
7  Overland  Road_Near
8  Hogwarts  NoneInclude
9  Hogwarts  NoneExclude
10 Hogwarts  Near
11 Hogsmeade NoneInclude
12 Hogsmeade NoneExclude
13 Hogsmeade Near
14 Hogsmeade Foliage_Near
```

### RuntimeGrid on-save (`RuntimeGridRulesForActorSave`)

```
1  DA_HogsmeadeGrid_Rules        → HogsmeadeGrid
2  DA_HogwartsGrid_Rules         → HogwartsGrid
3  DA_HogwartsInteriorGrid_Rules → SmallGrid
4  DA_NoneGrid_Rules             → None (catch-all)
```

### RuntimeGrid streaming-generation (`RuntimeGridRulesForStreamingGeneration`)

```
1  DA_SmallGrid_Rules            → SmallGrid (view-only)
```

> **Important subtlety.** The generic `NoneInclude`/`NoneExclude` HLOD rules are
> listed **first** in each region block, ahead of the specific `Near`/`Water`/…
> rules. If order alone decided, the generic rules would always win. They don't —
> because of layer 3.

---

## 5.3 Layer 3 — `*RulesToExclude` (the real precedence)

Each generic rule lists the specific rules it must yield to in its
`ExclusionCriteria`. Semantics: *"if this actor also satisfies rule X's matching
conditions, then I do not claim it."* This inverts the array order for those actors —
the specific rule effectively takes priority even though it comes later.

**Overland HLOD deferral graph** (`A ──▶ B` = "A defers to B"):

```
NoneInclude ──▶ Near, Foliage_Near, Landscape_Near, Road_Near, Water_Near   (+ defers to grid rule SmallGrid)
NoneExclude ──▶ Near, Foliage_Near, Landscape_Near, Road_Near, Water_Near, NoneInclude
Near        ──▶ Foliage_Near                                                 (+ defers to grid rule SmallGrid)
```

Reading it:

- **`NoneExclude` is the true fallback.** It defers to every specific rule *and* to
  `NoneInclude`. So an actor only reaches "drop from HLOD" if no other Overland rule
  claimed it.
- **`NoneInclude` sits just above the fallback.** It defers to the five specific
  layer rules, so it only claims Level Instances that don't get a real layer.
- **`Near` defers to `Foliage_Near`**, so tree foliage inside a near LI is claimed by
  the foliage rule, not swept into the mesh-merge near layer.

The effective HLOD priority for an Overland actor is therefore:

```
Near / Landscape_Near / Water_Near / Road_Near   (specific, mutually exclusive by actor type)
        └─ Foliage_Near wins over Near for tree foliage
   →  NoneInclude   (Level Instances with no specific layer, kept in HLOD)
   →  NoneExclude   (everything else, dropped from HLOD)
```

**RuntimeGrid deferral graph:**

```
NoneGrid    ──▶ HogsmeadeGrid, HogwartsGrid, HogwartsInteriorGrid   (on-save catch-all yields to sub-world grids)
HogwartsGrid──▶ HogwartsInteriorGrid                                (exterior yields to interior/_INT → SmallGrid)
```

So on save the effective grid priority is:

```
HogsmeadeGrid | HogwartsInteriorGrid(_INT→SmallGrid) | HogwartsGrid(exterior)
   →  NoneGrid (clear to None)      →  [later] SmallGrid at streaming generation
```

Cross-family deferral also exists: `NoneInclude`/`Near` HLOD rules list
`RuntimeGridRulesToExclude = SmallGrid`, i.e. they don't claim actors that the
SmallGrid grid rule owns — keeping the grid and HLOD decisions consistent for the
small-object population.

---

## 5.4 Layer 4 — global force lists (override)

Independent of the rule assets, the config applies hard overrides:

- **`ActorTypesToForceExcludeFromHLOD`** — `StreamingDependencyGroupLocationVolume`,
  `IvyActor`, `WorldPartitionMiniMap`, `WorldDataLayers`, `OdcNavmeshActor`,
  `AvaNoteActor`, `WorldBitmapStreamingProxy`. These are dropped from HLOD
  (`SetHLODLayer(null)` + `bEnableAutoLODGeneration=false`) regardless of any rule.
- **`OutlinerPathsToForceExcludeFromHLOD`** — a long list of small-prop / detail
  substrings (`_INT`, `_POP`, `LI_Overland_Global_Sky`, `AUDIO`, `LerpVolume`,
  `IvyActor`, and many `SM_*` detail meshes: ivy, moss, debris, grass, seaweed,
  bracken, holly, pine needles, corner bricks, step stones, …). Any actor whose
  Outliner path contains one of these is force-excluded from HLOD. This is the
  coarse, config-level counterpart to the per-rule bounds guards — it strips small
  clutter that would otherwise bloat proxies.
- **`ActorTypesToClearRuntimeGrid`** — `WorldBitmapStreamingProxy` has its runtime
  grid cleared (it was explicitly moved out of the ignore list into force-clear +
  force-exclude, CL 1916537).

Because these run outside the rule engine, they win over a rule that would otherwise
keep the actor in HLOD or on a grid.

---

## 5.5 Worked example — a Level Instance in Overland

Actor: an `ALevelInstance` under `LV_Overland/.../Props`, spatially loaded, no
special data layer, not a sub-world, not blockout.

**HLOD (on save):**

1. Ignore list? `LevelInstance` is not ignored → continue.
2. `Overland NoneInclude` (array #1) matches type `LevelInstance`, but its
   `HLODLayerRulesToExclude` includes `Near`. Does the actor satisfy `Near`'s
   conditions? `Near` matches `LevelInstance` not in a sub-world / blockout → **yes**
   → `NoneInclude` **defers**.
3. `Overland NoneExclude` (#2) also defers to `Near` → **defers**.
4. `Overland Near` (#3) matches `LevelInstance`, not excluded (not `_BLK`, not a
   sub-world, and not tree foliage) → **claims**. Applies
   `TargetHLODLayer = LV_Overland_HLODLayer_Near`, `IncludeInHLOD = true`, stop.

**Grid (on save):**

1. `HogsmeadeGrid` (#1) — path not in Hogsmeade → no match.
2. `HogwartsGrid` (#2) — path not in Hogwarts → no match.
3. `HogwartsInteriorGrid` (#3) — no match.
4. `NoneGrid` (#4) — matches any `Actor`, not deferred here → **claims**, sets grid
   `None`.

**Grid (streaming generation):**

- `SmallGrid` — actor is now grid `None`, in Overland, not an excluded type/path/data
  layer → **override to `SmallGrid`**, *provided* `LV_Overland_HLODLayer_Near` is a
  valid HLOD layer on the SmallGrid partition. If it is not, the override is
  **skipped** and the `Skipped RuntimeGrid override` warning is logged — the classic
  Near-layer-vs-SmallGrid conflict.

**Force lists:** if the actor's path contained e.g. `_POP` or a listed detail-mesh
substring, HLOD would be force-excluded at the end regardless of the `Near` result.

---

## 5.6 Worked example — a river in Overland

Actor: `WaterBodyRiver`, spatially loaded, in `LV_Overland/.../Water`.

- **HLOD:** `NoneInclude`/`NoneExclude` both defer to `Water_Near`. `Near` matches
  only `LevelInstance` (not a water body) → no match. `Water_Near` (#6) matches
  `WaterBodyRiver` (its condition is `OR` over the five water classes) → **claims**,
  assigns `LV_Overland_HLODLayer_Water_Near`.
- **Grid:** `NoneGrid` clears to `None` on save; at generation `SmallGrid` may claim
  it unless excluded — water bodies are not in `DA_SmallGrid_Rules`' `TypesToExclude`,
  so they follow the same SmallGrid/HLOD-compatibility check as other actors.

---

## 5.7 Decision checklist (per actor, per family)

```
[Grid family]                         [HLOD family]
  ignored type? ── yes ─▶ skip          ignored type? ── yes ─▶ skip
       │ no                                   │ no
  walk RuntimeGridRulesForActorSave      walk HLODLayerRulesForActorSave
  first rule that matches &              first rule that matches &
  is not excluded/deferred ─▶ apply      is not excluded/deferred ─▶ apply
  (Hogsmeade / Hogwarts / _INT→Small     (specific layer ▶ NoneInclude ▶ NoneExclude)
   / else None)                                │
       │                                  force-exclude list ─▶ override to "no HLOD"
  streaming gen: SmallGrid override
  iff HLOD layer valid on target grid
```

For the concrete field values behind each rule referenced here, see
[document 2](RuntimeGridRules.md), [document 3](HLODLayerRules.md) and
[the inventory](DataAssetInventory.md).
