import bpy, json, struct
from pathlib import Path

ROOT = Path('/home/riyo/Documentos/game')
BLEND = ROOT / 'nexus/nivel_01/FM_PLAYER_WORK_055_BOUND.blend'
GLB = ROOT / 'assets/models/fm/player_generated_v5.glb'

bpy.ops.wm.open_mainfile(filepath=str(BLEND))

# Bajar texturas a 1024 solo en memoria para el export.
for img in bpy.data.images:
    if img.size[0] > 1024 or img.size[1] > 1024:
        img.scale(1024, 1024)

rig = bpy.data.objects['PlayerRig']
mesh = bpy.data.objects['Player_Game']

bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True)
mesh.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.context.view_layer.update()

bpy.ops.export_scene.gltf(
    filepath=str(GLB),
    export_format='GLB',
    use_selection=True,
    export_yup=True,
    export_apply=False,
    export_animations=True,
    export_animation_mode='ACTIONS',
    export_anim_single_armature=True,
    export_anim_slide_to_zero=True,
    export_cameras=False,
    export_lights=False,
    export_extras=True,
)

# Validación directa del chunk JSON.
data = GLB.read_bytes()
magic, version, length = struct.unpack_from('<III', data, 0)
off = 12
json_chunk = None
while off < length:
    clen, ctype = struct.unpack_from('<II', data, off)
    off += 8
    if ctype == 0x4E4F534A:
        json_chunk = data[off:off + clen]
        break
    off += clen
g = json.loads(json_chunk.decode('utf-8'))
tris = 0
for m in g.get('meshes', []):
    for p in m.get('primitives', []):
        idx = p.get('indices')
        if idx is not None:
            tris += g['accessors'][idx]['count'] // 3
print('PLAYER_EXPORT_V5_OK', GLB.stat().st_size,
      'meshes', len(g.get('meshes', [])),
      'skins', len(g.get('skins', [])),
      'joints', len(g['skins'][0]['joints']) if g.get('skins') else 0,
      'animations', [a.get('name') for a in g.get('animations', [])],
      'tris', tris,
      'materials', len(g.get('materials', [])),
      'images', len(g.get('images', [])),
      'cameras', len(g.get('cameras', [])),
      'lights', len(g.get('extensions', {}).get('KHR_lights_punctual', {}).get('lights', [])))
