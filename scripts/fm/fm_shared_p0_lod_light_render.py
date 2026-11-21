"""P0a.2 — standalone luminaire LOD comparison render.

Renders LOD0/LOD1/LOD2 of SM_SH_LUMINAIRE_1500_ON in a clean rig, without
reusing the door pass. Writes docs/fm_p0a2_lod_light.png and does not save
the .blend.
"""
import bpy
import math
import os
from mathutils import Matrix, Vector
from bpy_extras.object_utils import world_to_camera_view

OUT = "docs/fm_p0a2_lod_light.png"
RIG = "P0_LOD_LIGHT_RIG"
ASSETS = [
    ("SM_SH_LUMINAIRE_1500_ON_ROOT", "LOD0"),
    ("SM_SH_LUMINAIRE_1500_ON_LOD1_ROOT", "LOD1"),
    ("SM_SH_LUMINAIRE_1500_ON_LOD2_ROOT", "LOD2"),
]


def clear_rig():
    coll = bpy.data.collections.get(RIG)
    if not coll:
        return
    for ob in list(coll.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.collections.remove(coll)


def mat(name, color, rough=0.55, metallic=0.0, emission=None):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metallic
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 0.8
    return m


def add_box(coll, name, size, loc, material, rot=(0, 0, 0)):
    me = bpy.data.meshes.new(name)
    sx, sy, sz = (s * 0.5 for s in size)
    me.from_pydata(
        [(-sx, -sy, -sz), (sx, -sy, -sz), (sx, sy, -sz), (-sx, sy, -sz),
         (-sx, -sy, sz), (sx, -sy, sz), (sx, sy, sz), (-sx, sy, sz)],
        [],
        [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
         (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)])
    me.materials.append(material)
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = rot
    return ob


def add_label(coll, text, loc, size=0.16, material=None):
    cu = bpy.data.curves.new("P0_LOD_LightLabel_" + text, type='FONT')
    cu.body = text
    cu.align_x = 'CENTER'
    cu.align_y = 'CENTER'
    cu.size = size
    cu.extrude = 0.0015
    ob = bpy.data.objects.new("P0_LOD_LightLabel_" + text, cu)
    coll.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (math.radians(90), 0, 0)
    if material:
        ob.data.materials.append(material)
    return ob


def instance_asset(src_name, target, coll):
    src = bpy.data.objects.get(src_name)
    if src is None:
        raise RuntimeError("missing " + src_name)
    root = bpy.data.objects.new(src_name + "_RIG", None)
    coll.objects.link(root)
    root.location = Vector(target)
    root.rotation_euler = src.rotation_euler
    root.scale = src.scale
    rel = src.matrix_world.inverted()
    n = 0
    for child in src.children:
        if child.type != 'MESH':
            continue
        if child.get("fm_class") == "COLLISION" or child.name.endswith("-col"):
            continue
        dup = child.copy()
        dup.data = child.data
        coll.objects.link(dup)
        dup.parent = root
        dup.matrix_parent_inverse = Matrix.Identity(4)
        dup.matrix_local = rel @ child.matrix_world
        dup.hide_render = False
        n += 1
        wc = [dup.matrix_world @ v.co for v in dup.data.vertices]
        print("  DUP", dup.name, "mworld_t", tuple(round(v,3) for v in dup.matrix_world.translation),
              "wbbox", tuple(round(min(getattr(v,a) for v in wc),3) for a in 'xyz'),
              tuple(round(max(getattr(v,a) for v in wc),3) for a in 'xyz'))
    return n


def add_area(coll, name, loc, energy, size, target, color=(1, 1, 1)):
    data = bpy.data.lights.new(name, type='AREA')
    data.energy = energy
    data.shape = 'SQUARE'
    data.size = size
    data.color = color
    ob = bpy.data.objects.new(name, data)
    coll.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob


def main():
    scene = bpy.context.scene
    old = {
        "engine": scene.render.engine,
        "res_x": scene.render.resolution_x,
        "res_y": scene.render.resolution_y,
        "pct": scene.render.resolution_percentage,
        "samples": scene.cycles.samples,
        "denoise": scene.cycles.use_denoising,
        "exposure": scene.view_settings.exposure,
        "view": scene.view_settings.view_transform,
        "look": scene.view_settings.look,
        "world": scene.world,
        "camera": scene.camera,
        "filepath": scene.render.filepath,
        "transparent": scene.render.film_transparent,
    }
    hidden = {}
    for ob in bpy.data.objects:
        hidden[ob.name] = ob.hide_render
        ob.hide_render = True

    clear_rig()
    coll = bpy.data.collections.new(RIG)
    scene.collection.children.link(coll)

    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 96
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = 0.32

    world = bpy.data.worlds.new("P0_LOD_LightWorld") if not scene.world else scene.world
    scene.world = world
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs[0].default_value = (0.02, 0.023, 0.028, 1.0)
    bg.inputs[1].default_value = 0.30

    floor_mat = mat("M_P0_LOD_LightFloor", (0.12, 0.12, 0.125), 0.65)
    add_box(coll, "P0_LOD_LightFloor", (10.5, 6.5, 0.02), (0, 0.4, -0.01), floor_mat)
    back = mat("M_P0_LOD_LightBack", (0.012, 0.013, 0.016), 0.9)
    add_box(coll, "P0_LOD_LightBack", (12.0, 0.02, 5.0), (0, 2.8, 2.0), back)

    text = mat("M_P0_LOD_LightText", (0.8, 0.78, 0.72), 0.5, 0.0,
               emission=(0.9, 0.88, 0.8))
    xs = (-1.85, 0.0, 1.85)
    for (name, label), x in zip(ASSETS, xs):
        n = instance_asset(name, (x, 0, 1.72), coll)
        add_label(coll, label, (x, 0.35, 2.15), size=0.16, material=text)
        print("INSTANCE", label, name, "meshes", n)

    add_area(coll, "P0_LOD_LightKey", (-2.6, -4.8, 4.8), 800, 3.5, (0, 0, 1.6))
    add_area(coll, "P0_LOD_LightFill", (3.2, -4.0, 2.4), 300, 3.0, (0, 0, 1.6),
             color=(0.75, 0.84, 1.0))
    add_area(coll, "P0_LOD_LightRim", (0, 3.0, 4.2), 500, 3.0, (0, 0, 1.7),
             color=(1.0, 0.86, 0.72))

    cam_data = bpy.data.cameras.new("P0_LOD_LightCam")
    cam_data.lens = 48
    cam_data.sensor_width = 36
    cam = bpy.data.objects.new("P0_LOD_LightCam", cam_data)
    coll.objects.link(cam)
    cam.location = (0, -8.2, 2.0)
    cam.rotation_euler = (Vector((0, 0, 1.72)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = cam

    bpy.context.view_layer.update()
    print("RIG_OBJECTS", len(coll.objects), "CAM", scene.camera.name)
    vis = [o.name for o in coll.objects if o.type == 'MESH' and not o.hide_render]
    print("VISIBLE_MESHES", len(vis), vis[:12])
    for o in coll.objects:
        if o.type == 'MESH' and o.name.startswith("SM_SH_LUMINAIRE"):
            c = sum((o.matrix_world @ v.co for v in o.data.vertices), Vector()) / len(o.data.vertices)
            ndc = world_to_camera_view(scene, cam, c)
            print("  PROJECT", o.name, "center", tuple(round(v,3) for v in c), "ndc", tuple(round(v,3) for v in ndc))

    scene.render.filepath = os.path.abspath(OUT)
    bpy.ops.render.render(write_still=True)
    print("RENDERED", scene.render.filepath)

    clear_rig()
    for ob in bpy.data.objects:
        if ob.name in hidden:
            ob.hide_render = hidden[ob.name]
    scene.render.engine = old["engine"]
    scene.render.resolution_x = old["res_x"]
    scene.render.resolution_y = old["res_y"]
    scene.render.resolution_percentage = old["pct"]
    scene.cycles.samples = old["samples"]
    scene.cycles.use_denoising = old["denoise"]
    scene.view_settings.exposure = old["exposure"]
    scene.view_settings.view_transform = old["view"]
    scene.view_settings.look = old["look"]
    scene.world = old["world"]
    scene.camera = old["camera"]
    scene.render.filepath = old["filepath"]
    scene.render.film_transparent = old["transparent"]
    print("LIGHT_RENDER_DONE")


main()
