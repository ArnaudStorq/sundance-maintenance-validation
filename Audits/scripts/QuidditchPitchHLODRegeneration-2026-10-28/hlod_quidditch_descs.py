import unreal

descs = unreal.WorldPartitionBlueprintLibrary.get_actor_descs()


def fmt_box(b):
    return f"min=({b.min.x:.0f},{b.min.y:.0f},{b.min.z:.0f}) max=({b.max.x:.0f},{b.max.y:.0f},{b.max.z:.0f})"


for d in descs:
    label = str(d.get_editor_property("label"))
    if label.startswith("LV_HW_HLODLayer") or label == "LI_QuidditchPitch" or label.startswith("LI_Hogwarts"):
        dls = [str(a.export_text()).rsplit(".", 1)[-1] for a in d.get_editor_property("data_layer_assets")]
        print(f"{label:60s} grid={str(d.get_editor_property('runtime_grid')):22s} spatial={d.get_editor_property('is_spatially_loaded')} "
              f"{fmt_box(d.get_editor_property('bounds'))} dl={dls} pkg={d.get_editor_property('actor_package')}")
