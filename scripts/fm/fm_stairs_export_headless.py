"""Exporta el arte de las Escaleras (Main/E1/E2) desde el master V06 a GLB.

Uso:
  blender -b nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend \
      --python scripts/fm/fm_stairs_export_headless.py

No guarda el .blend. Exporta solo las tres colecciones de arte.
"""
import bpy
import json
import os
import struct
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
REPORT = os.path.join(ROOT, "docs/fm_stairs_art_export.json")
MAX_BYTES = 20 * 1024 * 1024

SECTORS = [
    {
        "id": "Main",
        "collection": "L1_ART_STAIRS_MAIN",
        "glb": "assets/models/fm/stairs_main_art.glb",
        "expected": 18,
        # STAIRS_MAIN_BOUNDS Godot: AABB((-12.15,-4.8,4.0),(20.3,11.8,46.15)).
        # El máximo y se amplía a -1.5 para incluir la transición MEP que
        # conecta el conducto del conector con el HVAC del corredor.
        "bounds_min": Vector((-12.15, -50.15, -4.8)),
        "bounds_max": Vector((8.15, -1.5, 7.0)),
        "prefix": "ST_Main_",
    },
    {
        "id": "E1",
        "collection": "L1_ART_STAIRS_E1",
        "glb": "assets/models/fm/stairs_e1_art.glb",
        "expected": 14,
        # STAIRS_E1_BOUNDS Godot: AABB((110,-4.8,-26.15),(10.15,10.8,18.3)).
        "bounds_min": Vector((110.0, 7.85, -4.8)),
        "bounds_max": Vector((120.15, 26.15, 6.0)),
        "prefix": "ST_E1_",
    },
    {
        "id": "E2",
        "collection": "L1_ART_STAIRS_E2",
        "glb": "assets/models/fm/stairs_e2_art.glb",
        "expected": 14,
        # STAIRS_E2_BOUNDS Godot: AABB((112,-4.8,25.85),(10.15,10.8,18.3)).
        "bounds_min": Vector((112.0, -44.15, -4.8)),
        "bounds_max": Vector((122.15, -25.85, 6.0)),
        "prefix": "ST_E2_",
    },
]


def world_aabb(ob):
    corners = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    mn = Vector((min(p.x for p in corners), min(p.y for p in corners),
                 min(p.z for p in corners)))
    mx = Vector((max(p.x for p in corners), max(p.y for p in corners),
                 max(p.z for p in corners)))
    return mn, mx


def select_art(sector):
    col = bpy.data.collections.get(sector["collection"])
    if col is None:
        raise RuntimeError("missing collection " + sector["collection"])
    meshes = [o for o in col.all_objects if o.type == "MESH"]
    if len(meshes) != sector["expected"]:
        raise RuntimeError("%s: expected %d meshes, found %d" %
                           (sector["id"], sector["expected"], len(meshes)))
    bpy.ops.object.select_all(action="DESELECT")
    for ob in meshes:
        ob.hide_set(False)
        ob.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    return meshes


def downscale_images(meshes, max_size=1024):
    images = set()
    for ob in meshes:
        for slot in ob.material_slots:
            mat = slot.material
            if mat is None or not mat.use_nodes:
                continue
            for node in mat.node_tree.nodes:
                if node.type == "TEX_IMAGE" and node.image is not None:
                    images.add(node.image)
    resized = []
    for img in images:
        w, h = img.size
        if max(w, h) <= max_size:
            continue
        scale = max_size / float(max(w, h))
        nw, nh = max(1, int(round(w * scale))), max(1, int(round(h * scale)))
        img.scale(nw, nh)
        resized.append((img.name, w, h, nw, nh))
    return resized


def export_glb(sector, path):
    if os.path.exists(path):
        os.remove(path)
    bpy.ops.export_scene.gltf(
        filepath=path, export_format="GLB", use_selection=True,
        export_yup=True, export_apply=True, export_animations=False,
        export_cameras=False, export_lights=False, export_extras=True,
        export_materials="EXPORT", export_image_format="AUTO",
        export_texcoords=True, export_normals=True,
    )
    if not os.path.exists(path):
        raise RuntimeError("GLB not written: " + path)


def read_glb(path):
    with open(path, "rb") as f:
        data = f.read()
    magic, version, length = struct.unpack_from("<III", data, 0)
    if magic != 0x46546C67:
        raise RuntimeError("not a GLB: " + path)
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
        raise RuntimeError("GLB without JSON chunk: " + path)
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
    lights = 0
    if "KHR_lights_punctual" in doc.get("extensions", {}):
        lights = len(doc["extensions"]["KHR_lights_punctual"].get("lights", []))
    return {
        "bytes": size,
        "meshes": len(meshes),
        "nodes": len(nodes),
        "materials": len(doc.get("materials", [])),
        "images": len(doc.get("images", [])),
        "tris": tris,
        "cameras": len(doc.get("cameras", [])),
        "lights": lights,
        "names_sample": [n.get("name", "") for n in nodes][:12],
    }


def main():
    results = []
    for sector in SECTORS:
        meshes = select_art(sector)
        bpy.context.view_layer.update()
        mins = Vector((1e9, 1e9, 1e9))
        maxs = Vector((-1e9, -1e9, -1e9))
        for ob in meshes:
            mn, mx = world_aabb(ob)
            for i in range(3):
                mins[i] = min(mins[i], mn[i])
                maxs[i] = max(maxs[i], mx[i])
        inside = all(
            mins[i] >= sector["bounds_min"][i] - 1e-3
            and maxs[i] <= sector["bounds_max"][i] + 1e-3
            for i in range(3)
        )
        resized = downscale_images(meshes, max_size=1024)
        path = os.path.join(ROOT, sector["glb"])
        export_glb(sector, path)
        info = inspect_glb(path)
        info["id"] = sector["id"]
        info["source_objects"] = len(meshes)
        info["resized_images"] = len(resized)
        info["source_aabb_blender"] = {
            "min": [round(v, 3) for v in mins],
            "max": [round(v, 3) for v in maxs],
        }
        info["bounds_blender"] = {
            "min": [round(v, 3) for v in sector["bounds_min"]],
            "max": [round(v, 3) for v in sector["bounds_max"]],
        }
        info["aabb_inside_bounds"] = inside
        info["file"] = sector["glb"]
        info["pass"] = (
            inside
            and info["bytes"] <= MAX_BYTES
            and info["cameras"] == 0
            and info["lights"] == 0
            and info["meshes"] > 0
            and info["images"] > 0
            and any(sector["prefix"] in n for n in info["names_sample"])
        )
        results.append(info)
        print("FM_STAIRS_EXPORT", json.dumps(info, ensure_ascii=False))
    with open(REPORT, "w", encoding="utf-8") as f:
        json.dump({"sectors": results}, f, indent=2, ensure_ascii=False)
    if not all(r["pass"] for r in results):
        raise RuntimeError("Stairs GLB validation failed")


if __name__ == "__main__":
    main()
