"""Clean redundant Level 2 threshold plates and trim the junction cover."""
import bpy
import os

ROOT = "/home/riyo/Documentos/game"
SCENE = bpy.context.scene

removed = []
for o in list(bpy.data.objects):
    if o.name.startswith("NEXUS_FIX_CONN_"):
        removed.append(o.name)
        bpy.data.objects.remove(o, do_unlink=True)

junction = bpy.data.objects.get("NEXUS_FIX_JUNCTION")
if junction:
    # Cover only the central T-junction gap between the main corridor and east/west wings.
    junction.location = (0.0, 12.875, -13.66)
    junction.dimensions = (3.5, 1.75, 0.04)
    junction.scale = (1.0, 1.0, 1.0)

# Keep actual gap patches; do not touch room floors.
path = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V05_level1_v20.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
print("L2_CLEANED", len(removed), "removed")
print("SAVED", path, os.path.getsize(path))
