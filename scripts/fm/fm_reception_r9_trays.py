import bpy
import bmesh
import json
import math
import os
import shutil
import sys
from mathutils import Matrix, Vector

ROOT = "/home/riyo/Documentos/game"
BLEND = os.path.join(ROOT, "nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend")
BACKUP = os.path.join(ROOT, "docs/backups/FM_LEVEL1_V06_ARCH_before_reception_r9_trays.blend")
QA = os.path.join(ROOT, "docs/fm_reception_r9_trays_qa.json")
sys.path.insert(0, os.path.join(ROOT, "scripts/fm"))
from fm_shared_p0_lib import box, cyl, join_group, ensure_materials  # noqa: E402

SCENE = bpy.data.scenes["NEXUS_L1_V06_ARCH"]
HERO = "L1_RECEPTION_R9_HERO"
RETIRED = "L1_RECEPTION_RETIRED_R9"
M = ensure_materials()

N_Y = -9.3
N_Z = 4.40
N_X0, N_X1 = -110.0, -70.0
W_X = -109.4
W_Z = 4.40
W_Y0, W_Y1 = -40.0, -8.0


def col(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        SCENE.collection.children.link(c)
    return c


def relink(ob, target):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    target.objects.link(ob)


def tris_of(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def stats(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.normal_update()
    nonmanifold = sum(1 for e in bm.edges if not e.is_manifold)
    degenerate = sum(1 for f in bm.faces if f.calc_area() < 1e-9)
    uv = len(bm.loops.layers.uv) > 0
    bm.free()
    return {
        "name": ob.name,
        "tris": tris_of(ob),
        "verts": len(ob.data.vertices),
        "polys": len(ob.data.polygons),
        "nonmanifold": nonmanifold,
        "degenerate": degenerate,
        "uv": uv,
    }


def cut_run(hero, name, length, loc, rot_z=0.0):
    src = bpy.data.objects.get("P0B_TRAY_RUN_400")
    if src is None:
        raise RuntimeError("P0B_TRAY_RUN_400 missing")
    me = src.data.copy()
    me.name = name + "_MESH"
    ob = bpy.data.objects.new(name, me)
    hero.objects.link(ob)
    bm = bmesh.new()
    bm.from_mesh(me)
    geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
    bmesh.ops.bisect_plane(
        bm, geom=geom, dist=1e-6,
        plane_co=(length, 0.0, 0.0), plane_no=(-1.0, 0.0, 0.0),
        clear_inner=True,
    )
    boundary = [e for e in bm.edges if e.is_boundary]
    if boundary:
        try:
            bmesh.ops.holes_fill(bm, edges=boundary, sides=0)
        except Exception as exc:
            print("HOLES_FILL_WARN", repr(exc))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(me)
    bm.free()
    me.update()
    ob.matrix_world = Matrix.Translation(loc) @ Matrix.Rotation(math.radians(rot_z), 4, 'Z')
    ob["fm_class"] = "SERVICE"
    ob["fm_family"] = "TRAY"
    ob["fm_generation"] = "VERIFIED_RECEPTION_R9"
    ob["fm_source_master"] = "P0B_TRAY_RUN_400"
    ob["fm_length_m"] = round(length, 3)
    return ob


def copy_mesh(src_name, name, matrix, target):
    src = bpy.data.objects.get(src_name)
    if src is None or src.type != 'MESH':
        raise RuntimeError("missing mesh " + src_name)
    ob = src.copy()
    ob.data = src.data
    ob.name = name
    target.objects.link(ob)
    ob.parent = None
    ob.matrix_world = matrix
    return ob


def in_reception(ob):
    pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    return (
        min(p.x for p in pts) >= -110.7 and max(p.x for p in pts) <= -69.3
        and min(p.y for p in pts) >= -40.7 and max(p.y for p in pts) <= -7.3
        and min(p.z for p in pts) >= -0.2 and max(p.z for p in pts) <= 5.6
    )


def aabb_of(objs):
    pts = []
    for ob in objs:
        pts.extend(ob.matrix_world @ Vector(c) for c in ob.bound_box)
    return [[round(min(p[i] for p in pts), 3) for i in range(3)],
            [round(max(p[i] for p in pts), 3) for i in range(3)]]


def main():
    os.makedirs(os.path.dirname(BACKUP), exist_ok=True)
    if not os.path.exists(BACKUP):
        shutil.copy2(BLEND, BACKUP)
        print("BACKUP", BACKUP)

    hero = col(HERO)
    retired = col(RETIRED)
    retired.hide_render = True
    retired.hide_viewport = True

    for ob in list(bpy.data.objects):
        if ob.name.startswith("REC09_TRAY_"):
            bpy.data.objects.remove(ob, do_unlink=True)

    retired_names = []
    for ob in list(bpy.data.objects):
        if ob.name.startswith("KIT_REC01_Tray_"):
            relink(ob, retired)
            ob.hide_render = True
            ob.hide_viewport = True
            retired_names.append(ob.name)
    print("RETIRED_OLD", len(retired_names), retired_names)

    n_run = cut_run(hero, "REC09_TRAY_N", N_X1 - N_X0, (N_X0, N_Y, N_Z), 0.0)
    w_run = cut_run(hero, "REC09_TRAY_W", W_Y1 - W_Y0, (W_X, W_Y0, W_Z), 90.0)

    # N: trapeze hangers from the ceiling, avoiding Y beams.
    np = []
    for x in (-106.0, -99.0, -93.0, -87.0, -81.0, -75.0):
        for y in (N_Y - 0.21, N_Y + 0.21):
            np.append(cyl(hero, "REC09_TRAY_N_ROD", 0.012, 0.76,
                          (x, y, 4.81), M["steel_dark"], axis='Z', seg=10, bevel=0.0002))
            np.append(cyl(hero, "REC09_TRAY_N_BOLT", 0.008, 0.018,
                          (x, y, 5.17), M["steel_bare"], axis='Z', seg=8, bevel=0.0002))
        np.append(box(hero, "REC09_TRAY_N_BAR", 0.52, 0.05, 0.05,
                      (x, N_Y, 4.32), M["steel_dark"], bevel=0.001, seg=2))
        np.append(box(hero, "REC09_TRAY_N_PLATE", 0.09, 0.09, 0.012,
                      (x, N_Y, 5.18), M["steel_dark"], bevel=0.001, seg=2))
    n_sup = join_group(hero, "REC09_TRAY_N_SUPPORTS", np, uv=True, wn=True)

    # W: wall cantilever brackets.
    wp = []
    for y in (-37.0, -34.0, -31.0, -25.0, -22.0, -16.0, -13.0, -10.0):
        wp.append(box(hero, "REC09_TRAY_W_PLATE", 0.025, 0.22, 0.30,
                      (-109.985, y, 4.40), M["steel_dark"], bevel=0.001, seg=2))
        wp.append(box(hero, "REC09_TRAY_W_ARM", 0.62, 0.06, 0.05,
                      (-109.69, y, 4.34), M["galv"], bevel=0.001, seg=2))
        for yy in (y - 0.07, y + 0.07):
            wp.append(cyl(hero, "REC09_TRAY_W_BOLT", 0.008, 0.022,
                          (-109.986, yy, 4.43), M["steel_bare"], axis='X', seg=8, bevel=0.0003))
    w_sup = join_group(hero, "REC09_TRAY_W_SUPPORTS", wp, uv=True, wn=True)

    # Cables and ties.
    def cables(name, axis, length, center, offsets, step, tie_size):
        parts = []
        for off, mat in zip(offsets, (M["rubber"], M["steel_dark"], M["paint_orange"])):
            if axis == 'X':
                parts.append(cyl(hero, "CABLE", 0.012, length,
                                 (center[0], center[1] + off, center[2]), mat,
                                 axis='X', seg=8, bevel=0.0002))
            else:
                parts.append(cyl(hero, "CABLE", 0.012, length,
                                 (center[0] + off, center[1], center[2]), mat,
                                 axis='Y', seg=8, bevel=0.0002))
        t = -length / 2.0 + 0.5
        while t < length / 2.0 - 0.2:
            if axis == 'X':
                parts.append(box(hero, "TIE", 0.035, 0.44, 0.022,
                                 (center[0] + t, center[1], center[2] + 0.035),
                                 M["steel_bare"], bevel=0.0004, seg=1))
            else:
                parts.append(box(hero, "TIE", 0.44, 0.035, 0.022,
                                 (center[0], center[1] + t, center[2] + 0.035),
                                 M["steel_bare"], bevel=0.0004, seg=1))
            t += step
        return join_group(hero, name, parts, uv=True, wn=True)

    n_cab = cables("REC09_TRAY_N_CABLES", 'X', 39.6, (-90.0, N_Y, 4.46), (-0.16, 0.0, 0.16), 1.5, 0.44)
    w_cab = cables("REC09_TRAY_W_CABLES", 'Y', 31.6, (W_X, -24.0, 4.46), (-0.16, 0.0, 0.16), 1.5, 0.44)

    caps = []
    for x, y, z, sx, sy in (
        (N_X0, N_Y, N_Z, 0.02, 0.44), (N_X1, N_Y, N_Z, 0.02, 0.44),
        (W_X, W_Y0, W_Z, 0.44, 0.02), (W_X, W_Y1, W_Z, 0.44, 0.02),
    ):
        caps.append(box(hero, "CAP", sx, sy, 0.12, (x, y, z),
                        M["steel_dark"], bevel=0.001, seg=2))
    caps_ob = join_group(hero, "REC09_TRAY_CAPS", caps, uv=True, wn=True)
    # Los cuatro remates se construyen en coordenadas de mundo. El join heredó
    # una rotación de 1° del primer objeto y desplazaba los remates lejanos.
    # La malla local ya está en la posición correcta: se fuerza identidad.
    caps_ob.location = (0.0, 0.0, 0.0)
    caps_ob.rotation_euler = (0.0, 0.0, 0.0)
    caps_ob.scale = (1.0, 1.0, 1.0)

    sleeves = []
    for i, (x, y, rot) in enumerate((
        (N_X0, N_Y, 0.0), (N_X1, N_Y, 0.0),
        (W_X, W_Y0, 90.0), (W_X, W_Y1, 90.0),
    )):
        sleeve = copy_mesh(
            "SM_SH_SLEEVE_TRAY_400",
            f"REC09_TRAY_SLEEVE_{i:02d}",
            Matrix.Translation((x, y, 4.40)) @ Matrix.Rotation(math.radians(rot), 4, 'Z'),
            hero,
        )
        sleeve["fm_class"] = "SERVICE"
        sleeve["fm_family"] = "TRAY"
        sleeve["fm_generation"] = "VERIFIED_RECEPTION_R9"
        sleeve["fm_source_master"] = "SM_SH_SLEEVE_TRAY_400"
        sleeves.append(sleeve)

    bpy.context.view_layer.update()
    new_objs = [n_run, w_run, n_sup, w_sup, n_cab, w_cab, caps_ob] + sleeves
    rows = [stats(o) for o in new_objs]
    for o in new_objs:
        o["fm_tris"] = tris_of(o)

    retired_visible = [ob.name for ob in bpy.data.objects
                       if ob.name in retired_names and not ob.hide_render]
    report = {
        "objects": rows,
        "total_tris": sum(r["tris"] for r in rows),
        "retired": retired_names,
        "retired_visible": retired_visible,
        "inside": all(in_reception(o) for o in new_objs),
        "aabb": aabb_of(new_objs),
        "north": {"x": [N_X0, N_X1], "y": N_Y, "z": N_Z},
        "west": {"y": [W_Y0, W_Y1], "x": W_X, "z": W_Z},
        "qa_pass": all(r["nonmanifold"] == 0 and r["degenerate"] == 0 and r["uv"] for r in rows),
    }
    with open(QA, "w") as fh:
        json.dump(report, fh, indent=2)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("REC09_TRAYS_DONE", json.dumps({
        "objects": len(rows),
        "tris": report["total_tris"],
        "qa_pass": report["qa_pass"],
        "inside": report["inside"],
        "aabb": report["aabb"],
        "retired": len(retired_names),
    }))


main()
