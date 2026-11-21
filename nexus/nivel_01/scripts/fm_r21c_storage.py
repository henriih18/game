"""Key rack and heavy equipment shelving for L1_SECURITY_R21C_HERO.

Both are wall units on the east wall of Security 03.  The key rack is an
open steel cabinet with three shelves, twelve hooks, keys with colour-coded
tags and stamped codes.  The shelving is a bolted 4-level unit with
X-bracing, slotted uprights, shelf lips and equipment (hard hats, bins,
cases, a coiled hose).  No documents or personal items.
"""
import math
import bpy
from mathutils import Vector, Matrix

import fm_ops_lib as L
import fm_r21c_lib as C


# --------------------------------------------------------------------------------------
# key rack
# --------------------------------------------------------------------------------------
def key_rack(mat, coll, debug=False):
    X0, Y0, Z0 = -71.146, 20.120, 1.120
    W, H, D = 0.950, 0.950, 0.140

    def X(v):
        return X0 + v

    def Y(v):
        return Y0 + v

    def Z(v):
        return Z0 + v

    parts = []
    # front frame (one island)
    parts.append(C.frame("R21C_KEYS_Frame", W, H, W - 0.070, H - 0.070, 0.030,
                         (X(-D + 0.015), Y(W * 0.5), Z(H * 0.5)),
                         mat["green"], coll, bevel=0.002, seg=3))
    # carcass: back, sides, top/bottom
    parts.append(C.hb("R21C_KEYS_Back", (0.035, W - 0.030, H - 0.010),
                      (X(-0.0175), Y(W * 0.5), Z(H * 0.5)), mat["green_dark"], coll,
                      bevel=0.003, seg=2))
    for sy in (0.014, W - 0.014):
        parts.append(C.hb(f"R21C_KEYS_Side{sy:.3f}", (D - 0.020, 0.018, H - 0.020),
                          (X(-D * 0.5 + 0.009), Y(sy), Z(H * 0.5)),
                          mat["green"], coll, bevel=0.003, seg=3))
    for sz, nm in ((0.010, "Bot"), (H - 0.010, "Top")):
        parts.append(C.hb(f"R21C_KEYS_{nm}", (D - 0.020, W - 0.004, 0.018),
                          (X(-D * 0.5 + 0.009), Y(W * 0.5), Z(sz)),
                          mat["green"], coll, bevel=0.003, seg=3))
    # three full-depth shelves with front lips
    shelf_z = (0.250, 0.560, 0.870)
    for i, sz in enumerate(shelf_z):
        parts.append(C.hb(f"R21C_KEYS_Shelf{i}", (0.128, W - 0.078, 0.014),
                          (X(-0.066), Y(W * 0.5), Z(sz)), mat["galv"], coll,
                          bevel=0.002, seg=2))
        parts.append(C.hb(f"R21C_KEYS_ShelfLip{i}", (0.012, W - 0.078, 0.024),
                          (X(-0.134), Y(W * 0.5), Z(sz - 0.016)), mat["galv"], coll,
                          bevel=0.0015, seg=2))
        # small corner brackets
        for sy in (0.046, W - 0.046):
            parts.append(C.hb(f"R21C_KEYS_ShelfBrk{i}{sy:.3f}", (0.084, 0.014, 0.048),
                              (X(-0.073), Y(sy), Z(sz - 0.032)), mat["steel_dark"], coll,
                              bevel=0.002, seg=2))
    # header plate on the upper front rail
    parts.append(C.hb("R21C_KEYS_Header", (0.006, 0.560, 0.062),
                      (X(-D - 0.003), Y(W * 0.5), Z(H - 0.030)), mat["dark"], coll,
                      bevel=0.0015, seg=2))
    parts.append(C.text("R21C_KEYS_HeaderText", "LLAVES", 0.044,
                        (X(-D - 0.0085), Y(W * 0.5), Z(H - 0.030)), C.ROT_E,
                        mat["white"], coll, extrude=0.0007))
    # hooks + keys + tags
    rows = (0.205, 0.515, 0.825)
    cols = (0.150, 0.370, 0.590, 0.810)
    colors = ("paint_red", "hazard_y")
    codes = ("A", "B", "C", "D")
    for r, rz in enumerate(rows):
        for c, cy in enumerate(cols):
            idx = r * 4 + c
            # hook
            parts.append(C.hb(f"R21C_KEYS_HookBase{idx}", (0.008, 0.026, 0.026),
                              (X(-0.033), Y(cy), Z(rz)), mat["steel_bare"], coll,
                              bevel=0.0014, seg=2))
            parts.append(C.tube(f"R21C_KEYS_Hook{idx}",
                                [(X(-0.036), Y(cy), Z(rz)),
                                 (X(-0.080), Y(cy), Z(rz + 0.002)),
                                 (X(-0.100), Y(cy), Z(rz + 0.014)),
                                 (X(-0.100), Y(cy), Z(rz + 0.020))],
                                0.0036, mat["steel_bare"], coll, sides=7))
            # ring
            parts.append(C.torus(f"R21C_KEYS_Ring{idx}",
                                 (X(-0.100), Y(cy), Z(rz + 0.004)), 0.0145, 0.0026,
                                 mat["steel_bare"], coll, rot=(0, math.radians(90), 0),
                                 major=18, minor=6))
            # key blade + teeth
            parts.append(C.hb(f"R21C_KEYS_Blade{idx}", (0.003, 0.011, 0.050),
                              (X(-0.100), Y(cy), Z(rz - 0.033)),
                              mat["aluminum"], coll, bevel=0.0008, seg=2))
            for k, (dy, dz) in enumerate(((0.008, -0.044), (0.006, -0.050),
                                           (0.009, -0.056))):
                parts.append(C.hb(f"R21C_KEYS_Tooth{idx}{k}", (0.0025, 0.007, 0.005),
                                  (X(-0.1005), Y(cy) + 0.010, Z(rz + dz)),
                                  mat["aluminum"], coll, bevel=0.0004, seg=1))
            # colour tag with a white label and stamped code
            tag_col = mat[colors[(r + c) % 2]]
            ty = cy + 0.028
            parts.append(C.hb(f"R21C_KEYS_Tag{idx}", (0.004, 0.032, 0.048),
                              (X(-0.104), Y(ty), Z(rz - 0.036)), tag_col, coll,
                              bevel=0.001, seg=2))
            parts.append(C.hb(f"R21C_KEYS_TagLabel{idx}", (0.0015, 0.024, 0.018),
                              (X(-0.1065), Y(ty), Z(rz - 0.026)), mat["paper"], coll,
                              bevel=0.0003, seg=1))
            if idx < 9:
                parts.append(C.text(f"R21C_KEYS_TagText{idx}", codes[idx % 4], 0.016,
                                    (X(-0.1078), Y(ty), Z(rz - 0.026)), C.ROT_E,
                                    mat["dark"], coll, extrude=0.0003))
            # empty hooks on the top row keep the rack readable
    # lock on the right stile + corner bolts
    parts.append(C.hb("R21C_KEYS_LockPlate", (0.012, 0.042, 0.100),
                      (X(-D - 0.004), Y(W - 0.055), Z(0.600)), mat["steel_bare"], coll,
                      bevel=0.002, seg=3))
    parts.append(C.cy("R21C_KEYS_Lock", 0.014, 0.014,
                      (X(-D - 0.012), Y(W - 0.055), Z(0.600)), mat["steel_bare"], coll,
                      rot=(0, math.radians(90), 0), segments=16, bevel=0.0015))
    parts.append(C.hb("R21C_KEYS_KeySlot", (0.004, 0.005, 0.014),
                      (X(-D - 0.020), Y(W - 0.055), Z(0.600)), mat["dark"], coll,
                      bevel=0.0005, seg=1))
    for yy in (0.045, W - 0.045):
        for zz in (0.045, H - 0.045):
            parts.append(C.screw(f"R21C_KEYS_FrameScrew{yy:.3f}{zz:.3f}",
                    (X(-D - 0.001), Y(yy), Z(zz)), (-1, 0, 0), mat["steel_bare"], coll,
                    r=0.0045, socket_mat=mat["dark"]))
    # corner reinforcement blocks inside
    for yy in (0.030, W - 0.030):
        for zz in (0.030, H - 0.030):
            parts.append(C.hb(f"R21C_KEYS_Corner{yy:.3f}{zz:.3f}",
                              (0.030, 0.030, 0.030),
                              (X(-0.120), Y(yy), Z(zz)), mat["steel_dark"], coll,
                              bevel=0.002, seg=2))
    if debug:
        return parts
    ob = C.join(parts, "R21C_KEYS_KeyRack", coll)
    return ob


# --------------------------------------------------------------------------------------
# shelving
# --------------------------------------------------------------------------------------
def shelving(mat, coll, debug=False):
    X0, Y0, Z0 = -71.146, 22.120, 0.0015
    W, H, D = 2.320, 2.300, 0.600

    def X(v):
        return X0 + v

    def Y(v):
        return Y0 + v

    def Z(v):
        return Z0 + v

    parts = []
    # four uprights + feet + top caps
    for iy, yy in enumerate((0.035, W - 0.035)):
        for ix, xx in enumerate((-0.050, -D + 0.050)):
            tag = f"{iy}{ix}"
            parts.append(C.hb(f"R21C_SHELF_Upright{tag}", (0.055, 0.055, H - 0.010),
                              (X(xx), Y(yy), Z(H * 0.5)), mat["galv"], coll,
                              bevel=0.003, seg=3))
            parts.append(C.hb(f"R21C_SHELF_Foot{tag}", (0.140, 0.140, 0.012),
                              (X(xx), Y(yy), Z(0.006)), mat["steel_dark"], coll,
                              bevel=0.003, seg=2))
            parts.append(C.hb(f"R21C_SHELF_Cap{tag}", (0.062, 0.062, 0.012),
                              (X(xx), Y(yy), Z(H - 0.006)), mat["plastic"], coll,
                              bevel=0.003, seg=2))
            for dx in (-0.040, 0.040):
                for dy in (-0.040, 0.040):
                    parts.append(C.bolt(f"R21C_SHELF_Anchor{tag}{dx:+.2f}{dy:+.2f}",
                           (X(xx) + dx, Y(yy) + dy, Z(0.013)), (0, 0, 1),
                           0.0075, 0.008, mat["steel_bare"], coll,
                           socket_mat=mat["dark"]))
    # beams at four levels, front and back
    levels = (0.360, 0.960, 1.560, 2.160)
    for i, zz in enumerate(levels):
        for side, xx in (("F", -D + 0.060), ("B", -0.060)):
            parts.append(C.hb(f"R21C_SHELF_Beam{i}{side}", (0.070, W - 0.110, 0.055),
                              (X(xx), Y(W * 0.5), Z(zz)), mat["galv"], coll,
                              bevel=0.003, seg=2))
            for yy in (0.030, W - 0.030):
                parts.append(C.hb(f"R21C_SHELF_BeamPlate{i}{side}{yy:.3f}",
                                  (0.078, 0.016, 0.080),
                                  (X(xx), Y(yy), Z(zz)), mat["steel_dark"], coll,
                                  bevel=0.002, seg=2))
                for dz in (-0.026, 0.026):
                    parts.append(C.screw(f"R21C_SHELF_BeamBolt{i}{side}{yy:.3f}{dz:+.3f}",
                            (X(xx) - 0.038, Y(yy), Z(zz + dz)), (-1, 0, 0),
                            mat["steel_bare"], coll, r=0.0055, socket_mat=mat["dark"]))
    # shelves + lips + label strips
    for i, zz in enumerate((0.390, 0.990, 1.590, 2.190)):
        parts.append(C.hb(f"R21C_SHELF_Shelf{i}", (D - 0.060, W - 0.120, 0.018),
                          (X(-D * 0.5), Y(W * 0.5), Z(zz)), mat["galv"], coll,
                          bevel=0.002, seg=2))
        parts.append(C.hb(f"R21C_SHELF_Lip{i}", (0.012, W - 0.120, 0.032),
                          (X(-D + 0.026), Y(W * 0.5), Z(zz - 0.015)),
                          mat["galv"], coll, bevel=0.0015, seg=2))
        parts.append(C.hb(f"R21C_SHELF_Label{i}", (0.006, 0.330, 0.024),
                          (X(-D + 0.019), Y(0.480), Z(zz - 0.014)),
                          mat["hazard_y"], coll, bevel=0.001, seg=2))
        if i >= 2:
            # shelf colour band is enough: tiny stamped text created unreliable
            # coplanar islands against the front lip after joining.
            pass
    # slotted holes on the front uprights
    for iy, yy in enumerate((0.035, W - 0.035)):
        for k in range(11):
            zz = 0.220 + k * 0.185
            parts.append(C.cy(f"R21C_SHELF_Slot{iy}{k}", 0.0065, 0.006,
                              (X(-0.578), Y(yy), Z(zz)), mat["dark"], coll,
                              rot=(0, math.radians(90), 0), segments=12, bevel=0.001))
    # X-bracing at the back
    for k, (z0, z1) in enumerate(((0.420, 1.060), (1.060, 1.700), (1.700, 2.120))):
        for s in (-1, 1):
            p0 = (X(-0.030), Y(0.070 if s < 0 else W - 0.070), Z(z0))
            p1 = (X(-0.030), Y(W - 0.070 if s < 0 else 0.070), Z(z1))
            parts.append(C.tube(f"R21C_SHELF_Brace{k}{s}", [p0, p1], 0.011,
                                mat["steel_dark"], coll, sides=6))
            if s < 0:
                for p in (p0, p1):
                    parts.append(C.bolt(f"R21C_SHELF_BraceBolt{k}{s}{p[1]:.2f}",
                           (p[0] - 0.008, p[1], p[2]), (-1, 0, 0), 0.010, 0.008,
                           mat["steel_bare"], coll, socket_mat=mat["dark"]))
    # contents
    shelf_top = {0: Z(0.390) + 0.010, 1: Z(0.990) + 0.010,
                 2: Z(1.590) + 0.010, 3: Z(2.190) + 0.010}
    # top shelf
    parts.append(C.helmet("R21C_SHELF_HelmetA", (X(-0.330), Y(0.430), shelf_top[3]), mat, coll,
             shell_key="white", rot_z=15))
    parts.append(C.helmet("R21C_SHELF_HelmetB", (X(-0.390), Y(0.820), shelf_top[3]), mat, coll,
             shell_key="hazard_y", rot_z=-35))
    parts.append(C.equipment_case("R21C_SHELF_CaseA", (X(-0.350), Y(1.520), shelf_top[3]), mat, coll,
                     rot_z=8))
    # third shelf
    parts.append(C.storage_bin("R21C_SHELF_BinA", (X(-0.330), Y(0.360), shelf_top[2]), mat, coll,
                  color="green", rot_z=4))
    parts.append(C.helmet("R21C_SHELF_HelmetC", (X(-0.380), Y(0.900), shelf_top[2]), mat, coll,
             shell_key="white", rot_z=70))
    parts.append(C.equipment_case("R21C_SHELF_CaseB", (X(-0.350), Y(1.560), shelf_top[2]), mat, coll,
                     rot_z=-6, h=0.24))
    # second shelf
    for k in range(3):
        parts.append(C.torus(f"R21C_SHELF_Hose{k}",
                             (X(-0.360), Y(0.470), shelf_top[1] + 0.014 + k * 0.026),
                             0.140, 0.014, mat["rubber_red"], coll,
                             major=24, minor=7))
    parts.append(C.cy("R21C_SHELF_HoseNozzle", 0.020, 0.080,
                      (X(-0.360), Y(0.610), shelf_top[1] + 0.066),
                      mat["steel_bare"], coll, rot=(math.radians(90), 0, 0),
                      segments=12, bevel=0.002))
    parts.append(C.storage_bin("R21C_SHELF_BinB", (X(-0.330), Y(1.200), shelf_top[1]), mat, coll,
                  color="dark", rot_z=-8))
    parts.append(C.helmet("R21C_SHELF_HelmetD", (X(-0.390), Y(1.760), shelf_top[1]), mat, coll,
             shell_key="green", rot_z=110))
    # bottom shelf
    parts.append(C.storage_bin("R21C_SHELF_BinC", (X(-0.320), Y(0.400), shelf_top[0]), mat, coll,
                  color="dark", rot_z=0, w=0.38, d=0.32, h=0.24))
    parts.append(C.storage_bin("R21C_SHELF_BinD", (X(-0.330), Y(0.920), shelf_top[0]), mat, coll,
                  color="green", rot_z=6, w=0.34, d=0.30, h=0.20))
    parts.append(C.equipment_case("R21C_SHELF_CaseC", (X(-0.350), Y(1.700), shelf_top[0]), mat, coll,
                     rot_z=10, w=0.56, d=0.38, h=0.30))
    if debug:
        return parts
    ob = C.join(parts, "R21C_SHELF_Unit", coll)
    return ob


def build(mat, coll):
    a = key_rack(mat, coll)
    b = shelving(mat, coll)
    return [a, b]
