"""Exporta la linterna local small_plastic_torch_2k a un GLB para el viewmodel de Godot."""

import os

import bpy

ROOT = "/home/riyo/Documentos/game"
SRC = os.path.join(
    ROOT,
    "assets/Modelos 3D/Objetos pequeños y narrativa ambiental",
    "small_plastic_torch_2k.blend",
    "small_plastic_torch_2k.blend",
)
OUT = os.path.join(ROOT, "assets/models/fm/flashlight_nexus.glb")


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=SRC)
    collection = next(
        (c for c in bpy.data.collections if "small_plastic_torch" in c.name.lower()),
        None,
    )
    if collection is not None:
        objects = list(collection.all_objects)
    else:
        objects = [o for o in bpy.data.objects if o.type == "MESH"]
    if not objects:
        raise RuntimeError("No se encontraron objetos para exportar")

    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.hide_set(False)
        obj.hide_viewport = False
        obj.hide_render = False
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]

    bpy.ops.export_scene.gltf(
        filepath=OUT,
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
        export_texcoords=True,
        export_normals=True,
        export_tangents=False,
        export_materials="EXPORT",
        export_image_format="WEBP",
        export_image_quality=70,
        export_cameras=False,
        export_lights=False,
        export_animations=False,
        export_extras=True,
    )
    print("FLASHLIGHT_GLB", OUT)
    print("FLASHLIGHT_BYTES", os.path.getsize(OUT))
    print("FLASHLIGHT_OBJECTS", len(objects))


if __name__ == "__main__":
    main()
