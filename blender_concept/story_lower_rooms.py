"""Add environmental storytelling to three representative lower-level rooms."""
import bpy
import math
import os
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
OUT = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V05_level1_v41.blend")

SCENE = bpy.context.scene
COL = bpy.data.collections.get("NEXUS_STORY_LOWER")
if COL is None:
    COL = bpy.data.collections.new("NEXUS_STORY_LOWER")
    SCENE.collection.children.link(COL)

# Remove any previous pass so the script is idempotent.
for obj in list(bpy.data.objects):
    if obj.name.startswith("NEXUS_STORY_") or obj.name.startswith("NEXUS_LOOT_"):
        bpy.data.objects.remove(obj, do_unlink=True)


def mat(name, fallback="NEXUS_Steel"):
    return bpy.data.materials.get(name) or bpy.data.materials.get(fallback)


def box(name, center, size, material, bevel=0.0, rot=(0.0, 0.0, 0.0), col=COL):
    mesh = bpy.data.meshes.new(name)
    x, y, z = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
    verts = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
             (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
             (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    obj.location = center
    obj.rotation_euler = rot
    if material:
        mesh.materials.append(material)
    if bevel > 0:
        mod = obj.modifiers.new("Bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    return obj


def ellipse(name, center, rx, ry, material, rot=0.0, segments=16, col=COL):
    mesh = bpy.data.meshes.new(name)
    verts = []
    for i in range(segments):
        a = 2.0 * math.pi * i / segments
        verts.append((math.cos(a) * rx, math.sin(a) * ry, 0.0))
    mesh.from_pydata(verts, [], [tuple(range(segments))])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    obj.location = center
    obj.rotation_euler.z = rot
    if material:
        mesh.materials.append(material)
    return obj


def cylinder(name, center, radius, depth, material, rot=(0.0, 0.0, 0.0), verts=12):
    mesh = bpy.data.meshes.new(name)
    verts_list = []
    for z in (-depth * 0.5, depth * 0.5):
        for i in range(verts):
            a = 2.0 * math.pi * i / verts
            verts_list.append((math.cos(a) * radius, math.sin(a) * radius, z))
    faces = []
    for i in range(verts):
        j = (i + 1) % verts
        faces.append((i, j, verts + j, verts + i))
    faces.append(tuple(range(verts - 1, -1, -1)))
    faces.append(tuple(range(verts, verts * 2)))
    mesh.from_pydata(verts_list, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    COL.objects.link(obj)
    obj.location = center
    obj.rotation_euler = rot
    if material:
        mesh.materials.append(material)
    return obj


def cable(name, points, material, radius=0.018):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for i, p in enumerate(points):
        spline.points[i].co = (p[0], p[1], p[2], 1.0)
    curve.bevel_depth = radius
    curve.bevel_resolution = 2
    obj = bpy.data.objects.new(name, curve)
    COL.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def point_light(name, loc, color, energy):
    light = bpy.data.lights.new(name, "POINT")
    light.color = color
    light.energy = energy
    light.shadow_soft_size = 0.22
    obj = bpy.data.objects.new(name, light)
    COL.objects.link(obj)
    obj.location = loc
    return obj


blood = mat("NEXUS_Blood_Dried", "NEXUS_Rubber")
paper = mat("NEXUS_Paper", "NEXUS_OffWhite")
sheet = mat("NEXUS_Clinical", "NEXUS_OffWhite")
glass = mat("NEXUS_Glass", "NEXUS_Clinical")
steel = mat("NEXUS_Steel")
rubber = mat("NEXUS_Rubber", "NEXUS_Steel")
amber = mat("NEXUS_Amber", "NEXUS_Paint")
white = mat("NEXUS_Clinical", "NEXUS_OffWhite")
oil = mat("NEXUS_Oil", "NEXUS_Rubber")
scorch = mat("NEXUS_Grime", "NEXUS_Rubber")

# ---------------------------------------------------------------- QUIROFANO
# Interrupted surgery: abandoned table, covered body, blood trail to the west door.
ellipse("NEXUS_STORY_QUIRO_BLOOD_BODY", (3.8, 16.2, -22.64), 0.95, 0.40, blood, 0.1)
box("NEXUS_STORY_QUIRO_BODY", (3.8, 16.2, -22.50), (1.75, 0.62, 0.26), sheet, 0.12)
box("NEXUS_STORY_QUIRO_BODY_HEAD", (2.80, 16.2, -22.46), (0.30, 0.34, 0.24), sheet, 0.10)
box("NEXUS_STORY_QUIRO_BODY_TAG", (4.35, 16.05, -22.33), (0.12, 0.08, 0.015), white, 0.005)

for i, (x, y, rx, ry) in enumerate([
    (1.0, 12.85, 0.35, 0.22), (0.15, 12.95, 0.28, 0.18),
    (-0.75, 13.10, 0.30, 0.17), (-1.65, 13.25, 0.24, 0.15),
    (-2.55, 13.40, 0.26, 0.14), (-3.35, 13.52, 0.22, 0.13),
]):
    ellipse(f"NEXUS_STORY_QUIRO_TRAIL_{i}", (x, y, -22.64), rx, ry, blood, i * 0.3)

box("NEXUS_STORY_QUIRO_TRAY", (2.55, 12.15, -22.56), (0.78, 0.48, 0.05), steel, 0.01, (0.18, -0.12, 0.25))
box("NEXUS_STORY_QUIRO_TRAY_LIP", (2.55, 11.94, -22.50), (0.76, 0.04, 0.10), steel, 0.006, (0.18, -0.12, 0.25))
for i, (dx, dy, ang) in enumerate([(-0.22, 0.02, 0.2), (0.0, -0.06, -0.4), (0.22, 0.04, 0.7)]):
    box(f"NEXUS_STORY_QUIRO_INSTR_{i}", (2.55 + dx, 12.15 + dy, -22.50),
        (0.22, 0.025, 0.012), steel, 0.003, (0.0, 0.0, ang))

for i, (px, py, ang) in enumerate([(-3.30, 15.55, 0.2), (-3.05, 15.70, -0.5),
                                   (-3.35, 15.95, 0.8), (-2.95, 16.15, -0.2)]):
    box(f"NEXUS_STORY_QUIRO_PAPER_{i}", (px, py, -22.63), (0.24, 0.32, 0.006), paper, 0.0, (0.0, 0.0, ang))

cylinder("NEXUS_STORY_QUIRO_IV_POLE", (-1.55, 10.95, -21.75), 0.035, 1.85, steel)
box("NEXUS_STORY_QUIRO_IV_BASE", (-1.55, 10.95, -22.60), (0.42, 0.42, 0.06), steel, 0.01)
box("NEXUS_STORY_QUIRO_IV_BAG", (-1.55, 10.95, -20.85), (0.17, 0.07, 0.32), sheet, 0.04)
box("NEXUS_STORY_QUIRO_MON_FLOOR", (5.15, 10.75, -22.52), (0.58, 0.38, 0.09), rubber, 0.01, (0.0, 0.0, 1.25))
ellipse("NEXUS_STORY_QUIRO_WALL_BLOOD", (0.55, 10.15, -21.15), 0.42, 0.55, blood, 0.0, 12)

# Recoverable sample case near the north-east corner.
box("NEXUS_LOOT_QUIRO_SAMPLE", (4.95, 17.25, -22.43), (0.42, 0.28, 0.20), white, 0.02)
box("NEXUS_LOOT_QUIRO_SAMPLE_LATCH", (4.95, 17.10, -22.33), (0.10, 0.03, 0.05), amber, 0.004)

# ------------------------------------------------------- CONTENCION PRIMARIA
# Breach from inside: blood drag, scratches, discarded restraints and foam.
for i, (x, z, ang) in enumerate([(-0.9, -31.25, 0.35), (0.2, -30.95, -0.25),
                                 (1.3, -31.15, 0.5), (2.2, -30.80, -0.4)]):
    box(f"NEXUS_STORY_CONTE_SCRATCH_{i}", (x, -9.13, z), (0.10, 0.02, 0.75), blood, 0.0, (0.0, ang, 0.0))

for i, (x, y, rx, ry) in enumerate([
    (0.55, -9.75, 0.38, 0.24), (0.35, -10.55, 0.32, 0.20),
    (0.15, -11.35, 0.34, 0.22), (0.0, -12.15, 0.28, 0.18),
    (-0.10, -12.95, 0.25, 0.16),
]):
    ellipse(f"NEXUS_STORY_CONTE_TRAIL_{i}", (x, y, -32.64), rx, ry, blood, i * 0.25)

for i, (x, y, ang) in enumerate([(3.65, -10.95, 0.3), (3.95, -10.70, -0.6),
                                 (4.15, -11.25, 0.9), (3.45, -11.35, -0.2)]):
    box(f"NEXUS_STORY_CONTE_GLASS_{i}", (x, y, -32.62), (0.28, 0.18, 0.012), glass, 0.0, (0.0, 0.0, ang))

box("NEXUS_STORY_CONTE_STRAP_0", (1.05, -10.40, -32.63), (0.62, 0.10, 0.018), rubber, 0.0, (0.0, 0.0, 0.45))
box("NEXUS_STORY_CONTE_STRAP_1", (-1.20, -10.05, -32.63), (0.55, 0.09, 0.018), rubber, 0.0, (0.0, 0.0, -0.35))
box("NEXUS_STORY_CONTE_STRAP_2", (0.30, -11.65, -32.63), (0.48, 0.08, 0.018), rubber, 0.0, (0.0, 0.0, 1.1))

# Discarded hazmat suit in the north-west corner.
box("NEXUS_STORY_CONTE_SUIT_TORSO", (-4.75, -10.10, -32.52), (0.62, 0.42, 0.18), white, 0.05, (0.0, 0.0, 0.65))
box("NEXUS_STORY_CONTE_SUIT_LEG_0", (-4.35, -10.55, -32.57), (0.55, 0.16, 0.12), white, 0.04, (0.0, 0.0, 0.9))
box("NEXUS_STORY_CONTE_SUIT_LEG_1", (-5.05, -10.55, -32.57), (0.50, 0.15, 0.12), white, 0.04, (0.0, 0.0, 0.4))
box("NEXUS_STORY_CONTE_SUIT_ARM", (-5.25, -9.75, -32.55), (0.52, 0.14, 0.12), white, 0.04, (0.0, 0.0, -0.5))
box("NEXUS_STORY_CONTE_SUIT_STRIPE", (-4.75, -10.10, -32.42), (0.58, 0.10, 0.012), amber, 0.0, (0.0, 0.0, 0.65))

for i, (x, y, rx, ry) in enumerate([(2.25, -9.85, 0.32, 0.18), (2.75, -10.05, 0.24, 0.14),
                                    (1.85, -9.65, 0.20, 0.13), (3.10, -9.55, 0.18, 0.12)]):
    ellipse(f"NEXUS_STORY_CONTE_FOAM_{i}", (x, y, -32.64), rx, ry, white, i * 0.4)

box("NEXUS_STORY_CONTE_CART", (-4.55, -16.25, -32.35), (0.85, 0.50, 0.55), steel, 0.02, (1.35, 0.0, 0.25))
box("NEXUS_STORY_CONTE_MASK", (0.75, -11.55, -32.61), (0.22, 0.16, 0.08), rubber, 0.02, (0.0, 0.0, 0.4))

box("NEXUS_STORY_CONTE_BEACON", (1.05, -9.20, -30.35), (0.20, 0.12, 0.14), blood, 0.01)
point_light("NEXUS_STORY_CONTE_LIGHT", (1.05, -9.55, -30.30), (1.0, 0.02, 0.01), 55.0)

box("NEXUS_LOOT_CONTE_DRIVE", (5.15, -10.05, -32.43), (0.24, 0.18, 0.10), rubber, 0.01)
box("NEXUS_LOOT_CONTE_DRIVE_LED", (5.15, -10.05, -32.37), (0.04, 0.02, 0.012), amber, 0.002)

# ------------------------------------------------------------- GENERADORES
# Failed generator, oil spill, scorched panel and abandoned tools.
for i, (x, y, rx, ry) in enumerate([
    (-4.55, 12.35, 0.55, 0.35), (-5.05, 11.85, 0.48, 0.28),
    (-5.55, 11.35, 0.42, 0.24), (-6.05, 10.85, 0.36, 0.20),
    (-6.50, 10.35, 0.30, 0.16), (-6.85, 9.90, 0.24, 0.13),
]):
    ellipse(f"NEXUS_STORY_GEN_OIL_{i}", (x, y, -43.64), rx, ry, oil, i * 0.2)

box("NEXUS_STORY_GEN_BURN", (-4.20, 12.62, -42.55), (1.30, 0.035, 0.82), scorch, 0.0)
box("NEXUS_STORY_GEN_BURN_EDGE", (-4.20, 12.60, -42.08), (1.42, 0.02, 0.06), amber, 0.0)
ellipse("NEXUS_STORY_GEN_SOOT", (-4.65, 11.95, -43.63), 0.62, 0.38, scorch, 0.2)

box("NEXUS_STORY_GEN_TOOLBOX", (-6.55, 10.45, -43.45), (0.62, 0.34, 0.24), steel, 0.02, (0.0, 0.0, 0.35))
box("NEXUS_STORY_GEN_TOOLBOX_LID", (-6.55, 10.45, -43.31), (0.60, 0.32, 0.04), rubber, 0.01, (0.0, 0.0, 0.35))
box("NEXUS_STORY_GEN_WRENCH", (-5.75, 10.15, -43.60), (0.45, 0.07, 0.025), steel, 0.005, (0.0, 0.0, -0.55))
box("NEXUS_STORY_GEN_HAMMER", (-6.95, 10.95, -43.58), (0.34, 0.09, 0.05), steel, 0.01, (0.0, 0.0, 0.95))

cylinder("NEXUS_STORY_GEN_HELMET", (-7.20, 9.75, -43.53), 0.18, 0.13, amber, (0.0, 0.0, 0.0), 14)
box("NEXUS_STORY_GEN_GLOVE", (-6.55, 9.85, -43.60), (0.18, 0.12, 0.035), rubber, 0.02, (0.0, 0.0, 0.5))

cable("NEXUS_STORY_GEN_CABLE", [(-8.60, 10.35, -40.55), (-8.45, 10.55, -41.20),
                                (-8.20, 10.85, -42.00), (-7.95, 11.20, -43.40)], rubber, 0.022)
box("NEXUS_STORY_GEN_CABLE_CLAMP", (-8.60, 10.35, -40.55), (0.30, 0.16, 0.08), steel, 0.01)

# A body bag near the east wall, away from the door route.
ellipse("NEXUS_STORY_GEN_BLOOD_BODY", (-3.05, 10.25, -43.64), 0.80, 0.34, blood, 0.15)
box("NEXUS_STORY_GEN_BODY", (-3.05, 10.25, -43.50), (1.60, 0.55, 0.22), rubber, 0.10, (0.0, 0.0, 0.15))
box("NEXUS_STORY_GEN_BODY_TAG", (-3.70, 10.10, -43.36), (0.16, 0.10, 0.012), white, 0.004)

# Trip cable across the south aisle: a noisy environmental hazard.
cylinder("NEXUS_STORY_GEN_TRIPWIRE", (-8.20, 9.55, -43.45), 0.012, 2.80, rubber, (0.0, math.pi / 2.0, 0.0), 8)
box("NEXUS_STORY_GEN_CANS", (-6.20, 9.70, -43.52), (0.30, 0.22, 0.18), steel, 0.01, (0.0, 0.0, 0.3))
box("NEXUS_STORY_GEN_CANS_2", (-5.95, 9.50, -43.56), (0.16, 0.16, 0.12), steel, 0.01, (0.0, 0.0, 0.8))

box("NEXUS_LOOT_GEN_FUSE", (-11.85, 10.20, -43.45), (0.38, 0.26, 0.18), steel, 0.02)
box("NEXUS_LOOT_GEN_FUSE_LABEL", (-11.85, 10.20, -43.35), (0.20, 0.02, 0.06), amber, 0.003)

bpy.context.scene.camera = bpy.data.objects.get("NEXUS_V05_CAM_Corridor")
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("STORY_LOWER_SAVED", OUT, os.path.getsize(OUT))
print("STORY_OBJECTS", len([o for o in bpy.data.objects if o.name.startswith(("NEXUS_STORY_", "NEXUS_LOOT_"))]))
