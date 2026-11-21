import bpy
import bmesh
import json
import math
import os
import shutil
import sys
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
BLEND = os.path.join(ROOT, "nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend")
BACKUP = os.path.join(ROOT, "docs/backups/FM_LEVEL1_V06_ARCH_before_security_p0a_services.blend")
QA = os.path.join(ROOT, "docs/fm_security_p0a_sprinkler_qa.json")
sys.path.insert(0, os.path.join(ROOT, "scripts/fm"))
from fm_shared_p0_lib import box, cyl, join_group, ensure_materials  # noqa: E402

SCENE = bpy.data.scenes["NEXUS_L1_V06_ARCH"]
HERO = "L1_SECURITY_P0A_HERO"
RETIRED = "L1_SECURITY_RETIRED_P0A"
M = ensure_materials()


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


def main():
    os.makedirs(os.path.dirname(BACKUP), exist_ok=True)
    if not os.path.exists(BACKUP):
        shutil.copy2(BLEND, BACKUP)
        print("BACKUP", BACKUP)

    hero = col(HERO)
    retired = col(RETIRED)
    retired.hide_render = True
    retired.hide_viewport = True

    # Idempotent cleanup of our own objects.
    for ob in list(bpy.data.objects):
        if ob.name.startswith("SEC_P0A_SPRINKLER_"):
            bpy.data.objects.remove(ob, do_unlink=True)

    old = bpy.data.objects.get("R21B_SERV_Sprinkler")
    if old:
        relink(old, retired)
        old.hide_render = True
        old.hide_viewport = True
        print("RETIRED", old.name, tris_of(old))

    src = bpy.data.objects.get("P0B_SPRINKLER_RUN_DN80")
    if src is None:
        raise RuntimeError("P0B_SPRINKLER_RUN_DN80 missing")

    length = 23.6
    pipe = src.copy()
    pipe.data = src.data.copy()
    pipe.name = "SEC_P0A_SPRINKLER_RUN"
    hero.objects.link(pipe)
    clean_pipe(pipe.data, length)
    pipe.parent = None
    pipe.rotation_euler = (0.0, 0.0, math.radians(90.0))
    pipe.location = (-90.7, 11.2, 4.38)
    pipe["fm_class"] = "SERVICE"
    pipe["fm_family"] = "SPRINKLER"
    pipe["fm_generation"] = "VERIFIED_SECURITY_P0A"
    pipe["fm_source_master"] = "P0B_SPRINKLER_RUN_DN80"

    red = bpy.data.materials.get("M_SH_Sprinkler_Red") or bpy.data.materials.get("M_FM_Sprinkler_Red")
    steel = bpy.data.materials.get("M_SH_Steel_Stainless") or bpy.data.materials.get("M_FM_Steel_Dark")
    dark = bpy.data.materials.get("M_SH_Steel_Dark") or steel
    brass = bpy.data.materials.get("M_SH_Brass") or steel

    head_parts = []
    for i, y in enumerate((12.0, 16.0, 20.0, 24.0, 28.0, 32.0)):
        body = cyl(hero, f"SEC_P0A_SPR_HEAD_BODY_{i:02d}", 0.032, 0.10,
                   (-90.7, y, 4.43), red, axis='Z', seg=16, bevel=0.0004)
        neck = cyl(hero, f"SEC_P0A_SPR_HEAD_NECK_{i:02d}", 0.017, 0.045,
                   (-90.7, y, 4.50), brass, axis='Z', seg=14, bevel=0.0003)
        defl = cyl(hero, f"SEC_P0A_SPR_HEAD_DEFL_{i:02d}", 0.048, 0.008,
                   (-90.7, y, 4.535), steel, axis='Z', seg=20, bevel=0.0002)
        bulb = cyl(hero, f"SEC_P0A_SPR_HEAD_BULB_{i:02d}", 0.010, 0.036,
                   (-90.7, y, 4.485), brass, axis='Z', seg=12, bevel=0.0002)
        head_parts.extend([body, neck, defl, bulb])
    heads = join_group(hero, "SEC_P0A_SPRINKLER_HEADS", head_parts, uv=True, wn=True)
    heads["fm_class"] = "SERVICE"
    heads["fm_family"] = "SPRINKLER"
    heads["fm_generation"] = "VERIFIED_SECURITY_P0A"

    supp_parts = []
    for i, y in enumerate((13.2, 17.2, 21.2, 25.2, 29.2, 33.2)):
        rod = cyl(hero, f"SEC_P0A_SPR_SUP_ROD_{i:02d}", 0.008, 0.36,
                  (-90.7, y, 4.62), steel, axis='Z', seg=10, bevel=0.0002)
        cleat = box(hero, f"SEC_P0A_SPR_SUP_CLEAT_{i:02d}", 0.075, 0.05, 0.025,
                    (-90.7, y, 4.445), dark, bevel=0.001, seg=2)
        plate = box(hero, f"SEC_P0A_SPR_SUP_PLATE_{i:02d}", 0.09, 0.09, 0.012,
                    (-90.7, y, 4.795), dark, bevel=0.001, seg=2)
        supp_parts.extend([rod, cleat, plate])
    sups = join_group(hero, "SEC_P0A_SPRINKLER_SUPPORTS", supp_parts, uv=True, wn=True)
    sups["fm_class"] = "SERVICE"
    sups["fm_family"] = "SPRINKLER"
    sups["fm_generation"] = "VERIFIED_SECURITY_P0A"

    caps = []
    for i, y in enumerate((11.2, 34.8)):
        cap = cyl(hero, f"SEC_P0A_SPR_CAP_{i:02d}", 0.072, 0.028,
                  (-90.7, y, 4.38), red, axis='Y', seg=18, bevel=0.0005)
        caps.append(cap)
    cap_ob = join_group(hero, "SEC_P0A_SPRINKLER_CAPS", caps, uv=True, wn=True)
    cap_ob["fm_class"] = "SERVICE"
    cap_ob["fm_family"] = "SPRINKLER"
    cap_ob["fm_generation"] = "VERIFIED_SECURITY_P0A"

    bpy.context.view_layer.update()
    new_objs = [pipe, heads, sups, cap_ob]
    rows = [stats(o) for o in new_objs]
    for o in new_objs:
        o["fm_tris"] = tris_of(o)

    report = {
        "objects": rows,
        "total_tris": sum(r["tris"] for r in rows),
        "retired": ["R21B_SERV_Sprinkler"],
        "pipe": {
            "start_y": 11.2,
            "end_y": 34.8,
            "length_m": 23.6,
            "x": -90.7,
            "z": 4.38,
        },
        "heads": 6,
        "supports": 6,
        "qa_pass": all(r["nonmanifold"] == 0 and r["degenerate"] == 0 and r["uv"] for r in rows),
    }
    os.makedirs(os.path.dirname(QA), exist_ok=True)
    with open(QA, "w") as fh:
        json.dump(report, fh, indent=2)

    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("SEC_P0A_SPRINKLER_DONE", json.dumps(report))


main()
