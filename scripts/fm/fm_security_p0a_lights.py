import bpy
import json
import math
import os
import shutil
from mathutils import Matrix, Vector

ROOT = "/home/riyo/Documentos/game"
BLEND = os.path.join(ROOT, "nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend")
BACKUP = os.path.join(ROOT, "docs/backups/FM_LEVEL1_V06_ARCH_before_security_p0a_lights.blend")
QA = os.path.join(ROOT, "docs/fm_security_p0a_lights_qa.json")
HERO = "L1_SECURITY_P0A_HERO"
RETIRED = "L1_SECURITY_RETIRED_P0A"
LEVEL = "NEXUS_L1_V06_ARCH"
LIB = "FM_ASSET_LIBRARY"

# Old ceiling fixtures: (index, x, y). Housing and panel share the same x/y.
CEILING = [
    (0, -101.5, 13.0),
    (1, -88.0, 13.0),
    (2, -74.5, 13.0),
    (3, -101.5, 31.0),
    (4, -88.0, 31.0),
    (5, -74.5, 31.0),
    (6, -88.0, 21.0),
]
# Old wall emergencies: (name, x, y, z, rotation Z degrees)
EMERG = [
    ("R21B_SERV_EmergencyS", -94.6, 10.0, 3.16, 0.0),
    ("R21B_SERV_EmergencyW1", -105.0, 14.6, 3.16, -90.0),
    ("R21B_SERV_EmergencyW2", -105.0, 27.6, 3.16, -90.0),
]


def ensure_collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    elif col.name not in [c.name for c in bpy.context.scene.collection.children]:
        bpy.context.scene.collection.children.link(col)
    col.hide_render = False
    col.hide_viewport = False
    return col


def unlink_all(ob):
    for col in list(ob.users_collection):
        col.objects.unlink(ob)


def move_to(ob, col):
    unlink_all(ob)
    col.objects.link(ob)


def mesh_tris(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons) if ob.type == 'MESH' else 0


def source_mesh(name):
    sc = bpy.data.scenes.get(LIB)
    if sc is None:
        raise RuntimeError("FM_ASSET_LIBRARY missing")
    exact = bpy.data.objects.get(name)
    if exact and exact.type == 'MESH':
        return exact
    for ob in bpy.data.objects:
        if ob.type == 'MESH' and ob.name.startswith(name):
            return ob
    raise RuntimeError("missing source " + name)


def instance(src, name, target, col, rot_z=0.0):
    new = src.copy()
    new.data = src.data
    new.parent = None
    new.name = name
    new.hide_render = False
    new.hide_viewport = False
    new.hide_set(False)
    col.objects.link(new)
    new.matrix_world = Matrix.Translation(Vector(target)) @ Matrix.Rotation(math.radians(rot_z), 4, 'Z')
    new["fm_generation"] = "VERIFIED_SECURITY_P0A"
    new["fm_source_master"] = src.name
    new["fm_tris"] = mesh_tris(new)
    return new


def main():
    if os.path.exists(BLEND):
        shutil.copy2(BLEND, BACKUP)
        print("BACKUP", BACKUP)

    hero = ensure_collection(HERO)
    retired = ensure_collection(RETIRED)
    retired.hide_render = True
    retired.hide_viewport = True

    # Idempotent cleanup of previous batch output.
    for ob in list(bpy.data.objects):
        if ob.name.startswith("SEC_P0A_"):
            bpy.data.objects.remove(ob, do_unlink=True)
    for ob in list(hero.objects):
        if ob.name in hero.objects:
            hero.objects.unlink(ob)

    leveled = bpy.data.scenes[LEVEL]
    old_objects = []
    for idx, x, y in CEILING:
        for prefix in ("KIT_SEC01_CeilingLightHousing_", "DET_SEC01_CeilingLightPanel_"):
            ob = bpy.data.objects.get(prefix + str(idx))
            if ob:
                old_objects.append(ob)
    for name, _x, _y, _z, _rot in EMERG:
        ob = bpy.data.objects.get(name)
        if ob:
            old_objects.append(ob)

    retired_names = []
    for ob in old_objects:
        if RETIRED not in [c.name for c in ob.users_collection]:
            move_to(ob, retired)
            retired_names.append(ob.name)
        ob.hide_render = True
        ob.hide_viewport = True
        ob.hide_set(True)

    lum = source_mesh("SM_SH_LUMINAIRE_1500_OFF")
    emg = source_mesh("SM_SH_EMERGENCY_WALL_E")
    new_objects = []
    for idx, x, y in CEILING:
        new_objects.append(instance(lum, "SEC_P0A_LUMINAIRE_%02d" % idx, (x, y, 4.42), hero, 0.0))
    for i, (name, x, y, z, rot) in enumerate(EMERG):
        new_objects.append(instance(emg, "SEC_P0A_EMERG_%s" % ("S" if i == 0 else "W%d" % i), (x, y, z), hero, rot))

    # Red practical lights for the two emergencies that had none.
    light_specs = [
        ("SEC_P0A_LIGHT_EMERG_S", (-94.6, 10.26, 3.08)),
        ("SEC_P0A_LIGHT_EMERG_W1", (-104.78, 14.6, 3.08)),
    ]
    new_lights = []
    for name, loc in light_specs:
        old = bpy.data.objects.get(name)
        if old:
            bpy.data.objects.remove(old, do_unlink=True)
        ld = bpy.data.lights.new(name, 'POINT')
        ld.energy = 8.0
        ld.color = (1.0, 0.04, 0.02)
        ld.shadow_soft_size = 0.16
        ob = bpy.data.objects.new(name, ld)
        ob.location = loc
        hero.objects.link(ob)
        ob.hide_render = False
        ob.hide_viewport = False
        new_lights.append(ob)

    bpy.context.view_layer.update()

    # QA.
    region = []
    for ob in new_objects:
        pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
        lo = [min(p[i] for p in pts) for i in range(3)]
        hi = [max(p[i] for p in pts) for i in range(3)]
        inside = (-106 <= lo[0] and hi[0] <= -70 and 9 <= lo[1] and hi[1] <= 37 and -0.6 <= lo[2] and hi[2] <= 5.6)
        region.append({
            "name": ob.name,
            "tris": mesh_tris(ob),
            "mesh": ob.data.name,
            "data_users": ob.data.users,
            "bbox": [[round(v, 3) for v in lo], [round(v, 3) for v in hi]],
            "inside_security": bool(inside),
        })

    qa = {
        "batch": "SECURITY_P0A_LIGHTS",
        "new_objects": len(new_objects),
        "new_lights": len(new_lights),
        "retired_old": retired_names,
        "retired_visible": [o.name for o in bpy.data.objects if o.name in retired_names and not o.hide_render],
        "all_inside": all(r["inside_security"] for r in region),
        "all_mesh_shared": all(r["data_users"] >= 2 for r in region),
        "objects": region,
        "lights": [o.name for o in new_lights],
        "hero_collection_objects": len(hero.objects),
        "source_masters": [lum.name, emg.name],
    }
    with open(QA, "w") as fh:
        json.dump(qa, fh, indent=2)
    print("SEC_P0A_LIGHTS_DONE", json.dumps({
        "new": len(new_objects), "lights": len(new_lights), "retired": len(retired_names),
        "inside": qa["all_inside"], "shared": qa["all_mesh_shared"],
    }))
    print("QA", QA)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("SAVED", BLEND)


main()
