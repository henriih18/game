"""Exporta el subconjunto jugable de la recepción de NEXUS a GLB.

No modifica el .blend fuente. Pensado para ejecutarse en headless:
  /opt/blender/blender --background nexus/nivel_01/NEXUS_L1_V05.blend \
      --python blender_concept/export_reception_glb.py

Criterio:
- objetos visibles (MESH/FONT/LIGHT/EMPTY) cuya caja mundial intersecta
  el volumen de recepción y áreas inmediatas;
- se excluyen las piezas ocultas y las colecciones históricas;
- se incluyen padres y descendientes para no romper jerarquías;
- se exportan extras, luces y animaciones.
"""
import bpy
import json
import os
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
OUT = os.path.join(ROOT, "assets/models/fm/reception_nexus.glb")
REPORT = os.path.join(ROOT, "nexus/nivel_01/reception_export_selection.json")

BOUNDS = {
    "min": Vector((-21.0, 1.0, -6.2)),
    "max": Vector((-3.0, 14.2, 0.8)),
}

EXCLUDE_PREFIXES = (
    "NEXUS_V05_SERVICE_CONN_",
    "NEXUS_LINK_L1_",
    "NEXUS_V05_CORR_END_SIGN_",
)

# Objetos que deben viajar aunque su centro quede fuera del volumen.
FORCE_NAMES = (
    "NEXUS_V05_RECEPCION_FLOOR",
    "NEXUS_V05_RECEPCION_WALL_N",
    "NEXUS_V05_RECEPCION_WALL_S",
    "NEXUS_V05_RECEPCION_WALL_E",
    "NEXUS_V05_RECEPCION_WALL_W",
    "NEXUS_V05_CORR_FLOOR",
    "NEXUS_V05_CORR_CEILING",
    "NEXUS_V05_REC_EXTRACT_ZONE",
    "NEXUS_V05_REC_EXTRACT_CAB_TRIGGER",
    "NEXUS_V05_REC_EXTRACT_RECEPTION_TRIGGER",
    "NEXUS_V05_ELEVATOR_SEQUENCE",
)

FORCE_COLLECTIONS = (
    "NEXUS_V05_ELEVATOR",
    "NEXUS_V05_REC_PLAY",
    "NEXUS_V05_REC_PASS126",
    "NEXUS_V05_REC_LOD1",
)

KEY_PREFIXES = (
    "NEXUS_V05_REC_",
    "NEXUS_V05_C_REC_ELEV_",
    "NEXUS_V05_C_REC_",
    "NEXUS_V05_RECEPCION_",
    "NEXUS_ASSET_L1_REC_",
    "NEXUS_L1_DIS_BREAK_",
    "NEXUS_L1_DIS_CHAIR_REC_",
    "NEXUS_L1_DIS_MONITOR_REC",
    "NEXUS_L1_DIS_BIN_REC",
)


def world_bounds(ob):
    if not ob.bound_box:
        c = ob.matrix_world.translation
        return c, c
    pts = [ob.matrix_world @ Vector(v) for v in ob.bound_box]
    return (
        Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
        Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))),
    )


def intersects_reception(ob):
    lo, hi = world_bounds(ob)
    return (
        hi.x >= BOUNDS["min"].x and lo.x <= BOUNDS["max"].x
        and hi.y >= BOUNDS["min"].y and lo.y <= BOUNDS["max"].y
        and hi.z >= BOUNDS["min"].z and lo.z <= BOUNDS["max"].z
    )


def is_excluded(ob):
    if ob.hide_render:
        return True
    if any(ob.name.startswith(p) for p in EXCLUDE_PREFIXES):
        return True
    for coll in ob.users_collection:
        if coll.name.endswith("_HIST") or "HISTOR" in coll.name.upper():
            return True
    return False


def add_with_family(selected, ob):
    selected.add(ob)
    # Padres: conservan la transformación y los extras de jerarquía.
    p = ob.parent
    while p is not None:
        selected.add(p)
        p = p.parent
    # Descendientes de empties/roots seleccionados (loot, triggers, etc.).
    if ob.type == "EMPTY":
        stack = list(ob.children)
        while stack:
            child = stack.pop()
            selected.add(child)
            stack.extend(child.children)


scene = bpy.context.scene
selected = set()

# Colecciones completas de gameplay y arquitectura de la recepción.
for coll_name in FORCE_COLLECTIONS:
    coll = bpy.data.collections.get(coll_name)
    if coll:
        for ob in coll.all_objects:
            if not is_excluded(ob):
                add_with_family(selected, ob)

for ob in scene.objects:
    if ob.type not in {"MESH", "FONT", "LIGHT", "EMPTY"}:
        continue
    if is_excluded(ob):
        continue
    name_hit = ob.name in FORCE_NAMES or any(ob.name.startswith(p) for p in KEY_PREFIXES)
    if name_hit or intersects_reception(ob):
        add_with_family(selected, ob)

# Nunca exportar históricos ni cámaras.
selected = {
    ob for ob in selected
    if ob.type != "CAMERA" and not is_excluded(ob)
}

# Orden estable y selección en la vista.
bpy.ops.object.select_all(action="DESELECT")
for ob in sorted(selected, key=lambda o: o.name):
    ob.select_set(True)
if selected:
    bpy.context.view_layer.objects.active = sorted(selected, key=lambda o: o.name)[0]

counts = {}
for ob in selected:
    counts[ob.type] = counts.get(ob.type, 0) + 1
tris = 0
for ob in selected:
    if ob.type == "MESH":
        me = ob.data
        me.calc_loop_triangles()
        tris += len(me.loop_triangles)

keys = {
    "loot": [o.name for o in selected if o.name.startswith("NEXUS_V05_REC_LOOT_")],
    "extraction": [o.name for o in selected if o.name.startswith("NEXUS_V05_REC_EXTRACT")],
    "elevator_doors": [o.name for o in selected if o.name in {"NEXUS_V05_C_REC_ELEV_L", "NEXUS_V05_C_REC_ELEV_R"}],
    "lights": [o.name for o in selected if o.type == "LIGHT"],
    "has_shared_clock": any("REC_CLOCK" in o.name for o in selected),
}
report = {
    "file": bpy.data.filepath,
    "bounds": {k: list(v) for k, v in BOUNDS.items()},
    "selected": len(selected),
    "by_type": counts,
    "triangles": tris,
    "key": keys,
    "output": OUT,
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(REPORT, "w", encoding="utf-8") as fh:
    json.dump(report, fh, indent=2, ensure_ascii=False)

print("EXPORT_REPORT", json.dumps(report, ensure_ascii=False))
print("HAS_LOOT", len(keys["loot"]), keys["loot"])
print("HAS_EXTRACTION", len(keys["extraction"]), keys["extraction"])
print("HAS_ELEVATOR_DOORS", keys["elevator_doors"])
print("HAS_CLOCK", keys["has_shared_clock"])

bpy.ops.export_scene.gltf(
    filepath=OUT,
    export_format="GLB",
    use_selection=True,
    export_cameras=False,
    export_lights=True,
    export_animations=True,
    export_current_frame=False,
    export_extras=True,
    export_yup=True,
    export_apply=True,
    export_image_format="WEBP",
    export_image_quality=70,
)

print("WROTE", OUT, os.path.getsize(OUT) if os.path.exists(OUT) else -1)
