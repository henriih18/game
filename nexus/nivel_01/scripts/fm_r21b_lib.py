"""FRECUENCIA MUERTA - L1_SECURITY_R21B_HERO toolkit.

Hero-quality hard-surface props for the west/centre/east filling of Security 03.
Authored at real-world scale in metres, world space, with baked bevels (3-4
segments on primary forms), box-projected UVs, weighted normals on assemblies
and procedural PBR materials. It never touches the R2 / R21A hero collections.
"""
import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

import fm_ops_lib as L

ROOT = "L1_SECURITY_R21B_HERO"
TAU = math.pi * 2.0


# --------------------------------------------------------------------------------------
# collection / lifecycle
# --------------------------------------------------------------------------------------
def clean_root():
    root = bpy.data.collections.get(ROOT)
    if not root:
        return

    def walk(c):
        for ch in list(c.children):
            walk(ch)
        for ob in list(c.objects):
            me = ob.data if ob.type == "MESH" else None
            bpy.data.objects.remove(ob, do_unlink=True)
            if me and me.users == 0:
                bpy.data.meshes.remove(me)
        if c.users == 0:
            bpy.data.collections.remove(c)

    walk(root)
    if root.users == 0:
        bpy.data.collections.remove(root)


def root_collection():
    scene = bpy.context.scene
    c = bpy.data.collections.get(ROOT)
    if c is None:
        c = bpy.data.collections.new(ROOT)
    if c.name not in scene.collection.children:
        scene.collection.children.link(c)
    return c


def sub(name):
    r = root_collection()
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
    if c.name not in r.children:
        r.children.link(c)
    return c


# --------------------------------------------------------------------------------------
# materials
# --------------------------------------------------------------------------------------
def _node(m, t):
    return next((n for n in m.node_tree.nodes if n.type == t), None)


def pbr(name, base, metallic=0.0, rough=0.5, noise=0.0, bump=0.0, rough_var=0.0,
        emission=None, emission_strength=0.0, alpha=1.0, sheen=0.0, ior=1.5,
        uv=True, grain=None, coat=0.0):
    """Procedural PBR material driven by UV (or object) coordinates."""
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    if m.node_tree is None:
        m.use_nodes = True
    nt = m.node_tree
    bsdf = _node(m, "BSDF_PRINCIPLED")
    out = _node(m, "OUTPUT_MATERIAL")
    if bsdf is None:
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    if out is None:
        out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    bsdf.inputs["Base Color"].default_value = (*base, 1.0)
    m.diffuse_color = (*base, 1.0)  # Workbench material-colour cutaways
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["IOR"].default_value = ior
    bsdf.inputs["Alpha"].default_value = alpha
    if "Sheen Weight" in bsdf.inputs:
        bsdf.inputs["Sheen Weight"].default_value = sheen
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = coat
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength

    # rebuild procedural chain
    for n in list(nt.nodes):
        if n.type not in {"OUTPUT_MATERIAL", "BSDF_PRINCIPLED"}:
            nt.nodes.remove(n)

    if noise > 0.0:
        tc = nt.nodes.new("ShaderNodeTexCoord")
        vec = tc.outputs["UV" if uv else "Object"]
        if grain is not None:
            mp = nt.nodes.new("ShaderNodeMapping")
            mp.inputs["Scale"].default_value = grain
            nt.links.new(vec, mp.inputs["Vector"])
            vec = mp.outputs["Vector"]
        tex = nt.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = noise
        tex.inputs["Detail"].default_value = 5.0
        tex.inputs["Roughness"].default_value = 0.58
        nt.links.new(vec, tex.inputs["Vector"])
        if rough_var > 0.0:
            ramp = nt.nodes.new("ShaderNodeValToRGB")
            ramp.color_ramp.elements[0].position = 0.24
            ramp.color_ramp.elements[0].color = (max(0.02, rough - rough_var),) * 3 + (1.0,)
            ramp.color_ramp.elements[1].position = 0.76
            ramp.color_ramp.elements[1].color = (min(0.98, rough + rough_var),) * 3 + (1.0,)
            nt.links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
            nt.links.new(ramp.outputs["Color"], bsdf.inputs["Roughness"])
        if bump > 0.0:
            bmp = nt.nodes.new("ShaderNodeBump")
            bmp.inputs["Strength"].default_value = bump
            bmp.inputs["Distance"].default_value = 0.0025
            nt.links.new(tex.outputs["Fac"], bmp.inputs["Height"])
            nt.links.new(bmp.outputs["Normal"], bsdf.inputs["Normal"])
    if alpha < 1.0:
        m.surface_render_method = "DITHERED"
    return m


def palette():
    mat = {}
    # paints / polymers
    mat["green"] = pbr("M_R21B_Paint_Green", (0.030, 0.052, 0.038), 0.0, 0.43,
                       noise=95.0, bump=0.07, rough_var=0.09, coat=0.05)
    mat["green_dark"] = pbr("M_R21B_Paint_GreenDark", (0.014, 0.024, 0.018), 0.0, 0.47,
                            noise=110.0, bump=0.08, rough_var=0.08)
    mat["olive"] = pbr("M_R21B_Paint_Olive", (0.052, 0.060, 0.046), 0.0, 0.50,
                       noise=80.0, bump=0.10, rough_var=0.08)
    mat["dark"] = pbr("M_R21B_Paint_Dark", (0.014, 0.016, 0.017), 0.0, 0.48,
                      noise=120.0, bump=0.06, rough_var=0.07)
    mat["plastic"] = pbr("M_R21B_Plastic", (0.012, 0.013, 0.015), 0.0, 0.37,
                         noise=180.0, bump=0.05, rough_var=0.06)
    mat["plastic_light"] = pbr("M_R21B_Plastic_Light", (0.105, 0.110, 0.112), 0.0, 0.44,
                               noise=150.0, bump=0.04, rough_var=0.05)
    mat["rubber"] = pbr("M_R21B_Rubber", (0.009, 0.009, 0.010), 0.0, 0.84,
                        noise=160.0, bump=0.10, rough_var=0.03)
    mat["rubber_red"] = pbr("M_R21B_Rubber_Red", (0.115, 0.012, 0.008), 0.0, 0.72,
                            noise=170.0, bump=0.08, rough_var=0.04)
    mat["paint_red"] = pbr("M_R21B_Paint_Red", (0.20, 0.012, 0.006), 0.0, 0.46,
                           noise=120.0, bump=0.05, rough_var=0.06)
    # metals (metallic binary)
    mat["steel"] = pbr("M_R21B_Steel", (0.105, 0.110, 0.118), 1.0, 0.42,
                       noise=130.0, bump=0.05, rough_var=0.10)
    mat["steel_bare"] = pbr("M_R21B_Steel_Bare", (0.46, 0.48, 0.50), 1.0, 0.28,
                            noise=160.0, bump=0.03, rough_var=0.08)
    mat["steel_dark"] = pbr("M_R21B_Steel_Dark", (0.065, 0.070, 0.076), 1.0, 0.48,
                            noise=115.0, bump=0.07, rough_var=0.09)
    mat["aluminum"] = pbr("M_R21B_Aluminum", (0.50, 0.52, 0.53), 1.0, 0.31,
                          noise=150.0, bump=0.03, rough_var=0.07)
    mat["galv"] = pbr("M_R21B_Galvanized", (0.30, 0.315, 0.32), 1.0, 0.56,
                      noise=75.0, bump=0.12, rough_var=0.10)
    mat["copper"] = pbr("M_R21B_Copper", (0.60, 0.24, 0.09), 1.0, 0.35,
                        noise=140.0, bump=0.05, rough_var=0.06)
    mat["rust"] = pbr("M_R21B_Steel_Rust", (0.115, 0.055, 0.022), 0.0, 0.72,
                      noise=55.0, bump=0.18, rough_var=0.10)
    # masonry / wood / fabric
    mat["concrete"] = pbr("M_R21B_Concrete", (0.085, 0.082, 0.076), 0.0, 0.92,
                          noise=38.0, bump=0.20, rough_var=0.04)
    mat["concrete_dark"] = pbr("M_R21B_Concrete_Dark", (0.048, 0.047, 0.044), 0.0, 0.94,
                               noise=45.0, bump=0.18, rough_var=0.03)
    mat["wood"] = pbr("M_R21B_Wood", (0.115, 0.066, 0.034), 0.0, 0.66,
                      noise=22.0, bump=0.10, rough_var=0.10, grain=(1.2, 9.0, 1.2))
    mat["wood_dark"] = pbr("M_R21B_Wood_Dark", (0.055, 0.030, 0.016), 0.0, 0.70,
                           noise=18.0, bump=0.10, rough_var=0.08, grain=(1.2, 10.0, 1.2))
    mat["fabric"] = pbr("M_R21B_Fabric", (0.028, 0.030, 0.026), 0.0, 0.95,
                        noise=240.0, bump=0.22, rough_var=0.02, sheen=0.35)
    mat["rug"] = pbr("M_R21B_Rug", (0.020, 0.028, 0.022), 0.0, 0.98,
                     noise=300.0, bump=0.28, rough_var=0.02, sheen=0.25)
    mat["rug_edge"] = pbr("M_R21B_Rug_Edge", (0.055, 0.045, 0.028), 0.0, 0.94,
                          noise=260.0, bump=0.16, rough_var=0.02)
    mat["canvas"] = pbr("M_R21B_Canvas", (0.34, 0.335, 0.32), 0.0, 0.88,
                        noise=280.0, bump=0.10, rough_var=0.03)
    # glass / water / ceramics
    mat["glass"] = pbr("M_R21B_Glass", (0.52, 0.62, 0.60), 0.0, 0.06, noise=90.0,
                       bump=0.0, rough_var=0.03, alpha=0.20, ior=1.5)
    mat["glass"].surface_render_method = "BLENDED"
    mat["glass"].use_backface_culling = False
    mat["frost"] = pbr("M_R21B_Glass_Frost", (0.55, 0.62, 0.58), 0.0, 0.42, noise=140.0,
                       bump=0.02, rough_var=0.04, alpha=0.62, ior=1.5)
    mat["frost"].surface_render_method = "BLENDED"
    mat["frost"].use_backface_culling = False
    mat["water"] = pbr("M_R21B_Water", (0.006, 0.008, 0.010), 0.0, 0.045, noise=80.0,
                       bump=0.04, rough_var=0.02, ior=1.33)
    mat["ceramic"] = pbr("M_R21B_Ceramic", (0.16, 0.165, 0.15), 0.0, 0.42,
                         noise=85.0, bump=0.05, rough_var=0.06, coat=0.12)
    # organic
    mat["plant_dark"] = pbr("M_R21B_Plant_Dark", (0.012, 0.040, 0.014), 0.0, 0.58,
                            noise=120.0, bump=0.14, rough_var=0.06, sheen=0.15)
    mat["plant_light"] = pbr("M_R21B_Plant_Light", (0.035, 0.090, 0.030), 0.0, 0.52,
                             noise=100.0, bump=0.12, rough_var=0.06, sheen=0.18)
    mat["soil"] = pbr("M_R21B_Soil", (0.020, 0.015, 0.010), 0.0, 1.0,
                      noise=90.0, bump=0.30, rough_var=0.01)
    mat["stone"] = pbr("M_R21B_Stone", (0.10, 0.098, 0.092), 0.0, 0.86,
                       noise=70.0, bump=0.18, rough_var=0.05)
    # emissive / screens
    mat["red"] = pbr("M_R21B_Emissive_Red", (0.16, 0.004, 0.002), 0.0, 0.20,
                     emission=(1.0, 0.025, 0.008), emission_strength=4.0)
    mat["amber"] = pbr("M_R21B_Emissive_Amber", (0.25, 0.07, 0.008), 0.0, 0.24,
                       emission=(1.0, 0.42, 0.04), emission_strength=2.0)
    mat["spark"] = pbr("M_R21B_Emissive_Spark", (0.6, 0.25, 0.02), 0.0, 0.18,
                       emission=(1.0, 0.48, 0.08), emission_strength=9.0)
    mat["led_green"] = pbr("M_R21B_LED_Green", (0.004, 0.02, 0.006), 0.0, 0.16,
                           emission=(0.06, 1.0, 0.18), emission_strength=2.4)
    mat["led_blue"] = pbr("M_R21B_LED_Blue", (0.003, 0.010, 0.03), 0.0, 0.16,
                          emission=(0.06, 0.36, 1.0), emission_strength=2.0)
    mat["screen_dead"] = pbr("M_R21B_Screen_Dead", (0.0012, 0.0014, 0.0016), 0.0, 0.24,
                             noise=150.0, bump=0.02, rough_var=0.02)
    mat["screen_cracked"] = pbr("M_R21B_Screen_Cracked", (0.0025, 0.003, 0.0034), 0.0, 0.10,
                                noise=100.0, bump=0.02, rough_var=0.02)
    mat["screen_glow"] = pbr("M_R21B_Screen_Glow", (0.002, 0.006, 0.005), 0.0, 0.16,
                             emission=(0.04, 0.42, 0.30), emission_strength=0.45)
    # signage / labels
    mat["white"] = pbr("M_R21B_Sign_White", (0.62, 0.62, 0.58), 0.0, 0.48,
                       noise=110.0, bump=0.03, rough_var=0.05)
    mat["sign_green"] = pbr("M_R21B_Sign_Green", (0.012, 0.105, 0.045), 0.0, 0.42,
                            noise=100.0, bump=0.03, rough_var=0.04)
    mat["exit_green"] = pbr("M_R21B_Exit_Green", (0.006, 0.070, 0.030), 0.0, 0.35,
                            noise=120.0, bump=0.02, emission=(0.02, 0.55, 0.12),
                            emission_strength=1.4)
    mat["paper"] = pbr("M_R21B_Label", (0.42, 0.40, 0.34), 0.0, 0.62,
                       noise=190.0, bump=0.05, rough_var=0.04)
    mat["hazard_y"] = pbr("M_R21B_Hazard_Yellow", (0.42, 0.285, 0.012), 0.0, 0.62,
                          noise=130.0, bump=0.04, rough_var=0.08)
    mat["hazard_k"] = pbr("M_R21B_Hazard_Black", (0.008, 0.009, 0.009), 0.0, 0.58,
                          noise=140.0, bump=0.04, rough_var=0.06)
    mat["dust"] = pbr("M_R21B_Dust", (0.075, 0.066, 0.052), 0.0, 0.99, noise=35.0,
                      bump=0.06, rough_var=0.01, alpha=0.34)
    mat["dust"].surface_render_method = "DITHERED"
    # cables
    mat["cable_black"] = pbr("M_R21B_Cable_Black", (0.008, 0.008, 0.009), 0.0, 0.58,
                             noise=200.0, bump=0.06, rough_var=0.04)
    mat["cable_orange"] = pbr("M_R21B_Cable_Orange", (0.22, 0.055, 0.008), 0.0, 0.55,
                              noise=180.0, bump=0.06, rough_var=0.04)
    mat["cable_grey"] = pbr("M_R21B_Cable_Grey", (0.08, 0.085, 0.09), 0.0, 0.52,
                            noise=200.0, bump=0.06, rough_var=0.04)
    return mat


# --------------------------------------------------------------------------------------
# mesh primitives / details
# --------------------------------------------------------------------------------------
def finish(bm, name, coll, mat, loc=(0, 0, 0), rot=(0, 0, 0), smooth=True,
           sharp=38.0, uv_scale=1.0):
    me = bpy.data.meshes.new(name)
    L._finish_bm(bm, me, smooth=smooth, sharp_angle=sharp)
    L._box_uv(me, uv_scale)
    return L._link(name, me, coll, mat, loc, rot)


def box(name, size, center, mat, coll, rot=(0, 0, 0), bevel=0.004, seg=3, uv=1.0):
    # very thin boxes must not be beveled: the bevel self-intersects, inverts volume
    # and produces z-fighting. They read as trim/panels, so a hard edge is correct.
    small = min(size)
    if small < 0.050:
        # small structural trim, bolts, vents: keep hard edges. Beveling these
        # sub-5 cm forms creates non-manifold n-gons that break volume QA and
        # z-fighting, with no visible gain at gameplay distance.
        bevel, seg = 0.0, 1
    else:
        bevel = min(bevel, small * 0.18)
        seg = min(seg, 3)
    return L.box(name, size, center, mat, coll, rot=rot, bevel=bevel, seg=seg, uv_scale=uv)


def cyl(name, radius, depth, center, mat, coll, rot=(0, 0, 0), segments=20, bevel=0.002,
        seg=2, r2=None, uv=1.0):
    if depth < 0.006:
        bevel = 0.0
    else:
        bevel = min(bevel, depth * 0.22, max(radius, 0.001) * 0.30)
    return L.cyl(name, radius, depth, center, mat, coll, rot=rot, segments=segments,
                 bevel=bevel, seg=seg, r2=r2, uv_scale=uv)


def tube(name, pts, radius, mat, coll, sides=8, cap=True, uv=1.0):
    return L.tube(name, pts, radius, mat, coll, sides=sides, cap=cap, uv_scale=uv)


def bolts(name, positions, normal, radius, depth, mat, coll, segments=6, washer=True):
    """Single closed hex-head bolts (no washer shell). The washer/head overlap in the
    upstream kit caused coplanar faces and unreliable volume signs on 1 cm parts."""
    import bmesh
    from mathutils import Matrix
    normal = Vector(normal).normalized()
    quat = normal.to_track_quat("Z", "Y")
    bm = bmesh.new()
    for p in positions:
        M = (Matrix.Translation(Vector(p)) @ quat.to_matrix().to_4x4() @
             Matrix.Translation((0, 0, depth * 0.55)))
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                              radius1=radius, radius2=radius * 0.92, depth=depth,
                              matrix=M)
    me = bpy.data.meshes.new(name)
    L._finish_bm(bm, me, smooth=True, sharp_angle=42.0)
    L._box_uv(me)
    return L._link(name, me, coll, mat, (0, 0, 0))


def join(parts, name, coll):
    ob = L.join(parts, name, coll)
    if ob:
        # drop unused slots (QA counts them as extra draw calls)
        used = set()
        for p in ob.data.polygons:
            used.add(p.material_index)
        for i in sorted(set(range(len(ob.material_slots))) - used, reverse=True):
            ob.data.materials.pop(index=i)
        L.fix_inverted_islands(ob)
        L.weighted_normal(ob)
    return ob


def bake_world(ob):
    """Bake object transform into mesh, leaving object at world origin (identity)."""
    if ob is None:
        return None
    ob.data.transform(ob.matrix_world)
    ob.matrix_world = Matrix.Identity(4)
    return ob


def place(ob, center, rot_z=0.0, rot=(0.0, 0.0, 0.0), drop=False):
    """Place a locally-built (baked) prop at center with rotation, optionally to floor."""
    if ob is None:
        return None
    bake_world(ob)
    m = (Matrix.Translation(Vector(center)) @
         Matrix.Rotation(math.radians(rot_z), 4, "Z") @
         (Matrix.Rotation(math.radians(rot[0]), 4, "X") @
          Matrix.Rotation(math.radians(rot[1]), 4, "Y") @
          Matrix.Rotation(math.radians(rot[2]), 4, "Z")))
    ob.matrix_world = m
    if drop:
        bpy.context.view_layer.update()
        lo = min((ob.matrix_world @ v.co).z for v in ob.data.vertices)
        ob.matrix_world = Matrix.Translation((0, 0, 0.0015 - lo)) @ ob.matrix_world
    bpy.context.view_layer.update()
    return ob


def rod(name, p0, p1, radius, mat, coll, segments=12, bevel=0.001):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    if d.length < 1e-6:
        return None
    ob = cyl(name, radius, d.length, (p0 + p1) * 0.5, mat, coll, segments=segments,
             bevel=bevel, seg=2)
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion = d.to_track_quat("Z", "Y")
    return ob


def annulus(name, center, r_out, r_in, thick, mat, coll, rot=(0, 0, 0), segments=32):
    bm = bmesh.new()
    top_o, top_i, bot_o, bot_i = [], [], [], []
    for i in range(segments):
        a = TAU * i / segments
        c, s = math.cos(a), math.sin(a)
        top_o.append(bm.verts.new((c * r_out, s * r_out, thick * 0.5)))
        top_i.append(bm.verts.new((c * r_in, s * r_in, thick * 0.5)))
        bot_o.append(bm.verts.new((c * r_out, s * r_out, -thick * 0.5)))
        bot_i.append(bm.verts.new((c * r_in, s * r_in, -thick * 0.5)))
    for i in range(segments):
        j = (i + 1) % segments
        bm.faces.new((top_o[i], top_o[j], top_i[j], top_i[i]))
        bm.faces.new((bot_o[j], bot_o[i], bot_i[i], bot_i[j]))
        bm.faces.new((bot_o[i], bot_o[j], top_o[j], top_o[i]))
        bm.faces.new((top_i[i], top_i[j], bot_i[j], bot_i[i]))
    ob = finish(bm, name, coll, mat)
    ob.location = center
    ob.rotation_euler = rot
    return ob


def leaf(name, base, length, width, tilt_x, tilt_y, twist, mat, coll, seed=1,
         curve=0.35):
    """Closed lens-section leaf built along +Z then tilted/rotated."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    segs = 8
    rings = []
    for i in range(segs + 1):
        t = i / segs
        w = width * math.sin(math.pi * min(1.0, t * 1.05)) ** 0.7
        w = max(0.0018, w) * (1.0 + rnd.uniform(-0.08, 0.08))
        # curve outwards in X, twist around Z
        x = curve * length * (t * t) * 0.45
        y = math.sin(t * math.pi * 0.85) * length * 0.10
        z = t * length
        a = math.radians(twist * t)
        # cross-section: left, ridge, right (front/back thickness)
        pts = []
        for sx, sy in ((-w, 0.0), (-w * 0.45, w * 0.28), (0.0, w * 0.38),
                       (w * 0.45, w * 0.28), (w, 0.0),
                       (w * 0.45, -w * 0.10), (0.0, -w * 0.14),
                       (-w * 0.45, -w * 0.10)):
            rx = sx * math.cos(a) - sy * math.sin(a)
            ry = sx * math.sin(a) + sy * math.cos(a)
            pts.append(bm.verts.new((x + rx, y + ry, z)))
        rings.append(pts)
    for i in range(segs):
        for k in range(8):
            a = rings[i][k]
            b = rings[i][(k + 1) % 8]
            c = rings[i + 1][(k + 1) % 8]
            d = rings[i + 1][k]
            bm.faces.new((a, b, c, d))
    bm.faces.new(tuple(reversed(rings[0])))
    bm.faces.new(tuple(rings[-1]))
    ob = finish(bm, name, coll, mat, smooth=True, sharp=55.0)
    # place on base with tilt
    ob.rotation_mode = "XYZ"
    ob.matrix_world = (Matrix.Translation(Vector(base)) @
                       Matrix.Rotation(math.radians(tilt_x), 4, "X") @
                       Matrix.Rotation(math.radians(tilt_y), 4, "Y"))
    return ob


def ribbon(name, pts, width, thick, mat, coll, up=(0, 0, 1), taper=None):
    """Closed rectangular ribbon along a polyline (belts, tapes, seals)."""
    pts = [Vector(p) for p in pts]
    up = Vector(up).normalized()
    bm = bmesh.new()
    rings = []
    n = len(pts)
    for i, p in enumerate(pts):
        if i == 0:
            t = pts[1] - pts[0]
        elif i == n - 1:
            t = pts[-1] - pts[-2]
        else:
            t = pts[i + 1] - pts[i - 1]
        t.normalize()
        side = t.cross(up)
        if side.length < 1e-6:
            side = Vector((1, 0, 0))
        side.normalize()
        w = width * (taper[i] if taper else 1.0) * 0.5
        h = thick * 0.5
        ring = [bm.verts.new(p - side * w - up * h), bm.verts.new(p + side * w - up * h),
                bm.verts.new(p + side * w + up * h), bm.verts.new(p - side * w + up * h)]
        rings.append(ring)
    for i in range(n - 1):
        for k in range(4):
            a = rings[i][k]
            b = rings[i][(k + 1) % 4]
            c = rings[i + 1][(k + 1) % 4]
            d = rings[i + 1][k]
            bm.faces.new((a, b, c, d))
    bm.faces.new(tuple(reversed(rings[0])))
    bm.faces.new(tuple(rings[-1]))
    return finish(bm, name, coll, mat)


def extrude_poly(name, pts2d, z, thick, mat, coll, rot=(0, 0, 0), center=(0, 0, 0)):
    """Extrude a 2D polygon (XY) from z to z+thick."""
    bm = bmesh.new()
    bottom, top = [], []
    for x, y in pts2d:
        bottom.append(bm.verts.new((x, y, z)))
        top.append(bm.verts.new((x, y, z + thick)))
    bm.faces.new(tuple(reversed(bottom)))
    bm.faces.new(tuple(top))
    n = len(pts2d)
    for i in range(n):
        a, b = bottom[i], bottom[(i + 1) % n]
        c, d = top[(i + 1) % n], top[i]
        bm.faces.new((a, b, c, d))
    return finish(bm, name, coll, mat, center, rot)


def panel_poly_yz(name, pts_yz, x, thick, mat, coll):
    """Flat polygon in the YZ plane at x, extruded by thick along +X."""
    bm = bmesh.new()
    a, b = [], []
    for y, z in pts_yz:
        a.append(bm.verts.new((x, y, z)))
        b.append(bm.verts.new((x + thick, y, z)))
    bm.faces.new(tuple(reversed(a)))
    bm.faces.new(tuple(b))
    n = len(pts_yz)
    for i in range(n):
        bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    return finish(bm, name, coll, mat, smooth=False, sharp=25.0)


def ring(name, center, radius, depth, mat, coll, axis="Z", segments=24, bevel=0.001):
    rot = {"Z": (0, 0, 0), "X": (0, math.radians(90), 0), "Y": (math.radians(90), 0, 0)}[axis]
    return cyl(name, radius, depth, center, mat, coll, rot=rot, segments=segments,
               bevel=bevel, seg=2)


def vent(name, center, size, mat_frame, mat_slat, coll, rot=(0, 0, 0), slats=7,
         slant=28.0):
    """Recessed louvre: dark backing + slats + thin frame, joined."""
    w, h, d = size
    parts = []
    parts.append(box(name + "_Back", (w * 0.92, d * 0.35, h * 0.92), (0, 0, 0),
                     mat_frame, coll, rot=rot, bevel=0.0015, seg=2))
    gap = h * 0.86 / slats
    for i in range(slats):
        z = -h * 0.43 + gap * (i + 0.5)
        parts.append(box(f"{name}_Slat{i}", (w * 0.92, d * 0.55, gap * 0.42),
                         (0, 0, z), mat_slat, coll,
                         rot=(math.radians(slant), 0, 0), bevel=0.0008, seg=2))
    # frame bars
    parts.append(box(name + "_FT", (w, d, h * 0.06), (0, 0, h * 0.47), mat_frame, coll,
                     rot=rot, bevel=0.001, seg=2))
    parts.append(box(name + "_FB", (w, d, h * 0.06), (0, 0, -h * 0.47), mat_frame, coll,
                     rot=rot, bevel=0.001, seg=2))
    parts.append(box(name + "_FL", (w * 0.04, d, h), (-w * 0.48, 0, 0), mat_frame, coll,
                     rot=rot, bevel=0.001, seg=2))
    parts.append(box(name + "_FR", (w * 0.04, d, h), (w * 0.48, 0, 0), mat_frame, coll,
                     rot=rot, bevel=0.001, seg=2))
    ob = join(parts, name, coll)
    ob.location = center
    ob.rotation_euler = rot
    return ob


def frame_rect(name, outer_w, outer_h, inner_w, inner_h, depth, center, mat, coll):
    """Closed rectangular picture-frame: one island, no overlapping corner boxes."""
    bm = bmesh.new()
    ow, oh = outer_w * 0.5, outer_h * 0.5
    iw, ih = inner_w * 0.5, inner_h * 0.5
    d = depth * 0.5
    # front (-x), back (+x)
    of = [bm.verts.new((-d, -ow, -oh)), bm.verts.new((-d, ow, -oh)),
          bm.verts.new((-d, ow, oh)), bm.verts.new((-d, -ow, oh))]
    ob = [bm.verts.new((d, -ow, -oh)), bm.verts.new((d, ow, -oh)),
          bm.verts.new((d, ow, oh)), bm.verts.new((d, -ow, oh))]
    inf = [bm.verts.new((-d, -iw, -ih)), bm.verts.new((-d, iw, -ih)),
           bm.verts.new((-d, iw, ih)), bm.verts.new((-d, -iw, ih))]
    inb = [bm.verts.new((d, -iw, -ih)), bm.verts.new((d, iw, -ih)),
           bm.verts.new((d, iw, ih)), bm.verts.new((d, -iw, ih))]
    for i in range(4):
        j = (i + 1) % 4
        # front ring (normal -X)
        bm.faces.new((of[i], inf[i], inf[j], of[j]))
        # back ring (normal +X)
        bm.faces.new((ob[j], inb[j], inb[i], ob[i]))
        # outer wall
        bm.faces.new((of[j], of[i], ob[i], ob[j]))
        # inner wall
        bm.faces.new((inf[i], inf[j], inb[j], inb[i]))
    me = bpy.data.meshes.new(name)
    L._finish_bm(bm, me, smooth=False, sharp_angle=30.0)
    L._box_uv(me)
    return L._link(name, me, coll, mat, center)


def handle(name, center, length, mat, coll, rot=(0, 0, 0), standoff=0.03, radius=0.009):
    """U-shaped pull handle on two standoffs; local X = length, Y = out from face."""
    parts = []
    for x in (-length * 0.5 + 0.03, length * 0.5 - 0.03):
        parts.append(cyl(name + f"_Post{x:.2f}", radius * 0.72, standoff,
                         (x, standoff * 0.5, 0), mat, coll,
                         rot=(math.radians(90), 0, 0), segments=10, bevel=0.001))
    pts = [(-length * 0.5 + 0.03, standoff, 0), (-length * 0.5 + 0.06, standoff + 0.012, 0),
           (0, standoff + 0.018, 0), (length * 0.5 - 0.06, standoff + 0.012, 0),
           (length * 0.5 - 0.03, standoff, 0)]
    parts.append(tube(name + "_Bar", pts, radius, mat, coll, sides=10))
    ob = join(parts, name, coll)
    ob.location = center
    ob.rotation_euler = rot
    return ob


def hinge(name, center, height, mat, coll, rot=(0, 0, 0), radius=0.011):
    parts = []
    parts.append(cyl(name + "_Pin", radius, height, (0, 0, 0), mat, coll, segments=14,
                     bevel=0.001))
    for z in (-height * 0.32, height * 0.32):
        parts.append(box(f"{name}_Leaf{z:.2f}", (0.052, 0.006, height * 0.20),
                         (0.024, -0.006, z), mat, coll, bevel=0.0012, seg=2))
    ob = join(parts, name, coll)
    ob.location = center
    ob.rotation_euler = rot
    return ob


def cabinet_door(name, w, h, d, center, mat_face, mat_edge, mat_handle, coll,
                 open_deg=0.0, hinge_side=-1, handle_side=1, vent_size=None,
                 lock=True, rot_z=0.0):
    """Detailed inset-panel door, hinged on local X edge. Local face = -Y."""
    parts = []
    fw = 0.045
    # outer frame bars (front plane at y=-d/2)
    parts.append(box(name + "_Top", (w, d, fw), (0, 0, h * 0.5 - fw * 0.5), mat_face, coll,
                     bevel=0.0025, seg=3))
    parts.append(box(name + "_Bot", (w, d, fw), (0, 0, -h * 0.5 + fw * 0.5), mat_face, coll,
                     bevel=0.0025, seg=3))
    parts.append(box(name + "_L", (fw, d, h - 2 * fw), (-w * 0.5 + fw * 0.5, 0, 0), mat_face,
                     coll, bevel=0.0025, seg=3))
    parts.append(box(name + "_R", (fw, d, h - 2 * fw), (w * 0.5 - fw * 0.5, 0, 0), mat_face,
                     coll, bevel=0.0025, seg=3))
    # recessed inner panel
    parts.append(box(name + "_Panel", (w - 2 * fw - 0.004, d * 0.55, h - 2 * fw - 0.004),
                     (0, d * 0.16, 0), mat_edge, coll, bevel=0.002, seg=3))
    # inset seam strips (proud 2 mm, creates panel-line shadow)
    for sx in (-1, 1):
        parts.append(box(f"{name}_SeamV{sx}", (0.004, 0.004, h - 2 * fw - 0.012),
                         (sx * (w * 0.5 - fw - 0.004), -d * 0.5 - 0.001, 0),
                         mat_handle, coll, bevel=0.0005, seg=1))
    for sz in (-1, 1):
        parts.append(box(f"{name}_SeamH{sz}", (w - 2 * fw - 0.012, 0.004, 0.004),
                         (0, -d * 0.5 - 0.001, sz * (h * 0.5 - fw - 0.004)),
                         mat_handle, coll, bevel=0.0005, seg=1))
    if vent_size:
        vw, vh = vent_size
        vz = h * 0.5 - fw - vh * 0.5 - 0.035
        parts.append(box(name + "_VentBack", (vw * 0.94, d * 0.30, vh * 0.94),
                         (0, d * 0.18, vz), mat_handle, coll, bevel=0.0015, seg=2))
        for i in range(4):
            parts.append(box(f"{name}_VentSlat{i}", (vw * 0.94, d * 0.30, vh * 0.10),
                             (0, d * 0.06, vz - vh * 0.36 + i * vh * 0.22),
                             mat_handle, coll, rot=(math.radians(30), 0, 0),
                             bevel=0.0008, seg=2))
    # vertical pull grip on the front face
    hx = handle_side * (w * 0.5 - 0.09)
    parts.append(box(name + "_GripBar", (0.020, 0.020, 0.17),
                     (hx, -d * 0.5 - 0.032, -0.02), mat_handle, coll,
                     bevel=0.003, seg=3))
    for gz in (-0.075, 0.035):
        parts.append(box(f"{name}_GripPost{gz:.2f}", (0.016, 0.026, 0.016),
                         (hx, -d * 0.5 - 0.014, -0.02 + gz), mat_handle, coll,
                         bevel=0.002, seg=2))
    parts.append(box(name + "_GripPlate", (0.045, 0.006, 0.22),
                     (hx, -d * 0.5 - 0.003, -0.02), mat_face, coll,
                     bevel=0.002, seg=2))
    if lock:
        parts.append(cyl(name + "_Lock", 0.016, 0.012, (hx, -d * 0.5 - 0.006, 0.12),
                         mat_handle, coll, rot=(math.radians(90), 0, 0), segments=14,
                         bevel=0.001))
    # hinges on hinge side
    for hz in (-h * 0.33, h * 0.33):
        parts.append(hinge(f"{name}_Hinge{hz:.2f}", (hinge_side * (w * 0.5 + 0.004), 0, hz),
                           0.075, mat_handle, coll, radius=0.009))
    # number plate
    parts.append(box(name + "_Plate", (0.065, 0.003, 0.035),
                     (-hinge_side * (w * 0.5 - 0.10), -d * 0.5 - 0.002, h * 0.5 - 0.16),
                     mat_handle, coll, bevel=0.001, seg=2))
    ob = join(parts, name, coll)
    # hinge about local hinge edge
    piv = Vector((hinge_side * w * 0.5, 0, 0))
    m = (Matrix.Translation(center) @ Matrix.Rotation(math.radians(rot_z), 4, "Z") @
         Matrix.Translation(piv) @ Matrix.Rotation(math.radians(open_deg), 4, "Z") @
         Matrix.Translation(-piv))
    ob.matrix_world = m @ ob.matrix_world
    return ob


def grille(name, center, size, mat, coll, rot=(0, 0, 0), bars=9, axis="Y"):
    """Bar grille (screen/shutter) with frame. Local plane XZ, depth Y."""
    w, h, d = size
    parts = []
    parts.append(box(name + "_FT", (w, d, 0.025), (0, 0, h * 0.5 - 0.0125), mat, coll,
                     bevel=0.002, seg=2))
    parts.append(box(name + "_FB", (w, d, 0.025), (0, 0, -h * 0.5 + 0.0125), mat, coll,
                     bevel=0.002, seg=2))
    parts.append(box(name + "_FL", (0.025, d, h), (-w * 0.5 + 0.0125, 0, 0), mat, coll,
                     bevel=0.002, seg=2))
    parts.append(box(name + "_FR", (0.025, d, h), (w * 0.5 - 0.0125, 0, 0), mat, coll,
                     bevel=0.002, seg=2))
    for i in range(bars):
        x = -w * 0.5 + 0.05 + (w - 0.10) * i / max(1, bars - 1)
        parts.append(cyl(f"{name}_Bar{i}", 0.0055, h - 0.035, (x, 0, 0), mat, coll,
                         segments=8, bevel=0.0008))
    ob = join(parts, name, coll)
    ob.location = center
    ob.rotation_euler = rot
    return ob


def text(name, body, size, center, rot, mat, coll, extrude=0.0015):
    return L.text_mesh(name, body, size, center, rot, mat, coll, extrude=extrude)


def rock(name, center, scale, mat, coll, seed=1, subdiv=2):
    rnd = random.Random(seed)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=1.0)
    for v in bm.verts:
        v.co.x *= scale[0] * (1.0 + rnd.uniform(-0.22, 0.22))
        v.co.y *= scale[1] * (1.0 + rnd.uniform(-0.22, 0.22))
        v.co.z *= scale[2] * (1.0 + rnd.uniform(-0.25, 0.25))
        v.co += Vector((rnd.uniform(-0.04, 0.04) * scale[0],
                        rnd.uniform(-0.04, 0.04) * scale[1],
                        rnd.uniform(-0.04, 0.04) * scale[2]))
    me = bpy.data.meshes.new(name)
    L._finish_bm(bm, me, smooth=False, sharp_angle=30.0)
    L._box_uv(me)
    ob = L._link(name, me, coll, mat, center)
    return ob
