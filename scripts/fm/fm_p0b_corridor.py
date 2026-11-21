"""FRECUENCIA MUERTA - P0b.1 corridor service spine + Z10 branch.

Builds one continuous HVAC 800x600 run, one 400x100 cable tray and one
DN80 sprinkler main from x=-99 to x=73.5, plus a branch to the existing
Z10 duct at x=43. Optimised run geometry (not repeated 10k hero modules).

Run through the live Blender socket:
    python3 /tmp/opencode/bpy_run.py scripts/fm/fm_p0b_corridor.py
"""
import bpy
import bmesh
import json
import math
import os
import shutil
import sys
import time
from mathutils import Vector, Matrix

sys.path.insert(0, "/home/riyo/Documentos/game/scripts/fm")

from fm_shared_p0_lib import (ensure_materials, make_part, box, cyl, join_group,
                              smart_uv, tri_count, _select_only, bm_box, bm_cyl,
                              bm_rect_tube_x, bm_rect_frame_x, bm_pipe_x)

M = ensure_materials()
GALV = M["galv"]
DARK = M["steel_dark"]
BARE = M["steel_bare"]
RED = M["sprink_red"]
LABEL = M["label"]
RUB = M["rubber"]

BLEND = "/home/riyo/Documentos/game/nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend"
BACKUP = "/home/riyo/Documentos/game/docs/backups/FM_LEVEL1_V06_ARCH_before_p0b1.blend"
COLL_NAME = "L1_P0B_SERVICES"
QA_PATH = "/home/riyo/Documentos/game/docs/fm_p0b_qa.json"

X0, X1 = -99.0, 73.8
DUCT_Y, DUCT_Z, DUCT_W, DUCT_H = -2.0, 3.55, 0.8, 0.6
TRAY_Y, TRAY_Z = 0.2, 3.20
SPR_Y, SPR_Z = 2.4, 3.90
SEG = 2.4
CEIL_Z = 3.99


def clear_coll():
    coll = bpy.data.collections.get(COLL_NAME)
    if coll is None:
        coll = bpy.data.collections.new(COLL_NAME)
        bpy.context.scene.collection.children.link(coll)
    else:
        for ob in list(coll.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        for ch in list(coll.children):
            bpy.data.collections.remove(ch)
    coll.hide_viewport = False
    coll.hide_render = False
    return coll


def link(ob, coll):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    coll.objects.link(ob)
    return ob


def proto(coll, name, parts, uv=True):
    ob = join_group(coll, name, parts, uv=uv, wn=False)
    return ob


def instanced_run(coll, proto_ob, count, step, start, rot_z=0.0):
    """Duplicate the prototype as linked meshes and join them into one object."""
    objs = []
    for i in range(count):
        ob = proto_ob.copy()          # linked mesh data
        ob.data = proto_ob.data
        ob.name = "%s_%03d" % (proto_ob.name, i)
        coll.objects.link(ob)
        ob.location = start
        ob.rotation_euler = (0.0, 0.0, rot_z)
        objs.append(ob)
        start = (start[0] + step, start[1], start[2]) if rot_z == 0.0 else \
               (start[0], start[1] + step, start[2])
    _select_only(objs[0])
    for ob in objs:
        ob.select_set(True)
    bpy.ops.object.join()
    final = bpy.context.view_layer.objects.active
    final.name = proto_ob.name
    final.data.name = proto_ob.name + "_MESH"
    for c in list(proto_ob.users_collection):
        c.objects.unlink(proto_ob)
    bpy.data.objects.remove(proto_ob, do_unlink=True)
    return final


# ---------------------------------------------------------------------------
# duct segment
# ---------------------------------------------------------------------------

def duct_segment(coll, name):
    L, w, h = SEG, DUCT_W, DUCT_H
    parts = []
    parts.append(make_part(name + "_Body",
                           bm_rect_tube_x(0.0, L, w, h, 0.004),
                           GALV, coll, 0.0012, 1))
    # one flange per joint (x=0); the next segment supplies the following flange
    parts.append(make_part(name + "_Flange",
                           bm_rect_frame_x(0.0, 0.028, w + 0.06, h + 0.06,
                                           w - 0.004, h - 0.004),
                           GALV, coll, 0.0012, 2))
    # four corner bolt heads, shallow
    for i, (yy, zz) in enumerate(((-w / 2, -h / 2), (w / 2, -h / 2),
                                  (w / 2, h / 2), (-w / 2, h / 2))):
        parts.append(cyl(coll, "%s_B%02d" % (name, i), 0.0075, 0.005,
                         (0.030, yy, zz), DARK, 'X', 6, 0.0004, 1))
    # cross-break ribs, one pair per segment
    for i, xx in enumerate((L * 0.32, L * 0.66)):
        parts.append(box(coll, "%s_RT%02d" % (name, i), 0.012, w + 0.012, 0.006,
                         (xx, 0, h / 2 + 0.003), GALV, 0.001, 1))
        parts.append(box(coll, "%s_RB%02d" % (name, i), 0.012, w + 0.012, 0.006,
                         (xx, 0, -h / 2 - 0.003), GALV, 0.001, 1))
    # longitudinal lock seam on the bottom edge
    parts.append(box(coll, name + "_Seam", L, 0.010, 0.008,
                     (L / 2, -w / 2 + 0.006, -h / 2 - 0.004), GALV, 0.001, 1))
    # top cleats for hangers
    for xx in (L * 0.25, L * 0.75):
        parts.append(box(coll, "%s_C%02d" % (name, int(xx * 100)), 0.06, 0.16, 0.025,
                         (xx, 0, h / 2 + 0.012), DARK, 0.0015, 1))
    return proto(coll, name, parts)


# ---------------------------------------------------------------------------
# tray segment
# ---------------------------------------------------------------------------

def tray_segment(coll, name):
    L, w, h = SEG, 0.4, 0.1
    parts = []
    # side rails (L profile) built as two thin vertical + bottom lips
    for s in (-1, 1):
        y = s * (w / 2 - 0.015)
        parts.append(box(coll, "%s_Rail%+d" % (name, s), L, 0.03, h,
                         (L / 2, y, 0), GALV, 0.001, 1))
        parts.append(box(coll, "%s_Lip%+d" % (name, s), L, 0.04, 0.008,
                         (L / 2, y - s * 0.025, -h / 2 + 0.004), GALV, 0.0008, 1))
    # rungs
    for i in range(8):
        xx = 0.12 + i * (L - 0.24) / 7.0
        parts.append(box(coll, "%s_R%02d" % (name, i), 0.022, w - 0.05, 0.008,
                         (xx, 0, -h / 2 + 0.006), BARE, 0.0006, 1))
    # splice plate at x=0
    parts.append(box(coll, name + "_Splice", 0.10, w + 0.02, 0.004,
                     (0.02, 0, -h / 2 - 0.004), BARE, 0.0008, 1))
    return proto(coll, name, parts)


# ---------------------------------------------------------------------------
# sprinkler segment
# ---------------------------------------------------------------------------

def sprinkler_segment(coll, name):
    L = SEG
    parts = []
    parts.append(make_part(name + "_Pipe",
                           bm_pipe_x(0.0, L, 0.0525, 0.0445, 0, 0, 12),
                           RED, coll, 0.0006, 1))
    # coupling
    parts.append(cyl(coll, name + "_Cpl", 0.062, 0.09, (0.045, 0, 0),
                     DARK, 'X', 12, 0.0006, 1))
    # hanger cleat
    parts.append(box(coll, name + "_Cleat", 0.05, 0.10, 0.02,
                     (L * 0.5, 0, 0.058), DARK, 0.001, 1))
    return proto(coll, name, parts)


# ---------------------------------------------------------------------------
# supports
# ---------------------------------------------------------------------------

def duct_support(coll, name):
    parts = []
    for s in (-1, 1):
        parts.append(cyl(coll, "%s_R%+d" % (name, s), 0.008, CEIL_Z - 3.12,
                         (0, s * 0.46, (CEIL_Z + 3.12) / 2), BARE, 'Z', 8))
    parts.append(box(coll, name + "_Bar", 0.04, 1.02, 0.04, (0, 0, 3.12), DARK, 0.001, 1))
    for s in (-1, 1):
        parts.append(box(coll, "%s_Pad%+d" % (name, s), 0.08, 0.05, 0.02,
                         (0, s * 0.30, 3.145), RUB, 0.0008, 1))
    return proto(coll, name, parts)


def tray_support(coll, name):
    parts = []
    for s in (-1, 1):
        parts.append(cyl(coll, "%s_R%+d" % (name, s), 0.007, CEIL_Z - 3.13,
                         (0, s * 0.20, (CEIL_Z + 3.13) / 2), BARE, 'Z', 8))
    parts.append(box(coll, name + "_Bar", 0.04, 0.50, 0.035, (0, 0, 3.13), DARK, 0.001, 1))
    return proto(coll, name, parts)


def sprinkler_support(coll, name):
    parts = [cyl(coll, name + "_Rod", 0.006, CEIL_Z - 3.90,
                 (0, 0, (CEIL_Z + 3.90) / 2), BARE, 'Z', 8)]
    # split ring around the pipe (two half boxes, cheap and readable)
    for s in (-1, 1):
        parts.append(box(coll, "%s_Clamp%+d" % (name, s), 0.035, 0.06, 0.09,
                         (0, s * 0.052, 3.90), DARK, 0.001, 1))
    return proto(coll, name, parts)


# ---------------------------------------------------------------------------
# sprinkler head (simplified but readable at corridor distance)
# ---------------------------------------------------------------------------

def sprinkler_head(coll, name):
    parts = []
    parts.append(cyl(coll, name + "_Drop", 0.011, 0.66, (0, 0, 3.57), RED, 'Z', 8))
    parts.append(cyl(coll, name + "_Body", 0.018, 0.05, (0, 0, 3.22), BARE, 'Z', 8))
    parts.append(cyl(coll, name + "_Def", 0.043, 0.008, (0, 0, 3.18), BARE, 'Z', 12))
    parts.append(cyl(coll, name + "_Bulb", 0.008, 0.025, (0, 0, 3.20), RED, 'Z', 8))
    return proto(coll, name, parts)


# ---------------------------------------------------------------------------
# collar / blind flange
# ---------------------------------------------------------------------------

def rect_collar(coll, name, w, h, depth=0.05):
    parts = [make_part(name + "_F", bm_rect_frame_x(0, depth, w + 0.10, h + 0.10,
                                                    w, h), GALV, coll, 0.0012, 2)]
    for i, (yy, zz) in enumerate(((-w / 2, -h / 2), (w / 2, -h / 2),
                                  (w / 2, h / 2), (-w / 2, h / 2))):
        parts.append(cyl(coll, "%s_B%02d" % (name, i), 0.0075, 0.006,
                         (depth, yy, zz), DARK, 'X', 6, 0.0004, 1))
    return proto(coll, name, parts)


def blind_plate(coll, name, w, h):
    parts = [box(coll, name + "_P", 0.012, w, h, (0, 0, 0), GALV, 0.0012, 1)]
    for i, (yy, zz) in enumerate(((-w / 2 + 0.06, -h / 2 + 0.06),
                                  (w / 2 - 0.06, -h / 2 + 0.06),
                                  (w / 2 - 0.06, h / 2 - 0.06),
                                  (-w / 2 + 0.06, h / 2 - 0.06))):
        parts.append(cyl(coll, "%s_B%02d" % (name, i), 0.007, 0.006,
                         (0.012, yy, zz), DARK, 'X', 6, 0.0004, 1))
    return proto(coll, name, parts)


def label_plate(coll, name):
    parts = [box(coll, name + "_L", 0.16, 0.002, 0.05, (0, 0, 0), LABEL, 0.0004, 1)]
    for s in (-1, 1):
        parts.append(cyl(coll, "%s_S%+d" % (name, s), 0.0025, 0.002,
                         (s * 0.06, 0.002, 0), BARE, 'Y', 6, 0.0002, 1))
    return proto(coll, name, parts)


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------

def main():
    t0 = time.time()
    coll = clear_coll()

    n = int(round((X1 - X0) / SEG))
    # duct
    dp = duct_segment(coll, "P0B_HVAC_SEG")
    duct = instanced_run(coll, dp, n, SEG, (X0, DUCT_Y, DUCT_Z))
    duct.name = "P0B_HVAC_RUN_800x600"
    duct.data.name = duct.name

    # tray
    tp = tray_segment(coll, "P0B_TRAY_SEG")
    tray = instanced_run(coll, tp, n, SEG, (X0, TRAY_Y, TRAY_Z))
    tray.name = "P0B_TRAY_RUN_400"
    tray.data.name = tray.name

    # sprinkler
    sp = sprinkler_segment(coll, "P0B_SPR_SEG")
    spr = instanced_run(coll, sp, n, SEG, (X0, SPR_Y, SPR_Z))
    spr.name = "P0B_SPRINKLER_RUN_DN80"
    spr.data.name = spr.name

    # supports
    dsup = duct_support(coll, "P0B_SUP_DUCT")
    dsup_objs = []
    for i, xx in enumerate([X0 + 2.4 + k * 4.8 for k in range(int((X1 - X0 - 4.8) / 4.8) + 1)]):
        ob = dsup.copy(); ob.data = dsup.data; ob.name = "P0B_SUP_DUCT_%02d" % i
        coll.objects.link(ob); ob.location = (xx, DUCT_Y, 0); dsup_objs.append(ob)
    _select_only(dsup_objs[0])
    for ob in dsup_objs: ob.select_set(True)
    bpy.ops.object.join(); dsup_final = bpy.context.view_layer.objects.active
    dsup_final.name = "P0B_SUPPORTS_HVAC"
    bpy.data.objects.remove(dsup, do_unlink=True)

    tsup = tray_support(coll, "P0B_SUP_TRAY")
    tsup_objs = []
    for i, xx in enumerate([X0 + 1.5 + k * 3.0 for k in range(int((X1 - X0 - 3.0) / 3.0) + 1)]):
        ob = tsup.copy(); ob.data = tsup.data; ob.name = "P0B_SUP_TRAY_%02d" % i
        coll.objects.link(ob); ob.location = (xx, TRAY_Y, 0); tsup_objs.append(ob)
    _select_only(tsup_objs[0])
    for ob in tsup_objs: ob.select_set(True)
    bpy.ops.object.join(); tsup_final = bpy.context.view_layer.objects.active
    tsup_final.name = "P0B_SUPPORTS_TRAY"
    bpy.data.objects.remove(tsup, do_unlink=True)

    ss = sprinkler_support(coll, "P0B_SUP_SPR")
    ss_objs = []
    for i, xx in enumerate([X0 + 2.0 + k * 4.0 for k in range(int((X1 - X0 - 4.0) / 4.0) + 1)]):
        ob = ss.copy(); ob.data = ss.data; ob.name = "P0B_SUP_SPR_%02d" % i
        coll.objects.link(ob); ob.location = (xx, SPR_Y, 0); ss_objs.append(ob)
    _select_only(ss_objs[0])
    for ob in ss_objs: ob.select_set(True)
    bpy.ops.object.join(); ss_final = bpy.context.view_layer.objects.active
    ss_final.name = "P0B_SUPPORTS_SPRINKLER"
    bpy.data.objects.remove(ss, do_unlink=True)

    # heads
    hp = sprinkler_head(coll, "P0B_SPR_HEAD_PROTO")
    h_objs = []
    for i, xx in enumerate([X0 + 2.0 + k * 4.0 for k in range(int((X1 - X0 - 3.0) / 4.0) + 1)]):
        ob = hp.copy(); ob.data = hp.data; ob.name = "P0B_SPR_HEAD_%02d" % i
        coll.objects.link(ob); ob.location = (xx, SPR_Y, 0); h_objs.append(ob)
    _select_only(h_objs[0])
    for ob in h_objs: ob.select_set(True)
    bpy.ops.object.join(); h_final = bpy.context.view_layer.objects.active
    h_final.name = "P0B_SPRINKLER_HEADS"
    bpy.data.objects.remove(hp, do_unlink=True)

    # end flanges + blind plates
    for xx, nm in ((X0, "W"), (X1, "E")):
        col = rect_collar(coll, "P0B_END_FLANGE_" + nm, DUCT_W, DUCT_H)
        col.location = (xx, DUCT_Y, DUCT_Z)
        if xx == X0:
            col.rotation_euler = (0, 0, math.pi)
        d = blind_plate(coll, "P0B_BLIND_" + nm, DUCT_W + 0.02, DUCT_H + 0.02)
        d.location = (xx + (-0.012 if xx == X0 else 0.012), DUCT_Y, DUCT_Z)

    # labels every 9.6 m, on the south face of the duct
    lp = label_plate(coll, "P0B_LABEL_PROTO")
    lab_objs = []
    for i, xx in enumerate([X0 + 4.8 + k * 9.6 for k in range(int((X1 - X0 - 4.8) / 9.6) + 1)]):
        ob = lp.copy(); ob.data = lp.data; ob.name = "P0B_LABEL_%02d" % i
        coll.objects.link(ob)
        ob.location = (xx, DUCT_Y + DUCT_W / 2 + 0.002, DUCT_Z + 0.12)
        ob.rotation_euler = (math.pi / 2, 0, 0)
        lab_objs.append(ob)
    _select_only(lab_objs[0])
    for ob in lab_objs: ob.select_set(True)
    bpy.ops.object.join(); lab_final = bpy.context.view_layer.objects.active
    lab_final.name = "P0B_LABELS"
    bpy.data.objects.remove(lp, do_unlink=True)

    # Z10 branch: from the main duct at y=-2 to the existing duct at y=19.6
    branch_count = 9  # 9 * 2.4 = 21.6 m -> y = 19.6
    bp = duct_segment(coll, "P0B_HVAC_BRANCH_SEG")
    branch = instanced_run(coll, bp, branch_count, SEG,
                           (43.0, DUCT_Y, DUCT_Z), rot_z=math.pi / 2)
    branch.name = "P0B_HVAC_BRANCH_Z10"
    branch.data.name = branch.name

    # saddle at the main duct (branch root)
    s1 = rect_collar(coll, "P0B_TEE_MAIN", DUCT_W, DUCT_H)
    s1.location = (43.0, DUCT_Y + DUCT_W / 2, DUCT_Z)
    s1.rotation_euler = (0, 0, -math.pi / 2)
    # connection plate at the Z10 duct
    s2 = rect_collar(coll, "P0B_TEE_Z10", DUCT_W, DUCT_H)
    s2.location = (43.0, 19.6, DUCT_Z)
    s2.rotation_euler = (0, 0, -math.pi / 2)

    # sleeves at the corridor header (y=4) and Z10 entrance (y=8)
    sleeve_master = bpy.data.objects.get("SM_SH_SLEEVE_RECT_800x600")
    if sleeve_master:
        for yy, nm in ((4.0, "CORR"), (8.0, "Z10")):
            sl = bpy.data.objects.new("P0B_SLEEVE_" + nm, sleeve_master.data)
            coll.objects.link(sl)
            sl.location = (43.0, yy, DUCT_Z)
            sl.rotation_euler = (0, 0, math.pi / 2)

    # final normals
    for ob in [o for o in coll.objects if o.type == 'MESH']:
        me = ob.data
        bm = bmesh.new(); bm.from_mesh(me)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        bm.to_mesh(me); bm.free()
        for p in me.polygons:
            p.use_smooth = True

    bpy.context.view_layer.update()

    # QA
    report = {"build": "P0B.1", "collection": COLL_NAME,
              "range": [X0, X1], "objects": {}, "totals": {}}
    total_tris = 0
    for ob in sorted([o for o in coll.objects if o.type == 'MESH'], key=lambda o: o.name):
        me = ob.data
        bm = bmesh.new(); bm.from_mesh(me)
        nonman = sum(1 for e in bm.edges if not e.is_manifold)
        deg = sum(1 for f in bm.faces if f.calc_area() < 1e-9)
        bm.free()
        tris = sum(len(p.vertices) - 2 for p in me.polygons)
        total_tris += tris
        bb = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
        report["objects"][ob.name] = {
            "tris": tris, "verts": len(me.vertices), "non_manifold": nonman,
            "degenerate": deg, "uv": bool(me.uv_layers),
            "bbox_min": [round(min(v[i] for v in bb), 3) for i in range(3)],
            "bbox_max": [round(max(v[i] for v in bb), 3) for i in range(3)],
        }
    report["totals"] = {"meshes": len(report["objects"]), "tris": total_tris}
    report["elapsed_s"] = round(time.time() - t0, 1)
    os.makedirs(os.path.dirname(QA_PATH), exist_ok=True)
    with open(QA_PATH, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)

    os.makedirs(os.path.dirname(BACKUP), exist_ok=True)
    if not os.path.exists(BACKUP):
        shutil.copy2(BLEND, BACKUP)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)

    print("P0B1_DONE meshes=%d tris=%d elapsed=%.1fs" %
          (report["totals"]["meshes"], total_tris, report["elapsed_s"]))
    for k, v in sorted(report["objects"].items()):
        print("  %-34s %7d tris nm=%d deg=%d" % (k, v["tris"], v["non_manifold"], v["degenerate"]))


if __name__ != "__main__":
    # exec() from the BlenderMCP addon runs with __name__ == "builtins".
    main()
