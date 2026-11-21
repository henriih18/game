"""Detail pass for the NEXUS V04 containment nave."""
import bpy
import math
import os
from mathutils import Vector, Matrix

ROOT = "/home/riyo/Documentos/game"
SCENE = bpy.context.scene
Z0 = -13.8
PREFIX = "NEXUS_NAVE_DETAIL_"
COLL = bpy.data.collections.get("NEXUS_V04_DETAIL")
if COLL is None:
    COLL = bpy.data.collections.new("NEXUS_V04_DETAIL")
    bpy.data.collections["NEXUS_V04_LAB_SCALE"].children.link(COLL)


def mat(n):
    return bpy.data.materials.get(n)


def box(name, center, size, material, bevel=0.012):
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


def cyl(name, center, radius, depth, material, axis="Z", verts=20):
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
    if axis == "X": o.rotation_euler.y = math.pi / 2
    elif axis == "Y": o.rotation_euler.x = math.pi / 2
    if material: mesh.materials.append(material)
    return o


def text(name, body, loc, normal, size, material):
    n = Vector(normal).normalized()
    up = Vector((0, 0, 1))
    if abs(n.dot(up)) > 0.95: up = Vector((0, 1, 0))
    right = up.cross(n).normalized()
    up2 = n.cross(right).normalized()
    rot = Matrix((right, up2, n)).transposed().to_4x4()
    plate = box(PREFIX + name + "_PLATE", Vector(loc) - n * 0.03, (size * 5.0, size * 1.4, 0.05), mat("NEXUS_SignPlate") or mat("NEXUS_Concrete_Dark"))
    plate.matrix_world = Matrix.Translation(Vector(loc) - n * 0.04) @ rot
    curve = bpy.data.curves.new(PREFIX + name + "_TEXT", type="FONT")
    curve.body = body
    curve.align_x = "CENTER"; curve.align_y = "CENTER"
    curve.size = size; curve.extrude = 0.005
    txt = bpy.data.objects.new(curve.name, curve); COLL.objects.link(txt)
    txt.matrix_world = Matrix.Translation(Vector(loc) + n * 0.002) @ rot
    if material: txt.data.materials.append(material)


def clear_old():
    for o in list(bpy.data.objects):
        if o.name.startswith(PREFIX):
            bpy.data.objects.remove(o, do_unlink=True)


def tank_detail():
    steel = mat("NEXUS_Steel")
    dark = mat("NEXUS_Dark_Metal") or mat("NEXUS_Painted_Metal")
    red = mat("NEXUS_Red")
    amber = mat("NEXUS_Amber")
    # Base plinth and rings.
    cyl(PREFIX + "BASE_0", (-10.7, 2.0, Z0 + 0.22), 2.55, 0.35, steel, "Z", 32)
    cyl(PREFIX + "BASE_1", (-10.7, 2.0, Z0 + 0.52), 2.30, 0.22, dark, "Z", 32)
    cyl(PREFIX + "BASE_2", (-10.7, 2.0, Z0 + 0.70), 2.08, 0.14, steel, "Z", 32)
    # Vertical cage ribs.
    for i in range(8):
        a = 2 * math.pi * i / 8
        x = -10.7 + math.cos(a) * 2.25
        y = 2.0 + math.sin(a) * 2.25
        cyl(f"{PREFIX}RIB_{i}", (x, y, Z0 + 2.65), 0.055, 3.9, steel, "Z", 10)
    # Top rings.
    cyl(PREFIX + "TOP_0", (-10.7, 2.0, Z0 + 4.42), 2.30, 0.16, steel, "Z", 32)
    cyl(PREFIX + "TOP_1", (-10.7, 2.0, Z0 + 4.58), 2.02, 0.10, dark, "Z", 32)
    # Hoses from tank base toward the south wall.
    for i, z in enumerate((Z0 + 1.1, Z0 + 1.35)):
        cyl(f"{PREFIX}HOSE_{i}", (-9.8, -1.0, z), 0.055, 4.5, mat("NEXUS_Rubber"), "Y", 12)
    # Control panel on the east face of the tank.
    box(PREFIX + "PANEL", (-7.75, 1.7, Z0 + 1.55), (0.35, 1.0, 1.3), dark, 0.02)
    box(PREFIX + "PANEL_SCREEN", (-7.55, 1.7, Z0 + 2.0), (0.04, 0.72, 0.45), mat("NEXUS_Screen"), 0.006)
    for i in range(3):
        box(f"{PREFIX}PANEL_LED_{i}", (-7.52, 1.3 + i * 0.28, Z0 + 1.25), (0.02, 0.06, 0.06), red, 0.002)
    # Hazard band around the base.
    for i in range(10):
        a = 2 * math.pi * i / 10
        b = box(f"{PREFIX}HAZARD_{i}", (-10.7 + math.cos(a) * 2.42, 2.0 + math.sin(a) * 2.42, Z0 + 0.35), (0.55, 0.06, 0.08), amber, 0.003)
        b.rotation_euler.z = a
    # Pipe bridge above the tank.
    cyl(PREFIX + "PIPE_BRIDGE", (-10.7, 2.0, Z0 + 5.1), 0.12, 7.0, mat("NEXUS_Rusted_Metal"), "X", 16)


def nave_clutter():
    steel = mat("NEXUS_Steel")
    rust = mat("NEXUS_Rusted_Metal")
    rubber = mat("NEXUS_Rubber")
    debris = mat("NEXUS_Debris")
    blood = mat("NEXUS_Blood_Dried")
    amber = mat("NEXUS_Amber")
    # Broken glass and metal shards around the tank.
    for i in range(12):
        a = i * 0.9
        x = -10.7 + math.cos(a) * (3.2 + 0.25 * (i % 3))
        y = 2.0 + math.sin(a) * (3.2 + 0.25 * (i % 2))
        s = box(f"{PREFIX}SHARD_{i}", (x, y, Z0 + 0.05), (0.10 + 0.04 * (i % 3), 0.06, 0.015), debris, 0.002)
        s.rotation_euler.z = a
    # Cable coils and cables on the floor.
    for i, (x, y) in enumerate(((-4.2, 4.1), (-3.4, 3.4), (-5.0, 3.0))):
        cyl(f"{PREFIX}COIL_{i}", (x, y, Z0 + 0.08), 0.38, 0.10, rubber, "Z", 20)
    for i in range(5):
        cyl(f"{PREFIX}FLOOR_CABLE_{i}", (-7.0 + i * 0.25, -2.2, Z0 + 0.06), 0.028, 5.0, rubber, "X", 8)
    # Hazard strips and a dried trail.
    box(PREFIX + "TRAIL", (-8.4, 1.5, Z0 + 0.015), (2.2, 0.7, 0.02), blood, 0.002)
    box(PREFIX + "TRAIL_2", (-6.3, 0.8, Z0 + 0.015), (1.3, 0.35, 0.02), blood, 0.002)
    # Pallet with a broken crate and barrels.
    box(PREFIX + "PALLET_2", (0.0, -2.4, Z0 + 0.10), (1.6, 1.0, 0.12), debris, 0.01)
    box(PREFIX + "CRATE_BROKEN", (-0.2, -2.4, Z0 + 0.55), (0.8, 0.6, 0.7), rust, 0.015)
    for i, (x, y) in enumerate(((-4.0, -1.8), (-4.9, -1.4), (-5.9, -1.9))):
        cyl(f"{PREFIX}BARREL_{i}", (x, y, Z0 + 0.48), 0.33, 0.95, rust, "Z", 16)
    # Hanging cables under the east catwalk.
    for i in range(6):
        x = -2.8 + (i % 2) * 0.4
        y = -3.8 + i * 1.2
        cyl(f"{PREFIX}DROP_CABLE_{i}", (x, y, Z0 + 4.1), 0.018, 1.3, rubber, "Z", 8)
    # Ceiling/pipe hangers.
    for i, y in enumerate((-3.0, 1.0, 5.0)):
        box(f"{PREFIX}HANGER_{i}", (-10.7, y, Z0 + 6.6), (0.12, 0.12, 0.5), steel, 0.006)


def signage():
    amber = mat("NEXUS_SignText") or mat("NEXUS_Amber")
    text("TANK_WARN", "CONTENCION 01  //  PRESION", (-10.7, 2.0, Z0 + 5.25), (0, -1, 0), 0.18, amber)
    text("BIO_WARN", "RIESGO BIOLOGICO", (-7.55, 1.7, Z0 + 3.0), (1, 0, 0), 0.13, amber)
    text("NO_ENTRY", "NO ENTRAR", (-1.75, -2.4, Z0 + 2.4), (-1, 0, 0), 0.14, amber)
    text("CATWALK", "PASARELA 02", (-2.3, 1.3, Z0 + 2.3), (1, 0, 0), 0.12, amber)


def cameras():
    def aim(name, loc, target, lens):
        cam = bpy.data.objects.get(name)
        cam.location = Vector(loc); cam.data.lens = lens
        f = (Vector(target) - cam.location).normalized()
        up = Vector((0, 0, 1))
        if abs(f.dot(up)) > 0.98: up = Vector((0, 1, 0))
        right = f.cross(up).normalized(); up2 = right.cross(f).normalized()
        cam.matrix_world = Matrix.Translation(cam.location) @ Matrix((right, up2, -f)).transposed().to_4x4()
    aim("NEXUS_V04_CAM_Nave", (-10.7, 7.4, Z0 + 3.45), (-10.7, -1.0, Z0 + 2.55), 18.0)
    aim("NEXUS_V04_CAM_Mezz", (-6.5, -3.8, Z0 + 2.2), (-15.0, 3.0, Z0 + 3.2), 22.0)
    aim("NEXUS_V04_CAM_Corridor", (-0.9, -6.8, Z0 + 2.0), (0.8, 11.8, Z0 + 2.0), 20.0)
    aim("NEXUS_V04_CAM_Tank", (-4.2, 5.2, Z0 + 3.1), (-10.7, 1.8, Z0 + 2.4), 24.0)
    SCENE.camera = bpy.data.objects.get("NEXUS_V04_CAM_Nave")


clear_old()
tank_detail()
nave_clutter()
signage()
cameras()
SCENE.view_settings.exposure = 1.45
path = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V04_nave_detail.blend")
i = 2
while os.path.exists(path):
    path = os.path.join(ROOT, "blender_concept", f"FM_NEXUS_V04_nave_detail_{i:02d}.blend")
    i += 1
bpy.ops.wm.save_as_mainfile(filepath=path)
print("NAVE_DETAIL_SAVED", path, os.path.getsize(path))
