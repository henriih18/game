"""El Coleccionista — v2 de escultura controlada.

Objetivo: corregir la silueta respecto a la referencia oficial. Criatura
emaciada y jorobada, con brazos largos, garras, máscara de gas, mochila
cargada de trastos, taparrabos y farol. Sin abrigo largo ni capucha: la
referencia muestra el cuerpo escuálido y el equipo de saqueo.

Pipeline:
- cuerpo base con esqueleto + Skin + Subsurf + Remesh + Smooth + Displace,
- costillas y columna como detalle geométrico,
- máscara de gas dura, mochila con ollas/botellas/manta, correas, taparrabos,
  llaves y farol,
- UVs Smart Project, materiales PBR reutilizados y export GLB.

Todo se guarda en `nexus/nivel_01/FM_COLLECTOR_V2.blend` y se exporta a
`assets/models/fm/collector_creature_v2.glb`. No toca el máster del nivel ni
la referencia.
"""

import math
import os

import bpy
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
BLEND = os.path.join(ROOT, "nexus/nivel_01/FM_COLLECTOR_V2.blend")
GLB = os.path.join(ROOT, "assets/models/fm/collector_creature_v2.glb")
RENDER = "/tmp/opencode/collector_v2.png"
COL_NAME = "COLLECTOR_V2"


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def reset():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.curves, bpy.data.materials,
                  bpy.data.images, bpy.data.cameras, bpy.data.lights):
        for item in list(block):
            if item.users == 0:
                block.remove(item)


def col():
    c = bpy.data.collections.get(COL_NAME)
    if c is None:
        c = bpy.data.collections.new(COL_NAME)
        bpy.context.scene.collection.children.link(c)
    return c


def link(obj, c=None):
    c = c or col()
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    c.objects.link(obj)
    return obj


def mat(name, color, rough=0.6, metal=0.0, emission=None, strength=0.0):
    m = bpy.data.materials.get(name)
    if m is not None:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
    return m


def textured(name, path, color, rough=0.8, normal_path=None, normal_strength=0.6):
    m = bpy.data.materials.get(name)
    if m is not None:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(path, check_existing=True)
    tex.location = (-420, 240)
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    if normal_path and os.path.exists(normal_path):
        ntex = nt.nodes.new("ShaderNodeTexImage")
        ntex.image = bpy.data.images.load(normal_path, check_existing=True)
        ntex.image.colorspace_settings.name = "Non-Color"
        ntex.location = (-420, -60)
        nmap = nt.nodes.new("ShaderNodeNormalMap")
        nmap.inputs["Strength"].default_value = normal_strength
        nmap.location = (-180, -60)
        nt.links.new(ntex.outputs["Color"], nmap.inputs["Color"])
        nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def cube(name, center, size, material, bevel=0.0, segments=2, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    ob = bpy.context.object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel > 0:
        mod = ob.modifiers.new("Bevel", "BEVEL")
        mod.width = bevel
        mod.segments = segments
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.modifier_apply(modifier=mod.name)
    if any(rot):
        ob.rotation_euler = tuple(math.radians(a) for a in rot)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    ob.data.materials.append(material)
    link(ob)
    return ob


def cyl(name, center, radius, depth, material, axis="Z", segments=20, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=segments, radius=radius, depth=depth, location=center)
    ob = bpy.context.object
    ob.name = name
    if axis == "X":
        ob.rotation_euler[1] = math.radians(90)
    elif axis == "Y":
        ob.rotation_euler[0] = math.radians(90)
    if any(rot):
        ob.rotation_euler[0] += math.radians(rot[0])
        ob.rotation_euler[1] += math.radians(rot[1])
        ob.rotation_euler[2] += math.radians(rot[2])
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    ob.data.materials.append(material)
    link(ob)
    return ob


def sphere(name, center, radius, material, scale=(1, 1, 1), segments=32, rings=16):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments, ring_count=rings, radius=radius, location=center)
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(material)
    link(ob)
    return ob


def torus(name, center, major, minor, material, rot=(0, 0, 0), scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major, minor_radius=minor, major_segments=32,
        minor_segments=10, location=center)
    ob = bpy.context.object
    ob.name = name
    ob.rotation_euler = tuple(math.radians(a) for a in rot)
    ob.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    ob.data.materials.append(material)
    link(ob)
    return ob


def cone(name, center, r1, r2, depth, material, segments=16, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(
        vertices=segments, radius1=r1, radius2=r2, depth=depth, location=center)
    ob = bpy.context.object
    ob.name = name
    ob.rotation_euler = tuple(math.radians(a) for a in rot)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    ob.data.materials.append(material)
    link(ob)
    return ob


def segment(name, a, b, r1, r2, material, segments=16):
    a = Vector(a)
    b = Vector(b)
    direction = b - a
    length = direction.length
    mid = (a + b) * 0.5
    ob = cone(name, tuple(mid), r1, r2, length, material, segments=segments)
    quat = direction.to_track_quat("Z", "Y")
    ob.rotation_euler = quat.to_euler()
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    return ob


def uv_unwrap(obj):
    if obj is None or obj.type != "MESH":
        return
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.015)
    bpy.ops.object.mode_set(mode="OBJECT")


def smooth(obj, angle=40.0):
    if obj is None or obj.type != "MESH":
        return
    for poly in obj.data.polygons:
        poly.use_smooth = True
    obj.data.update()


# ---------------------------------------------------------------------------
# Cuerpo
# ---------------------------------------------------------------------------

def build_body(material_skin):
    verts = []
    edges = []
    radii = []

    def add(co, r):
        verts.append(co)
        radii.append(r)
        return len(verts) - 1

    # Columna jorobada: el frente es -Y.
    pelvis = add((0.0, 0.00, 0.96), 0.155)
    spine1 = add((0.0, -0.03, 1.14), 0.135)
    spine2 = add((0.0, -0.10, 1.32), 0.150)
    chest = add((0.0, -0.18, 1.52), 0.205)
    neck = add((0.0, -0.24, 1.78), 0.080)
    head = add((0.0, -0.28, 1.96), 0.115)
    edges += [(pelvis, spine1), (spine1, spine2), (spine2, chest),
              (chest, neck), (neck, head)]

    for s in (-1, 1):
        shoulder = add((0.29 * s, -0.16, 1.66), 0.095)
        elbow = add((0.46 * s, -0.07, 1.20), 0.062)
        wrist = add((0.53 * s, 0.00, 0.78), 0.042)
        hand = add((0.55 * s, 0.01, 0.66), 0.058)
        edges += [(chest, shoulder), (shoulder, elbow), (elbow, wrist),
                  (wrist, hand)]
        hip = add((0.15 * s, 0.00, 0.92), 0.110)
        knee = add((0.18 * s, -0.02, 0.50), 0.082)
        ankle = add((0.20 * s, 0.00, 0.10), 0.052)
        foot = add((0.20 * s, -0.13, 0.06), 0.060)
        edges += [(pelvis, hip), (hip, knee), (knee, ankle), (ankle, foot)]

    me = bpy.data.meshes.new("CollectorV2Body")
    me.from_pydata(verts, edges, [])
    me.update()
    ob = bpy.data.objects.new("CollectorV2_Body", me)
    link(ob)
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    skin = ob.modifiers.new("Skin", "SKIN")
    skin.use_smooth_shade = True
    bpy.context.view_layer.update()
    layer = me.skin_vertices[0].data
    for i, r in enumerate(radii):
        layer[i].radius = (r, r)
    layer[pelvis].use_root = True
    bpy.ops.object.modifier_apply(modifier=skin.name)

    sub = ob.modifiers.new("Sub", "SUBSURF")
    sub.levels = 2
    sub.render_levels = 2
    bpy.ops.object.modifier_apply(modifier=sub.name)

    # Cráneo, mandíbula, manos y pies.
    parts = [ob]
    parts.append(sphere("V2_Skull", (0, -0.28, 1.99), 0.115, material_skin,
                        scale=(0.92, 1.08, 1.16)))
    parts.append(sphere("V2_Jaw", (0, -0.36, 1.89), 0.075, material_skin,
                        scale=(0.82, 0.94, 0.72)))
    for s in (-1, 1):
        parts.append(sphere("V2_Hand_%d" % s, (0.55 * s, 0.01, 0.65), 0.060,
                            material_skin, scale=(0.82, 1.10, 0.55)))
        for i in range(4):
            x = 0.55 * s + (i - 1.5) * 0.022
            parts.append(segment("V2_Finger_%d_%d" % (s, i),
                                 (x, 0.01, 0.64),
                                 (x + 0.012 * s, -0.02, 0.53),
                                 0.012, 0.008, material_skin, 8))
        parts.append(segment("V2_Thumb_%d" % s,
                             (0.55 * s - 0.03 * s, 0.00, 0.66),
                             (0.58 * s - 0.05 * s, -0.05, 0.60),
                             0.012, 0.008, material_skin, 8))
        parts.append(sphere("V2_Foot_%d" % s, (0.20 * s, -0.16, 0.06), 0.070,
                            material_skin, scale=(0.78, 1.55, 0.52)))
        for i in range(3):
            x = 0.20 * s + (i - 1) * 0.030
            parts.append(segment("V2_Toe_%d_%d" % (s, i),
                                 (x, -0.24, 0.05),
                                 (x, -0.31, 0.035),
                                 0.016, 0.010, material_skin, 8))

    for part in parts[1:]:
        part.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.join()
    ob = bpy.context.object

    rem = ob.modifiers.new("Fuse", "REMESH")
    rem.mode = "VOXEL"
    rem.voxel_size = 0.012
    rem.use_smooth_shade = True
    bpy.ops.object.modifier_apply(modifier=rem.name)

    sm = ob.modifiers.new("Smooth", "SMOOTH")
    sm.factor = 0.5
    sm.iterations = 3
    bpy.ops.object.modifier_apply(modifier=sm.name)

    # Piel: ruido fino para romper la superficie.
    tex = bpy.data.textures.new("V2_SkinNoise", "CLOUDS")
    tex.noise_scale = 0.045
    disp = ob.modifiers.new("SkinDetail", "DISPLACE")
    disp.texture = tex
    disp.strength = 0.004
    disp.mid_level = 0.5
    bpy.ops.object.modifier_apply(modifier=disp.name)

    smooth(ob, 36)
    ob.data.materials.clear()
    ob.data.materials.append(material_skin)
    uv_unwrap(ob)
    return ob


def add_ribs(skin):
    for i, (z, rx, ry) in enumerate((
            (1.23, 0.155, 0.115), (1.32, 0.175, 0.125),
            (1.41, 0.195, 0.135), (1.50, 0.205, 0.140))):
        torus("V2_Rib_%d" % i, (0, -0.06, z), rx, 0.012, skin,
              rot=(90, 0, 0), scale=(1.0, ry / rx, 1.0))
    for i in range(5):
        sphere("V2_Spine_%d" % i, (0, 0.18 + 0.006 * i, 1.20 + i * 0.085),
               0.022, skin, scale=(0.55, 1.0, 0.85))


# ---------------------------------------------------------------------------
# Equipo
# ---------------------------------------------------------------------------

def build_gear(skin, canvas, leather, steel, brass, dark, lens, bone):
    # Taparrabos de tela rasgada.
    torus("V2_Belt", (0, 0, 0.98), 0.20, 0.025, leather,
          rot=(90, 0, 0), scale=(1.0, 0.62, 1.0))
    for i in range(10):
        a = (i / 10.0) * math.tau
        x = math.cos(a) * 0.19
        y = math.sin(a) * 0.115
        length = 0.24 + 0.07 * (i % 3)
        cube("V2_Rag_%d" % i, (x, y, 0.86 - length * 0.5),
             (0.075, 0.020, length), canvas, bevel=0.005, rot=(0, 0, math.degrees(a)))

    # Mochila: bastidor, saco, manta, ollas y botellas.
    for s in (-1, 1):
        cube("V2_PackBar_%d" % s, (0.24 * s, 0.30, 1.36),
             (0.035, 0.035, 0.86), steel, bevel=0.005)
    cube("V2_PackCross", (0, 0.30, 1.72), (0.50, 0.035, 0.035), steel, bevel=0.005)
    sphere("V2_PackSack", (0, 0.40, 1.46), 0.32, canvas,
           scale=(1.05, 0.72, 0.95))
    cyl("V2_PackRoll", (0, 0.42, 1.94), 0.105, 0.56, canvas, axis="X")
    for s in (-1, 1):
        cyl("V2_Pot_%d" % s, (0.42 * s, 0.35, 1.38), 0.115, 0.20, steel,
            axis="Y", segments=18)
        torus("V2_PotRim_%d" % s, (0.42 * s, 0.45, 1.38), 0.105, 0.012, steel,
              rot=(90, 0, 0))
        cyl("V2_Bottle_%d" % s, (0.28 * s, 0.46, 1.16), 0.045, 0.16, brass,
            segments=12)
    cube("V2_PackFlap", (0, 0.31, 1.78), (0.42, 0.10, 0.18), leather, bevel=0.02)

    # Correas al pecho y hombros.
    for s in (-1, 1):
        cube("V2_Strap_%d" % s, (0.19 * s, -0.19, 1.50),
             (0.060, 0.030, 0.58), leather, bevel=0.005, rot=(0, 0, 4 * s))
        cube("V2_ShoulderStrap_%d" % s, (0.24 * s, -0.10, 1.72),
             (0.075, 0.30, 0.030), leather, bevel=0.005, rot=(8, 0, 0))
    cube("V2_ChestStrap", (0, -0.24, 1.42), (0.46, 0.030, 0.050), leather, bevel=0.005)

    # Máscara de gas.
    cube("V2_MaskPlate", (0, -0.40, 2.00), (0.26, 0.075, 0.23), dark, bevel=0.025, segments=3)
    for s in (-1, 1):
        torus("V2_GoggleRing_%d" % s, (0.072 * s, -0.445, 2.04),
              0.058, 0.014, brass, rot=(90, 0, 0))
        cyl("V2_GoggleLens_%d" % s, (0.072 * s, -0.452, 2.04), 0.048, 0.020,
            lens, axis="Y", segments=20)
        cube("V2_MaskStrap_%d" % s, (0.13 * s, -0.30, 2.03),
             (0.025, 0.20, 0.040), leather, bevel=0.004)
    cyl("V2_Filter", (0, -0.47, 1.92), 0.070, 0.12, steel, axis="Y", segments=18)
    cyl("V2_FilterCap", (0, -0.535, 1.92), 0.075, 0.02, dark, axis="Y", segments=18)
    for i in range(5):
        torus("V2_HoseRing_%d" % i, (0.10 + i * 0.035, 0.04 + i * 0.05, 1.86 - i * 0.03),
              0.025, 0.008, dark, rot=(0, 90, 0))

    # Cinturón, llaves y farol.
    cube("V2_BeltBuckle", (0, -0.16, 0.98), (0.09, 0.03, 0.075), brass, bevel=0.006)
    for i in range(5):
        x = -0.10 + i * 0.05
        cyl("V2_KeyRing_%d" % i, (x, -0.19, 0.88), 0.012, 0.05, brass,
            axis="Z", segments=8)
        cube("V2_Key_%d" % i, (x, -0.21, 0.83), (0.018, 0.008, 0.055), brass, bevel=0.002)
    cube("V2_LanternBody", (0.33, -0.04, 0.80), (0.14, 0.14, 0.22), steel, bevel=0.02)
    cube("V2_LanternCore", (0.33, -0.04, 0.80), (0.08, 0.08, 0.14), lens, bevel=0.01)
    cube("V2_LanternTop", (0.33, -0.04, 0.93), (0.16, 0.16, 0.03), steel, bevel=0.008)
    torus("V2_LanternHandle", (0.33, -0.04, 0.98), 0.075, 0.010, steel, rot=(90, 0, 0))
    for i in range(4):
        cube("V2_LanternBar_%d" % i,
             (0.33 + (0.06 if i % 2 else -0.06), -0.04 + (0.06 if i > 1 else -0.06), 0.80),
             (0.010, 0.010, 0.22), steel)
    light_data = bpy.data.lights.new("V2_LanternLight", "POINT")
    light_data.energy = 8.0
    light_data.color = (1.0, 0.62, 0.25)
    light_data.shadow_soft_size = 0.15
    light = bpy.data.objects.new("V2_LanternLight", light_data)
    light.location = (0.33, -0.04, 0.80)
    link(light)
    bpy.context.scene.collection.objects.link(light)

    # Garras de manos y pies.
    for s in (-1, 1):
        for i in range(4):
            x = 0.55 * s + (i - 1.5) * 0.022
            cone("V2_ClawHand_%d_%d" % (s, i), (x + 0.012 * s, -0.04, 0.51),
                 0.010, 0.002, 0.055, bone, segments=8, rot=(90, 0, 0))
        for i in range(3):
            x = 0.20 * s + (i - 1) * 0.030
            cone("V2_ClawFoot_%d_%d" % (s, i), (x, -0.33, 0.03),
                 0.012, 0.002, 0.060, bone, segments=8, rot=(90, 0, 0))


# ---------------------------------------------------------------------------
# Escena, render y export
# ---------------------------------------------------------------------------

def build_scene():
    reset()
    c = col()
    skin = textured("M_V2_Skin",
                    os.path.join(ROOT, "assets/art/fm/flesh_albedo.png"),
                    (0.62, 0.52, 0.42), 0.80,
                    os.path.join(ROOT, "assets/art/fm/flesh_normal.png"), 0.6)
    canvas = textured("M_V2_Canvas",
                      os.path.join(ROOT, "assets/art/fm/cloth_albedo.png"),
                      (0.16, 0.13, 0.09), 0.95)
    leather = mat("M_V2_Leather", (0.045, 0.032, 0.022), 0.82)
    steel = mat("M_V2_Steel", (0.16, 0.17, 0.17), 0.42, 0.9)
    brass = mat("M_V2_Brass", (0.48, 0.33, 0.12), 0.34, 0.95)
    dark = mat("M_V2_Dark", (0.018, 0.015, 0.012), 0.62)
    lens = mat("M_V2_Lens", (0.7, 0.45, 0.10), 0.20, 0.0,
               emission=(1.0, 0.55, 0.12), strength=3.0)
    bone = mat("M_V2_Bone", (0.60, 0.54, 0.42), 0.70)

    body = build_body(skin)
    add_ribs(skin)
    build_gear(skin, canvas, leather, steel, brass, dark, lens, bone)

    # UVs para el equipo principal (los primitivos tienen UVs propias).
    for ob in c.objects:
        if ob.type == "MESH" and ob.name in {
                "CollectorV2_Body", "V2_PackSack", "V2_Rag_0", "V2_Rag_1",
                "V2_Rag_2", "V2_Rag_3", "V2_Rag_4", "V2_Rag_5"}:
            uv_unwrap(ob)

    # Suelo de revisión.
    cube("ReviewGround", (0, 0, -0.04), (10, 10, 0.02), dark, bevel=0.0)

    # Cámara 3/4.
    cam_data = bpy.data.cameras.new("ReviewCam")
    cam = bpy.data.objects.new("ReviewCam", cam_data)
    c.objects.link(cam)
    cam.location = (3.4, -5.6, 1.55)
    target = Vector((0, 0, 1.15))
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam_data.lens = 55
    bpy.context.scene.camera = cam

    def area(name, loc, energy, size, color, rot):
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        data.color = color
        ob = bpy.data.objects.new(name, data)
        c.objects.link(ob)
        ob.location = loc
        ob.rotation_euler = tuple(math.radians(a) for a in rot)
        return ob

    area("Key", (2.6, -3.6, 4.0), 420, 3.0, (1.0, 0.86, 0.70), (36, 0, 36))
    area("Fill", (-3.2, -2.4, 2.4), 180, 4.0, (0.62, 0.76, 1.0), (64, 0, -52))
    area("Rim", (-1.4, 3.4, 3.0), 320, 2.5, (0.72, 0.84, 1.0), (116, 0, 192))

    scene = bpy.context.scene
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.filepath = RENDER
    scene.render.image_settings.file_format = "PNG"
    try:
        scene.render.engine = "BLENDER_EEVEE"
    except TypeError:
        pass
    scene.render.film_transparent = False
    scene.world.color = (0.015, 0.018, 0.020)
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"

    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("COLLECTOR_V2_SAVED", BLEND)

    bpy.ops.render.render(write_still=True)
    print("COLLECTOR_V2_RENDER", RENDER)

    # Export GLB: solo mallas de la colección, sin cámara/luces/suelo.
    bpy.ops.object.select_all(action="DESELECT")
    export_objects = [ob for ob in c.objects if ob.type == "MESH" and ob.name != "ReviewGround"]
    for ob in export_objects:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = export_objects[0] if export_objects else None
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
        export_texcoords=True,
        export_normals=True,
    )
    print("COLLECTOR_V2_GLB", GLB)


if __name__ == "__main__":
    build_scene()
