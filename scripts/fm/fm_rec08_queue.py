import bpy
import bmesh
import json
import math
import os
import shutil
import sys

from mathutils import Vector

sys.path.insert(0, "/home/riyo/Documentos/game/scripts/fm")
from fm_shared_p0_lib import ensure_materials, box, cyl, cone, join_group, _pbr, srgb

ROOT = "/home/riyo/Documentos/game"
BLEND = os.path.join(ROOT, "nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend")
BACKUP = os.path.join(ROOT, "docs/backups/FM_LEVEL1_V06_ARCH_before_rec08.blend")
QA = os.path.join(ROOT, "docs/fm_rec08_queue_qa.json")
R8_NAME = "L1_RECEPTION_R8_HERO"
RETIRED_NAME = "L1_RECEPTION_RETIRED"

M = ensure_materials()
CHROME = M["steel_bare"]
DARK = M["steel_dark"]
GALV = M["galv"]
BLACK = M["plastic"]
ORANGE = M["paint_orange"]
BELT = _pbr("M_REC08_Belt", srgb(18, 20, 19), 0.0, 0.90,
            scale=140, bump=0.0004, micro=300, rough_var=0.03)
# Direct matte fabric values so the belt reads black, not chrome.
_belt_bsdf = next(n for n in BELT.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
for _inp in ("Base Color", "Roughness"):
    for _link in list(_belt_bsdf.inputs[_inp].links):
        BELT.node_tree.links.remove(_link)
_belt_bsdf.inputs["Base Color"].default_value = (0.006, 0.007, 0.006, 1.0)
_belt_bsdf.inputs["Roughness"].default_value = 0.94
if "Specular IOR Level" in _belt_bsdf.inputs:
    _belt_bsdf.inputs["Specular IOR Level"].default_value = 0.03
RUBBER = _pbr("M_REC08_Rubber", srgb(8, 9, 8), 0.0, 0.92)


def coll_get(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


R8 = coll_get(R8_NAME)
RETIRED = coll_get(RETIRED_NAME)


def clean_r8():
    for ob in list(R8.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for ob in list(bpy.data.objects):
        if ob.name.startswith("REC08_"):
            bpy.data.objects.remove(ob, do_unlink=True)


def retire_old():
    names = []
    for ob in list(bpy.data.objects):
        if ob.type != 'MESH':
            continue
        n = ob.name
        if (n.startswith("PROP_REC02_Barrier_") or
                n.startswith("PROP_REC02_Belt_") or
                n.startswith("PROP_REC02_Stanchion")):
            for c in list(ob.users_collection):
                c.objects.unlink(ob)
            RETIRED.objects.link(ob)
            ob.hide_render = True
            ob.hide_viewport = True
            names.append(n)
    return names


def B(parts, name, sx, sy, sz, center, mat, bevel=0.002, seg=2):
    ob = box(R8, name, sx, sy, sz, center, mat, bevel, seg)
    parts.append(ob)
    return ob


def C(parts, name, r, depth, center, mat, axis='Z', seg=24, bevel=0.0008):
    ob = cyl(R8, name, r, depth, center, mat, axis, seg, bevel, 2)
    parts.append(ob)
    return ob


def K(parts, name, r1, r2, depth, center, mat, axis='Z', seg=24, bevel=0.0008):
    ob = cone(R8, name, r1, r2, depth, center, mat, axis, seg, bevel, 2)
    parts.append(ob)
    return ob


def screw(parts, x, y, z, r=0.006):
    C(parts, "screw", r, 0.006, (x, y, z), DARK, seg=12, bevel=0.00025)
    B(parts, "screw_slot", r * 1.15, 0.0016, 0.0012,
      (x, y, z + 0.0034), CHROME, bevel=0.0)


def add_base(parts, x, y):
    C(parts, "base_rubber", 0.158, 0.008, (x, y, 0.004), RUBBER, seg=32, bevel=0.0012)
    C(parts, "base", 0.152, 0.026, (x, y, 0.021), CHROME, seg=32, bevel=0.0025)
    C(parts, "base_rim", 0.138, 0.006, (x, y, 0.036), GALV, seg=32, bevel=0.001)
    C(parts, "post_collar", 0.058, 0.030, (x, y, 0.048), DARK, seg=24, bevel=0.0015)
    for ang in (45, 135, 225, 315):
        a = math.radians(ang)
        screw(parts, x + math.cos(a) * 0.108, y + math.sin(a) * 0.108, 0.036)


def add_post(parts, x, y, height=0.90):
    K(parts, "post", 0.031, 0.024, height - 0.11, (x, y, 0.06 + (height - 0.11) / 2),
      CHROME, seg=24, bevel=0.0012)
    C(parts, "post_bottom_ring", 0.034, 0.026, (x, y, 0.055), CHROME, seg=24, bevel=0.0015)
    C(parts, "post_top_ring", 0.030, 0.024, (x, y, 0.855), CHROME, seg=24, bevel=0.0012)
    C(parts, "post_band", 0.0275, 0.012, (x, y, 0.825), ORANGE, seg=24, bevel=0.001)
    C(parts, "post_cap", 0.026, 0.018, (x, y, 0.885), CHROME, seg=24, bevel=0.0015)
    C(parts, "post_dome", 0.019, 0.008, (x, y, 0.897), CHROME, seg=20, bevel=0.0015)
    # small NEXUS marker on the south face of the post
    B(parts, "post_badge", 0.016, 0.002, 0.009, (x, y - 0.025, 0.755), ORANGE, bevel=0.0)


def add_cassette(parts, x, y, z, dx, dy):
    along_y = abs(dy) > 0.5
    cx = x + dx * 0.052
    cy = y + dy * 0.052
    sx, sy = (0.096, 0.076) if along_y else (0.076, 0.096)
    B(parts, "cassette", sx, sy, 0.078, (cx, cy, z), BLACK, bevel=0.008, seg=3)
    # belt slot on the outgoing face
    if along_y:
        B(parts, "belt_slot", 0.014, 0.006, 0.062,
          (cx, cy + dy * 0.041, z), DARK, bevel=0.001)
    else:
        B(parts, "belt_slot", 0.006, 0.014, 0.062,
          (cx + dx * 0.041, cy, z), DARK, bevel=0.001)
    # tension knob
    C(parts, "tension_knob", 0.013, 0.012, (cx, cy, z + 0.045), ORANGE, seg=16, bevel=0.001)
    C(parts, "tension_washer", 0.018, 0.003, (cx, cy, z + 0.038), GALV, seg=16, bevel=0.0005)
    # round side plate at the outer end of the housing
    if along_y:
        C(parts, "cassette_disc_L", 0.029, 0.006, (cx - 0.049, cy, z), GALV, axis='X', seg=20, bevel=0.001)
        C(parts, "cassette_disc_R", 0.029, 0.006, (cx + 0.049, cy, z), GALV, axis='X', seg=20, bevel=0.001)
        screw(parts, cx - 0.049, cy, z + 0.021, 0.0045)
        screw(parts, cx + 0.049, cy, z + 0.021, 0.0045)
    else:
        C(parts, "cassette_disc_N", 0.029, 0.006, (cx, cy - 0.049, z), GALV, axis='Y', seg=20, bevel=0.001)
        C(parts, "cassette_disc_S", 0.029, 0.006, (cx, cy + 0.049, z), GALV, axis='Y', seg=20, bevel=0.001)
        screw(parts, cx, cy - 0.049, z + 0.021, 0.0045)
        screw(parts, cx, cy + 0.049, z + 0.021, 0.0045)


def finalize(ob, name):
    ob.name = name
    ob.data.name = name
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    R8.objects.link(ob)
    ob.hide_render = False
    ob.hide_viewport = False
    return ob


def add_stanchion(name, x, y, dirs):
    parts = []
    add_base(parts, x, y)
    add_post(parts, x, y)
    for dx, dy, cz in dirs:
        add_cassette(parts, x, y, cz, dx, dy)
    ob = join_group(R8, name, parts, uv=True, wn=True)
    return finalize(ob, name)


def belt_ribbon(name, x0, y0, x1, y1, z0, sag, width, thick, mat,
                segments=28, normal_offset=0.0, z_offset=0.0):
    dx = x1 - x0
    dy = y1 - y0
    length = math.hypot(dx, dy)
    if length < 1e-6:
        return None
    nx = -dy / length
    ny = dx / length
    verts = []
    for i in range(segments + 1):
        t = i / segments
        cx = x0 + dx * t + nx * normal_offset
        cy = y0 + dy * t + ny * normal_offset
        cz = z0 - sag * math.sin(math.pi * t) + z_offset
        for side in (-1, 1):
            for up in (-1, 1):
                verts.append((cx + nx * side * thick / 2,
                              cy + ny * side * thick / 2,
                              cz + up * width / 2))
    faces = []

    def idx(i, side, up):
        return i * 4 + (1 if side > 0 else 0) * 2 + (1 if up > 0 else 0)

    for i in range(segments):
        faces.append((idx(i, -1, 1), idx(i, 1, 1), idx(i + 1, 1, 1), idx(i + 1, -1, 1)))
        faces.append((idx(i, -1, -1), idx(i + 1, -1, -1), idx(i + 1, 1, -1), idx(i, 1, -1)))
        faces.append((idx(i, -1, -1), idx(i, -1, 1), idx(i + 1, -1, 1), idx(i + 1, -1, -1)))
        faces.append((idx(i, 1, -1), idx(i + 1, 1, -1), idx(i + 1, 1, 1), idx(i, 1, 1)))
    faces.append((idx(0, -1, -1), idx(0, 1, -1), idx(0, 1, 1), idx(0, -1, 1)))
    faces.append((idx(segments, -1, -1), idx(segments, -1, 1), idx(segments, 1, 1), idx(segments, 1, -1)))

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    mesh.validate()
    ob = bpy.data.objects.new(name, mesh)
    R8.objects.link(ob)
    ob.data.materials.append(mat)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(mesh)
    bm.free()
    for p in mesh.polygons:
        p.use_smooth = True
    return ob


def add_belt(name, x0, y0, x1, y1, z0=0.90, sag=0.012):
    parts = []
    main = belt_ribbon(name + "_MAIN", x0, y0, x1, y1, z0, sag, 0.050, 0.0022, BELT)
    parts.append(main)
    ob = join_group(R8, name, parts, uv=True, wn=True)
    return finalize(ob, name)


def add_barrier():
    # post at the west side, belt receiver at the east side
    parts = []
    add_base(parts, -86.25, -9.75)
    add_post(parts, -86.25, -9.75, 0.92)
    add_cassette(parts, -86.25, -9.75, 0.92, 1.0, 0.0)
    post = join_group(R8, "REC08_BARRIER_POST", parts, uv=True, wn=True)
    finalize(post, "REC08_BARRIER_POST")

    parts = []
    C(parts, "receiver_base_rubber", 0.120, 0.007, (-84.25, -9.75, 0.0035), RUBBER, seg=28, bevel=0.001)
    C(parts, "receiver_base", 0.112, 0.022, (-84.25, -9.75, 0.016), CHROME, seg=28, bevel=0.002)
    C(parts, "receiver_stem", 0.018, 0.862, (-84.25, -9.75, 0.455), CHROME, seg=20, bevel=0.001)
    C(parts, "receiver_cap", 0.024, 0.020, (-84.25, -9.75, 0.896), CHROME, seg=20, bevel=0.0015)
    B(parts, "receiver_plate", 0.048, 0.032, 0.085, (-84.22, -9.75, 0.90), GALV, bevel=0.003)
    B(parts, "receiver_slot", 0.008, 0.022, 0.062, (-84.202, -9.75, 0.90), DARK, bevel=0.001)
    C(parts, "receiver_band", 0.020, 0.012, (-84.25, -9.75, 0.80), ORANGE, seg=20, bevel=0.001)
    for ang in (45, 135, 225, 315):
        a = math.radians(ang)
        screw(parts, -84.25 + math.cos(a) * 0.078, -9.75 + math.sin(a) * 0.078, 0.028)
    recv = join_group(R8, "REC08_BARRIER_RECEIVER", parts, uv=True, wn=True)
    finalize(recv, "REC08_BARRIER_RECEIVER")

    add_belt("REC08_BARRIER_BELT", -86.17, -9.75, -84.33, -9.75, z0=0.90, sag=0.006)
    return post, recv


def qa_stats(ob):
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    non_manifold = sum(1 for e in bm.edges if not e.is_manifold)
    degenerate = 0
    for f in bm.faces:
        if f.calc_area() < 1e-10:
            degenerate += 1
    bm.free()
    bb = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    mn = [min(v[i] for v in bb) for i in range(3)]
    mx = [max(v[i] for v in bb) for i in range(3)]
    return {
        "tris": len(me.polygons) * 2,
        "verts": len(me.vertices),
        "polys": len(me.polygons),
        "non_manifold": non_manifold,
        "degenerate": degenerate,
        "uv": len(me.uv_layers) > 0,
        "bbox_min": [round(v, 4) for v in mn],
        "bbox_max": [round(v, 4) for v in mx],
    }


def main():
    if os.path.exists(BLEND) and not os.path.exists(BACKUP):
        shutil.copy2(BLEND, BACKUP)
    clean_r8()
    retired = retire_old()

    add_stanchion("REC08_STANCHION_A", -89.0, -10.5, [(0, 1, 0.90), (1, 0, 0.84)])
    add_stanchion("REC08_STANCHION_B", -89.0, -13.5, [(0, 1, 0.90)])
    add_stanchion("REC08_STANCHION_C", -86.0, -13.5, [(0, 1, 0.90)])
    add_stanchion("REC08_STANCHION_D", -86.0, -10.5, [(0, -1, 0.90), (-1, 0, 0.84)])

    add_belt("REC08_BELT_A", -89.0, -13.5, -89.0, -10.5, sag=0.012)
    add_belt("REC08_BELT_B", -86.0, -13.5, -86.0, -10.5, sag=0.012)
    add_belt("REC08_BELT_C", -89.0, -10.5, -86.0, -10.5, z0=0.84, sag=0.008)
    add_barrier()

    bpy.context.view_layer.update()
    objs = [o for o in R8.objects if o.type == 'MESH']
    stats = {o.name: qa_stats(o) for o in sorted(objs, key=lambda x: x.name)}
    total_tris = sum(s["tris"] for s in stats.values())
    total_verts = sum(s["verts"] for s in stats.values())
    bb = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    mn = [round(min(v[i] for v in bb), 4) for i in range(3)]
    mx = [round(max(v[i] for v in bb), 4) for i in range(3)]
    report = {
        "collection": R8_NAME,
        "objects": stats,
        "total_tris": total_tris,
        "total_verts": total_verts,
        "bbox_min": mn,
        "bbox_max": mx,
        "retired": retired,
        "retired_count": len(retired),
        "notes": {
            "queue": "4 stanchions with dual cassettes at corners, 3 sagging belts with stitching, retractable barrier with receiver at the security desk",
            "old_queue_retired": "PROP_REC02_Barrier_*, PROP_REC02_Belt_*, PROP_REC02_Stanchion* moved to L1_RECEPTION_RETIRED and hidden",
        },
    }
    with open(QA, "w") as fh:
        json.dump(report, fh, indent=2)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("REC08_DONE", total_tris, total_verts, len(objs), len(retired))
    for n, s in stats.items():
        print("REC08_OBJ", n, s["tris"], s["non_manifold"], s["degenerate"], s["uv"])


main()
