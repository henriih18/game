"""Export the Z10 abandonment meshes and practical lights to GLB."""

import bpy
import json
import os
from mathutils import Vector

OUT = "/home/riyo/Documentos/game"
GLB = OUT + "/assets/models/fm/z10_abandon.glb"
REPORT = OUT + "/docs/fm_z10_abandon_export.json"

STRAYS = ("PROP_Z10_LockerDoor_01", "STUDIO_Z10_Backdrop", "STUDIO_Z10_Floor")


def target_objects():
    objs = []
    for cname in ("L1_Z10_ABANDON", "L1_Z10_LIGHTING"):
        col = bpy.data.collections.get(cname)
        if not col:
            continue
        for ob in col.all_objects:
            if ob.type in {'MESH', 'LIGHT'} and ob.name != "VOL_Z10_Fog":
                if ob not in objs:
                    objs.append(ob)
    return objs


def aabb(objs):
    lo = Vector((1e30, 1e30, 1e30))
    hi = Vector((-1e30, -1e30, -1e30))
    found = False
    for ob in objs:
        if ob.type != 'MESH':
            continue
        for corner in ob.bound_box:
            p = ob.matrix_world @ Vector(corner)
            lo.x = min(lo.x, p.x); lo.y = min(lo.y, p.y); lo.z = min(lo.z, p.z)
            hi.x = max(hi.x, p.x); hi.y = max(hi.y, p.y); hi.z = max(hi.z, p.z)
            found = True
    return ([round(v, 5) for v in lo], [round(v, 5) for v in hi]) if found else (None, None)


def main():
    bpy.context.view_layer.update()
    objs = target_objects()
    meshes = [ob for ob in objs if ob.type == 'MESH']
    lights = [ob for ob in objs if ob.type == 'LIGHT']
    tris = sum(len(ob.data.loop_triangles) for ob in meshes)
    unique = len({ob.data.name for ob in meshes})
    lo, hi = aabb(objs)

    hidden_state = {}
    for ob in objs:
        hidden_state[ob.name] = (ob.hide_get(), ob.hide_viewport, ob.hide_render)
        ob.hide_set(False)
        ob.hide_viewport = False
        ob.hide_render = False

    detached = []
    for name in STRAYS:
        ob = bpy.data.objects.get(name)
        if not ob:
            continue
        cols = list(ob.users_collection)
        for col in cols:
            col.objects.unlink(ob)
        detached.append((ob, cols))

    bpy.ops.object.select_all(action='DESELECT')
    for ob in objs:
        ob.select_set(True)
    if objs:
        bpy.context.view_layer.objects.active = objs[0]

    try:
        bpy.ops.export_scene.gltf(
            filepath=GLB,
            export_format='GLB',
            use_selection=True,
            export_apply=False,
            export_lights=True,
            export_cameras=False,
            export_yup=True,
        )
    finally:
        for ob, cols in detached:
            for col in cols:
                col.objects.link(ob)
        for name, (hset, hview, hrender) in hidden_state.items():
            ob = bpy.data.objects.get(name)
            if ob:
                ob.hide_set(hset)
                ob.hide_viewport = hview
                ob.hide_render = hrender

    data = {
        "glb": GLB,
        "bytes": os.path.getsize(GLB),
        "objects": len(objs),
        "meshes": len(meshes),
        "unique_meshes": unique,
        "lights": len(lights),
        "tris": tris,
        "bbox_min": lo,
        "bbox_max": hi,
        "names": sorted(ob.name for ob in objs),
        "light_names": sorted(ob.name for ob in lights),
    }
    with open(REPORT, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    print("Z10_ABANDON_EXPORT", len(objs), len(meshes), unique, len(lights), tris,
          os.path.getsize(GLB), lo, hi)
    print("REPORT", REPORT)


main()
