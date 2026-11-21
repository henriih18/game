import bpy
import bmesh
import json
import math
import os
import random
import sys
from mathutils import Vector, Matrix, Euler

sys.path.insert(0, "/home/riyo/Documentos/game/scripts/fm")
from fm_shared_p0_lib import ensure_materials  # noqa: E402

M = ensure_materials()
GALV = M["galv"]
DARK = M["steel_dark"]
BARE = M["steel_bare"]
RED = M["sprink_red"]
LABEL = M["label"]
RUB = M["rubber"]

COLL = "L1_Z10_ABANDON"
LIGHT_COLL = "L1_Z10_LIGHTING"
ATMO = "L1_Z10_ATMOSPHERE"
DOCS = "/home/riyo/Documentos/game/docs"


def collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    for ob in list(col.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    col.hide_viewport = False
    col.hide_render = False
    return col


def select_only(ob):
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob


def material(name, base=(0.5, 0.5, 0.5, 1.0), rough=0.5, metal=0.0,
             emission=None, strength=0.0, alpha=1.0, transmission=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is None:
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        out = next((n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'), None)
        if out is None:
            out = nt.nodes.new("ShaderNodeOutputMaterial")
        nt.links.new(bsdf.outputs[0], out.inputs[0])
    def setv(key, value):
        if key in bsdf.inputs:
            bsdf.inputs[key].default_value = value
    setv("Base Color", base)
    setv("Roughness", rough)
    setv("Metallic", metal)
    setv("Alpha", alpha)
    setv("Transmission Weight", transmission)
    setv("IOR", 1.45)
    if emission is not None:
        setv("Emission Color", emission)
        setv("Emission Strength", strength)
    if alpha < 1.0:
        try:
            mat.blend_method = 'BLEND'
        except Exception:
            pass
    return mat


PAPER = material("M_Z10_Paper", (0.70, 0.68, 0.61, 1.0), 0.88)
MANILA = material("M_Z10_Manila", (0.42, 0.29, 0.13, 1.0), 0.82)
HOLE = material("M_Z10_CeilingHole", (0.004, 0.004, 0.005, 1.0), 1.0)
LAMP = material("M_Z10_WorkLamp", (1.0, 0.85, 0.62, 1.0), 0.4,
                emission=(1.0, 0.72, 0.38, 1.0), strength=12.0)
GLASS = material("M_Z10_WorkGlass", (0.8, 0.85, 0.9, 1.0), 0.04,
                 transmission=0.95, alpha=0.35)


def volume_material(name, density=0.012):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for node in list(nt.nodes):
        if node.type == 'BSDF_PRINCIPLED':
            nt.nodes.remove(node)
    vol = nt.nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs["Density"].default_value = density
    vol.inputs["Color"].default_value = (0.70, 0.75, 0.80, 1.0)
    vol.inputs["Anisotropy"].default_value = 0.30
    out = next((n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'), None)
    if out is None:
        out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(vol.outputs[0], out.inputs["Volume"])
    return mat


VOL = volume_material("M_Z10_Volume", 0.010)


def new_box(name, size, loc, mat, bevel=0.0, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.rotation_euler = rot
    if bevel > 0.0:
        mod = ob.modifiers.new("Bevel", 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = 'ANGLE'
        select_only(ob)
        bpy.ops.object.modifier_apply(modifier=mod.name)
    ob.data.materials.append(mat)
    return ob


def new_cyl(name, radius, depth, loc, mat, axis='Z', segments=16,
            bevel=0.0, quat=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=segments, radius=radius,
                                        depth=depth, end_fill_type='NGON',
                                        location=loc)
    ob = bpy.context.object
    ob.name = name
    if quat is not None:
        ob.rotation_mode = 'QUATERNION'
        ob.rotation_quaternion = quat
    elif axis == 'X':
        ob.rotation_euler = (0.0, math.pi / 2.0, 0.0)
    elif axis == 'Y':
        ob.rotation_euler = (math.pi / 2.0, 0.0, 0.0)
    if bevel > 0.0:
        mod = ob.modifiers.new("Bevel", 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = 'ANGLE'
        select_only(ob)
        bpy.ops.object.modifier_apply(modifier=mod.name)
    ob.data.materials.append(mat)
    return ob


def new_cone(name, r1, r2, depth, loc, rot, mat, segments=24):
    bpy.ops.mesh.primitive_cone_add(vertices=segments, radius1=r1, radius2=r2,
                                    depth=depth, end_fill_type='NOTHING',
                                    location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(mat)
    return ob


def join_parts(parts, name):
    parts = [p for p in parts if p is not None]
    if not parts:
        return None
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    ob = bpy.context.object
    ob.name = name
    ob.data.name = name
    return ob


def source_center(src):
    pts = [src.matrix_world @ Vector(c) for c in src.bound_box]
    return sum(pts, Vector((0.0, 0.0, 0.0))) / 8.0


def dup_at(src_name, new_name, col, loc, rz=0.0, rx=0.0, ry=0.0, scale=1.0):
    src = bpy.data.objects.get(src_name)
    if src is None:
        print("MISSING_SOURCE", src_name)
        return None
    bpy.context.view_layer.update()
    center = source_center(src)
    ob = src.copy()
    ob.data = src.data
    ob.name = new_name
    col.objects.link(ob)
    ob.parent = None
    R = Euler((rx, ry, rz), 'XYZ').to_matrix().to_4x4()
    S = Matrix.Diagonal((scale, scale, scale, 1.0))
    ob.matrix_world = Matrix.Translation(loc) @ R @ S @ \
        Matrix.Translation(-center) @ src.matrix_world
    ob.hide_render = False
    ob.hide_viewport = False
    ob.hide_set(False)
    ob["fm_class"] = "DEBRIS"
    ob["fm_source"] = src_name
    return ob


def dup_on_floor(src_name, new_name, col, x, y, rz=0.0, rx=0.0, ry=0.0,
                 scale=1.0, floor_z=0.0):
    ob = dup_at(src_name, new_name, col, (x, y, 0.0), rz, rx, ry, scale)
    if ob is None:
        return None
    bpy.context.view_layer.update()
    zmin = min((ob.matrix_world @ v.co).z for v in ob.data.vertices)
    m = ob.matrix_world.copy()
    m.translation.z += floor_z - zmin
    ob.matrix_world = m
    bpy.context.view_layer.update()
    return ob


def make_worklight(col):
    base_loc = Vector((56.2, 9.6, 0.0))
    target = Vector((44.0, 9.6, 1.4))
    yaw = math.atan2(target.y - base_loc.y, target.x - base_loc.x)
    parts = []

    hub = Vector((0.0, 0.0, 0.98))
    for i, ang in enumerate((0.0, 120.0, 240.0)):
        a = math.radians(ang)
        foot = Vector((0.42 * math.cos(a), 0.42 * math.sin(a), 0.025))
        vec = foot - hub
        mid = (hub + foot) * 0.5
        quat = vec.to_track_quat('Z', 'Y')
        parts.append(new_cyl("WL_Leg_%d" % i, 0.018, vec.length, mid, DARK,
                             segments=12, quat=quat))
        parts.append(new_box("WL_Foot_%d" % i, (0.09, 0.09, 0.03),
                             (foot.x, foot.y, 0.015), RUB, bevel=0.004))
    parts.append(new_cyl("WL_Hub", 0.055, 0.10, (0, 0, 0.98), GALV,
                         segments=20, bevel=0.004))
    parts.append(new_cyl("WL_Pole", 0.024, 1.00, (0, 0, 1.48), GALV,
                         segments=16, bevel=0.003))
    parts.append(new_cyl("WL_PoleCollar", 0.034, 0.05, (0, 0, 1.98), DARK,
                         segments=16, bevel=0.003))

    head = Vector((0.12, 0.0, 1.98))
    parts.append(new_box("WL_Housing", (0.32, 0.24, 0.28),
                         (head.x, head.y, head.z), GALV, bevel=0.012))
    parts.append(new_box("WL_Back", (0.06, 0.20, 0.24),
                         (-0.06, 0.0, 1.98), DARK, bevel=0.008))
    parts.append(new_cone("WL_Reflector", 0.09, 0.17, 0.14,
                          (0.22, 0.0, 1.98), (0.0, math.pi / 2.0, 0.0), BARE))
    parts.append(new_cyl("WL_Lamp", 0.055, 0.018, (0.17, 0.0, 1.98), LAMP,
                         axis='X', segments=24))
    parts.append(new_box("WL_Glass", (0.006, 0.31, 0.23),
                         (0.296, 0.0, 1.98), GLASS, bevel=0.0))
    for i, yy in enumerate((-0.12, -0.06, 0.0, 0.06, 0.12)):
        parts.append(new_cyl("WL_CageV_%d" % i, 0.004, 0.25,
                             (0.305, yy, 1.98), BARE, segments=8))
    for i, zz in enumerate((1.865, 2.095)):
        parts.append(new_cyl("WL_CageH_%d" % i, 0.004, 0.28,
                             (0.305, 0.0, zz), BARE, axis='Y', segments=8))
    parts.append(new_cyl("WL_HandleTop", 0.012, 0.20, (0.05, 0.0, 2.20),
                         DARK, axis='X', segments=10))
    for i, xx in enumerate((-0.05, 0.15)):
        parts.append(new_cyl("WL_HandleV_%d" % i, 0.012, 0.12,
                             (xx, 0.0, 2.14), DARK, segments=10))
    for i, yy in enumerate((-0.15, 0.15)):
        parts.append(new_box("WL_Yoke_%d" % i, (0.10, 0.02, 0.20),
                             (-0.02, yy, 1.96), DARK, bevel=0.004))
    parts.append(new_cyl("WL_Pivot", 0.020, 0.34, (-0.02, 0.0, 1.96),
                         GALV, axis='Y', segments=12, bevel=0.002))
    parts.append(new_box("WL_SwitchBox", (0.10, 0.07, 0.12),
                         (0.0, 0.07, 1.30), DARK, bevel=0.005))
    parts.append(new_cyl("WL_Button", 0.015, 0.02, (0.0, 0.11, 1.33),
                         RED, axis='Y', segments=12))
    parts.append(new_box("WL_Label", (0.10, 0.002, 0.04),
                         (0.12, -0.125, 2.06), LABEL, bevel=0.0))

    curve = bpy.data.curves.new("WL_CableCurve", 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 2
    curve.bevel_depth = 0.006
    curve.bevel_resolution = 2
    spline = curve.splines.new('BEZIER')
    pts = [(0.29, 0.02, 1.92), (0.35, 0.12, 1.55),
           (0.28, 0.16, 0.85), (0.18, 0.10, 0.10),
           (0.30, -0.05, 0.02)]
    spline.bezier_points.add(len(pts) - 1)
    for bp, co in zip(spline.bezier_points, pts):
        bp.co = co
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    cable = bpy.data.objects.new("WL_Cable", curve)
    col.objects.link(cable)
    select_only(cable)
    bpy.ops.object.convert(target='MESH')
    cable = bpy.context.object
    cable.data.materials.append(RUB)
    parts.append(cable)

    ob = join_parts(parts, "PROP_Z10_WorkLight")
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    col.objects.link(ob)
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
    select_only(ob)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    ob.location = base_loc
    ob.rotation_euler = (0.0, 0.0, yaw)
    ob["fm_class"] = "PROP"
    ob["fm_hero"] = True
    ob["fm_family"] = "WORKLIGHT"
    return ob, base_loc, yaw, target


def add_light(name, kind, loc, energy, color, target=None, size=0.3,
              spot_size=55.0, spot_blend=0.2, col=None):
    data = bpy.data.lights.new(name, type=kind)
    data.energy = energy
    data.color = color
    if kind == 'SPOT':
        data.spot_size = math.radians(spot_size)
        data.spot_blend = spot_blend
    if hasattr(data, "shadow_soft_size"):
        data.shadow_soft_size = size
    data.use_shadow = True
    ob = bpy.data.objects.new(name, data)
    (col or LIGHT_COLL).objects.link(ob)
    ob.location = loc
    if target is not None:
        direction = Vector(target) - Vector(loc)
        ob.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return ob


def world_bbox(ob):
    pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    return (Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
            Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))))


def box_intersects(a_min, a_max, b_min, b_max):
    return not (a_max.x < b_min[0] or a_min.x > b_max[0] or
                a_max.y < b_min[1] or a_min.y > b_max[1] or
                a_max.z < b_min[2] or a_min.z > b_max[2])


def main():
    for ob in list(bpy.data.objects):
        if ob.name.startswith("PROP_Z10_WorkLight"):
            bpy.data.objects.remove(ob, do_unlink=True)
    col = collection(COLL)
    lcol = collection(LIGHT_COLL)
    acol = collection(ATMO)
    random.seed(7)

    work, base_loc, yaw, target = make_worklight(col)

    lum_src = bpy.data.objects.get("SM_SH_LUMINAIRE_1500_ON_LOD1")
    if lum_src is None:
        lum_src = bpy.data.objects.get("SM_SH_LUMINAIRE_1500_ON")
    bpy.context.view_layer.update()
    lum_center = source_center(lum_src)
    lum_specs = [((47.0, 14.0), 0.0), ((57.0, 14.0), 0.0),
                 ((52.0, 25.0), math.pi / 2.0)]
    for i, ((xx, yy), rot) in enumerate(lum_specs):
        ob = lum_src.copy()
        ob.data = lum_src.data
        ob.name = "LIGHT_Z10_Luminaire_%02d" % (i + 1)
        lcol.objects.link(ob)
        ob.parent = None
        ob.matrix_world = Matrix.Translation((xx, yy, 3.826)) @ \
            Euler((0, 0, rot), 'XYZ').to_matrix().to_4x4() @ \
            Matrix.Translation(-lum_center) @ lum_src.matrix_world
        ob.hide_render = False
        ob["fm_class"] = "LIGHT_FIXTURE"
        add_light("LIGHT_Z10_Point_%02d" % (i + 1), 'POINT',
                  (xx, yy, 3.64), 55.0, (0.78, 0.86, 1.0),
                  size=0.35, col=lcol)

    add_light("LIGHT_Z10_SouthSpill", 'POINT', (42.5, 9.2, 2.6),
              35.0, (0.35, 0.55, 1.0), size=0.5, col=lcol)

    head_world = base_loc + Euler((0, 0, yaw), 'XYZ').to_matrix() @ Vector((0.30, 0.0, 1.98))
    add_light("LIGHT_Z10_WorkSpot", 'SPOT', head_world, 260.0,
              (1.0, 0.78, 0.55), target=target, size=0.08,
              spot_size=45.0, spot_blend=0.25, col=lcol)
    add_light("LIGHT_Z10_WorkFill", 'POINT', head_world, 45.0,
              (1.0, 0.72, 0.42), size=0.12, col=lcol)

    dup_at("R21D_FIX_Emergency_Checkpoint", "DET_Z10_Emergency_E", col,
           (61.82, 22.0, 3.05), rz=math.radians(-90))
    add_light("LIGHT_Z10_Emergency_E", 'POINT', (61.5, 22.0, 3.00),
              10.0, (1.0, 0.02, 0.01), size=0.12, col=lcol)

    debris = [
        ("R21D_CableReel_Tipped", "DET_Z10_CableReel", 43.2, 10.2, 25),
        ("R21C_CHAOS_ChairA", "DET_Z10_Chair_A", 44.8, 10.7, 70),
        ("R21D_Pallet", "DET_Z10_Pallet", 42.2, 11.8, 8),
        ("R21C_CHAOS_ChunkA", "DET_Z10_Chunk_A", 43.6, 10.2, 0),
        ("R21C_CHAOS_ChunkB", "DET_Z10_Chunk_B", 42.8, 10.9, 35),
        ("R21C_CHAOS_ChunkC", "DET_Z10_Chunk_C", 44.4, 11.0, 80),
        ("R21D_Puddle_Checkpoint", "DET_Z10_Puddle_A", 43.4, 11.2, 12),
        ("R21D_Dust_0", "DET_Z10_Dust_A", 44.0, 11.2, 0),
        ("R21D_LockerDoor_FloorB", "DET_Z10_LockerDoor", 41.8, 27.6, 15),
        ("R21D_Chair_DraggedB", "DET_Z10_Chair_B", 43.8, 28.4, 110),
        ("R21C_CHAOS_CRT_A", "DET_Z10_CRT_A", 42.6, 28.9, 200),
        ("R21D_CeilingTile_FlatA", "DET_Z10_Tile_A", 41.6, 28.8, 30),
        ("R21D_CeilingTile_FlatB", "DET_Z10_Tile_B", 44.6, 27.8, 75),
        ("R21D_Puddle_Hole", "DET_Z10_Puddle_B", 43.0, 27.0, 0),
        ("R21D_DustHeavy_0", "DET_Z10_Dust_B", 42.5, 28.2, 0),
        ("R21D_CRT_Broken", "DET_Z10_CRT_B", 60.2, 12.0, 200),
        ("R21D_ElectricalCover", "DET_Z10_ElecCover", 60.6, 11.0, 30),
        ("R21D_ConduitBent", "DET_Z10_Conduit", 59.8, 13.2, 75),
        ("R21D_Debris_Metal_3", "DET_Z10_Metal_A", 59.4, 12.6, 20),
        ("R21D_Debris_Metal_5", "DET_Z10_Metal_B", 60.0, 13.8, 80),
        ("R21D_GlassPane_Broken", "DET_Z10_Glass", 60.4, 10.4, 45),
        ("R21D_Puddle_CheckpointWet", "DET_Z10_Puddle_C", 59.6, 12.4, 0),
        ("R21D_Chair_DraggedC", "DET_Z10_Chair_C", 59.0, 27.8, 160),
        ("R21D_Cone_Tipped", "DET_Z10_Cone_A", 60.2, 26.6, 60),
        ("R21D_Cone_Upright", "DET_Z10_Cone_B", 58.4, 28.8, 0),
        ("R21D_CeilingTile_FlatA", "DET_Z10_Tile_C", 60.0, 28.6, 12),
        ("R21D_Dust_1", "DET_Z10_Dust_C", 59.5, 27.0, 0),
    ]
    for src, name, xx, yy, rz in debris:
        floor = 0.012 if ("Puddle" in src or "Dust" in src) else 0.0
        dup_on_floor(src, name, col, xx, yy, rz=math.radians(rz), floor_z=floor)

    for i, (xx, yy) in enumerate(((45.5, 12.0), (46.0, 12.4), (44.8, 12.8),
                                  (47.0, 9.8), (57.0, 9.2), (58.0, 9.8),
                                  (56.5, 27.0), (57.2, 27.6), (45.0, 26.0),
                                  (44.0, 25.4), (49.0, 9.4), (52.0, 9.2),
                                  (60.0, 25.0), (59.0, 24.4))):
        new_box("PAPER_%02d" % i, (0.21, 0.297, 0.003),
                (xx, yy, 0.008), PAPER, bevel=0.0,
                rot=(0, 0, math.radians(random.uniform(0, 180))))
    papers = [o for o in col.objects if o.name.startswith("PAPER_")]
    papers_obj = join_parts(papers, "DET_Z10_Papers")
    if papers_obj:
        papers_obj["fm_class"] = "DEBRIS"
        papers_obj["fm_source"] = "PROCEDURAL_PAPERS"

    folder_parts = []
    for i, (xx, yy, rz) in enumerate(((56.8, 10.0, 20), (44.2, 26.2, 65))):
        folder_parts.append(new_box("FOLDER_%02d" % i, (0.24, 0.32, 0.008),
                                    (xx, yy, 0.010), MANILA, bevel=0.0,
                                    rot=(0, 0, math.radians(rz))))
    folders = join_parts(folder_parts, "DET_Z10_Folders")
    if folders:
        folders["fm_class"] = "DEBRIS"

    cb_body = new_box("CB_Body", (0.23, 0.32, 0.012), (57.4, 10.6, 0.010),
                      MANILA, bevel=0.002, rot=(0, 0, math.radians(35)))
    cb_clip = new_box("CB_Clip", (0.06, 0.02, 0.012), (57.4, 10.46, 0.018),
                      BARE, bevel=0.001, rot=(0, 0, math.radians(35)))
    clipboard = join_parts([cb_body, cb_clip], "DET_Z10_Clipboard")
    if clipboard:
        clipboard["fm_class"] = "DEBRIS"

    new_box("DET_Z10_CeilingHole", (0.62, 0.62, 0.002),
            (50.5, 24.5, 3.986), HOLE, bevel=0.0)
    dup_at("R21D_CeilingGrid_0", "DET_Z10_CeilingGrid", col,
           (50.5, 24.5, 3.95), rz=math.radians(15), rx=math.radians(8))
    dup_at("R21D_CeilingTile_HangingD", "DET_Z10_Tile_Hanging", col,
           (50.5, 24.5, 3.94), rz=math.radians(25), rx=math.radians(10))
    for src, name, xx, yy in (("R21D_Cable_HangA", "DET_Z10_Cable_A", 50.8, 24.2),
                              ("R21D_Cable_HangB", "DET_Z10_Cable_B", 53.0, 21.0),
                              ("R21D_Cable_HangC", "DET_Z10_Cable_C", 58.2, 29.4)):
        dup_on_floor(src, name, col, xx, yy, rz=0.0, floor_z=0.0)

    vol = new_box("VOL_Z10_Fog", (22.0, 22.0, 4.2), (51.0, 19.0, 2.1),
                  VOL, bevel=0.0)
    for c in list(vol.users_collection):
        c.objects.unlink(vol)
    acol.objects.link(vol)
    vol.hide_render = False
    vol.hide_set(True)

    bpy.context.view_layer.update()

    # Snap any floor prop whose evaluated bbox dips below z=0. Ceiling
    # grids, hanging tiles and cables are intentionally above the floor.
    hanging = {"DET_Z10_CeilingGrid", "DET_Z10_Tile_Hanging"}
    for ob in list(col.objects):
        if ob.type != 'MESH' or ob.name in hanging:
            continue
        zmin = min((ob.matrix_world @ Vector(c)).z for c in ob.bound_box)
        if zmin < -0.0005:
            m = ob.matrix_world.copy()
            m.translation.z += -zmin
            ob.matrix_world = m
            print("FLOOR_SNAP", ob.name, round(zmin, 4))

    bpy.context.view_layer.update()

    new_objs = [o for o in list(col.objects) + list(lcol.objects) + list(acol.objects)
                if o.type in {'MESH', 'LIGHT'}]
    total_tris = 0
    report = {}
    new_geo = []
    for ob in new_objs:
        if ob.type == 'MESH':
            me = ob.data
            me.calc_loop_triangles()
            bm = bmesh.new()
            bm.from_mesh(me)
            nonman = sum(1 for e in bm.edges if len(e.link_faces) > 2)
            deg = sum(1 for f in bm.faces if f.calc_area() < 1e-10)
            bm.free()
            tris = len(me.loop_triangles)
            total_tris += tris
            report[ob.name] = {
                "type": "MESH", "tris": tris, "verts": len(me.vertices),
                "non_manifold_edges": nonman, "degenerate_faces": deg,
                "uv": bool(me.uv_layers),
                "source": ob.get("fm_source", "NEW"),
                "bbox": [list(round(v, 4) for v in world_bbox(ob)[0]),
                         list(round(v, 4) for v in world_bbox(ob)[1])],
            }
            if ob.get("fm_source") in (None, "NEW", "PROCEDURAL_PAPERS"):
                new_geo.append(ob.name)
        else:
            report[ob.name] = {"type": ob.data.type,
                               "energy": round(ob.data.energy, 2),
                               "loc": [round(v, 3) for v in ob.location]}

    mn = Vector((1e9, 1e9, 1e9))
    mx = Vector((-1e9, -1e9, -1e9))
    for ob in new_objs:
        if ob.type != 'MESH':
            continue
        a, b = world_bbox(ob)
        mn.x = min(mn.x, a.x); mn.y = min(mn.y, a.y); mn.z = min(mn.z, a.z)
        mx.x = max(mx.x, b.x); mx.y = max(mx.y, b.y); mx.z = max(mx.z, b.z)

    outside = []
    for ob in new_objs:
        if ob.type != 'MESH':
            continue
        a, b = world_bbox(ob)
        if (a.x < 39.95 or b.x > 62.05 or a.y < 7.95 or b.y > 30.05 or
                a.z < -0.05 or b.z > 4.25):
            outside.append(ob.name)

    zones = {
        "south_portal": ((40.0, 8.0, 0.0), (46.0, 9.5, 4.2)),
        "east_portal": ((59.0, 18.0, 0.0), (62.0, 24.0, 2.9)),
        "north_portal": ((46.0, 28.0, 0.0), (52.0, 30.0, 4.2)),
    }
    conflicts = {}
    for zname, (zmin, zmax) in zones.items():
        hits = []
        for ob in new_objs:
            if ob.type != 'MESH' or ob.name.startswith("VOL_"):
                continue
            a, b = world_bbox(ob)
            if box_intersects(a, b, zmin, zmax):
                hits.append(ob.name)
        conflicts[zname] = hits

    out = {
        "collections": [COLL, LIGHT_COLL, ATMO],
        "object_count": len(new_objs),
        "mesh_count": sum(1 for o in new_objs if o.type == 'MESH'),
        "light_count": sum(1 for o in new_objs if o.type == 'LIGHT'),
        "total_tris_new": total_tris,
        "bbox_min": [round(v, 4) for v in mn],
        "bbox_max": [round(v, 4) for v in mx],
        "outside_room": outside,
        "portal_conflicts": conflicts,
        "new_geometry": new_geo,
        "objects": report,
    }
    os.makedirs(DOCS, exist_ok=True)
    with open(os.path.join(DOCS, "fm_z10_abandon_qa.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print("Z10_ABANDON_DONE", len(new_objs), total_tris,
          [round(v, 3) for v in mn], [round(v, 3) for v in mx])
    print("PORTAL_CONFLICTS", json.dumps(conflicts))


main()
