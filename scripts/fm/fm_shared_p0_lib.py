"""
FRECUENCIA MUERTA - P0a shared hero library: helpers.

All geometry is built at real scale in metres, bevelled, with UVs and a
single consolidated material set.  Objects are assembled with local
coordinates and grouped under an Empty root whose origin is the asset
pivot (floor / hinge / wall mount / service port).

Run inside Blender 5.2 via blender-mcp:
    exec(open("/home/riyo/Documentos/game/scripts/fm/fm_shared_p0_lib.py").read())
"""
import bpy
import bmesh
import math
import json
from mathutils import Vector, Matrix

ROOT_COLL = "L1_SHARED_HERO"
MAT_PREFIX = "M_SH_"

# ---------------------------------------------------------------------------
# collections
# ---------------------------------------------------------------------------

def get_coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    return c


def ensure_tree():
    root = get_coll(ROOT_COLL)
    doors = get_coll("DOORS", root)
    lights = get_coll("LIGHTING", root)
    services = get_coll("SERVICES", root)
    test = get_coll("P0_TEST_ASSEMBLY", root)
    return {"root": root, "doors": doors, "lighting": lights,
            "services": services, "test": test}


def clear_collection_tree(name):
    """Delete a collection created by this P0 pass and all its objects.

    Guarded: only names under L1_SHARED_HERO are accepted.
    """
    if name != ROOT_COLL and not bpy.data.collections.get(name):
        return
    if name != ROOT_COLL:
        parent = bpy.data.collections.get(ROOT_COLL)
        c = bpy.data.collections.get(name)
        if c is None or parent is None or c.name not in [x.name for x in parent.children]:
            raise RuntimeError("refusing to clear non-shared collection: " + name)
    col = bpy.data.collections.get(name)
    if col is None:
        return
    # collect objects recursively (never touch objects outside this tree)
    obs = set()
    stack = [col]
    while stack:
        c = stack.pop()
        obs.update(c.objects)
        stack.extend(c.children)
    for ob in list(obs):
        data = ob.data
        bpy.data.objects.remove(ob, do_unlink=True)
        if data is not None and getattr(data, "users", 0) == 0:
            try:
                if isinstance(data, bpy.types.Mesh):
                    bpy.data.meshes.remove(data)
            except Exception:
                pass
    # remove children then the collection
    for child in list(col.children):
        clear_collection_tree(child.name)
    bpy.data.collections.remove(col)


# ---------------------------------------------------------------------------
# materials
# ---------------------------------------------------------------------------

def _c(r, g, b, a=1.0):
    return (r, g, b, a)


def _srgb_to_linear(v):
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def srgb(r, g, b):
    """sRGB 0-255 -> linear tuple, for readable measured values."""
    return (_srgb_to_linear(r / 255.0), _srgb_to_linear(g / 255.0),
            _srgb_to_linear(b / 255.0), 1.0)


def _pbr(name, base, metallic, rough, scale=35.0, bump=0.0015,
         dirt=0.30, micro=180.0, rough_var=0.10, emission=None,
         emission_strength=0.0, alpha=None, transmission=0.0,
         coat=0.0):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (700, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (420, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tex = nt.nodes.new("ShaderNodeTexCoord")
    tex.location = (-900, 0)
    mapn = nt.nodes.new("ShaderNodeMapping")
    mapn.location = (-720, 0)
    mapn.inputs["Scale"].default_value = (1.0, 1.0, 1.0)
    nt.links.new(tex.outputs["Object"], mapn.inputs["Vector"])

    # macro grime / colour variation
    n1 = nt.nodes.new("ShaderNodeTexNoise")
    n1.location = (-520, 180)
    n1.inputs["Scale"].default_value = scale
    n1.inputs["Detail"].default_value = 5.0
    n1.inputs["Roughness"].default_value = 0.62
    nt.links.new(mapn.outputs["Vector"], n1.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.location = (-320, 180)
    ramp.color_ramp.elements[0].position = 0.18
    ramp.color_ramp.elements[0].color = (base[0] * 0.52, base[1] * 0.52, base[2] * 0.52, 1)
    ramp.color_ramp.elements[1].position = 0.82
    ramp.color_ramp.elements[1].color = (min(base[0] * 1.18, 1), min(base[1] * 1.18, 1), min(base[2] * 1.18, 1), 1)
    nt.links.new(n1.outputs["Fac"], ramp.inputs["Fac"])

    # universal dirt layer: AO darkens crevices (standard 19.2.D)
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion")
    ao.location = (-520, -80)
    ao.inputs["Distance"].default_value = 0.18
    ao_ramp = nt.nodes.new("ShaderNodeValToRGB")
    ao_ramp.location = (-320, -80)
    ao_ramp.color_ramp.elements[0].position = 0.0
    ao_ramp.color_ramp.elements[0].color = (0.32, 0.29, 0.25, 1)
    ao_ramp.color_ramp.elements[1].position = 1.0
    ao_ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
    nt.links.new(ao.outputs["AO"], ao_ramp.inputs["Fac"])

    mix = nt.nodes.new("ShaderNodeMixRGB")
    mix.location = (-60, 120)
    mix.blend_type = "MULTIPLY"
    mix.inputs["Fac"].default_value = 0.55
    nt.links.new(ramp.outputs["Color"], mix.inputs["Color1"])
    nt.links.new(ao_ramp.outputs["Color"], mix.inputs["Color2"])
    nt.links.new(mix.outputs["Color"], bsdf.inputs["Base Color"])

    # micro roughness + bump
    n2 = nt.nodes.new("ShaderNodeTexNoise")
    n2.location = (-520, -320)
    n2.inputs["Scale"].default_value = micro
    n2.inputs["Detail"].default_value = 3.0
    n2.inputs["Roughness"].default_value = 0.55
    nt.links.new(mapn.outputs["Vector"], n2.inputs["Vector"])
    rr = nt.nodes.new("ShaderNodeValToRGB")
    rr.location = (-300, -320)
    rr.color_ramp.elements[0].position = 0.2
    rr.color_ramp.elements[0].color = (max(rough - rough_var, 0.02),) * 3 + (1,)
    rr.color_ramp.elements[1].position = 0.8
    rr.color_ramp.elements[1].color = (min(rough + rough_var, 1.0),) * 3 + (1,)
    nt.links.new(n2.outputs["Fac"], rr.inputs["Fac"])
    nt.links.new(rr.outputs["Color"], bsdf.inputs["Roughness"])

    bumpn = nt.nodes.new("ShaderNodeBump")
    bumpn.location = (60, -320)
    bumpn.inputs["Strength"].default_value = min(0.35, max(0.02, bump * 12))
    bumpn.inputs["Distance"].default_value = bump
    nt.links.new(n2.outputs["Fac"], bumpn.inputs["Height"])
    nt.links.new(bumpn.outputs["Normal"], bsdf.inputs["Normal"])

    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = rough
    if alpha is not None:
        bsdf.inputs["Alpha"].default_value = alpha
        m.surface_render_method = "BLENDED"
    if transmission:
        bsdf.inputs["Transmission Weight"].default_value = transmission
    if coat:
        bsdf.inputs["Coat Weight"].default_value = coat
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = (emission[0], emission[1], emission[2], 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    # viewport hint only
    m.diffuse_color = (base[0], base[1], base[2], 1)
    return m


MATS = {}


def ensure_materials():
    if len(MATS) >= 20 and "glass" in MATS:
        return MATS
    MATS.clear()
    M = MATS
    M["galv"] = _pbr("M_SH_Steel_Galv", srgb(186, 190, 187), 1.0, 0.42,
                     scale=22, bump=0.0012, micro=160, rough_var=0.11)
    M["steel_dark"] = _pbr("M_SH_Steel_Dark", srgb(74, 78, 80), 1.0, 0.38,
                           scale=30, bump=0.0009, micro=200, rough_var=0.08)
    M["steel_bare"] = _pbr("M_SH_Steel_Stainless", srgb(198, 202, 204), 1.0, 0.27,
                           scale=45, bump=0.0006, micro=260, rough_var=0.10)
    M["paint_door"] = _pbr("M_SH_Paint_SecurityGreen", srgb(38, 62, 49), 0.0, 0.55,
                           scale=16, bump=0.0016, micro=210, rough_var=0.13)
    M["paint_orange"] = _pbr("M_SH_Paint_SafetyOrange", srgb(214, 92, 26), 0.0, 0.52,
                             scale=20, bump=0.0012, micro=180, rough_var=0.10)
    M["rubber"] = _pbr("M_SH_Rubber_Seal", srgb(28, 29, 28), 0.0, 0.86,
                       scale=60, bump=0.0018, micro=320, rough_var=0.05)
    M["aluminum"] = _pbr("M_SH_Aluminum", srgb(190, 196, 200), 1.0, 0.33,
                         scale=48, bump=0.0007, micro=280, rough_var=0.10)
    M["brass"] = _pbr("M_SH_Brass", srgb(168, 118, 54), 1.0, 0.30,
                      scale=42, bump=0.0008, micro=240, rough_var=0.09)
    M["copper"] = _pbr("M_SH_Copper", srgb(150, 82, 44), 1.0, 0.34,
                       scale=40, bump=0.0008, micro=240, rough_var=0.10)
    M["sprink_red"] = _pbr("M_SH_Sprinkler_Red", srgb(152, 24, 18), 0.0, 0.46,
                           scale=24, bump=0.0012, micro=190, rough_var=0.10)
    M["conduit"] = _pbr("M_SH_Conduit_Galv", srgb(160, 164, 162), 0.92, 0.44,
                        scale=36, bump=0.0009, micro=220, rough_var=0.10)
    M["cable"] = _pbr("M_SH_Cable_Black", srgb(20, 20, 21), 0.0, 0.72,
                      scale=80, bump=0.0015, micro=360, rough_var=0.06)
    M["lens_red"] = _pbr("M_SH_Lens_Red_On", _c(0.36, 0.006, 0.004), 0.0, 0.20,
                         scale=70, bump=0.0004, micro=300, rough_var=0.04,
                         emission=_c(1.0, 0.035, 0.012), emission_strength=6.0)
    M["lens_red_dead"] = _pbr("M_SH_Lens_Red_Off", _c(0.16, 0.018, 0.012), 0.0, 0.33,
                              scale=55, bump=0.0005, micro=260, rough_var=0.06)
    M["diffuser_on"] = _pbr("M_SH_Diffuser_On", _c(0.78, 0.76, 0.68), 0.0, 0.36,
                            scale=90, bump=0.0003, micro=420, rough_var=0.05,
                            emission=_c(1.0, 0.90, 0.72), emission_strength=2.6)
    M["diffuser_off"] = _pbr("M_SH_Diffuser_Off", _c(0.54, 0.56, 0.52), 0.0, 0.44,
                             scale=80, bump=0.0004, micro=380, rough_var=0.05)
    M["glass"] = _pbr("M_SH_Vision_Glass", _c(0.56, 0.66, 0.66), 0.0, 0.05,
                      scale=20, bump=0.0002, micro=200, rough_var=0.02,
                      alpha=0.22)
    M["label"] = _pbr("M_SH_Label_Aluminium", srgb(196, 190, 174), 0.35, 0.52,
                      scale=60, bump=0.0005, micro=300, rough_var=0.06)
    M["concrete"] = _pbr("M_SH_Test_Concrete", srgb(102, 100, 96), 0.0, 0.90,
                         scale=6, bump=0.004, micro=70, rough_var=0.06)
    M["firestop"] = _pbr("M_SH_Firestop_Red", srgb(154, 38, 28), 0.0, 0.78,
                         scale=30, bump=0.003, micro=120, rough_var=0.06)
    M["plastic"] = _pbr("M_SH_Plastic_Black", srgb(36, 37, 37), 0.0, 0.58,
                        scale=50, bump=0.0008, micro=260, rough_var=0.06)
    M["insulation"] = _pbr("M_SH_Insulation_Foil", srgb(176, 172, 158), 0.55, 0.62,
                           scale=12, bump=0.003, micro=90, rough_var=0.08)
    return M


# ---------------------------------------------------------------------------
# bmesh primitives
# ---------------------------------------------------------------------------

def _finish_bm(bm, bevel=0.0, segments=3, remove_doubles=True):
    if remove_doubles:
        bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    if bevel and bevel > 0:
        bm.edges.ensure_lookup_table()
        bmesh.ops.bevel(bm, geom=bm.edges[:], offset=bevel, offset_type='OFFSET',
                        segments=segments, profile=0.5, affect='EDGES',
                        clamp_overlap=True, loop_slide=True,
                        miter_outer='ARC')
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bmesh.ops.dissolve_degenerate(bm, dist=1e-6, edges=bm.edges[:])
    return bm


def bm_box(sx, sy, sz, center=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= sx
        v.co.y *= sy
        v.co.z *= sz
        v.co += Vector(center)
    return bm


def bm_cyl(r, depth, center=(0, 0, 0), axis='Z', segments=16):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False,
                          segments=segments, radius1=r, radius2=r, depth=depth)
    if axis == 'X':
        bmesh.ops.rotate(bm, cent=(0, 0, 0),
                         matrix=Matrix.Rotation(math.radians(90), 3, 'Y'),
                         verts=bm.verts[:])
    elif axis == 'Y':
        bmesh.ops.rotate(bm, cent=(0, 0, 0),
                         matrix=Matrix.Rotation(math.radians(90), 3, 'X'),
                         verts=bm.verts[:])
    bmesh.ops.translate(bm, vec=Vector(center), verts=bm.verts[:])
    return bm


def bm_cone(r1, r2, depth, center=(0, 0, 0), axis='Z', segments=16):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False,
                          segments=segments, radius1=r1, radius2=r2, depth=depth)
    if axis == 'X':
        bmesh.ops.rotate(bm, cent=(0, 0, 0),
                         matrix=Matrix.Rotation(math.radians(90), 3, 'Y'),
                         verts=bm.verts[:])
    elif axis == 'Y':
        bmesh.ops.rotate(bm, cent=(0, 0, 0),
                         matrix=Matrix.Rotation(math.radians(90), 3, 'X'),
                         verts=bm.verts[:])
    bmesh.ops.translate(bm, vec=Vector(center), verts=bm.verts[:])
    return bm


def bm_prism_x(profile_yz, width, center=(0, 0, 0)):
    """Extrude a closed 2D profile (list of (y,z)) along X."""
    bm = bmesh.new()
    a, b = [], []
    x0, x1 = -width / 2.0, width / 2.0
    for (yy, zz) in profile_yz:
        a.append(bm.verts.new((x0, yy, zz)))
        b.append(bm.verts.new((x1, yy, zz)))
    n = len(profile_yz)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))
    bm.faces.new(list(reversed(a)))
    bm.faces.new(b)
    bmesh.ops.translate(bm, vec=Vector(center), verts=bm.verts[:])
    return bm


def bm_rect_frame_x(x0, x1, ow, oh, iw, ih, cy=0.0, cz=0.0):
    """Closed rectangular ring (flange / sleeve end plate) along X."""
    bm = bmesh.new()
    def V(x, y, z):
        return bm.verts.new((x, y, z))
    o0 = [V(x0, cy - ow / 2, cz - oh / 2), V(x0, cy + ow / 2, cz - oh / 2),
          V(x0, cy + ow / 2, cz + oh / 2), V(x0, cy - ow / 2, cz + oh / 2)]
    o1 = [V(x1, cy - ow / 2, cz - oh / 2), V(x1, cy + ow / 2, cz - oh / 2),
          V(x1, cy + ow / 2, cz + oh / 2), V(x1, cy - ow / 2, cz + oh / 2)]
    i0 = [V(x0, cy - iw / 2, cz - ih / 2), V(x0, cy + iw / 2, cz - ih / 2),
          V(x0, cy + iw / 2, cz + ih / 2), V(x0, cy - iw / 2, cz + ih / 2)]
    i1 = [V(x1, cy - iw / 2, cz - ih / 2), V(x1, cy + iw / 2, cz - ih / 2),
          V(x1, cy + iw / 2, cz + ih / 2), V(x1, cy - iw / 2, cz + ih / 2)]
    for k in range(4):
        j = (k + 1) % 4
        bm.faces.new((o0[k], o0[j], i0[j], i0[k]))       # x0 face
        bm.faces.new((i1[k], i1[j], o1[j], o1[k]))       # x1 face
        bm.faces.new((o0[j], o0[k], o1[k], o1[j]))       # outer
        bm.faces.new((i0[k], i0[j], i1[j], i1[k]))       # inner
    return bm


def bm_rect_tube_x(x0, x1, ow, oh, wall, cy=0.0, cz=0.0):
    iw, ih = ow - 2 * wall, oh - 2 * wall
    return bm_rect_frame_x(x0, x1, ow, oh, iw, ih, cy, cz)


def bm_rect_loft_x(x0, x1, w0, h0, w1, h1, wall, cy=0.0, cz=0.0):
    bm = bmesh.new()
    def corners(x, w, h):
        return [bm.verts.new((x, cy - w / 2, cz - h / 2)),
                bm.verts.new((x, cy + w / 2, cz - h / 2)),
                bm.verts.new((x, cy + w / 2, cz + h / 2)),
                bm.verts.new((x, cy - w / 2, cz + h / 2))]
    def inner(x, w, h):
        return [bm.verts.new((x, cy - (w - 2 * wall) / 2, cz - (h - 2 * wall) / 2)),
                bm.verts.new((x, cy + (w - 2 * wall) / 2, cz - (h - 2 * wall) / 2)),
                bm.verts.new((x, cy + (w - 2 * wall) / 2, cz + (h - 2 * wall) / 2)),
                bm.verts.new((x, cy - (w - 2 * wall) / 2, cz + (h - 2 * wall) / 2))]
    o0, o1 = corners(x0, w0, h0), corners(x1, w1, h1)
    i0, i1 = inner(x0, w0, h0), inner(x1, w1, h1)
    for k in range(4):
        j = (k + 1) % 4
        bm.faces.new((o0[k], o0[j], o1[j], o1[k]))
        bm.faces.new((i1[k], i1[j], i0[j], i0[k]))
        bm.faces.new((o0[k], o0[j], i0[j], i0[k]))
        bm.faces.new((i1[k], i1[j], o1[j], o1[k]))
    return bm


def bm_pipe_x(x0, x1, r_out, r_in, cy=0.0, cz=0.0, segments=20):
    bm = bmesh.new()
    a_o, a_i, b_o, b_i = [], [], [], []
    for i in range(segments):
        t = 2 * math.pi * i / segments
        y, z = math.cos(t), math.sin(t)
        a_o.append(bm.verts.new((x0, cy + y * r_out, cz + z * r_out)))
        a_i.append(bm.verts.new((x0, cy + y * r_in, cz + z * r_in)))
        b_o.append(bm.verts.new((x1, cy + y * r_out, cz + z * r_out)))
        b_i.append(bm.verts.new((x1, cy + y * r_in, cz + z * r_in)))
    for i in range(segments):
        j = (i + 1) % segments
        bm.faces.new((a_o[i], a_o[j], b_o[j], b_o[i]))
        bm.faces.new((b_i[i], b_i[j], a_i[j], a_i[i]))
        bm.faces.new((a_i[i], a_i[j], a_o[j], a_o[i]))
        bm.faces.new((b_o[i], b_o[j], b_i[j], b_i[i]))
    return bm


def bm_pipe_arc(start=(0, 0, 0), bend=0.55, r_out=0.05, r_in=0.043,
                angle=90.0, seg=8, ring=16):
    """90 deg elbow, starts at origin heading +X, bends towards +Y."""
    bm = bmesh.new()
    rings = []
    for s in range(seg + 1):
        th = math.radians(-90.0 + angle * s / seg)
        px = bend * math.cos(th)
        py = bend + bend * math.sin(th)
        nx, ny = math.cos(th), math.sin(th)
        ro, ri = [], []
        for k in range(ring):
            ph = 2 * math.pi * k / ring
            c, sn = math.cos(ph), math.sin(ph)
            for rr, lst in ((r_out, ro), (r_in, ri)):
                lst.append(bm.verts.new((start[0] + px + nx * rr * c,
                                         start[1] + py + ny * rr * c,
                                         start[2] + rr * sn)))
        rings.append((ro, ri))
    for s in range(seg):
        ro0, ri0 = rings[s]
        ro1, ri1 = rings[s + 1]
        for k in range(ring):
            j = (k + 1) % ring
            bm.faces.new((ro0[k], ro0[j], ro1[j], ro1[k]))
            bm.faces.new((ri1[k], ri1[j], ri0[j], ri0[k]))
    ro0, ri0 = rings[0]
    ro1, ri1 = rings[-1]
    for k in range(ring):
        j = (k + 1) % ring
        bm.faces.new((ri0[k], ri0[j], ro0[j], ro0[k]))
        bm.faces.new((ro1[k], ro1[j], ri1[j], ri1[k]))
    return bm


# ---------------------------------------------------------------------------
# object assembly
# ---------------------------------------------------------------------------

def make_part(name, bm, mat, coll, bevel=0.0015, segments=3, smooth=True):
    _finish_bm(bm, bevel=bevel, segments=segments)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    if mat is not None:
        me.materials.append(mat)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    return ob


def box(coll, name, sx, sy, sz, center, mat, bevel=0.002, seg=3):
    b = min(bevel, min(sx, sy, sz) * 0.38) if bevel else 0.0
    return make_part(name, bm_box(sx, sy, sz, center), mat, coll, b, seg)


def cyl(coll, name, r, depth, center, mat, axis='Z', seg=16, bevel=0.0008, bseg=2):
    b = min(bevel, r * 0.35, depth * 0.35) if bevel else 0.0
    return make_part(name, bm_cyl(r, depth, center, axis, seg), mat, coll, b, bseg)


def cone(coll, name, r1, r2, depth, center, mat, axis='Z', seg=16, bevel=0.0008, bseg=2):
    b = min(bevel, min(r1, r2) * 0.35, depth * 0.35) if bevel else 0.0
    return make_part(name, bm_cone(r1, r2, depth, center, axis, seg), mat, coll, b, bseg)


def prism(coll, name, profile, width, center, mat, bevel=0.0015, seg=3):
    return make_part(name, bm_prism_x(profile, width, center), mat, coll, bevel, seg)


def frame_x(coll, name, x0, x1, ow, oh, iw, ih, cy, cz, mat, bevel=0.0008, seg=2):
    return make_part(name, bm_rect_frame_x(x0, x1, ow, oh, iw, ih, cy, cz), mat, coll, bevel, seg)


def tube_x(coll, name, x0, x1, ow, oh, wall, cy, cz, mat, bevel=0.0012, seg=2):
    return make_part(name, bm_rect_tube_x(x0, x1, ow, oh, wall, cy, cz), mat, coll, bevel, seg)


def pipe_x(coll, name, x0, x1, ro, ri, cy, cz, mat, segments=20, bevel=0.0006, seg=2):
    return make_part(name, bm_pipe_x(x0, x1, ro, ri, cy, cz, segments), mat, coll, bevel, seg)


def _select_only(ob):
    for o in bpy.context.selected_objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob


def consolidate_materials(ob):
    mats, mapping = [], {}
    for i, slot in enumerate(ob.material_slots):
        m = slot.material
        if m is None:
            continue
        if m not in mats:
            mats.append(m)
        mapping[i] = mats.index(m)
    old = [p.material_index for p in ob.data.polygons]
    ob.data.materials.clear()
    for m in mats:
        ob.data.materials.append(m)
    for p, i in zip(ob.data.polygons, old):
        p.material_index = mapping.get(i, 0)


def smart_uv(ob):
    _select_only(ob)
    try:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.004,
                                 area_weight=0.0, correct_aspect=True,
                                 scale_to_bounds=False)
        bpy.ops.object.mode_set(mode='OBJECT')
        return True
    except Exception as exc:
        if ob.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        # fallback: cube projection per face via operator
        try:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.cube_project(cube_size=1.0, correct_aspect=True)
            bpy.ops.object.mode_set(mode='OBJECT')
            return True
        except Exception:
            if ob.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            print("UV fallback failed", ob.name, exc)
            return False


def join_group(coll, name, parts, uv=True, wn=True):
    if not parts:
        return None
    for o in bpy.context.selected_objects:
        o.select_set(False)
    for o in parts:
        o.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    if len(parts) > 1:
        bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = name
    ob.data.name = name
    # final normal pass over the joined mesh
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(ob.data)
    bm.free()
    consolidate_materials(ob)
    for p in ob.data.polygons:
        p.use_smooth = True
    if wn:
        m = ob.modifiers.new("FN_WeightedNormal", "WEIGHTED_NORMAL")
        m.mode = 'FACE_AREA'
        m.weight = 50
        m.keep_sharp = True
        _select_only(ob)
        try:
            bpy.ops.object.modifier_apply(modifier=m.name)
        except Exception as exc:
            print("WN apply failed", name, exc)
    if uv:
        smart_uv(ob)
    ob.location = (0, 0, 0)
    ob.rotation_euler = (0, 0, 0)
    ob.scale = (1, 1, 1)
    return ob


def make_root(name, coll, display_size=0.4):
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_type = 'PLAIN_AXES'
    ob.empty_display_size = display_size
    coll.objects.link(ob)
    return ob


def parent_to(ob, root):
    ob.parent = root
    ob.matrix_parent_inverse = Matrix.Identity(4)
    return ob


def tri_count(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def finalize_master(root, coll, meshes, location=(0, 0, 0), meta=None):
    for ob in meshes:
        if ob is None:
            continue
        if ob.name not in coll.objects:
            coll.objects.link(ob)
        parent_to(ob, root)
    root.location = Vector(location)
    root["fm_asset"] = root.name
    root["fm_generation"] = "VERIFIED_P0A"
    root["fm_lod"] = "LOD0"
    tris = sum(tri_count(o) for o in meshes if o)
    root["fm_tris"] = tris
    if meta:
        for k, v in meta.items():
            root[k] = v
    return root


# ---------------------------------------------------------------------------
# detail helpers (screws / bolts)
# ---------------------------------------------------------------------------

def screw(coll, name, center, normal, r=0.005, mat=None, slot_mat=None, length=0.003):
    """Cross-slot screw. normal is the outward direction (axis string X/Y/Z
    or a vector)."""
    M = ensure_materials()
    mat = mat or M["steel_bare"]
    slot_mat = slot_mat or M["steel_dark"]
    length = max(length, 0.0030)
    axis, sign = _axis_of(normal)
    n = Vector(normal).normalized()
    off = n * (length * 0.5 - 0.0012)
    c = Vector(center) + off
    parts = [cyl(coll, name + "_Head", r, length, c, mat, axis, 12, bevel=0.0005, bseg=2)]
    return parts


def bolt(coll, name, center, normal, r=0.009, head=0.006, mat=None, length=0.02):
    M = ensure_materials()
    mat = mat or M["steel_dark"]
    axis, _ = _axis_of(normal)
    n = Vector(normal).normalized()
    c = Vector(center) + n * (head * 0.5 - 0.0015)
    parts = [cyl(coll, name + "_Head", r, head, c, mat, axis, 6, bevel=0.0006, bseg=2),
             cyl(coll, name + "_Shank", r * 0.55, length,
                 Vector(center) + n * (0.0012 - length * 0.5), mat, axis, 8,
                 bevel=0.0003, bseg=1)]
    return parts


def _axis_of(normal):
    if isinstance(normal, str):
        return normal if normal in ("X", "Y", "Z") else 'Z', 1
    v = Vector(normal)
    i = max(range(3), key=lambda k: abs(v[k]))
    return "XYZ"[i], (1 if v[i] >= 0 else -1)


def flange_bolts(coll, prefix, axis, plane, half_w, half_h, normal,
                 mat=None, r=0.0075, inset=0.055):
    """Eight bolts around a rectangular flange.

    axis: 'X' means the flange plane is YZ at coordinate `plane`.
    """
    M = ensure_materials()
    mat = mat or M["steel_dark"]
    pts = [(-half_w + inset, -half_h + inset), (half_w - inset, -half_h + inset),
           (half_w - inset, half_h - inset), (-half_w + inset, half_h - inset),
           (0, -half_h + inset), (0, half_h - inset),
           (-half_w + inset, 0), (half_w - inset, 0)]
    parts = []
    for i, (u, v) in enumerate(pts):
        if axis == 'X':
            center = (plane, u, v)
        elif axis == 'Y':
            center = (u, plane, v)
        else:
            center = (u, v, plane)
        parts += bolt(coll, "%s_%02d" % (prefix, i), center, normal,
                      r=r, mat=mat)
    return parts
