"""Final tank/camera correction for the V04 nave detail."""
import bpy
import math
import os
from mathutils import Vector, Matrix

SCENE = bpy.context.scene
Z0 = -13.8
ROOT = "/home/riyo/Documentos/game"


def bsdf_of(mat):
    if not mat or not mat.use_nodes:
        return None
    return next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)


def make_goo():
    m = bpy.data.materials.get("NEXUS_GooTrans") or bpy.data.materials.new("NEXUS_GooTrans")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = (0.02, 0.30, 0.08, 1.0)
    b.inputs["Roughness"].default_value = 0.18
    b.inputs["Metallic"].default_value = 0.0
    b.inputs["Alpha"].default_value = 0.32
    b.inputs["Emission Color"].default_value = (0.02, 0.55, 0.12, 1.0)
    b.inputs["Emission Strength"].default_value = 1.2
    nt.links.new(b.outputs["BSDF"], out.inputs["Surface"])
    try:
        m.surface_render_method = "BLENDED"
    except Exception:
        pass
    return m


goo = make_goo()
tank_goo = bpy.data.objects.get("NEXUS_V04_NAVE_TANK_GOO")
if tank_goo:
    tank_goo.data.materials.clear()
    tank_goo.data.materials.append(goo)
    tank_goo.show_transparent = True

# Bring the tank glass closer to clear glass so the specimen reads.
glass = bpy.data.materials.get("NEXUS_Glass")
b = bsdf_of(glass)
if b:
    b.inputs["Base Color"].default_value = (0.35, 0.52, 0.55, 1.0)
    b.inputs["Roughness"].default_value = 0.08
    b.inputs["Alpha"].default_value = 0.14
    b.inputs["Transmission Weight"].default_value = 0.0
try:
    glass.surface_render_method = "BLENDED"
except Exception:
    pass


def aim(name, loc, target, lens):
    cam = bpy.data.objects.get(name)
    cam.location = Vector(loc)
    cam.data.lens = lens
    f = (Vector(target) - Vector(loc)).normalized()
    up = Vector((0, 0, 1))
    if abs(f.dot(up)) > 0.98: up = Vector((0, 1, 0))
    right = f.cross(up).normalized()
    up2 = right.cross(f).normalized()
    cam.matrix_world = Matrix.Translation(cam.location) @ Matrix((right, up2, -f)).transposed().to_4x4()

aim("NEXUS_V04_CAM_Nave", (-4.0, 7.0, Z0 + 4.2), (-11.0, 2.0, Z0 + 2.6), 22.0)
aim("NEXUS_V04_CAM_Mezz", (-6.5, -3.8, Z0 + 3.0), (-15.0, 3.0, Z0 + 3.8), 24.0)
aim("NEXUS_V04_CAM_Corridor", (-0.9, -6.8, Z0 + 2.0), (0.8, 11.8, Z0 + 2.0), 20.0)
aim("NEXUS_V04_CAM_Tank", (-4.2, 5.2, Z0 + 3.1), (-10.7, 1.8, Z0 + 2.4), 24.0)
SCENE.camera = bpy.data.objects["NEXUS_V04_CAM_Nave"]
SCENE.view_settings.exposure = 1.35

path = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V04_nave_final.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
print("NAVE_FINAL_SAVED", path, os.path.getsize(path))
