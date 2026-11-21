import bpy
import bmesh
import json
import math
import os
import shutil
import sys

from mathutils import Vector, Matrix

sys.path.insert(0, "/home/riyo/Documentos/game/scripts/fm")
from fm_shared_p0_lib import ensure_materials, box, cyl, join_group, _pbr, srgb

ROOT = "/home/riyo/Documentos/game"
BLEND = os.path.join(ROOT, "nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend")
BACKUP = os.path.join(ROOT, "docs/backups/FM_LEVEL1_V06_ARCH_before_rec07.blend")
QA = os.path.join(ROOT, "docs/fm_rec07_security_desk_qa.json")
R7_NAME = "L1_RECEPTION_R7_HERO"
RETIRED_NAME = "L1_RECEPTION_RETIRED"

M = ensure_materials()
LAM = _pbr("M_REC07_Laminate", srgb(36, 52, 44), 0.0, 0.55, scale=14,
           bump=0.0006, micro=240, rough_var=0.05)
LAM_DARK = _pbr("M_REC07_Laminate_Dark", srgb(20, 28, 24), 0.0, 0.60, scale=18,
                bump=0.0005, micro=260, rough_var=0.05)
EDGE = _pbr("M_REC07_Edge", srgb(9, 10, 9), 0.0, 0.70)
CHROME = M["steel_bare"]
DARK = M["steel_dark"]
GALV = M["galv"]
ALU = M["aluminum"]
BLACK = M["plastic"]
ORANGE = M["paint_orange"]
BRASS = M["brass"]
PAPER = _pbr("M_REC07_Paper", srgb(214, 210, 196), 0.0, 0.88, scale=48,
             bump=0.0002, micro=320, rough_var=0.02)
MANILA = _pbr("M_REC07_Manila", srgb(148, 118, 72), 0.0, 0.86, scale=36,
              bump=0.0003, micro=300, rough_var=0.03)
KEY = _pbr("M_REC07_Key", srgb(30, 32, 31), 0.0, 0.58, scale=40,
           bump=0.0002, micro=300, rough_var=0.02)
CERAMIC = _pbr("M_REC07_Ceramic", srgb(198, 196, 188), 0.0, 0.38)
TEXT = _pbr("M_REC07_Text", srgb(210, 210, 196), 0.0, 0.50)
SCREEN = _pbr("M_REC07_Screen", srgb(8, 12, 10), 0.0, 0.18,
              emission=srgb(28, 66, 52), emission_strength=1.2)
CCTV_A = _pbr("M_REC07_CCTV_A", srgb(30, 62, 54), 0.0, 0.30,
              emission=srgb(14, 38, 30), emission_strength=0.8)
CCTV_B = _pbr("M_REC07_CCTV_B", srgb(46, 56, 50), 0.0, 0.30,
              emission=srgb(18, 30, 24), emission_strength=0.6)
CCTV_C = _pbr("M_REC07_CCTV_C", srgb(22, 34, 38), 0.0, 0.30,
              emission=srgb(10, 22, 28), emission_strength=0.5)
RED = _pbr("M_REC07_Red", srgb(160, 22, 18), 0.0, 0.40,
           emission=srgb(150, 12, 8), emission_strength=1.0)


def coll_get(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


R7 = coll_get(R7_NAME)
RETIRED = coll_get(RETIRED_NAME)


def B(parts, name, sx, sy, sz, center, mat, bevel=0.002, seg=2):
    ob = box(bpy.context.scene.collection, name, sx, sy, sz, center, mat, bevel, seg)
    parts.append(ob)
    return ob


def C(parts, name, r, depth, center, mat, axis='Z', seg=20, bevel=0.0006):
    ob = cyl(bpy.context.scene.collection, name, r, depth, center, mat, axis, seg, bevel, 1)
    parts.append(ob)
    return ob


def clean_r7():
    for ob in list(R7.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for ob in list(bpy.data.objects):
        if ob.name.startswith("REC07_"):
            bpy.data.objects.remove(ob, do_unlink=True)


def retire_old():
    names = []
    for ob in list(bpy.data.objects):
        if ob.type != 'MESH':
            continue
        n = ob.name
        if (n.startswith("PROP_REC02_Security_") or
                n.startswith("PROP_REC02_Monitor_Security_") or
                n.startswith("PROP_REC02_Chair_Security_")):
            for c in list(ob.users_collection):
                c.objects.unlink(ob)
            RETIRED.objects.link(ob)
            ob.hide_render = True
            ob.hide_viewport = True
            names.append(n)
    return names


def add_text(parts, body, x, y, z, size):
    try:
        bpy.ops.object.text_add(location=(x, y, z))
        txt = bpy.context.object
        txt.name = "REC07_TEXT_TMP"
        txt.data.body = body
        txt.data.align_x = 'CENTER'
        txt.data.align_y = 'CENTER'
        txt.data.size = size
        txt.data.extrude = 0.002
        txt.data.bevel_depth = 0.0004
        txt.matrix_world = Matrix.Translation((x, y, z)) @ Matrix((
            (-1, 0, 0, 0),
            (0, 0, 1, 0),
            (0, 1, 0, 0),
            (0, 0, 0, 1),
        ))
        bpy.context.view_layer.objects.active = txt
        txt.select_set(True)
        bpy.ops.object.convert(target='MESH')
        txt = bpy.context.object
        txt.data.materials.clear()
        txt.data.materials.append(TEXT)
        parts.append(txt)
        return txt
    except Exception as exc:
        print("TEXT_SKIP", repr(exc))
        return None


def add_security_monitor(parts):
    x, y = -83.50, -10.80
    z = 0.870
    B(parts, "MON_BASE", 0.18, 0.26, 0.025, (x, y, z + 0.0125), DARK, 0.001)
    B(parts, "MON_FOOT", 0.26, 0.32, 0.008, (x, y, z + 0.004), GALV, 0.001)
    B(parts, "MON_NECK", 0.06, 0.06, 0.20, (x, y, z + 0.11), DARK, 0.001)
    B(parts, "MON_HINGE", 0.10, 0.12, 0.08, (x, y, z + 0.22), BLACK, 0.001)
    fz = 1.22
    B(parts, "MON_SHELL", 0.05, 0.58, 0.36, (x, y, fz), BLACK, 0.0015)
    B(parts, "MON_BACK", 0.014, 0.54, 0.32, (x - 0.030, y, fz), BLACK, 0.001)
    for i in range(6):
        B(parts, "MON_VENT_%d" % i, 0.004, 0.300, 0.010,
          (x - 0.038, y, fz - 0.10 + i * 0.04), DARK, 0.0005)
    B(parts, "MON_VESA", 0.016, 0.120, 0.120, (x - 0.041, y, fz), DARK, 0.001)
    for sy in (-1, 1):
        for sz in (-1, 1):
            C(parts, "MON_VESA_BOLT_%d_%d" % (sy, sz), 0.006, 0.006,
              (x - 0.050, y + sy * 0.045, fz + sz * 0.045), CHROME, 'X', 8, 0.0004)
    B(parts, "MON_SCREEN", 0.004, 0.530, 0.300, (x + 0.0265, y, fz), SCREEN, 0.0004)
    for sz in (-1, 1):
        B(parts, "MON_BEZEL_TB_%d" % sz, 0.010, 0.580, 0.018,
          (x + 0.026, y, fz + sz * 0.171), BLACK, 0.0006)
    for sy in (-1, 1):
        B(parts, "MON_BEZEL_LR_%d" % sy, 0.010, 0.018, 0.330,
          (x + 0.026, y + sy * 0.281, fz), BLACK, 0.0006)
    B(parts, "MON_LOGO", 0.004, 0.075, 0.012, (x + 0.033, y, fz - 0.160), ORANGE, 0.0003)
    tiles = [CCTV_A, CCTV_B, CCTV_C]
    for row in range(3):
        for col in range(3):
            mat = tiles[(row + col) % 3]
            B(parts, "MON_CCTV_%d_%d" % (row, col), 0.002, 0.155, 0.085,
              (x + 0.030, y + (col - 1) * 0.170, fz + (1 - row) * 0.100), mat, 0.0002)
    for col in (-1, 1):
        B(parts, "MON_GRID_V_%d" % col, 0.002, 0.006, 0.300,
          (x + 0.032, y + col * 0.085, fz), BLACK, 0.0002)
    for row in (-1, 1):
        B(parts, "MON_GRID_H_%d" % row, 0.002, 0.530, 0.006,
          (x + 0.032, y, fz + row * 0.050), BLACK, 0.0002)
    C(parts, "MON_REC_DOT", 0.008, 0.004, (x + 0.033, y - 0.245, fz + 0.150), RED, 'X', 10, 0.0002)
    B(parts, "MON_TIME_BAR", 0.002, 0.120, 0.008, (x + 0.033, y + 0.170, fz - 0.135), DARK, 0.0002)
    B(parts, "MON_TOP_BAR", 0.004, 0.180, 0.006, (x + 0.033, y - 0.130, fz + 0.155), DARK, 0.0002)


def add_desk(parts):
    x0, x1 = -85.10, -82.90
    y0, y1 = -11.15, -10.45
    z0, z1 = 0.97, 1.02
    hx0, hx1 = -83.56, -83.44
    hy0, hy1 = -10.86, -10.74
    # top split around the monitor neck hole
    B(parts, "DESK_TOP_W", hx0 - x0, y1 - y0, z1 - z0, ((x0 + hx0) / 2, -10.80, (z0 + z1) / 2), LAM, 0.002)
    B(parts, "DESK_TOP_E", x1 - hx1, y1 - y0, z1 - z0, ((hx1 + x1) / 2, -10.80, (z0 + z1) / 2), LAM, 0.002)
    B(parts, "DESK_TOP_N", hx1 - hx0, hy0 - y0, z1 - z0, (-83.50, (y0 + hy0) / 2, (z0 + z1) / 2), LAM, 0.002)
    B(parts, "DESK_TOP_S", hx1 - hx0, y1 - hy1, z1 - z0, (-83.50, (hy1 + y1) / 2, (z0 + z1) / 2), LAM, 0.002)
    # perimeter edge
    B(parts, "DESK_EDGE_N", x1 - x0, 0.020, 0.055, (-84.0, y1 - 0.010, 1.012), EDGE, 0.001)
    B(parts, "DESK_EDGE_S", x1 - x0, 0.020, 0.055, (-84.0, y0 + 0.010, 1.012), EDGE, 0.001)
    B(parts, "DESK_EDGE_W", 0.020, y1 - y0, 0.055, (x0 + 0.010, -10.80, 1.012), EDGE, 0.001)
    B(parts, "DESK_EDGE_E", 0.020, y1 - y0, 0.055, (x1 - 0.010, -10.80, 1.012), EDGE, 0.001)
    # monitor hole bezel and brush
    B(parts, "DESK_HOLE_BEZEL_N", 0.18, 0.020, 0.012, (-83.50, hy0 - 0.010, 1.028), DARK, 0.001)
    B(parts, "DESK_HOLE_BEZEL_S", 0.18, 0.020, 0.012, (-83.50, hy1 + 0.010, 1.028), DARK, 0.001)
    B(parts, "DESK_HOLE_BEZEL_W", 0.020, 0.14, 0.012, (hx0 - 0.010, -10.80, 1.028), DARK, 0.001)
    B(parts, "DESK_HOLE_BEZEL_E", 0.020, 0.14, 0.012, (hx1 + 0.010, -10.80, 1.028), DARK, 0.001)
    B(parts, "DESK_HOLE_BRUSH", 0.020, 0.12, 0.010, (-83.50, -10.74, 1.030), BLACK, 0.0005)
    # front / modesty / side
    B(parts, "DESK_FRONT", x1 - x0, 0.06, 0.90, (-84.0, -10.50, 0.45), LAM_DARK, 0.002)
    for i, x in enumerate((-84.38, -83.62)):
        B(parts, "DESK_FRONT_REVEAL_%d" % i, 0.012, 0.008, 0.86, (x, -10.468, 0.45), EDGE, 0.0005)
    B(parts, "DESK_ORANGE_LINE", x1 - x0, 0.010, 0.026, (-84.0, -10.466, 0.835), ORANGE, 0.0005)
    B(parts, "DESK_KICK", x1 - x0, 0.030, 0.12, (-84.0, -10.462, 0.075), GALV, 0.001)
    B(parts, "DESK_RUBBER_BASE", x1 - x0 + 0.04, 0.040, 0.035, (-84.0, -10.470, 0.020), EDGE, 0.001)
    B(parts, "DESK_PLAQUE", 0.62, 0.012, 0.16, (-84.0, -10.462, 0.640), BLACK, 0.001)
    B(parts, "DESK_PLAQUE_LINE", 0.62, 0.006, 0.016, (-84.0, -10.455, 0.705), ORANGE, 0.0003)
    C(parts, "DESK_BADGE_OUTER", 0.060, 0.010, (-84.22, -10.455, 0.640), ORANGE, 'Y', 6, 0.0006)
    C(parts, "DESK_BADGE_INNER", 0.046, 0.012, (-84.22, -10.454, 0.640), BLACK, 'Y', 6, 0.0006)
    B(parts, "DESK_BADGE_BAR", 0.050, 0.008, 0.010, (-84.22, -10.448, 0.640), TEXT, 0.0003)
    for i in range(3):
        B(parts, "DESK_PLAQUE_BAR_%d" % i, 0.10, 0.006, 0.012,
          (-84.00 + i * 0.12, -10.455, 0.640), TEXT, 0.0003)
    B(parts, "DESK_MODESTY", x1 - x0, 0.05, 0.90, (-84.0, -11.12, 0.45), LAM_DARK, 0.002)
    B(parts, "DESK_ACCESS_PANEL", 0.50, 0.020, 0.40, (-83.50, -11.148, 0.55), BLACK, 0.001)
    for i in range(6):
        B(parts, "DESK_ACCESS_VENT_%d" % i, 0.40, 0.006, 0.012,
          (-83.50, -11.159, 0.455 + i * 0.038), DARK, 0.0004)
    for i, (sx, sz) in enumerate(((-0.22, -0.16), (0.22, -0.16), (-0.22, 0.16), (0.22, 0.16))):
        C(parts, "DESK_ACCESS_SCREW_%d" % i, 0.007, 0.006,
          (-83.50 + sx, -11.161, 0.55 + sz), CHROME, 'Y', 8, 0.0003)
    B(parts, "DESK_WEST_SIDE", 0.06, y1 - y0, 0.97, (x0 + 0.030, -10.80, 0.485), LAM_DARK, 0.002)
    B(parts, "DESK_WEST_KICK", 0.06, y1 - y0, 0.10, (x0 + 0.030, -10.80, 0.070), GALV, 0.001)
    # open east kneehole
    for i, y in enumerate((-11.10, -10.50)):
        B(parts, "DESK_EAST_POST_%d" % i, 0.05, 0.05, 0.97, (x1 - 0.025, y, 0.485), GALV, 0.001)
        B(parts, "DESK_EAST_PAD_%d" % i, 0.07, 0.07, 0.020, (x1 - 0.025, y, 0.010), EDGE, 0.001)
    B(parts, "DESK_EAST_RAIL", 0.05, y1 - y0, 0.05, (x1 - 0.025, -10.80, 0.105), GALV, 0.001)
    B(parts, "DESK_EAST_TOP_RAIL", 0.05, y1 - y0, 0.05, (x1 - 0.025, -10.80, 0.945), GALV, 0.001)
    # west storage cabinet
    B(parts, "DESK_CABINET", 0.55, 0.60, 0.72, (-84.60, -10.80, 0.36), LAM_DARK, 0.002)
    B(parts, "DESK_CABINET_DOOR", 0.020, 0.54, 0.62, (-84.32, -10.80, 0.38), LAM, 0.001)
    B(parts, "DESK_CABINET_HANDLE", 0.020, 0.030, 0.180, (-84.305, -10.55, 0.50), BRASS, 0.001)
    C(parts, "DESK_CABINET_LOCK", 0.018, 0.012, (-84.305, -10.55, 0.66), BRASS, 'X', 12, 0.0004)
    for i in range(5):
        B(parts, "DESK_CABINET_VENT_%d" % i, 0.006, 0.30, 0.010,
          (-84.306, -10.80, 0.20 + i * 0.035), DARK, 0.0004)
    # shelf and cable tray
    B(parts, "DESK_MONITOR_SHELF", 0.55, 0.55, 0.030, (-83.50, -10.80, 0.855), GALV, 0.001)
    B(parts, "DESK_CABLE_TRAY", 1.60, 0.22, 0.06, (-84.15, -10.80, 0.915), GALV, 0.001)
    for i, yy in enumerate((-10.86, -10.80, -10.74)):
        C(parts, "DESK_CABLE_%d" % i, 0.011, 0.10, (-83.55, yy, 0.915), BLACK if i != 1 else ORANGE, 'Z', 8, 0.0003)
    # socket strip under the top
    B(parts, "DESK_POWER_STRIP", 0.42, 0.08, 0.045, (-84.15, -10.56, 0.930), BLACK, 0.001)
    for i in range(4):
        B(parts, "DESK_SOCKET_%d" % i, 0.055, 0.030, 0.010, (-84.30 + i * 0.10, -10.52, 0.950), DARK, 0.0003)


def add_equipment(parts):
    add_security_monitor(parts)
    # keyboard
    B(parts, "KBD_BASE", 0.16, 0.45, 0.025, (-82.98, -10.80, 1.0325), BLACK, 0.001)
    for row in range(5):
        for col in range(14):
            B(parts, "KEY_%d_%d" % (row, col), 0.020, 0.024, 0.007,
              (-83.045 + row * 0.026, -11.000 + col * 0.029, 1.049), KEY, 0.0004)
    B(parts, "KBD_SPACE", 0.022, 0.120, 0.007, (-82.932, -10.800, 1.049), KEY, 0.0004)
    B(parts, "MOUSEPAD", 0.22, 0.18, 0.003, (-82.94, -10.55, 1.0215), EDGE, 0.0005)
    B(parts, "MOUSE", 0.06, 0.10, 0.030, (-82.94, -10.55, 1.035), BLACK, 0.004)
    B(parts, "MOUSE_BTN", 0.055, 0.040, 0.006, (-82.94, -10.58, 1.052), DARK, 0.0005)
    # radio charger
    B(parts, "RADIO_BASE", 0.36, 0.20, 0.06, (-84.75, -10.62, 1.050), BLACK, 0.002)
    for i, x in enumerate((-84.83, -84.67)):
        B(parts, "RADIO_SLOT_%d" % i, 0.07, 0.08, 0.020, (x, -10.62, 1.090), DARK, 0.001)
        B(parts, "RADIO_%d" % i, 0.060, 0.040, 0.180, (x, -10.62, 1.190), BLACK, 0.003)
        C(parts, "RADIO_ANT_%d" % i, 0.004, 0.100, (x, -10.62, 1.330), BLACK, 'Z', 8, 0.0002)
        B(parts, "RADIO_LED_%d" % i, 0.012, 0.012, 0.005, (x, -10.70, 1.100), RED, 0.0002)
        B(parts, "RADIO_KNOB_%d" % i, 0.018, 0.018, 0.012, (x, -10.60, 1.280), DARK, 0.0005)
    # logbook and pen
    B(parts, "LOG_BOOK", 0.30, 0.22, 0.020, (-84.55, -10.95, 1.030), PAPER, 0.001)
    B(parts, "LOG_BOARD", 0.32, 0.24, 0.008, (-84.55, -10.95, 1.016), MANILA, 0.001)
    B(parts, "LOG_CLIP", 0.050, 0.030, 0.012, (-84.55, -11.045, 1.045), CHROME, 0.001)
    C(parts, "LOG_PEN", 0.006, 0.145, (-84.60, -10.90, 1.050), BLACK, 'Y', 8, 0.0003)
    # mug
    C(parts, "MUG_BODY", 0.040, 0.090, (-84.15, -10.95, 1.065), CERAMIC, 'Z', 24, 0.001)
    B(parts, "MUG_HANDLE", 0.020, 0.050, 0.060, (-84.10, -10.95, 1.065), CERAMIC, 0.004)
    C(parts, "MUG_COFFEE", 0.034, 0.006, (-84.15, -10.95, 1.107), EDGE, 'Z', 24, 0.0002)


def add_chair():
    src = bpy.data.objects.get("REC06_CHAIR_HERO")
    if src is None:
        print("CHAIR_SOURCE_MISSING")
        return None
    bb = [src.matrix_world @ Vector(c) for c in src.bound_box]
    center = sum(bb, Vector()) / 8.0
    chair = src.copy()
    chair.data = src.data
    chair.name = "REC07_SECURITY_CHAIR_HERO"
    for c in list(chair.users_collection):
        c.objects.unlink(chair)
    R7.objects.link(chair)
    # Rotar solo en Z alrededor del centro XY; conservar la altura original.
    pivot = Vector((center.x, center.y, 0.0))
    chair.matrix_world = (Matrix.Translation((-82.75, -10.80, 0.0)) @
                          Matrix.Rotation(math.radians(90), 4, 'Z') @
                          Matrix.Translation(-pivot) @ src.matrix_world)
    chair.hide_render = False
    chair.hide_viewport = False
    chair.hide_set(False)
    return chair


def stats(ob):
    me = ob.data
    me.calc_loop_triangles()
    bm = bmesh.new()
    bm.from_mesh(me)
    nonman = sum(1 for e in bm.edges if not e.is_manifold)
    degen = sum(1 for f in bm.faces if f.calc_area() < 1e-9)
    bm.free()
    return {
        "tris": len(me.loop_triangles),
        "verts": len(me.vertices),
        "polys": len(me.polygons),
        "non_manifold": nonman,
        "degenerate": degen,
        "uv": len(me.uv_layers) > 0,
        "hide_render": bool(ob.hide_render),
    }


def bbox_of(objs):
    pts = []
    for ob in objs:
        for c in ob.bound_box:
            pts.append(ob.matrix_world @ Vector(c))
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return [round(v, 4) for v in mn], [round(v, 4) for v in mx]


def main():
    if os.path.exists(BLEND) and not os.path.exists(BACKUP):
        shutil.copy2(BLEND, BACKUP)
        print("BACKUP", BACKUP)
    clean_r7()
    retired = retire_old()

    desk_parts = []
    add_desk(desk_parts)
    desk = join_group(R7, "REC07_SECURITY_DESK_HERO", desk_parts, uv=True, wn=True)

    equip_parts = []
    add_equipment(equip_parts)
    equip = join_group(R7, "REC07_SECURITY_EQUIPMENT_HERO", equip_parts, uv=True, wn=True)

    # join_group conserva la colección del objeto activo (Scene Collection).
    # Forzar que las tres mallas vivan en R7 para que el render y el export las vean.
    for hero in (desk, equip):
        for coll in list(hero.users_collection):
            coll.objects.unlink(hero)
        R7.objects.link(hero)
        hero.hide_render = False
        hero.hide_viewport = False
        hero.hide_set(False)

    chair = add_chair()
    bpy.context.view_layer.update()

    objs = [desk, equip] + ([chair] if chair else [])
    report = {
        "collection": R7_NAME,
        "retired": retired,
        "retired_count": len(retired),
        "objects": {},
        "total_tris": 0,
    }
    for ob in objs:
        st = stats(ob)
        report["objects"][ob.name] = st
        report["total_tris"] += st["tris"]
    mn, mx = bbox_of(objs)
    report["bbox_min"] = mn
    report["bbox_max"] = mx
    with open(QA, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)

    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("REC07_DONE", report["total_tris"], len(objs), len(retired), True)
    for name, st in report["objects"].items():
        print(name, st)


main()
