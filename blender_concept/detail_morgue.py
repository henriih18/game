"""Morgue storage wall, sink and readable body bags (L3)."""
import bpy
import math
from mathutils import Vector

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


def cyl(name, center, radius, depth, material, axis="Z", verts=12):
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


# Dark satin body-bag material.
bag = bpy.data.materials.get("NEXUS_BodyBag")
if bag is None:
    bag = bpy.data.materials.new("NEXUS_BodyBag")
    bag.use_nodes = True
    bsdf = next(n for n in bag.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (0.035, 0.040, 0.046, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.42
    bsdf.inputs["Metallic"].default_value = 0.0

for i in range(4):
    obj = bpy.data.objects.get(f"NEXUS_LROOM_MORGUE_BAG_{i}")
    if obj:
        obj.data.materials.clear()
        obj.data.materials.append(bag)
    # Zipper and pull along the bag.
    y = 3.06 if i in (0, 1) else 5.94
    x = 13.24 if i in (0, 2) else 16.76
    box(f"NEXUS_STORY_MORGUE_ZIP_{i}", (x, y, -21.90), (0.035, 1.72, 0.012), "NEXUS_Steel", 0.002)
    box(f"NEXUS_STORY_MORGUE_ZIPPULL_{i}", (x + 0.03, y - 0.82, -21.88), (0.05, 0.10, 0.02), "NEXUS_Steel", 0.002)
    box(f"NEXUS_STORY_MORGUE_FOOTAG_{i}", (x, y - 0.99, -21.89), (0.11, 0.13, 0.012), "NEXUS_Paper", 0.0)

# Refrigerated drawer bank on the north wall (x 12..18, y 8.0).
for col, x in enumerate((12.35, 15.65)):
    for row, z in enumerate((-22.0, -21.28, -20.56)):
        name = f"NEXUS_STORY_MORGUE_DRAWER_{col}_{row}"
        box(name, (x, 8.0, z), (1.45, 0.78, 0.66), "NEXUS_Steel", 0.012)
        box(name + "_FRONT", (x, 7.60, z), (1.38, 0.05, 0.60), "NEXUS_Painted_Metal", 0.006)
        box(name + "_HANDLE", (x, 7.55, z), (0.52, 0.05, 0.05), "NEXUS_Steel", 0.006)
        box(name + "_LABEL", (x + 0.48, 7.56, z + 0.16), (0.18, 0.015, 0.08), "NEXUS_Paper", 0.0)
        box(name + "_LIGHT", (x - 0.55, 7.56, z + 0.22), (0.04, 0.02, 0.04), "NEXUS_Amber", 0.0)

# Stainless sink and mirror on the east wall.
box("NEXUS_STORY_MORGUE_SINK_COUNTER", (18.35, 6.55, -22.2), (0.7, 1.6, 0.06), "NEXUS_Steel", 0.01)
box("NEXUS_STORY_MORGUE_SINK_BASE", (18.35, 6.55, -22.48), (0.6, 1.4, 0.5), "NEXUS_Painted_Metal", 0.008)
box("NEXUS_STORY_MORGUE_SINK_BASIN", (18.35, 6.45, -22.16), (0.42, 0.62, 0.12), "NEXUS_Steel", 0.008)
cyl("NEXUS_STORY_MORGUE_FAUCET", (18.55, 6.45, -21.95), 0.025, 0.42, "NEXUS_Steel")
cyl("NEXUS_STORY_MORGUE_FAUCET_ARM", (18.46, 6.45, -21.76), 0.022, 0.2, "NEXUS_Steel", "X")
box("NEXUS_STORY_MORGUE_MIRROR", (18.94, 6.55, -21.45), (0.03, 1.3, 0.9), "NEXUS_Mirror_Soft", 0.006)
box("NEXUS_STORY_MORGUE_SOAP", (18.7, 7.1, -21.9), (0.12, 0.1, 0.22), "NEXUS_Clinical", 0.008)
box("NEXUS_STORY_MORGUE_TOWELS", (18.55, 5.85, -21.88), (0.28, 0.22, 0.12), "NEXUS_OffWhite", 0.01)
box("NEXUS_STORY_MORGUE_BIOHAZARD", (18.93, 5.6, -21.02), (0.02, 0.22, 0.22), "NEXUS_Amber", 0.0)

bpy.ops.wm.save_as_mainfile(filepath="/home/riyo/Documentos/game/blender_concept/FM_NEXUS_V05_level1_v50.blend")
print("MORGUE_DETAIL_SAVED", len([o for o in COL.objects if o.type == "MESH"]))
