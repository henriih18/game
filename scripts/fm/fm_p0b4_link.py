import bpy
import bmesh
import json
import os
from mathutils import Vector

COLL_NAME = "L1_P0B4_Z10"
DOCS = "/home/riyo/Documentos/game/docs"
X_START = 61.828
X_END = 70.0
DUCT_Y = 20.0
DUCT_Z = 3.55
SPR_Z = 3.90
CEIL_Z = 3.99


def get_collection(name):
    col = bpy.data.collections.get(name)
    if not col:
        raise RuntimeError("missing collection " + name)
    return col


def cut_copy(src_name, new_name, xmin_world, xmax_world, target_y, col):
    src = bpy.data.objects.get(src_name)
    if not src:
        raise RuntimeError("missing source " + src_name)
    ob = src.copy()
    ob.data = src.data.copy()
    ob.name = new_name
    ob.data.name = new_name
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    col.objects.link(ob)
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
    return ob


def add_riser_plates(col):
    pipes = [
        ("A", 46.27, (15.8, 16.0, 16.2)),
        ("B", 55.73, (23.8, 24.0, 24.2)),
    ]
    src = bpy.data.objects.get("PROP_Z10_RiserA_pipe_0")
    mat = src.data.materials[0] if src and src.data.materials else None
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("MapaUV")
    plate = (0.14, 0.14, 0.012)
    for rig, xx, ys in pipes:
        for zz in (0.006, CEIL_Z - 0.004):
            for yy in ys:
                ret = bmesh.ops.create_cube(bm, size=1.0)
                verts = ret["verts"]
                bmesh.ops.scale(bm, verts=verts, vec=plate)
                bmesh.ops.translate(bm, verts=verts, vec=(xx, yy, zz))
                # 4 small bolt heads on the plate corners
                for dx in (-0.052, 0.052):
                    for dy in (-0.052, 0.052):
                        r2 = bmesh.ops.create_cube(bm, size=1.0)
                        v2 = r2["verts"]
                        bmesh.ops.scale(bm, verts=v2, vec=(0.016, 0.016, 0.010))
                        bmesh.ops.translate(bm, verts=v2, vec=(xx + dx, yy + dy, zz + 0.009))
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
    me = bpy.data.meshes.new("P0B4_RISER_PASS_PLATES")
    bm.to_mesh(me)
    bm.free()
    if mat:
        me.materials.append(mat)
    ob = bpy.data.objects.new("P0B4_RISER_PASS_PLATES", me)
    col.objects.link(ob)
    ob["fm_class"] = "SERVICE"
    ob["fm_family"] = "RISER"
    return ob


def qa(ob):
    me = ob.data
    me.calc_loop_triangles()
    bm = bmesh.new()
    bm.from_mesh(me)
    nm = sum(1 for e in bm.edges if len(e.link_faces) > 2)
    deg = sum(1 for f in bm.faces if f.calc_area() < 1e-10)
    bm.free()
    return {"tris": len(me.loop_triangles), "verts": len(me.vertices),
            "non_manifold_edges": nm, "degenerate_faces": deg,
            "uv": bool(me.uv_layers)}


def main():
    col = get_collection(COLL_NAME)
    # Remove previous link-run attempt if re-run.
    for name in ("P0B4_HVAC_LINK_RUN", "P0B4_SUPPORTS_LINK",
                 "P0B4_FIREDAMPER_LINK", "P0B4_SLEEVE_LINK_E",
                 "P0B4_RISER_PASS_PLATES"):
        ob = bpy.data.objects.get(name)
        if ob:
            bpy.data.objects.remove(ob, do_unlink=True)

    run = cut_copy("P0B_HVAC_RUN_800x600", "P0B4_HVAC_LINK_RUN",
                   X_START, X_END, DUCT_Y, col)
    run["fm_class"] = "SERVICE"
    run["fm_family"] = "HVAC"

    sup = cut_copy("P0B_SUPPORTS_HVAC", "P0B4_SUPPORTS_LINK",
                   X_START, X_END, DUCT_Y, col)
    sup["fm_class"] = "SERVICE"
    sup["fm_family"] = "SUPPORT"

    fd = instance_master("SM_SH_FIREDAMPER_800x600", "P0B4_FIREDAMPER_LINK",
                         col, (69.28, DUCT_Y, DUCT_Z))
    fd["fm_family"] = "FIRE_DAMPER"

    sleeve = instance_master("SM_SH_SLEEVE_RECT_800x600", "P0B4_SLEEVE_LINK_E",
                             col, (70.0, DUCT_Y, DUCT_Z))
    sleeve["fm_family"] = "SLEEVE"

    plates = add_riser_plates(col)

    report = {}
    for ob in (run, sup, fd, sleeve, plates):
        report[ob.name] = qa(ob)
    total = sum(v["tris"] for v in report.values())
    out = {
        "collection": COLL_NAME,
        "objects": report,
        "total_tris_added": total,
        "link_run_bbox": None,
    }
    bb = [run.matrix_world @ Vector(c) for c in run.bound_box]
    out["link_run_bbox"] = [
        [round(min(p[i] for p in bb), 4) for i in range(3)],
        [round(max(p[i] for p in bb), 4) for i in range(3)],
    ]
    out["checks"] = {
        "non_manifold_total": sum(v["non_manifold_edges"] for v in report.values()),
        "degenerate_total": sum(v["degenerate_faces"] for v in report.values()),
        "uv_missing": [k for k, v in report.items() if not v["uv"]],
    }
    with open(os.path.join(DOCS, "fm_p0b4_link_qa.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print("P0B4_LINK_DONE", total, out["link_run_bbox"], out["checks"])


main()
