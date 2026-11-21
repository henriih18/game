"""Pase de iluminación de la RECEPCIÓN del Nivel 1 (v126).

Motivo: la luz de área de 900 W estaba a 6 cm del techo, generando
shadow acne en forma de trama de puntos, y el relleno de 1100 W aplanaba
toda la sala. Este pase reemplaza el esquema por focos empotrados con
sombras, prácticos cálidos y emergencia roja, manteniendo el mobiliario
existente y sin tocar otras salas.
"""

import bpy
from mathutils import Vector

RECEP_LIGHTS = "V05_LIGHTS"
COLLECTION = "NEXUS_V05_REC_PASS126"

# (x, y) de los seis downlights construidos en el pase de geometría
CANS = [(-17.0, 3.6), (-12.0, 3.6), (-7.0, 3.6),
        (-17.0, 9.8), (-12.0, 9.8), (-7.0, 9.8)]
# dos luminarias fundidas: aportan lectura de abandono y ahorran luces
DEAD = {(-7.0, 3.6), (-7.0, 9.8)}


def collection():
    coll = bpy.data.collections.get(COLLECTION)
    if coll is None:
        coll = bpy.data.collections.new(COLLECTION)
        bpy.context.scene.collection.children.link(coll)
    return coll


def target_collection():
    return bpy.data.collections.get(RECEP_LIGHTS) or collection()


def light(name, kind, loc, energy, color, rot=(0.0, 0.0, 0.0), **kwargs):
    coll = target_collection()
    obj = bpy.data.objects.get(name)
    if obj is None or obj.type != "LIGHT":
        data = bpy.data.lights.new(name, kind)
        obj = bpy.data.objects.new(name, data)
        coll.objects.link(obj)
    obj.data.type = kind
    obj.data.energy = energy
    obj.data.color = color
    obj.location = Vector(loc)
    obj.rotation_euler = rot
    for key, value in kwargs.items():
        setattr(obj.data, key, value)
    return obj


def dead_material():
    mat = bpy.data.materials.get("NEXUS_V05_MAT_LED_Dead")
    if mat is None:
        mat = bpy.data.materials.new("NEXUS_V05_MAT_LED_Dead")
        mat.use_nodes = True
        bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        bsdf.inputs["Base Color"].default_value = (0.035, 0.038, 0.035, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.30
        bsdf.inputs["Metallic"].default_value = 0.0
    return mat


def main():
    scene = bpy.context.scene

    # --- 1. la vieja luz de techo deja de estar embebida y de proyectar sombra ---
    old = bpy.data.objects.get("NEXUS_V05_RECEPCION_LIGHT")
    if old is not None:
        old.data.type = "AREA"
        old.data.shape = "RECTANGLE"
        old.data.size = 2.6
        old.data.size_y = 0.55
        old.data.energy = 90.0
        old.data.color = (0.95, 0.93, 0.88)
        old.data.use_shadow = False
        old.location = (-12.0, 6.7, -0.62)

    # --- 2. el relleno plano de 1100 W pasa a ser un rebote suave ---
    fill = bpy.data.objects.get("NEXUS_V05_REC_FILL.001")
    if fill is not None:
        fill.data.energy = 120.0
        fill.data.use_shadow = False
        fill.data.size = 8.0
        fill.data.size_y = 5.0
        fill.location = (-12.0, 6.0, -2.6)

    # --- 3. focos empotrados con sombra: charcos de luz en el suelo ---
    index_light = 0
    for (x, y) in CANS:
        if (x, y) in DEAD:
            continue
        index_light += 1
        light(
            f"NEXUS_V05_REC_SPOT_{index_light}", "SPOT", (x, y, -0.16), 850.0,
            (1.0, 0.90, 0.78), spot_size=1.05, spot_blend=0.55,
            shadow_soft_size=0.05, use_shadow=True,
        )

    # --- 4. lámparas colgantes existentes ---
    light("NEXUS_V05_REC_PEND_LIGHT_0", "POINT", (-15.0, 8.0, -2.62), 45.0,
          (1.0, 0.86, 0.70), shadow_soft_size=0.16, use_shadow=True)
    light("NEXUS_V05_REC_PEND_LIGHT_1", "POINT", (-9.0, 8.0, -2.62), 30.0,
          (1.0, 0.86, 0.70), shadow_soft_size=0.16, use_shadow=True)

    # --- 5. práctico cálido sobre el mostrador ---
    light("NEXUS_V05_REC_DESK_LAMP_LIGHT", "POINT", (-9.4, 8.1, -4.62), 55.0,
          (1.0, 0.80, 0.56), shadow_soft_size=0.12, use_shadow=False)

    # --- 6. emergencia roja interior ---
    light("NEXUS_V05_REC_EMERG_DOOR", "POINT", (-13.4, 2.12, -3.0), 30.0,
          (1.0, 0.07, 0.03), shadow_soft_size=0.07, use_shadow=False)
    light("NEXUS_V05_REC_EMERG_NW", "POINT", (-19.55, 10.6, -3.0), 22.0,
          (1.0, 0.09, 0.04), shadow_soft_size=0.07, use_shadow=False)
    # rebotes suaves hacia el techo para que se lean los servicios
    for index, (x, y) in enumerate(((-16.0, 5.0), (-9.5, 8.0)), start=1):
        bounce = light(f"NEXUS_V05_REC_CEILING_BOUNCE_{index}", "AREA",
                       (x, y, -2.9), 30.0, (0.88, 0.92, 1.0),
                       rot=(3.1416, 0.0, 0.0), shape="RECTANGLE", use_shadow=False)
        bounce.data.size = 4.0
        bounce.data.size_y = 3.0

    # --- 7. retroiluminación del rótulo corporativo ---
    sign = light("NEXUS_V05_REC_SIGN_WASH", "AREA", (-12.0, 10.85, -2.55), 30.0,
                 (1.0, 0.80, 0.58), rot=(1.5708, 0.0, 0.0),
                 shape="RECTANGLE", use_shadow=False)
    sign.data.size = 3.2
    sign.data.size_y = 0.9

    # --- 8. luminarias fundidas ---
    # --- emissividad de las lentes encendidas ---
    led = bpy.data.materials.get("NEXUS_V05_MAT_LED_Panel")
    if led is not None:
        bsdf = next((n for n in led.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if bsdf is not None:
            bsdf.inputs["Emission Strength"].default_value = 18.0
    dead = dead_material()
    switched = 0
    for index, (x, y) in enumerate(CANS, start=1):
        if (x, y) not in DEAD:
            continue
        lens = bpy.data.objects.get(f"NEXUS_V05_REC_CS_DOWNLIGHT_LENS_{index - 1}")
        if lens is None:
            continue
        lens.data.materials.clear()
        lens.data.materials.append(dead)
        switched += 1

    # --- informe ---
    lights = [o for o in target_collection().objects if o.type == "LIGHT"]
    print("REC_LIGHTS_IN_COLLECTION", len(lights))
    print("DEAD_FIXTURES", switched)
    print("EEVEE samples:", scene.eevee.taa_render_samples)


main()
