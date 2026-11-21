"""CCTV video wall, support structure and cable trays for the operations centre."""
import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

import fm_ops_lib as L


WALL_Y = 35.845
CENTER_X = -85.40
CENTER_Z = 2.42
COLS = (-0.98, 0.0, 0.98)
ROWS = (0.64, 0.0, -0.64)


def _screen(prefix, center, mat, coll, screen_mat, tilt_deg=4.0, ui=True,
            tilt_extra=0.0):
    parts = []
    parts.append(L.box(prefix + "_Chassis", (0.860, 0.060, 0.500), (0, 0.035, 0),
                       mat["M_HERO_Steel_Dark"], coll, bevel=0.008, seg=4))
    parts.append(L.box(prefix + "_BackBulge", (0.300, 0.045, 0.240), (0, 0.080, 0.020),
                       mat["M_HERO_Steel_Dark"], coll, bevel=0.010, seg=3))
    parts.append(L.box(prefix + "_BezelT", (0.796, 0.030, 0.042), (0, -0.005, 0.249),
                       mat["M_HERO_Plastic"], coll, bevel=0.006, seg=3))
    parts.append(L.box(prefix + "_BezelB", (0.796, 0.030, 0.042), (0, -0.005, -0.249),
                       mat["M_HERO_Plastic"], coll, bevel=0.006, seg=3))
    parts.append(L.box(prefix + "_BezelL", (0.042, 0.030, 0.420), (-0.419, -0.005, 0),
                       mat["M_HERO_Plastic"], coll, bevel=0.006, seg=3))
    parts.append(L.box(prefix + "_BezelR", (0.042, 0.030, 0.420), (0.419, -0.005, 0),
                       mat["M_HERO_Plastic"], coll, bevel=0.006, seg=3))
    # screen sits 8-9 mm behind the bezel front, no separate lip bars
    parts.append(L.box(prefix + "_Screen", (0.795, 0.004, 0.438), (0, -0.009, 0),
                       screen_mat, coll, bevel=0.0, seg=1, smooth=False))
    if ui:
        parts.append(L.box(prefix + "_UI_Side", (0.040, 0.003, 0.400), (-0.335, -0.0125, 0),
                           mat["screen_ui"], coll, bevel=0.0, seg=1, smooth=False))
        parts.append(L.box(prefix + "_UI_Bar", (0.710, 0.003, 0.010), (0.020, -0.0125, -0.196),
                           mat["screen_ui"], coll, bevel=0.0, seg=1, smooth=False))
        parts.append(L.box(prefix + "_UI_Line", (0.500, 0.003, 0.004), (0.060, -0.0125, 0.180),
                           mat["screen_ui"], coll, bevel=0.0, seg=1, smooth=False))
        for i in range(3):
            parts.append(L.box(f"{prefix}_UI_Pip{i}", (0.010, 0.004, 0.010),
                               (-0.322, -0.0145, 0.150 - i * 0.030), mat["ops_green"], coll,
                               bevel=0.0, seg=1, smooth=False))
    # top vents, sunk into the chassis roof
    for i in range(6):
        parts.append(L.box(f"{prefix}_Vent{i}", (0.500, 0.012, 0.008),
                           (0, -0.020 + i * 0.016, 0.249), mat["M_HERO_Plastic"], coll,
                           bevel=0.001, seg=1))
    # back bracket pads, bezel bolts, badge
    for x in (-0.190, 0.190):
        parts.append(L.box(f"{prefix}_Pad{x}", (0.070, 0.020, 0.070), (x, 0.074, 0.020),
                           mat["M_HERO_Steel_Bare"], coll, bevel=0.003, seg=2))
    parts.append(L.box(prefix + "_Badge", (0.060, 0.004, 0.012), (0, -0.020, -0.226),
                       mat["M_HERO_Aluminum"], coll, bevel=0.001, seg=2))
    ob = L.join(parts, prefix, coll)
    m = (Matrix.Translation(Vector(center)) @
         Matrix.Rotation(math.radians(tilt_deg + tilt_extra), 4, "X"))
    L.transform_objects([ob], m)
    L.weighted_normal(ob)
    return ob


def build_cctv(mat, coll):
    objs = []
    # backing plate and structural frame
    support = []
    support.append(L.box("R21A_CCTV_Backplate", (3.400, 0.050, 2.250),
                         (CENTER_X, WALL_Y - 0.027, CENTER_Z), mat["olive_dark"], coll,
                         bevel=0.008, seg=3))
    for x in (-1.300, 0.0, 1.300):
        support.append(L.box(f"R21A_CCTV_VRail{x}", (0.070, 0.130, 2.180),
                             (CENTER_X + x, WALL_Y - 0.065, CENTER_Z),
                             mat["M_HERO_Galvanized"], coll, bevel=0.005, seg=3))
    for z in (-1.000, 0.0, 1.000):
        support.append(L.box(f"R21A_CCTV_HRail{z}", (3.250, 0.110, 0.070),
                             (CENTER_X, WALL_Y - 0.065, CENTER_Z + z),
                             mat["M_HERO_Galvanized"], coll, bevel=0.005, seg=3))
    # diagonal braces, embedded into the backplate
    for sx in (-1, 1):
        support.append(L.box(f"R21A_CCTV_Brace{sx}", (0.050, 0.060, 1.250),
                             (CENTER_X + sx * 1.430, WALL_Y - 0.075, CENTER_Z),
                             mat["M_HERO_Steel_Dark"], coll,
                             rot=(0, sx * math.radians(16), 0), bevel=0.004, seg=2))
    objs.append(L.join(support, "R21A_CCTV_Support", coll))

    # nine monitors
    screen_keys = ["screen_dead_ops", "screen_glow", "screen_scan",
                   "M_HERO_Screen_Cracked", "screen_glow_dim", "screen_dead_ops",
                   "screen_glow", "screen_glow_dim", "M_HERO_Screen_Cracked"]
    tilts = [4, 4, 4, 4, 4, 6.5, 4, 4, 5]
    brackets = []
    for idx, (cx, cz) in enumerate([(c, r) for r in ROWS for c in COLS]):
        x = CENTER_X + cx
        z = CENTER_Z + cz
        center = (x, WALL_Y - 0.230, z)
        skey = screen_keys[idx]
        ui = skey not in ("M_HERO_Screen_Dead", "M_HERO_Screen_Cracked")
        name = f"R21A_CCTV_Screen_{idx:02d}"
        objs.append(_screen(name, center, mat, coll, mat[skey], tilt_deg=tilts[idx], ui=ui))
        # one solid mounting bracket per screen, from chassis back to the wall rail
        brackets.append(L.box(f"{name}_Bracket", (0.250, 0.160, 0.090),
                              (x, WALL_Y - 0.160, z), mat["M_HERO_Steel_Dark"],
                              coll, bevel=0.004, seg=3))
        brackets.append(L.box(f"{name}_BracketFoot", (0.300, 0.040, 0.140),
                              (x, WALL_Y - 0.085, z), mat["M_HERO_Galvanized"],
                              coll, bevel=0.003, seg=2))
    objs.append(L.join(brackets, "R21A_CCTV_Brackets", coll))

    # simple engraved camera-number plates under each monitor (no floating text islands)
    labels = []
    for idx, (cx, cz) in enumerate([(c, r) for r in ROWS for c in COLS]):
        labels.append(L.box(f"R21A_CCTV_Label_{idx:02d}", (0.200, 0.008, 0.045),
                            (CENTER_X + cx, WALL_Y - 0.055, CENTER_Z + cz - 0.335),
                            mat["label"], coll, bevel=0.0015, seg=2))
        labels.append(L.box(f"R21A_CCTV_LabelMark_{idx:02d}", (0.080, 0.002, 0.010),
                            (CENTER_X + cx, WALL_Y - 0.060, CENTER_Z + cz - 0.335),
                            mat["M_HERO_Paint_Dark"], coll, bevel=0.0, seg=1,
                            smooth=False))
    objs.append(L.join(labels, "R21A_CCTV_Labels", coll))

    # overhead cable tray along the wall to the rack
    tray = []
    tray_x0, tray_x1 = CENTER_X - 1.85, -77.70
    length = tray_x1 - tray_x0
    mid = (tray_x0 + tray_x1) * 0.5
    tray.append(L.box("R21A_CCTV_TrayBottom", (length, 0.280, 0.020), (mid, WALL_Y - 0.320, 3.620),
                      mat["M_HERO_Galvanized"], coll, bevel=0.004, seg=2))
    for sy in (-1, 1):
        tray.append(L.box(f"R21A_CCTV_TraySide{sy}", (length, 0.016, 0.090),
                          (mid, WALL_Y - 0.320 + sy * 0.140, 3.665), mat["M_HERO_Galvanized"],
                          coll, bevel=0.003, seg=2))
    for i in range(int(length / 0.55) + 1):
        x = tray_x0 + i * 0.55
        tray.append(L.box(f"R21A_CCTV_TrayRung{i}", (0.035, 0.260, 0.014),
                          (x, WALL_Y - 0.320, 3.632), mat["M_HERO_Steel_Dark"], coll,
                          bevel=0.002, seg=1))
    # hangers
    for i in range(5):
        x = tray_x0 + 0.4 + i * (length - 0.8) / 4.0
        tray.append(L.cyl(f"R21A_CCTV_Hanger{i}", 0.008, 1.080, (x, WALL_Y - 0.320, 4.240),
                          mat["M_HERO_Steel_Bare"], coll, segments=8, bevel=0.001))
        tray.append(L.cyl(f"R21A_CCTV_HangerNut{i}", 0.019, 0.020, (x, WALL_Y - 0.320, 3.700),
                          mat["M_HERO_Steel_Bare"], coll, segments=6, bevel=0.001))
        tray.append(L.box(f"R21A_CCTV_HangerPlate{i}", (0.060, 0.300, 0.012),
                          (x, WALL_Y - 0.320, 3.610), mat["M_HERO_Steel_Dark"], coll,
                          bevel=0.002, seg=1))
    objs.append(L.join(tray, "R21A_CCTV_CableTray", coll))

    # cables: drops from the top row into the tray, dangling tails under broken screens
    cables = []
    rnd = random.Random(8)
    for idx, (cx, cz) in enumerate([(c, r) for r in ROWS for c in COLS]):
        x = CENTER_X + cx
        z = CENTER_Z + cz
        if cz > 0.5:
            for k in range(2):
                p0 = (x + (k - 0.5) * 0.05, WALL_Y - 0.260, z + 0.220)
                p1 = (x + (k - 0.5) * 0.09, WALL_Y - 0.330, 3.630)
                cables.append(L.cable(f"R21A_CCTV_Drop_{idx}_{k}", p0, p1, 0.24, 0.0055,
                                      mat["M_HERO_Rubber"] if k == 0 else mat["cable_blue"],
                                      coll, n=18, sides=7, wiggle=0.02, seed=idx * 3 + k))
        if idx in (2, 5, 8):
            # torn cable tail hanging from the bottom bezel, starting inside the chassis
            p0 = (x + 0.10, WALL_Y - 0.190, z - 0.200)
            p1 = (x - 0.05 + rnd.uniform(-0.05, 0.05), WALL_Y - 0.290, z - 1.05)
            cables.append(L.cable(f"R21A_CCTV_Tail_{idx}", p0, p1, 0.10, 0.006,
                                  mat["M_HERO_Rubber"], coll, n=14, sides=7, wiggle=0.04,
                                  seed=idx + 40))

    # one consolidated bundle in the tray, dropping into the rack top
    p0 = (CENTER_X - 1.60, WALL_Y - 0.340, 3.640)
    p1 = (-77.70, WALL_Y - 0.340, 3.635)
    p2 = (-77.70, WALL_Y - 0.260, 2.020)
    pts = [p0, ((p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5, 3.650), p1, p2]
    cables.append(L.tube("R21A_CCTV_Bundle", pts, 0.022, mat["M_HERO_Rubber"], coll, sides=10))
    p3 = (CENTER_X - 1.60, WALL_Y - 0.300, 3.638)
    p4 = (-77.74, WALL_Y - 0.300, 3.638)
    p5 = (-77.74, WALL_Y - 0.230, 2.040)
    cables.append(L.tube("R21A_CCTV_BundleData",
                         [p3, ((p3[0] + p4[0]) * 0.5, (p3[1] + p4[1]) * 0.5, 3.638), p4, p5],
                         0.008, mat["cable_blue"], coll, sides=7))
    objs.append(L.join(cables, "R21A_CCTV_Cables", coll))

    # wall signage
    sign = []
    sign.append(L.box("R21A_CCTV_SignPlate", (2.300, 0.012, 0.180), (CENTER_X, WALL_Y - 0.062, 1.205),
                      mat["M_HERO_Paint_Dark"], coll, bevel=0.003, seg=2))
    sign.append(L.box("R21A_CCTV_SignRail", (2.300, 0.014, 0.018), (CENTER_X, WALL_Y - 0.070, 1.300),
                      mat["M_HERO_Aluminum"], coll, bevel=0.002, seg=2))
    sign.append(L.text_mesh("R21A_CCTV_SignText", "CENTRO DE VIGILANCIA", 0.075,
                            (CENTER_X, WALL_Y - 0.0685, 1.205), (math.radians(90), 0, 0),
                            mat["label"], coll, extrude=0.0012))
    sign.append(L.text_mesh("R21A_CCTV_SignSub", "NEXUS // CCTV-03", 0.030,
                            (CENTER_X, WALL_Y - 0.0685, 1.128), (math.radians(90), 0, 0),
                            mat["M_HERO_LED_Amber"], coll, extrude=0.0008))
    objs.append(L.join(sign, "R21A_CCTV_Sign", coll))
    return objs
