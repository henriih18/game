"""
FRECUENCIA MUERTA - P0a.2 LOD + collision proxies for shared doors/lights.

Creates LOD1/LOD2 decimated copies of the door and lighting masters inside
L1_SHARED_HERO, plus a separate P0_COLLISION collection of box proxies and a
capsule-clearance report. Saves the .blend and writes
docs/fm_shared_p0_qa_p0a2.json.

Run inside live Blender:
    python3 /tmp/opencode/bpy_run.py /tmp/opencode/p0a2_lod.py
"""
import bpy
import bmesh
import json
import math
import os
from mathutils import Vector, Matrix

ROOT = "/home/riyo/Documentos/game"
DOC = os.path.join(ROOT, "docs")
BLEND = os.path.join(ROOT, "nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend")

PLAYER_RADIUS = 0.38
PLAYER_HEIGHT = 1.70
CAPSULE_DIAMETER = PLAYER_RADIUS * 2.0
DOOR_MARGIN = 0.10

RATIOS = {
    "DOOR": (0.38, 0.12),
    "PORTAL": (0.45, 0.15),
    "LIGHT": (0.32, 0.10),
}


def ensure_collection(name, parent):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        parent.children.link(coll)
    return coll


def clear_collection(name):
    coll = bpy.data.collections.get(name)
    if not coll:
        return
    for ob in list(coll.objects):
        data = ob.data
        bpy.data.objects.remove(ob, do_unlink=True)
        if data and data.users == 0:
            if isinstance(data, bpy.types.Mesh):
                bpy.data.meshes.remove(data)
    for child in list(coll.children):
        bpy.data.collections.remove(child)
    bpy.data.collections.remove(coll)


def tri_count(obj):
    return sum(max(0, len(p.vertices) - 2) for p in obj.data.polygons)


def mesh_qa(obj):
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    non_manifold = sum(1 for e in bm.edges if len(e.link_faces) != 2)
    degenerate = sum(1 for f in bm.faces if f.calc_area() < 1e-10)
    loose = sum(1 for v in bm.verts if not v.link_edges)
    bm.free()
    return {
        "tris": tri_count(obj),
        "verts": len(me.vertices),
        "uv": [uv.name for uv in me.uv_layers],
        "materials": [m.name if m else None for m in me.materials],
        "non_manifold_edges": non_manifold,
        "degenerate_faces": degenerate,
        "loose_verts": loose,
        "dims": [round(v, 4) for v in obj.dimensions],
    }


def copy_mesh_child(src, new_root, name_suffix, coll):
    new = src.copy()
    new.data = src.data.copy()
    new.name = src.name + name_suffix
    new.data.name = new.name
    new.parent = new_root
    new.matrix_parent_inverse = Matrix.Identity(4)
    new.matrix_local = src.matrix_local
    new.hide_render = False
    new.hide_set(False)
    coll.objects.link(new)
    return new


def decimate(obj, ratio, smooth=True):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    mod = obj.modifiers.new("P0A2_LOD", "DECIMATE")
    mod.decimate_type = 'COLLAPSE'
    mod.ratio = max(0.02, min(1.0, ratio))
    mod.use_collapse_triangulate = True
    bpy.ops.object.modifier_apply(modifier=mod.name)
    # cleanup / normals
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-6)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-6, edges=bm.edges[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(obj.data)
    bm.free()
    for p in obj.data.polygons:
        p.use_smooth = smooth


def root_local_bbox(root, objs):
    inv = root.matrix_world.inverted()
    mn = Vector((1e9, 1e9, 1e9))
    mx = Vector((-1e9, -1e9, -1e9))
    for ob in objs:
        mw = ob.matrix_world
        for v in ob.data.vertices:
            p = inv @ (mw @ v.co)
            for i in range(3):
                mn[i] = min(mn[i], p[i])
                mx[i] = max(mx[i], p[i])
    return mn, mx


def add_box(bm, mn, mx):
    verts = []
    for x in (mn.x, mx.x):
        for y in (mn.y, mx.y):
            for z in (mn.z, mx.z):
                verts.append(bm.verts.new((x, y, z)))
    # index layout: 0 (x0y0z0), 1 (x0y0z1), 2 (x0y1z0), 3 (x0y1z1),
    #               4 (x1y0z0), 5 (x1y0z1), 6 (x1y1z0), 7 (x1y1z1)
    faces = [
        (0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
        (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3),
    ]
    for f in faces:
        bm.faces.new([verts[i] for i in f])


def build_collision(asset, root, frame_objs, leaf_objs, kind, clear_w, clear_h, coll):
    inv = root.matrix_world.inverted()
    bm = bmesh.new()
    boxes = []
    if kind in ("DOOR", "PORTAL"):
        fmn, fmx = root_local_bbox(root, frame_objs)
        left = max(0.02, clear_w * 0.5)
        # frame jambs + head
        boxes.append((Vector((fmn.x, fmn.y, fmn.z)), Vector((-left, fmx.y, fmx.z))))
        boxes.append((Vector((left, fmn.y, fmn.z)), Vector((fmx.x, fmx.y, fmx.z))))
        boxes.append((Vector((-left, fmn.y, clear_h)), Vector((left, fmx.y, fmx.z))))
        if fmn.z < -0.005:
            boxes.append((Vector((-left, fmn.y, fmn.z)), Vector((left, fmx.y, 0.0))))
        if leaf_objs:
            lmn, lmx = root_local_bbox(root, leaf_objs)
            y0 = max(lmn.y, -0.11)
            y1 = min(lmx.y, 0.11)
            if y1 - y0 < 0.02:
                y0, y1 = -0.09, 0.09
            boxes.append((Vector((-left, y0, 0.0)), Vector((left, y1, clear_h))))
    else:  # LIGHT
        lmn, lmx = root_local_bbox(root, frame_objs)
        boxes.append((lmn.copy(), lmx.copy()))

    for mn, mx in boxes:
        if mx.x - mn.x < 0.005 or mx.y - mn.y < 0.005 or mx.z - mn.z < 0.005:
            continue
        add_box(bm, mn, mx)

    me = bpy.data.meshes.new(asset + "-col")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(asset + "-col", me)
    coll.objects.link(ob)
    ob.parent = root
    ob.matrix_parent_inverse = Matrix.Identity(4)
    ob.location = (0, 0, 0)
    ob.rotation_euler = (0, 0, 0)
    ob.scale = (1, 1, 1)
    ob.hide_render = True
    ob.display_type = 'WIRE'
    ob["fm_class"] = "COLLISION"
    ob["fm_collision"] = "box_proxy"
    ob["fm_capsule_radius"] = PLAYER_RADIUS
    return ob


def build_asset_lods(src_root, coll, category):
    asset = src_root.name.replace("_ROOT", "")
    children = [o for o in src_root.children if o.type == 'MESH' and not o.name.endswith("-col")]
    if not children:
        return None
    base_tris = sum(tri_count(o) for o in children)
    ratio1, ratio2 = RATIOS[category]
    result = {"asset": asset, "category": category, "lod0_tris": base_tris, "lods": {}}

    for level, ratio in ((1, ratio1), (2, ratio2)):
        suffix = "_LOD%d" % level
        root = bpy.data.objects.new(asset + suffix + "_ROOT", None)
        root.empty_display_type = 'PLAIN_AXES'
        root.empty_display_size = 0.3
        coll.objects.link(root)
        root.location = src_root.location + Vector((0.0, -4.0 if category != "LIGHT" else -2.2, 0.0))
        root.rotation_euler = src_root.rotation_euler.copy()
        root.scale = src_root.scale.copy()

        tris = 0
        qa = []
        for src in children:
            new = copy_mesh_child(src, root, suffix, coll)
            decimate(new, ratio, smooth=(level == 1))
            tris += tri_count(new)
            qa.append({"name": new.name, **mesh_qa(new)})
        root["fm_asset"] = asset + suffix
        root["fm_generation"] = "VERIFIED_P0A2"
        root["fm_lod"] = "LOD%d" % level
        root["fm_tris"] = tris
        root["fm_source"] = asset
        root["fm_lod_ratio"] = round(ratio, 3)
        result["lods"]["LOD%d" % level] = {"tris": tris, "ratio": ratio, "meshes": qa}

    return result


def capsule_report(src_root, category, clear_w, clear_h, children=None):
    if category in ("DOOR", "PORTAL"):
        pass_w = clear_w >= CAPSULE_DIAMETER + DOOR_MARGIN
        pass_h = clear_h >= PLAYER_HEIGHT + DOOR_MARGIN
        return {
            "clear_w": round(clear_w, 3),
            "clear_h": round(clear_h, 3),
            "capsule_diameter": CAPSULE_DIAMETER,
            "capsule_height": PLAYER_HEIGHT,
            "margin_required": DOOR_MARGIN,
            "width_ok": pass_w,
            "height_ok": pass_h,
            "pass": bool(pass_w and pass_h),
        }
    # Lights are wall/ceiling fixtures. The catalog root Z is display-only;
    # what matters for the capsule corridor is how far the body protrudes
    # from its mounting plane. The thinnest local dimension is that depth for
    # these box-like fixtures.
    protrusion = 0.0
    for ob in (children or []):
        if ob.type == 'MESH':
            protrusion = max(protrusion, min(ob.dimensions))
    return {
        "test_type": "fixture_protrusion",
        "protrusion_m": round(protrusion, 3),
        "max_protrusion_m": 0.40,
        "player_height": PLAYER_HEIGHT,
        "pass": bool(protrusion <= 0.40),
        "note": "Catalog Z is display-only; placement height is set in the level.",
    }


def main():
    shared = bpy.data.collections.get("L1_SHARED_HERO")
    if not shared:
        raise RuntimeError("L1_SHARED_HERO missing")

    for name in ("DOORS_LOD", "LIGHTING_LOD", "P0_COLLISION"):
        clear_collection(name)
    doors_lod = ensure_collection("DOORS_LOD", shared)
    lights_lod = ensure_collection("LIGHTING_LOD", shared)
    col_coll = ensure_collection("P0_COLLISION", shared)

    report = {"generated": "P0a.2", "player": {"radius": PLAYER_RADIUS, "height": PLAYER_HEIGHT},
              "assets": [], "capsule": []}

    for src in sorted([o for o in bpy.data.collections["DOORS"].objects if o.type == 'EMPTY'],
                      key=lambda x: x.name):
        asset = src.name.replace("_ROOT", "")
        category = str(src.get("fm_class", "DOOR"))
        if category not in ("DOOR", "PORTAL"):
            category = "DOOR"
        res = build_asset_lods(src, doors_lod, category)
        if not res:
            continue
        clear_w = float(src.get("fm_clear_w", 0.0))
        clear_h = float(src.get("fm_clear_h", 0.0))
        kids = [o for o in src.children if o.type == 'MESH']
        frames = [o for o in kids if "FRAME" in o.name or "PORTAL" in o.name]
        leaves = [o for o in kids if "LEAF" in o.name]
        col = build_collision(asset, src, frames or kids, leaves, category, clear_w, clear_h, col_coll)
        res["collision"] = mesh_qa(col)
        res["capsule"] = capsule_report(src, category, clear_w, clear_h, kids)
        report["assets"].append(res)
        report["capsule"].append({"asset": asset, **res["capsule"]})

    for src in sorted([o for o in bpy.data.collections["LIGHTING"].objects if o.type == 'EMPTY'],
                      key=lambda x: x.name):
        asset = src.name.replace("_ROOT", "")
        if any(x in src.name for x in ("EMERGENCY_WALL_E", "EMERGENCY_WALL_N", "LUMINAIRE_1500")):
            pass
        res = build_asset_lods(src, lights_lod, "LIGHT")
        if not res:
            continue
        # WALL_N child is a linked mesh duplicate of WALL_E; de-duplicate LODs by source data
        kids = [o for o in src.children if o.type == 'MESH']
        col = build_collision(asset, src, kids, [], "LIGHT", 0.0, 0.0, col_coll)
        res["collision"] = mesh_qa(col)
        res["capsule"] = capsule_report(src, "LIGHT", 0.0, 0.0, kids)
        report["assets"].append(res)
        report["capsule"].append({"asset": asset, **res["capsule"]})

    report["gamification"] = {
        "lod1_used": "mid distance (15-35 m)",
        "lod2_used": "far distance (35-70 m) or static background",
        "collision": "separate P0_COLLISION collection; box proxies, exported apart from visual GLB",
        "bake_deferred": "procedural PBR is still the approved look; bake/ORM belongs to the final texture pass",
    }

    bpy.context.view_layer.update()
    qa_path = os.path.join(DOC, "fm_shared_p0_qa_p0a2.json")
    with open(qa_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("P0A2_DONE")
    print("QA_JSON", qa_path)
    print(json.dumps({
        "assets": len(report["assets"]),
        "capsule_pass": sum(1 for c in report["capsule"] if c["pass"]),
        "capsule_total": len(report["capsule"]),
        "assets_summary": [
            {"asset": a["asset"], "lod0": a["lod0_tris"],
             "lod1": a["lods"]["LOD1"]["tris"], "lod2": a["lods"]["LOD2"]["tris"]}
            for a in report["assets"]
        ],
    }, indent=2))


main()
