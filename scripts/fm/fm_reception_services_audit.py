import bpy
import json
from mathutils import Vector

OUT = "/tmp/opencode/reception_services_audit.json"
X0, X1 = -112.0, -68.0
Y0, Y1 = -42.0, -6.0
Z0, Z1 = -0.8, 6.0
sc = bpy.data.scenes["NEXUS_L1_V06_ARCH"]


def bb(ob):
    pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    return [[round(min(p[i] for p in pts), 3) for i in range(3)],
            [round(max(p[i] for p in pts), 3) for i in range(3)]]


def in_region(ob):
    b = bb(ob)
    return not (b[1][0] < X0 or b[0][0] > X1 or b[1][1] < Y0 or b[0][1] > Y1 or b[1][2] < Z0 or b[0][2] > Z1)


def tris(ob):
    if ob.type != 'MESH':
        return 0
    return sum(max(0, len(p.vertices) - 2) for p in ob.data.polygons)


rows = []
for ob in sc.objects:
    if ob is None or not in_region(ob):
        continue
    mats = [m.name for m in ob.data.materials if m] if ob.type == 'MESH' else []
    rows.append({
        "name": ob.name,
        "type": ob.type,
        "tris": tris(ob),
        "dims": [round(v, 3) for v in ob.dimensions],
        "loc": [round(v, 3) for v in ob.matrix_world.translation],
        "bbox": bb(ob),
        "cols": sorted(c.name for c in ob.users_collection),
        "mats": mats,
        "hide": bool(ob.hide_render),
    })

service_keys = ("hvac", "duct", "tray", "sprinkler", "conduit", "pipe", "sleeve", "flange", "vent", "diffuser", "grille", "damper", "light", "lamp", "emergency", "exit")
services = [r for r in rows if any(k in r["name"].lower() for k in service_keys)]
arch = [r for r in rows if any(k in r["name"].lower() for k in ("ceiling", "soffit", "beam", "column", "wall", "floor", "slab"))]
report = {
    "region": [X0, X1, Y0, Y1, Z0, Z1],
    "objects": len(rows),
    "by_collection": {},
    "services": services,
    "architecture": arch,
    "all": rows,
}
for r in rows:
    for c in r["cols"]:
        report["by_collection"][c] = report["by_collection"].get(c, 0) + 1
with open(OUT, "w") as fh:
    json.dump(report, fh, indent=2)
print("REC_SVC_AUDIT", OUT, "objects", len(rows))
print("COLLECTIONS", json.dumps(report["by_collection"], indent=2))
print("SERVICES")
for r in sorted(services, key=lambda x: x["name"]):
    print(r["name"], r["type"], r["tris"], "dims", r["dims"], "loc", r["loc"], "bbox", r["bbox"], "cols", r["cols"])
print("ARCH")
for r in sorted(arch, key=lambda x: x["name"]):
    print(r["name"], r["type"], r["tris"], "dims", r["dims"], "loc", r["loc"], "bbox", r["bbox"])
