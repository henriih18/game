import bpy
import json
import os
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
GLB = os.path.join(ROOT, "assets/models/fm/reception_sector.glb")
REPORT = os.path.join(ROOT, "docs/fm_reception_sector_export.json")
COLLECTIONS = (
    "L1_RECEPTION_R1",
    "L1_RECEPTION_R2",
    "L1_RECEPTION_R3",
    "L1_RECEPTION_R5",
    "L1_RECEPTION_R6_HERO",
    "L1_RECEPTION_R7_HERO",
    "L1_RECEPTION_R8_HERO",
    "L1_RECEPTION_R9_HERO",
    "L1_RECEPTION_R10_AGING",
    "L1_RECEPTION_R11_HERO",
    "L1_RECEPTION_R12_HERO",
    "L1_RECEPTION_R13_HERO",
    "L1_ARCH_CEILINGS",
    "L1_ARCH_COLUMNS",
    "L1_ARCH_CIRCULATION",
    "L1_ARCH_ZONES",
)
REGION_MIN = (-110.2, -40.2, -1.0)
REGION_MAX = (-69.8, -3.8, 5.6)

selected = []
for cname in COLLECTIONS:
    col = bpy.data.collections.get(cname)
    if col is None:
        continue
    for ob in col.all_objects:
        if ob is None or ob.type != 'MESH':
            continue
        if ob.hide_render and ob.hide_viewport:
            continue
        corners = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
        center = sum(corners, Vector()) / 8.0
        if not (REGION_MIN[0] <= center.x <= REGION_MAX[0]
                and REGION_MIN[1] <= center.y <= REGION_MAX[1]
                and REGION_MIN[2] <= center.z <= REGION_MAX[2]):
            continue
        selected.append(ob)
selected = list({ob.name: ob for ob in selected}.values())
keep = {ob.name for ob in selected}
for ob in list(bpy.data.objects):
    if ob.name not in keep:
        bpy.data.objects.remove(ob, do_unlink=True)

for ob in selected:
    world = ob.matrix_world.copy()
    ob.parent = None
    ob.matrix_world = world
    ob.hide_render = False
    ob.hide_viewport = False
    ob.hide_set(False)
    ob.select_set(True)
bpy.context.view_layer.objects.active = selected[0]
bpy.context.view_layer.update()

bpy.ops.export_scene.gltf(
    filepath=GLB,
    export_format='GLB',
    use_selection=False,
    export_apply=True,
    export_cameras=False,
    export_lights=False,
    export_extras=True,
)

points = []
for ob in selected:
    for c in ob.bound_box:
        points.append(ob.matrix_world @ Vector(c))
mn = [min(p[i] for p in points) for i in range(3)]
mx = [max(p[i] for p in points) for i in range(3)]
report = {
    "objects": len(selected),
    "unique_meshes": len({ob.data.name for ob in selected}),
    "tris": sum(sum(len(p.vertices) - 2 for p in ob.data.polygons) for ob in selected),
    "names": sorted(ob.name for ob in selected),
    "aabb": [[round(v, 4) for v in mn], [round(v, 4) for v in mx]],
    "bytes": os.path.getsize(GLB),
    "strays": [ob.name for ob in selected if ob.name.startswith(("STUDIO", "VAL_", "PLAYER", "PROP_Z10"))],
}
with open(REPORT, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print("RECEPTION_SECTOR_EXPORT", json.dumps(report, ensure_ascii=False))
