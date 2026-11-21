import bpy
from mathutils import Vector
for name in ("P0B_SPRINKLER_RUN_DN80", "P0B_SPRINKLER_HEADS", "P0B_SUPPORTS_SPRINKLER"):
    ob = bpy.data.objects.get(name)
    if not ob:
        print("MISSING", name)
        continue
    print("OBJ", name, "loc", tuple(round(v,3) for v in ob.location), "rot", tuple(round(v,3) for v in ob.rotation_euler), "dims", tuple(round(v,3) for v in ob.dimensions))
    print("  mats", [m.name if m else None for m in ob.data.materials])
    pts=[ob.matrix_world @ Vector(c) for c in ob.bound_box]
    print("  bbox", [round(min(p[i] for p in pts),3) for i in range(3)], [round(max(p[i] for p in pts),3) for i in range(3)])
print("MATS", [m.name for m in bpy.data.materials if "Sprink" in m.name or "Steel" in m.name][:20])
