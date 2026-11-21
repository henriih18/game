"""El Coleccionista — pipeline de escultura, retopología y bake.

Genera un modelo game-ready desde cero en un .blend aparte:
  1. Bloque orgánico con metaballs (torso, joroba, extremidades, manos, cabeza).
  2. Detalle superficial con Displace (pliegues y poros).
  3. Retopología por decimación a ~40k tris y UVs Smart Project.
  4. Bake de normal y AO desde el high-poly.
  5. Equipo: mochila, bidones, correas, llaves, farol y ojos.
  6. Export GLB y render de revisión.

Uso:
  blender -b --factory-startup --python scripts/fm/fm_collector_sculpt.py
"""

import math
import os
import sys

import bpy
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
BLEND = os.path.join(ROOT, "nexus/nivel_01/FM_COLLECTOR_SCULPT.blend")
GLB = os.path.join(ROOT, "assets/models/fm/collector_creature.glb")
TEX_DIR = os.path.join(ROOT, "assets/art/fm/collector")
RENDER = "/tmp/opencode/collector_sculpt.png"

os.makedirs(TEX_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 8
    scene.render.film_transparent = False
    scene.world = bpy.data.worlds.new("CollectorWorld")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.035, 0.04, 0.045, 1.0)
        bg.inputs["Strength"].default_value = 0.6


def collection(name):
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col


def link_to(ob, col):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    col.objects.link(ob)


def material(name, color, rough=0.6, metal=0.0, emission=None, strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
    return mat


def box(name, center, size, mat, bevel=0.0, segments=2, rot=(0, 0, 0), col=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    ob = bpy.context.object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.rotation_euler = rot
    if bevel > 0:
        mod = ob.modifiers.new("Bevel", "BEVEL")
        mod.width = bevel
        mod.segments = segments
        mod.limit_method = "ANGLE"
    ob.data.materials.append(mat)
    if col:
        link_to(ob, col)
    return ob


def cyl(name, center, radius, depth, mat, axis="Z", segments=24, rot=(0, 0, 0), col=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=segments, radius=radius,
                                        depth=depth, location=center)
    ob = bpy.context.object
    ob.name = name
    if axis == "X":
        ob.rotation_euler = (0, math.radians(90), 0)
    elif axis == "Y":
        ob.rotation_euler = (math.radians(90), 0, 0)
    if rot != (0, 0, 0):
        ob.rotation_euler = rot
    ob.data.materials.append(mat)
    if col:
        link_to(ob, col)
    return ob




def segment(name, a, b, r1, r2, mat, verts=16, col=None):
    """Cilindro/cono alineado entre dos puntos (mangas y perneras)."""
    from mathutils import Vector
    va, vb = Vector(a), Vector(b)
    d = vb - va
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2,
                                    depth=d.length, location=(va + vb) * 0.5)
    ob = bpy.context.object
    ob.name = name
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion = d.to_track_quat("Z", "Y")
    ob.data.materials.append(mat)
    if col:
        link_to(ob, col)
    return ob


def sphere(name, center, radius, mat, scale=(1, 1, 1), segments=32, rings=16, col=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings,
                                        radius=radius, location=center)
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(mat)
    if col:
        link_to(ob, col)
    return ob


def cone(name, center, radius1, radius2, depth, mat, verts=24, scale=(1,1,1), col=None):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=radius1,
                                    radius2=radius2, depth=depth,
                                    location=center)
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    ob.data.materials.append(mat)
    if col:
        link_to(ob, col)
    return ob


def shade_smooth(ob, angle=35):
    for poly in ob.data.polygons:
        poly.use_smooth = True
    # Blender 5.2 eliminó Mesh.use_auto_smooth. El operador de sombreado por
    # ángulo marca aristas sharp y mantiene las superficies curvas suaves.
    try:
        with bpy.context.temp_override(
                object=ob, active_object=ob,
                selected_objects=[ob], selected_editable_objects=[ob]):
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(angle))
    except Exception as exc:
        print("SHADE_SMOOTH_FALLBACK", ob.name, exc)


# ---------------------------------------------------------------------------
# Bloque orgánico
# ---------------------------------------------------------------------------

def build_body_high(col):
    """Cuerpo base continuo: esqueleto + Skin + remesh voxel.

    Las metaballs dejaban las extremidades como cuentas separadas. Un
    esqueleto con Skin produce un volumen continuo y el remesh voxel lo
    fusiona en una sola superficie orgánica antes del displace y la
    retopología.
    """
    verts = []
    edges = []
    radii = []

    def add(co, rx, rz=None):
        verts.append(co)
        radii.append((rx, rz if rz is not None else rx))
        return len(verts) - 1

    pelvis = add((0.0, 0.0, 1.00), 0.21)
    spine1 = add((0.0, -0.03, 1.24), 0.20)
    spine2 = add((0.0, -0.10, 1.46), 0.24)
    chest = add((0.0, -0.18, 1.64), 0.27)
    neck = add((0.0, -0.16, 1.96), 0.11)
    head = add((0.0, -0.12, 2.14), 0.17)
    edges += [(pelvis, spine1), (spine1, spine2), (spine2, chest),
              (chest, neck), (neck, head)]
    for side in (-1, 1):
        shoulder = add((0.41 * side, -0.15, 1.72), 0.14)
        elbow = add((0.55 * side, -0.08, 1.32), 0.10)
        wrist = add((0.61 * side, 0.02, 0.92), 0.070)
        hand = add((0.63 * side, 0.04, 0.80), 0.080)
        edges += [(chest, shoulder), (shoulder, elbow), (elbow, wrist),
                  (wrist, hand)]
        hip = add((0.21 * side, 0.0, 0.98), 0.16)
        knee = add((0.25 * side, -0.02, 0.52), 0.120)
        ankle = add((0.27 * side, 0.0, 0.12), 0.08)
        foot = add((0.27 * side, -0.16, 0.07), 0.085)
        edges += [(pelvis, hip), (hip, knee), (knee, ankle), (ankle, foot)]

    me = bpy.data.meshes.new("CollectorBody")
    me.from_pydata(verts, edges, [])
    me.update()
    body = bpy.data.objects.new("Collector_Body_High", me)
    link_to(body, col)
    bpy.context.view_layer.objects.active = body
    body.select_set(True)
    skin = body.modifiers.new("Skin", "SKIN")
    skin.use_smooth_shade = True
    bpy.context.view_layer.update()
    layer = me.skin_vertices[0].data
    for i, (rx, rz) in enumerate(radii):
        layer[i].radius = (rx, rz)
    layer[pelvis].use_root = True
    bpy.ops.object.modifier_apply(modifier=skin.name)

    sub = body.modifiers.new("Sub", "SUBSURF")
    sub.levels = 2
    sub.render_levels = 2
    bpy.ops.object.modifier_apply(modifier=sub.name)

    # Cabeza, mandíbula, manos y pies se unen antes del remesh para que el
    # voxel los fusione con el cuerpo.
    parts = [body]
    def part(name, center, radius, scale, mat):
        ob = sphere(name, center, radius, mat, scale=scale, col=col)
        parts.append(ob)
    skin_mat = material("M_Collector_Preview", (0.55, 0.51, 0.46), 0.82)
    part("Head", (0.0, -0.12, 2.14), 0.165, (0.92, 1.02, 1.18), skin_mat)
    part("Jaw", (0.0, -0.20, 2.00), 0.105, (0.80, 0.92, 0.62), skin_mat)
    part("Brow", (0.0, -0.23, 2.18), 0.105, (1.0, 0.55, 0.35), skin_mat)
    for side in (-1, 1):
        part("Ear_%d" % side, (0.16 * side, -0.11, 2.12), 0.05,
             (0.55, 0.9, 1.1), skin_mat)
        part("Hand_%d" % side, (0.63 * side, 0.04, 0.80), 0.085,
             (1.05, 1.45, 0.82), skin_mat)
        for i in range(4):
            part("Finger_%d_%d" % (side, i),
                 (0.63 * side + (i - 1.5) * 0.035, -0.04, 0.72),
                 0.025, (1.0, 1.0, 2.2), skin_mat)
        part("Thumb_%d" % side, (0.69 * side, 0.02, 0.78), 0.03,
             (1.0, 1.4, 1.1), skin_mat)
        part("Foot_%d" % side, (0.27 * side, -0.16, 0.08), 0.09,
             (0.95, 1.85, 0.55), skin_mat)
        for i in range(3):
            part("Toe_%d_%d" % (side, i),
                 (0.27 * side + (i - 1) * 0.045, -0.31, 0.06),
                 0.028, (1.0, 1.2, 0.8), skin_mat)

    bpy.ops.object.select_all(action="DESELECT")
    for ob in parts:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.join()
    body = bpy.context.object
    body.name = "Collector_Body_High"

    rem = body.modifiers.new("Fuse", "REMESH")
    rem.mode = "VOXEL"
    rem.voxel_size = 0.014
    rem.use_smooth_shade = True
    bpy.ops.object.modifier_apply(modifier=rem.name)

    smooth = body.modifiers.new("Relax", "SMOOTH")
    smooth.factor = 0.5
    smooth.iterations = 3
    bpy.ops.object.modifier_apply(modifier=smooth.name)

    # Pliegues y piel.
    tex1 = bpy.data.textures.new("SkinFine", type="CLOUDS")
    tex1.noise_scale = 0.055
    tex1.noise_depth = 3
    tex1.noise_basis = "BLENDER_ORIGINAL"
    d1 = body.modifiers.new("SkinFine", "DISPLACE")
    d1.texture = tex1
    d1.strength = 0.007
    d1.mid_level = 0.5

    tex2 = bpy.data.textures.new("SkinWide", type="CLOUDS")
    tex2.noise_scale = 0.24
    tex2.noise_depth = 2
    d2 = body.modifiers.new("SkinWide", "DISPLACE")
    d2.texture = tex2
    d2.strength = 0.012

    bpy.ops.object.modifier_apply(modifier=d1.name)
    bpy.ops.object.modifier_apply(modifier=d2.name)
    shade_smooth(body, 38)
    return body


def build_low(body, col):
    low = body.copy()
    low.data = body.data.copy()
    low.name = "Collector_Body"
    col.objects.link(low)
    body.hide_render = True
    body.hide_set(True)

    # Retopología game-ready.
    tri = sum(len(p.vertices) - 2 for p in low.data.polygons)
    ratio = min(0.9, 42000.0 / max(1, tri))
    mod = low.modifiers.new("Retopo", "DECIMATE")
    mod.ratio = ratio
    mod.use_collapse_triangulate = True
    bpy.context.view_layer.objects.active = low
    low.select_set(True)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles(threshold=0.0005)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.uv.smart_project(angle_limit=math.radians(66),
                             island_margin=0.015)
    bpy.ops.object.mode_set(mode="OBJECT")
    shade_smooth(low, 38)
    return low


# ---------------------------------------------------------------------------
# Texturas y bake
# ---------------------------------------------------------------------------

def image(name, path, color=False):
    img = bpy.data.images.get(name)
    if img:
        return img
    img = bpy.data.images.new(name, 2048, 2048, alpha=False)
    img.filepath_raw = path
    img.file_format = "PNG"
    img.colorspace_settings.name = "sRGB" if color else "Non-Color"
    return img


def bake_maps(high, low):
    normal_img = image("T_Collector_N", os.path.join(TEX_DIR, "T_Collector_N.png"))
    ao_img = image("T_Collector_AO", os.path.join(TEX_DIR, "T_Collector_AO.png"))

    mat = bpy.data.materials.new("M_Collector_Bake")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = normal_img
    tex.select = True
    nt.nodes.active = tex
    low.data.materials.clear()
    low.data.materials.append(mat)

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 1
    scene.render.bake.margin = 16
    scene.render.bake.use_clear = True

    # `build_low` oculta el high después de copiarlo; el bake selected-to-active
    # necesita que ambas mallas estén visibles y seleccionables.
    high.hide_set(False)
    high.hide_viewport = False
    high.hide_render = False
    low.hide_set(False)
    low.hide_viewport = False
    low.hide_render = False
    bpy.context.view_layer.update()

    bpy.ops.object.select_all(action="DESELECT")
    high.select_set(True)
    low.select_set(True)
    bpy.context.view_layer.objects.active = low
    bpy.ops.object.bake(type="NORMAL", use_selected_to_active=True,
                        cage_extrusion=0.025, normal_space="TANGENT")
    normal_img.filepath_raw = os.path.join(TEX_DIR, "T_Collector_N.png")
    normal_img.file_format = "PNG"
    normal_img.save()

    tex.image = ao_img
    nt.nodes.active = tex
    scene.cycles.samples = 24
    # En Blender 5.x la distancia de AO vive en world.light_settings, no es
    # un argumento del operador de bake.
    if scene.world is not None:
        scene.world.light_settings.distance = 0.35
    bpy.ops.object.bake(type="AO", use_selected_to_active=True,
                        cage_extrusion=0.025)
    ao_img.filepath_raw = os.path.join(TEX_DIR, "T_Collector_AO.png")
    ao_img.file_format = "PNG"
    ao_img.save()
    # El high solo se necesita para el bake. Si queda visible, tapa al low
    # con el material de preview y el render final no muestra la piel.
    high.hide_render = True
    high.hide_set(True)
    low.hide_render = False
    low.hide_set(False)
    return normal_img, ao_img


def skin_material(normal_img, ao_img):
    mat = bpy.data.materials.new("M_Collector_Skin")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = 0.72

    # Albedo limpio de piel pálida: la textura de carne original tiene un
    # moteado de camuflaje que a escala de juego parece ruido. El detalle
    # viene del mapa normal horneado y de la rugosidad.
    bsdf.inputs["Base Color"].default_value = (0.10, 0.075, 0.055, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.78
    t_n = nt.nodes.new("ShaderNodeTexImage")
    t_n.image = normal_img
    nm = nt.nodes.new("ShaderNodeNormalMap")
    nm.inputs["Strength"].default_value = 0.35
    nt.links.new(t_n.outputs["Color"], nm.inputs["Color"])
    nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


# ---------------------------------------------------------------------------
# Equipo
# ---------------------------------------------------------------------------

def build_gear(col):
    leather = material("M_Collector_Leather", (0.008, 0.006, 0.004), 0.78)
    canvas = material("M_Collector_Canvas", (0.018, 0.014, 0.010), 0.92)
    rope = material("M_Collector_Rope", (0.04, 0.033, 0.024), 0.95)
    steel = material("M_Collector_Steel", (0.16, 0.17, 0.17), 0.42, 0.9)
    brass = material("M_Collector_Brass", (0.44, 0.31, 0.12), 0.34, 0.95)
    glow = material("M_Collector_Lantern", (1.0, 0.62, 0.22), 0.4,
                    emission=(1.0, 0.55, 0.18), strength=6.0)
    eye = material("M_Collector_Eye", (0.25, 0.16, 0.06), 0.3,
                   emission=(1.0, 0.45, 0.12), strength=0.35)
    dark = material("M_Collector_Dark", (0.015, 0.012, 0.010), 0.85)
    bone = material("M_Collector_Bone", (0.62, 0.56, 0.44), 0.70)
    skin = material("M_Collector_Skin", (0.55, 0.51, 0.46), 0.82)

    # Mochila: saco de lona deformado + rollo + bidones.
    sack = sphere("Collector_Pack", (0, 0.34, 1.66), 0.34, canvas,
                  (1.05, 0.80, 1.25), segments=40, rings=24, col=col)
    tex = bpy.data.textures.new("CanvasNoise", type="CLOUDS")
    tex.noise_scale = 0.10
    tex.noise_depth = 2
    d = sack.modifiers.new("Canvas", "DISPLACE")
    d.texture = tex
    d.strength = 0.020
    bpy.context.view_layer.objects.active = sack
    bpy.ops.object.modifier_apply(modifier=d.name)
    shade_smooth(sack, 45)
    cyl("Collector_Roll", (0, 0.44, 1.94), 0.11, 0.62, rope, axis="X",
        segments=24, col=col)
    for s in (-1, 1):
        cyl("Collector_Drum_%s" % s, (0.30 * s, 0.30, 1.47), 0.115, 0.42,
            steel, segments=24, col=col)
        for z in (1.31, 1.45, 1.59):
            cyl("Collector_DrumBand_%s_%s" % (s, z), (0.30 * s, 0.30, z),
                0.122, 0.025, brass, segments=24, col=col)

    # Correas del arnés y cinturón.
    for s in (-1, 1):
        box("Collector_Strap_%s" % s, (0.19 * s, -0.28, 1.66),
            (0.062, 0.035, 0.64), leather, bevel=0.008, segments=3,
            rot=(0, 0, math.radians(-6 * s)), col=col)
        box("Collector_Buckle_%s" % s, (0.19 * s, -0.305, 1.52),
            (0.075, 0.018, 0.075), brass, bevel=0.004, segments=2, col=col)
    box("Collector_Belt", (0, -0.02, 1.12), (0.60, 0.36, 0.075),
        leather, bevel=0.008, segments=2, col=col)
    box("Collector_Buckle", (0, -0.21, 1.12), (0.095, 0.022, 0.085),
        brass, bevel=0.004, segments=2, col=col)

    # Saquitos y llaves.
    for s in (-1, 1):
        sphere("Collector_Pouch_%s" % s, (0.40 * s, -0.02, 1.00), 0.11,
               canvas, (1.0, 0.85, 1.1), segments=24, rings=16, col=col)
        box("Collector_PouchFlap_%s" % s, (0.40 * s, -0.10, 1.06),
            (0.13, 0.03, 0.08), leather, bevel=0.006, segments=2, col=col)
    ring = cyl("Collector_KeyRing", (0.28, -0.22, 1.02), 0.055, 0.012,
               brass, axis="Y", segments=24, col=col)
    for i in range(5):
        a = math.radians(-40 + i * 20)
        box("Collector_Key_%d" % i,
            (0.28 + math.sin(a) * 0.075, -0.23, 1.02 - math.cos(a) * 0.075),
            (0.012, 0.006, 0.085), brass, bevel=0.002, segments=2,
            rot=(0, 0, a), col=col)

    # Farol en el costado izquierdo.
    lx, ly, lz = -0.42, 0.02, 1.28
    box("Collector_LanternBody", (lx, ly, lz), (0.12, 0.12, 0.20),
        steel, bevel=0.008, segments=2, col=col)
    for i in (-1, 0, 1):
        box("Collector_LanternBar_%d" % i, (lx + i * 0.045, ly - 0.062, lz),
            (0.012, 0.012, 0.17), steel, bevel=0.002, segments=1, col=col)
    sphere("Collector_LanternCore", (lx, ly, lz), 0.045, glow,
           segments=20, rings=12, col=col)
    cyl("Collector_LanternHook", (lx, ly + 0.06, lz + 0.14), 0.012, 0.12,
        steel, axis="Y", segments=12, col=col)

    # Ojos emisivos.
    for s in (-1, 1):
        sphere("Collector_EyeSocket_%s" % s, (0.062 * s, -0.255, 2.165),
               0.040, dark, segments=16, rings=10, col=col)
        sphere("Collector_Eye_%s" % s, (0.062 * s, -0.288, 2.165),
               0.016, eye, segments=16, rings=8, col=col)
    # Nariz, boca y dientes.
    sphere("Collector_Nose", (0.0, -0.292, 2.075), 0.026, skin, (0.8, 1.0, 0.9),
           segments=14, rings=8, col=col)
    box("Collector_Mouth", (0.0, -0.286, 2.010), (0.095, 0.018, 0.026),
        dark, bevel=0.004, segments=2, col=col)
    for i in range(6):
        box("Collector_Tooth_%d" % i,
            ((i - 2.5) * 0.016, -0.295, 2.022), (0.011, 0.008, 0.018),
            bone, bevel=0.001, segments=1, col=col)

    # Ropa y máscara de saqueador: ocultan el cuerpo liso y dan la
    # silueta cargada y amenazante de la referencia.
    sphere("Collector_Hood", (0.0, -0.02, 2.16), 0.205, canvas,
           (1.04, 1.16, 1.02), segments=28, rings=16, col=col)
    sphere("Collector_CloakChest", (0.0, -0.10, 1.62), 0.355, canvas,
           (1.10, 0.78, 0.86), segments=28, rings=16, col=col)
    sphere("Collector_CloakSkirt", (0.0, -0.06, 1.28), 0.315, canvas,
           (1.02, 0.70, 0.82), segments=28, rings=16, col=col)
    for s in (-1, 1):
        sphere("Collector_ShoulderPad_%s" % s, (0.40 * s, -0.06, 1.74),
               0.145, leather, (1.15, 0.85, 0.62), segments=24, rings=14,
               col=col)
        sphere("Collector_Glove_%s" % s, (0.63 * s, 0.02, 0.79), 0.090,
               leather, (0.95, 1.25, 0.95), segments=20, rings=12, col=col)
        box("Collector_Boot_%s" % s, (0.27 * s, -0.10, 0.075),
            (0.18, 0.34, 0.16), leather, bevel=0.010, segments=3, col=col)
    # Máscara metálica con goggles y respirador.
    box("Collector_Mask", (0.0, -0.320, 2.13), (0.225, 0.055, 0.175),
        steel, bevel=0.014, segments=3, col=col)
    for s in (-1, 1):
        cyl("Collector_GoggleRing_%s" % s, (0.058 * s, -0.335, 2.165),
            0.046, 0.030, steel, axis="Y", segments=24, col=col)
        sphere("Collector_GoggleLens_%s" % s, (0.058 * s, -0.352, 2.165),
               0.031, eye, (1.0, 1.0, 0.80), segments=20, rings=12, col=col)
    cyl("Collector_Respirator", (0.0, -0.370, 2.045), 0.050, 0.050, steel,
        axis="Y", segments=24, col=col)
    cyl("Collector_RespiratorGrill", (0.0, -0.398, 2.045), 0.036, 0.012,
        dark, axis="Y", segments=20, col=col)
    # Manguera corrugada del respirador a la mochila.
    for i in range(6):
        t = i / 5.0
        x = 0.085 * math.sin(t * math.pi)
        y = -0.34 + t * 0.62
        z = 2.00 - t * 0.18
        tail = (0.10, 0.11, 0.11) if i % 2 == 0 else (0.085, 0.095, 0.095)
        sphere("Collector_Hose_%d" % i, (x, y, z), 0.036,
               dark, (1.0, 1.0, 0.72), segments=16, rings=10, col=col)
    # Harapos colgando de la túnica.
    for i in range(6):
        ang = math.radians(-70 + i * 28)
        box("Collector_Rag_%d" % i,
            (0.26 * math.sin(ang), 0.03 + 0.22 * math.cos(ang), 1.08),
            (0.075, 0.012, 0.24 + 0.03 * (i % 3)), canvas,
            bevel=0.003, segments=1, rot=(0, 0, ang), col=col)

    # Ropa de saqueador: cubre torso, brazos y piernas; deja visibles
    # únicamente guantes, botas y máscara.
    sphere("Collector_Coat", (0.0, -0.04, 1.42), 0.34, canvas,
           (1.18, 0.88, 1.78), segments=32, rings=20, col=col)
    sphere("Collector_Mantle", (0.0, -0.02, 1.78), 0.40, canvas,
           (1.12, 0.82, 0.52), segments=28, rings=16, col=col)
    sphere("Collector_HoodOuter", (0.0, -0.01, 2.15), 0.23, canvas,
           (1.10, 1.10, 1.05), segments=28, rings=18, col=col)
    for s in (-1, 1):
        segment("Collector_Sleeve_%s" % s,
                (0.41 * s, -0.15, 1.72), (0.55 * s, -0.08, 1.32),
                0.170, 0.130, canvas, col=col)
        segment("Collector_SleeveLow_%s" % s,
                (0.55 * s, -0.08, 1.32), (0.61 * s, 0.02, 0.92),
                0.130, 0.100, canvas, col=col)
        segment("Collector_Pant_%s" % s,
                (0.21 * s, 0.0, 0.98), (0.25 * s, -0.02, 0.52),
                0.190, 0.150, canvas, col=col)
        segment("Collector_PantLow_%s" % s,
                (0.25 * s, -0.02, 0.52), (0.27 * s, 0.0, 0.14),
                0.150, 0.105, canvas, col=col)
        box("Collector_Strap_%s" % s, (0.17 * s, -0.315, 1.62),
            (0.070, 0.030, 0.56), leather, bevel=0.006, segments=2,
            rot=(0, 0, 0.10 * s), col=col)
        box("Collector_Pouch_%s" % s, (0.38 * s, -0.24, 1.18),
            (0.16, 0.12, 0.19), leather, bevel=0.012, segments=3, col=col)
    box("Collector_OuterBelt", (0.0, -0.345, 1.16), (0.56, 0.045, 0.10),
        leather, bevel=0.008, segments=2, col=col)
    box("Collector_Buckle", (0.0, -0.372, 1.16), (0.075, 0.024, 0.075),
        brass, bevel=0.006, segments=2, col=col)


# ---------------------------------------------------------------------------
# Revisión y export
# ---------------------------------------------------------------------------

def add_review(col):
    ground = box("Review_Ground", (0, 0, -0.01), (8, 8, 0.02),
                 material("M_Review_Ground", (0.03, 0.032, 0.03), 0.9),
                 col=col)
    ground.hide_render = False

    cam_data = bpy.data.cameras.new("ReviewCam")
    cam = bpy.data.objects.new("ReviewCam", cam_data)
    col.objects.link(cam)
    cam.location = (3.2, -6.4, 1.6)
    cam.rotation_euler = (math.radians(86), 0, math.radians(28))
    cam_data.lens = 50
    bpy.context.scene.camera = cam

    key = bpy.data.lights.new("Key", type="AREA")
    key.energy = 900
    key.size = 3.0
    key.color = (1.0, 0.86, 0.70)
    ko = bpy.data.objects.new("Key", key)
    col.objects.link(ko)
    ko.location = (2.8, -3.4, 4.0)
    ko.rotation_euler = (math.radians(40), 0, math.radians(35))

    fill = bpy.data.lights.new("Fill", type="AREA")
    fill.energy = 350
    fill.size = 4.0
    fill.color = (0.62, 0.76, 1.0)
    fo = bpy.data.objects.new("Fill", fill)
    col.objects.link(fo)
    fo.location = (-3.6, -2.0, 2.6)
    fo.rotation_euler = (math.radians(65), 0, math.radians(-50))

    rim = bpy.data.lights.new("Rim", type="AREA")
    rim.energy = 600
    rim.size = 2.5
    rim.color = (0.70, 0.82, 1.0)
    ro = bpy.data.objects.new("Rim", rim)
    col.objects.link(ro)
    ro.location = (-1.2, 3.4, 3.0)
    ro.rotation_euler = (math.radians(115), 0, math.radians(190))

    scene = bpy.context.scene
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = RENDER
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"


def main():
    reset()
    col = collection("COLLECTOR")
    high = build_body_high(col)
    low = build_low(high, col)
    normal_img, ao_img = bake_maps(high, low)
    skin = skin_material(normal_img, ao_img)
    low.data.materials.clear()
    low.data.materials.append(skin)
    build_gear(col)
    add_review(col)

    # Aplicar modificadores pendientes y exportar.
    bpy.ops.object.select_all(action="DESELECT")
    for ob in col.objects:
        if ob.type == "MESH" and not ob.hide_render:
            ob.select_set(True)
    bpy.context.view_layer.objects.active = low
    bpy.ops.export_scene.gltf(
        filepath=GLB,
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=True,
        export_animations=False,
        export_cameras=False,
        export_lights=False,
        export_materials="EXPORT",
        export_image_format="AUTO",
        export_texcoords=True,
        export_normals=True,
    )

    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    bpy.ops.render.render(write_still=True)

    tris = sum(len(p.vertices) - 2 for p in low.data.polygons)
    total = sum(sum(len(p.vertices) - 2 for p in o.data.polygons)
                for o in col.objects if o.type == "MESH" and not o.hide_render)
    print("COLLECTOR_SCULPT body_tris=%d total_tris=%d glb=%s" %
          (tris, total, GLB))
    print("COLLECTOR_SCULPT saved=%s" % BLEND)


if __name__ == "__main__":
    main()
