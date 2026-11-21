"""Construye el arte de Vestuarios (L1_ART_VESTUARIOS) en el máster V06.

Uso desde Blender MCP (live):
    exec(compile(open("/home/riyo/Documentos/game/scripts/fm/fm_vestuarios_build.py").read(),
                 "fm_vestuarios_build.py", "exec"))

El script es idempotente: elimina y reconstruye la colección L1_ART_VESTUARIOS.
No guarda el .blend, no toca otras colecciones y no añade luces ni cámaras.
"""

import bpy
import bmesh
import math
import os
from collections import defaultdict
from mathutils import Vector, Matrix, Euler

PROJECT = "/home/riyo/Documentos/game"
TEX = os.path.join(PROJECT, "assets", "texturas")
COL_NAME = "L1_ART_VESTUARIOS"

# ---------------------------------------------------------------------------
# Materiales
# ---------------------------------------------------------------------------


def _img(path, colorspace):
    img = bpy.data.images.get(os.path.basename(path))
    if img is None:
        img = bpy.data.images.load(path, check_existing=True)
    img.colorspace_settings.name = colorspace
    return img


def _principled(mat):
    return next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def _pbr(name, base_path, rough_path=None, normal_path=None, metallic=0.0,
         rough_value=0.5, base_color=None):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (420, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (100, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = rough_value
    if base_color is not None:
        bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
    if base_path:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.location = (-420, 220)
        tex.image = _img(base_path, "sRGB")
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    if rough_path:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.location = (-420, -20)
        tex.image = _img(rough_path, "Non-Color")
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Roughness"])
    if normal_path:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.location = (-420, -260)
        tex.image = _img(normal_path, "Non-Color")
        nmap = nt.nodes.new("ShaderNodeNormalMap")
        nmap.location = (-140, -260)
        nt.links.new(tex.outputs["Color"], nmap.inputs["Color"])
        nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def _solid(name, color, rough=0.6, metallic=0.0, emission=None, emission_strength=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (300, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (0, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metallic
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


def ensure_materials():
    art = os.path.join(PROJECT, "assets", "art", "fm", "vestuarios")
    green = _pbr(
        "M_VEST_Locker_Green",
        os.path.join(art, "T_VEST_LOCKER_GREEN_1K_BC.jpg"),
        os.path.join(art, "T_VEST_LOCKER_GREEN_1K_ROUGH.png"),
        metallic=0.0, rough_value=0.55,
    )
    _pbr(
        "M_VEST_Tile",
        os.path.join(art, "T_VEST_TILE_1K_BC.jpg"),
        metallic=0.0, rough_value=0.55,
    )
    _solid("M_VEST_Galv", (0.57, 0.60, 0.62), rough=0.38, metallic=0.9)
    _solid("M_VEST_Mirror", (0.92, 0.95, 0.98), rough=0.06, metallic=1.0)
    _solid("M_VEST_Ceramic", (0.82, 0.82, 0.78), rough=0.22)
    _solid("M_VEST_Cloth_Dark", (0.055, 0.075, 0.070), rough=0.92)
    _solid("M_VEST_Cloth_Olive", (0.10, 0.115, 0.075), rough=0.90)
    _solid("M_VEST_Cloth_Orange", (0.55, 0.18, 0.035), rough=0.78)
    _solid("M_VEST_Towel", (0.42, 0.46, 0.40), rough=0.95)
    _solid("M_VEST_Paper", (0.72, 0.70, 0.60), rough=0.92)
    _solid("M_VEST_Cork", (0.26, 0.16, 0.075), rough=0.88)
    _solid("M_VEST_Emissive_Cool", (0.75, 0.86, 0.95), rough=0.3,
           emission=(0.75, 0.90, 1.0), emission_strength=6.0)
    _solid("M_VEST_Emissive_Green", (0.02, 0.35, 0.12), rough=0.35,
           emission=(0.05, 0.90, 0.30), emission_strength=3.0)
    _solid("M_VEST_HardHat", (0.72, 0.30, 0.03), rough=0.42)
    _solid("M_VEST_Black", (0.015, 0.017, 0.018), rough=0.65)
    _solid("M_VEST_Red", (0.38, 0.018, 0.012), rough=0.38)
    # Charco oscuro: conserva el alfa de la textura de charco existente.
    src = bpy.data.materials.get("M_REC03_DecalPuddle")
    if src is not None:
        mat = src.copy()
        mat.name = "M_VEST_Puddle"
        bsdf = _principled(mat)
        for link in list(mat.node_tree.links):
            if link.to_socket == bsdf.inputs["Base Color"]:
                mat.node_tree.links.remove(link)
        bsdf.inputs["Base Color"].default_value = (0.008, 0.014, 0.016, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.06
        bsdf.inputs["Metallic"].default_value = 0.0
        mat.surface_render_method = "DITHERED"
    print("VEST materials OK")


# ---------------------------------------------------------------------------
# Constructor de malla por material
# ---------------------------------------------------------------------------


class MeshBuilder:
    def __init__(self, name):
        self.name = name
        self.verts = []
        self.faces = []
        self.face_uvs = []
        self.face_mats = []
        self.mat_order = []
        self.mat_index = {}

    def _mat(self, mat):
        key = mat.name
        if key not in self.mat_index:
            self.mat_index[key] = len(self.mat_order)
            self.mat_order.append(mat)
        return self.mat_index[key]

    def _append(self, mat, verts, faces, uvs):
        base = len(self.verts)
        mi = self._mat(mat)
        self.verts.extend(verts)
        for f, uv in zip(faces, uvs):
            self.faces.append([base + i for i in f])
            self.face_uvs.append(uv)
            self.face_mats.append(mi)

    @staticmethod
    def _bevel_box(size, bevel, segments):
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts:
            v.co.x *= size[0]
            v.co.y *= size[1]
            v.co.z *= size[2]
        if bevel > 0.0:
            bmesh.ops.bevel(
                bm, geom=list(bm.edges), offset=bevel, segments=segments,
                affect="EDGES", profile=0.5, clamp_overlap=True,
            )
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.normal_update()
        verts = [v.co.copy() for v in bm.verts]
        faces = [[v.index for v in f.verts] for f in bm.faces]
        normals = [f.normal.copy() for f in bm.faces]
        bm.free()
        return verts, faces, normals

    def add_box(self, center, size, mat, bevel=0.0, segments=1, rot=(0, 0, 0),
                uv_scale=1.0):
        verts, faces, normals = self._bevel_box(size, bevel, segments)
        R = Euler(rot, "XYZ").to_matrix()
        c = Vector(center)
        wverts = [R @ v + c for v in verts]
        wnormals = [R @ n for n in normals]
        uvs = []
        for f, n in zip(faces, wnormals):
            ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
            uv = []
            for vi in f:
                p = wverts[vi]
                if az >= ax and az >= ay:
                    u, v = p.x, p.y
                elif ax >= ay:
                    u, v = p.y, p.z
                else:
                    u, v = p.x, p.z
                uv.append((u * uv_scale, v * uv_scale))
            uvs.append(uv)
        self._append(mat, wverts, faces, uvs)

    def add_cyl(self, center, radius, depth, mat, axis="Z", segments=16,
                rot=(0, 0, 0), uv_scale=1.0, bevel=0.0):
        bm = bmesh.new()
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=segments,
            radius1=radius, radius2=radius, depth=depth,
        )
        if bevel > 0.0:
            bmesh.ops.bevel(
                bm, geom=list(bm.edges), offset=bevel, segments=1,
                affect="EDGES", profile=0.5, clamp_overlap=True,
            )
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.normal_update()
        verts = [v.co.copy() for v in bm.verts]
        faces = [[v.index for v in f.verts] for f in bm.faces]
        normals = [f.normal.copy() for f in bm.faces]
        bm.free()
        base = Euler(rot, "XYZ").to_matrix()
        if axis == "X":
            base = base @ Matrix.Rotation(math.radians(90), 3, "Y")
        elif axis == "Y":
            base = base @ Matrix.Rotation(math.radians(90), 3, "X")
        c = Vector(center)
        wverts = [base @ v + c for v in verts]
        wnormals = [base @ n for n in normals]
        uvs = []
        for f, n in zip(faces, wnormals):
            ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
            uv = []
            for vi in f:
                p = wverts[vi]
                if az >= ax and az >= ay:
                    u, v = p.x, p.y
                elif ax >= ay:
                    u, v = p.y, p.z
                else:
                    u, v = p.x, p.z
                uv.append((u * uv_scale, v * uv_scale))
            uvs.append(uv)
        self._append(mat, wverts, faces, uvs)

    def add_plane(self, center, sx, sy, mat, rot=(0, 0, 0), uv_rect=(0, 0, 1, 1)):
        verts = [Vector((-sx / 2, -sy / 2, 0)), Vector((sx / 2, -sy / 2, 0)),
                 Vector((sx / 2, sy / 2, 0)), Vector((-sx / 2, sy / 2, 0))]
        R = Euler(rot, "XYZ").to_matrix()
        c = Vector(center)
        verts = [R @ v + c for v in verts]
        u0, v0, u1, v1 = uv_rect
        uvs = [[(u0, v0), (u1, v0), (u1, v1), (u0, v1)]]
        self._append(mat, verts, [[0, 1, 2, 3]], uvs)

    def build(self, collection):
        if not self.verts:
            return None
        me = bpy.data.meshes.new(self.name)
        me.from_pydata([tuple(v) for v in self.verts], [], self.faces)
        me.validate(verbose=False)
        me.update()
        # Suelda duplicados de las caras de bisel antes de asignar UVs. Evita
        # caras coplanares sin vértices compartidos que produzcan z-fighting.
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-5)
        bm.to_mesh(me)
        bm.free()
        me.update()
        uv_layer = me.uv_layers.new(name="UVMap")
        for poly, uvs, mi in zip(me.polygons, self.face_uvs, self.face_mats):
            poly.material_index = mi
            for li, uv in zip(poly.loop_indices, uvs):
                uv_layer.data[li].uv = uv
            poly.use_smooth = True
        for mat in self.mat_order:
            me.materials.append(mat)
        ob = bpy.data.objects.new(self.name, me)
        collection.objects.link(ob)
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)
        try:
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(34))
        except Exception:
            pass
        ob.select_set(False)
        return ob


# ---------------------------------------------------------------------------
# Piezas
# ---------------------------------------------------------------------------


def _rot2(x, y, angle):
    c, s = math.cos(angle), math.sin(angle)
    return x * c - y * s, x * s + y * c


def build_locker_bank(name, cx, cy, rot_z, width=2.4, depth=0.55,
                      height=1.95, doors=6, open_doors=(), number_start=1,
                      interior_items=()):
    mb = MeshBuilder(name)
    green = bpy.data.materials["M_VEST_Locker_Green"]
    steel = bpy.data.materials["M_FM_Steel_Dark"]
    dark = bpy.data.materials["M_VEST_Black"]
    label_white = bpy.data.materials["M_FM_Label_White"]
    nums = [bpy.data.materials["M_FM_Label_Num_01"],
            bpy.data.materials["M_FM_Label_Num_02"],
            bpy.data.materials["M_FM_Label_Num_03"]]
    cloth = bpy.data.materials["M_VEST_Cloth_Olive"]
    rubber = bpy.data.materials["M_FM_Rubber"]

    Rz = Matrix.Rotation(rot_z, 4, "Z")
    T = Matrix.Translation((cx, cy, 0.0))
    M = T @ Rz

    def P(x, y, z):
        v = M @ Vector((x, y, z))
        return tuple(v)

    def B(local_center, size, mat, bevel=0.0, seg=1, local_rot=0.0, uv_scale=1.0):
        x, y, z = local_center
        mb.add_box(P(x, y, z), size, mat, bevel=bevel, segments=seg,
                   rot=(0, 0, rot_z + local_rot), uv_scale=uv_scale)

    door_w = width / doors
    front = depth / 2.0
    # Carcasa con juntas a tope: las caras se tocan con normales opuestas,
    # no se solapan coplanariamente.
    bottom_z0, bottom_z1 = 0.1025, 0.1275
    top_z0, top_z1 = height - 0.05, height
    # Los paneles verticales se embuten en las losas superior e inferior con
    # alturas ligeramente distintas: sus caras extremas quedan ocultas y no
    # comparten plano, evitando z-fighting interno.
    side_z0, side_z1 = bottom_z1 - 0.006, top_z0 + 0.006
    back_z0, back_z1 = bottom_z1 - 0.004, top_z0 + 0.008
    div_z0, div_z1 = bottom_z1 - 0.008, top_z0 + 0.004
    B((0, -0.02, 0.05), (width - 0.03, depth - 0.09, 0.10), dark)
    B((0, 0.01, (bottom_z0 + bottom_z1) / 2.0),
      (width - 0.04, depth - 0.02, bottom_z1 - bottom_z0), green)
    B((0, 0, height - 0.025), (width, depth, top_z1 - top_z0),
      green, bevel=0.004)
    # El fondo sobresale 3 mm por detrás de la losa superior y los laterales
    # quedan retranqueados: ninguna cara grande comparte plano con otra.
    B((0, -front + 0.007, (back_z0 + back_z1) / 2.0),
      (width - 0.04, 0.02, back_z1 - back_z0), green)
    B((-width / 2 + 0.01, 0.005, (side_z0 + side_z1) / 2.0),
      (0.02, depth - 0.04, side_z1 - side_z0), green)
    B((width / 2 - 0.01, 0.005, (side_z0 + side_z1) / 2.0),
      (0.02, depth - 0.04, side_z1 - side_z0), green)
    for i in range(1, doors):
        x = -width / 2 + i * door_w
        B((x, 0.005, (div_z0 + div_z1) / 2.0),
          (0.014, depth - 0.06, div_z1 - div_z0), green)
    # Estantes y ganchos internos, apoyados en el fondo.
    for i in range(doors):
        x = -width / 2 + (i + 0.5) * door_w
        B((x, -0.005, 1.50), (door_w - 0.05, depth - 0.05, 0.02), steel)
        B((x, -front + 0.05, 1.38), (0.012, 0.06, 0.09), steel)
        B((x, -front + 0.095, 1.325), (0.012, 0.03, 0.02), steel)

    # Puertas
    for i in range(doors):
        x0 = -width / 2 + i * door_w
        xc = x0 + door_w / 2.0
        hinge_x = x0 + 0.015
        hinge_y = front + 0.005
        # Ángulo positivo: la puerta abre hacia la sala, no hacia la carcasa.
        angle = math.radians(68.0) if i in open_doors else 0.0
        if i in open_doors and (i % 2 == 0):
            angle = math.radians(82.0)

        def D(lx, ly, lz):
            # Coordenadas locales de puerta cerrada -> giro sobre bisagra.
            dx, dy = lx - hinge_x, ly - hinge_y
            rx, ry = _rot2(dx, dy, angle)
            return P(hinge_x + rx, hinge_y + ry, lz)

        door_center = (xc, front + 0.012, 0.115 + (height - 0.17) / 2.0)
        dc = D(*door_center)
        mb.add_box(dc, (door_w - 0.018, 0.022, height - 0.17), green,
                   bevel=0.0025, segments=1, rot=(0, 0, rot_z + angle),
                   uv_scale=0.9)
        # Refuerzo interior de la puerta y placa de número
        lp = D(xc, front + 0.028, height - 0.24)
        mb.add_box(lp, (0.075, 0.004, 0.04), label_white,
                   rot=(0, 0, rot_z + angle))
        np = D(xc, front + 0.036, height - 0.24)
        north_facing = abs(rot_z - math.pi) < 0.1
        num_uv = (0, 1, 1, 0) if north_facing else (1, 1, 0, 0)
        mb.add_plane(np, 0.055, 0.055, nums[(number_start + i) % 3],
                     rot=(math.radians(-90), 0, rot_z + angle),
                     uv_rect=num_uv)
        # Rejillas de ventilación (separadas 3 mm de la chapa de la puerta)
        for j in range(3):
            vp = D(xc, front + 0.031, height - 0.34 - j * 0.032)
            mb.add_box(vp, (door_w * 0.48, 0.006, 0.010), dark,
                       rot=(0, 0, rot_z + angle))
        # Tirador y cerradura
        hp = D(x0 + door_w - 0.055, front + 0.034, 1.06)
        mb.add_box(hp, (0.030, 0.035, 0.130), steel,
                   bevel=0.002, segments=1, rot=(0, 0, rot_z + angle))
        kp = D(x0 + door_w - 0.055, front + 0.027, 1.22)
        mb.add_box(kp, (0.032, 0.020, 0.040), steel,
                   rot=(0, 0, rot_z + angle))
        if angle != 0.0:
            for hz in (0.42, 1.00, 1.58):
                hp2 = D(x0 + 0.018, front + 0.018, hz)
                mb.add_box(hp2, (0.012, 0.020, 0.055), steel,
                           rot=(0, 0, rot_z + angle))
            # Ropa doblada y botas en taquillas abiertas seleccionadas
            if i in interior_items:
                # La ropa y las botas van dentro del compartimento, no en la
                # puerta: no deben girar con la bisagra.
                cp = P(xc, -0.03, 1.54)
                mb.add_box(cp, (door_w - 0.10, depth - 0.16, 0.06), cloth,
                           bevel=0.006, segments=1, rot=(0, 0, rot_z))
                bp1 = P(xc - 0.07, -0.05, 0.19)
                bp2 = P(xc + 0.07, -0.05, 0.19)
                mb.add_box(bp1, (0.10, 0.24, 0.13), rubber,
                           bevel=0.006, segments=1, rot=(0, 0, rot_z))
                mb.add_box(bp2, (0.10, 0.24, 0.13), rubber,
                           bevel=0.006, segments=1, rot=(0, 0, rot_z))

    return mb.build(_collection())


def build_bench(name, cx, cy, rot_z, length=2.4, width=0.42,
                height=0.45, lower_shelf=False):
    mb = MeshBuilder(name)
    wood = bpy.data.materials["M_FM_Workbench_Wood"]
    steel = bpy.data.materials["M_FM_Steel_Dark"]
    rubber = bpy.data.materials["M_FM_Rubber"]
    Rz = Matrix.Rotation(rot_z, 4, "Z")
    T = Matrix.Translation((cx, cy, 0.0))
    M = T @ Rz

    def P(x, y, z):
        return tuple(M @ Vector((x, y, z)))

    def B(c, s, m, **kw):
        mb.add_box(P(*c), s, m, rot=(0, 0, rot_z), **kw)

    B((0, 0, height - 0.022), (length, width, 0.045), wood, bevel=0.004)
    # Patas apoyadas sobre las regletas de goma; sin caras coplanarias.
    leg_z0, leg_z1 = 0.024, height - 0.005
    for sx in (-1, 1):
        x = sx * (length / 2 - 0.12)
        for sy in (-1, 1):
            B((x, sy * (width / 2 - 0.06), (leg_z0 + leg_z1) / 2),
              (0.045, 0.045, leg_z1 - leg_z0), steel, bevel=0.002)
        B((x, 0, 0.10), (0.038, width - 0.10, 0.04), steel)
    B((0, 0, 0.10), (length - 0.28, 0.04, 0.035), steel)
    for sy in (-1, 1):
        B((0, sy * (width / 2 - 0.06), 0.012), (length - 0.20, 0.05, 0.024), rubber)
    if lower_shelf:
        B((0, 0, 0.18), (length - 0.12, width - 0.04, 0.025), wood)
    return mb.build(_collection())


def build_ceiling_and_lights():
    steel = bpy.data.materials["M_FM_Steel_Dark"]
    galv = bpy.data.materials["M_VEST_Galv"]
    dark = bpy.data.materials["M_VEST_Black"]
    cool = bpy.data.materials["M_VEST_Emissive_Cool"]
    red = bpy.data.materials["M_R21B_Emissive_Red"]

    # Tuberías y cableado
    mb = MeshBuilder("VEST_Ceiling_Pipes_CABLE")
    for y, r in ((43.0, 0.055), (43.45, 0.035), (44.0, 0.070)):
        mb.add_cyl((45, y, 3.94), r, 30.0, steel, axis="X", segments=12,
                   uv_scale=0.5)
        for x in range(31, 61, 5):
            mb.add_cyl((x, y, 3.94), r + 0.025, 0.055, steel, axis="X",
                       segments=12, uv_scale=0.5)
    for x, r in ((31.6, 0.05), (58.4, 0.06)):
        mb.add_cyl((x, 52.0, 3.96), r, 24.0, steel, axis="Y", segments=12,
                   uv_scale=0.5)
    # Bandejas portacables
    for y in (47.1, 57.2):
        mb.add_box((45, y, 3.97), (30.0, 0.42, 0.02), galv, uv_scale=0.8)
        for sx in (-1, 1):
            mb.add_box((45, y + sx * 0.21, 4.02), (30.0, 0.02, 0.09), galv)
        for x in range(31, 61, 2):
            mb.add_box((x, y, 3.99), (0.035, 0.40, 0.025), galv)
        for x in range(32, 60, 4):
            mb.add_box((x, y, 4.10), (0.02, 0.02, 0.22), steel)
        for off in (-0.10, 0.0, 0.10):
            mb.add_cyl((45, y + off, 3.95), 0.018, 29.0, dark, axis="X",
                       segments=8)
    # Conducto de ventilación (bajo las vigas)
    mb.add_box((33.4, 52.0, 3.80), (0.55, 23.0, 0.38), galv, bevel=0.005,
               uv_scale=0.6)
    for y in (42, 46, 50, 54, 62):
        mb.add_box((33.4, y, 4.04), (0.60, 0.035, 0.06), steel)
        mb.add_box((33.4, y, 4.04), (0.03, 0.03, 0.30), steel)
    for y in (46.0, 54.0, 62.0):
        mb.add_box((33.4, y, 3.605), (0.42, 0.30, 0.015), dark)
        for j in range(4):
            mb.add_box((33.4, y - 0.11 + j * 0.073, 3.598),
                       (0.34, 0.018, 0.012), galv)
    # Línea de rociadores
    mb.add_cyl((45, 41.4, 4.00), 0.022, 30.0, red, axis="X", segments=8)
    for x in range(32, 60, 4):
        mb.add_cyl((x, 41.4, 3.94), 0.012, 0.16, red, axis="Z", segments=8)
    pipes = mb.build(_collection())
    # 2 cm por debajo de las vigas para evitar contactos coplanarios.
    pipes.location.z -= 0.02

    # Luminarias
    positions = [(36, 44.8, 0), (48, 44.8, 0), (36, 55.2, 0),
                 (48, 55.2, 0), (55, 45.5, 0), (55.5, 59.5, 0),
                 (40, 50.2, 8)]
    for idx, (x, y, tilt) in enumerate(positions):
        mb = MeshBuilder("VEST_LightFixture_%02d_LIGHT" % idx)
        rot = math.radians(tilt)
        if idx == 3:
            # Luminaria rota: una pantalla caída.
            mb.add_box((x, y, 3.94), (1.25, 0.18, 0.07), steel,
                       rot=(0, 0, rot))
            mb.add_box((x - 0.2, y, 3.899), (0.55, 0.035, 0.035), cool,
                       rot=(0, 0, rot))
        else:
            mb.add_box((x, y, 3.95), (1.25, 0.18, 0.07), steel, bevel=0.003,
                       rot=(0, 0, rot))
            for sy in (-0.045, 0.045):
                mb.add_box((x, y + sy, 3.899), (1.13, 0.032, 0.032), cool,
                           rot=(0, 0, rot))
            for sx in (-1, 1):
                mb.add_box((x + sx * 0.635, y, 3.95), (0.02, 0.19, 0.08),
                           steel, rot=(0, 0, rot))
        for sx in (-1, 1):
            mb.add_cyl((x + sx * 0.42, y, 4.18), 0.008, 0.44, steel,
                       axis="Z", segments=8)
        mb.build(_collection())

    # Balizas de emergencia
    for idx, (x, y, z, rz) in enumerate((
        (43.0, 40.20, 3.05, 0.0),
        (30.20, 50.0, 3.05, math.radians(90)),
        (54.0, 63.80, 3.05, math.radians(180)),
    )):
        mb = MeshBuilder("VEST_EmergencyBeacon_%02d_LIGHT" % idx)
        mb.add_box((x, y, z), (0.20, 0.12, 0.16), steel,
                   rot=(0, 0, rz))
        mb.add_cyl((x, y + 0.065, z), 0.055, 0.10, red, axis="Y",
                   segments=12, rot=(0, 0, rz))
        mb.build(_collection())


def build_showers():
    tile = bpy.data.materials["M_VEST_Tile"]
    steel = bpy.data.materials["M_FM_Steel_Dark"]
    dark = bpy.data.materials["M_VEST_Black"]
    cloth = bpy.data.materials["M_VEST_Towel"]
    galv = bpy.data.materials["M_VEST_Galv"]

    # Plataforma y paredes alicatadas
    mb = MeshBuilder("VEST_Shower_Platform_Tile")
    mb.add_box((55.45, 60.0, 0.0125), (8.5, 7.6, 0.025), tile, uv_scale=0.55)
    mb.build(_collection())

    mb = MeshBuilder("VEST_Shower_TileWalls")
    # Las paredes alicatadas arrancan sobre la plataforma (z=0,025), sin
    # solaparse con su losa.
    mb.add_box((55.45, 63.82, 1.3125), (8.9, 0.05, 2.575), tile, uv_scale=0.55)
    mb.add_box((59.82, 60.0, 1.3125), (0.05, 7.9, 2.575), tile, uv_scale=0.55)
    mb.add_box((51.22, 61.05, 1.115), (0.09, 5.7, 2.170), tile, uv_scale=0.55)
    mb.add_box((55.45, 63.80, 2.64), (8.9, 0.06, 0.08), steel)
    mb.add_box((59.80, 60.0, 2.64), (0.08, 7.9, 0.08), steel)
    mb.add_box((51.22, 61.05, 2.24), (0.12, 5.7, 0.08), steel)
    for x in (53.4, 55.6, 57.8):
        mb.add_box((x, 62.65, 1.115), (0.08, 2.5, 2.170), tile, uv_scale=0.55)
        mb.add_box((x, 61.42, 2.22), (0.10, 0.06, 0.06), steel)
    mb.build(_collection())

    # Duchas y grifería
    mb = MeshBuilder("VEST_Shower_Hardware")
    xs = (52.3, 54.5, 56.7, 58.9)
    for i, x in enumerate(xs):
        mb.add_cyl((x, 63.76, 2.35), 0.018, 0.72, steel, axis="Z", segments=10)
        mb.add_cyl((x, 63.53, 2.68), 0.016, 0.48, steel, axis="Y", segments=10)
        mb.add_cyl((x, 63.28, 2.61), 0.110, 0.035, steel, axis="Z",
                   segments=16, bevel=0.003)
        mb.add_cyl((x, 63.74, 1.30), 0.052, 0.035, steel, axis="Y", segments=14)
        mb.add_box((x, 63.71, 1.30), (0.16, 0.035, 0.025), steel)
        mb.add_box((x, 63.705, 1.30), (0.025, 0.030, 0.16), steel)
        # Rejilla de desagüe
        mb.add_box((x, 62.55, 0.032), (0.34, 0.34, 0.012), dark)
        for j in range(5):
            mb.add_box((x, 62.42 + j * 0.065, 0.040), (0.30, 0.018, 0.012), galv)
    # Barra de cortinas y soportes
    mb.add_cyl((55.45, 61.36, 2.20), 0.016, 8.5, steel, axis="X", segments=10)
    for x in (51.35, 55.45, 59.55):
        mb.add_box((x, 61.36, 2.24), (0.05, 0.06, 0.08), steel)
    for j in range(18):
        mb.add_cyl((51.5 + j * 0.46, 61.36, 2.17), 0.022, 0.02, steel,
                   axis="Y", segments=8)
    mb.build(_collection())

    # Cortinas: una ausente (índice 2), una rasgada y dos recogidas para
    # dejar ver el alicatado y la grifería. Así la ducha se lee como espacio.
    curtain_cfg = [
        (0.62, -0.62, 1.72, 0.40, "M_VEST_Cloth_Olive"),
        (1.18, -0.34, 1.58, 0.56, "M_VEST_Towel"),
        (0.0, 0.0, 0.0, 0.0, None),
        (0.82, -0.45, 1.02, 1.10, "M_VEST_Cloth_Olive"),
    ]
    for i, x in enumerate(xs):
        width, xoff, height, z0, mat_name = curtain_cfg[i]
        if width <= 0.0:
            continue
        mb = MeshBuilder("VEST_Shower_Curtain_%02d_CLOTH" % i)
        mat = bpy.data.materials[mat_name]
        seg = max(6, int(width / 0.14))
        for j in range(seg):
            x0 = x + xoff + (j + 0.5) * width / seg
            zc = z0 + height / 2
            fold = 0.035 if j % 2 == 0 else -0.02
            mb.add_box((x0, 61.36 + fold, zc),
                       (width / seg - 0.001, 0.012, height),
                       mat, uv_scale=1.4)
        mb.build(_collection())

    # Banco y banqueta dentro del vestidor de duchas
    for name, x in (("VEST_Shower_Bench_A", 53.0),
                    ("VEST_Shower_Bench_B", 57.6)):
        bench = build_bench(name, x, 60.55, 0.0, 2.1, 0.38, 0.43,
                            lower_shelf=True)
        bench.location.z = 0.025


def build_vanity():
    tile = bpy.data.materials["M_VEST_Tile"]
    ceramic = bpy.data.materials["M_VEST_Ceramic"]
    steel = bpy.data.materials["M_FM_Steel_Dark"]
    mirror = bpy.data.materials["M_VEST_Mirror"]
    dark = bpy.data.materials["M_VEST_Black"]
    green = bpy.data.materials["M_VEST_Locker_Green"]

    mb = MeshBuilder("VEST_Vanity_Counter")
    # Armario y encimera (retranqueados 5 cm de la cara interior y=63,85)
    mb.add_box((48.45, 63.55, 0.43), (4.0, 0.50, 0.82), green, bevel=0.004)
    mb.add_box((48.45, 63.52, 0.87), (4.10, 0.58, 0.06), ceramic, bevel=0.004)
    mb.add_box((48.45, 63.52, 0.03), (4.05, 0.52, 0.06), dark)
    # Lavabos (inset oscuro + aro cerámico)
    for x in (47.15, 48.45, 49.75):
        mb.add_box((x, 63.50, 0.905), (0.52, 0.36, 0.012), dark)
        mb.add_box((x, 63.50, 0.912), (0.46, 0.30, 0.012), ceramic)
        mb.add_box((x, 63.38, 0.95), (0.04, 0.16, 0.03), steel)
        mb.add_cyl((x, 63.46, 0.99), 0.012, 0.16, steel, axis="Z", segments=8)
        mb.add_cyl((x, 63.40, 1.07), 0.010, 0.16, steel, axis="Y", segments=8)
    # Espejos: bastidor visto desde el sur, espejo retrasado y marco fino.
    for x in (47.15, 48.45, 49.75):
        mb.add_box((x, 63.780, 1.78), (0.92, 0.025, 1.05), steel)
        mb.add_plane((x, 63.755, 1.78), 0.84, 0.97, mirror,
                     rot=(math.radians(90), 0, 0))
        mb.add_box((x, 63.730, 2.315), (0.94, 0.030, 0.030), steel)
        mb.add_box((x, 63.730, 1.245), (0.94, 0.030, 0.030), steel)
        for sx in (-1, 1):
            mb.add_box((x + sx * 0.455, 63.730, 1.78),
                       (0.030, 0.030, 1.10), steel)
        mb.add_box((x, 63.735, 1.20), (0.90, 0.05, 0.035), steel)
    # Alicatado sobre la encimera
    mb.add_box((48.45, 63.82, 1.22), (4.10, 0.035, 0.55), tile, uv_scale=0.8)
    # Dispensadores y secamanos
    for x in (46.55, 50.35):
        mb.add_box((x, 63.80, 1.35), (0.18, 0.10, 0.30), steel)
        mb.add_box((x, 63.74, 1.20), (0.06, 0.04, 0.08), dark)
    mb.build(_collection())


def build_walls_and_signs():
    steel = bpy.data.materials["M_FM_Steel_Dark"]
    dark = bpy.data.materials["M_VEST_Black"]
    cork = bpy.data.materials["M_VEST_Cork"]
    paper = bpy.data.materials["M_VEST_Paper"]
    white = bpy.data.materials["M_FM_Label_White"]
    green = bpy.data.materials["M_VEST_Emissive_Green"]
    red = bpy.data.materials["M_VEST_Red"]

    # Tablón de anuncios sobre las taquillas del muro sur
    mb = MeshBuilder("VEST_NoticeBoard_SIGN")
    mb.add_box((50.0, 40.19, 2.55), (3.6, 0.04, 0.78), cork, bevel=0.004)
    mb.add_box((50.0, 40.215, 2.94), (3.70, 0.05, 0.05), steel)
    mb.add_box((50.0, 40.215, 2.16), (3.70, 0.05, 0.05), steel)
    for x in (48.18, 51.82):
        mb.add_box((x, 40.215, 2.55), (0.05, 0.05, 0.82), steel)
    # Papeles y carteles
    for i, (x, z, w, h, ang) in enumerate((
        (48.85, 2.62, 0.34, 0.44, 0.03), (49.35, 2.55, 0.28, 0.36, -0.05),
        (49.90, 2.66, 0.30, 0.40, 0.02), (50.45, 2.48, 0.26, 0.34, 0.06),
        (51.25, 2.58, 0.40, 0.52, -0.02), (50.95, 2.42, 0.22, 0.28, 0.10),
    )):
        mb.add_plane((x, 40.225, z), w, h, paper,
                     rot=(math.radians(-90), ang, 0))
    mb.add_box((48.35, 40.24, 2.35), (0.30, 0.015, 0.38), red)
    mb.build(_collection())

    # Rótulo TAQUILLAS sobre la entrada principal
    mb = MeshBuilder("VEST_EntrySign_SIGN")
    mb.add_box((43.0, 40.19, 3.36), (2.55, 0.06, 0.68), dark)
    mb.add_plane((43.0, 40.23, 3.36), 2.40, 0.60,
                 bpy.data.materials["M_FM_Label_Taquillas"],
                 rot=(math.radians(-90), 0, 0), uv_rect=(1, 1, 0, 0))
    mb.add_box((43.0, 40.19, 3.74), (2.62, 0.05, 0.04), steel)
    mb.add_box((43.0, 40.19, 2.98), (2.62, 0.05, 0.04), steel)
    mb.build(_collection())

    # Rótulo de servicio sobre la puerta oeste
    mb = MeshBuilder("VEST_WestSign_SIGN")
    mb.add_box((30.19, 50.0, 3.24), (0.06, 1.95, 0.52), dark)
    mb.add_plane((30.23, 50.0, 3.24), 1.80, 0.44,
                 bpy.data.materials["M_FM_Sign_Servicio"],
                 rot=(math.radians(90), 0, math.radians(90)))
    mb.build(_collection())

    # Extintor y cartel
    mb = MeshBuilder("VEST_Extinguisher")
    mb.add_cyl((46.55, 40.32, 0.62), 0.075, 0.58, red, axis="Z", segments=14)
    mb.add_cyl((46.55, 40.32, 0.95), 0.032, 0.10, steel, axis="Z", segments=10)
    mb.add_box((46.55, 40.32, 1.02), (0.16, 0.05, 0.035), dark)
    mb.add_box((46.55, 40.42, 0.80), (0.13, 0.02, 0.10), white)
    mb.add_box((46.55, 40.24, 0.55), (0.24, 0.10, 0.06), steel)
    mb.add_plane((46.55, 40.215, 1.45), 0.50, 0.125,
                 bpy.data.materials["M_FM_Label_Extintor"],
                 rot=(math.radians(-90), 0, 0), uv_rect=(1, 1, 0, 0))
    mb.build(_collection())

    # Botiquín
    mb = MeshBuilder("VEST_FirstAid")
    mb.add_box((55.0, 40.24, 1.55), (0.46, 0.13, 0.52), white, bevel=0.004)
    mb.add_box((55.0, 40.31, 1.55), (0.028, 0.012, 0.26), green)
    mb.add_box((55.0, 40.31, 1.55), (0.16, 0.012, 0.045), green)
    mb.build(_collection())

    # Reloj de pared
    mb = MeshBuilder("VEST_Clock")
    mb.add_cyl((45.85, 40.24, 3.02), 0.23, 0.045, dark, axis="Y", segments=24)
    mb.add_cyl((45.85, 40.215, 3.02), 0.205, 0.02, white, axis="Y", segments=24)
    mb.add_box((45.85, 40.20, 3.07), (0.012, 0.01, 0.14), dark)
    mb.add_box((45.91, 40.20, 3.02), (0.11, 0.01, 0.012), dark)
    mb.build(_collection())

    # Señal de salida sobre puerta sur
    _exit_sign(43.0, 40.20, 2.70, 0.0)
    _exit_sign(30.20, 50.0, 2.76, math.radians(90))


def _exit_sign(x, y, z, rz):
    """Cartel SALIDA emisivo con texto convertido a malla."""
    mb = MeshBuilder("VEST_ExitSign_%d_SIGN" % int(z * 100 + x))
    mb.add_box((x, y, z), (0.86, 0.05, 0.28), bpy.data.materials["M_VEST_Black"],
               rot=(0, 0, rz))
    mb.add_box((x, y + 0.03, z), (0.78, 0.02, 0.22),
               bpy.data.materials["M_VEST_Emissive_Green"], rot=(0, 0, rz))
    mb.build(_collection())
    # Texto blanco
    cu = bpy.data.curves.new("TMP_EXIT_TEXT", type="FONT")
    cu.body = "SALIDA"
    cu.size = 0.115
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.extrude = 0.002
    ob = bpy.data.objects.new("TMP_EXIT_TEXT", cu)
    bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    eval_ob = ob.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(eval_ob)
    mat = bpy.data.materials["M_FM_Label_White"]
    me.materials.append(mat)
    ob2 = bpy.data.objects.new("VEST_ExitSignText_SIGN", me)
    _collection().objects.link(ob2)
    if abs(rz) < 0.1:
        loc = Vector((x, y + 0.045, z))
        normal = Vector((0, 1, 0))
    else:
        loc = Vector((x + 0.045, y, z))
        normal = Vector((1, 0, 0))
    up = Vector((0, 0, 1))
    right = up.cross(normal).normalized()
    basis = Matrix((right, up, normal)).transposed()
    ob2.matrix_world = Matrix.Translation(loc) @ basis.to_4x4()
    bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.curves.remove(cu)


def build_props():
    wood = bpy.data.materials["M_FM_Workbench_Wood"]
    steel = bpy.data.materials["M_FM_Steel_Dark"]
    dark = bpy.data.materials["M_VEST_Black"]
    rubber = bpy.data.materials["M_FM_Rubber"]
    cloth = bpy.data.materials["M_VEST_Cloth_Dark"]
    olive = bpy.data.materials["M_VEST_Cloth_Olive"]
    towel = bpy.data.materials["M_VEST_Towel"]
    paper = bpy.data.materials["M_VEST_Paper"]
    orange = bpy.data.materials["M_VEST_HardHat"]
    red = bpy.data.materials["M_VEST_Red"]

    # Ropa colgada y bolsas: objetos decorativos (CLOTH)
    for i, (x, y, z, rz, mat, sx, sy) in enumerate((
        (31.1, 53.0, 1.55, 0.2, cloth, 0.52, 0.16),
        (31.1, 57.2, 1.50, -0.3, olive, 0.46, 0.14),
        (34.0, 63.2, 1.45, 3.0, cloth, 0.50, 0.15),
        (46.3, 63.2, 1.40, 3.1, olive, 0.44, 0.14),
    )):
        mb = MeshBuilder("VEST_Cloth_Hanging_%02d_CLOTH" % i)
        # Cuerpo, hombros y mangas se tocan sin solaparse.
        mb.add_box((x, y, z), (sx, sy, 0.72), mat, bevel=0.02, segments=1,
                   rot=(0, 0, rz), uv_scale=1.5)
        mb.add_box((x, y, z + 0.42), (sx * 1.02, sy * 1.05, 0.12), mat,
                   bevel=0.02, rot=(0, 0, rz), uv_scale=1.5)
        for s in (-1, 1):
            mb.add_box((x + s * (sx / 2 + 0.05), y, z + 0.18),
                       (0.10, sy * 1.05, 0.42), mat, bevel=0.015,
                       rot=(0, 0, rz), uv_scale=1.5)
        mb.add_cyl((x, y, z + 0.53), 0.012, 0.10, steel, axis="Z", segments=8)
        mb.build(_collection())

    # Bultos y toallas en bancos
    mb = MeshBuilder("VEST_BenchProps_CLOTH")
    for x, y, z, rz in ((33.8, 42.25, 0.49, 0.1), (49.7, 42.25, 0.49, -0.2),
                        (57.35, 43.85, 0.49, 0.4)):
        mb.add_box((x, y, z), (0.50, 0.28, 0.25), cloth, bevel=0.03,
                   segments=2, rot=(0, 0, rz), uv_scale=1.2)
        mb.add_box((x, y, z + 0.16), (0.52, 0.10, 0.035), dark,
                   rot=(0, 0, rz))
    for x, y, z, rz in ((35.7, 61.45, 0.49, 0.1), (43.4, 61.45, 0.49, -0.1),
                        (32.4, 55.1, 0.49, 1.6)):
        mb.add_box((x, y, z), (0.44, 0.34, 0.10), towel, bevel=0.02,
                   rot=(0, 0, rz), uv_scale=1.5)
    # Botas debajo de bancos
    for x, y in ((33.8, 42.1), (49.7, 42.1), (57.35, 43.75)):
        for s in (-1, 1):
            mb.add_box((x + s * 0.09, y, 0.075), (0.10, 0.26, 0.15), rubber,
                       bevel=0.012, segments=1)
    mb.build(_collection())

    # Casco sobre banco de entrada
    mb = MeshBuilder("VEST_HardHat")
    mb.add_cyl((40.9, 42.9, 0.47), 0.17, 0.20, orange, axis="Z", segments=18)
    mb.add_cyl((40.9, 42.9, 0.57), 0.11, 0.10, orange, axis="Z", segments=18)
    mb.add_cyl((40.9, 42.9, 0.465), 0.21, 0.025, orange, axis="Z", segments=18)
    mb.build(_collection())

    # Papeles en el suelo
    mb = MeshBuilder("VEST_Papers_PAPER")
    for i, (x, y, rz) in enumerate(((47.3, 40.8, 0.3), (47.0, 41.2, -0.6),
                                    (46.5, 40.6, 1.2), (50.9, 40.5, 0.1),
                                    (51.5, 40.9, -0.4))):
        mb.add_plane((x, y, 0.015), 0.21, 0.29, paper,
                     rot=(0, 0, rz))
    mb.build(_collection())

    # Cubo y fregona junto a la puerta de servicio
    mb = MeshBuilder("VEST_MopBucket")
    mb.add_cyl((57.2, 41.2, 0.18), 0.20, 0.34, bpy.data.materials["M_VEST_Paper"],
               axis="Z", segments=16)
    mb.add_cyl((57.2, 41.2, 0.35), 0.17, 0.02, dark, axis="Z", segments=16)
    mb.add_cyl((57.45, 41.2, 0.55), 0.018, 1.10, steel, axis="Z", segments=8)
    mb.add_box((57.5, 41.2, 0.95), (0.20, 0.12, 0.10), towel, bevel=0.015)
    mb.build(_collection())

    # Puerta de taquilla descolgada apoyada en el muro este
    mb = MeshBuilder("VEST_BrokenLockerDoor")
    door_rot = (0, math.radians(12), math.radians(8))
    mb.add_box((59.45, 54.6, 0.90), (0.42, 0.025, 1.74),
               bpy.data.materials["M_VEST_Locker_Green"],
               bevel=0.003, rot=door_rot)
    mb.add_box((59.45, 54.55, 1.55), (0.06, 0.012, 0.035),
               bpy.data.materials["M_FM_Label_White"], rot=door_rot)
    mb.build(_collection())

    # Manchas de agua / charcos (decal)
    mb = MeshBuilder("VEST_Puddles_DECAL")
    puddle = bpy.data.materials["M_VEST_Puddle"]
    for x, y, sx, sy, rz in ((54.0, 61.2, 1.5, 1.1, 0.2),
                             (52.2, 59.0, 0.8, 0.6, 1.0),
                             (44.0, 41.0, 1.1, 0.7, -0.4),
                             (48.0, 62.0, 0.6, 0.5, 0.7)):
        mb.add_plane((x, y, 0.036 if y > 56 else 0.009), sx, sy, puddle,
                     rot=(0, 0, rz))
    mb.build(_collection())

    # Huella de mano en el azulejo de la ducha
    mb = MeshBuilder("VEST_Handprint_DECAL")
    hand = bpy.data.materials["M_REC03_DecalHand"]
    mb.add_plane((53.3, 63.78, 1.55), 0.17, 0.20, hand,
                 rot=(math.radians(90), 0, 0))
    mb.build(_collection())


def _add_text_object(name, text, size, loc, normal, mat, extrude=0.003):
    cu = bpy.data.curves.new("TMP_" + name, type="FONT")
    cu.body = text
    cu.size = size
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.extrude = extrude
    ob = bpy.data.objects.new("TMP_" + name, cu)
    bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    me.materials.append(mat)
    ob2 = bpy.data.objects.new(name, me)
    _collection().objects.link(ob2)
    up = Vector((0, 0, 1))
    n = Vector(normal).normalized()
    right = up.cross(n).normalized()
    basis = Matrix((right, up, n)).transposed()
    ob2.matrix_world = Matrix.Translation(Vector(loc)) @ basis.to_4x4()
    bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.curves.remove(cu)
    return ob2


def build_ceiling_beams():
    steel = bpy.data.materials["M_FM_Steel_Dark"]
    for i, y in enumerate((48.0, 58.0)):
        mb = MeshBuilder("VEST_CeilingBeam_X_%02d" % (i + 1))
        mb.add_box((45.0, y, 4.30), (29.7, 0.24, 0.03), steel)
        mb.add_box((45.0, y, 4.04), (29.7, 0.24, 0.03), steel)
        mb.add_box((45.0, y, 4.17), (29.7, 0.035, 0.25), steel)
        mb.build(_collection())
    for i, x in enumerate((38.0, 50.0)):
        mb = MeshBuilder("VEST_CeilingBeam_Y_%02d" % (i + 1))
        # 12 mm por encima de las vigas X para que las alas no sean coplanarias.
        mb.add_box((x, 52.0, 4.312), (0.24, 23.7, 0.03), steel)
        mb.add_box((x, 52.0, 4.052), (0.24, 23.7, 0.03), steel)
        mb.add_box((x, 52.0, 4.182), (0.035, 23.7, 0.25), steel)
        mb.build(_collection())


def build_wall_details():
    steel = bpy.data.materials["M_FM_Steel_Dark"]
    dark = bpy.data.materials["M_VEST_Black"]
    red = bpy.data.materials["M_VEST_Red"]
    white = bpy.data.materials["M_FM_Label_White"]

    def vent(name, cx, cy, rz):
        mb = MeshBuilder(name)
        # Marco, fondo y lamas; se construye en local y se gira en Z.
        # En el muro sur (rz=0) el frente mira a -Y; en este/oeste el frente
        # mira al interior, por lo que se invierte la profundidad local.
        sign = -1.0 if abs(rz) < 0.1 else 1.0
        pieces = [
            ((0, 0, 0), (1.22, 0.07, 0.48), steel),
            ((0, sign * 0.045, 0), (1.08, 0.025, 0.36), dark),
        ]
        for j in range(5):
            pieces.append(((0, sign * 0.060, -0.14 + j * 0.07),
                           (1.02, 0.014, 0.035), steel))
        c, s = math.cos(rz), math.sin(rz)
        for (lx, ly, lz), size, mat in pieces:
            wx = cx + lx * c - ly * s
            wy = cy + lx * s + ly * c
            mb.add_box((wx, wy, 3.00 + lz), size, mat,
                       rot=(0, 0, rz))
        mb.build(_collection())

    vent("VEST_Vent_N_01", 33.4, 63.81, 0.0)
    vent("VEST_Vent_N_02", 42.0, 63.81, 0.0)
    vent("VEST_Vent_E_01", 59.81, 44.0, math.radians(90))
    vent("VEST_Vent_E_02", 59.81, 50.0, math.radians(90))
    vent("VEST_Vent_W_01", 30.19, 56.0, math.radians(-90))
    vent("VEST_Vent_W_02", 30.19, 60.0, math.radians(-90))

    # Pulsador de alarma junto a la puerta de servicio.
    mb = MeshBuilder("VEST_FireAlarm")
    mb.add_box((55.65, 40.25, 1.38), (0.17, 0.08, 0.24), red, bevel=0.003)
    mb.add_plane((55.65, 40.30, 1.42), 0.09, 0.06, white,
                 rot=(math.radians(-90), 0, 0))
    mb.add_cyl((55.65, 40.31, 1.28), 0.025, 0.02, white, axis="Y", segments=10)
    mb.build(_collection())

    # Carrete de manguera contra incendios en el muro este.
    mb = MeshBuilder("VEST_FireHoseReel")
    mb.add_cyl((59.70, 54.8, 1.25), 0.32, 0.16, red, axis="X", segments=20,
               bevel=0.004)
    mb.add_cyl((59.60, 54.8, 1.25), 0.24, 0.18, dark, axis="X", segments=18)
    mb.add_cyl((59.82, 54.8, 1.25), 0.10, 0.08, steel, axis="X", segments=12)
    mb.add_box((59.50, 54.8, 0.88), (0.08, 0.10, 0.18), red)
    mb.add_cyl((59.50, 54.8, 0.80), 0.025, 0.18, steel, axis="Z", segments=8)
    mb.build(_collection())

    # Logotipo NEXUS sobre las taquillas del muro norte.
    mb = MeshBuilder("VEST_NexusLogo_SIGN")
    mb.add_box((38.7, 63.81, 3.24), (2.15, 0.06, 0.62), dark)
    mb.add_box((38.7, 63.80, 3.55), (2.22, 0.05, 0.03), steel)
    mb.add_box((38.7, 63.80, 2.93), (2.22, 0.05, 0.03), steel)
    mb.build(_collection())
    _add_text_object("VEST_NexusLogoText_SIGN", "NEXUS", 0.34,
                     (38.7, 63.76, 3.24), (0, -1, 0),
                     bpy.data.materials["M_VEST_Emissive_Green"], 0.004)


def build_baseboards():
    mb = MeshBuilder("VEST_Baseboards_TRIM")
    dark = bpy.data.materials["M_VEST_Locker_Green"]
    # Muro sur (y=40,15): tramos visibles entre taquillas y puertas.
    for x0, x1 in ((30.2, 31.45), (38.75, 39.98), (46.02, 47.05),
                   (54.35, 55.95)):
        mb.add_box(((x0 + x1) / 2, 40.18, 0.07),
                   (x1 - x0, 0.035, 0.14), dark)
    # Muro oeste (x=30,15).
    for y0, y1 in ((40.2, 41.55), (46.45, 47.98), (52.02, 52.75)):
        mb.add_box((30.18, (y0 + y1) / 2, 0.07),
                   (0.035, y1 - y0, 0.14), dark)
    # Muro este (x=59,85).
    for y0, y1 in ((40.2, 41.55), (53.65, 55.95)):
        mb.add_box((59.82, (y0 + y1) / 2, 0.07),
                   (0.035, y1 - y0, 0.14), dark)
    # Muro norte (y=63,85), solo el tramo del lavabo.
    mb.add_box((48.55, 63.82, 0.07), (5.25, 0.035, 0.14), dark)
    mb.build(_collection())


def build_column_details():
    steel = bpy.data.materials["M_FM_Steel_Dark"]
    rubber = bpy.data.materials["M_FM_Rubber"]
    for i, (x, y) in enumerate(((38, 48), (38, 58), (50, 48), (50, 58))):
        mb = MeshBuilder("VEST_ColumnBase_%02d" % (i + 1))
        mb.add_box((x, y, 0.015), (0.66, 0.66, 0.024), steel)
        mb.add_box((x, y, 0.045), (0.58, 0.58, 0.04), steel)
        for sx in (-1, 1):
            for sy in (-1, 1):
                mb.add_cyl((x + sx * 0.245, y + sy * 0.245, 0.075),
                           0.022, 0.022, steel, axis="Z", segments=8)
        mb.add_box((x, y, 0.80), (0.50, 0.50, 0.12), rubber,
                   bevel=0.006, segments=1)
        mb.add_box((x, y, 1.18), (0.52, 0.52, 0.025), steel)
        mb.build(_collection())


# ---------------------------------------------------------------------------
# Ensamblado
# ---------------------------------------------------------------------------


def _collection():
    col = bpy.data.collections.get(COL_NAME)
    if col is None:
        col = bpy.data.collections.new(COL_NAME)
        bpy.context.scene.collection.children.link(col)
    return col


def clean_collection():
    col = bpy.data.collections.get(COL_NAME)
    if col is not None:
        for ob in list(col.objects):
            data = ob.data
            bpy.data.objects.remove(ob, do_unlink=True)
            if data is not None and data.users == 0:
                if isinstance(data, bpy.types.Mesh):
                    bpy.data.meshes.remove(data)
                elif isinstance(data, bpy.types.Curve):
                    bpy.data.curves.remove(data)
        bpy.data.collections.remove(col)
    print("VEST collection cleaned")


def build_all():
    clean_collection()
    ensure_materials()

    # 23 bancos de taquillas: 138 puertas.
    # Muro sur, oeste, este y norte con huecos de circulación.
    banks = []
    # Caras interiores reales: sur y=40.15, norte y=63.85, oeste x=30.15,
    # este x=59.85. El fondo de cada banco queda 2 cm por delante.
    for i, x in enumerate((32.7, 35.1, 37.5)):
        banks.append((f"VEST_LockerBank_SW_{i+1:02d}", x, 40.445, 0.0,
                      (0, 2) if i == 0 else ((4,) if i == 1 else ())))
    for i, x in enumerate((48.3, 50.7, 53.1)):
        banks.append((f"VEST_LockerBank_SE_{i+1:02d}", x, 40.445, 0.0,
                      (1, 5) if i == 1 else ()))
    for i, y in enumerate((42.8, 45.2, 47.6, 50.0, 52.4)):
        banks.append((f"VEST_LockerBank_E_{i+1:02d}", 59.565, y,
                      math.radians(90), (3,) if i == 1 else ()))
    for i, x in enumerate((32.7, 35.1, 37.5, 39.9, 42.3, 44.7)):
        banks.append((f"VEST_LockerBank_N_{i+1:02d}", x, 63.565,
                      math.radians(180), (5,) if i == 2 else ()))
    for i, y in enumerate((54.0, 56.4, 58.8, 61.2)):
        banks.append((f"VEST_LockerBank_WN_{i+1:02d}", 30.44, y,
                      math.radians(-90), (2, 4) if i == 1 else ()))
    for i, y in enumerate((42.8, 45.2)):
        banks.append((f"VEST_LockerBank_WS_{i+1:02d}", 30.44, y,
                      math.radians(-90), ()))

    for idx, (name, x, y, rz, opens) in enumerate(banks):
        items = (0, 2) if idx in (0, 4, 7, 18) else ()
        build_locker_bank(name, x, y, rz, open_doors=opens,
                          number_start=(idx * 6) % 9, interior_items=items)

    # Bancos
    benches = [
        ("VEST_Bench_SW_A", 33.9, 42.25, 0.0),
        ("VEST_Bench_SW_B", 36.3, 42.25, 0.0),
        ("VEST_Bench_SE_A", 49.5, 42.25, 0.0),
        ("VEST_Bench_SE_B", 51.9, 42.25, 0.0),
        ("VEST_Bench_E_A", 57.35, 43.85, math.radians(90)),
        ("VEST_Bench_E_B", 57.35, 46.25, math.radians(90)),
        ("VEST_Bench_E_C", 57.35, 48.65, math.radians(90)),
        ("VEST_Bench_E_D", 57.35, 51.05, math.radians(90)),
        ("VEST_Bench_N_A", 33.9, 61.45, 0.0),
        ("VEST_Bench_N_B", 36.3, 61.45, 0.0),
        ("VEST_Bench_N_C", 43.4, 61.45, 0.0),
        ("VEST_Bench_WN_A", 32.4, 55.1, math.radians(90)),
        ("VEST_Bench_WN_B", 32.4, 57.5, math.radians(90)),
        ("VEST_Bench_WS_A", 32.4, 44.0, math.radians(90)),
        # Islas centrales: dos bancos espalda con espalda en cada cuadrante.
        ("VEST_Bench_Island_SW_A", 36.5, 45.65, 0.0),
        ("VEST_Bench_Island_SW_B", 36.5, 46.35, math.pi),
        ("VEST_Bench_Island_SE_A", 48.5, 45.65, 0.0),
        ("VEST_Bench_Island_SE_B", 48.5, 46.35, math.pi),
        ("VEST_Bench_Island_NW_A", 36.5, 53.65, 0.0),
        ("VEST_Bench_Island_NW_B", 36.5, 54.35, math.pi),
        ("VEST_Bench_Island_NE_A", 48.5, 53.65, 0.0),
        ("VEST_Bench_Island_NE_B", 48.5, 54.35, math.pi),
    ]
    for i, (name, x, y, rz) in enumerate(benches):
        build_bench(name, x, y, rz, lower_shelf=(i % 3 == 0))

    build_showers()
    build_vanity()
    build_walls_and_signs()
    build_ceiling_and_lights()
    build_ceiling_beams()
    build_wall_details()
    build_baseboards()
    build_props()
    build_column_details()

    # Runner de goma en el eje de entrada
    mb = MeshBuilder("VEST_Runner_Main_MAT")
    mb.add_box((43.0, 47.5, 0.007), (0.95, 12.0, 0.014),
               bpy.data.materials["M_FM_Rubber"], bevel=0.002)
    mb.build(_collection())

    # Estadísticas
    col = _collection()
    tris = 0
    verts = 0
    for ob in col.objects:
        if ob.type != "MESH":
            continue
        verts += len(ob.data.vertices)
        tris += sum(len(p.vertices) - 2 for p in ob.data.polygons)
    print("VEST_BUILD objects=%d verts=%d tris=%d" % (len(col.objects), verts, tris))
    for ob in sorted(col.objects, key=lambda o: o.name):
        print("VEST_OBJ", ob.name,
              "tris", sum(len(p.vertices) - 2 for p in ob.data.polygons),
              "mats", len(ob.data.materials))


if __name__ == "__main__":
    build_all()
