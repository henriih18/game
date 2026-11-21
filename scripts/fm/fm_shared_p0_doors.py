"""
FRECUENCIA MUERTA - P0a DOORS masters.

Conventions (metres, Z up):
  frame root origin = centre of the clear opening at finished floor level.
  leaf object origin = hinge axis; leaf geometry is built 0..width on +X and
  is mirrored for right-hand leaves without using a negative object scale.
  y = wall thickness axis; door faces are y +/-.
"""
import bpy
import bmesh
import math
import json
from mathutils import Vector

from fm_shared_p0_lib import (ensure_tree, ensure_materials, make_root,
                              parent_to, box, cyl, cone, screw, bolt,
                              join_group, finalize_master, smart_uv, tri_count,
                              make_part, bm_box, bm_cyl, bm_rect_frame_x,
                              frame_x)

M = ensure_materials()
T = ensure_tree()
COLL = T["doors"]

# door face material assignments
PAINT = M["paint_door"]
GALV = M["galv"]
DARK = M["steel_dark"]
BARE = M["steel_bare"]
ALU = M["aluminum"]
RUB = M["rubber"]
GLASS = M["glass"]
BRASS = M["brass"]
LABEL = M["label"]


# ---------------------------------------------------------------------------
# shared hardware
# ---------------------------------------------------------------------------

def hinge_frame(coll, prefix, hx, z, inward):
    """Frame-side hinge plate on the jamb face, embedded 1 mm and proud 5 mm."""
    parts = []
    xc = hx + 0.007 * inward
    parts.append(box(coll, prefix + "_Plate", 0.006, 0.090, 0.110,
                     (xc, 0.0, z), DARK, 0.0012, 3))
    nx = (1 * inward, 0, 0)
    for i, dz in enumerate((-0.032, 0.032)):
        parts += screw(coll, "%s_SCR%d" % (prefix, i),
                       (hx + 0.010 * inward, -0.030, z + dz),
                       nx, r=0.0042, mat=BARE, length=0.002)
        parts += screw(coll, "%s_SCRB%d" % (prefix, i),
                       (hx + 0.010 * inward, 0.030, z + dz),
                       nx, r=0.0042, mat=BARE, length=0.002)
    return parts


def hinge_leaf(coll, prefix, z):
    """Leaf-side hinge: plate on the pull face, knuckle on the hinge axis,
    pin caps and screws.  Leaf local origin is the hinge axis."""
    parts = []
    parts.append(box(coll, prefix + "_Plate", 0.045, 0.006, 0.110,
                     (0.024, -0.034, z), DARK, 0.0012, 3))
    parts.append(cyl(coll, prefix + "_Knuckle", 0.0115, 0.120,
                     (0.0, 0.0, z), DARK, 'Z', 16, 0.0012, 3))
    for i, dz in enumerate((-0.037, 0.037)):
        parts.append(cyl(coll, prefix + "_Ring%d" % i, 0.0150, 0.005,
                         (0.0, 0.0, z + dz), BARE, 'Z', 16, 0.0004, 2))
    for i, dz in enumerate((-0.040, 0.040)):
        parts.append(cyl(coll, prefix + "_Cap%d" % i, 0.007, 0.006,
                         (0.0, 0.0, z + dz), BARE, 'Z', 8, 0.0008, 2))
    for i, (xx, zz) in enumerate(((0.018, -0.032), (0.018, 0.032),
                                  (0.038, 0.0))):
        parts += screw(coll, "%s_SCRL%d" % (prefix, i),
                       (xx, -0.037, z + zz), (0, -1, 0),
                       r=0.0042, mat=BARE, length=0.002)
    return parts


def lever_set(coll, prefix, x, z, width):
    """Lever handle + escutcheon + key cylinder on both faces."""
    parts = []
    for side, sy in (("A", 1.0), ("B", -1.0)):
        y = 0.0315 * sy
        n = (0, sy, 0)
        parts.append(box(coll, prefix + "_Esc_" + side, 0.048, 0.004, 0.155,
                         (x, y + 0.002 * sy, z), BARE, 0.0012, 3))
        parts.append(cyl(coll, prefix + "_Rose_" + side, 0.030, 0.008,
                         (x, y + 0.007 * sy, z + 0.015), ALU, 'Y', 20,
                         0.0008, 2))
        parts.append(cyl(coll, prefix + "_Neck_" + side, 0.010, 0.030,
                         (x, y + 0.022 * sy, z + 0.015), ALU, 'Y', 12,
                         0.0006, 2))
        # lever points towards the hinge for A, towards the latch for B:
        # both point to -X which is the natural approach side on the pull face
        lx = x - 0.075
        parts.append(box(coll, prefix + "_Lever_" + side, 0.150, 0.020, 0.026,
                         (lx, y + 0.038 * sy, z + 0.015), ALU, 0.004, 3))
        parts.append(cyl(coll, prefix + "_LeverEnd_" + side, 0.012, 0.020,
                         (x - 0.148, y + 0.038 * sy, z + 0.015), ALU,
                         'X', 12, 0.002, 2))
        # key cylinder below the rose
        parts.append(cyl(coll, prefix + "_Cyl_" + side, 0.0125, 0.011,
                         (x, y + 0.008 * sy, z - 0.070), BRASS, 'Y', 16,
                         0.0006, 2))
        parts.append(box(coll, prefix + "_Keyway_" + side, 0.004, 0.0015,
                         0.010, (x, y + 0.014 * sy, z - 0.070),
                         DARK, 0.0003, 1))
        for i, zz in enumerate((-0.055, 0.055)):
            parts += screw(coll, "%s_ESCR%d_%s" % (prefix, i, side),
                           (x - 0.020, y + 0.004 * sy, z + zz), n,
                           r=0.0038, mat=BARE, length=0.0018)
    return parts


def latch_edge(coll, prefix, width, z):
    """Mortise faceplate and latch/dead bolts on the latch edge."""
    parts = []
    ex = width + 0.001
    parts.append(box(coll, prefix + "_Faceplate", 0.004, 0.052, 0.220,
                     (ex + 0.0005, 0.0, z), BARE, 0.0008, 2))
    parts.append(box(coll, prefix + "_LatchBolt", 0.018, 0.030, 0.024,
                     (ex + 0.010, 0.0, z - 0.020), ALU, 0.0012, 2))
    parts.append(box(coll, prefix + "_DeadBolt", 0.014, 0.026, 0.032,
                     (ex + 0.010, 0.0, z + 0.055), DARK, 0.0012, 2))
    for i, zz in enumerate((-0.085, 0.085)):
        parts += screw(coll, "%s_FPS%d" % (prefix, i),
                       (ex + 0.003, 0.0, z + zz), (1, 0, 0),
                       r=0.0036, mat=BARE, length=0.0016)
    return parts


def push_bar(coll, prefix, width, z):
    parts = []
    y = 0.0315
    x0, x1 = 0.14, width - 0.10
    xm = (x0 + x1) / 2
    parts.append(box(coll, prefix + "_Bar", x1 - x0, 0.034, 0.042,
                     (xm, y + 0.038, z), ALU, 0.008, 4))
    for i, bx in enumerate((x0 + 0.03, x1 - 0.03)):
        parts.append(box(coll, prefix + "_Bracket%d" % i, 0.055, 0.032, 0.095,
                         (bx, y + 0.015, z), DARK, 0.002, 3))
        for j, dz in enumerate((-0.030, 0.030)):
            parts += screw(coll, "%s_PBS%d_%d" % (prefix, i, j),
                           (bx, y + 0.031, z + dz), (0, 1, 0),
                           r=0.0042, mat=BARE, length=0.002)
    # grip bands
    for i, gx in enumerate((xm - 0.16, xm + 0.16)):
        parts.append(box(coll, prefix + "_Grip%d" % i, 0.018, 0.038, 0.046,
                         (gx, y + 0.038, z), RUB, 0.003, 3))
    # latch rod towards the latch edge
    parts.append(cyl(coll, prefix + "_LatchRod", 0.008, 0.080,
                     (x1 + 0.030, y + 0.020, z), DARK, 'X', 10, 0.0004, 1))
    return parts


def closer_leaf(coll, prefix, width, height):
    """Door closer on the pull face.  Body near mid-leaf, folded arm reaching
    the frame bracket at the hinge head.  Body x 0.35..0.65; shoe at x=0.075."""
    parts = []
    bx, bz = 0.50, height - 0.140
    parts.append(box(coll, prefix + "_Body", 0.300, 0.064, 0.078,
                     (bx, -0.063, bz), ALU, 0.012, 4))
    for i, ex in enumerate((0.358, 0.642)):
        parts.append(box(coll, prefix + "_EndCap%d" % i, 0.020, 0.068, 0.082,
                         (ex, -0.063, bz), DARK, 0.002, 3))
    parts.append(cyl(coll, prefix + "_Spindle", 0.016, 0.095,
                     (0.350, -0.063, bz + 0.055), DARK, 'Z', 12, 0.0006, 2))
    parts.append(box(coll, prefix + "_Arm1", 0.285, 0.020, 0.014,
                     (0.212, -0.063, bz + 0.100), DARK, 0.004, 3))
    parts.append(cyl(coll, prefix + "_ArmPivot", 0.014, 0.032,
                     (0.150, -0.063, bz + 0.100), BARE, 'Z', 12, 0.0006, 2))
    parts.append(box(coll, prefix + "_Arm2", 0.110, 0.018, 0.012,
                     (0.120, -0.063, bz + 0.118), DARK, 0.003, 3))
    parts.append(box(coll, prefix + "_Shoe", 0.070, 0.050, 0.030,
                     (0.075, -0.063, bz + 0.100), DARK, 0.002, 3))
    for i, (xx, zz) in enumerate(((0.42, bz - 0.025), (0.60, bz - 0.025),
                                  (0.42, bz + 0.025), (0.60, bz + 0.025))):
        parts += screw(coll, "%s_CLS%d" % (prefix, i),
                       (xx, -0.095, zz), (0, -1, 0),
                       r=0.0045, mat=BARE, length=0.0022)
    parts.append(box(coll, prefix + "_Label", 0.060, 0.0015, 0.028,
                     (0.50, -0.096, bz), LABEL, 0.0004, 2))
    return parts


def vision_panel(coll, prefix, x0, x1, z0, z1, leaf_thick=0.0315):
    parts = []
    xm, zm = (x0 + x1) / 2, (z0 + z1) / 2
    w, h = x1 - x0, z1 - z0
    # glass pane larger than the hole, embedded in the leaf ring
    parts.append(box(coll, prefix + "_Glass", w + 0.024, 0.006, h + 0.024,
                     (xm, 0.0, zm), GLASS, 0.0008, 2))
    # inner reveal liners bridge the glass to the steel ring
    for sy in (1.0, -1.0):
        yc = 0.013 * sy
        parts.append(box(coll, prefix + "_LinerT_%s" % ("A" if sy > 0 else "B"),
                         w + 0.034, 0.022, 0.024,
                         (xm, yc, z1 + 0.008), PAINT, 0.0012, 2))
        parts.append(box(coll, prefix + "_LinerB_%s" % ("A" if sy > 0 else "B"),
                         w + 0.034, 0.022, 0.024,
                         (xm, yc, z0 - 0.008), PAINT, 0.0012, 2))
        parts.append(box(coll, prefix + "_LinerL_%s" % ("A" if sy > 0 else "B"),
                         0.024, 0.022, h + 0.034,
                         (x0 - 0.008, yc, zm), PAINT, 0.0012, 2))
        parts.append(box(coll, prefix + "_LinerR_%s" % ("A" if sy > 0 else "B"),
                         0.024, 0.022, h + 0.034,
                         (x1 + 0.008, yc, zm), PAINT, 0.0012, 2))
    # aluminium clamping frame both faces
    for side, sy in (("A", 1.0), ("B", -1.0)):
        yy = 0.0305 * sy
        parts.append(box(coll, prefix + "_FrameT_" + side, w + 0.060, 0.011,
                         0.030, (xm, yy, z1 + 0.015), ALU, 0.0015, 3))
        parts.append(box(coll, prefix + "_FrameB_" + side, w + 0.060, 0.011,
                         0.030, (xm, yy, z0 - 0.015), ALU, 0.0015, 3))
        yv = yy - 0.0022 * sy
        parts.append(box(coll, prefix + "_FrameL_" + side, 0.030, 0.011,
                         h + 0.010, (x0 - 0.015, yv, zm), ALU, 0.0015, 3))
        parts.append(box(coll, prefix + "_FrameR_" + side, 0.030, 0.011,
                         h + 0.010, (x1 + 0.015, yv, zm), ALU, 0.0015, 3))
        for i, (sx, sz) in enumerate(((x0 - 0.015, z0 - 0.015),
                                      (x1 + 0.015, z0 - 0.015),
                                      (x0 - 0.015, z1 + 0.015),
                                      (x1 + 0.015, z1 + 0.015))):
            parts += screw(coll, "%s_VS%s%d" % (prefix, side, i),
                           (sx, yy + 0.005 * sy, sz), (0, sy, 0),
                           r=0.0036, mat=BARE, length=0.0016)
    return parts


def kick_plate(coll, prefix, width, z0=0.045, z1=0.255):
    parts = []
    x0, x1 = 0.055, width - 0.055
    parts.append(box(coll, prefix + "_Plate", x1 - x0, 0.003, z1 - z0,
                     ((x0 + x1) / 2, 0.033, (z0 + z1) / 2), BARE, 0.0012, 3))
    # folded top lip
    parts.append(box(coll, prefix + "_Lip", x1 - x0, 0.010, 0.010,
                     ((x0 + x1) / 2, 0.030, z1 + 0.004), BARE, 0.0008, 2))
    for i in range(4):
        xx = x0 + 0.04 + i * (x1 - x0 - 0.08) / 3.0
        for j, zz in enumerate((z0 + 0.035, z1 - 0.035)):
            parts += screw(coll, "%s_KPS%d_%d" % (prefix, i, j),
                           (xx, 0.0345, zz), (0, 1, 0),
                           r=0.0034, mat=BARE, length=0.0014)
    return parts


def flush_bolt(coll, prefix, width, z, up=True, rod_len=0.075, rod_off=0.040,
               guide_off=0.070):
    parts = []
    ex = width - 0.050
    parts.append(box(coll, prefix + "_Plate", 0.030, 0.004, 0.090,
                     (ex, 0.0315, z), BARE, 0.0012, 3))
    parts.append(cyl(coll, prefix + "_Rod", 0.007, rod_len,
                     (ex, 0.0, z + (rod_off if up else -rod_off)), DARK, 'Z',
                     10, 0.0004, 1))
    parts.append(cyl(coll, prefix + "_Guide", 0.011, 0.020,
                     (ex, 0.0, z + (guide_off if up else -guide_off)), DARK, 'Z',
                     12, 0.0006, 2))
    for i, zz in enumerate((-0.030, 0.030)):
        parts += screw(coll, "%s_FBS%d" % (prefix, i),
                       (ex, 0.0335, z + zz), (0, 1, 0),
                       r=0.0036, mat=BARE, length=0.0014)
    return parts


def leaf_parts(coll, prefix, width, height, hole, z0=0.0, kind="security",
               active=True):
    """Build the leaf in local coords: hinge axis at x=0, leaf 0..width."""
    parts = []
    hx0, hx1, hz0, hz1 = hole
    # --- ring plate with the vision hole (one manifold ring)
    bm = bmesh.new()
    def V(x, y, z):
        return bm.verts.new((x, y, z))
    yo = 0.025
    of = [V(0.004, -yo, z0), V(width, -yo, z0), V(width, -yo, height), V(0.004, -yo, height)]
    ob = [V(0.004, yo, z0), V(width, yo, z0), V(width, yo, height), V(0.004, yo, height)]
    inf = [V(hx0, -yo, hz0), V(hx1, -yo, hz0), V(hx1, -yo, hz1), V(hx0, -yo, hz1)]
    inb = [V(hx0, yo, hz0), V(hx1, yo, hz0), V(hx1, yo, hz1), V(hx0, yo, hz1)]
    for k in range(4):
        j = (k + 1) % 4
        bm.faces.new((of[k], of[j], inf[j], inf[k]))
        bm.faces.new((inb[k], inb[j], ob[j], ob[k]))
        bm.faces.new((of[j], of[k], ob[k], ob[j]))
        bm.faces.new((inf[k], inf[j], inb[j], inb[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    parts.append(make_part(prefix + "_Core", bm, PAINT, coll, 0.0015, 3))

    # --- raised stiles / rails (both faces)
    for sy in (1.0, -1.0):
        yy = 0.028 * sy
        parts.append(box(coll, prefix + "_StileL_%s" % ("A" if sy > 0 else "B"),
                         0.085, 0.008, height - 0.02, (0.055, yy, height / 2),
                         PAINT, 0.002, 3))
        parts.append(box(coll, prefix + "_StileR_%s" % ("A" if sy > 0 else "B"),
                         0.085, 0.008, height - 0.02,
                         (width - 0.055, yy, height / 2), PAINT, 0.002, 3))
        yr = 0.0275 * sy
        parts.append(box(coll, prefix + "_RailB_%s" % ("A" if sy > 0 else "B"),
                         width - 0.10, 0.008, 0.14, (width / 2, yr, 0.105),
                         PAINT, 0.002, 3))
        parts.append(box(coll, prefix + "_RailT_%s" % ("A" if sy > 0 else "B"),
                         width - 0.10, 0.008, 0.12,
                         (width / 2, yr, height - 0.085), PAINT, 0.002, 3))
        parts.append(box(coll, prefix + "_RailM_%s" % ("A" if sy > 0 else "B"),
                         width - 0.10, 0.008, 0.14, (width / 2, yr, hz0 - 0.085),
                         PAINT, 0.002, 3))
        # lower panel raised border
        px0, px1 = 0.105, width - 0.105
        pz0, pz1 = 0.185, hz0 - 0.165
        parts.append(box(coll, prefix + "_PanelT_%s" % ("A" if sy > 0 else "B"),
                         px1 - px0, 0.006, 0.016, ((px0 + px1) / 2, 0.027 * sy, pz1),
                         PAINT, 0.0012, 2))
        parts.append(box(coll, prefix + "_PanelB_%s" % ("A" if sy > 0 else "B"),
                         px1 - px0, 0.006, 0.016, ((px0 + px1) / 2, 0.027 * sy, pz0),
                         PAINT, 0.0012, 2))
        parts.append(box(coll, prefix + "_PanelL_%s" % ("A" if sy > 0 else "B"),
                         0.016, 0.006, pz1 - pz0, (px0, 0.027 * sy, (pz0 + pz1) / 2),
                         PAINT, 0.0012, 2))
        parts.append(box(coll, prefix + "_PanelR_%s" % ("A" if sy > 0 else "B"),
                         0.016, 0.006, pz1 - pz0, (px1, 0.027 * sy, (pz0 + pz1) / 2),
                         PAINT, 0.0012, 2))

    # --- internal stiffener ribs on the pull side
    for i, xx in enumerate((0.24, width - 0.24)):
        parts.append(box(coll, prefix + "_Rib%d" % i, 0.036, 0.020, 0.92,
                         (xx, -0.038, height * 0.42), GALV, 0.002, 3))
        parts.append(box(coll, prefix + "_RibFoot%d" % i, 0.070, 0.030, 0.010,
                         (xx, -0.042, 0.215), GALV, 0.0015, 2))
    parts.append(box(coll, prefix + "_RibH", width - 0.25, 0.018, 0.030,
                     (width / 2, -0.038, 0.78), GALV, 0.0015, 2))

    # --- edge caps
    parts.append(box(coll, prefix + "_CapTop", width + 0.004, 0.056, 0.022,
                     (width / 2, 0.0, height - 0.009), DARK, 0.0015, 3))
    parts.append(box(coll, prefix + "_CapBot", width + 0.004, 0.056, 0.022,
                     (width / 2, 0.0, 0.009), DARK, 0.0015, 3))
    # bottom sweep
    parts.append(box(coll, prefix + "_Sweep", width - 0.06, 0.014, 0.028,
                     (width / 2, -0.030, 0.022), RUB, 0.0012, 2))

    # --- vision panel
    parts += vision_panel(coll, prefix + "_Vision", hx0, hx1, hz0, hz1,
                          0.0315)

    # --- hinges (three) - world z 0.355 / ~1.225 / 2.095 for the 2.40 door
    for i, hz in enumerate((0.320, height * 0.51, height - 0.275)):
        parts += hinge_leaf(coll, "%s_HG%d" % (prefix, i), hz)

    # --- lock / lever / edge (active leaves only)
    lz = 1.060
    if active:
        parts += lever_set(coll, prefix + "_LEV", width - 0.115, lz, width)
        parts += latch_edge(coll, prefix + "_LATCH", width, lz)

    # --- panic bar and kick plate on the push face
    parts += push_bar(coll, prefix + "_PB", width, 1.000)
    parts += kick_plate(coll, prefix, width)

    # --- closer on the pull face
    parts += closer_leaf(coll, prefix + "_CL", width, height)

    # --- small blank identification plate
    parts.append(box(coll, prefix + "_IDPlate", 0.055, 0.004, 0.025,
                     (width - 0.085, 0.032, height - 0.34), LABEL, 0.0004, 2))
    for i, xx in enumerate((width - 0.103, width - 0.067)):
        parts += screw(coll, "%s_IDSCR%d" % (prefix, i),
                       (xx, 0.034, height - 0.34), (0, 1, 0),
                       r=0.0028, mat=BARE, length=0.0012)

    if not active:
        # inactive leaf: astragal at the meeting edge + flush bolts
        parts.append(box(coll, prefix + "_Astragal", 0.026, 0.070, height - 0.03,
                         (width - 0.008, 0.0, height / 2), DARK, 0.002, 3))
        parts.append(box(coll, prefix + "_AstragalSeal", 0.010, 0.012,
                         height - 0.08, (width - 0.020, 0.0315, height / 2),
                         RUB, 0.0012, 2))
        parts += flush_bolt(coll, prefix + "_FBTop", width, height - 0.095, True)
        parts += flush_bolt(coll, prefix + "_FBBot", width, 0.305, False,
                            rod_len=0.260, rod_off=0.135, guide_off=0.245)
    return parts


def mirror_mesh_x(ob):
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    for v in bm.verts:
        v.co.x = -v.co.x
    bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(me)
    bm.free()


# ---------------------------------------------------------------------------
# frame
# ---------------------------------------------------------------------------

def frame_parts(coll, prefix, clear_w, clear_h, wall_t=0.20, double=False):
    parts = []
    face, depth = 0.07, wall_t + 0.020
    hw = clear_w / 2.0
    # jambs
    for side, sx in (("L", -1.0), ("R", 1.0)):
        parts.append(box(coll, prefix + "_Jamb" + side, face, depth, clear_h,
                         (sx * (hw + face / 2), 0.0, clear_h / 2), GALV,
                         0.0035, 3))
        # architrave on both wall faces
        for fy in (-1.0, 1.0):
            parts.append(box(coll, prefix + "_Arch" + side + ("F" if fy > 0 else "B"),
                             0.115, 0.013, clear_h + 0.02,
                             (sx * (hw + face + 0.010), fy * (depth / 2 + 0.0055),
                              (clear_h + 0.02) / 2), GALV, 0.0015, 3))
        # outer anchor tabs (3)
        for i, az in enumerate((0.42, 1.20, 1.98)):
            ax = sx * (hw + face + 0.010)
            parts.append(box(coll, "%s_ANCH%s%d" % (prefix, side, i),
                             0.080, 0.020, 0.100, (ax, 0.0, az), DARK,
                             0.0012, 2))
            for j, dz in enumerate((-0.030, 0.030)):
                parts += bolt(coll, "%s_ANB%s%d_%d" % (prefix, side, i, j),
                              (ax, 0.0, az + dz), (sx, 0, 0), r=0.0065,
                              head=0.005, length=0.012)
        # hinge-side reinforcement plates
        if (side == "L") or double:
            for i, hz in enumerate((0.355, clear_h * 0.51, clear_h - 0.305)):
                hx = sx * hw
                parts += hinge_frame(coll, "%s_HGF%s%d" % (prefix, side, i),
                                     hx, hz, 1 if sx < 0 else -1)
        # latch strike (single right jamb / double centre handled on leaf)
        if side == "R" and not double:
            parts.append(box(coll, prefix + "_StrikePlate", 0.008, 0.090,
                             0.230, (hw + 0.001, 0.0, 1.060), BARE,
                             0.0012, 3))
            parts.append(box(coll, prefix + "_StrikeSlot", 0.002, 0.028, 0.055,
                             (hw + 0.0055, 0.0, 1.040), DARK, 0.0006, 2))
        # blank label plate
        if side == "L":
            parts.append(box(coll, prefix + "_FrameLabel", 0.052, 0.004, 0.026,
                             (-(hw + face / 2), -(depth / 2 + 0.0135),
                              clear_h * 0.66), LABEL, 0.0004, 2))
            for i, dz in enumerate((-0.008, 0.008)):
                parts += screw(coll, "%s_FLB%d" % (prefix, i),
                               (-(hw + face / 2), -(depth / 2 + 0.0155),
                                clear_h * 0.66 + dz), (0, -1, 0),
                               r=0.0026, mat=BARE, length=0.0012)

    # door stops, interrupted at hinges (and at the strike on the latch jamb)
    def stops(col, x, sgn, hinge_side):
        out = []
        if hinge_side:
            zs = [(0.030, 0.245), (0.465, 1.105), (1.305, 1.945),
                  (2.145, 2.370)]
        else:
            zs = [(0.030, 0.245), (0.465, 0.940), (1.180, 1.945),
                  (2.145, 2.370)]
        for i, (za, zb) in enumerate(zs):
            if zb - za < 0.04:
                continue
            out.append(box(col, "%s_Stop%d" % (prefix + ("_L" if sgn < 0 else "_R"), i),
                           0.024, 0.026, zb - za,
                           (x, 0.045, (za + zb) / 2), GALV, 0.0012, 3))
        out.append(box(col, "%s_Seal" % (prefix + ("_L" if sgn < 0 else "_R")),
                       0.006, 0.006, 2.32, (x - sgn * 0.012, 0.032, 1.20),
                       RUB, 0.001, 2))
        return out

    parts += stops(coll, -hw + 0.011, -1, True)
    parts += stops(coll, hw - 0.011, 1, False)

    # head
    parts.append(box(coll, prefix + "_Head", clear_w + 2 * face, depth + 0.004, 0.077,
                     (0, 0, clear_h + 0.0355), GALV, 0.0035, 3))
    for fy in (-1.0, 1.0):
        parts.append(box(coll, prefix + "_ArchHead" + ("F" if fy > 0 else "B"),
                         clear_w + 2 * face + 0.20, 0.012, 0.115,
                         (0, fy * (depth / 2 + 0.0075), clear_h + 0.020),
                         GALV, 0.0015, 3))
    parts.append(box(coll, prefix + "_HeadStop", clear_w - 0.02, 0.026, 0.024,
                     (0, 0.045, clear_h - 0.012), GALV, 0.0012, 3))
    parts.append(box(coll, prefix + "_HeadSeal", clear_w - 0.05, 0.006, 0.006,
                     (0, 0.032, clear_h - 0.012), RUB, 0.001, 2))
    # head corner gussets
    for sx in (-1, 1):
        parts.append(box(coll, prefix + "_Gusset%s" % ("L" if sx < 0 else "R"),
                         0.090, 0.060, 0.080,
                         (sx * (hw + 0.030), 0.075, clear_h + 0.040),
                         GALV, 0.002, 3))

    # threshold with nosing (lifted 2 mm so it never shares the floor plane)
    parts.append(box(coll, prefix + "_Threshold", clear_w + 0.10, depth - 0.02,
                     0.026, (0, 0, 0.015), BARE, 0.0015, 3))
    parts.append(box(coll, prefix + "_SillNoseF", clear_w + 0.06, 0.035, 0.016,
                     (0, -(depth / 2 - 0.010), 0.009), BARE, 0.001, 2))
    parts.append(box(coll, prefix + "_SillNoseB", clear_w + 0.06, 0.035, 0.016,
                     (0, (depth / 2 - 0.010), 0.009), BARE, 0.001, 2))
    for i, xx in enumerate((-hw + 0.08, hw - 0.08)):
        parts += bolt(coll, "%s_THB%d" % (prefix, i), (xx, 0.0, 0.028),
                      (0, 0, 1), r=0.0065, head=0.004, length=0.012)

    # closer bracket on the head (leaf side, pull face)
    parts.append(box(coll, prefix + "_CloserBracket", 0.115, 0.070, 0.050,
                     (-hw + 0.075, -0.063, clear_h - 0.075), DARK,
                     0.002, 3))
    for i, dz in enumerate((-0.015, 0.015)):
        parts += screw(coll, "%s_CBR%d" % (prefix, i),
                       (-hw + 0.075, -0.100, clear_h - 0.075 + dz),
                       (0, -1, 0), r=0.0038, mat=BARE, length=0.0016)

    # cable pass / door contact on the head
    parts.append(box(coll, prefix + "_DoorContact", 0.060, 0.040, 0.022,
                     (hw - 0.18, 0.0, clear_h - 0.010), DARK, 0.0015, 2))
    parts.append(cyl(coll, prefix + "_ContactLED", 0.006, 0.004,
                     (hw - 0.18, 0.0, clear_h - 0.023), M["lens_red_dead"],
                     'Z', 10, 0.0004, 1))
    return parts


# ---------------------------------------------------------------------------
# master builders
# ---------------------------------------------------------------------------

def build_single(coll, name, clear_w=1.10, clear_h=2.40, service=False,
                 loc=(0, 0, 0)):
    root = make_root(name + "_ROOT", coll)
    prefix = name
    fp = frame_parts(coll, prefix + "_FRAME", clear_w, clear_h)
    frame = join_group(coll, prefix + "_FRAME", fp)
    parent_to(frame, root)

    width = clear_w - 0.02
    height = clear_h - 0.065
    if service:
        hole = (width * 0.38, width * 0.64, height * 0.60, height * 0.82)
        lp = leaf_parts(coll, prefix + "_LEAF", width, height, hole,
                        kind="service", active=True)
    else:
        hole = (width * 0.35, width * 0.65, height * 0.56, height * 0.82)
        lp = leaf_parts(coll, prefix + "_LEAF", width, height, hole,
                        kind="security", active=True)
    leaf = join_group(coll, prefix + "_LEAF", lp)
    leaf.location = (-(clear_w / 2 - 0.010), 0.0, 0.035)
    parent_to(leaf, root)
    finalize_master(root, coll, [frame, leaf], loc, {
        "fm_class": "DOOR", "fm_subtype": "service" if service else "security_single",
        "fm_clear_w": clear_w, "fm_clear_h": clear_h,
        "fm_leaf_w": width, "fm_leaf_h": height,
        "fm_pivot": "frame: opening centre at floor; leaf: hinge axis",
        "fm_ports": json.dumps({"wall": "y=0, thickness 0.20"}),
    })
    return root


def build_double(coll, name, clear_w=1.80, clear_h=2.60, loc=(3.0, 0, 0)):
    root = make_root(name + "_ROOT", coll)
    prefix = name
    fp = frame_parts(coll, prefix + "_FRAME", clear_w, clear_h, double=True)
    frame = join_group(coll, prefix + "_FRAME", fp)
    parent_to(frame, root)

    width_l = 0.900
    width_r = 0.890
    height = clear_h - 0.065
    hole_l = (width_l * 0.30, width_l * 0.60, height * 0.55, height * 0.81)
    hole_r = (width_r * 0.30, width_r * 0.60, height * 0.55, height * 0.81)

    lp = leaf_parts(coll, prefix + "_LEAF_L", width_l, height, hole_l,
                    kind="security", active=False)
    leaf_l = join_group(coll, prefix + "_LEAF_L", lp)
    leaf_l.location = (-(clear_w / 2 - 0.010), 0.0, 0.035)
    parent_to(leaf_l, root)

    rp = leaf_parts(coll, prefix + "_LEAF_R", width_r, height, hole_r,
                    kind="security", active=True)
    leaf_r = join_group(coll, prefix + "_LEAF_R", rp, uv=False)
    mirror_mesh_x(leaf_r)          # right-hand leaf, no negative object scale
    smart_uv(leaf_r)
    leaf_r.location = (clear_w / 2 - 0.010, 0.0, 0.035)
    parent_to(leaf_r, root)

    finalize_master(root, coll, [frame, leaf_l, leaf_r], loc, {
        "fm_class": "DOOR", "fm_subtype": "security_double",
        "fm_clear_w": clear_w, "fm_clear_h": clear_h,
        "fm_leaf_w": "0.900 + 0.890", "fm_leaf_h": height,
        "fm_pivot": "frame: opening centre at floor; leaves: hinge axes",
    })
    return root


def portal(coll, name, clear_w, loc_x=8.0):
    root = make_root(name + "_ROOT", coll)
    prefix = name
    parts = []
    face, depth = 0.18, 0.34
    hw = clear_w / 2.0
    ch = 2.88
    # jambs + plinths
    for side, sx in (("L", -1.0), ("R", 1.0)):
        x = sx * (hw + face / 2)
        parts.append(box(coll, prefix + "_Jamb" + side, face, depth, ch,
                         (x, 0, ch / 2 + 0.006), GALV, 0.004, 3))
        parts.append(box(coll, prefix + "_Plinth" + side, 0.30, 0.42, 0.225,
                         (x, 0, 0.1125), DARK, 0.004, 3))
        parts.append(box(coll, prefix + "_PlinthCap" + side, 0.34, 0.46, 0.028,
                         (x, 0, 0.236), BARE, 0.002, 3))
        # side cover plates create a panel line
        for fy in (-1, 1):
            parts.append(box(coll, prefix + "_Cover" + side + ("F" if fy > 0 else "B"),
                             0.135, 0.014, ch - 0.16,
                             (x, fy * (depth / 2 + 0.0065), ch / 2 + 0.04),
                             GALV, 0.002, 3))
        # stiffener ribs on the outside
        for i, rz in enumerate((0.55, 1.45, 2.35)):
            parts.append(box(coll, "%s_Rib%s%d" % (prefix, side, i),
                             0.052, 0.020, 0.36,
                             (sx * (hw + face + 0.006), 0, rz), GALV,
                             0.0015, 3))
        # anchor bolts through the plinth
        for i, yy in enumerate((-0.13, 0.13)):
            parts += bolt(coll, "%s_PAB%s%d" % (prefix, side, i),
                          (x, yy, 0.238), (0, 0, 1), r=0.009, head=0.006,
                          length=0.02)
        # rubber bumper strip on the inner face
        parts.append(box(coll, prefix + "_Bumper" + side, 0.040, 0.070,
                         ch - 0.42, (sx * (hw - 0.017), 0.0, ch / 2 - 0.05),
                         RUB, 0.004, 3))
        for i, bz in enumerate((0.55, 2.35)):
            parts.append(box(coll, "%s_BumperClamp%s%d" % (prefix, side, i),
                             0.070, 0.030, 0.060,
                             (sx * (hw + 0.020), 0.0, bz), DARK, 0.0015, 3))
        # hazard marker on the plinth
        parts.append(box(coll, prefix + "_Hazard" + side, 0.22, 0.006, 0.060,
                         (x, -(0.212), 0.150), M["paint_orange"], 0.001, 2))

    # header
    parts.append(box(coll, prefix + "_Header", clear_w + 2 * face, depth + 0.004, 0.284,
                     (0, 0, ch + 0.138), GALV, 0.004, 3))
    parts.append(box(coll, prefix + "_HeaderCap", clear_w + 2 * face + 0.08,
                     depth + 0.06, 0.034, (0, 0, ch + 0.293), BARE,
                     0.002, 3))
    # header gussets front and back
    ng = max(3, int(round(clear_w / 1.2)))
    for i in range(ng):
        gx = -clear_w / 2 + clear_w * (i + 0.5) / ng
        for fy in (-1, 1):
            parts.append(box(coll, "%s_HRib%d%s" % (prefix, i, "F" if fy > 0 else "B"),
                             0.055, 0.030, 0.185,
                             (gx, fy * (depth / 2 + 0.012), ch + 0.125),
                             GALV, 0.0015, 3))
    # lifting lugs
    for sx in (-1, 1):
        parts.append(cyl(coll, prefix + "_Lug%s" % ("L" if sx < 0 else "R"),
                         0.040, 0.030, (sx * (hw + 0.10), 0.0, ch + 0.345),
                         DARK, 'Y', 16, 0.0015, 3))
        parts.append(box(coll, prefix + "_LugPlate%s" % ("L" if sx < 0 else "R"),
                         0.090, 0.014, 0.070,
                         (sx * (hw + 0.10), 0.0, ch + 0.322), GALV, 0.0015, 2))
    # header bolts
    for i, xx in enumerate((-hw + 0.08, 0.0, hw - 0.08)):
        for j, zz in enumerate((ch + 0.06, ch + 0.20)):
            parts += bolt(coll, "%s_HB%d_%d" % (prefix, i, j),
                          (xx, -(depth / 2 + 0.005), zz), (0, -1, 0),
                          r=0.0075, length=0.014)
    # threshold (stops at the jamb faces, no overlapping plinth footprint)
    parts.append(box(coll, prefix + "_Threshold", clear_w - 0.004, 0.36, 0.012,
                     (0, 0, 0.008), BARE, 0.0015, 3))
    for i, xx in enumerate((-hw + 0.10, 0.0, hw - 0.10)):
        for j, yy in enumerate((-0.11, 0.11)):
            parts += bolt(coll, "%s_TB%d_%d" % (prefix, i, j),
                          (xx, yy, 0.014), (0, 0, 1), r=0.0065,
                          head=0.004, length=0.012)
    # centre mullion on the 8 m portal (keeps the header credible)
    if clear_w >= 7.5:
        parts.append(box(coll, prefix + "_Mullion", 0.20, depth - 0.004, ch,
                         (0, 0, ch / 2 + 0.008), GALV, 0.0035, 3))
        parts.append(box(coll, prefix + "_MullionBase", 0.30, 0.40, 0.200,
                         (0, 0, 0.105), DARK, 0.003, 3))
        parts.append(box(coll, prefix + "_MullionCap", 0.28, depth + 0.04, 0.030,
                         (0, 0, ch + 0.015), BARE, 0.002, 3))
        for fy in (-1, 1):
            parts.append(box(coll, prefix + "_MullionCover" + ("F" if fy > 0 else "B"),
                             0.15, 0.014, ch - 0.14,
                             (0, fy * 0.1735, ch / 2 + 0.04),
                             GALV, 0.0015, 3))
        for i, zz in enumerate((0.55, 1.45, 2.35)):
            for fy in (-1, 1):
                parts.append(box(coll, "%s_MRib%d%s" % (prefix, i, "F" if fy > 0 else "B"),
                                 0.050, 0.014, 0.30,
                                 (0.085 * fy, fy * (depth / 2 + 0.006), zz),
                                 GALV, 0.0012, 2))
        parts += bolt(coll, prefix + "_MB1", (0, 0, 0.205), (0, 0, 1),
                      r=0.009, head=0.006, length=0.02)

    ob = join_group(coll, name, parts)
    parent_to(ob, root)
    finalize_master(root, coll, [ob], (loc_x, 0, 0), {
        "fm_class": "PORTAL", "fm_subtype": "open_portal_%d" % int(clear_w * 1000),
        "fm_clear_w": clear_w, "fm_clear_h": ch, "fm_outer_w": clear_w + 0.36,
        "fm_pivot": "opening centre at floor",
        "fm_mullion": "yes" if clear_w >= 7.5 else "no",
    })
    return root


def build_all():
    if bpy.data.collections.get("DOORS"):
        from fm_shared_p0_lib import clear_collection_tree
        clear_collection_tree("DOORS")
    ensure_tree()
    coll = bpy.data.collections["DOORS"]
    out = []
    out.append(build_single(coll, "SM_SH_DOOR_SEC_SINGLE", 1.10, 2.40, False,
                            loc=(0, 0, 0)))
    out.append(build_double(coll, "SM_SH_DOOR_SEC_DOUBLE", 1.80, 2.60,
                            loc=(2.5, 0, 0)))
    out.append(build_single(coll, "SM_SH_DOOR_SERVICE", 1.00, 2.40, True,
                            loc=(5.2, 0, 0)))
    out.append(portal(coll, "SM_SH_PORTAL_4000", 4.00, loc_x=8.0))
    out.append(portal(coll, "SM_SH_PORTAL_6000", 6.00, loc_x=13.0))
    out.append(portal(coll, "SM_SH_PORTAL_8000", 8.00, loc_x=20.5))
    # report
    for r in out:
        meshes = [o for o in bpy.data.objects if o.parent == r and o.type == 'MESH']
        print("MASTER", r.name, "loc", tuple(round(v, 2) for v in r.location),
              "meshes", len(meshes), "tris", sum(tri_count(o) for o in meshes))
    return out


if __name__ == "__main__":
    build_all()
