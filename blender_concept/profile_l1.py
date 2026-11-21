"""Perfil estático del Nivel 1 modular. No modifica la escena."""
import bpy
import json
from pathlib import Path

ROOT = Path('/home/riyo/Documentos/game')
OUT = ROOT / 'nexus/nivel_01/profile_baseline.json'
scene = bpy.context.scene
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
cache = {}

def evaluated(o):
    if o.type != 'MESH':
        return (0, 0, 0)
    ev = o.evaluated_get(dg)
    me = ev.to_mesh()
    if me is None:
        return (0, 0, 0)
    me.calc_loop_triangles()
    result = (len(me.loop_triangles), len(me.vertices), max(1, len(me.materials)))
    ev.to_mesh_clear()
    return result

def visible(o):
    return not o.hide_render

roots = {}
for o in scene.objects:
    if o.type == 'EMPTY' and o.get('asset_source'):
        tris = verts = slots = meshes = 0
        for child in o.children_recursive:
            if visible(child) and child.type == 'MESH':
                a, b, c = evaluated(child)
                tris += a
                verts += b
                slots += c
                meshes += 1
        roots[o.name] = {
            'source': o.get('asset_source'),
            'triangles': tris,
            'vertices': verts,
            'material_slots': slots,
            'meshes': meshes,
            'instances': 1,
        }

# Agrupar raíces que comparten exactamente la misma biblioteca de origen.
groups = {}
for name, row in roots.items():
    source = row['source'] or '(sin origen)'
    g = groups.setdefault(source, {'source': source, 'instances': 0, 'roots': [], 'triangles': 0, 'material_slots': 0, 'meshes': 0})
    g['instances'] += 1
    g['roots'].append(name)
    g['triangles'] += row['triangles']
    g['material_slots'] += row['material_slots']
    g['meshes'] += row['meshes']

collections = []
for c in scene.collection.children:
    objs = list(c.all_objects)
    tris = sum(evaluated(o)[0] for o in objs if visible(o))
    collections.append({'name': c.name, 'objects': len(objs), 'triangles': tris, 'hide_render': c.hide_render})

meshes = [o for o in scene.objects if o.type == 'MESH' and visible(o)]
lights = [o for o in scene.objects if o.type == 'LIGHT' and visible(o)]
images = []
for im in bpy.data.images:
    if im.source != 'FILE' or not im.filepath:
        continue
    w, h = im.size
    path = bpy.path.abspath(im.filepath)
    images.append({
        'name': im.name,
        'path': path,
        'size': [w, h],
        'exists': Path(path).exists(),
        'rgba_mip_bytes': int(w * h * 4 * 4 / 3) if w and h else 0,
    })

result = {
    'file': bpy.data.filepath,
    'objects_scene': len(scene.objects),
    'mesh_objects_visible': len(meshes),
    'unique_mesh_data': len({o.data.as_pointer() for o in meshes}),
    'triangles_visible': sum(evaluated(o)[0] for o in meshes),
    'material_slots_visible': sum(evaluated(o)[2] for o in meshes),
    'lights_visible': len(lights),
    'lights_shadow_enabled': sum(bool(o.data.use_shadow) for o in lights),
    'collections': sorted(collections, key=lambda x: x['triangles'], reverse=True),
    'asset_groups': sorted(groups.values(), key=lambda x: x['triangles'], reverse=True),
    'images': sorted(images, key=lambda x: x['rgba_mip_bytes'], reverse=True),
    'texture_rgba_mip_bytes_total': sum(x['rgba_mip_bytes'] for x in images),
    'missing_images': [x['path'] for x in images if not x['exists']],
    'libraries': [{'path': x.filepath, 'resolved': bpy.path.abspath(x.filepath)} for x in bpy.data.libraries],
}
OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
print('PROFILE_JSON', OUT)
print('SUMMARY', {k: result[k] for k in ('objects_scene','mesh_objects_visible','unique_mesh_data','triangles_visible','material_slots_visible','lights_visible','lights_shadow_enabled','texture_rgba_mip_bytes_total')})
print('TOP_ASSETS')
for row in result['asset_groups'][:20]:
    print(row['triangles'], row['instances'], row['source'])
print('TOP_TEXTURES')
for row in result['images'][:12]:
    print(row['rgba_mip_bytes'], row['size'], row['name'])
