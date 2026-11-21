"""Add a back-office and restroom block inside Level 1 reception."""
import bpy
import math
import os
from mathutils import Vector, Matrix

ROOT = "/home/riyo/Documentos/game"
Z0 = -5.8
SCENE = bpy.context.scene

C_STRUCT = bpy.data.collections["V05_STRUCT"]
C_PROPS = bpy.data.collections["V05_PROPS"]
C_LIGHTS = bpy.data.collections["V05_LIGHTS"]
C_CAMS = bpy.data.collections["V05_CAMS"]
C_STORY = bpy.data.collections["V05_STORY"]


def mat(name, fallback="NEXUS_Painted_Metal"):
    return bpy.data.materials.get(name) or bpy.data.materials.get(fallback)


def box(name, center, size, material, col=C_PROPS, bevel=0.008):
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
    m = mat(material)
    if m:
        mesh.materials.append(m)
    if bevel > 0:
        md = o.modifiers.new("Bevel", "BEVEL")
        md.width = bevel
        md.segments = 1
    return o


def cyl(name, center, radius, depth, material, col=C_PROPS, axis="Z", verts=16):
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
    m = mat(material)
    if m:
        mesh.materials.append(m)
    return o


def text_x(name, body, x, y, z, size, normal=(-1, 0, 0), material="NEXUS_SignText"):
    n = Vector(normal).normalized()
    up = Vector((0, 0, 1))
    right = up.cross(n).normalized()
    up2 = n.cross(right).normalized()
    rot = Matrix((right, up2, n)).transposed().to_4x4()
    plate = box(name + "_PLATE", (x, y, z), (0.035, size * 5.4, size * 1.5),
                "NEXUS_SignPlate", C_STRUCT, 0.004)
    plate.matrix_world = Matrix.Translation(Vector((x, y, z))) @ rot
    c = bpy.data.curves.new(name + "_TEXT", type="FONT")
    c.body = body
    c.align_x = "CENTER"
    c.align_y = "CENTER"
    c.size = size
    c.extrude = 0.003
    o = bpy.data.objects.new(c.name, c)
    C_STRUCT.objects.link(o)
    o.matrix_world = Matrix.Translation(Vector((x - 0.021, y, z))) @ rot
    o.data.materials.append(mat(material))
    return o


# --- Move the planter that would sit inside the new restroom. ---
for nm in ("NEXUS_V05_REC_PLANTER_1", "NEXUS_V05_REC_PLANT_1"):
    o = bpy.data.objects.get(nm)
    if o:
        o.location.x = -8.0
        o.location.y = 10.6

# --- Block shell: x -8.2..-4.3, y 1.86..7.7, height 3.0. ---
X0, X1 = -8.2, -4.3
Y0, Y1 = 1.86, 7.7
YM = 4.7
H = 3.0
T = 0.12

# West wall with two door openings (restroom 2.6..3.5, office 5.8..6.7).
west_segments = [(Y0, 2.6), (3.5, 5.8), (6.7, Y1)]
for i, (a, b) in enumerate(west_segments):
    if b - a > 0.03:
        box(f"NEXUS_V05_OFFICE_WALL_W_{i}", (X0, (a + b) * 0.5, Z0 + H * 0.5),
            (T, b - a, H), "NEXUS_Concrete", C_STRUCT, 0.006)
for name, a, b in (("REST", 2.6, 3.5), ("OFF", 5.8, 6.7)):
    box(f"NEXUS_V05_OFFICE_WALL_{name}_TOP", (X0, (a + b) * 0.5, Z0 + 2.55),
        (T, b - a, 0.9), "NEXUS_Concrete", C_STRUCT, 0.006)

# North and east walls, partition, roof.
box("NEXUS_V05_OFFICE_WALL_N", ((X0 + X1) * 0.5, Y1, Z0 + H * 0.5),
    (X1 - X0, T, H), "NEXUS_Concrete", C_STRUCT, 0.006)
box("NEXUS_V05_OFFICE_WALL_E", (X1, (Y0 + Y1) * 0.5, Z0 + H * 0.5),
    (T, Y1 - Y0, H), "NEXUS_Concrete", C_STRUCT, 0.006)
box("NEXUS_V05_OFFICE_PARTITION", ((X0 + X1) * 0.5, YM, Z0 + H * 0.5),
    (X1 - X0, T, H), "NEXUS_Painted_Metal", C_STRUCT, 0.006)
box("NEXUS_V05_OFFICE_ROOF", ((X0 + X1) * 0.5, (Y0 + Y1) * 0.5, Z0 + H + 0.06),
    (X1 - X0 + 0.18, Y1 - Y0 + 0.18, 0.12), "NEXUS_Concrete_Dark", C_STRUCT, 0.008)
for i, (cx, cy, sx, sy) in enumerate((
        ((X0 + X1) * 0.5, Y0 + 0.03, X1 - X0, 0.06),
        ((X0 + X1) * 0.5, Y1 - 0.03, X1 - X0, 0.06),
        (X0 + 0.03, (Y0 + Y1) * 0.5, 0.06, Y1 - Y0),
        (X1 - 0.03, (Y0 + Y1) * 0.5, 0.06, Y1 - Y0))):
    box(f"NEXUS_V05_OFFICE_PARAPET_{i}", (cx, cy, Z0 + H + 0.16),
        (sx, sy, 0.2), "NEXUS_Painted_Metal", C_STRUCT, 0.004)

# Floor overlays and baseboards.
box("NEXUS_V05_OFFICE_CARPET", ((X0 + X1) * 0.5, (YM + Y1) * 0.5, Z0 + 0.011),
    (X1 - X0 - 0.1, Y1 - YM - 0.1, 0.02), "NEXUS_Rug_Dark", C_PROPS, 0.001)
box("NEXUS_V05_REST_TILE", ((X0 + X1) * 0.5, (Y0 + YM) * 0.5, Z0 + 0.011),
    (X1 - X0 - 0.1, YM - Y0 - 0.1, 0.02), "NEXUS_Clinical", C_PROPS, 0.001)
for i, (cx, cy, sx, sy) in enumerate((
        ((X0 + X1) * 0.5, Y1 - 0.08, X1 - X0 - 0.06, 0.04),
        (X0 + 0.08, (Y0 + Y1) * 0.5, 0.04, Y1 - Y0 - 0.06),
        (X1 - 0.08, (Y0 + Y1) * 0.5, 0.04, Y1 - Y0 - 0.06))):
    box(f"NEXUS_V05_OFFICE_BASE_{i}", (cx, cy, Z0 + 0.12),
        (sx, sy, 0.18), "NEXUS_Painted_Metal", C_STRUCT, 0.003)

# Door frames and leaves.
def door(name, yc, width, glass):
    leaf_x = X0 - 0.055
    box(name + "_FRAME_L", (leaf_x, yc - width * 0.5 - 0.035, Z0 + 1.1),
        (0.07, 0.07, 2.2), "NEXUS_Steel", C_STRUCT, 0.004)
    box(name + "_FRAME_R", (leaf_x, yc + width * 0.5 + 0.035, Z0 + 1.1),
        (0.07, 0.07, 2.2), "NEXUS_Steel", C_STRUCT, 0.004)
    box(name + "_FRAME_TOP", (leaf_x, yc, Z0 + 2.16),
        (0.07, width + 0.14, 0.08), "NEXUS_Steel", C_STRUCT, 0.004)
    box(name + "_LEAF", (leaf_x - 0.035, yc, Z0 + 1.05),
        (0.045, width, 2.08), "NEXUS_Painted_Metal", C_PROPS, 0.006)
    if glass:
        box(name + "_GLASS", (leaf_x - 0.061, yc, Z0 + 1.51),
            (0.012, width * 0.6, 1.0), "NEXUS_Glass", C_PROPS, 0.002)
    box(name + "_HANDLE", (leaf_x - 0.07, yc + width * 0.32, Z0 + 1.0),
        (0.035, 0.05, 0.18), "NEXUS_Steel", C_PROPS, 0.004)
    box(name + "_SIGN", (leaf_x - 0.075, yc, Z0 + 1.62),
        (0.012, 0.28, 0.12), "NEXUS_SignPlate", C_PROPS, 0.002)


door("NEXUS_V05_REST_DOOR", 3.05, 0.9, False)
door("NEXUS_V05_OFFICE_DOOR", 6.25, 0.9, True)

# West-facade signs.
text_x("NEXUS_V05_OFFICE_SIGN", "ADMINISTRACION", X0 - 0.16, 6.25, Z0 + 2.72, 0.105)
text_x("NEXUS_V05_REST_SIGN", "ASEOS", X0 - 0.16, 3.05, Z0 + 2.72, 0.1)

# Office window on the west wall, north of the office door.
WY0, WY1 = 7.0, 7.6
WZ0, WZ1 = Z0 + 1.15, Z0 + 2.25
box("NEXUS_V05_OFFICE_WINDOW_FRAME", (X0, (WY0 + WY1) * 0.5, (WZ0 + WZ1) * 0.5),
    (0.16, WY1 - WY0 + 0.12, WZ1 - WZ0 + 0.12), "NEXUS_Steel", C_STRUCT, 0.004)
box("NEXUS_V05_OFFICE_WINDOW_GLASS", (X0 - 0.02, (WY0 + WY1) * 0.5, (WZ0 + WZ1) * 0.5),
    (0.025, WY1 - WY0, WZ1 - WZ0), "NEXUS_Glass", C_PROPS, 0.001)
box("NEXUS_V05_OFFICE_WINDOW_SILL", (X0 - 0.09, (WY0 + WY1) * 0.5, WZ0 - 0.04),
    (0.22, WY1 - WY0 + 0.16, 0.06), "NEXUS_Steel", C_STRUCT, 0.004)

# --- Office interior. ---
box("NEXUS_V05_OFFICE_DESK_TOP", (-6.2, 7.15, Z0 + 0.75), (2.0, 0.8, 0.08),
    "NEXUS_Steel", C_PROPS, 0.006)
for i, (x, y) in enumerate(((-7.05, 6.85), (-5.35, 6.85), (-7.05, 7.45), (-5.35, 7.45))):
    box(f"NEXUS_V05_OFFICE_DESK_LEG_{i}", (x, y, Z0 + 0.37), (0.06, 0.06, 0.74),
        "NEXUS_Painted_Metal", C_PROPS, 0.003)
box("NEXUS_V05_OFFICE_MONITOR", (-6.2, 7.33, Z0 + 1.18), (0.62, 0.05, 0.38),
    "NEXUS_MonitorScreen", C_PROPS, 0.004)
box("NEXUS_V05_OFFICE_MONITOR_STAND", (-6.2, 7.36, Z0 + 0.92), (0.18, 0.12, 0.18),
    "NEXUS_Steel", C_PROPS, 0.003)
box("NEXUS_V05_OFFICE_KEYBOARD", (-6.2, 6.92, Z0 + 0.79), (0.5, 0.17, 0.025),
    "NEXUS_Rubber", C_PROPS, 0.002)
box("NEXUS_V05_OFFICE_PAPERS", (-5.45, 7.02, Z0 + 0.8), (0.28, 0.36, 0.012),
    "NEXUS_OffWhite", C_PROPS, 0.001)
box("NEXUS_V05_OFFICE_PHONE", (-7.0, 7.02, Z0 + 0.81), (0.18, 0.25, 0.06),
    "NEXUS_Rubber", C_PROPS, 0.006)
# Chair.
box("NEXUS_V05_OFFICE_CHAIR_SEAT", (-6.2, 6.35, Z0 + 0.47), (0.5, 0.5, 0.08),
    "NEXUS_Rubber", C_PROPS, 0.02)
box("NEXUS_V05_OFFICE_CHAIR_BACK", (-6.2, 6.08, Z0 + 0.85), (0.5, 0.08, 0.72),
    "NEXUS_Rubber", C_PROPS, 0.02)
cyl("NEXUS_V05_OFFICE_CHAIR_POST", (-6.2, 6.35, Z0 + 0.22), 0.05, 0.44,
    "NEXUS_Steel", C_PROPS, "Z", 12)
for i, (x, y) in enumerate(((-6.55, 6.1), (-5.85, 6.1), (-6.55, 6.6), (-5.85, 6.6))):
    box(f"NEXUS_V05_OFFICE_CHAIR_LEG_{i}", (x, y, Z0 + 0.06), (0.05, 0.05, 0.12),
        "NEXUS_Steel", C_PROPS, 0.002)
# Filing cabinet and shelf.
box("NEXUS_V05_OFFICE_CABINET", (-7.75, 5.35, Z0 + 0.65), (0.5, 0.62, 1.3),
    "NEXUS_Painted_Metal", C_PROPS, 0.006)
for i in range(3):
    box(f"NEXUS_V05_OFFICE_CABINET_DRAWER_{i}", (-7.45, 5.35, Z0 + 0.28 + i * 0.4),
        (0.02, 0.5, 0.32), "NEXUS_Steel", C_PROPS, 0.002)
for i in range(4):
    box(f"NEXUS_V05_OFFICE_BINDER_{i}", (-4.48, 5.35 + i * 0.32, Z0 + 1.9),
        (0.16, 0.24, 0.34), "NEXUS_SignPlate" if i % 2 else "NEXUS_Red_Matte",
        C_PROPS, 0.003)
box("NEXUS_V05_OFFICE_NOTICE", (-6.8, Y1 - 0.15, Z0 + 1.95), (1.3, 0.04, 0.7),
    "NEXUS_SignPlate", C_PROPS, 0.004)
for i in range(3):
    box(f"NEXUS_V05_OFFICE_NOTICE_PAPER_{i}", (-6.8, Y1 - 0.18, Z0 + 2.18 - i * 0.2),
        (0.42, 0.01, 0.14), "NEXUS_OffWhite", C_PROPS, 0.001)
box("NEXUS_V05_OFFICE_BIN", (-4.65, 5.0, Z0 + 0.3), (0.32, 0.32, 0.6),
    "NEXUS_Painted_Metal", C_PROPS, 0.01)
# Ceiling light panel.
box("NEXUS_V05_OFFICE_LIGHT_PANEL", (-6.2, 6.15, Z0 + 2.93), (1.1, 0.35, 0.04),
    "NEXUS_CorridorLight", C_LIGHTS, 0.002)
ld = bpy.data.lights.new("NEXUS_V05_OFFICE_LIGHT", "AREA")
ld.color = (1.0, 0.88, 0.72)
ld.energy = 180.0
ld.shape = "RECTANGLE"
ld.size = 1.1
ld.size_y = 0.35
lo = bpy.data.objects.new(ld.name, ld)
C_LIGHTS.objects.link(lo)
lo.location = (-6.2, 6.15, Z0 + 2.88)

# --- Restroom interior. ---
# Toilet against the east wall.
box("NEXUS_V05_REST_TOILET_TANK", (X1 - 0.28, 2.62, Z0 + 0.62), (0.28, 0.52, 0.52),
    "NEXUS_Clinical", C_PROPS, 0.02)
box("NEXUS_V05_REST_TOILET_BOWL", (X1 - 0.62, 2.62, Z0 + 0.28), (0.55, 0.45, 0.38),
    "NEXUS_Clinical", C_PROPS, 0.03)
box("NEXUS_V05_REST_TOILET_SEAT", (X1 - 0.62, 2.62, Z0 + 0.48), (0.58, 0.48, 0.05),
    "NEXUS_OffWhite", C_PROPS, 0.02)
box("NEXUS_V05_REST_FLUSH", (X1 - 0.28, 2.62, Z0 + 0.92), (0.12, 0.2, 0.06),
    "NEXUS_Steel", C_PROPS, 0.004)
# Privacy partition.
box("NEXUS_V05_REST_PARTITION", (-5.55, 2.82, Z0 + 1.0), (0.08, 1.35, 2.0),
    "NEXUS_Painted_Metal", C_STRUCT, 0.005)
box("NEXUS_V05_REST_PARTITION_TRIM", (-5.55, 2.82, Z0 + 2.02), (0.1, 1.4, 0.05),
    "NEXUS_Steel", C_STRUCT, 0.003)
# Sink counter on the north wall.
box("NEXUS_V05_REST_SINK_COUNTER", (-6.55, 4.35, Z0 + 0.84), (1.15, 0.55, 0.08),
    "NEXUS_Clinical", C_PROPS, 0.005)
box("NEXUS_V05_REST_SINK_BASIN", (-6.55, 4.3, Z0 + 0.78), (0.5, 0.38, 0.16),
    "NEXUS_OffWhite", C_PROPS, 0.02)
cyl("NEXUS_V05_REST_FAUCET", (-6.55, 4.52, Z0 + 0.98), 0.025, 0.18,
    "NEXUS_Steel", C_PROPS, "Z", 10)
box("NEXUS_V05_REST_MIRROR", (-6.55, 4.62, Z0 + 1.65), (0.9, 0.03, 0.75),
    "NEXUS_Mirror_Soft", C_PROPS, 0.003)
box("NEXUS_V05_REST_HAND_DRYER", (X1 - 0.16, 4.1, Z0 + 1.55), (0.18, 0.28, 0.42),
    "NEXUS_Steel", C_PROPS, 0.01)
box("NEXUS_V05_REST_BIN", (-4.75, 4.38, Z0 + 0.28), (0.28, 0.28, 0.56),
    "NEXUS_Painted_Metal", C_PROPS, 0.008)
box("NEXUS_V05_REST_GRAB_BAR", (X1 - 0.18, 3.15, Z0 + 0.9), (0.05, 0.55, 0.05),
    "NEXUS_Steel", C_PROPS, 0.004)
box("NEXUS_V05_REST_PAPER", (X1 - 0.16, 2.98, Z0 + 0.9), (0.08, 0.14, 0.14),
    "NEXUS_OffWhite", C_PROPS, 0.004)
box("NEXUS_V05_REST_LIGHT_PANEL", (-6.4, 3.3, Z0 + 2.93), (0.8, 0.3, 0.04),
    "NEXUS_CorridorLight", C_LIGHTS, 0.002)
ld = bpy.data.lights.new("NEXUS_V05_REST_LIGHT", "AREA")
ld.color = (0.82, 0.93, 1.0)
ld.energy = 120.0
ld.shape = "RECTANGLE"
ld.size = 0.8
ld.size_y = 0.3
lo = bpy.data.objects.new(ld.name, ld)
C_LIGHTS.objects.link(lo)
lo.location = (-6.4, 3.3, Z0 + 2.88)

# --- Roof plant. ---
box("NEXUS_V05_OFFICE_HVAC_CURB", (-6.2, 6.1, Z0 + H + 0.16), (1.0, 0.9, 0.14),
    "NEXUS_Steel", C_STRUCT, 0.006)
box("NEXUS_V05_OFFICE_HVAC", (-6.2, 6.1, Z0 + H + 0.52), (1.25, 0.95, 0.62),
    "NEXUS_Painted_Metal", C_PROPS, 0.01)
for i in range(5):
    box(f"NEXUS_V05_OFFICE_HVAC_GRILLE_{i}", (-6.2, 6.1 + (i - 2) * 0.13, Z0 + H + 0.84),
        (0.9, 0.04, 0.02), "NEXUS_Steel", C_PROPS, 0.001)
cyl("NEXUS_V05_OFFICE_HVAC_FAN", (-6.2, 6.1, Z0 + H + 0.9), 0.28, 0.08,
    "NEXUS_Steel", C_PROPS, "Z", 16)
box("NEXUS_V05_OFFICE_DUCT", (-4.72, 6.1, Z0 + H + 0.5), (0.4, 0.42, 0.4),
    "NEXUS_Rusted_Metal", C_PROPS, 0.006)
box("NEXUS_V05_OFFICE_ROOF_BEACON", (-7.85, 7.35, Z0 + H + 0.24), (0.14, 0.14, 0.18),
    "NEXUS_Amber", C_PROPS, 0.004)
# Exterior wall plate on the north face.
text_x("NEXUS_V05_OFFICE_EXT_SIGN", "NEXUS // ADMINISTRACION", X0 - 0.16, 5.0, Z0 + 2.55, 0.09)

# Cameras for review.
def camera(name, loc, target, lens=24.0):
    cd = bpy.data.cameras.new(name)
    co = bpy.data.objects.new(name, cd)
    C_CAMS.objects.link(co)
    co.location = Vector(loc)
    cd.lens = lens
    f = (Vector(target) - co.location).normalized()
    up = Vector((0, 0, 1))
    if abs(f.dot(up)) > 0.98:
        up = Vector((0, 1, 0))
    right = f.cross(up).normalized()
    up2 = right.cross(f).normalized()
    co.matrix_world = Matrix.Translation(co.location) @ Matrix((right, up2, -f)).transposed().to_4x4()
    return co


camera("NEXUS_V05_CAM_Office", (-7.85, 5.0, Z0 + 2.3), (-5.3, 7.0, Z0 + 1.0), 24.0)
camera("NEXUS_V05_CAM_Rest", (-7.8, 4.42, Z0 + 2.2), (-4.9, 2.75, Z0 + 1.0), 24.0)
camera("NEXUS_V05_CAM_OfficeExt", (-14.0, 4.0, Z0 + 2.4), (-6.2, 5.2, Z0 + 2.7), 28.0)

SCENE.camera = bpy.data.objects.get("NEXUS_V05_CAM_OfficeExt")
SCENE.view_settings.exposure = 1.5

path = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V05_level1_v21.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
print("LEVEL1_OFFICE_SAVED", path, os.path.getsize(path))
