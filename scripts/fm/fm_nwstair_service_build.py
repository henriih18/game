"""Sala técnica de NWStair (Opción B de verticalidad).

Construye una sala de servicio realista de 8 x 6 m a cota -4,5, conectada a la
meseta inferior de NWStair por un espolón de 2 m. Todo el mobiliario y la
maquinaria son geometría propia con proporciones reales, biseles y UVs; no se
copian props de otras salas ni se añaden objetos narrativos.

Colección: L1_ART_NWSTAIR_SERVICE
"""

import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fm_warehouse_build as wh  # noqa: E402

vest = wh.vest

COL_NAME = "L1_ART_NWSTAIR_SERVICE"
wh.COL_NAME = COL_NAME

# Cotas principales (Blender; Godot z = -y).
FLOOR_TOP = -4.50
FLOOR_BOT = -4.70
CEIL_BOT = -1.90
CEIL_TOP = -1.70
X0, X1 = -76.0, -68.0          # caras interiores
Y0, Y1 = 64.5, 70.5            # caras interiores
CX, CY = (X0 + X1) * 0.5, (Y0 + Y1) * 0.5
DOOR_X0, DOOR_X1 = -72.90, -71.10
DOOR_TOP = -2.15
WALL_T = 0.30


# ---------------------------------------------------------------------------
# Materiales
# ---------------------------------------------------------------------------

def materials():
    M = {}
    M["concrete"] = wh.get_mat("M_FM_Concrete_Wall")
    M["floor"] = wh.get_mat("M_FM_Concrete_Floor")
    M["paint"] = wh.get_mat("M_FM_Painted_Green")
    M["panel"] = wh.get_mat("M_FM_Metal_Panel")
    M["steel"] = wh.get_mat("M_FM_Steel_Dark")
    M["steel2"] = wh.get_mat("M_HERO_Steel_Dark")
    M["galv"] = wh.get_mat("M_WH_Galv")
    M["yellow"] = wh.get_mat("M_FM_Safety_Yellow")
    M["wood"] = wh.get_mat("M_FM_Workbench_Wood")
    M["water"] = wh.get_mat("M_MT_PipeWater")
    M["steam"] = wh.get_mat("M_MT_PipeSteam")
    M["insul"] = wh.get_mat("M_MT_Insulation")
    M["rubber"] = wh.get_mat("M_FM_Rubber")
    M["white"] = wh.get_mat("M_MT_EmissiveWhite")
    M["cool"] = wh.get_mat("M_VEST_Emissive_Cool")
    M["red"] = wh.get_mat("M_VEST_Red")
    M["label"] = wh.get_mat("M_VEST_Paper")
    M["gauge"] = wh.mat("M_NWS_GaugeFace", (0.78, 0.80, 0.73), 0.30)
    M["needle"] = wh.mat("M_NWS_Needle", (0.55, 0.03, 0.02), 0.42)
    M["brass"] = wh.mat("M_NWS_Brass", (0.52, 0.33, 0.10), 0.32, 0.85)
    M["darkpaint"] = wh.mat("M_NWS_DarkPaint", (0.045, 0.060, 0.055), 0.55, 0.10)
    M["epoxy"] = wh.mat("M_NWS_Epoxy", (0.055, 0.095, 0.075), 0.48, 0.0)
    return M


# ---------------------------------------------------------------------------
# Helpers de modelado
# ---------------------------------------------------------------------------

def box(mb, m, cx, cy, cz, sx, sy, sz, bevel=0.0, segments=1,
        rot=(0, 0, 0)):
    mb.add_box((cx, cy, cz), (sx, sy, sz), m, bevel=bevel,
               segments=segments, rot=rot)


def cyl(mb, m, cx, cy, cz, radius, depth, axis="Z", segments=16, bevel=0.0):
    # Los biseles de cilindro generan anillos coplanares con las tapas y
    # disparan el z-fighting. Las tapas mecanizadas quedan limpias sin bisel.
    mb.add_cyl((cx, cy, cz), radius, depth, m, axis=axis,
               segments=segments, bevel=0.0)


def bolt(mb, m, x, y, z, axis="Z", radius=0.012):
    # 12 mm de largo: 3 mm dentro de la brida y 9 mm fuera. Antes la tapa
    # quedaba a 1,5 mm de la cara y el detector la marcaba como coplanar.
    cyl(mb, m, x, y, z, radius, 0.012, axis=axis, segments=8)


def flange(mb, m, x, y, z, r, thick, axis="Z", bolts=6):
    cyl(mb, m, x, y, z, r, thick, axis=axis, segments=24, bevel=0.002)
    # Tornillos en la cara del flange.
    if axis == "Z":
        for i in range(bolts):
            a = 2.0 * math.pi * i / bolts
            bolt(mb, m, x + (r - 0.014) * math.cos(a),
                 y + (r - 0.014) * math.sin(a), z + thick * 0.5 + 0.003,
                 axis="Z")
    elif axis == "Y":
        for i in range(bolts):
            a = 2.0 * math.pi * i / bolts
            bolt(mb, m, x + (r - 0.014) * math.cos(a), y + thick * 0.5 + 0.003,
                 z + (r - 0.014) * math.sin(a), axis="Y")
    else:
        for i in range(bolts):
            a = 2.0 * math.pi * i / bolts
            bolt(mb, m, x + thick * 0.5 + 0.003,
                 y + (r - 0.014) * math.cos(a),
                 z + (r - 0.014) * math.sin(a), axis="X")


def pipe(mb, m, p0, p1, radius, segments=16):
    """Cilindro entre dos puntos alineado a un eje."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    length = d.length
    if length < 1e-6:
        return
    c = (p0 + p1) * 0.5
    if abs(d.x) > max(abs(d.y), abs(d.z)):
        axis = "X"
    elif abs(d.y) > abs(d.z):
        axis = "Y"
    else:
        axis = "Z"
    cyl(mb, m, c.x, c.y, c.z, radius, length, axis=axis, segments=segments)


def valve(mb, M, x, y, z, axis="Z", size=0.10):
    m = M["red"]
    # Cuerpo de válvula de compuerta.
    if axis == "Z":
        cyl(mb, m, x, y, z, size * 1.15, size * 1.1, axis="Z", segments=20,
            bevel=0.003)
        cyl(mb, M["steel"], x, y, z + size * 0.75, size * 0.35, size * 0.6,
            axis="Z", segments=16)
        # Volante.
        cyl(mb, M["red"], x, y, z + size * 1.15, size * 1.25, 0.026,
            axis="Z", segments=28, bevel=0.003)
        for i in range(4):
            a = math.pi * 0.5 * i
            box(mb, M["red"], x + size * 0.62 * math.cos(a),
                y + size * 0.62 * math.sin(a), z + size * 1.15 - 0.004,
                size * 1.15, 0.024, 0.024, rot=(0, 0, a))
    elif axis == "X":
        cyl(mb, m, x, y, z, size * 1.15, size * 1.1, axis="X", segments=20,
            bevel=0.003)
        cyl(mb, M["steel"], x, y, z + size * 0.75, size * 0.35, size * 0.6,
            axis="Z", segments=16)
        cyl(mb, M["red"], x, y, z + size * 1.15, size * 1.25, 0.026,
            axis="Z", segments=28, bevel=0.003)


def gauge(mb, M, x, y, z, face="Y", radius=0.065):
    steel = M["steel"]
    if face == "Y":
        cyl(mb, steel, x, y, z, radius * 0.45, 0.045, axis="Y",
            segments=16, bevel=0.002)
        cyl(mb, M["brass"], x, y + 0.028, z, radius, 0.030, axis="Y",
            segments=24, bevel=0.002)
        cyl(mb, M["gauge"], x, y + 0.050, z, radius * 0.82, 0.006,
            axis="Y", segments=24)
        box(mb, M["needle"], x + radius * 0.25, y + 0.055, z,
            radius * 0.7, 0.004, 0.008, rot=(0, 0, math.radians(28)))
    else:
        cyl(mb, steel, x, y, z, radius * 0.45, 0.045, axis="X",
            segments=16, bevel=0.002)
        cyl(mb, M["brass"], x + 0.028, y, z, radius, 0.030, axis="X",
            segments=24, bevel=0.002)
        cyl(mb, M["gauge"], x + 0.050, y, z, radius * 0.82, 0.006,
            axis="X", segments=24)


def handwheel(mb, m, x, y, z, r=0.12, axis="Z"):
    cyl(mb, m, x, y, z, r, 0.024, axis=axis, segments=24, bevel=0.003)
    for i in range(4):
        a = math.pi * 0.5 * i
        box(mb, m, x + r * 0.6 * math.cos(a), y + r * 0.6 * math.sin(a),
            z, r * 1.0, 0.022, 0.022, rot=(0, 0, a))


# ---------------------------------------------------------------------------
# Arquitectura
# ---------------------------------------------------------------------------

def architecture(mb, M):
    concrete, paint = M["concrete"], M["paint"]
    steel, panel = M["steel"], M["panel"]

    # Losa de suelo, muros y techo. Solapes de 10 cm para evitar caras
    # coplanares en las esquinas.
    box(mb, M["floor"], CX, CY, (FLOOR_TOP + FLOOR_BOT) * 0.5,
        X1 - X0 + 0.4, Y1 - Y0 + 0.4, 0.20, bevel=0.015, segments=2)
    # Muro sur partido en dos tramos: el vano de la puerta debe ser real,
    # no un marco decorativo sobre un muro ciego.
    sw_y = Y0 - WALL_T * 0.5
    for wx0, wx1 in ((X0 - 0.2, DOOR_X0), (DOOR_X1, X1 + 0.2)):
        box(mb, concrete, (wx0 + wx1) * 0.5, sw_y, -3.225,
            wx1 - wx0, WALL_T, 2.75, bevel=0.012, segments=2)
    box(mb, concrete, CX, Y1 + WALL_T * 0.5, -3.225,
        X1 - X0 + 0.4, WALL_T, 2.75, bevel=0.012, segments=2)
    box(mb, concrete, X0 - WALL_T * 0.5, CY, -3.225,
        WALL_T, Y1 - Y0 + 0.4, 2.75, bevel=0.012, segments=2)
    box(mb, concrete, X1 + WALL_T * 0.5, CY, -3.225,
        WALL_T, Y1 - Y0 + 0.4, 2.75, bevel=0.012, segments=2)
    box(mb, concrete, CX, CY, (CEIL_BOT + CEIL_TOP) * 0.5,
        X1 - X0 + 0.4, Y1 - Y0 + 0.4, 0.20, bevel=0.012, segments=2)

    # Pilastras de esquina: dan lectura estructural y ocultan las juntas.
    for sx in (X0 + 0.09, X1 - 0.09):
        for sy in (Y0 + 0.09, Y1 - 0.09):
            box(mb, paint, sx, sy, -3.225, 0.18, 0.18, 2.75,
                bevel=0.012, segments=3)

    # Espolón de conexión con la meseta inferior.
    ex0, ex1 = -73.05, -70.95
    box(mb, M["floor"], (ex0 + ex1) * 0.5, 62.10,
        (FLOOR_TOP + FLOOR_BOT) * 0.5 - 0.001, ex1 - ex0, 4.55, 0.20,
        bevel=0.012, segments=2)
    box(mb, concrete, ex0 - 0.075, 62.10, -3.225, 0.15, 4.55, 2.75,
        bevel=0.010, segments=2)
    box(mb, concrete, ex1 + 0.075, 62.10, -3.225, 0.15, 4.55, 2.75,
        bevel=0.010, segments=2)
    box(mb, concrete, (ex0 + ex1) * 0.5, 62.10,
        (CEIL_BOT + CEIL_TOP) * 0.5 - 0.002, ex1 - ex0, 4.55, 0.20,
        bevel=0.010, segments=2)

    # Dintel del acceso a la sala.
    box(mb, concrete, (DOOR_X0 + DOOR_X1) * 0.5, Y0 - 0.06,
        (DOOR_TOP + CEIL_BOT) * 0.5, DOOR_X1 - DOOR_X0 + 0.16, 0.30,
        CEIL_BOT - DOOR_TOP + 0.09, bevel=0.010, segments=2)

    # Zócalo sanitario y panelado inferior de las paredes. En el muro sur
    # se interrumpen en el vano de la puerta.
    # Cada capa termina en un plano distinto para que las testas no sean
    # coplanares entre panel, remate y zócalo.
    for bx0, bx1 in ((X0 + 0.25, DOOR_X0 - 0.22),
                     (DOOR_X1 + 0.22, X1 - 0.25)):
        bcx = (bx0 + bx1) * 0.5
        bw = bx1 - bx0
        box(mb, paint, bcx, Y0 + 0.045, FLOOR_TOP + 0.585,
            bw, 0.040, 1.26, bevel=0.006, segments=2)
    for bx0, bx1 in ((X0 + 0.28, DOOR_X0 - 0.25),
                     (DOOR_X1 + 0.25, X1 - 0.28)):
        bcx = (bx0 + bx1) * 0.5
        bw = bx1 - bx0
        box(mb, steel, bcx, Y0 + 0.050, FLOOR_TOP + 1.215,
            bw, 0.055, 0.030, bevel=0.004, segments=2)
    sy = Y1 - 0.02
    box(mb, paint, CX, sy - 0.025, FLOOR_TOP + 0.585,
        X1 - X0 - 0.60, 0.040, 1.26, bevel=0.006, segments=2)
    box(mb, steel, CX, sy - 0.030, FLOOR_TOP + 1.215,
        X1 - X0 - 0.66, 0.055, 0.030, bevel=0.004, segments=2)
    for sx in (X0 + 0.02, X1 - 0.02):
        box(mb, paint, sx + (0.025 if sx < CX else -0.025), CY, FLOOR_TOP + 0.585,
            0.040, Y1 - Y0 - 0.60, 1.26, bevel=0.006, segments=2)
        box(mb, steel, sx + (0.030 if sx < CX else -0.030), CY, FLOOR_TOP + 1.215,
            0.055, Y1 - Y0 - 0.66, 0.030, bevel=0.004, segments=2)

    # Zócalo de goma, también interrumpido en el vano sur.
    for bx0, bx1 in ((X0 + 0.31, DOOR_X0 - 0.28),
                     (DOOR_X1 + 0.28, X1 - 0.31)):
        box(mb, M["rubber"], (bx0 + bx1) * 0.5, Y0 + 0.080,
            FLOOR_TOP + 0.055, bx1 - bx0, 0.070, 0.13,
            bevel=0.006, segments=2)
    box(mb, M["rubber"], CX, Y1 - 0.080, FLOOR_TOP + 0.055,
        X1 - X0 - 0.72, 0.070, 0.13, bevel=0.006, segments=2)
    for sx in (X0 + 0.035, X1 - 0.035):
        box(mb, M["rubber"], sx + (0.045 if sx < CX else -0.045), CY, FLOOR_TOP + 0.055,
            0.070, Y1 - Y0 - 0.72, 0.13, bevel=0.006, segments=2)

    # Vigas de techo.
    for y in (65.5, 67.5, 69.5):
        # Ala inferior visible 12 cm bajo el techo y alma embutida en la losa.
        box(mb, steel, CX, y, CEIL_BOT - 0.10, X1 - X0 - 0.44, 0.18, 0.06,
            bevel=0.006, segments=2)
        box(mb, steel, CX, y, CEIL_BOT - 0.03, X1 - X0 - 0.30, 0.06, 0.14,
            bevel=0.004, segments=2)
    # Canaleta central, separada 5 mm del techo.
    box(mb, panel, CX, CY, CEIL_BOT - 0.055, X1 - X0 - 0.6, 0.34, 0.10,
        bevel=0.006, segments=2)
    for x in (-75.0, -72.0, -69.0):
        box(mb, steel, x, CY, CEIL_BOT - 0.02, 0.10, 0.44, 0.08,
            bevel=0.004, segments=2)

    # Marco de puerta de acero.
    fx = 0.08
    box(mb, panel, DOOR_X0 + 0.055, Y0 - 0.02, -3.29, fx, 0.16, 2.44,
        bevel=0.0, segments=1)
    box(mb, panel, DOOR_X1 - 0.055, Y0 - 0.02, -3.29, fx, 0.16, 2.44,
        bevel=0.0, segments=1)
    box(mb, panel, (DOOR_X0 + DOOR_X1) * 0.5, Y0 - 0.02, DOOR_TOP + 0.02,
        DOOR_X1 - DOOR_X0 - 0.07, 0.16, 0.10, bevel=0.0, segments=1)
    for x in (DOOR_X0 - 0.16, DOOR_X1 + 0.16):
        for z in (FLOOR_TOP + 0.18, FLOOR_TOP + 2.10):
            bolt(mb, steel, x, Y0 - 0.10, z, axis="Y", radius=0.016)

    # Hoja de puerta abierta 105°, con bisagras y manilla.
    f = wh.Frame(DOOR_X0 + 0.06, Y0 - 0.03, math.radians(105.0))
    f.box(mb, 0.82, 0.0, -3.33, 1.64, 0.060, 2.32, M["panel"],
          bevel=0.010, segments=3)
    f.box(mb, 0.85, 0.045, -3.32, 1.50, 0.012, 1.10, M["paint"],
          bevel=0.004, segments=2)
    for z in (-4.35, -3.70, -2.45):
        # Bisagras detrás de la hoja (y local −0.040): antes quedaban tangentes
        # a su cara y el bisel del cilindro generaba bandas coplanares.
        f.cyl(mb, 0.02, -0.040, z, 0.030, 0.10, M["galv"], axis="Z",
              segments=12, bevel=0.0)
    f.box(mb, 1.53, -0.055, -3.45, 0.05, 0.10, 0.22, M["galv"],
          bevel=0.006, segments=3)
    f.box(mb, 1.53, -0.10, -3.45, 0.04, 0.05, 0.18, M["galv"],
          bevel=0.004, segments=2)
    f.box(mb, 1.55, 0.03, -2.40, 0.20, 0.012, 0.12, M["label"],
          bevel=0.002, segments=1)


# ---------------------------------------------------------------------------
# Maquinaria
# ---------------------------------------------------------------------------

def pump_skid(mb, M, cx, cy, rz=0.0):
    f = wh.Frame(cx, cy, rz)
    steel, galv, paint = M["steel"], M["galv"], M["paint"]

    # Plinto y bancada.
    f.box(mb, 0, 0, FLOOR_TOP + 0.07, 1.90, 1.15, 0.14, M["concrete"],
          bevel=0.010, segments=2)
    f.box(mb, 0, 0, FLOOR_TOP + 0.20, 1.74, 0.98, 0.10, steel,
          bevel=0.010, segments=3)
    for x in (-0.78, 0.78):
        for y in (-0.40, 0.40):
            f.box(mb, x, y, FLOOR_TOP + 0.11, 0.12, 0.12, 0.02, galv,
                  bevel=0.004, segments=2)

    # Motor eléctrico.
    f.cyl(mb, 0.30, 0.0, FLOOR_TOP + 0.50, 0.235, 0.62, M["darkpaint"],
          axis="X", segments=28, bevel=0.004)
    # Aletas de refrigeración.
    for i in range(11):
        x = 0.02 + i * 0.055
        f.cyl(mb, x, 0.0, FLOOR_TOP + 0.50, 0.252, 0.012, M["darkpaint"],
              axis="X", segments=24)
    f.cyl(mb, 0.62, 0.0, FLOOR_TOP + 0.50, 0.255, 0.06, steel, axis="X",
          segments=28, bevel=0.004)
    f.cyl(mb, -0.02, 0.0, FLOOR_TOP + 0.50, 0.255, 0.06, steel, axis="X",
          segments=28, bevel=0.004)
    # Caja de bornas.
    f.box(mb, 0.10, 0.0, FLOOR_TOP + 0.80, 0.24, 0.20, 0.12, steel,
          bevel=0.008, segments=3)
    f.box(mb, 0.10, 0.105, FLOOR_TOP + 0.80, 0.17, 0.012, 0.07, M["label"],
          bevel=0.002, segments=1)

    # Acoplamiento y guarda.
    f.cyl(mb, -0.42, 0.0, FLOOR_TOP + 0.50, 0.075, 0.30, galv, axis="X",
          segments=20)
    for x in (-0.60, -0.45, -0.30):
        f.cyl(mb, x, 0.0, FLOOR_TOP + 0.50, 0.16, 0.018, steel, axis="X",
              segments=24)
    f.box(mb, -0.44, 0.0, FLOOR_TOP + 0.66, 0.32, 0.05, 0.03, steel,
          bevel=0.004, segments=2)
    f.box(mb, -0.44, 0.0, FLOOR_TOP + 0.34, 0.32, 0.05, 0.03, steel,
          bevel=0.004, segments=2)

    # Voluta de bomba.
    f.cyl(mb, -0.82, 0.0, FLOOR_TOP + 0.50, 0.295, 0.34, paint, axis="X",
          segments=28, bevel=0.006)
    f.cyl(mb, -1.00, 0.0, FLOOR_TOP + 0.50, 0.155, 0.10, paint, axis="X",
          segments=24, bevel=0.004)
    # Brida de aspiración.
    f.cyl(mb, -1.07, 0.0, FLOOR_TOP + 0.50, 0.205, 0.035, galv, axis="X",
          segments=24, bevel=0.002)
    for i in range(8):
        a = 2 * math.pi * i / 8
        f.cyl(mb, -1.09, 0.17 * math.cos(a), FLOOR_TOP + 0.50 +
              0.17 * math.sin(a), 0.012, 0.008, steel, axis="X", segments=8)
    # Descarga superior.
    f.cyl(mb, -0.82, 0.0, FLOOR_TOP + 0.78, 0.115, 0.28, paint, axis="Z",
          segments=24)
    f.cyl(mb, -0.82, 0.0, FLOOR_TOP + 0.93, 0.155, 0.032, galv, axis="Z",
          segments=24, bevel=0.002)
    # Carcasa y eje visto.
    f.cyl(mb, -0.82, 0.0, FLOOR_TOP + 0.50, 0.070, 0.36, galv, axis="X",
          segments=20)
    # Patas de la bomba.
    for x in (-0.92, -0.70):
        f.box(mb, x, 0.0, FLOOR_TOP + 0.30, 0.12, 0.44, 0.16, paint,
              bevel=0.006, segments=3)

    # Válvula de aspiración y manómetro de descarga.
    valve(mb, M, cx - f.rz * 0.0 + math.cos(rz) * -1.22,
          cy + math.sin(rz) * -1.22, FLOOR_TOP + 0.50, axis="X", size=0.11)
    gx = cx + math.cos(rz) * -0.82
    gy = cy + math.sin(rz) * -0.82
    gauge(mb, M, gx, gy - 0.20, FLOOR_TOP + 1.05, face="Y", radius=0.070)
    box(mb, M["steel"], gx, gy - 0.10, FLOOR_TOP + 1.01, 0.04, 0.20, 0.04,
        bevel=0.004, segments=2)


def pipe_header(mb, M, x0, x1, y, z, radius, material, label):
    pipe(mb, material, (x0, y, z), (x1, y, z), radius, segments=20)
    # Bridas y soportes cada ~1,8 m.
    n = max(2, int(abs(x1 - x0) / 1.8) + 1)
    for i in range(n):
        x = x0 + (x1 - x0) * i / (n - 1)
        flange(mb, M["galv"], x, y, z, radius * 1.55, 0.045, axis="X",
               bolts=0)
        box(mb, M["steel"], x, y - radius - 0.09, z, 0.06, 0.10, 0.16,
            bevel=0.004, segments=2)
        box(mb, M["steel"], x, y - radius - 0.15, z + 0.10, 0.05, 0.05,
            0.30, bevel=0.004, segments=2)
    # Etiqueta de medio.
    wh.text_sign(f"NWS_Label_{label}_SIGN", label, 0.075,
                 (x0 + (x1 - x0) * 0.5, y - radius - 0.012, z + 0.16),
                 (0, -1, 0), M["label"], extrude=0.0015)


def machinery(mb, M):
    # Dos bombas centrífugas, ejes alineados con X.
    pump_skid(mb, M, -74.30, 66.85)
    pump_skid(mb, M, -70.00, 66.85)

    # Cabeceras de agua y vapor en el muro norte.
    pipe_header(mb, M, -75.55, -68.45, 70.18, -2.26, 0.105, M["water"], "AGUA")
    pipe_header(mb, M, -75.55, -68.45, 70.18, -2.70, 0.125, M["insul"], "VAPOR")

    # Bajantes a las bombas y colector de aspiración.
    for px in (-74.30, -70.00):
        pipe(mb, M["water"], (px, 70.18, -2.26), (px, 68.10, -2.26), 0.075)
        pipe(mb, M["water"], (px, 68.10, -2.26), (px, 68.10, -3.65), 0.075)
        pipe(mb, M["water"], (px, 68.10, -3.65), (px, 67.85, -3.65), 0.075)
        flange(mb, M["galv"], px, 68.10, -2.95, 0.11, 0.035, axis="Z")
        valve(mb, M, px, 68.10, -3.15, axis="Z", size=0.085)
        gauge(mb, M, px, 70.01, -2.24, face="Y", radius=0.060)

    # Colector de aspiración hacia la pared oeste.
    pipe(mb, M["water"], (-75.55, 66.85, -3.65), (-74.30, 66.85, -3.65),
         0.075)
    pipe(mb, M["water"], (-71.50, 66.85, -3.65), (-70.00, 66.85, -3.65),
         0.075)
    # Descargas al techo y al colector de vapor.
    for px in (-74.30, -70.00):
        pipe(mb, M["steam"], (px, 66.85, -3.55), (px, 66.85, -2.15),
             0.070, segments=16)
        flange(mb, M["galv"], px, 66.85, -2.55, 0.105, 0.032, axis="Z")
        valve(mb, M, px, 66.85, -2.72, axis="Z", size=0.080)

    # Válvulas de aislamiento junto a las cabeceras.
    valve(mb, M, -75.20, 70.18, -2.26, axis="X", size=0.095)
    valve(mb, M, -68.80, 70.18, -2.26, axis="X", size=0.095)

    # Soportes de tubería en el techo.
    for x in (-75.2, -73.0, -70.8, -68.7):
        box(mb, M["steel"], x, 70.18, -2.05, 0.06, 0.08, 0.64,
            bevel=0.004, segments=2)
        box(mb, M["steel"], x, 70.18, -1.92, 0.05, 0.42, 0.05,
            bevel=0.004, segments=2)


# ---------------------------------------------------------------------------
# Eléctrico, banco, servicios
# ---------------------------------------------------------------------------

def electrical(mb, M):
    steel, galv, paint = M["steel"], M["galv"], M["paint"]
    # Tres armarios de suelo en el muro oeste.
    for i, cy in enumerate((65.30, 66.15, 67.00)):
        cx = -75.70
        box(mb, paint, cx, cy, -3.60, 0.30, 0.72, 1.80,
            bevel=0.010, segments=3)
        # Puerta con bisagras y pestillo.
        box(mb, steel, cx + 0.17, cy, -3.60, 0.035, 0.64, 1.68,
            bevel=0.006, segments=3)
        for z in (-4.25, -3.60, -2.95):
            cyl(mb, galv, cx + 0.195, cy - 0.28, z, 0.014, 0.085,
                axis="Z", segments=10, bevel=0.001)
        box(mb, galv, cx + 0.20, cy + 0.28, -3.50, 0.030, 0.055, 0.14,
            bevel=0.004, segments=2)
        # Filas de breakers.
        for row in range(4):
            z = -3.95 + row * 0.30
            box(mb, M["darkpaint"], cx + 0.205, cy, z, 0.030, 0.48, 0.20,
                bevel=0.003, segments=2)
            for k in range(4):
                box(mb, M["label"], cx + 0.225, cy - 0.17 + k * 0.113,
                    z, 0.006, 0.070, 0.12, bevel=0.001, segments=1)
        # Etiqueta de riesgo.
        box(mb, M["yellow"], cx + 0.225, cy + 0.20, -2.55, 0.006, 0.22,
            0.16, bevel=0.001, segments=1)
        wh.text_sign(f"NWS_Label_Elec_{i}_SIGN", "RIESGO ELECTRICO", 0.045,
                     (cx + 0.231, cy + 0.20, -2.55), (1, 0, 0),
                     M["darkpaint"], extrude=0.0012)

    # Bandeja de cables sobre los armarios.
    tray_y = 65.15
    tray_z = -2.02
    box(mb, galv, -72.20, tray_y, tray_z, 6.9, 0.50, 0.04,
        bevel=0.004, segments=2)
    for sy in (-0.24, 0.24):
        box(mb, galv, -72.20, tray_y + sy, tray_z + 0.07, 6.9, 0.04, 0.12,
            bevel=0.004, segments=2)
    for i in range(12):
        x = -75.45 + i * 0.60
        box(mb, galv, x, tray_y, tray_z + 0.040, 0.04, 0.40, 0.05,
            bevel=0.002, segments=1)
    for k, (dy, m) in enumerate(((-0.10, M["darkpaint"]),
                                 (0.0, M["red"]), (0.10, M["steel"]))):
        pipe(mb, m, (-75.55, tray_y + dy, tray_z + 0.075),
             (-68.75, tray_y + dy, tray_z + 0.075), 0.018, segments=10)
    # Soportes de bandeja al techo.
    for x in (-75.2, -72.2, -69.2):
        box(mb, steel, x, tray_y, -1.98, 0.05, 0.06, 0.32,
            bevel=0.003, segments=2)

    # Conduits desde los armarios a la bandeja. Tramos ortogonales en
    # carriles distintos para que no se crucen ni generen coplanaridad.
    for i, cy in enumerate((65.30, 66.15, 67.00)):
        lane_x = -74.60 - i * 0.065
        pipe(mb, galv, (-75.48, cy, -2.70), (-75.48, cy, -2.02),
             0.028, segments=12)
        pipe(mb, galv, (-75.48, cy, -2.02), (lane_x, cy, -2.02),
             0.028, segments=12)
        pipe(mb, galv, (lane_x, cy, -2.02), (lane_x, 65.15, -2.02),
             0.028, segments=12)
        flange(mb, galv, -75.48, cy, -2.30, 0.045, 0.025, axis="Z",
               bolts=4)

    # Cuadro de control pequeño junto a la puerta, con placa de montaje.
    box(mb, steel, -74.90, 64.60, -2.60, 0.45, 0.10, 0.55,
        bevel=0.006, segments=2)
    box(mb, steel, -74.90, 64.72, -2.60, 0.55, 0.20, 0.75,
        bevel=0.008, segments=3)
    box(mb, M["cool"], -74.90, 64.83, -2.45, 0.38, 0.012, 0.20,
        bevel=0.002, segments=1)
    for k in range(3):
        cyl(mb, M["yellow"] if k == 0 else M["red"] if k == 1 else
            M["cool"], -75.10 + k * 0.20, 64.835, -2.72, 0.035, 0.014,
            axis="Y", segments=16)
    wh.text_sign("NWS_Label_Control_SIGN", "CONTROL NW-01", 0.040,
                 (-74.90, 64.84, -2.83), (0, 1, 0), M["label"],
                 extrude=0.0012)


def workbench(mb, M):
    steel, wood, galv = M["steel"], M["wood"], M["galv"]
    # Banco contra el muro este, 2,0 m de largo en Y.
    cx = -68.42
    cy = 69.35
    box(mb, wood, cx, cy, -3.58, 0.82, 2.00, 0.055,
        bevel=0.006, segments=3)
    box(mb, steel, cx, cy, -3.66, 0.76, 1.94, 0.04,
        bevel=0.004, segments=2)
    for sy in (-0.92, 0.92):
        for sx in (-0.34, 0.34):
            box(mb, steel, cx + sx, cy + sy, -4.08, 0.055, 0.055, 0.84,
                bevel=0.005, segments=2)
    box(mb, steel, cx, cy, -4.40, 0.68, 1.86, 0.035,
        bevel=0.004, segments=2)
    # Cajones.
    for i in range(3):
        box(mb, M["panel"], cx + 0.35, cy - 0.55 + i * 0.55, -3.88,
            0.08, 0.50, 0.26, bevel=0.005, segments=3)
        box(mb, galv, cx + 0.395, cy - 0.55 + i * 0.55, -3.88,
            0.015, 0.16, 0.025, bevel=0.002, segments=2)
    # Tornillo de banco.
    box(mb, steel, cx - 0.02, cy + 0.72, -3.47, 0.26, 0.18, 0.14,
        bevel=0.008, segments=3)
    box(mb, steel, cx - 0.14, cy + 0.72, -3.47, 0.10, 0.10, 0.18,
        bevel=0.006, segments=3)
    cyl(mb, galv, cx - 0.25, cy + 0.72, -3.47, 0.020, 0.30, axis="Y",
        segments=12)
    # Panel perforado con listones y herramientas colgadas.
    box(mb, M["panel"], cx + 0.38, cy, -2.82, 0.025, 1.60, 0.90,
        bevel=0.004, segments=2)
    for i in range(7):
        box(mb, M["darkpaint"], cx + 0.400, cy - 0.66 + i * 0.22,
            -2.82, 0.016, 0.045, 0.78, bevel=0.001, segments=1)
    # Herramientas: llave, destornillador y martillo. Las piezas se
    # intersectan por dentro, sin caras coplanares.
    # Llave de boca: mango plano + anillo embutido en el extremo.
    box(mb, galv, cx + 0.415, cy - 0.52, -2.58, 0.012, 0.22, 0.026,
        bevel=0.002, segments=2)
    cyl(mb, galv, cx + 0.415, cy - 0.62, -2.70, 0.030, 0.010,
        axis="X", segments=18)
    # Destornillador: mango y vástago solapados 2 mm.
    cyl(mb, M["red"], cx + 0.415, cy - 0.28, -2.56, 0.016, 0.090,
        axis="Z", segments=12)
    cyl(mb, galv, cx + 0.415, cy - 0.28, -2.67, 0.006, 0.100,
        axis="Z", segments=8)
    cyl(mb, galv, cx + 0.415, cy - 0.28, -2.72, 0.002, 0.020,
        axis="Z", segments=6)
    # Martillo: mango vertical y cabeza embutida.
    cyl(mb, M["wood"], cx + 0.415, cy - 0.02, -2.58, 0.011, 0.200,
        axis="Z", segments=10)
    box(mb, galv, cx + 0.415, cy - 0.02, -2.69, 0.014, 0.090, 0.045,
        bevel=0.002, segments=2)
    # Lámpara de banco.
    box(mb, M["darkpaint"], cx + 0.30, cy - 0.78, -3.54, 0.12, 0.12,
        0.025, bevel=0.004, segments=2)
    pipe(mb, galv, (cx + 0.30, cy - 0.78, -3.53),
         (cx + 0.24, cy - 0.78, -3.05), 0.012, segments=8)
    cyl(mb, M["darkpaint"], cx + 0.18, cy - 0.78, -2.98, 0.10, 0.14,
        axis="X", segments=16, bevel=0.006)
    cyl(mb, M["white"], cx + 0.10, cy - 0.78, -2.98, 0.075, 0.006,
        axis="X", segments=16)


def services(mb, M):
    steel, galv = M["steel"], M["galv"]
    # Extractor de pared con rejilla y conducto corto.
    box(mb, galv, -68.28, 68.10, -2.28, 0.16, 0.78, 0.62,
        bevel=0.008, segments=3)
    for i in range(7):
        box(mb, steel, -68.18, 67.78 + i * 0.106, -2.28, 0.020, 0.035,
            0.48, bevel=0.002, segments=1)
    cyl(mb, steel, -68.22, 68.10, -2.28, 0.20, 0.06, axis="X",
        segments=24, bevel=0.004)
    # Rejilla de impulsión sobre la puerta.
    box(mb, galv, -72.00, 64.74, -2.02, 0.90, 0.10, 0.26,
        bevel=0.006, segments=2)
    for i in range(6):
        box(mb, steel, -72.36 + i * 0.145, 64.80, -2.02, 0.030, 0.015,
            0.20, bevel=0.001, segments=1)
    # Desagüe de suelo con marco y slats.
    box(mb, steel, -69.20, 65.10, FLOOR_TOP + 0.008, 0.48, 0.48, 0.016,
        bevel=0.004, segments=2)
    for i in range(5):
        box(mb, galv, -69.38 + i * 0.09, 65.10, FLOOR_TOP + 0.019,
            0.035, 0.40, 0.006, bevel=0.001, segments=1)
    # Extintor realista en el muro este.
    ex, ey = -68.30, 65.10
    cyl(mb, M["red"], ex, ey, -3.95, 0.105, 0.56, axis="Z",
        segments=20, bevel=0.004)
    cyl(mb, M["red"], ex, ey, -3.64, 0.075, 0.08, axis="Z",
        segments=20, bevel=0.003)
    cyl(mb, galv, ex, ey, -3.60, 0.040, 0.10, axis="Z", segments=12)
    box(mb, steel, ex, ey, -3.40, 0.05, 0.05, 0.18, bevel=0.004,
        segments=2)
    pipe(mb, M["rubber"], (ex, ey, -3.58), (ex + 0.10, ey, -3.92),
         0.014, segments=8)
    gauge(mb, M, ex, ey + 0.12, -3.62, face="Y", radius=0.040)
    box(mb, M["label"], ex, ey + 0.108, -3.95, 0.12, 0.004, 0.18,
        bevel=0.001, segments=1)
    # Soporte de pared.
    box(mb, steel, ex - 0.06, ey, -3.95, 0.10, 0.16, 0.30,
        bevel=0.005, segments=2)

    # Líneas de suelo: perímetro de seguridad y pasillo.
    box(mb, M["yellow"], -72.0, 64.90, FLOOR_TOP + 0.006, 4.60, 0.07,
        0.006, bevel=0.0)
    box(mb, M["yellow"], -72.0, 66.00, FLOOR_TOP + 0.006, 4.60, 0.07,
        0.006, bevel=0.0)
    for px in (-74.30, -70.00):
        box(mb, M["yellow"], px, 66.85, FLOOR_TOP + 0.006, 2.20, 1.40,
            0.006, bevel=0.0)
    box(mb, M["yellow"], -72.00, 68.65, FLOOR_TOP + 0.006, 7.60, 0.07,
        0.006, bevel=0.0)

    # Flecha de salida.
    verts = [(-0.075, -0.32), (0.075, -0.32), (0.075, 0.06),
             (-0.075, 0.06), (-0.22, 0.06), (0.22, 0.06), (0.0, 0.30)]
    faces = [(0, 1, 2, 3), (3, 6, 4), (2, 5, 6)]
    uvs = [[(0, 0), (1, 0), (1, 1), (0, 1)], [(0, 0), (1, 0), (0.5, 1)],
           [(0.5, 0), (1, 1), (0, 0)]]
    z = FLOOR_TOP + 0.006
    pts = [(x - 72.0, y + 64.95) for (x, y) in verts]
    mb._append(M["yellow"], [(x, y, z) for (x, y) in pts], faces, uvs)


def lights_and_signs(mb, M):
    # Tres luminarias lineales LED.
    for x in (-74.60, -72.00, -69.40):
        box(mb, M["galv"], x, 67.50, CEIL_BOT + 0.045, 1.30, 0.18, 0.07,
            bevel=0.005, segments=2)
        box(mb, M["cool"], x, 67.50, CEIL_BOT + 0.005, 1.18, 0.12, 0.018,
            bevel=0.002, segments=1)
        for sy in (-0.55, 0.55):
            box(mb, M["steel"], x, 67.50 + sy, CEIL_BOT + 0.10, 0.05, 0.04,
                0.12, bevel=0.003, segments=2)

    # Baliza de emergencia sobre la puerta.
    box(mb, M["red"], -71.20, 64.56, -2.28, 0.16, 0.10, 0.10,
        bevel=0.006, segments=3)
    box(mb, M["red"], -71.20, 64.50, -2.33, 0.12, 0.04, 0.05,
        bevel=0.003, segments=2)
    box(mb, M["red"], -71.20, 64.50, -2.23, 0.12, 0.04, 0.05,
        bevel=0.003, segments=2)

    # Señalización funcional, sin objetos narrativos.
    wh.text_sign("NWS_Sign_Room_SIGN", "SALA TECNICA", 0.11,
                 (-72.00, 64.18, -2.03), (0, -1, 0), M["label"],
                 extrude=0.002)
    wh.text_sign("NWS_Sign_Exit_SIGN", "SALIDA", 0.12,
                 (-72.00, 64.52, -2.26), (0, 1, 0), M["label"],
                 extrude=0.002)
    wh.text_sign("NWS_Sign_NW01_SIGN", "NW-01", 0.10,
                 (-75.70, 67.62, -2.88), (0, 1, 0), M["label"],
                 extrude=0.002)
    wh.text_sign("NWS_Sign_NoBlock_SIGN", "NO BLOQUEAR", 0.070,
                 (-73.70, 64.52, -3.00), (0, 1, 0), M["label"],
                 extrude=0.0015)
    wh.text_sign("NWS_Sign_Elec_SIGN", "RIESGO ELECTRICO", 0.060,
                 (-75.46, 64.95, -2.55), (1, 0, 0), M["yellow"],
                 extrude=0.0015)


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build():
    if wh.COL_NAME != COL_NAME:
        wh.COL_NAME = COL_NAME
    wh.clean()
    M = materials()

    mb = vest.MeshBuilder("NWS_Architecture")
    architecture(mb, M)
    mb.build(wh.col())

    mb = vest.MeshBuilder("NWS_Pumps")
    machinery(mb, M)
    mb.build(wh.col())

    mb = vest.MeshBuilder("NWS_Electrical")
    electrical(mb, M)
    mb.build(wh.col())

    mb = vest.MeshBuilder("NWS_Workbench")
    workbench(mb, M)
    mb.build(wh.col())

    mb = vest.MeshBuilder("NWS_Services")
    services(mb, M)
    mb.build(wh.col())

    mb = vest.MeshBuilder("NWS_Lights")
    lights_and_signs(mb, M)
    mb.build(wh.col())

    c = wh.col()
    total_v = total_t = 0
    for ob in c.objects:
        if ob.type == "MESH":
            total_v += len(ob.data.vertices)
            total_t += sum(max(1, len(p.vertices) - 2) for p in ob.data.polygons)
    print(f"NWSTAIR_SERVICE_BUILD objects={len(c.objects)} verts={total_v} tris={total_t}")


if __name__ == "__main__":
    build()
