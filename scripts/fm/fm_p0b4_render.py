"""Context and close-up renders of P0b.4 Z10 services (temporary rig)."""
import bpy
import sys
from mathutils import Vector

OUT = "/home/riyo/Documentos/game/docs"
RIG = "P0B4_RENDER_RIG"


def aim(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def area(coll, name, loc, target, energy, size, color=(1, 1, 1)):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = energy
    data.shape = 'SQUARE'
    data.size = size
    data.color = color
    ob = bpy.data.objects.new(name, data)
    coll.objects.link(ob)
    ob.location = loc
    aim(ob, target)
    try:
        ob.visible_camera = False
    except AttributeError:
        pass
    return ob


def camera(coll, name, loc, target, lens):
    data = bpy.data.cameras.new(name)
    data.lens = lens
    ob = bpy.data.objects.new(name, data)
    coll.objects.link(ob)
    ob.location = loc
    aim(ob, target)
    bpy.context.scene.camera = ob
    return ob


def show(ob, state):
    ob.hide_render = state


def main():
    scene = bpy.context.scene
    saved = {
        "engine": scene.render.engine,
        "x": scene.render.resolution_x, "y": scene.render.resolution_y,
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

    p0b4 = bpy.data.collections.get("L1_P0B4_Z10")
    ret = bpy.data.collections.get("Z10_RETIRED_P0B4")
    ret_state = (ret.hide_render, ret.hide_viewport) if ret else None
    if ret:
        ret.hide_render = True
        ret.hide_viewport = True
    for ob in p0b4.all_objects:
        ob.hide_render = False

    # Z10 shell and surviving props.
    for ob in bpy.data.objects:
        n = ob.name
        if n.startswith("KIT_PILOT_Z10_") or n.startswith("PROP_Z10_"):
            if n.startswith("PROP_Z10_HVACDuct") or n.startswith("PROP_Z10_HVACFlange"):
                continue
            if n.startswith("PROP_Z10_HVACHanger") or n.startswith("PROP_Z10_HVACSupports"):
                continue
            if n.startswith("PROP_Z10_SVC_HVAC"):
                continue
            if n.startswith("PROP_Z10_SprinklerPipe") or n.startswith("PROP_Z10_SprinklerHead"):
                continue
            if n.startswith("PROP_Z10_SprinklerHanger"):
                continue
            ob.hide_render = False

    rig = bpy.data.collections.get(RIG)
    if rig:
        for ob in list(rig.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.collections.remove(rig)
    coll = bpy.data.collections.new(RIG)
    scene.collection.children.link(coll)

    area(coll, "P0B4_KEY_A", (43.5, 12.0, 3.75), (50.0, 20.0, 3.45), 1100, 3.0,
         (0.90, 0.95, 1.0))
    area(coll, "P0B4_KEY_B", (56.0, 13.5, 3.75), (55.0, 21.0, 3.45), 900, 3.0,
         (0.86, 0.92, 1.0))
    area(coll, "P0B4_RIM", (52.0, 27.0, 3.65), (52.0, 18.0, 3.5), 700, 4.0,
         (0.75, 0.85, 1.0))
    area(coll, "P0B4_FILL", (50.0, 10.0, 1.8), (50.0, 20.0, 2.6), 350, 6.0,
         (0.55, 0.65, 0.85))

    scene.render.engine = 'CYCLES'
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    scene.cycles.device = 'GPU'
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = 0.45

    world = scene.world
    if world is None:
        world = bpy.data.worlds.new("P0B4_RENDER_WORLD")
        scene.world = world
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[0].default_value = (0.004, 0.006, 0.010, 1.0)
    bg.inputs[1].default_value = 0.18

    camera(coll, "P0B4_CAM_CONTEXT", (42.0, 12.0, 2.15), (53.0, 20.0, 3.38), 24)
    bpy.context.view_layer.update()
    scene.render.filepath = OUT + "/fm_p0b4_z10_context.png"
    bpy.ops.render.render(write_still=True)
    print("RENDERED", scene.render.filepath)

    camera(coll, "P0B4_CAM_DETAIL", (52.5, 16.4, 2.25), (59.5, 20.0, 3.42), 38)
    bpy.context.view_layer.update()
    scene.render.filepath = OUT + "/fm_p0b4_z10_detail.png"
    bpy.ops.render.render(write_still=True)
    print("RENDERED", scene.render.filepath)

    for name, value in hidden.items():
        ob = bpy.data.objects.get(name)
        if ob:
            ob.hide_render = value
    if ret and ret_state:
        ret.hide_render, ret.hide_viewport = ret_state
    for ob in list(coll.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.collections.remove(coll)
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
    print("P0B4_RENDER_DONE")


if __name__ != "__main__":
    main()
