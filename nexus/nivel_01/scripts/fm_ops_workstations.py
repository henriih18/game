"""Workstations, chairs, monitors and desk equipment for the security operations centre."""
import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

import fm_ops_lib as L


# --------------------------------------------------------------------------------------
# small equipment
# --------------------------------------------------------------------------------------
def _mouse(prefix, origin, mat, coll, rot_z=0.0):
    parts = []
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=1.0)
    for v in bm.verts:
        v.co.x *= 0.034
        v.co.y *= 0.058
        v.co.z *= 0.022
        if v.co.z < -0.002:
            v.co.z = -0.002
    me = bpy.data.meshes.new(prefix + "_Shell")
    L._finish_bm(bm, me, smooth=True, sharp_angle=60)
    L._box_uv(me)
    parts.append(L._link(prefix + "_Shell", me, coll, mat["M_HERO_Plastic"], (0, 0, 0.023)))
    parts.append(L.box(prefix + "_BtnL", (0.028, 0.045, 0.008), (-0.016, 0.020, 0.041),
                       mat["M_HERO_Plastic"], coll, bevel=0.0025, seg=3))
    parts.append(L.box(prefix + "_BtnR", (0.028, 0.045, 0.008), (0.016, 0.020, 0.041),
                       mat["M_HERO_Plastic"], coll, bevel=0.0025, seg=3))
    parts.append(L.cyl(prefix + "_Wheel", 0.011, 0.008, (0, 0.030, 0.042), mat["M_HERO_Rubber"],
                       coll, rot=(0, math.radians(90), 0), segments=16, bevel=0.0015))
    parts.append(L.box(prefix + "_Seam", (0.002, 0.050, 0.001), (0, 0.020, 0.045),
                       mat["M_HERO_Steel_Dark"], coll, bevel=0.0004, seg=1))
    ob = L.join(parts, prefix, coll)
    L.transform_objects([ob], Matrix.Translation(origin) @ Matrix.Rotation(rot_z, 4, "Z"))
    L.weighted_normal(ob)
    return ob


def _keyboard(prefix, origin, mat, coll, rot_z=0.0, cable_end=(0.62, 0.20, 0.003)):
    parts = []
    parts.append(L.box(prefix + "_Body", (0.445, 0.160, 0.022), (0, 0, 0.011),
                       mat["M_HERO_Plastic"], coll, bevel=0.004, seg=4))
    parts.append(L.box(prefix + "_Riser", (0.425, 0.022, 0.014), (0, 0.064, 0.028),
                       mat["M_HERO_Plastic"], coll, bevel=0.002, seg=2))
    # keycaps
    keys = []
    key_w, key_gap = 0.024, 0.004
    rows = [
        (0.050, 14), (0.022, 14), (-0.006, 14), (-0.034, 13), (-0.060, 12),
    ]
    for ri, (y, count) in enumerate(rows):
        total = count * key_gap + (count - 1) * key_gap
        x0 = -((count - 1) * (key_w + key_gap)) * 0.5
        for i in range(count):
            keys.append((x0 + i * (key_w + key_gap), y))
    # space bar replaces last row centre
    key_objs = []
    for i, (x, y) in enumerate(keys):
        if i >= len(keys) - 12:
            continue
        key_objs.append(L.box(f"{prefix}_Key_{i}", (key_w, key_w, 0.012),
                              (x, y, 0.025), mat["keycap"], coll,
                              bevel=0.0018, seg=2))
    key_objs.append(L.box(prefix + "_Space", (0.150, 0.022, 0.012), (-0.010, -0.060, 0.025),
                          mat["keycap"], coll, bevel=0.0018, seg=2))
    key_objs.append(L.box(prefix + "_KeyWin", (0.024, 0.022, 0.012), (0.118, -0.060, 0.025),
                          mat["keycap"], coll, bevel=0.0018, seg=2))
    keys_ob = L.join(key_objs, prefix + "_Keys", coll)
    parts.append(keys_ob)

    # cable to grommet
    pts = [(0.0, 0.084, 0.012), (0.02, 0.14, 0.006), (0.20, 0.19, 0.004),
           (cable_end[0] - 0.04, cable_end[1], 0.003), cable_end]
    parts.append(L.tube(prefix + "_Cable", pts, 0.0038, mat["M_HERO_Rubber"], coll, sides=7))
    ob = L.join(parts, prefix, coll)
    L.transform_objects([ob], Matrix.Translation(origin) @ Matrix.Rotation(rot_z, 4, "Z"))
    L.weighted_normal(ob)
    return ob


def _monitor(prefix, origin, mat, coll, screen_mat, rot_z=0.0, cable_end=(0.62, 0.20, 0.002)):
    """27-inch console monitor, screen faces -Y before rotation. Local z=0 is the desk top."""
    parts = []
    parts.append(L.box(prefix + "_Base", (0.300, 0.220, 0.014), (0, 0.010, 0.008),
                       mat["M_HERO_Steel_Dark"], coll, bevel=0.004, seg=4))
    parts.append(L.box(prefix + "_BaseTop", (0.240, 0.180, 0.008), (0, 0.010, 0.018),
                       mat["M_HERO_Aluminum"], coll, bevel=0.003, seg=3))
    parts.append(L.cyl(prefix + "_Swivel", 0.060, 0.014, (0, 0.015, 0.027),
                       mat["M_HERO_Steel_Dark"], coll, segments=28, bevel=0.002, seg=2))
    # neck leans back slightly
    parts.append(L.box(prefix + "_Neck", (0.074, 0.052, 0.235), (0, 0.035, 0.150),
                       mat["M_HERO_Steel_Dark"], coll, bevel=0.005, seg=3))
    parts.append(L.cyl(prefix + "_Hinge", 0.035, 0.130, (0, 0.055, 0.268),
                       mat["M_HERO_Plastic"], coll, rot=(0, math.radians(90), 0),
                       segments=20, bevel=0.002))
    parts.append(L.box(prefix + "_Vesa", (0.140, 0.014, 0.140), (0, 0.075, 0.300),
                       mat["M_HERO_Steel_Dark"], coll, bevel=0.003, seg=3))
    parts.append(L.box(prefix + "_Chassis", (0.620, 0.060, 0.400), (0, 0.105, 0.435),
                       mat["M_HERO_Plastic"], coll, bevel=0.008, seg=4))
    parts.append(L.box(prefix + "_BackBulge", (0.290, 0.035, 0.230), (0, 0.145, 0.440),
                       mat["M_HERO_Plastic"], coll, bevel=0.012, seg=3))
    # bezel ring (front at y=0.070)
    parts.append(L.box(prefix + "_BezelT", (0.568, 0.032, 0.036), (0, 0.062, 0.626),
                       mat["M_HERO_Plastic"], coll, bevel=0.006, seg=3))
    parts.append(L.box(prefix + "_BezelB", (0.568, 0.032, 0.052), (0, 0.062, 0.240),
                       mat["M_HERO_Plastic"], coll, bevel=0.006, seg=3))
    parts.append(L.box(prefix + "_BezelL", (0.036, 0.032, 0.360), (-0.302, 0.062, 0.435),
                       mat["M_HERO_Plastic"], coll, bevel=0.005, seg=3))
    parts.append(L.box(prefix + "_BezelR", (0.036, 0.032, 0.360), (0.302, 0.062, 0.435),
                       mat["M_HERO_Plastic"], coll, bevel=0.005, seg=3))
    # recessed screen
    parts.append(L.box(prefix + "_Screen", (0.575, 0.004, 0.350), (0, 0.044, 0.437),
                       screen_mat, coll, bevel=0.0, seg=1, smooth=False))
    if screen_mat.name not in ("M_HERO_Screen_Dead", "M_HERO_Screen_Cracked",
                               "M_HERO_Ops_ScreenDead"):
        # faint console UI. Layer depths are kept >2 mm apart to avoid coplanar faces.
        parts.append(L.box(prefix + "_UI_Left", (0.010, 0.003, 0.330), (-0.280, 0.0415, 0.437),
                           mat["screen_ui"], coll, bevel=0.0, seg=1, smooth=False))
        parts.append(L.box(prefix + "_UI_Bottom", (0.430, 0.003, 0.007), (0.035, 0.0415, 0.284),
                           mat["screen_ui"], coll, bevel=0.0, seg=1, smooth=False))
        parts.append(L.box(prefix + "_UI_Top", (0.110, 0.003, 0.004), (0.140, 0.0415, 0.592),
                           mat["screen_ui"], coll, bevel=0.0, seg=1, smooth=False))
        for i in range(3):
            parts.append(L.box(f"{prefix}_UI_Pip{i}", (0.020, 0.005, 0.007),
                               (-0.262, 0.0390, 0.350 + i * 0.020), mat["ops_green"], coll,
                               bevel=0.0, seg=1, smooth=False))
    # chin details: buttons, led, badge
    for i in range(4):
        parts.append(L.box(f"{prefix}_Btn{i}", (0.014, 0.006, 0.007),
                           (0.160 + i * 0.024, 0.078, 0.236), mat["M_HERO_Steel_Dark"],
                           coll, bevel=0.0012, seg=2))
    parts.append(L.box(prefix + "_PowerLED", (0.005, 0.004, 0.0025), (0.100, 0.080, 0.236),
                       mat["led_green"], coll, bevel=0.0002, seg=1))
    parts.append(L.box(prefix + "_Badge", (0.060, 0.004, 0.012), (-0.220, 0.079, 0.236),
                       mat["M_HERO_Aluminum"], coll, bevel=0.001, seg=2))
    # rear vents and ports
    parts.append(L.box(prefix + "_VentBack", (0.160, 0.004, 0.120), (0.150, 0.166, 0.435),
                       mat["M_HERO_Steel_Dark"], coll, bevel=0.001, seg=1))
    for i in range(7):
        parts.append(L.box(f"{prefix}_VentSlat{i}", (0.150, 0.004, 0.007),
                           (0.150, 0.169, 0.385 + i * 0.017), mat["M_HERO_Plastic"],
                           coll, bevel=0.001, seg=1))
    for i in range(3):
        parts.append(L.box(f"{prefix}_Port{i}", (0.030, 0.020, 0.014), (-0.060 + i * 0.038, 0.128, 0.300),
                           mat["M_HERO_Steel_Dark"], coll, bevel=0.0015, seg=2))
    # power/data cable
    pts = [(0.080, 0.150, 0.250), (0.100, 0.200, 0.100), (0.130, 0.240, 0.020),
           (cable_end[0] - 0.08, cable_end[1], 0.006), cable_end]
    parts.append(L.tube(prefix + "_Cable", pts, 0.0050, mat["M_HERO_Rubber"], coll, sides=8))
    ob = L.join(parts, prefix, coll)
    L.transform_objects([ob], Matrix.Translation(origin) @ Matrix.Rotation(rot_z, 4, "Z"))
    L.weighted_normal(ob)
    return ob


def _radio(prefix, origin, mat, coll, rot_z=0.0):
    """Desktop radio transceiver with speaker grille, LCD, knobs, handset and coiled cord."""
    parts = []
    parts.append(L.box(prefix + "_Base", (0.360, 0.230, 0.055), (0, 0, 0.028),
                       mat["M_HERO_Plastic"], coll, bevel=0.008, seg=3))
    # sloped front face
    parts.append(L.box(prefix + "_Face", (0.350, 0.170, 0.130), (0, -0.040, 0.110),
                       mat["olive_dark"], coll, rot=(math.radians(-16), 0, 0),
                       bevel=0.006, seg=3))
    # speaker grille bars
    for i in range(9):
        parts.append(L.box(f"{prefix}_Grille{i}", (0.115, 0.006, 0.006),
                           (-0.105, -0.120, 0.074 + i * 0.010), mat["grille"], coll,
                           bevel=0.0008, seg=1))
    # LCD
    parts.append(L.box(prefix + "_LCDBezel", (0.100, 0.008, 0.052), (0.020, -0.124, 0.132),
                       mat["M_HERO_Steel_Dark"], coll, bevel=0.002, seg=2))
    parts.append(L.box(prefix + "_LCD", (0.082, 0.003, 0.036), (0.020, -0.129, 0.132),
                       mat["screen_glow_dim"], coll, bevel=0.0, seg=1, smooth=False))
    # channel knob + volume knob
    for i, (x, z) in enumerate(((-0.112, 0.134), (-0.062, 0.134))):
        parts.append(L.cyl(f"{prefix}_Knob{i}", 0.020, 0.020, (x, -0.132, z),
                           mat["M_HERO_Steel_Dark"], coll, rot=(math.radians(90), 0, 0),
                           segments=18, bevel=0.0015))
        parts.append(L.box(f"{prefix}_KnobMark{i}", (0.003, 0.002, 0.012), (x, -0.143, z + 0.006),
                           mat["M_HERO_Aluminum"], coll, bevel=0.0, seg=1))
    # buttons sit on the sloped face and are embedded 5 mm into it
    for i in range(4):
        parts.append(L.box(f"{prefix}_Btn{i}", (0.016, 0.012, 0.010), (0.070 + i * 0.022, -0.106, 0.162),
                           mat["M_HERO_Steel_Dark"], coll, rot=(math.radians(-16), 0, 0),
                           bevel=0.001, seg=1))
    # antenna
    parts.append(L.cyl(prefix + "_AntBase", 0.012, 0.025, (0.145, 0.075, 0.060),
                       mat["M_HERO_Steel_Dark"], coll, segments=12, bevel=0.001))
    parts.append(L.cyl(prefix + "_Antenna", 0.0045, 0.300, (0.145, 0.075, 0.220),
                       mat["M_HERO_Rubber"], coll, segments=8, bevel=0.001))
    # handset cradle and handset on right side
    parts.append(L.box(prefix + "_Cradle", (0.060, 0.190, 0.035), (0.192, 0.0, 0.060),
                       mat["M_HERO_Plastic"], coll, bevel=0.004, seg=2))
    parts.append(L.box(prefix + "_Handset", (0.046, 0.190, 0.048), (0.218, 0.0, 0.115),
                       mat["M_HERO_Plastic"], coll, bevel=0.012, seg=4))

    # coiled cord
    parts.append(L.coil(prefix + "_Cord", (0.218, 0.098, 0.100), (0, 0, -1), 0.020, 0.010,
                        4.5, 0.003, mat["M_HERO_Rubber"], coll, n=12, sides=6))
    parts.append(L.tube(prefix + "_CordLead", [(0.218, 0.098, 0.055), (0.240, 0.110, 0.030),
                                               (0.205, 0.130, 0.008)], 0.003,
                        mat["M_HERO_Rubber"], coll, sides=6))
    # small nameplate on the base (metal plate, no floating text)
    parts.append(L.box(prefix + "_NamePlate", (0.090, 0.006, 0.018), (0.010, -0.116, 0.035),
                       mat["M_HERO_Aluminum"], coll, bevel=0.0015, seg=2))
    ob = L.join(parts, prefix, coll)
    L.transform_objects([ob], Matrix.Translation(origin) @ Matrix.Rotation(rot_z, 4, "Z"))
    L.weighted_normal(ob)
    return ob


def _ptz(prefix, origin, mat, coll, rot_z=0.0):
    """CCTV PTZ joystick controller."""
    parts = []
    parts.append(L.box(prefix + "_Base", (0.220, 0.165, 0.040), (0, 0, 0.022),
                       mat["M_HERO_Plastic"], coll, bevel=0.007, seg=3))
    parts.append(L.box(prefix + "_Face", (0.200, 0.140, 0.012), (0, -0.005, 0.045),
                       mat["olive_dark"], coll, rot=(math.radians(-7), 0, 0), bevel=0.004, seg=2))
    # joystick
    parts.append(L.cyl(prefix + "_StickBoot", 0.030, 0.022, (-0.045, -0.020, 0.049),
                       mat["M_HERO_Rubber"], coll, segments=18, bevel=0.003))
    parts.append(L.cyl(prefix + "_Stick", 0.007, 0.060, (-0.045, -0.020, 0.075),
                       mat["M_HERO_Steel_Bare"], coll, segments=10, bevel=0.001))
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=0.018)
    me = bpy.data.meshes.new(prefix + "_Knob")
    L._finish_bm(bm, me, smooth=True, sharp_angle=60)
    L._box_uv(me)
    parts.append(L._link(prefix + "_Knob", me, coll, mat["M_HERO_Rubber"], (-0.045, -0.020, 0.105)))
    # display
    parts.append(L.box(prefix + "_LCDBezel", (0.072, 0.040, 0.010), (0.055, -0.045, 0.054),
                       mat["M_HERO_Steel_Dark"], coll, bevel=0.002, seg=2))
    parts.append(L.box(prefix + "_LCD", (0.058, 0.026, 0.003), (0.055, -0.045, 0.060),
                       mat["screen_glow_dim"], coll, bevel=0.0, seg=1, smooth=False))
    parts.append(L.text_mesh(prefix + "_Label", "PTZ", 0.018, (-0.030, 0.060, 0.056),
                             (math.radians(-7), 0, 0), mat["label"], coll, extrude=0.0006))
    parts.append(L.tube(prefix + "_Cable", [(0.0, 0.080, 0.010), (0.05, 0.115, 0.006),
                                            (0.16, 0.150, 0.004)], 0.003,
                        mat["M_HERO_Rubber"], coll, sides=6))
    ob = L.join(parts, prefix, coll)
    L.transform_objects([ob], Matrix.Translation(origin) @ Matrix.Rotation(rot_z, 4, "Z"))
    L.weighted_normal(ob)
    return ob


def _phone(prefix, origin, mat, coll, rot_z=0.0):
    parts = []
    parts.append(L.box(prefix + "_Base", (0.210, 0.180, 0.045), (0, 0, 0.024),
                       mat["M_HERO_Plastic"], coll, bevel=0.008, seg=3))
    parts.append(L.box(prefix + "_Face", (0.185, 0.150, 0.012), (0, -0.012, 0.050),
                       mat["olive_dark"], coll, bevel=0.004, seg=2))
    parts.append(L.box(prefix + "_LCDBezel", (0.090, 0.045, 0.010), (-0.035, 0.020, 0.058),
                       mat["M_HERO_Steel_Dark"], coll, bevel=0.002, seg=2))
    parts.append(L.box(prefix + "_LCD", (0.074, 0.030, 0.003), (-0.035, 0.020, 0.064),
                       mat["screen_glow_dim"], coll, bevel=0.0, seg=1, smooth=False))
    # keypad 3x4
    for r in range(4):
        for c in range(3):
            parts.append(L.box(f"{prefix}_Key{r}{c}", (0.020, 0.014, 0.004),
                               (0.035 + c * 0.026, 0.055 - r * 0.022, 0.057),
                               mat["M_HERO_Plastic"], coll, bevel=0.0012, seg=1))
    # handset
    parts.append(L.box(prefix + "_Handset", (0.200, 0.052, 0.042), (0, 0.088, 0.070),
                       mat["M_HERO_Plastic"], coll, bevel=0.014, seg=4))

    parts.append(L.box(prefix + "_Hook", (0.020, 0.030, 0.040), (0, 0.108, 0.040),
                       mat["M_HERO_Plastic"], coll, bevel=0.003, seg=2))
    parts.append(L.coil(prefix + "_Cord", (-0.085, 0.100, 0.045), (0, -0.1, -0.25),
                        0.018, 0.009, 4.0, 0.0028, mat["M_HERO_Rubber"], coll, n=12, sides=6))
    ob = L.join(parts, prefix, coll)
    L.transform_objects([ob], Matrix.Translation(origin) @ Matrix.Rotation(rot_z, 4, "Z"))
    L.weighted_normal(ob)
    return ob


# --------------------------------------------------------------------------------------
# desk
# --------------------------------------------------------------------------------------
def _desk_shell(prefix, mat, coll):
    parts = []
    # top split into main field + rear cable lid with a 5 mm service gap
    parts.append(L.box(prefix + "_Top", (2.100, 0.700, 0.055), (0, -0.040, 0.745),
                       mat["laminate"], coll, bevel=0.006, seg=4))
    parts.append(L.box(prefix + "_TopRail", (2.000, 0.100, 0.030), (0, 0.300, 0.712),
                       mat["M_HERO_Steel_Dark"], coll, bevel=0.003, seg=2))
    parts.append(L.box(prefix + "_CableLid", (2.100, 0.100, 0.020), (0, 0.365, 0.735),
                       mat["M_HERO_Steel_Dark"], coll, bevel=0.004, seg=3))
    # edge banding
    parts.append(L.box(prefix + "_EdgeF", (2.100, 0.014, 0.038), (0, -0.397, 0.737),
                       mat["M_HERO_Rubber"], coll, bevel=0.004, seg=3))
    parts.append(L.box(prefix + "_EdgeL", (0.014, 0.700, 0.038), (-1.055, -0.040, 0.737),
                       mat["M_HERO_Rubber"], coll, bevel=0.004, seg=3))
    parts.append(L.box(prefix + "_EdgeR", (0.014, 0.700, 0.038), (1.055, -0.040, 0.737),
                       mat["M_HERO_Rubber"], coll, bevel=0.004, seg=3))
    # side panels with applied inset panels
    for side, sx in (("L", -1.020), ("R", 1.020)):
        parts.append(L.box(prefix + f"_Side{side}", (0.036, 0.720, 0.660), (sx, 0.010, 0.385),
                           mat["olive"], coll, bevel=0.006, seg=3))
        parts.append(L.box(prefix + f"_SideInset{side}", (0.008, 0.560, 0.470),
                           (sx + (0.018 if side == "R" else -0.018), 0.010, 0.390),
                           mat["olive_dark"], coll, bevel=0.004, seg=3))
        parts.append(L.box(prefix + f"_SideRail{side}", (0.010, 0.600, 0.030),
                           (sx + (0.018 if side == "R" else -0.018), 0.010, 0.660),
                           mat["M_HERO_Steel_Dark"], coll, bevel=0.002, seg=2))
        # adjustable feet
        for fy in (-0.300, 0.320):
            parts.append(L.cyl(f"{prefix}_Foot{side}{fy}", 0.028, 0.040, (sx, fy, 0.023),
                               mat["M_HERO_Steel_Dark"], coll, segments=16, bevel=0.002))
            parts.append(L.cyl(f"{prefix}_FootPad{side}{fy}", 0.036, 0.010, (sx, fy, 0.005),
                               mat["M_HERO_Rubber"], coll, segments=20, bevel=0.003))
        parts.append(L.bolts(prefix + f"_SideBolts{side}",
                             [(sx + (0.030 if side == "R" else -0.030), 0.010 + dy, 0.010 + dz)
                              for dy in (-0.245, 0.245) for dz in (0.220, 0.470)],
                             ((1 if side == "R" else -1), 0, 0), 0.006, 0.008,
                             mat["M_HERO_Steel_Bare"], coll))
    # rear modesty panels
    parts.append(L.box(prefix + "_Back", (1.960, 0.030, 0.500), (0, 0.382, 0.380),
                       mat["olive"], coll, bevel=0.004, seg=3))
    for i, x in enumerate((-0.650, 0.0, 0.650)):
        parts.append(L.box(f"{prefix}_BackInset{i}", (0.590, 0.010, 0.360), (x, 0.400, 0.380),
                           mat["olive_dark"], coll, bevel=0.003, seg=2))
    # vent on the rear right panel
    parts.append(L.box(prefix + "_BackVentFrame", (0.220, 0.010, 0.150), (0.650, 0.408, 0.380),
                       mat["M_HERO_Steel_Dark"], coll, bevel=0.002, seg=2))
    for i in range(7):
        parts.append(L.box(f"{prefix}_BackVentSlat{i}", (0.190, 0.008, 0.008),
                           (0.650, 0.411, 0.330 + i * 0.016), mat["M_HERO_Steel_Bare"],
                           coll, bevel=0.001, seg=1))
    # front beam and status strip
    parts.append(L.box(prefix + "_FrontBeam", (1.960, 0.050, 0.110), (0, -0.370, 0.672),
                       mat["M_HERO_Steel_Dark"], coll, bevel=0.005, seg=3))
    parts.append(L.box(prefix + "_StatusStrip", (0.280, 0.008, 0.007), (-0.620, -0.398, 0.690),
                       mat["ops_amber"], coll, bevel=0.0, seg=1))
    parts.append(L.box(prefix + "_StatusStrip2", (0.150, 0.008, 0.007), (-0.350, -0.398, 0.690),
                       mat["ops_green"], coll, bevel=0.0, seg=1))
    # underside cable tray
    parts.append(L.box(prefix + "_Tray", (1.380, 0.170, 0.060), (0, 0.090, 0.610),
                       mat["M_HERO_Galvanized"], coll, bevel=0.004, seg=3))
    for i in range(5):
        parts.append(L.box(f"{prefix}_TraySlot{i}", (0.060, 0.120, 0.008),
                           (-0.500 + i * 0.250, 0.090, 0.578), mat["M_HERO_Steel_Dark"],
                           coll, bevel=0.001, seg=1))
    for x in (-0.620, 0.620):
        parts.append(L.box(f"{prefix}_TrayBracket{x}", (0.030, 0.030, 0.100), (x, 0.155, 0.670),
                           mat["M_HERO_Steel_Dark"], coll, bevel=0.002, seg=2))
    # grommet
    parts.append(L.cyl(prefix + "_GrommetRing", 0.058, 0.014, (0.720, 0.220, 0.776),
                       mat["M_HERO_Rubber"], coll, segments=28, bevel=0.003))
    parts.append(L.cyl(prefix + "_GrommetDisc", 0.040, 0.004, (0.720, 0.220, 0.7845),
                       mat["M_HERO_Steel_Dark"], coll, segments=24, bevel=0.001))
    # under-desk tower (left)
    parts.append(L.box(prefix + "_Tower", (0.210, 0.440, 0.460), (-0.760, 0.040, 0.250),
                       mat["M_HERO_Steel_Dark"], coll, bevel=0.008, seg=3))
    parts.append(L.box(prefix + "_TowerFace", (0.190, 0.014, 0.420), (-0.760, -0.184, 0.255),
                       mat["olive_dark"], coll, bevel=0.004, seg=2))
    for i in range(9):
        parts.append(L.box(f"{prefix}_TowerVent{i}", (0.160, 0.006, 0.006),
                           (-0.760, -0.194, 0.105 + i * 0.015), mat["grille"], coll,
                           bevel=0.0008, seg=1))
    parts.append(L.cyl(prefix + "_TowerButton", 0.012, 0.006, (-0.825, -0.193, 0.420),
                       mat["M_HERO_Aluminum"], coll, rot=(math.radians(90), 0, 0),
                       segments=14, bevel=0.001))
    parts.append(L.box(prefix + "_TowerLED", (0.006, 0.004, 0.004), (-0.700, -0.194, 0.420),
                       mat["led_green"], coll, bevel=0.0, seg=1))
    for x in (-0.840, -0.680):
        for y in (-0.140, 0.220):
            parts.append(L.cyl(f"{prefix}_TowerFoot{x}{y}", 0.016, 0.018, (x, y, 0.009),
                               mat["M_HERO_Rubber"], coll, segments=10, bevel=0.001))
    # label plate
    parts.append(L.box(prefix + "_LabelPlate", (0.190, 0.010, 0.055), (0.760, -0.400, 0.672),
                       mat["M_HERO_Aluminum"], coll, bevel=0.002, seg=2))
    return parts


def build_desk(prefix, origin, mat, coll, monitor_screens, with_phone=True, with_radio=True,
               with_ptz=False, extras=True):
    """monitor_screens: list of (dx, dy, screen_key, rot_deg) in desk-local space."""
    origin = Vector(origin)
    shell = _desk_shell(prefix, mat, coll)
    objs = [L.join(shell, prefix + "_Shell", coll)]
    for i, (dx, dy, skey, rz) in enumerate(monitor_screens):
        objs.append(_monitor(f"{prefix}_Monitor{i}", (dx, dy, 0.774), mat, coll,
                             mat[skey], rot_z=math.radians(rz),
                             cable_end=(0.720, 0.220, 0.003)))
    objs.append(_keyboard(prefix + "_Keyboard", (-0.020, -0.220, 0.774), mat, coll,
                          rot_z=math.radians(-2), cable_end=(0.700, 0.218, 0.003)))
    objs.append(L.box(prefix + "_MousePad", (0.300, 0.250, 0.005), (0.500, -0.270, 0.7745),
                      mat["M_HERO_Rubber"], coll, bevel=0.002, seg=2))
    objs.append(_mouse(prefix + "_Mouse", (0.500, -0.265, 0.777), mat, coll,
                       rot_z=math.radians(-8)))
    if with_phone:
        objs.append(_phone(prefix + "_Phone", (-0.840, -0.180, 0.774), mat, coll,
                           rot_z=math.radians(14)))
    if with_ptz:
        objs.append(_ptz(prefix + "_PTZ", (-0.790, 0.010, 0.774), mat, coll,
                         rot_z=math.radians(-12)))
    if with_radio:
        objs.append(_radio(prefix + "_Radio", (0.840, 0.095, 0.774), mat, coll,
                           rot_z=math.radians(-8)))
    if extras:
        # small cable coil and spare keyboard? keep a service tag plate on the side
        objs.append(L.box(prefix + "_TagPlate", (0.120, 0.006, 0.040), (1.043, -0.210, 0.520),
                          mat["M_HERO_Aluminum"], coll, bevel=0.0015, seg=2))
    # place the whole desk assembly
    L.transform_objects(objs, Matrix.Translation(origin))
    for ob in objs:
        L.weighted_normal(ob)
    return objs


# --------------------------------------------------------------------------------------
# chair
# --------------------------------------------------------------------------------------
def build_chair(prefix, origin, mat, coll, facing_deg=0.0, tipped=False):
    parts = []
    # five-star base
    for i in range(5):
        a = math.radians(90 + i * 72)
        cx, cy = math.cos(a) * 0.155, math.sin(a) * 0.155
        leg = L.box(f"{prefix}_Leg{i}", (0.310, 0.052, 0.038), (cx, cy, 0.060),
                    mat["chair_shell"], coll, rot=(0, 0, a), bevel=0.008, seg=3)
        parts.append(leg)
        ex, ey = math.cos(a) * 0.310, math.sin(a) * 0.310
        parts.append(L.cyl(f"{prefix}_Caster{i}", 0.032, 0.024, (ex, ey, 0.032),
                           mat["M_HERO_Rubber"], coll,
                           rot=(math.radians(90), 0, a + math.radians(90)), segments=18,
                           bevel=0.004))
        parts.append(L.cyl(f"{prefix}_Hub{i}", 0.010, 0.030, (ex, ey, 0.032),
                           mat["M_HERO_Aluminum"], coll,
                           rot=(math.radians(90), 0, a + math.radians(90)), segments=10,
                           bevel=0.001))
        # fork plates
        for side in (-1, 1):
            ox = math.cos(a + math.radians(90)) * 0.020 * side
            oy = math.sin(a + math.radians(90)) * 0.020 * side
            parts.append(L.box(f"{prefix}_Fork{i}{side}", (0.030, 0.012, 0.052),
                               (ex + ox, ey + oy, 0.058), mat["M_HERO_Steel_Dark"], coll,
                               rot=(0, 0, a + math.radians(90)), bevel=0.002, seg=2))
        parts.append(L.cyl(f"{prefix}_Stem{i}", 0.009, 0.050, (ex, ey, 0.082),
                           mat["M_HERO_Steel_Bare"], coll, segments=10, bevel=0.001))
    parts.append(L.cyl(prefix + "_HubCap", 0.060, 0.035, (0, 0, 0.100), mat["chair_shell"],
                       coll, segments=28, bevel=0.006, seg=3))
    # gas cylinder
    parts.append(L.cyl(prefix + "_GasOuter", 0.030, 0.190, (0, 0, 0.200),
                       mat["M_HERO_Steel_Dark"], coll, segments=24, bevel=0.003))
    parts.append(L.cyl(prefix + "_GasInner", 0.016, 0.130, (0, 0, 0.335),
                       mat["M_HERO_Steel_Bare"], coll, segments=20, bevel=0.002))
    # tilt mechanism
    parts.append(L.box(prefix + "_Mech", (0.250, 0.210, 0.060), (0, 0.005, 0.410),
                       mat["M_HERO_Steel_Dark"], coll, bevel=0.006, seg=3))
    parts.append(L.cyl(prefix + "_Lever", 0.007, 0.160, (-0.185, 0.050, 0.400),
                       mat["M_HERO_Steel_Bare"], coll, rot=(math.radians(90), 0, math.radians(15)),
                       segments=10, bevel=0.001))
    parts.append(L.box(prefix + "_LeverKnob", (0.050, 0.030, 0.024), (-0.190, 0.085, 0.400),
                       mat["M_HERO_Plastic"], coll, bevel=0.005, seg=3))
    # seat pan and cushion
    parts.append(L.box(prefix + "_SeatPan", (0.500, 0.470, 0.035), (0, 0, 0.445),
                       mat["chair_shell"], coll, bevel=0.010, seg=3))
    parts.append(L.box(prefix + "_Seat", (0.510, 0.480, 0.080), (0, 0, 0.493),
                       mat["fabric"], coll, bevel=0.028, seg=4))
    parts.append(L.box(prefix + "_SeatSeam", (0.450, 0.004, 0.004), (0, -0.180, 0.520),
                       mat["M_HERO_Steel_Dark"], coll, bevel=0.0006, seg=1))
    # back support rails
    for x in (-0.180, 0.180):
        parts.append(L.box(f"{prefix}_Spine{x}", (0.045, 0.040, 0.420), (x, -0.220, 0.690),
                           mat["M_HERO_Steel_Dark"], coll, rot=(math.radians(8), 0, 0),
                           bevel=0.005, seg=3))
    parts.append(L.box(prefix + "_BackFrame", (0.480, 0.050, 0.610), (0, -0.268, 0.910),
                       mat["chair_shell"], coll, rot=(math.radians(8), 0, 0),
                       bevel=0.020, seg=4))
    parts.append(L.box(prefix + "_Back", (0.440, 0.060, 0.540), (0, -0.300, 0.915),
                       mat["chair_shell"], coll, rot=(math.radians(8), 0, 0),
                       bevel=0.030, seg=4))
    parts.append(L.box(prefix + "_Lumbar", (0.360, 0.050, 0.110), (0, -0.270, 0.700),
                       mat["chair_shell"], coll, rot=(math.radians(8), 0, 0),
                       bevel=0.020, seg=3))
    parts.append(L.box(prefix + "_Headrest", (0.300, 0.060, 0.150), (0, -0.300, 1.245),
                       mat["chair_shell"], coll, rot=(math.radians(8), 0, 0),
                       bevel=0.028, seg=4))
    parts.append(L.box(prefix + "_HeadrestRail", (0.060, 0.030, 0.120), (0, -0.270, 1.180),
                       mat["M_HERO_Steel_Dark"], coll, rot=(math.radians(8), 0, 0),
                       bevel=0.004, seg=2))
    # armrests
    for x in (-0.300, 0.300):
        parts.append(L.box(f"{prefix}_ArmPost{x}", (0.045, 0.090, 0.220), (x, 0.020, 0.560),
                           mat["chair_shell"], coll, bevel=0.008, seg=3))
        parts.append(L.box(f"{prefix}_ArmPad{x}", (0.300, 0.085, 0.040), (x, 0.030, 0.680),
                           mat["M_HERO_Rubber"], coll, bevel=0.012, seg=4))
        parts.append(L.box(f"{prefix}_ArmRail{x}", (0.200, 0.030, 0.020), (x, 0.030, 0.618),
                           mat["M_HERO_Steel_Dark"], coll, bevel=0.003, seg=2))
    # back bolts
    parts.append(L.bolts(prefix + "_BackBolts",
                         [(-0.170, -0.316, 0.700), (0.170, -0.316, 0.700),
                          (-0.170, -0.316, 1.120), (0.170, -0.316, 1.120)],
                         (0, 1, 0), 0.006, 0.008, mat["M_HERO_Steel_Bare"], coll))
    ob = L.join(parts, prefix, coll)
    L.weighted_normal(ob)
    if not tipped:
        L.transform_objects([ob], Matrix.Translation(Vector(origin)) @
                            Matrix.Rotation(math.radians(facing_deg), 4, "Z"))
    else:
        # lie the chair on its left side, then drop it exactly onto the floor
        pivot = Vector((0, 0, 0.50))
        m = (Matrix.Translation(Vector(origin)) @
             Matrix.Rotation(math.radians(facing_deg), 4, "Z") @
             Matrix.Translation(pivot) @
             Matrix.Rotation(math.radians(96), 4, "Y") @
             Matrix.Translation(-pivot))
        ob.matrix_world = m
        bpy.context.view_layer.update()
        lo = min((ob.matrix_world @ Vector(c)).z for c in ob.bound_box)
        ob.matrix_world = Matrix.Translation((0, 0, 0.0015 - lo)) @ ob.matrix_world
    bpy.context.view_layer.update()
    return ob
