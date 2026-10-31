# FRECUENCIA MUERTA — reconstrucción del pasillo existente en Blender.
# Script independiente para Blender MCP. No modifica Godot ni fotos-referencia.
import bpy
import bmesh
import math
import os
import random
from mathutils import Vector, Quaternion, Euler, Matrix

ROOT = "/home/riyo/Documentos/game"
OUT_DIR = os.path.join(ROOT, "blender_concept")
RENDER_DIR = os.path.join(OUT_DIR, "renders")
ART = os.path.join(ROOT, "assets", "art", "fm")
os.makedirs(RENDER_DIR, exist_ok=True)
random.seed(17)

# ---------------------------------------------------------------------------
# Escena independiente
# ---------------------------------------------------------------------------
scene = bpy.data.scenes.new("FM_CORRIDOR_FINAL")
scene.unit_settings.system = 'METRIC'
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.render.fps = 24
scene.view_settings.view_transform = 'AgX'
try:
    scene.view_settings.look = 'AgX - Medium High Contrast'
except Exception:
    pass
scene.view_settings.exposure = 0.15
for prop, val in (("taa_render_samples", 64), ("use_raytracing", True),
                  ("use_shadows", True), ("use_volumetric_lights", True)):
    try:
        setattr(scene.eevee, prop, val)
    except Exception:
        pass
try:
    scene.eevee.volumetric_tile_size = '4'
except Exception:
    pass
for window in bpy.context.window_manager.windows:
    window.scene = scene

# ---------------------------------------------------------------------------
# Colecciones
# ---------------------------------------------------------------------------
def new_collection(name, parent=None):
    col = bpy.data.collections.new(name)
    (parent or scene.collection).children.link(col)
    return col

COL_ARCH = new_collection("FM_Arquitectura")
COL_STRUCT = new_collection("FM_Estructura")
COL_PIPES = new_collection("FM_Tuberias_Cableado")
COL_DOOR = new_collection("FM_Puerta_Seguridad")
COL_SIGNS = new_collection("FM_Senalizacion")
COL_LIGHT = new_collection("FM_Iluminacion")
COL_SET = new_collection("FM_Set_Dressing")
COL_DAMAGE = new_collection("FM_Danos")
COL_CREATURE = new_collection("FM_Criatura_Vigilante")
COL_CAMS = new_collection("FM_Camaras")
COL_LIGHTS = new_collection("FM_Luces")

# ---------------------------------------------------------------------------
# Utilidades de malla
# ---------------------------------------------------------------------------
def _mesh_obj(name, verts, faces, mat, col, loc=(0, 0, 0), rot=(0, 0, 0), bevel=0.0):
    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.rotation_euler = rot
    if mat is not None:
        obj.data.materials.append(mat)
    col.objects.link(obj)
    if bevel > 0.0:
        mod = obj.modifiers.new("Bisel", 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = 'ANGLE'
    return obj

def box(name, loc, size, mat, col, rot=(0, 0, 0), bevel=0.008):
    sx, sy, sz = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
    verts = [(-sx, -sy, -sz), (sx, -sy, -sz), (sx, sy, -sz), (-sx, sy, -sz),
             (-sx, -sy, sz), (sx, -sy, sz), (sx, sy, sz), (-sx, sy, sz)]
    faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
             (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    return _mesh_obj(name, verts, faces, mat, col, loc, rot, bevel)

def cylinder(name, loc, radius, depth, mat, col, rot=(0, 0, 0), segments=24, bevel=0.0):
    verts = []
    for i in range(segments):
        a = math.tau * i / segments
        verts.append((math.cos(a) * radius, math.sin(a) * radius, -depth * 0.5))
    for i in range(segments):
        a = math.tau * i / segments
        verts.append((math.cos(a) * radius, math.sin(a) * radius, depth * 0.5))
    faces = []
    for i in range(segments):
        j = (i + 1) % segments
        faces.append((i, j, segments + j, segments + i))
    faces.append(tuple(range(segments - 1, -1, -1)))
    faces.append(tuple(range(segments, segments * 2)))
    return _mesh_obj(name, verts, faces, mat, col, loc, rot, bevel)

def cyl_between(name, p1, p2, radius, mat, col, segments=18):
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    length = d.length
    if length < 1e-5:
        return None
    rot = d.to_track_quat('Z', 'Y').to_euler()
    return cylinder(name, (p1 + p2) * 0.5, radius, length, mat, col, rot, segments)

def cone(name, loc, direction, length, radius, mat, col, segments=12):
    verts = []
    for i in range(segments):
        a = math.tau * i / segments
        verts.append((math.cos(a) * radius, math.sin(a) * radius, 0.0))
    verts.append((0.0, 0.0, length))
    faces = []
    for i in range(segments):
        j = (i + 1) % segments
        faces.append((i, j, segments))
    faces.append(tuple(range(segments - 1, -1, -1)))
    obj = _mesh_obj(name, verts, faces, mat, col, loc)
    obj.rotation_euler = Vector(direction).normalized().to_track_quat('Z', 'Y').to_euler()
    return obj

def _apply_uv(obj, uvs):
    mesh = obj.data
    if not mesh.uv_layers:
        mesh.uv_layers.new(name="UVMap")
    layer = mesh.uv_layers.active
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            vi = mesh.loops[li].vertex_index
            layer.data[li].uv = uvs[vi]

def plane_xz(name, center, size, mat, col, rot_y=0.0, bevel=0.0):
    sx, sz = size[0] * 0.5, size[1] * 0.5
    verts = [(-sx, 0, -sz), (-sx, 0, sz), (sx, 0, sz), (sx, 0, -sz)]
    obj = _mesh_obj(name, verts, [(0, 1, 2, 3)], mat, col, center, (0, rot_y, 0), bevel)
    _apply_uv(obj, [(0, 0), (0, 1), (1, 1), (1, 0)])
    return obj

def plane_xy(name, center, size, mat, col, rot=(0, 0, 0), bevel=0.0):
    sx, sy = size[0] * 0.5, size[1] * 0.5
    verts = [(-sx, -sy, 0), (sx, -sy, 0), (sx, sy, 0), (-sx, sy, 0)]
    obj = _mesh_obj(name, verts, [(0, 1, 2, 3)], mat, col, center, rot, bevel)
    _apply_uv(obj, [(0, 0), (1, 0), (1, 1), (0, 1)])
    return obj

def curve_tube(name, points, radius, mat, col):
    curve = bpy.data.curves.new(name + "_curve", type='CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 6
    curve.bevel_depth = radius
    curve.bevel_resolution = 2
    spline = curve.splines.new('POLY')
    spline.points.add(len(points) - 1)
    for i, p in enumerate(points):
        spline.points[i].co = (p[0], p[1], p[2], 1.0)
    obj = bpy.data.objects.new(name, curve)
    obj.data.materials.append(mat)
    col.objects.link(obj)
    return obj

# ---------------------------------------------------------------------------
# Materiales PBR
# ---------------------------------------------------------------------------
def _load_img(filename, non_color=False):
    path = os.path.join(ART, filename)
    if not os.path.exists(path):
        return None
    image = bpy.data.images.load(path, check_existing=True)
    if non_color:
        image.colorspace_settings.name = 'Non-Color'
    return image

def _bsdf(mat):
    nodes = mat.node_tree.nodes
    for n in nodes:
        if n.type == 'BSDF_PRINCIPLED':
            return n
    return None

def _set_in(node, name, value):
    if node and name in node.inputs:
        node.inputs[name].default_value = value

def _image_material(name, albedo_file, normal_file=None, rough_file=None,
                    tint=(1, 1, 1), metallic=0.0, roughness=0.5, scale=0.6):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    coord = nt.nodes.new('ShaderNodeTexCoord')
    mapping = nt.nodes.new('ShaderNodeMapping')
    mapping.inputs['Scale'].default_value = (scale, scale, scale)
    nt.links.new(coord.outputs['Object'], mapping.inputs['Vector'])
    tex = nt.nodes.new('ShaderNodeTexImage')
    tex.image = _load_img(albedo_file)
    tex.projection = 'BOX'
    tex.projection_blend = 0.35
    tex.extension = 'REPEAT'
    nt.links.new(mapping.outputs['Vector'], tex.inputs['Vector'])
    mix = nt.nodes.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    mix.blend_type = 'MULTIPLY'
    mix.inputs[0].default_value = 1.0
    nt.links.new(tex.outputs['Color'], mix.inputs[6])
    mix.inputs[7].default_value = (*tint, 1.0)
    nt.links.new(mix.outputs[2], bsdf.inputs['Base Color'])
    _set_in(bsdf, 'Metallic', metallic)
    _set_in(bsdf, 'Roughness', roughness)
    if rough_file:
        rtex = nt.nodes.new('ShaderNodeTexImage')
        rtex.image = _load_img(rough_file, True)
        rtex.projection = 'BOX'
        rtex.projection_blend = 0.35
        nt.links.new(mapping.outputs['Vector'], rtex.inputs['Vector'])
        nt.links.new(rtex.outputs['Color'], bsdf.inputs['Roughness'])
    if normal_file:
        ntex = nt.nodes.new('ShaderNodeTexImage')
        ntex.image = _load_img(normal_file, True)
        ntex.projection = 'BOX'
        ntex.projection_blend = 0.35
        nt.links.new(mapping.outputs['Vector'], ntex.inputs['Vector'])
        nmap = nt.nodes.new('ShaderNodeNormalMap')
        nmap.inputs['Strength'].default_value = 0.65
        nt.links.new(ntex.outputs['Color'], nmap.inputs['Color'])
        nt.links.new(nmap.outputs['Normal'], bsdf.inputs['Normal'])
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def _simple_material(name, color, metallic=0.0, roughness=0.5, emission=None,
                     emission_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    _set_in(bsdf, 'Metallic', metallic)
    _set_in(bsdf, 'Roughness', roughness)
    if emission:
        _set_in(bsdf, 'Emission Color', (*emission, 1.0))
        _set_in(bsdf, 'Emission Strength', emission_strength)
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

MAT_CONCRETE = _image_material("FM_Concrete_Weathered", "concrete_wall_albedo.png",
                               "concrete_wall_normal.png", "concrete_wall_roughness.png",
                               tint=(0.66, 0.70, 0.63), roughness=0.90, scale=0.55)
MAT_METAL = _image_material("FM_Metal_Panel", "metal_panel_albedo.png",
                            "metal_panel_normal.png", "metal_panel_roughness.png",
                            tint=(0.62, 0.68, 0.70), metallic=0.72, roughness=0.48, scale=0.75)
MAT_FLOOR = _image_material("FM_Floor_Wet", "floor_wet_albedo.png",
                            "floor_wet_normal.png", "floor_wet_roughness.png",
                            tint=(0.31, 0.35, 0.32), metallic=0.40, roughness=0.18, scale=0.55)
MAT_RUST = _image_material("FM_Rust", "rust_albedo.png", "rust_normal.png",
                           "rust_roughness.png", tint=(0.38, 0.27, 0.22),
                           metallic=0.35, roughness=0.84, scale=1.2)
MAT_HAZARD = _image_material("FM_Hazard_Stripes", "hazard_stripe.png", None, None,
                             tint=(0.85, 0.72, 0.48), metallic=0.15, roughness=0.62, scale=1.8)
MAT_DARK = _simple_material("FM_Dark_Metal", (0.018, 0.022, 0.025), 0.82, 0.33)
MAT_DARKER = _simple_material("FM_Recess", (0.004, 0.006, 0.006), 0.15, 0.72)
MAT_YELLOW = _simple_material("FM_Warning_Yellow", (0.62, 0.36, 0.035), 0.25, 0.55)
MAT_RED_PIPE = _simple_material("FM_Red_Pipe", (0.12, 0.022, 0.012), 0.35, 0.58)
MAT_CYAN = _simple_material("FM_Cyan_Emission", (0.005, 0.02, 0.025), 0.0, 0.15,
                            emission=(0.04, 0.82, 1.0), emission_strength=12.0)
MAT_RED = _simple_material("FM_Red_Emergency", (0.02, 0.002, 0.001), 0.0, 0.25,
                           emission=(1.0, 0.02, 0.005), emission_strength=9.0)
MAT_WARM = _simple_material("FM_Warm_Lamp", (0.04, 0.02, 0.008), 0.0, 0.3,
                            emission=(1.0, 0.42, 0.10), emission_strength=6.0)
MAT_GREEN = _simple_material("FM_Bio_Green", (0.002, 0.02, 0.005), 0.0, 0.25,
                             emission=(0.04, 0.85, 0.22), emission_strength=5.0)
MAT_BLOOD = _simple_material("FM_Blood", (0.045, 0.002, 0.0015), 0.0, 0.32)
MAT_WATER = _simple_material("FM_Puddle_Water", (0.010, 0.020, 0.020), 0.55, 0.065)
_set_in(_bsdf(MAT_WATER), 'Coat Weight', 0.6)
_set_in(_bsdf(MAT_WATER), 'Alpha', 0.40)
if hasattr(MAT_WATER, "surface_render_method"):
    MAT_WATER.surface_render_method = 'DITHERED'
MAT_GLASS = _simple_material("FM_Tank_Glass", (0.008, 0.030, 0.022), 0.30, 0.07,
                             emission=(0.010, 0.08, 0.030), emission_strength=0.22)
_set_in(_bsdf(MAT_GLASS), 'Transmission Weight', 0.42)
_set_in(_bsdf(MAT_GLASS), 'IOR', 1.46)
MAT_PAPER = _simple_material("FM_Paper", (0.095, 0.085, 0.060), 0.0, 0.96)
MAT_BONE = _simple_material("FM_Bone", (0.075, 0.060, 0.042), 0.0, 0.86)
MAT_CREATURE = _simple_material("FM_Vigilante_Skin", (0.018, 0.012, 0.010), 0.0, 0.74)
MAT_MOUTH = _simple_material("FM_Vigilante_Maw", (0.001, 0.0005, 0.0005), 0.0, 0.9)
MAT_TEXT = _simple_material("FM_Sign_Text", (0.42, 0.38, 0.27), 0.0, 0.55,
                            emission=(0.85, 0.58, 0.22), emission_strength=1.0)
MAT_TEXT_CYAN = _simple_material("FM_Sign_Text_Cyan", (0.04, 0.22, 0.24), 0.0, 0.4,
                                 emission=(0.10, 0.75, 0.80), emission_strength=1.0)
MAT_TEXT_RED = _simple_material("FM_Sign_Text_Red", (0.24, 0.02, 0.01), 0.0, 0.5,
                                emission=(0.9, 0.04, 0.01), emission_strength=1.0)

# Decal material
def decal_material(name, image_file, opacity=0.85, color=(0.10, 0.01, 0.008),
                   roughness=0.65, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    tex = nt.nodes.new('ShaderNodeTexImage')
    tex.image = _load_img(image_file)
    tex.extension = 'CLIP'
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    nt.links.new(tex.outputs['Alpha'], bsdf.inputs['Alpha'])
    _set_in(bsdf, 'Roughness', roughness)
    _set_in(bsdf, 'Metallic', metallic)
    bsdf.inputs['Alpha'].default_value = opacity
    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = 'DITHERED'
    else:
        mat.blend_method = 'BLEND'
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

MAT_BLOOD_DECAL = decal_material("FM_Blood_Decal", "blood_splat.png", 0.90,
                                 (0.095, 0.004, 0.002), 0.30)
MAT_TRAIL_DECAL = decal_material("FM_Blood_Trail", "blood_trail.png", 0.84,
                                 (0.075, 0.003, 0.0015), 0.34)
MAT_GRIME_DECAL = decal_material("FM_Grime_Decal", "grunge_decal.png", 0.55,
                                 (0.018, 0.016, 0.013), 0.92)
MAT_HAND_DECAL = decal_material("FM_Handprint_Decal", "handprint.png", 0.82,
                                (0.085, 0.003, 0.0015), 0.34)
MAT_CRACK_DECAL = decal_material("FM_Glass_Crack", "glass_crack.png", 0.65,
                                 (0.52, 0.58, 0.58), 0.20)
MAT_PUDDLE_DECAL = decal_material("FM_Puddle_Decal", "puddle.png", 0.72,
                                  (0.010, 0.018, 0.020), 0.035, 0.35)

# ---------------------------------------------------------------------------
# Helpers de escena
# ---------------------------------------------------------------------------
def text_obj(name, body, loc, size, mat, col, rot=(0, 0, 0), extrude=0.002):
    curve = bpy.data.curves.new(name + "_curve", type='FONT')
    curve.body = body
    curve.size = size
    curve.extrude = extrude
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.resolution_u = 3
    obj = bpy.data.objects.new(name, curve)
    obj.location = loc
    obj.rotation_euler = rot
    obj.data.materials.append(mat)
    col.objects.link(obj)
    return obj

def sign_plate(name, loc, size, text, text_size, mat_text, col, rot_y=0.0, text_color=None):
    # size = (width, height); placa delgada sobre el muro o puerta.
    box(name + "_Plate", loc, (size[0], size[1], 0.035), MAT_DARK, col, (0, rot_y, 0), 0.006)
    # El texto se coloca delante de la placa según la normal.
    if abs(rot_y) > 0.1:
        normal = Vector((math.sin(rot_y), 0, math.cos(rot_y)))
        tloc = Vector(loc) + normal * 0.03
        text_obj(name + "_Text", text, tloc, text_size, mat_text or MAT_TEXT, col,
                 (0, rot_y, 0))
    else:
        tloc = Vector(loc) + Vector((0, 0, 0.03))
        text_obj(name + "_Text", text, tloc, text_size, mat_text or MAT_TEXT, col)

def look_matrix(loc, target):
    # Base explícita: evita el roll de 180° de to_track_quat cuando la
    # dirección es casi paralela a -Z.
    loc = Vector(loc)
    forward = (Vector(target) - loc).normalized()
    right = forward.cross(Vector((0, 1, 0)))
    if right.length < 1e-5:
        right = Vector((1, 0, 0))
    right.normalize()
    up = right.cross(forward).normalized()
    rot = Matrix((right, up, -forward)).transposed().to_4x4()
    rot.translation = loc
    return rot

def area_light(name, loc, energy, color, size, size_y, target, col=COL_LIGHTS):
    data = bpy.data.lights.new(name, type='AREA')
    data.energy = energy
    data.color = color
    data.shape = 'RECTANGLE'
    data.size = size
    data.size_y = size_y
    data.use_shadow = True
    obj = bpy.data.objects.new(name, data)
    obj.matrix_world = look_matrix(loc, target)
    col.objects.link(obj)
    return obj

def point_light(name, loc, energy, color, radius=0.12, col=COL_LIGHTS):
    data = bpy.data.lights.new(name, type='POINT')
    data.energy = energy
    data.color = color
    data.shadow_soft_size = radius
    data.use_shadow = True
    obj = bpy.data.objects.new(name, data)
    obj.location = loc
    col.objects.link(obj)
    return obj

def spot_light(name, loc, target, energy, color, angle_deg, blend=0.45, radius=0.08, col=COL_LIGHTS):
    data = bpy.data.lights.new(name, type='SPOT')
    data.energy = energy
    data.color = color
    data.spot_size = math.radians(angle_deg)
    data.spot_blend = blend
    data.shadow_soft_size = radius
    data.use_shadow = True
    obj = bpy.data.objects.new(name, data)
    obj.matrix_world = look_matrix(loc, target)
    col.objects.link(obj)
    return obj

# ---------------------------------------------------------------------------
# Arquitectura
# ---------------------------------------------------------------------------
box("FM_Floor", (0, -0.16, 0), (5.4, 0.32, 24.4), MAT_FLOOR, COL_ARCH, bevel=0.012)
box("FM_Ceiling", (0, 4.22, 0), (5.4, 0.26, 24.4), MAT_CONCRETE, COL_ARCH, bevel=0.012)
box("FM_Wall_Right", (2.82, 2.08, 0), (0.24, 4.16, 24.4), MAT_CONCRETE, COL_ARCH)
box("FM_Wall_Left_Back", (-2.82, 2.08, -6.0), (0.24, 4.16, 12.4), MAT_CONCRETE, COL_ARCH)
box("FM_Wall_Left_Front", (-2.82, 2.08, 8.75), (0.24, 4.16, 6.5), MAT_CONCRETE, COL_ARCH)
box("FM_Wall_Left_Header", (-2.82, 3.72, 2.75), (0.24, 0.72, 5.5), MAT_METAL, COL_ARCH)

# Zócalos metálicos y molduras.
for side in (-1, 1):
    box("FM_Baseboard_%s" % ("L" if side < 0 else "R"),
        (2.72 * side, 0.18, 0), (0.20, 0.36, 24.1), MAT_DARK, COL_ARCH, bevel=0.006)
    box("FM_MidTrim_%s" % ("L" if side < 0 else "R"),
        (2.72 * side, 1.72, 0), (0.16, 0.10, 24.1), MAT_DARK, COL_ARCH, bevel=0.005)
    box("FM_TopTrim_%s" % ("L" if side < 0 else "R"),
        (2.72 * side, 4.02, 0), (0.18, 0.14, 24.1), MAT_DARK, COL_ARCH, bevel=0.005)

# Paneles metálicos superiores con juntas verticales.
for side in (-1, 1):
    y = 2.86
    for i in range(24):
        z = -11.5 + i * 1.0
        if side < 0 and -0.1 < z < 5.6:
            continue
        box("FM_Panel_%s_%02d" % ("L" if side < 0 else "R", i),
            (2.785 * side, y, z), (0.035, 2.15, 0.96), MAT_METAL, COL_ARCH, bevel=0.004)
    for i in range(25):
        z = -12.0 + i
        if side < 0 and -0.1 < z < 5.6:
            continue
        box("FM_Seam_%s_%02d" % ("L" if side < 0 else "R", i),
            (2.745 * side, y, z), (0.022, 2.18, 0.025), MAT_DARK, COL_ARCH, bevel=0.002)

# Suelo: juntas y placas.
for i in range(12):
    z = -10.8 + i * 2.0
    box("FM_FloorSeam_%02d" % i, (0, 0.006, z), (5.1, 0.012, 0.022), MAT_DARK, COL_ARCH, bevel=0.0)
for i in range(4):
    x = -2.0 + i * 1.33
    box("FM_FloorLong_%02d" % i, (x, 0.007, 0), (0.018, 0.014, 23.6), MAT_DARK, COL_ARCH, bevel=0.0)

# Entrada y remate trasero.
box("FM_Entry_Header", (0, 3.35, 11.9), (5.2, 0.55, 0.32), MAT_DARK, COL_STRUCT, bevel=0.012)
for side in (-1, 1):
    box("FM_Entry_Jamb_%d" % side, (2.35 * side, 1.7, 11.9), (0.35, 3.4, 0.32), MAT_DARK, COL_STRUCT, bevel=0.012)

# ---------------------------------------------------------------------------
# Estructura: costillas y vigas
# ---------------------------------------------------------------------------
for i in range(11):
    z = -10.0 + i * 2.0
    for side in (-1, 1):
        x = 2.56 * side
        box("FM_Rib_Web_%02d_%d" % (i, side), (x, 2.02, z), (0.08, 3.92, 0.24), MAT_DARK, COL_STRUCT, bevel=0.007)
        box("FM_Rib_Flange_%02d_%d" % (i, side), (x - 0.09 * side, 2.02, z), (0.08, 3.92, 0.36), MAT_DARK, COL_STRUCT, bevel=0.007)
        # Placas de anclaje y pernos.
        box("FM_Rib_Foot_%02d_%d" % (i, side), (x, 0.20, z), (0.30, 0.12, 0.46), MAT_DARK, COL_STRUCT, bevel=0.008)
        for by in (0.65, 3.55):
            for bz in (-0.12, 0.12):
                cylinder("FM_RibBolt_%02d_%d_%.1f_%.1f" % (i, side, by, bz),
                         (x - 0.14 * side, by, z + bz), 0.027, 0.018, MAT_RUST, COL_STRUCT,
                         (0, math.radians(90), 0), 10)
    box("FM_Rib_Cross_%02d" % i, (0, 4.05, z), (5.28, 0.17, 0.20), MAT_DARK, COL_STRUCT, bevel=0.008)
    box("FM_Rib_Gusset_%02d" % i, (0, 3.88, z), (5.1, 0.08, 0.06), MAT_RUST, COL_STRUCT, bevel=0.004)

# Vigas longitudinales del techo.
for side in (-1, 1):
    box("FM_CeilingStringer_%d" % side, (1.45 * side, 4.10, 0), (0.12, 0.16, 23.8), MAT_DARK, COL_STRUCT, bevel=0.006)

# ---------------------------------------------------------------------------
# Ventanal de laboratorio (sin construir el laboratorio)
# ---------------------------------------------------------------------------
# Receso oscuro y vidrio: conserva el hueco del pasillo original, sin sala nueva.
box("FM_Lab_Recess", (-3.22, 1.8, 2.75), (0.12, 3.55, 5.5), MAT_DARKER, COL_ARCH)
box("FM_Lab_Glass", (-2.76, 1.78, 2.75), (0.025, 2.86, 5.22), MAT_GLASS, COL_ARCH, bevel=0.003)
for z in (0.18, 1.45, 2.75, 4.05, 5.32):
    box("FM_Lab_Mullion_%.2f" % z, (-2.71, 1.80, z), (0.10, 3.1, 0.075), MAT_DARK, COL_ARCH, bevel=0.005)
for y in (0.30, 1.34, 2.36, 3.22):
    box("FM_Lab_Transom_%.2f" % y, (-2.71, y, 2.75), (0.10, 0.075, 5.35), MAT_DARK, COL_ARCH, bevel=0.005)
box("FM_Lab_Threshold", (-2.70, 0.015, 2.75), (0.34, 0.025, 5.4), MAT_YELLOW, COL_ARCH, bevel=0.002)

# Grieta y suciedad sobre el vidrio.
plane_xy("FM_Lab_GlassCrack", (-2.742, 1.62, 3.65), (1.25, 1.65), MAT_CRACK_DECAL,
         COL_DAMAGE, (0, math.radians(90), math.radians(-4)))

# Marco de entrada del laboratorio.
for z in (0.0, 5.5):
    box("FM_Lab_Frame_%.1f" % z, (-2.82, 1.92, z), (0.38, 3.9, 0.22), MAT_DARK, COL_ARCH, bevel=0.01)
box("FM_Lab_Frame_Top", (-2.82, 3.74, 2.75), (0.38, 0.20, 5.5), MAT_DARK, COL_ARCH, bevel=0.01)

# ---------------------------------------------------------------------------
# Puerta de seguridad
# ---------------------------------------------------------------------------
box("FM_Door_Frame_L", (-1.58, 1.52, -9.9), (0.24, 3.12, 0.30), MAT_DARK, COL_DOOR, bevel=0.008)
box("FM_Door_Frame_R", (1.58, 1.52, -9.9), (0.24, 3.12, 0.30), MAT_DARK, COL_DOOR, bevel=0.008)
box("FM_Door_Header", (0, 3.12, -9.9), (3.4, 0.22, 0.32), MAT_DARK, COL_DOOR, bevel=0.008)
for side in (-1, 1):
    box("FM_Door_Leaf_%d" % side, (0.68 * side, 1.37, -9.84), (1.3, 2.68, 0.12),
        MAT_METAL, COL_DOOR, bevel=0.008)
    # Refuerzos verticales y remaches.
    for r in (-0.32, 0.0, 0.32):
        box("FM_Door_Rib_%d_%.2f" % (side, r), (0.68 * side + r, 1.37, -9.765),
            (0.055, 2.48, 0.035), MAT_DARK, COL_DOOR, bevel=0.003)
    for yy in (0.58, 1.30, 2.02):
        cylinder("FM_Door_Bolt_%d_%.1f" % (side, yy), (0.68 * side + 0.46, yy, -9.745),
                 0.022, 0.014, MAT_RUST, COL_DOOR, (math.radians(90), 0, 0), 10)
    # Manija y bisagras.
    box("FM_Door_Handle_%d" % side, (0.28 * side, 1.15, -9.71), (0.10, 0.22, 0.06), MAT_DARK, COL_DOOR, bevel=0.006)
    for hy in (0.42, 2.30):
        box("FM_Door_Hinge_%d_%.1f" % (side, hy), (1.31 * side, hy, -9.78), (0.10, 0.26, 0.08), MAT_RUST, COL_DOOR, bevel=0.005)

box("FM_Door_CenterSeam", (0, 1.37, -9.755), (0.035, 2.54, 0.035), MAT_DARK, COL_DOOR, bevel=0.002)
# Franja hazard inferior y barras superiores.
box("FM_Door_Hazard", (0, 0.22, -9.70), (2.58, 0.42, 0.022), MAT_HAZARD, COL_DOOR, bevel=0.002)
box("FM_Door_RedBar", (0, 3.04, -9.72), (2.24, 0.065, 0.09), MAT_RED, COL_DOOR, bevel=0.004)
box("FM_Door_CyanBar", (0, 3.28, -9.72), (1.78, 0.055, 0.07), MAT_CYAN, COL_DOOR, bevel=0.004)
# Keypad.
box("FM_Door_Keypad", (1.78, 1.42, -9.68), (0.28, 0.40, 0.10), MAT_DARK, COL_DOOR, bevel=0.006)
box("FM_Door_Keypad_Screen", (1.78, 1.53, -9.615), (0.17, 0.10, 0.018), MAT_GREEN, COL_DOOR, bevel=0.002)
for i in range(6):
    box("FM_Door_Key_%d" % i, (1.70 + (i % 3) * 0.055, 1.36 - (i // 3) * 0.065, -9.62),
        (0.035, 0.035, 0.012), MAT_DARK, COL_DOOR, bevel=0.001)
# Umbral y banda de advertencia en el suelo.
box("FM_Door_Threshold_Hazard", (0, 0.012, -9.28), (2.8, 0.022, 0.72), MAT_HAZARD, COL_DOOR, bevel=0.0)
box("FM_Door_Threshold_Dark", (0, 0.008, -9.28), (2.9, 0.010, 0.82), MAT_DARKER, COL_DOOR, bevel=0.0)

# ---------------------------------------------------------------------------
# Tuberías, cableado y rejillas
# ---------------------------------------------------------------------------
cylinder("FM_Pipe_Red_Main", (-2.28, 3.52, 0), 0.12, 23.4, MAT_RED_PIPE, COL_PIPES, segments=20)
cylinder("FM_Pipe_Rust_Main", (-2.02, 3.20, 0), 0.072, 23.4, MAT_RUST, COL_PIPES, segments=16)
cylinder("FM_Pipe_Right_Rust", (2.48, 2.92, 0), 0.105, 23.4, MAT_RUST, COL_PIPES, segments=18)
cylinder("FM_Conduit_Cyan", (2.30, 3.52, 0), 0.036, 23.4, MAT_DARK, COL_PIPES, segments=12)
for z in range(-10, 12, 2):
    for x, y, r in ((-2.28, 3.52, 0.17), (-2.02, 3.20, 0.11), (2.48, 2.92, 0.15)):
        cylinder("FM_PipeClamp_%.0f_%.1f" % (z, x), (x, y, z), r, 0.075, MAT_DARK, COL_PIPES, segments=14)
    box("FM_PipeBracket_%.0f" % z, (-2.58, 3.42, z), (0.42, 0.08, 0.08), MAT_DARK, COL_PIPES, bevel=0.004)
    box("FM_PipeBracketR_%.0f" % z, (2.60, 2.98, z), (0.36, 0.08, 0.08), MAT_DARK, COL_PIPES, bevel=0.004)

# Bandeja de cables derecha.
box("FM_CableTray_Bottom", (1.86, 3.76, 0), (0.30, 0.035, 23.0), MAT_DARK, COL_PIPES, bevel=0.004)
for side in (-1, 1):
    box("FM_CableTray_Side_%d" % side, (1.86 + 0.15 * side, 3.84, 0), (0.025, 0.14, 23.0), MAT_DARK, COL_PIPES, bevel=0.003)
for i in range(5):
    cylinder("FM_Cable_%d" % i, (1.80 + i * 0.035, 3.79, 0), 0.012, 23.0,
             MAT_RED_PIPE if i == 2 else MAT_DARK, COL_PIPES, segments=8)

# Conductos y cajas eléctricas.
for z in (-7.0, -2.5, 3.2, 8.2):
    box("FM_JunctionBox_%.1f" % z, (2.66, 2.35, z), (0.18, 0.42, 0.34), MAT_DARK, COL_PIPES, bevel=0.006)
    box("FM_JunctionDoor_%.1f" % z, (2.56, 2.35, z), (0.02, 0.34, 0.26), MAT_METAL, COL_PIPES, bevel=0.003)
    cylinder("FM_JunctionConduit_%.1f" % z, (2.55, 1.88, z), 0.026, 0.95, MAT_DARK, COL_PIPES, segments=8)
    cylinder("FM_JunctionConduitTop_%.1f" % z, (2.55, 2.85, z + 0.18), 0.022, 0.60, MAT_DARK, COL_PIPES, segments=8)

# Rejillas de ventilación.
for z, side in ((-6.0, 1), (1.0, 1), (7.2, 1), (-8.0, -1)):
    x = 2.70 * side
    box("FM_Vent_Frame_%.1f_%d" % (z, side), (x, 2.62, z), (0.05, 0.62, 0.86), MAT_DARK, COL_STRUCT, bevel=0.005)
    for i in range(6):
        box("FM_Vent_Slat_%.1f_%d_%d" % (z, side, i), (x - 0.035 * side, 2.36 + i * 0.09, z),
            (0.02, 0.035, 0.72), MAT_METAL, COL_STRUCT, bevel=0.002, rot=(0, 0, math.radians(-8)))

# Cámaras de seguridad.
for z, side in ((-5.2, 1), (4.8, -1)):
    base = Vector((2.58 * side, 3.62, z))
    box("FM_SecurityCam_Mount_%.1f" % z, base, (0.16, 0.16, 0.26), MAT_DARK, COL_PIPES, bevel=0.006)
    cylinder("FM_SecurityCam_Body_%.1f" % z, base + Vector((-0.10 * side, -0.22, 0.05)), 0.075, 0.30,
             MAT_DARK, COL_PIPES, (math.radians(90), 0, math.radians(28 * side)), 14)
    cylinder("FM_SecurityCam_Lens_%.1f" % z, base + Vector((-0.20 * side, -0.34, 0.07)), 0.045, 0.045,
             MAT_DARKER, COL_PIPES, (math.radians(90), 0, math.radians(28 * side)), 14)
    point_light("FM_SecurityCam_LED_%.1f" % z, base + Vector((-0.20 * side, -0.36, 0.09)), 2.0,
                (1.0, 0.02, 0.01), 0.02)

# ---------------------------------------------------------------------------
# Iluminación: fixtures, emergencias y luces prácticas
# ---------------------------------------------------------------------------
for idx, z in enumerate((8.0, 3.0, -2.0, -7.0)):
    box("FM_Fixture_Housing_%d" % idx, (0, 4.00, z), (1.64, 0.10, 0.26), MAT_DARK, COL_LIGHT, bevel=0.006)
    box("FM_Fixture_Tube_%d" % idx, (0, 3.938, z), (1.42, 0.022, 0.105), MAT_CYAN, COL_LIGHT, bevel=0.002)
    for dx in (-0.62, 0.62):
        cylinder("FM_Fixture_Rod_%d_%.1f" % (idx, dx), (dx, 4.13, z), 0.012, 0.22, MAT_DARK, COL_LIGHT, segments=8)
    area_light("FM_Light_Ceiling_%d" % idx, (0, 3.82, z), 210.0, (0.48, 0.74, 1.0), 1.45, 0.13, (0, 0, z))

# Emergencias rojas en pared derecha.
for idx, z in enumerate((4.0, -4.0, -8.0)):
    box("FM_Emergency_Housing_%d" % idx, (2.64, 2.62, z), (0.16, 0.34, 0.24), MAT_DARK, COL_LIGHT, bevel=0.006)
    box("FM_Emergency_Lens_%d" % idx, (2.54, 2.62, z), (0.02, 0.22, 0.14), MAT_RED, COL_LIGHT, bevel=0.002)
    point_light("FM_Light_Emergency_%d" % idx, (2.38, 2.58, z), 42.0, (1.0, 0.025, 0.012), 0.10)

# Balizas superiores junto a la puerta.
for side in (-1, 1):
    box("FM_Door_Beacon_Base_%d" % side, (1.72 * side, 3.54, -9.70), (0.18, 0.10, 0.16), MAT_DARK, COL_LIGHT, bevel=0.004)
    cylinder("FM_Door_Beacon_Lens_%d" % side, (1.72 * side, 3.46, -9.62), 0.065, 0.10, MAT_RED, COL_LIGHT, segments=12)
    point_light("FM_Light_Door_Beacon_%d" % side, (1.72 * side, 3.40, -9.55), 12.0, (1.0, 0.015, 0.005), 0.08)

# Luz verde del laboratorio detrás del vidrio (sin sala).
point_light("FM_Light_LabSpill", (-2.90, 2.0, 2.5), 115.0, (0.05, 0.65, 0.18), 0.25)
area_light("FM_Light_LabFill", (-3.18, 2.4, 2.5), 65.0, (0.08, 0.45, 0.20), 2.0, 2.2, (-2.5, 1.4, 2.5))

# Key, fill y contraluz.
area_light("FM_Light_Key", (0, 3.75, 5.2), 300.0, (0.55, 0.78, 1.0), 3.2, 2.8, (0, 0.5, 0))
area_light("FM_Light_Fill", (0, 2.20, -1.5), 85.0, (0.20, 0.36, 0.55), 2.4, 2.0, (0, 1.2, -5.0))
area_light("FM_Light_EntryRim", (0, 2.5, 11.2), 130.0, (0.38, 0.62, 0.92), 2.0, 2.0, (0, 1.2, 0))
spot_light("FM_Light_DoorSpot", (0, 3.35, -7.45), (0, 1.15, -9.9), 950.0,
           (0.76, 0.88, 0.72), 48.0, 0.55, 0.10)
spot_light("FM_Light_DoorBlue", (0, 3.20, -11.0), (0, 1.3, -9.7), 120.0,
           (0.18, 0.40, 0.72), 45.0, 0.6, 0.10)
point_light("FM_Light_BackRim", (0, 2.45, -10.6), 55.0, (0.45, 0.65, 1.0), 0.15)
point_light("FM_Light_WarmWork", (-1.8, 1.9, 6.2), 28.0, (1.0, 0.42, 0.12), 0.10)

# Rebote cenital tenue: revela el techo sin crear barras blancas en los paneles.
for idx, z in enumerate((5.0, -4.0)):
    area_light("FM_Light_CeilingBounce_%d" % idx, (0, 3.55, z), 260.0,
               (0.35, 0.48, 0.62), 4.4, 3.2, (0, 4.20, z))

# ---------------------------------------------------------------------------
# Señalización
# ---------------------------------------------------------------------------
# Placa sobre la puerta.
box("FM_Sign_Sector_Plate", (0, 3.55, -9.80), (2.1, 0.52, 0.04), MAT_DARK, COL_SIGNS, bevel=0.005)
text_obj("FM_Sign_Sector_Text", "SECTOR 04", (0, 3.58, -9.765), 0.215, MAT_TEXT, COL_SIGNS)
text_obj("FM_Sign_Sector_Sub", "NEXUS // CONTENCIÓN", (0, 3.40, -9.765), 0.090, MAT_TEXT_CYAN, COL_SIGNS)

# Señales de pared izquierda (frente +X).
sign_plate("FM_Sign_BioLab", (-2.72, 3.82, 2.75), (1.60, 0.38), "BIO-LAB 04", 0.14,
           MAT_TEXT_CYAN, COL_SIGNS, math.radians(90))
sign_plate("FM_Sign_Contaminada", (-2.76, 2.45, 7.8), (1.80, 0.42), "ZONA CONTAMINADA", 0.13,
           MAT_TEXT_RED, COL_SIGNS, math.radians(90))
sign_plate("FM_Sign_Salida", (2.76, 2.55, 8.3), (1.95, 0.44), "SALIDA DE EMERGENCIA", 0.12,
           MAT_TEXT_CYAN, COL_SIGNS, math.radians(-90))
sign_plate("FM_Sign_Nivel3", (2.76, 2.95, -6.4), (1.55, 0.40), "AUTORIZACIÓN NIVEL 3", 0.090,
           MAT_TEXT, COL_SIGNS, math.radians(-90))
sign_plate("FM_Sign_Riesgo", (2.76, 2.35, -8.1), (1.35, 0.40), "RIESGO BIOLÓGICO", 0.098,
           MAT_TEXT_RED, COL_SIGNS, math.radians(-90))

# Sin flechas gigantes en el suelo: el pasillo original usa señalización de pared.

# ---------------------------------------------------------------------------
# Set dressing: puddles, sangre, papeles, escombros, daños
# ---------------------------------------------------------------------------
def floor_blob(name, center, radius_x, radius_z, mat, col, segments=18):
    cx, cz = center[0], center[2]
    verts = [(cx, center[1], cz)]
    for i in range(segments):
        a = math.tau * i / segments
        r = 1.0 + 0.16 * math.sin(i * 3.7 + 1.3) + random.uniform(-0.10, 0.10)
        verts.append((cx + math.cos(a) * radius_x * r, center[1],
                      cz + math.sin(a) * radius_z * r))
    faces = []
    for i in range(segments):
        faces.append((0, 1 + i, 1 + (i + 1) % segments))
    # Corregir el orden para que la normal mire hacia +Y.
    obj = _mesh_obj(name, verts, faces, mat, col)
    for poly in obj.data.polygons:
        if poly.normal.y < 0:
            poly.flip()
    return obj

for i, data in enumerate([
    (1.55, 4.6, 1.35, 2.6), (-1.65, 6.2, 0.90, 1.80),
    (0.65, -3.6, 1.55, 3.10), (-1.95, -6.6, 1.05, 2.35),
    (1.95, -1.7, 0.75, 1.35), (0.15, 9.4, 0.95, 2.0),
]):
    plane_xz("FM_PuddleDecal_%d" % i, (data[0], 0.010, data[1]),
             (data[2], data[3]), MAT_PUDDLE_DECAL, COL_SET,
             random.uniform(-0.5, 0.5))

for i, data in enumerate([
    (-1.75, 3.5, 1.0, 1.8), (-0.95, 1.8, 0.8, 1.2),
    (0.45, -1.0, 0.85, 1.4), (1.55, -4.5, 0.65, 1.0),
]):
    plane_xz("FM_BloodDecal_%d" % i, (data[0], 0.014, data[1]),
             (data[2], data[3]), MAT_BLOOD_DECAL, COL_DAMAGE,
             random.uniform(-0.8, 0.8))

# Rastro de sangre y huellas con textura.
plane_xz("FM_BloodTrail_Main", (-0.85, 0.018, 2.9), (1.35, 4.6), MAT_TRAIL_DECAL,
         COL_DAMAGE, math.radians(-9))
plane_xz("FM_BloodSplat_A", (0.4, 0.019, 4.8), (1.4, 1.4), MAT_BLOOD_DECAL, COL_DAMAGE, math.radians(31))
plane_xz("FM_BloodSplat_B", (-1.5, 0.019, 0.7), (1.0, 1.2), MAT_BLOOD_DECAL, COL_DAMAGE, math.radians(-47))

# Mancha y huella en la pared derecha.
plane_xy("FM_Handprint_Wall", (2.735, 1.55, -7.2), (0.38, 0.52), MAT_HAND_DECAL,
         COL_DAMAGE, (0, math.radians(-90), math.radians(8)))
plane_xy("FM_Grime_Wall_1", (2.741, 1.30, 2.0), (1.7, 1.1), MAT_GRIME_DECAL,
         COL_DAMAGE, (0, math.radians(-90), 0))
plane_xy("FM_Grime_Wall_2", (-2.741, 1.15, -5.0), (2.0, 1.4), MAT_GRIME_DECAL,
         COL_DAMAGE, (0, math.radians(90), 0))
plane_xy("FM_Grime_Wall_3", (2.741, 1.45, -4.6), (1.25, 0.85), MAT_GRIME_DECAL,
         COL_DAMAGE, (0, math.radians(-90), math.radians(4)))
plane_xy("FM_Grime_Wall_4", (2.741, 1.65, 7.0), (1.5, 0.9), MAT_GRIME_DECAL,
         COL_DAMAGE, (0, math.radians(-90), math.radians(-3)))
plane_xy("FM_Grime_Wall_5", (-2.741, 1.35, 8.6), (1.35, 0.95), MAT_GRIME_DECAL,
         COL_DAMAGE, (0, math.radians(90), 0))
plane_xy("FM_Grime_Wall_6", (-2.741, 1.55, -8.6), (1.6, 1.0), MAT_GRIME_DECAL,
         COL_DAMAGE, (0, math.radians(90), math.radians(5)))

# Escurrimientos de óxido y agua sobre los paneles.
for i in range(18):
    side = random.choice((-1, 1))
    z = random.uniform(-9.2, 9.6)
    y0 = random.uniform(0.9, 2.9)
    h = random.uniform(0.35, 1.45)
    box("FM_RustStreak_%02d" % i, (2.737 * side, y0 + h * 0.5, z),
        (0.006, h, random.uniform(0.012, 0.045)), MAT_RUST, COL_DAMAGE, bevel=0.0)

# Papeles.
for i in range(10):
    z = random.uniform(-8.8, 9.0)
    x = random.uniform(-2.2, 2.2)
    rot = (0, math.radians(random.uniform(0, 360)), 0)
    plane_xz("FM_Paper_%02d" % i, (x, 0.021, z),
             (random.uniform(0.10, 0.22), random.uniform(0.14, 0.28)),
             MAT_PAPER, COL_SET, rot[1])

# Cristales y escombros.
for i in range(15):
    z = random.uniform(-9.0, 9.5)
    x = random.choice((-1, 1)) * random.uniform(1.8, 2.45)
    box("FM_Debris_%02d" % i, (x, random.uniform(0.04, 0.12), z),
        (random.uniform(0.06, 0.18), random.uniform(0.04, 0.12), random.uniform(0.08, 0.24)),
        random.choice((MAT_RUST, MAT_DARK, MAT_METAL)), COL_SET,
        (random.uniform(-0.25, 0.25), random.uniform(0, 6.28), random.uniform(-0.22, 0.22)),
        bevel=0.003)

# Charcos de agua con superficies glossy reales (no solo decal).
for i, data in enumerate([
    (1.35, 3.2, 0.32, 0.68), (-1.35, 5.8, 0.28, 0.56),
    (0.2, -2.0, 0.45, 0.90), (-2.0, -6.2, 0.24, 0.48),
    (1.6, -7.8, 0.20, 0.40),
]):
    # Borde suave de textura + superficie de agua más pequeña.
    plane_xz("FM_PuddleRim_%d" % i, (data[0], 0.011, data[1]),
             (data[2] * 2.5, data[3] * 2.5), MAT_PUDDLE_DECAL, COL_SET,
             random.uniform(-0.5, 0.5))
    floor_blob("FM_PuddleWater_%d" % i, (data[0], 0.013, data[1]), data[2], data[3],
               MAT_WATER, COL_SET)

# Panel de techo desprendido y cables.
box("FM_DamagedCeilingPanel", (0.75, 3.66, 1.7), (1.55, 0.045, 0.82), MAT_METAL, COL_DAMAGE,
    (math.radians(13), math.radians(-3), math.radians(2)), 0.004)
for i in range(3):
    curve_tube("FM_HangingCable_%d" % i,
               [(0.4 + i * 0.25, 4.12, 1.2), (0.55 + i * 0.20, 3.92, 1.45),
                (0.72 + i * 0.18, 3.62, 1.62), (0.85 + i * 0.16, 3.35, 1.52)],
               0.008, MAT_DARK, COL_DAMAGE)

# Tubo roto con fuga y óxido.
cylinder("FM_BrokenPipe", (2.35, 3.05, -3.2), 0.08, 0.55, MAT_RUST, COL_DAMAGE,
         (math.radians(90), 0, math.radians(14)), 14)
for i in range(4):
    plane_xz("FM_RustStain_%d" % i, (2.69, 1.55 + i * 0.25, -3.2), (0.38, 1.2),
             MAT_GRIME_DECAL, COL_DAMAGE, math.radians(90 * (i % 2)))

# ---------------------------------------------------------------------------
# El Vigilante (silueta lejana, diseño documentado)
# ---------------------------------------------------------------------------
mb = bpy.data.metaballs.new("FM_Vigilante_Metaball")
mb.resolution = 0.035
mb.render_resolution = 0.035
vig = bpy.data.objects.new("FM_Vigilante", mb)
vig.location = (-1.95, 0.0, -7.20)
COL_CREATURE.objects.link(vig)
mb.materials.append(MAT_CREATURE)

def parent_local(obj, parent):
    # Las piezas se modelaron alrededor del origen local de la criatura.
    obj.parent = parent
    return obj

def mb_el(co, sx, sy, sz, stiffness=2.0):
    el = mb.elements.new()
    el.type = 'ELLIPSOID'
    el.co = co
    el.radius = 1.0
    el.size_x = sx
    el.size_y = sy
    el.size_z = sz
    el.stiffness = stiffness
    return el

mb_el((0, 1.42, 0), 0.24, 0.58, 0.20)
mb_el((0, 1.78, -0.03), 0.27, 0.40, 0.21)
mb_el((0, 1.08, 0), 0.18, 0.20, 0.16)
mb_el((0, 2.30, -0.06), 0.11, 0.20, 0.10)
mb_el((0, 2.60, -0.08), 0.16, 0.31, 0.15)
for side in (-1, 1):
    mb_el((0.34 * side, 1.72, 0.0), 0.075, 0.40, 0.075)
    mb_el((0.46 * side, 1.18, -0.05), 0.060, 0.35, 0.060)
    mb_el((0.20 * side, 0.62, 0.02), 0.075, 0.34, 0.080)
    mb_el((0.24 * side, 0.18, -0.03), 0.060, 0.25, 0.065)

# Púas orgánicas.
for side in (-1, 1):
    for i, (y, dz, length) in enumerate(((2.05, 0.12, 0.38), (1.78, 0.18, 0.32), (1.52, 0.17, 0.25))):
        sp = cone("FM_Vigilante_Spike_%d_%d" % (side, i), (0.26 * side, y, 0.10 + dz),
                  (0.65 * side, 0.25, 0.72), length, 0.035, MAT_BONE, COL_CREATURE, 8)
        parent_local(sp, vig)
for i in range(4):
    sp = cone("FM_Vigilante_BackSpike_%d" % i, (0.0, 1.55 + i * 0.16, 0.19),
              (0, 0.10, 1.0), 0.20 + i * 0.02, 0.028, MAT_BONE, COL_CREATURE, 8)
    parent_local(sp, vig)

# Garras y boca vertical.
for side in (-1, 1):
    for f in range(3):
        cl = cone("FM_Vigilante_Claw_%d_%d" % (side, f), (0.50 * side + (f - 1) * 0.035, 0.88, -0.08),
                  (0.15 * side, -1.0, -0.10), 0.16, 0.018, MAT_BONE, COL_CREATURE, 6)
        parent_local(cl, vig)
maw = plane_xy("FM_Vigilante_Maw", (0.0, 2.56, -0.225), (0.10, 0.36), MAT_MOUTH,
               COL_CREATURE, (0, 0, 0))
parent_local(maw, vig)
# Luz de contorno absoluta, fuera de la jerarquía de la criatura.
point_light("FM_Light_CreatureRim", (-1.95, 2.45, -8.6), 140.0, (0.85, 0.05, 0.025), 0.10)


# ---------------------------------------------------------------------------
# Cámaras
# ---------------------------------------------------------------------------
def camera(name, loc, target, lens=35.0, fstop=5.6, focus=None):
    data = bpy.data.cameras.new(name)
    data.lens = lens
    data.sensor_width = 36.0
    data.clip_start = 0.035
    data.clip_end = 120.0
    obj = bpy.data.objects.new(name, data)
    obj.matrix_world = look_matrix(loc, target)
    data.dof.use_dof = True
    data.dof.aperture_fstop = fstop
    data.dof.focus_distance = focus if focus is not None else (Vector(target) - Vector(loc)).length
    COL_CAMS.objects.link(obj)
    return obj

cam_general = camera("FM_Cam_General", (0, 1.68, 9.6), (0, 1.55, -8.8), 30.0, 5.6)
cam_entrance = camera("FM_Cam_Entrada", (2.15, 1.86, 10.7), (-0.55, 1.25, -7.5), 35.0, 4.0)
cam_door = camera("FM_Cam_Puerta", (0, 1.52, -7.25), (0, 1.45, -10.05), 58.0, 2.8)
cam_detail = camera("FM_Cam_Detalle", (1.35, 1.18, 3.55), (-2.45, 2.85, 1.2), 72.0, 2.2, 3.0)
cam_cine = camera("FM_Cam_Cine", (0.82, 1.25, 5.65), (0, 1.85, -9.4), 24.0, 2.0)

# ---------------------------------------------------------------------------
# Mundo: niebla volumétrica y fondo
# ---------------------------------------------------------------------------
world = bpy.data.worlds.new("FM_Corridor_World")
world.use_nodes = True
nt = world.node_tree
nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputWorld')
bg = nt.nodes.new('ShaderNodeBackground')
bg.inputs['Color'].default_value = (0.004, 0.008, 0.010, 1.0)
bg.inputs['Strength'].default_value = 0.22
vol = nt.nodes.new('ShaderNodeVolumeScatter')
vol.inputs['Color'].default_value = (0.35, 0.47, 0.48, 1.0)
vol.inputs['Density'].default_value = 0.010
vol.inputs['Anisotropy'].default_value = 0.38
nt.links.new(bg.outputs[0], out.inputs['Surface'])
nt.links.new(vol.outputs[0], out.inputs['Volume'])
scene.world = world

# Cámara activa y guardado sin sobrescribir ningún .blend existente.
scene.camera = cam_general
blend_path = os.path.join(OUT_DIR, "FM_CORRIDOR_FINAL.blend")
version = 2
while os.path.exists(blend_path):
    blend_path = os.path.join(OUT_DIR, "FM_CORRIDOR_FINAL_v%d.blend" % version)
    version += 1
bpy.ops.wm.save_as_mainfile(filepath=blend_path, check_existing=False)

print("FM_CORRIDOR_BUILD_OK")
print("BLEND:", blend_path)
print("OBJECTS:", len(scene.objects))
print("MATERIALS:", len(bpy.data.materials))

# Preview rápido para evaluar composición antes de los renders finales.
scene.camera = cam_general
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
try:
    scene.eevee.taa_render_samples = 32
except Exception:
    pass
preview_path = os.path.join(RENDER_DIR, "_preview_general_v4.png")
pv = 4
while os.path.exists(preview_path):
    pv += 1
    preview_path = os.path.join(RENDER_DIR, "_preview_general_v%d.png" % pv)
scene.render.filepath = preview_path
bpy.ops.render.render(write_still=True)
print("PREVIEW:", scene.render.filepath)
