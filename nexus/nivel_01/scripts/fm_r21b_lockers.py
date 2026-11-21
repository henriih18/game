"""Lockers / equipment zone for L1_SECURITY_R21B_HERO (east-south of Security 03)."""
import math
import random
import bpy
from mathutils import Vector, Matrix

import fm_ops_lib as L
import fm_r21b_lib as B


# --------------------------------------------------------------------------------------
# locker bank
# --------------------------------------------------------------------------------------
def locker_bank(name, mat, coll, W=4.40, H=1.98, D=0.50, doors=8,
                open_angles=None, dented=None, mirror_door=None):
    rnd = random.Random(331)
    parts = []
    # plinth and carcass
    parts.append(B.box(name + "_Plinth", (D - 0.05, W - 0.02, 0.085),
                       (-(D - 0.05) * 0.5 - 0.02, W * 0.5, 0.044),
                       mat["dark"], coll, bevel=0.004, seg=3))
    parts.append(B.box(name + "_Bottom", (D - 0.02, W - 0.02, 0.035),
                       (-(D - 0.02) * 0.5, W * 0.5, 0.103),
                       mat["steel_dark"], coll, bevel=0.004, seg=3))
    parts.append(B.box(name + "_Top", (D, W - 0.006, 0.035), (-D * 0.5, W * 0.5, H - 0.0175),
                       mat["steel_dark"], coll, bevel=0.005, seg=3))
    for i, yy in enumerate((0.011, W - 0.011)):
        parts.append(B.box(f"{name}_Side{i}", (D, 0.022, H - 0.12),
                           (-D * 0.5, yy, 0.115 + (H - 0.12) * 0.5),
                           mat["steel_dark"], coll, bevel=0.004, seg=3))
    dw = (W - 0.025) / doors
    for i in range(doors + 1):
        yy = 0.0125 + i * dw
        if i == 0:
            yy = 0.033
        elif i == doors:
            yy = W - 0.033
        parts.append(B.box(f"{name}_Div{i}", (D - 0.022, 0.020, H - 0.145),
                           (-(D - 0.022) * 0.5 - 0.001, yy, 0.12 + (H - 0.145) * 0.5),
                           mat["steel_dark"], coll, bevel=0.003, seg=2))
    # compartment shelf + rod + back plate
    for i in range(doors):
        yc = 0.0125 + (i + 0.5) * dw
        # foot
        parts.append(B.box(f"{name}_Foot{i}", (0.06, 0.06, 0.022),
                           (-D + 0.09, 0.0125 + i * dw + 0.05, 0.011),
                           mat["rubber"], coll, bevel=0.003, seg=2))

    # door objects (openable, individually built around their hinge)
    door_objs = []
    for i in range(doors):
        dwi = dw - 0.008
        hd = H - 0.18
        doorw = dwi
        dp = []
        # one-piece picture frame (no coplanar corner overlaps)
        dp.append(B.frame_rect(f"{name}_D{i}_Frame", doorw, 1.803,
                               doorw - 0.096, 1.707, 0.018,
                               (-0.009, doorw * 0.5, 0.9675), mat["green"], coll))
        dented_door = dented is not None and i in dented
        if dented_door:
            # lower panel is bent inwards, with a visible crease (accidental damage)
            dp.append(B.box(f"{name}_D{i}_PanelLow", (0.006, doorw - 0.020, 0.900),
                            (-0.007, doorw * 0.5, 0.535),
                            mat["green_dark"], coll, rot=(0, math.radians(3.5), 0),
                            bevel=0.0015, seg=2))
            dp.append(B.box(f"{name}_D{i}_PanelHigh", (0.006, doorw - 0.020, 0.870),
                            (-0.007, doorw * 0.5, 1.420),
                            mat["green_dark"], coll, bevel=0.0015, seg=2))
            dp.append(B.box(f"{name}_D{i}_Crease", (0.010, doorw - 0.08, 0.012),
                            (-0.016, doorw * 0.5, 0.985),
                            mat["dark"], coll, bevel=0.001, seg=1))
            dp.append(B.box(f"{name}_D{i}_Scuff", (0.003, 0.13, 0.08),
                            (-0.014, doorw * 0.62, 0.46), mat["rust"], coll,
                            bevel=0.001, seg=1))
        else:
            dp.append(B.box(f"{name}_D{i}_Panel", (0.006, doorw - 0.020, 1.775),
                            (-0.007, doorw * 0.5, 0.9675),
                            mat["green_dark"], coll, bevel=0.0015, seg=2))
        # seam shadow strips
        for yy in (0.06, doorw - 0.06):
            dp.append(B.box(f"{name}_D{i}_Seam{yy:.2f}", (0.004, 0.005, hd - 0.14),
                            (-0.011, yy, 0.10 + (hd - 0.10) * 0.5),
                            mat["dark"], coll, bevel=0.0005, seg=1))
        # lock + grip + label
        hy = doorw - 0.075
        dp.append(B.cyl(f"{name}_D{i}_Lock", 0.017, 0.012, (-0.024, hy, 0.93),
                        mat["steel_bare"], coll, rot=(0, math.radians(90), 0),
                        segments=16, bevel=0.002))
        dp.append(B.box(f"{name}_D{i}_KeySlot", (0.004, 0.007, 0.016),
                        (-0.029, hy, 0.93), mat["dark"], coll, bevel=0.0006, seg=1))
        dp.append(B.box(f"{name}_D{i}_Grip", (0.020, 0.020, 0.18),
                        (-0.042, doorw - 0.15, 0.96), mat["steel_bare"], coll,
                        bevel=0.003, seg=3))
        for gz in (-0.075, 0.075):
            dp.append(B.box(f"{name}_D{i}_GripPost{gz:.2f}", (0.030, 0.014, 0.016),
                            (-0.026, doorw - 0.15, 0.96 + gz), mat["steel_bare"], coll,
                            bevel=0.002, seg=2))
        # hinges at the pivot line
        for hz in (0.42, 1.42):
            dp.append(B.cyl(f"{name}_D{i}_Hinge{hz}", 0.010, 0.085,
                            (-0.009, 0.0, hz), mat["steel_bare"], coll, segments=12,
                            bevel=0.001))
            dp.append(B.box(f"{name}_D{i}_HingePlateA{hz}", (0.030, 0.012, 0.080),
                            (-0.021, 0.0, hz), mat["steel_dark"], coll, bevel=0.002, seg=2))
            dp.append(B.box(f"{name}_D{i}_HingePlateB{hz}", (0.014, 0.040, 0.080),
                            (0.002, 0.026, hz), mat["steel_dark"], coll, bevel=0.002, seg=2))
        if mirror_door is not None and i == mirror_door:
            dp.append(B.box(f"{name}_D{i}_Mirror", (0.006, doorw - 0.10, 0.52),
                            (0.004, doorw * 0.5, 1.05), mat["aluminum"], coll,
                            bevel=0.002, seg=2))
            for my in (0.10, doorw - 0.10):
                for mz in (0.82, 1.28):
                    dp.append(B.cyl(f"{name}_D{i}_MirrorScrew{my:.2f}{mz:.2f}", 0.007, 0.006,
                                    (0.009, my, mz), mat["steel_bare"], coll,
                                    rot=(0, math.radians(90), 0), segments=8, bevel=0.001))
        door = B.join(dp, f"{name}_Door{i:02d}", coll)
        B.bake_world(door)
        hinge_y = 0.0125 + i * dw + 0.004
        angle = 0.0
        if open_angles and i in open_angles:
            angle = open_angles[i]
        door.matrix_world = (Matrix.Translation(Vector((-D - 0.002, hinge_y, 0.0))) @
                             Matrix.Rotation(math.radians(angle), 4, "Z"))
        door_objs.append(door)
    parts.extend(door_objs)
    bank = B.join(parts, name, coll)
    return bank


def build(mat, coll):
    rnd = random.Random(9921)

    # ------------------------------------------------------------------ lockers A (east wall)
    bank_a = locker_bank("R21B_LOCK_BankA", mat, coll,
                         open_angles={1: 24.0, 4: 67.0, 7: 9.0},
                         dented={3, 6}, mirror_door=4)
    B.place(bank_a, (-71.149, 13.40, 0.0015), rot_z=0.0)

    # ------------------------------------------------------------------ lockers B (south wall)
    bank_b = locker_bank("R21B_LOCK_BankB", mat, coll,
                         open_angles={2: 45.0, 5: 15.0},
                         dented={0}, mirror_door=2)
    B.place(bank_b, (-80.60, 10.149, 0.0015), rot_z=-90.0)

    # ------------------------------------------------------------------ bench A (east)
    bench_a = changing_bench("R21B_LOCK_BenchA", mat, coll, length=2.40, width=0.42)
    B.place(bench_a, (-72.52, 15.55, 0.0015), rot_z=90.0)

    # ------------------------------------------------------------------ bench B (south)
    bench_b = changing_bench("R21B_LOCK_BenchB", mat, coll, length=2.40, width=0.42)
    B.place(bench_b, (-78.20, 11.38, 0.0015), rot_z=0.0)

    # ------------------------------------------------------------------ radio charging station
    rp = []
    rp.append(B.box("R21B_LOCK_Radio_Body", (0.230, 1.60, 1.00), (-0.125, 0.80, 0.50),
                    mat["green"], coll, bevel=0.010, seg=4))
    rp.append(B.box("R21B_LOCK_Radio_Face", (0.020, 1.54, 0.94), (-0.248, 0.80, 0.50),
                    mat["green_dark"], coll, bevel=0.004, seg=3))
    # top/bottom lips and cable plinth
    rp.append(B.box("R21B_LOCK_Radio_TopLip", (0.060, 1.62, 0.030), (-0.260, 0.80, 1.005),
                    mat["steel_dark"], coll, bevel=0.004, seg=3))
    rp.append(B.box("R21B_LOCK_Radio_BotLip", (0.060, 1.62, 0.030), (-0.260, 0.80, 0.015),
                    mat["steel_dark"], coll, bevel=0.004, seg=3))
    rp.append(B.box("R21B_LOCK_Radio_CableTray", (0.120, 1.44, 0.045), (-0.220, 0.80, 0.075),
                    mat["galv"], coll, bevel=0.003, seg=3))
    # six slots
    for i in range(6):
        y = 0.14 + i * 0.264
        # handheld radio in dock
        rp.append(radio(f"R21B_LOCK_Radio_Unit{i}", (-0.271, y, 0.163), mat, coll,
                        rot_z=0.0, antenna=0.10))
    # lock, side bolts, vents, cable glands
    rp.append(B.cyl("R21B_LOCK_Radio_Lock", 0.018, 0.014, (-0.262, 1.53, 0.86),
                    mat["steel_bare"], coll, rot=(0, math.radians(90), 0), segments=16,
                    bevel=0.002))
    rp.append(B.box("R21B_LOCK_Radio_Label", (0.004, 0.32, 0.070), (-0.262, 1.26, 0.925),
                    mat["paper"], coll, bevel=0.001, seg=2))
    radio_station = B.join(rp, "R21B_LOCK_RadioStation", coll)
    B.place(radio_station, (-71.149, 18.15, 1.15))

    # ------------------------------------------------------------------ key cabinet
    kp = []
    kp.append(B.box("R21B_LOCK_Keys_Back", (0.020, 0.82, 0.82), (-0.010, 0.41, 0.41),
                    mat["green"], coll, bevel=0.004, seg=3))
    kp.append(B.box("R21B_LOCK_Keys_Header", (0.006, 0.60, 0.10), (-0.022, 0.41, 0.72),
                    mat["paper"], coll, bevel=0.001, seg=2))
    for row, z in enumerate((0.58, 0.40, 0.22)):
        for k in range(4):
            y = 0.14 + k * 0.18
            kp.append(B.tube(f"R21B_LOCK_Keys_Hook{row}_{k}",
                             [(-0.020, y, z + 0.08), (-0.045, y, z + 0.07),
                              (-0.050, y, z + 0.04)], 0.0035, mat["steel_bare"], coll, sides=6))
            kp.append(B.box(f"R21B_LOCK_Keys_Tag{row}_{k}", (0.006, 0.045, 0.070),
                            (-0.047, y, z - 0.01), mat["paint_red"] if k % 2 else mat["hazard_y"],
                            coll, bevel=0.001, seg=2))
            kp.append(B.box(f"R21B_LOCK_Keys_Key{row}_{k}", (0.004, 0.012, 0.055),
                            (-0.051, y, z - 0.04), mat["aluminum"], coll,
                            bevel=0.001, seg=1))
    key_cab = B.join(kp, "R21B_LOCK_KeyCabinet", coll)
    B.place(key_cab, (-71.149, 20.10, 1.25))

    # ------------------------------------------------------------------ first aid cabinet
    fp = []
    fp.append(B.box("R21B_LOCK_FirstAid_Body", (0.150, 0.72, 0.72), (-0.075, 0.36, 0.36),
                    mat["white"], coll, bevel=0.008, seg=4))
    fp.append(B.box("R21B_LOCK_FirstAid_Door", (0.022, 0.66, 0.66), (-0.158, 0.36, 0.36),
                    mat["white"], coll, bevel=0.005, seg=3))
    # green cross
    fp.append(B.box("R21B_LOCK_FirstAid_CrossV", (0.006, 0.100, 0.300), (-0.171, 0.36, 0.38),
                    mat["sign_green"], coll, bevel=0.002, seg=2))
    fp.append(B.box("R21B_LOCK_FirstAid_CrossH", (0.006, 0.300, 0.100), (-0.169, 0.36, 0.38),
                    mat["sign_green"], coll, bevel=0.002, seg=2))
    fp.append(B.box("R21B_LOCK_FirstAid_Grip", (0.020, 0.020, 0.14), (-0.180, 0.66, 0.36),
                    mat["steel_bare"], coll, bevel=0.003, seg=3))
    for gz in (-0.055, 0.055):
        fp.append(B.box(f"R21B_LOCK_FirstAid_GripPost{gz}", (0.026, 0.014, 0.014),
                        (-0.166, 0.66, 0.36 + gz), mat["steel_bare"], coll,
                        bevel=0.002, seg=2))
    for z in (0.10, 0.36, 0.62):
        fp.append(B.cyl(f"R21B_LOCK_FirstAid_Hinge{z}", 0.007, 0.060, (-0.168, 0.03, z),
                        mat["steel_bare"], coll, segments=10, bevel=0.001))
    fp.append(B.box("R21B_LOCK_FirstAid_Latch", (0.022, 0.030, 0.055), (-0.176, 0.03, 0.36),
                    mat["steel_bare"], coll, bevel=0.003, seg=2))
    fp.append(B.box("R21B_LOCK_FirstAid_Label", (0.004, 0.22, 0.040), (-0.172, 0.36, 0.64),
                    mat["sign_green"], coll, bevel=0.001, seg=2))
    first_aid = B.join(fp, "R21B_LOCK_FirstAid", coll)
    B.place(first_aid, (-71.149, 21.10, 1.30))

    # ------------------------------------------------------------------ extinguisher (south wall)
    ex = extinguisher("R21B_LOCK_Extinguisher", mat, coll)
    B.place(ex, (-75.55, 10.352, 0.0015), rot_z=-90.0)

    # ------------------------------------------------------------------ locker-room mat
    mp = []
    mp.append(B.box("R21B_LOCK_MatLockers_Base", (1.80, 0.90, 0.012), (0, 0, 0.006),
                    mat["rubber"], coll, bevel=0.004, seg=3))
    mat_ob = B.join(mp, "R21B_LOCK_MatLockers", coll)
    B.place(mat_ob, (-75.40, 12.20, 0.0015))

    # ------------------------------------------------------------------ equipment shelving
    shelf_parts = []
    W, H, D = 2.20, 2.30, 0.56
    # uprights
    for yy in (0.02, W - 0.02):
        shelf_parts.append(B.box(f"R21B_LOCK_Shelf_Upright{yy}", (D, 0.045, H),
                                 (-D * 0.5, yy, H * 0.5), mat["steel_dark"], coll,
                                 bevel=0.004, seg=3))
        for k in range(8):
            shelf_parts.append(B.box(f"R21B_LOCK_Shelf_Slot{yy}_{k}", (0.006, 0.014, 0.070),
                                     (-D - 0.001, yy, 0.28 + k * 0.24), mat["dark"], coll,
                                     bevel=0.001, seg=1))
        shelf_parts.append(B.box(f"R21B_LOCK_Shelf_Foot{yy}", (D + 0.06, 0.16, 0.020),
                                 (-D * 0.5, yy, 0.009), mat["steel_dark"], coll,
                                 bevel=0.003, seg=2))
        shelf_parts.append(B.bolts(f"R21B_LOCK_Shelf_FootBolts{yy}",
                                   [(-D + 0.08, yy, 0.022), (-0.10, yy, 0.022)],
                                   (0, 0, 1), 0.007, 0.010, mat["steel_bare"], coll))
    # cross rails / shelves
    for i, z in enumerate((0.32, 0.92, 1.50, 2.06)):
        shelf_parts.append(B.box(f"R21B_LOCK_Shelf_Deck{i}", (D - 0.02, W - 0.05, 0.025),
                                 (-D * 0.5, W * 0.5, z), mat["galv"], coll,
                                 bevel=0.003, seg=3))
    # equipment: 3 cases, helmets, coiled rope, bins
    # hard hats on top shelf
    for i, yy in enumerate((0.42, 1.02)):
        shelf_parts.append(hard_hat(f"R21B_LOCK_Hat{i}", (-0.29, yy, 2.019), mat, coll,
                                    rot_z=i * 18.0))
    # coiled rope / cable on shelf
    shelf = B.join(shelf_parts, "R21B_LOCK_Shelving", coll)
    B.place(shelf, (-71.149, 22.18, 0.0015), rot_z=0.0)

    return coll


# --------------------------------------------------------------------------------------
# bench
# --------------------------------------------------------------------------------------
def changing_bench(name, mat, coll, length=2.4, width=0.42):
    p = []
    # seat slats (5) along length, across width
    for i in range(5):
        y = -width * 0.5 + 0.05 + i * (width - 0.10) / 4
        p.append(B.box(f"{name}_Slat{i}", (length - 0.10, 0.062, 0.035),
                       (0, y, 0.445), mat["wood"], coll, bevel=0.006, seg=3))
    # end frames
    for sx in (-1, 1):
        x = sx * (length * 0.5 - 0.11)
        p.append(B.box(f"{name}_EndFrame{sx}", (0.06, width - 0.02, 0.055),
                       (x, 0, 0.425), mat["steel_dark"], coll, bevel=0.004, seg=3))
        p.append(B.box(f"{name}_LegF{sx}", (0.045, 0.055, 0.40),
                       (x, width * 0.5 - 0.06, 0.22), mat["steel_dark"], coll,
                       bevel=0.004, seg=3))
        p.append(B.box(f"{name}_LegB{sx}", (0.045, 0.055, 0.40),
                       (x, -width * 0.5 + 0.06, 0.22), mat["steel_dark"], coll,
                       bevel=0.004, seg=3))
        p.append(B.box(f"{name}_FootF{sx}", (0.060, 0.065, 0.020),
                       (x, width * 0.5 - 0.06, 0.010), mat["rubber"], coll,
                       bevel=0.003, seg=2))
        p.append(B.box(f"{name}_FootB{sx}", (0.060, 0.065, 0.020),
                       (x, -width * 0.5 + 0.06, 0.010), mat["rubber"], coll,
                       bevel=0.003, seg=2))
    ob = B.join(p, name, coll)
    return ob


# --------------------------------------------------------------------------------------
# handheld radio
# --------------------------------------------------------------------------------------
def radio(name, center, mat, coll, rot_z=0.0, antenna=0.09):
    p = []
    p.append(B.box(name + "_Body", (0.042, 0.060, 0.155), (0, 0, 0.088),
                   mat["plastic"], coll, bevel=0.006, seg=4))
    p.append(B.box(name + "_Face", (0.010, 0.046, 0.100), (-0.024, 0, 0.090),
                   mat["dark"], coll, bevel=0.002, seg=3))
    p.append(B.box(name + "_Screen", (0.002, 0.034, 0.030), (-0.030, 0, 0.120),
                   mat["screen_glow"], coll, bevel=0.0005, seg=1))
    p.append(B.cyl(name + "_Knob", 0.013, 0.014, (0, 0.014, 0.170),
                   mat["dark"], coll, segments=12, bevel=0.002))
    p.append(B.cyl(name + "_Antenna", 0.004, antenna, (0, -0.018, 0.165 + antenna * 0.5),
                   mat["rubber"], coll, segments=8, bevel=0.0008))
    p.append(B.box(name + "_PTT", (0.010, 0.010, 0.035), (-0.020, 0.031, 0.075),
                   mat["rubber"], coll, bevel=0.002, seg=2))
    p.append(B.box(name + "_Grille", (0.004, 0.030, 0.028), (-0.029, 0, 0.055),
                   mat["dark"], coll, bevel=0.0006, seg=1))
    p.append(B.box(name + "_ChargeContact", (0.020, 0.036, 0.006), (0, 0, 0.005),
                   mat["copper"], coll, bevel=0.001, seg=2))
    ob = B.join(p, name, coll)
    B.place(ob, center, rot_z=rot_z)
    return ob


# --------------------------------------------------------------------------------------
# extinguisher
# --------------------------------------------------------------------------------------
def extinguisher(name, mat, coll):
    p = []
    p.append(B.cyl(name + "_Body", 0.155, 0.430, (0, 0, 0.245), mat["paint_red"], coll,
                   segments=32, bevel=0.010, r2=0.145))
    p.append(B.cyl(name + "_TopDome", 0.145, 0.075, (0, 0, 0.495), mat["paint_red"], coll,
                   segments=32, bevel=0.008, r2=0.070))
    p.append(B.cyl(name + "_Bottom", 0.145, 0.035, (0, 0, 0.025), mat["paint_red"], coll,
                   segments=32, bevel=0.006, r2=0.158))
    p.append(B.cyl(name + "_Neck", 0.042, 0.055, (0, 0, 0.550), mat["steel_bare"], coll,
                   segments=18, bevel=0.003))
    p.append(B.box(name + "_Valve", (0.095, 0.070, 0.070), (0, 0, 0.590),
                   mat["steel_dark"], coll, bevel=0.006, seg=3))
    p.append(B.box(name + "_LeverTop", (0.150, 0.030, 0.022), (-0.010, 0, 0.642),
                   mat["steel_dark"], coll, bevel=0.004, seg=3))
    p.append(B.box(name + "_LeverBot", (0.125, 0.032, 0.018), (0.010, 0, 0.610),
                   mat["steel_dark"], coll, bevel=0.004, seg=3))
    p.append(B.cyl(name + "_Pin", 0.006, 0.090, (0.045, 0.020, 0.632), mat["steel_bare"],
                   coll, rot=(0, math.radians(90), 0), segments=8, bevel=0.001))
    p.append(B.cyl(name + "_Gauge", 0.034, 0.024, (0.055, -0.055, 0.585), mat["steel_bare"],
                   coll, rot=(math.radians(90), 0, 0), segments=20, bevel=0.003))
    p.append(B.cyl(name + "_GaugeFace", 0.027, 0.004, (0.055, -0.068, 0.585), mat["white"],
                   coll, rot=(math.radians(90), 0, 0), segments=20, bevel=0.001))
    p.append(B.box(name + "_GaugeNeedle", (0.030, 0.003, 0.004), (0.055, -0.071, 0.585),
                   mat["red"], coll, rot=(0, 0, 20), bevel=0.0004, seg=1))
    # hose and nozzle
    p.append(B.tube(name + "_Hose",
                    [(0.02, -0.035, 0.575), (0.06, -0.08, 0.52), (0.13, -0.10, 0.40),
                     (0.15, -0.08, 0.28), (0.12, -0.04, 0.22)], 0.011,
                    mat["rubber"], coll, sides=8))
    p.append(B.cyl(name + "_Nozzle", 0.017, 0.115, (0.115, -0.04, 0.17), mat["steel_dark"],
                   coll, rot=(math.radians(75), 0, 0), segments=14, bevel=0.003,
                   r2=0.010))
    p.append(B.cyl(name + "_NozzleTip", 0.012, 0.045, (0.115, -0.075, 0.115),
                   mat["steel_bare"], coll, rot=(math.radians(75), 0, 0), segments=12,
                   bevel=0.002))
    # label band (no text)
    p.append(B.cyl(name + "_LabelBand", 0.157, 0.10, (0, 0, 0.330), mat["white"], coll,
                   segments=32, bevel=0.001))
    p.append(B.cyl(name + "_LabelBandRed", 0.159, 0.020, (0, 0, 0.385), mat["paint_red"],
                   coll, segments=32, bevel=0.001))
    p.append(B.cyl(name + "_LabelBandRed2", 0.159, 0.020, (0, 0, 0.275), mat["paint_red"],
                   coll, segments=32, bevel=0.001))
    # wall bracket
    p.append(B.box(name + "_Bracket", (0.060, 0.260, 0.300), (0.170, 0, 0.350),
                   mat["steel_dark"], coll, bevel=0.005, seg=3))
    p.append(B.box(name + "_BracketArm", (0.100, 0.050, 0.040), (0.120, 0, 0.470),
                   mat["steel_dark"], coll, bevel=0.004, seg=3))
    p.append(B.box(name + "_BracketStrap", (0.030, 0.340, 0.055), (0.150, 0, 0.360),
                   mat["steel_bare"], coll, bevel=0.004, seg=3))
    p.append(B.bolts(name + "_BracketBolts",
                     [(0.200, -0.09, 0.23), (0.200, 0.09, 0.23),
                      (0.200, -0.09, 0.47), (0.200, 0.09, 0.47)],
                     (1, 0, 0), 0.007, 0.010, mat["steel_bare"], coll))
    ob = B.join(p, name, coll)
    return ob


# --------------------------------------------------------------------------------------
# flight case / hard hat
# --------------------------------------------------------------------------------------
def flight_case(name, center, size, mat, coll, rot_z=0.0):
    w, d, h = size
    p = []
    p.append(B.box(name + "_Body", (w, d, h), (0, 0, h * 0.5), mat["plastic"], coll,
                   bevel=0.010, seg=4))
    p.append(B.box(name + "_Lid", (w + 0.004, d + 0.004, h * 0.16), (0, 0, h * 0.90),
                   mat["dark"], coll, bevel=0.004, seg=3))
    for sy in (-1, 1):
        p.append(B.box(f"{name}_Latch{sy}", (0.060, 0.018, 0.055),
                       (0, sy * (d * 0.5 + 0.004), h * 0.78), mat["steel_bare"], coll,
                       bevel=0.003, seg=3))
    p.append(B.box(name + "_Handle", (0.120, 0.026, 0.035), (0, -d * 0.5 - 0.02, h * 0.72),
                   mat["rubber"], coll, bevel=0.006, seg=3))
    ob = B.join(p, name, coll)
    B.place(ob, center, rot_z=rot_z)
    return ob


def hard_hat(name, center, mat, coll, rot_z=0.0):
    p = []
    # dome approximated by a squashed sphere cut at the brim
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=28, v_segments=14, radius=1.0)
    for v in bm.verts:
        v.co.x *= 0.135
        v.co.y *= 0.165
        v.co.z *= 0.115
        if v.co.z < 0.0:
            v.co.z = 0.0
    me = bpy.data.meshes.new(name + "_Dome")
    L._finish_bm(bm, me, smooth=True, sharp_angle=60.0)
    L._box_uv(me)
    p.append(L._link(name + "_Dome", me, coll, mat["hazard_y"], (0, 0, 0.070)))
    p.append(B.cyl(name + "_Brim", 0.175, 0.025, (0, 0.010, 0.062), mat["hazard_y"], coll,
                   segments=30, bevel=0.006, r2=0.160))
    ob = B.join(p, name, coll)
    B.place(ob, center, rot_z=rot_z)
    return ob
