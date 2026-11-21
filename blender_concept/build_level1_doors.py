import bpy
import math
import os
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
OUT_BLEND = ROOT + "/blender_concept/LEVEL1_DOORS.blend"
OUT_GLB = ROOT + "/assets/models/fm/doors/level1_doors.glb"
os.makedirs(os.path.dirname(OUT_GLB), exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0

COLL = bpy.data.collections.new("LEVEL1_DOORS")
scene.collection.children.link(COLL)

W = 1.58
H = 3.00
PARTS = []          # (kind, group, obj)
KINDS = {}
TEX = ROOT + "/assets/texturas/"
GEN = ROOT + "/assets/art/fm/generated/"


# ------------------------------------------------------------------ materials

def load_img(path, non_color=False):
    img = bpy.data.images.load(path, check_existing=True)
    if non_color:
        img.colorspace_settings.name = 'Non-Color'
    return img


def tex_mat(name, diff, normal, rough, metallic, base=(1, 1, 1, 1), normal_strength=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = base
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = 1.0
    if diff:
        t = nt.nodes.new('ShaderNodeTexImage')
        t.image = load_img(diff)
        t.location = (-700, 300)
        nt.links.new(t.outputs['Color'], bsdf.inputs['Base Color'])
    if rough:
        t = nt.nodes.new('ShaderNodeTexImage')
        t.image = load_img(rough, True)
        t.location = (-700, 0)
        nt.links.new(t.outputs['Color'], bsdf.inputs['Roughness'])
    if normal:
        t = nt.nodes.new('ShaderNodeTexImage')
        t.image = load_img(normal, True)
        t.location = (-700, -300)
        nm = nt.nodes.new('ShaderNodeNormalMap')
        nm.inputs['Strength'].default_value = normal_strength
        nm.location = (-350, -300)
        nt.links.new(t.outputs['Color'], nm.inputs['Color'])
        nt.links.new(nm.outputs['Normal'], bsdf.inputs['Normal'])
    return mat


def solid_mat(name, color, metallic, roughness, emission=None, emission_strength=0.0, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    if emission:
        bsdf.inputs['Emission Color'].default_value = (*emission, 1.0)
        bsdf.inputs['Emission Strength'].default_value = emission_strength
    if alpha < 1.0:
        bsdf.inputs['Alpha'].default_value = alpha
        mat.surface_render_method = 'BLENDED'
    return mat


MAT_BRUSH = solid_mat("DOOR_Brush", (0.46, 0.53, 0.58), 0.92, 0.30)
MAT_STEEL = tex_mat("DOOR_Steel",
    TEX + "Metal y oxidacion/rusty_metal_sheet_2k.blend/textures/rusty_metal_sheet_diff_2k.jpg",
    GEN + "gen_rusty_metal_sheet_normal.png", GEN + "gen_rusty_metal_sheet_rough.png",
    0.82, base=(0.72, 0.77, 0.82, 1))
MAT_GREEN = tex_mat("DOOR_Green",
    TEX + "Metal y oxidacion/green_metal_rust_2k.blend/textures/green_metal_rust_diff_2k.jpg",
    GEN + "gen_green_metal_rust_normal.png",
    TEX + "Metal y oxidacion/green_metal_rust_2k.blend/textures/green_metal_rust_rough_2k.jpg",
    0.12, base=(0.62, 0.78, 0.70, 1))
MAT_RUST = tex_mat("DOOR_Rust",
    TEX + "Metal y oxidacion/rusty_painted_metal_2k.blend/textures/rusty_painted_metal_diff_2k.jpg",
    None, None, 0.35, base=(0.92, 0.58, 0.38, 1))
MAT_BLUE = solid_mat("DOOR_Blue", (0.075, 0.125, 0.145), 0.55, 0.42)
MAT_PALE = solid_mat("DOOR_Pale", (0.070, 0.100, 0.085), 0.15, 0.72)
MAT_DARK = solid_mat("DOOR_DarkSteel", (0.032, 0.040, 0.044), 0.82, 0.44)
MAT_BLACK = solid_mat("DOOR_Black", (0.012, 0.015, 0.016), 0.35, 0.68)
MAT_INSET = solid_mat("DOOR_Inset", (0.030, 0.038, 0.038), 0.10, 0.88)
MAT_RUBBER = solid_mat("DOOR_Rubber", (0.020, 0.024, 0.026), 0.0, 0.90)
MAT_GLASS = solid_mat("DOOR_Glass", (0.06, 0.11, 0.13), 0.0, 0.16, alpha=0.30)
MAT_FROST = solid_mat("DOOR_Frost", (0.18, 0.24, 0.22), 0.0, 0.86, alpha=1.0)
MAT_HAZARD = solid_mat("DOOR_Hazard", (0.78, 0.42, 0.015), 0.0, 0.58)
MAT_LABEL = solid_mat("DOOR_Label", (0.58, 0.62, 0.62), 0.0, 0.62)
MAT_STATUS = solid_mat("DOOR_Status", (0.05, 0.05, 0.05), 0.0, 0.35,
    emission=(0.85, 0.90, 0.90), emission_strength=1.8)
MAT_CYAN = solid_mat("DOOR_Cyan", (0.02, 0.10, 0.12), 0.0, 0.30,
    emission=(0.15, 0.72, 0.88), emission_strength=2.2)
MAT_RED = solid_mat("DOOR_Red", (0.10, 0.015, 0.012), 0.0, 0.40,
    emission=(0.95, 0.10, 0.05), emission_strength=1.8)
MAT_AMBER = solid_mat("DOOR_Amber", (0.12, 0.045, 0.005), 0.0, 0.42,
    emission=(1.0, 0.32, 0.04), emission_strength=2.0)


# ------------------------------------------------------------------ helpers

def link(obj):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    COLL.objects.link(obj)


def apply_scale(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)


def finish(obj, kind, group, mat, bevel=0.008, unwrap=True):
    link(obj)
    obj.data.materials.append(mat)
    if unwrap:
        if not obj.data.uv_layers:
            obj.data.uv_layers.new(name="UVMap")
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        try:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.smart_project(angle_limit=math.radians(65), island_margin=0.02)
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except Exception:
                pass
    if bevel > 0:
        m = obj.modifiers.new("Bevel", 'BEVEL')
        m.width = bevel
        m.segments = 2
        m.limit_method = 'ANGLE'
        m.angle_limit = math.radians(40)
        m.harden_normals = True
        n = obj.modifiers.new("Weighted", 'WEIGHTED_NORMAL')
        n.keep_sharp = True
    PARTS.append((kind, group, obj))
    KINDS.setdefault(kind, set()).add(group)
    return obj


def box(kind, group, name, center, size, mat, bevel=0.008, unwrap=True):
    bx, by, bz = center[0], -center[2], center[1]
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bx, by, bz))
    obj = bpy.context.active_object
    obj.name = "%s_%s_%s" % (kind, group, name)
    obj.dimensions = (size[0], size[2], size[1])
    apply_scale(obj)
    return finish(obj, kind, group, mat, bevel, unwrap)


def cyl(kind, group, name, center, radius, depth, axis, mat, segments=16, bevel=0.0):
    bx, by, bz = center[0], -center[2], center[1]
    if axis == 'x':
        rot = (0, math.pi * 0.5, 0)
    elif axis == 'z':
        rot = (math.pi * 0.5, 0, 0)
    else:
        rot = (0, 0, 0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=segments, radius=radius, depth=depth,
                                        location=(bx, by, bz), rotation=rot)
    obj = bpy.context.active_object
    obj.name = "%s_%s_%s" % (kind, group, name)
    return finish(obj, kind, group, mat, bevel, False)


def bolt(kind, group, name, x, y, z, mat=MAT_DARK, r=0.014, depth=0.030):
    return cyl(kind, group, name, (x, y, z), r, depth, 'z', mat, 8)


def empty(name, parent=None, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    COLL.objects.link(e)
    e.empty_display_size = 0.10
    if parent is not None:
        e.parent = parent
        e.matrix_parent_inverse = parent.matrix_world.inverted()
        e.location = loc
    else:
        e.location = loc
    return e


# ------------------------------------------------------------------ geometry

def build_frame(kind, style, slide=False):
    body = style["body"]
    dark = MAT_DARK
    # Laterales.
    box(kind, "Frame", "PostL", (-0.045, H * 0.5, 0.0), (0.09, H + 0.16, 0.22), body, 0.010)
    box(kind, "Frame", "PostR", (W + 0.045, H * 0.5, 0.0), (0.09, H + 0.16, 0.22), body, 0.010)
    box(kind, "Frame", "Header", (W * 0.5, H + 0.07, 0.0), (W + 0.18, 0.14, 0.22), body, 0.010)
    # Junta interior clara y burlete.
    for x in (0.004, W - 0.004):
        box(kind, "Frame", "InnerTrim", (x, H * 0.5, 0.108), (0.020, H - 0.02, 0.018), MAT_STEEL, 0.002)
        box(kind, "Frame", "Seal", (x, H * 0.5, 0.0), (0.014, H - 0.04, 0.19), MAT_RUBBER, 0.002)
    # Umbral y placa de suelo.
    box(kind, "Frame", "Threshold", (W * 0.5, 0.018, 0.0), (W + 0.10, 0.036, 0.30), MAT_STEEL, 0.006)
    box(kind, "Frame", "ThresholdGrate", (W * 0.5, 0.040, 0.0), (W - 0.10, 0.010, 0.24), MAT_DARK, 0.0)
    # Placas de anclaje y tornillos.
    for x in (-0.045, W + 0.045):
        for y in (0.36, H * 0.5, H - 0.30):
            box(kind, "Frame", "BoltPlate", (x, y, 0.108), (0.15, 0.16, 0.018), MAT_STEEL, 0.004)
            for dx, dy in ((-0.045, -0.045), (0.045, -0.045), (-0.045, 0.045), (0.045, 0.045)):
                bolt(kind, "Frame", "Bolt", x + dx, y + dy, 0.122)
    # Placa de identificacion.
    box(kind, "Frame", "LabelPlate", (W * 0.5, H + 0.20, 0.115), (0.92, 0.15, 0.030), MAT_DARK, 0.004)
    box(kind, "Frame", "LabelInset", (W * 0.5, H + 0.20, 0.134), (0.86, 0.11, 0.010), MAT_LABEL, 0.002)
    # Riel superior para correderas.
    if slide:
        box(kind, "Frame", "Track", (W * 0.5, H + 0.18, 0.0), (W + 0.55, 0.12, 0.18), MAT_STEEL, 0.008)
        for x in (W * 0.25, W * 0.75):
            box(kind, "Frame", "TrackBrake", (x, H + 0.10, 0.0), (0.10, 0.10, 0.22), MAT_DARK, 0.004)
    # Rejilla de ventilacion inferior en el marco (mantenimiento).
    if style.get("vent"):
        vx = W + 0.045
        box(kind, "Frame", "VentFrame", (vx, 0.46, 0.118), (0.15, 0.30, 0.022), MAT_DARK, 0.003)
        for i in range(5):
            box(kind, "Frame", "VentSlat", (vx, 0.36 + i * 0.05, 0.133), (0.12, 0.012, 0.010), MAT_STEEL, 0.001)


def build_status(kind, style, y=None):
    y = H + 0.10 if y is None else y
    box(kind, "Status", "StatusHousing", (W * 0.5, y, 0.115), (0.26, 0.08, 0.045), MAT_DARK, 0.004)
    box(kind, "Status", "StatusLight", (W * 0.5, y, 0.142), (0.20, 0.045, 0.014), MAT_STATUS, 0.002)
    # Tira de acento bajo la placa.
    box(kind, "Frame", "AccentStrip", (W * 0.5, H + 0.12, 0.125), (0.78, 0.012, 0.008), style["accent"], 0.0)


def build_leaf(kind, group, x0, x1, style, hinge_x, free_x, window=True, grille=False,
               braces=False, glass_leaf=False, slide=False):
    body = style["body"]
    inset = style["inset"]
    thick = style.get("thick", 0.090)
    cx = (x0 + x1) * 0.5
    w = x1 - x0

    if glass_leaf:
        # Hoja de cristal con bastidor metálico.
        box(kind, group, "TopRail", (cx, H - 0.12, 0.0), (w, 0.14, thick + 0.02), body, 0.008)
        box(kind, group, "BotRail", (cx, 0.20, 0.0), (w, 0.22, thick + 0.02), body, 0.008)
        box(kind, group, "StileL", (x0 + 0.045, H * 0.5, 0.0), (0.075, H - 0.04, thick + 0.02), body, 0.006)
        box(kind, group, "StileR", (x1 - 0.045, H * 0.5, 0.0), (0.075, H - 0.04, thick + 0.02), body, 0.006)
        box(kind, group, "Glass", (cx, H * 0.52, 0.0), (w - 0.12, H - 0.42, 0.016), MAT_GLASS, 0.0, False)
        # Bandas de seguridad a media altura.
        for z in (1, -1):
            box(kind, group, "FrostBand", (cx, 1.12, z * (thick * 0.5 + 0.010)),
                (w - 0.16, 0.18, 0.008), MAT_FROST, 0.001, False)
    else:
        box(kind, group, "Slab", (cx, H * 0.5, 0.0), (w, H - 0.08, thick), body, 0.010)
        for z in (1, -1):
            # Panel hundido con marco.
            box(kind, group, "Panel", (cx, H * 0.56, z * (thick * 0.5 + 0.008)),
                (w * 0.68, H * 0.46, 0.020), inset, 0.006)
            box(kind, group, "PanelTop", (cx, H * 0.80, z * (thick * 0.5 + 0.014)),
                (w * 0.74, 0.035, 0.018), MAT_STEEL, 0.002)
            box(kind, group, "PanelBot", (cx, H * 0.33, z * (thick * 0.5 + 0.014)),
                (w * 0.74, 0.035, 0.018), MAT_STEEL, 0.002)
            # Costillas verticales.
            for rx in (cx - w * 0.27, cx + w * 0.27):
                box(kind, group, "Rib", (rx, H * 0.56, z * (thick * 0.5 + 0.022)),
                    (0.045, H * 0.48, 0.012), MAT_STEEL, 0.002)
        # Placa anti-golpes inferior.
        box(kind, group, "KickPlate", (cx, 0.27, 0.0), (w * 0.86, 0.28, thick + 0.020), MAT_STEEL, 0.006)
        if style.get("hazard"):
            for i in range(7):
                sx = x0 + 0.08 + i * (w - 0.16) / 6.0
                box(kind, group, "HazardStripe", (sx, 0.105, thick * 0.5 + 0.014),
                    (0.065, 0.085, 0.010), MAT_HAZARD if i % 2 == 0 else MAT_BLACK, 0.001)
                box(kind, group, "HazardStripeB", (sx, 0.105, -thick * 0.5 - 0.014),
                    (0.065, 0.085, 0.010), MAT_HAZARD if i % 2 == 0 else MAT_BLACK, 0.001)

    if window:
        wy = H * 0.74
        win_w = w * (0.30 if style.get("small_window") else 0.46)
        win_h = H * (0.10 if style.get("small_window") else 0.15)
        box(kind, group, "WindowFrame", (cx, wy, 0.0), (win_w, win_h, thick + 0.024), MAT_DARK, 0.006)
        wmat = style.get("window_mat", MAT_GLASS)
        box(kind, group, "WindowGlass", (cx, wy, 0.0), (win_w * 0.80, win_h * 0.78, 0.014), wmat, 0.0, False)
        if grille:
            for z in (1, -1):
                for i in range(7):
                    gx = cx - win_w * 0.38 + i * (win_w * 0.76 / 6.0)
                    box(kind, group, "GrilleV", (gx, wy, z * (thick * 0.5 + 0.024)),
                        (0.020, win_h * 0.78, 0.020), MAT_STEEL, 0.001)
                for i in range(5):
                    gy = wy - win_h * 0.36 + i * (win_h * 0.72 / 4.0)
                    box(kind, group, "GrilleH", (cx, gy, z * (thick * 0.5 + 0.024)),
                        (win_w * 0.80, 0.020, 0.020), MAT_STEEL, 0.001)
        elif style.get("bars"):
            for z in (1, -1):
                for i in range(3):
                    bx = cx - win_w * 0.25 + i * win_w * 0.25
                    box(kind, group, "WindowBar", (bx, wy, z * (thick * 0.5 + 0.018)),
                        (0.018, win_h * 0.85, 0.018), MAT_STEEL, 0.001)

    if braces:
        # Refuerzos diagonales en la cara exterior.
        for z in (1, -1):
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, H * 0.55, z * (thick * 0.5 + 0.030)))
            obj = bpy.context.active_object
            obj.name = "%s_%s_Brace" % (kind, group)
            obj.dimensions = (math.sqrt((H * 0.62) ** 2 + w ** 2), 0.020, 0.055)
            apply_scale(obj)
            obj.rotation_euler[1] = (-1.0 if z < 0 else 1.0) * math.atan2(w, H * 0.62)
            finish(obj, kind, group, MAT_STEEL, 0.003)

    # Manilla/tirador en el borde libre.
    for z in (1, -1):
        cxh = free_x
        pz = z * (thick * 0.5 + 0.045)
        cyl(kind, group, "Rosette", (cxh, 1.08, pz), 0.055, 0.022, 'z', MAT_STEEL, 16, 0.003)
        box(kind, group, "Lever", (cxh - math.copysign(0.10, free_x - hinge_x), 1.08, z * (thick * 0.5 + 0.060)),
            (0.20, 0.030, 0.030), MAT_STEEL, 0.004)
        # Cilindro de cerradura.
        cyl(kind, group, "Lock", (cxh, 0.98, pz), 0.022, 0.020, 'z', MAT_DARK, 12, 0.002)

    if slide:
        # Guias y rodillos.
        for z in (1, -1):
            box(kind, group, "SlideRail", (cx, 0.10, z * 0.16), (w * 0.92, 0.045, 0.035), MAT_STEEL, 0.003)
        for x in (x0 + 0.10, x1 - 0.10):
            cyl(kind, group, "TopRoller", (x, H - 0.05, 0.0), 0.035, 0.12, 'z', MAT_DARK, 12, 0.002)
    else:
        # Bisagras.
        for y in (0.38, H * 0.5, H - 0.38):
            cyl(kind, group, "Hinge", (hinge_x, y, 0.0), 0.038, 0.19, 'y', MAT_STEEL, 12, 0.003)
            cyl(kind, group, "HingePin", (hinge_x, y, 0.0), 0.016, 0.22, 'y', MAT_DARK, 8, 0.0)

    # Burlete en el borde libre.
    box(kind, group, "EdgeSeal", (free_x, H * 0.5, 0.0), (0.018, H - 0.10, thick + 0.010), MAT_RUBBER, 0.002)


def build_keypad(kind, style, x, y, z, label_text=None):
    box(kind, "Keypad", "Body", (x, y, z), (0.20, 0.30, 0.045), MAT_DARK, 0.005)
    box(kind, "Keypad", "Face", (x, y, z + 0.030), (0.17, 0.26, 0.018), MAT_BLACK, 0.003)
    box(kind, "Keypad", "Display", (x, y + 0.095, z + 0.043), (0.12, 0.035, 0.008), MAT_CYAN, 0.001, False)
    for row in range(4):
        for col in range(3):
            bx = x - 0.052 + col * 0.052
            by = y + 0.045 - row * 0.042
            box(kind, "Keypad", "Btn", (bx, by, z + 0.046), (0.034, 0.028, 0.014), MAT_STEEL, 0.003)
    box(kind, "Keypad", "CardSlot", (x, y - 0.085, z + 0.044), (0.10, 0.012, 0.010), MAT_BLACK, 0.001)
    box(kind, "Keypad", "Status", (x + 0.062, y + 0.105, z + 0.046), (0.014, 0.014, 0.010), MAT_STATUS, 0.001, False)
    box(kind, "Keypad", "Label", (x, y - 0.125, z + 0.040), (0.13, 0.028, 0.006), MAT_LABEL, 0.001, False)


def build_sensor(kind, style):
    y = H + 0.22
    box(kind, "Sensor", "Housing", (W * 0.5, y, 0.13), (0.38, 0.09, 0.12), MAT_DARK, 0.006)
    box(kind, "Sensor", "LensCyan", (W * 0.5 - 0.11, y - 0.035, 0.195), (0.07, 0.025, 0.012), MAT_CYAN, 0.001, False)
    box(kind, "Sensor", "LensRed", (W * 0.5 + 0.11, y - 0.035, 0.195), (0.05, 0.025, 0.012), MAT_RED, 0.001, False)


def build_manual_release(kind, style, x, y, z, side=-1.0):
    box(kind, "Manual", "Plate", (x, y, z), (0.18, 0.26, 0.030), MAT_STEEL, 0.004)
    box(kind, "Manual", "Handle", (x, y - 0.02, z + side * 0.055), (0.10, 0.16, 0.045), MAT_RED, 0.006)
    box(kind, "Manual", "Grip", (x, y - 0.02, z + side * 0.085), (0.065, 0.10, 0.025), MAT_BLACK, 0.003)
    box(kind, "Manual", "Label", (x, y + 0.16, z + side * 0.020), (0.12, 0.035, 0.006), MAT_HAZARD, 0.001, False)


# ------------------------------------------------------------------ six doors

STYLES = {
    "RECEPCION": dict(body=MAT_BRUSH, inset=MAT_INSET, accent=MAT_CYAN, thick=0.075, glass=True, bars=False),
    "SEGURIDAD": dict(body=MAT_GREEN, inset=MAT_INSET, accent=MAT_RED, thick=0.130, bars=True),
    "CONTROL": dict(body=MAT_BLUE, inset=MAT_INSET, accent=MAT_CYAN, thick=0.095),
    "ALMACEN": dict(body=MAT_RUST, inset=MAT_INSET, accent=MAT_HAZARD, thick=0.120, hazard=True),
    "VESTUARIOS": dict(body=MAT_GREEN, inset=MAT_INSET, accent=MAT_GREEN, thick=0.070, small_window=True),
    "MANTENIMIENTO": dict(body=MAT_DARK, inset=MAT_INSET, accent=MAT_RED, thick=0.110, vent=True, window_mat=MAT_BLACK, small_window=True),
}

# Recepcion: corredera automatica de dos hojas de cristal.
k = "RECEPCION"; s = STYLES[k]
build_frame(k, s, slide=True)
build_leaf(k, "LeafA", 0.015, W * 0.5 - 0.006, s, 0.0, W * 0.5 - 0.006, window=False, glass_leaf=True, slide=True)
build_leaf(k, "LeafB", W * 0.5 + 0.006, W - 0.015, s, W, W * 0.5 + 0.006, window=False, glass_leaf=True, slide=True)
build_status(k, s)
build_sensor(k, s)

# Seguridad: blindada de una hoja, teclado y lector.
k = "SEGURIDAD"; s = STYLES[k]
build_frame(k, s)
build_leaf(k, "LeafA", 0.015, W - 0.015, s, 0.0, W - 0.015, window=True, grille=False)
build_status(k, s)
build_keypad(k, s, W + 0.30, 1.36, 0.105)

# Control: doble hoja con apertura secuencial y mecanismo central.
k = "CONTROL"; s = STYLES[k]
build_frame(k, s)
build_leaf(k, "LeafA", 0.010, W * 0.5 - 0.006, s, 0.0, W * 0.5 - 0.006, window=True)
build_leaf(k, "LeafB", W * 0.5 + 0.006, W - 0.010, s, W, W * 0.5 + 0.006, window=True)
build_status(k, s)
box(k, "Frame", "SeqBox", (W * 0.5, 1.18, 0.125), (0.24, 0.34, 0.070), MAT_STEEL, 0.006)
box(k, "Frame", "SeqDisplay", (W * 0.5, 1.26, 0.166), (0.15, 0.10, 0.018), MAT_CYAN, 0.002, False)
box(k, "Frame", "SeqLever", (W * 0.5, 1.06, 0.175), (0.10, 0.055, 0.040), MAT_RED, 0.004)

# Almacen: corredera pesada de dos hojas con refuerzos y franjas.
k = "ALMACEN"; s = STYLES[k]
build_frame(k, s, slide=True)
build_leaf(k, "LeafA", 0.015, W * 0.5 - 0.006, s, 0.0, W * 0.5 - 0.006, window=False, braces=True, slide=True)
build_leaf(k, "LeafB", W * 0.5 + 0.006, W - 0.015, s, W, W * 0.5 + 0.006, window=False, braces=True, slide=True)
build_status(k, s)

# Vestuarios: hoja ligera con panel esmerilado y rejilla.
k = "VESTUARIOS"; s = STYLES[k]
build_frame(k, s)
build_leaf(k, "LeafA", 0.015, W - 0.015, s, 0.0, W - 0.015, window=True, grille=False)
build_status(k, s)
box(k, "LeafA", "FrostPanel", (W * 0.5, 1.95, 0.048), (0.64, 0.78, 0.010), MAT_FROST, 0.002, False)
for i in range(5):
    box(k, "LeafA", "VentSlat", (W * 0.5, 0.72 + i * 0.045, 0.052), (0.46, 0.020, 0.012), MAT_DARK, 0.001)

# Mantenimiento: hoja metalica con rejilla y liberacion manual.
k = "MANTENIMIENTO"; s = STYLES[k]
build_frame(k, s)
build_leaf(k, "LeafA", 0.015, W - 0.015, s, 0.0, W - 0.015, window=True, grille=True)
build_status(k, s)
build_manual_release(k, s, W + 0.28, 1.18, -0.105, -1.0)


# ------------------------------------------------------------------ merge per group/material

for kind, group, obj in list(PARTS):
    if obj.type != 'MESH':
        continue
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    try:
        bpy.ops.object.convert(target='MESH')
    except Exception:
        pass

by_group = {}
for kind, group, obj in PARTS:
    if obj.type != 'MESH' or not obj.data.materials:
        continue
    by_group.setdefault((kind, group), []).append(obj)

ROOT_EMPTIES = {}
GROUP_EMPTIES = {}
MERGED = []

for kind in sorted(KINDS.keys()):
    root = empty("DOOR_KIT_%s" % kind)
    ROOT_EMPTIES[kind] = root
    for group in sorted(KINDS[kind]):
        objs = by_group.get((kind, group), [])
        if not objs:
            continue
        pivot = (0.0, 0.0, 0.0)
        if group == "LeafB":
            pivot = (W, 0.0, 0.0)
        if group in ("LeafA", "LeafB"):
            ge = empty(group, root, (pivot[0], -pivot[2], pivot[1]))
            GROUP_EMPTIES[(kind, group)] = ge
        elif group in ("Frame", "Keypad", "Sensor", "Manual"):
            ge = empty(group, root, (0, 0, 0))
            GROUP_EMPTIES[(kind, group)] = ge
        else:
            ge = None

        mats = {}
        for obj in objs:
            mats.setdefault(obj.data.materials[0].name, []).append(obj)

        for mat_name, mat_objs in sorted(mats.items()):
            bpy.ops.object.select_all(action='DESELECT')
            for obj in mat_objs:
                obj.select_set(True)
            bpy.context.view_layer.objects.active = mat_objs[0]
            if len(mat_objs) > 1:
                bpy.ops.object.join()
            joined = bpy.context.active_object
            joined.name = "%s_%s_%s" % (kind, group, mat_name.replace("DOOR_", ""))
            if ge is not None:
                bpy.context.scene.cursor.location = (pivot[0], -pivot[2], pivot[1])
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
                mw = joined.matrix_world.copy()
                joined.parent = ge
                joined.matrix_parent_inverse = ge.matrix_world.inverted()
                joined.matrix_world = mw
            else:
                mw = joined.matrix_world.copy()
                joined.parent = root
                joined.matrix_parent_inverse = root.matrix_world.inverted()
                joined.matrix_world = mw
            MERGED.append(joined)

# Anclas de rotulo para Label3D.
for kind in sorted(KINDS.keys()):
    a = empty("LabelAnchor_%s" % kind, ROOT_EMPTIES[kind], (W * 0.5, -0.155, H + 0.20))
    a["door_label"] = kind

# ------------------------------------------------------------------ save/export

scene.render.resolution_x = 1280
scene.render.resolution_y = 720
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)

bpy.ops.object.select_all(action='DESELECT')
for obj in COLL.all_objects:
    obj.select_set(True)
bpy.context.view_layer.objects.active = ROOT_EMPTIES[sorted(ROOT_EMPTIES.keys())[0]]
bpy.ops.export_scene.gltf(
    filepath=OUT_GLB,
    export_format='GLB',
    use_selection=True,
    export_apply=True,
    export_yup=True,
    export_image_format='WEBP',
    export_image_quality=88,
    export_cameras=False,
    export_lights=False,
    export_animations=False,
    export_extras=True,
)
print("DOORS_SAVED", OUT_BLEND)
print("DOORS_GLB", OUT_GLB, os.path.getsize(OUT_GLB))
print("DOORS_SOURCE", len(PARTS))
print("DOORS_MERGED", len(MERGED))
print("DOORS_ROOTS", sorted(ROOT_EMPTIES.keys()))
