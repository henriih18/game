import bpy, math, json, os
from mathutils import Vector

scene = bpy.context.scene
prefixes = ('NEXUS_V05_REC_FLASHLIGHT_', 'NEXUS_V05_REC_EXTRACT_')
new = [o for o in scene.objects if o.name.startswith(prefixes)]
new_meshes = [o for o in new if o.type == 'MESH']
old_meshes = [o for o in scene.objects if o.type == 'MESH' and o not in new and not o.hide_render]

def bounds(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return (min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts),
            max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))

def vol(a, b):
    dx = min(a[3], b[3]) - max(a[0], b[0])
    dy = min(a[4], b[4]) - max(a[1], b[1])
    dz = min(a[5], b[5]) - max(a[2], b[2])
    if dx <= 0 or dy <= 0 or dz <= 0:
        return 0.0
    return dx * dy * dz

print('FILE', bpy.data.filepath)
print('SCENE_OBJECTS', len(scene.objects), 'NEW', len(new), 'NEW_MESHES', len(new_meshes))
print('PLAY', len(bpy.data.collections['NEXUS_V05_REC_PLAY'].objects))
print('CAMERA', scene.camera.name if scene.camera else None)
print('LOCAL_CLOCKS', [o.name for o in scene.objects if 'REC_CLOCK' in o.name and o.library is None])
print('TORCH_COLLECTION', [c.name for c in bpy.data.collections if c.name.startswith('small_plastic_torch')])
for o in new:
    b = bounds(o)
    print('NEW', o.name, o.type, 'bbox', tuple(round(v,3) for v in b), 'parent', o.parent.name if o.parent else None)
    if o.type == 'FONT':
        print('TEXT', o.data.body)

# Room bounds check (reception interior; loose margin for wall-mounted elements)
for o in new_meshes:
    b = bounds(o)
    if not (-20.1 <= b[0] and b[3] <= -3.9 and 1.65 <= b[1] and b[4] <= 11.8 and -5.7 <= b[2] and b[5] <= -2.5):
        print('OUTSIDE_RECEPTION', o.name, tuple(round(v,3) for v in b))
    if b[2] < -5.66:
        print('BELOW_FLOOR', o.name, round(b[2],4))

collisions = []
for n in new_meshes:
    a = bounds(n)
    for o in old_meshes:
        b = bounds(o)
        v = vol(a, b)
        if v > 0.0005:
            collisions.append((round(v,5), n.name, o.name))
for item in sorted(collisions, reverse=True)[:30]:
    print('COLLISION', item)

# Metadata
for name in ('NEXUS_V05_REC_FLASHLIGHT_RIG', 'NEXUS_V05_REC_EXTRACT_ZONE'):
    o = bpy.data.objects[name]
    print('META', name, {k: o[k] for k in o.keys()})

# Lights
for o in new:
    if o.type == 'LIGHT':
        print('LIGHT', o.name, o.data.type, o.data.energy, o.data.use_shadow,
              tuple(round(v,3) for v in o.matrix_world.translation),
              tuple(round(v,3) for v in (o.matrix_world.to_quaternion() @ Vector((0,0,-1)))))
print('SHADOW_LIGHTS', sum(1 for o in scene.objects if o.type == 'LIGHT' and o.data.use_shadow and not o.hide_render))
