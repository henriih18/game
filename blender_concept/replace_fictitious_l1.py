"""
Replace blocky/fictitious objects in NEXUS Level 1 with real asset models.

Replaces: monitors, tools, electrical panels, desk lamp, cooler bottle.
Originals are hidden (not deleted) with replaced_by tag.
Output: FM_NEXUS_V05_level1_v125.blend
"""
import bpy
import math
import os
from mathutils import Vector, Euler

ROOT = "/home/riyo/Documentos/game"
OUT = ROOT + "/FM_NEXUS_V05_level1_v125.blend"
ASSETS = os.path.join(ROOT, "assets", "Modelos 3D")
SCENE = bpy.context.scene
PREFIX = "NEXUS_ASSET_L1R_"
COLL_NAME = "NEXUS_ASSET_L1_REPLACE"
FLOOR = -5.65

# ── cleanup previous run ──────────────────────────────────────────────
for ob in list(bpy.data.objects):
    if ob.name.startswith(PREFIX):
        bpy.data.objects.remove(ob, do_unlink=True)
old_coll = bpy.data.collections.get(COLL_NAME)
if old_coll:
    bpy.data.collections.remove(old_coll)
coll = bpy.data.collections.new(COLL_NAME)
SCENE.collection.children.link(coll)

# ── asset loading cache ───────────────────────────────────────────────
_cache = {}

def load_collection(key, category):
    if key in _cache:
        return _cache[key]
    path = os.path.join(ASSETS, category, key + ".blend", key + ".blend")
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        dst.collections = [src.collections[0]]
    col = dst.collections[0]
    _cache[key] = col
    return col

def place_asset(key, category, name, loc, rot=None, scale=None):
    """Import asset, center it, place at location."""
    src_col = load_collection(key, category)
    root = bpy.data.objects.new(PREFIX + name + "_ROOT", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.1
    coll.objects.link(root)
    root["asset_source"] = key
    root["asset_license"] = "Poly Haven - verificar licencia antes de distribuir"
    root["placement"] = "V05 nivel 1 - reemplazo"

    # Compute source bbox center
    src_objs = list(src_col.all_objects)
    mins = [float('inf')]*3
    maxs = [float('-inf')]*3
    for o in src_objs:
        if o.type != 'MESH':
            continue
        for c in o.bound_box:
            v = o.matrix_world @ Vector(c)
            for i in range(3):
                mins[i] = min(mins[i], v[i])
                maxs[i] = max(maxs[i], v[i])
    center = Vector([(mins[i]+maxs[i])/2 for i in range(3)])

    # Instantiate objects
    for o in src_objs:
        new = o.copy()
        if o.data:
            new.data = o.data  # share mesh data
        new.name = PREFIX + name + "_" + o.name.split("_", 1)[-1] if "_" in o.name else PREFIX + name + "_" + o.name
        coll.objects.link(new)
        new.parent = root
        # Offset so bbox bottom-center is at origin
        new.location = o.matrix_world.translation - Vector([center.x, center.y, mins[2]])
        new.rotation_euler = o.rotation_euler

    root.location = loc
    if rot:
        root.rotation_euler = rot
    if scale:
        root.scale = scale
    return root

def hide_branch(name):
    """Hide object and all children, tag as replaced."""
    ob = bpy.data.objects.get(name)
    if not ob:
        return
    for child in [ob] + list(ob.children_recursive):
        child.hide_render = True
        child.hide_viewport = True
    ob["replaced_by"] = "NEXUS_ASSET_L1_REPLACE"

def hide_prefix(prefix):
    """Hide all objects whose name starts with prefix."""
    for ob in bpy.data.objects:
        if ob.name.startswith(prefix) and not ob.name.startswith(PREFIX):
            ob.hide_render = True
            ob.hide_viewport = True
            ob["replaced_by"] = "NEXUS_ASSET_L1_REPLACE"

# ══════════════════════════════════════════════════════════════════════
# 1. MONITORS — Television_01 for desks, television_02 for wall
# ══════════════════════════════════════════════════════════════════════
print("=== MONITORS ===", flush=True)
CAT_TV = "Objetos pequeños y narrativa ambiental"

# Office monitor — desk surface at z≈-4.85 (desk top at FLOOR+0.788)
hide_prefix("NEXUS_V05_OFFICE_MONITOR")
place_asset("Television_01_2k", CAT_TV, "OFFICE_MONITOR",
            (-6.20, 7.33, FLOOR + 0.788))

# Reception monitors — desk surface
hide_prefix("NEXUS_V05_REC_MON_A")
hide_prefix("NEXUS_V05_REC_MON_B")
place_asset("Television_01_2k", CAT_TV, "REC_MON_A",
            (-13.20, 8.01, FLOOR + 0.72))
place_asset("Television_01_2k", CAT_TV, "REC_MON_B",
            (-11.25, 8.01, FLOOR + 0.72))

# Security desk monitors — desk surface at FLOOR+0.788
for i, x in enumerate([1.80, 3.00, 4.20]):
    hide_prefix(f"NEXUS_V05_SEC_DESK_MON_{i}")
    place_asset("Television_01_2k", CAT_TV, f"SEC_DESK_MON_{i}",
                (x, 6.01, FLOOR + 0.788))

# Security wall monitors — 6 units (3 cols × 2 rows) on north wall y≈9.42
for col_i, x in enumerate([1.30, 3.00, 4.70]):
    for row_i, z in enumerate([-3.25, -4.30]):
        prefix = f"NEXUS_V05_SEC_MONWALL_{col_i}_{row_i}"
        hide_prefix(prefix)
        # Wall-mounted TV, facing south (-Y)
        place_asset("television_02_2k", CAT_TV, f"SEC_WALL_{col_i}_{row_i}",
                    (x, 9.42, z), rot=(math.pi/2, 0, 0))

# Control monitors
hide_prefix("NEXUS_V05_ACC_MON_A")
hide_prefix("NEXUS_V05_ACC_MON_B")
place_asset("Television_01_2k", CAT_TV, "ACC_MON_A",
            (12.35, 8.01, FLOOR + 0.788))
place_asset("Television_01_2k", CAT_TV, "ACC_MON_B",
            (13.65, 8.01, FLOOR + 0.788))

# Control east wall monitor — facing west (-X)
hide_prefix("NEXUS_V05_E_CTRL_MON")
place_asset("television_02_2k", CAT_TV, "CTRL_EAST_MON",
            (14.82, 6.60, -4.40), rot=(math.pi/2, 0, -math.pi/2))

print("Monitors done", flush=True)

# ══════════════════════════════════════════════════════════════════════
# 2. TOOLS — pegboard in maintenance (x≈6.2, facing east/+X)
# ══════════════════════════════════════════════════════════════════════
print("=== TOOLS ===", flush=True)
CAT_SMALL = "Objetos pequeños y narrativa ambiental"
CAT_INFRA = "Infraestructura industrial y mantenimiento"

# Hammer — replace handle+head with wooden hammer, hanging on pegboard
hide_prefix("NEXUS_V05_B_MAINT_HAMMER")
place_asset("wooden_hammer_01_2k", CAT_INFRA, "MAINT_HAMMER",
            (6.20, -7.30, -3.20), rot=(0, 0, math.pi/2))

# Screwdrivers — 3 units on pegboard
for i, y in enumerate([-6.60, -6.30, -6.00]):
    hide_prefix(f"NEXUS_V05_B_MAINT_SCREWDRIVER_{i}")
    place_asset("screwdriver_1k", CAT_SMALL, f"MAINT_SCREW_{i}",
                (6.20, y, -3.06), rot=(0, 0, math.pi/2))

# Wrench — on pegboard
hide_prefix("NEXUS_V05_B_MAINT_WRENCH")
place_asset("adjustable_wrench_1k", CAT_SMALL, "MAINT_WRENCH",
            (6.20, -8.05, -3.33), rot=(0, 0, math.pi/2))

# Toolbox — on workbench surface (FLOOR+0.90 = -4.75)
hide_prefix("NEXUS_V05_B_MAINT_TOOLBOX")
place_asset("metal_tool_chest_2k", CAT_INFRA, "MAINT_TOOLCHEST",
            (6.55, -7.80, FLOOR + 0.90))

# Additional maintenance tools on pegboard
hide_prefix("NEXUS_V05_D_MAINT_SCREWDRIVER")
hide_prefix("NEXUS_V05_D_MAINT_WRENCH")
hide_prefix("NEXUS_V05_D_MAINT_TOOLBOX")

# Pliers on pegboard (new addition near other tools)
place_asset("pliers_2k", CAT_INFRA, "MAINT_PLIERS",
            (6.20, -7.00, -3.20), rot=(0, 0, math.pi/2))

print("Tools done", flush=True)

# ══════════════════════════════════════════════════════════════════════
# 3. ELECTRICAL PANELS
# ══════════════════════════════════════════════════════════════════════
print("=== PANELS ===", flush=True)

# Corridor panel 0 — north wall, facing south (-Y)
hide_prefix("NEXUS_V05_D_CORR_PANEL_0")
place_asset("utility_box_01_2k", CAT_INFRA, "CORR_PANEL_0",
            (-8.00, 1.55, -3.40), rot=(math.pi/2, 0, 0))

# Corridor panel 1 — south wall, facing north (+Y)
hide_prefix("NEXUS_V05_D_CORR_PANEL_1")
place_asset("utility_box_01_2k", CAT_INFRA, "CORR_PANEL_1",
            (7.00, -1.55, -3.40), rot=(math.pi/2, 0, math.pi))

# Maintenance panel — large panel, facing south
hide_prefix("NEXUS_V05_MAINT_PANEL")
place_asset("utility_box_02_2k", CAT_INFRA, "MAINT_PANEL",
            (13.00, -6.85, -4.30), rot=(math.pi/2, 0, 0))

# Control panel — east wall, facing west (-X)
hide_prefix("NEXUS_V05_ACC_PANEL")
place_asset("utility_box_01_2k", CAT_INFRA, "ACC_PANEL",
            (16.55, 2.00, -3.70), rot=(math.pi/2, 0, -math.pi/2))

# Maintenance electrical cabinet — west wall, facing east (+X)
hide_prefix("NEXUS_V05_B_MAINT_CABINET")
place_asset("utility_box_02_2k", CAT_INFRA, "MAINT_CABINET",
            (6.20, -2.90, -3.90), rot=(math.pi/2, 0, math.pi/2))

print("Panels done", flush=True)

# ══════════════════════════════════════════════════════════════════════
# 4. OTHER OBJECTS
# ══════════════════════════════════════════════════════════════════════
print("=== OTHER ===", flush=True)

# Reception desk lamp → industrial pipe lamp
hide_prefix("NEXUS_V05_REC_LAMP")
place_asset("industrial_pipe_lamp_2k", CAT_INFRA, "REC_LAMP",
            (-10.10, 8.50, FLOOR + 0.72))

# Water cooler bottle → plastic gallon
hide_prefix("NEXUS_V05_C_SEC_COOLER_BOTTLE")
hide_prefix("NEXUS_V05_C_SEC_COOLER_CUP")
place_asset("plastic_bottle_gallon_2k", CAT_SMALL, "SEC_COOLER_BOTTLE",
            (7.35, 7.50, -4.43))

# Maintenance wall fan → keep as-is (it's a vent, not fictitious)
# Generator fan → keep as-is (structural part of generator)

# Clocks — already replaced in previous pass with wall_clock assets

print("Other done", flush=True)

# ══════════════════════════════════════════════════════════════════════
# SAVE
# ══════════════════════════════════════════════════════════════════════
# Clean temp objects
for ob in list(bpy.data.objects):
    if ob.name.startswith("TMP_"):
        bpy.data.objects.remove(ob, do_unlink=True)

# Set active camera
cam = bpy.data.objects.get("NEXUS_V05_CAM_Corridor")
if cam:
    SCENE.camera = cam

bpy.ops.wm.save_as_mainfile(filepath=OUT)
print(f"\nSaved: {OUT}", flush=True)

# Count results
asset_objs = [o for o in bpy.data.objects if o.name.startswith(PREFIX)]
roots = [o for o in asset_objs if o.type == 'EMPTY']
meshes = [o for o in asset_objs if o.type == 'MESH']
print(f"Replacement roots: {len(roots)}, meshes: {len(meshes)}", flush=True)
print(f"Total scene objects: {len(bpy.data.objects)}", flush=True)
