"""Level 1 pass E: final fix of props, signs, materials, lights and cameras."""
import bpy
import bmesh
import math
import os
import random
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


def remove_obj(o):
    try:
        bpy.data.objects.remove(o, do_unlink=True)
    except Exception:
        pass


def remove_prefix(prefix):
    for o in list(bpy.data.objects):
        if o.name.startswith(prefix):
            remove_obj(o)


def remove_contains(parts):
    for o in list(bpy.data.objects):
        n = o.name
        if any(k in n for k in parts):
            remove_obj(o)


# ---------------------------------------------------------------------------
# Clean previous E pass and the specific faulty objects.
# ---------------------------------------------------------------------------
remove_prefix("NEXUS_V05_E_")

for name in (
    "NEXUS_V05_C_REC_RUG",
    "NEXUS_V05_REC_CLOCK",
    "NEXUS_V05_REC_CLOCK_HAND",
    "NEXUS_V05_REC_CLOCK_HAND2",
    "NEXUS_V05_C_SEC_CLOCK",
    "NEXUS_V05_C_SEC_CLOCK_H1",
    "NEXUS_V05_C_SEC_CLOCK_H2",
    "NEXUS_V05_D_SEC_CLOCK",
    "NEXUS_V05_D_SEC_CLOCK_FACE",
    "NEXUS_V05_D_SEC_EXT",
    "NEXUS_V05_C_ACC_XRAY_MON_FRAME",
    "NEXUS_V05_C_ACC_XRAY_MON_SCREEN",
    "NEXUS_V05_D_VEST_SHOWER_HEAD",
    "NEXUS_V05_D_VEST_SHOWER_PIPE",
):
    o = bpy.data.objects.get(name)
    if o:
        remove_obj(o)

remove_contains(("REC_PLANT_LEAF", "STORE_SIGN", "MAINT_SIGN", "C_ACC_XRAY_MON", "D_VEST_SHOWER"))
for o in list(bpy.data.objects):
    n = o.name
    if "EXTINGUISHER" in n or n.startswith("NEXUS_V05_D_CORR_EXT_") or n.startswith("NEXUS_V05_D_SEC_EXT"):
        remove_obj(o)

# ---------------------------------------------------------------------------
# Materials.
# ---------------------------------------------------------------------------
def principled(mat):
    if not mat or not mat.use_nodes:
        return None
    for n in mat.node_tree.nodes:
        if n.type == "BSDF_PRINCIPLED":
            return n
    return None


def set_input(bsdf, name, value):
    if bsdf and name in bsdf.inputs:
        bsdf.inputs[name].default_value = value


def adjust_material(name, base=None, rough=None, metallic=None, emission=None, emission_color=None):
    mat = bpy.data.materials.get(name)
    bsdf = principled(mat)
    if bsdf is None:
        return
    if base is not None:
        set_input(bsdf, "Base Color", (*base, 1.0))
    if rough is not None:
        set_input(bsdf, "Roughness", rough)
    if metallic is not None:
        set_input(bsdf, "Metallic", metallic)
    if emission is not None:
        set_input(bsdf, "Emission Strength", emission)
    if emission_color is not None and "Emission Color" in bsdf.inputs:
        set_input(bsdf, "Emission Color", (*emission_color, 1.0))


def make_material(name, base, rough=0.5, metallic=0.0, emission=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = principled(mat)
    set_input(bsdf, "Base Color", (*base, 1.0))
    set_input(bsdf, "Roughness", rough)
    set_input(bsdf, "Metallic", metallic)
    set_input(bsdf, "Emission Strength", emission)
    return mat


adjust_material("NEXUS_Plant", base=(0.01, 0.03, 0.012), rough=0.95, metallic=0.0)
adjust_material("NEXUS_Red", base=(0.4, 0.01, 0.005), rough=0.42, metallic=0.1, emission=0.5)
adjust_material("NEXUS_GaugeFace", base=(0.9, 0.9, 0.85), rough=0.3, metallic=0.0)
make_material("NEXUS_Foliage_Dark", (0.008, 0.025, 0.01), rough=0.96)
make_material("NEXUS_Extinguisher_Red", (0.22, 0.01, 0.008), rough=0.35, metallic=0.2)
make_material("NEXUS_Mirror_Soft", (0.72, 0.76, 0.8), rough=0.14, metallic=0.45)
make_material("NEXUS_Grime", (0.025, 0.022, 0.018), rough=0.9)
make_material("NEXUS_ClockFace", (0.82, 0.8, 0.72), rough=0.45)

# ---------------------------------------------------------------------------
# Mesh helpers.
# ---------------------------------------------------------------------------
def box(name, center, size, matname, col, bevel=0.008, rot=None):
    mesh = bpy.data.meshes.new(name)
    x, y, z = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
    verts = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
             (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
             (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    col.objects.link(o)
    o.location = center
    if rot:
        o.rotation_euler = rot
    mm = bpy.data.materials.get(matname)
    if mm:
        mesh.materials.append(mm)
    if bevel > 0:
        md = o.modifiers.new("Bevel", "BEVEL")
        md.width = bevel
        md.segments = 1
    return o


def cyl(name, center, radius, depth, matname, col, axis="Z", verts=24, bevel=0.0):
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
    mm = bpy.data.materials.get(matname)
    if mm:
        mesh.materials.append(mm)
    if bevel > 0:
        md = o.modifiers.new("Bevel", "BEVEL")
        md.width = bevel
        md.segments = 1
    return o


def ico(name, center, radius, matname, col, scale=(1, 1, 1), subdiv=1):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=1.0)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    col.objects.link(o)
    o.location = center
    o.scale = (radius * scale[0], radius * scale[1], radius * scale[2])
    mm = bpy.data.materials.get(matname)
    if mm:
        mesh.materials.append(mm)
    return o


def text_obj(name, body, loc, normal, size, matname, col=CS):
    n = Vector(normal).normalized()
    up = Vector((0, 0, 1))
    if abs(n.dot(up)) > 0.95:
        up = Vector((0, 1, 0))
    right = up.cross(n).normalized()
    up2 = n.cross(right).normalized()
    rot = Matrix((right, up2, n)).transposed().to_4x4()
    curve = bpy.data.curves.new(name + "_TEXT", type="FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    curve.extrude = 0.004
    o = bpy.data.objects.new(curve.name, curve)
    col.objects.link(o)
    o.matrix_world = Matrix.Translation(Vector(loc) + n * 0.01) @ rot
    mm = bpy.data.materials.get(matname)
    if mm:
        curve.materials.append(mm)
    return o


def sign(name, body, loc, normal, text_size=0.13, plate=(2.2, 0.4), mat_plate="NEXUS_SignPlate", mat_text="NEXUS_SignText"):
    n = Vector(normal).normalized()
    up = Vector((0, 0, 1))
    if abs(n.dot(up)) > 0.95:
        up = Vector((0, 1, 0))
    right = up.cross(n).normalized()
    up2 = n.cross(right).normalized()
    rot = Matrix((right, up2, n)).transposed().to_4x4()
    plate_o = box(name + "_PLATE", (0, 0, 0), (plate[0], plate[1], 0.04), mat_plate, CS, 0.006)
    plate_o.matrix_world = Matrix.Translation(Vector(loc) - n * 0.02) @ rot
    text_obj(name + "_TEXT", body, Vector(loc) + n * 0.015, n, text_size, mat_text, CS)


def aim_camera(name, loc, target, lens):
    cam = bpy.data.objects.get(name)
    if cam is None:
        cd = bpy.data.cameras.new(name)
        cam = bpy.data.objects.new(name, cd)
        CC.objects.link(cam)
    cam.location = Vector(loc)
    cam.data.lens = lens
    f = (Vector(target) - cam.location).normalized()
    up = Vector((0, 0, 1))
    if abs(f.dot(up)) > 0.98:
        up = Vector((0, 1, 0))
    right = f.cross(up).normalized()
    up2 = right.cross(f).normalized()
    cam.matrix_world = Matrix.Translation(cam.location) @ Matrix((right, up2, -f)).transposed().to_4x4()
    return cam


def area_light(name, loc, target, energy, color, size=3.0, size_y=1.5):
    ld = bpy.data.lights.new(name, "AREA")
    ld.energy = energy
    ld.color = color
    ld.shape = "RECTANGLE"
    ld.size = size
    ld.size_y = size_y
    lo = bpy.data.objects.new(name, ld)
    CL.objects.link(lo)
    lo.location = Vector(loc)
    direction = (Vector(target) - Vector(loc)).normalized()
    lo.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    return lo


def point_light(name, loc, energy, color, radius=0.25):
    ld = bpy.data.lights.new(name, "POINT")
    ld.energy = energy
    ld.color = color
    ld.shadow_soft_size = radius
    lo = bpy.data.objects.new(name, ld)
    CL.objects.link(lo)
    lo.location = Vector(loc)
    return lo


# ---------------------------------------------------------------------------
# Reception fixes.
# ---------------------------------------------------------------------------
# Move the suitcase away from the planter.
for o in list(bpy.data.objects):
    if "REC_SUITCASE" in o.name:
        o.location.x = -16.7
        o.location.y = 2.2

# Dark foliage clusters.
random.seed(11)
for plant_i, (cx, cy) in enumerate(((-18.0, 3.0), (-6.0, 3.0))):
    for k in range(13):
        ang = random.uniform(0, math.tau)
        rad = random.uniform(0.0, 0.42)
        px = cx + math.cos(ang) * rad
        py = cy + math.sin(ang) * rad
        pz = random.uniform(-4.55, -3.85)
        s = random.uniform(0.16, 0.27)
        sx = random.uniform(0.85, 1.35)
        sy = random.uniform(0.85, 1.35)
        sz = random.uniform(0.7, 1.2)
        ico(f"NEXUS_V05_E_REC_FOLIAGE_{plant_i}_{k}", (px, py, pz), s,
            "NEXUS_Foliage_Dark", CP, (sx, sy, sz), 2)

# Vertical clock on the west wall of reception.
def clock(name, center, normal, radius=0.25):
    n = Vector(normal).normalized()
    axis = "X" if abs(n.x) > 0.5 else "Y"
    cyl(name + "_RIM", center, radius * 1.08, 0.06, "NEXUS_Painted_Metal", CP, axis, 32)
    face_center = Vector(center) + n * 0.032
    cyl(name + "_FACE", face_center, radius, 0.02, "NEXUS_ClockFace", CP, axis, 32)
    # Tick marks.
    for i in range(12):
        a = math.tau * i / 12.0
        if axis == "X":
            p = face_center + Vector((0.0, math.sin(a) * radius * 0.78, math.cos(a) * radius * 0.78))
            t = box(f"{name}_TICK_{i}", p, (0.012, 0.022, 0.035), "NEXUS_Rubber", CP, 0.0)
            t.rotation_euler.x = -a
        else:
            p = face_center + Vector((math.sin(a) * radius * 0.78, 0.0, math.cos(a) * radius * 0.78))
            t = box(f"{name}_TICK_{i}", p, (0.022, 0.012, 0.035), "NEXUS_Rubber", CP, 0.0)
            t.rotation_euler.y = a
    # Hands: minute and hour.
    if axis == "X":
        h1 = box(name + "_H1", face_center + n * 0.01, (0.012, 0.02, 0.17), "NEXUS_Rubber", CP, 0.0)
        h1.rotation_euler.x = -0.5
        h2 = box(name + "_H2", face_center + n * 0.012, (0.012, 0.018, 0.11), "NEXUS_Rubber", CP, 0.0)
        h2.rotation_euler.x = -2.0
    else:
        h1 = box(name + "_H1", face_center + n * 0.01, (0.02, 0.012, 0.17), "NEXUS_Rubber", CP, 0.0)
        h1.rotation_euler.y = 0.5
        h2 = box(name + "_H2", face_center + n * 0.012, (0.018, 0.012, 0.11), "NEXUS_Rubber", CP, 0.0)
        h2.rotation_euler.y = 2.0


clock("NEXUS_V05_E_REC_CLOCK", (-19.80, 9.4, -2.9), (1, 0, 0), 0.25)

# ---------------------------------------------------------------------------
# Security fixes.
# ---------------------------------------------------------------------------
clock("NEXUS_V05_E_SEC_CLOCK", (7.0, 9.50, -2.85), (0, -1, 0), 0.22)

for name, energy in (
    ("NEXUS_V05_C_SEC_BEACON_LIGHT", 12.0),
    ("NEXUS_V05_SEC_BEACON_LIGHT", 10.0),
):
    o = bpy.data.objects.get(name)
    if o:
        o.data.energy = energy

# ---------------------------------------------------------------------------
# Control room scanner detail.
# ---------------------------------------------------------------------------
# Remove any remaining horizontal monitor slab.
remove_contains(("C_ACC_XRAY_MON",))

box("NEXUS_V05_E_CTRL_MON_FRAME", (14.86, 6.6, -4.4), (0.06, 0.9, 0.6), "NEXUS_Painted_Metal", CP, 0.008)
box("NEXUS_V05_E_CTRL_MON_SCREEN", (14.82, 6.6, -4.4), (0.02, 0.82, 0.52), "NEXUS_Screen", CP, 0.003)
box("NEXUS_V05_E_CTRL_MON_BASE", (14.86, 6.6, -4.76), (0.06, 0.5, 0.16), "NEXUS_Steel", CP, 0.006)
for i in range(5):
    box(f"NEXUS_V05_E_CTRL_BTN_{i}", (14.80, 6.35 + i * 0.1, -4.84), (0.02, 0.04, 0.04), "NEXUS_Amber" if i < 2 else "NEXUS_Screen", CP, 0.002)

# Conveyor rails and lead curtains.
for i, x in enumerate((15.03, 16.17)):
    box(f"NEXUS_V05_E_CTRL_RAIL_{i}", (x, 6.6, -4.04), (0.05, 3.4, 0.12), "NEXUS_Steel", CP, 0.004)
for end, y in enumerate((5.08, 8.12)):
    for i, x in enumerate((15.15, 15.45, 15.75, 16.05)):
        box(f"NEXUS_V05_E_CTRL_CURTAIN_{end}_{i}", (x, y, -4.42), (0.22, 0.02, 0.55), "NEXUS_Rubber", CP, 0.002)
for z, w in ((-4.22, 3.0), (-5.55, 3.0)):
    box(f"NEXUS_V05_E_CTRL_HAZ_{int(abs(z)*10)}", (14.90, 6.6, z), (0.02, w, 0.08), "NEXUS_Amber", CP, 0.002)

# Suitcase on the belt.
box("NEXUS_V05_E_CTRL_CASE", (15.6, 7.55, -3.90), (0.52, 0.34, 0.2), "NEXUS_Rubber", CP, 0.02)
box("NEXUS_V05_E_CTRL_CASE_HANDLE", (15.6, 7.55, -3.77), (0.16, 0.03, 0.04), "NEXUS_Steel", CP, 0.004)

sign("NEXUS_V05_E_CTRL_SIGN", "ESCANER // RAYOS X", (14.88, 7.55, -4.60), (-1, 0, 0), 0.085, (1.5, 0.28))

area_light("NEXUS_V05_E_CTRL_FILL", (13.8, 6.6, -2.7), (15.6, 6.6, -4.7), 300.0, (0.78, 0.88, 1.0), 3.0, 1.5)
aim_camera("NEXUS_V05_CAM_Control", (9.3, 2.7, -2.9), (15.4, 7.3, -4.2), 17.0)

# ---------------------------------------------------------------------------
# Locker room shower and mirrors.
# ---------------------------------------------------------------------------
# Replace mirror glass material.
for o in bpy.data.objects:
    if o.type == "MESH" and "B_VEST_MIRROR_GLASS" in o.name:
        mat = bpy.data.materials.get("NEXUS_Mirror_Soft")
        if mat:
            if o.data.materials:
                for i in range(len(o.data.materials)):
                    o.data.materials[i] = mat
            else:
                o.data.materials.append(mat)

# Shower tray and enclosure in the south-east corner.
box("NEXUS_V05_E_VEST_SHOWER_TRAY", (-9.7, -8.5, -5.60), (1.0, 1.0, 0.10), "NEXUS_Clinical", CP, 0.02)
box("NEXUS_V05_E_VEST_SHOWER_CURB_W", (-10.20, -8.5, -5.56), (0.06, 1.0, 0.09), "NEXUS_Concrete", CP, 0.006)
box("NEXUS_V05_E_VEST_SHOWER_CURB_N", (-9.7, -8.00, -5.56), (1.0, 0.06, 0.09), "NEXUS_Concrete", CP, 0.006)
cyl("NEXUS_V05_E_VEST_SHOWER_DRAIN", (-9.7, -8.5, -5.545), 0.07, 0.02, "NEXUS_Steel", CP, "Z", 16)
box("NEXUS_V05_E_VEST_SHOWER_TILE_E", (-9.15, -8.5, -4.2), (0.04, 1.1, 2.3), "NEXUS_Clinical", CS, 0.004)
box("NEXUS_V05_E_VEST_SHOWER_TILE_S", (-9.7, -9.54, -4.2), (1.1, 0.04, 2.3), "NEXUS_Clinical", CS, 0.004)
# Glass panels, leaving an opening for entry.
box("NEXUS_V05_E_VEST_SHOWER_GLASS_W", (-10.20, -8.5, -4.3), (0.04, 1.0, 2.2), "NEXUS_Glass", CP, 0.004)
box("NEXUS_V05_E_VEST_SHOWER_GLASS_N", (-9.45, -8.00, -4.3), (0.5, 0.04, 2.2), "NEXUS_Glass", CP, 0.004)
# Pipe, arm, head and controls.
cyl("NEXUS_V05_E_VEST_SHOWER_PIPE", (-9.15, -8.5, -3.7), 0.025, 2.0, "NEXUS_Steel", CP, "Z", 12)
cyl("NEXUS_V05_E_VEST_SHOWER_ARM", (-9.35, -8.5, -3.05), 0.025, 0.4, "NEXUS_Steel", CP, "X", 12)
cyl("NEXUS_V05_E_VEST_SHOWER_HEAD", (-9.55, -8.5, -3.05), 0.12, 0.035, "NEXUS_Steel", CP, "Z", 16)
box("NEXUS_V05_E_VEST_SHOWER_VALVE", (-9.15, -8.5, -3.55), (0.06, 0.12, 0.12), "NEXUS_Steel", CP, 0.006)
box("NEXUS_V05_E_VEST_SOAP", (-9.15, -8.2, -3.35), (0.05, 0.1, 0.16), "NEXUS_Steel", CP, 0.004)
sign("NEXUS_V05_E_VEST_SHOWER_SIGN", "DUCHA", (-10.23, -8.5, -3.35), (-1, 0, 0), 0.10, (0.6, 0.24))

# Lighting for mirrors and lockers.
point_light("NEXUS_V05_E_VEST_MIRROR_LIGHT", (-10.5, -6.3, -3.1), 90.0, (1.0, 0.9, 0.75), 0.3)
point_light("NEXUS_V05_E_VEST_LOCKER_LIGHT", (-14.5, -7.4, -3.0), 80.0, (0.95, 0.9, 0.8), 0.3)
aim_camera("NEXUS_V05_CAM_Vestuarios", (-18.5, -2.0, -3.0), (-11.0, -8.0, -3.2), 17.5)

# ---------------------------------------------------------------------------
# Storage.
# ---------------------------------------------------------------------------
for o in bpy.data.objects:
    n = o.name
    if "D_STORE_HOIST_BEAM" in n:
        o.location.z = -1.85
    elif "D_STORE_HOIST_TROLLEY" in n:
        o.location.z = -1.73
    elif "D_STORE_HOIST_CHAIN" in n:
        o.location.z = -2.55
        o.scale.z = 1.30 / 1.65
    elif "D_STORE_HOIST_HOOK" in n:
        o.location.z = -3.20

sign("NEXUS_V05_E_STORE_SIGN", "ALMACEN // SECTOR C", (-2.0, -9.54, -2.6), (0, 1, 0), 0.18, (4.0, 0.70))

# Broken crates and grime.
for i, (x, y, rot) in enumerate(((0.6, -4.4, 0.25), (-4.2, -4.8, -0.3), (2.0, -6.2, 0.12))):
    crate = box(f"NEXUS_V05_E_STORE_BROKEN_{i}", (x, y, F + 0.22), (0.55, 0.42, 0.44),
                "NEXUS_Debris", CP, 0.008, rot=(0, 0, rot))
    for j in range(4):
        box(f"NEXUS_V05_E_STORE_SPILL_{i}_{j}", (x - 0.3 + j * 0.2, y + 0.25, F + 0.06),
            (0.12, 0.08, 0.05), "NEXUS_Debris", CT, 0.002)
for i, (x, y) in enumerate(((-2.0, -6.0), (2.0, -7.6), (-5.5, -7.2))):
    cyl(f"NEXUS_V05_E_STORE_GRIME_{i}", (x, y, F + 0.006), 0.55, 0.012, "NEXUS_Grime", CT, "Z", 24)

# ---------------------------------------------------------------------------
# Maintenance.
# ---------------------------------------------------------------------------
for o in bpy.data.objects:
    if "B_MAINT_BARREL" in o.name:
        o.location.y = -3.55

# Gauge connector and face.
cyl("NEXUS_V05_E_MAINT_GAUGE_NECK", (17.3, -7.34, -4.2), 0.035, 0.12, "NEXUS_Steel", CP, "Y", 12)
for name in ("NEXUS_V05_B_MAINT_BOILER_GAUGE_FACE", "NEXUS_V05_B_MAINT_BOILER_GAUGE_NEEDLE"):
    o = bpy.data.objects.get(name)
    if o and o.type == "MESH":
        mat = bpy.data.materials.get("NEXUS_GaugeFace" if "FACE" in name else "NEXUS_Red")
        if mat:
            if o.data.materials:
                for i in range(len(o.data.materials)):
                    o.data.materials[i] = mat
            else:
                o.data.materials.append(mat)

# Air tank pipe, valve and gauge.
cyl("NEXUS_V05_E_MAINT_AIR_PIPE", (18.8, -5.0, -2.25), 0.06, 2.4, "NEXUS_Steel", CP, "Z", 12)
cyl("NEXUS_V05_E_MAINT_AIR_VALVE", (18.8, -5.0, -2.0), 0.13, 0.035, "NEXUS_Red", CP, "Z", 16)
cyl("NEXUS_V05_E_MAINT_AIR_GAUGE", (18.8, -4.92, -3.2), 0.10, 0.04, "NEXUS_Steel", CP, "Y", 16)
cyl("NEXUS_V05_E_MAINT_AIR_GAUGE_FACE", (18.8, -4.90, -3.2), 0.08, 0.01, "NEXUS_GaugeFace", CP, "Y", 16)

# Lighting and camera.
for name, energy in (
    ("NEXUS_V05_B_MAINT_LAMP_A_LIGHT", 70.0),
    ("NEXUS_V05_B_MAINT_LAMP_B_LIGHT", 70.0),
    ("NEXUS_V05_B_MAINT_BENCH_LIGHT", 300.0),
):
    o = bpy.data.objects.get(name)
    if o:
        o.data.energy = energy
area_light("NEXUS_V05_E_MAINT_FILL", (11.5, -6.0, -2.2), (12.0, -8.0, -3.2), 450.0, (1.0, 0.82, 0.62), 4.0, 3.0)
aim_camera("NEXUS_V05_CAM_Mantenimiento", (18.8, -2.2, -3.0), (9.5, -7.8, -3.4), 17.5)

# ---------------------------------------------------------------------------
# Corridor signs and extinguishers.
# ---------------------------------------------------------------------------
corridor_signs = (
    ("RECEPCION", -12.0, 1.54, -1),
    ("SEGURIDAD", 3.0, 1.54, -1),
    ("CONTROL DE ACCESO", 13.0, 1.54, -1),
    ("VESTUARIOS", -14.0, -1.54, 1),
    ("ALMACEN", -2.0, -1.54, 1),
    ("MANTENIMIENTO", 13.0, -1.54, 1),
)
for body, x, y, ny in corridor_signs:
    sign(f"NEXUS_V05_E_CORR_SIGN_{body.replace(' ', '_')}", body,
         (x, y, -1.95), (0, ny, 0), 0.13, (2.2, 0.38))

ext_locations = (
    ("REC", (-4.27, 10.5, -4.55)),
    ("SEC", (7.72, 3.0, -4.55)),
    ("ACC", (16.77, 4.2, -4.55)),
    ("CORR0", (-17.0, 1.5, -4.55)),
    ("CORR1", (1.0, -1.5, -4.55)),
    ("CORR2", (16.0, 1.5, -4.55)),
    ("MAINT", (19.45, -2.15, -4.55)),
    ("STORE", (3.55, -2.5, -4.55)),
)


def extinguisher(key, loc):
    x, y, z = loc
    cyl(f"NEXUS_V05_E_EXT_{key}_BODY", (x, y, z), 0.09, 0.52, "NEXUS_Extinguisher_Red", CP, "Z", 20)
    cyl(f"NEXUS_V05_E_EXT_{key}_TOP", (x, y, z + 0.27), 0.095, 0.04, "NEXUS_Rubber", CP, "Z", 20)
    cyl(f"NEXUS_V05_E_EXT_{key}_BOTTOM", (x, y, z - 0.27), 0.095, 0.04, "NEXUS_Rubber", CP, "Z", 20)
    cyl(f"NEXUS_V05_E_EXT_{key}_LABEL", (x, y, z), 0.093, 0.14, "NEXUS_OffWhite", CP, "Z", 20)
    box(f"NEXUS_V05_E_EXT_{key}_HANDLE", (x, y, z + 0.37), (0.04, 0.04, 0.14), "NEXUS_Rubber", CP, 0.004)
    box(f"NEXUS_V05_E_EXT_{key}_LEVER", (x + 0.07, y, z + 0.38), (0.16, 0.03, 0.03), "NEXUS_Rubber", CP, 0.003)
    box(f"NEXUS_V05_E_EXT_{key}_HOSE", (x + 0.10, y, z - 0.10), (0.025, 0.025, 0.32), "NEXUS_Rubber", CP, 0.002, rot=(0, 0.18, 0))
    cyl(f"NEXUS_V05_E_EXT_{key}_NOZZLE", (x + 0.12, y, z - 0.26), 0.025, 0.08, "NEXUS_Rubber", CP, "Z", 12)


for key, loc in ext_locations:
    extinguisher(key, loc)

# ---------------------------------------------------------------------------
# Final state.
# ---------------------------------------------------------------------------
aim_camera("NEXUS_V05_CAM_Corridor", (-20.5, 0.0, -2.8), (18.0, 0.0, -2.8), 20.0)
SCENE.camera = bpy.data.objects["NEXUS_V05_CAM_Corridor"]
SCENE.view_settings.exposure = 1.5
path = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V05_level1_v18.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
print("V18_SAVED", path, os.path.getsize(path))
