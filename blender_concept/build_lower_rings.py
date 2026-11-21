"""Build clean ring circulation for NEXUS lower levels 3-5.

The old diagonal corridors were hidden in rebuild_lower_a.py. This script
creates an orthogonal ring around a central service block on each level,
with outer wall infill between the existing rooms, ceiling, lights and
door thresholds. It does not touch the rooms themselves.
"""
import bpy
import math
import os
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
OUT = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V05_level1_v25.blend")

Z = {3: -22.8, 4: -32.8, 5: -43.8}
RING = {
    3: dict(out_x=11.0, out_y=9.0, in_x=8.0, in_y=6.0, rooms=[
        "ENFERMERIA", "HABITACIONES_MEDICAS", "QUIROFANO", "MORGUE",
        "CAMARAS_FRIGORIFICAS", "AISLAMIENTO_A", "AISLAMIENTO_B"]),
    4: dict(out_x=11.0, out_y=9.0, in_x=8.0, in_y=6.0, rooms=[
        "ARMERIA_HERRAMIENTAS", "BUNKER_SEGURIDAD", "CONTENCION_PRIMARIA",
        "CONTENCION_SECUNDARIA", "CONTROL_CONTENCION", "LAB_RESTRINGIDO"]),
    5: dict(out_x=13.0, out_y=9.0, in_x=10.0, in_y=6.0, rooms=[
        "ARCHIVO_SECRETO", "BOMBEO_INUNDACION", "EXTRACCION_PROFUNDA",
        "GENERADORES", "REFRIGERACION", "TUNEL_PROFUNDO"]),
}

SCENE = bpy.context.scene


def collection(name, parent):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        parent.children.link(c)
    return c


TOP = collection("NEXUS_LOWER_CIRCULATION", SCENE.collection)


def mat(name, fallback="NEXUS_Concrete"):
    return bpy.data.materials.get(name) or bpy.data.materials.get(fallback)


def box(name, center, size, material, col, bevel=0.008):
    mesh = bpy.data.meshes.new(name)
    x, y, z = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
    verts = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
             (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
             (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    col.objects.link(o)
    o.location = center
    m = material if isinstance(material, bpy.types.Material) else mat(material)
    if m:
        mesh.materials.append(m)
    if bevel > 0:
        md = o.modifiers.new("Bevel", "BEVEL")
        md.width = bevel
        md.segments = 1
    return o


def world_bounds(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return (min(p.x for p in pts), max(p.x for p in pts),
            min(p.y for p in pts), max(p.y for p in pts))


def room_spans(level, axis, value):
    """Return room spans crossing a ring boundary line."""
    spans = []
    for prefix in RING[level]["rooms"]:
        floor = bpy.data.objects.get(prefix + "_FLOOR")
        if floor is None:
            print("MISSING_FLOOR", prefix)
            continue
        x0, x1, y0, y1 = world_bounds(floor)
        if axis == "x":  # boundary is a vertical line x=value
            if x0 <= value + 0.03 and x1 >= value - 0.03:
                spans.append((y0, y1))
        else:  # boundary is a horizontal line y=value
            if y0 <= value + 0.03 and y1 >= value - 0.03:
                spans.append((x0, x1))
    return spans


def complement(spans, lo, hi):
    spans = sorted((max(lo, a), min(hi, b)) for a, b in spans if b > lo and a < hi)
    merged = []
    for a, b in spans:
        if not merged or a > merged[-1][1] + 1e-4:
            merged.append([a, b])
        else:
            merged[-1][1] = max(merged[-1][1], b)
    gaps = []
    cur = lo
    for a, b in merged:
        if a - cur > 0.05:
            gaps.append((cur, a))
        cur = max(cur, b)
    if hi - cur > 0.05:
        gaps.append((cur, hi))
    return gaps


def wall(name, center, size, col):
    return box(name, center, size, "NEXUS_Concrete", col, 0.012)


def outer_walls(level, cfg, z, col):
    ox, oy = cfg["out_x"], cfg["out_y"]
    h = 3.6
    zc = z + h * 0.5
    # North/south infill between rooms.
    for side, y in (("N", oy), ("S", -oy)):
        spans = room_spans(level, "y", y)
        for i, (a, b) in enumerate(complement(spans, -ox, ox)):
            wall(f"NEXUS_LRING_L{level}_{side}_INFILL_{i}", ((a + b) * 0.5, y, zc),
                 (b - a, 0.28, h), col)
    # East/west infill between rooms.
    for side, x in (("E", ox), ("W", -ox)):
        spans = room_spans(level, "x", x)
        for i, (a, b) in enumerate(complement(spans, -oy, oy)):
            wall(f"NEXUS_LRING_L{level}_{side}_INFILL_{i}", (x, (a + b) * 0.5, zc),
                 (0.28, b - a, h), col)


def inner_walls(level, cfg, z, col):
    ix, iy = cfg["in_x"], cfg["in_y"]
    h = 3.6
    zc = z + h * 0.5
    # Door opening on the north inner wall, centred at x=0, 2 m wide.
    wall(f"NEXUS_LRING_L{level}_INNER_N_A", (-(ix + 1.0) * 0.5, iy, zc),
         (ix - 1.0, 0.28, h), col)
    wall(f"NEXUS_LRING_L{level}_INNER_N_B", ((ix + 1.0) * 0.5, iy, zc),
         (ix - 1.0, 0.28, h), col)
    box(f"NEXUS_LRING_L{level}_INNER_N_LINTEL", (0.0, iy, z + 3.0),
        (2.0, 0.28, 1.2), mat("NEXUS_Concrete"), col, 0.01)
    wall(f"NEXUS_LRING_L{level}_INNER_S", (0.0, -iy, zc), (2 * ix, 0.28, h), col)
    wall(f"NEXUS_LRING_L{level}_INNER_E", (ix, 0.0, zc), (0.28, 2 * iy, h), col)
    wall(f"NEXUS_LRING_L{level}_INNER_W", (-ix, 0.0, zc), (0.28, 2 * iy, h), col)


def floors_and_ceilings(level, cfg, z, col):
    ox, oy, ix, iy = cfg["out_x"], cfg["out_y"], cfg["in_x"], cfg["in_y"]
    # Ring floor: four bands, touching but not overlapping the rooms.
    box(f"NEXUS_LRING_L{level}_FLOOR_N", (0, (iy + oy) * 0.5, z),
        (2 * ox, oy - iy, 0.3), mat("NEXUS_Concrete"), col, 0.015)
    box(f"NEXUS_LRING_L{level}_FLOOR_S", (0, -(iy + oy) * 0.5, z),
        (2 * ox, oy - iy, 0.3), mat("NEXUS_Concrete"), col, 0.015)
    box(f"NEXUS_LRING_L{level}_FLOOR_E", ((ix + ox) * 0.5, 0, z),
        (ox - ix, 2 * iy, 0.3), mat("NEXUS_Concrete"), col, 0.015)
    box(f"NEXUS_LRING_L{level}_FLOOR_W", (-(ix + ox) * 0.5, 0, z),
        (ox - ix, 2 * iy, 0.3), mat("NEXUS_Concrete"), col, 0.015)
    # Central block floor/ceiling, prepared for later fit-out.
    box(f"NEXUS_LRING_L{level}_CENTRAL_FLOOR", (0, 0, z),
        (2 * ix, 2 * iy, 0.3), mat("NEXUS_Concrete_Dark"), col, 0.015)
    # Ceilings.
    zc = z + 3.6
    box(f"NEXUS_LRING_L{level}_CEIL_N", (0, (iy + oy) * 0.5, zc),
        (2 * ox, oy - iy, 0.24), mat("NEXUS_Concrete_Dark"), col, 0.01)
    box(f"NEXUS_LRING_L{level}_CEIL_S", (0, -(iy + oy) * 0.5, zc),
        (2 * ox, oy - iy, 0.24), mat("NEXUS_Concrete_Dark"), col, 0.01)
    box(f"NEXUS_LRING_L{level}_CEIL_E", ((ix + ox) * 0.5, 0, zc),
        (ox - ix, 2 * iy, 0.24), mat("NEXUS_Concrete_Dark"), col, 0.01)
    box(f"NEXUS_LRING_L{level}_CEIL_W", (-(ix + ox) * 0.5, 0, zc),
        (ox - ix, 2 * iy, 0.24), mat("NEXUS_Concrete_Dark"), col, 0.01)
    box(f"NEXUS_LRING_L{level}_CENTRAL_CEIL", (0, 0, zc),
        (2 * ix, 2 * iy, 0.24), mat("NEXUS_Concrete_Dark"), col, 0.01)


def lights(level, cfg, z, col):
    ox, oy, ix, iy = cfg["out_x"], cfg["out_y"], cfg["in_x"], cfg["in_y"]
    zc = z + 3.38
    positions = []
    for x in (-ox + 2.0, -ox * 0.35, ox * 0.35, ox - 2.0):
        positions.append((x, (iy + oy) * 0.5, 0))
        positions.append((x, -(iy + oy) * 0.5, 0))
    for y in (-iy + 1.5, 0, iy - 1.5):
        positions.append(((ix + ox) * 0.5, y, 1))
        positions.append((-(ix + ox) * 0.5, y, 1))
    for i, (x, y, rot) in enumerate(positions):
        ld = bpy.data.lights.new(f"NEXUS_LRING_L{level}_LIGHT_{i}", "AREA")
        ld.energy = 90.0
        ld.color = (0.62, 0.78, 0.95)
        ld.shape = "RECTANGLE"
        ld.size = 1.8
        ld.size_y = 0.18
        lo = bpy.data.objects.new(ld.name, ld)
        col.objects.link(lo)
        lo.location = (x, y, zc)
        if rot:
            lo.rotation_euler.z = math.pi / 2
        box(f"NEXUS_LRING_L{level}_STRIP_{i}", (x, y, zc + 0.02),
            (1.7, 0.09, 0.04) if not rot else (0.09, 1.7, 0.04),
            "NEXUS_CorridorLight", col, 0.004)
    # Red emergency beacons at four corners.
    for i, (x, y) in enumerate(((-ox + 0.5, oy - 0.5), (ox - 0.5, oy - 0.5),
                                 (-ox + 0.5, -oy + 0.5), (ox - 0.5, -oy + 0.5))):
        ld = bpy.data.lights.new(f"NEXUS_LRING_L{level}_EMERG_{i}", "POINT")
        ld.energy = 28.0
        ld.color = (1.0, 0.03, 0.02)
        ld.shadow_soft_size = 0.2
        lo = bpy.data.objects.new(ld.name, ld)
        col.objects.link(lo)
        lo.location = (x, y, z + 3.0)
        box(f"NEXUS_LRING_L{level}_EMERG_HOUSING_{i}", (x, y, z + 3.0),
            (0.28, 0.16, 0.16), "NEXUS_Painted_Metal", col, 0.006)


def door_thresholds(level, cfg, z, col):
    ox, oy = cfg["out_x"], cfg["out_y"]
    for prefix in RING[level]["rooms"]:
        frames = [o for o in bpy.data.objects
                  if o.name.startswith(prefix + "_DOOR_FRAME")
                  and not o.name.endswith("_TOP") and not o.hide_render]
        if len(frames) < 2:
            print("NO_FRAMES", prefix)
            continue
        p0 = frames[0].matrix_world.translation
        p1 = frames[1].matrix_world.translation
        if abs(p0.x - p1.x) > abs(p0.y - p1.y):
            # Door in a horizontal wall; threshold runs along X.
            cx = (p0.x + p1.x) * 0.5
            cy = p0.y
            if cy > 0:
                cy -= 0.07
            else:
                cy += 0.07
            box(f"NEXUS_LRING_L{level}_THRESH_{prefix}", (cx, cy, z + 0.02),
                (1.84, 0.16, 0.04), "NEXUS_Amber", col, 0.004)
        else:
            # Door in a vertical wall; threshold runs along Y.
            cx = p0.x
            cy = (p0.y + p1.y) * 0.5
            if cx > 0:
                cx -= 0.07
            else:
                cx += 0.07
            box(f"NEXUS_LRING_L{level}_THRESH_{prefix}", (cx, cy, z + 0.02),
                (0.16, 1.84, 0.04), "NEXUS_Amber", col, 0.004)


def baseboards(level, cfg, z, col):
    ox, oy, ix, iy = cfg["out_x"], cfg["out_y"], cfg["in_x"], cfg["in_y"]
    # Thin dark base along the inner walls, kept clear of the door opening.
    box(f"NEXUS_LRING_L{level}_BASE_INNER_N_A", (-(ix + 1.0) * 0.5, iy - 0.15, z + 0.12),
        (ix - 1.0, 0.06, 0.18), "NEXUS_Painted_Metal", col, 0.003)
    box(f"NEXUS_LRING_L{level}_BASE_INNER_N_B", ((ix + 1.0) * 0.5, iy - 0.15, z + 0.12),
        (ix - 1.0, 0.06, 0.18), "NEXUS_Painted_Metal", col, 0.003)
    box(f"NEXUS_LRING_L{level}_BASE_INNER_S", (0, -iy + 0.15, z + 0.12),
        (2 * ix, 0.06, 0.18), "NEXUS_Painted_Metal", col, 0.003)


def main():
    # Remove any partial result from a previous failed run.
    for o in list(bpy.data.objects):
        if o.name.startswith("NEXUS_LRING_"):
            bpy.data.objects.remove(o, do_unlink=True)
    for level in (3, 4, 5):
        cfg = RING[level]
        z = Z[level]
        col = collection(f"NEXUS_LRING_L{level}", TOP)
        floors_and_ceilings(level, cfg, z, col)
        outer_walls(level, cfg, z, col)
        inner_walls(level, cfg, z, col)
        lights(level, cfg, z, col)
        door_thresholds(level, cfg, z, col)
        baseboards(level, cfg, z, col)
        print("RING_BUILT", level, cfg["out_x"], cfg["out_y"], cfg["in_x"], cfg["in_y"])
    bpy.ops.wm.save_as_mainfile(filepath=OUT)
    print("RINGS_SAVED", OUT, os.path.getsize(OUT))


if __name__ == "__main__":
    main()
