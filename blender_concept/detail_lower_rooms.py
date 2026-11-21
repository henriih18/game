"""Basic functional props for the L3-L5 rooms."""
import bpy
import math
import os

ROOT = "/home/riyo/Documentos/game"
COL = bpy.data.collections.get("NEXUS_LROOM_PROPS")
if COL is None:
    COL = bpy.data.collections.new("NEXUS_LROOM_PROPS")
    bpy.context.scene.collection.children.link(COL)

ROOMS = {
    # L3 medical
    "ENFERMERIA": "beds",
    "HABITACIONES_MEDICAS": "beds",
    "QUIROFANO": "or",
    "MORGUE": "morgue",
    "CAMARAS_FRIGORIFICAS": "cold",
    "AISLAMIENTO_A": "isolation",
    "AISLAMIENTO_B": "isolation",
    # L4 security
    "ARMERIA_HERRAMIENTAS": "tools",
    "BUNKER_SEGURIDAD": "bunker",
    "CONTENCION_PRIMARIA": "containment",
    "CONTENCION_SECUNDARIA": "containment",
    "CONTROL_CONTENCION": "control",
    "LAB_RESTRINGIDO": "lab",
    # L5 industrial
    "ARCHIVO_SECRETO": "archive",
    "BOMBEO_INUNDACION": "pumps",
    "EXTRACCION_PROFUNDA": "extraction",
    "GENERADORES": "generators",
    "REFRIGERACION": "cooling",
    "TUNEL_PROFUNDO": "tunnel",
}


def mat(name):
    return bpy.data.materials.get(name)


def box(name, center, size, material, bevel=0.006):
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


def cyl(name, center, radius, depth, material, axis="Z", verts=16):
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


def clean():
    for o in list(bpy.data.objects):
        if o.name.startswith(("NEXUS_LROOM_", "TMP_")):
            bpy.data.objects.remove(o, do_unlink=True)


def room_info(name):
    f = bpy.data.objects.get(name + "_FLOOR")
    if not f:
        return None
    return f.location.copy(), f.dimensions.x, f.dimensions.y, f.location.z


def bed(p, x, y, z, tag):
    box(f"NEXUS_LROOM_{p}_BED_{tag}_FRAME", (x, y, z + 0.45), (0.95, 2.1, 0.12),
        "NEXUS_Steel", 0.008)
    for i, (dx, dy) in enumerate(((-0.38, -0.9), (0.38, -0.9), (-0.38, 0.9), (0.38, 0.9))):
        box(f"NEXUS_LROOM_{p}_BED_{tag}_LEG_{i}", (x + dx, y + dy, z + 0.22),
            (0.06, 0.06, 0.45), "NEXUS_Steel", 0.003)
    box(f"NEXUS_LROOM_{p}_BED_{tag}_MAT", (x, y, z + 0.55), (0.88, 2.0, 0.16),
        "NEXUS_Clinical", 0.02)
    box(f"NEXUS_LROOM_{p}_BED_{tag}_PILLOW", (x, y + 0.75, z + 0.66), (0.45, 0.32, 0.12),
        "NEXUS_OffWhite", 0.02)


def cabinet(p, x, y, z, tag="CAB", h=2.0):
    box(f"NEXUS_LROOM_{p}_{tag}_BODY", (x, y, z + h * 0.5), (0.8, 0.5, h),
        "NEXUS_Clinical", 0.008)
    box(f"NEXUS_LROOM_{p}_{tag}_DOOR", (x, y - 0.27, z + h * 0.55), (0.72, 0.04, h * 0.8),
        "NEXUS_Painted_Metal", 0.004)


def desk(p, x, y, z, tag="DESK", w=2.2, d=0.9, h=0.85):
    box(f"NEXUS_LROOM_{p}_{tag}_TOP", (x, y, z + h), (w, d, 0.08),
        "NEXUS_Steel", 0.008)
    for i, (dx, dy) in enumerate(((-w * 0.4, -d * 0.35), (w * 0.4, -d * 0.35),
                                  (-w * 0.4, d * 0.35), (w * 0.4, d * 0.35))):
        box(f"NEXUS_LROOM_{p}_{tag}_LEG_{i}", (x + dx, y + dy, z + h * 0.5),
            (0.06, 0.06, h), "NEXUS_Steel", 0.003)


def monitor(p, x, y, z, tag="MON", w=0.55, h=0.38):
    box(f"NEXUS_LROOM_{p}_{tag}_BODY", (x, y, z + 1.35), (w, 0.05, h),
        "NEXUS_MonitorScreen", 0.004)
    box(f"NEXUS_LROOM_{p}_{tag}_STAND", (x, y + 0.08, z + 1.1), (0.3, 0.2, 0.1),
        "NEXUS_Steel", 0.003)


def shelf(p, x, y, z, tag="SH", w=2.0, h=2.2):
    for i in range(4):
        box(f"NEXUS_LROOM_{p}_{tag}_BOARD_{i}", (x, y, z + 0.35 + i * 0.55),
            (w, 0.5, 0.06), "NEXUS_Steel", 0.004)
    for i, dx in enumerate((-w * 0.45, w * 0.45)):
        box(f"NEXUS_LROOM_{p}_{tag}_POST_{i}", (x + dx, y, z + h * 0.5),
            (0.06, 0.5, h), "NEXUS_Steel", 0.004)
    for i in range(3):
        box(f"NEXUS_LROOM_{p}_{tag}_BOX_{i}", (x - w * 0.25 + i * w * 0.25, y, z + 0.65),
            (0.5, 0.4, 0.35), "NEXUS_Debris", 0.006)


def crate(p, x, y, z, tag="CR", s=0.8):
    box(f"NEXUS_LROOM_{p}_{tag}", (x, y, z + s * 0.5), (s, s, s), "NEXUS_Debris", 0.008)
    box(f"NEXUS_LROOM_{p}_{tag}_BAND", (x, y, z + s * 0.5), (s + 0.02, 0.08, 0.08),
        "NEXUS_Steel", 0.002)


def console(p, x, y, z, tag="CON", w=2.5):
    box(f"NEXUS_LROOM_{p}_{tag}_BASE", (x, y, z + 0.45), (w, 0.9, 0.9),
        "NEXUS_Painted_Metal", 0.008)
    box(f"NEXUS_LROOM_{p}_{tag}_TOP", (x, y, z + 0.92), (w + 0.1, 1.0, 0.08),
        "NEXUS_Steel", 0.006)
    for i in range(3):
        box(f"NEXUS_LROOM_{p}_{tag}_SCR_{i}", (x - w * 0.3 + i * w * 0.3, y + 0.2, z + 1.3),
            (0.5, 0.05, 0.35), "NEXUS_MonitorScreen", 0.003)


def pipe(p, x, y, z, length, tag="PIPE", axis="X"):
    cyl(f"NEXUS_LROOM_{p}_{tag}", (x, y, z), 0.12, length, "NEXUS_Rusted_Metal", axis, 12)


def build(name, kind):
    info = room_info(name)
    if not info:
        print("NO_ROOM", name)
        return
    c, sx, sy, z = info
    z += 0.15
    p = name
    if kind == "beds":
        for i, dx in enumerate((-sx * 0.18, sx * 0.18)):
            bed(p, c.x + dx, c.y + sy * 0.08, z, i)
        cabinet(p, c.x - sx * 0.38, c.y - sy * 0.25, z, "CAB_A")
        cabinet(p, c.x + sx * 0.38, c.y - sy * 0.25, z, "CAB_B")
        monitor(p, c.x, c.y + sy * 0.38, z, "MON")
    elif kind == "or":
        box(f"NEXUS_LROOM_{p}_TABLE", (c.x, c.y, z + 0.9), (1.0, 2.2, 0.12),
            "NEXUS_Clinical", 0.02)
        box(f"NEXUS_LROOM_{p}_TABLE_BASE", (c.x, c.y, z + 0.45), (0.55, 0.55, 0.9),
            "NEXUS_Steel", 0.01)
        cyl(f"NEXUS_LROOM_{p}_LIGHT", (c.x, c.y, z + 2.9), 0.45, 0.12,
            "NEXUS_Clinical", "Z", 20)
        cyl(f"NEXUS_LROOM_{p}_LIGHT_ARM", (c.x, c.y, z + 3.2), 0.06, 0.6,
            "NEXUS_Steel", "Z", 10)
        cabinet(p, c.x - sx * 0.35, c.y + sy * 0.3, z, "CART")
        monitor(p, c.x + sx * 0.35, c.y - sy * 0.2, z, "MON")
    elif kind == "morgue":
        for i, (dx, dy) in enumerate(((-sx * 0.22, -sy * 0.18), (sx * 0.22, -sy * 0.18),
                                      (-sx * 0.22, sy * 0.18), (sx * 0.22, sy * 0.18))):
            box(f"NEXUS_LROOM_{p}_SLAB_{i}", (c.x + dx, c.y + dy, z + 0.55),
                (0.85, 2.2, 0.22), "NEXUS_Steel", 0.01)
            box(f"NEXUS_LROOM_{p}_BAG_{i}", (c.x + dx, c.y + dy, z + 0.68),
                (0.7, 1.9, 0.12), "NEXUS_Rubber", 0.02)
        cabinet(p, c.x - sx * 0.38, c.y + sy * 0.35, z, "CAB")
    elif kind == "cold":
        for i in range(3):
            x = c.x - sx * 0.28 + i * sx * 0.28
            box(f"NEXUS_LROOM_{p}_RACK_{i}", (x, c.y + sy * 0.28, z + 1.1),
                (1.15, 0.8, 2.2), "NEXUS_Steel", 0.01)
            box(f"NEXUS_LROOM_{p}_RACK_DOOR_{i}", (x, c.y + sy * 0.28 - 0.42, z + 1.1),
                (1.0, 0.04, 1.9), "NEXUS_Clinical", 0.004)
        pipe(p, c.x, c.y - sy * 0.3, z + 2.9, sx * 0.8, "PIPE")
    elif kind == "isolation":
        bed(p, c.x, c.y - sy * 0.1, z, 0)
        box(f"NEXUS_LROOM_{p}_CHAIR", (c.x + sx * 0.28, c.y + sy * 0.2, z + 0.45),
            (0.6, 0.6, 0.1), "NEXUS_Rubber", 0.02)
        box(f"NEXUS_LROOM_{p}_WINDOW", (c.x, c.y + sy * 0.38, z + 1.6),
            (2.0, 0.05, 1.2), "NEXUS_Glass", 0.004)
        monitor(p, c.x - sx * 0.28, c.y + sy * 0.2, z, "MON")
    elif kind == "tools":
        desk(p, c.x, c.y - sy * 0.2, z, "BENCH", 3.2, 1.0, 0.9)
        for i in range(2):
            box(f"NEXUS_LROOM_{p}_TOOLRACK_{i}", (c.x - 1.0 + i * 2.0, c.y + sy * 0.35, z + 1.2),
                (1.4, 0.3, 1.8), "NEXUS_Painted_Metal", 0.008)
        cabinet(p, c.x - sx * 0.38, c.y - sy * 0.1, z, "LOCK")
        cabinet(p, c.x + sx * 0.38, c.y - sy * 0.1, z, "LOCK2")
    elif kind == "bunker":
        console(p, c.x, c.y - sy * 0.2, z, "CONSOLE", 3.0)
        for i, (dx, dy) in enumerate(((-sx * 0.32, sy * 0.25), (-sx * 0.32, -sy * 0.1),
                                      (sx * 0.32, sy * 0.25))):
            crate(p, c.x + dx, c.y + dy, z, f"CR{i}", 0.9)
        cabinet(p, c.x + sx * 0.38, c.y - sy * 0.25, z, "LOCK")
    elif kind == "containment":
        for i, dx in enumerate((-sx * 0.24, sx * 0.24)):
            cyl(f"NEXUS_LROOM_{p}_CYL_{i}", (c.x + dx, c.y + sy * 0.05, z + 1.6),
                1.15, 3.0, "NEXUS_Steel", "Z", 20)
            cyl(f"NEXUS_LROOM_{p}_CYL_TOP_{i}", (c.x + dx, c.y + sy * 0.05, z + 3.12),
                1.2, 0.12, "NEXUS_Rusted_Metal", "Z", 20)
        console(p, c.x, c.y - sy * 0.32, z, "CONSOLE", 3.0)
        box(f"NEXUS_LROOM_{p}_HAZ", (c.x, c.y - sy * 0.42, z + 0.02), (sx * 0.7, 0.3, 0.02),
            "NEXUS_Amber", 0.002)
    elif kind == "control":
        box(f"NEXUS_LROOM_{p}_MONWALL", (c.x, c.y + sy * 0.36, z + 1.6),
            (3.4, 0.3, 1.8), "NEXUS_Painted_Metal", 0.008)
        for i in range(4):
            box(f"NEXUS_LROOM_{p}_MON_{i}", (c.x - 1.2 + i * 0.8, c.y + sy * 0.2, z + 1.6),
                (0.65, 0.05, 0.45), "NEXUS_MonitorScreen", 0.004)
        desk(p, c.x, c.y - sy * 0.05, z, "DESK", 3.0, 1.0, 0.85)
        for i, dx in enumerate((-0.8, 0.8)):
            box(f"NEXUS_LROOM_{p}_CHAIR_{i}", (c.x + dx, c.y - sy * 0.22, z + 0.5),
                (0.55, 0.55, 0.1), "NEXUS_Rubber", 0.02)
    elif kind == "lab":
        desk(p, c.x, c.y - sy * 0.2, z, "BENCH", 3.2, 1.0, 0.9)
        box(f"NEXUS_LROOM_{p}_HOOD", (c.x + sx * 0.3, c.y + sy * 0.3, z + 1.1),
            (1.6, 1.2, 2.2), "NEXUS_Clinical", 0.01)
        box(f"NEXUS_LROOM_{p}_HOOD_GLASS", (c.x + sx * 0.3, c.y + sy * 0.3 - 0.62, z + 1.5),
            (1.3, 0.04, 0.9), "NEXUS_Glass", 0.004)
        cabinet(p, c.x - sx * 0.38, c.y + sy * 0.3, z, "CAB")
        monitor(p, c.x, c.y + sy * 0.1, z, "MON")
    elif kind == "archive":
        for i, (dx, dy) in enumerate(((-sx * 0.28, -sy * 0.22), (sx * 0.28, -sy * 0.22),
                                      (-sx * 0.28, sy * 0.22), (sx * 0.28, sy * 0.22))):
            shelf(p, c.x + dx, c.y + dy, z, f"SH{i}", 0.9, 2.2)
        desk(p, c.x, c.y, z, "DESK", 1.8, 0.8, 0.8)
    elif kind == "pumps":
        for i, (dx, dy) in enumerate(((-sx * 0.2, -sy * 0.1), (sx * 0.2, -sy * 0.1))):
            box(f"NEXUS_LROOM_{p}_PUMP_{i}", (c.x + dx, c.y + dy, z + 0.75),
                (1.3, 1.3, 1.5), "NEXUS_Painted_Metal", 0.01)
            cyl(f"NEXUS_LROOM_{p}_MOTOR_{i}", (c.x + dx, c.y + dy, z + 1.6),
                0.35, 1.0, "NEXUS_Steel", "X", 16)
        pipe(p, c.x, c.y + sy * 0.3, z + 2.9, sx * 0.8, "PIPE")
        box(f"NEXUS_LROOM_{p}_GRATE", (c.x, c.y - sy * 0.3, z + 0.02),
            (sx * 0.5, 1.0, 0.04), "NEXUS_Steel", 0.004)
    elif kind == "extraction":
        box(f"NEXUS_LROOM_{p}_WINCH", (c.x, c.y + sy * 0.2, z + 0.9),
            (2.6, 2.0, 1.8), "NEXUS_Rusted_Metal", 0.01)
        for i, dx in enumerate((-1.0, 1.0)):
            box(f"NEXUS_LROOM_{p}_CAGE_POST_{i}", (c.x + dx, c.y - sy * 0.2, z + 1.5),
                (0.12, 0.12, 3.0), "NEXUS_Steel", 0.006)
        box(f"NEXUS_LROOM_{p}_CAGE_TOP", (c.x, c.y - sy * 0.2, z + 3.0),
            (2.2, 2.0, 0.12), "NEXUS_Steel", 0.006)
        console(p, c.x + sx * 0.32, c.y, z, "PANEL", 1.5)
    elif kind == "generators":
        for i, dx in enumerate((-sx * 0.3, sx * 0.3)):
            box(f"NEXUS_LROOM_{p}_GEN_{i}", (c.x + dx, c.y, z + 0.95),
                (2.8, 1.7, 1.9), "NEXUS_Painted_Metal", 0.01)
            box(f"NEXUS_LROOM_{p}_GEN_PANEL_{i}", (c.x + dx, c.y - 0.88, z + 1.1),
                (1.4, 0.05, 0.8), "NEXUS_Screen", 0.004)
        cyl(f"NEXUS_LROOM_{p}_FUEL", (c.x, c.y + sy * 0.32, z + 1.0), 0.9, 2.0,
            "NEXUS_Rusted_Metal", "Z", 18)
        pipe(p, c.x, c.y - sy * 0.32, z + 2.9, sx * 0.7, "PIPE")
    elif kind == "cooling":
        for i in range(3):
            x = c.x - sx * 0.25 + i * sx * 0.25
            box(f"NEXUS_LROOM_{p}_UNIT_{i}", (x, c.y + sy * 0.25, z + 1.1),
                (1.6, 1.0, 2.2), "NEXUS_Steel", 0.01)
            box(f"NEXUS_LROOM_{p}_UNIT_GRILL_{i}", (x, c.y + sy * 0.25 - 0.52, z + 1.3),
                (1.2, 0.04, 0.9), "NEXUS_Grime", 0.004)
        pipe(p, c.x, c.y - sy * 0.3, z + 2.9, sx * 0.8, "PIPE")
    elif kind == "tunnel":
        for i in range(3):
            x = c.x - sx * 0.3 + i * sx * 0.3
            for j, dy in enumerate((-sy * 0.4, sy * 0.4)):
                box(f"NEXUS_LROOM_{p}_FRAME_{i}_POST_{j}", (x, c.y + dy, z + 1.4),
                    (0.28, 0.28, 2.8), "NEXUS_Rusted_Metal", 0.006)
            box(f"NEXUS_LROOM_{p}_FRAME_{i}_TOP", (x, c.y, z + 2.8),
                (0.3, sy * 0.9, 0.3), "NEXUS_Rusted_Metal", 0.006)
        pipe(p, c.x, c.y + sy * 0.3, z + 2.8, sx * 0.8, "PIPE")
        for i in range(5):
            box(f"NEXUS_LROOM_{p}_DEBRIS_{i}", (c.x - 1.6 + i * 0.8, c.y - sy * 0.35, z + 0.05),
                (0.3, 0.2, 0.08), "NEXUS_Debris", 0.004)


def main():
    clean()
    for name, kind in ROOMS.items():
        build(name, kind)
    bpy.ops.wm.save_as_mainfile(
        filepath=os.path.join(ROOT, "blender_concept", "FM_NEXUS_V05_level1_v38.blend"))
    print("LOWER_ROOM_PROPS_SAVED", len(ROOMS))


if __name__ == "__main__":
    main()
