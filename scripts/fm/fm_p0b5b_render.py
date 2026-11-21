"""P0b.5b review renders: hero branch tee and ceiling-wide sprinkler layout."""

import bpy
import math

OUT = "/home/riyo/Documentos/game/docs"
DOCS = "/home/riyo/Documentos/game/docs"
RIG = "P0B5B_RENDER_RIG"


def clear_rig():
    for ob in list(bpy.data.objects):
        if ob.name.startswith(("P0B5B_CAM_", "P0B5B_KEY", "P0B5B_FILL",
                               "P0B5B_RIM")):
            data = ob.data
            bpy.data.objects.remove(ob, do_unlink=True)
            if data and getattr(data, "users", 0) == 0:
                try:
                    if isinstance(data, bpy.types.Mesh):
                        bpy.data.meshes.remove(data)
                    elif isinstance(data, bpy.types.Light):
                        bpy.data.lights.remove(data)
                    elif isinstance(data, bpy.types.Camera):
                        bpy.data.cameras.remove(data)
                except Exception:
                    pass
    col = bpy.data.collections.get(RIG)
    if col:
        bpy.data.collections.remove(col)


def camera(name, loc, target, lens):
    from mathutils import Vector
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    ob = bpy.data.objects.new(name, cd)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    d = Vector(target) - Vector(loc)
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = ob
    return ob


def area(name, loc, target, power, size, color):
    from mathutils import Vector
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy = power
    ld.shape = 'DISK'
    ld.size = size
    ld.color = color
    ob = bpy.data.objects.new(name, ld)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    d = Vector(target) - Vector(loc)
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return ob


def show_collection(name, state, visible_before=None):
    col = bpy.data.collections.get(name)
    if not col:
        return
    col.hide_render = not state
    for ob in col.all_objects:
        if state:
            was_hidden = visible_before.get(ob.name, (False, False, False))[0] if visible_before else False
            if not was_hidden:
                ob.hide_render = False
        else:
            ob.hide_render = True


def main():
    scene = bpy.context.scene
    saved = {
        "engine": scene.render.engine,
        "res_x": scene.render.resolution_x,
        "res_y": scene.render.resolution_y,
        "res_pct": scene.render.resolution_percentage,
        "samples": getattr(scene.cycles, "samples", 64),
        "exposure": scene.view_settings.exposure,
        "view": scene.view_settings.view_transform,
        "look": scene.view_settings.look,
    }
    hidden = {}
    for ob in bpy.data.objects:
        hidden[ob.name] = (ob.hide_render, ob.hide_viewport, ob.hide_get())
        ob.hide_render = True
    for name in ("L1_P0B5_Z10", "L1_P0B4_Z10", "L1_PROPS_Z10",
                 "L1_KIT_PILOT", "L1_Z10_ABANDON"):
        show_collection(name, True, hidden)
    # Keep studio lights off; use the rig only.
    for name in ("STUDIO_Z10_Key", "STUDIO_Z10_Fill"):
        ob = bpy.data.objects.get(name)
        if ob:
            ob.hide_render = True

    clear_rig()
    col = bpy.data.collections.new(RIG)
    scene.collection.children.link(col)

    scene.render.engine = 'CYCLES'
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    try:
        scene.cycles.device = 'GPU'
    except Exception:
        pass
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = 0.65

    # Close-up: tee at x55 / y17 seen from the south-west, below.
    camera("P0B5B_CAM_TEE", (51.2, 12.8, 2.35), (55.0, 17.0, 3.72), 42)
    area("P0B5B_KEY", (51.0, 13.5, 3.8), (55.0, 17.0, 3.75),
         700.0, 2.2, (1.0, 0.91, 0.80))
    area("P0B5B_FILL", (58.5, 13.0, 3.4), (55.0, 17.0, 3.7),
         320.0, 2.0, (0.72, 0.84, 1.0))
    area("P0B5B_RIM", (58.0, 21.0, 3.9), (55.0, 17.0, 3.75),
         420.0, 1.8, (1.0, 0.78, 0.62))
    bpy.context.view_layer.update()
    scene.render.filepath = DOCS + "/fm_p0b5b_tee_close.png"
    bpy.ops.render.render(write_still=True)
    print("RENDERED", scene.render.filepath)

    # Wide ceiling view: both branch lines, main run, duct and trays.
    for name in ("P0B5B_KEY", "P0B5B_FILL", "P0B5B_RIM"):
        ob = bpy.data.objects.get(name)
        if ob:
            ob.hide_render = True
    camera("P0B5B_CAM_WIDE", (44.0, 11.0, 1.9), (52.5, 22.0, 3.85), 20)
    area("P0B5B_WKEY", (46.0, 12.0, 3.6), (52.0, 20.0, 3.8),
         1600.0, 4.0, (1.0, 0.94, 0.86))
    area("P0B5B_WFILL", (58.0, 24.0, 3.5), (52.0, 18.0, 3.8),
         650.0, 4.0, (0.74, 0.85, 1.0))
    area("P0B5B_WRIM", (47.0, 28.0, 3.9), (52.0, 20.0, 3.8),
         900.0, 3.0, (1.0, 0.80, 0.64))
    bpy.context.view_layer.update()
    scene.view_settings.exposure = 0.85
    scene.render.filepath = DOCS + "/fm_p0b5b_branches_wide.png"
    bpy.ops.render.render(write_still=True)
    print("RENDERED", scene.render.filepath)

    # Restore scene.
    for name, (hr, hv, hs) in hidden.items():
        ob = bpy.data.objects.get(name)
        if ob:
            ob.hide_render = hr
            ob.hide_viewport = hv
            ob.hide_set(hs)
    scene.render.engine = saved["engine"]
    scene.render.resolution_x = saved["res_x"]
    scene.render.resolution_y = saved["res_y"]
    scene.render.resolution_percentage = saved["res_pct"]
    scene.cycles.samples = saved["samples"]
    scene.view_settings.exposure = saved["exposure"]
    scene.view_settings.view_transform = saved["view"]
    scene.view_settings.look = saved["look"]
    clear_rig()
    bpy.context.view_layer.update()
    print("P0B5B_RENDER_DONE")


main()
