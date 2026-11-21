"""Fix sign orientation, ring brightness and camera framing for V04 nave."""
import bpy
import math
import os
from mathutils import Vector, Matrix

SCENE = bpy.context.scene
Z0 = -13.8
COLL = bpy.data.collections.get("NEXUS_V04_DETAIL")
PREFIX = "NEXUS_NAVE_SIGN3_"
AMBER = bpy.data.materials.get("NEXUS_SignText") or bpy.data.materials.get("NEXUS_Amber")


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


def text(name, body, loc, normal, size):
    n = Vector(normal).normalized()
    up = Vector((0, 0, 1))
    if abs(n.dot(up)) > 0.95:
        up = Vector((0, 1, 0))
    right = up.cross(n).normalized()
    up2 = n.cross(right).normalized()
    rot = Matrix((right, up2, n)).transposed().to_4x4()
    curve = bpy.data.curves.new(PREFIX + name, type="FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    curve.extrude = 0.005
    o = bpy.data.objects.new(curve.name, curve)
    COLL.objects.link(o)
    o.matrix_world = Matrix.Translation(Vector(loc) + n * 0.004) @ rot
    o.data.materials.append(AMBER)
    return o


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


# Softer ring: still bright, but less clipped.
ring_mat = bpy.data.materials.get("NEXUS_RingLight") or bpy.data.materials.new("NEXUS_RingLight")
ring_mat.use_nodes = True
nt = ring_mat.node_tree
nt.nodes.clear()
out = nt.nodes.new("ShaderNodeOutputMaterial")
b = nt.nodes.new("ShaderNodeBsdfPrincipled")
b.inputs["Base Color"].default_value = (0.75, 0.92, 1.0, 1.0)
b.inputs["Roughness"].default_value = 0.3
b.inputs["Emission Color"].default_value = (0.55, 0.88, 1.0, 1.0)
b.inputs["Emission Strength"].default_value = 2.0
nt.links.new(b.outputs["BSDF"], out.inputs["Surface"])
ring = bpy.data.objects.get("NEXUS_V04_NAVE_RING")
if ring:
    ring.data.materials.clear()
    ring.data.materials.append(ring_mat)

# Hide old mirrored text; keep the plates.
for o in bpy.data.objects:
    if o.name.startswith("NEXUS_NAVE_SIGN_") and o.name.endswith("_TEXT"):
        o.hide_render = True
        try: o.hide_set(True)
        except Exception: pass
    if o.name.startswith(PREFIX):
        bpy.data.objects.remove(o, do_unlink=True)

# Recreate text with the correct right/up basis.
text("NAVE", "NAVE DE CONTENCION", (-1.61, -1.0, Z0 + 2.9), (-1, 0, 0), 0.14)
text("BIO", "RIESGO BIOLOGICO", (-10.7, -4.82, Z0 + 2.7), (0, 1, 0), 0.14)
text("EXIT", "ACCESO RESTRINGIDO", (0.0, 11.82, Z0 + 2.8), (0, -1, 0), 0.13)

# Pull the nave camera back/up so the ring and catwalk fit.
aim("NEXUS_V04_CAM_Nave", (-4.0, 7.2, Z0 + 4.8), (-11.0, 2.0, Z0 + 3.2), 18.0)
aim("NEXUS_V04_CAM_Mezz", (-6.5, -3.8, Z0 + 3.0), (-15.0, 3.0, Z0 + 3.8), 24.0)
aim("NEXUS_V04_CAM_Corridor", (0.9, -6.2, Z0 + 2.0), (-1.2, 11.8, Z0 + 2.0), 22.0)
aim("NEXUS_V04_CAM_Tank", (-4.2, 5.2, Z0 + 3.1), (-10.7, 1.8, Z0 + 2.4), 26.0)
SCENE.camera = bpy.data.objects.get("NEXUS_V04_CAM_Nave")
SCENE.view_settings.exposure = 1.35

path = os.path.join("/home/riyo/Documentos/game/blender_concept", "FM_NEXUS_V04_nave_final_v3.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
print("NAVE_V3_SAVED", path, os.path.getsize(path))
