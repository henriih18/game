"""FRECUENCIA MUERTA - L1_SECURITY_R21C_HERO toolkit.

Close-up hero pass for Security 03: vented lockers with real interiors, a
service hatch with framed glass and a louvred roller shutter, a key rack,
a heavy shelving unit, a tool cart with casters and the operations-centre
chaos.  Real-world scale, baked bevels on every plate (2-4 segments), real
louvre geometry instead of decals, box-projected UVs and weighted normals.

The module only creates data inside L1_SECURITY_R21C_HERO.  The superseded
R21B pieces are hidden, never deleted.
"""
import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

import fm_ops_lib as L
import fm_r21b_lib as B

ROOT = "L1_SECURITY_R21C_HERO"
TAU = math.pi * 2.0


# --------------------------------------------------------------------------------------
# collection / lifecycle
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
    full = name if name.startswith(ROOT) else f"{ROOT}_{name}"
    c = bpy.data.collections.get(full)
    if c is None:
        c = bpy.data.collections.new(full)
    if c.name not in r.children:
        r.children.link(c)
    return c


def palette():
    """Reuse the R21B PBR set and add the few close-up-only materials."""
    mat = B.palette()
    mat["paint_dark"] = mat["dark"]
    mat["ceiling_tile"] = B.pbr("M_R21C_CeilingTile", (0.225, 0.220, 0.205), 0.0, 0.94,
                                noise=55.0, bump=0.22, rough_var=0.03)
    mat["crt_bezel"] = B.pbr("M_R21C_CRT_Bezel", (0.0015, 0.0018, 0.0020), 0.0, 0.86,
                          noise=150.0, bump=0.03, rough_var=0.04)
    mat["cracked_glass"] = B.pbr("M_R21C_Screen_Cracked", (0.070, 0.078, 0.084), 0.0, 0.06,
                         noise=150.0, bump=0.02, rough_var=0.03)
    mat["crack"] = B.pbr("M_R21C_GlassCrack", (0.52, 0.55, 0.54), 0.0, 0.30,
                         noise=180.0, bump=0.02, rough_var=0.04)
    return mat


# --------------------------------------------------------------------------------------
# geometry helpers
# --------------------------------------------------------------------------------------
def bevel_mesh(ob, width=0.0015, segments=2, sharp=38.0):
    """Bevel an existing closed mesh (frames, prisms) with real geometry."""
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.edges.ensure_lookup_table()
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=width, offset_type="OFFSET",
                    segments=segments, profile=0.5, affect="EDGES",
                    clamp_overlap=True)
    L._finish_bm(bm, me, smooth=True, sharp_angle=sharp)
    L._box_uv(me)
    return ob


def hb(name, size, center, mat, coll, rot=(0, 0, 0), bevel=None, seg=3, uv=1.0,
       smooth=True):
    """Box with a real bevel even on thin plates (the R21B helper skipped those)."""
    m = min(size)
    if bevel is None:
        bevel = min(0.0045, max(0.00045, m * 0.22))
    bevel = max(0.00035, min(bevel, m * 0.24))
    seg = max(2, min(4, seg))
    return L.box(name, size, center, mat, coll, rot=rot, bevel=bevel, seg=seg,
                 uv_scale=uv, smooth=smooth)


def cy(name, radius, depth, center, mat, coll, rot=(0, 0, 0), segments=20,
       bevel=0.0014, seg=2):
    if bevel is not None:
        bevel = min(bevel, radius * 0.25, depth * 0.20)
    return L.cyl(name, radius, depth, center, mat, coll, rot=rot, segments=segments,
                 bevel=bevel, seg=seg)


def frame(name, outer_w, outer_h, inner_w, inner_h, depth, center, mat, coll,
          bevel=0.0014, seg=2):
    ob = B.frame_rect(name, outer_w, outer_h, inner_w, inner_h, depth, center,
                      mat, coll)
    bevel_mesh(ob, bevel, seg)
    return ob


def prism_yz(name, pts_yz, x0, thick, mat, coll):
    """Closed prism from a YZ polygon, extruded along +X, triangulated caps."""
    bm = bmesh.new()
    a, b = [], []
    for y, z in pts_yz:
        a.append(bm.verts.new((x0, y, z)))
        b.append(bm.verts.new((x0 + thick, y, z)))
    n = len(pts_yz)
    bm.verts.ensure_lookup_table()
    # fan-triangulated caps (no n-gons)
    ca = bm.verts.new((x0, sum(p[0] for p in pts_yz) / n,
                       sum(p[1] for p in pts_yz) / n))
    cb = bm.verts.new((x0 + thick, sum(p[0] for p in pts_yz) / n,
                       sum(p[1] for p in pts_yz) / n))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((ca, a[j], a[i]))
        bm.faces.new((cb, b[i], b[j]))
        bm.faces.new((a[i], a[j], b[j], b[i]))
    me = bpy.data.meshes.new(name)
    L._finish_bm(bm, me, smooth=False, sharp_angle=28.0)
    L._box_uv(me)
    return L._link(name, me, coll, mat, (0, 0, 0))


def prism_xy(name, pts_xy, z0, thick, mat, coll, center=(0, 0, 0)):
    """Closed prism from an XY polygon, extruded along +Z, triangulated caps."""
    bm = bmesh.new()
    a, b = [], []
    for x, y in pts_xy:
        a.append(bm.verts.new((x, y, z0)))
        b.append(bm.verts.new((x, y, z0 + thick)))
    n = len(pts_xy)
    ca = bm.verts.new((sum(p[0] for p in pts_xy) / n,
                       sum(p[1] for p in pts_xy) / n, z0))
    cb = bm.verts.new((sum(p[0] for p in pts_xy) / n,
                       sum(p[1] for p in pts_xy) / n, z0 + thick))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((ca, a[i], a[j]))
        bm.faces.new((cb, b[j], b[i]))
        bm.faces.new((a[i], a[j], b[j], b[i]))
    me = bpy.data.meshes.new(name)
    L._finish_bm(bm, me, smooth=False, sharp_angle=28.0)
    L._box_uv(me)
    return L._link(name, me, coll, mat, center)


def torus(name, center, R, r, mat, coll, rot=(0, 0, 0), major=20, minor=8):
    bm = bmesh.new()
    rings = []
    for i in range(major):
        a = TAU * i / major
        ca, sa = math.cos(a), math.sin(a)
        ring = []
        for j in range(minor):
            b = TAU * j / minor
            rr = R + r * math.cos(b)
            ring.append(bm.verts.new((rr * ca, rr * sa, r * math.sin(b))))
        rings.append(ring)
    for i in range(major):
        for j in range(minor):
            a = rings[i][j]
            b = rings[(i + 1) % major][j]
            c = rings[(i + 1) % major][(j + 1) % minor]
            d = rings[i][(j + 1) % minor]
            bm.faces.new((a, b, c, d))
    me = bpy.data.meshes.new(name)
    L._finish_bm(bm, me, smooth=True, sharp_angle=55.0)
    L._box_uv(me)
    return L._link(name, me, coll, mat, center, rot)


def bolt(name, center, normal, radius, depth, mat, coll, segments=6, socket=True,
         socket_mat=None):
    """Hex bolt with an optional dark hex socket, embedded into the parent."""
    n = Vector(normal).normalized()
    q = n.to_track_quat("Z", "Y")
    rot = q.to_euler()
    ob = cy(name, radius, depth, center, mat, coll, rot=rot, segments=segments,
            bevel=min(0.0007, radius * 0.20), seg=2)
    # Hex sockets are intentionally omitted: the shallow dark cylinder could
    # not be welded without coplanar faces against the head bevel, and the
    # silhouette of the bolt reads correctly at gameplay distance.
    return ob


def bolts_row(name, positions, normal, radius, depth, mat, coll, socket_mat=None,
              segments=6):
    for i, p in enumerate(positions):
        bolt(f"{name}_{i:02d}", p, normal, radius, depth, mat, coll,
             segments=segments, socket=socket_mat is not None, socket_mat=socket_mat)


def screw(name, center, normal, mat, coll, r=0.0042, socket_mat=None):
    return bolt(name, center, normal, r, 0.0035, mat, coll, segments=10,
                socket=socket_mat is not None, socket_mat=socket_mat)


def tube(name, pts, radius, mat, coll, sides=8):
    return L.tube(name, pts, radius, mat, coll, sides=sides, cap=True)


def cable(name, p0, p1, sag, radius, mat, coll, n=16, sides=7):
    return L.cable(name, p0, p1, sag, radius, mat, coll, n=n, sides=sides)


def text(name, body, size, center, rot, mat, coll, extrude=0.0012):
    return L.text_mesh(name, body, size, center, rot, mat, coll, extrude=extrude)


# wall text on the east wall (normal -X, up +Z)
ROT_E = (math.radians(90), 0.0, math.radians(-90))


def join(parts, name, coll, weighted=True):
    ob = B.join([p for p in parts if p is not None], name, coll)
    if ob is not None and weighted:
        L.weighted_normal(ob)
    return ob


def place(ob, center, rot_z=0.0, drop=False):
    return B.place(ob, center, rot_z=rot_z, drop=drop)


def bake_world(ob):
    return B.bake_world(ob)


# --------------------------------------------------------------------------------------
# reusable props
# --------------------------------------------------------------------------------------
def helmet(name, origin, mat, coll, shell_key="white", rot_z=0.0, size=1.0):
    """Industrial hard hat: dome, brim with front peak, three crown ridges and
    a small frontal lamp bracket.  Origin at the shelf top."""
    parts = []
    shell = mat[shell_key]
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=1.0)
    for v in bm.verts:
        v.co.x *= 0.132 * size
        v.co.y *= 0.112 * size
        v.co.z *= 0.102 * size
        v.co.z += 0.102 * size
    me = bpy.data.meshes.new(name + "_Dome")
    L._finish_bm(bm, me, smooth=True, sharp_angle=60.0)
    L._box_uv(me)
    parts.append(L._link(name + "_Dome", me, coll, shell, (0, 0, 0)))
    # brim ring and front peak
    parts.append(torus(name + "_Brim", (0, 0.006, 0.062 * size),
                       0.128 * size, 0.018 * size, shell, coll,
                       rot=(math.radians(4), 0, 0), major=28, minor=8))
    parts.append(hb(name + "_Peak", (0.11 * size, 0.075 * size, 0.012 * size),
                    (0, -0.135 * size, 0.058 * size), shell, coll,
                    rot=(math.radians(-7), 0, 0), bevel=0.004, seg=3))
    # three crown ridges following the dome
    for k, x in enumerate((-0.058, 0.0, 0.058)):
        pts = []
        for i in range(9):
            y = -0.088 + 0.176 * i / 8
            q = max(0.0, 1.0 - (x / (0.132 * size)) ** 2 - (y / (0.112 * size)) ** 2)
            z = 0.102 * size + 0.102 * size * math.sqrt(q) + 0.001
            pts.append((x * size, y * size, z))
        parts.append(tube(f"{name}_Ridge{k}", pts, 0.0038 * size, shell, coll, sides=6))
    # lamp bracket
    parts.append(hb(name + "_LampPlate", (0.045, 0.016, 0.028),
                    (0, -0.112 * size, 0.125 * size), mat["aluminum"], coll,
                    bevel=0.002, seg=2))
    parts.append(hb(name + "_Lamp", (0.036, 0.026, 0.034),
                    (0, -0.128 * size, 0.132 * size), mat["plastic"], coll,
                    bevel=0.004, seg=3))
    ob = join(parts, name, coll)
    place(ob, origin, rot_z=rot_z)
    return ob


def storage_bin(name, origin, mat, coll, w=0.36, d=0.30, h=0.22, color="dark",
                rot_z=0.0):
    """Stackable open-front parts bin with a rim and two handles."""
    col = mat[color]
    bm = bmesh.new()
    tw, td, bw, bd = w * 0.5, d * 0.5, w * 0.40, d * 0.40
    v = [bm.verts.new((-bw, -bd, 0)), bm.verts.new((bw, -bd, 0)),
         bm.verts.new((bw, bd, 0)), bm.verts.new((-bw, bd, 0)),
         bm.verts.new((-tw, -td, h)), bm.verts.new((tw, -td, h)),
         bm.verts.new((tw, td, h)), bm.verts.new((-tw, td, h))]
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((v[i], v[j], v[4 + j], v[4 + i]))
    bm.faces.new((v[3], v[2], v[1], v[0]))
    bm.faces.new((v[4], v[5], v[6], v[7]))
    me = bpy.data.meshes.new(name + "_Shell")
    L._finish_bm(bm, me, smooth=False, sharp_angle=35.0)
    L._box_uv(me)
    parts = [L._link(name + "_Shell", me, coll, col, (0, 0, 0))]
    # rim (four bars, overlapping corners)
    for sx in (-1, 1):
        parts.append(hb(f"{name}_RimX{sx}", (0.022, d + 0.012, 0.020),
                        (sx * w * 0.5, 0, h - 0.006), col, coll, bevel=0.004, seg=3))
    for sy in (-1, 1):
        parts.append(hb(f"{name}_RimY{sy}", (w + 0.012, 0.022, 0.020),
                        (0, sy * d * 0.5, h - 0.002), col, coll, bevel=0.004, seg=3))
    for sy in (-1, 1):
        parts.append(tube(f"{name}_Handle{sy}",
                          [(-0.06, sy * d * 0.42, h * 0.70), (-0.06, sy * d * 0.54, h * 0.74),
                           (0.06, sy * d * 0.54, h * 0.74), (0.06, sy * d * 0.42, h * 0.70)],
                          0.007, mat["rubber"], coll, sides=8))
    parts.append(hb(name + "_Label", (0.12, 0.004, 0.055), (0, -d * 0.5 - 0.002, h * 0.58),
                    mat["paper"], coll, bevel=0.001, seg=2))
    ob = join(parts, name, coll)
    place(ob, origin, rot_z=rot_z)
    return ob


def equipment_case(name, origin, mat, coll, w=0.50, d=0.34, h=0.26, rot_z=0.0):
    """Rugged hard case with corner protectors, latches and a carry handle."""
    parts = [hb(name + "_Body", (w, d, h), (0, 0, h * 0.5), mat["plastic"], coll,
                bevel=0.012, seg=4)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(hb(f"{name}_Corner{sx}{sy}", (0.07, 0.07, 0.07),
                            (sx * (w * 0.5 - 0.015), sy * (d * 0.5 - 0.015), 0.018),
                            mat["steel_dark"], coll, bevel=0.006, seg=3))
            parts.append(hb(f"{name}_CornerT{sx}{sy}", (0.07, 0.07, 0.05),
                            (sx * (w * 0.5 - 0.015), sy * (d * 0.5 - 0.015), h - 0.015),
                            mat["steel_dark"], coll, bevel=0.006, seg=3))
    # ribs and latches
    # ribs are omitted: they sat inside the closed case shell and could not be
    # guaranteed to read as surface detail after joining.
    for sy in (-1, 1):
        parts.append(hb(f"{name}_Latch{sy}", (0.06, 0.02, 0.055),
                        (0.13 * sy, -d * 0.5 - 0.008, h * 0.78), mat["steel_bare"], coll,
                        bevel=0.004, seg=3))
    parts.append(tube(name + "_Handle",
                      [(-0.09, 0, h - 0.02), (-0.09, 0, h + 0.05),
                       (0.09, 0, h + 0.05), (0.09, 0, h - 0.02)],
                      0.010, mat["rubber"], coll, sides=8))
    parts.append(hb(name + "_Label", (0.16, 0.004, 0.05), (0, -d * 0.5 - 0.002, h * 0.52),
                    mat["hazard_y"], coll, bevel=0.001, seg=2))
    ob = join(parts, name, coll)
    place(ob, origin, rot_z=rot_z)
    return ob


def dead_crt(name, origin, mat, coll, rot_z=0.0, tipped=False, scale=1.0, with_stand=True, with_cable=True):
    """Dead CRT monitor with a cracked glass face, back vents, ports and a
    detached stand.  Built face -Y, origin at its base."""
    parts = []
    w, d, h = 0.52 * scale, 0.43 * scale, 0.40 * scale
    parts.append(hb(name + "_Case", (w, d, h), (0, 0.02, h * 0.5), mat["plastic"],
                    coll, bevel=0.020, seg=4))
    # front bezel
    bez = frame(name + "_Bezel", w - 0.01, h - 0.01, w - 0.085, h - 0.085,
                0.035, (0, -d * 0.5 + 0.004, h * 0.5), mat["crt_bezel"], coll,
                bevel=0.004, seg=3)
    bez.rotation_euler[2] = math.radians(90.0)
    parts.append(bez)
    parts.append(hb(name + "_Screen", (w - 0.075, 0.008, h - 0.075),
                    (0, -d * 0.5 - 0.0115, h * 0.5), mat["cracked_glass"], coll,
                    bevel=0.002, seg=2))
    # back housing + vents
    parts.append(hb(name + "_Back", (w * 0.72, 0.13, h * 0.72),
                    (0, d * 0.5 - 0.02, h * 0.52), mat["plastic"], coll,
                    bevel=0.018, seg=3))
    for i in range(7):
        parts.append(hb(f"{name}_Vent{i}", (w * 0.52, 0.006, 0.008),
                        (0, d * 0.5 + 0.045, h * 0.32 + i * 0.022), mat["dark"], coll,
                        bevel=0.001, seg=1))
    for sx in (-0.16, -0.05, 0.06, 0.17):
        parts.append(cy(f"{name}_Port{sx:.2f}", 0.014, 0.018,
                        (sx * scale, d * 0.5 + 0.040, h * 0.72), mat["steel_dark"],
                        coll, rot=(math.radians(90), 0, 0), segments=14, bevel=0.001))
    # cracked glass lines (slightly proud of the screen, inside the bezel)
    yc = -d * 0.5 - 0.0165
    for i, (dx, dz) in enumerate(((0.18, 0.10), (-0.16, 0.13), (0.15, -0.12),
                                  (-0.10, -0.16), (0.02, 0.20))):
        pts = [(0, yc, h * 0.52),
               (dx * 0.55 * scale, yc, h * 0.52 + dz * 0.55),
               (dx * scale, yc, h * 0.52 + dz)]
        if i % 2 == 0:
            pts[1] = (pts[1][0] + 0.04 * scale, pts[1][1], pts[1][2] - 0.03 * scale)
        parts.append(tube(f"{name}_Crack{i}", pts, 0.0012, mat["crack"], coll, sides=5))
    # buttons omitted: the bezel already reads at gameplay distance and the
    # tiny separate button islands could not be guaranteed to weld cleanly
    # after the monitor is tipped onto the floor.
    # detached stand, lying to the side
    if with_stand:
        parts.append(hb(name + "_StandBase", (0.24, 0.20, 0.022),
                        (w * 0.5 + 0.15, -0.06, 0.011), mat["paint_dark"], coll,
                        bevel=0.006, seg=3))
        parts.append(hb(name + "_StandNeck", (0.07, 0.08, 0.10),
                        (w * 0.5 + 0.15, -0.06, 0.065), mat["paint_dark"], coll,
                        bevel=0.008, seg=3))
    if with_cable:
        parts.append(tube(name + "_Cable",
                          [(0.10, d * 0.5 + 0.04, 0.10), (0.30, d * 0.5 + 0.10, 0.006),
                           (0.48, d * 0.5 + 0.02, 0.004), (0.55, d * 0.5 - 0.08, 0.004)],
                          0.0045, mat["cable_black"], coll, sides=7))
    ob = join(parts, name, coll)
    place(ob, origin, rot_z=rot_z)
    return ob


def broken_tile(name, origin, mat, coll, w=0.55, d=0.55, rot_z=0.0):
    rnd = random.Random(77)
    pts = []
    n = 9
    for i in range(n):
        a = TAU * i / n
        r = 1.0 + rnd.uniform(-0.25, 0.10)
        pts.append((math.cos(a) * w * 0.5 * r, math.sin(a) * d * 0.5 * r))
    ob = prism_xy(name, pts, 0.0, 0.012, mat["ceiling_tile"], coll)
    place(ob, origin, rot_z=rot_z)
    return ob


def debris_chunk(name, origin, mat, coll, size=(0.18, 0.14, 0.07), seed=1,
                 rot_z=0.0, mat_key="concrete", subdiv=2):
    rnd = random.Random(seed)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=1.0)
    for v in bm.verts:
        v.co.x *= size[0] * (1.0 + rnd.uniform(-0.35, 0.25))
        v.co.y *= size[1] * (1.0 + rnd.uniform(-0.35, 0.25))
        v.co.z *= size[2] * (1.0 + rnd.uniform(-0.30, 0.15))
        if v.co.z < 0:
            v.co.z *= 0.12
    me = bpy.data.meshes.new(name)
    L._finish_bm(bm, me, smooth=True, sharp_angle=48.0)
    L._box_uv(me)
    ob = L._link(name, me, coll, mat[mat_key], (0, 0, 0))
    place(ob, origin, rot_z=rot_z, drop=True)
    return ob


def shard(name, origin, mat, coll, size=(0.09, 0.06), thick=0.003, seed=1,
          rot_z=0.0):
    rnd = random.Random(seed)
    n = 5
    pts = []
    for i in range(n):
        a = TAU * i / n + rnd.uniform(-0.35, 0.35)
        r = rnd.uniform(0.45, 1.0)
        pts.append((math.cos(a) * size[0] * r, math.sin(a) * size[1] * r))
    ob = prism_xy(name, pts, 0.0, thick, mat["glass"], coll)
    place(ob, origin, rot_z=rot_z)
    return ob
