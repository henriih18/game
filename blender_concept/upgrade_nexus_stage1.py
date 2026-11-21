"""Stage 1 upgrade for the open NEXUS complex in Blender.

Adds scene organization, PBR materials, corridor ceilings/lights, door leaves,
room lighting and presentation cameras. Does not delete existing geometry.
Designed to run through Blender MCP via exec(compile(...)).
"""
import bpy
import os
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
TEX = os.path.join(ROOT, "assets", "art", "fm")
CREATED_PREFIX = "NEXUS_UP_"
SCENE = bpy.context.scene


def ensure_collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        SCENE.collection.children.link(col)
    return col


COL_STRUCT = ensure_collection("01_STRUCTURE")
COL_CIRC = ensure_collection("02_CIRCULATION")
COL_FURN = ensure_collection("03_DECOR_FURNITURE")
COL_TECH = ensure_collection("04_DECOR_TECH")
COL_PIPES = ensure_collection("05_PIPES_CABLES")
COL_DAMAGE = ensure_collection("06_DISASTER_DAMAGE")
COL_STORY = ensure_collection("07_STORYTELLING")
COL_LIGHT = ensure_collection("08_LIGHTING")
COL_CAMS = ensure_collection("09_CAMERAS")
COL_CREATURES = ensure_collection("10_CREATURES")


def move_to(obj, col):
    for c in list(obj.users_collection):
        if c != col:
            try:
                c.objects.unlink(obj)
            except RuntimeError:
                pass
    if obj.name not in col.objects:
        col.objects.link(obj)


def classify_all():
    for obj in list(bpy.data.objects):
        n = obj.name.upper()
        if obj.type == "CAMERA":
            move_to(obj, COL_CAMS)
        elif obj.type == "LIGHT":
            move_to(obj, COL_LIGHT)
        elif obj.type == "FONT":
            move_to(obj, COL_TECH)
        elif obj.type == "MESH":
            if n.startswith("CORRIDOR_") or n.startswith("STAIR_") or "DOOR_FRAME" in n:
                move_to(obj, COL_CIRC)
            elif n.startswith("SIGN_") or "SIGN_PANEL" in n:
                move_to(obj, COL_TECH)
            elif n.endswith("_LIGHT_HOUSING") or n.endswith("_LIGHT_LAMP"):
                move_to(obj, COL_LIGHT)
            elif any(k in n for k in ("PIPE", "CABLE", "CONDUIT", "VENT", "DUCT", "TRAY", "JUNCTION")):
                move_to(obj, COL_PIPES)
            else:
                move_to(obj, COL_STRUCT)


# ---------------------------------------------------------------- materials
def load_image(name, non_color=False):
    path = os.path.join(TEX, name)
    if not os.path.exists(path):
        return None
    img = bpy.data.images.get(name)
    if img is None:
        img = bpy.data.images.load(path, check_existing=True)
    if non_color:
        try:
            img.colorspace_settings.name = "Non-Color"
        except Exception:
            pass
    return img


def clear_node_tree(mat):
    if not mat.use_nodes:
        mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (520, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (220, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return nt, bsdf


def add_texture_chain(nt, bsdf, albedo_name, rough_name, normal_name, scale=0.55, tint=None):
    tex = nt.nodes.new("ShaderNodeTexCoord")
    tex.location = (-900, 0)
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.location = (-700, 0)
    mapping.inputs["Scale"].default_value = (scale, scale, scale)
    nt.links.new(tex.outputs["Object"], mapping.inputs["Vector"])

    def img_node(name, y, non_color=False):
        img = load_image(name, non_color)
        if img is None:
            return None
        n = nt.nodes.new("ShaderNodeTexImage")
        n.image = img
        n.location = (-480, y)
        n.extension = "REPEAT"
        nt.links.new(mapping.outputs["Vector"], n.inputs["Vector"])
        return n

    alb = img_node(albedo_name, 260)
    if alb is not None:
        if tint is None:
            nt.links.new(alb.outputs["Color"], bsdf.inputs["Base Color"])
        else:
            mix = nt.nodes.new("ShaderNodeMixRGB")
            mix.blend_type = "MULTIPLY"
            mix.inputs["Fac"].default_value = 1.0
            mix.inputs["Color2"].default_value = tint
            mix.location = (-220, 260)
            nt.links.new(alb.outputs["Color"], mix.inputs["Color1"])
            nt.links.new(mix.outputs["Color"], bsdf.inputs["Base Color"])

    rough = img_node(rough_name, 0, True)
    if rough is not None:
        nt.links.new(rough.outputs["Color"], bsdf.inputs["Roughness"])

    normal = img_node(normal_name, -260, True)
    if normal is not None:
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nm.location = (-220, -260)
        nm.inputs["Strength"].default_value = 1.0
        nt.links.new(normal.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])


def make_emissive(mat, color, strength=3.0):
    nt, bsdf = clear_node_tree(mat)
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.35
    bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
    bsdf.inputs["Emission Strength"].default_value = strength
    return mat


def update_materials():
    mats = bpy.data.materials
    # Textured architectural surfaces.
    for name, alb, rough, normal, metallic, scale, tint in [
        ("NEXUS_Concrete", "concrete_wall_albedo.png", "concrete_wall_roughness.png", "concrete_wall_normal.png", 0.0, 0.65, None),
        ("NEXUS_Concrete_Dark", "concrete_wall_albedo.png", "concrete_wall_roughness.png", "concrete_wall_normal.png", 0.0, 0.55, (0.30, 0.34, 0.34, 1.0)),
        ("NEXUS_Painted_Metal", "metal_panel_albedo.png", "metal_panel_roughness.png", "metal_panel_normal.png", 0.10, 0.75, None),
        ("NEXUS_Steel", "metal_panel_albedo.png", "metal_panel_roughness.png", "metal_panel_normal.png", 1.0, 0.85, (0.70, 0.76, 0.78, 1.0)),
        ("NEXUS_Rusted_Metal", "rust_albedo.png", "rust_roughness.png", "rust_normal.png", 0.25, 0.60, None),
        ("NEXUS_OffWhite", "concrete_wall_albedo.png", "concrete_wall_roughness.png", "concrete_wall_normal.png", 0.0, 0.80, (1.25, 1.22, 1.15, 1.0)),
        ("NEXUS_Clinical", "concrete_wall_albedo.png", "concrete_wall_roughness.png", "concrete_wall_normal.png", 0.0, 0.80, (0.85, 1.0, 0.95, 1.0)),
    ]:
        mat = mats.get(name)
        if mat is None:
            continue
        nt, bsdf = clear_node_tree(mat)
        bsdf.inputs["Metallic"].default_value = metallic
        add_texture_chain(nt, bsdf, alb, rough, normal, scale, tint)

    for name, color, strength in [
        ("NEXUS_Red", (1.0, 0.025, 0.012), 3.0),
        ("NEXUS_Amber", (1.0, 0.38, 0.04), 2.8),
        ("NEXUS_Green", (0.06, 1.0, 0.22), 2.6),
        ("NEXUS_CorridorLight", (0.62, 0.86, 1.0), 3.5),
    ]:
        mat = mats.get(name) or mats.new(name)
        make_emissive(mat, color, strength)

    screen = mats.get("NEXUS_Screen")
    if screen is not None:
        nt, bsdf = clear_node_tree(screen)
        bsdf.inputs["Base Color"].default_value = (0.01, 0.08, 0.075, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.25
        img = load_image("screen_scan.png")
        if img is not None:
            t = nt.nodes.new("ShaderNodeTexImage")
            t.image = img
            t.location = (-300, 0)
            nt.links.new(t.outputs["Color"], bsdf.inputs["Emission Color"])
            bsdf.inputs["Emission Strength"].default_value = 2.2

    glass = mats.get("NEXUS_Glass")
    if glass is not None:
        nt, bsdf = clear_node_tree(glass)
        bsdf.inputs["Base Color"].default_value = (0.55, 0.72, 0.74, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.05
        bsdf.inputs["Metallic"].default_value = 0.0
        bsdf.inputs["IOR"].default_value = 1.45
        bsdf.inputs["Transmission Weight"].default_value = 0.85
        try:
            glass.surface_render_method = "DITHERED"
        except Exception:
            pass

    water = mats.get("NEXUS_Water")
    if water is not None:
        nt, bsdf = clear_node_tree(water)
        bsdf.inputs["Base Color"].default_value = (0.02, 0.12, 0.12, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.08
        bsdf.inputs["IOR"].default_value = 1.33
        bsdf.inputs["Transmission Weight"].default_value = 0.75
        try:
            water.surface_render_method = "DITHERED"
        except Exception:
            pass

    blood = mats.get("NEXUS_Blood_Dried")
    if blood is not None:
        nt, bsdf = clear_node_tree(blood)
        bsdf.inputs["Base Color"].default_value = (0.10, 0.006, 0.004, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.62

    debris = mats.get("NEXUS_Debris")
    if debris is not None:
        nt, bsdf = clear_node_tree(debris)
        bsdf.inputs["Base Color"].default_value = (0.09, 0.085, 0.07, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.95


# ---------------------------------------------------------------- geometry
def remove_created(prefix):
    for obj in list(bpy.data.objects):
        if obj.name.startswith(prefix):
            bpy.data.objects.remove(obj, do_unlink=True)


def box(name, center, size, mat, col, bevel=0.02):
    mesh = bpy.data.meshes.new(name)
    x, y, z = size[0] * 0.5, size[1] * 0.5, size[2] * 0.5
    verts = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
             (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    obj.location = center
    if mat is not None:
        mesh.materials.append(mat)
    if bevel > 0:
        m = obj.modifiers.new("Bevel", "BEVEL")
        m.width = bevel
        m.segments = 2
    return obj


def door_leaves():
    groups = {}
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        n = obj.name
        if n.endswith("_DOOR_FRAME") or n.endswith("_DOOR_FRAME.001"):
            base = n.replace(".001", "")
            groups.setdefault(base, []).append(obj)
    made = 0
    for base, jambs in groups.items():
        if len(jambs) < 2:
            continue
        p1, p2 = jambs[0].location.copy(), jambs[1].location.copy()
        dx, dy = abs(p1.x - p2.x), abs(p1.y - p2.y)
        width = max(dx, dy) - 0.08
        if width < 0.55:
            continue
        top = bpy.data.objects.get(base + "_TOP")
        top_z = top.location.z if top is not None else (p1.z + 1.8)
        height = 3.2
        center = Vector(((p1.x + p2.x) * 0.5, (p1.y + p2.y) * 0.5, top_z - height * 0.5))
        room = base.replace("_DOOR_FRAME", "").replace("NEXUS_", "")
        name = "NEXUS_UP_DOOR_" + room
        size = (width, 0.09, height) if dx >= dy else (0.09, width, height)
        leaf = box(name, center, size, bpy.data.materials.get("NEXUS_Painted_Metal"), COL_CIRC, 0.025)
        # glass window
        win_size = (min(0.55, width * 0.25), 0.11, 0.62) if dx >= dy else (0.11, min(0.55, width * 0.25), 0.62)
        win_center = center + Vector((0, 0, 0.25))
        box(name + "_Window", win_center, win_size, bpy.data.materials.get("NEXUS_Glass"), COL_CIRC, 0.01)
        # handle, offset along the leaf width
        offset = width * 0.32
        if dx >= dy:
            hpos = center + Vector((offset, -0.065, -0.05))
            hsize = (0.035, 0.05, 0.42)
        else:
            hpos = center + Vector((-0.065, offset, -0.05))
            hsize = (0.05, 0.035, 0.42)
        box(name + "_Handle", hpos, hsize, bpy.data.materials.get("NEXUS_Steel"), COL_CIRC, 0.008)
        # amber kick strip
        if dx >= dy:
            ksize = (width * 0.9, 0.012, 0.07)
        else:
            ksize = (0.012, width * 0.9, 0.07)
        box(name + "_Kick", center + Vector((0, 0, -height * 0.5 + 0.18)), ksize, bpy.data.materials.get("NEXUS_Amber"), COL_CIRC, 0.005)
        made += 1
    print("DOORS_MADE", made)


def corridor_ceilings_and_lights():
    made_c = 0
    made_l = 0
    for obj in list(bpy.data.objects):
        if obj.type != "MESH" or not obj.name.startswith("CORRIDOR_") or not obj.name.endswith("_FLOOR"):
            continue
        f = obj.location
        sx, sy = obj.dimensions.x, obj.dimensions.y
        cz = f.z + 3.2
        cname = "NEXUS_UP_CORR_CEIL_" + obj.name.replace("_FLOOR", "")
        box(cname, Vector((f.x, f.y, cz)), (max(0.5, sx - 0.04), max(0.5, sy - 0.04), 0.14),
            bpy.data.materials.get("NEXUS_Concrete_Dark"), COL_STRUCT, 0.012)
        if sx >= sy:
            strip_len = min(2.2, max(0.8, sx - 0.7))
            strip_size = (strip_len, 0.08, 0.06)
            light_size = (strip_len, 0.22)
        else:
            strip_len = min(2.2, max(0.8, sy - 0.7))
            strip_size = (0.08, strip_len, 0.06)
            light_size = (0.22, strip_len)
        box("NEXUS_UP_CORR_STRIP_" + obj.name.replace("_FLOOR", ""),
            Vector((f.x, f.y, cz - 0.10)), strip_size,
            bpy.data.materials.get("NEXUS_CorridorLight"), COL_LIGHT, 0.005)
        ld = bpy.data.lights.new("NEXUS_UP_CORR_LIGHT_" + obj.name.replace("_FLOOR", ""), "AREA")
        ld.energy = 55.0
        ld.color = (0.62, 0.82, 1.0)
        ld.shape = "RECTANGLE"
        ld.size = max(0.4, light_size[0])
        ld.size_y = max(0.2, light_size[1])
        lo = bpy.data.objects.new(ld.name, ld)
        COL_LIGHT.objects.link(lo)
        lo.location = Vector((f.x, f.y, cz - 0.18))
        made_c += 1
        made_l += 1
    print("CORRIDOR_CEILINGS", made_c, "CORRIDOR_LIGHTS", made_l)


def retune_room_lights():
    for obj in bpy.data.objects:
        if obj.type != "LIGHT" or not obj.name.endswith("_LIGHT_AREA"):
            continue
        n = obj.name.upper()
        if any(k in n for k in ("LAB_", "SALA_ANALISIS", "OBSERVACION", "ARCHIVO", "SERVIDORES")):
            obj.data.color = (0.62, 0.82, 1.0); obj.data.energy = 135.0
        elif any(k in n for k in ("QUIROFANO", "ENFERMERIA", "HABITACIONES", "MORGUE", "AISLAMIENTO")):
            obj.data.color = (0.86, 0.92, 1.0); obj.data.energy = 145.0
        elif any(k in n for k in ("CONTENCION", "BUNKER", "ARMERIA", "TUNEL")):
            obj.data.color = (1.0, 0.055, 0.025); obj.data.energy = 70.0
        elif any(k in n for k in ("MANTENIMIENTO", "GENERADORES", "BOMBEO", "REFRIGERACION", "CAMARAS_FRIGORIFICAS")):
            obj.data.color = (1.0, 0.48, 0.12); obj.data.energy = 105.0
        else:
            obj.data.color = (0.92, 0.88, 0.78); obj.data.energy = 120.0
        obj.data.use_shadow = any(k in n for k in ("LAB_BIOLOGIA", "CONTENCION_PRIMARIA", "QUIROFANO", "SERVIDORES"))


def world_and_render():
    world = bpy.data.worlds.get("World")
    if world is None:
        world = bpy.data.worlds.new("World")
    SCENE.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    out.location = (400, 0)
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.location = (150, 100)
    bg.inputs["Color"].default_value = (0.008, 0.014, 0.018, 1.0)
    bg.inputs["Strength"].default_value = 0.045
    vol = nt.nodes.new("ShaderNodeVolumePrincipled")
    vol.location = (130, -180)
    vol.inputs["Color"].default_value = (0.30, 0.42, 0.45, 1.0)
    vol.inputs["Density"].default_value = 0.0035
    vol.inputs["Anisotropy"].default_value = 0.25
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    nt.links.new(vol.outputs["Volume"], out.inputs["Volume"])

    try:
        SCENE.render.engine = "BLENDER_EEVEE"
    except Exception:
        pass
    SCENE.render.resolution_x = 1920
    SCENE.render.resolution_y = 1080
    SCENE.render.resolution_percentage = 100
    SCENE.render.image_settings.file_format = "PNG"
    try:
        SCENE.eevee.taa_render_samples = 64
    except Exception:
        pass
    try:
        SCENE.view_settings.view_transform = "AgX"
        SCENE.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass


def make_camera(name, loc, target, lens=30.0):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.sensor_width = 36.0
    co = bpy.data.objects.new(name, cd)
    COL_CAMS.objects.link(co)
    co.location = loc
    d = Vector(target) - Vector(loc)
    co.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return co


def cameras():
    cams = []
    cams.append(make_camera("NEXUS_UP_CAM_Overview", (44.0, -42.0, 18.0), (0.0, -2.0, -24.0), 32.0))
    cams.append(make_camera("NEXUS_UP_CAM_Corridor_L2", (-5.0, -9.6, -12.2), (-5.0, 5.0, -12.2), 24.0))
    cams.append(make_camera("NEXUS_UP_CAM_Lab_Biologia", (-20.5, 4.8, -12.3), (-15.2, 1.5, -12.2), 24.0))
    cams.append(make_camera("NEXUS_UP_CAM_Contencion", (-21.0, 5.5, -31.0), (-14.0, 1.2, -31.5), 24.0))
    SCENE.camera = cams[0]
    print("CAMERAS", [c.name for c in cams])


def save_version():
    base = os.path.join(ROOT, "blender_concept", "FM_NEXUS_V02_stage1")
    path = base + ".blend"
    i = 2
    while os.path.exists(path):
        path = f"{base}_{i:02d}.blend"
        i += 1
    bpy.ops.wm.save_as_mainfile(filepath=path)
    print("SAVED", path, os.path.getsize(path))


# ---------------------------------------------------------------- run
remove_created("NEXUS_UP_")
classify_all()
update_materials()
door_leaves()
corridor_ceilings_and_lights()
retune_room_lights()
world_and_render()
cameras()
bpy.context.view_layer.update()
print("STAGE1_DONE objects", len(bpy.data.objects), "materials", len(bpy.data.materials))
save_version()
