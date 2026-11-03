Parent: [Reference Docs](README.md)

# Parallel processing for `WorldPartitionRuleBuilder`

*Split the nightly [Apply World Partition Rules](TeamCityJobs.md#apply-world-partition-rules)
run across several agents so the 10-hour `LV_Overland` pass finishes in a 2-3 hour window.*

**Status:** the builder code (Phase 1) is implemented in the `WorldBuildingEditor` module.
Defaults reproduce today's behaviour exactly; the TeamCity fan-out (Phase 3) is the remaining work.

## Contents

- [The problem](#the-problem)
- [What is a shard](#what-is-a-shard)
- [Why this is faster](#why-this-is-faster)
- [How an actor is assigned to a shard](#how-an-actor-is-assigned-to-a-shard)
- [Parameters](#parameters)
- [Testing locally](#testing-locally)
- [Deploying on TeamCity](#deploying-on-teamcity)
- [Correctness guarantees](#correctness-guarantees)
- [See also](#see-also)

---

## The problem

Applying World Partition rules to `LV_Overland` takes about **10 hours** on a single agent, inside
the nightly window. It is the long pole: a rule change cannot be verified the same day.

The run walks every actor descriptor, then loads and rewrites only the ones that disagree with the
rules. Measured on the 2026-10-20 `-ReportOnly` run:

| Metric | Value |
|--------|-------|
| Actor descriptors walked | 622 307 |
| Unique actors needing a write | 57 273 |

That is ~0.6 s per written actor, and **the writes are 90% of the wall clock**. Each actor is an
independent Perforce package with no ordering dependency, so the work is embarrassingly parallel.

The build is already split by outliner path (`Missions`, `Dungeons`, `LI_Hogwarts`, ...), but that
axis caps at ~3x: two regions (`Hogwarts Valley` 32%, `Stronghold_Brathborne` 15%) dominate and
cannot be subdivided by path. **The split has to cut *inside* a region** - a spatial grid does that.

## What is a shard

> A **shard** is one slice of the work plus the process that runs it. We launch the **same
> commandlet, on the same level, with the same command line** N times; a single parameter tells each
> copy "you are shard *i* of *N*". Each copy processes only the actors it owns.

A **cell** is a square of the map (a fixed grid); a **shard** is the set of cells one agent handles.
There is **no coordinator and no communication** between shards: each one computes, from each actor's
descriptor, which shard owns it. Because the computation is deterministic and identical everywhere,
the N answers fit together with **no overlap and no gap**.

> Analogy: N people get the same phone book and "handle only the names whose hash equals your
> number". Nobody talks to anybody, yet every name is handled exactly once - as long as everyone has
> the same book (one Perforce revision) and the same rule (a fixed grid, never the per-machine world
> bounds).

## Why this is faster

The writes divide by N; the fixed costs (agent setup, world init, the descriptor walk) do not:

```
wall clock(N)  =  T_fixed  +  T_write / N
```

```mermaid
flowchart LR
  subgraph Today["Today: 1 agent, ~10 h"]
    T0["57k writes"] --> T1["one process does all 57k"]
  end
  subgraph Eight["8 shards: ~2-3 h each, in parallel"]
    W["57k writes"] --> S0["shard 0: ~7k"]
    W --> S1["shard 1: ~7k"]
    W --> Sd["..."]
    W --> S7["shard 7: ~7k"]
  end
```

`T_fixed` is not yet measured, so the gain depends on it. Against today's 10 hours:

| `T_fixed` | 4 shards | 8 shards |
|-----------|----------|----------|
| 30 min | 2 h 55 (3.5x) | 1 h 40 (5.9x) |
| 1 h | 3 h 15 (3.1x) | 2 h 05 (4.7x) |
| 2 h | 4 h 00 (2.5x) | 3 h 00 (3.3x) |

**Target: 8 shards → the 10-hour run in a 2-3 hour window.** 8 is also the practical ceiling: the
nightly window shares a pool of 13 agents, so N = 16 is out without growing it.

## How an actor is assigned to a shard

Decided from the descriptor alone, before anything is loaded - the test runs **first** in
`ShouldProcessActor`, so a foreign actor costs only one cheap bounds check:

```mermaid
flowchart LR
  D["Actor descriptor"] --> Q{"Spatially loaded<br/>with valid bounds?"}
  Q -- yes --> C["cell = floor(center.xy / ShardCellSize)"]
  Q -- "no" --> G["hash(Guid)"]
  C --> H["hash(cell)"]
  H --> M["mod SplitWorld"]
  G --> M
  M --> O["owning shard index"]
```

Two details carry the correctness:

- **Centre, not overlap.** An actor straddling a cell edge belongs to exactly one cell, so two
  agents never fight over the same `.uasset`.
- **Level Instances shard by their inner-level package**, not by cell. Every placement of one asset
  writes the same shared inner packages, so all placements must land on the same shard.

### `SplitWorld` is not a geometric cut

The world's shape (square, rectangle) is irrelevant: we never slice the map into `N` big blocks. The
grid covers it with **hundreds of small fixed cells** (`ShardCellSize` ≈ 1 km), and each cell is then
**dealt to a shard by hash**, like dealing a deck of cards to `N` players:

```mermaid
flowchart LR
  R["World = hundreds of ~1 km cells"] --> D["deal each cell by hash(cell) mod N"]
  D --> P0["shard 0: cells from all over the map"]
  D --> P1["shard 1: cells from all over the map"]
  D --> Pd["..."]
```

So **any positive `N` works** - `5`, `7`, `13`, no need for a power of two or an even divisor. `N`
only has to divide the *cell count*, not the world's geometry, and interleaving by hash is what keeps
each shard balanced even though dense regions (Hogwarts Valley) sit in one corner.

Practical caps (waste, not errors): `N` far above the cell count leaves some shards nearly empty, and
`N` above the agent pool (13) cannot run fully in parallel. `N < 1` is clamped to `1`.

## Parameters

Builder switches (`WorldPartitionRuleBuilder`); defaults = today's behaviour, bit for bit:

| Switch | Default | Meaning |
|--------|---------|---------|
| `-SplitWorld=N` | `1` | Number of shards. `1` = no sharding. |
| `-SplitWorldStartAt=I` | `0` | Which shard this process is, 0-based. |
| `-ShardCellSize=<cm>` | `102400` | Cell edge. Fixed grid anchored at the world origin. |
| `-CellCoord=X,Y` | — | Dev-only: process just one cell ("redo this area"). |

In `-ReportOnly`, the JSON report also carries `ShardCount` / `ShardIndex` / `ShardCellSize` so the
disjointness check (below) can tell the sharded reports apart.

## Testing locally

No agents and no writes needed - `-ReportOnly` only reads descriptors. The key test proves the whole
design in one shot: **the N shards cover every actor exactly once.**

```bat
:: 1) The reference: the usual unsharded run (no -SplitWorld, so it defaults to 1).
::    Only difference from a normal -ReportOnly run is the output filename.
UnrealEditor-Cmd.exe Sundance -run=WorldPartitionBuilderCommandlet -Builder=WorldPartitionRuleBuilder ^
  -DataLayerRules -HLODLayerRules -RuntimeGridRules -ReportOnly ^
  -ReportFile=report-ref.json  <LevelPath>

:: 2) The 4 shards: same run + -SplitWorld=4 and a shard index, all on the same revision.
UnrealEditor-Cmd.exe Sundance -run=WorldPartitionBuilderCommandlet -Builder=WorldPartitionRuleBuilder ^
  -DataLayerRules -HLODLayerRules -RuntimeGridRules -ReportOnly ^
  -SplitWorld=4 -SplitWorldStartAt=0 -ReportFile=report-0.json  <LevelPath>
:: ... repeat for -SplitWorldStartAt=1, 2, 3
```

Then assert, over the `ActorPath` sets in the five reports:

- **union** of shards 0-3 **== reference** (completeness: nobody is missed);
- all pairwise **intersections empty** (disjointness: nobody is processed twice).

Other useful local runs:

```bat
:: one real shard, left pending for review instead of submitted
ApplyWorldPartitionRules.bat -StayPending ... -SplitWorld=4 -SplitWorldStartAt=2

:: redo a single map area after a local fix
UnrealEditor-Cmd.exe ... -Builder=WorldPartitionRuleBuilder -CellCoord=12,7 <LevelPath>
```

## Deploying on TeamCity

TeamCity is on 2024.12.3, so the built-in **Matrix Build** feature applies. Keep the **same build
configuration** and add two parameters, then a matrix dimension over the shard index:

| TeamCity parameter | Default | Maps to |
|--------------------|---------|---------|
| `wp-rules.split_count` | `1` | `-SplitWorld` |
| `wp-rules.split_index` | `0` | `-SplitWorldStartAt` |

1. **Dark launch.** Append `-SplitWorld=%wp-rules.split_count% -SplitWorldStartAt=%wp-rules.split_index%`
   to the Apply step. With the defaults it behaves exactly as today, so it can ship and bake for a week.
2. **Fan out.** Make `wp-rules.split_index` a Matrix dimension `0..7`. TeamCity creates 8 parallel
   builds plus a composite head, each on its own agent and Perforce workspace, each submitting its
   own changelist (the actor sets are disjoint, so the submits never collide).
3. **Pin the revision.** All shards take a snapshot dependency on the same `CompileEditor` build -
   this is the "same phone book" guarantee.
4. **Verify.** A `..._Verify` build depends on all shards and re-runs `-ReportOnly` over the whole
   level; it fails if the finding count rises above tolerance.

```mermaid
graph LR
    C["CompileEditor<br/>(one revision)"] --> S0["shard 0"]
    C --> S1["shard 1"]
    C --> Sd["shard ..."]
    C --> S7["shard 7"]
    S0 --> V["Verify<br/>-ReportOnly, whole level"]
    S1 --> V
    Sd --> V
    S7 --> V
```

## Correctness guarantees

| Risk | Closed by |
|------|-----------|
| Actor claimed by two shards | Centre-based cell ownership - no overlap by construction. |
| Actor claimed by no shard | Assignment is a total function of the descriptor. |
| Shards compute different grids | Fixed origin + fixed cell size; never the per-machine world bounds. |
| Shards on different revisions | TeamCity snapshot dependency pins one revision. |
| Level Instance placements split | Sharded by inner-level container package. |
| Shared `.umap` / `WorldDataLayers` written by many | Only shard 0 writes them; any other shard that needs to fails loudly. |
| One shard fails | Composite fails; existing revert/cleanup steps run `execute_always`. |

Both set-based properties are proven by the [local disjointness test](#testing-locally), cheap enough
to keep as a recurring CI check.

**Open question - nested Level Instances.** A nested Level Instance reachable only through a parent
owned by a different shard could be missed. This is tied to the existing placement-dedup question
(the same asset placed *k* times is processed *k* times today), which needs a World Building ruling
before it is touched. The whole-level `-ReportOnly` Verify step surfaces any resulting miss.

## See also

- [TeamCity jobs](TeamCityJobs.md) - the Apply/Validate configurations, parameters and schedule.
- [`-ReportOnly` vs `-ValidateOnly`](ReportOnlyVsValidateOnly.md) - the read-only modes this plan uses.
- [Builders & commandlets](BuildersAndCommandlets.md#uworldpartitionrulebuilder) - the builder being modified.
- [World Partition builders catalog](WorldPartitionBuildersCatalog.md) - every WP builder, including the Pipeline builder this design borrows `-SplitWorld` from.
