"""Narrative props for ENFERMERIA and MORGUE (L3)."""
import bpy
import math
from mathutils import Vector, Matrix

COL = bpy.data.collections.get("NEXUS_STORY_LOWER")
if COL is None:
    COL = bpy.data.collections.new("NEXUS_STORY_LOWER")
    bpy.context.scene.collection.children.link(COL)


def mat(name):
    return bpy.data.materials.get(name)


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
    m = mat(material)
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
    m = mat(material)
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
    plate = bpy.data.objects[name + "_PLATE"]
    plate.matrix_world = Matrix.Translation(Vector(loc) - n * 0.04) @ rot
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


# ---------------- ENFERMERIA (L3) ----------------
# IV stand beside bed 0.
cyl("NEXUS_STORY_ENF_IV_BASE", (-7.68, 13.72, -22.58), 0.2, 0.05, "NEXUS_Steel")
cyl("NEXUS_STORY_ENF_IV_POLE", (-7.68, 13.72, -21.75), 0.022, 1.65, "NEXUS_Steel")
box("NEXUS_STORY_ENF_IV_BAG", (-7.68, 13.72, -20.98), (0.2, 0.06, 0.3), "NEXUS_Clinical", 0.02)
box("NEXUS_STORY_ENF_IV_TAG", (-7.68, 13.69, -20.93), (0.12, 0.01, 0.05), "NEXUS_Paper", 0.0)

# Covered patient on bed 1, sheet slightly above the mattress.
box("NEXUS_STORY_ENF_SHEET", (-5.56, 12.95, -21.93), (0.58, 1.55, 0.07), "NEXUS_OffWhite", 0.02)
box("NEXUS_STORY_ENF_HEAD", (-5.56, 13.62, -21.85), (0.3, 0.3, 0.18), "NEXUS_OffWhite", 0.03)
box("NEXUS_STORY_ENF_TAG", (-5.05, 13.42, -21.84), (0.08, 0.12, 0.02), "NEXUS_Paper", 0.0)

# Blood trail from bed 1 toward the east door.
for i, (x, y, sx, sy) in enumerate((
    (-4.85, 12.95, 0.34, 0.24),
    (-4.45, 12.85, 0.38, 0.26),
    (-4.05, 12.72, 0.3, 0.2),
    (-3.68, 12.62, 0.24, 0.18),
    (-3.38, 12.55, 0.16, 0.12),
)):
    box(f"NEXUS_STORY_ENF_BLOOD_{i}", (x, y, -22.63), (sx, sy, 0.02), "NEXUS_Blood_Dried", 0.002)

# Medical cart.
box("NEXUS_STORY_ENF_CART_TOP", (-7.0, 10.45, -21.72), (1.15, 0.55, 0.05), "NEXUS_Steel", 0.01)
box("NEXUS_STORY_ENF_CART_SHELF", (-7.0, 10.45, -22.25), (1.05, 0.48, 0.03), "NEXUS_Steel", 0.006)
for i, (x, y) in enumerate(((-7.45, 10.25), (-6.55, 10.25), (-7.45, 10.65), (-6.55, 10.65))):
    cyl(f"NEXUS_STORY_ENF_CART_WHEEL_{i}", (x, y, -22.55), 0.055, 0.04, "NEXUS_Rubber", "X", 10)
box("NEXUS_STORY_ENF_CART_TRAY", (-7.25, 10.45, -21.66), (0.42, 0.3, 0.04), "NEXUS_Steel", 0.004)
for i in range(4):
    box(f"NEXUS_STORY_ENF_MED_{i}", (-7.45 + i * 0.075, 10.45, -21.6), (0.05, 0.12, 0.08), "NEXUS_Clinical", 0.006)
box("NEXUS_STORY_ENF_PAPERS", (-6.55, 10.5, -21.68), (0.28, 0.2, 0.015), "NEXUS_Paper", 0.0)
box("NEXUS_LOOT_ENF_MEDS", (-6.9, 10.4, -21.56), (0.32, 0.24, 0.16), "NEXUS_Clinical", 0.012)
box("NEXUS_LOOT_ENF_MEDS_STRAP", (-6.9, 10.4, -21.47), (0.34, 0.05, 0.025), "NEXUS_Amber", 0.002)

# Tipped wheelchair near the north-east corner.
box("NEXUS_STORY_ENF_CHAIR_SEAT", (-4.2, 14.75, -22.28), (0.62, 0.58, 0.08), "NEXUS_Rubber", 0.02)
box("NEXUS_STORY_ENF_CHAIR_BACK", (-4.2, 15.02, -21.9), (0.62, 0.08, 0.65), "NEXUS_Rubber", 0.02)
cyl("NEXUS_STORY_ENF_CHAIR_WHEEL_0", (-4.48, 14.48, -22.55), 0.24, 0.05, "NEXUS_Rubber", "X", 14)
cyl("NEXUS_STORY_ENF_CHAIR_WHEEL_1", (-3.92, 14.48, -22.55), 0.24, 0.05, "NEXUS_Rubber", "X", 14)
box("NEXUS_STORY_ENF_CHAIR_FOOT", (-4.2, 14.42, -22.55), (0.5, 0.08, 0.05), "NEXUS_Steel", 0.006)

# Overturned stool.
cyl("NEXUS_STORY_ENF_STOOL_TOP", (-9.35, 14.85, -22.35), 0.22, 0.05, "NEXUS_Rubber", "Z", 12)
for i, (x, y) in enumerate(((-9.52, 14.68), (-9.18, 14.68), (-9.52, 15.02), (-9.18, 15.02))):
    cyl(f"NEXUS_STORY_ENF_STOOL_LEG_{i}", (x, y, -22.55), 0.018, 0.4, "NEXUS_Steel")

# ---------------- MORGUE (L3) ----------------
# Open body bag detail and toe tag on slab 0.
box("NEXUS_STORY_MORGUE_BAG_FLAP", (13.0, 3.1, -21.9), (0.42, 1.6, 0.03), "NEXUS_Rubber", 0.008)
box("NEXUS_STORY_MORGUE_TOE_TAG", (13.24, 2.18, -21.84), (0.1, 0.14, 0.015), "NEXUS_Paper", 0.0)
box("NEXUS_STORY_MORGUE_TAG_STRING", (13.24, 2.28, -21.87), (0.015, 0.1, 0.015), "NEXUS_OffWhite", 0.0)

# Blood under slab 0 and a short trail to the drain.
for i, (x, y, sx, sy) in enumerate((
    (13.24, 2.72, 0.62, 0.72),
    (13.58, 2.32, 0.4, 0.3),
    (13.92, 2.0, 0.32, 0.24),
    (14.28, 1.7, 0.26, 0.2),
    (14.55, 1.38, 0.2, 0.16),
)):
    box(f"NEXUS_STORY_MORGUE_BLOOD_{i}", (x, y, -22.63), (sx, sy, 0.02), "NEXUS_Blood_Dried", 0.002)
box("NEXUS_STORY_MORGUE_DRAIN", (14.62, 1.18, -22.63), (0.42, 0.42, 0.02), "NEXUS_Steel", 0.002)
for i in range(3):
    box(f"NEXUS_STORY_MORGUE_DRAIN_SLOT_{i}", (14.62, 1.05 + i * 0.12, -22.61), (0.34, 0.035, 0.012), "NEXUS_Concrete_Dark", 0.0)

# Instrument cart near the west wall, clear of the door.
box("NEXUS_STORY_MORGUE_CART_TOP", (11.86, 6.45, -21.66), (1.05, 0.55, 0.05), "NEXUS_Steel", 0.01)
box("NEXUS_STORY_MORGUE_CART_LOW", (11.86, 6.45, -22.25), (0.95, 0.48, 0.03), "NEXUS_Steel", 0.006)
for i, (x, y) in enumerate(((11.48, 6.27), (12.24, 6.27), (11.48, 6.63), (12.24, 6.63))):
    cyl(f"NEXUS_STORY_MORGUE_CART_WHEEL_{i}", (x, y, -22.55), 0.05, 0.04, "NEXUS_Rubber", "X", 10)
box("NEXUS_STORY_MORGUE_TRAY", (11.62, 6.42, -21.6), (0.5, 0.32, 0.04), "NEXUS_Steel", 0.004)
for i in range(3):
    box(f"NEXUS_STORY_MORGUE_TOOL_{i}", (11.5 + i * 0.12, 6.42, -21.55), (0.03, 0.22, 0.02), "NEXUS_Steel", 0.002)
box("NEXUS_STORY_MORGUE_CLIPBOARD", (12.25, 6.45, -21.6), (0.24, 0.32, 0.02), "NEXUS_Paper", 0.0)
box("NEXUS_LOOT_MORGUE_KEY", (12.3, 7.06, -20.6), (0.02, 0.14, 0.05), "NEXUS_Steel", 0.002)
box("NEXUS_LOOT_MORGUE_KEY_TAG", (12.3, 7.18, -20.6), (0.12, 0.08, 0.02), "NEXUS_Amber", 0.0)

# Cold working light over the slabs.
ld = bpy.data.lights.new("NEXUS_STORY_MORGUE_LIGHT", "AREA")
ld.shape = "RECTANGLE"
ld.size = 3.2
ld.size_y = 1.2
ld.energy = 180.0
ld.color = (0.66, 0.82, 1.0)
lo = bpy.data.objects.new(ld.name, ld)
COL.objects.link(lo)
lo.location = (15.0, 4.4, -20.5)

# Restricted access sign by the door.
text("NEXUS_STORY_MORGUE_SIGN", "MORGUE // ACCESO RESTRINGIDO", (11.03, 6.8, -20.75), (1, 0, 0), 0.1)

print("STORY_ENF_MORGUE_DONE", len([o for o in COL.objects if o.type == "MESH"]))
