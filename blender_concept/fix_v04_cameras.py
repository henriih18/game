"""Camera and focal-point fixes for the V04 NEXUS nave."""
import bpy
import math
import os
from mathutils import Vector, Matrix

SCENE = bpy.context.scene
Z0 = -13.8
COLL = bpy.data.collections.get("NEXUS_V04_DETAIL")
PREFIX = "NEXUS_V04_FIX_"


def aim(name, loc, target, lens):
    cam = bpy.data.objects.get(name)
    cam.location = Vector(loc)
    cam.data.lens = lens
    f = (Vector(target) - Vector(loc)).normalized()
    up = Vector((0, 0, 1))
    if abs(f.dot(up)) > 0.98:
        up = Vector((0, 1, 0))
    right = f.cross(up).normalized()
    up2 = right.cross(f).normalized()
    cam.matrix_world = Matrix.Translation(cam.location) @ Matrix((right, up2, -f)).transposed().to_4x4()


def box(name, center, size, material, bevel=0.01):
    mesh = bpy.data.meshes.new(name)
    x, y, z = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
    verts = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
             (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    mesh.from_pydata(verts, [], faces); mesh.update()
    o = bpy.data.objects.new(name, mesh); COLL.objects.link(o); o.location = center
    if material: mesh.materials.append(material)
    if bevel > 0:
        m = o.modifiers.new("Bevel", "BEVEL"); m.width = bevel; m.segments = 1
    return o


def cyl(name, center, radius, depth, material, verts=20):
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
    mesh.from_pydata(vl, [], fs); mesh.update()
    o = bpy.data.objects.new(name, mesh); COLL.objects.link(o); o.location = center
    if material: mesh.materials.append(material)
    return o


# Clear previous fixes.
for o in list(bpy.data.objects):
    if o.name.startswith(PREFIX):
        bpy.data.objects.remove(o, do_unlink=True)

# Dark specimen inside the containment tank so it does not read as a green column.
cyl(PREFIX + "SPECIMEN_BODY", (-10.7, 2.0, Z0 + 1.9), 0.32, 2.0, bpy.data.materials.get("NEXUS_Concrete_Dark"), 20)
cyl(PREFIX + "SPECIMEN_HEAD", (-10.7, 2.0, Z0 + 2.95), 0.22, 0.34, bpy.data.materials.get("NEXUS_Concrete_Dark"), 16)

# Add monitor frames and stands so the screens no longer float.
for i, x in enumerate((-13.0, -12.0, -11.0)):
    box(f"{PREFIX}MON_FRAME_{i}", (x, 0.39, Z0 + 1.45), (0.78, 0.05, 0.54), bpy.data.materials.get("NEXUS_Painted_Metal"), 0.006)
    box(f"{PREFIX}MON_STAND_{i}", (x, 0.22, Z0 + 1.17), (0.08, 0.18, 0.28), bpy.data.materials.get("NEXUS_Steel"), 0.005)

# Better camera framings.
aim("NEXUS_V04_CAM_Mezz", (-16.6, 5.4, Z0 + 4.10), (-5.0, 2.0, Z0 + 3.95), 20.0)
aim("NEXUS_V04_CAM_Corridor", (0.85, -6.8, Z0 + 2.0), (-0.4, 11.8, Z0 + 2.0), 20.0)
aim("NEXUS_V04_CAM_Nave", (-3.4, -4.6, Z0 + 3.6), (-12.0, 3.0, Z0 + 3.6), 18.0)
aim("NEXUS_V04_CAM_Tank", (-4.2, 5.2, Z0 + 3.1), (-10.7, 1.8, Z0 + 2.4), 24.0)

SCENE.camera = bpy.data.objects.get("NEXUS_V04_CAM_Mezz")
SCENE.view_settings.exposure = 1.45

path = os.path.join("/home/riyo/Documentos/game/blender_concept", "FM_NEXUS_V04_lab_scale_final.blend")
i = 2
while os.path.exists(path):
    path = os.path.join("/home/riyo/Documentos/game/blender_concept", f"FM_NEXUS_V04_lab_scale_final_{i:02d}.blend")
    i += 1
bpy.ops.wm.save_as_mainfile(filepath=path)
print("FIX_SAVED", path, os.path.getsize(path))
