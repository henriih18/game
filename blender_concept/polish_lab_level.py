"""Polish the new lab level: clean signage, glass/goo, visible ceiling strips, props."""
import bpy
import math
import os
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
SCENE = bpy.context.scene
C_PROPS = bpy.data.collections.get("NEXUS_V03_LAB_PROPS")
C_STRUCT = bpy.data.collections.get("NEXUS_V03_LAB_STRUCT")
C_LIGHT = bpy.data.collections.get("NEXUS_V03_LAB_LIGHTS")


def mat(name):
    return bpy.data.materials.get(name)


def simple_material(name, color, roughness=0.6, metallic=0.0, emission=None, strength=0.0, alpha=1.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Alpha"].default_value = alpha
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    if alpha < 1.0:
        try:
            m.surface_render_method = "BLENDED"
        except Exception:
            pass
    return m


def box(name, center, size, material, col, bevel=0.01):
    mesh = bpy.data.meshes.new(name)
    x, y, z = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
    verts = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
             (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    col.objects.link(o)
    o.location = center
    if material:
        mesh.materials.append(material)
    if bevel > 0:
        m = o.modifiers.new("Bevel", "BEVEL"); m.width = bevel; m.segments = 1
    return o


def cyl(name, center, radius, depth, material, col, vertices=16):
    mesh = bpy.data.meshes.new(name)
    verts = []
    for z in (-depth * 0.5, depth * 0.5):
        for i in range(vertices):
            a = 2 * math.pi * i / vertices
            verts.append((math.cos(a) * radius, math.sin(a) * radius, z))
    faces = []
    for i in range(vertices):
        j = (i + 1) % vertices
        faces.append((i, j, vertices + j, vertices + i))
    faces.append(tuple(range(vertices - 1, -1, -1)))
    faces.append(tuple(range(vertices, vertices * 2)))
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    col.objects.link(o)
    o.location = center
    if material:
        mesh.materials.append(material)
    return o


# Materials
sign_plate = simple_material("NEXUS_SignPlate", (0.008, 0.012, 0.012), 0.72, 0.25)
sign_text = simple_material("NEXUS_SignText", (0.02, 0.012, 0.005), 0.4, 0.0, (1.0, 0.35, 0.04), 5.0)
glass = mat("NEXUS_Glass")
if glass:
    nt = glass.node_tree
    bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.42, 0.62, 0.66, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.06
        bsdf.inputs["Metallic"].default_value = 0.0
        bsdf.inputs["Transmission Weight"].default_value = 0.0
        bsdf.inputs["Alpha"].default_value = 0.16
    try:
        glass.surface_render_method = "BLENDED"
    except Exception:
        pass
green = mat("NEXUS_Green")
if green:
    nt = green.node_tree
    bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.015, 0.55, 0.16, 1.0)
        bsdf.inputs["Emission Color"].default_value = (0.05, 1.0, 0.25, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 4.5

# Replace noisy sign plates and text materials.
for o in bpy.data.objects:
    if o.name.startswith("NEXUS_V03_SIGN_PLATE"):
        o.data.materials.clear()
        o.data.materials.append(sign_plate)
    elif o.name.startswith("NEXUS_V03_SIGN_TEXT") or o.name.startswith("NEXUS_V03_BIO_WARNING"):
        o.data.materials.clear()
        o.data.materials.append(sign_text)

# Visible ceiling strips in each new room.
strips = [
    ("BIO", -10.0, -5.4, "NEXUS_CorridorLight"),
    ("CHEM", 0.5, -5.4, "NEXUS_CorridorLight"),
    ("ARCH", 10.5, -5.2, "NEXUS_Amber"),
    ("AN", -10.0, 4.9, "NEXUS_CorridorLight"),
    ("OBS", -0.5, 5.4, "NEXUS_CorridorLight"),
    ("SRV", 9.0, 4.9, "NEXUS_CorridorLight"),
]
for tag, x, y, mname in strips:
    box(f"NEXUS_V03_{tag}_STRIP", (x, y, -10.23), (2.1, 0.10, 0.05), mat(mname), C_LIGHT, 0.004)

# Storage cabinet and chemistry bottles to increase density.
box("NEXUS_V03_BIO_CABINET", (-13.6, -9.05, -12.2), (1.9, 0.35, 2.0), mat("NEXUS_Painted_Metal"), C_PROPS, 0.02)
for i in range(3):
    box(f"NEXUS_V03_BIO_CAB_SHELF_{i}", (-13.6, -8.85, -13.0 + i * 0.6), (1.7, 0.25, 0.04), mat("NEXUS_Steel"), C_PROPS, 0.005)
for i in range(6):
    cyl(f"NEXUS_V03_BIO_BOTTLE_{i}", (-13.1 + (i % 3) * 0.4, -3.1 + (i // 3) * 0.25, -12.55), 0.06, 0.22,
        mat("NEXUS_Glass"), C_PROPS, 12)
# Wall monitor in the chemistry lab.
box("NEXUS_V03_CHEM_WALL_MON", (0.5, -1.55, -11.3), (0.9, 0.06, 0.55), mat("NEXUS_Screen"), C_PROPS, 0.01)
# Ceiling duct near the archive, to break the empty ceiling.
box("NEXUS_V03_ARCH_DUCT", (10.5, -4.8, -10.45), (3.2, 0.35, 0.28), mat("NEXUS_Steel"), C_STRUCT, 0.01)
# A second debris cluster and handprint-like dark patch in the corridor.
box("NEXUS_V03_CORR_DEBRIS", (-4.8, 1.0, -13.62), (0.5, 0.25, 0.05), mat("NEXUS_Debris"), C_PROPS, 0.01)
box("NEXUS_V03_CORR_PANEL", (8.0, 1.33, -11.8), (1.4, 0.03, 0.9), mat("NEXUS_Painted_Metal"), C_PROPS, 0.01)

# Save a new version, never overwriting the previous lab-level file.
path = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V03_lab_level_polish.blend")
i = 2
while os.path.exists(path):
    path = os.path.join(ROOT, "blender_concept", f"FM_NEXUS_V03_lab_level_polish_{i:02d}.blend")
    i += 1
bpy.ops.wm.save_as_mainfile(filepath=path)
print("POLISH_SAVED", path, os.path.getsize(path))
