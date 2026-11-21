import bpy
import bmesh
import json
import math
import os
from mathutils import Vector

import sys
sys.path.insert(0, "/home/riyo/Documentos/game/scripts/fm")
from fm_shared_p0_lib import ensure_materials, box, cyl, join_group

COLL = "L1_P0B4_Z10"
RET = "Z10_RETIRED_P0B4"
DOCS = "/home/riyo/Documentos/game/docs"

WEST_X = 40.42
WEST_Y0, WEST_Y1, WEST_Z = 4.67, 34.93, 3.02
EAST_X = 61.68
EAST_Y0, EAST_Y1, EAST_Z = 8.0, 30.0, 3.54
W, H = 0.40, 0.10
SEG = 2.40
RUNG_SP = 0.30
BRACKET_SP = 3.00

M = ensure_materials()
GALV = M["galv"]
DARK = M["steel_dark"]
BARE = M["steel_bare"]
RED = M["sprink_red"]
RUB = M["rubber"]


def link_only(ob, col):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    col.objects.link(ob)


def cable_orange():
    mat = bpy.data.materials.get("M_P0B4_CABLE_ORANGE")
    if mat:
        bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        bsdf.inputs['Base Color'].default_value = (0.62, 0.22, 0.03, 1.0)
        return mat
    mat = bpy.data.materials.new("M_P0B4_CABLE_ORANGE")
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = (0.62, 0.22, 0.03, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.62
    bsdf.inputs['Metallic'].default_value = 0.0
    return mat


ORANGE = cable_orange()


def build_tray(col, name, x, y0, y1, z, wall_x):
    parts = []
    n = [0]

    def B(sx, sy, sz, center, mat, bev=0.001, seg=2):
        n[0] += 1
        ob = box(col, "%s_P%04d" % (name, n[0]), sx, sy, sz, center, mat, bev, seg)
        parts.append(ob)
        return ob

    # Segment rails with top/bottom return flanges.
    y = y0
    first = True
    while y < y1 - 1e-6:
        ln = min(SEG, y1 - y)
        cy = y + ln / 2.0
        for s in (-1, 1):
            rx = x + s * (W / 2.0 + 0.01)
            B(0.020, ln, H, (rx, cy, z), GALV, 0.0015, 2)
            B(0.030, ln, 0.020, (rx - s * 0.015, cy, z + H / 2 - 0.010), GALV, 0.001, 2)
            B(0.030, ln, 0.020, (rx - s * 0.015, cy, z - H / 2 + 0.010), GALV, 0.001, 2)
        if not first:
            # Splice plates and bolts at each joint.
            for s in (-1, 1):
                px = x + s * (W / 2.0 + 0.021)
                B(0.012, 0.16, 0.14, (px, y, z), GALV, 0.001, 2)
                for dz in (-0.045, 0.045):
                    for dy in (-0.052, 0.052):
                        parts.append(cyl(col, "%s_BOLT_%04d" % (name, n[0]),
                                         0.006, 0.016, (px + s * 0.012, y + dy, z + dz),
                                         BARE, axis='X', seg=8, bevel=0.0004, bseg=1))
                        n[0] += 1
        first = False
        y += ln

    # Rungs.
    yy = y0 + 0.15
    while yy < y1 - 1e-6:
        B(W - 0.04, 0.030, 0.012, (x, yy, z - H / 2 + 0.020), GALV, 0.0008, 2)
        for s in (-1, 1):
            B(0.018, 0.050, 0.030, (x + s * (W / 2 - 0.02), yy, z - H / 2 + 0.020),
              BARE, 0.0008, 1)
        yy += RUNG_SP

    # Cantilever wall brackets.
    yy = y0 + 1.5
    side = 1.0 if wall_x < x else -1.0
    while yy < y1 - 0.2:
        wp_x = wall_x + side * 0.011
        B(0.024, 0.22, 0.30, (wp_x, yy, z - 0.17), DARK, 0.0015, 2)
        arm_len = abs(x - wall_x) + 0.04
        B(arm_len, 0.060, 0.055, ((x + wall_x) / 2.0, yy, z - 0.070),
          DARK, 0.0015, 2)
        p0 = Vector((wall_x + side * 0.02, yy, z - 0.275))
        p1 = Vector((x - side * 0.05, yy, z - 0.075))
        v = p1 - p0
        ob = cyl(col, "%s_STRUT_%04d" % (name, n[0]), 0.016, v.length,
                 (0, 0, 0), DARK, axis='Z', seg=8, bevel=0.0005, bseg=1)
        ob.location = (p0 + p1) / 2.0
        ob.rotation_euler = v.to_track_quat('Z', 'Y').to_euler()
        parts.append(ob)
        n[0] += 1
        for dz in (-0.080, 0.080):
            for dy in (-0.060, 0.060):
                parts.append(cyl(col, "%s_WBOLT_%04d" % (name, n[0]),
                                 0.007, 0.030, (wp_x + side * 0.016, yy + dy, z - 0.17 + dz),
                                 BARE, axis='X', seg=8, bevel=0.0004, bseg=1))
                n[0] += 1
        yy += BRACKET_SP

    # End caps.
    for ey in (y0, y1):
        B(W + 0.04, 0.018, H + 0.02, (x, ey, z), DARK, 0.001, 2)

    # Cable bundles.
    for ox, r, mat in ((-0.110, 0.028, RUB), (0.0, 0.024, ORANGE), (0.110, 0.020, RUB)):
        parts.append(cyl(col, "%s_CABLE_%04d" % (name, n[0]), r, y1 - y0,
                         (x + ox, (y0 + y1) / 2.0, z + 0.010), mat,
                         axis='Y', seg=10, bevel=0.0004, bseg=1))
        n[0] += 1
    yy = y0 + 0.30
    while yy < y1:
        B(W - 0.06, 0.018, 0.080, (x, yy, z + 0.010), RUB, 0.0005, 1)
        yy += 0.60

    ob = join_group(col, name, parts, uv=True, wn=True)
    ob["fm_class"] = "SERVICE"
    ob["fm_family"] = "CABLE_TRAY"
    ob["fm_section"] = "400x100"
    return ob


def add_west_sleeves(col):
    parts = []
    for yy in (8.0, 30.0):
        for dz in (-0.10, 0.10):
            parts.append(box(col, "P0B4_TRAY_SLV_%s_%s" % (yy, dz),
                             0.50, 0.24, 0.020, (WEST_X, yy, WEST_Z + dz),
                             GALV, 0.0015, 2))
        for dx in (-0.24, 0.24):
            parts.append(box(col, "P0B4_TRAY_SLV_%s_%s" % (yy, dx),
                             0.020, 0.24, 0.20, (WEST_X + dx, yy, WEST_Z),
                             GALV, 0.0015, 2))
        # Intumescent strips around the opening, not a solid pad.
        for dz in (-0.080, 0.080):
            parts.append(box(col, "P0B4_TRAY_FS_%s_%s" % (yy, dz),
                             0.44, 0.018, 0.018, (WEST_X, yy + 0.12, WEST_Z + dz),
                             RED, 0.0005, 1))
        for dx in (-0.210, 0.210):
            parts.append(box(col, "P0B4_TRAY_FS_%s_%s" % (yy, dx),
                             0.018, 0.018, 0.16, (WEST_X + dx, yy + 0.12, WEST_Z),
                             RED, 0.0005, 1))
    ob = join_group(col, "P0B4_TRAY_SLEEVES", parts, uv=True, wn=True)
    ob["fm_class"] = "SERVICE"
    ob["fm_family"] = "SLEEVE"
    return ob


def retire(col):
    prefixes = (
        "PROP_Z10_WestTray",
        "PROP_Z10_SVC_WestTrayCables",
        "KIT_PILOT_Z10_Tray_",
        "KIT_PILOT_Z10_TrayBracket_",
    )
    moved = []
    for ob in list(bpy.data.objects):
        if any(ob.name == p or ob.name.startswith(p) for p in prefixes):
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
    return {"tris": len(me.loop_triangles), "verts": len(me.vertices),
            "non_manifold_edges": nonman, "degenerate_faces": deg,
            "uv": bool(me.uv_layers)}


def main():
    root = bpy.data.collections.get(COLL)
    if not root:
        raise RuntimeError("missing collection " + COLL)
    # Idempotent rebuild: remove previous tray objects (including .001 duplicates).
    for ob in list(root.objects):
        if ob.name.startswith("P0B4_TRAY_"):
            bpy.data.objects.remove(ob, do_unlink=True)
    for dup in ("P0B4_SUPPORTS_LINK.001", "P0B4_SUPPORTS_SPRINKLER.001"):
        ob = bpy.data.objects.get(dup)
        if ob and bpy.data.objects.get(dup[:-4]):
            bpy.data.objects.remove(ob, do_unlink=True)
    ret = bpy.data.collections.get(RET)
    if not ret:
        ret = bpy.data.collections.new(RET)
        bpy.context.scene.collection.children.link(ret)
    retired = retire(ret)

    west = build_tray(root, "P0B4_TRAY_WEST", WEST_X, WEST_Y0, WEST_Y1, WEST_Z, 40.0)
    east = build_tray(root, "P0B4_TRAY_EAST", EAST_X, EAST_Y0, EAST_Y1, EAST_Z, 62.0)
    slv = add_west_sleeves(root)

    bpy.context.view_layer.update()
    new = [west, east, slv]
    report = {}
    total = 0
    for ob in new:
        s = stats(ob)
        report[ob.name] = s
        total += s["tris"]
    out = {
        "collection": COLL,
        "objects": report,
        "total_tris_added": total,
        "retired": retired,
        "checks": {
            "non_manifold_total": sum(v["non_manifold_edges"] for v in report.values()),
            "degenerate_total": sum(v["degenerate_faces"] for v in report.values()),
            "uv_missing": [k for k, v in report.items() if not v["uv"]],
        },
    }
    os.makedirs(DOCS, exist_ok=True)
    with open(os.path.join(DOCS, "fm_p0b4_tray_qa.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)

    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print("P0B4_TRAY_DONE", len(new), total, retired)


main()
