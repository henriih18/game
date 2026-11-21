import bpy
import math
import os
import sys
from mathutils import Vector, Matrix

ROOT = "/home/riyo/Documentos/game"
DOCS = os.path.join(ROOT, "docs")
RIG = "REC07_RENDER_RIG"

INCLUDE = [
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
    scene.view_settings.exposure = 0.42
    if scene.world:
        scene.world.color = (0.012, 0.014, 0.018)

    col = bpy.data.collections.new(RIG)
    scene.collection.children.link(col)
    area(col, "REC07_KEY", (-81.8, -8.6, 2.9), (-84.0, -10.8, 1.0),
         360.0, 4.0, (1.0, 0.92, 0.80))
    area(col, "REC07_FILL", (-86.2, -11.6, 2.2), (-84.0, -10.8, 0.9),
         140.0, 3.5, (0.72, 0.84, 1.0))
    area(col, "REC07_RIM", (-83.5, -13.4, 2.7), (-84.0, -10.8, 1.1),
         300.0, 3.0, (1.0, 0.88, 0.72))
    area(col, "REC07_WKFILL", (-81.8, -11.4, 2.3), (-83.4, -10.8, 1.1),
         90.0, 2.0, (1.0, 0.93, 0.84))

    shots = [
        ("front", (-84.0, -8.55, 2.0), (-84.0, -10.85, 0.98), 26),
        ("threequarter", (-81.5, -8.8, 1.85), (-84.0, -10.8, 1.0), 28),
        ("workstation", (-80.4, -11.9, 1.9), (-83.4, -10.75, 1.18), 42),
        ("detail", (-82.35, -9.35, 1.55), (-83.55, -10.8, 1.05), 50),
        ("plaque", (-84.0, -9.0, 1.35), (-84.0, -10.47, 0.62), 60),
    ]
    for tag, loc, target, lens in shots:
        cam = camera(col, "REC07_CAM_" + tag, loc, target, lens)
        for ob in bpy.data.objects:
            if ob.type == 'CAMERA' and ob is not cam:
                ob.hide_render = True
        cam.hide_render = False
        vl.objects.active = cam
        scene.camera = cam

        # La cola R2 sigue siendo blockout y tapa el frente del desk; se oculta
        # solo en la toma frontal, no en la escena.
        for ob in bpy.data.objects:
            if ob.name.startswith(("PROP_REC02_Belt", "PROP_REC02_Stanchion",
                                   "PROP_REC02_Barrier")):
                st = saved.get(ob.name)
                if st:
                    ob.hide_render = st[0] or (tag == "front")

        bpy.context.view_layer.update()
        print("REC07_SHOT", tag,
              scene.camera.name if scene.camera else None,
              tuple(round(v, 3) for v in cam.matrix_world.translation),
              cam.name in vl.objects)
        scene.render.filepath = os.path.join(DOCS, "fm_rec07_security_" + tag + ".png")
        bpy.ops.render.render(write_still=True)
        print("RENDERED", scene.render.filepath)

    for ob in bpy.data.objects:
        if ob.name.startswith("REC07_CAM_") or ob.name.startswith("REC07_KEY") or \
           ob.name.startswith("REC07_FILL") or ob.name.startswith("REC07_RIM") or \
           ob.name.startswith("REC07_WKFILL"):
            bpy.data.objects.remove(ob, do_unlink=True)
    if RIG in bpy.data.collections:
        bpy.data.collections.remove(bpy.data.collections[RIG])
    for name, st in saved.items():
        ob = bpy.data.objects.get(name)
        if ob:
            ob.hide_render = st[0]
            ob.hide_viewport = st[1]
            ob.hide_set(st[2])
    scene.render.engine = old["engine"]
    scene.render.resolution_x = old["res_x"]
    scene.render.resolution_y = old["res_y"]
    scene.cycles.samples = old["samples"]
    scene.cycles.use_denoising = old["denoise"]
    scene.view_settings.exposure = old["exposure"]
    scene.view_settings.view_transform = old["view"]
    scene.view_settings.look = old["look"]
    if scene.world and old["world"] is not None:
        scene.world.color = old["world"]
    print("REC07_RENDER_DONE")


main()
