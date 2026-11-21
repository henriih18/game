"""FRECUENCIA MUERTA - Security access corridor sector export (headless only).

Builds `assets/models/fm/security_access_sector.glb` from the current V06
master.  Exports by selection: it never deletes objects and never saves the
.blend.

The corridor has no dedicated collection.  Its 11 shell meshes live in
`L1_ARCH_ALTERNATE` under the shared prefix `SM_L1_Alt_SecurityCorridor_`:

  horizontal run  x -70.85 .. -38.2   y 10.0 .. 11.8   z -0.2 .. 2.4
  vertical branch x -38.4  .. -36.6   y  4.0 .. 11.8   z -0.2 .. 2.4

It starts at the north wall of the main corridor (opening x -38.2 .. -36.8)
and enters the east wall of Security (opening y 10.2 .. 11.6).  Floor top is
z = 0.0, same datum as corridor_sector and security_sector, so the three
sectors share one Godot origin with no vertical step.

The corridor has no props, services or doors in V06: only the shell and one
emergency light (`LIGHT_L1_SecurityCorridor`, excluded) plus the floor
annotation `ANNOT_L1_SecurityCorridor` (excluded by token).  The Security east
wall blockout and the main corridor north wall already belong to their own
sectors and are deliberately not duplicated here.

Run:
  /opt/blender/blender -b nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend \
      --python scripts/fm/fm_security_access_export_headless.py
"""
import bpy
import json
import os
import struct
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
GLB = os.path.join(ROOT, "assets/models/fm/security_access_sector.glb")
REPORT = os.path.join(ROOT, "docs/fm_security_access_sector_export.json")

COLLECTION = "L1_ARCH_ALTERNATE"
NAME_PREFIX = "SM_L1_Alt_SecurityCorridor_"

# Objects that must never reach the sector, even if they match the prefix.
EXCLUDE_TOKENS = (
    "LOD1", "LOD2", "_LOD",
    "RETIRED", "LIB_", "STUDIO", "ANNOT_",
    "P0_TEST", "PLAYER", "VAL_", "LAB_",
    "FM_LIBRARY", "L1_SHARED_HERO", "DOORS",
)

# Expected shell meshes.  Used as a completeness check, not as the filter.
EXPECTED = (
    "SM_L1_Alt_SecurityCorridor_Ceiling_H",
    "SM_L1_Alt_SecurityCorridor_Ceiling_V",
    "SM_L1_Alt_SecurityCorridor_Floor_H",
    "SM_L1_Alt_SecurityCorridor_Floor_V",
    "SM_L1_Alt_SecurityCorridor_Wall_E",
    "SM_L1_Alt_SecurityCorridor_Wall_N_0",
    "SM_L1_Alt_SecurityCorridor_Wall_N_1",
    "SM_L1_Alt_SecurityCorridor_Wall_N_2",
    "SM_L1_Alt_SecurityCorridor_Wall_N_V",
    "SM_L1_Alt_SecurityCorridor_Wall_S",
    "SM_L1_Alt_SecurityCorridor_Wall_W",
)

# Selection volume (slightly padded).  Covers both runs of the corridor.
REGION_MIN = Vector((-71.3, 3.7, -0.5))
REGION_MAX = Vector((-36.3, 12.1, 2.7))

# Tight envelope used for stray validation (centre of each object).
ENVELOPE_MIN = Vector((-71.1, 4.0, -0.3))
ENVELOPE_MAX = Vector((-36.5, 11.9, 2.5))


def world_aabb(ob):
    corners = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    mn = Vector((min(p.x for p in corners),
                 min(p.y for p in corners),
                 min(p.z for p in corners)))
    mx = Vector((max(p.x for p in corners),
                 max(p.y for p in corners),
                 max(p.z for p in corners)))
    return mn, mx


def excluded(name):
    return any(token in name for token in EXCLUDE_TOKENS)


def inside_region(ob):
    mn, mx = world_aabb(ob)
    ctr = (mn + mx) * 0.5
    return (REGION_MIN.x <= ctr.x <= REGION_MAX.x and
            REGION_MIN.y <= ctr.y <= REGION_MAX.y and
            REGION_MIN.z <= ctr.z <= REGION_MAX.z)


def collect():
    col = bpy.data.collections.get(COLLECTION)
    if col is None:
        raise RuntimeError("missing collection " + COLLECTION)
    selected = {}
    rejected = []
    for ob in col.all_objects:
        if ob is None or ob.type != "MESH":
            continue
        if not ob.name.startswith(NAME_PREFIX):
            continue
        if excluded(ob.name) or not inside_region(ob):
            rejected.append(ob.name)
            continue
        selected[ob.name] = ob
    return selected, rejected


# ---------------------------------------------------------------- GLB check
def mat4_identity():
    return [1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0]


def mat4_mul(a, b):
    out = [0.0] * 16
    for c in range(4):
        for r in range(4):
            out[c * 4 + r] = sum(a[k * 4 + r] * b[c * 4 + k] for k in range(4))
    return out


def mat4_from_trs(t, r, s):
    x, y, z, w = r
    xx, yy, zz = x * x, y * y, z * z
    xy, xz, yz = x * y, x * z, y * z
    wx, wy, wz = w * x, w * y, w * z
    return [
        (1 - 2 * (yy + zz)) * s[0], (2 * (xy + wz)) * s[0], (2 * (xz - wy)) * s[0], 0.0,
        (2 * (xy - wz)) * s[1], (1 - 2 * (xx + zz)) * s[1], (2 * (yz + wx)) * s[1], 0.0,
        (2 * (xz + wy)) * s[2], (2 * (yz - wx)) * s[2], (1 - 2 * (xx + yy)) * s[2], 0.0,
        t[0], t[1], t[2], 1.0,
    ]


def node_matrix(node):
    if "matrix" in node:
        return list(node["matrix"])
    return mat4_from_trs(
        node.get("translation", [0.0, 0.0, 0.0]),
        node.get("rotation", [0.0, 0.0, 0.0, 1.0]),
        node.get("scale", [1.0, 1.0, 1.0]),
    )


def transform_point(m, p):
    return (
        m[0] * p[0] + m[4] * p[1] + m[8] * p[2] + m[12],
        m[1] * p[0] + m[5] * p[1] + m[9] * p[2] + m[13],
        m[2] * p[0] + m[6] * p[1] + m[10] * p[2] + m[14],
    )


def read_glb(path):
    with open(path, "rb") as f:
        data = f.read()
    magic, version, length = struct.unpack_from("<III", data, 0)
    if magic != 0x46546C67:
        raise RuntimeError("not a GLB")
    offset = 12
    doc = None
    while offset < length:
        chunk_len, chunk_type = struct.unpack_from("<II", data, offset)
        offset += 8
        chunk = data[offset:offset + chunk_len]
        offset += chunk_len
        if chunk_type == 0x4E4F534A:
            doc = json.loads(chunk.decode("utf-8"))
    if doc is None:
        raise RuntimeError("GLB without JSON chunk")
    return doc, len(data)


def inspect_glb(path):
    doc, size = read_glb(path)
    accessors = doc.get("accessors", [])
    meshes = doc.get("meshes", [])
    nodes = doc.get("nodes", [])

    tris = 0
    for mesh in meshes:
        for prim in mesh.get("primitives", []):
            if prim.get("mode", 4) != 4:
                continue
            if "indices" in prim:
                tris += accessors[prim["indices"]]["count"] // 3
            else:
                tris += accessors[prim["attributes"]["POSITION"]]["count"] // 3

    mn = [1e9, 1e9, 1e9]
    mx = [-1e9, -1e9, -1e9]
    mesh_nodes = 0
    roots = []
    for scene in doc.get("scenes", []):
        roots.extend(scene.get("nodes", []))
    if not roots:
        roots = list(range(len(nodes)))
    stack = [(i, mat4_identity()) for i in roots]
    while stack:
        index, parent = stack.pop()
        node = nodes[index]
        world = mat4_mul(parent, node_matrix(node))
        if "mesh" in node:
            mesh_nodes += 1
            for prim in meshes[node["mesh"]].get("primitives", []):
                acc = accessors[prim["attributes"]["POSITION"]]
                lo, hi = acc.get("min"), acc.get("max")
                if lo is None or hi is None:
                    continue
                for xs in (lo[0], hi[0]):
                    for ys in (lo[1], hi[1]):
                        for zs in (lo[2], hi[2]):
                            p = transform_point(world, (xs, ys, zs))
                            for i in range(3):
                                mn[i] = min(mn[i], p[i])
                                mx[i] = max(mx[i], p[i])
        for child in node.get("children", []):
            stack.append((child, world))

    lights = 0
    if "KHR_lights_punctual" in doc.get("extensions", {}):
        lights = len(doc["extensions"]["KHR_lights_punctual"].get("lights", []))
    cameras = len(doc.get("cameras", []))
    forbidden = [n.get("name", "") for n in nodes
                 if any(t.lower() in n.get("name", "").lower()
                        for t in EXCLUDE_TOKENS)]
    return {
        "bytes": size,
        "meshes": len(meshes),
        "mesh_nodes": mesh_nodes,
        "nodes": len(nodes),
        "materials": len(doc.get("materials", [])),
        "images": len(doc.get("images", [])),
        "tris": tris,
        "cameras": cameras,
        "lights": lights,
        "animations": len(doc.get("animations", [])),
        "skins": len(doc.get("skins", [])),
        "aabb_gltf_min": [round(v, 4) for v in mn],
        "aabb_gltf_max": [round(v, 4) for v in mx],
        # GLB is Y-up and Godot keeps Y-up: no extra axis conversion.
        "aabb_godot_position": [round(v, 4) for v in mn],
        "aabb_godot_size": [round(mx[i] - mn[i], 4) for i in range(3)],
        "forbidden_nodes": forbidden,
    }


# --------------------------------------------------------------------- main
def main():
    view_layer = bpy.context.view_layer

    # Hidden collections are not evaluated and report identity matrices.
    hidden_collections = []
    col = bpy.data.collections.get(COLLECTION)
    if col is not None and (col.hide_viewport or col.hide_render):
        hidden_collections.append((col, col.hide_viewport, col.hide_render))
        col.hide_viewport = False
        col.hide_render = False
        view_layer.update()

    selected, rejected = collect()
    missing = [n for n in EXPECTED if n not in selected]
    if missing:
        raise RuntimeError("security access corridor incomplete, missing: "
                           + ", ".join(missing))
    if rejected:
        print("SECURITY_ACCESS_REJECTED " + json.dumps(rejected))
    if len(selected) != len(EXPECTED):
        raise RuntimeError("unexpected extra meshes: "
                           + json.dumps(sorted(set(selected) - set(EXPECTED))))

    # Flatten parent transforms so no studio/player hierarchy is pulled in.
    saved_parents = {}
    for ob in selected.values():
        if ob.parent is not None:
            saved_parents[ob.name] = (ob.parent, ob.matrix_world.copy())
            world = ob.matrix_world.copy()
            ob.parent = None
            ob.matrix_world = world
    view_layer.update()

    saved_hide = {}
    bpy.ops.object.select_all(action="DESELECT")
    for ob in selected.values():
        saved_hide[ob.name] = (ob.hide_render, ob.hide_viewport, ob.hide_get())
        ob.hide_render = False
        ob.hide_viewport = False
        ob.hide_set(False)
        ob.select_set(True)
    view_layer.objects.active = selected[sorted(selected)[0]]
    view_layer.update()

    # Bake object scale into mesh data (in memory only).  Negative or
    # non-uniform node scales flip winding in importers.
    for ob in selected.values():
        if ob.data.users > 1:
            ob.data = ob.data.copy()
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    view_layer.update()

    os.makedirs(os.path.dirname(GLB), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=GLB,
        export_format="GLB",
        use_selection=True,
        use_visible=False,
        export_apply=True,
        export_cameras=False,
        export_lights=False,
        export_animations=False,
        export_extras=True,
        export_yup=True,
    )

    bpy.ops.object.select_all(action="DESELECT")
    for name, (parent, world) in saved_parents.items():
        ob = bpy.data.objects.get(name)
        if ob is not None:
            ob.parent = parent
            ob.matrix_world = world
    for name, (hr, hv, hs) in saved_hide.items():
        ob = bpy.data.objects.get(name)
        if ob is not None:
            ob.hide_render, ob.hide_viewport = hr, hv
            ob.hide_set(hs)
    for c, hv, hr in hidden_collections:
        c.hide_viewport, c.hide_render = hv, hr
    view_layer.update()

    tris = 0
    materials = set()
    images = set()
    points = []
    strays = []
    for name, ob in selected.items():
        tris += sum(len(p.vertices) - 2 for p in ob.data.polygons)
        materials.update(m.name for m in ob.data.materials if m is not None)
        if ob.data.materials:
            for m in ob.data.materials:
                if m is None or not m.use_nodes:
                    continue
                for node in m.node_tree.nodes:
                    if node.type == "TEX_IMAGE" and node.image is not None:
                        images.add(node.image.name)
        mn, mx = world_aabb(ob)
        points.extend([mn, mx])
        ctr = (mn + mx) * 0.5
        if (ctr.x < ENVELOPE_MIN.x or ctr.x > ENVELOPE_MAX.x or
                ctr.y < ENVELOPE_MIN.y or ctr.y > ENVELOPE_MAX.y or
                ctr.z < ENVELOPE_MIN.z or ctr.z > ENVELOPE_MAX.z):
            strays.append(name)

    mn = [min(p[i] for p in points) for i in range(3)]
    mx = [max(p[i] for p in points) for i in range(3)]
    glb = inspect_glb(GLB)

    report = {
        "glb_path": GLB,
        "blend": bpy.data.filepath,
        "collection": COLLECTION,
        "name_prefix": NAME_PREFIX,
        "region_blender": [[round(v, 2) for v in REGION_MIN],
                           [round(v, 2) for v in REGION_MAX]],
        "objects": len(selected),
        "unique_meshes": len({ob.data.name for ob in selected.values()}),
        "tris_blender": tris,
        "materials": len(materials),
        "material_names": sorted(materials),
        "images": len(images),
        "image_names": sorted(images),
        "aabb_blender": [[round(v, 4) for v in mn], [round(v, 4) for v in mx]],
        "aabb_godot_position": [round(mn[0], 4), round(mn[2], 4), round(-mx[1], 4)],
        "aabb_godot_size": [round(mx[0] - mn[0], 4),
                            round(mx[2] - mn[2], 4),
                            round(mx[1] - mn[1], 4)],
        "names": sorted(selected.keys()),
        "strays": strays,
        "glb": glb,
    }
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    summary = {
        "objects": report["objects"],
        "unique_meshes": report["unique_meshes"],
        "tris_blender": tris,
        "materials": report["material_names"],
        "bytes": glb["bytes"],
        "aabb_godot_position": report["aabb_godot_position"],
        "aabb_godot_size": report["aabb_godot_size"],
        "strays": strays,
        "glb_cameras": glb["cameras"],
        "glb_lights": glb["lights"],
        "glb_meshes": glb["meshes"],
        "glb_tris": glb["tris"],
        "forbidden_nodes": glb["forbidden_nodes"],
    }
    print("SECURITY_ACCESS_EXPORT " + json.dumps(summary, separators=(",", ":")))
    print("SECURITY_ACCESS_REPORT " + REPORT)

    if strays or glb["cameras"] or glb["lights"] or glb["forbidden_nodes"]:
        raise RuntimeError("security access sector validation failed")


main()
