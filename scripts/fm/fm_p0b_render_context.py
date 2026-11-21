"""Context renders of P0b.1 inside the real corridor (temporary rig)."""
import bpy
import sys
from mathutils import Vector

sys.path.insert(0, "/home/riyo/Documentos/game/scripts/fm")

OUT = "/home/riyo/Documentos/game/docs"
RIG = "P0B_CTX_RIG"


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

    # services
    for ob in bpy.data.collections["L1_P0B_SERVICES"].all_objects:
        ob.hide_render = False
    # corridor shell
    for ob in bpy.data.objects:
        n = ob.name
        if n.startswith("SM_L1_Corridor_Main_") or n.startswith("SM_L1_Corridor_Door_"):
            ob.hide_render = False
    # ceilings are in a hidden collection; enable it only for the render
    ceil = bpy.data.collections.get("L1_ARCH_CEILINGS")
    ceil_state = (ceil.hide_render, ceil.hide_viewport) if ceil else None
    if ceil:
        ceil.hide_render = False
        ceil.hide_viewport = False

    saved_rig = bpy.data.collections.get(RIG)
    if saved_rig:
        for ob in list(saved_rig.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.collections.remove(saved_rig)
    coll = bpy.data.collections.new(RIG)
    scene.collection.children.link(coll)

    # practical corridor lights for validation
    for i, xx in enumerate((-75, -45, -15, 15, 45, 68)):
        area(coll, "P0B_CTX_%02d" % i, (xx, -0.6, 3.72), (xx, -0.6, 0.0),
             900, 3.0, (0.86, 0.93, 1.0))
    area(coll, "P0B_CTX_FILL", (-70, -3.4, 2.4), (0, -1.0, 3.2), 900, 6.0,
         (0.75, 0.82, 1.0))

    scene.render.engine = 'CYCLES'
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.cycles.samples = 48
    scene.cycles.use_denoising = True
    scene.cycles.device = 'GPU'
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = 0.20

    world = scene.world
    if world is None:
        world = bpy.data.worlds.new("P0B_CTX_WORLD")
        scene.world = world
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[0].default_value = (0.006, 0.008, 0.012, 1.0)
    bg.inputs[1].default_value = 0.10

    camera(coll, "P0B_CTX_CAM_LONG", (-72, -2.2, 1.65), (15, -0.8, 3.15), 26)
    bpy.context.view_layer.update()
    scene.render.filepath = OUT + "/fm_p0b_corridor_long.png"
    bpy.ops.render.render(write_still=True)
    print("RENDERED", scene.render.filepath)

    # cutaway: hide the ceiling and the north wall above the Z10 door
    if ceil:
        ceil.hide_render = True
    cut = []
    for n in ("SM_L1_Corridor_Main_Wall_N_7", "SM_L1_Corridor_Door_N_40_L",
              "SM_L1_Corridor_Door_N_40_R", "SM_L1_Corridor_Door_N_40_T"):
        ob = bpy.data.objects.get(n)
        if ob:
            ob.hide_render = True
            cut.append(ob)
    for n in ("PROP_Z10_HVACDuct", "PROP_Z10_HVACFlange_42.0", "PROP_Z10_HVACFlange_44.5",
              "PROP_Z10_HVACSupports"):
        ob = bpy.data.objects.get(n)
        if ob:
            ob.hide_render = False
    area(coll, "P0B_CTX_TOP", (43, 4, 8.5), (43, 4, 3.2), 2600, 12)
    camera(coll, "P0B_CTX_CAM_BRANCH", (28, -10, 10), (43, 6, 3.4), 35)
    bpy.context.view_layer.update()
    scene.render.filepath = OUT + "/fm_p0b_z10_branch.png"
    bpy.ops.render.render(write_still=True)
    print("RENDERED", scene.render.filepath)
    for ob in cut:
        ob.hide_render = False

    for name, value in hidden.items():
        ob = bpy.data.objects.get(name)
        if ob:
            ob.hide_render = value
    if ceil and ceil_state:
        ceil.hide_render, ceil.hide_viewport = ceil_state
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
    print("P0B_CTX_DONE")


if __name__ != "__main__":
    main()
