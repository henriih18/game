"""Second R21D repair pass: doors, cabinet, lamp, glass puddle and shards."""
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


def repair2():
    chaos = R.sub("CHAOS")
    fixtures = R.sub("FIXTURES")
    mat = R.materials()

    # locker doors with overlapping vents/hinge plates
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

    # electrical cabinet with hinge bridge
    drop_obj("R21D_ElectricalBox")
    drop_obj("R21D_ElectricalBox_Soot")
    R.build_electrical_box("R21D_ElectricalBox", fixtures, mat)

    # checkpoint fixture with non-coplanar housing
    drop_obj("R21D_FIX_Emergency_Checkpoint")
    R.build_checkpoint_lamp("R21D_FIX_Emergency_Checkpoint", fixtures, mat)

    # glass puddle moved clear of the shard field
    drop_obj("R21D_Puddle_Glass")
    R.jagged_ring("R21D_Puddle_Glass", -88.90, 24.80, 0.90, 0.55, 0.0035,
                  mat["water"], chaos, n=18, seed=51)

    # each shard gets a distinct height; glass flat boxes stop z-fighting
    for o in bpy.data.objects:
        if o.type != "MESH":
            continue
        if o.name.startswith(("R21D_CRTShard_", "R21D_GlassShard_", "R21D_HatchShard_")):
            try:
                idx = int(o.name.rsplit("_", 1)[-1])
            except ValueError:
                continue
            target = 0.0015 + idx * 0.00025
            o.location.z += target - min_z(o)
        elif o.name.startswith("R21D_Debris_Concrete_"):
            o.location.z += 0.001 - min_z(o)

    bpy.context.view_layer.update()
    print("R21D_REPAIR2_OK objects", len(R.root_collection().all_objects))


if __name__ == "__main__":
    repair2()
