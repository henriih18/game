"""Benchmark repetible de dos cámaras del Nivel 1; no guarda el .blend."""
import bpy, json, time, sys
from pathlib import Path

ROOT=Path('/home/riyo/Documentos/game')
mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'baseline'
outdir=ROOT/'nexus/nivel_01/benchmark'/mode
outdir.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1280
scene.render.resolution_y=720
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
results=[]
for camera_name,slug in [('NEXUS_V05_CAM_Corridor','corridor'),('NEXUS_V05_CAM_Recepcion','reception')]:
    scene.camera=bpy.data.objects[camera_name]
    times=[]
    for index in range(2):
        scene.render.filepath=str(outdir/f'{slug}_{index}.png')
        start=time.perf_counter()
        bpy.ops.render.render(write_still=True)
        elapsed=time.perf_counter()-start
        times.append(elapsed)
        print('RENDER',mode,slug,index,round(elapsed,3),flush=True)
    results.append({'camera':camera_name,'seconds':times,'warm_seconds':times[-1],'image':str(outdir/f'{slug}_1.png')})
report={'mode':mode,'file':bpy.data.filepath,'engine':scene.render.engine,'resolution':[1280,720],'samples':scene.eevee.taa_render_samples if hasattr(scene,'eevee') else None,'results':results}
(outdir/'times.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('BENCHMARK_JSON',outdir/'times.json')
