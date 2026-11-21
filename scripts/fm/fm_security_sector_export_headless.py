"""FRECUENCIA MUERTA - Security 03 sector export (headless only).

Builds `assets/models/fm/security_sector.glb` from the current V06 blend.
Like the reception sector exporter, this DELETES every object that is not
selected, so it must run in a separate headless Blender process. It never
saves the .blend.

Run:
  /opt/blender/blender -b nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend \
      --python scripts/fm/fm_security_sector_export_headless.py
"""
import bpy
import json
import os
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
GLB = os.path.join(ROOT, "assets/models/fm/security_sector.glb")
REPORT = os.path.join(ROOT, "docs/fm_security_sector_export.json")

COLLECTIONS = (
    "L1_SECURITY_P0A_HERO",
    "L1_SECURITY_R2_HERO",
    "L1_SECURITY_R1",
    "L1_SECURITY_R21A_HERO",
    "L1_SECURITY_R21B_HERO",
    "L1_SECURITY_R21C_HERO",
    "L1_SECURITY_R21D_HERO",
    "L1_P0B6_SHELL",
    "L1_ARCH_CEILINGS",
    "L1_ARCH_COLUMNS",
    "L1_ARCH_CIRCULATION",
    "L1_ARCH_ZONES",
)

REGION_MIN = Vector((-110.2, 9.8, -1.0))
REGION_MAX = Vector((-69.8, 36.2, 5.6))

# La cinta de la barrera de cola cruza el vano sur de Seguridad a 0,90 m y
# deja huecos laterales de 0,56 m: bloquea el paso del jugador y del agente
# de navegación. Se exporta la barrera retraída (se omiten cinta, hebilla,
# palanca y clip; los postes y las carcasas se conservan), de modo que el
# acceso vuelve a ser transitable sin inventar geometría nueva.
EXCLUDE_NAMES = {
    "PROP_HERO_SEC_Barrier_Belt",
    "PROP_HERO_SEC_Barrier_Buckle",
    "PROP_HERO_SEC_Barrier_BuckleLever",
    "PROP_HERO_SEC_Barrier_EndClip",
}


def in_region(ob):
    mw = ob.matrix_world
    c = Vector((0.0, 0.0, 0.0))
    for corner in ob.bound_box:
        c += mw @ Vector(corner)
    c /= 8.0
    return (REGION_MIN.x <= c.x <= REGION_MAX.x and
            REGION_MIN.y <= c.y <= REGION_MAX.y and
            REGION_MIN.z <= c.z <= REGION_MAX.z)


def downscale_images(meshes, max_size=1024):
    """Reduce en memoria las texturas compartidas antes de empaquetar el GLB.

    El máster comparte sets 2K con Z10 y otras salas; sin este paso el GLB de
    Seguridad duplica texturas que el juego ya tiene y crece de 32 a 70 MB.
    Solo afecta a esta sesión headless: el .blend no se guarda.
    """
    images = set()
    for ob in meshes:
        for slot in ob.material_slots:
            mat = slot.material
            if mat is None or not mat.use_nodes:
                continue
            for node in mat.node_tree.nodes:
                if node.type == "TEX_IMAGE" and node.image is not None:
                    images.add(node.image)
    resized = []
    for img in images:
        w, h = img.size
        if max(w, h) <= max_size:
            continue
        scale = max_size / float(max(w, h))
        nw, nh = max(1, int(round(w * scale))), max(1, int(round(h * scale)))
        img.scale(nw, nh)
        resized.append((img.name, w, h, nw, nh))
    print("SECURITY_SECTOR_IMAGES_RESIZED", len(resized))
    for item in resized:
        print("  IMG", item)
    return resized


def main():
    selected = {}
    for cname in COLLECTIONS:
        col = bpy.data.collections.get(cname)
        if col is None:
            print("SECURITY_EXPORT_MISSING_COLLECTION", cname)
            continue
        for ob in col.all_objects:
            if ob.type != "MESH":
                continue
            if ob.name in EXCLUDE_NAMES:
                continue
            if ob.hide_render and ob.hide_viewport:
                continue
            if ob.name in selected:
                continue
            if in_region(ob):
                selected[ob.name] = ob

    keep = set(selected.keys())
    for ob in list(bpy.data.objects):
        if ob.name not in keep:
            bpy.data.objects.remove(ob, do_unlink=True)

    view_layer = bpy.context.view_layer
    for ob in selected.values():
        mw = ob.matrix_world.copy()
        ob.parent = None
        ob.matrix_world = mw
        ob.hide_render = False
        ob.hide_viewport = False
        ob.hide_set(False)
        ob.select_set(True)
    view_layer.objects.active = selected[next(iter(selected))]
    view_layer.update()

    downscale_images(list(selected.values()), max_size=1024)

    bpy.ops.export_scene.gltf(
        filepath=GLB,
        export_format='GLB',
        use_selection=False,
        export_apply=True,
        export_cameras=False,
        export_lights=False,
        export_extras=True,
    )

    tris = 0
    unique = set()
    names = sorted(selected.keys())
    mins = [1e9, 1e9, 1e9]
    maxs = [-1e9, -1e9, -1e9]
    for ob in selected.values():
        tris += sum(len(p.vertices) - 2 for p in ob.data.polygons)
        unique.add(ob.data.name)
        mw = ob.matrix_world
        for corner in ob.bound_box:
            p = mw @ Vector(corner)
            for i in range(3):
                mins[i] = min(mins[i], p[i])
                maxs[i] = max(maxs[i], p[i])

    bad_tokens = ("STUDIO", "VAL_", "PLAYER", "PROP_Z10",
                  "Zone01_Reception", "Zone06_Warehouse",
                  "LIB_", "RETIRED")
    strays = [n for n in names if any(t in n for t in bad_tokens)]

    report = {
        "objects": len(selected),
        "unique_meshes": len(unique),
        "tris": tris,
        "names": names,
        "aabb": [[round(v, 4) for v in mins],
                 [round(v, 4) for v in maxs]],
        "bytes": os.path.getsize(GLB) if os.path.exists(GLB) else 0,
        "strays": strays,
        "collections": list(COLLECTIONS),
        "region": [[round(v, 2) for v in REGION_MIN],
                   [round(v, 2) for v in REGION_MAX]],
    }
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    summary = {k: report[k] for k in
               ("objects", "unique_meshes", "tris", "aabb", "bytes", "strays")}
    print("SECURITY_SECTOR_EXPORT " + json.dumps(summary, separators=(",", ":")))


main()
