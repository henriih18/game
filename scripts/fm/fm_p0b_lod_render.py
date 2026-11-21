"""P0b.3 LOD visual comparison for the corridor HVAC spine.

Cuts a 2.4 m section from LOD0/LOD1/LOD2 and lays the three sections side by
side in a temporary studio rig. Library meshes are duplicated and cut, never
modified. Writes docs/fm_p0b_lod_compare.png; does not save the .blend.
"""
import bpy
import bmesh
import math
from mathutils import Vector

RIG = "P0B_LOD_RENDER_RIG"
OUT = "docs/fm_p0b_lod_compare.png"
SOURCES = [
    ("P0B_HVAC_RUN_800x600", "LOD0", -2.8),
    ("P0B_HVAC_RUN_800x600_LOD1", "LOD1", 0.0),
    ("P0B_HVAC_RUN_800x600_LOD2", "LOD2", 2.8),
]
CUT_X = 2.4


def clear_rig():
    coll = bpy.data.collections.get(RIG)
    if not coll:
        return
    for ob in list(coll.objects):
        data = ob.data
        bpy.data.objects.remove(ob, do_unlink=True)
        if data and data.users == 0 and isinstance(data, bpy.types.Mesh):
            bpy.data.meshes.remove(data)
    bpy.data.collections.remove(coll)


def simple_mat(name, color, rough=0.55):
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    return mat


def add_floor(coll):
    me = bpy.data.meshes.new("P0B_LOD_Floor")
    me.from_pydata(
        [(-8, -4, 3.0), (10, -4, 3.0), (10, 4, 3.0), (-8, 4, 3.0)],
        [], [(0, 1, 2, 3)])
    me.materials.append(simple_mat("M_P0B_LOD_Floor", (0.03, 0.032, 0.035), 0.8))
    ob = bpy.data.objects.new("P0B_LOD_Floor", me)
    coll.objects.link(ob)
    return ob


def add_wall(coll):
    me = bpy.data.meshes.new("P0B_LOD_Wall")
    me.from_pydata(
        [(-8, 2.6, 3.0), (10, 2.6, 3.0), (10, 2.6, 6.2), (-8, 2.6, 6.2)],
        [], [(0, 1, 2, 3)])
    me.materials.append(simple_mat("M_P0B_LOD_Wall", (0.025, 0.027, 0.03), 0.9))
    ob = bpy.data.objects.new("P0B_LOD_Wall", me)
    coll.objects.link(ob)
    return ob


def add_label(coll, text, loc, mat, size=0.2):
    cu = bpy.data.curves.new("P0B_LOD_Label_" + text, type='FONT')
    cu.body = text
    cu.align_x = 'CENTER'
    cu.align_y = 'CENTER'
    cu.size = size
    cu.extrude = 0.002
    ob = bpy.data.objects.new("P0B_LOD_Label_" + text, cu)
    coll.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (math.radians(90), 0, 0)
    ob.data.materials.append(mat)
    return ob


def add_area(coll, name, loc, energy, size, color, target):
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


def cut_section(src, target_x):
    dup = src.copy()
    dup.data = src.data.copy()
    me = dup.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.bisect_plane(
        bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
        plane_co=(CUT_X, 0.0, 0.0), plane_no=(1.0, 0.0, 0.0),
        clear_outer=True)
    bm.to_mesh(me)
    bm.free()
    me.name = src.data.name + "_SECTION"
    dup.name = src.name + "_SECTION"
    dup.parent = None
    dup.location = (target_x, 0.0, 3.55)
    dup.rotation_euler = (0.0, 0.0, 0.0)
    dup.scale = (1.0, 1.0, 1.0)
    dup.hide_render = False
    dup.hide_set(False)
    return dup


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
        "camera": scene.camera,
        "filepath": scene.render.filepath,
    }
    hidden = {ob.name: ob.hide_render for ob in bpy.data.objects}
    for ob in bpy.data.objects:
        ob.hide_render = True

    clear_rig()
    coll = bpy.data.collections.new(RIG)
    scene.collection.children.link(coll)

    add_floor(coll)
    add_wall(coll)

    text_mat = simple_mat("M_P0B_LOD_Text", (0.85, 0.83, 0.76), 0.4)
    tb = next(n for n in text_mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    tb.inputs["Emission Color"].default_value = (0.95, 0.92, 0.82, 1.0)
    tb.inputs["Emission Strength"].default_value = 0.5

    for i, (src_name, label, x) in enumerate(SOURCES):
        src = bpy.data.objects.get(src_name)
        if src is None:
            raise RuntimeError("missing " + src_name)
        dup = cut_section(src, x)
        coll.objects.link(dup)
        add_label(coll, label, (x + CUT_X / 2.0, 0.0, 4.28), text_mat, 0.18)

    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 96
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = 0.15

    if scene.world is None:
        scene.world = bpy.data.worlds.new("P0B_LOD_World")
    scene.world.use_nodes = True
    bg = next(n for n in scene.world.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs[0].default_value = (0.006, 0.007, 0.009, 1.0)
    bg.inputs[1].default_value = 0.25

    add_area(coll, "P0B_LOD_KEY", (-4.0, -6.0, 6.8), 1100, 4.0,
             (1.0, 0.97, 0.9), (1.2, 0.0, 3.5))
    add_area(coll, "P0B_LOD_FILL", (6.0, -5.0, 4.6), 450, 3.5,
             (0.72, 0.82, 1.0), (1.2, 0.0, 3.5))
    add_area(coll, "P0B_LOD_RIM", (3.0, 2.0, 6.0), 700, 3.0,
             (1.0, 0.86, 0.72), (1.2, 0.0, 3.55))

    cam_data = bpy.data.cameras.new("P0B_LOD_Cam")
    cam_data.lens = 42
    cam = bpy.data.objects.new("P0B_LOD_Cam", cam_data)
    coll.objects.link(cam)
    cam.location = (1.2, -11.0, 3.85)
    cam.rotation_euler = (Vector((1.2, 0.0, 3.52)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = cam

    scene.render.filepath = OUT
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)

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
    scene.camera = old["camera"]
    scene.render.filepath = old["filepath"]
    clear_rig()
    print("RENDERED", OUT)


main()
