"""Narrativa y detalle para ARCHIVO_SECRETO y BOMBEO_INUNDACION (L5)."""
import bpy
import math
import os
from mathutils import Vector, Matrix

ROOT = "/home/riyo/Documentos/game"
COLL = bpy.data.collections["NEXUS_STORY_LOWER"]


def mat(name):
    return bpy.data.materials.get(name)


def box(name, center, size, matname, bevel=0.008):
    m = bpy.data.meshes.new(name)
    x, y, z = size[0] / 2, size[1] / 2, size[2] / 2
    v = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
         (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    f = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
         (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    m.from_pydata(v, [], f)
    m.update()
    o = bpy.data.objects.new(name, m)
    COLL.objects.link(o)
    o.location = center
    mm = mat(matname)
    if mm:
        m.materials.append(mm)
    if bevel > 0:
        md = o.modifiers.new("Bevel", "BEVEL")
        md.width = bevel
        md.segments = 1
    return o


def cyl(name, center, radius, depth, matname, axis="Z", verts=14):
    m = bpy.data.meshes.new(name)
    vl = []
    for z in (-depth / 2, depth / 2):
        for i in range(verts):
            a = 2 * math.pi * i / verts
            vl.append((math.cos(a) * radius, math.sin(a) * radius, z))
    fs = []
    for i in range(verts):
        j = (i + 1) % verts
        fs.append((i, j, verts + j, verts + i))
    fs.append(tuple(range(verts - 1, -1, -1)))
    fs.append(tuple(range(verts, verts * 2)))
    m.from_pydata(vl, [], fs)
    m.update()
    o = bpy.data.objects.new(name, m)
    COLL.objects.link(o)
    o.location = center
    if axis == "X":
        o.rotation_euler.y = math.pi / 2
    elif axis == "Y":
        o.rotation_euler.x = math.pi / 2
    mm = mat(matname)
    if mm:
        m.materials.append(mm)
    return o


def sphere(name, center, radius, matname):
    m = bpy.data.meshes.new(name)
    verts = []
    faces = []
    rings = 8
    segs = 12
    for r in range(rings + 1):
        phi = math.pi * r / rings
        for s in range(segs):
            th = 2 * math.pi * s / segs
            verts.append((radius * math.sin(phi) * math.cos(th),
                          radius * math.sin(phi) * math.sin(th),
                          radius * math.cos(phi)))
    for r in range(rings):
        for s in range(segs):
            a = r * segs + s
            b = r * segs + (s + 1) % segs
            c = (r + 1) * segs + (s + 1) % segs
            d = (r + 1) * segs + s
            faces.append((a, b, c, d))
    m.from_pydata(verts, [], faces)
    m.update()
    o = bpy.data.objects.new(name, m)
    COLL.objects.link(o)
    o.location = center
    mm = mat(matname)
    if mm:
        m.materials.append(mm)
    return o


def sign(name, body, loc, normal, size):
    n = Vector(normal).normalized()
    up = Vector((0, 0, 1))
    if abs(n.dot(up)) > 0.95:
        up = Vector((0, 1, 0))
    right = up.cross(n).normalized()
    up2 = n.cross(right).normalized()
    rot = Matrix((right, up2, n)).transposed().to_4x4()
    plate = box(name + "_PLATE", Vector(loc), (size * 5.0, size * 1.3, 0.05),
                "NEXUS_SignPlate", 0.004)
    plate.matrix_world = Matrix.Translation(Vector(loc)) @ rot
    c = bpy.data.curves.new(name + "_TEXT", type="FONT")
    c.body = body
    c.align_x = "CENTER"
    c.align_y = "CENTER"
    c.size = size
    c.extrude = 0.004
    o = bpy.data.objects.new(c.name, c)
    COLL.objects.link(o)
    o.matrix_world = Matrix.Translation(Vector(loc) + n * 0.004) @ rot
    o.data.materials.append(mat("NEXUS_SignText") or mat("NEXUS_Amber"))


# ---------------- ARCHIVO_SECRETO ----------------
# Cuerpo desplomado contra el muro norte.
box("NEXUS_STORY_ARCH_BODY_TORSO", (16.9, -2.15, -43.18), (0.52, 0.34, 0.78), "NEXUS_Clinical")
box("NEXUS_STORY_ARCH_BODY_LEGS", (16.9, -2.72, -43.52), (0.40, 0.78, 0.18), "NEXUS_Rubber")
sphere("NEXUS_STORY_ARCH_BODY_HEAD", (16.9, -2.00, -42.70), 0.145, "NEXUS_Skin_Pale")
box("NEXUS_STORY_ARCH_BLOOD", (16.75, -2.45, -43.635), (1.0, 0.7, 0.02), "NEXUS_Blood_Dried", 0.002)
# Rastro de sangre hacia la puerta.
trail = [(15.8, -2.3), (15.0, -2.4), (14.2, -2.8), (13.65, -3.4),
         (13.55, -4.1), (13.6, -4.8)]
for i, (x, y) in enumerate(trail):
    box("NEXUS_STORY_ARCH_TRAIL_%d" % i, (x, y, -43.632),
        (0.34 + (i % 2) * 0.08, 0.24, 0.012), "NEXUS_Blood_Dried", 0.002)
# Papeles y cajas.
for i, (x, y, r) in enumerate([(15.2, -4.0, 0.3), (15.9, -4.3, -0.2),
                               (16.2, -3.6, 0.6), (17.3, -4.2, -0.5),
                               (17.9, -3.1, 0.15), (14.0, -5.1, 0.4)]):
    o = box("NEXUS_STORY_ARCH_PAPER_%d" % i, (x, y, -43.634),
            (0.30, 0.22, 0.006), "NEXUS_Paper", 0.001)
    o.rotation_euler.z = r
# Caja volcada con archivos.
box("NEXUS_STORY_ARCH_BOX", (13.85, -3.95, -43.46), (0.50, 0.40, 0.30), "NEXUS_Debris")
for i, (x, y, z) in enumerate([(13.75, -4.25, -43.58), (14.05, -4.35, -43.56),
                               (13.95, -4.10, -43.56)]):
    o = box("NEXUS_STORY_ARCH_FILE_%d" % i, (x, y, z), (0.28, 0.20, 0.05), "NEXUS_Paper", 0.002)
    o.rotation_euler.z = 0.25 - i * 0.2
# Terminal y expediente sobre el escritorio.
box("NEXUS_STORY_ARCH_MON", (16.05, -5.18, -42.62), (0.42, 0.05, 0.30), "NEXUS_MonitorScreen")
box("NEXUS_STORY_ARCH_KEYB", (16.05, -4.82, -42.79), (0.40, 0.16, 0.03), "NEXUS_Rubber")
box("NEXUS_STORY_ARCH_LOOT", (17.05, -5.02, -42.78), (0.36, 0.28, 0.07), "NEXUS_Paper", 0.003)
box("NEXUS_STORY_ARCH_LOOT_STRIPE", (17.05, -4.87, -42.785), (0.34, 0.05, 0.012), "NEXUS_Red", 0.0)
# Lámpara de emergencia roja.
box("NEXUS_STORY_ARCH_BEACON", (16.5, -1.66, -41.1), (0.28, 0.10, 0.14), "NEXUS_Painted_Metal")
ld = bpy.data.lights.new("NEXUS_STORY_ARCH_LIGHT", "POINT")
ld.color = (1.0, 0.05, 0.03)
ld.energy = 28
ld.shadow_soft_size = 0.18
lo = bpy.data.objects.new(ld.name, ld)
COLL.objects.link(lo)
lo.location = (16.5, -1.75, -41.1)
sign("NEXUS_STORY_ARCH_SIGN", "ARCHIVO // NIVEL 5", (13.16, -6.9, -41.45), (1, 0, 0), 0.11)
# Huella de mano en el muro oeste.
box("NEXUS_STORY_ARCH_HAND", (13.17, -3.2, -42.0), (0.02, 0.22, 0.30), "NEXUS_Blood_Dried", 0.002)

# ---------------- BOMBEO_INUNDACION ----------------
# Agua sobre la rejilla.
box("NEXUS_STORY_PUMP_WATER", (18.0, 1.72, -43.605), (7.6, 2.0, 0.02), "NEXUS_Meltwater", 0.0)
box("NEXUS_STORY_PUMP_WATER_EDGE", (18.0, 2.74, -43.612), (5.6, 0.18, 0.012), "NEXUS_Meltwater", 0.0)
# Fuga de la tubería.
cyl("NEXUS_STORY_PUMP_DRIP", (18.0, 6.9, -43.3), 0.035, 0.55, "NEXUS_Meltwater", "Z", 10)
box("NEXUS_STORY_PUMP_PUDDLE", (18.0, 6.7, -43.632), (0.9, 0.7, 0.012), "NEXUS_Meltwater", 0.0)
# Herramientas y cubo.
cyl("NEXUS_STORY_PUMP_BUCKET", (14.35, 6.55, -43.50), 0.19, 0.30, "NEXUS_Painted_Metal", "Z", 14)
cyl("NEXUS_STORY_PUMP_BUCKET_IN", (14.35, 6.55, -43.50), 0.16, 0.02, "NEXUS_Meltwater", "Z", 14)
box("NEXUS_STORY_PUMP_MOP", (14.75, 6.7, -43.05), (0.05, 0.05, 1.15), "NEXUS_Rust")
box("NEXUS_STORY_PUMP_MOP_HEAD", (14.75, 6.7, -43.55), (0.34, 0.18, 0.08), "NEXUS_Grime")
# Válvula en la tubería.
cyl("NEXUS_STORY_PUMP_VALVE", (18.0, 6.9, -42.2), 0.10, 0.18, "NEXUS_Rusted_Metal", "Z", 12)
for i in range(4):
    a = math.pi * i / 2
    box("NEXUS_STORY_PUMP_VALVE_ARM_%d" % i,
        (18.0 + math.cos(a) * 0.20, 6.9 + math.sin(a) * 0.20, -42.2),
        (0.36, 0.05, 0.05), "NEXUS_Rusted_Metal")
    bpy.data.objects["NEXUS_STORY_PUMP_VALVE_ARM_%d" % i].rotation_euler.z = a
# Salvavidas en el muro norte.
cyl("NEXUS_STORY_PUMP_RING", (21.6, 8.33, -41.9), 0.30, 0.10, "NEXUS_Amber", "Y", 16)
cyl("NEXUS_STORY_PUMP_RING_HOLE", (21.6, 8.33, -41.9), 0.18, 0.12, "NEXUS_Concrete_Dark", "Y", 16)
# Loot sobre el motor.
box("NEXUS_STORY_PUMP_LOOT", (20.0, 3.7, -41.40), (0.34, 0.26, 0.18), "NEXUS_Clinical")
box("NEXUS_STORY_PUMP_LOOT_STRIPE", (20.0, 3.7, -41.305), (0.32, 0.24, 0.02), "NEXUS_Amber", 0.0)
# Cartel y baliza.
sign("NEXUS_STORY_PUMP_SIGN", "BOMBEO // RIESGO DE INUNDACION", (13.16, 1.45, -41.45), (1, 0, 0), 0.09)
box("NEXUS_STORY_PUMP_BEACON", (21.8, 8.0, -41.2), (0.22, 0.10, 0.12), "NEXUS_Painted_Metal")
ld = bpy.data.lights.new("NEXUS_STORY_PUMP_LIGHT", "POINT")
ld.color = (1.0, 0.06, 0.03)
ld.energy = 30
ld.shadow_soft_size = 0.2
lo = bpy.data.objects.new(ld.name, ld)
COLL.objects.link(lo)
lo.location = (21.8, 7.85, -41.2)
# Marca de arrastre cerca de la rejilla.
for i, (x, y) in enumerate([(17.4, 2.9), (17.1, 3.4), (16.8, 3.9)]):
    box("NEXUS_STORY_PUMP_DRAG_%d" % i, (x, y, -43.634), (0.30, 0.16, 0.01), "NEXUS_Blood_Dried", 0.001)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "blender_concept", "FM_NEXUS_V05_level1_v74.blend"))
print("STORY_L5_A_DONE", len([o for o in bpy.data.objects if o.name.startswith("NEXUS_STORY_")]))
