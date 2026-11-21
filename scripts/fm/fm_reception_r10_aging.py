import bpy
import bmesh
import json
import math
import os
import random
import shutil
import sys
from mathutils import Matrix, Vector

ROOT = "/home/riyo/Documentos/game"
BLEND = os.path.join(ROOT, "nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend")
BACKUP = os.path.join(ROOT, "docs/backups/FM_LEVEL1_V06_ARCH_before_reception_r10_aging.blend")
QA = os.path.join(ROOT, "docs/fm_reception_r10_aging_qa.json")
COL = "L1_RECEPTION_R10_AGING"
SCENE = bpy.data.scenes["NEXUS_L1_V06_ARCH"]
random.seed(1010)


def ensure_collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        SCENE.collection.children.link(col)
    return col


def clear_collection(col):
    for ob in list(col.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for child in list(col.children):
        bpy.data.collections.remove(child)


def principled(mat):
    return next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')


def simple_mat(name, color, rough=0.9, alpha=1.0, metallic=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = principled(mat)
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Alpha'].default_value = alpha
    try:
        mat.surface_render_method = 'DITHERED'
    except Exception:
        pass
    try:
        mat.blend_method = 'BLEND'
    except Exception:
        pass
    mat.use_backface_culling = False
    return mat


def mesh_from_pydata(name, verts, faces, mat):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate()
    me.update()
    ob = bpy.data.objects.new(name, me)
    COL_OBJ.objects.link(ob)
    ob.data.materials.append(mat)
    uv = me.uv_layers.new(name="MapaUV")
    for poly in me.polygons:
        for li in poly.loop_indices:
            vi = me.loops[li].vertex_index
            co = me.vertices[vi].co
            uv.data[li].uv = (co.x * 0.5, co.y * 0.5)
    ob["fm_class"] = "AGING_DECAL"
    ob["fm_generation"] = "VERIFIED_RECEPTION_R10"
    ob.visible_shadow = False
    return ob


def floor_patch(name, pts, z, mat):
    verts = [(x, y, z) for x, y in pts]
    faces = [list(range(len(verts)))]
    return mesh_from_pydata(name, verts, faces, mat)


def wall_patch(name, pts, axis, fixed, mat):
    if axis == 'X':
        verts = [(fixed, y, z) for y, z in pts]
    else:
        verts = [(x, fixed, z) for x, z in pts]
    faces = [list(range(len(verts)))]
    return mesh_from_pydata(name, verts, faces, mat)


def slab(name, center, size, rot_z, mat):
    cx, cy, cz = center
    sx, sy, sz = size
    corners = [
        (-sx / 2, -sy / 2, -sz / 2), (sx / 2, -sy / 2, -sz / 2),
        (sx / 2, sy / 2, -sz / 2), (-sx / 2, sy / 2, -sz / 2),
        (-sx / 2, -sy / 2, sz / 2), (sx / 2, -sy / 2, sz / 2),
        (sx / 2, sy / 2, sz / 2), (-sx / 2, sy / 2, sz / 2),
    ]
    rot = Matrix.Rotation(math.radians(rot_z), 3, 'Z')
    verts = [tuple(rot @ Vector(c) + Vector((cx, cy, cz))) for c in corners]
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    return mesh_from_pydata(name, verts, faces, mat)


def shared(src_name, new_name, target, rot_z=0.0, scale=1.0, rot_x=0.0):
    src = bpy.data.objects.get(src_name)
    if src is None or src.type != 'MESH':
        print("MISSING", src_name)
        return None
    new = bpy.data.objects.new(new_name, src.data)
    COL_OBJ.objects.link(new)
    new.scale = (scale, scale, scale)
    new.rotation_euler = (math.radians(rot_x), 0.0, math.radians(rot_z))
    corners = [Vector(c) * scale for c in src.bound_box]
    rm = Matrix.Rotation(math.radians(rot_x), 3, 'X') @ Matrix.Rotation(math.radians(rot_z), 3, 'Z')
    corners = [rm @ c for c in corners]
    mn = Vector((min(c.x for c in corners), min(c.y for c in corners), min(c.z for c in corners)))
    mx = Vector((max(c.x for c in corners), max(c.y for c in corners), max(c.z for c in corners)))
    center = (mn + mx) * 0.5
    new.location = (target[0] - center.x, target[1] - center.y, target[2] - mn.z)
    new["fm_class"] = "AGING_PROP"
    new["fm_generation"] = "VERIFIED_RECEPTION_R10"
    new["fm_source"] = src_name
    return new


def main():
    if not os.path.exists(BACKUP):
        shutil.copy2(BLEND, BACKUP)
        print("BACKUP", BACKUP)

    global COL_OBJ
    COL_OBJ = ensure_collection(COL)
    clear_collection(COL_OBJ)
    if COL_OBJ.name not in [c.name for c in SCENE.collection.children]:
        SCENE.collection.children.link(COL_OBJ)

    grime = simple_mat("M_REC10_Grime", (0.080, 0.085, 0.075), 0.95, 0.16)
    dust = simple_mat("M_REC10_Dust", (0.26, 0.24, 0.20), 1.0, 0.14)
    wet = simple_mat("M_REC10_Wet", (0.020, 0.030, 0.030), 0.08, 0.55)
    rust = simple_mat("M_REC10_Rust", (0.090, 0.035, 0.014), 0.92, 0.35)
    chip = simple_mat("M_REC10_Chip", (0.010, 0.011, 0.010), 0.8, 0.85)
    scuff = simple_mat("M_REC10_Scuff", (0.060, 0.065, 0.060), 0.90, 0.09)
    paper = simple_mat("M_REC10_Paper", (0.58, 0.55, 0.45), 0.92, 1.0)
    manila = simple_mat("M_REC10_Manila", (0.30, 0.19, 0.09), 0.9, 1.0)
    black = simple_mat("M_REC10_Black", (0.005, 0.006, 0.005), 0.65, 1.0)
    tape = simple_mat("M_REC10_TapeWorn", (0.35, 0.28, 0.08), 0.95, 0.55)

    # Bandas de suciedad adheridas a muros y esquinas.
    floor_patch("REC10_GRIME_W", [
        (-109.75, -39.3), (-108.65, -39.3), (-108.9, -35.8), (-108.7, -32.0),
        (-109.35, -28.2), (-108.8, -24.0), (-109.15, -20.2), (-108.65, -16.0),
        (-109.25, -12.0), (-108.55, -8.4), (-109.75, -8.4),
    ], 0.012, grime)
    floor_patch("REC10_GRIME_NW", [
        (-109.7, -8.45), (-109.7, -8.0), (-95.2, -8.0), (-95.5, -8.7),
        (-99.4, -9.0), (-103.6, -8.75), (-107.4, -8.7),
    ], 0.013, grime)
    floor_patch("REC10_GRIME_NE", [
        (-85.0, -8.0), (-70.4, -8.0), (-70.4, -8.55), (-76.0, -8.85),
        (-80.5, -8.7), (-84.0, -8.9),
    ], 0.013, grime)
    floor_patch("REC10_GRIME_E", [
        (-70.3, -39.4), (-70.3, -8.2), (-71.2, -8.2), (-71.0, -13.0),
        (-71.35, -18.0), (-70.9, -23.4), (-71.15, -29.0), (-70.85, -34.0),
        (-71.25, -39.4),
    ], 0.012, grime)
    floor_patch("REC10_GRIME_SW", [
        (-109.5, -39.95), (-96.2, -39.95), (-96.5, -39.25), (-101.0, -39.1),
        (-106.0, -39.3),
    ], 0.013, grime)
    floor_patch("REC10_GRIME_SE", [
        (-84.2, -39.95), (-70.4, -39.95), (-70.4, -39.1), (-75.0, -39.2),
        (-80.0, -39.0), (-83.2, -39.35),
    ], 0.013, grime)

    # Roces y marcas de arrastre en el recorrido.
    for i, pts in enumerate((
        [(-96.70, -12.30), (-96.40, -12.50), (-96.30, -19.20), (-96.60, -19.30)],
        [(-90.95, -14.00), (-90.65, -14.20), (-90.65, -22.00), (-90.95, -21.90)],
        [(-96.75, -24.90), (-96.55, -25.10), (-94.60, -31.00), (-94.80, -31.20)],
        [(-90.50, -26.00), (-90.20, -26.20), (-89.00, -33.20), (-89.30, -33.35)],
        [(-94.20, -10.45), (-93.90, -10.55), (-91.60, -10.75), (-91.55, -10.55)],
    )):
        floor_patch(f"REC10_SCUFF_{i:02d}", pts, 0.018, scuff)
    floor_patch("REC10_DRAG_WAIT", [
        (-106.2, -23.95), (-98.4, -23.55), (-98.35, -23.25), (-106.1, -23.65),
    ], 0.017, scuff)

    # Polvo acumulado bajo bancos, esquinas y columnas.
    floor_patch("REC10_DUST_BENCH", [
        (-109.55, -26.4), (-105.8, -26.2), (-105.5, -18.4), (-109.5, -18.2),
        (-109.65, -21.0),
    ], 0.011, dust)
    floor_patch("REC10_DUST_WCORNER", [
        (-109.7, -27.2), (-104.3, -27.4), (-105.2, -25.2), (-109.5, -25.0),
    ], 0.011, dust)
    for i, (cx, cy) in enumerate(((-90.0, -20.0), (-90.0, -32.0), (-80.0, -32.0))):
        pts = []
        for k in range(9):
            a = 2 * math.pi * k / 8
            r = 0.85 + 0.15 * ((k * 7) % 5) / 5.0
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        floor_patch(f"REC10_DUST_COL_{i}", pts, 0.0105, dust)
    floor_patch("REC10_DUST_ECORNER", [
        (-73.0, -36.8), (-70.4, -37.2), (-70.4, -39.7), (-75.8, -39.6),
        (-75.0, -37.4),
    ], 0.011, dust)

    # Manchas de agua y humedad.
    for i, (cx, cy, r) in enumerate(((-99.1, -10.2, 0.9), (-86.9, -16.1, 0.75))):
        pts = []
        for k in range(10):
            a = 2 * math.pi * k / 10
            rr = r * (0.8 + 0.25 * ((k * 3) % 5) / 5.0)
            pts.append((cx + rr * math.cos(a), cy + rr * 0.72 * math.sin(a)))
        floor_patch(f"REC10_WET_RING_{i}", pts, 0.014, wet)

    # Chips de pintura en el zócalo y el frente del mostrador.
    for i, (x, y, z) in enumerate((
        (-103.4, -8.14, 0.55), (-99.7, -8.14, 0.92), (-78.2, -8.14, 0.48),
        (-73.9, -8.14, 0.98), (-109.86, -21.2, 0.62), (-109.86, -31.1, 1.02),
        (-39.84, -0.1, 0.0),
    )):
        if i == 6:
            continue
        pts = [(x - 0.12, z - 0.04), (x + 0.08, z - 0.02), (x + 0.14, z + 0.05), (x - 0.03, z + 0.06)]
        wall_patch(f"REC10_CHIP_{i:02d}", pts, 'Y', y, chip)
    for i, (x, y, z) in enumerate(((-102.6, -12.54, 0.11), (-100.5, -12.54, 0.16), (-103.85, -12.54, 0.08))):
        wall_patch(f"REC10_DESK_CHIP_{i}", [
            (x - 0.08, z - 0.025), (x + 0.06, z - 0.015), (x + 0.09, z + 0.02), (x - 0.04, z + 0.03),
        ], 'Y', -12.545, chip)

    # Estrías de óxido bajo servicios y en muros.
    wall_patch("REC10_RUST_E", [
        (-14.4, 4.55), (-13.95, 4.55), (-14.05, 3.65), (-14.18, 3.2), (-14.35, 3.7),
    ], 'X', -70.145, rust)
    wall_patch("REC10_RUST_W", [
        (-30.3, 4.45), (-29.9, 4.45), (-30.0, 3.7), (-30.18, 3.35), (-30.32, 3.8),
    ], 'X', -109.855, rust)

    # Manchas de techo y goteo sobre el soffit.
    for i, (cx, cy, sx, sy) in enumerate(((-99.6, -18.2, 2.2, 1.35), (-88.0, -27.2, 1.35, 1.0))):
        pts = []
        for k in range(9):
            a = 2 * math.pi * k / 9
            rr = 0.75 + 0.25 * ((k * 5) % 7) / 7.0
            pts.append((cx + sx * rr * math.cos(a), cy + sy * rr * math.sin(a)))
        floor_patch(f"REC10_CEIL_STAIN_{i}", pts, 5.192, wet)
    floor_patch("REC10_SOFFIT_STAIN", [
        (-101.8, -10.48), (-99.2, -10.48), (-99.4, -10.46), (-101.6, -10.46),
    ], 4.55, rust)

    # Cinta de peligro desgastada.
    for i, pts in enumerate((
        [(-97.02, -12.8), (-96.84, -12.82), (-96.8, -13.5), (-96.98, -13.45)],
        [(-91.18, -20.8), (-91.0, -20.9), (-91.02, -21.6), (-91.2, -21.55)],
        [(-97.0, -31.2), (-96.82, -31.3), (-96.84, -32.1), (-97.02, -32.0)],
    )):
        floor_patch(f"REC10_TAPE_{i}", pts, 0.019, tape)

    # Papeles y carpetas.
    papers = [
        (-103.8, -12.12, 12), (-102.9, -11.94, -8), (-101.6, -12.03, 35),
        (-100.8, -11.83, -22), (-102.2, -11.6, 8), (-101.2, -12.22, 18),
        (-89.8, -14.2, 44), (-88.7, -14.6, -12), (-87.2, -15.0, 21),
        (-86.4, -14.5, -30), (-107.8, -20.2, 15), (-107.2, -21.1, -6),
        (-106.5, -23.0, 27), (-107.9, -24.6, 55),
    ]
    for i, (x, y, rz) in enumerate(papers):
        slab(f"REC10_PAPER_{i:02d}", (x, y, 0.009), (0.21, 0.297, 0.0015), rz, paper)
    slab("REC10_FOLDER_TABLE", (-107.25, -22.0, 0.460), (0.24, 0.32, 0.006), 14, manila)
    slab("REC10_FOLDER_TAB", (-107.16, -21.9, 0.466), (0.08, 0.10, 0.003), 14, manila)
    slab("REC10_CLIPBOARD", (-107.25, -21.65, 0.463), (0.23, 0.31, 0.008), -19, manila)
    slab("REC10_CLIP", (-107.25, -21.65, 0.472), (0.09, 0.035, 0.006), -19, black)
    slab("REC10_FOLDER_FLOOR", (-106.9, -24.3, 0.009), (0.24, 0.32, 0.005), 37, manila)

    # Escombros pequeños reutilizados de la biblioteca.
    debris = [
        ("DET_HERO_SEC_Debris_Concrete_0", (-108.2, -16.2, 0.0), 18, 1.0),
        ("DET_HERO_SEC_Debris_Concrete_3", (-107.7, -25.8, 0.0), -35, 1.0),
        ("DET_HERO_SEC_Debris_Concrete_5", (-101.3, -8.95, 0.0), 62, 0.9),
        ("DET_HERO_SEC_Debris_Concrete_1", (-74.2, -12.4, 0.0), 24, 0.85),
        ("DET_HERO_SEC_Debris_Concrete_4", (-75.6, -30.1, 0.0), -12, 0.95),
        ("DET_HERO_SEC_Debris_MetalScrap_0", (-84.7, -9.1, 0.0), 41, 1.0),
        ("DET_HERO_SEC_Debris_MetalScrap_1", (-86.2, -15.7, 0.0), -21, 0.9),
        ("R21D_Cone_Tipped", (-97.7, -35.2, 0.0), 72, 1.0),
        ("R21D_CeilingTile_FlatA", (-107.7, -18.2, 0.012), 17, 1.0),
        ("R21D_CeilingGrid_0", (-108.0, -18.8, 0.012), -11, 0.95),
        ("R21D_ReelCable", (-71.4, -16.2, 0.0), 30, 1.0),
    ]
    for src, target, rz, sc in debris:
        name = src.replace("DET_HERO_SEC_", "REC10_").replace("R21D_", "REC10_")
        ob = shared(src, name, target, rz, sc)
        if ob is not None:
            ob["fm_family"] = "DEBRIS"

    # Puddles con la malla de la biblioteca.
    for i, (src, target, rz) in enumerate((
        ("DET_HERO_SEC_Puddle_Secondary", (-99.1, -10.2, 0.014), -20),
        ("DET_HERO_SEC_Puddle_Secondary", (-86.9, -16.1, 0.014), 45),
    )):
        ob = shared(src, f"REC10_PUDDLE_{i}", target, rz, 1.0)
        if ob is not None:
            ob["fm_family"] = "PUDDLE"

    # Suciedad de contacto en losas del techo.
    for i, (cx, cy) in enumerate(((-100.0, -16.0), (-88.0, -24.0), (-76.0, -12.5))):
        pts = []
        for k in range(9):
            a = 2 * math.pi * k / 9
            rr = 0.45 + 0.10 * ((k * 4) % 5) / 5.0
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        floor_patch(f"REC10_CEIL_DUST_{i}", pts, 5.19, dust)

    bpy.context.view_layer.update()
    objs = [o for o in COL_OBJ.all_objects if o is not None]
    meshes = [o for o in objs if o.type == 'MESH']
    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in meshes)
    decals = [o for o in meshes if o.get("fm_class") == "AGING_DECAL"]
    props = [o for o in meshes if o.get("fm_class") == "AGING_PROP"]

    pts = []
    for o in meshes:
        pts += [o.matrix_world @ v.co for v in o.data.vertices]
    mn = [min(p[i] for p in pts) for i in range(3)]
    mx = [max(p[i] for p in pts) for i in range(3)]
    inside = (mn[0] >= -110.3 and mx[0] <= -69.7 and
              mn[1] >= -40.3 and mx[1] <= -7.7 and
              mn[2] >= -0.02 and mx[2] <= 5.25)

    conflicts = []
    for o in props:
        pts = [o.matrix_world @ v.co for v in o.data.vertices]
        x0 = min(p.x for p in pts); x1 = max(p.x for p in pts)
        y0 = min(p.y for p in pts); y1 = max(p.y for p in pts)
        z1 = max(p.z for p in pts)
        if x1 > -96.8 and x0 < -91.2 and y1 > -33.0 and y0 < -8.5 and z1 > 0.05:
            conflicts.append(o.name)

    report = {
        "collection": COL,
        "objects": len(objs),
        "meshes": len(meshes),
        "tris": tris,
        "decals": len(decals),
        "props": len(props),
        "shared_meshes": sum(1 for o in meshes if o.data.users >= 2),
        "materials": sorted({m.name for o in meshes for m in o.data.materials if m}),
        "aabb": [mn, mx],
        "inside_reception": inside,
        "walkway_conflicts": conflicts,
        "qa_pass": inside and not conflicts,
        "notes": "Desgaste ambiental de Recepción: suciedad perimetral, roces, polvo, chips, óxido, manchas de techo, papeles y escombros. No toca arquitectura, hero clusters ni el recorrido central.",
    }
    with open(QA, "w") as fh:
        json.dump(report, fh, indent=2)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("REC10_AGING_DONE", json.dumps(report, indent=2))


main()
