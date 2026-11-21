import bpy
import math
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
OUT = ROOT + "/FM_NEXUS_V05_level1_v113.blend"
PREFIX = "NEXUS_V05_SERVICE_CONN_POLISH_"
COLL_NAME = "NEXUS_V05_SERVICE_CONN"

SCENE = bpy.context.scene
COLL = bpy.data.collections.get(COLL_NAME)
if COLL is None:
    raise RuntimeError("No existe la colección " + COLL_NAME)


def finish(ob, name, material):
    ob.name = name
    if ob.data is not None:
        ob.data.name = name + "_MESH"
    for m in list(ob.data.materials):
        pass
    ob.data.materials.clear()
    mat = bpy.data.materials.get(material)
    if mat is None:
        raise RuntimeError("Material no encontrado: " + material)
    ob.data.materials.append(mat)
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    COLL.objects.link(ob)
    return ob


def box(name, center, size, material, bevel=0.0, rotation=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    ob = bpy.context.active_object
    ob.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if rotation is not None:
        ob.rotation_mode = "QUATERNION"
        ob.rotation_quaternion = rotation
    if bevel > 0.0:
        mod = ob.modifiers.new("BEVEL", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return finish(ob, name, material)


def sign(name, body, center, facing, width=1.3, height=0.30, size=0.16):
    f = Vector(facing).normalized()
    q = f.to_track_quat("Z", "Y")
    box(name + "_PLATE", center, (width, height, 0.05), "NEXUS_SignPlate", bevel=0.004, rotation=q)
    bpy.ops.object.text_add(location=Vector(center) + f * 0.045)
    ob = bpy.context.active_object
    ob.data.body = body
    ob.data.size = size
    ob.data.align_x = "CENTER"
    ob.data.align_y = "CENTER"
    ob.data.extrude = 0.003
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion = q
    return finish(ob, name + "_TEXT", "NEXUS_SignText")


def wall_arrow(name, x, y, z, direction_y, material="NEXUS_Amber"):
    """Flecha plana en un muro orientada a lo largo de Y."""
    t = 0.012
    tip = 0.20
    back = -0.08
    half = 0.12
    y0 = y + back * direction_y
    y1 = y + tip * direction_y
    verts = [
        (x - t, y0, z - half), (x - t, y0, z + half), (x - t, y1, z),
        (x + t, y0, z - half), (x + t, y0, z + half), (x + t, y1, z),
    ]
    faces = [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]
    me = bpy.data.meshes.new(name + "_MESH")
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    COLL.objects.link(ob)
    return finish(ob, name, material)


def floor_arrow(name, x, y, z, direction_y=1.0, material="NEXUS_Amber"):
    """Flecha plana de suelo; direction_y=1 apunta al norte."""
    t = 0.004
    tip = 0.34
    back = -0.22
    half = 0.16
    y0 = y + back * direction_y
    y1 = y + tip * direction_y
    verts = [
        (x - half, y0, z), (x + half, y0, z), (x, y1, z),
        (x - half, y0, z + t), (x + half, y0, z + t), (x, y1, z + t),
    ]
    faces = [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]
    me = bpy.data.meshes.new(name + "_MESH")
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    COLL.objects.link(ob)
    return finish(ob, name, material)


# Limpiar una ejecución previa de este pulido
for ob in list(bpy.data.objects):
    if ob.name.startswith(PREFIX):
        bpy.data.objects.remove(ob, do_unlink=True)

# Zócalos metálicos oscuros, sin cubrir los vanos.
# Oeste: vano y -6,60..-5,00. Este: vano y -4,70..-3,50.
WAINSCOT_Z = -4.65
WAINSCOT_H = 1.70
for side, x, segments in (
    ("W", 4.153, [(-9.40, -6.60), (-5.00, -2.00)]),
    ("E", 5.847, [(-9.40, -4.70), (-3.50, -2.00)]),
):
    for i, (y0, y1) in enumerate(segments):
        cy = (y0 + y1) / 2.0
        ly = y1 - y0
        box(
            f"{PREFIX}WAINSCOT_{side}_{i}",
            (x, cy, WAINSCOT_Z),
            (0.014, ly, WAINSCOT_H),
            "NEXUS_Rack_Paint",
        )
        box(
            f"{PREFIX}WAINSCOT_{side}_{i}_TOP",
            (x, cy, WAINSCOT_Z + WAINSCOT_H / 2.0 + 0.015),
            (0.024, ly, 0.035),
            "NEXUS_Steel",
        )
        box(
            f"{PREFIX}WAINSCOT_{side}_{i}_KICK",
            (x, cy, -5.54),
            (0.024, ly, 0.14),
            "NEXUS_Steel",
        )
        # Refuerzos verticales discretos
        for j, yy in enumerate((y0 + 0.25, y1 - 0.25)):
            box(
                f"{PREFIX}WAINSCOT_{side}_{i}_RIB_{j}",
                (x, yy, WAINSCOT_Z),
                (0.026, 0.025, WAINSCOT_H),
                "NEXUS_Steel",
            )

# Señalización interior de los dos vanos.
sign(
    PREFIX + "SIGN_MUELLE",
    "MUELLE // CARGA",
    (4.165, -5.80, -2.58),
    (1, 0, 0),
    width=1.35,
    height=0.28,
    size=0.15,
)
sign(
    PREFIX + "SIGN_MANTENIMIENTO",
    "MANTENIMIENTO",
    (5.835, -4.10, -2.58),
    (-1, 0, 0),
    width=1.15,
    height=0.28,
    size=0.16,
)

# Señal de orientación en el muro de fondo que se ve al entrar desde el almacén.
sign(
    PREFIX + "SIGN_DIR_MANT",
    "MANTENIMIENTO",
    (5.835, -5.62, -2.98),
    (-1, 0, 0),
    width=1.15,
    height=0.26,
    size=0.15,
)
wall_arrow(PREFIX + "ARROW_MANT", 5.828, -5.48, -3.42, 1.0)

# Señal de orientación en el muro de fondo que se ve al entrar desde mantenimiento.
sign(
    PREFIX + "SIGN_DIR_MUELLE",
    "MUELLE",
    (4.165, -4.28, -2.98),
    (1, 0, 0),
    width=1.0,
    height=0.26,
    size=0.17,
)
wall_arrow(PREFIX + "ARROW_MUELLE", 4.172, -4.14, -3.42, -1.0)

# Flechas de suelo en el eje del pasillo.
floor_arrow(PREFIX + "FLOOR_ARROW_N", 5.00, -5.15, -5.642, 1.0)
floor_arrow(PREFIX + "FLOOR_ARROW_S", 5.00, -6.25, -5.642, -1.0)

# Ajuste de luces: algo más tenue y con la luminaria por debajo del difusor.
for name, energy in (
    ("NEXUS_V05_SERVICE_CONN_LIGHT_0", 110.0),
    ("NEXUS_V05_SERVICE_CONN_LIGHT_1", 110.0),
    ("NEXUS_V05_SERVICE_CONN_EMERGENCY_LIGHT", 22.0),
):
    ob = bpy.data.objects.get(name)
    if ob and ob.type == "LIGHT":
        ob.data.energy = energy
for name in ("NEXUS_V05_SERVICE_CONN_LIGHT_0", "NEXUS_V05_SERVICE_CONN_LIGHT_1"):
    ob = bpy.data.objects.get(name)
    if ob:
        ob.location.z = -1.98

# Cámara de revisión del pasillo.
cam = bpy.data.objects.get("NEXUS_V05_SERVICE_CONN_CAM_ServiceConn")
if cam is None:
    data = bpy.data.cameras.new("NEXUS_V05_SERVICE_CONN_CAM_ServiceConn")
    cam = bpy.data.objects.new("NEXUS_V05_SERVICE_CONN_CAM_ServiceConn", data)
    bpy.context.scene.collection.objects.link(cam)
cam.location = (5.00, -8.70, -3.70)
target = Vector((5.00, -4.20, -3.55))
cam.rotation_mode = "XYZ"
cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
cam.data.lens = 18

# Quitar cámaras temporales de revisión.
for name in ("TMP_CAM_STORE_CONN", "TMP_CAM_MAINT_CONN"):
    ob = bpy.data.objects.get(name)
    if ob:
        bpy.data.objects.remove(ob, do_unlink=True)

# Cámara activa estable del proyecto.
base_cam = bpy.data.objects.get("NEXUS_V05_CAM_Corridor")
if base_cam:
    SCENE.camera = base_cam

bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("SAVED", OUT)
print("OBJECTS", len(bpy.data.objects))
print("SERVICE_CONN", len(COLL.objects))
print("POLISH", len([o for o in bpy.data.objects if o.name.startswith(PREFIX)]))
print("TMP", [o.name for o in bpy.data.objects if o.name.startswith("TMP_")])
