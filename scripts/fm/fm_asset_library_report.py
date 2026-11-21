import bpy
import json
import os

ROOT = "/home/riyo/Documentos/game"
FILE = bpy.data.filepath
IS_LIB = "fm_shared_hero_library" in FILE
OUT = os.path.join(ROOT, "docs/FM_ASSET_LIBRARY_FILE_REPORT.json" if IS_LIB else "docs/FM_ASSET_LIBRARY_MAIN_REPORT.json")


def coll_report(col):
    objs = [o for o in col.all_objects if o is not None]
    meshes = [o for o in objs if o.type == 'MESH']
    return {
        "objects": len(objs),
        "meshes": len(meshes),
        "tris": sum(len(o.data.polygons) * 2 for o in meshes),
        "children": sorted(c.name for c in col.children),
    }


root = bpy.data.collections.get("FM_LIBRARY")
report = {
    "file": FILE,
    "scenes": [s.name for s in bpy.data.scenes],
    "active_scene": bpy.context.scene.name if bpy.context.scene else None,
    "has_fm_library": root is not None,
    "level_shared_objects": [],
    "source_security": {},
    "library": coll_report(root) if root else None,
    "groups": {},
    "all_mesh_tris": sum(len(o.data.polygons) * 2 for o in bpy.data.objects if o.type == 'MESH'),
}
if root:
    for child in root.children:
        report["groups"][child.name] = coll_report(child)
        for sub in child.children:
            report["groups"][sub.name] = coll_report(sub)

level = bpy.data.scenes.get("NEXUS_L1_V06_ARCH")
if level:
    shared = bpy.data.collections.get("L1_SHARED_HERO")
    if shared:
        names = {o.name for o in shared.all_objects if o is not None}
        report["level_shared_objects"] = [o.name for o in level.objects if o.name in names]
    for src_name in ("L1_SECURITY_R2_HERO", "L1_SECURITY_R21A_HERO",
                     "L1_SECURITY_R21C_HERO_LOCKERS", "L1_SECURITY_R21D_HERO_CHAOS"):
        src = bpy.data.collections.get(src_name)
        if src:
            report["source_security"][src_name] = coll_report(src)

with open(OUT, "w") as fh:
    json.dump(report, fh, indent=2)
print("LIBRARY_REPORT", OUT)
print(json.dumps({k: report[k] for k in ("file", "scenes", "library", "groups")}, indent=2))
