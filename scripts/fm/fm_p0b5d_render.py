"""FRECUENCIA MUERTA - P0b.5d review renders.

Shots:
  conduit        east wall conduit, junction boxes and door span
  heads_wide     main line + north branch heads
  heads_close    branch head at (45,10), drop + deflector
  riser_tags     riser B valve tags and handwheels
  riser_sleeves  slab sleeves/firestop (ceiling tiles hidden for inspection)

Run: python3 /tmp/opencode/bpy_run.py scripts/fm/fm_p0b5d_render.py
"""
import bpy
import os
from mathutils import Matrix, Vector

ROOT = "/home/riyo/Documentos/game"
DOCS = os.path.join(ROOT, "docs")
RIG = "P0B5D_RENDER_RIG"


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
    area(col, "P0B5D_EAST", (59.5, 12.5, 2.5), 220, 3.0,
         (0.75, 0.85, 1.0), (61.78, 18.0, 3.15))
    area(col, "P0B5D_SOUTH", (43.5, 11.5, 2.2), 260, 3.0,
         (1.0, 0.82, 0.66), (45.0, 10.0, 3.4))

    shots = [
        ("conduit", (58.5, 12.8, 2.35), (61.78, 18.0, 3.15), 40, False),
        ("heads_wide", (50.5, 25.5, 1.7), (50.0, 17.0, 3.55), 24, False),
        ("heads_close", (43.0, 12.8, 2.30), (45.0, 10.0, 3.45), 50, False),
        ("riser_tags", (52.2, 22.3, 1.55), (55.73, 23.95, 1.55), 40, False),
        ("riser_sleeves", (53.4, 22.0, 3.65), (55.73, 23.9, 4.02), 45, True),
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
    print("P0B5D_RENDER_DONE")


main()
