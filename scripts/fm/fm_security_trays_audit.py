import bpy
import json
import os
from mathutils import Vector

OUT = "/tmp/opencode/security_trays_audit.json"
NAMES = [
    "R21B_SERV_WestCableTray",
    "R21B_SERV_CentreCableTray",
    "R21A_CCTV_CableTray",
    "R21B_SERV_VentS",
    "R21B_SERV_VentE",
    "R21B_SERV_VentW",
]
sc = bpy.data.scenes["NEXUS_L1_V06_ARCH"]


def bbox(ob):
    pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    return [[round(min(p[i] for p in pts), 4) for i in range(3)],
            [round(max(p[i] for p in pts), 4) for i in range(3)]]


def info(ob):
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons) if ob.type == 'MESH' else 0
    mats = []
    if ob.type == 'MESH':
        mats = sorted({s.material.name for s in ob.material_slots if s.material})
    return {
        "name": ob.name,
        "type": ob.type,
        "tris": tris,
        "verts": len(ob.data.vertices) if ob.type == 'MESH' else 0,
        "dims": [round(v, 4) for v in ob.dimensions],
        "loc": [round(v, 4) for v in ob.matrix_world.translation],
        "bbox": bbox(ob),
        "rot": [round(v, 4) for v in ob.rotation_euler],
        "collections": sorted(c.name for c in ob.users_collection),
        "materials": mats,
        "hide_render": bool(ob.hide_render),
    }


rows = []
for n in NAMES:
    ob = bpy.data.objects.get(n)
    if ob is None:
        rows.append({"name": n, "missing": True})
    else:
        rows.append(info(ob))

# Library tray/support masters.
lib = bpy.data.collections.get("FM_LIBRARY")
lib_rows = []
if lib:
    for ob in lib.all_objects:
        if ob and ob.type == 'MESH' and ("TRAY" in ob.name.upper() or "SUPPORT" in ob.name.upper()):
            lib_rows.append(info(ob))

# Objects near tray paths for wall/ceiling context.
paths = []
for r in rows:
    if r.get("missing"):
        continue
    mn, mx = r["bbox"]
    paths.append((r["name"], mn, mx))

near = []
for ob in sc.objects:
    if ob is None or ob.type != 'MESH':
        continue
    try:
        p = ob.matrix_world.translation
    except Exception:
        continue
    for name, mn, mx in paths:
        if mn[0] - 1.0 <= p.x <= mx[0] + 1.0 and mn[1] - 1.0 <= p.y <= mx[1] + 1.0 and mn[2] - 1.0 <= p.z <= mx[2] + 1.0:
            near.append({"name": ob.name, "loc": [round(v, 3) for v in p], "tris": len(ob.data.polygons) * 2, "near": name})
            break

report = {"trays": rows, "library_masters": lib_rows, "near": near}
with open(OUT, "w") as fh:
    json.dump(report, fh, indent=2)
print("TRAY_AUDIT", OUT)
for r in rows:
    print("TRAY", json.dumps(r))
print("LIB_TRAY_COUNT", len(lib_rows))
for r in lib_rows[:20]:
    print("LIB", r["name"], r["tris"], r["dims"], r["loc"])
print("NEAR_COUNT", len(near))
for r in near[:40]:
    print("NEAR", json.dumps(r))
