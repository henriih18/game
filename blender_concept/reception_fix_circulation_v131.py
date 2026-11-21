"""Move the second reception waiting bench out of the entrance aisle.

The bench spans x -12.5..-8.5 at y 2.6..3.4, directly in front of the reception
door (x -12.8..-11.2). The free gap behind it is exactly the 0.76 m player
diameter, so the room is unreachable in practice. The bench is rotated 90 deg
and placed as a continuation of the existing west-wall waiting bench, leaving
the entrance and the extraction zone clear.

Run:
  blender -b nexus/nivel_01/NEXUS_L1_V05.blend --python blender_concept/reception_fix_circulation_v131.py
"""

import math
import os

import bpy
from mathutils import Matrix, Vector

ROOT = "/home/riyo/Documentos/game"
OUT = os.path.join(ROOT, "nexus/nivel_01/NEXUS_L1_V05_recepcion_v131.blend")
PREFIX = "NEXUS_V05_REC_BENCH2"
LEG_PREFIX = "NEXUS_V05_D_REC_BENCH2_LEG_"
OLD_CENTER = Vector((-10.5, 3.0, 0.0))
NEW_CENTER = Vector((-18.9, 9.0, 0.0))
ANGLE = math.radians(90.0)

names = [PREFIX] + [f"{LEG_PREFIX}{a}_{b}" for a in (0, 1) for b in (0, 1)]
objects = []
for name in names:
    ob = bpy.data.objects.get(name)
    if ob is None:
        raise RuntimeError(f"missing object: {name}")
    objects.append(ob)

transform = (
    Matrix.Translation(NEW_CENTER)
    @ Matrix.Rotation(ANGLE, 4, "Z")
    @ Matrix.Translation(-OLD_CENTER)
)
for ob in objects:
    ob.matrix_world = transform @ ob.matrix_world
    ob["circulation_fix"] = "reception_v131_bench_moved_to_west_wall"

bpy.context.view_layer.update()


def bounds(ob):
    corners = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    return (
        min(c.x for c in corners),
        max(c.x for c in corners),
        min(c.y for c in corners),
        max(c.y for c in corners),
        min(c.z for c in corners),
        max(c.z for c in corners),
    )


for ob in objects:
    b = bounds(ob)
    print("BENCH", ob.name, tuple(round(v, 2) for v in b))

# Assert the new footprint is inside the reception open area and away from the
# door opening (x -12.8..-11.2) and the extraction zone (centre -13.9, 2.78).
group_min_x = min(bounds(o)[0] for o in objects)
group_max_x = max(bounds(o)[1] for o in objects)
group_min_y = min(bounds(o)[2] for o in objects)
group_max_y = max(bounds(o)[3] for o in objects)
checks = {
    "inside_west_open_area": group_min_x > -19.82 and group_max_x < -18.0,
    "clear_of_door_span": group_max_x < -12.8,
    "clear_of_extraction": group_max_y > 2.78 + 0.75,
    "legs_on_floor": -5.651 <= min(bounds(o)[4] for o in objects) <= -5.60,
}
print("CHECKS", checks)
if not all(checks.values()):
    raise RuntimeError(f"bench placement checks failed: {checks}")

# Report any AABB overlap with other visible meshes; ignore the moved group.
group = set(objects)
collisions = []
for other in bpy.context.scene.objects:
    if other.type != "MESH" or other.hide_render or other in group:
        continue
    ob = bounds(other)
    for moved in objects:
        mb = bounds(moved)
        dx = min(mb[1], ob[1]) - max(mb[0], ob[0])
        dy = min(mb[3], ob[3]) - max(mb[2], ob[2])
        dz = min(mb[5], ob[5]) - max(mb[4], ob[4])
        if dx > 0.01 and dy > 0.01 and dz > 0.01:
            collisions.append((moved.name, other.name, round(dx * dy * dz, 4)))
print("OVERLAPS", len(collisions))
for row in collisions[:20]:
    print("  ", row)

bpy.context.scene.camera = bpy.data.objects.get("NEXUS_V05_CAM_Recepcion")
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("SAVED", OUT, os.path.getsize(OUT), "OBJECTS", len(bpy.context.scene.objects))
