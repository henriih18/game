"""Review renders for the Z10 abandonment and practical lighting pass."""

import bpy
import math
from mathutils import Vector

OUT = "/home/riyo/Documentos/game/docs"
RIG = "Z10_ABANDON_RENDER_RIG"


def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def camera(coll, name, loc, target, lens):
    data = bpy.data.cameras.new(name)
    data.lens = lens
    ob = bpy.data.objects.new(name, data)
    coll.objects.link(ob)
    ob.location = loc
    look_at(ob, target)
    bpy.context.scene.camera = ob
    return ob


def area(coll, name, loc, target, energy, size, color):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = energy
    data.shape = 'DISK'
    data.size = size
    data.color = color
    ob = bpy.data.objects.new(name, data)
    coll.objects.link(ob)
    ob.location = loc
    look_at(ob, target)
    return ob


def main():
    scene = bpy.context.scene
    saved = {
        "engine": scene.render.engine,
        "x": scene.render.resolution_x,
        "y": scene.render.resolution_y,
        "pct": scene.render.resolution_percentage,
        "samples": scene.cycles.samples,
        "denoise": scene.cycles.use_denoising,
        "exposure": scene.view_settings.exposure,
        "look": scene.view_settings.look,
        "camera": scene.camera.name if scene.camera else None,
    }
    hidden = {ob.name: ob.hide_render for ob in bpy.data.objects}
    for ob in bpy.data.objects:
        ob.hide_render = True

    # New Z10 services.
    for ob in bpy.data.collections.get("L1_P0B4_Z10").all_objects:
        ob.hide_render = False

    # Z10 shell and surviving props, excluding retired services.
    for ob in bpy.data.objects:
        n = ob.name
        if n.startswith("KIT_PILOT_Z10_") or n.startswith("PROP_Z10_"):
            if any(n.startswith(p) for p in (
                "PROP_Z10_HVACDuct", "PROP_Z10_HVACFlange",
                "PROP_Z10_HVACHanger", "PROP_Z10_HVACSupports",
                "PROP_Z10_SVC_HVAC", "PROP_Z10_SprinklerPipe",
                "PROP_Z10_SprinklerHead", "PROP_Z10_SprinklerHanger",
                "PROP_Z10_WestTray", "PROP_Z10_SVC_WestTrayCables",
            )):
                continue
            ob.hide_render = False

    # Abandonment props, practical lights and local volume.
    for cname in ("L1_Z10_ABANDON", "L1_Z10_LIGHTING", "L1_Z10_ATMOSPHERE"):
        col = bpy.data.collections.get(cname)
        if col:
            for ob in col.all_objects:
                ob.hide_render = False

    # Never use the studio key/fill for the review: the point is to test
    # the practical lighting that will ship in the game.
    for n in ("STUDIO_Z10_Key", "STUDIO_Z10_Fill"):
        ob = bpy.data.objects.get(n)
        if ob:
            ob.hide_render = True

    rig = bpy.data.collections.get(RIG)
    if rig:
        for ob in list(rig.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.collections.remove(rig)
    coll = bpy.data.collections.new(RIG)
    scene.collection.children.link(coll)

    # Minimal bounce card so the deep room does not collapse to black.
    area(coll, "Z10_FILL_BOUNCE", (46.0, 12.0, 2.2), (46.0, 20.0, 2.0),
         140.0, 3.0, (0.55, 0.68, 1.0))
    area(coll, "Z10_FILL_BOUNCE_E", (56.0, 20.0, 2.4), (56.0, 26.0, 2.0),
         80.0, 3.0, (0.62, 0.72, 1.0))

    scene.render.engine = 'CYCLES'
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    scene.view_settings.exposure = 1.15
    try:
        scene.view_settings.look = 'AgX - Medium High Contrast'
    except TypeError:
        pass

    camera(coll, "Z10_CAM_WIDE", (42.5, 26.0, 2.0), (56.0, 11.0, 1.5), 18)
    scene.render.filepath = OUT + "/fm_z10_abandon_wide.png"
    bpy.ops.render.render(write_still=True)
    print("RENDERED", scene.render.filepath)

    camera(coll, "Z10_CAM_WORKLIGHT", (52.0, 11.8, 1.65), (56.2, 9.6, 1.45), 35)
    scene.render.filepath = OUT + "/fm_z10_abandon_worklight.png"
    bpy.ops.render.render(write_still=True)
    print("RENDERED", scene.render.filepath)

    camera(coll, "Z10_CAM_CEILING", (48.0, 16.0, 1.6), (51.0, 24.0, 4.0), 20)
    scene.render.filepath = OUT + "/fm_z10_abandon_ceiling.png"
    bpy.ops.render.render(write_still=True)
    print("RENDERED", scene.render.filepath)

    for ob in list(coll.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.collections.remove(coll)
    for name, value in hidden.items():
        ob = bpy.data.objects.get(name)
        if ob:
            ob.hide_render = value
    scene.render.engine = saved["engine"]
    scene.render.resolution_x = saved["x"]
    scene.render.resolution_y = saved["y"]
    scene.render.resolution_percentage = saved["pct"]
    scene.cycles.samples = saved["samples"]
    scene.cycles.use_denoising = saved["denoise"]
    scene.view_settings.exposure = saved["exposure"]
    scene.view_settings.look = saved["look"]
    if saved["camera"]:
        scene.camera = bpy.data.objects.get(saved["camera"])
    print("Z10_ABANDON_RENDER_DONE")


main()
