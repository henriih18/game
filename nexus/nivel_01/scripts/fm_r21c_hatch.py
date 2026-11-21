"""Service hatch for L1_SECURITY_R21C_HERO (east wall of Security 03).

Integrates a framed service window into the existing wall opening, with a
partially broken glass pane, cracked glazing, a louvred roller shutter in
its housing, a stainless service counter with real cabinet doors, an
intercom, conduit and glass debris.  All geometry is world-space and
overlaps the wall/opening instead of sitting coplanar with it.
"""
import math
import random
import bpy
import bmesh
from mathutils import Vector, Matrix

import fm_ops_lib as L
import fm_r21c_lib as C

WALL_X = -71.15
Y0, Y1 = 10.20, 11.60
Z0, Z1 = 0.0, 2.20


# --------------------------------------------------------------------------------------
# window frame
# --------------------------------------------------------------------------------------
def window_frame(mat, coll):
    parts = []
    fx = -71.17
    depth = 0.18
    # jambs and header, embedded into the wall opening
    parts.append(C.hb("R21C_HATCH_FrameJambS", (depth, 0.100, 2.20),
                      (fx + depth * 0.5, Y0 - 0.02, 1.112), mat["green"], coll,
                      bevel=0.004, seg=3))
    parts.append(C.hb("R21C_HATCH_FrameJambN", (depth, 0.100, 2.20),
                      (fx + depth * 0.5, Y1 + 0.02, 1.112), mat["green"], coll,
                      bevel=0.004, seg=3))
    parts.append(C.hb("R21C_HATCH_FrameHeader", (depth, 1.60, 0.100),
                      (fx + depth * 0.5, (Y0 + Y1) * 0.5, 2.15), mat["green"], coll,
                      bevel=0.004, seg=3))
    # reveal liners inside the wall thickness
    for nm, yy in (("S", Y0 + 0.012), ("N", Y1 - 0.012)):
        parts.append(C.hb(f"R21C_HATCH_Reveal{nm}", (0.300, 0.012, 2.16),
                          (-71.00, yy, 1.101), mat["galv"], coll,
                          bevel=0.002, seg=2))
    parts.append(C.hb("R21C_HATCH_RevealTop", (0.300, 1.36, 0.012),
                      (-71.00, (Y0 + Y1) * 0.5, 2.188), mat["galv"], coll,
                      bevel=0.002, seg=2))
    # sill
    parts.append(C.hb("R21C_HATCH_Sill", (0.235, 1.46, 0.024),
                      (-71.0925, (Y0 + Y1) * 0.5, 1.054), mat["steel_bare"], coll,
                      bevel=0.004, seg=3))
    # anchor plates + bolts on the room face
    for i, (yy, zz) in enumerate(((Y0 - 0.02, 0.22), (Y0 - 0.02, 1.10),
                                  (Y1 + 0.02, 0.22), (Y1 + 0.02, 1.10),
                                  ((Y0 + Y1) * 0.5, 2.15))):
        parts.append(C.hb(f"R21C_HATCH_Anchor{i}", (0.008, 0.075, 0.11),
                          (fx - 0.003, yy, zz), mat["steel_dark"], coll,
                          bevel=0.002, seg=2))
        for dz in (-0.030, 0.030):
            parts.append(C.screw(f"R21C_HATCH_AnchorBolt{i}{dz:+.3f}",
                    (fx - 0.008, yy, zz + dz), (-1, 0, 0), mat["steel_bare"], coll,
                    r=0.0058, socket_mat=mat["dark"]))
    # glazing gaskets (rubber), overlapping frame + glass
    parts.append(C.hb("R21C_HATCH_GasketS", (0.020, 0.030, 1.05),
                      (-71.047, Y0 + 0.038, 1.60), mat["rubber"], coll,
                      bevel=0.002, seg=2))
    parts.append(C.hb("R21C_HATCH_GasketNLow", (0.020, 0.030, 0.49),
                      (-71.047, Y1 - 0.038, 1.315), mat["rubber"], coll,
                      bevel=0.002, seg=2))
    parts.append(C.hb("R21C_HATCH_GasketTop", (0.020, 0.78, 0.030),
                      (-71.047, Y0 + 0.44, 2.113), mat["rubber"], coll,
                      bevel=0.002, seg=2))
    parts.append(C.hb("R21C_HATCH_GasketBottom", (0.020, 1.28, 0.030),
                      (-71.047, (Y0 + Y1) * 0.5, 1.078), mat["rubber"], coll,
                      bevel=0.002, seg=2))
    # window lock on the north jamb
    parts.append(C.hb("R21C_HATCH_WindowLockPlate", (0.016, 0.036, 0.10),
                      (-71.055, Y1 - 0.075, 1.44), mat["steel_bare"], coll,
                      bevel=0.003, seg=3))
    parts.append(C.cy("R21C_HATCH_WindowLock", 0.013, 0.018,
                      (-71.070, Y1 - 0.075, 1.44), mat["steel_bare"], coll,
                      rot=(0, math.radians(90), 0), segments=16, bevel=0.0015))
    parts.append(C.hb("R21C_HATCH_WindowLatch", (0.014, 0.030, 0.022),
                      (-71.068, Y1 - 0.105, 1.44), mat["steel_bare"], coll,
                      bevel=0.002, seg=2))
    ob = C.join(parts, "R21C_HATCH_WindowFrame", coll)
    return ob


# --------------------------------------------------------------------------------------
# broken glass pane
# --------------------------------------------------------------------------------------
def glass_pane(mat, coll):
    # remaining pane: large jagged bite out of the upper-north corner
    outline = [
        (Y0 + 0.045, 1.080),
        (Y1 - 0.045, 1.080),
        (Y1 - 0.045, 1.300),
        (Y1 - 0.175, 1.330),
        (Y1 - 0.145, 1.400),
        (Y1 - 0.315, 1.430),
        (Y1 - 0.275, 1.500),
        (Y1 - 0.445, 1.530),
        (Y1 - 0.405, 1.630),
        (Y1 - 0.525, 1.680),
        (Y1 - 0.485, 1.800),
        (Y1 - 0.595, 1.860),
        (Y1 - 0.555, 2.000),
        (Y1 - 0.640, 2.120),
        (Y0 + 0.045, 2.120),
    ]
    parts = [C.prism_yz("R21C_HATCH_Glass", outline, -71.060, 0.012,
                        mat["glass"], coll)]
    # cracks, 1.5 mm proud of the room face
    xc = -71.062
    crack_sets = [
        [(Y1 - 0.045, 1.300), (Y1 - 0.230, 1.240), (Y1 - 0.380, 1.180)],
        [(Y1 - 0.145, 1.400), (Y1 - 0.300, 1.440), (Y1 - 0.450, 1.400)],
        [(Y1 - 0.275, 1.500), (Y1 - 0.430, 1.540), (Y1 - 0.550, 1.490)],
        [(Y1 - 0.445, 1.630), (Y1 - 0.600, 1.660), (Y1 - 0.700, 1.600)],
        [(Y1 - 0.605, 1.900), (Y1 - 0.760, 1.930), (Y1 - 0.820, 1.880)],
        [(Y1 - 0.555, 2.000), (Y1 - 0.760, 2.040), (Y1 - 0.860, 2.010)],
    ]
    for i, pts in enumerate(crack_sets):
        parts.append(C.tube(f"R21C_HATCH_Crack{i}",
                            [(xc, y, z) for y, z in pts], 0.0013,
                            mat["crack"], coll, sides=5))
    # small radial cracks around the break origin
    ox, oz = Y1 - 0.150, 1.335
    for i in range(5):
        a = math.radians(20 + i * 33)
        parts.append(C.tube(f"R21C_HATCH_CrackRad{i}",
                            [(xc, ox, oz),
                             (xc, ox + math.cos(a) * 0.055, oz + math.sin(a) * 0.045),
                             (xc, ox + math.cos(a) * 0.095, oz + math.sin(a) * 0.075)],
                            0.0010, mat["crack"], coll, sides=5))
    ob = C.join(parts, "R21C_HATCH_Glass", coll, weighted=False)
    return ob


# --------------------------------------------------------------------------------------
# roller shutter
# --------------------------------------------------------------------------------------
def shutter(mat, coll, debug=False):
    parts = []
    # housing mounted above the opening, inside the room
    parts.append(C.hb("R21C_HATCH_ShutterHousing", (0.160, 1.56, 0.180),
                      (-71.225, (Y0 + Y1) * 0.5, 2.250), mat["galv"], coll,
                      bevel=0.010, seg=4))
    for sy in (Y0 - 0.078, Y1 + 0.078):
        parts.append(C.hb(f"R21C_HATCH_ShutterEnd{sy:.2f}", (0.180, 0.020, 0.200),
                          (-71.225, sy, 2.250), mat["steel_dark"], coll,
                          bevel=0.005, seg=3))
        for dz in (-0.060, 0.060):
            parts.append(C.screw(f"R21C_HATCH_ShutterEndBolt{sy:.2f}{dz:+.3f}",
                    (-71.310, sy, 2.250 + dz), (-1, 0, 0), mat["steel_bare"], coll,
                    r=0.006, socket_mat=mat["dark"]))
    parts.append(C.hb("R21C_HATCH_ShutterLip", (0.030, 1.50, 0.014),
                      (-71.300, (Y0 + Y1) * 0.5, 2.160), mat["steel_dark"], coll,
                      bevel=0.003, seg=2))
    # slats from 1.54 to 2.14
    n = 15
    z0, z1 = 1.612, 2.142
    step = (z1 - z0) / (n - 1)
    for i in range(n):
        parts.append(C.hb(f"R21C_HATCH_ShutterSlat{i}", (0.030, 1.320, 0.044),
                          (-71.190, (Y0 + Y1) * 0.5, z0 + i * step), mat["galv"], coll,
                          rot=(0, math.radians(18), 0), bevel=0.003, seg=3))
    # bottom bar, rubber seal and lock
    parts.append(C.hb("R21C_HATCH_ShutterBottom", (0.042, 1.355, 0.058),
                      (-71.192, (Y0 + Y1) * 0.5, 1.600), mat["galv"], coll,
                      bevel=0.006, seg=3))
    parts.append(C.hb("R21C_HATCH_ShutterSeal", (0.050, 1.335, 0.016),
                      (-71.190, (Y0 + Y1) * 0.5, 1.568), mat["rubber"], coll,
                      bevel=0.003, seg=2))
    parts.append(C.hb("R21C_HATCH_ShutterLockPlate", (0.020, 0.110, 0.090),
                      (-71.178, (Y0 + Y1) * 0.5, 1.600), mat["steel_dark"], coll,
                      bevel=0.003, seg=2))
    parts.append(C.cy("R21C_HATCH_ShutterLock", 0.016, 0.016,
                      (-71.166, (Y0 + Y1) * 0.5, 1.600), mat["steel_bare"], coll,
                      rot=(0, math.radians(90), 0), segments=14, bevel=0.0015))
    for sx in (-1, 1):
        parts.append(C.hb(f"R21C_HATCH_ShutterHandle{sx}", (0.030, 0.045, 0.018),
                          (-71.184, (Y0 + Y1) * 0.5 + sx * 0.075, 1.577),
                          mat["steel_bare"], coll, bevel=0.003, seg=2))
    # side guides
    for sy, side in ((Y0 + 0.018, "S"), (Y1 - 0.018, "N")):
        parts.append(C.hb(f"R21C_HATCH_GuideBack{side}", (0.012, 0.060, 1.145),
                          (-71.152, sy, 1.595), mat["galv"], coll,
                          bevel=0.002, seg=2))
        parts.append(C.hb(f"R21C_HATCH_GuideLip{side}", (0.030, 0.012, 1.145),
                          (-71.235, sy, 1.595), mat["galv"], coll,
                          bevel=0.003, seg=2))
        parts.append(C.hb(f"R21C_HATCH_GuideWeb{side}", (0.072, 0.008, 1.130),
                          (-71.193, sy + 0.001, 1.595), mat["galv"], coll,
                          bevel=0.002, seg=2))
        for i in range(4):
            parts.append(C.screw(f"R21C_HATCH_GuideBolt{side}{i}", (-71.246, sy, 1.12 + i * 0.30),
                    (-1, 0, 0), mat["steel_bare"], coll, r=0.005, socket_mat=mat["dark"]))
    # hand crank on the north end
    parts.append(C.hb("R21C_HATCH_CrankGear", (0.100, 0.090, 0.120),
                      (-71.270, Y1 + 0.095, 2.245), mat["steel_dark"], coll,
                      bevel=0.008, seg=3))
    parts.append(C.cy("R21C_HATCH_CrankShaft", 0.014, 0.150,
                      (-71.345, Y1 + 0.095, 2.245), mat["steel_bare"], coll,
                      rot=(0, math.radians(90), 0), segments=14, bevel=0.0015))
    parts.append(C.hb("R21C_HATCH_CrankArm", (0.020, 0.030, 0.180),
                      (-71.390, Y1 + 0.095, 2.160), mat["steel_bare"], coll,
                      bevel=0.004, seg=3))
    parts.append(C.cy("R21C_HATCH_CrankGrip", 0.012, 0.060,
                      (-71.390, Y1 + 0.095, 2.070), mat["plastic"], coll,
                      segments=12, bevel=0.002))
    # warning plate
    parts.append(C.hb("R21C_HATCH_ShutterLabel", (0.008, 0.360, 0.070),
                      (-71.307, (Y0 + Y1) * 0.5 - 0.30, 2.238), mat["hazard_y"], coll,
                      bevel=0.0015, seg=2))
    parts.append(C.frame("R21C_HATCH_ShutterLabelBorder", 0.350, 0.060,
                         0.330, 0.040, 0.008,
                         (-71.311, (Y0 + Y1) * 0.5 - 0.30, 2.238),
                         mat["dark"], coll, bevel=0.001, seg=2))
    if debug:
        return parts
    ob = C.join(parts, "R21C_HATCH_Shutter", coll)
    return ob


# --------------------------------------------------------------------------------------
# counter
# --------------------------------------------------------------------------------------
def counter_door(name, y_left, width, z0, z1, mat, coll, open_deg=0.0, debug=False):
    parts = []
    h = z1 - z0
    zc = (z0 + z1) * 0.5
    yc = y_left + width * 0.5
    xf = -71.772
    parts.append(C.frame(name + "_Frame", width, h, width - 0.10, h - 0.10, 0.028,
                         (xf, yc, zc), mat["green"], coll, bevel=0.0018, seg=2))
    parts.append(C.hb(name + "_Panel", (0.011, width - 0.062, h - 0.062),
                      (-71.7705, yc, zc), mat["green_dark"], coll, bevel=0.002, seg=2))
    # handle near the free edge (right side for the left door)
    hy = y_left + width - 0.075
    parts.append(C.hb(name + "_HandlePlate", (0.012, 0.040, 0.320),
                      (-71.790, hy, zc + 0.015), mat["green"], coll, bevel=0.002, seg=3))
    parts.append(C.hb(name + "_Grip", (0.020, 0.018, 0.110),
                      (-71.812, hy, zc), mat["steel_bare"], coll, bevel=0.003, seg=3))
    for gz in (-0.040, 0.040):
        parts.append(C.hb(name + f"_GripPost{gz:+.3f}", (0.020, 0.013, 0.016),
                          (-71.800, hy, zc + gz), mat["steel_bare"], coll,
                          bevel=0.002, seg=2))
    parts.append(C.cy(name + "_Lock", 0.016, 0.012, (-71.800, hy, zc + 0.145),
                      mat["steel_bare"], coll, rot=(0, math.radians(90), 0),
                      segments=16, bevel=0.0015))
    parts.append(C.hb(name + "_KeySlot", (0.004, 0.006, 0.014),
                      (-71.808, hy, zc + 0.145), mat["dark"], coll,
                      bevel=0.0005, seg=1))
    # hinges on the outer edge
    for hz in (z0 + 0.14, z1 - 0.14):
        parts.append(C.cy(name + f"_Hinge{hz:.2f}", 0.011, 0.070,
                          (-71.790, y_left + 0.015, hz), mat["steel_bare"], coll,
                          segments=14, bevel=0.0012))
    if debug:
        return parts
    ob = C.join(parts, name, coll)
    return ob


def counter(mat, coll, debug=False):
    parts = []
    # toe kick + carcass
    parts.append(C.hb("R21C_HATCH_CounterToe", (0.560, 1.820, 0.145),
                      (-71.440, 11.005, 0.0725), mat["dark"], coll,
                      bevel=0.004, seg=3))
    parts.append(C.hb("R21C_HATCH_CounterBody", (0.600, 1.900, 0.870),
                      (-71.460, 11.005, 0.575), mat["green"], coll,
                      bevel=0.008, seg=4))
    # side panels (overlap body)
    for sy in (10.055, 11.955):
        parts.append(C.hb(f"R21C_HATCH_CounterSide{sy:.3f}", (0.620, 0.020, 0.900),
                          (-71.470, sy, 0.570), mat["green_dark"], coll,
                          bevel=0.004, seg=3))
    # stainless top with nosing
    parts.append(C.hb("R21C_HATCH_CounterTop", (0.680, 1.950, 0.045),
                      (-71.480, 11.005, 1.0225), mat["steel_bare"], coll,
                      bevel=0.005, seg=4))
    parts.append(C.hb("R21C_HATCH_CounterNose", (0.026, 1.930, 0.055),
                      (-71.810, 11.005, 1.005), mat["steel_bare"], coll,
                      bevel=0.004, seg=3))
    # kick plate
    parts.append(C.hb("R21C_HATCH_CounterKick", (0.018, 1.780, 0.090),
                      (-71.757, 11.005, 0.185), mat["steel_bare"], coll,
                      bevel=0.003, seg=2))
    # toe vent slots
    for i in range(7):
        parts.append(C.hb(f"R21C_HATCH_ToeVent{i}", (0.006, 0.120, 0.022),
                          (-71.723, 10.28 + i * 0.24, 0.075), mat["dark"], coll,
                          bevel=0.001, seg=1))
    # central stile
    parts.append(C.hb("R21C_HATCH_CounterStile", (0.040, 0.060, 0.800),
                      (-71.760, 11.005, 0.560), mat["green"], coll,
                      bevel=0.003, seg=3))
    # doors
    d1 = counter_door("R21C_HATCH_CounterDoorA", 10.075, 0.870, 0.205, 0.955,
                      mat, coll, open_deg=7.0)
    d2 = counter_door("R21C_HATCH_CounterDoorB", 11.065, 0.870, 0.205, 0.955,
                      mat, coll, open_deg=0.0)
    # the doors are built in place already; only the left one swings a little
    C.bake_world(d1)
    piv = Vector((-71.772, 10.075, 0))
    d1.matrix_world = (Matrix.Translation(piv) @ Matrix.Rotation(math.radians(7.0), 4, "Z") @
                       Matrix.Translation(-piv))
    parts.append(d1)
    parts.append(d2)
    # interior shelf visible through the ajar door
    parts.append(C.hb("R21C_HATCH_CounterShelf", (0.526, 1.910, 0.020),
                      (-71.437, 11.005, 0.545), mat["galv"], coll,
                      bevel=0.002, seg=2))
    # back panel, 5 mm off the wall
    parts.append(C.hb("R21C_HATCH_CounterBack", (0.020, 1.820, 0.820),
                      (-71.166, 11.005, 0.570), mat["dark"], coll,
                      bevel=0.002, seg=2))
    # transaction tray + rubber mat + cable grommet
    parts.append(C.hb("R21C_HATCH_TrayBase", (0.420, 0.300, 0.010),
                      (-71.470, 10.720, 1.047), mat["steel_bare"], coll,
                      bevel=0.002, seg=2))
    for sx in (-1, 1):
        parts.append(C.hb(f"R21C_HATCH_TrayLipX{sx}", (0.018, 0.300, 0.034),
                          (-71.470 + sx * 0.210, 10.720, 1.065),
                          mat["steel_bare"], coll, bevel=0.003, seg=2))
    for sy in (-1, 1):
        parts.append(C.hb(f"R21C_HATCH_TrayLipY{sy}", (0.420, 0.018, 0.034),
                          (-71.470, 10.720 + sy * 0.150, 1.065),
                          mat["steel_bare"], coll, bevel=0.003, seg=2))
    parts.append(C.hb("R21C_HATCH_TrayMat", (0.380, 0.260, 0.005),
                      (-71.470, 10.720, 1.0535), mat["rubber"], coll,
                      bevel=0.001, seg=1))
    parts.append(C.cy("R21C_HATCH_Grommet", 0.030, 0.012,
                      (-71.410, 11.820, 1.046), mat["rubber"], coll,
                      segments=18, bevel=0.002))
    parts.append(C.cy("R21C_HATCH_GrommetHole", 0.020, 0.010,
                      (-71.410, 11.820, 1.044), mat["dark"], coll,
                      segments=16, bevel=0.001))
    if debug:
        return parts
    ob = C.join(parts, "R21C_HATCH_Counter", coll)
    return ob


# --------------------------------------------------------------------------------------
# intercom + conduit
# --------------------------------------------------------------------------------------
def intercom(mat, coll):
    parts = []
    xf = -71.145
    yc, zc = 11.790, 1.410
    parts.append(C.hb("R21C_HATCH_IntercomBody", (0.080, 0.200, 0.260),
                      (xf - 0.040, yc, zc), mat["green"], coll,
                      bevel=0.012, seg=4))
    parts.append(C.hb("R21C_HATCH_IntercomFace", (0.012, 0.180, 0.240),
                      (xf - 0.084, yc, zc), mat["green_dark"], coll,
                      bevel=0.005, seg=3))
    # speaker slots
    for i in range(7):
        parts.append(C.hb(f"R21C_HATCH_IntercomSlot{i}", (0.006, 0.120, 0.007),
                          (xf - 0.092, yc, 1.345 + i * 0.018),
                          mat["dark"], coll, bevel=0.001, seg=1))
    # push-to-talk button and LED
    parts.append(C.cy("R21C_HATCH_IntercomButtonRing", 0.022, 0.008,
                      (xf - 0.092, yc, 1.310), mat["steel_bare"], coll,
                      rot=(0, math.radians(90), 0), segments=18, bevel=0.0015))
    parts.append(C.cy("R21C_HATCH_IntercomButton", 0.015, 0.014,
                      (xf - 0.098, yc, 1.310), mat["paint_red"], coll,
                      rot=(0, math.radians(90), 0), segments=18, bevel=0.002))
    parts.append(C.cy("R21C_HATCH_IntercomLED", 0.005, 0.007,
                      (xf - 0.093, yc - 0.065, 1.310), mat["led_green"], coll,
                      rot=(0, math.radians(90), 0), segments=10, bevel=0.001))
    parts.append(C.text("R21C_HATCH_IntercomText", "INTERCOM", 0.023,
                        (xf - 0.094, yc, 1.505), C.ROT_E, mat["white"], coll,
                        extrude=0.0005))
    # cable gland + conduit down to the counter
    parts.append(C.cy("R21C_HATCH_IntercomGland", 0.012, 0.030,
                      (xf - 0.040, yc, zc - 0.135), mat["galv"], coll,
                      segments=12, bevel=0.002))
    parts.append(C.tube("R21C_HATCH_Conduit",
                        [(xf - 0.040, yc, zc - 0.145), (xf - 0.040, yc, 1.13),
                         (xf - 0.040, yc, 1.06)],
                        0.010, mat["galv"], coll, sides=10))
    for zz in (1.295, 1.180):
        parts.append(C.hb(f"R21C_HATCH_ConduitClamp{zz:.3f}", (0.020, 0.050, 0.018),
                          (xf - 0.038, yc, zz), mat["steel_dark"], coll,
                          bevel=0.002, seg=2))
        parts.append(C.cy(f"R21C_HATCH_ConduitScrew{zz:.3f}", 0.005, 0.010,
                          (xf - 0.050, yc, zz), mat["steel_bare"], coll,
                          rot=(0, math.radians(90), 0), segments=10, bevel=0.001))
    # junction box under the counter top
    parts.append(C.hb("R21C_HATCH_JunctionBox", (0.070, 0.120, 0.100),
                      (-71.180, 11.790, 1.005), mat["galv"], coll,
                      bevel=0.006, seg=3))
    parts.append(C.hb("R21C_HATCH_JunctionLid", (0.010, 0.100, 0.080),
                      (-71.142, 11.790, 1.005), mat["steel_dark"], coll,
                      bevel=0.002, seg=2))
    for dz in (-0.030, 0.030):
        parts.append(C.screw(f"R21C_HATCH_JunctionScrew{dz:+.3f}", (-71.135, 11.790, 1.005 + dz),
                (-1, 0, 0), mat["steel_bare"], coll, r=0.0045, socket_mat=mat["dark"]))
    ob = C.join(parts, "R21C_HATCH_Intercom", coll)
    return ob


# --------------------------------------------------------------------------------------
# sign
# --------------------------------------------------------------------------------------
def sign(mat, coll):
    parts = []
    parts.append(C.hb("R21C_HATCH_SignBack", (0.022, 0.720, 0.280),
                      (-71.159, 10.900, 2.470), mat["green"], coll,
                      bevel=0.004, seg=3))
    parts.append(C.frame("R21C_HATCH_SignFrame", 0.750, 0.310, 0.690, 0.250,
                         0.030, (-71.166, 10.900, 2.470), mat["aluminum"], coll,
                         bevel=0.003, seg=2))
    parts.append(C.text("R21C_HATCH_SignText", "SERVICIO", 0.105,
                        (-71.172, 10.900, 2.500), C.ROT_E, mat["white"], coll,
                        extrude=0.0012))
    parts.append(C.text("R21C_HATCH_SignSub", "NEXUS / CONTROL DE ACCESO", 0.026,
                        (-71.172, 10.900, 2.395), C.ROT_E, mat["sign_green"], coll,
                        extrude=0.0007))
    for yy in (10.58, 11.22):
        for zz in (2.38, 2.56):
            parts.append(C.screw(f"R21C_HATCH_SignScrew{yy:.2f}{zz:.2f}", (-71.172, yy, zz),
                    (-1, 0, 0), mat["steel_bare"], coll, r=0.0042, socket_mat=mat["dark"]))
    ob = C.join(parts, "R21C_HATCH_Sign", coll, weighted=False)
    return ob


# --------------------------------------------------------------------------------------
# debris
# --------------------------------------------------------------------------------------
def debris(mat, coll):
    parts = []
    counter_shards = [
        (-71.52, 11.13, 0.060, 10),
        (-71.42, 11.22, 0.050, 35),
        (-71.60, 11.26, 0.045, 70),
        (-71.35, 11.13, 0.040, 120),
        (-71.47, 11.38, 0.035, 155),
        (-71.56, 11.06, 0.030, 200),
    ]
    for i, (xx, yy, sz, ang) in enumerate(counter_shards):
        parts.append(C.shard(f"R21C_HATCH_ShardCounter{i}",
                             (xx, yy, 1.044), mat, coll,
                             size=(sz, sz * 0.72), thick=0.003,
                             seed=100 + i, rot_z=ang))
    floor_shards = [
        (-71.62, 10.62, 0.070, 0),
        (-71.54, 10.82, 0.050, 48),
        (-71.66, 11.02, 0.060, 95),
        (-71.50, 11.22, 0.045, 140),
        (-71.60, 11.40, 0.055, 190),
        (-71.44, 10.98, 0.035, 260),
    ]
    for i, (xx, yy, sz, ang) in enumerate(floor_shards):
        parts.append(C.shard(f"R21C_HATCH_ShardFloor{i}",
                             (xx, yy, -0.001), mat, coll,
                             size=(sz, sz * 0.68), thick=0.003,
                             seed=200 + i, rot_z=ang))
    ob = C.join(parts, "R21C_HATCH_Shards", coll, weighted=False)
    return ob


def build(mat, coll):
    objs = []
    objs.append(window_frame(mat, coll))
    objs.append(glass_pane(mat, coll))
    objs.append(shutter(mat, coll))
    objs.append(counter(mat, coll))
    objs.append(intercom(mat, coll))
    objs.append(sign(mat, coll))
    objs.append(debris(mat, coll))
    return objs
