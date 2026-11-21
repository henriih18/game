"""Bind the new Level 1 reception collections into the linked level collection.

The master file links only NEXUS_L1_V05 from the level file. Collections created
outside that root never reach the master, even though they are saved in L1.
This pass moves the reception collections under the level root without changing
any object transform or deleting data, then saves a new version.

Run:
  blender -b nexus/nivel_01/NEXUS_L1_V05.blend --python blender_concept/bind_l1_collections_v130.py
"""

import os

import bpy

ROOT = "/home/riyo/Documentos/game"
SOURCE = os.path.join(ROOT, "nexus/nivel_01/NEXUS_L1_V05.blend")
OUT = os.path.join(ROOT, "nexus/nivel_01/NEXUS_L1_V05_recepcion_v130.blend")
ROOT_COLLECTION = "NEXUS_L1_V05"
MOVE = ("NEXUS_V05_REC_PASS126", "NEXUS_V05_REC_LOD1", "NEXUS_V05_REC_PLAY")

scene = bpy.context.scene
level_root = bpy.data.collections.get(ROOT_COLLECTION)
if level_root is None:
    raise RuntimeError(f"Missing collection: {ROOT_COLLECTION}")

moved = []
for name in MOVE:
    col = bpy.data.collections.get(name)
    if col is None:
        print("MISSING", name)
        continue
    if col.name == level_root.name:
        raise RuntimeError("Refusing to parent a collection to itself")
    if level_root in col.children_recursive:
        raise RuntimeError(f"Cycle detected while parenting {name}")
    # Remove every top-level link from the scene root, but keep a link if the
    # collection is already nested somewhere else.
    if col.name in [c.name for c in scene.collection.children]:
        scene.collection.children.unlink(col)
    if col.name not in [c.name for c in level_root.children]:
        level_root.children.link(col)
    moved.append((name, len(col.all_objects)))

print("MOVED", moved)
print("LEVEL_ROOT_OBJECTS", len(level_root.all_objects))
print("SCENE_OBJECTS", len(scene.objects))
print("TOP_COLLECTIONS", [c.name for c in scene.collection.children])

scene.camera = bpy.data.objects.get("NEXUS_V05_CAM_Recepcion")
print("CAMERA", scene.camera.name if scene.camera else None)

bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("SAVED", OUT)
print("SIZE", os.path.getsize(OUT))
