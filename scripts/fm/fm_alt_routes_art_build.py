"""FRECUENCIA MUERTA - arte de las rutas alternativas del Nivel 1 V06.

Viste las galerias y tuneles de servicio con la misma lectura industrial del
resto de la instalacion: conducciones de pared, abrazaderas, placas de
senalizacion, franjas de peligro, lineas de suelo y charcos.  No crea muros ni
suelos: la geometria de paso ya existe en alternate_routes.glb.

Todos los objetos nuevos llevan un token de omision de colision
(SIGN/CABLE/HAZ/FLOOR_LINE/DIS_WATER) para que FMGLBCollision no altere el
navmesh ni estreche los tuneles de 1,25 m.

Uso:
  blender -b nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend \
      --python scripts/fm/fm_alt_routes_art_build.py
"""
import math
import sys

import bpy
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
sys.path.insert(0, ROOT + "/scripts/fm")
import fm_warehouse_build as wh  # noqa: E402

wh.COL_NAME = "L1_ART_ALT_ROUTES"
vest = wh.vest
COL = "L1_ART_ALT_ROUTES"

M = {}


def make_materials():
    M["paint"] = wh.mat("M_ALT_Paint", (0.060, 0.090, 0.080), 0.62)
    M["panel"] = wh.mat("M_ALT_Panel", (0.105, 0.125, 0.115), 0.50, 0.15)
    M["text"] = wh.mat("M_ALT_Text", (0.78, 0.82, 0.74), 0.42)
    M["galv"] = wh.mat("M_ALT_Galv", (0.34, 0.37, 0.37), 0.36, 0.65)
    M["rust"] = wh.mat("M_ALT_Rust", (0.18, 0.085, 0.040), 0.86)
    M["yellow"] = wh.mat("M_ALT_Yellow", (0.62, 0.43, 0.030), 0.55)
    M["rubber"] = wh.mat("M_ALT_Rubber", (0.018, 0.020, 0.018), 0.92)
    M["emissive"] = wh.mat("M_ALT_Emissive", (0.08, 0.30, 0.22), 0.35,
                           emission=(0.10, 0.85, 0.55), strength=2.0)
    M["emerg"] = wh.mat("M_ALT_Emerg", (0.30, 0.03, 0.02), 0.40,
                        emission=(1.0, 0.08, 0.03), strength=2.5)
    M["water"] = wh.mat("M_ALT_Water", (0.020, 0.045, 0.050), 0.06)
    bsdf = next(n for n in M["water"].node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Alpha"].default_value = 0.34
    M["water"].surface_render_method = "BLENDED"


def pipe(mb, axis, start, end, z, radius=0.020, material=None):
    """Cilindro recto entre dos puntos del mismo eje (X o Y)."""
    mat = material or M["galv"]
    if axis == "X":
        x0, x1 = sorted((start, end))
        mb.add_cyl(((x0 + x1) * 0.5, 0.0, z), radius, x1 - x0, mat,
                   axis="X", segments=12)
    else:
        y0, y1 = sorted((start, end))
        mb.add_cyl((0.0, (y0 + y1) * 0.5, z), radius, y1 - y0, mat,
                   axis="Y", segments=12)


def pipe_x(mb, x0, x1, y, z, radius=0.020, material=None):
    mat = material or M["galv"]
    mb.add_cyl(((x0 + x1) * 0.5, y, z), radius, abs(x1 - x0), mat,
               axis="X", segments=12)


def pipe_y(mb, y0, y1, x, z, radius=0.020, material=None):
    mat = material or M["galv"]
    mb.add_cyl((x, (y0 + y1) * 0.5, z), radius, abs(y1 - y0), mat,
               axis="Y", segments=12)


def clamp_x(mb, x, y, z, axis="X"):
    if axis == "X":
        size = (0.055, 0.095, 0.095)
    else:
        size = (0.095, 0.055, 0.095)
    mb.add_box((x, y, z), size, M["panel"], bevel=0.0)


def conduit_x(mb, x0, x1, y, z, clamps=5, material=None):
    pipe_x(mb, x0, x1, y, z, material=material)
    for i in range(clamps):
        t = (i + 0.5) / clamps
        clamp_x(mb, x0 + (x1 - x0) * t, y, z, axis="X")


def conduit_y(mb, y0, y1, x, z, clamps=5, material=None):
    pipe_y(mb, y0, y1, x, z, material=material)
    for i in range(clamps):
        t = (i + 0.5) / clamps
        clamp_x(mb, x, y0 + (y1 - y0) * t, z, axis="Y")


def plate_and_sign(mb_plates, name, text, loc, normal, width=0.95,
                   height=0.24, text_size=0.115):
    n = Vector(normal).normalized()
    p = Vector(loc)
    # La placa se embute 2 mm en el paramento: la cara trasera queda dentro del
    # muro y la delantera 6 mm fuera, sin coplanaridad ni flotación.
    center = p - n * 0.002
    if abs(n.x) > 0.5:
        size = (0.016, width, height)
    elif abs(n.y) > 0.5:
        size = (width, 0.016, height)
    else:
        size = (width, height, 0.016)
    mb_plates.add_box(tuple(center), size, M["panel"], bevel=0.0)
    # Soporte embutido en el paramento: une la placa a la pared y evita que
    # el detector de QA la trate como una isla flotante.
    if abs(n.x) > 0.5:
        bracket = (0.18, 0.030, 0.030)
    elif abs(n.y) > 0.5:
        bracket = (0.030, 0.18, 0.030)
    else:
        bracket = (0.030, 0.030, 0.18)
    mb_plates.add_box(tuple(p - n * 0.10), bracket, M["galv"], bevel=0.0)
    # El texto queda 6 mm por delante de la placa para evitar coplanaridad.
    wh.text_sign(name + "_SIGN", text, text_size, tuple(p + n * 0.020), normal,
                 M["text"], extrude=0.002)


def hazard(mb, x, y, width, depth=0.10):
    mb.add_box((x, y, 0.004), (width, depth, 0.006), M["yellow"], bevel=0.0)


def puddle(mb, x, y, sx, sy, rz=0.0):
    mb.add_plane((x, y, 0.003), sx, sy, M["water"], rot=(0, 0, rz))


def build():
    make_materials()
    wh.clean()

    # --- Conducciones de pared -------------------------------------------------
    mb = vest.MeshBuilder("ALT_Conduits_CABLE")
    # EastGallery (eje Y, paredes x104.38 / x105.62)
    conduit_y(mb, -7.65, 7.65, 104.49, 1.28, 5)
    conduit_y(mb, -7.65, 7.65, 105.51, 1.28, 5, material=M["paint"])
    # MaintCorridor (eje X, paredes y-20.12 / y-18.88) y ramal
    conduit_x(mb, 2.35, 55.65, -20.01, 1.28, 9)
    conduit_x(mb, 2.35, 55.65, -18.99, 1.28, 9, material=M["paint"])
    conduit_y(mb, -18.55, -4.45, 19.89, 1.28, 4)
    conduit_y(mb, -18.55, -4.45, 21.11, 1.28, 4, material=M["paint"])
    # NorthConnector + NorthGallery
    conduit_y(mb, 60.3, 64.55, -94.48, 1.28, 2)
    conduit_y(mb, 60.3, 64.55, -93.52, 1.28, 2, material=M["paint"])
    conduit_x(mb, -95.65, -30.35, 64.99, 1.28, 11)
    conduit_x(mb, -95.65, -30.35, 66.01, 1.28, 11, material=M["paint"])
    # OfficesCrawl
    conduit_x(mb, -40.05, -30.3, 30.49, 1.28, 2)
    conduit_x(mb, -40.05, -30.3, 31.51, 1.28, 2, material=M["paint"])
    conduit_y(mb, 12.0, 31.55, -40.01, 1.28, 4)
    conduit_y(mb, 12.0, 31.55, -38.99, 1.28, 4, material=M["paint"])
    # ReceptionStair + enlace
    conduit_x(mb, -69.65, -12.35, -32.51, 1.28, 10)
    conduit_x(mb, -69.65, -12.35, -31.49, 1.28, 10, material=M["paint"])
    conduit_y(mb, -31.75, -4.35, -37.51, 1.28, 6)
    conduit_y(mb, -31.75, -4.35, -36.49, 1.28, 6, material=M["paint"])
    # ServiceLoop
    conduit_x(mb, 58.95, 69.75, 35.49, 1.28, 4)
    conduit_x(mb, 58.95, 69.75, 36.51, 1.28, 4, material=M["paint"])
    conduit_y(mb, 35.45, 39.85, 57.49, 1.28, 2)
    conduit_y(mb, 35.45, 39.85, 58.51, 1.28, 2, material=M["paint"])
    # NWStair: dos montantes de servicio en los muros laterales
    conduit_y(mb, 40.3, 59.7, -76.80, 2.55, 5, material=M["paint"])
    conduit_y(mb, 40.3, 59.7, -67.20, 2.55, 5)
    mb.build(wh.col())

    # --- Senalizacion ---------------------------------------------------------
    mb_plates = vest.MeshBuilder("ALT_SignPlates_SIGN")
    signs = [
        ("ALT_Sign_East_W", "GALERÍA ESTE", (104.50, 6.0, 0.95), (1, 0, 0), 0.078),
        ("ALT_Sign_East_M", "GALERÍA ESTE", (105.50, -6.0, 0.95), (-1, 0, 0), 0.078),
        ("ALT_Sign_Maint_S", "PASILLO TÉCNICO", (4.0, -19.00, 0.95), (0, -1, 0), 0.072),
        ("ALT_Sign_Maint_M", "PASILLO TÉCNICO", (54.0, -20.00, 0.95), (0, 1, 0), 0.072),
        ("ALT_Sign_North_C", "GALERÍA NORTE", (-92.0, 65.00, 0.95), (0, 1, 0), 0.078),
        ("ALT_Sign_North_O", "GALERÍA NORTE", (-32.0, 66.00, 0.95), (0, -1, 0), 0.078),
        ("ALT_Sign_Crawl_O", "CONDUCTO DE SERVICIO", (-34.0, 31.51, 0.95), (0, -1, 0), 0.060),
        ("ALT_Sign_Reception", "ACCESO RECEPCIÓN", (-68.0, -31.50, 0.95), (0, -1, 0), 0.070),
        ("ALT_Sign_ReceptLink", "ACCESO RECEPCIÓN", (-36.49, -20.0, 0.95), (-1, 0, 0), 0.066),
        ("ALT_Sign_Service_V", "ENLACE VESTUARIOS", (65.0, 36.51, 0.95), (0, -1, 0), 0.060),
        ("ALT_Sign_Service_W", "ENLACE VESTUARIOS", (57.516, 38.0, 0.95), (1, 0, 0), 0.060),
        ("ALT_Sign_NWStair", "ESCALERA NOROESTE", (-76.80, 50.0, 1.80), (1, 0, 0), 0.075),
        ("ALT_Sign_Security", "PASILLO DE SEGURIDAD", (-68.0, 10.20, 1.90), (0, 1, 0), 0.075),
    ]
    for name, text, loc, normal, size in signs:
        plate_and_sign(mb_plates, name, text, loc, normal, text_size=size)
    mb_plates.build(wh.col())

    # --- Franjas de peligro en las bocas --------------------------------------
    mb_haz = vest.MeshBuilder("ALT_Hazard_HAZ")
    hazard(mb_haz, 105.0, 7.90, 1.35)
    hazard(mb_haz, 105.0, -7.90, 1.35)
    hazard(mb_haz, 2.70, -19.5, 1.20, depth=0.10)
    hazard(mb_haz, 55.30, -19.5, 1.20, depth=0.10)
    hazard(mb_haz, -94.0, 60.55, 1.20)
    hazard(mb_haz, -30.55, 65.5, 1.20)
    hazard(mb_haz, -30.55, 31.1, 1.10)
    hazard(mb_haz, -69.55, -32.0, 1.20)
    mb_haz.build(wh.col())

    # --- Lineas de guiado y charcos -------------------------------------------
    mb_line = vest.MeshBuilder("ALT_FloorLines_FLOOR_LINE")
    mb_line.add_box((29.0, -19.82, 0.012), (52.0, 0.035, 0.012), M["yellow"])
    mb_line.add_box((-63.0, 65.82, 0.012), (64.0, 0.035, 0.012), M["yellow"])
    mb_line.add_box((-41.0, -31.82, 0.012), (56.0, 0.035, 0.012), M["yellow"])
    mb_line.build(wh.col())

    mb_pud = vest.MeshBuilder("ALT_Puddles_DIS_WATER")
    puddle(mb_pud, 105.0, 1.2, 0.62, 0.34, 0.4)
    puddle(mb_pud, 35.0, -19.5, 0.78, 0.38, -0.2)
    puddle(mb_pud, -64.0, 65.5, 0.70, 0.36, 0.8)
    puddle(mb_pud, -28.0, -32.0, 0.72, 0.34, -0.5)
    mb_pud.build(wh.col())

    # --- Balizas de servicio --------------------------------------------------
    beacons = ((105.0, 7.7), (2.5, -19.5), (55.5, -19.5),
               (-94.0, 60.5), (-30.3, 65.5), (-30.3, 31.1),
               (-69.9, -32.0))
    mb_led = vest.MeshBuilder("ALT_Beacons_LIGHT")
    for x, y in beacons:
        mb_led.add_box((x, y, 1.33), (0.12, 0.05, 0.08), M["emissive"], bevel=0.0)
    mb_led.build(wh.col())

    # Soportes al techo de los túneles (1,45 m) para que las balizas no floten.
    mb_stem = vest.MeshBuilder("ALT_BeaconStems_TRIM")
    for x, y in beacons:
        mb_stem.add_box((x, y, 1.405), (0.02, 0.02, 0.10), M["galv"], bevel=0.0)
    mb_stem.build(wh.col())

    print("ALT_ROUTES_ART objects=%d tris=%d" % (
        len(wh.col().objects),
        sum(len(o.data.polygons) * 2 for o in wh.col().objects if o.type == "MESH"),
    ))


if __name__ == "__main__":
    build()
