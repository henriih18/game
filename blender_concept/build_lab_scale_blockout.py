"""NEXUS lab level scale blockout: large volumes, bent corridor, mezzanine.

This is intentionally a blockout: it validates scale, circulation and sightlines
before props, damage and PBR detail. It hides the previous lab level, never deletes it.
"""
import bpy
import math
import os
from mathutils import Vector, Matrix

ROOT = "/home/riyo/Documentos/game"
SCENE = bpy.context.scene
Z0 = -13.8
DOOR_H = 3.2

# Hide the previous lab level, keep it recoverable.
for o in bpy.data.objects:
    if o.name.startswith("NEXUS_V03_") or o.name.startswith("NEXUS_UP_") or o.name.startswith("CORRIDOR_L-2"):
        o.hide_render = True
        try:
            o.hide_set(True)
        except Exception:
            pass

parent = bpy.data.collections.get("NEXUS_V04_LAB_SCALE")
if parent is None:
    parent = bpy.data.collections.new("NEXUS_V04_LAB_SCALE")
    SCENE.collection.children.link(parent)


def sub(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        parent.children.link(c)
    return c


C_STRUCT = sub("NEXUS_V04_STRUCT")
C_PROPS = sub("NEXUS_V04_PROPS")
C_LIGHT = sub("NEXUS_V04_LIGHTS")
C_CAMS = sub("NEXUS_V04_CAMS")


def mat(name):
    return bpy.data.materials.get(name)


def box(name, center, size, material, col, bevel=0.02):
    mesh = bpy.data.meshes.new(name)
    x, y, z = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
    verts = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
             (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    col.objects.link(o)
    o.location = center
    if material:
        mesh.materials.append(material)
    if bevel > 0:
        m = o.modifiers.new("Bevel", "BEVEL")
        m.width = bevel
        m.segments = 1
    return o


def cylinder(name, center, radius, depth, material, col, axis="Z", vertices=32):
    mesh = bpy.data.meshes.new(name)
    verts = []
    for z in (-depth * 0.5, depth * 0.5):
        for i in range(vertices):
            a = 2 * math.pi * i / vertices
            verts.append((math.cos(a) * radius, math.sin(a) * radius, z))
    faces = []
    for i in range(vertices):
        j = (i + 1) % vertices
        faces.append((i, j, vertices + j, vertices + i))
    faces.append(tuple(range(vertices - 1, -1, -1)))
    faces.append(tuple(range(vertices, vertices * 2)))
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    col.objects.link(o)
    o.location = center
    if axis == "X":
        o.rotation_euler.y = math.pi / 2
    elif axis == "Y":
        o.rotation_euler.x = math.pi / 2
    if material:
        mesh.materials.append(material)
    return o


def torus(name, center, major, minor, material, col):
    mesh = bpy.data.meshes.new(name)
    verts = []
    seg, ring = 48, 12
    for i in range(seg):
        a = 2 * math.pi * i / seg
        for j in range(ring):
            b = 2 * math.pi * j / ring
            r = major + minor * math.cos(b)
            verts.append((math.cos(a) * r, math.sin(a) * r, minor * math.sin(b)))
    faces = []
    for i in range(seg):
        ni = (i + 1) % seg
        for j in range(ring):
            nj = (j + 1) % ring
            faces.append((i * ring + j, ni * ring + j, ni * ring + nj, i * ring + nj))
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    col.objects.link(o)
    o.location = center
    if material:
        mesh.materials.append(material)
    return o


def text(name, body, loc, size, rot_x, mat_name, col):
    curve = bpy.data.curves.new(name, type="FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    curve.extrude = 0.008
    o = bpy.data.objects.new(name, curve)
    col.objects.link(o)
    o.location = loc
    o.rotation_euler.x = rot_x
    o.data.materials.append(mat(mat_name))
    return o


def doorway(name, x, y, side, w=1.8, h=DOOR_H):
    # side: N/S/E/W is the room wall side where the door sits.
    if side in ("N", "S"):
        leaf_size = (w - 0.08, 0.10, h - 0.08)
        frame = ((w + 0.24, 0.16, 0.12), (0, 0, h + 0.04))
        jamb = (0.12, 0.16, h)
        jx = w * 0.5 + 0.06
        j1 = box(name + "_J1", (x - jx, y, Z0 + h * 0.5), jamb, mat("NEXUS_Painted_Metal"), C_STRUCT, 0.01)
        j2 = box(name + "_J2", (x + jx, y, Z0 + h * 0.5), jamb, mat("NEXUS_Painted_Metal"), C_STRUCT, 0.01)
    else:
        leaf_size = (0.10, w - 0.08, h - 0.08)
        frame = ((0.16, w + 0.24, 0.12), (0, 0, h + 0.04))
        jamb = (0.16, 0.12, h)
        jy = w * 0.5 + 0.06
        j1 = box(name + "_J1", (x, y - jy, Z0 + h * 0.5), jamb, mat("NEXUS_Painted_Metal"), C_STRUCT, 0.01)
        j2 = box(name + "_J2", (x, y + jy, Z0 + h * 0.5), jamb, mat("NEXUS_Painted_Metal"), C_STRUCT, 0.01)
    box(name + "_TOP", (x, y, Z0 + h + 0.02), (frame[0][0], frame[0][1], 0.12), mat("NEXUS_Painted_Metal"), C_STRUCT, 0.01)
    box(name + "_LEAF", (x, y, Z0 + h * 0.5), leaf_size, mat("NEXUS_Painted_Metal"), C_STRUCT, 0.025)
    # amber threshold
    if side in ("N", "S"):
        box(name + "_TH", (x, y, Z0 + 0.03), (w + 0.2, 0.18, 0.02), mat("NEXUS_Amber"), C_STRUCT, 0.004)
    else:
        box(name + "_TH", (x, y, Z0 + 0.03), (0.18, w + 0.2, 0.02), mat("NEXUS_Amber"), C_STRUCT, 0.004)


def room(name, cx, cy, sx, sy, h, door_side, door_w=1.8):
    x0, x1 = cx - sx * 0.5, cx + sx * 0.5
    y0, y1 = cy - sy * 0.5, cy + sy * 0.5
    box(f"NEXUS_V04_{name}_FLOOR", (cx, cy, Z0), (sx, sy, 0.3), mat("NEXUS_Concrete"), C_STRUCT, 0.02)
    box(f"NEXUS_V04_{name}_CEILING", (cx, cy, Z0 + h + 0.12), (sx, sy, 0.24), mat("NEXUS_Concrete_Dark"), C_STRUCT, 0.02)
    # Walls with one door opening.
    for side, fixed, a0, a1 in (("N", y1, x0, x1), ("S", y0, x0, x1)):
        if side == door_side:
            box(f"NEXUS_V04_{name}_WALL_{side}_A", ((a0 + cx - door_w * 0.5) * 0.5, fixed, Z0 + h * 0.5),
                (abs(cx - door_w * 0.5 - a0), 0.28, h), mat("NEXUS_Concrete"), C_STRUCT, 0.02)
            box(f"NEXUS_V04_{name}_WALL_{side}_B", ((cx + door_w * 0.5 + a1) * 0.5, fixed, Z0 + h * 0.5),
                (abs(a1 - (cx + door_w * 0.5)), 0.28, h), mat("NEXUS_Concrete"), C_STRUCT, 0.02)
            box(f"NEXUS_V04_{name}_LINTEL_{side}", (cx, fixed, Z0 + (h + DOOR_H) * 0.5),
                (door_w, 0.28, h - DOOR_H), mat("NEXUS_Concrete"), C_STRUCT, 0.02)
            doorway(f"NEXUS_V04_{name}_DOOR", cx, fixed, side, door_w, DOOR_H)
        else:
            box(f"NEXUS_V04_{name}_WALL_{side}", (cx, fixed, Z0 + h * 0.5), (sx, 0.28, h), mat("NEXUS_Concrete"), C_STRUCT, 0.02)
    for side, fixed, a0, a1 in (("E", x1, y0, y1), ("W", x0, y0, y1)):
        if side == door_side:
            box(f"NEXUS_V04_{name}_WALL_{side}_A", (fixed, (a0 + cy - door_w * 0.5) * 0.5, Z0 + h * 0.5),
                (0.28, abs(cy - door_w * 0.5 - a0), h), mat("NEXUS_Concrete"), C_STRUCT, 0.02)
            box(f"NEXUS_V04_{name}_WALL_{side}_B", (fixed, (cy + door_w * 0.5 + a1) * 0.5, Z0 + h * 0.5),
                (0.28, abs(a1 - (cy + door_w * 0.5)), h), mat("NEXUS_Concrete"), C_STRUCT, 0.02)
            box(f"NEXUS_V04_{name}_LINTEL_{side}", (fixed, cy, Z0 + (h + DOOR_H) * 0.5),
                (0.28, door_w, h - DOOR_H), mat("NEXUS_Concrete"), C_STRUCT, 0.02)
            doorway(f"NEXUS_V04_{name}_DOOR", fixed, cy, side, door_w, DOOR_H)
        else:
            box(f"NEXUS_V04_{name}_WALL_{side}", (fixed, cy, Z0 + h * 0.5), (0.28, sy, h), mat("NEXUS_Concrete"), C_STRUCT, 0.02)
    # Ceiling practical.
    ld = bpy.data.lights.new(f"NEXUS_V04_{name}_LIGHT", "AREA")
    ld.color = (0.62, 0.82, 1.0)
    ld.energy = 280.0 if h < 5.0 else 1100.0
    ld.shape = "RECTANGLE"
    ld.size = min(4.0, sx * 0.3)
    ld.size_y = 0.45
    lo = bpy.data.objects.new(ld.name, ld)
    C_LIGHT.objects.link(lo)
    lo.location = (cx, cy, Z0 + h - 0.32)
    strip_mat = "NEXUS_Amber" if "ARCHIVO" in name else "NEXUS_CorridorLight"
    box(f"NEXUS_V04_{name}_STRIP", (cx, cy, Z0 + h - 0.22), (min(3.0, sx * 0.35), 0.12, 0.06), mat(strip_mat), C_LIGHT, 0.004)


def corridor(name, cx, cy, sx, sy, h=4.2):
    box(f"NEXUS_V04_{name}_FLOOR", (cx, cy, Z0), (sx, sy, 0.3), mat("NEXUS_Concrete"), C_STRUCT, 0.02)
    box(f"NEXUS_V04_{name}_CEILING", (cx, cy, Z0 + h + 0.12), (sx, sy, 0.24), mat("NEXUS_Concrete_Dark"), C_STRUCT, 0.02)
    # Structural columns along the long edges, every ~4 m.
    if sx >= sy:
        for x in range(int(cx - sx * 0.5) + 2, int(cx + sx * 0.5), 4):
            for y in (cy - sy * 0.5, cy + sy * 0.5):
                box(f"NEXUS_V04_{name}_COL_{x}_{y}", (x, y, Z0 + h * 0.5), (0.38, 0.38, h), mat("NEXUS_Painted_Metal"), C_STRUCT, 0.015)
    else:
        for y in range(int(cy - sy * 0.5) + 2, int(cy + sy * 0.5), 4):
            for x in (cx - sx * 0.5, cx + sx * 0.5):
                box(f"NEXUS_V04_{name}_COL_{x}_{y}", (x, y, Z0 + h * 0.5), (0.38, 0.38, h), mat("NEXUS_Painted_Metal"), C_STRUCT, 0.015)
    # Linear light strips and area lights.
    n = max(2, int(max(sx, sy) // 6))
    for i in range(n):
        t = (i + 0.5) / n
        if sx >= sy:
            p = (cx - sx * 0.5 + sx * t, cy, Z0 + h - 0.2)
            box(f"NEXUS_V04_{name}_STRIP_{i}", p, (2.4, 0.10, 0.05), mat("NEXUS_CorridorLight"), C_LIGHT, 0.004)
            ld = bpy.data.lights.new(f"NEXUS_V04_{name}_LIGHT_{i}", "AREA")
            ld.color = (0.65, 0.84, 1.0)
            ld.energy = 120.0
            ld.shape = "RECTANGLE"; ld.size = 2.2; ld.size_y = 0.25
            lo = bpy.data.objects.new(ld.name, ld); C_LIGHT.objects.link(lo)
            lo.location = (p[0], p[1], p[2] - 0.1)
        else:
            p = (cx, cy - sy * 0.5 + sy * t, Z0 + h - 0.2)
            box(f"NEXUS_V04_{name}_STRIP_{i}", p, (0.10, 2.4, 0.05), mat("NEXUS_CorridorLight"), C_LIGHT, 0.004)
            ld = bpy.data.lights.new(f"NEXUS_V04_{name}_LIGHT_{i}", "AREA")
            ld.color = (0.65, 0.84, 1.0)
            ld.energy = 120.0
            ld.shape = "RECTANGLE"; ld.size = 0.25; ld.size_y = 2.2
            lo = bpy.data.objects.new(ld.name, ld); C_LIGHT.objects.link(lo)
            lo.location = (p[0], p[1], p[2] - 0.1)


# Main volumes.
room("LAB_BIOLOGIA", -10.0, -12.0, 14.0, 10.0, 4.8, "E", 1.8)
room("LAB_QUIMICA", -10.0, 19.0, 12.0, 10.0, 4.8, "S", 1.8)
room("SALA_ANALISIS", 8.0, 20.0, 10.0, 8.0, 4.2, "S", 1.8)
room("ARCHIVO_CIENTIFICO", 7.0, 0.0, 11.0, 8.0, 4.0, "W", 1.8)
room("SERVIDORES", 7.0, -10.0, 8.0, 7.0, 4.0, "W", 1.8)
room("NEXUS_NAVE", -10.7, 2.0, 18.0, 14.0, 7.0, "E", 3.2)
room("AIRLOCK", 0.0, -12.0, 4.0, 4.0, 3.6, "N", 1.8)

# Bent circulation: main spine, east wing, west branch, airlock connector.
corridor("CORR_MAIN", 0.0, 1.0, 3.4, 22.0)
corridor("CORR_EAST", 7.0, 12.0, 14.0, 3.4)
corridor("CORR_WEST", -7.0, 12.0, 14.0, 3.4)
# Connectors (floor/ceiling only).
for name, cx, cy, sx, sy in (
    ("CONN_BIO", -1.5, -12.0, 3.0, 3.4),
    ("CONN_CHEM", -10.0, 14.5, 3.4, 5.0),
    ("CONN_AN", 8.0, 14.5, 3.4, 5.0),
    ("CONN_ARCH", 1.8, 0.0, 0.6, 3.4),
    ("CONN_SRV", 1.7, -10.0, 2.6, 3.4),
):
    box(f"NEXUS_V04_{name}_FLOOR", (cx, cy, Z0), (sx, sy, 0.3), mat("NEXUS_Concrete"), C_STRUCT, 0.01)
    box(f"NEXUS_V04_{name}_CEIL", (cx, cy, Z0 + 4.2 + 0.12), (sx, sy, 0.24), mat("NEXUS_Concrete_Dark"), C_STRUCT, 0.01)

# Nave focal elements: containment tank, overhead ring, mezzanine and stairs.
tank = cylinder("NEXUS_V04_NAVE_TANK", (-10.7, 2.0, Z0 + 2.2), 2.1, 4.4, mat("NEXUS_Glass"), C_PROPS, "Z", 32)
cylinder("NEXUS_V04_NAVE_TANK_GOO", (-10.7, 2.0, Z0 + 1.5), 1.75, 2.8, mat("NEXUS_Green"), C_PROPS, "Z", 32)
cylinder("NEXUS_V04_NAVE_TANK_BASE", (-10.7, 2.0, Z0 + 0.25), 2.35, 0.5, mat("NEXUS_Steel"), C_PROPS, "Z", 32)
torus("NEXUS_V04_NAVE_RING", (-10.7, 2.0, Z0 + 6.1), 3.7, 0.10, mat("NEXUS_CorridorLight"), C_PROPS)

# Mezzanine platform and rail.
box("NEXUS_V04_MEZZ", (-15.4, 2.0, Z0 + 3.55), (6.0, 8.0, 0.28), mat("NEXUS_Painted_Metal"), C_PROPS, 0.02)
for i, (x, y, sx, sy) in enumerate((
    (-12.45, 2.0, 0.08, 8.0),
    (-15.4, -1.98, 6.0, 0.08),
    (-15.4, 5.98, 6.0, 0.08),
)):
    box(f"NEXUS_V04_MEZZ_RAIL_{i}", (x, y, Z0 + 4.45), (sx, sy, 1.55), mat("NEXUS_Steel"), C_PROPS, 0.01)
# Stairs from nave floor to mezzanine (simple block steps).
for i in range(9):
    box(f"NEXUS_V04_STAIR_{i}", (-18.0 + i * 0.38, 2.0, Z0 + 0.2 + i * 0.38),
        (0.38, 2.2, 0.2), mat("NEXUS_Painted_Metal"), C_STRUCT, 0.01)

# Door signage.
text("NEXUS_V04_SIGN_NAVE", "NAVE DE CONTENCION", (-1.55, 2.0, Z0 + 3.55), 0.22, -math.pi / 2, "NEXUS_Amber", C_STRUCT)
text("NEXUS_V04_SIGN_BIo", "LABORATORIO DE BIOLOGIA", (-2.9, -12.0, Z0 + 3.55), 0.18, -math.pi / 2, "NEXUS_Amber", C_STRUCT)
text("NEXUS_V04_SIGN_LEVEL", "NIVEL -2  //  LABORATORIOS", (0.0, -13.4, Z0 + 3.1), 0.2, 0.0, "NEXUS_Amber", C_STRUCT)

# Presentation cameras.
def camera(name, loc, target, lens=24.0):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    co = bpy.data.objects.new(name, cd)
    C_CAMS.objects.link(co)
    co.location = Vector(loc)
    f = (Vector(target) - Vector(loc)).normalized()
    up = Vector((0, 0, 1))
    if abs(f.dot(up)) > 0.98:
        up = Vector((0, 1, 0))
    right = f.cross(up).normalized()
    up2 = right.cross(f).normalized()
    co.matrix_world = Matrix.Translation(co.location) @ Matrix((right, up2, -f)).transposed().to_4x4()
    return co

cam_corr = camera("NEXUS_V04_CAM_Corridor", (0.0, -8.5, -12.15), (0.0, 11.0, -12.15), 22.0)
cam_nave = camera("NEXUS_V04_CAM_Nave", (-2.6, 7.2, -12.0), (-10.7, 2.0, -11.4), 20.0)
cam_mezz = camera("NEXUS_V04_CAM_Mezz", (-15.4, -1.6, -9.8), (-6.0, 2.0, -12.0), 20.0)
SCENE.camera = cam_corr

# Render setup.
SCENE.render.engine = "BLENDER_EEVEE"
SCENE.render.resolution_x = 1920
SCENE.render.resolution_y = 1080
SCENE.render.resolution_percentage = 100
SCENE.render.image_settings.file_format = "PNG"
try:
    SCENE.eevee.taa_render_samples = 64
except Exception:
    pass
try:
    SCENE.view_settings.view_transform = "AgX"
    SCENE.view_settings.look = "AgX - Medium High Contrast"
    SCENE.view_settings.exposure = 1.25
except Exception:
    pass

bpy.context.view_layer.update()
print("SCALE_BLOCKOUT_DONE objects", len(bpy.data.objects), "visible", sum(1 for o in bpy.data.objects if not o.hide_render))
path = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V04_lab_scale_blockout.blend")
i = 2
while os.path.exists(path):
    path = os.path.join(ROOT, "blender_concept", f"FM_NEXUS_V04_lab_scale_blockout_{i:02d}.blend")
    i += 1
bpy.ops.wm.save_as_mainfile(filepath=path)
print("SAVED", path, os.path.getsize(path))
