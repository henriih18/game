"""P0a.2 LOD visual comparison renders.

Builds a temporary rig with three instances of the same asset (LOD0, LOD1,
LOD2) side by side, labels them, and renders one PNG per family:

  docs/fm_p0a2_lod_door.png
  docs/fm_p0a2_lod_light.png

The library objects are never modified: instances share mesh data and live
in a temporary collection that is deleted afterwards. Render settings are
restored, and the .blend is not saved.
"""
import bpy
import math
import os
from mathutils import Matrix, Vector

OUT_DIR = "docs"
RIG = "P0_LOD_RENDER_RIG"

DOOR = [
    ("SM_SH_DOOR_SEC_SINGLE_ROOT", "LOD0"),
    ("SM_SH_DOOR_SEC_SINGLE_LOD1_ROOT", "LOD1"),
    ("SM_SH_DOOR_SEC_SINGLE_LOD2_ROOT", "LOD2"),
]
LIGHT = [
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


def simple_mat(name, color, rough=0.55, metallic=0.0):
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def add_floor(coll, z, width=10.0, depth=7.0, center_y=0.0):
    me = bpy.data.meshes.new("P0_LOD_Floor")
    w2, d2 = width / 2.0, depth / 2.0
    me.from_pydata(
        [(-w2, center_y - d2, z), (w2, center_y - d2, z),
         (w2, center_y + d2, z), (-w2, center_y + d2, z)],
        [], [(0, 1, 2, 3)])
    me.materials.append(simple_mat("M_P0_LOD_Floor", (0.055, 0.058, 0.06), 0.72))
    ob = bpy.data.objects.new("P0_LOD_Floor", me)
    coll.objects.link(ob)
    return ob


def add_label(coll, text, loc, size=0.16, mat=None):
    cu = bpy.data.curves.new("P0_LOD_Label_" + text, type='FONT')
    cu.body = text
    cu.align_x = 'CENTER'
    cu.align_y = 'CENTER'
    cu.size = size
    cu.extrude = 0.0015
    ob = bpy.data.objects.new("P0_LOD_Label_" + text, cu)
    coll.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (math.radians(90), 0, 0)
    if mat:
        ob.data.materials.append(mat)
    return ob


def instance_asset(src_name, target_loc, coll):
    src = bpy.data.objects.get(src_name)
    if src is None:
        raise RuntimeError("missing source root: " + src_name)
    root = bpy.data.objects.new(src.name + "_RIG", None)
    coll.objects.link(root)
    root.location = Vector(target_loc)
    root.rotation_euler = src.rotation_euler
    root.scale = src.scale

    rel = src.matrix_world.inverted()
    count = 0
    for child in src.children:
        if child.type != 'MESH':
            continue
        if child.get("fm_class") == "COLLISION" or child.name.endswith("-col"):
            continue
        dup = child.copy()
        dup.data = child.data  # shared mesh, no duplication in the library
        coll.objects.link(dup)
        dup.parent = root
        dup.matrix_parent_inverse = Matrix.Identity(4)
        dup.matrix_local = rel @ child.matrix_world
        dup.hide_render = False
        count += 1
    return root, count


def add_area(coll, name, loc, energy, size, color=(1, 1, 1), target=(0, 0, 1.2)):
    data = bpy.data.lights.new(name, type='AREA')
    data.energy = energy
    data.shape = 'SQUARE'
    data.size = size
    data.color = color
    ob = bpy.data.objects.new(name, data)
    coll.objects.link(ob)
    ob.location = loc
    direction = Vector(target) - Vector(loc)
    ob.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return ob


def add_camera(coll, name, loc, target, lens):
    data = bpy.data.cameras.new(name)
    data.lens = lens
    data.sensor_width = 36
    ob = bpy.data.objects.new(name, data)
    coll.objects.link(ob)
    ob.location = loc
    direction = Vector(target) - Vector(loc)
    ob.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return ob


def main():
    scene = bpy.context.scene
    old = {
        "engine": scene.render.engine,
        "res_x": scene.render.resolution_x,
        "res_y": scene.render.resolution_y,
        "pct": scene.render.resolution_percentage,
        "samples": scene.cycles.samples,
        "use_denoise": scene.cycles.use_denoising,
        "exposure": scene.view_settings.exposure,
        "view": scene.view_settings.view_transform,
        "look": scene.view_settings.look,
        "world": scene.world,
        "camera": scene.camera,
        "filepath": scene.render.filepath,
        "film_transparent": scene.render.film_transparent,
    }
    hidden = {}
    for ob in bpy.data.objects:
        hidden[ob.name] = ob.hide_render
        ob.hide_render = True

    clear_rig()
    coll = bpy.data.collections.new(RIG)
    scene.collection.children.link(coll)

    text_mat = simple_mat("M_P0_LOD_Text", (0.82, 0.80, 0.74), 0.5)
    text_bsdf = next(n for n in text_mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    text_bsdf.inputs["Emission Color"].default_value = (0.9, 0.88, 0.8, 1.0)
    text_bsdf.inputs["Emission Strength"].default_value = 0.6

    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 96
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = 0.55

    world = bpy.data.worlds.new("P0_LOD_World") if not scene.world else scene.world
    scene.world = world
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs[0].default_value = (0.012, 0.014, 0.018, 1.0)
    bg.inputs[1].default_value = 0.35

    # ---------------- door comparison ----------------
    add_floor(coll, -0.006, width=10.0, depth=6.0, center_y=0.0)
    xs = (-1.75, 0.0, 1.75)
    for (root_name, label), x in zip(DOOR, xs):
        instance_asset(root_name, (x, 0, 0), coll)
        add_label(coll, label, (x, 0.12, 2.95), size=0.17, mat=text_mat)
    add_area(coll, "P0_LOD_Key", (-3.2, -5.5, 5.2), 1500, 4.0, (1.0, 0.97, 0.92))
    add_area(coll, "P0_LOD_Fill", (3.6, -4.0, 2.6), 520, 3.0, (0.72, 0.82, 1.0))
    add_area(coll, "P0_LOD_Rim", (0.0, 3.2, 4.2), 900, 3.0, (1.0, 0.86, 0.72))
    cam = add_camera(coll, "P0_LOD_CamDoor", (0.0, -10.8, 2.0), (0.0, 0.0, 1.30), 48)
    scene.camera = cam
    scene.render.filepath = os.path.join(OUT_DIR, "fm_p0a2_lod_door.png")
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)
    print("RENDERED", scene.render.filepath)

    # hide door rig objects for the light shot
    for ob in list(coll.objects):
        ob.hide_render = True
    for ob in list(coll.objects):
        if ob.name.startswith(("P0_LOD_Floor", "P0_LOD_Label", "P0_LOD_Key", "P0_LOD_Fill", "P0_LOD_Rim", "P0_LOD_CamDoor")):
            continue
        ob.hide_render = True

    # ---------------- luminaire comparison ----------------
    # reuse floor/labels are recreated below to avoid overlap
    for ob in list(coll.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    add_floor(coll, -0.006, width=8.0, depth=5.0, center_y=0.0)
    lxs = (-1.55, 0.0, 1.55)
    for (root_name, label), x in zip(LIGHT, lxs):
        instance_asset(root_name, (x, 0, 1.72), coll)
        add_label(coll, label, (x, 0.10, 0.55), size=0.14, mat=text_mat)
    add_area(coll, "P0_LOD_Key", (-2.4, -4.6, 4.4), 950, 3.2, (1.0, 0.97, 0.92), target=(0, 0, 1.7))
    add_area(coll, "P0_LOD_Fill", (2.8, -3.2, 2.2), 380, 2.6, (0.72, 0.82, 1.0), target=(0, 0, 1.7))
    add_area(coll, "P0_LOD_Rim", (0.0, 2.4, 3.6), 600, 2.6, (1.0, 0.86, 0.72), target=(0, 0, 1.7))
    cam = add_camera(coll, "P0_LOD_CamLight", (0.0, -5.4, 1.95), (0.0, 0.0, 1.66), 62)
    scene.camera = cam
    scene.render.filepath = os.path.join(OUT_DIR, "fm_p0a2_lod_light.png")
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)
    print("RENDERED", scene.render.filepath)

    # ---------------- cleanup ----------------
    clear_rig()
    for ob in bpy.data.objects:
        if ob.name in hidden:
            ob.hide_render = hidden[ob.name]
    scene.render.engine = old["engine"]
    scene.render.resolution_x = old["res_x"]
    scene.render.resolution_y = old["res_y"]
    scene.render.resolution_percentage = old["pct"]
    scene.cycles.samples = old["samples"]
    scene.cycles.use_denoising = old["use_denoise"]
    scene.view_settings.exposure = old["exposure"]
    scene.view_settings.view_transform = old["view"]
    scene.view_settings.look = old["look"]
    scene.world = old["world"]
    scene.camera = old["camera"]
    scene.render.filepath = old["filepath"]
    scene.render.film_transparent = old["film_transparent"]
    print("LOD_RENDER_DONE")


main()
