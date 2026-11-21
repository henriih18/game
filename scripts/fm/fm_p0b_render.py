"""Render P0b.1 corridor services (temporary rig, does not save the .blend)."""
import bpy
import math
import sys
from mathutils import Vector

sys.path.insert(0, "/home/riyo/Documentos/game/scripts/fm")

OUT = "/home/riyo/Documentos/game/docs"
RIG = "P0B_RENDER_RIG"


def simple_mat(name, color, rough=0.7, metal=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    return m


def clear_rig():
    c = bpy.data.collections.get(RIG)
    if c:
        for ob in list(c.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.collections.remove(c)


def add_floor(coll, z, size=220.0):
    me = bpy.data.meshes.new("P0B_FLOOR")
    verts = [(-size, -size, z), (size, -size, z), (size, size, z), (-size, size, z)]
    me.from_pydata(verts, [], [(0, 1, 2, 3)])
    me.update()
    ob = bpy.data.objects.new("P0B_FLOOR", me)
    coll.objects.link(ob)
    me.materials.append(simple_mat("P0B_FLOOR_MAT", (0.022, 0.024, 0.028), 0.92))
    return ob


def add_light(coll, name, loc, energy, size, color=(1, 1, 1)):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = energy
    data.shape = 'SQUARE'
    data.size = size
    data.color = color
    ob = bpy.data.objects.new(name, data)
    coll.objects.link(ob)
    ob.location = loc
    return ob


def aim(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def add_camera(coll, name, loc, target, lens):
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
        "res_x": scene.render.resolution_x,
        "res_y": scene.render.resolution_y,
        "pct": scene.render.resolution_percentage,
        "samples": getattr(scene.cycles, "samples", 64),
        "use_denoise": getattr(scene.cycles, "use_denoising", True),
        "exposure": scene.view_settings.exposure,
        "look": scene.view_settings.look,
        "world": scene.world.name if scene.world else None,
        "camera": scene.camera.name if scene.camera else None,
    }
    hidden = {ob.name: ob.hide_render for ob in bpy.data.objects}
    for ob in bpy.data.objects:
        ob.hide_render = True

    svc = bpy.data.collections.get("L1_P0B_SERVICES")
    for ob in svc.all_objects:
        ob.hide_render = False

    clear_rig()
    coll = bpy.data.collections.new(RIG)
    scene.collection.children.link(coll)
    add_floor(coll, -0.02)

    key = add_light(coll, "P0B_KEY", (-55, -7, 4.0), 3200, 10)
    aim(key, (-30, -1.6, 3.5))
    fill = add_light(coll, "P0B_FILL", (10, -8, 3.2), 1800, 9, (0.75, 0.85, 1.0))
    aim(fill, (25, -1.6, 3.4))
    rim = add_light(coll, "P0B_RIM", (45, 5, 4.4), 2600, 8)
    aim(rim, (43, 2, 3.5))
    far = add_light(coll, "P0B_FAR", (65, -7, 4.0), 2200, 9)
    aim(far, (45, -0.5, 3.4))

    scene.render.engine = 'CYCLES'
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.cycles.samples = 48
    scene.cycles.use_denoising = True
    scene.cycles.device = 'GPU'
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = 0.30

    world = scene.world
    if world is None:
        world = bpy.data.worlds.new("P0B_WORLD")
        scene.world = world
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[0].default_value = (0.008, 0.010, 0.014, 1.0)
    bg.inputs[1].default_value = 0.15

    # long view
    add_camera(coll, "P0B_CAM_LONG", (-25, -14, 8.5), (15, 0, 3.3), 32)
    bpy.context.view_layer.update()
    scene.render.filepath = OUT + "/fm_p0b_corridor_long.png"
    bpy.ops.render.render(write_still=True)
    print("RENDERED", scene.render.filepath)

    # branch / Z10 connection
    add_camera(coll, "P0B_CAM_BRANCH", (25, -14, 9.0), (43, 8, 3.3), 35)
    bpy.context.view_layer.update()
    scene.render.filepath = OUT + "/fm_p0b_z10_branch.png"
    bpy.ops.render.render(write_still=True)
    print("RENDERED", scene.render.filepath)

    # close-up of the main tee / sleeve
    add_camera(coll, "P0B_CAM_TEE", (35, -9, 7.0), (43, 5, 3.4), 42)
    bpy.context.view_layer.update()
    scene.render.filepath = OUT + "/fm_p0b_tee.png"
    bpy.ops.render.render(write_still=True)
    print("RENDERED", scene.render.filepath)

    # restore
    for name, value in hidden.items():
        ob = bpy.data.objects.get(name)
        if ob:
            ob.hide_render = value
    clear_rig()
    scene.render.engine = saved["engine"]
    scene.render.resolution_x = saved["res_x"]
    scene.render.resolution_y = saved["res_y"]
    scene.render.resolution_percentage = saved["pct"]
    scene.cycles.samples = saved["samples"]
    scene.cycles.use_denoising = saved["use_denoise"]
    scene.view_settings.exposure = saved["exposure"]
    scene.view_settings.look = saved["look"]
    if saved["world"]:
        scene.world = bpy.data.worlds.get(saved["world"])
    if saved["camera"]:
        scene.camera = bpy.data.objects.get(saved["camera"])
    print("P0B_RENDER_DONE")


if __name__ != "__main__":
    main()
