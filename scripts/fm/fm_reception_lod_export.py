import bpy
import json
import os

ROOT = "/home/riyo/Documentos/game"
GLB = os.path.join(ROOT, "assets/models/fm/reception_lod_test.glb")
REPORT = os.path.join(ROOT, "docs/fm_reception_lod_export.json")
SOURCES = [
    "L1_RECEPTION_R6_HERO",
    "L1_RECEPTION_R7_HERO",
    "L1_RECEPTION_R8_HERO",
    "L1_RECEPTION_R9_HERO",
    "L1_RECEPTION_R12_HERO",
    "L1_RECEPTION_R13_HERO",
]
LOD_COL = "L1_RECEPTION_LOD"
TMP = "REC_LOD_EXPORT_TMP"


def tris(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def find_layer(layer, name):
    if layer.name == name:
        return layer
    for child in layer.children:
        found = find_layer(child, name)
        if found:
            return found
    return None


def main():
    scene = bpy.context.scene
    selected = []
    for cname in SOURCES:
        col = bpy.data.collections.get(cname)
        if col is None:
            continue
        for ob in col.all_objects:
            if ob is None or ob.type != 'MESH':
                continue
            if ob.name.endswith("_LOD1") or ob.name.endswith("_LOD2"):
                continue
            if tris(ob) < 2000:
                continue
            selected.append(ob)
    lod_col = bpy.data.collections.get(LOD_COL)
    if lod_col:
        selected.extend([ob for ob in lod_col.all_objects if ob is not None and ob.type == 'MESH'])
    selected = list(dict.fromkeys(selected))

    tmp = bpy.data.collections.get(TMP)
    if tmp:
        bpy.data.collections.remove(tmp)
    tmp = bpy.data.collections.new(TMP)
    scene.collection.children.link(tmp)
    state = {}
    for ob in selected:
        state[ob.name] = (ob.parent, ob.matrix_world.copy(), ob.hide_render, ob.hide_viewport, ob.hide_get())
        tmp.objects.link(ob)
        ob.parent = None
        ob.hide_render = False
        ob.hide_viewport = False
        ob.hide_set(False)
    bpy.context.view_layer.update()

    layer = find_layer(bpy.context.view_layer.layer_collection, TMP)
    bpy.context.view_layer.active_layer_collection = layer
    bpy.ops.export_scene.gltf(
        filepath=GLB,
        export_format='GLB',
        use_selection=False,
        use_active_collection=True,
        use_active_collection_with_nested=True,
        export_lights=False,
        export_cameras=False,
        export_apply=False,
    )

    for ob in selected:
        parent, mw, hr, hv, hs = state[ob.name]
        ob.parent = parent
        ob.matrix_world = mw
        ob.hide_render = hr
        ob.hide_viewport = hv
        ob.hide_set(hs)
    bpy.data.collections.remove(tmp)
    bpy.context.view_layer.update()

    unique = {ob.data.name for ob in selected}
    report = {
        "glb": GLB,
        "bytes": os.path.getsize(GLB) if os.path.exists(GLB) else 0,
        "objects": len(selected),
        "meshes_unique": len(unique),
        "tris": sum(tris(ob) for ob in selected),
        "names": sorted(ob.name for ob in selected),
    }
    with open(REPORT, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print("RECEPTION_LOD_EXPORT", json.dumps({k: report[k] for k in ("bytes", "objects", "meshes_unique", "tris")}))


main()
