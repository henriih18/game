"""Final camera pass: mezzanine platform, corridor bend, nave ring."""
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


# Show the mezzanine platform from inside the nave, with the tank off to the right.
aim("NEXUS_V04_CAM_Mezz", (-10.0, -4.0, Z0 + 2.2), (-15.5, 3.0, Z0 + 3.8), 22.0)
# Look into the east bend of the corridor instead of into the T-junction seam.
aim("NEXUS_V04_CAM_Corridor", (0.0, -7.0, Z0 + 2.05), (8.0, 12.0, Z0 + 2.0), 20.0)
# Keep the ring, tank and catwalk in frame.
aim("NEXUS_V04_CAM_Nave", (-4.0, 7.2, Z0 + 4.8), (-11.0, 2.0, Z0 + 3.2), 18.0)
aim("NEXUS_V04_CAM_Tank", (-4.2, 5.2, Z0 + 3.1), (-10.7, 1.8, Z0 + 2.4), 26.0)

SCENE.camera = bpy.data.objects.get("NEXUS_V04_CAM_Mezz")
SCENE.view_settings.exposure = 1.4

path = os.path.join("/home/riyo/Documentos/game/blender_concept", "FM_NEXUS_V04_nave_final_v5.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
print("V5_SAVED", path, os.path.getsize(path))
