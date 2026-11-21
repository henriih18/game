"""Exporta el arte de la sala tecnica NWStair del master V06.

Uso:
  blender -b nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend \
      --python scripts/fm/fm_alt_routes_art_export_headless.py

No guarda el .blend. Exporta la coleccion L1_ART_ALT_ROUTES completa:
arquitectura, bombas, cuadros electricos, banco, servicios y senalizacion
funcional. El GLB no incluye camaras ni luces.
"""
import bpy
import json
import os
import struct
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
COLLECTION = "L1_ART_NWSTAIR_SERVICE"
GLB = "assets/models/fm/nwstair_service_art.glb"
REPORT = os.path.join(ROOT, "docs/fm_nwstair_service_art_export.json")
MAX_BYTES = 12 * 1024 * 1024
EXPECTED = 17
BOUNDS_MIN = Vector((-76.3, 59.5, -4.8))
BOUNDS_MAX = Vector((-67.7, 70.8, -1.6))


def read_glb_json(path):
    with open(path, "rb") as f:
        data = f.read()
    magic, version, length = struct.unpack_from("<III", data, 0)
    if magic != 0x46546C67:
        return None
    offset = 12
    while offset < length:
        chunk_len, chunk_type = struct.unpack_from("<II", data, offset)
        offset += 8
        chunk = data[offset:offset + chunk_len]
        offset += chunk_len
        if chunk_type == 0x4E4F534A:
            return json.loads(chunk.decode("utf-8"))
    return None


def world_aabb(ob):
    corners = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    mn = Vector((min(p.x for p in corners), min(p.y for p in corners),
                 min(p.z for p in corners)))
    mx = Vector((max(p.x for p in corners), max(p.y for p in corners),
                 max(p.z for p in corners)))
    return mn, mx


def inspect_glb(path):
    doc = read_glb_json(path)
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
        "bytes": os.path.getsize(path),
        "meshes": len(meshes),
        "nodes": len(nodes),
        "materials": len(doc.get("materials", [])),
        "images": len(doc.get("images", [])),
        "tris": tris,
        "cameras": len(doc.get("cameras", [])),
        "lights": lights,
        "names_sample": [n.get("name", "") for n in nodes][:24],
    }


def main():
    col = bpy.data.collections.get(COLLECTION)
    if col is None:
        raise RuntimeError("missing collection " + COLLECTION)
    meshes = [ob for ob in col.all_objects if ob.type == "MESH"]
    if len(meshes) != EXPECTED:
        raise RuntimeError("expected %d art meshes, found %d" % (EXPECTED, len(meshes)))

    bpy.ops.object.select_all(action="DESELECT")
    for ob in meshes:
        ob.hide_set(False)
        ob.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.context.view_layer.update()

    mins = Vector((1e9, 1e9, 1e9))
    maxs = Vector((-1e9, -1e9, -1e9))
    tris = 0
    for ob in meshes:
        mn, mx = world_aabb(ob)
        for i in range(3):
            mins[i] = min(mins[i], mn[i])
            maxs[i] = max(maxs[i], mx[i])
        ob.data.calc_loop_triangles()
        tris += len(ob.data.loop_triangles)

    inside = all(
        mins[i] >= BOUNDS_MIN[i] - 1e-3 and maxs[i] <= BOUNDS_MAX[i] + 1e-3
        for i in range(3)
    )

    path = os.path.join(ROOT, GLB)
    if os.path.exists(path):
        os.remove(path)
    bpy.ops.export_scene.gltf(
        filepath=path, export_format="GLB", use_selection=True,
        export_yup=True, export_apply=True, export_animations=False,
        export_cameras=False, export_lights=False, export_extras=True,
        export_materials="EXPORT", export_image_format="AUTO",
        export_texcoords=True, export_normals=True,
    )
    info = inspect_glb(path)
    info.update({
        "file": GLB,
        "source_objects": len(meshes),
        "source_tris": tris,
        "source_aabb_blender": {
            "min": [round(v, 3) for v in mins],
            "max": [round(v, 3) for v in maxs],
        },
        "bounds_blender": {
            "min": [round(v, 3) for v in BOUNDS_MIN],
            "max": [round(v, 3) for v in BOUNDS_MAX],
        },
        "aabb_inside_bounds": inside,
    })
    info["pass"] = (
        inside
        and info["bytes"] <= MAX_BYTES
        and info["cameras"] == 0
        and info["lights"] == 0
        and info["meshes"] == EXPECTED
        and all(n.startswith("NWS_") for n in info["names_sample"])
    )
    with open(REPORT, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    print("FM_NWSTAIR_SERVICE_EXPORT", json.dumps(info, ensure_ascii=False))
    if not info["pass"]:
        raise RuntimeError("nwstair service art GLB validation failed")


if __name__ == "__main__":
    main()
