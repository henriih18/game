"""Repair pass for R21D geometry blockers found by qa_check.

Rebuilds the objects whose internal islands were coplanar or detached, and
repositions the decals/debris that sat above the floor.  Run after
fm_r21d_chaos.build(); it does not touch the hero collections.
"""
import bpy
import math
import importlib
import sys

sys.path.insert(0, "/home/riyo/Documentos/game/nexus/nivel_01/scripts")
import fm_r21d_chaos as R

importlib.reload(R)


def drop_obj(name):
    o = bpy.data.objects.get(name)
    if o is None:
        return
    me = o.data if o.type == "MESH" else None
    bpy.data.objects.remove(o, do_unlink=True)
    if me and me.users == 0:
        bpy.data.meshes.remove(me)


def min_z(o):
    bpy.context.view_layer.update()
    return min((o.matrix_world @ v.co).z for v in o.data.vertices)


def repair():
    chaos = R.sub("CHAOS")
    fixtures = R.sub("FIXTURES")
    mat = R.materials()

    # --- ceiling tiles: single beveled slab each ---------------------------------
    tiles = [
        ("R21D_CeilingTile_FlatA", (-84.80, 18.62, 0.0), (0.0, 0.0, 23.0), False),
        ("R21D_CeilingTile_FlatB", (-85.56, 18.15, 0.0), (0.0, 0.0, -12.0), False),
        ("R21D_CeilingTile_LeanC", (-86.54, 17.55, 0.0), (-68.0, 0.0, 9.0), False),
        ("R21D_CeilingTile_HangingD", (-83.90, 19.16, 4.05), (-26.0, 0.0, 14.0), True),
    ]
    for name, loc, rot, hanging in tiles:
        drop_obj(name)
        R.build_ceiling_tile(name, loc, rot, chaos, mat, hanging=hanging)

    # --- detached locker doors ----------------------------------------------------
    drop_obj("R21D_LockerDoor_LeaningA")
    door_a = R.build_locker_door("R21D_LockerDoor_LeaningA", (0, 0, 0),
                                 (0, 0, 0), chaos, mat, bent=False)
    door_a.matrix_world = (R.Matrix.Translation((-71.74, 18.92, 0.0)) @
                           R.Matrix.Rotation(math.radians(38.0), 4, "Y") @
                           R.Matrix.Rotation(math.radians(90.0), 4, "Z"))
    bpy.context.view_layer.update()
    lo = min((door_a.matrix_world @ v.co).z for v in door_a.data.vertices)
    door_a.matrix_world = R.Matrix.Translation((0, 0, 0.001 - lo)) @ door_a.matrix_world

    drop_obj("R21D_LockerDoor_FloorB")
    R.build_locker_door("R21D_LockerDoor_FloorB", (-77.45, 12.28, 0.0),
                        (-88.0, 0.0, 28.0), chaos, mat, bent=False)

    # --- electrical cabinet -------------------------------------------------------
    drop_obj("R21D_ElectricalBox")
    drop_obj("R21D_ElectricalBox_Soot")
    R.build_electrical_box("R21D_ElectricalBox", fixtures, mat)

    # --- CRT and checkpoint fixture ----------------------------------------------
    drop_obj("R21D_CRT_Broken")
    R.build_crt("R21D_CRT_Broken", (-84.18, 14.32, 0.0), 17.0, chaos, mat)

    drop_obj("R21D_FIX_Emergency_Checkpoint")
    R.build_checkpoint_lamp("R21D_FIX_Emergency_Checkpoint", fixtures, mat)

    # --- pallets ------------------------------------------------------------------
    drop_obj("R21D_Pallet")
    R.build_pallet("R21D_Pallet", (-73.05, 20.55, 0.0), 92.0, chaos, mat, boxes=2)
    drop_obj("R21D_PalletB")
    R.build_pallet("R21D_PalletB", (-95.30, 16.45, 0.0), 8.0, chaos, mat, boxes=1)

    # --- decals and small debris --------------------------------------------------
    for n in ("R21D_Puddle_HoleWet", "R21D_Puddle_Hole"):
        drop_obj(n)
    R.jagged_ring("R21D_Puddle_HoleWet", -83.55, 17.55, 1.35, 0.88, 0.0015,
                  mat["concrete_dark"], chaos, n=24, seed=41)
    R.jagged_ring("R21D_Puddle_Hole", -83.55, 17.55, 1.08, 0.68, 0.0035,
                  mat["water"], chaos, n=24, seed=42)

    # raise/lower the low props onto the floor
    for o in bpy.data.objects:
        if o.type != "MESH":
            continue
        if o.name.startswith("R21D_Debris_Metal_"):
            o.location.z += 0.001 - min_z(o)
        elif o.name == "R21D_ElectricalCover":
            o.location.z += 0.001 - min_z(o)

    # spread shard heights so parallel glass boxes stop z-fighting
    for o in bpy.data.objects:
        if o.type != "MESH":
            continue
        if o.name.startswith(("R21D_CRTShard_", "R21D_GlassShard_", "R21D_HatchShard_")):
            parts = o.name.rsplit("_", 1)
            try:
                idx = int(parts[-1])
            except ValueError:
                continue
            o.location.z += (idx % 3) * 0.0009

    # ceiling grid/hole must intersect the slab above
    for o in bpy.data.objects:
        if o.name.startswith("R21D_CeilingGrid_"):
            o.location.z += 0.022
        elif o.name == "R21D_CeilingHole":
            o.location.z += 0.006

    # rebuild the two short suspension wires with their lower end inside the tile
    for i, (x, y) in enumerate(((-83.62, 19.02), (-84.18, 19.34))):
        drop_obj(f"R21D_CeilingWire_{i}")
        R.L.cable(f"R21D_CeilingWire_{i}", (x, y, 4.705), (x, y, 4.060),
                  0.01, 0.0045, mat["steel_bare"], chaos, n=7, sides=5)

    bpy.context.view_layer.update()
    print("R21D_REPAIR_OK objects", len(R.root_collection().all_objects))


if __name__ == "__main__":
    repair()
