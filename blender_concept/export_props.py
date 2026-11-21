import bpy
import os
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
OUT = ROOT + "/assets/models/fm/props"
os.makedirs(OUT, exist_ok=True)

ASSETS = {
    "potted_plant": "assets/Modelos 3D/Vegetación, musgo y plantas/potted_plant_02_2k.blend/potted_plant_02_2k.blend",
    "utility_box": "assets/Modelos 3D/Infraestructura industrial y mantenimiento/utility_box_02_2k.blend/utility_box_02_2k.blend",
    "shelves": "assets/Modelos 3D/Mobiliario y almacenamiento/steel_frame_shelves_01_2k.blend/steel_frame_shelves_01_2k.blend",
    "drawer": "assets/Modelos 3D/Mobiliario y almacenamiento/vintage_wooden_drawer_01_4k.blend/vintage_wooden_drawer_01_4k.blend",
    "power_box": "assets/Modelos 3D/Infraestructura industrial y mantenimiento/power_box_01_2k.blend/power_box_01_2k.blend",
    "camera": "assets/Modelos 3D/Infraestructura industrial y mantenimiento/security_camera_01_2k.blend/security_camera_01_2k.blend",
    "fire_alarm": "assets/Modelos 3D/Infraestructura industrial y mantenimiento/fire_alarm_2k.blend/fire_alarm_2k.blend",
    "medical_box": "assets/Modelos 3D/Laboratorios y equipamiento científico/medical_box_2k.blend/medical_box_2k.blend",
    "stool": "assets/Modelos 3D/Mobiliario y almacenamiento/metal_stool_01_1k.blend/metal_stool_01_1k.blend",
    "chemistry": "assets/Modelos 3D/Laboratorios y equipamiento científico/chemistry_set_4k.blend/chemistry_set_4k.blend",
    "microscope": "assets/Modelos 3D/Laboratorios y equipamiento científico/industrial_microscope_4k.blend/industrial_microscope_4k.blend",
    "clock": "assets/Modelos 3D/Objetos pequeños y narrativa ambiental/wall_clock_1k.blend/wall_clock_1k.blend",
    "crate": "assets/Modelos 3D/Mobiliario y almacenamiento/plastic_crate_01_1k.blend/plastic_crate_01_1k.blend",
    "barrel": "assets/Modelos 3D/Objetos pequeños y narrativa ambiental/barrel_03_2k.blend/barrel_03_2k.blend",
    "radio": "assets/Modelos 3D/Objetos pequeños y narrativa ambiental/vintage_radio_transceiver_4k.blend/vintage_radio_transceiver_4k.blend",
}

for key, rel in ASSETS.items():
    path = ROOT + "/" + rel
    if not os.path.exists(path):
        print("MISSING", key, path)
        continue
    bpy.ops.wm.open_mainfile(filepath=path)
    # Reducir texturas de props para no saturar VRAM en el perfil bajo.
    for img in bpy.data.images:
        try:
            w, h = img.size
            if w > 1024 or h > 1024:
                sc = 1024.0 / max(w, h)
                img.scale(max(1, int(w * sc)), max(1, int(h * sc)))
        except Exception:
            pass
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    meshes = [o for o in bpy.context.view_layer.objects if o.type == 'MESH' and not o.hide_render]
    for o in meshes:
        o.select_set(True)
    if not meshes:
        print("NO_MESH", key)
        continue
    bpy.context.view_layer.objects.active = meshes[0]
    mn = Vector((1e9, 1e9, 1e9))
    mx = Vector((-1e9, -1e9, -1e9))
    for o in meshes:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            for i in range(3):
                mn[i] = min(mn[i], w[i]); mx[i] = max(mx[i], w[i])
    out = OUT + "/" + key + ".glb"
    bpy.ops.export_scene.gltf(
        filepath=out, export_format='GLB', use_selection=True,
        export_apply=True, export_yup=True, export_image_format='WEBP',
        export_image_quality=85, export_cameras=False, export_lights=False,
        export_animations=False,
    )
    print("PROP", key, "objs", len(meshes), "dims", tuple(round(mx[i]-mn[i], 3) for i in range(3)), "min", tuple(round(v,2) for v in mn), "size", os.path.getsize(out))
