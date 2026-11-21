"""Viste Almacén / Suministros (Z06) en el master V06.

Idempotente: reconstruye L1_ART_WAREHOUSE. No guarda el .blend, no toca otras
colecciones y no añade luces ni cámaras. Reutiliza MeshBuilder/materiales de
Vestuarios y props ya detallados del proyecto.

Uso desde Blender MCP:
    exec(compile(open("scripts/fm/fm_warehouse_build.py").read(),
                 "fm_warehouse_build.py", "exec"))
"""

import bpy
import math
import os
import importlib.util

from mathutils import Vector, Matrix

PROJECT = "/home/riyo/Documentos/game"
COL_NAME = "L1_ART_WAREHOUSE"
VEST_PATH = os.path.join(PROJECT, "scripts", "fm", "fm_vestuarios_build.py")

_spec = importlib.util.spec_from_file_location("vest", VEST_PATH)
vest = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vest)
vest.ensure_materials()

# Caras interiores de la sala (Blender).
X0, X1 = 70.15, 109.85
Y0, Y1 = 8.15, 37.85
ZTOP = 5.89


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


def get_mat(name, fallback="M_FM_Steel_Dark"):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.get(fallback)
    if m is None:
        m = mat("M_WH_Fallback", (0.18, 0.19, 0.18), 0.6)
    return m


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
    ob.hide_viewport = False
    ob.hide_set(False)
    # Some library props bake their world position into the mesh data, while
    # others keep it in the object transform.  Normalise against the local
    # bounding box so every copy lands with its bottom centre at (x, y, z).
    xs = [c[0] for c in src.bound_box]
    ys = [c[1] for c in src.bound_box]
    zs = [c[2] for c in src.bound_box]
    base = Vector(((min(xs) + max(xs)) * 0.5,
                   (min(ys) + max(ys)) * 0.5,
                   min(zs)))
    ob.matrix_world = (Matrix.Translation((x, y, z))
                       @ Matrix.Rotation(rz, 4, "Z")
                       @ Matrix.Rotation(rx, 4, "X")
                       @ Matrix.Translation(-base))
    return ob


class Frame:
    """Coloca piezas locales (lx, ly) en una sala con rotación Z."""

    def __init__(self, cx, cy, rz=0.0):
        self.cx, self.cy, self.rz = cx, cy, rz
        self.c = math.cos(rz)
        self.s = math.sin(rz)

    def p(self, lx, ly):
        return (self.cx + lx * self.c - ly * self.s,
                self.cy + lx * self.s + ly * self.c)

    def box(self, mb, lx, ly, z, sx, sy, sz, material, bevel=0.0,
            segments=1, rot=(0.0, 0.0, 0.0), uv_scale=1.0):
        x, y = self.p(lx, ly)
        r = (rot[0], rot[1], rot[2] + self.rz)
        return mb.add_box((x, y, z), (sx, sy, sz), material,
                          bevel=bevel, segments=segments, rot=r,
                          uv_scale=uv_scale)

    def cyl(self, mb, lx, ly, z, radius, depth, material, axis="Z",
            segments=16, rot=(0.0, 0.0, 0.0), bevel=0.0, uv_scale=1.0):
        x, y = self.p(lx, ly)
        r = (rot[0], rot[1], rot[2] + self.rz)
        return mb.add_cyl((x, y, z), radius, depth, material, axis=axis,
                          segments=segments, rot=r, bevel=bevel,
                          uv_scale=uv_scale)


def world_box(mb, center, size, material, bevel=0.0, segments=1,
              rot=(0.0, 0.0, 0.0), uv_scale=1.0):
    return mb.add_box(center, size, material, bevel=bevel,
                      segments=segments, rot=rot, uv_scale=uv_scale)


def tray_segment(mb, material, x0, y0, x1, y1, z, width=0.50):
    """Tramo recto de bandeja de cables. Los extremos son la línea central."""
    if abs(x1 - x0) >= abs(y1 - y0):
        length = x1 - x0
        if abs(length) < 0.08:
            return
        cx, cy = (x0 + x1) * 0.5, (y0 + y1) * 0.5
        mb.add_box((cx, cy, z), (length, width, 0.05), material, bevel=0.0)
        for sy in (-1, 1):
            mb.add_box((cx, cy + sy * (width * 0.5 - 0.01), z + 0.07),
                       (length - 0.04, 0.04, 0.14), material, bevel=0.0)
        step = 1.0
        x = x0 + 0.5
        while x < x1 - 0.3:
            mb.add_box((x, cy, z + 0.045), (0.04, width - 0.04, 0.05),
                       material, bevel=0.0)
            x += step
    else:
        length = y1 - y0
        if abs(length) < 0.08:
            return
        cx, cy = (x0 + x1) * 0.5, (y0 + y1) * 0.5
        mb.add_box((cx, cy, z), (width, length, 0.05), material, bevel=0.0)
        for sx in (-1, 1):
            mb.add_box((cx + sx * (width * 0.5 - 0.01), cy, z + 0.07),
                       (0.04, length - 0.04, 0.14), material, bevel=0.0)
        step = 1.0
        y = y0 + 0.5
        while y < y1 - 0.3:
            mb.add_box((cx, y, z + 0.045), (width - 0.04, 0.04, 0.05),
                       material, bevel=0.0)
            y += step


def tray_hanger(mb, material, x, y, z, ceiling):
    bottom = z + 0.05
    height = ceiling - bottom
    if height <= 0.05:
        return
    mb.add_box((x, y, bottom + height * 0.5), (0.03, 0.03, height),
               material, bevel=0.0)


def tray_sleeve(mb, material, wall_x, y, z):
    """Marco de pasamuros. Se coloca en la cara interior del muro."""
    sx = wall_x + 0.08
    for dz in (-0.25, 0.25):
        mb.add_box((sx, y, z + dz), (0.16, 0.90, 0.05), material,
                   bevel=0.0)
    for dy in (-0.40, 0.40):
        mb.add_box((sx, y + dy, z), (0.12, 0.05, 0.45), material,
                   bevel=0.0)


# ---------------------------------------------------------------------------
# Materiales
# ---------------------------------------------------------------------------


def materials():
    mat("M_WH_RackBlue", (0.020, 0.050, 0.105), 0.44, 0.05)
    mat("M_WH_RackOrange", (0.60, 0.20, 0.012), 0.46, 0.0)
    mat("M_WH_RackDeck", (0.13, 0.135, 0.13), 0.56, 0.35)
    mat("M_WH_Yellow", (0.62, 0.42, 0.018), 0.52, 0.0)
    mat("M_WH_WhiteLine", (0.60, 0.61, 0.56), 0.72, 0.0)
    mat("M_WH_BlackRubber", (0.006, 0.007, 0.007), 0.92, 0.0)
    mat("M_WH_DarkMetal", (0.022, 0.025, 0.027), 0.42, 0.72)
    mat("M_WH_Galv", (0.32, 0.34, 0.34), 0.38, 0.82)
    mat("M_WH_Label", (0.62, 0.62, 0.54), 0.86, 0.0)
    mat("M_WH_LabelDark", (0.008, 0.010, 0.009), 0.68, 0.0)
    mat("M_WH_ToteBlue", (0.015, 0.070, 0.145), 0.52, 0.0)
    mat("M_WH_ToteGray", (0.115, 0.125, 0.115), 0.58, 0.0)
    mat("M_WH_Tarp", (0.018, 0.022, 0.020), 0.95, 0.0)
    mat("M_WH_Oil", (0.004, 0.005, 0.004), 0.075, 0.0)
    mat("M_WH_Blood", (0.070, 0.004, 0.003), 0.34, 0.0)
    mat("M_WH_EmissiveRed", (0.42, 0.008, 0.004), 0.34, 0.0,
        emission=(1.0, 0.025, 0.012), strength=4.0)
    mat("M_WH_EmissiveAmber", (0.48, 0.22, 0.008), 0.34, 0.0,
        emission=(1.0, 0.50, 0.04), strength=3.0)
    mat("M_WH_ScreenGlow", (0.01, 0.10, 0.10), 0.28, 0.0,
        emission=(0.08, 0.62, 0.60), strength=2.2)
    film = mat("M_WH_Film", (0.52, 0.60, 0.58), 0.20, 0.0)
    bsdf = next(n for n in film.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Alpha"].default_value = 0.16
    film.surface_render_method = "BLENDED"
    mat("M_WH_Forklift", (0.66, 0.44, 0.018), 0.42, 0.0)
    mat("M_WH_Seat", (0.025, 0.030, 0.028), 0.78, 0.0)


# ---------------------------------------------------------------------------
# Estanterías y carga
# ---------------------------------------------------------------------------


def pallet(mb, f, lx, ly, z):
    wood = get_mat("M_FM_Wood_Detailed", "M_VEST_Cork")
    dark = get_mat("M_FM_Steel_Dark")
    for sx in (-0.48, 0.0, 0.48):
        f.box(mb, lx + sx, ly, z + 0.040, 0.080, 0.95, 0.080, wood,
              bevel=0.004)
    for dy in (-0.38, -0.19, 0.0, 0.19, 0.38):
        f.box(mb, lx, ly + dy, z + 0.108, 1.14, 0.125, 0.030, wood,
              bevel=0.004)
    for sx in (-0.48, 0.0, 0.48):
        for dy in (-0.38, 0.38):
            # Tacos embutidos en los largueros: sin caras coplanares.
            f.box(mb, lx + sx, ly + dy, z + 0.015, 0.060, 0.060, 0.024,
                  dark, bevel=0.002)


def cargo_box(mb, f, lx, ly, z, sx, sy, sz, material=None):
    material = material or get_mat("M_FM_Cardboard")
    label = get_mat("M_WH_Label")
    tape = get_mat("M_WH_LabelDark")
    f.box(mb, lx, ly, z + sz * 0.5, sx, sy, sz, material,
          bevel=0.0)
    # Cinta de embalaje y etiqueta, separadas de la cara al menos 3 mm.
    f.box(mb, lx, ly, z + sz + 0.004, 0.045, sy * 0.92, 0.003, tape,
          bevel=0.0)
    f.box(mb, lx, ly - sy * 0.5 - 0.005, z + sz * 0.58,
          sx * 0.42, 0.004, sz * 0.22, label, bevel=0.0)


def tote(mb, f, lx, ly, z, sx=0.50, sy=0.40, sz=0.30, material=None):
    material = material or get_mat("M_WH_ToteBlue")
    label = get_mat("M_WH_Label")
    t = 0.025
    # Fondo embutido en las paredes y levantado 4 mm: sus caras no son
    # coplanares con las tapas inferiores de las paredes.
    f.box(mb, lx, ly, z + 0.015, sx - 0.035, sy - 0.035, 0.022, material)
    f.box(mb, lx, ly - sy * 0.5 + t * 0.5, z + sz * 0.5, sx, t, sz, material)
    f.box(mb, lx, ly + sy * 0.5 - t * 0.5, z + sz * 0.5, sx, t, sz, material)
    f.box(mb, lx - sx * 0.5 + t * 0.5, ly, z + sz * 0.5, t, sy, sz, material)
    f.box(mb, lx + sx * 0.5 - t * 0.5, ly, z + sz * 0.5, t, sy, sz, material)
    # Asas y etiqueta. Las asas laterales se omiten: en totes adyacentes
    # se solapaban entre sí y con las paredes.
    f.box(mb, lx, ly - sy * 0.5 - 0.006, z + sz * 0.55,
          sx * 0.42, 0.003, sz * 0.24, label, bevel=0.0)


def film_wrap(mb, f, lx, ly, z, sx, sy, sz):
    film = get_mat("M_WH_Film")
    for dy in (-sy * 0.5 - 0.006, sy * 0.5 + 0.006):
        f.box(mb, lx, ly + dy, z, sx + 0.02, 0.003, sz, film, bevel=0.0)
    for dx in (-sx * 0.5 - 0.006, sx * 0.5 + 0.006):
        f.box(mb, lx + dx, ly, z, 0.003, sy + 0.02, sz, film, bevel=0.0)
    f.box(mb, lx, ly, z + sz * 0.5 + 0.012, sx + 0.02, sy + 0.02, 0.003,
          film, bevel=0.0)


def rack_load(mb, f, lx, ly, z, kind=0):
    pallet(mb, f, lx, ly, z)
    base = z + 0.140
    if kind == 0:
        cargo_box(mb, f, lx - 0.255, ly, base, 0.480, 0.430, 0.380)
        cargo_box(mb, f, lx + 0.255, ly, base, 0.480, 0.430, 0.380)
        cargo_box(mb, f, lx, ly, base + 0.392, 0.500, 0.420, 0.345)
        film_wrap(mb, f, lx, ly, base + 0.36, 1.02, 0.94, 0.76)
    elif kind == 1:
        tote(mb, f, lx - 0.255, ly, base, 0.500, 0.420, 0.300,
             get_mat("M_WH_ToteBlue"))
        tote(mb, f, lx + 0.255, ly, base, 0.500, 0.420, 0.300,
             get_mat("M_WH_ToteGray"))
        tote(mb, f, lx, ly, base + 0.306, 0.500, 0.420, 0.300,
             get_mat("M_WH_ToteBlue"))
    else:
        cargo_box(mb, f, lx - 0.255, ly, base, 0.480, 0.430, 0.420)
        cargo_box(mb, f, lx - 0.255, ly, base + 0.432, 0.460, 0.410, 0.300)
        cargo_box(mb, f, lx + 0.255, ly, base, 0.480, 0.430, 0.420)


def rack_bay(name, cx, cy, rz=0.0, width=2.70, depth=1.10, height=3.60):
    f = Frame(cx, cy, rz)
    mb = vest.MeshBuilder(name)
    blue = get_mat("M_WH_RackBlue")
    orange = get_mat("M_WH_RackOrange")
    deck = get_mat("M_WH_RackDeck")
    dark = get_mat("M_WH_DarkMetal")
    levels = (0.18, 1.28, 2.38, 3.48)

    for sx in (-1, 1):
        for sy in (-1, 1):
            lx = sx * (width * 0.5 - 0.075)
            ly = sy * (depth * 0.5 - 0.075)
            # Montante embutido 3 mm en la placa; placa separada del suelo
            # y pie de nivelación embutido en la placa (sin caras coplanares).
            f.box(mb, lx, ly, 0.035 + (height - 0.035) * 0.5,
                  0.090, 0.070, height - 0.035, blue,
                  bevel=0.0)
            f.box(mb, lx, ly, 0.021, 0.240, 0.240, 0.034, deck,
                  bevel=0.004)
            # Sin pie cilíndrico: su tapa coincidía con la base del montante.
            for z in levels:
                f.box(mb, lx, ly, z, 0.155, 0.125, 0.145, blue,
                      bevel=0.005)

    for z in levels:
        for sy in (-1, 1):
            f.box(mb, 0, sy * (depth * 0.5 - 0.075), z,
                  width - 0.08, 0.080, 0.120, orange, bevel=0.006)
            f.box(mb, 0, sy * (depth * 0.5 - 0.075), z - 0.070,
                  width - 0.18, 0.055, 0.035, orange, bevel=0.003)
            for sx in (-1, 1):
                f.box(mb, sx * (width * 0.5 - 0.075),
                      sy * (depth * 0.5 - 0.075), z - 0.080,
                      0.180, 0.100, 0.050, orange, bevel=0.003)
                # Pasadores omitidos: sus casquillos biselados generaban
                # anillos coplanares con las caras del perfil.

    for z in (0.73, 1.83, 2.93):
        f.box(mb, 0, depth * 0.5 - 0.075, z, width - 0.22, 0.045, 0.055,
              blue, bevel=0.003)
        f.box(mb, 0, -depth * 0.5 + 0.075, z, width - 0.22, 0.045, 0.055,
              blue, bevel=0.003)
    for sx in (-1, 1):
        # Extremos embutidos 10 mm en los montantes: sin tapas coplanares.
        f.box(mb, sx * (width * 0.5 - 0.075), 0, 0.73,
              0.045, depth - 0.20, 0.055, blue, bevel=0.003)
        f.box(mb, sx * (width * 0.5 - 0.075), 0, 2.93,
              0.045, depth - 0.20, 0.055, blue, bevel=0.003)

    for li, z in enumerate(levels[:3]):
        for sx in (-1, 1):
            kind = (li + (1 if sx > 0 else 0)) % 3
            rack_load(mb, f, sx * 0.655, 0.0, z + 0.068, kind)

    mb.build(col())


def rack_labels():
    mb = vest.MeshBuilder("WH_RackLabels_SIGN")
    label = get_mat("M_WH_Label")
    dark = get_mat("M_WH_LabelDark")
    for cx in (81.4, 84.3, 87.2, 90.1, 93.0):
        y = 36.0 - 1.10 * 0.5 - 0.012
        mb.add_plane((cx, y, 2.02), 0.52, 0.18, label,
                     rot=(math.radians(90), 0, 0))
        mb.add_box((cx, y - 0.006, 2.02), (0.36, 0.004, 0.035), dark,
                   bevel=0.0)
        mb.add_box((cx - 0.19, y - 0.006, 2.02), (0.035, 0.004, 0.12), dark,
                   bevel=0.0)
    for cy in (19.6, 22.6, 25.6):
        x = 108.55 - 1.10 * 0.5 - 0.012
        mb.add_plane((x, cy, 2.02), 0.52, 0.18, label,
                     rot=(0, math.radians(-90), 0))
        mb.add_box((x - 0.006, cy, 2.02), (0.004, 0.36, 0.035), dark,
                   bevel=0.0)
        mb.add_box((x - 0.006, cy - 0.19, 2.02), (0.004, 0.035, 0.12), dark,
                   bevel=0.0)
    mb.build(col())


# ---------------------------------------------------------------------------
# Elementos de almacén
# ---------------------------------------------------------------------------


def security_cage():
    f = Frame(106.0, 34.8, 0.0)
    mb = vest.MeshBuilder("WH_SecurityCage")
    steel = get_mat("M_WH_Galv")
    dark = get_mat("M_WH_DarkMetal")
    x0, x1 = -1.80, 1.80
    y0, y1 = -1.60, 1.60
    h = 2.65
    for x in (x0, x1):
        for y in (y0, y1):
            # Poste levantado 10 mm: su base queda dentro de la placa y
            # lejos del plano inferior de esta.
            f.box(mb, x, y, 0.010 + (h - 0.010) * 0.5,
                  0.080, 0.080, h - 0.010, steel, bevel=0.005)
            f.box(mb, x, y, 0.018, 0.18, 0.18, 0.036, dark, bevel=0.003)
    for z in (0.08, 2.58):
        for y in (y0 + 0.012, y1 - 0.012):
            f.box(mb, 0, y, z, 3.48, 0.060, 0.060, steel, bevel=0.003)
        for x in (x0 + 0.012, x1 - 0.012):
            f.box(mb, x, 0, z, 0.060, 3.16, 0.060, steel, bevel=0.003)

    # Paneles de malla: barras verticales y horizontales. Las verticales
    # se acortan 2 cm por extremo para no compartir tapas con los postes.
    for y in [y0 + i * 0.18 for i in range(19)]:
        f.box(mb, x0, y, 1.33, 0.022, 0.022, 2.38, steel, bevel=0.001)
        f.box(mb, x1, y, 1.33, 0.022, 0.022, 2.38, steel, bevel=0.001)
    for x in [x0 + i * 0.18 for i in range(21)]:
        f.box(mb, x, y0, 1.33, 0.022, 0.022, 2.38, steel, bevel=0.001)
        f.box(mb, x, y1, 1.33, 0.022, 0.022, 2.38, steel, bevel=0.001)
    for z in (0.42, 0.84, 1.26, 1.68, 2.10, 2.52):
        f.box(mb, x0 + 0.012, 0, z, 0.022, 3.16, 0.022, steel, bevel=0.001)
        f.box(mb, x1 - 0.012, 0, z, 0.022, 3.16, 0.022, steel, bevel=0.001)
        f.box(mb, 0, y0 + 0.012, z, 3.48, 0.022, 0.022, steel, bevel=0.001)
        f.box(mb, 0, y1 - 0.012, z, 3.48, 0.022, 0.022, steel, bevel=0.001)
    # Puerta y candado en la cara oeste.
    f.box(mb, x0, 0.75, 1.33, 0.070, 0.070, 2.42, steel, bevel=0.003)
    f.box(mb, x0, -0.75, 1.33, 0.070, 0.070, 2.42, steel, bevel=0.003)
    f.box(mb, x0 - 0.002, 0, 2.46, 0.064, 1.44, 0.064, steel, bevel=0.003)
    f.box(mb, x0 - 0.025, 0.64, 1.55, 0.060, 0.10, 0.16, dark, bevel=0.004)
    f.box(mb, x0 - 0.060, 0.64, 1.63, 0.060, 0.07, 0.07, steel, bevel=0.003)
    # Contenido: dos palets de carga asegurada, separados de los barrotes.
    pallet(mb, f, -0.65, 0.55, 0.002)
    cargo_box(mb, f, -0.65, 0.55, 0.129, 0.52, 0.44, 0.36)
    cargo_box(mb, f, -0.65, 0.55, 0.498, 0.46, 0.40, 0.30)
    pallet(mb, f, 0.65, 0.55, 0.002)
    tote(mb, f, 0.65, 0.55, 0.129, 0.52, 0.42, 0.30,
         get_mat("M_WH_ToteGray"))
    tote(mb, f, 0.65, 0.55, 0.433, 0.50, 0.40, 0.28,
         get_mat("M_WH_ToteBlue"))
    mb.build(col())
    text_sign("WH_CageSign_SIGN", "ALTA SEGURIDAD", 0.11,
              (103.94, 34.8, 2.18), (-1, 0, 0),
              get_mat("M_VEST_Emissive_Green"), 0.002)


def forklift():
    f = Frame(78.5, 30.5, 0.0)
    mb = vest.MeshBuilder("WH_Forklift")
    yellow = get_mat("M_WH_Forklift")
    dark = get_mat("M_WH_DarkMetal")
    black = get_mat("M_WH_BlackRubber")
    seat = get_mat("M_WH_Seat")
    steel = get_mat("M_WH_Galv")
    red = get_mat("M_FM_Industrial_Red")
    amber = get_mat("M_WH_EmissiveAmber")
    label = get_mat("M_WH_Label")

    # Chasis, contrapeso y capó.
    f.box(mb, 0.28, 0, 0.46, 1.45, 1.02, 0.42, yellow, bevel=0.018,
          segments=2)
    f.box(mb, -0.72, 0, 0.52, 0.78, 1.05, 0.58, yellow, bevel=0.020,
          segments=2)
    f.box(mb, 0.02, 0, 0.76, 0.86, 0.92, 0.26, dark, bevel=0.012)
    f.box(mb, -0.12, 0, 0.91, 0.62, 0.70, 0.11, seat, bevel=0.012)
    f.box(mb, -0.40, 0, 1.15, 0.10, 0.66, 0.42, seat, bevel=0.012)
    f.box(mb, 0.55, 0, 1.02, 0.22, 0.22, 0.28, dark, bevel=0.010)
    f.cyl(mb, 0.55, 0, 1.22, 0.17, 0.030, black, axis="Z", segments=16)
    f.box(mb, 0.55, 0, 1.22, 0.30, 0.035, 0.035, dark, bevel=0.002)
    f.box(mb, 0.55, 0, 1.22, 0.035, 0.30, 0.035, dark, bevel=0.002)

    # Ruedas.
    f.cyl(mb, 0.72, -0.58, 0.30, 0.285, 0.20, black, axis="Y",
          segments=20, bevel=0.010)
    f.cyl(mb, 0.72, 0.58, 0.30, 0.285, 0.20, black, axis="Y",
          segments=20, bevel=0.010)
    f.cyl(mb, -0.68, -0.52, 0.235, 0.225, 0.17, black, axis="Y",
          segments=18, bevel=0.008)
    f.cyl(mb, -0.68, 0.52, 0.235, 0.225, 0.17, black, axis="Y",
          segments=18, bevel=0.008)
    for x in (0.72, -0.68):
        for y in (-0.58, 0.58):
            r = 0.12 if x > 0 else 0.09
            f.cyl(mb, x, y, 0.30 if x > 0 else 0.235, r,
                  0.215 if x > 0 else 0.185, steel, axis="Y",
                  segments=12, bevel=0.004)

    # Mástil, horquillas y jaula antivuelco.
    for y in (-0.46, 0.46):
        f.box(mb, 1.00, y, 1.30, 0.11, 0.11, 2.50, dark, bevel=0.006)
    for z in (0.55, 1.15, 1.75, 2.35):
        f.box(mb, 1.00, 0, z, 0.12, 0.98, 0.10, dark, bevel=0.004)
    for y in (-0.24, 0.24):
        f.box(mb, 1.55, y, 0.085, 1.10, 0.13, 0.055, steel, bevel=0.004)
    f.box(mb, 1.04, 0, 0.22, 0.10, 0.70, 0.10, dark, bevel=0.004)

    for x in (-0.55, 0.55):
        for y in (-0.50, 0.50):
            f.box(mb, x, y, 1.55, 0.070, 0.070, 1.10, dark, bevel=0.004)
    f.box(mb, 0, 0, 2.12, 1.34, 1.12, 0.06, dark, bevel=0.006)
    for y in (-0.44, 0.0, 0.44):
        f.box(mb, 0, y, 2.16, 1.24, 0.055, 0.045, yellow, bevel=0.003)
    f.box(mb, 0, 0, 2.02, 0.055, 1.02, 0.055, yellow, bevel=0.003)

    # Bombona de GLP y baliza.
    f.cyl(mb, -0.62, 0, 1.02, 0.15, 0.70, red, axis="Y", segments=16,
          bevel=0.006)
    f.box(mb, -0.62, 0, 1.20, 0.12, 0.48, 0.035, dark, bevel=0.002)
    f.box(mb, 0.55, 0, 2.20, 0.10, 0.10, 0.12, amber, bevel=0.005)
    f.cyl(mb, 0.55, 0, 2.29, 0.06, 0.06, amber, axis="Z", segments=10)

    # Identificación.
    f.box(mb, -0.72, -0.535, 0.47, 0.34, 0.006, 0.20, label, bevel=0.0)
    f.box(mb, 0.15, -0.515, 0.64, 0.58, 0.004, 0.16, yellow, bevel=0.0)
    mb.build(col())


def conveyor():
    f = Frame(94.5, 9.55, 0.0)
    mb = vest.MeshBuilder("WH_Conveyor")
    steel = get_mat("M_FM_Steel_Dark")
    galv = get_mat("M_WH_Galv")
    dark = get_mat("M_WH_DarkMetal")
    yellow = get_mat("M_WH_Yellow")
    black = get_mat("M_WH_BlackRubber")
    red = get_mat("M_WH_EmissiveRed")
    length = 5.20
    for x in (-2.45, -1.35, -0.25, 0.85, 1.95):
        for y in (-0.28, 0.28):
            f.box(mb, x, y, 0.40, 0.060, 0.060, 0.80, steel, bevel=0.003)
    for y in (-0.33, 0.33):
        f.box(mb, 0, y, 0.82, length, 0.050, 0.12, yellow, bevel=0.004)
        f.box(mb, 0, y, 0.70, length, 0.040, 0.045, steel, bevel=0.002)
    for i in range(26):
        x = -2.44 + i * 0.195
        f.cyl(mb, x, 0, 0.885, 0.045, 0.58, galv, axis="Y",
              segments=10)
    f.box(mb, 2.10, 0, 0.58, 0.40, 0.52, 0.28, steel, bevel=0.008)
    f.box(mb, 2.36, 0.46, 1.02, 0.22, 0.20, 0.34, dark, bevel=0.006)
    f.cyl(mb, 2.36, 0.46, 1.18, 0.045, 0.035, red, axis="Z", segments=10)
    f.box(mb, 2.36, 0.46, 1.10, 0.12, 0.02, 0.08,
          get_mat("M_WH_ScreenGlow"), bevel=0.0)
    # Cajas sobre la cinta.
    cargo_box(mb, f, -0.55, 0, 0.934, 0.46, 0.40, 0.34)
    cargo_box(mb, f, 0.45, 0, 0.934, 0.42, 0.38, 0.30)
    mb.build(col())


def packing_station():
    f = Frame(87.2, 8.92, 0.0)
    mb = vest.MeshBuilder("WH_PackingTable")
    steel = get_mat("M_FM_Steel_Dark")
    wood = get_mat("M_FM_Workbench_Wood")
    galv = get_mat("M_WH_Galv")
    dark = get_mat("M_WH_DarkMetal")
    paper = get_mat("M_VEST_Paper")
    yellow = get_mat("M_WH_Yellow")
    screen = get_mat("M_WH_ScreenGlow")

    f.box(mb, 0, 0, 0.905, 5.40, 0.95, 0.08, wood, bevel=0.008)
    for x in (-2.55, -1.25, 0.05, 1.35, 2.55):
        for y in (-0.38, 0.38):
            f.box(mb, x, y, 0.44, 0.065, 0.065, 0.86, steel, bevel=0.003)
    f.box(mb, 0, 0, 0.30, 5.30, 0.82, 0.06, galv, bevel=0.006)
    f.box(mb, 0, -0.46, 1.10, 5.10, 0.035, 1.20,
          get_mat("M_FM_Pegboard"), bevel=0.004)
    for x in (-2.48, 2.48):
        f.box(mb, x, -0.50, 0.55, 0.05, 0.05, 1.10, steel, bevel=0.002)
    # Estante superior con impresora y monitor.
    f.box(mb, 1.45, -0.30, 1.62, 0.90, 0.42, 0.05, galv, bevel=0.004)
    f.box(mb, 1.45, -0.30, 1.76, 0.50, 0.38, 0.24, dark, bevel=0.010)
    f.box(mb, 1.45, -0.495, 1.78, 0.34, 0.018, 0.16, screen, bevel=0.0)
    f.box(mb, 0.55, -0.30, 1.67, 0.40, 0.34, 0.28, dark, bevel=0.008)
    f.box(mb, 0.55, -0.475, 1.73, 0.28, 0.012, 0.17, screen, bevel=0.0)
    # Báscula, dispensador y cajas.
    f.box(mb, -1.55, 0.02, 0.985, 0.48, 0.38, 0.08, galv, bevel=0.006)
    f.box(mb, -1.55, 0.02, 1.06, 0.20, 0.16, 0.10, dark, bevel=0.004)
    f.box(mb, -1.55, 0.02, 1.12, 0.16, 0.04, 0.07, screen, bevel=0.0)
    f.box(mb, -0.70, -0.10, 1.00, 0.28, 0.22, 0.18, dark, bevel=0.006)
    f.cyl(mb, -0.70, -0.10, 1.12, 0.07, 0.10, yellow, axis="X",
          segments=10)
    cargo_box(mb, f, 0.35, 0.03, 0.949, 0.42, 0.36, 0.32)
    cargo_box(mb, f, 0.95, 0.00, 0.949, 0.46, 0.40, 0.36)
    # Portapapeles y hoja.
    f.box(mb, -0.25, 0.28, 0.955, 0.34, 0.24, 0.015, paper, bevel=0.002)
    f.box(mb, -0.25, 0.28, 0.968, 0.28, 0.19, 0.004, dark, bevel=0.0)
    f.box(mb, -1.05, 0.30, 0.958, 0.24, 0.17, 0.005, paper, bevel=0.0)
    mb.build(col())


def staging_island():
    f = Frame(96.5, 30.5, 0.0)
    mb = vest.MeshBuilder("WH_Staging")
    for lx in (-0.68, 0.68):
        pallet(mb, f, lx, 0, 0.002)
        cargo_box(mb, f, lx - 0.24, 0, 0.146, 0.45, 0.42, 0.38)
        cargo_box(mb, f, lx + 0.24, 0, 0.146, 0.45, 0.42, 0.38)
        cargo_box(mb, f, lx, 0, 0.534, 0.48, 0.42, 0.34)
        film_wrap(mb, f, lx, 0, 0.52, 1.02, 0.94, 0.72)
    tote(mb, f, 0, 0.72, 0.002, 0.50, 0.40, 0.30,
         get_mat("M_WH_ToteGray"))
    tote(mb, f, 0.55, 0.72, 0.002, 0.50, 0.40, 0.30,
         get_mat("M_WH_ToteBlue"))
    tote(mb, f, 0.28, 0.72, 0.308, 0.50, 0.40, 0.30,
         get_mat("M_WH_ToteGray"))
    mb.build(col())


def mezzanine():
    """Plataforma de supervisión sobre el pasillo central, con rampa."""
    x0, x1 = 87.60, 93.60
    y0, y1 = 27.60, 33.60
    deck_top = 2.60
    deck_th = 0.16
    deck_z = deck_top - deck_th * 0.5
    galv = get_mat("M_WH_Galv")
    dark = get_mat("M_WH_DarkMetal")
    blue = get_mat("M_WH_RackBlue")
    deck_mat = get_mat("M_WH_RackDeck")
    yellow = get_mat("M_WH_Yellow")
    label = get_mat("M_WH_Label")

    mb = vest.MeshBuilder("WH_Mezzanine")
    # Plataforma y fleje amarillo de borde.
    mb.add_box(((x0 + x1) * 0.5, (y0 + y1) * 0.5, deck_z),
               (x1 - x0, y1 - y0, deck_th), deck_mat, bevel=0.0)
    for x in (x0 + 0.05, x1 - 0.05):
        mb.add_box((x, (y0 + y1) * 0.5, deck_top + 0.010),
                   (0.06, y1 - y0 - 0.10, 0.008), yellow, bevel=0.0)
    for y in (y0 + 0.05, y1 - 0.05):
        mb.add_box(((x0 + x1) * 0.5, y, deck_top + 0.010),
                   (x1 - x0 - 0.10, 0.06, 0.008), yellow, bevel=0.0)

    # Postes y vigas de apoyo.
    for x in (x0 + 0.28, x1 - 0.28):
        for y in (y0 + 0.28, y1 - 0.28):
            mb.add_box((x, y, 1.23), (0.14, 0.14, 2.46), blue, bevel=0.0)
            mb.add_box((x, y, 2.395), (0.28, 0.28, 0.11), dark, bevel=0.0)
    for x in (x0 + 0.28, x1 - 0.28):
        mb.add_box((x, (y0 + y1) * 0.5, 2.42),
                   (0.12, y1 - y0 - 0.30, 0.14), blue, bevel=0.0)
    for y in (y0 + 0.28, y1 - 0.28):
        mb.add_box(((x0 + x1) * 0.5, y, 2.42),
                   (x1 - x0 - 0.30, 0.12, 0.14), blue, bevel=0.0)

    # Barandilla perimetral, con hueco en el borde sur para la rampa.
    posts = set()
    for x in (x0 + 0.10, x0 + 1.60, x0 + 3.10, x1 - 0.10):
        posts.add((round(x, 3), round(y1 - 0.10, 3)))
        posts.add((round(x, 3), round(y0 + 0.10, 3)))
    for y in (y0 + 0.10, y0 + 1.60, y0 + 3.10, y1 - 0.10):
        posts.add((round(x0 + 0.10, 3), round(y, 3)))
        posts.add((round(x1 - 0.10, 3), round(y, 3)))
    for x, y in sorted(posts):
        mb.add_box((x, y, deck_top + 0.53), (0.055, 0.055, 1.14),
                   galv, bevel=0.0)
    mb.add_box(((x0 + x1) * 0.5, y1 - 0.08, deck_top + 1.08),
               (x1 - x0 - 0.30, 0.05, 0.05), galv, bevel=0.0)
    mb.add_box(((x0 + x1) * 0.5, y1 - 0.08, deck_top + 0.58),
               (x1 - x0 - 0.30, 0.04, 0.04), galv, bevel=0.0)
    sx0, sx1 = x0 + 1.50, x1 - 0.08
    mb.add_box(((sx0 + sx1) * 0.5, y0 + 0.08, deck_top + 1.08),
               (sx1 - sx0, 0.05, 0.05), galv, bevel=0.0)
    mb.add_box(((sx0 + sx1) * 0.5, y0 + 0.08, deck_top + 0.58),
               (sx1 - sx0, 0.04, 0.04), galv, bevel=0.0)
    for x in (x0 + 0.08, x1 - 0.08):
        mb.add_box((x, (y0 + y1) * 0.5, deck_top + 1.08),
                   (0.05, y1 - y0 - 0.30, 0.05), galv, bevel=0.0)
        mb.add_box((x, (y0 + y1) * 0.5, deck_top + 0.58),
                   (0.04, y1 - y0 - 0.30, 0.04), galv, bevel=0.0)

    # Rampa de acceso (1,5 m de ancho, 26,6°), con peldaños antideslizantes.
    rx0, rx1 = x0, x0 + 1.50
    ry0, ry1 = 22.40, 27.60
    rz0, rz1 = 0.02, deck_top
    run = ry1 - ry0
    rise = rz1 - rz0
    length = math.hypot(run, rise)
    theta = math.atan2(rise, run)
    cy, cz = (ry0 + ry1) * 0.5, (rz0 + rz1) * 0.5
    thick = 0.10
    mb.add_box(((rx0 + rx1) * 0.5,
                cy + math.sin(theta) * thick * 0.5,
                cz - math.cos(theta) * thick * 0.5),
               (rx1 - rx0, length, thick), deck_mat, bevel=0.0,
               rot=(theta, 0.0, 0.0))
    for i in range(13):
        y = ry0 + 0.28 + i * 0.40
        z = rz0 + (y - ry0) / run * rise
        mb.add_box(((rx0 + rx1) * 0.5, y, z + 0.012),
                   (rx1 - rx0 - 0.14, 0.04, 0.025), yellow, bevel=0.0)
    # Umbrales y pasamanos de la rampa. La placa de base solapa el suelo y el
    # arranque de la rampa para que el navmesh una ambos tramos.
    mb.add_box(((rx0 + rx1) * 0.5, ry0 - 0.18, 0.020),
               (rx1 - rx0 - 0.02, 1.20, 0.060), yellow, bevel=0.0)
    for x in (rx0 + 0.05, rx1 - 0.05):
        for y in (ry0 + 0.05, ry0 + 1.30, ry0 + 2.60, ry0 + 3.90,
                  ry1 - 0.05):
            z = rz0 + (y - ry0) / run * rise
            mb.add_box((x, y, z + 0.51), (0.05, 0.05, 1.08),
                       galv, bevel=0.0)
        for lift in (0.55, 1.02):
            zc = cz + lift
            mb.add_box((x, cy + math.sin(theta) * 0.025,
                        zc - math.cos(theta) * 0.025),
                       (0.05, length, 0.05), galv, bevel=0.0,
                       rot=(theta, 0.0, 0.0))

    # Panel y soportes del rótulo de la barandilla sur.
    mb.add_box((90.60, 27.60, 3.38), (1.95, 0.05, 0.30), dark, bevel=0.0)
    for x in (89.80, 91.40):
        mb.add_box((x, 27.64, 3.38), (0.04, 0.10, 0.04), galv, bevel=0.0)
    mb.build(col())

    # Mobiliario de supervisión sobre la plataforma.
    mb = vest.MeshBuilder("WH_Mezz_Desk")
    wood = get_mat("M_FM_Workbench_Wood", "M_WH_RackDeck")
    green = get_mat("M_FM_Painted_Green", "M_WH_RackBlue")
    screen = get_mat("M_WH_ScreenGlow")
    cx, cy2, top = 91.70, 32.25, 3.35
    mb.add_box((cx, cy2, top), (1.55, 0.72, 0.06), wood, bevel=0.0)
    for dx in (-0.68, 0.68):
        for dy in (-0.28, 0.28):
            mb.add_box((cx + dx, cy2 + dy, top - 0.37),
                       (0.05, 0.05, 0.70), dark, bevel=0.0)
    mb.add_box((cx, cy2 - 0.31, top - 0.36), (1.40, 0.035, 0.56),
               green, bevel=0.0)
    mb.add_box((cx, cy2 + 0.12, top + 0.25), (0.62, 0.06, 0.40),
               dark, bevel=0.0)
    mb.add_box((cx, cy2 + 0.09, top + 0.25), (0.54, 0.012, 0.32),
               screen, bevel=0.0)
    mb.add_box((cx, cy2 + 0.12, top + 0.04), (0.18, 0.08, 0.03),
               dark, bevel=0.0)
    mb.add_box((cx, cy2 - 0.12, top + 0.02), (0.42, 0.16, 0.03),
               dark, bevel=0.0)
    mb.add_box((cx - 0.45, cy2 - 0.10, top + 0.007), (0.24, 0.18, 0.008),
               label, bevel=0.0)
    mb.add_box((cx + 0.55, cy2 - 0.10, top + 0.04), (0.18, 0.22, 0.08),
               dark, bevel=0.0)
    mb.build(col())

    mb = vest.MeshBuilder("WH_Mezz_Chair")
    seat_z = 3.05
    mb.add_box((91.70, 33.05, seat_z), (0.48, 0.46, 0.06), dark,
               bevel=0.0)
    mb.add_box((91.70, 33.27, seat_z + 0.24), (0.46, 0.06, 0.48),
               dark, bevel=0.0)
    for dx in (-0.19, 0.19):
        for dy in (-0.17, 0.17):
            mb.add_box((91.70 + dx, 33.05 + dy, 2.8275),
                       (0.04, 0.04, 0.445), galv, bevel=0.0)
    mb.build(col())

    mb = vest.MeshBuilder("WH_Mezz_Cabinet")
    mb.add_box((93.08, 32.85, 3.225), (0.55, 0.64, 1.25), green,
               bevel=0.0)
    mb.add_box((93.08, 32.52, 3.225), (0.47, 0.018, 1.10), dark,
               bevel=0.0)
    for z in (2.88, 3.28, 3.68):
        mb.add_box((93.08, 32.50, z), (0.34, 0.020, 0.025), galv,
                   bevel=0.0)
    mb.build(col())

    mb = vest.MeshBuilder("WH_Mezz_Crates")
    f = Frame(88.55, 32.45, 0.0)
    pallet(mb, f, 0, 0, deck_top + 0.002)
    cargo_box(mb, f, -0.24, 0, deck_top + 0.134, 0.46, 0.42, 0.36)
    cargo_box(mb, f, 0.24, 0, deck_top + 0.134, 0.46, 0.42, 0.36)
    cargo_box(mb, f, 0, 0, deck_top + 0.514, 0.48, 0.42, 0.30)
    tote(mb, f, 0.30, 0.72, deck_top + 0.002, 0.46, 0.36, 0.28,
         get_mat("M_WH_ToteBlue"))
    mb.build(col())

    # Luminarias de la plataforma (sin colisión).
    mb = vest.MeshBuilder("WH_Mezz_Lamps_LIGHT")
    cool = get_mat("M_VEST_Emissive_Cool")
    amber = get_mat("M_WH_EmissiveAmber")
    for x, y in ((89.60, 30.60), (91.70, 30.60)):
        mb.add_box((x, y, 2.45), (0.62, 0.18, 0.04), cool, bevel=0.0)
    mb.add_box((92.35, 32.30, 3.53), (0.06, 0.06, 0.24), dark,
               bevel=0.0)
    mb.add_box((92.35, 32.30, 3.67), (0.16, 0.16, 0.04), amber,
               bevel=0.0)
    mb.build(col())

    mb = vest.MeshBuilder("WH_Mezz_FloorMark_FLOOR_LINE")
    _ax, _ay, _az = 88.35, 21.45, 0.012
    _pts = ((-0.075, -0.32), (0.075, -0.32), (0.075, 0.06),
            (-0.075, 0.06), (-0.22, 0.06), (0.22, 0.06), (0.0, 0.30))
    _verts = [(_ax + px, _ay + py, _az) for px, py in _pts]
    _faces = [(0, 1, 2, 3), (3, 6, 4), (2, 5, 6)]
    _uvs = [[(0, 0), (1, 0), (1, 1), (0, 1)],
            [(0, 0), (1, 1), (0, 1)],
            [(0, 0), (1, 0), (0.5, 1)]]
    mb._append(yellow, _verts, _faces, _uvs)
    mb.build(col())

    text_sign("WH_Mezz_Sign_SIGN", "CONTROL DE INVENTARIO", 0.145,
              (90.60, 27.565, 3.38), (0, -1, 0), label)
    text_sign("WH_Mezz_LoadSign_SIGN", "CARGA MAX. 250 kg", 0.075,
              (88.35, 27.565, 2.98), (0, -1, 0), label)


def pallet_jack():
    f = Frame(81.2, 22.0, math.radians(90))
    mb = vest.MeshBuilder("WH_PalletJack")
    steel = get_mat("M_FM_Safety_Yellow", "M_WH_Yellow")
    dark = get_mat("M_WH_DarkMetal")
    black = get_mat("M_WH_BlackRubber")
    for y in (-0.25, 0.25):
        f.box(mb, 0.48, y, 0.085, 1.10, 0.13, 0.055, steel, bevel=0.004)
    f.box(mb, -0.08, 0, 0.14, 0.35, 0.62, 0.14, steel, bevel=0.006)
    f.cyl(mb, 0.08, 0, 0.18, 0.10, 0.58, dark, axis="Y", segments=12)
    f.cyl(mb, -0.28, 0, 0.18, 0.10, 0.10, black, axis="Y", segments=12)
    f.cyl(mb, -0.28, 0.30, 0.18, 0.10, 0.10, black, axis="Y", segments=12)
    f.box(mb, -0.38, 0, 0.72, 0.05, 0.05, 1.05, steel, bevel=0.003)
    f.box(mb, -0.40, 0, 1.23, 0.05, 0.52, 0.05, dark, bevel=0.003)
    # Sin topes embebidos: sus caras eran coplanares con la barra del asa.
    mb.build(col())


def toppled_cart():
    f = Frame(76.2, 11.4, math.radians(-28))
    mb = vest.MeshBuilder("WH_ToppledCart")
    galv = get_mat("M_WH_Galv")
    dark = get_mat("M_WH_DarkMetal")
    black = get_mat("M_WH_BlackRubber")
    f.box(mb, 0, 0, 0.12, 0.90, 1.15, 0.08, galv, bevel=0.005)
    for x in (-0.34, 0.34):
        for y in (-0.42, 0.42):
            f.cyl(mb, x, y, 0.042, 0.038, 0.06, black, axis="Y",
                  segments=10)
    for x in (-0.42, 0.42):
        f.box(mb, x, 0, 0.17, 0.05, 1.13, 0.10, dark, bevel=0.003)
    f.box(mb, -0.46, 0, 0.42, 0.05, 0.05, 0.60, dark, bevel=0.003)
    f.box(mb, -0.46, 0, 0.72, 0.05, 0.55, 0.05, dark, bevel=0.003)
    cargo_box(mb, f, 0.22, 0.20, 0.164, 0.40, 0.34, 0.30)
    mb.build(col())


# ---------------------------------------------------------------------------
# Techo, muros y señalización
# ---------------------------------------------------------------------------


def ceiling_services():
    steel = get_mat("M_FM_Steel_Dark")
    galv = get_mat("M_WH_Galv")
    dark = get_mat("M_WH_DarkMetal")
    red = get_mat("M_FM_Sprinkler_Red")
    cool = get_mat("M_VEST_Emissive_Cool")
    amber = get_mat("M_WH_EmissiveAmber")
    light_red = get_mat("M_WH_EmissiveRed")

    # Vigas I sobre las líneas de columnas.
    mb = vest.MeshBuilder("WH_CeilingBeams_TRIM")
    for y in (16.0, 24.0, 32.0):
        mb.add_box((90.0, y, 5.34), (39.7, 0.30, 0.045), steel, bevel=0.004)
        mb.add_box((90.0, y, 5.50), (39.7, 0.045, 0.28), steel, bevel=0.003)
        mb.add_box((90.0, y, 5.66), (39.7, 0.30, 0.045), steel, bevel=0.004)
        for x in (70.25, 109.75):
            mb.add_box((x, y, 5.50), (0.10, 0.45, 0.52), dark, bevel=0.005)
    mb.build(col())

    # Conducto HVAC con cuello y rejillas.
    mb = vest.MeshBuilder("WH_HVAC_DIFFUSER")
    x0, x1 = 70.45, 104.0
    cy, cz = 20.0, 3.72
    length = x1 - x0
    cx = (x0 + x1) * 0.5
    mb.add_box((cx, cy, cz + 0.34), (length, 1.05, 0.045), galv, bevel=0.0)
    mb.add_box((cx, cy, cz - 0.34), (length, 1.05, 0.045), galv, bevel=0.0)
    mb.add_box((cx, cy - 0.52, cz), (length, 0.045, 0.72), galv, bevel=0.0)
    mb.add_box((cx, cy + 0.52, cz), (length, 0.045, 0.72), galv, bevel=0.0)
    for i in range(13):
        x = x0 + i * (length / 12.0)
        mb.add_box((x, cy, cz), (0.055, 1.10, 0.76), dark, bevel=0.003)
        mb.add_box((x, cy, 4.98), (0.035, 0.035, 1.84), steel, bevel=0.002)
    for x in (74.0, 82.0, 90.0, 98.0):
        mb.add_box((x, cy, cz - 0.355), (0.72, 0.46, 0.025), dark,
                   bevel=0.004)
        for dy in (-0.18, 0.0, 0.18):
            mb.add_box((x, cy + dy, cz - 0.385), (0.62, 0.035, 0.02), galv,
                       bevel=0.001)
    mb.build(col())

    # Bandeja de cables.
    mb = vest.MeshBuilder("WH_CableTray_CABLE")
    for y in (22.75, 23.25):
        mb.add_box((89.9, y, 4.52), (39.4, 0.04, 0.10), galv, bevel=0.003)
    for i in range(111):
        x = 70.35 + i * 0.355
        mb.add_box((x, 23.0, 4.50), (0.035, 0.52, 0.035), galv, bevel=0.001)
    for x in (72.0, 80.0, 88.0, 96.0, 104.0):
        mb.add_box((x, 23.0, 4.50), (0.12, 0.55, 0.05), galv, bevel=0.002)
        mb.add_box((x, 23.0, 5.17), (0.035, 0.035, 1.32), steel, bevel=0.002)
    mb.build(col())

    # Ramal de bandeja hacia la escalera de emergencia E1.
    mb = vest.MeshBuilder("WH_E1_TrayLink_CABLE")
    tray_mat = get_mat("M_WH_Galv")
    cable_mat = get_mat("M_VEST_Black")
    tray_segment(mb, tray_mat, 107.0, 12.25, 107.0, 22.75, 4.50)
    tray_segment(mb, tray_mat, 107.25, 12.25, 110.0, 12.25, 4.50)
    for x in (106.90, 107.00, 107.10):
        mb.add_cyl((x, 17.50, 4.56), 0.018, 10.10, cable_mat,
                   axis="Y", segments=8)
    for y in (12.15, 12.25, 12.35):
        mb.add_cyl((108.63, y, 4.56), 0.018, 2.50, cable_mat,
                   axis="X", segments=8)
    for x, y in ((107.0, 21.0), (107.0, 17.0), (107.0, 13.0),
                 (108.5, 12.25), (109.5, 12.25)):
        tray_hanger(mb, tray_mat, x, y, 4.50, 5.89)
    mb.build(col())

    # Enlace de bandeja con Z10 por el ServiceLink y resalte en el vano oeste.
    mb = vest.MeshBuilder("WH_ServiceLink_Tray_CABLE")
    # Tramo horizontal dentro del ServiceLink, a cota compatible con su techo.
    mb.add_box((65.95, 22.75, 3.020), (8.30, 0.50, 0.05), galv,
               bevel=0.0)
    for y in (22.50, 23.00):
        mb.add_box((65.95, y, 3.075), (8.22, 0.04, 0.12), galv,
                   bevel=0.0)
    for i in range(11):
        mb.add_box((62.20 + i * 0.76, 22.75, 3.090),
                   (0.04, 0.50, 0.08), galv, bevel=0.0)
    # Codo vertical y pasamuros inferior (el vano solo tiene 2,6 m).
    for y in (22.54, 22.96):
        mb.add_box((69.90, y, 2.750), (0.05, 0.05, 0.62), galv,
                   bevel=0.0)
    for i in range(3):
        mb.add_box((69.90, 22.75, 2.50 + i * 0.18),
                   (0.04, 0.42, 0.04), galv, bevel=0.0)
    # Cables que cruzan el vano.
    for y in (22.60, 22.75, 22.90):
        mb.add_cyl((70.10, y, 2.44), 0.020, 0.62, dark,
                   axis="X", segments=8)
    # Marco de sleeve en el muro oeste.
    for z in (2.24, 2.56):
        mb.add_box((70.0, 22.75, z), (0.14, 1.30, 0.05), steel,
                   bevel=0.0)
    for y in (22.10, 23.40):
        mb.add_box((70.0, y, 2.40), (0.10, 0.05, 0.33), steel,
                   bevel=0.0)
    # Resalte vertical dentro del Almacén hasta la bandeja existente.
    for y in (22.50, 23.00):
        mb.add_box((70.35, y, 3.500), (0.05, 0.06, 2.10), galv,
                   bevel=0.0)
    for i in range(6):
        mb.add_box((70.35, 22.75, 2.58 + i * 0.34),
                   (0.04, 0.52, 0.04), galv, bevel=0.0)
    for y in (22.60, 22.75, 22.90):
        mb.add_cyl((70.35, y, 3.480), 0.020, 2.02, dark,
                   axis="Z", segments=8)
    # Conexión superior con el extremo oeste de la bandeja del Almacén.
    mb.add_box((70.55, 22.75, 4.510), (0.50, 0.55, 0.05), galv,
               bevel=0.0)
    for z in (3.35, 4.15):
        mb.add_box((70.20, 22.75, z), (0.28, 0.70, 0.06), steel,
                   bevel=0.0)
    mb.build(col())
    mb = vest.MeshBuilder("WH_Sprinkler_CABLE")
    mb.add_cyl((89.9, 27.0, 4.86), 0.055, 39.3, red, axis="X", segments=12)
    for x in (74.0, 82.0, 90.0, 98.0, 106.0):
        mb.add_cyl((x, 27.0, 4.64), 0.020, 0.44, red, axis="Z", segments=8)
        mb.add_cyl((x, 27.0, 4.40), 0.055, 0.035, galv, axis="Z", segments=10)
        mb.add_box((x, 27.0, 5.22), (0.03, 0.03, 1.15), steel, bevel=0.001)
    mb.build(col())

    # Polipasto sobre la isla de staging.
    mb = vest.MeshBuilder("WH_Hoist_TRIM")
    mb.add_box((97.0, 30.0, 5.02), (0.20, 9.0, 0.24), steel, bevel=0.006)
    for y in (25.6, 34.4):
        mb.add_box((97.0, y, 5.38), (0.12, 0.12, 0.64), dark, bevel=0.004)
    mb.add_box((97.0, 30.0, 4.90), (0.42, 0.55, 0.22), dark, bevel=0.006)
    for i in range(6):
        mb.add_box((97.0, 30.0, 4.72 - i * 0.12), (0.035, 0.035, 0.12),
                   galv, bevel=0.001)
    mb.add_box((97.0, 30.0, 3.92), (0.10, 0.10, 0.16), dark, bevel=0.004)
    mb.add_box((97.0, 30.0, 3.82), (0.22, 0.06, 0.06), galv, bevel=0.003)
    mb.build(col())

    # Luminarias high-bay.
    for i, (x, y) in enumerate([(p, q) for q in (14.0, 28.0)
                                for p in (78.0, 86.0, 94.0, 102.0)]):
        mb = vest.MeshBuilder("WH_HighBay_LIGHT_%02d" % (i + 1))
        mb.add_cyl((x, y, 5.20), 0.20, 0.10, dark, axis="Z", segments=14)
        mb.add_cyl((x, y, 5.10), 0.31, 0.09, steel, axis="Z", segments=14)
        mb.add_cyl((x, y, 5.045), 0.265, 0.025, cool, axis="Z",
                   segments=14)
        for dx, dy in ((-0.18, -0.18), (0.18, -0.18),
                       (-0.18, 0.18), (0.18, 0.18)):
            mb.add_box((x + dx, y + dy, 5.55), (0.018, 0.018, 0.58),
                       steel, bevel=0.001)
        mb.build(col())

    # Balizas de emergencia en las salidas.
    for i, (x, y, z, rz) in enumerate((
            (72.0, 8.42, 3.05, 0.0),
            (109.58, 12.0, 3.05, math.radians(90)),
            (70.42, 35.8, 3.05, math.radians(-90)))):
        mb = vest.MeshBuilder("WH_Emerg_LIGHT_%02d" % (i + 1))
        mb.add_box((x, y, z - 0.16), (0.16, 0.08, 0.10), dark, bevel=0.004)
        mb.add_cyl((x, y, z), 0.075, 0.10, light_red, axis="Z",
                   segments=12)
        mb.add_cyl((x, y, z + 0.06), 0.05, 0.05, amber, axis="Z",
                   segments=10)
        if i == 0:
            mb.add_box((x, 8.29, z - 0.12), (0.10, 0.30, 0.08), steel,
                       bevel=0.002)
        elif i == 1:
            mb.add_box((109.72, y, z - 0.12), (0.30, 0.10, 0.08), steel,
                       bevel=0.002)
        else:
            mb.add_box((70.29, y, z - 0.12), (0.30, 0.10, 0.08), steel,
                       bevel=0.002)
        mb.build(col())


def wainscot_segment(name, axis, coord, start, end, out):
    """Panel corrugado entre dos coordenadas sobre un muro.

    `out` apunta desde el muro hacia el interior de la sala (+1/-1).
    """
    if end - start < 0.4:
        return
    mb = vest.MeshBuilder(name)
    panel = get_mat("M_FM_Metal_Panel")
    rib = get_mat("M_Z10_HERO_Steel_Galv_2K", "M_WH_Galv")
    cap = get_mat("M_WH_Yellow")
    base = get_mat("M_WH_DarkMetal")
    mid = (start + end) * 0.5
    length = end - start
    if axis == "x":
        center = (mid, coord, 1.10)
        size = (length, 0.025, 2.10)
        rib_size = (0.040, 0.045, 2.05)
        cap_size = (length - 0.02, 0.060, 0.055)
        base_size = (length - 0.02, 0.055, 0.10)
    else:
        center = (coord, mid, 1.10)
        size = (0.025, length, 2.10)
        rib_size = (0.045, 0.040, 2.05)
        cap_size = (0.060, length - 0.02, 0.055)
        base_size = (0.055, length - 0.02, 0.10)
    world_box(mb, center, size, panel, bevel=0.0)
    if axis == "x":
        world_box(mb, (mid, coord + out * 0.025, 2.16), cap_size, cap,
                  bevel=0.002)
        world_box(mb, (mid, coord + out * 0.020, 0.06), base_size, base,
                  bevel=0.002)
    else:
        world_box(mb, (coord + out * 0.025, mid, 2.16), cap_size, cap,
                  bevel=0.002)
        world_box(mb, (coord + out * 0.020, mid, 0.06), base_size, base,
                  bevel=0.002)
    n = max(1, int(length / 0.34))
    for i in range(n):
        p = start + (i + 0.5) * (length / n)
        if axis == "x":
            world_box(mb, (p, coord + out * 0.030, 1.10), rib_size, rib,
                      bevel=0.001)
        else:
            world_box(mb, (coord + out * 0.030, p, 1.10), rib_size, rib,
                      bevel=0.001)
    mb.build(col())


def wall_treatment():
    # Zócalos metálicos, evitando vanos.
    wainscot_segment("WH_Wainscot_S_01", "x", 8.18, 74.10, 109.70, 1)
    wainscot_segment("WH_Wainscot_N_01", "x", 37.82, 70.20, 109.70, -1)
    wainscot_segment("WH_Wainscot_E_01", "y", 109.82, 14.10, 37.70, -1)
    wainscot_segment("WH_Wainscot_W_S_01", "y", 70.18, 8.20, 18.00, 1)
    wainscot_segment("WH_Wainscot_W_N_01", "y", 70.18, 24.00, 34.00, 1)

    # Franja de peligro sobre el zócalo.
    mb = vest.MeshBuilder("WH_HazardBand_TRIM")
    hz = get_mat("M_FM_Hazard_Stripes", "M_WH_Yellow")
    for axis, coord, a, b, out in (("x", 8.205, 74.2, 109.7, 1),
                                   ("x", 37.795, 70.3, 109.7, -1),
                                   ("y", 109.795, 14.2, 37.7, -1),
                                   ("y", 70.205, 8.3, 33.9, 1)):
        mid = (a + b) * 0.5
        ln = b - a
        if axis == "x":
            mb.add_box((mid, coord + out * 0.010, 2.245),
                       (ln, 0.012, 0.14), hz, bevel=0.0)
        else:
            mb.add_box((coord + out * 0.010, mid, 2.245),
                       (0.012, ln, 0.14), hz, bevel=0.0)
    mb.build(col())


def wall_sign(name, text, tsize, loc, normal, panel_w, panel_h,
              text_mat=None, panel_mat=None, double_sided=False):
    text_mat = text_mat or get_mat("M_VEST_Emissive_Green")
    panel_mat = panel_mat or get_mat("M_WH_DarkMetal")
    n = Vector(normal).normalized()
    c = Vector(loc)
    # Panel con su cara frontal a 6 cm del muro.
    c = c + n * 0.035
    if abs(n.y) > abs(n.x):
        size = (panel_w, 0.06, panel_h)
    else:
        size = (0.06, panel_w, panel_h)
    mb = vest.MeshBuilder(name)
    mb.add_box(tuple(c), size, panel_mat, bevel=0.006, segments=2)
    mb.build(col())
    text_sign(name + "_TEXT", text, tsize, tuple(c + n * 0.036), normal,
              text_mat, 0.003)
    if double_sided:
        text_sign(name + "_TEXT_B", text, tsize, tuple(c - n * 0.036),
                  tuple(-n), text_mat, 0.003)


def signage():
    dark = get_mat("M_WH_DarkMetal")
    green = get_mat("M_VEST_Emissive_Green")
    cool = get_mat("M_VEST_Emissive_Cool")
    red = get_mat("M_VEST_Red")
    paper = get_mat("M_VEST_Paper")

    wall_sign("WH_Sign_Main_SIGN", "ALMACÉN", 0.40,
              (72.0, 8.22, 3.50), (0, 1, 0), 4.20, 0.82, green, dark)
    wall_sign("WH_Sign_Supplies_SIGN", "SUMINISTROS", 0.30,
              (96.0, 37.78, 4.30), (0, -1, 0), 3.60, 0.78, green, dark)
    wall_sign("WH_Sign_Loading_SIGN", "CARGA / DESCARGA", 0.27,
              (70.22, 21.0, 4.05), (1, 0, 0), 4.00, 0.78, green, dark)
    wall_sign("WH_Sign_ExitEast_SIGN", "SALIDA", 0.18,
              (109.78, 12.0, 2.86), (-1, 0, 0), 1.20, 0.48, green, dark)
    wall_sign("WH_Sign_NoSmoke_SIGN", "NO FUMAR", 0.13,
              (84.0, 8.22, 2.62), (0, 1, 0), 1.05, 0.42, red, paper)
    # Señales colgadas de pasillo, con cadenas hasta el techo.
    for i, (x, label) in enumerate(((80.0, "PASILLO A"),
                                     (90.0, "PASILLO B"))):
        z = 3.78
        mb = vest.MeshBuilder("WH_Sign_Aisle%s_SIGN" % chr(65 + i))
        mb.add_box((x, 24.0, z), (1.35, 0.055, 0.52), dark, bevel=0.005)
        for dx in (-0.48, 0.48):
            mb.add_box((x + dx, 24.0, 4.83), (0.025, 0.025, 2.05),
                       get_mat("M_FM_Steel_Dark"), bevel=0.001)
        mb.build(col())
        text_sign("WH_Sign_Aisle%s_TEXT" % chr(65 + i), label, 0.15,
                  (x, 23.97, z), (0, -1, 0), green, 0.003)
        text_sign("WH_Sign_Aisle%s_TEXT_B" % chr(65 + i), label, 0.15,
                  (x, 24.03, z), (0, 1, 0), green, 0.003)

    # Etiquetas de extintor y alta tensión.
    mb = vest.MeshBuilder("WH_Labels_SIGN")
    ext_label = get_mat("M_FM_Label_Extintor")
    mb.add_plane((77.0, 8.24, 1.85), 0.42, 0.12, ext_label,
                 rot=(math.radians(-90), 0, 0))
    mb.add_plane((70.24, 29.0, 1.85), 0.12, 0.42, ext_label,
                 rot=(0, math.radians(90), 0))
    mb.add_plane((109.76, 30.0, 1.85), 0.12, 0.42, ext_label,
                 rot=(0, math.radians(-90), 0))
    mb.add_plane((70.18, 16.2, 2.55), 0.14, 0.55,
                 get_mat("M_FM_Label_AltaTension_2"),
                 rot=(0, math.radians(90), 0))
    mb.build(col())

    # Extintores físicos.
    mb = vest.MeshBuilder("WH_Extinguishers")
    redm = get_mat("M_FM_Extinguisher_Red", "M_VEST_Red")
    blackm = get_mat("M_WH_BlackRubber")
    steel = get_mat("M_WH_Galv")
    for x, y, rz in ((77.0, 8.38, 0.0), (70.40, 29.0, math.radians(90)),
                     (109.60, 30.0, math.radians(-90))):
        mb.add_cyl((x, y, 0.56), 0.090, 0.52, redm, axis="Z", segments=14)
        mb.add_cyl((x, y, 0.86), 0.040, 0.10, blackm, axis="Z", segments=10)
        mb.add_box((x, y, 0.92), (0.17, 0.06, 0.035), blackm, bevel=0.002)
        mb.add_box((x, y + 0.05, 0.70), (0.04, 0.10, 0.35), blackm,
                   bevel=0.002)
        mb.add_box((x, y, 0.30), (0.18, 0.12, 0.05), steel, bevel=0.002)
    mb.build(col())


# ---------------------------------------------------------------------------
# Suelo, props y narrativa
# ---------------------------------------------------------------------------


def floor_details():
    white = get_mat("M_WH_WhiteLine")
    yellow = get_mat("M_WH_Yellow")
    dark = get_mat("M_WH_DarkMetal")
    galv = get_mat("M_WH_Galv")

    # Líneas peatonales y de carretilla.
    mb = vest.MeshBuilder("WH_FloorLines_FLOOR_LINE")
    mb.add_plane((74.58, 22.9, 0.006), 0.075, 27.2, white)
    for x in (77.35, 80.05):
        mb.add_plane((x, 22.0, 0.007), 0.075, 25.6, yellow)
    # Paso de cebra en la puerta sur.
    for i in range(5):
        mb.add_plane((70.6 + i * 0.65, 9.35, 0.008), 0.42, 1.25, white)
    # Marco de staging.
    for z, sx, sy, cx, cy in ((0.009, 4.0, 0.07, 96.5, 29.0),
                              (0.009, 4.0, 0.07, 96.5, 32.0),
                              (0.009, 0.07, 3.0, 94.5, 30.5),
                              (0.009, 0.07, 3.0, 98.5, 30.5)):
        mb.add_plane((cx, cy, z), sx, sy, yellow)
    mb.build(col())

    mb = vest.MeshBuilder("WH_FloorArrows_FLOOR_LINE")
    shape = ((-0.075, -0.32), (0.075, -0.32), (0.075, 0.06),
             (-0.075, 0.06), (-0.22, 0.06), (0.22, 0.06), (0.0, 0.30))
    faces = ((0, 1, 2, 3), (3, 6, 4), (2, 5, 6))
    uvs = ([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)],
           [(0.0, 0.0), (0.5, 1.0), (0.0, 1.0)],
           [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)])
    for x, y, rz in ((72.0, 12.1, 0.0), (82.0, 23.0, 0.0),
                     (101.0, 20.0, math.radians(180))):
        rot = Matrix.Rotation(rz, 3, "Z")
        verts = [tuple(rot @ Vector((vx, vy, 0.0)) + Vector((x, y, 0.012)))
                 for vx, vy in shape]
        mb._append(white, verts, [list(f) for f in faces],
                   [list(uv) for uv in uvs])
    mb.build(col())

    # Rejillas de desagüe.
    mb = vest.MeshBuilder("WH_Drain_GRILLE")
    for x, y in ((80.0, 20.0), (96.0, 12.0), (86.0, 33.5)):
        mb.add_box((x, y, 0.012), (0.72, 0.72, 0.020), dark, bevel=0.002)
        for i in range(-3, 4):
            mb.add_box((x, y + i * 0.085, 0.024), (0.62, 0.030, 0.012),
                       galv, bevel=0.0)
    mb.build(col())

    # Charcos, aceite, papeles, film y palet roto.
    mb = vest.MeshBuilder("WH_Puddles_PUDDLE")
    puddle = get_mat("M_VEST_Puddle")
    for x, y, sx, sy, rz in ((74.3, 13.6, 1.35, 0.80, 0.2),
                             (82.0, 27.4, 1.10, 0.70, -0.3),
                             (101.2, 20.2, 1.55, 0.85, 0.4),
                             (75.7, 31.5, 1.25, 0.72, -0.1),
                             (97.2, 12.8, 0.95, 0.58, 0.5)):
        mb.add_plane((x, y, 0.004), sx, sy, puddle, rot=(0, 0, rz))
    mb.build(col())

    mb = vest.MeshBuilder("WH_Oil_DECAL")
    oil = get_mat("M_WH_Oil")
    for x, y, sx, sy, rz in ((79.8, 27.0, 1.0, 0.55, 0.2),
                             (73.0, 30.0, 0.8, 0.45, -0.5),
                             (100.0, 18.2, 0.75, 0.40, 0.0)):
        mb.add_plane((x, y, 0.005), sx, sy, oil, rot=(0, 0, rz))
    mb.build(col())

    mb = vest.MeshBuilder("WH_Papers_DECAL")
    paper = get_mat("M_VEST_Paper")
    for x, y, rz in ((82.8, 10.3, 0.3), (83.2, 10.6, -0.5), (86.2, 11.0, 1.2),
                     (90.2, 12.1, -0.8), (73.2, 9.8, 0.5), (75.0, 19.2, 1.4),
                     (99.8, 13.0, -0.2), (105.0, 10.0, 0.7)):
        mb.add_plane((x, y, 0.014), 0.21, 0.297, paper, rot=(0, 0, rz))
    mb.build(col())

    mb = vest.MeshBuilder("WH_FilmScraps_DECAL")
    film = get_mat("M_WH_Film")
    for x, y, sx, sy, rz in ((97.8, 31.4, 0.5, 0.35, 0.4),
                             (98.2, 13.0, 0.42, 0.30, -0.3),
                             (84.0, 12.0, 0.55, 0.32, 0.7),
                             (73.0, 28.0, 0.35, 0.25, 0.2)):
        mb.add_plane((x, y, 0.016), sx, sy, film, rot=(0, 0, rz))
    mb.build(col())

    mb = vest.MeshBuilder("WH_BrokenPallet_DECAL")
    wood = get_mat("M_FM_Wood_Detailed", "M_VEST_Cork")
    for i, (x, y, rz) in enumerate(((73.1, 12.6, 0.2), (73.4, 12.9, -0.5),
                                    (73.0, 13.2, 1.1), (73.6, 13.4, 0.7),
                                    (73.2, 13.7, -0.2))):
        mb.add_box((x, y, 0.035 + i * 0.004), (1.05, 0.12, 0.035), wood,
                   bevel=0.003, rot=(0, 0, rz))
    mb.build(col())

    mb = vest.MeshBuilder("WH_TireMarks_DECAL")
    tire = get_mat("M_WH_Oil")
    for i, (x, y, rz, ln) in enumerate(
            ((77.9, 17.0, 0.05, 4.0), (78.7, 17.2, 0.05, 3.6),
             (101.0, 20.8, 1.4, 5.0), (100.2, 21.0, 1.4, 4.5))):
        mb.add_plane((x, y, 0.011 + i * 0.003), 0.16, ln, tire,
                     rot=(0, 0, rz))
    mb.build(col())


def narrative():
    # Bulto cubierto y rastro de sangre en la esquina SE.
    mb = vest.MeshBuilder("WH_CoveredBundle")
    wood = get_mat("M_FM_Wood_Detailed", "M_VEST_Cork")
    dark = get_mat("M_WH_Tarp")
    steel = get_mat("M_WH_Galv")
    f = Frame(106.2, 9.25, math.radians(18))
    for sx in (-0.45, 0.0, 0.45):
        f.box(mb, sx, 0, 0.045, 0.10, 0.92, 0.09, wood, bevel=0.004)
    for dy in (-0.36, -0.12, 0.12, 0.36):
        f.box(mb, 0, dy, 0.115, 1.08, 0.16, 0.04, wood, bevel=0.003)
    f.box(mb, 0, 0, 0.30, 1.02, 0.52, 0.28, dark, bevel=0.050,
          segments=3)
    f.box(mb, -0.30, 0.02, 0.44, 0.46, 0.44, 0.18, dark, bevel=0.045,
          segments=3)
    f.box(mb, 0.28, -0.02, 0.40, 0.38, 0.46, 0.14, dark, bevel=0.040,
          segments=3)
    f.box(mb, 0.52, 0.30, 0.28, 0.34, 0.16, 0.10, dark, bevel=0.030,
          segments=2)
    f.box(mb, -0.52, -0.28, 0.20, 0.20, 0.16, 0.22, steel, bevel=0.006)
    mb.build(col())

    mb = vest.MeshBuilder("WH_BloodTrail_BLOOD")
    blood = get_mat("M_WH_Blood")
    for i in range(9):
        t = i / 8.0
        x = 109.35 + (106.4 - 109.35) * t
        y = 12.2 + (9.5 - 12.2) * t
        s = 0.18 + 0.14 * (1.0 - t)
        mb.add_plane((x + 0.06 * math.sin(i), y, 0.008),
                     s * 1.5, s, blood, rot=(0, 0, 0.4 + i * 0.2))
    mb.add_plane((104.85, 8.95, 0.009), 1.20, 0.72, blood,
                 rot=(0, 0, 0.3))
    mb.build(col())

    mb = vest.MeshBuilder("WH_Handprint_DECAL")
    hand = get_mat("M_REC03_DecalHand", "M_WH_Blood")
    mb.add_plane((105.2, 9.55, 0.012), 0.24, 0.30, hand,
                 rot=(0, 0, 0.8))
    mb.build(col())

    # Cajas y palets sueltos junto a la puerta sur (sin bloquear el vano).
    for i, (x, y, rz, z) in enumerate(((76.3, 10.2, 0.2, 0.0),
                                        (76.8, 10.5, -0.4, 0.0),
                                        (76.5, 10.3, 0.1, 0.31))):
        mb = vest.MeshBuilder("WH_ScatterBox_%02d" % (i + 1))
        cargo_box(mb, Frame(x, y, rz), 0, 0, z, 0.42, 0.36, 0.31)
        mb.build(col())


def shelf_unit(name, x, y, rz):
    f = Frame(x, y, rz)
    mb = vest.MeshBuilder(name)
    steel = get_mat("M_WH_Galv", "M_WH_DarkMetal")
    deck = get_mat("M_WH_RackDeck")
    tote_mat = get_mat("M_WH_ToteBlue")
    for sx in (-1, 1):
        for sy in (-1, 1):
            f.box(mb, sx * 0.50, sy * 0.22, 1.012, 0.04, 0.04, 2.0, steel,
                  bevel=0.003)
            f.box(mb, sx * 0.50, sy * 0.22, 0.012, 0.07, 0.07, 0.024,
                  get_mat("M_WH_BlackRubber"), bevel=0.002)
    for z in (0.30, 0.78, 1.26, 1.74):
        f.box(mb, 0, 0, z, 1.08, 0.50, 0.025, deck, bevel=0.003)
    tote(mb, f, 0.0, 0.0, 1.756, 0.50, 0.40, 0.30, tote_mat)
    cargo_box(mb, f, 0.0, 0.02, 0.316, 0.44, 0.36, 0.31)
    mb.build(col())


def pallet_prop(name, x, y, rz):
    f = Frame(x, y, rz)
    mb = vest.MeshBuilder(name)
    pallet(mb, f, 0, 0, 0.0)
    mb.build(col())


def props():
    shelf_unit("WH_Prop_Shelf_W_01", 70.50, 10.35, math.radians(90))
    shelf_unit("WH_Prop_Shelf_W_02", 70.50, 11.55, math.radians(90))
    shelf_unit("WH_Prop_Shelf_W_03", 70.50, 27.20, math.radians(90))
    copy_prop("PROP_Z10_SpillPallet", "WH_Prop_SpillPallet", 72.75, 30.0,
              0.0, rz=math.radians(4))
    copy_prop("PROP_Z10_Barrel_0", "WH_Prop_Barrel_01", 72.35, 29.75, 0.205,
              rz=math.radians(15))
    copy_prop("PROP_Z10_Barrel_0", "WH_Prop_Barrel_02", 73.20, 30.10, 0.205,
              rz=math.radians(-25))
    copy_prop("PROP_Z10_LargeCableDrum", "WH_Prop_CableDrum", 75.65, 32.0,
              0.0, rz=math.radians(20))
    copy_prop("PROP_Z10_StorageCart", "WH_Prop_StorageCart", 75.8, 15.7,
              0.0, rz=math.radians(90))
    copy_prop("PROP_Z10_WasteBin", "WH_Prop_WasteBin", 83.45, 10.25, 0.0,
              rz=math.radians(10))
    pallet_prop("WH_Prop_Pallet_01", 91.6, 11.0, math.radians(8))
    pallet_prop("WH_Prop_Pallet_02", 98.2, 12.2, math.radians(-12))
    for i, (x, y, z, rz) in enumerate(((91.3, 10.9, 0.127, 0.2),
                                        (91.8, 11.2, 0.127, -0.3),
                                        (98.0, 12.1, 0.127, 0.1),
                                        (98.5, 12.4, 0.127, 0.4))):
        copy_prop("PROP_Z10_Box_A0", "WH_Prop_Box_%02d" % (i + 1),
                  x, y, z, rz=rz)
    copy_prop("PROP_Z10_ToolCart", "WH_Prop_ToolCart", 82.0, 24.8, 0.0,
              rz=math.radians(-90))


# ---------------------------------------------------------------------------
# Ensamblado
# ---------------------------------------------------------------------------


def build():
    clean()
    materials()
    for i, cx in enumerate((81.4, 84.3, 87.2, 90.1, 93.0)):
        rack_bay("WH_Rack_N_%02d" % (i + 1), cx, 36.0, 0.0)
    for i, cy in enumerate((19.6, 22.6, 25.6)):
        rack_bay("WH_Rack_E_%02d" % (i + 1), 108.55, cy, math.radians(90))
    rack_labels()
    security_cage()
    forklift()
    conveyor()
    packing_station()
    staging_island()
    mezzanine()
    pallet_jack()
    toppled_cart()
    ceiling_services()
    wall_treatment()
    signage()
    floor_details()
    narrative()
    props()

    c = col()
    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons)
               for o in c.objects if o.type == "MESH")
    verts = sum(len(o.data.vertices) for o in c.objects if o.type == "MESH")
    print("WH_BUILD objects=%d verts=%d tris=%d" % (len(c.objects), verts, tris))
    for o in sorted(c.objects, key=lambda x: x.name):
        print("WH_OBJ", o.name,
              sum(len(p.vertices) - 2 for p in o.data.polygons)
              if o.type == "MESH" else 0)


if __name__ == "__main__":
    build()
