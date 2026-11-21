import bpy
import json
import os
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
GLB = os.path.join(ROOT, "assets/models/fm/reception_waiting_lod.glb")
REPORT = os.path.join(ROOT, "docs/fm_reception_waiting_lod_export.json")
COLLECTIONS = (
    "L1_RECEPTION_R11_HERO",
    "L1_RECEPTION_R12_HERO",
    "L1_RECEPTION_R12_LOD",
    "L1_RECEPTION_R12_COLLISION",
)
STRAYS = ("PROP_Z10_LockerDoor_01", "STUDIO_Z10_Backdrop", "STUDIO_Z10_Floor")
SCENE = bpy.data.scenes["NEXUS_L1_V06_ARCH"]

objects = []
for cname in COLLECTIONS:
    col = bpy.data.collections.get(cname)
    if col is None:
        continue
    for ob in col.all_objects:
        if ob is not None and ob.type == 'MESH':
            objects.append(ob)

objects = list({ob.name: ob for ob in objects}.values())
state = {ob.name: (ob.hide_render, ob.hide_viewport, ob.hide_get(), ob.select_get()) for ob in objects}
stray_state = {}
for name in STRAYS:
    ob = bpy.data.objects.get(name)
    if ob is None:
        continue
    stray_state[name] = [c.name for c in ob.users_collection]
    for c in list(ob.users_collection):
        c.objects.unlink(ob)

parent_state = {ob.name: (ob.parent, ob.matrix_world.copy()) for ob in objects}
for ob in objects:
    world = ob.matrix_world.copy()
    ob.parent = None
    ob.matrix_world = world
    ob.hide_render = False
    ob.hide_viewport = False
    ob.hide_set(False)
    ob.select_set(True)
bpy.context.view_layer.objects.active = objects[0]
bpy.context.view_layer.update()

bpy.ops.export_scene.gltf(
    filepath=GLB,
    export_format='GLB',
    use_selection=True,
    export_apply=True,
    export_cameras=False,
    export_lights=False,
    export_extras=True,
)

for name, cols in stray_state.items():
    ob = bpy.data.objects.get(name)
    if ob:
        for cname in cols:
            col = bpy.data.collections.get(cname)
            if col and ob.name not in col.objects:
                col.objects.link(ob)

for ob in objects:
    parent, world = parent_state[ob.name]
    ob.parent = parent
    ob.matrix_world = world
for ob in objects:
    hr, hv, hs, sel = state[ob.name]
    ob.hide_render = hr
    ob.hide_viewport = hv
    ob.hide_set(hs)
    ob.select_set(sel)
bpy.context.view_layer.update()

meshes = [ob for ob in objects if ob.type == 'MESH']
points = []
for ob in meshes:
    for c in ob.bound_box:
        points.append(ob.matrix_world @ Vector(c))
mn = [min(p[i] for p in points) for i in range(3)]
mx = [max(p[i] for p in points) for i in range(3)]
report = {
    "objects": len(meshes),
    "unique_meshes": len({ob.data.name for ob in meshes}),
    "tris": sum(sum(len(p.vertices) - 2 for p in ob.data.polygons) for ob in meshes),
    "collisions": sum(1 for ob in meshes if ob.name.endswith("-col")),
    "names": sorted(ob.name for ob in meshes),
    "aabb": [[round(v, 4) for v in mn], [round(v, 4) for v in mx]],
    "bytes": os.path.getsize(GLB),
    "strays": [ob.name for ob in meshes if ob.name in STRAYS or ob.name.startswith(("STUDIO", "VAL_", "PROP_Z10"))],
}
with open(REPORT, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print("REC12_WAITING_EXPORT", json.dumps(report, ensure_ascii=False))
