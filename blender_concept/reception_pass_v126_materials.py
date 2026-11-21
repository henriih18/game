"""Pase de materiales de la RECEPCIÓN del Nivel 1 (v126).

Solo toca objetos NEXUS_V05_RECEPCION_* y los decals de desastre de la
recepción. No modifica ni mueve archivos de la biblioteca `assets/`.

Uso: se ejecuta dentro de Blender con la escena NEXUS_L1_V05 abierta.
"""

import os

import bpy

ROOT = "/home/riyo/Documentos/game"
ASSETS = os.path.join(ROOT, "assets")

TEX = {
    "wall_diff": "texturas/Pintura y paredes/worn_plaster_wall_2k.blend/textures/worn_plaster_wall_diff_2k.jpg",
    "wall_rough": "texturas/Pintura y paredes/worn_plaster_wall_2k.blend/textures/worn_plaster_wall_rough_2k.exr",
    "wall_nor": "texturas/Pintura y paredes/worn_plaster_wall_2k.blend/textures/worn_plaster_wall_nor_gl_2k.exr",
    "panel_diff": "texturas/Pintura y paredes/factory_wall_2k.blend/textures/factory_wall_diff_2k.jpg",
    "panel_rough": "texturas/Pintura y paredes/factory_wall_2k.blend/textures/factory_wall_rough_2k.jpg",
    "panel_nor": "texturas/Pintura y paredes/factory_wall_2k.blend/textures/factory_wall_nor_gl_2k.exr",
    "ceil_diff": "texturas/Hormigon y cemento/dirty_concrete_2k.blend/textures/dirty_concrete_diff_2k.jpg",
    "ceil_rough": "texturas/Hormigon y cemento/dirty_concrete_2k.blend/textures/dirty_concrete_rough_2k.jpg",
    "ceil_nor": "texturas/Hormigon y cemento/dirty_concrete_2k.blend/textures/dirty_concrete_nor_gl_2k.exr",
    "floor_diff": "texturas/Hormigon y cemento/worn_concrete_floor_2k.blend/textures/worn_concrete_floor_diff_2k.jpg",
    "floor_rough": "texturas/Hormigon y cemento/worn_concrete_floor_2k.blend/textures/worn_concrete_floor_rough_2k.exr",
    "floor_nor": "texturas/Hormigon y cemento/worn_concrete_floor_2k.blend/textures/worn_concrete_floor_nor_gl_2k.exr",
    "dirt_diff": "texturas/Suciedad y deterioro/dirt_2k.blend/textures/dirt_diff_2k.jpg",
    "dirt_nor": "texturas/Suciedad y deterioro/dirt_2k.blend/textures/dirt_nor_gl_2k.exr",
    "blood": "art/fm/blood_splat.png",
    "hand": "art/fm/handprint.png",
}

FLOOR_Z = -5.8  # cota del suelo de la recepción
RECEP_BOUNDS = ((-20.4, -3.6), (1.4, 12.0), (-6.2, 0.6))  # X, Y, Z del volumen


def in_reception(obj):
    loc = obj.matrix_world.translation
    return all(
        RECEP_BOUNDS[axis][0] <= loc[axis] <= RECEP_BOUNDS[axis][1] for axis in range(3)
    )


def load_image(key, non_color=False):
    path = os.path.join(ASSETS, TEX[key])
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    image = bpy.data.images.load(path, check_existing=True)
    wanted = "Non-Color" if non_color else "sRGB"
    if image.colorspace_settings.name != wanted:
        image.colorspace_settings.name = wanted
    return image


def reset_material(name):
    """Devuelve un material con árbol de nodos vacío y estable."""
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()
    out = tree.nodes.new("ShaderNodeOutputMaterial")
    out.location = (900, 0)
    bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (600, 0)
    tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def _tex(tree, image, loc, non_color_lookup=None):
    tex = tree.nodes.new("ShaderNodeTexImage")
    tex.image = image
    tex.location = loc
    return tex


def build_surface_material(
    name,
    diff_key,
    rough_key,
    nor_key,
    map_scale,
    tint,
    normal_strength,
    rough_range=(0.45, 0.92),
    grime_band=None,
    grime_color=None,
    extra_dirt_key=None,
    extra_dirt_scale=None,
    extra_dirt_strength=0.0,
    saturation=1.0,
):
    """Material PBR con proyección por coordenadas de objeto.

    grime_band=(z_inferior, z_superior, factor_minimo) aplica oscurecimiento
    progresivo cerca del suelo usando la altura real del mundo.
    """
    mat = reset_material(name)
    tree = mat.node_tree
    bsdf = next(n for n in tree.nodes if n.type == "BSDF_PRINCIPLED")

    coord = tree.nodes.new("ShaderNodeTexCoord")
    coord.location = (-1400, 0)
    mapping = tree.nodes.new("ShaderNodeMapping")
    mapping.location = (-1200, 0)
    mapping.inputs["Scale"].default_value = (map_scale, map_scale, map_scale)
    tree.links.new(coord.outputs["Object"], mapping.inputs["Vector"])

    diff = _tex(tree, load_image(diff_key), (-900, 300))
    rough = _tex(tree, load_image(rough_key, True), (-900, 0))
    tree.links.new(mapping.outputs["Vector"], diff.inputs["Vector"])
    tree.links.new(mapping.outputs["Vector"], rough.inputs["Vector"])

    color_socket = diff.outputs["Color"]

    if extra_dirt_key and extra_dirt_strength > 0.0:
        dirt_map = tree.nodes.new("ShaderNodeMapping")
        dirt_map.location = (-1200, -400)
        dirt_map.inputs["Scale"].default_value = (
            extra_dirt_scale,
            extra_dirt_scale,
            extra_dirt_scale,
        )
        tree.links.new(coord.outputs["Object"], dirt_map.inputs["Vector"])
        dirt = _tex(tree, load_image(extra_dirt_key), (-900, -400))
        tree.links.new(dirt_map.outputs["Vector"], dirt.inputs["Vector"])
        mix_dirt = tree.nodes.new("ShaderNodeMixRGB")
        mix_dirt.blend_type = "MULTIPLY"
        mix_dirt.location = (-650, 200)
        mix_dirt.inputs["Fac"].default_value = extra_dirt_strength
        tree.links.new(color_socket, mix_dirt.inputs["Color1"])
        tree.links.new(dirt.outputs["Color"], mix_dirt.inputs["Color2"])
        color_socket = mix_dirt.outputs["Color"]

    multiply = tree.nodes.new("ShaderNodeMixRGB")
    multiply.blend_type = "MULTIPLY"
    multiply.location = (-420, 300)
    multiply.inputs["Fac"].default_value = 1.0
    multiply.inputs["Color2"].default_value = (*tint, 1.0)
    tree.links.new(color_socket, multiply.inputs["Color1"])
    color_socket = multiply.outputs["Color"]

    if saturation != 1.0:
        desat = tree.nodes.new("ShaderNodeHueSaturation")
        desat.location = (-300, 300)
        desat.inputs["Saturation"].default_value = saturation
        tree.links.new(color_socket, desat.inputs["Color"])
        color_socket = desat.outputs["Color"]

    if grime_band is not None:
        z_low, z_high, factor = grime_band
        geometry = tree.nodes.new("ShaderNodeNewGeometry")
        geometry.location = (-900, 600)
        separate = tree.nodes.new("ShaderNodeSeparateXYZ")
        separate.location = (-700, 600)
        tree.links.new(geometry.outputs["Position"], separate.inputs["Vector"])
        ramp = tree.nodes.new("ShaderNodeMapRange")
        ramp.location = (-520, 600)
        ramp.inputs["From Min"].default_value = z_low
        ramp.inputs["From Max"].default_value = z_high
        ramp.inputs["To Min"].default_value = factor
        ramp.inputs["To Max"].default_value = 1.0
        ramp.clamp = True
        tree.links.new(separate.outputs["Z"], ramp.inputs["Value"])
        grime = tree.nodes.new("ShaderNodeMixRGB")
        grime.blend_type = "MULTIPLY"
        grime.location = (-200, 300)
        grime.inputs["Fac"].default_value = 1.0
        gc = grime_color or (0.55, 0.53, 0.48, 1.0)
        tree.links.new(color_socket, grime.inputs["Color1"])
        # La rampa aporta un escalar; se multiplica por el tono de suciedad
        scale_gc = tree.nodes.new("ShaderNodeMixRGB")
        scale_gc.blend_type = "MULTIPLY"
        scale_gc.location = (-380, 500)
        scale_gc.inputs["Fac"].default_value = 1.0
        scale_gc.inputs["Color1"].default_value = gc
        tree.links.new(ramp.outputs["Result"], scale_gc.inputs["Color2"])
        tree.links.new(scale_gc.outputs["Color"], grime.inputs["Color2"])
        color_socket = grime.outputs["Color"]

    tree.links.new(color_socket, bsdf.inputs["Base Color"])

    rough_range_node = tree.nodes.new("ShaderNodeMapRange")
    rough_range_node.location = (-420, 0)
    rough_range_node.inputs["To Min"].default_value = rough_range[0]
    rough_range_node.inputs["To Max"].default_value = rough_range[1]
    tree.links.new(rough.outputs["Color"], rough_range_node.inputs["Value"])
    tree.links.new(rough_range_node.outputs["Result"], bsdf.inputs["Roughness"])

    if nor_key:
        nor = _tex(tree, load_image(nor_key, True), (-900, -300))
        tree.links.new(mapping.outputs["Vector"], nor.inputs["Vector"])
        normal_map = tree.nodes.new("ShaderNodeNormalMap")
        normal_map.location = (-420, -300)
        normal_map.inputs["Strength"].default_value = normal_strength
        tree.links.new(nor.outputs["Color"], normal_map.inputs["Color"])
        tree.links.new(normal_map.outputs["Normal"], bsdf.inputs["Normal"])

    bsdf.inputs["Metallic"].default_value = 0.0
    return mat


def build_simple_material(name, color, roughness, metallic=0.0):
    mat = reset_material(name)
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def build_decal_material(name, image_key, tint, alpha, roughness):
    """Decal con textura y alfa; sin material transparente previo."""
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()
    out = tree.nodes.new("ShaderNodeOutputMaterial")
    out.location = (600, 0)
    bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (300, 0)
    tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    uv = tree.nodes.new("ShaderNodeTexCoord")
    uv.location = (-600, 0)
    tex = _tex(tree, load_image(image_key), (-400, 0))
    tree.links.new(uv.outputs["UV"], tex.inputs["Vector"])

    mix = tree.nodes.new("ShaderNodeMixRGB")
    mix.blend_type = "MULTIPLY"
    mix.location = (-120, 100)
    mix.inputs["Fac"].default_value = 1.0
    mix.inputs["Color2"].default_value = (*tint, 1.0)
    tree.links.new(tex.outputs["Color"], mix.inputs["Color1"])
    tree.links.new(mix.outputs["Color"], bsdf.inputs["Base Color"])

    alpha_mix = tree.nodes.new("ShaderNodeMath")
    alpha_mix.operation = "MULTIPLY"
    alpha_mix.location = (-120, -200)
    alpha_mix.inputs[1].default_value = alpha
    tree.links.new(tex.outputs["Alpha"], alpha_mix.inputs[0])
    tree.links.new(alpha_mix.outputs["Value"], bsdf.inputs["Alpha"])

    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = 0.0

    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = "DITHERED"
    mat.use_backface_culling = False
    return mat


def ensure_planar_uv(obj):
    """Proyección planar normalizada 0-1 sobre el plano local dominante."""
    mesh = obj.data
    if not mesh.uv_layers:
        mesh.uv_layers.new(name="UVMap")
    uv_layer = mesh.uv_layers.active
    coords = [v.co for v in mesh.vertices]
    dims = [max(c[i] for c in coords) - min(c[i] for c in coords) for i in range(3)]
    flat = dims.index(min(dims))
    axes = [axis for axis in range(3) if axis != flat]
    lo = [min(c[a] for c in coords) for a in axes]
    span = [max(dims[a], 1e-6) for a in axes]
    for poly in mesh.polygons:
        for loop_index in poly.loop_indices:
            vert_index = mesh.loops[loop_index].vertex_index
            co = mesh.vertices[vert_index].co
            u = (co[axes[0]] - lo[0]) / span[0]
            v = (co[axes[1]] - lo[1]) / span[1]
            try:
                uv_layer.data[loop_index].uv = (u, v)
            except AttributeError:
                uv_layer.data[loop_index].vector = (u, v)


def assign(obj, material):
    obj.data.materials.clear()
    obj.data.materials.append(material)
    obj.data.materials[0] = material


def main():
    wall = build_surface_material(
        "NEXUS_V05_MAT_Rec_Wall",
        "wall_diff",
        "wall_rough",
        "wall_nor",
        map_scale=0.30,
        tint=(0.34, 0.37, 0.35),
        normal_strength=0.40,
        rough_range=(0.60, 0.95),
        grime_band=(FLOOR_Z, FLOOR_Z + 1.8, 0.35),
        grime_color=(0.42, 0.40, 0.35, 1.0),
        saturation=0.45,
    )
    ceiling = build_surface_material(
        "NEXUS_V05_MAT_Rec_Ceiling",
        "ceil_diff",
        "ceil_rough",
        "ceil_nor",
        map_scale=0.20,
        tint=(0.24, 0.25, 0.24),
        normal_strength=0.15,
        rough_range=(0.80, 1.0),
        saturation=0.50,
    )
    floor = build_surface_material(
        "NEXUS_V05_MAT_Rec_Floor",
        "floor_diff",
        "floor_rough",
        "floor_nor",
        map_scale=0.26,
        tint=(0.36, 0.37, 0.35),
        normal_strength=0.65,
        rough_range=(0.30, 0.80),
        extra_dirt_key="dirt_diff",
        extra_dirt_scale=0.11,
        extra_dirt_strength=0.45,
        saturation=0.55,
    )
    wainscot = build_surface_material(
        "NEXUS_V05_MAT_Rec_Wainscot",
        "panel_diff",
        "panel_rough",
        "panel_nor",
        map_scale=1.65,
        tint=(0.62, 0.72, 0.64),
        normal_strength=0.85,
        rough_range=(0.42, 0.85),
        saturation=0.55,
    )
    paper = build_simple_material("NEXUS_L1_MAT_Paper", (0.72, 0.70, 0.63), 0.88, 0.0)

    targets = {
        "NEXUS_V05_RECEPCION_WALL_N": wall,
        "NEXUS_V05_RECEPCION_WALL_S_A": wall,
        "NEXUS_V05_RECEPCION_WALL_S_B": wall,
        "NEXUS_V05_RECEPCION_WALL_W": wall,
        "NEXUS_V05_RECEPCION_WALL_E": wall,
        "NEXUS_V05_RECEPCION_LINTEL_S": wall,
        "NEXUS_V05_RECEPCION_ABOVE_S": wall,
        "NEXUS_V05_RECEPCION_CEILING": ceiling,
        "NEXUS_V05_RECEPCION_FLOOR": floor,
        "NEXUS_V05_RECEPCION_BASE": wainscot,
    }
    applied = 0
    for name, material in targets.items():
        obj = bpy.data.objects.get(name)
        if obj is None:
            print("AVISO: falta", name)
            continue
        assign(obj, material)
        applied += 1

    blood = build_decal_material(
        "NEXUS_L1_MAT_Blood", "blood", (0.62, 0.055, 0.035), 1.0, 0.30
    )
    blood_dark = build_decal_material(
        "NEXUS_L1_MAT_Blood_Dark", "blood", (0.30, 0.025, 0.018), 0.92, 0.34
    )
    hand = build_decal_material(
        "NEXUS_L1_MAT_Handprint", "hand", (0.55, 0.045, 0.030), 0.85, 0.36
    )

    decals = 0
    for obj in bpy.data.objects:
        if obj.type != "MESH" or not obj.name.startswith("NEXUS_L1_DIS_"):
            continue
        name = obj.name
        if "BLOOD" in name:
            material = blood_dark if "DARK" in name else blood
            if "OFFICE_BLOOD" in name or "DESK_BLOOD" in name:
                material = blood_dark
            ensure_planar_uv(obj)
            assign(obj, material)
            decals += 1
        elif "HAND" in name or "_WALL_HAND" in name:
            ensure_planar_uv(obj)
            assign(obj, hand)
            decals += 1
        elif "PAPER" in name or "BINDER" in name or "TOWEL" in name:
            if not in_reception(obj):
                continue
            if obj.data.materials and obj.data.materials[0] is paper:
                continue
            current = obj.data.materials[0].name if obj.data.materials else ""
            if current in {"NEXUS_OffWhite", "NEXUS_Clinical"}:
                assign(obj, paper)
                decals += 1

    print("RECEP_MATERIALS_APPLIED", applied)
    print("DECALS_REBUILT", decals)
    print("MATERIALES", [m.name for m in (wall, ceiling, floor, wainscot, paper, blood, blood_dark, hand)])


main()
