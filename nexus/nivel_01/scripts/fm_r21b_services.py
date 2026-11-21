"""Architectural services / wall dressing for L1_SECURITY_R21B_HERO.

Skirting, cable trays, HVAC duct, sprinkler line, wall vents, hose cabinet,
clock, emergency fixtures, exit and room signage. Renders and the saved
scene remain dark: only low-energy red practicals are added.
"""
import math
import random
import bpy
from mathutils import Vector, Matrix

import fm_ops_lib as L
import fm_r21b_lib as B


def build(mat, coll, lights_coll):
    rnd = random.Random(3311)

    # ------------------------------------------------------------------ skirting
    sk = []
    def skirt(name, axis, fixed, a0, a1, face_sign):
        # axis 0 -> along Y at x=fixed; axis 1 -> along X at y=fixed
        ln = a1 - a0
        if axis == 0:
            sk.append(B.box(name, (0.026, ln, 0.105),
                            (fixed + face_sign * 0.013, (a0 + a1) * 0.5, 0.0525),
                            mat["rubber"], coll, bevel=0.003, seg=2))

        else:
            sk.append(B.box(name, (ln, 0.026, 0.105),
                            ((a0 + a1) * 0.5, fixed + face_sign * 0.013, 0.0525),
                            mat["rubber"], coll, bevel=0.003, seg=2))

    skirt("R21B_SERV_Skirt_W", 0, -104.85, 10.35, 35.75, 1)
    skirt("R21B_SERV_Skirt_S1", 1, 10.15, -104.80, -92.05, 1)
    skirt("R21B_SERV_Skirt_S2", 1, 10.15, -85.95, -71.25, 1)
    skirt("R21B_SERV_Skirt_E1", 0, -71.15, 11.70, 35.75, -1)
    skirt("R21B_SERV_Skirt_N1", 1, 35.85, -104.80, -96.05, -1)
    skirt("R21B_SERV_Skirt_N2", 1, 35.85, -91.95, -71.25, -1)
    skirting = B.join(sk, "R21B_SERV_Skirting", coll)

    # ------------------------------------------------------------------ west wall cable tray
    tp = []
    y0, y1 = 13.0, 31.5
    xw = -104.55
    tp.append(B.box("R21B_SERV_WestTray_Bottom", (0.30, y1 - y0, 0.012),
                    (xw, (y0 + y1) * 0.5, 3.520), mat["galv"], coll, bevel=0.002, seg=2))
    for sx in (-1, 1):
        tp.append(B.box(f"R21B_SERV_WestTray_Rail{sx}", (0.012, y1 - y0, 0.075),
                        (xw + sx * 0.144, (y0 + y1) * 0.5, 3.565),
                        mat["galv"], coll, bevel=0.002, seg=2))
    # brackets to wall
    for i in range(8):
        yy = y0 + 0.4 + i * (y1 - y0 - 0.8) / 7
        tp.append(B.box(f"R21B_SERV_WestTray_Bracket{i}", (0.34, 0.050, 0.030),
                        (-104.69, yy, 3.500), mat["steel_dark"], coll,
                        bevel=0.003, seg=2))
        tp.append(B.box(f"R21B_SERV_WestTray_Drop{i}", (0.030, 0.050, 0.26),
                        (-104.835, yy, 3.640), mat["steel_dark"], coll,
                        bevel=0.003, seg=2))
        tp.append(B.bolts(f"R21B_SERV_WestTray_Bolt{i}",
                          [(-104.835, yy, 3.760)], (1, 0, 0), 0.006, 0.008,
                          mat["steel_bare"], coll))
    # cables in the tray
    for i, (xx, rr, mm) in enumerate(((-104.63, 0.014, "cable_black"),
                                       (-104.55, 0.010, "cable_grey"),
                                       (-104.46, 0.017, "cable_black"))):
        tp.append(L.cable(f"R21B_SERV_WestTray_Cable{i}", (xx, y0 + 0.1, 3.555),
                          (xx, y1 - 0.1, 3.555), 0.02, rr, mat[mm], coll,
                          n=32, sides=6, wiggle=0.008, seed=i + 2))
    west_tray = B.join(tp, "R21B_SERV_WestCableTray", coll)

    # ------------------------------------------------------------------ HVAC duct
    dp = []
    xd = -97.20
    y0, y1 = 13.6, 33.4
    zc = 4.12
    nseg = 4
    for i in range(nseg):
        ya = y0 + (y1 - y0) * i / nseg
        yb = y0 + (y1 - y0) * (i + 1) / nseg
        dp.append(B.box(f"R21B_SERV_Duct_Seg{i}", (0.62, yb - ya - 0.02, 0.50),
                        (xd, (ya + yb) * 0.5, zc), mat["galv"], coll,
                        bevel=0.006, seg=3))
        dp.append(B.box(f"R21B_SERV_Duct_Flange{i}", (0.68, 0.055, 0.56),
                        (xd, ya, zc), mat["steel_dark"], coll, bevel=0.004, seg=3))
        for sx in (-1, 1):
            dp.append(B.bolts(f"R21B_SERV_Duct_FlangeBolts{i}{sx}",
                              [(xd + sx * 0.30, ya, zc + 0.22),
                               (xd + sx * 0.30, ya, zc - 0.22)],
                              (0, 1, 0), 0.007, 0.010, mat["steel_bare"], coll))
    dp.append(B.box("R21B_SERV_Duct_FlangeEnd", (0.68, 0.055, 0.56), (xd, y1, zc),
                    mat["steel_dark"], coll, bevel=0.004, seg=3))
    # hangers
    for i in range(6):
        yy = y0 + 0.7 + i * (y1 - y0 - 1.4) / 5
        for sx in (-1, 1):
            dp.append(B.cyl(f"R21B_SERV_Duct_Hanger{i}{sx}", 0.008, 0.34,
                            (xd + sx * 0.26, yy, 4.51), mat["steel_bare"], coll,
                            segments=8, bevel=0.001))
            dp.append(B.box(f"R21B_SERV_Duct_HangerFoot{i}{sx}", (0.04, 0.04, 0.020),
                            (xd + sx * 0.26, yy, 4.695), mat["steel_dark"], coll,
                            bevel=0.002, seg=2))
        dp.append(B.box(f"R21B_SERV_Duct_HangerBar{i}", (0.66, 0.04, 0.028),
                        (xd, yy, 4.365), mat["steel_dark"], coll, bevel=0.002, seg=2))
    # side grilles
    for i, yy in enumerate((18.0, 23.0, 28.0)):
        dp.append(B.box(f"R21B_SERV_Duct_GrilleFrame{i}", (0.020, 0.44, 0.28),
                        (xd + 0.315, yy, zc - 0.02), mat["steel_dark"], coll,
                        bevel=0.003, seg=3))
        dp.append(B.box(f"R21B_SERV_Duct_GrilleBack{i}", (0.010, 0.38, 0.22),
                        (xd + 0.322, yy, zc - 0.02), mat["dark"], coll,
                        bevel=0.001, seg=2))
        for k in range(6):
            dp.append(B.box(f"R21B_SERV_Duct_GrilleSlat{i}_{k}", (0.018, 0.38, 0.017),
                            (xd + 0.320, yy, zc - 0.13 + k * 0.042),
                            mat["galv"], coll, rot=(math.radians(25), 0, 0),
                            bevel=0.001, seg=1))
    duct = B.join(dp, "R21B_SERV_HVACDuct", coll)

    # ------------------------------------------------------------------ sprinkler line
    sp = []
    xs = -90.70
    sp.append(B.cyl("R21B_SERV_Sprinkler_Pipe", 0.036, 23.6, (xs, 23.0, 4.38),
                    mat["paint_red"], coll, rot=(math.radians(90), 0, 0), segments=16,
                    bevel=0.003))
    for i in range(9):
        yy = 11.8 + i * 2.8
        sp.append(B.box(f"R21B_SERV_Sprinkler_Hanger{i}", (0.040, 0.040, 0.33),
                        (xs, yy, 4.535), mat["steel_bare"], coll, bevel=0.002, seg=2))
        if i % 2 == 0:
            sp.append(B.cyl(f"R21B_SERV_Sprinkler_Head{i}", 0.018, 0.075,
                            (xs, yy, 4.315), mat["steel_bare"], coll, segments=12,
                            bevel=0.002))
    sprinkler = B.join(sp, "R21B_SERV_Sprinkler", coll)

    # ------------------------------------------------------------------ centre cable tray
    tp2 = []
    xt = -84.55
    y0, y1 = 12.6, 24.6
    tp2.append(B.box("R21B_SERV_CentreTray_Bottom", (0.30, y1 - y0, 0.012),
                     (xt, (y0 + y1) * 0.5, 4.285), mat["galv"], coll, bevel=0.002, seg=2))
    for sx in (-1, 1):
        tp2.append(B.box(f"R21B_SERV_CentreTray_Rail{sx}", (0.012, y1 - y0, 0.075),
                         (xt + sx * 0.144, (y0 + y1) * 0.5, 4.330),
                         mat["galv"], coll, bevel=0.002, seg=2))
    for i in range(4):
        yy = y0 + 0.5 + i * (y1 - y0 - 1.0) / 3
        for sx in (-1, 1):
            tp2.append(B.cyl(f"R21B_SERV_CentreTray_Hanger{i}{sx}", 0.007, 0.40,
                             (xt + sx * 0.13, yy, 4.50), mat["steel_bare"], coll,
                             segments=8, bevel=0.001))
            tp2.append(B.box(f"R21B_SERV_CentreTray_Foot{i}{sx}", (0.04, 0.04, 0.018),
                             (xt + sx * 0.13, yy, 4.695), mat["steel_dark"], coll,
                             bevel=0.002, seg=2))
        tp2.append(B.box(f"R21B_SERV_CentreTray_Bar{i}", (0.34, 0.04, 0.025),
                         (xt, yy, 4.278), mat["steel_dark"], coll, bevel=0.002, seg=2))
    for i, (xx, rr, mm) in enumerate(((-84.63, 0.012, "cable_black"),
                                       (-84.55, 0.009, "cable_grey"),
                                       (-84.47, 0.015, "cable_black"))):
        tp2.append(L.cable(f"R21B_SERV_CentreTray_Cable{i}", (xx, y0 + 0.1, 4.310),
                           (xx, y1 - 0.1, 4.310), 0.03, rr, mat[mm], coll,
                           n=28, sides=6, wiggle=0.01, seed=i + 11))
    centre_tray = B.join(tp2, "R21B_SERV_CentreCableTray", coll)

    # ------------------------------------------------------------------ wall vents
    def wall_vent(name, center, size, normal_axis, rot):
        # built local XZ plane, thickness Y; place and rotate
        vp = []
        w, h, d = size
        vp.append(B.box(name + "_Frame", (w, d, h), (0, 0, 0),
                        mat["steel_dark"], coll, bevel=0.003, seg=3))
        vp.append(B.box(name + "_Back", (w - 0.07, d * 0.3, h - 0.07), (0, d * 0.28, 0),
                        mat["dark"], coll, bevel=0.001, seg=2))
        for k in range(7):
            vp.append(B.box(f"{name}_Slat{k}", (w - 0.09, d * 0.65, h * 0.055),
                            (0, d * 0.05, -h * 0.40 + k * h * 0.80 / 6),
                            mat["galv"], coll, rot=(math.radians(28), 0, 0),
                            bevel=0.001, seg=1))
        for sx in (-1, 1):
            for sz in (-1, 1):
                vp.append(B.bolts(f"{name}_Bolt{sx}{sz}",
                                  [(sx * (w * 0.5 - 0.045), 0, sz * (h * 0.5 - 0.045))],
                                  (0, -1, 0), 0.006, 0.008, mat["steel_bare"], coll))
        ob = B.join(vp, name, coll)
        ob.location = center
        ob.rotation_euler = rot
        return ob
    wall_vent("R21B_SERV_VentW", (-104.82, 32.40, 3.72), (0.90, 0.54, 0.075), 0,
              (0, 0, math.radians(90)))
    wall_vent("R21B_SERV_VentS", (-83.10, 10.17, 3.68), (0.85, 0.50, 0.075), 0,
              (0, 0, math.radians(180)))
    wall_vent("R21B_SERV_VentE", (-71.12, 24.20, 3.68), (0.80, 0.48, 0.075), 0,
              (0, 0, math.radians(-90)))

    # ------------------------------------------------------------------ hose reel cabinet
    hp = []
    hp.append(B.box("R21B_SERV_Hose_Back", (0.30, 0.86, 0.86), (-104.70, 26.20, 1.48),
                    mat["paint_red"], coll, bevel=0.006, seg=3))
    hp.append(B.box("R21B_SERV_Hose_Door", (0.014, 0.78, 0.76), (-104.545, 26.20, 1.48),
                    mat["glass"], coll, bevel=0.001, seg=2))
    # hose coil inside
    for j, xx in enumerate((-104.68, -104.66, -104.64)):
        pts = []
        for k in range(25):
            a = math.radians(k * 360 / 24)
            pts.append((xx, 26.20 + math.cos(a) * 0.24, 1.48 + math.sin(a) * 0.24))
        hp.append(L.tube(f"R21B_SERV_Hose_Coil{j}", pts, 0.011, mat["rubber_red"],
                         coll, sides=6))
    hp.append(B.cyl("R21B_SERV_Hose_Valve", 0.055, 0.035, (-104.64, 25.95, 1.62),
                    mat["steel_bare"], coll, rot=(0, math.radians(90), 0), segments=16,
                    bevel=0.003))
    hp.append(B.annulus("R21B_SERV_Hose_Wheel", (-104.615, 25.95, 1.62), 0.075, 0.035, 0.012,
                        mat["paint_red"], coll, rot=(0, math.radians(90), 0)))
    hp.append(B.tube("R21B_SERV_Hose_Nozzle",
                     [(-104.66, 26.55, 1.35), (-104.63, 26.70, 1.25),
                      (-104.60, 26.78, 1.16)], 0.014, mat["steel_bare"], coll, sides=8))
    hose = B.join(hp, "R21B_SERV_HoseCabinet", coll)

    # ------------------------------------------------------------------ wall clock
    cp = []
    cp.append(B.cyl("R21B_SERV_Clock_Back", 0.250, 0.045, (-104.828, 23.90, 2.55),
                    mat["steel_dark"], coll, rot=(0, math.radians(90), 0), segments=32,
                    bevel=0.004))
    cp.append(B.cyl("R21B_SERV_Clock_Rim", 0.238, 0.055, (-104.793, 23.90, 2.55),
                    mat["aluminum"], coll, rot=(0, math.radians(90), 0), segments=32,
                    bevel=0.004))
    cp.append(B.cyl("R21B_SERV_Clock_Face", 0.212, 0.020, (-104.763, 23.90, 2.55),
                    mat["dark"], coll, rot=(0, math.radians(90), 0), segments=32,
                    bevel=0.001))
    for k in range(12):
        a = math.radians(k * 30)
        rr = 0.180
        cp.append(B.box(f"R21B_SERV_Clock_Tick{k}", (0.006, 0.012, 0.032),
                        (-104.750, 23.90 + math.sin(a) * rr, 2.55 + math.cos(a) * rr),
                        mat["white"], coll, rot=(a, 0, 0), bevel=0.0005, seg=1))
    clock = B.join(cp, "R21B_SERV_Clock", coll)

    # ------------------------------------------------------------------ emergency light fixtures + red practicals
    def emergency_fixture(name, center, rot):
        ep = []
        ep.append(B.box(name + "_Box", (0.30, 0.20, 0.22), (0, 0, 0.0),
                        mat["paint_red"], coll, bevel=0.008, seg=4))
        ep.append(B.box(name + "_Lens", (0.22, 0.020, 0.13), (0, -0.105, 0.0),
                        mat["red"], coll, bevel=0.004, seg=3))
        ep.append(B.box(name + "_LensFrame", (0.26, 0.030, 0.17), (0, -0.095, 0.0),
                        mat["steel_dark"], coll, bevel=0.003, seg=3))
        ep.append(B.box(name + "_Bracket", (0.10, 0.055, 0.08), (0, 0.125, 0.0),
                        mat["steel_dark"], coll, bevel=0.003, seg=2))
        ob = B.join(ep, name, coll)
        B.place(ob, center, rot_z=rot)
        return ob
    emergency_fixture("R21B_SERV_EmergencyW1", (-104.78, 14.60, 3.16), 90.0)
    emergency_fixture("R21B_SERV_EmergencyW2", (-104.78, 27.60, 3.16), 90.0)
    emergency_fixture("R21B_SERV_EmergencyS", (-94.60, 10.17, 3.16), 180.0)
    # red practicals (low energy, saved scene stays dark)
    for i, (x, y, z) in enumerate(((-104.55, 14.60, 3.10), (-104.55, 27.60, 3.10),
                                    (-94.60, 10.40, 3.10))):
        ld = bpy.data.lights.new(f"R21B_LIGHT_Emergency_{i}", "POINT")
        ld.energy = 1.6
        ld.color = (1.0, 0.035, 0.012)
        ld.shadow_soft_size = 0.10
        ob = bpy.data.objects.new(f"R21B_LIGHT_Emergency_{i}", ld)
        lights_coll.objects.link(ob)
        ob.location = (x, y, z)
    # spark practical
    ld = bpy.data.lights.new("R21B_LIGHT_Spark", "POINT")
    ld.energy = 1.2
    ld.color = (1.0, 0.38, 0.06)
    ld.shadow_soft_size = 0.05
    ob = bpy.data.objects.new("R21B_LIGHT_Spark", ld)
    lights_coll.objects.link(ob)
    ob.location = (-87.60, 16.00, 1.05)

    # ------------------------------------------------------------------ fire alarm pull station
    ap = []
    ap.append(B.box("R21B_SERV_Alarm_Back", (0.24, 0.10, 0.32), (0, 0, 0),
                    mat["paint_red"], coll, bevel=0.006, seg=3))
    ap.append(B.box("R21B_SERV_Alarm_Face", (0.19, 0.03, 0.26), (0, -0.055, 0),
                    mat["white"], coll, bevel=0.003, seg=2))
    ap.append(B.box("R21B_SERV_Alarm_Handle", (0.13, 0.05, 0.055), (0, -0.085, -0.015),
                    mat["paint_red"], coll, bevel=0.004, seg=3))
    ap.append(B.box("R21B_SERV_Alarm_Arrow", (0.07, 0.012, 0.09), (0, -0.075, 0.075),
                    mat["paint_red"], coll, bevel=0.002, seg=2))
    ap.append(B.box("R21B_SERV_Alarm_LED", (0.020, 0.010, 0.012), (0.06, -0.075, 0.105),
                    mat["led_green"], coll, bevel=0.001, seg=1))
    alarm = B.join(ap, "R21B_SERV_FireAlarm", coll)
    B.place(alarm, (-92.65, 10.16, 1.35), rot_z=180.0)

    # ------------------------------------------------------------------ exit sign (above south door)
    xp = []
    xp.append(B.box("R21B_SERV_Exit_Back", (0.56, 0.060, 0.24), (0, 0, 0),
                    mat["exit_green"], coll, bevel=0.003, seg=3))
    xp.append(B.box("R21B_SERV_Exit_Bar", (0.38, 0.006, 0.055), (0, -0.034, 0),
                    mat["white"], coll, bevel=0.001, seg=2))
    exit_sign = B.join(xp, "R21B_SERV_ExitSign", coll)
    B.place(exit_sign, (-89.0, 10.16, 3.34), rot_z=0.0)

    # ------------------------------------------------------------------ room identity sign (west wall)
    rp = []
    rp.append(B.box("R21B_SERV_RoomSign_Back", (0.035, 2.65, 0.62), (0, 0, 0),
                    mat["green_dark"], coll, bevel=0.004, seg=3))
    rp.append(B.box("R21B_SERV_RoomSign_Frame", (0.045, 2.73, 0.70), (-0.006, 0, 0),
                    mat["aluminum"], coll, bevel=0.003, seg=3))
    rp.append(B.text("R21B_SERV_RoomSign_Text", "SEGURIDAD 03", 0.30, (0.019, 0, 0.0),
                     (0, math.radians(90), math.radians(90)), mat["white"], coll))
    rp.append(B.box("R21B_SERV_RoomSign_Line", (0.004, 2.20, 0.020), (0.019, 0, -0.20),
                    mat["hazard_y"], coll, bevel=0.001, seg=1))
    room_sign = B.join(rp, "R21B_SERV_RoomSign", coll)
    B.place(room_sign, (-104.831, 13.55, 2.32), rot_z=0.0)

    return coll
