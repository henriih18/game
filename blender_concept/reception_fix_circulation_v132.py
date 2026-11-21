"""Open the reception entrance by retiring the redundant second waiting bench.

The bench (top + four legs) occupies x -12.5..-8.5, y 2.6..3.4, directly in
front of the reception door. The aisle behind it is exactly the 0.76 m player
diameter, so the room is effectively unreachable. A four-metre bench and three
waiting chairs already exist along the west wall, so the second bench is
redundant. This pass hides it (reversibly) instead of deleting or colliding it
with the existing seating.

Run:
  blender -b nexus/nivel_01/NEXUS_L1_V05.blend --python blender_concept/reception_fix_circulation_v132.py
"""

import os

import bpy

ROOT = "/home/riyo/Documentos/game"
OUT = os.path.join(ROOT, "nexus/nivel_01/NEXUS_L1_V05_recepcion_v132.blend")
NAMES = ["NEXUS_V05_REC_BENCH2"] + [
    f"NEXUS_V05_D_REC_BENCH2_LEG_{a}_{b}" for a in (0, 1) for b in (0, 1)
]

for name in NAMES:
    ob = bpy.data.objects.get(name)
    if ob is None:
        raise RuntimeError(f"missing object: {name}")
    ob["original_location"] = tuple(round(v, 4) for v in ob.location)
    ob["circulation_fix"] = "reception_v132_bench_hidden_entrance"
    ob["replaced_by"] = "NEXUS_V05_REC_BENCH;NEXUS_ASSET_L1_REC_WAIT_CHAIR_0_ROOT;NEXUS_ASSET_L1_REC_WAIT_CHAIR_1_ROOT;NEXUS_ASSET_L1_REC_WAIT_CHAIR_2_ROOT"
    ob["hide_reason"] = "blocked the only route between the reception door and the room"
    ob.hide_render = True
    ob.hide_viewport = True

bpy.context.scene.camera = bpy.data.objects.get("NEXUS_V05_CAM_Recepcion")
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("SAVED", OUT, os.path.getsize(OUT), "OBJECTS", len(bpy.context.scene.objects))
print("HIDDEN", [(n, bpy.data.objects[n].hide_render) for n in NAMES])
