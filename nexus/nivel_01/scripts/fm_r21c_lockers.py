"""Hero lockers for L1_SECURITY_R21C_HERO.

Two banks (east and south walls of Security 03) with real vented doors,
recessed panels, three hinges per door, locks, handles, number plates,
interior shelves, brackets, clothes rods, hooks and boot trays.  All
assemblies are one joined mesh per bank; overlapping parts avoid any
coplanar face.
"""
import math
import random
import bpy
import bmesh
from mathutils import Vector, Matrix

import fm_ops_lib as L
import fm_r21c_lib as C


# --------------------------------------------------------------------------------------
# door
# --------------------------------------------------------------------------------------
def dented_panel(name, w, h, thick, center, mat, coll, dent_y, dent_z, depth=0.030,
                 radius=0.24, cuts=6):
    """Recessed door panel with a real pressed-in dent (subdivided shell)."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= thick
        v.co.y *= w
        v.co.z *= h
    bm.edges.ensure_lookup_table()
    bmesh.ops.subdivide_edges(bm, edges=list(bm.edges), cuts=cuts, use_grid_fill=True)
    dyc = dent_y - w * 0.5
    dzc = dent_z - h * 0.5
    for v in bm.verts:
        d = math.sqrt(((v.co.y - dyc) / radius) ** 2 +
                      ((v.co.z - dzc) / (radius * 0.75)) ** 2)
        if d < 1.0:
            f = (1.0 - d * d) ** 1.6
            if v.co.x < 0:
                v.co.x += depth * f
            else:
                v.co.x += depth * 0.45 * f
    me = bpy.data.meshes.new(name)
    L._finish_bm(bm, me, smooth=True, sharp_angle=42.0)
    L._box_uv(me)
    return L._link(name, me, coll, mat, center)


def locker_door(name, door_w, door_h, mat, coll, open_deg=0.0, dented=False,
                mirror=False, number=1, face_key="green", sag=0.0, rust=False):
    parts = []
    d = 0.028
    # outer frame: back 2 mm inside the carcass, front 26 mm proud
    parts.append(C.frame(name + "_Frame", door_w, door_h, door_w - 0.092,
                         door_h - 0.096, d, (-0.012, door_w * 0.5, door_h * 0.5),
                         mat[face_key], coll, bevel=0.0016, seg=2))
    # lower panel (recessed 8 mm behind the frame face)
    pw = door_w - 0.056
    ph = 1.145
    pz = 0.0475 + ph * 0.5
    if dented:
        parts.append(dented_panel(name + "_PanelDent", pw, ph, 0.011,
                                  (-0.0048, door_w * 0.5, 0.0475 + ph * 0.5),
                                  mat["green_dark"], coll,
                                  dent_y=pw * 0.52, dent_z=ph * 0.47,
                                  depth=0.034, radius=0.235, cuts=6))
        # chipped paint at the lower edge
        parts.append(C.hb(name + "_Chip0", (0.003, 0.075, 0.022),
                          (-0.0095, 0.26, 0.075), mat["rust"], coll, bevel=0.0004, seg=1))
        parts.append(C.hb(name + "_Chip1", (0.003, 0.045, 0.016),
                          (-0.0095, door_w * 0.68, 0.125), mat["rust"], coll,
                          bevel=0.0004, seg=1))
    else:
        parts.append(C.hb(name + "_Panel", (0.011, pw, ph),
                          (-0.0048, door_w * 0.5, 0.0475 + ph * 0.5),
                          mat["green_dark"], coll, bevel=0.0018, seg=2))
    # mid rail and top filler
    parts.append(C.hb(name + "_MidRail", (0.025, door_w - 0.046, 0.052),
                      (-0.0115, door_w * 0.5, 1.222), mat[face_key], coll,
                      bevel=0.0018, seg=2))
    parts.append(C.hb(name + "_TopFill", (0.025, door_w - 0.046, 0.030),
                      (-0.0115, door_w * 0.5, 1.758), mat[face_key], coll,
                      bevel=0.0015, seg=2))
    # louvre bank: real slats in front of a dark backing
    parts.append(C.hb(name + "_VentBack", (0.0035, door_w - 0.076, 0.520),
                      (-0.0025, door_w * 0.5, 1.500), mat["dark"], coll,
                      bevel=0.0007, seg=1))
    n_slats = 8
    z0, z1 = 1.258, 1.742
    step = (z1 - z0) / (n_slats - 1)
    for i in range(n_slats):
        parts.append(C.hb(name + f"_Louvre{i}", (0.0065, door_w - 0.078, 0.045),
                          (-0.0105, door_w * 0.5, z0 + i * step), mat[face_key], coll,
                          rot=(0, math.radians(32), 0), bevel=0.0012, seg=2))
    # lock escutcheon + cylinder + keyhole
    lock_y = door_w - 0.070
    parts.append(C.hb(name + "_Escutcheon", (0.009, 0.048, 0.155),
                      (-0.0245, lock_y, 1.075), mat["steel_bare"], coll,
                      bevel=0.0022, seg=3))
    parts.append(C.cy(name + "_LockRing", 0.0215, 0.009, (-0.0325, lock_y, 1.105),
                      mat["steel_bare"], coll, rot=(0, math.radians(90), 0),
                      segments=20, bevel=0.0016))
    parts.append(C.cy(name + "_LockBody", 0.0135, 0.016, (-0.040, lock_y, 1.105),
                      mat["steel_bare"], coll, rot=(0, math.radians(90), 0),
                      segments=16, bevel=0.0012))
    parts.append(C.hb(name + "_KeySlot", (0.004, 0.0055, 0.016),
                      (-0.049, lock_y, 1.105), mat["dark"], coll,
                      bevel=0.0005, seg=1))
    # latch bolt on the free edge
    parts.append(C.hb(name + "_Latch", (0.015, 0.020, 0.075),
                      (-0.012, door_w - 0.004, 1.075), mat["steel_bare"], coll,
                      bevel=0.0015, seg=2))
    # pull handle
    hx, hy = -0.031, door_w - 0.125
    parts.append(C.hb(name + "_HandlePlate", (0.009, 0.048, 0.225),
                      (-0.0245, hy, 0.935), mat[face_key], coll, bevel=0.002, seg=3))
    parts.append(C.hb(name + "_Grip", (0.019, 0.019, 0.170),
                      (-0.050, hy, 0.935), mat["steel_bare"], coll,
                      bevel=0.003, seg=3))
    for gz in (-0.070, 0.070):
        parts.append(C.hb(name + f"_GripPost{gz:+.3f}", (0.026, 0.014, 0.018),
                          (-0.038, hy, 0.935 + gz), mat["steel_bare"], coll,
                          bevel=0.002, seg=2))
    # number plate with a real number
    ly = door_w * 0.5
    lz = door_h - 0.092
    parts.append(C.hb(name + "_NumberHolder", (0.011, 0.082, 0.046),
                      (-0.0265, ly, lz), mat["dark"], coll, bevel=0.001, seg=2))
    parts.append(C.hb(name + "_NumberPlate", (0.004, 0.068, 0.035),
                      (-0.0335, ly, lz), mat["paper"], coll, bevel=0.0006, seg=1))
    parts.append(C.text(name + "_Number", str(number), 0.040,
                        (-0.0362, ly, lz), C.ROT_E, mat["dark"], coll, extrude=0.0008))
    # three hinges: moving leaf + middle knuckle (fixed half lives on the carcass)
    for hz in (0.245, 0.910, 1.575):
        parts.append(C.cy(name + f"_HingePin{hz:.3f}", 0.0085, 0.105,
                          (-0.014, 0.0, hz), mat["steel_bare"], coll,
                          segments=14, bevel=0.0009))
        parts.append(C.cy(name + f"_HingeKnuckle{hz:.3f}", 0.0115, 0.030,
                          (-0.014, 0.0, hz), mat["steel_bare"], coll,
                          segments=16, bevel=0.0012))
        parts.append(C.hb(name + f"_HingeLeaf{hz:.3f}", (0.006, 0.055, 0.072),
                          (-0.031, 0.029, hz), mat["steel_bare"], coll,
                          bevel=0.0016, seg=2))
        parts.append(C.hb(name + f"_HingeArm{hz:.3f}", (0.018, 0.026, 0.050),
                          (-0.020, 0.015, hz), mat["steel_bare"], coll,
                          bevel=0.0014, seg=2))
        for sy in (0.016, 0.044):
            for sz in (-0.022, 0.022):
                parts.append(C.screw(name + f"_HingeScrew{hz:.3f}{sy:.3f}{sz:+.3f}",
                        (-0.0345, sy, hz + sz), (-1, 0, 0), mat["steel_bare"], coll,
                        r=0.0033, socket_mat=mat["dark"]))
    # inside mirror on one open door
    if mirror:
        parts.append(C.hb(name + "_Mirror", (0.005, door_w - 0.11, 0.420),
                          (0.004, door_w * 0.5, 0.985), mat["aluminum"], coll,
                          bevel=0.0018, seg=2))
        for my in (0.085, door_w - 0.085):
            for mz in (0.795, 1.175):
                parts.append(C.screw(name + f"_MirrorScrew{my:.3f}{mz:.3f}",
                        (0.0075, my, mz), (1, 0, 0), mat["steel_bare"], coll,
                        r=0.0042, socket_mat=mat["dark"]))
    if rust:
        parts.append(C.hb(name + "_RustEdge", (0.004, door_w * 0.62, 0.014),
                          (-0.0275, door_w * 0.42, 0.021), mat["rust"], coll,
                          bevel=0.0004, seg=1))
    ob = C.join(parts, name, coll)
    return ob


# --------------------------------------------------------------------------------------
# fixed hinge halves + carcass
# --------------------------------------------------------------------------------------
def fixed_hinge(name, D, hinge_y, z, mat, coll):
    parts = []
    for dz in (-0.032, 0.032):
        parts.append(C.cy(name + f"_Sleeve{dz:+.3f}", 0.0132, 0.028,
                          (-D - 0.014, hinge_y, z + dz), mat["steel_bare"], coll,
                          segments=16, bevel=0.0012))
    parts.append(C.hb(name + "_Plate", (0.010, 0.036, 0.086),
                      (-D - 0.003, hinge_y - 0.020, z), mat["steel_bare"], coll,
                      bevel=0.0016, seg=2))
    parts.append(C.hb(name + "_Arm", (0.014, 0.016, 0.022),
                      (-D - 0.010, hinge_y - 0.020, z), mat["steel_bare"], coll,
                      bevel=0.0014, seg=2))
    for dz in (-0.025, 0.025):
        parts.append(C.screw(name + f"_Screw{dz:+.3f}", (-D - 0.008, hinge_y - 0.010, z + dz),
                (-1, 0, 0), mat["steel_bare"], coll, r=0.0032, socket_mat=mat["dark"]))
    return parts


def locker_bank(name, mat, coll, W=4.40, H=1.98, D=0.52, doors=8,
                open_angles=None, dented=None, mirror_doors=None, rust_doors=None,
                debug=False):
    open_angles = open_angles or {}
    dented = dented or set()
    mirror_doors = mirror_doors or set()
    rust_doors = rust_doors or set()
    rnd = random.Random(331)
    parts = []

    # feet, plinth, decks, carcass
    for i in range(6):
        yy = 0.16 + i * (W - 0.32) / 5.0
        parts.append(C.hb(f"{name}_Foot{i}", (0.07, 0.07, 0.018),
                          (-D + 0.10, yy, 0.009), mat["rubber"], coll,
                          bevel=0.004, seg=3))
    parts.append(C.hb(name + "_Plinth", (D - 0.075, W - 0.03, 0.078),
                      (-(D - 0.075) * 0.5 - 0.015, W * 0.5, 0.053),
                      mat["dark"], coll, bevel=0.004, seg=3))
    parts.append(C.hb(name + "_Bottom", (D - 0.012, W - 0.02, 0.026),
                      (-(D - 0.012) * 0.5, W * 0.5, 0.104),
                      mat["steel_dark"], coll, bevel=0.004, seg=3))
    parts.append(C.hb(name + "_Top", (D + 0.012, W + 0.008, 0.034),
                      (-(D + 0.012) * 0.5, W * 0.5, H - 0.017),
                      mat["steel_dark"], coll, bevel=0.005, seg=4))
    parts.append(C.hb(name + "_TopLip", (0.010, W + 0.008, 0.030),
                      (-D - 0.010, W * 0.5, H - 0.046), mat["steel_dark"], coll,
                      bevel=0.003, seg=3))
    # back panel 2 mm off the wall, sides and dividers overlap it
    parts.append(C.hb(name + "_Back", (0.016, W - 0.02, H - 0.135),
                      (-0.010, W * 0.5, 0.112 + (H - 0.135) * 0.5),
                      mat["steel_dark"], coll, bevel=0.003, seg=2))
    for i, yy in enumerate((0.014, W - 0.014)):
        parts.append(C.hb(f"{name}_Side{i}", (D, 0.020, H - 0.15),
                          (-D * 0.5, yy, 0.12 + (H - 0.15) * 0.5),
                          mat["steel_dark"], coll, bevel=0.003, seg=3))

    inner_w = W - 0.05
    dw = inner_w / doors
    dpos = [0.025 + i * dw for i in range(doors + 1)]
    for i in range(doors + 1):
        parts.append(C.hb(f"{name}_Div{i}", (D - 0.040, 0.018, H - 0.15),
                          (-(D - 0.040) * 0.5 - 0.010, dpos[i], 0.115 + (H - 0.15) * 0.5),
                          mat["steel_dark"], coll, bevel=0.003, seg=2))
    # front hinge posts (24 mm stile at the left edge of every compartment)
    for i in range(doors):
        parts.append(C.hb(f"{name}_Post{i}", (0.048, 0.024, H - 0.115),
                          (-D + 0.024, dpos[i] + 0.012, 0.105 + (H - 0.115) * 0.5),
                          mat["green"], coll, bevel=0.003, seg=3))
        for bz in (0.42, 1.55):
            parts.append(C.hb(f"{name}_Bumper{i}{bz:.2f}", (0.007, 0.016, 0.055),
                              (-D - 0.0025, dpos[i] + 0.022, bz), mat["rubber"], coll,
                              bevel=0.0015, seg=2))

    door_objs = []
    for i in range(doors):
        left = dpos[i] + 0.024
        right = dpos[i + 1] - 0.009
        dw_comp = right - left
        door_w = dw_comp - 0.006
        door_h = 1.820
        hinge_y = left
        # interior fit-out: shelf, brackets, rod, hooks, boot tray
        comp_y = (left + right) * 0.5
        parts.append(C.hb(f"{name}_Shelf{i}", (0.455, dw_comp - 0.002, 0.017),
                          (-0.2575, comp_y, 1.452), mat["galv"], coll,
                          bevel=0.002, seg=2))
        parts.append(C.hb(f"{name}_ShelfLip{i}", (0.012, dw_comp - 0.002, 0.024),
                          (-0.490, comp_y, 1.436), mat["galv"], coll,
                          bevel=0.0015, seg=2))
        for sy in (-1, 1):
            by = comp_y + sy * (dw_comp * 0.5 - 0.004)
            parts.append(C.hb(f"{name}_Brk{i}{sy}", (0.160, 0.012, 0.150),
                              (-0.395, by, 1.376), mat["steel_dark"], coll,
                              bevel=0.002, seg=2))
            parts.append(C.screw(f"{name}_BrkScrew{i}{sy}", (-0.395, by - sy * 0.007, 1.392),
                    (0, -sy, 0), mat["steel_bare"], coll, r=0.004, socket_mat=mat["dark"]))
        # clothes rod + mounts
        parts.append(C.cy(f"{name}_Rod{i}", 0.0085, dw_comp - 0.026,
                          (-0.290, comp_y, 1.660), mat["aluminum"], coll,
                          rot=(math.radians(90), 0, 0), segments=16, bevel=0.001))
        for sy in (-1, 1):
            ey = comp_y + sy * (dw_comp * 0.5 - 0.014)
            parts.append(C.cy(f"{name}_RodMount{i}{sy}", 0.016, 0.012,
                              (-0.290, ey, 1.660), mat["steel_bare"], coll,
                              rot=(math.radians(90), 0, 0), segments=14, bevel=0.0012))
            parts.append(C.hb(f"{name}_RodPlate{i}{sy}", (0.050, 0.020, 0.042),
                              (-0.290, ey, 1.660), mat["steel_bare"], coll,
                              bevel=0.0016, seg=2))
        # two coat hooks on the back
        for k, hy in enumerate((comp_y - dw_comp * 0.22, comp_y + dw_comp * 0.22)):
            parts.append(C.tube(f"{name}_Hook{i}{k}",
                                [(-0.020, hy, 1.300), (-0.070, hy, 1.305),
                                 (-0.078, hy, 1.318), (-0.078, hy, 1.338)],
                                0.0042, mat["steel_bare"], coll, sides=7))
            parts.append(C.hb(f"{name}_HookPlate{i}{k}", (0.006, 0.030, 0.030),
                              (-0.020, hy, 1.300), mat["steel_bare"], coll,
                              bevel=0.0012, seg=2))
        if i in (1, 4):
            parts.append(C.hb(f"{name}_BootTray{i}", (0.330, dw_comp * 0.62, 0.016),
                              (-0.315, comp_y, 0.124), mat["rubber"], coll,
                              bevel=0.003, seg=2))
            for sy in (-1, 1):
                parts.append(C.hb(f"{name}_BootLip{i}{sy}", (0.330, 0.014, 0.030),
                                  (-0.315, comp_y + sy * dw_comp * 0.31, 0.144),
                                  mat["rubber"], coll, bevel=0.002, seg=2))
        # fixed hinge halves on the front post
        for hz in (0.245, 0.910, 1.575):
            parts.extend(fixed_hinge(f"{name}_FixHinge{i}{hz:.3f}", D, hinge_y,
                                     0.105 + hz, mat, coll))
        # door
        door = locker_door(f"{name}_Door{i:02d}", door_w, door_h, mat, coll,
                           open_deg=open_angles.get(i, 0.0), dented=i in dented,
                           mirror=i in mirror_doors, number=i + 1,
                           face_key=("olive" if i == 2 else "green"),
                           rust=i in rust_doors)
        C.bake_world(door)
        ang = open_angles.get(i, 0.0)
        piv = Vector((-0.014, 0.0, 0.0))
        origin = Vector((-D, hinge_y, 0.105))
        m = (Matrix.Translation(origin) @ Matrix.Translation(piv) @
             Matrix.Rotation(math.radians(ang), 4, "Z") @ Matrix.Translation(-piv))
        if i == 6:
            m = m @ Matrix.Rotation(math.radians(2.2), 4, "Y")
        door.matrix_world = m
        door_objs.append(door)

    parts.extend(door_objs)
    if debug:
        return parts
    bank = C.join(parts, name, coll)
    return bank


# --------------------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------------------
def build(mat, coll):
    bank_a = locker_bank("R21C_LOCK_BankA", mat, coll,
                         open_angles={1: 26.0, 4: 68.0, 7: 12.0},
                         dented={3, 6}, mirror_doors={4}, rust_doors={2, 6})
    C.bake_world(bank_a)
    bank_b = locker_bank("R21C_LOCK_BankB", mat, coll,
                         open_angles={2: 46.0, 5: 14.0},
                         dented={0, 5}, mirror_doors={2}, rust_doors={0, 7})
    C.bake_world(bank_b)
    return bank_a, bank_b


def place_banks(banks):
    a, b = banks
    C.place(a, (-71.146, 13.40, 0.0015))
    C.place(b, (-80.60, 10.154, 0.0015), rot_z=-90.0)


if __name__ == "__main__":
    pass
