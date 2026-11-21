"""FRECUENCIA MUERTA - Recepcion Nivel 1 - pase de luz y rotulacion (v127).

La sala esta sin corriente: solo deben verse las lamparas de emergencia.
Este pase:

  * Apaga las emisiones que sobrevivieron al corte (pantallas, rotulos,
    pulsadores y la lampara de tubo del mostrador).
  * Baja la saturacion del rojo puro para que las superficies se distingan.
  * Anade la luz fria que se cuela desde el pasillo por la puerta de vidrio,
    que es la unica fuente de contraste fisicamente coherente.
  * Refuerza la emergencia en el tramo este, que quedaba a oscuras.

Idempotente.
"""

import bpy
import math

REC_LIGHTS = {
    "NEXUS_V05_REC_EMERG_DOOR": 85.0,
    "NEXUS_V05_REC_EMERG_N": 95.0,
    "NEXUS_V05_REC_EMERG_NW": 95.0,
    "NEXUS_V05_REC_EMERG_E": 80.0,
    "NEXUS_V05_REC_EMERG_OFFICE": 18.0,
    "NEXUS_V05_REC_EMERG_REST": 16.0,
}
EMERGENCY_COLOR = (1.0, 0.13, 0.07)
SPILL_NAME = "NEXUS_V05_REC_SPILL_CORRIDOR"


def set_emission(mat_name, strength, base_color=None):
    mat = bpy.data.materials.get(mat_name)
    if mat is None or not mat.use_nodes:
        return None
    bsdf = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        return None
    bsdf.inputs["Emission Strength"].default_value = strength
    if base_color is not None:
        bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
    return mat


def dead_material(name, color=(0.05, 0.055, 0.05), roughness=0.55, metallic=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Emission Strength"].default_value = 0.0
    return mat


def kill_pipe_lamp():
    """La lampara de tubo del mostrador seguia emitiendo a 82.4."""
    targets = [
        ("NEXUS_ASSET_L1R_REC_LAMP_pipe_lamp", dead_material("NEXUS_V05_MAT_Lamp_Dead_Shell", (0.09, 0.08, 0.06), 0.42, 0.85)),
        ("NEXUS_ASSET_L1R_REC_LAMP_pipe_lamp_bulb", dead_material("NEXUS_V05_MAT_Lamp_Dead_Bulb", (0.10, 0.10, 0.09), 0.35, 0.0)),
        ("NEXUS_ASSET_L1R_REC_LAMP_pipe_lamp_switch", dead_material("NEXUS_V05_MAT_Lamp_Dead_Switch", (0.07, 0.07, 0.06), 0.55, 0.0)),
    ]
    changed = 0
    for obj_name, mat in targets:
        obj = bpy.data.objects.get(obj_name)
        if obj is None or obj.type != "MESH" or not obj.data.materials:
            continue
        if obj.material_slots[0].link != "OBJECT":
            obj.material_slots[0].link = "OBJECT"
        obj.material_slots[0].material = mat
        changed += 1
    return changed


def tune_emergency_lights():
    touched = 0
    for name, energy in REC_LIGHTS.items():
        light = bpy.data.objects.get(name)
        if light is None or light.type != "LIGHT":
            continue
        data = light.data
        data.energy = energy
        data.color = EMERGENCY_COLOR
        data.use_shadow = True
        data.cutoff_distance = 26.0
        touched += 1
    return touched


def build_corridor_spill():
    """Luz fria del pasillo entrando por la puerta de vidrio."""
    existing = bpy.data.objects.get(SPILL_NAME)
    if existing:
        bpy.data.objects.remove(existing, do_unlink=True)

    light_data = bpy.data.lights.new(SPILL_NAME, "AREA")
    light_data.shape = "RECTANGLE"
    light_data.size = 2.2
    light_data.size_y = 3.2
    light_data.energy = 140.0
    light_data.color = (0.55, 0.68, 0.86)
    light_data.use_shadow = True
    light_data.cutoff_distance = 13.0

    obj = bpy.data.objects.new(SPILL_NAME, light_data)
    coll = bpy.data.collections.get("NEXUS_V05_REC_PLAY")
    (coll or bpy.context.scene.collection).objects.link(obj)
    obj.location = (-12.0, 1.15, -4.25)
    obj.rotation_euler = (math.radians(90.0), 0.0, 0.0)
    obj["purpose"] = "spill_corridor"
    return obj


def build_east_emergency():
    """Lampara extra en el tramo este, junto a la escalera, para no dejar un pozo negro."""
    name = "NEXUS_V05_REC_EMERG_MID"
    existing = bpy.data.objects.get(name)
    if existing:
        bpy.data.objects.remove(existing, do_unlink=True)
    data = bpy.data.lights.new(name, "POINT")
    data.energy = 55.0
    data.color = EMERGENCY_COLOR
    data.shadow_soft_size = 0.12
    data.use_shadow = True
    data.cutoff_distance = 26.0
    obj = bpy.data.objects.new(name, data)
    coll = bpy.data.collections.get("NEXUS_V05_REC_PLAY")
    (coll or bpy.context.scene.collection).objects.link(obj)
    obj.location = (-9.6, 10.9, -2.95)
    return obj


def main():
    # rotulacion y pantallas sin corriente
    set_emission("NEXUS_Screen", 0.0, (0.02, 0.025, 0.025))
    set_emission("NEXUS_V05_MAT_Sign_Text", 0.03)
    set_emission("NEXUS_V05_MAT_Sign_Battery", 0.0)
    set_emission("NEXUS_Amber", 0.0)
    # La lampara de tubo se apago en la biblioteca compartida
    # (industrial_pipe_lamp tenia emision 82.4); aqui ya no hace falta tocarla.
    killed = 0
    lights = tune_emergency_lights()
    spill = build_corridor_spill()
    mid = build_east_emergency()

    print("LAMP_OBJECTS_KILLED", killed)
    print("EMERGENCY_TUNED", lights)
    print("SPILL", spill.name, spill.data.energy)
    print("MID", mid.name, mid.data.energy)


main()
