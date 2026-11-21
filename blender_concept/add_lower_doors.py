"""Add door leaves to the L3-L5 rooms and the central blocks."""
import bpy
import math
import os

ROOT = "/home/riyo/Documentos/game"
COL = bpy.data.collections.get("NEXUS_LDOORS")
if COL is None:
    COL = bpy.data.collections.new("NEXUS_LDOORS")
    bpy.context.scene.collection.children.link(COL)

ROOMS = [
    # L3
    "ENFERMERIA", "HABITACIONES_MEDICAS", "QUIROFANO", "MORGUE",
    "CAMARAS_FRIGORIFICAS", "AISLAMIENTO_A", "AISLAMIENTO_B",
    # L4
    "ARMERIA_HERRAMIENTAS", "BUNKER_SEGURIDAD", "CONTENCION_PRIMARIA",
    "CONTENCION_SECUNDARIA", "CONTROL_CONTENCION", "LAB_RESTRINGIDO",
    # L5
    "ARCHIVO_SECRETO", "BOMBEO_INUNDACION", "EXTRACCION_PROFUNDA",
    "GENERADORES", "REFRIGERACION", "TUNEL_PROFUNDO",
]


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


def door_frame(prefix):
    a = bpy.data.objects.get(prefix + "_DOOR_FRAME")
    b = bpy.data.objects.get(prefix + "_DOOR_FRAME.001")
    if a is None or b is None:
        # Some rooms may use a different suffix.
        frames = [o for o in bpy.data.objects if o.name.startswith(prefix + "_DOOR_FRAME")]
        if len(frames) < 2:
            return None
        frames.sort(key=lambda o: o.name)
        a, b = frames[0], frames[1]
    return a.matrix_world.translation.copy(), b.matrix_world.translation.copy()


def floor_z(prefix):
    f = bpy.data.objects.get(prefix + "_FLOOR")
    return f.location.z if f else -22.8


def room_center(prefix):
    f = bpy.data.objects.get(prefix + "_FLOOR")
    if f:
        return f.location.copy()
    return None


def add_door(prefix, index):
    pts = door_frame(prefix)
    if not pts:
        print("NO_FRAMES", prefix)
        return
    p1, p2 = pts
    u = (p2 - p1)
    u.z = 0.0
    length = u.length
    if length < 0.8:
        print("BAD_FRAME", prefix)
        return
    u.normalize()
    n = (-u.y, u.x, 0.0)
    c = room_center(prefix)
    if c is not None:
        mid = (p1 + p2) * 0.5
        if (c.x - mid.x) * n[0] + (c.y - mid.y) * n[1] < 0:
            n = (-n[0], -n[1], 0.0)
    # Open 65 degrees into the room, or closed for a few doors.
    open_angle = math.radians(65.0) if index % 3 else 0.0
    # Rotate u toward n by open_angle.
    ca, sa = math.cos(open_angle), math.sin(open_angle)
    # Build an orthonormal 2D basis (u, n) and rotate in it.
    dx = u.x * ca + n[0] * sa
    dy = u.y * ca + n[1] * sa
    hinge = p1
    leaf_len = min(1.55, length - 0.08)
    center = (hinge.x + dx * leaf_len * 0.5,
              hinge.y + dy * leaf_len * 0.5,
              floor_z(prefix) + 1.65)
    leaf = box(f"NEXUS_LDOOR_{prefix}_LEAF", center,
               (leaf_len, 0.07, 3.0), "NEXUS_Painted_Metal", 0.008)
    leaf.rotation_euler[2] = math.atan2(dy, dx)
    # Hinge post.
    box(f"NEXUS_LDOOR_{prefix}_HINGE", (hinge.x, hinge.y, floor_z(prefix) + 1.65),
        (0.08, 0.08, 3.05), "NEXUS_Steel", 0.004)
    # Handle near the free edge.
    hx = hinge.x + dx * (leaf_len - 0.18)
    hy = hinge.y + dy * (leaf_len - 0.18)
    box(f"NEXUS_LDOOR_{prefix}_HANDLE", (hx - n[0] * 0.08, hy - n[1] * 0.08,
                                        floor_z(prefix) + 1.45),
        (0.05, 0.05, 0.28), "NEXUS_Steel", 0.003)
    # Kick plate.
    box(f"NEXUS_LDOOR_{prefix}_KICK", (hx, hy, floor_z(prefix) + 0.32),
        (0.5, 0.02, 0.35), "NEXUS_Steel", 0.002)


def main():
    for i, prefix in enumerate(ROOMS):
        add_door(prefix, i)
    bpy.ops.wm.save_as_mainfile(
        filepath=os.path.join(ROOT, "blender_concept", "FM_NEXUS_V05_level1_v29.blend"))
    print("LOWER_DOORS_SAVED", len(ROOMS))


if __name__ == "__main__":
    main()
