"""Detail the V04 biology/chemistry rooms and close the mezzanine edge."""
import bpy
import math
import os
from mathutils import Vector, Matrix

ROOT = "/home/riyo/Documentos/game"
SCENE = bpy.context.scene
Z0 = -13.8
COLL = bpy.data.collections.get("NEXUS_V04_DETAIL")
PREFIX = "NEXUS_LAB_V04_"


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


def sign(name, body, loc, normal, size, material):
    n = Vector(normal).normalized()
    up = Vector((0, 0, 1))
    if abs(n.dot(up)) > 0.95: up = Vector((0, 1, 0))
    right = up.cross(n).normalized()
    up2 = n.cross(right).normalized()
    rot = Matrix((right, up2, n)).transposed().to_4x4()
    plate = box(PREFIX + name + "_PLATE", Vector(loc) - n * 0.03, (size * 5.0, size * 1.4, 0.06), mat("NEXUS_SignPlate") or mat("NEXUS_Concrete_Dark"))
    plate.matrix_world = Matrix.Translation(Vector(loc) - n * 0.04) @ rot
    curve = bpy.data.curves.new(PREFIX + name + "_TEXT", type="FONT")
    curve.body = body; curve.align_x = "CENTER"; curve.align_y = "CENTER"
    curve.size = size; curve.extrude = 0.005
    txt = bpy.data.objects.new(curve.name, curve); COLL.objects.link(txt)
    txt.matrix_world = Matrix.Translation(Vector(loc) + n * 0.002) @ rot
    txt.data.materials.append(material)


def bench(name, x, y, sx, sy):
    top = Z0 + 0.92
    box(PREFIX + name + "_TOP", (x, y, top), (sx, sy, 0.08), mat("NEXUS_Steel"))
    for dx in (-sx * 0.42, sx * 0.42):
        for dy in (-sy * 0.32, sy * 0.32):
            box(f"{PREFIX}{name}_LEG_{dx}_{dy}", (x + dx, y + dy, Z0 + 0.45), (0.07, 0.07, 0.86), mat("NEXUS_Painted_Metal"))
    box(PREFIX + name + "_SHELF", (x, y, Z0 + 0.38), (sx * 0.9, sy * 0.7, 0.04), mat("NEXUS_Painted_Metal"), 0.004)


def tank(name, x, y):
    goo = mat("NEXUS_GooTrans") or mat("NEXUS_Green")
    cyl(PREFIX + name + "_GLASS", (x, y, Z0 + 1.45), 0.55, 2.1, mat("NEXUS_Glass"), "Z", 24)
    cyl(PREFIX + name + "_GOO", (x, y, Z0 + 0.95), 0.44, 0.9, goo, "Z", 24)
    cyl(PREFIX + name + "_BASE", (x, y, Z0 + 0.45), 0.65, 0.22, mat("NEXUS_Steel"), "Z", 24)
    cyl(PREFIX + name + "_TOP", (x, y, Z0 + 2.55), 0.65, 0.18, mat("NEXUS_Steel"), "Z", 24)
    box(PREFIX + name + "_SPEC", (x, y, Z0 + 1.4), (0.28, 0.22, 1.1), mat("NEXUS_Concrete_Dark"), 0.06)


def monitor(name, x, y, z, w=0.7, h=0.45):
    box(PREFIX + name + "_FRAME", (x, y, z), (w + 0.06, 0.05, h + 0.06), mat("NEXUS_Painted_Metal"))
    box(PREFIX + name + "_SCREEN", (x, y - 0.035, z), (w, 0.02, h), mat("NEXUS_Screen"), 0.003)
    box(PREFIX + name + "_STAND", (x, y + 0.10, z - 0.28), (0.08, 0.18, 0.28), mat("NEXUS_Steel"), 0.004)


def biology():
    # West/north benches, three containment tanks, console and gurney.
    bench("BIO_BENCH_W1", -15.5, -9.5, 0.9, 3.0)
    bench("BIO_BENCH_W2", -15.5, -13.8, 0.9, 3.0)
    bench("BIO_BENCH_N", -10.0, -8.2, 4.0, 0.9)
    for i, x in enumerate((-14.4, -11.2, -8.0)):
        tank(f"BIO_TANK_{i}", x, -15.2)
    # Console on the east side, away from the door.
    bench("BIO_CONSOLE", -5.2, -8.8, 2.2, 0.9)
    for i, x in enumerate((-5.9, -5.2, -4.5)):
        monitor(f"BIO_MON_{i}", x, -9.3, Z0 + 1.52, 0.55, 0.38)
    # Gurney and body bag.
    box(PREFIX + "BIO_GURNEY", (-8.0, -14.6, Z0 + 0.78), (1.9, 0.65, 0.1), mat("NEXUS_Steel"), 0.02)
    for dx in (-0.75, 0.75):
        for dy in (-0.25, 0.25):
            box(f"{PREFIX}BIO_GURNEY_LEG_{dx}_{dy}", (-8.0 + dx, -14.6 + dy, Z0 + 0.38), (0.06, 0.06, 0.72), mat("NEXUS_Steel"))
    box(PREFIX + "BIO_BODY", (-8.0, -14.6, Z0 + 0.98), (1.75, 0.55, 0.25), mat("NEXUS_Rubber"), 0.14)
    box(PREFIX + "BIO_BODY_HEAD", (-7.1, -14.6, Z0 + 0.98), (0.28, 0.34, 0.25), mat("NEXUS_Rubber"), 0.12)
    # Cabinets, bottles, blood and debris.
    box(PREFIX + "BIO_CABINET", (-16.3, -8.0, Z0 + 1.2), (0.8, 0.45, 2.2), mat("NEXUS_Painted_Metal"), 0.02)
    for i in range(6):
        cyl(f"{PREFIX}BIO_BOTTLE_{i}", (-15.0 + (i % 3) * 0.35, -9.0 + (i // 3) * 0.3, Z0 + 1.05), 0.055, 0.22, mat("NEXUS_Glass"), "Z", 12)
    box(PREFIX + "BIO_BLOOD", (-7.0, -11.5, Z0 + 0.02), (1.8, 0.9, 0.02), mat("NEXUS_Blood_Dried"), 0.002)
    box(PREFIX + "BIO_BLOOD_2", (-9.8, -13.0, Z0 + 0.02), (0.8, 0.4, 0.02), mat("NEXUS_Blood_Dried"), 0.002)
    for i in range(8):
        box(f"{PREFIX}BIO_DEBRIS_{i}", (-13.0 + i * 0.55, -11.0 + (i % 3) * 0.4, Z0 + 0.04), (0.16, 0.1, 0.05), mat("NEXUS_Debris"), 0.003)
    # Ceiling pipe and cable tray.
    cyl(PREFIX + "BIO_PIPE", (-10.0, -8.5, Z0 + 4.3), 0.10, 12.0, mat("NEXUS_Rusted_Metal"), "X", 16)
    box(PREFIX + "BIO_TRAY", (-10.0, -9.1, Z0 + 4.25), (12.0, 0.3, 0.08), mat("NEXUS_Steel"), 0.005)
    sign("BIO_SIGN", "LABORATORIO DE BIOLOGIA", (-16.84, -12.0, Z0 + 3.2), (1, 0, 0), 0.15, mat("NEXUS_SignText") or mat("NEXUS_Amber"))


def chemistry():
    # Benches, fume hood, barrels, spill and hazard.
    bench("CHEM_BENCH_N", -10.0, 22.4, 6.5, 0.9)
    bench("CHEM_BENCH_W", -15.3, 19.5, 0.9, 3.5)
    box(PREFIX + "CHEM_HOOD", (-14.5, 20.5, Z0 + 1.25), (2.2, 1.2, 2.5), mat("NEXUS_Painted_Metal"), 0.02)
    box(PREFIX + "CHEM_HOOD_GLASS", (-13.38, 20.5, Z0 + 1.55), (0.04, 1.0, 1.4), mat("NEXUS_Glass"), 0.01)
    for i, (x, y) in enumerate(((-5.5, 21.8), (-4.8, 22.4), (-6.2, 22.5))):
        cyl(f"{PREFIX}CHEM_BARREL_{i}", (x, y, Z0 + 0.48), 0.33, 0.95, mat("NEXUS_Rusted_Metal"), "Z", 16)
    box(PREFIX + "CHEM_SPILL", (-9.0, 19.0, Z0 + 0.02), (1.8, 1.1, 0.02), mat("NEXUS_Blood_Dried"), 0.002)
    box(PREFIX + "CHEM_HAZARD", (-10.0, 14.6, Z0 + 0.02), (2.4, 0.3, 0.02), mat("NEXUS_Amber"), 0.002)
    for i in range(8):
        box(f"{PREFIX}CHEM_DEBRIS_{i}", (-13.0 + i * 0.6, 18.0 + (i % 2) * 0.5, Z0 + 0.04), (0.15, 0.1, 0.05), mat("NEXUS_Debris"), 0.003)
    monitor("CHEM_MON", -10.0, 16.2, Z0 + 1.8, 0.8, 0.5)
    sign("CHEM_SIGN", "LABORATORIO QUIMICA", (-15.84, 19.0, Z0 + 3.2), (1, 0, 0), 0.15, mat("NEXUS_SignText") or mat("NEXUS_Amber"))


def mezzanine_edge():
    # Close the open edge of the mezzanine with a simple guardrail.
    x = -12.4
    z = Z0 + 3.55
    for i in range(5):
        y = -2.0 + i * 2.0
        box(f"{PREFIX}MEZZ_POST_{i}", (x, y, z + 0.55), (0.06, 0.06, 1.1), mat("NEXUS_Steel"))
    box(PREFIX + "MEZZ_BAR_0", (x, 2.0, z + 0.5), (0.05, 8.0, 0.05), mat("NEXUS_Steel"))
    box(PREFIX + "MEZZ_BAR_1", (x, 2.0, z + 1.0), (0.05, 8.0, 0.05), mat("NEXUS_Steel"))
    box(PREFIX + "MEZZ_TRIM", (x, 2.0, z + 0.05), (0.12, 8.0, 0.12), mat("NEXUS_Steel"))
    # Dark backs for the three console monitors.
    for i, x2 in enumerate((-13.0, -12.0, -11.0)):
        box(f"{PREFIX}MON_BACK_{i}", (x2, 0.26, Z0 + 1.45), (0.82, 0.05, 0.58), mat("NEXUS_Painted_Metal"), 0.006)


for o in list(bpy.data.objects):
    if o.name.startswith(PREFIX):
        bpy.data.objects.remove(o, do_unlink=True)

biology()
chemistry()
mezzanine_edge()
SCENE.view_settings.exposure = 1.4
path = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V04_lab_detail.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
print("LAB_DETAIL_SAVED", path, os.path.getsize(path))
