"""Detail the remaining V04 lab rooms: analysis, archive and servers."""
import bpy
import math
import os
from mathutils import Vector, Matrix

ROOT = "/home/riyo/Documentos/game"
Z0 = -13.8
COLL = bpy.data.collections.get("NEXUS_V04_DETAIL")
PREFIX = "NEXUS_LAB_MORE_"


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


def cyl(name, center, radius, depth, material, axis="Z", verts=16):
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


def screen(name, x, y, z, w=0.7, h=0.45, ry=0.0):
    box(PREFIX + name + "_FRAME", (x, y, z), (w + 0.06, 0.06, h + 0.06), mat("NEXUS_Painted_Metal"), 0.006)
    box(PREFIX + name + "_SCREEN", (x, y - 0.04, z), (w, 0.02, h), mat("NEXUS_Screen"), 0.003)


def sign(name, body, loc, normal, size):
    n = Vector(normal).normalized(); up = Vector((0, 0, 1))
    if abs(n.dot(up)) > 0.95: up = Vector((0, 1, 0))
    right = up.cross(n).normalized(); up2 = n.cross(right).normalized()
    rot = Matrix((right, up2, n)).transposed().to_4x4()
    box(PREFIX + name + "_PLATE", Vector(loc) - n * 0.03, (size * 5.0, size * 1.4, 0.06), mat("NEXUS_SignPlate") or mat("NEXUS_Concrete_Dark"))
    bpy.data.objects[PREFIX + name + "_PLATE"].matrix_world = Matrix.Translation(Vector(loc) - n * 0.04) @ rot
    c = bpy.data.curves.new(PREFIX + name + "_TEXT", type="FONT")
    c.body = body; c.align_x = "CENTER"; c.align_y = "CENTER"; c.size = size; c.extrude = 0.005
    o = bpy.data.objects.new(c.name, c); COLL.objects.link(o)
    o.matrix_world = Matrix.Translation(Vector(loc) + n * 0.002) @ rot
    o.data.materials.append(mat("NEXUS_SignText") or mat("NEXUS_Amber"))


def clear():
    for o in list(bpy.data.objects):
        if o.name.startswith(PREFIX):
            bpy.data.objects.remove(o, do_unlink=True)


def analysis():
    # Center 8,20. Tables and instruments.
    box(PREFIX + "AN_TABLE_A", (6.0, 18.0, Z0 + 0.82), (4.0, 1.3, 0.08), mat("NEXUS_Steel"), 0.015)
    box(PREFIX + "AN_TABLE_B", (10.0, 21.5, Z0 + 0.82), (4.0, 1.3, 0.08), mat("NEXUS_Steel"), 0.015)
    for i, (x, y) in enumerate(((6.0, 18.0), (10.0, 21.5))):
        for dx in (-1.5, 1.5):
            box(f"{PREFIX}AN_LEG_{i}_{dx}", (x + dx, y, Z0 + 0.4), (0.08, 1.0, 0.8), mat("NEXUS_Painted_Metal"), 0.006)
    for i, x in enumerate((5.2, 6.0, 6.8)):
        screen(f"AN_MON_{i}", x, 18.35, Z0 + 1.45, 0.62, 0.4)
    # Microscopes and sample racks.
    for i, (x, y) in enumerate(((9.0, 20.8), (10.0, 20.8), (11.0, 20.8))):
        box(f"{PREFIX}AN_MICRO_BASE_{i}", (x, y, Z0 + 0.92), (0.35, 0.25, 0.08), mat("NEXUS_Steel"), 0.01)
        cyl(f"{PREFIX}AN_MICRO_BODY_{i}", (x, y, Z0 + 1.18), 0.07, 0.45, mat("NEXUS_Steel"), "Z", 12)
        box(f"{PREFIX}AN_MICRO_HEAD_{i}", (x, y - 0.12, Z0 + 1.38), (0.22, 0.12, 0.1), mat("NEXUS_Steel"), 0.008)
    for i in range(8):
        cyl(f"{PREFIX}AN_VIAL_{i}", (7.6 + (i % 4) * 0.18, 20.7 + (i // 4) * 0.3, Z0 + 0.98), 0.035, 0.18, mat("NEXUS_Glass"), "Z", 10)
    box(PREFIX + "AN_CABINET", (3.2, 23.0, Z0 + 1.2), (0.8, 0.45, 2.2), mat("NEXUS_Painted_Metal"), 0.02)
    box(PREFIX + "AN_BLOOD", (5.0, 22.0, Z0 + 0.02), (1.2, 0.5, 0.02), mat("NEXUS_Blood_Dried"), 0.002)
    screen("AN_WALL", 12.4, 20.0, Z0 + 2.3, 1.1, 0.6)
    sign("AN_SIGN", "SALA DE ANALISIS", (2.9, 20.0, Z0 + 3.2), (1, 0, 0), 0.14)


def archive():
    # Center 7,0. Shelves, boxes, papers, fallen shelf.
    for i, x in enumerate((2.4, 4.2, 6.0, 7.8, 9.6)):
        box(f"{PREFIX}ARCH_SHELF_{i}", (x, 0.0, Z0 + 1.2), (0.7, 0.55, 2.4), mat("NEXUS_Painted_Metal"), 0.015)
        for j in range(3):
            box(f"{PREFIX}ARCH_BOX_{i}_{j}", (x, 0.0, Z0 + 0.5 + j * 0.65), (0.6, 0.42, 0.32), mat("NEXUS_Debris"), 0.008)
    # Fallen shelf and papers.
    f = box(PREFIX + "ARCH_FALLEN", (4.8, -2.0, Z0 + 0.35), (0.7, 2.6, 0.6), mat("NEXUS_Painted_Metal"), 0.01)
    f.rotation_euler.y = 1.1
    for i in range(12):
        box(f"{PREFIX}ARCH_PAPER_{i}", (3.0 + (i % 6) * 1.1, -1.8 + (i // 6) * 0.8, Z0 + 0.03), (0.22, 0.3, 0.01), mat("NEXUS_OffWhite"), 0.002)
    box(PREFIX + "ARCH_TABLE", (10.4, -2.0, Z0 + 0.82), (2.0, 1.0, 0.08), mat("NEXUS_Steel"), 0.015)
    screen("ARCH_MON", 10.4, -2.6, Z0 + 1.4, 0.7, 0.45)
    box(PREFIX + "ARCH_BLOOD", (7.0, 2.8, Z0 + 0.02), (0.8, 0.5, 0.02), mat("NEXUS_Blood_Dried"), 0.002)
    sign("ARCH_SIGN", "ARCHIVO CIENTIFICO", (1.0, 0.0, Z0 + 3.0), (1, 0, 0), 0.14)


def servers():
    # Center 7,-10. Racks on the north wall and a console.
    for i, x in enumerate((3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5)):
        box(f"{PREFIX}SRV_RACK_{i}", (x, -7.3, Z0 + 1.2), (0.8, 0.6, 2.3), mat("NEXUS_Steel"), 0.018)
        box(f"{PREFIX}SRV_PANEL_{i}", (x, -7.62, Z0 + 1.5), (0.6, 0.03, 1.2), mat("NEXUS_Screen"), 0.004)
        for j in range(4):
            box(f"{PREFIX}SRV_LED_{i}_{j}", (x - 0.22 + j * 0.14, -7.65, Z0 + 1.9), (0.03, 0.02, 0.03), mat("NEXUS_CorridorLight"), 0.002)
    box(PREFIX + "SRV_TRAY", (7.0, -7.4, Z0 + 3.0), (8.0, 0.3, 0.08), mat("NEXUS_Steel"), 0.006)
    box(PREFIX + "SRV_CONSOLE", (7.0, -11.2, Z0 + 0.82), (2.6, 0.9, 0.08), mat("NEXUS_Steel"), 0.015)
    for i, x in enumerate((6.2, 7.0, 7.8)):
        screen(f"SRV_MON_{i}", x, -11.6, Z0 + 1.45, 0.6, 0.4)
    box(PREFIX + "SRV_BLOOD", (9.6, -11.0, Z0 + 0.02), (0.7, 0.45, 0.02), mat("NEXUS_Blood_Dried"), 0.002)
    box(PREFIX + "SRV_DEBRIS", (4.0, -11.5, Z0 + 0.04), (0.5, 0.25, 0.06), mat("NEXUS_Debris"), 0.004)
    sign("SRV_SIGN", "SERVIDORES NEXUS", (11.4, -10.0, Z0 + 3.0), (-1, 0, 0), 0.14)


def lights():
    for name, loc, color, energy in (
        ("AN_LIGHT", (8, 20, Z0 + 4.0), (0.6, 0.8, 1.0), 550.0),
        ("ARCH_LIGHT", (7, 0, Z0 + 3.8), (1.0, 0.58, 0.22), 350.0),
        ("SRV_LIGHT", (7, -10, Z0 + 3.8), (0.55, 0.85, 1.0), 500.0),
    ):
        ld = bpy.data.lights.new(PREFIX + name, "AREA")
        ld.energy = energy; ld.color = color; ld.shape = "RECTANGLE"; ld.size = 4.0; ld.size_y = 2.5
        o = bpy.data.objects.new(ld.name, ld); COLL.objects.link(o); o.location = loc


def cameras():
    def aim(name, loc, target, lens):
        cam = bpy.data.objects.get(name)
        if cam is None:
            cd = bpy.data.cameras.new(name)
            cam = bpy.data.objects.new(name, cd)
            COLL.objects.link(cam)
        cam.location = Vector(loc); cam.data.lens = lens
        f = (Vector(target) - cam.location).normalized(); up = Vector((0, 0, 1))
        if abs(f.dot(up)) > 0.98: up = Vector((0, 1, 0))
        right = f.cross(up).normalized(); up2 = right.cross(f).normalized()
        cam.matrix_world = Matrix.Translation(cam.location) @ Matrix((right, up2, -f)).transposed().to_4x4()
    aim("NEXUS_V04_CAM_Analisis", (3.2, 16.2, Z0 + 2.1), (9.0, 21.0, Z0 + 2.2), 18.0)
    aim("NEXUS_V04_CAM_Archivo", (1.2, -3.2, Z0 + 2.1), (8.0, 0.0, Z0 + 2.2), 18.0)
    aim("NEXUS_V04_CAM_Servidores", (3.0, -12.8, Z0 + 2.1), (7.0, -9.0, Z0 + 2.2), 18.0)


clear()
analysis()
archive()
servers()
lights()
cameras()
bpy.context.scene.camera = bpy.data.objects.get("NEXUS_V04_CAM_Analisis")
bpy.context.scene.view_settings.exposure = 1.4
path = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V04_lab_detail_more.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
print("MORE_LABS_SAVED", path, os.path.getsize(path))
