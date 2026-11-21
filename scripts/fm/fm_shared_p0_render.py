"""
P0a render pass: doors, lighting, services and continuity test.
Temporary studio rig is created, used and deleted; render settings restored.
"""
import bpy
import math
from mathutils import Vector

DOCS = "/home/riyo/Documentos/game/docs/"
SHARED = "L1_SHARED_HERO"
TEST = "P0_TEST_ASSEMBLY"
RIG = "P0_RENDER_RIG"


def look_at(cam, target):
    d = Vector(target) - cam.location
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def new_light(coll, name, loc, energy, size, color=(1, 1, 1)):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy = energy
    ld.size = size
    ld.color = color
    ob = bpy.data.objects.new(name, ld)
    ob.location = loc
    coll.objects.link(ob)
    return ob


def make_studio_mat(name, base, rough=0.7):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs["Base Color"].default_value = (base, base, base, 1)
    b.inputs["Roughness"].default_value = rough
    m.diffuse_color = (base, base, base, 1)
    return m


def hide_level(enable):
    for col in bpy.data.collections:
        if col.name in (SHARED, TEST, RIG):
            continue
        for ob in col.all_objects:
            if ob.type in ('MESH', 'LIGHT', 'CAMERA', 'EMPTY'):
                ob.hide_render = enable


def main():
    scene = bpy.context.scene
    old = {
        "engine": scene.render.engine,
        "resx": scene.render.resolution_x,
        "resy": scene.render.resolution_y,
        "resz": scene.render.resolution_percentage,
        "samples": getattr(scene, "cycles", None).samples if hasattr(scene, "cycles") else None,
        "view": scene.view_settings.view_transform,
        "look": scene.view_settings.look,
        "exp": scene.view_settings.exposure,
        "cam": scene.camera,
        "filepath": scene.render.filepath,
    }
    # remove previous rig
    c = bpy.data.collections.get(RIG)
    if c:
        for ob in list(c.all_objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.collections.remove(c)
    rig = bpy.data.collections.new(RIG)
    scene.collection.children.link(rig)

    floor_mat = make_studio_mat("M_P0_STUDIO_Floor", 0.11, 0.72)
    wall_mat = make_studio_mat("M_P0_STUDIO_Wall", 0.045, 0.8)

    # huge neutral floor, low enough for all shots
    bpy.ops.mesh.primitive_plane_add(size=400, location=(150, 0, -0.025))
    floor = bpy.context.active_object
    floor.name = "P0_RIG_Floor"
    floor.data.materials.append(floor_mat)
    for c2 in list(floor.users_collection):
        c2.objects.unlink(floor)
    rig.objects.link(floor)

    # cameras
    def cam(name, loc, target, lens):
        cd = bpy.data.cameras.new(name)
        cd.lens = lens
        ob = bpy.data.objects.new(name, cd)
        ob.location = loc
        rig.objects.link(ob)
        look_at(ob, target)
        return ob

    cam_doors = cam("P0_CAM_Doors", (5.6, -12.5, 3.4), (5.8, 0, 1.35), 35)
    cam_lights = cam("P0_CAM_Lights", (2.8, -4.6, 2.15), (2.8, 0, 1.65), 35)
    cam_services = cam("P0_CAM_Services", (5.2, -9.5, 9.5), (5.2, 8.0, 0.35), 35)
    cam_test = cam("P0_CAM_Test", (305.2, -6.8, 4.2), (300.9, 0.0, 3.0), 30)

    # lights (repositioned per shot)
    key = new_light(rig, "P0_KEY", (2, -6, 6), 1400, 7.0, (1.0, 0.96, 0.9))
    fill = new_light(rig, "P0_FILL", (-4, -4, 3), 500, 6.0, (0.72, 0.82, 1.0))
    rim = new_light(rig, "P0_RIM", (8, 3, 5), 1100, 5.0, (0.8, 0.9, 1.0))

    world = scene.world
    if world is None:
        world = bpy.data.worlds.new("P0_WORLD")
        scene.world = world
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs["Color"].default_value = (0.010, 0.012, 0.016, 1)
    bg.inputs["Strength"].default_value = 0.35

    # render settings
    scene.render.engine = 'CYCLES'
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = 'PNG'
    scene.cycles.samples = 128
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.02
    scene.cycles.use_denoising = True
    scene.cycles.device = 'GPU'
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = 0.45

    hide_level(True)

    def do(name, camera, key_loc, fill_loc, rim_loc, energy=(1400, 500, 1100)):
        key.location = key_loc
        fill.location = fill_loc
        rim.location = rim_loc
        key.data.energy, fill.data.energy, rim.data.energy = energy
        scene.camera = camera
        scene.render.filepath = DOCS + name
        bpy.ops.render.render(write_still=True)
        print("RENDERED", name)

    do("fm_shared_p0_doors.png", cam_doors,
       (2.0, -8.0, 6.5), (-4.0, -5.0, 2.5), (14.0, 4.0, 7.0))
    do("fm_shared_p0_lighting.png", cam_lights,
       (0.5, -3.2, 2.8), (-1.5, -2.0, 1.6), (5.5, 2.0, 3.0),
       (220, 60, 140))
    do("fm_shared_p0_services.png", cam_services,
       (0.0, -6.0, 14.0), (-5.0, 2.0, 6.0), (12.0, 12.0, 10.0),
       (2600, 900, 1800))
    do("fm_shared_p0_test_assembly.png", cam_test,
       (302.0, -5.0, 7.0), (299.0, 2.0, 3.0), (304.0, 4.0, 6.0),
       (1200, 450, 900))

    hide_level(False)
    # restore
    scene.render.engine = old["engine"]
    scene.render.resolution_x = old["resx"]
    scene.render.resolution_y = old["resy"]
    scene.render.resolution_percentage = old["resz"]
    if old["samples"] is not None:
        scene.cycles.samples = old["samples"]
    scene.view_settings.view_transform = old["view"]
    scene.view_settings.look = old["look"]
    scene.view_settings.exposure = old["exp"]
    scene.camera = old["cam"]
    scene.render.filepath = old["filepath"]
    # remove rig
    for ob in list(rig.all_objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.collections.remove(rig)
    for m in ("M_P0_STUDIO_Floor", "M_P0_STUDIO_Wall"):
        mat = bpy.data.materials.get(m)
        if mat:
            bpy.data.materials.remove(mat)
    print("P0_RENDER_DONE")


if __name__ == "__main__":
    main()
