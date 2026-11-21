"""Recepción del Nivel 1 (v126d): metales con textura PBR.

Los servicios de techo (conductos, bandejas, montantes, bridas) usaban
color plano y se leían como plástico. Se reconstruyen esos materiales con
texturas de `assets/texturas/Metal y oxidacion/`, con proyección por
coordenadas de objeto para que la escala sea coherente entre piezas.
"""

import os

import bpy

ASSETS = "/home/riyo/Documentos/game/assets"

TEX = {
    "painted_diff": "texturas/Metal y oxidacion/rusty_painted_metal_2k.blend/textures/rusty_painted_metal_diff_2k.jpg",
    "painted_rough": "texturas/Metal y oxidacion/rusty_painted_metal_2k.blend/textures/rusty_painted_metal_rough_2k.exr",
    "painted_nor": "texturas/Metal y oxidacion/rusty_painted_metal_2k.blend/textures/rusty_painted_metal_nor_gl_2k.exr",
    "sheet_diff": "texturas/Metal y oxidacion/rusty_metal_sheet_2k.blend/textures/rusty_metal_sheet_diff_2k.jpg",
    "sheet_rough": "texturas/Metal y oxidacion/rusty_metal_sheet_2k.blend/textures/rusty_metal_sheet_rough_2k.exr",
    "sheet_nor": "texturas/Metal y oxidacion/rusty_metal_sheet_2k.blend/textures/rusty_metal_sheet_nor_gl_2k.exr",
    "green_diff": "texturas/Metal y oxidacion/green_metal_rust_2k.blend/textures/green_metal_rust_diff_2k.jpg",
    "green_rough": "texturas/Metal y oxidacion/green_metal_rust_2k.blend/textures/green_metal_rust_rough_2k.jpg",
    "green_nor": "texturas/Metal y oxidacion/green_metal_rust_2k.blend/textures/green_metal_rust_nor_gl_2k.exr",
}


def image(key, non_color=False):
    path = os.path.join(ASSETS, TEX[key])
    img = bpy.data.images.load(path, check_existing=True)
    want = "Non-Color" if non_color else "sRGB"
    if img.colorspace_settings.name != want:
        img.colorspace_settings.name = want
    return img


def build(name, diff, rough, nor, scale, tint, normal_strength, metallic, rough_range):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()
    out = tree.nodes.new("ShaderNodeOutputMaterial")
    out.location = (700, 0)
    bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (400, 0)
    tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    coord = tree.nodes.new("ShaderNodeTexCoord")
    coord.location = (-1000, 0)
    mapping = tree.nodes.new("ShaderNodeMapping")
    mapping.location = (-820, 0)
    mapping.inputs["Scale"].default_value = (scale, scale, scale)
    tree.links.new(coord.outputs["Object"], mapping.inputs["Vector"])

    t_diff = tree.nodes.new("ShaderNodeTexImage")
    t_diff.image = image(diff)
    t_diff.location = (-560, 240)
    tree.links.new(mapping.outputs["Vector"], t_diff.inputs["Vector"])

    t_rough = tree.nodes.new("ShaderNodeTexImage")
    t_rough.image = image(rough, True)
    t_rough.location = (-560, 0)
    tree.links.new(mapping.outputs["Vector"], t_rough.inputs["Vector"])

    tint_node = tree.nodes.new("ShaderNodeMixRGB")
    tint_node.blend_type = "MULTIPLY"
    tint_node.location = (-260, 240)
    tint_node.inputs["Fac"].default_value = 1.0
    tint_node.inputs["Color2"].default_value = (*tint, 1.0)
    tree.links.new(t_diff.outputs["Color"], tint_node.inputs["Color1"])
    tree.links.new(tint_node.outputs["Color"], bsdf.inputs["Base Color"])

    rr = tree.nodes.new("ShaderNodeMapRange")
    rr.location = (-260, 0)
    rr.inputs["To Min"].default_value = rough_range[0]
    rr.inputs["To Max"].default_value = rough_range[1]
    tree.links.new(t_rough.outputs["Color"], rr.inputs["Value"])
    tree.links.new(rr.outputs["Result"], bsdf.inputs["Roughness"])

    t_nor = tree.nodes.new("ShaderNodeTexImage")
    t_nor.image = image(nor, True)
    t_nor.location = (-560, -260)
    tree.links.new(mapping.outputs["Vector"], t_nor.inputs["Vector"])
    nm = tree.nodes.new("ShaderNodeNormalMap")
    nm.location = (-260, -260)
    nm.inputs["Strength"].default_value = normal_strength
    tree.links.new(t_nor.outputs["Color"], nm.inputs["Color"])
    tree.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])

    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def main():
    build("NEXUS_V05_MAT_Galv", "painted_diff", "painted_rough", "painted_nor",
          scale=0.55, tint=(0.62, 0.64, 0.63), normal_strength=0.7,
          metallic=0.85, rough_range=(0.35, 0.85))
    build("NEXUS_V05_MAT_Galv_Dark", "painted_diff", "painted_rough", "painted_nor",
          scale=0.9, tint=(0.30, 0.31, 0.30), normal_strength=0.8,
          metallic=0.8, rough_range=(0.40, 0.90))
    build("NEXUS_V05_MAT_CableTray", "sheet_diff", "sheet_rough", "sheet_nor",
          scale=1.1, tint=(0.42, 0.43, 0.41), normal_strength=0.9,
          metallic=0.75, rough_range=(0.40, 0.90))
    build("NEXUS_V05_MAT_Conduit", "sheet_diff", "sheet_rough", "sheet_nor",
          scale=1.6, tint=(0.50, 0.51, 0.48), normal_strength=0.8,
          metallic=0.6, rough_range=(0.45, 0.90))
    build("NEXUS_V05_MAT_Pipe_Red", "green_diff", "green_rough", "green_nor",
          scale=1.4, tint=(1.15, 0.16, 0.10), normal_strength=0.7,
          metallic=0.55, rough_range=(0.30, 0.80))

    # pequeños refuerzos de material en el mostrador
    top = bpy.data.materials.get("NEXUS_V05_MAT_Counter_Top")
    if top is not None:
        bsdf = next(n for n in top.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        bsdf.inputs["Base Color"].default_value = (0.055, 0.058, 0.056, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.34

    print("METAL_MATERIALS", [n for n in ("NEXUS_V05_MAT_Galv", "NEXUS_V05_MAT_Galv_Dark",
                                          "NEXUS_V05_MAT_CableTray", "NEXUS_V05_MAT_Conduit",
                                          "NEXUS_V05_MAT_Pipe_Red")
                              if bpy.data.materials.get(n)])


main()
