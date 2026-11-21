"""Build a clean, larger Level 1 (access/services) for NEXUS."""
import bpy
import math
import os
from mathutils import Vector, Matrix

ROOT = "/home/riyo/Documentos/game"
Z0 = -5.8
SCENE = bpy.context.scene

# Hide the old level 1 geometry, not delete it.
for o in bpy.data.objects:
    if -6.6 < o.location.z < -5.0 and not o.name.startswith("NEXUS_V05_"):
        o.hide_render = True
        try:
            o.hide_set(True)
        except Exception:
            pass

parent = bpy.data.collections.get("NEXUS_V05_LEVEL1")
if parent is None:
    parent = bpy.data.collections.new("NEXUS_V05_LEVEL1")
    SCENE.collection.children.link(parent)


def sub(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        parent.children.link(c)
    return c


C_STRUCT = sub("V05_STRUCT")
C_PROPS = sub("V05_PROPS")
C_LIGHT = sub("V05_LIGHTS")
C_CAMS = sub("V05_CAMS")
C_STORY = sub("V05_STORY")


def mat(n):
    return bpy.data.materials.get(n)


def box(name, center, size, material, col, bevel=0.012):
    mesh = bpy.data.meshes.new(name)
    x, y, z = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
    verts = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
             (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    mesh.from_pydata(verts, [], faces); mesh.update()
    o = bpy.data.objects.new(name, mesh); col.objects.link(o); o.location = center
    if material: mesh.materials.append(material)
    if bevel > 0:
        m = o.modifiers.new("Bevel", "BEVEL"); m.width = bevel; m.segments = 1
    return o


def cyl(name, center, radius, depth, material, col, axis="Z", verts=16):
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
    o = bpy.data.objects.new(name, mesh); col.objects.link(o); o.location = center
    if axis == "X": o.rotation_euler.y = math.pi / 2
    elif axis == "Y": o.rotation_euler.x = math.pi / 2
    if material: mesh.materials.append(material)
    return o


def text(name, body, loc, normal, size, material, col=C_STRUCT):
    n = Vector(normal).normalized(); up = Vector((0, 0, 1))
    if abs(n.dot(up)) > 0.95: up = Vector((0, 1, 0))
    right = up.cross(n).normalized(); up2 = n.cross(right).normalized()
    rot = Matrix((right, up2, n)).transposed().to_4x4()
    box(name + "_PLATE", Vector(loc) - n * 0.03, (size * 5.0, size * 1.4, 0.06), mat("NEXUS_SignPlate") or mat("NEXUS_Concrete_Dark"), col)
    bpy.data.objects[name + "_PLATE"].matrix_world = Matrix.Translation(Vector(loc) - n * 0.04) @ rot
    c = bpy.data.curves.new(name + "_TEXT", type="FONT")
    c.body = body; c.align_x = "CENTER"; c.align_y = "CENTER"; c.size = size; c.extrude = 0.005
    o = bpy.data.objects.new(c.name, c); col.objects.link(o)
    o.matrix_world = Matrix.Translation(Vector(loc) + n * 0.002) @ rot
    o.data.materials.append(material)


def wall_x(name, x1, x2, y, z, height, material):
    if abs(x2 - x1) < 0.05: return
    box(name, ((x1 + x2) * 0.5, y, z), (abs(x2 - x1), 0.28, height), material, C_STRUCT)


def wall_y(name, y1, y2, x, z, height, material):
    if abs(y2 - y1) < 0.05: return
    box(name, (x, (y1 + y2) * 0.5, z), (0.28, abs(y2 - y1), height), material, C_STRUCT)


def door(name, x, y, side, height=3.2):
    base = Z0 + 0.02
    cz = base + height * 0.5
    box(name + "_L", (x - 0.86, y, cz), (0.12, 0.16, height), mat("NEXUS_Painted_Metal"), C_STRUCT, 0.008)
    box(name + "_R", (x + 0.86, y, cz), (0.12, 0.16, height), mat("NEXUS_Painted_Metal"), C_STRUCT, 0.008)
    box(name + "_TOP", (x, y, base + height + 0.06), (1.84, 0.16, 0.12), mat("NEXUS_Painted_Metal"), C_STRUCT, 0.008)
    box(name + "_LEAF", (x, y, cz), (1.62, 0.09, height - 0.08), mat("NEXUS_Painted_Metal"), C_STRUCT, 0.02)
    box(name + "_GLASS", (x, y + side * 0.02, cz + 0.4), (0.5, 0.11, 0.55), mat("NEXUS_Glass"), C_STRUCT, 0.01)
    box(name + "_HANDLE", (x + 0.55, y + side * 0.07, cz - 0.05), (0.04, 0.05, 0.38), mat("NEXUS_Steel"), C_STRUCT, 0.005)


def room(name, cx, cy, sx, sy, height, door_side, light_color, energy):
    x0, x1 = cx - sx / 2, cx + sx / 2
    y0, y1 = cy - sy / 2, cy + sy / 2
    zc = Z0 + height / 2
    box(f"NEXUS_V05_{name}_FLOOR", (cx, cy, Z0), (sx, sy, 0.3), mat("NEXUS_Concrete"), C_STRUCT, 0.02)
    box(f"NEXUS_V05_{name}_CEILING", (cx, cy, Z0 + height), (sx, sy, 0.24), mat("NEXUS_Concrete_Dark"), C_STRUCT, 0.02)
    for s, yy in (("N", y1), ("S", y0)):
        if (s == "N" and door_side == "N") or (s == "S" and door_side == "S"):
            wall_x(f"NEXUS_V05_{name}_WALL_{s}_A", x0, cx - 0.9, yy, zc, height, mat("NEXUS_Concrete"))
            wall_x(f"NEXUS_V05_{name}_WALL_{s}_B", cx + 0.9, x1, yy, zc, height, mat("NEXUS_Concrete"))
            box(f"NEXUS_V05_{name}_LINTEL_{s}", (cx, yy, Z0 + 3.45), (1.8, 0.28, 0.35), mat("NEXUS_Concrete"), C_STRUCT, 0.008)
            if height > 3.6:
                box(f"NEXUS_V05_{name}_ABOVE_{s}", (cx, yy, Z0 + 3.6 + (height - 3.6) * 0.5),
                    (1.8, 0.28, height - 3.6), mat("NEXUS_Concrete"), C_STRUCT, 0.008)
            door(f"NEXUS_V05_{name}_DOOR", cx, yy, 1 if s == "N" else -1)
        else:
            wall_x(f"NEXUS_V05_{name}_WALL_{s}", x0, x1, yy, zc, height, mat("NEXUS_Concrete"))
    wall_y(f"NEXUS_V05_{name}_WALL_W", y0, y1, x0, zc, height, mat("NEXUS_Concrete"))
    wall_y(f"NEXUS_V05_{name}_WALL_E", y0, y1, x1, zc, height, mat("NEXUS_Concrete"))
    # Baseboard and ceiling light.
    box(f"NEXUS_V05_{name}_BASE", (cx, y0 + 0.03, Z0 + 0.15), (sx - 0.1, 0.06, 0.12), mat("NEXUS_Painted_Metal"), C_STRUCT, 0.004)
    ld = bpy.data.lights.new(f"NEXUS_V05_{name}_LIGHT", "AREA")
    ld.color = light_color; ld.energy = energy; ld.shape = "RECTANGLE"; ld.size = min(3.0, sx * 0.4); ld.size_y = 0.4
    lo = bpy.data.objects.new(ld.name, ld); C_LIGHT.objects.link(lo); lo.location = (cx, cy, Z0 + height - 0.18)
    box(f"NEXUS_V05_{name}_STRIP", (cx, cy, Z0 + height - 0.12), (min(2.4, sx * 0.4), 0.1, 0.05), mat("NEXUS_CorridorLight"), C_LIGHT, 0.004)
    return x0, x1, y0, y1


# Corridor shell: x -22..22, y -1.7..1.7.
box("NEXUS_V05_CORR_FLOOR", (0, 0, Z0), (44.0, 3.4, 0.3), mat("NEXUS_Concrete"), C_STRUCT, 0.02)
box("NEXUS_V05_CORR_CEILING", (0, 0, Z0 + 4.2), (44.0, 3.4, 0.24), mat("NEXUS_Concrete_Dark"), C_STRUCT, 0.02)
for sx in (-22, 22):
    box(f"NEXUS_V05_CORR_END_{sx}", (sx, 0, Z0 + 2.1), (0.28, 3.4, 4.2), mat("NEXUS_Concrete"), C_STRUCT, 0.012)
    text(f"NEXUS_V05_CORR_END_SIGN_{sx}", "SALIDA", (sx - (0.02 if sx > 0 else -0.02), 0, Z0 + 3.25), (-1 if sx > 0 else 1, 0, 0), 0.13, mat("NEXUS_SignText") or mat("NEXUS_Amber"))
# Corridor lights, pipes and cable tray.
for i, x in enumerate(range(-19, 21, 4)):
    box(f"NEXUS_V05_CORR_STRIP_{i}", (x, 0, Z0 + 4.05), (2.1, 0.1, 0.05), mat("NEXUS_CorridorLight"), C_LIGHT, 0.004)
    ld = bpy.data.lights.new(f"NEXUS_V05_CORR_LIGHT_{i}", "AREA")
    ld.color = (0.62, 0.82, 1.0); ld.energy = 90; ld.shape = "RECTANGLE"; ld.size = 2.0; ld.size_y = 0.25
    lo = bpy.data.objects.new(ld.name, ld); C_LIGHT.objects.link(lo); lo.location = (x, 0, Z0 + 3.95)
for j, (y, m) in enumerate(((-1.05, "NEXUS_Rusted_Metal"), (1.05, "NEXUS_Steel"))):
    cyl(f"NEXUS_V05_CORR_PIPE_{j}", (0, y, Z0 + 3.55), 0.075, 43.0, mat(m), C_STRUCT, "X", 16)
box("NEXUS_V05_CORR_TRAY", (0, 0.95, Z0 + 3.5), (43.0, 0.3, 0.08), mat("NEXUS_Steel"), C_STRUCT, 0.006)

# Rooms: larger than the old 7x6/8x7 grid.
room("RECEPCION", -12, 6.7, 16, 10, 6.0, "S", (0.92, 0.90, 0.82), 520)
room("SEGURIDAD", 3, 5.7, 10, 8, 4.2, "S", (0.72, 0.84, 1.0), 450)
room("CONTROL_ACCESO", 13, 5.7, 8, 8, 4.2, "S", (0.62, 0.82, 1.0), 400)
room("VESTUARIOS", -14, -5.7, 10, 8, 4.0, "N", (0.92, 0.88, 0.78), 380)
room("ALMACEN", -2, -5.7, 12, 8, 4.2, "N", (1.0, 0.70, 0.32), 320)
room("MANTENIMIENTO", 13, -5.7, 14, 8, 5.0, "N", (1.0, 0.52, 0.16), 380)

# Close the corridor gaps between rooms with wall segments.
for yy, spans in ((1.7, [(-4, -2), (8, 9), (17, 22)]), (-1.7, [(-22, -19), (-9, -8), (4, 6), (20, 22)])):
    for i, (a, b) in enumerate(spans):
        box(f"NEXUS_V05_GAP_{yy}_{i}", ((a + b) / 2, yy, Z0 + 2.1), (abs(b - a), 0.28, 4.2), mat("NEXUS_Concrete"), C_STRUCT, 0.012)

# Reception: desk, bench, planters, sign.
box("NEXUS_V05_REC_DESK", (-12, 8.0, Z0 + 0.82), (4.2, 1.2, 0.08), mat("NEXUS_Steel"), C_PROPS, 0.02)
box("NEXUS_V05_REC_DESK_FRONT", (-12, 8.5, Z0 + 0.45), (4.0, 0.15, 0.9), mat("NEXUS_Painted_Metal"), C_PROPS, 0.01)
for i, x in enumerate((-14, -10)):
    box(f"NEXUS_V05_REC_CHAIR_{i}", (x, 9.6, Z0 + 0.5), (0.55, 0.55, 0.1), mat("NEXUS_Rubber"), C_PROPS, 0.03)
    box(f"NEXUS_V05_REC_CHAIR_BACK_{i}", (x, 9.85, Z0 + 0.95), (0.55, 0.1, 0.8), mat("NEXUS_Rubber"), C_PROPS, 0.03)
box("NEXUS_V05_REC_BENCH", (-18.5, 4.0, Z0 + 0.45), (0.8, 4.0, 0.1), mat("NEXUS_Painted_Metal"), C_PROPS, 0.015)
for i, x in enumerate((-18.0, -6.0)):
    box(f"NEXUS_V05_REC_PLANTER_{i}", (x, 3.0, Z0 + 0.45), (0.8, 0.8, 0.9), mat("NEXUS_Painted_Metal"), C_PROPS, 0.02)
    cyl(f"NEXUS_V05_REC_PLANT_{i}", (x, 3.0, Z0 + 1.2), 0.3, 0.8, mat("NEXUS_Green"), C_PROPS, "Z", 12)
text("NEXUS_V05_REC_SIGN", "NEXUS // RECEPCION", (-12, 11.6, Z0 + 4.0), (0, 1, 0), 0.18, mat("NEXUS_SignText") or mat("NEXUS_Amber"))

# Security: desk, monitors, lockers, camera station.
box("NEXUS_V05_SEC_DESK", (3, 6.0, Z0 + 0.82), (3.8, 1.1, 0.08), mat("NEXUS_Steel"), C_PROPS, 0.02)
for i, x in enumerate((1.8, 3.0, 4.2)):
    box(f"NEXUS_V05_SEC_MON_{i}", (x, 6.3, Z0 + 1.5), (0.5, 0.04, 0.35), mat("NEXUS_Screen"), C_PROPS, 0.005)
for i, x in enumerate((0.0, 6.0)):
    box(f"NEXUS_V05_SEC_LOCKER_{i}", (x, 8.0, Z0 + 1.2), (0.9, 0.5, 2.2), mat("NEXUS_Painted_Metal"), C_PROPS, 0.015)
box("NEXUS_V05_SEC_CAMERA", (6.4, 3.0, Z0 + 2.8), (0.35, 0.35, 0.25), mat("NEXUS_Steel"), C_PROPS, 0.02)
box("NEXUS_V05_SEC_BLOOD", (5.3, 5.2, Z0 + 0.02), (0.8, 0.4, 0.02), mat("NEXUS_Blood_Dried"), C_STORY, 0.002)

# Access control: barriers and consoles.
for i, x in enumerate((10.5, 13.0, 15.5)):
    box(f"NEXUS_V05_ACC_BARRIER_{i}", (x, 4.0, Z0 + 0.55), (0.35, 1.9, 0.08), mat("NEXUS_Steel"), C_PROPS, 0.01)
    box(f"NEXUS_V05_ACC_POST_{i}", (x, 3.0, Z0 + 0.55), (0.22, 0.22, 1.1), mat("NEXUS_Painted_Metal"), C_PROPS, 0.01)
box("NEXUS_V05_ACC_CONSOLE", (13.0, 8.0, Z0 + 0.9), (2.4, 0.9, 0.1), mat("NEXUS_Steel"), C_PROPS, 0.015)
box("NEXUS_V05_ACC_SCREEN", (13.0, 8.4, Z0 + 1.5), (1.1, 0.05, 0.6), mat("NEXUS_Screen"), C_PROPS, 0.006)

# Locker room: lockers and benches.
for i, x in enumerate((-18.4, -17.3, -16.2, -15.1, -14.0, -12.9, -11.8, -10.7)):
    box(f"NEXUS_V05_LOCK_LOCKER_{i}", (x, -9.2, Z0 + 1.2), (0.85, 0.45, 2.2), mat("NEXUS_Painted_Metal"), C_PROPS, 0.012)
box("NEXUS_V05_LOCK_BENCH", (-14.0, -5.0, Z0 + 0.45), (6.0, 0.8, 0.1), mat("NEXUS_Painted_Metal"), C_PROPS, 0.015)
for i, x in enumerate((-16.0, -12.0)):
    box(f"NEXUS_V05_LOCK_BAG_{i}", (x, -4.8, Z0 + 0.6), (0.6, 0.5, 0.4), mat("NEXUS_Rubber"), C_PROPS, 0.04)
text("NEXUS_V05_LOCK_SIGN", "VESTUARIOS", (-14, -1.5, Z0 + 2.8), (0, 1, 0), 0.13, mat("NEXUS_SignText") or mat("NEXUS_Amber"))

# Storage: shelves, crates, barrels.
for i, x in enumerate((-7.0, -5.0, -3.0, -1.0, 1.0)):
    box(f"NEXUS_V05_STORE_SHELF_{i}", (x, -8.0, Z0 + 1.2), (0.8, 0.55, 2.4), mat("NEXUS_Painted_Metal"), C_PROPS, 0.012)
    for j in range(3):
        box(f"NEXUS_V05_STORE_BOX_{i}_{j}", (x, -8.0, Z0 + 0.5 + j * 0.65), (0.65, 0.42, 0.32), mat("NEXUS_Debris"), C_PROPS, 0.006)
for i, (x, y) in enumerate(((4.0, -8.0), (5.0, -7.5), (6.0, -8.3))):
    cyl(f"NEXUS_V05_STORE_BARREL_{i}", (x, y, Z0 + 0.48), 0.33, 0.95, mat("NEXUS_Rusted_Metal"), C_PROPS, "Z", 16)
text("NEXUS_V05_STORE_SIGN", "ALMACEN", (-2, -1.5, Z0 + 2.8), (0, 1, 0), 0.13, mat("NEXUS_SignText") or mat("NEXUS_Amber"))

# Maintenance: generator, pipes, tools, hazard.
box("NEXUS_V05_MAINT_GEN", (13.0, -8.0, Z0 + 1.3), (3.2, 2.2, 2.6), mat("NEXUS_Steel"), C_PROPS, 0.03)
box("NEXUS_V05_MAINT_PANEL", (13.0, -6.85, Z0 + 1.5), (1.5, 0.05, 1.0), mat("NEXUS_Screen"), C_PROPS, 0.006)
for i, y in enumerate((-9.0, -6.0)):
    box(f"NEXUS_V05_MAINT_PIPE_{i}", (13.0, y, Z0 + 3.6), (12.0, 0.18, 0.18), mat("NEXUS_Rusted_Metal"), C_PROPS, 0.01)
box("NEXUS_V05_MAINT_HAZARD", (13.0, -2.2, Z0 + 0.02), (3.0, 0.4, 0.02), mat("NEXUS_Amber"), C_STRUCT, 0.002)
for i in range(6):
    box(f"NEXUS_V05_MAINT_DEBRIS_{i}", (9.0 + i * 0.6, -4.5 + (i % 2) * 0.5, Z0 + 0.05), (0.18, 0.12, 0.06), mat("NEXUS_Debris"), C_STORY, 0.003)
text("NEXUS_V05_MAINT_SIGN", "MANTENIMIENTO", (13, -1.5, Z0 + 2.8), (0, 1, 0), 0.13, mat("NEXUS_SignText") or mat("NEXUS_Amber"))

# Cameras.
def camera(name, loc, target, lens):
    cd = bpy.data.cameras.new(name); co = bpy.data.objects.new(name, cd); C_CAMS.objects.link(co)
    co.location = Vector(loc); cd.lens = lens
    f = (Vector(target) - co.location).normalized(); up = Vector((0, 0, 1))
    if abs(f.dot(up)) > 0.98: up = Vector((0, 1, 0))
    right = f.cross(up).normalized(); up2 = right.cross(f).normalized()
    co.matrix_world = Matrix.Translation(co.location) @ Matrix((right, up2, -f)).transposed().to_4x4()
    return co

camera("NEXUS_V05_CAM_Corridor", (-21.0, 0.0, Z0 + 2.0), (18.0, 0.0, Z0 + 2.0), 20.0)
camera("NEXUS_V05_CAM_Recepcion", (-4.0, 3.0, Z0 + 2.2), (-14.0, 8.0, Z0 + 2.2), 20.0)
camera("NEXUS_V05_CAM_Seguridad", (0.0, 3.0, Z0 + 2.2), (3.0, 7.0, Z0 + 2.0), 20.0)
SCENE.camera = bpy.data.objects["NEXUS_V05_CAM_Corridor"]
SCENE.view_settings.exposure = 1.45
SCENE.render.engine = "BLENDER_EEVEE"
SCENE.eevee.taa_render_samples = 64
SCENE.render.resolution_x = 1920
SCENE.render.resolution_y = 1080

path = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V05_level1.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
print("LEVEL1_SAVED", path, os.path.getsize(path))
