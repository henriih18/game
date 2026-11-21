"""Exporta el Nivel 1 completo de NEXUS a GLB para la escena jugable de Godot.

No modifica el .blend: solo selecciona geometría visible del nivel, oculta las
hojas de puerta principales para dejar los vanos transitables y exporta.
"""
import json
import os

import bpy
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
OUT = os.path.join(ROOT, "assets/models/fm/level1_nexus.glb")
REPORT = os.path.join(ROOT, "nexus/nivel_01/level1_export_selection.json")

DOOR_LEAVES = {
    "NEXUS_V05_RECEPCION_DOOR_LEAF",
    "NEXUS_V05_RECEPCION_DOOR_GLASS",
    "NEXUS_V05_RECEPCION_DOOR_HANDLE",
    "NEXUS_V05_SEGURIDAD_DOOR_LEAF",
    "NEXUS_V05_SEGURIDAD_DOOR_GLASS",
    "NEXUS_V05_SEGURIDAD_DOOR_HANDLE",
    "NEXUS_V05_CONTROL_ACCESO_DOOR_LEAF",
    "NEXUS_V05_CONTROL_ACCESO_DOOR_GLASS",
    "NEXUS_V05_CONTROL_ACCESO_DOOR_HANDLE",
    "NEXUS_V05_VESTUARIOS_DOOR_LEAF",
    "NEXUS_V05_VESTUARIOS_DOOR_GLASS",
    "NEXUS_V05_VESTUARIOS_DOOR_HANDLE",
    "NEXUS_V05_ALMACEN_DOOR_LEAF",
    "NEXUS_V05_ALMACEN_DOOR_GLASS",
    "NEXUS_V05_ALMACEN_DOOR_HANDLE",
    "NEXUS_V05_MANTENIMIENTO_DOOR_LEAF",
    "NEXUS_V05_MANTENIMIENTO_DOOR_GLASS",
    "NEXUS_V05_MANTENIMIENTO_DOOR_HANDLE",
    "NEXUS_V05_OFFICE_DOOR_LEAF",
    "NEXUS_V05_OFFICE_DOOR_GLASS",
    "NEXUS_V05_OFFICE_DOOR_HANDLE",
    "NEXUS_V05_REST_DOOR_LEAF",
    "NEXUS_V05_REST_DOOR_HANDLE",
}

bpy.ops.object.select_all(action="DESELECT")
selected = []
skipped = []
triangles = 0

for obj in bpy.data.objects:
    if obj.type not in {"MESH", "FONT"}:
        continue
    if obj.hide_render or obj.hide_viewport:
        skipped.append(obj.name)
        continue
    if obj.name.startswith("TMP_") or "HIST" in obj.name:
        skipped.append(obj.name)
        continue
    if obj.name in DOOR_LEAVES:
        skipped.append(obj.name)
        continue
    center = obj.matrix_world @ Vector((0.0, 0.0, 0.0))
    if not (-7.0 <= center.z <= 1.0):
        skipped.append(obj.name)
        continue
    obj.select_set(True)
    selected.append(obj)
    if obj.type == "MESH":
        triangles += sum(max(1, len(p.vertices) - 2) for p in obj.data.polygons)

# Asegura que los padres de los objetos seleccionados también se exporten.
for obj in list(selected):
    parent = obj.parent
    while parent is not None:
        if parent.type == "EMPTY" and not parent.hide_render:
            parent.select_set(True)
        parent = parent.parent

print("LEVEL1_SELECTED", len(selected))
print("LEVEL1_TRIANGLES", triangles)
print("LEVEL1_SKIPPED", len(skipped))
print("LEVEL1_OUT", OUT)

bpy.ops.export_scene.gltf(
    filepath=OUT,
    export_format="GLB",
    use_selection=True,
    export_apply=True,
    export_yup=True,
    export_extras=True,
    export_animations=True,
    export_cameras=False,
    export_lights=False,
    export_image_format="WEBP",
    export_image_quality=70,
)

with open(REPORT, "w", encoding="utf-8") as handle:
    json.dump(
        {
            "file": OUT,
            "selected": len(selected),
            "triangles": triangles,
            "skipped": len(skipped),
            "door_leaves_excluded": sorted(DOOR_LEAVES),
        },
        handle,
        indent=2,
    )

print("LEVEL1_EXPORT_DONE", os.path.getsize(OUT))
