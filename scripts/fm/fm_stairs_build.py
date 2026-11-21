"""Viste las escaleras Z11 (principal), Z12a (E1) y Z12b (E2) del master V06.

Idempotente: reconstruye L1_ART_STAIRS_MAIN / _E1 / _E2. No guarda el .blend,
no toca otras colecciones y no anade luces ni camaras. La geometria de los
peldaños y mesetas del shell se conserva; el arte se limita a acabados,
barandillas, senalizacion, servicios y utileria.
"""

import bpy
import math
import os
import importlib.util

from mathutils import Vector, Matrix

PROJECT = "/home/riyo/Documentos/game"
WH_PATH = os.path.join(PROJECT, "scripts", "fm", "fm_warehouse_build.py")

_spec = importlib.util.spec_from_file_location("wh", WH_PATH)
wh = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wh)
vest = wh.vest

COL_MAIN = "L1_ART_STAIRS_MAIN"
COL_E1 = "L1_ART_STAIRS_E1"
COL_E2 = "L1_ART_STAIRS_E2"
COLS = (COL_MAIN, COL_E1, COL_E2)


def col(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c


def clean():
    for name in COLS:
        c = bpy.data.collections.get(name)
        if c is None:
            continue
        for ob in list(c.objects):
            data = ob.data
            bpy.data.objects.remove(ob, do_unlink=True)
            if data is not None and data.users == 0:
                if isinstance(data, bpy.types.Mesh):
                    bpy.data.meshes.remove(data)
                elif isinstance(data, bpy.types.Curve):
                    bpy.data.curves.remove(data)
        bpy.data.collections.remove(c)


def mat(name, color, rough=0.6, metallic=0.0, emission=None, strength=0.0):
    return wh.mat(name, color, rough, metallic, emission, strength)


def gm(name, fallback="M_FM_Steel_Dark"):
    return wh.get_mat(name, fallback)


def text_sign(name, text, size, loc, normal, material, collection):
    cu = bpy.data.curves.new("TMP_" + name, type="FONT")
    cu.body = text
    cu.size = size
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.extrude = 0.003
    ob = bpy.data.objects.new("TMP_" + name, cu)
    bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    me.materials.append(material)
    ob2 = bpy.data.objects.new(name, me)
    collection.objects.link(ob2)
    up = Vector((0, 0, 1))
    n = Vector(normal).normalized()
    right = up.cross(n).normalized()
    basis = Matrix((right, up, n)).transposed()
    ob2.matrix_world = Matrix.Translation(Vector(loc)) @ basis.to_4x4()
    bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.curves.remove(cu)
    return ob2


# ---------------------------------------------------------------------------
# Materiales
# ---------------------------------------------------------------------------


def materials():
    mat("M_ST_Paint", (0.045, 0.075, 0.072), 0.62, 0.0)
    mat("M_ST_PaintDark", (0.020, 0.032, 0.031), 0.68, 0.0)
    mat("M_ST_Concrete", (0.13, 0.135, 0.13), 0.90, 0.0)
    mat("M_ST_ConcreteDark", (0.07, 0.073, 0.07), 0.94, 0.0)
    mat("M_ST_Yellow", (0.62, 0.42, 0.018), 0.52, 0.0)
    mat("M_ST_Red", (0.48, 0.018, 0.008), 0.48, 0.0)
    mat("M_ST_Orange", (0.60, 0.20, 0.012), 0.50, 0.0)
    mat("M_ST_Rust", (0.16, 0.052, 0.012), 0.88, 0.0)
    mat("M_ST_Rubber", (0.010, 0.012, 0.011), 0.94, 0.0)
    mat("M_ST_White", (0.70, 0.71, 0.66), 0.80, 0.0)
    mat("M_ST_Emissive", (0.55, 0.68, 0.70), 0.30, 0.0,
        emission=(0.78, 0.90, 1.0), strength=3.0)
    mat("M_ST_EmissiveRed", (0.40, 0.02, 0.01), 0.35, 0.0,
        emission=(1.0, 0.05, 0.02), strength=3.0)
    mat("M_ST_SignDark", (0.008, 0.010, 0.009), 0.62, 0.0)
    water = mat("M_ST_Water", (0.035, 0.045, 0.042), 0.08, 0.0)
    bsdf = next(n for n in water.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Alpha"].default_value = 0.55
    water.surface_render_method = "BLENDED"
    mat("M_ST_Tile", (0.11, 0.14, 0.13), 0.48, 0.0)


# ---------------------------------------------------------------------------
# Utilidades de shell
# ---------------------------------------------------------------------------


def ob_aabb(name):
    o = bpy.data.objects.get(name)
    if o is None:
        return None
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return (Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb))),
            Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb))))


def steps(prefix, count=24):
    out = []
    for i in range(count):
        a = ob_aabb("%s%02d" % (prefix, i))
        if a is not None:
            out.append(a)
    return out


def nosing_line(stair_steps):
    a0, b0 = stair_steps[0]
    an, bn = stair_steps[-1]
    return ((a0.x + b0.x) * 0.5, (a0.y + b0.y) * 0.5, b0.z,
            (an.x + bn.x) * 0.5, (an.y + bn.y) * 0.5, bn.z)


def wainscot_x(mb, x, y0, y1, side, paint, cap):
    mid = (y0 + y1) * 0.5
    length = y1 - y0 - 0.10
    mb.add_box((x + side * 0.027, mid, 0.60), (0.045, length, 1.18),
               paint, bevel=0.0)
    mb.add_box((x + side * 0.045, mid, 1.205), (0.075, length + 0.04, 0.045),
               cap, bevel=0.0)


def wainscot_y(mb, y, x0, x1, side, paint, cap):
    mid = (x0 + x1) * 0.5
    length = x1 - x0 - 0.10
    mb.add_box((mid, y + side * 0.027, 0.60), (length, 0.045, 1.18),
               paint, bevel=0.0)
    mb.add_box((mid, y + side * 0.045, 1.205), (length + 0.04, 0.075, 0.045),
               cap, bevel=0.0)


def guardrail(mb, p0, p1, steel, n_posts=5):
    """Barandilla horizontal a z=0 con dos travesaños y postes."""
    x0, y0 = p0
    x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    ang = math.atan2(dy, dx)
    mid = ((x0 + x1) * 0.5, (y0 + y1) * 0.5)
    for h in (0.58, 1.03):
        mb.add_box((mid[0], mid[1], h), (length, 0.045, 0.045), steel,
                   bevel=0.0, rot=(0, 0, ang))
    for i in range(n_posts):
        t = i / float(n_posts - 1)
        x = x0 + dx * t
        y = y0 + dy * t
        mb.add_box((x, y, 0.55), (0.055, 0.055, 1.10), steel, bevel=0.0,
                   rot=(0, 0, ang))


def stair_rails(mb, ss, x_left, x_right, steel):
    (x0, y0, z0, x1, y1, z1) = nosing_line(ss)
    dy = y1 - y0
    dz = z1 - z0
    length = math.hypot(dy, dz)
    ang = math.atan2(dz, dy)
    for x in (x_left, x_right):
        for h in (0.58, 1.03):
            mb.add_box((x, (y0 + y1) * 0.5, (z0 + z1) * 0.5 + h),
                       (0.05, length, 0.05), steel, bevel=0.0,
                       rot=(ang, 0, 0))
        for i in range(0, len(ss), 4):
            a, b = ss[i]
            y = (a.y + b.y) * 0.5
            z = b.z
            mb.add_box((x, y, z + 0.52), (0.04, 0.04, 1.04), steel,
                       bevel=0.0)


def step_nosings(mb, ss, yellow, ascending, x_pad=0.04):
    for a, b in ss:
        if ascending:
            y = b.y - 0.025
        else:
            y = a.y + 0.025
        mb.add_box(((a.x + b.x) * 0.5, y, b.z + 0.010),
                   (b.x - a.x - x_pad * 2.0, 0.05, 0.012), yellow,
                   bevel=0.0)


def ceiling_run(mb, x, y0, y1, z, radius, material, count=1):
    for i in range(count):
        mb.add_cyl((x, (y0 + y1) * 0.5, z - i * 0.22), radius,
                   abs(y1 - y0), material, axis="Y", segments=10,
                   bevel=0.0)


def light_panel(mb, x, y, z, mat_light, sx=0.55, sy=0.16):
    mb.add_box((x, y, z), (sx, sy, 0.055), mat_light, bevel=0.0)
    mb.add_box((x, y, z + 0.06), (sx + 0.10, sy + 0.10, 0.05),
               gm("M_FM_Metal_Panel"), bevel=0.0)


def extinguisher(collection, name, x, y, z):
    mb = vest.MeshBuilder(name)
    mb.add_cyl((x, y, z + 0.25), 0.075, 0.50, gm("M_FM_Industrial_Red"),
               axis="Z", segments=12)
    mb.add_cyl((x, y, z + 0.54), 0.032, 0.09, gm("M_FM_Steel_Dark"),
               axis="Z", segments=10)
    mb.add_box((x, y - 0.065, z + 0.50), (0.07, 0.035, 0.08),
               gm("M_ST_SignDark"), bevel=0.0)
    mb.add_box((x, y, z + 0.61), (0.10, 0.05, 0.035),
               gm("M_FM_Steel_Dark"), bevel=0.0)
    mb.build(collection)


def wet_sign(mb, x, y, z, yellow, dark):
    for side in (-1, 1):
        mb.add_box((x + side * 0.12, y, z + 0.30), (0.035, 0.32, 0.58),
                   yellow, bevel=0.0, rot=(0, 0.18 * side, 0))
    mb.add_box((x, y, z + 0.01), (0.42, 0.34, 0.02), dark, bevel=0.0)


# ---------------------------------------------------------------------------
# Núcleo principal Z11
# ---------------------------------------------------------------------------


def build_main():
    c = col(COL_MAIN)
    paint = gm("M_ST_Paint")
    cap = gm("M_ST_PaintDark")
    steel = gm("M_WH_Galv")
    yellow = gm("M_ST_Yellow")
    concrete = gm("M_ST_Concrete")

    ss = steps("SM_L1_Stair_Main_Step_")

    mb = vest.MeshBuilder("ST_Main_StepNosings_TRIM")
    step_nosings(mb, ss, yellow, ascending=False)
    mb.build(c)

    mb = vest.MeshBuilder("ST_Main_Handrails_TRIM")
    stair_rails(mb, ss, -3.93, -0.07, steel)
    mb.build(c)

    mb = vest.MeshBuilder("ST_Main_Guardrails_TRIM")
    guardrail(mb, (-3.97, -44.0), (-0.03, -44.0), steel, 3)
    guardrail(mb, (-3.97, -44.0), (-3.97, -32.2), steel, 5)
    guardrail(mb, (-0.03, -44.0), (-0.03, -32.2), steel, 5)
    mb.build(c)

    mb = vest.MeshBuilder("ST_Main_Wainscot_TRIM")
    wainscot_x(mb, -11.85, -49.6, -33.0, +1, paint, cap)
    wainscot_x(mb, -11.85, -31.2, -30.2, +1, paint, cap)
    wainscot_x(mb, 7.85, -49.6, -30.4, -1, paint, cap)
    wainscot_y(mb, -49.85, -11.6, 7.6, +1, paint, cap)
    wainscot_y(mb, -29.85, -11.6, -4.2, -1, paint, cap)
    wainscot_y(mb, -29.85, 2.2, 7.6, -1, paint, cap)
    wainscot_x(mb, -3.85, -29.3, -20.8, +1, paint, cap)
    wainscot_x(mb, -3.85, -18.2, -4.4, +1, paint, cap)
    wainscot_x(mb, 1.88, -29.3, -20.8, -1, paint, cap)
    wainscot_x(mb, 1.88, -18.2, -4.4, -1, paint, cap)
    mb.build(c)

    mb = vest.MeshBuilder("ST_Main_Ceiling_CABLE")
    ceiling_run(mb, 5.9, -49.4, -30.6, 6.35, 0.075, gm("M_FM_Steel_Dark"), 1)
    ceiling_run(mb, 6.35, -49.4, -30.6, 6.13, 0.055, gm("M_ST_Rust"), 1)
    mb.add_box((7.25, -40.0, 6.02), (0.52, 18.8, 0.07), steel, bevel=0.0)
    for i in range(6):
        mb.add_box((7.25, -48.6 + i * 3.4, 5.95), (0.50, 0.035, 0.08),
                   gm("M_ST_Rubber"), bevel=0.0)
    mb.add_box((7.30, -40.0, 6.075), (0.18, 18.4, 0.025), gm("M_ST_Red"),
               bevel=0.0)
    mb.add_box((7.10, -40.0, 6.075), (0.10, 18.4, 0.025), gm("M_FM_Plastic_Blue"),
               bevel=0.0)
    mb.add_cyl((-11.45, -40.0, 6.30), 0.065, 19.2, gm("M_ST_Orange"),
               axis="Y", segments=10)
    for y in (-48.0, -43.0, -38.0, -33.0):
        mb.add_box((5.9, y, 6.70), (0.04, 0.04, 0.56), steel, bevel=0.0)
        mb.add_box((6.35, y, 6.59), (0.04, 0.04, 0.82), steel, bevel=0.0)
        mb.add_box((7.25, y, 6.50), (0.05, 0.05, 1.00), steel, bevel=0.0)
        mb.add_box((-11.45, y, 6.67), (0.04, 0.04, 0.63), steel, bevel=0.0)
    mb.build(c)

    mb = vest.MeshBuilder("ST_Main_ConnectorServices_CABLE")
    ceiling_run(mb, -1.0, -29.4, -4.4, 3.92, 0.045, gm("M_WH_Galv"), 1)
    # Transición al HVAC del corredor: codo reductor y collar de damper.
    mb.add_box((-1.0, -3.15, 3.55), (0.70, 2.50, 0.55),
               gm("M_WH_Galv"), bevel=0.003)
    mb.add_box((-1.0, -3.15, 3.89), (0.30, 0.34, 0.18),
               gm("M_WH_Galv"), bevel=0.002)
    mb.add_box((-1.0, -4.12, 3.55), (0.82, 0.12, 0.68),
               gm("M_FM_Steel_Dark"), bevel=0.0)
    for y in (-27.0, -21.0, -15.0, -9.0):
        mb.add_box((-1.0, y, 4.04), (0.04, 0.04, 0.28), steel, bevel=0.0)
    for i in range(4):
        mb.add_box((-1.0, -27.0 + i * 6.0, 3.80), (0.55, 0.12, 0.045),
                   gm("M_ST_White"), bevel=0.0)
    mb.build(c)

    mb = vest.MeshBuilder("ST_Main_Lights_LIGHT")
    for i in range(4):
        light_panel(mb, 1.0, -46.0 + i * 5.0, 6.05, gm("M_ST_Emissive"))
    for i in range(4):
        light_panel(mb, -1.0, -27.0 + i * 6.0, 3.78, gm("M_ST_Emissive"),
                    sx=0.60, sy=0.16)
    mb.build(c)

    mb = vest.MeshBuilder("ST_Main_FloorLines_FLOOR_LINE")
    for x in (-4.06, -0.94):
        mb.add_box((x, -38.10, 0.012), (0.055, 12.0, 0.004), yellow,
                   bevel=0.0)
    mb.build(c)

    mb = vest.MeshBuilder("ST_Main_Decals_DECAL")
    for i in range(5):
        mb.add_box((-11.845, -47.0 + i * 3.1, 1.55 + (i % 2) * 0.4),
                   (0.006, 0.22, 0.9), gm("M_ST_Rust"), bevel=0.0)
    mb.add_box((-7.0, -49.845, 0.45), (1.5, 0.006, 0.55), gm("M_ST_Rust"),
               bevel=0.0)
    mb.build(c)

    mb = vest.MeshBuilder("ST_Main_Puddle_DIS_WATER")
    for i, (x, y, sx, sy) in enumerate(((-2.0, -43.3, 1.5, 1.0),
                                        (-0.8, -41.6, 0.8, 0.7))):
        mb.add_plane((x, y, -4.485 + i * 0.003), sx, sy, gm("M_ST_Water"))
    mb.build(c)

    mb = vest.MeshBuilder("ST_Main_Props")
    wet_sign(mb, -3.45, -43.0, -4.49, yellow, gm("M_ST_PaintDark"))
    mb.add_cyl((-3.55, -42.2, -4.33), 0.17, 0.34, gm("M_FM_Plastic_Blue"),
               axis="Z", segments=12)
    mb.build(c)
    extinguisher(c, "ST_Main_Extinguisher", 7.55, -48.6, 0.0)
    extinguisher(c, "ST_Main_ExtinguisherTop", 7.55, -31.2, 0.0)

    text_sign("ST_Main_SignName_SIGN", "ESCALERAS PRINCIPALES", 0.46,
              (0.0, -49.79, 2.95), (0, 1, 0), gm("M_ST_White"), c)
    text_sign("ST_Main_SignLevel_SIGN", "NIVEL 1", 0.34,
              (4.8, -49.79, 2.30), (0, 1, 0), gm("M_ST_White"), c)
    text_sign("ST_Main_SignExit_SIGN", "SALIDA", 0.30,
              (-0.25, -41.2, -3.10), (-1, 0, 0), gm("M_ST_White"), c)
    text_sign("ST_Main_SignBasement_SIGN", "NIVEL -1", 0.24,
              (-3.55, -44.4, -2.60), (0, 1, 0), gm("M_ST_White"), c)
    text_sign("ST_Main_SignNoBlock_SIGN", "NO BLOQUEAR", 0.19,
              (-3.80, -25.0, 2.10), (1, 0, 0), gm("M_ST_White"), c)


# ---------------------------------------------------------------------------
# Escaleras de emergencia E1 / E2
# ---------------------------------------------------------------------------


def build_emergency(key, prefix, col_name, landing, walls, sign_name,
                    x0, x1, y0, y1, pipe_x_a, pipe_x_b,
                    tray_x, link_wall_x, link_y, link_z):
    c = col(col_name)
    paint = gm("M_ST_Paint")
    cap = gm("M_ST_PaintDark")
    steel = gm("M_WH_Galv")
    yellow = gm("M_ST_Yellow")
    ss = steps(prefix)
    lower_z = -4.5

    mb = vest.MeshBuilder("ST_%s_StepNosings_TRIM" % key)
    step_nosings(mb, ss, yellow, ascending=True)
    mb.build(c)

    mb = vest.MeshBuilder("ST_%s_Handrails_TRIM" % key)
    stair_rails(mb, ss, ss[0][0].x + 0.08, ss[0][1].x - 0.08, steel)
    mb.build(c)

    mb = vest.MeshBuilder("ST_%s_Guardrails_TRIM" % key)
    hx0 = ss[0][0].x - 0.20
    hx1 = ss[0][1].x + 0.20
    y_top = ss[0][0].y - 0.2
    guardrail(mb, (hx0, y_top), (hx0, landing[1] - 0.30), steel, 5)
    guardrail(mb, (hx1, y_top), (hx1, landing[1] - 0.30), steel, 5)
    mb.build(c)

    mb = vest.MeshBuilder("ST_%s_Wainscot_TRIM" % key)
    for spec in walls:
        if spec[0] == "x":
            wainscot_x(mb, spec[1], spec[2], spec[3], spec[4], paint, cap)
        else:
            wainscot_y(mb, spec[1], spec[2], spec[3], spec[4], paint, cap)
    mb.build(c)

    mb = vest.MeshBuilder("ST_%s_Ceiling_CABLE" % key)
    ceiling_run(mb, pipe_x_a, y0 + 0.5, y1 - 0.5, 5.55, 0.065,
                gm("M_ST_Red"), 1)
    ceiling_run(mb, pipe_x_b, y0 + 0.5, y1 - 0.5, 5.55, 0.045,
                gm("M_ST_Rust"), 1)
    for y in (y0 + 3.0, y0 + 9.0, y1 - 3.0):
        mb.add_box((pipe_x_a, y, 5.79), (0.04, 0.04, 0.40), steel, bevel=0.0)
        mb.add_box((pipe_x_b, y, 5.79), (0.04, 0.04, 0.40), steel, bevel=0.0)
    mb.build(c)

    # Bandeja de cables: entra desde el edificio y recorre la caja de escalera.
    mb = vest.MeshBuilder("ST_%s_TrayLink_CABLE" % key)
    tray_mat = gm("M_WH_Galv")
    cable_mat = gm("M_VEST_Black")
    wh.tray_segment(mb, tray_mat, tray_x, y0 + 0.25, tray_x, y1 - 0.25,
                    link_z)
    bridge_x0 = link_wall_x + 0.02
    bridge_x1 = tray_x - 0.27
    wh.tray_segment(mb, tray_mat, bridge_x0, link_y, bridge_x1, link_y,
                    link_z)
    for dx in (-0.10, 0.0, 0.10):
        mb.add_cyl((tray_x + dx, (y0 + y1) * 0.5, link_z + 0.06),
                   0.018, y1 - y0 - 0.60, cable_mat, axis="Y", segments=8)
    for dy in (-0.10, 0.0, 0.10):
        mb.add_cyl(((bridge_x0 + bridge_x1) * 0.5, link_y + dy,
                    link_z + 0.06), 0.018, bridge_x1 - bridge_x0 - 0.20,
                   cable_mat, axis="X", segments=8)
    for y in (y0 + 1.0, y0 + 4.0, y0 + 8.0, y1 - 4.0, y1 - 1.0):
        wh.tray_hanger(mb, tray_mat, tray_x, y, link_z, 5.99)
    for x in (bridge_x0 + 0.80, bridge_x1 - 0.80):
        wh.tray_hanger(mb, tray_mat, x, link_y, link_z, 5.99)
    wh.tray_sleeve(mb, tray_mat, link_wall_x, link_y, link_z)
    mb.build(c)

    mb = vest.MeshBuilder("ST_%s_Lights_LIGHT" % key)
    for y in (y0 + 5.0, y1 - 4.0):
        light_panel(mb, (x0 + x1) * 0.5, y, 5.35,
                    gm("M_ST_Emissive"), sx=0.20, sy=0.64)
    mb.build(c)

    mb = vest.MeshBuilder("ST_%s_FloorLines_FLOOR_LINE" % key)
    cx = (ss[0][0].x + ss[0][1].x) * 0.5
    mb.add_box((cx, ss[0][0].y - 0.6, 0.014),
               (2.0, 0.055, 0.004), yellow, bevel=0.0)
    mb.add_box((cx, landing[1] - 0.35, 0.014),
               (2.0, 0.055, 0.004), yellow, bevel=0.0)
    mb.build(c)

    mb = vest.MeshBuilder("ST_%s_Decals_DECAL" % key)
    for i in range(3):
        mb.add_box((x0 + 2.2 + i * 2.0, y0 + 0.17, 1.55 + (i % 2) * 0.35),
                   (0.20, 0.006, 0.85), gm("M_ST_Rust"), bevel=0.0)
    mb.build(c)

    mb = vest.MeshBuilder("ST_%s_Puddle_DIS_WATER" % key)
    mb.add_plane((landing[0] + 0.3, landing[1] - 1.4, lower_z + 0.015),
                 1.2, 0.9, gm("M_ST_Water"))
    mb.build(c)

    extinguisher(c, "ST_%s_Extinguisher" % key, x1 - 0.35, y0 + 1.4, 0.0)

    text_sign("ST_%s_SignName_SIGN" % key, sign_name, 0.30,
              ((x0 + x1) * 0.5, y0 + 0.22, 2.65), (0, 1, 0),
              gm("M_ST_White"), c)
    text_sign("ST_%s_SignExit_SIGN" % key, "SALIDA", 0.26,
              (x1 - 0.22, (y0 + y1) * 0.5, 2.50), (-1, 0, 0),
              gm("M_ST_White"), c)
    text_sign("ST_%s_SignEmergency_SIGN" % key, "EMERGENCIA", 0.20,
              ((x0 + x1) * 0.5, y1 - 0.25, 2.65), (0, -1, 0),
              gm("M_ST_EmissiveRed"), c)


def build_e1():
    build_emergency(
        "E1", "SM_L1_Stair_E1_Step_", COL_E1, (115.0, 26.0),
        [("x", 119.85, 8.4, 25.6, -1),
         ("y", 25.85, 110.4, 119.6, -1),
         ("y", 8.15, 110.4, 119.6, +1)],
        "SALIDA E1", 110.0, 120.0, 8.0, 26.0, 118.9, 115.1,
        115.0, 110.0, 12.0, 4.50)


def build_e2():
    build_emergency(
        "E2", "SM_L1_Stair_E2_Step_", COL_E2, (117.0, -26.0),
        [("x", 121.85, -43.6, -26.4, -1),
         ("y", -26.15, 112.4, 121.6, -1),
         ("y", -43.85, 112.4, 121.6, +1)],
        "SALIDA E2", 112.0, 122.0, -44.0, -26.0, 120.9, 117.1,
        117.0, 112.0, -38.0, 4.55)


# ---------------------------------------------------------------------------


def build():
    clean()
    materials()
    build_main()
    build_e1()
    build_e2()
    for name in COLS:
        c = col(name)
        nt = sum(len(o.data.polygons) for o in c.objects if o.type == "MESH")
        print("STAIRS_BUILD", name, "objects=%d" % len(c.objects),
              "tris=%d" % (nt * 2))


if __name__ == "__main__":
    build()
