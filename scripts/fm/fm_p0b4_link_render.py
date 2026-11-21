import bpy
import math
from mathutils import Vector

DOCS = "/home/riyo/Documentos/game/docs"
RIG = "P0B4_LINK_RENDER_RIG"

SHOW = {
    "L1_P0B4_Z10",
    "L1_KIT_PILOT",
    "L1_PROPS_Z10",
    "L1_ARCH_CEILINGS",
    "L1_ARCH_FLOORS",
}


def clear_rig():
    col = bpy.data.collections.get(RIG)
    if col:
        for ob in list(col.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.collections.remove(col)


def add_floor(name, size, z, mat):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, z))
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(mat)
    return ob


def simple_mat(name, color, rough=0.6, metallic=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metallic
    return m


def make_light(name, loc, energy, size, color=(1, 1, 1)):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = energy
    data.shape = 'SQUARE'
    data.size = size
    data.color = color
    ob = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    return ob


def point_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def camera(name, loc, target, lens):
    data = bpy.data.cameras.new(name)
    data.lens = lens
    ob = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    point_at(ob, target)
    bpy.context.scene.camera = ob
    return ob


def render(path):
    bpy.context.view_layer.update()
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("RENDERED", path)


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
    hidden = {}
    for ob in scene.objects:
        hidden[ob.name] = ob.hide_render

    clear_rig()
    rig = bpy.data.collections.new(RIG)
    scene.collection.children.link(rig)

    # visibility: only Z10 shell, P0B4, props and ceilings
    for ob in scene.objects:
        if ob.name in hidden and ob.name not in {o.name for o in rig.objects}:
            ob.hide_render = not any(c.name in SHOW for c in ob.users_collection)

    # clamp world
    world = scene.world
    if world and world.use_nodes:
        bg = next((n for n in world.node_tree.nodes if n.type == 'BACKGROUND'), None)
        if bg:
            bg.inputs['Color'].default_value = (0.006, 0.007, 0.009, 1)
            bg.inputs['Strength'].default_value = 0.25

    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = 0.9

    mat_floor = simple_mat("P0B4_LINK_FLOOR_MAT", (0.12, 0.11, 0.10), 0.85)
    floor = add_floor("P0B4_LINK_FLOOR", 12.0, 0.01, mat_floor)
    floor.location.x = 66.0
    floor.location.y = 21.0
    for c in list(floor.users_collection):
        c.objects.unlink(floor)
    rig.objects.link(floor)

    key = make_light("P0B4_LINK_KEY", (64.5, 21.5, 3.6), 900, 2.2)
    fill = make_light("P0B4_LINK_FILL", (64.0, 20.0, 2.6), 500, 2.0, (0.55, 0.68, 1.0))
    rim = make_light("P0B4_LINK_RIM", (69.0, 20.0, 3.4), 400, 1.8, (1.0, 0.55, 0.35))
    for ob in (key, fill, rim):
        for c in list(ob.users_collection):
            c.objects.unlink(ob)
        rig.objects.link(ob)

    camera("P0B4_LINK_CAM", (63.0, 22.2, 2.7), (69.6, 20.0, 3.42), 24)
    render(f"{DOCS}/fm_p0b4_link.png")

    # Riser A close-up: hide ceilings to avoid a black top and move camera close.
    for ob in list(scene.objects):
        if ob.name.startswith("SM_L1_Conn_ServiceLink_Ceiling") or ob.name.startswith("KIT_PILOT_Z10_Ceiling"):
            ob.hide_render = True
    for ob in (key, fill, rim):
        bpy.data.objects.remove(ob, do_unlink=True)
    key = make_light("P0B4_RISER_KEY", (47.6, 17.6, 3.3), 320, 1.6)
    fill = make_light("P0B4_RISER_FILL", (46.8, 14.8, 2.2), 120, 1.4, (0.6, 0.7, 1.0))
    rim = make_light("P0B4_RISER_RIM", (45.0, 16.0, 3.0), 180, 1.2, (1.0, 0.55, 0.35))
    for ob in (key, fill, rim):
        for c in list(ob.users_collection):
            c.objects.unlink(ob)
        rig.objects.link(ob)
    camera("P0B4_RISER_CAM", (48.3, 17.5, 2.0), (46.27, 16.0, 1.7), 55)
    scene.view_settings.exposure = 0.7
    render(f"{DOCS}/fm_p0b4_risers.png")

    # restore
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
    clear_rig()
    print("P0B4_LINK_RENDER_DONE")


main()
