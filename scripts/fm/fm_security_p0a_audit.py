import bpy
import json
import os
from mathutils import Vector

OUT = "/tmp/opencode/security_audit.json"
X0, X1 = -106.0, -70.0
Y0, Y1 = 9.0, 37.0
Z0, Z1 = -0.6, 5.6

sc = bpy.data.scenes["NEXUS_L1_V06_ARCH"]


def dims(ob):
    try:
        return [round(v, 3) for v in ob.dimensions]
    except Exception:
        return [0, 0, 0]


def bbox(ob):
    try:
        pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
        return [[round(min(p[i] for p in pts), 3) for i in range(3)],
                [round(max(p[i] for p in pts), 3) for i in range(3)]]
    except Exception:
        return [[0, 0, 0], [0, 0, 0]]


def in_region(ob):
    try:
        p = ob.matrix_world.translation
        return X0 <= p.x <= X1 and Y0 <= p.y <= Y1 and Z0 <= p.z <= Z1
    except Exception:
        return False


objs = [o for o in sc.objects if o is not None and in_region(o)]
rows = []
for ob in objs:
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons) if ob.type == 'MESH' else 0
    rows.append({
        "name": ob.name,
        "type": ob.type,
        "tris": tris,
        "dims": dims(ob),
        "loc": [round(v, 3) for v in ob.matrix_world.translation],
        "bbox": bbox(ob),
        "collections": sorted(c.name for c in ob.users_collection),
        "hide_render": bool(ob.hide_render),
        "hide_viewport": bool(ob.hide_viewport),
    })

rows.sort(key=lambda r: (r["type"], -r["tris"], r["name"]))
lib = bpy.data.collections.get("FM_LIBRARY")
lib_tree = {}
if lib:
    for col in lib.children:
        lib_tree[col.name] = {
            "objects": len(col.all_objects),
            "children": sorted(c.name for c in col.children),
        }

report = {
    "scene": sc.name,
    "region": [X0, X1, Y0, Y1, Z0, Z1],
    "object_count": len(rows),
    "by_type": {},
    "lights": [r for r in rows if r["type"] == 'LIGHT'],
    "doors": [r for r in rows if any(k in r["name"].lower() for k in ("door", "portal", "gate"))],
    "services": [r for r in rows if any(k in r["name"].lower() for k in ("hvac", "duct", "tray", "sprinkler", "conduit", "pipe", "sleeve", "flange", "vent", "diffuser", "grille", "damper", "riser"))],
    "emergency": [r for r in rows if any(k in r["name"].lower() for k in ("emergency", "luminaire", "light"))],
    "library": lib_tree,
    "all": rows,
}
for r in rows:
    report["by_type"][r["type"]] = report["by_type"].get(r["type"], 0) + 1
with open(OUT, "w") as fh:
    json.dump(report, fh, indent=2)
print("SEC_AUDIT", OUT, "objects", len(rows))
print("BY_TYPE", report["by_type"])
print("LIGHTS", [(r["name"], r["tris"], r["loc"]) for r in report["lights"]])
print("DOORS", [(r["name"], r["tris"], r["loc"], r["dims"]) for r in report["doors"]])
print("EMERGENCY", [(r["name"], r["tris"], r["loc"], r["dims"]) for r in report["emergency"]])
print("SERVICES", [(r["name"], r["tris"], r["loc"], r["dims"]) for r in report["services"]])
print("LIB", json.dumps(lib_tree, indent=2))
