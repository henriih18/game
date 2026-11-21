import bpy
import os
from mathutils import Matrix, Vector

ROOT = "/home/riyo/Documentos/game"
DOCS = os.path.join(ROOT, "docs")
RIG = "P0B5C_RENDER_RIG"


def look_at(ob, target):
    forward = (Vector(target) - ob.location).normalized()
    up = Vector((0, 0, 1))
    right = forward.cross(up)
    if right.length < 1e-6:
        right = Vector((1, 0, 0))
    right.normalize()
    up = right.cross(forward).normalized()
    ob.rotation_euler = Matrix((right, up, -forward)).transposed().to_euler()


def area(col, name, loc, energy, size, color, target):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = energy
    data.shape = 'DISK'
    data.size = size
    data.color = color
    ob = bpy.data.objects.new(name, data)
    ob.location = loc
    col.objects.link(ob)
    look_at(ob, target)
    return ob


def camera(col, name, loc, target, lens):
    data = bpy.data.cameras.new(name)
    data.lens = lens
    ob = bpy.data.objects.new(name, data)
    ob.location = loc
    col.objects.link(ob)
    look_at(ob, target)
    return ob


def main():
    scene = bpy.data.scenes["NEXUS_L1_V06_ARCH"]
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.view_settings.look = 'AgX - Medium High Contrast'
    old_exp = scene.view_settings.exposure
    scene.view_settings.exposure = 0.62

    visible_before = {ob.name: (ob.hide_render, ob.hide_viewport, ob.hide_get()) for ob in scene.objects}
    cam_state = {ob.name: ob.hide_render for ob in scene.objects if ob.type == 'CAMERA'}
    for ob in scene.objects:
        ob.hide_render = True

    def show(prefix):
        for col in bpy.data.collections:
            if col.name.startswith(prefix) and "RETIRED" not in col.name:
                for ob in col.all_objects:
                    if ob is not None and ob.name in scene.objects:
                        ob.hide_render = False

    for p in ("L1_P0B5_Z10", "L1_P0B4_Z10", "L1_PROPS_Z10", "L1_KIT_PILOT"):
        show(p)

    col = bpy.data.collections.new(RIG)
    scene.collection.children.link(col)
    area(col, "P0B5C_KEY", (51.0, 17.0, 3.4), 700, 4.5, (1.0, 0.86, 0.70), (55.0, 21.0, 3.6))
    area(col, "P0B5C_FILL", (58.0, 25.0, 2.6), 300, 3.5, (0.62, 0.76, 1.0), (55.7, 22.0, 3.6))
    area(col, "P0B5C_RIM", (50.0, 25.0, 4.2), 420, 3.0, (0.85, 0.92, 1.0), (54.0, 21.0, 3.8))

    shots = [
        ("close", (53.0, 22.6, 2.90), (55.65, 21.55, 3.86), 55),
        ("wide", (48.0, 28.0, 2.6), (53.5, 20.0, 3.6), 22),
    ]
    for tag, loc, target, lens in shots:
        cam = camera(col, "P0B5C_CAM_" + tag, loc, target, lens)
        for c in scene.objects:
            if c.type == 'CAMERA':
                c.hide_render = c is not cam
        scene.camera = cam
        bpy.context.view_layer.update()
        scene.render.filepath = os.path.join(DOCS, "fm_p0b5c_feeds_" + tag + ".png")
        bpy.ops.render.render(write_still=True)
        print("RENDERED", scene.render.filepath)

    for ob in list(col.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.collections.remove(col)
    for ob in scene.objects:
        if ob.name in visible_before:
            hr, hv, hs = visible_before[ob.name]
            ob.hide_render = hr
            ob.hide_viewport = hv
            ob.hide_set(hs)
        if ob.name in cam_state:
            ob.hide_render = cam_state[ob.name]
    scene.view_settings.exposure = old_exp
    print("P0B5C_RENDER_DONE")


main()
