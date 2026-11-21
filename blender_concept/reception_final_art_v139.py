"""Pase final de iluminación de recepción para la versión jugable.

Base: nexus/nivel_01/NEXUS_L1_V05.blend (v138).
Salida: el mismo archivo vivo, sin crear checkpoint nuevo.
"""
import bpy

ROOT = "/home/riyo/Documentos/game"
OUT = ROOT + "/nexus/nivel_01/NEXUS_L1_V05.blend"

LIGHT_COLL = bpy.data.collections.get("V05_LIGHTS") or bpy.context.scene.collection
POSITIONS = [
    (-17.0, 3.6, -0.55),
    (-7.0, 3.6, -0.55),
    (-17.0, 9.8, -0.55),
    (-7.0, 9.8, -0.55),
]


def ensure_light(index, loc):
    name = f"NEXUS_V05_REC_FINAL_LIGHT_{index}"
    data = bpy.data.lights.get(name)
    if data is None:
        data = bpy.data.lights.new(name, "POINT")
    obj = bpy.data.objects.get(name)
    if obj is None:
        obj = bpy.data.objects.new(name, data)
        LIGHT_COLL.objects.link(obj)
    else:
        obj.data = data
    obj.location = loc
    data.type = "POINT"
    data.energy = 180.0
    data.color = (1.0, 0.83, 0.68)
    data.shadow_soft_size = 0.28
    data.use_shadow = index in (0, 2)
    return obj


def main():
    for index, loc in enumerate(POSITIONS):
        ensure_light(index, loc)

    bpy.context.view_layer.update()
    cam = bpy.data.objects.get("NEXUS_V05_CAM_Recepcion")
    if cam:
        bpy.context.scene.camera = cam
    bpy.context.scene.frame_set(1)

    visible = [o for o in bpy.context.scene.objects if o.type == "LIGHT" and not o.hide_render]
    shadowed = [o for o in visible if o.data.use_shadow]
    print("OBJECTS", len(bpy.context.scene.objects))
    print("VISIBLE_LIGHTS", len(visible))
    print("SHADOWED_LIGHTS", len(shadowed))
    print("CAM", bpy.context.scene.camera.name if bpy.context.scene.camera else None)

    bpy.ops.wm.save_as_mainfile(filepath=OUT)
    print("SAVED", OUT)


if __name__ == "__main__":
    main()
