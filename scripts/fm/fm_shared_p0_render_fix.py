"""Re-render the P0a shared services catalogue and the P0 test assembly.

The previous catalogue renders were too dark and too far away.  This script
keeps the same studio setup but uses closer cameras and stronger key/fill
lights.  It only renders the two images that need fixing; doors and lighting
catalogues are left untouched.

Run inside the live Blender through /tmp/opencode/bpy_run.py.
"""
import math
import os

import bpy
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
OUT_SERVICES = os.path.join(ROOT, "docs/fm_shared_p0_services.png")
OUT_TEST = os.path.join(ROOT, "docs/fm_shared_p0_test_assembly.png")

RIG = "P0_RENDER_FIX_RIG"


def clear_rig():
    coll = bpy.data.collections.get(RIG)
    if coll:
        for ob in list(coll.objects):
            data = ob.data
            bpy.data.objects.remove(ob, do_unlink=True)
            if data and getattr(data, "users", 0) == 0:
                if isinstance(data, bpy.types.Mesh):
                    bpy.data.meshes.remove(data)
        bpy.data.collections.remove(coll)


def save_state():
    scene = bpy.context.scene
    return {
        "engine": scene.render.engine,
        "res_x": scene.render.resolution_x,
        "res_y": scene.render.resolution_y,
        "pct": scene.render.resolution_percentage,
        "filepath": scene.render.filepath,
        "exposure": scene.view_settings.exposure,
        "look": scene.view_settings.look,
        "view_transform": scene.view_settings.view_transform,
        "world_strength": scene.world.color if scene.world else None,
        "samples": getattr(scene.cycles, "samples", None) if hasattr(scene, "cycles") else None,
        "denoise": getattr(scene.cycles, "use_denoising", None) if hasattr(scene, "cycles") else None,
        "film_transparent": scene.render.film_transparent,
    }


def restore_state(state):
    scene = bpy.context.scene
    scene.render.engine = state["engine"]
    scene.render.resolution_x = state["res_x"]
    scene.render.resolution_y = state["res_y"]
    scene.render.resolution_percentage = state["pct"]
    scene.render.filepath = state["filepath"]
    scene.view_settings.exposure = state["exposure"]
    scene.view_settings.look = state["look"]
    scene.view_settings.view_transform = state["view_transform"]
    scene.render.film_transparent = state["film_transparent"]
    if hasattr(scene, "cycles"):
        if state["samples"] is not None:
            scene.cycles.samples = state["samples"]
        if state["denoise"] is not None:
            scene.cycles.use_denoising = state["denoise"]


def aim(ob, target):
    direction = Vector(target) - ob.location
    ob.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def area_light(coll, name, location, target, energy, size, color=(1.0, 1.0, 1.0)):
    data = bpy.data.lights.new(name, type="AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    ob = bpy.data.objects.new(name, data)
    coll.objects.link(ob)
    ob.location = location
    aim(ob, target)
    return ob


def camera(coll, name, location, target, lens):
    data = bpy.data.cameras.new(name)
    data.lens = lens
    data.sensor_width = 36.0
    ob = bpy.data.objects.new(name, data)
    coll.objects.link(ob)
    ob.location = location
    aim(ob, target)
    return ob


def studio_floor(coll, z, size, name="P0_RENDER_FIX_FLOOR"):
    mesh = bpy.data.meshes.new(name)
    verts = [(-size, -size, z), (size, -size, z), (size, size, z), (-size, size, z)]
    mesh.from_pydata(verts, [], [(0, 1, 2, 3)])
    mesh.update()
    ob = bpy.data.objects.new(name, mesh)
    coll.objects.link(ob)
    mat = bpy.data.materials.get("M_SH_Test_Concrete")
    if mat:
        mesh.materials.append(mat)
    return ob


def render(scene, cam, path):
    scene.camera = cam
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("RENDERED", path)


def main():
    scene = bpy.context.scene
    state = save_state()
    clear_rig()

    rig = bpy.data.collections.new(RIG)
    scene.collection.children.link(rig)

    # Isolate the catalogue from the level shell: hide every object first, then
    # re-enable only the target collection for each shot.
    original_hide = {ob.name: ob.hide_render for ob in bpy.data.objects if ob is not None}
    for ob in bpy.data.objects:
        if ob is not None:
            ob.hide_render = True

    scene.render.engine = "CYCLES"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.cycles.samples = 96
    scene.cycles.use_denoising = True
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.75

    # Keep only the shared library visible; hide doors/lights when shooting the
    # services row so they do not clutter the frame.
    shared = bpy.data.collections.get("L1_SHARED_HERO")
    services_coll = bpy.data.collections.get("SERVICES")
    doors_coll = bpy.data.collections.get("DOORS")
    lights_coll = bpy.data.collections.get("LIGHTING")
    test_coll = bpy.data.collections.get("P0_TEST_ASSEMBLY")

    def hide_collection(coll, hide):
        if not coll:
            return
        for ob in coll.all_objects:
            if ob is not None:
                ob.hide_render = hide

    hide_collection(shared, True)

    # ---------------- services catalogue ----------------
    hide_collection(services_coll, False)
    for coll in (doors_coll, lights_coll, test_coll):
        hide_collection(coll, True)

    floor = studio_floor(rig, -0.56, 30.0)
    floor.hide_render = False

    key = area_light(rig, "P0_FIX_KEY", (-1.5, -7.0, 7.5), (4.8, 4.0, 0.6), 3400, 6.0)
    fill = area_light(rig, "P0_FIX_FILL", (10.5, -4.0, 4.0), (4.8, 4.0, 0.6), 1400, 5.0,
                      color=(0.82, 0.90, 1.0))
    rim = area_light(rig, "P0_FIX_RIM", (3.5, 15.0, 6.0), (4.8, 5.0, 0.8), 2200, 5.0)

    cam_services = camera(rig, "P0_FIX_CAM_SERVICES", (4.8, -7.6, 5.4),
                          (4.8, 4.2, 0.55), 35.0)
    render(scene, cam_services, OUT_SERVICES)
    floor.hide_render = True
    for ob in (key, fill, rim):
        ob.hide_render = True

    # ---------------- test assembly ----------------
    for coll in (doors_coll, lights_coll, services_coll):
        hide_collection(coll, True)
    hide_collection(test_coll, False)

    floor2 = studio_floor(rig, -0.14, 12.0, name="P0_RENDER_FIX_FLOOR_TEST")
    floor2.location.x = 301.2
    key2 = area_light(rig, "P0_FIX_KEY2", (298.5, -5.5, 7.2), (301.6, 0.0, 2.9), 3400, 5.0)
    fill2 = area_light(rig, "P0_FIX_FILL2", (305.5, -3.5, 3.2), (301.6, 0.0, 2.9), 1400, 4.5,
                       color=(0.82, 0.90, 1.0))
    rim2 = area_light(rig, "P0_FIX_RIM2", (302.0, 6.0, 6.5), (301.6, 0.0, 2.9), 2200, 4.5)

    cam_test = camera(rig, "P0_FIX_CAM_TEST", (302.8, -5.6, 5.0),
                     (301.2, 0.0, 2.8), 30.0)
    render(scene, cam_test, OUT_TEST)

    # Restore visibility for every object.
    for ob in bpy.data.objects:
        if ob is not None:
            ob.hide_render = original_hide.get(ob.name, False)

    clear_rig()
    restore_state(state)
    print("P0_FIX_RENDER_DONE")


main()
