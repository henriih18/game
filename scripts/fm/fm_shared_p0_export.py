"""P0a.2 — exportación de prueba para Godot.

Genera dos GLB:
  assets/models/fm/p0a_library_lod.glb  — muestra de puerta/portal/luminaria
      con LOD0/LOD1/LOD2 + colisiones, y módulos de servicio P0a.1.
  assets/models/fm/p0a_test_assembly.glb — ensamblaje de continuidad completo.

No guarda el .blend. Los materiales son procedurales; el GLB exporta solo
factores PBR, suficiente para validar geometría, escala y colisiones.
"""
import bpy
import json
import os
import time

ROOT = "/home/riyo/Documentos/game"
LIB_OUT = os.path.join(ROOT, "assets/models/fm/p0a_library_lod.glb")
TEST_OUT = os.path.join(ROOT, "assets/models/fm/p0a_test_assembly.glb")
REPORT = os.path.join(ROOT, "docs/fm_p0a2_export.json")

LIB_ROOTS = [
    "SM_SH_DOOR_SEC_SINGLE_ROOT",
    "SM_SH_DOOR_SEC_SINGLE_LOD1_ROOT",
    "SM_SH_DOOR_SEC_SINGLE_LOD2_ROOT",
    "SM_SH_PORTAL_4000_ROOT",
    "SM_SH_PORTAL_4000_LOD1_ROOT",
    "SM_SH_PORTAL_4000_LOD2_ROOT",
    "SM_SH_LUMINAIRE_1500_ON_ROOT",
    "SM_SH_LUMINAIRE_1500_ON_LOD1_ROOT",
    "SM_SH_LUMINAIRE_1500_ON_LOD2_ROOT",
    "SM_SH_HVAC_RECT800x600_L2000_ROOT",
    "SM_SH_HVAC_TEE_800x600_ROOT",
    "SM_SH_HVAC_TRANS_800x600_600x400_ROOT",
    "SM_SH_SLEEVE_RECT_600x400_ROOT",
    "SM_SH_SHAFT_ACCESS_600x1200_ROOT",
]


def deselect_all():
    for ob in bpy.data.objects:
        try:
            ob.select_set(False)
        except RuntimeError:
            pass


def select_hierarchy(root):
    root.select_set(True)
    for child in root.children_recursive:
        child.select_set(True)


def mesh_stats(objects):
    count = 0
    tris = 0
    for ob in objects:
        if ob.type != "MESH":
            continue
        count += 1
        me = ob.data
        me.calc_loop_triangles()
        tris += len(me.loop_triangles)
    return count, tris


def find_layer_collection(layer_coll, name):
    if layer_coll.collection.name == name:
        return layer_coll
    for child in layer_coll.children:
        found = find_layer_collection(child, name)
        if found is not None:
            return found
    return None


def export_glb(path, objects, report):
    deselect_all()
    for ob in objects:
        if ob.name in bpy.data.objects:
            ob.select_set(True)
    bpy.context.view_layer.objects.active = objects[0] if objects else None
    meshes, tris = mesh_stats(objects)

    # Export only the curated set, even if other objects remain selected in
    # another view layer. Linking to a temporary active collection avoids
    # strays such as PROP_Z10_LockerDoor_01.
    tmp = bpy.data.collections.new("P0_EXPORT_TMP")
    bpy.context.scene.collection.children.link(tmp)
    for ob in objects:
        if ob.name in bpy.data.objects:
            tmp.objects.link(ob)
    old_active = bpy.context.view_layer.active_layer_collection
    layer_coll = find_layer_collection(bpy.context.view_layer.layer_collection, tmp.name)
    if layer_coll is not None:
        bpy.context.view_layer.active_layer_collection = layer_coll

    try:
        bpy.ops.export_scene.gltf(
            filepath=path,
            export_format="GLB",
            use_selection=False,
            use_active_collection=True,
            use_active_collection_with_nested=True,
            export_cameras=False,
            export_lights=False,
            export_animations=False,
            export_current_frame=False,
            export_extras=True,
            export_yup=True,
            export_apply=True,
            export_image_format="WEBP",
            export_image_quality=80,
        )
    finally:
        bpy.context.view_layer.active_layer_collection = old_active
        for ob in list(tmp.objects):
            tmp.objects.unlink(ob)
        bpy.data.collections.remove(tmp)

    size = os.path.getsize(path) if os.path.exists(path) else -1
    entry = {
        "path": os.path.relpath(path, ROOT),
        "objects": len(objects),
        "meshes": meshes,
        "triangles": tris,
        "bytes": size,
    }
    report["exports"].append(entry)
    print("EXPORTED", entry)


def main():
    report = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "exports": []}

    # Library subset with LODs and collision children.
    selected = []
    missing = []
    for name in LIB_ROOTS:
        root = bpy.data.objects.get(name)
        if root is None:
            missing.append(name)
            continue
        select_hierarchy(root)
        selected.append(root)
        selected.extend(list(root.children_recursive))
    # Deduplicate while preserving order.
    seen = set()
    unique = []
    for ob in selected:
        if ob.name not in seen:
            seen.add(ob.name)
            unique.append(ob)
    report["missing_roots"] = missing
    export_glb(LIB_OUT, unique, report)

    # Full continuity test assembly.
    coll = bpy.data.collections.get("P0_TEST_ASSEMBLY")
    test_objects = [o for o in coll.objects if o.type in {"MESH", "EMPTY"}] if coll else []
    report["test_assembly_meshes"] = len(test_objects)
    export_glb(TEST_OUT, test_objects, report)

    report["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
    deselect_all()
    print("P0A2_EXPORT_DONE")
    print(json.dumps(report, indent=2, ensure_ascii=False))


main()
