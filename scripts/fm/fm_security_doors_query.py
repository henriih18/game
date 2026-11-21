import bpy
import json
from mathutils import Vector

sc = bpy.data.scenes["NEXUS_L1_V06_ARCH"]
names = []
for ob in sc.objects:
    if ob is None:
        continue
    n = ob.name
    if n.startswith("SM_L1_Zone03_Security_Door_") or ("Security" in n and ("Door" in n or "Reader" in n or "Access" in n)):
        names.append(ob)

out = []
for ob in sorted(names, key=lambda o: o.name):
    pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    out.append({
        "name": ob.name,
        "type": ob.type,
        "tris": sum(len(p.vertices) - 2 for p in ob.data.polygons) if ob.type == 'MESH' else 0,
        "dims": [round(v, 3) for v in ob.dimensions],
        "bbox": [[round(min(p[i] for p in pts), 3) for i in range(3)],
                 [round(max(p[i] for p in pts), 3) for i in range(3)]],
        "loc": [round(v, 3) for v in ob.matrix_world.translation],
        "collections": sorted(c.name for c in ob.users_collection),
        "hide_render": bool(ob.hide_render),
    })
print(json.dumps(out, indent=2))
