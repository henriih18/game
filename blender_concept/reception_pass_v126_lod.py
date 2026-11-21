"""Optimización de la RECEPCIÓN del Nivel 1 (v126).

Crea copias locales decimadas (LOD1) de los props más pesados de la
recepción. Los objetos y mallas de la biblioteca compartida NO se
modifican: el objeto original se oculta y se marca con `replaced_by`,
igual que en los pases anteriores del proyecto.

Objetivo: bajar los triángulos visibles de la sala manteniendo la
silueta de los props a distancia de juego.
"""

import bmesh
import bpy
from mathutils import Vector

X = (-20.4, -3.6)
Y = (1.4, 12.0)
Z = (-6.2, 0.6)
COLLECTION = "NEXUS_V05_REC_LOD1"
MAX_TRIS = 2500
MIN_RATIO = 0.06
# presupuesto por tipo de prop: lo que está en el mostrador o se ve de cerca
# necesita más malla que una silla repetida o un portapapeles.
BUDGETS = (
    ("chair", 1200),
    ("clock", 600),
    ("clipboard", 500),
    ("stapler", 400),
    ("monitor", 700),
    ("MON_", 700),
    ("paper", 300),
    ("desk", 1100),
    ("box_low", 900),
    ("trashbag", 1100),
    ("lamp", 1600),
    ("fire_alarm", 800),
)
SKIP_PREFIX = ("NEXUS_V05_REC_CS_", "NEXUS_V05_REC_COUNTER_", "NEXUS_V05_REC_BASEBOARD_",
               "NEXUS_V05_REC_WAINSCOT_", "NEXUS_V05_REC_EMERG_", "NEXUS_V05_RECEPCION_")


def in_reception(obj):
    loc = obj.matrix_world.translation
    return X[0] <= loc.x <= X[1] and Y[0] <= loc.y <= Y[1] and Z[0] <= loc.z <= Z[1]


def collection():
    coll = bpy.data.collections.get(COLLECTION)
    if coll is None:
        coll = bpy.data.collections.new(COLLECTION)
        bpy.context.scene.collection.children.link(coll)
    return coll


def budget_for(name):
    lowered = name.lower()
    for key, value in BUDGETS:
        if key.lower() in lowered:
            return value
    return MAX_TRIS


def decimate_ratio(tris, cap):
    if tris <= cap:
        return 1.0
    return max(cap / tris, MIN_RATIO)


def build_lod(obj, ratio, coll):
    name = obj.name + "_LOD1"
    existing = bpy.data.objects.get(name)
    if existing is not None:
        return existing, 0

    source = obj.data
    source.calc_loop_triangles()
    before = len(source.loop_triangles)

    bm = bmesh.new()
    bm.from_mesh(source)
    mesh = bpy.data.meshes.new(name + "_mesh")
    bm.to_mesh(mesh)
    bm.free()
    for mat in source.materials:
        mesh.materials.append(mat)

    temp = bpy.data.objects.new("__tmp_decimate", mesh)
    bpy.context.scene.collection.objects.link(temp)
    mod = temp.modifiers.new("lod", "DECIMATE")
    mod.decimate_type = "COLLAPSE"
    mod.ratio = ratio
    mod.use_collapse_triangulate = True

    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = temp.evaluated_get(depsgraph)
    baked = bpy.data.meshes.new_from_object(evaluated)
    baked.name = name + "_mesh"
    for mat in source.materials:
        if mat is not None and mat.name not in [m.name for m in baked.materials if m]:
            baked.materials.append(mat)
    baked.materials.clear()
    for mat in source.materials:
        baked.materials.append(mat)

    bpy.data.objects.remove(temp, do_unlink=True)
    bpy.data.meshes.remove(mesh)

    lod = bpy.data.objects.new(name, baked)
    coll.objects.link(lod)
    # sin padre: el prop es estático y así la matriz del mundo no se altera
    lod.matrix_world = obj.matrix_world.copy()
    lod["lod_of"] = obj.name
    lod["lod_ratio"] = round(ratio, 3)

    bpy.context.view_layer.update()
    delta = (lod.matrix_world.translation - obj.matrix_world.translation).length
    if delta > 0.001:
        raise RuntimeError(f"LOD desplazado {name}: {delta:.3f} m")

    obj.hide_render = True
    obj.hide_viewport = True
    obj["replaced_by"] = name
    baked.calc_loop_triangles()
    return lod, before - len(baked.loop_triangles)


def reset(previous_coll):
    """Elimina LOD1 previos de este pase y restaura los originales."""
    removed = 0
    for obj in list(bpy.data.objects):
        if obj.get("lod_of"):
            baked = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            if baked.users == 0:
                bpy.data.meshes.remove(baked)
            removed += 1
    restored = 0
    for obj in bpy.data.objects:
        target = obj.get("replaced_by")
        if isinstance(target, str) and target.endswith("_LOD1"):
            obj.hide_render = False
            obj.hide_viewport = False
            del obj["replaced_by"]
            restored += 1
    print("RESET_REMOVED", removed, "RESTORED", restored)


def main():
    reset(bpy.data.collections.get(COLLECTION))
    coll = collection()
    candidates = []
    for obj in bpy.data.objects:
        if obj.type != "MESH" or not obj.visible_get() or not in_reception(obj):
            continue
        if obj.name.startswith(SKIP_PREFIX) or obj.name.startswith("NEXUS_L1_DIS_"):
            pass
        if obj.name.startswith(("NEXUS_V05_REC_CS_", "NEXUS_V05_REC_COUNTER_",
                                "NEXUS_V05_REC_BASEBOARD_", "NEXUS_V05_REC_WAINSCOT_",
                                "NEXUS_V05_REC_EMERG_", "NEXUS_V05_RECEPCION_")):
            continue
        obj.data.calc_loop_triangles()
        tris = len(obj.data.loop_triangles)
        if tris < 1500:
            continue
        candidates.append((tris, obj))

    # Los objetos enlazados viven dentro de la colección de biblioteca
    # NEXUS_ASSET_L1: ocultarlos por script no persiste al guardar el .blend
    # (requiere override de biblioteca, que este proyecto no usa). Por eso
    # solo se deciman objetos locales; los assets compartidos quedan como
    # pendiente explícito en la documentación.
    skipped = [item for item in candidates if item[1].library is not None]
    candidates = [item for item in candidates if item[1].library is None]
    print("SKIPPED_LINKED_ASSETS", len(skipped), "tris", sum(t for t, _ in skipped))

    candidates.sort(reverse=True, key=lambda item: item[0])
    total_saved = 0
    made = []
    for tris, obj in candidates[:40]:
        ratio = decimate_ratio(tris, budget_for(obj.name))
        if ratio >= 0.999:
            continue
        lod, saved = build_lod(obj, ratio, coll)
        total_saved += saved
        made.append((obj.name, tris, len(lod.data.loop_triangles)))

    for name, before, after in made:
        print(f"LOD {name:<50} {before:6,} -> {after:6,}")
    print("LOD_OBJECTS_CREATED", len(made))
    print("TRIS_SAVED", total_saved)


main()
