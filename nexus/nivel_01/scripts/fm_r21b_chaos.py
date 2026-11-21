"""Non-narrative chaos and clutter for L1_SECURITY_R21B_HERO.

Dead equipment, cable reels, crates, bins, fallen ceiling fixtures, debris,
water, dust, cables and a large central ficus. No bodies, blood, notes,
photographs or personal items.
"""
import math
import random
import bpy
from mathutils import Vector, Matrix

import fm_ops_lib as L
import fm_r21b_lib as B


def build(mat, coll):
    rnd = random.Random(6653)

    # ------------------------------------------------------------------ tool cart
    cp = []
    cp.append(B.box("R21B_CHAOS_ToolCart_Body", (0.72, 0.46, 0.92), (0, 0, 0.49),
                    mat["green"], coll, bevel=0.008, seg=4))
    cp.append(B.box("R21B_CHAOS_ToolCart_Top", (0.76, 0.50, 0.045), (0, 0, 0.965),
                    mat["steel_dark"], coll, bevel=0.005, seg=3))
    cp.append(B.box("R21B_CHAOS_ToolCart_Mat", (0.68, 0.42, 0.010), (0, 0, 0.991),
                    mat["rubber"], coll, bevel=0.002, seg=2))
    for i in range(5):
        z = 0.13 + i * 0.165
        cp.append(B.box(f"R21B_CHAOS_ToolCart_Drawer{i}", (0.66, 0.018, 0.140),
                        (0, 0.240, z), mat["green_dark"], coll, bevel=0.002, seg=2))
        cp.append(B.box(f"R21B_CHAOS_ToolCart_Pull{i}", (0.28, 0.014, 0.018),
                        (0, 0.257, z), mat["steel_bare"], coll, bevel=0.002, seg=2))
    cp.append(B.box("R21B_CHAOS_ToolCart_Plinth", (0.68, 0.42, 0.032),
                    (0, 0, 0.016), mat["dark"], coll, bevel=0.004, seg=3))
    cart = B.join(cp, "R21B_CHAOS_ToolCart", coll)
    B.place(cart, (-80.65, 21.75, 0.0015), rot_z=8.0)

    # ------------------------------------------------------------------ cable reels
    reel1 = cable_reel("R21B_CHAOS_CableReelA", mat, coll)
    B.place(reel1, (-81.95, 22.85, 0.0015), rot_z=18.0)
    reel2 = cable_reel("R21B_CHAOS_CableReelB", mat, coll, tipped=True)
    B.place(reel2, (-79.65, 23.35, 0.0015), rot_z=-35.0)

    # ------------------------------------------------------------------ crates + pallet
    pp = []
    pp.append(B.box("R21B_CHAOS_Pallet_Top", (1.18, 0.82, 0.030), (0, 0, 0.120),
                    mat["wood_dark"], coll, bevel=0.003, seg=2))
    for i in range(7):
        pp.append(B.box(f"R21B_CHAOS_Pallet_Slat{i}", (0.11, 0.80, 0.022),
                        (-0.50 + i * 0.166, 0, 0.145), mat["wood"], coll,
                        bevel=0.002, seg=2))
    for sy in (-1, 1):
        pp.append(B.box(f"R21B_CHAOS_Pallet_Runner{sy}", (1.18, 0.12, 0.10),
                        (0, sy * 0.32, 0.06), mat["wood_dark"], coll, bevel=0.003, seg=2))
    for sx in (-1, 0, 1):
        pp.append(B.box(f"R21B_CHAOS_Pallet_Block{sx}", (0.14, 0.12, 0.10),
                        (sx * 0.48, 0, 0.06), mat["wood_dark"], coll, bevel=0.003, seg=2))
    pallet = B.join(pp, "R21B_CHAOS_Pallet", coll)
    B.place(pallet, (-78.85, 18.45, 0.0015), rot_z=-6.0)

    # two stacked flight cases on the pallet
    from fm_r21b_lockers import flight_case
    c1 = flight_case("R21B_CHAOS_CaseA", (-78.95, 18.45, 0.356), (0.70, 0.52, 0.38),
                     mat, coll, rot_z=4.0)
    c2 = flight_case("R21B_CHAOS_CaseB", (-78.78, 18.40, 0.706), (0.62, 0.46, 0.32),
                     mat, coll, rot_z=-5.0)
    # wooden crate beside
    crate_parts = []
    crate_parts.append(B.box("R21B_CHAOS_Crate_Body", (0.62, 0.50, 0.44), (-80.20, 17.20, 0.221),
                             mat["wood"], coll, bevel=0.004, seg=3))
    crate = B.join(crate_parts, "R21B_CHAOS_Crate", coll)

        # ------------------------------------------------------------------ bins
    for i, (x, y, style) in enumerate(((-77.20, 18.05, "metal"),
                                       (-76.95, 22.55, "plastic"))):
        bp = []
        if style == "metal":
            bp.append(B.box(f"R21B_CHAOS_Bin{i}_Body", (0.34, 0.34, 0.50), (0, 0, 0.250),
                            mat["steel_dark"], coll, bevel=0.008, seg=4))
            bp.append(B.box(f"R21B_CHAOS_Bin{i}_Lid", (0.37, 0.37, 0.035), (0, 0, 0.505),
                            mat["galv"], coll, bevel=0.006, seg=3))
        else:
            bp.append(B.box(f"R21B_CHAOS_Bin{i}_Body", (0.34, 0.34, 0.52), (0, 0, 0.260),
                            mat["green"], coll, bevel=0.010, seg=4))
            bp.append(B.box(f"R21B_CHAOS_Bin{i}_Lid", (0.37, 0.37, 0.040), (0, 0, 0.520),
                            mat["green_dark"], coll, bevel=0.008, seg=4))
        bp.append(B.box(f"R21B_CHAOS_Bin{i}_Handle", (0.12, 0.030, 0.025),
                        (0, 0.185, 0.525), mat["dark"], coll, bevel=0.004, seg=3))
        ob = B.join(bp, f"R21B_CHAOS_Bin_{i:02d}", coll)
        B.place(ob, (x, y, 0.0015))

        # ------------------------------------------------------------------ dead monitors
    mon1 = crt_monitor("R21B_CHAOS_DeadMonitorA", mat, coll, tipped=False)
    B.place(mon1, (-79.62, 18.62, 0.871), rot_z=-28.0)
    mon2 = crt_monitor("R21B_CHAOS_DeadMonitorB", mat, coll, tipped=True)
    B.place(mon2, (-100.55, 14.55, 0.0015), rot_z=112.0)

    # ------------------------------------------------------------------ ceiling light on floor + hanging
    fallen = ceiling_light("R21B_CHAOS_FallenLight", mat, coll, fallen=True)
    B.place(fallen, (-100.20, 14.10, 0.0015), rot_z=26.0, rot=(0, 0, 0))
    hanging = ceiling_light("R21B_CHAOS_HangingLight", mat, coll, hanging=True)
    B.place(hanging, (-86.20, 20.40, 4.10), rot_z=-14.0, rot=(7.0, 0, 0))

    # ------------------------------------------------------------------ debris, water, dust
    dp = []
    spots = [(-88.62, 17.42, 0.30, 0.24, 0.20), (-88.30, 17.62, 0.20, 0.16, 0.13),
             (-88.92, 17.70, 0.16, 0.14, 0.10), (-79.38, 21.38, 0.26, 0.20, 0.17),
             (-79.06, 21.15, 0.18, 0.15, 0.11), (-95.22, 24.12, 0.27, 0.21, 0.18),
             (-94.92, 23.92, 0.14, 0.12, 0.09), (-75.30, 13.10, 0.18, 0.15, 0.12),
             (-74.92, 13.32, 0.13, 0.11, 0.08), (-83.10, 22.20, 0.22, 0.17, 0.14),
             (-82.80, 22.45, 0.12, 0.10, 0.08), (-91.20, 24.70, 0.20, 0.16, 0.12)]
    for i, (x, y, sx, sy, sz) in enumerate(spots):
        rock = B.rock(f"R21B_CHAOS_Debris{i}", (x, y, sz * 0.55), (sx, sy, sz),
                      mat["concrete"], coll, seed=90 + i, subdiv=1)
        dp.append(rock)
    # bent sheet metal
    dp.append(B.box("R21B_CHAOS_BentSheet", (0.82, 0.42, 0.012), (-87.90, 17.10, 0.012),
                    mat["rust"], coll, rot=(math.radians(-4), math.radians(2), math.radians(18)),
                    bevel=0.003, seg=2))
    debris = B.join(dp, "R21B_CHAOS_Debris", coll)

    # puddles
    for i, (x, y, rx, ry, seed) in enumerate(((-83.25, 18.10, 0.85, 0.62, 3),
                                               (-72.55, 12.35, 0.55, 0.38, 4),
                                               (-94.55, 15.55, 0.45, 0.32, 5))):
        L.irregular_disc(f"R21B_CHAOS_Puddle{i}", (x, y, 0.0015), rx, ry, 0.0015,
                         mat["water"], coll, n=20, seed=seed)
    # dust patches
    for i, (x, y, rx, ry, seed) in enumerate(((-89.20, 18.10, 1.1, 0.65, 11),
                                               (-77.80, 20.10, 0.9, 0.55, 12),
                                               (-93.10, 22.90, 1.2, 0.7, 13),
                                               (-75.10, 13.90, 0.8, 0.5, 14),
                                               (-85.60, 16.00, 0.7, 0.45, 15))):
        L.irregular_disc(f"R21B_CHAOS_Dust{i}", (x, y, 0.0012), rx, ry, 0.0012,
                         mat["dust"], coll, n=18, seed=seed)

    # ------------------------------------------------------------------ cables
    cables = []
    cables.append(L.cable("R21B_CHAOS_CableA", (-80.20, 22.10, 0.008),
                          (-71.40, 22.55, 0.008), 0.004, 0.012, mat["cable_black"],
                          coll, n=20, sides=6, wiggle=0.10, seed=2))
    cables.append(L.cable("R21B_CHAOS_CableB", (-80.35, 21.55, 0.008),
                          (-77.30, 19.15, 0.008), 0.003, 0.010, mat["cable_orange"],
                          coll, n=16, sides=6, wiggle=0.08, seed=3))
    cables.append(L.cable("R21B_CHAOS_CableC", (-86.20, 20.40, 4.12),
                          (-85.95, 19.15, 0.010), 0.15, 0.006, mat["cable_black"],
                          coll, n=18, sides=6, wiggle=0.08, seed=4))
    cables.append(L.coil("R21B_CHAOS_CableCoil", (-77.10, 21.20, 0.008), (0, 0, 1),
                         0.22, 0.025, 2.8, 0.008, mat["cable_black"], coll, n=22, sides=6))
    cable_ob = B.join(cables, "R21B_CHAOS_Cables", coll)

    # ------------------------------------------------------------------ sparking junction box on column
    sp = []
    sp.append(B.box("R21B_CHAOS_SparkBox_Back", (0.20, 0.14, 0.28), (-87.765, 16.00, 1.25),
                    mat["steel_dark"], coll, bevel=0.004, seg=3))
    for k in range(3):
        sp.append(B.cyl(f"R21B_CHAOS_SparkBox_Gland{k}", 0.018, 0.030,
                        (-87.79, 15.94 + k * 0.05, 1.08), mat["rubber"], coll,
                        segments=12, bevel=0.003))
    sp.append(B.tube("R21B_CHAOS_SparkBox_WireA",
                     [(-87.75, 15.98, 1.12), (-87.70, 15.88, 1.02), (-87.80, 15.80, 0.96),
                      (-87.86, 15.82, 0.92)], 0.004, mat["copper"], coll, sides=6))
    sp.append(B.tube("R21B_CHAOS_SparkBox_WireB",
                     [(-87.75, 16.02, 1.12), (-87.68, 16.10, 1.02), (-87.72, 16.20, 0.95)],
                     0.004, mat["copper"], coll, sides=6))
    # spark prongs
    spark = B.join(sp, "R21B_CHAOS_SparkBox", coll)

    # ------------------------------------------------------------------ central ficus
    build_ficus(mat, coll, (-90.70, 20.60, 0.0015))

    # ------------------------------------------------------------------ central backless bench
    bench = simple_bench("R21B_CHAOS_CenterBench", mat, coll)
    B.place(bench, (-88.55, 22.35, 0.0015), rot_z=0.0)

    return coll


# --------------------------------------------------------------------------------------
# cable reel
# --------------------------------------------------------------------------------------
def cable_reel(name, mat, coll, tipped=False):
    p = []
    axis = "Y"
    # wooden flanges, axis Y
    for sy in (-1, 1):
        p.append(B.cyl(f"{name}_Flange{sy}", 0.455, 0.055, (0, sy * 0.265, 0.55),
                       mat["wood"], coll, rot=(math.radians(90), 0, 0), segments=30,
                       bevel=0.008))
        p.append(B.cyl(f"{name}_FlangeRim{sy}", 0.465, 0.020, (0, sy * 0.289, 0.55),
                       mat["wood_dark"], coll, rot=(math.radians(90), 0, 0), segments=30,
                       bevel=0.004, r2=0.435))
        for k in range(6):
            a = math.radians(k * 60)
            p.append(B.cyl(f"{name}_FlangeBolt{sy}_{k}", 0.012, 0.012,
                           (math.cos(a) * 0.32, sy * 0.295, 0.55 + math.sin(a) * 0.32),
                           mat["steel_bare"], coll, rot=(math.radians(90), 0, 0),
                           segments=8, bevel=0.001))
    p.append(B.cyl(name + "_Drum", 0.235, 0.49, (0, 0, 0.55), mat["wood_dark"], coll,
                   rot=(math.radians(90), 0, 0), segments=28, bevel=0.006))
    p.append(B.cyl(name + "_Axle", 0.035, 0.72, (0, 0, 0.55), mat["steel_dark"], coll,
                   rot=(math.radians(90), 0, 0), segments=16, bevel=0.003))
    # wound cable rings
    for j, yy in enumerate((-0.18, -0.09, 0.0, 0.09, 0.18)):
        pts = []
        for k in range(25):
            a = math.radians(k * 360 / 24)
            pts.append((math.cos(a) * 0.250, yy, 0.55 + math.sin(a) * 0.250))
        p.append(L.tube(f"{name}_Cable{j}", pts, 0.014, mat["cable_black"], coll, sides=6))
    # A-frame stand
    for sy in (-1, 1):
        y = sy * 0.34
        p.append(B.box(f"{name}_StandLegA{sy}", (0.075, 0.10, 0.62),
                       (-0.16, y, 0.31), mat["steel_dark"], coll,
                       rot=(0, math.radians(-8), 0), bevel=0.004, seg=3))
        p.append(B.box(f"{name}_StandLegB{sy}", (0.075, 0.10, 0.62),
                       (0.16, y, 0.31), mat["steel_dark"], coll,
                       rot=(0, math.radians(8), 0), bevel=0.004, seg=3))
        p.append(B.box(f"{name}_StandFoot{sy}", (0.56, 0.14, 0.045), (0, y, 0.025),
                       mat["steel_dark"], coll, bevel=0.004, seg=3))
        p.append(B.box(f"{name}_StandTop{sy}", (0.12, 0.14, 0.09), (0, y, 0.58),
                       mat["steel_dark"], coll, bevel=0.004, seg=3))
    ob = B.join(p, name, coll)
    if tipped:
        # lay the reel on its flange, keep it touching the floor
        B.place(ob, (0, 0, 0), rot=(90.0, 0, 0), drop=True)
    return ob


# --------------------------------------------------------------------------------------
# CRT monitor
# --------------------------------------------------------------------------------------
def crt_monitor(name, mat, coll, tipped=False):
    p = []
    p.append(B.box(name + "_Base", (0.28, 0.24, 0.030), (0, -0.04, 0.015),
                   mat["plastic"], coll, bevel=0.006, seg=3))
    p.append(B.box(name + "_Body", (0.42, 0.40, 0.34), (0, 0.02, 0.20),
                   mat["plastic"], coll, bevel=0.020, seg=4))
    p.append(B.box(name + "_Bezel", (0.44, 0.040, 0.36), (0, -0.20, 0.21),
                   mat["dark"], coll, bevel=0.012, seg=4))
    p.append(B.box(name + "_Screen", (0.355, 0.008, 0.275), (0, -0.222, 0.21),
                   mat["screen_cracked"], coll, bevel=0.003, seg=3))
    p.append(B.box(name + "_Rear", (0.24, 0.12, 0.22), (0, 0.27, 0.21),
                   mat["plastic"], coll, bevel=0.020, seg=4))
    p.append(B.box(name + "_Label", (0.09, 0.004, 0.025), (0, -0.225, 0.34),
                   mat["paper"], coll, bevel=0.001, seg=1))
    p.append(B.cyl(name + "_Knob", 0.014, 0.020, (-0.18, -0.225, 0.08),
                   mat["dark"], coll, rot=(math.radians(90), 0, 0), segments=12,
                   bevel=0.002))
    p.append(B.tube(name + "_Cable",
                    [(-0.12, 0.28, 0.12), (-0.18, 0.36, 0.08), (-0.26, 0.40, 0.01),
                     (-0.36, 0.38, 0.008)], 0.006, mat["cable_black"], coll, sides=6))
    ob = B.join(p, name, coll)
    if tipped:
        ob.rotation_mode = "XYZ"
        ob.rotation_euler = (0, math.radians(104), 0)
        bpy.context.view_layer.update()
        lo = min((ob.matrix_world @ v.co).z for v in ob.data.vertices)
        ob.location = (ob.location.x, ob.location.y, 0.0015 - lo)
        bpy.context.view_layer.update()
    return ob


# --------------------------------------------------------------------------------------
# ceiling light fixture
# --------------------------------------------------------------------------------------
def ceiling_light(name, mat, coll, hanging=False, fallen=False):
    ob = B.box(name + "_Housing", (1.50, 0.44, 0.080), (0, 0, 0.04),
               mat["galv"], coll, bevel=0.004, seg=3)
    # one box, two materials: the diffuser face is simply the top/bottom face
    ob.data.materials.append(mat["canvas"])
    for poly in ob.data.polygons:
        if fallen and poly.normal.z > 0.6:
            poly.material_index = 1
        elif (not fallen) and poly.normal.z < -0.6:
            poly.material_index = 1
    if hanging:
        wires = []
        for sx in (-1, 1):
            wires.append(B.tube(f"{name}_Wire{sx}",
                                [(sx * 0.50, 0, 0.10), (sx * 0.55, 0.04, 0.40),
                                 (sx * 0.58, 0.06, 0.62)], 0.004, mat["cable_black"],
                                coll, sides=6))
        wires.append(ob)
        ob = B.join(wires, name, coll)
    return ob


def leaf_low(name, base, length, width, tx, ty, twist, mat, coll, seed=1):
    import bmesh
    rnd = random.Random(seed)
    bm = bmesh.new()
    rings = []
    segs = 4
    for i in range(segs + 1):
        t = i / segs
        w = max(0.0018, width * math.sin(math.pi * min(1.0, t * 1.02)) ** 0.75)
        x = 0.28 * length * t * t
        z = length * t
        a = math.radians(twist * t)
        ring = []
        for sx in (-1, 1):
            ring.append(bm.verts.new((x + sx * w * math.cos(a),
                                      sx * w * math.sin(a), z)))
            ring.append(bm.verts.new((x + sx * w * 0.35 * math.cos(a),
                                      sx * w * 0.35 * math.sin(a) + 0.004, z)))
        rings.append(ring)
    for i in range(segs):
        for k in range(4):
            a = rings[i][k]
            b = rings[i][(k + 1) % 4]
            c = rings[i + 1][(k + 1) % 4]
            d = rings[i + 1][k]
            bm.faces.new((a, b, c, d))
    bm.faces.new(tuple(reversed(rings[0])))
    bm.faces.new(tuple(rings[-1]))
    ob = B.finish(bm, name, coll, mat, smooth=True, sharp=55.0)
    ob.rotation_mode = "XYZ"
    ob.matrix_world = (Matrix.Translation(Vector(base)) @
                       Matrix.Rotation(math.radians(tx), 4, "X") @
                       Matrix.Rotation(math.radians(ty), 4, "Y"))
    return ob


def build_ficus(mat, coll, origin):
    """Large potted snake plant for the centre of the room."""
    ox, oy, oz = origin
    rnd = random.Random(907)
    p = []
    p.append(B.cyl("R21B_CHAOS_Ficus_Pot", 0.33, 0.56, (0, 0, 0.280), mat["ceramic"], coll,
                   segments=28, bevel=0.008, r2=0.37))
    p.append(B.annulus("R21B_CHAOS_Ficus_Rim", (0, 0, 0.560), 0.380, 0.342, 0.035,
                       mat["ceramic"], coll))
    p.append(B.cyl("R21B_CHAOS_Ficus_Soil", 0.345, 0.020, (0, 0, 0.565), mat["soil"], coll,
                   segments=26, bevel=0.003))
    pot = B.join(p, "R21B_CHAOS_Ficus_PotGroup", coll)
    B.place(pot, (ox, oy, oz))
    leaves = []
    for k in range(24):
        a = math.radians(k * 360.0 / 24 + rnd.uniform(-7, 7))
        rr = rnd.uniform(0.02, 0.26)
        base = (ox + math.cos(a) * rr, oy + math.sin(a) * rr, 0.548)
        ln = rnd.uniform(0.62, 1.05)
        wd = rnd.uniform(0.035, 0.065)
        lf = B.leaf(f"R21B_CHAOS_Ficus_Leaf{k:02d}", base, ln, wd,
                    rnd.uniform(-14, 14), rnd.uniform(-14, 14), rnd.uniform(-25, 25),
                    mat["plant_dark"] if k % 3 else mat["plant_light"], coll,
                    seed=700 + k, curve=0.30)
        lf.rotation_mode = "XYZ"
        lf.rotation_euler.rotate_axis("Z", a)
        leaves.append(lf)
    fol = B.join(leaves, "R21B_CHAOS_Ficus_Foliage", coll)
    return pot


def simple_bench(name, mat, coll, length=2.0):
    p = []
    for i in range(4):
        yy = -0.15 + i * 0.10
        p.append(B.box(f"{name}_Slat{i}", (length - 0.10, 0.080, 0.040),
                       (0, yy, 0.445), mat["wood"], coll, bevel=0.005, seg=3))
    for sx in (-1, 1):
        x = sx * (length * 0.5 - 0.12)
        p.append(B.box(f"{name}_Frame{sx}", (0.060, 0.42, 0.055), (x, 0, 0.420),
                       mat["steel_dark"], coll, bevel=0.004, seg=3))
        for sy in (-1, 1):
            p.append(B.box(f"{name}_Leg{sx}{sy}", (0.050, 0.050, 0.40),
                           (x, sy * 0.15, 0.22), mat["steel_dark"], coll,
                           bevel=0.004, seg=3))
            p.append(B.box(f"{name}_Foot{sx}{sy}", (0.060, 0.060, 0.020),
                           (x, sy * 0.15, 0.010), mat["rubber"], coll, bevel=0.003, seg=2))
    ob = B.join(p, name, coll)
    return ob
