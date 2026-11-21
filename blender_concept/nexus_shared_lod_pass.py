"""FRECUENCIA MUERTA - LOD de los assets de biblioteca usados por la recepcion.

La recepcion carga 18 objetos enlazados desde NEXUS_SHARED_ASSETS.blend. Se
verifico que esas mallas no se usan en los niveles 2-5 ni en el nucleo, pero
si en las salas del Nivel 1 que comparten el asset (oficina y seguridad).

Este script decima las mallas de la biblioteca, no las instancias: al estar
compartidas, la reduccion se aplica a todas las copias del Nivel 1.

Uso:
    blender -b nexus/compartido/NEXUS_SHARED_ASSETS.blend \
        --python blender_concept/nexus_shared_lod_pass.py

No forma parte del bucle normal del proyecto; se ejecuta una sola vez.
"""

import bpy

# malla: (ratio, nota)
TARGETS = {
    "Mesh.007": (0.40, "sillas SchoolChair_01 (5.072 -> ~2.030)"),
    "clipboard_a.002": (0.22, "portapapeles (6.176 -> ~1.360)"),
    "frame.003": (0.30, "carcasa de reloj de pared (3.380 -> ~1.010)"),
    "Plane.011": (0.50, "escritorio metalico (4.186 -> ~2.090)"),
    "Top_Cart.002": (0.35, "carrito de cafe, tapa y props (16.929 -> ~5.930)"),
    "Bottom_Cart.002": (0.35, "carrito de cafe, cuerpo (8.970 -> ~3.140)"),
    "Vert.002": (0.45, "lampara de tubo (7.606 -> ~3.420)"),
    "Cube.3288": (0.55, "monitores CRT (1.918 -> ~1.050)"),
}


def apply_decimate(mesh_name, ratio):
    """Decima una malla compartida y devuelve la nueva a todos sus usuarios."""
    mesh = bpy.data.meshes.get(mesh_name)
    if mesh is None:
        return None
    mesh.calc_loop_triangles()
    before = len(mesh.loop_triangles)
    users = [o for o in bpy.data.objects if o.type == "MESH" and o.data == mesh]

    # copia de un solo usuario para poder aplicar el modificador
    work = mesh.copy()
    work.name = mesh_name + "_lod"
    obj = bpy.data.objects.new("_lod_tmp", work)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    for o in bpy.context.selected_objects:
        o.select_set(False)
    obj.select_set(True)

    mod = obj.modifiers.new("LOD_DECIMATE", "DECIMATE")
    mod.decimate_type = "COLLAPSE"
    mod.ratio = ratio
    mod.use_collapse_triangulate = True
    bpy.ops.object.modifier_apply(modifier=mod.name)

    bpy.data.objects.remove(obj, do_unlink=True)
    for user in users:
        user.data = work
    old_name = mesh_name
    bpy.data.meshes.remove(mesh)
    work.name = old_name

    work.calc_loop_triangles()
    after = len(work.loop_triangles)
    return before, after


def main():
    total_before = total_after = 0
    for mesh_name, (ratio, note) in TARGETS.items():
        result = apply_decimate(mesh_name, ratio)
        if result is None:
            print("MISSING", mesh_name)
            continue
        before, after = result
        total_before += before
        total_after += after
        print("LOD", mesh_name, before, "->", after, "|", note)
    print("LOD_TOTAL", total_before, "->", total_after,
          "(%d %%)" % round(100 * (1 - total_after / max(1, total_before))))
    bpy.ops.wm.save_mainfile()
    print("SAVED", bpy.data.filepath)


main()
