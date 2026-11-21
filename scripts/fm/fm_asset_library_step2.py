import bpy
import json
import os

from mathutils import Matrix

ROOT = "/home/riyo/Documentos/game"
BLEND = os.path.join(ROOT, "nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend")
QA = os.path.join(ROOT, "docs/FM_ASSET_LIBRARY_STEP2.json")
LIB_SCENE = "FM_ASSET_LIBRARY"
LIB_ROOT = "FM_LIBRARY"
SEC_ROOT = "LIB_SECURITY_HERO"

GROUPS = [
    {
        "name": "LIB_SEC_CHECKPOINT",
        "source": "L1_SECURITY_R2_HERO",
        "prefixes": ("KIT_HERO_SEC_", "PROP_HERO_SEC_"),
        "offset": (200.0, 0.0, 0.0),
        "notes": "Checkpoint hero: counter top/details, monitor, keyboard, reader, intercom, barrier, partition, sign",
    },
    {
        "name": "LIB_SEC_CHECKPOINT_DEBRIS",
        "source": "L1_SECURITY_R2_HERO",
        "prefixes": ("DET_HERO_SEC_",),
        "offset": (200.0, 8.0, 0.0),
        "notes": "Checkpoint debris and cable details",
    },
    {
        "name": "LIB_SEC_OPS",
        "source": "L1_SECURITY_R21A_HERO",
        "prefixes": None,
        "offset": (200.0, 50.0, 0.0),
        "notes": "Ops center hero: workstations, chairs, monitors, rack, CCTV, breaker panel, chaos",
    },
    {
        "name": "LIB_SEC_LOCKERS",
        "source": "L1_SECURITY_R21C_HERO_LOCKERS",
        "prefixes": None,
        "offset": (200.0, 100.0, 0.0),
        "notes": "Hero locker banks; ~91k tris each, LOD required before mass placement",
    },
    {
        "name": "LIB_SEC_HATCH",
        "source": "L1_SECURITY_R21C_HERO_HATCH",
        "prefixes": None,
        "offset": (200.0, 120.0, 0.0),
        "notes": "Security hatch: shutter, counter, sign, intercom, window frame, glass, shards",
    },
    {
        "name": "LIB_SEC_STORAGE",
        "source": "L1_SECURITY_R21C_HERO_STORAGE",
        "prefixes": None,
        "offset": (200.0, 140.0, 0.0),
        "notes": "Shelving unit and key rack",
    },
    {
        "name": "LIB_SEC_CART",
        "source": "L1_SECURITY_R21C_HERO_CART",
        "prefixes": None,
        "offset": (200.0, 160.0, 0.0),
        "notes": "Tool cart",
    },
    {
        "name": "LIB_SEC_FIXTURES",
        "source": "L1_SECURITY_R21D_HERO_FIXTURES",
        "prefixes": None,
        "offset": (200.0, 180.0, 0.0),
        "notes": "Electrical box, soot overlay and checkpoint emergency fixture",
    },
    {
        "name": "LIB_SEC_DEBRIS_R21C",
        "source": "L1_SECURITY_R21C_HERO_CHAOS",
        "prefixes": None,
        "offset": (200.0, 200.0, 0.0),
        "notes": "Close-up chaos set: chairs, CRT, cable drops, chunks, loose cable, glass, tile",
    },
    {
        "name": "LIB_SEC_DEBRIS_R21D",
        "source": "L1_SECURITY_R21D_HERO_CHAOS",
        "prefixes": (
            "R21D_Chair_", "R21D_CableReel_", "R21D_Pallet", "R21D_LockerDoor_",
            "R21D_CRT_", "R21D_GlassPane_", "R21D_Cone_", "R21D_CeilingTile_",
            "R21D_CeilingGrid_", "R21D_Cable_Hang", "R21D_Puddle_", "R21D_Dust",
            "R21D_Debris_Metal_", "R21D_ElectricalCover", "R21D_ReelCable",
            "R21D_Cable_Checkpoint",
        ),
        "offset": (200.0, 220.0, 0.0),
        "notes": "Reusable debris, ceiling damage, puddles, dust, cones and cables from the R21D set",
    },
]


def collection_new(name, parent):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
    if col.name not in [c.name for c in parent.children]:
        parent.children.link(col)
    return col


def clear_group(dest):
    for ob in list(dest.objects):
        bpy.data.objects.remove(ob, do_unlink=True)


def copy_group(group, sec_root):
    src = bpy.data.collections.get(group["source"])
    if src is None:
        print("MISSING_SOURCE", group["source"])
        return None
    dest = bpy.data.collections.get(group["name"])
    if dest is not None:
        clear_group(dest)
    else:
        dest = collection_new(group["name"], sec_root)

    root = bpy.data.objects.new(group["name"] + "_ROOT", None)
    dest.objects.link(root)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.6
    root.location = group["offset"]
    root["fm_library_group"] = group["name"]
    root["fm_source_collection"] = group["source"]
    root["fm_notes"] = group["notes"]

    offset = Matrix.Translation(group["offset"])
    copied = 0
    tris = 0
    shared = 0
    seen = set()
    # Materialize the list before linking copies: mutating the scene while
    # iterating Collection.all_objects can truncate the iterator.
    src_objects = [o for o in src.all_objects if o is not None and o.type == 'MESH']
    for src_ob in src_objects:
        if src_ob.name in seen:
            continue
        if group["prefixes"] and not any(src_ob.name.startswith(p) for p in group["prefixes"]):
            continue
        seen.add(src_ob.name)
        ob = src_ob.copy()
        ob.data = src_ob.data
        ob.parent = None
        ob.matrix_world = offset @ src_ob.matrix_world
        ob.name = "LIB_" + src_ob.name
        ob.hide_render = False
        ob.hide_viewport = False
        ob.hide_set(False)
        ob["fm_library"] = True
        ob["fm_library_group"] = group["name"]
        ob["fm_source_object"] = src_ob.name
        ob["fm_source_collection"] = group["source"]
        ob["fm_reuse_mode"] = "LINKED_DUPLICATE_SHARED_MESH"
        if len(ob.data.polygons) * 2 > 20000:
            ob["fm_lod_pending"] = True
        dest.objects.link(ob)
        copied += 1
        tris += len(ob.data.polygons) * 2
        if ob.data.users >= 2:
            shared += 1

    root["fm_objects"] = copied
    root["fm_tris"] = tris
    root["fm_shared_meshes"] = shared
    print("LIB_GROUP", group["name"], "objects", copied, "tris", tris, "shared", shared)
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("LIB_GROUP_SAVED", group["name"])
    return {
        "name": group["name"],
        "source": group["source"],
        "objects": copied,
        "tris": tris,
        "shared_meshes": shared,
        "offset": group["offset"],
    }


def main():
    lib_scene = bpy.data.scenes.get(LIB_SCENE)
    if lib_scene is None:
        raise RuntimeError("FM_ASSET_LIBRARY missing")
    lib_root = bpy.data.collections.get(LIB_ROOT)
    if lib_root is None:
        raise RuntimeError("FM_LIBRARY missing")
    sec_root = bpy.data.collections.get(SEC_ROOT)
    if sec_root is None:
        sec_root = bpy.data.collections.new(SEC_ROOT)
        lib_root.children.link(sec_root)

    results = []
    for group in GROUPS:
        info = copy_group(group, sec_root)
        if info:
            results.append(info)

    total_objects = sum(r["objects"] for r in results)
    total_tris = sum(r["tris"] for r in results)
    report = {
        "library_scene": LIB_SCENE,
        "security_root": SEC_ROOT,
        "groups": results,
        "total_objects": total_objects,
        "total_tris": total_tris,
        "notes": [
            "Copies are linked duplicates sharing mesh data with the Security originals.",
            "Originals remain untouched in the level scene.",
            "Saved after each group to survive a heavy pass.",
        ],
    }
    with open(QA, "w") as fh:
        json.dump(report, fh, indent=2)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("STEP2_DONE", total_objects, total_tris, len(results))


main()
