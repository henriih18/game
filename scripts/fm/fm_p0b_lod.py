"""
FRECUENCIA MUERTA - P0b.3 LOD for the corridor service spine.

Creates hidden LOD1/LOD2 copies of the 17 meshes in L1_P0B_SERVICES inside
the child collection L1_P0B_LOD.  LODs share the same world transform as
LOD0 but stay hidden in viewport/render; they are library assets, not extra
geometry in the corridor.  Decimate COLLAPSE, cleanup, flat LOD2, per-mesh
QA, save .blend and write docs/fm_p0b_qa_lod.json.

Run inside live Blender:
    python3 /tmp/opencode/bpy_run.py scripts/fm/fm_p0b_lod.py
"""
import bpy
import bmesh
import json
import os

ROOT = "/home/riyo/Documentos/game"
DOC = os.path.join(ROOT, "docs")
BLEND = os.path.join(ROOT, "nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend")

RATIOS = (0.35, 0.12)
MIN_TRIS_LOD2 = 900


def tri_count(ob):
    return sum(max(0, len(p.vertices) - 2) for p in ob.data.polygons)


def mesh_qa(ob):
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    non_manifold = sum(1 for e in bm.edges if len(e.link_faces) != 2)
    degenerate = sum(1 for f in bm.faces if f.calc_area() < 1e-10)
    loose = sum(1 for v in bm.verts if not v.link_edges)
    bm.free()
    return {
        "tris": tri_count(ob),
        "verts": len(me.vertices),
        "uv": [uv.name for uv in me.uv_layers],
        "materials": [m.name if m else None for m in me.materials],
        "non_manifold_edges": non_manifold,
        "degenerate_faces": degenerate,
        "loose_verts": loose,
        "dims": [round(v, 4) for v in ob.dimensions],
    }


def ensure_collection(name, parent):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        parent.children.link(coll)
    return coll


def clear_collection(coll):
    for ob in list(coll.objects):
        data = ob.data
        bpy.data.objects.remove(ob, do_unlink=True)
        if data and data.users == 0 and isinstance(data, bpy.types.Mesh):
            bpy.data.meshes.remove(data)
    for child in list(coll.children):
        clear_collection(child)
        bpy.data.collections.remove(child)


def decimate(obj, ratio, smooth):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    mod = obj.modifiers.new("P0B_LOD", "DECIMATE")
    mod.decimate_type = 'COLLAPSE'
    mod.ratio = max(0.02, min(1.0, ratio))
    mod.use_collapse_triangulate = True
    bpy.ops.object.modifier_apply(modifier=mod.name)

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-6)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-6, edges=bm.edges[:])
    # Decimation can weld the rims of two touching shells into a single edge
    # with four faces. Splitting those edges restores two manifold shells.
    over = [e for e in bm.edges if len(e.link_faces) > 2]
    if over:
        bmesh.ops.split_edges(bm, edges=over)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(obj.data)
    bm.free()
    for p in obj.data.polygons:
        p.use_smooth = smooth


def main():
    src_coll = bpy.data.collections.get("L1_P0B_SERVICES")
    if not src_coll:
        raise RuntimeError("L1_P0B_SERVICES missing")

    lod_coll = ensure_collection("L1_P0B_LOD", src_coll)
    clear_collection(lod_coll)

    sources = sorted([o for o in src_coll.objects if o.type == 'MESH'], key=lambda x: x.name)
    report = {
        "generated": "P0b.3",
        "ratios": {"LOD1": RATIOS[0], "LOD2": RATIOS[1]},
        "note": "LOD copies stay hidden in viewport/render; they are library assets.",
        "assets": [],
        "totals": {},
    }

    totals = {"LOD0": 0, "LOD1": 0, "LOD2": 0}
    for src in sources:
        entry = {"asset": src.name, "lod0_tris": tri_count(src), "lods": {}}
        totals["LOD0"] += entry["lod0_tris"]

        for level, ratio in ((1, RATIOS[0]), (2, RATIOS[1])):
            new = src.copy()
            new.data = src.data.copy()
            new.name = "%s_LOD%d" % (src.name, level)
            new.data.name = new.name
            lod_coll.objects.link(new)
            new.parent = None
            new.matrix_world = src.matrix_world.copy()
            new.hide_render = True
            new.hide_viewport = True
            new.hide_set(True)

            effective = ratio
            if level == 2 and entry["lod0_tris"] < MIN_TRIS_LOD2:
                effective = min(1.0, max(ratio, 0.25))
            decimate(new, effective, smooth=(level == 1))
            tris = tri_count(new)
            totals["LOD%d" % level] += tris
            new["fm_class"] = "LOD"
            new["fm_lod"] = "LOD%d" % level
            new["fm_source"] = src.name
            new["fm_tris"] = tris
            new["fm_lod_ratio"] = round(effective, 3)
            entry["lods"]["LOD%d" % level] = {
                "ratio": round(effective, 3),
                "meshes": [{"name": new.name, **mesh_qa(new)}],
            }

        report["assets"].append(entry)

    report["totals"] = totals
    report["reduction"] = {
        "LOD1_pct": round(100.0 * totals["LOD1"] / max(1, totals["LOD0"]), 2),
        "LOD2_pct": round(100.0 * totals["LOD2"] / max(1, totals["LOD0"]), 2),
    }

    qa_fail = []
    for entry in report["assets"]:
        for level in ("LOD1", "LOD2"):
            qa = entry["lods"][level]["meshes"][0]
            if qa["non_manifold_edges"] or qa["degenerate_faces"] or not qa["uv"]:
                qa_fail.append({"asset": entry["asset"], "level": level,
                                "non_manifold": qa["non_manifold_edges"],
                                "degenerate": qa["degenerate_faces"],
                                "uv": bool(qa["uv"])})
    report["qa_fail"] = qa_fail

    bpy.context.view_layer.update()
    qa_path = os.path.join(DOC, "fm_p0b_qa_lod.json")
    with open(qa_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("P0B_LOD_DONE")
    print("QA_JSON", qa_path)
    print(json.dumps({
        "objects": len(report["assets"]),
        "totals": totals,
        "reduction": report["reduction"],
        "qa_fail": qa_fail,
    }, indent=2))


main()
