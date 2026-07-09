# 4. HLOD Layer target assets

The `UHLODLayer` assets (`/Script/Engine.HLODLayer`) that the HLOD **rules** point at
via `TargetHLODLayer`, plus the supporting imposter-config asset. These define **how**
a proxy is built (which HLOD builder), what `LayerType` it is, and how layers chain to
each other via `ParentLayer`.

> Layer *build* settings are largely numeric (cell size, loading range, triangle
> percentages, texture sizes) and are **not** readable from the package text. What is
> reliably extractable — and what this document reports — is each layer's **class,
> `LayerType`, HLOD builder class, `ParentLayer` link, and referenced material /
> imposter config**. Numeric distances are noted as "on the asset / map hash" and are
> not quoted.

## 4.1 HLOD builder classes seen in the project

| Builder class | Produces |
|---------------|----------|
| `HLODBuilderMeshMergeWithAutoInstancing` | Merged static mesh + auto-instancing of repeats. |
| `HLODBuilderMeshApproximateWithAutoInstancing` | Approximated (remeshed) proxy + instancing. |
| `HLODBuilderMeshApproximate` (`MeshApproximate` type) | Approximated proxy (no instancing variant). |
| `HLODBuilderMeshSimplify` | Simplified proxy. |
| `HLODBuilderInstancing` | Instances only, filtered by minimum extent. |
| `HLODBuilderFilteredInstancing` | Instancing filtered (landscape/road/water near layers). |
| `FoliageHLODBuilder` | Foliage-specific proxy driven by an imposter config. |
| `FarFoliageHLODBuilder` / `…MeshMergeFromSource` | Far-foliage HLOD from source imposter meshes. |
| `HLODBuilderDummy` | **No geometry** — a placeholder layer that generates nothing. |

`LayerType` (`EHLODLayerType`) values observed: `Custom` (builder chosen explicitly),
`MeshMerge`, `MeshApproximate`, `MeshSimplify`.

---

## 4.2 Overland layers

| Asset | `LayerType` | Builder | `ParentLayer` | Notes |
|-------|-------------|---------|---------------|-------|
| `LV_Overland_HLODLayer_Near` | `Custom` | `HLODBuilderMeshMergeWithAutoInstancing` | `LV_Overland_HLODLayer_Far` | Main near layer; has a component **MinimumExtent** filter + auto-classification. Target of `DA_Overland_HLODLayer_Near_Rules`. |
| `LV_Overland_HLODLayer_Far` | `Custom` | `HLODBuilderMeshApproximateWithAutoInstancing` | *(root)* | Far layer; component filter removes non-Nanite components. |
| `LV_Overland_HLODLayer_BLK_Far` | `MeshApproximate` | `HLODBuilderMeshApproximate` | `LV_Overland_HLODLayer_Far` | Blockout far proxy. |
| `LV_Overland_HLODLayer_Foliage_Near` | `Custom` | **`HLODBuilderDummy`** | *(none)* | **No proxy** — placeholder near-foliage layer (see §4.6). |
| `LV_Overland_HLODLayer_Foliage_Far` | `Custom` | `FoliageHLODBuilder` | *(none)* | Uses `ImposterConfig → DA_Overland_FoliageImposter_Config`. |
| `LV_Overland_HLODLayer_Landscape_Near` | `MeshMerge` | `HLODBuilderFilteredInstancing` / mesh-merge | `LV_Overland_HLODLayer_Landscape_Far2` | Target of the landscape rule. |
| `LV_Overland_HLODLayer_Landscape_Far2` | `MeshMerge` | `HLODBuilderFilteredInstancing` / mesh-merge | *(root)* | The live landscape-far layer. |
| `LV_Overland_HLODLayer_Landscape_Far` | — | — | — | **`ObjectRedirector` → `LV_Overland_HLODLayer_Landscape_Near`** (deprecated name; not a real layer, see §4.5). |
| `LV_Overland_HLODLayer_Road_Near` | `MeshSimplify` | `HLODBuilderMeshSimplify` (area-weighted normals) | *(root)* | Target of the road rule. |
| `LV_Overland_HLODLayer_Water_Near` | `MeshApproximate` | `HLODBuilderMeshApproximate` (filtered instancing) | *(root)* | Target of the water rule. |

**Overland parent chain (near → far):**

```
Near        → Far        (main geometry)
BLK_Far     → Far        (blockout)
Landscape_Near → Landscape_Far2
Road_Near   (standalone)
Water_Near  (standalone)
Foliage_Near (Dummy)  /  Foliage_Far (imposter)
```

---

## 4.3 Hogsmeade layers

| Asset | `LayerType` | Builder | `ParentLayer` | Notes |
|-------|-------------|---------|---------------|-------|
| `LV_HM_HLODLayer_Near` | *(Custom)* | `HLODBuilderInstancing` (FilterMinimumExtent) | `LV_HM_HLODLayer_Mid` | Target of `DA_HM_HLODLayer_Near_Rules`. |
| `LV_HM_HLODLayer_Mid` | `Custom` | `HLODBuilderMeshMergeWithAutoInstancing` | `LV_HM_HLODLayer_Far` | Mid tier (Hogsmeade has 3 tiers). |
| `LV_HM_HLODLayer_Far` | `Custom` | `HLODBuilderMeshApproximateWithAutoInstancing` | *(root)* | Far tier. |
| `LV_HM_HLODLayer_Foliage_Near` | `Custom` | **`HLODBuilderDummy`** | *(none)* | No proxy (matches the Overland pattern). |
| `LV_HM_HLODLayer_Foliage_Far` | `Custom` | `FoliageHLODBuilder` | *(none)* | `ImposterConfig → DA_Overland_FoliageImposter_Config` (shared with Overland). |

**Hogsmeade chain:** `Near → Mid → Far` (a three-level chain, unlike Overland's
two-level `Near → Far`).

---

## 4.4 Hogwarts layers

| Asset | `LayerType` | Builder | `ParentLayer` | Notes |
|-------|-------------|---------|---------------|-------|
| `LV_HW_HLODLayer_Near` | *(Custom)* | `HLODBuilderInstancing` (FilterMinimumExtent) | `LV_HW_HLODLayer_Mid` | Target of `DA_HW_HLODLayer_Near_Rules`. |
| `LV_HW_HLODLayer_Mid` | `Custom` | `HLODBuilderMeshApproximateWithAutoInstancing` | `LV_HW_HLODLayer_Far` | Mid tier. |
| `LV_HW_HLODLayer_Far` | `Custom` | `HLODBuilderMeshApproximateWithAutoInstancing` | *(root)* | Far tier; extra approximation settings (`bOccludeFromBottom`, `GapDistance`, `WindingThreshold`). |

**Hogwarts chain:** `Near → Mid → Far` (three levels, like Hogsmeade). Hogwarts uses
**mesh-approximation** for Mid/Far, whereas Hogsmeade uses mesh-merge at Mid.

---

## 4.5 The Landscape_Far redirector

`LV_Overland_HLODLayer_Landscape_Far` is **not** a layer — it is an
`ObjectRedirector` whose `DestinationObject` is
`LV_Overland_HLODLayer_Landscape_Near`:

```
/Script/Engine.HLODLayer'/Game/Data/WorldPartition/HLOD/Overland/LV_Overland_HLODLayer_Landscape_Near.LV_Overland_HLODLayer_Landscape_Near'
```

It exists so that any old reference to the historical `Landscape_Far` name resolves to
the current `Landscape_Near` layer. The live landscape-far tier is
`LV_Overland_HLODLayer_Landscape_Far2`. Don't treat `Landscape_Far` as an active
target.

---

## 4.6 The `Dummy` layers and the foliage split

Two categories of "no-op" layer exist:

- **`LV_Overland_HLODLayer_Dummy`** (at the `HLOD/` root) — a `HLODBuilderDummy`
  layer, the auto-injected default the engine falls back on. It generates nothing.
- **`LV_*_HLODLayer_Foliage_Near`** (Overland + Hogsmeade) — also `HLODBuilderDummy`.

This is the key to reading the `Foliage_Near` **rules** (document 3): those rules
match tree foliage and assign **no** explicit layer while keeping `IncludeInHLOD =
true`. Near-range foliage HLOD is therefore effectively a no-op (Dummy), while the
distance representation of foliage is produced by:

- `LV_*_HLODLayer_Foliage_Far` via `FoliageHLODBuilder` + `DA_Overland_FoliageImposter_Config`, and
- the dedicated **FarFoliage** layers (§4.7).

---

## 4.7 FarFoliage layers and imposter config

| Asset | Class | Role |
|-------|-------|------|
| `LV_FarFoliage_HLODLayer_Foliage_Mid` | `UHLODLayer` (`Custom`) | `FarFoliageHLODBuilder`; `ParentLayer → Foliage_Far`; uses `FlattenMaterial_VT`. Referenced by `DefaultPlugins.ini` `AllowedRuntimeGrids(FarFoliageGrid)`. |
| `LV_FarFoliage_HLODLayer_Foliage_Far` | `UHLODLayer` (`Custom`) | `HLODBuilderMeshMergeFromSource`; root of the FarFoliage chain. |
| `DA_FarFoliage_Config` | `UFarFoliageImposterConfig` (**not** a layer) | Maps foliage source meshes (`SK_*_Nanite`) → far-foliage HLOD meshes (`SM_*_FarFoliageHLOD`), with fallback meshes and uniform scale. Drives far-foliage imposter generation. |

`DA_FarFoliage_Config` enumerates the species handled by far-foliage imposters
(Alder, Birch, Oak, ScotsPine, Spruce, Bracken, WhiteDeadNettle, GenericGrass, …).
It is the data backing the `FarFoliageGrid` / FarFoliage HLOD path, distinct from the
per-region `Foliage_Far` layers.

---

## 4.8 Rule → target-layer map (quick reference)

| HLOD rule | Assigns layer | Layer builder |
|-----------|---------------|---------------|
| `DA_Overland_HLODLayer_Near_Rules` | `LV_Overland_HLODLayer_Near` | MeshMerge + instancing |
| `DA_Overland_HLODLayer_Landscape_Near_Rules` | `LV_Overland_HLODLayer_Landscape_Near` | MeshMerge (filtered instancing) |
| `DA_Overland_HLODLayer_Water_Near_Rules` | `LV_Overland_HLODLayer_Water_Near` | MeshApproximate |
| `DA_Overland_HLODLayer_Road_Near_Rules` | `LV_Overland_HLODLayer_Road_Near` | MeshSimplify |
| `DA_Overland_HLODLayer_Foliage_Near_Rules` | *(none — inherits)* | Foliage_Near = Dummy |
| `DA_HW_HLODLayer_Near_Rules` | `LV_HW_HLODLayer_Near` | Instancing |
| `DA_HM_HLODLayer_Near_Rules` | `LV_HM_HLODLayer_Near` | Instancing |
| `DA_HM_HLODLayer_Foliage_Near_Rules` | *(none — inherits)* | Foliage_Near = Dummy |
| `*_NoneInclude_Rules` | *(none — inherits, kept in HLOD)* | — |
| `*_NoneExclude_Rules` | *(none — removed from HLOD)* | — |
