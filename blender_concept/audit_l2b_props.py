"""Auditoria de props del Nivel 2B: limites, apoyos y solapes entre objetos."""
import bpy
from mathutils import Vector

PREFIX = "NEXUS_STORY_L2B_"
FLOOR = -13.65
# x0, x1, y0, y1, z0, z1 (interiores)
ROOMS = {
    "AIRLOCK": (-1.86, 1.86, -13.86, -10.14, -13.8, -10.2),
    "ARCHIVO": (1.64, 12.36, -3.86, 3.86, -13.8, -9.8),
    "SERVIDORES": (3.14, 10.86, -13.36, -6.64, -13.8, -9.8),
    "ANALISIS": (3.14, 12.86, 16.14, 23.86, -13.8, -9.6),
}


def bbox(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return (Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
            Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))))


def room_of(o):
    for name, (x0, x1, y0, y1, z0, z1) in ROOMS.items():
        if x0 - 0.4 <= o.location.x <= x1 + 0.4 and y0 - 0.4 <= o.location.y <= y1 + 0.4:
            return name
    return None


def overlap(a0, a1, b0, b1):
    dx = min(a1.x, b1.x) - max(a0.x, b0.x)
    dy = min(a1.y, b1.y) - max(a0.y, b0.y)
    dz = min(a1.z, b1.z) - max(a0.z, b0.z)
    if dx <= 0 or dy <= 0 or dz <= 0:
        return 0.0, (dx, dy, dz)
    return dx * dy * dz, (dx, dy, dz)


objs = [o for o in bpy.data.objects
        if o.type == "MESH" and o.name.startswith(PREFIX)]
print("NEW", len(objs))

# 1. fuera de los limites de su sala
for o in objs:
    r = room_of(o)
    if r is None:
        print("OUTSIDE_ROOM", o.name, tuple(round(v, 2) for v in o.location))
        continue
    x0, x1, y0, y1, z0, z1 = ROOMS[r]
    a, b = bbox(o)
    if (a.x < x0 - 0.45 or b.x > x1 + 0.45 or a.y < y0 - 0.45 or
            b.y > y1 + 0.45 or a.z < z0 - 0.02 or b.z > z1 + 0.45):
        print("OUT_OF_BOUNDS", r, o.name,
              tuple(round(v, 2) for v in a), tuple(round(v, 2) for v in b))

# 2. objetos por debajo del suelo
for o in objs:
    a, b = bbox(o)
    if a.z < FLOOR - 0.015:
        print("BELOW_FLOOR", o.name, round(a.z, 3))

# 3. apoyos: objeto elevado sin nada justo debajo
skip = ("SIGN", "CABLE", "PIPE", "DUCT", "LIGHT", "BRACKET", "HANDLE",
        "GLASS", "LIQUID", "CAP", "BOTTLE", "VIAL", "PLATE", "PANEL",
        "DRAIN", "SLOT", "TAPE", "BEAM", "HANDLE", "KNOB", "LABEL",
        "SCREEN", "BUTTON", "KEY", "VISOR", "STRAP", "HOOK", "NOZZLE",
        "BRISTLE", "PAPER", "SHEET", "DECAL", "TRIM")
unsupported = []
for o in objs:
    a, b = bbox(o)
    if a.z <= FLOOR + 0.06:
        continue
    if any(s in o.name for s in skip):
        continue
    support = False
    for other in bpy.data.objects:
        if other == o or other.type != "MESH" or other.hide_render:
            continue
        oa, ob = bbox(other)
        if abs(ob.z - a.z) > 0.075:
            continue
        dx = min(b.x, ob.x) - max(a.x, oa.x)
        dy = min(b.y, ob.y) - max(a.y, oa.y)
        if dx > 0.02 and dy > 0.02:
            support = True
            break
    if not support:
        unsupported.append((o.name, round(a.z, 3), tuple(round(v, 2) for v in o.location)))
print("UNSUPPORTED", len(unsupported))
for row in unsupported:
    print("  ", row)

# 4. solapes entre props nuevos (AABB), ignorando piezas contenidas
collisions = []
for i, oa in enumerate(objs):
    a0, a1 = bbox(oa)
    va = max(1e-6, (a1.x - a0.x) * (a1.y - a0.y) * (a1.z - a0.z))
    for ob in objs[i + 1:]:
        b0, b1 = bbox(ob)
        vol, dims = overlap(a0, a1, b0, b1)
        if vol <= 0.001:
            continue
        vb = max(1e-6, (b1.x - b0.x) * (b1.y - b0.y) * (b1.z - b0.z))
        if vol > 0.55 * min(va, vb):
            continue  # contenido intencional (liquido, cap, etc.)
        collisions.append((round(vol, 4), oa.name, ob.name,
                           tuple(round(v, 3) for v in dims)))
collisions.sort(reverse=True)
print("COLLISIONS", len(collisions))
for row in collisions:
    print("  ", row)

print("AUDIT_DONE")
