"""Operations-centre chaos for L1_SECURITY_R21C_HERO.

Two additional tipped office chairs, two dead CRT monitors (one on its back
with a cracked screen, one upright on the floor), two hanging cable drops
and a small debris field.  Everything is placed in the open floor of the
ops centre, clear of the hero workstations and the glass partition.
"""
import math
import bpy
from mathutils import Vector, Matrix

import fm_ops_lib as L
import fm_r21c_lib as C


def _tip(ob, origin, rot_z=0.0, angle=-90.0, pivot_z=0.20, floor=0.0015):
    """Bake, rotate around a local pivot and drop the result onto the floor."""
    C.bake_world(ob)
    piv = Vector((0, 0, pivot_z))
    m = (Matrix.Translation(Vector(origin)) @
         Matrix.Rotation(math.radians(rot_z), 4, "Z") @
         Matrix.Translation(piv) @
         Matrix.Rotation(math.radians(angle), 4, "X") @
         Matrix.Translation(-piv))
    ob.matrix_world = m
    bpy.context.view_layer.update()
    lo = min((ob.matrix_world @ v.co).z for v in ob.data.vertices)
    ob.matrix_world = Matrix.Translation((0, 0, floor - lo)) @ ob.matrix_world
    bpy.context.view_layer.update()
    return ob


def _crash_monitor(name, origin, rot_z, mat, coll, tipped=False):
    ob = C.dead_crt(name, (0, 0, 0), mat, coll, with_stand=False,
                    with_cable=not tipped)
    if tipped:
        _tip(ob, origin, rot_z=rot_z, angle=-90.0, pivot_z=0.20)
    else:
        C.place(ob, origin, rot_z=rot_z)
    return ob


def _hanging_cable(name, p0, p1, sag, radius, mat, coll, cable_key="cable_black"):
    p0, p1 = Vector(p0), Vector(p1)
    parts = []
    parts.append(L.cable(name + "_Run", p0, p1, sag, radius, mat[cable_key], coll,
                         n=18, sides=8))
    parts.append(C.hb(name + "_CeilingPlate", (0.130, 0.130, 0.020),
                      (p0.x, p0.y, 4.694), mat["steel_dark"], coll,
                      bevel=0.004, seg=3))
    parts.append(C.cy(name + "_Clamp", 0.018, 0.030, (p0.x, p0.y, 4.670),
                      mat["steel_bare"], coll, segments=14, bevel=0.0015))
    parts.append(C.hb(name + "_EndPlug", (0.055, 0.045, 0.085),
                      (p1.x, p1.y, p1.z - 0.045), mat["plastic"], coll,
                      bevel=0.008, seg=3))
    parts.append(C.cy(name + "_EndGland", 0.014, 0.035,
                      (p1.x, p1.y, p1.z + 0.005), mat["steel_bare"], coll,
                      segments=12, bevel=0.002))
    for i, z in enumerate((4.45, 4.10)):
        # a couple of wall/ceiling clamps along the drop
        t = 0.20 + i * 0.22
        px = p0.x + (p1.x - p0.x) * t
        py = p0.y + (p1.y - p0.y) * t
        pz = p0.z + (p1.z - p0.z) * t - math.sin(math.pi * t) * sag
        parts.append(C.hb(f"{name}_Clip{i}", (0.040, 0.040, 0.020),
                          (px, py, pz), mat["steel_dark"], coll,
                          bevel=0.002, seg=2))
    ob = C.join(parts, name, coll)
    return ob


def build(mat, coll):
    import fm_ops_workstations as OW
    hero = L.make_materials()
    objs = []
    # additional tipped chairs (the ops centre already has one)
    objs.append(OW.build_chair("R21C_CHAOS_ChairA", (-86.65, 27.45, 0.0),
                               hero, coll, facing_deg=28, tipped=True))
    objs.append(OW.build_chair("R21C_CHAOS_ChairB", (-83.55, 27.35, 0.0),
                               hero, coll, facing_deg=-58, tipped=True))
    # dead CRTs: one on its back, screen up; one discarded upright
    objs.append(_crash_monitor("R21C_CHAOS_CRT_A", (-85.35, 28.72, 0.0), 18.0,
                               mat, coll, tipped=True))
    objs.append(_crash_monitor("R21C_CHAOS_CRT_B", (-81.95, 28.55, 0.0), -32.0,
                               mat, coll, tipped=False))
    # loose cable from the tipped monitor
    loose = []
    loose.append(L.cable("R21C_CHAOS_LooseCable",
                         (-85.0, 28.95, 0.006), (-84.35, 29.45, 0.006), 0.0,
                         0.005, mat["cable_black"], coll, n=12, sides=7))
    loose.append(C.hb("R21C_CHAOS_LoosePlug", (0.045, 0.035, 0.030),
                      (-84.32, 29.46, 0.015), mat["plastic"], coll,
                      bevel=0.005, seg=2))
    objs.append(C.join(loose, "R21C_CHAOS_LooseCable", coll))
    # hanging cable drops
    objs.append(_hanging_cable("R21C_CHAOS_CableDropA",
                               (-86.80, 29.15, 4.70), (-86.45, 28.55, 2.52),
                               0.26, 0.006, mat, coll, "cable_black"))
    objs.append(_hanging_cable("R21C_CHAOS_CableDropB",
                               (-81.55, 29.10, 4.70), (-81.90, 28.45, 2.62),
                               0.18, 0.005, mat, coll, "cable_grey"))
    # debris field: tile, concrete, metal, glass
    objs.append(C.broken_tile("R21C_CHAOS_Tile", (-84.75, 29.18, 0.0),
                              mat, coll, w=0.62, d=0.58, rot_z=24))
    objs.append(C.debris_chunk("R21C_CHAOS_ChunkA", (-84.35, 28.42, 0.0),
                               mat, coll, size=(0.16, 0.13, 0.075), seed=11,
                               rot_z=22, subdiv=3))
    objs.append(C.debris_chunk("R21C_CHAOS_ChunkB", (-86.25, 28.05, 0.0),
                               mat, coll, size=(0.21, 0.12, 0.055), seed=12,
                               rot_z=71, subdiv=3))
    objs.append(C.debris_chunk("R21C_CHAOS_ChunkC", (-82.60, 27.92, 0.0),
                               mat, coll, size=(0.13, 0.10, 0.050), seed=13,
                               rot_z=140, subdiv=3))
    shards = []
    for i, (dx, dy, sz, ang) in enumerate(((-0.18, 0.05, 0.045, 0),
                                            (0.06, 0.14, 0.035, 55),
                                            (0.16, -0.10, 0.030, 120))):
        shards.append(C.shard(f"R21C_CHAOS_Glass{i}",
                              (-85.05 + dx, 28.82 + dy, -0.001),
                              mat, coll, size=(sz, sz * 0.7), thick=0.003,
                              seed=300 + i, rot_z=ang))
    objs.append(C.join(shards, "R21C_CHAOS_GlassDebris", coll, weighted=False))
    return objs
