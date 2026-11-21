"""Verificación de solo lectura del máster NEXUS contra v125."""

import json
import os

import bpy

ROOT = "/home/riyo/Documentos/game"
SOURCE = ROOT + "/FM_NEXUS_V05_level1_v125.blend"
MASTER = ROOT + "/nexus/master/NEXUS_MASTER.blend"
REPORT = ROOT + "/nexus/verification.json"


def snapshot(path):
    bpy.ops.wm.open_mainfile(filepath=path)
    scene = bpy.context.scene
    bpy.context.view_layer.update()
    objects = {}
    triangles = 0
    for ob in scene.objects:
        objects[ob.name] = {
            "type": ob.type,
            "matrix": tuple(value for row in ob.matrix_world for value in row),
            "hide_render": ob.hide_render,
            "hide_viewport": ob.hide_viewport,
        }
        if ob.type == "MESH":
            triangles += sum(len(poly.vertices) - 2 for poly in ob.data.polygons)
    libraries = [lib.filepath for lib in bpy.data.libraries]
    missing_libraries = [
        path for path in libraries
        if not os.path.isfile(bpy.path.abspath(path))
    ]
    return {
        "objects": objects,
        "triangles": triangles,
        "camera": scene.camera.name if scene.camera else None,
        "libraries": libraries,
        "missing_libraries": missing_libraries,
    }


def main():
    source = snapshot(SOURCE)
    master = snapshot(MASTER)
    source_names = set(source["objects"])
    master_names = set(master["objects"])
    transform_mismatches = []
    visibility_mismatches = []
    type_mismatches = []
    for name in sorted(source_names & master_names):
        a = source["objects"][name]
        b = master["objects"][name]
        if a["type"] != b["type"]:
            type_mismatches.append(name)
        if max(abs(x - y) for x, y in zip(a["matrix"], b["matrix"])) > 0.00001:
            transform_mismatches.append(name)
        if (a["hide_render"], a["hide_viewport"]) != (b["hide_render"], b["hide_viewport"]):
            visibility_mismatches.append(name)

    report = {
        "source_objects": len(source_names),
        "master_objects": len(master_names),
        "missing_objects": sorted(source_names - master_names),
        "extra_objects": sorted(master_names - source_names),
        "type_mismatches": type_mismatches,
        "transform_mismatches": transform_mismatches,
        "visibility_mismatches": visibility_mismatches,
        "source_triangles": source["triangles"],
        "master_triangles": master["triangles"],
        "source_camera": source["camera"],
        "master_camera": master["camera"],
        "master_libraries": master["libraries"],
        "missing_libraries": master["missing_libraries"],
    }
    failures = [
        key for key in [
            "missing_objects", "extra_objects", "type_mismatches",
            "transform_mismatches", "visibility_mismatches", "missing_libraries",
        ] if report[key]
    ]
    if source["triangles"] != master["triangles"]:
        failures.append("triangle_count")
    if source["camera"] != master["camera"]:
        failures.append("active_camera")
    report["failures"] = failures
    with open(REPORT, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
    if failures:
        raise RuntimeError("Fallos de verificación: " + ", ".join(failures))


if __name__ == "__main__":
    main()
