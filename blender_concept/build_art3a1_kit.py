import bpy
import math
import os
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
OUT_BLEND = ROOT + "/blender_concept/ART3A1_kit.blend"
OUT_GLB = ROOT + "/assets/models/fm/art3a1/level1_art3a1_kit.glb"
os.makedirs(os.path.dirname(OUT_GLB), exist_ok=True)

# Limpiar escena de trabajo (archivo nuevo, no toca NEXUS_L1_V05.blend).
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0

kit_col = bpy.data.collections.new("ART3A1_KIT")
scene.collection.children.link(kit_col)
desk_col = bpy.data.collections.new("ART3A1_REC_DESK")
duct_col = bpy.data.collections.new("ART3A1_CORR_DUCT")
wall_col = bpy.data.collections.new("ART3A1_CORR_WALL")
kit_col.children.link(desk_col)
kit_col.children.link(duct_col)
kit_col.children.link(wall_col)

KIT_OBJECTS = []

# ---------------------------------------------------------------- materiales

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
        t.image = load_img(diff, False)
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

def solid_mat(name, color, metallic, roughness, emission=None, emission_strength=0.0, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    if emission:
        bsdf.inputs['Emission Color'].default_value = (*emission, 1.0)
        bsdf.inputs['Emission Strength'].default_value = emission_strength
    if alpha < 1.0:
        bsdf.inputs['Alpha'].default_value = alpha
        mat.surface_render_method = 'BLENDED'
    return mat

TEX = ROOT + "/assets/texturas/"
GEN = ROOT + "/assets/art/fm/generated/"
MAT_STEEL = tex_mat("ART3A1_Steel", TEX + "Metal y oxidacion/rusty_metal_sheet_2k.blend/textures/rusty_metal_sheet_diff_2k.jpg", GEN + "gen_rusty_metal_sheet_normal.png", GEN + "gen_rusty_metal_sheet_rough.png", 0.8, base=(0.65, 0.70, 0.76, 1))
MAT_GREEN = tex_mat("ART3A1_GreenPaint", TEX + "Metal y oxidacion/green_metal_rust_2k.blend/textures/green_metal_rust_diff_2k.jpg", GEN + "gen_green_metal_rust_normal.png", TEX + "Metal y oxidacion/green_metal_rust_2k.blend/textures/green_metal_rust_rough_2k.jpg", 0.08, base=(0.72, 0.86, 0.78, 1))
MAT_WOOD = tex_mat("ART3A1_Wood", ROOT + "/assets/Modelos 3D/Mobiliario y almacenamiento/wooden_crate_01_2k.blend/textures/wooden_crate_01_diff_2k.jpg", GEN + "gen_wooden_crate_01_normal.png", GEN + "gen_wooden_crate_01_rough.png", 0.0, base=(0.72, 0.60, 0.48, 1))
MAT_WALL = tex_mat("ART3A1_Wall", TEX + "Pintura y paredes/worn_plaster_wall_2k.blend/textures/worn_plaster_wall_diff_2k.jpg", GEN + "gen_worn_plaster_wall_normal.png", GEN + "gen_worn_plaster_wall_rough.png", 0.0, base=(0.55, 0.62, 0.68, 1))
MAT_DARK = solid_mat("ART3A1_DarkMetal", (0.035, 0.045, 0.050), 0.8, 0.52)
MAT_RUBBER = solid_mat("ART3A1_Rubber", (0.018, 0.022, 0.026), 0.0, 0.86)
MAT_GLASS = solid_mat("ART3A1_Glass", (0.08, 0.13, 0.16), 0.0, 0.06, alpha=0.15)
MAT_CYAN = solid_mat("ART3A1_CyanStrip", (0.02, 0.10, 0.12), 0.0, 0.30, emission=(0.15, 0.70, 0.86), emission_strength=3.2)
MAT_AMBER = solid_mat("ART3A1_AmberStrip", (0.10, 0.035, 0.005), 0.0, 0.42, emission=(1.0, 0.26, 0.04), emission_strength=2.2)
MAT_YELLOW = solid_mat("ART3A1_Hazard", (0.62, 0.34, 0.015), 0.0, 0.62)
MAT_WHITE = solid_mat("ART3A1_Label", (0.62, 0.65, 0.66), 0.0, 0.68)
MAT_DUCT = solid_mat("ART3A1_DuctPaint", (0.045, 0.085, 0.070), 0.12, 0.72)

# ---------------------------------------------------------------- helpers

def link_col(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)

def apply_scale(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

def uv_unwrap(obj, scale=1.0):
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
    if scale != 1.0 and obj.data.uv_layers:
        for d in obj.data.uv_layers.active.data:
            d.uv.x *= scale
            d.uv.y *= scale

def finish(obj, col, mat, bevel=0.012, unwrap=True, uv_scale=1.0):
    link_col(obj, col)
    obj.data.materials.append(mat)
    if unwrap:
        uv_unwrap(obj, uv_scale)
    if bevel > 0:
        m = obj.modifiers.new("Bevel", 'BEVEL')
        m.width = bevel
        m.segments = 2
        m.limit_method = 'ANGLE'
        m.angle_limit = math.radians(40)
        m.harden_normals = True
        n = obj.modifiers.new("Weighted", 'WEIGHTED_NORMAL')
        n.keep_sharp = True
    KIT_OBJECTS.append(obj)
    return obj

def cube(name, loc, size, mat, col, bevel=0.012, unwrap=True, uv_scale=1.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.dimensions = size
    apply_scale(obj)
    return finish(obj, col, mat, bevel, unwrap, uv_scale)

def cyl(name, loc, radius, depth, mat, col, rot=(0, 0, 0), segments=24, bevel=0.0, unwrap=True, uv_scale=1.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=segments, radius=radius, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    return finish(obj, col, mat, bevel, unwrap, uv_scale)

def bolt(name, loc, col, rot=(math.pi/2, 0, 0), r=0.012):
    return cyl(name, loc, r, 0.026, MAT_DARK, col, rot=rot, segments=8, bevel=0.0, unwrap=False)

def empty(name, col):
    e = bpy.data.objects.new(name, None)
    col.objects.link(e)
    return e

def parent_all(root, objs):
    for o in objs:
        if o.parent is None:
            o.parent = root
            o.matrix_parent_inverse = root.matrix_world.inverted()

# ---------------------------------------------------------------- recepción: mostrador

desk_root = empty("ART3A1_REC_DESK_ROOT", desk_col)
desk_objs = []
X0, X1 = -14.10, -9.90
YC = 7.31
Z_FLOOR = -5.65
Z_TOP = -4.94

desk_objs.append(cube("ART3A1_DESK_FASCIA", (-12.0, YC, -5.30), (X1-X0, 0.10, 0.64), MAT_GREEN, desk_col, 0.018, True, 2.0))
desk_objs.append(cube("ART3A1_DESK_TOP_EDGE", (-12.0, 7.33, -4.915), (4.36, 0.16, 0.055), MAT_WOOD, desk_col, 0.012, True, 1.5))
desk_objs.append(cube("ART3A1_DESK_KICK", (-12.0, 7.28, -5.58), (4.20, 0.06, 0.16), MAT_DARK, desk_col, 0.008, False))
for i in range(4):
    x = -13.55 + i * 1.05
    desk_objs.append(cube("ART3A1_DESK_PANEL_%d" % i, (x, 7.245, -5.30), (0.92, 0.045, 0.44), MAT_GREEN, desk_col, 0.014, True, 1.5))
    desk_objs.append(cube("ART3A1_DESK_PANEL_TOP_%d" % i, (x, 7.225, -5.055), (0.98, 0.035, 0.035), MAT_STEEL, desk_col, 0.006, False))
    desk_objs.append(cube("ART3A1_DESK_PANEL_BOT_%d" % i, (x, 7.225, -5.545), (0.98, 0.035, 0.035), MAT_STEEL, desk_col, 0.006, False))
    desk_objs.append(bolt("ART3A1_DESK_BOLT_%d_A" % i, (x - 0.40, 7.21, -5.10), desk_col))
    desk_objs.append(bolt("ART3A1_DESK_BOLT_%d_B" % i, (x + 0.40, 7.21, -5.10), desk_col))
desk_objs.append(cube("ART3A1_DESK_SIDE_E", (-9.92, 8.0, -5.31), (0.10, 1.32, 0.66), MAT_GREEN, desk_col, 0.014, True, 1.5))
desk_objs.append(cube("ART3A1_DESK_SIDE_W", (-14.08, 8.0, -5.31), (0.10, 1.32, 0.66), MAT_GREEN, desk_col, 0.014, True, 1.5))
desk_objs.append(cube("ART3A1_DESK_UNDERLIGHT", (-12.0, 7.235, -5.02), (3.70, 0.025, 0.025), MAT_CYAN, desk_col, 0.0, False))
desk_objs.append(cube("ART3A1_DESK_UNDERLIGHT_HOUSING", (-12.0, 7.27, -4.985), (3.82, 0.06, 0.045), MAT_DARK, desk_col, 0.006, False))

# Cristal y herrajes del mostrador.
desk_objs.append(cube("ART3A1_DESK_GLASS", (-12.0, 7.86, -4.55), (2.70, 0.018, 0.56), MAT_GLASS, desk_col, 0.006, False))
for x in (-13.36, -10.64):
    desk_objs.append(cyl("ART3A1_DESK_GLASS_POST_%s" % int(x), (x, 7.86, -4.52), 0.027, 0.72, MAT_STEEL, desk_col, segments=16, bevel=0.004, unwrap=False))
desk_objs.append(cube("ART3A1_DESK_GLASS_TOP", (-12.0, 7.86, -4.16), (2.76, 0.045, 0.045), MAT_STEEL, desk_col, 0.008, False))
desk_objs.append(cube("ART3A1_DESK_GLASS_BOT", (-12.0, 7.86, -4.88), (2.76, 0.045, 0.045), MAT_STEEL, desk_col, 0.008, False))
for x in (-13.36, -10.64):
    desk_objs.append(bolt("ART3A1_DESK_GLASS_BOLT_%s" % int(x), (x, 7.81, -4.20), desk_col, rot=(math.pi/2, 0, 0), r=0.010))
parent_all(desk_root, desk_objs)

# ---------------------------------------------------------------- corredor: conductos

duct_root = empty("ART3A1_CORR_DUCT_ROOT", duct_col)
duct_objs = []
for seg, cx in enumerate((-10.0, 10.0)):
    x_start = cx - 5.0
    x_end = cx + 5.0
    duct_objs.append(cube("ART3A1_DUCT_BODY_%d" % seg, (cx, 1.15, -2.20), (10.0, 0.48, 0.32), MAT_DUCT, duct_col, 0.020, True, 2.4))
    # Bridas, refuerzos y soportes.
    for i in range(5):
        x = x_start + i * 2.5
        duct_objs.append(cube("ART3A1_DUCT_FLANGE_%d_%d" % (seg, i), (x, 1.15, -2.20), (0.055, 0.63, 0.46), MAT_STEEL, duct_col, 0.008, False))
        for dy in (-0.24, 0.24):
            for dz in (-0.15, 0.15):
                duct_objs.append(bolt("ART3A1_DUCT_FLANGE_BOLT_%d_%d_%s_%s" % (seg, i, dy, dz), (x - 0.032, 1.15 + dy, -2.20 + dz), duct_col, rot=(0, math.pi/2, 0), r=0.008))
    for i in range(9):
        x = x_start + 0.6 + i * 1.0
        duct_objs.append(cube("ART3A1_DUCT_RIB_%d_%d" % (seg, i), (x, 1.15, -2.20), (0.028, 0.57, 0.40), MAT_STEEL, duct_col, 0.004, False))
    # Rejillas de salida orientadas al pasillo.
    for i, x in enumerate((x_start + 1.8, x_start + 5.0, x_start + 8.2)):
        duct_objs.append(cube("ART3A1_DUCT_GRILLE_FRAME_%d_%d" % (seg, i), (x, 0.862, -2.20), (0.72, 0.035, 0.27), MAT_DARK, duct_col, 0.006, False))
        for j in range(4):
            duct_objs.append(cube("ART3A1_DUCT_GRILLE_SLAT_%d_%d_%d" % (seg, i, j), (x, 0.842, -2.30 + j * 0.066), (0.64, 0.012, 0.020), MAT_STEEL, duct_col, 0.002, False))
    # Soportes al techo.
    for x in (x_start + 1.0, cx, x_end - 1.0):
        duct_objs.append(cyl("ART3A1_DUCT_HANGER_%d_%s" % (seg, int(x)), (x, 1.15, -1.87), 0.022, 0.50, MAT_STEEL, duct_col, segments=12, bevel=0.0, unwrap=False))
        duct_objs.append(cube("ART3A1_DUCT_HANGER_BRACKET_%d_%s" % (seg, int(x)), (x, 1.15, -1.73), (0.16, 0.07, 0.035), MAT_STEEL, duct_col, 0.004, False))
for o in duct_objs:
    o.location.y += 0.23
    o.location.z += 0.20
parent_all(duct_root, duct_objs)

# ---------------------------------------------------------------- corredor: paneles de pared

wall_root = empty("ART3A1_CORR_WALL_ROOT", wall_col)
wall_objs = []
for side, y in ((0, 1.54), (1, -1.54)):
    for seg, cx in enumerate((-8.7, 8.7)):
        w = 3.4
        wall_objs.append(cube("ART3A1_WALL_BACK_%d_%d" % (side, seg), (cx, y, -4.12), (w, 0.070, 3.12), MAT_DARK, wall_col, 0.010, True, 2.2))
        wall_objs.append(cube("ART3A1_WALL_FRAME_T_%d_%d" % (side, seg), (cx, y - 0.045 if y > 0 else y + 0.045, -2.58), (w + 0.08, 0.045, 0.06), MAT_STEEL, wall_col, 0.006, False))
        wall_objs.append(cube("ART3A1_WALL_FRAME_B_%d_%d" % (side, seg), (cx, y - 0.045 if y > 0 else y + 0.045, -5.58), (w + 0.08, 0.045, 0.06), MAT_STEEL, wall_col, 0.006, False))
        wall_objs.append(cube("ART3A1_WALL_FRAME_L_%d_%d" % (side, seg), (cx - w*0.5, y - 0.045 if y > 0 else y + 0.045, -4.12), (0.06, 0.045, 3.12), MAT_STEEL, wall_col, 0.006, False))
        wall_objs.append(cube("ART3A1_WALL_FRAME_R_%d_%d" % (side, seg), (cx + w*0.5, y - 0.045 if y > 0 else y + 0.045, -4.12), (0.06, 0.045, 3.12), MAT_STEEL, wall_col, 0.006, False))
        # Paneles hundidos y costillas.
        for i in range(3):
            px = cx - 1.0 + i * 1.0
            wall_objs.append(cube("ART3A1_WALL_PANEL_%d_%d_%d" % (side, seg, i), (px, y - 0.055 if y > 0 else y + 0.055, -4.10), (0.90, 0.025, 2.55), MAT_GREEN, wall_col, 0.008, True, 1.6))
        for i in range(7):
            rx = cx - 1.35 + i * 0.45
            wall_objs.append(cube("ART3A1_WALL_RIB_%d_%d_%d" % (side, seg, i), (rx, y - 0.085 if y > 0 else y + 0.085, -4.05), (0.022, 0.030, 2.62), MAT_STEEL, wall_col, 0.003, False))
        for rz in (-2.95, -3.95, -4.95, -5.35):
            wall_objs.append(cube("ART3A1_WALL_SEAM_%d_%d_%s" % (side, seg, int(rz*10)), (cx, y - 0.085 if y > 0 else y + 0.085, rz), (3.30, 0.030, 0.025), MAT_STEEL, wall_col, 0.003, False))
        # Rejilla de ventilación.
        wx = cx - 0.9 if seg == 0 else cx + 0.9
        wall_objs.append(cube("ART3A1_WALL_VENT_%d_%d" % (side, seg), (wx, y - 0.075 if y > 0 else y + 0.075, -3.10), (0.72, 0.035, 0.38), MAT_DARK, wall_col, 0.006, False))
        for j in range(5):
            wall_objs.append(cube("ART3A1_WALL_VENT_SLAT_%d_%d_%d" % (side, seg, j), (wx, y - 0.095 if y > 0 else y + 0.095, -3.24 + j * 0.065), (0.64, 0.010, 0.018), MAT_STEEL, wall_col, 0.002, False))
        # Caja eléctrica y conducto.
        bx = cx + 1.15
        wall_objs.append(cube("ART3A1_WALL_BOX_%d_%d" % (side, seg), (bx, y - 0.075 if y > 0 else y + 0.075, -3.75), (0.34, 0.12, 0.46), MAT_DARK, wall_col, 0.008, False))
        wall_objs.append(cube("ART3A1_WALL_BOX_DOOR_%d_%d" % (side, seg), (bx, y - 0.145 if y > 0 else y + 0.145, -3.75), (0.28, 0.025, 0.40), MAT_GREEN, wall_col, 0.006, False))
        wall_objs.append(cube("ART3A1_WALL_LABEL_%d_%d" % (side, seg), (bx - 0.30, y - 0.145 if y > 0 else y + 0.145, -3.30), (0.20, 0.010, 0.13), MAT_YELLOW, wall_col, 0.002, False))
        for bx2 in (-1.42, 1.42):
            for bz in (-5.45, -2.72):
                wall_objs.append(bolt("ART3A1_WALL_BOLT_%d_%d_%s_%s" % (side, seg, bx2, bz), (cx + bx2, y - 0.095 if y > 0 else y + 0.095, bz), wall_col, rot=(math.pi/2, 0, 0), r=0.010))
parent_all(wall_root, wall_objs)

# ---------------------------------------------------------------- guardar y exportar

scene.render.resolution_x = 1280
scene.render.resolution_y = 720
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)

# Aplicar modificadores y fusionar por material para que el GLB no tenga 230 draw calls.
for obj in KIT_OBJECTS:
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
for obj in KIT_OBJECTS:
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
    joined.name = "ART3A1_MERGED_" + mat_name.replace("ART3A1_", "")
    link_col(joined, kit_col)
    merged.append(joined)

for obj in bpy.context.selected_objects:
    obj.select_set(False)
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
print("ART3A1_SAVED", OUT_BLEND)
print("ART3A1_GLB", OUT_GLB, os.path.getsize(OUT_GLB))
print("ART3A1_OBJECTS_SOURCE", len(KIT_OBJECTS))
print("ART3A1_OBJECTS_MERGED", len(merged))
