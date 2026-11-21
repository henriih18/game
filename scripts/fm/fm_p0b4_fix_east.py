import bpy
import bmesh
import json
import os
from mathutils import Vector

DOCS = "/home/riyo/Documentos/game/docs"
COLL_NAME = "L1_P0B4_Z10"
RET_NAME = "Z10_RETIRED_P0B4"


def coll(name):
    c = bpy.data.collections.get(name)
    if not c:
        raise RuntimeError("missing collection " + name)
    return c


def link_only(ob, col):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    col.objects.link(ob)


def mesh_stats(ob):
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
        for c in ob.bound_box:
            p = ob.matrix_world @ Vector(c)
            mn.x = min(mn.x, p.x); mn.y = min(mn.y, p.y); mn.z = min(mn.z, p.z)
            mx.x = max(mx.x, p.x); mx.y = max(mx.y, p.y); mx.z = max(mx.z, p.z)
    return [round(v, 4) for v in mn], [round(v, 4) for v in mx]


def make_cutter():
    me = bpy.data.meshes.new("P0B4_CUTTER")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("P0B4_CUTTER", me)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = (61.5, 20.0, 3.40)
    ob.scale = (1.0, 0.92, 0.42)
    ob.hide_render = True
    return ob


def cut_panel():
    ob = bpy.data.objects["PROP_Z10_SVC_EastCompletion"]
    original = ob.data.copy()
    original.name = "PROP_Z10_SVC_EastCompletion_PRE_P0B4"
    ob.data = ob.data.copy()
    ob.data.name = "PROP_Z10_SVC_EastCompletion_P0B4"
    cutter = make_cutter()
    bpy.context.view_layer.update()
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    mod = ob.modifiers.new("P0B4_HVAC_NOTCH", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    mod.object = cutter
    try:
        bpy.ops.object.modifier_apply(modifier=mod.name)
    except Exception as exc:
        print("BOOLEAN_FAIL", repr(exc))
        ob.data = original
        bpy.data.objects.remove(cutter, do_unlink=True)
        return ob, original, False
    bpy.data.objects.remove(cutter, do_unlink=True)
    bpy.context.view_layer.update()
    s = mesh_stats(ob)
    print("PANEL_AFTER", s)
    if s["non_manifold_edges"] > 0 or s["degenerate_faces"] > 0:
        print("PANEL_REVERT")
        ob.data = original
        bpy.context.view_layer.update()
        return ob, original, False
    return ob, original, True


def duplicate_mesh_obj(src_name, new_name, loc, scale, col):
    src = bpy.data.objects[src_name]
    ob = src.copy()
    ob.name = new_name
    col.objects.link(ob)
    ob.location = loc
    ob.scale = scale
    ob.hide_render = False
    ob.hide_viewport = False
    ob.hide_set(False)
    return ob


def main():
    root = coll(COLL_NAME)
    ret = coll(RET_NAME)

    panel, panel_orig, panel_ok = cut_panel()

    # Close the east conduit over the door with the detailed 2 m tube, scaled to 6 m.
    conduit = duplicate_mesh_obj(
        "KIT_PILOT_Z10_Conduit_02", "P0B4_CONDUIT_E_DOOR",
        (61.78, 21.0, 3.15), (1.0, 3.0, 1.0), root)
    conduit["fm_class"] = "SERVICE"
    conduit["fm_family"] = "CONDUIT"
    conduit["fm_note"] = "6 m section over east door, shared mesh with KIT_PILOT_Z10_Conduit_02"

    for i, yy in enumerate((19.5, 22.5)):
        cl = duplicate_mesh_obj(
            "KIT_PILOT_Z10_ConduitClamp_02",
            "P0B4_CONDUIT_CLAMP_%02d" % (i + 1),
            (61.78, yy, 3.15), (1.0, 1.0, 1.0), root)

    # Retire orphan wall sleeves (no pipe passes through them).
    retired_sleeves = []
    for n in ("KIT_PILOT_Z10_Sleeve_00", "KIT_PILOT_Z10_Sleeve_01"):
        ob = bpy.data.objects.get(n)
        if ob:
            link_only(ob, ret)
            ob.hide_render = True
            ob.hide_viewport = True
            ob.hide_set(True)
            retired_sleeves.append(n)

    bpy.context.view_layer.update()
    new_objs = [o for o in root.objects if o.type == "MESH"]
    report = {}
    for ob in sorted(new_objs, key=lambda o: o.name):
        report[ob.name] = mesh_stats(ob)
    mn, mx = world_bbox(new_objs)

    out = {
        "panel": panel.name,
        "panel_cut_ok": panel_ok,
        "panel_stats": mesh_stats(panel),
        "retired_sleeves": retired_sleeves,
        "objects": report,
        "object_count": len(new_objs),
        "total_tris": sum(v["tris"] for v in report.values()),
        "bbox_min": mn,
        "bbox_max": mx,
        "checks": {
            "non_manifold_total": sum(v["non_manifold_edges"] for v in report.values()),
            "degenerate_total": sum(v["degenerate_faces"] for v in report.values()),
            "uv_missing": [k for k, v in report.items() if not v["uv"]],
        },
    }
    with open(os.path.join(DOCS, "fm_p0b4_fix_qa.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)

    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print("P0B4_FIX_DONE", len(new_objs), out["total_tris"], mn, mx, "panel_ok", panel_ok)
    print("RETIRED_SLEEVES", retired_sleeves)


main()
