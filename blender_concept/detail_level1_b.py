"""Detail pass B for Level 1: locker room, storage and maintenance.

Builds real open shelving, sinks, benches, workshop, boiler and environmental
story details.  Every new object uses the NEXUS_V05_B_ prefix so the script is
safe to re-run: previous pass-B objects are removed first.
"""
import bpy
import math
import os
from mathutils import Vector, Matrix

ROOT = "/home/riyo/Documentos/game"
Z1 = -5.8
F = -5.65
PREFIX = "NEXUS_V05_B_"

CS = bpy.data.collections["V05_STRUCT"]
CP = bpy.data.collections["V05_PROPS"]
CL = bpy.data.collections["V05_LIGHTS"]
CC = bpy.data.collections["V05_CAMS"]
CT = bpy.data.collections["V05_STORY"]


# ---------------------------------------------------------------- cleanup ---
for o in list(bpy.data.objects):
    if o.name.startswith(PREFIX):
        bpy.data.objects.remove(o, do_unlink=True)

# Old storage props that were solid blocks, boxes hidden inside them, or
# barrels outside the room.
for o in list(bpy.data.objects):
    if o.name.startswith(("NEXUS_V05_STORE_SHELF_",
                          "NEXUS_V05_STORE_BOX_",
                          "NEXUS_V05_STORE_BARREL_")):
        bpy.data.objects.remove(o, do_unlink=True)

# Put the existing bags on top of the central bench instead of inside it.
for name in ("NEXUS_V05_LOCK_BAG_0", "NEXUS_V05_LOCK_BAG_1"):
    o = bpy.data.objects.get(name)
    if o:
        o.location.z = -5.10


# --------------------------------------------------------------- materials --
def mat(name):
    return bpy.data.materials.get(name)


def new_mat(name, base, rough=0.5, metallic=0.0):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.diffuse_color = (*base, 1.0)
    bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        if bsdf.inputs.get("Base Color"):
            bsdf.inputs["Base Color"].default_value = (*base, 1.0)
        if bsdf.inputs.get("Roughness"):
            bsdf.inputs["Roughness"].default_value = rough
        if bsdf.inputs.get("Metallic"):
            bsdf.inputs["Metallic"].default_value = metallic
    return m


new_mat("NEXUS_Wood", (0.20, 0.12, 0.06), 0.78)
new_mat("NEXUS_Mirror", (0.90, 0.92, 0.95), 0.03, 1.0)
new_mat("NEXUS_Oil", (0.012, 0.010, 0.008), 0.10, 0.0)


# ------------------------------------------------------------------ helpers --
def box(name, center, size, matname, col=CP, bevel=0.008, rot=None):
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
    m = mat(matname)
    if m:
        mesh.materials.append(m)
    if bevel > 0:
        b = min(bevel, min(size) * 0.22)
        md = o.modifiers.new("Bevel", "BEVEL")
        md.width = b
        md.segments = 1
    return o


def rod(name, a, b, radius, matname, col=CP, verts=10):
    a = Vector(a)
    b = Vector(b)
    d = b - a
    length = d.length
    if length < 0.0001:
        return None
    mesh = bpy.data.meshes.new(name)
    vl = []
    for z in (-length * 0.5, length * 0.5):
        for i in range(verts):
            ang = 2.0 * math.pi * i / verts
            vl.append((math.cos(ang) * radius, math.sin(ang) * radius, z))
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
    o.location = (a + b) * 0.5
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    m = mat(matname)
    if m:
        mesh.materials.append(m)
    return o


def disk(name, center, radius, depth, matname, col=CP, axis="Z"):
    c = Vector(center)
    if axis == "X":
        a = c - Vector((depth * 0.5, 0, 0))
        b = c + Vector((depth * 0.5, 0, 0))
    elif axis == "Y":
        a = c - Vector((0, depth * 0.5, 0))
        b = c + Vector((0, depth * 0.5, 0))
    else:
        a = c - Vector((0, 0, depth * 0.5))
        b = c + Vector((0, 0, depth * 0.5))
    return rod(name, a, b, radius, matname, col, 24)


def cone(name, center, r_bottom, r_top, depth, matname, col=CP, verts=20):
    mesh = bpy.data.meshes.new(name)
    vl = []
    for z, r in ((-depth * 0.5, r_bottom), (depth * 0.5, r_top)):
        for i in range(verts):
            ang = 2.0 * math.pi * i / verts
            vl.append((math.cos(ang) * r, math.sin(ang) * r, z))
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
    m = mat(matname)
    if m:
        mesh.materials.append(m)
    return o


def sign(name, body, loc, normal, size=0.13):
    n = Vector(normal).normalized()
    up = Vector((0, 0, 1))
    if abs(n.dot(up)) > 0.95:
        up = Vector((0, 1, 0))
    right = up.cross(n).normalized()
    up2 = n.cross(right).normalized()
    rot = Matrix((right, up2, n)).transposed().to_4x4()
    w = max(0.5, len(body) * size * 0.62 + 0.25)
    h = size * 1.75
    plate = box(name + "_PLATE", (0, 0, 0), (w, h, 0.06),
                "NEXUS_SignPlate", CS, 0.006)
    plate.matrix_world = Matrix.Translation(Vector(loc) + n * 0.035) @ rot
    cu = bpy.data.curves.new(name + "_TEXT", type="FONT")
    cu.body = body
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.size = size
    cu.extrude = 0.004
    o = bpy.data.objects.new(cu.name, cu)
    CS.objects.link(o)
    o.matrix_world = Matrix.Translation(Vector(loc) + n * 0.072) @ rot
    o.data.materials.append(mat("NEXUS_SignText") or mat("NEXUS_Amber"))


def crate(name, center, size, matname="NEXUS_Debris", band=False):
    box(name, center, size, matname, CP, 0.012)
    box(name + "_TAPE",
        (center[0], center[1], center[2] + size[2] * 0.5 + 0.004),
        (size[0] * 0.16, size[1] * 0.94, 0.006),
        "NEXUS_OffWhite", CP, 0.001)
    if band:
        box(name + "_BAND", center,
            (size[0] * 1.012, size[1] * 1.012, min(0.03, size[2] * 0.12)),
            "NEXUS_Painted_Metal", CP, 0.001)


def barrel(name, center, radius=0.33, height=0.95,
           body="NEXUS_Rusted_Metal"):
    c = Vector(center)
    rod(name, (c.x, c.y, c.z), (c.x, c.y, c.z + height),
        radius, body, CP, 16)
    for i, dz in enumerate((0.18, 0.50, 0.82)):
        disk(f"{name}_RING_{i}", (c.x, c.y, c.z + dz), radius + 0.015,
             0.035, "NEXUS_Steel", CP)
    disk(name + "_LID", (c.x, c.y, c.z + height + 0.012),
         radius, 0.024, "NEXUS_Steel", CP)


def area_light(name, loc, energy, color, size, size_y=None, rot=(0, 0, 0)):
    ld = bpy.data.lights.new(name, "AREA")
    ld.energy = energy
    ld.color = color
    if size_y:
        ld.shape = "RECTANGLE"
        ld.size = size
        ld.size_y = size_y
    else:
        ld.shape = "SQUARE"
        ld.size = size
    lo = bpy.data.objects.new(ld.name, ld)
    CL.objects.link(lo)
    lo.location = loc
    lo.rotation_euler = rot
    return lo


def point_light(name, loc, energy, color, radius=0.18):
    ld = bpy.data.lights.new(name, "POINT")
    ld.energy = energy
    ld.color = color
    ld.shadow_soft_size = radius
    lo = bpy.data.objects.new(ld.name, ld)
    CL.objects.link(lo)
    lo.location = loc
    return lo


def pendant(name, x, y, ceiling_z, drop, energy, color):
    bottom = ceiling_z - drop
    rod(name + "_CORD", (x, y, ceiling_z), (x, y, bottom + 0.18),
        0.010, "NEXUS_Rubber", CS)
    cone(name + "_SHADE", (x, y, bottom + 0.08),
         0.30, 0.055, 0.22, "NEXUS_Painted_Metal", CS, 24)
    disk(name + "_BULB", (x, y, bottom - 0.025), 0.055, 0.09,
         "NEXUS_CorridorLight", CS)
    point_light(name + "_LIGHT", (x, y, bottom - 0.16), energy, color, 0.22)


# =============================================================== VESTUARIOS ==
# Bench legs for the existing central bench.
for i, (x, y) in enumerate(((-16.8, -5.25), (-11.2, -5.25),
                            (-16.8, -4.75), (-11.2, -4.75))):
    box(f"{PREFIX}VEST_BENCH_LEG_{i}", (x, y, -5.525),
        (0.08, 0.08, 0.25), "NEXUS_Painted_Metal", CP, 0.004)

# Second bench along the west wall.
box(f"{PREFIX}VEST_BENCH2", (-18.30, -6.50, -5.35),
    (0.80, 4.00, 0.10), "NEXUS_Painted_Metal", CP, 0.012)
for i, y in enumerate((-8.30, -4.70)):
    for j, x in enumerate((-18.60, -18.00)):
        box(f"{PREFIX}VEST_BENCH2_LEG_{i}_{j}", (x, y, -5.525),
            (0.08, 0.08, 0.25), "NEXUS_Painted_Metal", CP, 0.004)

# Sinks and mirrors along the east wall.
sign("NEXUS_V05_B_VEST_LAVABOS", "LAVABOS",
     (-9.16, -6.30, -3.22), (-1, 0, 0), 0.085)

box(f"{PREFIX}VEST_TILE", (-9.15, -6.30, -5.05),
    (0.03, 3.80, 1.20), "NEXUS_Clinical", CS, 0.004)
box(f"{PREFIX}VEST_COUNTER", (-9.42, -6.30, -4.80),
    (0.55, 3.80, 0.10), "NEXUS_OffWhite", CP, 0.012)
box(f"{PREFIX}VEST_COUNTER_FRONT", (-9.68, -6.30, -5.25),
    (0.04, 3.80, 0.80), "NEXUS_Clinical", CP, 0.006)
for i, y in enumerate((-7.35, -6.30, -5.25)):
    box(f"{PREFIX}VEST_BASIN_{i}", (-9.42, y, -4.72),
        (0.44, 0.44, 0.08), "NEXUS_Clinical", CP, 0.02)
    disk(f"{PREFIX}VEST_DRAIN_{i}", (-9.42, y, -4.675),
         0.045, 0.010, "NEXUS_Steel", CP)
    rod(f"{PREFIX}VEST_FAUCET_{i}_UP", (-9.18, y, -4.74),
        (-9.18, y, -4.34), 0.024, "NEXUS_Steel", CP)
    rod(f"{PREFIX}VEST_FAUCET_{i}_OUT", (-9.18, y, -4.34),
        (-9.36, y, -4.34), 0.022, "NEXUS_Steel", CP)
    rod(f"{PREFIX}VEST_FAUCET_{i}_DOWN", (-9.36, y, -4.34),
        (-9.36, y, -4.48), 0.018, "NEXUS_Steel", CP)
    box(f"{PREFIX}VEST_FAUCET_{i}_HANDLE", (-9.18, y + 0.12, -4.38),
        (0.05, 0.12, 0.03), "NEXUS_Steel", CP, 0.004)

for i, y in enumerate((-7.35, -6.30, -5.25)):
    box(f"{PREFIX}VEST_MIRROR_FRAME_{i}", (-9.16, y, -3.95),
        (0.04, 1.00, 1.20), "NEXUS_Steel", CP, 0.008)
    box(f"{PREFIX}VEST_MIRROR_GLASS_{i}", (-9.19, y, -3.95),
        (0.02, 0.88, 1.08), "NEXUS_Mirror", CP, 0.002)

# Bloody handprint on the middle mirror.
box(f"{PREFIX}VEST_HAND_PALM", (-9.205, -6.30, -4.08),
    (0.012, 0.12, 0.14), "NEXUS_Blood_Dried", CT, 0.001)
for i, (dy, dz, h) in enumerate(((-0.06, 0.13, 0.09),
                                  (-0.02, 0.15, 0.10),
                                  (0.02, 0.14, 0.09),
                                  (0.06, 0.12, 0.08))):
    box(f"{PREFIX}VEST_HAND_FINGER_{i}", (-9.205, -6.30 + dy, -4.08 + dz),
        (0.012, 0.025, h), "NEXUS_Blood_Dried", CT, 0.001)
box(f"{PREFIX}VEST_HAND_THUMB", (-9.205, -6.36, -4.08),
    (0.012, 0.03, 0.08), "NEXUS_Blood_Dried", CT, 0.001)

# Extra lockers on the north wall, both sides of the door.
def locker(name, cx, cy, width=0.85, depth=0.50, height=2.0):
    box(name, (cx, cy, F + height * 0.5), (width, depth, height),
        "NEXUS_Painted_Metal", CP, 0.012)
    front = cy - depth * 0.5 - 0.006
    box(name + "_SEAM", (cx, front, F + height * 0.5),
        (0.015, 0.012, height * 0.92), "NEXUS_Steel", CP, 0.001)
    box(name + "_HANDLE", (cx + width * 0.28, front - 0.022,
                           F + height * 0.52),
        (0.045, 0.03, 0.12), "NEXUS_Steel", CP, 0.004)
    for i in range(3):
        box(f"{name}_VENT_{i}", (cx, front - 0.006,
                                 F + height - 0.18 - i * 0.06),
            (width * 0.55, 0.01, 0.015), "NEXUS_Concrete_Dark", CP, 0.001)
    box(name + "_TOP", (cx, cy, F + height + 0.025),
        (width + 0.05, depth + 0.05, 0.05), "NEXUS_Painted_Metal", CP, 0.005)


for i, x in enumerate((-18.28, -17.38, -11.90, -11.00)):
    locker(f"{PREFIX}VEST_LOCKER_N_{i}", x, -2.12)

# Towels, shoes, laundry and wet-floor details.
for i, (x, y, w, d) in enumerate(((-15.4, -5.00, 0.50, 0.34),
                                  (-13.0, -4.98, 0.44, 0.30),
                                  (-18.30, -6.10, 0.34, 0.44),
                                  (-18.30, -6.80, 0.34, 0.44))):
    box(f"{PREFIX}VEST_TOWEL_{i}", (x, y, -5.275),
        (w, d, 0.05), "NEXUS_OffWhite", CP, 0.006)

for i, (x, y, rz) in enumerate(((-16.2, -5.35, 0.2), (-15.7, -5.30, -0.3),
                                (-12.4, -5.32, 0.4), (-11.9, -5.28, -0.1),
                                (-17.8, -4.90, 0.0))):
    box(f"{PREFIX}VEST_SHOE_{i}", (x, y, -5.58),
        (0.26, 0.11, 0.07), "NEXUS_Rubber", CP, 0.02, (0, 0, rz))

# Discarded coverall.
box(f"{PREFIX}VEST_COVERALL", (-11.2, -6.2, -5.60),
    (0.70, 0.46, 0.08), "NEXUS_Green", CT, 0.01, (0, 0, 0.4))
box(f"{PREFIX}VEST_COVERALL_ARM", (-11.5, -6.05, -5.58),
    (0.42, 0.18, 0.07), "NEXUS_Green", CT, 0.01, (0, 0, -0.5))

# Laundry cart in the south-east corner.
box(f"{PREFIX}VEST_CART_BASE", (-9.72, -8.55, -5.45),
    (0.80, 0.62, 0.10), "NEXUS_Painted_Metal", CP, 0.01)
box(f"{PREFIX}VEST_CART_BAG", (-9.72, -8.55, -4.98),
    (0.70, 0.52, 0.72), "NEXUS_OffWhite", CP, 0.02)
for i, (dx, dy) in enumerate(((-0.34, -0.24), (0.34, -0.24),
                               (-0.34, 0.24), (0.34, 0.24))):
    rod(f"{PREFIX}VEST_CART_POST_{i}",
        (-9.72 + dx, -8.55 + dy, -5.55),
        (-9.72 + dx, -8.55 + dy, -4.32), 0.025,
        "NEXUS_Painted_Metal", CP)
for i, dy in enumerate((-0.24, 0.24)):
    disk(f"{PREFIX}VEST_CART_WHEEL_{i}", (-9.45, -8.55 + dy, -5.52),
         0.09, 0.06, "NEXUS_Rubber", CP, "Y")

# Mop bucket, mop and wet-floor cone.
disk(f"{PREFIX}VEST_BUCKET", (-9.78, -3.10, -5.35),
     0.24, 0.50, "NEXUS_Amber", CP)
rod(f"{PREFIX}VEST_MOP_HANDLE", (-9.78, -3.10, -5.10),
    (-9.55, -3.10, -2.5), 0.022, "NEXUS_Wood", CP)
box(f"{PREFIX}VEST_MOP_HEAD", (-9.55, -3.10, -3.2),
    (0.16, 0.36, 0.10), "NEXUS_OffWhite", CP, 0.03)
cone(f"{PREFIX}VEST_WET_SIGN", (-10.55, -4.10, -5.28),
     0.19, 0.025, 0.62, "NEXUS_Amber", CP, 18)
disk(f"{PREFIX}VEST_FLOOR_DRAIN", (-13.20, -7.20, -5.645),
     0.18, 0.012, "NEXUS_Steel", CP)

# Wall vent, sign and light.
box(f"{PREFIX}VEST_VENT", (-14.0, -1.90, -2.62),
    (0.90, 0.06, 0.34), "NEXUS_Steel", CS, 0.01)
for i in range(6):
    box(f"{PREFIX}VEST_VENT_SLAT_{i}", (-14.0, -1.94, -2.75 + i * 0.055),
        (0.78, 0.02, 0.018), "NEXUS_Concrete_Dark", CS, 0.001)

sign("NEXUS_V05_B_VEST_SIGN", "VESTUARIOS",
     (-14.0, -1.84, -2.93), (0, -1, 0), 0.145)
sign("NEXUS_V05_B_VEST_NOTICE", "DUCHAS FUERA DE SERVICIO",
     (-18.94, -6.30, -2.70), (1, 0, 0), 0.075)
area_light(f"{PREFIX}VEST_SINK_LIGHT", (-10.80, -6.30, -1.95),
           170.0, (0.80, 0.90, 1.0), 1.5, 0.28)


# ================================================================== ALMACEN ==
def rack(name, cx, cy, width, depth, height, levels, axis="X"):
    """Open warehouse rack: four posts, front/back beams and shelf decks."""
    hw = width * 0.5 - 0.055
    hd = depth * 0.5 - 0.055
    for i, (sx, sy) in enumerate(((-hw, -hd), (hw, -hd),
                                   (-hw, hd), (hw, hd))):
        if axis == "X":
            px, py = cx + sx, cy + sy
        else:
            px, py = cx + sy, cy + sx
        box(f"{name}_POST_{i}", (px, py, F + height * 0.5),
            (0.09, 0.09, height), "NEXUS_Amber", CP, 0.008)

    for li, level in enumerate(levels):
        if axis == "X":
            box(f"{name}_DECK_{li}", (cx, cy, F + level - 0.02),
                (width - 0.04, depth - 0.04, 0.04),
                "NEXUS_Steel", CP, 0.004)
            for side, sy in (("F", -depth * 0.5), ("B", depth * 0.5)):
                box(f"{name}_BEAM_{li}_{side}", (cx, cy + sy,
                                                 F + level - 0.07),
                    (width, 0.06, 0.12), "NEXUS_Amber", CP, 0.004)
        else:
            box(f"{name}_DECK_{li}", (cx, cy, F + level - 0.02),
                (depth - 0.04, width - 0.04, 0.04),
                "NEXUS_Steel", CP, 0.004)
            for side, sx in (("F", -depth * 0.5), ("B", depth * 0.5)):
                box(f"{name}_BEAM_{li}_{side}", (cx + sx, cy,
                                                 F + level - 0.07),
                    (0.06, width, 0.12), "NEXUS_Amber", CP, 0.004)


def rack_crate(name, rack_cx, rack_cy, offset, level, w, d, h,
               axis="X", matname="NEXUS_Debris", band=True):
    if axis == "X":
        loc = (rack_cx + offset, rack_cy, F + level + h * 0.5 + 0.008)
        size = (w, d, h)
    else:
        loc = (rack_cx, rack_cy + offset, F + level + h * 0.5 + 0.008)
        size = (d, w, h)
    crate(name, loc, size, matname, band)


south_racks = (-6.20, -2.00, 2.20)
for ri, rx in enumerate(south_racks):
    rack(f"{PREFIX}STORE_RACK_S_{ri}", rx, -9.23, 3.20, 0.65, 2.75,
         (0.18, 1.00, 1.80, 2.55), "X")
    patterns = (
        ((-0.85, 0.18, 0.70, 0.50, 0.42), (0.85, 0.18, 0.62, 0.48, 0.50),
         (-1.10, 1.00, 0.58, 0.44, 0.36), (0.00, 1.00, 0.66, 0.50, 0.42),
         (1.10, 1.00, 0.52, 0.42, 0.34), (-0.75, 1.80, 0.60, 0.46, 0.38),
         (0.75, 1.80, 0.52, 0.42, 0.32), (0.00, 2.55, 0.56, 0.42, 0.30)),
        ((-0.90, 0.18, 0.62, 0.48, 0.45), (0.75, 0.18, 0.72, 0.50, 0.38),
         (-1.05, 1.00, 0.56, 0.42, 0.35), (0.05, 1.00, 0.62, 0.46, 0.42),
         (1.05, 1.00, 0.50, 0.40, 0.30), (-0.65, 1.80, 0.48, 0.40, 0.34),
         (0.65, 1.80, 0.56, 0.44, 0.30), (0.00, 2.55, 0.54, 0.40, 0.28)),
        ((-0.80, 0.18, 0.58, 0.46, 0.36), (0.80, 0.18, 0.66, 0.50, 0.44),
         (-1.00, 1.00, 0.62, 0.44, 0.38), (0.00, 1.00, 0.58, 0.46, 0.32),
         (1.00, 1.00, 0.54, 0.40, 0.40), (-0.60, 1.80, 0.52, 0.40, 0.30),
         (0.60, 1.80, 0.58, 0.42, 0.34), (0.00, 2.55, 0.50, 0.38, 0.28)),
    )
    for bi, (off, lv, w, d, h) in enumerate(patterns[ri]):
        rack_crate(f"{PREFIX}STORE_CRATE_S_{ri}_{bi}",
                   rx, -9.23, off, lv, w, d, h, "X",
                   "NEXUS_Debris" if bi % 3 else "NEXUS_Rusted_Metal",
                   band=(bi % 2 == 0))

for ri, ry in enumerate((-7.40, -4.40)):
    rack(f"{PREFIX}STORE_RACK_W_{ri}", -7.53, ry, 2.40, 0.65, 2.75,
         (0.18, 1.00, 1.80, 2.55), "Y")
    for bi, (off, lv, w, d, h) in enumerate(((-0.55, 0.18, 0.62, 0.46, 0.42),
                                              (0.55, 0.18, 0.55, 0.42, 0.36),
                                              (-0.55, 1.00, 0.58, 0.44, 0.34),
                                              (0.55, 1.00, 0.52, 0.40, 0.40),
                                              (0.00, 1.80, 0.56, 0.42, 0.30))):
        rack_crate(f"{PREFIX}STORE_CRATE_W_{ri}_{bi}",
                   -7.53, ry, off, lv, w, d, h, "Y",
                   "NEXUS_Debris", band=(bi % 2 == 0))


def pallet(name, center, size=(1.20, 1.00)):
    cx, cy = center
    for i, y in enumerate((-0.42, 0.0, 0.42)):
        box(f"{name}_BLOCK_{i}", (cx, cy + y, F + 0.05),
            (size[0] * 0.85, 0.10, 0.10), "NEXUS_Wood", CP, 0.006)
    for i, x in enumerate((-0.48, -0.24, 0.0, 0.24, 0.48)):
        box(f"{name}_PLANK_{i}", (cx + x * size[0], cy, F + 0.12),
            (0.16, size[1], 0.05), "NEXUS_Wood", CP, 0.004)
    for i, y in enumerate((-0.46, 0.46)):
        box(f"{name}_RUNNER_{i}", (cx, cy + y * size[1], F + 0.035),
            (size[0], 0.08, 0.07), "NEXUS_Wood", CP, 0.004)


pallet(f"{PREFIX}STORE_PALLET_0", (-3.20, -5.30))
crate(f"{PREFIX}STORE_PALLET_0_CRATE_0", (-3.52, -5.30, -5.24),
      (0.58, 0.62, 0.44), "NEXUS_Debris", True)
crate(f"{PREFIX}STORE_PALLET_0_CRATE_1", (-2.88, -5.30, -5.22),
      (0.56, 0.58, 0.48), "NEXUS_Debris", False)
crate(f"{PREFIX}STORE_PALLET_0_CRATE_2", (-3.20, -5.30, -4.80),
      (0.62, 0.60, 0.38), "NEXUS_Rusted_Metal", True)

pallet(f"{PREFIX}STORE_PALLET_1", (0.90, -3.80), (1.10, 0.95))
for i, (dx, dy, w, d, h) in enumerate(((-0.28, -0.22, 0.48, 0.42, 0.34),
                                        (0.28, -0.22, 0.46, 0.40, 0.30),
                                        (-0.28, 0.22, 0.44, 0.38, 0.38),
                                        (0.28, 0.22, 0.48, 0.40, 0.32))):
    crate(f"{PREFIX}STORE_PALLET_1_CRATE_{i}",
          (0.90 + dx, -3.80 + dy, -5.16 + h * 0.5),
          (w, d, h), "NEXUS_Debris", (i % 2 == 0))

# Barrel cluster by the west wall.
for i, (x, y) in enumerate(((-6.90, -3.05), (-6.15, -3.05),
                             (-6.55, -2.38))):
    barrel(f"{PREFIX}STORE_BARREL_{i}", (x, y, F), 0.30, 0.90,
           "NEXUS_Rusted_Metal" if i != 1 else "NEXUS_Painted_Metal")

# Hand truck.
box(f"{PREFIX}STORE_TRUCK_TOE", (2.85, -6.55, -5.52),
    (0.52, 0.70, 0.08), "NEXUS_Steel", CP, 0.01)
for i, dx in enumerate((-0.22, 0.22)):
    rod(f"{PREFIX}STORE_TRUCK_RAIL_{i}", (2.85 + dx, -6.55, -5.48),
        (2.85 + dx, -6.55, -3.85), 0.026, "NEXUS_Steel", CP)
for i, z in enumerate((-5.15, -4.65, -4.15)):
    rod(f"{PREFIX}STORE_TRUCK_CROSS_{i}", (2.85, -6.55, z),
        (2.85, -7.15, z), 0.020, "NEXUS_Steel", CP)
for i, dy in enumerate((-6.85, -6.25)):
    disk(f"{PREFIX}STORE_TRUCK_WHEEL_{i}", (2.85, dy, -5.52),
         0.18, 0.08, "NEXUS_Rubber", CP, "X")

# Fallen shelf panel and spilled boxes near the east wall.
box(f"{PREFIX}STORE_FALLEN_SHELF", (3.58, -4.35, -4.85),
    (0.06, 2.00, 1.60), "NEXUS_Painted_Metal", CP, 0.012, (0, -0.35, 0))
for i, (x, y, z, rz) in enumerate(((2.92, -5.20, -5.48, 0.25),
                                    (3.20, -4.90, -5.38, -0.18),
                                    (2.78, -3.95, -5.50, 0.55))):
    crate(f"{PREFIX}STORE_SPILL_{i}", (x, y, z),
          (0.52, 0.42, 0.30), "NEXUS_Debris", i == 1)

# Floor markings and warning stripe at the door.
box(f"{PREFIX}STORE_FLOOR_LINE", (-2.0, -8.55, F + 0.012),
    (11.2, 0.08, 0.012), "NEXUS_Amber", CS, 0.002)
box(f"{PREFIX}STORE_FLOOR_LINE_2", (-2.0, -2.75, F + 0.012),
    (11.2, 0.06, 0.012), "NEXUS_Amber", CS, 0.002)
for i in range(5):
    box(f"{PREFIX}STORE_DOOR_HAZ_{i}", (-2.0 + (i - 2) * 0.34,
                                        -2.28, F + 0.013),
        (0.18, 0.42, 0.010), "NEXUS_Concrete_Dark", CS, 0.001, (0, 0, 0.5))

# Hanging work lamp.
pendant(f"{PREFIX}STORE_LAMP", -1.10, -6.60, -1.60, 0.95,
        95.0, (1.0, 0.72, 0.38))

# Fire extinguisher by the door.
rod(f"{PREFIX}STORE_EXTINGUISHER_BODY", (3.55, -2.50, -5.55),
    (3.55, -2.50, -4.75), 0.10, "NEXUS_Red", CP, 14)
rod(f"{PREFIX}STORE_EXTINGUISHER_TOP", (3.55, -2.50, -4.75),
    (3.55, -2.50, -4.64), 0.055, "NEXUS_Steel", CP)
box(f"{PREFIX}STORE_EXTINGUISHER_BRACKET", (3.55, -2.44, -4.75),
    (0.20, 0.05, 0.04), "NEXUS_Steel", CP, 0.004)

sign("NEXUS_V05_B_STORE_SIGN", "ALMACEN",
     (-2.0, -1.84, -2.93), (0, -1, 0), 0.145)
sign("NEXUS_V05_B_STORE_NOTICE", "NO BLOQUEAR",
     (-8.00, -6.30, -3.05), (1, 0, 0), 0.080)
area_light(f"{PREFIX}STORE_LIGHT_A", (-4.50, -5.80, -1.76),
           190.0, (0.78, 0.88, 1.0), 2.2, 0.25)
area_light(f"{PREFIX}STORE_LIGHT_B", (0.70, -4.40, -1.76),
           170.0, (0.82, 0.90, 1.0), 2.0, 0.25)


# ============================================================ MANTENIMIENTO ==
# Workbench along the west wall.
box(f"{PREFIX}MAINT_BENCH_TOP", (6.55, -6.40, -4.80),
    (0.85, 3.80, 0.10), "NEXUS_Wood", CP, 0.015)
for i, (x, y) in enumerate(((6.25, -8.10), (6.85, -8.10),
                             (6.25, -4.70), (6.85, -4.70))):
    box(f"{PREFIX}MAINT_BENCH_LEG_{i}", (x, y, -5.20),
        (0.08, 0.08, 0.90), "NEXUS_Painted_Metal", CP, 0.004)
box(f"{PREFIX}MAINT_BENCH_SHELF", (6.55, -6.40, -5.35),
    (0.70, 3.55, 0.05), "NEXUS_Steel", CP, 0.006)

# Pegboard and tools.
box(f"{PREFIX}MAINT_PEGBOARD", (6.16, -6.40, -3.65),
    (0.035, 3.40, 1.20), "NEXUS_Debris", CS, 0.006)
for i in range(8):
    box(f"{PREFIX}MAINT_PEG_HOLE_{i}", (6.185, -7.55 + i * 0.24, -3.65),
        (0.008, 0.025, 0.025), "NEXUS_Concrete_Dark", CS, 0.001)
rod(f"{PREFIX}MAINT_WRENCH", (6.20, -7.80, -3.55),
    (6.20, -7.80, -3.10), 0.018, "NEXUS_Steel", CP)
rod(f"{PREFIX}MAINT_HAMMER_HANDLE", (6.20, -7.05, -3.45),
    (6.20, -7.05, -2.98), 0.020, "NEXUS_Wood", CP)
box(f"{PREFIX}MAINT_HAMMER_HEAD", (6.20, -7.05, -2.96),
    (0.08, 0.30, 0.09), "NEXUS_Steel", CP, 0.006)
for i, y in enumerate((-6.35, -6.05, -5.75)):
    rod(f"{PREFIX}MAINT_SCREWDRIVER_{i}", (6.20, y, -3.22),
        (6.20, y, -2.90), 0.012, "NEXUS_Steel", CP)
    box(f"{PREFIX}MAINT_SCREWDRIVER_{i}_HANDLE", (6.20, y, -3.25),
        (0.05, 0.05, 0.11), "NEXUS_Amber", CP, 0.004)

# Toolbox, vise, rags and parts on the bench.
box(f"{PREFIX}MAINT_TOOLBOX", (6.55, -7.55, -4.61),
    (0.45, 0.70, 0.28), "NEXUS_Red", CP, 0.012)
rod(f"{PREFIX}MAINT_TOOLBOX_HANDLE", (6.55, -7.55, -4.44),
    (6.55, -7.55, -4.35), 0.035, "NEXUS_Steel", CP)
box(f"{PREFIX}MAINT_VISE_BASE", (6.68, -5.10, -4.66),
    (0.30, 0.30, 0.16), "NEXUS_Steel", CP, 0.008)
box(f"{PREFIX}MAINT_VISE_JAW", (6.68, -5.10, -4.53),
    (0.34, 0.22, 0.12), "NEXUS_Steel", CP, 0.006)
for i, (y, w) in enumerate(((-6.75, 0.30), (-5.70, 0.22))):
    box(f"{PREFIX}MAINT_RAG_{i}", (6.55, y, -4.735),
        (0.34, w, 0.03), "NEXUS_OffWhite", CP, 0.005)
for i in range(6):
    disk(f"{PREFIX}MAINT_BOLT_{i}", (6.48 + (i % 3) * 0.10, -6.10,
                                     -4.735), 0.035, 0.025,
         "NEXUS_Steel", CP)

# Tool chest against the south wall.
box(f"{PREFIX}MAINT_CHEST", (6.60, -9.15, -4.80),
    (0.80, 0.60, 1.70), "NEXUS_Painted_Metal", CP, 0.015)
for i, z in enumerate((-5.42, -5.00, -4.58, -4.16)):
    box(f"{PREFIX}MAINT_CHEST_DRAWER_{i}", (6.60, -8.84, z),
        (0.72, 0.035, 0.34), "NEXUS_Steel", CP, 0.004)
    box(f"{PREFIX}MAINT_CHEST_HANDLE_{i}", (6.60, -8.815, z + 0.05),
        (0.28, 0.03, 0.035), "NEXUS_Painted_Metal", CP, 0.003)

# Generator detail: exhaust, ribs, fan and warning label.
rod(f"{PREFIX}MAINT_EXHAUST", (13.0, -8.0, -3.20),
    (13.0, -8.0, -0.90), 0.09, "NEXUS_Rusted_Metal", CP)
for i, x in enumerate((11.75, 12.35, 13.65, 14.25)):
    box(f"{PREFIX}MAINT_GEN_RIB_{i}", (x, -6.87, -4.40),
        (0.08, 0.04, 1.80), "NEXUS_Painted_Metal", CP, 0.004)
disk(f"{PREFIX}MAINT_GEN_FAN", (11.70, -6.87, -4.50),
     0.42, 0.05, "NEXUS_Concrete_Dark", CP, "Y")
for i in range(3):
    box(f"{PREFIX}MAINT_GEN_GRILLE_{i}", (11.70, -6.92, -4.50 + (i - 1) * 0.18),
        (0.72, 0.02, 0.035), "NEXUS_Steel", CP, 0.002)
sign("NEXUS_V05_B_MAINT_ALTA", "ALTA TENSION",
     (13.0, -6.85, -3.55), (0, 1, 0), 0.075)

# Boiler / pressure vessel.
box(f"{PREFIX}MAINT_BOILER_BASE", (17.30, -8.20, -5.55),
    (2.00, 1.80, 0.20), "NEXUS_Concrete_Dark", CP, 0.01)
rod(f"{PREFIX}MAINT_BOILER_BODY", (17.30, -8.20, -5.45),
    (17.30, -8.20, -3.30), 0.85, "NEXUS_Rusted_Metal", CP, 24)
for i, z in enumerate((-5.00, -4.32, -3.62)):
    disk(f"{PREFIX}MAINT_BOILER_BAND_{i}", (17.30, -8.20, z),
         0.88, 0.07, "NEXUS_Steel", CP)
disk(f"{PREFIX}MAINT_BOILER_TOP", (17.30, -8.20, -3.26),
     0.86, 0.08, "NEXUS_Steel", CP)
disk(f"{PREFIX}MAINT_BOILER_GAUGE", (17.30, -7.32, -4.20),
     0.13, 0.06, "NEXUS_Steel", CP, "Y")
disk(f"{PREFIX}MAINT_BOILER_GAUGE_FACE", (17.30, -7.28, -4.20),
     0.105, 0.012, "NEXUS_OffWhite", CP, "Y")
box(f"{PREFIX}MAINT_BOILER_NEEDLE", (17.30, -7.27, -4.20),
    (0.012, 0.006, 0.075), "NEXUS_Red", CP, 0.001, (0, 0.5, 0))
rod(f"{PREFIX}MAINT_BOILER_PIPE_A", (17.00, -8.20, -3.20),
    (17.00, -8.20, -0.90), 0.07, "NEXUS_Steel", CP)
rod(f"{PREFIX}MAINT_BOILER_PIPE_B", (17.60, -8.20, -3.20),
    (17.60, -8.20, -1.90), 0.07, "NEXUS_Steel", CP)
rod(f"{PREFIX}MAINT_BOILER_PIPE_C", (17.60, -8.20, -1.90),
    (19.30, -8.20, -1.90), 0.07, "NEXUS_Steel", CP)
disk(f"{PREFIX}MAINT_BOILER_VALVE", (17.00, -8.20, -2.05),
     0.18, 0.05, "NEXUS_Red", CP)

# Oil spill.
o = rod(f"{PREFIX}MAINT_OIL", (15.90, -6.10, F + 0.004),
        (15.90, -6.10, F + 0.016), 1.05, "NEXUS_Oil", CT, 28)
if o:
    o.scale.x = 1.45
o = rod(f"{PREFIX}MAINT_OIL_2", (15.10, -5.15, F + 0.004),
        (15.10, -5.15, F + 0.014), 0.52, "NEXUS_Oil", CT, 24)
if o:
    o.scale.x = 1.20

# Hazard border around the generator.
box(f"{PREFIX}MAINT_HAZ_FRONT", (13.0, -6.65, F + 0.014),
    (3.6, 0.10, 0.012), "NEXUS_Amber", CS, 0.002)
box(f"{PREFIX}MAINT_HAZ_BACK", (13.0, -9.35, F + 0.014),
    (3.6, 0.10, 0.012), "NEXUS_Amber", CS, 0.002)
box(f"{PREFIX}MAINT_HAZ_W", (11.20, -8.0, F + 0.014),
    (0.10, 2.7, 0.012), "NEXUS_Amber", CS, 0.002)
box(f"{PREFIX}MAINT_HAZ_E", (14.80, -8.0, F + 0.014),
    (0.10, 2.7, 0.012), "NEXUS_Amber", CS, 0.002)

# Vertical pipes, clamps and valves along the east wall.
for i, y in enumerate((-9.05, -8.35)):
    rod(f"{PREFIX}MAINT_PIPE_E_{i}", (19.58, y, F),
        (19.58, y, -0.90), 0.08, "NEXUS_Rusted_Metal", CP)
    for j, z in enumerate((-4.60, -3.10, -1.60)):
        box(f"{PREFIX}MAINT_PIPE_CLAMP_{i}_{j}", (19.58, y, z),
            (0.28, 0.14, 0.08), "NEXUS_Steel", CP, 0.004)
disk(f"{PREFIX}MAINT_PIPE_VALVE", (19.58, -8.70, -3.80),
     0.19, 0.05, "NEXUS_Red", CP)

# Ladder.
for i, y in enumerate((-4.48, -3.92)):
    rod(f"{PREFIX}MAINT_LADDER_RAIL_{i}", (19.42, y, F),
        (19.42, y, -2.25), 0.035, "NEXUS_Steel", CP)
for i in range(8):
    rod(f"{PREFIX}MAINT_LADDER_RUNG_{i}",
        (19.42, -4.48, -5.35 + i * 0.40),
        (19.42, -3.92, -5.35 + i * 0.40), 0.026,
        "NEXUS_Steel", CP)

# Gas cylinders by the east wall.
for i, (y, matname) in enumerate(((-2.80, "NEXUS_Red"),
                                   (-3.45, "NEXUS_Green"))):
    rod(f"{PREFIX}MAINT_CYLINDER_{i}", (19.20, y, F),
        (19.20, y, F + 1.20), 0.22, matname, CP, 18)
    disk(f"{PREFIX}MAINT_CYLINDER_{i}_TOP", (19.20, y, F + 1.22),
         0.20, 0.06, "NEXUS_Steel", CP)
    rod(f"{PREFIX}MAINT_CYLINDER_{i}_VALVE", (19.20, y, F + 1.24),
        (19.20, y, F + 1.38), 0.045, "NEXUS_Steel", CP)

# Electrical cabinet, first-aid kit and extinguisher.
box(f"{PREFIX}MAINT_CABINET", (6.20, -3.05, -3.90),
    (0.25, 1.10, 1.60), "NEXUS_Painted_Metal", CS, 0.01)
box(f"{PREFIX}MAINT_CABINET_DOOR", (6.34, -3.05, -3.90),
    (0.03, 1.00, 1.45), "NEXUS_Steel", CS, 0.006)
for i in range(3):
    disk(f"{PREFIX}MAINT_CABINET_LED_{i}", (6.36, -3.35 + i * 0.28, -3.55),
         0.035, 0.012, "NEXUS_Red" if i == 0 else "NEXUS_Green", CP, "X")
box(f"{PREFIX}MAINT_FIRST_AID", (6.17, -4.25, -3.55),
    (0.10, 0.45, 0.45), "NEXUS_OffWhite", CS, 0.008)
box(f"{PREFIX}MAINT_FIRST_AID_CROSS_V", (6.11, -4.25, -3.55),
    (0.015, 0.08, 0.26), "NEXUS_Red", CS, 0.001)
box(f"{PREFIX}MAINT_FIRST_AID_CROSS_H", (6.11, -4.25, -3.55),
    (0.015, 0.26, 0.08), "NEXUS_Red", CS, 0.001)
rod(f"{PREFIX}MAINT_EXTINGUISHER", (19.45, -2.15, -5.55),
    (19.45, -2.15, -4.70), 0.10, "NEXUS_Red", CP, 14)
rod(f"{PREFIX}MAINT_EXTINGUISHER_TOP", (19.45, -2.15, -4.70),
    (19.45, -2.15, -4.58), 0.055, "NEXUS_Steel", CP)

# Crates and spare parts near the boiler.
crate(f"{PREFIX}MAINT_CRATE_0", (18.55, -6.55, -5.35),
      (0.70, 0.55, 0.60), "NEXUS_Debris", True)
crate(f"{PREFIX}MAINT_CRATE_1", (18.55, -5.85, -5.45),
      (0.55, 0.45, 0.40), "NEXUS_Rusted_Metal", False)
barrel(f"{PREFIX}MAINT_BARREL", (18.55, -5.05, F), 0.28, 0.85,
       "NEXUS_Rusted_Metal")

# Pendant lights, red emergency light and bench task light.
pendant(f"{PREFIX}MAINT_LAMP_A", 9.50, -5.00, -0.80, 1.00,
        110.0, (1.0, 0.72, 0.38))
pendant(f"{PREFIX}MAINT_LAMP_B", 17.00, -4.50, -0.80, 1.00,
        110.0, (1.0, 0.72, 0.38))
area_light(f"{PREFIX}MAINT_BENCH_LIGHT", (6.80, -6.40, -2.80),
           140.0, (0.88, 0.92, 1.0), 1.2, 0.25)
point_light(f"{PREFIX}MAINT_EMERGENCY", (13.0, -2.10, -1.30),
            45.0, (1.0, 0.04, 0.02), 0.20)
box(f"{PREFIX}MAINT_EMERGENCY_HOUSING", (13.0, -2.10, -1.30),
    (0.35, 0.14, 0.14), "NEXUS_Painted_Metal", CS, 0.006)
disk(f"{PREFIX}MAINT_FLOOR_DRAIN", (13.0, -5.60, -5.645),
     0.20, 0.012, "NEXUS_Steel", CP)

sign("NEXUS_V05_B_MAINT_SIGN", "MANTENIMIENTO",
     (13.0, -1.84, -2.93), (0, -1, 0), 0.135)
sign("NEXUS_V05_B_MAINT_MACHINE", "SALA DE MAQUINAS",
     (20.00 - 0.14, -6.60, -3.55), (-1, 0, 0), 0.085)

# Ceiling pipe flanges.
for i, x in enumerate((8.0, 11.0, 14.0, 17.0, 19.0)):
    for j, y in enumerate((-9.0, -6.0)):
        disk(f"{PREFIX}MAINT_PIPE_FLANGE_{i}_{j}", (x, y, -2.20),
             0.14, 0.06, "NEXUS_Steel", CP)

# Save.
bpy.context.scene.camera = bpy.data.objects.get("NEXUS_V05_CAM_Recepcion")
bpy.context.scene.view_settings.exposure = 1.5
path = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V05_level1_v13.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
print("LEVEL1_B_SAVED", path, os.path.getsize(path))
