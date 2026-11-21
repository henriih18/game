import bpy
import bmesh
import json
import os
import shutil
import sys

ROOT = "/home/riyo/Documentos/game"
BLEND = os.path.join(ROOT, "nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend")
BACKUP = os.path.join(ROOT, "docs/backups/FM_LEVEL1_V06_ARCH_before_reception_r10_rug.blend")
QA = os.path.join(ROOT, "docs/fm_reception_r10_rug_qa.json")
COL = "L1_RECEPTION_R11_HERO"
RETIRED = "L1_RECEPTION_RETIRED"
SCENE = bpy.data.scenes["NEXUS_L1_V06_ARCH"]

sys.path.insert(0, os.path.join(ROOT, "scripts/fm"))
from fm_shared_p0_lib import box, join_group, _pbr, srgb  # noqa: E402


def ensure_collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        SCENE.collection.children.link(col)
    return col


def retire_old_rug():
    col = bpy.data.collections.get(RETIRED)
    if col is None:
        col = bpy.data.collections.new(RETIRED)
        SCENE.collection.children.link(col)
    moved = []
    for ob in list(SCENE.objects):
        if ob.name.startswith("PROP_REC02_Waiting_Rug"):
            for c in list(ob.users_collection):
                c.objects.unlink(ob)
            col.objects.link(ob)
            ob.hide_render = True
            ob.hide_viewport = True
            ob.hide_set(True)
            moved.append(ob.name)
    return moved


def clear_previous():
    col = bpy.data.collections.get(COL)
    if col:
        for ob in list(col.objects):
            bpy.data.objects.remove(ob, do_unlink=True)


def stats(ob):
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    non_manifold = sum(1 for e in bm.edges if not e.is_manifold)
    degenerate = sum(1 for f in bm.faces if f.calc_area() < 1e-10)
    bm.free()
    return {
        "tris": sum(len(p.vertices) - 2 for p in me.polygons),
        "verts": len(me.vertices),
        "non_manifold": non_manifold,
        "degenerate": degenerate,
        "uv": bool(me.uv_layers),
    }


def main():
    if not os.path.exists(BACKUP):
        shutil.copy2(BLEND, BACKUP)
        print("BACKUP", BACKUP)

    retired = retire_old_rug()
    clear_previous()
    col = ensure_collection(COL)

    rug_mat = _pbr("M_REC10_Rug", srgb(92, 104, 90), 0.0, 0.98,
                   scale=120, bump=0.0012, micro=500, rough_var=0.05)
    border_mat = _pbr("M_REC10_Rug_Border", srgb(128, 136, 118), 0.0, 0.94,
                      scale=80, bump=0.0006, micro=420, rough_var=0.04)

    cx, cy = -107.30, -22.00
    parts = []
    parts.append(box(col, "REC10_RUG_BASE", 5.90, 3.90, 0.012,
                     (cx, cy, 0.006), rug_mat, bevel=0.002, seg=2))
    # Borde elevado 2 mm, cuatro tiras.
    parts.append(box(col, "REC10_RUG_BORDER_N", 5.90, 0.18, 0.002,
                     (cx, cy + 1.86, 0.014), border_mat, bevel=0.001, seg=1))
    parts.append(box(col, "REC10_RUG_BORDER_S", 5.90, 0.18, 0.002,
                     (cx, cy - 1.86, 0.014), border_mat, bevel=0.001, seg=1))
    parts.append(box(col, "REC10_RUG_BORDER_E", 0.18, 3.54, 0.002,
                     (cx + 2.86, cy, 0.014), border_mat, bevel=0.001, seg=1))
    parts.append(box(col, "REC10_RUG_BORDER_W", 0.18, 3.54, 0.002,
                     (cx - 2.86, cy, 0.014), border_mat, bevel=0.001, seg=1))
    # Refuerzo de esquina y una pestaña levantada para romper la lectura de plano.
    parts.append(box(col, "REC10_RUG_CORNER", 0.28, 0.28, 0.003,
                     (cx + 2.76, cy - 1.76, 0.0145), border_mat, bevel=0.001, seg=1))
    parts.append(box(col, "REC10_RUG_LIFT", 0.55, 0.04, 0.018,
                     (cx - 2.60, cy + 1.78, 0.022), rug_mat, bevel=0.001, seg=1))

    ob = join_group(col, "REC10_RUG_HERO", parts, uv=True, wn=True)
    ob["fm_class"] = "HERO_PROP"
    ob["fm_generation"] = "VERIFIED_RECEPTION_R10"
    ob["fm_source_master"] = "PROP_REC02_Waiting_Rug"
    bpy.context.view_layer.update()

    data = stats(ob)
    data.update({
        "collection": COL,
        "name": ob.name,
        "retired": retired,
        "aabb": [
            [round(v, 4) for v in (min((ob.matrix_world @ __import__('mathutils').Vector(c)).x for c in ob.bound_box),
                                   min((ob.matrix_world @ __import__('mathutils').Vector(c)).y for c in ob.bound_box),
                                   min((ob.matrix_world @ __import__('mathutils').Vector(c)).z for c in ob.bound_box))],
            [round(v, 4) for v in (max((ob.matrix_world @ __import__('mathutils').Vector(c)).x for c in ob.bound_box),
                                   max((ob.matrix_world @ __import__('mathutils').Vector(c)).y for c in ob.bound_box),
                                   max((ob.matrix_world @ __import__('mathutils').Vector(c)).z for c in ob.bound_box))],
        ],
        "qa_pass": data["non_manifold"] == 0 and data["degenerate"] == 0 and data["uv"],
    })
    with open(QA, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("REC10_RUG_DONE", json.dumps(data, ensure_ascii=False))


main()
