"""FRECUENCIA MUERTA - Level 1 V06 corridor sector export (headless only).

Builds `assets/models/fm/corridor_sector.glb` from the current V06 master.
It never saves the .blend and never touches existing GLBs.

Why one GLB instead of west/east halves:
  The corridor is 174 m long, but the shell is only ~60 meshes / ~267 k tris.
  The floor, ceiling and the P0B HVAC/tray/sprinkler runs are single meshes
  spanning the whole corridor, so an object-level split would either leave
  those meshes in one half or duplicate them. Splitting would need mesh
  bisection (destructive or duplicated geometry) for no measurable streaming
  win at this budget. If a future art pass raises the corridor budget, the
  split point should be x = -13 (see corredor oeste/east below).

Corridor extents (Blender, metres):
  x -100.0 .. 74.0 (174 m)   y -4.2 .. 4.2 (8.4 m)   z -0.2 .. 4.2
  West half would be x -100.0 .. -13.0, east half x -13.0 .. 74.0.

The corridor has no dedicated collection in the master. Its shell lives in
L1_ARCH_CIRCULATION (north wall, ends, door openings), L1_ARCH_ALTERNATE
(south wall segments), L1_ARCH_CEILINGS (real ceiling), and the floor is the
single mesh `SM_L1_Corridor_Main_Floor`, wrongly filed under L1_CAMERAS.
L1_ARCH_ZONES / L1_ARCH_COLUMNS contain room shells and unplaced Z10
templates only, so they contribute 0 real corridor meshes and are filtered
out by the same rules as the other collections.

Run:
  /opt/blender/blender -b nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend \
      --python scripts/fm/fm_corridor_sector_export_headless.py
"""
import bpy
import json
import math
import os
import struct
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
GLB = os.path.join(ROOT, "assets/models/fm/corridor_sector.glb")
REPORT = os.path.join(ROOT, "docs/fm_corridor_sector_export.json")

# Collections explicitly requested for the corridor sector.  ALTERNATE is
# included because the corridor south wall was authored there.
COLLECTIONS = (
    "L1_ARCH_ZONES",
    "L1_ARCH_CIRCULATION",
    "L1_ARCH_COLUMNS",
    "L1_ARCH_CEILINGS",
    "L1_ARCH_ALTERNATE",
    "L1_P0B_SERVICES",
)

# Single corridor mesh filed outside the architecture collections.
EXTRA_OBJECTS = {
    "SM_L1_Corridor_Main_Floor": "L1_CAMERAS",
}

# Objects that must never reach the sector, even if they land in the region.
EXCLUDE_TOKENS = (
    "LOD1", "LOD2", "_LOD",
    "RETIRED", "LIB_", "STUDIO", "ANNOT_",
    "P0_TEST", "PLAYER", "VAL_",
    "Zone10_ServiceConnector", "ServiceVestibule", "Column_ServiceConnector",
)

# Corridor volume used for selection (slightly padded in x/y/z).
REGION_MIN = Vector((-100.6, -4.7, -0.5))
REGION_MAX = Vector((74.6, 4.7, 4.6))

# Tight envelope used for stray validation.
ENVELOPE_MIN = Vector((-100.3, -4.3, -0.3))
ENVELOPE_MAX = Vector((74.3, 4.3, 4.3))
CONTAIN_RATIO = 0.90


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
    if not (REGION_MIN.x <= ctr.x <= REGION_MAX.x and
            REGION_MIN.y <= ctr.y <= REGION_MAX.y and
            REGION_MIN.z <= ctr.z <= REGION_MAX.z):
        return False
    # Reject huge shells / room floors that merely touch the corridor.
    ix = max(0.0, min(mx.x, REGION_MAX.x) - max(mn.x, REGION_MIN.x))
    iy = max(0.0, min(mx.y, REGION_MAX.y) - max(mn.y, REGION_MIN.y))
    footprint = max((mx.x - mn.x) * (mx.y - mn.y), 1e-6)
    return (ix * iy) / footprint >= CONTAIN_RATIO


def collect_candidates():
    selected = {}
    per_collection = {}
    for cname in COLLECTIONS:
        col = bpy.data.collections.get(cname)
        if col is None:
            print("CORRIDOR_EXPORT_MISSING_COLLECTION", cname)
            per_collection[cname] = 0
            continue
        count = 0
        for ob in col.all_objects:
            if ob is None or ob.type != "MESH":
                continue
            if excluded(ob.name):
                continue
            if not inside_region(ob):
                continue
            selected.setdefault(ob.name, ob)
            count += 1
        per_collection[cname] = count

    for name, cname in EXTRA_OBJECTS.items():
        ob = bpy.data.objects.get(name)
        if ob is not None and ob.type == "MESH" and not excluded(name):
            selected.setdefault(name, ob)
            per_collection[cname] = per_collection.get(cname, 0) + 1
    return selected, per_collection


def mesh_tris(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


# ---------------------------------------------------------------- GLB check
def mat4_identity():
    return [1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0]


def mat4_mul(a, b):
    # Column-major glTF matrices, result = a * b.
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
    m = [
        (1 - 2 * (yy + zz)) * s[0], (2 * (xy + wz)) * s[0], (2 * (xz - wy)) * s[0], 0.0,
        (2 * (xy - wz)) * s[1], (1 - 2 * (xx + zz)) * s[1], (2 * (yz + wx)) * s[1], 0.0,
        (2 * (xz + wy)) * s[2], (2 * (yz - wx)) * s[2], (1 - 2 * (xx + yy)) * s[2], 0.0,
        t[0], t[1], t[2], 1.0,
    ]
    return m


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
    node_stack = [(i, mat4_identity()) for i in roots]
    while node_stack:
        index, parent = node_stack.pop()
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
            node_stack.append((child, world))

    lights = 0
    if "KHR_lights_punctual" in doc.get("extensions", {}):
        lights = len(doc["extensions"]["KHR_lights_punctual"].get("lights", []))
    cameras = len(doc.get("cameras", []))
    forbidden = [n.get("name", "") for n in nodes
                 if any(token.lower() in n.get("name", "").lower()
                        for token in EXCLUDE_TOKENS)]
    materials = len(doc.get("materials", []))
    images = len(doc.get("images", []))
    # Node/accessor bounds are already glTF Y-up, and Godot keeps Y-up, so
    # the GLB AABB is the Godot AABB with no extra axis conversion.
    g_min = list(mn) if mn[0] < 1e8 else [0.0, 0.0, 0.0]
    g_max = list(mx) if mn[0] < 1e8 else [0.0, 0.0, 0.0]
    return {
        "bytes": size,
        "meshes": len(meshes),
        "mesh_nodes": mesh_nodes,
        "nodes": len(nodes),
        "materials": materials,
        "images": images,
        "tris": tris,
        "cameras": cameras,
        "lights": lights,
        "animations": len(doc.get("animations", [])),
        "skins": len(doc.get("skins", [])),
        "aabb_gltf_min": [round(v, 4) for v in mn],
        "aabb_gltf_max": [round(v, 4) for v in mx],
        "aabb_godot_position": [round(v, 4) for v in g_min],
        "aabb_godot_size": [round(g_max[i] - g_min[i], 4) for i in range(3)],
        "forbidden_nodes": forbidden,
    }


# --------------------------------------------------------------------- main
def main():
    # Hidden master collections are not evaluated: their objects report an
    # identity matrix_world.  Unhide the candidate collections just for the
    # export so the ceiling and template meshes get their real transforms.
    hidden_collections = []
    for cname in set(COLLECTIONS) | set(EXTRA_OBJECTS.values()):
        col = bpy.data.collections.get(cname)
        if col is not None and (col.hide_viewport or col.hide_render):
            hidden_collections.append((col, col.hide_viewport, col.hide_render))
            col.hide_viewport = False
            col.hide_render = False
    if hidden_collections:
        bpy.context.view_layer.update()

    selected, per_collection = collect_candidates()
    if not selected:
        raise RuntimeError("corridor selection is empty")

    # Flatten parent transforms so no studio/player hierarchy is pulled in.
    saved_parents = {}
    for ob in selected.values():
        if ob.parent is not None:
            saved_parents[ob.name] = (ob.parent, ob.matrix_world.copy())
            world = ob.matrix_world.copy()
            ob.parent = None
            ob.matrix_world = world
    bpy.context.view_layer.update()

    saved_hide = {}
    bpy.ops.object.select_all(action="DESELECT")
    for ob in selected.values():
        saved_hide[ob.name] = (ob.hide_render, ob.hide_viewport, ob.hide_get())
        ob.hide_render = False
        ob.hide_viewport = False
        ob.hide_set(False)
        ob.select_set(True)
    bpy.context.view_layer.objects.active = selected[sorted(selected)[0]]
    bpy.context.view_layer.update()

    # Bake object scale into the mesh data.  A few master objects (notably
    # SM_L1_Corridor_Main_Wall_N_8) carry a negative Z scale; exporting that
    # as a glTF node scale flips triangle winding in engine importers.  This
    # only mutates the in-memory headless session, never the .blend.
    for ob in selected.values():
        if ob.data.users > 1:
            ob.data = ob.data.copy()
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.context.view_layer.update()

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
    for col, hv, hr in hidden_collections:
        col.hide_viewport, col.hide_render = hv, hr
    bpy.context.view_layer.update()

    # Blender-side measurements (pre-export, authoritative for source checks).
    tris = 0
    materials = set()
    images = set()
    points = []
    strays = []
    for name, ob in selected.items():
        tris += mesh_tris(ob)
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
        "collections": list(COLLECTIONS),
        "collection_meshes": per_collection,
        "extra_objects": EXTRA_OBJECTS,
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
        "materials": len(materials),
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
    print("CORRIDOR_SECTOR_EXPORT " + json.dumps(summary, separators=(",", ":")))
    print("CORRIDOR_SECTOR_REPORT " + REPORT)

    if strays or glb["cameras"] or glb["lights"] or glb["forbidden_nodes"]:
        raise RuntimeError("corridor sector validation failed")


main()
