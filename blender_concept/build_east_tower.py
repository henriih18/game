"""Build the northeast vertical tower and its level connectors.

Conserves the existing levels. Opens the ring north infills, builds the
east connector corridors and the 8x8 m tower with elevator shaft,
emergency ladder shaft and level slabs.
"""
import bpy
import math
import os
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
SCENE = bpy.context.scene

ZF = {1: -5.8, 2: -13.8, 3: -22.8, 4: -32.8, 5: -43.8}
CEIL = {1: -1.6, 2: -9.48, 3: -19.32, 4: -29.32, 5: -40.32}
TOWER_BOTTOM = -44.1
TOWER_TOP = -1.36
TX0, TX1 = 22.0, 30.0
TY0, TY1 = 9.0, 17.0
WALL = 0.28
TOWER_COL = None


def get_collection():
    global TOWER_COL
    c = bpy.data.collections.get("NEXUS_VTOWER")
    if c is None:
        c = bpy.data.collections.new("NEXUS_VTOWER")
        SCENE.collection.children.link(c)
    TOWER_COL = c
    return c


def mat(name):
    return bpy.data.materials.get(name)


def box(name, center, size, material, col=None, bevel=0.008):
    col = col or TOWER_COL
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
    m = mat(material) if isinstance(material, str) else material
    if m:
        mesh.materials.append(m)
    if bevel > 0:
        md = o.modifiers.new("Bevel", "BEVEL")
        md.width = bevel
        md.segments = 1
    return o


def shrink_existing(name, center, size):
    o = bpy.data.objects.get(name)
    if o is None:
        print("MISSING", name)
        return None
    o.location = center
    o.dimensions = size
    return o


def remove_object(name):
    o = bpy.data.objects.get(name)
    if o:
        bpy.data.objects.remove(o, do_unlink=True)


def build_connector(level, x_start, y0, y1, x_end=21.86, ceiling_center=None):
    """Floor/ceiling/walls for a level connector running east-west."""
    zf = ZF[level]
    zc = ceiling_center if ceiling_center is not None else CEIL[level]
    xmid = (x_start + x_end) * 0.5
    xlen = x_end - x_start
    ymid = (y0 + y1) * 0.5
    ylen = y1 - y0
    box(f"NEXUS_LINK_L{level}_FLOOR", (xmid, ymid, zf), (xlen, ylen, 0.3),
        "NEXUS_Concrete", bevel=0.02)
    box(f"NEXUS_LINK_L{level}_CEILING", (xmid, ymid, zc), (xlen, ylen, 0.24),
        "NEXUS_Concrete_Dark", bevel=0.02)
    # South wall, only east of the ring opening.
    box(f"NEXUS_LINK_L{level}_WALL_S", (xmid, y0 - WALL * 0.5, (zf + zc) * 0.5),
        (xlen, WALL, zc - zf), "NEXUS_Concrete", bevel=0.01)
    # North wall.
    box(f"NEXUS_LINK_L{level}_WALL_N", (xmid, y1 + WALL * 0.5, (zf + zc) * 0.5),
        (xlen, WALL, zc - zf), "NEXUS_Concrete", bevel=0.01)
    # Threshold strip at the tower end.
    box(f"NEXUS_LINK_L{level}_THRESH", (x_end - 0.45, ymid, zf + 0.015),
        (0.9, ylen - 0.1, 0.03), "NEXUS_Steel", bevel=0.004)
    box(f"NEXUS_LINK_L{level}_GAP", (22.0, ymid, zf + 0.012),
        (0.6, ylen - 0.1, 0.024), "NEXUS_Steel", bevel=0.003)
    # Ceiling light strip.
    box(f"NEXUS_LINK_L{level}_LIGHT", (xmid, ymid, zc - 0.13),
        (min(3.0, xlen * 0.5), 0.12, 0.05), "NEXUS_CorridorLight", bevel=0.004)
    ld = bpy.data.lights.new(f"NEXUS_LINK_L{level}_AREA", "AREA")
    ld.color = (0.62, 0.82, 1.0)
    ld.energy = 120.0
    ld.shape = "RECTANGLE"
    ld.size = min(3.0, xlen * 0.4)
    ld.size_y = 0.35
    lo = bpy.data.objects.new(ld.name, ld)
    TOWER_COL.objects.link(lo)
    lo.location = (xmid, ymid, zc - 0.2)


def build_north_leg(level, x0, x1, y0=9.0, y1=12.14):
    """North-south leg from the ring opening into the east-west connector."""
    zf = ZF[level]
    zc = CEIL[level]
    xmid = (x0 + x1) * 0.5
    ymid = (y0 + y1) * 0.5
    box(f"NEXUS_LINK_L{level}_LEG_FLOOR", (xmid, ymid, zf),
        (x1 - x0, y1 - y0, 0.3), "NEXUS_Concrete", bevel=0.02)
    box(f"NEXUS_LINK_L{level}_LEG_CEIL", (xmid, ymid, zc),
        (x1 - x0, y1 - y0, 0.24), "NEXUS_Concrete_Dark", bevel=0.02)
    # West wall of the leg.
    box(f"NEXUS_LINK_L{level}_LEG_WALL_W", (x0 - WALL * 0.5, ymid, (zf + zc) * 0.5),
        (WALL, y1 - y0, zc - zf), "NEXUS_Concrete", bevel=0.01)
    # East wall only south of the turn if the opening is narrower than the leg.
    # The leg opens directly into the east-west connector at x1.
    box(f"NEXUS_LINK_L{level}_LEG_LIGHT", (xmid, ymid, zc - 0.13),
        (0.12, min(2.6, y1 - y0), 0.05), "NEXUS_CorridorLight", bevel=0.004)
    ld = bpy.data.lights.new(f"NEXUS_LINK_L{level}_LEG_AREA", "AREA")
    ld.color = (0.62, 0.82, 1.0)
    ld.energy = 90.0
    ld.shape = "RECTANGLE"
    ld.size = 1.4
    ld.size_y = 0.3
    lo = bpy.data.objects.new(ld.name, ld)
    TOWER_COL.objects.link(lo)
    lo.location = (xmid, ymid, zc - 0.2)


def wall_segment(name, x0, x1, y, z0, z1, thickness=WALL):
    box(name, ((x0 + x1) * 0.5, y, (z0 + z1) * 0.5),
        (x1 - x0, thickness, z1 - z0), "NEXUS_Concrete", bevel=0.01)


def tower_wall_x(name, x, y0, y1, z0, z1, thickness=WALL):
    box(name, (x, (y0 + y1) * 0.5, (z0 + z1) * 0.5),
        (thickness, y1 - y0, z1 - z0), "NEXUS_Concrete", bevel=0.01)


def tower_floor(level):
    z = ZF[level]
    # Lobby slab plus narrow side strips; shafts occupy the north 3 m.
    box(f"NEXUS_VTOWER_L{level}_SLAB_S", (26.0, 11.57, z - 0.15),
        (7.72, 4.86, 0.3), "NEXUS_Concrete", bevel=0.02)
    box(f"NEXUS_VTOWER_L{level}_SLAB_W", (22.57, 15.5, z - 0.15),
        (0.86, 3.0, 0.3), "NEXUS_Concrete", bevel=0.02)
    box(f"NEXUS_VTOWER_L{level}_SLAB_E", (29.43, 15.5, z - 0.15),
        (0.86, 3.0, 0.3), "NEXUS_Concrete", bevel=0.02)
    # Lobby threshold from the west connector.
    box(f"NEXUS_VTOWER_L{level}_LOBBY_THRESH", (22.14, 10.4, z + 0.015),
        (0.28, 2.6, 0.03), "NEXUS_Steel", bevel=0.004)


def build_tower():
    # Remove any half-built tower from previous failed attempts.
    for o in list(bpy.data.objects):
        if o.name.startswith("NEXUS_VTOWER_") or o.name.startswith("NEXUS_LINK_"):
            bpy.data.objects.remove(o, do_unlink=True)

    # 1. Open the ring north infills.
    shrink_existing("NEXUS_LRING_L3_N_INFILL_0", (6.5, 9.0, -21.0), (3.0, WALL, 3.6))
    shrink_existing("NEXUS_LRING_L4_N_INFILL_0", (7.0, 9.0, -31.0), (2.0, WALL, 3.6))
    shrink_existing("NEXUS_LRING_L5_N_INFILL_0", (8.0, 9.0, -42.0), (4.0, WALL, 3.6))

    # 2. Connectors L3-L5: north leg + east-west run.
    build_north_leg(3, 8.0, 11.0)
    build_connector(3, 11.0, 9.0, 12.14)
    build_north_leg(4, 8.0, 11.0)
    build_connector(4, 11.0, 9.0, 12.14)
    build_north_leg(5, 10.0, 13.0)
    build_connector(5, 13.0, 9.0, 12.14)

    # 3. L2 connector from the east wing.
    build_connector(2, 14.0, 10.3, 13.7, ceiling_center=CEIL[2])

    # 4. L1: remove the dead-end wall, build the north corridor.
    remove_object("NEXUS_V05_CORR_END_22")
    remove_object("NEXUS_V05_CORR_END_SIGN_22_PLATE")
    remove_object("NEXUS_V05_CORR_END_SIGN_22_TEXT")
    zf, zc = ZF[1], CEIL[1]
    box("NEXUS_LINK_L1_FLOOR", (23.5, 3.65, zf), (3.0, 10.7, 0.3),
        "NEXUS_Concrete", bevel=0.02)
    box("NEXUS_LINK_L1_CEILING", (23.5, 3.65, zc), (3.0, 10.7, 0.24),
        "NEXUS_Concrete_Dark", bevel=0.02)
    box("NEXUS_LINK_L1_WALL_W", (21.86, 5.35, (zf + zc) * 0.5),
        (WALL, 7.3, zc - zf), "NEXUS_Concrete", bevel=0.01)
    box("NEXUS_LINK_L1_WALL_E", (25.14, 3.65, (zf + zc) * 0.5),
        (WALL, 10.7, zc - zf), "NEXUS_Concrete", bevel=0.01)
    box("NEXUS_LINK_L1_WALL_S", (23.5, -1.7, (zf + zc) * 0.5),
        (3.0, WALL, zc - zf), "NEXUS_Concrete", bevel=0.01)
    box("NEXUS_LINK_L1_THRESH", (23.5, 8.55, zf + 0.015),
        (2.9, 0.9, 0.03), "NEXUS_Steel", bevel=0.004)
    box("NEXUS_LINK_L1_GAP", (23.5, 9.0, zf + 0.012),
        (2.9, 0.6, 0.024), "NEXUS_Steel", bevel=0.003)
    for i, y in enumerate((-0.5, 3.5, 7.5)):
        box(f"NEXUS_LINK_L1_LIGHT_{i}", (23.5, y, zc - 0.13),
            (2.0, 0.12, 0.05), "NEXUS_CorridorLight", bevel=0.004)
        ld = bpy.data.lights.new(f"NEXUS_LINK_L1_AREA_{i}", "AREA")
        ld.color = (0.62, 0.82, 1.0)
        ld.energy = 110.0
        ld.shape = "RECTANGLE"
        ld.size = 1.8
        ld.size_y = 0.3
        lo = bpy.data.objects.new(ld.name, ld)
        TOWER_COL.objects.link(lo)
        lo.location = (23.5, y, zc - 0.2)

    # 5. Tower shell walls.
    # South wall: solid east of the L1 door; below the door and a small lintel.
    wall_segment("NEXUS_VTOWER_WALL_S_E", 25.0, 30.0, 9.0, TOWER_BOTTOM, TOWER_TOP)
    wall_segment("NEXUS_VTOWER_WALL_S_LOW", 22.0, 25.0, 9.0, TOWER_BOTTOM, ZF[1])
    wall_segment("NEXUS_VTOWER_WALL_S_LINTEL", 22.0, 25.0, 9.0, CEIL[1] - 0.12, TOWER_TOP)

    # West wall: strip north of the openings, and segmented bands with openings.
    tower_wall_x("NEXUS_VTOWER_WALL_W_N", 22.0, 13.7, 17.0, TOWER_BOTTOM, TOWER_TOP)
    # Segment below L5.
    tower_wall_x("NEXUS_VTOWER_WALL_W_0", 22.0, 9.0, 13.7, TOWER_BOTTOM, ZF[5])
    # L5 opening: floor to ceiling; solid band ceiling to L4 floor.
    tower_wall_x("NEXUS_VTOWER_WALL_W_5B", 22.0, 9.0, 13.7, CEIL[5], ZF[4])
    # L4 opening; band to L3.
    tower_wall_x("NEXUS_VTOWER_WALL_W_4B", 22.0, 9.0, 13.7, CEIL[4], ZF[3])
    # L3 opening; band to L2.
    tower_wall_x("NEXUS_VTOWER_WALL_W_3B", 22.0, 9.0, 13.7, CEIL[3], ZF[2])
    # L2 opening; band to L1.
    tower_wall_x("NEXUS_VTOWER_WALL_W_2B", 22.0, 9.0, 13.7, CEIL[2], ZF[1])
    # L1 west wall solid.
    tower_wall_x("NEXUS_VTOWER_WALL_W_1", 22.0, 9.0, 13.7, ZF[1], TOWER_TOP)

    # North and east walls, solid.
    wall_segment("NEXUS_VTOWER_WALL_N", 22.0, 30.0, 17.0, TOWER_BOTTOM, TOWER_TOP)
    tower_wall_x("NEXUS_VTOWER_WALL_E", 30.0, 9.0, 17.0, TOWER_BOTTOM, TOWER_TOP)

    # Roof.
    box("NEXUS_VTOWER_ROOF", (26.0, 13.0, -1.48), (8.0, 8.0, 0.24),
        "NEXUS_Concrete_Dark", bevel=0.02)

    # 6. Level slabs.
    for level in (1, 2, 3, 4, 5):
        tower_floor(level)

    # 7. Elevator shaft (x 26..29, y 14..17).
    ex0, ex1, ey0, ey1 = 26.0, 29.0, 14.0, 17.0
    shaft_h = TOWER_TOP - TOWER_BOTTOM
    for nm, x, y, sx, sy in (
        ("W", ex0, 15.5, 0.2, 3.0),
        ("E", ex1, 15.5, 0.2, 3.0),
    ):
        box(f"NEXUS_VTOWER_ELEV_WALL_{nm}", (x, y, (TOWER_BOTTOM + TOWER_TOP) * 0.5),
            (sx, sy, shaft_h), "NEXUS_Concrete", bevel=0.008)
    # South shaft wall with door openings at every level.
    for level in (1, 2, 3, 4, 5):
        zf = ZF[level]
        zc = CEIL[level]
        # side pieces and lintel around a 1.6 m door.
        box(f"NEXUS_VTOWER_ELEV_DOOR_L{level}_L", (26.5, ey0, (zf + zc) * 0.5),
            (0.5, 0.2, zc - zf), "NEXUS_Steel", bevel=0.006)
        box(f"NEXUS_VTOWER_ELEV_DOOR_L{level}_R", (28.5, ey0, (zf + zc) * 0.5),
            (0.5, 0.2, zc - zf), "NEXUS_Steel", bevel=0.006)
        box(f"NEXUS_VTOWER_ELEV_DOOR_L{level}_TOP", (27.5, ey0, zc - 0.2),
            (1.6, 0.2, 0.4), "NEXUS_Steel", bevel=0.006)
        # Sliding leaves, slightly inset.
        box(f"NEXUS_VTOWER_ELEV_LEAF_L{level}", (27.1, ey0 - 0.13, (zf + zc) * 0.5),
            (0.72, 0.06, 2.2), "NEXUS_Painted_Metal", bevel=0.008)
        box(f"NEXUS_VTOWER_ELEV_LEAF_R{level}", (27.9, ey0 - 0.13, (zf + zc) * 0.5),
            (0.72, 0.06, 2.2), "NEXUS_Painted_Metal", bevel=0.008)
        # Call plate and indicator.
        box(f"NEXUS_VTOWER_ELEV_CALL_{level}", (28.9, ey0 - 0.15, zf + 1.1),
            (0.12, 0.04, 0.22), "NEXUS_Amber", bevel=0.004)
        box(f"NEXUS_VTOWER_ELEV_IND_{level}", (28.9, ey0 - 0.15, zf + 1.45),
            (0.22, 0.03, 0.08), "NEXUS_Screen", bevel=0.002)

    # 8. Stair shaft (x 23..26, y 12..15) and emergency ladder.
    sx0, sx1, sy0, sy1 = 23.0, 26.0, 14.0, 17.0
    for nm, x, y, sx, sy in (
        ("W", sx0, 15.5, 0.2, 3.0),
    ):
        box(f"NEXUS_VTOWER_STAIR_WALL_{nm}", (x, y, (TOWER_BOTTOM + TOWER_TOP) * 0.5),
            (sx, sy, shaft_h), "NEXUS_Concrete", bevel=0.008)
    # South wall with a door opening at each level.
    for level in (1, 2, 3, 4, 5):
        zf = ZF[level]
        zc = CEIL[level]
        box(f"NEXUS_VTOWER_STAIR_DOOR_L{level}_L", (23.6, sy0, (zf + zc) * 0.5),
            (0.4, 0.2, zc - zf), "NEXUS_Concrete", bevel=0.006)
        box(f"NEXUS_VTOWER_STAIR_DOOR_L{level}_R", (25.4, sy0, (zf + zc) * 0.5),
            (0.4, 0.2, zc - zf), "NEXUS_Concrete", bevel=0.006)
        box(f"NEXUS_VTOWER_STAIR_DOOR_L{level}_TOP", (24.5, sy0, zc - 0.2),
            (1.4, 0.2, 0.4), "NEXUS_Concrete", bevel=0.006)
        # Steel door leaf against the wall, open inward.
        box(f"NEXUS_VTOWER_STAIR_LEAF_{level}", (25.15, sy0 + 0.55, zf + 1.15),
            (0.06, 1.1, 2.2), "NEXUS_Painted_Metal", bevel=0.008)
        box(f"NEXUS_VTOWER_STAIR_SIGN_{level}", (24.5, sy0 - 0.11, zc - 0.45),
            (0.8, 0.04, 0.18), "NEXUS_SignText", bevel=0.004)

    # Continuous ladder in the stair shaft.
    lx, ly = 24.5, 15.5
    z0, z1 = ZF[5], ZF[1]
    for i, x in enumerate((lx - 0.28, lx + 0.28)):
        box(f"NEXUS_VTOWER_LADDER_RAIL_{i}", (x, ly, (z0 + z1) * 0.5),
            (0.06, 0.06, z1 - z0), "NEXUS_Steel", bevel=0.004)
    count = int((z1 - z0) / 0.3)
    for i in range(count + 1):
        z = z0 + i * 0.3
        box(f"NEXUS_VTOWER_LADDER_RUNG_{i}", (lx, ly, z),
            (0.5, 0.04, 0.04), "NEXUS_Steel", bevel=0.003)
    # Landing at each floor.
    for level in (1, 2, 3, 4, 5):
        zf = ZF[level]
        box(f"NEXUS_VTOWER_LANDING_{level}", (24.5, 14.6, zf + 0.02),
            (1.6, 1.2, 0.04), "NEXUS_Steel", bevel=0.004)
        box(f"NEXUS_VTOWER_LANDING_RAIL_{level}", (24.5, 14.2, zf + 0.55),
            (1.6, 0.05, 1.0), "NEXUS_Painted_Metal", bevel=0.004)
        ld = bpy.data.lights.new(f"NEXUS_VTOWER_STAIR_LIGHT_{level}", "POINT")
        ld.color = (1.0, 0.08, 0.04)
        ld.energy = 35.0
        ld.shadow_soft_size = 0.2
        lo = bpy.data.objects.new(ld.name, ld)
        TOWER_COL.objects.link(lo)
        lo.location = (24.5, 14.45, zf + 2.6)
        box(f"NEXUS_VTOWER_STAIR_LAMP_{level}", (24.5, 14.46, zf + 2.6),
            (0.2, 0.06, 0.1), "NEXUS_Red", bevel=0.003)

    # 9. Lobby lights and signage.
    for level in (1, 2, 3, 4, 5):
        zf = ZF[level]
        zc = CEIL[level]
        box(f"NEXUS_VTOWER_LOBBY_LIGHT_{level}", (24.0, 10.5, zc - 0.13),
            (2.2, 0.12, 0.05), "NEXUS_CorridorLight", bevel=0.004)
        ld = bpy.data.lights.new(f"NEXUS_VTOWER_LOBBY_AREA_{level}", "AREA")
        ld.color = (0.72, 0.84, 1.0)
        ld.energy = 180.0
        ld.shape = "RECTANGLE"
        ld.size = 2.0
        ld.size_y = 0.3
        lo = bpy.data.objects.new(ld.name, ld)
        TOWER_COL.objects.link(lo)
        lo.location = (24.0, 10.5, zc - 0.2)
        box(f"NEXUS_VTOWER_LEVEL_PLATE_{level}", (22.15, 9.55, zf + 2.9),
            (0.05, 0.8, 0.22), "NEXUS_SignPlate", bevel=0.004)
        box(f"NEXUS_VTOWER_LEVEL_TEXT_{level}", (22.12, 9.55, zf + 2.9),
            (0.02, 0.55, 0.12), "NEXUS_SignText", bevel=0.002)

    # Elevator car at L1, for visual reference.
    zf = ZF[1]
    box("NEXUS_VTOWER_CAR_FLOOR", (27.5, 15.5, zf + 0.08), (2.4, 2.4, 0.08),
        "NEXUS_Steel", bevel=0.006)
    box("NEXUS_VTOWER_CAR_CEIL", (27.5, 15.5, zf + 2.35), (2.4, 2.4, 0.08),
        "NEXUS_Steel", bevel=0.006)
    for i, (x, y, sx, sy) in enumerate(((27.5, 14.35, 2.4, 0.06), (27.5, 16.65, 2.4, 0.06),
                                        (26.35, 15.5, 0.06, 2.4), (28.65, 15.5, 0.06, 2.4))):
        box(f"NEXUS_VTOWER_CAR_WALL_{i}", (x, y, zf + 1.2), (sx, sy, 2.2),
            "NEXUS_Painted_Metal", bevel=0.004)
    box("NEXUS_VTOWER_CAR_DOOR", (27.5, 14.32, zf + 1.2), (1.4, 0.05, 2.1),
        "NEXUS_Steel", bevel=0.004)


def main():
    get_collection()
    build_tower()
    SCENE.camera = bpy.data.objects.get("NEXUS_V05_CAM_Corridor")
    path = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V05_level1_v28.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path)
    print("EAST_TOWER_SAVED", path, os.path.getsize(path))


if __name__ == "__main__":
    main()
