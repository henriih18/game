"""Narrativa ambiental para EXTACCION_PROFUNDA, REFRIGERACION y TUNEL_PROFUNDO (L5)."""
import bpy
import math
import os
from mathutils import Vector, Matrix

ROOT = "/home/riyo/Documentos/game"
SCENE = bpy.context.scene
Z = -43.8
FLOOR = Z + 0.15
COL = bpy.data.collections.get("NEXUS_STORY_LOWER")
if COL is None:
    COL = bpy.data.collections.new("NEXUS_STORY_LOWER")
    SCENE.collection.children.link(COL)


def mat(name):
    return bpy.data.materials.get(name)


if mat("NEXUS_Coolant_Spill") is None:
    coolant = bpy.data.materials.new("NEXUS_Coolant_Spill")
    coolant.use_nodes = True
    bsdf = next(n for n in coolant.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (0.015, 0.085, 0.12, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.06
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Alpha"].default_value = 0.82
    coolant.diffuse_color = (0.015, 0.085, 0.12, 0.82)
    coolant.surface_render_method = "DITHERED"

# Limpieza de una ejecución parcial previa.
for o in list(bpy.data.objects):
    if o.name.startswith(("NEXUS_STORY_EXTRACT_", "NEXUS_STORY_COLD_",
                          "NEXUS_STORY_TUNNEL_", "NEXUS_FILL_EXTRACCION",
                          "NEXUS_FILL_REFRIGERACION", "NEXUS_FILL_TUNEL")):
        bpy.data.objects.remove(o, do_unlink=True)


def box(name, center, size, material, bevel=0.008, rotation=None):
    mesh = bpy.data.meshes.new(name)
    x, y, z = size[0] / 2, size[1] / 2, size[2] / 2
    verts = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
             (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
             (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    COL.objects.link(o)
    o.location = center
    if rotation:
        o.rotation_euler = rotation
    m = mat(material)
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
    m = mat(material)
    if m:
        mesh.materials.append(m)
    return o


def text(name, body, loc, normal, size, material="NEXUS_SignText"):
    n = Vector(normal).normalized()
    up = Vector((0, 0, 1))
    if abs(n.dot(up)) > 0.95:
        up = Vector((0, 1, 0))
    right = up.cross(n).normalized()
    up2 = n.cross(right).normalized()
    rot = Matrix((right, up2, n)).transposed().to_4x4()
    plate = box(name + "_PLATE", tuple(Vector(loc) - n * 0.035),
                (size * 5.4, size * 1.6, 0.05), "NEXUS_SignPlate", 0.005)
    plate.matrix_world = Matrix.Translation(Vector(loc) - n * 0.05) @ rot
    curve = bpy.data.curves.new(name + "_TEXT", type="FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    curve.extrude = 0.003
    o = bpy.data.objects.new(curve.name, curve)
    COL.objects.link(o)
    o.matrix_world = Matrix.Translation(Vector(loc)) @ rot
    m = mat(material)
    if m:
        curve.materials.append(m)


def puddle(name, x, y, sx, sy, material="NEXUS_Blood_Dried", z=FLOOR + 0.011):
    box(name, (x, y, z), (sx, sy, 0.02), material, 0.002)


def body_bag(prefix, x, y, z=FLOOR + 0.08):
    box(prefix + "_BAG", (x, y, z), (0.74, 1.88, 0.16), "NEXUS_BodyBag_Arch", 0.12)
    box(prefix + "_CHEST", (x, y + 0.28, z + 0.10), (0.58, 0.62, 0.14), "NEXUS_BodyBag_Arch", 0.05)
    box(prefix + "_LEGS", (x, y - 0.62, z + 0.07), (0.48, 0.70, 0.12), "NEXUS_BodyBag_Arch", 0.05)
    box(prefix + "_HEAD", (x, y + 0.77, z + 0.10), (0.29, 0.27, 0.14), "NEXUS_BodyBag_Arch", 0.05)
    box(prefix + "_ZIP", (x, y, z + 0.09), (0.035, 1.68, 0.012), "NEXUS_Steel", 0.001)
    box(prefix + "_TAG", (x + 0.28, y + 0.84, z + 0.10), (0.13, 0.09, 0.012), "NEXUS_OffWhite", 0.001)


# ---------------- EXTRACCION_PROFUNDA ----------------
# Cable y gancho bajo el cabrestante.
cyl("NEXUS_STORY_EXTRACT_CABLE", (-7.5, -12.47, -42.48), 0.018, 1.25, "NEXUS_Rubber", "Z", 10)
cyl("NEXUS_STORY_EXTRACT_HOOK_BODY", (-7.5, -12.47, -43.12), 0.075, 0.16, "NEXUS_Steel", "Z", 12)
box("NEXUS_STORY_EXTRACT_HOOK_TIP", (-7.5, -12.40, -43.22), (0.05, 0.16, 0.05), "NEXUS_Steel", 0.006)

# Bolsa junto a la jaula y rastro hacia la puerta.
body_bag("NEXUS_STORY_EXTRACT_CORPSE", -10.35, -15.05)
for i, (x, y) in enumerate(((-9.5, -14.4), (-8.9, -13.5), (-8.2, -12.5),
                            (-7.9, -11.4), (-7.7, -10.4), (-7.55, -9.55))):
    puddle(f"NEXUS_STORY_EXTRACT_BLOOD_{i}", x, y, 0.48 - i * 0.02, 0.30)

# Cajas, herramienta y manifiesto.
box("NEXUS_STORY_EXTRACT_CRATE_0", (-11.55, -15.35, FLOOR + 0.36), (0.95, 0.72, 0.72), "NEXUS_Wood", 0.012)
box("NEXUS_STORY_EXTRACT_CRATE_1", (-11.62, -14.40, FLOOR + 0.28), (0.70, 0.54, 0.56), "NEXUS_Wood", 0.012)
box("NEXUS_STORY_EXTRACT_TOOLBOX", (-11.55, -12.90, FLOOR + 0.15), (0.62, 0.34, 0.30), "NEXUS_Red_Matte", 0.01)
box("NEXUS_STORY_EXTRACT_MANIFEST", (-4.10, -13.95, FLOOR + 0.007), (0.36, 0.26, 0.014), "NEXUS_OffWhite", 0.001, (0, 0, 0.25))
box("NEXUS_STORY_EXTRACT_PAPER", (-3.58, -14.10, FLOOR + 0.006), (0.28, 0.22, 0.012), "NEXUS_OffWhite", 0.001, (0, 0, -0.35))

# Loot sobre la consola.
box("NEXUS_STORY_EXTRACT_LOOT", (-3.75, -13.10, -42.692), (0.36, 0.28, 0.10), "NEXUS_Clinical", 0.008)
box("NEXUS_STORY_EXTRACT_LOOT_STRIP", (-3.75, -13.10, -42.635), (0.30, 0.05, 0.014), "NEXUS_Amber", 0.001)

# Baliza ámbar y cartel.
box("NEXUS_STORY_EXTRACT_BEACON", (-10.9, -9.16, -41.25), (0.22, 0.08, 0.14), "NEXUS_Amber", 0.006)
light = bpy.data.lights.new("NEXUS_STORY_EXTRACT_BEACON_LIGHT", "POINT")
light.energy = 24.0
light.color = (1.0, 0.42, 0.10)
light.shadow_soft_size = 0.2
lo = bpy.data.objects.new(light.name, light)
COL.objects.link(lo)
lo.location = (-10.9, -9.35, -41.20)
text("NEXUS_STORY_EXTRACT_SIGN", "EXTRACCION // PLATAFORMA 05", (-12.78, -13.0, -41.55), (1, 0, 0), 0.12)

# Relleno frío de trabajo.
fill = bpy.data.lights.new("NEXUS_FILL_EXTRACCION", "AREA")
fill.energy = 290.0
fill.color = (0.70, 0.82, 1.0)
fill.shape = "RECTANGLE"
fill.size = 4.5
fill.size_y = 3.0
fo = bpy.data.objects.new(fill.name, fill)
COL.objects.link(fo)
fo.location = (-7.5, -13.0, -41.05)


# ---------------- REFRIGERACION ----------------
# Fuga de refrigerante y escarcha.
for i, (x, y, r) in enumerate(((-0.25, 14.20, 0.62), (0.35, 13.55, 0.40), (0.95, 13.20, 0.26))):
    cyl(f"NEXUS_STORY_COLD_SPILL_{i}", (x, y, FLOOR + 0.009), r, 0.018, "NEXUS_Coolant_Spill", "Z", 20)
for i, (x, y, sx, sy) in enumerate(((-1.35, 14.10, 0.62, 0.48), (1.65, 14.25, 0.52, 0.40),
                                    (3.90, 14.10, 0.55, 0.42), (5.15, 10.30, 0.48, 0.34))):
    box(f"NEXUS_STORY_COLD_FROST_{i}", (x, y, FLOOR + 0.011), (sx, sy, 0.022), "NEXUS_Frost", 0.002)
# Escarcha sobre la tubería.
cyl("NEXUS_STORY_COLD_PIPE_ICE", (2.05, 11.10, -40.75), 0.15, 1.1, "NEXUS_Frost", "X", 14)

# Cuerpo con abrigo, sentado contra el muro este.
box("NEXUS_STORY_COLD_TORSO", (5.48, 12.15, FLOOR + 0.41), (0.52, 0.38, 0.82), "NEXUS_Jacket", 0.06)
box("NEXUS_STORY_COLD_LEGS", (5.45, 11.35, FLOOR + 0.12), (0.48, 0.95, 0.24), "NEXUS_Jacket", 0.05)
box("NEXUS_STORY_COLD_BOOT_0", (5.38, 10.80, FLOOR + 0.08), (0.20, 0.32, 0.16), "NEXUS_Rubber", 0.03)
box("NEXUS_STORY_COLD_BOOT_1", (5.62, 10.80, FLOOR + 0.08), (0.20, 0.32, 0.16), "NEXUS_Rubber", 0.03)
cyl("NEXUS_STORY_COLD_HEAD", (5.47, 12.10, FLOOR + 0.94), 0.145, 0.24, "NEXUS_Skin_Pale", "Z", 16)
box("NEXUS_STORY_COLD_FROST_BODY", (5.48, 12.15, FLOOR + 0.72), (0.34, 0.24, 0.025), "NEXUS_Frost", 0.002)

# Carro y herramienta.
box("NEXUS_STORY_COLD_CART", (-1.20, 12.30, FLOOR + 0.48), (0.80, 0.52, 0.06), "NEXUS_Steel", 0.008)
for i, (dx, dy) in enumerate(((-0.32, -0.20), (0.32, -0.20), (-0.32, 0.20), (0.32, 0.20))):
    box(f"NEXUS_STORY_COLD_CART_LEG_{i}", (-1.20 + dx, 12.30 + dy, FLOOR + 0.24), (0.04, 0.04, 0.48), "NEXUS_Steel", 0.003)
box("NEXUS_STORY_COLD_TOOLBOX", (-1.20, 12.30, FLOOR + 0.56), (0.46, 0.28, 0.16), "NEXUS_Red_Matte", 0.008)

# Válvula de la tubería.
cyl("NEXUS_STORY_COLD_VALVE", (4.25, 11.10, -40.75), 0.18, 0.06, "NEXUS_Red", "X", 14)
for i, ang in enumerate((0, math.pi / 2)):
    box(f"NEXUS_STORY_COLD_VALVE_SPOKE_{i}", (4.29, 11.10, -40.75), (0.035, 0.34, 0.035), "NEXUS_Red", 0.002, (ang, 0, 0))

# Loot criogénico sobre la unidad este.
box("NEXUS_STORY_COLD_LOOT", (4.25, 15.50, -41.355), (0.38, 0.30, 0.14), "NEXUS_Clinical", 0.008)
box("NEXUS_STORY_COLD_LOOT_STRIP", (4.25, 15.50, -41.278), (0.30, 0.05, 0.014), "NEXUS_Amber", 0.001)

# Baliza fría, cartel y relleno.
box("NEXUS_STORY_COLD_BEACON", (-1.72, 10.20, -41.35), (0.20, 0.07, 0.13), "NEXUS_ColdStrip", 0.005)
light = bpy.data.lights.new("NEXUS_STORY_COLD_BEACON_LIGHT", "POINT")
light.energy = 22.0
light.color = (0.35, 0.62, 1.0)
light.shadow_soft_size = 0.22
lo = bpy.data.objects.new(light.name, light)
COL.objects.link(lo)
lo.location = (-1.72, 10.0, -41.30)
text("NEXUS_STORY_COLD_SIGN", "REFRIGERACION // -18 C", (4.30, 9.16, -41.25), (0, 1, 0), 0.12)

fill = bpy.data.lights.new("NEXUS_FILL_REFRIGERACION", "AREA")
fill.energy = 310.0
fill.color = (0.52, 0.72, 1.0)
fill.shape = "RECTANGLE"
fill.size = 5.0
fill.size_y = 3.0
fo = bpy.data.objects.new(fill.name, fill)
COL.objects.link(fo)
fo.location = (2.0, 13.0, -41.10)


# ---------------- TUNEL_PROFUNDO ----------------
# Derrumbe al fondo este.
for i, (x, y, sx, sy, sz, rz) in enumerate(((10.25, -13.20, 1.10, 0.90, 0.55, 0.22),
                                            (10.35, -11.90, 0.95, 0.80, 0.42, -0.30),
                                            (9.30, -10.10, 1.10, 0.65, 0.38, 0.45),
                                            (10.50, -14.40, 0.90, 0.70, 0.34, -0.15))):
    box(f"NEXUS_STORY_TUNNEL_ROCK_{i}", (x, y, FLOOR + sz / 2 + 0.01), (sx, sy, sz), "NEXUS_Debris", 0.03, (0, 0, rz))
box("NEXUS_STORY_TUNNEL_FALLEN_BEAM", (9.35, -12.45, FLOOR + 0.12), (0.24, 4.20, 0.24), "NEXUS_Rusted_Metal", 0.01, (0, 0, 0.38))
box("NEXUS_STORY_TUNNEL_COLLAPSE_DUST", (9.80, -12.60, FLOOR + 0.011), (2.3, 4.0, 0.02), "NEXUS_Grime", 0.001)

# Bolsa atrapada bajo el derrumbe.
body_bag("NEXUS_STORY_TUNNEL_CORPSE", 9.55, -13.85)
box("NEXUS_STORY_TUNNEL_CORPSE_ROCK", (9.70, -14.25, FLOOR + 0.16), (0.70, 0.52, 0.32), "NEXUS_Debris", 0.02, (0, 0, 0.18))

# Rastro de sangre desde el derrumbe hacia la puerta.
for i, (x, y, sx, sy) in enumerate(((8.85, -13.65, 0.52, 0.34), (7.85, -13.05, 0.48, 0.30),
                                    (6.70, -12.40, 0.42, 0.28), (5.55, -11.60, 0.38, 0.24),
                                    (4.85, -10.65, 0.34, 0.22), (4.58, -9.75, 0.30, 0.20))):
    puddle(f"NEXUS_STORY_TUNNEL_BLOOD_{i}", x, y, sx, sy)

# Cable colgante.
cyl("NEXUS_STORY_TUNNEL_CABLE", (6.85, -14.25, -41.25), 0.018, 2.40, "NEXUS_Rubber", "Z", 8)
box("NEXUS_STORY_TUNNEL_CABLE_END", (6.85, -14.25, -42.44), (0.08, 0.05, 0.16), "NEXUS_Steel", 0.004)

# Cajas de perforación y loot geológico.
box("NEXUS_STORY_TUNNEL_CRATE_0", (0.10, -14.55, FLOOR + 0.30), (0.90, 0.64, 0.60), "NEXUS_Wood", 0.012)
box("NEXUS_STORY_TUNNEL_CRATE_1", (1.10, -14.75, FLOOR + 0.24), (0.70, 0.54, 0.48), "NEXUS_Wood", 0.012)
box("NEXUS_STORY_TUNNEL_DRILL", (-1.10, -14.30, FLOOR + 0.18), (0.55, 0.30, 0.36), "NEXUS_Rusted_Metal", 0.01)
box("NEXUS_STORY_TUNNEL_LOOT", (0.10, -14.55, FLOOR + 0.66), (0.40, 0.30, 0.12), "NEXUS_Clinical", 0.008)
box("NEXUS_STORY_TUNNEL_LOOT_STRIP", (0.10, -14.55, FLOOR + 0.727), (0.32, 0.05, 0.014), "NEXUS_Amber", 0.001)

# Cinta de peligro y cartel.
for i, (x, y, h) in enumerate(((8.55, -15.45, -42.80), (8.55, -9.55, -42.80))):
    cyl(f"NEXUS_STORY_TUNNEL_TAPE_POST_{i}", (x, y, FLOOR + 0.55), 0.035, 1.10, "NEXUS_Painted_Metal", "Z", 10)
box("NEXUS_STORY_TUNNEL_TAPE", (8.55, -12.50, FLOOR + 0.95), (0.035, 5.90, 0.07), "NEXUS_Amber", 0.002)
text("NEXUS_STORY_TUNNEL_SIGN", "TUNEL // SECTOR COLAPSADO", (2.20, -9.12, -41.30), (0, 1, 0), 0.11)

# Baliza y relleno cálido.
box("NEXUS_STORY_TUNNEL_BEACON", (3.35, -9.16, -41.30), (0.22, 0.08, 0.14), "NEXUS_Red", 0.006)
light = bpy.data.lights.new("NEXUS_STORY_TUNNEL_BEACON_LIGHT", "POINT")
light.energy = 24.0
light.color = (1.0, 0.06, 0.03)
light.shadow_soft_size = 0.22
lo = bpy.data.objects.new(light.name, light)
COL.objects.link(lo)
lo.location = (3.35, -9.35, -41.25)
fill = bpy.data.lights.new("NEXUS_FILL_TUNEL", "AREA")
fill.energy = 280.0
fill.color = (1.0, 0.55, 0.30)
fill.shape = "RECTANGLE"
fill.size = 6.0
fill.size_y = 3.0
fo = bpy.data.objects.new(fill.name, fill)
COL.objects.link(fo)
fo.location = (4.5, -12.5, -41.05)

# Ajuste de luces de sala para que las tres salas se lean.
for name, color, energy in (
    ("EXTRACCION_PROFUNDA_LIGHT_AREA", (0.68, 0.80, 1.0), 320.0),
    ("REFRIGERACION_LIGHT_AREA", (0.54, 0.72, 1.0), 280.0),
    ("TUNEL_PROFUNDO_LIGHT_AREA", (1.0, 0.34, 0.14), 280.0),
):
    o = bpy.data.objects.get(name)
    if o:
        o.data.color = color
        o.data.energy = energy

bpy.context.scene.camera = bpy.data.objects.get("TMP_STORY_CAM") or bpy.context.scene.camera
path = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V05_level1_v76.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
print("STORY_L5_B_DONE", len(COL.objects), path, os.path.getsize(path))
