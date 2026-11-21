import bpy
import os
from mathutils import Matrix, Vector

ROOT = "/home/riyo/Documentos/game"
DOCS = os.path.join(ROOT, "docs")
RIG = "SEC_P0A_PORTAL_RENDER_RIG"


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
    scene.view_settings.exposure = 0.70

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

    # South portal lighting (outside corridor + inside security).
    area(col, "SEC_P_KEY_S", (-89, 4.6, 3.4), 900, 5.0, (1.0, 0.84, 0.68), (-89, 10, 1.8))
    area(col, "SEC_P_FILL_S", (-96, 8.0, 2.5), 380, 4.0, (0.62, 0.76, 1.0), (-89, 10, 1.8))
    area(col, "SEC_P_RIM_S", (-81, 13.5, 3.6), 520, 4.0, (0.85, 0.92, 1.0), (-89, 10, 2.2))
    # North portal lighting.
    area(col, "SEC_P_KEY_N", (-94, 32.0, 3.4), 750, 4.5, (1.0, 0.86, 0.70), (-94, 36, 1.6))
    area(col, "SEC_P_FILL_N", (-99, 37.5, 2.5), 300, 3.5, (0.64, 0.78, 1.0), (-94, 36, 1.6))

    shots = [
        ("south_out", (-89.0, 5.2, 1.95), (-89.0, 10.0, 1.72), 24),
        ("south_in", (-80.0, 16.0, 2.25), (-89.0, 10.0, 1.75), 24),
        ("north_in", (-94.0, 31.5, 1.95), (-94.0, 36.0, 1.55), 26),
        ("detail_s", (-89.0, 5.2, 2.2), (-89.0, 10.0, 2.7), 50),
    ]
    for tag, loc, target, lens in shots:
        cam = camera(col, "SEC_P_CAM_" + tag, loc, target, lens)
        scene.camera = cam
        bpy.context.view_layer.update()
        scene.render.filepath = os.path.join(DOCS, "fm_security_p0a_portal_" + tag + ".png")
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
    print("SEC_P0A_PORTAL_RENDER_DONE")


main()
