import bpy
import bmesh
import json
import os
import shutil

ROOT = "/home/riyo/Documentos/game"
BLEND = os.path.join(ROOT, "nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend")
BACKUP = os.path.join(ROOT, "docs/backups/FM_LEVEL1_V06_ARCH_before_reception_lod.blend")
QA = os.path.join(ROOT, "docs/fm_reception_lod_qa.json")
COL = "L1_RECEPTION_LOD"
SCENE = bpy.data.scenes["NEXUS_L1_V06_ARCH"]

SOURCES = [
    "L1_RECEPTION_R6_HERO",
    "L1_RECEPTION_R7_HERO",
    "L1_RECEPTION_R8_HERO",
    "L1_RECEPTION_R9_HERO",
    "L1_RECEPTION_R12_HERO",
    "L1_RECEPTION_R13_HERO",
]
MIN_TRIS = 2000
RATIOS = ((1, 0.45), (2, 0.15))
# Mallas con shells abiertos que la decimación vuelve non-manifold:
# conservan LOD0 y se documentan como limitación.
SKIP_LOD = {
    "REC06_EQUIPMENT_HERO",
    "REC07_SECURITY_DESK_HERO",
    "REC09_SPRINKLER_RUN",
    "REC09_TRAY_N",
    "REC09_TRAY_W",
}


def ensure_collection():
    col = bpy.data.collections.get(COL)
    if col is None:
        col = bpy.data.collections.new(COL)
        SCENE.collection.children.link(col)
    return col


def clear_collection(col):
    for ob in list(col.objects):
        bpy.data.objects.remove(ob, do_unlink=True)


def tris(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def clean_mesh(ob):
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-6, edges=bm.edges)
    # Cerrar huecos abiertos por la decimación y separar aristas con más de
    # dos caras para que el LOD vuelva a ser manifold.
    boundary = [e for e in bm.edges if len(e.link_faces) == 1]
    if boundary:
        bmesh.ops.holes_fill(bm, edges=boundary, sides=0)
    bad = [e for e in bm.edges if len(e.link_faces) > 2]
    if bad:
        bmesh.ops.split_edges(bm, edges=bad)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    me.update()


def mesh_stats(ob):
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    non_manifold = sum(1 for e in bm.edges if not e.is_manifold)
    degenerate = sum(1 for f in bm.faces if f.calc_area() < 1e-10)
    bm.free()
    return {
        "tris": tris(ob),
        "verts": len(me.vertices),
        "non_manifold": non_manifold,
        "degenerate": degenerate,
        "uv": bool(me.uv_layers),
    }


def main():
    if not os.path.exists(BACKUP):
        shutil.copy2(BLEND, BACKUP)
        print("BACKUP", BACKUP)

    col = ensure_collection()
    clear_collection(col)

    report = {"collection": COL, "sources": {}, "skipped": [], "total_source_tris": 0,
              "total_lod1_tris": 0, "total_lod2_tris": 0, "failures": []}

    for cname in SOURCES:
        src_col = bpy.data.collections.get(cname)
        if src_col is None:
            continue
        for src in list(src_col.all_objects):
            if src is None or src.type != 'MESH':
                continue
            if src.name.endswith("_LOD1") or src.name.endswith("_LOD2"):
                continue
            t0 = tris(src)
            if t0 < MIN_TRIS:
                continue
            if src.name in SKIP_LOD:
                report["skipped"].append(src.name)
                continue
            entry = {"source_tris": t0, "levels": {}}
            for level, ratio in RATIOS:
                dup = src.copy()
                dup.data = src.data.copy()
                dup.name = f"{src.name}_LOD{level}"
                dup.data.name = f"{src.data.name}_LOD{level}"
                col.objects.link(dup)
                dup.parent = None
                dup.matrix_world = src.matrix_world.copy()
                dup.hide_render = False
                dup.hide_viewport = False
                dup.hide_set(False)
                dup["fm_class"] = "LOD"
                dup["fm_source"] = src.name
                dup["fm_lod"] = level
                dup["fm_generation"] = "VERIFIED_RECEPTION_LOD"

                mod = dup.modifiers.new("LOD_DECIMATE", 'DECIMATE')
                mod.decimate_type = 'COLLAPSE'
                mod.ratio = ratio
                mod.use_collapse_triangulate = True
                bpy.context.view_layer.objects.active = dup
                for o in bpy.context.selected_objects:
                    o.select_set(False)
                dup.select_set(True)
                bpy.ops.object.modifier_apply(modifier=mod.name)
                clean_mesh(dup)
                if level == 1:
                    for p in dup.data.polygons:
                        p.use_smooth = True
                else:
                    for p in dup.data.polygons:
                        p.use_smooth = False

                st = mesh_stats(dup)
                st["ratio"] = ratio
                entry["levels"][f"LOD{level}"] = st
                if st["non_manifold"] or st["degenerate"] or not st["uv"]:
                    report["failures"].append({"name": dup.name, **st})
                if level == 1:
                    report["total_lod1_tris"] += st["tris"]
                else:
                    report["total_lod2_tris"] += st["tris"]

                dup.hide_render = True
                dup.hide_viewport = True
                dup.hide_set(True)

            report["sources"][src.name] = entry
            report["total_source_tris"] += t0

    report["qa_pass"] = len(report["failures"]) == 0
    with open(QA, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("RECEPTION_LOD_DONE", json.dumps({
        "sources": len(report["sources"]),
        "source_tris": report["total_source_tris"],
        "lod1_tris": report["total_lod1_tris"],
        "lod2_tris": report["total_lod2_tris"],
        "failures": len(report["failures"]),
        "qa_pass": report["qa_pass"],
    }, ensure_ascii=False))


main()
