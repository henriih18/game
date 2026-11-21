"""Server/UPS rack, column radio dock and emergency fixtures for the operations centre."""
import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

import fm_ops_lib as L


RACK_X = -78.00
RACK_Y = 35.16
WALL_Y = 35.845
RACK_Z0 = 0.0
RACK_W = 0.80
RACK_D = 0.85
RACK_H = 2.00


def _server_unit(prefix, z, h, mat, coll, pulled=0.0, live="green"):
    yfront = RACK_Y - RACK_D * 0.5 - 0.006 - pulled
    parts = []
    parts.append(L.box(prefix + "_Body", (0.720, 0.540, h), (RACK_X, RACK_Y - pulled, z),
                       mat["M_HERO_Steel_Dark"], coll, bevel=0.004, seg=2))
    parts.append(L.box(prefix + "_Face", (0.700, 0.014, h * 0.90), (RACK_X, yfront, z),
                       mat["olive_dark"], coll, bevel=0.003, seg=2))
    # vent slots, sunk into the front face
    n = max(3, int(h / 0.012))
    for i in range(n):
        parts.append(L.box(f"{prefix}_Vent{i}", (0.300, 0.008, 0.004),
                           (RACK_X - 0.150, yfront - 0.008, z - h * 0.35 + i * 0.010),
                           mat["grille"], coll, bevel=0.0005, seg=1))
    # handles, embedded into the face
    for sx in (-1, 1):
        parts.append(L.box(f"{prefix}_Handle{sx}", (0.022, 0.020, h * 0.45),
                           (RACK_X + sx * 0.305, yfront - 0.008, z), mat["M_HERO_Aluminum"],
                           coll, bevel=0.003, seg=2))
    # LEDs, embedded into the face
    parts.append(L.box(prefix + "_LED0", (0.006, 0.008, 0.006),
                       (RACK_X + 0.220, yfront - 0.006, z + h * 0.20),
                       mat["led_green" if live == "green" else "led_blue"], coll,
                       bevel=0.0, seg=1))
    parts.append(L.box(prefix + "_LED1", (0.006, 0.008, 0.006),
                       (RACK_X + 0.245, yfront - 0.006, z + h * 0.20),
                       mat["M_HERO_LED_Amber"], coll, bevel=0.0, seg=1))
    # label plate, embedded into the face
    parts.append(L.box(prefix + "_LabelPlate", (0.110, 0.008, 0.026),
                       (RACK_X + 0.100, yfront - 0.006, z + h * 0.20),
                       mat["label"], coll, bevel=0.001, seg=1))
    return parts


def build_rack(mat, coll):
    objs = []
    frame = []
    # posts
    for sx in (-1, 1):
        for sy in (-1, 1):
            frame.append(L.box(f"R21A_RACK_Post{sx}{sy}", (0.045, 0.045, RACK_H),
                               (RACK_X + sx * 0.374, RACK_Y + sy * 0.400, RACK_H * 0.5 + 0.02),
                               mat["olive"], coll, bevel=0.005, seg=3))
    frame.append(L.box("R21A_RACK_Top", (0.800, 0.850, 0.050), (RACK_X, RACK_Y, 1.985),
                       mat["olive"], coll, bevel=0.006, seg=3))
    frame.append(L.box("R21A_RACK_Bottom", (0.800, 0.850, 0.070), (RACK_X, RACK_Y, 0.085),
                       mat["olive"], coll, bevel=0.006, seg=3))
    # internal mounting rails (front and rear) - all 19" units bolt to these
    for sx in (-1, 1):
        for sy in (-1, 1):
            frame.append(L.box(f"R21A_RACK_Rail{sx}{sy}", (0.026, 0.026, 1.720),
                               (RACK_X + sx * 0.355, RACK_Y + sy * 0.180, 0.960),
                               mat["M_HERO_Steel_Dark"], coll, bevel=0.002, seg=2))
    frame.append(L.box("R21A_RACK_RearPanel", (0.780, 0.012, 1.900),
                       (RACK_X, RACK_Y + 0.420, 1.010), mat["olive_dark"], coll,
                       bevel=0.003, seg=2))
    # side panels with vent fields
    for sx in (-1, 1):
        side_x = RACK_X + sx * 0.398
        frame.append(L.box(f"R21A_RACK_Side{sx}", (0.014, 0.800, 1.780), (side_x, RACK_Y, 1.040),
                           mat["olive"], coll, bevel=0.003, seg=2))
        for row in range(4):
            z = 0.300 + row * 0.400
            frame.append(L.box(f"R21A_RACK_SideVentFrame{sx}{row}", (0.010, 0.420, 0.210),
                               (side_x + sx * 0.010, RACK_Y, z), mat["olive_dark"], coll,
                               bevel=0.002, seg=2))
            for i in range(9):
                frame.append(L.box(f"R21A_RACK_SideVentSlat{sx}{row}{i}", (0.008, 0.360, 0.007),
                                   (side_x + sx * 0.014, RACK_Y, z - 0.078 + i * 0.019),
                                   mat["grille"], coll, bevel=0.0005, seg=1))
    # feet
    for sx in (-1, 1):
        for sy in (-1, 1):
            frame.append(L.cyl(f"R21A_RACK_Foot{sx}{sy}", 0.032, 0.035,
                               (RACK_X + sx * 0.330, RACK_Y + sy * 0.350, 0.019),
                               mat["M_HERO_Steel_Dark"], coll, segments=16, bevel=0.002))
            frame.append(L.cyl(f"R21A_RACK_FootPad{sx}{sy}", 0.040, 0.010,
                               (RACK_X + sx * 0.330, RACK_Y + sy * 0.350, 0.005),
                               mat["M_HERO_Rubber"], coll, segments=20, bevel=0.002))
    # top fan grilles
    for i, x in enumerate((-0.200, 0.200)):
        frame.append(L.cyl(f"R21A_RACK_FanRing{i}", 0.120, 0.014,
                           (RACK_X + x, RACK_Y + 0.080, 2.014), mat["M_HERO_Steel_Bare"],
                           coll, segments=28, bevel=0.002))
        frame.append(L.cyl(f"R21A_RACK_FanHub{i}", 0.030, 0.014,
                           (RACK_X + x, RACK_Y + 0.080, 2.016), mat["M_HERO_Steel_Dark"],
                           coll, segments=16, bevel=0.002))
        for k in range(3):
            a = math.radians(k * 60)
            frame.append(L.box(f"R21A_RACK_FanSpoke{i}{k}", (0.090, 0.010, 0.004),
                               (RACK_X + x + math.cos(a) * 0.060,
                                RACK_Y + 0.080 + math.sin(a) * 0.060, 2.016),
                               mat["M_HERO_Steel_Dark"], coll, rot=(0, 0, a), bevel=0.0, seg=1))
    # rear cable entry and door lock plate
    frame.append(L.box("R21A_RACK_CableEntry", (0.250, 0.060, 0.140), (RACK_X + 0.120, RACK_Y + 0.380, 1.955),
                       mat["M_HERO_Steel_Dark"], coll, bevel=0.004, seg=2))
    frame.append(L.box("R21A_RACK_RearVent", (0.520, 0.014, 1.300), (RACK_X, RACK_Y + 0.412, 1.000),
                       mat["olive"], coll, bevel=0.003, seg=2))
    objs.append(L.join(frame, "R21A_RACK_Frame", coll))

    # interior: UPS, patch panel, server units
    interior = []
    # UPS
    interior.append(L.box("R21A_RACK_UPS_Body", (0.720, 0.560, 0.300), (RACK_X, RACK_Y, 0.275),
                          mat["M_HERO_Steel_Dark"], coll, bevel=0.005, seg=2))
    interior.append(L.box("R21A_RACK_UPS_Face", (0.700, 0.016, 0.270), (RACK_X, RACK_Y - 0.425, 0.275),
                          mat["olive_dark"], coll, bevel=0.003, seg=2))
    interior.append(L.box("R21A_RACK_UPS_LCD", (0.190, 0.008, 0.090), (RACK_X - 0.110, RACK_Y - 0.432, 0.305),
                          mat["screen_glow_dim"], coll, bevel=0.0, seg=1, smooth=False))
    for i in range(4):
        interior.append(L.box(f"R21A_RACK_UPS_Btn{i}", (0.030, 0.010, 0.028),
                              (RACK_X + 0.080 + i * 0.045, RACK_Y - 0.431, 0.300),
                              mat["M_HERO_Plastic"], coll, bevel=0.002, seg=2))
    for i in range(5):
        interior.append(L.box(f"R21A_RACK_UPS_Vent{i}", (0.240, 0.008, 0.006),
                              (RACK_X - 0.060, RACK_Y - 0.431, 0.175 + i * 0.014),
                              mat["grille"], coll, bevel=0.0005, seg=1))
    interior.append(L.box("R21A_RACK_UPS_LED", (0.008, 0.006, 0.008), (RACK_X + 0.250, RACK_Y - 0.436, 0.340),
                          mat["led_green"], coll, bevel=0.0, seg=1))
    interior.append(L.box("R21A_RACK_UPS_LabelPlate", (0.120, 0.008, 0.032), (RACK_X - 0.300, RACK_Y - 0.430, 0.220),
                          mat["label"], coll, bevel=0.0015, seg=2))
    # patch panel
    interior.append(L.box("R21A_RACK_Patch_Body", (0.720, 0.300, 0.080), (RACK_X, RACK_Y - 0.120, 1.760),
                          mat["M_HERO_Steel_Dark"], coll, bevel=0.004, seg=2))
    interior.append(L.box("R21A_RACK_Patch_Face", (0.700, 0.014, 0.070), (RACK_X, RACK_Y - 0.278, 1.760),
                          mat["olive_dark"], coll, bevel=0.002, seg=2))
    for row in range(2):
        for i in range(12):
            interior.append(L.box(f"R21A_RACK_Port{row}{i}", (0.020, 0.012, 0.018),
                                  (RACK_X - 0.280 + i * 0.050, RACK_Y - 0.290, 1.778 - row * 0.030),
                                  mat["M_HERO_Plastic"], coll, bevel=0.001, seg=1))
    # servers: 1U/2U mix, one unit pulled out
    unit_zs = [(0.520, 0.085, 0.0, "green"), (0.615, 0.085, 0.0, "blue"),
               (0.710, 0.085, 0.0, "green"), (0.805, 0.085, 0.035, "green"),
               (0.900, 0.085, 0.0, "blue"), (0.995, 0.085, 0.0, "green"),
               (1.135, 0.170, 0.0, "green"), (1.320, 0.085, 0.0, "green"),
               (1.415, 0.085, 0.0, "blue"), (1.510, 0.085, 0.0, "green"),
               (1.605, 0.085, 0.0, "green")]
    for i, (z, h, pulled, live) in enumerate(unit_zs):
        interior.extend(_server_unit(f"R21A_RACK_SRV{i:02d}", z, h, mat, coll, pulled=pulled, live=live))
        interior.append(L.text_mesh(f"R21A_RACK_SRVLbl{i:02d}", f"SRV-{i + 1:02d}", 0.020,
                                    (RACK_X + 0.100, RACK_Y - 0.4415 - pulled, z + h * 0.20),
                                    (math.radians(90), 0, 0), mat["M_HERO_Paint_Dark"], coll,
                                    extrude=0.0006))
    objs.append(L.join(interior, "R21A_RACK_Interior", coll))

    # perforated front door (built around hinge at x = RACK_X + 0.38)
    hinge_x = RACK_X + 0.380
    door = []
    door_y = RACK_Y - RACK_D * 0.5 - 0.028
    # outer frame
    door.append(L.box("R21A_RACK_DoorT", (0.680, 0.030, 0.050), (hinge_x - 0.380, door_y, 1.900),
                      mat["olive"], coll, bevel=0.004, seg=2))
    door.append(L.box("R21A_RACK_DoorB", (0.680, 0.030, 0.050), (hinge_x - 0.380, door_y, 0.260),
                      mat["olive"], coll, bevel=0.004, seg=2))
    door.append(L.box("R21A_RACK_DoorL", (0.040, 0.030, 1.700), (hinge_x - 0.740, door_y, 1.080),
                      mat["olive"], coll, bevel=0.004, seg=2))
    door.append(L.box("R21A_RACK_DoorR", (0.040, 0.030, 1.700), (hinge_x - 0.020, door_y, 1.080),
                      mat["olive"], coll, bevel=0.004, seg=2))
    # perforated field: horizontal slats + vertical bars
    for i in range(43):
        z = 0.315 + i * 0.037
        door.append(L.box(f"R21A_RACK_DoorSlat{i}", (0.700, 0.010, 0.012),
                          (hinge_x - 0.380, door_y - 0.007, z), mat["M_HERO_Steel_Dark"], coll,
                          bevel=0.0015, seg=1))

    # reinforcing rim and bent bottom corner
    door.append(L.box("R21A_RACK_DoorRim", (0.700, 0.040, 0.020), (hinge_x - 0.380, door_y - 0.012, 1.585),
                      mat["M_HERO_Galvanized"], coll, bevel=0.002, seg=2))
    door.append(L.box("R21A_RACK_DoorBent", (0.150, 0.016, 0.090), (hinge_x - 0.620, door_y - 0.016, 0.285),
                      mat["M_HERO_Steel_Bare"], coll, rot=(math.radians(18), 0, 0), bevel=0.003, seg=2))
    door.append(L.box("R21A_RACK_HandleBar", (0.030, 0.030, 0.260), (hinge_x - 0.685, door_y - 0.055, 1.080),
                      mat["M_HERO_Aluminum"], coll, bevel=0.005, seg=3))
    for z in (0.980, 1.180):
        door.append(L.box(f"R21A_RACK_HandlePost{z}", (0.040, 0.045, 0.028), (hinge_x - 0.665, door_y - 0.035, z),
                          mat["M_HERO_Steel_Dark"], coll, bevel=0.003, seg=2))
    door.append(L.box("R21A_RACK_Latch", (0.055, 0.045, 0.080), (hinge_x - 0.700, door_y + 0.005, 0.930),
                      mat["M_HERO_Steel_Dark"], coll, bevel=0.004, seg=3))
    door.append(L.cyl("R21A_RACK_Lock", 0.018, 0.012, (hinge_x - 0.700, door_y - 0.022, 0.930),
                      mat["M_HERO_Steel_Bare"], coll, rot=(math.radians(90), 0, 0), segments=16,
                      bevel=0.001))
    door_ob = L.join(door, "R21A_RACK_Door", coll)
    # open the door 17 degrees around its hinge
    hp = Vector((hinge_x, door_y, 0))
    M = (Matrix.Translation(hp) @ Matrix.Rotation(math.radians(17), 4, "Z") @
         Matrix.Translation(-hp))
    L.transform_objects([door_ob], M)
    L.weighted_normal(door_ob)
    objs.append(door_ob)

    # hinges (fixed to frame)
    hinges = []
    for z in (0.430, 1.080, 1.730):
        hinges.append(L.cyl(f"R21A_RACK_Hinge{z}", 0.018, 0.110, (hinge_x, door_y + 0.005, z),
                            mat["M_HERO_Steel_Bare"], coll, segments=18, bevel=0.002))
        hinges.append(L.box(f"R21A_RACK_HingePlate{z}", (0.050, 0.040, 0.120), (hinge_x + 0.030, door_y + 0.005, z),
                            mat["M_HERO_Steel_Dark"], coll, bevel=0.003, seg=2))
    objs.append(L.join(hinges, "R21A_RACK_Hinges", coll))

    # rack cabling
    cables = []
    # patch cables from patch panel to servers
    for i in range(8):
        z = 0.560 + i * 0.120
        p0 = (RACK_X - 0.250 + i * 0.075, RACK_Y - 0.275, 1.760)
        p1 = (RACK_X - 0.240 + i * 0.060, RACK_Y - 0.420, z)
        cables.append(L.cable(f"R21A_RACK_PatchCable{i}", p0, p1, 0.10, 0.0045,
                              mat["cable_blue"], coll, n=10, sides=6, wiggle=0.02, seed=i))
    # top power/data bundle to tray
    for k in range(3):
        p0 = (RACK_X - 0.150 + k * 0.120, RACK_Y + 0.300, 1.980)
        p1 = (RACK_X - 0.150 + k * 0.120, WALL_Y - 0.320, 3.620)
        cables.append(L.cable(f"R21A_RACK_TopCable{k}", p0, p1, 0.20, 0.008,
                              mat["M_HERO_Rubber"] if k == 0 else mat["cable_blue"], coll,
                              n=14, sides=7, wiggle=0.02, seed=70 + k))
    # loose cable kicked out from the rack base
    cables.append(L.tube("R21A_RACK_LooseCable",
                         [(RACK_X - 0.388, RACK_Y - 0.350, 0.400),
                          (RACK_X - 0.600, RACK_Y - 0.500, 0.040),
                          (RACK_X - 0.950, RACK_Y - 0.680, 0.010),
                          (RACK_X - 1.350, RACK_Y - 0.780, 0.010),
                          (RACK_X - 1.700, RACK_Y - 0.900, 0.010)],
                         0.010, mat["M_HERO_Rubber"], coll, sides=8))
    objs.append(L.join(cables, "R21A_RACK_Cables", coll))

    # rack label on the front top rail (visible from the room)
    lab = L.box("R21A_RACK_NamePlate", (0.420, 0.008, 0.110), (RACK_X, RACK_Y - 0.429, 1.960),
                mat["M_HERO_Paint_Dark"], coll, bevel=0.002, seg=2)
    objs.append(lab)
    return objs


def build_wall_panel(mat, coll):
    """Breaker / distribution panel on the north wall between CCTV and the rack."""
    x = -81.35
    y = 35.850
    parts = []
    parts.append(L.box("R21A_FIX_Breaker_Body", (0.960, 0.160, 1.220), (x, y - 0.080, 1.900),
                       mat["olive"], coll, bevel=0.008, seg=3))
    parts.append(L.box("R21A_FIX_Breaker_Door", (0.900, 0.026, 1.160), (x, y - 0.173, 1.900),
                       mat["olive_dark"], coll, bevel=0.005, seg=3))
    parts.append(L.box("R21A_FIX_Breaker_Frame", (0.930, 0.014, 1.190), (x, y - 0.166, 1.900),
                       mat["M_HERO_Steel_Dark"], coll, bevel=0.003, seg=2))
    # hinges and latch
    for z in (1.400, 1.900, 2.400):
        parts.append(L.cyl(f"R21A_FIX_Breaker_Hinge{z}", 0.016, 0.070, (x - 0.440, y - 0.185, z),
                           mat["M_HERO_Steel_Bare"], coll, segments=14, bevel=0.002))
    parts.append(L.box("R21A_FIX_Breaker_Latch", (0.050, 0.045, 0.090), (x + 0.420, y - 0.200, 1.900),
                       mat["M_HERO_Steel_Dark"], coll, bevel=0.004, seg=2))
    parts.append(L.cyl("R21A_FIX_Breaker_Lock", 0.016, 0.014, (x + 0.420, y - 0.228, 1.900),
                       mat["M_HERO_Steel_Bare"], coll, rot=(math.radians(90), 0, 0),
                       segments=14, bevel=0.001))
    # inset breaker window with rows of switches
    parts.append(L.box("R21A_FIX_Breaker_Window", (0.620, 0.020, 0.760), (x - 0.040, y - 0.195, 1.980),
                       mat["M_HERO_Steel_Dark"], coll, bevel=0.003, seg=2))
    for r in range(6):
        for c in range(4):
            parts.append(L.box(f"R21A_FIX_Breaker_Switch{r}{c}", (0.070, 0.020, 0.060),
                               (x - 0.250 + c * 0.130, y - 0.202, 2.260 - r * 0.105),
                               mat["M_HERO_Plastic"], coll, bevel=0.004, seg=2))
            parts.append(L.box(f"R21A_FIX_Breaker_LED{r}{c}", (0.008, 0.008, 0.008),
                               (x - 0.250 + c * 0.130, y - 0.208, 2.220 - r * 0.105),
                               mat["led_green"] if (r + c) % 3 else mat["M_HERO_LED_Red"], coll,
                               bevel=0.0, seg=1))
    # vents and label
    for i in range(5):
        parts.append(L.box(f"R21A_FIX_Breaker_Vent{i}", (0.300, 0.010, 0.008), (x + 0.240, y - 0.184, 1.420 + i * 0.020),
                           mat["grille"], coll, bevel=0.001, seg=1))
    parts.append(L.text_mesh("R21A_FIX_Breaker_Label", "DISTRIBUCION // SEC-03", 0.024,
                             (x - 0.080, y - 0.1883, 2.400), (math.radians(90), 0, 0),
                             mat["label"], coll, extrude=0.0008))
    # conduit down to the floor and up to the tray
    parts.append(L.cyl("R21A_FIX_Breaker_ConduitD", 0.024, 1.280, (x + 0.560, y - 0.040, 0.640),
                       mat["M_HERO_Galvanized"], coll, segments=12, bevel=0.002))
    parts.append(L.cyl("R21A_FIX_Breaker_ConduitU", 0.024, 1.300, (x + 0.560, y - 0.040, 3.050),
                       mat["M_HERO_Galvanized"], coll, segments=12, bevel=0.002))
    for z in (0.200, 0.700, 1.200, 2.500, 3.100):
        parts.append(L.box(f"R21A_FIX_Breaker_Clamp{z}", (0.050, 0.070, 0.028), (x + 0.560, y - 0.040, z),
                           mat["M_HERO_Steel_Dark"], coll, bevel=0.002, seg=2))
    ob = L.join(parts, "R21A_FIX_BreakerPanel", coll)
    L.weighted_normal(ob)
    return ob


def build_column_dock(mat, coll, column_x=-78.0, column_y=26.0):
    """Radio charging dock / emergency comms box bolted to the west face of a column."""
    objs = []
    face_x = column_x - 0.225
    parts = []
    parts.append(L.box("R21A_COL_DockBody", (0.170, 0.500, 0.620), (face_x - 0.085, column_y, 1.430),
                       mat["olive"], coll, bevel=0.006, seg=3))
    parts.append(L.box("R21A_COL_DockDoor", (0.014, 0.450, 0.550), (face_x - 0.175, column_y, 1.430),
                       mat["olive_dark"], coll, bevel=0.003, seg=2))
    parts.append(L.box("R21A_COL_DockFrame", (0.012, 0.470, 0.570), (face_x - 0.170, column_y, 1.430),
                       mat["M_HERO_Steel_Dark"], coll, bevel=0.002, seg=2))
    # two handsets in cradles
    for i, y in enumerate((column_y - 0.120, column_y + 0.120)):
        parts.append(L.box(f"R21A_COL_Cradle{i}", (0.060, 0.075, 0.180), (face_x - 0.195, y, 1.400),
                           mat["M_HERO_Plastic"], coll, bevel=0.006, seg=3))
        parts.append(L.box(f"R21A_COL_Handset{i}", (0.040, 0.060, 0.190), (face_x - 0.230, y, 1.420),
                           mat["M_HERO_Plastic"], coll, bevel=0.010, seg=3))

        parts.append(L.coil(f"R21A_COL_Cord{i}", (face_x - 0.235, y + 0.030, 1.330),
                            (0, 0, -1), 0.016, 0.008, 3.0, 0.0025, mat["M_HERO_Rubber"], coll,
                            n=10, sides=5))
    # status LEDs and label
    parts.append(L.box("R21A_COL_LED0", (0.006, 0.020, 0.006), (face_x - 0.181, column_y + 0.195, 1.690),
                       mat["led_green"], coll, bevel=0.0, seg=1))
    parts.append(L.box("R21A_COL_LED1", (0.006, 0.020, 0.006), (face_x - 0.181, column_y + 0.220, 1.690),
                       mat["M_HERO_LED_Amber"], coll, bevel=0.0, seg=1))
    # conduit down the column face to the floor
    parts.append(L.cyl("R21A_COL_Conduit", 0.020, 1.120, (face_x - 0.025, column_y + 0.190, 0.570),
                       mat["M_HERO_Galvanized"], coll, segments=12, bevel=0.002))
    for z in (0.180, 0.560, 0.940):
        parts.append(L.box(f"R21A_COL_Clamp{z}", (0.070, 0.055, 0.030), (face_x - 0.030, column_y + 0.190, z),
                           mat["M_HERO_Steel_Dark"], coll, bevel=0.002, seg=2))
    parts.append(L.box("R21A_COL_Junction", (0.110, 0.130, 0.160), (face_x - 0.055, column_y + 0.190, 0.130),
                       mat["M_HERO_Steel_Dark"], coll, bevel=0.004, seg=3))
    parts.append(L.bolts("R21A_COL_Bolts",
                         [(face_x - 0.010, column_y + dy, 1.430 + dz)
                          for dy in (-0.230, 0.230) for dz in (-0.280, 0.280)],
                         (-1, 0, 0), 0.007, 0.009, mat["M_HERO_Steel_Bare"], coll))
    objs.append(L.join(parts, "R21A_COL_RadioDock", coll))
    return objs


def build_emergency_fixture(prefix, loc, mat, coll, rot_z=0.0):
    """Wall-mounted red emergency light housing + lens (mesh only)."""
    parts = []
    parts.append(L.box(prefix + "_Housing", (0.320, 0.130, 0.220), (0, 0, 0),
                       mat["M_HERO_Steel_Dark"], coll, bevel=0.006, seg=3))
    parts.append(L.box(prefix + "_BackPlate", (0.390, 0.025, 0.290), (0, 0.075, 0),
                       mat["olive"], coll, bevel=0.004, seg=2))
    parts.append(L.box(prefix + "_LensFrame", (0.250, 0.030, 0.150), (0, -0.075, 0),
                       mat["M_HERO_Steel_Bare"], coll, bevel=0.004, seg=2))
    parts.append(L.box(prefix + "_Lens", (0.210, 0.018, 0.115), (0, -0.094, 0),
                       mat["M_HERO_LED_Red"], coll, bevel=0.006, seg=3))
    for i in range(4):
        parts.append(L.box(f"{prefix}_Grille{i}", (0.240, 0.020, 0.006),
                           (0, -0.092, -0.060 + i * 0.040), mat["M_HERO_Steel_Dark"], coll,
                           bevel=0.001, seg=1))
    parts.append(L.box(prefix + "_CableGland", (0.050, 0.060, 0.050), (0.130, 0.090, -0.080),
                       mat["M_HERO_Galvanized"], coll, bevel=0.003, seg=2))
    ob = L.join(parts, prefix, coll)
    L.transform_objects([ob], Matrix.Translation(Vector(loc)) @ Matrix.Rotation(rot_z, 4, "Z"))
    L.weighted_normal(ob)
    return ob
