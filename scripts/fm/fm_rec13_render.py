import bpy
import os
from mathutils import Matrix, Vector

ROOT = "/home/riyo/Documentos/game"
DOCS = os.path.join(ROOT, "docs")
RIG = "REC13_RENDER_RIG"


def look_at(ob, target):
    forward = (Vector(target) - ob.location).normalized()
    right = forward.cross(Vector((0, 0, 1)))
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

    before = {ob.name: (ob.hide_render, ob.hide_viewport, ob.hide_get()) for ob in scene.objects}
    cam_state = {ob.name: ob.hide_render for ob in scene.objects if ob.type == 'CAMERA'}
    for ob in scene.objects:
        ob.hide_render = True

    for cname in ("L1_RECEPTION_R13_HERO", "L1_RECEPTION_R1", "L1_RECEPTION_R2",
                  "L1_ARCH_SURFACE", "L1_ARCH_CEILINGS", "L1_ARCH_COLUMNS", "L1_ARCH_ZONES"):
        col = bpy.data.collections.get(cname)
        if col:
            for ob in col.all_objects:
                if ob is not None and ob.name in scene.objects:
                    ob.hide_render = False

    col = bpy.data.collections.new(RIG)
    scene.collection.children.link(col)
    area(col, "REC13_KEY", (-102.5, -34.5, 3.4), 700, 4.0, (1.0, 0.86, 0.70), (-106.0, -39.5, 1.1))
    area(col, "REC13_FILL", (-108.5, -35.0, 1.8), 300, 3.0, (0.62, 0.76, 1.0), (-106.0, -39.5, 1.2))
    area(col, "REC13_RIM", (-106.0, -40.2, 3.0), 450, 3.0, (0.85, 0.92, 1.0), (-106.0, -38.8, 1.0))
    area(col, "REC13_DECON_FILL", (-94.0, -31.5, 3.0), 250, 2.5, (1.0, 0.88, 0.74), (-94.0, -33.8, 2.45))
    area(col, "REC13_DESK_FILL", (-102.0, -18.0, 3.0), 220, 2.5, (1.0, 0.88, 0.74), (-102.0, -16.53, 3.55))

    shots = [
        ("lockers_wide", (-101.8, -33.0, 2.25), (-106.0, -39.55, 1.05), 28),
        ("lockers_threequarter", (-103.4, -35.0, 1.85), (-106.0, -39.55, 1.0), 35),
        ("lockers_door", (-105.2, -36.6, 1.55), (-105.2, -39.4, 1.0), 50),
        ("sign_lockers", (-104.2, -35.2, 2.6), (-106.0, -39.3, 2.05), 35),
        ("sign_desk", (-102.0, -18.5, 2.2), (-102.0, -16.53, 3.55), 35),
        ("sign_decon", (-94.0, -30.5, 2.1), (-94.0, -33.85, 2.42), 35),
    ]
    for tag, loc, target, lens in shots:
        cam = camera(col, "REC13_CAM_" + tag, loc, target, lens)
        for c in scene.objects:
            if c.type == 'CAMERA':
                c.hide_render = c is not cam
        scene.camera = cam
        bpy.context.view_layer.update()
        scene.render.filepath = os.path.join(DOCS, "fm_rec13_" + tag + ".png")
        bpy.ops.render.render(write_still=True)
        print("RENDERED", scene.render.filepath)

    for ob in list(col.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.collections.remove(col)
    for ob in scene.objects:
        if ob.name in before:
            hr, hv, hs = before[ob.name]
            ob.hide_render = hr
            ob.hide_viewport = hv
            ob.hide_set(hs)
        if ob.name in cam_state:
            ob.hide_render = cam_state[ob.name]
    scene.view_settings.exposure = old_exp
    print("REC13_RENDER_DONE")


main()
