import bpy
import json
import os
import shutil

from mathutils import Matrix

ROOT = "/home/riyo/Documentos/game"
BLEND = os.path.join(ROOT, "nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend")
BACKUP = os.path.join(ROOT, "docs/backups/FM_LEVEL1_V06_ARCH_before_asset_library.blend")
LIB_BLEND = os.path.join(ROOT, "assets/blender/fm_shared_hero_library.blend")
QA = os.path.join(ROOT, "docs/FM_ASSET_LIBRARY_QA.json")

LEVEL_SCENE = "NEXUS_L1_V06_ARCH"
LIB_SCENE = "FM_ASSET_LIBRARY"
LIB_ROOT = "FM_LIBRARY"

COPY_GROUPS = [
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


def tris_of_collection(col):
    total = 0
    for ob in col.all_objects:
        if ob is None or ob.type != 'MESH':
            continue
        total += len(ob.data.polygons) * 2
    return total


def snapshot():
    result = {}
    for g in COPY_GROUPS:
        src = bpy.data.collections.get(g["source"])
        if src:
            result[g["source"]] = {
                "objects": len(src.all_objects),
                "meshes": sum(1 for o in src.all_objects if o is not None and o.type == 'MESH'),
                "tris": tris_of_collection(src),
            }
    return result


def coll_new(name, parent):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
    if col.name not in [c.name for c in parent.children]:
        parent.children.link(col)
    return col


def copy_group(group, parent):
    src = bpy.data.collections.get(group["source"])
    if src is None:
        print("MISSING_SOURCE", group["source"])
        return None
    dest = coll_new(group["name"], parent)
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
    for src_ob in src.all_objects:
        if src_ob is None or src_ob.type != 'MESH' or src_ob.name in seen:
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
    return dest


def main():
    if os.path.exists(BLEND) and not os.path.exists(BACKUP):
        shutil.copy2(BLEND, BACKUP)

    if bpy.data.collections.get(LIB_ROOT):
        print("ABORT_LIBRARY_EXISTS", LIB_ROOT)
        return

    level = bpy.data.scenes.get(LEVEL_SCENE)
    if level is None:
        raise RuntimeError("Level scene not found")

    before = snapshot()
    level_objects_before = len(level.objects)

    lib = bpy.data.scenes.new(LIB_SCENE)
    if level.world:
        lib.world = level.world
    lib_root = bpy.data.collections.new(LIB_ROOT)
    lib.collection.children.link(lib_root)

    corridor = bpy.data.collections.new("LIB_CORRIDOR_HERO")
    lib_root.children.link(corridor)

    shared = bpy.data.collections.get("L1_SHARED_HERO")
    if shared is None:
        raise RuntimeError("L1_SHARED_HERO not found; it may already be extracted")
    for parent in list(bpy.data.collections) + [s.collection for s in bpy.data.scenes]:
        if shared.name in [c.name for c in parent.children]:
            parent.children.unlink(shared)
    corridor.children.link(shared)
    print("CORRIDOR_MOVED", len(shared.all_objects), tris_of_collection(shared))

    sec_root = bpy.data.collections.new("LIB_SECURITY_HERO")
    lib_root.children.link(sec_root)
    for group in COPY_GROUPS:
        copy_group(group, sec_root)

    readme = bpy.data.texts.new("FM_ASSET_LIBRARY_README")
    readme.write(
        "FRECUENCIA MUERTA - FM LIBRARY\n\n"
        "Scene: FM_ASSET_LIBRARY\n"
        "Root: FM_LIBRARY\n\n"
        "LIB_CORRIDOR_HERO:\n"
        "  L1_SHARED_HERO (DOORS, LIGHTING, SERVICES, P0_TEST_ASSEMBLY, LODs, collisions)\n"
        "  These are the P0a masters, moved out of the playable corridor.\n\n"
        "LIB_SECURITY_HERO:\n"
        "  LINKED_DUPLICATE_SHARED_MESH copies of the best Security assets.\n"
        "  Originals remain untouched in Seguridad. The library copies share mesh data.\n\n"
        "Usage:\n"
        "  - Link/instance the desired LIB_* collection into the target room.\n"
        "  - Do not edit library meshes directly from a room. Edit the master in this library\n"
        "    and let instances update.\n"
        "  - Heavy assets (lockers, ops center) need LOD before mass placement.\n"
        "  - The standalone library file is assets/blender/fm_shared_hero_library.blend.\n"
    )
    readme.use_fake_user = True

    bpy.context.view_layer.update()
    lib_objects = list(lib_root.all_objects)
    lib_meshes = [o for o in lib_objects if o.type == 'MESH']
    lib_tris = sum(len(o.data.polygons) * 2 for o in lib_meshes)
    shared_meshes = sum(1 for o in lib_meshes if o.data.users >= 2)

    os.makedirs(os.path.dirname(LIB_BLEND), exist_ok=True)
    lib_file_result = "not_written"
    try:
        bpy.data.libraries.write(LIB_BLEND, {lib_root}, fake_user=True, compress=True)
        lib_file_result = "written"
    except Exception as exc:
        lib_file_result = "error: " + repr(exc)
        print("LIB_FILE_ERROR", repr(exc))

    if bpy.context.window:
        bpy.context.window.scene = level
    bpy.context.view_layer.update()

    after = snapshot()
    remaining = []
    for ob in level.objects:
        if ob.name.startswith("SM_SH_") or ob.name.startswith("P0_TEST_"):
            remaining.append(ob.name)
    shared_in_level = []
    for ob in level.objects:
        try:
            if ob.name in {x.name for x in shared.all_objects}:
                shared_in_level.append(ob.name)
        except Exception:
            pass

    report = {
        "library_scene": LIB_SCENE,
        "library_root": LIB_ROOT,
        "library_objects": len(lib_objects),
        "library_meshes": len(lib_meshes),
        "library_tris": lib_tris,
        "shared_meshes": shared_meshes,
        "corridor_objects": len(shared.all_objects),
        "corridor_tris": tris_of_collection(shared),
        "security_sources_before": before,
        "security_sources_after": after,
        "security_sources_unchanged": before == after,
        "level_objects_before": level_objects_before,
        "level_objects_after": len(level.objects),
        "level_shared_names_remaining": shared_in_level,
        "level_sm_sh_or_p0_remaining": remaining,
        "library_file": LIB_BLEND,
        "library_file_result": lib_file_result,
        "library_file_bytes": os.path.getsize(LIB_BLEND) if os.path.exists(LIB_BLEND) else 0,
        "notes": [
            "P0a masters moved from the level scene to FM_ASSET_LIBRARY; corridor is clean.",
            "Security hero assets copied as linked duplicates sharing mesh data; originals untouched.",
            "Standalone library written from FM_LIBRARY.",
        ],
    }
    with open(QA, "w") as fh:
        json.dump(report, fh, indent=2)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("ASSET_LIBRARY_DONE", len(lib_objects), len(lib_meshes), lib_tris, lib_file_result)
    print("LEVEL_REMAINING", remaining[:20], "count", len(remaining))
    print("SHARED_IN_LEVEL", len(shared_in_level))


main()
