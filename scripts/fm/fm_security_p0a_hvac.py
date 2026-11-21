import bpy
import bmesh
import json
import math
import os
import sys
from mathutils import Matrix

ROOT = "/home/riyo/Documentos/game"
BLEND = os.path.join(ROOT, "nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend")
BACKUP = os.path.join(ROOT, "docs/backups/FM_LEVEL1_V06_ARCH_before_security_p0a_hvac.blend")
QA = os.path.join(ROOT, "docs/fm_security_p0a_hvac_qa.json")
sys.path.insert(0, os.path.join(ROOT, "scripts/fm"))
from fm_shared_p0_lib import box, cyl, join_group, ensure_materials

M = ensure_materials()
HCOL = bpy.data.collections.get("L1_SECURITY_P0A_HERO")
RCOL = bpy.data.collections.get("L1_SECURITY_RETIRED_P0A")
if HCOL is None:
    HCOL = bpy.data.collections.new("L1_SECURITY_P0A_HERO")
    bpy.context.scene.collection.children.link(HCOL)
if RCOL is None:
    RCOL = bpy.data.collections.new("L1_SECURITY_RETIRED_P0A")
    bpy.context.scene.collection.children.link(RCOL)


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


def copy_mesh(src_name, name, matrix):
    src = bpy.data.objects.get(src_name)
    if src is None or src.type != 'MESH':
        raise RuntimeError("missing source " + src_name)
    ob = bpy.data.objects.new(name, src.data)
    HCOL.objects.link(ob)
    ob.parent = None
    ob.matrix_world = matrix
    ob["fm_generation"] = "VERIFIED_SECURITY_P0A"
    ob["fm_source_master"] = src_name
    return ob


def cut_duct():
    src = bpy.data.objects.get("P0B_HVAC_RUN_800x600")
    if src is None:
        raise RuntimeError("P0B_HVAC_RUN_800x600 missing")
    me = src.data.copy()
    me.name = "SEC_P0A_HVAC_RUN_MESH"
    bm = bmesh.new()
    bm.from_mesh(me)
    geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
    bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-6, plane_co=(26.0, 0, 0), plane_no=(1, 0, 0), clear_outer=True)
    bm.edges.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    cap_edges = []
    for e in bm.edges:
        if not e.is_boundary:
            continue
        xs = [v.co.x for v in e.verts]
        if all(x < 0.05 for x in xs) or all(x > 25.95 for x in xs):
            cap_edges.append(e)
    if cap_edges:
        bmesh.ops.holes_fill(bm, edges=cap_edges, sides=0)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("SEC_P0A_HVAC_RUN", me)
    HCOL.objects.link(ob)
    ob.matrix_world = Matrix.Translation((-97.2, 10.0, 3.55)) @ Matrix.Rotation(math.radians(90), 4, 'Z')
    ob["fm_generation"] = "VERIFIED_SECURITY_P0A"
    ob["fm_source_master"] = "P0B_HVAC_RUN_800x600"
    return ob


def build_supports():
    parts = []
    for y in (12.0, 16.0, 20.0, 24.0, 28.0, 34.0):
        for x in (-97.55, -96.85):
            parts.append(cyl(HCOL, "SEC_P0A_HVAC_ROD", 0.008, 0.82, (x, y, 4.27), M["steel_dark"], axis='Z', seg=10))
            parts.append(box(HCOL, "SEC_P0A_HVAC_PLATE", 0.10, 0.10, 0.012, (x, y, 4.68), M["galv"], bevel=0.001, seg=1))
        parts.append(box(HCOL, "SEC_P0A_HVAC_CROSS", 0.82, 0.05, 0.05, (-97.2, y, 3.86), M["galv"], bevel=0.002, seg=2))
        parts.append(box(HCOL, "SEC_P0A_HVAC_CLEAT", 0.86, 0.035, 0.035, (-97.2, y, 3.84), M["steel_dark"], bevel=0.001, seg=1))
        for x in (-97.52, -96.88):
            parts.append(cyl(HCOL, "SEC_P0A_HVAC_BOLT", 0.006, 0.02, (x, y, 3.875), M["steel_bare"], axis='Z', seg=8))
    return join_group(HCOL, "SEC_P0A_HVAC_SUPPORTS", parts, uv=True, wn=True)


def build_sleeves():
    out = []
    for y in (10.0, 36.0):
        out.append(copy_mesh("SM_SH_SLEEVE_RECT_800x600", "SEC_P0A_HVAC_SLEEVE_%s" % ("S" if y < 20 else "N"),
                             Matrix.Translation((-97.2, y, 3.55)) @ Matrix.Rotation(math.radians(90), 4, 'Z')))
    return out


def build_dampers():
    out = []
    for y in (10.55, 35.45):
        out.append(copy_mesh("SM_SH_FIREDAMPER_800x600", "SEC_P0A_HVAC_FIREDAMPER_%s" % ("S" if y < 20 else "N"),
                             Matrix.Translation((-97.2, y, 3.55)) @ Matrix.Rotation(math.radians(90), 4, 'Z')))
    return out


def build_grilles():
    out = []
    for y in (14.0, 20.0, 26.0, 32.0):
        out.append(copy_mesh("SM_SH_HVAC_GRILLE_600x400", "SEC_P0A_HVAC_GRILLE_%02d" % int(y),
                             Matrix.Translation((-97.2, y, 3.25)) @ Matrix.Rotation(math.radians(90), 4, 'Y')))
    return out


def main():
    if not os.path.exists(BACKUP):
        bpy.ops.wm.save_as_mainfile(filepath=BLEND)
        import shutil
        shutil.copy2(BLEND, BACKUP)

    remove_existing("SEC_P0A_HVAC_")
    old = bpy.data.objects.get("R21B_SERV_HVACDuct")
    if old is not None:
        for c in list(old.users_collection):
            c.objects.unlink(old)
        RCOL.objects.link(old)
        old.hide_render = True
        old.hide_viewport = True
        old.hide_set(True)

    run = cut_duct()
    supports = build_supports()
    sleeves = build_sleeves()
    dampers = build_dampers()
    grilles = build_grilles()
    bpy.context.view_layer.update()

    new = [run, supports] + sleeves + dampers + grilles
    stats = [qa_obj(o) for o in new]
    qa_pass = all(s["nonmanifold"] == 0 and s["degenerate"] == 0 and s["uv"] for s in stats)
    report = {
        "collection": HCOL.name,
        "retired": [] if old is None else [old.name],
        "objects": len(new),
        "tris": sum(s["tris"] for s in stats),
        "verts": sum(s["verts"] for s in stats),
        "qa_pass": qa_pass,
        "stats": stats,
        "bounds": [
            [round(min((o.matrix_world @ __import__('mathutils').Vector(c)).x for c in o.bound_box), 3) for o in new],
            [round(min((o.matrix_world @ __import__('mathutils').Vector(c)).y for c in o.bound_box), 3) for o in new],
            [round(min((o.matrix_world @ __import__('mathutils').Vector(c)).z for c in o.bound_box), 3) for o in new],
        ],
    }
    # Simple overall AABB for readability.
    pts = []
    for o in new:
        pts += [o.matrix_world @ __import__('mathutils').Vector(c) for c in o.bound_box]
    report["aabb"] = [[round(min(p[i] for p in pts), 3) for i in range(3)],
                      [round(max(p[i] for p in pts), 3) for i in range(3)]]
    with open(QA, "w") as fh:
        json.dump(report, fh, indent=2)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("SEC_P0A_HVAC_DONE", json.dumps({"objects": len(new), "tris": report["tris"], "qa_pass": qa_pass, "aabb": report["aabb"]}))


main()
