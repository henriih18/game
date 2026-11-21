"""Divide NEXUS v125 en archivos por nivel sin modificar el archivo fuente.

Ejecutar:
  /opt/blender/blender --background --factory-startup \
    --python-exit-code 1 --python blender_concept/split_nexus_levels.py

La salida se crea dentro de nexus/. El master enlaza los niveles; Nivel 1
enlaza los assets comunes. Los originales nunca se sobrescriben.
"""

import json
import os

import bpy
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
SOURCE = ROOT + "/FM_NEXUS_V05_level1_v125.blend"
OUT = ROOT + "/nexus"

PATHS = {
    "L1": OUT + "/nivel_01/NEXUS_L1_V05.blend",
    "L2": OUT + "/nivel_02/NEXUS_L2_V04.blend",
    "L3": OUT + "/nivel_03/NEXUS_L3_MEDICAL.blend",
    "L4": OUT + "/nivel_04/NEXUS_L4_CONTAINMENT.blend",
    "L5": OUT + "/nivel_05/NEXUS_L5_INFRA.blend",
    "CORE": OUT + "/nucleo/NEXUS_CORE.blend",
    "SHARED": OUT + "/compartido/NEXUS_SHARED_ASSETS.blend",
    "HIST": OUT + "/compartido/NEXUS_HISTORICAL.blend",
    "MASTER": OUT + "/master/NEXUS_MASTER.blend",
}

ROOT_NAMES = {
    "L1": "NEXUS_L1_V05",
    "L2": "NEXUS_L2_V04",
    "L3": "NEXUS_L3_MEDICAL",
    "L4": "NEXUS_L4_CONTAINMENT",
    "L5": "NEXUS_L5_INFRA",
    "CORE": "NEXUS_CORE",
    "SHARED": "NEXUS_SHARED_ASSETS",
    "HIST": "NEXUS_HISTORICAL",
}

WHOLE = {
    "L1": [
        "NEXUS_V05_LEVEL1",
        "NEXUS_V05_SERVICE_CONN",
        "NEXUS_V05_SERVICE_CONN_HIST",
        "NEXUS_L1_DISASTER",
    ],
    "L2": ["NEXUS_V04_LAB_SCALE", "NEXUS_STORY_L2A", "NEXUS_STORY_L2B"],
    "L3": ["NEXUS_LRING_L3"],
    "L4": ["NEXUS_LRING_L4"],
    "L5": ["NEXUS_LRING_L5", "NEXUS_L5_POLISH"],
    "CORE": ["NEXUS_VTOWER"],
    "SHARED": ["NEXUS_ASSET_V05", "NEXUS_ASSET_L1", "NEXUS_ASSET_L1_REPLACE"],
    "HIST": ["NEXUS_V03_LAB_LEVEL"],
}

MIXED = [
    "FM_NEXUS_V01",
    "02_CIRCULATION",
    "NEXUS_LDOORS",
    "NEXUS_CENTRAL",
    "NEXUS_LROOM_PROPS",
    "NEXUS_STORY_LOWER",
]

BANDS = [
    ("L1", -8.0, 0.0),
    ("L2", -18.0, -8.0),
    ("L3", -28.0, -18.0),
    ("L4", -38.0, -28.0),
    ("L5", -55.0, -38.0),
]

CAMERAS = {
    "L1": "NEXUS_V05_CAM_Corridor",
    "L2": "NEXUS_V04_CAM_Airlock",
    "MASTER": "NEXUS_V05_CAM_Corridor",
}

EXPECTED = {
    "L1": 2154,
    "L2": 1861,
    "L3": 620,
    "L4": 621,
    "L5": 817,
    "CORE": 500,
    "SHARED": 224,
    "HIST": 1255,
}


def object_z(ob):
    if ob.type == "MESH" and ob.bound_box:
        return sum((ob.matrix_world @ Vector(v)).z for v in ob.bound_box) / 8.0
    return ob.matrix_world.translation.z


def object_band(ob):
    z = object_z(ob)
    for key, low, high in BANDS:
        if low <= z < high:
            return key
    return "HIST"


def classify(scene):
    assigned = {key: set() for key in EXPECTED}
    sources = {key: {} for key in EXPECTED}

    def add(key, ob, source):
        assigned[key].add(ob.name)
        sources[key].setdefault(source, set()).add(ob.name)

    for key, collection_names in WHOLE.items():
        for collection_name in collection_names:
            collection = bpy.data.collections[collection_name]
            for ob in collection.all_objects:
                add(key, ob, collection_name)

    # Los assets compartidos se editan en compartido y se enlazan a L1.
    for ob in bpy.data.collections["NEXUS_ASSET_V05"].all_objects:
        add("L1", ob, "NEXUS_ASSET_V05")
    for ob in bpy.data.collections["NEXUS_ASSET_L1"].all_objects:
        add("L1", ob, "NEXUS_ASSET_L1")
    for ob in bpy.data.collections["NEXUS_ASSET_L1_REPLACE"].all_objects:
        add("L1", ob, "NEXUS_ASSET_L1_REPLACE")

    for collection_name in MIXED:
        collection = bpy.data.collections[collection_name]
        for ob in collection.all_objects:
            key = "HIST" if ob.hide_render else object_band(ob)
            add(key, ob, collection_name)

    # Objetos sueltos de la raíz, incluida la cámara del Airlock.
    for ob in scene.collection.objects:
        key = "HIST" if ob.hide_render else object_band(ob)
        add(key, ob, "SCENE_ROOT")

    # Cualquier objeto no contemplado explícitamente se conserva por cotas.
    covered = set().union(*assigned.values())
    for ob in scene.objects:
        if ob.name not in covered:
            key = "HIST" if ob.hide_render else object_band(ob)
            add(key, ob, "UNASSIGNED")

    counts = {key: len(names) for key, names in assigned.items()}
    if counts != EXPECTED:
        raise RuntimeError(f"Recuentos inesperados: {counts}; esperados: {EXPECTED}")
    union = set().union(*assigned.values())
    if len(union) != len(scene.objects):
        raise RuntimeError("La clasificación contiene duplicados entre niveles")
    if union != {ob.name for ob in scene.objects}:
        raise RuntimeError("La clasificación no cubre exactamente la escena")
    return assigned, sources


def prepare_scene(root_name):
    scene = bpy.context.scene
    scene.name = root_name
    original_roots = [collection.name for collection in scene.collection.children]
    target = bpy.data.collections.new(root_name)
    scene.collection.children.link(target)
    return scene, target, original_roots


def add_selected(target, source_name, object_names):
    if not object_names:
        return
    safe_name = source_name.replace("NEXUS_", "").replace("02_", "")
    collection = bpy.data.collections.new(target.name + "_FROM_" + safe_name)
    target.children.link(collection)
    for name in sorted(object_names):
        collection.objects.link(bpy.data.objects[name])


def finish_file(scene, target, original_roots, output, camera_name=None):
    for collection_name in original_roots:
        collection = bpy.data.collections.get(collection_name)
        if collection is not None and collection.name in scene.collection.children:
            scene.collection.children.unlink(collection)
    for ob in list(scene.collection.objects):
        scene.collection.objects.unlink(ob)

    bpy.context.view_layer.update()
    actual = {ob.name for ob in scene.objects}
    expected = set(target["expected_objects"])
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise RuntimeError(
            f"Error en {target.name}: faltan={missing[:20]} sobran={extra[:20]}"
        )

    scene.camera = bpy.data.objects.get(camera_name) if camera_name else None
    if scene.camera is None:
        scene.camera = next((ob for ob in scene.objects if ob.type == "CAMERA"), None)
    # Las colecciones originales ya no están en escena; purgar sus datos evita
    # guardar una copia oculta del complejo completo dentro de cada nivel.
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version = 0
    os.makedirs(os.path.dirname(output), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=output, compress=True)
    bpy.ops.file.make_paths_relative()
    bpy.ops.wm.save_as_mainfile(filepath=output, compress=True)
    print("SAVED", output, len(scene.objects), os.path.getsize(output), flush=True)


def build_local_file(key):
    bpy.ops.wm.open_mainfile(filepath=SOURCE)
    assigned, sources = classify(bpy.context.scene)
    scene, target, original_roots = prepare_scene(ROOT_NAMES[key])
    target["expected_objects"] = sorted(assigned[key])

    whole_for_key = list(WHOLE.get(key, []))
    if key == "L1":
        whole_for_key.extend(WHOLE["SHARED"])
    for collection_name in whole_for_key:
        target.children.link(bpy.data.collections[collection_name])
    for source_name, names in sources[key].items():
        if source_name not in whole_for_key:
            add_selected(target, source_name, names)

    if key == "L1":
        # Sustituir las copias locales por una única biblioteca enlazada.
        for collection_name in WHOLE["SHARED"]:
            collection = bpy.data.collections[collection_name]
            target.children.unlink(collection)
            for ob in list(collection.all_objects):
                bpy.data.objects.remove(ob, do_unlink=True)
            bpy.data.collections.remove(collection)
        with bpy.data.libraries.load(PATHS["SHARED"], link=True) as (src, dst):
            dst.collections = [ROOT_NAMES["SHARED"]]
        target.children.link(dst.collections[0])

    finish_file(scene, target, original_roots, PATHS[key], CAMERAS.get(key))


def build_master():
    bpy.ops.wm.open_mainfile(filepath=SOURCE)
    expected_names = {ob.name for ob in bpy.context.scene.objects}
    scene = bpy.context.scene
    scene.name = "NEXUS_MASTER"

    for collection in list(scene.collection.children):
        scene.collection.children.unlink(collection)
    for ob in list(scene.collection.objects):
        scene.collection.objects.unlink(ob)
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)

    target = bpy.data.collections.new("NEXUS_MASTER")
    scene.collection.children.link(target)
    for key in ["L1", "L2", "L3", "L4", "L5", "CORE", "HIST"]:
        with bpy.data.libraries.load(PATHS[key], link=True) as (src, dst):
            dst.collections = [ROOT_NAMES[key]]
        target.children.link(dst.collections[0])

    bpy.context.view_layer.update()
    actual = {ob.name for ob in scene.objects}
    if actual != expected_names:
        raise RuntimeError(
            f"Master incompleto: faltan={sorted(expected_names - actual)[:20]} "
            f"sobran={sorted(actual - expected_names)[:20]}"
        )
    scene.camera = bpy.data.objects.get(CAMERAS["MASTER"])
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.preferences.filepaths.save_version = 0
    os.makedirs(os.path.dirname(PATHS["MASTER"]), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=PATHS["MASTER"], compress=True)
    bpy.ops.file.make_paths_relative()
    bpy.ops.wm.save_as_mainfile(filepath=PATHS["MASTER"], compress=True)
    print("SAVED", PATHS["MASTER"], len(scene.objects), os.path.getsize(PATHS["MASTER"]), flush=True)


def inspect_file(path):
    bpy.ops.wm.open_mainfile(filepath=path)
    scene = bpy.context.scene
    missing = []
    for image in bpy.data.images:
        if image.source == "FILE" and not image.packed_file:
            resolved = bpy.path.abspath(image.filepath, library=image.library)
            if not os.path.isfile(resolved):
                missing.append(image.filepath)
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
        "libraries": [lib.filepath for lib in bpy.data.libraries],
        "missing_images": sorted(missing),
    }


def main():
    if not os.path.isfile(SOURCE):
        raise FileNotFoundError(SOURCE)
    os.makedirs(OUT, exist_ok=True)

    # SHARED debe existir antes que L1; el resto antes que MASTER.
    for key in ["SHARED", "L1", "L2", "L3", "L4", "L5", "CORE", "HIST"]:
        build_local_file(key)
    build_master()

    reports = {key: inspect_file(path) for key, path in PATHS.items()}
    bpy.ops.wm.open_mainfile(filepath=SOURCE)
    source_count = len(bpy.context.scene.objects)
    if reports["MASTER"]["scene_objects"] != source_count:
        raise RuntimeError("El master no conserva el número de objetos de la fuente")
    new_missing = {
        key: report["missing_images"] for key, report in reports.items()
        if report["missing_images"]
    }
    if new_missing:
        raise RuntimeError(f"Imágenes ausentes tras la división: {new_missing}")

    manifest = {
        "source": SOURCE,
        "source_scene_objects": source_count,
        "method": "Niveles locales editables; assets comunes enlazados a L1; master enlazado",
        "files": reports,
    }
    manifest_path = OUT + "/manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)
    print("VERIFIED", manifest_path, flush=True)


if __name__ == "__main__":
    main()
