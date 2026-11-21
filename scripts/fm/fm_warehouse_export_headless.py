"""Exporta el arte del Almacén desde el master V06 a GLB.

Uso:
  blender -b nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend \
      --python scripts/fm/fm_warehouse_export_headless.py

No guarda el .blend. Exporta solo la colección L1_ART_WAREHOUSE.
"""
import bpy
import json
import os
import struct
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
GLB = os.path.join(ROOT, "assets/models/fm/warehouse_art.glb")
REPORT = os.path.join(ROOT, "docs/fm_warehouse_art_export.json")
COLLECTION = "L1_ART_WAREHOUSE"
EXPECTED_OBJECTS = 99
MAX_BYTES = 30 * 1024 * 1024

# WAREHOUSE_BOUNDS de Godot: AABB((62,-0.2,-38.15),(48.18,6.2,34.15)).
# En Blender: x 62..110.18, y 4.0..38.15, z -0.2..6.0.
# Se amplía x a 61.7 para incluir el puente de bandeja del ServiceLink,
# que forma parte del arte de servicios del Almacén.
BOUNDS_MIN = Vector((61.7, 4.0, -0.2))
BOUNDS_MAX = Vector((110.18, 38.15, 6.0))


def world_aabb(ob):
    corners = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    mn = Vector((min(p.x for p in corners), min(p.y for p in corners),
                 min(p.z for p in corners)))
    mx = Vector((max(p.x for p in corners), max(p.y for p in corners),
                 max(p.z for p in corners)))
    return mn, mx


def select_art():
    col = bpy.data.collections.get(COLLECTION)
    if col is None:
        raise RuntimeError("missing collection " + COLLECTION)
    meshes = [o for o in col.all_objects if o.type == "MESH"]
    if len(meshes) != EXPECTED_OBJECTS:
        raise RuntimeError("expected %d meshes, found %d" %
                           (EXPECTED_OBJECTS, len(meshes)))
    bpy.ops.object.select_all(action="DESELECT")
    for ob in meshes:
        ob.hide_set(False)
        ob.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    return meshes


def downscale_images(meshes, max_size=1024):
    """Reduce en memoria las texturas compartidas para no duplicar 2K en el GLB.

    No guarda el .blend: solo afecta a esta sesión headless de exportación.
    """
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
    print("FM_WAREHOUSE_IMAGES_RESIZED", len(resized))
    for item in resized:
        print("  IMG", item)
    return resized


def export_glb():
    if os.path.exists(GLB):
        os.remove(GLB)
    bpy.ops.export_scene.gltf(
        filepath=GLB, export_format="GLB", use_selection=True,
        export_yup=True, export_apply=True, export_animations=False,
        export_cameras=False, export_lights=False, export_extras=True,
        export_materials="EXPORT", export_image_format="AUTO",
        export_texcoords=True, export_normals=True,
    )
    if not os.path.exists(GLB):
        raise RuntimeError("GLB not written")


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
    meshes = select_art()
    mins = Vector((1e9, 1e9, 1e9))
    maxs = Vector((-1e9, -1e9, -1e9))
    for ob in meshes:
        mn, mx = world_aabb(ob)
        for i in range(3):
            mins[i] = min(mins[i], mn[i])
            maxs[i] = max(maxs[i], mx[i])
    inside = all(mins[i] >= BOUNDS_MIN[i] - 1e-3
                 and maxs[i] <= BOUNDS_MAX[i] + 1e-3 for i in range(3))
    resized = downscale_images(meshes, max_size=1024)
    export_glb()
    info = inspect_glb(GLB)
    info["source_objects"] = len(meshes)
    info["resized_images"] = len(resized)
    info["source_aabb_blender"] = {
        "min": [round(v, 3) for v in mins],
        "max": [round(v, 3) for v in maxs],
    }
    info["bounds_blender"] = {
        "min": [round(v, 3) for v in BOUNDS_MIN],
        "max": [round(v, 3) for v in BOUNDS_MAX],
    }
    info["aabb_inside_bounds"] = inside
    info["file"] = os.path.relpath(GLB, ROOT)
    info["max_bytes"] = MAX_BYTES
    info["pass"] = (
        inside
        and info["bytes"] <= MAX_BYTES
        and info["cameras"] == 0
        and info["lights"] == 0
        and info["meshes"] > 0
        and info["images"] > 0
        and any("WH_" in n for n in info["names_sample"])
    )
    with open(REPORT, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    print("FM_WAREHOUSE_EXPORT", json.dumps(info, ensure_ascii=False))
    if not info["pass"]:
        raise RuntimeError("Warehouse GLB validation failed")


if __name__ == "__main__":
    main()
