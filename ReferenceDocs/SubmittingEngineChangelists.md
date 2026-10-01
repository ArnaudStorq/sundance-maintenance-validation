Parent: [Reference Docs](README.md)

# Submitting an engine changelist (Dev-Engine)

How to submit engine code (`Engine/...`) through the `//sun/Dev-Engine` stream from
`MTLWKS20850`: which local workspace to use, how to move a changelist prepared in
`//sun/Dev`, how to fill Submit Sidekick, and how the change then reaches `//sun/Dev`.
Every value below was checked against Perforce on 2026-09-30.

- **Workspace**: `MTLWKS20850_SunDevEngine`, root `D:\SunDevEng`.
- **Submit tool**: P4V → **AVA: Submit Sidekick (Changelist)...**, run from that workspace.
- **Way back to Dev**: Robomerge, about a day later, under the author's name.

## Contents

- [Which stream](#which-stream)
- [Which local workspace](#which-local-workspace)
- [Step 1 — Sync the Dev-Engine workspace](#step-1--sync-the-dev-engine-workspace)
- [Step 2 — Put the change in a Dev-Engine changelist](#step-2--put-the-change-in-a-dev-engine-changelist)
  - [Option A — Write the change in the Dev-Engine workspace](#option-a--write-the-change-in-the-dev-engine-workspace)
  - [Option B — Move a changelist prepared in Dev](#option-b--move-a-changelist-prepared-in-dev)
- [Step 3 — Submit with Submit Sidekick](#step-3--submit-with-submit-sidekick)
  - [Description format](#description-format)
  - [What Submit Sidekick checks](#what-submit-sidekick-checks)
- [Step 4 — Follow the robomerge to Dev](#step-4--follow-the-robomerge-to-dev)
- [Worked example: CL 2102948](#worked-example-cl-2102948)
- [See also](#see-also)

## Which stream

`//sun/Dev-Engine` is a development stream, child of `//sun/Main` like `//sun/Dev`.
Robomerge keeps the two in step, in both directions:

| Bot | What it does |
|-----|--------------|
| `SUN (Dev-Engine -> Dev)` | brings Dev-Engine changes into `//sun/Dev` |
| `SUN (Dev -> Dev-Engine)` | brings Dev changes into `//sun/Dev-Engine` |

Dev-Engine is the usual route for engine code, not the only one. Of the last 200
changelists that touch `//sun/Dev/Engine/Source/...` (2026-08-07 to 2026-09-30), 169 came
from Dev-Engine through Robomerge and 31 were submitted directly in `//sun/Dev`, among them
Phil's engine-only CL 2079218. The two engine changelists of arnaud.storq (1890839, 1896115)
and Phil's RuntimeGrid ones (2025678, 2048903) went through Dev-Engine. No written rule says
which stream to pick: ask the reviewer when in doubt.

## Which local workspace

Use **`MTLWKS20850_SunDevEngine`** (root `D:\SunDevEng`), the workspace CL 1890839 and
CL 1896115 were submitted from. The other workspaces of the machine are not for this:

| Workspace | Root | Stream | For engine submits |
|-----------|------|--------|--------------------|
| `MTLWKS20850_SunDevEngine` | `D:\SunDevEng` | `//sun/Dev-Engine` | **Yes** |
| `arnaud.storq-sun-2` | `D:\Sun` | `//sun/Dev-NoAssets`, virtual stream of `//sun/Dev` | No: daily work, its submits land in `//sun/Dev` |
| `Arnaud.Storq_MTLWKS20850_2425_DevEngUpg` | `D:\DevEngUpg` | `//sun/Dev-EngineUpgrade` | No: engine upgrade stream, last used 2025-07 |
| `Arnaud.Storq-sun-3` | `D:\SunDev` | `//sun/Dev` | No: incomplete sync |

- **Selecting it**: `D:\SunDevEng\p4.ini` sets `P4CLIENT=MTLWKS20850_SunDevEngine` and the
  machine has `P4CONFIG=p4.ini`, so any `p4` command run inside `D:\SunDevEng` uses it. In P4V,
  switch to that workspace. UGS already has it (project
  `//sun/Dev-Engine/Sundance/Sundance.uproject`).
- **Content**: the whole project (`Engine`, `Sundance`, `UE5.sln`), minus most of
  `Sundance/Assets/...`, as in `Dev-NoAssets`. The editor can be built and run there.
- **State on 2026-09-30: stale.** No file in it is newer than CL 1896115 (2026-05-26), and
  its `submitsidekick.config.json` is at #12 while the depot is at #15.

## Step 1 — Sync the Dev-Engine workspace

Sync the whole workspace (UGS or P4V), then build the editor from `D:\SunDevEng\UE5.sln` if
you test there. Submit Sidekick reads the `submitsidekick.config.json` of the workspace root
([step 3](#step-3--submit-with-submit-sidekick)), so that file must be at head.

To move a change already built and tested in Dev, the strict minimum is that file plus the
files to submit:

```powershell
cd D:\SunDevEng
p4 sync //sun/Dev-Engine/submitsidekick.config.json <depot paths of the files to submit>
```

The workspace is then mixed and cannot be built: the only build of the change is the one
done in Dev.

## Step 2 — Put the change in a Dev-Engine changelist

### Option A — Write the change in the Dev-Engine workspace

Edit, build and test in `D:\SunDevEng`, then create the pending changelist in
`MTLWKS20850_SunDevEngine`. This is how CL 1890839 and CL 1896115 were made.

### Option B — Move a changelist prepared in Dev

Shelve the changelist in the Dev workspace, then unshelve it in the Dev-Engine workspace
through the branch view Perforce generates between the two streams:

```powershell
# 1. In D:\Sun: shelve the Dev changelist, or refresh its shelf
cd D:\Sun
p4 shelve -r -c <DevCL>

# 2. In P4V, workspace MTLWKS20850_SunDevEngine: create a pending changelist with the
#    same description and note its number, <EngCL>

# 3. In D:\SunDevEng: unshelve through the Dev -> Dev-Engine view, then resolve
cd D:\SunDevEng
p4 unshelve -s <DevCL> -S //sun/Dev-Engine -P //sun/Dev -c <EngCL>
p4 resolve -am -c <EngCL>
```

- `-S //sun/Dev-Engine -P //sun/Dev` generates the view `//sun/Dev-Engine/... //sun/Dev/...`
  (minus the isolated and excluded paths): each `//sun/Dev/...` file of the shelf opens on
  its `//sun/Dev-Engine/...` twin.
- The unshelve always leaves a resolve (`must resolve //sun/Dev/...@=<DevCL> before
  submitting`). With the workspace at head and the file identical in both streams,
  `p4 resolve -am` should just take the shelved content. Check the diff before submitting.
- Cross-stream unshelve needs the shelf to come from the same edge server. Both workspaces
  are bound to `mtl-p4rslc01`.
- Keep the Dev changelist until its robomerged copy shows up in `//sun/Dev`
  ([step 4](#step-4--follow-the-robomerge-to-dev)). Then drop it and sync `D:\Sun` as usual:

```powershell
cd D:\Sun
p4 shelve -d -c <DevCL>
p4 revert -c <DevCL> //...
p4 change -d <DevCL>
```

## Step 3 — Submit with Submit Sidekick

In P4V, on the Dev-Engine workspace, right-click the changelist →
**AVA: Submit Sidekick (Changelist)...**. The tool starts `SubmitSidekickLauncher.exe` with
`-ConfigFile $r\submitsidekick.config.json`, `$r` being the workspace root. From
`D:\SunDevEng` it therefore loads the Dev-Engine configuration, whose code category is
`Sundance Dev-Engine Code`, with the Dev-Engine CIS builds.

### Description format

The configuration builds the description in this order: type and category, feature,
description, tested, reviewers, approval, Jira. CL 1890839 as submitted:

```text
@MINOR $TOOLS
Stop spawning ghost UActorFolder assets for Level Instance actor folders during world folders rebuild
&TESTED Editor
@REVIEW Philippe St-Jean (WBGMontreal); Pierre-Luc Boulet (WBGMontreal)
[approved:jnelson]

[jira:SUNDANCE-54425;SUNDANCE-41837]
```

| Field | Values in the Dev-Engine configuration | Required |
|-------|----------------------------------------|----------|
| Type (`@MINOR`) | `Major`, `Minor`, `BugFix`, `BuildFix`, `Optimization` | Yes |
| Category (`$TOOLS`) | a fixed list of 66 values, e.g. `Editor`, `Engine`, `Streaming`, `Tools` | Yes |
| Tested (`&TESTED`) | `Editor`, `PC`, `PS5`, `PS5Pro`, `Server`, `Switch2`, `XSX` | Yes |
| Reviewers (`@REVIEW`) | at least one reviewer | Yes |
| Approval (`[approved:<user>]`) | a member of the lock group | Only while the stream is locked |
| Jira (`[jira:...]`) | `SUNDANCE`, `PHOENIX` or `SOLITUDE` issues | Yes |

**Approval.** The configuration defines the lock types `None`, `Soft`, `Hard`, `JIRA_Soft`
and `JIRA_Hard`. All but `None` require an approver, from `role_sun_lock_soft` for the soft
locks and `role_sun_lock_hard` for the hard ones. CL 1890839 carries `[approved:jnelson]`, and
jnelson is in `role_sun_lock_soft`; CL 1896115, four days later, carries none. So the
approval depends on the lock state of the stream at submit time, not on the change being
engine code.

### What Submit Sidekick checks

- **Validators**: `CheckForBrokenCIS`, `CheckForLocalFiles`, `CheckUserEdits`,
  `CheckChangesFreeze`, `CheckForJIRA`, `CheckForQaApprovedAndUe`,
  `CheckWithValidatonScripts` (sic).
- **CIS**: the last finished builds of the four Dev-Engine TeamCity configurations,
  `Sundance_DevEngine_CompileEditor_Win64Development`,
  `Sundance_DevEngine_CompileGame_Win64_CompileAll`,
  `Sundance_DevEngine_CompileGame_Xsx_AllConfigurations` and
  `Sundance_DevEngine_CompileGame_Ps5_CompilePs5`. Every type checks them except `BuildFix`.
- **Scripts** on the files of the changelist: `IncrementalGCValidation` (`.h`),
  `NoCheckInStrings` (`.h`, `.cpp`, `.py`, `.cs`) and `PlatformAssetOverridesSubmitChanges`
  (`.ini`, `.uasset`). The Dev configuration also runs `PermissionToSubmitIniFile` and
  `JsonParseValidation`; Dev-Engine does not.
- **Swarm** (`https://slc-swarm.wbiegames.com`): enabled, not required.
- **Preflight**: `PreflightSettings` names the TeamCity project
  `Sundance_Dev_Preflight_BuildPreflight` in both streams. Not tried on a Dev-Engine
  changelist.

## Step 4 — Follow the robomerge to Dev

The `SUN (Dev-Engine -> Dev)` bot re-submits the change in `//sun/Dev` **under the author's
name**, from the client `SVC_ROBOMERGE_LINUX_ROBOMERGE_SUN_Dev_FROM_Dev_Engine`. The
description gets `#ROBOMERGE` on top and a footer, here from CL 2051632:

```text
#ROBOMERGE-OWNER: @ tyler.dawson
#ROBOMERGE-AUTHOR: philippe.st-jean
#ROBOMERGE-SOURCE: CL 2048903 in //sun/Dev-Engine/...
#ROBOMERGE-BOT: SUN (Dev-Engine -> Dev) (v0--1)
```

Count about a day:

| Dev-Engine CL | Submitted | Dev CL | In Dev |
|---------------|-----------|--------|--------|
| 1890839 | 2026-05-22 (Friday) | 1895284 | 2026-05-26 |
| 1896115 | 2026-05-26 | 1898151 | 2026-05-27 |
| 2025678 | 2026-08-18 | 2028633 | 2026-08-19 |
| 2048903 | 2026-08-31 | 2051632 | 2026-09-01 |

The stream root holds `RoboMergeCLInfo.json` with `"GateCL": "UGS"`, which suggests the merge
waits for a changelist validated in UGS. That would explain the delay.

To find the Dev copy, look for the Dev-Engine CL number in the history of a changed file:

```powershell
p4 changes -l -m 5 //sun/Dev/Engine/Source/Runtime/Engine/Classes/Engine/Level.h | Select-String '^Change|ROBOMERGE-SOURCE'
```

```text
Change 1898151 on 2026/05/27 by arnaud.storq@SVC_ROBOMERGE_LINUX_ROBOMERGE_SUN_Dev_FROM_Dev_Engine
	#ROBOMERGE-SOURCE: CL 1896115 in //sun/Dev-Engine/...
```

Because they carry the author's name, the robomerged changelists show up in
`p4 changes -u arnaud.storq`; [P4-History](../WorkDoneByChangelists/P4-History/README.md)
filters them out (`#ROBOMERGE`).

## Worked example: CL 2102948

CL 2102948 (`RuntimeGrid: resolve None when validating actor references`, see
[Effective RuntimeGrid reference validation](EffectiveRuntimeGridReferenceValidation.md)) is
pending and shelved in `D:\Sun`, so in `//sun/Dev`. It touches one file,
`WorldPartitionStreamingGeneration.cpp`. On 2026-09-30:

- the file is identical in `//sun/Dev` (#19, the base of the change) and
  `//sun/Dev-Engine` (#18);
- `D:\SunDevEng` has #14 of it;
- the shelf matches the local file in `D:\Sun`, so no re-shelve is needed.

To submit it through Dev-Engine:

```powershell
cd D:\SunDevEng
p4 sync //sun/Dev-Engine/submitsidekick.config.json //sun/Dev-Engine/Engine/Source/Runtime/Engine/Private/WorldPartition/WorldPartitionStreamingGeneration.cpp
# or a full sync, to build and test in D:\SunDevEng
# create <EngCL> in P4V with the description of 2102948
p4 unshelve -s 2102948 -S //sun/Dev-Engine -P //sun/Dev -c <EngCL>
p4 resolve -am -c <EngCL>
```

The unshelve, previewed with `-n`, maps the file as expected:

```text
... //sun/Dev-Engine/Engine/Source/Runtime/Engine/Private/WorldPartition/WorldPartitionStreamingGeneration.cpp - must resolve //sun/Dev/Engine/Source/Runtime/Engine/Private/WorldPartition/WorldPartitionStreamingGeneration.cpp@=2102948 before submitting
```

Before submitting, replace `&TESTED Compile`: `Compile` is not a Submit Sidekick value. Use
`Editor` once the A/B test is done.

## See also

- [Perforce source control](PerforceSourceControl.md) — checkout, locked files, changelist
  validators
- [Peeves submit validation](PeevesSubmitValidation.md) — the validation run at submit
- [Effective RuntimeGrid reference validation](EffectiveRuntimeGridReferenceValidation.md) —
  the change of CL 2102948
- [CL 1890839](../WorkDoneByChangelists/P4-History/2026-05-22-09-04-stop-ghost-actorfolder-assets.md)
  and [CL 1896115](../WorkDoneByChangelists/P4-History/2026-05-26-14-39-expose-fixupactorfolders.md)
  — the two Dev-Engine submits of arnaud.storq
