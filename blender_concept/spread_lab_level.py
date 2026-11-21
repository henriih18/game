"""Spread the NEXUS lab rooms along a longer corridor and rebuild circulation."""
import bpy
import math
import os
from mathutils import Vector, Matrix

ROOT = "/home/riyo/Documentos/game"
SCENE = bpy.context.scene
C_STRUCT = bpy.data.collections["NEXUS_V03_LAB_STRUCT"]
C_PROPS = bpy.data.collections["NEXUS_V03_LAB_PROPS"]
C_LIGHT = bpy.data.collections["NEXUS_V03_LAB_LIGHTS"]
C_CAMS = bpy.data.collections["NEXUS_V03_LAB_CAMS"]
C_STORY = bpy.data.collections["NEXUS_V03_LAB_STORY"]


def box(name, center, size, material, col, bevel=0.012):
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
        m = o.modifiers.new("Bevel", "BEVEL"); m.width = bevel; m.segments = 1
    return o


def cyl(name, center, radius, depth, material, col, axis="X", vertices=16):
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
    mesh.from_pydata(verts, [], faces); mesh.update()
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


def mat(n):
    return bpy.data.materials.get(n)


# Move each room + its props. New layout: three rooms per side, widely spaced.
moves = {
    "LAB_BIOLOGIA": -12.0,
    "LAB_QUIMICA": -2.5,
    "ARCHIVO_CIENTIFICO": 7.5,
    "SALA_ANALISIS": -12.0,
    "OBSERVACION": -2.5,
    "SERVIDORES": 8.0,
}
props = {
    "LAB_BIOLOGIA": "NEXUS_V03_BIO_",
    "LAB_QUIMICA": "NEXUS_V03_CHEM_",
    "ARCHIVO_CIENTIFICO": "NEXUS_V03_ARCH_",
    "SALA_ANALISIS": "NEXUS_V03_AN_",
    "OBSERVACION": "NEXUS_V03_OBS_",
    "SERVIDORES": "NEXUS_V03_SRV_",
}
for o in bpy.data.objects:
    if o.name.startswith("NEXUS_V03_CAM_"):
        continue
    for room, dx in moves.items():
        if room in o.name or o.name.startswith(props[room]):
            o.location.x += dx
            break

# Remove the old corridor shell and rebuild it longer.
for o in list(bpy.data.objects):
    if o.name.startswith("NEXUS_V03_CORR"):
        bpy.data.objects.remove(o, do_unlink=True)

# New corridor: x -30..30, center y=0, width 2.8.
box("NEXUS_V03_CORRIDOR_FLOOR", (0, 0, -13.8), (60.0, 2.8, 0.3), mat("NEXUS_Concrete"), C_STRUCT, 0.02)
box("NEXUS_V03_CORRIDOR_CEILING", (0, 0, -10.2), (60.0, 2.8, 0.24), mat("NEXUS_Concrete_Dark"), C_STRUCT, 0.02)
# End walls with hazard and sign.
for i, sx in enumerate((-1, 1)):
    x = sx * 30.0
    box(f"NEXUS_V03_CORRIDOR_END_{i}", (x, 0, -12.0), (0.3, 2.8, 3.6), mat("NEXUS_Concrete"), C_STRUCT, 0.015)
    box(f"NEXUS_V03_CORRIDOR_END_PLATE_{i}", (x - sx * 0.16, 0, -11.2), (0.02, 1.8, 1.4), mat("NEXUS_Painted_Metal"), C_STRUCT, 0.01)
    box(f"NEXUS_V03_CORRIDOR_END_HAZARD_{i}", (x - sx * 0.17, 0, -13.35), (0.02, 1.9, 0.18), mat("NEXUS_Amber"), C_STRUCT, 0.005)

# Close the gaps between rooms with long wall stretches.
south = [(-30.0, -26.5), (-17.5, -7.0), (3.0, 14.0), (22.0, 30.0)]
north = [(-30.0, -26.0), (-18.0, -6.5), (0.5, 13.0), (21.0, 30.0)]
for yy, spans in ((-1.4, south), (1.4, north)):
    for i, (x1, x2) in enumerate(spans):
        box(f"NEXUS_V03_CORR_FILL_{yy}_{i}", ((x1 + x2) * 0.5, yy, -12.0), (x2 - x1, 0.25, 3.6), mat("NEXUS_Concrete"), C_STRUCT, 0.012)
        # inner metal cladding and trim
        cx = (x1 + x2) * 0.5
        inner_y = yy - (0.16 if yy > 0 else -0.16)
        box(f"NEXUS_V03_CORR_CLAD_{yy}_{i}", (cx, inner_y, -12.0), (max(1.0, x2 - x1 - 0.4), 0.03, 2.9), mat("NEXUS_Painted_Metal"), C_STRUCT, 0.008)
        box(f"NEXUS_V03_CORR_TRIM_{yy}_{i}", (cx, inner_y - (0.03 if yy > 0 else -0.03), -13.45), (max(0.8, x2 - x1 - 0.5), 0.04, 0.12), mat("NEXUS_Steel"), C_STRUCT, 0.004)
        for j, px in enumerate((x1 + 1.6, x2 - 1.6)):
            if abs(px - cx) < (x2 - x1) * 0.2:
                continue
            box(f"NEXUS_V03_CORR_VENT_{yy}_{i}_{j}", (px, inner_y, -11.6), (0.55, 0.04, 0.45), mat("NEXUS_Steel"), C_STRUCT, 0.006)

# Ceiling services and lights.
for j, (yy, m) in enumerate(((-1.02, "NEXUS_Rusted_Metal"), (1.02, "NEXUS_Steel"))):
    cyl(f"NEXUS_V03_CORR_PIPE_{j}", (0, yy, -10.62), 0.075, 59.4, mat(m), C_STRUCT, "X", 16)
box("NEXUS_V03_CORR_TRAY", (0, 0.85, -10.63), (59.0, 0.30, 0.08), mat("NEXUS_Steel"), C_STRUCT, 0.006)
for i in range(5):
    box(f"NEXUS_V03_CORR_CABLE_{i}", (0, 0.85 + (i - 2) * 0.05, -10.57), (58.5, 0.025, 0.025), mat("NEXUS_Rubber"), C_STRUCT, 0.003)
for i, x in enumerate(range(-28, 29, 4)):
    box(f"NEXUS_V03_CORR_STRIP_{i}", (x, 0, -10.32), (2.2, 0.10, 0.06), mat("NEXUS_CorridorLight"), C_LIGHT, 0.004)
    ld = bpy.data.lights.new(f"NEXUS_V03_CORR_LIGHT_{i}", "AREA")
    ld.color = (0.62, 0.84, 1.0)
    ld.energy = 95.0
    ld.shape = "RECTANGLE"
    ld.size = 2.0
    ld.size_y = 0.25
    lo = bpy.data.objects.new(ld.name, ld)
    C_LIGHT.objects.link(lo)
    lo.location = (x, 0, -10.42)

# Emergency lights along the corridor.
for i, x in enumerate((-24.0, -12.0, 0.0, 12.0, 24.0)):
    box(f"NEXUS_V03_CORR_EMERGENCY_HOUSING_{i}", (x, -1.3, -11.15), (0.18, 0.08, 0.42), mat("NEXUS_Painted_Metal"), C_LIGHT, 0.008)
    box(f"NEXUS_V03_CORR_EMERGENCY_LENS_{i}", (x, -1.23, -11.15), (0.08, 0.03, 0.26), mat("NEXUS_Red"), C_LIGHT, 0.003)
    ld = bpy.data.lights.new(f"NEXUS_V03_CORR_EMERGENCY_LIGHT_{i}", "POINT")
    ld.color = (1.0, 0.03, 0.01)
    ld.energy = 28.0
    ld.shadow_soft_size = 0.2
    lo = bpy.data.objects.new(ld.name, ld)
    C_LIGHT.objects.link(lo)
    lo.location = (x, -1.0, -11.15)

# Corridor dressing: junction boxes, crates, debris, dark stains.
for i, x in enumerate((-27.5, -20.0, -9.0, 1.5, 12.5, 23.0)):
    box(f"NEXUS_V03_CORR_JUNCTION_{i}", (x, 1.28, -11.85), (0.45, 0.16, 0.55), mat("NEXUS_Painted_Metal"), C_PROPS, 0.008)
    box(f"NEXUS_V03_CORR_JUNCTION_LED_{i}", (x, 1.19, -11.78), (0.10, 0.02, 0.06), mat("NEXUS_CorridorLight"), C_PROPS, 0.002)
for i, (x, y, sx, sy) in enumerate(((-18.0, 0.95, 0.6, 0.4), (6.0, -0.95, 0.5, 0.5), (18.0, 1.0, 0.7, 0.35), (26.0, -1.0, 0.6, 0.4))):
    box(f"NEXUS_V03_CORR_CRATE_{i}", (x, y, -13.55), (sx, sy, 0.45), mat("NEXUS_Rusted_Metal"), C_PROPS, 0.02)
for i, (x, y) in enumerate(((-22.0, -1.0), (3.0, 0.95), (14.0, -0.9), (27.0, 1.0))):
    box(f"NEXUS_V03_CORR_DEBRIS_{i}", (x, y, -13.60), (0.35, 0.16, 0.05), mat("NEXUS_Debris"), C_STORY, 0.005)
for i, (x, y) in enumerate(((-14.0, -0.4), (9.0, 0.4), (21.0, -0.5))):
    box(f"NEXUS_V03_CORR_STAIN_{i}", (x, y, -13.58), (0.65, 0.35, 0.012), mat("NEXUS_Blood_Dried"), C_STORY, 0.002)

# Level sign near the entrance.
box("NEXUS_V03_LEVEL_SIGN_PLATE", (-28.5, 1.28, -11.6), (1.9, 0.04, 0.3), mat("NEXUS_Concrete_Dark"), C_STRUCT, 0.006)
curve = bpy.data.curves.new("NEXUS_V03_LEVEL_SIGN_TEXT", type="FONT")
curve.body = "NIVEL -2  //  LABORATORIOS"
curve.align_x = "CENTER"; curve.align_y = "CENTER"; curve.size = 0.12; curve.extrude = 0.004
so = bpy.data.objects.new(curve.name, curve)
C_STRUCT.objects.link(so)
so.location = (-28.5, 1.25, -11.6)
so.rotation_euler.x = -math.pi / 2
so.data.materials.append(mat("NEXUS_Amber"))

# Cameras follow the new layout.
def aim(name, loc, target, lens=26.0):
    cam = bpy.data.objects.get(name)
    if cam is None:
        return
    cam.location = Vector(loc)
    cam.data.lens = lens
    f = (Vector(target) - Vector(loc)).normalized()
    up = Vector((0, 0, 1))
    right = f.cross(up).normalized()
    up2 = right.cross(f).normalized()
    cam.matrix_world = Matrix.Translation(cam.location) @ Matrix((right, up2, -f)).transposed().to_4x4()

aim("NEXUS_V03_CAM_Corridor", (-28.6, 0.0, -12.15), (12.0, 0.0, -12.15), 30.0)
aim("NEXUS_V03_CAM_Biologia", (-25.8, -2.0, -12.15), (-20.0, -6.0, -12.0), 24.0)
aim("NEXUS_V03_CAM_Quimica", (-6.3, -2.0, -12.15), (-0.5, -6.0, -12.0), 24.0)
SCENE.camera = bpy.data.objects.get("NEXUS_V03_CAM_Corridor")

bpy.context.view_layer.update()
path = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V03_lab_level_spread.blend")
i = 2
while os.path.exists(path):
    path = os.path.join(ROOT, "blender_concept", f"FM_NEXUS_V03_lab_level_spread_{i:02d}.blend")
    i += 1
bpy.ops.wm.save_as_mainfile(filepath=path)
print("SPREAD_SAVED", path, os.path.getsize(path), "objects", len(bpy.data.objects))
