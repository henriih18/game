"""Final Level 1 fixes: door signs, matte red props, bucket, lights and maintenance camera."""
import bpy
import os
from mathutils import Vector, Matrix

ROOT = "/home/riyo/Documentos/game"
SCENE = bpy.context.scene
Z1 = -5.8


def material(name, base, metallic=0.0, roughness=0.5, emission=None):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        return m
    bsdf.inputs["Base Color"].default_value = (*base, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (*(emission or (0, 0, 0)), 1.0)
        bsdf.inputs["Emission Strength"].default_value = 0.0 if emission is None else 1.0
    return m


# 1. Remove the old door-sign bars and enlarge/lower the new corridor signs.
removed = 0
for o in list(bpy.data.objects):
    if "D_DOORSIGN" in o.name:
        bpy.data.objects.remove(o, do_unlink=True)
        removed += 1

for o in bpy.data.objects:
    if o.name.startswith("NEXUS_V05_E_CORR_SIGN_"):
        o.location.z -= 0.25
        if o.name.endswith("_TEXT_TEXT"):
            o.scale.x *= 1.75
            o.scale.y *= 1.75
        elif o.name.endswith("_PLATE"):
            o.scale.x *= 2.6 / 2.2
            o.scale.z *= 0.42 / 0.38

# 2. Matte red for practical props, keeping alarms/LEDs emissive.
red_matte = material("NEXUS_Red_Matte", (0.18, 0.008, 0.005), metallic=0.2, roughness=0.45)
red_objects = [
    "NEXUS_V05_B_MAINT_TOOLBOX",
    "NEXUS_V05_D_MAINT_TOOLBOX",
    "NEXUS_V05_D_MAINT_TOOLBOX_LID",
    "NEXUS_V05_B_MAINT_CYLINDER_0",
    "NEXUS_V05_D_MAINT_AIR_VALVE",
    "NEXUS_V05_E_MAINT_AIR_VALVE",
    "NEXUS_V05_B_MAINT_PIPE_VALVE",
    "NEXUS_V05_B_MAINT_BOILER_VALVE",
    "NEXUS_V05_D_CORR_VALVE_0",
    "NEXUS_V05_D_CORR_VALVE_1",
    "NEXUS_V05_C_REC_HOSE_REEL",
]
changed = 0
for name in red_objects:
    o = bpy.data.objects.get(name)
    if not o or o.type != "MESH":
        continue
    for slot in o.material_slots:
        if slot.material and slot.material.name == "NEXUS_Red":
            slot.material = red_matte
            changed += 1

# 3. Bucket: painted metal, not a glowing lamp.
bucket = bpy.data.objects.get("NEXUS_V05_B_VEST_BUCKET")
if bucket and bucket.type == "MESH":
    painted = bpy.data.materials.get("NEXUS_Painted_Metal")
    if painted:
        if not bucket.data.materials:
            bucket.data.materials.append(painted)
        else:
            for i in range(len(bucket.data.materials)):
                bucket.data.materials[i] = painted

# 4. Darken rug and foliage.
for name, color in (("NEXUS_Rug_Dark", (0.02, 0.012, 0.01)),
                    ("NEXUS_Foliage_Dark", (0.006, 0.018, 0.008))):
    m = bpy.data.materials.get(name)
    if m and m.use_nodes:
        bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (*color, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.95

# 5. Beacon intensity.
for name, energy in (("NEXUS_V05_C_SEC_BEACON_LIGHT", 12.0),
                     ("NEXUS_V05_SEC_BEACON_LIGHT", 8.0),
                     ("NEXUS_V05_D_MAINT_BEACON_LIGHT", 10.0)):
    o = bpy.data.objects.get(name)
    if o and o.type == "LIGHT":
        o.data.energy = energy

# 6. Maintenance lighting and camera.
for name, energy in (("NEXUS_V05_B_MAINT_BENCH_LIGHT", 350.0),
                     ("NEXUS_V05_B_MAINT_LAMP_A_LIGHT", 75.0),
                     ("NEXUS_V05_B_MAINT_LAMP_B_LIGHT", 75.0)):
    o = bpy.data.objects.get(name)
    if o and o.type == "LIGHT":
        o.data.energy = energy

fill = bpy.data.objects.get("NEXUS_V05_F_MAINT_FILL")
if fill is None:
    ld = bpy.data.lights.new("NEXUS_V05_F_MAINT_FILL", "AREA")
    ld.energy = 650.0
    ld.color = (1.0, 0.82, 0.62)
    ld.shape = "RECTANGLE"
    ld.size = 4.5
    ld.size_y = 2.0
    fill = bpy.data.objects.new(ld.name, ld)
    bpy.data.collections["V05_LIGHTS"].objects.link(fill)
    fill.location = (12.0, -6.4, -2.15)


def aim(name, loc, target, lens):
    cam = bpy.data.objects.get(name)
    if not cam:
        return
    cam.location = Vector(loc)
    cam.data.lens = lens
    f = (Vector(target) - cam.location).normalized()
    up = Vector((0, 0, 1))
    if abs(f.dot(up)) > 0.98:
        up = Vector((0, 1, 0))
    right = f.cross(up).normalized()
    up2 = right.cross(f).normalized()
    cam.matrix_world = Matrix.Translation(cam.location) @ Matrix((right, up2, -f)).transposed().to_4x4()


aim("NEXUS_V05_CAM_Mantenimiento", (16.0, -2.2, -3.0), (12.5, -8.0, -3.4), 16.5)
aim("NEXUS_V05_CAM_Corridor", (-20.5, 0.0, -2.8), (18.0, 0.0, -2.8), 20.0)
SCENE.camera = bpy.data.objects.get("NEXUS_V05_CAM_Corridor")

path = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V05_level1_v19.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
print("V19_SAVED", path, os.path.getsize(path))
print("DOORSIGN_REMOVED", removed, "RED_SLOTS_CHANGED", changed)
