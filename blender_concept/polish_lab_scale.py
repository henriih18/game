"""Light/camera polish for the NEXUS V04 nave."""
import bpy
import os
from mathutils import Vector, Matrix

ROOT = "/home/riyo/Documentos/game"
SCENE = bpy.context.scene
Z0 = -13.8
COLL = bpy.data.collections.get("NEXUS_V04_DETAIL")


def light(name, kind, loc, energy, color, target=None, size=5.0):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = color
    if kind == "AREA":
        ld.shape = "RECTANGLE"
        ld.size = size
        ld.size_y = size * 0.6
    if kind == "SPOT":
        ld.spot_size = 0.9
        ld.spot_blend = 0.35
        ld.use_shadow = True
    if kind == "POINT":
        ld.shadow_soft_size = 0.3
    o = bpy.data.objects.new(name, ld)
    COLL.objects.link(o)
    o.location = Vector(loc)
    if target is not None:
        f = (Vector(target) - Vector(loc)).normalized()
        up = Vector((0, 0, 1))
        if abs(f.dot(up)) > 0.98:
            up = Vector((0, 1, 0))
        right = f.cross(up).normalized()
        up2 = right.cross(f).normalized()
        o.matrix_world = Matrix.Translation(o.location) @ Matrix((right, up2, -f)).transposed().to_4x4()
    return o


def camera(name, loc, target, lens):
    cam = bpy.data.objects.get(name)
    if cam is None:
        cd = bpy.data.cameras.new(name)
        cam = bpy.data.objects.new(name, cd)
        COLL.objects.link(cam)
    cam.location = Vector(loc)
    cam.data.lens = lens
    f = (Vector(target) - Vector(loc)).normalized()
    up = Vector((0, 0, 1))
    if abs(f.dot(up)) > 0.98:
        up = Vector((0, 1, 0))
    right = f.cross(up).normalized()
    up2 = right.cross(f).normalized()
    cam.matrix_world = Matrix.Translation(cam.location) @ Matrix((right, up2, -f)).transposed().to_4x4()
    return cam


# Existing fill is too weak for the 7 m volume.
fill = bpy.data.objects.get("NEXUS_V04_DETAIL_NAVE_FILL")
if fill:
    fill.data.energy = 1600.0
    fill.data.size = 7.0
    fill.data.size_y = 4.0

light("NEXUS_V04_POLISH_TANK_SPOT", "SPOT", (-10.7, -4.3, Z0 + 5.6), 2400.0, (0.62, 0.82, 1.0), (-10.7, 2.0, Z0 + 2.2), 2.0)
for i, x in enumerate((-17.0, -10.7, -4.2)):
    light(f"NEXUS_V04_POLISH_CATWALK_{i}", "AREA", (x, 8.0, Z0 + 4.65), 320.0, (0.55, 0.76, 1.0), None, 3.0)
light("NEXUS_V04_POLISH_RED", "POINT", (-3.0, 8.4, Z0 + 4.9), 180.0, (1.0, 0.02, 0.01))
light("NEXUS_V04_POLISH_MEZZ", "AREA", (-15.5, 3.0, Z0 + 5.2), 500.0, (0.62, 0.80, 1.0), None, 4.0)

camera("NEXUS_V04_CAM_Nave", (-10.7, -4.55, Z0 + 3.25), (-10.7, 2.0, Z0 + 3.05), 20.0)
camera("NEXUS_V04_CAM_Mezz", (-16.8, 5.3, Z0 + 4.25), (-6.0, 1.0, Z0 + 2.2), 20.0)
camera("NEXUS_V04_CAM_Corridor", (0.0, -9.6, Z0 + 2.1), (5.0, 12.0, Z0 + 2.1), 20.0)
camera("NEXUS_V04_CAM_Tank", (-4.2, 5.2, Z0 + 3.1), (-10.7, 1.8, Z0 + 2.4), 24.0)
SCENE.camera = bpy.data.objects.get("NEXUS_V04_CAM_Nave")
SCENE.view_settings.exposure = 1.55

path = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V04_lab_scale_polish.blend")
i = 2
while os.path.exists(path):
    path = os.path.join(ROOT, "blender_concept", f"FM_NEXUS_V04_lab_scale_polish_{i:02d}.blend")
    i += 1
bpy.ops.wm.save_as_mainfile(filepath=path)
print("POLISH_SAVED", path, os.path.getsize(path))
