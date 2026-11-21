"""Final review renders for L1_SECURITY_R21C_HERO.

Creates temporary cameras and practical review lights, renders 1280x720
EEVEE stills into docs/, then removes every temporary object.  The saved
.blend never contains the review lights or cameras.
"""
import bpy
import math
import os
from mathutils import Vector

OUT = "/home/riyo/Documentos/game/docs"


def _collection():
    c = bpy.data.collections.get("TMP_R21C_REVIEW")
    if c is None:
        c = bpy.data.collections.new("TMP_R21C_REVIEW")
        bpy.context.scene.collection.children.link(c)
    for o in list(c.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    return c


def _clear(c):
    for o in list(c.objects):
        bpy.data.objects.remove(o, do_unlink=True)


def area(c, name, loc, target, energy, size, color):
    d = bpy.data.lights.new(name, "AREA")
    d.energy = energy
    d.shape = "DISK"
    d.size = size
    d.color = color
    o = bpy.data.objects.new(name, d)
    o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    c.objects.link(o)
    return o


def spot(c, name, loc, target, energy, cone, color, blend=0.5):
    d = bpy.data.lights.new(name, "SPOT")
    d.energy = energy
    d.spot_size = math.radians(cone)
    d.spot_blend = blend
    d.color = color
    o = bpy.data.objects.new(name, d)
    o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    c.objects.link(o)
    return o


def point(c, name, loc, energy, color, radius=0.3):
    d = bpy.data.lights.new(name, "POINT")
    d.energy = energy
    d.color = color
    d.shadow_soft_size = radius
    o = bpy.data.objects.new(name, d)
    o.location = loc
    c.objects.link(o)
    return o


def camera(c, name, loc, target, lens, fstop=None, focus=None):
    d = bpy.data.cameras.new(name)
    d.lens = lens
    if fstop is not None:
        d.dof.use_dof = True
        d.dof.aperture_fstop = fstop
        d.dof.focus_distance = focus if focus is not None else (Vector(target) - Vector(loc)).length
    o = bpy.data.objects.new(name, d)
    o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    c.objects.link(o)
    return o


def render(path, cam, exposure):
    s = bpy.context.scene
    s.camera = cam
    s.view_settings.exposure = exposure
    s.render.engine = "BLENDER_EEVEE"
    s.eevee.taa_render_samples = 64
    s.render.resolution_x = 1280
    s.render.resolution_y = 720
    s.render.resolution_percentage = 100
    s.render.image_settings.file_format = "PNG"
    s.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("RENDERED", path)


def render_all():
    os.makedirs(OUT, exist_ok=True)
    s = bpy.context.scene
    old_cam = s.camera
    old_exp = s.view_settings.exposure
    c = _collection()
    try:
        # 1. wide of the room, ceiling visible, dark pilot grade
        _clear(c)
        area(c, "W_FILL", (-99.0, 15.5, 3.4), (-81.0, 24.0, 1.0), 520, 6.0, (1.0, 0.86, 0.68))
        area(c, "W_EAST", (-73.6, 18.0, 3.0), (-71.5, 16.8, 1.1), 650, 2.4, (0.60, 0.80, 1.0))
        area(c, "W_OPS", (-86.0, 29.5, 3.9), (-85.0, 32.0, 0.8), 480, 3.2, (0.55, 0.86, 0.82))
        area(c, "W_BRIEF", (-99.0, 21.0, 3.5), (-96.0, 20.0, 0.7), 260, 2.4, (1.0, 0.82, 0.62))
        area(c, "W_CART", (-82.0, 20.0, 2.7), (-80.4, 21.6, 0.7), 220, 1.8, (1.0, 0.90, 0.78))
        spot(c, "W_FLASH", (-99.5, 14.5, 2.8), (-79.0, 22.5, 0.6), 5200, 46,
             (1.0, 0.90, 0.76), 0.55)
        point(c, "W_CEIL_A", (-88.0, 22.0, 4.20), 160, (1.0, 0.74, 0.50), 0.5)
        point(c, "W_CEIL_B", (-78.0, 23.0, 4.20), 90, (0.62, 0.78, 1.0), 0.5)
        for i, (x, y) in enumerate(((-104.5, 14.6), (-104.5, 27.6),
                                    (-94.6, 10.4), (-71.2, 23.0))):
            point(c, f"W_RED{i}", (x, y, 3.05), 30, (1.0, 0.04, 0.015), 0.28)
        point(c, "W_GLOW_A", (-89.5, 30.0, 1.45), 22, (0.25, 0.75, 0.65), 0.5)
        point(c, "W_GLOW_B", (-85.5, 30.0, 1.45), 16, (0.22, 0.65, 0.60), 0.5)
        cam = camera(c, "W_CAM", (-103.4, 12.4, 3.4), (-79.0, 25.5, 1.9), 16)
        render(os.path.join(OUT, "fm_security_r21c_wide.png"), cam, -0.05)

        # 2. east wall: hatch, locker bank A, key rack and shelving
        _clear(c)
        area(c, "E_KEY_A", (-74.3, 11.8, 2.5), (-71.4, 11.3, 1.2), 560, 2.6, (1.0, 0.90, 0.80))
        area(c, "E_KEY_B", (-74.3, 17.8, 2.5), (-71.4, 17.5, 1.2), 560, 2.6, (1.0, 0.90, 0.80))
        area(c, "E_FILL", (-75.0, 15.2, 3.5), (-71.5, 15.2, 1.0), 260, 3.2, (0.62, 0.78, 1.0))
        area(c, "E_TOP", (-72.8, 15.2, 4.0), (-71.5, 15.2, 1.2), 120, 2.4, (1.0, 0.94, 0.88))
        point(c, "E_RED", (-71.2, 22.8, 2.9), 28, (1.0, 0.04, 0.015), 0.3)
        point(c, "E_HATCH", (-72.3, 11.0, 1.4), 24, (1.0, 0.62, 0.40), 0.4)
        cam = camera(c, "E_CAM", (-77.0, 14.7, 1.78), (-71.2, 15.8, 1.45), 15, fstop=8.0)
        render(os.path.join(OUT, "fm_security_r21c_east.png"), cam, -0.15)

        # 3. locker bank A hero close-up
        _clear(c)
        area(c, "L_KEY", (-74.6, 17.8, 2.3), (-71.9, 15.8, 1.15), 480, 2.4, (1.0, 0.90, 0.80))
        area(c, "L_FILL", (-73.0, 13.6, 1.5), (-71.7, 15.6, 1.0), 120, 1.8, (0.60, 0.76, 1.0))
        area(c, "L_RIM", (-70.4, 16.8, 2.4), (-71.9, 15.8, 1.4), 240, 1.4, (0.55, 0.85, 0.85))
        area(c, "L_TOP", (-73.5, 15.6, 3.8), (-71.8, 15.6, 1.2), 90, 3.0, (1.0, 0.92, 0.82))
        point(c, "L_INSIDE_A", (-71.92, 15.58, 1.48), 45, (1.0, 0.64, 0.40), 0.24)
        point(c, "L_INSIDE_B", (-71.92, 16.55, 1.20), 26, (1.0, 0.60, 0.36), 0.22)
        cam = camera(c, "L_CAM", (-75.15, 18.45, 1.62), (-71.55, 15.55, 1.22), 26, fstop=4.0)
        render(os.path.join(OUT, "fm_security_r21c_lockers.png"), cam, -0.18)

        # 4. service hatch close-up
        _clear(c)
        area(c, "H_KEY", (-74.4, 11.0, 2.0), (-71.4, 11.0, 1.35), 420, 2.0, (1.0, 0.93, 0.84))
        area(c, "H_TOP", (-72.4, 10.9, 3.0), (-71.5, 10.9, 1.1), 240, 2.2, (1.0, 0.95, 0.88))
        area(c, "H_FILL", (-73.8, 9.9, 1.4), (-71.4, 11.0, 1.2), 110, 1.4, (0.60, 0.76, 1.0))
        area(c, "H_RIM", (-70.8, 12.0, 2.4), (-71.5, 11.0, 1.6), 180, 1.2, (0.55, 0.85, 0.85))
        cam = camera(c, "H_CAM", (-74.85, 11.28, 1.62), (-71.35, 11.0, 1.42), 28, fstop=4.0)
        render(os.path.join(OUT, "fm_security_r21c_hatch.png"), cam, -0.15)

        # 5. tool cart
        _clear(c)
        area(c, "C_KEY", (-82.4, 20.0, 2.0), (-80.6, 21.7, 0.55), 380, 1.8, (1.0, 0.92, 0.82))
        area(c, "C_FILL", (-81.6, 22.9, 1.3), (-80.6, 21.8, 0.6), 120, 1.4, (0.60, 0.78, 1.0))
        area(c, "C_RIM", (-79.3, 20.8, 1.6), (-80.5, 21.7, 0.8), 200, 1.2, (0.55, 0.85, 0.85))
        area(c, "C_TOP", (-81.0, 21.5, 3.0), (-80.6, 21.7, 0.5), 80, 2.0, (1.0, 0.95, 0.9))
        point(c, "C_UNDER", (-80.65, 21.75, 0.25), 15, (1.0, 0.7, 0.4), 0.3)
        cam = camera(c, "C_CAM", (-82.10, 20.35, 1.50), (-80.55, 21.78, 0.62), 35, fstop=2.8)
        render(os.path.join(OUT, "fm_security_r21c_cart.png"), cam, -0.10)

        # 6. operations-centre chaos
        _clear(c)
        area(c, "O_KEY", (-90.8, 27.8, 2.3), (-86.6, 28.7, 0.7), 450, 2.4, (1.0, 0.90, 0.80))
        area(c, "O_FILL", (-87.2, 26.6, 1.5), (-86.0, 28.4, 0.7), 120, 1.8, (0.60, 0.78, 1.0))
        area(c, "O_RIM", (-83.0, 29.8, 2.7), (-85.8, 28.6, 1.1), 260, 1.6, (0.55, 0.86, 0.86))
        area(c, "O_TOP", (-85.2, 28.6, 3.7), (-85.2, 28.6, 0.6), 180, 2.4, (1.0, 0.94, 0.86))
        spot(c, "O_SCREEN", (-85.3, 28.2, 3.0), (-85.3, 28.7, 0.4), 300, 30,
             (0.65, 0.9, 1.0), 0.4)
        point(c, "O_GLOW", (-85.4, 29.9, 1.35), 34, (0.22, 0.70, 0.62), 0.4)
        point(c, "O_RED", (-88.0, 31.0, 2.6), 12, (1.0, 0.05, 0.02), 0.2)
        cam = camera(c, "O_CAM", (-88.80, 27.30, 1.75), (-85.50, 28.70, 0.65), 30, fstop=2.8)
        render(os.path.join(OUT, "fm_security_r21c_ops_chaos.png"), cam, -0.12)

        # 7. key rack + shelving
        _clear(c)
        area(c, "S_KEY", (-74.5, 20.5, 2.4), (-71.5, 20.8, 1.4), 460, 2.2, (1.0, 0.92, 0.82))
        area(c, "S_FILL", (-75.0, 22.8, 1.6), (-71.5, 22.8, 1.2), 150, 2.0, (0.62, 0.78, 1.0))
        area(c, "S_TOP", (-73.0, 22.0, 3.7), (-71.5, 22.0, 1.2), 120, 2.4, (1.0, 0.94, 0.88))
        cam = camera(c, "S_CAM", (-74.8, 22.15, 1.58), (-71.38, 22.15, 1.42), 26, fstop=4.0)
        render(os.path.join(OUT, "fm_security_r21c_storage.png"), cam, -0.15)
    finally:
        _clear(c)
        bpy.data.collections.remove(c)
        s.camera = old_cam
        s.view_settings.exposure = old_exp
        print("R21C_RENDERS_DONE")


if __name__ == "__main__":
    render_all()
