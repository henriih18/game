"""Review renders for the P0b.4 cable trays in Z10 (temporary rig)."""
import bpy
from mathutils import Vector

OUT = "/home/riyo/Documentos/game/docs"
RIG = "P0B4_TRAY_RENDER_RIG"


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
    for ob in p0b4.all_objects:
        ob.hide_render = False

    # Keep the Z10 shell and surviving props, excluding retired services.
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

    rig = bpy.data.collections.get(RIG)
    if rig:
        for ob in list(rig.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.collections.remove(rig)
    coll = bpy.data.collections.new(RIG)
    scene.collection.children.link(coll)

    area(coll, "TRAY_KEY", (45.0, 18.0, 3.65), (45.0, 22.0, 3.05), 800, 2.5,
         (0.90, 0.95, 1.0))
    area(coll, "TRAY_FILL", (58.0, 26.0, 3.3), (55.0, 20.0, 3.2), 500, 3.0,
         (0.72, 0.84, 1.0))
    area(coll, "TRAY_RIM", (50.0, 9.0, 3.3), (50.0, 16.0, 3.2), 350, 3.0,
         (0.55, 0.65, 0.85))
    area(coll, "TRAY_KEY_EAST", (59.0, 20.0, 3.8), (61.7, 22.0, 3.5), 520, 1.6,
         (1.0, 0.92, 0.82))

    scene.render.engine = 'CYCLES'
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    scene.cycles.device = 'GPU'
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = 0.65

    world = scene.world
    if world is None:
        world = bpy.data.worlds.new("P0B4_TRAY_WORLD")
        scene.world = world
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[0].default_value = (0.004, 0.006, 0.010, 1.0)
    bg.inputs[1].default_value = 0.15

    camera(coll, "TRAY_CAM_WEST", (44.8, 17.0, 2.0), (40.45, 22.0, 3.02), 30)
    bpy.context.view_layer.update()
    scene.render.filepath = OUT + "/fm_p0b4_tray_west.png"
    bpy.ops.render.render(write_still=True)
    print("RENDERED", scene.render.filepath)

    camera(coll, "TRAY_CAM_EAST", (58.5, 20.0, 2.6), (61.7, 22.0, 3.5), 35)
    bpy.context.view_layer.update()
    scene.render.filepath = OUT + "/fm_p0b4_tray_east.png"
    bpy.ops.render.render(write_still=True)
    print("RENDERED", scene.render.filepath)

    camera(coll, "TRAY_CAM_WIDE", (43.0, 10.0, 1.45), (54.0, 23.0, 3.75), 16)
    bpy.context.view_layer.update()
    scene.render.filepath = OUT + "/fm_p0b4_tray_wide.png"
    bpy.ops.render.render(write_still=True)
    print("RENDERED", scene.render.filepath)

    for name, value in hidden.items():
        ob = bpy.data.objects.get(name)
        if ob:
            ob.hide_render = value
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
    print("P0B4_TRAY_RENDER_DONE")


if __name__ != "__main__":
    main()
