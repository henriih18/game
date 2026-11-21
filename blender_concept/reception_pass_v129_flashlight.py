"""Recepción V05: linterna de primera persona, extracción provisional y limpieza.

Base: nexus/nivel_01/NEXUS_L1_V05_recepcion_v128.blend
Salida: nexus/nivel_01/NEXUS_L1_V05_recepcion_v129.blend

No crea lógica de jugador ni exporta a Godot. Añade geometría/luces y metadatos
de diseño que luego podrán consumirse desde Godot.
"""
import bpy
import math
from mathutils import Euler, Matrix, Vector

ROOT = "/home/riyo/Documentos/game"
OUT = ROOT + "/nexus/nivel_01/NEXUS_L1_V05_recepcion_v129.blend"
FLOOR = -5.65
PREFIX_FLASH = "NEXUS_V05_REC_FLASHLIGHT_"
PREFIX_EXTRACT = "NEXUS_V05_REC_EXTRACT_"
PLAY = "NEXUS_V05_REC_PLAY"
TORCH_ASSET = ROOT + "/assets/Modelos 3D/Objetos pequeños y narrativa ambiental/small_plastic_torch_2k.blend/small_plastic_torch_2k.blend"

SCENE = bpy.context.scene


def material(name, base=(0.04, 0.04, 0.045, 1.0), metallic=0.0, roughness=0.6):
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = base
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def emission_material(name, color, strength):
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    for node in list(nodes):
        nodes.remove(node)
    out = nodes.new("ShaderNodeOutputMaterial")
    em = nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1.0)
    em.inputs["Strength"].default_value = strength
    links.new(em.outputs["Emission"], out.inputs["Surface"])
    return mat


def play_collection():
    col = bpy.data.collections.get(PLAY)
    if col is None:
        raise RuntimeError("No existe " + PLAY)
    return col


def link_obj(obj):
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    play_collection().objects.link(obj)


def mesh_obj(name, verts, faces, mat, loc=(0, 0, 0)):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    link_obj(ob)
    if mat:
        me.materials.append(mat)
    return ob


def box(name, center, size, mat, bevel=0.0):
    x, y, z = (s / 2 for s in size)
    verts = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
             (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
             (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    ob = mesh_obj(name, verts, faces, mat, center)
    if bevel > 0:
        mod = ob.modifiers.new("edge_soft", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    return ob


def parent_keep(child, parent):
    bpy.context.view_layer.update()
    world = child.matrix_world.copy()
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()
    child.matrix_world = world


def ring_mesh(name, center, outer, inner, mat, segments=64):
    verts = []
    for r in (outer, inner):
        for i in range(segments):
            a = 2 * math.pi * i / segments
            verts.append((r * math.cos(a), r * math.sin(a), 0.004))
    faces = []
    for i in range(segments):
        j = (i + 1) % segments
        faces.append((i, j, segments + j, segments + i))
    ob = mesh_obj(name, verts, faces, mat, center)
    return ob


def sign(name, body, center, facing, width, height, size, mat_text):
    f = Vector(facing).normalized()
    q = f.to_track_quat("Z", "Y")
    plate = box(name + "_PLATE", center, (width, height, 0.035), material("NEXUS_SignPlate", (0.025, 0.03, 0.028, 1), 0.6, 0.4), 0.003)
    plate.rotation_mode = "QUATERNION"
    plate.rotation_quaternion = q
    curve = bpy.data.curves.new(name + "_TEXT", "FONT")
    curve.body = body
    curve.size = size
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.extrude = 0.0015
    txt = bpy.data.objects.new(name + "_TEXT", curve)
    txt.location = Vector(center) + f * 0.026
    txt.rotation_mode = "QUATERNION"
    txt.rotation_quaternion = q
    link_obj(txt)
    curve.materials.append(mat_text)
    return plate, txt


def clean_previous():
    for ob in list(bpy.data.objects):
        if ob.name.startswith(PREFIX_FLASH) or ob.name.startswith(PREFIX_EXTRACT):
            bpy.data.objects.remove(ob, do_unlink=True)
    for name in ("NEXUS_V05_REC_FLASHLIGHT", "NEXUS_V05_REC_EXTRACT"):
        col = bpy.data.collections.get(name)
        if col and col.users == 0:
            bpy.data.collections.remove(col)


def remove_loose_clock():
    removed = []
    local_clock = [
        o for o in bpy.data.objects
        if o.name.startswith("NEXUS_ASSET_L1_REC_CLOCK")
        and o.library is None
        and o.matrix_world.translation.x < -18.5
    ]
    for ob in local_clock:
        if ob.name in bpy.data.objects:
            removed.append(ob.name)
            bpy.data.objects.remove(ob, do_unlink=True)
    return removed


def import_torch():
    with bpy.data.libraries.load(TORCH_ASSET, link=False) as (src, dst):
        dst.collections = src.collections
    imported_col = next((c for c in bpy.data.collections if c.name.startswith("small_plastic_torch")), None)
    if imported_col is None:
        raise RuntimeError("No se cargó small_plastic_torch")
    imported = [o for o in imported_col.objects if o.type == "MESH"]
    if not imported:
        raise RuntimeError("El asset no tiene malla")
    body = imported[0]
    body.name = "NEXUS_V05_REC_FLASHLIGHT_BODY"
    body.data.name = "NEXUS_V05_REC_FLASHLIGHT_MESH"
    link_obj(body)
    if imported_col.users == 0:
        bpy.data.collections.remove(imported_col)
    return body


def build_flashlight():
    cam = bpy.data.objects["NEXUS_V05_CAM_Recepcion"]
    qcam = cam.matrix_world.to_quaternion()
    eye = cam.matrix_world.translation.copy()
    right = qcam @ Vector((1, 0, 0))
    up = qcam @ Vector((0, 1, 0))
    forward = qcam @ Vector((0, 0, -1))
    hand = eye + right * 0.210 - up * 0.170 + forward * 0.480
    root = bpy.data.objects.new("NEXUS_V05_REC_FLASHLIGHT_RIG", None)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.08
    root.location = hand
    root.rotation_mode = "QUATERNION"
    root.rotation_quaternion = forward.to_track_quat("-Y", "Z")
    root["equipment"] = "flashlight"
    root["equipped"] = True
    root["preview_only"] = True
    root["attach_to"] = "player_camera"
    root["battery_pct"] = 78
    root["battery_drain_pct_per_min"] = 1.2
    root["beam_angle_deg"] = 34
    root["range_m"] = 18
    root["reload_type"] = "replaceable_cells"
    root["exported_name"] = "flashlight_handheld"
    link_obj(root)

    body = import_torch()
    body.parent = root
    body.matrix_parent_inverse = Matrix.Identity(4)
    body.location = (0, 0, 0)
    body.rotation_mode = "QUATERNION"
    body.rotation_quaternion = (1, 0, 0, 0)
    body.scale = (1, 1, 1)
    body["asset_source"] = "assets/Modelos 3D/Objetos pequeños y narrativa ambiental/small_plastic_torch_2k.blend"
    body["asset_license"] = "Poly Haven - verificar licencia antes de distribuir"
    body["equipment"] = "flashlight"
    body["exported_name"] = "flashlight_body"

    lens_world = hand + forward * 0.1124
    light_data = bpy.data.lights.new("NEXUS_V05_REC_FLASHLIGHT_SPOT", "SPOT")
    light_data.energy = 1000.0
    light_data.color = (1.0, 0.93, 0.82)
    light_data.spot_size = math.radians(34)
    light_data.spot_blend = 0.45
    light_data.shadow_soft_size = 0.025
    light_data.use_shadow = True
    light = bpy.data.objects.new("NEXUS_V05_REC_FLASHLIGHT_SPOT", light_data)
    light.parent = root
    light.matrix_parent_inverse = Matrix.Identity(4)
    light.location = (0, -0.118, 0)
    light.rotation_mode = "QUATERNION"
    light.rotation_quaternion = Euler((-math.pi / 2, 0, 0), "XYZ").to_quaternion()
    light["tool_light"] = "flashlight"
    light["battery_source"] = root.name
    light["no_shadow_when_off"] = True
    link_obj(light)

    spill_data = bpy.data.lights.new("NEXUS_V05_REC_FLASHLIGHT_SPILL", "POINT")
    spill_data.energy = 7.0
    spill_data.color = (1.0, 0.88, 0.72)
    spill_data.shadow_soft_size = 0.16
    spill_data.use_shadow = False
    spill = bpy.data.objects.new("NEXUS_V05_REC_FLASHLIGHT_SPILL", spill_data)
    spill.parent = root
    spill.matrix_parent_inverse = Matrix.Identity(4)
    spill.location = (0, -0.20, 0)
    spill["tool_light"] = "flashlight_spill"
    link_obj(spill)

    lens_mat = emission_material("NEXUS_V05_MAT_Flashlight_Lens", (1.0, 0.86, 0.62), 3.2)
    lens = ring_mesh("NEXUS_V05_REC_FLASHLIGHT_LENS", (0, 0, 0), 0.029, 0.024, lens_mat, 40)
    lens.parent = root
    lens.matrix_parent_inverse = Matrix.Identity(4)
    lens.location = (0, -0.116, 0)
    lens.rotation_mode = "QUATERNION"
    lens.rotation_quaternion = Euler((-math.pi / 2, 0, 0), "XYZ").to_quaternion()
    return root, body, light


def build_extraction():
    x = -13.90
    wall_y = 1.945
    glow = emission_material("NEXUS_V05_MAT_ExtractGlow", (1.0, 0.34, 0.045), 2.4)
    screen = emission_material("NEXUS_V05_MAT_ExtractScreen", (0.04, 0.38, 0.31), 1.1)
    dark = material("NEXUS_Dark_Metal", (0.018, 0.022, 0.024, 1.0), 0.75, 0.35)
    sign_text = material("NEXUS_SignText", (0.82, 0.78, 0.58, 1.0), 0.0, 0.5)

    zone = bpy.data.objects.new("NEXUS_V05_REC_EXTRACT_ZONE", None)
    zone.empty_display_type = "CIRCLE"
    zone.empty_display_size = 0.75
    zone.location = (x, 2.78, FLOOR)
    zone["extraction_zone"] = True
    zone["activation_time_s"] = 8
    zone["radius_m"] = 0.75
    zone["required_players"] = 1
    zone["state"] = "standby"
    zone["route_stage"] = "reception_entry_provisional"
    zone["exported_name"] = "extraction_reception_entry"
    link_obj(zone)

    parts = []
    ring = ring_mesh("NEXUS_V05_REC_EXTRACT_RING", (x, 2.78, FLOOR + 0.006), 0.75, 0.705, glow)
    ring["extraction_marker"] = True
    parts.append(ring)

    parts.append(box("NEXUS_V05_REC_EXTRACT_CONSOLE", (x, wall_y, -4.28), (0.48, 0.14, 0.62), dark, 0.009))
    parts.append(box("NEXUS_V05_REC_EXTRACT_SCREEN", (x, wall_y + 0.073, -4.24), (0.34, 0.006, 0.22), screen, 0.002))
    parts.append(box("NEXUS_V05_REC_EXTRACT_INDICATOR", (x + 0.165, wall_y + 0.074, -3.995), (0.055, 0.012, 0.055), glow, 0.002))
    parts.append(box("NEXUS_V05_REC_EXTRACT_BUTTON", (x, wall_y + 0.075, -4.47), (0.09, 0.010, 0.045), glow, 0.002))
    plate, text = sign("NEXUS_V05_REC_EXTRACT_SIGN", "EXTRACCION // SALIDA", (x, wall_y, -3.43), (0, 1, 0), 1.30, 0.30, 0.095, sign_text)
    parts.extend((plate, text))

    light_data = bpy.data.lights.new("NEXUS_V05_REC_EXTRACT_LIGHT", "POINT")
    light_data.energy = 7.0
    light_data.color = (1.0, 0.38, 0.06)
    light_data.shadow_soft_size = 0.12
    light_data.use_shadow = False
    light = bpy.data.objects.new("NEXUS_V05_REC_EXTRACT_LIGHT", light_data)
    light.location = (x, 2.15, -3.95)
    light["extraction_light"] = True
    link_obj(light)
    parts.append(light)
    for part in parts:
        parent_keep(part, zone)
    return zone, ring


def main():
    clean_previous()
    removed_clock = remove_loose_clock()
    root, body, light = build_flashlight()
    zone, ring = build_extraction()
    SCENE.camera = bpy.data.objects["NEXUS_V05_CAM_Recepcion"]
    bpy.context.view_layer.update()
    print("REMOVED_CLOCK", removed_clock)
    print("FLASHLIGHT", root.name, tuple(round(v, 3) for v in root.matrix_world.translation))
    print("EXTRACT", tuple(round(v, 3) for v in zone.matrix_world.translation))
    print("PLAY_OBJECTS", len(play_collection().objects))
    print("SCENE_OBJECTS", len(SCENE.objects))
    bpy.ops.wm.save_as_mainfile(filepath=OUT)
    print("SAVED", OUT, len(SCENE.objects))


if __name__ == "__main__":
    main()
