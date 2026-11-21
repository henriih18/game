import bpy
import bmesh
import json
import math
import os
import shutil
import sys
from mathutils import Euler, Matrix, Vector

ROOT = "/home/riyo/Documentos/game"
BLEND = os.path.join(ROOT, "nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend")
BACKUP = os.path.join(ROOT, "docs/backups/FM_LEVEL1_V06_ARCH_before_reception_r12_waiting.blend")
QA = os.path.join(ROOT, "docs/fm_reception_r12_waiting_qa.json")
COL = "L1_RECEPTION_R12_HERO"
RETIRED = "L1_RECEPTION_RETIRED"
SCENE = bpy.data.scenes["NEXUS_L1_V06_ARCH"]

sys.path.insert(0, os.path.join(ROOT, "scripts/fm"))
from fm_shared_p0_lib import box, cyl, join_group, _pbr, srgb  # noqa: E402


def ensure_collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        SCENE.collection.children.link(col)
    return col


def clear_collection(col):
    for ob in list(col.objects):
        bpy.data.objects.remove(ob, do_unlink=True)


def retire(prefixes):
    col = bpy.data.collections.get(RETIRED)
    if col is None:
        col = bpy.data.collections.new(RETIRED)
        SCENE.collection.children.link(col)
    moved = []
    for ob in list(SCENE.objects):
        if any(ob.name.startswith(p) for p in prefixes):
            for c in list(ob.users_collection):
                c.objects.unlink(ob)
            col.objects.link(ob)
            ob.hide_render = True
            ob.hide_viewport = True
            ob.hide_set(True)
            moved.append(ob.name)
    return moved


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


def bench(col, name, cy, mats):
    steel, wood, rubber = mats
    parts = []
    cx = -109.54
    # Patas y bastidores laterales.
    for sy in (-1.02, 1.02):
        y = cy + sy
        parts.append(box(col, name + "_LEG_F", 0.045, 0.045, 0.42,
                         (-109.32, y, 0.21), steel, bevel=0.002, seg=2))
        parts.append(box(col, name + "_LEG_B", 0.045, 0.045, 0.98,
                         (-109.78, y, 0.49), steel, bevel=0.002, seg=2))
        parts.append(box(col, name + "_RAIL_F", 0.045, 0.045, 0.045,
                         (-109.32, y, 0.44), steel, bevel=0.002, seg=2))
        parts.append(box(col, name + "_RAIL_TOP", 0.50, 0.045, 0.045,
                         (-109.55, y, 0.44), steel, bevel=0.002, seg=2))
        parts.append(box(col, name + "_ARM", 0.52, 0.055, 0.035,
                         (-109.54, y, 0.66), steel, bevel=0.003, seg=2))
        parts.append(box(col, name + "_FOOT_F", 0.075, 0.075, 0.012,
                         (-109.32, y, 0.006), rubber, bevel=0.001, seg=1))
        parts.append(box(col, name + "_FOOT_B", 0.075, 0.075, 0.012,
                         (-109.78, y, 0.006), rubber, bevel=0.001, seg=1))
        parts.append(cyl(col, name + "_BOLT_A", 0.010, 0.006,
                         (-109.32, y - 0.032, 0.40), steel, axis='Y', seg=10, bevel=0.0004))
        parts.append(cyl(col, name + "_BOLT_B", 0.010, 0.006,
                         (-109.32, y - 0.032, 0.24), steel, axis='Y', seg=10, bevel=0.0004))
    # Travesaños bajo el asiento.
    for x in (-109.70, -109.36):
        parts.append(box(col, name + "_CROSS", 0.045, 2.09, 0.045,
                         (x, cy, 0.38), steel, bevel=0.002, seg=2))
    # Listones de asiento.
    for i, x in enumerate((-109.72, -109.59, -109.46, -109.33)):
        parts.append(box(col, name + f"_SEAT_SLAT_{i}", 0.105, 2.08, 0.038,
                         (x, cy, 0.465), wood, bevel=0.003, seg=2))
    # Listones de respaldo.
    for i, z in enumerate((0.58, 0.70, 0.82, 0.94)):
        parts.append(box(col, name + f"_BACK_SLAT_{i}", 0.038, 2.08, 0.095,
                         (-109.795, cy, z), wood, bevel=0.003, seg=2))
    # Topes de pared y tornillos de listones.
    for i, z in enumerate((0.58, 0.70, 0.82, 0.94)):
        for sy in (-1.00, 1.00):
            parts.append(cyl(col, name + f"_SCREW_{i}_{sy}", 0.007, 0.008,
                             (-109.80, cy + sy, z), steel, axis='X', seg=8, bevel=0.0003))
    return join_group(col, name, parts, uv=True, wn=True)


def table(col, mats):
    steel, wood, paper = mats
    parts = []
    cx, cy = -107.40, -21.80
    parts.append(box(col, "REC12_TABLE_TOP", 1.20, 0.80, 0.050,
                     (cx, cy, 0.425), wood, bevel=0.004, seg=3))
    parts.append(box(col, "REC12_TABLE_APRON_X", 1.08, 0.05, 0.070,
                     (cx, cy - 0.35, 0.365), steel, bevel=0.002, seg=2))
    parts.append(box(col, "REC12_TABLE_APRON_X2", 1.08, 0.05, 0.070,
                     (cx, cy + 0.35, 0.365), steel, bevel=0.002, seg=2))
    parts.append(box(col, "REC12_TABLE_APRON_Y", 0.05, 0.70, 0.070,
                     (cx - 0.54, cy, 0.365), steel, bevel=0.002, seg=2))
    parts.append(box(col, "REC12_TABLE_APRON_Y2", 0.05, 0.70, 0.070,
                     (cx + 0.54, cy, 0.365), steel, bevel=0.002, seg=2))
    for sx in (-0.52, 0.52):
        for sy in (-0.33, 0.33):
            parts.append(box(col, f"REC12_TABLE_LEG_{sx}_{sy}", 0.045, 0.045, 0.40,
                             (cx + sx, cy + sy, 0.20), steel, bevel=0.002, seg=2))
            parts.append(box(col, f"REC12_TABLE_FOOT_{sx}_{sy}", 0.070, 0.070, 0.010,
                             (cx + sx, cy + sy, 0.005), wood, bevel=0.001, seg=1))
    parts.append(box(col, "REC12_TABLE_SHELF", 1.02, 0.62, 0.025,
                     (cx, cy, 0.16), wood, bevel=0.002, seg=2))
    parts.append(box(col, "REC12_TABLE_MAG", 0.28, 0.20, 0.008,
                     (cx - 0.15, cy + 0.08, 0.454), paper, bevel=0.001, seg=1))
    parts.append(box(col, "REC12_TABLE_MAG2", 0.24, 0.17, 0.006,
                     (cx - 0.13, cy + 0.10, 0.462), paper, bevel=0.001, seg=1))
    return join_group(col, "REC12_TABLE", parts, uv=True, wn=True)


def planter(col, mats):
    concrete, soil, leaf, stem = mats
    parts = []
    cx, cy = -105.50, -19.50
    parts.append(box(col, "REC12_PLANTER_BODY", 0.56, 0.56, 0.72,
                     (cx, cy, 0.36), concrete, bevel=0.006, seg=3))
    parts.append(box(col, "REC12_PLANTER_RIM_N", 0.60, 0.045, 0.035,
                     (cx, cy + 0.28, 0.725), concrete, bevel=0.003, seg=2))
    parts.append(box(col, "REC12_PLANTER_RIM_S", 0.60, 0.045, 0.035,
                     (cx, cy - 0.28, 0.725), concrete, bevel=0.003, seg=2))
    parts.append(box(col, "REC12_PLANTER_RIM_E", 0.045, 0.56, 0.035,
                     (cx + 0.28, cy, 0.725), concrete, bevel=0.003, seg=2))
    parts.append(box(col, "REC12_PLANTER_RIM_W", 0.045, 0.56, 0.035,
                     (cx - 0.28, cy, 0.725), concrete, bevel=0.003, seg=2))
    parts.append(box(col, "REC12_PLANTER_SOIL", 0.48, 0.48, 0.025,
                     (cx, cy, 0.715), soil, bevel=0.002, seg=2))
    # Tallos y hojas estilizados.
    for i, (dx, dy, h, tilt) in enumerate((
        (-0.10, -0.08, 0.34, -0.18), (0.04, -0.12, 0.42, 0.12),
        (0.13, 0.02, 0.30, 0.22), (-0.02, 0.11, 0.38, -0.10),
        (-0.14, 0.10, 0.26, -0.24), (0.10, 0.14, 0.35, 0.16),
    )):
        base = (cx + dx, cy + dy, 0.73)
        parts.append(cyl(col, f"REC12_STEM_{i}", 0.009, h,
                         (base[0], base[1], 0.73 + h / 2), stem, axis='Z', seg=8, bevel=0.0003))
        for j in range(3):
            z = 0.78 + h * (0.42 + 0.18 * j)
            sx = 0.16 + 0.03 * j
            sy = 0.028 + 0.004 * j
            sz = 0.09 + 0.02 * j
            center = Vector((base[0] + tilt * (0.30 + 0.25 * j), base[1] + 0.02 * (j - 1), z))
            ob = box(col, f"REC12_LEAF_{i}_{j}", sx, sy, sz,
                     tuple(center), leaf, bevel=0.006, seg=2)
            parts.append(ob)
            rot = Euler((0.18 * (j - 1), 0.28 * (1 if j % 2 else -1), tilt * 1.6 + 0.35 * j)).to_matrix().to_4x4()
            ob.data.transform(Matrix.Translation(center) @ rot @ Matrix.Translation(-center))
    return join_group(col, "REC12_PLANTER", parts, uv=True, wn=True)


def main():
    if not os.path.exists(BACKUP):
        shutil.copy2(BLEND, BACKUP)
        print("BACKUP", BACKUP)

    retired = retire((
        "PROP_REC02_Bench_A_", "PROP_REC02_Bench_B_", "PROP_REC02_Table_",
        "PROP_REC02_Waiting_Planter", "PROP_REC02_Waiting_PlanterSoil",
    ))
    col = ensure_collection(COL)
    clear_collection(col)

    steel = _pbr("M_REC12_Steel", srgb(42, 46, 44), 0.75, 0.38,
                 scale=70, bump=0.0005, micro=360, rough_var=0.06)
    wood = _pbr("M_REC12_Wood", srgb(108, 82, 58), 0.0, 0.56,
                scale=18, bump=0.0015, micro=260, rough_var=0.10)
    rubber = _pbr("M_REC12_Rubber", srgb(14, 15, 14), 0.0, 0.82,
                  scale=180, bump=0.0004, micro=520, rough_var=0.03)
    paper = _pbr("M_REC12_Paper", srgb(198, 194, 178), 0.0, 0.86,
                 scale=70, bump=0.0002, micro=460, rough_var=0.02)
    concrete = _pbr("M_REC12_Concrete", srgb(104, 100, 92), 0.0, 0.92,
                    scale=22, bump=0.0018, micro=180, rough_var=0.05)
    soil = _pbr("M_REC12_Soil", srgb(42, 32, 22), 0.0, 0.98,
                scale=60, bump=0.0020, micro=220, rough_var=0.04)
    leaf = _pbr("M_REC12_Leaf", srgb(58, 110, 62), 0.0, 0.65,
                scale=45, bump=0.0010, micro=300, rough_var=0.08)
    stem = _pbr("M_REC12_Stem", srgb(52, 66, 38), 0.0, 0.80,
                scale=80, bump=0.0006, micro=360, rough_var=0.05)

    b = bench(col, "REC12_BENCH_A", -19.80, (steel, wood, rubber))
    b2 = bench(col, "REC12_BENCH_B", -23.80, (steel, wood, rubber))
    t = table(col, (steel, wood, paper))
    p = planter(col, (concrete, soil, leaf, stem))
    for ob in (b, b2, t, p):
        ob["fm_generation"] = "VERIFIED_RECEPTION_R12"
        ob["fm_class"] = "HERO_PROP"
    bpy.context.view_layer.update()

    data = {"collection": COL, "retired": retired, "objects": {}}
    ok = True
    for ob in (b, b2, t, p):
        s = stats(ob)
        data["objects"][ob.name] = s
        ok = ok and s["non_manifold"] == 0 and s["degenerate"] == 0 and s["uv"]
    data["qa_pass"] = ok
    with open(QA, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("REC12_WAITING_DONE", json.dumps(data, ensure_ascii=False))


main()
