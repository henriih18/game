import bpy
import os
import math
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
OUT = os.path.join(ROOT, "FM_NEXUS_V05_level1_v110.blend")
ASSET_ROOT = os.path.join(ROOT, "assets", "Modelos 3D")
PREFIX = "NEXUS_ASSET_V05_"
COLL_NAME = "NEXUS_ASSET_V05"
FLOOR = -5.65
SCENE = bpy.context.scene

ASSETS = {
    "cart": ("Mobiliario y almacenamiento", "industrial_storage_cart_2k", "industrial_storage_cart"),
    "crate": ("Mobiliario y almacenamiento", "plastic_crate_01_1k", "plastic_crate_01"),
    "box": ("Objetos pequeños y narrativa ambiental", "cardboard_box_01_2k", "cardboard_box_01"),
    "barrel": ("Objetos pequeños y narrativa ambiental", "Barrel_02_2k", "Barrel_02"),
    "toolbox": ("Objetos pequeños y narrativa ambiental", "metal_toolbox_2k", "metal_toolbox"),
    "caged": ("Infraestructura industrial y mantenimiento", "caged_hanging_light_2k", "caged_hanging_light"),
    "power": ("Infraestructura industrial y mantenimiento", "power_box_01_2k", "power_box_01"),
    "ext": ("Infraestructura industrial y mantenimiento", "korean_fire_extinguisher_01_2k", "korean_fire_extinguisher_01"),
}


def ensure_collection():
    coll = bpy.data.collections.get(COLL_NAME)
    if coll is None:
        coll = bpy.data.collections.new(COLL_NAME)
        SCENE.collection.children.link(coll)
    return coll


COLL = ensure_collection()

# Remove previous run objects from this asset pass only.
for ob in list(bpy.data.objects):
    if ob.name.startswith(PREFIX):
        bpy.data.objects.remove(ob, do_unlink=True)

# Remove temporary review cameras if they survived from inspection.
for tmp_name in ("TMP_CAM_STORE_EAST", "TMP_REVIEW_STORE_E", "TMP_REVIEW_MAINT_W"):
    tmp_cam = bpy.data.objects.get(tmp_name)
    if tmp_cam:
        bpy.data.objects.remove(tmp_cam, do_unlink=True)


def asset_path(key):
    folder, blend_name, _ = ASSETS[key]
    return os.path.join(ASSET_ROOT, folder, blend_name + ".blend", blend_name + ".blend")


def import_asset(key, label):
    path = asset_path(key)
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    _, _, coll_name = ASSETS[key]
    with bpy.data.libraries.load(path, link=False) as (data_from, data_to):
        data_to.collections = [coll_name]
    src = data_to.collections[0]
    if src is None:
        raise RuntimeError("No se pudo importar " + path)
    objs = [o for o in src.all_objects if o.type == "MESH" and not o.name.startswith("wdg_")]

    # Algunos assets de Poly Haven traen una armadura para abrir puertas.
    # Se hornea la pose de reposo para convertir el asset en geometría estática.
    if src.name not in SCENE.collection.children:
        SCENE.collection.children.link(src)
    old_frame = SCENE.frame_current
    SCENE.frame_set(1)
    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get()
    for o in objs:
        if not any(m.type == "ARMATURE" for m in o.modifiers):
            continue
        eval_obj = o.evaluated_get(deps)
        baked = bpy.data.meshes.new_from_object(
            eval_obj, preserve_all_data_layers=True, depsgraph=deps
        )
        old_mesh = o.data
        o.data = baked
        o.modifiers.clear()
        if old_mesh.users == 0:
            bpy.data.meshes.remove(old_mesh)
    SCENE.frame_set(old_frame)
    bpy.context.view_layer.update()

    for o in objs:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        COLL.objects.link(o)
        o.name = PREFIX + label + "_" + o.name
    for c in list(src.children_recursive):
        try:
            bpy.data.collections.remove(c)
        except Exception:
            pass
    try:
        bpy.data.collections.remove(src)
    except Exception:
        pass
    for o in objs:
        o["asset_source"] = path
        o["asset_license"] = "Poly Haven - verificar licencia antes de distribuir"
    return path, objs


def world_bbox(objs):
    mn = Vector((1e9, 1e9, 1e9))
    mx = Vector((-1e9, -1e9, -1e9))
    for o in objs:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            mn.x = min(mn.x, w.x)
            mn.y = min(mn.y, w.y)
            mn.z = min(mn.z, w.z)
            mx.x = max(mx.x, w.x)
            mx.y = max(mx.y, w.y)
            mx.z = max(mx.z, w.z)
    return mn, mx


def place_asset(key, label, location, rot_z=0.0, base_z=FLOOR, center_z=None):
    path, objs = import_asset(key, label)
    if not objs:
        raise RuntimeError("Asset sin mallas: " + label)
    bpy.context.view_layer.update()
    mn, mx = world_bbox(objs)
    center = (mn + mx) * 0.5
    empty = bpy.data.objects.new(PREFIX + label + "_ROOT", None)
    COLL.objects.link(empty)
    empty.empty_display_type = "PLAIN_AXES"
    empty.empty_display_size = 0.35
    empty.location = center
    empty.rotation_mode = "XYZ"
    empty.rotation_euler = (0.0, 0.0, rot_z)
    for o in objs:
        o.parent = empty
        o.matrix_parent_inverse = empty.matrix_world.inverted()
    bpy.context.view_layer.update()
    empty.location.x = location[0]
    empty.location.y = location[1]
    bpy.context.view_layer.update()
    mn, mx = world_bbox(objs)
    if center_z is None:
        empty.location.z += base_z - mn.z
    else:
        empty.location.z += center_z - (mn.z + mx.z) * 0.5
    bpy.context.view_layer.update()
    mn, mx = world_bbox(objs)
    empty["asset_source"] = path
    empty["asset_license"] = "Poly Haven - verificar licencia antes de distribuir"
    empty["placement"] = "V05 almacén / mantenimiento"
    print("ASSET", label, "objects", len(objs), "min", tuple(round(v, 3) for v in mn), "max", tuple(round(v, 3) for v in mx))
    return empty, objs, mn, mx


# --- ALMACÉN: zona de carga este, sin bloquear la puerta de personas ---
cart_wh, _, _, _ = place_asset("cart", "STORE_CART", (2.15, -2.65), rot_z=math.radians(90))
# Crate sobre la plataforma superior del carro (el carro mide 1.38 m de alto).
place_asset("crate", "STORE_CART_CRATE", (2.15, -2.95), base_z=FLOOR + 1.38)
place_asset("box", "STORE_FLOOR_BOX", (2.95, -8.20), rot_z=math.radians(-16))
place_asset("barrel", "STORE_BARREL", (3.35, -2.58), rot_z=math.radians(11))

# --- MANTENIMIENTO: banco, carro, luminaria, cuadro y extintor ---
place_asset("toolbox", "MAINT_BENCH_TOOLBOX", (6.55, -6.55), rot_z=math.radians(90), base_z=-4.75)
place_asset("cart", "MAINT_CART", (8.90, -7.15), rot_z=0.0)
caged, _, _, _ = place_asset("caged", "MAINT_CAGED_LIGHT", (9.50, -5.00), center_z=-1.90)
place_asset("power", "MAINT_POWER_BOX", (9.00, -9.55), rot_z=math.pi, center_z=-3.40)
place_asset("ext", "MAINT_EXTINGUISHER", (10.00, -9.05), rot_z=math.radians(6))

# Cable de la luminaria: del techo (-0.92) al punto superior de la jaula (-1.55).
cord_mat = bpy.data.materials.get("NEXUS_Dark_Metal") or bpy.data.materials.get("NEXUS_Steel")
bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.012, depth=0.63, location=(9.50, -5.00, -1.235))
cord = bpy.context.active_object
cord.name = PREFIX + "MAINT_CAGED_LIGHT_CORD"
for c in list(cord.users_collection):
    c.objects.unlink(cord)
COLL.objects.link(cord)
if cord_mat:
    cord.data.materials.append(cord_mat)

# Luz práctica de la luminaria de jaula.
light_data = bpy.data.lights.new(PREFIX + "MAINT_CAGED_LIGHT_LAMP", "POINT")
light_data.energy = 55.0
light_data.color = (1.0, 0.72, 0.42)
light_data.shadow_soft_size = 0.16
light_obj = bpy.data.objects.new(PREFIX + "MAINT_CAGED_LIGHT_LAMP", light_data)
COLL.objects.link(light_obj)
light_obj.location = (9.50, -5.00, -2.20)

# Cámara activa segura antes de guardar.
cam = bpy.data.objects.get("NEXUS_V05_CAM_Corridor")
if cam:
    SCENE.camera = cam

print("TOTAL_OBJECTS", len(bpy.data.objects))
print("ASSET_COLLECTION_OBJECTS", len(COLL.objects))
print("SAVING", OUT)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("SAVED", bpy.data.filepath)
