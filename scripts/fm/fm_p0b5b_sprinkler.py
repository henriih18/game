"""P0b.5b - hero branch lines and tees for the Z10 sprinkler grid.

Removes the two low-poly 20 m branch pipes from PROP_Z10_SprinklerBranches,
builds 20-sided red pipes with flanges/couplings/clamps, adds hero tees at
(45,17) and (55,17), dresses the eight branch heads with escutcheons and
removes the conflicting main head at (55,17).
"""

import bpy
import bmesh
import json
import math
import os
import shutil
import sys

from mathutils import Vector

sys.path.insert(0, "/home/riyo/Documentos/game/scripts/fm")
from fm_shared_p0_lib import ensure_materials, box, cyl, cone, join_group

COLL = "L1_P0B5_Z10"
RET = "Z10_RETIRED_P0B4"
DOCS = "/home/riyo/Documentos/game/docs"
BLEND = "/home/riyo/Documentos/game/nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend"
BACKUP = "/home/riyo/Documentos/game/docs/backups/FM_LEVEL1_V06_ARCH_before_p0b5b.blend"

M = ensure_materials()
RED = M["sprink_red"]
GALV = M["galv"]
DARK = M["steel_dark"]
BARE = M["steel_bare"]
BRASS = M["brass"]
LABEL = M["label"]

BRANCH_X = (45.0, 55.0)
BRANCH_Y0, BRANCH_Y1 = 9.0, 29.0
BRANCH_Z = 3.90
HEAD_YS = (10.0, 14.0, 24.0, 28.0)
TEE_Y = 17.0


def link_only(ob, col):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    col.objects.link(ob)


def parts_for_branch(col, x):
    parts = []
    n = [0]

    def C(r, depth, center, mat, axis='Z', seg=20, bev=0.0006):
        n[0] += 1
        ob = cyl(col, "P0B5B_%s_%04d" % (x, n[0]), r, depth, center,
                 mat, axis=axis, seg=seg, bevel=bev, bseg=1)
        parts.append(ob)
        return ob

    def B(sx, sy, sz, center, mat, bev=0.0005, seg=1):
        n[0] += 1
        ob = box(col, "P0B5B_%s_%04d" % (x, n[0]), sx, sy, sz, center,
                 mat, bev, seg)
        parts.append(ob)
        return ob

    # 20 m branch main.
    C(0.035, BRANCH_Y1 - BRANCH_Y0, (x, (BRANCH_Y0 + BRANCH_Y1) / 2, BRANCH_Z),
      RED, 'Y', 20)

    # Flanges every 2.4 m, six bolts each.
    y = 9.2
    while y <= 28.4 + 1e-6:
        C(0.055, 0.018, (x, y, BRANCH_Z), RED, 'Y', 20)
        for k in range(6):
            a = math.radians(60 * k + 30)
            bx = x + 0.045 * math.cos(a)
            bz = BRANCH_Z + 0.045 * math.sin(a)
            C(0.005, 0.024, (bx, y, bz), BARE, 'Y', 8, 0.0)
        y += 2.4

    # Clamps at the existing hanger positions.
    for hy in HEAD_YS:
        C(0.045, 0.024, (x, hy, BRANCH_Z), DARK, 'Y', 16)
        B(0.030, 0.026, 0.010, (x + 0.042, hy, BRANCH_Z), BARE, 0.0004, 1)

    # End caps at both ends.
    for yy in (BRANCH_Y0, BRANCH_Y1):
        C(0.045, 0.016, (x, yy, BRANCH_Z), GALV, 'Y', 20)
        for k in range(4):
            a = math.radians(90 * k)
            C(0.0045, 0.022, (x + 0.036 * math.cos(a), yy,
                              BRANCH_Z + 0.036 * math.sin(a)),
              BARE, 'Y', 8, 0.0)

    return parts


def build_branches(col):
    parts = []
    for x in BRANCH_X:
        parts.extend(parts_for_branch(col, x))
    ob = join_group(col, "P0B5_SPRINKLER_BRANCHES", parts, uv=True, wn=True)
    ob["fm_class"] = "SERVICE"
    ob["fm_family"] = "SPRINKLER_BRANCH"
    ob["fm_generation"] = "VERIFIED_P0B5B"
    return ob


def build_tees(col):
    parts = []
    n = [0]

    def C(r, depth, center, mat, axis='Z', seg=20, bev=0.0006):
        n[0] += 1
        ob = cyl(col, "P0B5B_TEE_%04d" % n[0], r, depth, center, mat,
                 axis=axis, seg=seg, bevel=bev, bseg=1)
        parts.append(ob)
        return ob

    for x in BRANCH_X:
        # Main run along X, branch along Y.
        C(0.070, 0.200, (x, TEE_Y, BRANCH_Z), RED, 'X', 20)
        C(0.052, 0.140, (x, TEE_Y, BRANCH_Z), RED, 'Y', 20)
        for sx in (-1, 1):
            C(0.078, 0.014, (x + sx * 0.100, TEE_Y, BRANCH_Z), RED, 'X', 20)
            for k in range(6):
                a = math.radians(60 * k + 30)
                C(0.0045, 0.020, (x + sx * 0.095,
                                  TEE_Y + 0.062 * math.cos(a),
                                  BRANCH_Z + 0.062 * math.sin(a)),
                  BARE, 'X', 8, 0.0)
        for sy in (-1, 1):
            C(0.060, 0.014, (x, TEE_Y + sy * 0.085, BRANCH_Z), RED, 'Y', 20)
            for k in range(6):
                a = math.radians(60 * k + 30)
                C(0.0045, 0.020, (x + 0.044 * math.cos(a),
                                  TEE_Y + sy * 0.085,
                                  BRANCH_Z + 0.044 * math.sin(a)),
                  BARE, 'Y', 8, 0.0)
        C(0.018, 0.030, (x, TEE_Y, BRANCH_Z + 0.060), BRASS, 'Z', 12)

    ob = join_group(col, "P0B5_SPRINKLER_TEES", parts, uv=True, wn=True)
    ob["fm_class"] = "SERVICE"
    ob["fm_family"] = "SPRINKLER_TEE"
    ob["fm_generation"] = "VERIFIED_P0B5B"
    return ob


def build_escutcheons(col):
    parts = []
    n = [0]
    for x in BRANCH_X:
        for y in HEAD_YS:
            n[0] += 1
            ob = cone(col, "P0B5B_ESC_%03d" % n[0], 0.060, 0.036, 0.018,
                      (x, y, 3.895), LABEL, axis='Z', seg=20, bevel=0.0004,
                      bseg=1)
            parts.append(ob)
            n[0] += 1
            ob = cyl(col, "P0B5B_ESCR_%03d" % n[0], 0.062, 0.006,
                     (x, y, 3.906), LABEL, axis='Z', seg=20,
                     bevel=0.0004, bseg=1)
            parts.append(ob)
    ob = join_group(col, "P0B5_SPRINKLER_ESCUTCHEONS", parts, uv=True, wn=True)
    ob["fm_class"] = "SERVICE"
    ob["fm_family"] = "SPRINKLER_ESCUTCHEON"
    ob["fm_generation"] = "VERIFIED_P0B5B"
    return ob


def delete_long_branch_pipes():
    ob = bpy.data.objects.get("PROP_Z10_SprinklerBranches")
    if ob is None or ob.type != 'MESH':
        raise RuntimeError("PROP_Z10_SprinklerBranches missing")
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()

    unseen = set(bm.faces)
    components = []
    while unseen:
        seed = next(iter(unseen))
        stack = [seed]
        unseen.discard(seed)
        faces = []
        while stack:
            f = stack.pop()
            faces.append(f)
            for e in f.edges:
                for nf in e.link_faces:
                    if nf in unseen:
                        unseen.discard(nf)
                        stack.append(nf)
        components.append(faces)

    removed_pipes = []
    removed_tees = []
    doit = []
    for faces in components:
        vs = {v for f in faces for v in f.verts}
        ws = [ob.matrix_world @ v.co for v in vs]
        xs = [p.x for p in ws]
        ys = [p.y for p in ws]
        zs = [p.z for p in ws]
        dx = max(xs) - min(xs)
        dy = max(ys) - min(ys)
        dz = max(zs) - min(zs)
        cx = (max(xs) + min(xs)) * 0.5
        cy = (max(ys) + min(ys)) * 0.5
        if (dy > 19.0 and dx < 0.12 and dz < 0.12 and
                (abs(cx - 45.0) < 0.2 or abs(cx - 55.0) < 0.2)):
            doit.extend(faces)
            removed_pipes.append({"cx": cx, "dy": dy, "faces": len(faces)})
        elif (0.09 < dx < 0.12 and 0.09 < dy < 0.12 and
              0.09 < dz < 0.12 and abs(cy - 17.0) < 0.2 and
              (abs(cx - 45.0) < 0.2 or abs(cx - 55.0) < 0.2)):
            doit.extend(faces)
            removed_tees.append({"cx": cx, "cy": cy, "faces": len(faces)})

    if doit:
        bmesh.ops.delete(bm, geom=doit, context='FACES')
        loose = [v for v in bm.verts if not v.link_faces]
        if loose:
            bmesh.ops.delete(bm, geom=loose, context='VERTS')
        bm.to_mesh(me)
        me.update()
    bm.free()
    return removed_pipes, removed_tees


def cut_conflicting_head():
    ob = bpy.data.objects.get("P0B4_SPRINKLER_HEADS")
    if ob is None:
        raise RuntimeError("P0B4_SPRINKLER_HEADS missing")
    before = sum(len(p.vertices) - 2 for p in ob.data.polygons)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(55.0, 17.0, 3.4775))
    cutter = bpy.context.active_object
    cutter.name = "P0B5B_HEAD_CUTTER"
    cutter.scale = (0.12, 0.12, 0.745)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    mod = ob.modifiers.new("P0B5B_CUT", 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.solver = 'EXACT'
    mod.object = cutter
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)

    after = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    return before, after


def stats(ob):
    me = ob.data
    me.calc_loop_triangles()
    bm = bmesh.new()
    bm.from_mesh(me)
    nonman = sum(1 for e in bm.edges if len(e.link_faces) > 2)
    deg = sum(1 for f in bm.faces if f.calc_area() < 1e-10)
    bm.free()
    return {"tris": len(me.loop_triangles), "verts": len(me.vertices),
            "non_manifold_edges": nonman, "degenerate_faces": deg,
            "uv": bool(me.uv_layers)}


def main():
    os.makedirs(os.path.dirname(BACKUP), exist_ok=True)
    if not os.path.exists(BACKUP):
        shutil.copy2(BLEND, BACKUP)

    col = bpy.data.collections.get(COLL)
    if col is None:
        col = bpy.data.collections.new(COLL)
        bpy.context.scene.collection.children.link(col)

    # Idempotent: remove previous P0b.5b objects.
    for ob in list(col.objects):
        if ob.name.startswith("P0B5_SPRINKLER_BRANCHES") or \
           ob.name.startswith("P0B5_SPRINKLER_TEES") or \
           ob.name.startswith("P0B5_SPRINKLER_ESCUTCHEONS"):
            bpy.data.objects.remove(ob, do_unlink=True)

    removed_pipes, removed_tees = delete_long_branch_pipes()
    head_before, head_after = cut_conflicting_head()

    branches = build_branches(col)
    tees = build_tees(col)
    esc = build_escutcheons(col)
    bpy.context.view_layer.update()

    qa = {
        "generation": "P0B5B",
        "removed_branch_pipes": removed_pipes,
        "removed_old_tees": removed_tees,
        "head_cut": {"before_tris": head_before, "after_tris": head_after},
        "objects": {},
    }
    for ob in (branches, tees, esc):
        qa["objects"][ob.name] = stats(ob)
    qa["branches_source"] = stats(bpy.data.objects["PROP_Z10_SprinklerBranches"])
    qa["heads_source"] = stats(bpy.data.objects["P0B4_SPRINKLER_HEADS"])
    with open(os.path.join(DOCS, "fm_p0b5b_qa.json"), "w", encoding="utf-8") as f:
        json.dump(qa, f, indent=2)

    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("P0B5B_DONE", {k: v["tris"] for k, v in qa["objects"].items()},
          "heads", head_before, head_after)


main()
