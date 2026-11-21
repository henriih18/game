"""Polish cold chamber lighting/racks and medical room curtain/patient."""
import bpy
import math
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
COLL = bpy.data.collections.get("NEXUS_STORY_LOWER")
if COLL is None:
    COLL = bpy.context.scene.collection


def material(name, color, rough=0.8, metallic=0.0, emission=None, strength=0.0):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
    bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metallic
        if emission:
            bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
            bsdf.inputs["Emission Strength"].default_value = strength
    m.diffuse_color = (*color, 1.0)
    return m


def box(name, center, size, mat, bevel=0.008):
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
    if mat:
        mesh.materials.append(mat)
    if bevel > 0:
        md = o.modifiers.new("Bevel", "BEVEL")
        md.width = bevel
        md.segments = 1
    return o


def sphere(name, center, dims, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=1.0, location=center)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    for c in list(o.users_collection):
        c.objects.unlink(o)
    COLL.objects.link(o)
    o.data.materials.append(mat)
    return o


curtain_mat = material("NEXUS_Curtain", (0.28, 0.34, 0.33), 0.95)
skin = material("NEXUS_Skin_Pale", (0.55, 0.40, 0.32), 0.72)
hair = material("NEXUS_Hair", (0.035, 0.028, 0.022), 0.9)
cold_glow = material("NEXUS_ColdStrip", (0.20, 0.48, 0.62), 0.35,
                     emission=(0.30, 0.70, 1.0), strength=2.2)

# Cold chamber: cold light instead of warm.
for name in ("CAMARAS_FRIGORIFICAS_LIGHT_AREA",):
    o = bpy.data.objects.get(name)
    if o and o.type == "LIGHT":
        o.data.color = (0.64, 0.80, 1.0)
        o.data.energy = 280.0
cold = bpy.data.objects.get("NEXUS_STORY_COLD_LIGHT")
if cold and cold.type == "LIGHT":
    cold.data.color = (0.56, 0.74, 1.0)
    cold.data.energy = 170.0
    cold.location.z = -21.75

# Rack frost, cold strip and frosted glass on each door.
for i in range(3):
    door = bpy.data.objects.get(f"NEXUS_LROOM_CAMARAS_FRIGORIFICAS_RACK_DOOR_{i}")
    if not door:
        continue
    x = door.location.x
    y = 1.515
    z = door.location.z
    box(f"NEXUS_POLISH_COLD_GLASS_{i}", (x, y, z + 0.05),
        (0.72, 0.012, 1.34), bpy.data.materials.get("NEXUS_Glass"), 0.002)
    box(f"NEXUS_POLISH_COLD_STRIP_{i}", (x - 0.46, y - 0.012, z),
        (0.035, 0.014, 1.72), cold_glow, 0.002)
    box(f"NEXUS_POLISH_COLD_STRIP_B_{i}", (x + 0.46, y - 0.012, z),
        (0.035, 0.014, 1.72), cold_glow, 0.002)
    box(f"NEXUS_POLISH_COLD_FROSTCAP_{i}", (x, y - 0.01, z + 1.02),
        (0.92, 0.016, 0.14), bpy.data.materials.get("NEXUS_Frost"), 0.003)
    box(f"NEXUS_POLISH_COLD_FROSTFOOT_{i}", (x, y - 0.01, z - 1.02),
        (0.88, 0.016, 0.10), bpy.data.materials.get("NEXUS_Frost"), 0.003)

# Replace the two flat curtain panels with pleated fabric.
for old in ("NEXUS_STORY_HAB_CURTAIN_0", "NEXUS_STORY_HAB_CURTAIN_1"):
    o = bpy.data.objects.get(old)
    if o:
        o.hide_render = True
        try:
            o.hide_set(True)
        except Exception:
            pass

for panel, y0 in ((0, -4.86), (1, -3.46)):
    for k in range(7):
        yy = y0 + k * 0.17
        xoff = 15.475 if k % 2 == 0 else 15.525
        box(f"NEXUS_POLISH_CURTAIN_{panel}_{k}", (xoff, yy, -20.42),
            (0.028, 0.155, 1.95), curtain_mat, 0.004)

# Replace block head with a real head and add body volume under the sheet.
old_head = bpy.data.objects.get("NEXUS_STORY_HAB_HEAD")
if old_head:
    old_head.hide_render = True
    try:
        old_head.hide_set(True)
    except Exception:
        pass

sphere("NEXUS_POLISH_HAB_HEAD", (17.12, -2.99, -21.86), (0.26, 0.24, 0.24), skin)
box("NEXUS_POLISH_HAB_HAIR", (17.12, -2.92, -21.80), (0.20, 0.16, 0.07), hair, 0.02)
box("NEXUS_POLISH_HAB_CHEST", (17.12, -3.55, -21.94), (0.42, 0.55, 0.075),
    bpy.data.materials.get("NEXUS_OffWhite"), 0.02)
box("NEXUS_POLISH_HAB_LEGS", (17.12, -4.35, -21.95), (0.34, 0.55, 0.06),
    bpy.data.materials.get("NEXUS_OffWhite"), 0.02)
box("NEXUS_POLISH_HAB_FEET", (17.12, -4.78, -21.90), (0.30, 0.22, 0.12),
    bpy.data.materials.get("NEXUS_OffWhite"), 0.02)

# Move morgue drawers 0.05 m out of the north wall.
for n in ("NEXUS_STORY_MORGUE_DRAWER_0_0", "NEXUS_STORY_MORGUE_DRAWER_0_1",
          "NEXUS_STORY_MORGUE_DRAWER_0_2", "NEXUS_STORY_MORGUE_DRAWER_1_0",
          "NEXUS_STORY_MORGUE_DRAWER_1_1", "NEXUS_STORY_MORGUE_DRAWER_1_2"):
    o = bpy.data.objects.get(n)
    if o:
        o.location.y -= 0.06

bpy.ops.wm.save_as_mainfile(filepath=ROOT + "/blender_concept/FM_NEXUS_V05_level1_v59.blend")
print("POLISH_COLD_HAB_SAVED", len(COLL.objects))
