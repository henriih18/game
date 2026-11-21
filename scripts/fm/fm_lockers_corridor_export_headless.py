"""Exporta SOLO el tramo de pasillo que falta entre Z10 y Vestuarios.

Fuente: nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend (no se guarda).
Salida: assets/models/fm/lockers_corridor_kit.glb

El máster ya contiene el suelo y el muro central del ChangingConnector, pero
no se exportaron a ningún GLB de Godot. El muro oeste y el techo del
ChangingConnector existen en una sola pieza de 35,7 m que se solapa con el
kit ya montado de Z10; para no duplicar caras coplanares se duplican en
memoria y se recortan en y=30 (Blender), conservando solo el tramo
y=30..39,84 que corresponde al hueco z=-30,15..-40,15 de Godot.

No se modifica ni se guarda el .blend. No se toca ningún GLB existente.

Uso:
  blender -b nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend \
      --python scripts/fm/fm_lockers_corridor_export_headless.py
"""

import os
import sys

import bpy
import bmesh
from mathutils import Vector

OUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "assets", "models", "fm", "lockers_corridor_kit.glb",
)
CUT_Y = 30.0

# Piezas del kit hero de Z10 que forman el tramo que falta. Ya existen en el
# máster; el script solo las selecciona y las exporta.
KIT_PIECES = [
    "KIT_PILOT_Z10_Floor_04.001",
    "KIT_PILOT_Z10_Floor_04.002",
    "KIT_PILOT_Z10_Floor_30.001",
    "KIT_PILOT_Z10_Wall_N_02.001",
    "KIT_PILOT_Z10_Wall_N_02.002",
    "KIT_PILOT_Z10_Wall_N_02.003",
    "KIT_PILOT_Z10_Base_W_29p0.001",
    "KIT_PILOT_Z10_Base_W_29p0.002",
    "KIT_PILOT_Z10_Base_W_29p0.003",
]
# Los tramos del kit se colocaron en el máster con solapes de 1-3 cm para no
# dejar juntas. Esos solapes son caras coplanares y producirían z-fighting al
# montar el pasillo en Godot. Se recortan solo en memoria (el .blend no se
# guarda) para que cada pieza termine exactamente donde empieza la siguiente.
KIT_CROPS = {
    "KIT_PILOT_Z10_Floor_04.002": (34.0, 37.98),
    "KIT_PILOT_Z10_Floor_30.001": (37.98, 40.0),
    "KIT_PILOT_Z10_Wall_N_02.002": (33.86, 37.86),
    "KIT_PILOT_Z10_Wall_N_02.003": (37.86, 39.83),
    "KIT_PILOT_Z10_Base_W_29p0.003": (36.24, 38.98),
}
# Muro oeste y techo: una sola pieza larga en el máster. Se recortan en
# memoria para no repetir el tramo que ya cubre el kit de Z10.
CROP_PIECES = [
    ("SM_L1_Conn_ChangingConnector_Wall_W_0", "SM_L1_LockersCorridor_Wall_W"),
    ("SM_L1_Conn_ChangingConnector_Ceiling", "SM_L1_LockersCorridor_Ceiling"),
]


def _bisect_keep(obj: "bpy.types.Object", world_y: float, keep_above: bool) -> None:
    """Recorta obj en el plano world_y y conserva el lado indicado."""
    # El techo vive en una colección oculta y su matrix_world no está
    # evaluada hasta refrescar la vista; sin esto el plano de corte se
    # aplicaría en coordenadas locales y se perdería toda la malla.
    bpy.context.view_layer.update()
    matrix = obj.matrix_world.copy()
    if matrix.translation.length < 0.001 and obj.location.length > 0.001:
        matrix = obj.matrix_basis.copy()
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    inv = matrix.inverted()
    plane_co = inv @ Vector((0.0, world_y, 0.0))
    normal_matrix = matrix.inverted().transposed().to_3x3()
    plane_no = (normal_matrix @ Vector((0.0, 1.0, 0.0))).normalized()
    # Se corta sin borrar y luego se eliminan los vértices por su coordenada
    # world Y. Así el resultado no depende de la orientación local de las
    # piezas rotadas del kit ni del signo de clear_inner/clear_outer.
    bmesh.ops.bisect_plane(
        bm,
        geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
        plane_co=plane_co,
        plane_no=plane_no,
        clear_inner=False,
        clear_outer=False,
    )
    eps = 1.0e-5
    if keep_above:
        doomed = [v for v in bm.verts if (matrix @ v.co).y < world_y - eps]
    else:
        doomed = [v for v in bm.verts if (matrix @ v.co).y > world_y + eps]
    if doomed:
        bmesh.ops.delete(bm, geom=doomed, context="VERTS")
    boundary = [edge for edge in bm.edges if edge.is_boundary]
    if boundary:
        bmesh.ops.holes_fill(bm, edges=boundary, sides=0)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def _bisect_keep_between(obj: "bpy.types.Object", y_min: float, y_max: float) -> None:
    """Recorta obj al tramo world_y ∈ [y_min, y_max]."""
    _bisect_keep(obj, y_min, True)
    _bisect_keep(obj, y_max, False)


def main() -> int:
    if bpy.data.filepath == "":
        print("ERROR: hay que abrir el máster con -b <blend>")
        return 1

    for obj in bpy.context.view_layer.objects:
        obj.select_set(False)

    selected = []
    missing = []
    for name in KIT_PIECES:
        obj = bpy.data.objects.get(name)
        if obj is None:
            missing.append(name)
            continue
        obj.hide_viewport = False
        obj.hide_render = False
        obj.hide_set(False)
        if name in KIT_CROPS:
            crop = KIT_CROPS[name]
            _bisect_keep_between(obj, crop[0], crop[1])
        obj.select_set(True)
        selected.append(obj)

    for source_name, new_name in CROP_PIECES:
        source = bpy.data.objects.get(source_name)
        if source is None:
            missing.append(source_name)
            continue
        source.hide_viewport = False
        source.hide_render = False
        source.hide_set(False)
        clone = source.copy()
        clone.data = source.data.copy()
        clone.name = new_name
        clone.data.name = new_name
        bpy.context.scene.collection.objects.link(clone)
        clone.hide_viewport = False
        clone.hide_render = False
        clone.hide_set(False)
        _bisect_keep(clone, CUT_Y, True)
        clone.select_set(True)
        selected.append(clone)

    if missing:
        print("ERROR: piezas ausentes en el máster: %s" % ", ".join(missing))
        return 1
    if not selected:
        print("ERROR: no hay geometría seleccionada")
        return 1

    bpy.context.view_layer.objects.active = selected[0]
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=OUT_PATH,
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
        export_materials="EXPORT",
        export_cameras=False,
        export_lights=False,
        export_extras=False,
    )
    print("FM_LOCKERS_CORRIDOR_EXPORT ok=%s objects=%d path=%s" % (
        str(os.path.exists(OUT_PATH)), len(selected), OUT_PATH,
    ))
    for obj in selected:
        print("  %s polys=%d mats=%s" % (
            obj.name,
            len(obj.data.polygons),
            [mat.name if mat else None for mat in obj.data.materials],
        ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
