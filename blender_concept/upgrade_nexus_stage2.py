"""Stage 2: detail the NEXUS server room as a representative quality sector."""
import bpy
import os
from mathutils import Vector, Matrix

ROOT = "/home/riyo/Documentos/game"
SCENE = bpy.context.scene
COL_FURN = bpy.data.collections.get("03_DECOR_FURNITURE")
COL_TECH = bpy.data.collections.get("04_DECOR_TECH")
COL_LIGHT = bpy.data.collections.get("08_LIGHTING")
COL_CAMS = bpy.data.collections.get("09_CAMERAS")
COL_STORY = bpy.data.collections.get("07_STORYTELLING")
PREFIX = "NEXUS_UP_SRV_"


def remove_created():
    for obj in list(bpy.data.objects):
        if obj.name.startswith(PREFIX):
            bpy.data.objects.remove(obj, do_unlink=True)


def box(name, center, size, mat, col, bevel=0.015):
    mesh = bpy.data.meshes.new(name)
    x, y, z = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
    verts = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
             (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    obj.location = center
    if mat:
        mesh.materials.append(mat)
    if bevel > 0:
        m = obj.modifiers.new("Bevel", "BEVEL")
        m.width = bevel
        m.segments = 1
    return obj


def mat(name):
    return bpy.data.materials.get(name)


def server_racks():
    dark = mat("NEXUS_Steel")
    sceen = mat("NEXUS_Screen")
    cyan = mat("NEXUS_CorridorLight")
    red = mat("NEXUS_Red")
    # North wall racks, fronts facing into the room (south, -Y).
    xs = [4.55, 5.55, 6.55, 7.55, 8.55, 9.55]
    for i, x in enumerate(xs):
        y = -6.15
        base = Vector((x, y, -12.55))
        box(f"{PREFIX}Rack_{i:02d}", base, (0.82, 0.72, 2.35), dark, COL_FURN, 0.025)
        box(f"{PREFIX}RackPanel_{i:02d}", base + Vector((0, -0.37, 0.25)), (0.62, 0.04, 1.35), sceen, COL_TECH, 0.005)
        for j in range(5):
            box(f"{PREFIX}LED_{i:02d}_{j:02d}", base + Vector((-0.24 + j * 0.12, -0.40, 0.68)), (0.035, 0.02, 0.035), cyan, COL_TECH, 0.002)
        box(f"{PREFIX}RackTop_{i:02d}", base + Vector((0, 0, 1.22)), (0.9, 0.8, 0.07), mat("NEXUS_Painted_Metal"), COL_FURN, 0.01)
    # Cable tray above the racks.
    box(f"{PREFIX}CableTray", (7.1, -6.55, -10.65), (5.8, 0.45, 0.12), dark, COL_TECH, 0.01)
    for i in range(6):
        box(f"{PREFIX}Cable_{i:02d}", (7.1, -6.55 + (i - 2.5) * 0.055, -10.54), (5.6, 0.035, 0.035), mat("NEXUS_Rubber"), COL_TECH, 0.005)


def console():
    metal = mat("NEXUS_Steel")
    wood = mat("NEXUS_Painted_Metal")
    screen = mat("NEXUS_Screen")
    cyan = mat("NEXUS_CorridorLight")
    center = Vector((7.0, -9.25, -12.75))
    box(f"{PREFIX}DeskTop", center, (3.0, 1.0, 0.09), metal, COL_FURN, 0.02)
    for dx in (-1.3, 1.3):
        for dy in (-0.38, 0.38):
            box(f"{PREFIX}DeskLeg_{dx}_{dy}", center + Vector((dx, dy, -0.48)), (0.08, 0.08, 0.9), wood, COL_FURN, 0.008)
    for i, dx in enumerate((-0.85, 0.0, 0.85)):
        box(f"{PREFIX}Monitor_{i}", center + Vector((dx, 0.05, 0.58)), (0.72, 0.06, 0.46), screen, COL_TECH, 0.012)
        box(f"{PREFIX}MonitorStand_{i}", center + Vector((dx, 0.05, 0.30)), (0.12, 0.12, 0.22), metal, COL_FURN, 0.006)
    # Chair
    box(f"{PREFIX}ChairSeat", (7.0, -7.95, -12.65), (0.65, 0.65, 0.10), mat("NEXUS_Rubber"), COL_FURN, 0.03)
    box(f"{PREFIX}ChairBack", (7.0, -7.62, -12.10), (0.62, 0.10, 0.8), mat("NEXUS_Rubber"), COL_FURN, 0.03)
    box(f"{PREFIX}ChairPost", (7.0, -7.95, -12.95), (0.08, 0.08, 0.55), metal, COL_FURN, 0.01)
    box(f"{PREFIX}ConsoleGlow", (7.0, -8.55, -12.83), (2.2, 0.04, 0.03), cyan, COL_TECH, 0.004)


def floor_detail():
    metal = mat("NEXUS_Steel")
    # Raised access-floor panels.
    for ix in range(4):
        for iy in range(3):
            box(f"{PREFIX}FloorPanel_{ix}_{iy}", (5.0 + ix * 1.3, -11.4 + iy * 1.6, -12.72), (1.26, 1.56, 0.035), metal, COL_FURN, 0.006)
    # Door warning strip near the south entrance.
    box(f"{PREFIX}HazardStrip", (7.0, -12.15, -12.68), (2.2, 0.25, 0.02), mat("NEXUS_Amber"), COL_TECH, 0.004)


def damage_and_story():
    # A knocked chair and a small dried blood trail near the door; no gore.
    box(f"{PREFIX}FallChairSeat", (9.4, -11.6, -12.72), (0.65, 0.65, 0.10), mat("NEXUS_Rubber"), COL_STORY, 0.03)
    box(f"{PREFIX}FallChairBack", (9.4, -11.95, -12.25), (0.62, 0.10, 0.7), mat("NEXUS_Rubber"), COL_STORY, 0.03)
    # A thin dark-red strip reads as a dried trail without noisy decals.
    box(f"{PREFIX}BloodTrail", (8.2, -11.4, -12.66), (0.22, 1.5, 0.012), mat("NEXUS_Blood_Dried"), COL_STORY, 0.002)


def lights_and_camera():
    # Emergency red practical and a cold fill for the server aisle.
    red_data = bpy.data.lights.new(f"{PREFIX}EmergencyLight", "POINT")
    red_data.color = (1.0, 0.03, 0.01)
    red_data.energy = 35.0
    red_data.shadow_soft_size = 0.25
    red_obj = bpy.data.objects.new(red_data.name, red_data)
    COL_LIGHT.objects.link(red_obj)
    red_obj.location = (10.3, -11.9, -11.2)

    cyan_data = bpy.data.lights.new(f"{PREFIX}FillLight", "AREA")
    cyan_data.color = (0.55, 0.78, 1.0)
    cyan_data.energy = 40.0
    cyan_data.shape = "RECTANGLE"
    cyan_data.size = 2.0
    cyan_data.size_y = 0.6
    cyan_obj = bpy.data.objects.new(cyan_data.name, cyan_data)
    COL_LIGHT.objects.link(cyan_obj)
    cyan_obj.location = (7.0, -9.2, -10.7)

    cam_data = bpy.data.cameras.new(f"{PREFIX}Camera")
    cam_data.lens = 24.0
    cam = bpy.data.objects.new(cam_data.name, cam_data)
    COL_CAMS.objects.link(cam)
    cam.location = (4.05, -11.8, -12.1)
    target = Vector((8.8, -7.0, -11.9))
    f = (target - cam.location).normalized()
    up = Vector((0, 0, 1))
    if abs(f.dot(up)) > 0.98:
        up = Vector((0, 1, 0))
    right = f.cross(up).normalized()
    up2 = right.cross(f).normalized()
    cam.matrix_world = Matrix.Translation(cam.location) @ Matrix((right, up2, -f)).transposed().to_4x4()
    SCENE.camera = cam
    return cam


def save_version():
    base = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V02_stage2")
    path = base + ".blend"
    i = 2
    while os.path.exists(path):
        path = f"{base}_{i:02d}.blend"
        i += 1
    bpy.ops.wm.save_as_mainfile(filepath=path)
    print("SAVED", path, os.path.getsize(path))


remove_created()
server_racks()
console()
floor_detail()
damage_and_story()
cam = lights_and_camera()
bpy.context.view_layer.update()
print("STAGE2_DONE objects", len(bpy.data.objects), "camera", cam.name)
save_version()
