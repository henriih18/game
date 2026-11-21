import bpy
import bmesh
import json
import math
import os
import shutil
import sys
from mathutils import Matrix

ROOT = "/home/riyo/Documentos/game"
BLEND = os.path.join(ROOT, "nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend")
BACKUP = os.path.join(ROOT, "docs/backups/FM_LEVEL1_V06_ARCH_before_p0b5c_feeds.blend")
QA = os.path.join(ROOT, "docs/fm_p0b5c_qa.json")
COL = "L1_P0B5_Z10"
RETIRED = "Z10_RETIRED_P0B4"
SCENE = bpy.data.scenes["NEXUS_L1_V06_ARCH"]

sys.path.insert(0, os.path.join(ROOT, "scripts/fm"))
from fm_shared_p0_lib import box, cyl, join_group  # noqa: E402


def mat(name):
    m = bpy.data.materials.get(name)
    if m is None:
        raise RuntimeError("Missing material " + name)
    return m


def torus(col, name, center, major, minor, rot, material):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major, minor_radius=minor,
        major_segments=20, minor_segments=8,
        location=center, rotation=rot,
    )
    ob = bpy.context.active_object
    ob.name = name
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    col.objects.link(ob)
    ob.data.materials.append(material)
    return ob


def radial_box(col, name, center, angle, sx, sy, sz, offset, material):
    """Radial detail in the YZ plane (wheel/gauge axis = X)."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=bm.verts)
    bmesh.ops.translate(bm, vec=(0.0, offset, 0.0), verts=bm.verts)
    bmesh.ops.rotate(bm, cent=(0.0, 0.0, 0.0),
                     matrix=Matrix.Rotation(angle, 3, 'X'), verts=bm.verts)
    bmesh.ops.translate(bm, vec=center, verts=bm.verts)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    ob.data.materials.append(material)
    return ob


def spoke(col, name, center, angle, material):
    return radial_box(col, name, center, angle, 0.008, 0.050, 0.009, 0.0335, material)


def clear_previous():
    col = bpy.data.collections.get(COL)
    if not col:
        return
    for ob in list(col.objects):
        if ob.name.startswith("P0B5_FEED_") or ob.name.startswith("P0B5_FEED_SUPPORT"):
            bpy.data.objects.remove(ob, do_unlink=True)


def retire_old():
    old = bpy.data.objects.get("PROP_Z10_SprinklerFeeds")
    if not old:
        return None
    ret = bpy.data.collections.get(RETIRED)
    if not ret:
        ret = bpy.data.collections.new(RETIRED)
        SCENE.collection.children.link(ret)
    for c in list(old.users_collection):
        c.objects.unlink(old)
    ret.objects.link(old)
    old.hide_render = True
    old.hide_viewport = True
    old.hide_set(True)
    return old.name


def stats(ob):
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    nm = sum(1 for e in bm.edges if not e.is_manifold)
    dg = sum(1 for f in bm.faces if f.calc_area() < 1e-10)
    bm.free()
    return {
        "tris": sum(len(p.vertices) - 2 for p in me.polygons),
        "verts": len(me.vertices),
        "non_manifold": nm,
        "degenerate": dg,
        "uv": bool(me.uv_layers),
    }


def build_feed(col, name, x, y0, y1, vy, couplings, red, steel, brass, white, dark):
    parts = []
    depth = y1 - y0
    cy = (y0 + y1) / 2.0
    z = 3.90
    parts.append(cyl(col, name + "_PIPE", 0.035, depth, (x, cy, z), red, axis='Y', seg=20, bevel=0.0006))
    # Bridas de extremo.
    for yy in (y0 + 0.015, y1 - 0.015):
        parts.append(cyl(col, name + f"_FLANGE_{yy:.3f}", 0.058, 0.030, (x, yy, z), red, axis='Y', seg=20, bevel=0.0008))
        for k in range(6):
            a = 2 * math.pi * k / 6
            parts.append(cyl(col, name + f"_BOLT_{yy:.3f}_{k}", 0.008, 0.010,
                             (x + 0.044 * math.cos(a), yy, z + 0.044 * math.sin(a)),
                             steel, axis='Y', seg=8, bevel=0.0002))
    # Acoplamientos intermedios, lejos del conducto y de la válvula.
    for k, yy in enumerate(couplings):
        parts.append(cyl(col, name + f"_COUPLING_{k}", 0.048, 0.040, (x, yy, z), red, axis='Y', seg=20, bevel=0.0006))
    # Válvula de compuerta con volante horizontal, visible bajo el techo.
    wheel_x = x - 0.265
    parts.append(cyl(col, name + "_VALVE_BODY", 0.055, 0.130, (x, vy, z), red, axis='Y', seg=20, bevel=0.0008))
    parts.append(cyl(col, name + "_BONNET", 0.032, 0.080, (x - 0.095, vy, z), brass, axis='X', seg=16, bevel=0.0004))
    parts.append(cyl(col, name + "_PACKING", 0.020, 0.018, (x - 0.142, vy, z), brass, axis='X', seg=12, bevel=0.0003))
    parts.append(cyl(col, name + "_STEM", 0.010, 0.110, (x - 0.202, vy, z), steel, axis='X', seg=10, bevel=0.0002))
    parts.append(torus(col, name + "_WHEEL", (wheel_x, vy, z), 0.060, 0.009,
                       (0.0, math.radians(90), 0.0), red))
    parts.append(cyl(col, name + "_HUB", 0.016, 0.020, (wheel_x, vy, z), brass, axis='X', seg=12, bevel=0.0003))
    for k in range(6):
        parts.append(spoke(col, name + f"_SPOKE_{k}", (wheel_x, vy, z),
                           math.radians(k * 60.0), red))
    # Manómetro orientado al oeste (-X), con cuello y tuerca de unión.
    gy = vy + 0.30
    parts.append(cyl(col, name + "_GAUGE_NIPPLE", 0.008, 0.042, (x - 0.056, gy, z), steel, axis='X', seg=8, bevel=0.0002))
    parts.append(cyl(col, name + "_GAUGE_BODY", 0.038, 0.024, (x - 0.089, gy, z), brass, axis='X', seg=16, bevel=0.0004))
    parts.append(cyl(col, name + "_GAUGE_RIM", 0.041, 0.006, (x - 0.103, gy, z), steel, axis='X', seg=16, bevel=0.0003))
    parts.append(cyl(col, name + "_GAUGE_FACE", 0.032, 0.003, (x - 0.107, gy, z), white, axis='X', seg=16, bevel=0.0002))
    face_x = x - 0.1095
    parts.append(radial_box(col, name + "_GAUGE_NEEDLE", (face_x, gy, z),
                            math.radians(120.0), 0.0015, 0.026, 0.0026, 0.016, dark))
    for k in range(12):
        parts.append(radial_box(col, name + f"_GAUGE_TICK_{k:02d}", (face_x, gy, z),
                                math.radians(k * 30.0), 0.0012, 0.006, 0.0018, 0.027, dark))
    # Soporte de techo.
    sy = y0 + depth * 0.55
    parts.append(cyl(col, name + "_ROD", 0.008, 0.12, (x, sy, z + 0.10), steel, axis='Z', seg=8, bevel=0.0002))
    parts.append(box(col, name + "_CLAMP", 0.095, 0.045, 0.030, (x, sy, z + 0.035), steel, bevel=0.002, seg=2))
    parts.append(box(col, name + "_PLATE", 0.16, 0.10, 0.012, (x, sy, z + 0.084), steel, bevel=0.002, seg=2))
    return join_group(col, name, parts, uv=True, wn=True)


def main():
    if not os.path.exists(BACKUP):
        shutil.copy2(BLEND, BACKUP)
        print("BACKUP", BACKUP)

    old = retire_old()
    clear_previous()
    col = bpy.data.collections.get(COL)
    if not col:
        col = bpy.data.collections.new(COL)
        SCENE.collection.children.link(col)

    red = mat("M_SH_Sprinkler_Red")
    steel = mat("M_SH_Steel_Stainless")
    brass = mat("M_SH_Brass")
    dark = mat("M_SH_Steel_Dark")
    white = mat("M_SH_GaugeFace") if bpy.data.materials.get("M_SH_GaugeFace") else bpy.data.materials.new("M_SH_GaugeFace")
    if not white.use_nodes:
        white.use_nodes = True
    bsdf = next(n for n in white.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = (0.72, 0.72, 0.68, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.35

    a = build_feed(col, "P0B5_FEED_A", 46.275, 15.805, 17.035, 16.55, [],
                   red, steel, brass, white, dark)
    b = build_feed(col, "P0B5_FEED_B", 55.725, 17.035, 23.800, 21.55, [18.45, 22.35],
                   red, steel, brass, white, dark)
    for ob in (a, b):
        ob["fm_class"] = "SERVICE"
        ob["fm_family"] = "SPRINKLER_FEED"
        ob["fm_generation"] = "VERIFIED_P0B5C_R2"
    bpy.context.view_layer.update()

    data = {
        "retired": old,
        "revision": "R2 horizontal side-stem valves, clear of duct and ceiling",
        "layout": {
            "pipe_z": 3.90,
            "valve_a_y": 16.55,
            "valve_b_y": 21.55,
            "wheel_top_z": 3.969,
            "ceiling_underside_z": 3.99,
            "duct_top_z": 3.85,
            "duct_y": [19.57, 20.43],
            "gauge_axis": "-X",
        },
        "objects": {},
    }
    ok = True
    for ob in (a, b):
        s = stats(ob)
        data["objects"][ob.name] = s
        ok = ok and s["non_manifold"] == 0 and s["degenerate"] == 0 and s["uv"]
    data["qa_pass"] = ok
    with open(QA, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("P0B5C_FEEDS_DONE", json.dumps(data, ensure_ascii=False))


main()
