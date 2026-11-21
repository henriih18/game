"""Viste el Aseo de planta (Z09) en el master V06.

Idempotente: reconstruye L1_ART_RESTROOM. No guarda el .blend, no toca otras
colecciones y no anade luces ni camaras. Geometria game-ready (bevel 0 en
paneles finos) y materiales PBR reutilizados del proyecto.
"""

import bpy
import math
import os
import importlib.util

PROJECT = "/home/riyo/Documentos/game"
COL_NAME = "L1_ART_RESTROOM"
WAREHOUSE_PATH = os.path.join(PROJECT, "scripts", "fm", "fm_warehouse_build.py")

_spec = importlib.util.spec_from_file_location("wh", WAREHOUSE_PATH)
wh = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wh)
wh.COL_NAME = COL_NAME
vest = wh.vest
col = wh.col
clean = wh.clean
mat = wh.mat
get_mat = wh.get_mat
text_sign = wh.text_sign

# Caras interiores del aseo (Blender). Godot z = -y.
X0, X1 = 18.15, 29.85
Y0, Y1 = 42.15, 57.85
ZCEIL = 3.20


def M(name, fallback="M_FM_Steel_Dark"):
    return get_mat(name, fallback)


def bx(mb, material, cx, cy, cz, sx, sy, sz, bevel=0.0, rot=(0.0, 0.0, 0.0),
       uv_scale=1.0):
    return mb.add_box((cx, cy, cz), (sx, sy, sz), material, bevel=bevel,
                      rot=rot, uv_scale=uv_scale)


def cyl(mb, material, cx, cy, cz, radius, depth, axis="Z", segments=16,
        rot=(0.0, 0.0, 0.0), bevel=0.0):
    return mb.add_cyl((cx, cy, cz), radius, depth, material, axis=axis,
                      segments=segments, rot=rot, bevel=bevel)


def blade(mb, material, p0, p1, z0, z1, thickness):
    """Panel vertical entre dos puntos (muro/division), sin rotaciones raras."""
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]
    length = math.hypot(dx, dy)
    rz = math.atan2(dy, dx)
    bx(mb, material, (p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5,
       (z0 + z1) * 0.5, length, thickness, z1 - z0,
       rot=(0.0, 0.0, rz), bevel=0.0)


def materials():
    mat("M_RS_Paint", (0.052, 0.080, 0.068), 0.72, 0.0)
    mat("M_RS_PaintDark", (0.022, 0.036, 0.030), 0.66, 0.0)
    mat("M_RS_Partition", (0.060, 0.092, 0.078), 0.48, 0.18)
    mat("M_RS_PartitionEdge", (0.26, 0.29, 0.27), 0.36, 0.75)
    mat("M_RS_Ceiling", (0.20, 0.22, 0.20), 0.88, 0.0)
    mat("M_RS_Grid", (0.055, 0.060, 0.055), 0.56, 0.35)
    mat("M_RS_Water", (0.020, 0.055, 0.055), 0.08, 0.0)
    mat("M_RS_WetFloor", (0.62, 0.48, 0.015), 0.55, 0.0)
    mat("M_RS_Red", (0.42, 0.018, 0.012), 0.44, 0.0)
    mat("M_RS_Green", (0.030, 0.26, 0.10), 0.44, 0.0,
        emission=(0.04, 0.55, 0.16), strength=1.4)
    mat("M_RS_Emissive", (0.55, 0.60, 0.58), 0.32, 0.0,
        emission=(0.86, 0.94, 1.0), strength=3.2)
    mat("M_RS_Chrome", (0.42, 0.44, 0.44), 0.30, 0.35)
    mat("M_RS_Mirror", (0.62, 0.66, 0.66), 0.12, 0.55)


def wainscot():
    """Zocalo ceramico hasta 2,30 m en los cuatro muros."""
    mb = vest.MeshBuilder("RS_Wainscot_TILE")
    tile = M("M_VEST_Tile", "M_FM_Concrete_Wall")
    cap = M("M_FM_Steel_Dark")
    h = 2.30
    # Oeste: dos tramos (el vano de acceso queda libre entre y46 y y52).
    for y0, y1 in ((42.19, 45.96), (52.04, 57.81)):
        bx(mb, tile, 18.175, (y0 + y1) * 0.5, 0.010 + h * 0.5,
           0.03, y1 - y0, h, uv_scale=0.65)
        bx(mb, cap, 18.175, (y0 + y1) * 0.5, h + 0.014,
           0.05, y1 - y0 - 0.03, 0.024)
    # Este: dos tramos (puerta a Vestuarios y48..52).
    for y0, y1 in ((42.19, 47.96), (52.04, 57.81)):
        bx(mb, tile, 29.825, (y0 + y1) * 0.5, 0.010 + h * 0.5,
           0.03, y1 - y0, h, uv_scale=0.65)
        bx(mb, cap, 29.825, (y0 + y1) * 0.5, h + 0.014,
           0.05, y1 - y0 - 0.03, 0.024)
    # Norte y sur.
    for y, flip in ((57.825, 1), (42.175, -1)):
        bx(mb, tile, 24.0, y, 0.010 + h * 0.5,
           11.6, 0.03, h, uv_scale=0.65)
        bx(mb, cap, 24.0, y, h + 0.014, 11.57, 0.05, 0.024)
    mb.build(col())


def floor_tiles():
    mb = vest.MeshBuilder("RS_FloorTiles_TRIM")
    tile = M("M_VEST_Tile", "M_FM_Concrete_Floor")
    bx(mb, tile, 24.0, 50.0, 0.003, 11.7, 15.7, 0.001,
       uv_scale=0.85)
    # Felpudo de goma junto a la puerta oeste.
    mat_ = M("M_VEST_Rubber", "M_FM_Rubber")
    bx(mb, mat_, 18.75, 49.0, 0.010, 1.10, 2.0, 0.008,
       uv_scale=1.0)
    mb.build(col())


def toilet(mb, x, y, facing):
    """Inodoro de porcelana con tanque. facing=+1 mira al sur."""
    ceramic = M("M_FM_Ceramic_White", "M_FM_Ceramic_White")
    seat = M("M_RS_PaintDark")
    chrome = M("M_RS_Chrome")
    # Tanque contra el muro.
    tank_y = y + 0.46 * facing
    bx(mb, ceramic, x, tank_y, 0.62, 0.40, 0.18, 0.52, bevel=0.004)
    bx(mb, ceramic, x, tank_y, 0.902, 0.42, 0.20, 0.03)
    cyl(mb, chrome, x, tank_y, 0.915, 0.025, 0.01, axis="Z", segments=12)
    # Base y taza.
    bx(mb, ceramic, x, y, 0.121, 0.34, 0.30, 0.22, bevel=0.006)
    cyl(mb, ceramic, x, y, 0.28, 0.205, 0.30, axis="Z", segments=20,
        bevel=0.004)
    cyl(mb, seat, x, y, 0.455, 0.225, 0.035, axis="Z", segments=20)
    cyl(mb, ceramic, x, y - 0.02 * facing, 0.475, 0.195, 0.012,
        axis="Z", segments=20)
    # Pulsador y tapa.
    bx(mb, chrome, x + 0.12, tank_y - 0.02 * facing, 0.66,
       0.05, 0.02, 0.014)


def stalls(north=True):
    name = "RS_StallsNorth" if north else "RS_StallsSouth"
    mb = vest.MeshBuilder(name)
    part = M("M_RS_Partition")
    edge = M("M_RS_PartitionEdge")
    door_mat = M("M_RS_Partition")
    chrome = M("M_RS_Chrome")
    if north:
        xs = [21.60, 23.12, 24.64, 26.16, 27.68, 29.70]
        y_back, y_front = 57.80, 56.08
        door_y = y_front
        toilet_y = 57.24
        facing = 1
    else:
        xs = [21.20, 22.76, 24.32, 25.88, 27.44, 29.60]
        y_back, y_front = 42.22, 43.92
        door_y = y_front
        toilet_y = 42.76
        facing = -1
    depth = y_back - y_front
    z0, z1 = 0.140, 1.955
    for x in xs:
        bx(mb, part, x, (y_back + y_front) * 0.5, (z0 + z1) * 0.5,
           0.04, depth, z1 - z0, bevel=0.0)
        back_fy = y_back - (0.06 if north else 0.12)
        for fy in (back_fy, y_front + 0.06):
            bx(mb, edge, x, fy, 0.082, 0.06, 0.06, 0.15)
        # Remate superior de acero.
        bx(mb, edge, x, (y_back + y_front) * 0.5, z1 + 0.020,
           0.06, depth, 0.024)
    # Larguero frontal superior.
    bx(mb, edge, (xs[0] + xs[-1]) * 0.5, y_front, 1.98,
       xs[-1] - xs[0], 0.045, 0.04)
    for i in range(len(xs) - 1):
        bay = xs[i + 1] - xs[i]
        x = (xs[i] + xs[i + 1]) * 0.5
        toilet(mb, x, toilet_y, facing)
        # Puerta: una hoja abierta en el vano 3 norte y en el 2 sur.
        if not ((north and i == 2) or ((not north) and i == 1)):
            w = bay - 0.09
            bx(mb, door_mat, x, door_y, 0.145 + 0.850,
               w, 0.03, 1.70, bevel=0.0)
            bx(mb, edge, x, door_y - 0.018 * facing, 1.87,
               w, 0.012, 0.04)
            # Bisagras y pestillo.
            cyl(mb, chrome, x - w * 0.5 + 0.035, door_y,
                0.35, 0.014, 0.02, axis="Y", segments=10)
            cyl(mb, chrome, x - w * 0.5 + 0.035, door_y,
                1.45, 0.014, 0.02, axis="Y", segments=10)
            bx(mb, chrome, x + w * 0.5 - 0.06, door_y - 0.034 * facing,
               1.02, 0.06, 0.02, 0.10)
            # Indicador de ocupado.
            occ = M("M_RS_Red") if i in (0, 3) else M("M_RS_Green")
            cyl(mb, occ, x + w * 0.5 - 0.10,
                door_y - 0.028 * facing, 1.58, 0.030, 0.012,
                axis="Y", segments=12)
        else:
            # Puerta retirada: bisagras rotas y marco.
            cyl(mb, chrome, xs[i] + 0.04, door_y, 0.42, 0.016, 0.03,
                axis="Y", segments=10)
            cyl(mb, chrome, xs[i] + 0.04, door_y, 1.38, 0.016, 0.03,
                axis="Y", segments=10)
        # Dispensador de papel en la particion izquierda.
        bx(mb, chrome, xs[i] + 0.055, y_front + 0.32 * facing,
           1.02, 0.035, 0.16, 0.20)
    # Barra de apoyo en el vano accesible (ultimo).
    xa0, xa1 = xs[-2], xs[-1]
    xa = (xa0 + xa1) * 0.5
    bx(mb, chrome, xa, y_back - 0.55 * facing, 0.86,
       xa1 - xa0 - 0.35, 0.035, 0.035)
    cyl(mb, chrome, xa0 + 0.14, y_back - 0.55 * facing, 0.43,
        0.017, 0.86, axis="Z", segments=10)
    cyl(mb, chrome, xa1 - 0.14, y_back - 0.55 * facing, 0.43,
        0.017, 0.86, axis="Z", segments=10)
    mb.build(col())


def urinals():
    mb = vest.MeshBuilder("RS_Urinals")
    ceramic = M("M_FM_Ceramic_White")
    chrome = M("M_RS_Chrome")
    part = M("M_RS_Partition")
    for x in (19.00, 19.80, 20.60):
        bx(mb, ceramic, x, 57.745, 1.00, 0.34, 0.10, 0.58, bevel=0.01)
        bx(mb, ceramic, x, 57.60, 0.86, 0.32, 0.22, 0.40, bevel=0.012)
        cyl(mb, chrome, x, 57.51, 1.10, 0.055, 0.02, axis="Y", segments=12)
        cyl(mb, chrome, x, 57.60, 0.66, 0.020, 0.08, axis="Y", segments=10)
    for x in (18.76, 19.40, 20.20, 20.96):
        bx(mb, part, x, 57.62, 1.06, 0.028, 0.42, 1.16)
        bx(mb, M("M_RS_PartitionEdge"), x, 57.63, 1.65, 0.04, 0.46, 0.025)
    mb.build(col())


def vanity(north=True):
    name = "RS_VanityNorth" if north else "RS_VanitySouth"
    mb = vest.MeshBuilder(name)
    paint = M("M_RS_PaintDark")
    top = M("M_RS_Ceiling")
    ceramic = M("M_FM_Ceramic_White")
    chrome = M("M_RS_Chrome")
    dark = M("M_RS_Water")
    if north:
        y0, y1 = 52.55, 57.55
        sinks = (53.25, 54.85, 56.45)
    else:
        y0, y1 = 42.60, 45.75
        sinks = (43.35, 44.95)
    cy = (y0 + y1) * 0.5
    # Mueble y encimera.
    bx(mb, paint, 18.50, cy, 0.47, 0.56, y1 - y0, 0.90)
    bx(mb, top, 18.50, cy, 0.945, 0.66, y1 - y0, 0.075, bevel=0.004)
    # Pies / zocalo.
    bx(mb, M("M_FM_Steel_Dark"), 18.50, cy, 0.032, 0.52, y1 - y0 - 0.06, 0.05)
    for sy in sinks:
        bx(mb, ceramic, 18.51, sy, 0.995, 0.42, 0.42, 0.040)
        bx(mb, dark, 18.51, sy, 1.021, 0.32, 0.32, 0.004)
        # Grifo.
        cyl(mb, chrome, 18.66, sy, 1.075, 0.020, 0.24, axis="Z",
            segments=10)
        cyl(mb, chrome, 18.60, sy, 1.175, 0.016, 0.22, axis="X",
            segments=10)
        # Jabonera.
        bx(mb, chrome, 18.66, sy + 0.30, 1.07, 0.08, 0.10, 0.18)
    # Puertas del mueble.
    for sy in sinks:
        bx(mb, M("M_RS_Partition"), 18.215, sy, 0.47, 0.02, 0.75, 0.72)
        bx(mb, chrome, 18.20, sy + 0.30, 0.80, 0.02, 0.03, 0.12)
    mb.build(col())


def mirrors_and_fixtures():
    mb = vest.MeshBuilder("RS_Mirrors_TRIM")
    mirror = M("M_RS_Mirror", "M_RS_Chrome")
    frame = M("M_FM_Steel_Dark")
    chrome = M("M_RS_Chrome")
    # Espejos del oeste, en dos tramos.
    for cy, length in ((55.05, 4.60), (44.17, 3.00)):
        bx(mb, frame, 18.205, cy, 1.66, 0.03, length + 0.12, 1.12)
        bx(mb, mirror, 18.225, cy, 1.66, 0.012, length, 1.02)
        bx(mb, frame, 18.205, cy, 1.10, 0.04, length + 0.14, 0.04)
        bx(mb, frame, 18.205, cy, 2.22, 0.04, length + 0.14, 0.04)
    # Dispensadores de jabon y toallas.
    for y, z, sz in ((52.82, 1.28, 0.30), (57.22, 1.35, 0.34),
                     (42.82, 1.28, 0.30), (45.48, 1.28, 0.30)):
        bx(mb, chrome, 18.225, y, z, 0.12, 0.16, sz)
        bx(mb, M("M_RS_PaintDark"), 18.285, y, z - sz * 0.32,
           0.015, 0.12, 0.04)
    # Secador de manos junto a la puerta norte.
    bx(mb, chrome, 18.24, 52.24, 1.30, 0.17, 0.26, 0.34)
    bx(mb, M("M_RS_PaintDark"), 18.335, 52.24, 1.18, 0.02, 0.18, 0.12)
    mb.build(col())


def cleaning_room():
    mb = vest.MeshBuilder("RS_CleaningRoom")
    wall = M("M_RS_Paint")
    tile = M("M_VEST_Tile", "M_FM_Concrete_Wall")
    dark = M("M_RS_PaintDark")
    ceramic = M("M_FM_Ceramic_White")
    chrome = M("M_RS_Chrome")
    # Tabiques: x=20.4 y42.19..44.75 y y=44.75 x18.19..20.4, con hueco de puerta.
    bx(mb, wall, 20.40, 43.46, 1.55, 0.08, 2.52, 3.10)
    bx(mb, wall, 20.05, 44.75, 1.55, 0.70, 0.08, 3.10)
    # Hoja abierta contra el tabique este.
    bx(mb, M("M_RS_Partition"), 20.32, 43.55, 1.06, 0.035, 0.78, 2.10)
    bx(mb, chrome, 20.33, 43.20, 1.05, 0.02, 0.06, 0.10)
    # Pileta de limpieza.
    bx(mb, tile, 19.50, 42.95, 0.38, 0.62, 0.54, 0.72, uv_scale=0.8)
    bx(mb, ceramic, 19.50, 42.95, 0.755, 0.54, 0.46, 0.05)
    bx(mb, dark, 19.50, 42.95, 0.787, 0.42, 0.34, 0.006)
    cyl(mb, chrome, 19.50, 42.83, 0.92, 0.018, 0.30, axis="Z", segments=10)
    cyl(mb, chrome, 19.50, 42.73, 1.02, 0.013, 0.18, axis="Y", segments=10)
    # Estante de quimicos.
    bx(mb, chrome, 20.27, 43.45, 1.52, 0.28, 1.10, 0.035)
    bx(mb, chrome, 20.27, 43.45, 1.86, 0.28, 1.10, 0.035)
    for i, y in enumerate((43.05, 43.35, 43.65, 43.95)):
        col_ = (M("M_RS_Green") if i % 2 == 0 else M("M_RS_Red"))
        bx(mb, col_, 20.28, y, 1.60, 0.12, 0.14, 0.18)
        bx(mb, M("M_VEST_Paper"), 20.28, y, 1.95, 0.10, 0.12, 0.14)
    # Cubo y fregona.
    cyl(mb, M("M_RS_WetFloor"), 18.85, 43.75, 0.19, 0.20, 0.38,
        axis="Z", segments=16)
    cyl(mb, chrome, 19.20, 43.90, 0.55, 0.012, 1.10, axis="Z",
        segments=8)
    bx(mb, M("M_VEST_Paper"), 19.20, 43.90, 0.08, 0.18, 0.10, 0.02)
    mb.build(col())


def ceiling():
    mb = vest.MeshBuilder("RS_Ceiling_DIFFUSER")
    slab = M("M_RS_Ceiling")
    grid = M("M_RS_Grid")
    # Losa superior que da continuidad y toca los muros.
    bx(mb, slab, 24.0, 50.0, 3.215, 11.7, 15.7, 0.03)
    # Marco perimetral.
    for y in (42.22, 57.78):
        bx(mb, grid, 24.0, y, 3.20, 11.64, 0.10, 0.08)
    for x in (18.22, 29.78):
        bx(mb, grid, x, 50.0, 3.20, 0.10, 15.64, 0.08)
    # Placas registrables 4x6.
    for ix in range(6):
        for iy in range(8):
            x = 19.15 + ix * 1.62
            y = 43.05 + iy * 1.86
            bx(mb, slab, x, y, 3.155, 1.54, 1.78, 0.035)
    mb.build(col())


def ceiling_lights():
    mb = vest.MeshBuilder("RS_LightPanels_LIGHT")
    em = M("M_RS_Emissive")
    frame = M("M_FM_Steel_Dark")
    for x in (20.60, 23.40, 26.20, 29.00):
        for y in (44.80, 55.00):
            bx(mb, frame, x, y, 3.146, 0.78, 0.78, 0.045)
            bx(mb, em, x, y, 3.120, 0.66, 0.66, 0.018)
    mb.build(col())


def services():
    mb = vest.MeshBuilder("RS_Services_CABLE")
    pipe = M("M_RS_PartitionEdge")
    grid = M("M_RS_Grid")
    # Dos colectores vistos bajo el techo.
    for y in (43.40, 56.40):
        cyl(mb, pipe, 24.0, y, 3.03, 0.045, 11.2, axis="X",
            segments=12)
        for x in (19.0, 24.0, 29.0):
            bx(mb, grid, x, y, 3.10, 0.04, 0.04, 0.16)
    # Rejillas de ventilacion en muro norte.
    for x in (24.6, 27.6):
        bx(mb, grid, x, 57.79, 2.85, 0.55, 0.03, 0.32)
        for i in range(5):
            bx(mb, M("M_FM_Steel_Dark"), x - 0.20 + i * 0.10, 57.765,
               2.85, 0.025, 0.01, 0.26)
    mb.build(col())

    # Bandeja de enlace con el pasillo y sleeve sobre la puerta oeste.
    mb = vest.MeshBuilder("RS_Tray_Link_CABLE")
    bx(mb, grid, 22.4, 50.2, 2.86, 14.0, 0.50, 0.05)
    for y in (49.96, 50.44):
        bx(mb, grid, 22.4, y, 2.91, 13.92, 0.04, 0.12)
    for x in (16.0, 19.0, 22.0, 25.0, 28.0, 29.2):
        bx(mb, grid, x, 50.2, 2.94, 0.04, 0.50, 0.10)
    for z in (2.70, 3.02):
        bx(mb, M("M_FM_Steel_Dark"), 18.0, 50.2, z, 0.10, 1.10, 0.06)
    for y in (49.65, 50.75):
        bx(mb, M("M_FM_Steel_Dark"), 18.0, y, 2.86, 0.08, 0.06, 0.34)
    mb.build(col())

    # Ramales desde los colectores existentes hasta la bandeja de enlace.
    mb = vest.MeshBuilder("RS_Tray_Branches_CABLE")
    for x in (20.5, 27.5):
        cyl(mb, grid, x, 46.8, 2.95, 0.045, 6.8, axis="Y", segments=10)
        cyl(mb, grid, x, 53.3, 2.95, 0.045, 6.2, axis="Y", segments=10)
    mb.build(col())

    # Red de agua: montantes y bajantes a lavabos.
    mb = vest.MeshBuilder("RS_Water_Supply_CABLE")
    copper = M("M_HERO_Copper", "M_RS_PartitionEdge")
    chrome = M("M_SH_Steel_Stainless", "M_RS_Chrome")
    for y0, y1, drops in ((52.4, 57.6, (53.2, 54.8, 56.4)),
                          (42.4, 45.8, (43.0, 44.8))):
        cyl(mb, copper, 18.30, (y0 + y1) * 0.5, 2.34, 0.028,
            y1 - y0, axis="Y", segments=10)
    for y in (53.2, 54.8, 56.4, 43.0, 44.8):
        cyl(mb, chrome, 18.43, y, 1.58, 0.016, 1.52, axis="Z",
            segments=10)
        bx(mb, chrome, 18.43, y, 2.32, 0.10, 0.10, 0.06)
        bx(mb, chrome, 18.43, y, 0.94, 0.16, 0.16, 0.04)
    # Montantes de alimentacion en las esquinas.
    for y in (42.5, 57.5):
        cyl(mb, copper, 18.34, y, 1.20, 0.035, 2.30, axis="Z",
            segments=10)
        bx(mb, M("M_RS_Red"), 18.34, y, 2.28, 0.12, 0.12, 0.06)
    mb.build(col())

    # Desagues: montantes verticales y sumideros de suelo.
    mb = vest.MeshBuilder("RS_Drain_Stacks_CABLE")
    for x, y in ((29.55, 44.8), (29.55, 55.2)):
        cyl(mb, chrome, x, y, 1.52, 0.055, 3.04, axis="Z",
            segments=12)
        cyl(mb, chrome, x, y, 2.98, 0.075, 0.08, axis="Z",
            segments=12)
        bx(mb, chrome, x, y, 0.06, 0.18, 0.18, 0.08)
    mb.build(col())

    mb = vest.MeshBuilder("RS_FloorDrains_GRILLE")
    for x, y in ((20.9, 44.0), (27.5, 56.0), (24.0, 50.0)):
        bx(mb, M("M_FM_Steel_Dark"), x, y, 0.006, 0.32, 0.32, 0.012)
        for i in range(5):
            bx(mb, chrome, x, y - 0.12 + i * 0.06, 0.014,
               0.26, 0.018, 0.008)
    mb.build(col())

    # Extraccion: conducto sobre los inodoros y extractor en esquina.
    mb = vest.MeshBuilder("RS_Extract_Duct_CABLE")
    galv = M("M_Z10_HERO_Steel_Galv_2K", "M_RS_Chrome")
    bx(mb, galv, 24.0, 57.55, 2.98, 10.8, 0.42, 0.24)
    for x in (24.6, 27.6):
        bx(mb, galv, x, 57.55, 2.82, 0.34, 0.32, 0.12)
    bx(mb, galv, 29.50, 57.55, 3.00, 0.46, 0.52, 0.24)
    for i in range(3):
        bx(mb, M("M_FM_Steel_Dark"), 29.34 + i * 0.08, 57.28,
           2.99, 0.035, 0.015, 0.18)
    mb.build(col())


def signage():
    white = M("M_MT_EmissiveWhite", "M_CTRL_White")
    green = M("M_RS_Green")
    dark = M("M_RS_PaintDark")
    text_sign("RS_Sign_Aseo_SIGN", "ASEO", 0.36, (18.10, 49.1, 2.98),
              (1, 0, 0), white)
    text_sign("RS_Sign_Wash_SIGN", "LAVADO DE MANOS", 0.15,
              (18.20, 55.0, 2.44), (1, 0, 0), white)
    text_sign("RS_Sign_Exit_SIGN", "SALIDA", 0.24, (29.84, 50.0, 2.72),
              (-1, 0, 0), white)
    text_sign("RS_Sign_Nexus_SIGN", "NEXUS", 0.12,
              (18.10, 46.7, 2.55), (1, 0, 0), green)
    # Cartel de suelo mojado: caballete amarillo con panel.
    mb = vest.MeshBuilder("RS_WetFloorSign_SIGN")
    bx(mb, M("M_RS_PaintDark"), 19.55, 52.46, 0.42, 0.48, 0.05, 0.80,
       bevel=0.004)
    bx(mb, M("M_RS_WetFloor"), 19.55, 52.43, 0.42, 0.44, 0.012, 0.72,
       bevel=0.003)
    bx(mb, M("M_RS_PaintDark"), 19.55, 52.425, 0.45,
       0.24, 0.008, 0.34)
    bx(mb, M("M_RS_WetFloor"), 19.55, 52.414, 0.52,
       0.055, 0.006, 0.16)
    bx(mb, M("M_RS_WetFloor"), 19.55, 52.414, 0.36,
       0.055, 0.006, 0.055)
    mb.build(col())
    # Indicador WC junto a la puerta oeste.
    mb = vest.MeshBuilder("RS_Sign_WC_SIGN")
    bx(mb, green, 18.17, 45.55, 2.55, 0.02, 0.30, 0.30)
    bx(mb, dark, 18.158, 45.55, 2.55, 0.01, 0.20, 0.20)
    mb.build(col())


def props_and_narrative():
    mb = vest.MeshBuilder("RS_Extinguisher")
    red = M("M_FM_Extinguisher_Red", "M_RS_Red")
    dark = M("M_FM_Steel_Dark")
    cx, cy = 29.72, 47.20
    cyl(mb, red, cx, cy, 0.36, 0.10, 0.56, axis="Z", segments=14)
    cyl(mb, red, cx, cy, 0.66, 0.055, 0.12, axis="Z", segments=10)
    bx(mb, dark, cx, cy, 0.74, 0.06, 0.06, 0.12)
    bx(mb, dark, 29.835, cy, 0.50, 0.035, 0.12, 0.20)
    bx(mb, dark, cx, cy, 1.02, 0.12, 0.03, 0.32)
    mb.build(col())

    mb = vest.MeshBuilder("RS_Puddles_DIS_WATER")
    water = M("M_VEST_Puddle", "M_RS_Water")
    for (x, y, sx, sy) in ((19.35, 45.25, 0.80, 0.50),
                           (19.20, 53.65, 0.60, 0.42),
                           (22.30, 43.30, 0.50, 0.35)):
        bx(mb, water, x, y, 0.008, sx, sy, 0.004, rot=(0, 0, 0.2))
    mb.build(col())

    mb = vest.MeshBuilder("RS_Papers_PAPER")
    paper = M("M_VEST_Paper")
    for i, (x, y, rz) in enumerate(((22.55, 55.15, 0.4),
                                    (26.95, 46.85, -0.3),
                                    (19.85, 50.55, 0.9),
                                    (28.90, 44.60, 0.1))):
        bx(mb, paper, x, y, 0.016 + i * 0.001, 0.21, 0.29, 0.003,
           rot=(0, 0, rz))
    mb.build(col())

    mb = vest.MeshBuilder("RS_BrokenTiles_DECAL")
    tile = M("M_VEST_Tile", "M_FM_Concrete_Floor")
    for i, (x, y, rz) in enumerate(((29.05, 51.25, 0.4),
                                    (28.80, 51.55, -0.2),
                                    (29.25, 51.05, 0.9))):
        bx(mb, tile, x, y, 0.012 + i * 0.001, 0.18, 0.14, 0.004,
           rot=(0, 0, rz))
    mb.build(col())

    mb = vest.MeshBuilder("RS_ToppledBucket")
    yellow = M("M_RS_WetFloor")
    bx(mb, yellow, 19.30, 44.20, 0.22, 0.38, 0.38, 0.30,
       rot=(0, 0.35, 0.3))
    bx(mb, M("M_FM_Steel_Dark"), 19.15, 44.10, 0.31, 0.10, 0.10, 0.02,
       rot=(0, 0.35, 0.3))
    mb.build(col())

    # Rastro discreto hacia la puerta este.
    mb = vest.MeshBuilder("RS_BloodTrail_BLOOD")
    blood = M("M_WH_Blood", "M_RS_Red")
    for i, (x, y, sx, sy) in enumerate(((20.55, 45.20, 0.18, 0.35),
                                        (21.60, 46.00, 0.16, 0.30),
                                        (22.85, 46.90, 0.13, 0.26),
                                        (24.20, 47.55, 0.11, 0.20))):
        bx(mb, blood, x, y, 0.010, sx, sy, 0.003, rot=(0, 0, -0.5 - i * 0.1))
    mb.build(col())

    # Huella en el espejo norte.
    mb = vest.MeshBuilder("RS_Handprint_DECAL")
    blood = M("M_WH_Blood", "M_RS_Red")
    for i, (y, z, sy, sz) in enumerate(((54.82, 1.62, 0.035, 0.16),
                                        (54.90, 1.63, 0.030, 0.15),
                                        (54.98, 1.63, 0.030, 0.15),
                                        (55.06, 1.62, 0.030, 0.12),
                                        (54.88, 1.48, 0.055, 0.09))):
        bx(mb, blood, 18.238, y, z, 0.006, sy, sz)
    mb.build(col())


def build():
    clean()
    materials()
    wainscot()
    floor_tiles()
    stalls(True)
    stalls(False)
    urinals()
    vanity(True)
    vanity(False)
    mirrors_and_fixtures()
    cleaning_room()
    ceiling()
    ceiling_lights()
    services()
    signage()
    props_and_narrative()
    bpy.context.view_layer.update()
    tris = sum(len(p.vertices) - 2 for ob in col().objects if ob.type == "MESH"
               for p in ob.data.polygons)
    print("RESTROOM_BUILD objects=%d tris=%d" % (len(col().objects), tris))


if __name__ == "__main__":
    build()
