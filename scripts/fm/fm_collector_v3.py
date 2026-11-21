"""El Coleccionista v3 — abrigo, capucha y mochila estructurados.

Parte del cuerpo orgánico de FM_COLLECTOR_SCULPT.blend, oculta el equipo de
bolas y construye una silueta de saqueador: abrigo largo abierto, capucha,
mangas, perneras y mochila con bastidor, saco, manta y ollas.

Se ejecuta headless:
  blender -b nexus/nivel_01/FM_COLLECTOR_SCULPT.blend \
      --python scripts/fm/fm_collector_v3.py

Guarda FM_COLLECTOR_V3.blend, exporta collector_creature_v3.glb y renderiza
/tmp/opencode/collector_v3.png. No toca el máster del nivel ni la referencia.
"""

import math
import os

import bpy
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
OUT_BLEND = os.path.join(ROOT, "nexus/nivel_01/FM_COLLECTOR_V3.blend")
OUT_GLB = os.path.join(ROOT, "assets/models/fm/collector_creature_v3.glb")
RENDER = "/tmp/opencode/collector_v3.png"
TEX_DIR = os.path.join(ROOT, "assets/art/fm/collector")
CLOTH_N = os.path.join(TEX_DIR, "T_Collector_Cloth_N.png")
LEATHER_N = os.path.join(TEX_DIR, "T_Collector_Leather_N.png")
CLOTH_BC = os.path.join(TEX_DIR, "T_Collector_Cloth_BC.png")
LEATHER_BC = os.path.join(TEX_DIR, "T_Collector_Leather_BC.png")


def mat(name, color, rough=0.8, metal=0.0, normal=None, strength=0.55, emission=None,
        albedo=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if albedo and os.path.exists(albedo):
        img = bpy.data.images.load(albedo, check_existing=True)
        img.colorspace_settings.name = "sRGB"
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = img
        tex.interpolation = "Linear"
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 1.6
    if normal and os.path.exists(normal):
        img = bpy.data.images.load(normal, check_existing=True)
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = img
        tex.interpolation = "Linear"
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nm.inputs["Strength"].default_value = strength
        nt.links.new(tex.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    m.diffuse_color = (*color, 1.0)
    return m


def make_materials():
    return {
        "canvas": mat("M_V3_Canvas", (0.014, 0.011, 0.008), 0.94, normal=CLOTH_N, strength=0.70, albedo=CLOTH_BC),
        "leather": mat("M_V3_Leather", (0.009, 0.0065, 0.004), 0.88, normal=LEATHER_N, strength=0.55, albedo=LEATHER_BC),
        "dark": mat("M_V3_Dark", (0.004, 0.0035, 0.003), 0.90, normal=LEATHER_N, strength=0.35, albedo=LEATHER_BC),
        "steel": mat("M_V3_Steel", (0.18, 0.19, 0.19), 0.44, 0.9, normal=LEATHER_N, strength=0.18),
        "brass": mat("M_V3_Brass", (0.20, 0.13, 0.045), 0.42, 0.9, normal=LEATHER_N, strength=0.2),
        "lens": mat("M_V3_Lens", (0.22, 0.13, 0.04), 0.22, 0.0, emission=(1.0, 0.55, 0.16)),
        "skin": mat("M_V3_Skin", (0.10, 0.075, 0.055), 0.82),
    }


def link(obj):
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    bpy.context.scene.collection.objects.link(obj)


def mesh_obj(name, verts, faces, material, uvs=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(material)
    if uvs:
        layer = me.uv_layers.new(name="UVMap")
        idx = 0
        for poly in me.polygons:
            n = poly.loop_total
            for k in range(n):
                layer.data[poly.loop_start + k].uv = uvs[idx + k]
            idx += n
    for p in me.polygons:
        p.use_smooth = True
    return ob


def loft(name, ring_defs, material, closed=False, thickness=0.0, uv_scale=1.0,
         jagged=0.0, fold=0.0):
    """ring_defs: list of (z, cx, cy, rx, ry, gap_deg)."""
    verts, faces, uvs = [], [], []
    n = 28
    for ri, (z, cx, cy, rx, ry, gap) in enumerate(ring_defs):
        span = 360.0 - gap
        start = 270.0 + gap * 0.5
        for i in range(n + (0 if closed else 1)):
            if closed:
                ang = math.radians(start + span * i / n)
            else:
                ang = math.radians(start + span * i / n)
            wobble = 1.0 + fold * math.sin(6.0 * ang + z * 7.0)
            x = cx + math.cos(ang) * rx * wobble
            y = cy + math.sin(ang) * ry * wobble
            zz = z
            if jagged and ri == 0:
                zz += jagged * math.sin(i * 5.1) * 0.5
            verts.append((x, y, zz))
    cols = n + (0 if closed else 1)
    for ri in range(len(ring_defs) - 1):
        for i in range(n if closed else cols - 1):
            a = ri * cols + i
            b = ri * cols + (i + 1) % cols if closed else a + 1
            c = (ri + 1) * cols + (i + 1) % cols if closed else b + cols
            d = (ri + 1) * cols + i
            faces.append((a, b, c, d))
            u0 = i / (n if closed else cols - 1)
            u1 = (i + 1) / (n if closed else cols - 1)
            v0 = ri / (len(ring_defs) - 1)
            v1 = (ri + 1) / (len(ring_defs) - 1)
            uvs.extend([(u0 * uv_scale, v0), (u1 * uv_scale, v0),
                        (u1 * uv_scale, v1), (u0 * uv_scale, v1)])
    ob = mesh_obj(name, verts, faces, material, uvs)
    if thickness > 0:
        sol = ob.modifiers.new("Thickness", "SOLIDIFY")
        sol.thickness = thickness
        sol.offset = 0.0
        sol.use_rim = True
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)
        bpy.ops.object.modifier_apply(modifier=sol.name)
    return ob


def tube(name, points, radii, material, sides=12, thickness=0.0):
    verts, faces, uvs = [], [], []
    for pi, (p, r) in enumerate(zip(points, radii)):
        p = Vector(p)
        if pi == 0:
            tangent = Vector(points[1]) - p
        elif pi == len(points) - 1:
            tangent = p - Vector(points[pi - 1])
        else:
            tangent = Vector(points[pi + 1]) - Vector(points[pi - 1])
        tangent.normalize()
        up = Vector((0, 0, 1))
        if abs(tangent.dot(up)) > 0.95:
            up = Vector((0, 1, 0))
        n1 = tangent.cross(up).normalized()
        n2 = tangent.cross(n1).normalized()
        for i in range(sides):
            ang = 2 * math.pi * i / sides
            off = n1 * (math.cos(ang) * r) + n2 * (math.sin(ang) * r)
            verts.append(tuple(p + off))
    for pi in range(len(points) - 1):
        for i in range(sides):
            a = pi * sides + i
            b = pi * sides + (i + 1) % sides
            c = (pi + 1) * sides + (i + 1) % sides
            d = (pi + 1) * sides + i
            faces.append((a, b, c, d))
            v0 = pi / (len(points) - 1)
            v1 = (pi + 1) / (len(points) - 1)
            u0 = i / sides
            u1 = (i + 1) / sides
            uvs.extend([(u0, v0), (u1, v0), (u1, v1), (u0, v1)])
    ob = mesh_obj(name, verts, faces, material, uvs)
    if thickness > 0:
        sol = ob.modifiers.new("Thickness", "SOLIDIFY")
        sol.thickness = thickness
        sol.offset = 0.0
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)
        bpy.ops.object.modifier_apply(modifier=sol.name)
    return ob


def box(name, center, size, material, bevel=0.02, segments=3, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    ob = bpy.context.object
    ob.name = name
    ob.scale = size
    ob.rotation_euler = rot
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if bevel > 0:
        mod = ob.modifiers.new("Bevel", "BEVEL")
        mod.width = bevel
        mod.segments = segments
        mod.limit_method = "ANGLE"
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)
        bpy.ops.object.modifier_apply(modifier=mod.name)
    ob.data.materials.append(material)
    return ob


def cyl(name, center, radius, depth, material, axis="Z", segments=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=segments, radius=radius, depth=depth, location=center)
    ob = bpy.context.object
    ob.name = name
    if axis == "X":
        ob.rotation_euler[1] = math.radians(90)
    elif axis == "Y":
        ob.rotation_euler[0] = math.radians(90)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    ob.data.materials.append(material)
    return ob


def ellipsoid(name, center, scale, material, segments=24, rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=center)
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    ob.data.materials.append(material)
    for poly in ob.data.polygons:
        poly.use_smooth = True
    return ob


def uv_smart(ob):
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    try:
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.02)
        bpy.ops.object.mode_set(mode="OBJECT")
    except Exception as exc:  # noqa: BLE001
        print("UV_SKIP", ob.name, exc)


def hide_old():
    hide_prefixes = (
        "Collector_Coat", "Collector_Mantle", "Collector_Cloak", "Collector_ChestWrap",
        "Collector_Shoulder", "Collector_Sleeve", "Collector_Pant", "Collector_Rag_",
        "Collector_HemStrip_", "Collector_Hood", "Collector_Pack", "Collector_Roll",
        "Collector_Drum", "Collector_Strap", "Collector_Buckle", "Collector_Pouch",
        "Collector_Belt", "Collector_OuterBelt", "Collector_BootToe",
        "Collector_Boot_", "Collector_Glove_",
        "Collector_Eye_",
    )
    for ob in bpy.data.objects:
        if ob.type != "MESH":
            continue
        if any(ob.name.startswith(p) for p in hide_prefixes):
            ob.hide_render = True
            ob.hide_set(True)


def build(m):
    # Abrigo largo, abierto al frente.
    coat_rings = [
        (0.26, 0.0, 0.02, 0.42, 0.30, 30),
        (0.50, 0.0, 0.01, 0.39, 0.28, 30),
        (0.82, 0.0, 0.00, 0.35, 0.26, 30),
        (1.14, 0.0, -0.03, 0.33, 0.25, 28),
        (1.42, 0.0, -0.07, 0.35, 0.27, 28),
        (1.66, 0.0, -0.12, 0.38, 0.29, 26),
        (1.88, 0.0, -0.17, 0.40, 0.30, 26),
    ]
    coat = loft("V3_Coat", coat_rings, m["canvas"], thickness=0.028, uv_scale=2.4, jagged=0.10, fold=0.035)
    uv_smart(coat)
    # Camisa interior: cierra el pecho para que no se vea piel bajo el abrigo.
    shirt = loft("V3_Shirt", [
        (0.95, 0.0, -0.02, 0.30, 0.23, 18),
        (1.20, 0.0, -0.05, 0.32, 0.24, 18),
        (1.48, 0.0, -0.08, 0.33, 0.25, 18),
        (1.72, 0.0, -0.12, 0.31, 0.24, 18),
        (1.84, 0.0, -0.14, 0.27, 0.21, 18),
    ], m["canvas"], thickness=0.018, uv_scale=1.8)
    uv_smart(shirt)
    for li in range(5):
        lace = box("V3_ShirtLace_%d" % li, (0.0, -0.30, 1.24 + li * 0.11), (0.10, 0.018, 0.018),
                   m["leather"], 0.004, 2)
        uv_smart(lace)
    collar = loft("V3_Collar", [
        (1.84, 0.0, -0.14, 0.30, 0.24, 74),
        (2.00, 0.0, -0.16, 0.28, 0.23, 74),
        (2.08, 0.0, -0.17, 0.25, 0.21, 74),
    ], m["leather"], thickness=0.025, uv_scale=1.6)
    uv_smart(collar)

    # Capucha abierta al frente.
    hood_rings = [
        (2.02, 0.0, -0.02, 0.22, 0.22, 96),
        (2.10, 0.0, -0.04, 0.24, 0.23, 96),
        (2.18, 0.0, -0.06, 0.22, 0.22, 96),
        (2.25, 0.0, -0.08, 0.17, 0.18, 96),
        (2.30, 0.0, -0.10, 0.11, 0.12, 96),
    ]
    hood = loft("V3_Hood", hood_rings, m["canvas"], thickness=0.026, uv_scale=1.8, fold=0.03)
    uv_smart(hood)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.205, minor_radius=0.028, major_segments=32,
        minor_segments=8, location=(0.0, -0.72, 2.04),
        rotation=(math.radians(90), 0, 0))
    brim = bpy.context.object
    brim.name = "V3_HoodBrim"
    brim.data.materials.append(m["leather"])
    hood_top = ellipsoid("V3_HoodTop", (0.0, -0.10, 2.30), (0.11, 0.10, 0.055), m["canvas"])
    uv_smart(hood_top)

    # Solapas del abrigo: rompen el frente plano y marcan la abertura.
    for s in (-1, 1):
        lapel = box("V3_Lapel_%s" % ("L" if s < 0 else "R"),
                    (0.17 * s, -0.31, 1.58), (0.10, 0.035, 0.52),
                    m["leather"], 0.012, 2,
                    rot=(math.radians(8), 0, math.radians(-7 * s)))
        uv_smart(lapel)
    cape = loft("V3_ShoulderCape", [
        (1.68, 0.0, -0.12, 0.39, 0.29, 58),
        (1.80, 0.0, -0.14, 0.41, 0.30, 58),
        (1.90, 0.0, -0.16, 0.36, 0.27, 58),
    ], m["canvas"], thickness=0.022, uv_scale=1.8)
    uv_smart(cape)

    # Mangas y perneras.
    for s in (-1, 1):
        sleeve = tube("V3_Sleeve_%s" % ("L" if s < 0 else "R"), [
            (0.37 * s, -0.10, 1.80), (0.41 * s, -0.09, 1.66),
            (0.47 * s, -0.07, 1.50), (0.52 * s, -0.04, 1.32),
            (0.56 * s, -0.01, 1.14), (0.58 * s, 0.00, 0.98),
            (0.59 * s, 0.01, 0.88),
        ], [0.130, 0.126, 0.120, 0.112, 0.102, 0.090, 0.078], m["canvas"], thickness=0.022)
        uv_smart(sleeve)
        pant = tube("V3_Pant_%s" % ("L" if s < 0 else "R"), [
            (0.21 * s, 0.0, 0.98), (0.23 * s, -0.01, 0.76),
            (0.24 * s, -0.02, 0.54), (0.25 * s, -0.01, 0.32),
            (0.27 * s, 0.0, 0.14),
        ], [0.175, 0.165, 0.150, 0.125, 0.095], m["canvas"], thickness=0.02)
        uv_smart(pant)
        cuff = cyl("V3_Cuff_%s" % ("L" if s < 0 else "R"), (0.62 * s, 0.01, 0.88), 0.105, 0.075, m["leather"], "Z", 18)
        uv_smart(cuff)
        tag = "L" if s < 0 else "R"
        sole = box("V3_BootSole_%s" % tag, (0.27 * s, -0.09, 0.025), (0.20, 0.36, 0.045), m["dark"], 0.018, 2)
        uv_smart(sole)
        foot = ellipsoid("V3_BootFoot_%s" % tag, (0.27 * s, -0.09, 0.100), (0.098, 0.185, 0.080), m["leather"])
        uv_smart(foot)
        toe = ellipsoid("V3_BootToe_%s" % tag, (0.27 * s, -0.245, 0.088), (0.090, 0.095, 0.064), m["leather"])
        uv_smart(toe)
        shaft = cyl("V3_BootShaft_%s" % tag, (0.27 * s, -0.02, 0.185), 0.090, 0.150, m["leather"], "Z", 18)
        uv_smart(shaft)
        for li in range(3):
            lace = box("V3_BootLace_%s_%d" % (tag, li), (0.27 * s, -0.12 + li * 0.050, 0.20), (0.13, 0.010, 0.010), m["brass"], 0.003, 1)
            uv_smart(lace)
        glove = ellipsoid("V3_Glove_%s" % tag, (0.63 * s, 0.0, 0.73), (0.078, 0.10, 0.11), m["leather"])
        uv_smart(glove)
        for fi in range(4):
            finger = ellipsoid("V3_Finger_%s_%d" % (tag, fi), (0.63 * s + (fi - 1.5) * 0.035, -0.095, 0.68), (0.017, 0.055, 0.022), m["leather"])
            uv_smart(finger)
        thumb = ellipsoid("V3_Thumb_%s" % tag, (0.57 * s, -0.05, 0.73), (0.022, 0.055, 0.026), m["leather"])
        uv_smart(thumb)
        wrap = cyl("V3_WristWrap_%s" % tag, (0.62 * s, 0.01, 0.84), 0.105, 0.075, m["canvas"], "Z", 18)
        uv_smart(wrap)

    # Mochila estructurada.
    frame = box("V3_Pack_Frame", (0.0, 0.31, 1.66), (0.52, 0.10, 0.70), m["steel"], 0.025, 2)
    uv_smart(frame)
    sack = ellipsoid("V3_Pack_Sack", (0.0, 0.39, 1.52), (0.26, 0.15, 0.28), m["canvas"])
    uv_smart(sack)
    top = ellipsoid("V3_Pack_Top", (0.0, 0.37, 1.84), (0.22, 0.14, 0.13), m["leather"])
    uv_smart(top)
    roll = cyl("V3_Pack_Roll", (0.0, 0.42, 1.78), 0.075, 0.50, m["canvas"], "X", 18)
    uv_smart(roll)
    for s in (-1, 1):
        pot = cyl("V3_Pack_Pot_%s" % ("L" if s < 0 else "R"), (0.30 * s, 0.36, 1.30), 0.10, 0.18, m["steel"], "Z", 18)
        uv_smart(pot)
        strap = box("V3_Pack_Strap_%s" % ("L" if s < 0 else "R"), (0.18 * s, 0.20, 1.62), (0.075, 0.30, 0.62), m["leather"], 0.012, 2,
                    rot=(math.radians(6), 0, 0))
        uv_smart(strap)
        buckle = box("V3_Pack_Buckle_%s" % ("L" if s < 0 else "R"), (0.18 * s, 0.04, 1.48), (0.075, 0.02, 0.075), m["brass"], 0.008, 2)
        uv_smart(buckle)

    # Peto de cuero sobre el pecho y correa.
    chest = box("V3_ChestPlate", (0.0, -0.235, 1.60), (0.30, 0.035, 0.34), m["leather"], 0.02, 3)
    uv_smart(chest)
    box("V3_ChestStrap", (0.0, -0.24, 1.46), (0.58, 0.045, 0.075), m["leather"], 0.01, 2)
    box("V3_ChestBuckle", (0.0, -0.235, 1.48), (0.075, 0.018, 0.075), m["steel"], 0.008, 2)
    for s in (-1, 1):
        box("V3_Pouch_%s" % ("L" if s < 0 else "R"), (0.36 * s, -0.14, 1.16), (0.16, 0.12, 0.20), m["leather"], 0.02, 3)
        box("V3_PouchFlap_%s" % ("L" if s < 0 else "R"), (0.36 * s, -0.205, 1.21), (0.15, 0.02, 0.10), m["dark"], 0.008, 2)

    # Balaclava oscura que cubre el cráneo y deja la cara a la máscara.
    balaclava = loft("V3_Balaclava", [
        (2.02, 0.0, -0.06, 0.20, 0.20, 100),
        (2.10, 0.0, -0.07, 0.205, 0.205, 100),
        (2.18, 0.0, -0.08, 0.185, 0.185, 100),
        (2.24, 0.0, -0.09, 0.135, 0.135, 100),
        (2.28, 0.0, -0.10, 0.045, 0.045, 100),
    ], m["dark"], thickness=0.018, uv_scale=1.6)
    uv_smart(balaclava)
    # Solapas y cierres del abrigo.
    for s in (-1, 1):
        lap = box("V3_Lapel_%s" % ("L" if s < 0 else "R"), (0.105 * s, -0.345, 1.52),
                  (0.075, 0.045, 0.70), m["leather"], 0.012, 2,
                  rot=(0, 0, math.radians(4 * s)))
        uv_smart(lap)
    for i, z in enumerate((1.30, 1.48, 1.66)):
        clasp = box("V3_Clasp_%d" % i, (0.0, -0.375, z), (0.070, 0.022, 0.034), m["steel"], 0.006, 2)
        uv_smart(clasp)

    # Cinturón nuevo sobre el abrigo.
    belt = loft("V3_Belt", [
        (1.06, 0.0, -0.02, 0.44, 0.32, 0),
        (1.14, 0.0, -0.02, 0.44, 0.32, 0),
    ], m["leather"], closed=True, thickness=0.015, uv_scale=2.0)
    uv_smart(belt)
    box("V3_BeltBuckle", (0.0, -0.34, 1.10), (0.085, 0.022, 0.075), m["steel"], 0.008, 2)



def setup_render():
    scene = bpy.context.scene
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.filepath = RENDER
    scene.render.film_transparent = False
    try:
        scene.view_settings.view_transform = "AgX"
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass
    scene.view_settings.exposure = 1.0
    world = scene.world or bpy.data.worlds.new("V3_World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.015, 0.017, 0.018, 1)
        bg.inputs[1].default_value = 0.35
    cam = bpy.data.objects.get("ReviewCam")
    if cam is None:
        cam_data = bpy.data.cameras.new("ReviewCam")
        cam = bpy.data.objects.new("ReviewCam", cam_data)
        bpy.context.scene.collection.objects.link(cam)
        scene.camera = cam
    cam.data.lens = 58
    cam.location = (3.9, -6.9, 1.60)
    target = Vector((0.0, 0.0, 1.05))
    direction = target - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    for ob in list(bpy.data.objects):
        if ob.type == "LIGHT" and ob.name in {"Key", "Fill", "Rim"}:
            ob.hide_render = True
    # Luces de revisión dedicadas.
    for name, loc, energy, color, size in (
        ("V3_Key", (3.4, -4.8, 3.4), 380, (1.0, 0.86, 0.68), 4.0),
        ("V3_Fill", (-3.8, -3.2, 2.4), 120, (0.62, 0.76, 1.0), 5.0),
        ("V3_Rim", (-1.8, 3.6, 3.2), 300, (0.72, 0.84, 1.0), 3.0),
    ):
        ld = bpy.data.lights.new(name, "AREA")
        ld.energy = energy
        ld.color = color
        ld.size = size
        lo = bpy.data.objects.new(name, ld)
        bpy.context.scene.collection.objects.link(lo)
        lo.location = loc
        lo.rotation_euler = (Vector((0, 0, 1.2)) - lo.location).to_track_quat("-Z", "Y").to_euler()


def main():
    hide_old()
    m = make_materials()
    # El cuerpo y el undersuit heredados de v1 conservan materiales claros:
    # se sustituyen por piel oscura y tela, para que el pecho no parezca desnudo.
    for name, key in (("Collector_Body", "skin"), ("Collector_Undersuit", "canvas")):
        ob = bpy.data.objects.get(name)
        if ob and ob.type == "MESH":
            ob.data.materials.clear()
            ob.data.materials.append(m[key])
    # El cuerpo de v1 queda bajo la ropa: si se renderiza, asoma por el
    # escote y las mangas como piel clara. La silueta la definen abrigo,
    # camisa, capucha y equipo.
    for name in ("Collector_Body", "Collector_Undersuit", "Collector_Nose"):
        ob = bpy.data.objects.get(name)
        if ob:
            ob.hide_render = True
            ob.hide_set(True)
    # La máscara se sube y se acerca al cráneo real (centro y≈−0.65, z≈1.97).
    for ob in bpy.data.objects:
        if ob.type == "MESH" and any(ob.name.startswith(p) for p in (
            "Collector_Mask", "Collector_Goggle", "Collector_Filter",
            "Collector_Respirator", "Collector_Hose",
        )):
            ob.location.y += 0.10
            ob.location.z += 0.14
    # Capucha/mochila se ajustan después de build(m): esos objetos aún no existen.
    build(m)
    for key_ob in bpy.data.objects:
        if key_ob.type == "MESH" and (key_ob.name.startswith("Collector_Key") or key_ob.name == "Collector_KeyRing"):
            key_ob.hide_render = True
            key_ob.hide_set(True)
    # Suavizado de tela: el loft de pocos anillos se lee como cartón sin esto.
    for name in [o.name for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(
            ("V3_Coat", "V3_Hood", "V3_Sleeve", "V3_Pant", "V3_Shirt",
             "V3_ShoulderCape", "V3_Collar", "V3_Balaclava"))]:
        ob = bpy.data.objects.get(name)
        if ob:
            sub = ob.modifiers.new("Smooth", "SUBSURF")
            sub.levels = 2
            sub.render_levels = 2
    # Pliegues de tela: Displace suave sobre el abrigo, capucha, mangas y perneras.
    for name in [o.name for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(
            ("V3_Coat", "V3_Hood", "V3_Sleeve", "V3_Pant", "V3_Shirt"))]:
        ob = bpy.data.objects.get(name)
        if not ob:
            continue
        tex = bpy.data.textures.new("V3_Folds_%s" % name, type="CLOUDS")
        tex.noise_scale = 0.22
        tex.noise_depth = 2
        disp = ob.modifiers.new("Folds", "DISPLACE")
        disp.texture = tex
        disp.texture_coords = "GLOBAL"
        disp.strength = 0.012
        disp.mid_level = 0.5
    # Capucha y balaclava se centran sobre la cabeza, no sobre la espalda.
    for name in ("V3_Hood", "V3_Balaclava"):
        ob = bpy.data.objects.get(name)
        if ob:
            ob.location.y = -0.58
            ob.location.z = 0.02
    hood_top = bpy.data.objects.get("V3_HoodTop")
    if hood_top:
        hood_top.location = (0.0, -0.58, 2.31)
    # La estructura metálica no se ve: el saco y el rollo bastan.
    for name in ("V3_Pack_Frame", "V3_Pack_Top"):
        ob = bpy.data.objects.get(name)
        if ob:
            ob.hide_render = True
            ob.hide_set(True)
    roll = bpy.data.objects.get("V3_Pack_Roll")
    if roll:
        roll.location.z = 1.86
    for ob in bpy.data.objects:
        if ob.type != "MESH":
            continue
        if ob.name.startswith(("V3_Pack_Frame", "V3_Pack_Top")):
            continue
        if ob.name.startswith("V3_") or ob.name in {
            "Collector_Mask",
            "Collector_GoggleRing_-1", "Collector_GoggleRing_1",
            "Collector_GoggleLens_-1", "Collector_GoggleLens_1",
            "Collector_Filter", "Collector_FilterCap", "Collector_Respirator",
            "Collector_RespiratorGrill",
            "Collector_LanternBody", "Collector_LanternCore", "Collector_LanternBar_-1",
            "Collector_LanternBar_0", "Collector_LanternBar_1", "Collector_LanternHook",
        }:
            ob.hide_render = False
            ob.hide_set(False)
    bpy.context.scene.view_settings.exposure = 1.25
    setup_render()
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
    print("COLLECTOR_V3_SAVED", OUT_BLEND)
    bpy.ops.object.select_all(action="DESELECT")
    export = []
    for ob in bpy.data.objects:
        if ob.type == "MESH" and not ob.hide_render and ob.name.startswith(("V3_", "Collector_")):
            ob.select_set(True)
            export.append(ob.name)
    bpy.ops.export_scene.gltf(
        filepath=OUT_GLB,
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
        export_cameras=False,
        export_lights=False,
        export_animations=False,
        export_materials="EXPORT",
    )
    print("COLLECTOR_V3_GLB", OUT_GLB, len(export))
    bpy.ops.render.render(write_still=True)
    print("COLLECTOR_V3_RENDER", RENDER)


if __name__ == "__main__":
    main()
