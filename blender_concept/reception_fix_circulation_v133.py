"""Reception v133: clear the door-to-counter aisle without deleting furniture.

Base: NEXUS_L1_V05_recepcion_v132.blend (bench duplicate hidden).
Moves the coffee table west off the door axis and the fallen east chair further
east. Everything else stays in place; origins and metadata are preserved.
"""

import bpy
from mathutils import Vector

OUT = "/home/riyo/Documentos/game/nexus/nivel_01/NEXUS_L1_V05_recepcion_v133.blend"
FIX = "reception_v133_clear_aisle"


def move_object(name, delta):
    ob = bpy.data.objects.get(name)
    if ob is None:
        print("MISSING", name)
        return
    ob["original_location"] = [round(v, 4) for v in ob.location]
    ob["circulation_fix"] = FIX
    ob.location = Vector(ob.location) + Vector(delta)
    print("MOVED", name, "->", tuple(round(v, 3) for v in ob.location))


def world_bounds(ob):
    cs = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    return (min(c.x for c in cs), max(c.x for c in cs),
            min(c.y for c in cs), max(c.y for c in cs),
            min(c.z for c in cs), max(c.z for c in cs))


bpy.context.view_layer.update()
scene = bpy.context.scene

# Table top and its four legs: 3.1 m west, out of the entry axis.
for name in ("NEXUS_V05_C_REC_TABLE_TOP",
             "NEXUS_V05_C_REC_TABLE_LEG_0",
             "NEXUS_V05_C_REC_TABLE_LEG_1",
             "NEXUS_V05_C_REC_TABLE_LEG_2",
             "NEXUS_V05_C_REC_TABLE_LEG_3"):
    move_object(name, (-3.1, 0.0, 0.0))

# Fallen chair B: root plus visible LOD1 duplicate (child is hidden).
for name in ("NEXUS_L1_DIS_CHAIR_REC_B", "NEXUS_L1_DIS_CHAIR_REC_B_01_LOD1"):
    move_object(name, (1.20, 0.0, 0.0))

bpy.context.view_layer.update()

# Conservative overlap report for the moved pieces against all other visible meshes.
moved = [n for n in ("NEXUS_V05_C_REC_TABLE_TOP", "NEXUS_V05_C_REC_TABLE_LEG_0",
                     "NEXUS_V05_C_REC_TABLE_LEG_1", "NEXUS_V05_C_REC_TABLE_LEG_2",
                     "NEXUS_V05_C_REC_TABLE_LEG_3", "NEXUS_L1_DIS_CHAIR_REC_B_01_LOD1")]
moved_boxes = {n: world_bounds(bpy.data.objects[n]) for n in moved if bpy.data.objects.get(n)}
hits = []
for other in scene.objects:
    if other.type != "MESH" or other.hide_render or other.name in moved:
        continue
    b = world_bounds(other)
    for name, a in moved_boxes.items():
        ox = min(a[1], b[1]) - max(a[0], b[0])
        oy = min(a[3], b[3]) - max(a[2], b[2])
        oz = min(a[5], b[5]) - max(a[4], b[4])
        if ox > 0.005 and oy > 0.005 and oz > 0.005:
            hits.append((name, other.name, round(ox * oy * oz, 4)))
for name, other, vol in sorted(hits, key=lambda h: -h[2])[:20]:
    print("OVERLAP", name, other, vol)
print("OVERLAP_COUNT", len(hits))

scene.camera = bpy.data.objects.get("NEXUS_V05_CAM_Recepcion")
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("SAVED", OUT, len(scene.objects))
