"""Build a clean, validated laboratory level for the NEXUS complex.

This replaces the old, overlapping level -2 with a compact vertical-slice
layout: one central corridor, three rooms on each side, real doors, props,
lighting, damage and narrative. Old level -2 objects are hidden, not deleted.
"""
import bpy
import math
import os
from mathutils import Vector, Matrix

ROOT = "/home/riyo/Documentos/game"
SCENE = bpy.context.scene
Z_FLOOR = -13.8
Z_CEIL = -10.2
WALL_H = 3.6
WALL_T = 0.25

# Hide the old lab level. The backup and new version keep it recoverable.
for o in bpy.data.objects:
    if -14.6 < o.location.z < -9.5 and not o.name.startswith("NEXUS_V03_"):
        o.hide_render = True
        try:
            o.hide_set(True)
        except Exception:
            pass

parent = bpy.data.collections.get("NEXUS_V03_LAB_LEVEL")
if parent is None:
    parent = bpy.data.collections.new("NEXUS_V03_LAB_LEVEL")
    SCENE.collection.children.link(parent)


def sub(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        parent.children.link(c)
    return c


C_STRUCT = sub("NEXUS_V03_LAB_STRUCT")
C_PROPS = sub("NEXUS_V03_LAB_PROPS")
C_LIGHT = sub("NEXUS_V03_LAB_LIGHTS")
C_CAMS = sub("NEXUS_V03_LAB_CAMS")
C_STORY = sub("NEXUS_V03_LAB_STORY")


def mat(name):
    return bpy.data.materials.get(name)


def box(name, center, size, material, col, bevel=0.015):
    mesh = bpy.data.meshes.new(name)
    x, y, z = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
    verts = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
             (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    obj.location = center
    if material:
        mesh.materials.append(material)
    if bevel > 0:
        m = obj.modifiers.new("Bevel", "BEVEL")
        m.width = bevel
        m.segments = 1
    return obj


def cylinder(name, center, radius, depth, material, col, axis="Z", vertices=24):
    mesh = bpy.data.meshes.new(name)
    verts = []
    for z in (-depth * 0.5, depth * 0.5):
        for i in range(vertices):
            a = 2.0 * math.pi * i / vertices
            verts.append((math.cos(a) * radius, math.sin(a) * radius, z))
    faces = []
    for i in range(vertices):
        j = (i + 1) % vertices
        faces.append((i, j, vertices + j, vertices + i))
    faces.append(tuple(range(vertices - 1, -1, -1)))
    faces.append(tuple(range(vertices, vertices * 2)))
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    obj.location = center
    if axis == "X":
        obj.rotation_euler.y = math.pi / 2
    elif axis == "Y":
        obj.rotation_euler.x = math.pi / 2
    if material:
        mesh.materials.append(material)
    return obj


def text(name, body, loc, size, rot_x, material, col):
    curve = bpy.data.curves.new(name, type="FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    curve.extrude = 0.006
    obj = bpy.data.objects.new(name, curve)
    col.objects.link(obj)
    obj.location = loc
    obj.rotation_euler.x = rot_x
    if material:
        obj.data.materials.append(material)
    return obj


def wall_segment(name, x1, x2, y, z, height, material, horizontal=True):
    if horizontal:
        w = abs(x2 - x1)
        if w < 0.03:
            return None
        return box(name, Vector(((x1 + x2) * 0.5, y, z)), (w, WALL_T, height), material, C_STRUCT, 0.012)
    h = abs(x2 - x1)
    if h < 0.03:
        return None
    return box(name, Vector((y, (x1 + x2) * 0.5, z)), (WALL_T, h, height), material, C_STRUCT, 0.012)


def door(x, y, side, room):
    # side: +1 means the room is north of the corridor (door faces -Y),
    # -1 means the room is south (door faces +Y).
    yaw = 0.0
    frame_y = y
    w = 1.6
    h = 3.2
    base_z = Z_FLOOR + 0.15
    center_z = base_z + h * 0.5
    jamb = mat("NEXUS_Painted_Metal")
    box(f"NEXUS_V03_DOOR_{room}_L", (x - w * 0.5 - 0.06, frame_y, center_z), (0.12, 0.16, h), jamb, C_STRUCT, 0.008)
    box(f"NEXUS_V03_DOOR_{room}_R", (x + w * 0.5 + 0.06, frame_y, center_z), (0.12, 0.16, h), jamb, C_STRUCT, 0.008)
    box(f"NEXUS_V03_DOOR_{room}_TOP", (x, frame_y, base_z + h + 0.06), (w + 0.24, 0.16, 0.12), jamb, C_STRUCT, 0.008)
    leaf = box(f"NEXUS_V03_DOOR_LEAF_{room}", (x, frame_y, center_z), (w - 0.08, 0.09, h - 0.08), mat("NEXUS_Painted_Metal"), C_STRUCT, 0.02)
    box(f"NEXUS_V03_DOOR_GLASS_{room}", (x, frame_y + side * 0.02, center_z + 0.35), (0.5, 0.11, 0.55), mat("NEXUS_Glass"), C_STRUCT, 0.01)
    box(f"NEXUS_V03_DOOR_HANDLE_{room}", (x + 0.55, frame_y + side * 0.07, center_z - 0.05), (0.04, 0.05, 0.38), mat("NEXUS_Steel"), C_STRUCT, 0.005)
    box(f"NEXUS_V03_DOOR_KICK_{room}", (x, frame_y, base_z + 0.15), (w - 0.18, 0.02, 0.08), mat("NEXUS_Amber"), C_STRUCT, 0.004)
    sign_y = frame_y + side * 0.14
    box(f"NEXUS_V03_SIGN_PLATE_{room}", (x, sign_y, base_z + h + 0.32), (1.6, 0.04, 0.28), mat("NEXUS_Concrete_Dark"), C_STRUCT, 0.006)
    text(f"NEXUS_V03_SIGN_TEXT_{room}", room.replace("_", " "), (x, sign_y + side * 0.005, base_z + h + 0.32), 0.15, -math.pi / 2 if side > 0 else math.pi / 2, mat("NEXUS_Amber"), C_STRUCT)


def room(name, cx, cy, sx, sy, door_side, light_color, light_energy=480.0):
    # door_side: "N" means corridor is north of room; "S" means south.
    x0, x1 = cx - sx * 0.5, cx + sx * 0.5
    y0, y1 = cy - sy * 0.5, cy + sy * 0.5
    box(f"NEXUS_V03_{name}_FLOOR", (cx, cy, Z_FLOOR), (sx, sy, 0.3), mat("NEXUS_Concrete"), C_STRUCT, 0.02)
    box(f"NEXUS_V03_{name}_CEILING", (cx, cy, Z_CEIL), (sx, sy, 0.24), mat("NEXUS_Concrete_Dark"), C_STRUCT, 0.02)
    # Outer walls. Corridor-facing wall gets an opening and a door.
    for side, yy in (("S", y0), ("N", y1)):
        if side == "N" and door_side == "N":
            wall_segment(f"NEXUS_V03_{name}_WALL_N_A", x0, cx - 0.8, yy, Z_FLOOR + WALL_H * 0.5, WALL_H, mat("NEXUS_Concrete"))
            wall_segment(f"NEXUS_V03_{name}_WALL_N_B", cx + 0.8, x1, yy, Z_FLOOR + WALL_H * 0.5, WALL_H, mat("NEXUS_Concrete"))
            box(f"NEXUS_V03_{name}_LINTEL_N", (cx, yy, Z_FLOOR + 3.45), (1.6, WALL_T, 0.3), mat("NEXUS_Concrete"), C_STRUCT, 0.008)
            door(cx, yy, 1, name)
        elif side == "S" and door_side == "S":
            wall_segment(f"NEXUS_V03_{name}_WALL_S_A", x0, cx - 0.8, yy, Z_FLOOR + WALL_H * 0.5, WALL_H, mat("NEXUS_Concrete"))
            wall_segment(f"NEXUS_V03_{name}_WALL_S_B", cx + 0.8, x1, yy, Z_FLOOR + WALL_H * 0.5, WALL_H, mat("NEXUS_Concrete"))
            box(f"NEXUS_V03_{name}_LINTEL_S", (cx, yy, Z_FLOOR + 3.45), (1.6, WALL_T, 0.3), mat("NEXUS_Concrete"), C_STRUCT, 0.008)
            door(cx, yy, -1, name)
        else:
            wall_segment(f"NEXUS_V03_{name}_WALL_{side}", x0, x1, yy, Z_FLOOR + WALL_H * 0.5, WALL_H, mat("NEXUS_Concrete"))
    for side, xx in (("W", x0), ("E", x1)):
        wall_segment(f"NEXUS_V03_{name}_WALL_{side}", y0, y1, xx, Z_FLOOR + WALL_H * 0.5, WALL_H, mat("NEXUS_Concrete"), horizontal=False)
    # Baseboard trim.
    for side, yy in (("S", y0 + 0.02), ("N", y1 - 0.02)):
        box(f"NEXUS_V03_{name}_BASE_{side}", (cx, yy, Z_FLOOR + 0.15), (sx - 0.1, 0.06, 0.12), mat("NEXUS_Painted_Metal"), C_STRUCT, 0.005)
    # Ceiling light.
    ld = bpy.data.lights.new(f"NEXUS_V03_{name}_LIGHT", "AREA")
    ld.color = light_color
    ld.energy = light_energy
    ld.shape = "RECTANGLE"
    ld.size = min(2.0, sx * 0.35)
    ld.size_y = 0.35
    lo = bpy.data.objects.new(ld.name, ld)
    C_LIGHT.objects.link(lo)
    lo.location = (cx, cy, Z_CEIL - 0.18)
    box(f"NEXUS_V03_{name}_LIGHT_HOUSING", (cx, cy, Z_CEIL - 0.10), (min(2.0, sx * 0.35), 0.14, 0.06), mat("NEXUS_Painted_Metal"), C_LIGHT, 0.004)
    # Hazard strip at the door threshold.
    door_y = y0 if door_side == "S" else y1
    box(f"NEXUS_V03_{name}_THRESHOLD", (cx, door_y, Z_FLOOR + 0.16), (1.7, 0.26, 0.02), mat("NEXUS_Amber"), C_STRUCT, 0.003)


# ---------------------------------------------------------------- corridor
CORR_X = 15.6
CORR_W = 2.8
box("NEXUS_V03_CORRIDOR_FLOOR", (0, 0, Z_FLOOR), (CORR_X * 2, CORR_W, 0.3), mat("NEXUS_Concrete"), C_STRUCT, 0.02)
box("NEXUS_V03_CORRIDOR_CEILING", (0, 0, Z_CEIL), (CORR_X * 2, CORR_W, 0.24), mat("NEXUS_Concrete_Dark"), C_STRUCT, 0.02)
# End walls with emergency doors.
for sx in (-1, 1):
    x = sx * CORR_X
    box(f"NEXUS_V03_CORRIDOR_END_{sx}", (x, 0, Z_FLOOR + WALL_H * 0.5), (WALL_T, CORR_W, WALL_H), mat("NEXUS_Concrete"), C_STRUCT, 0.012)
    box(f"NEXUS_V03_CORRIDOR_END_SIGN_{sx}", (x - sx * 0.01, 0, Z_FLOOR + 3.48), (0.02, 1.8, 0.22), mat("NEXUS_Concrete_Dark"), C_STRUCT, 0.004)
    text(f"NEXUS_V03_CORRIDOR_END_TEXT_{sx}", "SALIDA", (x - sx * 0.02, 0, Z_FLOOR + 3.48), 0.14, math.pi / 2 * sx, mat("NEXUS_Amber"), C_STRUCT)
# Ceiling light strips and practical area lights.
for i, x in enumerate(range(-13, 14, 4)):
    box(f"NEXUS_V03_CORR_STRIP_{i}", (x, 0, Z_CEIL - 0.12), (2.2, 0.10, 0.06), mat("NEXUS_CorridorLight"), C_LIGHT, 0.004)
    ld = bpy.data.lights.new(f"NEXUS_V03_CORR_LIGHT_{i}", "AREA")
    ld.color = (0.62, 0.84, 1.0)
    ld.energy = 95.0
    ld.shape = "RECTANGLE"
    ld.size = 2.0
    ld.size_y = 0.25
    lo = bpy.data.objects.new(ld.name, ld)
    C_LIGHT.objects.link(lo)
    lo.location = (x, 0, Z_CEIL - 0.22)
# Pipes and cable tray along the corridor ceiling.
for j, (yy, m) in enumerate(((-1.05, "NEXUS_Rusted_Metal"), (1.05, "NEXUS_Steel"))):
    cylinder(f"NEXUS_V03_CORR_PIPE_{j}", (0, yy, Z_CEIL - 0.42), 0.075, CORR_X * 2 - 0.4, mat(m), C_STRUCT, "X", 16)
box("NEXUS_V03_CORR_TRAY", (0, 0.9, Z_CEIL - 0.45), (CORR_X * 2 - 0.5, 0.32, 0.08), mat("NEXUS_Steel"), C_STRUCT, 0.006)
for i in range(5):
    box(f"NEXUS_V03_CORR_CABLE_{i}", (0, 0.9 + (i - 2) * 0.05, Z_CEIL - 0.39), (CORR_X * 2 - 0.7, 0.025, 0.025), mat("NEXUS_Rubber"), C_STRUCT, 0.003)

# ---------------------------------------------------------------- rooms
room("LAB_BIOLOGIA", -10.0, -5.4, 9.0, 8.0, "N", (0.62, 0.82, 1.0), 520.0)
room("LAB_QUIMICA", 0.5, -5.4, 10.0, 8.0, "N", (0.55, 0.80, 0.95), 480.0)
room("ARCHIVO_CIENTIFICO", 10.5, -5.2, 8.0, 7.0, "N", (1.0, 0.62, 0.25), 320.0)
room("SALA_ANALISIS", -10.0, 4.9, 8.0, 7.0, "S", (0.62, 0.82, 1.0), 430.0)
room("OBSERVACION", -0.5, 5.4, 7.0, 8.0, "S", (0.55, 0.78, 1.0), 380.0)
room("SERVIDORES", 9.0, 4.9, 8.0, 7.0, "S", (0.55, 0.85, 1.0), 420.0)

# Close the corridor-side gaps between room shells so the hallway is continuous.
for yy, spans in (
    (-1.4, [(-15.6, -14.5), (-5.5, -4.5), (5.5, 6.5), (14.5, 15.6)]),
    (1.4, [(-15.6, -14.0), (-6.0, -4.0), (3.0, 5.0), (13.0, 15.6)]),
):
    for i, (x1, x2) in enumerate(spans):
        box(f"NEXUS_V03_CORR_FILL_{yy}_{i}", ((x1 + x2) * 0.5, yy, Z_FLOOR + WALL_H * 0.5),
            (abs(x2 - x1), WALL_T, WALL_H), mat("NEXUS_Concrete"), C_STRUCT, 0.012)


def lab_bench(name, cx, cy, sx=3.0, sy=0.9):
    top_z = Z_FLOOR + 0.92
    box(name + "_TOP", (cx, cy, top_z), (sx, sy, 0.08), mat("NEXUS_Steel"), C_PROPS, 0.012)
    for dx in (-sx * 0.42, sx * 0.42):
        for dy in (-sy * 0.33, sy * 0.33):
            box(name + f"_LEG_{dx}_{dy}", (cx + dx, cy + dy, Z_FLOOR + 0.46), (0.07, 0.07, 0.86), mat("NEXUS_Painted_Metal"), C_PROPS, 0.006)
    box(name + "_SHELF", (cx, cy, Z_FLOOR + 0.38), (sx * 0.9, sy * 0.7, 0.04), mat("NEXUS_Painted_Metal"), C_PROPS, 0.004)


def tank(name, cx, cy, radius=0.55, height=1.9):
    cylinder(name + "_GLASS", (cx, cy, Z_FLOOR + height * 0.5 + 0.6), radius, height, mat("NEXUS_Glass"), C_PROPS, "Z", 24)
    cylinder(name + "_GOO", (cx, cy, Z_FLOOR + height * 0.38 + 0.6), radius * 0.78, height * 0.68, mat("NEXUS_Green"), C_PROPS, "Z", 24)
    cylinder(name + "_BASE", (cx, cy, Z_FLOOR + 0.55), radius * 1.05, 0.16, mat("NEXUS_Steel"), C_PROPS, "Z", 24)
    cylinder(name + "_TOP", (cx, cy, Z_FLOOR + height + 0.56), radius * 1.05, 0.14, mat("NEXUS_Steel"), C_PROPS, "Z", 24)
    box(name + "_SPECIMEN", (cx, cy, Z_FLOOR + 1.0), (radius * 0.55, radius * 0.35, 1.1), mat("NEXUS_Concrete_Dark"), C_PROPS, 0.08)


def screen(name, cx, cy, cz, w=0.7, h=0.45, ry=0.0):
    box(name + "_FRAME", (cx, cy, cz), (w + 0.06, 0.06, h + 0.06), mat("NEXUS_Painted_Metal"), C_PROPS, 0.008)
    box(name + "_SCREEN", (cx, cy - 0.04, cz), (w, 0.02, h), mat("NEXUS_Screen"), C_PROPS, 0.004)


def body_bag(name, cx, cy):
    box(name, (cx, cy, Z_FLOOR + 0.72), (1.75, 0.55, 0.26), mat("NEXUS_Rubber"), C_STORY, 0.16)
    box(name + "_HEAD", (cx + 0.92, cy, Z_FLOOR + 0.72), (0.28, 0.34, 0.26), mat("NEXUS_Rubber"), C_STORY, 0.12)
    box(name + "_STRAP", (cx - 0.15, cy, Z_FLOOR + 0.86), (0.10, 0.60, 0.03), mat("NEXUS_Painted_Metal"), C_STORY, 0.004)


def blood(name, cx, cy, sx, sy):
    # Irregular low patch, not a clean rectangle.
    pts = []
    n = 10
    for i in range(n):
        a = 2 * math.pi * i / n
        r = 0.55 + 0.18 * math.sin(i * 2.7)
        pts.append((cx + math.cos(a) * sx * r, cy + math.sin(a) * sy * r, Z_FLOOR + 0.17))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(pts, [], [tuple(range(n))])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    C_STORY.objects.link(obj)
    obj.data.materials.append(mat("NEXUS_Blood_Dried"))


# Biología: benches, tanks, console, gurney, body bag, damage.
for i, (x, y) in enumerate(((-12.8, -3.1), (-8.0, -3.1), (-12.8, -6.8), (-8.0, -6.8))):
    lab_bench(f"NEXUS_V03_BIO_BENCH_{i}", x, y)
for i, x in enumerate((-12.6, -10.8, -9.0)):
    tank(f"NEXUS_V03_BIO_TANK_{i}", x, -8.2)
# Console against the east wall.
lab_bench("NEXUS_V03_BIO_CONSOLE", -6.2, -3.2, 2.0, 0.75)
screen("NEXUS_V03_BIO_MON_A", -6.6, -3.55, Z_FLOOR + 1.5, 0.62, 0.42)
screen("NEXUS_V03_BIO_MON_B", -5.8, -3.55, Z_FLOOR + 1.5, 0.62, 0.42)
# Gurney and body bag.
box("NEXUS_V03_BIO_GURNEY", (-6.2, -7.5, Z_FLOOR + 0.78), (1.9, 0.65, 0.10), mat("NEXUS_Steel"), C_PROPS, 0.03)
for dx in (-0.75, 0.75):
    for dy in (-0.25, 0.25):
        box(f"NEXUS_V03_BIO_GURNEY_LEG_{dx}_{dy}", (-6.2 + dx, -7.5 + dy, Z_FLOOR + 0.38), (0.06, 0.06, 0.72), mat("NEXUS_Steel"), C_PROPS, 0.005)
body_bag("NEXUS_V03_BIO_BODY", -6.2, -7.5)
blood("NEXUS_V03_BIO_BLOOD_A", -7.4, -6.8, 0.9, 0.5)
blood("NEXUS_V03_BIO_BLOOD_B", -5.4, -4.7, 0.4, 0.35)
# Broken ceiling panel / debris.
box("NEXUS_V03_BIO_PANEL", (-9.6, -4.0, Z_FLOOR + 0.05), (1.2, 0.6, 0.03), mat("NEXUS_Concrete_Dark"), C_STORY, 0.02)
for i in range(5):
    box(f"NEXUS_V03_BIO_DEBRIS_{i}", (-11.0 + i * 0.35, -4.8 + i * 0.12, Z_FLOOR + 0.06), (0.12 + 0.04 * i, 0.08, 0.06), mat("NEXUS_Debris"), C_STORY, 0.006)
# Warning sign.
text("NEXUS_V03_BIO_WARNING", "RIESGO BIOLOGICO", (-10.0, -1.55, Z_FLOOR + 3.0), 0.17, math.pi / 2, mat("NEXUS_Amber"), C_STORY)

# Química: benches, fume hood, barrels, stains.
for i, (x, y) in enumerate(((-2.8, -3.1), (3.2, -3.1), (-2.8, -6.8), (3.2, -6.8))):
    lab_bench(f"NEXUS_V03_CHEM_BENCH_{i}", x, y, 3.2, 0.9)
box("NEXUS_V03_CHEM_HOOD", (5.0, -7.6, Z_FLOOR + 1.35), (2.2, 1.0, 2.5), mat("NEXUS_Painted_Metal"), C_PROPS, 0.03)
box("NEXUS_V03_CHEM_HOOD_GLASS", (4.0, -7.6, Z_FLOOR + 1.55), (0.04, 0.9, 1.4), mat("NEXUS_Glass"), C_PROPS, 0.01)
for i, x in enumerate((1.2, 2.0, 2.8)):
    cylinder(f"NEXUS_V03_CHEM_BARREL_{i}", (x, -8.0, Z_FLOOR + 0.45), 0.28, 0.9, mat("NEXUS_Rusted_Metal"), C_PROPS, "Z", 16)
blood("NEXUS_V03_CHEM_SPILL", 0.0, -5.0, 1.0, 0.6)
text("NEXUS_V03_CHEM_SIGN", "LABORATORIO QUIMICA", (0.5, -1.55, Z_FLOOR + 3.0), 0.16, math.pi / 2, mat("NEXUS_Amber"), C_STORY)

# Archivo: shelves and boxes.
for i, x in enumerate((-12.5, -9.8, -7.1, -4.4)):
    box(f"NEXUS_V03_ARCH_SHELF_{i}", (x, -8.1, Z_FLOOR + 1.15), (0.75, 0.5, 2.3), mat("NEXUS_Painted_Metal"), C_PROPS, 0.02)
    for j in range(3):
        box(f"NEXUS_V03_ARCH_BOX_{i}_{j}", (x, -8.1, Z_FLOOR + 0.55 + j * 0.65), (0.62, 0.42, 0.35), mat("NEXUS_Concrete_Dark"), C_PROPS, 0.008)
box("NEXUS_V03_ARCH_TABLE", (9.0, -4.4, Z_FLOOR + 0.82), (2.2, 1.0, 0.08), mat("NEXUS_Steel"), C_PROPS, 0.015)
for i in range(3):
    box(f"NEXUS_V03_ARCH_PAPER_{i}", (8.5 + i * 0.25, -4.6, Z_FLOOR + 0.88), (0.22, 0.3, 0.01), mat("NEXUS_OffWhite"), C_STORY, 0.002)

# Análisis: table, monitors, chairs.
box("NEXUS_V03_AN_TABLE", (-10.0, 4.0, Z_FLOOR + 0.82), (4.0, 1.3, 0.08), mat("NEXUS_Steel"), C_PROPS, 0.02)
for i, x in enumerate((-11.2, -10.0, -8.8)):
    screen(f"NEXUS_V03_AN_MON_{i}", x, 4.25, Z_FLOOR + 1.45, 0.72, 0.45)
for i, x in enumerate((-11.0, -9.0)):
    box(f"NEXUS_V03_AN_CHAIR_{i}", (x, 2.8, Z_FLOOR + 0.5), (0.55, 0.55, 0.1), mat("NEXUS_Rubber"), C_PROPS, 0.03)
    box(f"NEXUS_V03_AN_CHAIR_BACK_{i}", (x, 2.55, Z_FLOOR + 0.95), (0.55, 0.1, 0.8), mat("NEXUS_Rubber"), C_PROPS, 0.03)

# Observación: console and window to the lab corridor.
box("NEXUS_V03_OBS_CONSOLE", (-0.5, 6.8, Z_FLOOR + 0.82), (3.0, 1.0, 0.08), mat("NEXUS_Steel"), C_PROPS, 0.02)
for i, x in enumerate((-1.4, -0.5, 0.4)):
    screen(f"NEXUS_V03_OBS_MON_{i}", x, 7.1, Z_FLOOR + 1.45, 0.68, 0.42)

# Servidores: compact rack cluster.
for i, x in enumerate((6.0, 7.1, 8.2, 9.3, 10.4)):
    box(f"NEXUS_V03_SRV_RACK_{i}", (x, 7.8, Z_FLOOR + 1.2), (0.85, 0.65, 2.35), mat("NEXUS_Steel"), C_PROPS, 0.02)
    box(f"NEXUS_V03_SRV_PANEL_{i}", (x, 7.45, Z_FLOOR + 1.45), (0.6, 0.03, 1.25), mat("NEXUS_Screen"), C_PROPS, 0.005)
    for j in range(4):
        box(f"NEXUS_V03_SRV_LED_{i}_{j}", (x - 0.22 + j * 0.14, 7.42, Z_FLOOR + 1.85), (0.03, 0.02, 0.03), mat("NEXUS_CorridorLight"), C_PROPS, 0.002)
box("NEXUS_V03_SRV_CONSOL", (8.0, 5.7, Z_FLOOR + 0.82), (2.8, 0.9, 0.08), mat("NEXUS_Steel"), C_PROPS, 0.02)
for i, x in enumerate((7.2, 8.0, 8.8)):
    screen(f"NEXUS_V03_SRV_MON_{i}", x, 5.9, Z_FLOOR + 1.45, 0.62, 0.4)
blood("NEXUS_V03_SRV_BLOOD", 11.0, 5.4, 0.7, 0.5)
box("NEXUS_V03_SRV_FALLEN", (11.7, 6.0, Z_FLOOR + 0.55), (0.55, 0.55, 0.1), mat("NEXUS_Rubber"), C_STORY, 0.03)

# A couple of ceiling ducts and practical boxes in the corridor.
for i, x in enumerate((-8.0, 4.0, 12.0)):
    box(f"NEXUS_V03_CORR_JUNCTION_{i}", (x, 1.32, Z_FLOOR + 2.4), (0.35, 0.18, 0.5), mat("NEXUS_Painted_Metal"), C_STRUCT, 0.01)

# Presentation cameras.
def camera(name, loc, target, lens=24.0):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    co = bpy.data.objects.new(name, cd)
    C_CAMS.objects.link(co)
    co.location = Vector(loc)
    f = (Vector(target) - Vector(loc)).normalized()
    up = Vector((0, 0, 1))
    if abs(f.dot(up)) > 0.98:
        up = Vector((0, 1, 0))
    right = f.cross(up).normalized()
    up2 = right.cross(f).normalized()
    co.matrix_world = Matrix.Translation(co.location) @ Matrix((right, up2, -f)).transposed().to_4x4()
    return co

cam_corridor = camera("NEXUS_V03_CAM_Corridor", (-14.8, 0.0, -12.15), (12.0, 0.0, -12.15), 24.0)
cam_bio = camera("NEXUS_V03_CAM_Biologia", (-13.8, -2.0, -12.15), (-8.0, -6.0, -12.0), 24.0)
cam_chem = camera("NEXUS_V03_CAM_Quimica", (-3.8, -2.0, -12.15), (2.0, -6.0, -12.0), 24.0)
SCENE.camera = cam_corridor

# Final render setup.
SCENE.render.engine = "BLENDER_EEVEE"
SCENE.render.resolution_x = 1920
SCENE.render.resolution_y = 1080
SCENE.render.resolution_percentage = 100
SCENE.render.image_settings.file_format = "PNG"
try:
    SCENE.eevee.taa_render_samples = 64
except Exception:
    pass
try:
    SCENE.view_settings.view_transform = "AgX"
    SCENE.view_settings.look = "AgX - Medium High Contrast"
    SCENE.view_settings.exposure = 1.4
except Exception:
    pass

bpy.context.view_layer.update()
print("LAB_LEVEL_DONE objects", len(bpy.data.objects), "visible", sum(1 for o in bpy.data.objects if not o.hide_render))
path = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V03_lab_level.blend")
i = 2
while os.path.exists(path):
    path = os.path.join(ROOT, "blender_concept", f"FM_NEXUS_V03_lab_level_{i:02d}.blend")
    i += 1
bpy.ops.wm.save_as_mainfile(filepath=path)
print("SAVED", path, os.path.getsize(path))
