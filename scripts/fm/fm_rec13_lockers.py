import bpy
import bmesh
import json
import math
import os
import shutil
import sys

ROOT = "/home/riyo/Documentos/game"
BLEND = os.path.join(ROOT, "nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend")
BACKUP = os.path.join(ROOT, "docs/backups/FM_LEVEL1_V06_ARCH_before_reception_r13_lockers.blend")
QA = os.path.join(ROOT, "docs/fm_reception_r13_lockers_qa.json")
COL = "L1_RECEPTION_R13_HERO"
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


def locker_bank(col, mats):
    painted, dark, steel, label, brass, black = mats
    parts = []
    x0, x1 = -107.20, -104.80
    y_back, y_front = -39.84, -39.36
    z0, z1 = 0.0, 1.90
    cx, cy = (x0 + x1) / 2, (y_back + y_front) / 2
    # Carcasa.
    parts.append(box(col, "REC13_LOCK_BACK", 2.40, 0.025, 1.90,
                     (cx, y_back + 0.012, 0.95), painted, bevel=0.003, seg=2))
    parts.append(box(col, "REC13_LOCK_TOP", 2.40, 0.48, 0.035,
                     (cx, cy, 1.882), painted, bevel=0.003, seg=2))
    parts.append(box(col, "REC13_LOCK_BOTTOM", 2.40, 0.48, 0.035,
                     (cx, cy, 0.018), painted, bevel=0.003, seg=2))
    parts.append(box(col, "REC13_LOCK_SIDE_L", 0.035, 0.48, 1.90,
                     (x0 + 0.0175, cy, 0.95), painted, bevel=0.003, seg=2))
    parts.append(box(col, "REC13_LOCK_SIDE_R", 0.035, 0.48, 1.90,
                     (x1 - 0.0175, cy, 0.95), painted, bevel=0.003, seg=2))
    parts.append(box(col, "REC13_LOCK_PLINTH", 2.34, 0.44, 0.08,
                     (cx, cy, 0.04), dark, bevel=0.002, seg=2))
    parts.append(box(col, "REC13_LOCK_TOP_TRIM", 2.42, 0.50, 0.028,
                     (cx, cy, 1.914), steel, bevel=0.002, seg=2))
    # Divisiones y estantes.
    for i in range(7):
        x = x0 + i * 0.40
        parts.append(box(col, f"REC13_LOCK_PART_{i}", 0.018, 0.43, 1.80,
                         (x, cy, 0.94), dark, bevel=0.0015, seg=1))
    for i in range(6):
        x = x0 + 0.20 + i * 0.40
        parts.append(box(col, f"REC13_LOCK_SHELF_{i}", 0.37, 0.40, 0.018,
                         (x, cy, 0.62), dark, bevel=0.0015, seg=1))
        # Puerta.
        parts.append(box(col, f"REC13_LOCK_DOOR_{i}", 0.382, 0.030, 1.76,
                         (x, y_front - 0.002, 0.97), painted, bevel=0.003, seg=2))
        # Rejillas de ventilación.
        for k, z in enumerate((1.18, 1.24, 1.30)):
            parts.append(box(col, f"REC13_LOCK_VENT_{i}_{k}", 0.22, 0.010, 0.020,
                             (x, y_front + 0.016, z), black, bevel=0.001, seg=1))
        # Portaetiquetas.
        parts.append(box(col, f"REC13_LOCK_PLATE_{i}", 0.15, 0.010, 0.065,
                         (x, y_front + 0.014, 1.56), label, bevel=0.001, seg=1))
        parts.append(box(col, f"REC13_LOCK_PLATE_FRAME_{i}", 0.17, 0.008, 0.085,
                         (x, y_front + 0.010, 1.56), steel, bevel=0.001, seg=1))
        # Tirador y cerradura.
        parts.append(box(col, f"REC13_LOCK_HANDLE_{i}", 0.095, 0.025, 0.022,
                         (x + 0.12, y_front + 0.030, 0.97), steel, bevel=0.002, seg=2))
        parts.append(cyl(col, f"REC13_LOCK_HANDLE_BASE_{i}", 0.018, 0.012,
                         (x + 0.12, y_front + 0.020, 0.97), dark, axis='Y', seg=12, bevel=0.001))
        parts.append(cyl(col, f"REC13_LOCK_CYL_{i}", 0.014, 0.014,
                         (x - 0.11, y_front + 0.020, 1.00), brass, axis='Y', seg=12, bevel=0.001))
        # Bisagras.
        for k, z in enumerate((0.26, 0.97, 1.68)):
            parts.append(cyl(col, f"REC13_LOCK_HINGE_{i}_{k}", 0.009, 0.075,
                             (x - 0.185, y_front + 0.012, z), dark, axis='Z', seg=10, bevel=0.0005))
        # Tornillos de puerta.
        for sx, sz in ((0.16, 0.10), (0.16, 1.84), (-0.16, 0.10), (-0.16, 1.84)):
            parts.append(cyl(col, f"REC13_LOCK_SCREW_{i}_{sx}_{sz}", 0.006, 0.006,
                             (x + sx, y_front + 0.018, sz), steel, axis='Y', seg=8, bevel=0.0003))
    # Anclajes a muro.
    for i in range(6):
        x = x0 + 0.20 + i * 0.40
        for z in (0.25, 1.65):
            parts.append(cyl(col, f"REC13_LOCK_ANCHOR_{i}_{z}", 0.012, 0.020,
                             (x, y_back + 0.004, z), steel, axis='Y', seg=10, bevel=0.0005))
    return join_group(col, "REC13_LOCKERS_HERO", parts, uv=True, wn=True)


def sign(col, name, cx, cy, cz, w, h, d, mats, mount):
    frame, panel, steel, green, label = mats
    parts = []
    parts.append(box(col, name + "_FRAME", w, d, h, (cx, cy, cz), frame, bevel=0.004, seg=3))
    parts.append(box(col, name + "_PANEL", w - 0.10, d + 0.004, h - 0.07,
                     (cx, cy, cz), panel, bevel=0.002, seg=2))
    # Franja e icono.
    parts.append(box(col, name + "_STRIPE", w - 0.16, d + 0.010, 0.030,
                     (cx, cy, cz - h / 2 + 0.055), green, bevel=0.001, seg=1))
    for i, dx in enumerate((-0.12, 0.0, 0.12)):
        parts.append(box(col, name + f"_BAR_{i}", 0.035, d + 0.012, 0.060,
                         (cx + dx, cy, cz + 0.02), label, bevel=0.001, seg=1))
    if mount == 'WALL':
        for dx in (-w / 2 + 0.18, w / 2 - 0.18):
            parts.append(cyl(col, name + f"_STAND_{dx}", 0.012, 0.08,
                             (cx + dx, cy, cz), steel, axis='Y', seg=10, bevel=0.0005))
            parts.append(cyl(col, name + f"_BOLT_{dx}", 0.018, 0.012,
                             (cx + dx, cy + 0.045, cz), frame, axis='Y', seg=10, bevel=0.0005))
    elif mount == 'HANG':
        for dx in (-w / 2 + 0.28, w / 2 - 0.28):
            parts.append(cyl(col, name + f"_ROD_{dx}", 0.008, 0.55,
                             (cx + dx, cy, cz + h / 2 + 0.275), steel, axis='Z', seg=8, bevel=0.0003))
            parts.append(cyl(col, name + f"_ROD_NUT_{dx}", 0.014, 0.012,
                             (cx + dx, cy, cz + h / 2 + 0.01), frame, axis='Z', seg=8, bevel=0.0003))
    return join_group(col, name, parts, uv=True, wn=True)


def main():
    if not os.path.exists(BACKUP):
        shutil.copy2(BLEND, BACKUP)
        print("BACKUP", BACKUP)

    retired = retire((
        "PROP_REC02_Locker_", "KIT_REC02_Sign_Lockers",
        "KIT_REC02_Sign_Decon", "KIT_REC02_Sign_Desk",
    ))
    col = ensure_collection(COL)
    clear_collection(col)

    painted = _pbr("M_REC13_PaintedGreen", srgb(42, 60, 50), 0.15, 0.56,
                   scale=10, bump=0.0002, micro=700, rough_var=0.03)
    dark = _pbr("M_REC13_SteelDark", srgb(24, 28, 26), 0.65, 0.46,
                scale=90, bump=0.0005, micro=380, rough_var=0.05)
    steel = _pbr("M_REC13_Steel", srgb(118, 122, 116), 0.85, 0.34,
                 scale=70, bump=0.0004, micro=400, rough_var=0.04)
    label = _pbr("M_REC13_Label", srgb(206, 204, 190), 0.0, 0.72,
                 scale=120, bump=0.0002, micro=520, rough_var=0.02)
    brass = _pbr("M_REC13_Brass", srgb(150, 112, 48), 0.9, 0.32,
                 scale=60, bump=0.0004, micro=340, rough_var=0.05)
    black = _pbr("M_REC13_Black", srgb(8, 9, 8), 0.0, 0.70,
                 scale=160, bump=0.0003, micro=480, rough_var=0.03)
    sign_frame = _pbr("M_REC13_SignFrame", srgb(18, 22, 20), 0.4, 0.38,
                      scale=80, bump=0.0004, micro=360, rough_var=0.04)
    sign_panel = _pbr("M_REC13_SignPanel", srgb(178, 184, 168), 0.0, 0.55,
                      scale=40, bump=0.0003, micro=500, rough_var=0.03)
    sign_green = _pbr("M_REC13_SignGreen", srgb(74, 112, 82), 0.0, 0.48,
                      scale=60, bump=0.0004, micro=360, rough_var=0.04)

    lockers = locker_bank(col, (painted, dark, steel, label, brass, black))
    s_lock = sign(col, "REC13_SIGN_LOCKERS", -106.00, -39.335, 2.06,
                  2.40, 0.32, 0.055, (sign_frame, sign_panel, steel, sign_green, label), 'WALL')
    s_decon = sign(col, "REC13_SIGN_DECON", -94.00, -33.815, 2.42,
                   3.00, 0.28, 0.050, (sign_frame, sign_panel, steel, sign_green, label), 'WALL')
    s_desk = sign(col, "REC13_SIGN_DESK", -102.00, -16.53, 3.61,
                  3.00, 0.40, 0.060, (sign_frame, sign_panel, steel, sign_green, label), 'HANG')

    for ob in (lockers, s_lock, s_decon, s_desk):
        ob["fm_generation"] = "VERIFIED_RECEPTION_R13"
        ob["fm_class"] = "HERO_PROP"
    bpy.context.view_layer.update()

    data = {"collection": COL, "retired": retired, "objects": {}}
    ok = True
    for ob in (lockers, s_lock, s_decon, s_desk):
        s = stats(ob)
        data["objects"][ob.name] = s
        ok = ok and s["non_manifold"] == 0 and s["degenerate"] == 0 and s["uv"]
    data["qa_pass"] = ok
    with open(QA, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("REC13_LOCKERS_DONE", json.dumps(data, ensure_ascii=False))


main()
