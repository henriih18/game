"""Narrative and functional detail for the remaining L4 rooms."""
import bpy
import math
import os

ROOT = "/home/riyo/Documentos/game"
Z = -32.8
C = bpy.data.collections.get("NEXUS_STORY_LOWER")


def mat(name, fallback="NEXUS_Painted_Metal"):
    return bpy.data.materials.get(name) or bpy.data.materials.get(fallback)


def box(name, center, size, material, bevel=0.006):
    me = bpy.data.meshes.new(name)
    x, y, z = size[0] / 2, size[1] / 2, size[2] / 2
    v = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
         (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    f = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    me.from_pydata(v, [], f)
    me.update()
    o = bpy.data.objects.new(name, me)
    C.objects.link(o)
    o.location = center
    mm = mat(material)
    if mm:
        me.materials.append(mm)
    if bevel > 0:
        md = o.modifiers.new("Bevel", "BEVEL")
        md.width = bevel
        md.segments = 1
    return o


def cyl(name, center, radius, depth, material, verts=20):
    me = bpy.data.meshes.new(name)
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
    me.from_pydata(vl, [], fs)
    me.update()
    o = bpy.data.objects.new(name, me)
    C.objects.link(o)
    o.location = center
    mm = mat(material)
    if mm:
        me.materials.append(mm)
    return o


def plate_sign(name, center, size, axis="Y"):
    if axis == "Y":
        box(name, center, size, "NEXUS_SignPlate", 0.004)
        box(name + "_STRIP", (center[0], center[1] - 0.01 if size[1] < 0.1 else center[1], center[2] + size[2] * 0.32),
            (size[0] * 0.82, 0.012, 0.05), "NEXUS_Amber", 0.002)
    else:
        box(name, center, size, "NEXUS_SignPlate", 0.004)
        box(name + "_STRIP", (center[0] - 0.01 if size[0] < 0.1 else center[0], center[1], center[2] + size[2] * 0.32),
            (0.012, size[1] * 0.82, 0.05), "NEXUS_Amber", 0.002)


# ---------------------------------------------------------------- CONTENCION_SECUNDARIA
# Leak and drag trail from the right-hand cylinder.
for i, (x, y, r) in enumerate(((18.0, -5.55, 0.82), (17.2, -5.95, 0.55), (16.3, -6.2, 0.42), (15.4, -6.55, 0.32))):
    cyl(f"NEXUS_STORY_SEC_GOO_{i}", (x, y, Z + 0.160), r, 0.018, "NEXUS_Green")
for i, (x, y, r) in enumerate(((17.9, -5.35, 0.24), (18.25, -4.95, 0.2), (18.4, -4.55, 0.17))):
    cyl(f"NEXUS_STORY_SEC_DRIP_{i}", (x, y, Z + 0.158), r, 0.014, "NEXUS_Green")

# Broken restraint straps around the left cylinder.
for i, (x, y) in enumerate(((12.55, -3.05), (12.8, -2.65), (13.1, -2.35))):
    box(f"NEXUS_STORY_SEC_STRAP_{i}", (x, y, Z + 0.1625), (0.12, 1.05, 0.025), "NEXUS_Rubber", 0.004)

# Emergency decon shower in the north-east corner.
cyl("NEXUS_STORY_SEC_SHOWER_PIPE", (20.35, -0.85, Z + 1.45), 0.075, 2.6, "NEXUS_Steel")
box("NEXUS_STORY_SEC_SHOWER_HEAD", (20.35, -0.85, Z + 2.65), (0.38, 0.38, 0.06), "NEXUS_Steel", 0.02)
box("NEXUS_STORY_SEC_SHOWER_RAIL", (20.05, -1.55, Z + 2.2), (0.04, 1.3, 0.04), "NEXUS_Steel", 0.004)
box("NEXUS_STORY_SEC_SHOWER_CURTAIN", (19.55, -1.55, Z + 1.25), (0.02, 0.92, 1.8), "NEXUS_Curtain", 0.002)
box("NEXUS_STORY_SEC_SHOWER_DRAIN", (20.2, -0.9, Z + 0.160), (0.62, 0.62, 0.02), "NEXUS_Steel", 0.006)
plate_sign("NEXUS_STORY_SEC_SIGN", (14.2, -0.155, Z + 2.35), (1.7, 0.05, 0.38))
box("NEXUS_STORY_SEC_HOOK", (20.1, -1.05, Z + 1.7), (0.1, 0.06, 0.16), "NEXUS_Steel", 0.004)

# Tipped tool cart and scattered kit near the console.
box("NEXUS_STORY_SEC_CART_TOP", (16.9, -1.55, Z + 0.46), (0.85, 0.55, 0.06), "NEXUS_Steel", 0.006)
box("NEXUS_STORY_SEC_CART_SHELF", (16.9, -1.55, Z + 0.18), (0.78, 0.5, 0.04), "NEXUS_Steel", 0.004)
for i, (x, y) in enumerate(((16.55, -1.8), (17.25, -1.8), (16.55, -1.3), (17.25, -1.3))):
    cyl(f"NEXUS_STORY_SEC_CART_WHEEL_{i}", (x, y, Z + 0.21), 0.06, 0.05, "NEXUS_Rubber", 12)
box("NEXUS_STORY_SEC_CART_BOX", (16.9, -1.55, Z + 0.58), (0.4, 0.32, 0.18), "NEXUS_Clinical", 0.01)
box("NEXUS_STORY_SEC_CART_TOOL", (17.25, -1.5, Z + 0.5), (0.18, 0.04, 0.03), "NEXUS_Steel", 0.002)

# Console clutter.
box("NEXUS_STORY_SEC_PAPERS", (15.3, -7.25, Z + 1.13), (0.4, 0.3, 0.02), "NEXUS_OffWhite", 0.002)
box("NEXUS_STORY_SEC_CLIP", (15.9, -7.45, Z + 1.14), (0.22, 0.3, 0.02), "NEXUS_OffWhite", 0.002)
box("NEXUS_STORY_SEC_LOOT", (17.35, -7.3, Z + 1.18), (0.36, 0.26, 0.18), "NEXUS_Clinical", 0.012)
box("NEXUS_STORY_SEC_LOOT_LID", (17.35, -7.3, Z + 1.28), (0.38, 0.28, 0.03), "NEXUS_Amber", 0.004)
box("NEXUS_STORY_SEC_LOOT_TAG", (17.35, -7.44, Z + 1.13), (0.16, 0.02, 0.06), "NEXUS_OffWhite", 0.002)

# Blood drag marks toward the west door.
for i, (x, y, r) in enumerate(((13.0, -4.7, 0.26), (12.4, -4.75, 0.3), (11.9, -4.65, 0.22), (11.5, -4.5, 0.18))):
    cyl(f"NEXUS_STORY_SEC_BLOOD_{i}", (x, y, Z + 0.158), r, 0.016, "NEXUS_Blood_Dried")
box("NEXUS_STORY_SEC_HANDPRINT", (11.18, -2.7, Z + 1.05), (0.24, 0.02, 0.3), "NEXUS_Blood_Dried", 0.002)

# ---------------------------------------------------------------- CONTROL_CONTENCION
# Desk equipment.
for i, x in enumerate((-16.15, -14.85)):
    box(f"NEXUS_STORY_CTRL_KEYBOARD_{i}", (x, -0.28, Z + 1.055), (0.45, 0.17, 0.03), "NEXUS_Rubber", 0.004)
box("NEXUS_STORY_CTRL_PHONE", (-17.0, -0.55, Z + 1.07), (0.22, 0.18, 0.06), "NEXUS_Rubber", 0.012)
box("NEXUS_STORY_CTRL_RADIO", (-14.2, -0.55, Z + 1.10), (0.18, 0.12, 0.12), "NEXUS_Rubber", 0.01)
box("NEXUS_STORY_CTRL_MUG", (-16.9, -0.05, Z + 1.095), (0.09, 0.09, 0.11), "NEXUS_OffWhite", 0.02)
box("NEXUS_STORY_CTRL_PAPERS", (-15.4, -0.65, Z + 1.05), (0.38, 0.28, 0.02), "NEXUS_OffWhite", 0.002)
box("NEXUS_STORY_CTRL_LOOT", (-14.75, -0.7, Z + 1.055), (0.24, 0.16, 0.03), "NEXUS_Amber", 0.006)

# Status board on the west wall.
box("NEXUS_STORY_CTRL_BOARD", (-19.84, 0.0, Z + 2.3), (0.05, 2.6, 1.25), "NEXUS_SignPlate", 0.006)
for i in range(5):
    for j in range(3):
        m = ("NEXUS_Red", "NEXUS_Amber", "NEXUS_Screen")[(i + j) % 3]
        box(f"NEXUS_STORY_CTRL_LED_{i}_{j}", (-19.79, -1.0 + j * 0.95, Z + 2.72 - i * 0.19),
            (0.02, 0.16, 0.08), m, 0.002)
box("NEXUS_STORY_CTRL_BOARD_LABEL", (-19.78, 0.0, Z + 1.8), (0.02, 2.2, 0.16), "NEXUS_Amber", 0.002)

# Alarm panel and extinguisher near the east door.
box("NEXUS_STORY_CTRL_ALARM", (-12.6, -3.83, Z + 2.15), (0.55, 0.06, 0.75), "NEXUS_Painted_Metal", 0.008)
box("NEXUS_STORY_CTRL_ALARM_BUTTON", (-12.6, -3.79, Z + 2.3), (0.13, 0.03, 0.13), "NEXUS_Red", 0.006)
box("NEXUS_STORY_CTRL_ALARM_LABEL", (-12.6, -3.79, Z + 1.88), (0.38, 0.02, 0.1), "NEXUS_Amber", 0.002)
cyl("NEXUS_STORY_CTRL_EXT", (-11.7, -2.85, Z + 0.45), 0.13, 0.6, "NEXUS_Extinguisher_Red", 16)
box("NEXUS_STORY_CTRL_EXT_HANDLE", (-11.7, -2.85, Z + 0.80), (0.06, 0.06, 0.14), "NEXUS_Rubber", 0.004)

# Overturned chair, blood smear and drag trail.
box("NEXUS_STORY_CTRL_CHAIR_SEAT", (-13.7, -2.35, Z + 0.71), (0.52, 0.52, 0.08), "NEXUS_Rubber", 0.02)
for i, (x, y) in enumerate(((-13.95, -2.6), (-13.45, -2.6), (-13.95, -2.1), (-13.45, -2.1))):
    box(f"NEXUS_STORY_CTRL_CHAIR_LEG_{i}", (x, y, Z + 0.26), (0.04, 0.04, 0.52), "NEXUS_Steel", 0.002)
box("NEXUS_STORY_CTRL_BLOOD_DESK", (-15.2, -0.85, Z + 1.046), (0.5, 0.22, 0.012), "NEXUS_Blood_Dried", 0.002)
for i, (x, y, r) in enumerate(((-14.9, -1.4, 0.24), (-14.3, -1.9, 0.3), (-13.7, -2.2, 0.22))):
    cyl(f"NEXUS_STORY_CTRL_BLOOD_{i}", (x, y, Z + 0.157), r, 0.014, "NEXUS_Blood_Dried")

# ---------------------------------------------------------------- LAB_RESTRINGIDO
# Monitor stand to the floor.
box("NEXUS_STORY_LAB_MON_BASE", (15.5, 5.3, Z + 0.18), (0.5, 0.4, 0.06), "NEXUS_Steel", 0.006)
cyl("NEXUS_STORY_LAB_MON_POLE", (15.5, 5.3, Z + 0.86), 0.04, 1.3, "NEXUS_Steel", 12)
box("NEXUS_STORY_LAB_MON_COLLAR", (15.5, 5.3, Z + 1.3), (0.12, 0.1, 0.08), "NEXUS_Steel", 0.004)

# Two lab stools.
for i, (x, y) in enumerate(((14.45, 3.95), (16.55, 3.95))):
    box(f"NEXUS_STORY_LAB_STOOL_SEAT_{i}", (x, y, Z + 0.88), (0.46, 0.46, 0.06), "NEXUS_Rubber", 0.03)
    for j, (dx, dy) in enumerate(((-0.17, -0.17), (0.17, -0.17), (-0.17, 0.17), (0.17, 0.17))):
        box(f"NEXUS_STORY_LAB_STOOL_LEG_{i}_{j}", (x + dx, y + dy, Z + 0.50), (0.04, 0.04, 0.7), "NEXUS_Steel", 0.002)

# Mobile lab cart.
box("NEXUS_STORY_LAB_CART_TOP", (13.15, 5.05, Z + 0.86), (1.0, 0.62, 0.06), "NEXUS_Steel", 0.006)
box("NEXUS_STORY_LAB_CART_SHELF", (13.15, 5.05, Z + 0.42), (0.94, 0.58, 0.04), "NEXUS_Steel", 0.004)
for i, (x, y) in enumerate(((12.75, 4.82), (13.55, 4.82), (12.75, 5.28), (13.55, 5.28))):
    cyl(f"NEXUS_STORY_LAB_CART_WHEEL_{i}", (x, y, Z + 0.21), 0.06, 0.05, "NEXUS_Rubber", 12)
box("NEXUS_STORY_LAB_CART_BOX", (13.15, 5.05, Z + 1.0), (0.36, 0.28, 0.18), "NEXUS_Clinical", 0.01)

# Bench instruments.
box("NEXUS_STORY_LAB_SCOPE_BASE", (14.75, 2.9, Z + 1.115), (0.26, 0.22, 0.05), "NEXUS_Steel", 0.006)
cyl("NEXUS_STORY_LAB_SCOPE_ARM", (14.75, 3.05, Z + 1.29), 0.035, 0.3, "NEXUS_Steel", 12)
box("NEXUS_STORY_LAB_SCOPE_HEAD", (14.75, 3.1, Z + 1.46), (0.12, 0.16, 0.1), "NEXUS_Steel", 0.006)
box("NEXUS_STORY_LAB_RACK", (16.25, 2.95, Z + 1.14), (0.3, 0.16, 0.1), "NEXUS_Clinical", 0.004)
for i in range(6):
    cyl(f"NEXUS_STORY_LAB_VIAL_{i}", (16.1 + (i % 3) * 0.11, 2.92 + (i // 3) * 0.06, Z + 1.25), 0.022, 0.12,
        "NEXUS_Glass", 10)
for i, x in enumerate((15.1, 15.45, 16.9)):
    cyl(f"NEXUS_STORY_LAB_BOTTLE_{i}", (x, 2.85, Z + 1.17), 0.055, 0.16, "NEXUS_Amber", 12)
box("NEXUS_STORY_LAB_NOTEBOOK", (17.0, 2.95, Z + 1.10), (0.26, 0.2, 0.02), "NEXUS_OffWhite", 0.002)

# Chemical spill and broken glass.
cyl("NEXUS_STORY_LAB_SPILL", (17.4, 4.35, Z + 0.160), 0.62, 0.02, "NEXUS_Green", 24)
for i, (x, y) in enumerate(((17.0, 4.0), (17.65, 4.3), (17.3, 4.7), (17.8, 4.75), (16.95, 4.55))):
    box(f"NEXUS_STORY_LAB_GLASS_{i}", (x, y, Z + 0.1625), (0.1, 0.06, 0.012), "NEXUS_Glass", 0.002)
box("NEXUS_STORY_LAB_HOOD_CRACK", (18.2, 6.25, Z + 1.7), (0.5, 0.02, 0.4), "NEXUS_Grime", 0.002)

# Incubator fridge.
box("NEXUS_STORY_LAB_FRIDGE", (18.8, 1.35, Z + 1.05), (1.0, 0.7, 1.8), "NEXUS_Clinical", 0.02)
box("NEXUS_STORY_LAB_FRIDGE_DOOR", (18.8, 1.71, Z + 1.10), (0.88, 0.04, 1.5), "NEXUS_Painted_Metal", 0.006)
box("NEXUS_STORY_LAB_FRIDGE_HANDLE", (19.15, 1.75, Z + 1.15), (0.04, 0.06, 0.35), "NEXUS_Steel", 0.004)
box("NEXUS_STORY_LAB_FRIDGE_DISPLAY", (18.8, 1.74, Z + 1.80), (0.24, 0.02, 0.1), "NEXUS_Screen", 0.002)

# Eyewash station on the north wall.
box("NEXUS_STORY_LAB_EYE_BASIN", (13.9, 8.18, Z + 1.05), (0.5, 0.35, 0.12), "NEXUS_Steel", 0.01)
cyl("NEXUS_STORY_LAB_EYE_PIPE", (13.9, 8.32, Z + 0.65), 0.04, 0.8, "NEXUS_Steel", 10)
box("NEXUS_STORY_LAB_EYE_SIGN", (13.9, 8.32, Z + 1.75), (0.32, 0.05, 0.28), "NEXUS_SignPlate", 0.004)

# Loot vial and paperwork.
box("NEXUS_STORY_LAB_LOOT", (16.7, 2.85, Z + 1.17), (0.16, 0.12, 0.16), "NEXUS_Clinical", 0.008)
box("NEXUS_STORY_LAB_LOOT_CAP", (16.7, 2.85, Z + 1.26), (0.18, 0.14, 0.03), "NEXUS_Amber", 0.004)
box("NEXUS_STORY_LAB_PAPERS", (14.2, 3.1, Z + 1.10), (0.35, 0.26, 0.02), "NEXUS_OffWhite", 0.002)

# Balance the room light to a cool work tone.
for n in ("CONTROL_CONTENCION_LIGHT_AREA", "LAB_RESTRINGIDO_LIGHT_AREA", "CONTENCION_SECUNDARIA_LIGHT_AREA"):
    o = bpy.data.objects.get(n)
    if o and o.type == "LIGHT":
        o.data.color = (0.72, 0.82, 1.0)
        o.data.energy = 320.0

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "blender_concept", "FM_NEXUS_V05_level1_v65.blend"))
print("STORY_L4_REST_DONE")
