"""Pase de acercado a la referencia para El Imitador generado.

- Oscurece y enriquece la piel con un set nuevo (BC + R).
- Encorva el torso y estrecha/alarga el cráneo y el cuello.
- Hunde el abdomen y marca costillas de forma sutil.
- Oscurece la cavidad bucal y añade dientes finos.
- Renderiza vistas de revisión.

Idempotente solo por ejecución: no reconstruye desde cero, deforma la malla
actual. Guarda el .blend de trabajo.
"""
from __future__ import annotations

import math
import random
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path("/home/riyo/Documentos/game")
TEX = ROOT / "assets" / "art" / "fm" / "imitador"
BLEND = ROOT / "nexus" / "nivel_01" / "FM_IMITATOR_GENERATED_WORK.blend"
RENDER_FULL = Path("/tmp/opencode/imi_ref_full.png")
RENDER_HEAD = Path("/tmp/opencode/imi_ref_head.png")


def smoothstep(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def load_image(path: Path, color_space: str) -> bpy.types.Image:
    img = bpy.data.images.load(str(path), check_existing=True)
    img.colorspace_settings.name = color_space
    return img


def set_principled_input(node: bpy.types.Node, name: str, value) -> None:
    sock = node.inputs.get(name)
    if sock is not None:
        sock.default_value = value


def setup_skin(ob: bpy.types.Object) -> None:
    mat = bpy.data.materials.get("M_Gen_ImitadorSkin")
    if mat is None:
        mat = bpy.data.materials.new("M_Gen_ImitadorSkin")
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    bsdf = next((n for n in nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        out = next((n for n in nodes if n.type == "OUTPUT_MATERIAL"), None)
        if out is None:
            out = nodes.new("ShaderNodeOutputMaterial")
        links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    bc = load_image(TEX / "T_Imitador_Skin_Ref_BC.png", "sRGB")
    rough = load_image(TEX / "T_Imitador_Skin_Ref_R.png", "Non-Color")
    normal = load_image(ROOT / "assets" / "art" / "fm" / "flesh_normal.png", "Non-Color")

    tex = next((n for n in nodes if n.type == "TEX_IMAGE" and n.image and n.image.name.startswith("T_Imitador")), None)
    if tex is None:
        tex = nodes.new("ShaderNodeTexImage")
        tex.location = (-620, 320)
    tex.image = bc
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])

    rt = next((n for n in nodes if n.type == "TEX_IMAGE" and n.image and n.image.name.startswith("T_Imitador_Skin_Ref_R")), None)
    if rt is None:
        rt = nodes.new("ShaderNodeTexImage")
        rt.location = (-620, 20)
    rt.image = rough
    links.new(rt.outputs["Color"], bsdf.inputs["Roughness"])

    nt_normal = next((n for n in nodes if n.type == "NORMAL_MAP"), None)
    if nt_normal is None:
        nt_normal = nodes.new("ShaderNodeNormalMap")
        nt_normal.location = (-300, -160)
    nt_normal.inputs["Strength"].default_value = 0.85
    nt_normal.inputs["Color"].default_value = (0.5, 0.5, 1.0, 1.0)
    ntex = next((n for n in nodes if n.type == "TEX_IMAGE" and n.image and n.image.name == "flesh_normal.png"), None)
    if ntex is None:
        ntex = nodes.new("ShaderNodeTexImage")
        ntex.location = (-620, -260)
    ntex.image = normal
    links.new(ntex.outputs["Color"], nt_normal.inputs["Color"])
    links.new(nt_normal.outputs["Normal"], bsdf.inputs["Normal"])

    set_principled_input(bsdf, "Roughness", 0.66)
    set_principled_input(bsdf, "Metallic", 0.0)
    set_principled_input(bsdf, "Specular IOR Level", 0.34)
    set_principled_input(bsdf, "Subsurface Weight", 0.045)
    set_principled_input(bsdf, "Subsurface Radius", (0.09, 0.035, 0.022))
    set_principled_input(bsdf, "Subsurface Scale", 0.035)
    mat.diffuse_color = (0.20, 0.12, 0.10, 1.0)
    print("SKIN_SET", mat.name)


def deform_mesh(ob: bpy.types.Object) -> None:
    me = ob.data
    # Pivote de la inclinación: parte baja del esternón.
    pivot = Vector((0.0, 0.0, 1.15))
    hunch = math.radians(8.0)
    cos_h, sin_h = math.cos(hunch), math.sin(hunch)

    head_c = Vector((0.15, -0.78, 1.99))
    for v in me.vertices:
        p = v.co.copy()

        # 1) Encorvar la parte superior del cuerpo hacia delante (-Y).
        w_h = smoothstep((p.z - 1.15) / 0.85)
        if w_h > 0.0:
            rel = p - pivot
            y = rel.y * cos_h - rel.z * sin_h
            z = rel.y * sin_h + rel.z * cos_h
            p = Vector((rel.x, y, z)) + pivot

        # 2) Estrechar y alargar el cráneo; cuello más fino.
        w_head = smoothstep((p.z - 1.70) / 0.22) * smoothstep((-0.25 - p.y) / 0.22)
        if w_head > 0.0:
            rel = p - head_c
            p = head_c + Vector((
                rel.x * (1.0 - 0.15 * w_head),
                rel.y * (1.0 + 0.05 * w_head),
                rel.z * (1.0 + 0.12 * w_head),
            ))

        w_neck = smoothstep((p.z - 1.52) / 0.16) * smoothstep((0.10 - p.y) / 0.40) * (1.0 - smoothstep((p.z - 1.78) / 0.10))
        if w_neck > 0.0:
            p.x *= 1.0 - 0.10 * w_neck

        # 3) Abdomen hundido y costillas sutiles.
        w_torso = smoothstep((p.z - 0.98) / 0.10) * smoothstep((1.55 - p.z) / 0.18) * smoothstep((-0.08 - p.y) / 0.18)
        if w_torso > 0.0:
            side = 1.0 - smoothstep((abs(p.x - 0.10) - 0.30) / 0.16)
            p.y += 0.022 * w_torso * side
            rib = max(0.0, math.sin((p.z - 1.02) * 38.0)) ** 3
            p.y -= 0.010 * rib * w_torso * side

        v.co = p
    me.update()
    print("DEFORM_DONE", len(me.vertices))


def mouth_bounds(ob: bpy.types.Object):
    me = ob.data
    maw_idx = next((i for i, s in enumerate(ob.material_slots) if s.material and s.material.name == "M_Gen_Maw"), -1)
    if maw_idx < 0:
        return None
    verts = set()
    for p in me.polygons:
        if p.material_index == maw_idx:
            verts.update(p.vertices)
    if not verts:
        return None
    co = [me.vertices[i].co for i in verts]
    mn = Vector((min(v.x for v in co), min(v.y for v in co), min(v.z for v in co)))
    mx = Vector((max(v.x for v in co), max(v.y for v in co), max(v.z for v in co)))
    return mn, mx


def darken_mouth(ob: bpy.types.Object, bounds) -> None:
    if bounds is None:
        return
    mn, mx = bounds
    c = (mn + mx) * 0.5
    rx = max(0.09, (mx.x - mn.x) * 0.5)
    rz = max(0.12, (mx.z - mn.z) * 0.5)
    me = ob.data
    skin_idx = next((i for i, s in enumerate(ob.material_slots) if s.material and s.material.name == "M_Gen_ImitadorSkin"), -1)
    maw_idx = next((i for i, s in enumerate(ob.material_slots) if s.material and s.material.name == "M_Gen_Maw"), -1)
    if skin_idx < 0 or maw_idx < 0:
        return
    changed = 0
    for p in me.polygons:
        if p.material_index != skin_idx:
            continue
        q = p.center
        if q.y < mn.y + 0.015:
            continue
        if ((q.x - c.x) / rx) ** 2 + ((q.z - c.z) / rz) ** 2 <= 0.92:
            p.material_index = maw_idx
            changed += 1
    me.update()
    print("MOUTH_DARKENED", changed)


def add_teeth(ob: bpy.types.Object, bounds, join: bool = True) -> None:
    if bounds is None:
        return
    mn, mx = bounds
    c = (mn + mx) * 0.5
    rx = max(0.10, (mx.x - mn.x) * 0.5)
    rz = max(0.13, (mx.z - mn.z) * 0.5)
    bone = bpy.data.materials.get("M_Gen_Bone")
    if bone is None:
        return
    made = []
    random.seed(7)
    # 12 dientes superiores y 12 inferiores, finos y hacia dentro.
    for i in range(12):
        t = (i + 0.5) / 12.0
        ang = math.pi * (0.08 + 0.84 * t)
        for sign in (-1.0, 1.0):
            z = c.z + sign * rz * math.sin(ang) * 0.94
            x = c.x + rx * math.cos(ang) * 0.92
            base = Vector((x, mn.y + 0.012, z))
            direction = (Vector((c.x, base.y - 0.035, c.z)) - base).normalized()
            length = 0.046 + random.uniform(-0.006, 0.008)
            bpy.ops.mesh.primitive_cone_add(
                vertices=7, radius1=0.0048, radius2=0.0008, depth=length,
                location=base + direction * (length * 0.5),
            )
            tooth = bpy.context.object
            tooth.name = f"Imitator_RefTooth_{i}_{'u' if sign > 0 else 'd'}"
            tooth.rotation_mode = "QUATERNION"
            tooth.rotation_quaternion = direction.to_track_quat("Z", "Y")
            tooth.data.materials.append(bone)
            made.append(tooth)
    # Unir los dientes a la malla principal conservando materiales.
    if join:
        bpy.ops.object.select_all(action="DESELECT")
        ob.select_set(True)
        for tooth in made:
            tooth.select_set(True)
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.join()
    print("TEETH", len(made))


def render_views() -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 640
    scene.render.resolution_y = 640
    scene.render.resolution_percentage = 100
    cam = bpy.data.objects.get("ReviewCam")
    if cam is None:
        data = bpy.data.cameras.new("ReviewCam")
        cam = bpy.data.objects.new("ReviewCam", data)
        scene.collection.objects.link(cam)
    cam.data.lens = 55
    scene.camera = cam
    # Vista completa tres cuartos.
    cam.location = (2.6, -3.8, 1.75)
    target = Vector((0.0, 0.0, 1.15))
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(RENDER_FULL)
    bpy.ops.render.render(write_still=True)
    # Primer plano de cabeza.
    cam.location = (1.35, -2.0, 2.05)
    target = Vector((0.15, -0.55, 1.92))
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(RENDER_HEAD)
    bpy.ops.render.render(write_still=True)
    print("RENDERS", RENDER_FULL, RENDER_HEAD)


def main() -> None:
    ob = bpy.data.objects.get("Imitator_Generated")
    if ob is None:
        raise RuntimeError("Imitator_Generated no existe")
    setup_skin(ob)
    deform_mesh(ob)
    bounds = mouth_bounds(ob)
    print("MOUTH_BOUNDS", bounds)
    darken_mouth(ob, bounds)
    add_teeth(ob, bounds)
    # Suavizado tras unir dientes.
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(36.0))
    render_views()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    print("IMITATOR_REF_PASS_SAVED", BLEND)


if __name__ == "__main__":
    main()
