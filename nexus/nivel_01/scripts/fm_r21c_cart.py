"""Hero tool cart / cabinet for L1_SECURITY_R21C_HERO.

Rolling five-drawer tool cabinet with four casters, ball-bearing slides,
aluminium pulls, gang lock bar, rubber bumpers, a lipped top with a rubber
mat and a divided parts tray.  One drawer is pulled out to show the box.
"""
import math
import bpy
import bmesh
from mathutils import Vector, Matrix

import fm_ops_lib as L
import fm_r21c_lib as C

CX, CY = -80.650, 21.750
W, D = 0.720, 0.480


def caster(name, x, y, mat, coll, swivel=0.0):
    parts = []
    # wheel (axis X), hub and tread
    parts.append(C.cy(name + "_Wheel", 0.062, 0.034, (x, y, 0.062), mat["rubber"], coll,
                      rot=(0, math.radians(90), 0), segments=24, bevel=0.004))
    parts.append(C.cy(name + "_Hub", 0.026, 0.040, (x, y, 0.062), mat["aluminum"], coll,
                      rot=(0, math.radians(90), 0), segments=16, bevel=0.002))
    # fork plates
    for dy in (-0.024, 0.024):
        parts.append(C.hb(f"{name}_Fork{dy:+.3f}", (0.012, 0.008, 0.080),
                          (x, y + dy, 0.086), mat["steel_dark"], coll,
                          bevel=0.002, seg=2))
    parts.append(C.hb(name + "_ForkTop", (0.062, 0.062, 0.012),
                      (x, y, 0.124), mat["steel_dark"], coll, bevel=0.003, seg=2))
    parts.append(C.cy(name + "_Swivel", 0.030, 0.016, (x, y, 0.133),
                      mat["steel_bare"], coll, segments=20, bevel=0.002))
    parts.append(C.hb(name + "_Plate", (0.085, 0.085, 0.010),
                      (x, y, 0.146), mat["steel_dark"], coll, bevel=0.003, seg=2))
    for dx in (-0.028, 0.028):
        for dy in (-0.028, 0.028):
            parts.append(C.bolt(f"{name}_Bolt{dx:+.3f}{dy:+.3f}", (x + dx, y + dy, 0.152),
                   (0, 0, 1), 0.0065, 0.007, mat["steel_bare"], coll,
                   socket_mat=mat["dark"]))
    # small swivel offset for readability
    ob = C.join(parts, name, coll)
    if swivel:
        C.bake_world(ob)
        piv = Vector((x, y, 0.133))
        ob.matrix_world = (Matrix.Translation(piv) @ Matrix.Rotation(math.radians(swivel), 4, "Z") @
                           Matrix.Translation(-piv))
    return ob


def drawer(name, x0, y_front, z0, h, mat, coll, open_dy=0.0, label_key="hazard_y", debug=False):
    parts = []
    yf = y_front + open_dy
    # front
    parts.append(C.hb(name + "_Front", (0.690, 0.024, h - 0.006),
                      (x0, yf, z0 + h * 0.5), mat["green"], coll,
                      bevel=0.003, seg=3))
    # raised panel
    parts.append(C.hb(name + "_Panel", (0.650, 0.012, h - 0.030),
                      (x0, yf - 0.0175, z0 + h * 0.5), mat["green_dark"], coll,
                      bevel=0.002, seg=2))
    # pull handle with two posts
    parts.append(C.hb(name + "_Handle", (0.300, 0.020, 0.020),
                      (x0, yf - 0.037, z0 + h * 0.5), mat["aluminum"], coll,
                      bevel=0.003, seg=3))
    for dx in (-0.120, 0.120):
        parts.append(C.hb(name + f"_HandlePost{dx:+.3f}", (0.020, 0.020, 0.016),
                          (x0 + dx, yf - 0.028, z0 + h * 0.5), mat["aluminum"], coll,
                          bevel=0.002, seg=2))
    # label holder and colour strip
    lx = x0 - 0.255
    parts.append(C.hb(name + "_LabelHolder", (0.080, 0.008, 0.032),
                      (lx, yf - 0.0205, z0 + h * 0.5 + 0.030), mat["dark"], coll,
                      bevel=0.001, seg=2))
    parts.append(C.hb(name + "_Label", (0.070, 0.004, 0.024),
                      (lx, yf - 0.0245, z0 + h * 0.5 + 0.030), mat["paper"], coll,
                      bevel=0.0005, seg=1))
    parts.append(C.hb(name + "_Colour", (0.010, 0.004, 0.020),
                      (lx + 0.060, yf - 0.023, z0 + h * 0.5 + 0.030),
                      mat[label_key], coll, bevel=0.0005, seg=1))
    # drawer box + slides (hidden when closed, visible on the pulled drawer)
    box_back = yf + 0.430
    parts.append(C.hb(name + "_BoxBottom", (0.660, 0.420, 0.014),
                      (x0, yf + 0.220, z0 + 0.020), mat["steel_dark"], coll,
                      bevel=0.002, seg=2))
    for dx in (-0.330, 0.330):
        parts.append(C.hb(name + f"_BoxSide{dx:+.3f}", (0.014, 0.420, h - 0.040),
                          (x0 + dx, yf + 0.220, z0 + h * 0.5),
                          mat["steel_dark"], coll, bevel=0.002, seg=2))
    parts.append(C.hb(name + "_BoxBack", (0.660, 0.016, h - 0.050),
                      (x0, box_back, z0 + h * 0.5), mat["steel_dark"], coll,
                      bevel=0.002, seg=2))
    for dx in (-0.342, 0.342):
        parts.append(C.hb(name + f"_Slide{dx:+.3f}", (0.012, 0.360, 0.030),
                          (x0 + dx, yf + 0.180, z0 + 0.030),
                          mat["steel_bare"], coll, bevel=0.0015, seg=2))
    if debug:
        return parts
    ob = C.join(parts, name, coll)
    return ob


def build(mat, coll, debug=False):
    parts = []
    # base frame and casters
    parts.append(C.hb("R21C_CART_Base", (0.740, 0.500, 0.055),
                      (CX, CY, 0.1725), mat["steel_dark"], coll,
                      bevel=0.004, seg=3))
    parts.append(caster("R21C_CART_Caster0", CX - 0.300, CY - 0.185, mat, coll, swivel=18))
    parts.append(caster("R21C_CART_Caster1", CX + 0.300, CY - 0.185, mat, coll, swivel=-12))
    parts.append(caster("R21C_CART_Caster2", CX - 0.300, CY + 0.185, mat, coll, swivel=0))
    parts.append(caster("R21C_CART_Caster3", CX + 0.300, CY + 0.185, mat, coll, swivel=0))
    # carcass
    parts.append(C.hb("R21C_CART_Back", (0.700, 0.020, 0.640),
                      (CX, CY + 0.240, 0.555), mat["green"], coll,
                      bevel=0.004, seg=3))
    for dx in (-0.350, 0.350):
        parts.append(C.hb(f"R21C_CART_Side{dx:+.3f}", (0.020, 0.440, 0.660),
                          (CX + dx, CY, 0.555), mat["green"], coll,
                          bevel=0.004, seg=3))
    parts.append(C.hb("R21C_CART_Bottom", (0.710, 0.480, 0.030),
                      (CX, CY, 0.215), mat["steel_dark"], coll,
                      bevel=0.003, seg=2))
    parts.append(C.hb("R21C_CART_TopDeck", (0.710, 0.500, 0.030),
                      (CX, CY, 0.885), mat["steel_dark"], coll,
                      bevel=0.003, seg=2))
    for dx in (-0.350, 0.350):
        for dy in (-0.240, 0.240):
            parts.append(C.hb(f"R21C_CART_Post{dx:+.3f}{dy:+.3f}", (0.024, 0.024, 0.660),
                              (CX + dx, CY + dy, 0.555), mat["steel_dark"], coll,
                              bevel=0.002, seg=2))
    # drawer stack
    yf = CY - 0.242
    stack = [(0.240, 0.085), (0.332, 0.110), (0.449, 0.110), (0.566, 0.160), (0.732, 0.160)]
    for i, (z0, h) in enumerate(stack):
        open_dy = -0.120 if i == 2 else 0.0
        parts.append(drawer(f"R21C_CART_Drawer{i}", CX, yf, z0, h, mat, coll,
                            open_dy=open_dy,
                            label_key=("hazard_y" if i % 2 == 0 else "white")))
    # top plate, lip, mat and tray
    parts.append(C.hb("R21C_CART_Top", (0.780, 0.540, 0.040),
                      (CX, CY, 0.920), mat["green"], coll, bevel=0.006, seg=4))
    for dy in (-1, 1):
        parts.append(C.hb(f"R21C_CART_TopLipY{dy}", (0.780, 0.020, 0.020),
                          (CX, CY + dy * 0.260, 0.947), mat["steel_dark"], coll,
                          bevel=0.002, seg=2))
    for dx in (-1, 1):
        parts.append(C.hb(f"R21C_CART_TopLipX{dx}", (0.020, 0.500, 0.020),
                          (CX + dx * 0.390, CY, 0.947), mat["steel_dark"], coll,
                          bevel=0.002, seg=2))
    parts.append(C.hb("R21C_CART_Mat", (0.700, 0.460, 0.007),
                      (CX, CY, 0.9415), mat["rubber"], coll, bevel=0.001, seg=1))
    # divided parts tray
    tx, ty = CX - 0.110, CY + 0.095
    parts.append(C.hb("R21C_CART_TrayBase", (0.230, 0.150, 0.010),
                      (tx, ty, 0.948), mat["steel_dark"], coll, bevel=0.002, seg=2))
    for dx in (-1, 1):
        parts.append(C.hb(f"R21C_CART_TraySideX{dx}", (0.012, 0.130, 0.045),
                          (tx + dx * 0.106, ty, 0.968), mat["steel_dark"], coll,
                          bevel=0.002, seg=2))
    for dy in (-1, 1):
        parts.append(C.hb(f"R21C_CART_TraySideY{dy}", (0.210, 0.012, 0.045),
                          (tx, ty + dy * 0.066, 0.968), mat["steel_dark"], coll,
                          bevel=0.002, seg=2))
    parts.append(C.hb("R21C_CART_TrayDiv", (0.010, 0.120, 0.040),
                      (tx + 0.010, ty, 0.965), mat["steel_dark"], coll,
                      bevel=0.002, seg=2))
    # a few bolts in the tray
    for i, (dx, dy) in enumerate(((-0.065, -0.030), (-0.045, 0.020),
                                   (0.045, -0.025), (0.060, 0.028),
                                   (-0.020, 0.040))):
        parts.append(C.bolt(f"R21C_CART_TrayBolt{i}", (tx + dx, ty + dy, 0.957),
               (0, 0, 1), 0.0065, 0.008, mat["steel_bare"], coll,
               socket_mat=mat["dark"]))
    # side push handle
    for dy in (-0.150, 0.150):
        parts.append(C.tube(f"R21C_CART_HandlePost{dy:+.3f}",
                            [(CX + 0.360, CY + dy, 0.790), (CX + 0.400, CY + dy, 0.830),
                             (CX + 0.400, CY + dy, 0.980)], 0.014, mat["aluminum"],
                            coll, sides=9))
        parts.append(C.hb(f"R21C_CART_HandleBracket{dy:+.3f}", (0.030, 0.040, 0.060),
                          (CX + 0.350, CY + dy, 0.800), mat["steel_dark"], coll,
                          bevel=0.003, seg=2))
    parts.append(C.tube("R21C_CART_HandleBar",
                        [(CX + 0.400, CY - 0.165, 0.980), (CX + 0.400, CY - 0.100, 0.992),
                         (CX + 0.400, CY + 0.100, 0.992), (CX + 0.400, CY + 0.165, 0.980)],
                        0.014, mat["aluminum"], coll, sides=9))
    parts.append(C.cy("R21C_CART_Grip", 0.018, 0.200, (CX + 0.400, CY, 0.995),
                      mat["rubber"], coll, rot=(math.radians(90), 0, 0),
                      segments=14, bevel=0.002))
    # gang lock bar + lock
    parts.append(C.hb("R21C_CART_LockBar", (0.024, 0.012, 0.600),
                      (CX + 0.315, CY - 0.255, 0.540), mat["steel_bare"], coll,
                      bevel=0.002, seg=2))
    parts.append(C.hb("R21C_CART_LockPlate", (0.045, 0.012, 0.080),
                      (CX + 0.315, CY - 0.261, 0.790), mat["steel_dark"], coll,
                      bevel=0.002, seg=2))
    parts.append(C.cy("R21C_CART_Lock", 0.016, 0.014, (CX + 0.315, CY - 0.268, 0.790),
                      mat["steel_bare"], coll, rot=(math.radians(90), 0, 0),
                      segments=16, bevel=0.0015))
    parts.append(C.hb("R21C_CART_KeySlot", (0.005, 0.004, 0.014),
                      (CX + 0.315, CY - 0.276, 0.790), mat["dark"], coll,
                      bevel=0.0005, seg=1))
    # rubber bumpers
    for dx in (-0.365, 0.365):
        for dz in (0.260, 0.860):
            parts.append(C.hb(f"R21C_CART_Bumper{dx:+.3f}{dz:.3f}", (0.035, 0.035, 0.035),
                              (CX + dx, CY - 0.252, dz), mat["rubber"], coll,
                              bevel=0.006, seg=3))
    # label on the top lip
    parts.append(C.hb("R21C_CART_TopLabel", (0.300, 0.006, 0.035),
                      (CX, CY - 0.268, 0.947), mat["hazard_y"], coll,
                      bevel=0.001, seg=2))
    if debug:
        return parts
    ob = C.join(parts, "R21C_CART_ToolCart", coll)
    return ob


if __name__ == "__main__":
    pass
