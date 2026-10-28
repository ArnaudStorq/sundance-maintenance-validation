import unreal

FOLDER = "/Game/Data/WorldPartition/HLOD/Hogwarts"
reg = unreal.AssetRegistryHelpers.get_asset_registry()
assets = reg.get_assets_by_path(FOLDER, recursive=True)


def safe(obj, prop):
    try:
        return obj.get_editor_property(prop)
    except Exception as e:
        return f"<err {e}>"


def dump_condition(c):
    out = {}
    for p in ["logic_operator", "actor_types", "actor_tags", "outliner_path_contains",
              "use_max_bounds_dimension", "max_bounds_dimension", "use_max_bounds_volume", "max_bounds_volume",
              "use_min_bounds_dimension", "min_bounds_dimension", "use_min_bounds_volume", "min_bounds_volume",
              "use_runtime_grid", "runtime_grid", "use_is_inside_level_instance", "is_inside_level_instance"]:
        out[p] = safe(c, p)
    return out


for a in assets:
    obj = a.get_asset()
    print("=" * 80)
    print(a.package_name, obj.get_class().get_name())
    if isinstance(obj, unreal.HLODLayer):
        for p in ["layer_type", "parent_layer", "is_spatially_loaded", "cell_size", "loading_range",
                  "hlod_builder_settings", "hlod_modifier_class", "hlod_actor_class"]:
            print(f"  {p}: {safe(obj, p)}")
    else:
        for p in ["is_enabled", "target_hlod_layer", "include_in_hlod"]:
            print(f"  {p}: {safe(obj, p)}")
        conds = safe(obj, "matching_conditions")
        if isinstance(conds, unreal.Array):
            for i, c in enumerate(conds):
                print(f"  cond[{i}]: {dump_condition(c)}")
        ex = safe(obj, "exclusion_criteria")
        if not isinstance(ex, str):
            for p in ["types_to_exclude", "data_layer_rules_to_exclude", "hlod_layer_rules_to_exclude",
                      "runtime_grid_rules_to_exclude", "exclude_if_not_spatially_loaded", "actor_tags_to_exclude",
                      "outliner_paths_to_exclude", "use_is_inside_level_instance", "is_inside_level_instance"]:
                print(f"  excl.{p}: {safe(ex, p)}")
