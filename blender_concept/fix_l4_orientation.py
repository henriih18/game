"""Rotate L4 rooms whose doors currently face away from the new ring corridor."""
import bpy
import math
import os
from mathutils import Matrix, Vector

ROOT = "/home/riyo/Documentos/game"
OUT = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V05_level1_v23.blend")

ROOMS = (
    "ARMERIA_HERRAMIENTAS",
    "BUNKER_SEGURIDAD",
    "CONTENCION_PRIMARIA",
)


def room_objects(prefix):
    return [o for o in bpy.data.objects if o.name == prefix or o.name.startswith(prefix + "_")]


def rotate_room(prefix, angle_deg):
    objs = room_objects(prefix)
    floor = bpy.data.objects.get(prefix + "_FLOOR")
    if not objs or floor is None:
        print("MISSING", prefix, len(objs), bool(floor))
        return
    c = floor.location.copy()
    R = Matrix.Rotation(math.radians(angle_deg), 4, "Z")
    T = Matrix.Translation(c) @ R @ Matrix.Translation(-c)
    for o in objs:
        o.matrix_world = T @ o.matrix_world
    print("ROTATED", prefix, angle_deg, tuple(round(v, 2) for v in floor.location))


def main():
    for prefix in ROOMS:
        rotate_room(prefix, 180)
    bpy.ops.wm.save_as_mainfile(filepath=OUT)
    print("L4_ORIENT_SAVED", OUT, os.path.getsize(OUT))
    for prefix in ROOMS:
        frames = [o for o in bpy.data.objects
                  if o.name.startswith(prefix + "_DOOR_FRAME")
                  and not o.name.endswith("_TOP")
                  and not o.hide_render]
        print(prefix, [(round(o.location.x, 2), round(o.location.y, 2)) for o in frames])


if __name__ == "__main__":
    main()
