"""Pase de geometría de la RECEPCIÓN del Nivel 1 (v126).

Añade servicios de techo (conductos, bandejas, tuberías, difusores,
downlights), reconstruye el mostrador de recepción y añade zócalos
perimetrales. Los originales blocky no se borran: se ocultan y se marcan
con `replaced_by`, siguiendo la convención de pases anteriores.

Idempotente: si los objetos ya existen con el mismo nombre, se reutilizan.
"""

import bmesh
import bpy
from mathutils import Vector

RECEP_Z_FLOOR = -5.8
RECEP_Z_CEIL = 0.2
COLLECTION = "NEXUS_V05_REC_PASS126"
COUNTER = (-12.0, 8.0)  # centro del mostrador existente
COLS = []


# --------------------------------------------------------------------------
# utilidades de construcción
# --------------------------------------------------------------------------
def get_collection(name):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    return coll


def _finish(name, bm, center, material, coll, rot_z=0.0):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.get(name)
    if obj is not None:
        old_mesh = obj.data
        obj.data = mesh
        if old_mesh.users == 0:
            bpy.data.meshes.remove(old_mesh)
    else:
        obj = bpy.data.objects.new(name, mesh)
        coll.objects.link(obj)
    obj.location = Vector(center)
    obj.rotation_euler = (0.0, 0.0, rot_z)
    mesh.materials.clear()
    if material is not None:
        mesh.materials.append(material)
    return obj


def box(name, center, size, material, coll, rot_z=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    return _finish(name, bm, center, material, coll, rot_z)


def cylinder(name, center, radius, depth, material, coll, segments=16, axis="Z", rot_z=0.0):
    bm = bmesh.new()
    try:
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=segments,
            radius1=radius, radius2=radius, depth=depth,
        )
    except TypeError:
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=segments,
            diameter1=radius, diameter2=radius, depth=depth,
        )
    if axis == "X":
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0),
                         matrix=__import__("mathutils").Matrix.Rotation(1.5708, 3, "Y"))
    elif axis == "Y":
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0),
                         matrix=__import__("mathutils").Matrix.Rotation(1.5708, 3, "X"))
    return _finish(name, bm, center, material, coll, rot_z)


# --------------------------------------------------------------------------
# materiales nuevos (no tocan los compartidos)
# --------------------------------------------------------------------------
def material(name, color, roughness=0.5, metallic=0.0, emission=None, emission_strength=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = next((n for n in tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        out = next(n for n in tree.nodes if n.type == "OUTPUT_MATERIAL")
        bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled")
        tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


def build_materials():
    return {
        "galv": material("NEXUS_V05_MAT_Galv", (0.30, 0.31, 0.31), 0.42, 0.85),
        "galv_dark": material("NEXUS_V05_MAT_Galv_Dark", (0.17, 0.18, 0.18), 0.48, 0.75),
        "pipe_red": material("NEXUS_V05_MAT_Pipe_Red", (0.32, 0.035, 0.025), 0.35, 0.4),
        "tray": material("NEXUS_V05_MAT_CableTray", (0.22, 0.23, 0.22), 0.55, 0.7),
        "conduit": material("NEXUS_V05_MAT_Conduit", (0.24, 0.25, 0.24), 0.6, 0.2),
        "led": material("NEXUS_V05_MAT_LED_Panel", (0.85, 0.88, 0.85), 0.3, 0.0,
                        emission=(1.0, 0.94, 0.82), emission_strength=12.0),
        "top": material("NEXUS_V05_MAT_Counter_Top", (0.085, 0.09, 0.088), 0.26, 0.45),
        "front": material("NEXUS_V05_MAT_Counter_Front", (0.030, 0.048, 0.042), 0.34, 0.15),
        "reveal": material("NEXUS_V05_MAT_Counter_Reveal", (0.012, 0.014, 0.013), 0.5, 0.3),
        "base": material("NEXUS_V05_MAT_Baseboard", (0.035, 0.040, 0.038), 0.45, 0.2),
        "cable": material("NEXUS_V05_MAT_Cable_Bundle", (0.02, 0.02, 0.021), 0.7, 0.0),
    }


# --------------------------------------------------------------------------
# servicios de techo
# --------------------------------------------------------------------------
def build_ceiling_services(mats, coll):
    # --- conducto principal este-oeste ---
    main_y = 6.6
    main_z = -0.62
    box("NEXUS_V05_REC_CS_DUCT_MAIN", (-12.0, main_y, -0.72), (15.3, 1.25, 0.72), mats["galv"], coll)
    for index, x in enumerate((-19.6, -17.2, -14.8, -12.4, -10.0, -7.6, -5.2)):
        box(f"NEXUS_V05_REC_CS_DUCT_MAIN_FLANGE_{index}", (x, main_y, -0.72),
            (0.08, 1.33, 0.80), mats["galv_dark"], coll)
        for side, sign in (("A", -1), ("B", 1)):
            cylinder(f"NEXUS_V05_REC_CS_HANGER_{index}_{side}",
                     (x, main_y + sign * 0.52, -0.30), 0.014, 0.12,
                     mats["galv_dark"], coll, segments=8)
            box(f"NEXUS_V05_REC_CS_HANGER_FOOT_{index}_{side}",
                (x, main_y + sign * 0.42, -0.30), (0.06, 0.06, 0.05), mats["galv_dark"], coll)

    # --- ramal norte-sur ---
    box("NEXUS_V05_REC_CS_DUCT_BRANCH", (-17.2, 4.15, -0.66),
        (0.80, 4.35, 0.58), mats["galv"], coll)
    box("NEXUS_V05_REC_CS_DUCT_BRANCH_JOINT", (-17.2, 6.1, -0.68),
        (0.86, 0.55, 0.64), mats["galv_dark"], coll)

    # --- difusores cuadrados colgados ---
    for index, (x, y) in enumerate(((-17.2, 4.0), (-17.2, 5.7), (-13.6, 6.6), (-9.4, 6.6))):
        base_z = -0.95 if x == -17.2 else -1.08
        neck_h = (base_z - 0.225) - (-1.02)
        box(f"NEXUS_V05_REC_CS_DIFFUSER_NECK_{index}", (x, y, -1.02 + neck_h / 2),
            (0.42, 0.42, max(neck_h, 0.05)), mats["galv"], coll)
        box(f"NEXUS_V05_REC_CS_DIFFUSER_{index}", (x, y, -1.06),
            (0.58, 0.58, 0.06), mats["galv"], coll)
        box(f"NEXUS_V05_REC_CS_DIFFUSER_FACE_{index}", (x, y, -1.10),
            (0.50, 0.50, 0.02), mats["galv_dark"], coll)

    # --- bandeja de cables este-oeste ---
    tray_z = -0.46
    box("NEXUS_V05_REC_CS_TRAY_TRAY", (-12.0, 3.4, tray_z), (15.2, 0.42, 0.02), mats["tray"], coll)
    for side, sign in (("N", -1), ("S", 1)):
        box(f"NEXUS_V05_REC_CS_TRAY_RAIL_{side}", (-12.0, 3.4 + sign * 0.21, tray_z + 0.035),
            (15.2, 0.02, 0.07), mats["tray"], coll)
    for index, x in enumerate((-18.6, -15.4, -12.2, -9.0, -5.8)):
        box(f"NEXUS_V05_REC_CS_TRAY_RUNG_{index}", (x, 3.4, tray_z + 0.03),
            (0.03, 0.44, 0.015), mats["tray"], coll)
        cylinder(f"NEXUS_V05_REC_CS_TRAY_HANGER_{index}", (x, 3.4, tray_z + 0.35),
                 0.010, 0.62, mats["conduit"], coll, segments=8)
    for index, y_offset in enumerate((-0.13, 0.0, 0.12)):
        box(f"NEXUS_V05_REC_CS_TRAY_CABLE_{index}", (-12.0, 3.4 + y_offset, tray_z + 0.05),
            (15.0, 0.05, 0.05), mats["cable"], coll)

    # --- banda de cables norte-sur sobre la oficina ---
    box("NEXUS_V05_REC_CS_TRAY_EAST", (-6.2, 6.7, tray_z), (0.42, 9.9, 0.02), mats["tray"], coll)
    for index, y in enumerate((2.4, 4.6, 6.8, 9.0, 11.2)):
        box(f"NEXUS_V05_REC_CS_TRAY_EAST_RUNG_{index}", (-6.2, y, tray_z + 0.03),
            (0.44, 0.03, 0.015), mats["tray"], coll)
        cylinder(f"NEXUS_V05_REC_CS_TRAY_EAST_HANGER_{index}", (-6.2, y, tray_z + 0.35),
                 0.010, 0.62, mats["conduit"], coll, segments=8)

    # --- rociadores ---
    box("NEXUS_V05_REC_CS_SPRINK_SECTION", (-12.0, 10.6, -0.38), (15.2, 0.12, 0.06), mats["galv_dark"], coll)
    cylinder("NEXUS_V05_REC_CS_SPRINK_PIPE", (-12.0, 10.6, -0.40), 0.055, 15.2,
             mats["pipe_red"], coll, segments=14, axis="X")
    for index, x in enumerate((-18.4, -15.2, -12.0, -8.8, -5.6)):
        cylinder(f"NEXUS_V05_REC_CS_SPRINK_DROP_{index}", (x, 10.6, -0.62),
                 0.022, 0.38, mats["pipe_red"], coll, segments=10)
        cylinder(f"NEXUS_V05_REC_CS_SPRINK_HEAD_{index}", (x, 10.6, -0.83),
                 0.045, 0.06, mats["galv"], coll, segments=10)
        cylinder(f"NEXUS_V05_REC_CS_SPRINK_DEFLECTOR_{index}", (x, 10.6, -0.87),
                 0.06, 0.012, mats["galv"], coll, segments=10)

    # --- bajantes verticales en muro oeste ---
    for index, (yy, radius, mat) in enumerate(((2.4, 0.07, "pipe_red"), (2.75, 0.05, "galv"),
                                               (10.9, 0.06, "galv"))):
        cylinder(f"NEXUS_V05_REC_CS_RISER_{index}", (-19.7, yy, -2.9),
                 radius, 5.6, mats[mat], coll, segments=12)

    # --- downlights empotrados ---
    for index, (x, y) in enumerate(((-17.0, 3.6), (-12.0, 3.6), (-7.0, 3.6),
                                    (-17.0, 9.8), (-12.0, 9.8), (-7.0, 9.8))):
        cylinder(f"NEXUS_V05_REC_CS_DOWNLIGHT_CAN_{index}", (x, y, -0.02),
                 0.17, 0.12, mats["galv_dark"], coll, segments=16)
        cylinder(f"NEXUS_V05_REC_CS_DOWNLIGHT_LENS_{index}", (x, y, -0.09),
                 0.14, 0.02, mats["led"], coll, segments=16)
        cylinder(f"NEXUS_V05_REC_CS_DOWNLIGHT_TRIM_{index}", (x, y, -0.03),
                 0.20, 0.03, mats["galv"], coll, segments=20)

    # --- detectores de humo ---
    for index, (x, y) in enumerate(((-15.6, 5.2), (-9.0, 8.2), (-16.4, 9.2))):
        cylinder(f"NEXUS_V05_REC_CS_SMOKE_DETECTOR_{index}", (x, y, -0.10),
                 0.09, 0.05, mats["galv"], coll, segments=14)
        cylinder(f"NEXUS_V05_REC_CS_SMOKE_DETECTOR_LED_{index}", (x, y, -0.13),
                 0.012, 0.01, mats["led"], coll, segments=8)


def build_emergency_fixtures(mats, coll):
    """Carcasas de emergencia para que las luces rojas no floten."""
    red = bpy.data.materials.get("NEXUS_V05_MAT_Emergency_Lens")
    if red is None:
        red = material("NEXUS_V05_MAT_Emergency_Lens", (0.45, 0.02, 0.01), 0.25, 0.0,
                       emission=(1.0, 0.06, 0.02), emission_strength=6.0)

    # junto a la puerta de acceso, no en el vano (muro sur, cara interior y=1.84)
    box("NEXUS_V05_REC_EMERG_DOOR_HOUSING", (-13.4, 1.93, -3.0),
        (0.34, 0.12, 0.13), mats["galv_dark"], coll)
    box("NEXUS_V05_REC_EMERG_DOOR_LENS", (-13.4, 1.855, -3.0),
        (0.26, 0.02, 0.085), red, coll)
    box("NEXUS_V05_REC_EMERG_DOOR_HOOD", (-13.4, 1.90, -2.90),
        (0.34, 0.16, 0.02), mats["galv_dark"], coll)

    # esquina noroeste (muro oeste, cara interior x=-19.86)
    box("NEXUS_V05_REC_EMERG_NW_HOUSING", (-19.80, 10.6, -3.0),
        (0.12, 0.34, 0.13), mats["galv_dark"], coll)
    box("NEXUS_V05_REC_EMERG_NW_LENS", (-19.725, 10.6, -3.0),
        (0.02, 0.26, 0.085), red, coll)
    box("NEXUS_V05_REC_EMERG_NW_HOOD", (-19.76, 10.6, -2.90),
        (0.16, 0.34, 0.02), mats["galv_dark"], coll)


# --------------------------------------------------------------------------
# mostrador
# --------------------------------------------------------------------------
def build_counter(mats, coll):
    cx, cy = COUNTER
    width, depth = 4.2, 1.2
    top_z = -4.94
    floor = RECEP_Z_FLOOR
    south = cy - depth / 2  # cara visitante
    north = cy + depth / 2

    box("NEXUS_V05_REC_COUNTER_TOP", (cx, cy, top_z - 0.03),
        (width + 0.16, depth + 0.12, 0.06), mats["top"], coll)
    box("NEXUS_V05_REC_COUNTER_TOP_NOSE", (cx, south - 0.045, top_z - 0.045),
        (width + 0.16, 0.05, 0.03), mats["reveal"], coll)

    front_bottom = floor + 0.10
    panel_h = (top_z - 0.06) - front_bottom
    panel_center_z = front_bottom + panel_h / 2
    box("NEXUS_V05_REC_COUNTER_FRONT", (cx, south + 0.04, panel_center_z),
        (width, 0.08, panel_h), mats["front"], coll)
    for index in range(1, 4):
        x = cx - width / 2 + index * (width / 4.0)
        box(f"NEXUS_V05_REC_COUNTER_REVEAL_{index}", (x, south - 0.004, panel_center_z),
            (0.022, 0.014, panel_h - 0.04), mats["reveal"], coll)
    box("NEXUS_V05_REC_COUNTER_KICK", (cx, south + 0.09, floor + 0.05),
        (width - 0.16, 0.06, 0.10), mats["reveal"], coll)

    box("NEXUS_V05_REC_COUNTER_BACK", (cx, north - 0.04, panel_center_z),
        (width, 0.05, panel_h), mats["front"], coll)
    for sign, x in (("W", cx - width / 2 + 0.04), ("E", cx + width / 2 - 0.04)):
        box(f"NEXUS_V05_REC_COUNTER_END_{sign}", (x, cy, panel_center_z),
            (0.08, depth, panel_h), mats["front"], coll)

    # cajonera y bandeja de cables del lado del personal
    box("NEXUS_V05_REC_COUNTER_DRAWER_UNIT", (cx + 1.05, cy + 0.28, -5.42),
        (0.62, 0.55, 0.66), mats["galv_dark"], coll)
    for index, z in enumerate((-5.62, -5.38)):
        box(f"NEXUS_V05_REC_COUNTER_DRAWER_FRONT_{index}", (cx + 1.05, cy + 0.02, z),
            (0.58, 0.02, 0.20), mats["galv"], coll)
        box(f"NEXUS_V05_REC_COUNTER_DRAWER_PULL_{index}", (cx + 1.05, cy - 0.01, z + 0.06),
            (0.20, 0.02, 0.02), mats["reveal"], coll)
    box("NEXUS_V05_REC_COUNTER_CABLE_TRAY", (cx, cy + 0.36, -5.72),
        (width - 0.3, 0.12, 0.03), mats["tray"], coll)

    # altura de trabajo del personal
    box("NEXUS_V05_REC_COUNTER_FOOTREST", (cx - 0.6, cy + 0.3, -5.62),
        (2.2, 0.35, 0.04), mats["galv_dark"], coll)

    # ocultar el mostrador blocky original
    originals = ["NEXUS_V05_REC_DESK", "NEXUS_V05_REC_DESK_FRONT",
                 "NEXUS_V05_REC_DESK_FRONT_S", "NEXUS_V05_REC_DESK_SIDE_W",
                 "NEXUS_V05_REC_DESK_SIDE_E"]
    originals += [f"NEXUS_V05_REC_DESK_LEG_{i}" for i in range(4)]
    hidden = 0
    for name in originals:
        obj = bpy.data.objects.get(name)
        if obj is None:
            continue
        obj.hide_render = True
        obj.hide_viewport = True
        obj["replaced_by"] = "NEXUS_V05_REC_COUNTER_*"
        hidden += 1
    print("COUNTER_HIDDEN_ORIGINALS", hidden)


# --------------------------------------------------------------------------
# zócalos
# --------------------------------------------------------------------------
def build_baseboards(mats, coll):
    height = 0.12
    proud = 0.025
    z = RECEP_Z_FLOOR + height / 2
    y_north = 11.7 - 0.14 - proud / 2
    x_west = -20.0 + 0.14 + proud / 2
    x_east = -4.0 - 0.14 - proud / 2
    y_south = 1.7 + 0.14 + proud / 2

    box("NEXUS_V05_REC_BASEBOARD_N", (-12.0, y_north, z),
        (15.86, proud, height), mats["base"], coll)
    box("NEXUS_V05_REC_BASEBOARD_W", (x_west, 6.7, z),
        (proud, 9.86, height), mats["base"], coll)
    box("NEXUS_V05_REC_BASEBOARD_E", (x_east, 6.7, z),
        (proud, 9.86, height), mats["base"], coll)
    # muro sur, partido por la puerta de acceso (x -12.9..-11.1)
    seg_a_len = -12.9 - (x_west + proud / 2)
    box("NEXUS_V05_REC_BASEBOARD_S_A",
        ((x_west + proud / 2) + seg_a_len / 2, y_south, z),
        (seg_a_len, proud, height), mats["base"], coll)
    seg_b_start = -11.1
    seg_b_len = (x_east - proud / 2) - seg_b_start
    box("NEXUS_V05_REC_BASEBOARD_S_B", (seg_b_start + seg_b_len / 2, y_south, z),
        (seg_b_len, proud, height), mats["base"], coll)

    old = bpy.data.objects.get("NEXUS_V05_RECEPCION_BASE")
    if old is not None:
        old.hide_render = True
        old.hide_viewport = True
        old["replaced_by"] = "NEXUS_V05_REC_BASEBOARD_*"


def build_wainscot(mats, coll):
    """Banda de chapa verde corrugada de 1,00 m en todo el perímetro."""
    bottom = RECEP_Z_FLOOR + 0.12
    height = 1.0
    z = bottom + height / 2
    thick = 0.04
    half = thick / 2
    trim_z = bottom + height + 0.02
    trim_h = 0.04

    y_north = 11.56 - half
    x_west = -19.86 + half
    x_east = -4.14 - half
    y_south = 1.84 + half

    box("NEXUS_V05_REC_WAINSCOT_N", (-12.0, y_north, z),
        (15.86, thick, height), mats["wainscot"], coll)
    box("NEXUS_V05_REC_WAINSCOT_W", (x_west, 6.7, z),
        (thick, 9.86, height), mats["wainscot"], coll)
    box("NEXUS_V05_REC_WAINSCOT_E", (x_east, 6.7, z),
        (thick, 9.86, height), mats["wainscot"], coll)

    door_l, door_r = -12.9, -11.1
    seg_a_start = x_west - half
    seg_a_len = door_l - seg_a_start
    box("NEXUS_V05_REC_WAINSCOT_S_A", (seg_a_start + seg_a_len / 2, y_south, z),
        (seg_a_len, thick, height), mats["wainscot"], coll)
    seg_b_len = (x_east + half) - door_r
    box("NEXUS_V05_REC_WAINSCOT_S_B", (door_r + seg_b_len / 2, y_south, z),
        (seg_b_len, thick, height), mats["wainscot"], coll)

    # remate superior metálico
    box("NEXUS_V05_REC_WAINSCOT_TRIM_N", (-12.0, y_north - 0.005, trim_z),
        (15.9, thick + 0.03, trim_h), mats["base"], coll)
    box("NEXUS_V05_REC_WAINSCOT_TRIM_W", (x_west + 0.005, 6.7, trim_z),
        (thick + 0.03, 9.9, trim_h), mats["base"], coll)
    box("NEXUS_V05_REC_WAINSCOT_TRIM_E", (x_east - 0.005, 6.7, trim_z),
        (thick + 0.03, 9.9, trim_h), mats["base"], coll)
    box("NEXUS_V05_REC_WAINSCOT_TRIM_S_A", (seg_a_start + seg_a_len / 2, y_south + 0.005, trim_z),
        (seg_a_len, thick + 0.03, trim_h), mats["base"], coll)
    box("NEXUS_V05_REC_WAINSCOT_TRIM_S_B", (door_r + seg_b_len / 2, y_south + 0.005, trim_z),
        (seg_b_len, thick + 0.03, trim_h), mats["base"], coll)


# --------------------------------------------------------------------------
# zócalos
# --------------------------------------------------------------------------
def main():
    mats = build_materials()
    mats["wainscot"] = bpy.data.materials["NEXUS_V05_MAT_Rec_Wainscot"]
    coll = get_collection(COLLECTION)
    build_ceiling_services(mats, coll)
    build_counter(mats, coll)
    build_baseboards(mats, coll)
    build_wainscot(mats, coll)
    build_emergency_fixtures(mats, coll)
    total = len([o for o in coll.objects if o.type == "MESH"])
    tris = 0
    for obj in coll.objects:
        if obj.type != "MESH":
            continue
        obj.data.calc_loop_triangles()
        tris += len(obj.data.loop_triangles)
    print("REC_PASS126_OBJECTS", total)
    print("REC_PASS126_TRIS", tris)


main()
