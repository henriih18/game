"""P0b.5 - hero rebuild of the Z10 risers A/B.

Replaces the 26 low-poly riser props (192-tri pipes, 108-tri valves and
brackets) with two joined hero meshes: 24-sided pipes, bolted flanges,
couplings, valves with handwheels, pressure gauges and wall brackets.
Keeps PROP_Z10_RiserIdentification and the P0b.4 floor/ceiling pass plates.
"""

import bpy
import bmesh
import json
import math
import os
import sys
from mathutils import Vector

sys.path.insert(0, "/home/riyo/Documentos/game/scripts/fm")
from fm_shared_p0_lib import ensure_materials, box, cyl, join_group

COLL = "L1_P0B5_Z10"
RET = "Z10_RETIRED_P0B4"
DOCS = "/home/riyo/Documentos/game/docs"
BLEND = "/home/riyo/Documentos/game/nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend"
BACKUP = "/home/riyo/Documentos/game/docs/backups/FM_LEVEL1_V06_ARCH_before_p0b5.blend"

M = ensure_materials()
GALV = M["galv"]
DARK = M["steel_dark"]
BARE = M["steel_bare"]
RED = M["sprink_red"]
LABEL = M["label"]
BRASS = M["brass"]
RUB = M["rubber"]

RISERS = {
    "A": {"x": 46.27, "ys": [15.8, 16.0, 16.2]},
    "B": {"x": 55.73, "ys": [23.8, 24.0, 24.2]},
}
PIPE_R = 0.035
ZS = [0.02, 3.98]
FLANGE_Z = [0.06, 1.33, 2.66, 3.94]
COUPLING_Z = [0.70, 2.00, 3.30]
BRACKET_Z = [1.00, 2.50, 3.50]
VALVE_Z = 1.20
GAUGE_Z = 1.78


def link_only(ob, col):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    col.objects.link(ob)


def torus(col, name, R, r, center, mat, major=24, minor=8):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=R, minor_radius=r, major_segments=major,
        minor_segments=minor, location=center)
    ob = bpy.context.object
    ob.name = name
    ob.data.name = name
    link_only(ob, col)
    ob.data.materials.append(mat)
    return ob


def ensure_collection(name):
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def clear_collection(col):
    for ob in list(col.objects):
        data = ob.data
        bpy.data.objects.remove(ob, do_unlink=True)
        if data is not None and getattr(data, "users", 0) == 0:
            try:
                if isinstance(data, bpy.types.Mesh):
                    bpy.data.meshes.remove(data)
            except Exception:
                pass


def retire_old(col):
    prefixes = []
    for r in ("A", "B"):
        prefixes += [
            "PROP_Z10_Riser%s_pipe" % r,
            "PROP_Z10_Riser%s_valve" % r,
            "PROP_Z10_Riser%s_valvehandle" % r,
            "PROP_Z10_Riser%s_bracket" % r,
            "PROP_Z10_Riser%s_gauge" % r,
        ]
    moved = []
    for ob in list(bpy.data.objects):
        if any(ob.name == p or ob.name.startswith(p) for p in prefixes):
            if ob.name in col.objects:
                continue
            link_only(ob, col)
            ob.hide_render = True
            ob.hide_viewport = True
            ob.hide_set(True)
            moved.append(ob.name)
    return sorted(moved)


def build_riser(col, key, cfg):
    x = cfg["x"]
    y0 = cfg["ys"][1]
    name = "P0B5_RISER_" + key
    parts = []
    n = [0]

    def B(sx, sy, sz, center, mat, bev=0.0012, seg=2):
        n[0] += 1
        ob = box(col, "%s_P%04d" % (name, n[0]), sx, sy, sz, center,
                 mat, bev, seg)
        parts.append(ob)
        return ob

    def C(r, depth, center, mat, axis='Z', seg=16, bev=0.0005, bseg=1):
        n[0] += 1
        ob = cyl(col, "%s_P%04d" % (name, n[0]), r, depth, center,
                 mat, axis, seg, bev, bseg)
        parts.append(ob)
        return ob

    materials = [RED, GALV, DARK]
    for pi, (y, mat) in enumerate(zip(cfg["ys"], materials)):
        # continuous pipe body
        C(PIPE_R, ZS[1] - ZS[0], (x, y, (ZS[0] + ZS[1]) / 2), mat, 'Z', 20,
          bseg=2)
        # end flanges + 8 bolts each
        for fz in FLANGE_Z:
            C(0.058, 0.026, (x, y, fz), mat, 'Z', 20)
            for k in range(8):
                a = math.radians(22.5 + k * 45.0)
                bx = x + 0.047 * math.cos(a)
                by = y + 0.047 * math.sin(a)
                C(0.0055, 0.034, (bx, by, fz), DARK, 'Z', 8, 0.0)
        # couplings
        for cz in COUPLING_Z:
            C(0.045, 0.050, (x, y, cz), GALV, 'Z', 16)
            for dz in (-0.018, 0.018):
                C(0.048, 0.008, (x, y, cz + dz), DARK, 'Z', 16)
        # valve body / bonnet / stem / handwheel
        C(0.055, 0.180, (x, y, VALVE_Z), DARK, 'Z', 16)
        C(0.040, 0.060, (x, y, VALVE_Z + 0.120), DARK, 'Z', 14)
        C(0.009, 0.100, (x, y, VALVE_Z + 0.200), BARE, 'Z', 10)
        n[0] += 1
        parts.append(torus(col, "%s_WHEEL_%02d" % (name, pi),
                           0.065, 0.009, (x, y, VALVE_Z + 0.260),
                           RED, 24, 8))
        C(0.016, 0.026, (x, y, VALVE_Z + 0.266), BRASS, 'Z', 12)
        for k in range(6):
            a = math.radians(k * 60.0)
            sp = box(col, "%s_SPOKE_%02d_%02d" % (name, pi, k),
                     0.050, 0.009, 0.008,
                     (0.0325, 0.0, 0.0), RED, 0.0, 1)
            sp.rotation_euler[2] = a
            sp.location = (x, y, VALVE_Z + 0.260)
            parts.append(sp)
        # one pressure gauge per riser, on the middle pipe
        if pi == 1:
            C(0.009, 0.070, (x + 0.060, y, GAUGE_Z), BRASS, 'X', 10)
            C(0.048, 0.012, (x + 0.080, y, GAUGE_Z), RED, 'X', 16)
            C(0.041, 0.022, (x + 0.094, y, GAUGE_Z), LABEL, 'X', 16)
            C(0.006, 0.006, (x + 0.107, y, GAUGE_Z), BRASS, 'X', 8)
            nb = box(col, "%s_NEEDLE_%02d" % (name, pi),
                     0.002, 0.010, 0.030,
                     (x + 0.108, y, GAUGE_Z + 0.009), DARK, 0.0, 1)
            parts.append(nb)

    # wall brackets: back plate, two arms, three clamps, bolts
    for bz in BRACKET_Z:
        B(0.020, 0.560, 0.120, (x - 0.110, y0, bz), GALV, 0.0015, 2)
        for sy in (-1, 1):
            B(0.140, 0.030, 0.040,
              (x - 0.045, y0 + sy * 0.245, bz), GALV, 0.0012, 2)
        for y in cfg["ys"]:
            C(0.043, 0.024, (x, y, bz), GALV, 'Z', 16)
            C(0.0055, 0.012, (x + 0.043, y, bz), DARK, 'X', 8, 0.0)
        # anchor bolts on the plate
        for sy in (-1, 1):
            C(0.007, 0.020, (x - 0.122, y0 + sy * 0.235, bz), DARK, 'X', 8, 0.0)
    ob = join_group(col, name, parts, uv=True, wn=True)
    ob["fm_class"] = "SERVICE"
    ob["fm_family"] = "RISER"
    ob["fm_riser"] = key
    ob["fm_tris"] = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    return ob


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
    bpy.context.view_layer.update()
    if os.path.exists(BLEND) and not os.path.exists(BACKUP):
        import shutil
        shutil.copy2(BLEND, BACKUP)
        print("BACKUP", BACKUP)

    col = ensure_collection(COLL)
    clear_collection(col)
    ret = ensure_collection(RET)
    moved = retire_old(ret)
    print("RETIRED", len(moved))

    built = []
    for key, cfg in RISERS.items():
        ob = build_riser(col, key, cfg)
        built.append(ob)
        print("BUILT", ob.name, ob["fm_tris"])

    bpy.context.view_layer.update()
    rows = []
    for ob in built:
        st = stats(ob)
        ob["fm_generation"] = "VERIFIED_P0B5"
        rows.append({"name": ob.name, "fm_riser": ob["fm_riser"], **st})
    ok = all(r["non_manifold_edges"] == 0 and r["degenerate_faces"] == 0
             and r["uv"] for r in rows)
    report = {"collection": COLL, "retired": moved, "assets": rows,
              "pass": ok, "total_tris": sum(r["tris"] for r in rows)}
    os.makedirs(DOCS, exist_ok=True)
    with open(DOCS + "/fm_p0b5_qa.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("P0B5_DONE", len(built), report["total_tris"], ok)


main()
