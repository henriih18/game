"""Review renders for L1_SECURITY_R21A_HERO.

Run in Blender MCP after fm_ops_build.build(). Creates temporary cameras/lights and a
neutral review floor, renders three 1280x720 stills, then removes the temporary setup.
The saved .blend is not modified by this script.
"""
import bpy
import math
import os
from mathutils import Vector

OUT = "/home/riyo/Documentos/game/docs"


def _review_floor():
    m = bpy.data.materials.get("M_HERO_Ops_ReviewFloor")
    if m is None:
        m = bpy.data.materials.new("M_HERO_Ops_ReviewFloor")
        m.use_nodes = True
        nt = m.node_tree
        b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
        b.inputs["Base Color"].default_value = (0.032, 0.034, 0.037, 1)
        b.inputs["Roughness"].default_value = 0.78
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = 22.0
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.18
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        nt.links.new(nz.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def _collection():
    c = bpy.data.collections.get("TMP_REVIEW_OPS")
    if c is None:
        c = bpy.data.collections.new("TMP_REVIEW_OPS")
        bpy.context.scene.collection.children.link(c)
    for o in list(c.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    return c


def _area(coll, name, loc, energy, size, color, target):
    d = bpy.data.lights.new(name, "AREA")
    d.energy = energy
    d.shape = "DISK"
    d.size = size
    d.color = color
    o = bpy.data.objects.new(name, d)
    o.location = loc
    v = Vector(target) - Vector(loc)
    o.rotation_euler = v.to_track_quat("-Z", "Y").to_euler()
    coll.objects.link(o)
    return o


def _cam(coll, name, loc, target, lens):
    d = bpy.data.cameras.new(name)
    d.lens = lens
    o = bpy.data.objects.new(name, d)
    o.location = loc
    v = Vector(target) - Vector(loc)
    o.rotation_euler = v.to_track_quat("-Z", "Y").to_euler()
    coll.objects.link(o)
    return o


def _render(path, cam, exposure):
    s = bpy.context.scene
    s.camera = cam
    s.view_settings.exposure = exposure
    s.render.engine = "BLENDER_EEVEE"
    s.render.resolution_x = 1280
    s.render.resolution_y = 720
    s.render.resolution_percentage = 100
    s.render.image_settings.file_format = "PNG"
    s.render.filepath = path
    bpy.ops.render.render(write_still=True)


def render_all():
    os.makedirs(OUT, exist_ok=True)
    floor = bpy.data.objects["SM_L1_Zone03_Security_Floor"]
    orig = floor.material_slots[0].material
    floor.material_slots[0].material = _review_floor()
    c = _collection()
    try:
        # 1. workstation close-up
        _area(c, "CL_KEY", (-91.0, 28.0, 2.2), 170, 2.0, (1.0, 0.93, 0.85), (-89.5, 30.3, 1.0))
        _area(c, "CL_FILL", (-89.2, 27.8, 1.4), 45, 1.5, (0.60, 0.76, 1.0), (-89.5, 30.3, 1.0))
        _area(c, "CL_RIM", (-87.0, 31.2, 2.5), 100, 1.3, (0.55, 0.85, 0.85), (-89.5, 30.3, 1.2))
        _area(c, "CL_SIDE", (-92.5, 30.8, 2.5), 40, 2.5, (1.0, 0.9, 0.8), (-89.5, 30.3, 1.0))
        cam = _cam(c, "CLOSE_CAM", (-92.35, 28.75, 1.55), (-89.15, 30.45, 1.02), 40)
        _render(os.path.join(OUT, "fm_security_ops_hero_closeup.png"), cam, -0.22)
        for o in list(c.objects):
            bpy.data.objects.remove(o, do_unlink=True)

        # 2. three-quarter of the operations centre
        _area(c, "TQ_KEY", (-91.0, 26.5, 3.3), 330, 3.2, (1.0, 0.94, 0.86), (-86.0, 30.3, 1.1))
        _area(c, "TQ_FILL", (-83.0, 26.0, 2.5), 130, 2.6, (0.62, 0.78, 1.0), (-84.8, 30.4, 1.1))
        _area(c, "TQ_CCTV", (-83.5, 34.0, 3.6), 300, 2.8, (0.62, 0.88, 0.88), (-85.4, 35.6, 2.3))
        _area(c, "TQ_RACK", (-79.0, 33.6, 2.9), 150, 2.0, (0.70, 0.85, 1.0), (-78.0, 35.1, 1.3))
        _area(c, "TQ_TOP", (-88.0, 31.0, 4.5), 120, 4.0, (1.0, 0.95, 0.9), (-87.0, 31.0, 1.0))
        cam = _cam(c, "THREEQ_CAM", (-93.4, 26.6, 2.45), (-83.7, 31.35, 1.25), 30)
        _render(os.path.join(OUT, "fm_security_ops_hero_three_quarter.png"), cam, -0.15)
        for o in list(c.objects):
            bpy.data.objects.remove(o, do_unlink=True)

        # 3. wide room with the checkpoint in the foreground
        _area(c, "W_CHECK", (-89.5, 9.3, 2.9), 420, 2.0, (1.0, 0.9, 0.8), (-89.0, 13.8, 1.7))
        _area(c, "W_MID", (-87.0, 18.0, 3.9), 380, 4.0, (1.0, 0.9, 0.8), (-86.0, 20.0, 1.0))
        _area(c, "W_OPS", (-85.0, 30.0, 4.4), 520, 4.0, (1.0, 0.93, 0.85), (-85.0, 31.0, 1.0))
        _area(c, "W_WEST", (-89.0, 28.0, 4.2), 340, 3.5, (1.0, 0.9, 0.8), (-88.0, 29.0, 1.0))
        _area(c, "W_EAST", (-79.0, 34.0, 4.0), 240, 3.0, (0.7, 0.85, 1.0), (-78.0, 34.0, 1.0))
        cam = _cam(c, "WIDE_CAM", (-85.5, 11.6, 2.80), (-88.8, 20.0, 1.0), 18)
        _render(os.path.join(OUT, "fm_security_ops_hero_wide.png"), cam, -0.22)
    finally:
        floor.material_slots[0].material = orig
        for o in list(c.objects):
            bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.collections.remove(c)
    print("OPS_RENDERS_OK")


if __name__ == "__main__":
    render_all()
