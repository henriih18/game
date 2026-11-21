"""P0b.6 diagnostic renders: wayfinding line, CCTV tray link, security services.

Read-only for geometry: adds temporary cameras/lights, renders 3 PNGs, restores
settings. Does not save the .blend.

Run: python3 /tmp/opencode/bpy_run.py scripts/fm/fm_p0b6_render.py
"""
import bpy
import json
import os
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
SCENE = bpy.data.scenes["NEXUS_L1_V06_ARCH"]
OUT = os.path.join(ROOT, "docs")

old = {
    "engine": SCENE.render.engine,
    "samples": SCENE.cycles.samples,
    "denoise": SCENE.cycles.use_denoising,
    "rx": SCENE.render.resolution_x,
    "ry": SCENE.render.resolution_y,
    "pct": SCENE.render.resolution_percentage,
    "fmt": SCENE.render.image_settings.file_format,
    "filepath": SCENE.render.filepath,
    "vt": SCENE.view_settings.view_transform,
    "look": SCENE.view_settings.look,
    "exposure": SCENE.view_settings.exposure,
}

SCENE.render.engine = "CYCLES"
SCENE.cycles.samples = 48
SCENE.cycles.use_denoising = True
SCENE.render.resolution_x = 1280
SCENE.render.resolution_y = 720
SCENE.render.resolution_percentage = 100
SCENE.render.image_settings.file_format = "PNG"
SCENE.view_settings.view_transform = "AgX"
try:
    SCENE.view_settings.look = "AgX - Medium High Contrast"
except TypeError:
    pass
SCENE.view_settings.exposure = 0.62


def aim(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def area(name, loc, target, energy, size):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.size = size
    ob = bpy.data.objects.new(name, data)
    SCENE.collection.objects.link(ob)
    ob.location = loc
    aim(ob, target)
    ob.visible_camera = False
    return ob


def camera(name, loc, target, lens):
    data = bpy.data.cameras.new(name)
    data.lens = lens
    data.sensor_width = 36
    ob = bpy.data.objects.new(name, data)
    SCENE.collection.objects.link(ob)
    ob.location = loc
    aim(ob, target)
    SCENE.camera = ob
    return ob


lights = [
    area("P0B6_REC_KEY", (-90, -28, 3.9), (-94, -33, 0.3), 900, 4.0),
    area("P0B6_REC_FILL", (-101, -30, 2.4), (-94, -33, 0.6), 420, 5.0),
    area("P0B6_SEC_KEY", (-82, 24, 4.25), (-88, 30, 4.0), 1000, 5.0),
    area("P0B6_SEC_FILL", (-100, 18, 2.6), (-90, 25, 3.5), 480, 6.0),
    area("P0B6_SEC_RIM", (-78, 33, 4.3), (-85, 35, 4.0), 560, 4.0),
]

shots = [
    ("fm_p0b6_reception_line.png", (-91.8, -26.0, 1.65),
     (-94.0, -35.2, 0.10), 35),
    ("fm_p0b6_cctv_link.png", (-79.5, 29.5, 2.0),
     (-86.2, 35.4, 4.15), 38),
    ("fm_p0b6_security_services.png", (-78.0, 14.0, 1.8),
     (-96.0, 26.0, 3.7), 24),
]

paths = []
for filename, loc, target, lens in shots:
    cam = camera("CAM_" + filename, loc, target, lens)
    SCENE.render.filepath = os.path.join(OUT, filename)
    bpy.ops.render.render(write_still=True)
    paths.append(SCENE.render.filepath)
    bpy.data.objects.remove(cam, do_unlink=True)

for ob in lights:
    bpy.data.objects.remove(ob, do_unlink=True)

SCENE.render.engine = old["engine"]
SCENE.cycles.samples = old["samples"]
SCENE.cycles.use_denoising = old["denoise"]
SCENE.render.resolution_x = old["rx"]
SCENE.render.resolution_y = old["ry"]
SCENE.render.resolution_percentage = old["pct"]
SCENE.render.image_settings.file_format = old["fmt"]
SCENE.render.filepath = old["filepath"]
SCENE.view_settings.view_transform = old["vt"]
SCENE.view_settings.look = old["look"]
SCENE.view_settings.exposure = old["exposure"]

print("P0B6_RENDER_DONE " + json.dumps(paths, separators=(",", ":")))
