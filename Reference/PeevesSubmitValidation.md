# Peeves — validation at submit

**Peeves** is WB Games Montréal's in-house validation framework that runs at Perforce
submit. It is not a single C++ class; it is a **Python framework + a C++ bridge
plugin** that wraps Unreal's Data Validation stack and the Perforce submit UI.

- **Project owner:** David Jones (`davjones`).
- **Support channel:** Slack `#peeves-support`.

> The WB tweak in `DataValidationChangelist.cpp` ("checked out = warning, added =
> error, to match how we validate in Peeves") is tagged `[davjones]` — i.e. the Peeves
> owner keeps the engine Data Validation behaviour aligned with Peeves.

---

## Where it lives

| Component | Path |
|-----------|------|
| Plugin | `D:\Sun\Sundance\Plugins\PeevesPlugin\PeevesPlugin.uplugin` (modules `PeevesPluginDev`, `PeevesPluginEditor`; depends on `DataValidation`, `PythonScriptPlugin`) |
| Python framework | `D:\Sun\Sundance\Plugins\AvaPython\Content\Python\PEEVES\` |
| Main config | `…\PEEVES\Config\peeves.ini.json` |
| C++ bridge | `…\PeevesPlugin\Source\PeevesPluginEditor\Private\PeevesScriptHelpers.cpp` |
| Changelist verifier | `…\PEEVES\Scripts\Verifiers\verify_changelist.py` |
| Asset verifier | `…\PEEVES\Scripts\Verifiers\verify_assets.py` |
| Submit UI | `…\Plugins\UESSKPlugin-UE53\` (Changelist Manager / WPerforceControl) |

---

## Submit-time flow

1. **`verify_changelist.py`** (`VerifyChangelist`): cross-changelist dependency rules,
   content-override checks, then calls
   `unreal.PeevesScriptHelpers.is_changelist_valid(cl, False, PRE_SUBMIT)`.
2. **`UPeevesScriptHelpers::IsChangelistValid`** (`PeevesScriptHelpers.cpp:951`) builds a
   `UDataValidationChangelist` and runs the whole UE validator stack:
   - native `UObject::IsDataValid`
   - all enabled `UEditorValidatorBase` subclasses, including
     `UWorldPartitionChangelistValidator`, `UDirtyFilesChangelistValidator`, and the
     Sundance `UWorldPartitionMapCheckValidator` (see
     [Perforce source control](PerforceSourceControl.md) for those messages).
3. **`verify_assets.py --mode presubmit`** runs each asset's `verify()` in
   `PreSubmit` mode.

So Peeves is the umbrella; the World Partition / changelist correctness rules described
in [Perforce source control](PerforceSourceControl.md) are enforced **through** it. The WB tweak in
`DataValidationChangelist.cpp` explicitly exists to "match how we validate in Peeves"
(added refs = error, checked-out refs = warning).

---

## What Peeves validates (high level)

From `peeves.ini.json` and the per-asset Python classes:

- **Submit-location whitelist** — assets must be under allowed mount paths; otherwise
  `asset_invalid_location`: *"Submitting asset in an invalid location. Refer to
  guidelines for correct location."*
- **Dependency rules** — illegal Phoenix/dev/experimental/override references;
  conjurable-item placement constraints (`external_actors` / `world_assets` groups).
- **Blocked-group submission** — e.g. metadata system, MetaHuman transient assets.
- **Per-asset-class verify** — static meshes, textures, animations, blueprints, worlds…
- **MapCheck integration** — `world.py` runs `PeevesScriptHelpers.do_map_check(obj)`;
  MapCheck warnings/errors fail presubmit unless matched by
  `World.ignore_map_check_warnings` patterns.

---

## Non-partitioned levels at submit (the objective and the decision)

**Objective discussed:** make it a **blocking error at submit** when a *non-partitioned*
level is submitted, nudging the author to partition it.

**Current reality in the code** — there is **no dedicated "block non-partitioned .umap"
rule**. What actually happens:

- Non-WP worlds get **full per-actor validation** at world submit (`world.py:172`),
  whereas WP levels validate their external actors individually.
- The Sundance `UWorldPartitionMapCheckValidator` warns (during MapCheck):
  *"LevelInstance '{0}' is not using World Partition. Please convert it to a World
  Partition level."*
- Engine MapCheck (WB rephrase) warns that a LevelInstance world without external
  actors *"does not support World Partition streaming."*

**Design decision (to implement / test first):** if the level is **not referenced by
`LV_Overland`**, **skip the validation entirely** — there is no point forcing
partitioning on levels outside the streamed overworld. This "is it in the `LV_Overland`
hierarchy?" gate reuses the same traversal as
[Level Instances & OFPA](LevelInstancesAndOFPA.md)/`Editor.LogNonPartitionedLevelInstances`.

**Reservation on record:** validating this at submit is fastidious — the author only
discovers the problem late (at submit), and forcing a conversion at that moment risks
data loss. Hence the preference to (a) scope it tightly to the `LV_Overland` hierarchy
and (b) lean on the migration tooling ([converting levels to World Partition](ConvertingLevelsToWorldPartition.md))
rather than a hard submit gate.

---

## Related changelists

- [WorldEvent DataLayers checkout check (CL 1758012)](../WorkDoneByChangelists/P4-History/2026-03-11-09-21-worldevent-datalayers-checkout-check.md) — a data-safety check in the same spirit.

## See also

- [Perforce source control](PerforceSourceControl.md) (the validators Peeves runs)
- [Level Instances & OFPA](LevelInstancesAndOFPA.md) (the `LV_Overland` reference test)
