"""Pase manual de escultura para El Coleccionista.

Se ejecuta headless sobre nexus/nivel_01/FM_COLLECTOR_SCULPT.blend:
- inclina el torso hacia delante (joroba),
- estrecha la cintura y ensancha los hombros,
- añade arrugas radiales/verticales a la ropa,
- crea el ribete de la capucha y el filtro de la máscara antes de deformar,
- guarda el .blend y renderiza una vista de revisión.

No toca la referencia ni el máster del nivel. Es idempotente por la propiedad
de escena `collector_manual_pass_v1`.
"""

import math
import os

import bpy
from mathutils import Vector

SCENE_KEY = "collector_manual_pass_v1"
RENDER_PATH = "/tmp/opencode/collector_manual.png"


def smoothstep(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3.0 - 2.0 * t)


def bend_world(co):
    x, y, z = co.x, co.y, co.z
    t = smoothstep(0.98, 2.30, z)
    y -= 0.20 * t * t
    if z > 2.0:
        y -= 0.055 * min(1.0, (z - 2.0) / 0.30)
    waist = math.exp(-((z - 1.18) / 0.20) ** 2)
    x *= 1.0 - 0.105 * waist
    shoulders = math.exp(-((z - 1.70) / 0.18) ** 2)
    x *= 1.0 + 0.075 * shoulders
    x += 0.012 * math.sin(z * 2.2) * (1.0 if x >= 0 else -1.0)
    return Vector((x, y, z))


def wrinkle(co, center_y=0.0):
    x, y, z = co.x, co.y, co.z
    theta = math.atan2(y - center_y, x)
    radial = 0.017 * math.sin(9 * theta) + 0.009 * math.sin(17 * theta + 0.7)
    x += math.cos(theta) * radial
    y += math.sin(theta) * radial
    z += 0.008 * math.sin(7 * theta + 1.3)
    return Vector((x, y, z))


def collection():
    col = bpy.data.collections.get("COLLECTOR")
    if col is not None:
        return col
    body = bpy.data.objects.get("Collector_Body")
    if body and body.users_collection:
        return body.users_collection[0]
    return bpy.context.scene.collection


def material(name, fallback):
    return bpy.data.materials.get(name) or bpy.data.materials.get(fallback)


def ensure_object(obj, col):
    if obj.name not in col.objects:
        for other in list(obj.users_collection):
            other.objects.unlink(obj)
        col.objects.link(obj)


def add_hood_rim(col):
    if bpy.data.objects.get("Collector_HoodRim") is not None:
        return
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.185,
        minor_radius=0.030,
        major_segments=32,
        minor_segments=10,
        location=(0.0, -0.265, 2.105),
        rotation=(math.radians(90), 0.0, 0.0),
    )
    rim = bpy.context.object
    rim.name = "Collector_HoodRim"
    mat = material("M_Collector_Leather", "M_Collector_Canvas")
    if mat:
        rim.data.materials.append(mat)
    ensure_object(rim, col)


def add_filter(col):
    if bpy.data.objects.get("Collector_Filter") is None:
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=20,
            radius=0.058,
            depth=0.15,
            location=(0.155, -0.345, 2.045),
            rotation=(0.0, math.radians(90), 0.0),
        )
        canister = bpy.context.object
        canister.name = "Collector_Filter"
        mat = material("M_Collector_Steel", "M_Collector_Brass")
        if mat:
            canister.data.materials.append(mat)
        ensure_object(canister, col)
    if bpy.data.objects.get("Collector_FilterCap") is None:
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=20,
            radius=0.064,
            depth=0.018,
            location=(0.232, -0.345, 2.045),
            rotation=(0.0, math.radians(90), 0.0),
        )
        cap = bpy.context.object
        cap.name = "Collector_FilterCap"
        mat = material("M_Collector_Steel", "M_Collector_Brass")
        if mat:
            cap.data.materials.append(mat)
        ensure_object(cap, col)


def reapply_bend(obj):
    if obj is None or obj.type != "MESH":
        return
    mw = obj.matrix_world.copy()
    inv = mw.inverted()
    for vertex in obj.data.vertices:
        world = mw @ vertex.co
        vertex.co = inv @ bend_world(world)
    obj.data.update()


def apply_wrinkles(obj):
    if obj is None or obj.type != "MESH":
        return
    mw = obj.matrix_world.copy()
    inv = mw.inverted()
    center_y = obj.location.y
    for vertex in obj.data.vertices:
        world = mw @ vertex.co
        world = bend_world(world)
        world = wrinkle(world, center_y)
        vertex.co = inv @ world
    obj.data.update()


def main():
    scene = bpy.context.scene
    if scene.get(SCENE_KEY):
        print("COLLECTOR_MANUAL: already applied")
        return

    col = collection()

    # Se crean antes de deformar para que el ribete y el filtro sigan a la máscara.
    add_hood_rim(col)
    add_filter(col)

    body_names = [
        "Collector_Body", "Collector_Belt", "Collector_OuterBelt",
        "Collector_Buckle", "Collector_Buckle.001", "Collector_Buckle_-1",
        "Collector_Buckle_1", "Collector_Pouch_-1", "Collector_Pouch_-1.001",
        "Collector_Pouch_1", "Collector_Pouch_1.001", "Collector_PouchFlap_-1",
        "Collector_PouchFlap_1", "Collector_Strap_-1", "Collector_Strap_-1.001",
        "Collector_Strap_1", "Collector_Strap_1.001", "Collector_ShoulderPad_-1",
        "Collector_ShoulderPad_1", "Collector_Pack", "Collector_Roll",
        "Collector_Drum_-1", "Collector_Drum_1", "Collector_DrumBand_-1_1.31",
        "Collector_DrumBand_-1_1.45", "Collector_DrumBand_-1_1.59",
        "Collector_DrumBand_1_1.31", "Collector_DrumBand_1_1.45",
        "Collector_DrumBand_1_1.59", "Collector_KeyRing", "Collector_Key_0",
        "Collector_Key_1", "Collector_Key_2", "Collector_Key_3",
        "Collector_Key_4", "Collector_LanternBody", "Collector_LanternCore",
        "Collector_LanternBar_-1", "Collector_LanternBar_0",
        "Collector_LanternBar_1", "Collector_LanternHook", "Collector_Mask",
        "Collector_GoggleRing_-1", "Collector_GoggleRing_1",
        "Collector_GoggleLens_-1", "Collector_GoggleLens_1",
        "Collector_Respirator", "Collector_RespiratorGrill",
        "Collector_Hose_0", "Collector_Hose_1", "Collector_Hose_2",
        "Collector_Hose_3", "Collector_Hose_4", "Collector_Hose_5",
        "Collector_Mouth", "Collector_Nose", "Collector_EyeSocket_-1",
        "Collector_EyeSocket_1", "Collector_Eye_-1", "Collector_Eye_1",
        "Collector_Tooth_0", "Collector_Tooth_1", "Collector_Tooth_2",
        "Collector_Tooth_3", "Collector_Tooth_4", "Collector_Tooth_5",
        "Collector_HoodRim", "Collector_Filter", "Collector_FilterCap",
    ]
    cloth_names = [
        "Collector_Coat", "Collector_Mantle", "Collector_CloakChest",
        "Collector_CloakSkirt", "Collector_Hood", "Collector_HoodOuter",
        "Collector_Rag_0", "Collector_Rag_1", "Collector_Rag_2",
        "Collector_Rag_3", "Collector_Rag_4", "Collector_Rag_5",
    ]

    for name in body_names:
        reapply_bend(bpy.data.objects.get(name))
    for name in cloth_names:
        apply_wrinkles(bpy.data.objects.get(name))

    scene[SCENE_KEY] = True
    bpy.ops.wm.save_mainfile()
    print("COLLECTOR_MANUAL_SAVED", bpy.data.filepath)

    # Render de revisión con la cámara y luces existentes.
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.filepath = RENDER_PATH
    try:
        bpy.ops.render.render(write_still=True)
        print("COLLECTOR_MANUAL_RENDER", RENDER_PATH)
    except Exception as exc:  # noqa: BLE001
        print("COLLECTOR_MANUAL_RENDER_FAILED", exc)


if __name__ == "__main__":
    main()
