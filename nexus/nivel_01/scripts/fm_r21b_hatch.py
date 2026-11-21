"""Service hatch / office nook for L1_SECURITY_R21B_HERO (east wall, y 10.2-11.6)."""
import math
import random
import bpy
from mathutils import Vector, Matrix

import fm_ops_lib as L
import fm_r21b_lib as B


def build(mat, coll):
    rnd = random.Random(8821)

    # ------------------------------------------------------------------ L counter
    cp = []
    # plinth / carcass (local x = 0 at wall, +X = wall, -X = room)
    cp.append(B.box("R21B_HATCH_Counter_Plinth", (0.50, 1.95, 0.10), (-0.26, 1.025, 0.05),
                    mat["dark"], coll, bevel=0.004, seg=3))
    cp.append(B.box("R21B_HATCH_Counter_Body", (0.55, 1.95, 0.82), (-0.285, 1.025, 0.50),
                    mat["green"], coll, bevel=0.008, seg=4))
    cp.append(B.box("R21B_HATCH_Counter_Top", (0.66, 2.02, 0.045), (-0.36, 1.025, 0.935),
                    mat["steel_bare"], coll, bevel=0.005, seg=3))
    cp.append(B.box("R21B_HATCH_Counter_Kick", (0.04, 1.90, 0.10), (-0.545, 1.025, 0.055),
                    mat["rubber"], coll, bevel=0.002, seg=2))
    # front doors + vents
    for i, y in enumerate((0.62, 1.72)):
        cp.append(B.box(f"R21B_HATCH_Counter_Door{i}", (0.022, 0.98, 0.64),
                        (-0.570, y, 0.52), mat["green_dark"], coll, bevel=0.004, seg=3))
        cp.append(B.box(f"R21B_HATCH_Counter_DoorGrip{i}", (0.020, 0.020, 0.16),
                        (-0.600, y + 0.35, 0.56), mat["steel_bare"], coll,
                        bevel=0.003, seg=3))
        for gz in (-0.06, 0.06):
            cp.append(B.box(f"R21B_HATCH_Counter_DoorGripPost{i}{gz}", (0.026, 0.014, 0.014),
                            (-0.588, y + 0.35, 0.56 + gz), mat["steel_bare"], coll,
                            bevel=0.002, seg=2))
        cp.append(B.bolts(f"R21B_HATCH_Counter_Hinge{i}",
                          [(-0.583, y - 0.46, 0.25), (-0.583, y - 0.46, 0.79)],
                          (-1, 0, 0), 0.006, 0.007, mat["steel_dark"], coll))
    # transaction tray
    cp.append(B.box("R21B_HATCH_Tray_Base", (0.24, 0.34, 0.025), (-0.40, 0.90, 0.975),
                    mat["steel_dark"], coll, bevel=0.004, seg=3))
    # intercom on the counter
    cp.append(B.box("R21B_HATCH_Intercom_Base", (0.16, 0.20, 0.045), (-0.38, 1.52, 0.978),
                    mat["plastic"], coll, bevel=0.006, seg=3))
    cp.append(B.box("R21B_HATCH_Intercom_Body", (0.15, 0.19, 0.075), (-0.38, 1.52, 1.035),
                    mat["dark"], coll, bevel=0.008, seg=4))
    cp.append(B.box("R21B_HATCH_Intercom_Face", (0.004, 0.15, 0.050), (-0.458, 1.52, 1.045),
                    mat["steel_bare"], coll, bevel=0.001, seg=2))
    cp.append(B.cyl("R21B_HATCH_Intercom_Btn", 0.012, 0.008, (-0.462, 1.60, 1.045),
                    mat["paint_red"], coll, rot=(0, math.radians(90), 0), segments=14,
                    bevel=0.001))
    cp.append(B.box("R21B_HATCH_Intercom_LED", (0.003, 0.012, 0.006), (-0.462, 1.44, 1.050),
                    mat["led_green"], coll, bevel=0.0005, seg=1))
    counter = B.join(cp, "R21B_HATCH_ServiceCounter", coll)
    B.place(counter, (-71.149, 10.05, 0.0015))

    # ------------------------------------------------------------------ glass + frame in opening
    gp = []
    # frame at opening x=-71.02 (inside the 0.3 wall)
    gp.append(B.box("R21B_HATCH_Glass_FrameT", (0.055, 1.34, 0.040), (-71.02, 10.90, 2.175),
                    mat["steel_dark"], coll, bevel=0.004, seg=3))
    gp.append(B.box("R21B_HATCH_Glass_FrameB", (0.055, 1.34, 0.040), (-71.02, 10.90, 1.125),
                    mat["steel_dark"], coll, bevel=0.004, seg=3))
    gp.append(B.box("R21B_HATCH_Glass_FrameL", (0.055, 0.040, 1.09), (-71.02, 10.230, 1.650),
                    mat["steel_dark"], coll, bevel=0.004, seg=3))
    gp.append(B.box("R21B_HATCH_Glass_FrameR", (0.055, 0.040, 1.09), (-71.02, 11.570, 1.650),
                    mat["steel_dark"], coll, bevel=0.004, seg=3))
    gp.append(B.box("R21B_HATCH_Glass_Mullion", (0.050, 0.045, 1.00), (-71.02, 10.90, 1.620),
                    mat["steel_dark"], coll, bevel=0.003, seg=3))
    # left pane broken: 3 shards with jagged edges, some missing
    gp.append(B.panel_poly_yz("R21B_HATCH_Glass_PaneL_A",
                              [(10.245, 1.16), (10.58, 1.16), (10.52, 1.55),
                               (10.61, 1.92), (10.56, 2.115), (10.245, 2.115)],
                              -71.035, 0.006, mat["glass"], coll))
    gp.append(B.panel_poly_yz("R21B_HATCH_Glass_PaneL_B",
                              [(10.60, 1.16), (10.86, 1.16), (10.86, 2.115),
                               (10.58, 2.115), (10.64, 1.96), (10.55, 1.70),
                               (10.62, 1.42)],
                              -71.035, 0.006, mat["glass"], coll))
    # right pane intact but with a crack
    gp.append(B.box("R21B_HATCH_Glass_PaneR", (0.006, 0.68, 0.96), (-71.035, 11.245, 1.625),
                    mat["glass"], coll, bevel=0.001, seg=2))
    # frame bolts
    for yy in (10.25, 11.55):
        for zz in (1.14, 2.10):
            gp.append(B.bolts(f"R21B_HATCH_Glass_Bolt{yy}_{zz}",
                              [(-71.02, yy, zz)], (1, 0, 0), 0.007, 0.009,
                              mat["steel_bare"], coll))
    # broken window: panes are represented by the loose shards; the frame is the
    # wall reveal itself, so no full glazing object is delivered.
    glass = None
    for o in gp:
        bpy.data.objects.remove(o, do_unlink=True)

    # ------------------------------------------------------------------ roller shutter
    sh = []
    sh.append(B.box("R21B_HATCH_Shutter_Housing", (0.28, 1.86, 0.30), (-71.40, 10.90, 2.35),
                    mat["galv"], coll, bevel=0.006, seg=3))
    sh.append(B.box("R21B_HATCH_Shutter_HousingLip", (0.30, 1.90, 0.050), (-71.41, 10.90, 2.19),
                    mat["steel_dark"], coll, bevel=0.004, seg=3))
    # guide rails
    for yy in (10.02, 11.78):
        sh.append(B.box(f"R21B_HATCH_Shutter_Rail{yy}", (0.12, 0.10, 1.35),
                        (-71.40, yy, 1.55), mat["steel_dark"], coll, bevel=0.004, seg=3))
    # partially lowered curtain
    for i in range(12):
        z = 1.35 + i * 0.070
        sh.append(B.box(f"R21B_HATCH_Shutter_Slat{i}", (0.055, 0.70, 0.060),
                        (-71.40, 10.38, z), mat["galv"], coll, bevel=0.003, seg=2))
    sh.append(B.box("R21B_HATCH_Shutter_BottomBar", (0.070, 0.74, 0.065),
                    (-71.40, 10.38, 1.31), mat["steel_dark"], coll, bevel=0.004, seg=3))
    sh.append(B.box("R21B_HATCH_Shutter_Lock", (0.030, 0.08, 0.06),
                    (-71.44, 10.38, 1.31), mat["steel_bare"], coll, bevel=0.003, seg=2))
    # brackets tying the shutter assembly to the wall
    for yy in (10.20, 11.60):
        sh.append(B.box(f"R21B_HATCH_Shutter_BracketTop{yy}", (0.30, 0.06, 0.060),
                        (-71.29, yy, 2.46), mat["steel_dark"], coll, bevel=0.003, seg=3))
        sh.append(B.box(f"R21B_HATCH_Shutter_BracketBot{yy}", (0.27, 0.06, 0.055),
                        (-71.28, yy, 1.02), mat["steel_dark"], coll, bevel=0.003, seg=3))
    shutter = B.join(sh, "R21B_HATCH_Shutter", coll)

    # ------------------------------------------------------------------ office nook desk
    op = []
    op.append(B.box("R21B_HATCH_Nook_Top", (0.62, 1.25, 0.045), (-0.310, 12.66, 0.760),
                    mat["olive"], coll, bevel=0.005, seg=3))
    op.append(B.box("R21B_HATCH_Nook_TopEdge", (0.03, 1.21, 0.050), (-0.625, 12.66, 0.760),
                    mat["dark"], coll, bevel=0.003, seg=2))
    op.append(B.box("R21B_HATCH_Nook_Cabinet", (0.56, 1.17, 0.70), (-0.300, 12.66, 0.390),
                    mat["green"], coll, bevel=0.006, seg=3))
    op.append(B.box("R21B_HATCH_Nook_Kick", (0.04, 1.13, 0.08), (-0.553, 12.66, 0.040),
                    mat["rubber"], coll, bevel=0.002, seg=2))
    for i, y in enumerate((12.38, 12.94)):
        op.append(B.box(f"R21B_HATCH_Nook_Drawer{i}", (0.020, 0.50, 0.20),
                        (-0.585, y, 0.62), mat["green_dark"], coll, bevel=0.003, seg=3))
        op.append(B.box(f"R21B_HATCH_Nook_DrawerPull{i}", (0.020, 0.16, 0.020),
                        (-0.600, y, 0.62), mat["steel_bare"], coll, bevel=0.003, seg=2))
    # CRT terminal, screen faces -X
    op.append(B.box("R21B_HATCH_Nook_CRT_Base", (0.22, 0.30, 0.025), (-0.35, 12.62, 0.797),
                    mat["plastic"], coll, bevel=0.006, seg=3))
    op.append(B.box("R21B_HATCH_Nook_CRT_Body", (0.34, 0.40, 0.31), (-0.40, 12.62, 0.995),
                    mat["plastic"], coll, bevel=0.020, seg=4))
    op.append(B.box("R21B_HATCH_Nook_CRT_Bezel", (0.030, 0.38, 0.29), (-0.583, 12.62, 0.995),
                    mat["dark"], coll, bevel=0.010, seg=3))
    op.append(B.box("R21B_HATCH_Nook_CRT_Screen", (0.008, 0.32, 0.235), (-0.603, 12.62, 0.995),
                    mat["screen_dead"], coll, bevel=0.004, seg=3))
    op.append(B.cyl("R21B_HATCH_Nook_CRT_Knob", 0.014, 0.045, (-0.407, 12.79, 0.86),
                    mat["dark"], coll, segments=14, bevel=0.002))
    op.append(B.box("R21B_HATCH_Nook_Keyboard", (0.17, 0.42, 0.028), (-0.69, 12.64, 0.785),
                    mat["plastic"], coll, bevel=0.006, seg=3))
    op.append(B.box("R21B_HATCH_Nook_Keys", (0.13, 0.36, 0.012), (-0.70, 12.64, 0.800),
                    mat["dark"], coll, bevel=0.002, seg=2))
    op.append(B.box("R21B_HATCH_Nook_Phone", (0.18, 0.22, 0.055), (-0.72, 12.30, 0.795),
                    mat["plastic"], coll, bevel=0.010, seg=4))
    op.append(B.box("R21B_HATCH_Nook_PhoneHandset", (0.06, 0.20, 0.045), (-0.78, 12.30, 0.843),
                    mat["dark"], coll, bevel=0.012, seg=4))
    op.append(B.tube("R21B_HATCH_Nook_PhoneCord",
                     [(-0.78, 12.21, 0.83), (-0.76, 12.14, 0.80), (-0.72, 12.20, 0.79)],
                     0.0035, mat["cable_black"], coll, sides=6))
    op.append(B.tube("R21B_HATCH_Nook_CRTCable",
                     [(-0.30, 12.76, 0.80), (-0.26, 12.81, 0.74), (-0.22, 12.76, 0.70)],
                     0.006, mat["cable_black"], coll, sides=6))
    # pigeonhole unit above the desk
    op.append(B.box("R21B_HATCH_Nook_Pigeonhole", (0.14, 0.72, 0.52), (-0.090, 12.68, 1.78),
                    mat["green_dark"], coll, bevel=0.005, seg=3))
    for ix in range(3):
        for iz in range(3):
            op.append(B.box(f"R21B_HATCH_Nook_Slot{ix}_{iz}", (0.012, 0.19, 0.12),
                            (-0.163, 12.48 + ix * 0.22, 1.62 + iz * 0.16),
                            mat["dark"], coll, bevel=0.001, seg=1))
    op.append(B.box("R21B_HATCH_Nook_PigeonholeLabel", (0.004, 0.30, 0.06),
                    (-0.165, 12.68, 1.50), mat["paper"], coll, bevel=0.001, seg=2))
    # stool
    op.append(B.cyl("R21B_HATCH_Stool_Seat", 0.19, 0.055, (-1.02, 12.66, 0.62),
                    mat["fabric"], coll, segments=24, bevel=0.012))
    op.append(B.cyl("R21B_HATCH_Stool_Column", 0.030, 0.45, (-1.02, 12.66, 0.38),
                    mat["steel_dark"], coll, segments=18, bevel=0.003))
    op.append(B.cyl("R21B_HATCH_Stool_Base", 0.24, 0.035, (-1.02, 12.66, 0.035),
                    mat["steel_dark"], coll, segments=24, bevel=0.006))
    op.append(B.cyl("R21B_HATCH_Stool_Hub", 0.07, 0.06, (-1.02, 12.66, 0.075),
                    mat["dark"], coll, segments=20, bevel=0.005))
    for i in range(5):
        a = math.radians(90 + i * 72)
        op.append(B.rod(f"R21B_HATCH_Stool_Leg{i}",
                        (-1.02, 12.66, 0.07),
                        (-1.02 + math.cos(a) * 0.22, 12.66 + math.sin(a) * 0.22, 0.06),
                        0.018, mat["steel_dark"], coll, 8))
        op.append(B.cyl(f"R21B_HATCH_Stool_Caster{i}", 0.028, 0.025,
                        (-1.02 + math.cos(a) * 0.235, 12.66 + math.sin(a) * 0.235, 0.020),
                        mat["rubber"], coll, segments=12, bevel=0.004))
    # under-desk bin
    op.append(B.cyl("R21B_HATCH_Nook_Bin", 0.14, 0.36, (-0.76, 12.92, 0.190),
                    mat["plastic"], coll, segments=20, bevel=0.006, r2=0.155))
    op.append(B.annulus("R21B_HATCH_Nook_BinRim", (-0.76, 12.92, 0.370), 0.158, 0.140,
                        0.012, mat["dark"], coll))
    nook = B.join(op, "R21B_HATCH_OfficeNook", coll)
    B.place(nook, (-71.149, 0.0, 0.0))

    # ------------------------------------------------------------------ service signage
    sp = []
    sp.append(B.box("R21B_HATCH_Sign_Back", (0.020, 0.96, 0.32), (-71.160, 12.00, 2.30),
                    mat["steel_dark"], coll, bevel=0.003, seg=3))
    sp.append(B.box("R21B_HATCH_Sign_Face", (0.006, 0.84, 0.20), (-71.178, 12.00, 2.30),
                    mat["white"], coll, bevel=0.001, seg=2))
    txt = B.text("R21B_HATCH_Sign_Text", "SERVICIO", 0.105, (-71.184, 12.00, 2.30),
                 (math.radians(90), 0, math.radians(-90)), mat["sign_green"], coll)
    sp.append(txt)
    sign = B.join(sp, "R21B_HATCH_Sign", coll)

    # ------------------------------------------------------------------ broken glass shards
    shards = []
    shard_specs = [
        (-71.55, 10.62, 0.955, 0.09, 0.06, 12, 0),
        (-71.62, 10.78, 0.955, 0.06, 0.10, -20, 0),
        (-71.48, 10.45, 0.955, 0.05, 0.04, 35, 0),
        (-71.85, 10.92, 0.006, 0.08, 0.05, 60, 1),
        (-71.78, 11.10, 0.006, 0.06, 0.07, 10, 1),
        (-71.95, 10.66, 0.006, 0.04, 0.05, -40, 1),
    ]
    for i, (x, y, z, a, b, ang, floor) in enumerate(shard_specs):
        pts = [(-a * 0.5, -b * 0.4), (a * 0.6, -b * 0.5), (a * 0.4, b * 0.55),
               (-a * 0.3, b * 0.35)]
        ob = B.extrude_poly(f"R21B_HATCH_Shard{i}", pts, 0.0, 0.003, mat["glass"], coll,
                            rot=(0, 0, math.radians(ang)))
        if floor:
            ob.location = (x, y, 0.002)
        else:
            ob.location = (x, y, 0.958)
        shards.append(ob)
    B.join(shards, "R21B_HATCH_GlassShards", coll)

    return coll
