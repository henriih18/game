import bpy
from mathutils import Vector

DOCS = "/home/riyo/Documentos/game/docs"
RIG = "P0B4_LINK_RENDER_RIG2"
SHOW = {
    "L1_P0B4_Z10",
    "L1_KIT_PILOT",
    "L1_PROPS_Z10",
    "L1_ARCH_CEILINGS",
    "L1_ARCH_CIRCULATION",
    "L1_ARCH_ZONES",
    "L1_ARCH_SHELL",
}


def point_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def make_light(name, loc, target, energy, size, color=(1, 1, 1)):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = energy
    data.shape = 'SQUARE'
    data.size = size
    data.color = color
    ob = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    point_at(ob, target)
    return ob


def main():
    scene = bpy.context.scene
    saved = {
        "engine": scene.render.engine,
        "res_x": scene.render.resolution_x,
        "res_y": scene.render.resolution_y,
        "res_pct": scene.render.resolution_percentage,
        "samples": scene.cycles.samples,
        "exposure": scene.view_settings.exposure,
        "look": scene.view_settings.look,
        "filepath": scene.render.filepath,
    }
    hidden = {ob.name: ob.hide_render for ob in scene.objects}

    old = bpy.data.collections.get(RIG)
    if old:
        for ob in list(old.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.collections.remove(old)
    rig = bpy.data.collections.new(RIG)
    scene.collection.children.link(rig)

    for ob in scene.objects:
        if ob.name in hidden:
            ob.hide_render = not any(c.name in SHOW for c in ob.users_collection)

    world = scene.world
    if world and world.use_nodes:
        bg = next((n for n in world.node_tree.nodes if n.type == 'BACKGROUND'), None)
        if bg:
            bg.inputs['Color'].default_value = (0.005, 0.006, 0.008, 1)
            bg.inputs['Strength'].default_value = 0.25

    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = 0.55

    key = make_light("P0B4_LINK_KEY2", (65.2, 21.8, 3.35), (69.6, 20.0, 3.55), 700, 2.6, (1.0, 0.93, 0.82))
    fill = make_light("P0B4_LINK_FILL2", (64.0, 20.2, 2.15), (69.2, 20.0, 3.4), 420, 2.2, (0.55, 0.68, 1.0))
    rim = make_light("P0B4_LINK_RIM2", (68.6, 18.7, 3.1), (69.4, 20.0, 3.5), 480, 1.8, (1.0, 0.6, 0.4))
    for ob in (key, fill, rim):
        for c in list(ob.users_collection):
            c.objects.unlink(ob)
        rig.objects.link(ob)

    cam_data = bpy.data.cameras.new("P0B4_LINK_CAM2")
    cam_data.lens = 30
    cam = bpy.data.objects.new("P0B4_LINK_CAM2", cam_data)
    scene.collection.objects.link(cam)
    cam.location = (66.0, 22.6, 2.55)
    point_at(cam, (69.9, 20.0, 3.45))
    scene.camera = cam

    bpy.context.view_layer.update()
    scene.render.filepath = f"{DOCS}/fm_p0b4_link.png"
    bpy.ops.render.render(write_still=True)
    print("RENDERED", scene.render.filepath)

    for ob in scene.objects:
        if ob.name in hidden:
            ob.hide_render = hidden[ob.name]
    scene.render.engine = saved["engine"]
    scene.render.resolution_x = saved["res_x"]
    scene.render.resolution_y = saved["res_y"]
    scene.render.resolution_percentage = saved["res_pct"]
    scene.cycles.samples = saved["samples"]
    scene.view_settings.exposure = saved["exposure"]
    scene.view_settings.look = saved["look"]
    scene.render.filepath = saved["filepath"]
    for ob in list(rig.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.collections.remove(rig)
    print("P0B4_LINK_RENDER2_DONE")


main()
