"""FRECUENCIA MUERTA - helpers for L1_SECURITY_R21A_HERO (security operations centre).

Run inside Blender 5.2 through the MCP. Geometry is authored at real scale, in metres,
world space, with baked bevels (3-4 segments on primary forms) and box-projected UVs.
Modifiers (Weighted Normal) are added on final assemblies only.
"""
import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

TAU = math.pi * 2.0
COLL_ROOT_NAME = "L1_SECURITY_R21A_HERO"


# --------------------------------------------------------------------------------------
# collections
# --------------------------------------------------------------------------------------
def clean_old_root():
    """Remove only our own collection tree (idempotent rebuilds)."""
    root = bpy.data.collections.get(COLL_ROOT_NAME)
    if not root:
        return
    def walk(c):
        children = list(c.children)
        for ch in children:
            walk(ch)
            if ch.users == 0:
                bpy.data.collections.remove(ch)
        for ob in list(c.objects):
            me = ob.data if ob.type == "MESH" else None
            bpy.data.objects.remove(ob, do_unlink=True)
            if me and me.users == 0:
                bpy.data.meshes.remove(me)
    walk(root)
    bpy.data.collections.remove(root)
    # sweep orphans left behind by an interrupted previous build
    for c in list(bpy.data.collections):
        if not c.name.startswith("L1_SECURITY_R21A_"):
            continue
        for ob in list(c.objects):
            me = ob.data if ob.type == "MESH" else None
            bpy.data.objects.remove(ob, do_unlink=True)
            if me and me.users == 0:
                bpy.data.meshes.remove(me)
        bpy.data.collections.remove(c)


def make_root():
    scene = bpy.context.scene
    root = bpy.data.collections.get(COLL_ROOT_NAME)
    if root is None:
        root = bpy.data.collections.new(COLL_ROOT_NAME)
    if root.name not in scene.collection.children:
        scene.collection.children.link(root)
    return root


def sub(name):
    root = make_root()
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
    if c.name not in root.children:
        root.children.link(c)
    return c


# --------------------------------------------------------------------------------------
# materials
# --------------------------------------------------------------------------------------
def _mat(name):
    m = bpy.data.materials.get(name)
    return m


def _principled(name):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    if m.node_tree is None:
        m.use_nodes = True
    nt = m.node_tree
    bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    out = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None)
    if bsdf is None:
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    if out is None:
        out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return m, nt, bsdf


def pbr(name, base, metallic=0.0, rough=0.5, emission=None, emission_strength=0.0,
        noise_scale=0.0, bump=0.0, rough_var=0.0, alpha=1.0, sheen=0.0, ior=1.5):
    """Create/refresh a physically plausible procedural material (no image textures)."""
    m, nt, bsdf = _principled(name)
    bsdf.inputs["Base Color"].default_value = (*base, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["IOR"].default_value = ior
    bsdf.inputs["Alpha"].default_value = alpha
    if "Sheen Weight" in bsdf.inputs:
        bsdf.inputs["Sheen Weight"].default_value = sheen
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    # wipe previous procedural nodes (keep output/principled)
    for n in list(nt.nodes):
        if n.type not in {"OUTPUT_MATERIAL", "BSDF_PRINCIPLED"}:
            nt.nodes.remove(n)
    if noise_scale > 0.0:
        tc = nt.nodes.new("ShaderNodeTexCoord")
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = noise_scale
        noise.inputs["Detail"].default_value = 4.0
        noise.inputs["Roughness"].default_value = 0.55
        nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
        if rough_var > 0.0:
            ramp = nt.nodes.new("ShaderNodeValToRGB")
            ramp.color_ramp.elements[0].position = 0.25
            ramp.color_ramp.elements[0].color = (max(0.02, rough - rough_var),) * 3 + (1.0,)
            ramp.color_ramp.elements[1].position = 0.75
            ramp.color_ramp.elements[1].color = (min(0.98, rough + rough_var),) * 3 + (1.0,)
            nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
            nt.links.new(ramp.outputs["Color"], bsdf.inputs["Roughness"])
        if bump > 0.0:
            bmp = nt.nodes.new("ShaderNodeBump")
            bmp.inputs["Strength"].default_value = bump
            bmp.inputs["Distance"].default_value = 0.002
            nt.links.new(noise.outputs["Fac"], bmp.inputs["Height"])
            nt.links.new(bmp.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def make_materials():
    mats = {}
    for name in ("M_HERO_Steel_Dark", "M_HERO_Steel_Bare", "M_HERO_Steel_Rust",
                 "M_HERO_Galvanized", "M_HERO_Aluminum", "M_HERO_Plastic", "M_HERO_Rubber",
                 "M_HERO_Concrete", "M_HERO_Gypsum", "M_HERO_Screen_Dead",
                 "M_HERO_Screen_Cracked", "M_HERO_Copper", "M_HERO_Water",
                 "M_HERO_LED_Red", "M_HERO_LED_Amber", "M_HERO_Paint_Green",
                 "M_HERO_Paint_Dark", "M_HERO_Belt_Red"):
        mats[name] = _mat(name)
    mats["laminate"] = pbr("M_HERO_Ops_Laminate", (0.026, 0.029, 0.032), 0.0, 0.36,
                           noise_scale=55.0, bump=0.10, rough_var=0.08)
    mats["olive"] = pbr("M_HERO_Ops_PaintOlive", (0.052, 0.064, 0.052), 0.0, 0.50,
                        noise_scale=70.0, bump=0.14, rough_var=0.10)
    mats["olive_dark"] = pbr("M_HERO_Ops_PaintOliveDark", (0.022, 0.030, 0.025), 0.0, 0.46,
                             noise_scale=80.0, bump=0.12, rough_var=0.08)
    mats["screen_glow"] = pbr("M_HERO_Ops_ScreenGlow", (0.0015, 0.005, 0.005), 0.0, 0.16,
                              emission=(0.020, 0.145, 0.13), emission_strength=0.24)
    mats["screen_glow_dim"] = pbr("M_HERO_Ops_ScreenGlowDim", (0.0015, 0.004, 0.006), 0.0, 0.18,
                                  emission=(0.022, 0.070, 0.105), emission_strength=0.13)
    mats["screen_scan"] = pbr("M_HERO_Ops_ScreenScan", (0.001, 0.004, 0.004), 0.0, 0.15,
                              emission=(0.040, 0.185, 0.135), emission_strength=0.32)
    mats["screen_ui"] = pbr("M_HERO_Ops_ScreenUI", (0.008, 0.012, 0.011), 0.0, 0.25,
                            emission=(0.075, 0.30, 0.26), emission_strength=0.38)
    mats["screen_dead_ops"] = pbr("M_HERO_Ops_ScreenDead", (0.0006, 0.0007, 0.0008), 0.0, 0.24,
                                  noise_scale=140.0, bump=0.03)
    mats["keycap"] = pbr("M_HERO_Ops_Keycap", (0.058, 0.061, 0.065), 0.0, 0.52,
                         noise_scale=220.0, bump=0.05)
    mats["ops_amber"] = pbr("M_HERO_Ops_LED_AmberDim", (0.06, 0.02, 0.004), 0.0, 0.20,
                            emission=(1.0, 0.34, 0.075), emission_strength=0.7)
    mats["ops_green"] = pbr("M_HERO_Ops_LED_GreenDim", (0.01, 0.05, 0.015), 0.0, 0.20,
                            emission=(0.08, 1.0, 0.22), emission_strength=0.9)
    mats["ops_white"] = pbr("M_HERO_Ops_LED_White", (0.10, 0.11, 0.13), 0.0, 0.22,
                            emission=(0.55, 0.72, 1.0), emission_strength=0.45)
    mats["fabric"] = pbr("M_HERO_Ops_ChairFabric", (0.006, 0.007, 0.008), 0.0, 0.96,
                         noise_scale=180.0, bump=0.22, rough_var=0.02, sheen=0.0)
    mats["chair_shell"] = pbr("M_HERO_Ops_ChairShell", (0.006, 0.007, 0.008), 0.0, 0.93,
                              noise_scale=130.0, bump=0.10, rough_var=0.03)
    for mn in ("M_HERO_Ops_ChairFabric", "M_HERO_Ops_ChairShell"):
        mm = bpy.data.materials.get(mn)
        bb = next(n for n in mm.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        bb.inputs["Specular IOR Level"].default_value = 0.18
    mats["label"] = pbr("M_HERO_Ops_Label", (0.52, 0.52, 0.48), 0.0, 0.55,
                        noise_scale=90.0, bump=0.05)
    mats["led_green"] = pbr("M_HERO_Ops_LED_Green", (0.005, 0.02, 0.008), 0.0, 0.15,
                            emission=(0.05, 1.0, 0.18), emission_strength=2.6)
    mats["led_blue"] = pbr("M_HERO_Ops_LED_Blue", (0.004, 0.012, 0.03), 0.0, 0.15,
                           emission=(0.05, 0.35, 1.0), emission_strength=2.2)
    mats["cable_blue"] = pbr("M_HERO_Ops_CableBlue", (0.008, 0.022, 0.055), 0.0, 0.55,
                             noise_scale=120.0, bump=0.06)
    mats["dust"] = pbr("M_HERO_Ops_Dust", (0.06, 0.052, 0.043), 0.0, 0.98,
                       noise_scale=40.0, bump=0.05, alpha=0.42)
    mats["dust"].surface_render_method = "DITHERED"
    mats["ceiling"] = pbr("M_HERO_Ops_CeilingTile", (0.23, 0.225, 0.21), 0.0, 0.94,
                          noise_scale=35.0, bump=0.18, rough_var=0.03)
    mats["grille"] = pbr("M_HERO_Ops_Grille", (0.012, 0.014, 0.015), 0.0, 0.42,
                         noise_scale=150.0, bump=0.06)
    return mats


# --------------------------------------------------------------------------------------
# low level mesh helpers
# --------------------------------------------------------------------------------------
def _box_uv(me, scale=1.0):
    uv_layer = None
    if me.uv_layers:
        uv_layer = me.uv_layers.get("UVMap")
        if uv_layer is None:
            uv_layer = me.uv_layers[0]
            uv_layer.name = "UVMap"
    else:
        uv_layer = me.uv_layers.new(name="UVMap")
    uvs = uv_layer.data
    verts = me.vertices
    for poly in me.polygons:
        n = poly.normal
        ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
        for li in poly.loop_indices:
            co = verts[me.loops[li].vertex_index].co
            if az >= ax and az >= ay:
                u, v = co.x, co.y
            elif ax >= ay:
                u, v = co.y, co.z
            else:
                u, v = co.x, co.z
            uvs[li].uv = (u * scale, v * scale)


def _finish_bm(bm, me, smooth=True, sharp_angle=38.0):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    for f in bm.faces:
        f.smooth = smooth
    lim = math.radians(sharp_angle)
    for e in bm.edges:
        if len(e.link_faces) == 2:
            try:
                e.smooth = e.calc_face_angle(0.0) < lim
            except Exception:
                e.smooth = True
        else:
            e.smooth = False
    bm.to_mesh(me)
    bm.free()


def _link(name, me, coll, mat=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    if mat is not None:
        me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    coll.objects.link(ob)
    return ob


def box(name, size, center, mat, coll, rot=(0, 0, 0), bevel=0.004, seg=3,
        uv_scale=1.0, smooth=True):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.verts.ensure_lookup_table()
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
    if bevel > 0.0:
        b = min(bevel, min(size) * 0.45)
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=b, offset_type="OFFSET",
                        segments=seg, profile=0.5, affect="EDGES", clamp_overlap=True)
    me = bpy.data.meshes.new(name)
    _finish_bm(bm, me, smooth=smooth)
    _box_uv(me, uv_scale)
    return _link(name, me, coll, mat, center, rot)


def cyl(name, radius, depth, center, mat, coll, rot=(0, 0, 0), segments=20,
        bevel=0.002, seg=2, r2=None, uv_scale=1.0):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                          radius1=radius, radius2=(radius if r2 is None else r2),
                          depth=depth)
    bm.edges.ensure_lookup_table()
    if bevel > 0.0:
        rim = [e for e in bm.edges if len(e.link_faces) == 2 and e.calc_face_angle(0.0) > math.radians(50)]
        if rim:
            bmesh.ops.bevel(bm, geom=rim, offset=min(bevel, radius * 0.35, depth * 0.3),
                            offset_type="OFFSET", segments=seg, profile=0.5,
                            affect="EDGES", clamp_overlap=True)
    me = bpy.data.meshes.new(name)
    _finish_bm(bm, me, smooth=True, sharp_angle=46.0)
    _box_uv(me, uv_scale)
    return _link(name, me, coll, mat, center, rot)


def tube(name, pts, radius, mat, coll, sides=8, cap=True, uv_scale=1.0):
    pts = [Vector(p) for p in pts]
    n = len(pts)
    if n < 2:
        return None
    tangents = []
    for i in range(n):
        if i == 0:
            t = pts[1] - pts[0]
        elif i == n - 1:
            t = pts[-1] - pts[-2]
        else:
            t = pts[i + 1] - pts[i - 1]
        tangents.append(t.normalized())
    # initial frame
    t0 = tangents[0]
    ref = Vector((0, 0, 1)) if abs(t0.z) < 0.9 else Vector((1, 0, 0))
    nrm = (ref - t0 * ref.dot(t0)).normalized()
    rings = []
    bm = bmesh.new()
    for i, (p, t) in enumerate(zip(pts, tangents)):
        if i > 0:
            q = tangents[i - 1].rotation_difference(t)
            nrm = (q @ nrm).normalized()
        binrm = t.cross(nrm).normalized()
        ring = []
        for s in range(sides):
            a = TAU * s / sides
            co = p + nrm * (math.cos(a) * radius) + binrm * (math.sin(a) * radius)
            ring.append(bm.verts.new(co))
        rings.append(ring)
    bm.verts.ensure_lookup_table()
    for i in range(n - 1):
        for s in range(sides):
            a = rings[i][s]
            b = rings[i][(s + 1) % sides]
            c = rings[i + 1][(s + 1) % sides]
            d = rings[i + 1][s]
            bm.faces.new((a, b, c, d))
    if cap:
        c0 = bm.verts.new(pts[0])
        c1 = bm.verts.new(pts[-1])
        for s in range(sides):
            bm.faces.new((c0, rings[0][(s + 1) % sides], rings[0][s]))
            bm.faces.new((c1, rings[-1][s], rings[-1][(s + 1) % sides]))
    me = bpy.data.meshes.new(name)
    _finish_bm(bm, me, smooth=True, sharp_angle=50.0)
    _box_uv(me, uv_scale)
    return _link(name, me, coll, mat, (0, 0, 0))


def cable(name, p0, p1, sag, radius, mat, coll, n=14, sides=8, wiggle=0.0, seed=1):
    p0, p1 = Vector(p0), Vector(p1)
    rnd = random.Random(seed)
    pts = []
    for i in range(n):
        t = i / (n - 1)
        p = p0.lerp(p1, t)
        p.z -= math.sin(math.pi * t) * sag
        if wiggle:
            p.x += math.sin(math.pi * t) * wiggle * math.sin(t * 7.0 + seed)
            p.y += math.sin(math.pi * t) * wiggle * 0.5 * math.cos(t * 5.0 + seed)
        pts.append(p)
    return tube(name, pts, radius, mat, coll, sides=sides)


def coil(name, start, axis, radius, pitch, turns, wire_r, mat, coll, n=16, sides=6):
    """Helical coiled cord. axis = direction the coil advances (Vector)."""
    start = Vector(start)
    axis = Vector(axis).normalized()
    ref = Vector((0, 0, 1)) if abs(axis.z) < 0.9 else Vector((1, 0, 0))
    u = (ref - axis * ref.dot(axis)).normalized()
    v = axis.cross(u).normalized()
    pts = []
    seg = max(12, int(turns * n))
    for i in range(seg + 1):
        t = i / seg
        a = TAU * turns * t
        p = start + axis * (pitch * turns * t) + u * (math.cos(a) * radius) + v * (math.sin(a) * radius)
        pts.append(p)
    return tube(name, pts, wire_r, mat, coll, sides=sides)


def bolts(name, positions, normal, radius, depth, mat, coll, segments=6, washer=True):
    """Single mesh with many hex-head bolts, oriented along `normal`."""
    normal = Vector(normal).normalized()
    quat = normal.to_track_quat("Z", "Y")
    bm = bmesh.new()
    for p in positions:
        M = Matrix.Translation(Vector(p)) @ quat.to_matrix().to_4x4()
        if washer:
            bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12,
                                  radius1=radius * 1.55, radius2=radius * 1.55,
                                  depth=depth * 0.28, matrix=M @ Matrix.Translation((0, 0, depth * 0.14)))
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                              radius1=radius, radius2=radius * 0.94,
                              depth=depth, matrix=M @ Matrix.Translation((0, 0, depth * 0.75)))
    me = bpy.data.meshes.new(name)
    _finish_bm(bm, me, smooth=True, sharp_angle=42.0)
    _box_uv(me)
    return _link(name, me, coll, mat, (0, 0, 0))


def text_mesh(name, body, size, center, rot, mat, coll, extrude=0.0015, align="CENTER"):
    cu = bpy.data.curves.new(name + "_FONT", "FONT")
    cu.body = body
    cu.size = size
    cu.align_x = align
    cu.align_y = "CENTER"
    cu.extrude = extrude
    cu.resolution_u = 2
    cu.bevel_depth = 0.0004
    cu.bevel_resolution = 1
    ob = bpy.data.objects.new(name + "_TMP", cu)
    coll.objects.link(ob)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.curves.remove(cu)
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(me)
    bm.free()
    _box_uv(me)
    return _link(name, me, coll, mat, center, rot)


def join(objs, name, coll):
    objs = [o for o in objs if o and o.name in bpy.data.objects]
    if not objs:
        return None
    if len(objs) == 1:
        ob = objs[0]
        ob.name = name
        return ob
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    try:
        bpy.ops.object.join()
    except Exception as e:
        print("JOIN FAILED", name, e)
        return objs[0]
    ob = bpy.context.view_layer.objects.active
    ob.name = name
    for o in bpy.data.objects:
        if o.name.startswith(name + ".") and o.type == "MESH" and o.users_collection and not o.users_collection[0].objects.get(o.name):
            pass
    return ob


def fix_inverted_islands(ob):
    """Flip any closed shell whose signed volume is negative (kitbash normal repair)."""
    if ob is None or ob.type != "MESH":
        return 0
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    parent = list(range(len(bm.verts)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for e in bm.edges:
        a, b = find(e.verts[0].index), find(e.verts[1].index)
        if a != b:
            parent[a] = b
    isl = [find(i) for i in range(len(bm.verts))]
    closed = {}
    for g in set(isl):
        closed[g] = True
    for e in bm.edges:
        if len(e.link_faces) != 2:
            closed[isl[e.verts[0].index]] = False
    vol = {g: 0.0 for g in closed}
    for f in bm.faces:
        vs = [v.index for v in f.verts]
        if len(vs) < 3:
            continue
        a = bm.verts[vs[0]].co
        g = isl[vs[0]]
        for k in range(1, len(vs) - 1):
            b = bm.verts[vs[k]].co
            c = bm.verts[vs[k + 1]].co
            vol[g] += a.dot(b.cross(c)) / 6.0
    flip = {g for g in closed if closed[g] and vol[g] < -1e-12}
    if flip:
        faces = [f for f in bm.faces if isl[f.verts[0].index] in flip]
        bmesh.ops.reverse_faces(bm, faces=faces)
        bm.to_mesh(me)
    bm.free()
    return len(flip)


def weighted_normal(ob, weight=50):
    if ob is None:
        return
    for m in list(ob.modifiers):
        if m.type == "WEIGHTED_NORMAL":
            ob.modifiers.remove(m)
    m = ob.modifiers.new("WeightedNormal", "WEIGHTED_NORMAL")
    m.mode = "FACE_AREA"
    m.weight = weight
    m.keep_sharp = True


def transform_objects(objs, matrix):
    for o in objs:
        o.matrix_world = matrix @ o.matrix_world


def displace_verts(ob, amount, scale=8.0, seed=0, axis_lock=None):
    rnd = random.Random(seed)
    for v in ob.data.vertices:
        n = v.normal
        d = rnd.uniform(-amount, amount)
        v.co += Vector((n.x * d, n.y * d, n.z * d))


def irregular_disc(name, center, radius_x, radius_y, z, mat, coll, n=18, seed=1):
    rnd = random.Random(seed)
    bm = bmesh.new()
    c = bm.verts.new((center[0], center[1], z))
    ring = []
    for i in range(n):
        a = TAU * i / n
        r = 1.0 + rnd.uniform(-0.22, 0.22)
        ring.append(bm.verts.new((center[0] + math.cos(a) * radius_x * r,
                                  center[1] + math.sin(a) * radius_y * r, z)))
    for i in range(n):
        bm.faces.new((c, ring[i], ring[(i + 1) % n]))
    me = bpy.data.meshes.new(name)
    _finish_bm(bm, me, smooth=False)
    _box_uv(me)
    return _link(name, me, coll, mat, (0, 0, 0))
