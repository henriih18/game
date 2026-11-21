"""Conservative audit of the east core: L1 approach and vertical flight centre.

Two independent checks:
1. A 2D capsule grid from the L1 link (24, 0) to the L1 stair portal. Door
   leaves are excluded (assumed operable); low steps are excluded.
2. For every stair flight, three centreline samples at 25/50/75 % of the run.
   Side clearance uses a BVH of visible tower geometry without the walking
   surfaces; headroom casts a vertical ray from 0.40 m above the tread.

The result is an analytical clearance pass, not a CharacterBody simulation.

Run:
  blender -b nexus/master/NEXUS_MASTER.blend --python blender_concept/audit_core_route.py
"""

import json
import math
import os
from collections import deque

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = "/home/riyo/Documentos/game"
OUT = os.path.join(ROOT, "nexus/nucleo/core_route_audit.json")
RADIUS = 0.38
HEIGHT = 1.80
MIN_HEADROOM = 3.12
CELL = 0.05
STEP = 0.16
FLOOR = -5.80
X0, X1 = 21.4, 30.3
Y0, Y1 = -1.7, 15.7
START = (24.0, 0.0)
PORTAL = (30.0, 12.5)
DOOR_TOKENS = ("_DOOR_LEAF", "_DOOR_GLASS", "_DOOR_HANDLE", "DOOR_PIVOT")
TRAMOS = ("L1_L2", "L2_L3", "L3_L4", "L4_L5")


def bounds(ob):
    corners = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    xs = [c.x for c in corners]
    ys = [c.y for c in corners]
    zs = [c.z for c in corners]
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)


def flight_ends(ob):
    mw = ob.matrix_world
    zs = [(mw @ v.co).z for v in ob.data.vertices]
    zmax, zmin = max(zs), min(zs)
    top = [mw @ v.co for v in ob.data.vertices if (mw @ v.co).z >= zmax - 0.06]
    top_x = sum(v.x for v in top) / len(top)
    b = bounds(ob)
    bot_x = b[1] if abs(top_x - b[0]) < abs(top_x - b[1]) else b[0]
    return top_x, bot_x, (b[2] + b[3]) / 2, zmax, zmin + 0.16, b


def build_bvh(objects):
    verts, polys, offset = [], [], 0
    for ob in objects:
        if ob.type != "MESH" or ob.hide_render:
            continue
        mw = ob.matrix_world
        for v in ob.data.vertices:
            verts.append(mw @ v.co)
        for poly in ob.data.polygons:
            polys.append(tuple(offset + i for i in poly.vertices))
        offset += len(ob.data.vertices)
    return BVHTree.FromPolygons(verts, polys, all_triangles=False) if polys else None, len(verts), len(polys)


bpy.context.view_layer.update()
scene = bpy.context.scene
tower = []
for ob in scene.objects:
    if ob.type != "MESH" or ob.hide_render:
        continue
    b = bounds(ob)
    if b[1] < 21.0 or b[0] > 37.0 or b[3] < 8.0 or b[2] > 17.0 or b[5] < -45.0 or b[4] > -1.0:
        continue
    tower.append(ob)

side = [o for o in tower if not (("_FLIGHT_" in o.name or "_LANDING_" in o.name or "_THRESHOLD_" in o.name) and "CUT_" not in o.name)]
all_bvh, all_verts, all_polys = build_bvh(tower)
side_bvh, side_verts, side_polys = build_bvh(side)

report = {
    "file": bpy.data.filepath,
    "capsule_radius_m": RADIUS,
    "capsule_height_m": HEIGHT,
    "min_required_headroom_m": MIN_HEADROOM,
    "tower_objects": len(tower),
    "side_bvh": [side_verts, side_polys],
    "all_bvh": [all_verts, all_polys],
    "flights": [],
    "approach": {},
    "failures": [],
}

for ob in sorted(scene.objects, key=lambda o: o.name):
    if ob.type != "MESH" or ob.hide_render or "_FLIGHT_" not in ob.name or ob.name.endswith("_RAILS"):
        continue
    tramo = next((t for t in TRAMOS if "_FLIGHT_%s_" % t in ob.name), None)
    if tramo is None:
        continue
    top_x, bot_x, cy, ztop, zbot, b = flight_ends(ob)
    samples = []
    clear_min = 1e9
    clear_at = None
    head_min = 1e9
    head_at = None
    for t in (0.25, 0.50, 0.75):
        px = top_x + (bot_x - top_x) * t
        pz = ztop + (zbot - ztop) * t
        loc, normal, index, dist = side_bvh.find_nearest(Vector((px, cy, pz + 0.90)))
        clear = dist - RADIUS if loc is not None else None
        hit = all_bvh.ray_cast(Vector((px, cy, pz + 0.40)), Vector((0.0, 0.0, 1.0)))
        head = (hit[3] + 0.30) if hit[0] is not None else None
        samples.append({
            "t": t,
            "point": [round(px, 2), round(cy, 2), round(pz, 2)],
            "clearance_m": round(clear, 3) if clear is not None else None,
            "nearest": [round(v, 2) for v in loc] if loc else None,
            "headroom_m": round(head, 3) if head is not None else None,
        })
        if clear is not None and clear < clear_min:
            clear_min, clear_at = clear, samples[-1]
        if head is not None and head < head_min:
            head_min, head_at = head, samples[-1]
    entry = {
        "flight": ob.name,
        "tramo": tramo,
        "lane_y": round(cy, 2),
        "run_m": round(abs(bot_x - top_x), 2),
        "rise_m": round(ztop - zbot, 2),
        "top_x": round(top_x, 2),
        "bottom_x": round(bot_x, 2),
        "clearance_min_m": round(clear_min, 3) if clear_min < 1e8 else None,
        "clearance_at": clear_at,
        "headroom_min_m": round(head_min, 3) if head_min < 1e8 else None,
        "headroom_at": head_at,
        "samples": samples,
    }
    report["flights"].append(entry)
    if clear_min < 0:
        report["failures"].append("CAPSULE_%s" % ob.name)
    if head_min < MIN_HEADROOM:
        report["failures"].append("HEADROOM_%s" % ob.name)

# 2D accessibility from the L1 link to the stair portal.
nx = int(math.floor((X1 - X0) / CELL)) + 1
ny = int(math.floor((Y1 - Y0) / CELL)) + 1
blocked = bytearray(nx * ny)
for ob in scene.objects:
    if ob.type != "MESH" or ob.hide_render:
        continue
    b = bounds(ob)
    if b[5] <= FLOOR + STEP or b[4] >= FLOOR + HEIGHT:
        continue
    if any(tok in ob.name for tok in DOOR_TOKENS):
        continue
    if b[1] < X0 or b[0] > X1 or b[3] < Y0 or b[2] > Y1:
        continue
    if ob.name == "NEXUS_VTOWER_WALL_E":
        # The wall is a single boolean mesh with five door holes; its AABB is
        # solid. Replace it with the two solid spans around the L1 portal so
        # the grid does not falsely seal the 1.64 m opening.
        for yy0, yy1 in ((9.0, 11.66), (13.34, 17.0)):
            x0, x1 = b[0] - RADIUS, b[1] + RADIUS
            y0, y1 = yy0 - RADIUS, yy1 + RADIUS
            ix0 = max(0, int(math.ceil((x0 - X0) / CELL)))
            ix1 = min(nx - 1, int(math.floor((x1 - X0) / CELL)))
            iy0 = max(0, int(math.ceil((y0 - Y0) / CELL)))
            iy1 = min(ny - 1, int(math.floor((y1 - Y0) / CELL)))
            for iy in range(iy0, iy1 + 1):
                row = iy * nx
                for ix in range(ix0, ix1 + 1):
                    blocked[row + ix] = 1
        continue
    x0, x1, y0, y1 = b[0] - RADIUS, b[1] + RADIUS, b[2] - RADIUS, b[3] + RADIUS
    ix0 = max(0, int(math.ceil((x0 - X0) / CELL)))
    ix1 = min(nx - 1, int(math.floor((x1 - X0) / CELL)))
    iy0 = max(0, int(math.ceil((y0 - Y0) / CELL)))
    iy1 = min(ny - 1, int(math.floor((y1 - Y0) / CELL)))
    for iy in range(iy0, iy1 + 1):
        row = iy * nx
        for ix in range(ix0, ix1 + 1):
            blocked[row + ix] = 1


def index(p):
    return round((p[0] - X0) / CELL), round((p[1] - Y0) / CELL)


sx, sy = index(START)
tx, ty = index(PORTAL)
seen = bytearray(nx * ny)
parent = [-1] * (nx * ny)
start_ok = 0 <= sx < nx and 0 <= sy < ny and not blocked[sy * nx + sx]
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

target_idx = ty * nx + tx if 0 <= tx < nx and 0 <= ty < ny else -1
path = None
if target_idx >= 0 and seen[target_idx]:
    points = []
    idx = target_idx
    while idx != -1:
        iy, ix = divmod(idx, nx)
        points.append([round(X0 + ix * CELL, 2), round(Y0 + iy * CELL, 2)])
        idx = parent[idx]
    points.reverse()
    path = points[::20] + [points[-1]]
report["approach"] = {
    "start": list(START),
    "portal": list(PORTAL),
    "start_walkable": start_ok,
    "reachable": path is not None,
    "path": path,
    "walkable_cells": nx * ny - sum(blocked),
    "reachable_cells": sum(seen),
}
if path is None:
    report["failures"].append("L1_APPROACH_UNREACHABLE")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as handle:
    json.dump(report, handle, ensure_ascii=False, indent=2)

print("WROTE", OUT)
print("TOWER", len(tower), "FLIGHTS", len(report["flights"]), "APPROACH", report["approach"]["reachable"])
for f in report["flights"]:
    print(
        f["tramo"], f["flight"].rsplit("_", 1)[-1],
        "RUN", f["run_m"], "RISE", f["rise_m"],
        "CLEAR", f["clearance_min_m"], "HEAD", f["headroom_min_m"],
    )
print("FAILURES", report["failures"])
