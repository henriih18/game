import bpy
import bmesh
import json
import os
import shutil
import sys
from mathutils import Vector, Matrix

sys.path.insert(0, "/home/riyo/Documentos/game/scripts/fm")
from fm_shared_p0_lib import ensure_materials, box, cyl, join_group

ROOT = "/home/riyo/Documentos/game"
BLEND = os.path.join(ROOT, "nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend")
BACKUP = os.path.join(ROOT, "docs/backups/FM_LEVEL1_V06_ARCH_before_security_p0a_portals.blend")
QA = os.path.join(ROOT, "docs/fm_security_p0a_portals_qa.json")
COL_NAME = "L1_SECURITY_P0A_HERO"

M = ensure_materials()
FRAME = M["steel_dark"]
GALV = M["galv"]
ORANGE = M["paint_orange"]
SEAL = M["plastic"]
BARE = M["steel_bare"]

POST_W = 0.41
DEPTH = 0.46
HEADER_H = 0.24
COVER = 0.01

_ACTIVE_COL = None


def B(parts, *args, **kwargs):
    ob = box(_ACTIVE_COL, *args, **kwargs)
    parts.append(ob)
    return ob


def C(parts, *args, **kwargs):
    ob = cyl(_ACTIVE_COL, *args, **kwargs)
    parts.append(ob)
    return ob



def bbox_world(ob):
    pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    return [[round(min(p[i] for p in pts), 4) for i in range(3)],
            [round(max(p[i] for p in pts), 4) for i in range(3)]]


def mesh_qa(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    non_manifold = sum(1 for e in bm.edges if not e.is_manifold)
    degenerate = 0
    for f in bm.faces:
        if f.calc_area() < 1e-9:
            degenerate += 1
    bm.free()
    uv = len(ob.data.uv_layers) > 0
    return {
        "tris": sum(len(p.vertices) - 2 for p in ob.data.polygons),
        "verts": len(ob.data.vertices),
        "polys": len(ob.data.polygons),
        "non_manifold": non_manifold,
        "degenerate": degenerate,
        "uv": uv,
    }


def add_post(parts, tag, x_center, y, height, side):
    # Post boxes are deliberately 10 mm wider/taller than the old trim so
    # the old 12-triangle jamb is enclosed without coplanar faces.
    h = height + COVER
    B(parts, tag + "_POST", POST_W, DEPTH, h,
        (x_center, y, h * 0.5), FRAME, bevel=0.0025, seg=3)
    # Recessed access panel on both faces.
    for face, yy in (("F", y - DEPTH * 0.5 - 0.001), ("B", y + DEPTH * 0.5 + 0.001)):
        B(parts, tag + "_PANEL_" + face, POST_W - 0.11, 0.018, h - 0.34,
            (x_center, yy, h * 0.52), BARE, bevel=0.0012, seg=2)
        for i in range(3):
            z = 0.28 + i * (h - 0.62) / 2.0
            B(parts, tag + "_BAND_%s_%d" % (face, i), POST_W - 0.15, 0.024, 0.028,
                (x_center, yy, z), FRAME, bevel=0.001, seg=1)
        for i in range(4):
            z = 0.16 + i * (h - 0.32) / 3.0
            C(parts, tag + "_RIVET_%s_%d" % (face, i), 0.0105, 0.012,
                (x_center + (-0.14 if side == "L" else 0.14), yy, z),
                GALV, axis='Y', seg=8, bevel=0.0004, bseg=1)
    # Anchor plate and bolts.
    B(parts, tag + "_PLATE", POST_W + 0.10, DEPTH + 0.08, 0.026,
        (x_center, y, 0.013), GALV, bevel=0.0015, seg=2)
    for dx in (-0.14, 0.14):
        for dy in (-0.16, 0.16):
            C(parts, tag + "_ANCHOR_%s_%s" % (dx, dy), 0.012, 0.026,
                (x_center + dx, y + dy, 0.029), BARE, axis='Z', seg=8,
                bevel=0.0003, bseg=1)
    # Rubber seal on the inner edge.
    inner_x = x_center + (POST_W * 0.5) * (1 if side == "L" else -1)
    B(parts, tag + "_SEAL", 0.022, 0.05, h - 0.06,
        (inner_x, y, h * 0.5), SEAL, bevel=0.001, seg=1)


def add_header(parts, tag, x0, x1, y, height):
    width = x1 - x0
    zc = height - COVER + HEADER_H * 0.5
    B(parts, tag + "_HEADER", width, DEPTH, HEADER_H,
        ((x0 + x1) * 0.5, y, zc), FRAME, bevel=0.0025, seg=3)
    for face, yy in (("F", y - DEPTH * 0.5 - 0.001), ("B", y + DEPTH * 0.5 + 0.001)):
        B(parts, tag + "_HEADER_PANEL_" + face, width - 0.16, 0.018, HEADER_H - 0.08,
            ((x0 + x1) * 0.5, yy, zc), BARE, bevel=0.0012, seg=2)
        B(parts, tag + "_HEADER_STRIPE_" + face, min(width - 0.35, 1.4), 0.022, 0.075,
            ((x0 + x1) * 0.5, yy, zc), ORANGE, bevel=0.001, seg=1)
        for i in range(4):
            x = x0 + 0.18 + i * (width - 0.36) / 3.0
            C(parts, tag + "_HEADER_BOLT_%s_%d" % (face, i), 0.012, 0.014,
                (x, yy, zc + 0.055), GALV, axis='Y', seg=8,
                bevel=0.0004, bseg=1)
    # Top cap.
    B(parts, tag + "_CAP", width + 0.04, DEPTH + 0.04, 0.025,
        ((x0 + x1) * 0.5, y, height + HEADER_H - COVER + 0.0125),
        GALV, bevel=0.0015, seg=2)


def add_threshold(parts, tag, x0, x1, y):
    width = x1 - x0
    B(parts, tag + "_THRESHOLD", width, DEPTH, 0.025,
        ((x0 + x1) * 0.5, y, 0.0125), GALV, bevel=0.0015, seg=2)
    for i in range(6):
        x = x0 + 0.20 + i * (width - 0.40) / 5.0
        C(parts, tag + "_THRESHOLD_BOLT_%d" % i, 0.010, 0.012,
            (x, y, 0.027), BARE, axis='Z', seg=8, bevel=0.0003, bseg=1)


def build_portal(col, name, x_left, x_right, y, height):
    global _ACTIVE_COL
    _ACTIVE_COL = col
    for ob in list(col.objects):
        if ob.name == name:
            bpy.data.objects.remove(ob, do_unlink=True)
    parts = []
    # New posts enclose the old 0.16 m jambs and overlap the opening 1 cm.
    left_center = x_left - POST_W * 0.5
    right_center = x_right + POST_W * 0.5
    add_post(parts, name + "_L", left_center, y, height, "L")
    add_post(parts, name + "_R", right_center, y, height, "R")
    add_header(parts, name, left_center - POST_W * 0.5, right_center + POST_W * 0.5, y, height)
    add_threshold(parts, name, x_left, x_right, y)
    joined = join_group(col, name, parts, uv=True, wn=True)
    if joined is None:
        raise RuntimeError("join failed " + name)
    joined["fm_class"] = "PORTAL_FRAME"
    joined["fm_family"] = "SECURITY_P0A_PORTAL"
    joined["fm_generation"] = "VERIFIED_SECURITY_P0A_PORTALS"
    joined["fm_clear_w"] = round(x_right - x_left, 3)
    joined["fm_clear_h"] = round(height, 3)
    joined["fm_source_master"] = "SM_SH_PORTAL_* adapted"
    return joined


def main():
    if not os.path.exists(BACKUP):
        shutil.copy2(BLEND, BACKUP)
        print("BACKUP", BACKUP)
    col = bpy.data.collections.get(COL_NAME)
    if col is None:
        col = bpy.data.collections.new(COL_NAME)
        bpy.context.scene.collection.children.link(col)
    bpy.context.view_layer.objects.active = None
    s = build_portal(col, "SEC_P0A_PORTAL_S", -91.84, -86.16, 10.0, 3.04)
    n = build_portal(col, "SEC_P0A_PORTAL_N", -95.84, -92.16, 36.0, 2.44)
    bpy.context.view_layer.update()
    rows = []
    for ob in (s, n):
        q = mesh_qa(ob)
        q["name"] = ob.name
        q["bbox"] = bbox_world(ob)
        q["dims"] = [round(v, 3) for v in ob.dimensions]
        rows.append(q)
    old = []
    for namp in ("SM_L1_Zone03_Security_Door_S_L", "SM_L1_Zone03_Security_Door_S_R",
                 "SM_L1_Zone03_Security_Door_S_T", "SM_L1_Zone03_Security_Door_N_L",
                 "SM_L1_Zone03_Security_Door_N_R", "SM_L1_Zone03_Security_Door_N_T"):
        ob = bpy.data.objects.get(namp)
        if ob:
            old.append({"name": namp, "hide_render": bool(ob.hide_render),
                        "bbox": bbox_world(ob)})
    report = {
        "batch": "SECURITY_P0A_PORTALS",
        "objects": rows,
        "old_trim_kept": old,
        "collection": COL_NAME,
        "note": "Old 12-tri jamb/header trim remains behind the new posts/header, enclosed with 10 mm overlap; architecture untouched.",
    }
    with open(QA, "w") as fh:
        json.dump(report, fh, indent=2)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("SEC_P0A_PORTALS_DONE")
    print(json.dumps(report, indent=2))


main()
