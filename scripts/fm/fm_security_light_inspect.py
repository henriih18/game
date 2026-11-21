import bpy
import json
from mathutils import Vector

LIB = bpy.data.collections.get("LIB_CORRIDOR_HERO")
OUT = "/tmp/opencode/security_light_inspect.json"


def wbox(ob):
    pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    return [[round(min(p[i] for p in pts), 3) for i in range(3)],
            [round(max(p[i] for p in pts), 3) for i in range(3)]]


def info(ob):
    return {
        "name": ob.name,
        "type": ob.type,
        "tris": sum(len(p.vertices) - 2 for p in ob.data.polygons) if ob.type == 'MESH' else 0,
        "loc": [round(v, 3) for v in ob.matrix_world.translation],
        "dims": [round(v, 3) for v in ob.dimensions],
        "bbox": wbox(ob),
        "parent": ob.parent.name if ob.parent else None,
        "collections": sorted(c.name for c in ob.users_collection),
        "materials": [m.name for m in ob.data.materials] if ob.type == 'MESH' else [],
        "hide_render": bool(ob.hide_render),
    }


def find(names):
    return [bpy.data.objects[n] for n in names if n in bpy.data.objects]


lib_names = []
if LIB:
    for col in LIB.all_objects:
        pass
    for ob in LIB.all_objects:
        if ob and ob.type == 'MESH' and (ob.name.startswith("SM_SH_LUMINAIRE") or ob.name.startswith("SM_SH_EMERGENCY")):
            lib_names.append(ob.name)

old_names = [f"KIT_SEC01_CeilingLightHousing_{i}" for i in range(7)]
old_names += [f"DET_SEC01_CeilingLightPanel_{i}" for i in range(7)]
old_names += ["R21B_SERV_EmergencyS", "R21B_SERV_EmergencyW1", "R21B_SERV_EmergencyW2",
              "R21A_FIX_Emergency_E", "R21A_FIX_Emergency_N", "R21D_FIX_Emergency_Checkpoint"]
old_names += ["R21B_LIGHT_Emergency_1", "R21D_LIGHT_Emergency_Checkpoint", "R21D_LIGHT_ExitCold",
              "R21A_LIGHT_Emergency_E", "R21A_LIGHT_Emergency_N"]

report = {
    "library_masters": [info(bpy.data.objects[n]) for n in sorted(set(lib_names))],
    "old": [info(o) for o in find(old_names)],
    "lights": [info(o) for o in bpy.data.objects if o.type == 'LIGHT' and -106 <= o.matrix_world.translation.x <= -70 and 9 <= o.matrix_world.translation.y <= 37],
}
with open(OUT, "w") as fh:
    json.dump(report, fh, indent=2)
print("SEC_LIGHT_INSPECT", OUT)
print("LIB", json.dumps([{k: r[k] for k in ("name", "loc", "dims", "bbox", "parent", "materials")} for r in report["library_masters"]], indent=2))
print("OLD", json.dumps([{k: r[k] for k in ("name", "loc", "dims", "bbox", "parent", "collections", "materials")} for r in report["old"]], indent=2))
print("LIGHTS", json.dumps([{k: r[k] for k in ("name", "loc", "dims")} for r in report["lights"]], indent=2))
