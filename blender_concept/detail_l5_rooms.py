"""Detail the three remaining L5 rooms and fix small story-prop contacts.

Rooms: EXTRACCION_PROFUNDA, REFRIGERACION, TUNEL_PROFUNDO.
Saves FM_NEXUS_V05_level1_v78.blend.
"""
import bpy
import bmesh
import math
import os
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
Z = -43.8
FLOOR = -43.65
P = "NEXUS_POLISH_L5_"

col = bpy.data.collections.get("NEXUS_L5_POLISH")
if col is None:
    col = bpy.data.collections.new("NEXUS_L5_POLISH")
    bpy.context.scene.collection.children.link(col)


def mat(name):
    return bpy.data.materials.get(name)


def make_mat(name, base, rough=0.6, metal=0.0):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
    bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*base, 1.0)
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metal
    m.diffuse_color = (*base, 1.0)
    return m


COPPER = make_mat("NEXUS_Copper", (0.33, 0.12, 0.045), 0.32, 0.85)
DARK = make_mat("NEXUS_Dark_Metal", (0.018, 0.024, 0.027), 0.5, 0.65)
BLOOD = make_mat("NEXUS_Blood_Dark", (0.075, 0.002, 0.003), 0.42, 0.0)


def box(name, center, size, material, bevel=0.006, rot=None):
    me = bpy.data.meshes.new(name)
    x, y, z = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
    vs = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
          (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    fs = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
          (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    me.from_pydata(vs, [], fs)
    me.update()
    o = bpy.data.objects.new(name, me)
    col.objects.link(o)
    o.location = center
    if rot:
        o.rotation_euler = rot
    if material:
        me.materials.append(material)
    if bevel > 0:
        md = o.modifiers.new("Bevel", "BEVEL")
        md.width = bevel
        md.segments = 1
    return o


def cyl(name, center, radius, depth, material, axis="Z", verts=20):
    me = bpy.data.meshes.new(name)
    vs = []
    for zz in (-depth * 0.5, depth * 0.5):
        for i in range(verts):
            a = 2 * math.pi * i / verts
            vs.append((math.cos(a) * radius, math.sin(a) * radius, zz))
    fs = []
    for i in range(verts):
        j = (i + 1) % verts
        fs.append((i, j, verts + j, verts + i))
    fs.append(tuple(range(verts - 1, -1, -1)))
    fs.append(tuple(range(verts, verts * 2)))
    me.from_pydata(vs, [], fs)
    me.update()
    o = bpy.data.objects.new(name, me)
    col.objects.link(o)
    o.location = center
    if axis == "X":
        o.rotation_euler.y = math.pi / 2
    elif axis == "Y":
        o.rotation_euler.x = math.pi / 2
    if material:
        me.materials.append(material)
    return o


def ring(name, center, r_out, r_in, depth, material, axis="Y", seg=28):
    me = bpy.data.meshes.new(name)
    vs = []
    for zz in (-depth * 0.5, depth * 0.5):
        for i in range(seg):
            a = 2 * math.pi * i / seg
            vs.append((math.cos(a) * r_out, math.sin(a) * r_out, zz))
        for i in range(seg):
            a = 2 * math.pi * i / seg
            vs.append((math.cos(a) * r_in, math.sin(a) * r_in, zz))
    off = seg * 2
    fs = []
    for i in range(seg):
        j = (i + 1) % seg
        fs.append((i, j, off + j, off + i))                       # top
        fs.append((seg + i, seg + j, seg + off + j, seg + off + i))  # bottom
        fs.append((i, seg + i, seg + j, j))                        # outer
        fs.append((off + i, off + seg + i, off + seg + j, off + j))  # inner
    me.from_pydata(vs, [], fs)
    me.update()
    o = bpy.data.objects.new(name, me)
    col.objects.link(o)
    o.location = center
    if axis == "X":
        o.rotation_euler.y = math.pi / 2
    elif axis == "Y":
        o.rotation_euler.x = math.pi / 2
    if material:
        me.materials.append(material)
    return o


def sphere(name, center, radius, material, scale=(1, 1, 1)):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=12, radius=radius)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    col.objects.link(o)
    o.location = center
    o.scale = scale
    if material:
        me.materials.append(material)
    return o


# Clean any previous run.
for o in list(bpy.data.objects):
    if o.name.startswith(P):
        bpy.data.objects.remove(o, do_unlink=True)

# Fix small contacts left by the previous pass.
for name, dx in (("NEXUS_STORY_TUNNEL_COLLAPSE_DUST", -0.10),
                 ("NEXUS_STORY_TUNNEL_ROCK_0", -0.05)):
    o = bpy.data.objects.get(name)
    if o:
        o.location.x += dx
o = bpy.data.objects.get("NEXUS_STORY_EXTRACT_LOOT")
if o:
    o.location.z = -42.61
o = bpy.data.objects.get("NEXUS_STORY_EXTRACT_LOOT_STRIP")
if o:
    o.location.z = -42.555

# ---------------------------------------------------------------- EXTRACCION
steel = mat("NEXUS_Steel")
rust = mat("NEXUS_Rusted_Metal")
paint = mat("NEXUS_Painted_Metal")
rubber = mat("NEXUS_Rubber")
amber = mat("NEXUS_Amber")
red = mat("NEXUS_Red_Matte") or mat("NEXUS_Red")
monitor = mat("NEXUS_MonitorScreen") or mat("NEXUS_Screen")

# Winch drum and mechanical detail.
cyl(P + "WINCH_DRUM", (-7.5, -12.55, -42.48), 0.48, 1.18, steel, "X", 28)
cyl(P + "WINCH_FLANGE_L", (-8.11, -12.55, -42.48), 0.61, 0.10, rust, "X", 28)
cyl(P + "WINCH_FLANGE_R", (-6.89, -12.55, -42.48), 0.61, 0.10, rust, "X", 28)
for i, x in enumerate((-7.90, -7.50, -7.10)):
    cyl(P + f"WINCH_CABLE_{i}", (x, -12.55, -42.48), 0.50, 0.07, rubber, "X", 24)
box(P + "WINCH_GUIDE", (-7.5, -12.64, -42.02), (2.20, 0.09, 0.09), steel, 0.004)
for i, x in enumerate((-8.50, -6.50)):
    box(P + f"WINCH_GUIDE_POST_{i}", (x, -12.64, -42.40), (0.09, 0.09, 0.80), steel, 0.004)
box(P + "WINCH_MOTOR", (-7.5, -11.10, -41.56), (1.18, 0.90, 0.48), paint, 0.012)
cyl(P + "WINCH_GEARBOX", (-8.48, -11.40, -42.36), 0.38, 0.24, paint, "X", 24)
box(P + "WINCH_CONTROL", (-6.14, -11.80, -42.45), (0.12, 0.46, 0.56), red, 0.008)
for i, yy in enumerate((-11.96, -11.80, -11.64)):
    cyl(P + f"WINCH_BUTTON_{i}", (-6.07, yy, -42.45), 0.035, 0.025, amber, "X", 14)
for i, yy in enumerate((-11.18, -11.62, -12.02)):
    cyl(P + f"WINCH_HOSE_{i}", (-6.13, yy, -42.84), 0.034, 1.10, rubber, "Z", 12)
for i, x in enumerate((-8.35, -7.50, -6.65)):
    box(P + f"WINCH_HAZARD_{i}", (x, -12.415, -43.55), (0.62, 0.035, 0.18), amber, 0.002)
box(P + "WINCH_CAUTION", (-7.5, -12.425, -41.98), (0.62, 0.035, 0.20), amber, 0.003)
box(P + "WINCH_CAUTION_DARK", (-7.5, -12.445, -41.98), (0.54, 0.015, 0.05), DARK, 0.001)

# Cage structure and gate.
for i, (x, y) in enumerate(((-8.5, -15.5), (-6.5, -15.5), (-8.5, -13.7), (-6.5, -13.7))):
    box(P + f"CAGE_POST_{i}", (x, y, -42.15), (0.12, 0.12, 3.0), steel, 0.004)
for zz in (-42.05, -41.20, -40.72):
    box(P + f"CAGE_RAIL_N_{int(abs(zz)*10)}", (-7.5, -13.70, zz), (2.10, 0.06, 0.06), steel, 0.003)
    box(P + f"CAGE_RAIL_S_{int(abs(zz)*10)}", (-7.5, -15.50, zz), (2.10, 0.06, 0.06), steel, 0.003)
    box(P + f"CAGE_RAIL_E_{int(abs(zz)*10)}", (-6.50, -14.60, zz), (0.06, 1.90, 0.06), steel, 0.003)
    box(P + f"CAGE_RAIL_W_{int(abs(zz)*10)}", (-8.50, -14.60, zz), (0.06, 1.90, 0.06), steel, 0.003)
box(P + "CAGE_FLOOR", (-7.5, -14.60, -43.585), (2.10, 1.90, 0.10), steel, 0.010)
for i, yy in enumerate((-13.72, -13.96, -14.20, -14.44)):
    box(P + f"CAGE_GATE_BAR_{i}", (-7.5, -13.68, -41.55 - i * 0.34), (1.72, 0.06, 0.06), rust, 0.003)
box(P + "CAGE_SIGN", (-7.5, -15.545, -41.30), (0.80, 0.035, 0.26), amber, 0.003)
box(P + "CAGE_SIGN_BAR", (-7.5, -15.565, -41.30), (0.68, 0.012, 0.06), DARK, 0.001)
cyl(P + "CAGE_PULLEY", (-7.5, -14.60, -40.42), 0.24, 0.14, rust, "X", 20)
box(P + "CAGE_PULLEY_BRACKET", (-7.5, -14.60, -40.30), (0.12, 0.62, 0.18), steel, 0.004)

# Work light over the cage.
cyl(P + "WORKLIGHT_CABLE", (-7.6, -14.35, -40.72), 0.018, 0.70, rubber, "Z", 10)
cyl(P + "WORKLIGHT_SHADE", (-7.6, -14.35, -41.14), 0.27, 0.22, rust, "Z", 20)
cyl(P + "WORKLIGHT_BULB", (-7.6, -14.35, -41.27), 0.12, 0.05, amber, "Z", 16)
ld = bpy.data.lights.new(P + "WORKLIGHT", "POINT")
ld.energy = 90
ld.color = (1.0, 0.63, 0.30)
ld.shadow_soft_size = 0.20
lo = bpy.data.objects.new(ld.name, ld)
col.objects.link(lo)
lo.location = (-7.6, -14.35, -41.30)

# Console bezels, buttons and keyboard.
for i, x in enumerate((-4.43, -3.98, -3.53)):
    box(P + f"CONSOLE_BEZEL_T_{i}", (x, -12.79, -42.155), (0.58, 0.04, 0.045), DARK, 0.002)
    box(P + f"CONSOLE_BEZEL_B_{i}", (x, -12.79, -42.545), (0.58, 0.04, 0.045), DARK, 0.002)
    box(P + f"CONSOLE_BEZEL_L_{i}", (x - 0.285, -12.79, -42.35), (0.045, 0.04, 0.42), DARK, 0.002)
    box(P + f"CONSOLE_BEZEL_R_{i}", (x + 0.285, -12.79, -42.35), (0.045, 0.04, 0.42), DARK, 0.002)
    for j, xx in enumerate((-0.14, 0.0, 0.14)):
        cyl(P + f"CONSOLE_BTN_{i}_{j}", (x + xx, -12.77, -42.62), 0.025, 0.02, amber, "Y", 12)
box(P + "CONSOLE_KEYBOARD", (-3.98, -12.66, -42.675), (0.64, 0.23, 0.025), DARK, 0.003)
box(P + "CONSOLE_MAT", (-4.00, -12.28, -43.635), (1.25, 0.85, 0.018), rubber, 0.002)

# Dim the excessively bright console screens.
for i in range(3):
    o = bpy.data.objects.get(f"NEXUS_LROOM_EXTRACCION_PROFUNDA_PANEL_SCR_{i}")
    if o and monitor:
        o.data.materials.clear()
        o.data.materials.append(monitor)

# Wall services.
cyl(P + "SOUTH_PIPE", (-8.0, -16.80, -41.55), 0.075, 9.4, rust, "X", 16)
box(P + "SOUTH_CONDUIT", (-12.72, -16.78, -42.05), (0.07, 0.07, 3.2), steel, 0.003)
box(P + "SOUTH_JUNCTION", (-12.72, -16.72, -41.72), (0.30, 0.16, 0.42), paint, 0.006)
box(P + "SOUTH_JUNCTION_FACE", (-12.72, -16.63, -41.72), (0.22, 0.03, 0.28), DARK, 0.002)

# --------------------------------------------------------------- REFRIGERACION
for i, x in enumerate((-0.25, 2.0, 4.25)):
    cyl(P + f"COLD_FAN_RECESS_{i}", (x, 14.955, -42.35), 0.40, 0.035, DARK, "Y", 28)
    ring(P + f"COLD_FAN_RING_{i}", (x, 14.925, -42.35), 0.46, 0.395, 0.05, steel, "Y", 28)
    cyl(P + f"COLD_FAN_HUB_{i}", (x, 14.90, -42.35), 0.085, 0.10, steel, "Y", 16)
    for j, ang in enumerate((0.0, math.pi / 2, math.pi / 4, 3 * math.pi / 4)):
        box(P + f"COLD_FAN_BAR_{i}_{j}", (x, 14.895, -42.35),
            (0.74, 0.025, 0.035), steel, 0.001, rot=(0, ang, 0))
    for j, xx in enumerate((x - 0.72, x + 0.72)):
        cyl(P + f"COLD_COIL_{i}_{j}", (xx, 14.94, -42.40), 0.033, 1.10, COPPER, "Z", 12)
    box(P + f"COLD_UNIT_LABEL_{i}", (x, 14.97, -41.63), (0.62, 0.025, 0.16), amber, 0.002)
    box(P + f"COLD_UNIT_LABEL_DARK_{i}", (x, 14.985, -41.63), (0.52, 0.012, 0.04), DARK, 0.001)
    cyl(P + f"COLD_TOP_PIPE_{i}", (x, 16.35, -41.52), 0.075, 2.60, COPPER, "Y", 14)
cyl(P + "COLD_HEADER", (2.0, 17.55, -41.52), 0.12, 5.8, COPPER, "X", 18)
for i, x in enumerate((-0.25, 2.0, 4.25)):
    cyl(P + f"COLD_HEADER_DROP_{i}", (x, 17.55, -41.02), 0.075, 0.95, COPPER, "Z", 14)

# Floor drain and water.
box(P + "COLD_DRAIN_FRAME", (3.30, 12.55, -43.625), (1.05, 0.62, 0.035), steel, 0.004)
for i in range(5):
    box(P + f"COLD_DRAIN_BAR_{i}", (2.90 + i * 0.20, 12.55, -43.605), (0.06, 0.50, 0.02), DARK, 0.001)
box(P + "COLD_WATER", (3.35, 12.55, -43.632), (0.92, 0.50, 0.012), mat("NEXUS_Meltwater"), 0.0)

# Insulated drum and crates near the entrance.
cyl(P + "COLD_DRUM", (4.95, 10.55, -43.10), 0.36, 1.10, paint, "Z", 20)
cyl(P + "COLD_DRUM_LID", (4.95, 10.55, -42.53), 0.38, 0.08, steel, "Z", 20)
box(P + "COLD_DRUM_STRIPE", (4.95, 10.20, -43.10), (0.56, 0.035, 0.14), amber, 0.002)
box(P + "COLD_CRATE_0", (5.30, 9.45, -43.35), (0.64, 0.56, 0.56), mat("NEXUS_Debris"), 0.006)
box(P + "COLD_CRATE_1", (4.55, 9.40, -43.42), (0.48, 0.45, 0.42), mat("NEXUS_Debris"), 0.006)

# Seated body: coat, arms, hands, head.
h = bpy.data.objects.get("NEXUS_STORY_COLD_HEAD")
if h:
    h.hide_render = True
    try:
        h.hide_set(True)
    except Exception:
        pass
sphere(P + "COLD_HEAD", (5.47, 12.08, -42.70), 0.135, mat("NEXUS_Skin_Pale"), (1.0, 1.05, 0.92))
sphere(P + "COLD_HAIR", (5.47, 12.05, -42.64), 0.139, mat("NEXUS_Hair") or DARK, (1.0, 1.0, 0.55))
box(P + "COLD_COLLAR", (5.47, 12.13, -42.80), (0.56, 0.42, 0.09), mat("NEXUS_Jacket") or DARK, 0.006)
box(P + "COLD_SHOULDER_L", (5.16, 12.15, -42.85), (0.16, 0.50, 0.20), mat("NEXUS_Jacket") or DARK, 0.008)
box(P + "COLD_SHOULDER_R", (5.78, 12.15, -42.85), (0.16, 0.50, 0.20), mat("NEXUS_Jacket") or DARK, 0.008)
box(P + "COLD_ARM_L", (5.16, 11.91, -43.10), (0.15, 0.16, 0.48), mat("NEXUS_Jacket") or DARK, 0.008)
box(P + "COLD_FOREARM_L", (5.16, 11.75, -43.40), (0.13, 0.14, 0.34), mat("NEXUS_Jacket") or DARK, 0.006)
sphere(P + "COLD_HAND_L", (5.16, 11.68, -43.56), 0.085, mat("NEXUS_Skin_Pale"), (0.9, 1.0, 0.8))
box(P + "COLD_ARM_R", (5.78, 11.91, -43.10), (0.15, 0.16, 0.48), mat("NEXUS_Jacket") or DARK, 0.008)
box(P + "COLD_FOREARM_R", (5.78, 11.75, -43.40), (0.13, 0.14, 0.34), mat("NEXUS_Jacket") or DARK, 0.006)
sphere(P + "COLD_HAND_R", (5.78, 11.68, -43.56), 0.085, mat("NEXUS_Skin_Pale"), (0.9, 1.0, 0.8))
box(P + "COLD_ZIP", (5.27, 12.15, -43.18), (0.012, 0.04, 0.62), steel, 0.001)
box(P + "COLD_BADGE", (5.33, 12.27, -43.03), (0.01, 0.12, 0.08), amber, 0.001)
box(P + "COLD_BELT", (5.47, 12.15, -43.55), (0.52, 0.40, 0.07), DARK, 0.003)
box(P + "COLD_KNEE_L", (5.30, 11.43, -43.35), (0.20, 0.28, 0.24), mat("NEXUS_Jacket") or DARK, 0.008)
box(P + "COLD_KNEE_R", (5.65, 11.43, -43.35), (0.20, 0.28, 0.24), mat("NEXUS_Jacket") or DARK, 0.008)

# ---------------------------------------------------------------- TUNEL
# Overhead cable tray and supports.
box(P + "TUNNEL_TRAY", (4.5, -12.50, -40.42), (12.40, 0.38, 0.08), steel, 0.004)
for i, x in enumerate((-1.0, 3.0, 7.0, 10.0)):
    box(P + f"TUNNEL_TRAY_BRACKET_{i}", (x, -12.50, -40.25), (0.08, 0.52, 0.28), steel, 0.003)
# South wall conduit and drainage.
cyl(P + "TUNNEL_CONDUIT", (4.5, -15.82, -41.55), 0.075, 12.4, rust, "X", 16)
box(P + "TUNNEL_WALL_BOX", (0.20, -15.78, -41.70), (0.34, 0.18, 0.46), paint, 0.006)
box(P + "TUNNEL_WALL_BOX_FACE", (0.20, -15.68, -41.70), (0.26, 0.035, 0.32), DARK, 0.002)
for i, x in enumerate((1.4, 5.0, 8.6)):
    box(P + f"TUNNEL_DRAIN_WALL_{i}", (x, -14.72, -43.58), (1.25, 0.08, 0.10), steel, 0.002)
    box(P + f"TUNNEL_WATER_{i}", (x, -14.55, -43.632), (1.05, 0.26, 0.012), mat("NEXUS_Meltwater"), 0.0)
# Additional rubble along the south wall and near the collapse.
for i, (x, y, sx, sy, sz) in enumerate((
        (2.2, -15.55, 0.55, 0.32, 0.18),
        (3.0, -15.52, 0.40, 0.28, 0.14),
        (7.4, -15.45, 0.70, 0.38, 0.22),
        (8.2, -15.35, 0.48, 0.30, 0.16),
        (9.0, -15.30, 0.62, 0.36, 0.20))):
    box(P + f"TUNNEL_RUBBLE_{i}", (x, y, FLOOR + sz * 0.5), (sx, sy, sz), mat("NEXUS_Debris"), 0.012,
        rot=(0, 0, i * 0.24))
# Rebar at the collapse.
for i, (yy, zz) in enumerate(((-13.7, -41.15), (-12.9, -41.45), (-12.1, -41.10), (-11.3, -41.38))):
    cyl(P + f"TUNNEL_REBAR_{i}", (10.55, yy, zz), 0.025, 1.25, rust, "X", 10)
# Fallen ceiling panels.
for i, (x, y, zz, ry) in enumerate(((9.1, -12.3, -40.55, 0.28),
                                    (9.6, -13.2, -40.42, -0.22),
                                    (8.8, -13.9, -40.62, 0.35))):
    box(P + f"TUNNEL_CEILING_PANEL_{i}", (x, y, zz), (1.20, 0.72, 0.05), DARK, 0.004,
        rot=(0.18, ry, 0.10))
# Hazard bands on the portal posts.
for i, x in enumerate((0.6, 4.5, 8.4)):
    for j, yy in enumerate((-15.30, -9.70)):
        box(P + f"TUNNEL_FRAME_HAZ_{i}_{j}", (x, yy, FLOOR + 0.55), (0.34, 0.34, 0.20), amber, 0.002)
# Tool spool and jack.
cyl(P + "TUNNEL_SPOOL", (2.05, -13.55, -43.22), 0.38, 0.34, rubber, "Y", 18)
cyl(P + "TUNNEL_SPOOL_CORE", (2.05, -13.55, -43.22), 0.12, 0.40, steel, "Y", 14)
box(P + "TUNNEL_JACK_BASE", (7.0, -14.85, -43.60), (0.52, 0.52, 0.08), steel, 0.004)
box(P + "TUNNEL_JACK_POST", (7.0, -14.85, -42.95), (0.11, 0.11, 1.22), rust, 0.004)
box(P + "TUNNEL_JACK_TOP", (7.0, -14.85, -40.65), (0.34, 0.34, 0.09), steel, 0.004)
# Emergency light at the collapse.
box(P + "TUNNEL_EMERGENCY_BOX", (10.78, -12.50, -41.10), (0.09, 0.34, 0.20), rust, 0.003)
cyl(P + "TUNNEL_EMERGENCY_LENS", (10.72, -12.50, -41.10), 0.075, 0.04, red, "X", 14)
ld = bpy.data.lights.new(P + "TUNNEL_EMERGENCY_LIGHT", "POINT")
ld.energy = 55
ld.color = (1.0, 0.035, 0.02)
ld.shadow_soft_size = 0.25
lo = bpy.data.objects.new(ld.name, ld)
col.objects.link(lo)
lo.location = (10.45, -12.50, -41.10)
box(P + "TUNNEL_COLLAPSE_SIGN", (10.72, -11.80, -41.45), (0.06, 0.42, 0.22), amber, 0.002)

# Extra dark blood smears over the existing trail.
for i, (x, y, sx, sy) in enumerate(((8.40, -13.45, 0.30, 0.20),
                                    (7.30, -12.85, 0.28, 0.18),
                                    (6.10, -12.05, 0.25, 0.16),
                                    (5.05, -11.10, 0.22, 0.14))):
    box(P + f"TUNNEL_BLOOD_DARK_{i}", (x, y, -43.635), (sx, sy, 0.012), BLOOD, 0.004,
        rot=(0, 0, i * 0.45))

# Light balance: keep the emergency tint but make props legible.
o = bpy.data.objects.get("TUNEL_PROFUNDO_LIGHT_AREA")
if o and o.type == "LIGHT":
    o.data.color = (1.0, 0.18, 0.06)
    o.data.energy = 240
o = bpy.data.objects.get("NEXUS_FILL_TUNEL")
if o and o.type == "LIGHT":
    o.data.color = (1.0, 0.67, 0.44)
    o.data.energy = 300

print("L5_ROOMS_DETAILED", len([o for o in bpy.data.objects if o.name.startswith(P)]))

path = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V05_level1_v78.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
print("V78_SAVED", path, os.path.getsize(path))
