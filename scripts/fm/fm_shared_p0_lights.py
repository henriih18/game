"""
FRECUENCIA MUERTA - P0a LIGHTING masters.

Pivots:
  emergency wall  -> centre of the backplate on the wall plane (y=0), Z centred
  emergency ceil  -> ceiling plane, body hangs on -Z
  luminaire       -> ceiling plane, housing above +Z, diffuser at z=0
Lights are separate objects parented to the same root.
"""
import bpy
import bmesh
import math
import json
from mathutils import Vector, Matrix

from fm_shared_p0_lib import (ensure_tree, ensure_materials, make_root,
                              parent_to, box, cyl, cone, screw, bolt,
                              join_group, finalize_master, tri_count,
                              make_part, bm_box, bm_cyl, bm_prism_x,
                              clear_collection_tree)

M = ensure_materials()

PAINT = M["paint_door"]
GALV = M["galv"]
DARK = M["steel_dark"]
BARE = M["steel_bare"]
ALU = M["aluminum"]
RUB = M["rubber"]
GLASS = M["glass"]
LABEL = M["label"]
LENS = M["lens_red"]
LENS_OFF = M["lens_red_dead"]
CABLE = M["cable"]


# ---------------------------------------------------------------------------
# light nodes
# ---------------------------------------------------------------------------

def light_node(coll, name, kind, loc, energy, color, root,
               size=None, size_y=None, shape='RECTANGLE'):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = color
    if kind == 'POINT':
        ld.shadow_soft_size = 0.04
    if kind == 'AREA':
        ld.shape = shape
        ld.size = size or 1.0
        if shape == 'RECTANGLE':
            ld.size_y = size_y or 0.3
    ob = bpy.data.objects.new(name, ld)
    coll.objects.link(ob)
    ob.location = loc
    ob.parent = root
    ob.matrix_parent_inverse = Matrix.Identity(4)
    ob["fm_light_node"] = True
    return ob


# ---------------------------------------------------------------------------
# emergency wall
# ---------------------------------------------------------------------------

def build_emergency_wall(coll, name, loc=(0, 0, 1.5)):
    root = make_root(name + "_ROOT", coll)
    parts = []
    # backplate and gasket
    parts.append(box(coll, name + "_Backplate", 0.200, 0.024, 0.340,
                     (0, 0.012, 0), GALV, 0.003, 3))
    parts.append(box(coll, name + "_Gasket", 0.186, 0.004, 0.326,
                     (0, 0.024, 0), RUB, 0.0012, 2))
    # mounting strap and wall bolts
    parts.append(box(coll, name + "_Strap", 0.050, 0.010, 0.300,
                     (0, 0.007, 0), DARK, 0.0015, 3))
    for i, zz in enumerate((-0.140, 0.140)):
        parts += bolt(coll, "%s_WB%d" % (name, i), (0, -0.006, zz),
                      (0, -1, 0), r=0.0065, head=0.004, length=0.012)
    for i, (xx, zz) in enumerate(((-0.080, -0.120), (0.080, -0.120),
                                  (-0.080, 0.145), (0.080, 0.145))):
        parts += screw(coll, "%s_BPS%d" % (name, i), (xx, 0.026, zz),
                       (0, 1, 0), r=0.0045, mat=BARE, length=0.0016)

    # wedge housing (profile in YZ extruded along X)
    profile = [(0.026, -0.150), (0.145, -0.128), (0.145, 0.104),
               (0.108, 0.150), (0.026, 0.150)]
    housing = make_part(name + "_Housing", bm_prism_x(profile, 0.196, (0, 0, 0)),
                        PAINT, coll, 0.004, 3)
    parts.append(housing)
    # top cap and rear rib
    parts.append(box(coll, name + "_TopCap", 0.204, 0.044, 0.016,
                     (0, 0.106, 0.154), DARK, 0.0015, 3))

    # lens frame, lens, prism ribs, symbol
    parts.append(box(coll, name + "_LensBezel", 0.176, 0.014, 0.252,
                     (0, 0.149, 0.005), ALU, 0.003, 3))
    parts.append(box(coll, name + "_Lens", 0.142, 0.020, 0.214,
                     (0, 0.161, 0.005), LENS, 0.005, 4))
    for i in range(5):
        zz = -0.078 + i * 0.040
        parts.append(box(coll, "%s_Prism%d" % (name, i), 0.130, 0.008, 0.012,
                         (0, 0.171, zz), LENS, 0.002, 2))
    # white legend bar on the lens (single part, no coplanar overlaps)
    parts.append(box(coll, name + "_LegendBar", 0.014, 0.004, 0.130,
                     (0, 0.1745, 0.020), M["label"], 0.0012, 2))
    for i, (xx, zz) in enumerate(((-0.080, -0.120), (0.080, -0.120),
                                  (-0.080, 0.130), (0.080, 0.130))):
        parts += screw(coll, "%s_LNS%d" % (name, i), (xx, 0.156, zz),
                       (0, 1, 0), r=0.0034, mat=BARE, length=0.0014)

    # bottom louvre frame + slats
    parts.append(box(coll, name + "_GrilleFrame", 0.170, 0.100, 0.014,
                     (0, 0.075, -0.151), DARK, 0.0012, 3))
    for i in range(5):
        yy = 0.038 + i * 0.018
        parts.append(box(coll, "%s_Louvre%d" % (name, i), 0.150, 0.008, 0.008,
                         (0, yy, -0.158), GALV, 0.0008, 2))
    for i, (xx, yy) in enumerate(((-0.075, 0.035), (0.075, 0.035),
                                  (-0.075, 0.115), (0.075, 0.115))):
        parts += screw(coll, "%s_GRS%d" % (name, i), (xx, yy, -0.158),
                       (0, 0, -1), r=0.003, mat=BARE, length=0.0012)

    # conduit entry at the top, locknut, bushing and cable gland
    parts.append(box(coll, name + "_JunctionBox", 0.070, 0.055, 0.045,
                     (0.055, 0.075, 0.172), DARK, 0.0018, 3))
    parts.append(cyl(coll, name + "_Conduit", 0.012, 0.110,
                     (0.055, 0.075, 0.245), GALV, 'Z', 16, 0.0008, 2))
    parts.append(cyl(coll, name + "_Locknut", 0.019, 0.012,
                     (0.055, 0.075, 0.190), BARE, 'Z', 6, 0.0008, 2))
    parts.append(cyl(coll, name + "_Bushing", 0.016, 0.014,
                     (0.055, 0.075, 0.302), RUB, 'Z', 12, 0.001, 2))
    parts.append(cyl(coll, name + "_Cable", 0.006, 0.060,
                     (0.055, 0.075, 0.290), CABLE, 'Z', 8, 0.0004, 1))
    for i in range(2):
        parts += screw(coll, "%s_JB%d" % (name, i),
                       (0.035, 0.104, 0.175 + i * 0.015), (0, 1, 0),
                       r=0.0032, mat=BARE, length=0.0012)

    # test button and charge LED on the lower bezel
    parts.append(cyl(coll, name + "_TestButton", 0.010, 0.012,
                     (0.000, 0.155, -0.118), M["plastic"], 'Y', 16,
                     0.001, 2))
    parts.append(cyl(coll, name + "_ChargeLED", 0.004, 0.006,
                     (-0.060, 0.155, -0.118), M["diffuser_on"], 'Y', 10,
                     0.0004, 1))

    ob = join_group(coll, name, parts)
    parent_to(ob, root)
    light_node(coll, "LGT_" + name, 'POINT', (0, 0.180, 0.0), 4.0,
               (1.0, 0.03, 0.01), root)
    finalize_master(root, coll, [ob], loc, {
        "fm_class": "LIGHT", "fm_subtype": "emergency_wall",
        "fm_dims": "0.20 x 0.18 x 0.34 m (housing)",
        "fm_pivot": "backplate centre on wall plane y=0",
        "fm_light": "LGT_%s point 4 W red" % name,
    })
    return root


def duplicate_rotated(coll, src_root, new_name, loc, rot_z=math.pi):
    """Linked duplicate of a master hierarchy (mesh data shared)."""
    new_root = make_root(new_name + "_ROOT", coll)
    new_root.location = loc
    new_root.rotation_euler = (0, 0, rot_z)
    for ob in [o for o in bpy.data.objects if o.parent == src_root]:
        nb = ob.copy()
        nb.data = ob.data
        coll.objects.link(nb)
        nb.parent = new_root
        nb.matrix_parent_inverse = Matrix.Identity(4)
        nb.location = ob.location.copy()
        nb.rotation_euler = ob.rotation_euler.copy()
    return new_root


# ---------------------------------------------------------------------------
# emergency ceiling
# ---------------------------------------------------------------------------

def build_emergency_ceiling(coll, name, loc=(0, 0, 3.0)):
    root = make_root(name + "_ROOT", coll)
    parts = []
    # canopy on the ceiling plane
    parts.append(box(coll, name + "_Canopy", 0.300, 0.300, 0.040,
                     (0, 0, -0.020), GALV, 0.003, 3))
    for i, (xx, yy) in enumerate(((-0.120, -0.120), (0.120, -0.120),
                                  (-0.120, 0.120), (0.120, 0.120))):
        parts += screw(coll, "%s_CNS%d" % (name, i), (xx, yy, -0.040),
                       (0, 0, -1), r=0.0045, mat=BARE, length=0.0016)
    # stem and body
    parts.append(cyl(coll, name + "_Stem", 0.035, 0.060,
                     (0, 0, -0.065), DARK, 'Z', 16, 0.0015, 3))
    parts.append(box(coll, name + "_Body", 0.300, 0.290, 0.105,
                     (0, 0, -0.140), PAINT, 0.004, 3))
    # body ribs / vents
    for sy in (-1.0, 1.0):
        for i, xx in enumerate((-0.090, 0.0, 0.090)):
            parts.append(box(coll, "%s_Vent%d_%d" % (name, 0 if sy < 0 else 1, i),
                             0.055, 0.006, 0.022,
                             (xx, sy * 0.146, -0.155), DARK, 0.0008, 2))
    # bottom plate with two red heads
    parts.append(box(coll, name + "_BottomPlate", 0.270, 0.260, 0.018,
                     (0, 0, -0.200), GALV, 0.0015, 3))
    for i, xx in enumerate((-0.066, 0.066)):
        parts.append(box(coll, "%s_LensFrame%d" % (name, i), 0.112, 0.150, 0.014,
                         (xx, 0, -0.212), ALU, 0.0015, 3))
        parts.append(box(coll, "%s_Lens%d" % (name, i), 0.094, 0.132, 0.020,
                         (xx, 0, -0.222), LENS, 0.004, 4))
        for j in range(3):
            parts.append(box(coll, "%s_Prism%d_%d" % (name, i, j),
                             0.086, 0.012, 0.008,
                             (xx, -0.044 + j * 0.044, -0.227), LENS,
                             0.0012, 2))
        for j, (sx, sy) in enumerate(((-0.048, -0.065), (0.048, -0.065),
                                      (-0.048, 0.065), (0.048, 0.065))):
            parts += screw(coll, "%s_LS%d_%d" % (name, i, j),
                           (xx + sx, sy, -0.219), (0, 0, -1),
                           r=0.003, mat=BARE, length=0.0012)
    # test button / LED on the bottom plate
    parts.append(cyl(coll, name + "_TestButton", 0.010, 0.011,
                     (0, 0, -0.207), M["plastic"], 'Z', 16, 0.001, 2))
    parts.append(cyl(coll, name + "_ChargeLED", 0.004, 0.006,
                     (0, 0.085, -0.207), M["diffuser_on"], 'Z', 10,
                     0.0004, 1))
    # side conduit entry on the body (visible, fully attached)
    parts.append(cyl(coll, name + "_Locknut", 0.019, 0.012,
                     (0.154, 0, -0.140), BARE, 'X', 6, 0.0008, 2))
    parts.append(cyl(coll, name + "_Conduit", 0.012, 0.100,
                     (0.206, 0, -0.140), GALV, 'X', 16, 0.0008, 2))
    parts.append(cyl(coll, name + "_Bushing", 0.016, 0.014,
                     (0.260, 0, -0.140), RUB, 'X', 12, 0.001, 2))
    parts.append(cyl(coll, name + "_Cable", 0.006, 0.060,
                     (0.290, 0, -0.140), CABLE, 'X', 8, 0.0004, 1))

    ob = join_group(coll, name, parts)
    parent_to(ob, root)
    light_node(coll, "LGT_" + name, 'POINT', (0, 0, -0.240), 5.0,
               (1.0, 0.03, 0.01), root)
    finalize_master(root, coll, [ob], loc, {
        "fm_class": "LIGHT", "fm_subtype": "emergency_ceiling",
        "fm_dims": "0.30 x 0.30 x 0.24 m below ceiling",
        "fm_pivot": "ceiling plane z=0; body hangs -Z",
        "fm_light": "LGT_%s point 5 W red" % name,
    })
    return root


# ---------------------------------------------------------------------------
# 1.5 m modular ceiling luminaire
# ---------------------------------------------------------------------------

def build_luminaire(coll, name, on=True, loc=(0, 0, 1.0)):
    root = make_root(name + "_ROOT", coll)
    parts = []
    # recessed housing above the ceiling plane
    parts.append(box(coll, name + "_Housing", 1.500, 0.300, 0.090,
                     (0, 0, 0.060), GALV, 0.003, 3))
    # folded frame lip around the aperture
    parts.append(box(coll, name + "_FrameT", 1.560, 0.030, 0.022,
                     (0, -0.160, 0.006), ALU, 0.0018, 3))
    parts.append(box(coll, name + "_FrameB", 1.560, 0.030, 0.022,
                     (0, 0.160, 0.006), ALU, 0.0018, 3))
    parts.append(box(coll, name + "_FrameL", 0.030, 0.320, 0.022,
                     (-0.755, 0, 0.004), ALU, 0.0018, 3))
    parts.append(box(coll, name + "_FrameR", 0.030, 0.320, 0.022,
                     (0.755, 0, 0.004), ALU, 0.0018, 3))
    # diffuser (recessed 6 mm above the lip)
    parts.append(box(coll, name + "_Diffuser", 1.456, 0.284, 0.012,
                     (0, 0, 0.016), M["diffuser_on" if on else "diffuser_off"],
                     0.002, 2))
    # prismatic ribs on the underside
    for i in range(7):
        yy = -0.120 + i * 0.040
        parts.append(box(coll, "%s_Prism%d" % (name, i), 1.430, 0.010, 0.004,
                         (0, yy, 0.009),
                         M["diffuser_on" if on else "diffuser_off"],
                         0.0008, 2))
    # end caps and side vents
    for i, xx in enumerate((-0.745, 0.745)):
        parts.append(box(coll, "%s_EndCap%d" % (name, i), 0.016, 0.310, 0.100,
                         (xx, 0, 0.060), DARK, 0.0015, 3))
    for i in range(5):
        xx = -0.50 + i * 0.25
        parts.append(box(coll, "%s_VentA%d" % (name, i), 0.120, 0.006, 0.040,
                         (xx, 0.154, 0.075), DARK, 0.001, 2))
        parts.append(box(coll, "%s_VentB%d" % (name, i), 0.120, 0.006, 0.040,
                         (xx, -0.154, 0.075), DARK, 0.001, 2))
    # retention clips
    for i, xx in enumerate((-0.700, -0.350, 0.350, 0.700)):
        for sy in (-1, 1):
            parts.append(box(coll, "%s_Clip%d_%d" % (name, i, 0 if sy < 0 else 1),
                             0.040, 0.026, 0.045,
                             (xx, sy * 0.170, -0.004), BARE, 0.004, 3))
            parts += screw(coll, "%s_CLS%d_%d" % (name, i, 0 if sy < 0 else 1),
                           (xx, sy * 0.170, -0.0265), (0, 0, -1),
                           r=0.003, mat=BARE, length=0.0012)
    # terminal box, cable gland and flexible cable
    parts.append(box(coll, name + "_TerminalBox", 0.140, 0.090, 0.055,
                     (0.600, 0.090, 0.120), DARK, 0.002, 3))
    parts.append(cyl(coll, name + "_Gland", 0.014, 0.030,
                     (0.600, 0.090, 0.155), BARE, 'Z', 12, 0.0008, 2))
    parts.append(cyl(coll, name + "_CableA", 0.008, 0.120,
                     (0.600, 0.090, 0.225), CABLE, 'Z', 8, 0.0004, 1))
    parts.append(cyl(coll, name + "_CableB", 0.008, 0.100,
                     (0.545, 0.090, 0.280), CABLE, 'X', 8, 0.0004, 1))
    parts.append(cyl(coll, name + "_CableAnchor", 0.020, 0.010,
                     (0.490, 0.090, 0.280), BARE, 'X', 12, 0.0006, 2))
    # safety cable and anchor

    # label
    parts.append(box(coll, name + "_Label", 0.080, 0.004, 0.030,
                     (0.250, 0.177, 0.006), LABEL, 0.0004, 2))
    for i, xx in enumerate((0.220, 0.280)):
        parts += screw(coll, "%s_LS%d" % (name, i), (xx, 0.179, 0.006),
                       (0, 1, 0), r=0.0026, mat=BARE, length=0.0012)

    ob = join_group(coll, name, parts)
    parent_to(ob, root)
    if on:
        light_node(coll, "LGT_" + name, 'AREA', (0, 0, -0.010), 38.0,
                   (1.0, 0.88, 0.70), root, size=1.40, size_y=0.26,
                   shape='RECTANGLE')
    finalize_master(root, coll, [ob], loc, {
        "fm_class": "LIGHT", "fm_subtype": "ceiling_troffer_1500_%s" % ("on" if on else "off"),
        "fm_dims": "1.54 x 0.34 x 0.11 m",
        "fm_pivot": "ceiling plane z=0; housing above, diffuser at z=0.01",
        "fm_light": ("LGT_%s area 38 W warm" % name) if on else "none (dead variant)",
    })
    return root


def build_all():
    if bpy.data.collections.get("LIGHTING"):
        clear_collection_tree("LIGHTING")
    T = ensure_tree()
    coll = bpy.data.collections["LIGHTING"]
    out = []
    out.append(build_emergency_wall(coll, "SM_SH_EMERGENCY_WALL_E",
                                    loc=(0, 0, 1.55)))
    nroot = duplicate_rotated(coll, out[0], "SM_SH_EMERGENCY_WALL_N",
                              (0.65, 0, 1.55), math.pi)
    nroot["fm_asset"] = nroot.name
    nroot["fm_generation"] = "VERIFIED_P0A"
    nroot["fm_class"] = "LIGHT"
    nroot["fm_subtype"] = "emergency_wall_rotated_variant"
    nroot["fm_note"] = "linked mesh duplicate of SM_SH_EMERGENCY_WALL_E, rotated 180 deg"
    out.append(nroot)
    out.append(build_emergency_ceiling(coll, "SM_SH_EMERGENCY_CEILING",
                                       loc=(2.2, 0, 3.0)))
    out.append(build_luminaire(coll, "SM_SH_LUMINAIRE_1500_ON", True,
                               loc=(4.2, 0, 1.0)))
    out.append(build_luminaire(coll, "SM_SH_LUMINAIRE_1500_OFF", False,
                               loc=(6.5, 0, 1.0)))
    for r in out:
        meshes = [o for o in bpy.data.objects if o.parent == r and o.type == 'MESH']
        lights = [o for o in bpy.data.objects if o.parent == r and o.type == 'LIGHT']
        print("MASTER", r.name, "loc", tuple(round(v, 2) for v in r.location),
              "meshes", len(meshes), "tris", sum(tri_count(o) for o in meshes),
              "lights", len(lights))
    return out


if __name__ == "__main__":
    build_all()
