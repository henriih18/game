import bpy
import json
import os
import shutil

ROOT = "/home/riyo/Documentos/game"
BLEND = os.path.join(ROOT, "nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend")
BACKUP = os.path.join(ROOT, "docs/backups/FM_LEVEL1_V06_ARCH_before_asset_library.blend")
QA = os.path.join(ROOT, "docs/FM_ASSET_LIBRARY_STEP1.json")

LEVEL = "NEXUS_L1_V06_ARCH"
LIB_SCENE = "FM_ASSET_LIBRARY"
LIB_ROOT = "FM_LIBRARY"
CORRIDOR = "LIB_CORRIDOR_HERO"


def main():
    if os.path.exists(BLEND) and not os.path.exists(BACKUP):
        shutil.copy2(BLEND, BACKUP)
    if bpy.data.collections.get(LIB_ROOT):
        print("STEP1_ALREADY_DONE", LIB_ROOT)
        return
    level = bpy.data.scenes.get(LEVEL)
    shared = bpy.data.collections.get("L1_SHARED_HERO")
    if level is None or shared is None:
        raise RuntimeError("Missing level scene or L1_SHARED_HERO")

    lib = bpy.data.scenes.new(LIB_SCENE)
    if level.world:
        lib.world = level.world
    root = bpy.data.collections.new(LIB_ROOT)
    lib.collection.children.link(root)
    corridor = bpy.data.collections.new(CORRIDOR)
    root.children.link(corridor)

    for scene in bpy.data.scenes:
        if shared.name in scene.collection.children:
            scene.collection.children.unlink(shared)
    for coll in bpy.data.collections:
        if coll is corridor:
            continue
        if shared.name in coll.children:
            coll.children.unlink(shared)
    corridor.children.link(shared)

    if bpy.context.window:
        bpy.context.window.scene = level
    bpy.context.view_layer.update()

    level_names = {o.name for o in level.objects}
    shared_names = {o.name for o in shared.all_objects}
    remaining = sorted(level_names & shared_names)
    report = {
        "library_scene": LIB_SCENE,
        "library_root": LIB_ROOT,
        "corridor_collection": CORRIDOR,
        "shared_objects": len(shared.all_objects),
        "shared_tris": sum(len(o.data.polygons) * 2 for o in shared.all_objects if o.type == 'MESH'),
        "level_objects": len(level.objects),
        "shared_names_remaining_in_level": remaining[:20],
        "shared_remaining_count": len(remaining),
        "library_scene_objects": len(lib.objects),
        "library_scene_collections": [c.name for c in lib.collection.children],
    }
    with open(QA, "w") as fh:
        json.dump(report, fh, indent=2)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("STEP1_DONE", len(shared.all_objects), len(level.objects), len(remaining), len(lib.objects))


main()
