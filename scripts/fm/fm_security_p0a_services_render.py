import bpy
import os
from mathutils import Matrix, Vector

ROOT = "/home/riyo/Documentos/game"
DOCS = os.path.join(ROOT, "docs")
RIG = "SEC_P0A_SERVICES_RENDER_RIG"


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

    area(col, "SEC_S_KEY", (-74, 12.0, 3.4), 1100, 6.0, (1.0, 0.84, 0.68), (-91, 23, 2.6))
    area(col, "SEC_S_FILL", (-102, 14.0, 2.6), 500, 5.0, (0.62, 0.76, 1.0), (-91, 23, 2.2))
    area(col, "SEC_S_RIM", (-86, 34.0, 4.2), 760, 5.0, (0.85, 0.92, 1.0), (-91, 18, 3.0))

    shots = [
        ("east", (-73.0, 11.5, 2.35), (-93.0, 24.0, 3.15), 19),
        ("north", (-73.5, 33.5, 2.45), (-93.0, 16.0, 2.75), 20),
    ]
    for tag, loc, target, lens in shots:
        cam = camera(col, "SEC_S_CAM_" + tag, loc, target, lens)
        scene.camera = cam
        bpy.context.view_layer.update()
        scene.render.filepath = os.path.join(DOCS, "fm_security_p0a_services_" + tag + ".png")
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
    print("SEC_P0A_SERVICES_RENDER_DONE")


main()
