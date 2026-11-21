"""
FRECUENCIA MUERTA - P0a SERVICES masters.

Every module is built with the same connection sections:
  rect duct 800x600 / 600x400, circular 300, tray 400x100,
  sprinkler 80 / 50, conduit 25 / 40.
Ports are local coordinates stored on the root (fm_ports JSON).  Straight
modules run 0..L on +X; elbows leave +X and bend +Y; tees branch +Y (duct)
or -Z (sprinkler, conduit).
"""
import bpy
import bmesh
import math
import json
from mathutils import Vector, Matrix

from fm_shared_p0_lib import (ensure_tree, ensure_materials, make_root,
                              parent_to, box, cyl, cone, screw, bolt,
                              join_group, finalize_master, tri_count,
                              make_part, bm_box, bm_cyl, bm_pipe_x,
                              bm_pipe_arc, bm_rect_tube_x, bm_rect_frame_x,
                              bm_rect_loft_x, clear_collection_tree, flange_bolts)

M = ensure_materials()

GALV = M["galv"]
DARK = M["steel_dark"]
BARE = M["steel_bare"]
ALU = M["aluminum"]
RUB = M["rubber"]
RED = M["sprink_red"]
COND = M["conduit"]
CABLE = M["cable"]
BRASS = M["brass"]
FIRESTOP = M["firestop"]
LABEL = M["label"]
PAINT = M["paint_door"]
ORANGE = M["paint_orange"]


def bm_rot(bm, rz=0.0, ry=0.0, rx=0.0, loc=(0, 0, 0)):
    if rz:
        bmesh.ops.rotate(bm, cent=(0, 0, 0),
                         matrix=Matrix.Rotation(rz, 3, 'Z'), verts=bm.verts[:])
    if ry:
        bmesh.ops.rotate(bm, cent=(0, 0, 0),
                         matrix=Matrix.Rotation(ry, 3, 'Y'), verts=bm.verts[:])
    if rx:
        bmesh.ops.rotate(bm, cent=(0, 0, 0),
                         matrix=Matrix.Rotation(rx, 3, 'X'), verts=bm.verts[:])
    bmesh.ops.translate(bm, vec=Vector(loc), verts=bm.verts[:])
    return bm


def part_bm(coll, name, bm, mat, bevel=0.0012, seg=2):
    return make_part(name, bm, mat, coll, bevel, seg)


# ---------------------------------------------------------------------------
# rectangular duct
# ---------------------------------------------------------------------------

def duct_straight(coll, name, w, h, length, access=False):
    parts = []
    # body starts inside the inlet flange lip
    parts.append(part_bm(coll, name + "_Body",
                         bm_rect_tube_x(0.002, length - 0.003, w, h, 0.004, 0, 0),
                         GALV, 0.0015, 2))
    # inlet flange (port at x=0)
    parts.append(part_bm(coll, name + "_FlangeIn",
                         bm_rect_frame_x(0.0, 0.022, w + 0.082, h + 0.082,
                                         w - 0.004, h - 0.004, 0, 0),
                         GALV, 0.0015, 2))
    # identification plate
    parts.append(box(coll, name + "_Label", 0.070, 0.003, 0.030,
                     (0.28, -(h / 2 + 0.0015), 0.0), LABEL, 0.0004, 2))
    for i, xx in enumerate((0.255, 0.305)):
        parts += screw(coll, "%s_LS%d" % (name, i), (xx, -(h / 2 + 0.003), 0),
                       (0, -1, 0), r=0.0024, mat=BARE, length=0.001)
    ob = join_group(coll, name, parts)
    return ob


def duct_spool(coll, name, w, h, length=0.4):
    return duct_straight(coll, name, w, h, length, False)


def rect_elbow(coll, name, w, h, bend=0.9, angle=90.0):
    """Sweep 90 deg, starts at origin heading +X, bends +Y."""
    parts = []
    bm = bmesh.new()
    seg = 8
    rings = []
    for s in range(seg + 1):
        th = math.radians(-90.0 + angle * s / seg)
        px = bend * math.cos(th)
        py = bend + bend * math.sin(th)
        nx, ny = math.cos(th), math.sin(th)
        corners = []
        for ww, hh in ((w, h), (w - 0.008, h - 0.008)):
            ring = []
            for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                ring.append(bm.verts.new((px + nx * sx * ww / 2,
                                          py + ny * sx * ww / 2,
                                          sz * hh / 2)))
            corners.append(ring)
        rings.append(corners)
    for s in range(seg):
        for layer in (0, 1):
            r0, r1 = rings[s][layer], rings[s + 1][layer]
            for k in range(4):
                j = (k + 1) % 4
                if layer == 0:
                    bm.faces.new((r0[k], r0[j], r1[j], r1[k]))
                else:
                    bm.faces.new((r1[k], r1[j], r0[j], r0[k]))
        # end rims only at first and last
    r0o, r0i = rings[0]
    r1o, r1i = rings[-1]
    for k in range(4):
        j = (k + 1) % 4
        bm.faces.new((r0i[k], r0i[j], r0o[j], r0o[k]))
        bm.faces.new((r1o[k], r1o[j], r1i[j], r1i[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    parts.append(part_bm(coll, name + "_Body", bm, GALV, 0.0015, 2))
    # inlet flange in X
    parts.append(part_bm(coll, name + "_FlangeIn",
                         bm_rect_frame_x(0.0, 0.022, w + 0.082, h + 0.082,
                                         w - 0.004, h - 0.004, 0, 0),
                         GALV, 0.0015, 2))
    parts += flange_bolts(coll, name + "_FBI", 'X', 0.0,
                          (w + 0.082) / 2, (h + 0.082) / 2, (-1, 0, 0),
                          r=0.006, inset=0.05)
    # outlet flange facing +Y at (bend,bend)
    bm2 = bm_rect_frame_x(-0.021, 0.001, w + 0.082, h + 0.082,
                          w - 0.004, h - 0.004, 0, 0)
    bm_rot(bm2, rz=math.radians(90), loc=(bend, bend, 0))
    parts.append(part_bm(coll, name + "_FlangeOut", bm2, GALV, 0.0015, 2))
    for i, (u, v) in enumerate(((-0.45, -0.45), (0.45, -0.45),
                                (0.45, 0.45), (-0.45, 0.45),
                                (0.0, -0.5), (0.0, 0.5),
                                (-0.5, 0.0), (0.5, 0.0))):
        # on the +Y face at (bend,bend+0.023), u=X, v=Z
        parts += bolt(coll, "%s_FBO%d" % (name, i),
                      (bend + u * (w + 0.082) / 2 * 0.85, bend + 0.001,
                       v * (h + 0.082) / 2 * 0.85),
                      (0, 1, 0), r=0.006, length=0.012)
    # corner gussets
    for s in (0, 1):
        th = math.radians(-90.0 + 90.0 * s)
        gx, gy = bend * math.cos(th), bend + bend * math.sin(th)
        parts.append(box(coll, "%s_Gusset%d" % (name, s), 0.06, 0.06, 0.06,
                         (gx, gy, h / 2 + 0.03), GALV, 0.002, 2))
    ob = join_group(coll, name, parts)
    return ob, (bend, bend, 0)


def duct_tee(coll, name, w, h, main_len=1.6, branch_len=0.6):
    parts = []
    parts.append(part_bm(coll, name + "_Main",
                         bm_rect_tube_x(0.002, main_len - 0.003, w, h, 0.004, 0, 0),
                         GALV, 0.0015, 2))
    # branch towards +Y from the main side; start inside the main
    bm = bm_rect_tube_x(h / 2, branch_len - 0.003, w - 0.02, h - 0.02, 0.004, 0, 0)
    bm_rot(bm, ry=math.radians(90), loc=(main_len / 2, 0, 0))
    parts.append(part_bm(coll, name + "_Branch", bm, GALV, 0.0015, 2))
    # main flanges
    for x in (0.0, main_len):
        x0f = 0.0 if x == 0 else -0.022
        x1f = 0.022 if x == 0 else 0.0
        bm2 = bm_rect_frame_x(x0f, x1f, w + 0.082, h + 0.082,
                              w - 0.004, h - 0.004, 0, 0)
        bm_rot(bm2, loc=(x, 0, 0))
        parts.append(part_bm(coll, "%s_Flange%s" % (name, "A" if x == 0 else "B"),
                             bm2, GALV, 0.0015, 2))
        n = (-1, 0, 0) if x == 0 else (1, 0, 0)
    ob = join_group(coll, name, parts)
    return ob, (main_len / 2, branch_len, 0)


def bm_solid_loft(x0, x1, w0, h0, w1, h1, cy=0.0, cz=0.0):
    bm = bmesh.new()
    def ring(x, w, h):
        return [bm.verts.new((x, cy - w / 2, cz - h / 2)),
                bm.verts.new((x, cy + w / 2, cz - h / 2)),
                bm.verts.new((x, cy + w / 2, cz + h / 2)),
                bm.verts.new((x, cy - w / 2, cz + h / 2))]
    a, b = ring(x0, w0, h0), ring(x1, w1, h1)
    for k in range(4):
        j = (k + 1) % 4
        bm.faces.new((a[k], a[j], b[j], b[k]))
    bm.faces.new(tuple(reversed(a)))
    bm.faces.new(tuple(b))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def duct_transition(coll, name, w0, h0, w1, h1, length=0.6):
    parts = []
    parts.append(part_bm(coll, name + "_Body",
                         bm_solid_loft(0.002, length - 0.001, w0, h0, w1, h1, 0, 0),
                         GALV, 0.0015, 2))
    bm = bm_rect_frame_x(0.0, 0.022, w0 + 0.082, h0 + 0.082,
                         w0 - 0.004, h0 - 0.004, 0, 0)
    parts.append(part_bm(coll, name + "_FlangeIn", bm, GALV, 0.0015, 2))
    parts += flange_bolts(coll, name + "_FBI", 'X', 0.0,
                          (w0 + 0.082) / 2, (h0 + 0.082) / 2, (-1, 0, 0),
                          r=0.006, inset=0.05)
    bm2 = bm_rect_frame_x(-0.022, 0.0, w1 + 0.082, h1 + 0.082,
                          w1 - 0.004, h1 - 0.004, 0, 0)
    bm_rot(bm2, loc=(length, 0, 0))
    parts.append(part_bm(coll, name + "_FlangeOut", bm2, GALV, 0.0015, 2))
    parts += flange_bolts(coll, name + "_FBO", 'X', length - 0.001,
                          (w1 + 0.082) / 2, (h1 + 0.082) / 2, (1, 0, 0),
                          r=0.006, inset=0.05)
    ob = join_group(coll, name, parts)
    return ob


def duct_damper(coll, name, w, h, length=0.35):
    parts = []
    parts.append(part_bm(coll, name + "_Body",
                         bm_rect_tube_x(0.002, length - 0.003, w, h, 0.004, 0, 0),
                         GALV, 0.0015, 2))
    for x in (0.0, length):
        x0f = 0.0 if x == 0 else -0.022
        x1f = 0.022 if x == 0 else 0.0
        bm = bm_rect_frame_x(x0f, x1f, w + 0.082, h + 0.082,
                             w - 0.004, h - 0.004, 0, 0)
        bm_rot(bm, loc=(x, 0, 0))
        parts.append(part_bm(coll, "%s_Flange%s" % (name, x), bm, GALV, 0.0015, 2))
    # blade axle across the width
    parts.append(cyl(coll, name + "_Axle", 0.012, w + 0.030,
                     (length / 2, 0, h / 2 + 0.030), DARK, 'Y', 12, 0.0008, 2))
    parts.append(box(coll, name + "_Quadrant", 0.090, 0.012, 0.090,
                     (length / 2, -(h / 2 + 0.020), h / 2 + 0.030), BARE, 0.002, 2))
    parts.append(box(coll, name + "_Handle", 0.080, 0.010, 0.020,
                     (length / 2, -(h / 2 + 0.020), h / 2 + 0.060), DARK, 0.002, 2))
    parts.append(box(coll, name + "_Access", 0.180, 0.010, 0.140,
                     (length / 2, h / 2 + 0.005, 0.0), GALV, 0.0015, 3))
    for i, (sx, sz) in enumerate(((-0.070, -0.050), (0.070, -0.050),
                                  (-0.070, 0.050), (0.070, 0.050))):
        parts += screw(coll, "%s_AS%d" % (name, i),
                       (length / 2 + sx, h / 2 + 0.011, sz), (0, 1, 0),
                       r=0.003, mat=BARE, length=0.0012)
    ob = join_group(coll, name, parts)
    return ob


def grille(coll, name, w, h):
    """Wall supply grille with a 0.12 m neck along +X behind the face."""
    parts = []
    # neck and flange
    parts.append(part_bm(coll, name + "_Neck",
                         bm_rect_tube_x(0.0, 0.130, w, h, 0.003, 0, 0),
                         GALV, 0.0012, 2))
    parts.append(box(coll, name + "_BackPlate", w + 0.060, h + 0.060, 0.012,
                     (0.131, 0, 0), GALV, 0.0012, 2))
    parts.append(box(coll, name + "_FrameT", w + 0.080, 0.040, 0.030,
                     (0.125, 0, h / 2 + 0.030), ALU, 0.002, 3))
    parts.append(box(coll, name + "_FrameB", w + 0.080, 0.040, 0.030,
                     (0.125, 0, -h / 2 - 0.030), ALU, 0.002, 3))
    parts.append(box(coll, name + "_FrameL", 0.030, 0.040, h + 0.060,
                     (0.125, -w / 2 - 0.030, 0), ALU, 0.002, 3))
    parts.append(box(coll, name + "_FrameR", 0.030, 0.040, h + 0.060,
                     (0.125, w / 2 + 0.030, 0), ALU, 0.002, 3))
    # blades rotated about X to throw air sideways
    for i in range(5):
        zz = -h / 2 + 0.04 + i * (h - 0.08) / 4.0
        parts.append(box(coll, "%s_Blade%d" % (name, i), 0.014, w - 0.02, 0.045,
                         (0.135, 0, zz), ALU, 0.002, 2))
    # face plate
    parts.append(box(coll, name + "_Face", 0.020, w + 0.080, h + 0.080,
                     (0.145, 0, 0), ALU, 0.0015, 3))
    for i, (sy, sz) in enumerate(((-w / 2 - 0.03, -h / 2 - 0.03),
                                  (w / 2 + 0.03, -h / 2 - 0.03),
                                  (-w / 2 - 0.03, h / 2 + 0.03),
                                  (w / 2 + 0.03, h / 2 + 0.03))):
        parts += screw(coll, "%s_GS%d" % (name, i), (0.156, sy, sz),
                       (1, 0, 0), r=0.0034, mat=BARE, length=0.0014)
    ob = join_group(coll, name, parts)
    return ob


def duct_circular(coll, name, dia, length=2.0, spool=False):
    parts = []
    r = dia / 2
    parts.append(part_bm(coll, name + "_Body",
                         bm_pipe_x(0.0, length, r, r - 0.003, 0, 0, 24),
                         GALV, 0.001, 2))
    # coupling at the inlet
    parts.append(part_bm(coll, name + "_Coupling",
                         bm_pipe_x(-0.005, 0.065, r + 0.010, r - 0.006, 0, 0, 24),
                         GALV, 0.001, 2))
    # crimp rings
    for i, xx in enumerate((0.5, 1.0, 1.5)):
        if xx < length - 0.1:
            parts.append(part_bm(coll, "%s_Ring%d" % (name, i),
                                 bm_pipe_x(xx - 0.005, xx + 0.005, r + 0.004,
                                           r - 0.005, 0, 0, 24),
                                 GALV, 0.0006, 1))
    ob = join_group(coll, name, parts)
    return ob


def circular_elbow(coll, name, dia, bend=0.45):
    r = dia / 2
    parts = [part_bm(coll, name + "_Body",
                     bm_pipe_arc((0, 0, 0), bend, r, r - 0.003, 90, 10, 20),
                     GALV, 0.001, 2)]
    # couplings at both ports
    ob = join_group(coll, name, parts)
    return ob


def circular_tee(coll, name, dia, main_len=1.2, branch=0.5):
    r = dia / 2
    parts = [part_bm(coll, name + "_Main",
                     bm_pipe_x(0.0, main_len, r, r - 0.003, 0, 0, 20), GALV, 0.001, 2)]
    bm = bm_pipe_x(0.0, branch, r, r - 0.003, 0, 0, 20)
    bm_rot(bm, rz=math.radians(90), loc=(main_len / 2, 0, 0))
    parts.append(part_bm(coll, name + "_Branch", bm, GALV, 0.001, 2))
    for i, (sx, sy) in enumerate(((0, 0), (main_len, 0), (main_len / 2, branch))):
        bm2 = bm_pipe_x(-0.07 if i in (1, 2) else 0.0,
                        0.0 if i in (1, 2) else 0.07,
                        r + 0.010, r + 0.001, 0, 0, 20)
        if sy:
            bm_rot(bm2, rz=math.radians(90), loc=(sx, sy, 0))
        else:
            bm_rot(bm2, loc=(sx, sy, 0))
        parts.append(part_bm(coll, "%s_Coupling%d" % (name, i), bm2, GALV, 0.001, 2))
    # saddle collar
    bms = bm_pipe_x(-0.06, 0.06, r + 0.018, r + 0.004, 0, 0, 20)
    bm_rot(bms, rz=math.radians(90), loc=(main_len / 2, 0, 0))
    parts.append(part_bm(coll, name + "_Saddle", bms, GALV, 0.001, 2))
    ob = join_group(coll, name, parts)
    return ob


# ---------------------------------------------------------------------------
# cable tray
# ---------------------------------------------------------------------------

def tray_straight(coll, name, length=2.0, width=0.4, height=0.1):
    parts = []
    for sy in (-1, 1):
        yy = sy * (width / 2 - 0.002)
        parts.append(box(coll, "%s_RailT%s" % (name, "L" if sy < 0 else "R"),
                         length, 0.030, 0.008,
                         (length / 2, yy - sy * 0.015, height - 0.004),
                         GALV, 0.0008, 2))
        parts.append(box(coll, "%s_RailB%s" % (name, "L" if sy < 0 else "R"),
                         length, 0.030, 0.008,
                         (length / 2, yy - sy * 0.015, 0.008),
                         GALV, 0.0008, 2))
        parts.append(box(coll, "%s_Web%s" % (name, "L" if sy < 0 else "R"),
                         length - 0.020, 0.003, height - 0.008,
                         (length / 2, yy, height / 2), GALV, 0.0006, 1))
    # rungs
    nr = max(2, int(round(length / 0.33)))
    for i in range(nr):
        xx = 0.18 + i * (length - 0.36) / max(nr - 1, 1)
        parts.append(box(coll, "%s_Rung%d" % (name, i), 0.030, width + 0.022, 0.012,
                         (xx, 0, 0.011), GALV, 0.001, 2))
    # grounding lug
    parts.append(box(coll, name + "_GroundLug", 0.040, 0.030, 0.030,
                     (0.10, width / 2 + 0.014, 0.060), BRASS, 0.0015, 2))
    parts.append(cyl(coll, name + "_GroundBolt", 0.006, 0.030,
                     (0.10, width / 2 + 0.032, 0.060), BARE, 'Y', 6, 0.0005, 1))
    ob = join_group(coll, name, parts)
    return ob


def tray_riser(coll, name, length=1.0, width=0.4, height=0.1):
    ob = tray_straight(coll, name, length, width, height)
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.rotate(bm, cent=(0, 0, 0),
                     matrix=Matrix.Rotation(math.radians(90), 3, 'Y'),
                     verts=bm.verts[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(ob.data)
    bm.free()
    return ob


def tray_splice(coll, name, width=0.4):
    parts = []
    for sy in (-1, 1):
        yy = sy * (width / 2 + 0.004)
        parts.append(box(coll, "%s_Plate%s" % (name, "L" if sy < 0 else "R"),
                         0.140, 0.008, 0.120, (0, yy, 0.050), BARE, 0.0012, 2))
        for i, zz in enumerate((0.020, 0.050, 0.080)):
            parts += bolt(coll, "%s_B%s%d" % (name, "L" if sy < 0 else "R", i),
                          (0, yy, zz), (0, sy, 0), r=0.006, head=0.004,
                          length=0.010)
    ob = join_group(coll, name, parts)
    return ob


def tray_cover(coll, name, length=2.0, width=0.4):
    parts = []
    parts.append(box(coll, name + "_Cover", length, width + 0.060, 0.008,
                     (length / 2, 0, 0.004), GALV, 0.001, 2))
    for sy in (-1, 1):
        parts.append(box(coll, "%s_Lip%s" % (name, "L" if sy < 0 else "R"),
                         length, 0.008, 0.026,
                         (length / 2, sy * (width / 2 + 0.030), -0.009),
                         GALV, 0.001, 2))
    for i in range(5):
        xx = 0.2 + i * (length - 0.4) / 4.0
        for sy in (-1, 1):
            parts += screw(coll, "%s_CS%d_%d" % (name, i, 0 if sy < 0 else 1),
                           (xx, sy * (width / 2 + 0.020), 0.009),
                           (0, 0, 1), r=0.0032, mat=BARE, length=0.0012)
    ob = join_group(coll, name, parts)
    return ob


def pipe_straight(coll, name, dia, length=2.0, spool=False):
    r = dia / 2
    parts = [part_bm(coll, name + "_Pipe",
                     bm_pipe_x(0.0, length, r, r - 0.004, 0, 0, 20),
                     RED, 0.0008, 2)]
    # coupling at the inlet
    parts.append(part_bm(coll, name + "_Coupling",
                         bm_pipe_x(0.0, 0.080, r + 0.012, r + 0.001, 0, 0, 20),
                         RED, 0.001, 2))
    ob = join_group(coll, name, parts)
    return ob


def pipe_elbow(coll, name, dia, bend=0.45):
    r = dia / 2
    parts = [part_bm(coll, name + "_Pipe",
                     bm_pipe_arc((0, 0, 0), bend, r, r - 0.004, 90, 8, 16),
                     RED, 0.0008, 2)]
    for i, (x, y, rz) in enumerate(((0, 0, 0), (bend, bend, math.radians(90)))):
        bm = bm_pipe_x(0.0, 0.080, r + 0.012, r + 0.001, 0, 0, 16)
        bm_rot(bm, rz=rz, loc=(x, y, 0))
        parts.append(part_bm(coll, "%s_Coupling%d" % (name, i), bm, RED, 0.001, 2))
    ob = join_group(coll, name, parts)
    return ob


def sprinkler_tee(coll, name, dia=0.08, branch_dia=0.05, main_len=0.8,
                  branch_len=0.4):
    r = dia / 2
    br = branch_dia / 2
    parts = [part_bm(coll, name + "_Main",
                     bm_pipe_x(0.0, main_len, r, r - 0.004, 0, 0, 20), RED, 0.0008, 2)]
    bm = bm_pipe_x(0.0, branch_len, br, br - 0.003, 0, 0, 16)
    bm_rot(bm, ry=math.radians(90), loc=(main_len / 2, 0, 0))
    parts.append(part_bm(coll, name + "_Branch", bm, RED, 0.0008, 2))
    # weld collars + reducer at the branch outlet
    parts.append(part_bm(coll, name + "_Collar",
                         bm_pipe_x(main_len / 2 - 0.05, main_len / 2 + 0.05,
                                   r + 0.012, r + 0.001, 0, 0, 20), RED, 0.001, 2))
    parts.append(cone(coll, name + "_Reducer", br + 0.010, br + 0.002, 0.050,
                      (main_len / 2, 0, -branch_len - 0.025), RED, 'Z', 16,
                      0.0008, 2))
    ob = join_group(coll, name, parts)
    return ob


def sprinkler_head(coll, name):
    parts = []
    parts.append(cyl(coll, name + "_Nipple", 0.010, 0.040,
                     (0, 0, -0.020), BARE, 'Z', 12, 0.0005, 1))
    parts.append(cyl(coll, name + "_Hex", 0.014, 0.018,
                     (0, 0, -0.045), BRASS, 'Z', 6, 0.0008, 2))
    parts.append(box(coll, name + "_FrameBody", 0.020, 0.020, 0.030,
                     (0, 0, -0.070), BRASS, 0.002, 2))
    for sx in (-1, 1):
        parts.append(box(coll, "%s_Arm%s" % (name, "L" if sx < 0 else "R"),
                         0.006, 0.006, 0.075,
                         (sx * 0.022, 0, -0.105), BRASS, 0.0012, 2))
    parts.append(cyl(coll, name + "_Deflector", 0.034, 0.004,
                     (0, 0, -0.145), BARE, 'Z', 16, 0.0006, 1))
    for i in range(6):
        a = math.radians(i * 60)
        parts.append(box(coll, "%s_Tooth%d" % (name, i), 0.020, 0.004, 0.003,
                         (0.024 * math.cos(a), 0.024 * math.sin(a), -0.148),
                         BARE, 0.0004, 1))
    parts.append(cyl(coll, name + "_Bulb", 0.0035, 0.022,
                     (0, 0, -0.080), M["lens_red"], 'Z', 8, 0.0004, 1))
    ob = join_group(coll, name, parts)
    return ob


def sprinkler_drop(coll, name, length=0.45):
    parts = [part_bm(coll, name + "_Pipe",
                     bm_pipe_x(0.0, length, 0.025, 0.021, 0, 0, 16), RED, 0.0008, 2)]
    bm2 = bm_pipe_x(0.0, length, 0.025, 0.021, 0, 0, 16)
    bm_rot(bm2, ry=math.radians(90), loc=(0, 0, 0))
    parts = [part_bm(coll, name + "_Pipe", bm2, RED, 0.0008, 2)]
    parts.append(cyl(coll, name + "_Escutcheon", 0.055, 0.008,
                     (0, 0, 0.004), BARE, 'Z', 20, 0.001, 2))
    parts.append(cyl(coll, name + "_Bushing", 0.029, 0.040,
                     (0, 0, -length + 0.015), RED, 'Z', 16, 0.0008, 2))
    parts.append(cyl(coll, name + "_Socket", 0.017, 0.080,
                     (0, 0, -length - 0.030), BARE, 'Z', 12, 0.0006, 2))
    ob = join_group(coll, name, parts)
    return ob


def pipe_hanger(coll, name, dia=0.08, rod=1.15):
    parts = []
    # ceiling plate and rod
    parts.append(box(coll, name + "_CeilPlate", 0.080, 0.080, 0.010,
                     (0, 0, -0.005), DARK, 0.0012, 2))
    parts.append(cyl(coll, name + "_Rod", 0.0055, rod,
                     (0, 0, -rod / 2 - 0.003), BARE, 'Z', 8, 0.0004, 1))
    # clevis
    parts.append(box(coll, name + "_Clevis", 0.090, 0.010, 0.050,
                     (0, 0, -rod - 0.020), DARK, 0.0015, 2))
    for sy in (-1, 1):
        parts.append(box(coll, "%s_Jaw%s" % (name, "L" if sy < 0 else "R"),
                         0.060, 0.008, 0.160,
                         (0, sy * 0.040, -rod - 0.040), DARK, 0.0015, 2))
    parts.append(box(coll, name + "_ClampBottom", 0.080, dia + 0.020, 0.012,
                     (0, 0, -rod - dia / 2 - 0.004), DARK, 0.0012, 2))
    ob = join_group(coll, name, parts)
    return ob


def gate_valve(coll, name, dia=0.08, length=0.30):
    parts = []
    r = dia / 2
    parts.append(part_bm(coll, name + "_Body",
                         bm_pipe_x(0.0, length, r + 0.012, r + 0.001, 0, 0, 20),
                         RED, 0.001, 2))
    for x in (0.0, length):
        parts.append(part_bm(coll, "%s_Flange%s" % (name, x),
                             bm_pipe_x(x - 0.010, x + 0.010, r + 0.045,
                                       r - 0.006, 0, 0, 20), RED, 0.001, 2))
    parts.append(cyl(coll, name + "_Bonnet", 0.035, 0.080,
                     (length / 2, 0, r + 0.040), RED, 'Z', 16, 0.001, 2))
    parts.append(cyl(coll, name + "_Stem", 0.010, 0.160,
                     (length / 2, 0, r + 0.150), BARE, 'Z', 10, 0.0005, 1))
    parts.append(cyl(coll, name + "_Wheel", 0.090, 0.012,
                     (length / 2, 0, r + 0.230), DARK, 'Z', 20, 0.001, 2))
    parts.append(cyl(coll, name + "_Hub", 0.022, 0.030,
                     (length / 2, 0, r + 0.245), BARE, 'Z', 12, 0.001, 2))
    ob = join_group(coll, name, parts)
    return ob


# ---------------------------------------------------------------------------
# conduit
# ---------------------------------------------------------------------------

def conduit_straight(coll, name, dia, length=2.0, spool=False):
    r = dia / 2
    parts = [part_bm(coll, name + "_Pipe",
                     bm_pipe_x(0.0, length, r, r - 0.0015, 0, 0, 16),
                     COND, 0.0006, 2)]
    parts.append(part_bm(coll, name + "_Coupling",
                         bm_pipe_x(0.0, 0.050, r + 0.006, r + 0.001, 0, 0, 16),
                         COND, 0.0008, 1))
    ob = join_group(coll, name, parts)
    return ob


def conduit_elbow(coll, name, dia, bend=0.12):
    r = dia / 2
    parts = [part_bm(coll, name + "_Pipe",
                     bm_pipe_arc((0, 0, 0), bend, r, r - 0.0015, 90, 8, 12),
                     COND, 0.0006, 2)]
    for i, (x, y, rz) in enumerate(((0, 0, 0), (bend, bend, math.radians(90)))):
        bm = bm_pipe_x(0.0, 0.045, r + 0.006, r + 0.001, 0, 0, 12)
        bm_rot(bm, rz=rz, loc=(x, y, 0))
        parts.append(part_bm(coll, "%s_Coupling%d" % (name, i), bm, COND, 0.0008, 1))
    ob = join_group(coll, name, parts)
    return ob


def junction_box(coll, name, size=0.100, depth=0.050):
    parts = []
    parts.append(box(coll, name + "_Box", size, size, depth, (0, 0, 0),
                     COND, 0.002, 3))
    parts.append(box(coll, name + "_Cover", size * 0.92, size * 0.92, 0.006,
                     (0, 0, depth / 2 + 0.003), COND, 0.0012, 2))
    for i, (xx, yy) in enumerate(((-0.035, -0.035), (0.035, -0.035),
                                  (-0.035, 0.035), (0.035, 0.035))):
        parts += screw(coll, "%s_BS%d" % (name, i),
                       (xx, yy, depth / 2 + 0.006), (0, 0, 1),
                       r=0.0032, mat=BARE, length=0.0012)
    for i, xx in enumerate((-0.055, 0.055)):
        parts.append(box(coll, "%s_Ear%d" % (name, i), 0.020, 0.010, 0.030,
                         (xx, 0, depth / 2), COND, 0.001, 1))
    ob = join_group(coll, name, parts)
    return ob


def conduit_clamp(coll, name, dia):
    parts = []
    r = dia / 2
    # partial band (solid ring segment simplified as a full thin ring)
    parts.append(part_bm(coll, name + "_Band",
                         bm_pipe_x(-0.008, 0.008, r + 0.006, r + 0.001, 0, 0, 12),
                         COND, 0.0006, 1))
    parts.append(box(coll, name + "_Foot", 0.030, 0.026, 0.030,
                     (0, -r - 0.016, 0), COND, 0.0015, 2))
    parts += screw(coll, name + "_Screw", (0.014, -r - 0.016, 0.010), (0, 0, 1),
                   r=0.003, mat=BARE, length=0.0012)
    ob = join_group(coll, name, parts)
    return ob


# ---------------------------------------------------------------------------
# sleeves / firestop / shaft
# ---------------------------------------------------------------------------

def pipe_sleeve(coll, name, pipe_dia=0.08, sleeve_od=0.15, length=0.30):
    parts = []
    ri = sleeve_od / 2 - 0.005
    ro = sleeve_od / 2
    parts.append(part_bm(coll, name + "_Sleeve",
                         bm_pipe_x(-length / 2, length / 2, ro, ri, 0, 0, 20),
                         GALV, 0.001, 2))
    for sx in (-1, 1):
        parts.append(part_bm(coll, "%s_Esc%s" % (name, "L" if sx < 0 else "R"),
                             bm_pipe_x(sx * (length / 2 + 0.002) - 0.004,
                                       sx * (length / 2 + 0.002) + 0.004,
                                       ro + 0.050, ri + 0.005, 0, 0, 20),
                             BARE, 0.0012, 2))
        for i, (u, v) in enumerate(((0.060, 0.0), (-0.060, 0.0),
                                    (0.0, 0.060), (0.0, -0.060))):
            parts += bolt(coll, "%s_EB%d_%d" % (name, 0 if sx < 0 else 1, i),
                          (sx * (length / 2 + 0.007), u, v), (sx, 0, 0),
                          r=0.005, head=0.004, length=0.010)
    # intumescent firestop ring around the pipe
    parts.append(part_bm(coll, name + "_Firestop",
                         bm_pipe_x(-0.025, 0.025, ri + 0.002, pipe_dia / 2 - 0.002,
                                   0, 0, 20), FIRESTOP, 0.001, 2))
    parts.append(box(coll, name + "_Label", 0.060, 0.020, 0.040,
                     (0, ro - 0.004, 0), LABEL, 0.001, 2))
    ob = join_group(coll, name, parts)
    return ob


def rect_sleeve(coll, name, w=0.8, h=0.6, length=0.30):
    parts = []
    parts.append(part_bm(coll, name + "_Sleeve",
                         bm_rect_tube_x(-length / 2, length / 2,
                                        w + 0.10, h + 0.10, 0.006, 0, 0),
                         GALV, 0.0015, 2))
    parts.append(part_bm(coll, name + "_Firestop",
                         bm_rect_frame_x(-0.025, 0.025, w + 0.092, h + 0.092,
                                         w - 0.020, h - 0.020, 0, 0),
                         FIRESTOP, 0.0012, 2))
    ob = join_group(coll, name, parts)
    return ob


def tray_sleeve(coll, name, width=0.4, height=0.1, length=0.30):
    parts = []
    parts.append(part_bm(coll, name + "_Sleeve",
                         bm_rect_tube_x(-length / 2, length / 2,
                                        width + 0.14, height + 0.14, 0.005, 0, 0.05),
                         GALV, 0.0012, 2))
    parts.append(part_bm(coll, name + "_Firestop",
                         bm_rect_frame_x(-0.020, 0.020, width + 0.132, height + 0.132,
                                         width - 0.010, height - 0.010, 0, 0.05),
                         FIRESTOP, 0.001, 2))
    ob = join_group(coll, name, parts)
    return ob


def firestop_collar(coll, name, dia=0.08, length=0.12):
    parts = []
    parts.append(part_bm(coll, name + "_Collar",
                         bm_pipe_x(-length / 2, length / 2, 0.115,
                                   0.045, 0, 0, 20), FIRESTOP, 0.001, 2))
    for sy in (-1, 1):
        parts.append(box(coll, "%s_Latch%s" % (name, "L" if sy < 0 else "R"),
                         0.040, 0.010, 0.060,
                         (0, sy * 0.120, 0), BARE, 0.0012, 2))
        parts += bolt(coll, "%s_LB%s" % (name, "L" if sy < 0 else "R"),
                      (0, sy * 0.125, 0), (0, sy, 0), r=0.005,
                      head=0.004, length=0.010)
    ob = join_group(coll, name, parts)
    return ob


def fire_damper(coll, name, w=0.8, h=0.6, length=0.35):
    parts = []
    parts.append(part_bm(coll, name + "_Body",
                         bm_rect_tube_x(0.002, length, w, h, 0.005, 0, 0),
                         GALV, 0.0015, 2))
    for x in (0.0, length):
        x0f = 0.0 if x == 0 else -0.022
        x1f = 0.022 if x == 0 else 0.0
        bm = bm_rect_frame_x(x0f, x1f, w + 0.082, h + 0.082,
                             w - 0.004, h - 0.004, 0, 0)
        bm_rot(bm, loc=(x, 0, 0))
        parts.append(part_bm(coll, "%s_Flange%s" % (name, x), bm, GALV, 0.0015, 2))
    parts.append(box(coll, name + "_Access", 0.220, 0.012, 0.160,
                     (length / 2, h / 2 + 0.006, 0), GALV, 0.0015, 3))
    for i, (sx, sz) in enumerate(((-0.090, -0.060), (0.090, -0.060),
                                  (-0.090, 0.060), (0.090, 0.060))):
        parts += screw(coll, "%s_AS%d" % (name, i),
                       (length / 2 + sx, h / 2 + 0.013, sz), (0, 1, 0),
                       r=0.0032, mat=BARE, length=0.0012)
    parts.append(box(coll, name + "_Actuator", 0.140, 0.100, 0.090,
                     (length / 2, -(h / 2 + 0.060), 0.0), DARK, 0.002, 3))
    parts.append(cyl(coll, name + "_Indicator", 0.010, 0.030,
                     (length / 2, -(h / 2 + 0.115), 0.0), ORANGE, 'Y', 12,
                     0.0006, 2))
    parts.append(box(coll, name + "_Label", 0.090, 0.003, 0.040,
                     (length / 2, -(h / 2 + 0.112), 0.0), LABEL, 0.0005, 2))
    ob = join_group(coll, name, parts)
    return ob


def shaft_panel(coll, name):
    parts = []
    # frame and door, mounted on a wall plane y=0; door opens about the left
    parts.append(box(coll, name + "_FrameT", 0.680, 0.030, 0.040,
                     (0, 0.015, 1.260), GALV, 0.002, 3))
    parts.append(box(coll, name + "_FrameB", 0.680, 0.030, 0.040,
                     (0, 0.015, -0.020), GALV, 0.002, 3))
    parts.append(box(coll, name + "_FrameL", 0.040, 0.034, 1.300,
                     (-0.330, 0.015, 0.610), GALV, 0.002, 3))
    parts.append(box(coll, name + "_FrameR", 0.040, 0.034, 1.300,
                     (0.330, 0.015, 0.610), GALV, 0.002, 3))
    parts.append(box(coll, name + "_Door", 0.620, 0.020, 1.240,
                     (0, 0.020, 0.620), GALV, 0.002, 3))
    # hinges / lock / label
    ob = join_group(coll, name, parts)
    return ob


# ---------------------------------------------------------------------------
# supports
# ---------------------------------------------------------------------------

def support_trapeze(coll, name, width, rod=1.35, strut_z=None):
    """Ceiling trapeze for a duct of `width`; origin at the ceiling."""
    parts = []
    if strut_z is None:
        strut_z = -rod
    for sy in (-1, 1):
        yy = sy * (width / 2 + 0.12)
        parts.append(box(coll, "%s_CeilPlate%s" % (name, "L" if sy < 0 else "R"),
                         0.100, 0.100, 0.010, (0, yy, -0.005), DARK, 0.0012, 2))
        parts.append(cyl(coll, "%s_Rod%s" % (name, "L" if sy < 0 else "R"),
                         0.006, rod, (0, yy, -rod / 2 - 0.003), BARE, 'Z', 8,
                         0.0004, 1))
    parts.append(box(coll, name + "_Strut", 0.045, width + 0.32, 0.045,
                     (0, 0, strut_z - 0.022), DARK, 0.002, 3))
    for sy in (-1, 1):
        parts.append(box(coll, "%s_Clamp%s" % (name, "L" if sy < 0 else "R"),
                         0.060, 0.030, 0.160,
                         (0, sy * (width / 2 + 0.020), strut_z + 0.060),
                         DARK, 0.002, 2))
        parts.append(box(coll, "%s_Pad%s" % (name, "L" if sy < 0 else "R"),
                         0.050, 0.010, 0.120,
                         (0, sy * (width / 2 + 0.004), strut_z + 0.060),
                         RUB, 0.001, 1))
    ob = join_group(coll, name, parts)
    return ob


def support_tray(coll, name, width=0.4, rod=0.95):
    parts = []
    for sy in (-1, 1):
        yy = sy * (width / 2 + 0.12)
        parts.append(box(coll, "%s_CeilPlate%s" % (name, "L" if sy < 0 else "R"),
                         0.100, 0.100, 0.010, (0, yy, -0.005), DARK, 0.0012, 2))
        parts.append(cyl(coll, "%s_Rod%s" % (name, "L" if sy < 0 else "R"),
                         0.006, rod, (0, yy, -rod / 2 - 0.003), BARE, 'Z', 8, 0.0004, 1))
    parts.append(box(coll, name + "_Strut", 0.041, width + 0.30, 0.041,
                     (0, 0, -rod - 0.020), DARK, 0.002, 3))
    for sy in (-1, 1):
        parts.append(box(coll, "%s_Clamp%s" % (name, "L" if sy < 0 else "R"),
                         0.050, 0.025, 0.060,
                         (0, sy * (width / 2 + 0.015), -rod + 0.020), DARK,
                         0.0015, 2))
        parts.append(box(coll, "%s_Pad%s" % (name, "L" if sy < 0 else "R"),
                         0.040, 0.008, 0.030,
                         (0, sy * (width / 2 + 0.002), -rod + 0.020), RUB,
                         0.0008, 1))
    ob = join_group(coll, name, parts)
    return ob


def support_conduit(coll, name, dia=0.025, rod=1.6):
    parts = []
    for sy in (-1, 1):
        yy = sy * 0.15
        parts.append(box(coll, "%s_CeilPlate%s" % (name, "L" if sy < 0 else "R"),
                         0.090, 0.090, 0.010, (0, yy, -0.005), DARK, 0.0012, 2))
        parts.append(cyl(coll, "%s_Rod%s" % (name, "L" if sy < 0 else "R"),
                         0.005, rod, (0, yy, -rod / 2 - 0.003), BARE, 'Z', 8, 0.0004, 1))
    parts.append(box(coll, name + "_Strut", 0.041, 0.44, 0.041,
                     (0, 0, -rod - 0.020), DARK, 0.002, 3))
    for i, yy in enumerate((-0.12, 0.0, 0.12)):
        parts.append(box(coll, "%s_Foot%d" % (name, i), 0.030, 0.030, 0.026,
                         (0.0, yy, -rod - 0.005), COND, 0.0012, 2))
        for sy in (-1, 1):
            parts.append(box(coll, "%s_Jaw%d_%d" % (name, i, 0 if sy < 0 else 1),
                             0.050, 0.008, 0.050,
                             (0.0, yy + sy * (dia / 2 + 0.004), -rod + 0.020),
                             COND, 0.0008, 1))
        parts.append(box(coll, "%s_Saddle%d" % (name, i), 0.050, 0.060, 0.008,
                         (0.0, yy, -rod - 0.010), COND, 0.0008, 1))
    ob = join_group(coll, name, parts)
    return ob


# ---------------------------------------------------------------------------
# builders
# ---------------------------------------------------------------------------

def build_all():
    if bpy.data.collections.get("SERVICES"):
        clear_collection_tree("SERVICES")
    T = ensure_tree()
    coll = bpy.data.collections["SERVICES"]
    out = []
    specs = []

    def add(name, ob_pos, loc, meta):
        def first_obj(v):
            if hasattr(v, "type"):
                return v
            if isinstance(v, (tuple, list)):
                return first_obj(v[0])
            return v
        ob = first_obj(ob_pos)
        if ob.type == 'MESH' and not ob.data.uv_layers:
            from fm_shared_p0_lib import smart_uv
            smart_uv(ob)
        root = make_root(name + "_ROOT", coll)
        parent_to(ob, root)
        finalize_master(root, coll, [ob], loc, meta)
        out.append(root)

    # HVAC main
    add("SM_SH_HVAC_RECT800x600_L2000",
        (duct_straight(coll, "SM_SH_HVAC_RECT800x600_L2000", 0.8, 0.6, 2.0, True), (2.0, 0, 0)),
        (0, 0, 0.30), {"fm_class": "SERVICE", "fm_family": "HVAC",
                       "fm_section": "0.80 x 0.60 m", "fm_length": 2.0,
                       "fm_ports": json.dumps({"in": [0, 0, 0], "out": [2.0, 0, 0],
                                               "section": "0.80x0.60"})})
    add("SM_SH_HVAC_RECT800x600_PEN400",
        (duct_spool(coll, "SM_SH_HVAC_RECT800x600_PEN400", 0.8, 0.6, 0.4), (0.4, 0, 0)),
        (2.6, 0, 0.30), {"fm_class": "SERVICE", "fm_family": "HVAC",
                         "fm_section": "0.80 x 0.60 m", "fm_length": 0.4,
                         "fm_ports": json.dumps({"in": [0, 0, 0], "out": [0.4, 0, 0],
                                                 "section": "0.80x0.60"})})
    add("SM_SH_HVAC_RECT600x400_L2000",
        (duct_straight(coll, "SM_SH_HVAC_RECT600x400_L2000", 0.6, 0.4, 2.0, False), (2.0, 0, 0)),
        (3.4, 0, 0.20), {"fm_class": "SERVICE", "fm_family": "HVAC",
                         "fm_section": "0.60 x 0.40 m", "fm_length": 2.0,
                         "fm_ports": json.dumps({"in": [0, 0, 0], "out": [2.0, 0, 0],
                                                 "section": "0.60x0.40"})})
    add("SM_SH_HVAC_RECT600x400_PEN400",
        (duct_spool(coll, "SM_SH_HVAC_RECT600x400_PEN400", 0.6, 0.4, 0.4), (0.4, 0, 0)),
        (5.8, 0, 0.20), {"fm_class": "SERVICE", "fm_family": "HVAC",
                         "fm_section": "0.60 x 0.40 m", "fm_length": 0.4,
                         "fm_ports": json.dumps({"in": [0, 0, 0], "out": [0.4, 0, 0],
                                                 "section": "0.60x0.40"})})
    add("SM_SH_HVAC_ELBOW_800x600",
        (rect_elbow(coll, "SM_SH_HVAC_ELBOW_800x600", 0.8, 0.6, 0.9), (0.9, 0.9, 0)),
        (0, 2.0, 0.30), {"fm_class": "SERVICE", "fm_family": "HVAC",
                         "fm_section": "0.80 x 0.60 m", "fm_bend_radius": 0.9,
                         "fm_ports": json.dumps({"in": [0, 0, 0], "out": [0.9, 0.9, 0],
                                                 "section": "0.80x0.60"})})
    add("SM_SH_HVAC_TEE_800x600",
        (duct_tee(coll, "SM_SH_HVAC_TEE_800x600", 0.8, 0.6), (1.6, 0.6, 0)),
        (3.0, 2.0, 0.30), {"fm_class": "SERVICE", "fm_family": "HVAC",
                           "fm_section": "0.80 x 0.60 m",
                           "fm_ports": json.dumps({"in": [0, 0, 0], "out": [1.6, 0, 0],
                                                   "branch": [0.8, 0, -0.6],
                                                   "section": "0.80x0.60"})})
    add("SM_SH_HVAC_TRANS_800x600_600x400",
        (duct_transition(coll, "SM_SH_HVAC_TRANS_800x600_600x400", 0.8, 0.6, 0.6, 0.4, 0.6), (0.6, 0, 0)),
        (6.0, 2.0, 0.30), {"fm_class": "SERVICE", "fm_family": "HVAC",
                           "fm_ports": json.dumps({"in": [0, 0, 0], "out": [0.6, 0, 0],
                                                   "section_in": "0.80x0.60",
                                                   "section_out": "0.60x0.40"})})
    add("SM_SH_HVAC_DAMPER_800x600",
        (duct_damper(coll, "SM_SH_HVAC_DAMPER_800x600", 0.8, 0.6), (0.35, 0, 0)),
        (8.5, 2.0, 0.30), {"fm_class": "SERVICE", "fm_family": "HVAC",
                           "fm_ports": json.dumps({"in": [0, 0, 0], "out": [0.35, 0, 0],
                                                   "section": "0.80x0.60"})})
    add("SM_SH_HVAC_GRILLE_600x400",
        (grille(coll, "SM_SH_HVAC_GRILLE_600x400", 0.6, 0.4), (0.12, 0, 0)),
        (10.2, 2.0, 0.30), {"fm_class": "SERVICE", "fm_family": "HVAC",
                            "fm_ports": json.dumps({"in": [0, 0, 0],
                                                    "section": "0.60x0.40"})})
    add("SM_SH_HVAC_ROUND_300_L2000",
        (duct_circular(coll, "SM_SH_HVAC_ROUND_300_L2000", 0.3, 2.0), (2.0, 0, 0)),
        (0, 4.0, 0.15), {"fm_class": "SERVICE", "fm_family": "HVAC",
                         "fm_section": "circular 0.30 m", "fm_ports": json.dumps(
                             {"in": [0, 0, 0], "out": [2.0, 0, 0], "section": "round 0.30"})})
    add("SM_SH_HVAC_ROUND_300_ELBOW",
        (circular_elbow(coll, "SM_SH_HVAC_ROUND_300_ELBOW", 0.3, 0.45), (0.45, 0.45, 0)),
        (2.6, 4.0, 0.15), {"fm_class": "SERVICE", "fm_family": "HVAC",
                           "fm_ports": json.dumps({"in": [0, 0, 0], "out": [0.45, 0.45, 0],
                                                   "section": "round 0.30"})})
    add("SM_SH_HVAC_ROUND_300_TEE",
        (circular_tee(coll, "SM_SH_HVAC_ROUND_300_TEE", 0.3), (1.2, 0.5, 0)),
        (3.6, 4.0, 0.15), {"fm_class": "SERVICE", "fm_family": "HVAC",
                           "fm_ports": json.dumps({"in": [0, 0, 0], "out": [1.2, 0, 0],
                                                   "branch": [0.6, 0.5, 0],
                                                   "section": "round 0.30"})})

    # tray
    add("SM_SH_TRAY_400_L2000",
        (tray_straight(coll, "SM_SH_TRAY_400_L2000", 2.0, 0.4, 0.1), (2.0, 0, 0)),
        (0, 6.0, 0.0), {"fm_class": "SERVICE", "fm_family": "TRAY",
                        "fm_section": "0.40 x 0.10 m", "fm_ports": json.dumps(
                            {"in": [0, 0, 0], "out": [2.0, 0, 0], "section": "0.40x0.10"})})
    add("SM_SH_TRAY_400_PEN400",
        (tray_straight(coll, "SM_SH_TRAY_400_PEN400", 0.4, 0.4, 0.1), (0.4, 0, 0)),
        (2.6, 6.0, 0.0), {"fm_class": "SERVICE", "fm_family": "TRAY",
                          "fm_section": "0.40 x 0.10 m", "fm_length": 0.4,
                          "fm_ports": json.dumps({"in": [0, 0, 0], "out": [0.4, 0, 0],
                                                  "section": "0.40x0.10"})})
    add("SM_SH_TRAY_400_RISER_L1000",
        (tray_riser(coll, "SM_SH_TRAY_400_RISER_L1000", 1.0, 0.4, 0.1), (0, 0, -1.0)),
        (3.4, 6.0, 1.0), {"fm_class": "SERVICE", "fm_family": "TRAY",
                          "fm_section": "0.40 x 0.10 m", "fm_length": 1.0,
                          "fm_ports": json.dumps({"in": [0, 0, 0], "out": [0, 0, -1.0],
                                                  "section": "0.40x0.10"})})
    add("SM_SH_TRAY_400_SPLICE",
        (tray_splice(coll, "SM_SH_TRAY_400_SPLICE", 0.4), (0, 0, 0)),
        (4.2, 6.0, 0.05), {"fm_class": "SERVICE", "fm_family": "TRAY",
                           "fm_note": "join at module port; 6 bolts"})
    add("SM_SH_TRAY_400_COVER_L2000",
        (tray_cover(coll, "SM_SH_TRAY_400_COVER_L2000", 2.0, 0.4), (2.0, 0, 0)),
        (5.0, 6.0, 0.0), {"fm_class": "SERVICE", "fm_family": "TRAY",
                          "fm_ports": json.dumps({"in": [0, 0, 0], "out": [2.0, 0, 0],
                                                  "section": "0.40 cover"})})

    # sprinklers
    add("SM_SH_SPRINK_PIPE_80_L2000",
        (pipe_straight(coll, "SM_SH_SPRINK_PIPE_80_L2000", 0.08, 2.0), (2.0, 0, 0)),
        (0, 8.0, 0.0), {"fm_class": "SERVICE", "fm_family": "SPRINKLER",
                        "fm_section": "DN80", "fm_ports": json.dumps(
                            {"in": [0, 0, 0], "out": [2.0, 0, 0], "section": "DN80"})})
    add("SM_SH_SPRINK_PIPE_80_PEN400",
        (pipe_straight(coll, "SM_SH_SPRINK_PIPE_80_PEN400", 0.08, 0.4), (0.4, 0, 0)),
        (2.6, 8.0, 0.0), {"fm_class": "SERVICE", "fm_family": "SPRINKLER",
                          "fm_section": "DN80", "fm_length": 0.4,
                          "fm_ports": json.dumps({"in": [0, 0, 0], "out": [0.4, 0, 0],
                                                  "section": "DN80"})})
    add("SM_SH_SPRINK_PIPE_50_L2000",
        (pipe_straight(coll, "SM_SH_SPRINK_PIPE_50_L2000", 0.05, 2.0), (2.0, 0, 0)),
        (3.4, 8.0, 0.0), {"fm_class": "SERVICE", "fm_family": "SPRINKLER",
                          "fm_section": "DN50", "fm_ports": json.dumps(
                              {"in": [0, 0, 0], "out": [2.0, 0, 0], "section": "DN50"})})
    add("SM_SH_SPRINK_ELBOW_80",
        (pipe_elbow(coll, "SM_SH_SPRINK_ELBOW_80", 0.08, 0.45), (0.45, 0.45, 0)),
        (5.8, 8.0, 0.0), {"fm_class": "SERVICE", "fm_family": "SPRINKLER",
                          "fm_section": "DN80", "fm_ports": json.dumps(
                              {"in": [0, 0, 0], "out": [0.45, 0.45, 0], "section": "DN80"})})
    add("SM_SH_SPRINK_TEE_80_50",
        (sprinkler_tee(coll, "SM_SH_SPRINK_TEE_80_50", 0.08, 0.05, 0.8, 0.4), (0.8, 0, -0.4)),
        (0, 10.0, 0.0), {"fm_class": "SERVICE", "fm_family": "SPRINKLER",
                         "fm_ports": json.dumps({"in": [0, 0, 0], "out": [0.8, 0, 0],
                                                 "branch": [0.4, 0, -0.4],
                                                 "section": "DN80 / DN50"})})
    add("SM_SH_SPRINK_DROP_50",
        (sprinkler_drop(coll, "SM_SH_SPRINK_DROP_50", 0.45), (0, 0, -0.45)),
        (2.2, 10.0, 0.0), {"fm_class": "SERVICE", "fm_family": "SPRINKLER",
                           "fm_ports": json.dumps({"in": [0, 0, 0], "out": [0, 0, -0.45],
                                                   "section": "DN50"})})
    add("SM_SH_SPRINK_HEAD",
        (sprinkler_head(coll, "SM_SH_SPRINK_HEAD"), (0, 0, -0.16)),
        (3.4, 10.0, 0.0), {"fm_class": "SERVICE", "fm_family": "SPRINKLER",
                           "fm_note": "pendent head; thread top at z=0"})
    add("SM_SH_SPRINK_VALVE_80",
        (gate_valve(coll, "SM_SH_SPRINK_VALVE_80", 0.08, 0.30), (0.3, 0, 0)),
        (4.6, 10.0, 0.0), {"fm_class": "SERVICE", "fm_family": "SPRINKLER",
                           "fm_ports": json.dumps({"in": [0, 0, 0], "out": [0.3, 0, 0],
                                                   "section": "DN80"})})
    add("SM_SH_SPRINK_REDUCER_80_50",
        (cone(coll, "SM_SH_SPRINK_REDUCER_80_50", 0.04, 0.025, 0.16,
              (0.08, 0, 0), RED, 'X', 20, 0.001, 2), (0.16, 0, 0)),
        (6.0, 10.0, 0.0), {"fm_class": "SERVICE", "fm_family": "SPRINKLER",
                           "fm_ports": json.dumps({"in": [0, 0, 0], "out": [0.16, 0, 0],
                                                   "section_in": "DN80",
                                                   "section_out": "DN50"})})

    # conduit
    add("SM_SH_CONDUIT_25_L2000",
        (conduit_straight(coll, "SM_SH_CONDUIT_25_L2000", 0.025, 2.0), (2.0, 0, 0)),
        (0, 12.0, 0.0), {"fm_class": "SERVICE", "fm_family": "CONDUIT",
                         "fm_section": "25 mm", "fm_ports": json.dumps(
                             {"in": [0, 0, 0], "out": [2.0, 0, 0], "section": "25mm"})})
    add("SM_SH_CONDUIT_25_PEN400",
        (conduit_straight(coll, "SM_SH_CONDUIT_25_PEN400", 0.025, 0.4), (0.4, 0, 0)),
        (2.6, 12.0, 0.0), {"fm_class": "SERVICE", "fm_family": "CONDUIT",
                           "fm_section": "25 mm", "fm_length": 0.4,
                           "fm_ports": json.dumps({"in": [0, 0, 0], "out": [0.4, 0, 0],
                                                   "section": "25mm"})})
    add("SM_SH_CONDUIT_25_ELBOW",
        (conduit_elbow(coll, "SM_SH_CONDUIT_25_ELBOW", 0.025, 0.12), (0.12, 0.12, 0)),
        (3.4, 12.0, 0.0), {"fm_class": "SERVICE", "fm_family": "CONDUIT",
                           "fm_ports": json.dumps({"in": [0, 0, 0], "out": [0.12, 0.12, 0],
                                                   "section": "25mm"})})
    add("SM_SH_CONDUIT_BOX_100",
        (junction_box(coll, "SM_SH_CONDUIT_BOX_100", 0.10, 0.05), (0, 0, 0)),
        (4.2, 12.0, 0.0), {"fm_class": "SERVICE", "fm_family": "CONDUIT",
                           "fm_note": "100 x 100 x 50 mm junction box"})
    add("SM_SH_CONDUIT_CLAMP_25",
        (conduit_clamp(coll, "SM_SH_CONDUIT_CLAMP_25", 0.025), (0, 0, 0)),
        (5.0, 12.0, 0.0), {"fm_class": "SERVICE", "fm_family": "CONDUIT"})
    add("SM_SH_CONDUIT_40_L2000",
        (conduit_straight(coll, "SM_SH_CONDUIT_40_L2000", 0.04, 2.0), (2.0, 0, 0)),
        (5.8, 12.0, 0.0), {"fm_class": "SERVICE", "fm_family": "CONDUIT",
                           "fm_section": "40 mm", "fm_ports": json.dumps(
                               {"in": [0, 0, 0], "out": [2.0, 0, 0], "section": "40mm"})})
    add("SM_SH_CONDUIT_BOX_120",
        (junction_box(coll, "SM_SH_CONDUIT_BOX_120", 0.12, 0.06), (0, 0, 0)),
        (8.2, 12.0, 0.0), {"fm_class": "SERVICE", "fm_family": "CONDUIT",
                           "fm_note": "120 x 120 x 60 mm junction box"})

    # sleeves / firestop
    add("SM_SH_SLEEVE_PIPE_80",
        (pipe_sleeve(coll, "SM_SH_SLEEVE_PIPE_80", 0.08, 0.15, 0.30), (0, 0, 0)),
        (0, 14.0, 0.0), {"fm_class": "SERVICE", "fm_family": "SLEEVE",
                         "fm_note": "DN80 sleeve + intumescent firestop + escutcheons"})
    add("SM_SH_SLEEVE_RECT_800x600",
        (rect_sleeve(coll, "SM_SH_SLEEVE_RECT_800x600", 0.8, 0.6, 0.30), (0, 0, 0)),
        (1.8, 14.0, 0.0), {"fm_class": "SERVICE", "fm_family": "SLEEVE",
                           "fm_note": "rectangular sleeve + firestop board ring"})
    add("SM_SH_SLEEVE_TRAY_400",
        (tray_sleeve(coll, "SM_SH_SLEEVE_TRAY_400", 0.4, 0.1, 0.30), (0, 0, 0)),
        (3.6, 14.0, 0.0), {"fm_class": "SERVICE", "fm_family": "SLEEVE",
                           "fm_note": "tray sleeve + firestop gasket"})
    add("SM_SH_FIRESTOP_COLLAR_80",
        (firestop_collar(coll, "SM_SH_FIRESTOP_COLLAR_80", 0.08, 0.12), (0, 0, 0)),
        (5.4, 14.0, 0.0), {"fm_class": "SERVICE", "fm_family": "FIRESTOP"})
    add("SM_SH_FIREDAMPER_800x600",
        (fire_damper(coll, "SM_SH_FIREDAMPER_800x600", 0.8, 0.6, 0.35), (0.35, 0, 0)),
        (6.8, 14.0, 0.0), {"fm_class": "SERVICE", "fm_family": "FIRESTOP",
                           "fm_ports": json.dumps({"in": [0, 0, 0], "out": [0.35, 0, 0],
                                                   "section": "0.80x0.60"})})
    add("SM_SH_SHAFT_ACCESS_600x1200",
        (shaft_panel(coll, "SM_SH_SHAFT_ACCESS_600x1200"), (0, 0, 0)),
        (9.0, 14.0, 0.0), {"fm_class": "SERVICE", "fm_family": "SHAFT",
                           "fm_note": "600 x 1200 access panel, wall plane y=0"})

    # supports
    add("SM_SH_SUPPORT_TRAPEZE_800",
        (support_trapeze(coll, "SM_SH_SUPPORT_TRAPEZE_800", 0.8, 1.60), (0, 0, -1.60)),
        (0, 16.0, 1.60), {"fm_class": "SERVICE", "fm_family": "SUPPORT",
                          "fm_note": "ceiling trapeze for 800 duct; origin at ceiling, strut at z=-1.60"})
    add("SM_SH_SUPPORT_TRAPEZE_600",
        (support_trapeze(coll, "SM_SH_SUPPORT_TRAPEZE_600", 0.6, 1.20), (0, 0, -1.20)),
        (2.4, 16.0, 1.20), {"fm_class": "SERVICE", "fm_family": "SUPPORT",
                            "fm_note": "ceiling trapeze for 600 duct; strut at z=-1.20"})
    add("SM_SH_SUPPORT_TRAY_400",
        (support_tray(coll, "SM_SH_SUPPORT_TRAY_400", 0.4, 0.95), (0, 0, -0.95)),
        (4.6, 16.0, 0.95), {"fm_class": "SERVICE", "fm_family": "SUPPORT",
                            "fm_note": "ceiling trapeze for 400 tray; seat at z=-0.95"})
    add("SM_SH_SUPPORT_PIPE_80",
        (pipe_hanger(coll, "SM_SH_SUPPORT_PIPE_80", 0.08, 1.15), (0, 0, -1.15)),
        (6.6, 16.0, 1.15), {"fm_class": "SERVICE", "fm_family": "SUPPORT",
                            "fm_note": "clevis hanger DN80; pipe centre z=-1.15"})
    add("SM_SH_SUPPORT_CONDUIT_25",
        (support_conduit(coll, "SM_SH_SUPPORT_CONDUIT_25", 0.025, 1.60), (0, 0, -1.60)),
        (8.8, 16.0, 1.60), {"fm_class": "SERVICE", "fm_family": "SUPPORT",
                            "fm_note": "conduit trapeze; conduit centre z=-1.60"})

    for r in out:
        meshes = [o for o in bpy.data.objects if o.parent == r and o.type == 'MESH']
        print("MASTER", r.name, "loc", tuple(round(v, 2) for v in r.location),
              "tris", sum(tri_count(o) for o in meshes))
    return out


if __name__ == "__main__":
    build_all()
