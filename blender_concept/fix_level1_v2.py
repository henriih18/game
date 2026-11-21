"""Fix level 1 cameras/lights and cover level 2 connector overlaps."""
import bpy
import os
from mathutils import Vector, Matrix

ROOT = "/home/riyo/Documentos/game"
SCENE = bpy.context.scene
Z1 = -5.8
Z2 = -13.8


def box(name, center, size, material, col, bevel=0.008):
    mesh = bpy.data.meshes.new(name)
    x, y, z = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
    verts = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
             (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    mesh.from_pydata(verts, [], faces); mesh.update()
    o = bpy.data.objects.new(name, mesh); col.objects.link(o); o.location = center
    if material: mesh.materials.append(material)
    if bevel > 0:
        m = o.modifiers.new("Bevel", "BEVEL"); m.width = bevel; m.segments = 1
    return o


def aim(name, loc, target, lens):
    cam = bpy.data.objects.get(name)
    cam.location = Vector(loc); cam.data.lens = lens
    f = (Vector(target) - cam.location).normalized(); up = Vector((0, 0, 1))
    if abs(f.dot(up)) > 0.98: up = Vector((0, 1, 0))
    right = f.cross(up).normalized(); up2 = right.cross(f).normalized()
    cam.matrix_world = Matrix.Translation(cam.location) @ Matrix((right, up2, -f)).transposed().to_4x4()


# Level 1: scale/brightness/cameras.
for o in bpy.data.objects:
    if o.type == "LIGHT" and o.name.startswith("NEXUS_V05_"):
        if "_LIGHT" in o.name:
            o.data.energy = max(o.data.energy, 900.0)
        if "CORR_LIGHT" in o.name:
            o.data.energy = 150.0

aim("NEXUS_V05_CAM_Corridor", (-18.0, 0.0, Z1 + 2.0), (18.0, 0.0, Z1 + 2.0), 20.0)
aim("NEXUS_V05_CAM_Recepcion", (-5.2, 3.2, Z1 + 2.2), (-12.0, 8.5, Z1 + 2.5), 18.0)
aim("NEXUS_V05_CAM_Seguridad", (0.0, 3.2, Z1 + 2.2), (3.0, 7.0, Z1 + 2.0), 20.0)

# Extra fill for the tall reception volume.
ld = bpy.data.lights.new("NEXUS_V05_REC_FILL", "AREA")
ld.energy = 1100.0; ld.color = (0.92, 0.9, 0.82); ld.shape = "RECTANGLE"; ld.size = 6.0; ld.size_y = 3.0
lo = bpy.data.objects.new(ld.name, ld)
light_col = bpy.data.collections.get("V05_LIGHTS") or bpy.data.collections.get("NEXUS_V05_LIGHTS")
if light_col is None:
    light_col = bpy.data.collections.new("V05_LIGHTS")
light_col.objects.link(lo)
lo.location = (-12.0, 6.0, Z1 + 4.8)

# Level 2: cover connector floor overlaps with metal threshold plates.
C2 = bpy.data.collections.get("NEXUS_V04_DETAIL")
for o in list(bpy.data.objects):
    if o.type == "MESH" and o.name.startswith("NEXUS_V04_CONN_") and o.name.endswith("_FLOOR"):
        dims = o.dimensions.copy()
        loc = o.location.copy()
        box("NEXUS_FIX_CONN_" + o.name, (loc.x, loc.y, Z2 + 0.14),
            (max(0.2, dims.x - 0.04), max(0.2, dims.y - 0.04), 0.04),
            bpy.data.materials.get("NEXUS_Steel"), C2, 0.008)
        box("NEXUS_FIX_CONN_HAZ_" + o.name, (loc.x, loc.y, Z2 + 0.165),
            (max(0.15, dims.x - 0.15), 0.12, 0.01),
            bpy.data.materials.get("NEXUS_Amber"), C2, 0.002)

# Cover the main corridor T-junction seam.
box("NEXUS_FIX_JUNCTION", (0.0, 12.0, Z2 + 0.14), (3.5, 3.5, 0.04),
    bpy.data.materials.get("NEXUS_Steel"), C2, 0.008)

SCENE.camera = bpy.data.objects.get("NEXUS_V05_CAM_Recepcion")
SCENE.view_settings.exposure = 1.5

path = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V05_level1_v2.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
print("V05_V2_SAVED", path, os.path.getsize(path))
