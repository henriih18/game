"""Construye una cabina de ascensor transitable detrás del ascensor SALIDA de recepción.

Base: nexus/nivel_01/NEXUS_L1_V05.blend (v136, 2.389 objetos).
Salida: el mismo archivo vivo, sin crear checkpoint nuevo.
"""
import bpy
import math
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
OUT = ROOT + "/nexus/nivel_01/NEXUS_L1_V05.blend"
FLOOR = -5.65

L1 = bpy.data.collections.get("NEXUS_L1_V05")
STRUCT = bpy.data.collections.get("V05_STRUCT")
CAMS = bpy.data.collections.get("V05_CAMS")
PLAY = bpy.data.collections.get("NEXUS_V05_REC_PLAY")

ELEV = bpy.data.collections.get("NEXUS_V05_ELEVATOR")
HIST = bpy.data.collections.get("NEXUS_V05_ELEVATOR_HIST")

SOURCES = {
    "NEXUS_V05_RECEPCION_WALL_N": "V05_STRUCT",
    "NEXUS_V05_C_REC_ELEV_FRAME": "V05_STRUCT",
    "NEXUS_V05_REC_WAINSCOT_N": "NEXUS_V05_REC_PASS126",
    "NEXUS_V05_REC_WAINSCOT_TRIM_N": "NEXUS_V05_REC_PASS126",
}
DOORS = ("NEXUS_V05_C_REC_ELEV_L", "NEXUS_V05_C_REC_ELEV_R")
CLOCK = "NEXUS_ASSET_L1_REC_CLOCK_ROOT"
CALL = ("NEXUS_V05_C_REC_ELEV_BTN", "NEXUS_V05_C_REC_ELEV_CALL")
ZONE = "NEXUS_V05_REC_EXTRACT_ZONE"


def ensure_collection(name, parent):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    elif parent and c.name not in [ch.name for ch in parent.children]:
        # Only re-link if it is not already somewhere under the parent.
        if not any(c.name == ch.name for ch in parent.children):
            parent.children.link(c)
    return c


def move_to(obj, coll):
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    coll.objects.link(obj)


def remove_obj(obj):
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)


def box(name, center, size, material, coll, rotation=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = size
    if rotation is not None:
        ob.rotation_euler = rotation
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if material:
        ob.data.materials.clear()
        ob.data.materials.append(material)
    move_to(ob, coll)
    return ob


def cyl_y(name, center, radius, depth, material, coll, verts=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth,
                                        location=center, rotation=(math.pi / 2.0, 0.0, 0.0))
    ob = bpy.context.object
    ob.name = name
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if material:
        ob.data.materials.clear()
        ob.data.materials.append(material)
    move_to(ob, coll)
    return ob


def parent_keep(child, parent):
    # Un objeto recién creado no tiene matrix_world actualizada hasta que la
    # view layer se evalúa; sin esto, el trigger de la cabina se guardaba en (0,0,0).
    bpy.context.view_layer.update()
    mw = child.matrix_world.copy()
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()
    child.matrix_world = mw


def apply_all_modifiers(obj):
    if not obj:
        return
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    for m in list(obj.modifiers):
        try:
            bpy.ops.object.modifier_apply(modifier=m.name)
        except RuntimeError as exc:
            print("MODIFIER_SKIP", obj.name, m.name, exc)


def cut_copy(src, name, cutter, coll):
    dup = src.copy()
    dup.data = src.data.copy()
    dup.name = name
    dup.data.name = name + "_MESH"
    coll.objects.link(dup)
    dup.hide_render = False
    dup.hide_viewport = False
    apply_all_modifiers(dup)
    bpy.ops.object.select_all(action="DESELECT")
    dup.select_set(True)
    bpy.context.view_layer.objects.active = dup
    mod = dup.modifiers.new("ELEV_HOLE", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    mod.object = cutter
    try:
        bpy.ops.object.modifier_apply(modifier=mod.name)
    except RuntimeError as exc:
        print("BOOLEAN_FAILED", name, exc)
    return dup


def make_emission_material(name, color, strength):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (color[0] * 0.35, color[1] * 0.35, color[2] * 0.35, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.28
        bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
    return mat


def cleanup():
    global ELEV, HIST
    # Restaurar originales que estén en la colección histórica.
    for src_name, coll_name in SOURCES.items():
        ob = bpy.data.objects.get(src_name)
        if ob:
            if HIST and HIST in ob.users_collection:
                target = bpy.data.collections.get(coll_name) or STRUCT or L1
                if target:
                    move_to(ob, target)
                ob.hide_render = False
                ob.hide_viewport = False
                ob.hide_set(False)
                for k in ("original_collections", "structural_change", "hide_reason"):
                    if k in ob:
                        del ob[k]
    # Restaurar reloj y llamador.
    ob = bpy.data.objects.get(CLOCK)
    if ob and "elev_orig_location" in ob:
        ob.location = Vector(ob["elev_orig_location"])
        for k in ("elev_orig_location", "relocated_for"):
            if k in ob:
                del ob[k]
    for name in CALL:
        ob = bpy.data.objects.get(name)
        if ob and "elev_orig_location" in ob:
            ob.location = Vector(ob["elev_orig_location"])
            for k in ("elev_orig_location", "relocated_for"):
                if k in ob:
                    del ob[k]
    # Restaurar puertas y quitar animación.
    for name in DOORS:
        ob = bpy.data.objects.get(name)
        if not ob:
            continue
        if "elev_orig_x" in ob:
            ob.location.x = float(ob["elev_orig_x"])
        try:
            ob.animation_data_clear()
        except Exception:
            pass
        for k in ("elev_orig_x", "elev_anim"):
            if k in ob:
                del ob[k]
    # Quitar acciones de puertas de una ejecución anterior.
    for act in list(bpy.data.actions):
        if act.name.startswith("NEXUS_V05_ELEV_DOOR_"):
            bpy.data.actions.remove(act)
    # Quitar objetos generados.
    prefixes = ("NEXUS_V05_ELEV_", "NEXUS_V05_ELEVATOR_")
    for ob in list(bpy.data.objects):
        if ob.name == "NEXUS_V05_REC_EXTRACT_CAB_TRIGGER" or any(ob.name.startswith(p) for p in prefixes):
            remove_obj(ob)
    # Quitar colecciones generadas.
    for coll in (ELEV, HIST):
        if coll:
            try:
                bpy.data.collections.remove(coll)
            except Exception:
                pass
    ELEV = None
    HIST = None
    zone = bpy.data.objects.get(ZONE)
    if zone:
        for k in ("cab_trigger", "elevator_sequence", "approach_zone_size_m"):
            if k in zone:
                del zone[k]
        if "zone_shape" in zone:
            zone["zone_shape"] = "elevator_lobby"


def main():
    global ELEV, HIST
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    cleanup()

    ELEV = ensure_collection("NEXUS_V05_ELEVATOR", L1)
    HIST = ensure_collection("NEXUS_V05_ELEVATOR_HIST", L1)

    # --- 1. Duplicar y cortar muro, marco, zócalo y remate. ---
    wall = bpy.data.objects.get("NEXUS_V05_RECEPCION_WALL_N")
    frame = bpy.data.objects.get("NEXUS_V05_C_REC_ELEV_FRAME")
    wain = bpy.data.objects.get("NEXUS_V05_REC_WAINSCOT_N")
    trim = bpy.data.objects.get("NEXUS_V05_REC_WAINSCOT_TRIM_N")
    if not all((wall, frame, wain, trim)):
        raise RuntimeError("Faltan piezas del ascensor de recepción")

    cut_wall = box("NEXUS_V05_ELEV_CUT_WALL", (-17.50, 11.72, -4.4625),
                   (1.88, 0.76, 2.875), None, ELEV)
    cut_frame = box("NEXUS_V05_ELEV_CUT_FRAME", (-17.50, 11.60, -4.4625),
                    (1.88, 0.34, 2.875), None, ELEV)
    cut_wain = box("NEXUS_V05_ELEV_CUT_WAIN", (-17.50, 11.54, -5.25),
                   (1.88, 0.40, 1.30), None, ELEV)
    cut_trim = box("NEXUS_V05_ELEV_CUT_TRIM", (-17.50, 11.54, -4.66),
                   (1.88, 0.40, 0.12), None, ELEV)

    for src_name, cutter, new_name in (
        ("NEXUS_V05_RECEPCION_WALL_N", cut_wall, "NEXUS_V05_ELEV_SIM_WALL_N"),
        ("NEXUS_V05_C_REC_ELEV_FRAME", cut_frame, "NEXUS_V05_ELEV_SIM_FRAME_CUT"),
        ("NEXUS_V05_REC_WAINSCOT_N", cut_wain, "NEXUS_V05_ELEV_SIM_WAINSCOT_CUT"),
        ("NEXUS_V05_REC_WAINSCOT_TRIM_N", cut_trim, "NEXUS_V05_ELEV_SIM_TRIM_CUT"),
    ):
        src = bpy.data.objects.get(src_name)
        dup = cut_copy(src, new_name, cutter, ELEV)
        dup["source_object"] = src_name
        dup["structural_change"] = "elevator_cabin_v137"
        # Guardar el original en la colección histórica, oculto.
        move_to(src, HIST)
        src.hide_render = True
        src.hide_viewport = True
        src.hide_set(True)
        src["original_collections"] = SOURCES[src_name]
        src["structural_change"] = "elevator_cabin_v137"
        src["hide_reason"] = "hueco y cabina de ascensor"

    for cutter in (cut_wall, cut_frame, cut_wain, cut_trim):
        remove_obj(cutter)

    # Junta vertical estática en los bordes del hueco (cubre 2 cm de holgura).
    steel = bpy.data.materials.get("NEXUS_Steel")
    dark = bpy.data.materials.get("NEXUS_Dark_Metal")
    painted = bpy.data.materials.get("NEXUS_Painted_Metal")
    rubber = bpy.data.materials.get("NEXUS_Rubber")
    mirror = bpy.data.materials.get("NEXUS_V05_MAT_ELEV_MIRROR")
    if mirror is None:
        mirror = bpy.data.materials.new("NEXUS_V05_MAT_ELEV_MIRROR")
    if mirror.node_tree is None:
        mirror.use_nodes = True
    mirror_bsdf = next((n for n in mirror.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if mirror_bsdf:
        mirror_bsdf.inputs["Base Color"].default_value = (0.10, 0.12, 0.13, 1.0)
        mirror_bsdf.inputs["Metallic"].default_value = 0.65
        mirror_bsdf.inputs["Roughness"].default_value = 0.24
    mirror["material_note"] = "smoked mirror, reduced reflection for cabin readability"
    amber = bpy.data.materials.get("NEXUS_Amber")

    for x in (-18.43, -16.57):
        jamb = box("NEXUS_V05_ELEV_JAMB_%s" % ("L" if x < -17.5 else "R"),
                   (x, 11.55, -4.3375), (0.03, 0.10, 2.625), rubber, ELEV)
        jamb["component"] = "door_jamb"

    # Forro interior del hueco del muro.
    box("NEXUS_V05_ELEV_PORTAL_L", (-18.445, 11.68, -4.3375),
        (0.03, 0.30, 2.625), steel, ELEV)["component"] = "portal_liner"
    box("NEXUS_V05_ELEV_PORTAL_R", (-16.555, 11.68, -4.3375),
        (0.03, 0.30, 2.625), steel, ELEV)["component"] = "portal_liner"
    box("NEXUS_V05_ELEV_PORTAL_TOP", (-17.50, 11.68, -3.035),
        (1.88, 0.30, 0.03), steel, ELEV)["component"] = "portal_liner"

    # --- 2. Bolsillos de las hojas correderas. ---
    for side, x0, x1 in (("L", -19.42, -18.44), ("R", -16.56, -15.58)):
        box("NEXUS_V05_ELEV_POCKET_%s" % side,
            ((x0 + x1) / 2.0, 11.47, -4.3375),
            (x1 - x0, 0.04, 2.625), steel, ELEV)["component"] = "door_pocket"
        box("NEXUS_V05_ELEV_POCKET_TRIM_%s" % side,
            (x0 if side == "L" else x1, 11.445, -4.3375),
            (0.04, 0.055, 2.625), dark, ELEV)["component"] = "pocket_trim"

    # --- 3. Puertas: faldón, juntas y animación. ---
    door_l = bpy.data.objects.get("NEXUS_V05_C_REC_ELEV_L")
    door_r = bpy.data.objects.get("NEXUS_V05_C_REC_ELEV_R")
    seam = bpy.data.objects.get("NEXUS_V05_C_REC_ELEV_SEAM")
    if seam:
        seam.hide_render = True
        seam.hide_viewport = True
        seam["hide_reason"] = "sustituida por juntas de las hojas v137"

    for door, tag in ((door_l, "L"), (door_r, "R")):
        if "elev_orig_x" not in door:
            door["elev_orig_x"] = float(door.location.x)
        door.location.x = float(door["elev_orig_x"])
        door.animation_data_clear()
        # Faldón inferior que llega al suelo.
        skirt = box("NEXUS_V05_ELEV_DOOR_SKIRT_%s" % tag,
                    (door.location.x, 11.55, -5.6125),
                    (0.94, 0.08, 0.075), steel, ELEV)
        parent_keep(skirt, door)
        skirt["component"] = "door_skirt"
        # Junta de goma en el borde interior.
        seal_x = -17.485 if tag == "L" else -17.515
        seal = box("NEXUS_V05_ELEV_DOOR_SEAL_%s" % tag,
                   (seal_x, 11.55, -4.30),
                   (0.04, 0.10, 2.55), rubber, ELEV)
        parent_keep(seal, door)
        seal["component"] = "door_seal"

        start_x = float(door["elev_orig_x"])
        end_x = start_x - 0.95 if tag == "L" else start_x + 0.95
        door.animation_data_create()
        door.location.x = start_x
        door.keyframe_insert(data_path="location", index=0, frame=1)
        door.location.x = end_x
        door.keyframe_insert(data_path="location", index=0, frame=45)
        door.keyframe_insert(data_path="location", index=0, frame=105)
        door.location.x = start_x
        door.keyframe_insert(data_path="location", index=0, frame=130)
        if door.animation_data and door.animation_data.action:
            door.animation_data.action.name = "NEXUS_V05_ELEV_DOOR_%s_ACTION" % tag
            door.animation_data.action.use_fake_user = True
        door["elev_anim"] = "elevator_door_%s" % tag.lower()

    # --- 4. Umbral y cabina. ---
    box("NEXUS_V05_ELEV_THRESHOLD", (-17.50, 11.74, -5.659),
        (1.88, 0.16, 0.018), steel, ELEV)["component"] = "threshold"

    box("NEXUS_V05_ELEV_CAB_FLOOR", (-17.50, 12.76, -5.70),
        (2.04, 1.88, 0.10), dark, ELEV)["component"] = "cabin_floor"
    box("NEXUS_V05_ELEV_CAB_CEILING", (-17.50, 12.76, -3.06),
        (2.04, 1.88, 0.08), painted, ELEV)["component"] = "cabin_ceiling"
    box("NEXUS_V05_ELEV_CAB_WALL_L", (-18.48, 12.76, -4.335),
        (0.08, 1.88, 2.55), painted, ELEV)["component"] = "cabin_wall"
    box("NEXUS_V05_ELEV_CAB_WALL_R", (-16.52, 12.76, -4.335),
        (0.08, 1.88, 2.55), painted, ELEV)["component"] = "cabin_wall"
    box("NEXUS_V05_ELEV_CAB_WALL_BACK", (-17.50, 13.68, -4.335),
        (2.04, 0.08, 2.55), painted, ELEV)["component"] = "cabin_wall"

    # Espejo trasero y su marco.
    box("NEXUS_V05_ELEV_CAB_MIRROR", (-17.50, 13.625, -4.35),
        (1.56, 0.012, 1.95), mirror, ELEV)["component"] = "cabin_mirror"
    for name, center, size in (
        ("NEXUS_V05_ELEV_CAB_MIRROR_FRAME_T", (-17.50, 13.615, -3.355), (1.66, 0.03, 0.04)),
        ("NEXUS_V05_ELEV_CAB_MIRROR_FRAME_B", (-17.50, 13.615, -5.345), (1.66, 0.03, 0.04)),
        ("NEXUS_V05_ELEV_CAB_MIRROR_FRAME_L", (-18.31, 13.615, -4.35), (0.04, 0.03, 2.03)),
        ("NEXUS_V05_ELEV_CAB_MIRROR_FRAME_R", (-16.69, 13.615, -4.35), (0.04, 0.03, 2.03)),
    ):
        box(name, center, size, steel, ELEV)["component"] = "mirror_frame"

    # Pasamanos laterales.
    for tag, x in (("L", -18.36), ("R", -16.64)):
        cyl_y("NEXUS_V05_ELEV_CAB_RAIL_%s" % tag, (x, 12.72, -4.32),
              0.028, 1.42, steel, ELEV, 16)["component"] = "handrail"
        for y in (12.06, 13.38):
            box("NEXUS_V05_ELEV_CAB_RAIL_POST_%s_%s" % (tag, int(y * 100)),
                (x, y, -4.32), (0.05, 0.05, 0.16), steel, ELEV)["component"] = "handrail"

    # Placa de suelo y banda de advertencia.
    box("NEXUS_V05_ELEV_CAB_FLOOR_PLATE", (-17.50, 12.72, -5.646),
        (1.84, 1.76, 0.006), steel, ELEV)["component"] = "floor_plate"
    box("NEXUS_V05_ELEV_CAB_FLOOR_STRIP", (-17.50, 11.91, -5.642),
        (1.84, 0.05, 0.004), amber, ELEV)["component"] = "floor_safety_strip"

    # Luz de techo: panel emisivo y area light.
    mat_light = make_emission_material("NEXUS_V05_MAT_Elev_Ceiling", (1.0, 0.86, 0.66), 2.2)
    box("NEXUS_V05_ELEV_CAB_LIGHT_PANEL", (-17.50, 12.70, -3.098),
        (1.30, 0.92, 0.018), mat_light, ELEV)["component"] = "ceiling_light"
    ld = bpy.data.lights.new("NEXUS_V05_ELEV_CAB_LIGHT", type="AREA")
    ld.energy = 45.0
    ld.color = (1.0, 0.88, 0.70)
    ld.shape = "RECTANGLE"
    ld.size = 1.10
    ld.size_y = 0.80
    ld.use_shadow = False
    lo = bpy.data.objects.new("NEXUS_V05_ELEV_CAB_LIGHT", ld)
    ELEV.objects.link(lo)
    lo.location = (-17.50, 12.70, -3.17)
    lo["component"] = "cabin_light"

    # Rejilla de techo y difusor.
    box("NEXUS_V05_ELEV_CAB_VENT", (-17.50, 13.40, -3.105),
        (0.80, 0.38, 0.02), dark, ELEV)["component"] = "ceiling_vent"
    for i in range(5):
        box("NEXUS_V05_ELEV_CAB_VENT_SLAT_%d" % i,
            (-17.82 + i * 0.16, 13.40, -3.092),
            (0.04, 0.30, 0.006), steel, ELEV)["component"] = "vent_slat"

    # Panel interior de botones y pantalla.
    box("NEXUS_V05_ELEV_CAB_PANEL", (-16.57, 12.10, -4.28),
        (0.04, 0.34, 0.62), dark, ELEV)["component"] = "button_panel"
    mat_screen = make_emission_material("NEXUS_V05_MAT_Elev_Screen", (0.15, 0.85, 0.78), 1.4)
    box("NEXUS_V05_ELEV_CAB_PANEL_SCREEN", (-16.545, 12.10, -4.22),
        (0.012, 0.22, 0.16), mat_screen, ELEV)["component"] = "button_screen"
    for i, z in enumerate((-4.43, -4.36, -4.29)):
        box("NEXUS_V05_ELEV_CAB_BUTTON_%d" % i,
            (-16.535, 12.10, z), (0.012, 0.045, 0.025), amber, ELEV)["component"] = "button"

    # --- 5. Reloj y llamador fuera del recorrido de las puertas. ---
    clock = bpy.data.objects.get(CLOCK)
    if clock:
        if "elev_orig_location" not in clock:
            clock["elev_orig_location"] = list(clock.location)
        clock.location = (-16.20, 11.515, -2.85)
        clock["relocated_for"] = "elevator_v137_door_clearance"
    for name in CALL:
        ob = bpy.data.objects.get(name)
        if ob:
            if "elev_orig_location" not in ob:
                ob["elev_orig_location"] = list(ob.location)
            ob.location.y -= 0.05
            ob["relocated_for"] = "elevator_v137_door_clearance"

    # --- 6. Trigger de cabina y secuencia. ---
    zone = bpy.data.objects.get(ZONE)
    seq = bpy.data.objects.new("NEXUS_V05_ELEVATOR_SEQUENCE", None)
    seq.empty_display_type = "CUBE"
    seq.empty_display_size = 0.18
    seq.location = (-17.50, 12.60, -4.30)
    seq.hide_render = True
    ELEV.objects.link(seq)
    seq["door_open_frame"] = 45
    seq["door_hold_until_frame"] = 105
    seq["door_close_frame"] = 130
    seq["extraction_complete_frame"] = 160
    seq["door_open_time_s"] = 1.5
    seq["door_hold_s"] = 2.5
    seq["door_close_time_s"] = 1.0
    seq["animation_clip"] = "elevator_extraction_open_close"
    seq["requires_player_inside"] = True
    seq["exported_name"] = "elevator_extraction_sequence"

    trig = bpy.data.objects.new("NEXUS_V05_REC_EXTRACT_CAB_TRIGGER", None)
    trig.empty_display_type = "PLAIN_AXES"
    trig.empty_display_size = 0.16
    trig.location = (-17.50, 12.55, FLOOR)
    trig.hide_render = True
    (PLAY or ELEV).objects.link(trig)
    trig["extraction_zone"] = True
    trig["zone_shape"] = "elevator_car"
    trig["zone_size_m"] = [1.65, 1.35]
    trig["activation_time_s"] = 10
    trig["required_players"] = 1
    trig["requires_player_inside"] = True
    trig["state"] = "standby"
    trig["parent_controller"] = ZONE
    trig["exported_name"] = "extraction_elevator_car"

    if zone:
        parent_keep(trig, zone)
        zone["cab_trigger"] = trig.name
        zone["elevator_sequence"] = seq.name
        zone["zone_shape"] = "elevator_approach"
        zone["approach_zone_size_m"] = [2.10, 1.50]
        zone["exit_type"] = "elevator"
        zone["route_stage"] = "reception_elevator_exit"
        zone["exported_name"] = "extraction_reception_elevator"

    # --- 7. Cámara y escena. ---
    cam = bpy.data.objects.get("NEXUS_V05_CAM_ExtractionElevator")
    if cam is None:
        cd = bpy.data.cameras.new("NEXUS_V05_CAM_ExtractionElevator")
        cam = bpy.data.objects.new("NEXUS_V05_CAM_ExtractionElevator", cd)
        (CAMS or bpy.context.scene.collection).objects.link(cam)
    cam.data.lens = 15.0
    cam.location = (-17.50, 7.90, -4.22)
    target = Vector((-17.05, 11.45, -4.45))
    cam.rotation_mode = "XYZ"
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam["purpose"] = "review_extraction_elevator"

    scn = bpy.context.scene
    scn.frame_start = 1
    scn.frame_end = 160
    scn.frame_set(1)
    scn.camera = cam

    print("NEW_ELEV", len([o for o in bpy.data.objects if o.name.startswith("NEXUS_V05_ELEV_")]))
    print("CAB", len([o for o in bpy.data.objects if "ELEV_CAB" in o.name]))
    print("DOORS", [o.name for o in bpy.data.objects if o.name in DOORS])
    print("FRAME", scn.frame_start, scn.frame_end, scn.frame_current)
    print("CAM", scn.camera.name)
    bpy.ops.wm.save_as_mainfile(filepath=OUT)
    print("SAVED", OUT)


if __name__ == "__main__":
    main()
