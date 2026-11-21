import bpy
import bmesh
import json
import os
import shutil

ROOT = "/home/riyo/Documentos/game"
BLEND = os.path.join(ROOT, "nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend")
BACKUP = os.path.join(ROOT, "docs/backups/FM_LEVEL1_V06_ARCH_before_reception_r12_lod.blend")
QA = os.path.join(ROOT, "docs/fm_reception_r12_lod_qa.json")
SRC = "L1_RECEPTION_R12_HERO"
LOD = "L1_RECEPTION_R12_LOD"
COL = "L1_RECEPTION_R12_COLLISION"
SCENE = bpy.data.scenes["NEXUS_L1_V06_ARCH"]

RATIOS = {
    "REC12_BENCH_A": (0.38, 0.12),
    "REC12_BENCH_B": (0.38, 0.12),
    "REC12_TABLE": (0.45, 0.15),
    "REC12_PLANTER": (0.35, 0.10),
}


def ensure_collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        SCENE.collection.children.link(col)
    return col


def clear(col):
    for ob in list(col.objects):
        bpy.data.objects.remove(ob, do_unlink=True)


def stats(ob):
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    nm = sum(1 for e in bm.edges if not e.is_manifold)
    dg = sum(1 for f in bm.faces if f.calc_area() < 1e-10)
    bm.free()
    return {
        "tris": sum(len(p.vertices) - 2 for p in me.polygons),
        "verts": len(me.vertices),
        "non_manifold": nm,
        "degenerate": dg,
        "uv": bool(me.uv_layers),
    }


def clean_mesh(ob, smooth):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-6, edges=bm.edges)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    for p in ob.data.polygons:
        p.use_smooth = smooth


def add_box(col, name, dims, center):
    sx, sy, sz = dims
    verts = [
        (-sx/2, -sy/2, -sz/2), (sx/2, -sy/2, -sz/2),
        (sx/2, sy/2, -sz/2), (-sx/2, sy/2, -sz/2),
        (-sx/2, -sy/2, sz/2), (sx/2, -sy/2, sz/2),
        (sx/2, sy/2, sz/2), (-sx/2, sy/2, sz/2),
    ]
    faces = [(0,1,2,3), (4,7,6,5), (0,4,5,1), (1,5,6,2), (2,6,7,3), (3,7,4,0)]
    me = bpy.data.meshes.new(name + "_mesh")
    me.from_pydata(verts, [], faces)
    me.validate()
    ob = bpy.data.objects.new(name, me)
    ob.location = center
    col.objects.link(ob)
    ob.display_type = 'WIRE'
    ob.hide_render = True
    ob["fm_class"] = "COLLISION"
    return ob


def main():
    if not os.path.exists(BACKUP):
        shutil.copy2(BLEND, BACKUP)
        print("BACKUP", BACKUP)
    lod = ensure_collection(LOD)
    col = ensure_collection(COL)
    clear(lod)
    clear(col)
    report = {"objects": {}}
    ok = True
    for name, (r1, r2) in RATIOS.items():
        src = bpy.data.objects.get(name)
        if src is None:
            continue
        entry = {"lod0": stats(src), "lod": {}}
        for level, ratio in ((1, r1), (2, r2)):
            ob = src.copy()
            ob.data = src.data.copy()
            lod.objects.link(ob)
            ob.name = f"{name}_LOD{level}"
            ob.data.name = ob.name + "_mesh"
            ob.hide_render = True
            ob.hide_viewport = True
            ob.hide_set(True)
            mod = ob.modifiers.new("LOD_DECIMATE", 'DECIMATE')
            mod.decimate_type = 'COLLAPSE'
            mod.ratio = ratio
            mod.use_collapse_triangulate = True
            bpy.context.view_layer.objects.active = ob
            ob.select_set(True)
            bpy.ops.object.modifier_apply(modifier=mod.name)
            ob.select_set(False)
            clean_mesh(ob, smooth=(level == 1))
            s = stats(ob)
            s["ratio"] = ratio
            entry["lod"][str(level)] = s
            ok = ok and s["non_manifold"] == 0 and s["degenerate"] == 0 and s["uv"]
        report["objects"][name] = entry
        # Colisión sencilla.
        if name.startswith("REC12_BENCH"):
            cy = -19.80 if name.endswith("A") else -23.80
            add_box(col, name + "-col", (0.60, 2.12, 1.00), (-109.54, cy, 0.50))
        elif name == "REC12_TABLE":
            add_box(col, "REC12_TABLE-col", (1.22, 0.82, 0.46), (-107.40, -21.80, 0.23))
        elif name == "REC12_PLANTER":
            add_box(col, "REC12_PLANTER-col", (0.60, 0.60, 0.74), (-105.50, -19.50, 0.37))
    report["qa_pass"] = ok
    with open(QA, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("REC12_LOD_DONE", json.dumps(report, ensure_ascii=False))


main()
