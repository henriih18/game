"""FRECUENCIA MUERTA - Nivel 1
Sala de extraccion detras del extremo oeste del corredor.

- Convierte el muro ciego con rotulo SALIDA en un vano real de 1,60 x 3,07 m.
- Construye una sala de 6 x 6 m alineada con el corredor.
- Traslada la extraccion desde la puerta de recepcion al centro de la sala.
- Conserva el muro original oculto en una coleccion historica.
- No borra datos ni toca otras colecciones.
"""

import bpy
import glob
import math
import os
from mathutils import Vector

ROOM = "NEXUS_V05_EXTRACTION_ROOM"
HIST = "NEXUS_V05_EXTRACTION_HIST"
PREFIX = "NEXUS_V05_EXTR_"
ASSET_PREFIX = "NEXUS_V05_EXTR_ASSET_"
FLOOR = -5.65
CEIL = -1.72
ASSET_ROOT = "/home/riyo/Documentos/game/assets/Modelos 3D"


def ensure_collection(name, parent):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        parent.children.link(col)
    elif col.name not in parent.children:
        parent.children.link(col)
    return col


def move_to(ob, col):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    col.objects.link(ob)


def mat(name):
    return bpy.data.materials.get(name)


def apply_mat(ob, name):
    material = mat(name)
    if material is None:
        raise RuntimeError("Falta material: " + name)
    ob.data.materials.clear()
    ob.data.materials.append(material)


def box(name, center, size, material=None, rot_z=0.0, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center,
                                    rotation=(0.0, 0.0, rot_z))
    ob = bpy.context.active_object
    ob.name = name
    ob.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        apply_mat(ob, material)
    if bevel > 0.0:
        mod = ob.modifiers.new("BEVEL", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    move_to(ob, ROOM_COL)
    return ob


def cyl(name, center, radius, depth, material=None, rot=(0.0, 0.0, 0.0),
        verts=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius,
                                        depth=depth, location=center,
                                        rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    if material:
        apply_mat(ob, material)
    move_to(ob, ROOM_COL)
    return ob


def text(name, body, center, size, material, facing=(0.0, 0.0, 1.0),
         extrude=0.003, align="CENTER"):
    bpy.ops.object.text_add(location=center)
    ob = bpy.context.active_object
    ob.name = name
    ob.data.body = body
    ob.data.size = size
    ob.data.align_x = align
    ob.data.align_y = "CENTER"
    ob.data.extrude = extrude
    if facing is not None:
        f = Vector(facing).normalized()
        ob.rotation_mode = "QUATERNION"
        ob.rotation_quaternion = f.to_track_quat("Z", "Y")
    apply_mat(ob, material)
    move_to(ob, ROOM_COL)
    return ob


def sign(name, body, center, facing, width, height, size):
    f = Vector(facing).normalized()
    q = f.to_track_quat("Z", "Y")
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    plate = bpy.context.active_object
    plate.name = name + "_PLATE"
    plate.scale = (width, height, 0.045)
    plate.rotation_mode = "QUATERNION"
    plate.rotation_quaternion = q
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_mat(plate, "NEXUS_SignPlate")
    move_to(plate, ROOM_COL)
    txt = text(name + "_TEXT", body, Vector(center) + f * 0.04, size,
               "NEXUS_SignText", facing=facing, extrude=0.002)
    return plate, txt


SOURCES = {}


def asset_path(key):
    pattern = os.path.join(ASSET_ROOT, "*", key + ".blend", key + ".blend")
    paths = glob.glob(pattern)
    if not paths:
        raise RuntimeError("Asset no encontrado: " + key)
    return paths[0]


def load_sources(key):
    if key.lower() in SOURCES:
        return SOURCES[key.lower()]
    with bpy.data.libraries.load(asset_path(key), link=False) as (src, dst):
        dst.collections = list(src.collections)
    loaded = [c for c in dst.collections if c is not None]
    objs = []
    for c in loaded:
        for o in list(c.all_objects):
            if o.name not in ROOM_COL.objects:
                ROOM_COL.objects.link(o)
            objs.append(o)
        bpy.data.collections.remove(c)
    bpy.context.view_layer.update()
    SOURCES[key.lower()] = objs
    return objs


def bbox(objs):
    pts = []
    for o in objs:
        if o.type == "MESH":
            for corner in o.bound_box:
                pts.append(o.matrix_world @ Vector(corner))
    if not pts:
        return None
    return (Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
            Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))))


def place_asset(key, name, x, y, z, rot_z=0.0):
    src = load_sources(key)
    root = bpy.data.objects.new(ASSET_PREFIX + name + "_ROOT", None)
    ROOM_COL.objects.link(root)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.12
    inst = []
    for s in src:
        d = s.copy()
        if s.data is not None:
            d.data = s.data
        ROOM_COL.objects.link(d)
        d.parent = root
        d.matrix_parent_inverse = root.matrix_world.inverted()
        d.matrix_world = s.matrix_world.copy()
        d.name = ASSET_PREFIX + name + "_" + s.name
        inst.append(d)
    bpy.context.view_layer.update()
    bb = bbox(inst)
    if bb is None:
        raise RuntimeError("Asset vacio: " + key)
    mn, mx = bb
    root.location.x -= (mn.x + mx.x) * 0.5
    root.location.y -= (mn.y + mx.y) * 0.5
    root.location.z -= mn.z
    bpy.context.view_layer.update()
    root.rotation_mode = "XYZ"
    root.rotation_euler[2] = rot_z
    root.location = (x, y, z)
    bpy.context.view_layer.update()
    for o in [root] + inst:
        o["asset_source"] = key
        o["asset_license"] = "Poly Haven - verificar licencia antes de distribuir"
        o["placement"] = "V05 sala de extraccion"
    return root


def cleanup_sources():
    for objs in SOURCES.values():
        for o in list(objs):
            if o.name in bpy.data.objects:
                bpy.data.objects.remove(o, do_unlink=True)
    SOURCES.clear()


def make_extract_paint():
    name = "NEXUS_V05_MAT_ExtractPaint"
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (0.82, 0.22, 0.015, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.46
    bsdf.inputs["Emission Color"].default_value = (1.0, 0.30, 0.03, 1.0)
    bsdf.inputs["Emission Strength"].default_value = 0.55
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return m


def make_lamp_paint():
    name = "NEXUS_V05_MAT_ExtractLamp"
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (0.92, 0.88, 0.80, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.35
    bsdf.inputs["Emission Color"].default_value = (1.0, 0.93, 0.80, 1.0)
    bsdf.inputs["Emission Strength"].default_value = 3.0
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return m


def unparent_world(ob):
    mw = ob.matrix_world.copy()
    ob.parent = None
    ob.matrix_world = mw


def place(ob, loc, rot_z=0.0):
    ob.rotation_mode = "XYZ"
    ob.location = loc
    ob.rotation_euler = (0.0, 0.0, rot_z)


def main():
    global ROOM_COL
    l1 = bpy.data.collections.get("NEXUS_L1_V05")
    if l1 is None:
        raise RuntimeError("No existe NEXUS_L1_V05")

    ROOM_COL = ensure_collection(ROOM, l1)
    # Limpiar camaras temporales de revision si quedaron en la sesion.
    for ob in list(bpy.data.objects):
        if ob.name.startswith("TMP_"):
            bpy.data.objects.remove(ob, do_unlink=True)
    hist = ensure_collection(HIST, l1)
    hist.hide_render = True
    hist.hide_viewport = True

    # Limpiar solo objetos generados por este script.
    for ob in list(ROOM_COL.objects):
        if ob.name.startswith(PREFIX):
            bpy.data.objects.remove(ob, do_unlink=True)

    # Muro original -> historico oculto.
    wall = bpy.data.objects.get("NEXUS_V05_CORR_END_-22")
    if wall is not None:
        if "original_hide_render" not in wall:
            wall["original_hide_render"] = bool(wall.hide_render)
            wall["original_hide_viewport"] = bool(wall.hide_viewport)
            wall["original_collections"] = [c.name for c in wall.users_collection]
        wall["structural_change"] = "extraction_room_v135"
        wall["hide_reason"] = "vano de acceso a sala de extraccion"
        move_to(wall, hist)
        wall.hide_render = True
        wall.hide_viewport = True

    # Rotulo SALIDA original: se conserva, reubicado sobre el nuevo vano.
    plate = bpy.data.objects.get("NEXUS_V05_CORR_END_SIGN_-22_PLATE")
    stext = bpy.data.objects.get("NEXUS_V05_CORR_END_SIGN_-22_TEXT")
    if plate is not None:
        if "original_location" not in plate:
            plate["original_location"] = tuple(plate.location)
        plate.location = (-21.825, 0.0, -2.30)
        plate["extraction_room_move"] = "sobre vano oeste"
    if stext is not None:
        if "original_location" not in stext:
            stext["original_location"] = tuple(stext.location)
        stext.location = (-21.785, 0.0, -2.30)
        stext["extraction_room_move"] = "sobre vano oeste"

    make_extract_paint()
    make_lamp_paint()
    floor_mat = "NEXUS_V05_MAT_Floor_Worn"
    wall_mat = "NEXUS_Concrete"
    dark_mat = "NEXUS_Concrete_Dark"
    wain_mat = "NEXUS_Rack_Paint"
    steel = "NEXUS_Steel"
    dark = "NEXUS_Dark_Metal"
    amber = "NEXUS_Amber"
    glow = "NEXUS_V05_MAT_ExtractGlow"

    # Estructura de la sala.
    box(PREFIX + "FLOOR", (-25.0, 0.0, -5.80), (6.0, 6.0, 0.30), floor_mat)
    box(PREFIX + "CEILING", (-25.0, 0.0, -1.60), (6.0, 6.0, 0.24), dark_mat)
    box(PREFIX + "WALL_W", (-28.0, 0.0, -3.64), (0.28, 6.28, 4.32), wall_mat)
    box(PREFIX + "WALL_N", (-25.0, 3.0, -3.64), (6.28, 0.28, 4.32), wall_mat)
    box(PREFIX + "WALL_S", (-25.0, -3.0, -3.64), (6.28, 0.28, 4.32), wall_mat)

    # Muro este segmentado con vano de 1,60 m.
    box(PREFIX + "WALL_E_S", (-22.0, -1.97, -3.64), (0.28, 2.34, 4.32), wall_mat)
    box(PREFIX + "WALL_E_N", (-22.0, 1.97, -3.64), (0.28, 2.34, 4.32), wall_mat)
    box(PREFIX + "WALL_E_TOP", (-22.0, 0.0, -2.03), (0.28, 1.60, 1.10), wall_mat)

    # Marco del vano.
    box(PREFIX + "DOOR_JAMB_S", (-22.0, -0.86, -4.10), (0.34, 0.12, 3.10), steel)
    box(PREFIX + "DOOR_JAMB_N", (-22.0, 0.86, -4.10), (0.34, 0.12, 3.10), steel)
    box(PREFIX + "DOOR_HEAD", (-22.0, 0.0, -2.56), (0.34, 1.84, 0.14), steel)
    box(PREFIX + "DOOR_THRESHOLD", (-22.0, 0.0, -5.64), (0.34, 1.62, 0.025), steel)
    box(PREFIX + "DOOR_TRACK", (-22.31, 1.62, -2.53), (0.10, 1.70, 0.08), dark)

    # Hoja corredera aparcada dentro de la sala.
    box(PREFIX + "DOOR_LEAF", (-22.38, 1.62, -4.12), (0.08, 1.54, 3.02), "NEXUS_Painted_Metal", bevel=0.012)
    box(PREFIX + "DOOR_LEAF_HANDLE", (-22.43, 2.22, -4.23), (0.06, 0.05, 0.52), steel)
    box(PREFIX + "DOOR_LEAF_STRIPE", (-22.43, 1.62, -5.40), (0.06, 1.54, 0.16), amber)

    # Zocalos y remate superior.
    box(PREFIX + "WAIN_N", (-25.0, 2.845, -5.05), (5.70, 0.03, 1.20), wain_mat)
    box(PREFIX + "WAIN_S", (-25.0, -2.845, -5.05), (5.70, 0.03, 1.20), wain_mat)
    box(PREFIX + "WAIN_W", (-27.845, 0.0, -5.05), (0.03, 5.70, 1.20), wain_mat)
    box(PREFIX + "WAIN_E_S", (-22.145, -1.84, -5.05), (0.03, 2.00, 1.20), wain_mat)
    box(PREFIX + "WAIN_E_N", (-22.145, 1.84, -5.05), (0.03, 2.00, 1.20), wain_mat)
    for n, c, s in (
        ("TRIM_N", (-25.0, 2.835, -4.43), (5.74, 0.05, 0.07)),
        ("TRIM_S", (-25.0, -2.835, -4.43), (5.74, 0.05, 0.07)),
        ("TRIM_W", (-27.835, 0.0, -4.43), (0.05, 5.74, 0.07)),
    ):
        box(PREFIX + n, c, s, steel)

    # Compuerta industrial cerrada al oeste.
    box(PREFIX + "SHUTTER_W", (-27.80, 0.0, -3.93), (0.12, 3.34, 3.44), dark)
    for i in range(13):
        z = -5.55 + i * 0.24
        box(PREFIX + "SHUTTER_SLAT_%02d" % i,
            (-27.725, 0.0, z), (0.05, 3.24, 0.19), "NEXUS_Painted_Metal", bevel=0.006)
    box(PREFIX + "SHUTTER_FRAME_L", (-27.72, -1.70, -3.93), (0.10, 0.12, 3.52), steel)
    box(PREFIX + "SHUTTER_FRAME_R", (-27.72, 1.70, -3.93), (0.10, 0.12, 3.52), steel)
    box(PREFIX + "SHUTTER_HEADER", (-27.72, 0.0, -2.12), (0.10, 3.52, 0.18), steel)
    box(PREFIX + "SHUTTER_HAZ_0", (-27.685, -0.92, -5.46), (0.03, 0.38, 0.10), amber)
    box(PREFIX + "SHUTTER_HAZ_1", (-27.685, 0.00, -5.46), (0.03, 0.38, 0.10), amber)
    box(PREFIX + "SHUTTER_HAZ_2", (-27.685, 0.92, -5.46), (0.03, 0.38, 0.10), amber)

    # Delimitacion de la zona completa.
    box(PREFIX + "ZONE_N", (-25.0, 2.45, -5.642), (4.90, 0.09, 0.006), glow)
    box(PREFIX + "ZONE_S", (-25.0, -2.45, -5.642), (4.90, 0.09, 0.006), glow)
    box(PREFIX + "ZONE_W", (-27.45, 0.0, -5.642), (0.09, 4.90, 0.006), glow)
    box(PREFIX + "ZONE_E", (-22.55, 0.0, -5.642), (0.09, 4.90, 0.006), glow)
    text(PREFIX + "ZONE_TEXT", "EXTRACCION", (-26.35, 0.0, -5.638), 0.45,
         "NEXUS_V05_MAT_ExtractPaint", facing=None, extrude=0.004)

    # Carteles.
    sign(PREFIX + "SIGN_MAIN", "EXTRACCION // SALIDA", (-27.665, 0.0, -2.48),
         (1.0, 0.0, 0.0), 3.10, 0.50, 0.35)
    sign(PREFIX + "SIGN_ROOM", "ZONA DE EXTRACCION", (-22.18, 0.0, -2.25),
         (-1.0, 0.0, 0.0), 2.35, 0.36, 0.23)

    # Iluminacion de techo y emergencia.
    for i, x in enumerate((-23.55, -26.45)):
        box(PREFIX + "LIGHT_HOUSING_%d" % i, (x, 0.0, -1.74),
            (1.55, 0.38, 0.10), steel)
        box(PREFIX + "LIGHT_PANEL_%d" % i, (x, 0.0, -1.805),
            (1.34, 0.26, 0.025), "NEXUS_V05_MAT_ExtractLamp")
    box(PREFIX + "EMERGENCY_BOX", (-22.22, 0.0, -2.06), (0.10, 0.38, 0.18), dark)
    box(PREFIX + "EMERGENCY_LENS", (-22.16, 0.0, -2.06), (0.035, 0.18, 0.10),
        "NEXUS_Red")

    # Detalle funcional.
    box(PREFIX + "DRAIN", (-26.75, -2.15, -5.655), (0.82, 0.82, 0.020), dark)
    for i in range(7):
        box(PREFIX + "DRAIN_BAR_%d" % i, (-26.75, -2.50 + i * 0.12, -5.638),
            (0.72, 0.035, 0.012), steel)
    box(PREFIX + "PIPE_N", (-25.3, 2.78, -2.35), (5.20, 0.10, 0.10), dark)
    box(PREFIX + "PIPE_S", (-25.3, -2.78, -2.35), (5.20, 0.10, 0.10), dark)
    box(PREFIX + "UTILITY_BOX", (-23.10, 2.815, -3.55), (0.62, 0.10, 0.72), dark)
    for i in range(3):
        box(PREFIX + "UTILITY_LED_%d" % i, (-23.24 + i * 0.12, 2.755, -3.38),
            (0.045, 0.025, 0.045), "NEXUS_Green")
    box(PREFIX + "CONSOLE_SHELF", (-25.30, 2.66, -4.58), (1.20, 0.32, 0.06), steel)

    # Consola de extraccion: pedestal y baliza.
    box(PREFIX + "CONSOLE_PEDESTAL", (-25.30, 2.72, -5.125),
        (0.18, 0.18, 1.04), dark)
    box(PREFIX + "CONSOLE_BASE", (-25.30, 2.72, FLOOR + 0.018),
        (0.38, 0.30, 0.035), steel)
    cyl(PREFIX + "BEACON_BASE", (-25.30, 2.57, -3.93), 0.07, 0.08, dark, verts=16)
    cyl(PREFIX + "BEACON_LENS", (-25.30, 2.57, -3.84), 0.06, 0.10,
        "NEXUS_V05_MAT_ExtractGlow", verts=16)

    # Conduita vertical del cuadro electrico.
    cyl(PREFIX + "UTILITY_CONDUIT", (-23.10, 2.80, -2.85), 0.025, 2.20, dark,
        verts=10)
    for i, z in enumerate((-1.95, -2.85, -3.75)):
        box(PREFIX + "UTILITY_CLAMP_%d" % i, (-23.10, 2.79, z),
            (0.12, 0.05, 0.06), steel)

    # Ducha de emergencia junto al desague.
    cyl(PREFIX + "SHOWER_PIPE", (-27.63, -2.20, -3.20), 0.032, 2.40, steel,
        verts=12)
    box(PREFIX + "SHOWER_ARM", (-27.29, -2.20, -2.55), (0.72, 0.055, 0.055), steel)
    cyl(PREFIX + "SHOWER_HEAD", (-26.93, -2.20, -2.61), 0.16, 0.05, steel,
        verts=16)
    cyl(PREFIX + "SHOWER_VALVE", (-27.62, -2.20, -3.55), 0.13, 0.04, "NEXUS_Red",
        rot=(0.0, math.pi / 2.0, 0.0), verts=16)

    # Suministros y equipo de salida.
    place_asset("wooden_crate_01_2k", "CRATE_A", -26.35, -2.55, FLOOR + 0.008, 0.18)
    place_asset("wooden_crate_01_2k", "CRATE_B", -25.45, -2.55, FLOOR + 0.008, -0.12)
    place_asset("wooden_crate_01_2k", "CRATE_C", -26.35, -2.55, FLOOR + 0.358, 0.10)
    place_asset("barrel_03_2k", "BARREL", -27.05, 2.25, FLOOR, 0.0)
    place_asset("utility_box_01_2k", "UTILITY_CABINET", -23.30, 2.64, FLOOR, 0.0)
    place_asset("korean_fire_extinguisher_01_2k", "FIRE_EXT", -22.45, 2.62, FLOOR, 0.0)

    # Luces.
    data = bpy.data.lights.new(PREFIX + "LIGHT_KEY", "AREA")
    data.energy = 300.0
    data.shape = "RECTANGLE"
    data.size = 3.0
    data.size_y = 1.6
    data.color = (1.0, 0.86, 0.68)
    key = bpy.data.objects.new(PREFIX + "LIGHT_KEY", data)
    ROOM_COL.objects.link(key)
    key.location = (-24.0, 0.0, -1.88)
    key.rotation_euler = (0.0, 0.0, 0.0)

    data = bpy.data.lights.new(PREFIX + "LIGHT_FILL", "AREA")
    data.energy = 100.0
    data.shape = "RECTANGLE"
    data.size = 2.4
    data.size_y = 1.2
    data.color = (0.86, 0.90, 1.0)
    fill = bpy.data.objects.new(PREFIX + "LIGHT_FILL", data)
    ROOM_COL.objects.link(fill)
    fill.location = (-26.6, 0.0, -1.90)
    fill.rotation_euler = (0.0, 0.0, 0.0)

    data = bpy.data.lights.new(PREFIX + "LIGHT_EMERGENCY", "POINT")
    data.energy = 22.0
    data.color = (1.0, 0.08, 0.03)
    data.shadow_soft_size = 0.18
    data.use_shadow = False
    em = bpy.data.objects.new(PREFIX + "LIGHT_EMERGENCY", data)
    ROOM_COL.objects.link(em)
    em.location = (-22.22, 0.0, -2.05)

    # Mover el grupo de extraccion existente al centro de la sala.
    zone = bpy.data.objects.get("NEXUS_V05_REC_EXTRACT_ZONE")
    if zone is None:
        zone = bpy.data.objects.new("NEXUS_V05_REC_EXTRACT_ZONE", None)
        ROOM_COL.objects.link(zone)
    zone.empty_display_type = "PLAIN_AXES"
    zone.empty_display_size = 0.4
    zone.location = (-25.0, 0.0, FLOOR)
    zone.rotation_euler = (0.0, 0.0, 0.0)
    zone["extraction_zone"] = True
    zone["zone_shape"] = "room_box"
    zone["zone_size_m"] = [5.6, 5.6]
    zone["activation_time_s"] = 10
    zone["required_players"] = 1
    zone["state"] = "standby"
    zone["route_stage"] = "extraction_room_west_end"
    zone["exported_name"] = "extraction_room_west_end"
    zone["anchor"] = "NEXUS_V05_EXTR_CONSOLE"
    zone["layout_note"] = "toda la sala es la zona de extraccion; el terminal esta en el muro norte"
    for old in ("radius_m", "doorway_width_m"):
        if old in zone:
            del zone[old]
    move_to(zone, ROOM_COL)

    names = [
        "NEXUS_V05_REC_EXTRACT_RING",
        "NEXUS_V05_REC_EXTRACT_CONSOLE",
        "NEXUS_V05_REC_EXTRACT_SCREEN",
        "NEXUS_V05_REC_EXTRACT_INDICATOR",
        "NEXUS_V05_REC_EXTRACT_BUTTON",
        "NEXUS_V05_REC_EXTRACT_SIGN_PLATE",
        "NEXUS_V05_REC_EXTRACT_SIGN_TEXT",
        "NEXUS_V05_REC_EXTRACT_LIGHT",
    ]
    parts = {}
    for n in names:
        ob = bpy.data.objects.get(n)
        if ob is None:
            continue
        unparent_world(ob)
        move_to(ob, ROOM_COL)
        parts[n] = ob

    ring = parts.get("NEXUS_V05_REC_EXTRACT_RING")
    if ring is not None:
        ring.hide_render = True
        ring.hide_viewport = True
        ring["hide_reason"] = "la zona completa es la sala; no hay aro individual"

    con = parts.get("NEXUS_V05_REC_EXTRACT_CONSOLE")
    scr = parts.get("NEXUS_V05_REC_EXTRACT_SCREEN")
    ind = parts.get("NEXUS_V05_REC_EXTRACT_INDICATOR")
    but = parts.get("NEXUS_V05_REC_EXTRACT_BUTTON")
    spl = parts.get("NEXUS_V05_REC_EXTRACT_SIGN_PLATE")
    stx = parts.get("NEXUS_V05_REC_EXTRACT_SIGN_TEXT")
    lit = parts.get("NEXUS_V05_REC_EXTRACT_LIGHT")

    if con is not None:
        place(con, (-25.30, 2.790, -4.28), math.pi)
    if scr is not None:
        place(scr, (-25.30, 2.716, -4.24), math.pi)
    if ind is not None:
        place(ind, (-25.08, 2.716, -3.99), math.pi)
    if but is not None:
        place(but, (-25.30, 2.716, -4.47), math.pi)
    if spl is not None:
        spl.rotation_mode = "XYZ"
        spl.location = (-25.30, 2.842, -3.33)
        spl.rotation_euler = (1.571, 0.0, 1.571 + math.pi)
    if stx is not None:
        stx.rotation_mode = "XYZ"
        stx.location = (-25.30, 2.798, -3.33)
        stx.rotation_euler = (1.571, 0.0, 1.571 + math.pi)
    if lit is not None:
        lit.location = (-25.30, 2.57, -3.78)
        lit.data.energy = 12.0
        lit.data.color = (1.0, 0.38, 0.04)
        lit.data.use_shadow = False

    # La consola no debe flotar: pequeña placa de apoyo.
    box(PREFIX + "CONSOLE_BRACKET", (-25.30, 2.855, -3.94), (0.62, 0.045, 0.90), steel)

    # Camara fija de revisión.
    cam_data = bpy.data.cameras.get("NEXUS_V05_CAM_ExtractionRoom")
    if cam_data is None:
        cam_data = bpy.data.cameras.new("NEXUS_V05_CAM_ExtractionRoom")
    cam = bpy.data.objects.get("NEXUS_V05_CAM_ExtractionRoom")
    if cam is None:
        cam = bpy.data.objects.new("NEXUS_V05_CAM_ExtractionRoom", cam_data)
        ROOM_COL.objects.link(cam)
    cam.data = cam_data
    cam.location = (-22.45, -1.85, -3.05)
    direction = Vector((-26.15, 0.75, -4.35)) - cam.location
    cam.rotation_mode = "XYZ"
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam_data.lens = 13.5

    # Metadatos de sala.
    ROOM_COL["room_kind"] = "extraction"
    ROOM_COL["level"] = "L1"
    ROOM_COL["structural_change"] = "extraction_room_v135"
    ROOM_COL["zone_size_m"] = [6.0, 6.0]

    # Liberar los objetos fuente de los assets importados.
    cleanup_sources()

    # Fijar camara de trabajo y guardar en sitio.
    active = bpy.data.objects.get("NEXUS_V05_CAM_Recepcion")
    if active is not None:
        bpy.context.scene.camera = active
    print("EXTR_ROOM_OBJECTS", len([o for o in ROOM_COL.objects if o.name.startswith(PREFIX)]))
    print("EXTR_ROOM_TOTAL", len(ROOM_COL.objects))
    print("SCENE_OBJECTS", len(bpy.context.scene.objects))
    print("SAVE", bpy.data.filepath)
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)


main()
