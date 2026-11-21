import bpy
import os
from mathutils import Matrix, Vector

ROOT = "/home/riyo/Documentos/game"
DOCS = os.path.join(ROOT, "docs")
RIG = "SEC_P0A_TRAY_RENDER_RIG"


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
    scene.view_settings.exposure = 0.72

    visible_before = {ob.name: (ob.hide_render, ob.hide_viewport, ob.hide_get()) for ob in scene.objects}
    for ob in scene.objects:
        ob.hide_render = True

    def show(prefix):
        for col in bpy.data.collections:
            if col.name.startswith(prefix) and "RETIRED" not in col.name:
                for ob in col.all_objects:
                    if ob is not None and ob.name in scene.objects:
                        ob.hide_render = False

    for p in ("L1_SECURITY_R1", "L1_SECURITY_R2_HERO", "L1_SECURITY_R21A_HERO",
              "L1_SECURITY_R21B", "L1_SECURITY_R21C", "L1_SECURITY_R21D",
              "L1_SECURITY_P0A_HERO", "L1_ARCH_SURFACE", "L1_ARCH_CEILINGS",
              "L1_ARCH_COLUMNS", "L1_ARCH_ZONES", "L1_ARCH_CIRCULATION"):
        show(p)

    col = bpy.data.collections.new(RIG)
    scene.collection.children.link(col)

    area(col, "TRAY_KEY", (-74, 12, 3.2), 1100, 6.0, (1.0, 0.84, 0.68), (-90, 22, 2.4))
    area(col, "TRAY_FILL", (-98, 18, 2.8), 520, 5.0, (0.62, 0.76, 1.0), (-90, 22, 2.4))
    area(col, "TRAY_RIM", (-88, 34, 4.4), 700, 5.0, (0.85, 0.92, 1.0), (-90, 22, 3.0))
    area(col, "TRAY_WEST_FILL", (-101.5, 22, 3.0), 260, 3.0, (0.78, 0.84, 1.0), (-104.7, 22, 3.5))
    area(col, "TRAY_CENTRE_FILL", (-87.5, 18.5, 3.3), 260, 3.0, (1.0, 0.82, 0.62), (-84.55, 18.6, 4.3))

    shots = [
        ("wide", (-73.5, 12.5, 2.2), (-92.0, 23.0, 2.7), 21),
        ("west", (-100.5, 17.0, 2.1), (-104.7, 22.0, 3.55), 40),
        ("centre", (-88.0, 16.8, 2.4), (-84.55, 18.8, 4.30), 40),
        ("detail", (-103.2, 24.0, 2.8), (-104.7, 22.0, 3.55), 55),
    ]
    for tag, loc, target, lens in shots:
        cam = camera(col, "SEC_TRAY_CAM_" + tag, loc, target, lens)
        scene.camera = cam
        bpy.context.view_layer.update()
        scene.render.filepath = os.path.join(DOCS, "fm_security_p0a_tray_" + tag + ".png")
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
    scene.view_settings.exposure = old_exp
    print("SEC_P0A_TRAY_RENDER_DONE")


main()
