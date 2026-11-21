import bpy
import glob
import math
import os
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
ASSET_ROOT = os.path.join(ROOT, "assets", "Modelos 3D")
OUT = os.path.join(ROOT, "FM_NEXUS_V05_level1_v117.blend")
PREFIX = "NEXUS_ASSET_L1_"
COLL_NAME = "NEXUS_ASSET_L1"
FLOOR = -5.65
SCENE = bpy.context.scene

INDEX = {}
for p in glob.glob(os.path.join(ASSET_ROOT, "*", "*.blend", "*.blend")):
    INDEX[os.path.splitext(os.path.basename(p))[0].lower()] = p

# ---------------------------------------------------------------- cleanup
for c in list(bpy.data.collections):
    if c.name == COLL_NAME or c.name.startswith(PREFIX):
        for o in list(c.all_objects):
            if o.name in bpy.data.objects:
                bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.collections.remove(c)
for o in list(bpy.data.objects):
    if o.name.startswith(PREFIX):
        bpy.data.objects.remove(o, do_unlink=True)

coll = bpy.data.collections.get(COLL_NAME)
if coll is None:
    coll = bpy.data.collections.new(COLL_NAME)
    SCENE.collection.children.link(coll)

SOURCES = {}

# ---------------------------------------------------------------- helpers
def load_sources(key):
    if key.lower() in SOURCES:
        return SOURCES[key.lower()]
    path = INDEX.get(key.lower())
    if not path:
        raise RuntimeError("Asset not found: " + key)
    with bpy.data.libraries.load(path, link=False) as (data_from, data_to):
        data_to.collections = list(data_from.collections)
    loaded = [c for c in data_to.collections if c is not None]
    objs = []
    for c in loaded:
        for o in list(c.all_objects):
            if o.name not in coll.objects:
                coll.objects.link(o)
            objs.append(o)
        bpy.data.collections.remove(c)
    bpy.context.view_layer.update()
    SOURCES[key.lower()] = objs
    return objs

def bbox(objs):
    pts = []
    for o in objs:
        if o.type == 'MESH':
            for corner in o.bound_box:
                pts.append(o.matrix_world @ Vector(corner))
    if not pts:
        return None
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return mn, mx

def place(key, name, x, y, z, rot_z=0.0, anchor="bottom"):
    src = load_sources(key)
    root = bpy.data.objects.new(PREFIX + name + "_ROOT", None)
    coll.objects.link(root)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.12
    inst = []
    for s in src:
        d = s.copy()
        if s.data is not None:
            d.data = s.data
        coll.objects.link(d)
        d.parent = root
        d.matrix_parent_inverse = root.matrix_world.inverted()
        d.matrix_world = s.matrix_world.copy()
        d.name = PREFIX + name + "_" + s.name
        inst.append(d)
    bpy.context.view_layer.update()
    bb = bbox(inst)
    if bb is None:
        raise RuntimeError("Empty asset: " + key)
    mn, mx = bb
    cx = (mn.x + mx.x) * 0.5
    cy = (mn.y + mx.y) * 0.5
    root.location.x -= cx
    root.location.y -= cy
    root.location.z -= mn.z
    bpy.context.view_layer.update()
    root.rotation_mode = 'XYZ'
    root.rotation_euler[2] = rot_z
    if anchor == "center":
        root.location = (x, y, z - (mx.z - mn.z) * 0.5)
    else:
        root.location = (x, y, z)
    bpy.context.view_layer.update()
    for o in [root] + inst:
        o["asset_source"] = key
        o["asset_license"] = "Poly Haven - verificar licencia antes de distribuir"
        o["placement"] = "V05 nivel 1"
    return root

def hide(prefixes, by):
    for o in bpy.data.objects:
        if o.type != 'MESH':
            continue
        if any(o.name.startswith(p) for p in prefixes):
            o.hide_render = True
            o.hide_viewport = True
            o["replaced_by"] = by

def camera(name, loc, target, lens):
    data = bpy.data.cameras.get(name)
    if data is None:
        data = bpy.data.cameras.new(name)
    ob = bpy.data.objects.get(name)
    if ob is None:
        ob = bpy.data.objects.new(name, data)
        SCENE.collection.objects.link(ob)
    else:
        ob.data = data
    ob.location = loc
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    data.lens = lens
    return ob

# ---------------------------------------------------------------- replacements
hide([
    "NEXUS_V05_REC_WAIT_0_", "NEXUS_V05_REC_WAIT_1_", "NEXUS_V05_REC_WAIT_2_",
    "NEXUS_V05_REC_OFFICE_CHAIR_", "NEXUS_V05_REC_COFFEE_",
    "NEXUS_V05_SEC_CHAIR_A_", "NEXUS_V05_SEC_CHAIR_B_",
    "NEXUS_V05_ACC_CHAIR_A_", "NEXUS_V05_ACC_CHAIR_B_",
    "NEXUS_V05_OFFICE_DESK_TOP", "NEXUS_V05_OFFICE_DESK_LEG_",
    "NEXUS_V05_OFFICE_CHAIR_",
    "NEXUS_V05_B_STORE_BARREL_0", "NEXUS_V05_B_STORE_BARREL_1",
    "NEXUS_V05_B_STORE_BARREL_2", "NEXUS_V05_B_STORE_PALLET_1_CRATE_",
], "asset local Nivel 1")

# Reception
place("CoffeeCart_01_4k", "REC_COFFEE_CART", -17.25, 8.20, FLOOR, math.radians(90))
for i, yy in enumerate((6.95, 8.15, 9.35)):
    place("SchoolChair_01_2k", "REC_WAIT_CHAIR_%d" % i, -18.75, yy, FLOOR, math.radians(90))
place("SchoolChair_01_2k", "REC_DESK_CHAIR", -12.00, 9.15, FLOOR, 0.0)
place("wall_clock_1k", "REC_CLOCK", -17.00, 11.4715, -3.20, 0.0, "center")
place("vintage_stapler_2k", "REC_STAPLER", -10.55, 7.50, -4.927, 0.0)
place("clipboard_1k", "REC_CLIPBOARD", -10.80, 7.65, -4.94, 0.0)

# Security
for i, xx in enumerate((2.10, 3.95)):
    place("SchoolChair_01_2k", "SEC_CHAIR_%d" % i, xx, 4.85, FLOOR, math.radians(180))

# Access control
for i, xx in enumerate((11.90, 14.10)):
    place("SchoolChair_01_2k", "ACC_CHAIR_%d" % i, xx, 7.05, FLOOR, math.radians(180))

# Office
place("metal_office_desk_2k", "OFFICE_DESK", -6.20, 7.10, FLOOR, 0.0)
place("SchoolChair_01_2k", "OFFICE_CHAIR", -6.20, 6.35, FLOOR, math.radians(180))
place("classic_laptop_2k", "OFFICE_LAPTOP", -5.55, 7.15, -4.862, 0.0)
place("clipboard_1k", "OFFICE_CLIPBOARD", -7.00, 7.35, -4.862, 0.0)
place("wall_clock_1k", "OFFICE_CLOCK", -6.20, 7.6115, -3.20, 0.0, "center")

for n in ("NEXUS_V05_OFFICE_KEYBOARD", "NEXUS_V05_OFFICE_MONITOR",
          "NEXUS_V05_OFFICE_MONITOR_STAND", "NEXUS_V05_OFFICE_PHONE",
          "NEXUS_V05_OFFICE_PAPERS"):
    o = bpy.data.objects.get(n)
    if o is not None and not o.get("l1_raised"):
        o.location.z += 0.15
        o["l1_raised"] = True

# Restroom
place("WetFloorSign_01_1k", "REST_WET_SIGN", -6.40, 2.35, FLOOR, 0.0)
place("cleaner_tin_01_1k", "REST_CLEANER_TIN", -7.95, 2.15, FLOOR, 0.0)

# Vestuary
place("garden_gloves_01_1k", "VEST_GLOVES", -18.30, -6.00, -5.30, 0.0)
place("fishermans_hat_1k", "VEST_HAT", -18.30, -5.60, -5.266, 0.0)
place("trashbag_1k", "VEST_TRASHBAG", -10.20, -3.60, FLOOR, 0.0)
place("WetFloorSign_01_1k", "VEST_WET_SIGN", -13.20, -7.20, FLOOR, 0.0)

# Store
for i, (xx, yy) in enumerate(((-6.90, -3.05), (-6.15, -3.05), (-6.55, -2.38))):
    place("Barrel_03_2k", "STORE_BARREL_%d" % i, xx, yy, FLOOR, 0.0)
place("wooden_crate_02_2k", "STORE_PALLET_CRATE", 0.90, -3.80, -5.495, 0.0)
place("industrial_pastic_container_2k", "STORE_CONTAINER_A", 1.70, -8.30, FLOOR, 0.0)
place("plastic_container_1k", "STORE_CONTAINER_B", 2.40, -7.55, FLOOR, 0.0)

# Maintenance
place("tool_cart_2k", "MAINT_TOOL_CART", 10.20, -5.00, FLOOR, 0.0)
place("fire_alarm_2k", "MAINT_FIRE_ALARM", 8.00, -1.6815, -3.20, 0.0, "center")

# Corridor
for i, xx in enumerate((-16.0, -6.0, 6.0, 16.0)):
    place("industrial_wall_lamp_1k", "CORR_WALL_LAMP_%d" % i, xx, -1.625, -2.90, math.radians(180), "center")
place("fire_alarm_2k", "CORR_FIRE_ALARM", -11.00, 1.6815, -3.20, 0.0, "center")
place("WetFloorSign_01_1k", "CORR_WET_SIGN", -13.00, -0.80, FLOOR, 0.0)

# ---------------------------------------------------------------- source cleanup
for key, objs in SOURCES.items():
    for o in list(objs):
        if o.name in bpy.data.objects:
            bpy.data.objects.remove(o, do_unlink=True)

# ---------------------------------------------------------------- cameras
camera("NEXUS_V05_CAM_Recepcion", (-8.30, 3.20, -4.25), (-14.20, 8.20, -4.35), 20)
camera("NEXUS_V05_CAM_Rest", (-7.95, 4.32, -4.05), (-4.95, 2.65, -4.35), 18)
camera("NEXUS_V05_CAM_Corridor", (-20.50, 0.00, -4.15), (0.00, 0.00, -4.15), 20)

SCENE.camera = bpy.data.objects.get("NEXUS_V05_CAM_Corridor")

# ---------------------------------------------------------------- report
roots = [o for o in coll.objects if o.type == 'EMPTY' and o.name.startswith(PREFIX)]
meshes = [o for o in coll.all_objects if o.type == 'MESH']
print("L1_ASSET_ROOTS", len(roots))
print("L1_ASSET_MESHES", len(meshes))
print("L1_ASSET_COLLECTION", coll.name, len(coll.all_objects))
print("L1_ASSET_TOTAL_OBJECTS", len(bpy.data.objects))
print("L1_SAVED", OUT)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
