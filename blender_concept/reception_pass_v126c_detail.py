"""Recepción del Nivel 1 (v126c): paredes del recinto con textura y
muebles blocky con detalle.

1. Aplica los materiales de recepción (muro, techo, zócalo) a las paredes,
   particiones, parapetos y techos del recinto de oficina/aseo, que seguían
   con el hormigón genérico y se leían planos.
2. Añade bisel a los muebles de caja (bancos, sillones, mesas, jardineras)
   para que dejen de verse como primitivas.
3. Da materiales propios (tapizado, chapa pintada, madera) a esos muebles.
"""

import bmesh
import bpy

WALL_MAT = "NEXUS_V05_MAT_Rec_Wall"
CEIL_MAT = "NEXUS_V05_MAT_Rec_Ceiling"
BASE_MAT = "NEXUS_V05_MAT_Baseboard"

WALL_TARGETS = [
    "NEXUS_V05_OFFICE_WALL_W_0",
    "NEXUS_V05_OFFICE_WALL_W_1",
    "NEXUS_V05_OFFICE_WALL_W_2",
    "NEXUS_V05_OFFICE_WALL_N",
    "NEXUS_V05_OFFICE_WALL_E",
    "NEXUS_V05_OFFICE_WALL_REST_TOP",
    "NEXUS_V05_OFFICE_WALL_OFF_TOP",
    "NEXUS_V05_OFFICE_PARTITION",
    "NEXUS_V05_REST_PARTITION",
]
CEIL_TARGETS = [
    "NEXUS_V05_OFFICE_ROOF",
    "NEXUS_V05_OFFICE_PARAPET_0",
    "NEXUS_V05_OFFICE_PARAPET_1",
    "NEXUS_V05_OFFICE_PARAPET_2",
    "NEXUS_V05_OFFICE_PARAPET_3",
]
BASE_TARGETS = [
    "NEXUS_V05_OFFICE_BASE_0",
    "NEXUS_V05_OFFICE_BASE_1",
    "NEXUS_V05_OFFICE_BASE_2",
    "NEXUS_V05_REST_PARTITION_TRIM",
]

# objetos de caja que deben dejar de parecer cubos
BEVEL_TARGETS = [
    "NEXUS_V05_REC_BENCH",
    "NEXUS_V05_REC_BENCH2",
    "NEXUS_V05_C_REC_LOUNGE_W_SEAT",
    "NEXUS_V05_C_REC_LOUNGE_W_BACK",
    "NEXUS_V05_C_REC_LOUNGE_E_SEAT",
    "NEXUS_V05_C_REC_LOUNGE_E_BACK",
    "NEXUS_V05_C_REC_WAIT_S_SEAT",
    "NEXUS_V05_C_REC_WAIT_S_BACK",
    "NEXUS_V05_C_REC_TABLE_TOP",
    "NEXUS_V05_REC_PLANTER_0",
    "NEXUS_V05_REC_PLANTER_1",
    "NEXUS_V05_OFFICE_CABINET",
]

UPHOLSTERY = [
    "NEXUS_V05_REC_BENCH",
    "NEXUS_V05_REC_BENCH2",
    "NEXUS_V05_C_REC_LOUNGE_W_SEAT",
    "NEXUS_V05_C_REC_LOUNGE_W_BACK",
    "NEXUS_V05_C_REC_LOUNGE_E_SEAT",
    "NEXUS_V05_C_REC_LOUNGE_E_BACK",
    "NEXUS_V05_C_REC_WAIT_S_SEAT",
    "NEXUS_V05_C_REC_WAIT_S_BACK",
]
PAINTED = [
    "NEXUS_V05_REC_PLANTER_0",
    "NEXUS_V05_REC_PLANTER_1",
    "NEXUS_V05_OFFICE_CABINET",
]
WOOD = ["NEXUS_V05_C_REC_TABLE_TOP"]


def material(name, color, roughness, metallic=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def assign(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def single_user_mesh(obj):
    """Evita que el bisel afecte a muebles de otras salas."""
    if obj.data.users > 1:
        obj.data = obj.data.copy()


def bevel_object(obj, width=0.012, segments=2):
    single_user_mesh(obj)
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    try:
        bmesh.ops.bevel(
            bm,
            geom=list(bm.edges) + list(bm.verts),
            offset=width,
            offset_type="OFFSET",
            segments=segments,
            profile=0.5,
            affect="EDGES",
            clamp_overlap=True,
            loop_slide=True,
        )
    except TypeError:
        bmesh.ops.bevel(
            bm,
            geom=list(bm.edges),
            offset=width,
            segments=segments,
            affect="EDGES",
        )
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def main():
    wall = bpy.data.materials.get(WALL_MAT)
    ceil = bpy.data.materials.get(CEIL_MAT)
    base = bpy.data.materials.get(BASE_MAT)
    if wall is None or ceil is None:
        raise RuntimeError("faltan los materiales de recepción v126")

    textured = 0
    for name in WALL_TARGETS:
        obj = bpy.data.objects.get(name)
        if obj is None:
            continue
        assign(obj, wall)
        textured += 1
    for name in CEIL_TARGETS:
        obj = bpy.data.objects.get(name)
        if obj is None:
            continue
        assign(obj, ceil)
        textured += 1
    for name in BASE_TARGETS:
        obj = bpy.data.objects.get(name)
        if obj is None:
            continue
        assign(obj, base)
        textured += 1

    beveled = 0
    for name in BEVEL_TARGETS:
        obj = bpy.data.objects.get(name)
        if obj is None or obj.type != "MESH":
            continue
        if obj.get("bevel_passed"):
            continue
        bevel_object(obj)
        obj["bevel_passed"] = True
        beveled += 1

    upholstery = material("NEXUS_V05_MAT_Upholstery", (0.020, 0.042, 0.048), 0.38)
    painted = material("NEXUS_V05_MAT_Rec_Painted_Green", (0.035, 0.062, 0.052), 0.44, 0.2)
    wood = material("NEXUS_V05_MAT_Rec_Wood", (0.085, 0.055, 0.032), 0.55)

    restyled = 0
    for names, mat in ((UPHOLSTERY, upholstery), (PAINTED, painted), (WOOD, wood)):
        for name in names:
            obj = bpy.data.objects.get(name)
            if obj is None:
                continue
            assign(obj, mat)
            restyled += 1

    print("WALLS_TEXTURED", textured)
    print("FURNITURE_BEVELED", beveled)
    print("FURNITURE_RESTYLED", restyled)


main()
