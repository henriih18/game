"""Build the V05 warehouse-maintenance service connector.

Non-destructive: the original east/west walls and roller slats are archived in a
hidden collection, and replacement walls are created with real openings.
Base: FM_NEXUS_V05_level1_v110.blend
Output: FM_NEXUS_V05_level1_v111.blend
"""

import math

import bpy
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
OUT = ROOT + "/FM_NEXUS_V05_level1_v111.blend"
PREFIX = "NEXUS_V05_SERVICE_CONN_"
COLL_NAME = "NEXUS_V05_SERVICE_CONN"
HIST_NAME = "NEXUS_V05_SERVICE_CONN_HIST"
SCENE = bpy.context.scene
FLOOR = -5.65

CONCRETE = "NEXUS_Concrete"
DARK = "NEXUS_Concrete_Dark"
STEEL = "NEXUS_Steel"
PAINT = "NEXUS_Painted_Metal"
RUST = "NEXUS_Rusted_Metal"
GRILL = "NEXUS_GrillDark"
AMBER = "NEXUS_Amber"
RED = "NEXUS_Red"
LIGHT = "NEXUS_CorridorLight"
SIGNPLATE = "NEXUS_SignPlate"
SIGNTEXT = "NEXUS_SignText"
WATER = "NEXUS_Water"


def mat(name):
    m = bpy.data.materials.get(name)
    if m is None:
        raise RuntimeError("Missing material: " + name)
    return m


def collection(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        SCENE.collection.children.link(c)
    return c


COLL = collection(COLL_NAME)
HIST = collection(HIST_NAME)
HIST.hide_viewport = True
HIST.hide_render = True


def clean_previous():
    for o in list(bpy.data.objects):
        if o.name.startswith(PREFIX):
            bpy.data.objects.remove(o, do_unlink=True)
    for o in list(COLL.objects):
        bpy.data.objects.remove(o, do_unlink=True)


def put(o, name, material=None, props=True):
    o.name = name
    if material is not None:
        o.data.materials.clear()
        o.data.materials.append(mat(material))
    for c in list(o.users_collection):
        c.objects.unlink(o)
    COLL.objects.link(o)
    if props:
        o["service_conn_phase"] = "v111"
        o["service_conn_area"] = "V05 almacen - mantenimiento"
    return o


def finish_mesh(o, name, material, bevel=0.008):
    if bevel > 0:
        m = o.modifiers.new("bevel", "BEVEL")
        m.width = bevel
        m.segments = 2
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.modifier_apply(modifier=m.name)
    return put(o, name, material)


def box(name, center, size, material, bevel=0.008):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    o = bpy.context.active_object
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish_mesh(o, name, material, bevel)


def cyl(name, center, radius, depth, material, axis="Z", verts=16):
    rotation = (0, 0, 0)
    if axis == "Y":
        rotation = (math.pi / 2, 0, 0)
    elif axis == "X":
        rotation = (0, math.pi / 2, 0)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=verts, radius=radius, depth=depth, location=center, rotation=rotation
    )
    return finish_mesh(bpy.context.active_object, name, material, 0.0)


def plane(name, center, sx, sy, material):
    bpy.ops.mesh.primitive_plane_add(size=1, location=center)
    o = bpy.context.active_object
    o.dimensions = (sx, sy, 0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return put(o, name, material)


def sign(name, body, center, facing, width, height, size):
    f = Vector(facing).normalized()
    q = f.to_track_quat("Z", "Y")
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    plate = bpy.context.active_object
    plate.dimensions = (width, height, 0.045)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    plate.rotation_mode = "QUATERNION"
    plate.rotation_quaternion = q
    finish_mesh(plate, name + "_PLATE", SIGNPLATE, 0.003)

    bpy.ops.object.text_add(location=Vector(center) + f * 0.04)
    t = bpy.context.active_object
    t.data.body = body
    t.data.size = size
    t.data.align_x = "CENTER"
    t.data.align_y = "CENTER"
    t.data.extrude = 0.002
    t.rotation_mode = "QUATERNION"
    t.rotation_quaternion = q
    return put(t, name + "_TEXT", SIGNTEXT)


def light(name, kind, loc, energy, color, size=None, radius=None):
    data = bpy.data.lights.new(name, kind)
    data.energy = energy
    data.color = color
    if kind == "AREA":
        data.shape = "RECTANGLE"
        data.size = size[0]
        data.size_y = size[1]
    elif kind == "POINT":
        data.shadow_soft_size = radius if radius is not None else 0.2
    ob = bpy.data.objects.new(name, data)
    ob.location = loc
    COLL.objects.link(ob)
    ob["service_conn_phase"] = "v111"
    return ob


def camera(name, loc, target, lens):
    data = bpy.data.cameras.new(name)
    data.lens = lens
    ob = bpy.data.objects.new(name, data)
    ob.location = loc
    ob.rotation_mode = "XYZ"
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    COLL.objects.link(ob)
    return ob


def archive(o):
    if o is None:
        return
    if o.get("service_conn_archived"):
        return
    for c in list(o.users_collection):
        c.objects.unlink(o)
    HIST.objects.link(o)
    o["service_conn_archived"] = True
    o["service_conn_original_of"] = "warehouse-maintenance service connector"
    o.hide_render = True
    o.hide_viewport = True
    o.hide_set(True)


def move_group(keys, dy):
    for o in bpy.data.objects:
        if o.parent is not None:
            continue
        if any(k in o.name for k in keys):
            o.location.y += dy


def build_shell():
    # Warehouse east wall: north segment, south segment and lintel.
    box(PREFIX + "STORE_WALL_N", (4.0, -3.35, -3.7), (0.28, 3.30, 4.20), CONCRETE, 0.012)
    box(PREFIX + "STORE_WALL_S", (4.0, -8.15, -3.7), (0.28, 3.10, 4.20), CONCRETE, 0.012)
    box(PREFIX + "STORE_WALL_LINTEL", (4.0, -5.80, -2.225), (0.28, 1.60, 1.25), CONCRETE, 0.012)

    # Maintenance west wall: north segment, south segment and lintel.
    box(PREFIX + "MAINT_WALL_N", (6.0, -2.60, -3.30), (0.28, 1.80, 5.00), CONCRETE, 0.012)
    box(PREFIX + "MAINT_WALL_S", (6.0, -7.20, -3.30), (0.28, 5.00, 5.00), CONCRETE, 0.012)
    box(PREFIX + "MAINT_WALL_LINTEL", (6.0, -4.10, -1.825), (0.28, 1.20, 2.05), CONCRETE, 0.012)

    # Corridor floor, ceiling and south closure.
    box(PREFIX + "FLOOR", (5.0, -5.70, -5.80), (2.00, 8.00, 0.30), CONCRETE, 0.010)
    box(PREFIX + "CEILING", (5.0, -5.70, -1.60), (2.00, 8.00, 0.24), DARK, 0.010)
    box(PREFIX + "SOUTH_WALL", (5.0, -9.70, -3.64), (2.00, 0.28, 4.32), CONCRETE, 0.012)

    # Floor and ceiling edge trim.
    # Zócalos partidos en los vanos para no crear un bordillo de tobillo.
    box(PREFIX + "TRIM_W_S", (4.17, -8.075, -5.50), (0.06, 2.95, 0.18), STEEL, 0.004)
    box(PREFIX + "TRIM_W_N", (4.17, -3.425, -5.50), (0.06, 3.15, 0.18), STEEL, 0.004)
    box(PREFIX + "TRIM_E_S", (5.83, -7.125, -5.50), (0.06, 4.85, 0.18), STEEL, 0.004)
    box(PREFIX + "TRIM_E_N", (5.83, -2.675, -5.50), (0.06, 1.65, 0.18), STEEL, 0.004)
    box(PREFIX + "TRIM_CEIL_W", (4.22, -5.70, -1.74), (0.10, 7.60, 0.08), GRILL, 0.004)
    box(PREFIX + "TRIM_CEIL_E", (5.78, -5.70, -1.74), (0.10, 7.60, 0.08), GRILL, 0.004)


def build_store_opening():
    # New jambs and header inside the preserved loading door frame.
    for side, y in (("N", -6.60), ("S", -5.00)):
        box(PREFIX + "STORE_JAMB_" + side, (4.0, y, -4.25), (0.22, 0.14, 2.80), STEEL, 0.006)
    box(PREFIX + "STORE_HEADER", (4.0, -5.80, -2.79), (0.22, 1.60, 0.14), STEEL, 0.006)
    box(PREFIX + "STORE_THRESH", (4.0, -5.80, -5.64), (0.40, 1.60, 0.02), STEEL, 0.002)
    for i in range(4):
        y = -6.52 + i * 0.40
        box(PREFIX + "STORE_HAZ_%d" % i, (4.0, y, -5.627), (0.34, 0.16, 0.008), AMBER, 0.001)

    # Two side banks of roller slats, leaving the 1.60 m aperture clear.
    for side, y0, y1 in (("N", -5.00, -3.70), ("S", -7.70, -6.60)):
        width = y1 - y0
        cy = (y0 + y1) / 2
        for i in range(8):
            z = -5.51 + i * 0.36
            box(PREFIX + "STORE_SLAT_%s_%d" % (side, i),
                (3.845, cy, z), (0.055, width - 0.08, 0.28), RUST, 0.003)
        for j, yy in enumerate((y0 + 0.06, (y0 + y1) / 2, y1 - 0.06)):
            box(PREFIX + "STORE_RIB_%s_%d" % (side, j),
                (3.805, yy, -4.25), (0.035, 0.055, 2.80), PAINT, 0.003)

    # Roller drum above the aperture, still under the preserved header.
    cyl(PREFIX + "STORE_ROLLER", (3.98, -5.80, -2.69), 0.115, 4.02, STEEL, "Y", 20)
    box(PREFIX + "STORE_ROLLER_HOUSING", (3.96, -5.80, -2.62), (0.24, 4.18, 0.18), PAINT, 0.008)

    # Warning plate and service sign on the warehouse side.
    sign(PREFIX + "STORE_SIGN", "SERVICIO // MUELLE", (3.79, -5.80, -2.43), (-1, 0, 0), 1.45, 0.30, 0.16)
    sign(PREFIX + "STORE_WARN", "PASO RESTRINGIDO", (3.79, -5.80, -2.12), (-1, 0, 0), 1.25, 0.22, 0.12)


def build_maint_opening():
    for side, y in (("N", -4.70), ("S", -3.50)):
        box(PREFIX + "MAINT_JAMB_" + side, (6.0, y, -4.25), (0.22, 0.14, 2.80), STEEL, 0.006)
    box(PREFIX + "MAINT_HEADER", (6.0, -4.10, -2.79), (0.22, 1.20, 0.14), STEEL, 0.006)
    box(PREFIX + "MAINT_THRESH", (6.0, -4.10, -5.64), (0.40, 1.20, 0.02), STEEL, 0.002)
    for i in range(3):
        y = -4.54 + i * 0.36
        box(PREFIX + "MAINT_HAZ_%d" % i, (6.0, y, -5.627), (0.34, 0.15, 0.008), AMBER, 0.001)

    # Open leaf parked into maintenance, hinged at the north jamb.
    box(PREFIX + "MAINT_DOOR_LEAF", (6.74, -3.50, -4.25), (1.20, 0.06, 2.80), PAINT, 0.008)
    box(PREFIX + "MAINT_DOOR_STIFFENER_0", (6.74, -3.455, -3.75), (1.10, 0.025, 0.10), STEEL, 0.002)
    box(PREFIX + "MAINT_DOOR_STIFFENER_1", (6.74, -3.455, -4.75), (1.10, 0.025, 0.10), STEEL, 0.002)
    for i, z in enumerate((-5.10, -4.25, -3.40)):
        cyl(PREFIX + "MAINT_HINGE_%d" % i, (6.15, -3.50, z), 0.045, 0.14, STEEL, "Z", 12)
    box(PREFIX + "MAINT_HANDLE", (7.26, -3.53, -4.15), (0.05, 0.08, 0.34), STEEL, 0.004)
    box(PREFIX + "MAINT_DOOR_STOP", (7.33, -3.50, -5.54), (0.08, 0.10, 0.18), RED, 0.004)

    sign(PREFIX + "MAINT_SIGN", "ALMACEN // SERVICIO", (6.17, -4.10, -2.43), (1, 0, 0), 1.25, 0.28, 0.14)


def build_corridor_detail():
    # Ceiling cable tray and two pipe runs.
    box(PREFIX + "CABLE_TRAY", (5.0, -5.70, -1.77), (0.34, 7.40, 0.055), GRILL, 0.003)
    for i, x in enumerate((4.88, 5.00, 5.12)):
        cyl(PREFIX + "CABLE_%d" % i, (x, -5.70, -1.72), 0.018, 7.35, RUST, "Y", 8)
    for i, (x, z, r, m) in enumerate((
        (4.28, -2.35, 0.065, RUST),
        (4.34, -2.48, 0.040, "NEXUS_Copper"),
        (5.72, -2.18, 0.052, RUST),
    )):
        cyl(PREFIX + "PIPE_%d" % i, (x, -5.70, z), r, 7.35, m, "Y", 14)
        for j, y in enumerate((-8.8, -6.8, -4.8, -2.8)):
            box(PREFIX + "PIPE_CLAMP_%d_%d" % (i, j), (x, y, z), (0.16, 0.06, 0.06), STEEL, 0.003)

    # Floor drain and a small damp patch at the south end.
    box(PREFIX + "DRAIN_FRAME", (5.0, -7.70, -5.635), (0.42, 0.42, 0.012), GRILL, 0.002)
    for i in range(5):
        box(PREFIX + "DRAIN_SLAT_%d" % i, (4.83 + i * 0.085, -7.70, -5.627), (0.035, 0.32, 0.006), DARK, 0.001)
    plane(PREFIX + "DAMP_PATCH", (5.16, -8.62, -5.638), 0.70, 0.42, WATER)

    # Two simple ceiling fixtures with low-energy area lights.
    for i, y in enumerate((-4.20, -7.30)):
        box(PREFIX + "LIGHT_HOUSING_%d" % i, (5.0, y, -1.86), (0.72, 0.26, 0.10), PAINT, 0.006)
        box(PREFIX + "LIGHT_LENS_%d" % i, (5.0, y, -1.805), (0.60, 0.16, 0.015), LIGHT, 0.002)
        light(PREFIX + "LIGHT_%d" % i, "AREA", (5.0, y, -1.78), 42.0, (0.78, 0.86, 1.0), (0.70, 0.22))
    light(PREFIX + "EMERGENCY_LIGHT", "POINT", (5.62, -3.10, -2.55), 22.0, (1.0, 0.08, 0.04), radius=0.12)
    box(PREFIX + "EMERGENCY_HOUSING", (5.80, -3.10, -2.55), (0.08, 0.14, 0.18), RED, 0.004)

    # Small wall boxes and a junction box for scale.
    box(PREFIX + "JUNCTION_BOX", (5.78, -6.15, -2.85), (0.12, 0.30, 0.36), STEEL, 0.005)
    box(PREFIX + "JUNCTION_LABEL", (5.71, -6.15, -2.85), (0.015, 0.18, 0.10), AMBER, 0.001)
    box(PREFIX + "CONDUIT", (5.80, -6.15, -3.40), (0.04, 0.04, 0.80), STEEL, 0.002)

    # Service sign inside the corridor, facing east.
    sign(PREFIX + "CORR_SIGN", "PASILLO DE SERVICIO", (4.16, -8.20, -2.20), (1, 0, 0), 1.15, 0.24, 0.11)


def main():
    clean_previous()

    # Archive only the original surfaces; the preserved loading-door frame and
    # header remain visible as the outer facade.
    for name in (
        "NEXUS_V05_ALMACEN_WALL_E",
        "NEXUS_V05_MANTENIMIENTO_WALL_W",
        "NEXUS_V05_D_STORE_DOOR_HANDLE",
    ):
        archive(bpy.data.objects.get(name))
    for i in range(7):
        archive(bpy.data.objects.get("NEXUS_V05_D_STORE_DOOR_SLAT_%d" % i))

    # Reorganize the maintenance furniture around the new 1.20 m opening.
    move_group((
        "NEXUS_V05_B_MAINT_BENCH_",
        "NEXUS_V05_B_MAINT_PEG",
        "NEXUS_V05_B_MAINT_TOOLBOX",
        "NEXUS_V05_B_MAINT_RAG_",
        "NEXUS_V05_B_MAINT_VISE_",
        "NEXUS_V05_B_MAINT_BOLT_",
        "NEXUS_V05_B_MAINT_HAMMER_",
        "NEXUS_V05_B_MAINT_SCREWDRIVER_",
        "NEXUS_V05_B_MAINT_WRENCH",
        "NEXUS_V05_D_MAINT_SCREWDRIVER",
        "NEXUS_V05_D_MAINT_TOOLBOX",
        "NEXUS_V05_D_MAINT_WRENCH",
        "NEXUS_ASSET_V05_MAINT_BENCH_TOOLBOX",
    ), -0.25)
    move_group((
        "NEXUS_V05_B_MAINT_CABINET",
    ), 0.15)

    for o in bpy.data.objects:
        if o.name.startswith("NEXUS_V05_B_MAINT_FIRST_AID"):
            o.location.y = -5.95
            o.location.z = -4.52
            if o.name.endswith("_CROSS_H") or o.name.endswith("_CROSS_V"):
                o.location.x = 6.11

    build_shell()
    build_store_opening()
    build_maint_opening()
    build_corridor_detail()

    # Review camera inside the new corridor.
    camera(PREFIX + "CAM_ServiceConn", (4.55, -8.65, -3.05), (5.65, -4.20, -3.05), 16)

    bpy.context.view_layer.update()
    SCENE.camera = bpy.data.objects.get("NEXUS_V05_CAM_Corridor")
    bpy.ops.wm.save_as_mainfile(filepath=OUT)

    print("SAVED", OUT)
    print("CONN_OBJECTS", len(COLL.objects))
    print("HIST_OBJECTS", len(HIST.objects))
    print("TOTAL_OBJECTS", len(bpy.data.objects))


if __name__ == "__main__":
    main()
