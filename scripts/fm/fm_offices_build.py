"""Viste Oficinas / Administración (Z08) en el master V06.

Idempotente: reconstruye L1_ART_OFFICES. No guarda el .blend, no toca otras
colecciones y no añade luces ni camaras. Reutiliza MeshBuilder, materiales y
props ya detallados del proyecto.

Uso desde Blender MCP:
    import runpy
    runpy.run_path("/home/riyo/Documentos/game/scripts/fm/fm_offices_build.py",
                   run_name="__main__")
"""

import bpy
import math
import os
import importlib.util

from mathutils import Vector, Matrix

PROJECT = "/home/riyo/Documentos/game"
COL_NAME = "L1_ART_OFFICES"
WH_PATH = os.path.join(PROJECT, "scripts", "fm", "fm_warehouse_build.py")

_spec = importlib.util.spec_from_file_location("wh", WH_PATH)
wh = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wh)
wh.COL_NAME = COL_NAME
vest = wh.vest

# Caras interiores del shell (Blender).
X0, X1 = -29.85, 14.85
Y0, Y1 = 30.15, 69.85
ZTOP = 4.5

M = {}


def col():
    return wh.col()


def clean():
    wh.clean()


def make_materials():
    M["carpet"] = wh.mat("M_OF_Carpet", (0.052, 0.068, 0.064), 0.97)
    M["carpet_light"] = wh.mat("M_OF_CarpetLight", (0.085, 0.10, 0.095), 0.96)
    M["partition"] = wh.mat("M_OF_Partition", (0.042, 0.055, 0.050), 0.58)
    M["acoustic"] = wh.mat("M_OF_Acoustic", (0.09, 0.105, 0.098), 0.92)
    M["laminate"] = wh.mat("M_OF_Laminate", (0.105, 0.125, 0.115), 0.44)
    M["laminate_light"] = wh.mat("M_OF_LaminateLight", (0.15, 0.16, 0.145), 0.46)
    M["white"] = wh.mat("M_OF_White", (0.76, 0.77, 0.73), 0.48)
    M["paper"] = wh.get_mat("M_VEST_Paper", "M_FM_Steel_Dark")
    M["cardboard"] = wh.get_mat("M_FM_Cardboard", "M_FM_Workbench_Wood")
    M["steel"] = wh.get_mat("M_FM_Steel_Dark", "M_FM_Metal_Panel")
    M["panel"] = wh.get_mat("M_FM_Metal_Panel", "M_FM_Steel_Dark")
    M["green"] = wh.get_mat("M_FM_Painted_Green", "M_FM_Metal_Panel")
    M["wood"] = wh.get_mat("M_FM_Workbench_Wood", "M_FM_Steel_Dark")
    M["rug"] = wh.get_mat("M_R21B_Rug", "M_FM_Steel_Dark")
    M["rug_light"] = wh.get_mat("M_REC10_Rug", "M_OF_White")
    M["plant"] = wh.get_mat("M_R21B_Plant_Light", "M_OF_Partition")
    M["plant_dark"] = wh.get_mat("M_R21B_Plant_Dark", "M_OF_Partition")
    M["fabric"] = wh.get_mat("M_REC02_Fabric", "M_OF_Partition")
    M["ceramic"] = wh.get_mat("M_R21B_Ceramic", "M_OF_White")
    M["black"] = wh.get_mat("M_WH_DarkMetal", "M_FM_Steel_Dark")
    M["screen"] = wh.mat("M_OF_Screen", (0.015, 0.05, 0.06), 0.28,
                         emission=(0.05, 0.45, 0.55), strength=2.6)
    M["screen_dead"] = wh.mat("M_OF_ScreenDead", (0.012, 0.016, 0.016), 0.35)
    M["emissive"] = wh.mat("M_OF_EmissivePanel", (0.75, 0.82, 0.85), 0.4,
                           emission=(0.78, 0.9, 1.0), strength=3.4)
    M["emissive_warm"] = wh.mat("M_OF_EmissiveWarm", (0.9, 0.78, 0.55), 0.5,
                                emission=(1.0, 0.78, 0.42), strength=2.8)
    M["emerg"] = wh.mat("M_OF_EmergGreen", (0.02, 0.18, 0.06), 0.4,
                        emission=(0.05, 0.9, 0.22), strength=3.0)
    M["yellow"] = wh.get_mat("M_FM_Safety_Yellow", "M_OF_White")
    M["water"] = wh.get_mat("M_SEC02_Water", "M_OF_Screen")
    M["blood"] = wh.get_mat("M_WH_Blood", "M_OF_Partition")
    M["glass"] = wh.mat("M_OF_Glass", (0.18, 0.30, 0.30), 0.08, 0.0)
    mm = M["glass"]
    b = next(n for n in mm.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Alpha"].default_value = 0.18
    mm.surface_render_method = "BLENDED"


# ---------------------------------------------------------------------------
# Piezas basicas
# ---------------------------------------------------------------------------


def bx(mb, material, x, y, z, sx, sy, sz, bevel=0.0, rot=(0, 0, 0)):
    mb.add_box((x, y, z), (sx, sy, sz), material, bevel=bevel, rot=rot)


def cy(mb, material, x, y, z, radius, depth, axis="Z", segments=16, bevel=0.0):
    mb.add_cyl((x, y, z), radius, depth, material, axis=axis,
               segments=segments, bevel=bevel)


def glass_panel(name, x, y, z, sx, sy, sz):
    mb = vest.MeshBuilder(name)
    bx(mb, M["glass"], x, y, z, sx, sy, sz, bevel=0.0)
    mb.build(col())


def trim_box(name, material, x, y, z, sx, sy, sz, rz=0.0):
    mb = vest.MeshBuilder(name + "_TRIM")
    bx(mb, material, x, y, z, sx, sy, sz, bevel=0.002,
       rot=(0, 0, rz))
    mb.build(col())


def copy_prop(src, name, x, y, z=0.002, rz=0.0, rx=0.0):
    return wh.copy_prop(src, name, x, y, z, rz=rz, rx=rx)


def chair(name, x, y, rz=0.0, variant=0, z=0.002):
    src = "R21B_BRIEF_Chair_%02d" % (variant % 6)
    return copy_prop(src, name, x, y, z, rz=rz)


def tipped_chair(name, x, y, rz=0.0):
    return copy_prop("R21B_BRIEF_Chair_08_Tipped", name, x, y, 0.002, rz=rz)


def plant(name, x, y, scale=1.0):
    mb = vest.MeshBuilder(name + "_DECAL")
    cy(mb, M["ceramic"], x, y, 0.22 * scale, 0.22 * scale,
       0.44 * scale, segments=16)
    cy(mb, M["black"], x, y, 0.445 * scale, 0.19 * scale,
       0.02 * scale, segments=16)
    for i in range(7):
        a = i * (2.0 * math.pi / 7.0) + 0.25
        r = 0.12 * scale
        bx(mb, M["plant"], x + math.cos(a) * r, y + math.sin(a) * r,
           0.72 * scale, 0.075 * scale, 0.40 * scale, 0.012 * scale,
           rot=(0.55 * math.cos(a), 0.55 * math.sin(a), a))
        bx(mb, M["plant_dark"], x + math.cos(a) * r * 0.55,
           y + math.sin(a) * r * 0.55, 0.60 * scale,
           0.055 * scale, 0.32 * scale, 0.010 * scale,
           rot=(0.75 * math.cos(a), 0.75 * math.sin(a), a))
    mb.build(col())


def monitor(mb, f, lx, lz, dead=False, wide=0.50):
    # Cuerpo, pantalla y soporte; la pantalla queda 4 mm por delante.
    f.box(mb, lx, 0.17, lz + 0.20, wide, 0.055, 0.30, M["black"],
          bevel=0.002)
    f.box(mb, lx, 0.141, lz + 0.20, wide - 0.045, 0.004, 0.255,
          M["screen_dead"] if dead else M["screen"], bevel=0.0)
    f.box(mb, lx, 0.17, lz + 0.045, 0.045, 0.035, 0.10, M["black"],
          bevel=0.001)
    f.box(mb, lx, 0.17, lz + 0.008, 0.20, 0.13, 0.016, M["black"],
          bevel=0.001)


def keyboard(mb, f, lx, ly, lz):
    f.box(mb, lx, ly, lz + 0.012, 0.42, 0.14, 0.020, M["black"],
          bevel=0.002)


def desk(name, x, y, rz=0.0, width=1.60, depth=0.80, dead=False,
         screen_angle=0.0, lift=0.0):
    mb = vest.MeshBuilder(name)
    f = wh.Frame(x, y, rz)
    # Tablero y estructura.
    f.box(mb, 0, 0, 0.742, width, depth, 0.050, M["laminate"],
          bevel=0.004)
    f.box(mb, -(width * 0.5 - 0.035), 0, 0.365,
          0.040, depth - 0.06, 0.700, M["steel"], bevel=0.002)
    f.box(mb, (width * 0.5 - 0.035), 0, 0.365,
          0.040, depth - 0.06, 0.700, M["steel"], bevel=0.002)
    f.box(mb, 0, (depth * 0.5 - 0.035), 0.49,
          width - 0.12, 0.030, 0.44, M["panel"], bevel=0.002)
    # Pedestal con tres cajones.
    px = -(width * 0.5 - 0.30)
    f.box(mb, px, 0.02, 0.31, 0.36, 0.56, 0.60, M["panel"],
          bevel=0.003)
    for i in range(3):
        f.box(mb, px, -0.276, 0.145 + i * 0.185,
              0.32, 0.020, 0.155, M["laminate_light"], bevel=0.002)
        f.box(mb, px, -0.289, 0.185 + i * 0.185,
              0.10, 0.012, 0.016, M["black"], bevel=0.001)
    # Panel bajo de privacidad en el lado del visitante.
    f.box(mb, 0, -(depth * 0.5 + 0.020), 0.99,
          width, 0.040, 0.46, M["acoustic"], bevel=0.004)
    # Pasacables.
    cy(mb, M["black"], x + math.cos(rz) * 0.55,
       y + math.sin(rz) * 0.55, 0.772, 0.035, 0.008, segments=12)
    # Monitor, teclado, raton y papeles.
    monitor(mb, f, 0.18, 0.770, dead=dead)
    keyboard(mb, f, 0.18, -0.075, 0.770)
    f.box(mb, 0.42, -0.06, 0.779, 0.060, 0.095, 0.018, M["black"],
          bevel=0.003)
    f.box(mb, -0.30, -0.20, 0.772, 0.24, 0.30, 0.003, M["paper"],
          bevel=0.0, rot=(0, 0, 0.16))
    f.box(mb, -0.48, 0.16, 0.777, 0.09, 0.09, 0.020, M["white"],
          bevel=0.003)
    # Telefono.
    f.box(mb, -0.12, 0.23, 0.775, 0.18, 0.18, 0.035, M["black"],
          bevel=0.004)
    f.box(mb, -0.12, 0.23, 0.795, 0.14, 0.09, 0.018, M["black"],
          bevel=0.003)
    # Luz de escritorio.
    _lx, _ly = f.p(0.62, 0.24)
    cy(mb, M["black"], _lx, _ly, 0.79, 0.045, 0.012, segments=12)
    f.box(mb, 0.62, 0.24, 0.94, 0.025, 0.025, 0.30, M["black"],
          bevel=0.001)
    f.box(mb, 0.55, 0.24, 1.09, 0.20, 0.12, 0.035, M["black"],
          bevel=0.004, rot=(0, 0.35, 0))
    ob = mb.build(col())
    if lift:
        ob.location.z += lift


def meeting_table(name, x, y):
    mb = vest.MeshBuilder(name)
    f = wh.Frame(x, y, 0)
    f.box(mb, 0, 0, 0.755, 3.20, 1.40, 0.060, M["wood"], bevel=0.006)
    f.box(mb, -1.30, 0, 0.38, 0.090, 1.05, 0.76, M["steel"],
          bevel=0.003)
    f.box(mb, 1.30, 0, 0.38, 0.090, 1.05, 0.76, M["steel"],
          bevel=0.003)
    f.box(mb, 0, 0, 0.50, 2.56, 0.055, 0.30, M["panel"], bevel=0.002)
    # Jarra y vasos sobre la mesa (coordenadas de mundo).
    cy(mb, M["white"], x + 0.55, y + 0.1, 0.83, 0.075, 0.18, segments=16)
    for i in range(4):
        cy(mb, M["glass"], x - 0.2 + i * 0.19, y - 0.22, 0.81,
           0.033, 0.09, segments=12)
    f.box(mb, -0.55, 0.28, 0.790, 0.40, 0.28, 0.005, M["paper"],
          bevel=0.0, rot=(0, 0, -0.1))
    mb.build(col())


def table_round(name, x, y, lift=0.0):
    mb = vest.MeshBuilder(name)
    cy(mb, M["wood"], x, y, 0.735, 0.66, 0.055, segments=24)
    cy(mb, M["steel"], x, y, 0.375, 0.045, 0.72, segments=12)
    cy(mb, M["steel"], x, y, 0.025, 0.32, 0.05, segments=16)
    ob = mb.build(col())
    if lift:
        ob.location.z += lift


def filing_cabinet(name, x, y, rz=0.0):
    mb = vest.MeshBuilder(name)
    f = wh.Frame(x, y, rz)
    f.box(mb, 0, 0, 0.66, 0.52, 0.62, 1.30, M["panel"], bevel=0.004)
    for i in range(4):
        f.box(mb, 0, -0.312, 0.20 + i * 0.295,
              0.46, 0.018, 0.255, M["laminate"], bevel=0.002)
        f.box(mb, 0, -0.323, 0.20 + i * 0.295,
              0.14, 0.012, 0.018, M["black"], bevel=0.001)
        f.box(mb, 0.17, -0.322, 0.20 + i * 0.295,
              0.10, 0.006, 0.045, M["white"], bevel=0.0)
    f.box(mb, 0, 0, 1.315, 0.54, 0.64, 0.025, M["steel"],
          bevel=0.002)
    mb.build(col())


def archive_shelf(name, x, y, rz=0.0, bays=3):
    mb = vest.MeshBuilder(name)
    total = bays * 0.92
    f = wh.Frame(x, y, rz)
    for sx in (-1, 1):
        for sy in (-1, 1):
            f.box(mb, sx * (total * 0.5 - 0.025), sy * 0.22,
                  0.96, 0.040, 0.040, 1.92, M["steel"], bevel=0.002)
    for i in range(4):
        f.box(mb, 0, 0, 0.30 + i * 0.48, total, 0.48, 0.025,
              M["panel"], bevel=0.002)
    for b in range(bays):
        cx = -total * 0.5 + 0.46 + b * 0.92
        for level in range(3):
            f.box(mb, cx, 0.02, 0.335 + level * 0.48,
                  0.72, 0.38, 0.28, M["cardboard"], bevel=0.0)
            f.box(mb, cx, 0.02, 0.478 + level * 0.48,
                  0.30, 0.005, 0.055, M["white"], bevel=0.0)
    mb.build(col())


def server_rack(name, x, y, rz=0.0):
    mb = vest.MeshBuilder(name)
    f = wh.Frame(x, y, rz)
    f.box(mb, 0, 0, 0.92, 0.62, 0.92, 1.82, M["black"], bevel=0.003)
    f.box(mb, 0, -0.468, 1.15, 0.54, 0.012, 1.36, M["black"],
          bevel=0.0)
    for i in range(9):
        f.box(mb, 0, -0.480, 0.48 + i * 0.135,
              0.46, 0.025, 0.035, M["panel"], bevel=0.001)
        f.box(mb, 0.17, -0.497, 0.48 + i * 0.135,
              0.018, 0.006, 0.014,
              M["emissive"] if i % 3 else M["emerg"], bevel=0.0)
    f.box(mb, 0, 0, 1.845, 0.66, 0.96, 0.045, M["panel"],
          bevel=0.002)
    mb.build(col())


def vending_machine(name, x, y, rz=0.0):
    mb = vest.MeshBuilder(name)
    f = wh.Frame(x, y, rz)
    f.box(mb, 0, 0, 0.95, 1.00, 0.80, 1.90, M["panel"], bevel=0.005)
    f.box(mb, 0, -0.405, 1.12, 0.82, 0.012, 1.34, M["black"],
          bevel=0.0)
    f.box(mb, 0, -0.414, 1.12, 0.70, 0.006, 1.20, M["screen"],
          bevel=0.0)
    for i in range(4):
        f.box(mb, 0.32, -0.422, 0.62 + i * 0.14,
              0.06, 0.008, 0.09, M["emissive"], bevel=0.0)
    f.box(mb, 0, -0.425, 0.34, 0.92, 0.020, 0.10, M["black"],
          bevel=0.002)
    mb.build(col())


def counter_unit(name, x0, x1, y, depth=0.62):
    mb = vest.MeshBuilder(name)
    cx = (x0 + x1) * 0.5
    width = x1 - x0
    bx(mb, M["panel"], cx, y, 0.45, width, depth, 0.90, bevel=0.004)
    bx(mb, M["laminate_light"], cx, y, 0.91, width + 0.04,
       depth + 0.04, 0.050, bevel=0.004)
    bx(mb, M["steel"], cx, y - depth * 0.5 - 0.01, 0.12,
       width, 0.04, 0.16, bevel=0.002)
    mb.build(col())


def appliance_microwave(name, x, y, z=0.96):
    mb = vest.MeshBuilder(name)
    bx(mb, M["black"], x, y, z + 0.15, 0.52, 0.36, 0.30, bevel=0.004)
    bx(mb, M["screen_dead"], x + 0.03, y - 0.187, z + 0.15,
       0.38, 0.006, 0.21, bevel=0.0)
    bx(mb, M["white"], x + 0.21, y - 0.190, z + 0.15,
       0.06, 0.005, 0.24, bevel=0.0)
    mb.build(col())


def coffee_machine(name, x, y, z=0.96):
    mb = vest.MeshBuilder(name)
    bx(mb, M["black"], x, y, z + 0.20, 0.36, 0.34, 0.40, bevel=0.004)
    bx(mb, M["steel"], x, y - 0.175, z + 0.20, 0.28, 0.020, 0.30,
       bevel=0.0)
    bx(mb, M["emissive"], x + 0.08, y - 0.188, z + 0.33, 0.04, 0.006,
       0.04, bevel=0.0)
    mb.build(col())


def water_cooler(name, x, y):
    mb = vest.MeshBuilder(name)
    bx(mb, M["white"], x, y, 0.52, 0.32, 0.32, 1.02, bevel=0.006)
    cy(mb, M["water"], x, y, 1.14, 0.15, 0.24, segments=16)
    bx(mb, M["steel"], x, y - 0.17, 0.78, 0.20, 0.03, 0.06,
       bevel=0.002)
    mb.build(col())


def whiteboard(name, x, y, z, sx, sy, sz, normal="N"):
    mb = vest.MeshBuilder(name + "_SIGN")
    if normal in ("N", "S"):
        bx(mb, M["steel"], x, y, z, sx, sy, sz, bevel=0.004)
        bx(mb, M["white"], x, y + 0.035 if normal == "S" else y - 0.035,
           z, sx - 0.10, 0.012, sz - 0.10, bevel=0.0)
    else:
        bx(mb, M["steel"], x, y, z, sy, sx, sz, bevel=0.004)
        bx(mb, M["white"], x - 0.035 if normal == "W" else x + 0.035,
           y, z, 0.012, sx - 0.10, sz - 0.10, bevel=0.0)
    mb.build(col())


def rug_copy(name, x, y, rz=0.0, z=0.012):
    copy_prop("R21B_BRIEF_Rug", name + "_RUG", x, y, z, rz=rz)


def text(name, string, size, x, y, z, normal, material=None, extrude=0.002):
    return wh.text_sign(name + "_SIGN", string, size, (x, y, z),
                        normal, material or M["white"], extrude=extrude)


# ---------------------------------------------------------------------------
# Zonas
# ---------------------------------------------------------------------------


def lobby():
    # Mostrador de recepcion mirando al sur.
    mb = vest.MeshBuilder("OF_ReceptionDesk")
    f = wh.Frame(-1.5, 34.8, 0)
    f.box(mb, 0, 0, 0.53, 3.80, 1.16, 1.06, M["green"], bevel=0.005)
    f.box(mb, 0, 0, 1.085, 4.02, 1.32, 0.055, M["laminate"],
          bevel=0.005)
    f.box(mb, 0, -0.60, 0.53, 3.80, 0.025, 0.98, M["panel"],
          bevel=0.002)
    f.box(mb, 0, -0.615, 0.78, 2.60, 0.012, 0.10, M["yellow"],
          bevel=0.0)
    monitor(mb, f, -0.55, 1.105, wide=0.44)
    keyboard(mb, f, -0.55, -0.05, 1.105)
    f.box(mb, 0.42, -0.18, 1.112, 0.24, 0.30, 0.006, M["paper"],
          bevel=0.0)
    f.box(mb, 1.10, 0.10, 1.115, 0.22, 0.18, 0.035, M["black"],
          bevel=0.004)
    f.box(mb, 0.90, -0.34, 1.112, 0.10, 0.10, 0.020, M["white"],
          bevel=0.002)
    mb.build(col())
    chair("OF_ReceptionChair", -1.5, 36.15, math.pi, z=0.010)
    # Zona de espera.
    rug_copy("OF_LobbyRug", -22.0, 34.3, z=0.014)
    table_round("OF_LobbyTable", -22.0, 34.3, lift=0.04)
    chair("OF_WaitChair_01", -25.6, 33.2, 1.5708, 2, z=0.010)
    chair("OF_WaitChair_02", -25.6, 35.4, 1.5708, 3, z=0.010)
    chair("OF_WaitChair_03", -18.4, 33.2, -1.5708, 4, z=0.010)
    chair("OF_WaitChair_04", -18.4, 35.4, -1.5708, 5, z=0.010)
    plant("OF_LobbyPlant_01", -28.7, 31.2, 1.1)
    plant("OF_LobbyPlant_02", -6.6, 31.2, 0.95)
    # Elevador decorativo en el muro oeste.
    mb = vest.MeshBuilder("OF_Elevator")
    bx(mb, M["steel"], -29.80, 35.0, 1.22, 0.10, 4.10, 2.44,
       bevel=0.004)
    bx(mb, M["panel"], -29.73, 33.98, 1.22, 0.06, 1.94, 2.30,
       bevel=0.003)
    bx(mb, M["panel"], -29.73, 36.02, 1.22, 0.06, 1.94, 2.30,
       bevel=0.003)
    bx(mb, M["black"], -29.69, 35.0, 1.22, 0.02, 0.035, 2.30,
       bevel=0.0)
    bx(mb, M["steel"], -29.79, 35.0, 2.50, 0.12, 4.40, 0.18,
       bevel=0.004)
    bx(mb, M["emissive"], -29.675, 37.15, 1.42, 0.012, 0.22, 0.28,
       bevel=0.0)
    bx(mb, M["black"], -29.675, 32.85, 1.20, 0.012, 0.16, 0.28,
       bevel=0.0)
    cy(mb, M["white"], -29.665, 32.85, 1.24, 0.028, 0.01,
       axis="X", segments=12)
    cy(mb, M["white"], -29.665, 32.85, 1.12, 0.028, 0.01,
       axis="X", segments=12)
    mb.build(col())
    # Directorio y reloj.
    mb = vest.MeshBuilder("OF_Directory_SIGN")
    bx(mb, M["steel"], -21.0, 30.22, 1.65, 1.80, 0.05, 1.20,
       bevel=0.004)
    bx(mb, M["black"], -21.0, 30.26, 1.65, 1.64, 0.014, 1.04,
       bevel=0.0)
    for i in range(5):
        bx(mb, M["white"], -21.0, 30.278, 2.02 - i * 0.17,
           1.30 - (i % 2) * 0.25, 0.006, 0.035, bevel=0.0)
    mb.build(col())
    text("OF_LobbyTitle", "NEXUS  /  ADMINISTRACIÓN", 0.30,
         -10.0, 30.20, 3.55, (0, 1, 0), M["white"], 0.004)
    text("OF_LobbySub", "RECUPERACIÓN  ·  NIVEL 1", 0.16,
         -10.0, 30.20, 3.24, (0, 1, 0), M["white"], 0.003)
    copy_prop("PROP_Z10_WallClock", "OF_LobbyClock", -29.78, 32.0, 2.90,
              rz=math.pi * 0.5)
    text("OF_DirectoryText", "DIRECTORIO", 0.17, -21.0, 30.285, 2.29,
         (0, 1, 0), M["yellow"], 0.003)
    # Señal de salida sur.
    mb = vest.MeshBuilder("OF_ExitSign_SIGN")
    bx(mb, M["emerg"], -7.2, 30.22, 3.10, 0.55, 0.10, 0.22,
       bevel=0.003)
    mb.build(col())


def open_office():
    rows = (42.7, 47.3, 51.9)
    cols = (-25.8, -18.2, -6.3, 0.2)
    for ri, y in enumerate(rows):
        for ci, x in enumerate(cols):
            desk("OF_Desk_%d_%d" % (ri + 1, ci + 1), x, y,
                 width=1.60, depth=0.80,
                 dead=(ri == 1 and ci == 2))
            chair("OF_DeskChair_%d_%d" % (ri + 1, ci + 1), x, y - 0.58,
                  variant=(ri + ci) % 6, z=0.010)
    # Columnas integradas: pequeñas señales y paneles acusticos.
    for x in (-22.0, -10.0, 2.0):
        for y in (40.0, 56.0):
            mb = vest.MeshBuilder("OF_ColumnBand_%s_%s" % (x, y))
            bx(mb, M["yellow"], x, y - 0.228, 1.10,
               0.46, 0.012, 0.10, bevel=0.0)
            mb.build(col())
    # Archivadores y copiadora junto al muro oeste.
    for i in range(3):
        filing_cabinet("OF_FileCabinet_%d" % (i + 1), -28.95,
                       38.6 + i * 0.66, rz=math.pi * 0.5)
    mb = vest.MeshBuilder("OF_Copier")
    bx(mb, M["panel"], -28.9, 42.2, 0.55, 0.70, 0.66, 1.06,
       bevel=0.006)
    bx(mb, M["black"], -28.9, 42.2, 1.11, 0.76, 0.72, 0.10,
       bevel=0.004)
    bx(mb, M["screen"], -28.9, 41.85, 1.17, 0.24, 0.03, 0.10,
       bevel=0.0)
    bx(mb, M["white"], -28.9, 41.86, 0.93, 0.42, 0.02, 0.04,
       bevel=0.0)
    mb.build(col())
    # Papelera y planta.
    copy_prop("PROP_REC02_Bin", "OF_Bin_01", -27.6, 39.0, 0.002)
    plant("OF_OpenPlant_01", 0.8, 38.6, 1.0)
    # Rótulo de zona.
    text("OF_OpenTitle", "OFICINAS  ·  PLANTA ABIERTA", 0.20,
         -29.78, 45.0, 3.20, (1, 0, 0), M["white"], 0.003)


def credenza(name, x, y, rz=0.0):
    """Aparador bajo de oficina con cuerpo, plinto, tapa y puertas."""
    mb = vest.MeshBuilder(name)
    f = wh.Frame(x, y, rz)
    f.box(mb, 0, 0, 0.7075, 3.00, 0.56, 1.385, M["laminate"],
          bevel=0.004)
    f.box(mb, 0, 0, 0.0125, 2.92, 0.50, 0.025, M["black"],
          bevel=0.002)
    # Tapa solapada con el cuerpo (sin caras coplanares).
    f.box(mb, 0, 0, 1.405, 3.06, 0.62, 0.050, M["wood"],
          bevel=0.004)
    # Tres puertas frontales con tirador.
    for i in range(3):
        dx = -0.98 + i * 0.98
        f.box(mb, dx, -0.300, 0.72, 0.90, 0.030, 1.20,
              M["laminate_light"], bevel=0.003)
        f.box(mb, dx + 0.33, -0.320, 0.72, 0.025, 0.020, 0.30,
              M["steel"], bevel=0.002)
    mb.build(col())


def private_office(idx, x0, x1, label):
    cx = (x0 + x1) * 0.5
    # Tabiques laterales opacos con panel acustico.
    if idx > 0:
        mb = vest.MeshBuilder("OF_OfficePart_%d" % idx)
        bx(mb, M["partition"], x0, 64.0, 1.35, 0.12, 12.0, 2.70,
           bevel=0.003)
        bx(mb, M["acoustic"], x0 + 0.065, 64.0, 1.35,
           0.015, 10.0, 1.80, bevel=0.0)
        mb.build(col())
    # Frente de vidrio en y=58 con hueco de puerta.
    door0 = cx - 0.70
    door1 = cx + 0.70
    for j, (gx0, gx1) in enumerate(((x0, door0), (door1, x1))):
        if gx1 - gx0 < 0.25:
            continue
        glass_panel("OF_OfficeGlass_%d_%d" % (idx + 1, j + 1),
                    (gx0 + gx1) * 0.5, 58.0, 1.40,
                    gx1 - gx0, 0.040, 2.68)
    # Hoja de vidrio abierta 90 grados hacia el norte.
    mb = vest.MeshBuilder("OF_OfficeDoor_%d" % (idx + 1))
    bx(mb, M["glass"], door0 + 0.025, 58.68, 1.06,
       0.035, 1.28, 2.08, bevel=0.0)
    bx(mb, M["steel"], door0 + 0.025, 59.32, 1.06,
       0.045, 0.035, 2.10, bevel=0.001)
    bx(mb, M["black"], door0 + 0.050, 59.18, 1.05,
       0.025, 0.16, 0.03, bevel=0.001)
    mb.build(col())
    # Mobiliario.
    desk("OF_PrivateDesk_%d" % (idx + 1), cx, 64.0, width=2.00,
         depth=0.90, dead=(idx == 2), lift=0.04)
    chair("OF_PrivateChair_%d" % (idx + 1), cx, 63.15,
          variant=(idx + 2) % 6, z=0.027)
    chair("OF_GuestChair_%d_A" % (idx + 1), cx - 0.75, 62.9,
          math.pi, variant=(idx + 1) % 6, z=0.027)
    chair("OF_GuestChair_%d_B" % (idx + 1), cx + 0.75, 62.9,
          math.pi, variant=(idx + 3) % 6, z=0.027)
    credenza("OF_Credenza_%d" % (idx + 1), cx, 69.48, rz=0.0)
    filing_cabinet("OF_PrivateFile_%d" % (idx + 1),
                   x1 - 0.55, 69.52, rz=math.pi)
    rug_copy("OF_PrivateRug_%d" % (idx + 1), cx, 63.4, z=0.014)
    plant("OF_PrivatePlant_%d" % (idx + 1), x0 + 0.65, 68.9, 0.9)
    text("OF_PrivateLabel_%d" % (idx + 1), label, 0.16,
         cx, 57.90, 2.62, (0, -1, 0), M["white"], 0.003)


def meeting_room():
    # Cerramiento de vidrio: oeste x=3 y sur y=58 con puerta.
    glass_panel("OF_MeetGlass_W", 3.0, 63.5, 1.40, 0.040, 11.0, 2.68)
    for j, (x0, x1) in enumerate(((3.0, 5.2), (6.8, 14.0))):
        glass_panel("OF_MeetGlass_S_%d" % (j + 1), (x0 + x1) * 0.5,
                    58.0, 1.40, x1 - x0, 0.040, 2.68)
    for x in (3.0, 5.2, 6.8, 14.0):
        trim_box("OF_MeetFrame_%s" % x, M["steel"], x, 58.0, 1.36,
                 0.055, 0.070, 2.72)
    mb = vest.MeshBuilder("OF_MeetDoor")
    bx(mb, M["glass"], 5.22, 58.66, 1.06, 0.035, 1.28, 2.08,
       bevel=0.0)
    bx(mb, M["steel"], 5.22, 59.30, 1.06, 0.045, 0.035, 2.10,
       bevel=0.001)
    bx(mb, M["black"], 5.25, 59.14, 1.05, 0.025, 0.16, 0.03,
       bevel=0.001)
    mb.build(col())
    meeting_table("OF_MeetingTable", 8.5, 63.5)
    for i, x in enumerate((7.3, 8.5, 9.7)):
        chair("OF_MeetChair_N_%d" % (i + 1), x, 64.85, math.pi,
              variant=i, z=0.027)
        chair("OF_MeetChair_S_%d" % (i + 1), x, 62.15, 0.0,
              variant=i + 3, z=0.027)
    chair("OF_MeetChair_W", 6.15, 63.5, -math.pi * 0.5, 1, z=0.027)
    chair("OF_MeetChair_E", 10.85, 63.5, math.pi * 0.5, 4, z=0.027)
    whiteboard("OF_MeetBoard", 8.5, 69.81, 1.72, 3.10, 0.06, 1.32,
               normal="N")
    mb = vest.MeshBuilder("OF_MeetScreen_SIGN")
    bx(mb, M["steel"], 14.78, 63.5, 2.45, 0.05, 2.10, 1.20,
       bevel=0.003)
    bx(mb, M["white"], 14.748, 63.5, 2.45, 0.012, 1.98, 1.08,
       bevel=0.0)
    mb.build(col())
    credenza("OF_MeetCredenza", 8.5, 69.48, rz=0.0)
    rug_copy("OF_MeetRug", 8.5, 63.5, z=0.014)
    plant("OF_MeetPlant", 13.4, 68.9, 1.0)
    text("OF_MeetLabel", "SALA DE REUNIONES", 0.18,
         8.5, 57.90, 2.60, (0, -1, 0), M["white"], 0.003)


def archive_room():
    # Cerramiento con puerta al oeste en y49..50.4.
    for j, (y0, y1) in enumerate(((44.0, 49.0), (50.4, 56.0))):
        mb = vest.MeshBuilder("OF_ArchiveWall_W_%d" % (j + 1))
        bx(mb, M["partition"], 3.0, (y0 + y1) * 0.5, 1.35,
           0.12, y1 - y0, 2.70, bevel=0.003)
        mb.build(col())
    mb = vest.MeshBuilder("OF_ArchiveWall_S")
    bx(mb, M["partition"], 6.25, 44.0, 1.35, 6.5, 0.12, 2.70,
       bevel=0.003)
    mb.build(col())
    mb = vest.MeshBuilder("OF_ArchiveWall_N")
    bx(mb, M["partition"], 6.25, 56.0, 1.35, 6.5, 0.12, 2.70,
       bevel=0.003)
    mb.build(col())
    mb = vest.MeshBuilder("OF_ArchiveWall_E")
    bx(mb, M["partition"], 9.5, 50.0, 1.35, 0.12, 12.0, 2.70,
       bevel=0.003)
    mb.build(col())
    # Marco y puerta abierta.
    mb = vest.MeshBuilder("OF_ArchiveDoor")
    bx(mb, M["panel"], 3.70, 49.0, 1.06, 1.34, 0.045, 2.08,
       bevel=0.003)
    bx(mb, M["screen_dead"], 3.70, 48.975, 2.10, 0.60, 0.006, 0.30,
       bevel=0.0)
    bx(mb, M["black"], 4.28, 48.95, 1.02, 0.10, 0.02, 0.04,
       bevel=0.001)
    mb.build(col())
    # Estanterias y racks.
    for i, sy in enumerate((47.0, 52.6)):
        archive_shelf("OF_ArchiveShelf_%d" % (i + 1), 8.75,
                      sy, rz=-math.pi * 0.5, bays=3)
    for i in range(4):
        server_rack("OF_ServerRack_%d" % (i + 1), 4.25 + i * 0.72,
                    55.20)
    mb = vest.MeshBuilder("OF_ArchiveAC")
    bx(mb, M["white"], 9.18, 54.9, 2.15, 0.55, 0.36, 0.42,
       bevel=0.004)
    bx(mb, M["black"], 9.18, 54.70, 2.15, 0.43, 0.012, 0.30,
       bevel=0.0)
    mb.build(col())
    mb = vest.MeshBuilder("OF_ArchiveSAI")
    bx(mb, M["black"], 4.4, 45.0, 0.48, 0.50, 0.70, 0.90,
       bevel=0.004)
    bx(mb, M["screen"], 4.4, 44.64, 0.62, 0.20, 0.012, 0.08,
       bevel=0.0)
    mb.build(col())
    text("OF_ArchiveLabel", "ARCHIVO  /  SERVIDORES", 0.18,
         6.2, 44.07, 2.55, (0, 1, 0), M["white"], 0.003)
    copy_prop("PROP_Z10_WallClock", "OF_ArchiveClock", 9.38, 46.0,
              3.02, rz=-math.pi * 0.5)


def cafeteria():
    # Muro norte con puerta x8..9.4.
    for j, (x0, x1) in enumerate(((3.0, 8.0), (9.4, 14.0))):
        mb = vest.MeshBuilder("OF_CafeWall_N_%d" % (j + 1))
        bx(mb, M["partition"], (x0 + x1) * 0.5, 40.0, 1.35,
           x1 - x0, 0.12, 2.70, bevel=0.003)
        mb.build(col())
    mb = vest.MeshBuilder("OF_CafeWall_W")
    bx(mb, M["partition"], 3.0, 35.5, 1.35, 0.12, 11.0, 2.70,
       bevel=0.003)
    mb.build(col())
    mb = vest.MeshBuilder("OF_CafeDoor")
    bx(mb, M["panel"], 8.02, 40.66, 1.06, 0.045, 1.28, 2.08,
       bevel=0.003)
    bx(mb, M["screen_dead"], 7.99, 40.66, 1.95, 0.006, 0.62, 0.30,
       bevel=0.0)
    mb.build(col())
    # Encimera sur.
    counter_unit("OF_CafeCounter", 4.0, 10.0, 30.62)
    # Fregadero.
    mb = vest.MeshBuilder("OF_CafeSink")
    bx(mb, M["steel"], 6.2, 30.62, 0.945, 0.62, 0.42, 0.025,
       bevel=0.002)
    bx(mb, M["black"], 6.2, 30.62, 0.960, 0.48, 0.30, 0.008,
       bevel=0.0)
    cy(mb, M["steel"], 6.2, 30.45, 1.05, 0.025, 0.22, segments=12)
    bx(mb, M["steel"], 6.2, 30.33, 1.16, 0.05, 0.20, 0.03,
       bevel=0.002)
    mb.build(col())
    coffee_machine("OF_CoffeeMachine", 4.9, 30.78, z=0.94)
    appliance_microwave("OF_Microwave", 8.4, 30.78, z=0.94)
    # Nevera y fuente de agua junto al muro este.
    mb = vest.MeshBuilder("OF_Fridge")
    bx(mb, M["white"], 14.35, 32.5, 0.92, 0.72, 0.70, 1.82,
       bevel=0.006)
    bx(mb, M["black"], 13.975, 32.5, 1.26, 0.012, 0.64, 0.035,
       bevel=0.0)
    mb.build(col())
    water_cooler("OF_WaterCooler", 14.15, 36.0)
    vending_machine("OF_Vending", 3.45, 38.8, math.pi * 0.5)
    # Mesas y sillas.
    for i, (x, y) in enumerate(((7.0, 34.5), (10.8, 37.2))):
        table_round("OF_CafeTable_%d" % (i + 1), x, y)
        for j in range(4):
            a = j * math.pi * 0.5 + math.pi * 0.25
            chair("OF_CafeChair_%d_%d" % (i + 1, j + 1),
                  x + math.cos(a) * 0.96, y + math.sin(a) * 0.96,
                  -a + math.pi * 0.5, variant=(i * 4 + j) % 6)
    # Reciclaje y fregona.
    mb = vest.MeshBuilder("OF_RecycleBins")
    for i in range(3):
        bx(mb, M["panel"], 12.6 + i * 0.42, 31.0, 0.31,
           0.36, 0.38, 0.62, bevel=0.004)
        bx(mb, M["white"], 12.6 + i * 0.42, 30.80, 0.50,
           0.20, 0.006, 0.10, bevel=0.0)
    mb.build(col())
    mb = vest.MeshBuilder("OF_MopBucket")
    bx(mb, M["yellow"], 13.6, 39.2, 0.22, 0.42, 0.38, 0.44,
       bevel=0.004)
    cy(mb, M["black"], 13.6, 39.2, 0.58, 0.022, 0.70, segments=8)
    mb.build(col())
    text("OF_CafeLabel", "CAFETERÍA", 0.20, 8.7, 39.88, 2.60,
         (0, -1, 0), M["white"], 0.003)


def connector():
    # Alfombra corrida del conector.
    mb = vest.MeshBuilder("OF_ConnectorRunner_CARPET")
    bx(mb, M["carpet_light"], -10.0, 17.0, 0.006, 2.60, 25.6, 0.006,
       bevel=0.0)
    mb.build(col())
    # Panelado de pared y zocalos.
    for side, x in (("W", -13.82), ("E", -6.18)):
        mb = vest.MeshBuilder("OF_ConnectorPanel_%s_TRIM" % side)
        bx(mb, M["green"], x, 17.0, 0.62, 0.035, 25.5, 1.16,
           bevel=0.002)
        bx(mb, M["steel"], x, 17.0, 1.20, 0.055, 25.3, 0.06,
           bevel=0.002)
        bx(mb, M["steel"], x, 17.0, 0.055, 0.055, 25.3, 0.07,
           bevel=0.002)
        mb.build(col())
    # Bancos y plantas.
    for i, y in enumerate((12.0, 18.5, 25.0)):
        mb = vest.MeshBuilder("OF_ConnectorBench_%d" % (i + 1))
        bx(mb, M["wood"], -13.55, y, 0.44, 0.48, 2.00, 0.06,
           bevel=0.004)
        bx(mb, M["steel"], -13.55, y, 0.235, 0.40, 1.80, 0.04,
           bevel=0.002)
        for sy in (-0.85, 0.85):
            bx(mb, M["steel"], -13.55, y + sy, 0.21,
               0.38, 0.05, 0.42, bevel=0.002)
        mb.build(col())
        plant("OF_ConnectorPlant_%d" % (i + 1), -6.75, y + 1.8, 0.85)
    # Luminarias y senaletica.
    for i in range(6):
        y = 7.5 + i * 4.2
        mb = vest.MeshBuilder("OF_ConnectorLight_%d_LIGHT" % (i + 1))
        bx(mb, M["emissive"], -10.0, y, 4.32, 0.22, 1.35, 0.035,
           bevel=0.0)
        mb.build(col())
        mb = vest.MeshBuilder("OF_ConnectorFixture_%d_TRIM" % (i + 1))
        bx(mb, M["steel"], -10.0, y, 4.36, 0.30, 1.50, 0.045,
           bevel=0.002)
        bx(mb, M["steel"], -10.0, y - 0.7, 4.38, 0.04, 0.04, 0.12,
           bevel=0.0)
        bx(mb, M["steel"], -10.0, y + 0.7, 4.38, 0.04, 0.04, 0.12,
           bevel=0.0)
        mb.build(col())
    # Tablones y senales.
    mb = vest.MeshBuilder("OF_ConnectorBoard_SIGN")
    bx(mb, M["steel"], -13.82, 9.8, 1.62, 0.06, 1.60, 1.06,
       bevel=0.003)
    bx(mb, M["paper"], -13.78, 9.8, 1.62, 0.012, 1.44, 0.90,
       bevel=0.0)
    for i in range(5):
        bx(mb, M["white"], -13.77, 9.8, 1.98 - i * 0.17,
           0.006, 1.10 - (i % 2) * 0.25, 0.030, bevel=0.0)
    mb.build(col())
    text("OF_ConnectorTitle", "OFICINAS  ·  ADMINISTRACIÓN", 0.18,
         -13.80, 5.6, 2.55, (1, 0, 0), M["white"], 0.003)
    text("OF_ConnectorExit", "SALIDA  →", 0.16, -13.80, 27.0, 2.55,
         (1, 0, 0), M["emerg"], 0.003)
    text("OF_ConnectorAseos", "ASEOS  ↑", 0.14, -6.20, 22.0, 2.35,
         (-1, 0, 0), M["white"], 0.003)
    # Extintor y reloj.
    mb = vest.MeshBuilder("OF_ConnectorExtinguisher")
    cy(mb, M["blood"], -13.55, 14.6, 0.42, 0.10, 0.58, segments=14)
    bx(mb, M["black"], -13.55, 14.6, 0.75, 0.09, 0.10, 0.12,
       bevel=0.002)
    bx(mb, M["steel"], -13.80, 14.6, 0.48, 0.04, 0.30, 0.06,
       bevel=0.002)
    mb.build(col())
    copy_prop("PROP_Z10_WallClock", "OF_ConnectorClock", -13.82, 20.0,
              3.05, rz=math.pi * 0.5)
    # Cajas y rastro narrativo.
    mb = vest.MeshBuilder("OF_ConnectorBoxes")
    bx(mb, M["cardboard"], -7.0, 5.8, 0.18, 0.52, 0.44, 0.36,
       bevel=0.0, rot=(0, 0, 0.2))
    bx(mb, M["cardboard"], -6.95, 5.98, 0.40, 0.42, 0.36, 0.30,
       bevel=0.0, rot=(0, 0, -0.1))
    mb.build(col())
    mb = vest.MeshBuilder("OF_ConnectorBlood_BLOOD")
    for i in range(7):
        bx(mb, M["blood"], -9.75 + (i % 3) * 0.10, 26.4 - i * 0.55,
           0.014, 0.18 + (i % 2) * 0.10, 0.32, 0.004,
           bevel=0.0, rot=(0, 0, 0.2 * i))
    mb.build(col())
    tipped_chair("OF_ConnectorTippedChair", -12.9, 7.4, 0.7)


def ceilings():
    # Bandejas de cable y conductos sobre pasillos.
    mb = vest.MeshBuilder("OF_CableTray_CABLE")
    # Bandeja continua del conector al lobby y cruce hacia la planta abierta.
    bx(mb, M["panel"], -10.0, 21.375, 3.950, 0.50, 34.25, 0.05,
       bevel=0.0)
    for x in (-10.25, -9.75):
        bx(mb, M["panel"], x, 21.375, 4.000, 0.04, 34.05, 0.14,
           bevel=0.0)
    for i in range(7):
        bx(mb, M["black"], -10.0, 6.0 + i * 5.4, 4.06, 0.36, 0.06,
           0.18, bevel=0.0)
    # Cruce en el lobby hacia la bandeja de la planta abierta.
    bx(mb, M["panel"], -12.0, 38.5, 3.950, 4.0, 0.45, 0.05,
       bevel=0.0)
    for y in (38.28, 38.72):
        bx(mb, M["panel"], -12.0, y, 4.000, 3.96, 0.04, 0.14,
           bevel=0.0)
    # Pasamuros sobre la puerta sur (marco de sleeve).
    for z in (3.78, 4.12):
        bx(mb, M["steel"], -10.0, 30.0, z, 1.10, 0.16, 0.06,
           bevel=0.0)
    for x in (-10.55, -9.45):
        bx(mb, M["steel"], x, 30.0, 3.95, 0.06, 0.12, 0.36,
           bevel=0.0)
    mb.build(col())
    mb = vest.MeshBuilder("OF_CableTray_Open_CABLE")
    bx(mb, M["panel"], -14.0, 47.0, 3.975, 0.45, 17.0, 0.05,
       bevel=0.0)
    for x in (-14.22, -13.78):
        bx(mb, M["panel"], x, 47.0, 4.025, 0.04, 16.8, 0.14,
           bevel=0.0)
    mb.build(col())
    mb = vest.MeshBuilder("OF_Duct_DIFFUSER")
    bx(mb, M["panel"], -18.0, 46.0, 4.18, 0.85, 14.0, 0.55,
       bevel=0.0)
    # Tirantes que unen el conducto con el techo.
    for y in (41.0, 51.0):
        bx(mb, M["steel"], -18.0, y, 4.475, 0.06, 0.06, 0.05,
           bevel=0.0)
    mb.build(col())
    # Luminarias de techo en oficinas, recepcion y cafe.
    lights = []
    for x in (-25.0, -14.0, -4.0):
        for y in (33.0, 42.0, 49.0, 55.0):
            lights.append((x, y))
    for x in (5.0, 10.0):
        for y in (33.0, 37.0, 46.0, 52.0, 62.0, 67.0):
            lights.append((x, y))
    for i, (x, y) in enumerate(lights):
        mb = vest.MeshBuilder("OF_CeilingLight_%02d_LIGHT" % (i + 1))
        bx(mb, M["emissive"], x, y, 4.30, 0.60, 0.60, 0.030,
           bevel=0.0)
        mb.build(col())
        mb = vest.MeshBuilder("OF_CeilingFrame_%02d_TRIM" % (i + 1))
        bx(mb, M["steel"], x, y, 4.34, 0.68, 0.68, 0.040,
           bevel=0.002)
        mb.build(col())
    # Detectores y rociadores, unidos por sus colectores de techo.
    mb = vest.MeshBuilder("OF_CeilingServices")
    for y in (32.0, 66.0):
        cy(mb, M["steel"], -12.0, y, 4.40, 0.012, 34.0, axis="X",
           segments=8)
    for i in range(8):
        x = -28.0 + (i % 4) * 10.0
        y = 32.0 + (i // 4) * 34.0
        cy(mb, M["white"], x, y, 4.40, 0.055, 0.035, segments=10)
        cy(mb, M["blood"], x + 2.0, y, 4.42, 0.018, 0.03, segments=8)
    mb.build(col())


def floor_details():
    # Alfombras de zonas.
    mb = vest.MeshBuilder("OF_Carpet_Lobby_CARPET")
    bx(mb, M["carpet"], -1.85, 33.8, 0.006, 9.3, 6.6, 0.006,
       bevel=0.0)
    mb.build(col())
    mb = vest.MeshBuilder("OF_Carpet_Open_CARPET")
    bx(mb, M["carpet"], -12.0, 47.3, 0.006, 29.0, 17.0, 0.006,
       bevel=0.0)
    mb.build(col())
    mb = vest.MeshBuilder("OF_Carpet_North_CARPET")
    bx(mb, M["carpet"], -16.0, 64.0, 0.006, 27.6, 11.6, 0.006,
       bevel=0.0)
    mb.build(col())
    mb = vest.MeshBuilder("OF_Carpet_Meet_CARPET")
    bx(mb, M["carpet"], 8.5, 63.5, 0.006, 10.8, 10.8, 0.006,
       bevel=0.0)
    mb.build(col())
    # Lineas de seguridad y paso.
    mb = vest.MeshBuilder("OF_FloorLines_FLOOR_LINE")
    bx(mb, M["yellow"], -10.0, 33.0, 0.012, 0.06, 5.0, 0.004,
       bevel=0.0)
    bx(mb, M["yellow"], -10.0, 41.0, 0.012, 0.06, 3.0, 0.004,
       bevel=0.0)
    bx(mb, M["yellow"], 9.4, 44.5, 0.012, 0.06, 4.0, 0.004,
       bevel=0.0)
    bx(mb, M["yellow"], 9.4, 54.0, 0.012, 0.06, 2.0, 0.004,
       bevel=0.0)
    mb.build(col())
    # Flechas de evacuacion.
    mb = vest.MeshBuilder("OF_EvacArrows_FLOOR_LINE")
    for (x, y, rz) in ((-10.0, 8.0, math.pi), (-4.0, 33.8, -1.5708),
                       (9.8, 42.4, math.pi), (5.0, 57.2, math.pi)):
        verts = [(x - 0.07, y - 0.34, 0.012), (x + 0.07, y - 0.34, 0.012),
                 (x + 0.07, y + 0.06, 0.012), (x - 0.07, y + 0.06, 0.012),
                 (x - 0.22, y + 0.06, 0.012), (x + 0.22, y + 0.06, 0.012),
                 (x, y + 0.32, 0.012)]
        # Rotacion manual alrededor de (x,y).
        ca, sa = math.cos(rz), math.sin(rz)
        verts = [(x + (vx - x) * ca - (vy - y) * sa,
                  y + (vx - x) * sa + (vy - y) * ca, vz)
                 for vx, vy, vz in verts]
        faces = [(0, 1, 2, 3), (3, 6, 4), (2, 5, 6)]
        uvs = [[(0, 0), (1, 0), (1, 1), (0, 1)],
               [(0, 0), (1, 0), (0.5, 1)],
               [(0.5, 0), (1, 1), (0, 0)]]
        mb._append(M["white"], verts, faces, uvs)
    mb.build(col())
    # Papeles y tazas.
    mb = vest.MeshBuilder("OF_Papers_PAPER")
    spots = [(-3.0, 37.2, 0.2), (-12.4, 44.0, -0.4),
             (-20.5, 46.4, 0.7), (4.4, 35.7, 0.3),
             (-8.4, 20.2, 0.1), (6.8, 62.2, -0.2)]
    for x, y, rz in spots:
        bx(mb, M["paper"], x, y, 0.030, 0.21, 0.30, 0.003,
           bevel=0.0, rot=(0, 0, rz))
    mb.build(col())
    mb = vest.MeshBuilder("OF_Cups_PAPER")
    for x, y, z in ((-3.6, 34.0, 0.062), (-15.2, 51.2, 0.062),
                    (8.6, 63.1, 0.070), (-9.9, 37.6, 0.062)):
        cy(mb, M["white"], x, y, z, 0.040, 0.095, segments=12)
    mb.build(col())


def signage():
    text("OF_Sign_Reception", "RECEPCIÓN", 0.14, -1.5, 34.17, 1.24,
         (0, -1, 0), M["white"], 0.003)
    # Cartel de alta tension junto al archivo.
    mb = vest.MeshBuilder("OF_HighVoltage_SIGN")
    bx(mb, M["yellow"], 9.57, 53.0, 2.30, 0.015, 0.34, 0.24,
       bevel=0.0)
    mb.build(col())
    text("OF_HighVoltageText", "ALTA\nTENSIÓN", 0.085, 9.585, 53.0,
         2.30, (1, 0, 0), M["black"], 0.002)
    # Plan de evacuacion en el conector.
    mb = vest.MeshBuilder("OF_EvacPlan_SIGN")
    bx(mb, M["white"], -6.20, 11.2, 1.62, 0.015, 0.52, 0.72,
       bevel=0.0)
    bx(mb, M["green"], -6.19, 11.2, 1.62, 0.006, 0.40, 0.58,
       bevel=0.0)
    mb.build(col())


def build():
    make_materials()
    clean()
    lobby()
    open_office()
    labels = ("GERENCIA", "OPERACIONES", "RRHH", "DIRECCIÓN")
    bounds = ((-29.85, -23.0), (-23.0, -16.0), (-16.0, -9.0),
              (-9.0, -2.0))
    for i, (x0, x1) in enumerate(bounds):
        private_office(i, x0, x1, labels[i])
    meeting_room()
    archive_room()
    cafeteria()
    connector()
    ceilings()
    floor_details()
    signage()
    print("OFFICES_BUILD objects=%d" % len(col().objects))
    print("OFFICES_BUILD tris=%d" % sum(
        len(o.data.loop_triangles) if o.type == "MESH" else 0
        for o in col().objects))


if __name__ == "__main__":
    build()
