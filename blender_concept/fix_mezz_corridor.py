"""Fix the mezzanine and corridor cameras for the V04 nave."""
import bpy
import os
from mathutils import Vector, Matrix

SCENE = bpy.context.scene
Z0 = -13.8


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


# Look east along the mezzanine platform, over its railing into the nave.
aim("NEXUS_V04_CAM_Mezz", (-18.0, 5.0, Z0 + 4.05), (-11.0, 0.5, Z0 + 3.9), 20.0)
# Offset the corridor shot so the far-end seam is not dead centre.
aim("NEXUS_V04_CAM_Corridor", (0.9, -7.0, Z0 + 2.05), (-0.9, 11.8, Z0 + 2.05), 22.0)
aim("NEXUS_V04_CAM_Tank", (-4.2, 5.2, Z0 + 3.1), (-10.7, 1.8, Z0 + 2.4), 26.0)
SCENE.camera = bpy.data.objects["NEXUS_V04_CAM_Mezz"]
SCENE.view_settings.exposure = 1.4

path = os.path.join("/home/riyo/Documentos/game/blender_concept", "FM_NEXUS_V04_nave_final_v4.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
print("V4_SAVED", path, os.path.getsize(path))
