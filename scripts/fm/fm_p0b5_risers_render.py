"""Review renders for P0b.5 risers (does not save the .blend)."""

import bpy
from mathutils import Vector

OUT = "/home/riyo/Documentos/game/docs/"
RIG = "P0B5_RENDER_RIG"


def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def area(name, loc, target, energy, size, color):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = energy
    data.shape = 'SQUARE'
    data.size = size
    data.color = color
    ob = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    look_at(ob, target)
    return ob


def camera(name, loc, target, lens):
    data = bpy.data.cameras.new(name)
    data.lens = lens
    ob = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    look_at(ob, target)
    return ob


def main():
    scene = bpy.context.scene
    saved = {
        "engine": scene.render.engine,
        "resx": scene.render.resolution_x,
        "resy": scene.render.resolution_y,
        "pct": scene.render.resolution_percentage,
        "samples": getattr(scene.cycles, "samples", 64),
        "exposure": scene.view_settings.exposure,
        "look": scene.view_settings.look,
        "filepath": scene.render.filepath,
    }
    saved_hide = {ob.name: ob.hide_render for ob in bpy.data.objects}

    for ob in bpy.data.objects:
        ob.hide_render = True
    for cname in ("L1_P0B5_Z10", "L1_PROPS_Z10", "L1_KIT_PILOT",
                  "L1_P0B4_Z10", "L1_Z10_ABANDON"):
        col = bpy.data.collections.get(cname)
        if col:
            for ob in col.all_objects:
                ob.hide_render = False
    for name in ("STUDIO_Z10_Key", "STUDIO_Z10_Fill", "STUDIO_Z10_Backdrop",
                 "STUDIO_Z10_Floor"):
        ob = bpy.data.objects.get(name)
        if ob:
            ob.hide_render = True

    scene.render.engine = 'CYCLES'
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    scene.view_settings.exposure = 0.45
    scene.view_settings.look = 'AgX - Medium High Contrast'

    area("P0B5_KEY", (43.6, 18.8, 3.3), (46.3, 16.0, 1.6),
         900.0, 2.6, (1.0, 0.88, 0.72))
    area("P0B5_FILL", (48.8, 17.4, 2.1), (46.3, 16.0, 1.6),
         380.0, 2.2, (0.70, 0.82, 1.0))
    area("P0B5_RIM", (45.6, 13.2, 3.8), (46.3, 16.0, 2.0),
         620.0, 2.0, (1.0, 0.94, 0.82))

    cam = camera("P0B5_CAM_CLOSE", (49.0, 16.4, 1.55),
                 (46.27, 16.0, 1.45), 50)
    close_key = area("P0B5_CKEY", (48.2, 15.0, 3.0), (46.3, 16.0, 1.5),
                     600.0, 2.0, (1.0, 0.90, 0.78))
    close_fill = area("P0B5_CFILL", (48.2, 17.4, 1.2), (46.3, 16.0, 1.5),
                      220.0, 1.8, (0.72, 0.84, 1.0))
    scene.camera = cam
    scene.render.filepath = OUT + "fm_p0b5_riser_close.png"
    bpy.ops.render.render(write_still=True)
    print("RENDERED", scene.render.filepath)
    close_key.hide_render = True
    close_fill.hide_render = True

    scene.view_settings.exposure = 0.70
    wide_key = area("P0B5_WKEY", (44.0, 13.0, 3.2), (50.0, 19.0, 1.6),
                    1400.0, 3.0, (1.0, 0.91, 0.80))
    wide_fill = area("P0B5_WFILL", (56.0, 16.0, 2.0), (52.0, 20.0, 1.6),
                     600.0, 2.5, (0.72, 0.84, 1.0))
    wide_rim = area("P0B5_WRIM", (52.0, 25.0, 4.0), (52.0, 20.0, 1.6),
                    900.0, 2.0, (1.0, 0.94, 0.82))
    cam.location = (42.5, 10.5, 2.7)
    look_at(cam, (51.0, 20.0, 1.6))
    cam.data.lens = 30
    scene.render.filepath = OUT + "fm_p0b5_risers_wide.png"
    bpy.ops.render.render(write_still=True)
    print("RENDERED", scene.render.filepath)

    rig_prefixes = ("P0B5_KEY", "P0B5_FILL", "P0B5_RIM", "P0B5_CKEY",
                    "P0B5_CFILL", "P0B5_WKEY", "P0B5_WFILL", "P0B5_WRIM",
                    "P0B5_CAM_")
    for ob in list(bpy.data.objects):
        if ob.name.startswith(rig_prefixes):
            data = ob.data
            bpy.data.objects.remove(ob, do_unlink=True)
            if data is not None and getattr(data, "users", 0) == 0:
                try:
                    if isinstance(data, bpy.types.Light):
                        bpy.data.lights.remove(data)
                    elif isinstance(data, bpy.types.Camera):
                        bpy.data.cameras.remove(data)
                except Exception:
                    pass

    scene.render.engine = saved["engine"]
    scene.render.resolution_x = saved["resx"]
    scene.render.resolution_y = saved["resy"]
    scene.render.resolution_percentage = saved["pct"]
    if hasattr(scene, "cycles"):
        scene.cycles.samples = saved["samples"]
    scene.view_settings.exposure = saved["exposure"]
    scene.view_settings.look = saved["look"]
    scene.render.filepath = saved["filepath"]
    for ob in bpy.data.objects:
        ob.hide_render = saved_hide.get(ob.name, False)
    print("P0B5_RENDER_DONE")


main()
