"""Viste Control de Acceso (Z04) en el master V06.

Idempotente: reconstruye L1_ART_CONTROL. No guarda el .blend ni toca otras
colecciones. Reutiliza MeshBuilder/materiales de Vestuarios y props existentes.
"""
import bpy
import bmesh
import math
import os
import importlib.util
from mathutils import Vector, Matrix

PROJECT = "/home/riyo/Documentos/game"
COL_NAME = "L1_ART_CONTROL"
VEST_PATH = os.path.join(PROJECT, "scripts", "fm", "fm_vestuarios_build.py")

_spec = importlib.util.spec_from_file_location("vest", VEST_PATH)
vest = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vest)
vest.ensure_materials()

# Caras interiores de la sala (Blender).
X0, X1 = -104.85, -77.15
Y0, Y1 = 40.15, 59.85
ZTOP = 6.0


def col():
    c = bpy.data.collections.get(COL_NAME)
    if c is None:
        c = bpy.data.collections.new(COL_NAME)
        bpy.context.scene.collection.children.link(c)
    return c


def mat(name, color, rough=0.6, metallic=0.0, emission=None, strength=0.0):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(b.outputs["BSDF"], out.inputs["Surface"])
    b.inputs["Base Color"].default_value = (*color, 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metallic
    if emission:
        b.inputs["Emission Color"].default_value = (*emission, 1.0)
        b.inputs["Emission Strength"].default_value = strength
    return m


def materials():
    mat("M_CTRL_Desk", (0.028, 0.055, 0.050), 0.58)
    mat("M_CTRL_DeskTop", (0.19, 0.21, 0.19), 0.36)
    glass = mat("M_CTRL_Glass", (0.030, 0.060, 0.070), 0.16, 0.05)
    gp = next(n for n in glass.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    gp.inputs["Alpha"].default_value = 0.22
    glass.surface_render_method = "BLENDED"
    mat("M_CTRL_Yellow", (0.62, 0.42, 0.02), 0.52)
    mat("M_CTRL_ScreenGlow", (0.02, 0.16, 0.20), 0.28, emission=(0.10, 0.65, 0.80), strength=3.0)
    mat("M_CTRL_ScreenDead", (0.004, 0.008, 0.010), 0.12)
    mat("M_CTRL_LED_Green", (0.01, 0.20, 0.07), 0.3, emission=(0.04, 0.62, 0.20), strength=1.35)
    mat("M_CTRL_LED_Red", (0.20, 0.01, 0.005), 0.3, emission=(0.82, 0.035, 0.015), strength=1.6)
    mat("M_CTRL_White", (0.72, 0.72, 0.66), 0.8)
    mat("M_CTRL_Dark", (0.012, 0.014, 0.015), 0.62)
    mat("M_CTRL_LampWarm", (0.35, 0.22, 0.08), 0.4,
        emission=(1.0, 0.62, 0.28), strength=3.0)
    mat("M_CTRL_WallStain", (0.035, 0.030, 0.026), 0.95)
    mat("M_CTRL_LightPanel", (0.55, 0.62, 0.62), 0.40,
        emission=(0.72, 0.85, 0.95), strength=1.15)
    mat("M_CTRL_CeilingPanel", (0.19, 0.20, 0.18), 0.88)
    mat("M_CTRL_CeilingStain", (0.09, 0.085, 0.07), 0.92)
    mat("M_CTRL_CeilingGrid", (0.10, 0.11, 0.10), 0.44, 0.65)


def clean():
    c = bpy.data.collections.get(COL_NAME)
    if c is None:
        return
    for ob in list(c.objects):
        data = ob.data
        bpy.data.objects.remove(ob, do_unlink=True)
        if data is not None and data.users == 0 and isinstance(data, bpy.types.Mesh):
            bpy.data.meshes.remove(data)
    bpy.data.collections.remove(c)


def text_sign(name, text, size, loc, normal, material, extrude=0.003):
    cu = bpy.data.curves.new("TMP_" + name, type="FONT")
    cu.body = text
    cu.size = size
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.extrude = extrude
    ob = bpy.data.objects.new("TMP_" + name, cu)
    bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    me.materials.append(material)
    ob2 = bpy.data.objects.new(name, me)
    col().objects.link(ob2)
    up = Vector((0, 0, 1))
    n = Vector(normal).normalized()
    right = up.cross(n).normalized()
    basis = Matrix((right, up, n)).transposed()
    ob2.matrix_world = Matrix.Translation(Vector(loc)) @ basis.to_4x4()
    bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.curves.remove(cu)
    return ob2


def copy_prop(src_name, name, x, y, z, rz=0.0, rx=0.0):
    src = bpy.data.objects.get(src_name)
    if src is None:
        print("MISSING_PROP", src_name)
        return None
    ob = src.copy()
    ob.data = src.data
    ob.animation_data_clear()
    col().objects.link(ob)
    ob.parent = None
    ob.name = name
    ob.hide_render = False
    ob.hide_set(False)
    minz = min(c[2] for c in src.bound_box)
    ob.matrix_world = (Matrix.Translation((x, y, z - minz))
                       @ Matrix.Rotation(rz, 4, "Z")
                       @ Matrix.Rotation(rx, 4, "X"))
    return ob


def simple_chair(name, x, y, z=0.0, rz=0.0, fallen=False):
    mb = vest.MeshBuilder(name)
    steel = bpy.data.materials["M_FM_Steel_Dark"]
    dark = bpy.data.materials["M_CTRL_Dark"]
    rubber = bpy.data.materials["M_FM_Rubber"]
    if fallen:
        mb.add_box((x, y, z + 0.14), (0.52, 0.48, 0.09), dark,
                   rot=(0, 0, rz))
        mb.add_box((x - 0.18, y + 0.10, z + 0.22), (0.52, 0.07, 0.52),
                   dark, rot=(math.radians(72), 0, rz))
        for sx in (-1, 1):
            for sy in (-1, 1):
                mb.add_box((x + sx * 0.18, y + sy * 0.16, z + 0.05),
                           (0.04, 0.04, 0.10), steel, rot=(0, 0, rz))
    else:
        mb.add_box((x, y, z + 0.46), (0.52, 0.50, 0.09), dark,
                   rot=(0, 0, rz))
        mb.add_box((x, y - 0.235, z + 0.77), (0.52, 0.07, 0.55), dark,
                   rot=(0, 0, rz))
        for sx in (-1, 1):
            for sy in (-1, 1):
                mb.add_box((x + sx * 0.20, y + sy * 0.18, z + 0.21),
                           (0.04, 0.04, 0.42), steel, rot=(0, 0, rz))
        mb.add_box((x, y, z + 0.08), (0.42, 0.38, 0.03), steel,
                   rot=(0, 0, rz))
        mb.add_box((x, y + 0.02, z + 0.33), (0.44, 0.06, 0.04), rubber,
                   rot=(0, 0, rz))
    mb.build(col())


def camera(name, x, y, z, rz):
    mb = vest.MeshBuilder(name)
    steel = bpy.data.materials["M_FM_Steel_Dark"]
    dark = bpy.data.materials["M_CTRL_Dark"]
    red = bpy.data.materials["M_CTRL_LED_Red"]
    mb.add_box((x, y, z), (0.26, 0.16, 0.16), dark, bevel=0.004,
               rot=(0, 0, rz))
    mb.add_cyl((x + 0.16 * math.cos(rz), y + 0.16 * math.sin(rz), z),
               0.055, 0.10, steel, axis="Y", segments=12, rot=(0, 0, rz))
    mb.add_box((x, y, z + 0.14), (0.10, 0.10, 0.12), steel,
               rot=(0, 0, rz))
    mb.add_box((x, y, z + 0.22), (0.30, 0.16, 0.04), steel,
               rot=(0, 0, rz))
    mb.add_box((x - 0.10 * math.cos(rz), y - 0.10 * math.sin(rz), z + 0.02),
               (0.02, 0.02, 0.02), red, rot=(0, 0, rz))
    mb.build(col())


def counter(name, cx, cy, length, rot=0.0):
    mb = vest.MeshBuilder(name)
    desk = bpy.data.materials["M_CTRL_Desk"]
    top = bpy.data.materials["M_CTRL_DeskTop"]
    panel = bpy.data.materials.get("M_FM_Metal_Panel", desk)
    painted = bpy.data.materials.get("M_FM_Painted_Green", desk)
    steel = bpy.data.materials["M_FM_Steel_Dark"]
    dark = bpy.data.materials["M_CTRL_Dark"]
    R = Matrix.Rotation(rot, 4, "Z")
    T = Matrix.Translation((cx, cy, 0))
    M = T @ R

    def P(x, y, z):
        return tuple(M @ Vector((x, y, z)))

    def B(c, s, m, **kw):
        mb.add_box(P(*c), s, m, rot=(0, 0, rot), **kw)

    # Cuerpo modular, zócalo retranqueado y encimera con borde.
    B((0, 0, 0.47), (length, 0.58, 0.84), desk)
    B((0, 0, 0.045), (length - 0.14, 0.48, 0.09), dark)
    B((0, 0, 0.925), (length + 0.10, 0.74, 0.05), top)
    B((0, -0.355, 0.925), (length + 0.08, 0.035, 0.06), steel)
    B((0, 0.305, 0.925), (length + 0.04, 0.025, 0.045), steel)
    # Tres módulos frontales con junta vertical y tirador.
    bay = length / 3.0
    for i in range(3):
        x = -length / 2 + (i + 0.5) * bay
        B((x, 0.305, 0.50), (bay - 0.06, 0.025, 0.66), panel)
        B((x, 0.323, 0.80), (bay - 0.16, 0.018, 0.035), steel)
        # Marco perimetral del módulo.
        for sx in (-1, 1):
            B((x + sx * (bay / 2 - 0.035), 0.318, 0.50),
              (0.025, 0.020, 0.70), steel)
        B((x, 0.318, 0.155), (bay - 0.05, 0.020, 0.025), steel)
    # Módulo de cajones en el extremo oeste.
    for j in range(3):
        z = 0.28 + j * 0.20
        B((-length / 2 + bay * 0.5, 0.330, z), (bay - 0.12, 0.030, 0.17),
          painted)
        B((-length / 2 + bay * 0.5, 0.350, z + 0.06),
          (bay - 0.22, 0.016, 0.022), steel)
    # Bandeja de cables y soportes bajo la encimera.
    B((0, 0.24, 0.84), (length - 0.12, 0.24, 0.035), steel)
    for x in (-length / 2 + 0.18, -0.6, 0.6, length / 2 - 0.18):
        B((x, 0.24, 0.80), (0.05, 0.28, 0.05), steel)
    # Tapas laterales y rodapié metálico.
    for sx in (-1, 1):
        B((sx * (length / 2 + 0.01), 0, 0.50), (0.025, 0.58, 0.82),
          panel)
    mb.build(col())


def turnstile_row():
    galv = bpy.data.materials.get("M_WH_Galv") or bpy.data.materials["M_FM_Metal_Panel"]
    steel = bpy.data.materials["M_FM_Steel_Dark"]
    dark = bpy.data.materials["M_CTRL_Dark"]
    green = bpy.data.materials["M_CTRL_LED_Green"]
    red = bpy.data.materials["M_CTRL_LED_Red"]
    screen = bpy.data.materials["M_CTRL_ScreenGlow"]
    xs = (-96.0, -93.0, -90.0, -87.0)
    for i, x in enumerate(xs):
        mb = vest.MeshBuilder("CTRL_Turnstile_%02d" % (i + 1))
        # Placa de anclaje, cuerpo de acero cepillado y tapa de acceso.
        mb.add_box((x, 47.5, 0.026), (0.46, 0.88, 0.024), dark, bevel=0.004)
        mb.add_box((x, 47.5, 0.52), (0.34, 0.76, 0.96), galv,
                   bevel=0.014, segments=3)
        mb.add_box((x, 47.5, 1.015), (0.38, 0.80, 0.05), dark,
                   bevel=0.008, segments=2)
        # Registros de mantenimiento a ambos lados, con tornillos.
        for sy in (-1, 1):
            yy = 47.5 + sy * 0.390
            mb.add_box((x, yy, 0.55), (0.24, 0.010, 0.58), steel,
                       bevel=0.003)
            for zz in (0.31, 0.79):
                for xx in (-0.09, 0.09):
                    mb.add_box((x + xx, yy + sy * 0.006, zz),
                               (0.018, 0.008, 0.018), dark)
        # Lector de tarjetas inclinado y pantalla.
        mb.add_box((x, 47.14, 1.09), (0.17, 0.13, 0.15), dark, bevel=0.005)
        mb.add_plane((x, 47.072, 1.11), 0.11, 0.075, screen,
                     rot=(math.radians(90), 0, 0))
        mb.add_box((x, 47.075, 1.055), (0.12, 0.006, 0.026), green)
        # Columna y cabezal de estado.
        mb.add_box((x, 47.5, 1.09), (0.09, 0.09, 0.12), dark)
        mb.add_box((x, 47.5, 1.165), (0.06, 0.06, 0.018),
                   red if i == 1 else green)
        # Eje y brazos de tripode (los carriles 2 y 3 quedan abiertos/rotos).
        if i not in (1, 2):
            mb.add_cyl((x, 47.5, 0.90), 0.062, 0.16, steel,
                       axis="Z", segments=16)
            for j in range(3):
                a = math.radians(j * 120 + 15)
                ax = math.cos(a) * 0.18
                ay = math.sin(a) * 0.18
                mb.add_box((x + ax, 47.5 + ay, 0.90),
                           (0.36, 0.038, 0.038), galv,
                           bevel=0.004, rot=(0, 0, a))
                mb.add_box((x + math.cos(a) * 0.355,
                            47.5 + math.sin(a) * 0.355, 0.90),
                           (0.045, 0.045, 0.045), dark,
                           rot=(0, 0, a))
        else:
            mb.add_cyl((x, 47.5, 0.90), 0.062, 0.08, steel,
                       axis="Z", segments=16)
        # Bumper de goma en la esquina de paso.
        mb.add_box((x, 47.5, 0.24), (0.36, 0.05, 0.06),
                   bpy.data.materials["M_FM_Rubber"], bevel=0.006)
        mb.build(col())
    # Lectores de tarjetas de pared, con base, pantalla y latiguillo.
    for i, (x, y) in enumerate(((-83.0, 40.8), (-77.55, 47.0))):
        mb = vest.MeshBuilder("CTRL_CardReader_%02d" % (i + 1))
        mb.add_box((x, y, 0.06), (0.22, 0.22, 0.12), dark, bevel=0.006)
        mb.add_box((x, y, 0.585), (0.12, 0.12, 1.00), galv,
                   bevel=0.008, segments=2)
        mb.add_box((x, y, 1.12), (0.22, 0.18, 0.12), dark, bevel=0.006)
        mb.add_plane((x, y - 0.096, 1.14), 0.10, 0.07, green,
                     rot=(math.radians(90), 0, 0))
        mb.add_cyl((x + 0.07, y + 0.08, 0.40), 0.010, 0.55,
                   bpy.data.materials["M_FM_Rubber"], axis="Z", segments=8)
        mb.build(col())


def guard_booth():
    desk = bpy.data.materials["M_CTRL_Desk"]
    steel = bpy.data.materials["M_FM_Steel_Dark"]
    galv = bpy.data.materials.get("M_WH_Galv") or bpy.data.materials["M_FM_Metal_Panel"]
    glass = bpy.data.materials["M_CTRL_Glass"]
    top = bpy.data.materials["M_CTRL_DeskTop"]
    dark = bpy.data.materials["M_CTRL_Dark"]
    # Plataforma, escalón y zócalo perimetral.
    mb = vest.MeshBuilder("CTRL_GuardBooth_Base")
    mb.add_box((-101.9, 56.7, 0.11), (5.1, 5.6, 0.22), desk, bevel=0.006)
    mb.add_box((-100.4, 53.55, 0.055), (1.8, 0.55, 0.11), steel, bevel=0.004)
    mb.add_box((-101.8, 53.92, 0.24), (5.0, 0.05, 0.08), galv, bevel=0.004)
    mb.build(col())
    # Cerramiento de aluminio y vidrio, con puerta practicable al sur.
    mb = vest.MeshBuilder("CTRL_GuardBooth_Glass")
    z0, z1 = 0.22, 3.05
    for x in (-104.3, -101.8, -99.35):
        mb.add_box((x, 54.0, 1.62), (0.07, 0.07, 2.80), galv,
                   bevel=0.006)
    mb.add_box((-101.8, 54.0, 3.08), (5.05, 0.10, 0.08), galv, bevel=0.006)
    mb.add_box((-101.8, 54.0, 0.52), (5.05, 0.10, 0.10), galv, bevel=0.006)
    for x0, x1 in ((-104.25, -103.42), (-102.48, -99.45)):
        mb.add_box(((x0 + x1) / 2, 54.03, 1.78),
                   (x1 - x0, 0.018, 2.36), glass)
    # Puerta de vidrio al sur, con marco y manilla.
    mb.add_box((-102.95, 54.0, 1.72), (0.05, 0.07, 2.32), galv)
    mb.add_box((-102.95, 54.03, 1.72), (0.88, 0.018, 2.10), glass)
    mb.add_box((-102.50, 54.08, 1.45), (0.025, 0.025, 0.52), galv)
    mb.add_box((-102.52, 54.10, 1.55), (0.10, 0.035, 0.035), dark)
    # Montantes laterales y traseros.
    mb.add_box((-104.25, 56.75, 1.63), (0.07, 5.35, 2.82), galv)
    mb.add_box((-99.40, 56.75, 1.63), (0.07, 5.35, 2.82), galv)
    # Persianas interiores en los laterales.
    for sy in (55.0, 56.4):
        for k in range(9):
            mb.add_box((-104.20, sy, 2.72 - k * 0.035),
                       (0.02, 1.18, 0.018), dark)
            mb.add_box((-99.45, sy, 2.72 - k * 0.035),
                       (0.02, 1.18, 0.018), dark)
    # Rejilla de ventilación en el frente y techo interior.
    for k in range(6):
        mb.add_box((-101.8, 54.06, 2.80 - k * 0.035),
                   (0.80, 0.02, 0.012), dark)
    mb.add_box((-101.8, 56.0, 3.03), (4.95, 5.2, 0.04), dark)
    mb.build(col())
    # Mostrador interior con cajonera y bandeja de cables.
    mb = vest.MeshBuilder("CTRL_GuardBooth_Desk")
    mb.add_box((-101.5, 56.8, 0.62), (3.6, 0.62, 0.78), desk)
    mb.add_box((-101.5, 56.8, 1.025), (3.8, 0.76, 0.05), top, bevel=0.004)
    mb.add_box((-101.5, 57.2, 0.68), (3.4, 0.04, 0.52), top)
    for x in (-102.7, -101.5, -100.3):
        mb.add_box((x, 56.48, 0.62), (0.95, 0.02, 0.62), desk, bevel=0.003)
        mb.add_box((x, 56.46, 0.78), (0.30, 0.03, 0.03), galv)
    mb.build(col())
    simple_chair("CTRL_Booth_Chair", -101.5, 55.7, 0.22, math.pi)
    # Puesto de monitorización con CRT encajados en carcasa.
    mb = vest.MeshBuilder("CTRL_Booth_Monitors")
    glow = bpy.data.materials["M_CTRL_ScreenGlow"]
    dead = bpy.data.materials["M_CTRL_ScreenDead"]
    for i, x in enumerate((-102.6, -101.5, -100.4)):
        mb.add_box((x, 57.0, 1.20), (0.44, 0.34, 0.38), dark, bevel=0.008)
        mb.add_box((x, 56.81, 1.22), (0.40, 0.025, 0.30), dark, bevel=0.004)
        mb.add_plane((x, 56.795, 1.22), 0.34, 0.24,
                     glow if i != 1 else dead,
                     rot=(math.radians(90), 0, 0))
        for k in range(4):
            mb.add_box((x, 56.79, 1.34 - k * 0.018),
                       (0.36, 0.012, 0.008), dark)
        mb.add_box((x, 56.95, 1.045), (0.40, 0.18, 0.03), dark)
    mb.add_box((-101.5, 56.45, 1.045), (0.18, 0.24, 0.05), dark)
    mb.build(col())


def server_racks():
    """Racks 19" de chapa con puerta perforada y detalles exentos.

    Se construyen como un cuerpo único y piezas separadas 4-8 mm para que no
    haya caras coplanares internas (QA de z-fighting).
    """
    steel = bpy.data.materials["M_FM_Steel_Dark"]
    galv = bpy.data.materials.get("M_WH_Galv") or bpy.data.materials["M_FM_Metal_Panel"]
    dark = bpy.data.materials["M_CTRL_Dark"]
    green = bpy.data.materials["M_CTRL_LED_Green"]
    red = bpy.data.materials["M_CTRL_LED_Red"]
    rubber = bpy.data.materials["M_FM_Rubber"]
    for i, y in enumerate((50.4, 51.6, 52.8)):
        mb = vest.MeshBuilder("CTRL_ServerRack_%02d" % (i + 1))
        # Cuerpo único del armario, del suelo al techo.
        mb.add_box((-78.0, y, 1.08), (0.78, 0.78, 2.06), steel,
                   bevel=0.008, segments=2)
        # Puerta de chapa, separada 5 mm del cuerpo.
        mb.add_box((-78.420, y, 1.08), (0.020, 0.70, 1.88), galv,
                   bevel=0.004, segments=2)
        # Ranuras de ventilación en la puerta, 4 mm por delante.
        for k in range(7):
            mb.add_box((-78.440, y, 0.38 + k * 0.20),
                       (0.008, 0.56, 0.030), dark, bevel=0.001)
        # Manilla y bisagras, separadas de la cara de la puerta.
        mb.add_box((-78.445, y + 0.30, 1.06), (0.012, 0.045, 0.22), steel,
                   bevel=0.002)
        for z in (0.36, 1.08, 1.80):
            mb.add_box((-78.445, y - 0.33, z), (0.012, 0.060, 0.10), steel,
                       bevel=0.002)
        # LEDs de estado en el frente superior.
        mb.add_box((-78.444, y + 0.24, 1.88), (0.008, 0.040, 0.014), green)
        mb.add_box((-78.444, y + 0.29, 1.88), (0.008, 0.040, 0.014), red)
        # Rejillas laterales, 6 mm fuera del cuerpo.
        for sx in (-1, 1):
            for k in range(6):
                mb.add_box((-78.0 + sx * 0.402, y, 0.40 + k * 0.26),
                           (0.010, 0.54, 0.045), dark, bevel=0.001)
        # Extractores en el techo, 4 mm por encima.
        for fx in (-0.18, 0.18):
            mb.add_cyl((-78.0 + fx, y, 2.14), 0.095, 0.045, dark,
                       axis="Z", segments=16)
        # Cables de datos por el lateral, separados del cuerpo y entre sí.
        for c in range(5):
            mb.add_cyl((-78.46, y + 0.24 + c * 0.014,
                        0.62 + c * 0.10), 0.010, 0.70,
                       rubber, axis="Z", segments=8)
        mb.build(col())


def key_cabinet():
    desk = bpy.data.materials["M_CTRL_Desk"]
    steel = bpy.data.materials["M_FM_Steel_Dark"]
    dark = bpy.data.materials["M_CTRL_Dark"]
    mb = vest.MeshBuilder("CTRL_KeyCabinet")
    mb.add_box((-104.62, 52.2, 2.10), (0.28, 2.00, 1.80), desk, bevel=0.005)
    for sx in (-1, 1):
        mb.add_box((-104.47, 52.2 + sx * 0.50, 2.10),
                   (0.02, 0.86, 1.62), dark)
        for j in range(5):
            mb.add_box((-104.45, 52.2 + sx * 0.50 - 0.28 + j * 0.14, 2.10),
                       (0.012, 0.012, 0.10), steel)
    mb.add_box((-104.47, 52.2, 3.02), (0.02, 1.92, 0.05), steel)
    mb.build(col())
    mb = vest.MeshBuilder("CTRL_KeyCabinet_Labels")
    mb.add_plane((-104.44, 52.2, 2.70), 0.55, 0.14,
                 bpy.data.materials["M_CTRL_White"],
                 rot=(0, math.radians(90), 0), uv_rect=(0, 1, 1, 0))
    mb.build(col())


def monitor_wall():
    steel = bpy.data.materials["M_FM_Steel_Dark"]
    galv = bpy.data.materials.get("M_WH_Galv", steel)
    dark = bpy.data.materials["M_CTRL_Dark"]
    glow = bpy.data.materials["M_CTRL_ScreenGlow"]
    dead = bpy.data.materials["M_CTRL_ScreenDead"]
    rubber = bpy.data.materials["M_FM_Rubber"]

    # Estantería robusta de dos niveles, anclada al muro oeste.
    for level, z in enumerate((2.35, 3.15)):
        mb = vest.MeshBuilder("CTRL_MonitorShelf_%d" % level)
        mb.add_box((-104.66, 47.5, z - 0.035), (0.52, 5.06, 0.07), galv)
        mb.add_box((-104.72, 47.5, z - 0.085), (0.06, 5.10, 0.06), steel)
        # Soportes diagonales anclados al muro, sin caras paralelas al estante.
        for y in (45.0, 46.2, 47.4, 48.6, 49.8):
            mb.add_box((-104.60, y, z - 0.19), (0.06, 0.05, 0.36), steel, rot=(0, math.radians(28), 0))
            mb.add_box((-104.86, y, z - 0.13), (0.04, 0.10, 0.22), steel)
        # Riel de cables separado 5 cm del estante.
        mb.add_box((-104.55, 47.5, z - 0.12), (0.08, 5.00, 0.035), dark)
        mb.build(col())

        for j, y in enumerate((46.3, 47.5, 48.7, 49.9)):
            mb = vest.MeshBuilder("CTRL_CRT_%d_%d" % (level, j))
            # Carcasa profunda con trasera escalonada.
            mb.add_box((-104.48, y, z + 0.25), (0.40, 0.46, 0.40), dark)
            mb.add_box((-104.69, y, z + 0.25), (0.16, 0.34, 0.30), dark)
            mb.add_box((-104.78, y, z + 0.25), (0.06, 0.24, 0.22), dark)
            # Marco frontal y pantalla hundida.
            mb.add_box((-104.265, y, z + 0.26), (0.035, 0.44, 0.36),
                       galv)
            mb.add_box((-104.245, y, z + 0.26), (0.010, 0.38, 0.30),
                       dark)
            mb.add_plane((-104.238, y, z + 0.26), 0.33, 0.25,
                         glow if (j + level) % 3 else dead,
                         rot=(0, math.radians(-90), 0),
                         uv_rect=(0, 0, 1, 1))
            # Rejillas de ventilación y pies.
            for k in range(5):
                mb.add_box((-104.73, y - 0.12 + k * 0.06, z + 0.36),
                           (0.10, 0.025, 0.035), steel)
            for sy in (-1, 1):
                mb.add_box((-104.44, y + sy * 0.13, z + 0.035),
                           (0.32, 0.05, 0.035), dark)
            # Cable de datos y alimentación cayendo al riel.
            for sy in (-0.12, 0.12):
                mb.add_cyl((-104.60, y + sy, z - 0.18), 0.012, 0.42,
                           rubber, axis="Z", segments=8)
            mb.build(col())

    # Un CRT volcado en el suelo, con pantalla rota.
    mb = vest.MeshBuilder("CTRL_CRT_Fallen")
    ang = math.radians(28)
    mb.add_box((-103.9, 44.4, 0.22), (0.38, 0.46, 0.40), dark, rot=(0, 0, ang))
    # Pantalla sobre la cara frontal real de la carcasa, sin solaparla.
    sx = -103.9 + math.cos(ang) * 0.196
    sy = 44.4 + math.sin(ang) * 0.196
    mb.add_plane((sx, sy, 0.24), 0.30, 0.24, dead,
                 rot=(0, math.radians(-90), ang),
                 uv_rect=(0, 0, 1, 1))
    mb.build(col())


def ceiling_and_lights():
    steel = bpy.data.materials["M_FM_Steel_Dark"]
    galv = bpy.data.materials["M_VEST_Galv"]
    dark = bpy.data.materials["M_CTRL_Dark"]
    cool = bpy.data.materials["M_VEST_Emissive_Cool"]
    red = bpy.data.materials["M_R21B_Emissive_Red"]
    # Bandejas y cableado
    mb = vest.MeshBuilder("CTRL_Ceiling_CABLE")
    for y in (46.0, 56.0):
        mb.add_box((-91.0, y, 5.50), (27.5, 0.38, 0.02), galv)
        for sx in (-1, 1):
            mb.add_box((-91.0, y + sx * 0.19, 5.56), (27.5, 0.02, 0.10), galv)
        for x in range(-104, -77, 2):
            mb.add_box((x, y, 5.52), (0.03, 0.36, 0.025), galv)
        for off in (-0.10, 0.0, 0.10):
            mb.add_cyl((-91.0, y + off, 5.47), 0.016, 27.0, dark, axis="X",
                       segments=8)
    for x in (-103.4, -78.6):
        mb.add_cyl((x, 50.0, 5.56), 0.05, 19.0, steel, axis="Y", segments=10)
    mb.build(col())
    # Climatización local: impulsión y retorno con AHU de techo.
    mb = vest.MeshBuilder("CTRL_HVAC_Duct_CABLE")
    mb.add_box((-91.0, 50.0, 5.08), (18.0, 0.62, 0.48), galv,
               bevel=0.003)
    mb.add_box((-91.0, 44.2, 5.08), (18.0, 0.62, 0.48), galv,
               bevel=0.003)
    mb.add_box((-85.0, 47.1, 5.08), (1.40, 1.30, 0.62), galv,
               bevel=0.004)
    mb.add_box((-85.0, 48.45, 5.08), (0.55, 1.55, 0.45), galv,
               bevel=0.002)
    mb.add_box((-85.0, 45.75, 5.08), (0.55, 1.55, 0.45), galv,
               bevel=0.002)
    for y in (50.0, 44.2):
        for x in (-100.0, -91.0, -82.0):
            mb.add_box((x, y, 4.82), (0.60, 0.46, 0.04), galv,
                       bevel=0.0)
            for i in range(4):
                mb.add_box((x - 0.21 + i * 0.14, y, 4.79),
                           (0.05, 0.38, 0.018), dark, bevel=0.0)
    for x in (-100.0, -94.0, -88.0, -82.0):
        mb.add_box((x, 50.0, 5.36), (0.05, 0.05, 0.28), steel,
                   bevel=0.0)
        mb.add_box((x, 44.2, 5.36), (0.05, 0.05, 0.28), steel,
                   bevel=0.0)
    mb.build(col())
    for i, (x, y) in enumerate(((-100, 45), (-100, 55), (-91, 45),
                                (-91, 55), (-82, 45), (-82, 55),
                                (-91, 50), (-94, 42.5))):
        mb = vest.MeshBuilder("CTRL_Light_%02d_LIGHT" % (i + 1))
        mb.add_box((x, y, 5.55), (1.25, 0.18, 0.07), steel, bevel=0.003)
        for sy in (-0.045, 0.045):
            mb.add_box((x, y + sy, 5.505), (1.12, 0.03, 0.03), cool)
        for sx in (-1, 1):
            mb.add_box((x + sx * 0.62, y, 5.55), (0.03, 0.19, 0.08), steel)
        for sx in (-1, 1):
            mb.add_box((x + sx * 0.42, y, 5.78), (0.015, 0.015, 0.42), steel)
        mb.build(col())
    # Balizas
    for i, (x, y, z, rz) in enumerate(((-94.0, 40.30, 3.20, 0.0),
                                       (-77.28, 44.0, 3.20, math.radians(90)))):
        mb = vest.MeshBuilder("CTRL_Beacon_%02d_LIGHT" % (i + 1))
        mb.add_box((x, y, z), (0.22, 0.12, 0.18), steel, rot=(0, 0, rz))
        mb.add_cyl((x, y + 0.06, z), 0.06, 0.10, red, axis="Y",
                   segments=12, rot=(0, 0, rz))
        mb.build(col())


def wall_details():
    desk = bpy.data.materials["M_CTRL_Desk"]
    yellow = bpy.data.materials["M_CTRL_Yellow"]
    dark = bpy.data.materials["M_CTRL_Dark"]
    paper = bpy.data.materials["M_VEST_Paper"]
    white = bpy.data.materials["M_CTRL_White"]
    steel = bpy.data.materials["M_FM_Steel_Dark"]
    # Zócalo técnico de 1,8 m en las paredes, con remate amarillo.
    mb = vest.MeshBuilder("CTRL_WallBands_TRIM")
    for x, sx in ((-104.82, 1), (-77.18, -1)):
        mb.add_box((x, 50.0, 0.9), (0.03, 19.4, 1.8), desk)
        mb.add_box((x + sx * 0.02, 50.0, 1.82), (0.04, 19.4, 0.04), yellow)
    for y, sy, segments in (
            (59.82, -1, ((-104.6, -94.6), (-93.4, -77.4))),
            (40.18, 1, ((-104.6, -96.6), (-91.4, -77.4)))):
        for x0, x1 in segments:
            cx = (x0 + x1) / 2
            ln = x1 - x0
            mb.add_box((cx, y, 0.9), (ln, 0.03, 1.8), desk)
            mb.add_box((cx, y + sy * 0.02, 1.82), (ln, 0.04, 0.04), yellow)
    mb.build(col())
    # Panel de evacuación en el muro norte.
    mb = vest.MeshBuilder("CTRL_NoticeBoard_SIGN")
    mb.add_box((-88.5, 59.80, 2.35), (1.30, 0.05, 0.90), dark)
    mb.add_plane((-88.5, 59.77, 2.35), 1.15, 0.75, paper,
                 rot=(math.radians(90), 0, 0), uv_rect=(0, 1, 1, 0))
    mb.build(col())
    text_sign("CTRL_NoticeText", "PLANO DE EVACUACIÓN", 0.055,
              (-88.5, 59.74, 2.68), (0, -1, 0), white, 0.001)
    # Reloj de pared junto al panel.
    mb = vest.MeshBuilder("CTRL_Clock")
    mb.add_cyl((-84.5, 59.80, 3.25), 0.24, 0.05, steel, axis="Y", segments=24)
    mb.add_cyl((-84.5, 59.77, 3.25), 0.20, 0.02, white, axis="Y", segments=24)
    mb.add_box((-84.5, 59.75, 3.25), (0.02, 0.01, 0.14), dark)
    mb.add_box((-84.5, 59.75, 3.25), (0.10, 0.01, 0.02), dark)
    mb.build(col())


def floor_details():
    yellow = bpy.data.materials["M_CTRL_Yellow"]
    dark = bpy.data.materials["M_CTRL_Dark"]
    rubber = bpy.data.materials["M_FM_Rubber"]
    mb = vest.MeshBuilder("CTRL_Floor_TRIM")
    # Líneas de carril y zona de filtro
    for x in (-96.2, -92.8):
        mb.add_box((x, 44.8, 0.006), (0.08, 6.0, 0.006), yellow)
    # Las líneas transversales quedan 6 mm por encima para no ser coplanarias.
    for y in (47.05, 47.95):
        mb.add_box((-92.5, y, 0.012), (9.0, 0.07, 0.006), yellow)
    for x in (-100.5, -86.5):
        mb.add_box((x, 47.5, 0.006), (0.12, 0.60, 0.006), yellow)
    mb.add_box((-94.0, 41.8, 0.009), (1.6, 1.6, 0.012), rubber)
    # Franja de peligro en el umbral sur
    for j in range(10):
        mb.add_box((-96.0 + j * 0.4 + 0.2, 40.35, 0.007),
                   (0.20, 0.22, 0.008), dark if j % 2 else yellow)
    mb.build(col())


def props():
    steel = bpy.data.materials["M_FM_Steel_Dark"]
    dark = bpy.data.materials["M_CTRL_Dark"]
    white = bpy.data.materials["M_CTRL_White"]
    paper = bpy.data.materials["M_VEST_Paper"]
    red = bpy.data.materials["M_VEST_Red"]
    yellow = bpy.data.materials["M_CTRL_Yellow"]
    # Teclados, monitores, teléfonos y tazas sobre los mostradores
    for i, x in enumerate((-102.4, -100.9, -88.6, -87.1)):
        y = 44.55
        mb = vest.MeshBuilder("CTRL_DeskProps_%02d" % (i + 1))
        mb.add_box((x, 43.72, 0.966), (0.42, 0.16, 0.03), dark)
        mb.add_box((x, 44.10, 1.08), (0.48, 0.10, 0.34), dark,
                   bevel=0.004)
        mb.add_box((x, 44.04, 1.08), (0.40, 0.015, 0.26),
                   bpy.data.materials["M_CTRL_ScreenGlow"])
        mb.build(col())
    # Silla caída y silla del puesto
    simple_chair("CTRL_Chair_West", -100.6, 43.0, 0.0, 0.0)
    simple_chair("CTRL_Chair_East", -88.4, 43.0, 0.0, 0.0)
    simple_chair("CTRL_Chair_Fallen", -86.0, 46.2, 0.0, 0.8, True)
    # Papeles y tazas sobre las encimeras (sin islas flotantes)
    mb = vest.MeshBuilder("CTRL_CounterPapers")
    for x, y, rz in ((-100.9, 43.75, 0.2), (-87.6, 43.75, -0.5)):
        mb.add_plane((x, y, 0.953), 0.22, 0.30, paper,
                     rot=(0, 0, rz))
    mb.build(col())
    mb = vest.MeshBuilder("CTRL_CounterCups")
    for x, y in ((-101.8, 43.80), (-88.2, 43.80)):
        mb.add_cyl((x, y, 1.00), 0.035, 0.10, white, axis="Z", segments=10)
    mb.build(col())
    # Llaves junto al lector, apoyadas en el suelo
    mb = vest.MeshBuilder("CTRL_Keys")
    for j in range(4):
        mb.add_cyl((-95.6 + j * 0.10, 45.8, 0.008), 0.006, 0.06, steel,
                   axis="X", segments=6)
    mb.build(col())
    # Cono y señal de suelo húmedo
    mb = vest.MeshBuilder("CTRL_FloorProps")
    mb.add_cyl((-80.0, 42.0, 0.32), 0.17, 0.64, yellow, axis="Z", segments=10)
    mb.add_box((-80.0, 42.0, 0.03), (0.42, 0.42, 0.04), dark)
    mb.add_box((-80.0, 42.0, 0.66), (0.14, 0.14, 0.04), yellow)
    for sx in (-1, 1):
        mb.add_box((-82.2 + sx * 0.18, 43.0, 0.35), (0.04, 0.36, 0.70),
                   yellow, rot=(0, 0, 0.15 * sx))
    mb.add_box((-82.2, 43.0, 0.36), (0.30, 0.04, 0.50), dark)
    mb.build(col())
    # Papelera junto al acceso oeste, fuera de la ruta central.
    mb = vest.MeshBuilder("CTRL_TrashBin")
    mb.add_cyl((-98.6, 41.3, 0.32), 0.22, 0.64, steel, axis="Z", segments=16)
    mb.add_cyl((-98.6, 41.3, 0.66), 0.23, 0.04, dark, axis="Z", segments=16)
    mb.add_cyl((-98.6, 41.3, 0.50), 0.225, 0.03, yellow, axis="Z",
               segments=16)
    mb.build(col())
    # Lámpara de mesa de la garita.
    mb = vest.MeshBuilder("CTRL_Booth_Lamp")
    lamp = bpy.data.materials["M_CTRL_LampWarm"]
    mb.add_cyl((-102.2, 56.9, 1.08), 0.09, 0.03, lamp, axis="Z", segments=12)
    mb.add_cyl((-102.2, 56.9, 1.25), 0.015, 0.34, steel, axis="Z", segments=8)
    mb.add_cyl((-102.2, 56.9, 1.43), 0.16, 0.10, lamp, axis="Z", segments=16)
    mb.build(col())


def security_equipment():
    steel = bpy.data.materials["M_FM_Steel_Dark"]
    dark = bpy.data.materials["M_CTRL_Dark"]
    green = bpy.data.materials["M_CTRL_LED_Green"]
    glow = bpy.data.materials["M_CTRL_ScreenGlow"]
    # Arco detector de metales en el carril central
    mb = vest.MeshBuilder("CTRL_MetalDetector")
    for sx in (-1, 1):
        mb.add_box((-94.5 + sx * 0.75, 46.2, 1.18),
                   (0.26, 0.34, 2.24), steel, bevel=0.006)
        mb.add_box((-94.5 + sx * 0.75, 46.00, 1.18),
                   (0.16, 0.02, 1.86), dark)
        mb.add_box((-94.5 + sx * 0.75, 45.95, 1.42),
                   (0.018, 0.018, 0.72), green)
        mb.add_box((-94.5 + sx * 0.75, 46.2, 0.03),
                   (0.40, 0.48, 0.06), dark)
    mb.add_box((-94.5, 46.2, 2.42), (1.76, 0.36, 0.24), steel, bevel=0.006)
    mb.add_box((-94.5, 46.02, 2.42), (1.08, 0.02, 0.10), dark)
    mb.add_box((-94.5, 46.005, 2.42), (0.92, 0.02, 0.045),
               bpy.data.materials["M_CTRL_LightPanel"])
    mb.build(col())
    # Equipo de rayos X y cinta transportadora
    mb = vest.MeshBuilder("CTRL_XRay")
    mb.add_box((-83.2, 46.6, 0.70), (1.80, 0.86, 1.40), steel, bevel=0.008)
    mb.add_box((-83.2, 46.14, 0.70), (1.72, 0.03, 1.30), dark)
    mb.add_box((-83.2, 46.12, 1.12), (1.10, 0.02, 0.30), glow)
    mb.add_box((-83.2, 46.6, 0.38), (2.10, 0.52, 0.10), dark)
    for j in range(9):
        mb.add_box((-84.05 + j * 0.21, 46.6, 0.44),
                   (0.16, 0.48, 0.02), steel)
    for sx in (-1, 1):
        mb.add_box((-83.2 + sx * 0.55, 46.12, 0.72),
                   (0.10, 0.02, 0.52), dark)
    mb.add_box((-83.2, 46.10, 1.36), (1.30, 0.04, 0.18), dark)
    mb.build(col())


def signage():
    dark = bpy.data.materials["M_CTRL_Dark"]
    steel = bpy.data.materials["M_FM_Steel_Dark"]
    green = bpy.data.materials["M_VEST_Emissive_Green"]
    # Rótulo principal sobre la puerta sur
    mb = vest.MeshBuilder("CTRL_Sign_Main")
    mb.add_box((-94.0, 40.19, 3.35), (3.2, 0.06, 0.66), dark)
    mb.add_box((-94.0, 40.225, 3.35), (3.05, 0.02, 0.56), dark)
    mb.build(col())
    text_sign("CTRL_Sign_ControlText", "CONTROL DE ACCESO", 0.22,
              (-94.0, 40.24, 3.35), (0, 1, 0), green, 0.004)
    # Seguridad sobre el mostrador oeste
    mb = vest.MeshBuilder("CTRL_Sign_Security")
    mb.add_box((-101.0, 40.19, 2.55), (2.4, 0.05, 0.55), dark)
    mb.add_plane((-101.0, 40.22, 2.55), 2.25, 0.48,
                 bpy.data.materials["M_HERO_Sign_Seguridad"],
                 rot=(math.radians(-90), 0, 0), uv_rect=(1, 1, 0, 0))
    mb.build(col())
    # NEXUS sobre el muro oeste
    text_sign("CTRL_Sign_Nexus", "NEXUS", 0.38, (-77.22, 51.6, 3.80),
              (-1, 0, 0), green, 0.004)
    # Salida de emergencia este
    text_sign("CTRL_Sign_Exit", "SALIDA", 0.16, (-77.20, 44.0, 2.75),
              (-1, 0, 0), bpy.data.materials["M_VEST_Emissive_Green"], 0.004)
    # Rótulo colgado sobre el filtro central.
    mb = vest.MeshBuilder("CTRL_Sign_Hanging")
    mb.add_box((-94.5, 45.8, 3.75), (2.40, 0.08, 0.50), dark)
    for x in (-95.5, -93.5):
        mb.add_box((x, 45.8, 4.95), (0.03, 0.03, 1.90), steel)
    mb.add_box((-94.5, 45.84, 3.75), (2.25, 0.02, 0.40), dark)
    mb.build(col())
    text_sign("CTRL_Sign_HangingText", "FILTRO NORTE", 0.16,
              (-94.5, 45.74, 3.75), (0, -1, 0), green, 0.003)
    # Etiquetas de alta tensión y extintor
    mb = vest.MeshBuilder("CTRL_Labels_SIGN")
    mb.add_plane((-104.82, 47.5, 2.75), 0.55, 0.14,
                 bpy.data.materials["M_FM_Label_AltaTension_2"],
                 rot=(0, math.radians(-90), 0), uv_rect=(1, 1, 0, 0))
    mb.add_plane((-81.2, 59.80, 2.35), 0.55, 0.14,
                 bpy.data.materials["M_FM_Label_Extintor"],
                 rot=(math.radians(90), 0, 0), uv_rect=(0, 1, 1, 0))
    mb.build(col())


def ceiling_grid():
    """Cielo raso registrable 600x1200 con perfilería y tejas dañadas."""
    panel = bpy.data.materials["M_CTRL_CeilingPanel"]
    stain = bpy.data.materials["M_CTRL_CeilingStain"]
    grid = bpy.data.materials["M_CTRL_CeilingGrid"]
    mb = vest.MeshBuilder("CTRL_CeilingGrid")
    z = 5.86
    x0, x1 = X0 + 0.12, X1 - 0.12
    y0, y1 = Y0 + 0.12, Y1 - 0.12
    # Tejas de 1.20 x 0.60; algunas ausentes o manchadas.
    nx = int((x1 - x0) / 1.20)
    ny = int((y1 - y0) / 0.60)
    for ix in range(nx):
        for iy in range(ny):
            if (ix * 7 + iy * 11) % 53 == 0:
                continue  # teja hundida/ausente
            cx = x0 + 0.60 + ix * 1.20
            cy = y0 + 0.30 + iy * 0.60
            mat_teja = stain if (ix * 5 + iy * 3) % 29 == 0 else panel
            mb.add_box((cx, cy, z), (1.14, 0.54, 0.018), mat_teja,
                       bevel=0.002)
    # Perfilería principal y travesaños.
    for ix in range(nx + 1):
        cx = x0 + ix * 1.20
        mb.add_box((cx, (y0 + y1) * 0.5, z - 0.012),
                   (0.045, y1 - y0, 0.040), grid, bevel=0.002)
    for iy in range(ny + 1):
        cy = y0 + iy * 0.60
        mb.add_box(((x0 + x1) * 0.5, cy, z - 0.012),
                   (x1 - x0, 0.032, 0.034), grid, bevel=0.002)
    # Varillas de suspensión cada 2,4 m.
    for ix in range(0, nx + 1, 2):
        for iy in range(0, ny + 1, 4):
            cx = x0 + ix * 1.20
            cy = y0 + iy * 0.60
            mb.add_cyl((cx, cy, z + 0.07), 0.006, 0.14, grid,
                       axis="Z", segments=6)
    mb.build(col())


def wall_cladding():
    """Zócalo metálico corrugado de 1,3 m en los cuatro muros, con huecos."""
    panel = bpy.data.materials["M_FM_Metal_Panel"]
    rib = bpy.data.materials["M_FM_Painted_Green"]
    rail = bpy.data.materials["M_FM_Steel_Dark"]
    mb = vest.MeshBuilder("CTRL_WallCladding")

    def run(axis, fixed, a0, a1, inward):
        if a1 - a0 < 0.20:
            return
        # Dejar 2 cm en cada extremo para que los paneles no compartan
        # planos con el zócalo perpendicular en las esquinas.
        aa0, aa1 = a0 + 0.02, a1 - 0.02
        c = ((aa0 + aa1) * 0.5, fixed, 0.72) if axis == "x" else (fixed, (aa0 + aa1) * 0.5, 0.72)
        size = (aa1 - aa0, 0.028, 1.30) if axis == "x" else (0.028, aa1 - aa0, 1.30)
        mb.add_box(c, size, panel)
        # Costillas verticales cada 0,30 m, hacia el interior.
        n = max(1, int((a1 - a0) / 0.30))
        for i in range(n + 1):
            p = aa0 + 0.04 + (aa1 - aa0 - 0.08) * i / n
            if axis == "x":
                mb.add_box((p, fixed + inward * 0.040, 0.72),
                           (0.034, 0.030, 1.28), rib)
            else:
                mb.add_box((fixed + inward * 0.040, p, 0.72),
                           (0.030, 0.034, 1.28), rib)
        # Remate superior e inferior.
        rc = ((a0 + a1) * 0.5, fixed + inward * 0.050, 1.415) if axis == "x" else (fixed + inward * 0.050, (a0 + a1) * 0.5, 1.415)
        rs = (a1 - a0 - 0.12, 0.050, 0.060) if axis == "x" else (0.060, a1 - a0 - 0.12, 0.060)
        mb.add_box(rc, rs, rail)
        kc = ((a0 + a1) * 0.5, fixed + inward * 0.050, 0.030) if axis == "x" else (fixed + inward * 0.050, (a0 + a1) * 0.5, 0.030)
        ks = (a1 - a0 - 0.12, 0.040, 0.120) if axis == "x" else (0.040, a1 - a0 - 0.12, 0.120)
        mb.add_box(kc, ks, rail)

    # Sur con vano de puerta x -96..-92; norte con hueco -94.5..-93.5.
    run("x", Y0 + 0.035, X0 + 0.06, -96.0, 1)
    run("x", Y0 + 0.035, -92.0, X1 - 0.06, 1)
    run("x", Y1 - 0.035, X0 + 0.06, -94.5, -1)
    run("x", Y1 - 0.035, -93.5, X1 - 0.06, -1)
    # Oeste completa; este con puerta y 42..46.
    run("y", X0 + 0.035, Y0 + 0.06, Y1 - 0.06, 1)
    run("y", X1 - 0.035, Y0 + 0.06, 42.0, -1)
    run("y", X1 - 0.035, 46.0, Y1 - 0.06, -1)
    mb.build(col())





def floor_surface():
    """Suelo texturizado y desgastado sobre la losa del blockout."""
    concrete = bpy.data.materials["M_FM_Concrete_Floor"]
    stain = bpy.data.materials["M_CTRL_WallStain"]
    mb = vest.MeshBuilder("CTRL_FloorOverlay_DECAL")
    mb.add_plane((-91.0, 50.0, 0.003), 27.4, 19.4, concrete,
                 uv_rect=(0, 0, 13.7, 9.7))
    mb.build(col())
    # Manchas y zonas húmedas, ligeramente por encima del suelo.
    mb = vest.MeshBuilder("CTRL_FloorStains_DECAL")
    for x, y, sx, sy, rz in ((-99.0, 42.1, 1.4, 0.5, 0.2),
                             (-88.0, 45.6, 1.0, 0.35, -0.4),
                             (-95.8, 49.8, 1.8, 0.42, 0.1),
                             (-82.0, 52.4, 0.9, 0.30, 0.7),
                             (-101.2, 57.0, 0.7, 0.25, -0.2),
                             (-91.0, 55.5, 1.2, 0.28, 0.3)):
        mb.add_plane((x, y, 0.008), sx, sy, stain,
                     rot=(0, 0, rz), uv_rect=(0, 0, 1, 1))
    mb.build(col())


def wall_dressing():
    """Paneles de hormigón, juntas, conduits, rejillas y manchas de pared."""
    wall = bpy.data.materials["M_FM_Concrete_Wall"]
    steel = bpy.data.materials["M_FM_Steel_Dark"]
    dark = bpy.data.materials["M_CTRL_Dark"]
    stain = bpy.data.materials["M_CTRL_WallStain"]
    galv = bpy.data.materials.get("M_WH_Galv") or steel
    mb = vest.MeshBuilder("CTRL_WallPanels_DECAL")
    # Sur, con hueco de puerta x -96..-92.
    for x0, x1 in ((X0 + 0.10, -96.05), (-91.95, X1 - 0.10)):
        mb.add_plane(((x0 + x1) * 0.5, Y0 + 0.022, 3.80),
                     x1 - x0, 3.90, wall, rot=(math.radians(-90), 0, 0),
                     uv_rect=(0, 0, (x1 - x0) / 2.6, 1.5))
    # Norte, con hueco de ventanilla x -94.5..-93.5.
    for x0, x1 in ((X0 + 0.10, -94.55), (-93.45, X1 - 0.10)):
        mb.add_plane(((x0 + x1) * 0.5, Y1 - 0.022, 3.80),
                     x1 - x0, 3.90, wall, rot=(math.radians(90), 0, 0),
                     uv_rect=(0, 0, (x1 - x0) / 2.6, 1.5))
    # Oeste completa.
    mb.add_plane((X0 + 0.022, 50.0, 3.80), 3.90, 19.4, wall,
                 rot=(0, math.radians(90), 0), uv_rect=(0, 0, 1.5, 7.4))
    # Este, con hueco de puerta y42..46.
    for y0, y1 in ((Y0 + 0.10, 42.05), (45.95, Y1 - 0.10)):
        mb.add_plane((X1 - 0.022, (y0 + y1) * 0.5, 3.80),
                     3.90, y1 - y0, wall, rot=(0, math.radians(-90), 0),
                     uv_rect=(0, 0, 1.5, (y1 - y0) / 2.6))
    mb.build(col())

    mb = vest.MeshBuilder("CTRL_WallSeams_TRIM")
    for x in (-102.4, -99.4, -86.4, -83.4):
        mb.add_box((x, Y0 + 0.030, 3.80), (0.045, 0.018, 3.86), dark)
    for x in (-102.4, -99.4, -86.4, -83.4):
        mb.add_box((x, Y1 - 0.030, 3.80), (0.045, 0.018, 3.86), dark)
    for y in (43.6, 46.4, 49.2, 52.0, 54.8, 57.6):
        mb.add_box((X0 + 0.030, y, 3.80), (0.018, 0.045, 3.86), dark)
        mb.add_box((X1 - 0.030, y, 3.80), (0.018, 0.045, 3.86), dark)
    mb.build(col())

    # Conduits y cajas de derivación en el muro norte.
    mb = vest.MeshBuilder("CTRL_WallConduits_CABLE")
    for z, y in ((4.55, Y1 - 0.070), (4.20, Y1 - 0.095)):
        mb.add_cyl((X0 + 13.0, y, z), 0.028, 20.0, dark, axis="X", segments=10)
        for x in (-102.0, -96.0, -90.0, -84.0, -79.0):
            mb.add_box((x, y + 0.020, z), (0.05, 0.05, 0.10), galv, bevel=0.004)
    for x in (-100.0, -88.0):
        mb.add_box((x, Y1 - 0.080, 3.10), (0.42, 0.10, 0.52), dark, bevel=0.006)
        mb.add_box((x, Y1 - 0.135, 3.10), (0.32, 0.012, 0.40), galv)
    mb.build(col())

    # Rejillas de ventilación y manchas.
    mb = vest.MeshBuilder("CTRL_WallVents_GRILLE")
    for x, z in ((-101.6, 3.25), (-84.0, 3.25)):
        mb.add_box((x, Y0 + 0.040, z), (0.62, 0.035, 0.40), dark, bevel=0.004)
        for k in range(6):
            mb.add_box((x, Y0 + 0.062, z - 0.15 + k * 0.06),
                       (0.54, 0.012, 0.022), galv)
    mb.build(col())

    mb = vest.MeshBuilder("CTRL_WallStains_DECAL")
    for x, z, sx, sz in ((-98.2, 2.15, 0.55, 1.10), (-89.4, 2.35, 0.35, 0.75),
                         (-83.0, 2.05, 0.45, 0.85), (-101.8, 2.55, 0.30, 0.60)):
        mb.add_plane((x, Y0 + 0.040, z), sx, sz, stain,
                     rot=(math.radians(-90), 0, 0), uv_rect=(0, 0, 1, 1))
    mb.build(col())


def queue_barriers():
    """Barandillas de cola junto a los mostradores, sin colisión."""
    steel = bpy.data.materials["M_FM_Steel_Dark"]
    dark = bpy.data.materials["M_CTRL_Dark"]
    rubber = bpy.data.materials["M_FM_Rubber"]
    mb = vest.MeshBuilder("CTRL_QueueBarriers_TRIM")
    for side_x in (-103.35, -78.55):
        for y in (42.3, 44.1, 45.9):
            mb.add_cyl((side_x, y, 0.035), 0.055, 0.07, rubber,
                       axis="Z", segments=14)
            mb.add_cyl((side_x, y, 0.51), 0.024, 0.94, steel,
                       axis="Z", segments=12)
            mb.add_box((side_x, y, 0.90), (0.09, 0.09, 0.13), dark,
                       bevel=0.006)
            mb.add_box((side_x, y, 0.985), (0.06, 0.06, 0.03), steel,
                       bevel=0.003)
        for y0, y1 in ((42.3, 44.1), (44.1, 45.9)):
            mb.add_box((side_x, (y0 + y1) * 0.5, 0.86),
                       (0.026, y1 - y0 - 0.10, 0.055), dark, bevel=0.002)
    mb.build(col())


def abandonment_clutter():
    """Papeles, carpetas, cinta, cables y residuos del complejo abandonado."""
    paper = bpy.data.materials["M_VEST_Paper"]
    dark = bpy.data.materials["M_CTRL_Dark"]
    rubber = bpy.data.materials["M_FM_Rubber"]
    red = bpy.data.materials["M_VEST_Red"]
    steel = bpy.data.materials["M_FM_Steel_Dark"]
    mb = vest.MeshBuilder("CTRL_Clutter_DECAL")
    for x, y, rz, sx, sy in ((-98.8, 42.2, 0.4, 0.22, 0.30),
                             (-97.6, 42.8, -0.3, 0.20, 0.28),
                             (-90.2, 45.1, 0.8, 0.22, 0.30),
                             (-89.1, 44.3, -0.5, 0.20, 0.27),
                             (-95.4, 50.2, 0.2, 0.24, 0.32),
                             (-82.0, 51.7, -0.7, 0.21, 0.29),
                             (-101.9, 56.0, 0.5, 0.20, 0.28),
                             (-84.0, 57.5, 0.1, 0.22, 0.30)):
        mb.add_plane((x, y, 0.012), sx, sy, paper, rot=(0, 0, rz))
    for x, y, rz in ((-97.2, 43.5, 0.3), (-88.6, 46.0, -0.6),
                     (-94.2, 51.0, 0.5)):
        mb.add_box((x, y, 0.018), (0.26, 0.34, 0.020), dark,
                   bevel=0.002, rot=(0, 0, rz))
    # Cinta de precaución caída.
    mb.add_box((-94.0, 43.7, 0.012), (3.6, 0.06, 0.010), red,
               bevel=0.002, rot=(0, 0, 0.05))
    mb.build(col())

    # Rollo de cable y pequeño amasijo junto a racks.
    mb = vest.MeshBuilder("CTRL_ClutterCable_CABLE")
    mb.add_cyl((-80.4, 54.6, 0.035), 0.26, 0.035, rubber,
               axis="Z", segments=20)
    mb.add_cyl((-80.4, 54.6, 0.060), 0.20, 0.035, dark,
               axis="Z", segments=18)
    mb.add_cyl((-80.2, 54.9, 0.080), 0.018, 1.30, rubber,
               axis="Y", segments=8)
    mb.build(col())

    mb = vest.MeshBuilder("CTRL_ClutterDebris_DECAL")
    for x, y, sx in ((-92.0, 42.4, 0.18), (-96.2, 54.0, 0.14),
                     (-83.8, 49.0, 0.16), (-101.0, 51.0, 0.12)):
        mb.add_box((x, y, 0.012), (sx, sx * 0.7, 0.012), steel,
                   bevel=0.002, rot=(0, 0, x * 0.1))
    mb.build(col())


def light_panels():
    """Paneles de luz difusa bajo el techo registrable."""
    panel = bpy.data.materials["M_CTRL_LightPanel"]
    frame = bpy.data.materials["M_CTRL_Dark"]
    mb = vest.MeshBuilder("CTRL_LightPanels_LIGHT")
    for x in (-100.0, -94.0, -88.0):
        for y in (44.0, 50.0, 56.0):
            mb.add_box((x, y, 5.805), (1.24, 0.64, 0.030), frame,
                       bevel=0.004)
            mb.add_plane((x, y, 5.787), 1.14, 0.54, panel,
                         rot=(math.pi, 0, 0), uv_rect=(0, 0, 1, 1))
    mb.build(col())


def build():
    clean()
    materials()
    counter("CTRL_Counter_West", -100.5, 43.9, 5.6)
    counter("CTRL_Counter_East", -88.5, 43.9, 5.6)
    turnstile_row()
    guard_booth()
    server_racks()
    key_cabinet()
    monitor_wall()
    ceiling_grid()
    ceiling_and_lights()
    wall_details()
    wall_cladding()
    wall_dressing()
    floor_surface()
    floor_details()
    light_panels()
    queue_barriers()
    props()
    abandonment_clutter()
    security_equipment()
    signage()
    # Cámaras de seguridad en las esquinas
    for i, (x, y, rz) in enumerate(((-104.4, 40.6, math.radians(-45)),
                                    (-77.6, 40.6, math.radians(45)),
                                    (-104.4, 59.4, math.radians(-135)),
                                    (-77.6, 59.4, math.radians(135)))):
        camera("CTRL_Camera_%02d" % (i + 1), x, y, 3.65, rz)
    # Extintor físico junto al acceso este
    mb = vest.MeshBuilder("CTRL_Extinguisher")
    mb.add_cyl((-80.6, 40.35, 0.62), 0.075, 0.58,
               bpy.data.materials["M_VEST_Red"], axis="Z", segments=14)
    mb.add_cyl((-80.6, 40.35, 0.95), 0.032, 0.10,
               bpy.data.materials["M_FM_Steel_Dark"], axis="Z", segments=10)
    mb.add_box((-80.6, 40.35, 1.02), (0.16, 0.05, 0.035),
               bpy.data.materials["M_CTRL_Dark"])
    mb.build(col())
    c = col()
    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons)
               for o in c.objects if o.type == "MESH")
    verts = sum(len(o.data.vertices) for o in c.objects if o.type == "MESH")
    print("CTRL_BUILD objects=%d verts=%d tris=%d" % (len(c.objects), verts, tris))
    for o in sorted(c.objects, key=lambda x: x.name):
        print("CTRL_OBJ", o.name,
              sum(len(p.vertices) - 2 for p in o.data.polygons) if o.type == "MESH" else 0)


if __name__ == "__main__":
    build()
