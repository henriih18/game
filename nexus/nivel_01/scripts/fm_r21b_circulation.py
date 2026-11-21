"""Circulation / filling for L1_SECURITY_R21B_HERO.

Glass screens around the ops centre, checkpoint queue, floor wayfinding,
planters, waiting benches, column protection and the locker-room PPE station.
"""
import math
import random
import bpy
from mathutils import Vector, Matrix

import fm_ops_lib as L
import fm_r21b_lib as B


# --------------------------------------------------------------------------------------
# glass partition
# --------------------------------------------------------------------------------------
def build(mat, coll):
    parts = []
    rnd = random.Random(4471)

    # ------------------------------------------------------------------ glass screen (south edge of ops centre)
    y = 25.95
    segments = [
        (-91.50, -88.32, 3),
        (-87.68, -86.30, 1),
        (-85.10, -82.00, 3),
    ]
    posts = []
    for x0, x1, n in segments:
        for i in range(n + 1):
            x = x0 + (x1 - x0) * i / n
            posts.append((x, x0, x1, i, n))
            parts.append(B.box(f"R21B_CIRC_GlassPost_{x:.2f}", (0.070, 0.140, 2.37),
                               (x, y, 1.205), mat["steel_dark"], coll,
                               bevel=0.005, seg=3))
        # glass panels
        for i in range(n):
            xa = x0 + (x1 - x0) * i / n
            xb = x0 + (x1 - x0) * (i + 1) / n
            cx = (xa + xb) * 0.5
            w = xb - xa - 0.085
            parts.append(B.box(f"R21B_CIRC_GlassPanel_{xa:.2f}", (w, 0.012, 2.24),
                               (cx, y, 1.19), mat["glass"], coll, bevel=0.001, seg=1))
            # small edge clamps
        # continuous shoe + top rail
        parts.append(B.box(f"R21B_CIRC_GlassShoe_{x0:.2f}", (x1 - x0, 0.110, 0.090),
                           ((x0 + x1) * 0.5, y, 0.055), mat["steel_dark"], coll,
                           bevel=0.004, seg=3))
        parts.append(B.box(f"R21B_CIRC_GlassRail_{x0:.2f}", (x1 - x0, 0.085, 0.052),
                           ((x0 + x1) * 0.5, y, 2.330), mat["steel_bare"], coll,
                           bevel=0.004, seg=3))
    screen = B.join(parts, "R21B_CIRC_GlassScreen", coll)

    # door (separate, hinged open)
    dp = []
    dw, dh, dt = 1.16, 2.30, 0.048
    dp.append(B.box("R21B_CIRC_GlassDoor_StileL", (0.070, dt, dh), (0.035, 0, dh * 0.5),
                    mat["green"], coll, bevel=0.004, seg=3))
    dp.append(B.box("R21B_CIRC_GlassDoor_StileR", (0.070, dt, dh), (dw - 0.035, 0, dh * 0.5),
                    mat["green"], coll, bevel=0.004, seg=3))
    dp.append(B.box("R21B_CIRC_GlassDoor_RailB", (dw - 0.14, dt, 0.16), (dw * 0.5, 0, 0.08),
                    mat["green"], coll, bevel=0.004, seg=3))
    dp.append(B.box("R21B_CIRC_GlassDoor_RailT", (dw - 0.14, dt, 0.12), (dw * 0.5, 0, dh - 0.06),
                    mat["green"], coll, bevel=0.004, seg=3))
    dp.append(B.box("R21B_CIRC_GlassDoor_Glass", (dw - 0.18, 0.012, dh - 0.28),
                    (dw * 0.5, 0, dh * 0.5), mat["glass"], coll, bevel=0.001, seg=1))
    dp.append(B.box("R21B_CIRC_GlassDoor_Band", (dw - 0.22, 0.004, 0.14),
                    (dw * 0.5, -0.007, 1.15), mat["frost"], coll, bevel=0.0005, seg=1))
    dp.append(B.box("R21B_CIRC_GlassDoor_Kick", (dw - 0.22, 0.006, 0.18),
                    (dw * 0.5, -0.027, 0.19), mat["steel_bare"], coll, bevel=0.001, seg=2))
    # hinges
    for hz in (0.40, 1.15, 1.90):
        dp.append(B.cyl(f"R21B_CIRC_GlassDoor_Hinge{hz}", 0.012, 0.095, (0.0, 0.0, hz),
                        mat["steel_bare"], coll, segments=12, bevel=0.001))
        dp.append(B.box(f"R21B_CIRC_GlassDoor_HingePlateA{hz}", (0.050, 0.012, 0.080),
                        (0.028, -0.032, hz), mat["steel_dark"], coll, bevel=0.002, seg=2))
        dp.append(B.box(f"R21B_CIRC_GlassDoor_HingePlateB{hz}", (0.014, 0.050, 0.080),
                        (0.0, 0.034, hz), mat["steel_dark"], coll, bevel=0.002, seg=2))
    # closer
    dp.append(B.box("R21B_CIRC_GlassDoor_Closer", (0.24, 0.055, 0.070), (dw * 0.5, -0.060, 2.13),
                    mat["aluminum"], coll, bevel=0.006, seg=3))
    dp.append(B.rod("R21B_CIRC_GlassDoor_CloserArm", (dw * 0.5 + 0.05, -0.060, 2.13),
                    (0.12, -0.060, 2.02), 0.012, mat["steel_bare"], coll, 8))
    # lock
    door = B.join(dp, "R21B_CIRC_GlassDoor", coll)
    B.bake_world(door)
    door.matrix_world = (Matrix.Translation(Vector((-86.26, y, 0.0015))) @
                         Matrix.Rotation(math.radians(-22.0), 4, "Z"))

    # restricted access sign above the door
    sp = []
    sp.append(B.box("R21B_CIRC_RestrictedSign_Back", (0.94, 0.020, 0.24), (0, 0, 0),
                    mat["white"], coll, bevel=0.002, seg=2))
    sp.append(B.box("R21B_CIRC_RestrictedSign_Frame", (1.00, 0.026, 0.28), (0, 0.006, 0),
                    mat["steel_dark"], coll, bevel=0.003, seg=3))
    txt = B.text("R21B_CIRC_RestrictedSign_Text", "ACCESO RESTRINGIDO", 0.080,
                 (0, -0.012, -0.002), (math.radians(90), 0, 0), mat["sign_green"], coll)
    sp.append(txt)
    for sx in (-0.32, 0.32):
        sp.append(B.box(f"R21B_CIRC_RestrictedSign_Bracket{sx}", (0.040, 0.040, 0.140),
                        (sx, 0.0, -0.170), mat["steel_dark"], coll, bevel=0.002, seg=2))
    sign = B.join(sp, "R21B_CIRC_RestrictedSign", coll)
    B.place(sign, (-85.70, 25.93, 2.56))

    # ------------------------------------------------------------------ queue stanchions
    qp = []
    posts_q = [-86.50, -85.20, -83.90, -82.60]
    for i, x in enumerate(posts_q):
        qp.append(B.cyl(f"R21B_CIRC_Queue_Base{i}", 0.190, 0.030, (x, 14.35, 0.017),
                        mat["steel_dark"], coll, segments=28, bevel=0.005))
        qp.append(B.cyl(f"R21B_CIRC_Queue_BaseCover{i}", 0.165, 0.055, (x, 14.35, 0.055),
                        mat["dark"], coll, segments=24, bevel=0.010, r2=0.100))
        qp.append(B.cyl(f"R21B_CIRC_Queue_Pole{i}", 0.024, 0.900, (x, 14.35, 0.505),
                        mat["steel_bare"], coll, segments=18, bevel=0.003))
        qp.append(B.cyl(f"R21B_CIRC_Queue_Collar{i}", 0.035, 0.035, (x, 14.35, 0.090),
                        mat["steel_dark"], coll, segments=18, bevel=0.003))
        qp.append(B.box(f"R21B_CIRC_Queue_Head{i}", (0.085, 0.075, 0.105), (x, 14.35, 0.960),
                        mat["steel_dark"], coll, bevel=0.012, seg=4))
        qp.append(B.box(f"R21B_CIRC_Queue_HeadCap{i}", (0.095, 0.085, 0.018), (x, 14.35, 1.018),
                        mat["steel_bare"], coll, bevel=0.004, seg=3))
        qp.append(B.cyl(f"R21B_CIRC_Queue_Slot{i}", 0.020, 0.030, (x + 0.045, 14.35, 0.960),
                        mat["dark"], coll, rot=(0, math.radians(90), 0), segments=12,
                        bevel=0.002))
        for k in range(3):
            qp.append(B.box(f"R21B_CIRC_Queue_Rib{i}_{k}", (0.050, 0.008, 0.010),
                            (x, 14.35 - 0.032 + k * 0.032, 0.975), mat["rubber"], coll,
                            bevel=0.0008, seg=1))
    # sagging tapes
    for i in range(len(posts_q) - 1):
        xa, xb = posts_q[i] + 0.030, posts_q[i + 1] - 0.030
        pts = []
        for k in range(9):
            t = k / 8
            xx = xa + (xb - xa) * t
            pts.append((xx, 14.35, 0.935 - math.sin(math.pi * t) * 0.065))
        qp.append(B.ribbon(f"R21B_CIRC_Queue_Belt{i}", pts, 0.042, 0.004,
                           mat["rubber_red"], coll, up=(0, 0, 1)))
    queue = B.join(qp, "R21B_CIRC_Queue", coll)

    # ------------------------------------------------------------------ floor wayfinding
    fp = []
    # lane lines (worn segments)
    lane_segments = [(-91.85, 10.35, 14.20), (-91.85, 15.00, 20.80),
                     (-91.85, 21.60, 25.30),
                     (-86.15, 10.35, 13.20), (-86.15, 14.80, 20.80),
                     (-86.15, 21.60, 25.30)]
    for i, (x, y0, y1) in enumerate(lane_segments):
        n = max(1, int((y1 - y0) / 1.30))
        for k in range(n):
            ya = y0 + (y1 - y0) * k / n
            yb = y0 + (y1 - y0) * (k + 1) / n - 0.15
            fp.append(B.box(f"R21B_CIRC_FloorLine{i}_{k}", (0.085, yb - ya, 0.004),
                            (x, (ya + yb) * 0.5, 0.003), mat["hazard_y"], coll,
                            bevel=0.001, seg=1))
    # central dashed guide
    for k in range(7):
        yy = 15.1 + k * 1.45
        fp.append(B.box(f"R21B_CIRC_FloorDash{k}", (0.06, 0.80, 0.004),
                        (-89.00, yy, 0.003), mat["white"], coll, bevel=0.001, seg=1))
    # hazard band at ops threshold
    for k in range(32):
        x = -91.45 + k * 0.298
        if x > -82.05:
            break
        fp.append(B.box(f"R21B_CIRC_FloorHazard{k}", (0.298, 0.120, 0.004),
                        (x + 0.149, 25.48, 0.003),
                        mat["hazard_y"] if k % 2 == 0 else mat["hazard_k"], coll,
                        bevel=0.001, seg=1))
    # arrows
    def arrow(name, x, y, ang, length=0.62, width=0.36):
        pts = [(-width * 0.20, -length * 0.5), (width * 0.20, -length * 0.5),
               (width * 0.20, length * 0.10), (width * 0.50, length * 0.10),
               (0.0, length * 0.5), (-width * 0.50, length * 0.10),
               (-width * 0.20, length * 0.10)]
        ob = B.extrude_poly(name, pts, 0.0015, 0.003, mat["hazard_y"], coll,
                            center=(x, y, 0.0), rot=(0, 0, math.radians(ang)))
        return ob
    for i, (x, y, ang) in enumerate(((-94.06, 15.45, 0), (-94.06, 21.90, 0),
                                      (-82.38, 16.15, 0), (-83.30, 22.60, 0),
                                      (-89.00, 18.10, 0))):
        fp.append(arrow(f"R21B_CIRC_FloorArrow{i}", x, y, ang))
    # painted zone stencil
    st = B.text("R21B_CIRC_FloorStencil", "SEC-03", 0.52, (-92.85, 16.85, 0.0015),
                (0, 0, 0), mat["hazard_y"], coll, extrude=0.0015)
    fp.append(st)
    floor = B.join(fp, "R21B_CIRC_FloorMarkings", coll)

    # ------------------------------------------------------------------ low concrete planters
    for i, (cx, cy, length, leaves) in enumerate(((-84.00, 17.05, 1.50, 21),
                                                   (-96.75, 24.62, 1.02, 15))):
        pp = []
        pp.append(B.box(f"R21B_CIRC_Planter{i}_Body", (length, 0.62, 0.50),
                        (0, 0, 0.26), mat["concrete"], coll, bevel=0.012, seg=4))
        pp.append(B.box(f"R21B_CIRC_Planter{i}_Foot", (length - 0.10, 0.52, 0.030),
                        (0, 0, 0.015), mat["concrete_dark"], coll, bevel=0.004, seg=2))
        pp.append(B.box(f"R21B_CIRC_Planter{i}_Soil", (length - 0.12, 0.50, 0.025),
                        (0, 0, 0.512), mat["soil"], coll, bevel=0.002, seg=2))
        for k in range(4):
            xx = -length * 0.5 + 0.16 + k * (length - 0.32) / 3
            pp.append(B.box(f"R21B_CIRC_Planter{i}_Rib{k}", (0.030, 0.635, 0.30),
                            (xx, 0, 0.28), mat["concrete_dark"], coll, bevel=0.002, seg=2))
        planter = B.join(pp, f"R21B_CIRC_Planter_{i:02d}", coll)
        B.place(planter, (cx, cy, 0.0015))
        # foliage
        foliage = []
        for k in range(leaves):
            a = math.radians(k * 360.0 / leaves + rnd.uniform(-8, 8))
            rx = length * 0.5 - 0.16
            ry = 0.17
            rr = rnd.uniform(0.0, 1.0)
            base = (cx + math.cos(a) * rr * rx, cy + math.sin(a) * rr * ry, 0.508)
            ln = rnd.uniform(0.52, 0.96)
            wd = rnd.uniform(0.032, 0.060)
            lf = B.leaf(f"R21B_CIRC_Planter{i}_Leaf{k:02d}", base, ln, wd,
                        rnd.uniform(-15, 15), rnd.uniform(-15, 15), rnd.uniform(-25, 25),
                        mat["plant_dark"] if k % 3 else mat["plant_light"], coll,
                        seed=700 + k + i * 50, curve=0.35)
            lf.rotation_mode = "XYZ"
            lf.rotation_euler.rotate_axis("Z", a)
            foliage.append(lf)
        fol = B.join(foliage, f"R21B_CIRC_Planter{i}_Foliage", coll)

    # ------------------------------------------------------------------ waiting benches
    bench1 = waiting_bench("R21B_CIRC_WaitBenchA", mat, coll, length=2.0)
    B.place(bench1, (-95.45, 15.35, 0.0015), rot_z=0.0)
    bench2 = waiting_bench("R21B_CIRC_WaitBenchB", mat, coll, length=1.80)
    B.place(bench2, (-82.10, 19.20, 0.0015), rot_z=90.0)

    # ------------------------------------------------------------------ column protection
    bands = []
    for i, (cx, cy) in enumerate(((-98.0, 16.0), (-98.0, 26.0), (-88.0, 16.0),
                                   (-88.0, 26.0), (-78.0, 16.0), (-78.0, 26.0))):
        for sx in (-1, 1):
            bands.append(B.box(f"R21B_CIRC_ColumnBandX{i}{sx}", (0.020, 0.50, 0.13),
                               (cx + sx * 0.237, cy, 0.22), mat["hazard_y"], coll,
                               bevel=0.001, seg=1))
            bands.append(B.box(f"R21B_CIRC_ColumnBandY{i}{sx}", (0.50, 0.020, 0.13),
                               (cx, cy + sx * 0.237, 0.22), mat["hazard_y"], coll,
                               bevel=0.001, seg=1))
    band = B.join(bands, "R21B_CIRC_ColumnBands", coll)

    # ------------------------------------------------------------------ PPE station (south wall)
    build_ppe(mat, coll)

    return coll


# --------------------------------------------------------------------------------------
# waiting bench with back
# --------------------------------------------------------------------------------------
def waiting_bench(name, mat, coll, length=2.0, width=0.56):
    p = []
    # seat slats
    for i in range(5):
        yy = -0.18 + i * 0.09
        p.append(B.box(f"{name}_SeatSlat{i}", (length - 0.12, 0.070, 0.038),
                       (0, yy, 0.445), mat["wood"], coll, bevel=0.005, seg=3))
    # back slats
    for i in range(4):
        z = 0.68 + i * 0.115
        y = -0.255 - i * 0.020
        p.append(B.box(f"{name}_BackSlat{i}", (length - 0.12, 0.040, 0.080),
                       (0, y, z), mat["wood"], coll, rot=(math.radians(8), 0, 0),
                       bevel=0.005, seg=3))
    # end frames
    for sx in (-1, 1):
        x = sx * (length * 0.5 - 0.10)
        p.append(B.box(f"{name}_EndPlate{sx}", (0.060, width - 0.04, 0.050),
                       (x, -0.02, 0.420), mat["steel_dark"], coll, bevel=0.004, seg=3))
        p.append(B.box(f"{name}_LegF{sx}", (0.050, 0.060, 0.40),
                       (x, 0.16, 0.22), mat["steel_dark"], coll, bevel=0.004, seg=3))
        p.append(B.box(f"{name}_LegB{sx}", (0.050, 0.060, 0.88),
                       (x, -0.225, 0.46), mat["steel_dark"], coll, bevel=0.004, seg=3))
        p.append(B.box(f"{name}_FootF{sx}", (0.065, 0.075, 0.020),
                       (x, 0.16, 0.010), mat["rubber"], coll, bevel=0.003, seg=2))
        p.append(B.box(f"{name}_FootB{sx}", (0.065, 0.085, 0.020),
                       (x, -0.225, 0.010), mat["rubber"], coll, bevel=0.003, seg=2))
        p.append(B.box(f"{name}_BackPost{sx}", (0.055, 0.055, 0.62),
                       (x, -0.235, 0.79), mat["steel_dark"], coll,
                       rot=(math.radians(8), 0, 0), bevel=0.004, seg=3))
    ob = B.join(p, name, coll)
    return ob


# --------------------------------------------------------------------------------------
# column guard
# --------------------------------------------------------------------------------------
def column_guard(name, mat, coll, cx, cy):
    p = []
    # base plate
    p.append(B.box(name + "_Base", (0.62, 0.62, 0.022), (cx, cy, 0.0125),
                   mat["galv"], coll, bevel=0.004, seg=3))
    p.append(B.bolts(name + "_BaseBolts",
                     [(cx - 0.24, cy - 0.24, 0.024), (cx + 0.24, cy - 0.24, 0.024),
                      (cx - 0.24, cy + 0.24, 0.024), (cx + 0.24, cy + 0.24, 0.024)],
                     (0, 0, 1), 0.008, 0.010, mat["steel_bare"], coll))
    # four corner angles
    for sx in (-1, 1):
        for sy in (-1, 1):
            x = cx + sx * 0.245
            y = cy + sy * 0.245
            p.append(B.box(f"{name}_AngleX{sx}{sy}", (0.100, 0.040, 1.12), (x, y, 0.59),
                           mat["steel_dark"], coll, bevel=0.003, seg=3))
            p.append(B.box(f"{name}_AngleY{sx}{sy}", (0.040, 0.100, 1.12), (x, y, 0.59),
                           mat["steel_dark"], coll, bevel=0.003, seg=3))
            p.append(B.bolts(f"{name}_AngleBolts{sx}{sy}",
                             [(x, y, 0.34)], (0, 0, 1),
                             0.006, 0.008, mat["steel_bare"], coll))
    # hazard band around the column
    for sx in (-1, 1):
        p.append(B.box(f"{name}_BandX{sx}", (0.020, 0.50, 0.13),
                       (cx + sx * 0.238, cy, 0.22), mat["hazard_y"], coll,
                       bevel=0.001, seg=1))
        p.append(B.box(f"{name}_BandY{sx}", (0.50, 0.020, 0.13),
                       (cx, cy + sx * 0.238, 0.22), mat["hazard_y"], coll,
                       bevel=0.001, seg=1))
    for k in range(2):
        p.append(B.box(f"{name}_BandStripe{k}", (0.020, 0.070, 0.13),
                       (cx - 0.238, cy - 0.10 + k * 0.20, 0.22), mat["hazard_k"], coll,
                       bevel=0.0008, seg=1))
    ob = B.join(p, name, coll)
    return ob


# --------------------------------------------------------------------------------------
# PPE issue station (south wall, east of locker bank B)
# --------------------------------------------------------------------------------------
def build_ppe(mat, coll):
    p = []
    # lower cabinet + worktop
    p.append(B.box("R21B_PPE_Cabinet", (2.30, 0.48, 0.78), (0, 0.26, 0.39),
                   mat["green"], coll, bevel=0.008, seg=4))
    p.append(B.box("R21B_PPE_Top", (2.38, 0.54, 0.045), (0, 0.27, 0.80),
                   mat["steel_bare"], coll, bevel=0.005, seg=3))
    p.append(B.box("R21B_PPE_Kick", (2.22, 0.04, 0.08), (0, 0.49, 0.042),
                   mat["rubber"], coll, bevel=0.002, seg=2))
    for i, x in enumerate((-0.60, 0.60)):
        p.append(B.box(f"R21B_PPE_Door{i}", (1.10, 0.020, 0.64), (x, 0.505, 0.42),
                       mat["green_dark"], coll, bevel=0.004, seg=3))
        p.append(B.box(f"R21B_PPE_DoorGrip{i}", (0.020, 0.020, 0.16),
                       (x + 0.38, 0.526, 0.46), mat["steel_bare"], coll,
                       bevel=0.003, seg=3))
        for gz in (-0.06, 0.06):
            p.append(B.box(f"R21B_PPE_GripPost{i}{gz}", (0.026, 0.014, 0.014),
                           (x + 0.38, 0.513, 0.46 + gz), mat["steel_bare"], coll,
                           bevel=0.002, seg=2))
    # pegboard + frame
    p.append(B.box("R21B_PPE_Pegboard", (2.28, 0.030, 1.26), (0, 0.035, 1.59),
                   mat["green_dark"], coll, bevel=0.004, seg=3))
    # mirror - one plate, 3 mm proud of the board
    p.append(B.box("R21B_PPE_Mirror", (0.56, 0.006, 0.92), (0.88, 0.045, 1.63),
                   mat["steel_bare"], coll, bevel=0.001, seg=2))
    # two hard hats standing on the worktop
    from fm_r21b_lockers import hard_hat
    for i, x in enumerate((-0.52, 0.16)):
        hat = hard_hat(f"R21B_PPE_Hat{i}", (x, 0.20, 0.776), mat, coll, rot_z=12.0 - 24.0 * i)
        p.append(hat)
    # two equipment pouches
    for i, x in enumerate((0.15, 0.45)):
        p.append(B.box(f"R21B_PPE_Pouch{i}", (0.17, 0.09, 0.24), (x, 0.085, 1.70),
                       mat["olive"], coll, bevel=0.008, seg=4))
        p.append(B.box(f"R21B_PPE_PouchFlap{i}", (0.15, 0.020, 0.10), (x, 0.045, 1.78),
                       mat["green_dark"], coll, bevel=0.003, seg=3))
    ob = B.join(p, "R21B_CIRC_PPEStation", coll)
    B.place(ob, (-74.72, 10.149, 0.0015), rot_z=0.0)
    return ob
