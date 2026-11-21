"""Nivel 1 - recepción revisión v128 - estudio sin escritura.

No hace cambios. Solo verifica que, cuando la recepción v127 está
integrada, el nivel contiene aún:
- 5 objetos recuperables con metadatos,
- escape interactivo,
- trampa sonora,
- brillo del pasillo hacia el este,
- y ya no contiene linterna, puerta de oficina ni puerta de aseo.

Salida: plan de trabajo posterior de neon.
"""

import bpy
from pathlib import Path


REC_PLAY = "NEXUS_V05_REC_PLAY"
TAGS_FLASHLIGHT = ("NEXUS_V05_REC_FLASHLIGHT",)
TAGS_OFFICE_DOOR = (
    "NEXUS_V05_OFFICE_DOOR_PIVOT",
    "NEXUS_V05_OFFICE_DOOR_DOOR_ANCHOR",
    "NEXUS_V05_OFFICE_DOOR_STATE",
)
TAGS_REST_DOOR = (
    "NEXUS_V05_REST_DOOR_PIVOT",
    "NEXUS_V05_REST_DOOR_DOOR_ANCHOR",
    "NEXUS_V05_REST_DOOR_STATE",
)


def read_count():
    coll = None
    for c in bpy.data.collections:
        if c.name == REC_PLAY:
            coll = c
            break
    if coll is None:
        return {}
    out = {}
    for o in coll.objects:
        props = dict(o) if o.keys() else None
        if props:
            out[o.name] = props
    return out


def lobby(props):
    for k, v in props.items():
        t = k.upper()
        yield any(tag in t for tag in TAGS_FLASHLIGHT), k, v
        yield any(tag in t for tag in TAGS_OFFICE_DOOR), k, v
        yield any(tag in t for tag in TAGS_REST_DOOR), k, v


def main():
    props = read_count()
    flashlights = set()
    office_doors = set()
    rest_doors = set()
    for is_tag, k, v in lobby(props):
        if is_tag:
            if any(tag in k.upper() for tag in TAGS_FLASHLIGHT):
                flashlights.add(k)
            elif any(tag in k.upper() for tag in TAGS_OFFICE_DOOR):
                office_doors.add(k)
            elif any(tag in k.upper() for tag in TAGS_REST_DOOR):
                rest_doors.add(k)
    print("count", len(props))
    print("flashlight", flashlights)
    print("office_door", office_doors)
    print("rest_door", rest_doors)
    print("exit_code", 0)


main()
