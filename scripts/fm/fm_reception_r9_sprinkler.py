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
BACKUP = os.path.join(ROOT, "docs/backups/FM_LEVEL1_V06_ARCH_before_reception_r9_sprinkler.blend")
QA = os.path.join(ROOT, "docs/fm_reception_r9_sprinkler_qa.json")
sys.path.insert(0, os.path.join(ROOT, "scripts/fm"))
from fm_shared_p0_lib import box, cyl, join_group  # noqa: E402

SCENE = bpy.data.scenes["NEXUS_L1_V06_ARCH"]
HERO = "L1_RECEPTION_R9_HERO"
RETIRED = "L1_RECEPTION_RETIRED_R9"
PIPE_Z = 4.60
PIPE_Y = -30.0
X0, X1 = -110.0, -70.0
HEAD_X = [-106.0, -102.0, -96.0, -92.0, -86.0, -82.0, -76.0, -72.0]
SUPPORT_X = [-108.0, -104.0, -98.0, -94.0, -88.0, -84.0, -78.0, -74.0]


def col(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        SCENE.collection.children.link(c)
    return c


def relink(ob, target):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    target.objects.link(ob)


def tris_of(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def stats(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.normal_update()
    nonmanifold = sum(1 for e in bm.edges if not e.is_manifold)
    degenerate = sum(1 for f in bm.faces if f.calc_area() < 1e-9)
    uv = len(bm.loops.layers.uv) > 0
    bm.free()
    return {
        "name": ob.name,
        "tris": tris_of(ob),
        "verts": len(ob.data.vertices),
        "polys": len(ob.data.polygons),
        "nonmanifold": nonmanifold,
        "degenerate": degenerate,
        "uv": uv,
    }


def clean_pipe(data, length):
    bm = bmesh.new()
    bm.from_mesh(data)
    geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
    bmesh.ops.bisect_plane(
        bm,
        geom=geom,
        dist=1e-6,
        plane_co=(length, 0.0, 0.0),
        plane_no=(1.0, 0.0, 0.0),
        clear_outer=True,
    )
    boundary = [e for e in bm.edges if e.is_boundary]
    if boundary:
        try:
            bmesh.ops.holes_fill(bm, edges=boundary, sides=0)
        except Exception as exc:
            print("HOLES_FILL_WARN", repr(exc))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(data)
    bm.free()
    data.update()


def copy_mesh(src_name, name, matrix, target):
    src = bpy.data.objects.get(src_name)
    if src is None or src.type != 'MESH':
        raise RuntimeError("missing mesh " + src_name)
    ob = src.copy()
    ob.data = src.data
    ob.name = name
    target.objects.link(ob)
    ob.parent = None
    ob.matrix_world = matrix
    return ob


def in_reception(ob):
    pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    return (
        min(p.x for p in pts) >= -110.6 and max(p.x for p in pts) <= -69.4
        and min(p.y for p in pts) >= -40.6 and max(p.y for p in pts) <= -7.4
        and min(p.z for p in pts) >= -0.2 and max(p.z for p in pts) <= 5.6
    )


def aabb_of(objs):
    pts = []
    for ob in objs:
        pts.extend(ob.matrix_world @ Vector(c) for c in ob.bound_box)
    return [[round(min(p[i] for p in pts), 3) for i in range(3)],
            [round(max(p[i] for p in pts), 3) for i in range(3)]]


def main():
    os.makedirs(os.path.dirname(BACKUP), exist_ok=True)
    if not os.path.exists(BACKUP):
        shutil.copy2(BLEND, BACKUP)
        print("BACKUP", BACKUP)

    hero = col(HERO)
    retired = col(RETIRED)
    retired.hide_render = True
    retired.hide_viewport = True

    for ob in list(bpy.data.objects):
        if ob.name.startswith("REC09_SPRINKLER_"):
            bpy.data.objects.remove(ob, do_unlink=True)

    retired_names = []
    for ob in list(bpy.data.objects):
        if ob.name.startswith("KIT_REC01_Sprinkler_"):
            relink(ob, retired)
            ob.hide_render = True
            ob.hide_viewport = True
            retired_names.append(ob.name)
    print("RETIRED_OLD", len(retired_names), retired_names)

    src = bpy.data.objects.get("P0B_SPRINKLER_RUN_DN80")
    if src is None:
        raise RuntimeError("P0B_SPRINKLER_RUN_DN80 missing")

    pipe = src.copy()
    pipe.data = src.data.copy()
    pipe.name = "REC09_SPRINKLER_RUN"
    hero.objects.link(pipe)
    clean_pipe(pipe.data, X1 - X0)
    pipe.parent = None
    pipe.rotation_euler = (0.0, 0.0, 0.0)
    pipe.location = (X0, PIPE_Y, PIPE_Z)
    pipe["fm_class"] = "SERVICE"
    pipe["fm_family"] = "SPRINKLER"
    pipe["fm_generation"] = "VERIFIED_RECEPTION_R9"
    pipe["fm_source_master"] = "P0B_SPRINKLER_RUN_DN80"

    red = bpy.data.materials.get("M_SH_Sprinkler_Red") or bpy.data.materials.get("M_FM_Sprinkler_Red")
    steel = bpy.data.materials.get("M_SH_Steel_Stainless") or bpy.data.materials.get("M_FM_Steel_Dark")
    dark = bpy.data.materials.get("M_SH_Steel_Dark") or steel
    brass = bpy.data.materials.get("M_SH_Brass") or steel

    head_parts = []
    for i, x in enumerate(HEAD_X):
        body = cyl(hero, f"REC09_SPR_HEAD_BODY_{i:02d}", 0.032, 0.10,
                   (x, PIPE_Y, 4.65), red, axis='Z', seg=16, bevel=0.0004)
        neck = cyl(hero, f"REC09_SPR_HEAD_NECK_{i:02d}", 0.017, 0.045,
                   (x, PIPE_Y, 4.7225), brass, axis='Z', seg=14, bevel=0.0003)
        defl = cyl(hero, f"REC09_SPR_HEAD_DEFL_{i:02d}", 0.048, 0.008,
                   (x, PIPE_Y, 4.75), steel, axis='Z', seg=20, bevel=0.0002)
        bulb = cyl(hero, f"REC09_SPR_HEAD_BULB_{i:02d}", 0.010, 0.036,
                   (x, PIPE_Y, 4.72), brass, axis='Z', seg=12, bevel=0.0002)
        head_parts.extend([body, neck, defl, bulb])
    heads = join_group(hero, "REC09_SPRINKLER_HEADS", head_parts, uv=True, wn=True)
    heads["fm_class"] = "SERVICE"
    heads["fm_family"] = "SPRINKLER"
    heads["fm_generation"] = "VERIFIED_RECEPTION_R9"

    supp_parts = []
    for i, x in enumerate(SUPPORT_X):
        rod = cyl(hero, f"REC09_SPR_SUP_ROD_{i:02d}", 0.008, 0.20,
                  (x, PIPE_Y, 4.70), steel, axis='Z', seg=10, bevel=0.0002)
        cleat = box(hero, f"REC09_SPR_SUP_CLEAT_{i:02d}", 0.075, 0.05, 0.025,
                    (x, PIPE_Y, 4.635), dark, bevel=0.001, seg=2)
        plate = box(hero, f"REC09_SPR_SUP_PLATE_{i:02d}", 0.09, 0.09, 0.012,
                    (x, PIPE_Y, 4.805), dark, bevel=0.001, seg=2)
        supp_parts.extend([rod, cleat, plate])
    sups = join_group(hero, "REC09_SPRINKLER_SUPPORTS", supp_parts, uv=True, wn=True)
    sups["fm_class"] = "SERVICE"
    sups["fm_family"] = "SPRINKLER"
    sups["fm_generation"] = "VERIFIED_RECEPTION_R9"

    caps = []
    for i, x in enumerate((X0, X1)):
        cap = cyl(hero, f"REC09_SPR_CAP_{i:02d}", 0.072, 0.028,
                  (x, PIPE_Y, PIPE_Z), red, axis='X', seg=18, bevel=0.0005)
        caps.append(cap)
    cap_ob = join_group(hero, "REC09_SPRINKLER_CAPS", caps, uv=True, wn=True)
    cap_ob["fm_class"] = "SERVICE"
    cap_ob["fm_family"] = "SPRINKLER"
    cap_ob["fm_generation"] = "VERIFIED_RECEPTION_R9"

    sleeves = []
    for i, x in enumerate((X0, X1)):
        sleeve = copy_mesh(
            "SM_SH_SLEEVE_PIPE_80",
            f"REC09_SPRINKLER_SLEEVE_{i:02d}",
            Matrix.Translation((x, PIPE_Y, PIPE_Z)),
            hero,
        )
        sleeve["fm_class"] = "SERVICE"
        sleeve["fm_family"] = "SPRINKLER"
        sleeve["fm_generation"] = "VERIFIED_RECEPTION_R9"
        sleeve["fm_source_master"] = "SM_SH_SLEEVE_PIPE_80"
        sleeves.append(sleeve)

    bpy.context.view_layer.update()
    new_objs = [pipe, heads, sups, cap_ob] + sleeves
    rows = [stats(o) for o in new_objs]
    for o in new_objs:
        o["fm_tris"] = tris_of(o)

    retired_visible = [ob.name for ob in bpy.data.objects
                       if ob.name in retired_names and not ob.hide_render]
    report = {
        "objects": rows,
        "total_tris": sum(r["tris"] for r in rows),
        "retired": retired_names,
        "retired_visible": retired_visible,
        "inside": all(in_reception(o) for o in new_objs),
        "aabb": aabb_of(new_objs),
        "pipe": {"start_x": X0, "end_x": X1, "y": PIPE_Y, "z": PIPE_Z, "length_m": X1 - X0},
        "heads_x": HEAD_X,
        "supports_x": SUPPORT_X,
        "sleeves_x": [X0, X1],
        "qa_pass": all(r["nonmanifold"] == 0 and r["degenerate"] == 0 and r["uv"] for r in rows),
    }
    with open(QA, "w") as fh:
        json.dump(report, fh, indent=2)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("REC09_SPRINKLER_DONE", json.dumps({
        "objects": len(rows),
        "tris": report["total_tris"],
        "qa_pass": report["qa_pass"],
        "inside": report["inside"],
        "aabb": report["aabb"],
        "retired": len(retired_names),
    }))


main()
