import bpy
import json
from mathutils import Vector

names = ["P0B_TRAY_RUN_400", "P0B_SUPPORTS_TRAY", "SM_SH_TRAY_400_L2000", "SM_SH_SUPPORT_TRAY_400"]
for n in names:
    ob = bpy.data.objects.get(n)
    if not ob:
        print("MISSING", n)
        continue
    pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    mn = [round(min(p[i] for p in pts), 4) for i in range(3)]
    mx = [round(max(p[i] for p in pts), 4) for i in range(3)]
    mats = sorted({s.material.name for s in ob.material_slots if s.material}) if ob.type == 'MESH' else []
    print("OBJ", n, "tris", len(ob.data.polygons) * 2 if ob.type == 'MESH' else 0, "loc", [round(v, 3) for v in ob.matrix_world.translation], "bbox", mn, mx, "dims", [round(v, 4) for v in ob.dimensions], "mats", mats, "colls", [c.name for c in ob.users_collection])
