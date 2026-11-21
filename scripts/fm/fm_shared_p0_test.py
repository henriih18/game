"""
FRECUENCIA MUERTA - P0a P0_TEST_ASSEMBLY.

A 5.4 m service run crossing three fictitious concrete walls.  Every
component is a linked duplicate of a master (shared mesh data); the walls,
floor and ceiling are test-only geometry, not library assets.
"""
import bpy
import bmesh
import math
import json
from mathutils import Vector, Matrix

from fm_shared_p0_lib import (ensure_tree, ensure_materials, box, join_group,
                              clear_collection_tree, tri_count)
from fm_shared_p0_services import M, GALV, DARK, BARE, ALU, RUB, RED, COND

T = ensure_tree()
COLL = bpy.data.collections["P0_TEST_ASSEMBLY"]
ORIGIN = Vector((300.0, 0.0, 0.0))
CEIL = 4.85


def master_mesh(name):
    root = bpy.data.objects.get(name + "_ROOT")
    if root is None:
        raise RuntimeError("missing master " + name)
    for o in bpy.data.objects:
        if o.parent == root and o.type == 'MESH':
            return o
    raise RuntimeError("master has no mesh " + name)


def inst(name, loc, rot=(0, 0, 0), tag=None):
    src = master_mesh(name)
    ob = src.copy()
    ob.data = src.data
    ob.parent = None
    ob.matrix_parent_inverse = Matrix.Identity(4)
    ob.location = ORIGIN + Vector(loc)
    ob.rotation_euler = rot
    ob.name = (tag or name) + "_P0"
    COLL.objects.link(ob)
    return ob


def test_box(name, sx, sy, sz, loc, mat=None, bevel=0.0):
    b = box(COLL, name, sx, sy, sz, (0, 0, 0), mat or M["concrete"], bevel, 2)
    b.location = ORIGIN + Vector(loc)
    return b


def wall_with_holes(name, x, holes, width=3.8, height=CEIL, thick=0.24):
    """holes: list of (y,z,w,h) in wall local coordinates."""
    wall = test_box(name, thick, width, height, (x, 0, height / 2))
    # cutters
    cutters = []
    for i, (y, z, w, h) in enumerate(holes):
        c = test_box("%s_CUT%d" % (name, i), thick + 0.10, w, h,
                     (x, y, z))
        c.display_type = 'WIRE'
        c.hide_render = True
        cutters.append(c)
    for c in cutters:
        m = wall.modifiers.new("cut_" + c.name, "BOOLEAN")
        m.operation = 'DIFFERENCE'
        m.object = c
        m.solver = 'EXACT'
    bpy.context.view_layer.objects.active = wall
    for m in list(wall.modifiers):
        try:
            bpy.ops.object.modifier_apply(modifier=m.name)
        except Exception as exc:
            print("boolean failed", name, m.name, exc)
    for c in cutters:
        bpy.data.objects.remove(c, do_unlink=True)
    for p in wall.data.polygons:
        p.use_smooth = False
    return wall


def build():
    global COLL, T
    if bpy.data.collections.get("P0_TEST_ASSEMBLY"):
        clear_collection_tree("P0_TEST_ASSEMBLY")
    T = ensure_tree()
    coll = bpy.data.collections["P0_TEST_ASSEMBLY"]
    COLL = coll

    # ---- test shell -------------------------------------------------------
    test_box("P0_TA_Floor", 6.2, 4.4, 0.10, (0.4, 0, -0.05),
             M["concrete"], 0.0)
    test_box("P0_TA_Ceiling", 6.2, 4.4, 0.14, (0.4, 0, CEIL + 0.07),
             M["concrete"], 0.0)
    holes = [(0.0, 3.55, 1.00, 0.80),      # duct / transition
             (-1.0, 3.95, 0.58, 0.28),     # tray
             (1.0, 3.70, 0.20, 0.20),      # sprinkler
             (1.6, 3.25, 0.12, 0.12)]      # conduit
    wall_with_holes("P0_TA_WallRear", -2.0, holes)
    wall_with_holes("P0_TA_WallMid", 0.0, holes)
    wall_with_holes("P0_TA_WallFront", 3.2, holes)

    # ---- sleeves at the rear and middle walls ----------------------------
    for wx in (-2.0, 0.0):
        inst("SM_SH_SLEEVE_RECT_800x600", (wx, 0, 3.55),
             tag="P0_SLV_RECT_%d" % int(wx * 10))
        inst("SM_SH_SLEEVE_TRAY_400", (wx, -1.0, 3.90),
             tag="P0_SLV_TRAY_%d" % int(wx * 10))
        inst("SM_SH_SLEEVE_PIPE_80", (wx, 1.0, 3.70),
             tag="P0_SLV_PIPE_%d" % int(wx * 10))
    # front wall sleeves
    inst("SM_SH_SLEEVE_TRAY_400", (3.2, -1.0, 3.90), tag="P0_SLV_TRAY_F")
    inst("SM_SH_SLEEVE_PIPE_80", (3.2, 1.0, 3.70), tag="P0_SLV_PIPE_F")

    # ---- HVAC 800x600 -----------------------------------------------------
    inst("SM_SH_HVAC_RECT800x600_L2000", (-1.985, 0, 3.55), tag="P0_HVAC_A")
    inst("SM_SH_HVAC_RECT800x600_PEN400", (0.0, 0, 3.55), tag="P0_HVAC_SPOOL")
    inst("SM_SH_HVAC_RECT800x600_L2000", (0.4, 0, 3.55), tag="P0_HVAC_B")
    inst("SM_SH_HVAC_TRANS_800x600_600x400", (2.4, 0, 3.55), tag="P0_HVAC_TRANS")
    inst("SM_SH_HVAC_RECT600x400_PEN400", (3.0, 0, 3.55), tag="P0_HVAC_SMALL")
    inst("SM_SH_HVAC_GRILLE_600x400", (3.4, 0, 3.55), tag="P0_HVAC_GRILLE")

    # ---- cable tray 400 ---------------------------------------------------
    inst("SM_SH_TRAY_400_L2000", (-2.0, -1.0, 3.90), tag="P0_TRAY_A")
    inst("SM_SH_TRAY_400_PEN400", (0.0, -1.0, 3.90), tag="P0_TRAY_SPOOL")
    inst("SM_SH_TRAY_400_L2000", (0.4, -1.0, 3.90), tag="P0_TRAY_B")
    inst("SM_SH_TRAY_400_PEN400", (2.4, -1.0, 3.90), tag="P0_TRAY_C")
    inst("SM_SH_TRAY_400_PEN400", (2.8, -1.0, 3.90), tag="P0_TRAY_D")
    inst("SM_SH_TRAY_400_COVER_L2000", (0.4, -1.0, 4.00), tag="P0_TRAY_COVER")

    # ---- sprinkler DN80 / drop / head ------------------------------------
    inst("SM_SH_SPRINK_PIPE_80_L2000", (-2.0, 1.0, 3.70), tag="P0_SPR_A")
    inst("SM_SH_SPRINK_PIPE_80_PEN400", (0.0, 1.0, 3.70), tag="P0_SPR_SPOOL")
    inst("SM_SH_SPRINK_PIPE_80_L2000", (0.4, 1.0, 3.70), tag="P0_SPR_B")
    inst("SM_SH_SPRINK_TEE_80_50", (2.4, 1.0, 3.70), tag="P0_SPR_TEE")
    inst("SM_SH_SPRINK_DROP_50", (2.8, 1.0, 3.297), tag="P0_SPR_DROP")
    inst("SM_SH_SPRINK_HEAD", (2.8, 1.0, 2.853), tag="P0_SPR_HEAD")

    # ---- conduit 25 -------------------------------------------------------
    inst("SM_SH_CONDUIT_25_L2000", (-2.0, 1.6, 3.25), tag="P0_CDT_A")
    inst("SM_SH_CONDUIT_25_PEN400", (0.0, 1.6, 3.25), tag="P0_CDT_SPOOL")
    inst("SM_SH_CONDUIT_25_L2000", (0.4, 1.6, 3.25), tag="P0_CDT_B")
    inst("SM_SH_CONDUIT_25_PEN400", (2.4, 1.6, 3.25), tag="P0_CDT_C")
    inst("SM_SH_CONDUIT_BOX_100", (2.8, 1.6, 3.25), tag="P0_CDT_BOX")

    # ---- supports ---------------------------------------------------------
    inst("SM_SH_SUPPORT_TRAPEZE_800", (-1.4, 0, CEIL), tag="P0_SUP_HVAC_A")
    inst("SM_SH_SUPPORT_TRAPEZE_800", (1.6, 0, CEIL), tag="P0_SUP_HVAC_B")
    inst("SM_SH_SUPPORT_TRAY_400", (-1.2, -1.0, CEIL), tag="P0_SUP_TRAY_A")
    inst("SM_SH_SUPPORT_TRAY_400", (1.2, -1.0, CEIL), tag="P0_SUP_TRAY_B")
    inst("SM_SH_SUPPORT_PIPE_80", (-1.2, 1.0, CEIL), tag="P0_SUP_PIPE_A")
    inst("SM_SH_SUPPORT_PIPE_80", (1.4, 1.0, CEIL), tag="P0_SUP_PIPE_B")
    inst("SM_SH_SUPPORT_CONDUIT_25", (-1.4, 1.6, CEIL), tag="P0_SUP_CDT_A")
    inst("SM_SH_SUPPORT_CONDUIT_25", (1.4, 1.6, CEIL), tag="P0_SUP_CDT_B")

    # root for the assembly
    root = bpy.data.objects.new("P0_TEST_ASSEMBLY_ROOT", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.6
    coll.objects.link(root)
    root.location = ORIGIN
    for ob in [o for o in coll.objects if o is not root]:
        ob.parent = root
        ob.matrix_parent_inverse = Matrix.Identity(4)
        ob.location = ob.location - ORIGIN
    root["fm_asset"] = "P0_TEST_ASSEMBLY"
    root["fm_generation"] = "P0A_CONTINUITY_TEST"
    root["fm_note"] = ("linked duplicates of shared masters; test-only walls, "
                       "floor and ceiling; not deployed in L1 rooms")
    meshes = [o for o in bpy.data.objects if o.parent == root and o.type == 'MESH']
    from fm_shared_p0_lib import smart_uv
    for n in ("P0_TA_Floor", "P0_TA_Ceiling", "P0_TA_WallRear",
              "P0_TA_WallMid", "P0_TA_WallFront"):
        ob = bpy.data.objects.get(n)
        if ob and not ob.data.uv_layers:
            smart_uv(ob)
    print("TEST_MESHES", len(meshes), "TRIS", sum(tri_count(o) for o in meshes))
    return root


if __name__ == "__main__":
    build()
