"""Polish the V04 analysis/archive/server rooms and corridor camera."""
import bpy
import math
import os
from mathutils import Vector, Matrix

ROOT = "/home/riyo/Documentos/game"
SCENE = bpy.context.scene
Z0 = -13.8
COLL = bpy.data.collections.get("NEXUS_V04_DETAIL")
PREFIX = "NEXUS_POLISH_MORE_"


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


def clear():
    for o in list(bpy.data.objects):
        if o.name.startswith(PREFIX):
            bpy.data.objects.remove(o, do_unlink=True)


def aim(name, loc, target, lens):
    cam = bpy.data.objects.get(name)
    cam.location = Vector(loc); cam.data.lens = lens
    f = (Vector(target) - cam.location).normalized()
    up = Vector((0, 0, 1))
    if abs(f.dot(up)) > 0.98: up = Vector((0, 1, 0))
    right = f.cross(up).normalized(); up2 = right.cross(f).normalized()
    cam.matrix_world = Matrix.Translation(cam.location) @ Matrix((right, up2, -f)).transposed().to_4x4()


def props():
    # Analysis: chairs, boxes, paper and extra glassware.
    for i, (x, y) in enumerate(((5.2, 19.4), (7.8, 19.2), (10.8, 20.0))):
        box(f"{PREFIX}AN_CHAIR_{i}", (x, y, Z0 + 0.5), (0.55, 0.55, 0.1), mat("NEXUS_Rubber"), 0.03)
        box(f"{PREFIX}AN_CHAIR_BACK_{i}", (x, y + 0.25, Z0 + 0.95), (0.55, 0.1, 0.8), mat("NEXUS_Rubber"), 0.03)
    box(f"{PREFIX}AN_CRATE", (11.7, 18.0, Z0 + 0.4), (0.8, 0.7, 0.8), mat("NEXUS_Rusted_Metal"), 0.015)
    box(f"{PREFIX}AN_BOX", (12.0, 22.2, Z0 + 0.35), (0.65, 0.55, 0.7), mat("NEXUS_Debris"), 0.01)
    box(f"{PREFIX}AN_BLOOD_2", (9.8, 22.7, Z0 + 0.02), (1.0, 0.5, 0.02), mat("NEXUS_Blood_Dried"), 0.002)
    for i in range(5):
        box(f"{PREFIX}AN_PAPER_{i}", (4.0 + i * 0.5, 22.5, Z0 + 0.03), (0.22, 0.3, 0.01), mat("NEXUS_OffWhite"), 0.002)
    # Archive: floor boxes, papers, an overturned chair and a low cart.
    for i, (x, y) in enumerate(((3.5, -2.5), (8.5, -2.8), (10.0, 2.5))):
        box(f"{PREFIX}ARCH_FLOORBOX_{i}", (x, y, Z0 + 0.35), (0.7, 0.55, 0.7), mat("NEXUS_Debris"), 0.012)
    for i in range(6):
        box(f"{PREFIX}ARCH_FLOORPAPER_{i}", (3.0 + i * 1.1, -2.0, Z0 + 0.03), (0.2, 0.28, 0.01), mat("NEXUS_OffWhite"), 0.002)
    ch = box(f"{PREFIX}ARCH_CHAIR", (5.6, 1.8, Z0 + 0.55), (0.55, 0.55, 0.1), mat("NEXUS_Rubber"), 0.03)
    ch.rotation_euler.z = 0.7
    box(f"{PREFIX}ARCH_CHAIR_BACK", (5.6, 1.8, Z0 + 1.0), (0.55, 0.1, 0.75), mat("NEXUS_Rubber"), 0.03)
    # Servers: floor grates, boxes and a cable coil.
    for i in range(3):
        box(f"{PREFIX}SRV_GRATE_{i}", (4.0 + i * 2.2, -11.6, Z0 + 0.04), (1.4, 0.7, 0.06), mat("NEXUS_Steel"), 0.008)
    box(f"{PREFIX}SRV_BOX", (10.2, -12.2, Z0 + 0.35), (0.7, 0.55, 0.7), mat("NEXUS_Debris"), 0.01)
    box(f"{PREFIX}SRV_CABLE", (4.0, -9.3, Z0 + 0.08), (0.7, 0.25, 0.08), mat("NEXUS_Rubber"), 0.02)


def monitor_stands():
    for i, x in enumerate((5.2, 6.0, 6.8)):
        box(f"{PREFIX}AN_STAND_{i}", (x, 18.3, Z0 + 1.0), (0.06, 0.06, 0.9), mat("NEXUS_Steel"), 0.004)
    box(f"{PREFIX}ARCH_STAND", (10.4, -2.6, Z0 + 1.05), (0.06, 0.06, 0.7), mat("NEXUS_Steel"), 0.004)
    for i, x in enumerate((6.2, 7.0, 7.8)):
        box(f"{PREFIX}SRV_STAND_{i}", (x, -11.6, Z0 + 1.0), (0.06, 0.06, 0.9), mat("NEXUS_Steel"), 0.004)


def lights():
    for name, loc, energy, color in (
        ("AN", (8, 20, Z0 + 4.0), 1300.0, (0.62, 0.82, 1.0)),
        ("ARCH", (7, 0, Z0 + 3.9), 1100.0, (1.0, 0.64, 0.32)),
        ("SRV", (7, -10, Z0 + 3.9), 1000.0, (0.55, 0.85, 1.0)),
    ):
        ld = bpy.data.lights.new(PREFIX + name, "AREA")
        ld.energy = energy; ld.color = color; ld.shape = "RECTANGLE"; ld.size = 5.0; ld.size_y = 3.0
        o = bpy.data.objects.new(ld.name, ld); COLL.objects.link(o); o.location = loc


clear()
props()
monitor_stands()
lights()
# Analysis camera from the north-east, above table height.
aim("NEXUS_V04_CAM_Analisis", (3.4, 23.2, Z0 + 2.6), (8.0, 18.8, Z0 + 1.8), 20.0)
# Archive camera from the north-east, showing the room, not a near shelf.
aim("NEXUS_V04_CAM_Archivo", (11.5, 2.8, Z0 + 2.2), (3.5, -0.8, Z0 + 2.2), 18.0)
# Server camera from the south-west, along the racks.
aim("NEXUS_V04_CAM_Servidores", (3.4, -12.7, Z0 + 2.2), (7.0, -8.8, Z0 + 2.0), 18.0)
# Corridor camera past the near door panel.
aim("NEXUS_V04_CAM_Corridor", (0.0, 1.5, Z0 + 2.1), (7.0, 12.0, Z0 + 2.1), 20.0)
SCENE.camera = bpy.data.objects.get("NEXUS_V04_CAM_Analisis")
SCENE.view_settings.exposure = 1.5

path = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V04_lab_detail_more_v4.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
print("MORE_V4_SAVED", path, os.path.getsize(path))
