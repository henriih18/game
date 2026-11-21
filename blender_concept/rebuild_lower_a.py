"""Stage A: hide broken lower-level circulation and relocate the existing room shells.

The rooms are unparented object groups sharing a name prefix. Each group is moved
(and optionally rotated 90 degrees) as a unit around its floor centre.
"""
import bpy
import math
import os
from mathutils import Matrix, Vector

ROOT = "/home/riyo/Documentos/game"
OUT = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V05_level1_v22.blend")

# Rooms that need to be rotated 90 degrees so their doors face the new ring.
ROOMS = {
    # Level 3, floor z = -22.8
    "ENFERMERIA":             {"target": (-7.0, 12.5),  "rot": 0},
    "HABITACIONES_MEDICAS":   {"target": (15.5, -5.5),  "rot": 0},
    "QUIROFANO":              {"target": (1.0, 14.0),   "rot": 90},
    "MORGUE":                 {"target": (15.0, 5.5),   "rot": 0},
    "CAMARAS_FRIGORIFICAS":   {"target": (-15.0, 0.0),  "rot": 0},
    "AISLAMIENTO_A":          {"target": (-7.0, -12.5), "rot": 0},
    "AISLAMIENTO_B":          {"target": (1.0, -12.5),  "rot": 0},
    # Level 4, floor z = -32.8
    "ARMERIA_HERRAMIENTAS":   {"target": (-7.0, 12.5),  "rot": 0},
    "BUNKER_SEGURIDAD":       {"target": (1.5, 13.0),   "rot": 0},
    "CONTENCION_PRIMARIA":    {"target": (0.0, -14.0),  "rot": 0},
    "CONTENCION_SECUNDARIA":  {"target": (16.0, -6.0),  "rot": 0},
    "CONTROL_CONTENCION":     {"target": (-15.5, 0.0),  "rot": 0},
    "LAB_RESTRINGIDO":        {"target": (15.5, 5.5),   "rot": 0},
    # Level 5, floor z = -43.8
    "ARCHIVO_SECRETO":        {"target": (16.5, -5.0),  "rot": 0},
    "BOMBEO_INUNDACION":      {"target": (18.0, 5.5),   "rot": 0},
    "EXTRACCION_PROFUNDA":    {"target": (-7.5, -13.0), "rot": 0},
    "GENERADORES":            {"target": (-7.5, 13.5),  "rot": 0},
    "REFRIGERACION":          {"target": (2.0, 13.5),   "rot": 90},
    "TUNEL_PROFUNDO":         {"target": (4.5, -12.5),  "rot": 0},
}

HIDE_PREFIXES = (
    "CORRIDOR_L-3_",
    "CORRIDOR_L-4_",
    "CORRIDOR_L-5_",
    "STAIR_N2_N3_",
    "STAIR_N3_N4_",
    "LADDER_N4_N5_",
    "ELEVATOR_",
    "SHAFT_CATWALK_",
    "VERTICAL_SHAFT_",
)


def hide_broken_circulation():
    hidden = 0
    for o in bpy.data.objects:
        if o.name.startswith(HIDE_PREFIXES):
            o.hide_render = True
            try:
                o.hide_set(True)
            except Exception:
                pass
            hidden += 1
    return hidden


def room_objects(prefix):
    return [o for o in bpy.data.objects if o.name == prefix or o.name.startswith(prefix + "_")]


def move_room(prefix, target, angle_deg):
    objs = room_objects(prefix)
    floor = bpy.data.objects.get(prefix + "_FLOOR")
    if not objs or floor is None:
        print("MISSING", prefix, len(objs), bool(floor))
        return None
    c = floor.location.copy()
    target = Vector((target[0], target[1], c.z))
    if abs(angle_deg) > 0.01:
        R = Matrix.Rotation(math.radians(angle_deg), 4, "Z")
    else:
        R = Matrix.Identity(4)
    T = Matrix.Translation(target) @ R @ Matrix.Translation(-c)
    for o in objs:
        o.matrix_world = T @ o.matrix_world
    return floor.location.copy()


def main():
    hidden = hide_broken_circulation()
    moved = {}
    for prefix, spec in ROOMS.items():
        loc = move_room(prefix, spec["target"], spec["rot"])
        moved[prefix] = tuple(round(v, 2) for v in loc) if loc else None
    # Save a new incremental file.
    bpy.ops.wm.save_as_mainfile(filepath=OUT)
    print("LOWER_STAGE_A_SAVED", OUT, os.path.getsize(OUT))
    print("HIDDEN_BROKEN", hidden)
    for k, v in moved.items():
        print("MOVED", k, v)


if __name__ == "__main__":
    main()
