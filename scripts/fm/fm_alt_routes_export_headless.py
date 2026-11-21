"""Exporta la red de rutas alternativas del master V06 a un GLB unico.

Uso:
  blender -b nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend \
      --python scripts/fm/fm_alt_routes_export_headless.py

No guarda el .blend. La coleccion L1_ARCH_ALTERNATE contiene geometria de
rutas de servicio (galerias, tuneles y la escalera NW) que el V06 nunca
exporto. Se excluyen:

  - las mallas cuyo nombre ya existe en cualquier GLB de assets/models/fm
    (muros del corredor, del conector de escaleras, de Mantenimiento y la
    SecurityCorridor ya exportada dentro de security_access_sector.glb);
  - la anotacion ANNOT_L1_MaintCorridor.

El resultado son solo las piezas de ruta que faltan en el juego.
"""
import bpy
import glob
import json
import os
import struct
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
COLLECTION = "L1_ARCH_ALTERNATE"
GLB = "assets/models/fm/alternate_routes.glb"
REPORT = os.path.join(ROOT, "docs/fm_alternate_routes_export.json")
MAX_BYTES = 12 * 1024 * 1024
EXPECTED = 86
# AABB Blender de la red completa (Godot z = -y). La escalera NW baja a -4.8
# y la galeria norte llega a y=67.
BOUNDS_MIN = Vector((-96.5, -33.0, -5.0))
BOUNDS_MAX = Vector((106.0, 67.2, 6.2))


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


def existing_glb_names():
    names = set()
    output_path = os.path.join(ROOT, GLB)
    for path in glob.glob(os.path.join(ROOT, "assets/models/fm/*.glb")):
        # El propio GLB de salida no es una fuente de duplicados: si se lee,
        # sus 86 mallas se excluirian a si mismas en la siguiente exportacion.
        if os.path.abspath(path) == os.path.abspath(output_path):
            continue
        doc = read_glb_json(path)
        if doc is None:
            continue
        names.update(n.get("name", "") for n in doc.get("nodes", []))
    return names


def world_aabb(ob):
    corners = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    mn = Vector((min(p.x for p in corners), min(p.y for p in corners),
                 min(p.z for p in corners)))
    mx = Vector((max(p.x for p in corners), max(p.y for p in corners),
                 max(p.z for p in corners)))
    return mn, mx


def tune_materials():
    """Oscurece los materiales blockout solo en esta sesion headless.

    Las rutas se construyeron con los materiales del shell (gris claro). Al
    exportarlas como sector propio conviene que lean como pasillos tecnicos
    humedos, no como geometria de blockout. No se guarda el .blend.
    """
    palette = {
        "M_L1_Corridor_Floor": ((0.035, 0.042, 0.040), 0.62, 0.0),
        "M_L1_Wall_Blockout": ((0.075, 0.105, 0.095), 0.82, 0.0),
        "M_L1_Wall_Corridor": ((0.065, 0.090, 0.085), 0.82, 0.0),
        "M_L1_Stair_Concrete": ((0.080, 0.082, 0.078), 0.88, 0.0),
        "M_L1_Zone_MainStairs": ((0.060, 0.062, 0.060), 0.84, 0.0),
        "M_L1_Door_Frame": ((0.040, 0.048, 0.047), 0.42, 0.5),
    }
    for name, (color, rough, metal) in palette.items():
        material = bpy.data.materials.get(name)
        if material is None or material.node_tree is None:
            continue
        principled = next(
            (n for n in material.node_tree.nodes if n.type == "BSDF_PRINCIPLED"),
            None,
        )
        if principled is None:
            continue
        principled.inputs["Base Color"].default_value = (*color, 1.0)
        principled.inputs["Roughness"].default_value = rough
        principled.inputs["Metallic"].default_value = metal


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
        "names_sample": [n.get("name", "") for n in nodes][:16],
    }


def main():
    col = bpy.data.collections.get(COLLECTION)
    if col is None:
        raise RuntimeError("missing collection " + COLLECTION)
    duplicates = existing_glb_names()
    meshes = []
    excluded = []
    for ob in col.all_objects:
        if ob.type != "MESH":
            continue
        if ob.name == "ANNOT_L1_MaintCorridor" or ob.name in duplicates:
            excluded.append(ob.name)
            continue
        meshes.append(ob)
    if len(meshes) != EXPECTED:
        raise RuntimeError("expected %d route meshes, found %d (excluded %d)" % (
            EXPECTED, len(meshes), len(excluded)))

    bpy.ops.object.select_all(action="DESELECT")
    for ob in meshes:
        ob.hide_set(False)
        ob.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.context.view_layer.update()

    mins = Vector((1e9, 1e9, 1e9))
    maxs = Vector((-1e9, -1e9, -1e9))
    tris = 0
    routes = {}
    for ob in meshes:
        mn, mx = world_aabb(ob)
        for i in range(3):
            mins[i] = min(mins[i], mn[i])
            maxs[i] = max(maxs[i], mx[i])
        ob.data.calc_loop_triangles()
        tris += len(ob.data.loop_triangles)
        parts = ob.name.split("_")
        route = parts[3] if len(parts) > 3 else "other"
        routes[route] = routes.get(route, 0) + 1

    inside = all(
        mins[i] >= BOUNDS_MIN[i] - 1e-3 and maxs[i] <= BOUNDS_MAX[i] + 1e-3
        for i in range(3)
    )
    tune_materials()

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
        "excluded_objects": len(excluded),
        "excluded_sample": sorted(excluded)[:12],
        "routes": dict(sorted(routes.items())),
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
        and all(n.startswith("SM_L1_Alt_") for n in info["names_sample"])
    )
    with open(REPORT, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    print("FM_ALT_ROUTES_EXPORT", json.dumps(info, ensure_ascii=False))
    if not info["pass"]:
        raise RuntimeError("alternate routes GLB validation failed")


if __name__ == "__main__":
    main()
