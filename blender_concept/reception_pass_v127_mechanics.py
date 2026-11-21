"""FRECUENCIA MUERTA - Recepcion Nivel 1 - pase de mecanicas (v127).

Anade a NEXUS_V05_RECEPCION lo que falta para que la sala funcione en juego:

  * Objetos recuperables con peso, valor, fragilidad y ruido declarados.
  * Escondite interactivo con interior medido para el jugador.
  * Puerta de acceso con pivote real (hoja operable).
  * Trampa sonora fisica (cristales, latas y bandeja) en el recorrido.

Todo es geometria local, no modifica la biblioteca compartida. Los objetos
quedan marcados con propiedades personalizadas que el futuro exportador a
Godot puede leer para crear RigidBody, loot y puntos de escondite.

Idempotente: borra la coleccion NEXUS_V05_REC_PLAY antes de reconstruirla.
"""

import bmesh
import bpy
import math
from mathutils import Matrix, Vector

COLL_NAME = "NEXUS_V05_REC_PLAY"
PREFIX = "NEXUS_V05_REC_"

FLOOR_TOP = -5.65


# --------------------------------------------------------------------------
# utilidades
# --------------------------------------------------------------------------

def ensure_collection():
    coll = bpy.data.collections.get(COLL_NAME)
    if coll is None:
        coll = bpy.data.collections.new(COLL_NAME)
        bpy.context.scene.collection.children.link(coll)
    else:
        for obj in list(coll.all_objects):
            bpy.data.objects.remove(obj, do_unlink=True)
    return coll


def tag(obj, **props):
    for key, value in props.items():
        obj[key] = value
    return obj


def link(obj, coll):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)
    return obj


def bevel(obj, width=0.006, segments=2):
    """Bisel real via bmesh (no modificador, para que sobreviva al export)."""
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.bevel(
        bm,
        geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
        offset=width,
        segments=segments,
        profile=0.5,
        affect="EDGES",
        clamp_overlap=True,
    )
    bm.to_mesh(me)
    bm.free()
    me.update()
    return obj


def mesh_from_bm(name, bm, coll, mat=None, bevel_width=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    coll.objects.link(obj)
    if mat is not None:
        obj.data.materials.append(mat)
    if bevel_width:
        bevel(obj, bevel_width)
    return obj


def box(name, size, loc, coll, mat=None, rot_z=0.0, bevel_width=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    obj = mesh_from_bm(name, bm, coll, mat, bevel_width)
    obj.location = Vector(loc)
    obj.rotation_euler = (0.0, 0.0, rot_z)
    return obj


def cylinder(name, radius, depth, loc, coll, mat=None, segments=16, rot=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=segments,
        radius1=radius,
        radius2=radius,
        depth=depth,
    )
    obj = mesh_from_bm(name, bm, coll, mat)
    obj.location = Vector(loc)
    obj.rotation_euler = rot
    return obj


def apply_transform(obj):
    obj.data.transform(obj.matrix_world)
    obj.matrix_world = Matrix.Identity(4)


def material(name, color, roughness=0.6, metallic=0.0, transmission=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        return mat
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if "Transmission Weight" in bsdf.inputs:
        bsdf.inputs["Transmission Weight"].default_value = transmission
    return mat


def parent_keep_transform(child, parent):
    bpy.context.view_layer.update()
    world = child.matrix_world.copy()
    child.parent = parent
    child.matrix_world = world


def attach(child, parent):
    """Parenta conservando las coordenadas locales (ya relativas al root)."""
    loc = child.location.copy()
    rot = child.rotation_euler.copy()
    child.parent = parent
    child.matrix_parent_inverse = Matrix.Identity(4)
    child.location = loc
    child.rotation_euler = rot


# --------------------------------------------------------------------------
# materiales
# --------------------------------------------------------------------------

def build_materials():
    return {
        "shell": material("NEXUS_V05_MAT_Loot_Shell", (0.055, 0.060, 0.052), 0.55),
        "shell_light": material("NEXUS_V05_MAT_Loot_Shell_Light", (0.30, 0.31, 0.28), 0.62),
        "label": material("NEXUS_V05_MAT_Loot_Label", (0.62, 0.60, 0.52), 0.75),
        "orange": material("NEXUS_V05_MAT_Loot_Hazard", (0.48, 0.16, 0.03), 0.55),
        "rubber": material("NEXUS_V05_MAT_Loot_Rubber", (0.02, 0.02, 0.02), 0.85),
        "shard": material("NEXUS_V05_MAT_Shard", (0.55, 0.63, 0.62), 0.08, 0.0, 0.85),
        "tin": material("NEXUS_V05_MAT_Tin_Can", (0.42, 0.43, 0.44), 0.34, 1.0),
        "wood": bpy.data.materials.get("NEXUS_Wood"),
        "galv": bpy.data.materials.get("NEXUS_V05_MAT_Galv"),
        "steel": bpy.data.materials.get("NEXUS_Steel"),
        "green": bpy.data.materials.get("NEXUS_V05_MAT_Rec_Painted_Green"),
    }


# --------------------------------------------------------------------------
# objetos recuperables
# --------------------------------------------------------------------------

def build_case(mats, coll):
    """Maletin de recuperacion NEXUS: 17 kg, una mano, metal ruidoso."""
    base = bpy.data.objects.new(PREFIX + "LOOT_CASE_0", None)
    base.empty_display_size = 0.15
    coll.objects.link(base)
    base.location = (-13.55, 6.95, FLOOR_TOP)
    base.rotation_euler = (0, 0, 0.35)

    parts = []
    parts.append(box("REC_LOOT_CASE_0_BODY", (0.46, 0.20, 0.30), (0, 0, 0.15), coll, mats["shell"], bevel_width=0.008))
    parts.append(box("REC_LOOT_CASE_0_LID", (0.47, 0.21, 0.05), (0, 0, 0.315), coll, mats["shell"], bevel_width=0.007))
    parts.append(box("REC_LOOT_CASE_0_SEAM", (0.462, 0.205, 0.008), (0, 0, 0.292), coll, mats["rubber"]))
    parts.append(box("REC_LOOT_CASE_0_HANDLE", (0.13, 0.035, 0.028), (0, 0, 0.372), coll, mats["rubber"], bevel_width=0.004))
    for sx in (-0.175, 0.175):
        parts.append(box("REC_LOOT_CASE_0_LATCH_%s" % ("W" if sx < 0 else "E"), (0.045, 0.02, 0.05), (sx, 0.106, 0.30), coll, mats["galv"], bevel_width=0.003))
    for sx in (-0.215, 0.215):
        for sz in (0.035, 0.265):
            parts.append(box("REC_LOOT_CASE_0_CORNER_%s_%d" % ("W" if sx < 0 else "E", int(sz * 1000)), (0.035, 0.205, 0.05), (sx, 0, sz), coll, mats["galv"], bevel_width=0.003))
    parts.append(box("REC_LOOT_CASE_0_LABEL", (0.14, 0.004, 0.07), (-0.06, -0.104, 0.18), coll, mats["label"]))
    parts.append(box("REC_LOOT_CASE_0_STRIPE", (0.46, 0.008, 0.022), (0, -0.101, 0.075), coll, mats["orange"]))

    for p in parts:
        attach(p, base)
    tag(base, loot=True, loot_class="recuperable", loot_value=640.0, weight_kg=17.0,
        fragile=False, carry_hands=1, noise_kind="metal", noise_radius_m=4.0,
        physics="rigid_body", collider="box", exported_name="loot_case")
    return base


def build_sample(mats, coll):
    """Caja isotermica de muestras: 9 kg, fragil, valor alto."""
    base = bpy.data.objects.new(PREFIX + "LOOT_SAMPLE_0", None)
    base.empty_display_size = 0.15
    coll.objects.link(base)
    base.location = (-9.55, 6.45, FLOOR_TOP)
    base.rotation_euler = (0, 0, -0.22)

    parts = [
        box("REC_LOOT_SAMPLE_0_BODY", (0.42, 0.32, 0.26), (0, 0, 0.13), coll, mats["shell_light"], bevel_width=0.008),
        box("REC_LOOT_SAMPLE_0_LID", (0.43, 0.33, 0.04), (0, 0, 0.28), coll, mats["shell_light"], bevel_width=0.006),
        box("REC_LOOT_SAMPLE_0_GASKET", (0.425, 0.325, 0.01), (0, 0, 0.258), coll, mats["rubber"]),
        box("REC_LOOT_SAMPLE_0_LABEL", (0.20, 0.004, 0.11), (0.02, -0.162, 0.15), coll, mats["label"]),
        box("REC_LOOT_SAMPLE_0_HAZARD", (0.20, 0.004, 0.045), (0.02, -0.163, 0.055), coll, mats["orange"]),
        box("REC_LOOT_SAMPLE_0_HANDLE", (0.10, 0.03, 0.022), (0, 0, 0.312), coll, mats["rubber"]),
    ]
    for i, sx in enumerate((-0.155, 0.155)):
        parts.append(box("REC_LOOT_SAMPLE_0_CLIP_%d" % i, (0.035, 0.02, 0.07), (sx, 0.165, 0.22), coll, mats["galv"], bevel_width=0.003))
    for p in parts:
        attach(p, base)
    tag(base, loot=True, loot_class="recuperable", loot_value=900.0, weight_kg=9.0,
        fragile=True, carry_hands=1, noise_kind="plastic", noise_radius_m=2.5,
        physics="rigid_body", collider="box", exported_name="loot_sample")
    return base


def build_crate(mats, coll):
    """Caja de equipo: 42 kg, requiere dos jugadores."""
    base = bpy.data.objects.new(PREFIX + "LOOT_CRATE_0", None)
    base.empty_display_size = 0.25
    coll.objects.link(base)
    base.location = (-16.6, 4.6, FLOOR_TOP)
    base.rotation_euler = (0, 0, 0.15)

    parts = [
        box("REC_LOOT_CRATE_0_BODY", (0.86, 0.62, 0.52), (0, 0, 0.26), coll, mats["wood"], bevel_width=0.006),
        box("REC_LOOT_CRATE_0_LID", (0.88, 0.64, 0.05), (0, 0, 0.545), coll, mats["wood"], bevel_width=0.005),
        box("REC_LOOT_CRATE_0_STENCIL", (0.40, 0.004, 0.10), (0, -0.312, 0.30), coll, mats["label"]),
        box("REC_LOOT_CRATE_0_BAND", (0.86, 0.008, 0.04), (0, -0.311, 0.43), coll, mats["orange"]),
    ]
    for i, (sx, sy) in enumerate(((-0.415, -0.295), (0.415, -0.295), (-0.415, 0.295), (0.415, 0.295))):
        parts.append(box("REC_LOOT_CRATE_0_EDGE_%d" % i, (0.05, 0.05, 0.60), (sx, sy, 0.30), coll, mats["galv"], bevel_width=0.004))
    for p in parts:
        attach(p, base)
    tag(base, loot=True, loot_class="recuperable", loot_value=1800.0, weight_kg=42.0,
        fragile=False, carry_hands=2, requires_two_players=True,
        noise_kind="wood_metal", noise_radius_m=6.0, physics="rigid_body",
        collider="box", exported_name="loot_crate")
    return base


def build_docs(mats, coll):
    """Carpeta de documentos clasificados sobre el mostrador."""
    base = bpy.data.objects.new(PREFIX + "LOOT_DOCS_0", None)
    base.empty_display_size = 0.10
    coll.objects.link(base)
    base.location = (-12.95, 8.16, -4.94)
    base.rotation_euler = (0, 0, 0.12)

    parts = [
        box("REC_LOOT_DOCS_0_FOLDER", (0.34, 0.26, 0.035), (0, 0, 0.018), coll, mats["label"], bevel_width=0.004),
        box("REC_LOOT_DOCS_0_SHEETS", (0.32, 0.24, 0.022), (0.004, 0.002, 0.044), coll, mats["label"]),
        box("REC_LOOT_DOCS_0_TAB", (0.09, 0.10, 0.004), (-0.09, 0.155, 0.040), coll, mats["label"]),
        box("REC_LOOT_DOCS_0_BAND", (0.34, 0.035, 0.004), (0, -0.06, 0.058), coll, mats["orange"]),
    ]
    for p in parts:
        attach(p, base)
    tag(base, loot=True, loot_class="recuperable", loot_value=220.0, weight_kg=0.6,
        fragile=False, carry_hands=1, noise_kind="paper", noise_radius_m=1.0,
        physics="rigid_body", collider="box", exported_name="loot_docs")
    return base


def build_drive(mats, coll):
    """Cartucho de datos NEXUS dentro de su estuche."""
    base = bpy.data.objects.new(PREFIX + "LOOT_DRIVE_0", None)
    base.empty_display_size = 0.06
    coll.objects.link(base)
    base.location = (-10.62, 8.24, -4.94)
    base.rotation_euler = (0, 0, -0.4)

    parts = [
        box("REC_LOOT_DRIVE_0_CASE", (0.15, 0.11, 0.045), (0, 0, 0.022), coll, mats["shell"], bevel_width=0.005),
        box("REC_LOOT_DRIVE_0_LID", (0.15, 0.11, 0.012), (0, 0, 0.050), coll, mats["galv"], bevel_width=0.003),
        box("REC_LOOT_DRIVE_0_LABEL", (0.08, 0.004, 0.028), (0, -0.056, 0.026), coll, mats["label"]),
        box("REC_LOOT_DRIVE_0_CLIP", (0.02, 0.06, 0.012), (0.075, 0, 0.050), coll, mats["galv"]),
    ]
    for p in parts:
        attach(p, base)
    tag(base, loot=True, loot_class="especial", loot_value=1200.0, weight_kg=0.4,
        fragile=False, carry_hands=1, noise_kind="plastic", noise_radius_m=0.8,
        physics="rigid_body", collider="box", exported_name="loot_drive")
    return base


# --------------------------------------------------------------------------
# trampa sonora
# --------------------------------------------------------------------------

def build_noise_trap(mats, coll):
    """Cristales, latas y bandeja sueltos en el recorrido de la puerta."""
    root = bpy.data.objects.new(PREFIX + "TRAP_NOISE_0", None)
    root.empty_display_size = 0.2
    coll.objects.link(root)
    root.location = (-12.5, 3.75, FLOOR_TOP)
    root.rotation_euler = (0, 0, 0.2)

    parts = []

    # Cristales de 4-6 mm de grosor: volumen real, no decal.
    shard_specs = [
        ((0.00, 0.00), 0.085, 0.055),
        ((0.16, -0.10), 0.070, 0.045),
        ((-0.14, 0.08), 0.062, 0.040),
        ((0.05, 0.22), 0.055, 0.036),
        ((-0.22, -0.16), 0.048, 0.030),
        ((0.24, 0.16), 0.040, 0.026),
        ((-0.05, -0.27), 0.036, 0.024),
        ((0.12, 0.05), 0.030, 0.020),
    ]
    for i, ((ox, oy), a, b) in enumerate(shard_specs):
        bm = bmesh.new()
        verts = [
            bm.verts.new((-a * 0.5, -b * 0.35, 0.0)),
            bm.verts.new((a * 0.55, -b * 0.5, 0.0)),
            bm.verts.new((a * 0.15, b * 0.52, 0.0)),
            bm.verts.new((-a * 0.30, b * 0.20, 0.0)),
        ]
        face = bm.faces.new(verts)
        bmesh.ops.solidify(bm, geom=[face], thickness=0.005)
        shard = mesh_from_bm("REC_TRAP_NOISE_0_SHARD_%02d" % i, bm, coll, mats["shard"])
        shard.location = (ox, oy, 0.002)
        shard.rotation_euler = (0, 0, (i * 0.7) % math.tau)
        parts.append(shard)

    # Latas de aluminio caidas.
    for i, (ox, oy, rot) in enumerate(((0.42, -0.28, (math.pi / 2, 0, 0.4)), (-0.40, 0.34, (math.pi / 2, 0, -1.1)))):
        can = cylinder("REC_TRAP_NOISE_0_CAN_%d" % i, 0.033, 0.122, (ox, oy, 0.034), coll, mats["tin"], segments=14, rot=rot)
        parts.append(can)

    # Bandeja metalica volcada.
    tray = box("REC_TRAP_NOISE_0_TRAY", (0.36, 0.26, 0.012), (-0.06, -0.42, 0.008), coll, mats["steel"], bevel_width=0.004)
    tray.rotation_euler = (0, 0, 0.9)
    parts.append(tray)

    for p in parts:
        attach(p, root)
        tag(p, trap_part=True, noise_kind="glass" if "SHARD" in p.name else "metal",
            noise_radius_m=7.0, triggers_on="footstep")

    tag(root, trap=True, trap_kind="sound", noise_radius_m=7.0, noise_kind="glass_metal",
        triggers_on="footstep", breakable=True, exported_name="trap_noise")
    return root


# --------------------------------------------------------------------------
# escondite
# --------------------------------------------------------------------------

def build_hide_cabinet(mats, coll):
    """Armario de conserjeria: interior 0,96 x 0,90 x 1,95 m, una puerta abierta."""
    x0, x1 = -15.90, -14.90
    y0, y1 = 1.90, 2.85
    z0, z1 = FLOOR_TOP, FLOOR_TOP + 2.15
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    wall = 0.02

    root = bpy.data.objects.new(PREFIX + "HIDE_CABINET_0", None)
    root.empty_display_size = 0.3
    coll.objects.link(root)
    root.location = (cx, cy, z0)

    parts = []
    # cuerpo: laterales, trasera, techo y base
    parts.append(box("REC_HIDE_CABINET_0_SIDE_W", (wall, y1 - y0, z1 - z0), (x0 + wall / 2 - cx, 0, (z1 - z0) / 2), coll, mats["green"], bevel_width=0.004))
    parts.append(box("REC_HIDE_CABINET_0_SIDE_E", (wall, y1 - y0, z1 - z0), (x1 - wall / 2 - cx, 0, (z1 - z0) / 2), coll, mats["green"], bevel_width=0.004))
    parts.append(box("REC_HIDE_CABINET_0_BACK", (x1 - x0, wall, z1 - z0), (0, y0 + wall / 2 - cy, (z1 - z0) / 2), coll, mats["green"], bevel_width=0.004))
    parts.append(box("REC_HIDE_CABINET_0_TOP", (x1 - x0, y1 - y0, wall), (0, 0, z1 - z0 - wall / 2), coll, mats["green"], bevel_width=0.004))
    parts.append(box("REC_HIDE_CABINET_0_BASE", (x1 - x0, y1 - y0, 0.06), (0, 0, 0.03), coll, mats["shell"]))
    parts.append(box("REC_HIDE_CABINET_0_SHELF", (x1 - x0 - 2 * wall, 0.26, 0.02), (0, -0.20, 1.62), coll, mats["galv"]))

    # marco frontal
    parts.append(box("REC_HIDE_CABINET_0_FRAME_L", (0.05, 0.03, z1 - z0), (x0 + 0.025 - cx, y1 - 0.015 - cy, (z1 - z0) / 2), coll, mats["galv"], bevel_width=0.004))
    parts.append(box("REC_HIDE_CABINET_0_FRAME_R", (0.05, 0.03, z1 - z0), (x1 - 0.025 - cx, y1 - 0.015 - cy, (z1 - z0) / 2), coll, mats["galv"], bevel_width=0.004))
    parts.append(box("REC_HIDE_CABINET_0_FRAME_T", (x1 - x0, 0.03, 0.05), (0, y1 - 0.015 - cy, z1 - z0 - 0.025), coll, mats["galv"], bevel_width=0.004))

    # rejillas de ventilacion
    for i in range(5):
        parts.append(box("REC_HIDE_CABINET_0_VENT_%d" % i, (0.42, 0.008, 0.012), (0, y0 + 0.014 - cy, 1.30 + i * 0.055), coll, mats["galv"]))

    # hoja oeste cerrada y hoja este abierta 28 grados
    door_z = (z1 - z0) / 2
    closed_leaf = box("REC_HIDE_CABINET_0_DOOR_W", (0.48, 0.022, z1 - z0 - 0.09), (-0.25, y1 - 0.015 - cy, door_z), coll, mats["green"], bevel_width=0.004)
    parts.append(closed_leaf)

    hinge = bpy.data.objects.new(PREFIX + "HIDE_CABINET_0_DOOR", None)
    hinge.empty_display_size = 0.1
    hinge.location = (0.0, y1 - 0.015 - cy, door_z)
    hinge.rotation_euler = (0, 0, math.radians(28))
    coll.objects.link(hinge)
    attach(hinge, root)
    door_leaf = box("REC_HIDE_CABINET_0_DOOR_LEAF", (0.44, 0.022, z1 - z0 - 0.09), (0.22, 0, 0), coll, mats["green"], bevel_width=0.004)
    door_leaf.parent = hinge
    door_leaf.location = (0.22, 0, 0)
    parts.append(door_leaf)
    door_handle = box("REC_HIDE_CABINET_0_DOOR_HANDLE", (0.02, 0.06, 0.14), (0.40, -0.03, 0), coll, mats["galv"], bevel_width=0.003)
    door_handle.parent = hinge
    door_handle.location = (0.40, -0.03, 0)
    parts.append(door_handle)

    # etiqueta
    parts.append(box("REC_HIDE_CABINET_0_LABEL", (0.26, 0.004, 0.05), (0, y1 + 0.002 - cy, 1.94), coll, mats["label"]))

    for p in parts:
        if p.parent is None:
            attach(p, root)

    tag(root, hide_spot=True, hide_capacity=1, hide_type="cabinet",
        interior_width_m=round(x1 - x0 - 2 * wall, 3),
        interior_depth_m=round(y1 - y0 - wall, 3),
        interior_height_m=round(z1 - z0 - 0.06, 3),
        enter_offset_z=-1.0, cover="door", concealment=0.75,
        exported_name="hide_cabinet")
    tag(hinge, interactive="door", door_type="hinge", open_angle_deg=28.0,
        door_state="ajar", hide_spot_door=True)
    return root


# --------------------------------------------------------------------------
# puerta de acceso operable
# --------------------------------------------------------------------------

def build_operable_door(coll):
    """Convierte la hoja existente en una hoja con pivote de bisagra."""
    names = [
        "NEXUS_V05_RECEPCION_DOOR_LEAF",
        "NEXUS_V05_RECEPCION_DOOR_GLASS",
        "NEXUS_V05_RECEPCION_DOOR_HANDLE",
    ]
    leaf = bpy.data.objects.get(names[0])
    if leaf is None:
        print("AVISO: no existe la hoja de la puerta, se omite el pivote")
        return None

    old = bpy.data.objects.get(PREFIX + "DOOR_PIVOT")
    if old:
        bpy.data.objects.remove(old, do_unlink=True)

    # subir la hoja 70 mm: estaba enterrada 90 mm bajo el piso
    for n in names:
        obj = bpy.data.objects.get(n)
        if obj:
            obj.location.z += 0.07

    hinge_x = -12.81
    pivot = bpy.data.objects.new(PREFIX + "DOOR_PIVOT", None)
    pivot.empty_display_type = "ARROWS"
    pivot.empty_display_size = 0.3
    coll.objects.link(pivot)
    pivot.location = (hinge_x, 1.705, FLOOR_TOP)
    pivot.rotation_mode = "XYZ"

    for n in names:
        obj = bpy.data.objects.get(n)
        if obj:
            parent_keep_transform(obj, pivot)

    tag(pivot, interactive="door", door_type="swing", door_state="closed",
        open_angle_deg=95.0, swing_direction="inward", hinge_side="west",
        weight_kg=85.0, requires_hands=1, blocks_light=True,
        exported_name="door_reception_main")
    return pivot


# --------------------------------------------------------------------------

def main():
    coll = ensure_collection()
    mats = build_materials()
    built = [
        build_case(mats, coll),
        build_sample(mats, coll),
        build_crate(mats, coll),
        build_docs(mats, coll),
        build_drive(mats, coll),
        build_noise_trap(mats, coll),
        build_hide_cabinet(mats, coll),
        build_operable_door(coll),
    ]
    built = [b for b in built if b is not None]
    print("REC_PLAY_OBJECTS", len(coll.all_objects))
    print("REC_PLAY_ROOTS", len(built))
    for b in built:
        print("  ", b.name, b.type, [k for k in b.keys() if k != "_RNA_UI"][:8])


main()
