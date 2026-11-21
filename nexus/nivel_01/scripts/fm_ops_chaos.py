"""Non-narrative chaos: fallen hardware, cables, water, dust, debris and ceiling damage."""
import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

import fm_ops_lib as L


def _rock(name, center, size, mat, coll, seed):
    rnd = random.Random(seed)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)
    for v in bm.verts:
        d = 1.0 + rnd.uniform(-0.30, 0.22)
        v.co.x *= size[0] * d
        v.co.y *= size[1] * d
        v.co.z *= size[2] * d * 0.62
        v.co.x += rnd.uniform(-0.06, 0.06) * size[0]
        v.co.y += rnd.uniform(-0.06, 0.06) * size[1]
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    L._finish_bm(bm, me, smooth=False, sharp_angle=25.0)
    L._box_uv(me)
    zmin = min(v.co.z for v in me.vertices)
    ob = L._link(name, me, coll, mat, (center[0], center[1], center[2] - zmin - 0.012))
    return ob


def _shard(name, center, length, width, angle, mat, coll):
    bm = bmesh.new()
    v0 = bm.verts.new((-length * 0.5, 0, 0))
    v1 = bm.verts.new((length * 0.5, width * 0.2, 0))
    v2 = bm.verts.new((length * 0.1, -width * 0.5, 0))
    top = [v0, v1, v2]
    bot = [bm.verts.new((v.co.x, v.co.y, -0.004)) for v in top]
    bm.faces.new(top)
    bm.faces.new(list(reversed(bot)))
    for i in range(3):
        bm.faces.new((top[i], top[(i + 1) % 3], bot[(i + 1) % 3], bot[i]))
    me = bpy.data.meshes.new(name)
    L._finish_bm(bm, me, smooth=False, sharp_angle=25.0)
    L._box_uv(me)
    ob = L._link(name, me, coll, mat, (center[0], center[1], center[2]), (0, 0, angle))
    return ob


def build_chaos(mat, coll):
    objs = []

    # ------------------------------------------------------------------ fallen monitor
    # build the display lying face-up, then drop it onto the floor
    body = []
    body.append(L.box("R21A_CHAOS_FallenMonitor_Chassis", (0.600, 0.060, 0.400), (0, 0.030, 0),
                      mat["M_HERO_Plastic"], coll, bevel=0.008, seg=4))
    body.append(L.box("R21A_CHAOS_FallenMonitor_BezelT", (0.620, 0.032, 0.040), (0, -0.008, 0.200),
                      mat["M_HERO_Plastic"], coll, bevel=0.005, seg=3))
    body.append(L.box("R21A_CHAOS_FallenMonitor_BezelB", (0.620, 0.032, 0.040), (0, -0.008, -0.200),
                      mat["M_HERO_Plastic"], coll, bevel=0.005, seg=3))
    body.append(L.box("R21A_CHAOS_FallenMonitor_BezelL", (0.040, 0.032, 0.360), (-0.290, -0.008, 0),
                      mat["M_HERO_Plastic"], coll, bevel=0.005, seg=3))
    body.append(L.box("R21A_CHAOS_FallenMonitor_BezelR", (0.040, 0.032, 0.360), (0.290, -0.008, 0),
                      mat["M_HERO_Plastic"], coll, bevel=0.005, seg=3))
    body.append(L.box("R21A_CHAOS_FallenMonitor_Screen", (0.555, 0.006, 0.355), (0, -0.022, 0),
                      mat["M_HERO_Screen_Cracked"], coll, bevel=0.0, seg=1, smooth=False))
    body_ob = L.join(body, "R21A_CHAOS_FallenMonitor_Body", coll)
    L.transform_objects([body_ob], Matrix.Translation((-89.95, 27.35, 0.040)) @
                        Matrix.Rotation(math.radians(-90), 4, "X") @
                        Matrix.Rotation(math.radians(16), 4, "Z"))
    bpy.context.view_layer.update()
    lo = min((body_ob.matrix_world @ v.co).z for v in body_ob.data.vertices)
    body_ob.location.z += 0.0015 - lo
    bpy.context.view_layer.update()
    fm = [body_ob]
    # stand: base on the floor, bent neck and detached VESA plate
    fm.append(L.box("R21A_CHAOS_FallenMonitor_StandBase", (0.280, 0.200, 0.016), (-90.55, 27.60, 0.009),
                    mat["M_HERO_Steel_Dark"], coll, rot=(0, 0, math.radians(32)), bevel=0.005, seg=3))
    fm.append(L.box("R21A_CHAOS_FallenMonitor_Neck", (0.060, 0.050, 0.240), (-90.32, 27.50, 0.027),
                    mat["M_HERO_Steel_Dark"], coll, rot=(math.radians(90), 0, math.radians(36)),
                    bevel=0.005, seg=3))
    fm.append(L.box("R21A_CHAOS_FallenMonitor_Vesa", (0.120, 0.100, 0.012), (-90.14, 27.41, 0.007),
                    mat["M_HERO_Steel_Bare"], coll, rot=(0, 0, math.radians(20)), bevel=0.003, seg=2))

    objs.append(L.join(fm, "R21A_CHAOS_FallenMonitor", coll))

    # ------------------------------------------------------------------ fallen ceiling panel
    cp = []
    panel_center = (-77.55, 29.85, 0.0)
    cp.append(L.box("R21A_CHAOS_CeilingTile", (1.160, 0.560, 0.022), (panel_center[0], panel_center[1], 0.014),
                    mat["ceiling"], coll, rot=(math.radians(3), math.radians(-1.5), math.radians(6)),
                    bevel=0.003, seg=2))
    # suspension frame
    for i, (sx, sy) in enumerate(((1.240, 0.035), (0.035, 0.640))):
        for off in (-1, 1):
            if i == 0:
                c = (panel_center[0], panel_center[1] + off * 0.280, 0.006)
                size = (sx, sy, 0.030)
            else:
                c = (panel_center[0] + off * 0.575, panel_center[1], 0.006)
                size = (sy, sx, 0.030)
            cp.append(L.box(f"R21A_CHAOS_CeilingTee{i}{off}", size, c, mat["M_HERO_Galvanized"],
                            coll, rot=(0, 0, math.radians(6)), bevel=0.003, seg=2))
    cp.append(L.box("R21A_CHAOS_CeilingLamp", (0.520, 0.180, 0.070),
                    (panel_center[0] + 0.260, panel_center[1] - 0.080, 0.040),
                    mat["M_HERO_Steel_Dark"], coll, rot=(0, 0, math.radians(24)),
                    bevel=0.005, seg=3))
    cp.append(L.box("R21A_CHAOS_CeilingLampLens", (0.470, 0.135, 0.012),
                    (panel_center[0] + 0.260, panel_center[1] - 0.080, 0.078),
                    mat["M_HERO_Screen_Dead"], coll, rot=(0, 0, math.radians(24)),
                    bevel=0.002, seg=2))
    panel_ob = L.join(cp, "R21A_CHAOS_FallenCeiling_Body", coll)
    bpy.context.view_layer.update()
    lo = min((panel_ob.matrix_world @ v.co).z for v in panel_ob.data.vertices)
    panel_ob.location.z += 0.0015 - lo
    bpy.context.view_layer.update()
    cp = [panel_ob]
    # hanging wires back to the ceiling void
    for k, (dx, dy) in enumerate(((-0.40, -0.20), (0.28, 0.16), (0.42, -0.12))):
        p0 = (panel_center[0] + dx, panel_center[1] + dy, 0.020)
        p1 = (panel_center[0] + dx - 0.25, panel_center[1] + dy + 0.30, 4.780)
        cp.append(L.cable(f"R21A_CHAOS_CeilingWire{k}", p0, p1, 0.42, 0.005,
                          mat["M_HERO_Rubber"], coll, n=18, sides=6, wiggle=0.03, seed=120 + k))
    objs.append(L.join(cp, "R21A_CHAOS_FallenCeiling", coll))

    # ------------------------------------------------------------------ concrete debris
    rocks = []
    specs = [(-79.10, 27.20, (0.20, 0.16, 0.13), 1), (-78.55, 27.65, (0.12, 0.10, 0.08), 2),
             (-76.70, 28.55, (0.26, 0.19, 0.16), 3), (-75.95, 30.85, (0.14, 0.12, 0.10), 4),
             (-74.65, 31.55, (0.10, 0.09, 0.07), 5), (-88.35, 27.95, (0.15, 0.12, 0.09), 6),
             (-87.55, 28.80, (0.09, 0.08, 0.06), 7), (-84.10, 28.20, (0.17, 0.13, 0.10), 8),
             (-81.95, 32.05, (0.11, 0.10, 0.07), 9), (-73.90, 28.10, (0.22, 0.17, 0.14), 10),
             (-80.70, 34.55, (0.12, 0.10, 0.08), 11), (-76.20, 33.90, (0.08, 0.07, 0.05), 12)]
    for i, (x, y, s, seed) in enumerate(specs):
        rocks.append(_rock(f"R21A_CHAOS_Rock_{i:02d}", (x, y, 0.0), s, mat["M_HERO_Concrete"],
                           coll, seed + 200))
    objs.append(L.join(rocks, "R21A_CHAOS_DebrisConcrete", coll))

    # ------------------------------------------------------------------ metal scraps / glass
    scraps = []
    scrap_specs = [(-78.20, 27.90, 0.26, 0.16, 18), (-75.60, 29.95, 0.20, 0.12, -35),
                   (-85.10, 28.70, 0.18, 0.10, 62), (-74.20, 32.40, 0.30, 0.14, -8)]
    for i, (x, y, ln, wd, ang) in enumerate(scrap_specs):
        scraps.append(L.box(f"R21A_CHAOS_Scrap_{i}", (ln, wd, 0.006), (x, y, 0.004),
                            mat["M_HERO_Steel_Rust"], coll, rot=(0, math.radians(6), math.radians(ang)),
                            bevel=0.002, seg=2))
    objs.append(L.join(scraps, "R21A_CHAOS_MetalScrap", coll))

    shards = []
    for i in range(10):
        rnd = random.Random(300 + i)
        x = -89.55 + rnd.uniform(-0.55, 0.55)
        y = 26.95 + rnd.uniform(-0.30, 0.40)
        shards.append(_shard(f"R21A_CHAOS_Glass_{i}", (x, y, 0.004),
                             rnd.uniform(0.04, 0.13), rnd.uniform(0.02, 0.06),
                             rnd.uniform(0, 6.28), mat["M_HERO_Screen_Cracked"], coll))
    objs.append(L.join(shards, "R21A_CHAOS_GlassShards", coll))

    # ------------------------------------------------------------------ cable runs on the floor
    cables = []
    runs = [
        [(-77.95, 34.70, 0.012), (-77.60, 33.90, 0.012), (-77.25, 32.70, 0.012),
         (-77.10, 30.80, 0.012), (-77.60, 29.40, 0.012)],
        [(-78.05, 34.60, 0.012), (-78.70, 33.60, 0.012), (-79.90, 33.10, 0.012),
         (-81.40, 32.60, 0.012), (-82.40, 31.75, 0.012)],
        [(-78.20, 26.10, 0.012), (-79.60, 26.40, 0.012), (-81.30, 27.10, 0.012),
         (-83.00, 27.85, 0.012), (-85.05, 28.70, 0.012)],
        [(-86.90, 28.10, 0.012), (-86.20, 28.40, 0.012), (-85.20, 28.90, 0.012),
         (-84.65, 29.45, 0.012)],
    ]
    for i, pts in enumerate(runs):
        dens = []
        for k in range(len(pts) - 1):
            a, b = Vector(pts[k]), Vector(pts[k + 1])
            for t in (0.0, 0.33, 0.66):
                p = a.lerp(b, t)
                p.z = 0.008
                dens.append(p)
        last = Vector(pts[-1]); last.z = 0.008
        dens.append(last)
        cables.append(L.tube(f"R21A_CHAOS_FloorCable_{i}", dens, 0.008,
                             mat["M_HERO_Rubber"] if i % 2 == 0 else mat["cable_blue"], coll,
                             sides=7))
    objs.append(L.join(cables, "R21A_CHAOS_FloorCables", coll))

    # ------------------------------------------------------------------ cable reel
    reel = []
    rc = (-76.55, 33.60, 0.292)
    for sx in (-0.140, 0.140):
        reel.append(L.cyl(f"R21A_CHAOS_ReelDisc{sx}", 0.290, 0.035,
                          (rc[0] + sx, rc[1], rc[2]), mat["M_HERO_Plastic"], coll,
                          rot=(0, math.radians(90), 0), segments=32, bevel=0.004))
        reel.append(L.cyl(f"R21A_CHAOS_ReelHub{sx}", 0.110, 0.020,
                          (rc[0] + sx * 1.15, rc[1], rc[2]), mat["M_HERO_Steel_Dark"], coll,
                          rot=(0, math.radians(90), 0), segments=24, bevel=0.003))
    reel.append(L.cyl("R21A_CHAOS_ReelAxle", 0.045, 0.330, (rc[0], rc[1], rc[2]),
                      mat["M_HERO_Steel_Bare"], coll, rot=(0, math.radians(90), 0), segments=16,
                      bevel=0.002))
    # spooled cable
    for k in range(4):
        pts = []
        for i in range(41):
            a = TAU * i / 40
            pts.append((rc[0] + (k - 1.5) * 0.020, rc[1] + math.cos(a) * 0.205,
                        rc[2] + math.sin(a) * 0.205))
        reel.append(L.tube(f"R21A_CHAOS_ReelCable{k}", pts, 0.008, mat["M_HERO_Rubber"],
                           coll, sides=6))
    reel.append(L.tube("R21A_CHAOS_ReelTail",
                       [(rc[0] + 0.020, rc[1] - 0.200, 0.280), (rc[0] + 0.050, rc[1] - 0.320, 0.120),
                        (rc[0] + 0.120, rc[1] - 0.420, 0.012), (rc[0] + 0.330, rc[1] - 0.520, 0.012)],
                       0.008, mat["M_HERO_Rubber"], coll, sides=6))
    objs.append(L.join(reel, "R21A_CHAOS_CableReel", coll))

    # ------------------------------------------------------------------ water
    objs.append(L.irregular_disc("R21A_CHAOS_Puddle_Main", (-76.10, 31.10), 0.85, 0.65, 0.0015,
                                 mat["M_HERO_Water"], coll, n=22, seed=17))
    objs.append(L.irregular_disc("R21A_CHAOS_Puddle_Secondary", (-86.60, 27.05), 0.42, 0.30, 0.0015,
                                 mat["M_HERO_Water"], coll, n=18, seed=19))
    objs.append(L.irregular_disc("R21A_CHAOS_Puddle_Third", (-77.30, 34.60), 0.30, 0.22, 0.0015,
                                 mat["M_HERO_Water"], coll, n=16, seed=23))

    # ------------------------------------------------------------------ dust drifts
    for i, (x, y, rx, ry, seed) in enumerate(((-83.70, 28.55, 0.90, 0.55, 31),
                                               (-80.00, 33.30, 0.75, 0.45, 32),
                                               (-89.90, 28.20, 0.55, 0.35, 33))):
        objs.append(L.irregular_disc(f"R21A_CHAOS_Dust_{i}", (x, y), rx, ry, 0.0012,
                                     mat["dust"], coll, n=18, seed=seed))
    return objs


TAU = math.pi * 2.0
