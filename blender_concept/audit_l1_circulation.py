"""Conservative capsule-vs-AABB circulation audit for Level 1.

The check assumes the player capsule (radius 0.38 m, height 1.80 m) follows the
specified centerline. Door leaves/glass are excluded because the current scene
models them closed while gameplay expects them operable; their closed state is
reported separately. Low steps (<= 0.16 m above the floor) are walkable and are
reported separately. Everything else visible is treated as a blocker.

Run:
  blender -b nexus/nivel_01/NEXUS_L1_V05.blend --python blender_concept/audit_l1_circulation.py
"""

import json
import math
import os

import bpy
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
OUT = os.path.join(ROOT, "nexus/nivel_01/circulation_audit.json")
FLOOR = -5.65
RADIUS = 0.38
HEIGHT = 1.80
STEP = 0.05
STEP_HEIGHT = 0.16
DOOR_TOKENS = ("_DOOR_LEAF", "_DOOR_GLASS", "_DOOR_HANDLE", "DOOR_PIVOT")
IGNORE_TOKENS = ("NEXUS_V05_REC_FLASHLIGHT_", "NEXUS_V05_REC_EXTRACT_RING")

ROUTE = [
    ("reception_door_to_room", [(-12.0, 1.7), (-12.0, 2.2), (-12.0, 3.0), (-12.0, 4.0)]),
    ("reception_around_west", [(-12.0, 2.2), (-12.5, 2.2), (-13.3, 2.3), (-13.3, 4.0), (-11.0, 5.2)]),
    ("reception_to_corridor", [(-11.0, 5.2), (-13.3, 4.0), (-13.3, 2.3), (-12.0, 1.7), (-12.0, 0.0)]),
    ("corridor_west_to_security", [(-12.0, 0.0), (3.0, 0.0)]),
    ("security_approach", [(3.0, 0.0), (3.0, 1.7), (3.0, 4.2)]),
    ("security_to_control", [(3.0, 4.2), (3.0, 1.7), (3.0, 0.0), (12.2, 0.0), (12.2, 1.7), (12.5, 3.0), (12.5, 5.9), (12.5, 7.0)]),
    ("control_to_restricted", [(12.5, 7.0), (12.5, 5.9), (12.5, 3.0), (12.2, 1.7), (12.2, 0.0), (13.3, -0.3), (18.0, -0.3), (22.0, -0.3), (24.0, -0.3)]),
]


def world_bounds(ob):
    corners = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    xs = [c.x for c in corners]
    ys = [c.y for c in corners]
    zs = [c.z for c in corners]
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)


def point_rect_distance(px, py, rect):
    x0, x1, y0, y1 = rect
    dx = max(x0 - px, 0.0, px - x1)
    dy = max(y0 - py, 0.0, py - y1)
    return math.hypot(dx, dy)


def nearest(px, py):
    best = None
    for ob in blockers:
        rect = ob["xy"]
        # quick reject at 3 m
        if px < rect[0] - 3 or px > rect[1] + 3 or py < rect[2] - 3 or py > rect[3] + 3:
            continue
        d = point_rect_distance(px, py, rect)
        if best is None or d < best[0]:
            best = (d, ob["name"])
    if best is None:
        return 3.0, None
    return best


def sample_segment(a, b):
    ax, ay = a
    bx, by = b
    length = math.hypot(bx - ax, by - ay)
    count = max(1, int(math.ceil(length / STEP)))
    points = []
    for i in range(count + 1):
        t = i / count
        points.append((ax + (bx - ax) * t, ay + (by - ay) * t))
    return length, points


bpy.context.view_layer.update()
scene = bpy.context.scene
blockers = []
steps = []
door_objects = []
for ob in scene.objects:
    if ob.type != "MESH" or ob.hide_render:
        continue
    b = world_bounds(ob)
    z0, z1 = b[4], b[5]
    if z1 <= FLOOR + 0.02 or z0 >= FLOOR + HEIGHT:
        continue
    if any(t in ob.name for t in IGNORE_TOKENS):
        continue
    if any(t in ob.name for t in DOOR_TOKENS):
        door_objects.append(ob.name)
        continue
    item = {"name": ob.name, "xy": (b[0], b[1], b[2], b[3]), "z": (round(z0, 2), round(z1, 2))}
    if z1 <= FLOOR + STEP_HEIGHT:
        steps.append(item)
    else:
        blockers.append(item)

segments = []
all_hits = {}
for label, coords in ROUTE:
    total = 0.0
    minimum = {"clearance_m": 999.0, "point": None, "blocker": None}
    hits = {}
    for a, b in zip(coords, coords[1:]):
        length, points = sample_segment(a, b)
        total += length
        for point in points:
            distance, name = nearest(point[0], point[1])
            clearance = distance - RADIUS
            if clearance < minimum["clearance_m"]:
                minimum = {"clearance_m": round(clearance, 3), "point": [round(point[0], 2), round(point[1], 2)], "blocker": name}
            if clearance < 0:
                hits.setdefault(name, {"point": [round(point[0], 2), round(point[1], 2)], "clearance_m": round(clearance, 3)})
    segments.append({"label": label, "length_m": round(total, 2), "min_clearance": minimum, "blockers": hits})
    for name, info in hits.items():
        all_hits.setdefault(name, []).append((label, info["point"], info["clearance_m"]))

doors = []
for prefix in ("NEXUS_V05_RECEPCION_DOOR", "NEXUS_V05_SEGURIDAD_DOOR", "NEXUS_V05_CONTROL_ACCESO_DOOR", "NEXUS_V05_VESTUARIOS_DOOR", "NEXUS_V05_MANTENIMIENTO_DOOR", "NEXUS_V05_ALMACEN_DOOR"):
    left = bpy.data.objects.get(prefix + "_L")
    right = bpy.data.objects.get(prefix + "_R")
    top = bpy.data.objects.get(prefix + "_TOP")
    if not (left and right and top):
        continue
    lb = world_bounds(left)
    rb = world_bounds(right)
    tb = world_bounds(top)
    gap_x = rb[0] - lb[1]
    gap_y = rb[2] - lb[3]
    width = gap_x if gap_x > 0 else gap_y
    doors.append({
        "prefix": prefix,
        "clear_width_m": round(width, 3),
        "clear_height_m": round(tb[4] - FLOOR, 3),
        "leaf": next((o.name for o in scene.objects if o.name == prefix + "_LEAF"), None),
    })

# Measured pinches that matter for the route.
def bbox(name):
    ob = bpy.data.objects.get(name)
    return world_bounds(ob) if ob else None

bench = bbox("NEXUS_V05_REC_BENCH2")
wall_s = bbox("NEXUS_V05_RECEPCION_WALL_S_A")
cart = bbox("NEXUS_L1_DIS_CART_CORR_cart")
door_control = bbox("NEXUS_V05_CONTROL_ACCESO_DOOR_L")
pinches = {}
if bench and wall_s:
    pinches["reception_bench_to_south_wall"] = {
        "gap_m": round(bench[2] - wall_s[3], 3),
        "player_diameter_m": round(RADIUS * 2, 3),
        "margin_m": round(bench[2] - wall_s[3] - RADIUS * 2, 3),
        "bench_x": [round(bench[0], 2), round(bench[1], 2)],
        "bench_y": [round(bench[2], 2), round(bench[3], 2)],
    }
if cart and door_control:
    pinches["control_cart_to_door"] = {
        "cart_x": [round(cart[0], 2), round(cart[1], 2)],
        "cart_y": [round(cart[2], 2), round(cart[3], 2)],
        "door_west_edge_x": round(door_control[1], 2),
        "free_width_m": round(door_control[1] - cart[0] if False else 0, 3),
    }

report = {
    "file": bpy.data.filepath,
    "floor": FLOOR,
    "capsule": {"radius_m": RADIUS, "height_m": HEIGHT, "diameter_m": RADIUS * 2},
    "step_m": STEP,
    "step_height_m": STEP_HEIGHT,
    "segments": segments,
    "blockers_hit": {name: values for name, values in sorted(all_hits.items())},
    "door_geometry": doors,
    "door_leaf_objects_excluded": sorted(set(door_objects)),
    "low_steps_excluded": [{"name": s["name"], "z": s["z"]} for s in steps],
    "pinches": pinches,
    "blocker_count": len(blockers),
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as handle:
    json.dump(report, handle, ensure_ascii=False, indent=2)

print("WROTE", OUT)
for seg in segments:
    print("SEG", seg["label"], "len", seg["length_m"], "min_clearance", seg["min_clearance"], "blockers", len(seg["blockers"]))
    for name, info in sorted(seg["blockers"].items()):
        print("  ", name, info)
print("DOORS", doors)
print("PINCHES", pinches)
print("TOTAL_BLOCKERS", len(blockers), "STEPS", len(steps), "HIT_OBJECTS", len(all_hits))
