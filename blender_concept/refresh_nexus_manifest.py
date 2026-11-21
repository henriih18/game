"""Refresh nexus/manifest.json from the current modular files.

Read-only: opens every file, records counts, libraries and missing image paths,
then writes the manifest. No .blend is saved.
"""

import json
import os

import bpy

ROOT = "/home/riyo/Documentos/game"
OUT = os.path.join(ROOT, "nexus")
PATHS = {
    "L1": os.path.join(OUT, "nivel_01/NEXUS_L1_V05.blend"),
    "L2": os.path.join(OUT, "nivel_02/NEXUS_L2_V04.blend"),
    "L3": os.path.join(OUT, "nivel_03/NEXUS_L3_MEDICAL.blend"),
    "L4": os.path.join(OUT, "nivel_04/NEXUS_L4_CONTAINMENT.blend"),
    "L5": os.path.join(OUT, "nivel_05/NEXUS_L5_INFRA.blend"),
    "CORE": os.path.join(OUT, "nucleo/NEXUS_CORE.blend"),
    "SHARED": os.path.join(OUT, "compartido/NEXUS_SHARED_ASSETS.blend"),
    "HIST": os.path.join(OUT, "compartido/NEXUS_HISTORICAL.blend"),
    "MASTER": os.path.join(OUT, "master/NEXUS_MASTER.blend"),
}


def inspect_file(path):
    bpy.ops.wm.open_mainfile(filepath=path)
    scene = bpy.context.scene
    missing = []
    invalid = []
    for image in bpy.data.images:
        if image.source != "FILE" or image.packed_file:
            continue
        resolved = bpy.path.abspath(image.filepath, library=image.library)
        if not os.path.isfile(resolved):
            missing.append(image.filepath)
        elif os.path.getsize(resolved) < 256 and resolved.lower().endswith((".png", ".jpg", ".jpeg")):
            invalid.append(image.filepath)
    return {
        "path": path,
        "bytes": os.path.getsize(path),
        "scene_objects": len(scene.objects),
        "datablock_objects": len(bpy.data.objects),
        "datablock_meshes": len(bpy.data.meshes),
        "datablock_materials": len(bpy.data.materials),
        "mesh_objects": sum(ob.type == "MESH" for ob in scene.objects),
        "lights": sum(ob.type == "LIGHT" for ob in scene.objects),
        "cameras": sum(ob.type == "CAMERA" for ob in scene.objects),
        "active_camera": scene.camera.name if scene.camera else None,
        "libraries": [lib.filepath for lib in bpy.data.libraries if not lib.is_missing],
        "missing_libraries": [lib.filepath for lib in bpy.data.libraries if lib.is_missing],
        "missing_images": sorted(set(missing)),
        "suspicious_small_images": sorted(set(invalid)),
    }


reports = {key: inspect_file(path) for key, path in PATHS.items()}
manifest = {
    "source": os.path.join(ROOT, "FM_NEXUS_V05_level1_v125.blend"),
    "source_scene_objects": 7828,
    "method": "Niveles locales editables; assets comunes enlazados a L1; master enlazado",
    "note": (
        "El master se refresca al abrir: L1 evoluciono despues de la division. "
        "L1 v130 incluye pase de recepcion v126-v127, linterna y extraccion v129, "
        "y las colecciones REC_PASS126/REC_LOD1/REC_PLAY anidadas en NEXUS_L1_V05."
    ),
    "files": reports,
    "post_split_l1_versions": [
        "NEXUS_L1_V05_recepcion_v127.blend",
        "NEXUS_L1_V05_recepcion_v128.blend",
        "NEXUS_L1_V05_recepcion_v129.blend",
        "NEXUS_L1_V05_recepcion_v130.blend",
    ],
}
path = os.path.join(OUT, "manifest.json")
with open(path, "w", encoding="utf-8") as handle:
    json.dump(manifest, handle, ensure_ascii=False, indent=2)
print("WROTE", path)
print("L1", reports["L1"]["scene_objects"], reports["L1"]["bytes"])
print("MASTER", reports["MASTER"]["scene_objects"], reports["MASTER"]["bytes"])
print("MISSING_IMAGES", {k: v["missing_images"] for k, v in reports.items() if v["missing_images"]})
print("SUSPICIOUS", {k: v["suspicious_small_images"] for k, v in reports.items() if v["suspicious_small_images"]})
