"""P0a.1 hero pass for shared HVAC/services masters.

Rebuilds the weak rectangular HVAC family and shaft access in a temporary
collection, replaces every mesh datablock in place (masters + test assembly),
runs a structural QA and saves the blend.  No commit.
"""
import bpy
import bmesh
import math
import json
import os
import sys
from mathutils import Vector, Matrix

sys.path.insert(0, "/home/riyo/Documentos/game/scripts/fm")

from fm_shared_p0_lib import (
    ensure_tree, ensure_materials, get_coll, make_root, parent_to, box, cyl,
    screw, bolt, join_group, finalize_master, tri_count, make_part, bm_box,
    bm_cyl, bm_rect_tube_x, bm_rect_frame_x, bm_rect_loft_x, flange_bolts,
    clear_collection_tree,
)
from fm_shared_p0_services import bm_rot, bm_solid_loft, M, GALV, DARK, BARE, ALU, RUB, RED, \
    COND, CABLE, BRASS, FIRESTOP, LABEL, PAINT, ORANGE

TMP_NAME = "P0A1_HERO_TMP"
SERVICES = get_coll("SERVICES")
scene = bpy.context.scene

if TMP_NAME in bpy.data.collections:
    clear_collection_tree(TMP_NAME)
# remove the previous run's 600x400 sleeve master (idempotent rebuild)
_old_root = bpy.data.objects.get("SM_SH_SLEEVE_RECT_600x400_ROOT")
if _old_root:
    for _ch in list(_old_root.children):
        bpy.data.objects.remove(_ch, do_unlink=True)
    bpy.data.objects.remove(_old_root, do_unlink=True)
for _me in list(bpy.data.meshes):
    if _me.name.startswith("SM_SH_SLEEVE_RECT_600x400") and _me.users == 0:
        bpy.data.meshes.remove(_me)
for _o in list(bpy.data.objects):
    if _o.type == 'MESH' and _o.data.name.startswith("SM_SH_SLEEVE_RECT_600x400"):
        _me = _o.data
        bpy.data.objects.remove(_o, do_unlink=True)
        if _me.users == 0:
            bpy.data.meshes.remove(_me)
tmp = bpy.data.collections.new(TMP_NAME)
scene.collection.children.link(tmp)


def tpart(name, bm, mat, bevel=0.0012, seg=2):
    return make_part(name, bm, mat, tmp, bevel, seg)


def tbox(name, sx, sy, sz, center, mat, bevel=0.002, seg=3):
    return box(tmp, name, sx, sy, sz, center, mat, bevel, seg)


def tscrew(name, center, normal, r=0.004, mat=BARE, length=0.0015):
    return screw(tmp, name, center, normal, r=r, mat=mat, length=length)


def tbolt(name, center, normal, r=0.006, length=0.014):
    return bolt(tmp, name, center, normal, r=r, length=length)


def tcyl(name, r, depth, center, mat, axis='Z', seg=16, bevel=0.0008, bseg=2):
    return cyl(tmp, name, r, depth, center, mat, axis, seg, bevel, bseg)


def flange(name, x0, w, h, bolts=True, outward=(-1, 0, 0), plane=0.0):
    p = [tpart(name, bm_rect_frame_x(x0, x0 + 0.022, w + 0.082, h + 0.082,
                                     w - 0.004, h - 0.004, 0, 0), GALV, 0.0015, 2)]
    if bolts:
        # sink the bolt heads 0.5 mm into the flange so no face is coplanar
        plane = plane - outward[0] * 0.0005
        p += flange_bolts(tmp, name + "_FB", 'X', plane,
                          (w + 0.082) / 2, (h + 0.082) / 2, outward,
                          r=0.006, inset=0.05)
    return p


def corner_seams(name, w, h, x0, x1):
    p = []
    L = x1 - x0
    for i, (sy, sz) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        p.append(tbox("%s_Seam%d" % (name, i), L, 0.012, 0.012,
                      ((x0 + x1) / 2, sy * (w / 2 + 0.0015),
                       sz * (h / 2 + 0.0015)), GALV, 0.0012, 2))
    return p


def stiff_ring(name, x, w, h):
    return tpart(name, bm_rect_frame_x(x - 0.012, x + 0.012, w + 0.030,
                                       h + 0.030, w - 0.004, h - 0.004, 0, 0),
                 GALV, 0.0015, 2)


def rivet_row(name, w, h, x0, x1, step=0.22):
    p = []
    n = max(1, int((x1 - x0) / step))
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        p += tscrew("%s_RV%d" % (name, i), (x, -(w / 2 + 0.006), 0.0),
                    (0, -1, 0), r=0.0022, length=0.0012)
    return p


# ---------------------------------------------------------------------------
# straight duct (hero)
# ---------------------------------------------------------------------------

def hero_duct(name, w, h, length, spool=False):
    p = []
    p.append(tpart(name + "_Body",
                   bm_rect_tube_x(0.002, length - 0.002, w, h, 0.004, 0, 0),
                   GALV, 0.0015, 2))
    p += flange(name + "_FlangeIn", 0.0, w, h, True, (-1, 0, 0), 0.0)
    if spool:
        p += flange(name + "_FlangeOut", length - 0.022, w, h, True,
                    (1, 0, 0), length)
    p += corner_seams(name + "_Corner", w, h, 0.03, length - 0.03)
    xs = [0.55, 1.25] if length > 1.5 else [length * 0.55]
    for i, x in enumerate(xs):
        p.append(stiff_ring("%s_Ring%d" % (name, i), x, w, h))
    # longitudinal folded seam on the accessible face
    p.append(tbox(name + "_LongSeam", length - 0.10, 0.003, 0.006,
                  (length / 2, -(w / 2 + 0.0008), 0.0), GALV, 0.0006, 2))
    p += rivet_row(name + "_LongRivets", w, h, 0.08, length - 0.08)
    # access panel
    if not spool and length >= 1.5:
        ax = length * 0.55
        p.append(tbox(name + "_AccessFrame", 0.400, 0.010, 0.300,
                      (ax, -(w / 2 + 0.005), -0.02), GALV, 0.0012, 2))
        p.append(tbox(name + "_AccessDoor", 0.350, 0.007, 0.250,
                      (ax, -(w / 2 + 0.012), -0.02), ALU, 0.0012, 2))
        for i, (dx, dz) in enumerate(((-0.150, -0.100), (0.150, -0.100),
                                       (0.150, 0.100), (-0.150, 0.100))):
            p += tscrew("%s_AS%d" % (name, i),
                        (ax + dx, -(w / 2 + 0.016), -0.02 + dz),
                        (0, -1, 0), r=0.0034, length=0.0015)
        p.append(tbox(name + "_AccessLatch", 0.045, 0.012, 0.018,
                      (ax + 0.150, -(w / 2 + 0.017), 0.06), BARE, 0.0012, 2))
    # label
    p.append(tbox(name + "_Label", 0.085, 0.003, 0.038,
                  (0.34, -(w / 2 + 0.004), h / 2 - 0.085), LABEL, 0.0004, 2))
    for i, xx in enumerate((0.30, 0.38)):
        p += tscrew("%s_LS%d" % (name, i),
                    (xx, -(w / 2 + 0.006), h / 2 - 0.085),
                    (0, -1, 0), r=0.0022, length=0.0012)
    # hanger cleats on top; short spools get one central cleat
    cleat_xs = [length / 2] if length < 0.8 else [0.16, length - 0.16]
    for i, x in enumerate(cleat_xs):
        p.append(tbox("%s_Cleat%d" % (name, i), 0.090, 0.064, 0.006,
                      (x, 0.0, h / 2 + 0.004), GALV, 0.0012, 2))
        for j, sy in enumerate((-0.022, 0.022)):
            p += tbolt("%s_CB%d%d" % (name, i, j),
                       (x, sy, h / 2 + 0.008), (0, 0, 1), r=0.0045,
                       length=0.010)
    return join_group(tmp, name, p)


# ---------------------------------------------------------------------------
# tee
# ---------------------------------------------------------------------------

def hero_tee(name, w, h, main_len=1.6, branch_len=0.6):
    p = []
    p.append(tpart(name + "_Main",
                   bm_rect_tube_x(0.002, main_len - 0.002, w, h, 0.004, 0, 0),
                   GALV, 0.0015, 2))
    # branch goes down (-Z) from the main bottom face
    bm = bm_rect_tube_x(h / 2 - 0.004, branch_len - 0.002, w - 0.020,
                        h - 0.020, 0.004, 0, 0)
    bm_rot(bm, ry=math.radians(90), loc=(main_len / 2, 0, 0))
    p.append(tpart(name + "_Branch", bm, GALV, 0.0015, 2))
    # main flanges / bolts
    for lab, x, x0, x1, nrm in (("A", 0.0, 0.0, 0.022, (-1, 0, 0)),
                                 ("B", main_len, main_len - 0.022, main_len,
                                  (1, 0, 0))):
        p.append(tpart("%s_Flange%s" % (name, lab),
                       bm_rect_frame_x(x0, x1, w + 0.082, h + 0.082,
                                       w - 0.004, h - 0.004, 0, 0),
                       GALV, 0.0015, 2))
        p += flange_bolts(tmp, "%s_FB%s" % (name, lab), 'X',
                          x - nrm[0] * 0.0005,
                          (w + 0.082) / 2, (h + 0.082) / 2, nrm,
                          r=0.006, inset=0.05)
    # branch flange (normal -Z); branch outer section is (w-0.02, h-0.02)
    fb = bm_rect_frame_x(-0.022, 0.0, w + 0.062, h + 0.062,
                         w - 0.026, h - 0.026, 0, 0)
    bm_rot(fb, ry=math.radians(90), loc=(main_len / 2, 0, -branch_len))
    p.append(tpart(name + "_FlangeBr", fb, GALV, 0.0015, 2))
    for i, (dx, dy) in enumerate(((-0.30, -0.24), (0.30, -0.24),
                                   (0.30, 0.24), (-0.30, 0.24),
                                   (0.0, -0.26), (0.0, 0.26))):
        p += tbolt("%s_FBB%d" % (name, i),
                   (main_len / 2 + dx, dy, -branch_len + 0.0005), (0, 0, -1),
                   r=0.006, length=0.014)
    # saddle ring around the branch root on the underside
    sad = bm_rect_frame_x(0.0, 0.018, w + 0.010, h + 0.010,
                          w - 0.040, h - 0.040, 0, 0)
    bm_rot(sad, ry=math.radians(90), loc=(main_len / 2, 0, -h / 2 - 0.001))
    p.append(tpart(name + "_Saddle", sad, GALV, 0.0015, 2))
    # branch gussets
    for i, (dx, dy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        p.append(tbox("%s_Gusset%d" % (name, i), 0.055, 0.055, 0.030,
                      (main_len / 2 + dx * (w / 2 - 0.02),
                       dy * (h / 2 - 0.02), -h / 2 - 0.045), GALV, 0.002, 2))
    # main stiffeners
    for i, x in enumerate((0.28, main_len - 0.28)):
        if abs(x - main_len / 2) > 0.16:
            p.append(stiff_ring("%s_Ring%d" % (name, i), x, w, h))
    p.append(tbox(name + "_Label", 0.085, 0.003, 0.038,
                  (0.30, -(w / 2 + 0.004), h / 2 - 0.075), LABEL, 0.0004, 2))
    return join_group(tmp, name, p)


# ---------------------------------------------------------------------------
# transition
# ---------------------------------------------------------------------------

def hollow_transition_body(name, x0, x1, w0, h0, w1, h1, wall=0.004,
                           bevel=0.0015):
    """Outer loft minus an inner cutter, leaving a real open duct bore."""
    outer = tpart(name + "_Outer",
                  bm_solid_loft(x0, x1, w0, h0, w1, h1, 0, 0), GALV, bevel, 2)
    inner = tpart(name + "_Inner",
                  bm_solid_loft(x0 - 0.020, x1 + 0.020,
                                w0 - 2 * wall, h0 - 2 * wall,
                                w1 - 2 * wall, h1 - 2 * wall, 0, 0),
                  GALV, 0.0, 1)
    bpy.ops.object.select_all(action='DESELECT')
    outer.select_set(True)
    bpy.context.view_layer.objects.active = outer
    mod = outer.modifiers.new("P0A1_BOOL", 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.solver = 'EXACT'
    mod.object = inner
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(inner, do_unlink=True)
    return outer


def hero_transition(name, w0, h0, w1, h1, length=0.6):
    p = []
    p.append(hollow_transition_body(name + "_Body", 0.002, length - 0.002,
                                    w0, h0, w1, h1))
    p += flange(name + "_FlangeIn", 0.0, w0, h0, True, (-1, 0, 0), 0.0)
    p.append(tpart(name + "_FlangeOut",
                   bm_rect_frame_x(length - 0.022, length, w1 + 0.082,
                                   h1 + 0.082, w1 - 0.004, h1 - 0.004, 0, 0),
                   GALV, 0.0015, 2))
    p += flange_bolts(tmp, name + "_FBO", 'X', length - 0.0005,
                      (w1 + 0.082) / 2, (h1 + 0.082) / 2, (1, 0, 0),
                      r=0.006, inset=0.05)
    for i, x in enumerate((0.18, 0.42)):
        f = x / length
        ww = w0 + (w1 - w0) * f
        hh = h0 + (h1 - h0) * f
        p.append(tpart("%s_Ring%d" % (name, i),
                       bm_rect_frame_x(x - 0.010, x + 0.010, ww + 0.028,
                                       hh + 0.028, ww - 0.004, hh - 0.004, 0, 0),
                       GALV, 0.0015, 2))
    p.append(tbox(name + "_Label", 0.075, 0.003, 0.034,
                  (0.10, -(w0 / 2 + 0.004), h0 / 2 - 0.070), LABEL, 0.0004, 2))
    return join_group(tmp, name, p)


# ---------------------------------------------------------------------------
# dampers
# ---------------------------------------------------------------------------

def hero_damper(name, w, h, length=0.35, fire=False):
    p = []
    p.append(tpart(name + "_Body",
                   bm_rect_tube_x(0.002, length - 0.002, w, h, 0.005, 0, 0),
                   GALV, 0.0015, 2))
    for lab, x, x0, x1, nrm in (("A", 0.0, 0.0, 0.022, (-1, 0, 0)),
                                 ("B", length, length - 0.022, length,
                                  (1, 0, 0))):
        p.append(tpart("%s_Flange%s" % (name, lab),
                       bm_rect_frame_x(x0, x1, w + 0.082, h + 0.082,
                                       w - 0.004, h - 0.004, 0, 0),
                       GALV, 0.0015, 2))
        p += flange_bolts(tmp, "%s_FB%s" % (name, lab), 'X',
                          x - nrm[0] * 0.0005,
                          (w + 0.082) / 2, (h + 0.082) / 2, nrm,
                          r=0.006, inset=0.05)
    # blade, 35 deg open
    blade = bm_box(0.007, w - 0.025, h - 0.035)
    bm_rot(blade, ry=math.radians(35.0), loc=(length / 2, 0, 0))
    p.append(tpart(name + "_Blade", blade, RED if fire else ALU, 0.0012, 2))
    # axle and bearings
    p.append(tcyl(name + "_Axle", 0.012, w + 0.050,
                  (length / 2, 0, 0), DARK, 'Y', 12, 0.0008, 2))
    for sy, lab in ((-1, "L"), (1, "R")):
        p.append(tbox("%s_Bearing%s" % (name, lab), 0.045, 0.014, 0.115,
                      (length / 2, sy * (w / 2 + 0.014), 0), DARK, 0.0015, 2))
        p += tbolt("%s_BrgBolt%s" % (name, lab),
                   (length / 2, sy * (w / 2 + 0.022), 0), (0, sy, 0),
                   r=0.005, length=0.012)
    if fire:
        # fusible link + inspection port
        p.append(tbox(name + "_Link", 0.055, 0.012, 0.070,
                      (length / 2 + 0.10, -(w / 2 + 0.010), 0.0), BRASS,
                      0.0012, 2))
        p.append(tbox(name + "_InspectFrame", 0.220, 0.010, 0.160,
                      (length / 2, h / 2 + 0.005, 0), GALV, 0.0012, 2))
        p.append(tbox(name + "_InspectDoor", 0.190, 0.008, 0.130,
                      (length / 2, h / 2 + 0.011, 0), ALU, 0.0012, 2))
        for i, (dx, dz) in enumerate(((-0.075, -0.048), (0.075, -0.048),
                                       (0.075, 0.048), (-0.075, 0.048))):
            p += tscrew("%s_IS%d" % (name, i),
                        (length / 2 + dx, h / 2 + 0.016, dz), (0, 0, 1),
                        r=0.003, length=0.0012)
        p.append(tbox(name + "_Tag", 0.070, 0.003, 0.030,
                      (length / 2, -(w / 2 + 0.010), -h / 2 + 0.070),
                      ORANGE, 0.0004, 2))
    else:
        # quadrant / handle on the service side
        p.append(tbox(name + "_Quadrant", 0.095, 0.012, 0.095,
                      (length / 2, -(w / 2 + 0.020), h / 2 + 0.020),
                      BARE, 0.002, 2))
        p.append(tbox(name + "_Handle", 0.085, 0.010, 0.020,
                      (length / 2, -(w / 2 + 0.022), h / 2 + 0.045),
                      DARK, 0.002, 2))
        # actuator on the opposite side
        p.append(tbox(name + "_Actuator", 0.150, 0.105, 0.095,
                      (length / 2, w / 2 + 0.062, 0), DARK, 0.002, 3))
        p.append(tcyl(name + "_Indicator", 0.010, 0.030,
                      (length / 2, w / 2 + 0.120, 0), ORANGE, 'Y', 12,
                      0.0006, 2))
        p.append(tbox(name + "_Label", 0.080, 0.003, 0.035,
                      (length / 2, w / 2 + 0.118, -0.055), LABEL, 0.0004, 2))
        # access panel on top
        p.append(tbox(name + "_Access", 0.200, 0.160, 0.010,
                      (length / 2, 0, h / 2 + 0.005), GALV, 0.0012, 2))
        for i, (dx, dy) in enumerate(((-0.075, -0.055), (0.075, -0.055),
                                       (0.075, 0.055), (-0.075, 0.055))):
            p += tscrew("%s_AS%d" % (name, i),
                        (length / 2 + dx, dy, h / 2 + 0.010), (0, 0, 1),
                        r=0.003, length=0.0012)
    return join_group(tmp, name, p)


# ---------------------------------------------------------------------------
# grille
# ---------------------------------------------------------------------------

def hero_grille(name, w, h):
    p = []
    p.append(tpart(name + "_Neck",
                   bm_rect_tube_x(0.0, 0.130, w, h, 0.003, 0, 0),
                   GALV, 0.0012, 2))
    # face frame: a single closed ring (no corner overlaps)
    p.append(tpart(name + "_Frame",
                   bm_rect_frame_x(0.125, 0.155, w + 0.080, h + 0.080,
                                   w - 0.020, h - 0.020, 0, 0),
                   ALU, 0.0015, 3))
    p.append(tpart(name + "_RearFrame",
                   bm_rect_frame_x(0.108, 0.125, w + 0.020, h + 0.020,
                                   w - 0.020, h - 0.020, 0, 0),
                   GALV, 0.0012, 2))
    # horizontal double-deflection blades
    for i in range(5):
        zz = -h / 2 + 0.040 + i * (h - 0.080) / 4.0
        blade = bm_box(0.013, w - 0.024, 0.043)
        bm_rot(blade, ry=math.radians(18.0 if i % 2 == 0 else -18.0),
               loc=(0.140, 0, zz))
        p.append(tpart("%s_Blade%d" % (name, i), blade, ALU, 0.0012, 2))
    # vertical vanes behind the face
    for i in range(4):
        yy = -w / 2 + 0.030 + i * (w - 0.060) / 3.0
        p.append(tbox("%s_Vane%d" % (name, i), 0.006, 0.012, h - 0.050,
                      (0.118, yy, 0), ALU, 0.0010, 2))
    # opposed-blade damper at the neck
    for i in range(4):
        zz = -h / 2 + 0.020 + i * (h - 0.040) / 3.0
        p.append(tbox("%s_Damper%d" % (name, i), 0.006, w - 0.040, 0.030,
                      (0.085, 0, zz), DARK, 0.0010, 2))
    # corner screws
    for i, (sy, sz) in enumerate(((-w / 2 - 0.030, -h / 2 - 0.030),
                                   (w / 2 + 0.030, -h / 2 - 0.030),
                                   (w / 2 + 0.030, h / 2 + 0.030),
                                   (-w / 2 - 0.030, h / 2 + 0.030))):
        p += tscrew("%s_GS%d" % (name, i), (0.157, sy, sz), (1, 0, 0),
                    r=0.0034, length=0.0014)
    return join_group(tmp, name, p)


# ---------------------------------------------------------------------------
# sleeves
# ---------------------------------------------------------------------------

def hero_sleeve(name, w=0.8, h=0.6, length=0.30):
    p = []
    p.append(tpart(name + "_Sleeve",
                   bm_rect_tube_x(-length / 2, length / 2, w + 0.10,
                                  h + 0.10, 0.006, 0, 0), GALV, 0.0015, 2))
    for lab, x0 in (("A", -length / 2), ("B", length / 2 - 0.010)):
        p.append(tpart("%s_Trim%s" % (name, lab),
                       bm_rect_frame_x(x0, x0 + 0.010, w + 0.150, h + 0.150,
                                       w + 0.098, h + 0.098, 0, 0),
                       GALV, 0.0012, 2))
    p.append(tpart(name + "_Firestop",
                   bm_rect_frame_x(-0.025, 0.025, w + 0.180, h + 0.180,
                                   w + 0.090, h + 0.090, 0, 0),
                   FIRESTOP, 0.0012, 2))
    # trim bolts on both faces
    for lab, x, nrm in (("A", -length / 2 + 0.001, (-1, 0, 0)),
                        ("B", length / 2 - 0.001, (1, 0, 0))):
        for i, (dy, dz) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
            p += tbolt("%s_TB%s%d" % (name, lab, i),
                       (x,
                        dy * (w / 2 + 0.060), dz * (h / 2 + 0.060)),
                       nrm, r=0.005, length=0.012)
    p.append(tbox(name + "_Label", 0.070, 0.003, 0.032,
                  (length / 2 - 0.035, -(w / 2 + 0.055), h / 2 + 0.030),
                  LABEL, 0.0004, 2))
    return join_group(tmp, name, p)


# ---------------------------------------------------------------------------
# shaft access panel
# ---------------------------------------------------------------------------

def hero_shaft(name):
    p = []
    ow, oh = 0.700, 1.300
    bw = 0.040
    z0, z1 = -0.040, 1.260
    # frame bars, butt-jointed (no overlapping corners)
    p.append(tbox(name + "_FrameT", ow, 0.030, bw, (0, 0.015, z1 + bw / 2),
                  GALV, 0.002, 3))
    p.append(tbox(name + "_FrameB", ow, 0.030, bw, (0, 0.015, z0 + bw / 2),
                  GALV, 0.002, 3))
    p.append(tbox(name + "_FrameL", bw, 0.030, z1,
                  (-ow / 2 + bw / 2, 0.015, z1 / 2), GALV, 0.002, 3))
    p.append(tbox(name + "_FrameR", bw, 0.030, z1,
                  (ow / 2 - bw / 2, 0.015, z1 / 2), GALV, 0.002, 3))
    # door, recessed 8 mm behind the frame face
    p.append(tbox(name + "_Door", 0.600, 0.016, 1.200,
                  (0, 0.014, 0.630), GALV, 0.0015, 3))
    # door stiffening ribs (raised off the door face, no coplanar overlap)
    for i, zz in enumerate((0.380, 0.880)):
        p.append(tbox("%s_Rib%d" % (name, i), 0.470, 0.003, 0.020,
                      (0, 0.0240, zz), GALV, 0.0008, 2))
    # ventilation slots
    for i in range(4):
        p.append(tbox("%s_Slot%d" % (name, i), 0.220, 0.002, 0.006,
                      (0, 0.0240, 0.190 + i * 0.024), DARK, 0.0004, 2))
    # hinges
    for i, zz in enumerate((0.230, 0.610, 0.990)):
        p.append(tcyl("%s_Hinge%d" % (name, i), 0.012, 0.085,
                      (-0.302, 0.028, zz), DARK, 'Z', 12, 0.0008, 2))
        p.append(tbox("%s_HingePlate%d" % (name, i), 0.040, 0.008, 0.110,
                      (-0.285, 0.030, zz), GALV, 0.0012, 2))
    # latch / handle / lock
    p.append(tbox(name + "_LatchPlate", 0.055, 0.010, 0.150,
                  (0.270, 0.028, 0.640), GALV, 0.0015, 2))
    p.append(tbox(name + "_Handle", 0.030, 0.020, 0.120,
                  (0.285, 0.042, 0.640), DARK, 0.0015, 2))
    p.append(tcyl(name + "_Lock", 0.018, 0.018,
                  (0.270, 0.040, 0.520), BRASS, 'Y', 16, 0.0008, 2))
    p.append(tbox(name + "_Label", 0.140, 0.003, 0.060,
                  (0.170, 0.024, 1.120), LABEL, 0.0004, 2))
    # frame anchor bolts
    pts = [(-0.310, 1.280), (0.310, 1.280), (-0.310, -0.020),
           (0.310, -0.020), (0.0, 1.280), (0.0, -0.020),
           (-0.310, 0.620), (0.310, 0.620)]
    for i, (x, z) in enumerate(pts):
        p += tbolt("%s_AB%d" % (name, i), (x, 0.030, z), (0, 1, 0),
                   r=0.006, length=0.014)
    return join_group(tmp, name, p)


# ---------------------------------------------------------------------------
# build the new meshes
# ---------------------------------------------------------------------------
BUILD = []
BUILD.append(("SM_SH_HVAC_RECT800x600_L2000",
              hero_duct("SM_SH_HVAC_RECT800x600_L2000", 0.8, 0.6, 2.0)))
BUILD.append(("SM_SH_HVAC_RECT800x600_PEN400",
              hero_duct("SM_SH_HVAC_RECT800x600_PEN400", 0.8, 0.6, 0.4, True)))
BUILD.append(("SM_SH_HVAC_RECT600x400_L2000",
              hero_duct("SM_SH_HVAC_RECT600x400_L2000", 0.6, 0.4, 2.0)))
BUILD.append(("SM_SH_HVAC_RECT600x400_PEN400",
              hero_duct("SM_SH_HVAC_RECT600x400_PEN400", 0.6, 0.4, 0.4, True)))
BUILD.append(("SM_SH_HVAC_TEE_800x600", hero_tee("SM_SH_HVAC_TEE_800x600", 0.8, 0.6)))
BUILD.append(("SM_SH_HVAC_TRANS_800x600_600x400",
              hero_transition("SM_SH_HVAC_TRANS_800x600_600x400",
                              0.8, 0.6, 0.6, 0.4, 0.6)))
BUILD.append(("SM_SH_HVAC_DAMPER_800x600",
              hero_damper("SM_SH_HVAC_DAMPER_800x600", 0.8, 0.6, 0.35, False)))
BUILD.append(("SM_SH_FIREDAMPER_800x600",
              hero_damper("SM_SH_FIREDAMPER_800x600", 0.8, 0.6, 0.35, True)))
BUILD.append(("SM_SH_HVAC_GRILLE_600x400", hero_grille("SM_SH_HVAC_GRILLE_600x400", 0.6, 0.4)))
BUILD.append(("SM_SH_SLEEVE_RECT_800x600", hero_sleeve("SM_SH_SLEEVE_RECT_800x600", 0.8, 0.6)))
BUILD.append(("SM_SH_SHAFT_ACCESS_600x1200", hero_shaft("SM_SH_SHAFT_ACCESS_600x1200")))

# new master: 0.6 x 0.4 rectangular sleeve (built separately)
new_sleeve_ob = hero_sleeve("SM_SH_SLEEVE_RECT_600x400", 0.6, 0.4)

# ---------------------------------------------------------------------------
# replace in place
# ---------------------------------------------------------------------------
report = {}
for target, new_ob in BUILD:
    targets = [o for o in bpy.data.objects
               if o.type == 'MESH' and
               (o.data.name == target or o.data.name.startswith(target + "."))]
    old_datas = []
    for o in targets:
        if o.data not in old_datas:
            old_datas.append(o.data)
    new_data = new_ob.data
    for d in old_datas:
        d.name = "OLD_" + d.name
    new_data.name = target
    for o in targets:
        o.data = new_data
    # update master root tris
    root = bpy.data.objects.get(target + "_ROOT")
    if root:
        root["fm_tris"] = tri_count(new_ob)
        root["fm_generation"] = "VERIFIED_P0A1"
    report[target] = {
        "tris": tri_count(new_ob),
        "verts": len(new_data.vertices),
        "objects_replaced": len(targets),
        "old_datablocks": len(old_datas),
    }
    bpy.data.objects.remove(new_ob, do_unlink=True)
    for d in old_datas:
        if d.users == 0:
            bpy.data.meshes.remove(d)

# create the new 600x400 sleeve master (not a replacement)
root = make_root("SM_SH_SLEEVE_RECT_600x400_ROOT", SERVICES)
finalize_master(root, SERVICES, [new_sleeve_ob],
                location=(1.8, 15.4, 0.0),
                meta={"fm_category": "SERVICE",
                      "fm_ports": json.dumps({"in": [0, 0, 0],
                                              "out": [0, 0, 0]})})
report["SM_SH_SLEEVE_RECT_600x400"] = {
    "tris": tri_count(new_sleeve_ob), "verts": len(new_sleeve_ob.data.vertices),
    "objects_replaced": 0, "old_datablocks": 0, "new_master": True}
if new_sleeve_ob.name in tmp.objects:
    tmp.objects.unlink(new_sleeve_ob)

# remove temp collection (only build leftovers)
for o in list(tmp.objects):
    bpy.data.objects.remove(o, do_unlink=True)
bpy.data.collections.remove(tmp)

# ---------------------------------------------------------------------------
# QA
# ---------------------------------------------------------------------------
def poly_area_2d(pts):
    a = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        a += x1 * y2 - x2 * y1
    return abs(a) * 0.5


def clip_poly(subject, clip):
    out = list(subject)
    for i in range(len(clip)):
        if not out:
            break
        a, b = clip[i], clip[(i + 1) % len(clip)]
        ex, ey = b[0] - a[0], b[1] - a[1]
        inp, out = out, []

        def side(p):
            return ex * (p[1] - a[1]) - ey * (p[0] - a[0])

        for j in range(len(inp)):
            p, q = inp[j], inp[(j + 1) % len(inp)]
            sp, sq = side(p), side(q)
            if sp >= -1e-9:
                out.append(p)
            if (sp > 1e-9 and sq < -1e-9) or (sp < -1e-9 and sq > 1e-9):
                t = sp / (sp - sq)
                out.append((p[0] + (q[0] - p[0]) * t,
                            p[1] + (q[1] - p[1]) * t))
    return out


def coplanar_overlaps(me, tol=0.0004, limit=4000):
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    groups = {}
    for f in bm.faces:
        n = f.normal
        if n.length < 0.5:
            continue
        d = n.dot(f.calc_center_median())
        key = (round(n.x, 2), round(n.y, 2), round(n.z, 2), round(d / tol))
        groups.setdefault(key, []).append(f)
    pairs = []
    for key, fs in groups.items():
        if len(fs) < 2:
            continue
        if len(fs) > 80:
            fs = fs[:80]
        for i in range(len(fs)):
            for j in range(i + 1, len(fs)):
                f1, f2 = fs[i], fs[j]
                if len(pairs) >= limit:
                    break
                bb1 = [f1.verts[0].co.copy(), f1.verts[0].co.copy()]
                bb2 = [f2.verts[0].co.copy(), f2.verts[0].co.copy()]
                for v in f1.verts:
                    bb1[0].x = min(bb1[0].x, v.co.x); bb1[0].y = min(bb1[0].y, v.co.y); bb1[0].z = min(bb1[0].z, v.co.z)
                    bb1[1].x = max(bb1[1].x, v.co.x); bb1[1].y = max(bb1[1].y, v.co.y); bb1[1].z = max(bb1[1].z, v.co.z)
                for v in f2.verts:
                    bb2[0].x = min(bb2[0].x, v.co.x); bb2[0].y = min(bb2[0].y, v.co.y); bb2[0].z = min(bb2[0].z, v.co.z)
                    bb2[1].x = max(bb2[1].x, v.co.x); bb2[1].y = max(bb2[1].y, v.co.y); bb2[1].z = max(bb2[1].z, v.co.z)
                if (bb1[0].x > bb2[1].x - 1e-6 or bb2[0].x > bb1[1].x - 1e-6 or
                    bb1[0].y > bb2[1].y - 1e-6 or bb2[0].y > bb1[1].y - 1e-6 or
                    bb1[0].z > bb2[1].z - 1e-6 or bb2[0].z > bb1[1].z - 1e-6):
                    continue
                n = f1.normal
                ax = max(range(3), key=lambda k: abs(n[k]))
                u, v = [k for k in range(3) if k != ax]
                p1 = [(vv.co[u], vv.co[v]) for vv in f1.verts]
                p2 = [(vv.co[u], vv.co[v]) for vv in f2.verts]
                inter = clip_poly(p1, p2)
                if len(inter) >= 3 and poly_area_2d(inter) > 1e-7:
                    pairs.append((f1.index, f2.index, round(poly_area_2d(inter) * 1e6, 2)))
    bm.free()
    return pairs


qa = {}
QA_TARGETS = [t for t, _ in BUILD] + ["SM_SH_SLEEVE_RECT_600x400"]
for target in QA_TARGETS:
    root = bpy.data.objects.get(target + "_ROOT")
    objs = [o for o in bpy.data.objects if o.type == 'MESH' and
            o.data.name == target]
    if not objs:
        qa[target] = {"pass": False, "errors": ["no mesh objects"]}
        continue
    ob = objs[0]
    me = ob.data
    bm = bmesh.new(); bm.from_mesh(me)
    nonman = sum(1 for e in bm.edges if len(e.link_faces) != 2)
    loose = sum(1 for v in bm.verts if not v.link_faces)
    degen = sum(1 for f in bm.faces if f.calc_area() < 1e-10)
    bm.free()
    overlaps = coplanar_overlaps(me)
    errors = []
    if nonman: errors.append("nonmanifold_edges=%d" % nonman)
    if loose: errors.append("loose_verts=%d" % loose)
    if degen: errors.append("degenerate_faces=%d" % degen)
    if overlaps: errors.append("coplanar_overlaps=%d" % len(overlaps))
    if not me.uv_layers: errors.append("no_uv")
    qa[target] = {
        "pass": not errors,
        "tris": tri_count(ob),
        "verts": len(me.vertices),
        "materials": len(me.materials),
        "nonmanifold_edges": nonman,
        "loose_verts": loose,
        "degenerate_faces": degen,
        "coplanar_overlaps": overlaps[:12],
        "errors": errors,
        "objects": len(objs),
        "bbox": [round(v, 3) for v in ob.dimensions],
    }

# save
blend = bpy.data.filepath
bpy.ops.wm.save_as_mainfile(filepath=blend)
out = "/home/riyo/Documentos/game/docs/fm_shared_p0_qa_p0a1.json"
with open(out, "w") as f:
    json.dump({"build": report, "qa": qa}, f, indent=1)

print("P0A1_DONE")
print("FILE", blend)
print("QA", out)
for k, v in qa.items():
    print("QA", k, "PASS" if v["pass"] else "FAIL", v.get("tris"), v.get("errors"))
