"""Viste Mantenimiento (Z07) en el master V06.

Idempotente: reconstruye L1_ART_MAINTENANCE. No guarda el .blend, no toca
otras colecciones y no anade luces ni camaras. Identidad: planta tecnica /
sala de maquinas (calderas, bombas, tanques, cuadros electricos, taller).

Uso desde Blender MCP:
    exec(compile(open("scripts/fm/fm_maintenance_build.py").read(),
                 "fm_maintenance_build.py", "exec"))
"""

import bpy
import math
import os
import importlib.util

from mathutils import Vector, Matrix

PROJECT = "/home/riyo/Documentos/game"
COL_NAME = "L1_ART_MAINTENANCE"
WAREHOUSE_PATH = os.path.join(PROJECT, "scripts", "fm", "fm_warehouse_build.py")

_spec = importlib.util.spec_from_file_location("wh", WAREHOUSE_PATH)
wh = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wh)
wh.COL_NAME = COL_NAME
vest = wh.vest

# Caras interiores de la sala (Blender).
X0, X1 = 56.15, 111.85
Y0, Y1 = -47.85, -7.85
ZTOP = 5.90


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------


def col():
    c = bpy.data.collections.get(COL_NAME)
    if c is None:
        c = bpy.data.collections.new(COL_NAME)
        bpy.context.scene.collection.children.link(c)
    return c


def clean():
    c = bpy.data.collections.get(COL_NAME)
    if c is None:
        return
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


def get_mat(name, fallback="M_FM_Steel_Dark"):
    return wh.get_mat(name, fallback)


def solid(name, fallback, color=None, rough=None, metallic=None):
    m = bpy.data.materials.get(name)
    if m is not None:
        return m
    if color is None:
        return get_mat(fallback)
    return mat(name, color, rough if rough is not None else 0.5,
               metallic if metallic is not None else 0.0)


def text(name, body, size, loc, normal, material, extrude=0.002):
    return wh.text_sign(name, body, size, loc, normal, material, extrude)


# ---------------------------------------------------------------------------
# Materiales
# ---------------------------------------------------------------------------


def materials():
    mat("M_MT_BoilerGreen", (0.038, 0.085, 0.064), 0.46, 0.18)
    mat("M_MT_BoilerDark", (0.018, 0.022, 0.020), 0.52, 0.55)
    mat("M_MT_Insulation", (0.50, 0.53, 0.51), 0.84, 0.05)
    mat("M_MT_PipeSteam", (0.34, 0.030, 0.018), 0.52, 0.35)
    mat("M_MT_PipeWater", (0.020, 0.085, 0.190), 0.46, 0.40)
    mat("M_MT_PipeCond", (0.040, 0.165, 0.075), 0.52, 0.35)
    mat("M_MT_PipeAir", (0.58, 0.400, 0.020), 0.46, 0.35)
    mat("M_MT_PipeGas", (0.52, 0.30, 0.02), 0.48, 0.35)
    mat("M_MT_Yellow", (0.62, 0.42, 0.018), 0.52, 0.0)
    mat("M_MT_LineYellow", (0.60, 0.45, 0.030), 0.68, 0.0)
    mat("M_MT_Rubber", (0.008, 0.009, 0.009), 0.92, 0.0)
    mat("M_MT_GaugeFace", (0.80, 0.80, 0.74), 0.30, 0.0)
    mat("M_MT_Needle", (0.55, 0.020, 0.012), 0.40, 0.0)
    mat("M_MT_EmissiveWhite", (0.78, 0.86, 0.92), 0.28, 0.0,
        emission=(0.80, 0.92, 1.00), strength=5.0)
    mat("M_MT_EmissiveRed", (0.45, 0.010, 0.006), 0.32, 0.0,
        emission=(1.00, 0.030, 0.015), strength=4.0)
    mat("M_MT_Screen", (0.010, 0.075, 0.070), 0.28, 0.0,
        emission=(0.06, 0.55, 0.48), strength=1.6)
    mat("M_MT_TextLight", (0.78, 0.80, 0.72), 0.74, 0.0)
    mat("M_MT_TextDark", (0.010, 0.012, 0.010), 0.66, 0.0)
    mat("M_MT_Rust", (0.095, 0.030, 0.010), 0.90, 0.0)
    mat("M_MT_Soot", (0.008, 0.008, 0.007), 0.96, 0.0)
    mat("M_MT_Glove", (0.115, 0.075, 0.035), 0.88, 0.0)
    mat("M_MT_Concrete", (0.30, 0.30, 0.27), 0.88, 0.0)


# ---------------------------------------------------------------------------
# Primitivas de tuberia y detalle
# ---------------------------------------------------------------------------


def px(mb, x0, x1, y, z, r, material, segments=16):
    if abs(x1 - x0) < 1e-6:
        return
    mb.add_cyl(((x0 + x1) * 0.5, y, z), r, abs(x1 - x0), material,
               axis="X", segments=segments)


def py(mb, y0, y1, x, z, r, material, segments=16):
    if abs(y1 - y0) < 1e-6:
        return
    mb.add_cyl((x, (y0 + y1) * 0.5, z), r, abs(y1 - y0), material,
               axis="Y", segments=segments)


def pz(mb, x, y, z0, z1, r, material, segments=16):
    if abs(z1 - z0) < 1e-6:
        return
    mb.add_cyl((x, y, (z0 + z1) * 0.5), r, abs(z1 - z0), material,
               axis="Z", segments=segments)


def flange(mb, x, y, z, r, axis, material=None):
    mb.add_cyl((x, y, z), r * 1.45, 0.075,
               material or get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv"),
               axis=axis, segments=20)


def valve(mb, x, y, z, r, axis="X", body=None, wheel=None):
    body = body or get_mat("M_FM_Steel_Dark")
    wheel = wheel or get_mat("M_FM_Safety_Yellow")
    mb.add_cyl((x, y, z), r * 1.05, r * 2.5, body, axis=axis, segments=16)
    flange(mb, x - r * 1.45, y, z, r, axis)
    flange(mb, x + r * 1.45, y, z, r, axis)
    pz(mb, x, y, z + r * 0.9, z + r * 2.1, r * 0.16,
       get_mat("M_FM_Steel_Dark"), 10)
    wz = z + r * 2.2
    mb.add_cyl((x, y, wz), r * 2.0, 0.030, wheel, axis="Z", segments=20)
    for i in range(4):
        a = i * math.pi * 0.5
        mb.add_box((x + math.cos(a) * r, y + math.sin(a) * r, wz),
                   (r * 1.9, 0.030, 0.020), wheel,
                   rot=(0, 0, a))
    mb.add_cyl((x, y, wz + 0.020), r * 0.30, 0.055, body, axis="Z",
               segments=12)


def gauge(mb, x, y, z, axis="Y", r=0.085, face=None):
    face = face or get_mat("M_MT_GaugeFace")
    galv = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    mb.add_cyl((x, y, z), r, 0.060, galv, axis=axis, segments=20)
    if axis == "Y":
        mb.add_cyl((x, y - 0.036, z), r * 0.82, 0.020, face,
                   axis="Y", segments=20)
        mb.add_box((x, y - 0.049, z), (0.008, 0.006, r * 1.1),
                   get_mat("M_MT_Needle"))
    elif axis == "X":
        mb.add_cyl((x - 0.036, y, z), r * 0.82, 0.020, face,
                   axis="X", segments=20)
        mb.add_box((x - 0.049, y, z), (0.006, 0.008, r * 1.1),
                   get_mat("M_MT_Needle"))
    else:
        mb.add_cyl((x, y, z + 0.036), r * 0.82, 0.020, face,
                   axis="Z", segments=20)


def plate(mb, x, y, z, w, h, axis="Y", label=None):
    dark = get_mat("M_FM_Steel_Dark")
    label = label or get_mat("M_FM_Label_White", "M_MT_GaugeFace")
    if axis == "Y":
        mb.add_box((x, y, z), (w + 0.035, 0.020, h + 0.030), dark,
                   bevel=0.002)
        mb.add_box((x, y - 0.013, z), (w, 0.006, h), label, bevel=0.0)
    else:
        mb.add_box((x, y, z), (0.020, w + 0.035, h + 0.030), dark,
                   bevel=0.002)
        mb.add_box((x - 0.013, y, z), (0.006, w, h), label, bevel=0.0)


def ladder_x(mb, x, y, z0, z1, width, material=None):
    material = material or get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    h = z1 - z0
    for sy in (-1, 1):
        mb.add_box((x, y + sy * width * 0.5, z0 + h * 0.5),
                   (0.045, 0.045, h), material, bevel=0.003)
    z = z0 + 0.22
    while z < z1 - 0.12:
        mb.add_box((x, y, z), (0.035, width, 0.030), material,
                   bevel=0.0)
        z += 0.28


def ladder_y(mb, x, y, z0, z1, width, material=None):
    material = material or get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    h = z1 - z0
    for sx in (-1, 1):
        mb.add_box((x + sx * width * 0.5, y, z0 + h * 0.5),
                   (0.045, 0.045, h), material, bevel=0.003)
    z = z0 + 0.22
    while z < z1 - 0.12:
        mb.add_box((x, y, z), (width, 0.035, 0.030), material,
                   bevel=0.0)
        z += 0.28


def bolts_y(mb, x, y, z, radius, count=8, size=0.018):
    galv = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    for i in range(count):
        a = math.tau * i / count
        mb.add_cyl((x + math.cos(a) * radius, y, z + math.sin(a) * radius),
                   size, 0.030, galv, axis="Y", segments=8)


def bolts_x(mb, x, y, z, radius, count=8, size=0.018):
    galv = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    for i in range(count):
        a = math.tau * i / count
        mb.add_cyl((x, y + math.cos(a) * radius, z + math.sin(a) * radius),
                   size, 0.030, galv, axis="X", segments=8)


# ---------------------------------------------------------------------------
# Calderas
# ---------------------------------------------------------------------------


def boiler(name, cx, cy):
    f = wh.Frame(cx, cy, math.radians(-90))
    mb = vest.MeshBuilder(name)
    green = get_mat("M_MT_BoilerGreen")
    dark = get_mat("M_MT_BoilerDark")
    galv = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    conc = get_mat("M_FM_Concrete_Wall", "M_MT_Concrete")

    f.box(mb, 0, 0, 0.129, 2.70, 2.70, 0.250, conc, bevel=0.018)
    f.cyl(mb, 0, 0, 1.550, 1.05, 2.60, green, axis="Z", segments=32)
    f.cyl(mb, 0, 0, 0.340, 1.08, 0.160, dark, axis="Z", segments=32)
    f.cyl(mb, 0, 0, 2.900, 1.02, 0.120, dark, axis="Z", segments=32)
    f.cyl(mb, 0, 0, 3.040, 0.82, 0.180, green, axis="Z", segments=32)
    f.cyl(mb, 0, 0, 3.190, 0.56, 0.160, dark, axis="Z", segments=24)
    for z in (0.95, 1.65, 2.35):
        f.cyl(mb, 0, 0, z, 1.068, 0.075, dark, axis="Z", segments=32)

    # Puerta de registro y bisagras.
    f.box(mb, 0, -1.035, 1.55, 0.70, 0.090, 0.92, dark, bevel=0.006)
    f.box(mb, 0, -1.085, 1.55, 0.56, 0.020, 0.78, green, bevel=0.004)
    for z in (1.20, 1.90):
        f.cyl(mb, -0.380, -1.095, z, 0.038, 0.170, galv, axis="Z",
              segments=12)
        f.box(mb, -0.380, -1.080, z + 0.10, 0.090, 0.040, 0.030, galv)
    f.box(mb, 0.270, -1.115, 1.55, 0.160, 0.055, 0.035, galv, bevel=0.004)
    for dz in (-0.05, 0.05):
        f.box(mb, 0.205, -1.100, 1.55 + dz, 0.060, 0.030, 0.020, galv)

    # Placa y panel de instrumentos.
    f.box(mb, 0, -1.070, 2.62, 0.78, 0.040, 0.34, dark, bevel=0.004)
    for dx in (-0.20, 0.20):
        gauge(mb, f.p(dx, -1.092)[0], f.p(dx, -1.092)[1], 2.62,
              axis="Y", r=0.075)
    f.box(mb, 0, -1.060, 2.28, 0.55, 0.018, 0.15,
          get_mat("M_FM_Label_White", "M_MT_GaugeFace"))

    # Boca de inspeccion.
    f.cyl(mb, 0, -1.005, 2.98, 0.15, 0.070, galv, axis="Y", segments=20)
    f.cyl(mb, 0, -1.048, 2.98, 0.115, 0.015,
          get_mat("M_MT_EmissiveRed"), axis="Y", segments=20)

    # Chimenea y salida de vapor.
    f.cyl(mb, 0.45, 0.55, 4.50, 0.23, 2.50, galv, axis="Z", segments=24)
    f.cyl(mb, 0.45, 0.55, 5.76, 0.30, 0.10, dark, axis="Z", segments=24)
    for z in (4.10, 4.95):
        f.cyl(mb, 0.45, 0.55, z, 0.29, 0.070, dark, axis="Z", segments=24)
    f.box(mb, 0.45, 0.55, 4.04, 0.40, 0.40, 0.10, dark, bevel=0.006)

    f.cyl(mb, -0.34, 0.32, 3.62, 0.13, 0.55, galv, axis="Z", segments=16)
    f.cyl(mb, -0.34, 0.32, 3.95, 0.20, 0.08, dark, axis="Z", segments=16)
    pz(mb, f.p(-0.34, 0.32)[0], f.p(-0.34, 0.32)[1], 3.90, 4.75,
       0.13, get_mat("M_MT_PipeSteam"), 16)
    valve(mb, f.p(-0.34, 0.32)[0], f.p(-0.34, 0.32)[1], 4.30, 0.13,
          axis="Z", wheel=get_mat("M_VEST_Red"))

    # Valvula de seguridad.
    f.cyl(mb, 0.05, 0.05, 3.46, 0.11, 0.36, galv, axis="Z", segments=12)
    f.cyl(mb, 0.05, 0.05, 3.66, 0.18, 0.05, dark, axis="Z", segments=12)

    # Escalera de servicio en el lado norte.
    ladder_x(mb, cx, cy - 1.30, 0.42, 3.18, 0.42)
    for z in (0.65, 1.65, 2.65):
        f.box(mb, 0, -1.18, z, 0.50, 0.24, 0.035, galv)

    mb.build(col())


# ---------------------------------------------------------------------------
# Bombas, tanques, AHU, compresores
# ---------------------------------------------------------------------------


def pump_skid(name, cx, cy, rz=0.0):
    f = wh.Frame(cx, cy, rz)
    mb = vest.MeshBuilder(name)
    dark = get_mat("M_FM_Steel_Dark")
    galv = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    blue = get_mat("M_MT_PipeWater")
    conc = get_mat("M_FM_Concrete_Wall", "M_MT_Concrete")

    f.box(mb, 0, 0, 0.094, 3.35, 1.55, 0.180, conc, bevel=0.012)
    for sy in (-0.56, 0.56):
        f.box(mb, 0, sy, 0.215, 3.10, 0.14, 0.120, galv, bevel=0.004)
    for lx in (-1.40, 0.0, 1.40):
        f.box(mb, lx, 0, 0.235, 0.14, 1.20, 0.110, galv, bevel=0.004)

    for sx in (-0.82, 0.82):
        f.cyl(mb, sx, 0, 0.560, 0.32, 0.40, blue, axis="X", segments=24)
        f.cyl(mb, sx + 0.46, 0, 0.560, 0.25, 0.72, dark, axis="X",
              segments=20)
        f.box(mb, sx + 0.18, 0, 0.560, 0.20, 0.46, 0.46, galv, bevel=0.006)
        f.cyl(mb, sx - 0.34, 0, 0.680, 0.13, 0.30, galv, axis="X",
              segments=16)
        f.box(mb, sx, 0, 0.280, 0.62, 0.42, 0.10, dark, bevel=0.004)
    py(mb, cy - 0.95, cy + 0.95, cx - 0.82, 0.56, 0.16, blue, 20)
    py(mb, cy - 0.95, cy + 0.95, cx + 0.82, 0.56, 0.16, blue, 20)
    px(mb, cx - 1.55, cx + 1.55, cy + 0.95, 0.56, 0.16, blue, 20)
    px(mb, cx - 1.55, cx + 1.55, cy - 0.95, 0.56, 0.16, blue, 20)
    for sx in (-1.55, 1.55):
        for sy in (-0.95, 0.95):
            f.cyl(mb, sx, sy, 0.56, 0.19, 0.11, galv, axis="Z")
            f.cyl(mb, sx, sy, 0.63, 0.22, 0.02, dark, axis="Z")
    for sx in (-0.82, 0.82):
        valve(mb, f.p(sx, -0.95)[0], f.p(sx, -0.95)[1], 0.56, 0.14,
              axis="Y", wheel=get_mat("M_VEST_Red"))
        gauge(mb, f.p(sx + 0.18, -0.25)[0], f.p(sx + 0.18, -0.25)[1],
              0.95, axis="Z", r=0.07)
    f.box(mb, 0, 0.72, 0.45, 0.55, 0.30, 0.50, galv, bevel=0.006)
    mb.build(col())


def water_tank(name, cx, cy):
    mb = vest.MeshBuilder(name)
    body = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    blue = get_mat("M_MT_PipeWater")
    dark = get_mat("M_FM_Steel_Dark")
    conc = get_mat("M_FM_Concrete_Wall", "M_MT_Concrete")
    mb.add_box((cx, cy, 0.129), (2.85, 2.85, 0.250), conc, bevel=0.018)
    mb.add_cyl((cx, cy, 1.980), 1.15, 3.30, body, axis="Z", segments=32)
    mb.add_cyl((cx, cy, 0.330), 1.18, 0.150, dark, axis="Z", segments=32)
    mb.add_cyl((cx, cy, 3.650), 1.05, 0.140, body, axis="Z", segments=32)
    mb.add_cyl((cx, cy, 3.780), 0.62, 0.160, dark, axis="Z", segments=24)
    for z in (1.10, 2.05, 3.00):
        mb.add_cyl((cx, cy, z), 1.168, 0.075, dark, axis="Z", segments=32)

    # Registro frontal norte.
    mb.add_cyl((cx, cy + 1.165, 2.55), 0.30, 0.18, dark, axis="Y",
               segments=24)
    mb.add_cyl((cx, cy + 1.255, 2.55), 0.24, 0.03, body, axis="Y",
               segments=24)
    bolts_y(mb, cx, cy + 1.275, 2.55, 0.36, 8)

    # Escalera sur y visor de nivel.
    ladder_y(mb, cx, cy - 1.33, 0.45, 3.55, 0.44)
    for z in (0.75, 1.80, 2.85):
        mb.add_box((cx, cy - 1.20, z), (0.50, 0.24, 0.035), dark)
    pz(mb, cx + 1.22, cy + 0.42, 1.10, 3.10, 0.035,
       get_mat("M_MT_EmissiveWhite"), 10)
    for z in (1.10, 3.10):
        mb.add_cyl((cx + 1.22, cy + 0.42, z), 0.055, 0.06, dark,
                   axis="Z", segments=12)
    gauge(mb, cx + 1.18, cy + 0.55, 2.55, axis="X", r=0.075)

    # Tuberias de entrada y salida.
    pz(mb, cx - 0.38, cy, 3.60, 4.90, 0.17, blue, 20)
    flange(mb, cx - 0.38, cy, 4.80, 0.17, "Z")
    py(mb, cy - 1.10, cy - 0.20, cx, 0.45, 0.13, blue, 16)
    pz(mb, cx, cy - 1.10, 0.45, 1.05, 0.13, blue, 16)
    valve(mb, cx + 0.95, cy - 0.55, 0.45, 0.12, axis="Y",
          wheel=get_mat("M_VEST_Red"))
    mb.build(col())


def ahu(name, cx, cy, label):
    f = wh.Frame(cx, cy, 0.0)
    mb = vest.MeshBuilder(name)
    body = get_mat("M_FM_Steel_Dark", "M_VEST_Galv")
    galv = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    dark = get_mat("M_MT_BoilerDark")
    conc = get_mat("M_FM_Concrete_Wall", "M_MT_Concrete")
    f.box(mb, 0, 0, 0.094, 2.05, 5.25, 0.180, conc, bevel=0.012)
    f.box(mb, 0, 0, 1.275, 1.80, 5.00, 2.20, body, bevel=0.012)
    for sy in (-1.65, 0.0, 1.65):
        f.box(mb, -0.915, sy, 1.28, 0.05, 1.42, 1.92, galv, bevel=0.004)
        f.box(mb, -0.946, sy - 0.56, 1.55, 0.025, 0.10, 0.20, dark)
    for sy in (-0.82, 0.82):
        f.box(mb, -0.925, sy, 1.30, 0.035, 0.055, 2.06, dark)
    f.box(mb, -0.930, 0.0, 2.26, 0.030, 4.90, 0.060, galv)

    # Rejilla de retorno y ventilador.
    f.cyl(mb, -0.930, 0.0, 1.52, 0.48, 0.075, dark, axis="X",
          segments=24)
    for i in range(-3, 4):
        f.box(mb, -0.975, 0.0, 1.52 + i * 0.10, 0.020, 0.86, 0.045,
              galv)
    f.box(mb, -0.955, 0.0, 1.52, 0.10, 0.12, 0.12, dark)

    # Caja de filtros y tomas de instrumentos.
    f.box(mb, 0.70, -2.20, 2.42, 1.10, 0.80, 0.38, galv, bevel=0.006)
    for i in range(5):
        f.box(mb, 0.72, -2.20, 2.30 + i * 0.06, 0.95, 0.70, 0.018, dark)
    gauge(mb, cx - 0.96, cy + 0.55, 2.05, axis="X", r=0.07)
    gauge(mb, cx - 0.96, cy + 0.82, 2.05, axis="X", r=0.07)
    f.box(mb, -0.945, 0.20, 0.75, 0.035, 0.34, 0.24,
          get_mat("M_MT_Screen"))
    plate(mb, cx - 0.955, cy - 0.95, 2.10, 0.50, 0.16, axis="X")
    text("MT_Label_%s_TEXT" % label, label, 0.11, (cx - 0.975, cy - 0.95, 2.10),
         (-1, 0, 0), get_mat("M_MT_TextDark"))

    # Conducto vertical hasta el techo.
    f.box(mb, 0.25, 1.82, 4.05, 0.95, 0.95, 3.55, galv, bevel=0.006)
    for z in (2.50, 3.35, 4.20, 5.05):
        f.box(mb, 0.25, 1.82, z, 1.03, 1.03, 0.070, dark, bevel=0.004)
    f.box(mb, 0.25, 1.82, 5.80, 1.00, 1.00, 0.060, dark)
    g_gauge = 0
    mb.build(col())


def compressor(name, cx, cy):
    mb = vest.MeshBuilder(name)
    body = get_mat("M_MT_BoilerGreen")
    dark = get_mat("M_FM_Steel_Dark")
    galv = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    conc = get_mat("M_FM_Concrete_Wall", "M_MT_Concrete")
    yellow = get_mat("M_FM_Safety_Yellow")
    mb.add_box((cx, cy, 0.129), (1.45, 1.05, 0.250), conc, bevel=0.014)
    mb.add_box((cx, cy, 0.760), (1.20, 0.82, 1.00), body, bevel=0.014)
    mb.add_box((cx, cy + 0.42, 0.760), (1.02, 0.04, 0.86), galv,
               bevel=0.004)
    for i in range(6):
        mb.add_box((cx, cy + 0.445, 0.40 + i * 0.11),
                   (0.72, 0.025, 0.045), dark)
    mb.add_cyl((cx, cy, 1.36), 0.26, 0.86, galv, axis="X", segments=20)
    mb.add_box((cx + 0.10, cy + 0.34, 1.18), (0.45, 0.24, 0.34), dark,
               bevel=0.006)
    mb.add_box((cx + 0.10, cy + 0.465, 1.18), (0.34, 0.020, 0.22),
               get_mat("M_MT_Screen"))
    for i in range(3):
        mb.add_cyl((cx - 0.38 + i * 0.10, cy + 0.42, 0.80), 0.035, 0.06,
                   get_mat("M_MT_GaugeFace"), axis="Y", segments=12)
    plate(mb, cx + 0.30, cy + 0.395, 1.44, 0.42, 0.16, axis="Y")
    pz(mb, cx + 0.40, cy, 1.50, 3.80, 0.10, get_mat("M_MT_PipeAir"), 16)
    g_gauge = 0
    mb.build(col())


# ---------------------------------------------------------------------------
# Cuadros electricos, transformador y taller
# ---------------------------------------------------------------------------


def switchgear(name, cx):
    mb = vest.MeshBuilder(name)
    body = get_mat("M_MT_BoilerGreen")
    dark = get_mat("M_FM_Steel_Dark")
    galv = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    conc = get_mat("M_FM_Concrete_Wall", "M_MT_Concrete")
    y = -9.25
    mb.add_box((cx, y, 0.090), (1.98, 0.88, 0.180), conc, bevel=0.010)
    mb.add_box((cx, y, 1.190), (1.90, 0.80, 2.20), body, bevel=0.010)
    mb.add_box((cx, y - 0.410, 1.190), (1.84, 0.045, 2.10), galv,
               bevel=0.004)
    for i in range(4):
        mb.add_box((cx - 0.72 + i * 0.48, y - 0.438, 0.62),
                   (0.30, 0.020, 0.045), dark)
    mb.add_box((cx, y - 0.440, 1.62), (1.56, 0.020, 0.42), body,
               bevel=0.003)
    for i in range(3):
        mb.add_cyl((cx - 0.42 + i * 0.42, y - 0.455, 1.62), 0.060, 0.035,
                   get_mat("M_MT_GaugeFace"), axis="Y", segments=16)
    mb.add_box((cx + 0.76, y - 0.455, 1.15), (0.035, 0.070, 0.34), dark,
               bevel=0.003)
    mb.add_box((cx + 0.60, y - 0.452, 1.15), (0.22, 0.035, 0.045), galv)
    for i, dz in enumerate((0.36, 0.30, 0.24)):
        mat_i = get_mat("M_VEST_Emissive_Green") if i != 1 else \
            get_mat("M_MT_EmissiveRed")
        mb.add_cyl((cx - 0.78, y - 0.448, 2.05 - dz), 0.018, 0.025,
                   mat_i, axis="Y", segments=8)
    mb.add_box((cx, y, 2.37), (1.94, 0.84, 0.13), dark, bevel=0.004)
    plate(mb, cx, y - 0.455, 2.10, 0.44, 0.12, axis="Y")
    mb.build(col())


def workbench(name, cx, cy, rz, length=2.60):
    f = wh.Frame(cx, cy, rz)
    mb = vest.MeshBuilder(name)
    wood = get_mat("M_FM_Workbench_Wood", "M_FM_Wood_Detailed")
    steel = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    dark = get_mat("M_FM_Steel_Dark")
    for sx in (-1, 1):
        for sy in (-1, 1):
            f.box(mb, sx * (length * 0.5 - 0.10), sy * 0.33, 0.460,
                  0.075, 0.075, 0.880, steel, bevel=0.004)
    f.box(mb, 0, 0, 0.940, length, 0.86, 0.085, wood, bevel=0.006)
    f.box(mb, 0, 0, 0.882, length - 0.12, 0.74, 0.045, dark, bevel=0.004)
    f.box(mb, 0, 0, 0.220, length - 0.22, 0.72, 0.040, dark, bevel=0.003)
    f.box(mb, length * 0.5 - 0.50, 0.02, 0.545, 0.82, 0.66, 0.53,
          get_mat("M_MT_BoilerGreen"), bevel=0.008)
    for i in range(3):
        f.box(mb, length * 0.5 - 0.50, -0.322, 0.36 + i * 0.17, 0.74,
              0.025, 0.145, dark, bevel=0.003)
        f.box(mb, length * 0.5 - 0.50, -0.338, 0.36 + i * 0.17, 0.24,
              0.020, 0.022, steel)
    # Tornillo de banco.
    f.box(mb, -length * 0.30, -0.06, 1.030, 0.28, 0.24, 0.10, dark,
          bevel=0.006)
    f.box(mb, -length * 0.30, -0.20, 1.090, 0.16, 0.20, 0.12, steel,
          bevel=0.004)
    f.cyl(mb, -length * 0.30, -0.30, 1.030, 0.030, 0.32, steel,
          axis="Y", segments=10)
    f.cyl(mb, -length * 0.30, -0.46, 1.030, 0.050, 0.035, dark,
          axis="Y", segments=12)
    # Regleta de enchufes y bandeja trasera.
    mb.build(col())


def pegboard(name, cx, cy):
    f = wh.Frame(cx, cy, math.radians(90))
    mb = vest.MeshBuilder(name)
    board = get_mat("M_FM_Pegboard", "M_FM_Workbench_Wood")
    steel = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    dark = get_mat("M_FM_Steel_Dark")
    f.box(mb, 0, 0.565, 1.66, 2.45, 0.025, 1.18, board, bevel=0.003)
    for dz in (-0.60, 0.60):
        f.box(mb, 0, 0.585, 1.66 + dz, 2.48, 0.035, 0.045, steel)
    for sx in (-1.24, 1.24):
        f.box(mb, sx, 0.585, 1.66, 0.045, 0.035, 1.22, steel)
    # Herramientas colgadas.
    f.box(mb, -0.92, 0.545, 1.60, 0.045, 0.055, 0.42, dark)
    f.box(mb, -0.92, 0.540, 1.84, 0.22, 0.060, 0.08, steel)
    for i, x in enumerate((-0.60, -0.45, -0.30)):
        f.box(mb, x, 0.545, 1.55, 0.045, 0.050, 0.36 + i * 0.03, steel)
        f.box(mb, x, 0.545, 1.77, 0.075, 0.045, 0.08, dark)
    for i, x in enumerate((0.25, 0.38, 0.51, 0.64)):
        f.cyl(mb, x, 0.535, 1.60, 0.020, 0.26 + i * 0.03,
              get_mat("M_VEST_Red") if i % 2 else steel, axis="Z",
              segments=8)
        f.cyl(mb, x, 0.535, 1.75 + i * 0.015, 0.040, 0.05, dark,
              axis="Z", segments=8)
    f.box(mb, 0.92, 0.545, 1.57, 0.10, 0.05, 0.38, steel)
    f.box(mb, 0.92, 0.535, 1.38, 0.06, 0.06, 0.22, dark)
    mb.build(col())


def parts_cabinet(name, cx, cy):
    mb = vest.MeshBuilder(name)
    body = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    dark = get_mat("M_FM_Steel_Dark")
    mb.add_box((cx, cy, 0.90), (0.95, 0.38, 1.80), body, bevel=0.008)
    for i in range(2):
        mb.add_box((cx - 0.235 + i * 0.47, cy + 0.195, 0.90),
                   (0.42, 0.025, 1.68), dark, bevel=0.003)
        mb.add_box((cx - 0.235 + i * 0.47, cy + 0.215, 1.10),
                   (0.035, 0.045, 0.22), body)
    mb.add_box((cx, cy + 0.20, 1.55), (0.80, 0.022, 0.24),
               get_mat("M_MT_Screen"))
    plate(mb, cx, cy + 0.215, 1.85, 0.55, 0.12, axis="Y")
    mb.build(col())


def extinguisher(name, x, y, rz=0.0):
    mb = vest.MeshBuilder(name)
    red = get_mat("M_FM_Extinguisher_Red", "M_VEST_Red")
    dark = get_mat("M_FM_Steel_Dark")
    galv = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    black = get_mat("M_VEST_Black")
    mb.add_cyl((x, y, 0.279), 0.100, 0.550, red, axis="Z", segments=16)
    mb.add_cyl((x, y, 0.570), 0.075, 0.055, dark, axis="Z", segments=14)
    mb.add_cyl((x, y, 0.615), 0.042, 0.050, galv, axis="Z", segments=12)
    mb.add_box((x, y - 0.035, 0.640), (0.130, 0.050, 0.025), dark,
               rot=(0, 0, rz))
    mb.add_box((x + 0.015, y + 0.025, 0.665), (0.110, 0.035, 0.020), galv,
               rot=(0, 0, rz))
    mb.add_cyl((x + 0.082, y + 0.020, 0.600), 0.030, 0.045,
               get_mat("M_MT_GaugeFace"), axis="Z", segments=10)
    pz(mb, x + 0.094, y - 0.030, 0.210, 0.565, 0.016, black, 8)
    mb.add_box((x + 0.094, y - 0.075, 0.205), (0.045, 0.110, 0.030),
               black, rot=(0, 0, rz))
    mb.add_box((x, y + 0.100, 0.360), (0.075, 0.025, 0.180), dark,
               bevel=0.002, rot=(0, 0, rz))
    mb.add_plane((x, y - 0.101, 0.340), 0.115, 0.180,
                 get_mat("M_FM_Label_Extintor", "M_FM_Label_White"),
                 rot=(math.radians(90), 0, rz))
    mb.build(col())


def stool(name, x, y, rz=0.0):
    mb = vest.MeshBuilder(name)
    green = get_mat("M_MT_BoilerGreen")
    dark = get_mat("M_FM_Steel_Dark")
    mb.add_cyl((x, y, 0.628), 0.170, 0.052, green, axis="Z", segments=20)
    mb.add_cyl((x, y, 0.652), 0.145, 0.012, dark, axis="Z", segments=20)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.add_box((x + sx * 0.120, y + sy * 0.120, 0.305),
                       (0.030, 0.030, 0.600), dark,
                       rot=(0, 0, rz))
            mb.add_box((x + sx * 0.120, y + sy * 0.120, 0.0145),
                       (0.045, 0.045, 0.025), dark,
                       rot=(0, 0, rz))
    # Travesaños a dos alturas: sin caras coplanares en los cruces.
    for sy in (-0.12, 0.12):
        mb.add_box((x, y + sy, 0.150), (0.240, 0.024, 0.024), dark,
                   rot=(0, 0, rz))
    for sx in (-0.12, 0.12):
        mb.add_box((x + sx, y, 0.205), (0.024, 0.240, 0.024), dark,
                   rot=(0, 0, rz))
    mb.build(col())


def breaker_panel(name, x, y):
    mb = vest.MeshBuilder(name)
    body = get_mat("M_MT_BoilerGreen")
    dark = get_mat("M_FM_Steel_Dark")
    galv = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    mb.add_box((x, y, 1.680), (0.250, 1.060, 3.300), body, bevel=0.008)
    mb.add_box((x + 0.135, y, 1.680), (0.030, 0.960, 3.120), galv,
               bevel=0.003)
    for sy in (-0.42, 0.42):
        for z in (0.35, 3.01):
            mb.add_box((x + 0.152, y + sy, z), (0.020, 0.030, 0.120),
                       dark)
    for row in range(3):
        z = 0.88 + row * 0.82
        for i in range(4):
            yy = y - 0.33 + i * 0.22
            mb.add_box((x + 0.156, yy, z), (0.040, 0.170, 0.240),
                       dark, bevel=0.002)
            mb.add_box((x + 0.178, yy, z), (0.010, 0.055, 0.075),
                       galv)
        mb.add_box((x + 0.155, y, z + 0.29), (0.020, 0.88, 0.030),
                   galv)
    for i in range(5):
        mb.add_box((x + 0.154, y, 0.28 + i * 0.055),
                   (0.018, 0.62, 0.022), dark)
    mb.add_box((x + 0.165, y + 0.435, 1.55), (0.060, 0.035, 0.240),
               galv, bevel=0.003)
    plate(mb, x + 0.153, y - 0.28, 3.15, 0.42, 0.10, axis="X")
    mb.build(col())


def se_bench():
    f = wh.Frame(103.5, -47.32, 0.0)
    mb = vest.MeshBuilder("MT_SE_Workbench")
    wood = get_mat("M_FM_Workbench_Wood", "M_FM_Wood_Detailed")
    steel = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    dark = get_mat("M_FM_Steel_Dark")
    for sx in (-1, 1):
        for sy in (-1, 1):
            f.box(mb, sx * 1.80, sy * 0.32, 0.46, 0.08, 0.08, 0.88,
                  steel, bevel=0.004)
    f.box(mb, 0, 0, 0.940, 3.85, 0.85, 0.085, wood, bevel=0.006)
    f.box(mb, 0, 0, 0.22, 3.70, 0.72, 0.040, dark)
    f.box(mb, 0, 0.04, 0.55, 1.15, 0.66, 0.55, dark, bevel=0.008)
    for i in range(3):
        f.box(mb, 0, 0.39, 0.38 + i * 0.16, 1.02, 0.025, 0.13,
              get_mat("M_MT_BoilerGreen"), bevel=0.003)
    f.box(mb, -1.30, -0.05, 1.04, 0.26, 0.22, 0.10, dark, bevel=0.006)
    f.box(mb, -1.30, -0.18, 1.10, 0.15, 0.18, 0.11, steel, bevel=0.004)
    # Taladro de columna.
    f.cyl(mb, 1.15, 0.06, 0.61, 0.09, 0.66, steel, axis="Z", segments=14)
    f.box(mb, 1.15, 0.06, 0.97, 0.42, 0.34, 0.07, dark, bevel=0.004)
    f.box(mb, 1.15, 0.06, 1.34, 0.30, 0.30, 0.36,
          get_mat("M_MT_BoilerGreen"), bevel=0.010)
    f.cyl(mb, 1.15, 0.06, 1.17, 0.035, 0.18, steel, axis="Z", segments=10)
    f.cyl(mb, 1.15, 0.06, 1.08, 0.025, 0.12, dark, axis="Z", segments=8)
    for i in range(3):
        a = i * math.pi * 2 / 3
        f.box(mb, 1.15 + math.cos(a) * 0.13, 0.06 + math.sin(a) * 0.13,
              1.38, 0.10, 0.025, 0.025, get_mat("M_VEST_Red"))
    # Estante superior con cajas de piezas.
    for sx in (-1.45, 1.45):
        f.box(mb, sx, 0.37, 1.92, 0.05, 0.28, 0.05, steel)
    f.box(mb, 0, 0.40, 1.92, 3.00, 0.32, 0.035, steel)
    for i in range(6):
        f.box(mb, -1.25 + i * 0.50, 0.40, 2.02, 0.38, 0.28, 0.17,
              get_mat("M_MT_BoilerGreen") if i % 2 else
              get_mat("M_FM_Plastic_Blue"), bevel=0.004)
    mb.build(col())


# ---------------------------------------------------------------------------
# Techo, paredes, suelo
# ---------------------------------------------------------------------------


def wainscot_run(mb, axis, fixed, start, end, normal):
    if end - start < 0.5:
        return
    panel = get_mat("M_FM_Painted_Green", "M_MT_BoilerGreen")
    steel = get_mat("M_FM_Steel_Dark")
    yellow = get_mat("M_FM_Safety_Yellow", "M_MT_Yellow")
    mid = (start + end) * 0.5
    length = end - start
    off = fixed + normal * 0.032
    if axis == "X":
        mb.add_box((mid, off, 0.620), (length, 0.050, 0.960), panel,
                   bevel=0.004, uv_scale=0.6)
        mb.add_box((mid, off + normal * 0.004, 1.125),
                   (length + 0.02, 0.090, 0.045), steel, bevel=0.003)
        mb.add_box((mid, off + normal * 0.004, 0.075),
                   (length + 0.02, 0.070, 0.110), yellow, bevel=0.003)
        x = start + 2.4
        while x < end - 0.2:
            mb.add_box((x, off + normal * 0.028, 0.62),
                       (0.012, 0.020, 0.94), steel)
            x += 2.4
    else:
        mb.add_box((off, mid, 0.620), (0.050, length, 0.960), panel,
                   bevel=0.004, uv_scale=0.6)
        mb.add_box((off + normal * 0.004, mid, 1.125),
                   (0.090, length + 0.02, 0.045), steel, bevel=0.003)
        mb.add_box((off + normal * 0.004, mid, 0.075),
                   (0.070, length + 0.02, 0.110), yellow, bevel=0.003)
        y = start + 2.4
        while y < end - 0.2:
            mb.add_box((off + normal * 0.028, y, 0.62),
                       (0.020, 0.012, 0.94), steel)
            y += 2.4


def wainscot():
    mb = vest.MeshBuilder("MT_Wainscot_TRIM")
    # Caras interiores: N -7.85, S -47.85, W 56.15, E 111.85.
    wainscot_run(mb, "X", -7.85, 56.30, 59.90, +1)
    wainscot_run(mb, "X", -7.85, 66.10, 111.70, +1)
    wainscot_run(mb, "X", -47.85, 56.30, 111.70, +1)
    wainscot_run(mb, "Y", 56.15, -47.70, -8.30, +1)
    wainscot_run(mb, "Y", 111.85, -47.70, -40.10, -1)
    wainscot_run(mb, "Y", 111.85, -35.90, -8.30, -1)
    mb.build(col())


def ceiling_services():
    # Cabeceras de tuberia E-O sobre la nave.
    galv = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    steam = get_mat("M_MT_PipeSteam")
    water = get_mat("M_MT_PipeWater")
    cond = get_mat("M_MT_PipeCond")
    air = get_mat("M_MT_PipeAir")

    runs = (
        ("Steam_A", -19.10, 5.06, 0.155, steam, True),
        ("Water_A", -20.30, 5.02, 0.115, water, False),
        ("Cond_A", -21.50, 4.98, 0.095, cond, False),
        ("Air_A", -22.70, 4.94, 0.080, air, False),
    )
    for suffix, y, z, r, m, insulated in runs:
        for i, (a, b) in enumerate(((56.3, 75.0), (75.0, 95.0),
                                    (95.0, 111.7))):
            name = "MT_Header_%s_%d" % (suffix, i + 1)
            mb = vest.MeshBuilder(name)
            if insulated:
                pz_ = z
                px(mb, a, b, y, pz_, r, get_mat("M_MT_Insulation"), 20)
                x = a + 1.0
                while x < b - 0.3:
                    mb.add_cyl((x, y, pz_), r * 1.14, 0.070, galv,
                               axis="X", segments=20)
                    x += 1.2
            else:
                px(mb, a, b, y, z, r, m, 18)
                x = a + 1.4
                while x < b - 0.3:
                    flange(mb, x, y, z, r, "X")
                    x += 2.8
            mb.build(col())
        # Soportes al techo.
        mb = vest.MeshBuilder("MT_Supports_%s" % suffix)
        x = 58.0
        while x < 111.0:
            mb.add_box((x, y, 5.51), (0.06, 0.06, 0.86), galv)
            mb.add_box((x, y, 5.06 + r * 1.15), (0.10, 0.52, 0.055),
                       galv)
            x += 4.0
        mb.build(col())

    # Ramales de vapor a calderas.
    for cx in (80.0, 92.0):
        mb = vest.MeshBuilder("MT_SteamBranch_%d" % int(cx))
        px(mb, cx - 0.34, cx - 0.34, -22.70, 4.85, 0.12,
           get_mat("M_MT_PipeSteam"), 16)
        py(mb, -22.70, -19.10, cx - 0.34, 4.85, 0.12,
           get_mat("M_MT_PipeSteam"), 16)
        valve(mb, cx - 0.34, -21.40, 4.85, 0.12, axis="Y")
        mb.build(col())

    # Bandeja de cables sobre los cuadros.
    mb = vest.MeshBuilder("MT_CableTray_CABLE")
    tray_y, tray_z = -9.05, 4.74
    dark = get_mat("M_FM_Steel_Dark")
    galv = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    mb.add_box((89.0, tray_y, tray_z), (30.0, 0.52, 0.045), dark,
               bevel=0.003)
    for sy in (-1, 1):
        mb.add_box((89.0, tray_y + sy * 0.265, tray_z + 0.080),
                   (30.0, 0.035, 0.150), galv, bevel=0.003)
    for i in range(3):
        px(mb, 74.0, 104.0, tray_y - 0.10 + i * 0.10, tray_z + 0.055,
           0.022, get_mat("M_VEST_Black"), 8)
    x = 76.0
    while x < 104.0:
        mb.add_box((x, tray_y, 5.25), (0.05, 0.05, 1.00), dark)
        x += 4.0
    mb.build(col())

    # Conducto HVAC principal y rejillas.
    mb = vest.MeshBuilder("MT_HVAC_Duct")
    duct_y, duct_z = -13.60, 4.98
    for i, (a, b) in enumerate(((56.5, 78.0), (78.0, 98.0),
                                (98.0, 107.8))):
        mb.add_box(((a + b) * 0.5, duct_y, duct_z),
                   (b - a, 0.92, 0.70),
                   get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv"),
                   bevel=0.005)
        mb.add_box(((a + b) * 0.5, duct_y, duct_z - 0.370),
                   (b - a - 0.08, 0.86, 0.045),
                   get_mat("M_FM_Steel_Dark"), bevel=0.002)
    for x in (62.0, 70.0, 82.0, 90.0, 102.0):
        mb.add_box((x, duct_y, duct_z - 0.405), (0.55, 0.50, 0.050),
                   get_mat("M_FM_Steel_Dark"), bevel=0.003)
        for i in range(4):
            mb.add_box((x, duct_y - 0.19 + i * 0.13, duct_z - 0.432),
                       (0.50, 0.025, 0.020),
                       get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv"))
    mb.build(col())

    # Conexiones de aire de las AHU: intake y retorno por cubierta.
    mb = vest.MeshBuilder("MT_AHU_Air_CABLE")
    galv = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    dark = get_mat("M_FM_Steel_Dark")
    for cx, cy in ((108.6, -16.5), (108.6, -27.0)):
        mb.add_box((cx, cy, 5.885), (1.30, 1.10, 0.16), galv,
                   bevel=0.003)
        for i in range(5):
            mb.add_box((cx - 0.32 + i * 0.16, cy, 5.974),
                       (0.05, 0.62, 0.030), galv, bevel=0.0)
    mb.build(col())
    mb = vest.MeshBuilder("MT_CableTray_South_CABLE")
    dark = get_mat("M_FM_Steel_Dark")
    galv = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    mb.add_box((83.0, -46.10, 4.55), (50.0, 0.52, 0.045), dark,
               bevel=0.003)
    for sy in (-1, 1):
        mb.add_box((83.0, -46.10 + sy * 0.265, 4.63),
                   (50.0, 0.035, 0.150), galv, bevel=0.003)
    for i in range(3):
        px(mb, 58.0, 108.0, -46.20 + i * 0.10, 4.605,
           0.022, get_mat("M_VEST_Black"), 8)
    mb.build(col())

    # Ramal de bandeja hacia la escalera de emergencia E2.
    mb = vest.MeshBuilder("MT_E2_TrayLink_CABLE")
    tray_mat = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    cable_mat = get_mat("M_VEST_Black")
    wh.tray_segment(mb, tray_mat, 108.0, -45.85, 108.0, -38.0, 4.55)
    wh.tray_segment(mb, tray_mat, 108.25, -38.0, 112.0, -38.0, 4.55)
    for x in (107.90, 108.00, 108.10):
        mb.add_cyl((x, -41.93, 4.61), 0.018, 7.45, cable_mat,
                   axis="Y", segments=8)
    for y in (-38.10, -38.00, -37.90):
        mb.add_cyl((110.13, y, 4.61), 0.018, 3.50, cable_mat,
                   axis="X", segments=8)
    for x, y in ((108.0, -44.0), (108.0, -41.0), (108.0, -39.0),
                 (109.5, -38.0), (111.0, -38.0)):
        wh.tray_hanger(mb, tray_mat, x, y, 4.55, 5.99)
    mb.build(col())


def monorail():
    mb = vest.MeshBuilder("MT_Monorail_TRIM")
    steel = get_mat("M_FM_Safety_Yellow")
    dark = get_mat("M_FM_Steel_Dark")
    galv = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    y = -25.0
    mb.add_box((86.0, y, 4.58), (30.0, 0.34, 0.060), steel, bevel=0.004)
    mb.add_box((86.0, y, 4.40), (30.0, 0.070, 0.320), steel, bevel=0.003)
    mb.add_box((86.0, y, 4.22), (30.0, 0.24, 0.050), steel, bevel=0.003)
    for x in (72.0, 80.0, 90.0, 100.0):
        mb.add_box((x, y, 5.18), (0.08, 0.08, 1.20), dark)
        mb.add_box((x, y, 5.78), (0.25, 0.25, 0.05), dark)
    # Carro y polipasto.
    mb.add_box((86.0, y, 3.98), (0.52, 0.38, 0.30), dark, bevel=0.008)
    for sx in (-0.18, 0.18):
        for sy in (-0.12, 0.12):
            mb.add_box((86.0 + sx, y + sy, 4.155),
                       (0.10, 0.10, 0.070), galv, bevel=0.003)
    mb.add_box((86.0, y, 3.78), (0.34, 0.26, 0.20), steel, bevel=0.006)
    pz(mb, 86.0, y, 2.70, 3.69, 0.022, galv, 6)
    mb.add_box((86.0, y, 2.64), (0.22, 0.20, 0.12), dark, bevel=0.006)
    mb.add_cyl((86.0, y, 2.52), 0.12, 0.24, steel, axis="Y", segments=12)
    mb.build(col())


def lights():
    mb = vest.MeshBuilder("MT_Lights_LIGHT")
    dark = get_mat("M_FM_Steel_Dark")
    galv = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    tube = get_mat("M_VEST_Emissive_Cool")
    for x in (66.0, 84.0, 102.0):
        for y in (-11.5, -24.0, -36.5):
            for sx in (-0.40, 0.40):
                mb.add_box((x + sx, y, 5.68), (0.025, 0.025, 0.52),
                           galv)
            mb.add_box((x, y, 5.40), (1.45, 0.30, 0.12), dark,
                       bevel=0.006)
            mb.add_box((x, y, 5.315), (1.36, 0.36, 0.035), galv,
                       bevel=0.003)
            mb.add_box((x, y, 5.285), (1.28, 0.065, 0.055), tube,
                       bevel=0.0)
            for sx in (-0.69, 0.69):
                mb.add_box((x + sx, y, 5.34), (0.045, 0.32, 0.10),
                           dark)
    mb.build(col())

    mb = vest.MeshBuilder("MT_Emergency_LIGHT")
    red = get_mat("M_MT_EmissiveRed")
    dark = get_mat("M_FM_Steel_Dark")
    for x, y, nx, ny in ((70.0, -7.92, 0, -1), (56.22, -33.0, 1, 0),
                         (111.78, -22.0, -1, 0), (90.0, -47.92, 0, 1)):
        mb.add_box((x, y, 2.95), (0.28, 0.10, 0.20), dark, bevel=0.004)
        mb.add_box((x + nx * 0.055, y + ny * 0.055, 2.95),
                   (0.22, 0.035, 0.13), red, bevel=0.002)
    mb.build(col())

    mb = vest.MeshBuilder("MT_Fixtures_LIGHT")
    for x, y in ((70.0, -7.95), (56.25, -27.0), (111.75, -44.0),
                 (100.0, -47.79)):
        mb.add_box((x, y, 2.30), (0.24, 0.10, 0.36),
                   get_mat("M_FM_Steel_Dark"), bevel=0.004)
        mb.add_box((x, y, 2.30), (0.14, 0.025, 0.22),
                   get_mat("M_MT_EmissiveWhite"))
    mb.build(col())


# ---------------------------------------------------------------------------
# Sala de maquinas, tanques y taller
# ---------------------------------------------------------------------------


def plant_room():
    boiler("MT_Boiler_01", 80.0, -25.0)
    boiler("MT_Boiler_02", 92.0, -25.0)
    pump_skid("MT_PumpSkid_01", 86.0, -24.8, 0.0)
    pump_skid("MT_PumpSkid_02", 86.0, -31.3, 0.0)
    water_tank("MT_WaterTank_01", 74.0, -44.3)
    water_tank("MT_WaterTank_02", 80.6, -44.3)
    water_tank("MT_WaterTank_03", 87.2, -44.3)

    # Colector vertical de servicios en el muro oeste.
    mb = vest.MeshBuilder("MT_Risers")
    galv = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    for i, (m, r) in enumerate((
            (get_mat("M_MT_Insulation"), 0.145),
            (get_mat("M_MT_PipeWater"), 0.100),
            (get_mat("M_MT_PipeCond"), 0.090),
            (get_mat("M_MT_PipeAir"), 0.075))):
        x = 56.62
        y = -26.6 - i * 0.42
        pz(mb, x, y, 0.40, 5.00, r, m, 18)
        for z in (1.10, 2.40, 3.70):
            mb.add_cyl((x, y, z), r * 1.48, 0.075, galv, axis="Z",
                       segments=18)
        valve(mb, x, y, 1.65, r, axis="Z",
              wheel=get_mat("M_MT_Yellow"))
        py(mb, -26.6, -26.6, x, 0.40, 0.0, m)  # no-op defensivo
    px(mb, 56.62, 56.62, -26.6, 0.0, 0.0, galv)
    mb.build(col())

    # Tanque receptor de aire y secador en el muro este.
    mb = vest.MeshBuilder("MT_AirReceiver")
    body = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    dark = get_mat("M_FM_Steel_Dark")
    cx, cy = 108.2, -32.7
    for sx in (-0.36, 0.36):
        for sy in (-0.36, 0.36):
            mb.add_box((cx + sx, cy + sy, 0.180), (0.10, 0.10, 0.36),
                       dark, bevel=0.004)
    mb.add_cyl((cx, cy, 1.470), 0.56, 2.20, body, axis="Z", segments=28)
    mb.add_cyl((cx, cy, 0.360), 0.40, 0.18, dark, axis="Z", segments=20)
    mb.add_cyl((cx, cy, 2.620), 0.58, 0.16, body, axis="Z", segments=28)
    mb.add_cyl((cx, cy, 2.740), 0.30, 0.18, dark, axis="Z", segments=20)
    for z in (0.80, 1.55, 2.30):
        mb.add_cyl((cx, cy, z), 0.575, 0.060, dark, axis="Z", segments=28)
    gauge(mb, cx - 0.58, cy, 2.10, axis="X", r=0.08)
    pz(mb, cx, cy, 2.80, 4.55, 0.10, get_mat("M_MT_PipeAir"), 14)
    valve(mb, cx, cy, 2.95, 0.10, axis="Z",
          wheel=get_mat("M_VEST_Red"))
    plate(mb, cx - 0.54, cy + 0.32, 1.62, 0.40, 0.22, axis="X")
    mb.build(col())

    # Compresores y secador.
    compressor("MT_Compressor_01", 58.6, -43.8)
    compressor("MT_Compressor_02", 61.4, -43.8)
    mb = vest.MeshBuilder("MT_AirDryer")
    dryer = get_mat("M_MT_BoilerGreen")
    galv = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    mb.add_box((64.2, -45.5, 0.78), (0.85, 0.72, 1.50), dryer,
               bevel=0.010)
    mb.add_box((64.2, -45.5, 1.58), (0.75, 0.62, 0.08), galv,
               bevel=0.004)
    mb.add_box((64.2, -45.86, 0.78), (0.52, 0.030, 0.55),
               get_mat("M_MT_Screen"))
    for i in range(3):
        mb.add_cyl((64.2, -45.88, 0.42 + i * 0.18), 0.045, 0.05,
                   get_mat("M_MT_GaugeFace"), axis="Y", segments=12)
    mb.build(col())

    # AHUs en el muro este.
    ahu("MT_AHU_01", 108.5, -16.5, "AHU-01")
    ahu("MT_AHU_02", 108.5, -27.0, "AHU-02")

    # Cuadros electricos y transformador.
    for i in range(6):
        switchgear("MT_Switchgear_%02d" % (i + 1), 77.0 + i * 2.0)
    wh.copy_prop("PROP_Z10_Transformer", "MT_Transformer", 99.5, -12.0,
                 0.004, rz=0.0)
    breaker_panel("MT_BreakerPanel", 56.30, -31.4)
    extinguisher("MT_Extinguisher_01", 58.0, -9.0)
    extinguisher("MT_Extinguisher_02", 96.0, -8.15)
    extinguisher("MT_Extinguisher_03", 110.9, -43.0)


def workshop():
    workbench("MT_Workbench_NW", 56.78, -12.35, math.radians(90), 2.60)
    pegboard("MT_Pegboard_NW", 56.78, -12.35)
    wh.shelf_unit("MT_Shelf_01", 56.66, -15.45, math.radians(90))
    wh.shelf_unit("MT_Shelf_02", 56.66, -16.65, math.radians(90))
    wh.shelf_unit("MT_Shelf_03", 56.66, -17.85, math.radians(90))
    wh.copy_prop("PROP_Z10_ToolCart", "MT_ToolCart", 64.15, -15.35,
                 0.004, rz=math.radians(-18))
    stool("MT_Stool_01", 63.20, -11.75, math.radians(10))
    wh.copy_prop("PROP_Z10_Toolbox", "MT_Toolbox", 57.12, -12.00,
                 0.986, rz=math.radians(90))
    wh.copy_prop("PROP_Z10_Tool_Screwdriver", "MT_Tool_Screwdriver",
                 57.65, -12.75, 0.986, rz=math.radians(70))

    mb = vest.MeshBuilder("MT_WeldingScreen")
    frame = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    curtain = get_mat("M_MT_BoilerGreen")
    mb.add_box((65.25, -17.10, 1.06), (0.05, 1.62, 2.06), curtain,
               bevel=0.004)
    for y in (-17.86, -16.34):
        mb.add_box((65.25, y, 0.16), (0.08, 0.08, 0.30), frame,
                   bevel=0.003)
    mb.build(col())

    # Estacion quimica en el muro oeste.
    wh.copy_prop("PROP_Z10_SpillPallet", "MT_SpillPallet", 60.8, -23.3,
                 0.004, rz=math.radians(8))
    wh.copy_prop("PROP_Z10_Barrel_0", "MT_Barrel_01", 60.45, -23.05,
                 0.209, rz=math.radians(20))
    wh.copy_prop("PROP_Z10_Barrel_0", "MT_Barrel_02", 61.15, -23.45,
                 0.209, rz=math.radians(-35))
    wh.copy_prop("PROP_Z10_Barrel_1", "MT_Barrel_03", 60.75, -23.80,
                 0.209, rz=math.radians(70))

    # IBC sobre palet, con jaula.
    mb = vest.MeshBuilder("MT_IBC_Tote")
    cage = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    white = get_mat("M_FM_Plastic_Blue", "M_MT_GaugeFace")
    frame = get_mat("M_FM_Steel_Dark")
    cx, cy = 62.9, -24.8
    mb.add_box((cx, cy, 0.100), (1.16, 1.06, 0.20), frame, bevel=0.006)
    mb.add_box((cx, cy, 0.760), (1.02, 0.92, 1.12), white, bevel=0.014)
    for z in (0.42, 0.78, 1.14):
        mb.add_box((cx, cy - 0.468, z), (1.04, 0.022, 0.022), cage)
        mb.add_box((cx, cy + 0.468, z), (1.04, 0.022, 0.022), cage)
        mb.add_box((cx - 0.518, cy, z), (0.022, 0.94, 0.022), cage)
        mb.add_box((cx + 0.518, cy, z), (0.022, 0.94, 0.022), cage)
    for dx in (-0.49, 0.49):
        for dy in (-0.44, 0.44):
            mb.add_box((cx + dx, cy + dy, 0.76), (0.035, 0.035, 1.14),
                       cage)
    mb.add_box((cx, cy - 0.475, 1.35), (0.62, 0.030, 0.28), cage)
    mb.add_box((cx, cy - 0.492, 1.35), (0.22, 0.010, 0.16),
               get_mat("M_FM_Label_White"))
    mb.build(col())

    # Ducha y lavaojos de emergencia.
    mb = vest.MeshBuilder("MT_Eyewash")
    steel = get_mat("M_Z10_HERO_Steel_Stainless_2K", "M_VEST_Galv")
    green = get_mat("M_VEST_Emissive_Green")
    pz(mb, 57.15, -21.20, 0.20, 2.22, 0.055, steel, 14)
    mb.add_cyl((57.15, -21.20, 2.20), 0.20, 0.08, steel, axis="Z",
               segments=16)
    for a in (0.0, math.pi):
        mb.add_box((57.15 + math.cos(a) * 0.13, -21.20 + math.sin(a) * 0.13,
                    2.16), (0.10, 0.10, 0.035), get_mat("M_MT_Yellow"))
    mb.add_cyl((57.15, -21.55, 1.10), 0.24, 0.09, steel, axis="Z",
               segments=20)
    mb.add_box((57.15, -21.82, 1.10), (0.30, 0.14, 0.10), steel,
               bevel=0.004)
    for dx in (-0.10, 0.10):
        mb.add_cyl((57.15 + dx, -21.82, 1.16), 0.035, 0.06, steel,
                   axis="Z", segments=10)
    mb.add_box((57.18, -21.20, 1.35), (0.08, 0.16, 0.26), green)
    pz(mb, 57.15, -21.20, 1.14, 1.83, 0.035, steel, 8)
    mb.build(col())

    # Armario EPI.
    parts_cabinet("MT_EPI_Cabinet", 56.75, -19.55)
    # Banco de taller sur.
    se_bench()
    stool("MT_Stool_02", 102.0, -43.3, math.radians(-15))
    stool("MT_Stool_03", 105.0, -43.4, math.radians(25))
    wh.copy_prop("PROP_Z10_Toolbox", "MT_Toolbox_02", 104.10, -47.25,
                 0.986, rz=math.radians(4))


# ---------------------------------------------------------------------------
# Suelo, senalizacion y narrativa
# ---------------------------------------------------------------------------


def floor_details():
    mb = vest.MeshBuilder("MT_FloorLines_FLOOR_LINE")
    line = get_mat("M_MT_LineYellow")
    for x in (66.15, 72.85):
        mb.add_plane((x, (-8.20 - 47.70) * 0.5, 0.012), 0.10, 39.50,
                     line)
    for y in (-34.20, -37.80):
        mb.add_plane(((56.30 + 111.70) * 0.5, y, 0.012), 55.40, 0.10,
                     line)
    mb.build(col())

    mb = vest.MeshBuilder("MT_Hazard_HAZ")
    haz = get_mat("M_FM_Hazard_Stripes", "M_MT_Yellow")
    for cx, cy, w, d in ((80.0, -25.0, 3.05, 3.05),
                         (92.0, -25.0, 3.05, 3.05),
                         (74.0, -44.3, 3.20, 3.20),
                         (80.6, -44.3, 3.20, 3.20),
                         (87.2, -44.3, 3.20, 3.20),
                         (99.5, -12.0, 3.70, 2.15),
                         (60.8, -23.4, 3.10, 2.30)):
        for sx in (-1, 1):
            mb.add_box((cx + sx * (w * 0.5 + 0.10), cy, 0.015),
                       (0.18, d + 0.38, 0.008), haz, uv_scale=0.4)
        for sy in (-1, 1):
            mb.add_box((cx, cy + sy * (d * 0.5 + 0.10), 0.015),
                       (w + 0.38, 0.18, 0.008), haz, uv_scale=0.4)
    mb.build(col())

    mb = vest.MeshBuilder("MT_Drains_GRILLE")
    dark = get_mat("M_FM_Steel_Dark")
    galv = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    for x, y in ((61.2, -24.6), (82.0, -26.3), (92.0, -42.0),
                 (105.5, -38.8), (62.0, -14.0)):
        mb.add_box((x, y, 0.012), (0.78, 0.78, 0.022), dark, bevel=0.002)
        for i in range(-3, 4):
            mb.add_box((x, y + i * 0.09, 0.026), (0.66, 0.032, 0.012),
                       galv)
    mb.build(col())

    mb = vest.MeshBuilder("MT_Puddles_DIS_WATER")
    puddle = get_mat("M_VEST_Puddle")
    for x, y, sx, sy, rz in ((84.0, -29.6, 1.30, 0.75, 0.2),
                             (60.6, -25.9, 0.95, 0.60, -0.4),
                             (108.0, -31.2, 1.10, 0.65, 0.1),
                             (91.0, -41.3, 1.20, 0.70, -0.2)):
        mb.add_plane((x, y, 0.006), sx, sy, puddle, rot=(0, 0, rz))
    mb.build(col())

    mb = vest.MeshBuilder("MT_Oil_DIS_OIL")
    oil = get_mat("M_WH_Oil", "M_MT_Soot")
    for x, y, sx, sy, rz in ((63.4, -44.8, 0.95, 0.55, 0.3),
                             (86.2, -25.0, 0.85, 0.50, -0.2),
                             (58.2, -43.0, 0.70, 0.42, 0.5)):
        mb.add_plane((x, y, 0.010), sx, sy, oil, rot=(0, 0, rz))
    mb.build(col())

    mb = vest.MeshBuilder("MT_RustStains_DECAL")
    rust = get_mat("M_MT_Rust")
    for x, y, sx, sy, rz in ((67.8, -21.0, 1.10, 0.65, 0.2),
                             (78.2, -20.5, 0.90, 0.52, -0.3),
                             (101.0, -9.8, 1.30, 0.60, 0.1),
                             (56.9, -27.2, 0.80, 0.50, 0.4),
                             (105.0, -33.4, 1.00, 0.55, -0.1)):
        mb.add_plane((x, y, 0.004), sx, sy, rust, rot=(0, 0, rz))
    mb.build(col())

    mb = vest.MeshBuilder("MT_Rags_PAPER")
    rag = get_mat("M_VEST_Cloth_Olive")
    paper = get_mat("M_VEST_Paper")
    for x, y, rz in ((63.7, -43.5, 0.3), (82.8, -28.8, -0.7),
                     (101.4, -44.1, 1.1), (57.4, -13.7, 0.2)):
        mb.add_plane((x, y, 0.016), 0.36, 0.26, rag, rot=(0, 0, rz))
    for x, y, rz in ((57.0, -12.9, 0.4), (103.0, -46.7, -0.2),
                     (76.0, -24.0, 1.2)):
        mb.add_plane((x, y, 0.018), 0.21, 0.297, paper, rot=(0, 0, rz))
    mb.build(col())

    mb = vest.MeshBuilder("MT_DroppedBolts_DECAL")
    steel = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    for x, y, r in ((79.8, -22.0, 0.014), (80.2, -22.3, 0.012),
                    (86.4, -23.7, 0.015), (86.7, -24.1, 0.012),
                    (93.2, -31.8, 0.014), (100.8, -45.0, 0.012),
                    (61.9, -22.9, 0.013), (57.8, -12.4, 0.011)):
        mb.add_cyl((x, y, 0.010), r, 0.018, steel, axis="Z",
                   segments=6)
    mb.build(col())

    mb = vest.MeshBuilder("MT_Scorch_DECAL")
    soot = get_mat("M_MT_Soot")
    mb.add_plane((84.5, -10.3, 0.014), 0.90, 0.55, soot,
                 rot=(0, 0, 0.3))
    mb.add_plane((84.1, -10.6, 0.016), 0.50, 0.35, soot,
                 rot=(0, 0, -0.4))
    mb.build(col())

    mb = vest.MeshBuilder("MT_BloodTrail_BLOOD")
    blood = get_mat("M_WH_Blood", "M_MT_Rust")
    for i in range(6):
        t = i / 5.0
        x = 83.0 + (98.5 - 83.0) * t
        y = -30.0 + (-37.0 + 30.0) * t
        mb.add_plane((x, y, 0.011), 0.42 + 0.18 * (1 - t),
                     0.24 + 0.10 * (1 - t), blood,
                     rot=(0, 0, 0.5 + i * 0.25))
    mb.build(col())

    mb = vest.MeshBuilder("MT_MineralStain_DECAL")
    mineral = get_mat("M_MT_GaugeFace")
    mb.add_plane((56.75, -27.0, 0.007), 0.80, 0.55, mineral,
                 rot=(0, 0, 0.2))
    mb.build(col())

    mb = vest.MeshBuilder("MT_FloorMarks_FLOOR_SIGN")
    white = get_mat("M_MT_LineYellow")
    for x, y in ((68.8, -45.2), (70.2, -45.2)):
        mb.add_box((x, y, 0.013), (0.10, 0.65, 0.008), white)
    mb.build(col())


def signage():
    panels = vest.MeshBuilder("MT_SignPanels_SIGN")
    dark = get_mat("M_FM_Steel_Dark")
    yellow = get_mat("M_FM_Safety_Yellow", "M_MT_Yellow")
    green = get_mat("M_VEST_Emissive_Green")
    white_panel = get_mat("M_FM_Label_White", "M_MT_GaugeFace")
    light = get_mat("M_MT_TextLight")
    dark_text = get_mat("M_MT_TextDark")

    # Rotulo principal sobre la puerta norte.
    panels.add_box((63.0, -7.90, 3.62), (3.15, 0.08, 0.92), dark,
                   bevel=0.005)
    panels.add_box((63.0, -7.955, 3.62), (2.95, 0.020, 0.76),
                   white_panel)
    text("MT_Sign_MainText_SIGN", "MANTENIMIENTO", 0.30,
         (63.0, -7.980, 3.68), (0, -1, 0), dark_text)
    text("MT_Sign_MainSub_SIGN", "ZONA TECNICA  ·  ACCESO RESTRINGIDO",
         0.115, (63.0, -7.980, 3.36), (0, -1, 0), dark_text)

    # Salida de emergencia este.
    panels.add_box((111.79, -38.0, 3.15), (0.08, 2.15, 0.70), dark,
                   bevel=0.005)
    panels.add_box((111.74, -38.0, 3.15), (0.020, 1.95, 0.54), green)
    text("MT_Sign_ExitText_SIGN", "SALIDA E2", 0.20,
         (111.715, -38.0, 3.15), (-1, 0, 0), light)

    # Alta tension sobre los cuadros.
    panels.add_box((83.5, -7.90, 2.72), (2.55, 0.08, 0.60), dark,
                   bevel=0.005)
    panels.add_box((83.5, -7.955, 2.72), (2.35, 0.020, 0.44), yellow)
    text("MT_Sign_HighVoltage_SIGN", "ALTA TENSION", 0.17,
         (83.5, -7.980, 2.72), (0, -1, 0), dark_text)

    # Agua caliente sobre la columna central.
    panels.add_box((84.0, -20.20, 2.42), (0.95, 0.08, 0.44), dark,
                   bevel=0.004)
    panels.add_box((84.0, -20.255, 2.42), (0.82, 0.018, 0.32), yellow)
    text("MT_Sign_HotWater_SIGN", "AGUA CALIENTE", 0.105,
         (84.0, -20.278, 2.42), (0, -1, 0), dark_text)

    # Zona de maquinas en el muro oeste.
    panels.add_box((56.20, -35.5, 2.92), (0.08, 2.70, 0.72), dark,
                   bevel=0.005)
    panels.add_box((56.25, -35.5, 2.92), (0.020, 2.48, 0.54),
                   white_panel)
    text("MT_Sign_MachineZone_SIGN", "ZONA DE MAQUINAS", 0.18,
         (56.275, -35.5, 2.92), (1, 0, 0), dark_text)

    # Ducha de emergencia.
    panels.add_box((56.22, -21.2, 2.68), (0.06, 1.45, 0.38), green,
                   bevel=0.004)
    text("MT_Sign_Shower_SIGN", "DUCHA DE EMERGENCIA", 0.095,
         (56.260, -21.2, 2.68), (1, 0, 0), light)

    # Etiquetas de calderas.
    for i, cx in enumerate((80.0, 92.0)):
        text("MT_Sign_Boiler%02d_SIGN" % (i + 1), "CALDERA %02d" % (i + 1),
             0.105, (cx - 1.145, -25.0, 2.28), (-1, 0, 0), light)

    # Etiquetas de tuberias en la cabecera.
    pipe_labels = (("VAPOR", -19.10, 5.22, get_mat("M_MT_PipeSteam")),
                   ("AGUA FRIA", -20.30, 5.18, get_mat("M_MT_PipeWater")),
                   ("CONDENSADO", -21.50, 5.14, get_mat("M_MT_PipeCond")),
                   ("AIRE", -22.70, 5.10, get_mat("M_MT_PipeAir")))
    for i, (label, y, z, _m) in enumerate(pipe_labels):
        panels.add_box((88.0, y, z), (0.95, 0.02, 0.24), white_panel,
                       bevel=0.002)
        text("MT_Sign_Pipe_%s_SIGN" % i, label, 0.095,
             (88.0, y + 0.015, z), (0, 1, 0), dark_text)

    panels.build(col())


def narrative():
    # Carro volcado y guante junto a las bombas.
    mb = vest.MeshBuilder("MT_DroppedGlove_DECAL")
    glove = get_mat("M_MT_Glove")
    mb.add_plane((85.4, -29.0, 0.017), 0.30, 0.18, glove,
                 rot=(0, 0, 0.6))
    mb.add_plane((85.7, -29.3, 0.019), 0.16, 0.12, glove,
                 rot=(0, 0, -0.3))
    mb.build(col())

    mb = vest.MeshBuilder("MT_ToppledCart")
    dark = get_mat("M_FM_Steel_Dark")
    galv = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    mb.add_box((89.0, -29.6, 0.36), (0.62, 0.95, 0.08), dark,
               bevel=0.004, rot=(0, math.radians(68), math.radians(20)))
    for sx in (-0.26, 0.26):
        mb.add_box((89.0 + sx * 0.8, -29.6, 0.16),
                   (0.06, 0.06, 0.32), galv, bevel=0.003)
    mb.add_box((88.4, -29.9, 0.06), (0.30, 0.30, 0.10), dark,
               bevel=0.004)
    mb.build(col())

    # Trapos y herramientas en el banco.
    mb = vest.MeshBuilder("MT_BenchClutter")
    paper = get_mat("M_VEST_Paper")
    steel = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_VEST_Galv")
    mb.add_plane((57.0, -12.1, 0.986), 0.22, 0.30, paper,
                 rot=(0, 0, 0.4))
    mb.add_cyl((57.25, -12.8, 1.000), 0.035, 0.10,
               get_mat("M_VEST_Red"), axis="Z", segments=10)
    mb.build(col())

    # Marca de arrastre sutil hacia la puerta este.
    mb = vest.MeshBuilder("MT_DragMark_DECAL")
    drag = get_mat("M_MT_Rust")
    for i in range(4):
        mb.add_plane((86.0 + i * 2.2, -33.2 - i * 0.6, 0.012),
                     1.10, 0.22, drag, rot=(0, 0, -0.18))
    mb.build(col())


# ---------------------------------------------------------------------------
# Ensamblado
# ---------------------------------------------------------------------------


def build():
    clean()
    materials()
    wainscot()
    ceiling_services()
    monorail()
    lights()
    plant_room()
    workshop()
    signage()
    floor_details()
    narrative()

    c = col()
    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons)
               for o in c.objects if o.type == "MESH")
    verts = sum(len(o.data.vertices) for o in c.objects if o.type == "MESH")
    print("MT_BUILD objects=%d verts=%d tris=%d" % (len(c.objects), verts, tris))
    for o in sorted(c.objects, key=lambda x: x.name):
        print("MT_OBJ", o.name,
              sum(len(p.vertices) - 2 for p in o.data.polygons)
              if o.type == "MESH" else 0)


if __name__ == "__main__":
    build()
