"""Cut real observation windows into the north walls of AISLAMIENTO_A/B."""
import bpy

Z = -22.8
H = 3.6
ZT = Z + H
WIN_BOTTOM = Z + 1.1
WIN_TOP = WIN_BOTTOM + 1.2
WIN_MID = (WIN_BOTTOM + WIN_TOP) * 0.5
COL = bpy.data.collections.get("NEXUS_LROOM_AISLAMIENTO_A")
if COL is None:
    COL = bpy.data.collections.get("NEXUS_STORY_LOWER") or bpy.context.scene.collection


def mat(name):
    return bpy.data.materials.get(name)


def box(name, center, size, material, bevel=0.006, col=None):
    mesh = bpy.data.meshes.new(name)
    x, y, z = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
    verts = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
             (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    (col or COL).objects.link(obj)
    obj.location = center
    m = mat(material)
    if m:
        mesh.materials.append(m)
    if bevel > 0:
        mod = obj.modifiers.new("Bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 1
    return obj


def window(name, cx, x0, x1):
    # Remove the original solid segment that blocks the opening.
    old = bpy.data.objects.get(name + "_WALL_OLD")
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    # Lower wall under the window: full pier width.
    box(name + "_WIN_LOWER", (cx, -9.0, Z + 0.55),
        (abs(x1 - x0), 0.28, 1.1), "NEXUS_Concrete")
    # Upper lintel only over the opening.
    box(name + "_WIN_UPPER", ((x0 + x1) * 0.5, -9.0, WIN_TOP + 0.65),
        (x1 - x0, 0.28, ZT - WIN_TOP), "NEXUS_Concrete")
    # Side piers.
    left_w = x0 - (cx - 1.5875)
    right_w = (cx + 1.5875) - x1
    if left_w > 0.01:
        box(name + "_WIN_PIER_L", (x0 - left_w * 0.5, -9.0, Z + H * 0.5),
            (left_w, 0.28, H), "NEXUS_Concrete")
    if right_w > 0.01:
        box(name + "_WIN_PIER_R", (x1 + right_w * 0.5, -9.0, Z + H * 0.5),
            (right_w, 0.28, H), "NEXUS_Concrete")
    # Frame, glass, mullion and interior sill.
    w = x1 - x0
    box(name + "_WIN_FRAME_L", (x0 + 0.04, -9.0, WIN_MID), (0.08, 0.18, 1.2), "NEXUS_Painted_Metal", 0.004)
    box(name + "_WIN_FRAME_R", (x1 - 0.04, -9.0, WIN_MID), (0.08, 0.18, 1.2), "NEXUS_Painted_Metal", 0.004)
    box(name + "_WIN_FRAME_T", ((x0 + x1) * 0.5, -9.0, WIN_TOP - 0.04), (w, 0.18, 0.08), "NEXUS_Painted_Metal", 0.004)
    box(name + "_WIN_FRAME_B", ((x0 + x1) * 0.5, -9.0, WIN_BOTTOM + 0.04), (w, 0.18, 0.08), "NEXUS_Painted_Metal", 0.004)
    box(name + "_WIN_GLASS", ((x0 + x1) * 0.5, -9.0, WIN_MID), (w - 0.16, 0.035, 1.04), "NEXUS_Glass", 0.0)
    box(name + "_WIN_MULLION", ((x0 + x1) * 0.5, -9.0, WIN_MID), (0.05, 0.12, 1.04), "NEXUS_Painted_Metal", 0.002)
    box(name + "_WIN_SILL", ((x0 + x1) * 0.5, -8.82, WIN_BOTTOM - 0.03), (w + 0.16, 0.3, 0.06), "NEXUS_Steel", 0.004)


# Remove any partial window assembly from a previous run.
for prefix in ("AISLAMIENTO_A_WIN_", "AISLAMIENTO_B_WIN_"):
    for o in list(bpy.data.objects):
        if o.name.startswith(prefix):
            bpy.data.objects.remove(o, do_unlink=True)

# A: replace the left north segment (x -11..-7.825), opening x -10.4..-8.4.
old_a = bpy.data.objects.get("AISLAMIENTO_A_WALL_N-1")
if old_a:
    old_a.name = "AISLAMIENTO_A_WALL_OLD"
window("AISLAMIENTO_A", -9.4125, -10.4, -8.4)

# B: replace the right north segment (x 1.825..5.0), opening x 2.5..4.5.
old_b = bpy.data.objects.get("AISLAMIENTO_B_WALL_N1")
if old_b:
    old_b.name = "AISLAMIENTO_B_WALL_OLD"
window("AISLAMIENTO_B", 3.4125, 2.5, 4.5)

# Remove the old floating panels.
for n in ("NEXUS_LROOM_AISLAMIENTO_A_WINDOW", "NEXUS_LROOM_AISLAMIENTO_B_WINDOW"):
    o = bpy.data.objects.get(n)
    if o:
        bpy.data.objects.remove(o, do_unlink=True)

bpy.ops.wm.save_as_mainfile(filepath="/home/riyo/Documentos/game/blender_concept/FM_NEXUS_V05_level1_v54.blend")
print("ISOLATION_WINDOWS_SAVED")
