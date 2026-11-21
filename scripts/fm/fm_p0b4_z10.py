import bpy
import bmesh
import json
import math
import os
from mathutils import Vector

COLL_NAME = "L1_P0B4_Z10"
RET_NAME = "Z10_RETIRED_P0B4"
DOCS = "/home/riyo/Documentos/game/docs"

X_W = 40.2
X_E = 61.8
DUCT_Y = 20.0
DUCT_Z = 3.55
SPR_Y = 17.0
SPR_Z = 3.90
CEIL_Z = 4.19


def collection(name, parent=None):
    col = bpy.data.collections.get(name)
    if col:
        return col
    col = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(col)
    return col


def clear_collection(col):
    for ob in list(col.objects):
        bpy.data.objects.remove(ob, do_unlink=True)


def link_only(ob, col):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    col.objects.link(ob)


def cut_copy(src_name, new_name, xmin_world, xmax_world, target_y, col):
    src = bpy.data.objects.get(src_name)
    if not src:
        raise RuntimeError("missing source " + src_name)
    ob = src.copy()
    ob.data = src.data.copy()
    ob.name = new_name
    ob.data.name = new_name
    link_only(ob, col)
    ob.location.y = target_y
    lxmin = xmin_world - src.matrix_world.translation.x
    lxmax = xmax_world - src.matrix_world.translation.x
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
    bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5,
                           plane_co=(lxmin, 0, 0), plane_no=(1, 0, 0),
                           clear_inner=True, clear_outer=False)
    geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
    bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5,
                           plane_co=(lxmax, 0, 0), plane_no=(1, 0, 0),
                           clear_inner=False, clear_outer=True)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-6, edges=list(bm.edges))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(me)
    bm.free()
    me.update()
    return ob


def instance_master(master_name, new_name, col, loc, rot=(0, 0, 0)):
    src = bpy.data.objects.get(master_name)
    if not src:
        raise RuntimeError("missing master " + master_name)
    ob = bpy.data.objects.new(new_name, src.data)
    col.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = rot
    ob["fm_class"] = "SERVICE"
    ob["fm_lod"] = "LOD0"
    return ob


def add_support_extensions(col):
    src = bpy.data.objects.get("P0B_SUPPORTS_HVAC")
    mat = src.data.materials[0] if src and src.data.materials else None
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("MapaUV")
    xs = [42.6, 47.4, 52.2, 57.0]
    for xx in xs:
        for sy in (-1.0, 1.0):
            ret = bmesh.ops.create_cube(bm, size=1.0)
            verts = ret["verts"]
            bmesh.ops.scale(bm, verts=verts, vec=(0.016, 0.016, 0.200))
            bmesh.ops.translate(bm, verts=verts,
                                vec=(xx, DUCT_Y + sy * 0.46, (3.99 + CEIL_Z) / 2.0))
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for loop in f.loops:
            co = loop.vert.co
            if ax == 0:
                u, v = co.y, co.z
            elif ax == 1:
                u, v = co.x, co.z
            else:
                u, v = co.x, co.y
            loop[uvl].uv = (u * 8.0, v * 8.0)
    me = bpy.data.meshes.new("P0B4_SUPPORT_EXTENSIONS")
    bm.to_mesh(me)
    bm.free()
    if mat:
        me.materials.append(mat)
    ob = bpy.data.objects.new("P0B4_SUPPORT_EXTENSIONS", me)
    col.objects.link(ob)
    ob["fm_class"] = "SERVICE"
    ob["fm_family"] = "SUPPORT"
    return ob


def retire_old(col):
    prefixes = (
        "PROP_Z10_HVACDuct",
        "PROP_Z10_HVACFlange",
        "PROP_Z10_HVACHanger",
        "PROP_Z10_HVACSupports",
        "PROP_Z10_SVC_HVACCompletion",
        "PROP_Z10_SVC_HVACWallConnections",
        "PROP_Z10_SprinklerPipe",
        "PROP_Z10_SprinklerHead",
        "PROP_Z10_SprinklerHanger",
    )
    moved = []
    for ob in list(bpy.data.objects):
        if any(ob.name.startswith(p) for p in prefixes):
            link_only(ob, col)
            ob.hide_render = True
            ob.hide_viewport = True
            ob.hide_set(True)
            moved.append(ob.name)
    return sorted(moved)


def stats(ob):
    me = ob.data
    me.calc_loop_triangles()
    bm = bmesh.new()
    bm.from_mesh(me)
    nonman = sum(1 for e in bm.edges if len(e.link_faces) > 2)
    deg = sum(1 for f in bm.faces if f.calc_area() < 1e-10)
    bm.free()
    return {
        "tris": len(me.loop_triangles),
        "verts": len(me.vertices),
        "non_manifold_edges": nonman,
        "degenerate_faces": deg,
        "uv": bool(me.uv_layers),
    }


def world_bbox(objs):
    mn = Vector((1e9, 1e9, 1e9))
    mx = Vector((-1e9, -1e9, -1e9))
    for ob in objs:
        for v in ob.data.vertices:
            p = ob.matrix_world @ v.co
            mn.x = min(mn.x, p.x); mn.y = min(mn.y, p.y); mn.z = min(mn.z, p.z)
            mx.x = max(mx.x, p.x); mx.y = max(mx.y, p.y); mx.z = max(mx.z, p.z)
    return [round(v, 4) for v in mn], [round(v, 4) for v in mx]


def main():
    root = collection(COLL_NAME)
    ret = collection(RET_NAME)
    clear_collection(root)
    retired = retire_old(ret)

    hvac = cut_copy("P0B_HVAC_RUN_800x600", "P0B4_HVAC_RUN_800x600",
                    X_W, X_E + 0.028, DUCT_Y, root)
    hvac["fm_class"] = "SERVICE"
    hvac["fm_family"] = "HVAC"
    hvac["fm_section"] = "800x600"

    sup = cut_copy("P0B_SUPPORTS_HVAC", "P0B4_SUPPORTS_HVAC",
                   X_W, X_E, DUCT_Y, root)
    sup["fm_class"] = "SERVICE"
    sup["fm_family"] = "SUPPORT"

    spr = cut_copy("P0B_SPRINKLER_RUN_DN80", "P0B4_SPRINKLER_RUN_DN80",
                   X_W, X_E, SPR_Y, root)
    spr["fm_class"] = "SERVICE"
    spr["fm_family"] = "SPRINKLER"

    heads = cut_copy("P0B_SPRINKLER_HEADS", "P0B4_SPRINKLER_HEADS",
                     X_W, X_E, SPR_Y, root)
    heads["fm_class"] = "SERVICE"
    heads["fm_family"] = "SPRINKLER_HEAD"

    ssup = cut_copy("P0B_SUPPORTS_SPRINKLER", "P0B4_SUPPORTS_SPRINKLER",
                    X_W, X_E, SPR_Y, root)
    ssup["fm_class"] = "SERVICE"
    ssup["fm_family"] = "SUPPORT"

    add_support_extensions(root)

    # Wall sleeves: main duct (rectangular) and sprinkler (DN80)
    instance_master("SM_SH_SLEEVE_RECT_800x600", "P0B4_SLEEVE_HVAC_W",
                    root, (40.17, DUCT_Y, DUCT_Z))
    instance_master("SM_SH_SLEEVE_RECT_800x600", "P0B4_SLEEVE_HVAC_E",
                    root, (61.85, DUCT_Y, DUCT_Z))
    instance_master("SM_SH_SLEEVE_PIPE_80", "P0B4_SLEEVE_SPR_W",
                    root, (40.17, SPR_Y, SPR_Z))
    instance_master("SM_SH_SLEEVE_PIPE_80", "P0B4_SLEEVE_SPR_E",
                    root, (61.85, SPR_Y, SPR_Z))

    # Four supply diffusers under the main duct.
    for i, xx in enumerate((43.0, 48.0, 53.0, 58.0)):
        g = instance_master("SM_SH_HVAC_GRILLE_600x400",
                            "P0B4_GRILLE_%02d" % (i + 1), root,
                            (xx, DUCT_Y, 3.22), (0, math.pi / 2.0, 0))
        g["fm_class"] = "SERVICE"
        g["fm_family"] = "GRILLE"

    new_objs = [o for o in root.objects if o.type == 'MESH']
    report = {}
    total_tris = 0
    for ob in sorted(new_objs, key=lambda o: o.name):
        s = stats(ob)
        report[ob.name] = s
        total_tris += s["tris"]
    mn, mx = world_bbox(new_objs)

    out = {
        "collection": COLL_NAME,
        "retired_collection": RET_NAME,
        "retired_objects": retired,
        "objects": report,
        "object_count": len(new_objs),
        "total_tris": total_tris,
        "bbox_min": mn,
        "bbox_max": mx,
        "checks": {
            "non_manifold_total": sum(v["non_manifold_edges"] for v in report.values()),
            "degenerate_total": sum(v["degenerate_faces"] for v in report.values()),
            "uv_missing": [k for k, v in report.items() if not v["uv"]],
        },
    }
    os.makedirs(DOCS, exist_ok=True)
    with open(os.path.join(DOCS, "fm_p0b4_qa.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)

    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print("P0B4_DONE", len(new_objs), total_tris, mn, mx)
    print("RETIRED", len(retired))


main()
