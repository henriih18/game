"""Exporta el conector Seguridad-corredor que faltaba en el V06.

Uso:
  blender -b nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend \
      --python scripts/fm/fm_security_connector_export_headless.py

El conector existe en el master como `SM_L1_Conn_SecurityConnector_*`:
suelo de 6 x 6 m entre el corredor principal (y=4) y Seguridad (y=10), y los
dos muros laterales de 4,2 m de alto. El corredor ya tiene el vano abierto en
`SM_L1_Corridor_Main_Wall_S_1` (solo existe de z=3,2 a 4,2), pero el suelo y
los muros del conector nunca se exportaron a ningun GLB del juego.

El techo del master esta roto (AABB en el origen por transform sin aplicar),
asi que se excluye; la escena Godot anade una losa simple a 4,2 m.

No guarda el .blend.
"""
import bpy
import json
import os
import struct
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
GLB = "assets/models/fm/security_connector.glb"
REPORT = os.path.join(ROOT, "docs/fm_security_connector_export.json")
MAX_BYTES = 2 * 1024 * 1024
EXPECTED = 3
PREFIX = "SM_L1_Conn_SecurityConnector_"
EXPECTED_NAMES = (
    "SM_L1_Conn_SecurityConnector_Floor",
    "SM_L1_Conn_SecurityConnector_Wall_E_0",
    "SM_L1_Conn_SecurityConnector_Wall_W_0",
)
BOUNDS_MIN = Vector((-92.2, 4.0, -0.25))
BOUNDS_MAX = Vector((-85.8, 10.0, 4.25))


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
        "names": [n.get("name", "") for n in nodes],
    }


def main():
    meshes = []
    for name in EXPECTED_NAMES:
        ob = bpy.data.objects.get(name)
        if ob is None or ob.type != "MESH":
            raise RuntimeError("missing connector mesh " + name)
        meshes.append(ob)
    if len(meshes) != EXPECTED:
        raise RuntimeError("expected %d connector meshes" % EXPECTED)

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
        and all(n.startswith(PREFIX) for n in info["names"])
    )
    with open(REPORT, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    print("FM_SECURITY_CONNECTOR_EXPORT", json.dumps(info, ensure_ascii=False))
    if not info["pass"]:
        raise RuntimeError("security connector GLB validation failed")


if __name__ == "__main__":
    main()
