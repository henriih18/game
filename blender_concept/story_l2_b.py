"""FRECUENCIA MUERTA - NEXUS Nivel 2, detalle B.

AIRLOCK, ARCHIVO CIENTIFICO, SERVIDORES y SALA DE ANALISIS.
Crea la coleccion NEXUS_STORY_L2B y guarda FM_NEXUS_V05_level1_v90.blend.
No reconstruye nada: solo anade props, senalizacion y luces de apoyo.
"""

import bpy
import math
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
OUT = ROOT + "/FM_NEXUS_V05_level1_v90.blend"
PREFIX = "NEXUS_STORY_L2B_"
COLL_NAME = "NEXUS_STORY_L2B"
FLOOR = -13.65

SCENE = bpy.context.scene

coll = bpy.data.collections.get(COLL_NAME)
if coll is None:
    coll = bpy.data.collections.new(COLL_NAME)
    SCENE.collection.children.link(coll)

for ob in list(bpy.data.objects):
    if ob.name.startswith(PREFIX):
        bpy.data.objects.remove(ob, do_unlink=True)

old_air_cam = bpy.data.objects.get("NEXUS_V04_CAM_Airlock")
if old_air_cam is not None:
    bpy.data.objects.remove(old_air_cam, do_unlink=True)


def M(name):
    return bpy.data.materials.get(name)


def move(ob):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    coll.objects.link(ob)


def finish(ob, name, material, bevel=0.0):
    ob.name = PREFIX + name
    move(ob)
    mat = M(material)
    if mat is not None:
        ob.data.materials.append(mat)
    if bevel > 0.0:
        mod = ob.modifiers.new("bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = "ANGLE"
    return ob


def box(name, center, size, material, bevel=0.006, rotation=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    ob = bpy.context.active_object
    ob.scale = (size[0], size[1], size[2])
    if rotation is not None:
        ob.rotation_euler = rotation
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    b = bevel if min(size) > 0.03 else 0.0
    return finish(ob, name, material, b)


def cyl(name, center, radius, depth, material, axis="Z", verts=16, bevel=0.0):
    rot = (0, 0, 0)
    if axis == "X":
        rot = (0, math.pi / 2, 0)
    elif axis == "Y":
        rot = (math.pi / 2, 0, 0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius,
                                        depth=depth, location=center,
                                        rotation=rot)
    return finish(bpy.context.active_object, name, material, bevel)


def sphere(name, center, radius, material, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8,
                                         radius=radius, location=center)
    ob = bpy.context.active_object
    ob.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(ob, name, material)


def cone(name, center, r1, depth, material, r2=0.0, rotation=None, verts=12):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2,
                                    depth=depth, location=center,
                                    rotation=rotation or (0, 0, 0))
    return finish(bpy.context.active_object, name, material)


def torus(name, center, major, minor, material, rotation=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     major_segments=16, minor_segments=6,
                                     location=center,
                                     rotation=rotation or (0, 0, 0))
    return finish(bpy.context.active_object, name, material)


def beam(name, p1, p2, thickness, material, bevel=0.0):
    a, b = Vector(p1), Vector(p2)
    d = b - a
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(a + b) / 2)
    ob = bpy.context.active_object
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion = d.to_track_quat("Z", "Y")
    ob.scale = (thickness, thickness, d.length)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(ob, name, material, bevel)


def tube(name, p1, p2, radius, material, verts=10):
    a, b = Vector(p1), Vector(p2)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius,
                                        depth=d.length,
                                        location=(a + b) / 2)
    ob = bpy.context.active_object
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion = d.to_track_quat("Z", "Y")
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(ob, name, material)


def puddle(name, x, y, sx, sy, material="NEXUS_Blood_Dried", z=FLOOR + 0.012,
           rot=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.5,
                                        depth=0.01, location=(x, y, z),
                                        rotation=(0, 0, rot))
    ob = bpy.context.active_object
    ob.scale = (sx, sy, 1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(ob, name, material)


def sign(name, body, center, facing, width=1.8, height=0.42, size=0.19):
    """Placa vertical legible desde el lado hacia el que apunta `facing`."""
    f = Vector(facing).normalized()
    q = f.to_track_quat("Z", "Y")
    box(name + "_PLATE", center, (width, height, 0.05),
        "NEXUS_SignPlate", bevel=0.004, rotation=q.to_euler())
    bpy.ops.object.text_add(location=(Vector(center) + f * 0.045))
    ob = bpy.context.active_object
    ob.data.body = body
    ob.data.size = size
    ob.data.align_x = "CENTER"
    ob.data.align_y = "CENTER"
    ob.data.extrude = 0.003
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion = q
    return finish(ob, name + "_TEXT", "NEXUS_SignText")


def point(name, loc, energy, color=(1.0, 0.82, 0.62), radius=0.35):
    data = bpy.data.lights.new(PREFIX + name, "POINT")
    data.energy = energy
    data.color = color
    data.shadow_soft_size = radius
    ob = bpy.data.objects.new(PREFIX + name, data)
    ob.location = loc
    coll.objects.link(ob)
    return ob


def camera(name, loc, target, lens):
    data = bpy.data.cameras.get(name)
    if data is None:
        data = bpy.data.cameras.new(name)
    ob = bpy.data.objects.get(name)
    if ob is None:
        ob = bpy.data.objects.new(name, data)
        SCENE.collection.objects.link(ob)
    else:
        ob.data = data
    ob.location = loc
    direction = Vector(target) - Vector(loc)
    ob.rotation_mode = "XYZ"
    ob.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    data.lens = lens
    return ob


def bottle(name, x, y, z, height=0.22, radius=0.05,
           liquid="NEXUS_Toxic_Spill", cap="NEXUS_Dark_Metal"):
    cyl(name + "_GLASS", (x, y, z + height / 2), radius, height,
        "NEXUS_Glass", verts=10)
    cyl(name + "_LIQUID", (x, y, z + height * 0.45), radius * 0.74,
        height * 0.55, liquid, verts=10)
    cyl(name + "_CAP", (x, y, z + height + 0.015), radius * 0.62, 0.03,
        cap, verts=10)


def hazard_band(name, x, y, length, along="X", width=0.09,
                z=FLOOR + 0.012):
    n = max(2, int(length / 0.22))
    seg = length / n
    for i in range(n):
        if along == "X":
            c = (x - length / 2 + seg * (i + 0.5), y, z)
            s = (seg * 0.96, width, 0.012)
        else:
            c = (x, y - length / 2 + seg * (i + 0.5), z)
            s = (width, seg * 0.96, 0.012)
        box(name + "_%02d" % i, c, s,
            "NEXUS_Amber" if i % 2 == 0 else "NEXUS_Dark_Metal", bevel=0.0)


def handprint(name, x, y, z, normal="X"):
    if normal == "X":
        box(name + "_PALM", (x, y, z), (0.016, 0.10, 0.13),
            "NEXUS_Blood_Dark", bevel=0.0)
        for i, dy in enumerate((-0.045, -0.015, 0.015, 0.045)):
            box(name + "_FINGER_%d" % i, (x, y + dy, z + 0.115),
                (0.016, 0.022, 0.075 - abs(i - 1.5) * 0.012),
                "NEXUS_Blood_Dark", bevel=0.0)
    else:
        box(name + "_PALM", (x, y, z), (0.10, 0.016, 0.13),
            "NEXUS_Blood_Dark", bevel=0.0)
        for i, dx in enumerate((-0.045, -0.015, 0.015, 0.045)):
            box(name + "_FINGER_%d" % i, (x + dx, y, z + 0.115),
                (0.022, 0.016, 0.075 - abs(i - 1.5) * 0.012),
                "NEXUS_Blood_Dark", bevel=0.0)


def hazmat_suit(name, x, y, top_z, material="NEXUS_Clinical"):
    # Traje colgado de frente a la pared oeste; la pared queda en x-.
    box(name + "_TORSO", (x + 0.13, y, top_z - 0.56), (0.25, 0.48, 0.58),
        material)
    box(name + "_HOOD", (x + 0.13, y, top_z - 0.08), (0.30, 0.34, 0.30),
        material)
    box(name + "_VISOR", (x + 0.295, y, top_z - 0.08), (0.025, 0.22, 0.14),
        "NEXUS_ColdGlass", bevel=0.0)
    box(name + "_ARM_L", (x + 0.14, y - 0.31, top_z - 0.68),
        (0.18, 0.15, 0.52), material)
    box(name + "_ARM_R", (x + 0.14, y + 0.31, top_z - 0.68),
        (0.18, 0.15, 0.52), material)
    box(name + "_LEG_L", (x + 0.14, y - 0.13, top_z - 1.14),
        (0.20, 0.20, 0.72), material)
    box(name + "_LEG_R", (x + 0.14, y + 0.13, top_z - 1.14),
        (0.20, 0.20, 0.72), material)
    box(name + "_BOOT_L", (x + 0.16, y - 0.13, top_z - 1.53),
        (0.28, 0.20, 0.12), "NEXUS_Rubber")
    box(name + "_BOOT_R", (x + 0.16, y + 0.13, top_z - 1.53),
        (0.28, 0.20, 0.12), "NEXUS_Rubber")
    box(name + "_BELT", (x + 0.13, y, top_z - 0.82), (0.27, 0.50, 0.06),
        "NEXUS_Amber", bevel=0.0)


# ================================================================ AIRLOCK
# Ducha/descontaminacion de techo.
torus("AIR_DECON_RING", (0.0, -12.0, -10.28), 0.55, 0.035,
      "NEXUS_Steel")
point("AIR_RING_LIGHT", (0.0, -12.0, -10.48), 45.0,
      (0.62, 0.82, 1.0), 0.18)
for i, (dx, dy) in enumerate(((0.39, 0.39), (-0.39, 0.39),
                              (-0.39, -0.39), (0.39, -0.39))):
    cyl("AIR_NOZZLE_%d" % i, (dx, -12.0 + dy, -10.31), 0.035, 0.18,
        "NEXUS_Steel", verts=10)
    box("AIR_NOZZLE_TIP_%d" % i, (dx, -12.0 + dy, -10.405),
        (0.07, 0.07, 0.025), "NEXUS_Dark_Metal", bevel=0.0)
tube("AIR_CEIL_PIPE_W", (-1.82, -12.0, -10.27), (-0.55, -12.0, -10.27),
     0.038, "NEXUS_Steel")
tube("AIR_CEIL_PIPE_E", (1.82, -12.0, -10.27), (0.55, -12.0, -10.27),
     0.038, "NEXUS_Steel")
tube("AIR_CEIL_PIPE_N", (0.0, -10.18, -10.27), (0.0, -11.45, -10.27),
     0.030, "NEXUS_Steel")

# Drenaje central y agua de la ducha.
box("AIR_FLOOR_DRAIN", (0.0, -12.0, FLOOR + 0.014),
    (0.72, 0.72, 0.028), "NEXUS_GrillDark")
for i in range(5):
    box("AIR_DRAIN_SLOT_%d" % i, (0.0, -12.30 + i * 0.15, FLOOR + 0.031),
        (0.55, 0.035, 0.012), "NEXUS_Dark_Metal", bevel=0.0)
box("AIR_DRAIN_RIM", (0.0, -12.0, FLOOR + 0.016),
    (0.82, 0.82, 0.018), "NEXUS_Dark_Metal", bevel=0.0)
puddle("AIR_WET_0", 0.20, -12.15, 0.72, 0.42, "NEXUS_Water")
puddle("AIR_WET_1", 0.40, -11.60, 0.30, 0.18, "NEXUS_Water")
puddle("AIR_WET_2", 0.05, -11.10, 0.22, 0.14, "NEXUS_Water")
puddle("AIR_WET_3", -0.18, -10.62, 0.20, 0.11, "NEXUS_Water")

# Banco de descontaminacion y cepillo de botas.
box("AIR_BENCH_TOP", (0.55, -13.59, FLOOR + 0.44),
    (1.15, 0.40, 0.07), "NEXUS_Painted_Metal")
for i, (dx, dy) in enumerate(((-0.48, -0.14), (0.48, -0.14),
                              (-0.48, 0.14), (0.48, 0.14))):
    box("AIR_BENCH_LEG_%d" % i,
        (0.55 + dx, -13.59 + dy, FLOOR + 0.20),
        (0.05, 0.05, 0.40), "NEXUS_Dark_Metal")
box("AIR_BENCH_FOOT", (0.55, -13.40, FLOOR + 0.18),
    (1.0, 0.04, 0.05), "NEXUS_Dark_Metal")
box("AIR_BOOT_BRUSH", (1.35, -13.57, FLOOR + 0.035),
    (0.40, 0.48, 0.05), "NEXUS_Dark_Metal")
for i in range(4):
    box("AIR_BRUSH_BRISTLE_%d" % i,
        (1.35, -13.75 + i * 0.12, FLOOR + 0.065),
        (0.30, 0.035, 0.035), "NEXUS_Amber", bevel=0.0)
box("AIR_FOLDED_PPE", (0.42, -13.53, FLOOR + 0.50),
    (0.38, 0.28, 0.07), "NEXUS_Clinical")
box("AIR_FOLDED_MASK", (0.75, -13.53, FLOOR + 0.51),
    (0.13, 0.10, 0.045), "NEXUS_OffWhite")

# Ganchos y traje colgado en la pared oeste.
for i, y in enumerate((-12.95, -12.05)):
    cyl("AIR_SUIT_HOOK_%d" % i, (-1.82, y, -11.62), 0.035, 0.14,
        "NEXUS_Steel", axis="X", verts=10)
    box("AIR_HOOK_PLATE_%d" % i, (-1.84, y, -11.62),
        (0.03, 0.12, 0.18), "NEXUS_Dark_Metal", bevel=0.0)
hazmat_suit("AIR_SUIT", -1.64, -12.95, -11.96)
box("AIR_SUIT_HANGER", (-1.62, -12.95, -11.765), (0.05, 0.05, 0.32),
    "NEXUS_Dark_Metal")
box("AIR_APRON", (-1.76, -12.05, -12.45), (0.04, 0.48, 0.95),
    "NEXUS_Clinical")

# Panel de control de la esclusa.
box("AIR_PANEL", (1.20, -10.105, -11.35), (0.52, 0.08, 0.70),
    "NEXUS_Painted_Metal")
box("AIR_PANEL_SCREEN", (1.20, -10.055, -11.27), (0.35, 0.012, 0.24),
    "NEXUS_Screen", bevel=0.0)
box("AIR_PANEL_KEY_0", (1.06, -10.050, -11.52), (0.06, 0.012, 0.04),
    "NEXUS_Green", bevel=0.0)
box("AIR_PANEL_KEY_1", (1.20, -10.050, -11.52), (0.06, 0.012, 0.04),
    "NEXUS_Amber", bevel=0.0)
box("AIR_PANEL_KEY_2", (1.34, -10.050, -11.52), (0.06, 0.012, 0.04),
    "NEXUS_Red", bevel=0.0)
cyl("AIR_GAUGE", (1.48, -10.075, -11.18), 0.07, 0.03,
    "NEXUS_GaugeFace", axis="Y", verts=16)

sign("AIR_SIGN_MAIN", "ESCLUSA // DESCONTAMINACION",
     (0.0, -10.095, -10.36), (0, -1, 0),
     1.72, 0.30, 0.105)
sign("AIR_SIGN_DUCHA", "DUCHA DE EMERGENCIA",
     (0.0, -10.095, -11.00), (0, -1, 0),
     1.20, 0.24, 0.09)

# Cinta de peligro en el umbral.
hazard_band("AIR_THRESHOLD", 0.0, -10.48, 1.7, "X", 0.10)
hazard_band("AIR_DRAIN_HAZ_0", -0.60, -12.0, 0.55, "Y", 0.08)
hazard_band("AIR_DRAIN_HAZ_1", 0.60, -12.0, 0.55, "Y", 0.08)

# Senal de suelo mojado y cubo de limpieza.
box("AIR_WET_SIGN_L", (-1.12, -11.34, FLOOR + 0.32),
    (0.34, 0.025, 0.58), "NEXUS_Amber", rotation=(0.20, 0, 0))
box("AIR_WET_SIGN_R", (-1.12, -11.34, FLOOR + 0.32),
    (0.34, 0.025, 0.58), "NEXUS_Amber", rotation=(-0.20, 0, 0))
box("AIR_WET_SIGN_TOP", (-1.12, -11.34, FLOOR + 0.61),
    (0.34, 0.16, 0.06), "NEXUS_Dark_Metal")
cyl("AIR_BUCKET", (-1.55, -13.55, FLOOR + 0.20), 0.20, 0.38,
    "NEXUS_Amber")
cyl("AIR_BUCKET_WATER", (-1.55, -13.55, FLOOR + 0.36), 0.17, 0.03,
    "NEXUS_Water")
tube("AIR_MOP_HANDLE", (-1.55, -13.55, FLOOR + 0.35),
     (-1.35, -13.22, FLOOR + 1.32), 0.022, "NEXUS_Wood")
box("AIR_MOP_HEAD", (-1.34, -13.24, FLOOR + 0.06),
    (0.28, 0.18, 0.10), "NEXUS_OffWhite")

# Biocontenedor y tuberia de pared.
cyl("AIR_BIO_BIN", (1.46, -12.98, FLOOR + 0.28), 0.23, 0.56,
    "NEXUS_Amber")
cyl("AIR_BIO_BIN_LID", (1.46, -12.98, FLOOR + 0.59), 0.24, 0.06,
    "NEXUS_Red_Matte")
box("AIR_BIO_BIN_LABEL", (1.46, -13.22, FLOOR + 0.34),
    (0.20, 0.012, 0.18), "NEXUS_SignPlate", bevel=0.0)
tube("AIR_WALL_PIPE", (1.82, -12.90, FLOOR),
     (1.82, -12.90, -10.25), 0.035, "NEXUS_Steel")
cyl("AIR_WALL_VALVE", (1.78, -12.90, -11.55), 0.09, 0.05,
    "NEXUS_Rusted_Metal", axis="X", verts=12)
cyl("AIR_WALL_GAUGE", (1.70, -12.90, -11.25), 0.065, 0.035,
    "NEXUS_GaugeFace", axis="X", verts=16)

# ============================================================ ARCHIVO
# Archivadores planos contra la pared sur.
for i, x in enumerate((6.40, 7.55, 8.70, 9.85)):
    box("ARCH_FLAT_%d_BODY" % i, (x, -3.46, FLOOR + 0.44),
        (1.00, 0.68, 0.88), "NEXUS_Painted_Metal")
    box("ARCH_FLAT_%d_TOP" % i, (x, -3.46, FLOOR + 0.89),
        (1.04, 0.72, 0.04), "NEXUS_Dark_Metal")
    for j in range(4):
        box("ARCH_FLAT_%d_DRAWER_%d" % (i, j),
            (x, -3.108, FLOOR + 0.14 + j * 0.18),
            (0.88, 0.014, 0.15), "NEXUS_Painted_Metal", bevel=0.0)
        box("ARCH_FLAT_%d_HANDLE_%d" % (i, j),
            (x, -3.095, FLOOR + 0.14 + j * 0.18),
            (0.20, 0.02, 0.025), "NEXUS_Dark_Metal", bevel=0.0)
        box("ARCH_FLAT_%d_LABEL_%d" % (i, j),
            (x + 0.30, -3.095, FLOOR + 0.14 + j * 0.18),
            (0.20, 0.012, 0.055), "NEXUS_OffWhite", bevel=0.0)
    box("ARCH_FLAT_%d_SIGN" % i, (x, -3.095, FLOOR + 0.81),
        (0.50, 0.012, 0.08), "NEXUS_SignPlate", bevel=0.0)

# Mesa de consulta en el suroeste.
box("ARCH_DESK_TOP", (3.35, -3.40, FLOOR + 0.73),
    (1.65, 0.62, 0.07), "NEXUS_Wood")
for i, (dx, dy) in enumerate(((-0.72, -0.23), (0.72, -0.23),
                              (-0.72, 0.23), (0.72, 0.23))):
    box("ARCH_DESK_LEG_%d" % i,
        (3.35 + dx, -3.40 + dy, FLOOR + 0.36),
        (0.06, 0.06, 0.72), "NEXUS_Dark_Metal")
box("ARCH_DESK_PAPER_0", (3.10, -3.40, FLOOR + 0.775),
    (0.28, 0.38, 0.012), "NEXUS_OffWhite", bevel=0.0)
box("ARCH_DESK_PAPER_1", (3.48, -3.48, FLOOR + 0.776),
    (0.28, 0.38, 0.012), "NEXUS_OffWhite", bevel=0.0,
    rotation=(0, 0, 0.18))
box("ARCH_DESK_FOLDER", (3.88, -3.40, FLOOR + 0.78),
    (0.32, 0.24, 0.035), "NEXUS_Amber")
cyl("ARCH_LAMP_BASE", (4.02, -3.53, FLOOR + 0.76), 0.10, 0.025,
    "NEXUS_Dark_Metal", verts=16)
cyl("ARCH_LAMP_STEM", (4.02, -3.53, FLOOR + 0.93), 0.018, 0.34,
    "NEXUS_Dark_Metal", verts=10)
cone("ARCH_LAMP_SHADE", (4.02, -3.50, FLOOR + 1.11), 0.18, 0.14,
     "NEXUS_Green", r2=0.09)
point("ARCH_LAMP_LIGHT", (4.02, -3.46, FLOOR + 1.04), 24.0,
      (1.0, 0.72, 0.38), 0.25)

box("ARCH_DESK_CHAIR_SEAT", (3.35, -2.72, FLOOR + 0.46),
    (0.50, 0.50, 0.07), "NEXUS_Rug_Dark")
box("ARCH_DESK_CHAIR_BACK", (3.35, -2.48, FLOOR + 0.84),
    (0.50, 0.07, 0.70), "NEXUS_Rug_Dark")
for i, (dx, dy) in enumerate(((-0.20, -0.20), (0.20, -0.20),
                              (-0.20, 0.20), (0.20, 0.20))):
    box("ARCH_DESK_CHAIR_LEG_%d" % i,
        (3.35 + dx, -2.72 + dy, FLOOR + 0.22),
        (0.04, 0.04, 0.44), "NEXUS_Dark_Metal")

# Carro de archivo y cajas sobre las estanterias.
box("ARCH_CART_SHELF_0", (10.55, 0.92, FLOOR + 0.36),
    (0.82, 0.48, 0.05), "NEXUS_Painted_Metal")
box("ARCH_CART_SHELF_1", (10.55, 0.92, FLOOR + 0.78),
    (0.82, 0.48, 0.05), "NEXUS_Painted_Metal")
for i, (dx, dy) in enumerate(((-0.34, -0.19), (0.34, -0.19),
                              (-0.34, 0.19), (0.34, 0.19))):
    box("ARCH_CART_POST_%d" % i,
        (10.55 + dx, 0.92 + dy, FLOOR + 0.40),
        (0.035, 0.035, 0.80), "NEXUS_Dark_Metal")
    cyl("ARCH_CART_WHEEL_%d" % i,
        (10.55 + dx, 0.92 + dy, FLOOR + 0.07), 0.045, 0.035,
        "NEXUS_Rubber", axis="X", verts=10)
for i, dx in enumerate((-0.28, -0.09, 0.10, 0.28)):
    box("ARCH_CART_BINDER_%d" % i,
        (10.55 + dx, 0.92, FLOOR + 0.84),
        (0.16, 0.30, 0.035), "NEXUS_Amber" if i % 2 == 0
        else "NEXUS_Red_Matte", rotation=(0, 0, 0.12 * i))

for i, x in enumerate((2.40, 4.20, 6.00, 7.80, 9.60)):
    box("ARCH_TOPBOX_%d" % i, (x, 0.0, -11.20),
        (0.52, 0.42, 0.34), "NEXUS_Wood")
    box("ARCH_TOPBOX_%d_LABEL" % i, (x, -0.215, -11.20),
        (0.30, 0.012, 0.10), "NEXUS_OffWhite", bevel=0.0)
    box("ARCH_TOPBOX_%d_STRIPE" % i, (x, -0.221, -11.10),
        (0.30, 0.008, 0.025), "NEXUS_Red_Matte", bevel=0.0)

# Silla volcada y papeles.
box("ARCH_FALLEN_SEAT", (3.90, 1.25, FLOOR + 0.08),
    (0.52, 0.52, 0.08), "NEXUS_Rug_Dark", rotation=(0, 0, 0.65))
box("ARCH_FALLEN_BACK", (3.70, 1.63, FLOOR + 0.27),
    (0.52, 0.08, 0.55), "NEXUS_Rug_Dark",
    rotation=(0.55, 0, 0.65))
for i, (dx, dy) in enumerate(((-0.18, -0.18), (0.18, -0.18),
                              (-0.18, 0.18), (0.18, 0.18))):
    box("ARCH_FALLEN_LEG_%d" % i,
        (3.90 + dx, 1.25 + dy, FLOOR + 0.22),
        (0.045, 0.045, 0.28), "NEXUS_Dark_Metal",
        rotation=(0.5, 0, 0.65))

for i, (x, y, rot) in enumerate(((3.2, -1.95, 0.20), (4.4, -1.70, -0.30),
                                 (5.8, -2.35, 0.55), (6.9, -1.55, -0.15),
                                 (8.0, -2.20, 0.35), (9.2, -1.80, -0.50),
                                 (7.2, -3.05, 0.10), (11.0, -0.55, 0.80))):
    box("ARCH_PAPER_%d" % i, (x, y, FLOOR + 0.012),
        (0.22, 0.30, 0.008), "NEXUS_OffWhite", bevel=0.0,
        rotation=(0, 0, rot))
for i, (x, y, rot) in enumerate(((2.8, 0.95, 0.6), (4.9, -1.15, -0.4),
                                 (6.2, -1.05, 0.2), (8.9, -1.20, -0.7))):
    box("ARCH_BINDER_%d" % i, (x, y, FLOOR + 0.035),
        (0.28, 0.22, 0.045), "NEXUS_Amber" if i % 2 == 0
        else "NEXUS_Red_Matte", rotation=(0, 0, rot))

# Rastro de sangre desde el fondo de las estanterias hasta la puerta.
for i, (x, y, s, mat) in enumerate(((6.25, 2.55, 0.30, "NEXUS_Blood_Dark"),
                                    (5.45, 2.30, 0.24, "NEXUS_Blood_Dried"),
                                    (4.65, 2.05, 0.20, "NEXUS_Blood_Dark"),
                                    (3.85, 1.65, 0.18, "NEXUS_Blood_Dried"),
                                    (3.10, 1.18, 0.16, "NEXUS_Blood_Dark"),
                                    (2.48, 0.65, 0.14, "NEXUS_Blood_Dried"),
                                    (2.00, 0.60, 0.12, "NEXUS_Blood_Dark"),
                                    (1.72, -0.05, 0.11, "NEXUS_Blood_Dried"))):
    puddle("ARCH_BLOOD_TRAIL_%d" % i, x, y, s, s * 0.55, mat,
           z=FLOOR + 0.013, rot=0.35 * i)
box("ARCH_BLOOD_DRAG", (1.84, 0.50, FLOOR + 0.011),
    (0.45, 0.11, 0.010), "NEXUS_Blood_Dried", bevel=0.0,
    rotation=(0, 0, -0.70))
handprint("ARCH_HANDPRINT", 1.63, -1.18, -12.52, "X")

# Deshumidificador, cubo y gotera.
box("ARCH_DEHUM_BODY", (12.03, -1.00, FLOOR + 0.43),
    (0.54, 0.46, 0.86), "NEXUS_OffWhite")
box("ARCH_DEHUM_GRILL", (11.755, -1.00, FLOOR + 0.48),
    (0.012, 0.32, 0.38), "NEXUS_GrillDark", bevel=0.0)
box("ARCH_DEHUM_PANEL", (11.752, -1.00, FLOOR + 0.77),
    (0.012, 0.24, 0.12), "NEXUS_Screen", bevel=0.0)
for i, (dx, dy) in enumerate(((-0.20, -0.16), (0.20, -0.16),
                              (-0.20, 0.16), (0.20, 0.16))):
    cyl("ARCH_DEHUM_WHEEL_%d" % i,
        (12.03 + dx, -1.00 + dy, FLOOR + 0.06), 0.045, 0.03,
        "NEXUS_Rubber", axis="X", verts=10)
puddle("ARCH_DEHUM_PUDDLE", 12.02, -1.45, 0.28, 0.18, "NEXUS_Water")
cyl("ARCH_LEAK_BUCKET", (10.90, -3.33, FLOOR + 0.21), 0.18, 0.40,
    "NEXUS_Rusted_Metal")
cyl("ARCH_LEAK_WATER", (10.90, -3.33, FLOOR + 0.39), 0.155, 0.025,
    "NEXUS_Water")
puddle("ARCH_LEAK_STAIN", 10.65, -3.08, 0.55, 0.28, "NEXUS_Meltwater")

sign("ARCH_SIGN_MAIN", "ARCHIVO CIENTIFICO // CONFIDENCIAL",
     (8.0, -3.825, -10.95), (0, 1, 0),
     3.0, 0.34, 0.145)
sign("ARCH_SIGN_DOOR", "SOLO PERSONAL AUTORIZADO",
     (1.675, 0.0, -10.22), (1, 0, 0),
     1.90, 0.30, 0.115)
sign("ARCH_SIGN_FLAT", "CONSULTA // DOCUMENTACION",
     (4.15, -3.815, -10.95), (0, 1, 0),
     1.70, 0.26, 0.095)


# =========================================================== SERVIDORES
# Silla de operador.
box("SRV_CHAIR_SEAT", (7.00, -10.30, FLOOR + 0.46),
    (0.56, 0.54, 0.08), "NEXUS_Rug_Dark")
box("SRV_CHAIR_BACK", (7.00, -10.04, FLOOR + 0.84),
    (0.56, 0.08, 0.68), "NEXUS_Rug_Dark")
box("SRV_CHAIR_BASE", (7.00, -10.30, FLOOR + 0.30),
    (0.10, 0.10, 0.36), "NEXUS_Dark_Metal")
for i, (dx, dy) in enumerate(((-0.22, -0.16), (0.22, -0.16),
                              (-0.22, 0.16), (0.22, 0.16))):
    box("SRV_CHAIR_LEG_%d" % i,
        (7.00 + dx, -10.30 + dy, FLOOR + 0.09),
        (0.035, 0.035, 0.18), "NEXUS_Dark_Metal")
    sphere("SRV_CHAIR_WHEEL_%d" % i,
           (7.00 + dx, -10.30 + dy, FLOOR + 0.05), 0.045,
           "NEXUS_Rubber", scale=(1.0, 1.0, 0.55))

# Carro de diagnostico.
box("SRV_CART_TOP", (9.42, -9.18, FLOOR + 0.87),
    (0.86, 0.54, 0.06), "NEXUS_Painted_Metal")
box("SRV_CART_SHELF", (9.42, -9.18, FLOOR + 0.36),
    (0.80, 0.50, 0.05), "NEXUS_Painted_Metal")
for i, (dx, dy) in enumerate(((-0.35, -0.21), (0.35, -0.21),
                              (-0.35, 0.21), (0.35, 0.21))):
    box("SRV_CART_POST_%d" % i,
        (9.42 + dx, -9.18 + dy, FLOOR + 0.46),
        (0.035, 0.035, 0.86), "NEXUS_Dark_Metal")
    cyl("SRV_CART_WHEEL_%d" % i,
        (9.42 + dx, -9.18 + dy, FLOOR + 0.06), 0.045, 0.035,
        "NEXUS_Rubber", axis="X", verts=10)
box("SRV_CART_LAPTOP_BASE", (9.28, -9.18, FLOOR + 0.92),
    (0.36, 0.26, 0.025), "NEXUS_Dark_Metal")
box("SRV_CART_LAPTOP_SCREEN", (9.28, -9.05, FLOOR + 1.07),
    (0.36, 0.018, 0.28), "NEXUS_MonitorScreen",
    rotation=(-0.25, 0, 0))
box("SRV_CART_CASE", (9.70, -9.30, FLOOR + 0.92),
    (0.28, 0.18, 0.11), "NEXUS_Red_Matte")
box("SRV_CART_SPOOL", (9.70, -9.02, FLOOR + 0.92),
    (0.22, 0.22, 0.08), "NEXUS_Rubber")

# SAI en la pared este.
for k, y in enumerate((-8.95, -10.05)):
    box("SRV_UPS_%d_BODY" % k, (10.56, y, FLOOR + 0.91),
        (0.56, 0.72, 1.82), "NEXUS_Rack_Paint")
    box("SRV_UPS_%d_DOOR" % k, (10.272, y, FLOOR + 0.91),
        (0.018, 0.62, 1.62), "NEXUS_Painted_Metal", bevel=0.0)
    for i in range(5):
        box("SRV_UPS_%d_VENT_%d" % (k, i),
            (10.260, y, FLOOR + 0.44 + i * 0.10),
            (0.012, 0.40, 0.035), "NEXUS_GrillDark", bevel=0.0)
    box("SRV_UPS_%d_DISPLAY" % k, (10.258, y, FLOOR + 1.52),
        (0.012, 0.30, 0.14), "NEXUS_Screen", bevel=0.0)
    for i, dz in enumerate((0.0, 0.06, 0.12)):
        box("SRV_UPS_%d_LED_%d" % (k, i),
            (10.258, y + 0.23, FLOOR + 1.70 - dz),
            (0.012, 0.025, 0.018),
            "NEXUS_Green" if i == 0 else "NEXUS_Amber", bevel=0.0)
    box("SRV_UPS_%d_HANDLE" % k, (10.255, y - 0.23, FLOOR + 1.20),
        (0.035, 0.04, 0.30), "NEXUS_Dark_Metal", bevel=0.0)

# Baldosas tecnicas y mazos de cable.
for i, x in enumerate((6.05, 6.75, 7.45, 8.15, 8.85)):
    box("SRV_FLOOR_TILE_%d" % i, (x, -8.95, FLOOR + 0.012),
        (0.62, 0.62, 0.018), "NEXUS_GrillDark")
    box("SRV_FLOOR_TILE_%d_FRAME" % i, (x, -8.95, FLOOR + 0.007),
        (0.66, 0.66, 0.010), "NEXUS_Dark_Metal", bevel=0.0)
    for j in range(4):
        box("SRV_FLOOR_TILE_%d_SLOT_%d" % (i, j),
            (x, -9.18 + j * 0.15, FLOOR + 0.024),
            (0.50, 0.035, 0.008), "NEXUS_Dark_Metal", bevel=0.0)

for i, y in enumerate((-8.35, -8.50, -8.65)):
    tube("SRV_CABLE_%d" % i, (4.10, y, FLOOR + 0.04),
         (10.35, y, FLOOR + 0.04), 0.024, "NEXUS_Rubber")

# Puerta de rack abierta y discos en el suelo.
box("SRV_RACK_DOOR", (6.90, -7.84, FLOOR + 0.90),
    (0.56, 0.035, 1.76), "NEXUS_Rack_Paint",
    rotation=(0, 0, 0.18))
box("SRV_RACK_DOOR_HANDLE", (6.68, -7.78, FLOOR + 0.92),
    (0.035, 0.035, 0.24), "NEXUS_Dark_Metal")
for i, (x, y, rot) in enumerate(((6.15, -8.16, 0.30), (6.42, -8.10, -0.20),
                                 (6.69, -8.22, 0.55), (6.95, -8.08, -0.45))):
    box("SRV_DRIVE_%d" % i, (x, y, FLOOR + 0.035),
        (0.12, 0.18, 0.035), "NEXUS_Dark_Metal",
        rotation=(0, 0, rot))
    box("SRV_DRIVE_%d_LED" % i, (x + 0.02, y - 0.06, FLOOR + 0.054),
        (0.025, 0.012, 0.008), "NEXUS_Green", bevel=0.0)
box("SRV_BAD_PANEL", (8.50, -7.575, FLOOR + 1.30),
    (0.52, 0.018, 0.48), "NEXUS_Grime", bevel=0.0)
box("SRV_BAD_TAG", (8.50, -7.555, FLOOR + 1.13),
    (0.20, 0.012, 0.10), "NEXUS_Red_Matte", bevel=0.0)

# Botellas de supresion y extintor.
for i, x in enumerate((3.55, 4.15)):
    cyl("SRV_SUPP_CYL_%d" % i, (x, -12.95, FLOOR + 0.76),
        0.18, 1.52, "NEXUS_Extinguisher_Red")
    cyl("SRV_SUPP_TOP_%d" % i, (x, -12.95, FLOOR + 1.55),
        0.11, 0.08, "NEXUS_Dark_Metal")
    cyl("SRV_SUPP_VALVE_%d" % i, (x, -12.95, FLOOR + 1.62),
        0.045, 0.12, "NEXUS_Steel", verts=10)
    tube("SRV_SUPP_PIPE_%d" % i, (x, -12.95, FLOOR + 1.64),
         (x, -12.95, -10.10), 0.028, "NEXUS_Steel")
    box("SRV_SUPP_LABEL_%d" % i, (x, -13.13, FLOOR + 1.10),
        (0.22, 0.012, 0.16), "NEXUS_OffWhite", bevel=0.0)

cyl("SRV_EXT_BODY", (3.24, -12.25, FLOOR + 0.82), 0.11, 0.54,
    "NEXUS_Extinguisher_Red")
cyl("SRV_EXT_TOP", (3.24, -12.25, FLOOR + 1.11), 0.055, 0.10,
    "NEXUS_Dark_Metal", verts=10)
tube("SRV_EXT_HOSE", (3.24, -12.25, FLOOR + 1.13),
     (3.24, -12.00, FLOOR + 0.62), 0.016, "NEXUS_Rubber")
box("SRV_EXT_BRACKET", (3.14, -12.25, FLOOR + 0.90),
    (0.04, 0.26, 0.30), "NEXUS_Dark_Metal")

# Intercomunicador y senalizacion.
box("SRV_INTERCOM", (3.175, -11.80, FLOOR + 1.38),
    (0.07, 0.26, 0.38), "NEXUS_Painted_Metal")
box("SRV_INTERCOM_SCREEN", (3.135, -11.80, FLOOR + 1.44),
    (0.012, 0.18, 0.12), "NEXUS_Screen", bevel=0.0)
for i in range(3):
    box("SRV_INTERCOM_KEY_%d" % i,
        (3.135, -11.88 + i * 0.08, FLOOR + 1.24),
        (0.012, 0.045, 0.035), "NEXUS_Dark_Metal", bevel=0.0)

sign("SRV_SIGN_MAIN", "SERVIDORES // CLIMA CONTROLADO",
     (3.175, -10.0, -10.22), (1, 0, 0),
     2.10, 0.30, 0.115)
sign("SRV_SIGN_UPS", "UPS // NO DESCONECTAR",
     (10.835, -9.50, -10.30), (-1, 0, 0),
     1.50, 0.30, 0.105)
sign("SRV_SIGN_SUPP", "SUPRESION // NO BLOQUEAR",
     (3.85, -13.345, -10.90), (0, 1, 0),
     1.80, 0.28, 0.095)

hazard_band("SRV_UPS_HAZ", 10.15, -9.50, 1.50, "Y", 0.10)
hazard_band("SRV_RACK_HAZ", 7.00, -7.85, 4.80, "X", 0.07)


# ============================================================= ANALISIS
# Corregir asiento de los microscopios sobre la mesa B.
for i in range(3):
    for part in ("BASE", "BODY", "HEAD"):
        ob = bpy.data.objects.get("NEXUS_LAB_MORE_AN_MICRO_%s_%d" % (part, i))
        if ob is not None:
            ob.location.y = 21.05

# Cabina de bioseguridad en la pared norte.
box("AN_BSC_BASE", (10.80, 23.40, FLOOR + 0.42),
    (2.20, 0.80, 0.84), "NEXUS_Painted_Metal")
box("AN_BSC_BODY", (10.80, 23.40, FLOOR + 1.36),
    (2.20, 0.80, 1.04), "NEXUS_OffWhite")
box("AN_BSC_GLASS", (10.80, 23.00, FLOOR + 1.55),
    (2.02, 0.025, 0.62), "NEXUS_ColdGlass", bevel=0.0)
box("AN_BSC_SASH", (10.80, 23.04, FLOOR + 1.92),
    (2.04, 0.06, 0.10), "NEXUS_Dark_Metal")
box("AN_BSC_SHELF", (10.80, 23.35, FLOOR + 1.18),
    (1.98, 0.58, 0.05), "NEXUS_Steel")
box("AN_BSC_BACK", (10.80, 23.78, FLOOR + 1.42),
    (2.00, 0.03, 0.86), "NEXUS_Dark_Metal", bevel=0.0)
for i in range(4):
    box("AN_BSC_VENT_%d" % i,
        (10.05 + i * 0.48, 22.995, FLOOR + 0.88),
        (0.30, 0.012, 0.035), "NEXUS_GrillDark", bevel=0.0)
box("AN_BSC_PANEL", (9.78, 22.99, FLOOR + 1.42),
    (0.20, 0.012, 0.28), "NEXUS_Screen", bevel=0.0)
box("AN_BSC_TRAY", (10.80, 23.18, FLOOR + 1.23),
    (0.82, 0.34, 0.035), "NEXUS_Steel")
box("AN_BSC_BOTTLE", (10.55, 23.20, FLOOR + 1.30),
    (0.10, 0.10, 0.20), "NEXUS_Clinical")
point("AN_BSC_LIGHT", (10.80, 23.10, FLOOR + 1.75), 22.0,
      (0.55, 0.82, 1.0), 0.20)

# Centrifuga de suelo.
cyl("AN_CENT_BODY", (4.30, 19.90, FLOOR + 0.42), 0.36, 0.84,
    "NEXUS_OffWhite")
cyl("AN_CENT_LID", (4.30, 19.90, FLOOR + 0.86), 0.37, 0.10,
    "NEXUS_Steel")
cyl("AN_CENT_ROTOR", (4.30, 19.90, FLOOR + 0.93), 0.24, 0.05,
    "NEXUS_Dark_Metal")
box("AN_CENT_PANEL", (4.30, 19.55, FLOOR + 0.63),
    (0.42, 0.02, 0.20), "NEXUS_Screen", bevel=0.0)
for i in range(3):
    box("AN_CENT_KEY_%d" % i,
        (4.16 + i * 0.14, 19.55, FLOOR + 0.43),
        (0.075, 0.02, 0.035), "NEXUS_Dark_Metal", bevel=0.0)
cyl("AN_CENT_BASE", (4.30, 19.90, FLOOR + 0.06), 0.40, 0.06,
    "NEXUS_Dark_Metal")

# Carro central de muestras.
box("AN_CART_TOP", (9.42, 19.55, FLOOR + 0.87),
    (0.92, 0.56, 0.06), "NEXUS_Steel")
box("AN_CART_SHELF", (9.42, 19.55, FLOOR + 0.36),
    (0.86, 0.50, 0.05), "NEXUS_Painted_Metal")
for i, (dx, dy) in enumerate(((-0.38, -0.22), (0.38, -0.22),
                              (-0.38, 0.22), (0.38, 0.22))):
    box("AN_CART_POST_%d" % i,
        (9.42 + dx, 19.55 + dy, FLOOR + 0.46),
        (0.035, 0.035, 0.86), "NEXUS_Dark_Metal")
    cyl("AN_CART_WHEEL_%d" % i,
        (9.42 + dx, 19.55 + dy, FLOOR + 0.06), 0.045, 0.035,
        "NEXUS_Rubber", axis="X", verts=10)
box("AN_CART_CENTRIFUGE", (9.22, 19.55, FLOOR + 0.99),
    (0.28, 0.28, 0.20), "NEXUS_OffWhite")
cyl("AN_CART_ROTOR", (9.22, 19.55, FLOOR + 1.10), 0.11, 0.04,
    "NEXUS_Dark_Metal")
for i, y in enumerate((19.43, 19.53, 19.63, 19.73)):
    cyl("AN_CART_VIAL_%d" % i, (9.70, y, FLOOR + 0.99),
        0.022, 0.17, "NEXUS_Glass", verts=10)
    cyl("AN_CART_VIAL_LIQ_%d" % i, (9.70, y, FLOOR + 0.95),
        0.016, 0.07, "NEXUS_Toxic_Spill", verts=10)
box("AN_CART_PIPETTE", (9.42, 19.72, FLOOR + 0.92),
    (0.26, 0.08, 0.04), "NEXUS_Clinical")

# Nevera de muestras en la pared este.
box("AN_FRIDGE_BODY", (12.34, 17.02, FLOOR + 0.68),
    (0.56, 0.60, 1.32), "NEXUS_Clinical")
box("AN_FRIDGE_DOOR", (12.05, 17.02, FLOOR + 0.68),
    (0.025, 0.54, 1.18), "NEXUS_OffWhite", bevel=0.0)
box("AN_FRIDGE_DISPLAY", (12.03, 17.02, FLOOR + 1.14),
    (0.012, 0.22, 0.12), "NEXUS_Screen", bevel=0.0)
box("AN_FRIDGE_HANDLE", (12.02, 16.80, FLOOR + 0.76),
    (0.045, 0.035, 0.34), "NEXUS_Dark_Metal")
for i in range(3):
    box("AN_FRIDGE_VENT_%d" % i,
        (12.63, 17.02, FLOOR + 0.34 + i * 0.10),
        (0.012, 0.26, 0.035), "NEXUS_GrillDark", bevel=0.0)

# Banco de trabajo con reactivos y contenedor de cortantes.
box("AN_TABLEA_TRAY", (4.55, 18.02, FLOOR + 0.72),
    (0.46, 0.30, 0.05), "NEXUS_Steel")
for i, x in enumerate((4.42, 4.55, 4.68)):
    cyl("AN_TABLEA_VIAL_%d" % i, (x, 18.02, FLOOR + 0.82),
        0.026, 0.17, "NEXUS_Glass", verts=10)
    cyl("AN_TABLEA_VIAL_LIQ_%d" % i, (x, 18.02, FLOOR + 0.79),
        0.018, 0.07, "NEXUS_Green", verts=10)
box("AN_SHARPS", (4.18, 18.42, FLOOR + 0.79),
    (0.20, 0.20, 0.30), "NEXUS_Extinguisher_Red")
box("AN_SHARPS_LID", (4.18, 18.42, FLOOR + 0.95),
    (0.22, 0.22, 0.04), "NEXUS_Red_Matte")
box("AN_SHARPS_LABEL", (4.18, 18.31, FLOOR + 0.80),
    (0.14, 0.012, 0.10), "NEXUS_SignPlate", bevel=0.0)
box("AN_CLIPBOARD", (5.00, 18.30, FLOOR + 0.72),
    (0.24, 0.32, 0.018), "NEXUS_OffWhite", bevel=0.0,
    rotation=(0, 0, 0.15))

# Taburete caido y silla volcada.
box("AN_STOOL_SEAT", (4.95, 20.65, FLOOR + 0.45),
    (0.40, 0.40, 0.06), "NEXUS_Rug_Dark", rotation=(0.4, 0, 0.2))
for i, (dx, dy) in enumerate(((-0.15, -0.15), (0.15, -0.15),
                              (-0.15, 0.15), (0.15, 0.15))):
    cyl("AN_STOOL_LEG_%d" % i,
        (4.95 + dx, 20.65 + dy, FLOOR + 0.22), 0.025, 0.44,
        "NEXUS_Dark_Metal", verts=8)

box("AN_CHAIR_FALLEN_SEAT", (10.75, 18.95, FLOOR + 0.10),
    (0.52, 0.52, 0.08), "NEXUS_Rug_Dark", rotation=(0, 0, -0.55))
box("AN_CHAIR_FALLEN_BACK", (10.50, 19.30, FLOOR + 0.28),
    (0.52, 0.08, 0.55), "NEXUS_Rug_Dark",
    rotation=(-0.45, 0, -0.55))

# Derrame y material de absorcion.
puddle("AN_SPILL", 9.10, 20.15, 0.62, 0.38, "NEXUS_Toxic_Spill")
puddle("AN_SPILL_2", 8.76, 20.06, 0.18, 0.12, "NEXUS_Toxic_Spill")
box("AN_ABSORB_PAD", (9.35, 20.32, FLOOR + 0.018),
    (0.48, 0.36, 0.025), "NEXUS_OffWhite", bevel=0.0,
    rotation=(0, 0, 0.20))
for i, (x, y) in enumerate(((8.55, 20.45), (9.65, 20.45),
                            (8.55, 19.85), (9.65, 19.85))):
    box("AN_SPILL_HAZ_%d" % i, (x, y, FLOOR + 0.018),
        (0.18, 0.035, 0.012), "NEXUS_Amber", bevel=0.0,
        rotation=(0, 0, 0.78))
cyl("AN_BROKEN_VIAL", (8.92, 20.02, FLOOR + 0.06), 0.035, 0.12,
    "NEXUS_Glass", verts=10)
box("AN_VIAL_SHARD", (8.80, 20.12, FLOOR + 0.025),
    (0.08, 0.02, 0.012), "NEXUS_Glass", bevel=0.0,
    rotation=(0, 0, 0.6))

# Papeles, cafe y biocontenedor.
for i, (x, y, rot) in enumerate(((6.9, 22.28, 0.2), (7.3, 22.10, -0.3),
                                 (7.7, 22.32, 0.6), (10.2, 18.45, -0.1),
                                 (5.6, 19.92, 0.4))):
    box("AN_PAPER_%d" % i, (x, y, FLOOR + 0.012),
        (0.22, 0.30, 0.008), "NEXUS_OffWhite", bevel=0.0,
        rotation=(0, 0, rot))
puddle("AN_COFFEE", 7.15, 19.82, 0.26, 0.18, "NEXUS_Oil")
cyl("AN_COFFEE_CUP", (7.38, 19.86, FLOOR + 0.06), 0.045, 0.12,
    "NEXUS_OffWhite")
cyl("AN_BIO_BIN", (10.95, 16.62, FLOOR + 0.28), 0.23, 0.56,
    "NEXUS_Amber")
cyl("AN_BIO_BIN_LID", (10.95, 16.62, FLOOR + 0.59), 0.24, 0.06,
    "NEXUS_Red_Matte")

# Panel de protocolo en la pared norte.
box("AN_WALL_BOARD", (10.80, 23.825, -10.55),
    (1.62, 0.045, 0.82), "NEXUS_SignPlate")
for i, (dx, dz, w, h) in enumerate(((-0.42, 0.12, 0.34, 0.44),
                                    (0.02, 0.08, 0.26, 0.36),
                                    (0.36, 0.14, 0.30, 0.40))):
    box("AN_WALL_SHEET_%d" % i,
        (10.80 + dx, 23.795, -10.55 + dz),
        (w, 0.012, h), "NEXUS_OffWhite", bevel=0.0)
for i in range(3):
    box("AN_WALL_LINE_%d" % i,
        (10.80, 23.787, -10.34 + i * 0.10),
        (0.60, 0.006, 0.012), "NEXUS_Red_Matte", bevel=0.0)

sign("AN_SIGN_MAIN", "ANALISIS // MUESTRAS NIVEL 4",
     (8.0, 16.175, -10.22), (0, 1, 0),
     2.25, 0.32, 0.12)
sign("AN_SIGN_BSC", "BIOSEGURIDAD // NIVEL 3",
     (10.80, 23.795, -11.55), (0, -1, 0),
     1.55, 0.25, 0.09)
sign("AN_SIGN_FRIDGE", "REFRIGERADOR DE MUESTRAS",
     (12.835, 17.02, -11.90), (-1, 0, 0),
     1.55, 0.25, 0.085)

# Luz de tarea sobre la mesa B.
box("AN_TASK_LIGHT_BAR", (10.2, 21.1, -10.35),
    (1.40, 0.10, 0.06), "NEXUS_Dark_Metal")
for i, dx in enumerate((-0.62, 0.62)):
    tube("AN_TASK_LIGHT_HANG_%d" % i,
         (10.2 + dx, 21.1, -10.35), (10.2 + dx, 21.1, -9.62),
         0.012, "NEXUS_Dark_Metal")
point("AN_TASK_LIGHT", (10.2, 21.1, -10.30), 38.0,
      (1.0, 0.86, 0.64), 0.25)


# ---------------------------------------------------------------- cameras
# Encuadres de revision revisados en render. No afectan a la camara activa.
camera("NEXUS_V04_CAM_Airlock", (1.45, -13.25, -11.50),
       (-0.5, -10.7, -11.7), 12.0)
camera("NEXUS_V04_CAM_Archivo", (1.95, -1.20, -11.40),
       (10.4, -3.0, -11.35), 16.0)
camera("NEXUS_V04_CAM_Analisis", (3.60, 16.90, -11.55),
       (10.6, 21.0, -11.35), 16.0)

# ---------------------------------------------------------------- save
scene_objects = len(bpy.data.objects)
new_objects = len([o for o in bpy.data.objects if o.name.startswith(PREFIX)])
main_cam = bpy.data.objects.get("NEXUS_V05_CAM_Corridor")
if main_cam is not None:
    SCENE.camera = main_cam
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("SAVED", OUT)
print("NEW_OBJECTS", new_objects)
print("SCENE_OBJECTS", scene_objects)
print("CAMERA", SCENE.camera.name if SCENE.camera else None)
