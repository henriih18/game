"""Basic functional fit-out for the L3-L5 central blocks."""
import bpy
import math
import os

ROOT = "/home/riyo/Documentos/game"
COL = bpy.data.collections.get("NEXUS_CENTRAL")
if COL is None:
    COL = bpy.data.collections.new("NEXUS_CENTRAL")
    bpy.context.scene.collection.children.link(COL)

Z = {3: -22.8, 4: -32.8, 5: -43.8}
H = 3.6


def mat(name):
    return bpy.data.materials.get(name)


def box(name, center, size, material, bevel=0.008):
    mesh = bpy.data.meshes.new(name)
    x, y, z = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
    verts = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
             (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
             (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    COL.objects.link(o)
    o.location = center
    m = mat(material) if isinstance(material, str) else material
    if m:
        mesh.materials.append(m)
    if bevel > 0:
        md = o.modifiers.new("Bevel", "BEVEL")
        md.width = bevel
        md.segments = 1
    return o


def cyl(name, center, radius, depth, material, axis="Z", verts=20):
    mesh = bpy.data.meshes.new(name)
    vl = []
    for z in (-depth / 2, depth / 2):
        for i in range(verts):
            a = 2 * math.pi * i / verts
            vl.append((math.cos(a) * radius, math.sin(a) * radius, z))
    fs = []
    for i in range(verts):
        j = (i + 1) % verts
        fs.append((i, j, verts + j, verts + i))
    fs.append(tuple(range(verts - 1, -1, -1)))
    fs.append(tuple(range(verts, verts * 2)))
    mesh.from_pydata(vl, [], fs)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    COL.objects.link(o)
    o.location = center
    if axis == "X":
        o.rotation_euler.y = math.pi / 2
    elif axis == "Y":
        o.rotation_euler.x = math.pi / 2
    m = mat(material) if isinstance(material, str) else material
    if m:
        mesh.materials.append(m)
    return o


def light(name, loc, energy, color=(0.62, 0.82, 1.0), size=2.0):
    ld = bpy.data.lights.new(name, "AREA")
    ld.color = color
    ld.energy = energy
    ld.shape = "RECTANGLE"
    ld.size = size
    ld.size_y = 0.35
    lo = bpy.data.objects.new(ld.name, ld)
    COL.objects.link(lo)
    lo.location = loc


def panel(name, loc, size, material="NEXUS_CorridorLight"):
    box(name, loc, size, material, 0.004)


def strip_light(name, x, y, z, length=2.0):
    panel(name + "_LAMP", (x, y, z), (length, 0.12, 0.05))
    light(name + "_AREA", (x, y, z - 0.1), 260.0, size=length * 0.8)


def central_door(level):
    z = Z[level]
    box(f"NEXUS_CB_L{level}_DOOR_THRESH", (0.0, 5.92, z + 0.015),
        (2.0, 0.45, 0.03), "NEXUS_Steel", 0.004)
    for i, hinge_x in enumerate((-1.0, 1.0)):
        if hinge_x < 0:
            dx, dy = 0.5, -0.866
        else:
            dx, dy = -0.5, -0.866
        leaf_len = 0.95
        cx = hinge_x + dx * leaf_len * 0.5
        cy = 5.92 + dy * leaf_len * 0.5
        leaf = box(f"NEXUS_CB_L{level}_DOOR_LEAF_{i}", (cx, cy, z + 1.65),
                   (leaf_len, 0.07, 3.0), "NEXUS_Painted_Metal", 0.008)
        leaf.rotation_euler[2] = math.atan2(dy, dx)
        box(f"NEXUS_CB_L{level}_DOOR_HINGE_{i}", (hinge_x, 5.92, z + 1.65),
            (0.08, 0.08, 3.05), "NEXUS_Steel", 0.004)
        hx = hinge_x + dx * (leaf_len - 0.14)
        hy = 5.92 + dy * (leaf_len - 0.14)
        box(f"NEXUS_CB_L{level}_DOOR_HANDLE_{i}", (hx, hy, z + 1.45),
            (0.05, 0.05, 0.28), "NEXUS_Steel", 0.003)
    box(f"NEXUS_CB_L{level}_DOOR_SIGN", (0.0, 5.8, z + 3.08),
        (1.2, 0.05, 0.22), "NEXUS_SignText", 0.004)


def clean():
    for o in list(bpy.data.objects):
        if o.name.startswith(("NEXUS_CB_", "TMP_")):
            bpy.data.objects.remove(o, do_unlink=True)


def decon_l3():
    z = Z[3]
    # Partition north/south with a central 2 m door.
    box("NEXUS_CB_L3_PART_W", (-4.5, 2.0, z + 1.8), (7.0, 0.2, H), "NEXUS_Clinical", 0.01)
    box("NEXUS_CB_L3_PART_E", (4.5, 2.0, z + 1.8), (7.0, 0.2, H), "NEXUS_Clinical", 0.01)
    box("NEXUS_CB_L3_PART_LINTEL", (0.0, 2.0, z + 3.35), (2.0, 0.2, 0.5), "NEXUS_Clinical", 0.01)
    # Shower bays along the south wall.
    for i, x in enumerate((-6.0, -2.0, 2.0, 6.0)):
        box(f"NEXUS_CB_L3_SHOWER_DIV_{i}", (x, -4.9, z + 1.5), (0.12, 1.8, 2.8), "NEXUS_Clinical", 0.006)
        cyl(f"NEXUS_CB_L3_SHOWER_HEAD_{i}", (x, -5.55, z + 2.55), 0.09, 0.12, "NEXUS_Steel", "Y", 12)
        box(f"NEXUS_CB_L3_DRAIN_{i}", (x, -5.25, z + 0.02), (0.6, 0.6, 0.03), "NEXUS_Steel", 0.004)
        box(f"NEXUS_CB_L3_TILE_{i}", (x, -5.75, z + 1.4), (2.0, 0.04, 2.6), "NEXUS_Clinical", 0.004)
    # Bench and lockers on the north side.
    box("NEXUS_CB_L3_BENCH", (-5.0, 4.6, z + 0.45), (3.0, 0.8, 0.1), "NEXUS_Painted_Metal", 0.01)
    for i in range(3):
        box(f"NEXUS_CB_L3_LOCKER_{i}", (-7.2, 3.0 + i * 0.9, z + 1.2),
            (0.5, 0.8, 2.2), "NEXUS_Painted_Metal", 0.008)
    # Sinks and cabinets on the east.
    for i, y in enumerate((3.0, 4.5)):
        box(f"NEXUS_CB_L3_SINK_{i}", (7.2, y, z + 0.9), (0.8, 1.0, 0.12), "NEXUS_Clinical", 0.008)
        box(f"NEXUS_CB_L3_SINK_BASE_{i}", (7.2, y, z + 0.45), (0.6, 0.7, 0.9), "NEXUS_Clinical", 0.008)
    # Supply shelves.
    for i in range(2):
        box(f"NEXUS_CB_L3_SHELF_{i}", (-6.2, 5.3, z + 0.8 + i * 1.0),
            (2.2, 0.5, 0.08), "NEXUS_Steel", 0.006)
    # Lighting.
    for i, (x, y) in enumerate(((-4.0, 4.5), (4.0, 4.5), (-4.0, -1.5), (4.0, -1.5),
                                (0.0, 4.5), (0.0, 0.0), (0.0, -3.5))):
        strip_light(f"NEXUS_CB_L3_LIGHT_{i}", x, y, z + 3.25, 2.0)
    # Hazard sign strip at the door.
    box("NEXUS_CB_L3_HAZ", (0.0, 1.88, z + 0.02), (2.2, 0.12, 0.02), "NEXUS_Amber", 0.002)


def security_l4():
    z = Z[4]
    # Mantrap walls and scanner.
    box("NEXUS_CB_L4_MANT_W", (-2.0, 4.4, z + 1.8), (0.2, 3.2, H), "NEXUS_Concrete_Dark", 0.01)
    box("NEXUS_CB_L4_MANT_E", (2.0, 4.4, z + 1.8), (0.2, 3.2, H), "NEXUS_Concrete_Dark", 0.01)
    box("NEXUS_CB_L4_MANT_LINTEL", (0.0, 4.4, z + 3.35), (4.0, 0.2, 0.5), "NEXUS_Concrete_Dark", 0.01)
    box("NEXUS_CB_L4_SCANNER_L", (-1.0, 4.4, z + 1.4), (0.18, 0.35, 2.8), "NEXUS_Steel", 0.006)
    box("NEXUS_CB_L4_SCANNER_R", (1.0, 4.4, z + 1.4), (0.18, 0.35, 2.8), "NEXUS_Steel", 0.006)
    box("NEXUS_CB_L4_SCANNER_TOP", (0.0, 4.4, z + 2.85), (2.0, 0.35, 0.2), "NEXUS_Steel", 0.006)
    # Control booth, east side.
    box("NEXUS_CB_L4_BOOTH_W", (3.0, 0.0, z + 1.8), (0.15, 4.0, H), "NEXUS_Concrete_Dark", 0.008)
    box("NEXUS_CB_L4_BOOTH_N", (5.5, 2.0, z + 1.8), (5.0, 0.15, H), "NEXUS_Concrete_Dark", 0.008)
    box("NEXUS_CB_L4_BOOTH_S", (5.5, -2.0, z + 1.8), (5.0, 0.15, H), "NEXUS_Concrete_Dark", 0.008)
    box("NEXUS_CB_L4_BOOTH_DOOR", (3.0, -1.2, z + 1.1), (0.12, 0.9, 2.2), "NEXUS_Steel", 0.006)
    box("NEXUS_CB_L4_BOOTH_CONSOLE", (5.5, 0.0, z + 0.9), (3.0, 1.2, 0.12), "NEXUS_Steel", 0.008)
    for i, x in enumerate((4.5, 5.5, 6.5)):
        box(f"NEXUS_CB_L4_BOOTH_MON_{i}", (x, 0.35, z + 1.5), (0.55, 0.05, 0.4), "NEXUS_MonitorScreen", 0.004)
    # Holding bench and lockers west.
    box("NEXUS_CB_L4_BENCH", (-4.5, 0.0, z + 0.45), (3.0, 0.8, 0.1), "NEXUS_Painted_Metal", 0.01)
    for i in range(4):
        box(f"NEXUS_CB_L4_LOCKER_{i}", (-7.2, -2.4 + i * 1.2, z + 1.2),
            (0.5, 0.9, 2.2), "NEXUS_Painted_Metal", 0.008)
    # Security camera and red beacons.
    box("NEXUS_CB_L4_CAM", (0.0, 5.7, z + 3.0), (0.35, 0.3, 0.22), "NEXUS_Steel", 0.006)
    for i, x in enumerate((-3.0, 3.0)):
        box(f"NEXUS_CB_L4_BEACON_{i}", (x, 5.8, z + 3.1), (0.16, 0.1, 0.12), "NEXUS_Red", 0.003)
    # Lighting.
    for i, (x, y) in enumerate(((-4.0, 4.5), (5.0, 4.5), (-4.0, -4.0), (5.0, -4.0),
                                (0.0, 4.5), (0.0, 0.0), (0.0, -4.0))):
        strip_light(f"NEXUS_CB_L4_LIGHT_{i}", x, y, z + 3.25, 2.0)
    # Hazard stripes at the mantrap threshold.
    box("NEXUS_CB_L4_HAZ", (0.0, 5.85, z + 0.02), (3.0, 0.3, 0.02), "NEXUS_Amber", 0.002)


def water_l5():
    z = Z[5]
    # Two treatment tanks.
    for i, (x, y) in enumerate(((-6.5, -2.5), (-2.8, -2.5))):
        cyl(f"NEXUS_CB_L5_TANK_{i}", (x, y, z + 1.5), 1.5, 3.0, "NEXUS_Steel", "Z", 24)
        cyl(f"NEXUS_CB_L5_TANK_TOP_{i}", (x, y, z + 3.02), 1.55, 0.12, "NEXUS_Rusted_Metal", "Z", 24)
        box(f"NEXUS_CB_L5_TANK_LABEL_{i}", (x, y - 1.52, z + 2.0), (0.8, 0.04, 0.35), "NEXUS_Screen", 0.002)
    # Pump skid.
    box("NEXUS_CB_L5_PUMP_BASE", (4.5, -3.0, z + 0.12), (5.0, 2.2, 0.24), "NEXUS_Steel", 0.01)
    for i, x in enumerate((3.0, 4.5, 6.0)):
        box(f"NEXUS_CB_L5_PUMP_{i}", (x, -3.0, z + 0.8), (1.0, 1.2, 1.2), "NEXUS_Painted_Metal", 0.01)
        cyl(f"NEXUS_CB_L5_PUMP_MOTOR_{i}", (x, -3.0, z + 1.55), 0.32, 1.0, "NEXUS_Steel", "X", 16)
    # Pipes along the ceiling.
    for j, y in enumerate((-5.0, 4.5)):
        cyl(f"NEXUS_CB_L5_PIPE_{j}", (0.0, y, z + 3.15), 0.16, 14.0, "NEXUS_Rusted_Metal", "X", 16)
        for i, x in enumerate((-6.0, -2.0, 2.0, 6.0)):
            cyl(f"NEXUS_CB_L5_VALVE_{j}_{i}", (x, y, z + 3.15), 0.28, 0.08, "NEXUS_Red", "Y", 16)
    # Control panel on the east wall.
    box("NEXUS_CB_L5_PANEL", (8.8, 2.5, z + 1.4), (0.12, 2.0, 1.6), "NEXUS_Steel", 0.008)
    box("NEXUS_CB_L5_PANEL_SCREEN", (8.72, 2.5, z + 1.55), (0.05, 1.3, 0.7), "NEXUS_Screen", 0.004)
    # Drainage grate.
    box("NEXUS_CB_L5_GRATE", (0.0, 0.0, z + 0.02), (4.0, 1.0, 0.04), "NEXUS_Steel", 0.004)
    for i in range(5):
        box(f"NEXUS_CB_L5_GRATE_BAR_{i}", (-1.6 + i * 0.8, 0.0, z + 0.05),
            (0.06, 0.9, 0.04), "NEXUS_Rusted_Metal", 0.002)
    # Lighting.
    for i, (x, y) in enumerate(((-5.0, 4.5), (2.0, 4.5), (-5.0, -4.5), (4.0, 2.0),
                                (0.0, 4.5), (0.0, 0.0), (0.0, -4.5))):
        strip_light(f"NEXUS_CB_L5_LIGHT_{i}", x, y, z + 3.25, 2.0)


def main():
    clean()
    decon_l3()
    security_l4()
    water_l5()
    for level in (3, 4, 5):
        central_door(level)
    bpy.ops.wm.save_as_mainfile(
        filepath=os.path.join(ROOT, "blender_concept", "FM_NEXUS_V05_level1_v33.blend"))
    print("CENTRAL_BLOCKS_SAVED")


if __name__ == "__main__":
    main()
