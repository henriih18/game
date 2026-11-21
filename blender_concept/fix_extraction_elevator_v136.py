"""Mueve la extracción al ascensor SALIDA de recepción y revierte la sala oeste.

Base: nexus/nivel_01/NEXUS_L1_V05.blend (v135 con sala oeste).
Salida: el mismo archivo vivo, sin crear checkpoint nuevo.
"""
import bpy
import math
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
OUT = ROOT + "/nexus/nivel_01/NEXUS_L1_V05.blend"
FLOOR = -5.65

ROOM = bpy.data.collections.get("NEXUS_V05_EXTRACTION_ROOM")
HIST = bpy.data.collections.get("NEXUS_V05_EXTRACTION_HIST")
PLAY = bpy.data.collections.get("NEXUS_V05_REC_PLAY")
STRUCT = bpy.data.collections.get("V05_STRUCT")
CAMS = bpy.data.collections.get("V05_CAMS")


def move_to(obj, coll):
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    coll.objects.link(obj)


def del_prop(obj, key):
    if key in obj:
        del obj[key]


def remove_if(name):
    ob = bpy.data.objects.get(name)
    if ob:
        bpy.data.objects.remove(ob, do_unlink=True)


def box(name, center, size, material, coll):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        ob.data.materials.clear()
        ob.data.materials.append(material)
    move_to(ob, coll)
    return ob


def text(name, body, loc, size, material, coll):
    bpy.ops.object.text_add(location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.data.body = body
    ob.data.size = size
    ob.data.align_x = "CENTER"
    ob.data.align_y = "CENTER"
    ob.data.extrude = 0.003
    ob.rotation_euler = (math.pi / 2.0, 0.0, 0.0)
    if material:
        ob.data.materials.clear()
        ob.data.materials.append(material)
    move_to(ob, coll)
    return ob


def floor_text(name, body, loc, size, material, coll):
    bpy.ops.object.text_add(location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.data.body = body
    ob.data.size = size
    ob.data.align_x = "CENTER"
    ob.data.align_y = "CENTER"
    ob.data.extrude = 0.002
    ob.rotation_euler = (0.0, 0.0, 0.0)
    if material:
        ob.data.materials.clear()
        ob.data.materials.append(material)
    move_to(ob, coll)
    return ob


def parent_keep(child, parent):
    mw = child.matrix_world.copy()
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()
    child.matrix_world = mw


def make_camera(name, loc, target, lens, coll):
    data = bpy.data.cameras.get(name) or bpy.data.cameras.new(name)
    ob = bpy.data.objects.get(name)
    if ob is None:
        ob = bpy.data.objects.new(name, data)
        coll.objects.link(ob)
    else:
        ob.data = data
    ob.location = Vector(loc)
    direction = Vector(target) - Vector(loc)
    ob.rotation_mode = "XYZ"
    ob.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    data.lens = lens
    return ob


# 1. Restaurar muro del corredor y borrar la sala oeste.
wall = bpy.data.objects.get("NEXUS_V05_CORR_END_-22")
if wall:
    move_to(wall, STRUCT)
    wall.hide_render = False
    wall.hide_viewport = False
    wall.hide_set(False)
    for key in ("structural_change", "hide_reason", "original_hide_render",
                "original_hide_viewport", "original_collections"):
        del_prop(wall, key)
    wall["reverted_change"] = "extraction_room_v135"
    print("WALL_RESTORED", wall.name)

room_objects = set()
if ROOM:
    room_objects.update(o.name for o in ROOM.objects if o.name != "NEXUS_V05_CORR_END_-22")
room_objects.update(o.name for o in bpy.data.objects if o.name.startswith("NEXUS_V05_EXTR_"))
room_objects.update(o.name for o in bpy.data.objects if o.name.startswith("NEXUS_V05_REC_EXTRACT_"))
for name in sorted(room_objects):
    remove_if(name)
print("ROOM_OBJECTS_REMOVED", len(room_objects))

for coll in (HIST, ROOM):
    if coll:
        bpy.data.collections.remove(coll)
print("ROOM_COLLECTIONS_REMOVED", True)

# El rótulo SALIDA del fondo del corredor ya no corresponde a una salida:
# la extracción real está en el ascensor de recepción. Se oculta de forma reversible.
for sign_name in ("NEXUS_V05_CORR_END_SIGN_-22_PLATE", "NEXUS_V05_CORR_END_SIGN_-22_TEXT"):
    sign = bpy.data.objects.get(sign_name)
    if sign:
        if "original_hide_render" not in sign:
            sign["original_hide_render"] = bool(sign.hide_render)
            sign["original_hide_viewport"] = bool(sign.hide_viewport)
        sign["hide_reason"] = "extraction_moved_to_reception_elevator"
        sign.hide_render = True
        sign.hide_viewport = True
print("CORRIDOR_END_SIGN_HIDDEN", True)

# Despejar el frente del ascensor: la estación de café tapaba la salida.
break_root = bpy.data.objects.get("NEXUS_L1_DIS_BREAK_COUNTER")
if break_root and break_root.location.y > 7.5:
    moved = []
    for ob in bpy.data.objects:
        if ob.name.startswith("NEXUS_L1_DIS_BREAK_") and ob.parent is None:
            ob["original_location"] = [round(v, 4) for v in ob.location]
            ob["layout_fix"] = "elevator_extraction_clear"
            ob.location.y -= 1.8
            moved.append(ob.name)
    print("BREAK_STATION_MOVED", len(moved))
else:
    print("BREAK_STATION_ALREADY_CLEAR")

# 2. Crear extracción en el ascensor SALIDA de recepción.
mat_glow = bpy.data.materials.get("NEXUS_V05_MAT_ExtractGlow")
mat_screen = bpy.data.materials.get("NEXUS_V05_MAT_ExtractScreen")
mat_dark = bpy.data.materials.get("NEXUS_Dark_Metal")
mat_steel = bpy.data.materials.get("NEXUS_Steel")
mat_plate = bpy.data.materials.get("NEXUS_SignPlate")
mat_text = bpy.data.materials.get("NEXUS_SignText")
mat_amber = bpy.data.materials.get("NEXUS_Amber")

cx, cy = -17.50, 10.70
root = bpy.data.objects.new("NEXUS_V05_REC_EXTRACT_ZONE", None)
PLAY.objects.link(root)
root.location = (cx, cy, FLOOR)
root.empty_display_type = "PLAIN_AXES"
root.empty_display_size = 0.35
root["extraction_zone"] = True
root["zone_shape"] = "elevator_lobby"
root["zone_size_m"] = [2.10, 1.50]
root["activation_time_s"] = 10
root["required_players"] = 1
root["state"] = "standby"
root["route_stage"] = "reception_elevator_exit"
root["anchor"] = "NEXUS_V05_C_REC_ELEV_FRAME"
root["exit_type"] = "elevator"
root["exported_name"] = "extraction_reception_elevator"
root["layout_note"] = "Ascensor SALIDA dentro de recepcion, junto al reloj; zona en el lobby frontal."
bpy.context.view_layer.update()

# Aro rectangular de la zona, en el suelo.
z = FLOOR + 0.006
ring_specs = [
    ("NEXUS_V05_REC_EXTRACT_RING_N", (cx, 9.98, z), (2.10, 0.06, 0.012)),
    ("NEXUS_V05_REC_EXTRACT_RING_S", (cx, 11.42, z), (2.10, 0.06, 0.012)),
    ("NEXUS_V05_REC_EXTRACT_RING_W", (-18.55, cy, z), (0.06, 1.50, 0.012)),
    ("NEXUS_V05_REC_EXTRACT_RING_E", (-16.45, cy, z), (0.06, 1.50, 0.012)),
]
for name, center, size in ring_specs:
    ob = box(name, center, size, mat_glow, PLAY)
    ob["extraction_component"] = "zone_ring"
    parent_keep(ob, root)

# Consola mural a la derecha del ascensor, sin tapar el reloj ni el botón de llamada.
console_x = -15.10
console_y = 11.445
body = box("NEXUS_V05_REC_EXTRACT_CONSOLE", (console_x, console_y, -4.28),
           (0.52, 0.14, 0.62), mat_dark, PLAY)
body["extraction_component"] = "console"
body["mount"] = "wall_north_reception"
parent_keep(body, root)
screen = box("NEXUS_V05_REC_EXTRACT_SCREEN", (console_x, 11.368, -4.25),
             (0.40, 0.02, 0.30), mat_screen, PLAY)
screen["extraction_component"] = "screen"
parent_keep(screen, root)
indicator = box("NEXUS_V05_REC_EXTRACT_INDICATOR", (console_x - 0.17, 11.366, -4.00),
                (0.04, 0.02, 0.04), mat_amber, PLAY)
indicator["extraction_component"] = "indicator"
parent_keep(indicator, root)
button = box("NEXUS_V05_REC_EXTRACT_BUTTON", (console_x + 0.17, 11.366, -4.00),
             (0.06, 0.02, 0.05), mat_amber, PLAY)
button["extraction_component"] = "button"
parent_keep(button, root)

sign_x = console_x + 0.20
plate = box("NEXUS_V05_REC_EXTRACT_SIGN_PLATE", (sign_x, 11.495, -3.42),
            (1.35, 0.05, 0.28), mat_plate, PLAY)
plate["extraction_component"] = "sign_plate"
parent_keep(plate, root)
label = text("NEXUS_V05_REC_EXTRACT_SIGN_TEXT", "EXTRACCION", (sign_x, 11.455, -3.42),
             0.17, mat_text, PLAY)
label["extraction_component"] = "sign_text"
parent_keep(label, root)

floor_label = floor_text("NEXUS_V05_REC_EXTRACT_FLOOR_TEXT", "EXTRACCION",
                         (cx, 10.55, FLOOR + 0.012), 0.28, mat_text, PLAY)
floor_label["extraction_component"] = "floor_label"
parent_keep(floor_label, root)

# Luz naranja baja, coherente con la emergencia.
ld = bpy.data.lights.new("NEXUS_V05_REC_EXTRACT_LIGHT", type="POINT")
ld.energy = 8.0
ld.color = (1.0, 0.34, 0.08)
ld.shadow_soft_size = 0.16
ld.use_shadow = False
lo = bpy.data.objects.new("NEXUS_V05_REC_EXTRACT_LIGHT", ld)
PLAY.objects.link(lo)
lo.location = (console_x, 11.12, -3.94)
lo["extraction_component"] = "light"
parent_keep(lo, root)

# Cámara de revisión permanente, sin cambiar la cámara activa guardada.
cam = make_camera("NEXUS_V05_CAM_ExtractionElevator",
                  (-17.50, 7.90, -4.22), (-17.05, 11.45, -4.45), 15,
                  CAMS or PLAY)
cam["purpose"] = "review_extraction_elevator"

# Limpiar cámaras temporales y fijar la cámara guardada.
for name in ("TMP_CAM_REC_SALIDA", "TMP_CAM_CORR_W", "TMP_CAM_EXTR_E"):
    remove_if(name)
main_cam = bpy.data.objects.get("NEXUS_V05_CAM_Recepcion")
if main_cam:
    bpy.context.scene.camera = main_cam

# 3. Verificación rápida antes de guardar.
print("OBJECTS", len(bpy.data.objects))
print("SCENE_OBJECTS", len(bpy.context.scene.objects))
print("EXTR_PREFIX", len([o for o in bpy.data.objects if o.name.startswith("NEXUS_V05_EXTR_")]))
print("EXTRACT_GROUP", len([o for o in bpy.data.objects if o.name.startswith("NEXUS_V05_REC_EXTRACT")]))
print("PLAY", len(PLAY.objects) if PLAY else None)
print("ROOM_COLL", bool(bpy.data.collections.get("NEXUS_V05_EXTRACTION_ROOM")))
print("HIST_COLL", bool(bpy.data.collections.get("NEXUS_V05_EXTRACTION_HIST")))
print("WALL_COLLS", [c.name for c in wall.users_collection] if wall else None)
print("CAM", bpy.context.scene.camera.name if bpy.context.scene.camera else None)

bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("SAVED", OUT)
