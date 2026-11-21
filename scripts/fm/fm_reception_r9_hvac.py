import bpy
import bmesh
import json
import math
import os
import shutil
import sys
from mathutils import Matrix, Vector

ROOT = "/home/riyo/Documentos/game"
BLEND = os.path.join(ROOT, "nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend")
BACKUP = os.path.join(ROOT, "docs/backups/FM_LEVEL1_V06_ARCH_before_reception_r9_hvac.blend")
QA = os.path.join(ROOT, "docs/fm_reception_r9_hvac_qa.json")
sys.path.insert(0, os.path.join(ROOT, "scripts/fm"))
from fm_shared_p0_lib import box, cyl, join_group, ensure_materials

M = ensure_materials()
SC = bpy.data.scenes["NEXUS_L1_V06_ARCH"]
HCOL = bpy.data.collections.get("L1_RECEPTION_R9_HERO")
RCOL = bpy.data.collections.get("L1_RECEPTION_RETIRED_R9")
if HCOL is None:
    HCOL = bpy.data.collections.new("L1_RECEPTION_R9_HERO")
    SC.collection.children.link(HCOL)
if RCOL is None:
    RCOL = bpy.data.collections.new("L1_RECEPTION_RETIRED_R9")
    SC.collection.children.link(RCOL)

MAIN_Y = -14.0
MAIN_Z = 4.5
MAIN_X0 = -110.0
MAIN_X1 = -70.0
MAIN_LEN = MAIN_X1 - MAIN_X0
BRANCH_X = -88.0
BRANCH_Y0 = -14.0
BRANCH_LEN = 10.6
BRANCH_Z = 4.5


def remove_existing(prefix):
    for ob in list(HCOL.objects):
        if ob.name.startswith(prefix):
            bpy.data.objects.remove(ob, do_unlink=True)


def tri_count(ob):
    return sum(max(0, len(p.vertices) - 2) for p in ob.data.polygons)


def uv_ok(ob):
    return bool(ob.data.uv_layers)


def qa_obj(ob):
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    nonman = sum(1 for e in bm.edges if not e.is_manifold)
    deg = sum(1 for f in bm.faces if f.calc_area() < 1e-10)
    bm.free()
    return {"name": ob.name, "tris": tri_count(ob), "verts": len(me.vertices),
            "nonmanifold": nonman, "degenerate": deg, "uv": uv_ok(ob)}


def link_copy(src_name, name, matrix, mesh=None):
    src = bpy.data.objects.get(src_name)
    if src is None or src.type != 'MESH':
        raise RuntimeError("missing source " + src_name)
    ob = bpy.data.objects.new(name, mesh if mesh is not None else src.data)
    HCOL.objects.link(ob)
    ob.parent = None
    ob.matrix_world = matrix
    ob["fm_generation"] = "VERIFIED_RECEPTION_R9"
    ob["fm_source_master"] = src_name
    return ob


def cut_main():
    src = bpy.data.objects.get("P0B_HVAC_RUN_800x600")
    if src is None:
        raise RuntimeError("P0B_HVAC_RUN_800x600 missing")
    me = src.data.copy()
    me.name = "REC09_HVAC_MAIN_MESH"
    bm = bmesh.new()
    bm.from_mesh(me)
    edge_geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
    bmesh.ops.bisect_plane(bm, geom=edge_geom, dist=1e-6,
                           plane_co=(MAIN_LEN, 0, 0), plane_no=(1, 0, 0),
                           clear_outer=True)
    bm.edges.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    cap_edges = []
    for e in bm.edges:
        if not e.is_boundary:
            continue
        xs = [v.co.x for v in e.verts]
        if all(x < 0.05 for x in xs) or all(x > MAIN_LEN - 0.05 for x in xs):
            cap_edges.append(e)
    if cap_edges:
        bmesh.ops.holes_fill(bm, edges=cap_edges, sides=0)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("REC09_HVAC_MAIN", me)
    HCOL.objects.link(ob)
    ob.matrix_world = Matrix.Translation((MAIN_X0, MAIN_Y, MAIN_Z))
    ob["fm_generation"] = "VERIFIED_RECEPTION_R9"
    ob["fm_source_master"] = "P0B_HVAC_RUN_800x600"
    return ob


def build_branch():
    out = []
    trans_rot = Matrix.Rotation(math.radians(-90), 4, 'Z')
    out.append(link_copy("SM_SH_HVAC_TRANS_800x600_600x400", "REC09_HVAC_TRANSITION",
                         Matrix.Translation((BRANCH_X, BRANCH_Y0, BRANCH_Z)) @ trans_rot))
    src = bpy.data.objects.get("SM_SH_HVAC_RECT600x400_L2000")
    if src is None:
        raise RuntimeError("600x400 module missing")
    for i in range(5):
        y = BRANCH_Y0 - 0.6 - 2.0 * i
        out.append(link_copy("SM_SH_HVAC_RECT600x400_L2000", "REC09_HVAC_BRANCH_%02d" % i,
                             Matrix.Translation((BRANCH_X, y, BRANCH_Z)) @ trans_rot,
                             mesh=src.data))
    # End cap and bolts as one UV-mapped assembly.
    cap_y = BRANCH_Y0 - 0.6 - 10.0
    end_parts = [box(HCOL, "REC09_HVAC_BRANCH_CAP", 0.62, 0.02, 0.42,
                     (BRANCH_X, cap_y - 0.011, BRANCH_Z), M["galv"], bevel=0.002, seg=2)]
    for dx, dz in ((-0.24, -0.15), (-0.24, 0.15), (0.24, -0.15), (0.24, 0.15)):
        end_parts.append(cyl(HCOL, "REC09_HVAC_BRANCH_BOLT", 0.007, 0.018,
                             (BRANCH_X + dx, cap_y - 0.024, BRANCH_Z + dz),
                             M["steel_bare"], axis='Y', seg=8))
    out.append(join_group(HCOL, "REC09_HVAC_BRANCH_END", end_parts, uv=True, wn=True))
    return out


def build_main_grilles():
    out = []
    # Point down and keep the 0.6 m side along X (the duct axis).
    rot = Matrix.Rotation(math.radians(90), 4, 'Z') @ Matrix.Rotation(math.radians(90), 4, 'Y')
    for x in (-100.0, -94.0, -80.0, -72.0):
        out.append(link_copy("SM_SH_HVAC_GRILLE_600x400", "REC09_HVAC_GRILLE_MAIN_%s" % int(abs(x)),
                             Matrix.Translation((x, MAIN_Y, 4.18)) @ rot))
    return out


def build_branch_grilles():
    out = []
    rot = Matrix.Rotation(math.radians(90), 4, 'Z') @ Matrix.Rotation(math.radians(90), 4, 'Y')
    for i, y in enumerate((-17.0, -20.6, -23.4)):
        out.append(link_copy("SM_SH_HVAC_GRILLE_600x400", "REC09_HVAC_GRILLE_BRANCH_%02d" % i,
                             Matrix.Translation((BRANCH_X, y, 4.18)) @ rot))
    return out


def build_supports():
    parts = []
    # Main duct trapeze supports, every 4.8 m.
    for x in (-106.0, -100.8, -95.6, -90.4, -85.2, -81.5, -74.8, -71.2):
        for y in (MAIN_Y - 0.50, MAIN_Y + 0.50):
            parts.append(cyl(HCOL, "REC09_HVAC_ROD", 0.008, 0.34, (x, y, 5.02),
                             M["steel_dark"], axis='Z', seg=10))
            parts.append(box(HCOL, "REC09_HVAC_PLATE", 0.10, 0.10, 0.012, (x, y, 5.19),
                             M["galv"], bevel=0.001, seg=1))
        parts.append(box(HCOL, "REC09_HVAC_CROSS", 0.05, 1.10, 0.05, (x, MAIN_Y, 4.17),
                         M["galv"], bevel=0.002, seg=2))
        parts.append(box(HCOL, "REC09_HVAC_CLEAT", 0.035, 0.86, 0.035, (x, MAIN_Y, 4.15),
                         M["steel_dark"], bevel=0.001, seg=1))
        for y in (MAIN_Y - 0.35, MAIN_Y + 0.35):
            parts.append(cyl(HCOL, "REC09_HVAC_BOLT", 0.006, 0.02, (x, y, 4.19),
                             M["steel_bare"], axis='Z', seg=8))
    # Branch supports at y -18.0 and -23.0.
    for y in (-18.0, -23.0):
        for x in (BRANCH_X - 0.35, BRANCH_X + 0.35):
            parts.append(cyl(HCOL, "REC09_HVAC_BROD", 0.008, 0.45, (x, y, 4.97),
                             M["steel_dark"], axis='Z', seg=10))
            parts.append(box(HCOL, "REC09_HVAC_BPLATE", 0.10, 0.10, 0.012, (x, y, 5.19),
                             M["galv"], bevel=0.001, seg=1))
        parts.append(box(HCOL, "REC09_HVAC_BCROSS", 0.82, 0.05, 0.05, (BRANCH_X, y, 4.27),
                         M["galv"], bevel=0.002, seg=2))
        parts.append(box(HCOL, "REC09_HVAC_BCLEAT", 0.62, 0.035, 0.035, (BRANCH_X, y, 4.25),
                         M["steel_dark"], bevel=0.001, seg=1))
        for x in (BRANCH_X - 0.25, BRANCH_X + 0.25):
            parts.append(cyl(HCOL, "REC09_HVAC_BBOLT", 0.006, 0.02, (x, y, 4.29),
                             M["steel_bare"], axis='Z', seg=8))
    return join_group(HCOL, "REC09_HVAC_SUPPORTS", parts, uv=True, wn=True)


def build_sleeves_and_dampers():
    out = []
    for x, tag in ((MAIN_X0, "W"), (MAIN_X1, "E")):
        out.append(link_copy("SM_SH_SLEEVE_RECT_800x600", "REC09_HVAC_SLEEVE_%s" % tag,
                             Matrix.Translation((x, MAIN_Y, MAIN_Z))))
    for x, tag in ((MAIN_X0 + 0.55, "W"), (MAIN_X1 - 0.55, "E")):
        out.append(link_copy("SM_SH_FIREDAMPER_800x600", "REC09_HVAC_FIREDAMPER_%s" % tag,
                             Matrix.Translation((x, MAIN_Y, MAIN_Z))))
    return out


def retire_old():
    retired = []
    for ob in list(bpy.data.objects):
        if ob is None:
            continue
        if not ob.name.startswith("KIT_REC01_HVAC_"):
            continue
        if ob.name in [o.name for o in HCOL.objects]:
            continue
        for c in list(ob.users_collection):
            c.objects.unlink(ob)
        RCOL.objects.link(ob)
        ob.hide_render = True
        ob.hide_viewport = True
        ob.hide_set(True)
        retired.append(ob.name)
    return retired


def main():
    if not os.path.exists(BACKUP):
        bpy.ops.wm.save_as_mainfile(filepath=BLEND)
        shutil.copy2(BLEND, BACKUP)

    remove_existing("REC09_HVAC_")
    retired = retire_old()

    main_run = cut_main()
    branch = build_branch()
    sleeves = build_sleeves_and_dampers()
    grilles = build_main_grilles() + build_branch_grilles()
    supports = build_supports()
    bpy.context.view_layer.update()

    new = [main_run] + branch + sleeves + grilles + [supports]
    stats = [qa_obj(o) for o in new]
    pts = []
    for o in new:
        pts += [o.matrix_world @ Vector(c) for c in o.bound_box]
    aabb = [[round(min(p[i] for p in pts), 3) for i in range(3)],
            [round(max(p[i] for p in pts), 3) for i in range(3)]]
    inside = (aabb[0][0] >= -111.0 and aabb[1][0] <= -69.0 and
              aabb[0][1] >= -41.0 and aabb[1][1] <= -7.0 and
              aabb[0][2] >= -0.5 and aabb[1][2] <= 5.5)
    retired_visible = [n for n in retired if not bpy.data.objects[n].hide_render]
    qa_pass = all(s["nonmanifold"] == 0 and s["degenerate"] == 0 and s["uv"] for s in stats)
    report = {
        "collection": HCOL.name,
        "retired_collection": RCOL.name,
        "retired": retired,
        "retired_visible": retired_visible,
        "objects": len(new),
        "tris": sum(s["tris"] for s in stats),
        "verts": sum(s["verts"] for s in stats),
        "qa_pass": qa_pass,
        "inside": inside,
        "aabb": aabb,
        "stats": stats,
        "limits": [
            "No se conecta al ramal del corredor: termina en sleeve/fire damper.",
            "No se construyen patinillos; decision pendiente del usuario.",
            "Sin retorno HVAC; solo suministro.",
        ],
    }
    with open(QA, "w") as fh:
        json.dump(report, fh, indent=2)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("REC09_HVAC_DONE", json.dumps({"objects": len(new), "tris": report["tris"],
                                         "qa_pass": qa_pass, "inside": inside,
                                         "aabb": aabb, "retired": len(retired)}))


main()
