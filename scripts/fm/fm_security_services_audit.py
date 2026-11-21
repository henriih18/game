import bpy
import json
from mathutils import Vector

OUT = "/tmp/opencode/security_services_audit.json"
X0, X1 = -106.0, -70.0
Y0, Y1 = 9.0, 37.0
Z0, Z1 = 2.5, 5.5

sc = bpy.data.scenes["NEXUS_L1_V06_ARCH"]
keys = ("hvac", "duct", "tray", "sprinkler", "conduit", "pipe", "vent", "grille", "diffuser", "flange", "damper", "riser", "support", "hanger")

rows = []
for ob in sc.objects:
    if ob is None or ob.type != 'MESH':
        continue
    p = ob.matrix_world.translation
    if not (X0 <= p.x <= X1 and Y0 <= p.y <= Y1 and Z0 <= p.z <= Z1):
        continue
    if not any(k in ob.name.lower() for k in keys):
        continue
    pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    bmin = [round(min(q[i] for q in pts), 3) for i in range(3)]
    bmax = [round(max(q[i] for q in pts), 3) for i in range(3)]
    rows.append({
        "name": ob.name,
        "tris": sum(len(p.vertices) - 2 for p in ob.data.polygons),
        "dims": [round(v, 3) for v in ob.dimensions],
        "loc": [round(v, 3) for v in p],
        "bbox": [bmin, bmax],
        "collections": sorted(c.name for c in ob.users_collection),
        "hide_render": bool(ob.hide_render),
    })

rows.sort(key=lambda r: (r["bbox"][0][2], r["name"]))
with open(OUT, "w") as fh:
    json.dump(rows, fh, indent=2)
print("SEC_SERVICES", len(rows), OUT)
for r in rows:
    print(f'{r["name"]:42s} tris={r["tris"]:6d} dims={r["dims"]} loc={r["loc"]} bbox={r["bbox"]} col={r["collections"]}')
