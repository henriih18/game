"""Rebuild the cooling-room corpse as one coherent seated body."""
import bpy
import math
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
COLL = bpy.data.collections.get("NEXUS_L5_POLISH")
if COLL is None:
    COLL = bpy.data.collections.new("NEXUS_L5_POLISH")
    bpy.context.scene.collection.children.link(COLL)

coat = bpy.data.materials.get("NEXUS_BodyBag_Arch") or bpy.data.materials.get("NEXUS_Rubber")
skin = bpy.data.materials.get("NEXUS_Skin_Pale")
hair = bpy.data.materials.get("NEXUS_Hair")
boot = bpy.data.materials.get("NEXUS_Rubber")
amber = bpy.data.materials.get("NEXUS_Amber")
dark = bpy.data.materials.get("NEXUS_Dark_Metal") or bpy.data.materials.get("NEXUS_Steel")


def box(name, center, size, material, bevel=0.025, smooth=False):
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
        md.segments = 2
    if smooth:
        for p in mesh.polygons:
            p.use_smooth = True
    return o


def sphere(name, center, radius, material, seg=20, rings=12, scale=(1, 1, 1)):
    mesh = bpy.data.meshes.new(name)
    verts = []
    faces = []
    # Top and bottom poles.
    for r in range(rings + 1):
        phi = math.pi * r / rings
        for s in range(seg):
            th = 2 * math.pi * s / seg
            verts.append((radius * math.sin(phi) * math.cos(th) * scale[0],
                          radius * math.sin(phi) * math.sin(th) * scale[1],
                          radius * math.cos(phi) * scale[2]))
    for r in range(rings):
        for s in range(seg):
            a = r * seg + s
            b = r * seg + (s + 1) % seg
            c = (r + 1) * seg + (s + 1) % seg
            d = (r + 1) * seg + s
            faces.append((a, b, c, d))
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    COLL.objects.link(o)
    o.location = center
    if material:
        mesh.materials.append(material)
    for p in mesh.polygons:
        p.use_smooth = True
    return o


def cyl(name, center, radius, depth, material, verts=14):
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
    if material:
        mesh.materials.append(material)
    return o


def hide(name):
    o = bpy.data.objects.get(name)
    if o:
        o.hide_render = True
        try:
            o.hide_set(True)
        except Exception:
            pass


old_parts = [
    "NEXUS_STORY_COLD_TORSO", "NEXUS_STORY_COLD_LEGS", "NEXUS_STORY_COLD_BOOT_0",
    "NEXUS_STORY_COLD_BOOT_1", "NEXUS_STORY_COLD_FROST_BODY", "NEXUS_STORY_COLD_HEAD",
    "NEXUS_POLISH_L5_COLD_HEAD", "NEXUS_POLISH_L5_COLD_HAIR", "NEXUS_POLISH_L5_COLD_NECK",
    "NEXUS_POLISH_L5_COLD_COLLAR", "NEXUS_POLISH_L5_COLD_COLLAR.001",
    "NEXUS_POLISH_L5_COLD_BADGE", "NEXUS_POLISH_L5_COLD_BELT",
    "NEXUS_POLISH_L5_COLD_ZIP", "NEXUS_POLISH_L5_COLD_SHOULDER_L",
    "NEXUS_POLISH_L5_COLD_SHOULDER_R", "NEXUS_POLISH_L5_COLD_ARM_L",
    "NEXUS_POLISH_L5_COLD_ARM_R", "NEXUS_POLISH_L5_COLD_FOREARM_L",
    "NEXUS_POLISH_L5_COLD_FOREARM_R", "NEXUS_POLISH_L5_COLD_HAND_L",
    "NEXUS_POLISH_L5_COLD_HAND_R", "NEXUS_POLISH_L5_COLD_KNEE_L",
    "NEXUS_POLISH_L5_COLD_KNEE_R",
]
for n in old_parts:
    hide(n)

# Remove paper-like frost sheets and tint the puddles as dark meltwater.
for o in bpy.data.objects:
    if o.name.startswith("NEXUS_POLISH_L5_COLD_FROST_") or o.name.startswith("NEXUS_STORY_COLD_FROST_"):
        o.hide_render = True
        try:
            o.hide_set(True)
        except Exception:
            pass
    if o.name.startswith("NEXUS_STORY_COLD_SPILL_"):
        o.data.materials.clear()
        o.data.materials.append(bpy.data.materials.get("NEXUS_Meltwater"))

# Seated body, back against east wall, legs toward the room.
box("NEXUS_BODY_COLD_PELVIS", (5.55, 13.0, -43.44), (0.46, 0.42, 0.22), coat, 0.04)
box("NEXUS_BODY_COLD_TORSO", (5.55, 13.0, -43.10), (0.40, 0.52, 0.58), coat, 0.05)
box("NEXUS_BODY_COLD_SHOULDERS", (5.55, 13.0, -42.84), (0.36, 0.58, 0.16), coat, 0.04)
cyl("NEXUS_BODY_COLD_NECK", (5.55, 13.0, -42.76), 0.075, 0.14, skin)
sphere("NEXUS_BODY_COLD_HEAD", (5.55, 13.0, -42.62), 0.13, skin, 20, 12)
sphere("NEXUS_BODY_COLD_HAIR", (5.55, 13.02, -42.585), 0.132, hair, 20, 10, (1, 1, 0.62))
# Face points west.
box("NEXUS_BODY_COLD_EYE_L", (5.423, 12.952, -42.615), (0.012, 0.033, 0.018), dark, 0.002)
box("NEXUS_BODY_COLD_EYE_R", (5.423, 13.048, -42.615), (0.012, 0.033, 0.018), dark, 0.002)
box("NEXUS_BODY_COLD_NOSE", (5.415, 13.0, -42.648), (0.025, 0.03, 0.045), skin, 0.005)
# Arms hanging at the sides, hands beside the hips.
for side, y in (("L", 12.68), ("R", 13.32)):
    box(f"NEXUS_BODY_COLD_UPPERARM_{side}", (5.55, y, -43.04), (0.135, 0.14, 0.42), coat, 0.03)
    box(f"NEXUS_BODY_COLD_FOREARM_{side}", (5.57, y, -43.34), (0.12, 0.13, 0.30), coat, 0.03)
    box(f"NEXUS_BODY_COLD_HAND_{side}", (5.57, y, -43.54), (0.11, 0.12, 0.11), skin, 0.025)
# Legs extended forward (west), feet near the camera.
for side, y in (("L", 12.87), ("R", 13.13)):
    box(f"NEXUS_BODY_COLD_THIGH_{side}", (5.15, y, -43.48), (0.68, 0.19, 0.22), coat, 0.035)
    box(f"NEXUS_BODY_COLD_KNEE_{side}", (4.79, y, -43.46), (0.18, 0.20, 0.22), coat, 0.035)
    box(f"NEXUS_BODY_COLD_SHIN_{side}", (4.49, y, -43.50), (0.48, 0.17, 0.18), coat, 0.03)
    box(f"NEXUS_BODY_COLD_BOOT_{side}", (4.16, y, -43.56), (0.30, 0.18, 0.14), boot, 0.03)
# Coat skirt and details.
box("NEXUS_BODY_COLD_SKIRT", (5.18, 13.0, -43.36), (0.64, 0.46, 0.08), coat, 0.03)
box("NEXUS_BODY_COLD_ZIP", (5.345, 13.0, -43.09), (0.012, 0.022, 0.50), dark, 0.002)
box("NEXUS_BODY_COLD_BADGE", (5.33, 12.86, -43.04), (0.015, 0.08, 0.06), amber, 0.003)
box("NEXUS_BODY_COLD_BELT", (5.55, 13.0, -43.40), (0.44, 0.46, 0.06), dark, 0.01)
# Thin frost on one shoulder.
box("NEXUS_BODY_COLD_FROST", (5.38, 13.10, -42.795), (0.14, 0.12, 0.018),
    bpy.data.materials.get("NEXUS_ColdGlass") or bpy.data.materials.get("NEXUS_Clinical"), 0.004)

bpy.ops.wm.save_as_mainfile(filepath=f"{ROOT}/blender_concept/FM_NEXUS_V05_level1_v81.blend")
print("V81_SAVED")
