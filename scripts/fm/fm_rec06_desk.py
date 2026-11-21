"""REC06 - hero reception desk, credenza, equipment and chair.

Replaces the 60-triangle R2 desk family with a detailed L-shaped reception
counter, a three-door credenza, two monitors, keyboard, CPU and an ergonomic
task chair.  Existing pieces are retired (not deleted) to a hidden
collection so the pass is reversible.
"""

import bpy
import bmesh
import json
import math
import os
import shutil
import sys

from mathutils import Vector

sys.path.insert(0, "/home/riyo/Documentos/game/scripts/fm")
from fm_shared_p0_lib import ensure_materials, box, cyl, join_group, _pbr, srgb

ROOT = "/home/riyo/Documentos/game"
BLEND = ROOT + "/nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend"
BACKUP = ROOT + "/docs/backups/FM_LEVEL1_V06_ARCH_before_rec06_desk.blend"
QA = ROOT + "/docs/fm_rec06_desk_qa.json"

COLL = "L1_RECEPTION_R6_HERO"
RET = "L1_RECEPTION_RETIRED"

M = ensure_materials()
LAM = _pbr("M_REC06_Laminate", srgb(42, 52, 47), 0.0, 0.40,
           scale=16, bump=0.0008, micro=220, rough_var=0.08)
LAM_DARK = _pbr("M_REC06_Laminate_Dark", srgb(27, 33, 30), 0.0, 0.46,
                scale=22, bump=0.0008, micro=240, rough_var=0.07)
EDGE = _pbr("M_REC06_Edge_Rubber", srgb(18, 19, 18), 0.0, 0.62,
            scale=55, bump=0.0012, micro=320, rough_var=0.05)
SCREEN = _pbr("M_REC06_Screen", srgb(10, 16, 15), 0.0, 0.18,
              scale=70, bump=0.0003, micro=400, rough_var=0.04,
              emission=srgb(38, 78, 64), emission_strength=1.4)
PAPER = _pbr("M_REC06_Paper", srgb(212, 208, 194), 0.0, 0.82,
             scale=48, bump=0.0002, micro=320, rough_var=0.03)
CERAMIC = _pbr("M_REC06_Ceramic", srgb(198, 196, 188), 0.0, 0.30,
               scale=40, bump=0.0003, micro=280, rough_var=0.04)
KEY = _pbr("M_REC06_Key", srgb(30, 32, 31), 0.0, 0.58,
           scale=70, bump=0.0006, micro=300, rough_var=0.05)
FABRIC = _pbr("M_REC06_Fabric", srgb(28, 34, 31), 0.0, 0.88,
              scale=90, bump=0.0025, micro=420, rough_var=0.04)
CHROME = M["steel_bare"]
DARK = M["steel_dark"]
GALV = M["galv"]
ALU = M["aluminum"]
BLACK = M["plastic"]
ORANGE = M["paint_orange"]
BRASS = M["brass"]


def link_only(ob, col):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    col.objects.link(ob)


def get_coll(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c


def B(parts, name, sx, sy, sz, center, mat, bevel=0.002, seg=2):
    parts.append(box(bpy.context.scene.collection, name, sx, sy, sz,
                     center, mat, bevel, seg))


def C(parts, name, r, depth, center, mat, axis='Z', seg=20, bevel=0.0006):
    parts.append(cyl(bpy.context.scene.collection, name, r, depth, center,
                     mat, axis, seg, bevel, 1))


def add_monitor(parts, tag, base, face):
    """face=-1: screen looks south; +1: screen looks north."""
    x, y, z = base
    B(parts, tag + "_BASE", 0.26, 0.18, 0.025, (x, y, z + 0.0125), DARK, 0.002, 2)
    B(parts, tag + "_FOOT", 0.32, 0.22, 0.008, (x, y, z + 0.004), GALV, 0.001, 1)
    B(parts, tag + "_NECK", 0.060, 0.060, 0.160, (x, y, z + 0.105), DARK, 0.002, 2)
    B(parts, tag + "_HINGE", 0.12, 0.07, 0.07, (x, y, z + 0.185), BLACK, 0.002, 2)
    fy = y
    fz = z + 0.300
    B(parts, tag + "_SHELL", 0.58, 0.050, 0.36, (x, fy, fz), BLACK, 0.004, 3)
    B(parts, tag + "_BACK", 0.54, 0.014, 0.32, (x, fy - face * 0.030, fz), BLACK, 0.002, 2)
    # Recessed ventilation slots and a service label on the back shell.
    vy = fy - face * 0.036
    for dz in (-0.100, -0.060, -0.020, 0.020, 0.060, 0.100):
        B(parts, tag + "_VENT_%d" % int(dz * 1000), 0.300, 0.004, 0.010,
          (x, vy, fz + dz), EDGE, 0.0005, 1)
    B(parts, tag + "_VESA", 0.120, 0.016, 0.120, (x, fy - face * 0.040, fz),
      DARK, 0.002, 2)
    B(parts, tag + "_BACK_LOGO", 0.090, 0.004, 0.012,
      (x, vy - face * 0.002, fz - 0.140), ORANGE, 0.0004, 1)
    s_y = fy + face * 0.0265
    B(parts, tag + "_SCREEN", 0.530, 0.004, 0.300, (x, s_y, fz), SCREEN, 0.0006, 1)
    # Bezel lips around the screen.
    for dz in (-0.158, 0.158):
        B(parts, tag + "_BEZEL_%s" % ("T" if dz > 0 else "B"),
          0.58, 0.010, 0.018, (x, s_y - face * 0.004, fz + dz), BLACK, 0.0005, 1)
    for dx in (-0.278, 0.278):
        B(parts, tag + "_BEZEL_%s" % ("R" if dx > 0 else "L"),
          0.018, 0.010, 0.330, (x + dx, s_y - face * 0.004, fz), BLACK, 0.0005, 1)
    B(parts, tag + "_LOGO", 0.075, 0.004, 0.012, (x, s_y - face * 0.002, fz - 0.155),
      ORANGE, 0.0004, 1)
    # Cable from monitor to the desk grommet.
    C(parts, tag + "_CABLE_V", 0.007, 0.28, (x + 0.10, fy - face * 0.04, z + 0.14),
      BLACK, 'Z', 8)
    C(parts, tag + "_CABLE_H", 0.007, 0.24, (x + 0.10, fy - face * 0.16, z + 0.01),
      BLACK, 'Y', 8)


def add_keyboard(parts):
    x, y, z = -103.0, -13.20, 0.975
    B(parts, "REC06_KB_BODY", 0.45, 0.16, 0.014, (x, y, z + 0.007), BLACK, 0.002, 2)
    B(parts, "REC06_KB_RIM", 0.46, 0.17, 0.006, (x, y, z + 0.002), DARK, 0.001, 1)
    # 5 rows of keys.
    kw, kh, kz = 0.024, 0.022, 0.008
    for row in range(5):
        ky = y - 0.052 + row * 0.026
        n = 14 if row != 4 else 10
        for col in range(n):
            kx = x - 0.195 + col * 0.028
            if row == 4 and col > 3:
                kx += 0.055
            B(parts, "REC06_KB_%d_%d" % (row, col), kw, kh, kz,
              (kx, ky, z + 0.016), KEY, 0.0008, 1)
    B(parts, "REC06_KB_SPACE", 0.150, 0.022, 0.008, (x, y + 0.058, z + 0.016),
      KEY, 0.0008, 1)
    C(parts, "REC06_KB_CABLE", 0.005, 0.22, (x - 0.18, y - 0.10, z - 0.01),
      BLACK, 'Y', 8)


def add_cpu(parts):
    x, y, z = -100.35, -13.15, 0.21
    B(parts, "REC06_CPU_BODY", 0.22, 0.45, 0.42, (x, y, z), LAM_DARK, 0.003, 2)
    B(parts, "REC06_CPU_FRONT", 0.20, 0.018, 0.38, (x, y - 0.234, z), BLACK, 0.002, 2)
    # Mesh front intake and front I/O.
    for i in range(7):
        B(parts, "REC06_CPU_VENT_%d" % i, 0.16, 0.006, 0.010,
          (x, y - 0.245, z + 0.14 - i * 0.024), DARK, 0.0004, 1)
    C(parts, "REC06_CPU_POWER", 0.012, 0.006, (x - 0.06, y - 0.246, z + 0.175),
      ORANGE, 'Y', 12)
    for i in range(3):
        B(parts, "REC06_CPU_USB_%d" % i, 0.028, 0.006, 0.012,
          (x + 0.02 + i * 0.035, y - 0.246, z + 0.175), CHROME, 0.0004, 1)
    for sx in (-0.09, 0.09):
        for sy in (-0.19, 0.19):
            C(parts, "REC06_CPU_FOOT", 0.018, 0.018, (x + sx, y + sy, z - 0.215),
              BLACK, 'Z', 10)


def add_chair(parts):
    cx, cy = -102.0, -13.92
    # Five-star base.
    for i in range(5):
        a = math.radians(90 + i * 72)
        ex, ey = cx + math.cos(a) * 0.24, cy + math.sin(a) * 0.24
        B(parts, "REC06_CH_A%d" % i, 0.055, 0.30, 0.035,
          ((cx + ex) / 2, (cy + ey) / 2, 0.075), DARK, 0.004, 2)
        C(parts, "REC06_CH_CAST%d" % i, 0.032, 0.040, (ex, ey, 0.035),
          BLACK, 'Z', 16)
        C(parts, "REC06_CH_HUB%d" % i, 0.018, 0.012, (ex, ey, 0.058), CHROME, 'Z', 10)
    C(parts, "REC06_CH_HUB", 0.055, 0.06, (cx, cy, 0.11), DARK, 'Z', 20)
    C(parts, "REC06_CH_GAS", 0.026, 0.20, (cx, cy, 0.22), CHROME, 'Z', 16)
    C(parts, "REC06_CH_GAS2", 0.018, 0.14, (cx, cy, 0.30), CHROME, 'Z', 16)
    B(parts, "REC06_CH_MECH", 0.20, 0.24, 0.06, (cx, cy, 0.39), DARK, 0.003, 2)
    B(parts, "REC06_CH_SEAT", 0.50, 0.50, 0.10, (cx, cy, 0.46), FABRIC, 0.025, 4)
    B(parts, "REC06_CH_SEAT_FRAME", 0.52, 0.52, 0.035, (cx, cy, 0.405), BLACK, 0.004, 2)
    # Back frame with side rails, top rail and a mesh panel.
    for s in (-1, 1):
        B(parts, "REC06_CH_BACK_RAIL_%d" % s, 0.035, 0.045, 0.52,
          (cx + s * 0.225, cy - 0.278, 0.78), BLACK, 0.004, 2)
    B(parts, "REC06_CH_BACK_TOP", 0.49, 0.045, 0.035,
      (cx, cy - 0.278, 1.04), BLACK, 0.004, 2)
    B(parts, "REC06_CH_BACK_MESH", 0.42, 0.020, 0.42,
      (cx, cy - 0.260, 0.82), FABRIC, 0.012, 3)
    B(parts, "REC06_CH_LUMBAR", 0.34, 0.035, 0.10,
      (cx, cy - 0.242, 0.61), FABRIC, 0.010, 3)
    B(parts, "REC06_CH_LUMBAR_BAR", 0.36, 0.028, 0.028,
      (cx, cy - 0.270, 0.61), BLACK, 0.002, 2)
    for i in range(4):
        B(parts, "REC06_CH_RIB%d" % i, 0.40, 0.008, 0.008,
          (cx, cy - 0.248, 0.70 + i * 0.09), BLACK, 0.001, 1)
    # Armrests.
    for s in (-1, 1):
        ax = cx + s * 0.30
        B(parts, "REC06_CH_ARM_POST_%d" % s, 0.045, 0.045, 0.16,
          (ax, cy - 0.02, 0.54), DARK, 0.002, 2)
        B(parts, "REC06_CH_ARM_%d" % s, 0.07, 0.26, 0.035,
          (ax, cy - 0.04, 0.63), FABRIC, 0.008, 3)


def add_desk(parts):
    # Counter top and edge banding.
    B(parts, "REC06_DESK_TOP", 4.20, 0.85, 0.05, (-102, -13.0, 0.945), LAM, 0.003, 3)
    B(parts, "REC06_DESK_EDGE_F", 4.20, 0.024, 0.014, (-102, -12.58, 0.972), EDGE, 0.001, 1)
    B(parts, "REC06_DESK_EDGE_B", 4.20, 0.024, 0.014, (-102, -13.42, 0.972), EDGE, 0.001, 1)
    B(parts, "REC06_DESK_EDGE_L", 0.024, 0.85, 0.014, (-104.10, -13.0, 0.972), EDGE, 0.001, 1)
    B(parts, "REC06_DESK_EDGE_R", 0.024, 0.85, 0.014, (-99.90, -13.0, 0.972), EDGE, 0.001, 1)
    # Front fascia with four recessed panels and an orange datum line.
    B(parts, "REC06_DESK_FRONT", 4.20, 0.060, 0.90, (-102, -12.60, 0.45), LAM, 0.002, 2)
    for i in range(4):
        px = -103.5 + i * 1.0
        B(parts, "REC06_DESK_PANEL_%d" % i, 0.94, 0.012, 0.66,
          (px, -12.565, 0.47), LAM_DARK, 0.0015, 2)
    for px in (-103.5, -102.5, -101.5, -100.5):
        B(parts, "REC06_DESK_REVEAL_%d" % int(px * 10), 0.012, 0.008, 0.72,
          (px, -12.558, 0.48), EDGE, 0.0004, 1)
    B(parts, "REC06_DESK_ACCENT", 4.14, 0.010, 0.020, (-102, -12.556, 0.86),
      ORANGE, 0.0005, 1)
    B(parts, "REC06_DESK_KICK", 4.04, 0.030, 0.080, (-102, -12.64, 0.040),
      EDGE, 0.001, 1)
    # Bull-nose nosing.
    C(parts, "REC06_DESK_NOSE", 0.012, 4.20, (-102, -12.585, 0.972),
      EDGE, 'X', 16)
    # Modesty panel.
    B(parts, "REC06_DESK_MODESTY", 3.951, 0.050, 0.90, (-102, -13.39, 0.45),
      LAM_DARK, 0.002, 2)
    # Side panels and levelers.
    for s, sx in (("L", -104.08), ("R", -99.92)):
        B(parts, "REC06_DESK_SIDE_" + s, 0.070, 0.85, 0.93, (sx, -13.0, 0.465),
          LAM, 0.002, 2)
        B(parts, "REC06_DESK_SIDE_KICK_" + s, 0.075, 0.70, 0.06,
          (sx, -13.0, 0.03), EDGE, 0.001, 1)
        for sy in (-13.35, -12.65):
            C(parts, "REC06_DESK_LEVEL_" + s, 0.022, 0.022, (sx, sy, 0.011),
              CHROME, 'Z', 12)
    # L return.
    B(parts, "REC06_RETURN_FRONT", 0.060, 1.37, 0.918, (-104.27, -14.115, 0.459),
      LAM, 0.002, 2)
    B(parts, "REC06_RETURN_TOP", 0.50, 1.37, 0.05, (-104.05, -14.115, 0.943),
      LAM, 0.003, 3)
    B(parts, "REC06_RETURN_EDGE", 0.024, 1.37, 0.014, (-104.29, -14.115, 0.970),
      EDGE, 0.001, 1)
    B(parts, "REC06_RETURN_SIDE", 0.50, 0.060, 0.918, (-104.05, -14.78, 0.459),
      LAM, 0.002, 2)
    B(parts, "REC06_RETURN_KICK", 0.44, 0.030, 0.06, (-104.05, -14.75, 0.03),
      EDGE, 0.001, 1)
    C(parts, "REC06_RETURN_LEVEL", 0.022, 0.022, (-104.05, -14.72, 0.011),
      CHROME, 'Z', 12)
    # Under-desk cable tray and drops.
    B(parts, "REC06_CABLE_TRAY", 3.10, 0.22, 0.06, (-102, -13.25, 0.84),
      GALV, 0.001, 1)
    for x in (-103.0, -101.0, -100.3):
        C(parts, "REC06_CABLE_DROP_%d" % int(x * 10), 0.010, 0.18,
          (x, -13.10, 0.91), BLACK, 'Z', 8)
    # Grommets.
    for x in (-103.5, -100.5):
        C(parts, "REC06_GROMMET_%d" % int(x * 10), 0.045, 0.014, (x, -13.05, 0.972),
          BLACK, 'Z', 20)
        C(parts, "REC06_GROMMET_CAP_%d" % int(x * 10), 0.033, 0.016,
          (x, -13.05, 0.973), GALV, 'Z', 20)
    # Two shallow pencil drawers under the staff side.
    for i, x in enumerate((-100.9, -101.7)):
        B(parts, "REC06_PENCIL_%d" % i, 0.70, 0.035, 0.10, (x, -13.35, 0.83),
          LAM_DARK, 0.0015, 2)
        B(parts, "REC06_PENCIL_HANDLE_%d" % i, 0.16, 0.012, 0.016,
          (x, -13.373, 0.83), GALV, 0.0005, 1)
        C(parts, "REC06_PENCIL_LOCK_%d" % i, 0.010, 0.008,
          (x + 0.25, -13.373, 0.83), BRASS, 'Y', 10)
    # Credenza.
    B(parts, "REC06_CRED_BODY", 3.60, 0.50, 0.78, (-102, -14.55, 0.39),
      LAM, 0.003, 2)
    B(parts, "REC06_CRED_TOP", 3.70, 0.55, 0.05, (-102, -14.55, 0.805),
      LAM, 0.003, 3)
    B(parts, "REC06_CRED_EDGE", 3.70, 0.02, 0.012, (-102, -14.276, 0.832),
      EDGE, 0.0008, 1)
    B(parts, "REC06_CRED_KICK", 3.48, 0.03, 0.10, (-102, -14.325, 0.05),
      EDGE, 0.001, 1)
    for i, x in enumerate((-103.20, -102.00, -100.80)):
        B(parts, "REC06_CRED_DOOR_%d" % i, 1.12, 0.018, 0.62,
          (x, -14.291, 0.43), LAM_DARK, 0.0015, 2)
        B(parts, "REC06_CRED_HANDLE_%d" % i, 0.26, 0.016, 0.018,
          (x, -14.276, 0.62), GALV, 0.0005, 1)
        C(parts, "REC06_CRED_LOCK_%d" % i, 0.010, 0.008,
          (x + 0.40, -14.276, 0.64), BRASS, 'Y', 10)
    C(parts, "REC06_CRED_GROMMET", 0.035, 0.014, (-100.6, -14.55, 0.833),
      BLACK, 'Z', 16)


def add_equipment(parts):
    add_monitor(parts, "REC06_MON_CRED", (-102.9, -14.35, 0.83), +1)
    add_monitor(parts, "REC06_MON_DESK", (-103.0, -12.85, 0.97), -1)
    add_keyboard(parts)
    add_cpu(parts)
    # Papers, pen cup and mug: generic office dressing, no narrative.
    for i, (x, y, r) in enumerate(((-101.55, -13.02, 0.06),
                                   (-101.45, -12.98, -0.04),
                                   (-101.62, -12.95, 0.12))):
        B(parts, "REC06_PAPER_%d" % i, 0.21, 0.297, 0.002,
          (x, y, 0.973), PAPER, 0.0002, 1)
    C(parts, "REC06_PEN_CUP", 0.035, 0.10, (-101.95, -13.05, 1.02),
      DARK, 'Z', 16)
    for i in range(3):
        a = math.radians(20 + i * 35)
        C(parts, "REC06_PEN_%d" % i, 0.004, 0.14,
          (-101.95 + math.cos(a) * 0.012, -13.05 + math.sin(a) * 0.012, 1.10),
          ORANGE if i == 1 else DARK, 'Z', 8)
    C(parts, "REC06_MUG", 0.040, 0.09, (-100.95, -13.02, 1.02), CERAMIC, 'Z', 18)
    C(parts, "REC06_MUG_IN", 0.033, 0.006, (-100.95, -13.02, 1.066), BLACK, 'Z', 18)


def stats(ob):
    me = ob.data
    me.calc_loop_triangles()
    bm = bmesh.new()
    bm.from_mesh(me)
    nonman = sum(1 for e in bm.edges if len(e.link_faces) > 2)
    deg = sum(1 for f in bm.faces if f.calc_area() < 1e-10)
    bm.free()
    return {"name": ob.name, "tris": len(me.loop_triangles),
            "verts": len(me.vertices), "non_manifold_edges": nonman,
            "degenerate_faces": deg, "uv": bool(me.uv_layers)}


def retire():
    prefixes = (
        "PROP_REC02_Desk_",
        "PROP_REC02_Credenza",
        "PROP_REC02_Monitor_Credenza",
        "PROP_REC02_Monitor_Desk",
        "PROP_REC02_Chair_Desk",
        "PROP_REC02_Keyboard",
        "PROP_REC02_CPU",
    )
    ret = get_coll(RET)
    moved = []
    for ob in list(bpy.data.objects):
        if any(ob.name.startswith(p) for p in prefixes):
            link_only(ob, ret)
            ob.hide_render = True
            ob.hide_viewport = True
            ob.hide_set(True)
            moved.append(ob.name)
    return sorted(moved)


def main():
    if not os.path.exists(BACKUP):
        shutil.copy2(BLEND, BACKUP)
    root = get_coll(COLL)
    # Idempotent rebuild.
    for ob in list(root.objects):
        if ob.name.startswith("REC06_"):
            data = ob.data
            bpy.data.objects.remove(ob, do_unlink=True)
            if data is not None and getattr(data, "users", 0) == 0:
                try:
                    bpy.data.meshes.remove(data)
                except Exception:
                    pass

    moved = retire()

    desk_parts, equip_parts, chair_parts = [], [], []
    add_desk(desk_parts)
    add_equipment(equip_parts)
    add_chair(chair_parts)

    desk = join_group(root, "REC06_DESK_HERO", desk_parts, uv=True, wn=True)
    equip = join_group(root, "REC06_EQUIPMENT_HERO", equip_parts, uv=True, wn=True)
    chair = join_group(root, "REC06_CHAIR_HERO", chair_parts, uv=True, wn=True)

    # join_group can leave the result in the active collection; pin the hero
    # cluster to the reception R6 collection so renders and exports see it.
    r6 = bpy.data.collections.get(COLL)
    for ob in (desk, equip, chair):
        for col in list(ob.users_collection):
            col.objects.unlink(ob)
        r6.objects.link(ob)

    for ob, family in ((desk, "DESK"), (equip, "EQUIPMENT"), (chair, "CHAIR")):
        ob["fm_class"] = "PROP"
        ob["fm_family"] = "RECEPTION_DESK"
        ob["fm_generation"] = "VERIFIED_REC06"
        ob["fm_subfamily"] = family
        ob["fm_tris"] = stats(ob)["tris"]

    bpy.context.view_layer.update()
    report = {
        "collection": COLL,
        "retired_collection": RET,
        "retired": moved,
        "objects": [stats(ob) for ob in (desk, equip, chair)],
        "total_tris": sum(stats(ob)["tris"] for ob in (desk, equip, chair)),
        "total_verts": sum(stats(ob)["verts"] for ob in (desk, equip, chair)),
    }
    ok = all(o["non_manifold_edges"] == 0 and o["degenerate_faces"] == 0 and o["uv"]
             for o in report["objects"])
    report["qa_pass"] = ok
    with open(QA, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("REC06_DONE", report["total_tris"], report["total_verts"], ok)
    print("RETIRED", len(moved))
    for o in report["objects"]:
        print("OBJ", o["name"], o["tris"], o["non_manifold_edges"],
              o["degenerate_faces"], o["uv"])


main()
