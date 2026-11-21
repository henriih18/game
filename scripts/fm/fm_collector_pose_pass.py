"""Pase de pose y silueta para El Coleccionista.

- Inclina el torso hacia delante (joroba real, ~22 grados) desde la cintura.
- Añade pliegues radiales a la ropa (abrigo, capa, capucha, harapos).
- Crea un faldón deshilachado en el bajo del abrigo.
- Elimina las envolturas de guante que ocultaban los dedos.
- Oscurece la piel y guarda el .blend + render de revisión.

Se ejecuta headless sobre FM_COLLECTOR_SCULPT.blend. No toca el nivel ni la
referencia. Idempotente por la propiedad de escena `collector_pose_pass_v1`.
"""

import math

import bpy
from mathutils import Vector

KEY = "collector_pose_pass_v1"
RENDER = "/tmp/opencode/collector_pose1.png"
CLOTH = (
    "Collector_Coat", "Collector_Mantle", "Collector_CloakChest",
    "Collector_CloakSkirt", "Collector_Hood", "Collector_HoodOuter",
    "Collector_Rag_0", "Collector_Rag_1", "Collector_Rag_2",
    "Collector_Rag_3", "Collector_Rag_4", "Collector_Rag_5",
)


def smoothstep(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3.0 - 2.0 * t)


def lean(point):
    """Rotación hacia delante alrededor de X, con pivote en la cintura."""
    x, y, z = point.x, point.y, point.z
    if z <= 1.18:
        return Vector((x, y, z))
    angle = math.radians(22.0) * smoothstep(1.18, 2.25, z)
    ca, sa = math.cos(angle), math.sin(angle)
    py = y
    pz = z - 1.18
    return Vector((x, py * ca - pz * sa, 1.18 + py * sa + pz * ca))


def apply_lean(obj):
    if obj.type != "MESH":
        return
    mw = obj.matrix_world.copy()
    inv = mw.inverted()
    for v in obj.data.vertices:
        v.co = inv @ lean(mw @ v.co)
    obj.data.update()


def add_cloth_detail(obj, phase):
    if obj.type != "MESH":
        return
    # Geometría suficiente para que los pliegues se lean.
    sub = obj.modifiers.new("ClothSub", "SUBSURF")
    sub.subdivision_type = "SIMPLE"
    sub.levels = 2
    sub.render_levels = 2
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=sub.name)
    obj.select_set(False)

    mw = obj.matrix_world.copy()
    inv = mw.inverted()
    for v in obj.data.vertices:
        w = mw @ v.co
        theta = math.atan2(w.y, w.x)
        radial = (0.026 * math.sin(13.0 * theta + phase)
                  + 0.012 * math.sin(23.0 * theta + 0.7)
                  + 0.006 * math.sin(7.0 * theta + 1.9))
        w.x += math.cos(theta) * radial
        w.y += math.sin(theta) * radial
        w.z += 0.010 * math.sin(9.0 * theta + phase)
        v.co = inv @ w
    obj.data.update()


def darken_skin():
    for name in ("M_Collector_Skin", "M_Collector_Skin.001"):
        mat = bpy.data.materials.get(name)
        if mat is None or not mat.use_nodes:
            continue
        for node in mat.node_tree.nodes:
            if node.type == "BSDF_PRINCIPLED":
                node.inputs["Base Color"].default_value = (0.10, 0.075, 0.055, 1.0)
                node.inputs["Roughness"].default_value = 0.88


def remove_glove_wrap():
    for side in ("-1", "1"):
        obj = bpy.data.objects.get("Collector_GloveWrap_%s" % side)
        if obj is not None:
            bpy.data.objects.remove(obj, do_unlink=True)


def add_hem_strips(col):
    if bpy.data.objects.get("Collector_HemStrip_0") is not None:
        return
    mat = bpy.data.materials.get("M_Collector_Canvas")
    for i in range(16):
        ang = math.tau * i / 16.0
        r = 0.50 + 0.02 * math.sin(i * 2.3)
        length = 0.20 + 0.16 * (0.5 + 0.5 * math.sin(i * 1.7))
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(math.cos(ang) * r, math.sin(ang) * r, 0.62 - length * 0.5),
            rotation=(0.0, 0.0, ang),
        )
        ob = bpy.context.object
        ob.name = "Collector_HemStrip_%d" % i
        ob.scale = (0.09, 0.022, length)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        if mat:
            ob.data.materials.append(mat)
        if ob.name not in col.objects:
            for other in list(ob.users_collection):
                other.objects.unlink(ob)
            col.objects.link(ob)


def main():
    scene = bpy.context.scene
    if scene.get(KEY):
        print("COLLECTOR_POSE: already applied")
        return
    col = bpy.data.collections.get("COLLECTOR")
    if col is None:
        body = bpy.data.objects.get("Collector_Body")
        col = body.users_collection[0] if body and body.users_collection else scene.collection

    remove_glove_wrap()
    darken_skin()

    # La ropa se detalla antes de inclinarla para que los pliegues sigan la pose.
    for i, name in enumerate(CLOTH):
        obj = bpy.data.objects.get(name)
        if obj is not None:
            add_cloth_detail(obj, phase=i * 0.7)

    # Inclinación de todo el cuerpo/equipo.
    for obj in list(bpy.data.objects):
        if obj.name.startswith("Collector_") and obj.name != "Collector_Body_High":
            apply_lean(obj)

    add_hem_strips(col)
    scene[KEY] = True
    bpy.ops.wm.save_mainfile()
    print("COLLECTOR_POSE_SAVED", bpy.data.filepath)

    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.filepath = RENDER
    try:
        bpy.ops.render.render(write_still=True)
        print("COLLECTOR_POSE_RENDER", RENDER)
    except Exception as exc:  # noqa: BLE001
        print("COLLECTOR_POSE_RENDER_FAILED", exc)


if __name__ == "__main__":
    main()
