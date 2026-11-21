import bpy
import json
import os

COLL = "L1_P0B4_Z10"
OUT = "/home/riyo/Documentos/game/assets/models/fm/p0b4_z10_services.glb"
REPORT = "/home/riyo/Documentos/game/docs/fm_p0b4_export.json"
STRAYS = ("PROP_Z10_LockerDoor_01", "STUDIO_Z10_Backdrop", "STUDIO_Z10_Floor")


def tri_count(ob):
    me = ob.data
    me.calc_loop_triangles()
    return len(me.loop_triangles)


def main():
    col = bpy.data.collections.get(COLL)
    if not col:
        raise RuntimeError("missing collection " + COLL)
    objs = [o for o in col.objects if o.type == 'MESH' and o.name != "P0B4_RISER_PASS_PLATES"]
    # include riser plates too; they are part of the service package
    objs = [o for o in col.objects if o.type == 'MESH']
    for o in bpy.context.selected_objects:
        o.select_set(False)
    for o in objs:
        o.hide_set(False)
        o.hide_viewport = False
        o.hide_render = False
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]

    saved = {}
    for name in STRAYS:
        ob = bpy.data.objects.get(name)
        if not ob:
            continue
        saved[name] = [c.name for c in ob.users_collection]
        for c in list(ob.users_collection):
            c.objects.unlink(ob)
    try:
        bpy.ops.export_scene.gltf(
            filepath=OUT,
            export_format='GLB',
            use_selection=True,
            export_apply=True,
            export_yup=True,
            export_texcoords=True,
            export_normals=True,
            export_materials='EXPORT',
            export_cameras=False,
            export_lights=False,
        )
    finally:
        for name, cols in saved.items():
            ob = bpy.data.objects.get(name)
            for cname in cols:
                c = bpy.data.collections.get(cname)
                if c and ob.name not in c.objects:
                    c.objects.link(ob)

    total_tris = sum(tri_count(o) for o in objs)
    unique_meshes = len({o.data.name for o in objs})
    report = {
        "glb": OUT,
        "collection": COLL,
        "objects": len(objs),
        "unique_meshes": unique_meshes,
        "total_tris": total_tris,
        "bytes": os.path.getsize(OUT),
        "names": sorted(o.name for o in objs),
    }
    with open(REPORT, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
    print("P0B4_EXPORT_DONE", len(objs), unique_meshes, total_tris, report["bytes"])


main()
