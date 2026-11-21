import bpy
import os
from mathutils import Matrix, Vector

ROOT = "/home/riyo/Documentos/game"
DOCS = os.path.join(ROOT, "docs")
RIG = "REC09_SPR_RENDER_RIG"


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
    scene.view_settings.exposure = 0.78

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

    for p in ("L1_RECEPTION_R1", "L1_RECEPTION_R2", "L1_RECEPTION_R3",
              "L1_RECEPTION_R5", "L1_RECEPTION_R6_HERO", "L1_RECEPTION_R7_HERO",
              "L1_RECEPTION_R8_HERO", "L1_RECEPTION_R9_HERO",
              "L1_ARCH_SURFACE", "L1_ARCH_CEILINGS", "L1_ARCH_COLUMNS",
              "L1_ARCH_ZONES", "L1_ARCH_CIRCULATION"):
        show(p)

    col = bpy.data.collections.new(RIG)
    scene.collection.children.link(col)
    area(col, "REC09_SPR_KEY", (-73.0, -23.0, 3.5), 1050, 5.0, (1.0, 0.84, 0.68), (-92.0, -30.0, 4.2))
    area(col, "REC09_SPR_FILL", (-92.0, -36.0, 2.7), 450, 4.0, (0.62, 0.76, 1.0), (-92.0, -30.0, 4.2))
    area(col, "REC09_SPR_RIM", (-105.0, -22.0, 4.8), 760, 4.0, (0.85, 0.92, 1.0), (-92.0, -30.0, 4.2))

    shots = [
        ("wide", (-71.5, -24.0, 2.3), (-94.0, -30.0, 4.2), 20),
        ("line", (-74.0, -26.5, 3.6), (-105.0, -30.0, 4.3), 24),
        ("heads", (-92.0, -26.0, 3.7), (-92.0, -30.0, 4.62), 50),
        ("sleeve", (-72.8, -26.0, 3.7), (-70.0, -30.0, 4.6), 50),
    ]
    for tag, loc, target, lens in shots:
        cam = camera(col, "REC09_SPR_CAM_" + tag, loc, target, lens)
        for c in scene.objects:
            if c.type == 'CAMERA':
                c.hide_render = c is not cam
        scene.camera = cam
        bpy.context.view_layer.update()
        scene.render.filepath = os.path.join(DOCS, "fm_reception_r9_sprinkler_" + tag + ".png")
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
    print("REC09_SPRINKLER_RENDER_DONE")


main()
