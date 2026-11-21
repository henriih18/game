"""Final EEVEE review renders for the R21D pass.

Temporary cameras and the implied flashlight are created in TMP_R21D_FINAL
and removed after the batch.  The saved .blend keeps only the final practical
lighting: four red emergency pools, monitor glow, one cold exit light and the
electrical spark.  No general light is used.
"""
import bpy
import math
import os
from mathutils import Vector

OUT = "/home/riyo/Documentos/game/docs"


def _collection():
    c = bpy.data.collections.get("TMP_R21D_FINAL")
    if c is None:
        c = bpy.data.collections.new("TMP_R21D_FINAL")
        bpy.context.scene.collection.children.link(c)
    for o in list(c.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    return c


def _clear(c):
    for o in list(c.objects):
        bpy.data.objects.remove(o, do_unlink=True)


def camera(c, name, loc, target, lens):
    d = bpy.data.cameras.new(name)
    d.lens = lens
    o = bpy.data.objects.new(name, d)
    o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    c.objects.link(o)
    return o


def area(c, name, loc, target, energy, size, color=(1.0, 0.92, 0.80)):
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


def spot(c, name, loc, target, energy, cone, color=(1.0, 0.92, 0.80)):
    d = bpy.data.lights.new(name, "SPOT")
    d.energy = energy
    d.spot_size = math.radians(cone)
    d.spot_blend = 0.9
    d.color = color
    o = bpy.data.objects.new(name, d)
    o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    c.objects.link(o)
    return o


def render(path, cam, exposure=0.80):
    s = bpy.context.scene
    s.camera = cam
    s.view_settings.view_transform = "AgX"
    try:
        s.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        pass
    s.view_settings.exposure = exposure
    s.render.engine = "BLENDER_EEVEE"
    s.eevee.taa_render_samples = 64
    s.eevee.use_raytracing = True
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
    old_rt = s.eevee.use_raytracing
    c = _collection()
    try:
        # 1. wide: checkpoint, damaged cabinet, ops centre
        _clear(c)
        loc = (-84.5, 11.0, 2.6)
        tgt = (-94.0, 23.0, 1.75)
        area(c, "W_AREA", loc, tgt, 45, 1.5)
        spot(c, "W_SPOT", loc, tgt, 560, 66)
        cam = camera(c, "W_CAM", loc, tgt, 16)
        render(os.path.join(OUT, "fm_security_r21d_wide.png"), cam, 0.82)

        # 2. north wide: ops, collapsed ceiling, planter and checkpoint reader
        _clear(c)
        loc = (-84.0, 11.0, 2.3)
        tgt = (-86.0, 27.0, 1.55)
        area(c, "N_AREA", loc, tgt, 40, 1.4)
        spot(c, "N_SPOT", loc, tgt, 480, 66)
        cam = camera(c, "N_CAM", loc, tgt, 20)
        render(os.path.join(OUT, "fm_security_r21d_wide_north.png"), cam, 0.82)

        # 3. checkpoint close: sign, counter, reader, red emergency and debris
        _clear(c)
        loc = (-85.2, 10.7, 2.3)
        tgt = (-89.5, 13.2, 1.0)
        area(c, "C_AREA", loc, tgt, 28, 1.4)
        spot(c, "C_SPOT", loc, tgt, 290, 62)
        cam = camera(c, "C_CAM", loc, tgt, 20)
        render(os.path.join(OUT, "fm_security_r21d_checkpoint.png"), cam, 0.86)

        # 4. operations centre: CCTV wall, workstations, monitor glow
        _clear(c)
        loc = (-91.5, 27.3, 1.72)
        tgt = (-84.5, 31.2, 1.15)
        area(c, "O_AREA", loc, tgt, 32, 1.4)
        spot(c, "O_SPOT", loc, tgt, 320, 62)
        cam = camera(c, "O_CAM", loc, tgt, 24)
        render(os.path.join(OUT, "fm_security_r21d_ops.png"), cam, 0.84)

        # 5. chaos: damaged electrical cabinet, sparks, fallen ceiling and debris
        _clear(c)
        loc = (-91.0, 15.0, 2.0)
        tgt = (-84.0, 19.0, 0.95)
        area(c, "K_AREA", loc, tgt, 50, 1.4)
        spot(c, "K_SPOT", loc, tgt, 560, 68)
        cam = camera(c, "K_CAM", loc, tgt, 24)
        render(os.path.join(OUT, "fm_security_r21d_chaos.png"), cam, 0.88)

        # 6. extra: electrical box close-up for documentation
        _clear(c)
        loc = (-89.8, 14.2, 1.72)
        tgt = (-84.7, 18.8, 1.0)
        area(c, "E_AREA", loc, tgt, 42, 1.3)
        spot(c, "E_SPOT", loc, tgt, 470, 62)
        cam = camera(c, "E_CAM", loc, tgt, 26)
        render(os.path.join(OUT, "fm_security_r21d_electrical.png"), cam, 0.86)

    finally:
        _clear(c)
        bpy.data.collections.remove(c)
        s.camera = old_cam
        s.view_settings.exposure = old_exp
        s.eevee.use_raytracing = old_rt
        print("R21D_RENDERS_DONE")


if __name__ == "__main__":
    render_all()
