"""Narrative and function for HABITACIONES_MEDICAS and CAMARAS_FRIGORIFICAS."""
import bpy
import math
from mathutils import Vector, Matrix

COL = bpy.data.collections.get("NEXUS_STORY_LOWER")
if COL is None:
    COL = bpy.data.collections.new("NEXUS_STORY_LOWER")
    bpy.context.scene.collection.children.link(COL)


def mat(name):
    return bpy.data.materials.get(name)


def make_mat(name, base, rough=0.8, metal=0.0):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*base, 1.0)
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metal
    return m


FROST = make_mat("NEXUS_Frost", (0.72, 0.82, 0.88), 0.86, 0.0)
WATER = make_mat("NEXUS_Meltwater", (0.025, 0.045, 0.055), 0.08, 0.0)


def box(name, center, size, material, bevel=0.006):
    mesh = bpy.data.meshes.new(name)
    x, y, z = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
    verts = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
             (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    COL.objects.link(obj)
    obj.location = center
    m = mat(material) if isinstance(material, str) else material
    if m:
        mesh.materials.append(m)
    if bevel > 0:
        mod = obj.modifiers.new("Bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 1
    return obj


def cyl(name, center, radius, depth, material, axis="Z", verts=14):
    mesh = bpy.data.meshes.new(name)
    ring = []
    for z in (-depth * 0.5, depth * 0.5):
        for i in range(verts):
            a = 2.0 * math.pi * i / verts
            ring.append((math.cos(a) * radius, math.sin(a) * radius, z))
    faces = []
    for i in range(verts):
        j = (i + 1) % verts
        faces.append((i, j, verts + j, verts + i))
    faces.append(tuple(range(verts - 1, -1, -1)))
    faces.append(tuple(range(verts, verts * 2)))
    mesh.from_pydata(ring, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    COL.objects.link(obj)
    obj.location = center
    if axis == "X":
        obj.rotation_euler.y = math.pi / 2
    elif axis == "Y":
        obj.rotation_euler.x = math.pi / 2
    m = mat(material) if isinstance(material, str) else material
    if m:
        mesh.materials.append(m)
    return obj


def text(name, body, loc, normal, size):
    n = Vector(normal).normalized()
    up = Vector((0, 0, 1))
    if abs(n.dot(up)) > 0.95:
        up = Vector((0, 1, 0))
    right = up.cross(n).normalized()
    up2 = n.cross(right).normalized()
    rot = Matrix((right, up2, n)).transposed().to_4x4()
    box(name + "_PLATE", Vector(loc) - n * 0.03, (size * 5.2, size * 1.5, 0.04), "NEXUS_SignPlate", 0.004)
    bpy.data.objects[name + "_PLATE"].matrix_world = Matrix.Translation(Vector(loc) - n * 0.04) @ rot
    curve = bpy.data.curves.new(name + "_TEXT", type="FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    curve.extrude = 0.004
    obj = bpy.data.objects.new(curve.name, curve)
    COL.objects.link(obj)
    obj.matrix_world = Matrix.Translation(Vector(loc)) @ rot
    obj.data.materials.append(mat("NEXUS_SignText") or mat("NEXUS_Amber"))


# ---------------- HABITACIONES_MEDICAS ----------------
# Floor stand for the patient monitor.
box("NEXUS_STORY_HAB_MON_BASE", (15.5, -1.46, -22.62), (0.48, 0.48, 0.05), "NEXUS_Steel", 0.01)
cyl("NEXUS_STORY_HAB_MON_POLE", (15.5, -1.46, -22.10), 0.025, 1.05, "NEXUS_Steel")

# Privacy curtain rail and two panels between the beds.
cyl("NEXUS_STORY_HAB_CURTAIN_RAIL", (15.5, -3.65, -19.38), 0.022, 2.5, "NEXUS_Steel", "Y", 10)
for i, y in enumerate((-4.35, -2.95)):
    box(f"NEXUS_STORY_HAB_CURTAIN_{i}", (15.5, y, -20.42), (0.035, 1.05, 1.95), "NEXUS_Clinical", 0.008)
    for j in range(4):
        box(f"NEXUS_STORY_HAB_CURTAIN_LOOP_{i}_{j}", (15.5, y - 0.42 + j * 0.28, -19.42), (0.05, 0.035, 0.08), "NEXUS_Steel", 0.003)

# Bedside tables.
for tag, x in (("A", 13.88), ("B", 17.12)):
    box(f"NEXUS_STORY_HAB_TABLE_{tag}_TOP", (x, -5.45, -21.56), (0.5, 0.4, 0.05), "NEXUS_Clinical", 0.01)
    for i, (dx, dy) in enumerate(((-0.2, -0.15), (0.2, -0.15), (-0.2, 0.15), (0.2, 0.15))):
        cyl(f"NEXUS_STORY_HAB_TABLE_{tag}_LEG_{i}", (x + dx, -5.45 + dy, -22.10), 0.02, 1.05, "NEXUS_Steel")

# Items on bedside tables.
box("NEXUS_STORY_HAB_FILE", (13.72, -5.43, -21.51), (0.24, 0.3, 0.02), "NEXUS_Paper", 0.0)
box("NEXUS_STORY_HAB_CUP", (14.02, -5.38, -21.47), (0.07, 0.07, 0.1), "NEXUS_Clinical", 0.01)
box("NEXUS_LOOT_HAB_KEY", (17.12, -5.42, -21.5), (0.03, 0.13, 0.04), "NEXUS_Steel", 0.002)
box("NEXUS_LOOT_HAB_KEY_TAG", (17.12, -5.3, -21.5), (0.1, 0.07, 0.02), "NEXUS_Amber", 0.0)
box("NEXUS_STORY_HAB_MEDS", (17.28, -5.46, -21.48), (0.16, 0.16, 0.12), "NEXUS_Clinical", 0.012)

# IV stands at the foot of both beds.
for tag, x in (("A", 13.45), ("B", 17.55)):
    cyl(f"NEXUS_STORY_HAB_IV_{tag}_BASE", (x, -2.28, -22.58), 0.2, 0.05, "NEXUS_Steel")
    cyl(f"NEXUS_STORY_HAB_IV_{tag}_POLE", (x, -2.28, -21.75), 0.022, 1.65, "NEXUS_Steel")
    box(f"NEXUS_STORY_HAB_IV_{tag}_BAG", (x, -2.28, -20.98), (0.2, 0.06, 0.3), "NEXUS_Clinical", 0.02)

# Occupied bed 1: sheet and head.
box("NEXUS_STORY_HAB_SHEET", (17.12, -3.8, -21.93), (0.62, 1.5, 0.06), "NEXUS_OffWhite", 0.02)
box("NEXUS_STORY_HAB_HEAD", (17.12, -3.0, -21.86), (0.28, 0.26, 0.16), "NEXUS_OffWhite", 0.03)
box("NEXUS_STORY_HAB_TAG", (17.5, -3.55, -21.9), (0.07, 0.11, 0.02), "NEXUS_Paper", 0.0)

# Blood trail from bed 1 to the west door, routed around bed 0.
for i, (x, y) in enumerate((
    (16.8, -2.0), (16.1, -1.9), (15.3, -1.9), (14.5, -1.9),
    (13.7, -1.92), (13.0, -2.0), (12.4, -2.5), (12.2, -3.3), (12.2, -4.1),
)):
    box(f"NEXUS_STORY_HAB_BLOOD_{i}", (x, y, -22.63), (0.32, 0.22, 0.02), "NEXUS_Blood_Dried", 0.002)

# Overturned wheelchair by the south-east corner.
box("NEXUS_STORY_HAB_CHAIR_SEAT", (19.0, -1.45, -22.24), (0.6, 0.56, 0.08), "NEXUS_Rubber", 0.02)
box("NEXUS_STORY_HAB_CHAIR_BACK", (19.0, -1.18, -21.88), (0.6, 0.08, 0.62), "NEXUS_Rubber", 0.02)
cyl("NEXUS_STORY_HAB_CHAIR_WHEEL_0", (18.72, -1.72, -22.55), 0.23, 0.05, "NEXUS_Rubber", "X", 12)
cyl("NEXUS_STORY_HAB_CHAIR_WHEEL_1", (19.28, -1.72, -22.55), 0.23, 0.05, "NEXUS_Rubber", "X", 12)

# Sign and hand sanitizer at the entrance.
text("NEXUS_STORY_HAB_SIGN", "HABITACIONES MEDICAS", (11.16, -2.75, -20.42), (1, 0, 0), 0.1)
box("NEXUS_STORY_HAB_SANITIZER", (11.2, -2.9, -21.25), (0.12, 0.12, 0.24), "NEXUS_Clinical", 0.02)


# ---------------- CAMARAS_FRIGORIFICAS ----------------
# Frost patches on the floor.
for i, (x, y, sx, sy) in enumerate((
    (-18.1, 2.8, 1.1, 0.55), (-12.3, -2.9, 1.3, 0.7), (-17.6, -2.8, 0.9, 0.45), (-13.4, 2.9, 1.0, 0.5),
)):
    box(f"NEXUS_STORY_COLD_FROST_{i}", (x, y, -22.64), (sx, sy, 0.02), FROST, 0.004)

# Meltwater puddles.
for i, (x, y, sx, sy) in enumerate((
    (-16.6, -0.2, 0.95, 0.5), (-13.4, -2.35, 0.8, 0.4), (-18.0, 0.55, 0.6, 0.35),
)):
    box(f"NEXUS_STORY_COLD_WATER_{i}", (x, y, -22.63), (sx, sy, 0.015), WATER, 0.002)

# Gurney with a body bag in the south half.
box("NEXUS_STORY_COLD_GURNEY_TOP", (-16.8, -1.0, -21.85), (0.72, 1.95, 0.08), "NEXUS_Steel", 0.01)
for i, (dx, dy) in enumerate(((-0.28, -0.82), (0.28, -0.82), (-0.28, 0.82), (0.28, 0.82))):
    cyl(f"NEXUS_STORY_COLD_GURNEY_WHEEL_{i}", (-16.8 + dx, -1.0 + dy, -22.55), 0.07, 0.04, "NEXUS_Rubber", "X", 10)
box("NEXUS_STORY_COLD_BODYBAG", (-16.8, -1.0, -21.76), (0.62, 1.72, 0.12), "NEXUS_BodyBag", 0.04)
box("NEXUS_STORY_COLD_BODY_CHEST", (-16.8, -1.35, -21.68), (0.46, 0.62, 0.06), "NEXUS_BodyBag", 0.02)
box("NEXUS_STORY_COLD_BODY_LEGS", (-16.8, -0.45, -21.69), (0.34, 0.55, 0.05), "NEXUS_BodyBag", 0.02)
box("NEXUS_STORY_COLD_TOETAG", (-16.8, -0.08, -21.71), (0.12, 0.14, 0.015), "NEXUS_Paper", 0.0)

# Broken vial tray near the gurney.
box("NEXUS_STORY_COLD_TRAY", (-15.75, -1.9, -22.56), (0.42, 0.3, 0.04), "NEXUS_Steel", 0.004)
for i in range(3):
    cyl(f"NEXUS_STORY_COLD_VIAL_{i}", (-15.88 + i * 0.12, -1.9, -22.5), 0.025, 0.1, "NEXUS_Glass", "Z", 8)
box("NEXUS_STORY_COLD_VIAL_GLASS", (-15.55, -1.95, -22.62), (0.3, 0.22, 0.02), "NEXUS_Glass", 0.0)

# Loot: cold sample case by rack 2.
box("NEXUS_LOOT_COLD_SAMPLE", (-12.7, 0.95, -22.42), (0.3, 0.22, 0.18), "NEXUS_Clinical", 0.012)
box("NEXUS_LOOT_COLD_SAMPLE_LID", (-12.7, 0.95, -22.32), (0.32, 0.24, 0.03), "NEXUS_Amber", 0.002)

# Cold working light.
ld = bpy.data.lights.new("NEXUS_STORY_COLD_LIGHT", "POINT")
ld.energy = 90.0
ld.color = (0.62, 0.8, 1.0)
ld.shadow_soft_size = 0.2
lo = bpy.data.objects.new(ld.name, ld)
COL.objects.link(lo)
lo.location = (-15.0, 0.0, -21.6)

# Warning sign by the west door.
text("NEXUS_STORY_COLD_SIGN", "CAMARA FRIGORIFICA // -20 C", (-10.84, -2.4, -20.85), (1, 0, 0), 0.1)

print("STORY_MED_REST_DONE", len([o for o in COL.objects if o.type == "MESH"]))
bpy.ops.wm.save_as_mainfile(filepath="/home/riyo/Documentos/game/blender_concept/FM_NEXUS_V05_level1_v58.blend")
print("V58_SAVED")
