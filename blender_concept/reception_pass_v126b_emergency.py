"""Recepción del Nivel 1 (v126b): iluminación de emergencia únicamente.

El complejo está abandonado: no hay corriente general. Se apagan todos los
practicables (focos empotrados, colgantes, relleno, luz de rótulo) y las
lentes dejan de emitir. Solo quedan lámparas de emergencia rojas y la
señalización de evacuación con batería propia.

No se borran luces: se apagan y se ocultan para poder revertir el pase.
"""

import bpy
from mathutils import Vector

RECEP = ((-20.4, -3.6), (1.4, 12.0), (-6.2, 0.6))
RECEP_LIGHTS = "V05_LIGHTS"
PASS_COLLECTION = "NEXUS_V05_REC_PASS126"

# luces que dejan de funcionar (electricidad cortada)
NORMAL_LIGHTS = [
    "NEXUS_V05_RECEPCION_LIGHT",
    "NEXUS_V05_REC_FILL.001",
    "NEXUS_V05_REC_SPOT_1",
    "NEXUS_V05_REC_SPOT_2",
    "NEXUS_V05_REC_SPOT_3",
    "NEXUS_V05_REC_SPOT_4",
    "NEXUS_V05_REC_PEND_LIGHT_0",
    "NEXUS_V05_REC_PEND_LIGHT_1",
    "NEXUS_V05_REC_DESK_LAMP_LIGHT",
    "NEXUS_V05_REC_SIGN_WASH",
    "NEXUS_V05_REC_CEILING_BOUNCE_1",
    "NEXUS_V05_REC_CEILING_BOUNCE_2",
    "NEXUS_V05_OFFICE_LIGHT",
    "NEXUS_V05_REST_LIGHT",
]

# lentes y difusores que dejan de brillar
DEAD_SURFACES = [
    "NEXUS_V05_C_REC_PEND_BULB_0",
    "NEXUS_V05_C_REC_PEND_BULB_1",
    "NEXUS_V05_RECEPCION_STRIP",
    "NEXUS_V05_OFFICE_LIGHT_PANEL",
    "NEXUS_V05_REST_LIGHT_PANEL",
    "NEXUS_V05_REC_CS_DOWNLIGHT_LENS_0",
    "NEXUS_V05_REC_CS_DOWNLIGHT_LENS_1",
    "NEXUS_V05_REC_CS_DOWNLIGHT_LENS_3",
    "NEXUS_V05_REC_CS_DOWNLIGHT_LENS_4",
    "NEXUS_V05_REC_CS_SMOKE_DETECTOR_LED_0",
    "NEXUS_V05_REC_CS_SMOKE_DETECTOR_LED_1",
    "NEXUS_V05_REC_CS_SMOKE_DETECTOR_LED_2",
]

# emergencias: nombre, posición, energía, color, radio de fuente
EMERGENCIES = [
    ("NEXUS_V05_REC_EMERG_DOOR", (-13.4, 2.30, -2.55), 210.0, (1.0, 0.06, 0.02), 0.12),
    ("NEXUS_V05_REC_EMERG_NW", (-19.55, 10.6, -2.55), 200.0, (1.0, 0.08, 0.03), 0.12),
    ("NEXUS_V05_REC_EMERG_N", (-17.6, 11.30, -2.55), 200.0, (1.0, 0.07, 0.02), 0.12),
    ("NEXUS_V05_REC_EMERG_E", (-4.45, 6.4, -2.55), 190.0, (1.0, 0.06, 0.02), 0.12),
    ("NEXUS_V05_REC_EMERG_OFFICE", (-6.6, 6.2, -3.45), 30.0, (1.0, 0.07, 0.03), 0.09),
    ("NEXUS_V05_REC_EMERG_REST", (-6.6, 3.0, -3.45), 25.0, (1.0, 0.07, 0.03), 0.09),
]


def collection():
    coll = bpy.data.collections.get(PASS_COLLECTION)
    if coll is None:
        coll = bpy.data.collections.new(PASS_COLLECTION)
        bpy.context.scene.collection.children.link(coll)
    return coll


def dead_material():
    mat = bpy.data.materials.get("NEXUS_V05_MAT_LED_Dead")
    if mat is None:
        mat = bpy.data.materials.new("NEXUS_V05_MAT_LED_Dead")
        mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (0.03, 0.033, 0.031, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.32
    bsdf.inputs["Emission Strength"].default_value = 0.0
    return mat


def dim_sign_material():
    """Señalización con batería: emite, pero mucho menos que un rótulo vivo."""
    mat = bpy.data.materials.get("NEXUS_V05_MAT_Sign_Battery")
    if mat is None:
        mat = bpy.data.materials.new("NEXUS_V05_MAT_Sign_Battery")
        mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (0.02, 0.024, 0.022, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.5
    bsdf.inputs["Emission Color"].default_value = (1.0, 0.42, 0.09, 1.0)
    bsdf.inputs["Emission Strength"].default_value = 0.0
    return mat


def main():
    # 1. apagar practicables
    off = 0
    for name in NORMAL_LIGHTS:
        light = bpy.data.objects.get(name)
        if light is None:
            continue
        light.data.energy = 0.0
        light.data.use_shadow = False
        light.hide_render = True
        light.hide_viewport = True
        light["power_state"] = "sin corriente (complejo abandonado)"
        off += 1

    # 2. lentes y difusores apagados
    dead = dead_material()
    dark = 0
    for name in DEAD_SURFACES:
        obj = bpy.data.objects.get(name)
        if obj is None or obj.type != "MESH":
            continue
        obj.data.materials.clear()
        obj.data.materials.append(dead)
        dark += 1

    # 3. emergencias rojas
    coll = bpy.data.collections.get(RECEP_LIGHTS) or collection()
    for name, loc, energy, color, radius in EMERGENCIES:
        obj = bpy.data.objects.get(name)
        if obj is None or obj.type != "LIGHT":
            data = bpy.data.lights.new(name, "POINT")
            obj = bpy.data.objects.new(name, data)
            coll.objects.link(obj)
        obj.data.type = "POINT"
        obj.data.energy = energy
        obj.data.color = color
        obj.data.shadow_soft_size = radius
        obj.data.use_shadow = True
        obj.location = Vector(loc)
        obj.hide_render = False
        obj.hide_viewport = False
        obj["power_state"] = "emergencia"

    # 4. señalización con batería
    sign = dim_sign_material()
    sign_objects = [
        "NEXUS_V05_E_CORR_SIGN_RECEPCION_PLATE",
        "NEXUS_V05_REC_SIGN_PLATE",
        "NEXUS_V05_REC_WALLSIGN_PLATE",
        "NEXUS_V05_C_REC_ELEV_SIGN_PLATE",
        "NEXUS_V05_OFFICE_SIGN_PLATE",
        "NEXUS_V05_REST_SIGN_PLATE",
        "NEXUS_V05_OFFICE_EXT_SIGN_PLATE",
        "NEXUS_V05_C_REC_DIR_BOARD",
        "NEXUS_V05_C_REC_LOGOPANEL",
    ]
    dimmed = 0
    for name in sign_objects:
        obj = bpy.data.objects.get(name)
        if obj is None or obj.type != "MESH":
            continue
        obj.data.materials.clear()
        obj.data.materials.append(sign)
        dimmed += 1

    # 5. textos de señalización: bajar emisión sin tocar el material compartido
    text_mat = bpy.data.materials.get("NEXUS_V05_MAT_Sign_Text")
    if text_mat is None:
        text_mat = bpy.data.materials.new("NEXUS_V05_MAT_Sign_Text")
        text_mat.use_nodes = True
    tbsdf = next(n for n in text_mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    tbsdf.inputs["Base Color"].default_value = (0.55, 0.30, 0.09, 1.0)
    tbsdf.inputs["Emission Color"].default_value = (1.0, 0.46, 0.12, 1.0)
    tbsdf.inputs["Emission Strength"].default_value = 0.22
    texts = 0
    for obj in bpy.data.objects:
        if obj.type != "FONT" or obj.hide_render:
            continue
        loc = obj.matrix_world.translation
        if not (RECEP[0][0] <= loc.x <= RECEP[0][1] and RECEP[1][0] <= loc.y <= RECEP[1][1]):
            continue
        obj.data.materials.clear()
        obj.data.materials.append(text_mat)
        texts += 1

    print("LIGHTS_OFF", off)
    print("SURFACES_DEAD", dark)
    print("EMERGENCIES", len(EMERGENCIES))
    print("SIGNS_DIMMED", dimmed, "TEXTS", texts)


main()
