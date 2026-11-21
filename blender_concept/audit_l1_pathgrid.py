"""Grid reachability audit for Level 1 with the player capsule radius.

A cell is walkable when a 0.38 m radius circle centred on it does not overlap the
plan-view AABB of any visible mesh between floor+0.16 m and floor+1.80 m. Door
leaves/glass are excluded (assumed operable), low steps are excluded, and the
result is a conservative reachability map, not a navmesh.

Run:
  blender -b nexus/nivel_01/NEXUS_L1_V05.blend --python blender_concept/audit_l1_pathgrid.py
"""

import json
import math
import os
from collections import deque

import bpy
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
OUT = os.path.join(ROOT, "nexus/nivel_01/circulation_reachability.json")
FLOOR = -5.65
RADIUS = 0.38
HEIGHT = 1.80
CELL = 0.05
STEP_HEIGHT = 0.16
X0, X1 = -29.0, 25.0
Y0, Y1 = -10.0, 14.0
DOOR_TOKENS = ("_DOOR_LEAF", "_DOOR_GLASS", "_DOOR_HANDLE", "DOOR_PIVOT",
               "NEXUS_V05_C_REC_ELEV_L", "NEXUS_V05_C_REC_ELEV_R")
IGNORE_TOKENS = ("NEXUS_V05_REC_FLASHLIGHT_", "NEXUS_V05_REC_EXTRACT_RING")

# Huecos reales que el AABB de una malla cortada no puede representar.
# x0, x1, y0, y1; se despeja el paso central con margen de cápsula.
PORTALS = [
    (-18.44, -16.56, 10.90, 12.60),  # hueco del ascensor de recepción
]

START = (-12.0, 0.0)
TARGETS = {
    "reception_just_inside": (-12.0, 2.05),
    "reception_entry": (-12.0, 2.6),
    "reception_counter_front": (-12.0, 6.6),
    "reception_west": (-16.0, 6.5),
    "security": (3.0, 4.2),
    "control_just_inside": (13.2, 2.1),
    "control_before_arch": (13.0, 5.2),
    "control_after_arch": (13.0, 6.4),
    "control_desk": (13.0, 7.0),
    "restricted_link": (23.5, 0.0),
    "corridor_west_south": (-15.0, -1.0),
    "corridor_west_end_south": (-20.0, -1.0),
    "extraction_elevator_center": (-17.5, 10.7),
    "extraction_elevator_zone_north": (-17.5, 11.0),
    "extraction_console_front": (-15.1, 10.9),
    "extraction_lobby_approach": (-16.3, 9.7),
    "elevator_car_center": (-17.5, 12.5),
    "elevator_car_back": (-17.5, 13.2),
    "vestuarios_just_inside": (-14.0, -2.1),
    "almacen_just_inside": (-2.0, -2.1),
    "mantenimiento_just_inside": (13.0, -2.1),
}


def world_bounds(ob):
    corners = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    xs = [c.x for c in corners]
    ys = [c.y for c in corners]
    zs = [c.z for c in corners]
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)


def cell_index(x, y):
    return int(round((x - X0) / CELL)), int(round((y - Y0) / CELL))


def cell_center(ix, iy):
    return X0 + ix * CELL, Y0 + iy * CELL


bpy.context.view_layer.update()
scene = bpy.context.scene
nx = int(math.floor((X1 - X0) / CELL)) + 1
ny = int(math.floor((Y1 - Y0) / CELL)) + 1
blocked = bytearray(nx * ny)
obstacles = []

for ob in scene.objects:
    if ob.type != "MESH" or ob.hide_render:
        continue
    b = world_bounds(ob)
    if b[5] <= FLOOR + STEP_HEIGHT or b[4] >= FLOOR + HEIGHT:
        continue
    if any(t in ob.name for t in DOOR_TOKENS) or any(t in ob.name for t in IGNORE_TOKENS):
        continue
    x0, x1, y0, y1 = b[0] - RADIUS, b[1] + RADIUS, b[2] - RADIUS, b[3] + RADIUS
    if x1 < X0 or x0 > X1 or y1 < Y0 or y0 > Y1:
        continue
    obstacles.append({"name": ob.name, "xy": [round(v, 2) for v in (b[0], b[1], b[2], b[3])], "z": [round(b[4], 2), round(b[5], 2)]})
    ix0 = max(0, int(math.ceil((x0 - X0) / CELL)))
    ix1 = min(nx - 1, int(math.floor((x1 - X0) / CELL)))
    iy0 = max(0, int(math.ceil((y0 - Y0) / CELL)))
    iy1 = min(ny - 1, int(math.floor((y1 - Y0) / CELL)))
    for iy in range(iy0, iy1 + 1):
        row = iy * nx
        for ix in range(ix0, ix1 + 1):
            blocked[row + ix] = 1

for px0, px1, py0, py1 in PORTALS:
    ix0 = max(0, int(math.ceil((px0 + RADIUS - X0) / CELL)))
    ix1 = min(nx - 1, int(math.floor((px1 - RADIUS - X0) / CELL)))
    iy0 = max(0, int(math.ceil((py0 - Y0) / CELL)))
    iy1 = min(ny - 1, int(math.floor((py1 - Y0) / CELL)))
    for iy in range(iy0, iy1 + 1):
        row = iy * nx
        for ix in range(ix0, ix1 + 1):
            blocked[row + ix] = 0

sx, sy = cell_index(*START)
start_ok = not blocked[sy * nx + sx]
seen = bytearray(nx * ny)
parent = [-1] * (nx * ny)
if start_ok:
    q = deque([sy * nx + sx])
    seen[sy * nx + sx] = 1
    while q:
        idx = q.popleft()
        iy, ix = divmod(idx, nx)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            jx, jy = ix + dx, iy + dy
            if 0 <= jx < nx and 0 <= jy < ny:
                j = jy * nx + jx
                if not seen[j] and not blocked[j]:
                    seen[j] = 1
                    parent[j] = idx
                    q.append(j)


def reconstruct(target):
    tx, ty = cell_index(*target)
    if not (0 <= tx < nx and 0 <= ty < ny):
        return None
    idx = ty * nx + tx
    if not seen[idx]:
        return None
    points = []
    while idx != -1:
        iy, ix = divmod(idx, nx)
        points.append([round(cell_center(ix, iy)[0], 2), round(cell_center(ix, iy)[1], 2)])
        idx = parent[idx]
    points.reverse()
    # Keep a manageable polyline: every 20th point plus the target.
    simplified = points[::20]
    if simplified[-1] != points[-1]:
        simplified.append(points[-1])
    return simplified


results = {}
for name, target in TARGETS.items():
    path = reconstruct(target)
    results[name] = {"target": list(target), "reachable": path is not None, "path": path}

component = sum(seen)
report = {
    "file": bpy.data.filepath,
    "cell_m": CELL,
    "bounds": [[X0, X1], [Y0, Y1]],
    "capsule_radius_m": RADIUS,
    "step_height_m": STEP_HEIGHT,
    "start": list(START),
    "start_walkable": start_ok,
    "reachable_cells": component,
    "walkable_cells": nx * ny - sum(blocked),
    "targets": results,
    "obstacle_count": len(obstacles),
    "obstacles": obstacles,
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as handle:
    json.dump(report, handle, ensure_ascii=False, indent=2)

# Compact plan map of the reception for visual diagnosis.
print("MAP reception (# blocked, . reachable, space isolated-free)")
step = 0.2
ymax = 11.6
y = ymax
while y >= 1.8:
    row = []
    x = -20.0
    while x <= -4.0:
        ix, iy = cell_index(x, y)
        if not (0 <= ix < nx and 0 <= iy < ny):
            row.append("?")
        else:
            j = iy * nx + ix
            row.append("#" if blocked[j] else ("." if seen[j] else " "))
        x += step
    print(f"{y:5.1f} " + "".join(row))
    y -= step
print("      " + "".join(str(int(abs(x)) % 10) for x in [round(-20.0 + i * step, 1) for i in range(int((-4.0 + 20.0) / step) + 1)]))

print("WROTE", OUT)
print("START", START, "WALKABLE", start_ok, "COMPONENT", component, "FREE", nx * ny - sum(blocked), "OBSTACLES", len(obstacles))
for name, result in results.items():
    print("TARGET", name, result["target"], "REACHABLE", result["reachable"], "WAYPOINTS", len(result["path"] or []))
    if result["path"]:
        print("  ", result["path"][:24])
