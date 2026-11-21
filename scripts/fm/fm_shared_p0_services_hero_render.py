"""P0a.1 review renders: fittings with visible branch/bore, shaft access."""
import bpy
import math
from mathutils import Vector

DOCS = "/home/riyo/Documentos/game/docs/"
RIG = "P0A1_RIG2"
SHOW = "P0A1_SHOW2"


def look_at(cam, target):
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat('-Z', 'Y').to_euler()


def light(coll, name, loc, energy, size, color=(1, 1, 1)):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy = energy
    ld.size = size
    ld.color = color
    ob = bpy.data.objects.new(name, ld)
    ob.location = loc
    coll.objects.link(ob)
    return ob


def mat(name, base, rough=0.65):
    m = bpy.data.materials.new(name)
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs["Base Color"].default_value = (base, base, base, 1)
    b.inputs["Roughness"].default_value = rough
    return m


def main():
    scene = bpy.context.scene
    old = (scene.render.engine, scene.render.resolution_x, scene.render.resolution_y,
           scene.render.resolution_percentage, scene.cycles.samples,
           scene.view_settings.view_transform, scene.view_settings.look,
           scene.view_settings.exposure, scene.camera, scene.render.filepath)
    for n in (RIG, SHOW):
        c = bpy.data.collections.get(n)
        if c:
            for ob in list(c.all_objects):
                bpy.data.objects.remove(ob, do_unlink=True)
            bpy.data.collections.remove(c)
    rig = bpy.data.collections.new(RIG)
    scene.collection.children.link(rig)
    show = bpy.data.collections.new(SHOW)
    scene.collection.children.link(show)
    for ob in bpy.data.objects:
        if ob.type in ('MESH', 'LIGHT', 'CAMERA', 'EMPTY'):
            ob.hide_render = True

    fm = mat("M_P0A1_FLOOR2", 0.08, 0.62)
    bpy.ops.mesh.primitive_plane_add(size=60, location=(2.0, 0, -0.006))
    floor = bpy.context.active_object
    floor.name = "P0A1_FLOOR2"
    floor.data.materials.append(fm)
    for c in list(floor.users_collection):
        c.objects.unlink(floor)
    rig.objects.link(floor)

    def inst(target, loc, rot=(0, 0, 0)):
        ob = bpy.data.objects.new("SHOW2_" + target, bpy.data.objects[target].data)
        ob.location = loc
        ob.rotation_euler = rot
        show.objects.link(ob)
        return ob

    inst("SM_SH_HVAC_RECT800x600_L2000", (-1.55, 0.0, 0.31), (0, 0, math.radians(8)))
    t = inst("SM_SH_HVAC_TEE_800x600", (0.75, 0.0, 0.30), (math.radians(180), 0, 0))
    inst("SM_SH_HVAC_TRANS_800x600_600x400", (2.55, 0.0, 0.30), (0, 0, 0))
    inst("SM_SH_HVAC_GRILLE_600x400", (3.55, 0.0, 0.25), (0, 0, 0))
    inst("SM_SH_HVAC_DAMPER_800x600", (4.55, 0.0, 0.30), (0, 0, 0))
    inst("SM_SH_FIREDAMPER_800x600", (5.45, 0.0, 0.30), (0, 0, 0))

    cd = bpy.data.cameras.new("CAM_FIT2")
    cd.lens = 42
    cam = bpy.data.objects.new("CAM_FIT2", cd)
    cam.location = (5.6, -7.6, 3.6)
    rig.objects.link(cam)
    look_at(cam, (2.0, 0.0, 0.55))

    key = light(rig, "KEY2", (1.0, -5.0, 5.5), 1900, 8.0, (1.0, 0.96, 0.9))
    fill = light(rig, "FILL2", (-4.0, -3.0, 2.6), 750, 6.0, (0.7, 0.82, 1.0))
    rim = light(rig, "RIM2", (7.0, 3.0, 4.5), 1500, 6.0, (0.82, 0.9, 1.0))

    world = scene.world or bpy.data.worlds.new("P0A1_WORLD2")
    scene.world = world
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs["Color"].default_value = (0.008, 0.010, 0.014, 1)
    bg.inputs["Strength"].default_value = 0.30

    scene.render.engine = 'CYCLES'
    scene.render.resolution_x = 1440
    scene.render.resolution_y = 810
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.cycles.samples = 80
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.02
    scene.cycles.use_denoising = True
    scene.cycles.device = 'GPU'
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = 0.5

    scene.camera = cam
    scene.render.filepath = DOCS + "fm_p0a1_hero_fittings2.png"
    if False:
        bpy.ops.render.render(write_still=True)
        print("RENDERED fittings2")

    # shaft scene
    for ob in list(show.all_objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    wall = mat("M_P0A1_WALL2", 0.055, 0.8)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.105, 1.0))
    back = bpy.context.active_object
    back.name = "P0A1_BACKWALL"
    back.scale = (2.4, 0.20, 2.6)
    back.data.materials.append(wall)
    for c in list(back.users_collection):
        c.objects.unlink(back)
    show.objects.link(back)
    inst("SM_SH_SHAFT_ACCESS_600x1200", (0.0, -0.02, 0.0), (0, 0, math.radians(180)))
    inst("SM_SH_SLEEVE_RECT_800x600", (-1.25, -0.05, 0.35), (0, math.radians(10), 0))
    inst("SM_SH_SLEEVE_RECT_600x400", (1.05, -0.05, 0.45), (0, math.radians(-10), 0))

    cam.location = (0.15, -4.4, 1.55)
    look_at(cam, (0.0, 0.0, 0.62))
    cd.lens = 52
    key.location = (0.6, -3.0, 3.6); key.data.energy = 900; key.data.size = 4.0
    fill.location = (-2.4, -2.0, 1.6); fill.data.energy = 350; fill.data.size = 4.0
    rim.location = (2.6, 1.6, 3.0); rim.data.energy = 700; rim.data.size = 4.0

    scene.render.filepath = DOCS + "fm_p0a1_shaft_hero.png"
    bpy.ops.render.render(write_still=True)
    print("RENDERED shaft")

    for ob in list(rig.all_objects) + list(show.all_objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.collections.remove(rig)
    bpy.data.collections.remove(show)
    for m in ("M_P0A1_FLOOR2", "M_P0A1_WALL2"):
        mm = bpy.data.materials.get(m)
        if mm:
            bpy.data.materials.remove(mm)
    for ob in bpy.data.objects:
        if ob.type in ('MESH', 'LIGHT', 'CAMERA', 'EMPTY'):
            ob.hide_render = False
    scene.render.engine, scene.render.resolution_x, scene.render.resolution_y, \
        scene.render.resolution_percentage, scene.cycles.samples, \
        scene.view_settings.view_transform, scene.view_settings.look, \
        scene.view_settings.exposure, scene.camera, scene.render.filepath = old
    print("P0A1_RENDER2_DONE")


main()
