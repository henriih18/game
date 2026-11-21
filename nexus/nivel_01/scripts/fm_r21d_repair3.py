"""Third R21D repair pass: laser-focus on remaining QA blockers."""
import bpy
import math
import importlib
import sys
from mathutils import Matrix, Vector

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


def tilt_and_drop(o, rx, ry):
    bb = [o.matrix_world @ Vector(v) for v in o.bound_box]
    c = Vector(((min(p.x for p in bb) + max(p.x for p in bb)) * 0.5,
                (min(p.y for p in bb) + max(p.y for p in bb)) * 0.5,
                (min(p.z for p in bb) + max(p.z for p in bb)) * 0.5))
    m = (Matrix.Translation(c) @ Matrix.Rotation(math.radians(rx), 4, "X") @
         Matrix.Rotation(math.radians(ry), 4, "Y") @ Matrix.Translation(-c))
    o.matrix_world = m @ o.matrix_world
    bpy.context.view_layer.update()
    o.location.z += 0.0015 - min_z(o)


def repair3():
    chaos = R.sub("CHAOS")
    fixtures = R.sub("FIXTURES")
    mat = R.materials()

    # locker doors with panel/vent gaps
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

    # electrical cabinet (label and handle now sit on their faces)
    drop_obj("R21D_ElectricalBox")
    drop_obj("R21D_ElectricalBox_Soot")
    R.build_electrical_box("R21D_ElectricalBox", fixtures, mat)

    # checkpoint fixture with 1 mm assembly gaps
    drop_obj("R21D_FIX_Emergency_Checkpoint")
    R.build_checkpoint_lamp("R21D_FIX_Emergency_Checkpoint", fixtures, mat)

    # tilt every flat shard so no two glass planes are parallel/coplanar
    for o in bpy.data.objects:
        if o.type != "MESH":
            continue
        if o.name.startswith(("R21D_CRTShard_", "R21D_GlassShard_", "R21D_HatchShard_")):
            try:
                idx = int(o.name.rsplit("_", 1)[-1])
            except ValueError:
                continue
            rx = 2.0 + (idx % 5) * 1.7
            ry = -3.0 + (idx % 4) * 1.9
            tilt_and_drop(o, rx, ry)

    bpy.context.view_layer.update()
    print("R21D_REPAIR3_OK objects", len(R.root_collection().all_objects))


if __name__ == "__main__":
    repair3()
