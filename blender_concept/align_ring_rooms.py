"""Align the east-side room doors with the centre of the ring corridor."""
import bpy
import os
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
OUT = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V05_level1_v24.blend")

OFFSETS = {
    # Level 3: move the east rooms away from the south/north corridor corners.
    "HABITACIONES_MEDICAS": (0.0, 1.0),
    "MORGUE": (0.0, -1.0),
    # Level 4: same correction after the 180-degree rotations.
    "CONTENCION_SECUNDARIA": (0.0, 1.5),
    "LAB_RESTRINGIDO": (0.0, -1.0),
    # Level 5: the pumping room door straddled the north-east corner.
    "BOMBEO_INUNDACION": (0.0, -1.0),
}


def room_objects(prefix):
    return [o for o in bpy.data.objects if o.name == prefix or o.name.startswith(prefix + "_")]


def main():
    for prefix, (dx, dy) in OFFSETS.items():
        objs = room_objects(prefix)
        if not objs:
            print("MISSING", prefix)
            continue
        for o in objs:
            o.location.x += dx
            o.location.y += dy
        print("SHIFTED", prefix, dx, dy)
    bpy.ops.wm.save_as_mainfile(filepath=OUT)
    print("RING_ALIGN_SAVED", OUT, os.path.getsize(OUT))
    for prefix in OFFSETS:
        frames = [o for o in bpy.data.objects
                  if o.name.startswith(prefix + "_DOOR_FRAME")
                  and not o.name.endswith("_TOP")
                  and not o.hide_render]
        print(prefix, [(round(o.location.x, 2), round(o.location.y, 2)) for o in frames])


if __name__ == "__main__":
    main()
