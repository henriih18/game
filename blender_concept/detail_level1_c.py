"""Level 1 detail pass C: fix monitors and enrich reception, security and access control."""
import bpy
import math
import os
from mathutils import Vector, Matrix

ROOT = "/home/riyo/Documentos/game"
Z1 = -5.8
F = -5.65
SCENE = bpy.context.scene

CS = bpy.data.collections["V05_STRUCT"]
CP = bpy.data.collections["V05_PROPS"]
CC = bpy.data.collections["V05_CAMS"]
CL = bpy.data.collections["V05_LIGHTS"]
CT = bpy.data.collections["V05_STORY"]


def mat(name):
    return bpy.data.materials.get(name)


def make_mat(name, base, rough=0.8, metallic=0.0, emission=None, emission_strength=0.0):
    m = bpy.data.materials.get(name)
    if m is not None:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = (*base, 1.0)
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = rough
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if emission:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emission_strength
    return m


make_mat("NEXUS_MonitorScreen", (0.004, 0.014, 0.020), 0.22, 0.0, (0.005, 0.06, 0.08), 1.1)
make_mat("NEXUS_Plant", (0.035, 0.095, 0.045), 0.82)
make_mat("NEXUS_Carpet", (0.055, 0.085, 0.075), 0.96)
make_mat("NEXUS_PlasticWrap", (0.62, 0.66, 0.64), 0.30)


def box(name, center, size, material, col, bevel=0.008):
    mesh = bpy.data.meshes.new(name)
    x, y, z = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
    verts = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
             (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    col.objects.link(o)
    o.location = center
    mm = mat(material)
    if mm:
        mesh.materials.append(mm)
    if bevel > 0:
        md = o.modifiers.new("Bevel", "BEVEL")
        md.width = bevel
        md.segments = 1
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
    mesh.from_pydata(vl, [], fs)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    col.objects.link(o)
    o.location = center
    if axis == "X":
        o.rotation_euler.y = math.pi / 2
    elif axis == "Y":
        o.rotation_euler.x = math.pi / 2
    mm = mat(material)
    if mm:
        mesh.materials.append(mm)
    return o


def sphere(name, center, radius, material, col, segments=12, rings=8):
    mesh = bpy.data.meshes.new(name)
    verts = []
    faces = []
    for i in range(rings + 1):
        theta = math.pi * i / rings
        z = math.cos(theta) * radius
        r = math.sin(theta) * radius
        for j in range(segments):
            phi = 2 * math.pi * j / segments
            verts.append((r * math.cos(phi), r * math.sin(phi), z))
    for i in range(rings):
        for j in range(segments):
            a = i * segments + j
            b = i * segments + (j + 1) % segments
            c = (i + 1) * segments + j
            d = (i + 1) * segments + (j + 1) % segments
            faces.append((a, b, d, c))
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    col.objects.link(o)
    o.location = center
    mm = mat(material)
    if mm:
        mesh.materials.append(mm)
    return o


def basis(normal):
    n = Vector(normal).normalized()
    up = Vector((0, 0, 1))
    if abs(n.dot(up)) > 0.95:
        up = Vector((0, 1, 0))
    right = up.cross(n).normalized()
    up2 = n.cross(right).normalized()
    return n, right, up2, Matrix((right, up2, n)).transposed().to_4x4()


def text_only(name, body, loc, normal, size, material="NEXUS_SignText", col=CS):
    n, right, up2, rot = basis(normal)
    c = bpy.data.curves.new(name + "_TEXT", type="FONT")
    c.body = body
    c.align_x = "CENTER"
    c.align_y = "CENTER"
    c.size = size
    c.extrude = 0.004
    o = bpy.data.objects.new(c.name, c)
    col.objects.link(o)
    o.matrix_world = Matrix.Translation(Vector(loc)) @ rot
    mm = mat(material)
    if mm:
        o.data.materials.append(mm)
    return o


def sign(name, body, loc, normal, size=0.13, width=5.2, col=CS):
    n, right, up2, rot = basis(normal)
    plate = box(name + "_PLATE", (0, 0, 0), (size * width, size * 1.5, 0.06), "NEXUS_SignPlate", col, 0.004)
    plate.matrix_world = Matrix.Translation(Vector(loc) + n * 0.03) @ rot
    text_only(name + "_TEXT", body, Vector(loc) + n * 0.07, n, size, "NEXUS_SignText", col)


def monitor(prefix, x, y, z, w, h, normal=(0, -1, 0), screen_mat="NEXUS_MonitorScreen"):
    n, right, up2, rot = basis(normal)
    frame = box(prefix + "_FRAME", (0, 0, 0), (w + 0.07, h + 0.07, 0.05), "NEXUS_Painted_Metal", CP, 0.006)
    frame.matrix_world = Matrix.Translation(Vector((x, y, z))) @ rot
    screen = box(prefix + "_SCREEN", (0, 0, 0), (w, h, 0.02), screen_mat, CP, 0.003)
    screen.matrix_world = Matrix.Translation(Vector((x, y, z)) + n * 0.04) @ rot
    for i, (yy, ww) in enumerate(((h * 0.26, 0.52), (h * 0.06, 0.36), (-h * 0.14, 0.46))):
        line = box(prefix + f"_LINE_{i}", (0, 0, 0), (w * ww, h * 0.045, 0.005), "NEXUS_Amber", CP, 0.001)
        line.matrix_world = (Matrix.Translation(Vector((x, y, z)) + n * 0.055
                                                + right * (-w * 0.16) + up2 * yy) @ rot)
    led = box(prefix + "_LED", (0, 0, 0), (0.025, 0.025, 0.006), "NEXUS_CorridorLight", CP, 0.001)
    led.matrix_world = (Matrix.Translation(Vector((x, y, z)) + n * 0.055
                                           + right * (w * 0.5 - 0.05) + up2 * (-h * 0.5 + 0.045)) @ rot)


def lounge_chair(name, x, y, back_side):
    z = F
    box(name + "_SEAT", (x, y, z + 0.45), (0.62, 0.62, 0.10), "NEXUS_Rubber", CP, 0.025)
    box(name + "_BACK", (x + back_side * 0.31, y, z + 0.82), (0.08, 0.62, 0.62), "NEXUS_Rubber", CP, 0.02)
    for i, (dx, dy) in enumerate(((-0.22, -0.22), (-0.22, 0.22), (0.22, -0.22), (0.22, 0.22))):
        box(name + f"_LEG_{i}", (x + dx, y + dy, z + 0.20), (0.05, 0.05, 0.40), "NEXUS_Steel", CP, 0.004)


def chair_north(name, x, y):
    z = F
    box(name + "_SEAT", (x, y, z + 0.45), (0.55, 0.55, 0.08), "NEXUS_Rubber", CP, 0.02)
    box(name + "_BACK", (x, y + 0.27, z + 0.82), (0.55, 0.06, 0.62), "NEXUS_Rubber", CP, 0.02)
    for i, (dx, dy) in enumerate(((-0.20, -0.20), (-0.20, 0.20), (0.20, -0.20), (0.20, 0.20))):
        box(name + f"_LEG_{i}", (x + dx, y + dy, z + 0.20), (0.045, 0.045, 0.40), "NEXUS_Steel", CP, 0.004)


# Remove previous C-pass objects and older wrongly-oriented monitor panels / old plants.
for o in list(bpy.data.objects):
    if o.name.startswith("NEXUS_V05_C_"):
        bpy.data.objects.remove(o, do_unlink=True)
for o in list(bpy.data.objects):
    n = o.name
    if n.startswith(("NEXUS_V05_REC_MON_", "NEXUS_V05_SEC_DESK_MON_", "NEXUS_V05_ACC_MON_", "NEXUS_V05_SEC_MONWALL_")):
        if n.endswith(("_FRAME", "_SCREEN", "_LED")):
            bpy.data.objects.remove(o, do_unlink=True)
for n in ("NEXUS_V05_REC_PLANT_0", "NEXUS_V05_REC_PLANT_1"):
    o = bpy.data.objects.get(n)
    if o:
        bpy.data.objects.remove(o, do_unlink=True)

# ---------------------------------------------------------------------------
# Monitors: vertical frames and screens
# ---------------------------------------------------------------------------
monitor("NEXUS_V05_REC_MON_A", -13.2, 8.05, -4.59, 0.50, 0.30, (0, -1, 0))
monitor("NEXUS_V05_REC_MON_B", -11.25, 8.05, -4.59, 0.50, 0.30, (0, -1, 0))
monitor("NEXUS_V05_SEC_DESK_MON_0", 1.8, 6.05, -4.59, 0.55, 0.32, (0, -1, 0))
monitor("NEXUS_V05_SEC_DESK_MON_1", 3.0, 6.05, -4.59, 0.55, 0.32, (0, -1, 0))
monitor("NEXUS_V05_SEC_DESK_MON_2", 4.2, 6.05, -4.59, 0.55, 0.32, (0, -1, 0))
monitor("NEXUS_V05_ACC_MON_A", 12.35, 8.05, -4.50, 0.62, 0.36, (0, -1, 0))
monitor("NEXUS_V05_ACC_MON_B", 13.65, 8.05, -4.50, 0.62, 0.36, (0, -1, 0))

for ix, x in enumerate((1.3, 3.0, 4.7)):
    for iz, z in enumerate((-3.25, -4.30)):
        monitor(f"NEXUS_V05_SEC_MONWALL_{ix}_{iz}", x, 9.46, z, 0.95, 0.55, (0, -1, 0))

# ---------------------------------------------------------------------------
# Reception
# ---------------------------------------------------------------------------
# Ceiling beams and pendant lamps.
for i, y in enumerate((4.8, 7.4, 10.0)):
    box(f"NEXUS_V05_C_REC_BEAM_{i}", (-12.0, y, -0.10), (15.8, 0.25, 0.35), "NEXUS_Concrete_Dark", CS, 0.01)
for i, x in enumerate((-15.0, -9.0)):
    cyl(f"NEXUS_V05_C_REC_PEND_CORD_{i}", (x, 8.0, -1.12), 0.014, 2.55, "NEXUS_Rubber", CP, "Z", 8)
    cyl(f"NEXUS_V05_C_REC_PEND_SHADE_{i}", (x, 8.0, -2.46), 0.28, 0.18, "NEXUS_Steel", CP, "Z", 20)
    cyl(f"NEXUS_V05_C_REC_PEND_BULB_{i}", (x, 8.0, -2.57), 0.17, 0.02, "NEXUS_CorridorLight", CP, "Z", 20)

# NEXUS backwall logo behind the reception desk.
box("NEXUS_V05_C_REC_LOGOPANEL", (-12.0, 11.64, -3.05), (5.2, 0.06, 1.85), "NEXUS_SignPlate", CS, 0.006)
text_only("NEXUS_V05_C_REC_LOGO", "NEXUS", (-12.0, 11.58, -2.82), (0, -1, 0), 0.55, "NEXUS_SignText", CS)
text_only("NEXUS_V05_C_REC_LOGOSUB", "RECUPERACION  //  LOGISTICA", (-12.0, 11.58, -3.42), (0, -1, 0), 0.15, "NEXUS_SignText", CS)

# Elevator on the north wall.
box("NEXUS_V05_C_REC_ELEV_FRAME", (-17.5, 11.62, -4.25), (2.2, 0.08, 2.9), "NEXUS_Painted_Metal", CS, 0.01)
box("NEXUS_V05_C_REC_ELEV_L", (-17.95, 11.55, -4.30), (0.94, 0.08, 2.55), "NEXUS_Steel", CS, 0.008)
box("NEXUS_V05_C_REC_ELEV_R", (-17.05, 11.55, -4.30), (0.94, 0.08, 2.55), "NEXUS_Steel", CS, 0.008)
box("NEXUS_V05_C_REC_ELEV_SEAM", (-17.5, 11.50, -4.30), (0.025, 0.02, 2.52), "NEXUS_Rubber", CS, 0.002)
box("NEXUS_V05_C_REC_ELEV_CALL", (-16.20, 11.52, -4.15), (0.16, 0.05, 0.30), "NEXUS_Painted_Metal", CP, 0.006)
cyl("NEXUS_V05_C_REC_ELEV_BTN", (-16.20, 11.47, -4.08), 0.035, 0.02, "NEXUS_Amber", CP, "Y", 12)
sign("NEXUS_V05_C_REC_ELEV_SIGN", "SALIDA", (-17.5, 11.47, -2.62), (0, -1, 0), 0.11, 3.4)

# Reception directory on the west wall.
box("NEXUS_V05_C_REC_DIR_BOARD", (-19.87, 5.0, -2.85), (0.06, 1.2, 1.5), "NEXUS_SignPlate", CS, 0.005)
text_only("NEXUS_V05_C_REC_DIR_TITLE", "DIRECTORIO", (-19.80, 5.0, -2.25), (1, 0, 0), 0.13, "NEXUS_SignText", CS)
for i, (yy, zz, ww) in enumerate(((-0.18, -2.58, 0.72), (-0.18, -2.78, 0.55), (-0.18, -2.98, 0.64))):
    box(f"NEXUS_V05_C_REC_DIR_LINE_{i}", (-19.79, 5.0 + yy, zz), (0.01, ww, 0.025), "NEXUS_OffWhite", CP, 0.001)
text_only("NEXUS_V05_C_REC_DIR_L1", "NIVEL 1", (-19.78, 5.0, -3.30), (1, 0, 0), 0.09, "NEXUS_OffWhite", CS)

# Reception seating cluster: rug, low table, two lounge chairs.
box("NEXUS_V05_C_REC_RUG", (-12.0, 4.3, F + 0.012), (6.0, 3.0, 0.024), "NEXUS_Carpet", CP, 0.004)
box("NEXUS_V05_C_REC_TABLE_TOP", (-12.0, 4.3, F + 0.38), (1.4, 0.8, 0.06), "NEXUS_Debris", CP, 0.008)
for i, (dx, dy) in enumerate(((-0.60, -0.30), (-0.60, 0.30), (0.60, -0.30), (0.60, 0.30))):
    box(f"NEXUS_V05_C_REC_TABLE_LEG_{i}", (-12.0 + dx, 4.3 + dy, F + 0.18), (0.06, 0.06, 0.36), "NEXUS_Steel", CP, 0.004)
box("NEXUS_V05_C_REC_MAG_0", (-12.25, 4.25, F + 0.425), (0.42, 0.30, 0.015), "NEXUS_OffWhite", CP, 0.002)
box("NEXUS_V05_C_REC_MAG_1", (-11.95, 4.38, F + 0.44), (0.38, 0.28, 0.012), "NEXUS_Amber", CP, 0.002)
lounge_chair("NEXUS_V05_C_REC_LOUNGE_W", -14.4, 4.3, -1)
lounge_chair("NEXUS_V05_C_REC_LOUNGE_E", -9.6, 4.3, 1)
chair_north("NEXUS_V05_C_REC_WAIT_S", -12.0, 2.75)

# Entry mat.
box("NEXUS_V05_C_REC_MAT", (-12.0, 2.45, F + 0.008), (2.6, 1.0, 0.016), "NEXUS_Rubber", CP, 0.004)

# Plants: trunk plus dark green foliage clusters.
for i, (x, y) in enumerate(((-18.0, 3.0), (-6.0, 3.0))):
    cyl(f"NEXUS_V05_C_REC_PLANT_TRUNK_{i}", (x, y, F + 0.55), 0.075, 1.0, "NEXUS_Debris", CP, "Z", 10)
    for j, (dx, dy, dz, rr) in enumerate(((0.0, 0.0, 1.25, 0.40), (0.24, 0.08, 1.05, 0.30), (-0.22, -0.10, 1.08, 0.28), (0.02, 0.22, 0.92, 0.26), (-0.04, -0.20, 0.90, 0.24))):
        sphere(f"NEXUS_V05_C_REC_PLANT_LEAF_{i}_{j}", (x + dx, y + dy, F + dz), rr, "NEXUS_Plant", CP, 10, 6)

# Fire hose reel and camera.
cyl("NEXUS_V05_C_REC_HOSE_REEL", (-19.75, 10.5, -3.45), 0.32, 0.18, "NEXUS_Red", CP, "X", 20)
box("NEXUS_V05_C_REC_HOSE_BRACKET", (-19.88, 10.5, -3.45), (0.12, 0.55, 0.55), "NEXUS_Steel", CP, 0.006)
box("NEXUS_V05_C_REC_CAM_BODY", (-4.45, 11.35, -1.15), (0.28, 0.22, 0.20), "NEXUS_Painted_Metal", CP, 0.01)
cyl("NEXUS_V05_C_REC_CAM_LENS", (-4.60, 11.35, -1.17), 0.07, 0.10, "NEXUS_Glass", CP, "X", 12)

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
# Printer on the cabinet.
box("NEXUS_V05_C_SEC_PRINTER_BODY", (6.9, 8.8, -3.86), (0.66, 0.54, 0.34), "NEXUS_Painted_Metal", CP, 0.01)
box("NEXUS_V05_C_SEC_PRINTER_TRAY", (6.9, 8.66, -3.66), (0.52, 0.36, 0.025), "NEXUS_Rubber", CP, 0.004)
box("NEXUS_V05_C_SEC_PRINTER_PAPER", (6.9, 8.55, -3.70), (0.38, 0.26, 0.018), "NEXUS_OffWhite", CP, 0.002)
box("NEXUS_V05_C_SEC_PRINTER_LED", (7.14, 8.54, -3.73), (0.04, 0.02, 0.025), "NEXUS_CorridorLight", CP, 0.001)

# Water cooler.
cyl("NEXUS_V05_C_SEC_COOLER_BODY", (7.35, 7.5, F + 0.52), 0.24, 1.04, "NEXUS_Painted_Metal", CP, "Z", 16)
cyl("NEXUS_V05_C_SEC_COOLER_BOTTLE", (7.35, 7.5, F + 1.22), 0.18, 0.46, "NEXUS_Water", CP, "Z", 16)
cyl("NEXUS_V05_C_SEC_COOLER_CAP", (7.35, 7.5, F + 1.47), 0.09, 0.06, "NEXUS_Steel", CP, "Z", 12)
box("NEXUS_V05_C_SEC_CUPS", (7.56, 7.5, F + 0.84), (0.12, 0.12, 0.30), "NEXUS_OffWhite", CP, 0.005)

# Document boxes and paperwork.
for i, (x, y, z) in enumerate(((5.8, 8.2, F + 0.20), (6.2, 8.3, F + 0.20), (5.8, 8.2, F + 0.58))):
    box(f"NEXUS_V05_C_SEC_BOX_{i}", (x, y, z), (0.52, 0.42, 0.34), "NEXUS_Debris", CP, 0.006)
    box(f"NEXUS_V05_C_SEC_BOX_PAPER_{i}", (x, y, z + 0.18), (0.38, 0.02, 0.22), "NEXUS_OffWhite", CP, 0.002)
for i in range(4):
    box(f"NEXUS_V05_C_SEC_FLOORPAPER_{i}", (2.8 + i * 0.45, 3.4 + (i % 2) * 0.5, F + 0.006), (0.30, 0.22, 0.012), "NEXUS_OffWhite", CP, 0.002)

# Wall map board on the east wall.
box("NEXUS_V05_C_SEC_MAP_BOARD", (7.87, 5.7, -2.75), (0.06, 1.4, 1.55), "NEXUS_Clinical", CS, 0.006)
text_only("NEXUS_V05_C_SEC_MAP_TITLE", "PLANO DE INSTALACION", (7.80, 5.7, -2.18), (-1, 0, 0), 0.095, "NEXUS_SignText", CS)
for i, (yy, zz, ww, hh) in enumerate(((-0.25, -2.55, 0.55, 0.06), (0.10, -2.55, 0.80, 0.06), (-0.10, -2.75, 0.45, 0.06), (0.30, -2.75, 0.55, 0.06), (-0.35, -2.95, 0.35, 0.06))):
    box(f"NEXUS_V05_C_SEC_MAP_LINE_{i}", (7.80, 5.7 + yy, zz), (0.012, ww, hh), "NEXUS_Red", CP, 0.001)

# Lockers: handles and vents.
for i, x in enumerate((0.0, 6.0)):
    box(f"NEXUS_V05_C_SEC_LOCKER_HANDLE_{i}", (x + 0.30, 7.72, -4.60), (0.04, 0.03, 0.24), "NEXUS_Steel", CP, 0.003)
    for j in range(3):
        box(f"NEXUS_V05_C_SEC_LOCKER_VENT_{i}_{j}", (x, 7.72, -3.20 - j * 0.06), (0.42, 0.01, 0.018), "NEXUS_Rubber", CP, 0.001)

# Wall clock.
cyl("NEXUS_V05_C_SEC_CLOCK", (0.0, 9.57, -2.25), 0.22, 0.04, "NEXUS_OffWhite", CP, "Y", 20)
box("NEXUS_V05_C_SEC_CLOCK_H1", (0.0, 9.54, -2.18), (0.015, 0.01, 0.12), "NEXUS_Rubber", CP, 0.001)
box("NEXUS_V05_C_SEC_CLOCK_H2", (0.06, 9.54, -2.25), (0.09, 0.01, 0.015), "NEXUS_Rubber", CP, 0.001)

# Red beacon and extinguisher near the door.
cyl("NEXUS_V05_C_SEC_BEACON", (7.65, 2.45, -2.50), 0.11, 0.20, "NEXUS_Red", CP, "Z", 12)
ld = bpy.data.lights.new("NEXUS_V05_C_SEC_BEACON_LIGHT", "POINT")
ld.color = (1.0, 0.03, 0.02)
ld.energy = 35
ld.shadow_soft_size = 0.15
lo = bpy.data.objects.new(ld.name, ld)
CL.objects.link(lo)
lo.location = (7.65, 2.45, -2.30)
box("NEXUS_V05_C_SEC_EXTINGUISHER", (7.72, 3.0, -4.95), (0.20, 0.20, 0.68), "NEXUS_Red", CP, 0.01)
box("NEXUS_V05_C_SEC_EXT_BRACKET", (7.82, 3.0, -4.55), (0.06, 0.12, 0.08), "NEXUS_Steel", CP, 0.004)

# ---------------------------------------------------------------------------
# Access control
# ---------------------------------------------------------------------------
# X-ray baggage scanner.
box("NEXUS_V05_C_ACC_XRAY_BODY", (15.6, 6.6, -4.90), (1.4, 3.0, 1.5), "NEXUS_Painted_Metal", CP, 0.02)
box("NEXUS_V05_C_ACC_XRAY_BELT", (15.6, 6.6, -4.10), (1.10, 3.4, 0.08), "NEXUS_Rubber", CP, 0.006)
for i, y in enumerate((5.1, 8.1)):
    box(f"NEXUS_V05_C_ACC_XRAY_OPEN_{i}", (15.6, y, -4.55), (0.95, 0.06, 0.75), "NEXUS_Rubber", CP, 0.004)
    for j in range(4):
        box(f"NEXUS_V05_C_ACC_XRAY_CURTAIN_{i}_{j}", (15.20 + j * 0.26, y + (0.06 if y < 6 else -0.06), -4.55),
            (0.18, 0.03, 0.70), "NEXUS_Rubber", CP, 0.002)
box("NEXUS_V05_C_ACC_XRAY_HAZ_S", (15.6, 5.06, -5.58), (1.45, 0.12, 0.02), "NEXUS_Amber", CP, 0.002)
box("NEXUS_V05_C_ACC_XRAY_HAZ_N", (15.6, 8.14, -5.58), (1.45, 0.12, 0.02), "NEXUS_Amber", CP, 0.002)
monitor("NEXUS_V05_C_ACC_XRAY_MON", 14.86, 6.6, -4.40, 0.80, 0.50, (-1, 0, 0))
sign("NEXUS_V05_C_ACC_XRAY_SIGN", "RAYOS X", (16.92, 6.6, -2.55), (-1, 0, 0), 0.13, 4.5)

# Metal detector base plates and side sensors.
for i, x in enumerate((12.30, 13.70)):
    box(f"NEXUS_V05_C_ACC_ARCH_BASE_{i}", (x, 5.75, F + 0.04), (0.42, 0.48, 0.08), "NEXUS_Steel", CP, 0.006)
    box(f"NEXUS_V05_C_ACC_ARCH_SENSOR_{i}", (x, 5.75, -4.10), (0.10, 0.12, 1.70), "NEXUS_Rubber", CP, 0.004)

# Queue sign and floor marks.
sign("NEXUS_V05_C_ACC_QUEUE_SIGN", "PREPARE SU IDENTIFICACION", (9.55, 6.8, -2.70), (1, 0, 0), 0.10, 9.0)
box("NEXUS_V05_C_ACC_FLOOR_SIGN", (10.6, 3.0, F + 0.01), (1.8, 0.65, 0.02), "NEXUS_Amber", CP, 0.002)
text_only("NEXUS_V05_C_ACC_FLOOR_TEXT", "ESPERA", (10.6, 3.0, F + 0.025), (0, 0, 1), 0.12, "NEXUS_Rubber", CP)

# Console paperwork and radio.
box("NEXUS_V05_C_ACC_PAPERS", (13.8, 8.02, -4.48), (0.36, 0.28, 0.025), "NEXUS_OffWhite", CP, 0.002)
box("NEXUS_V05_C_ACC_RADIO", (12.0, 8.02, -4.53), (0.28, 0.18, 0.10), "NEXUS_Rubber", CP, 0.006)
cyl("NEXUS_V05_C_ACC_RADIO_ANT", (12.0, 7.98, -4.38), 0.012, 0.22, "NEXUS_Steel", CP, "Z", 8)
box("NEXUS_V05_C_ACC_BADGES", (12.7, 8.02, -4.52), (0.30, 0.20, 0.03), "NEXUS_OffWhite", CP, 0.002)

# Camera and beacon.
box("NEXUS_V05_C_ACC_CAM_BODY", (9.2, 9.3, -2.40), (0.26, 0.20, 0.18), "NEXUS_Painted_Metal", CP, 0.01)
cyl("NEXUS_V05_C_ACC_CAM_LENS", (9.20, 9.18, -2.42), 0.065, 0.10, "NEXUS_Glass", CP, "Y", 12)
cyl("NEXUS_V05_C_ACC_BEACON", (16.6, 2.4, -2.55), 0.10, 0.18, "NEXUS_Red", CP, "Z", 12)

# Update control camera to show the arch and the scanner.
cam = bpy.data.objects.get("NEXUS_V05_CAM_Control")
if cam:
    loc = Vector((9.2, 2.9, Z1 + 3.0))
    target = Vector((14.0, 7.0, Z1 + 2.4))
    cam.location = loc
    cam.data.lens = 16.5
    f = (target - loc).normalized()
    up = Vector((0, 0, 1))
    r = f.cross(up).normalized()
    u = r.cross(f).normalized()
    cam.matrix_world = Matrix.Translation(loc) @ Matrix((r, u, -f)).transposed().to_4x4()

SCENE.camera = bpy.data.objects.get("NEXUS_V05_CAM_Recepcion")
SCENE.view_settings.exposure = 1.5

path = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V05_level1_v15.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
print("LEVEL1_C_SAVED", path, os.path.getsize(path))
