"""P0b.5d second review pass: conduit junction box close-up + riser sleeves.

Run: python3 /tmp/opencode/bpy_run.py scripts/fm/fm_p0b5d_render2.py
"""
import bpy
import os
from mathutils import Matrix, Vector

ROOT = "/home/riyo/Documentos/game"
DOCS = os.path.join(ROOT, "docs")
RIG = "P0B5D_RENDER2_RIG"


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

    visible_before = {ob.name: (ob.hide_render, ob.hide_viewport, ob.hide_get())
                      for ob in scene.objects}
    cam_state = {ob.name: ob.hide_render
                 for ob in scene.objects if ob.type == 'CAMERA'}
    for ob in scene.objects:
        ob.hide_render = True

    def show(prefix):
        for col in bpy.data.collections:
            if col.name.startswith(prefix) and "RETIRED" not in col.name:
                for ob in col.all_objects:
                    if ob is not None and ob.name in scene.objects:
                        ob.hide_render = False

    for p in ("L1_P0B5D_Z10", "L1_P0B5_Z10", "L1_P0B4_Z10",
              "L1_PROPS_Z10", "L1_KIT_PILOT"):
        show(p)

    ceiling = [ob for ob in scene.objects
               if ob.type == 'MESH' and "ceiling" in ob.name.lower()]

    col = bpy.data.collections.new(RIG)
    scene.collection.children.link(col)
    area(col, "P0B5D_KEY", (51.0, 17.0, 3.4), 700, 4.5,
         (1.0, 0.86, 0.70), (55.0, 21.0, 3.6))
    area(col, "P0B5D_FILL", (58.0, 25.0, 2.6), 300, 3.5,
         (0.62, 0.76, 1.0), (55.7, 22.0, 3.6))
    area(col, "P0B5D_RIM", (50.0, 25.0, 4.2), 420, 3.0,
         (0.85, 0.92, 1.0), (54.0, 21.0, 3.8))
    area(col, "P0B5D_JB", (59.6, 27.0, 2.75), 180, 2.0,
         (0.80, 0.88, 1.0), (61.78, 28.0, 3.15))
    area(col, "P0B5D_TOP", (54.4, 26.0, 4.0), 180, 2.0,
         (0.85, 0.90, 1.0), (55.73, 23.9, 4.0))

    shots = [
        ("conduit_jb", (59.8, 26.4, 2.55), (61.78, 28.0, 3.15), 55, False),
        ("riser_sleeves2", (53.6, 26.2, 3.55), (55.73, 23.9, 4.00), 45, True),
    ]
    for tag, loc, target, lens, hide_ceiling in shots:
        for ob in ceiling:
            ob.hide_render = hide_ceiling
        cam = camera(col, "P0B5D_CAM_" + tag, loc, target, lens)
        for c in scene.objects:
            if c.type == 'CAMERA':
                c.hide_render = c is not cam
        scene.camera = cam
        bpy.context.view_layer.update()
        scene.render.filepath = os.path.join(DOCS, "fm_p0b5d_" + tag + ".png")
        bpy.ops.render.render(write_still=True)
        print("RENDERED", scene.render.filepath)

    for ob in ceiling:
        ob.hide_render = visible_before.get(ob.name, (True, True, True))[0]
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
    print("P0B5D_RENDER2_DONE")


main()
