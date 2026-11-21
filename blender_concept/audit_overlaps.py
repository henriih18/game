"""Audit real floor-footprint overlaps using oriented bounding boxes."""
import bpy
import json
import sys
from mathutils import Vector


def visible(o):
    if o.hide_render:
        return False
    for c in o.users_collection:
        if c.hide_render:
            return False
    return True


def convex_hull(points):
    pts = sorted(set((round(p[0], 5), round(p[1], 5)) for p in points))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def poly_area(poly):
    if len(poly) < 3:
        return 0.0
    s = 0.0
    for i, p in enumerate(poly):
        q = poly[(i + 1) % len(poly)]
        s += p[0] * q[1] - q[0] * p[1]
    return abs(s) * 0.5


def inside(p, a, b):
    return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) >= -1e-9


def line_intersect(s, e, a, b):
    x1, y1 = s
    x2, y2 = e
    x3, y3 = a
    x4, y4 = b
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(den) < 1e-12:
        return e
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


def clip(subject, clip_poly):
    output = subject
    if not output:
        return []
    for i, a in enumerate(clip_poly):
        b = clip_poly[(i + 1) % len(clip_poly)]
        inp = output
        output = []
        if not inp:
            break
        s = inp[-1]
        for e in inp:
            if inside(e, a, b):
                if not inside(s, a, b):
                    output.append(line_intersect(s, e, a, b))
                output.append(e)
            elif inside(s, a, b):
                output.append(line_intersect(s, e, a, b))
            s = e
    return output


def footprint(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return convex_hull([(p.x, p.y) for p in pts])


def audit(zmin, zmax, prefix=None, threshold=0.01):
    floors = []
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.endswith("_FLOOR") or not visible(o):
            continue
        if prefix and not o.name.startswith(prefix):
            continue
        z = (o.matrix_world.translation.z)
        if zmin <= z <= zmax:
            floors.append(o)
    print("FLOORS", len(floors))
    rows = []
    for i, a in enumerate(floors):
        pa = footprint(a)
        aa = poly_area(pa)
        for b in floors[i + 1:]:
            pb = footprint(b)
            inter = clip(pa, pb)
            area = poly_area(inter)
            if area > threshold:
                rows.append({
                    "a": a.name,
                    "b": b.name,
                    "area": round(area, 3),
                    "a_area": round(aa, 2),
                    "b_area": round(poly_area(pb), 2),
                })
    rows.sort(key=lambda r: r["area"], reverse=True)
    print("OVERLAPS", len(rows))
    for r in rows:
        print(r["area"], r["a"], r["b"])
    return rows


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) >= 2:
        zmin, zmax = float(args[0]), float(args[1])
        prefix = args[2] if len(args) > 2 and args[2] != "-" else None
        out = args[3] if len(args) > 3 else "/tmp/opencode/floor_overlaps.json"
        rows = audit(zmin, zmax, prefix)
        with open(out, "w") as f:
            json.dump(rows, f, indent=2)
        print("WROTE", out)
    else:
        print("usage: -- zmin zmax prefix|- out.json")
