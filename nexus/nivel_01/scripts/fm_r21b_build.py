"""Build L1_SECURITY_R21B_HERO (Security 03 filling).

Run through the Blender MCP:
    exec(open('/home/riyo/Documentos/game/nexus/nivel_01/scripts/fm_r21b_build.py').read())
"""
import sys
import importlib

sys.path.insert(0, "/home/riyo/Documentos/game/nexus/nivel_01/scripts")

import fm_ops_lib
import fm_r21b_lib
import fm_r21b_briefing
import fm_r21b_lockers
import fm_r21b_hatch
import fm_r21b_circulation
import fm_r21b_chaos
import fm_r21b_services

for m in (fm_ops_lib, fm_r21b_lib, fm_r21b_briefing, fm_r21b_lockers, fm_r21b_hatch,
          fm_r21b_circulation, fm_r21b_chaos, fm_r21b_services):
    importlib.reload(m)

import bpy

B = fm_r21b_lib

B.clean_root()
mat = B.palette()
brief = B.sub("L1_SECURITY_R21B_BRIEFING")
fm_r21b_briefing.build(mat, brief)
lock = B.sub("L1_SECURITY_R21B_LOCKERS")
fm_r21b_lockers.build(mat, lock)
hatch = B.sub("L1_SECURITY_R21B_HATCH")
fm_r21b_hatch.build(mat, hatch)
circ = B.sub("L1_SECURITY_R21B_CIRCULATION")
fm_r21b_circulation.build(mat, circ)
chaos = B.sub("L1_SECURITY_R21B_CHAOS")
fm_r21b_chaos.build(mat, chaos)
lights = B.sub("L1_SECURITY_R21B_LIGHTS")
fm_r21b_services.build(mat, circ, lights)

# QA quick summary
total_tris = 0
mesh_objs = 0
light_objs = 0
for c in bpy.data.collections:
    if not c.name.startswith("L1_SECURITY_R21B"):
        continue
    for ob in c.objects:
        if ob.type == "MESH":
            mesh_objs += 1
            total_tris += sum(len(p.vertices) - 2 for p in ob.data.polygons)
        elif ob.type == "LIGHT":
            light_objs += 1
print(f"R21B built: {mesh_objs} meshes, {total_tris} tris, {light_objs} lights")
bpy.context.view_layer.update()
