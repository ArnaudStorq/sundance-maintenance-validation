Parent: [Reference Docs](README.md)

# TeamCity jobs

The two automated jobs that maintain `LV_Overland` streaming data on the build farm:
the **World Partition rule pass** and the **distributed HLOD generation**. Both are
`WorldPartitionBuilderCommandlet` runs wrapped in a TeamCity build configuration, both
commit their results to Perforce, and both feed the daily HTML report hub.

| Job | Build configuration | Builder it runs |
|-----|---------------------|-----------------|
| **Apply World Partition Rules** | [`Sundance_Dev_Tools_ApplyWorldPartitionRules`](https://slc-teamcity.wbiegames.com/buildConfiguration/Sundance_Dev_Tools_ApplyWorldPartitionRules#all-projects) | `UWorldPartitionRuleBuilder` (project builder, `WorldBuildingEditor`) |
| **Generate HLODs (distributed)** | [`Sundance_Dev_Tools_HLODs_Distributed_GenerateHLODs`](https://slc-teamcity.wbiegames.com/buildConfiguration/Sundance_Dev_Tools_HLODs_Distributed_GenerateHLODs#all-projects) | `UWorldPartitionHLODsBuilder` (engine builder, distributed mode) |

Server: `https://slc-teamcity.wbiegames.com`. Read access is enough to inspect builds,
logs and parameters; **starting** a build or **editing** its parameters requires project
permissions that the World Building team asks Philippe St-Jean for.

> ⚠ Note: the build configurations themselves live on the TeamCity server, not in
> Perforce or in this repository. The **parameters** documented below are the builder
> switches the jobs pass through (those are in code, and are exact); the **trigger
> times** are what the team observes in practice. Confirm a value in
> *Build Configuration → Parameters / Triggers* before relying on it.

---

## Apply World Partition Rules

[`Sundance_Dev_Tools_ApplyWorldPartitionRules`](https://slc-teamcity.wbiegames.com/buildConfiguration/Sundance_Dev_Tools_ApplyWorldPartitionRules#all-projects)

### What it does

Runs the project's `WorldPartitionRuleBuilder` headlessly over a target world and its
Level Instances, and re-applies the three rule families — **Data Layer**, **HLOD Layer**,
**RuntimeGrid** — to every actor in scope. It is the batch equivalent of the on-save rule
re-application, so a level that nobody opens still converges to the rules
([rule engine mechanics](WorldPartitionRulesAnalysis/RuleEngineMechanics.md)).

Per actor, the pass:

1. Reads the **actor descriptor** (no load) and evaluates the rules against it.
2. **Loads** the actor only if something actually has to change; compliant actors are
   never loaded. This is what keeps a 650 000-actor world tractable.
3. Checks out the package, applies the rules, and saves. A package that cannot be checked
   out is skipped with `Skipping rule application for actor [...]: package cannot be
   checked out (...)`, which also makes **two jobs running in parallel safe** — the second
   one skips what the first already has open.
4. Logs non-compliant Data Layers, so the information the
   [disabled MapCheck CVars](MapCheckValidationCVars.md) no longer report at level load
   still lands in the nightly report.

The build ends with a described changelist submitted to Perforce. That is also why this
job is the prime suspect whenever art content changes with no human author — see
[transform drift](TransformDrift.md).

### Parameters

The TeamCity parameters map one-to-one onto the builder switches
(`WorldPartitionRuleBuilder.cpp:74–116`):

| Parameter / switch | Effect |
|--------------------|--------|
| `-DataLayerRules` | Apply the Data Layer rules. **Opt-in**: omit it and the family is skipped. |
| `-HLODLayerRules` | Apply the HLOD Layer rules. |
| `-RuntimeGridRules` | Apply the RuntimeGrid rules. |
| `-ContainOutlinerPathSubstrings=a,b` | Scope **in**: process only actors whose Outliner path contains one of the substrings. **OR semantics** (any match is enough). |
| `-DiscardOutlinerPathSubstrings=x,y` | Scope **out**: skip actors whose Outliner path contains one of the substrings. |
| `-ActorClassNames=A,B` | Scope by **native class name**, OR semantics, substring match — so a base class also catches its subclasses (`PlacedFoliage` matches `PlacedFoliage_*`). Added 2026-09-15 to make the Far Foliage passes affordable. |
| `-ReportOnly` | Dry run: answers from descriptors, loads/checks out/saves **nothing**, and writes a JSON report of what the rules *would* change. |
| `-ReportFile=<path>` | Override the report path (default `Saved/Logs/WorldPartition/WorldPartitionRulesReport-<Level>.json`). |
| `-InvokeAvaSavePackageDelegates` | Run the AVA save delegates (AutoDb authoring bridge) during the save. |
| `-BuildMachine -Unattended` | Non-interactive mode. Always set on the farm. |

The target world (`LV_Overland`, `LI_Hogwarts`, `LI_Hogsmeade`, …) is the commandlet's
positional argument, exposed as its own TeamCity parameter.

Scoping is how the nightly load is split: one build per content area, with the Outliner
substrings doing the partitioning. Because the builder still has to **open every Level
Instance** to inspect its actors, class and path filters cut the *processing* time, not
the opening time.

> The builder has **no `-DryRun`** switch — the dry-run mechanism is `-ReportOnly`.

### The command line behind the job

The same invocation is shipped as a local script,
`D:\Sun\Sundance\Tools\Scripts\WorldGeneration\ApplyWorldPartitionRules.bat` — the
reference for what the job actually passes:

```bat
UnrealEditor-Cmd.exe Sundance ^
 -stdout -FullStdOutLogOutput -SCCProvider=Perforce ^
 -run=WorldPartitionBuilderCommandlet ^
 -Builder=WorldPartitionRuleBuilder ^
 -DataLayerRules -HLODLayerRules -RuntimeGridRules ^
 -AutoSubmit -AllowFailedSave ^
 -AutoSubmitTags="@AUTOMATION $OVERLAND" ^
 -AllowCommandletRendering -Verbose ^
 <LevelPath>
```

| Script flag | Adds | Meaning |
|-------------|------|---------|
| `-Submit` | `-AutoSubmit -AllowFailedSave -AutoSubmitTags="@AUTOMATION $OVERLAND"` | Submit the changelist automatically, tagged `@AUTOMATION $OVERLAND` — this is the tag to search for in Perforce when hunting down an automated content change. |
| `-StayPending` | the same, plus `-StayPending` | Create the changelist but **leave it pending** for review. The safe mode when validating a rule change. |
| `-Test` | — | Print the command line without running it. |

Run it locally with `-StayPending` to reproduce a nightly build on one level before
asking for a farm run.

### When it runs

- **Nightly**, triggered in the evening; long passes now finish the following morning
  (run time grew with the actor count, from ~500 000 to ~650 000 actors).
- The schedule is **split by day of week** so each night covers a different slice of the
  content — e.g. Tuesday/Thursday for Mission & Dungeon content — and the **weekend runs
  everything with no filter**.
- Extra builds are started **manually** whenever a rule changes and the affected content
  must be re-processed before the next night (the usual pattern after editing a rule data
  asset: change the rule, launch the pass, review the changelist).
- The job has been **paused** on occasion (September 2026, during the Forageables
  `AttachParent` investigation); a paused configuration produces no build at all, so an
  empty night is not necessarily a failure.

### Outputs

- Log artifacts under `Sundance/Saved/Logs` in the build's artifacts — the folder the
  [WPRulesReviewer](../Tools/WPRulesReviewer/) tool downloads and parses
  (`AppSettings.TeamCityArtifactLogPath`).
- A submitted Perforce changelist per build.
- The warning/finding counts that feed `WorldPartitionRulesSnapshot.html` and the other
  pages of the report hub, refreshed once per day.

---

## Generate HLODs (distributed)

[`Sundance_Dev_Tools_HLODs_Distributed_GenerateHLODs`](https://slc-teamcity.wbiegames.com/buildConfiguration/Sundance_Dev_Tools_HLODs_Distributed_GenerateHLODs#all-projects)

### What it does

Runs the engine's `WorldPartitionHLODsBuilder` in **distributed mode** to regenerate the
`AWorldPartitionHLOD` actors — the merged proxy meshes that stand in for distant content.
Distributed mode is three steps (`WorldPartitionHLODsBuilder.cpp:1905–1917`), which is
what the `_Distributed_` in the configuration id refers to:

| Step | Jobs | Switches | What happens |
|------|------|----------|--------------|
| **Setup** | 1 | `-SetupHLODs -DistributedBuild -BuilderCount=N` | Creates/deletes the HLOD actors the world needs, computes the per-builder workload, writes `HLODBuildManifest.ini` and stages the files under `Intermediate/HLODTemp/HLODBuilder[0..N-1]/`. Deleted HLOD actors go straight to `ToSubmit/`. |
| **Build** | N (parallel) | `-BuildHLODs -DistributedBuild -BuilderIdx=i` | Builder *i* reads its section of the manifest, builds only those HLOD actors (mesh merge / simplify / approximate, per HLOD layer) and drops the results into `ToSubmit/`. A builder index with no section simply skips the world. |
| **Finalize** | 1 | `-FinalizeHLODs -DistributedBuild` | Gathers everything under `ToSubmit/` and **submits it to Perforce**. |

The manifest carries the engine version and the builder count; a build step whose engine
version does not match the manifest fails on purpose, so a mid-run engine upgrade cannot
produce mixed HLOD data.

### Parameters

| Parameter / switch | Effect |
|--------------------|--------|
| `-SetupHLODs` / `-BuildHLODs` / `-RebuildHLODs` / `-FinalizeHLODs` | The step to run. `-RebuildHLODs` = build with `bForceBuild`, ignoring the up-to-date check. |
| `-DeleteHLODs` / `-DumpStats` | Maintenance steps: delete every HLOD actor, or print HLOD actor statistics. |
| `-DistributedBuild` | Use the shared `Intermediate/HLODTemp` working directory and the generated manifest (it overrides any `-BuildManifest=`). |
| `-BuilderCount=N` | Setup only: how many parallel build jobs to generate work for. Must be > 0. |
| `-BuilderIdx=i` | Build only: which manifest section this agent owns. |
| `-BuildManifest=<file>` | Manifest path for a non-distributed manifest build. |
| `-BuildHLODLayer=<name>` | Restrict the build to one HLOD layer (e.g. a `Foliage_Near` pass). |
| `-BuildSingleHLOD=<name>` | Build exactly one HLOD actor — the debugging entry point. |
| `-ResumeBuild=<index>` | Resume a build that died part-way. |
| `-ReportOnly` | Report what would be built; build nothing. |
| `-ReuseParentBranchHLODs` | Reuse HLODs already built in the parent stream instead of rebuilding them. |
| `-AllowCommandletRendering` | Required for the build step: `RequiresCommandletRendering() == true`. |
| `-AllowFailedSave`, `-AllowFailedWorkloadValidation`, `-ModifyFilesWithoutCheckout`, `-ForceDistributeHLODs` | AVA additions: tolerate save/validation failures on the farm, write without checkout, and push every HLOD actor through `HLODTemp` even when unmodified. |

### The command line behind the job

The non-distributed equivalent is
`D:\Sun\Sundance\Tools\Scripts\WorldGeneration\WorldPartitionBuildHLODs.bat` (single
machine: Setup and Build in one process, Finalize folded into `-Submit`):

```bat
UnrealEditor-Cmd.exe Sundance ^
 -stdout -FullStdOutLogOutput -SCCProvider=Perforce ^
 -run=WorldPartitionBuilderCommandlet ^
 -Builder=WorldPartitionHLODsBuilder ^
 -SetupHLODs -BuildHLODs ^
 -AutoSubmit -FinalizeHLODs -AllowFailedSave ^
 -AutoSubmitTags="@AUTOMATION $OVERLAND" ^
 -AllowCommandletRendering -Verbose ^
 [-BuildHLODLayer=<Layer>] <LevelPath>
```

Sibling scripts in the same folder: `WorldPartitionRebuildHLODs.bat` (`-RebuildHLODs`,
force) and `WorldPartitionDeleteHLODs.bat`. Same `-Submit` / `-StayPending` / `-Test`
flags and the same `@AUTOMATION $OVERLAND` submit tag as the rule script.

### When it runs

- **Nightly**, in the same evening window as the rule pass, and manually on demand after
  a large content or HLOD-layer change.
- Because the heavy step is fanned out over N agents, the wall-clock time depends on how
  many build agents the farm gives the job that night — the same agent contention that
  makes the rule pass spill into the morning.

### Outputs

- A Perforce submit from the Finalize step containing the rebuilt HLOD actor packages.
- `HLODTrend.html` and the HLOD panels of the report hub, refreshed once per day.
- Build logs per agent, useful when a single HLOD actor fails to build: the failing
  builder index points at its manifest section.

---

## Reading the results

- **WPRulesReviewer** ([`Tools/WPRulesReviewer/`](../Tools/WPRulesReviewer/)) talks to the
  REST API (`app/rest/builds?locator=buildType:<id>`), lists recent builds of a build
  configuration, downloads the `.log` artifacts and triages the warnings. It defaults to
  `Sundance_Dev_Tools_ApplyWorldPartitionRules`; point `TeamCityBuildTypeId` at the HLOD
  configuration to review that job instead.
- **Authentication** is a personal access token: *avatar → Profile → Access Tokens →
  Create access token*, then paste it in *Settings → TeamCity → Access token (Bearer)*.
  The API rejects anonymous requests (`401 Authentication required`).
- The **report hub** (`WorldStreamingHub.html`, `HLODTrend.html`,
  `WorldPartitionRulesSnapshot.html`, `StreamingGenerationSnapshot.html`) is the
  human-facing view of both jobs and updates once per day.

### The reporting pipeline

Two Python scripts in `D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\Report\`
turn a build's output into the hub's data. Both take a `--build-id` precisely so a
TeamCity build number or changelist can be stamped on the data point:

| Script | Input → output | Feeds |
|--------|----------------|-------|
| `CurateWorldPartitionRulesData.py` | `Sundance.log` → `WorldPartitionRules-CL*.json` (pre-parsed findings) + appends to `WorldPartitionRulesTrendData.json` | `WorldPartitionRulesSnapshot.html`, `WorldPartitionRulesTrend.html` |
| `GenerateHLODTrendData.py` | `HLODTrendData/HLODStats-CL*.csv` → `HLODTrendData.json` | `HLODTrend.html`, `HLODSnapshot.html` |

The curator parses the exact log lines the rule builder emits — `Applied HLODLayer '...'
to actor '...'`, `Applied DataLayer`, `Applied RuntimeGrid`, `Missing DataLayer`,
`matches multiple HLODLayer rules (N)`, and the `Skipping rule application for actor
[...]: package cannot be checked out (Checked out by: <user> @ <workspace>)` line. That
last one is why the reports can attribute a skipped actor to the person holding the file.

> This is also the contract to respect when adding a new warning: if the message does not
> match one of these patterns, it shows up in the log but **not** in the dashboard.

## Operating notes

- **Rules are re-processed nightly**, so a bad rule value costs at most one day — but it
  also means a bad rule value *will* be written to content within a day.
- **Never treat a rule as a warning silencer.** The job submits real content changes; a
  rule added to hide a warning ships that change to everyone.
- Keep the Confluence rules page updated with every rule change, since the job applies
  whatever Perforce says — **Perforce data is the source of truth**.

## See also

- [Builders & commandlets](BuildersAndCommandlets.md) — the builders these jobs run, with
  line-level code
- [World Partition builders catalog](WorldPartitionBuildersCatalog.md) — every builder and
  its switches
- [World Partition rules](WorldPartitionRules.md) — the rules the nightly pass applies
- [Transform drift](TransformDrift.md) — what a bad automated run can do to content
- [MapCheck validation CVars](MapCheckValidationCVars.md) — the checks that now rely on
  the nightly report instead of the per-load MapCheck
- [Perforce source control](PerforceSourceControl.md) — the checkout rules the jobs obey
