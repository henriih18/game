"""FRECUENCIA MUERTA - Nivel 1 recepción - v128: linterna + puertas oficina/aseo.

Ya estaba integrada la recepción v127.
Ruta a ejecutar después: exportar a Godot desde la exportación.

Este pase no mueve la recepción v127; tan solo la complementa con lo que
ya existe como prefabs interactivos en Blender:
- linterna de emergencia (objeto root exportable para Godot),
- puertas de oficina y aseo con pivote, ángulo y tags consistentes con lo
  que ya hizo la recepción.
"""

import bpy
import math
from pathlib import Path


REC_PLAY = "NEXUS_V05_REC_PLAY"
FLASHLIGHT = "NEXUS_V05_REC_FLASHLIGHT"
OFFICE_DOOR_PIVOT = "NEXUS_V05_OFFICE_DOOR_PIVOT"
REST_DOOR_PIVOT = "NEXUS_V05_REST_DOOR_PIVOT"


FLASHLIGHT_PROPS = {
    "interactive": "flashlight",
    "light_type": "flashlight",
    "battery_default": 60.0,
    "battery_current": 60.0,
    "uses_battery": True,
    "noise_on_open": "switch",
    "noise_radius_m": 2.0,
    "exported_name": "flashlight",
}


OFFICE_DOOR_PROPS = {
    "interactive": "door",
    "door_type": "swing",
    "door_state": "closed",
    "open_angle_deg": 85.0,
    "swing_direction": "inward",
    "hinge_side": "west",
    "weight_kg": 45.0,
    "requires_hands": 1,
    "blocks_light": True,
    "exported_name": "door_office",
}


REST_DOOR_PROPS = {
    "interactive": "door",
    "door_type": "swing",
    "door_state": "closed",
    "open_angle_deg": 80.0,
    "swing_direction": "inward",
    "hinge_side": "east",
    "weight_kg": 32.0,
    "requires_hands": 1,
    "blocks_light": True,
    "exported_name": "door_rest",
}


def get_or_make_collection():
    coll = bpy.data.collections.get(REC_PLAY)
    if coll is None:
        coll = bpy.data.collections.new(REC_PLAY)
        bpy.context.scene.collection.children.link(coll)
    return coll


def flashlight_setup(obj):
    obj["interactive"] = FLASHLIGHT_PROPS
    obj["exported_name"] = FLASHLIGHT_PROPS["exported_name"]
    obj["loot"] = False
    obj["portable"] = False
    obj["interactive"] = "flashlight"
    if obj.data is not None and getattr(obj.data, "materials", None):
        for slot in obj.material_slots:
            m = slot.material
            if m is not None:
                slot.material = m


def build_flashlight():
    coll = get_or_make_collection()
    if bpy.data.objects.get(FLASHLIGHT):
        return bpy.data.objects[FLASHLIGHT]
    data = bpy.data.objects.new(FLASHLIGHT, None)
    data.empty_display_type = "PLAIN_AXES"
    data.empty_display_size = 0.05
    data.location = (-10.0, 2.0, -2.0)
    data.rotation_euler = (math.radians(90.0), 0.0, -math.radians(90.0))
    coll.objects.link(data)
    flashlight_setup(data)
    return data


def build_office_door():
    coll = get_or_make_collection()
    if bpy.data.objects.get(OFFICE_DOOR_PIVOT):
        return bpy.data.objects[OFFICE_DOOR_PIVOT]
    obj = bpy.data.objects.new(OFFICE_DOOR_PIVOT, None)
    obj.empty_display_type = "ARROWS"
    obj.empty_display_size = 0.8
    obj.location = (-5.0, 1.9, -2.9)
    obj.rotation_euler = (0.0, 0.0, 0.0)
    coll.objects.link(obj)
    props = {**OFFICE_DOOR_PROPS, "door_state": "closed", "exported_name": "door_office"}
    for k, v in props.items():
        obj[k] = v
    return obj


def build_rest_door():
    coll = get_or_make_collection()
    if bpy.data.objects.get(REST_DOOR_PIVOT):
        return bpy.data.objects[REST_DOOR_PIVOT]
    obj = bpy.data.objects.new(REST_DOOR_PIVOT, None)
    obj.empty_display_type = "ARROWS"
    obj.empty_display_size = 0.8
    obj.location = (-5.8, 7.3, -2.9)
    obj.rotation_euler = (0.0, 0.0, 0.0)
    coll.objects.link(obj)
    props = {**REST_DOOR_PROPS, "door_state": "closed", "exported_name": "door_rest"}
    for k, v in props.items():
        obj[k] = v
    return obj


def main():
    solve = build_flashlight()
    office = build_office_door()
    rest = build_rest_door()
    coll = get_or_make_collection()

    print("flashlight", solve.name if solve else None, dict(solve) if solve else None)
    print("office_door", office.name if office else None, dict(office) if office else None)
    print("rest_door", rest.name if rest else None, dict(rest) if rest else None)

    print("count", len(coll.objects))
    print("missing")
    for o in coll.objects:
        if o.name.lower().startswith("nexus_v05_rec_flashlight") or (
            o.name.lower() not in ("nexus_v05_office_door_pivot", "nexus_v05_rest_door_pivot") and not o.keys()
        ):
            print(o.name)

    for o in coll.objects:
        if "interactive" in o and o["interactive"] not in (
            "flashlight", "door",
        ) and o.name.startswith("NEXUS_V05_REC"):
            print("interactive", o.name, o["interactive"], o.get("exported_name"))
    print("exit_code", 0)


main()
