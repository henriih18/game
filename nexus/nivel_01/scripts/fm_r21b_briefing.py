"""Briefing / training zone for L1_SECURITY_R21B_HERO."""
import math
import random
import bpy
from mathutils import Vector, Matrix

import fm_ops_lib as L
import fm_r21b_lib as B


def build(mat, coll):
    parts = []
    rnd = random.Random(2107)

    # ------------------------------------------------------------------ rug
    rug_parts = []
    rug_parts.append(B.box("R21B_BRIEF_Rug_Base", (4.75, 3.45, 0.012),
                           (0, 0, 0.006), mat["rug"], coll, bevel=0.003, seg=3))
    rug = B.join(rug_parts, "R21B_BRIEF_Rug", coll)
    B.place(rug, (-96.85, 20.45, 0.0))

    # ------------------------------------------------------------------ conference table
    tp = []
    # top + laminate inlay
    tp.append(B.box("R21B_BRIEF_Table_Top", (3.05, 1.22, 0.058), (0, 0, 0.755),
                    mat["dark"], coll, bevel=0.009, seg=4))
    tp.append(B.box("R21B_BRIEF_Table_Laminate", (2.95, 1.12, 0.006), (0, 0, 0.786),
                    mat["olive"], coll, bevel=0.002, seg=2))
    tp.append(B.box("R21B_BRIEF_Table_EdgeBandW", (0.05, 1.20, 0.052), (-1.51, 0, 0.756),
                    mat["steel_dark"], coll, bevel=0.003, seg=3))
    tp.append(B.box("R21B_BRIEF_Table_EdgeBandE", (0.05, 1.20, 0.052), (1.51, 0, 0.756),
                    mat["steel_dark"], coll, bevel=0.003, seg=3))
    # steel T-legs
    for i, x in enumerate((-1.24, 1.24)):
        tp.append(B.box(f"R21B_BRIEF_Table_Leg{i}", (0.085, 0.16, 0.70),
                        (x, 0, 0.375), mat["steel_dark"], coll, bevel=0.006, seg=3))
        tp.append(B.box(f"R21B_BRIEF_Table_Foot{i}", (0.10, 1.02, 0.065),
                        (x, 0, 0.032), mat["steel_dark"], coll, bevel=0.006, seg=3))
        tp.append(B.box(f"R21B_BRIEF_Table_Gusset{i}", (0.09, 0.30, 0.22),
                        (x, 0, 0.64), mat["steel_dark"], coll, bevel=0.006, seg=3))
        tp.append(B.bolts(f"R21B_BRIEF_Table_FootBolts{i}",
                          [(x - 0.055, 0.34, 0.05), (x + 0.055, 0.34, 0.05),
                           (x - 0.055, -0.34, 0.05), (x + 0.055, -0.34, 0.05)],
                          (0, 0, 1), 0.007, 0.010, mat["steel_bare"], coll))
    # cross beam + cable tray
    tp.append(B.box("R21B_BRIEF_Table_Beam", (2.32, 0.10, 0.12), (0, 0, 0.62),
                    mat["steel_dark"], coll, bevel=0.006, seg=3))
    tp.append(B.box("R21B_BRIEF_Table_Tray", (1.95, 0.24, 0.075), (0.10, 0, 0.665),
                    mat["galv"], coll, bevel=0.005, seg=3))
    tp.append(B.box("R21B_BRIEF_Table_TrayLipN", (1.94, 0.02, 0.10), (0.10, 0.12, 0.685),
                    mat["steel_dark"], coll, bevel=0.002, seg=2))
    tp.append(B.box("R21B_BRIEF_Table_TrayLipS", (1.94, 0.02, 0.10), (0.10, -0.12, 0.685),
                    mat["steel_dark"], coll, bevel=0.002, seg=2))
    # power strip + cable coil in tray
    tp.append(B.box("R21B_BRIEF_Table_PowerStrip", (0.42, 0.07, 0.05), (0.70, 0, 0.71),
                    mat["plastic"], coll, bevel=0.004, seg=3))
    for i in range(4):
        tp.append(B.box(f"R21B_BRIEF_Table_Socket{i}", (0.035, 0.028, 0.008),
                        (0.70 - 0.14 + i * 0.093, 0.0, 0.737), mat["dark"], coll,
                        bevel=0.001, seg=2))
    tp.append(L.coil("R21B_BRIEF_Table_Coil", (0.15, 0.0, 0.69), (0, 1, 0),
                     0.055, 0.028, 3.0, 0.006, mat["cable_black"], coll, n=14, sides=6))
    # grommets + cables
    for x in (-0.86, 0.86):
        tp.append(B.annulus(f"R21B_BRIEF_Table_Grommet{x}", (x, 0.28, 0.794),
                            0.070, 0.050, 0.012, mat["rubber"], coll))
        tp.append(B.tube(f"R21B_BRIEF_Table_GrommetCable{x}",
                         [(x, 0.28, 0.795), (x, 0.30, 0.75), (x + 0.12, 0.22, 0.70),
                          (x + 0.12, 0.10, 0.69)], 0.005, mat["cable_black"], coll, sides=6))
    # under-top bolts
    tp.append(B.bolts("R21B_BRIEF_Table_UnderBolts",
                      [(-1.24, 0.30, 0.72), (1.24, 0.30, 0.72),
                       (-1.24, -0.30, 0.72), (1.24, -0.30, 0.72)],
                      (0, 0, 1), 0.008, 0.010, mat["steel_bare"], coll))
    table = B.join(tp, "R21B_BRIEF_Table", coll)
    B.place(table, (-96.85, 20.45, 0.0))

    # ------------------------------------------------------------------ training chairs
    chairs = []
    chair_spots = [
        (-98.25, 21.55, 180.0, False), (-96.85, 21.55, 180.0, False),
        (-95.45, 21.55, 180.0, False), (-98.25, 19.35, 0.0, False),
        (-96.85, 19.35, 0.0, False), (-95.45, 19.35, 0.0, False),
    ]
    for i, (x, y, f, tipped) in enumerate(chair_spots):
        chairs.append(training_chair(f"R21B_BRIEF_Chair_{i:02d}", mat, coll,
                                     (x, y, 0.0015), f, False))
    # two genuinely tipped chairs, clear of the walkway
    chairs.append(training_chair("R21B_BRIEF_Chair_08_Tipped", mat, coll,
                                 (-96.10, 22.30, 0.0), 24.0, True))
    chairs.append(training_chair("R21B_BRIEF_Chair_09_Tipped", mat, coll,
                                 (-94.35, 18.65, 0.0), -117.0, True))

    # ------------------------------------------------------------------ planning board (west wall)
    bp = []
    bp.append(B.box("R21B_BRIEF_Board_Back", (0.020, 3.55, 1.56), (0.010, 0, 0.78),
                    mat["aluminum"], coll, bevel=0.003, seg=3))
    bp.append(B.box("R21B_BRIEF_Board_Surface", (0.010, 3.40, 1.41), (0.024, 0, 0.78),
                    mat["white"], coll, bevel=0.0015, seg=2))
    # abstract floor-plan graphic: thin magnetic strips (no text)
    plan = [(-0.05, 0.95, 1.20, 0.012), (-0.05, 0.65, 1.20, 0.012),
            (-0.05, 1.15, 1.20, 0.012), (-0.60, 0.90, 0.012, 0.55),
            (0.20, 0.90, 0.012, 0.55), (0.60, 0.90, 0.012, 0.55),
            (0.05, 1.02, 0.50, 0.012), (0.35, 0.72, 0.30, 0.012)]
    for i, (yy, zz, w, h) in enumerate(plan):
        bp.append(B.box(f"R21B_BRIEF_Board_Plan{i}", (0.003, w, h), (0.031, yy, zz),
                        mat["white"] if i % 3 == 0 else mat["hazard_y"], coll,
                        bevel=0.0005, seg=1))
    for i, (yy, zz) in enumerate(((-1.10, 1.30), (-0.88, 1.08), (0.95, 0.92),
                                  (1.15, 1.28), (0.55, 0.90))):
        bp.append(B.cyl(f"R21B_BRIEF_Board_Magnet{i}", 0.026, 0.010,
                        (0.034, yy, zz), mat["paint_red"] if i % 2 else mat["hazard_y"], coll,
                        rot=(0, math.radians(90), 0), segments=18, bevel=0.002))
    # standoffs to wall
    for yy in (-1.55, 0, 1.55):
        for zz in (0.20, 1.36):
            bp.append(B.cyl(f"R21B_BRIEF_Board_Standoff{yy}_{zz}", 0.012, 0.030,
                            (-0.010, yy, zz), mat["steel_bare"], coll,
                            rot=(0, math.radians(90), 0), segments=10, bevel=0.001))
    board = B.join(bp, "R21B_BRIEF_PlanningBoard", coll)
    B.place(board, (-104.849, 21.20, 1.18))

    # ------------------------------------------------------------------ projection screen
    sp = []
    sp.append(B.cyl("R21B_BRIEF_Screen_Housing", 0.050, 2.16, (0, 0, 1.52),
                    mat["dark"], coll, rot=(math.radians(90), 0, 0), segments=20, bevel=0.004))
    sp.append(B.cyl("R21B_BRIEF_Screen_CapL", 0.056, 0.025, (0, -1.09, 1.52),
                    mat["plastic"], coll, rot=(math.radians(90), 0, 0), segments=20, bevel=0.002))
    sp.append(B.cyl("R21B_BRIEF_Screen_CapR", 0.056, 0.025, (0, 1.09, 1.52),
                    mat["plastic"], coll, rot=(math.radians(90), 0, 0), segments=20, bevel=0.002))
    sp.append(B.box("R21B_BRIEF_Screen_Fabric", (0.006, 2.03, 1.28), (0.020, 0, 0.80),
                    mat["canvas"], coll, bevel=0.001, seg=2))
    sp.append(B.box("R21B_BRIEF_Screen_BottomBar", (0.030, 2.08, 0.028), (0.020, 0, 0.145),
                    mat["steel_dark"], coll, bevel=0.004, seg=3))
    sp.append(B.tube("R21B_BRIEF_Screen_PullCord",
                     [(0.02, 0.0, 0.14), (0.02, 0.015, -0.10), (0.02, 0.0, -0.26)],
                     0.0035, mat["cable_black"], coll, sides=6))
    sp.append(B.cyl("R21B_BRIEF_Screen_CordGrip", 0.012, 0.055, (0.02, 0.0, -0.265),
                    mat["plastic"], coll, segments=12, bevel=0.003))
    for yy in (-1.0, 1.0):
        sp.append(B.box(f"R21B_BRIEF_Screen_Bracket{yy}", (0.055, 0.060, 0.06),
                        (-0.012, yy, 1.52), mat["steel_dark"], coll,
                        bevel=0.004, seg=3))
    screen = B.join(sp, "R21B_BRIEF_Screen", coll)
    B.place(screen, (-104.846, 17.65, 1.28))

    # ------------------------------------------------------------------ ceiling projector
    pp = []
    pp.append(B.box("R21B_BRIEF_Projector_MountPlate", (0.24, 0.24, 0.020), (0, 0, -0.010),
                    mat["dark"], coll, bevel=0.004, seg=3))
    pp.append(B.bolts("R21B_BRIEF_Projector_MountBolts",
                      [(-0.085, -0.085, -0.020), (0.085, -0.085, -0.020),
                       (-0.085, 0.085, -0.020), (0.085, 0.085, -0.020)],
                      (0, 0, -1), 0.007, 0.008, mat["steel_bare"], coll))
    pp.append(B.cyl("R21B_BRIEF_Projector_Pole", 0.034, 0.18, (0, 0, -0.11),
                    mat["steel_dark"], coll, segments=16, bevel=0.003))
    pp.append(B.cyl("R21B_BRIEF_Projector_Joint", 0.055, 0.075, (0, 0, -0.21),
                    mat["plastic"], coll, rot=(0, math.radians(90), 0), segments=18,
                    bevel=0.004))
    pp.append(B.box("R21B_BRIEF_Projector_Body", (0.38, 0.30, 0.115), (0, 0, -0.29),
                    mat["plastic"], coll, bevel=0.012, seg=4))
    pp.append(B.box("R21B_BRIEF_Projector_Top", (0.30, 0.24, 0.012), (0, 0, -0.226),
                    mat["dark"], coll, bevel=0.004, seg=3))
    # lens toward -X
    pp.append(B.cyl("R21B_BRIEF_Projector_LensBarrel", 0.052, 0.075, (-0.205, 0, -0.285),
                    mat["dark"], coll, rot=(0, math.radians(90), 0), segments=24, bevel=0.004))
    pp.append(B.cyl("R21B_BRIEF_Projector_LensRing", 0.058, 0.014, (-0.242, 0, -0.285),
                    mat["steel_bare"], coll, rot=(0, math.radians(90), 0), segments=24,
                    bevel=0.002))
    pp.append(B.cyl("R21B_BRIEF_Projector_Glass", 0.043, 0.006, (-0.247, 0, -0.285),
                    mat["screen_glow"], coll, rot=(0, math.radians(90), 0), segments=24,
                    bevel=0.001))
    # side vents
    for sx in (-1, 1):
        for i in range(6):
            pp.append(B.box(f"R21B_BRIEF_Projector_Vent{sx}_{i}", (0.055, 0.010, 0.008),
                            (0.08, sx * 0.151, -0.325 + i * 0.012), mat["dark"], coll,
                            bevel=0.0008, seg=1))
    pp.append(B.box("R21B_BRIEF_Projector_FootF", (0.045, 0.045, 0.020), (-0.13, 0.10, -0.355),
                    mat["rubber"], coll, bevel=0.003, seg=2))
    pp.append(B.box("R21B_BRIEF_Projector_FootB", (0.045, 0.045, 0.020), (0.13, -0.10, -0.355),
                    mat["rubber"], coll, bevel=0.003, seg=2))
    pp.append(B.tube("R21B_BRIEF_Projector_Cable",
                     [(0.10, 0.12, -0.31), (0.10, 0.14, -0.22), (0.10, 0.10, -0.16),
                      (0.10, 0.04, -0.05)], 0.005, mat["cable_black"], coll, sides=6))
    proj = B.join(pp, "R21B_BRIEF_Projector", coll)
    B.place(proj, (-100.25, 17.65, 4.699))

    # ------------------------------------------------------------------ credenza under board
    cp = []
    cp.append(B.box("R21B_BRIEF_Credenza_Plinth", (0.50, 3.00, 0.10), (0.25, 0, 0.05),
                    mat["dark"], coll, bevel=0.004, seg=3))
    cp.append(B.box("R21B_BRIEF_Credenza_Body", (0.55, 3.02, 0.66), (0.275, 0, 0.43),
                    mat["dark"], coll, bevel=0.006, seg=3))
    cp.append(B.box("R21B_BRIEF_Credenza_Top", (0.60, 3.08, 0.038), (0.30, 0, 0.80),
                    mat["steel_dark"], coll, bevel=0.006, seg=3))
    cp.append(B.box("R21B_BRIEF_Credenza_Kick", (0.03, 2.92, 0.09), (0.545, 0, 0.06),
                    mat["rubber"], coll, bevel=0.002, seg=2))
    for i, y in enumerate((-1.00, 0.0, 1.00)):
        cp.append(B.box(f"R21B_BRIEF_Credenza_Door{i}", (0.020, 0.94, 0.60),
                        (0.560, y, 0.45), mat["green"], coll, bevel=0.004, seg=3))
        cp.append(B.box(f"R21B_BRIEF_Credenza_DoorInset{i}", (0.010, 0.84, 0.50),
                        (0.571, y, 0.45), mat["green_dark"], coll, bevel=0.002, seg=2))
        cp.append(B.box(f"R21B_BRIEF_Credenza_Grip{i}", (0.020, 0.018, 0.17),
                        (0.590, y + 0.36, 0.47), mat["steel_bare"], coll,
                        bevel=0.003, seg=3))
        for gz in (-0.07, 0.07):
            cp.append(B.box(f"R21B_BRIEF_Credenza_GripPost{i}{gz}", (0.018, 0.016, 0.016),
                            (0.580, y + 0.36, 0.47 + gz), mat["steel_bare"], coll,
                            bevel=0.002, seg=2))
    # vent on centre door
    for i in range(5):
        cp.append(B.box(f"R21B_BRIEF_Credenza_Vent{i}", (0.006, 0.34, 0.008),
                        (0.574, 0.0, 0.20 + i * 0.022), mat["dark"], coll,
                        bevel=0.0006, seg=1))
    # articulated task lamp (off) on top
    cp.append(B.cyl("R21B_BRIEF_Credenza_LampBase", 0.075, 0.025, (0.30, -1.15, 0.835),
                    mat["dark"], coll, segments=22, bevel=0.004))
    cp.append(B.rod("R21B_BRIEF_Credenza_LampArmA", (0.30, -1.15, 0.85),
                            (0.30, -1.26, 1.20), 0.011, mat["steel_bare"], coll, 10))
    cp.append(B.rod("R21B_BRIEF_Credenza_LampArmB", (0.30, -1.26, 1.20),
                            (0.30, -1.08, 1.40), 0.010, mat["steel_bare"], coll, 10))
    cp.append(B.cyl("R21B_BRIEF_Credenza_LampJoint", 0.021, 0.045, (0.30, -1.26, 1.20),
                    mat["plastic"], coll, rot=(0, math.radians(90), 0), segments=14,
                    bevel=0.002))
    cp.append(B.cyl("R21B_BRIEF_Credenza_LampShade", 0.075, 0.12, (0.30, -1.02, 1.39),
                    mat["green"], coll, rot=(math.radians(55), 0, 0), segments=24,
                    bevel=0.003, r2=0.045))
    cp.append(B.tube("R21B_BRIEF_Credenza_LampCable",
                     [(0.30, -1.15, 0.84), (0.34, -1.10, 0.82), (0.42, -0.90, 0.82)],
                     0.0035, mat["cable_black"], coll, sides=6))
    # wall standoffs
    for y in (-1.42, 1.42):
        cp.append(B.box(f"R21B_BRIEF_Credenza_Bracket{y}", (0.05, 0.06, 0.10),
                        (0.02, y, 0.74), mat["steel_dark"], coll, bevel=0.003, seg=2))
    cred = B.join(cp, "R21B_BRIEF_Credenza", coll)
    B.place(cred, (-104.849, 21.20, 0.0))

    # ------------------------------------------------------------------ lectern
    lp = []
    lp.append(B.box("R21B_BRIEF_Lectern_Base", (0.60, 0.46, 0.045), (0, 0, 0.024),
                    mat["steel_dark"], coll, bevel=0.008, seg=4))
    lp.append(B.box("R21B_BRIEF_Lectern_Toe", (0.50, 0.38, 0.025), (0, 0, 0.058),
                    mat["rubber"], coll, bevel=0.004, seg=2))
    lp.append(B.box("R21B_BRIEF_Lectern_Column", (0.14, 0.12, 0.88), (0, 0, 0.50),
                    mat["green"], coll, bevel=0.008, seg=4))
    lp.append(B.box("R21B_BRIEF_Lectern_FrontPanel", (0.18, 0.02, 0.58), (0, -0.068, 0.43),
                    mat["green_dark"], coll, bevel=0.003, seg=3))
    lp.append(B.box("R21B_BRIEF_Lectern_Top", (0.68, 0.50, 0.055), (0, 0.02, 1.00),
                    mat["dark"], coll, rot=(math.radians(-16), 0, 0), bevel=0.008, seg=4))
    lp.append(B.box("R21B_BRIEF_Lectern_Shelf", (0.46, 0.22, 0.025), (0, -0.10, 0.68),
                    mat["steel_dark"], coll, bevel=0.004, seg=3))
    lp.append(B.bolts("R21B_BRIEF_Lectern_Bolts",
                      [(-0.24, -0.18, 0.055), (0.24, -0.18, 0.055),
                       (-0.24, 0.18, 0.055), (0.24, 0.18, 0.055)],
                      (0, 0, 1), 0.008, 0.010, mat["steel_bare"], coll))
    # gooseneck mic
    lp.append(B.tube("R21B_BRIEF_Lectern_MicGooseneck",
                     [(0.16, 0.10, 1.02), (0.17, 0.12, 1.12), (0.15, 0.08, 1.22),
                      (0.12, 0.02, 1.28)], 0.006, mat["steel_bare"], coll, sides=8))
    lp.append(B.cyl("R21B_BRIEF_Lectern_MicHead", 0.020, 0.055, (0.115, 0.005, 1.30),
                    mat["dark"], coll, rot=(math.radians(60), 0, math.radians(30)),
                    segments=16, bevel=0.004))
    lp.append(B.tube("R21B_BRIEF_Lectern_MicCable",
                     [(0.16, 0.10, 1.01), (0.18, 0.12, 0.80), (0.16, 0.12, 0.10),
                      (0.12, 0.16, 0.03)], 0.003, mat["cable_black"], coll, sides=6))
    lectern = B.join(lp, "R21B_BRIEF_Lectern", coll)
    B.place(lectern, (-100.70, 23.00, 0.0015), rot_z=124.0)

    # ------------------------------------------------------------------ coat rack
    kp = []
    kp.append(B.cyl("R21B_BRIEF_CoatRack_Base", 0.27, 0.035, (0, 0, 0.019),
                    mat["steel_dark"], coll, segments=28, bevel=0.006))
    kp.append(B.cyl("R21B_BRIEF_CoatRack_BaseCap", 0.23, 0.045, (0, 0, 0.050),
                    mat["dark"], coll, segments=28, bevel=0.008, r2=0.18))
    kp.append(B.cyl("R21B_BRIEF_CoatRack_Pole", 0.022, 1.72, (0, 0, 0.90),
                    mat["steel_bare"], coll, segments=18, bevel=0.002))
    kp.append(B.cyl("R21B_BRIEF_CoatRack_Collar", 0.032, 0.035, (0, 0, 0.12),
                    mat["steel_dark"], coll, segments=18, bevel=0.003))
    kp.append(B.cyl("R21B_BRIEF_CoatRack_Top", 0.034, 0.045, (0, 0, 1.775),
                    mat["dark"], coll, segments=18, bevel=0.006))
    kp.append(B.annulus("R21B_BRIEF_CoatRack_Ring", (0, 0, 1.60), 0.15, 0.135, 0.012,
                        mat["steel_bare"], coll))
    for i in range(7):
        a = math.radians(i * 51.4)
        p0 = (math.cos(a) * 0.02, math.sin(a) * 0.02, 1.68)
        p1 = (math.cos(a) * 0.12, math.sin(a) * 0.12, 1.70)
        p2 = (math.cos(a) * 0.18, math.sin(a) * 0.18, 1.76)
        p3 = (math.cos(a) * 0.16, math.sin(a) * 0.16, 1.82)
        kp.append(B.tube(f"R21B_BRIEF_CoatRack_Hook{i}", [p0, p1, p2, p3],
                         0.010, mat["steel_bare"], coll, sides=8))
    coat = B.join(kp, "R21B_BRIEF_CoatRack", coll)
    B.place(coat, (-103.55, 23.35, 0.0015))

    # ------------------------------------------------------------------ waste bins
    for i, (x, y, style) in enumerate(((-102.85, 18.90, "metal"),
                                       (-99.80, 23.05, "plastic"))):
        bp2 = []
        if style == "metal":
            bp2.append(B.box(f"R21B_BRIEF_Bin{i}_Body", (0.32, 0.32, 0.47), (0, 0, 0.235),
                             mat["steel_dark"], coll, bevel=0.010, seg=4))
            bp2.append(B.box(f"R21B_BRIEF_Bin{i}_Lid", (0.35, 0.35, 0.035), (0, 0, 0.485),
                             mat["galv"], coll, bevel=0.006, seg=3))
        else:
            bp2.append(B.box(f"R21B_BRIEF_Bin{i}_Body", (0.34, 0.34, 0.52), (0, 0, 0.260),
                             mat["green"], coll, bevel=0.010, seg=4))
            bp2.append(B.box(f"R21B_BRIEF_Bin{i}_Lid", (0.37, 0.37, 0.040), (0, 0, 0.520),
                             mat["green_dark"], coll, bevel=0.008, seg=4))
        hy = 0.500 if style == "metal" else 0.525
        bp2.append(B.box(f"R21B_BRIEF_Bin{i}_Handle", (0.10, 0.030, 0.025),
                         (0, 0.165, hy), mat["dark"], coll, bevel=0.004, seg=3))
        ob = B.join(bp2, f"R21B_BRIEF_Bin_{i:02d}", coll)
        B.place(ob, (x, y, 0.0015))

        # ------------------------------------------------------------------ plants
    for i, (x, y, scale) in enumerate(((-104.05, 24.15, 1.05), (-103.95, 16.25, 0.90))):
        pp2 = []
        pp2.append(B.cyl(f"R21B_BRIEF_Plant{i}_Pot", 0.18 * scale, 0.40 * scale,
                         (0, 0, 0.20 * scale), mat["ceramic"], coll, segments=28,
                         bevel=0.006, r2=0.215 * scale))
        pp2.append(B.annulus(f"R21B_BRIEF_Plant{i}_Rim", (0, 0, 0.40 * scale),
                             0.222 * scale, 0.195 * scale, 0.025 * scale,
                             mat["ceramic"], coll))
        pp2.append(B.cyl(f"R21B_BRIEF_Plant{i}_Soil", 0.195 * scale, 0.020,
                         (0, 0, 0.392 * scale), mat["soil"], coll, segments=26, bevel=0.003))
        for s in range(4):
            a = math.radians(s * 93 + i * 20)
            rr = 0.11 * scale
            pp2.append(B.rock(f"R21B_BRIEF_Plant{i}_Stone{s}",
                              (math.cos(a) * rr, math.sin(a) * rr, 0.405 * scale),
                              (0.035 * scale, 0.028 * scale, 0.020 * scale),
                              mat["stone"], coll, seed=s + 20 * i, subdiv=1))
        pot = B.join(pp2, f"R21B_BRIEF_Plant{i}_PotGroup", coll)
        B.place(pot, (x, y, 0.0015))
        leaves = []
        count = 17 if i == 0 else 13
        for k in range(count):
            a = math.radians(k * 360.0 / count + rnd.uniform(-10, 10))
            rr = rnd.uniform(0.02, 0.12) * scale
            base = (x + math.cos(a) * rr, y + math.sin(a) * rr, 0.386 * scale)
            l = rnd.uniform(0.58, 1.02) * scale
            w = rnd.uniform(0.030, 0.055) * scale
            tx = rnd.uniform(-16, 16)
            ty = rnd.uniform(-16, 16)
            tw = rnd.uniform(-24, 24)
            mm = mat["plant_dark"] if k % 3 else mat["plant_light"]
            lf = B.leaf(f"R21B_BRIEF_Plant{i}_Leaf{k:02d}", base, l, w, tx, ty, tw,
                        mm, coll, seed=k + 100 * i, curve=0.35)
            lf.rotation_mode = "XYZ"
            # add yaw around the pot centre after the tilt
            lf.rotation_euler.rotate_axis("Z", a)
            leaves.append(lf)
        lv = B.join(leaves, f"R21B_BRIEF_Plant{i}_Foliage", coll)

    # ------------------------------------------------------------------ floor power tower
    fp = []
    fp.append(B.box("R21B_BRIEF_PowerTower_Base", (0.20, 0.15, 0.035), (0, 0, 0.018),
                    mat["steel_dark"], coll, bevel=0.005, seg=3))
    fp.append(B.box("R21B_BRIEF_PowerTower_Body", (0.18, 0.13, 0.13), (0, 0, 0.10),
                    mat["plastic"], coll, bevel=0.008, seg=4))
    fp.append(B.box("R21B_BRIEF_PowerTower_Top", (0.16, 0.11, 0.012), (0, 0, 0.17),
                    mat["dark"], coll, bevel=0.004, seg=3))
    for i in range(4):
        fp.append(B.box(f"R21B_BRIEF_PowerTower_Socket{i}", (0.040, 0.010, 0.042),
                        (-0.060 + i * 0.040, -0.068, 0.10), mat["dark"], coll,
                        bevel=0.002, seg=2))
    fp.append(B.tube("R21B_BRIEF_PowerTower_Cable",
                     [(0.0, 0.05, 0.04), (0.10, 0.10, 0.015), (0.55, 0.35, 0.012),
                      (1.10, 0.10, 0.008)], 0.006, mat["cable_black"], coll, sides=6))
    tower = B.join(fp, "R21B_BRIEF_PowerTower", coll)
    B.place(tower, (-99.25, 18.85, 0.0015))

    # one floor mat at the briefing edge (rubber, no dirt narrative)
    mp = []
    mp.append(B.box("R21B_BRIEF_Mat_Base", (2.2, 0.95, 0.012), (0, 0, 0.006),
                    mat["rubber"], coll, bevel=0.004, seg=3))
    mp.append(B.box("R21B_BRIEF_Mat_Border", (2.10, 0.85, 0.004), (0, 0, 0.012),
                    mat["rubber_red"], coll, bevel=0.002, seg=2))
    mat_ob = B.join(mp, "R21B_BRIEF_EntryMat", coll)
    B.place(mat_ob, (-101.55, 24.55, 0.0))

    return coll


# --------------------------------------------------------------------------------------
# training chair
# --------------------------------------------------------------------------------------
def training_chair(name, mat, coll, origin, facing_deg=0.0, tipped=False):
    p = []
    # legs + feet
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        foot = (sx * 0.215, sy * 0.185, 0.012)
        top = (sx * 0.185, sy * 0.155, 0.43)
        p.append(B.cyl(f"{name}_Foot{i}", 0.022, 0.024, foot, mat["rubber"], coll,
                       segments=14, bevel=0.004))
        p.append(B.rod(f"{name}_Leg{i}", (foot[0], foot[1], 0.02),
                       top, 0.0135, mat["steel_dark"], coll, 12))
    # seat frame
    p.append(B.box(name + "_SeatFrame", (0.47, 0.45, 0.035), (0, 0, 0.435),
                   mat["steel_dark"], coll, bevel=0.006, seg=3))
    p.append(B.box(name + "_SeatPan", (0.455, 0.435, 0.020), (0, 0, 0.458),
                   mat["dark"], coll, bevel=0.006, seg=3))
    p.append(B.box(name + "_SeatCushion", (0.460, 0.440, 0.060), (0, 0, 0.492),
                   mat["fabric"], coll, bevel=0.024, seg=4))
    p.append(B.box(name + "_SeatSeam", (0.410, 0.004, 0.004), (0, -0.185, 0.5235),
                   mat["dark"], coll, bevel=0.0006, seg=1))
    # back supports
    for sx in (-1, 1):
        p.append(B.rod(f"{name}_BackSpine{sx}", (sx * 0.16, -0.20, 0.44),
                       (sx * 0.16, -0.225, 0.73), 0.0125, mat["steel_dark"], coll, 10))
    p.append(B.box(name + "_BackShell", (0.455, 0.055, 0.43), (0, -0.245, 0.815),
                   mat["dark"], coll, rot=(math.radians(8), 0, 0), bevel=0.020, seg=4))
    p.append(B.box(name + "_BackCushion", (0.415, 0.055, 0.365), (0, -0.278, 0.812),
                   mat["fabric"], coll, rot=(math.radians(8), 0, 0), bevel=0.026, seg=4))
    p.append(B.box(name + "_Lumbar", (0.350, 0.040, 0.075), (0, -0.255, 0.665),
                   mat["fabric"], coll, rot=(math.radians(8), 0, 0), bevel=0.016, seg=3))
    p.append(B.box(name + "_BackTopRail", (0.390, 0.020, 0.022), (0, -0.260, 1.005),
                   mat["steel_dark"], coll, rot=(math.radians(8), 0, 0), bevel=0.004, seg=3))
    # bolts + cross brace
    p.append(B.rod(name + "_CrossA", (-0.20, -0.10, 0.23), (0.20, 0.10, 0.23),
                   0.008, mat["steel_bare"], coll, 8))
    p.append(B.rod(name + "_CrossB", (-0.20, 0.10, 0.23), (0.20, -0.10, 0.23),
                   0.008, mat["steel_bare"], coll, 8))
    ob = B.join(p, name, coll)
    if not tipped:
        B.place(ob, origin, rot_z=facing_deg)
    else:
        B.place(ob, origin, rot_z=facing_deg, rot=(0, 97.0, 0), drop=True)
    return ob
