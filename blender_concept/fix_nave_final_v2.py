"""Final focal/camera correction for the NEXUS V04 nave."""
import bpy
import math
import os
from mathutils import Vector, Matrix

SCENE = bpy.context.scene
Z0 = -13.8
COLL = bpy.data.collections.get("NEXUS_V04_DETAIL")
PREFIX = "NEXUS_NAVE_SIGN_"


def mat(n):
    return bpy.data.materials.get(n)


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


def sign(name, body, loc, normal, size, material):
    n = Vector(normal).normalized()
    up = Vector((0, 0, 1))
    if abs(n.dot(up)) > 0.95:
        up = Vector((0, 1, 0))
    # For a viewer looking against the normal, screen-right is n x up.
    right = n.cross(up).normalized()
    up2 = up
    rot = Matrix((right, up2, n)).transposed().to_4x4()
    plate = box(PREFIX + name + "_PLATE", Vector(loc) - n * 0.03, (size * 5.2, size * 1.5, 0.06), mat("NEXUS_SignPlate") or mat("NEXUS_Concrete_Dark"))
    plate.matrix_world = Matrix.Translation(Vector(loc) - n * 0.04) @ rot
    curve = bpy.data.curves.new(PREFIX + name + "_TEXT", type="FONT")
    curve.body = body
    curve.align_x = "CENTER"; curve.align_y = "CENTER"
    curve.size = size; curve.extrude = 0.005
    txt = bpy.data.objects.new(curve.name, curve); COLL.objects.link(txt)
    txt.matrix_world = Matrix.Translation(Vector(loc) + n * 0.002) @ rot
    if material: txt.data.materials.append(material)


def aim(name, loc, target, lens):
    cam = bpy.data.objects.get(name)
    cam.location = Vector(loc); cam.data.lens = lens
    f = (Vector(target) - cam.location).normalized()
    up = Vector((0, 0, 1))
    if abs(f.dot(up)) > 0.98: up = Vector((0, 1, 0))
    right = f.cross(up).normalized()
    up2 = right.cross(f).normalized()
    cam.matrix_world = Matrix.Translation(cam.location) @ Matrix((right, up2, -f)).transposed().to_4x4()


# The goo was still a tall opaque cylinder. Leave only a liquid pool at the bottom.
goo = bpy.data.objects.get("NEXUS_V04_NAVE_TANK_GOO")
if goo:
    goo.scale.z = 0.30
    goo.location.z = Z0 + 1.02
    goo.data.materials.clear()
    goo.data.materials.append(mat("NEXUS_GooTrans"))

# Hide old mirrored overhead labels.
for o in list(bpy.data.objects):
    if o.name.startswith("NEXUS_NAVE_DETAIL_") and (o.name.endswith("_TEXT") or o.name.endswith("_PLATE")):
        o.hide_render = True
        try: o.hide_set(True)
        except Exception: pass

# Clean, legible labels on the nave walls.
sign("NAVE", "NAVE DE CONTENCION", (-1.63, -1.0, Z0 + 2.9), (-1, 0, 0), 0.14, mat("NEXUS_SignText") or mat("NEXUS_Amber"))
sign("BIO", "RIESGO BIOLOGICO", (-10.7, -4.86, Z0 + 2.7), (0, 1, 0), 0.14, mat("NEXUS_SignText") or mat("NEXUS_Amber"))
sign("EXIT", "ACCESO RESTRINGIDO", (0.0, 11.86, Z0 + 2.8), (0, -1, 0), 0.13, mat("NEXUS_SignText") or mat("NEXUS_Amber"))

aim("NEXUS_V04_CAM_Nave", (-4.0, 7.2, Z0 + 3.8), (-11.0, 2.0, Z0 + 2.8), 20.0)
aim("NEXUS_V04_CAM_Mezz", (-6.5, -3.8, Z0 + 3.0), (-15.0, 3.0, Z0 + 3.8), 24.0)
aim("NEXUS_V04_CAM_Corridor", (0.6, -6.8, Z0 + 2.0), (-0.8, 11.8, Z0 + 2.0), 22.0)
aim("NEXUS_V04_CAM_Tank", (-4.2, 5.2, Z0 + 3.1), (-10.7, 1.8, Z0 + 2.4), 26.0)
SCENE.camera = bpy.data.objects["NEXUS_V04_CAM_Nave"]
SCENE.view_settings.exposure = 1.35

path = os.path.join("/home/riyo/Documentos/game/blender_concept", "FM_NEXUS_V04_nave_final_v2.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
print("NAVE_V2_SAVED", path, os.path.getsize(path))
