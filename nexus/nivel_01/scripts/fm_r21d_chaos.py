"""FRECUENCIA MUERTA - L1_SECURITY_R21D_HERO.

R2.1d pass: visible damage, abandonment and final dark lighting for
Security 03.

The pass intentionally avoids new hero micro-detail.  It reuses the R2/R21A/
R21B/R21C assets, duplicates a few of them as displaced wreckage and adds
low/mid-poly industrial debris with real bevels:

- three dragged/tipped office chairs,
- two detached locker doors (one leaning, one on the floor),
- a collapsed ceiling field with fallen tiles, grid and hanging cables,
- one broken CRT with cracked screen and glass shards,
- a damaged electrical cabinet on the central column with sparks,
- broken framed glass, puddles, dust, concrete/metal debris,
- pallets, crates, cable reels and cones for an abandoned-working-room read.

Aisles stay clear.  All geometry goes into L1_SECURITY_R21D_HERO.
"""
import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

import fm_ops_lib as L
import fm_r21b_lib as B

ROOT = "L1_SECURITY_R21D_HERO"
TAU = math.pi * 2.0


# --------------------------------------------------------------------------------------
# collections
# --------------------------------------------------------------------------------------
def clean_root():
    root = bpy.data.collections.get(ROOT)
    if not root:
        return

    def walk(c):
        for ch in list(c.children):
            walk(ch)
        for ob in list(c.objects):
            me = ob.data if ob.type == "MESH" else None
            bpy.data.objects.remove(ob, do_unlink=True)
            if me and me.users == 0:
                bpy.data.meshes.remove(me)
        if c.users == 0:
            bpy.data.collections.remove(c)

    walk(root)
    if root.users == 0:
        bpy.data.collections.remove(root)


def root_collection():
    scene = bpy.context.scene
    c = bpy.data.collections.get(ROOT)
    if c is None:
        c = bpy.data.collections.new(ROOT)
    if c.name not in scene.collection.children:
        scene.collection.children.link(c)
    return c


def sub(name):
    r = root_collection()
    full = f"{ROOT}_{name}"
    c = bpy.data.collections.get(full)
    if c is None:
        c = bpy.data.collections.new(full)
    if c.name not in r.children:
        r.children.link(c)
    return c


# --------------------------------------------------------------------------------------
# materials
# --------------------------------------------------------------------------------------
def materials():
    mat = {
        "steel_dark": bpy.data.materials["M_HERO_Steel_Dark"],
        "steel_bare": bpy.data.materials["M_HERO_Steel_Bare"],
        "steel_rust": bpy.data.materials["M_HERO_Steel_Rust"],
        "galv": bpy.data.materials["M_HERO_Galvanized"],
        "aluminum": bpy.data.materials["M_HERO_Aluminum"],
        "plastic": bpy.data.materials["M_HERO_Plastic"],
        "rubber": bpy.data.materials["M_HERO_Rubber"],
        "paint_dark": bpy.data.materials["M_R21B_Paint_Dark"],
        "paint_green": bpy.data.materials["M_R21B_Paint_Green"],
        "paint_green_dark": bpy.data.materials["M_R21B_Paint_GreenDark"],
        "paint_olive": bpy.data.materials["M_R21B_Paint_Olive"],
        "paint_red": bpy.data.materials["M_R21B_Paint_Red"],
        "label": bpy.data.materials["M_R21B_Label"],
        "wood": bpy.data.materials["M_R21B_Wood"],
        "wood_dark": bpy.data.materials["M_R21B_Wood_Dark"],
        "cable_black": bpy.data.materials["M_R21B_Cable_Black"],
        "cable_grey": bpy.data.materials["M_R21B_Cable_Grey"],
        "cable_orange": bpy.data.materials["M_R21B_Cable_Orange"],
        "concrete": bpy.data.materials["M_R21B_Concrete"],
        "concrete_dark": bpy.data.materials["M_R21B_Concrete_Dark"],
        "ceiling": bpy.data.materials["M_HERO_Ops_CeilingTile"],
        "dust": bpy.data.materials["M_R21B_Dust"],
        "dust2": bpy.data.materials["M_HERO_Ops_Dust"],
        "water": bpy.data.materials["M_R21B_Water"],
        "glass": bpy.data.materials["M_R21B_Glass"],
        "glass_frost": bpy.data.materials["M_R21B_Glass_Frost"],
        "glass_crack": bpy.data.materials["M_R21C_GlassCrack"],
        "crt_bezel": bpy.data.materials["M_R21C_CRT_Bezel"],
        "crt_screen": bpy.data.materials["M_R21C_Screen_Cracked"],
        "screen_dead": bpy.data.materials["M_HERO_Ops_ScreenDead"],
        "emissive_red": bpy.data.materials["M_R21B_Emissive_Red"],
        "led_red": bpy.data.materials["M_HERO_LED_Red"],
        "cardboard": bpy.data.materials["M_FM_Cardboard"],
    }
    mat["soot"] = B.pbr("M_R21D_Soot", (0.009, 0.008, 0.007), 0.0, 0.96,
                        noise=90.0, bump=0.35, rough_var=0.03, alpha=1.0)
    mat["spark"] = B.pbr("M_R21D_Spark", (0.06, 0.01, 0.002), 0.0, 0.25,
                         noise=0.0, emission=(1.0, 0.18, 0.03), emission_strength=18.0)
    mat["cone_orange"] = B.pbr("M_R21D_ConeOrange", (0.46, 0.085, 0.012), 0.0, 0.62,
                               noise=55.0, bump=0.12, rough_var=0.08)
    mat["cone_white"] = B.pbr("M_R21D_ConeWhite", (0.62, 0.60, 0.54), 0.0, 0.48,
                              noise=45.0, bump=0.05, rough_var=0.04)
    return mat


# --------------------------------------------------------------------------------------
# low-level geometry
# --------------------------------------------------------------------------------------
def poly_prism_xz(name, pts_xz, y0, thick, mat, coll):
    """Closed thin prism in XZ plane, extruded along Y (soot/scorch decals)."""
    bm = bmesh.new()
    a, b = [], []
    for x, z in pts_xz:
        a.append(bm.verts.new((x, y0, z)))
        b.append(bm.verts.new((x, y0 + thick, z)))
    n = len(pts_xz)
    cx = sum(p[0] for p in pts_xz) / n
    cz = sum(p[1] for p in pts_xz) / n
    ca = bm.verts.new((cx, y0, cz))
    cb = bm.verts.new((cx, y0 + thick, cz))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((ca, a[j], a[i]))
        bm.faces.new((cb, b[i], b[j]))
        bm.faces.new((a[i], a[j], b[j], b[i]))
    me = bpy.data.meshes.new(name)
    L._finish_bm(bm, me, smooth=False, sharp_angle=26.0)
    L._box_uv(me)
    return L._link(name, me, coll, mat, (0, 0, 0))


def poly_plate_xy(name, pts_xy, z0, thick, mat, coll):
    """Closed irregular plate in XY plane, used for puddles and dust."""
    bm = bmesh.new()
    a, b = [], []
    for x, y in pts_xy:
        a.append(bm.verts.new((x, y, z0)))
        b.append(bm.verts.new((x, y, z0 + thick)))
    n = len(pts_xy)
    cx = sum(p[0] for p in pts_xy) / n
    cy = sum(p[1] for p in pts_xy) / n
    ca = bm.verts.new((cx, cy, z0))
    cb = bm.verts.new((cx, cy, z0 + thick))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((ca, a[i], a[j]))
        bm.faces.new((cb, b[j], b[i]))
        bm.faces.new((a[i], a[j], b[j], b[i]))
    me = bpy.data.meshes.new(name)
    L._finish_bm(bm, me, smooth=False, sharp_angle=24.0)
    L._box_uv(me)
    return L._link(name, me, coll, mat, (0, 0, 0))


def jagged_ring(name, cx, cy, rx, ry, z, mat, coll, n=20, seed=1):
    rnd = random.Random(seed)
    pts = []
    for i in range(n):
        a = TAU * i / n
        r = 1.0 + rnd.uniform(-0.16, 0.16)
        pts.append((cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r))
    return poly_plate_xy(name, pts, z, 0.0015, mat, coll)


def cone(name, base, height, r_base, r_top, mat, coll, rot=(0, 0, 0), segments=16):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segments,
                          radius1=r_base, radius2=r_top, depth=height)
    bm.verts.ensure_lookup_table()
    for v in bm.verts:
        v.co.z += height * 0.5
    me = bpy.data.meshes.new(name)
    L._finish_bm(bm, me, smooth=True, sharp_angle=40.0)
    L._box_uv(me)
    return L._link(name, me, coll, mat, base, rot)


def duplicate_asset(src_name, name, coll, loc, rot_z=0.0, rot_xyz=(0.0, 0.0, 0.0),
                    drop=True):
    """Duplicate an existing prop, recentre its mesh and place it in world space."""
    src = bpy.data.objects.get(src_name)
    if src is None:
        raise RuntimeError(f"missing source asset {src_name}")
    ob = src.copy()
    ob.data = src.data.copy()
    ob.name = name
    ob.data.name = name + "_MESH"
    coll.objects.link(ob)
    # bake current transform, then move the geometry centre to the object origin
    ob.data.transform(ob.matrix_world)
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    if not bm.verts:
        bm.free()
        return ob
    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    zs = [v.co.z for v in bm.verts]
    c = Vector(((min(xs) + max(xs)) * 0.5, (min(ys) + max(ys)) * 0.5,
                (min(zs) + max(zs)) * 0.5))
    bm.free()
    ob.data.transform(Matrix.Translation(-c))
    ob.matrix_world = Matrix.Identity(4)
    m = (Matrix.Translation(Vector(loc)) @
         Matrix.Rotation(math.radians(rot_z), 4, "Z") @
         Matrix.Rotation(math.radians(rot_xyz[0]), 4, "X") @
         Matrix.Rotation(math.radians(rot_xyz[1]), 4, "Y") @
         Matrix.Rotation(math.radians(rot_xyz[2]), 4, "Z"))
    ob.matrix_world = m
    if drop:
        bpy.context.view_layer.update()
        lo = min((ob.matrix_world @ v.co).z for v in ob.data.vertices)
        ob.matrix_world = Matrix.Translation((0, 0, 0.001 - lo)) @ ob.matrix_world
    bpy.context.view_layer.update()
    return ob


def transform_about_centre(ob, rz=0.0, dx=0.0, dy=0.0):
    if ob is None:
        return
    bpy.context.view_layer.update()
    bb = [ob.matrix_world @ Vector(v) for v in ob.bound_box]
    c = Vector(((min(p.x for p in bb) + max(p.x for p in bb)) * 0.5,
                (min(p.y for p in bb) + max(p.y for p in bb)) * 0.5,
                0.0))
    m = Matrix.Translation((dx, dy, 0.0)) @ Matrix.Translation(c) @ \
        Matrix.Rotation(math.radians(rz), 4, "Z") @ Matrix.Translation(-c)
    ob.matrix_world = m @ ob.matrix_world
    bpy.context.view_layer.update()


def finish(ob, name):
    if ob is not None:
        ob.name = name
        L.fix_inverted_islands(ob)
        L.weighted_normal(ob)
        for m in list(ob.modifiers):
            with bpy.context.temp_override(object=ob, active_object=ob,
                                           selected_objects=[ob],
                                           selected_editable_objects=[ob]):
                try:
                    bpy.ops.object.modifier_apply(modifier=m.name)
                except Exception as e:
                    print("MODIFIER FAIL", name, e)
    return ob


# --------------------------------------------------------------------------------------
# props
# --------------------------------------------------------------------------------------
def build_locker_door(name, loc, rot, coll, mat, bent=False):
    parts = []
    # outer slab, real frame and recessed panel
    parts.append(L.box(name + "_Slab", (0.44, 0.028, 0.92), (0.22, 0, 0.46),
                       mat["paint_green"], coll, bevel=0.003, seg=3))
    parts.append(L.box(name + "_Panel", (0.34, 0.012, 0.72), (0.22, -0.019, 0.50),
                       mat["paint_green_dark"], coll, bevel=0.002, seg=2))
    for i in range(8):
        parts.append(L.box(f"{name}_Vent{i}", (0.24, 0.008, 0.014),
                           (0.22, -0.028, 0.31 + i * 0.034),
                           mat["steel_dark"], coll, bevel=0.0012, seg=2))
    parts.append(L.box(name + "_Handle", (0.026, 0.024, 0.22), (0.40, -0.027, 0.55),
                       mat["aluminum"], coll, bevel=0.003, seg=2))
    parts.append(L.box(name + "_Lock", (0.045, 0.012, 0.06), (0.40, -0.021, 0.38),
                       mat["steel_dark"], coll, bevel=0.0015, seg=2))
    parts.append(L.box(name + "_Plate", (0.10, 0.004, 0.035), (0.22, -0.017, 0.83),
                       mat["label"], coll, bevel=0.0008, seg=2))
    for i, z in enumerate((0.20, 0.46, 0.72)):
        parts.append(L.box(f"{name}_Hinge{i}", (0.050, 0.036, 0.10),
                           (0.020, 0.0, z), mat["galv"], coll,
                           bevel=0.002, seg=2))
    ob = L.join(parts, name, coll)
    finish(ob, name)
    # lean it against the lockers / lay it on the floor
    ob.matrix_world = (Matrix.Translation(Vector(loc)) @
                       Matrix.Rotation(math.radians(rot[2]), 4, "Z") @
                       Matrix.Rotation(math.radians(rot[0]), 4, "X") @
                       Matrix.Rotation(math.radians(rot[1]), 4, "Y"))
    bpy.context.view_layer.update()
    lo = min((ob.matrix_world @ v.co).z for v in ob.data.vertices)
    ob.matrix_world = Matrix.Translation((0, 0, 0.001 - lo)) @ ob.matrix_world
    bpy.context.view_layer.update()
    return ob


def build_ceiling_tile(name, loc, rot, coll, mat, hanging=False):
    """One beveled mineral-fibre tile; no internal frame islands (avoids coplanar faces)."""
    ob = L.box(name + "_Face", (0.58, 0.58, 0.028), (0, 0, 0.014),
               mat["ceiling"], coll, bevel=0.004, seg=3)
    finish(ob, name)
    ob.matrix_world = (Matrix.Translation(Vector(loc)) @
                       Matrix.Rotation(math.radians(rot[2]), 4, "Z") @
                       Matrix.Rotation(math.radians(rot[0]), 4, "X") @
                       Matrix.Rotation(math.radians(rot[1]), 4, "Y"))
    if not hanging:
        bpy.context.view_layer.update()
        lo = min((ob.matrix_world @ v.co).z for v in ob.data.vertices)
        ob.matrix_world = Matrix.Translation((0, 0, 0.001 - lo)) @ ob.matrix_world
    bpy.context.view_layer.update()
    return ob


def build_crt(name, loc, rot_z, coll, mat):
    parts = []
    # shell / back housing / screen-up
    parts.append(L.box(name + "_Shell", (0.56, 0.44, 0.34), (0, 0, 0.20),
                       mat["plastic"], coll, bevel=0.022, seg=3))
    parts.append(L.box(name + "_Back", (0.38, 0.30, 0.10), (0, 0.02, 0.06),
                       mat["crt_bezel"], coll, bevel=0.010, seg=2))
    parts.append(L.box(name + "_Bezel", (0.50, 0.38, 0.035), (0, 0, 0.377),
                       mat["crt_bezel"], coll, bevel=0.004, seg=2))
    parts.append(L.box(name + "_Screen", (0.43, 0.31, 0.010), (0, 0, 0.392),
                       mat["crt_screen"], coll, bevel=0.001, seg=1))
    # cracked-glass overlay: one impact centre and radial fractures
    for i, pts2 in enumerate((
            [(0.02, 0.03), (-0.10, 0.09), (-0.17, 0.14)],
            [(0.02, 0.03), (0.11, 0.10), (0.18, 0.13)],
            [(0.02, 0.03), (-0.04, -0.09), (-0.08, -0.15)],
            [(0.02, 0.03), (0.09, -0.06), (0.14, -0.12)],
            [(0.02, 0.03), (-0.14, -0.03), (-0.19, -0.06)],
            [(0.02, 0.03), (0.14, 0.02), (0.20, 0.04)])):
        pts3 = [(x, y, 0.399) for x, y in pts2]
        parts.append(L.tube(f"{name}_Crack{i}", pts3, 0.0022,
                            mat["glass_crack"], coll, sides=5, cap=True))
    parts.append(L.cyl(name + "_Impact", 0.016, 0.004, (0.02, 0.03, 0.398),
                       mat["glass_crack"], coll, segments=10, bevel=0.0005, seg=1))
    # vents on the sides
    for i in range(6):
        parts.append(L.box(f"{name}_VentL{i}", (0.008, 0.30, 0.009),
                           (-0.275, 0, 0.17 + i * 0.032),
                           mat["crt_bezel"], coll, bevel=0.0006, seg=1))
        parts.append(L.box(f"{name}_VentR{i}", (0.008, 0.30, 0.009),
                           (0.275, 0, 0.17 + i * 0.032),
                           mat["crt_bezel"], coll, bevel=0.0006, seg=1))
    for i, (x, y) in enumerate(((-0.20, -0.16), (0.20, -0.16), (0.0, 0.17))):
        parts.append(L.cyl(f"{name}_Foot{i}", 0.022, 0.025, (x, y, 0.012),
                           mat["rubber"], coll, segments=8, bevel=0.001, seg=1))
    parts.append(L.cable(name + "_Cable", (0.10, 0.16, 0.12),
                         (0.52, 0.34, 0.02), 0.03, 0.009,
                         mat["cable_black"], coll, n=12, sides=6))
    ob = L.join(parts, name, coll)
    finish(ob, name)
    ob.matrix_world = Matrix.Translation(Vector(loc)) @ \
        Matrix.Rotation(math.radians(rot_z), 4, "Z")
    bpy.context.view_layer.update()
    lo = min((ob.matrix_world @ v.co).z for v in ob.data.vertices)
    ob.matrix_world = Matrix.Translation((0, 0, 0.001 - lo)) @ ob.matrix_world
    return ob


def build_glass_pane(name, loc, rot, coll, mat):
    parts = []
    # frame
    parts.append(L.box(name + "_FrameL", (0.035, 0.05, 1.90), (-0.50, 0, 0.95),
                       mat["aluminum"], coll, bevel=0.003, seg=2))
    parts.append(L.box(name + "_FrameR", (0.035, 0.05, 1.90), (0.50, 0, 0.95),
                       mat["aluminum"], coll, bevel=0.003, seg=2))
    parts.append(L.box(name + "_FrameT", (1.03, 0.05, 0.035), (0, 0, 1.88),
                       mat["aluminum"], coll, bevel=0.003, seg=2))
    parts.append(L.box(name + "_FrameB", (1.03, 0.05, 0.035), (0, 0, 0.03),
                       mat["aluminum"], coll, bevel=0.003, seg=2))
    # jagged broken pane: upper-right quadrant missing
    pts = [(-0.47, 0.06), (-0.47, 1.84), (-0.12, 1.84), (0.02, 1.56),
           (0.19, 1.70), (0.30, 1.38), (0.47, 1.46), (0.47, 0.62),
           (0.35, 0.40), (0.10, 0.48), (-0.03, 0.26), (-0.30, 0.38)]
    parts.append(poly_prism_xz(name + "_Pane", pts, -0.003, 0.006,
                               mat["glass"], coll))
    # crack strips on the pane
    cracks = [
        [(-0.10, 1.50), (0.02, 1.18), (0.20, 1.02), (0.39, 0.83)],
        [(0.02, 1.18), (-0.21, 0.94), (-0.34, 0.73)],
        [(0.20, 1.02), (0.12, 0.72), (0.27, 0.54)],
        [(-0.40, 0.50), (-0.18, 0.74), (0.02, 0.84)],
    ]
    for i, pts2 in enumerate(cracks):
        pts3 = [(x, -0.004, z) for x, z in pts2]
        parts.append(L.tube(f"{name}_Crack{i}", pts3, 0.0025,
                            mat["glass_crack"], coll, sides=5, cap=True))
    ob = L.join(parts, name, coll)
    finish(ob, name)
    ob.matrix_world = (Matrix.Translation(Vector(loc)) @
                       Matrix.Rotation(math.radians(rot[2]), 4, "Z") @
                       Matrix.Rotation(math.radians(rot[0]), 4, "X") @
                       Matrix.Rotation(math.radians(rot[1]), 4, "Y"))
    bpy.context.view_layer.update()
    lo = min((ob.matrix_world @ v.co).z for v in ob.data.vertices)
    ob.matrix_world = Matrix.Translation((0, 0, 0.001 - lo)) @ ob.matrix_world
    return ob


def build_pallet(name, loc, rot_z, coll, mat, boxes=0):
    parts = []
    # stringers and deck boards
    for y in (-0.44, 0.0, 0.44):
        parts.append(L.box(f"{name}_Stringer{len(parts)}", (1.05, 0.085, 0.075),
                           (0, y, 0.05), mat["wood_dark"], coll,
                           bevel=0.003, seg=2))
    for i in range(6):
        x = -0.47 + i * 0.19
        parts.append(L.box(f"{name}_Deck{i}", (0.15, 1.0, 0.022),
                           (x, 0, 0.096), mat["wood"], coll,
                           bevel=0.002, seg=2))
    for y in (-0.38, 0.38):
        parts.append(L.box(f"{name}_Bottom{len(parts)}", (0.95, 0.10, 0.022),
                           (0, y, 0.012), mat["wood_dark"], coll,
                           bevel=0.002, seg=2))
    # simple wooden crates on top
    for i in range(boxes):
        bx = -0.25 + (i % 2) * 0.52
        bz = 0.100 + (i // 2) * 0.37
        crate = L.box(f"{name}_Crate{i}", (0.42, 0.42, 0.34),
                      (bx, 0.0, bz + 0.17), mat["wood"], coll,
                      bevel=0.006, seg=3)
        parts.append(crate)
        parts.append(L.box(f"{name}_CrateBand{i}", (0.44, 0.44, 0.025),
                           (bx, 0.0, bz + 0.30), mat["wood_dark"], coll,
                           bevel=0.002, seg=2))
    ob = L.join(parts, name, coll)
    finish(ob, name)
    ob.matrix_world = Matrix.Translation(Vector(loc)) @ \
        Matrix.Rotation(math.radians(rot_z), 4, "Z")
    bpy.context.view_layer.update()
    lo = min((ob.matrix_world @ v.co).z for v in ob.data.vertices)
    ob.matrix_world = Matrix.Translation((0, 0, 0.001 - lo)) @ ob.matrix_world
    return ob


def build_cardboard_box(name, loc, rot_z, size, coll, mat):
    parts = [L.box(name + "_Body", (size[0], size[1], size[2]),
                   (0, 0, size[2] * 0.5), mat["cardboard"], coll,
                   bevel=0.006, seg=2)]
    parts.append(L.box(name + "_Tape", (size[0] * 1.01, 0.055, 0.004),
                       (0, 0, size[2] + 0.002), mat["label"], coll,
                       bevel=0.0007, seg=1))
    ob = L.join(parts, name, coll)
    finish(ob, name)
    ob.matrix_world = Matrix.Translation(Vector(loc)) @ \
        Matrix.Rotation(math.radians(rot_z), 4, "Z")
    bpy.context.view_layer.update()
    lo = min((ob.matrix_world @ v.co).z for v in ob.data.vertices)
    ob.matrix_world = Matrix.Translation((0, 0, 0.001 - lo)) @ ob.matrix_world
    return ob


def build_cone(name, loc, rot_z, tipped, coll, mat):
    parts = [cone(name + "_Body", (0, 0, 0.020), 0.50, 0.155, 0.035,
                  mat["cone_orange"], coll, segments=18)]
    parts.append(L.box(name + "_Base", (0.34, 0.34, 0.035), (0, 0, 0.0175),
                       mat["cone_orange"], coll, bevel=0.006, seg=3))
    for i, z in enumerate((0.20, 0.30)):
        parts.append(cone(f"{name}_Band{i}", (0, 0, z), 0.038, 0.112 - i * 0.016,
                          0.098 - i * 0.016, mat["cone_white"], coll, segments=18))
    ob = L.join(parts, name, coll)
    finish(ob, name)
    ob.matrix_world = (Matrix.Translation(Vector(loc)) @
                       Matrix.Rotation(math.radians(rot_z), 4, "Z") @
                       Matrix.Rotation(math.radians(88.0 if tipped else 0.0), 4, "Y"))
    bpy.context.view_layer.update()
    lo = min((ob.matrix_world @ v.co).z for v in ob.data.vertices)
    ob.matrix_world = Matrix.Translation((0, 0, 0.001 - lo)) @ ob.matrix_world
    return ob


def build_electrical_box(name, coll, mat):
    parts = []
    # cabinet on the south face of the central column (column y face 15.77)
    cx, cy, cz = -88.0, 15.70, 1.65
    parts.append(L.box(name + "_Back", (0.64, 0.18, 0.86), (cx, cy, cz),
                       mat["paint_olive"], coll, bevel=0.008, seg=3))
    parts.append(L.box(name + "_Inner", (0.54, 0.025, 0.72), (cx, cy - 0.105, cz),
                       mat["soot"], coll, bevel=0.002, seg=2))
    door = L.box(name + "_Door", (0.58, 0.025, 0.78),
                 (0.29, 0.0, 0.0), mat["paint_olive"], coll,
                 bevel=0.006, seg=3)
    door.data.transform(Matrix.Translation((-0.29, 0.0, 0.0)))
    door.location = (cx - 0.29, cy - 0.075, cz)
    door.rotation_euler = (0.0, 0.0, math.radians(-64.0))
    parts.append(door)
    # a vertical hinge plate bridges the cabinet face and the open door
    parts.append(L.box(name + "_HingePlate", (0.045, 0.13, 0.80),
                       (cx - 0.29, cy - 0.055, cz), mat["galv"], coll,
                       bevel=0.003, seg=2))
    # hinge stubs and handle
    for i, z in enumerate((cz - 0.27, cz + 0.27)):
        parts.append(L.cyl(f"{name}_Hinge{i}", 0.014, 0.10,
                           (cx - 0.30, cy - 0.075, z), mat["galv"], coll,
                           rot=(0, math.pi / 2, 0), segments=8,
                           bevel=0.001, seg=1))
    parts.append(L.box(name + "_Handle", (0.035, 0.028, 0.16),
                       (cx - 0.089, cy - 0.533, cz), mat["aluminum"], coll,
                       bevel=0.003, seg=2))
    # breakers
    for i in range(6):
        bx = cx - 0.22 + (i % 3) * 0.20
        bz = cz + 0.18 - (i // 3) * 0.16
        parts.append(L.box(f"{name}_Breaker{i}", (0.08, 0.035, 0.13),
                           (bx, cy - 0.125, bz), mat["plastic"], coll,
                           bevel=0.002, seg=2))
        parts.append(L.box(f"{name}_Lever{i}", (0.045, 0.022, 0.055),
                           (bx, cy - 0.148, bz), mat["aluminum"], coll,
                           bevel=0.0015, seg=2))
    # bus bars and terminal strip (terminal reaches back into the inner panel)
    parts.append(L.box(name + "_Bus", (0.44, 0.012, 0.025),
                       (cx, cy - 0.126, cz - 0.16), mat["steel_bare"], coll,
                       bevel=0.001, seg=1))
    parts.append(L.box(name + "_Terminal", (0.38, 0.08, 0.08),
                       (cx - 0.04, cy - 0.12, cz - 0.20), mat["rubber"], coll,
                       bevel=0.002, seg=2))
    parts.append(L.box(name + "_Label", (0.22, 0.005, 0.055),
                       (cx, cy - 0.094, cz + 0.31), mat["label"], coll,
                       bevel=0.001, seg=1))
    # loose wires spilling from the broken terminal
    for i, (x, y, z, m) in enumerate((
            (cx - 0.10, cy - 0.10, cz - 0.22, mat["cable_black"]),
            (cx + 0.02, cy - 0.08, cz - 0.18, mat["cable_orange"]),
            (cx + 0.12, cy - 0.12, cz - 0.24, mat["cable_grey"]))):
        parts.append(L.cable(f"{name}_Wire{i}", (x, y, z),
                             (x + 0.20 - i * 0.12, y - 0.22, 0.03),
                             0.05, 0.008, m, coll, n=10, sides=6))
    # small sparks / broken arc
    for i, pts in enumerate((
            [(cx - 0.13, cy - 0.14, cz - 0.18), (cx - 0.10, cy - 0.17, cz - 0.12),
             (cx - 0.15, cy - 0.18, cz - 0.07)],
            [(cx - 0.08, cy - 0.14, cz - 0.17), (cx - 0.04, cy - 0.18, cz - 0.11),
             (cx - 0.01, cy - 0.17, cz - 0.05)],
            [(cx + 0.13, cy - 0.14, cz - 0.20), (cx + 0.10, cy - 0.19, cz - 0.14),
             (cx + 0.15, cy - 0.18, cz - 0.09)])):
        parts.append(L.tube(f"{name}_Spark{i}", pts, 0.004, mat["spark"], coll,
                            sides=5, cap=True))
    ob = L.join(parts, name, coll)
    finish(ob, name)
    # scorch on the column above the cabinet, thin prism in XZ
    soot_pts = []
    rnd = random.Random(7)
    for i in range(16):
        a = TAU * i / 16
        soot_pts.append((cx + math.cos(a) * 0.44 * (1 + rnd.uniform(-0.2, 0.2)),
                         cz + 0.70 + math.sin(a) * 0.38 * (1 + rnd.uniform(-0.2, 0.2))))
    soot = poly_prism_xz(name + "_Soot", soot_pts, 15.762, 0.006, mat["soot"], coll)
    finish(soot, name + "_Soot")
    return ob


def build_checkpoint_lamp(name, coll, mat):
    parts = []
    x, y, z = -85.7, 10.19, 3.25
    parts.append(L.box(name + "_Bracket", (0.28, 0.10, 0.18), (x, y, z),
                       mat["steel_dark"], coll, bevel=0.004, seg=2))
    parts.append(L.box(name + "_Housing", (0.22, 0.05, 0.13), (x, y + 0.076, z - 0.03),
                       mat["paint_red"], coll, bevel=0.005, seg=2))
    parts.append(L.box(name + "_Lens", (0.15, 0.014, 0.075), (x, y + 0.109, z - 0.03),
                       mat["emissive_red"], coll, bevel=0.002, seg=2))
    parts.append(L.box(name + "_Grille", (0.19, 0.012, 0.020), (x, y + 0.108, z + 0.035),
                       mat["steel_dark"], coll, bevel=0.001, seg=1))
    ob = L.join(parts, name, coll)
    return finish(ob, name)


# --------------------------------------------------------------------------------------
# final lighting
# --------------------------------------------------------------------------------------
def _point(name, loc, energy, color, radius, coll):
    d = bpy.data.lights.new(name, "POINT")
    d.energy = energy
    d.color = color
    d.shadow_soft_size = radius
    o = bpy.data.objects.new(name, d)
    o.location = loc
    coll.objects.link(o)
    return o


def _area(name, loc, target, energy, color, size, coll):
    d = bpy.data.lights.new(name, "AREA")
    d.energy = energy
    d.color = color
    d.shape = "RECTANGLE"
    d.size = size[0]
    d.size_y = size[1]
    o = bpy.data.objects.new(name, d)
    o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    coll.objects.link(o)
    return o


def _boost_screen_material(base_name, new_name, strength):
    base = bpy.data.materials.get(base_name)
    if base is None:
        return None
    m = bpy.data.materials.get(new_name)
    if m is None:
        m = base.copy()
        m.name = new_name
    bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bsdf.inputs["Emission Strength"].default_value = strength
    return m


def _assign_security_screen_materials():
    glow = _boost_screen_material("M_HERO_Ops_ScreenGlow", "M_R21D_ScreenGlow", 1.55)
    ui = _boost_screen_material("M_HERO_Ops_ScreenUI", "M_R21D_ScreenUI", 2.60)
    if glow is None or ui is None:
        return
    for o in bpy.context.scene.objects:
        if o.type != "MESH" or not o.users_collection:
            continue
        bb = [o.matrix_world @ Vector(v) for v in o.bound_box]
        cx = (min(p.x for p in bb) + max(p.x for p in bb)) * 0.5
        cy = (min(p.y for p in bb) + max(p.y for p in bb)) * 0.5
        if not (-106.0 < cx < -70.0 and 9.0 < cy < 37.0):
            continue
        for slot in o.material_slots:
            if slot.material is None:
                continue
            if slot.material.name == "M_HERO_Ops_ScreenGlow":
                slot.material = glow
            elif slot.material.name == "M_HERO_Ops_ScreenUI":
                slot.material = ui


def _set_light(name, energy, color=None, radius=None, loc=None, hide=False):
    o = bpy.data.objects.get(name)
    if o is None or o.type != "LIGHT":
        return None
    o.data.energy = energy
    if color is not None:
        o.data.color = color
    if radius is not None:
        if hasattr(o.data, "shadow_soft_size"):
            o.data.shadow_soft_size = radius
    if loc is not None:
        o.location = loc
    o.hide_render = hide
    o.hide_viewport = hide
    return o


def finalize_lighting():
    """Four red emergency pools, monitor glow and one cold exit light. No general fill."""
    lc = sub("LIGHTS")
    for o in list(lc.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    # 1) checkpoint emergency fixture + red pool
    old_fix = bpy.data.objects.get("R21D_FIX_Emergency_Checkpoint")
    if old_fix:
        old_mesh = old_fix.data
        bpy.data.objects.remove(old_fix, do_unlink=True)
        if old_mesh.users == 0:
            bpy.data.meshes.remove(old_mesh)
    build_checkpoint_lamp("R21D_FIX_Emergency_Checkpoint",
                          bpy.data.collections.get(f"{ROOT}_FIXTURES"), materials())
    _point("R21D_LIGHT_Emergency_Checkpoint", (-85.70, 10.58, 3.22),
           18.0, (1.0, 0.030, 0.012), 0.17, lc)

    # 2) north operations emergency (existing fixture, stronger practical)
    _set_light("R21A_LIGHT_Emergency_N", 18.0, (1.0, 0.032, 0.012), 0.18)
    # 3) east lockers / hatch emergency
    _set_light("R21A_LIGHT_Emergency_E", 12.0, (1.0, 0.032, 0.012), 0.16)
    # 4) west briefing emergency
    _set_light("R21B_LIGHT_Emergency_1", 12.0, (1.0, 0.032, 0.012), 0.18)

    # turn off the surplus red practices; keep their housings as dark props
    for n in ("R21B_LIGHT_Emergency_0", "R21B_LIGHT_Emergency_2",
              "LIGHT_SEC03_Emergency_N", "LIGHT_SEC03_Emergency_E",
              "LIGHT_SEC02_Emergency"):
        _set_light(n, 0.0, hide=True)
    for n in ("LIGHT_SEC01_Ceiling_0", "LIGHT_SEC01_Ceiling_1",
              "LIGHT_SEC01_Ceiling_2", "LIGHT_SEC01_Ceiling_3",
              "LIGHT_SEC01_Ceiling_4", "LIGHT_SEC01_Ceiling_5",
              "LIGHT_SEC01_Ceiling_6"):
        _set_light(n, 0.0, hide=True)

    off = B.pbr("M_R21D_EmergencyOff", (0.10, 0.008, 0.004), 0.0, 0.52,
                noise=45.0, bump=0.12, rough_var=0.05)
    for n in ("R21B_SERV_EmergencyW1", "R21B_SERV_EmergencyS"):
        o = bpy.data.objects.get(n)
        if o and o.type == "MESH":
            for slot in o.material_slots:
                if slot.material and slot.material.name == "M_R21B_Emissive_Red":
                    slot.material = off

    # monitor glow: keep the four practical cyan areas, slightly stronger
    _set_light("R21A_LIGHT_Glow_A", 6.0, (0.28, 0.72, 0.64), 0.5)
    _set_light("R21A_LIGHT_Glow_B", 4.5, (0.24, 0.62, 0.58), 0.5)
    _set_light("R21A_LIGHT_Glow_C", 3.0, (0.22, 0.55, 0.58), 0.5)
    _set_light("R21A_LIGHT_Glow_CCTV", 14.0, (0.22, 0.62, 0.58), 0.5)
    _area("R21D_LIGHT_CheckpointGlow", (-89.35, 12.74, 1.40),
          (-89.35, 11.6, 1.15), 2.4, (0.26, 0.70, 0.62), (0.42, 0.18), lc)

    # spark on the damaged electrical cabinet
    _set_light("R21B_LIGHT_Spark", 3.2, (1.0, 0.18, 0.035), 0.09,
               loc=(-88.05, 15.33, 1.36))

    # cold emergency at the south exit sign (very dim, no general light)
    _point("R21D_LIGHT_ExitCold", (-89.0, 10.56, 3.20),
           1.5, (0.42, 0.78, 1.0), 0.12, lc)

    _assign_security_screen_materials()

    s = bpy.context.scene
    s.view_settings.view_transform = "AgX"
    try:
        s.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        pass
    s.view_settings.exposure = 0.72
    s.eevee.taa_render_samples = 64

    print("R21D_LIGHTING_OK lights", len(lc.objects))



# --------------------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------------------
def build():
    clean_root()
    mat = materials()
    chaos = sub("CHAOS")
    fixtures = sub("FIXTURES")

    rnd = random.Random(2104)

    # --- dragged / tipped chairs (reuse the R21C hero chair) -------------------------
    duplicate_asset("R21C_CHAOS_ChairA", "R21D_Chair_DraggedA", chaos,
                    (-85.65, 14.85, 0.0), rot_z=34.0, rot_xyz=(0.0, 84.0, 0.0))
    duplicate_asset("R21C_CHAOS_ChairB", "R21D_Chair_DraggedB", chaos,
                    (-96.35, 17.95, 0.0), rot_z=-63.0, rot_xyz=(82.0, 0.0, 18.0))
    duplicate_asset("R21A_CHAIR_C_TIPPED", "R21D_Chair_DraggedC", chaos,
                    (-80.95, 27.65, 0.0), rot_z=118.0, rot_xyz=(0.0, 0.0, 0.0))
    # a fourth, upright but shoved out of the briefing table
    duplicate_asset("R21C_CHAOS_ChairA", "R21D_Chair_Displaced", chaos,
                    (-98.35, 17.55, 0.0), rot_z=41.0)

    # --- detached locker doors -------------------------------------------------------
    door_a = build_locker_door("R21D_LockerDoor_LeaningA", (0.0, 0.0, 0.0),
                               (0.0, 0.0, 0.0), chaos, mat, bent=True)
    door_a.matrix_world = (Matrix.Translation((-71.74, 18.92, 0.0)) @
                           Matrix.Rotation(math.radians(38.0), 4, "Y") @
                           Matrix.Rotation(math.radians(90.0), 4, "Z"))
    bpy.context.view_layer.update()
    lo = min((door_a.matrix_world @ v.co).z for v in door_a.data.vertices)
    door_a.matrix_world = Matrix.Translation((0, 0, 0.001 - lo)) @ door_a.matrix_world
    build_locker_door("R21D_LockerDoor_FloorB", (-77.45, 12.28, 0.0),
                      (-88.0, 0.0, 28.0), chaos, mat, bent=False)

    # --- collapsed ceiling field -----------------------------------------------------
    build_ceiling_tile("R21D_CeilingTile_FlatA", (-84.80, 18.62, 0.0),
                       (0.0, 0.0, 23.0), chaos, mat)
    build_ceiling_tile("R21D_CeilingTile_FlatB", (-85.56, 18.15, 0.0),
                       (0.0, 0.0, -12.0), chaos, mat)
    build_ceiling_tile("R21D_CeilingTile_LeanC", (-86.54, 17.55, 0.0),
                       (-68.0, 0.0, 9.0), chaos, mat)
    hanging = build_ceiling_tile("R21D_CeilingTile_HangingD", (-83.90, 19.16, 4.05),
                                 (-26.0, 0.0, 14.0), chaos, mat, hanging=True)
    # two suspension wires from the ceiling grid to the hanging tile
    for i, (x, y) in enumerate(((-83.62, 19.02), (-84.18, 19.34))):
        L.cable(f"R21D_CeilingWire_{i}", (x, y, 4.705), (x, y, 4.060),
                0.01, 0.0045, mat["steel_bare"], chaos, n=7, sides=5)
    # dark missing-tile patch in the ceiling
    hole = []
    for i in range(14):
        a = TAU * i / 14
        hole.append((-84.60 + math.cos(a) * 1.05 * (1 + rnd.uniform(-0.18, 0.18)),
                    19.25 + math.sin(a) * 0.80 * (1 + rnd.uniform(-0.18, 0.18))))
    poly_plate_xy("R21D_CeilingHole", hole, 4.682, 0.020, mat["soot"], chaos)
    # exposed grid bars around the hole
    for i, (x, y, sx, sy) in enumerate((
            (-85.80, 18.30, 0.06, 1.55), (-83.35, 18.30, 0.06, 1.55),
            (-84.58, 17.55, 2.45, 0.06), (-84.58, 19.00, 1.20, 0.06))):
        L.box(f"R21D_CeilingGrid_{i}", (sx, sy, 0.045), (x, y, 4.690),
              mat["galv"], chaos, bevel=0.003, seg=2)
    # hanging torn cables from the hole
    L.cable("R21D_Cable_HangA", (-85.05, 18.95, 4.705), (-84.72, 18.62, 1.05),
            0.05, 0.016, mat["cable_black"], chaos, n=16, sides=6, wiggle=0.10, seed=3)
    L.cable("R21D_Cable_HangB", (-84.18, 19.42, 4.705), (-84.45, 19.10, 1.42),
            0.12, 0.013, mat["cable_grey"], chaos, n=16, sides=6, wiggle=0.14, seed=8)
    L.cable("R21D_Cable_HangC", (-83.55, 18.55, 4.705), (-83.85, 18.25, 0.75),
            0.04, 0.011, mat["cable_orange"], chaos, n=16, sides=6, wiggle=0.09, seed=5)
    # torn conduit with flange
    L.cyl("R21D_ConduitFlange", 0.07, 0.030, (-83.55, 18.55, 4.69),
          mat["galv"], chaos, segments=12, bevel=0.003, seg=2)
    L.cable("R21D_ConduitBent", (-83.55, 18.55, 4.70), (-83.35, 18.28, 3.55),
            0.16, 0.028, mat["steel_dark"], chaos, n=10, sides=8)

    # --- broken CRT and glass --------------------------------------------------------
    build_crt("R21D_CRT_Broken", (-84.18, 14.32, 0.0), 17.0, chaos, mat)
    # CRT safety glass fragments around the broken screen
    for i in range(10):
        a = rnd.uniform(0, TAU)
        rr = rnd.uniform(0.35, 0.85)
        L.box(f"R21D_CRTShard_{i}",
              (rnd.uniform(0.012, 0.035), rnd.uniform(0.03, 0.10), 0.002),
              (-84.18 + math.cos(a) * rr, 14.32 + math.sin(a) * rr, 0.003 + i * 0.00035),
              mat["glass"], chaos, rot=(0, 0, rnd.uniform(0, 360)),
              bevel=0.0003, seg=1)
    build_glass_pane("R21D_GlassPane_Broken", (-90.72, 25.55, 0.0),
                     (-12.0, 0.0, 0.0), chaos, mat)
    # shards around the pane and the hatch
    for i in range(14):
        a = rnd.uniform(0, TAU)
        rr = rnd.uniform(0.25, 1.20)
        shard = L.box(f"R21D_GlassShard_{i}",
                      (rnd.uniform(0.015, 0.045), rnd.uniform(0.05, 0.16), 0.0025),
                      (-90.50 + math.cos(a) * rr, 25.20 + math.sin(a) * rr * 0.55, 0.003 + i * 0.00035),
                      mat["glass"], chaos, rot=(0, 0, rnd.uniform(0, 360)),
                      bevel=0.0003, seg=1)
    for i in range(8):
        L.box(f"R21D_HatchShard_{i}",
              (rnd.uniform(0.02, 0.05), rnd.uniform(0.04, 0.12), 0.002),
              (-72.10 + rnd.uniform(-0.8, 0.4), 11.10 + rnd.uniform(-0.7, 0.8), 0.003 + i * 0.00035),
              mat["glass"], chaos, rot=(0, 0, rnd.uniform(0, 360)),
              bevel=0.0003, seg=1)

    # --- damaged electrical cabinet --------------------------------------------------
    build_electrical_box("R21D_ElectricalBox", fixtures, mat)
    # a little cover plate and debris on the floor below
    L.box("R21D_ElectricalCover", (0.22, 0.16, 0.018), (-88.25, 15.30, 0.02),
          mat["paint_olive"], chaos, rot=(0, 0, 33), bevel=0.002, seg=2)

    # --- lockers / floor clutter -----------------------------------------------------
    build_pallet("R21D_Pallet", (-73.05, 20.55, 0.0), 92.0, chaos, mat, boxes=2)
    build_cardboard_box("R21D_Crate_Dropped", (-72.55, 21.75, 0.0),
                        36.0, (0.48, 0.42, 0.34), chaos, mat)
    build_cardboard_box("R21D_Crate_Stack", (-72.45, 20.15, 0.0),
                        6.0, (0.40, 0.34, 0.28), chaos, mat)
    build_pallet("R21D_PalletB", (-95.30, 16.45, 0.0), 8.0, chaos, mat, boxes=1)
    duplicate_asset("R21B_CHAOS_CableReelA", "R21D_CableReel_Tipped", chaos,
                    (-93.55, 15.10, 0.0), rot_z=71.0, rot_xyz=(0.0, 84.0, 0.0))
    build_cone("R21D_Cone_Tipped", (-86.72, 13.28, 0.0), 22.0, True, chaos, mat)
    build_cone("R21D_Cone_Upright", (-81.10, 17.75, 0.0), -12.0, False, chaos, mat)

    # loose cable from the tipped reel across the floor
    L.cable("R21D_ReelCable", (-93.45, 15.02, 0.10), (-91.70, 14.80, 0.03),
            0.02, 0.012, mat["cable_black"], chaos, n=14, sides=6, wiggle=0.12, seed=2)
    L.cable("R21D_Cable_Checkpoint", (-89.62, 14.62, 4.705), (-89.45, 14.52, 2.10),
            0.02, 0.013, mat["cable_black"], chaos, n=14, sides=6, wiggle=0.05, seed=9)

    # --- puddles / dust / debris -----------------------------------------------------
    jagged_ring("R21D_Puddle_CheckpointWet", -90.05, 15.25, 1.55, 0.92, 0.0015,
                mat["concrete_dark"], chaos, n=22, seed=31)
    jagged_ring("R21D_Puddle_Checkpoint", -90.05, 15.25, 1.25, 0.70, 0.0035,
                mat["water"], chaos, n=22, seed=32)
    jagged_ring("R21D_Puddle_HoleWet", -83.55, 17.55, 1.35, 0.88, 0.0015,
                mat["concrete_dark"], chaos, n=24, seed=41)
    jagged_ring("R21D_Puddle_Hole", -83.55, 17.55, 1.08, 0.68, 0.0035,
                mat["water"], chaos, n=24, seed=42)
    jagged_ring("R21D_Puddle_Glass", -88.90, 24.80, 0.90, 0.55, 0.0035,
                mat["water"], chaos, n=18, seed=51)
    for i, (x, y, rx, ry, seed) in enumerate((
            (-99.60, 13.10, 1.60, 1.05, 61), (-76.20, 25.20, 1.90, 1.10, 62),
            (-101.20, 29.80, 1.45, 0.90, 63))):
        jagged_ring(f"R21D_Dust_{i}", x, y, rx, ry, 0.0012, mat["dust"], chaos,
                    n=20, seed=seed)
    for i, (x, y, rx, ry, seed) in enumerate((
            (-96.10, 23.60, 2.40, 1.30, 71), (-80.50, 15.50, 1.70, 1.00, 72))):
        jagged_ring(f"R21D_DustHeavy_{i}", x, y, rx, ry, 0.0018, mat["dust2"], chaos,
                    n=20, seed=seed)
    # concrete and metal debris around the collapsed ceiling and column bases
    for i in range(16):
        a = rnd.uniform(0, TAU)
        rr = rnd.uniform(0.45, 2.20)
        x = -84.60 + math.cos(a) * rr
        y = 18.35 + math.sin(a) * rr * 0.75
        s = rnd.uniform(0.06, 0.22)
        r = B.rock(f"R21D_Debris_Concrete_{i}", (x, y, s * 0.55),
                   (s, s * 0.85, s * 0.55), mat["concrete"], chaos, seed=100 + i, subdiv=2)
        lo = min((r.matrix_world @ v.co).z for v in r.data.vertices)
        r.location.z += 0.001 - lo
    for i in range(8):
        x = -88.0 + rnd.uniform(-1.5, 1.5)
        y = 15.6 + rnd.uniform(-1.1, 1.1)
        s = rnd.uniform(0.04, 0.12)
        r = B.rock(f"R21D_Debris_Metal_{i}", (x, y, s * 0.18),
                   (s, s * 0.6, s * 0.18), mat["steel_rust"], chaos,
                   seed=200 + i, subdiv=2)
        lo = min((r.matrix_world @ v.co).z for v in r.data.vertices)
        r.location.z += 0.001 - lo

    # --- displaced existing furniture ------------------------------------------------
    transform_about_centre(bpy.data.objects.get("R21B_CIRC_WaitBenchB"),
                           rz=18.0, dx=-0.55, dy=0.20)
    transform_about_centre(bpy.data.objects.get("R21C_CART_ToolCart"),
                           rz=22.0, dx=1.00, dy=-1.25)
    transform_about_centre(bpy.data.objects.get("R21B_BRIEF_Chair_04"),
                           rz=38.0, dx=-1.45, dy=-1.35)

    # report
    total = 0
    for o in root_collection().all_objects:
        if o.type == "MESH":
            total += sum(len(p.vertices) - 2 for p in o.data.polygons)
    print("R21D_BUILD_OK objects", len(root_collection().all_objects), "tris", total)


if __name__ == "__main__":
    build()
    finalize_lighting()
