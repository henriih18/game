"""Final visual polish for L5: console, cooling room body and fan guards."""
import bpy
import math
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
COLL = bpy.data.collections.get("NEXUS_L5_POLISH")
if COLL is None:
    COLL = bpy.data.collections.new("NEXUS_L5_POLISH")
    bpy.context.scene.collection.children.link(COLL)


def mat(name):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        m.diffuse_color = (0.02, 0.03, 0.04, 1.0)
    return m


def principled(name, color, rough=0.6, metallic=0.0, emission=None, strength=0.0):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metallic
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    m.diffuse_color = (*color, 1.0)
    return m


def box(name, center, size, material, bevel=0.006):
    mesh = bpy.data.meshes.new(name)
    x, y, z = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
    verts = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
             (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    COLL.objects.link(o)
    o.location = center
    if material:
        mesh.materials.append(material)
    if bevel > 0:
        md = o.modifiers.new("Bevel", "BEVEL")
        md.width = bevel
        md.segments = 1
    return o


def cyl(name, center, radius, depth, material, axis="Z", verts=20):
    mesh = bpy.data.meshes.new(name)
    vl = []
    for z in (-depth * 0.5, depth * 0.5):
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
    if material:
        mesh.materials.append(material)
    return o


def torus_y(name, center, major, minor, material, seg=32, mseg=6):
    mesh = bpy.data.meshes.new(name)
    verts = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        for j in range(mseg):
            b = 2 * math.pi * j / mseg
            r = major + math.cos(b) * minor
            verts.append((math.cos(a) * r, math.sin(b) * minor, math.sin(a) * r))
    faces = []
    for i in range(seg):
        ni = (i + 1) % seg
        for j in range(mseg):
            nj = (j + 1) % mseg
            faces.append((i * mseg + j, ni * mseg + j, ni * mseg + nj, i * mseg + nj))
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    COLL.objects.link(o)
    o.location = center
    if material:
        mesh.materials.append(material)
    return o


def hide(o):
    if not o:
        return
    o.hide_render = True
    try:
        o.hide_set(True)
    except Exception:
        pass


def assign(name, material):
    o = bpy.data.objects.get(name)
    if o:
        if o.data.materials:
            o.data.materials[0] = material
        else:
            o.data.materials.append(material)


# Materials.
cold_coat = principled("NEXUS_ColdCoat", (0.018, 0.026, 0.036), 0.9)
frost_dark = principled("NEXUS_Frost_Dark", (0.30, 0.40, 0.46), 0.78)
console_teal = principled("NEXUS_Console_Teal", (0.006, 0.030, 0.034), 0.30,
                          emission=(0.0, 0.16, 0.14), strength=0.35)
dark_metal = bpy.data.materials.get("NEXUS_Dark_Metal") or bpy.data.materials.get("NEXUS_Steel")

# Coolant and frost material tuning.
cool = bpy.data.materials.get("NEXUS_Coolant_Spill")
if cool and cool.use_nodes:
    bsdf = next((n for n in cool.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.006, 0.032, 0.052, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.045
frost = bpy.data.materials.get("NEXUS_Frost")
if frost and frost.use_nodes:
    bsdf = next((n for n in frost.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.38, 0.48, 0.54, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.72

# Extraction console: remove the flat emissive bar and rebuild the monitor bank.
for o in bpy.data.objects:
    if o.name.startswith("NEXUS_POLISH_L5_CONSOLE_BEZEL_") or o.name.startswith("NEXUS_POLISH_L5_CONSOLE_BTN_"):
        hide(o)

screen_x = (-4.41, -3.98, -3.55)
for i, x in enumerate(screen_x):
    scr = bpy.data.objects.get(f"NEXUS_LROOM_EXTRACCION_PROFUNDA_PANEL_SCR_{i}")
    if scr:
        scr.location = (x, -12.855, -42.50)
        scr.dimensions = (0.39, 0.05, 0.30)
        scr.data.materials.clear()
        scr.data.materials.append(console_teal)
    # Housing and neck.
    box(f"NEXUS_POLISH_L5_CONSOLE_HOUSING_{i}", (x, -12.80, -42.50),
        (0.46, 0.11, 0.36), dark_metal, 0.008)
    box(f"NEXUS_POLISH_L5_CONSOLE_NECK_{i}", (x, -12.80, -42.685),
        (0.12, 0.12, 0.045), dark_metal, 0.004)
    # Bezel lip around the screen.
    box(f"NEXUS_POLISH_L5_CONSOLE_LIP_T_{i}", (x, -12.845, -42.335),
        (0.45, 0.02, 0.025), dark_metal, 0.003)
    box(f"NEXUS_POLISH_L5_CONSOLE_LIP_B_{i}", (x, -12.845, -42.665),
        (0.45, 0.02, 0.025), dark_metal, 0.003)
    box(f"NEXUS_POLISH_L5_CONSOLE_LIP_L_{i}", (x - 0.225, -12.845, -42.50),
        (0.02, 0.02, 0.34), dark_metal, 0.003)
    box(f"NEXUS_POLISH_L5_CONSOLE_LIP_R_{i}", (x + 0.225, -12.845, -42.50),
        (0.02, 0.02, 0.34), dark_metal, 0.003)

# Rebuild buttons on the real front face of the console (toward the camera/south).
for row, z in enumerate((-42.83, -42.92)):
    for col in range(4):
        box(f"NEXUS_POLISH_L5_CONSOLE_NBTN_{row}_{col}",
            (-4.47 + col * 0.29, -13.465, z), (0.07, 0.02, 0.05),
            bpy.data.materials.get("NEXUS_Amber"), 0.004)

# Cooling units: dark backing, fan blades and an open wire guard.
for o in bpy.data.objects:
    if o.name.startswith("NEXUS_POLISH_L5_COLD_FAN_BAR_"):
        hide(o)

unit_x = (-0.25, 2.0, 4.25)
for i, x in enumerate(unit_x):
    grill = bpy.data.objects.get(f"NEXUS_LROOM_REFRIGERACION_UNIT_GRILL_{i}")
    if grill:
        grill.data.materials.clear()
        grill.data.materials.append(dark_metal)
    # Circular recess and fan blades.
    cyl(f"NEXUS_POLISH_L5_COLD_FAN_DISC_{i}", (x, 14.90, -42.35), 0.40, 0.025,
        bpy.data.materials.get("NEXUS_Grime") or dark_metal, "Y", 28)
    for b in range(5):
        a = 2 * math.pi * b / 5 + 0.25
        bx = x + math.sin(a) * 0.17
        bz = -42.35 + math.cos(a) * 0.17
        blade = box(f"NEXUS_POLISH_L5_COLD_BLADE_{i}_{b}", (bx, 14.865, bz),
                    (0.10, 0.018, 0.26), dark_metal, 0.004)
        blade.rotation_euler.y = a
    # Wire guard: outer ring plus six spokes.
    torus_y(f"NEXUS_POLISH_L5_COLD_GUARD_RING_{i}", (x, 14.84, -42.35),
            0.395, 0.012, dark_metal, 32, 5)
    for s in range(6):
        a = 2 * math.pi * s / 6
        sx = x + math.sin(a) * 0.19
        sz = -42.35 + math.cos(a) * 0.19
        spoke = box(f"NEXUS_POLISH_L5_COLD_GUARD_SPOKE_{i}_{s}", (sx, 14.835, sz),
                    (0.014, 0.012, 0.19), dark_metal, 0.002)
        spoke.rotation_euler.y = a
    # Dark label plate with small amber status lights.
    lab = bpy.data.objects.get(f"NEXUS_POLISH_L5_COLD_UNIT_LABEL_{i}")
    if lab:
        lab.data.materials.clear()
        lab.data.materials.append(dark_metal)
    for l in range(3):
        box(f"NEXUS_POLISH_L5_COLD_STATUS_{i}_{l}",
            (x - 0.18 + l * 0.10, 14.945, -41.62), (0.055, 0.012, 0.045),
            bpy.data.materials.get("NEXUS_Amber"), 0.002)

# Remove the old rectangular frost sheets; replace with irregular thin patches.
for o in bpy.data.objects:
    if o.name.startswith("NEXUS_STORY_COLD_FROST_"):
        hide(o)

frost_spots = [
    (-1.25, 14.25, 0.30), (0.95, 13.75, 0.24), (1.85, 14.55, 0.20),
    (3.35, 14.10, 0.28), (4.85, 13.55, 0.22), (5.20, 10.75, 0.26),
    (4.70, 12.00, 0.18), (-1.75, 12.60, 0.19), (3.80, 10.95, 0.17),
]
for i, (x, y, r) in enumerate(frost_spots):
    cyl(f"NEXUS_POLISH_L5_COLD_FROST_{i}", (x, y, -43.635), r, 0.016,
        frost_dark, "Z", 7)

# Body: remove duplicated head, use a dark cold-weather coat and add a neck.
hide(bpy.data.objects.get("NEXUS_STORY_COLD_HEAD"))
for n in ("NEXUS_STORY_COLD_TORSO", "NEXUS_STORY_COLD_LEGS",
          "NEXUS_POLISH_L5_COLD_SHOULDER_L", "NEXUS_POLISH_L5_COLD_SHOULDER_R",
          "NEXUS_POLISH_L5_COLD_ARM_L", "NEXUS_POLISH_L5_COLD_ARM_R",
          "NEXUS_POLISH_L5_COLD_FOREARM_L", "NEXUS_POLISH_L5_COLD_FOREARM_R",
          "NEXUS_POLISH_L5_COLD_KNEE_L", "NEXUS_POLISH_L5_COLD_KNEE_R"):
    assign(n, cold_coat)
cyl("NEXUS_POLISH_L5_COLD_NECK", (5.47, 12.07, -42.87), 0.095, 0.14,
    bpy.data.materials.get("NEXUS_Skin_Pale"), "Z", 14)
box("NEXUS_POLISH_L5_COLD_COLLAR", (5.47, 12.12, -42.90),
    (0.36, 0.30, 0.10), cold_coat, 0.015)

# Slightly calmer room light so the blue no longer washes the floor.
room = bpy.data.objects.get("REFRIGERACION_LIGHT_AREA")
if room:
    room.data.energy = 240.0
fill = bpy.data.objects.get("NEXUS_FILL_REFRIGERACION")
if fill:
    fill.data.energy = 210.0

bpy.ops.wm.save_as_mainfile(filepath=f"{ROOT}/blender_concept/FM_NEXUS_V05_level1_v79.blend")
print("V79_SAVED")
