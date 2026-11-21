"""P0b.1 — exportación de la columna de servicios del corredor.

Exporta la colección L1_P0B_SERVICES completa a
assets/models/fm/p0b_corridor_services.glb y escribe un informe con
conteos y AABB. No guarda el .blend.
"""
import bpy
import json
import os
import time
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
OUT = os.path.join(ROOT, "assets/models/fm/p0b_corridor_services.glb")
REPORT = os.path.join(ROOT, "docs/fm_p0b_export.json")
COLL_NAME = "L1_P0B_SERVICES"


def deselect_all():
    for ob in bpy.data.objects:
        try:
            ob.select_set(False)
        except RuntimeError:
            pass


def main():
    coll = bpy.data.collections.get(COLL_NAME)
    if coll is None:
        raise RuntimeError("Missing collection " + COLL_NAME)
    objects = [ob for ob in coll.objects if ob.type == "MESH"]
    if not objects:
        raise RuntimeError("No mesh objects in " + COLL_NAME)

    tris = 0
    verts = 0
    lo = Vector((1e9, 1e9, 1e9))
    hi = Vector((-1e9, -1e9, -1e9))
    for ob in objects:
        me = ob.data
        me.calc_loop_triangles()
        tris += len(me.loop_triangles)
        verts += len(me.vertices)
        for corner in ob.bound_box:
            p = ob.matrix_world @ Vector(corner)
            for i in range(3):
                lo[i] = min(lo[i], p[i])
                hi[i] = max(hi[i], p[i])

    deselect_all()
    for ob in objects:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]

    # El exportador glTF incluye objetos visibles aunque no estén
    # seleccionados. Se desvinculan temporalmente los strays conocidos de
    # Z10 para garantizar que el GLB contenga solo la columna P0b.
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

    size = os.path.getsize(OUT) if os.path.exists(OUT) else -1
    report = {
        "started": time.strftime("%Y-%m-%d %H:%M:%S"),
        "collection": COLL_NAME,
        "path": os.path.relpath(OUT, ROOT),
        "objects": len(objects),
        "meshes": len({ob.data.name for ob in objects}),
        "vertices": verts,
        "triangles": tris,
        "bytes": size,
        "aabb_min": [round(v, 4) for v in lo],
        "aabb_max": [round(v, 4) for v in hi],
        "aabb_size": [round(hi[i] - lo[i], 4) for i in range(3)],
        "names": sorted(ob.name for ob in objects),
    }
    with open(REPORT, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
    print("P0B_EXPORTED", json.dumps(report, ensure_ascii=False))


main()
