import bpy
import math
import os
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
OUT_BLEND = ROOT + "/blender_concept/LEVEL1_DRESSING.blend"
OUT_GLB = ROOT + "/assets/models/fm/art3a2/level1_dressing.glb"
os.makedirs(os.path.dirname(OUT_GLB), exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0

COLL = bpy.data.collections.new("LEVEL1_DRESSING")
scene.collection.children.link(COLL)

OBJS = []

# ------------------------------------------------------------------ materials
TEX = ROOT + "/assets/texturas/"
GEN = ROOT + "/assets/art/fm/generated/"


def load_img(path, non_color=False):
    img = bpy.data.images.load(path, check_existing=True)
    if non_color:
        img.colorspace_settings.name = 'Non-Color'
    return img


def tex_mat(name, diff, normal, rough, metallic, base=(1, 1, 1, 1), normal_strength=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = base
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = 1.0
    if diff:
        t = nt.nodes.new('ShaderNodeTexImage')
        t.image = load_img(diff)
        t.location = (-700, 300)
        nt.links.new(t.outputs['Color'], bsdf.inputs['Base Color'])
    if rough:
        t = nt.nodes.new('ShaderNodeTexImage')
        t.image = load_img(rough, True)
        t.location = (-700, 0)
        nt.links.new(t.outputs['Color'], bsdf.inputs['Roughness'])
    if normal:
        t = nt.nodes.new('ShaderNodeTexImage')
        t.image = load_img(normal, True)
        t.location = (-700, -300)
        nm = nt.nodes.new('ShaderNodeNormalMap')
        nm.inputs['Strength'].default_value = normal_strength
        nm.location = (-350, -300)
        nt.links.new(t.outputs['Color'], nm.inputs['Color'])
        nt.links.new(nm.outputs['Normal'], bsdf.inputs['Normal'])
    return mat


def solid_mat(name, color, metallic, roughness, emission=None, emission_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    if emission:
        bsdf.inputs['Emission Color'].default_value = (*emission, 1.0)
        bsdf.inputs['Emission Strength'].default_value = emission_strength
    return mat


MAT_STEEL = tex_mat("ART3A1_Steel", TEX + "Metal y oxidacion/rusty_metal_sheet_2k.blend/textures/rusty_metal_sheet_diff_2k.jpg", GEN + "gen_rusty_metal_sheet_normal.png", GEN + "gen_rusty_metal_sheet_rough.png", 0.8, base=(0.65, 0.70, 0.76, 1))
MAT_GREEN = tex_mat("ART3A1_GreenPaint", TEX + "Metal y oxidacion/green_metal_rust_2k.blend/textures/green_metal_rust_diff_2k.jpg", GEN + "gen_green_metal_rust_normal.png", TEX + "Metal y oxidacion/green_metal_rust_2k.blend/textures/green_metal_rust_rough_2k.jpg", 0.08, base=(0.72, 0.86, 0.78, 1))
MAT_WALL = tex_mat("ART3A1_Wall", TEX + "Pintura y paredes/worn_plaster_wall_2k.blend/textures/worn_plaster_wall_diff_2k.jpg", GEN + "gen_worn_plaster_wall_normal.png", GEN + "gen_worn_plaster_wall_rough.png", 0.0, base=(0.55, 0.62, 0.68, 1))
MAT_CONCRETE = tex_mat("ART3A2_Concrete", TEX + "Hormigon y cemento/concrete_wall_003_2k.blend/textures/concrete_wall_003_diff_2k.jpg", GEN + "gen_concrete_wall_003_normal.png", TEX + "Hormigon y cemento/concrete_wall_003_2k.blend/textures/concrete_wall_003_rough_2k.jpg", 0.0, base=(0.55, 0.60, 0.65, 1))
MAT_DARK = solid_mat("ART3A1_DarkMetal", (0.035, 0.045, 0.050), 0.8, 0.52)
MAT_DUCT = solid_mat("ART3A1_DuctPaint", (0.045, 0.085, 0.070), 0.12, 0.72)
MAT_HAZARD = solid_mat("ART3A1_Hazard", (0.62, 0.34, 0.015), 0.0, 0.62)
MAT_LABEL = solid_mat("ART3A1_Label", (0.62, 0.65, 0.66), 0.0, 0.68)
MAT_CYAN = solid_mat("ART3A1_CyanStrip", (0.02, 0.10, 0.12), 0.0, 0.30, emission=(0.15, 0.70, 0.86), emission_strength=2.0)
MAT_BULB = solid_mat("ART3A2_Bulb", (0.9, 0.8, 0.6), 0.0, 0.3, emission=(1.0, 0.72, 0.42), emission_strength=5.0)
MAT_LENS = solid_mat("ART3A2_Lens", (0.35, 0.5, 0.55), 0.0, 0.15, emission=(0.55, 0.85, 1.0), emission_strength=2.2)
MAT_WOOD = tex_mat("ART3A2_Wood", ROOT + "/assets/Modelos 3D/Mobiliario y almacenamiento/wooden_crate_01_2k.blend/textures/wooden_crate_01_diff_2k.jpg", GEN + "gen_wooden_crate_01_normal.png", GEN + "gen_wooden_crate_01_rough.png", 0.0, base=(0.72, 0.60, 0.48, 1))
MAT_SCREEN = solid_mat("ART3A2_Screen", (0.01, 0.05, 0.06), 0.0, 0.25, emission=(0.06, 0.40, 0.48), emission_strength=0.55)

FLOOR = -5.65

# ------------------------------------------------------------------ helpers


def link(obj):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    COLL.objects.link(obj)


def apply_scale(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)


def finish(obj, mat, bevel=0.010, unwrap=True):
    link(obj)
    obj.data.materials.append(mat)
    if unwrap:
        if not obj.data.uv_layers:
            obj.data.uv_layers.new(name="UVMap")
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        try:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.smart_project(angle_limit=math.radians(65), island_margin=0.02)
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except Exception:
                pass
    if bevel > 0:
        m = obj.modifiers.new("Bevel", 'BEVEL')
        m.width = bevel
        m.segments = 2
        m.limit_method = 'ANGLE'
        m.angle_limit = math.radians(40)
        m.harden_normals = True
        n = obj.modifiers.new("Weighted", 'WEIGHTED_NORMAL')
        n.keep_sharp = True
    OBJS.append(obj)
    return obj


def gbox(name, gpos, gsize, mat, bevel=0.010, unwrap=True):
    """gpos/gsize in Godot coords (x right, y up, z south)."""
    bx, by, bz = gpos[0], -gpos[2], gpos[1]
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bx, by, bz))
    obj = bpy.context.active_object
    obj.name = name
    obj.dimensions = (gsize[0], gsize[2], gsize[1])
    apply_scale(obj)
    return finish(obj, mat, bevel, unwrap)


def gcyl_y(name, gpos, radius, height, mat, segments=20, bevel=0.0, unwrap=False):
    bx, by, bz = gpos[0], -gpos[2], gpos[1]
    bpy.ops.mesh.primitive_cylinder_add(vertices=segments, radius=radius, depth=height, location=(bx, by, bz))
    obj = bpy.context.active_object
    obj.name = name
    return finish(obj, mat, bevel, unwrap)


def gcyl_axis(name, gpos, radius, length, axis, mat, segments=16):
    """axis: 'x' or 'z' in Godot."""
    bx, by, bz = gpos[0], -gpos[2], gpos[1]
    rot = (0, math.pi / 2, 0) if axis == 'x' else (math.pi / 2, 0, 0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=segments, radius=radius, depth=length, location=(bx, by, bz), rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    return finish(obj, mat, 0.0, False)


def gsphere(name, gpos, radius, mat):
    bx, by, bz = gpos[0], -gpos[2], gpos[1]
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=radius, location=(bx, by, bz))
    obj = bpy.context.active_object
    obj.name = name
    return finish(obj, mat, 0.0, False)


def gcone_down(name, gpos, r_top, r_bottom, height, mat):
    bx, by, bz = gpos[0], -gpos[2], gpos[1]
    bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=r_bottom, radius2=r_top, depth=height, location=(bx, by, bz))
    obj = bpy.context.active_object
    obj.name = name
    return finish(obj, mat, 0.0, False)


def gring(name, gpos, major, minor, mat, axis='y'):
    bx, by, bz = gpos[0], -gpos[2], gpos[1]
    rot = (0, 0, 0)
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=24, minor_segments=6, location=(bx, by, bz), rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    return finish(obj, mat, 0.0, False)


# ------------------------------------------------------------------ wall ribs
# (axis, const, start, end, inward, doors_along)
WALLS = [
    ("z", -19.80, -11.40, -1.70, +1, [], -2.55),     # reception west (wainscot)
    ("z", -2.10, -9.45, -1.80, +1, [], -1.72),       # security west
    ("z", 7.80, -9.45, -1.80, -1, [], -1.72),        # security east
    ("z", 8.90, -9.50, -1.80, +1, [], -1.72),        # control west
    ("z", 14.90, -9.50, -1.80, -1, [], -1.72),       # control east
    ("z", -18.80, 1.90, 9.00, +1, [], -1.92),        # vest west
    ("z", -9.20, 1.90, 9.00, -1, [], -1.92),         # vest east
    ("x", 1.90, -18.80, -9.20, +1, [-14.86], -1.92), # vest corridor wall
    ("z", -7.80, 1.90, 9.50, +1, [], -1.72),         # storage west
    ("z", 2.10, 1.90, 9.50, -1, [], -1.72),          # storage east
    ("x", 1.90, -7.80, 2.10, +1, [-2.86], -1.72),    # storage corridor wall
    ("z", 6.20, 1.80, 9.80, +1, [], -0.92),          # maint west
    ("z", 18.30, 1.80, 9.80, -1, [], -0.92),         # maint east
    ("x", 1.80, 6.20, 18.30, +1, [12.14], -0.92),    # maint corridor wall
    ("x", -1.70, -22.00, 22.00, +1, [-12.86, 2.14, 12.14], -1.72),   # corridor north wall
    ("x", 1.70, -22.00, 22.00, -1, [-14.86, -2.86, 12.14], -1.72),   # corridor south wall
]

for wi, (axis, const, start, end, inward, doors, ceil) in enumerate(WALLS):
    wall_h = max(2.4, ceil - FLOOR - 0.24)
    wall_cy = (ceil + FLOOR) * 0.5 - 0.04
    length = end - start
    # free intervals for horizontal trim
    cuts = sorted(doors)
    segs = []
    cursor = start
    for d in cuts:
        if d - 1.25 > cursor:
            segs.append((cursor, d - 1.25))
        cursor = max(cursor, d + 1.25)
    if end > cursor:
        segs.append((cursor, end))
    # baseboard and mid seam per free segment
    for si, (a, b) in enumerate(segs):
        mid = (a + b) * 0.5
        seg_len = b - a
        if axis == "z":
            pos = (const + inward * 0.035, FLOOR + 0.09, mid)
            gsize = (0.055, 0.16, seg_len)
            seam = (const + inward * 0.045, FLOOR + 1.06, mid)
            ssize = (0.045, 0.035, seg_len)
        else:
            pos = (mid, FLOOR + 0.09, const + inward * 0.035)
            gsize = (seg_len, 0.16, 0.055)
            seam = (mid, FLOOR + 1.06, const + inward * 0.045)
            ssize = (seg_len, 0.035, 0.045)
        gbox("DRS_BASE_%d_%d" % (wi, si), pos, gsize, MAT_STEEL, 0.004, False)
        gbox("DRS_SEAM_%d_%d" % (wi, si), seam, ssize, MAT_STEEL, 0.004, False)
        cap_y = FLOOR + wall_h - 0.06
        if axis == "z":
            gbox("DRS_CAP_%d_%d" % (wi, si), (const + inward * 0.045, cap_y, mid), (0.045, 0.035, seg_len), MAT_STEEL, 0.004, False)
        else:
            gbox("DRS_CAP_%d_%d" % (wi, si), (mid, cap_y, const + inward * 0.045), (seg_len, 0.035, 0.045), MAT_STEEL, 0.004, False)
    # vertical ribs
    n = max(2, int(length / 0.92))
    for i in range(n + 1):
        along = start + 0.36 + i * (length - 0.72) / n
        if any(abs(along - d) < 1.25 for d in doors):
            continue
        if axis == "z":
            gpos = (const + inward * 0.030, wall_cy, along)
            gsize = (0.034, wall_h, 0.030)
        else:
            gpos = (along, wall_cy, const + inward * 0.030)
            gsize = (0.030, wall_h, 0.034)
        gbox("DRS_RIB_%d_%d" % (wi, i), gpos, gsize, MAT_STEEL, 0.006, False)
        # small mounting plates
        for yy in (FLOOR + 0.30, ceil - 0.38):
            if axis == "z":
                gbox("DRS_PLATE_%d_%d_%d" % (wi, i, int(yy * 10)), (const + inward * 0.030, yy, along), (0.020, 0.14, 0.14), MAT_DARK, 0.003, False)
            else:
                gbox("DRS_PLATE_%d_%d_%d" % (wi, i, int(yy * 10)), (along, yy, const + inward * 0.030), (0.14, 0.14, 0.020), MAT_DARK, 0.003, False)
    # occasional service box on long walls
    for i in range(2, n, 6):
        along = start + 0.36 + i * (length - 0.72) / n
        if any(abs(along - d) < 1.5 for d in doors):
            continue
        if axis == "z":
            gbox("DRS_BOX_%d_%d" % (wi, i), (const + inward * 0.12, FLOOR + 2.35, along), (0.20, 0.42, 0.30), MAT_DARK, 0.006, False)
            gbox("DRS_BOX_DOOR_%d_%d" % (wi, i), (const + inward * 0.23, FLOOR + 2.35, along), (0.025, 0.34, 0.23), MAT_GREEN, 0.004, False)
            gbox("DRS_BOX_LABEL_%d_%d" % (wi, i), (const + inward * 0.245, FLOOR + 2.52, along), (0.010, 0.07, 0.12), MAT_HAZARD, 0.002, False)
        else:
            gbox("DRS_BOX_%d_%d" % (wi, i), (along, FLOOR + 2.35, const + inward * 0.12), (0.30, 0.42, 0.20), MAT_DARK, 0.006, False)
            gbox("DRS_BOX_DOOR_%d_%d" % (wi, i), (along, FLOOR + 2.35, const + inward * 0.23), (0.23, 0.34, 0.025), MAT_GREEN, 0.004, False)
            gbox("DRS_BOX_LABEL_%d_%d" % (wi, i), (along, FLOOR + 2.52, const + inward * 0.245), (0.12, 0.07, 0.010), MAT_HAZARD, 0.002, False)

# ------------------------------------------------------------------ ceiling beams
ROOMS = [
    ("SEG", -2.10, 7.80, -9.45, -1.80, -1.72),
    ("CTL", 8.90, 14.90, -9.50, -1.80, -1.72),
    ("VEST", -18.80, -9.20, 1.90, 9.00, -1.92),
    ("ALM", -7.80, 2.10, 1.90, 9.50, -1.72),
    ("MANT", 6.20, 18.30, 1.80, 9.80, -0.92),
    ("REC", -19.80, -4.60, -11.40, -1.70, 0.08),
]

for name, x0, x1, z0, z1, ceil in ROOMS:
    w = x1 - x0
    d = z1 - z0
    by = ceil - 0.20
    if w <= d:
        # beams across x, stepping z
        count = max(1, int(d / 3.2))
        for i in range(count + 1):
            z = z0 + 0.9 + i * max(0.1, (d - 1.8) / max(1, count))
            gbox("DRS_BEAM_%s_%d_B" % (name, i), ((x0 + x1) * 0.5, by, z), (w - 0.20, 0.020, 0.16), MAT_STEEL, 0.004, False)
            gbox("DRS_BEAM_%s_%d_W" % (name, i), ((x0 + x1) * 0.5, by + 0.10, z), (w - 0.20, 0.20, 0.030), MAT_STEEL, 0.004, False)
            gbox("DRS_BEAM_%s_%d_T" % (name, i), ((x0 + x1) * 0.5, by + 0.21, z), (w - 0.20, 0.020, 0.16), MAT_STEEL, 0.004, False)
            for sx in (x0 + 0.25, x1 - 0.25):
                gbox("DRS_BEAM_%s_%d_BR_%s" % (name, i, int(sx * 10)), (sx, by + 0.06, z), (0.22, 0.12, 0.22), MAT_DARK, 0.004, False)
    else:
        count = max(1, int(w / 3.2))
        for i in range(count + 1):
            x = x0 + 0.9 + i * max(0.1, (w - 1.8) / max(1, count))
            gbox("DRS_BEAM_%s_%d_B" % (name, i), (x, by, (z0 + z1) * 0.5), (0.16, 0.020, d - 0.20), MAT_STEEL, 0.004, False)
            gbox("DRS_BEAM_%s_%d_W" % (name, i), (x, by + 0.10, (z0 + z1) * 0.5), (0.030, 0.20, d - 0.20), MAT_STEEL, 0.004, False)
            gbox("DRS_BEAM_%s_%d_T" % (name, i), (x, by + 0.21, (z0 + z1) * 0.5), (0.16, 0.020, d - 0.20), MAT_STEEL, 0.004, False)
            for sz in (z0 + 0.25, z1 - 0.25):
                gbox("DRS_BEAM_%s_%d_BR_%s" % (name, i, int(sz * 10)), (x, by + 0.06, sz), (0.22, 0.12, 0.22), MAT_DARK, 0.004, False)

# corridor beams
for i in range(11):
    x = -20.0 + i * 4.0
    gbox("DRS_BEAM_CORR_%d_B" % i, (x, -1.92, 0.0), (0.16, 0.020, 3.20), MAT_STEEL, 0.004, False)
    gbox("DRS_BEAM_CORR_%d_W" % i, (x, -1.82, 0.0), (0.030, 0.20, 3.20), MAT_STEEL, 0.004, False)
    gbox("DRS_BEAM_CORR_%d_T" % i, (x, -1.71, 0.0), (0.16, 0.020, 3.20), MAT_STEEL, 0.004, False)

# ------------------------------------------------------------------ ducts
DUCTS = [
    ("SEG", 0.0, -5.6, -9.2, 7.6, -1.72),
    ("CTL", 11.9, -5.6, -9.2, 7.6, -1.72),
    ("ALM", -2.8, 5.6, -7.6, 2.0, -1.72),
    ("MANT", 12.2, 5.6, 6.4, 18.1, -0.92),
]
for name, cx, cy, a0, a1, ceil in DUCTS:
    length = a1 - a0
    mid = (a0 + a1) * 0.5
    gbox("DRS_DUCT_%s" % name, (cx, ceil - 0.42, mid), (0.46, 0.30, length), MAT_DUCT, 0.012, True)
    flanges = max(2, int(length / 2.4))
    for i in range(flanges + 1):
        p = a0 + 0.15 + i * (length - 0.3) / flanges
        gbox("DRS_DUCT_FL_%s_%d" % (name, i), (cx, ceil - 0.42, p), (0.54, 0.36, 0.045), MAT_STEEL, 0.004, False)
    for i in range(flanges):
        p = a0 + 0.15 + (i + 0.5) * (length - 0.3) / flanges
        gbox("DRS_DUCT_GRILLE_%s_%d" % (name, i), (cx, ceil - 0.60, p), (0.30, 0.025, 0.34), MAT_DARK, 0.004, False)
        for j in range(4):
            gbox("DRS_DUCT_GSLAT_%s_%d_%d" % (name, i, j), (cx, ceil - 0.62, p - 0.12 + j * 0.08), (0.26, 0.010, 0.020), MAT_STEEL, 0.002, False)
    for i in range(max(2, int(length / 3.0)) + 1):
        p = a0 + 0.5 + i * (length - 1.0) / max(1, int(length / 3.0))
        gbox("DRS_DUCT_HANG_%s_%d" % (name, i), (cx, ceil - 0.20, p), (0.04, 0.22, 0.04), MAT_STEEL, 0.0, False)
        gbox("DRS_DUCT_HBR_%s_%d" % (name, i), (cx, ceil - 0.12, p), (0.30, 0.05, 0.06), MAT_STEEL, 0.003, False)

# ------------------------------------------------------------------ caged pendants
PENDANTS = [
    ("SEG", 3.0, -6.0, -1.72, (1.0, 0.52, 0.24)),
    ("CTL", 13.0, -6.0, -1.72, (0.82, 0.90, 1.0)),
    ("VEST", -14.0, 4.6, -1.92, (1.0, 0.58, 0.30)),
    ("ALM", -2.0, 5.3, -1.72, (1.0, 0.52, 0.24)),
    ("MANT", 13.0, 5.6, -0.92, (1.0, 0.55, 0.28)),
    ("MANT", 10.0, 7.6, -0.92, (0.75, 0.88, 1.0)),
]
for name, x, z, ceil, col in PENDANTS:
    ly = ceil - 0.62
    gcyl_y("DRS_PEND_ROD_%s_%s_%s" % (name, int(x * 10), int(z * 10)), (x, (ceil + ly) * 0.5, z), 0.012, ceil - ly, MAT_DARK, 10)
    gbox("DRS_PEND_MOUNT_%s_%s_%s" % (name, int(x * 10), int(z * 10)), (x, ceil - 0.02, z), (0.16, 0.04, 0.16), MAT_DARK, 0.004, False)
    gcone_down("DRS_PEND_SHADE_%s_%s_%s" % (name, int(x * 10), int(z * 10)), (x, ly + 0.06, z), 0.065, 0.20, 0.14, MAT_DARK)
    gring("DRS_PEND_RING_%s_%s_%s" % (name, int(x * 10), int(z * 10)), (x, ly - 0.03, z), 0.155, 0.006, MAT_STEEL)
    gring("DRS_PEND_RING2_%s_%s_%s" % (name, int(x * 10), int(z * 10)), (x, ly - 0.17, z), 0.11, 0.005, MAT_STEEL)
    for b in range(6):
        ang = b * math.pi / 3.0
        bx = x + math.cos(ang) * 0.135
        bz = z + math.sin(ang) * 0.135
        gcyl_y("DRS_PEND_BAR_%s_%s_%s_%d" % (name, int(x * 10), int(z * 10), b), (bx, ly - 0.10, bz), 0.005, 0.22, MAT_STEEL, 6)
    gsphere("DRS_PEND_BULB_%s_%s_%s" % (name, int(x * 10), int(z * 10)), (x, ly - 0.09, z), 0.048, MAT_BULB)
    gcyl_y("DRS_PEND_SOCKET_%s_%s_%s" % (name, int(x * 10), int(z * 10)), (x, ly - 0.01, z), 0.030, 0.06, MAT_DARK, 12)

# ------------------------------------------------------------------ office/rest detail
# Aseo mirror frame and shelf (mirror at x -6.25, z -4.58).
gbox("DRS_MIRROR_TOP", (-6.55, -3.62, -4.58), (1.20, 0.06, 0.08), MAT_DARK, 0.004, False)
gbox("DRS_MIRROR_BOT", (-6.55, -4.70, -4.58), (1.20, 0.06, 0.08), MAT_DARK, 0.004, False)
gbox("DRS_MIRROR_L", (-7.13, -4.16, -4.58), (0.08, 1.02, 0.08), MAT_DARK, 0.004, False)
gbox("DRS_MIRROR_R", (-5.97, -4.16, -4.58), (0.08, 1.02, 0.08), MAT_DARK, 0.004, False)
gbox("DRS_REST_SHELF", (-6.55, -4.86, -4.42), (0.95, 0.05, 0.24), MAT_DARK, 0.004, False)
gbox("DRS_REST_SOAP", (-6.80, -4.72, -4.42), (0.09, 0.20, 0.09), MAT_LABEL, 0.004, False)
gbox("DRS_REST_TOWEL", (-6.30, -4.83, -4.40), (0.28, 0.08, 0.16), MAT_LABEL, 0.004, False)
# Office shelf and desk return.
gbox("DRS_OFFICE_SHELF", (-7.60, -3.10, -6.90), (0.32, 1.80, 1.10), MAT_DARK, 0.008, False)
for i in range(4):
    gbox("DRS_OFFICE_SHELF_BOARD_%d" % i, (-7.42, -4.85 + i * 0.48, -6.90), (0.24, 0.04, 1.02), MAT_STEEL, 0.004, False)
gbox("DRS_OFFICE_CAB", (-5.20, -4.80, -6.75), (0.70, 0.90, 0.120), MAT_GREEN, 0.006, False)
for i in range(2):
    gbox("DRS_OFFICE_CAB_DOOR_%d" % i, (-5.20, -4.80, -6.68), (0.30, 0.78, 0.025), MAT_GREEN, 0.004, False)
    gbox("DRS_OFFICE_CAB_HANDLE_%d" % i, (-5.20 + (-0.09 if i == 0 else 0.09), -4.80, -6.655), (0.02, 0.14, 0.02), MAT_STEEL, 0.002, False)

# ------------------------------------------------------------------ hazard labels on doors
DOOR_LABELS = [
    ("SEG", 2.14, -1.72, "z"),
    ("CTL", 12.14, -1.72, "z"),
    ("VEST", -14.86, 1.72, "z"),
    ("ALM", -2.86, 1.72, "z"),
    ("MANT", 12.14, 1.72, "z"),
]
for name, x, z, axis in DOOR_LABELS:
    gbox("DRS_DOOR_LABEL_%s" % name, (x, -3.32, z + (-0.08 if z < 0 else 0.08)), (0.62, 0.16, 0.012), MAT_HAZARD, 0.002, False)


# ------------------------------------------------------------------ recepción: panel de directorio
gbox("DRS_REC_DIR_PANEL", (-19.70, -3.20, -6.20), (0.06, 1.15, 3.10), MAT_DARK, 0.006, False)
gbox("DRS_REC_DIR_TOP", (-19.66, -2.62, -6.20), (0.04, 0.06, 3.18), MAT_STEEL, 0.003, False)
gbox("DRS_REC_DIR_BOT", (-19.66, -3.78, -6.20), (0.04, 0.06, 3.18), MAT_STEEL, 0.003, False)
gbox("DRS_REC_DIR_L", (-19.66, -3.20, -7.74), (0.04, 1.22, 0.06), MAT_STEEL, 0.003, False)
gbox("DRS_REC_DIR_R", (-19.66, -3.20, -4.66), (0.04, 1.22, 0.06), MAT_STEEL, 0.003, False)
gbox("DRS_REC_DIR_HEAD", (-19.63, -2.72, -6.20), (0.03, 0.16, 2.90), MAT_CYAN, 0.002, False)
for i in range(3):
    for j in range(2):
        gbox("DRS_REC_DIR_TILE_%d_%d" % (i, j), (-19.65, -3.06 - j * 0.40, -7.05 + i * 0.85), (0.03, 0.28, 0.70), MAT_GREEN, 0.003, False)
        gbox("DRS_REC_DIR_LABEL_%d_%d" % (i, j), (-19.62, -3.22 - j * 0.40, -7.05 + i * 0.85), (0.01, 0.04, 0.42), MAT_LABEL, 0.001, False)

# ------------------------------------------------------------------ control: consola y rack
gbox("DRS_CTL_DESK_TOP", (9.45, -4.74, -6.0), (0.80, 0.07, 2.40), MAT_DARK, 0.006, False)
for z in (-4.95, -7.05):
    for x in (9.15, 9.72):
        gbox("DRS_CTL_DESK_LEG_%d_%d" % (int(x*10), int(z*10)), (x, -5.20, z), (0.06, 0.92, 0.06), MAT_STEEL, 0.004, False)
gbox("DRS_CTL_DESK_KICK", (9.45, -5.45, -6.0), (0.72, 0.12, 2.30), MAT_DARK, 0.004, False)
gbox("DRS_CTL_CABLE", (9.62, -4.88, -6.0), (0.30, 0.08, 1.90), MAT_STEEL, 0.003, False)
for i, z in enumerate((-6.62, -5.38)):
    gbox("DRS_CTL_MON_BEZEL_%d" % i, (9.55, -4.20, z), (0.06, 0.56, 0.82), MAT_DARK, 0.004, False)
    gbox("DRS_CTL_MON_SCREEN_%d" % i, (9.59, -4.20, z), (0.02, 0.46, 0.70), MAT_SCREEN, 0.002, False)
    gbox("DRS_CTL_MON_STAND_%d" % i, (9.55, -4.58, z), (0.10, 0.18, 0.16), MAT_DARK, 0.003, False)
    for k in range(3):
        gbox("DRS_CTL_MON_UI_%d_%d" % (i, k), (9.605, -4.34 + k * 0.11, z), (0.004, 0.028, 0.46), MAT_DARK, 0.001, False)
    gbox("DRS_CTL_MON_UI_SIDE_%d" % i, (9.605, -4.20, z + 0.25), (0.004, 0.30, 0.06), MAT_DARK, 0.001, False)
gbox("DRS_CTL_KEYBOARD", (9.28, -4.70, -6.0), (0.24, 0.025, 0.62), MAT_DARK, 0.003, False)
gbox("DRS_CTL_BOARD", (8.96, -2.75, -6.0), (0.06, 1.10, 2.20), MAT_DARK, 0.006, False)
for k in range(4):
    gbox("DRS_CTL_BOARD_TILE_%d" % k, (8.93, -2.72, -6.80 + k * 0.54), (0.02, 0.66, 0.42), MAT_GREEN, 0.003, False)
    gbox("DRS_CTL_BOARD_BAR_%d" % k, (8.91, -3.06, -6.80 + k * 0.54), (0.01, 0.04, 0.34), MAT_CYAN, 0.001, False)

# ------------------------------------------------------------------ rack técnico en seguridad y control
for name, x, z in (("SEG", 7.55, -8.95), ("CTL", 14.45, -8.95)):
    gbox("DRS_RACK_%s_BODY" % name, (x, -4.70, z), (0.55, 1.80, 0.80), MAT_DARK, 0.008, False)
    gbox("DRS_RACK_%s_FRONT" % name, (x - 0.29, -4.70, z), (0.03, 1.62, 0.68), MAT_GREEN, 0.004, False)
    for k in range(6):
        gbox("DRS_RACK_%s_LED_%d" % (name, k), (x - 0.31, -3.95 - k * 0.20, z + 0.22), (0.01, 0.035, 0.035), MAT_CYAN, 0.001, False)
    for k in range(3):
        gbox("DRS_RACK_%s_VENT_%d" % (name, k), (x - 0.31, -5.15, z - 0.18 + k * 0.12), (0.01, 0.03, 0.30), MAT_STEEL, 0.001, False)

# ------------------------------------------------------------------ vestuarios: listones de banco
for label, x in (("W", -15.70), ("E", -12.30)):
    for k in range(5):
        gbox("DRS_VEST_SLAT_%s_%d" % (label, k), (x, -5.325, 5.66 + k * 0.07), (2.00, 0.035, 0.055), MAT_WOOD, 0.003, False)

# ------------------------------------------------------------------ corredor: rejillas de pared
for side, z, inward in (("N", -1.66, +1), ("S", 1.66, -1)):
    for i, x in enumerate((-18.0, -6.0, 6.0, 18.0)):
        gbox("DRS_CORR_VENT_%s_%d_FRAME" % (side, i), (x, -3.30, z + inward * 0.02), (0.92, 0.50, 0.045), MAT_DARK, 0.004, False)
        for k in range(5):
            gbox("DRS_CORR_VENT_%s_%d_SLAT_%d" % (side, i, k), (x, -3.47 + k * 0.085, z + inward * 0.045), (0.80, 0.018, 0.018), MAT_STEEL, 0.001, False)

# ------------------------------------------------------------------ finalize
# ------------------------------------------------------------------ finalize
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)

for obj in OBJS:
    if obj.type != 'MESH':
        continue
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    try:
        bpy.ops.object.convert(target='MESH')
    except Exception:
        pass

groups = {}
for obj in OBJS:
    if obj.type != 'MESH' or not obj.data.materials:
        continue
    mat = obj.data.materials[0]
    groups.setdefault(mat.name, []).append(obj)

merged = []
for mat_name, objs in groups.items():
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objs:
        mw = obj.matrix_world.copy()
        obj.parent = None
        obj.matrix_world = mw
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    joined = bpy.context.active_object
    joined.name = "DRESS_" + mat_name.replace("ART3A1_", "").replace("ART3A2_", "")
    for c in list(joined.users_collection):
        c.objects.unlink(joined)
    COLL.objects.link(joined)
    merged.append(joined)

bpy.ops.object.select_all(action='DESELECT')
for obj in merged:
    obj.select_set(True)
bpy.context.view_layer.objects.active = merged[0]
bpy.ops.export_scene.gltf(
    filepath=OUT_GLB,
    export_format='GLB',
    use_selection=True,
    export_apply=True,
    export_yup=True,
    export_image_format='WEBP',
    export_image_quality=85,
    export_cameras=False,
    export_lights=False,
    export_animations=False,
    export_extras=True,
)
print("DRESSING_SAVED", OUT_BLEND)
print("DRESSING_GLB", OUT_GLB, os.path.getsize(OUT_GLB))
print("DRESSING_SOURCE", len(OBJS))
print("DRESSING_MERGED", len(merged))
