"""Final visual correction for the new NEXUS lab level."""
import bpy
import os

ROOT = "/home/riyo/Documentos/game"
SCENE = bpy.context.scene


def find_bsdf(mat):
    if not mat or not mat.use_nodes:
        return None
    return next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)


green = bpy.data.materials.get("NEXUS_Green")
bsdf = find_bsdf(green)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.008, 0.28, 0.07, 1.0)
    bsdf.inputs["Emission Color"].default_value = (0.02, 0.55, 0.12, 1.0)
    bsdf.inputs["Emission Strength"].default_value = 1.35

glass = bpy.data.materials.get("NEXUS_Glass")
bsdf = find_bsdf(glass)
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.38, 0.55, 0.58, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.075
    bsdf.inputs["Transmission Weight"].default_value = 0.0
    bsdf.inputs["Alpha"].default_value = 0.12
try:
    glass.surface_render_method = "BLENDED"
except Exception:
    pass

SCENE.view_settings.exposure = 1.15

# Put the door labels at eye level on the door leaf, not above the lintel.
for o in bpy.data.objects:
    if o.name.startswith("NEXUS_V03_SIGN_PLATE_"):
        o.location.z = -11.48
        o.scale.z = 0.72
    elif o.name.startswith("NEXUS_V03_SIGN_TEXT_"):
        o.location.z = -11.48
        if hasattr(o.data, "size"):
            o.data.size = 0.11

# Practical fill in the biology room; the ceiling area light is too directional.
for i, loc in enumerate(((-12.4, -4.0, -11.1), (-8.2, -6.8, -11.1))):
    ld = bpy.data.lights.new(f"NEXUS_V03_BIO_FILL_{i}", "POINT")
    ld.color = (0.58, 0.80, 1.0)
    ld.energy = 75.0
    ld.shadow_soft_size = 0.35
    lo = bpy.data.objects.new(ld.name, ld)
    bpy.data.collections["NEXUS_V03_LAB_LIGHTS"].objects.link(lo)
    lo.location = loc

# A small equipment cart to break up the lab floor.
cart_mat = bpy.data.materials.get("NEXUS_Steel")
mesh = bpy.data.meshes.new("NEXUS_V03_BIO_CART")
x, y, z = 0.55, 0.38, 0.36
verts = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
         (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
mesh.from_pydata(verts, [], faces); mesh.update()
cart = bpy.data.objects.new("NEXUS_V03_BIO_CART", mesh)
bpy.data.collections["NEXUS_V03_LAB_PROPS"].objects.link(cart)
cart.location = (-7.2, -4.2, -13.05)
cart.data.materials.append(cart_mat)
for i, (dx, dy) in enumerate(((-0.4, -0.25), (0.4, -0.25), (-0.4, 0.25), (0.4, 0.25))):
    c = bpy.data.meshes.new(f"NEXUS_V03_BIO_CART_WHEEL_{i}")
    # small beveled cube reads as a caster
    ws = 0.07
    vv = [(-ws, -ws, -ws), (ws, -ws, -ws), (ws, ws, -ws), (-ws, ws, -ws),
          (-ws, -ws, ws), (ws, -ws, ws), (ws, ws, ws), (-ws, ws, ws)]
    c.from_pydata(vv, [], [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)])
    c.update()
    wo = bpy.data.objects.new(f"NEXUS_V03_BIO_CART_WHEEL_{i}", c)
    wo.location = (-7.2 + dx, -4.2 + dy, -13.58)
    wo.data.materials.append(bpy.data.materials.get("NEXUS_Rubber"))
    bpy.data.collections["NEXUS_V03_LAB_PROPS"].objects.link(wo)

bpy.context.scene.camera = bpy.data.objects.get("NEXUS_V03_CAM_Corridor")
path = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V03_lab_level_final.blend")
i = 2
while os.path.exists(path):
    path = os.path.join(ROOT, "blender_concept", f"FM_NEXUS_V03_lab_level_final_{i:02d}.blend")
    i += 1
bpy.ops.wm.save_as_mainfile(filepath=path)
print("FINAL_SAVED", path, os.path.getsize(path))
