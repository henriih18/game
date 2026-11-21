import bpy
import os
from mathutils import Vector, Matrix

ROOT = "/home/riyo/Documentos/game"
DOCS = os.path.join(ROOT, "docs")
RIG = "REC08_RENDER_RIG"

INCLUDE = [
    "L1_RECEPTION_R8_HERO",
    "L1_RECEPTION_R7_HERO",
    "L1_RECEPTION_R6_HERO",
    "L1_RECEPTION_R1",
    "L1_RECEPTION_R2",
    "L1_RECEPTION_R3",
    "L1_RECEPTION_R5",
    "L1_ARCH_CIRCULATION",
    "L1_ARCH_CEILINGS",
    "L1_ARCH_COLUMNS",
    "L1_ARCH_ZONES",
    "L1_ARCH_SURFACE",
]


def camera(col, name, loc, target, lens):
    data = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, data)
    col.objects.link(cam)
    cam.location = loc
    forward = (Vector(target) - Vector(loc)).normalized()
    world_up = Vector((0.0, 0.0, 1.0))
    right = forward.cross(world_up)
    if right.length < 1e-6:
        right = Vector((1.0, 0.0, 0.0))
    right.normalize()
    up = right.cross(forward).normalized()
    rot = Matrix((right, up, -forward)).transposed()
    cam.rotation_euler = rot.to_euler()
    data.lens = lens
    return cam


def area(col, name, loc, target, power, size, color):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = power
    data.shape = 'DISK'
    data.size = size
    data.color = color
    ob = bpy.data.objects.new(name, data)
    col.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob


def main():
    scene = bpy.context.scene
    vl = bpy.context.view_layer
    old = {
        "engine": scene.render.engine,
        "res_x": scene.render.resolution_x,
        "res_y": scene.render.resolution_y,
        "samples": scene.cycles.samples,
        "denoise": scene.cycles.use_denoising,
        "exposure": scene.view_settings.exposure,
        "view": scene.view_settings.view_transform,
        "look": scene.view_settings.look,
        "world": tuple(scene.world.color) if scene.world else None,
    }
    saved = {}
    for ob in bpy.data.objects:
        saved[ob.name] = (ob.hide_render, ob.hide_viewport, ob.hide_get())
        ob.hide_render = True

    for cname in INCLUDE:
        c = bpy.data.collections.get(cname)
        if not c:
            print("MISSING_COLLECTION", cname)
            continue
        for ob in c.all_objects:
            st = saved.get(ob.name)
            if st and not st[0] and not st[1]:
                ob.hide_render = False

    bpy.context.view_layer.update()

    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.cycles.samples = 96
    scene.cycles.use_denoising = True
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = 0.55
    if scene.world:
        scene.world.color = (0.012, 0.014, 0.018)

    col = bpy.data.collections.new(RIG)
    scene.collection.children.link(col)
    area(col, "REC08_KEY", (-91.0, -9.4, 3.4), (-87.4, -11.6, 0.85),
         620.0, 4.5, (1.0, 0.92, 0.80))
    area(col, "REC08_FILL", (-84.0, -13.8, 2.3), (-87.4, -11.4, 0.9),
         240.0, 3.5, (0.72, 0.84, 1.0))
    area(col, "REC08_RIM", (-87.2, -15.2, 3.0), (-87.6, -11.0, 1.1),
         420.0, 3.0, (1.0, 0.88, 0.72))

    shots = [
        ("wide", (-92.8, -16.6, 2.4), (-87.4, -11.4, 0.9), 24),
        ("threequarter", (-83.4, -16.2, 1.95), (-87.4, -11.3, 0.9), 28),
        ("stanchion", (-90.4, -12.3, 1.35), (-89.0, -10.65, 0.82), 55),
        ("barrier", (-88.2, -8.6, 1.9), (-85.0, -9.8, 0.95), 30),
        ("detail", (-87.9, -11.9, 1.25), (-89.0, -10.55, 0.91), 68),
    ]
    for tag, loc, target, lens in shots:
        cam = camera(col, "REC08_CAM_" + tag, loc, target, lens)
        for ob in bpy.data.objects:
            if ob.type == 'CAMERA' and ob is not cam:
                ob.hide_render = True
        cam.hide_render = False
        vl.objects.active = cam
        scene.camera = cam
        bpy.context.view_layer.update()
        print("REC08_SHOT", tag,
              scene.camera.name if scene.camera else None,
              tuple(round(v, 3) for v in cam.matrix_world.translation))
        scene.render.filepath = os.path.join(DOCS, "fm_rec08_queue_" + tag + ".png")
        bpy.ops.render.render(write_still=True)
        print("RENDERED", scene.render.filepath)

    for ob in bpy.data.objects:
        st = saved.get(ob.name)
        if st:
            ob.hide_render = st[0]
            ob.hide_viewport = st[1]
            ob.hide_set(st[2])
    for ob in list(col.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.collections.remove(col)
    scene.render.engine = old["engine"]
    scene.render.resolution_x = old["res_x"]
    scene.render.resolution_y = old["res_y"]
    scene.cycles.samples = old["samples"]
    scene.cycles.use_denoising = old["denoise"]
    scene.view_settings.exposure = old["exposure"]
    scene.view_settings.view_transform = old["view"]
    scene.view_settings.look = old["look"]
    if scene.world and old["world"]:
        scene.world.color = old["world"]
    print("REC08_RENDER_DONE")


main()
