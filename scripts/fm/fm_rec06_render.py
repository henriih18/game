"""Render the REC06 reception desk hero from three angles."""

import bpy
import os

DOCS = "/home/riyo/Documentos/game/docs"
RIG = "REC06_RENDER_RIG"

INCLUDE = [
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
EXCLUDE_PREFIX = ("PROP_REC02_Desk_", "PROP_REC02_Credenza",
                  "PROP_REC02_Monitor_Credenza", "PROP_REC02_Monitor_Desk",
                  "PROP_REC02_Chair_Desk", "PROP_REC02_Keyboard",
                  "PROP_REC02_CPU")


def clear_rig():
    col = bpy.data.collections.get(RIG)
    if col:
        for ob in list(col.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.collections.remove(col)


def area(col, name, loc, target, energy, size, color=(1, 0.93, 0.82)):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = energy
    data.shape = 'DISK'
    data.size = size
    data.color = color
    ob = bpy.data.objects.new(name, data)
    col.objects.link(ob)
    ob.location = loc
    direction = (target[0] - loc[0], target[1] - loc[1], target[2] - loc[2])
    from mathutils import Vector
    ob.rotation_euler = Vector(direction).to_track_quat('-Z', 'Y').to_euler()
    return ob


def camera(col, name, loc, target, lens):
    data = bpy.data.cameras.new(name)
    data.lens = lens
    ob = bpy.data.objects.new(name, data)
    col.objects.link(ob)
    ob.location = loc
    from mathutils import Vector, Matrix
    forward = Vector((target[0] - loc[0], target[1] - loc[1],
                      target[2] - loc[2])).normalized()
    world_up = Vector((0.0, 0.0, 1.0))
    right = forward.cross(world_up)
    if right.length < 1e-5:
        right = Vector((1.0, 0.0, 0.0))
    right.normalize()
    up = right.cross(forward).normalized()
    rot = Matrix((right, up, -forward)).transposed()
    ob.rotation_euler = rot.to_euler()
    return ob


def main():
    scene = bpy.context.scene
    saved = {}
    for ob in bpy.data.objects:
        saved[ob.name] = (ob.hide_render, ob.hide_viewport, ob.hide_get())
        ob.hide_render = True

    for name in INCLUDE:
        col = bpy.data.collections.get(name)
        if not col:
            continue
        for ob in col.all_objects:
            if any(ob.name.startswith(p) for p in EXCLUDE_PREFIX):
                continue
            ob.hide_render = False

    old_engine = scene.render.engine
    old_res = (scene.render.resolution_x, scene.render.resolution_y)
    old_samples = scene.cycles.samples
    old_exposure = scene.view_settings.exposure
    old_view = scene.view_settings.view_transform
    old_look = scene.view_settings.look
    old_world = scene.world.color[:] if scene.world else None

    try:
        scene.render.engine = 'CYCLES'
    except Exception:
        pass
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.cycles.samples = 96
    scene.cycles.use_denoising = True
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = 0.38
    if scene.world:
        scene.world.color = (0.012, 0.014, 0.018)

    col = bpy.data.collections.new(RIG)
    scene.collection.children.link(col)
    area(col, "REC06_KEY", (-104.2, -10.0, 3.05), (-102.0, -13.2, 1.0),
         420.0, 5.0, (1.0, 0.92, 0.80))
    area(col, "REC06_FILL", (-98.4, -10.4, 2.35), (-102.0, -13.2, 1.0),
         180.0, 3.5, (0.72, 0.84, 1.0))
    area(col, "REC06_RIM", (-102.0, -16.6, 2.9), (-102.0, -13.8, 1.15),
         420.0, 3.0, (1.0, 0.88, 0.72))
    area(col, "REC06_WKFILL", (-101.0, -14.1, 2.4), (-102.0, -13.85, 1.0),
         90.0, 2.0, (1.0, 0.93, 0.84))

    shots = [
        ("front", (-102.0, -9.0, 2.05), (-102.0, -13.20, 0.92), 24),
        ("threequarter", (-98.35, -10.15, 1.62), (-102.0, -13.55, 0.98), 30),
        ("detail", (-100.9, -11.1, 1.55), (-102.4, -13.45, 1.12), 50),
        ("staff", (-97.6, -17.6, 2.05), (-102.0, -13.55, 0.95), 28),
        ("workstation", (-99.2, -14.05, 1.55), (-102.0, -13.85, 0.85), 50),
    ]
    for tag, loc, target, lens in shots:
        cam = camera(col, "REC06_CAM_" + tag, loc, target, lens)
        for ob in bpy.data.objects:
            if ob.type == 'CAMERA' and ob is not cam:
                ob.hide_render = True
        cam.hide_render = False
        bpy.context.view_layer.objects.active = cam
        scene.camera = cam
        bpy.context.view_layer.update()
        print("REC06_SHOT", tag,
              scene.camera.name if scene.camera else None,
              tuple(round(v, 3) for v in cam.matrix_world.translation),
              cam.name in bpy.context.view_layer.objects)
        scene.render.filepath = os.path.join(DOCS, "fm_rec06_desk_" + tag + ".png")
        bpy.ops.render.render(write_still=True)
        print("RENDERED", scene.render.filepath)

    bpy.context.view_layer.update()
    print("REC06_RENDER_DONE")
    clear_rig()

    for name, (hr, hv, hs) in saved.items():
        ob = bpy.data.objects.get(name)
        if ob:
            ob.hide_render = hr
            ob.hide_viewport = hv
            ob.hide_set(hs)

    scene.render.engine = old_engine
    scene.render.resolution_x, scene.render.resolution_y = old_res
    scene.cycles.samples = old_samples
    scene.view_settings.exposure = old_exposure
    scene.view_settings.view_transform = old_view
    scene.view_settings.look = old_look
    if scene.world and old_world is not None:
        scene.world.color = old_world


main()
