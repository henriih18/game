"""Level 1 detail pass D: vestuarios, almacen, mantenimiento, corredor y remates."""
import bpy
import math
import os
from mathutils import Vector, Matrix

ROOT = "/home/riyo/Documentos/game"
Z1 = -5.8
F = -5.65

C_STRUCT = bpy.data.collections["V05_STRUCT"]
C_PROPS = bpy.data.collections["V05_PROPS"]
C_CAMS = bpy.data.collections["V05_CAMS"]
C_LIGHTS = bpy.data.collections["V05_LIGHTS"]
C_STORY = bpy.data.collections["V05_STORY"]


def get_mat(name, fallback="NEXUS_Steel"):
    return bpy.data.materials.get(name) or bpy.data.materials.get(fallback)


def new_mat(name, color, metallic=0.0, roughness=0.6):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
    return m


new_mat("NEXUS_Rug_Dark", (0.055, 0.025, 0.022), 0.0, 0.95)
new_mat("NEXUS_Rack_Paint", (0.10, 0.16, 0.14), 0.55, 0.5)
new_mat("NEXUS_GaugeFace", (0.015, 0.02, 0.018), 0.0, 0.35)
new_mat("NEXUS_GrillDark", (0.04, 0.045, 0.045), 0.7, 0.45)


def box(name, center, size, mat_name, col=C_STRUCT, bevel=0.008, rot=None):
    mesh = bpy.data.meshes.new(name)
    x, y, z = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
    verts = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
             (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    mesh.from_pydata(verts, [], faces); mesh.update()
    o = bpy.data.objects.new(name, mesh); col.objects.link(o); o.location = center
    m = bpy.data.materials.get(mat_name)
    if m:
        mesh.materials.append(m)
    if bevel > 0:
        md = o.modifiers.new("Bevel", "BEVEL"); md.width = bevel; md.segments = 1
    if rot:
        o.rotation_euler = rot
    return o


def cyl(name, center, radius, depth, mat_name, col=C_STRUCT, axis="Z", verts=16):
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
    if axis == "X":
        o.rotation_euler.y = math.pi / 2
    elif axis == "Y":
        o.rotation_euler.x = math.pi / 2
    m = bpy.data.materials.get(mat_name)
    if m:
        mesh.materials.append(m)
    return o


def text_obj(name, body, loc, normal, size, mat_name="NEXUS_SignText", col=C_STRUCT):
    n = Vector(normal).normalized()
    up = Vector((0, 0, 1))
    if abs(n.dot(up)) > 0.95:
        up = Vector((0, 1, 0))
    right = up.cross(n).normalized()
    up2 = n.cross(right).normalized()
    rot = Matrix((right, up2, n)).transposed().to_4x4()
    c = bpy.data.curves.new(name + "_TEXT", type="FONT")
    c.body = body
    c.align_x = "CENTER"
    c.align_y = "CENTER"
    c.size = size
    c.extrude = 0.004
    o = bpy.data.objects.new(c.name, c)
    col.objects.link(o)
    o.matrix_world = Matrix.Translation(Vector(loc)) @ rot
    m = bpy.data.materials.get(mat_name)
    if m:
        o.data.materials.append(m)
    return o


def sign(name, body, loc, normal, size=0.12, plate_w=1.4, plate_h=0.24):
    n = Vector(normal).normalized()
    up = Vector((0, 0, 1))
    if abs(n.dot(up)) > 0.95:
        up = Vector((0, 1, 0))
    right = up.cross(n).normalized()
    up2 = n.cross(right).normalized()
    rot = Matrix((right, up2, n)).transposed().to_4x4()
    p = box(name + "_PLATE", Vector(loc) + n * 0.015, (plate_w, plate_h, 0.04),
            "NEXUS_SignPlate", C_STRUCT, 0.004)
    p.matrix_world = Matrix.Translation(Vector(loc) + n * 0.015) @ rot
    text_obj(name + "_TEXT", body, Vector(loc) + n * 0.045, normal, size, "NEXUS_SignText")


def add_legs(prefix, cx, cy, sx, sy, top_z, leg=0.08):
    for ix, dx in enumerate((-sx * 0.5 + 0.15, sx * 0.5 - 0.15)):
        for iy, dy in enumerate((-sy * 0.5 + 0.12, sy * 0.5 - 0.12)):
            box(f"{prefix}_LEG_{ix}_{iy}", (cx + dx, cy + dy, top_z - 0.12),
                (leg, leg, 0.24), "NEXUS_Painted_Metal", C_PROPS, 0.004)


# Remove previous D pass and specific broken objects.
for o in list(bpy.data.objects):
    if o.name.startswith("NEXUS_V05_D_"):
        bpy.data.objects.remove(o, do_unlink=True)

for o in list(bpy.data.objects):
    n = o.name
    if "SEC_LOCKER_0" in n:
        bpy.data.objects.remove(o, do_unlink=True)
    elif n in ("NEXUS_V05_REC_RUG", "NEXUS_V05_LOCK_BENCH"):
        bpy.data.objects.remove(o, do_unlink=True)
    elif n.startswith("NEXUS_V05_B_VEST_BENCH_LEG_"):
        bpy.data.objects.remove(o, do_unlink=True)

# ---------- Reception ----------
box("NEXUS_V05_D_REC_RUG", (-12.0, 4.3, F + 0.012), (4.6, 2.6, 0.024), "NEXUS_Rug_Dark", C_PROPS, 0.002)
add_legs("NEXUS_V05_D_REC_BENCH2", -10.5, 3.0, 4.0, 0.8, -5.4)
add_legs("NEXUS_V05_D_REC_BENCH", -18.5, 4.0, 0.8, 4.0, -5.4)
logo = bpy.data.objects.get("NEXUS_V05_C_REC_LOGOPANEL")
if logo:
    logo.location.y = 11.53
text_obj("NEXUS_V05_D_REC_LOGO", "NEXUS", (-12.0, 11.49, -3.0), (0, -1, 0), 0.46, "NEXUS_SignText", C_STRUCT)
text_obj("NEXUS_V05_D_REC_SUBLOGO", "RECUPERACION  //  OPERACIONES", (-12.0, 11.49, -3.55), (0, -1, 0), 0.075, "NEXUS_SignText", C_STRUCT)

# ---------- Security: rest of the room ----------
box("NEXUS_V05_D_SEC_PRINTER", (7.6, 8.5, -5.25), (0.75, 0.6, 0.45), "NEXUS_OffWhite", C_PROPS, 0.015)
box("NEXUS_V05_D_SEC_PRINTER_TOP", (7.6, 8.5, -5.0), (0.62, 0.48, 0.06), "NEXUS_Rubber", C_PROPS, 0.01)
box("NEXUS_V05_D_SEC_DOCBOX_0", (7.0, 9.35, -5.3), (0.5, 0.4, 0.3), "NEXUS_Debris", C_STORY, 0.008)
box("NEXUS_V05_D_SEC_DOCBOX_1", (7.55, 9.35, -5.3), (0.5, 0.4, 0.3), "NEXUS_Debris", C_STORY, 0.008)
box("NEXUS_V05_D_SEC_CLOCK", (8.8, 9.4, -3.0), (0.42, 0.06, 0.42), "NEXUS_OffWhite", C_PROPS, 0.02)
cyl("NEXUS_V05_D_SEC_CLOCK_FACE", (8.8, 9.36, -3.0), 0.17, 0.02, "NEXUS_Concrete", C_PROPS, "Y", 20)
box("NEXUS_V05_D_SEC_EXT", (-3.3, 9.35, -4.5), (0.2, 0.22, 0.6), "NEXUS_Red", C_PROPS, 0.01)

# ---------- Vestuarios ----------
for cx in (-15.7, -12.3):
    box(f"NEXUS_V05_D_VEST_BENCH_{'W' if cx < -14 else 'E'}", (cx, -5.8, -5.35),
        (2.4, 0.8, 0.1), "NEXUS_Painted_Metal", C_PROPS, 0.012)
    add_legs(f"NEXUS_V05_D_VEST_BENCH_{'W' if cx < -14 else 'E'}", cx, -5.8, 2.4, 0.8, -5.4)
    box(f"NEXUS_V05_D_VEST_TOWEL_{'W' if cx < -14 else 'E'}", (cx - 0.3, -5.8, -5.28),
        (0.5, 0.32, 0.05), "NEXUS_OffWhite", C_PROPS, 0.004)

for o in bpy.data.objects:
    if o.name.startswith("NEXUS_V05_LOCK_LOCKER_"):
        try:
            i = int(o.name.rsplit("_", 1)[1])
        except ValueError:
            continue
        x = o.location.x
        box(f"NEXUS_V05_D_LOCK_HANDLE_{i}", (x + 0.27, -8.94, -4.55),
            (0.05, 0.035, 0.14), "NEXUS_Steel", C_PROPS, 0.004)
        for j, zz in enumerate((-3.82, -3.9, -3.98)):
            box(f"NEXUS_V05_D_LOCK_VENT_{i}_{j}", (x - 0.08, -8.94, zz),
                (0.4, 0.015, 0.02), "NEXUS_GrillDark", C_PROPS, 0.002)

box("NEXUS_V05_D_VEST_SHOWER_HEAD", (-18.85, -8.8, -2.6), (0.12, 0.12, 0.08), "NEXUS_Steel", C_PROPS, 0.01)
cyl("NEXUS_V05_D_VEST_SHOWER_PIPE", (-18.9, -8.8, -3.0), 0.03, 0.8, "NEXUS_Steel", C_PROPS, "Z", 10)
box("NEXUS_V05_D_VEST_SOAP", (-9.55, -5.55, -4.62), (0.16, 0.1, 0.22), "NEXUS_OffWhite", C_PROPS, 0.006)

# ---------- Almacen ----------
rack_mat = bpy.data.materials.get("NEXUS_Rack_Paint")
for o in bpy.data.objects:
    if o.name.startswith("NEXUS_V05_B_STORE_RACK_") and o.type == "MESH":
        o.data.materials.clear()
        if rack_mat:
            o.data.materials.append(rack_mat)

box("NEXUS_V05_D_STORE_HOIST_BEAM", (-2.0, -6.0, -1.55), (10.0, 0.18, 0.18), "NEXUS_Rusted_Metal", C_PROPS, 0.01)
box("NEXUS_V05_D_STORE_HOIST_TROLLEY", (1.5, -6.0, -1.38), (0.5, 0.35, 0.22), "NEXUS_Steel", C_PROPS, 0.012)
cyl("NEXUS_V05_D_STORE_HOIST_CHAIN", (1.5, -6.0, -2.35), 0.022, 1.65, "NEXUS_Steel", C_PROPS, "Z", 8)
box("NEXUS_V05_D_STORE_HOIST_HOOK", (1.5, -6.0, -3.22), (0.13, 0.06, 0.25), "NEXUS_Steel", C_PROPS, 0.008)
box("NEXUS_V05_D_STORE_HOIST_CTRL", (-3.5, -6.0, -3.0), (0.25, 0.25, 0.35), "NEXUS_Amber", C_PROPS, 0.01)

# Roll-up door on the east wall.
box("NEXUS_V05_D_STORE_DOOR_FRAME_L", (3.92, -7.7, -4.2), (0.14, 0.18, 2.9), "NEXUS_Painted_Metal", C_STRUCT, 0.01)
box("NEXUS_V05_D_STORE_DOOR_FRAME_R", (3.92, -3.7, -4.2), (0.14, 0.18, 2.9), "NEXUS_Painted_Metal", C_STRUCT, 0.01)
box("NEXUS_V05_D_STORE_DOOR_TOP", (3.92, -5.7, -2.8), (0.14, 4.2, 0.18), "NEXUS_Painted_Metal", C_STRUCT, 0.01)
for i in range(7):
    box(f"NEXUS_V05_D_STORE_DOOR_SLAT_{i}", (3.86, -5.7, -5.65 + i * 0.38),
        (0.05, 3.95, 0.3), "NEXUS_Rusted_Metal", C_STRUCT, 0.004)
box("NEXUS_V05_D_STORE_DOOR_HANDLE", (3.78, -5.7, -4.1), (0.05, 1.2, 0.06), "NEXUS_Steel", C_PROPS, 0.004)

for i, (x, y, sx, sy) in enumerate(((-2.0, -6.2, 1.4, 0.9), (1.0, -5.8, 1.2, 0.8))):
    box(f"NEXUS_V05_D_STORE_STAIN_{i}", (x, y, F + 0.008), (sx, sy, 0.012),
        "NEXUS_Debris", C_STORY, 0.002)
for i, (x, y) in enumerate(((-5.0, -6.0), (-4.3, -5.4), (2.8, -7.0), (0.4, -7.4))):
    box(f"NEXUS_V05_D_STORE_SPILL_{i}", (x, y, F + 0.02), (0.35, 0.28, 0.18),
        "NEXUS_Debris", C_STORY, 0.006)
sign("NEXUS_V05_D_STORE_SIGN", "ALMACEN  //  SECTOR C", (-2.0, -1.9, -2.6), (0, -1, 0), 0.11, 2.2, 0.26)

# ---------- Mantenimiento ----------
cyl("NEXUS_V05_D_MAINT_AIR_TANK", (18.8, -5.0, -4.55), 0.5, 2.2, "NEXUS_Steel", C_PROPS, "Z", 20)
for i, (dx, dy) in enumerate(((-0.42, -0.32), (0.42, -0.32), (0.0, 0.45))):
    box(f"NEXUS_V05_D_MAINT_AIR_LEG_{i}", (18.8 + dx, -5.0 + dy, -5.6),
        (0.08, 0.08, 0.5), "NEXUS_Steel", C_PROPS, 0.004)
cyl("NEXUS_V05_D_MAINT_AIR_PIPE", (18.8, -5.0, -2.3), 0.07, 2.5, "NEXUS_Rusted_Metal", C_PROPS, "Z", 12)
cyl("NEXUS_V05_D_MAINT_AIR_VALVE", (18.8, -5.0, -3.35), 0.18, 0.05, "NEXUS_Red", C_PROPS, "Z", 12)

cyl("NEXUS_V05_D_MAINT_FAN", (19.7, -6.4, -3.0), 0.55, 0.12, "NEXUS_GrillDark", C_PROPS, "X", 20)
for i in range(3):
    box(f"NEXUS_V05_D_MAINT_FAN_BAR_{i}", (19.62, -6.4, -3.42 + i * 0.42),
        (0.02, 0.85, 0.035), "NEXUS_Steel", C_PROPS, 0.002)

for i in range(2):
    box(f"NEXUS_V05_D_MAINT_LADDER_RAIL_{i}", (6.7 + i * 0.6, -9.35, -4.2),
        (0.06, 0.06, 3.2), "NEXUS_Steel", C_PROPS, 0.004)
for i in range(6):
    box(f"NEXUS_V05_D_MAINT_LADDER_RUNG_{i}", (7.0, -9.35, -5.55 + i * 0.52),
        (0.6, 0.05, 0.04), "NEXUS_Steel", C_PROPS, 0.003)

box("NEXUS_V05_D_MAINT_TOOLBOX", (6.55, -5.6, -4.63), (0.62, 0.38, 0.24), "NEXUS_Red", C_PROPS, 0.01)
box("NEXUS_V05_D_MAINT_TOOLBOX_LID", (6.55, -5.6, -4.5), (0.64, 0.4, 0.04), "NEXUS_Red", C_PROPS, 0.008)
box("NEXUS_V05_D_MAINT_WRENCH", (7.25, -5.3, -4.74), (0.48, 0.05, 0.03), "NEXUS_Steel", C_PROPS, 0.003)
box("NEXUS_V05_D_MAINT_SCREWDRIVER", (7.45, -5.7, -4.74), (0.3, 0.03, 0.03), "NEXUS_Amber", C_PROPS, 0.002)

box("NEXUS_V05_D_MAINT_OIL_0", (10.4, -6.2, F + 0.01), (1.4, 0.9, 0.012), "NEXUS_Rubber", C_STORY, 0.002)
box("NEXUS_V05_D_MAINT_OIL_1", (14.8, -4.0, F + 0.01), (0.8, 0.6, 0.012), "NEXUS_Rubber", C_STORY, 0.002)
box("NEXUS_V05_D_MAINT_BEACON", (13.0, -1.95, -2.75), (0.18, 0.18, 0.25), "NEXUS_Red", C_PROPS, 0.01)
ld = bpy.data.lights.new("NEXUS_V05_D_MAINT_BEACON_LIGHT", "POINT")
ld.color = (1.0, 0.03, 0.01); ld.energy = 25.0; ld.shadow_soft_size = 0.2
lo = bpy.data.objects.new(ld.name, ld); C_LIGHTS.objects.link(lo); lo.location = (13.0, -1.8, -2.65)

# Fix boiler gauge material and add a short connection.
for n, m in (("NEXUS_V05_B_MAINT_BOILER_GAUGE", "NEXUS_Steel"),
             ("NEXUS_V05_B_MAINT_BOILER_GAUGE_FACE", "NEXUS_GaugeFace"),
             ("NEXUS_V05_B_MAINT_BOILER_NEEDLE", "NEXUS_Red")):
    o = bpy.data.objects.get(n)
    if o:
        o.data.materials.clear()
        mm = bpy.data.materials.get(m)
        if mm:
            o.data.materials.append(mm)
cyl("NEXUS_V05_D_MAINT_GAUGE_PIPE", (17.3, -7.4, -4.2), 0.03, 0.18, "NEXUS_Steel", C_PROPS, "Y", 8)

sign("NEXUS_V05_D_MAINT_SIGN", "MANTENIMIENTO", (13.0, -1.9, -2.6), (0, -1, 0), 0.12, 2.0, 0.26)

# ---------- Corridor ----------
door_signs = [
    ("RECEPCION", -12.0, 1.56, (0, -1, 0)),
    ("SEGURIDAD", 3.0, 1.56, (0, -1, 0)),
    ("CONTROL", 13.0, 1.56, (0, -1, 0)),
    ("VESTUARIOS", -14.0, -1.56, (0, 1, 0)),
    ("ALMACEN", -2.0, -1.56, (0, 1, 0)),
    ("MANTENIMIENTO", 13.0, -1.56, (0, 1, 0)),
]
for i, (body, x, y, n) in enumerate(door_signs):
    sign(f"NEXUS_V05_D_DOORSIGN_{i}", body, (x, y, -2.28), n, 0.095, 1.5, 0.22)

for i, x in enumerate((-18, -10, -2, 6, 14, 20)):
    for j, y in enumerate((-1.05, 1.05)):
        cyl(f"NEXUS_V05_D_CORR_FLANGE_{i}_{j}", (x, y, -2.25), 0.10, 0.055,
            "NEXUS_Rusted_Metal", C_PROPS, "X", 12)
for i, (x, y) in enumerate(((-6.0, 1.05), (10.0, -1.05))):
    cyl(f"NEXUS_V05_D_CORR_VALVE_{i}", (x, y, -2.12), 0.17, 0.045,
        "NEXUS_Red", C_PROPS, "Z", 12)
    cyl(f"NEXUS_V05_D_CORR_VALVE_STEM_{i}", (x, y, -2.2), 0.025, 0.15,
        "NEXUS_Steel", C_PROPS, "Z", 8)

for i, (x, y, z) in enumerate(((-8.0, 1.55, -3.4), (7.0, -1.55, -3.4))):
    box(f"NEXUS_V05_D_CORR_PANEL_{i}", (x, y, z), (0.7, 0.09, 1.0), "NEXUS_Painted_Metal", C_PROPS, 0.01)
    box(f"NEXUS_V05_D_CORR_PANEL_LED_{i}", (x, y - 0.07 if y > 0 else y + 0.07, z + 0.3),
        (0.45, 0.015, 0.035), "NEXUS_Amber", C_PROPS, 0.002)

for i, (x, y) in enumerate(((-17.0, 1.5), (1.0, -1.5), (16.0, 1.5))):
    cyl(f"NEXUS_V05_D_CORR_EXT_{i}", (x, y, -4.55), 0.12, 0.62, "NEXUS_Red", C_PROPS, "Z", 12)
    box(f"NEXUS_V05_D_CORR_EXT_BRACKET_{i}", (x, y, -4.25), (0.06, 0.06, 0.2), "NEXUS_Steel", C_PROPS, 0.003)

for i in range(6):
    box(f"NEXUS_V05_D_CORR_BLOOD_{i}", (-4.0 + i * 1.1, 0.75 + (i % 2) * 0.12, F + 0.012),
        (0.7, 0.35, 0.012), "NEXUS_Blood_Dried", C_STORY, 0.002)

box("NEXUS_V05_D_CORR_WALLSTAIN_0", (4.0, 1.55, -3.8), (0.8, 0.01, 0.5), "NEXUS_Debris", C_STORY, 0.002)
box("NEXUS_V05_D_CORR_WALLSTAIN_1", (-11.5, -1.55, -3.3), (1.1, 0.01, 0.6), "NEXUS_Debris", C_STORY, 0.002)

box("NEXUS_V05_D_CORR_BROKEN_CEIL", (6.0, 0.6, -1.62), (1.3, 0.7, 0.05),
    "NEXUS_Concrete_Dark", C_STRUCT, 0.003, rot=(0.12, 0.0, -0.08))
box("NEXUS_V05_D_CORR_CEIL_HOLE", (6.0, 0.6, -1.58), (1.55, 0.9, 0.02), "NEXUS_Rubber", C_STRUCT, 0.001)
cyl("NEXUS_V05_D_CORR_CABLE", (6.6, 0.8, -1.95), 0.018, 0.8, "NEXUS_Rubber", C_STORY, "Z", 6)

box("NEXUS_V05_D_CORR_VENT", (-3.0, -1.55, -2.7), (0.95, 0.06, 0.36), "NEXUS_Painted_Metal", C_PROPS, 0.004)
for i in range(5):
    box(f"NEXUS_V05_D_CORR_VENT_SLAT_{i}", (-3.0, -1.585, -2.84 + i * 0.065),
        (0.8, 0.015, 0.02), "NEXUS_GrillDark", C_PROPS, 0.001)

for i, x in enumerate((-13.0, 8.0)):
    box(f"NEXUS_V05_D_CORR_SPEAKER_{i}", (x, 1.55, -2.0), (0.3, 0.08, 0.2), "NEXUS_Rubber", C_PROPS, 0.004)

# Final camera framing and save.
cam = bpy.data.objects.get("NEXUS_V05_CAM_Corridor")
if cam:
    bpy.context.scene.camera = cam

bpy.context.scene.view_settings.exposure = 1.5
path = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V05_level1_v17.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
print("L1_V17_SAVED", path, os.path.getsize(path))
