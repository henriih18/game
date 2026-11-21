"""Aplica las reglas de extracción para 8 jugadores a la recepción (v138).

No modifica geometría: actualiza metadatos de la zona, de la secuencia,
del trigger de recepción y de los cinco objetos recuperables.

Base y salida: nexus/nivel_01/NEXUS_L1_V05.blend (guardado en sitio).
"""
import bpy
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
OUT = ROOT + "/nexus/nivel_01/NEXUS_L1_V05.blend"
PLAY = bpy.data.collections.get("NEXUS_V05_REC_PLAY")
ZONE_NAME = "NEXUS_V05_REC_EXTRACT_ZONE"
CAB_NAME = "NEXUS_V05_REC_EXTRACT_CAB_TRIGGER"
ROOM_NAME = "NEXUS_V05_REC_EXTRACT_RECEPTION_TRIGGER"
SEQ_NAME = "NEXUS_V05_ELEVATOR_SEQUENCE"

LOOT = {
    "NEXUS_V05_REC_LOOT_CASE_0": {
        "rarity": "uncommon", "size_class": "medium", "volume_approx_l": 67.4,
        "condition": "intact", "effects": "heavy_metal_noise",
        "disassemblable": False, "components": "", "reward_once": True,
    },
    "NEXUS_V05_REC_LOOT_SAMPLE_0": {
        "rarity": "rare", "size_class": "medium", "volume_approx_l": 66.1,
        "condition": "intact_fragile", "effects": "biohazard_risk",
        "disassemblable": False, "components": "", "reward_once": True,
    },
    "NEXUS_V05_REC_LOOT_CRATE_0": {
        "rarity": "rare", "size_class": "large", "volume_approx_l": 443.0,
        "condition": "intact", "effects": "high_noise;requires_two_players",
        "disassemblable": False, "components": "", "reward_once": True,
    },
    "NEXUS_V05_REC_LOOT_DOCS_0": {
        "rarity": "common", "size_class": "small", "volume_approx_l": 7.8,
        "condition": "intact", "effects": "paper_noise",
        "disassemblable": False, "components": "", "reward_once": True,
    },
    "NEXUS_V05_REC_LOOT_DRIVE_0": {
        "rarity": "exceptional", "size_class": "small", "volume_approx_l": 1.7,
        "condition": "intact", "effects": "data_value",
        "disassemblable": False, "components": "", "reward_once": True,
    },
}


def remove_prop(obj, key):
    if key in obj:
        del obj[key]


def parent_keep(child, parent):
    bpy.context.view_layer.update()
    mw = child.matrix_world.copy()
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()
    child.matrix_world = mw
    bpy.context.view_layer.update()


def get_room_trigger(zone):
    ob = bpy.data.objects.get(ROOM_NAME)
    if ob is None:
        ob = bpy.data.objects.new(ROOM_NAME, None)
        ob.empty_display_type = "CUBE"
        ob.empty_display_size = 0.5
        (PLAY or zone.users_collection[0]).objects.link(ob)
        ob.location = (-12.0, 6.7, -5.65)
    if ob.parent is None:
        parent_keep(ob, zone)
    return ob


zone = bpy.data.objects.get(ZONE_NAME)
if zone is None:
    raise RuntimeError("No existe " + ZONE_NAME)
cab = bpy.data.objects.get(CAB_NAME)
seq = bpy.data.objects.get(SEQ_NAME)
if not seq:
    raise RuntimeError("No existe " + SEQ_NAME)

# 1. La zona de extracción es la recepción completa (16 x 10 m).
zone["zone_shape"] = "reception_room"
zone["zone_size_m"] = [16.0, 10.0]
zone["zone_center"] = [-12.0, 6.7]
zone["zone_bounds_x"] = [-20.0, -4.0]
zone["zone_bounds_y"] = [1.7, 11.7]
zone["zone_bounds_z"] = [-5.65, -1.72]
zone["max_players"] = 8
zone["min_players"] = 1
zone["capacity_players"] = 8
zone["required_players"] = 1
zone["activation_condition"] = "all_connected_alive_players_inside_reception"
zone["completion_condition"] = "players_inside_reception_at_completion"
zone["partial_extraction"] = True
zone["players_outside_result"] = "left_behind_not_extracted"
zone["downed_players_inside"] = "count_as_present"
zone["disconnected_players"] = "ignored"
zone["dead_players"] = "ignored"
zone["activation_time_s"] = 2.0
zone["total_sequence_s"] = 8.7
zone["sequence_duration_s"] = 6.7
zone["door_open_time_s"] = 1.5
zone["door_hold_s"] = 2.5
zone["door_close_time_s"] = 1.0
zone["travel_time_s"] = 1.3
zone["loot_delivery_rule"] = "loot_inside_reception_or_carried_by_extracted_player"
zone["loot_outside_result"] = "not_counted"
zone["duplicate_reward_guard"] = True
zone["object_and_components_exclusive"] = True
zone["components_count_individually"] = True
zone["visual_marker"] = "elevator_lobby_ring"
zone["visual_marker_note"] = "El aro marca la salida; la zona de extracción es la recepción completa."
zone["elevator_role"] = "visual_exit_sequence"
zone["layout_note"] = "Ascensor SALIDA dentro de recepcion, junto al reloj; la extraccion se valida en toda la recepcion."
zone["route_stage"] = "reception_room_exit"
zone["design_status"] = "v138_provisional_playtest"
zone["capacity_note"] = "La recepción de 16 x 10 m aloja hasta 8 jugadores; la cabina es la salida visual, no el volumen de extracción."
zone["metadata_version"] = "v138"
remove_prop(zone, "approach_zone_size_m")

# 2. Trigger lógico de la recepción, separado del lobby del ascensor.
room = get_room_trigger(zone)
room["trigger_role"] = "extraction_zone"
room["zone_shape"] = "reception_room"
room["zone_size_m"] = [16.0, 10.0]
room["max_players"] = 8
room["min_players"] = 1
room["visual_only"] = False
room["exported_name"] = "extraction_reception_room_trigger"
room["metadata_version"] = "v138"
zone["reception_trigger"] = ROOM_NAME

# 3. La cabina sigue siendo el disparador visual; no se exige que quepan 8.
if cab:
    cab["trigger_role"] = "cab_visual_trigger"
    cab["extraction_validation"] = False
    cab["max_players_visual"] = 2
    cab["capacity_note"] = "La cabina es la salida visual; la extracción se valida en la recepción."
    cab["metadata_version"] = "v138"
    zone["cab_trigger"] = CAB_NAME

# 4. Secuencia y reglas de equipo.
seq["extraction_mode"] = "team_reception_room"
seq["max_players"] = 8
seq["min_players"] = 1
remove_prop(seq, "requires_player_inside")
seq["requires_player_inside_reception"] = True
seq["requires_cab_occupancy"] = False
seq["activation_condition"] = zone["activation_condition"]
seq["completion_condition"] = zone["completion_condition"]
seq["partial_extraction"] = True
seq["players_outside_result"] = "left_behind_not_extracted"
seq["loot_delivery_rule"] = zone["loot_delivery_rule"]
seq["duplicate_reward_guard"] = True
seq["design_status"] = "v138_provisional_playtest"
seq["metadata_version"] = "v138"

# 5. Contrato de los cinco recuperables.
for name, data in LOOT.items():
    ob = bpy.data.objects.get(name)
    if ob is None:
        print("LOOT_MISSING", name)
        continue
    ob["delivery_zone"] = "reception_room"
    ob["reward_once"] = data["reward_once"]
    ob["rarity"] = data["rarity"]
    ob["size_class"] = data["size_class"]
    ob["volume_approx_l"] = data["volume_approx_l"]
    ob["condition"] = data["condition"]
    ob["effects"] = data["effects"]
    ob["disassemblable"] = data["disassemblable"]
    ob["components"] = data["components"]
    ob["component_of"] = ""
    ob["metadata_version"] = "v138"
    print("LOOT", name, ob.get("rarity"), ob.get("size_class"), ob.get("volume_approx_l"))

print("ZONE", dict(zone.items()))
print("ROOM_TRIGGER", room.name, tuple(round(v, 2) for v in room.matrix_world.translation))
print("SEQ", dict(seq.items()))
print("OBJECTS", len(bpy.data.objects))
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("SAVED", bpy.data.filepath)
