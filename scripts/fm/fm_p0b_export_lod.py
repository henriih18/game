"""P0b.3 — exporta la columna de servicios con LOD0/LOD1/LOD2.

Salida: assets/models/fm/p0b_corridor_services_lod.glb
Informe: docs/fm_p0b_export_lod.json

Los LOD1/LOD2 viven ocultos en L1_P0B_LOD; se hacen visibles y
seleccionables solo durante la exportación y se restauran en finally.
No guarda el .blend.
"""
import bpy
import json
import os
import time
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
OUT = os.path.join(ROOT, "assets/models/fm/p0b_corridor_services_lod.glb")
REPORT = os.path.join(ROOT, "docs/fm_p0b_export_lod.json")
LOD0_COLL = "L1_P0B_SERVICES"
LOD_COLL = "L1_P0B_LOD"


def deselect_all():
    for ob in bpy.data.objects:
        try:
            ob.select_set(False)
        except RuntimeError:
            pass


def aabb_of(objects):
    lo = Vector((1e9, 1e9, 1e9))
    hi = Vector((-1e9, -1e9, -1e9))
    for ob in objects:
        for corner in ob.bound_box:
            p = ob.matrix_world @ Vector(corner)
            for i in range(3):
                lo[i] = min(lo[i], p[i])
                hi[i] = max(hi[i], p[i])
    return lo, hi


def stats(objects):
    tris = 0
    verts = 0
    for ob in objects:
        me = ob.data
        me.calc_loop_triangles()
        tris += len(me.loop_triangles)
        verts += len(me.vertices)
    return verts, tris


def main():
    lod0_coll = bpy.data.collections.get(LOD0_COLL)
    lod_coll = bpy.data.collections.get(LOD_COLL)
    if lod0_coll is None or lod_coll is None:
        raise RuntimeError("Missing P0b collections")
    lod0 = [ob for ob in lod0_coll.objects if ob.type == "MESH"]
    lod1 = [ob for ob in lod_coll.objects if ob.type == "MESH" and ob.name.endswith("_LOD1")]
    lod2 = [ob for ob in lod_coll.objects if ob.type == "MESH" and ob.name.endswith("_LOD2")]
    if len(lod0) != 17 or len(lod1) != 17 or len(lod2) != 17:
        raise RuntimeError(
            "Unexpected LOD counts: %d/%d/%d" % (len(lod0), len(lod1), len(lod2))
        )
    objects = lod0 + lod1 + lod2
    lo, hi = aabb_of(lod0)
    v0, t0 = stats(lod0)
    v1, t1 = stats(lod1)
    v2, t2 = stats(lod2)

    deselect_all()
    hidden_state = {}
    for ob in lod1 + lod2:
        hidden_state[ob.name] = (
            ob.hide_render, ob.hide_viewport, ob.hide_get()
        )
        ob.hide_render = False
        ob.hide_viewport = False
        ob.hide_set(False)
    for ob in objects:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = lod0[0]

    stray_names = (
        "PROP_Z10_LockerDoor_01",
        "STUDIO_Z10_Backdrop",
        "STUDIO_Z10_Floor",
    )
    saved_collections = {}
    for name in stray_names:
        stray = bpy.data.objects.get(name)
        if stray is None:
            continue
        saved_collections[name] = list(stray.users_collection)
        for owner in list(stray.users_collection):
            owner.objects.unlink(stray)

    try:
        bpy.ops.export_scene.gltf(
            filepath=OUT,
            export_format="GLB",
            use_selection=True,
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
        for name, owners in saved_collections.items():
            stray = bpy.data.objects.get(name)
            if stray is None:
                continue
            for owner in owners:
                if stray.name not in owner.objects:
                    owner.objects.link(stray)
        for ob in lod1 + lod2:
            state = hidden_state.get(ob.name)
            if state is None:
                continue
            ob.hide_render, ob.hide_viewport, _ = state
            ob.hide_set(True)
        deselect_all()

    size = os.path.getsize(OUT) if os.path.exists(OUT) else -1
    report = {
        "started": time.strftime("%Y-%m-%d %H:%M:%S"),
        "path": os.path.relpath(OUT, ROOT),
        "objects": len(objects),
        "objects_by_lod": {"LOD0": len(lod0), "LOD1": len(lod1), "LOD2": len(lod2)},
        "meshes": len({ob.data.name for ob in objects}),
        "vertices": {"LOD0": v0, "LOD1": v1, "LOD2": v2},
        "triangles": {"LOD0": t0, "LOD1": t1, "LOD2": t2},
        "triangles_total": t0 + t1 + t2,
        "bytes": size,
        "aabb_min": [round(v, 4) for v in lo],
        "aabb_max": [round(v, 4) for v in hi],
        "aabb_size": [round(hi[i] - lo[i], 4) for i in range(3)],
        "names": sorted(ob.name for ob in objects),
    }
    with open(REPORT, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
    print("P0B_LOD_EXPORTED", json.dumps(report, ensure_ascii=False))


main()
