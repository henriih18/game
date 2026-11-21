"""El Coleccionista v3 — abrigo y equipo con formas controladas.

Parte de FM_COLLECTOR_SCULPT.blend (cuerpo continuo ya esculpido), retira las
formas de bolas de la v1 y construye un abrigo largo abierto, capucha, mangas,
perneras y una mochila estructurada. Conserva la máscara, correas, llaves y
farol. Guarda FM_COLLECTOR_V3.blend, exporta collector_creature_v3.glb y
renderiza /tmp/opencode/collector_v3.png.

No toca fotos-referencia/, el máster del nivel ni escenas del slice.
"""

import math
import os
import random

import bpy
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
OUT_BLEND = os.path.join(ROOT, "nexus/nivel_01/FM_COLLECTOR_V3.blend")
OUT_GLB = os.path.join(ROOT, "assets/models/fm/collector_creature_v3.glb")
OUT_RENDER = "/tmp/opencode/collector_v3.png"
TEX_DIR = os.path.join(ROOT, "assets/art/fm/collector")

COLLECTION_NAME = "COLLECTOR_V3"


def collection():
    col = bpy.data.collections.get(COLLECTION_NAME)
    if col is None:
        col = bpy.data.collections.new(COLLECTION_NAME)
        bpy.context.scene.collection.children.link(col)
    return col


def image_material(name, tex_path, tint, roughness=0.9, metallic=0.0,
                   normal_path=None, normal_strength=0.5):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*tint, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(tex_path, check_existing=True)
    tex.interpolation = "Linear"
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    if normal_path and os.path.exists(normal_path):
        ntex = nt.nodes.new("ShaderNodeTexImage")
        ntex.image = bpy.data.images.load(normal_path, check_existing=True)
        ntex.image.colorspace_settings.name = "Non-Color"
        nmap = nt.nodes.new("ShaderNodeNormalMap")
        nmap.inputs["Strength"].default_value = normal_strength
        nt.links.new(ntex.outputs["Color"], nmap.inputs["Color"])
        nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def flat_material(name, color, roughness=0.8, metallic=0.0, emission=None,
                  strength=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
    return mat


def mesh_object(name, verts, faces, mat, uvs=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    me.validate(verbose=False)
    ob = bpy.data.objects.new(name, me)
    collection().objects.link(ob)
    ob.data.materials.append(mat)
    if uvs:
        uv = me.uv_layers.new(name="UVMap")
        uv.data.foreach_set("uv", [c for face_uv in uvs for loop_uv in face_uv for c in loop_uv])
    for poly in me.polygons:
        poly.use_smooth = True
    return ob


def shade_smooth(ob, angle=0.9):
    me = ob.data
    for p in me.polygons:
        p.use_smooth = True
    try:
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)
        bpy.ops.object.shade_smooth_by_angle(angle=angle)
    except Exception:
        pass


def loft(name, rings, mat, u_repeat=3.0, v_repeat=4.0, angle0=300.0,
         angle1=600.0, segments=28):
    """rings: list of (z, rx, ry, cx, cy). Abre un hueco frontal."""
    verts = []
    uvs = []
    for (z, rx, ry, cx, cy) in rings:
        for i in range(segments + 1):
            a = math.radians(angle0 + (angle1 - angle0) * i / segments)
            fold = 1.0 + 0.035 * math.sin(7.0 * a + z * 2.2) + 0.015 * math.sin(13.0 * a - z)
            verts.append((cx + math.cos(a) * rx * fold,
                          cy + math.sin(a) * ry * fold, z))
    faces = []
    face_uvs = []
    for r in range(len(rings) - 1):
        for i in range(segments):
            a = r * (segments + 1) + i
            b = a + 1
            c = a + segments + 2
            d = a + segments + 1
            faces.append((a, b, c, d))
            u0 = u_repeat * i / segments
            u1 = u_repeat * (i + 1) / segments
            v0 = v_repeat * r / (len(rings) - 1)
            v1 = v_repeat * (r + 1) / (len(rings) - 1)
            face_uvs.append([(u0, v0), (u1, v0), (u1, v1), (u0, v1)])
    ob = mesh_object(name, verts, faces, mat, face_uvs)
    mod = ob.modifiers.new("Solidify", "SOLIDIFY")
    mod.thickness = 0.025
    mod.offset = 0.0
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier=mod.name)
    shade_smooth(ob)
    return ob


def tube(name, points, radii, mat, segments=14, u_repeat=2.0, v_repeat=3.0):
    pts = [Vector(p) for p in points]
    verts = []
    for i, p in enumerate(pts):
        if i == 0:
            t = (pts[1] - pts[0]).normalized()
        elif i == len(pts) - 1:
            t = (pts[-1] - pts[-2]).normalized()
        else:
            t = (pts[i + 1] - pts[i - 1]).normalized()
        up = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        side = t.cross(up).normalized()
        up2 = side.cross(t).normalized()
        for j in range(segments + 1):
            a = 2.0 * math.pi * j / segments
            fold = 1.0 + 0.03 * math.sin(5.0 * a + i)
            verts.append(p + (side * math.cos(a) + up2 * math.sin(a)) * radii[i] * fold)
    faces = []
    face_uvs = []
    for r in range(len(pts) - 1):
        for i in range(segments):
            a = r * (segments + 1) + i
            b = a + 1
            c = a + segments + 2
            d = a + segments + 1
            faces.append((a, b, c, d))
            face_uvs.append([(u_repeat * i / segments, v_repeat * r / (len(pts) - 1)),
                             (u_repeat * (i + 1) / segments, v_repeat * r / (len(pts) - 1)),
                             (u_repeat * (i + 1) / segments, v_repeat * (r + 1) / (len(pts) - 1)),
                             (u_repeat * i / segments, v_repeat * (r + 1) / (len(pts) - 1))])
    ob = mesh_object(name, verts, faces, mat, face_uvs)
    shade_smooth(ob)
    return ob


def rounded_box(name, loc, size, mat, bevel=0.02, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel > 0:
        mod = ob.modifiers.new("Bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        mod.limit_method = "ANGLE"
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.modifier_apply(modifier=mod.name)
    ob.data.materials.append(mat)
    for p in ob.data.polygons:
        p.use_smooth = False
    return ob


def cylinder(name, loc, radius, depth, mat, axis="Z", segments=20, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=segments, radius=radius, depth=depth,
                                       location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    if axis == "X":
        ob.rotation_euler = (0, math.radians(90), 0)
    elif axis == "Y":
        ob.rotation_euler = (math.radians(90), 0, 0)
    ob.data.materials.append(mat)
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def sphere(name, loc, radius, mat, scale=(1, 1, 1), segments=24, rings=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings,
                                         radius=radius, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(mat)
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def make_cloth_normals():
    """Genera normales de tela/cuero simples y tileables con PIL."""
    try:
        from PIL import Image, ImageFilter
        import numpy as np
    except Exception:
        return None, None
    os.makedirs(TEX_DIR, exist_ok=True)
    rng = np.random.default_rng(7)
    size = 512
    base = rng.normal(0.0, 1.0, (size, size)).astype(np.float32)
    # suavizado periódico simple
    for _ in range(3):
        base = (base + np.roll(base, 1, 0) + np.roll(base, -1, 0) +
                np.roll(base, 1, 1) + np.roll(base, -1, 1)) / 5.0
    base = (base - base.min()) / max(1e-6, base.max() - base.min())
    # trama de tejido
    yy, xx = np.mgrid[0:size, 0:size]
    weave = 0.12 * np.sin(xx * math.pi / 4.0) * np.sin(yy * math.pi / 4.0)
    height = np.clip(base * 0.85 + weave, 0, 1)
    dx = np.roll(height, -1, 1) - np.roll(height, 1, 1)
    dy = np.roll(height, -1, 0) - np.roll(height, 1, 0)
    n = np.dstack((-dx * 2.0, -dy * 2.0, np.ones_like(height)))
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    normal = ((n * 0.5 + 0.5) * 255).astype(np.uint8)
    cloth_n = os.path.join(TEX_DIR, "T_V3_Cloth_N.png")
    Image.fromarray(normal).save(cloth_n)
    # cuero: más grueso y con poros
    leather_h = np.clip(base * 0.65 + 0.2 * np.sin(xx * 0.9 + yy * 1.3), 0, 1)
    dx = np.roll(leather_h, -1, 1) - np.roll(leather_h, 1, 1)
    dy = np.roll(leather_h, -1, 0) - np.roll(leather_h, 1, 0)
    n = np.dstack((-dx * 1.4, -dy * 1.4, np.ones_like(leather_h)))
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    normal = ((n * 0.5 + 0.5) * 255).astype(np.uint8)
    leather_n = os.path.join(TEX_DIR, "T_V3_Leather_N.png")
    Image.fromarray(normal).save(leather_n)
    return cloth_n, leather_n


def hide_old():
    keep = {
        "Collector_Body", "Collector_Body_High", "Collector_Undersuit",
        "Collector_Mask", "Collector_GoggleRing_-1", "Collector_GoggleRing_1",
        "Collector_GoggleLens_-1", "Collector_GoggleLens_1",
        "Collector_Respirator", "Collector_RespiratorGrill",
        "Collector_Filter", "Collector_FilterCap",
        "Collector_Hose_0", "Collector_Hose_1", "Collector_Hose_2",
        "Collector_Hose_3", "Collector_Hose_4", "Collector_Hose_5",
        "Collector_Belt", "Collector_OuterBelt", "Collector_Buckle",
        "Collector_KeyRing", "Collector_Key_0", "Collector_Key_1",
        "Collector_Key_2", "Collector_Key_3", "Collector_Key_4",
        "Collector_LanternBody", "Collector_LanternCore",
        "Collector_LanternBar_-1", "Collector_LanternBar_0",
        "Collector_LanternBar_1", "Collector_LanternHook",
    }
    for ob in list(bpy.data.objects):
        if ob.name in keep:
            continue
        if ob.name.startswith("Collector_"):
            bpy.data.objects.remove(ob, do_unlink=True)
    # El cuerpo de alta resolución no se exporta.
    high = bpy.data.objects.get("Collector_Body_High")
    if high:
        high.hide_render = True
        high.hide_set(True)
    body = bpy.data.objects.get("Collector_Body")
    if body:
        body.hide_render = False
        body.hide_set(False)
    under = bpy.data.objects.get("Collector_Undersuit")
    if under:
        under.hide_render = False
        under.hide_set(False)


def build_clothing(canvas, leather, metal, brass, dark):
    # Abrigo largo, abierto al frente, con bajo irregular.
    coat_rings = [
        (1.88, 0.47, 0.31, 0.0, -0.05),
        (1.65, 0.48, 0.32, 0.0, -0.045),
        (1.40, 0.46, 0.31, 0.0, -0.035),
        (1.15, 0.45, 0.31, 0.0, -0.02),
        (0.90, 0.48, 0.34, 0.0, -0.01),
        (0.60, 0.52, 0.37, 0.0, 0.0),
        (0.32, 0.56, 0.40, 0.0, 0.01),
    ]
    coat = loft("V3_Coat", coat_rings, canvas, u_repeat=3.5, v_repeat=4.0)
    # Bajo irregular del abrigo.
    for v in coat.data.vertices:
        if v.co.z < 0.34:
            a = math.atan2(v.co.y, v.co.x)
            v.co.z += 0.025 * math.sin(9.0 * a) + 0.012 * math.sin(17.0 * a)
    coat.data.update()

    # Cuello alto.
    loft("V3_Collar", [(1.86, 0.24, 0.19, 0.0, -0.06),
                       (1.98, 0.22, 0.18, 0.0, -0.06)], leather,
         u_repeat=2.0, v_repeat=1.0)

    # Capucha abierta al frente.
    hood_rings = [
        (1.92, 0.27, 0.25, 0.0, 0.0),
        (2.04, 0.29, 0.27, 0.0, 0.0),
        (2.16, 0.27, 0.25, 0.0, 0.01),
        (2.27, 0.21, 0.20, 0.0, 0.03),
        (2.35, 0.11, 0.10, 0.0, 0.05),
    ]
    loft("V3_Hood", hood_rings, canvas, u_repeat=2.0, v_repeat=2.0,
         angle0=35.0, angle1=325.0, segments=24)

    # Mangas.
    for s in (-1, 1):
        tube("V3_Sleeve_%s" % ("L" if s < 0 else "R"),
             [(0.40 * s, -0.08, 1.78), (0.52 * s, -0.02, 1.38),
              (0.58 * s, 0.01, 0.98), (0.60 * s, 0.02, 0.86)],
             [0.155, 0.125, 0.095, 0.085], canvas, segments=14)
        cylinder("V3_Cuff_%s" % ("L" if s < 0 else "R"),
                 (0.60 * s, 0.02, 0.86), 0.105, 0.06, leather, axis="Z")

    # Perneras visibles bajo el abrigo.
    for s in (-1, 1):
        tube("V3_Pant_%s" % ("L" if s < 0 else "R"),
             [(0.20 * s, 0.0, 0.98), (0.24 * s, 0.0, 0.55),
              (0.26 * s, 0.0, 0.18), (0.27 * s, -0.02, 0.08)],
             [0.17, 0.14, 0.10, 0.09], canvas, segments=14)
        cylinder("V3_BootCuff_%s" % ("L" if s < 0 else "R"),
                 (0.27 * s, -0.02, 0.12), 0.12, 0.10, leather, axis="Z")

    # Mochila estructurada.
    rounded_box("V3_PackFrame", (0.0, 0.36, 1.62), (0.58, 0.24, 0.74),
                leather, bevel=0.025)
    rounded_box("V3_PackSack", (0.0, 0.50, 1.52), (0.48, 0.26, 0.52),
                canvas, bevel=0.06)
    cylinder("V3_PackRoll", (0.0, 0.52, 1.94), 0.095, 0.54, canvas,
             axis="X", segments=18)
    for s in (-1, 1):
        cylinder("V3_Pot_%s" % ("L" if s < 0 else "R"),
                 (0.23 * s, 0.50, 1.82), 0.085, 0.20, metal, axis="Z",
                 segments=18)
    for s in (-1, 1):
        rounded_box("V3_PackStrap_%s" % ("L" if s < 0 else "R"),
                    (0.22 * s, -0.12, 1.50), (0.075, 0.10, 0.60),
                    leather, bevel=0.01, rot=(0, 0, 0))
        rounded_box("V3_PackBuckle_%s" % ("L" if s < 0 else "R"),
                    (0.22 * s, -0.18, 1.20), (0.09, 0.04, 0.09),
                    brass, bevel=0.008)

    # Cinturón exterior y bolsas.
    rounded_box("V3_Belt", (0.0, -0.02, 1.10), (0.62, 0.40, 0.07),
                leather, bevel=0.02)
    for s in (-1, 1):
        rounded_box("V3_Pouch_%s" % ("L" if s < 0 else "R"),
                    (0.34 * s, -0.22, 1.02), (0.16, 0.12, 0.20),
                    leather, bevel=0.02)
    # Tiras de tela colgando del cinturón, integradas en el bajo.
    for i in range(7):
        x = -0.24 + i * 0.08
        rounded_box("V3_Strap_%d" % i, (x, -0.30, 0.88),
                    (0.035, 0.02, 0.26 + 0.04 * (i % 3)), dark, bevel=0.004)


def build_scene_lights():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [
        i.identifier for i in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"

    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.018, 0.020, 0.024, 1.0)
        bg.inputs[1].default_value = 0.6

    bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 0, 0))
    ground = bpy.context.object
    ground.name = "V3_Ground"
    gm = flat_material("M_V3_Ground", (0.035, 0.038, 0.04), 0.96)
    ground.data.materials.append(gm)

    bpy.ops.object.camera_add(location=(3.4, -5.6, 1.55))
    cam = bpy.context.object
    cam.name = "V3_Camera"
    cam.data.lens = 55
    direction = Vector((0, 0, 1.15)) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam

    for name, loc, energy, color, size in (
        ("V3_Key", (3.0, -4.0, 4.2), 420.0, (1.0, 0.86, 0.70), 3.0),
        ("V3_Fill", (-3.5, -2.5, 2.6), 180.0, (0.62, 0.76, 1.0), 4.0),
        ("V3_Rim", (-1.0, 3.2, 3.4), 320.0, (0.70, 0.82, 1.0), 2.5),
    ):
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.color = color
        data.shape = "DISK"
        data.size = size
        ob = bpy.data.objects.new(name, data)
        scene.collection.objects.link(ob)
        ob.location = loc
        ob.rotation_euler = (Vector((0, 0, 1.2)) - ob.location).to_track_quat("-Z", "Y").to_euler()


def main():
    random.seed(7)
    os.makedirs(TEX_DIR, exist_ok=True)
    cloth_n, leather_n = make_cloth_normals()
    canvas_tex = os.path.join(ROOT, "assets/art/fm/cloth_albedo.png")
    canvas = image_material("M_V3_Canvas", canvas_tex, (0.45, 0.40, 0.33),
                            roughness=0.95, normal_path=cloth_n,
                            normal_strength=0.55)
    leather = image_material("M_V3_Leather", canvas_tex, (0.19, 0.14, 0.10),
                             roughness=0.82, normal_path=leather_n,
                             normal_strength=0.45)
    metal = flat_material("M_V3_Metal", (0.18, 0.19, 0.19), 0.42, 1.0)
    brass = flat_material("M_V3_Brass", (0.55, 0.38, 0.12), 0.32, 1.0)
    dark = flat_material("M_V3_Dark", (0.018, 0.016, 0.014), 0.82)

    hide_old()
    build_clothing(canvas, leather, metal, brass, dark)
    build_scene_lights()

    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
    print("V3_SAVED", OUT_BLEND)

    # Exportar solo las mallas visibles nuevas y el cuerpo conservado.
    bpy.ops.object.select_all(action="DESELECT")
    export_objs = []
    for ob in bpy.data.objects:
        if ob.type != "MESH":
            continue
        if ob.hide_render:
            continue
        if ob.name in {"V3_Ground"}:
            continue
        ob.select_set(True)
        export_objs.append(ob)
    bpy.context.view_layer.objects.active = export_objs[0] if export_objs else None
    bpy.ops.export_scene.gltf(filepath=OUT_GLB, export_format="GLB",
                              use_selection=True, export_yup=True,
                              export_apply=True, export_animations=False,
                              export_cameras=False, export_lights=False,
                              export_materials="EXPORT", export_image_format="AUTO")
    print("V3_GLB", OUT_GLB, len(export_objs))

    bpy.context.scene.render.filepath = OUT_RENDER
    bpy.ops.render.render(write_still=True)
    print("V3_RENDER", OUT_RENDER)


if __name__ == "__main__":
    main()
