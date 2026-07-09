# World Partition Rules — Data Asset Analysis

A precise, data-driven analysis of the World Partition **rule system** as it is
actually configured in Sundance (UE 5.7), derived from the Data Assets under
`/Game/Data/WorldPartition/` (Perforce: `//sun/Dev/Sundance/Content/Data/WorldPartition/`,
local: `D:\Sun\Sundance\Content\Data\WorldPartition\`).

> **Source of truth.** This analysis is built primarily from the serialized
> `.uasset` files themselves, cross-checked against the project configuration in
> `D:\Sun\Sundance\Config\DefaultEditor.ini` / `DefaultPlugins.ini` and the engine
> mechanics documented in the [reference topics](README.md). Where a value
> is only knowable from the map's runtime hash or from prior documentation (e.g.
> grid cell sizes, numeric bounds thresholds), it is **explicitly flagged** as such.
> The companion Confluence page *"HLODs & Grids Setup"* was not reachable without
> authentication and was therefore **not** relied upon; the assets are authoritative.

## What this documents

- **How the rule engine works** — the two execution paths (on-save subsystems and
  the streaming-generation mutator), the batch builder, the base rule structures,
  and how a rule mutates actor data.
- **The exact content of every rule asset** — target grid / HLOD layer, matching
  conditions (actor types, tags, outliner paths, bounds), and exclusion criteria.
- **How priority / precedence is resolved** — config array order, first-match-wins,
  the `*RulesToExclude` deferral mechanism, and the global force-exclude / clear /
  ignore lists.
- **The HLOD layer target assets** the rules point at (builder types, layer types,
  parent chains).

## Index

| # | Document | Read it for |
|---|----------|-------------|
| — | [00 — Executive summary](#executive-summary) | The 2-minute mental model (below). |
| 1 | [Rule engine mechanics](RuleEngineMechanics.md) | How rules are declared, evaluated and applied to actors. |
| 2 | [Runtime Grid rules](RuntimeGridRules.md) | The 5 grid rule assets and the on-save vs streaming-generation grid split. |
| 3 | [HLOD Layer rules](HLODLayerRules.md) | The 12 HLOD rule assets, `NoneInclude` vs `NoneExclude`, per-region chains. |
| 4 | [HLOD Layer target assets](HLODLayerTargetAssets.md) | The `UHLODLayer` assets the rules assign (builders, parent chains). |
| 5 | [Processing order & priority](ProcessingOrderAndPriority.md) | The precise precedence model + worked examples. |
| 6 | [Data asset inventory](DataAssetInventory.md) | Appendix: every asset with its extracted fields. |

## Executive summary

Sundance drives per-actor streaming settings **automatically** from a set of
**rule Data Assets**, instead of hand-tagging every actor. Three per-actor
properties are governed ([streaming properties](WorldPartitionStreamingProperties.md)):

- **RuntimeGrid** — which streaming grid the actor belongs to.
- **HLODLayer** (+ `IncludeInHLOD`) — how the actor is represented at distance.
- **DataLayers** — logical grouping (assigned by rules living outside this folder,
  in `/Game/Data/DataLayers/`).

`/Game/Data/WorldPartition/` contains the **RuntimeGrid** and **HLOD** rule assets,
plus the **HLOD layer** assets they target:

```
/Game/Data/WorldPartition/
├── RuntimeGrid/                 # 5 URuntimeGridRuleAsset (grid assignment)
│   ├── DA_HogsmeadeGrid_Rules
│   ├── DA_HogwartsGrid_Rules
│   ├── DA_HogwartsInteriorGrid_Rules
│   ├── DA_NoneGrid_Rules
│   └── DA_SmallGrid_Rules        # streaming-generation only
└── HLOD/                        # 12 UHLODLayerRuleAsset + UHLODLayer targets + configs
    ├── Overland/  (7 rules + 10 layer assets)
    ├── Hogsmeade/ (4 rules + 5 layer assets)
    ├── Hogwarts/  (3 rules + 3 layer assets)
    ├── FarFoliage/ (2 layer assets + 1 imposter config)
    └── LV_Overland_HLODLayer_Dummy
```

Four mechanics matter above all else:

1. **Two execution paths.** Most rules run **on manual actor save** (the rule
   subsystems, listed in `*RulesForActorSave`). The `SmallGrid` grid rule runs
   **only during streaming generation** (`RuntimeGridRulesForStreamingGeneration`)
   as a **view-only** override — it is not baked into the actor. This is why the
   on-save grid rules assign explicit sub-world grids and *clear* Overland actors to
   `None`, while `SmallGrid` is applied later at generation time.
2. **First matching rule wins.** For each actor, the engine walks the configured
   rule array in order and applies the first rule whose *matching conditions* pass
   and whose *exclusion criteria* do not fire, then stops.
3. **Precedence is expressed with `*RulesToExclude`, not a numeric priority.**
   A generic rule (e.g. `NoneExclude`) lists the specific rules (`Near`, `Water_Near`,
   …) in its exclusion criteria, so it *defers* to them even though it appears first
   in the array. There is no priority integer in the assets.
4. **Grid ↔ HLOD-layer compatibility gates everything.** A grid override is refused
   (`Skipped RuntimeGrid override`) when the actor's HLOD layer is not valid on the
   target grid's partition. This single constraint is the root of most of the
   project's HLOD/streaming warnings.

## How to reproduce the extraction

The rule/​layer assets are binary `.uasset` files. The structured facts in these
documents were obtained by reading each package's name, import and export tables
(printable strings) and correlating them with the class layout. A minimal
reproduction (PowerShell) that dumps the readable labels of every asset:

```powershell
Get-ChildItem -Recurse "D:\Sun\Sundance\Content\Data\WorldPartition" -Filter *.uasset |
  ForEach-Object {
    "===== $($_.FullName) ====="
    $b = [IO.File]::ReadAllBytes($_.FullName); $s = ''
    foreach ($c in $b) {
      if ($c -ge 32 -and $c -lt 127) { $s += [char]$c }
      elseif ($s.Length -ge 4) { $s; $s = '' } else { $s = '' }
    }
  }
```

- **Reliable from strings:** asset class, `TargetRuntimeGrid` / `TargetHLODLayer`,
  matched actor types (class imports), outliner path substrings, `*RulesToExclude`
  references, `LogicOperator` (AND/OR), and which top-level booleans are set
  (delta-serialized, e.g. `IncludeInHLOD`).
- **Not visible in strings (flagged where used):** raw numeric values such as
  bounds thresholds and grid `CellSize` / `LoadingRange` (these live on the map's
  runtime hash, not in the rule asset).

## See also

- [Streaming properties](WorldPartitionStreamingProperties.md) — the three streaming properties and the invalid-HLOD-layer gate.
- [World Partition rules](WorldPartitionRules.md) — the practitioner how-to plus the rule subsystem internals and the SmallGrid toggle.
- [Fixing MapCheck issues](FixingMapCheckIssues.md) — cause → fix playbook that these rules feed into.
