"""Add a safety cage and rest platforms to the emergency ladder in the NE tower."""
import bpy
import os

ROOT = "/home/riyo/Documentos/game"
OUT = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V05_level1_v40.blend")

rung = bpy.data.objects.get("NEXUS_VTOWER_LADDER_RUNG_0")
if rung and rung.users_collection:
    COLL = rung.users_collection[0]
else:
    COLL = bpy.data.collections.get("NEXUS_V04_DETAIL") or bpy.context.scene.collection

STEEL = bpy.data.materials.get("NEXUS_Steel")
AMBER = bpy.data.materials.get("NEXUS_Amber")
GRATE = bpy.data.materials.get("NEXUS_Grating") or STEEL

CX, CY = 24.5, 15.5
Z0, Z1 = -43.4, -6.2
REST_Z = [-9.8, -18.3, -28.3, -38.3]


def cube_geo(verts, faces, center, size):
    x, y, z = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
    cx, cy, cz = center
    b = len(verts)
    verts.extend([
        (cx - x, cy - y, cz - z), (cx + x, cy - y, cz - z),
        (cx + x, cy + y, cz - z), (cx - x, cy + y, cz - z),
        (cx - x, cy - y, cz + z), (cx + x, cy - y, cz + z),
        (cx + x, cy + y, cz + z), (cx - x, cy + y, cz + z),
    ])
    faces.extend([
        (b, b + 1, b + 2, b + 3), (b + 7, b + 6, b + 5, b + 4),
        (b, b + 4, b + 5, b + 1), (b + 1, b + 5, b + 6, b + 2),
        (b + 2, b + 6, b + 7, b + 3), (b + 3, b + 7, b + 4, b),
    ])


def object_from_geo(name, verts, faces, material, bevel=0.0):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    COLL.objects.link(obj)
    if material:
        mesh.materials.append(material)
    if bevel > 0:
        mod = obj.modifiers.new("Bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 1
    return obj


# Remove any previous version of the cage/rests so the script is idempotent.
for obj in list(bpy.data.objects):
    if obj.name.startswith(("NEXUS_VTOWER_LADDER_CAGE", "NEXUS_VTOWER_LADDER_REST_")):
        bpy.data.objects.remove(obj, do_unlink=True)

# --- Safety cage: rectangular hoops + four vertical straps ---
verts, faces = [], []
step = 0.8
count = int((Z1 - Z0) / step)
for i in range(count + 1):
    z = Z0 + i * step
    if any(abs(z - rz) < 0.35 for rz in REST_Z):
        continue
    # Hoop: 1.1 m wide in X and 1.0 m deep in Y around the ladder.
    cube_geo(verts, faces, (CX, 15.05, z), (1.10, 0.05, 0.05))
    cube_geo(verts, faces, (CX, 16.05, z), (1.10, 0.05, 0.05))
    cube_geo(verts, faces, (23.95, 15.55, z), (0.05, 1.00, 0.05))
    cube_geo(verts, faces, (25.05, 15.55, z), (0.05, 1.00, 0.05))

for x in (23.95, 25.05):
    for y in (15.05, 16.05):
        cube_geo(verts, faces, (x, y, (Z0 + Z1) * 0.5), (0.05, 0.05, Z1 - Z0))

cage = object_from_geo("NEXUS_VTOWER_LADDER_CAGE", verts, faces, STEEL, 0.0)

# --- Rest platforms every ~9 m, offset south so the ladder stays clear ---
for idx, rz in enumerate(REST_Z, start=1):
    v, f = [], []
    # Platform, edge strip and toe plate.
    cube_geo(v, f, (CX, 14.475, rz), (1.70, 1.15, 0.06))
    cube_geo(v, f, (CX, 15.02, rz + 0.055), (1.70, 0.05, 0.05))
    cube_geo(v, f, (CX, 13.91, rz + 0.95), (1.74, 0.04, 0.04))
    # Guard rails on south, east and west; the north side stays open to the ladder.
    for zz in (rz + 0.52, rz + 0.98):
        cube_geo(v, f, (CX, 13.91, zz), (1.70, 0.05, 0.05))
        cube_geo(v, f, (23.66, 14.475, zz), (0.05, 1.18, 0.05))
        cube_geo(v, f, (25.34, 14.475, zz), (0.05, 1.18, 0.05))
    # Corner posts on the south side.
    for x in (23.66, 25.34):
        cube_geo(v, f, (x, 13.91, rz + 0.5), (0.05, 0.05, 1.0))
    object_from_geo(f"NEXUS_VTOWER_LADDER_REST_{idx}", v, f, STEEL, 0.0)
    # Amber edge marker on each platform.
    av, af = [], []
    cube_geo(av, af, (CX, 13.94, rz + 1.01), (1.55, 0.03, 0.025))
    object_from_geo(f"NEXUS_VTOWER_LADDER_REST_MARK_{idx}", av, af, AMBER, 0.0)

# Keep the platform material distinct if a grating material exists.
for idx in range(1, len(REST_Z) + 1):
    obj = bpy.data.objects.get(f"NEXUS_VTOWER_LADDER_REST_{idx}")
    if obj and GRATE and GRATE.name != "NEXUS_Steel":
        obj.data.materials.clear()
        obj.data.materials.append(GRATE)

bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("LADDER_SAFETY_SAVED", OUT, os.path.getsize(OUT))
print("CAGE_VERTS", len(cage.data.vertices), "CAGE_FACES", len(cage.data.polygons))
print("REST_PLATFORMS", len(REST_Z))
