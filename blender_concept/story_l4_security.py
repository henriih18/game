"""Narrative detail for ARMERIA_HERRAMIENTAS and BUNKER_SEGURIDAD (L4)."""
import bpy
import math

ROOT = "/home/riyo/Documentos/game"
COLL = bpy.data.collections.get("NEXUS_STORY_LOWER")
if COLL is None:
    COLL = bpy.data.collections.get("NEXUS_STORY_L4")
    if COLL is None:
        COLL = bpy.data.collections.new("NEXUS_STORY_L4")
        bpy.context.scene.collection.children.link(COLL)


def mat(name):
    return bpy.data.materials.get(name)


def box(name, center, size, material, bevel=0.006):
    mesh = bpy.data.meshes.new(name)
    x, y, z = size[0] / 2, size[1] / 2, size[2] / 2
    verts = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
             (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
             (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    COLL.objects.link(o)
    o.location = center
    m = mat(material)
    if m:
        mesh.materials.append(m)
    if bevel > 0:
        md = o.modifiers.new("Bevel", "BEVEL")
        md.width = bevel
        md.segments = 1
    return o


def cyl(name, center, radius, depth, material, axis="Z", verts=12):
    mesh = bpy.data.meshes.new(name)
    vl = []
    for z in (-depth / 2, depth / 2):
        for i in range(verts):
            a = 2 * math.pi * i / verts
            vl.append((math.cos(a) * radius, math.sin(a) * radius, z))
    fs = []
    for i in range(verts):
        j = (i + 1) % verts
        fs.append((i, j, verts + j, verts + i))
    fs.append(tuple(range(verts - 1, -1, -1)))
    fs.append(tuple(range(verts, verts * 2)))
    mesh.from_pydata(vl, [], fs)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    COLL.objects.link(o)
    o.location = center
    if axis == "X":
        o.rotation_euler.y = math.pi / 2
    elif axis == "Y":
        o.rotation_euler.x = math.pi / 2
    m = mat(material)
    if m:
        mesh.materials.append(m)
    return o


# ---------- ARMERIA_HERRAMIENTAS (x -11..-3, y 9..16) ----------
# Central work table with disassembled equipment.
box("NEXUS_STORY_ARM_TABLE_TOP", (-7.0, 13.2, -31.75), (2.6, 1.15, 0.09), "NEXUS_Steel", 0.01)
for i, (dx, dy) in enumerate(((-1.2, -0.48), (1.2, -0.48), (-1.2, 0.48), (1.2, 0.48))):
    box(f"NEXUS_STORY_ARM_TABLE_LEG_{i}", (-7.0 + dx, 13.2 + dy, -32.2),
        (0.07, 0.07, 0.9), "NEXUS_Painted_Metal")
box("NEXUS_STORY_ARM_VISE", (-7.9, 13.2, -31.55), (0.28, 0.22, 0.22), "NEXUS_Rusted_Metal", 0.02)
box("NEXUS_STORY_ARM_PART_0", (-6.6, 13.05, -31.63), (0.55, 0.32, 0.12), "NEXUS_Steel", 0.02)
box("NEXUS_STORY_ARM_PART_1", (-6.1, 13.45, -31.66), (0.25, 0.18, 0.08), "NEXUS_Rusted_Metal", 0.01)
box("NEXUS_STORY_ARM_TOOLBOX", (-7.0, 13.65, -31.56), (0.62, 0.32, 0.2), "NEXUS_Red_Matte", 0.02)
box("NEXUS_STORY_ARM_TOOLBOX_LID", (-7.0, 13.82, -31.48), (0.62, 0.06, 0.16), "NEXUS_Red_Matte", 0.015)
for i, x in enumerate((-7.25, -7.0, -6.75)):
    box(f"NEXUS_STORY_ARM_SCREW_{i}", (x, 13.55, -31.48), (0.04, 0.12, 0.04), "NEXUS_Steel", 0.005)
box("NEXUS_STORY_ARM_LOOT", (-8.35, 13.15, -31.52), (0.42, 0.3, 0.24), "NEXUS_Steel", 0.02)
box("NEXUS_STORY_ARM_LOOT_TAG", (-8.35, 13.31, -31.42), (0.18, 0.02, 0.07), "NEXUS_Amber", 0.004)

# Wall tool board (east wall).
box("NEXUS_STORY_ARM_BOARD", (-3.18, 13.4, -30.9), (0.06, 2.2, 1.2), "NEXUS_Painted_Metal", 0.01)
for i, (yy, zz, w, h) in enumerate(((-0.7, 0.25, 0.05, 0.55), (-0.35, 0.1, 0.06, 0.7),
                                     (0.0, 0.28, 0.08, 0.42), (0.42, 0.05, 0.05, 0.8),
                                     (0.75, 0.22, 0.06, 0.5))):
    box(f"NEXUS_STORY_ARM_TOOL_{i}", (-3.14, 13.4 + yy, -30.9 + zz),
        (0.035, w, h), "NEXUS_Steel", 0.004)
box("NEXUS_STORY_ARM_TAPE", (-3.15, 13.0, -30.55), (0.03, 0.18, 0.18), "NEXUS_Amber", 0.004)

# Battery charging rack (west wall).
box("NEXUS_STORY_ARM_CHARGE", (-10.82, 13.6, -31.8), (0.28, 1.4, 1.7), "NEXUS_Painted_Metal", 0.01)
for i, yy in enumerate((13.15, 13.6, 14.05)):
    box(f"NEXUS_STORY_ARM_BATT_{i}", (-10.62, yy, -31.35), (0.18, 0.3, 0.22), "NEXUS_Rubber", 0.02)
    box(f"NEXUS_STORY_ARM_BATT_LED_{i}", (-10.52, yy + 0.1, -31.27), (0.02, 0.04, 0.03), "NEXUS_Amber", 0.002)

# Overturned cart and scattered gear near the door.
box("NEXUS_STORY_ARM_CART", (-4.4, 10.3, -32.35), (0.8, 1.2, 0.45), "NEXUS_Steel", 0.02)
cyl("NEXUS_STORY_ARM_CART_WHEEL_0", (-4.1, 9.8, -32.55), 0.1, 0.06, "NEXUS_Rubber", "X")
cyl("NEXUS_STORY_ARM_CART_WHEEL_1", (-4.1, 10.8, -32.55), 0.1, 0.06, "NEXUS_Rubber", "X")
box("NEXUS_STORY_ARM_HELMET", (-6.4, 9.6, -32.5), (0.28, 0.3, 0.16), "NEXUS_Amber", 0.04)
box("NEXUS_STORY_ARM_GLOVE", (-6.0, 9.9, -32.61), (0.18, 0.28, 0.04), "NEXUS_Rubber", 0.01)
box("NEXUS_STORY_ARM_CASE", (-8.8, 9.6, -32.45), (0.65, 0.35, 0.3), "NEXUS_Steel", 0.02)

# Blood trail from the bench toward the door and a body partly under the bench.
for i, yy in enumerate((11.6, 11.1, 10.55, 10.0, 9.5)):
    box(f"NEXUS_STORY_ARM_BLOOD_{i}", (-7.35, yy, -32.63), (0.28, 0.38, 0.02),
        "NEXUS_Blood_Dried", 0.002)
box("NEXUS_STORY_ARM_BODY", (-6.15, 10.95, -32.45), (0.55, 1.35, 0.22), "NEXUS_Rubber", 0.04)
box("NEXUS_STORY_ARM_BODY_HEAD", (-6.15, 10.25, -32.48), (0.26, 0.3, 0.24), "NEXUS_Skin_Pale", 0.04)
box("NEXUS_STORY_ARM_HANDPRINT", (-8.9, 9.02, -31.5), (0.16, 0.02, 0.24), "NEXUS_Blood_Dried", 0.002)

# ---------- BUNKER_SEGURIDAD (x -3..6, y 9..17) ----------
# Monitor bank on the back wall (north).
for i, (xx, zz) in enumerate(((0.1, -30.6), (1.1, -30.6), (2.1, -30.6), (3.1, -30.6),
                               (0.6, -31.35), (1.6, -31.35), (2.6, -31.35))):
    box(f"NEXUS_STORY_BUNK_MON_{i}", (xx, 16.86, zz), (0.72, 0.06, 0.5), "NEXUS_MonitorScreen", 0.006)
    box(f"NEXUS_STORY_BUNK_MON_BEZEL_{i}", (xx, 16.82, zz), (0.82, 0.04, 0.6), "NEXUS_Painted_Metal", 0.004)
box("NEXUS_STORY_BUNK_MON_FRAME", (1.6, 16.9, -30.9), (3.6, 0.06, 1.5), "NEXUS_Steel", 0.008)

# Map board on the east wall with marked routes.
box("NEXUS_STORY_BUNK_MAP", (5.82, 13.0, -30.9), (0.06, 2.4, 1.3), "NEXUS_OffWhite", 0.008)
for i, (yy, zz, w, h) in enumerate(((12.2, -30.55, 1.4, 0.035), (13.6, -31.15, 1.0, 0.03),
                                     (12.9, -30.9, 0.03, 0.7))):
    box(f"NEXUS_STORY_BUNK_MAP_RED_{i}", (5.78, yy, zz), (0.02, w, h), "NEXUS_Red_Matte", 0.002)
box("NEXUS_STORY_BUNK_MAP_MARK", (5.78, 13.9, -30.45), (0.02, 0.12, 0.12), "NEXUS_Amber", 0.002)

# Console extras: radio, phone, papers, cups, laptop.
box("NEXUS_STORY_BUNK_RADIO", (0.35, 11.28, -31.55), (0.4, 0.3, 0.16), "NEXUS_Rubber", 0.015)
box("NEXUS_STORY_BUNK_RADIO_FACE", (0.35, 11.42, -31.55), (0.3, 0.02, 0.1), "NEXUS_Screen", 0.004)
cyl("NEXUS_STORY_BUNK_ANT", (0.55, 11.28, -31.25), 0.012, 0.45, "NEXUS_Steel", "Z", 8)
box("NEXUS_STORY_BUNK_PHONE", (2.55, 11.25, -31.62), (0.24, 0.18, 0.08), "NEXUS_Rubber", 0.02)
box("NEXUS_STORY_BUNK_PAPERS", (1.2, 11.2, -31.68), (0.42, 0.3, 0.02), "NEXUS_Paper", 0.002)
box("NEXUS_STORY_BUNK_CLIP", (1.2, 11.2, -31.66), (0.12, 0.08, 0.02), "NEXUS_Steel", 0.002)
cyl("NEXUS_STORY_BUNK_CUP", (2.9, 11.18, -31.62), 0.05, 0.1, "NEXUS_OffWhite", "Z", 12)
box("NEXUS_STORY_BUNK_KEYCARD", (1.9, 11.2, -31.67), (0.09, 0.14, 0.012), "NEXUS_Amber", 0.002)
box("NEXUS_STORY_BUNK_KEYCARD_LABEL", (1.9, 11.2, -31.662), (0.06, 0.04, 0.002), "NEXUS_SignText", 0.0)

# Overturned chair, barricade crates, blood and claw marks.
box("NEXUS_STORY_BUNK_CHAIR_SEAT", (2.9, 12.4, -32.32), (0.55, 0.55, 0.08), "NEXUS_Rubber", 0.03)
box("NEXUS_STORY_BUNK_CHAIR_BACK", (2.9, 12.68, -31.98), (0.55, 0.08, 0.55), "NEXUS_Rubber", 0.03)
for i, (dx, dy) in enumerate(((-0.2, -0.2), (0.2, -0.2), (-0.2, 0.2), (0.2, 0.2))):
    box(f"NEXUS_STORY_BUNK_CHAIR_LEG_{i}", (2.9 + dx, 12.4 + dy, -32.55),
        (0.04, 0.04, 0.3), "NEXUS_Steel")
box("NEXUS_STORY_BUNK_CRATE_0", (-2.0, 12.2, -32.2), (0.8, 0.8, 0.8), "NEXUS_Debris", 0.03)
box("NEXUS_STORY_BUNK_CRATE_1", (-2.0, 12.2, -31.35), (0.7, 0.7, 0.7), "NEXUS_Debris", 0.03)
box("NEXUS_STORY_BUNK_CRATE_2", (4.6, 9.9, -32.2), (0.75, 0.75, 0.8), "NEXUS_Debris", 0.03)
box("NEXUS_STORY_BUNK_BLOOD", (2.2, 11.9, -32.63), (0.8, 0.45, 0.02), "NEXUS_Blood_Dried", 0.002)
for i, xx in enumerate((3.55, 3.75, 3.95)):
    box(f"NEXUS_STORY_BUNK_CLAW_{i}", (xx, 9.02, -31.0 + i * 0.18),
        (0.035, 0.02, 0.55), "NEXUS_Blood_Dried", 0.002)

# Emergency red light and wall sign.
box("NEXUS_STORY_BUNK_BEACON_HOUSE", (5.7, 9.3, -30.75), (0.16, 0.22, 0.16), "NEXUS_Painted_Metal", 0.01)
box("NEXUS_STORY_BUNK_BEACON_LENS", (5.78, 9.3, -30.75), (0.04, 0.16, 0.12), "NEXUS_Red", 0.01)
box("NEXUS_STORY_BUNK_SIGN", (-2.86, 11.5, -30.6), (0.06, 1.8, 0.3), "NEXUS_SignPlate", 0.006)

ld = bpy.data.lights.new("NEXUS_STORY_BUNK_RED", "POINT")
ld.color = (1.0, 0.06, 0.04)
ld.energy = 55.0
ld.shadow_soft_size = 0.3
lo = bpy.data.objects.new(ld.name, ld)
COLL.objects.link(lo)
lo.location = (5.4, 9.8, -30.6)

bpy.ops.wm.save_as_mainfile(filepath=ROOT + "/blender_concept/FM_NEXUS_V05_level1_v61.blend")
print("STORY_L4_SECURITY_DONE", len(COLL.objects))
