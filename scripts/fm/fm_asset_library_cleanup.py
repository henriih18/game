import bpy
import json
import os

ROOT = "/home/riyo/Documentos/game"
LIB_BLEND = os.path.join(ROOT, "assets/blender/fm_shared_hero_library.blend")
QA = os.path.join(ROOT, "docs/FM_ASSET_LIBRARY_QA_FINAL.json")
KEEP = "FM_ASSET_LIBRARY"
ROOT_COL = "FM_LIBRARY"


def tris_of(col):
    total = 0
    for ob in col.all_objects:
        if ob is not None and ob.type == 'MESH':
            total += len(ob.data.polygons) * 2
    return total


def main():
    for sc in list(bpy.data.scenes):
        if sc.name != KEEP:
            print("REMOVE_SCENE", sc.name)
            bpy.data.scenes.remove(sc)

    keep_scene = bpy.data.scenes.get(KEEP)
    if keep_scene is None:
        raise RuntimeError("FM_ASSET_LIBRARY missing")

    root = bpy.data.collections.get(ROOT_COL)
    if root is None:
        raise RuntimeError("FM_LIBRARY missing")

    # Ensure the library root is linked to the kept scene.
    if root.name not in [c.name for c in keep_scene.collection.children]:
        keep_scene.collection.children.link(root)

    # Remove any other top-level collections that survived scene deletion.
    for col in list(bpy.data.collections):
        if col.name in {ROOT_COL}:
            continue
        if col.name in [c.name for c in root.children]:
            continue
        if col.name in [c.name for c in keep_scene.collection.children]:
            print("UNLINK_COLLECTION", col.name)
            keep_scene.collection.children.unlink(col)
        # Collections still used inside the library are preserved by the root subtree.

    bpy.context.view_layer.update()

    # Purge datablocks with no users, now that level/studio scenes are gone.
    try:
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
    except Exception as exc:
        print("PURGE_WARN", repr(exc))

    if bpy.context.window:
        bpy.context.window.scene = keep_scene
    bpy.context.view_layer.update()

    meshes = [o for o in root.all_objects if o is not None and o.type == 'MESH']
    objects = [o for o in root.all_objects if o is not None]
    shared = sum(1 for o in meshes if o.data.users >= 2)
    report = {
        "library_file": LIB_BLEND,
        "scenes": [s.name for s in bpy.data.scenes],
        "active_scene": keep_scene.name,
        "root_collection": ROOT_COL,
        "collections": len(root.children),
        "objects": len(objects),
        "meshes": len(meshes),
        "shared_meshes": shared,
        "tris": sum(len(o.data.polygons) * 2 for o in meshes),
        "materials": len(bpy.data.materials),
        "texts": [t.name for t in bpy.data.texts],
        "children": sorted(c.name for c in root.children),
        "bytes": os.path.getsize(LIB_BLEND),
    }
    with open(QA, "w") as fh:
        json.dump(report, fh, indent=2)
    bpy.ops.wm.save_as_mainfile(filepath=LIB_BLEND)
    print("LIBRARY_CLEAN_DONE", json.dumps(report, indent=2))


main()
