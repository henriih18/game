"""El Coleccionista v4 — criatura jorobada, anatomia realista y equipo de saqueo.

Se construye desde cero (sin reutilizar el cuerpo v1) con masas anatomicas
unidas por remesh voxel. El frente del modelo es -Y.
"""
import bpy
import bmesh
import math
import os
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
BLEND = os.path.join(ROOT, "nexus/nivel_01/FM_COLLECTOR_V4.blend")
GLB = os.path.join(ROOT, "assets/models/fm/collector_creature_v4.glb")
RENDER = "/tmp/opencode/collector_v4.png"
COL_NAME = "FM_COLLECTOR_V4"

FLESH_ALBEDO = os.path.join(ROOT, "assets/art/fm/collector/T_Collector_Skin_BC.png")
FLESH_NORMAL = os.path.join(ROOT, "assets/art/fm/flesh_normal.png")
FLESH_ROUGH = os.path.join(ROOT, "assets/art/fm/flesh_roughness.png")
CLOTH_ALBEDO = os.path.join(ROOT, "assets/art/fm/cloth_albedo.png")
CLOTH_NORMAL = os.path.join(ROOT, "assets/art/fm/collector/T_Collector_Cloth_N.png")
LEATHER_NORMAL = os.path.join(ROOT, "assets/art/fm/collector/T_Collector_Leather_N.png")
RUST_ALBEDO = os.path.join(ROOT, "assets/art/fm/rust_albedo.png")
RUST_NORMAL = os.path.join(ROOT, "assets/art/fm/rust_normal.png")
RUST_ROUGH = os.path.join(ROOT, "assets/art/fm/rust_roughness.png")


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def col():
    c = bpy.data.collections.get(COL_NAME)
    if c is None:
        c = bpy.data.collections.new(COL_NAME)
        bpy.context.scene.collection.children.link(c)
    return c


def link(obj, c=None):
    (c or col()).objects.link(obj)
    return obj


def mat(name, color, rough=0.6, metal=0.0, emission=None, strength=0.0):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
    return m


def textured(name, albedo, color, rough=0.8, normal_path=None, normal_strength=0.6,
             metallic=0.0, emission=None, strength=0.0):
    m = mat(name, color, rough, metallic, emission, strength)
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    if albedo and os.path.exists(albedo):
        img = bpy.data.images.load(albedo, check_existing=True)
        tex = m.node_tree.nodes.new("ShaderNodeTexImage")
        tex.image = img
        m.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    if normal_path and os.path.exists(normal_path):
        img = bpy.data.images.load(normal_path, check_existing=True)
        img.colorspace_settings.name = "Non-Color"
        tex = m.node_tree.nodes.new("ShaderNodeTexImage")
        tex.image = img
        nm = m.node_tree.nodes.new("ShaderNodeNormalMap")
        nm.inputs["Strength"].default_value = normal_strength
        m.node_tree.links.new(tex.outputs["Color"], nm.inputs["Color"])
        m.node_tree.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def cube(name, center, size, material, bevel=0.0, segments=2, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel > 0:
        md = ob.modifiers.new("Bevel", "BEVEL")
        md.width = bevel
        md.segments = segments
        md.limit_method = "ANGLE"
        md.angle_limit = math.radians(30)
        bpy.ops.object.modifier_apply(modifier=md.name)
    ob.data.materials.append(material)
    return link(ob)


def cyl(name, center, radius, depth, material, axis="Z", segments=24, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=segments, radius=radius,
                                        depth=depth, location=center)
    ob = bpy.context.object
    ob.name = name
    if axis == "X":
        ob.rotation_euler[1] = math.radians(90)
    elif axis == "Y":
        ob.rotation_euler[0] = math.radians(90)
    if rot != (0, 0, 0):
        ob.rotation_euler.rotate(Vector(rot).to_track_quat('Z', 'Y'))
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    ob.data.materials.append(material)
    return link(ob)


def sphere(name, center, radius, material, scale=(1, 1, 1), segments=32, rings=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings,
                                         radius=radius, location=center)
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(material)
    return link(ob)


def segment(name, a, b, r1, r2, material, segments=16):
    a = Vector(a); b = Vector(b)
    d = b - a
    mid = (a + b) * 0.5
    bpy.ops.mesh.primitive_cone_add(vertices=segments, radius1=r1, radius2=r2,
                                     depth=d.length, location=mid)
    ob = bpy.context.object
    ob.name = name
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    ob.data.materials.append(material)
    return link(ob)


def torus(name, center, major, minor, material, rot=(0, 0, 0), scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     major_segments=32, minor_segments=12,
                                     location=center, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(material)
    return link(ob)


def uv_unwrap(ob):
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")


def smooth(ob, angle=38.0):
    for p in ob.data.polygons:
        p.use_smooth = True
    try:
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(angle))
    except Exception:
        pass


def add_ellipsoid(parts, name, center, size, material=None):
    ob = sphere(name, center, 1.0, material or bpy.data.materials["M_V4_Skin"],
                scale=size, segments=32, rings=20)
    parts.append(ob)
    return ob


def build_body(skin):
    # Cuerpo continuo a partir de un esqueleto Skin: columna jorobada,
    # caja torácica estrecha, brazos largos y piernas cortas.
    verts = []
    edges = []
    radii = []

    def add(co, rx, rz=None):
        verts.append(co)
        radii.append((rx, rz if rz is not None else rx))
        return len(verts) - 1

    pelvis = add((0.0, 0.06, 0.90), 0.150)
    spine1 = add((0.0, 0.00, 1.06), 0.125)
    spine2 = add((0.0, -0.10, 1.22), 0.145)
    chest = add((0.0, -0.24, 1.38), 0.200)
    neck = add((0.0, -0.44, 1.52), 0.075)
    head = add((0.0, -0.60, 1.64), 0.100)
    edges += [(pelvis, spine1), (spine1, spine2), (spine2, chest),
              (chest, neck), (neck, head)]

    for s in (-1, 1):
        shoulder = add((0.27 * s, -0.36, 1.48), 0.085)
        elbow = add((0.35 * s, -0.30, 1.14), 0.050)
        wrist = add((0.39 * s, -0.24, 0.74), 0.035)
        hand = add((0.40 * s, -0.22, 0.62), 0.045)
        edges += [(chest, shoulder), (shoulder, elbow), (elbow, wrist),
                  (wrist, hand)]
        hip = add((0.14 * s, 0.06, 0.86), 0.100)
        knee = add((0.16 * s, -0.22, 0.46), 0.070)
        ankle = add((0.18 * s, -0.08, 0.10), 0.045)
        foot = add((0.18 * s, -0.22, 0.050), 0.050)
        edges += [(pelvis, hip), (hip, knee), (knee, ankle), (ankle, foot)]

    me = bpy.data.meshes.new("V4BodySkeleton")
    me.from_pydata(verts, edges, [])
    me.update()
    body = bpy.data.objects.new("V4_Body", me)
    link(body)
    bpy.context.view_layer.objects.active = body
    body.select_set(True)
    skin_mod = body.modifiers.new("Skin", "SKIN")
    skin_mod.use_smooth_shade = True
    bpy.context.view_layer.update()
    layer = me.skin_vertices[0].data
    for i, (rx, rz) in enumerate(radii):
        layer[i].radius = (rx, rz)
    layer[pelvis].use_root = True
    bpy.ops.object.modifier_apply(modifier=skin_mod.name)

    sub = body.modifiers.new("Sub", "SUBSURF")
    sub.levels = 2
    sub.render_levels = 2
    bpy.ops.object.modifier_apply(modifier=sub.name)

    # Masas que se fusionan con el cuerpo: joroba, cráneo, mandíbula y ceja.
    parts = [body]
    parts.append(add_ellipsoid(parts, "V4_Hump", (0, 0.06, 1.48),
                               (0.230, 0.190, 0.210)))
    parts.append(add_ellipsoid(parts, "V4_Skull", (0, -0.62, 1.65),
                               (0.108, 0.122, 0.145)))
    parts.append(add_ellipsoid(parts, "V4_Jaw", (0, -0.68, 1.56),
                               (0.076, 0.090, 0.076)))
    parts.append(add_ellipsoid(parts, "V4_Brow", (0, -0.725, 1.71),
                               (0.090, 0.040, 0.034)))
    for s in (-1, 1):
        parts.append(add_ellipsoid(parts, "V4_Ear_%d" % s,
                                   (0.106 * s, -0.60, 1.65),
                                   (0.024, 0.032, 0.050)))
        parts.append(add_ellipsoid(parts, "V4_Clavicle_%d" % s,
                                   (0.20 * s, -0.28, 1.42),
                                   (0.085, 0.075, 0.070)))

    bpy.ops.object.select_all(action="DESELECT")
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    body = bpy.context.object
    body.name = "V4_Body"
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    rem = body.modifiers.new("Fuse", "REMESH")
    rem.mode = "VOXEL"
    rem.voxel_size = 0.012
    rem.use_smooth_shade = True
    bpy.ops.object.modifier_apply(modifier=rem.name)

    sm = body.modifiers.new("Smooth", "SMOOTH")
    sm.factor = 0.55
    sm.iterations = 8
    bpy.ops.object.modifier_apply(modifier=sm.name)

    tex = bpy.data.textures.new("V4_Pores", "CLOUDS")
    tex.noise_scale = 0.035
    tex.noise_depth = 3
    d1 = body.modifiers.new("Pores", "DISPLACE")
    d1.texture = tex
    d1.strength = 0.0022
    d1.mid_level = 0.5
    bpy.ops.object.modifier_apply(modifier=d1.name)
    tex2 = bpy.data.textures.new("V4_Muscle", "VORONOI")
    tex2.noise_scale = 0.10
    tex2.distance_metric = "DISTANCE"
    d2 = body.modifiers.new("Muscle", "DISPLACE")
    d2.texture = tex2
    d2.strength = 0.0045
    d2.mid_level = 0.5
    bpy.ops.object.modifier_apply(modifier=d2.name)

    dec = body.modifiers.new("Game", "DECIMATE")
    dec.ratio = 0.42
    dec.use_collapse_triangulate = True
    bpy.ops.object.modifier_apply(modifier=dec.name)

    smooth(body, 42)
    body.data.materials.clear()
    body.data.materials.append(skin)
    uv_unwrap(body)
    return body


def build_extremities(skin):
    # Dedos y palmas se modelan aparte del remesh para que no se fundan en
    # una manopla o una aleta. Se solapan con la muñeca y la planta.
    for s in (-1, 1):
        sphere("V4_PalmMass_%d" % s, (0.43 * s, -0.14, 0.31), 1.0, skin,
               scale=(0.070, 0.045, 0.070), segments=20, rings=12)
        for i in range(4):
            x = 0.43 * s + (i - 1.5) * 0.030
            segment("V4_FingerA_%d_%d" % (s, i),
                    (x, -0.150, 0.335), (x + 0.005 * s, -0.230, 0.165),
                    0.013, 0.006, skin, 10)
            cube("V4_ClawHand_%d_%d" % (s, i),
                 (x + 0.005 * s, -0.242, 0.153),
                 (0.011, 0.024, 0.017),
                 bpy.data.materials["M_V4_Bone"], bevel=0.002)
        segment("V4_ThumbA_%d" % s,
                (0.385 * s, -0.110, 0.335), (0.345 * s, -0.185, 0.220),
                0.014, 0.007, skin, 10)
    for s in (-1, 1):
        for i in range(5):
            x = 0.240 * s + (i - 2) * 0.028
            y0 = -0.290 - abs(i - 2) * 0.006
            y1 = -0.365 - abs(i - 2) * 0.008
            segment("V4_ToeA_%d_%d" % (s, i),
                    (x, y0, 0.058), (x, y1, 0.038),
                    0.015, 0.009, skin, 10)
        for i in range(5):
            x = 0.240 * s + (i - 2) * 0.028
            y1 = -0.365 - abs(i - 2) * 0.008
            cube("V4_ToeNail_%d_%d" % (s, i),
                 (x, y1 - 0.010, 0.036), (0.012, 0.020, 0.010),
                 bpy.data.materials["M_V4_Bone"], bevel=0.002)


def build_surface_details(skin, skin_dark, canvas, leather, bone):
    # Bultos de columna bajo la joroba.
    for i, z in enumerate((1.04, 1.14, 1.24, 1.34, 1.44)):
        sphere("V4_Spine_%d" % i, (0, 0.10 + 0.01 * i, z), 0.022, bone,
               scale=(0.65, 1.15, 0.75))
    # Correas que sujetan la mochila por delante.
    for s in (-1, 1):
        segment("V4_Sling_%d" % s,
                (0.16 * s, -0.42, 1.28), (0.19 * s, 0.28, 1.44),
                0.019, 0.017, leather, 8)


def loft_shell(name, rings, gap_deg, material, thickness=0.010, segments=28):
    """Shell abierto por delante. rings = [(z, rx, ry), ...]."""
    import math as _m
    gap = _m.radians(gap_deg)
    start = -_m.pi * 0.5 + gap * 0.5
    end = _m.pi * 1.5 - gap * 0.5
    verts = []
    for z, rx, ry in rings:
        for i in range(segments + 1):
            a = start + (end - start) * i / segments
            verts.append((_m.cos(a) * rx, _m.sin(a) * ry, z))
    faces = []
    row = segments + 1
    for r in range(len(rings) - 1):
        for i in range(segments):
            a = r * row + i
            faces.append((a, a + 1, a + row + 1, a + row))
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    link(ob)
    ob.data.materials.append(material)
    sol = ob.modifiers.new("Thickness", "SOLIDIFY")
    sol.thickness = thickness
    sol.offset = 0.0
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.modifier_apply(modifier=sol.name)
    smooth(ob, 40)
    return ob


def build_clothing(canvas, leather, dark):
    # Abrigo largo abierto, con faldón irregular.
    loft_shell("V4_Coat", [
        (1.46, 0.235, 0.185), (1.30, 0.270, 0.210),
        (1.10, 0.305, 0.235), (0.90, 0.330, 0.255),
        (0.72, 0.345, 0.270),
    ], 58.0, canvas, 0.012)
    # Capa corta sobre los hombros.
    loft_shell("V4_ShoulderCape", [
        (1.54, 0.255, 0.205), (1.46, 0.315, 0.240),
        (1.36, 0.335, 0.255),
    ], 62.0, canvas, 0.010)
    # Faldón rasgado: tiras alrededor del bajo, sin invadir la abertura.
    for i in range(10):
        a = math.radians(-90 + 74 + i * (212.0 / 9.0))
        x = math.cos(a) * 0.335
        y = math.sin(a) * 0.255
        cube("V4_CoatRag_%02d" % i, (x, y, 0.635),
             (0.075, 0.024, 0.20 + 0.05 * (i % 3)), canvas,
             bevel=0.004, rot=(0, 0, a + math.pi * 0.5))
    # Mangas tubulares.
    for s in (-1, 1):
        segment("V4_SleeveA_%d" % s,
                (0.255 * s, -0.315, 1.48), (0.345 * s, -0.270, 1.16),
                0.082, 0.058, canvas, 14)
        segment("V4_SleeveB_%d" % s,
                (0.345 * s, -0.270, 1.16), (0.388 * s, -0.215, 0.79),
                0.058, 0.042, canvas, 14)
        cyl("V4_Cuff_%d" % s, (0.390 * s, -0.210, 0.775), 0.052, 0.045,
            leather, segments=16)
        # Perneras hasta el tobillo.
        segment("V4_LegWrapA_%d" % s,
                (0.145 * s, 0.02, 0.86), (0.160 * s, -0.20, 0.48),
                0.095, 0.070, canvas, 14)
        segment("V4_LegWrapB_%d" % s,
                (0.160 * s, -0.20, 0.48), (0.180 * s, -0.06, 0.12),
                0.070, 0.050, canvas, 14)
        cube("V4_AnkleWrap_%d" % s, (0.180 * s, -0.06, 0.13),
             (0.085, 0.075, 0.09), leather, bevel=0.010)
    # Capucha trasera que enmarca la máscara sin taparla.
    sphere("V4_HoodBack", (0, -0.50, 1.70), 1.0, dark,
           scale=(0.155, 0.145, 0.185), segments=24, rings=16)
    loft_shell("V4_Collar", [
        (1.55, 0.135, 0.115), (1.62, 0.150, 0.130),
    ], 120.0, canvas, 0.010)


def build_gear(skin, canvas, leather, steel, brass, dark, lens, bone):
    # Taparrabos de lona rasgado.
    n = 18
    for i in range(n):
        a = math.pi * 2 * i / n
        x = math.sin(a) * 0.18
        y = math.cos(a) * 0.135
        length = 0.30 + 0.10 * math.sin(i * 2.7)
        cube("V4_Loin_%02d" % i, (x, y, 0.92 - length * 0.5),
             (0.075, 0.028, length), canvas, bevel=0.004)
    belt = torus("V4_Belt", (0, 0, 1.06), 0.19, 0.028, leather,
                 scale=(1.0, 0.78, 1.0))
    # Arnés de pecho y hombros.
    for s in (-1, 1):
        cube("V4_Harness_%d" % s, (0.18 * s, -0.29, 1.52),
             (0.065, 0.032, 0.62), leather, bevel=0.006,
             rot=(0, 0, -0.10 * s))
        cube("V4_ShoulderStrap_%d" % s, (0.22 * s, 0.02, 1.73),
             (0.075, 0.30, 0.035), leather, bevel=0.004)
        cube("V4_Pouch_%d" % s, (0.29 * s, -0.18, 1.08),
             (0.11, 0.10, 0.16), leather, bevel=0.012)
        cube("V4_PouchFlap_%d" % s, (0.29 * s, -0.24, 1.14),
             (0.10, 0.032, 0.08), leather, bevel=0.008)
        sphere("V4_Buckle_%d" % s, (0.18 * s, -0.315, 1.32), 0.032,
                brass, scale=(1.0, 0.5, 0.7))
    # Costuras y remaches del arnés.
    for z in (1.26, 1.40, 1.54, 1.68):
        for s in (-1, 1):
            sphere("V4_Rivet_%d_%d" % (s, int(z * 100)), (0.18 * s, -0.31, z),
                    0.010, steel, scale=(1, 0.5, 1))

    # Mochila: bastidor, saco, cajas, rollo, ollas y correas.
    pack_canvas = mat("M_V4_PackCanvas", (0.22, 0.18, 0.115), 0.92)
    pack_leather = mat("M_V4_PackLeather", (0.070, 0.045, 0.026), 0.82)
    for s in (-1, 1):
        cyl("V4_PackFrame_%d" % s, (0.19 * s, 0.30, 1.34), 0.015, 0.68,
            steel, axis="Z", segments=12)
    cube("V4_PackCrossTop", (0, 0.34, 1.70), (0.42, 0.035, 0.035), steel, bevel=0.008)
    cube("V4_PackCrossLow", (0, 0.34, 0.98), (0.42, 0.035, 0.035), steel, bevel=0.008)
    sphere("V4_PackSack", (0, 0.41, 1.38), 1.0, canvas,
           scale=(0.24, 0.17, 0.32), segments=32, rings=20)
    sphere("V4_PackSackLow", (0, 0.40, 1.10), 1.0, canvas,
           scale=(0.18, 0.14, 0.16), segments=32, rings=20)
    cyl("V4_PackRoll", (0, 0.39, 1.72), 0.075, 0.44, canvas, axis="X", segments=18)
    for s in (-1, 1):
        cyl("V4_PackRollCap_%d" % s, (0.22 * s, 0.39, 1.72), 0.085, 0.026,
            leather, axis="X", segments=18)
    # Cajas y bidones.
    cube("V4_PackBoxA", (0.10, 0.47, 1.62), (0.28, 0.16, 0.18), canvas,
         bevel=0.016, rot=(0, 0, 0.12))
    cube("V4_PackBoxB", (-0.12, 0.46, 1.30), (0.20, 0.15, 0.17), dark,
         bevel=0.014, rot=(0, 0, -0.10))
    for s in (-1, 1):
        cyl("V4_PackDrum_%d" % s, (0.29 * s, 0.40, 1.16), 0.070, 0.24,
            steel, axis="Z", segments=18)
        for z in (1.31, 1.45):
            torus("V4_DrumBand_%d_%d" % (s, int(z * 100)),
                  (0.32 * s, 0.44, z), 0.073, 0.010, brass,
                  scale=(1, 1, 0.7))
    # Olla colgando.
    sphere("V4_Pot", (0.26, 0.27, 1.08), 0.10, dark, scale=(1.0, 1.0, 0.78))
    torus("V4_PotRim", (0.26, 0.27, 1.15), 0.096, 0.011, steel)
    # Correas de la mochila y hebillas.
    for s in (-1, 1):
        cube("V4_PackStrap_%d" % s, (0.20 * s, 0.10, 1.55),
             (0.055, 0.30, 0.035), leather, bevel=0.004,
             rot=(0.20, 0, 0))
        sphere("V4_PackBuckle_%d" % s, (0.20 * s, -0.06, 1.38), 0.028,
                brass, scale=(1, 0.6, 0.7))
    # Farol colgando del cinturón.
    lx = -0.43
    cyl("V4_LanternBody", (lx, -0.12, 0.84), 0.075, 0.17, steel, segments=16)
    cyl("V4_LanternGlass", (lx, -0.12, 0.84), 0.062, 0.11, lens, segments=16)
    torus("V4_LanternTop", (lx, -0.12, 0.93), 0.078, 0.012, brass)
    torus("V4_LanternBase", (lx, -0.12, 0.75), 0.078, 0.012, brass)
    for i in range(4):
        a = math.pi * 0.5 * i
        cube("V4_LanternBar_%d" % i,
             (lx + math.cos(a) * 0.070, -0.12 + math.sin(a) * 0.070, 0.84),
             (0.012, 0.012, 0.19), steel, bevel=0.002)
    torus("V4_LanternRing", (lx, -0.12, 0.96), 0.035, 0.008, steel,
          rot=(math.radians(90), 0, 0))
    # Llaves en el cinturón.
    for i in range(4):
        x = -0.20 + i * 0.055
        cyl("V4_KeyShaft_%d" % i, (x, -0.22, 0.97), 0.006, 0.10, brass,
            segments=8)
        cube("V4_KeyHead_%d" % i, (x, -0.22, 1.03), (0.026, 0.010, 0.026),
             brass, bevel=0.003)

    # Mangueras de la máscara a la mochila.
    for s in (-1, 1):
        a = Vector((0.12 * s, -0.70, 1.74))
        b = Vector((0.22 * s, 0.30, 1.62))
        m = (a + b) * 0.5 + Vector((0.04 * s, -0.04, -0.10))
        segment("V4_HoseA_%d" % s, a, m, 0.022, 0.020, dark, 10)
        segment("V4_HoseB_%d" % s, m, b, 0.020, 0.018, dark, 10)
        for i in range(4):
            t = (i + 1) / 5.0
            p = a.lerp(b, t) + Vector((0.04 * s * math.sin(t * math.pi), 0, -0.08 * math.sin(t * math.pi)))
            torus("V4_HoseRib_%d_%d" % (s, i), p, 0.022, 0.006, steel,
                  rot=(0, math.radians(90), 0))


def build_mask(skin, steel, brass, dark, lens):
    # Placa facial y cráneo exterior.
    sphere("V4_MaskPlate", (0, -0.735, 1.70), 1.0, dark,
           scale=(0.095, 0.045, 0.125), segments=32, rings=20)
    sphere("V4_MaskForehead", (0, -0.725, 1.80), 1.0, dark,
           scale=(0.085, 0.042, 0.040), segments=24, rings=12)
    # Goggles.
    for s in (-1, 1):
        torus("V4_GoggleRim_%d" % s, (0.042 * s, -0.795, 1.755), 0.030, 0.009,
              brass, rot=(math.radians(90), 0, 0))
        sphere("V4_GoggleLens_%d" % s, (0.050 * s, -0.835, 1.800), 0.030,
               lens, scale=(1, 0.55, 1), segments=24, rings=12)
        cyl("V4_GoggleHousing_%d" % s, (0.050 * s, -0.800, 1.800), 0.045, 0.022,
            steel, axis="Y", segments=20)
    # Respirador y filtro.
    cyl("V4_Respirator", (0, -0.805, 1.655), 0.040, 0.055, brass, axis="Y", segments=20)
    cyl("V4_Filter", (0.105, -0.745, 1.640), 0.043, 0.10, steel, axis="Y", segments=20)
    cyl("V4_FilterCap", (0.120, -0.845, 1.66), 0.059, 0.026, brass, axis="Y", segments=20)
    for i in range(5):
        cube("V4_FilterGrille_%d" % i, (0.120, -0.862, 1.635 + i * 0.011),
             (0.086, 0.010, 0.006), dark, bevel=0.002)
    # Correas de la máscara.
    for s in (-1, 1):
        cube("V4_MaskStrap_%d" % s, (0.100 * s, -0.640, 1.70),
             (0.035, 0.22, 0.028), dark, bevel=0.004,
             rot=(0, 0, 0.10 * s))
    cube("V4_MaskStrapTop", (0, -0.645, 1.84), (0.23, 0.035, 0.028), dark,
         bevel=0.004)
    # Dientes/mandíbula inferior visible bajo la máscara.
    for i in range(4):
        cube("V4_Tooth_%d" % i, (-0.040 + i * 0.026, -0.780, 1.605),
             (0.013, 0.012, 0.026), bpy.data.materials["M_V4_Bone"], bevel=0.002)


def build_scene():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.filepath = RENDER
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.9

    world = bpy.data.worlds.new("V4_World")
    scene.world = world
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = (0.018, 0.020, 0.024, 1)
    bg.inputs["Strength"].default_value = 0.35

    # Suelo.
    bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 0, 0))
    ground = bpy.context.object
    ground.name = "V4_ReviewGround"
    gm = mat("M_V4_Ground", (0.030, 0.032, 0.035), 0.68)
    ground.data.materials.append(gm)

    # Cámara 3/4.
    cam_data = bpy.data.cameras.new("V4_ReviewCam")
    cam = bpy.data.objects.new("V4_ReviewCam", cam_data)
    col().objects.link(cam)
    cam.location = (4.6, -4.4, 1.55)
    target = Vector((0.0, -0.05, 0.82))
    cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam_data.lens = 60
    scene.camera = cam

    def area(name, loc, energy, size, color, rot):
        d = bpy.data.lights.new(name, "AREA")
        d.energy = energy
        d.shape = "DISK"
        d.size = size
        d.color = color
        o = bpy.data.objects.new(name, d)
        col().objects.link(o)
        o.location = loc
        o.rotation_euler = rot
        return o

    area("V4_Key", (3.0, -4.2, 4.2), 320, 3.0, (0.84, 0.90, 1.00),
         (math.radians(42), 0, math.radians(35)))
    area("V4_Fill", (-3.8, -2.8, 2.6), 90, 4.0, (0.60, 0.74, 1.0),
         (math.radians(68), 0, math.radians(-50)))
    area("V4_Rim", (-1.6, 3.8, 3.2), 240, 2.5, (0.62, 0.78, 1.0),
         (math.radians(118), 0, math.radians(200)))

    bpy.ops.render.render(write_still=True)


def main():
    reset()
    c = col()
    skin = textured("M_V4_Skin", FLESH_ALBEDO, (0.58, 0.54, 0.50), 0.80,
                    FLESH_NORMAL, 0.50)
    skin_dark = textured("M_V4_SkinDark", FLESH_ALBEDO, (0.34, 0.30, 0.27), 0.88,
                         FLESH_NORMAL, 0.45)
    canvas = textured("M_V4_Canvas", CLOTH_ALBEDO, (0.075, 0.060, 0.045), 0.94,
                      CLOTH_NORMAL, 0.55)
    leather = textured("M_V4_Leather", CLOTH_ALBEDO, (0.035, 0.026, 0.017), 0.80,
                       LEATHER_NORMAL, 0.75)
    # Acero neutro: la máscara y los bidones no deben heredar el óxido rojizo.
    steel = mat("M_V4_Steel", (0.14, 0.15, 0.16), 0.60, 1.0)
    brass = mat("M_V4_Brass", (0.16, 0.10, 0.035), 0.40, 0.9)
    dark = mat("M_V4_Dark", (0.012, 0.010, 0.009), 0.82)
    lens = mat("M_V4_Lens", (0.16, 0.09, 0.02), 0.22, 0.0,
               emission=(1.0, 0.38, 0.08), strength=0.45)
    bone = mat("M_V4_Bone", (0.42, 0.38, 0.30), 0.68)

    body = build_body(skin)
    build_surface_details(skin, skin_dark, canvas, leather, bone)
    build_extremities(skin)
    before_gear = set(bpy.data.objects)
    build_gear(skin, canvas, leather, steel, brass, dark, lens, bone)
    build_mask(skin, steel, brass, dark, lens)
    for ob in set(bpy.data.objects) - before_gear:
        ob.location.z -= 0.40

    # Pequeña inclinación global de la parte superior para acentuar la joroba.
    # (La geometría ya está modelada encorvada; no se rota el cuerpo entero.)

    # Suavizado y UVs de las piezas duras.
    for ob in list(c.objects):
        if ob.type != "MESH" or ob.name in ("V4_Body", "V4_ReviewGround"):
            continue
        smooth(ob, 38)
        uv_unwrap(ob)

    bpy.ops.wm.save_as_mainfile(filepath=BLEND)

    # Exportar solo el arte (sin suelo/cámara/luces).
    bpy.ops.object.select_all(action="DESELECT")
    meshes = [o for o in c.objects if o.type == "MESH" and o.name != "V4_ReviewGround"]
    for o in meshes:
        o.hide_render = False
        o.hide_viewport = False
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.export_scene.gltf(filepath=GLB, export_format="GLB",
                              use_selection=True, export_yup=True,
                              export_apply=True, export_animations=False,
                              export_cameras=False, export_lights=False,
                              export_materials="EXPORT", export_texcoords=True,
                              export_normals=True)
    print("COLLECTOR_V4_GLB", GLB, len(meshes))
    build_scene()
    print("COLLECTOR_V4_RENDER", RENDER)
    print("COLLECTOR_V4_SAVED", BLEND)


main()
