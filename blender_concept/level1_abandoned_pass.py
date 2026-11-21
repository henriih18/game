"""FRECUENCIA MUERTA - Nivel 1 (V05): abandono, desorden, texturas y HDRI.

Ejecutar sobre FM_NEXUS_V05_level1_v118.blend. No toca otros niveles.
Guarda FM_NEXUS_V05_level1_v124.blend.
"""

import bpy
import math
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
OUT = ROOT + "/FM_NEXUS_V05_level1_v124.blend"
PREFIX = "NEXUS_L1_DIS_"
COLL_NAME = "NEXUS_L1_DISASTER"
FLOOR = -5.65
SCENE = bpy.context.scene


def M(name, fallback="NEXUS_Steel"):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.get(fallback)
    return mat


def ensure_collection():
    for o in list(bpy.data.objects):
        if o.name.startswith(PREFIX):
            bpy.data.objects.remove(o, do_unlink=True)
    coll = bpy.data.collections.get(COLL_NAME)
    if coll is not None:
        bpy.data.collections.remove(coll)
    coll = bpy.data.collections.new(COLL_NAME)
    SCENE.collection.children.link(coll)
    return coll


COLL = ensure_collection()


def finish(obj, name, mat=None, kind="prop"):
    obj.name = name
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    COLL.objects.link(obj)
    if mat is not None:
        obj.data.materials.clear()
        obj.data.materials.append(M(mat))
    obj["l1_disaster"] = True
    obj["dis_kind"] = kind
    return obj


def box(name, center, size, mat, rot=None, kind="prop"):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    o = bpy.context.active_object
    o.dimensions = size
    if rot is not None:
        o.rotation_euler = rot
    return finish(o, name, mat, kind)


def cyl(name, center, radius, depth, mat, rot=None, verts=16, kind="prop"):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=verts, radius=radius, depth=depth, location=center
    )
    o = bpy.context.active_object
    if rot is not None:
        o.rotation_euler = rot
    return finish(o, name, mat, kind)


def puddle(name, x, y, sx, sy, mat, rot=0.0, kind="floor"):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=24, radius=1.0, depth=0.004, location=(x, y, FLOOR + 0.002)
    )
    o = bpy.context.active_object
    o.scale = (sx, sy, 1.0)
    o.rotation_euler = (0.0, 0.0, rot)
    return finish(o, name, mat, kind)


def paper(name, x, y, rot, mat="NEXUS_OffWhite"):
    return box(
        name,
        (x, y, FLOOR + 0.003),
        (0.21, 0.297, 0.004),
        mat,
        rot=(0.0, 0.0, rot),
        kind="floor",
    )


def shard(name, x, y, rot):
    return box(
        name,
        (x, y, FLOOR + 0.002),
        (0.055, 0.022, 0.003),
        "NEXUS_Glass",
        rot=(0.0, 0.0, rot),
        kind="floor",
    )


def debris(name, x, y, sx, sy, sz, rot, mat="NEXUS_Debris"):
    return box(
        name,
        (x, y, FLOOR + sz * 0.5),
        (sx, sy, sz),
        mat,
        rot=(0.0, 0.0, rot),
        kind="floor",
    )


def blood(name, x, y, sx, sy, rot, mat="NEXUS_L1_MAT_Blood"):
    return puddle(name, x, y, sx, sy, mat, rot=rot, kind="blood")


def branch(root):
    yield root
    for child in root.children:
        yield from branch(child)


def duplicate_root(src_name, new_name, loc, rot, settle=True):
    src = bpy.data.objects.get(src_name)
    if src is None:
        print("MISSING ROOT", src_name)
        return None

    def copy_node(node, new_parent, tag):
        dup = node.copy()
        dup.data = node.data
        for c in list(dup.users_collection):
            c.objects.unlink(dup)
        COLL.objects.link(dup)
        dup.name = new_name + tag
        dup.parent = new_parent
        dup.matrix_parent_inverse = node.matrix_parent_inverse.copy()
        dup.matrix_local = node.matrix_local.copy()
        dup["l1_disaster"] = True
        dup["dis_kind"] = "duplicate"
        for child in node.children:
            copy_node(child, dup, tag + "_" + child.name.rsplit("_", 1)[-1])
        return dup

    root = copy_node(src, None, "")
    root.location = loc
    root.rotation_mode = "XYZ"
    root.rotation_euler = rot
    root.scale = (1.0, 1.0, 1.0)
    bpy.context.view_layer.update()
    if settle:
        zs = []
        for o in branch(root):
            if o.type == "MESH":
                zs.extend((o.matrix_world @ __import__("mathutils").Vector(c)).z for c in o.bound_box)
        if zs:
            root.location.z += FLOOR - min(zs)
    bpy.context.view_layer.update()
    return root


def hide_branch(root_name, replacement):
    root = bpy.data.objects.get(root_name)
    if root is None:
        print("MISSING HIDE", root_name)
        return
    for o in branch(root):
        o.hide_render = True
        o.hide_viewport = True
        o["replaced_by"] = replacement


def make_floor_material():
    mat = bpy.data.materials.new("NEXUS_V05_MAT_Floor_Worn")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (900, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (650, 0)
    bsdf.inputs["Metallic"].default_value = 0.0
    texco = nt.nodes.new("ShaderNodeTexCoord")
    texco.location = (-900, 0)
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    sep.location = (-700, 0)
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    comb.location = (-500, 0)
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.location = (-300, 0)
    mapping.inputs["Scale"].default_value = (0.30, 0.30, 1.0)

    base = "//assets/texturas/Hormigon y cemento/worn_concrete_floor_2k.blend/textures/"
    diff = nt.nodes.new("ShaderNodeTexImage")
    diff.location = (-50, 250)
    rough = nt.nodes.new("ShaderNodeTexImage")
    rough.location = (-50, 0)
    normal = nt.nodes.new("ShaderNodeTexImage")
    normal.location = (-50, -250)
    for node, fname, cs in (
        (diff, "worn_concrete_floor_diff_2k.jpg", "sRGB"),
        (rough, "worn_concrete_floor_rough_2k.exr", "Non-Color"),
        (normal, "worn_concrete_floor_nor_gl_2k.exr", "Non-Color"),
    ):
        path = bpy.path.abspath(base + fname)
        img = bpy.data.images.get(fname)
        if img is None:
            img = bpy.data.images.load(path, check_existing=True)
        img.filepath = bpy.path.relpath(path)
        img.colorspace_settings.name = cs
        node.image = img

    hue = nt.nodes.new("ShaderNodeHueSaturation")
    hue.name = "V05_DARKEN"
    hue.location = (400, 250)
    hue.inputs["Fac"].default_value = 1.0
    hue.inputs["Hue"].default_value = 0.5
    hue.inputs["Saturation"].default_value = 0.35
    hue.inputs["Value"].default_value = 0.16
    nm = nt.nodes.new("ShaderNodeNormalMap")
    nm.location = (400, -250)
    nm.inputs["Strength"].default_value = 0.75

    nt.links.new(texco.outputs["Object"], sep.inputs["Vector"])
    nt.links.new(sep.outputs["X"], comb.inputs["X"])
    nt.links.new(sep.outputs["Y"], comb.inputs["Y"])
    nt.links.new(comb.outputs["Vector"], mapping.inputs["Vector"])
    for node in (diff, rough, normal):
        nt.links.new(mapping.outputs["Vector"], node.inputs["Vector"])
    nt.links.new(diff.outputs["Color"], hue.inputs["Color"])
    nt.links.new(hue.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(rough.outputs["Color"], bsdf.inputs["Roughness"])
    nt.links.new(normal.outputs["Color"], nm.inputs["Color"])
    nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def apply_floor_material():
    final = bpy.data.materials.get("NEXUS_V05_MAT_Floor_Worn")
    if final is None:
        test = bpy.data.materials.get("NEXUS_V05_TEST_FLOOR")
        if test is not None:
            test.name = "NEXUS_V05_MAT_Floor_Worn"
            final = test
        else:
            final = make_floor_material()
    for node in final.node_tree.nodes:
        if node.type == "MAPPING":
            node.inputs["Scale"].default_value = (0.30, 0.30, 1.0)
        if node.type == "HUE_SAT" and node.name == "V05_DARKEN":
            node.inputs["Saturation"].default_value = 0.35
            node.inputs["Value"].default_value = 0.16

    floors = [
        "NEXUS_V05_RECEPCION_FLOOR",
        "NEXUS_V05_CORR_FLOOR",
        "NEXUS_V05_SEGURIDAD_FLOOR",
        "NEXUS_V05_CONTROL_ACCESO_FLOOR",
        "NEXUS_V05_VESTUARIOS_FLOOR",
        "NEXUS_V05_ALMACEN_FLOOR",
        "NEXUS_V05_MANTENIMIENTO_FLOOR",
        "NEXUS_V05_SERVICE_CONN_FLOOR",
        "NEXUS_LINK_L1_FLOOR",
    ]
    count = 0
    for name in floors:
        o = bpy.data.objects.get(name)
        if o is None or o.type != "MESH":
            print("MISSING FLOOR", name)
            continue
        if o.data.users > 1:
            o.data = o.data.copy()
        old = o.data.materials[0].name if o.data.materials else ""
        if not o.get("orig_material"):
            o["orig_material"] = old
        if o.data.materials:
            o.data.materials[0] = final
        else:
            o.data.materials.append(final)
        count += 1
    print("FLOORS_APPLIED", count)
    return final


def set_hdri():
    world = bpy.data.worlds.get("World")
    if world is None:
        world = bpy.data.worlds.new("World")
    world.use_nodes = True
    nt = world.node_tree
    out = next((n for n in nt.nodes if n.type == "OUTPUT_WORLD"), None)
    if out is None:
        out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = None
    for link in out.inputs["Surface"].links:
        if link.from_node.type == "BACKGROUND":
            bg = link.from_node
    if bg is None:
        bg = nt.nodes.new("ShaderNodeBackground")
        nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    env = next((n for n in nt.nodes if n.type == "TEX_ENVIRONMENT"), None)
    if env is None:
        env = nt.nodes.new("ShaderNodeTexEnvironment")
        nt.links.new(env.outputs["Color"], bg.inputs["Color"])
    path = ROOT + "/assets/HDRI/Instalaciones industriales y abandonadas/abandoned_workshop_2k.hdr"
    img = bpy.data.images.get("abandoned_workshop_2k.hdr")
    if img is None:
        img = bpy.data.images.load(path, check_existing=True)
    img.filepath = bpy.path.relpath(path)
    env.image = img
    bg.inputs["Strength"].default_value = 0.02
    print("HDRI", img.name, bg.inputs["Strength"].default_value)


def make_l1_materials():
    for name, color, rough in (
        ("NEXUS_L1_MAT_Blood", (0.055, 0.0025, 0.0025), 0.42),
        ("NEXUS_L1_MAT_Blood_Dark", (0.025, 0.0010, 0.0010), 0.28),
    ):
        mat = bpy.data.materials.get(name)
        if mat is None:
            mat = bpy.data.materials.new(name)
            mat.use_nodes = True
            nt = mat.node_tree
            nt.nodes.clear()
            out = nt.nodes.new("ShaderNodeOutputMaterial")
            out.location = (300, 0)
            bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
            bsdf.location = (0, 0)
            bsdf.inputs["Base Color"].default_value = (*color, 1.0)
            bsdf.inputs["Roughness"].default_value = rough
            bsdf.inputs["Metallic"].default_value = 0.0
            nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
        mat["l1_material"] = True

    mirror = bpy.data.materials.get("NEXUS_L1_MAT_Mirror")
    if mirror is None:
        mirror = bpy.data.materials.new("NEXUS_L1_MAT_Mirror")
        mirror.use_nodes = True
        nt = mirror.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        out.location = (300, 0)
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.location = (0, 0)
        bsdf.inputs["Base Color"].default_value = (0.35, 0.40, 0.42, 1.0)
        bsdf.inputs["Metallic"].default_value = 0.9
        bsdf.inputs["Roughness"].default_value = 0.12
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    mirror["l1_material"] = True
    ob = bpy.data.objects.get("NEXUS_V05_REST_MIRROR")
    if ob is not None and ob.type == "MESH":
        if not ob.get("orig_material"):
            ob["orig_material"] = ob.data.materials[0].name if ob.data.materials else ""
        if ob.data.materials:
            ob.data.materials[0] = mirror
        else:
            ob.data.materials.append(mirror)
        ob["modified_by"] = "NEXUS_L1_DIS_mirror"
    print("L1_MATERIALS", [m.name for m in bpy.data.materials if m.get("l1_material")])


def camera(name, loc, target, lens):
    data = bpy.data.cameras.get(name)
    if data is None:
        data = bpy.data.cameras.new(name)
    ob = bpy.data.objects.get(name)
    if ob is None:
        ob = bpy.data.objects.new(name, data)
        SCENE.collection.objects.link(ob)
    else:
        ob.data = data
    ob.location = loc
    ob.rotation_mode = "XYZ"
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    data.lens = lens
    return ob


def build_break_station():
    hide_branch("NEXUS_ASSET_L1_REC_COFFEE_CART_ROOT", "NEXUS_L1_DIS_BREAK_STATION")
    hide_branch("NEXUS_ASSET_L1_OFFICE_LAPTOP_ROOT", "NEXUS_L1_DIS_OFFICE_BINDER")
    hide_branch("NEXUS_ASSET_L1_REST_CLEANER_TIN_ROOT", "NEXUS_L1_DIS_REST_CLEANING")

    desk = duplicate_root(
        "NEXUS_ASSET_L1_OFFICE_DESK_ROOT",
        "NEXUS_L1_DIS_BREAK_COUNTER",
        (-17.25, 8.20, FLOOR),
        (0.0, 0.0, math.radians(90)),
    )
    if desk is None:
        return
    top = FLOOR + 0.788
    box("NEXUS_L1_DIS_BREAK_MACHINE", (-17.25, 8.20, top + 0.275),
        (0.46, 0.40, 0.55), "NEXUS_Dark_Metal")
    box("NEXUS_L1_DIS_BREAK_FACE", (-17.25, 7.99, top + 0.30),
        (0.36, 0.02, 0.26), "NEXUS_Steel")
    box("NEXUS_L1_DIS_BREAK_SCREEN", (-17.25, 7.978, top + 0.38),
        (0.12, 0.01, 0.06), "NEXUS_Screen")
    cyl("NEXUS_L1_DIS_BREAK_SPOUT", (-17.25, 7.94, top + 0.12),
        0.025, 0.13, "NEXUS_Steel", rot=(0.0, 0.0, 0.0))
    box("NEXUS_L1_DIS_BREAK_DRIP", (-17.25, 7.96, top + 0.02),
        (0.30, 0.22, 0.02), "NEXUS_Dark_Metal")
    for i, y in enumerate((8.55, 8.72, 8.89)):
        cyl("NEXUS_L1_DIS_BREAK_CUP_%d" % i, (-17.02, y, top + 0.045),
            0.035, 0.09, "NEXUS_OffWhite")
    box("NEXUS_L1_DIS_BREAK_TRAY", (-17.10, 8.72, top + 0.008),
        (0.28, 0.38, 0.015), "NEXUS_Steel")
    cyl("NEXUS_L1_DIS_BREAK_BIN", (-16.45, 9.45, FLOOR + 0.225),
        0.16, 0.45, "NEXUS_Dark_Metal", verts=20)
    print("BREAK_STATION", desk.name)


def build_office_replacement():
    box("NEXUS_L1_DIS_OFFICE_BINDER", (-5.95, 7.10, FLOOR + 0.788 + 0.02),
        (0.30, 0.24, 0.04), "NEXUS_Clinical", rot=(0.0, 0.0, 0.25))
    box("NEXUS_L1_DIS_OFFICE_PEN_CUP", (-5.55, 6.68, FLOOR + 0.788 + 0.06),
        (0.08, 0.08, 0.12), "NEXUS_Dark_Metal")
    cyl("NEXUS_L1_DIS_REST_SPRAY", (-7.95, 2.15, FLOOR + 0.11),
        0.04, 0.22, "NEXUS_OffWhite", verts=12)
    box("NEXUS_L1_DIS_REST_SPRAY_TRIGGER", (-7.91, 2.15, FLOOR + 0.20),
        (0.09, 0.04, 0.04), "NEXUS_OffWhite")
    cyl("NEXUS_L1_DIS_REST_BUCKET", (-7.55, 2.25, FLOOR + 0.16),
        0.17, 0.32, "NEXUS_Steel", verts=20)
    cyl("NEXUS_L1_DIS_REST_MOP", (-7.38, 2.10, FLOOR + 0.62),
        0.015, 1.20, "NEXUS_Wood", rot=(0.0, 0.10, 0.20), verts=10)
    box("NEXUS_L1_DIS_OFFICE_FLOOR_BINDER", (-6.90, 6.15, FLOOR + 0.025),
        (0.30, 0.24, 0.04), "NEXUS_Clinical", rot=(0.0, 0.0, 0.45))
    for i, (x, y, r) in enumerate((
        (-7.00, 6.45, 0.3), (-6.60, 6.35, -0.7), (-7.40, 6.50, 1.1),
    )):
        box("NEXUS_L1_DIS_OFFICE_PAPER_FLOOR_%d" % i,
            (x, y, FLOOR + 0.004), (0.21, 0.297, 0.004),
            "NEXUS_OffWhite", rot=(0.0, 0.0, r), kind="floor")
    puddle("NEXUS_L1_DIS_OFFICE_BLOOD", -6.90, 6.40, 0.30, 0.20,
           "NEXUS_L1_MAT_Blood_Dark", rot=0.4, kind="blood")
    box("NEXUS_L1_DIS_OFFICE_MONITOR_FLOOR", (-7.45, 6.25, FLOOR + 0.18),
        (0.50, 0.08, 0.35), "NEXUS_Dark_Metal", rot=(0.0, 0.0, 0.6))
    box("NEXUS_L1_DIS_OFFICE_MONITOR_SCREEN", (-7.45, 6.20, FLOOR + 0.20),
        (0.40, 0.01, 0.25), "NEXUS_Screen", rot=(0.0, 0.0, 0.6))
    box("NEXUS_L1_DIS_OFFICE_WALL_HAND", (-4.35, 6.90, -4.20),
        (0.02, 0.16, 0.22), "NEXUS_L1_MAT_Blood_Dark")
    box("NEXUS_L1_DIS_OFFICE_DESK_BLOOD",
        (-6.90, 7.00, FLOOR + 0.788 + 0.007),
        (0.25, 0.18, 0.006), "NEXUS_L1_MAT_Blood_Dark")
    duplicate_root("NEXUS_ASSET_L1_OFFICE_CHAIR_ROOT",
                   "NEXUS_L1_DIS_CHAIR_OFFICE", (-5.20, 5.90, FLOOR),
                   (math.radians(90), 0.0, 0.5))
    cyl("NEXUS_L1_DIS_REST_BIN_TIPPED", (-6.15, 2.65, FLOOR + 0.15),
        0.14, 0.30, "NEXUS_Dark_Metal",
        rot=(math.radians(90), 0.0, 0.5), verts=16)
    for i, (x, y, r) in enumerate((
        (-6.40, 2.85, 0.2), (-6.05, 2.95, -0.5), (-6.25, 3.15, 0.9),
    )):
        box("NEXUS_L1_DIS_REST_TOWEL_%d" % i, (x, y, FLOOR + 0.006),
            (0.13, 0.10, 0.012), "NEXUS_OffWhite",
            rot=(0.0, 0.0, r), kind="floor")
    box("NEXUS_L1_DIS_REST_EXHAUST", (-4.39, 4.10, -3.25),
        (0.04, 0.55, 0.18), "NEXUS_Dark_Metal")
    for i in range(4):
        box("NEXUS_L1_DIS_REST_EXHAUST_SLAT_%d" % i,
            (-4.37, 3.90 + i * 0.13, -3.25),
            (0.02, 0.06, 0.14), "NEXUS_Steel")
    cyl("NEXUS_L1_DIS_REST_EXHAUST_PIPE", (-4.665, 4.10, -3.25),
        0.055, 0.55, "NEXUS_Dark_Metal",
        rot=(0.0, math.radians(90), 0.0), verts=12)


def build_disaster():
    papers = [
        (-13.6, 5.0, 0.3), (-11.4, 4.2, -0.8), (-14.8, 6.2, 1.1), (-9.2, 6.4, 0.5),
        (2.4, 3.4, 0.2), (4.2, 3.0, -0.5), (6.0, 2.6, 1.0), (1.4, 7.6, -0.4), (5.6, 8.2, 0.7),
        (11.2, 3.2, 0.1), (12.6, 4.0, -0.6), (15.2, 3.2, 0.9), (16.0, 5.2, -0.2),
        (-7.0, 5.4, 0.4), (-5.9, 5.1, -0.9), (-6.6, 4.9, 1.2),
        (-7.0, 3.0, 0.3), (-6.2, 3.4, -0.7),
        (-16.6, -4.2, 0.6), (-12.6, -6.2, -0.8), (-10.6, -8.0, 0.2),
        (-4.6, -4.4, 0.1), (-3.2, -4.9, -0.6), (-1.2, -5.6, 0.8),
        (12.4, -4.6, 0.2), (13.4, -5.1, -0.7), (11.8, -3.6, 0.5),
        (-17.2, 1.2, 0.3), (-15.2, -1.2, -0.6), (-8.2, 1.1, 0.8),
        (-3.2, -1.1, 0.4), (3.2, 1.2, -0.9), (9.2, -1.2, 0.7),
        (4.5, -8.5, 0.2), (5.5, -2.5, -0.5),
        (23.5, 1.0, 0.3), (24.0, 8.0, -0.6),
        (-10.5, 4.0, 0.2), (-9.5, 3.6, -0.6), (-11.8, 3.4, 0.9),
        (-7.0, 5.6, 0.4), (-6.6, 5.3, -0.9), (-7.5, 5.4, 1.2),
        (-6.4, 3.0, 0.2), (-6.0, 2.8, -0.7),
        (-18.0, -0.9, 0.3), (-17.0, 0.8, -0.5), (-15.8, -1.0, 0.9),
        (-14.2, 0.7, -0.2), (-12.5, -0.8, 0.6), (-11.2, 0.9, -0.9),
        (0.2, 4.2, 0.3), (1.0, 3.8, -0.5),
        (10.5, 4.0, 0.4), (15.8, 4.6, -0.7),
    ]
    for i, (x, y, r) in enumerate(papers):
        paper("NEXUS_L1_DIS_PAPER_%02d" % i, x, y, r,
              "NEXUS_Clinical" if i % 3 == 0 else "NEXUS_OffWhite")

    bloods = [
        (-12.8, 7.0, 0.55, 0.35, 0.2), (-11.0, 6.5, 0.70, 0.40, 0.3),
        (-9.2, 5.8, 0.60, 0.30, 0.4), (-7.5, 5.0, 0.50, 0.30, 0.5),
        (-5.5, 3.8, 0.70, 0.40, 0.6), (3.0, 4.2, 0.80, 0.30, 0.2),
        (5.5, 3.0, 0.60, 0.30, 0.7), (15.0, 5.5, 0.70, 0.30, 0.2),
        (16.0, 4.0, 0.60, 0.25, 0.6), (-17.0, -7.5, 0.60, 0.40, 0.3),
        (-16.0, -6.0, 0.70, 0.30, 0.4), (-15.0, -4.5, 0.60, 0.30, 0.5),
        (-14.0, -3.0, 0.50, 0.30, 0.6), (-4.0, -8.0, 0.60, 0.30, 0.2),
        (-2.0, -7.0, 0.70, 0.30, 0.3), (0.0, -6.0, 0.60, 0.30, 0.4),
        (2.0, -5.0, 0.50, 0.30, 0.5), (10.0, -3.0, 0.60, 0.30, 0.2),
        (2.5, 1.2, 0.60, 0.30, 0.2), (4.0, 0.8, 0.50, 0.30, 0.7),
        (23.5, 0.8, 0.50, 0.30, 0.3),
        (-10.0, 3.6, 0.40, 0.20, 0.3),
        (2.0, 4.5, 0.50, 0.20, 0.2),
        (12.0, 4.5, 0.50, 0.20, 0.5),
        (-7.30, 5.10, 0.26, 0.18, 0.4),
        (-6.50, 3.10, 0.25, 0.18, 0.6),
        (-18.0, 0.5, 0.80, 0.25, 0.1),
        (-16.0, 0.3, 0.60, 0.20, 0.4),
        (-14.0, 0.6, 0.50, 0.20, 0.7),
    ]
    for i, (x, y, sx, sy, r) in enumerate(bloods):
        blood("NEXUS_L1_DIS_BLOOD_%02d" % i, x, y, sx, sy, r,
              "NEXUS_L1_MAT_Blood_Dark" if i % 4 == 0 else "NEXUS_L1_MAT_Blood")

    waters = [
        (-6.8, 3.2, 0.50, 0.35), (-15.0, -6.0, 0.70, 0.50),
        (-13.0, -4.0, 0.50, 0.30), (-14.0, -1.0, 0.90, 0.40),
        (4.4, -3.0, 0.35, 0.50), (6.2, 1.2, 0.50, 0.30),
    ]
    for i, (x, y, sx, sy) in enumerate(waters):
        puddle("NEXUS_L1_DIS_WATER_%02d" % i, x, y, sx, sy, "NEXUS_Water")
    puddle("NEXUS_L1_DIS_OIL_0", 14.0, -4.0, 0.80, 0.50, "NEXUS_Oil")
    puddle("NEXUS_L1_DIS_OIL_1", 12.0, -3.0, 0.50, 0.30, "NEXUS_Oil")
    puddle("NEXUS_L1_DIS_STORE_SPILL", -3.5, -6.5, 0.80, 0.55, "NEXUS_Meltwater")

    debris_items = [
        (-6.0, -2.5, 0.40, 0.30, 0.08, 0.3), (-5.5, -2.2, 0.25, 0.20, 0.06, 1.0),
        (0.0, 7.5, 0.35, 0.30, 0.08, 0.5), (6.5, 3.5, 0.30, 0.25, 0.06, 0.8),
        (15.8, 6.0, 0.25, 0.20, 0.05, 0.2), (16.2, 5.6, 0.20, 0.15, 0.04, 0.9),
        (-7.8, 4.0, 0.20, 0.15, 0.03, 0.4), (-6.5, 3.6, 0.15, 0.12, 0.03, 1.1),
        (-16.5, -4.0, 0.30, 0.20, 0.05, 0.5), (-16.8, -3.6, 0.20, 0.15, 0.04, 0.9),
        (16.0, -2.5, 0.50, 0.20, 0.08, 0.2), (15.0, -2.2, 0.30, 0.15, 0.05, 0.6),
        (-20.0, 1.3, 0.30, 0.20, 0.05, 0.1), (-5.0, -1.3, 0.25, 0.20, 0.05, 0.7),
        (20.0, 1.3, 0.30, 0.20, 0.05, 0.4), (5.6, -6.0, 0.20, 0.15, 0.04, 0.3),
        (24.0, 8.0, 0.30, 0.20, 0.05, 0.8),
        (-18.2, 1.1, 0.30, 0.20, 0.06, 0.2),
        (-17.2, -1.2, 0.25, 0.20, 0.05, 0.8),
        (-16.0, 1.2, 0.20, 0.15, 0.04, 0.4),
        (-14.8, -1.1, 0.30, 0.20, 0.06, 1.0),
        (-13.2, 1.2, 0.20, 0.15, 0.04, 0.6),
        (-11.8, -1.2, 0.25, 0.20, 0.05, 0.3),
    ]
    for i, (x, y, sx, sy, sz, r) in enumerate(debris_items):
        debris("NEXUS_L1_DIS_DEBRIS_%02d" % i, x, y, sx, sy, sz, r,
               "NEXUS_Concrete_Dark" if i % 3 == 0 else "NEXUS_Debris")

    for i, (x, y) in enumerate([
        (15.8, 6.0), (16.1, 5.7), (15.5, 5.9),
        (-6.2, 3.4), (-6.0, 3.6), (6.2, 1.4), (6.0, 1.2), (10.0, -3.2),
        (-18.4, 0.9), (-17.5, -1.0), (-15.0, 1.1), (-13.0, -1.0),
        (-11.0, 1.0), (-9.0, -1.0),
    ]):
        shard("NEXUS_L1_DIS_GLASS_%02d" % i, x, y, i * 0.7)

    duplicate_root("NEXUS_ASSET_L1_REC_WAIT_CHAIR_0_ROOT",
                   "NEXUS_L1_DIS_CHAIR_REC_A", (-13.0, 4.8, FLOOR),
                   (math.radians(-90), 0.0, 0.6))
    duplicate_root("NEXUS_ASSET_L1_REC_WAIT_CHAIR_0_ROOT",
                   "NEXUS_L1_DIS_CHAIR_REC_B", (-10.8, 4.4, FLOOR),
                   (math.radians(90), 0.0, -0.8))
    duplicate_root("NEXUS_ASSET_L1_SEC_CHAIR_0_ROOT",
                   "NEXUS_L1_DIS_CHAIR_SEC", (5.0, 4.4, FLOOR),
                   (math.radians(90), 0.0, 0.7))
    duplicate_root("NEXUS_ASSET_L1_ACC_CHAIR_0_ROOT",
                   "NEXUS_L1_DIS_CHAIR_ACC", (11.6, 4.4, FLOOR),
                   (math.radians(-90), 0.0, -0.4))
    duplicate_root("NEXUS_ASSET_L1_REC_WAIT_CHAIR_0_ROOT",
                   "NEXUS_L1_DIS_CHAIR_CORR", (-15.5, 1.0, FLOOR),
                   (math.radians(90), 0.0, 0.2))
    duplicate_root("NEXUS_ASSET_L1_STORE_BARREL_0_ROOT",
                   "NEXUS_L1_DIS_BARREL_FALLEN", (-3.5, -6.5, FLOOR),
                   (math.radians(90), 0.0, 0.3))
    duplicate_root("NEXUS_ASSET_L1_MAINT_TOOL_CART_ROOT",
                   "NEXUS_L1_DIS_CART_TIPPED", (15.0, -4.5, FLOOR),
                   (0.0, math.radians(90), 0.2))
    duplicate_root("NEXUS_ASSET_L1_MAINT_TOOL_CART_ROOT",
                   "NEXUS_L1_DIS_CART_CORR", (12.0, 1.15, FLOOR),
                   (0.0, 0.0, 0.25))
    duplicate_root("NEXUS_ASSET_L1_STORE_PALLET_CRATE_ROOT",
                   "NEXUS_L1_DIS_CRATE_SPILLED", (-1.0, -5.5, FLOOR),
                   (math.radians(20), 0.0, 0.5))
    duplicate_root("NEXUS_ASSET_L1_VEST_TRASHBAG_ROOT",
                   "NEXUS_L1_DIS_BAG_REC", (-8.5, 5.5, FLOOR),
                   (0.0, 0.0, 0.4))
    duplicate_root("NEXUS_ASSET_L1_VEST_TRASHBAG_ROOT",
                   "NEXUS_L1_DIS_BAG_CORR", (17.0, -1.2, FLOOR),
                   (0.0, 0.0, -0.5))
    duplicate_root("NEXUS_ASSET_L1_VEST_TRASHBAG_ROOT",
                   "NEXUS_L1_DIS_BAG_VEST", (-10.5, -8.0, FLOOR),
                   (0.0, 0.0, 0.9))
    duplicate_root("NEXUS_ASSET_L1_REST_WET_SIGN_ROOT",
                   "NEXUS_L1_DIS_WET_SIGN_FALLEN", (-13.0, 0.5, FLOOR),
                   (math.radians(90), 0.0, 0.3))

    for i, (x, y, r) in enumerate(((-4.5, -4.5, 0.2), (-4.0, -5.0, -0.6),
                                   (-3.0, -4.8, 0.8), (-5.0, -5.5, -0.3))):
        cyl("NEXUS_L1_DIS_CAN_%02d" % i, (x, y, FLOOR + 0.035),
            0.035, 0.12, "NEXUS_Rusted_Metal",
            rot=(math.radians(90), 0.0, r), verts=10)

    for i, (x, y, r) in enumerate(((-16.5, -4.0, 0.5), (-12.5, -6.0, -0.7))):
        box("NEXUS_L1_DIS_CLOTH_%02d" % i, (x, y, FLOOR + 0.04),
            (0.50, 0.40, 0.08), "NEXUS_OffWhite", rot=(0.0, 0.0, r))

    box("NEXUS_L1_DIS_MONITOR_SEC", (0.0, 7.5, FLOOR + 0.18),
        (0.50, 0.08, 0.35), "NEXUS_Dark_Metal", rot=(0.0, 0.0, 0.6))
    box("NEXUS_L1_DIS_MONITOR_SEC_SCREEN", (0.0, 7.45, FLOOR + 0.20),
        (0.40, 0.01, 0.25), "NEXUS_Screen", rot=(0.0, 0.0, 0.6))
    box("NEXUS_L1_DIS_MONITOR_ACC", (16.0, 3.0, FLOOR + 0.18),
        (0.50, 0.08, 0.35), "NEXUS_Dark_Metal", rot=(0.0, 0.0, -0.4))
    box("NEXUS_L1_DIS_MONITOR_ACC_SCREEN", (16.0, 2.95, FLOOR + 0.20),
        (0.40, 0.01, 0.25), "NEXUS_Screen", rot=(0.0, 0.0, -0.4))
    box("NEXUS_L1_DIS_MONITOR_REC", (-11.95, 3.7, FLOOR + 0.04),
        (0.50, 0.08, 0.35), "NEXUS_Dark_Metal",
        rot=(math.radians(90), 0.0, 0.35))
    box("NEXUS_L1_DIS_MONITOR_REC_SCREEN", (-11.95, 3.7, FLOOR + 0.086),
        (0.40, 0.01, 0.25), "NEXUS_Screen",
        rot=(math.radians(90), 0.0, 0.35))
    cyl("NEXUS_L1_DIS_BIN_REC", (-9.1, 4.0, FLOOR + 0.18),
        0.16, 0.36, "NEXUS_Dark_Metal",
        rot=(math.radians(90), 0.0, 0.2), verts=16)

    for i, (x, y, r) in enumerate(((6.8, 8.5, math.radians(90)),)):
        cyl("NEXUS_L1_DIS_BIN_SEC", (x, y, FLOOR + 0.18),
            0.18, 0.36, "NEXUS_Dark_Metal", rot=(r, 0.0, 0.0), verts=16)

    for i, (x, y, z, sx, sy, sz, ry) in enumerate((
        (-11.5, 7.39, FLOOR + 0.75, 0.12, 0.02, 0.18, 0.0),
        (3.0, 5.52, FLOOR + 0.75, 0.12, 0.02, 0.18, 0.0),
        (-6.2, 6.62, FLOOR + 0.70, 0.14, 0.02, 0.20, 0.0),
    )):
        box("NEXUS_L1_DIS_HAND_%02d" % i, (x, y, z),
            (sx, sy, sz), "NEXUS_L1_MAT_Blood_Dark")

    cyl("NEXUS_L1_DIS_CORR_CABLE", (5.5, 1.4, -2.15),
        0.02, 0.9, "NEXUS_Dark_Metal", verts=8)
    cyl("NEXUS_L1_DIS_CORR_CABLE_W", (-16.0, 1.4, -2.15),
        0.02, 0.9, "NEXUS_Dark_Metal", verts=8)
    box("NEXUS_L1_DIS_CORR_PANEL", (6.2, 1.50, FLOOR + 0.60),
        (0.80, 0.06, 1.20), "NEXUS_Concrete_Dark",
        rot=(math.radians(-12), 0.0, 0.0))
    box("NEXUS_L1_DIS_CORR_PANEL_W", (-17.5, 1.35, FLOOR + 0.60),
        (0.80, 0.06, 1.20), "NEXUS_Concrete_Dark",
        rot=(math.radians(-12), 0.0, 0.0))
    cyl("NEXUS_L1_DIS_MAINT_PIPE", (16.0, -2.5, FLOOR + 0.05),
        0.04, 1.20, "NEXUS_Steel", rot=(0.0, math.radians(90), 0.0), verts=10)
    print("DISASTER_OBJECTS", len(COLL.objects))


def main():
    apply_floor_material()
    set_hdri()
    make_l1_materials()
    build_break_station()
    build_office_replacement()
    build_disaster()
    camera("NEXUS_V05_CAM_Rest", (-7.95, 3.05, -3.85),
           (-5.2, 3.8, -4.5), 16)
    for o in list(bpy.data.objects):
        if o.name.startswith("TMP_"):
            bpy.data.objects.remove(o, do_unlink=True)
    cam = bpy.data.objects.get("NEXUS_V05_CAM_Corridor")
    if cam is not None:
        SCENE.camera = cam
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=OUT)
    print("SAVED", OUT)
    print("OBJECTS", len(bpy.data.objects))
    print("COLL", len(COLL.objects))


main()
