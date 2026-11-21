"""Presupuesto de sombras del Nivel 1. Se ejecuta sobre NEXUS_L1_V05.blend."""
import bpy, json
from pathlib import Path

scene=bpy.context.scene
disabled=[]
kept=[]
fill_tokens=('REC_FILL','E_CTRL_FILL','E_MAINT_FILL','F_MAINT_FILL','B_STORE_LIGHT_A','B_STORE_LIGHT_B')
for o in scene.objects:
    if o.type!='LIGHT' or o.hide_render or o.library:
        continue
    light=o.data
    name=o.name
    no_shadow=light.type=='POINT' or any(t in name for t in fill_tokens)
    if name.startswith('NEXUS_V05_CORR_LIGHT_'):
        try: no_shadow=no_shadow or int(name.rsplit('_',1)[1])%2==1
        except ValueError: pass
    if name=='NEXUS_V05_SERVICE_CONN_LIGHT_1':
        no_shadow=True
    light.use_shadow=not no_shadow
    if no_shadow:
        disabled.append(name)
    else:
        light.shadow_maximum_resolution=0.005
        kept.append(name)
scene['l1_shadow_policy']='Main area lights only; fill points and alternating corridor fill without shadows; max pixel 0.005 m'
scene['l1_shadow_lights_disabled']=len(disabled)
scene['l1_shadow_lights_kept']=len(kept)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
report={'file':bpy.data.filepath,'shadows_kept':kept,'shadows_disabled':disabled,'pool':scene.eevee.shadow_pool_size}
Path('/home/riyo/Documentos/game/nexus/nivel_01/light_optimization.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('SHADOWS_KEPT',len(kept),kept)
print('SHADOWS_DISABLED',len(disabled))
print('SAVED',bpy.data.filepath)
