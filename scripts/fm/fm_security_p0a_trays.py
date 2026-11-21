import bpy
import bmesh
import json
import math
import os
from mathutils import Matrix, Vector

ROOT = "/home/riyo/Documentos/game"
BLEND = os.path.join(ROOT, "nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend")
BACKUP = os.path.join(ROOT, "docs/backups/FM_LEVEL1_V06_ARCH_before_security_trays.blend")
QA = os.path.join(ROOT, "docs/fm_security_p0a_trays_qa.json")

HERO = "L1_SECURITY_P0A_HERO"
RETIRED = "L1_SECURITY_RETIRED_P0A"
OLD = ["R21B_SERV_WestCableTray", "R21B_SERV_CentreCableTray"]


def ensure_col(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def unlink_all(ob):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)


def retire(name, retired):
    ob = bpy.data.objects.get(name)
    if not ob:
        return False
    unlink_all(ob)
    retired.objects.link(ob)
    ob.hide_render = True
    ob.hide_viewport = True
    try:
        ob.hide_set(True)
    except Exception:
        pass
    return True


def tris(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def bbox(ob):
    pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    return [[round(min(p[i] for p in pts), 4) for i in range(3)],
            [round(max(p[i] for p in pts), 4) for i in range(3)]]


def cut_run(col, name, length, loc, rot_z=90.0):
    src = bpy.data.objects.get("P0B_TRAY_RUN_400")
    if src is None:
        raise RuntimeError("P0B_TRAY_RUN_400 missing")
    me = src.data.copy()
    me.name = name + "_MESH"
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    bm = bmesh.new()
    bm.from_mesh(me)
    geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
    bmesh.ops.bisect_plane(
        bm, geom=geom, dist=1e-6,
        plane_co=(length, 0.0, 0.0), plane_no=(-1.0, 0.0, 0.0),
        clear_inner=True,
    )
    bm.to_mesh(me)
    bm.free()
    me.update()
    ob.matrix_world = Matrix.Translation(loc) @ Matrix.Rotation(math.radians(rot_z), 4, 'Z')
    ob["fm_generation"] = "VERIFIED_SECURITY_P0A"
    ob["fm_source_master"] = "P0B_TRAY_RUN_400"
    ob["fm_length_m"] = round(length, 3)
    return ob


def main():
    import shutil
    import sys
    sys.path.insert(0, os.path.join(ROOT, "scripts/fm"))
    from fm_shared_p0_lib import ensure_materials, box, cyl, join_group

    if not os.path.exists(BACKUP):
        shutil.copy2(BLEND, BACKUP)
        print("BACKUP", BACKUP)

    scene = bpy.data.scenes["NEXUS_L1_V06_ARCH"]
    hero = ensure_col(HERO)
    retired = ensure_col(RETIRED)
    M = ensure_materials()

    # Clean previo idempotente.
    for ob in list(hero.objects):
        if ob.name.startswith("SEC_P0A_TRAY_"):
            bpy.data.objects.remove(ob, do_unlink=True)
    for n in OLD:
        retire(n, retired)

    # Bandeja oeste: 18.5 m, montada en el muro x=-105, corre en +Y.
    west = cut_run(hero, "SEC_P0A_TRAY_WEST_18M5", 18.5,
                   (-104.72, 13.0, 3.55), 90.0)
    # Bandeja central: 12 m, suspendida del techo, corre en +Y.
    centre = cut_run(hero, "SEC_P0A_TRAY_CENTRE_12M", 12.0,
                     (-84.555, 12.6, 4.30), 90.0)

    # Soportes de pared oeste (7).
    wp = []
    for y in (13.2, 16.2, 19.2, 22.2, 25.2, 28.2, 31.2):
        wp.append(box(hero, "W_PLATE", 0.025, 0.22, 0.30,
                      (-104.987, y, 3.55), M["steel_dark"], bevel=0.001, seg=2))
        wp.append(box(hero, "W_ARM", 0.56, 0.06, 0.05,
                      (-104.72, y, 3.49), M["galv"], bevel=0.001, seg=2))
        for yy in (y - 0.07, y + 0.07):
            wp.append(cyl(hero, "W_BOLT", 0.008, 0.022,
                          (-104.986, yy, 3.58), M["steel_bare"], axis='X', seg=8, bevel=0.0003))
    supports_w = join_group(hero, "SEC_P0A_TRAY_SUPPORTS_WEST", wp, uv=True, wn=True)

    # Soportes de techo central (5).
    cp = []
    for y in (13.2, 16.2, 19.2, 22.2, 24.2):
        for x in (-84.76, -84.34):
            cp.append(cyl(hero, "C_ROD", 0.012, 0.50,
                          (x, y, 4.54), M["steel_dark"], axis='Z', seg=8, bevel=0.0002))
        cp.append(box(hero, "C_BAR", 0.52, 0.05, 0.05,
                      (-84.55, y, 4.28), M["steel_dark"], bevel=0.001, seg=2))
        for x in (-84.76, -84.34):
            cp.append(cyl(hero, "C_BOLT", 0.008, 0.018,
                          (x, y, 4.255), M["steel_bare"], axis='Z', seg=8, bevel=0.0003))
    supports_c = join_group(hero, "SEC_P0A_TRAY_SUPPORTS_CENTRE", cp, uv=True, wn=True)

    # Cables y bridas.
    def cables(name, length, y0, x0, z, step):
        parts = []
        for i, (dx, mat) in enumerate(((-0.16, M["rubber"]), (0.0, M["steel_dark"]), (0.16, M["paint_orange"]))):
            parts.append(cyl(hero, "CABLE", 0.012, length,
                             (x0 + dx, y0 + length / 2.0, z), mat, axis='Y', seg=8, bevel=0.0002))
        k = 0
        y = y0 + 0.5
        while y < y0 + length - 0.2:
            for dx in (-0.16, 0.0, 0.16):
                parts.append(box(hero, "TIE", 0.035, 0.018, 0.055,
                                 (x0 + dx, y, z + 0.02), M["steel_bare"], bevel=0.0004, seg=1))
            k += 1
            y += step
        return join_group(hero, name, parts, uv=True, wn=True)

    cables_w = cables("SEC_P0A_TRAY_CABLES_WEST", 18.4, 13.05, -104.72, 3.60, 1.5)
    cables_c = cables("SEC_P0A_TRAY_CABLES_CENTRE", 11.9, 12.65, -84.555, 4.35, 1.5)

    # Tapas de extremo.
    caps = []
    for x, y, z in ((-104.72, 13.0, 3.55), (-104.72, 31.5, 3.55),
                    (-84.555, 12.6, 4.30), (-84.555, 24.6, 4.30)):
        caps.append(box(hero, "CAP", 0.47, 0.02, 0.12, (x, y, z), M["steel_dark"], bevel=0.001, seg=2))
    caps_ob = join_group(hero, "SEC_P0A_TRAY_ENDCAPS", caps, uv=True, wn=True)

    bpy.context.view_layer.update()

    new = [west, centre, supports_w, supports_c, cables_w, cables_c, caps_ob]
    qa = []
    for ob in new:
        me = ob.data
        deg = 0
        for p in me.polygons:
            if p.area < 1e-9:
                deg += 1
        qa.append({
            "name": ob.name,
            "tris": tris(ob),
            "verts": len(me.vertices),
            "degenerate": deg,
            "uv": [l.name for l in me.uv_layers],
            "bbox": bbox(ob),
            "shared_users": me.users,
        })
    retired_visible = []
    for n in OLD:
        ob = bpy.data.objects.get(n)
        if ob and not ob.hide_render:
            retired_visible.append(n)
    report = {
        "batch": "SECURITY_P0A_TRAYS",
        "objects": len(new),
        "tris": sum(x["tris"] for x in qa),
        "qa": qa,
        "retired": OLD,
        "retired_visible": retired_visible,
        "inside": all(-106 <= x["bbox"][0][0] and x["bbox"][1][0] <= -70 and
                      9 <= x["bbox"][0][1] and x["bbox"][1][1] <= 37 and
                      -0.6 <= x["bbox"][0][2] and x["bbox"][1][2] <= 5.6 for x in qa),
    }
    with open(QA, "w") as fh:
        json.dump(report, fh, indent=2)
    print("SEC_TRAY_DONE", report["objects"], report["tris"], report["inside"], retired_visible)
    for x in qa:
        print("OBJ", x["name"], x["tris"], x["degenerate"], x["uv"], x["bbox"])
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("SAVED", BLEND)


main()
