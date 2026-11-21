"""Detail the V04 NEXUS lab scale blockout: cameras, signs, catwalks, props."""
import bpy
import math
import os
from mathutils import Vector, Matrix

ROOT = "/home/riyo/Documentos/game"
SCENE = bpy.context.scene
Z0 = -13.8
PREFIX = "NEXUS_V04_DETAIL_"

parent = bpy.data.collections.get("NEXUS_V04_LAB_SCALE")
if parent is None:
    parent = bpy.data.collections.new("NEXUS_V04_LAB_SCALE")
    SCENE.collection.children.link(parent)

DETAIL = bpy.data.collections.get("NEXUS_V04_DETAIL")
if DETAIL is None:
    DETAIL = bpy.data.collections.new("NEXUS_V04_DETAIL")
    parent.children.link(DETAIL)


def mat(name):
    return bpy.data.materials.get(name)


def remove_old():
    for o in list(bpy.data.objects):
        if o.name.startswith(PREFIX):
            bpy.data.objects.remove(o, do_unlink=True)


def box(name, center, size, material, bevel=0.012):
    mesh = bpy.data.meshes.new(name)
    x, y, z = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
    verts = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
             (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    DETAIL.objects.link(o)
    o.location = center
    if material:
        mesh.materials.append(material)
    if bevel > 0:
        m = o.modifiers.new("Bevel", "BEVEL"); m.width = bevel; m.segments = 1
    return o


def cyl(name, center, radius, depth, material, axis="Z", verts=16):
    mesh = bpy.data.meshes.new(name)
    verts_list = []
    for z in (-depth * 0.5, depth * 0.5):
        for i in range(verts):
            a = 2 * math.pi * i / verts
            verts_list.append((math.cos(a) * radius, math.sin(a) * radius, z))
    faces = []
    for i in range(verts):
        j = (i + 1) % verts
        faces.append((i, j, verts + j, verts + i))
    faces.append(tuple(range(verts - 1, -1, -1)))
    faces.append(tuple(range(verts, verts * 2)))
    mesh.from_pydata(verts_list, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    DETAIL.objects.link(o)
    o.location = center
    if axis == "X": o.rotation_euler.y = math.pi / 2
    elif axis == "Y": o.rotation_euler.x = math.pi / 2
    if material: mesh.materials.append(material)
    return o


def sign(name, body, loc, normal, width, height, text_size, material):
    n = Vector(normal).normalized()
    up = Vector((0, 0, 1))
    if abs(n.dot(up)) > 0.95:
        up = Vector((0, 1, 0))
    right = up.cross(n).normalized()
    up2 = n.cross(right).normalized()
    rot = Matrix((right, up2, n)).transposed().to_4x4()
    plate = box(PREFIX + name + "_PLATE", Vector(loc) - n * 0.025, (width, height, 0.05), mat("NEXUS_SignPlate") or mat("NEXUS_Concrete_Dark"))
    plate.matrix_world = Matrix.Translation(Vector(loc) - n * 0.03) @ rot
    # Text local axes: X right, Y up, Z normal.
    curve = bpy.data.curves.new(PREFIX + name + "_TEXT", type="FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = text_size
    curve.extrude = 0.005
    txt = bpy.data.objects.new(curve.name, curve)
    DETAIL.objects.link(txt)
    txt.matrix_world = Matrix.Translation(Vector(loc) + n * 0.012) @ rot
    txt.data.materials.append(material)


def railing(name, x0, y0, x1, y1, z, height=1.05):
    length = (Vector((x1, y1, 0)) - Vector((x0, y0, 0))).length
    if length < 0.1:
        return
    posts = max(2, int(length / 1.5) + 1)
    for i in range(posts):
        t = i / (posts - 1)
        px = x0 + (x1 - x0) * t
        py = y0 + (y1 - y0) * t
        box(f"{PREFIX}{name}_POST_{i}", (px, py, z + height * 0.5), (0.06, 0.06, height), mat("NEXUS_Steel"))
    # Two horizontal bars, oriented along the segment.
    ang = math.atan2(y1 - y0, x1 - x0)
    for j, dz in enumerate((height * 0.45, height * 0.92)):
        o = box(f"{PREFIX}{name}_BAR_{j}", ((x0 + x1) * 0.5, (y0 + y1) * 0.5, z + dz),
                (length, 0.045, 0.045), mat("NEXUS_Steel"), 0.005)
        o.rotation_euler.z = ang


def grating(name, cx, cy, sx, sy, z):
    box(PREFIX + name + "_BASE", (cx, cy, z), (sx, sy, 0.08), mat("NEXUS_Steel"), 0.01)
    if sx >= sy:
        n = max(2, int(sx / 0.28))
        for i in range(n):
            x = cx - sx * 0.5 + (i + 0.5) * sx / n
            box(f"{PREFIX}{name}_SLAT_{i}", (x, cy, z + 0.05), (0.05, sy * 0.94, 0.025), mat("NEXUS_Steel"), 0.003)
    else:
        n = max(2, int(sy / 0.28))
        for i in range(n):
            y = cy - sy * 0.5 + (i + 0.5) * sy / n
            box(f"{PREFIX}{name}_SLAT_{i}", (cx, y, z + 0.05), (sx * 0.94, 0.05, 0.025), mat("NEXUS_Steel"), 0.003)


def catwalk():
    z = Z0 + 4.85
    # North catwalk and east catwalk form an L around the nave.
    grating("CATWALK_N", -10.75, 8.35, 17.4, 1.25, z)
    grating("CATWALK_E", -2.30, 1.3, 1.25, 12.8, z)
    railing("RAIL_N_OUT", -19.45, 9.0, -2.05, 9.0, z)
    railing("RAIL_N_IN", -19.45, 7.72, -3.05, 7.72, z)
    railing("RAIL_E_OUT", -1.68, -4.9, -1.68, 7.75, z)
    railing("RAIL_E_IN", -2.95, -4.9, -2.95, 7.75, z)
    # Support columns.
    for i, x in enumerate((-18.0, -14.0, -10.0, -6.0, -2.5)):
        box(f"{PREFIX}CATWALK_COL_N_{i}", (x, 8.9, Z0 + 2.45), (0.18, 0.18, 4.9), mat("NEXUS_Steel"), 0.01)
    for i, y in enumerate((-3.2, 1.0, 5.2, 8.5)):
        box(f"{PREFIX}CATWALK_COL_E_{i}", (-1.9, y, Z0 + 2.45), (0.18, 0.18, 4.9), mat("NEXUS_Steel"), 0.01)
    # Stairs from mezzanine to north catwalk.
    steps = 8
    for i in range(steps):
        h = Z0 + 3.55 + (i + 1) * (1.3 / steps)
        box(f"{PREFIX}STAIR_STEP_{i}", (-13.7, 6.0 + i * 0.24, h - 0.06), (1.15, 0.28, 0.12), mat("NEXUS_Steel"), 0.006)
    railing("STAIR_RAIL_L", -14.4, 6.0, -14.4, 7.9, Z0 + 4.25, 1.0)
    railing("STAIR_RAIL_R", -13.0, 6.0, -13.0, 7.9, Z0 + 4.25, 1.0)


def machinery():
    # Three process cabinets along the south wall.
    for i, x in enumerate((-16.8, -12.8, -8.8)):
        box(f"{PREFIX}MACHINE_{i}", (x, -3.9, Z0 + 1.1), (1.8, 1.1, 2.2), mat("NEXUS_Steel"), 0.02)
        box(f"{PREFIX}MACHINE_PANEL_{i}", (x, -3.32, Z0 + 1.25), (1.25, 0.04, 1.1), mat("NEXUS_Painted_Metal"), 0.006)
        box(f"{PREFIX}MACHINE_STRIPE_{i}", (x, -3.31, Z0 + 0.35), (1.4, 0.02, 0.08), mat("NEXUS_Amber"), 0.004)
        for j in range(4):
            box(f"{PREFIX}MACHINE_VENT_{i}_{j}", (x - 0.45 + j * 0.3, -3.30, Z0 + 1.75), (0.18, 0.02, 0.06), mat("NEXUS_Debris"), 0.002)
    # Overhead crane beam and hoist.
    box(f"{PREFIX}CRANE_BEAM", (-10.8, 2.0, Z0 + 6.4), (16.0, 0.45, 0.4), mat("NEXUS_Steel"), 0.02)
    box(f"{PREFIX}CRANE_HOIST", (-7.0, 2.0, Z0 + 5.95), (0.8, 0.6, 0.55), mat("NEXUS_Painted_Metal"), 0.02)
    box(f"{PREFIX}CRANE_CABLE", (-7.0, 2.0, Z0 + 4.8), (0.04, 0.04, 2.3), mat("NEXUS_Rubber"), 0.004)
    # Control desk under the mezzanine.
    box(f"{PREFIX}CONTROL_DESK", (-12.0, 0.0, Z0 + 0.82), (3.4, 1.1, 0.08), mat("NEXUS_Steel"), 0.02)
    for dx in (-1.4, 1.4):
        box(f"{PREFIX}CONTROL_LEG_{dx}", (-12.0 + dx, 0.0, Z0 + 0.42), (0.08, 0.9, 0.8), mat("NEXUS_Painted_Metal"), 0.006)
    for i, x in enumerate((-13.0, -12.0, -11.0)):
        box(f"{PREFIX}CONTROL_MON_{i}", (x, 0.35, Z0 + 1.45), (0.7, 0.06, 0.46), mat("NEXUS_Screen"), 0.01)
    # Crates, barrels and pallets.
    for i, (x, y) in enumerate(((-4.8, 4.8), (-3.9, 5.5), (-5.4, 3.9))):
        box(f"{PREFIX}CRATE_{i}", (x, y, Z0 + 0.45), (0.9, 0.7, 0.9), mat("NEXUS_Rusted_Metal"), 0.015)
    for i, (x, y) in enumerate(((-15.8, 6.4), (-16.6, 6.9), (-18.2, -2.8))):
        cyl(f"{PREFIX}BARREL_{i}", (x, y, Z0 + 0.48), 0.34, 0.96, mat("NEXUS_Rusted_Metal"), "Z", 16)
    box(f"{PREFIX}PALLET", (-7.0, 5.8, Z0 + 0.12), (1.6, 1.0, 0.12), mat("NEXUS_Debris"), 0.01)
    # Debris, cable coils and a small dark spill.
    for i in range(8):
        box(f"{PREFIX}DEBRIS_{i}", (-6.0 + i * 0.45, -1.3 + (i % 3) * 0.3, Z0 + 0.06), (0.18, 0.12, 0.06), mat("NEXUS_Debris"), 0.004)
    for i in range(3):
        cyl(f"{PREFIX}CABLE_COIL_{i}", (4.0 + i * 0.5, -8.6, Z0 + 0.08), 0.42, 0.08, mat("NEXUS_Rubber"), "Z", 20)
    box(f"{PREFIX}SPILL", (-8.4, 1.8, Z0 + 0.01), (1.6, 0.9, 0.02), mat("NEXUS_Blood_Dried"), 0.002)


def pipes_and_lights():
    # Large process pipes along the nave walls and ceiling.
    for i, (y, z, r, m) in enumerate(((-4.6, 6.55, 0.18, "NEXUS_Rusted_Metal"), (8.1, 6.35, 0.14, "NEXUS_Steel"))):
        cyl(f"{PREFIX}PIPE_{i}", (-10.7, y, Z0 + z), r, 17.2, mat(m), "X", 20)
        for j, x in enumerate((-18.5, -14.5, -10.5, -6.5, -2.5)):
            box(f"{PREFIX}PIPE_CLAMP_{i}_{j}", (x, y, Z0 + z), (0.16, 0.4, 0.08), mat("NEXUS_Steel"), 0.004)
    # Cable tray along the east wall.
    box(f"{PREFIX}TRAY", (-1.95, 2.0, Z0 + 5.7), (0.35, 11.0, 0.08), mat("NEXUS_Steel"), 0.006)
    # Emergency and fill lights.
    for i, (loc, e) in enumerate((((-2.5, 8.6, Z0 + 5.6), 80.0), ((-18.5, -4.4, Z0 + 5.4), 65.0))):
        ld = bpy.data.lights.new(f"{PREFIX}EMERGENCY_{i}", "POINT")
        ld.color = (1.0, 0.035, 0.015); ld.energy = e; ld.shadow_soft_size = 0.3
        lo = bpy.data.objects.new(ld.name, ld); DETAIL.objects.link(lo); lo.location = loc
    ld = bpy.data.lights.new(f"{PREFIX}NAVE_FILL", "AREA")
    ld.color = (0.56, 0.78, 1.0); ld.energy = 450.0; ld.shape = "RECTANGLE"; ld.size = 5.0; ld.size_y = 3.0
    lo = bpy.data.objects.new(ld.name, ld); DETAIL.objects.link(lo); lo.location = (-10.7, 2.0, Z0 + 6.7)
    # Under-catwalk strip.
    box(f"{PREFIX}STRIP", (-10.7, 8.15, Z0 + 4.70), (12.0, 0.10, 0.05), mat("NEXUS_CorridorLight"), 0.004)


def signs():
    sign("NAVE", "NAVE DE CONTENCION", (-1.60, 2.0, Z0 + 5.2), (-1, 0, 0), 2.6, 0.36, 0.18, mat("NEXUS_SignText") or mat("NEXUS_Amber"))
    sign("LAB", "NIVEL -2  //  LABORATORIOS", (0.0, 11.9, Z0 + 5.2), (0, -1, 0), 3.2, 0.38, 0.18, mat("NEXUS_SignText") or mat("NEXUS_Amber"))
    sign("AIRLOCK", "ESCLUSA 02", (0.0, -10.9, Z0 + 5.0), (0, 1, 0), 1.8, 0.30, 0.15, mat("NEXUS_SignText") or mat("NEXUS_Amber"))
    # Hide the old mirrored/floating sign texts.
    for n in ("NEXUS_V04_SIGN_NAVE", "NEXUS_V04_SIGN_BIo", "NEXUS_V04_SIGN_LEVEL"):
        o = bpy.data.objects.get(n)
        if o:
            o.hide_render = True
            try: o.hide_set(True)
            except Exception: pass


def camera(name, loc, target, lens):
    cam = bpy.data.objects.get(name)
    if cam is None:
        cd = bpy.data.cameras.new(name)
        cam = bpy.data.objects.new(name, cd)
        DETAIL.objects.link(cam)
    cam.location = Vector(loc)
    cam.data.lens = lens
    f = (Vector(target) - Vector(loc)).normalized()
    up = Vector((0, 0, 1))
    if abs(f.dot(up)) > 0.98: up = Vector((0, 1, 0))
    right = f.cross(up).normalized()
    up2 = right.cross(f).normalized()
    cam.matrix_world = Matrix.Translation(cam.location) @ Matrix((right, up2, -f)).transposed().to_4x4()
    return cam


remove_old()
catwalk()
machinery()
pipes_and_lights()
signs()
c_mezz = camera("NEXUS_V04_CAM_Mezz", (-14.4, 5.2, Z0 + 4.0), (-6.0, 0.5, Z0 + 2.2), 20.0)
c_nave = camera("NEXUS_V04_CAM_Nave", (-3.7, 6.2, Z0 + 3.5), (-11.0, 1.5, Z0 + 2.2), 18.0)
c_corr = camera("NEXUS_V04_CAM_Corridor", (0.0, -9.6, Z0 + 2.1), (5.0, 12.0, Z0 + 2.1), 20.0)
c_tank = camera("NEXUS_V04_CAM_Tank", (-4.0, 5.0, Z0 + 3.0), (-10.7, 1.6, Z0 + 2.2), 24.0)
SCENE.camera = c_nave

try:
    SCENE.view_settings.exposure = 1.15
    SCENE.render.engine = "BLENDER_EEVEE"
    SCENE.eevee.taa_render_samples = 64
    SCENE.render.resolution_x = 1920
    SCENE.render.resolution_y = 1080
except Exception:
    pass

path = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V04_lab_scale_detail.blend")
i = 2
while os.path.exists(path):
    path = os.path.join(ROOT, "blender_concept", f"FM_NEXUS_V04_lab_scale_detail_{i:02d}.blend")
    i += 1
bpy.ops.wm.save_as_mainfile(filepath=path)
print("DETAIL_SAVED", path, os.path.getsize(path), "objects", len(bpy.data.objects))
