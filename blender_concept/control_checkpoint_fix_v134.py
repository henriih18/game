"""Clear the central lane through the Level 1 access-control detector.

The queue belt and its central post sit exactly under the body scanner: the
barrier's plan-view footprint (x 12.82..13.18, y 3.05..4.95) plus the player
radius closes the 1.70 m detector opening (x 12.24..13.76) to a 1.30 m clear
span, and the post adds a second pinch. Players can only bypass the scanner by
walking around the whole checkpoint.

This pass retracts the central belt and marks the post as removed during the
evacuation, reversibly (hidden, never deleted). The two outer queue lines stay.
"""

import os

import bpy

ROOT = "/home/riyo/Documentos/game"
OUT = os.path.join(ROOT, "nexus/nivel_01/NEXUS_L1_V05_control_v134.blend")
FIX = "control_v134_clear_detector_lane"

BARRIER = "NEXUS_V05_ACC_BARRIER_1"
POST = "NEXUS_V05_ACC_POST_1"


def hide_for_fix(ob, reason):
    ob["original_location"] = list(ob.location)
    ob["original_hide_render"] = bool(ob.hide_render)
    ob["original_hide_viewport"] = bool(ob.hide_viewport)
    ob["circulation_fix"] = FIX
    ob["hide_reason"] = reason
    ob["hide_render"] = True
    ob["hide_viewport"] = True
    ob.hide_render = True
    ob.hide_viewport = True


def main():
    barrier = bpy.data.objects.get(BARRIER)
    post = bpy.data.objects.get(POST)
    if barrier is None or post is None:
        raise RuntimeError("Missing central checkpoint objects")
    hide_for_fix(barrier, "central queue belt retracted for scanner access")
    hide_for_fix(post, "central queue post removed during evacuation")
    barrier["checkpoint_state"] = "retracted"
    post["checkpoint_state"] = "removed"

    # Leave the level file on its usual review camera.
    camera = bpy.data.objects.get("NEXUS_V05_CAM_Recepcion")
    if camera is not None:
        bpy.context.scene.camera = camera

    bpy.ops.wm.save_as_mainfile(filepath=OUT)
    print("SAVED", OUT)
    print("HIDDEN", BARRIER, POST)
    print("OBJECTS", len(bpy.context.scene.objects))
    print("CAMERA", bpy.context.scene.camera.name if bpy.context.scene.camera else None)


if __name__ == "__main__":
    main()
