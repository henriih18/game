"""FRECUENCIA MUERTA - NEXUS Nivel 2, detalle A.

NAVE, LAB_BIOLOGIA y LAB_QUIMICA.
Crea la coleccion NEXUS_STORY_L2A y guarda FM_NEXUS_V05_level1_v86.blend.
No reconstruye nada: solo anade props, senalizacion y luces de apoyo.
"""

import bpy
import math
from mathutils import Vector, Euler

ROOT = "/home/riyo/Documentos/game"
OUT = ROOT + "/FM_NEXUS_V05_level1_v86.blend"
PREFIX = "NEXUS_STORY_L2A_"
COLL_NAME = "NEXUS_STORY_L2A"
FLOOR = -13.65

SCENE = bpy.context.scene

coll = bpy.data.collections.get(COLL_NAME)
if coll is None:
    coll = bpy.data.collections.new(COLL_NAME)
    SCENE.collection.children.link(coll)

for ob in list(bpy.data.objects):
    if ob.name.startswith(PREFIX):
        bpy.data.objects.remove(ob, do_unlink=True)


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


def sign(name, body, center, rotation, width=1.8, height=0.42, size=0.19):
    rot = rotation
    box(name + "_PLATE", center, (width, height, 0.05),
        "NEXUS_SignPlate", bevel=0.004, rotation=rot)
    n = Euler(rot).to_matrix() @ Vector((0, 0, 1))
    bpy.ops.object.text_add(location=(Vector(center) + n * 0.045))
    ob = bpy.context.active_object
    ob.data.body = body
    ob.data.size = size
    ob.data.align_x = "CENTER"
    ob.data.align_y = "CENTER"
    ob.data.extrude = 0.003
    ob.rotation_euler = rot
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


def top_of(name, fallback):
    ob = bpy.data.objects.get(name)
    if ob is None:
        return fallback
    return max((ob.matrix_world @ Vector(c)).z for c in ob.bound_box)


# ---------------------------------------------------------------- NAVE fixes
top0 = bpy.data.objects.get("NEXUS_NAVE_DETAIL_TOP_0")
if top0 is not None and top0.data.materials:
    top0.data.materials[0] = M("NEXUS_Dark_Metal")
top1 = bpy.data.objects.get("NEXUS_NAVE_DETAIL_TOP_1")
if top1 is not None and top1.data.materials:
    top1.data.materials[0] = M("NEXUS_Painted_Metal")
spot = bpy.data.objects.get("NEXUS_V04_POLISH_TANK_SPOT")
if spot is not None and spot.type == "LIGHT":
    spot.data.energy = 1050

ring = bpy.data.objects.get("NEXUS_V04_NAVE_RING")
if ring is not None:
    ring.data.materials.clear()
    ring.data.materials.append(M("NEXUS_Dark_Metal"))
    span = max(ring.dimensions.x, ring.dimensions.y)
    if span > 5.35:
        factor = 5.32 / span
        ring.scale = (factor, factor, factor)
        bpy.context.view_layer.objects.active = ring
        for ob in bpy.context.selected_objects:
            ob.select_set(False)
        ring.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        ring.select_set(False)
    ring.location.z = -8.0

# ---------------------------- NAVE: barricada del tanque
cones = [(-7.4, 4.5), (-7.4, -0.5), (-14.0, 4.5), (-14.0, -0.5)]
for i, (x, y) in enumerate(cones):
    box("NAVE_CONE_BASE_%d" % i, (x, y, FLOOR + 0.03), (0.34, 0.34, 0.06),
        "NEXUS_Rubber")
    cone("NAVE_CONE_%d" % i, (x, y, FLOOR + 0.32), 0.17, 0.55, "NEXUS_Amber")
    cyl("NAVE_CONE_BAND_%d" % i, (x, y, FLOOR + 0.34), 0.115, 0.09,
        "NEXUS_OffWhite", verts=12)
beam("NAVE_TAPE_W", (-14.0, -0.5, FLOOR + 0.62),
     (-14.0, 4.5, FLOOR + 0.62), 0.025, "NEXUS_Amber")
beam("NAVE_TAPE_N", (-14.0, 4.5, FLOOR + 0.62),
     (-7.4, 4.5, FLOOR + 0.62), 0.025, "NEXUS_Amber")

# ---------------------------- NAVE: zona de carga norte
box("NAVE_PJ_BODY", (-5.0, 6.6, FLOOR + 0.32), (0.55, 0.6, 0.5),
    "NEXUS_Painted_Metal")
box("NAVE_PJ_FORK_0", (-5.9, 6.35, FLOOR + 0.1), (1.3, 0.14, 0.08),
    "NEXUS_Steel")
box("NAVE_PJ_FORK_1", (-5.9, 6.85, FLOOR + 0.1), (1.3, 0.14, 0.08),
    "NEXUS_Steel")
for i, y in enumerate((6.3, 6.9)):
    cyl("NAVE_PJ_WHEEL_%d" % i, (-4.85, y, FLOOR + 0.1), 0.1, 0.12,
        "NEXUS_Rubber", axis="Y")
beam("NAVE_PJ_HANDLE", (-4.8, 6.6, FLOOR + 0.55),
     (-4.15, 6.6, FLOOR + 1.35), 0.05, "NEXUS_Amber")
box("NAVE_PJ_GRIP", (-4.1, 6.6, FLOOR + 1.4), (0.3, 0.12, 0.1),
    "NEXUS_Rubber")

box("NAVE_WRAP_PALLET", (-10.6, 6.9, FLOOR + 0.07), (1.35, 1.05, 0.14),
    "NEXUS_Wood")
for i in range(2):
    z = FLOOR + 0.14 + 0.38 + i * 0.72
    box("NAVE_WRAP_BOX_%d" % i, (-10.6, 6.9, z), (1.0, 0.8, 0.7),
        "NEXUS_Debris", bevel=0.02)
for i, x in enumerate((-10.05, -11.15)):
    box("NAVE_WRAP_STRAP_%d" % i, (x, 6.9, FLOOR + 0.9),
        (0.05, 0.82, 1.45), "NEXUS_Amber", bevel=0.0)

for i, (x, y, s) in enumerate(((-8.3, 6.5, 0.9), (-8.35, 6.55, 0.8),
                               (-8.15, 6.75, 0.6))):
    box("NAVE_STACK_%d" % i, (x, y, FLOOR + s / 2 + i * 0.78),
        (s, s, s * 0.85), "NEXUS_Wood", bevel=0.02)
box("NAVE_TIPPED_CRATE", (-7.1, 7.7, FLOOR + 0.48), (0.85, 0.7, 0.8),
    "NEXUS_Wood", bevel=0.02, rotation=(0.12, 0.08, 0.4))
for i in range(3):
    box("NAVE_PACK_%d" % i, (-6.6 + i * 0.35, 8.15 - i * 0.1, FLOOR + 0.05),
        (0.28, 0.22, 0.08), "NEXUS_OffWhite", rotation=(0, 0, i * 0.4))

# estanteria caida contra la pared norte
box("NAVE_SHELF_BACK", (-5.6, 8.05, FLOOR + 0.06), (2.6, 2.0, 0.09),
    "NEXUS_Rack_Paint", rotation=(0, 0, 0.1))
for i, y in enumerate((7.4, 7.9, 8.4)):
    box("NAVE_SHELF_BOARD_%d" % i, (-5.6, y, FLOOR + 0.27),
        (2.5, 0.06, 0.5), "NEXUS_Rusted_Metal", rotation=(0, 0, 0.1))
for i in range(4):
    box("NAVE_SHELF_DEBRIS_%d" % i,
        (-6.4 + i * 0.5, 7.7 + (i % 2) * 0.4, FLOOR + 0.1),
        (0.3, 0.22, 0.16), "NEXUS_Debris", rotation=(0, 0, i * 0.5))

box("NAVE_LOCKBOX", (-2.35, 7.8, FLOOR + 0.28), (0.55, 0.45, 0.5),
    "NEXUS_Dark_Metal")
box("NAVE_LOCKBOX_LID", (-2.35, 7.65, FLOOR + 0.57), (0.55, 0.4, 0.06),
    "NEXUS_Dark_Metal", rotation=(0.5, 0, 0))
box("NAVE_LOCKBOX_HANDLE", (-2.35, 7.56, FLOOR + 0.38), (0.18, 0.04, 0.05),
    "NEXUS_Amber")

# ---------------------------- NAVE: tecnico y rastro
puddle("NAVE_BLOOD_POOL", -7.3, 1.1, 1.05, 0.78, "NEXUS_Blood_Dark", rot=0.3)
for i, (x, y, s) in enumerate(((-7.0, 1.15, 0.45), (-7.45, 1.35, 0.35),
                               (-7.85, 1.6, 0.4), (-8.15, 1.8, 0.3))):
    puddle("NAVE_BLOOD_TRAIL_%d" % i, x, y, s, s * 0.6, "NEXUS_Blood_Dried")
box("NAVE_BODY_TORSO", (-7.15, 1.15, FLOOR + 0.24), (0.55, 0.62, 0.3),
    "NEXUS_Jacket", rotation=(0, 0, 0.94))
sphere("NAVE_BODY_HEAD", (-7.6, 1.5, FLOOR + 0.24), 0.14, "NEXUS_Skin_Pale")
sphere("NAVE_BODY_HELMET", (-7.86, 1.28, FLOOR + 0.28), 0.19, "NEXUS_Amber",
       scale=(1, 1, 0.7))
for i, dx in enumerate((-0.18, 0.18)):
    beam("NAVE_BODY_LEG_%d" % i, (-6.8 + dx, 0.85, FLOOR + 0.18),
         (-6.3 + dx, 0.35, FLOOR + 0.12), 0.17, "NEXUS_Dark_Metal")
    box("NAVE_BODY_BOOT_%d" % i, (-6.25 + dx, 0.25, FLOOR + 0.1),
        (0.22, 0.34, 0.18), "NEXUS_Rubber")
beam("NAVE_BODY_ARM_0", (-7.35, 1.35, FLOOR + 0.3),
     (-8.0, 1.55, FLOOR + 0.1), 0.14, "NEXUS_Jacket")
box("NAVE_BODY_HAND_0", (-8.05, 1.57, FLOOR + 0.08), (0.12, 0.18, 0.1),
    "NEXUS_Skin_Pale")
beam("NAVE_BODY_ARM_1", (-6.95, 1.4, FLOOR + 0.3),
     (-6.6, 1.75, FLOOR + 0.1), 0.14, "NEXUS_Jacket")
box("NAVE_FLASHLIGHT", (-8.1, 1.75, FLOOR + 0.08), (0.1, 0.28, 0.1),
    "NEXUS_Dark_Metal", rotation=(0, 0, 0.55))
cyl("NAVE_FLASHLIGHT_LENS", (-8.22, 1.82, FLOOR + 0.08), 0.06, 0.04,
    "NEXUS_OffWhite", axis="Y")
point("NAVE_BODY_LIGHT", (-8.15, 1.7, FLOOR + 0.3), 35, (1.0, 0.75, 0.5), 0.2)
box("NAVE_TABLET", (-6.55, 0.62, FLOOR + 0.04), (0.28, 0.38, 0.025),
    "NEXUS_Dark_Metal", rotation=(0, 0, 0.7))
box("NAVE_TABLET_SCREEN", (-6.55, 0.62, FLOOR + 0.058), (0.2, 0.28, 0.01),
    "NEXUS_Screen", rotation=(0, 0, 0.7))

# ---------------------------- NAVE: cadena colgante
box("NAVE_CHAIN_PLATE", (-6.5, 1.5, -9.36), (0.42, 0.42, 0.08),
    "NEXUS_Dark_Metal")
for i in range(9):
    z = -9.5 - i * 0.14
    rot = (math.pi / 2, 0, 0) if i % 2 == 0 else (0, math.pi / 2, 0)
    torus("NAVE_CHAIN_LINK_%d" % i, (-6.5, 1.5, z), 0.07, 0.018,
          "NEXUS_Rusted_Metal", rotation=rot)
torus("NAVE_HOOK", (-6.5, 1.5, -10.92), 0.14, 0.022, "NEXUS_Rusted_Metal",
      rotation=(math.pi / 2, 0, 0))

# ---------------------------- NAVE: botin y lampara
desk_top = top_of("NEXUS_V04_DETAIL_CONTROL_DESK", -12.6)
box("NAVE_SPECIMEN_CASE", (-11.2, 0.0, desk_top + 0.16),
    (0.58, 0.38, 0.32), "NEXUS_Dark_Metal")
box("NAVE_SPECIMEN_GLASS", (-11.2, 0.0, desk_top + 0.33),
    (0.5, 0.3, 0.03), "NEXUS_Glass")
box("NAVE_SPECIMEN_LABEL", (-11.2, 0.2, desk_top + 0.17),
    (0.3, 0.02, 0.12), "NEXUS_Amber")

beam("NAVE_LAMP_LEG_0", (-13.2, 6.2, FLOOR + 0.02),
     (-13.2, 6.2, FLOOR + 1.55), 0.05, "NEXUS_Dark_Metal")
for i, (dx, dy) in enumerate(((0.35, 0.25), (-0.35, 0.25), (0, -0.4))):
    beam("NAVE_LAMP_FOOT_%d" % i, (-13.2, 6.2, FLOOR + 0.45),
         (-13.2 + dx, 6.2 + dy, FLOOR + 0.02), 0.04, "NEXUS_Dark_Metal")
box("NAVE_LAMP_HEAD", (-13.2, 6.2, FLOOR + 1.65), (0.42, 0.3, 0.28),
    "NEXUS_Painted_Metal")
box("NAVE_LAMP_FACE", (-13.2, 6.2, FLOOR + 1.52), (0.32, 0.22, 0.03),
    "NEXUS_OffWhite", rotation=(0.35, 0, 0))
point("NAVE_WORK_LIGHT", (-13.2, 6.2, FLOOR + 1.45), 65, (1.0, 0.86, 0.68), 0.25)

# ---------------------------- NAVE: senalizacion
sign("NAVE_SIGN_CARGA", "NAVE // CARGA", (-8.3, 8.94, -11.55),
     (math.pi / 2, 0, 0), 2.1, 0.46, 0.2)
sign("NAVE_SIGN_CONT", "CONTENCION // NO ACCESO", (-1.74, 4.9, -11.55),
     (math.pi / 2, 0, -math.pi / 2), 2.0, 0.42, 0.16)
for i, (dx, dy) in enumerate(((-2.55, 0), (2.55, 0), (0, 2.55))):
    cyl("NAVE_RING_CABLE_%d" % i, (-10.7 + dx, 2 + dy, -7.41),
        0.018, 1.18, "NEXUS_Dark_Metal", verts=8)

print("NAVE detail listo")

# ---------------------------------------------------------------- BIOLOGIA
TOP = FLOOR + 0.8
box("BIO_ISLAND_BASE", (-10.2, -11.4, FLOOR + 0.36), (3.2, 1.2, 0.72),
    "NEXUS_Painted_Metal")
box("BIO_ISLAND_TOP", (-10.2, -11.4, FLOOR + 0.76), (3.4, 1.4, 0.08),
    "NEXUS_Clinical")
for i, x in enumerate((-11.2, -10.2, -9.2)):
    box("BIO_ISLAND_DOOR_%d" % i, (x, -12.02, FLOOR + 0.36),
        (0.85, 0.03, 0.62), "NEXUS_OffWhite")
    box("BIO_ISLAND_HANDLE_%d" % i, (x + 0.32, -12.05, FLOOR + 0.5),
        (0.04, 0.03, 0.12), "NEXUS_Dark_Metal")
box("BIO_SINK", (-11.15, -11.4, FLOOR + 0.78), (0.62, 0.46, 0.08),
    "NEXUS_Dark_Metal")
box("BIO_SINK_WATER", (-11.15, -11.4, FLOOR + 0.795), (0.5, 0.34, 0.02),
    "NEXUS_Water")
tube("BIO_FAUCET", (-11.56, -11.4, FLOOR + 0.8),
     (-11.56, -11.4, FLOOR + 1.18), 0.025, "NEXUS_Steel")
beam("BIO_FAUCET_ARM", (-11.56, -11.4, FLOOR + 1.16),
     (-11.25, -11.4, FLOOR + 1.16), 0.04, "NEXUS_Steel")
tube("BIO_FAUCET_TIP", (-11.25, -11.4, FLOOR + 1.16),
     (-11.25, -11.4, FLOOR + 1.02), 0.022, "NEXUS_Steel")

box("BIO_MICRO_BASE", (-9.0, -11.55, FLOOR + 0.83), (0.26, 0.3, 0.05),
    "NEXUS_Dark_Metal")
box("BIO_MICRO_ARM", (-9.1, -11.55, FLOOR + 1.02), (0.08, 0.1, 0.34),
    "NEXUS_Dark_Metal")
box("BIO_MICRO_STAGE", (-8.98, -11.55, FLOOR + 0.94), (0.24, 0.22, 0.03),
    "NEXUS_Steel")
cyl("BIO_MICRO_TUBE", (-8.98, -11.55, FLOOR + 1.2), 0.045, 0.16,
    "NEXUS_Steel")
cyl("BIO_MICRO_LENS", (-8.98, -11.55, FLOOR + 1.29), 0.055, 0.04,
    "NEXUS_Dark_Metal")
cyl("BIO_MICRO_OBJ", (-8.98, -11.55, FLOOR + 1.09), 0.035, 0.1,
    "NEXUS_Dark_Metal")

cyl("BIO_CENTRIFUGE", (-9.85, -12.0, FLOOR + 0.95), 0.22, 0.28,
    "NEXUS_OffWhite", verts=20)
cyl("BIO_CENTRIFUGE_LID", (-9.85, -12.0, FLOOR + 1.1), 0.2, 0.05,
    "NEXUS_Clinical", verts=20)
box("BIO_CENTRIFUGE_KNOB", (-9.65, -12.0, FLOOR + 1.0), (0.05, 0.08, 0.04),
    "NEXUS_Amber")
box("BIO_RACK", (-10.5, -11.0, FLOOR + 0.84), (0.36, 0.22, 0.08),
    "NEXUS_Dark_Metal")
for i in range(6):
    x = -10.65 + i * 0.06
    cyl("BIO_VIAL_%d" % i, (x, -11.0, FLOOR + 0.95), 0.018, 0.16,
        "NEXUS_Glass", verts=8)
    cyl("BIO_VIAL_CAP_%d" % i, (x, -11.0, FLOOR + 1.04), 0.022, 0.035,
        ("NEXUS_Amber", "NEXUS_Green", "NEXUS_Blood_Dark")[i % 3], verts=8)
box("BIO_TRAY", (-9.45, -11.15, FLOOR + 0.83), (0.42, 0.3, 0.04),
    "NEXUS_Steel")
box("BIO_TRAY_ITEM", (-9.5, -11.15, FLOOR + 0.87), (0.18, 0.12, 0.05),
    "NEXUS_Clinical")

for i, (x, y) in enumerate(((-11.7, -10.0), (-8.75, -12.65))):
    cyl("BIO_STOOL_SEAT_%d" % i, (x, y, FLOOR + 0.6), 0.3, 0.06,
        "NEXUS_Rubber", verts=20)
    tube("BIO_STOOL_POLE_%d" % i, (x, y, FLOOR + 0.03), (x, y, FLOOR + 0.58),
         0.045, "NEXUS_Steel")
    cyl("BIO_STOOL_BASE_%d" % i, (x, y, FLOOR + 0.03), 0.22, 0.05,
        "NEXUS_Steel", verts=16)
point("BIO_ISLAND_LIGHT", (-10.2, -11.4, FLOOR + 1.9), 40,
      (0.82, 0.9, 1.0), 0.3)

# decontaminacion junto a la puerta este
tube("BIO_SHOWER_PIPE", (-3.3, -10.3, FLOOR), (-3.3, -10.3, FLOOR + 2.7),
     0.055, "NEXUS_Steel")
beam("BIO_SHOWER_ARM", (-3.3, -10.3, FLOOR + 2.68),
     (-3.62, -10.3, FLOOR + 2.68), 0.055, "NEXUS_Steel")
cyl("BIO_SHOWER_HEAD", (-3.62, -10.3, FLOOR + 2.64), 0.18, 0.05,
    "NEXUS_Steel", verts=16)
tube("BIO_SHOWER_CHAIN", (-3.28, -10.3, FLOOR + 2.1),
     (-3.28, -10.3, FLOOR + 1.1), 0.012, "NEXUS_Dark_Metal")
box("BIO_SHOWER_HANDLE", (-3.28, -10.3, FLOOR + 1.06), (0.06, 0.1, 0.18),
    "NEXUS_Amber")
box("BIO_SHOWER_GRATE", (-3.85, -10.3, FLOOR + 0.02), (0.9, 0.9, 0.04),
    "NEXUS_GrillDark")
for i in range(5):
    box("BIO_SHOWER_SLAT_%d" % i, (-3.85, -10.62 + i * 0.16, FLOOR + 0.045),
        (0.78, 0.04, 0.02), "NEXUS_Dark_Metal")
box("BIO_DECON_MAT", (-3.7, -11.25, FLOOR + 0.012), (0.8, 0.7, 0.02),
    "NEXUS_Amber")

box("BIO_EYE_BASIN", (-3.4, -9.5, FLOOR + 0.95), (0.45, 0.38, 0.12),
    "NEXUS_Steel")
tube("BIO_EYE_NOZ_0", (-3.5, -9.58, FLOOR + 1.0),
     (-3.5, -9.58, FLOOR + 1.16), 0.02, "NEXUS_Steel")
tube("BIO_EYE_NOZ_1", (-3.5, -9.42, FLOOR + 1.0),
     (-3.5, -9.42, FLOOR + 1.16), 0.02, "NEXUS_Steel")
box("BIO_EYE_PEDAL", (-3.5, -9.5, FLOOR + 0.03), (0.3, 0.18, 0.04),
    "NEXUS_Rubber")

for i, (x, y, s) in enumerate(((-3.95, -13.95, 0.58), (-4.6, -14.55, 0.5))):
    box("BIO_BIN_%d" % i, (x, y, FLOOR + s / 2 + 0.04), (s, s, s * 1.15),
        "NEXUS_Amber")
    box("BIO_BIN_LID_%d" % i, (x, y, FLOOR + s * 1.15 + 0.06), (s + 0.04, s + 0.04, 0.06),
        "NEXUS_Dark_Metal")
    box("BIO_BIN_LABEL_%d" % i, (x, y - s / 2 - 0.015, FLOOR + s * 0.7),
        (s * 0.5, 0.02, s * 0.25), "NEXUS_OffWhite")

# pared oeste: nevera y estanteria de muestras
box("BIO_FRIDGE", (-16.55, -12.0, FLOOR + 0.95), (0.72, 1.0, 1.9),
    "NEXUS_Clinical")
box("BIO_FRIDGE_GLASS", (-16.17, -12.0, FLOOR + 1.0), (0.03, 0.82, 1.5),
    "NEXUS_ColdGlass")
box("BIO_FRIDGE_HANDLE", (-16.13, -11.72, FLOOR + 1.0), (0.04, 0.05, 0.7),
    "NEXUS_Steel")
box("BIO_SHELF_BACK", (-16.68, -14.7, FLOOR + 0.9), (0.05, 1.3, 1.8),
    "NEXUS_Rack_Paint")
for i, z in enumerate((0.15, 0.65, 1.15, 1.6)):
    box("BIO_SHELF_BOARD_%d" % i, (-16.55, -14.7, FLOOR + z),
        (0.32, 1.28, 0.04), "NEXUS_Rusted_Metal")
for i in range(5):
    box("BIO_SAMPLE_BOX_%d" % i,
        (-16.52, -15.1 + i * 0.2, FLOOR + 1.2),
        (0.22, 0.16, 0.14), "NEXUS_OffWhite",
        rotation=(0, 0, (i % 2) * 0.15))

# vitrina de muestras en la pared norte
CAB_Y = -7.30
box("BIO_CAB_BACK", (-10.2, -7.16, FLOOR + 2.3), (2.8, 0.04, 1.0),
    "NEXUS_OffWhite")
for i, x in enumerate((-11.57, -8.83)):
    box("BIO_CAB_SIDE_%d" % i, (x, CAB_Y, FLOOR + 2.3), (0.06, 0.28, 1.0),
        "NEXUS_Painted_Metal")
box("BIO_CAB_TOP", (-10.2, CAB_Y, FLOOR + 2.78), (2.8, 0.28, 0.06),
    "NEXUS_Painted_Metal")
box("BIO_CAB_BOTTOM", (-10.2, CAB_Y, FLOOR + 1.82), (2.8, 0.28, 0.06),
    "NEXUS_Painted_Metal")
for i, z in enumerate((FLOOR + 2.06, FLOOR + 2.36, FLOOR + 2.66)):
    box("BIO_CAB_SHELF_%d" % i, (-10.2, CAB_Y, z), (2.68, 0.24, 0.03),
        "NEXUS_Steel")
    for j, (dx, mat) in enumerate(((-0.72, "NEXUS_Green"),
                                   (-0.38, "NEXUS_Amber"),
                                   (0.02, "NEXUS_Toxic_Spill"),
                                   (0.44, "NEXUS_Blood_Dark"))):
        cyl("BIO_CAB_BOTTLE_%d_%d" % (i, j), (-10.2 + dx, -7.30, z + 0.11),
            0.055, 0.2, "NEXUS_Glass", verts=10)
        cyl("BIO_CAB_LIQUID_%d_%d" % (i, j), (-10.2 + dx, -7.30, z + 0.075),
            0.04, 0.12, mat, verts=10)
        cyl("BIO_CAB_CAP_%d_%d" % (i, j), (-10.2 + dx, -7.30, z + 0.22),
            0.03, 0.03, "NEXUS_Dark_Metal", verts=10)
box("BIO_CAB_GLASS", (-10.2, -7.445, FLOOR + 2.3), (2.68, 0.012, 0.9),
    "NEXUS_Glass")
box("BIO_CAB_HANDLE", (-8.95, -7.46, FLOOR + 2.3), (0.03, 0.03, 0.28),
    "NEXUS_Dark_Metal")

# puesto de preparacion en el banco norte
BOFF = FLOOR + 0.81
box("BIO_BENCH_CENTRIFUGE", (-11.25, -8.2, BOFF + 0.15), (0.46, 0.4, 0.3),
    "NEXUS_Clinical")
box("BIO_BENCH_CENTRIFUGE_LID", (-11.25, -8.2, BOFF + 0.31), (0.4, 0.34, 0.03),
    "NEXUS_Dark_Metal")
box("BIO_BENCH_CENTRIFUGE_PANEL", (-11.25, -8.405, BOFF + 0.18),
    (0.18, 0.012, 0.06), "NEXUS_MonitorScreen")
box("BIO_BENCH_RACK", (-10.25, -8.2, BOFF + 0.04), (0.5, 0.22, 0.05),
    "NEXUS_Steel")
for i in range(5):
    cyl("BIO_BENCH_VIAL_%d" % i, (-10.47 + i * 0.11, -8.2, BOFF + 0.15),
        0.022, 0.18, "NEXUS_Glass", verts=8)
box("BIO_BENCH_TRAY", (-9.25, -8.22, BOFF + 0.03), (0.7, 0.4, 0.04),
    "NEXUS_Steel")
for i, (dx, mat) in enumerate(((-0.18, "NEXUS_Green"), (0.0, "NEXUS_Amber"),
                               (0.18, "NEXUS_OffWhite"))):
    cyl("BIO_BENCH_BOTTLE_%d" % i, (-9.25 + dx, -8.22, BOFF + 0.13),
        0.05, 0.18, mat, verts=10)
box("BIO_BENCH_CLIPBOARD", (-8.55, -8.05, BOFF + 0.02), (0.3, 0.38, 0.015),
    "NEXUS_OffWhite", rotation=(0, 0, 0.18))

# rastros
box("BIO_FALLEN_TRAY", (-9.4, -9.55, FLOOR + 0.065), (0.5, 0.36, 0.05),
    "NEXUS_Steel", rotation=(0.08, 0.12, 0.4))
for i in range(4):
    cyl("BIO_FALLEN_VIAL_%d" % i,
        (-9.7 + i * 0.17, -9.4 - (i % 2) * 0.18, FLOOR + 0.045),
        0.024, 0.15, "NEXUS_Glass", axis="X", verts=8)
box("BIO_GLOVE", (-7.35, -9.5, FLOOR + 0.015), (0.14, 0.26, 0.025),
    "NEXUS_Clinical", rotation=(0, 0, 0.5))
for i in range(4):
    box("BIO_GLOVE_FINGER_%d" % i,
        (-7.5 + i * 0.04, -9.64 - i * 0.015, FLOOR + 0.02),
        (0.025, 0.1, 0.015), "NEXUS_Clinical", rotation=(0, 0, 0.5))
for i in range(3):
    box("BIO_PAPER_%d" % i, (-14.6 + i * 0.18, -10.2 - i * 0.12, FLOOR + 0.01),
        (0.24, 0.32, 0.008), "NEXUS_OffWhite", rotation=(0, 0, i * 0.6))

box("BIO_HANDPRINT", (-14.4, -14.63, FLOOR + 1.35), (0.13, 0.015, 0.17),
    "NEXUS_Blood_Dark")
for i in range(4):
    box("BIO_HANDPRINT_FINGER_%d" % i,
        (-14.47 + i * 0.045, -14.63, FLOOR + 1.48), (0.025, 0.012, 0.09),
        "NEXUS_Blood_Dark")

beam("BIO_ARM", (-7.8, -13.45, FLOOR + 0.07), (-7.25, -13.0, FLOOR + 0.07),
     0.12, "NEXUS_Skin_Pale")
box("BIO_ARM_HAND", (-7.16, -12.95, FLOOR + 0.07), (0.16, 0.11, 0.07),
    "NEXUS_Skin_Pale", rotation=(0, 0, 0.7))
puddle("BIO_ARM_BLOOD", -7.5, -13.3, 0.55, 0.4, "NEXUS_Blood_Dark")
for i, (x, y, s) in enumerate(((-7.9, -13.55, 0.4), (-7.6, -13.0, 0.3),
                               (-7.25, -12.45, 0.28), (-6.85, -12.0, 0.22),
                               (-6.4, -11.65, 0.18))):
    puddle("BIO_DRAG_%d" % i, x, y, s, s * 0.55, "NEXUS_Blood_Dried")

sign("BIO_SIGN_DECON", "BIO // DECONTAMINACION", (-3.07, -10.3, -10.55),
     (math.pi / 2, 0, -math.pi / 2), 1.9, 0.4, 0.15)
sign("BIO_SIGN_TRAJE", "PROHIBIDO SIN TRAJE", (-3.07, -13.4, -11.35),
     (math.pi / 2, 0, -math.pi / 2), 1.6, 0.36, 0.13)
sign("BIO_SIGN_MUESTRAS", "MUESTRAS // NIVEL 3", (-16.93, -12.3, -11.35),
     (math.pi / 2, 0, math.pi / 2), 1.8, 0.4, 0.15)

print("BIOLOGIA detail listo")

# ---------------------------------------------------------------- QUIMICA
box("CHEM_ISLAND_BASE", (-11.5, 19.0, FLOOR + 0.36), (1.3, 3.4, 0.72),
    "NEXUS_Painted_Metal")
box("CHEM_ISLAND_TOP", (-11.5, 19.0, FLOOR + 0.76), (1.5, 3.6, 0.08),
    "NEXUS_Clinical")
for i, y in enumerate((17.7, 18.9)):
    box("CHEM_SINK_%d" % i, (-11.5, y, FLOOR + 0.78), (0.56, 0.5, 0.08),
        "NEXUS_Dark_Metal")
    box("CHEM_SINK_WATER_%d" % i, (-11.5, y, FLOOR + 0.795),
        (0.44, 0.38, 0.02), "NEXUS_Water")
    tube("CHEM_FAUCET_%d" % i, (-11.95, y, FLOOR + 0.8),
         (-11.95, y, FLOOR + 1.15), 0.024, "NEXUS_Steel")
    beam("CHEM_FAUCET_ARM_%d" % i, (-11.95, y, FLOOR + 1.13),
         (-11.68, y, FLOOR + 1.13), 0.038, "NEXUS_Steel")
    tube("CHEM_FAUCET_TIP_%d" % i, (-11.68, y, FLOOR + 1.13),
         (-11.68, y, FLOOR + 1.0), 0.02, "NEXUS_Steel")
for i in range(2):
    box("CHEM_ISLAND_DOOR_%d" % i, (-10.83, 18.1 + i * 0.9, FLOOR + 0.36),
        (0.03, 0.8, 0.62), "NEXUS_OffWhite")

box("CHEM_REAGENT_RACK", (-11.5, 20.35, FLOOR + 0.86), (0.8, 0.35, 0.08),
    "NEXUS_Dark_Metal")
for i in range(5):
    x = -11.8 + i * 0.15
    cyl("CHEM_RACK_BOTTLE_%d" % i, (x, 20.35, FLOOR + 1.0), 0.04, 0.2,
        ("NEXUS_Amber", "NEXUS_Green", "NEXUS_Toxic_Spill")[i % 3], verts=10)
    cyl("CHEM_RACK_CAP_%d" % i, (x, 20.35, FLOOR + 1.11), 0.025, 0.04,
        "NEXUS_Dark_Metal", verts=10)

box("CHEM_GLASS_TRAY", (-11.25, 18.3, FLOOR + 0.84), (0.55, 0.4, 0.05),
    "NEXUS_Steel")
for i in range(3):
    cyl("CHEM_BEAKER_%d" % i, (-11.4 + i * 0.16, 18.25, FLOOR + 0.94),
        0.06, 0.16, "NEXUS_Glass", verts=12)
cone("CHEM_FLASK", (-11.2, 18.55, FLOOR + 0.93), 0.09, 0.16,
     "NEXUS_Glass", r2=0.025)
cyl("CHEM_FLASK_NECK", (-11.2, 18.55, FLOOR + 1.02), 0.025, 0.08,
    "NEXUS_Glass", verts=10)
box("CHEM_BURNER_BASE", (-11.1, 19.45, FLOOR + 0.83), (0.14, 0.14, 0.05),
    "NEXUS_Dark_Metal")
tube("CHEM_BURNER_TUBE", (-11.1, 19.45, FLOOR + 0.85),
     (-11.1, 19.45, FLOOR + 1.13), 0.022, "NEXUS_Steel")
box("CHEM_SAMPLE_CASE", (-11.5, 19.8, FLOOR + 0.93), (0.65, 0.42, 0.26),
    "NEXUS_Dark_Metal")
box("CHEM_SAMPLE_CASE_STRIPE", (-11.5, 19.8, FLOOR + 1.0), (0.5, 0.02, 0.08),
    "NEXUS_Amber")

cyl("CHEM_STOOL_SEAT", (-10.15, 17.65, FLOOR + 0.6), 0.3, 0.06,
    "NEXUS_Rubber", verts=20)
tube("CHEM_STOOL_POLE", (-10.15, 17.65, FLOOR + 0.03),
     (-10.15, 17.65, FLOOR + 0.58), 0.045, "NEXUS_Steel")
cyl("CHEM_STOOL_BASE", (-10.15, 17.65, FLOOR + 0.03), 0.22, 0.05,
    "NEXUS_Steel", verts=16)
point("CHEM_ISLAND_LIGHT", (-11.5, 19.0, FLOOR + 1.55), 32,
      (1.0, 0.86, 0.66), 0.28)

# estanterias de reactivos en la pared sur
def reagent_shelf(tag, cx, width, boards):
    box(tag + "_BACK", (cx, 14.32, FLOOR + 1.05), (width, 0.05, 2.1),
        "NEXUS_Rack_Paint")
    for side, dx in ((0, -width / 2 + 0.04), (1, width / 2 - 0.04)):
        box(tag + "_POST_%d" % side, (cx + dx, 14.42, FLOOR + 1.05),
            (0.06, 0.24, 2.1), "NEXUS_Rusted_Metal")
    for i, z in enumerate(boards):
        box(tag + "_BOARD_%d" % i, (cx, 14.42, FLOOR + z),
            (width - 0.04, 0.24, 0.04), "NEXUS_Rusted_Metal")
        if i < 3:
            for j in range(4):
                bx = cx - width / 2 + 0.3 + j * (width - 0.6) / 3
                cyl(tag + "_BOTTLE_%d_%d" % (i, j),
                    (bx, 14.42, FLOOR + z + 0.12), 0.05, 0.18,
                    ("NEXUS_Green", "NEXUS_Toxic_Spill", "NEXUS_Amber",
                     "NEXUS_Blood_Dark")[(i + j) % 4], verts=10)
                cyl(tag + "_CAP_%d_%d" % (i, j),
                    (bx, 14.42, FLOOR + z + 0.23), 0.028, 0.04,
                    "NEXUS_Dark_Metal", verts=8)


reagent_shelf("CHEM_SHELF_A", -13.65, 1.9, (0.25, 0.75, 1.25, 1.7))
reagent_shelf("CHEM_SHELF_B", -7.2, 1.6, (0.25, 0.75, 1.25, 1.7))
for i, (x, y) in enumerate(((-12.7, 15.1), (-7.9, 15.2), (-13.1, 15.5))):
    cyl("CHEM_FALLEN_BOTTLE_%d" % i, (x, y, FLOOR + 0.09), 0.05, 0.18,
        ("NEXUS_Green", "NEXUS_Amber", "NEXUS_Toxic_Spill")[i], verts=10)

# carro volcado y polvo neutralizante
box("CHEM_CART", (-8.4, 18.0, FLOOR + 0.095), (0.7, 1.0, 0.08),
    "NEXUS_Steel", rotation=(0.05, 0.1, 0.5))
beam("CHEM_CART_HANDLE", (-8.7, 17.6, FLOOR + 0.1),
     (-9.05, 17.3, FLOOR + 0.8), 0.04, "NEXUS_Steel")
for i, (x, y) in enumerate(((-9.1, 18.4), (-8.0, 17.5), (-7.7, 18.3))):
    cyl("CHEM_CART_WHEEL_%d" % i, (x, y, FLOOR + 0.08), 0.08, 0.05,
        "NEXUS_Rubber", axis="Y", verts=12)
for i in range(4):
    cyl("CHEM_SPILLED_BOTTLE_%d" % i,
        (-9.05 + i * 0.25, 18.65 - i * 0.12, FLOOR + 0.07), 0.045, 0.16,
        ("NEXUS_Green", "NEXUS_Toxic_Spill", "NEXUS_Water",
         "NEXUS_Amber")[i], axis="X", verts=10)
puddle("CHEM_POWDER", -8.1, 18.55, 0.75, 0.55, "NEXUS_OffWhite")

# conducto de extraccion de la campana
box("CHEM_DUCT_RISE", (-14.5, 20.5, FLOOR + 3.3), (0.5, 0.5, 1.9),
    "NEXUS_Dark_Metal")
box("CHEM_DUCT_ELBOW", (-14.5, 20.5, FLOOR + 4.05), (0.62, 0.62, 0.4),
    "NEXUS_Dark_Metal")
box("CHEM_DUCT_RUN", (-11.65, 20.5, FLOOR + 4.1), (5.7, 0.45, 0.45),
    "NEXUS_Dark_Metal")
for i, x in enumerate((-13.2, -10.2)):
    box("CHEM_DUCT_STRAP_%d" % i, (x, 20.5, FLOOR + 4.32),
        (0.06, 0.52, 0.1), "NEXUS_Rusted_Metal")
box("CHEM_DUCT_GRILLE", (-8.77, 20.5, FLOOR + 4.1), (0.06, 0.52, 0.52),
    "NEXUS_GrillDark")

# ducha de emergencia, lavaojos y traje
tube("CHEM_SHOWER_PIPE", (-4.2, 18.5, FLOOR), (-4.2, 18.5, FLOOR + 2.75),
     0.055, "NEXUS_Steel")
beam("CHEM_SHOWER_ARM", (-4.2, 18.5, FLOOR + 2.72),
     (-4.55, 18.5, FLOOR + 2.72), 0.055, "NEXUS_Steel")
cyl("CHEM_SHOWER_HEAD", (-4.55, 18.5, FLOOR + 2.68), 0.18, 0.05,
    "NEXUS_Steel", verts=16)
tube("CHEM_SHOWER_CHAIN", (-4.17, 18.5, FLOOR + 2.2),
     (-4.17, 18.5, FLOOR + 1.2), 0.012, "NEXUS_Dark_Metal")
box("CHEM_SHOWER_HANDLE", (-4.17, 18.5, FLOOR + 1.15), (0.06, 0.1, 0.18),
    "NEXUS_Amber")
box("CHEM_SHOWER_GRATE", (-4.85, 18.5, FLOOR + 0.02), (0.95, 0.95, 0.04),
    "NEXUS_GrillDark")
box("CHEM_SHOWER_MAT", (-4.65, 18.5, FLOOR + 0.012), (0.8, 0.8, 0.02),
    "NEXUS_Amber")

box("CHEM_EYE_BASIN", (-4.18, 17.4, FLOOR + 0.95), (0.45, 0.38, 0.12),
    "NEXUS_Steel")
tube("CHEM_EYE_NOZ_0", (-4.28, 17.48, FLOOR + 1.0),
     (-4.28, 17.48, FLOOR + 1.16), 0.02, "NEXUS_Steel")
tube("CHEM_EYE_NOZ_1", (-4.28, 17.32, FLOOR + 1.0),
     (-4.28, 17.32, FLOOR + 1.16), 0.02, "NEXUS_Steel")
box("CHEM_EYE_PEDAL", (-4.3, 17.4, FLOOR + 0.03), (0.3, 0.18, 0.04),
    "NEXUS_Rubber")

box("CHEM_SUIT_TORSO", (-4.32, 16.0, FLOOR + 1.45), (0.2, 0.55, 0.95),
    "NEXUS_Clinical")
sphere("CHEM_SUIT_HOOD", (-4.32, 16.0, FLOOR + 2.02), 0.19,
       "NEXUS_Clinical", scale=(0.9, 1, 1))
box("CHEM_SUIT_VISOR", (-4.44, 16.0, FLOOR + 2.02), (0.03, 0.24, 0.12),
    "NEXUS_Dark_Metal")
for side, dy in ((0, -0.3), (1, 0.3)):
    beam("CHEM_SUIT_ARM_%d" % side, (-4.32, 16.0 + dy, FLOOR + 1.75),
         (-4.32, 16.0 + dy * 1.1, FLOOR + 1.05), 0.14, "NEXUS_Clinical")
    beam("CHEM_SUIT_LEG_%d" % side, (-4.32, 16.0 + dy * 0.5, FLOOR + 1.0),
         (-4.32, 16.0 + dy * 0.55, FLOOR + 0.15), 0.16, "NEXUS_Clinical")
    box("CHEM_SUIT_GLOVE_%d" % side, (-4.32, 16.0 + dy * 1.1, FLOOR + 1.0),
        (0.13, 0.16, 0.12), "NEXUS_Rubber")
box("CHEM_SUIT_HOOK", (-4.05, 16.0, FLOOR + 2.25), (0.08, 0.08, 0.08),
    "NEXUS_Rusted_Metal")

box("CHEM_MONITOR_BASE", (-10.0, 16.2, FLOOR + 0.03), (0.5, 0.5, 0.06),
    "NEXUS_Dark_Metal")
box("CHEM_MONITOR_POLE", (-10.0, 16.2, FLOOR + 0.85), (0.12, 0.12, 1.6),
    "NEXUS_Dark_Metal")
point("CHEM_HOOD_LIGHT", (-14.3, 20.4, FLOOR + 2.65), 28,
      (0.8, 0.95, 0.82), 0.25)

# equipo de banco norte
COFF = FLOOR + 0.81
box("CHEM_BENCH_HOTPLATE", (-9.3, 22.4, COFF + 0.07), (0.42, 0.34, 0.14),
    "NEXUS_Dark_Metal")
box("CHEM_BENCH_PLATE", (-9.3, 22.4, COFF + 0.15), (0.32, 0.26, 0.02),
    "NEXUS_Steel")
for i, x in enumerate((-9.42, -9.3, -9.18)):
    cyl("CHEM_BENCH_KNOB_%d" % i, (x, 22.56, COFF + 0.08), 0.022, 0.03,
        "NEXUS_Amber", axis="Y", verts=10)
for i, (x, mat) in enumerate(((-8.5, "NEXUS_Green"),
                              (-8.05, "NEXUS_Amber"))):
    cyl("CHEM_BENCH_BEAKER_%d" % i, (x, 22.4, COFF + 0.11), 0.075, 0.22,
        "NEXUS_Glass", verts=12)
    cyl("CHEM_BENCH_LIQUID_%d" % i, (x, 22.4, COFF + 0.07), 0.055, 0.12,
        mat, verts=12)
box("CHEM_BENCH_RACK", (-10.9, 22.4, COFF + 0.04), (0.55, 0.24, 0.05),
    "NEXUS_Steel")
for i in range(5):
    cyl("CHEM_BENCH_VIAL_%d" % i, (-11.1 + i * 0.1, 22.4, COFF + 0.15),
        0.022, 0.18, "NEXUS_Glass", verts=8)
box("CHEM_BENCH_SCALE", (-12.0, 22.4, COFF + 0.06), (0.32, 0.3, 0.1),
    "NEXUS_Clinical")
box("CHEM_BENCH_SCALE_PAN", (-12.0, 22.4, COFF + 0.12), (0.26, 0.24, 0.02),
    "NEXUS_Steel")
box("CHEM_BENCH_SCALE_DISP", (-12.0, 22.25, COFF + 0.07), (0.12, 0.01, 0.04),
    "NEXUS_MonitorScreen")

# estanterias murales de reactivos
for i, x in enumerate((-13.8, -6.4)):
    box("CHEM_WALL_SHELF_%d" % i, (x, 23.8, FLOOR + 2.35), (1.5, 0.32, 0.05),
        "NEXUS_Painted_Metal")
    for j, dx in enumerate((-0.55, 0.55)):
        beam("CHEM_SHELF_BRACKET_%d_%d" % (i, j),
             (x + dx, 23.96, FLOOR + 2.32), (x + dx, 23.66, FLOOR + 2.12),
             0.035, "NEXUS_Dark_Metal")
    for j, (dx, mat) in enumerate(((-0.55, "NEXUS_Toxic_Spill"),
                                   (-0.2, "NEXUS_Amber"),
                                   (0.18, "NEXUS_Red"),
                                   (0.55, "NEXUS_Green"))):
        cyl("CHEM_SHELF_BOTTLE_%d_%d" % (i, j), (x + dx, 23.78, FLOOR + 2.46),
            0.055, 0.2, "NEXUS_Glass", verts=10)
        cyl("CHEM_SHELF_LIQUID_%d_%d" % (i, j), (x + dx, 23.78, FLOOR + 2.42),
            0.04, 0.12, mat, verts=10)
        cyl("CHEM_SHELF_CAP_%d_%d" % (i, j), (x + dx, 23.78, FLOOR + 2.57),
            0.03, 0.03, "NEXUS_Dark_Metal", verts=10)

# desague bajo el derrame
box("CHEM_FLOOR_DRAIN", (-8.8, 19.1, FLOOR + 0.012), (0.55, 0.55, 0.024),
    "NEXUS_GrillDark")
for i in range(4):
    box("CHEM_DRAIN_SLOT_%d" % i, (-8.8, 18.91 + i * 0.13, FLOOR + 0.026),
        (0.42, 0.035, 0.012), "NEXUS_Dark_Metal")

# bajante industrial en la esquina noreste
tube("CHEM_WALL_PIPE", (-4.35, 23.35, FLOOR), (-4.35, 23.35, -9.0),
     0.07, "NEXUS_Steel")
tube("CHEM_WALL_PIPE_ELBOW", (-4.35, 23.35, -9.0), (-4.9, 23.35, -9.0),
     0.07, "NEXUS_Steel")
box("CHEM_WALL_VALVE", (-4.35, 23.35, FLOOR + 1.3), (0.22, 0.22, 0.1),
    "NEXUS_Rusted_Metal")

sign("CHEM_SIGN_DOOR", "QUIMICA // CORROSIVO", (-10.0, 14.07, -11.05),
     (math.pi / 2, 0, math.pi), 2.3, 0.46, 0.17)
sign("CHEM_SIGN_SHOWER", "DUCHA DE EMERGENCIA", (-4.07, 18.5, -10.45),
     (math.pi / 2, 0, -math.pi / 2), 1.6, 0.34, 0.12)
sign("CHEM_SIGN_STORE", "ALMACEN DE REACTIVOS", (-10.0, 23.93, -11.45),
     (math.pi / 2, 0, 0), 2.5, 0.4, 0.15)

print("QUIMICA detail listo")

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
