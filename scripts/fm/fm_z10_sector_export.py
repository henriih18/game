"""Export the complete Z10 room + Service Link to a clean GLB."""

import bpy
import json
import os
from mathutils import Vector

OUT = "/home/riyo/Documentos/game"
GLB = OUT + "/assets/models/fm/z10_sector.glb"
REPORT = OUT + "/docs/fm_z10_sector_export.json"
TMP = "P0_EXPORT_TMP"

INCLUDE_COLLECTIONS = {
    "L1_KIT_PILOT",
    "L1_PROPS_Z10",
    "L1_P0B4_Z10",
    "L1_P0B5_Z10",
    "L1_P0B5D_Z10",
    "L1_Z10_ABANDON",
    "L1_Z10_LIGHTING",
    "L1_P0B_SERVICES",
    "L1_ARCH_CIRCULATION",
    "L1_ARCH_CEILINGS",
    "L1_ARCH_ZONES",
}
EXCLUDE_COLLECTIONS = {
    "Z10_RETIRED_P0B4",
    "L1_P0B_LOD",
    "STUDIO_Z10_SET",
    "STUDIO_Z10_LOCKERS",
    "Z10_LEGACY_DUPLICATES",
    "PLAYER_BASE_Z10",
    "L1_LIGHTING_INTENT",
    "L1_ARCH_SURFACE",
    "L1_ARCH_LABELS",
}
EXCLUDE_PREFIXES = (
    "PROP_Z10_LockerDoor_01",
    "KIT_PILOT_Z10_Floor_Airlock_00",
    "KIT_PILOT_Z10_Ceiling_Airlock_01",
    "SM_L1_Conn_ChangingConnector_",
)
ONLY_NAMES = {
    "SM_L1_Conn_ServiceLink_Ceiling",
    "SM_L1_Zone06_Warehouse_Wall_W_1",
}
CIRC_ALLOW = (
    "SM_L1_Conn_ServiceLink_",
)


def in_region(ob):
    if ob.type == 'LIGHT':
        p = ob.matrix_world.translation
        return ((40.0 <= p.x <= 62.0 and 8.0 <= p.y <= 30.0) or
                (62.0 <= p.x <= 70.2 and 18.0 <= p.y <= 24.0))
    if ob.type != 'MESH':
        return False
    pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    cx = (min(p.x for p in pts) + max(p.x for p in pts)) * 0.5
    cy = (min(p.y for p in pts) + max(p.y for p in pts)) * 0.5
    if 40.0 <= cx <= 62.0 and 8.0 <= cy <= 30.0:
        return True
    if 62.0 <= cx <= 70.2 and 18.0 <= cy <= 24.0:
        return True
    return False


def allowed(ob):
    if ob.type not in {'MESH', 'LIGHT'}:
        return False
    if ob.name.startswith(EXCLUDE_PREFIXES):
        return False
    for c in ob.users_collection:
        if c.name in EXCLUDE_COLLECTIONS:
            return False
    colls = {c.name for c in ob.users_collection}
    if not (colls & INCLUDE_COLLECTIONS):
        return False
    if "L1_ARCH_CIRCULATION" in colls and not ob.name.startswith(CIRC_ALLOW):
        return False
    return True


def mesh_tris(ob):
    if ob.type != 'MESH' or not ob.data:
        return 0
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def main():
    bpy.context.view_layer.update()
    # Hidden master collections are not evaluated, so their objects report an
    # identity matrix_world.  Unhide them just for the export (and bbox report)
    # so forced-only names such as SM_L1_Conn_ServiceLink_Ceiling keep their
    # real transform instead of landing at the origin.
    hidden_colls = []
    for name in INCLUDE_COLLECTIONS:
        c = bpy.data.collections.get(name)
        if c is not None and (c.hide_viewport or c.hide_render):
            hidden_colls.append((c, c.hide_viewport, c.hide_render))
            c.hide_viewport = False
            c.hide_render = False
    if hidden_colls:
        bpy.context.view_layer.update()

    selected = [ob for ob in bpy.data.objects if allowed(ob) and
                (ob.name in ONLY_NAMES or in_region(ob))]

    # Flatten parent transforms so no studio/player hierarchy is pulled in.
    saved_parents = {}
    for ob in selected:
        if ob.parent:
            saved_parents[ob.name] = (ob.parent, ob.matrix_world.copy())
            mw = ob.matrix_world.copy()
            ob.parent = None
            ob.matrix_world = mw
    bpy.context.view_layer.update()

    view_layer = bpy.context.view_layer

    # Temporarily unlink every object in an excluded collection so the glTF
    # exporter cannot pick up studio/player/retired/legacy helpers.
    strays = []
    for ob in bpy.data.objects:
        if any(c.name in EXCLUDE_COLLECTIONS for c in ob.users_collection):
            colls = list(ob.users_collection)
            strays.append((ob, colls))
            for c in colls:
                c.objects.unlink(ob)

    bpy.ops.object.select_all(action='DESELECT')
    for ob in selected:
        ob.hide_render = False
        ob.select_set(True)
    view_layer.objects.active = selected[0] if selected else None

    bpy.ops.export_scene.gltf(
        filepath=GLB,
        export_format='GLB',
        use_selection=True,
        use_visible=False,
        use_active_collection=False,
        use_active_collection_with_nested=False,
        export_lights=True,
        export_cameras=False,
        export_animations=False,
        export_extras=True,
        export_apply=False,
        export_tangents=True,
        export_texcoords=True,
        export_normals=True,
        export_all_vertex_colors=True,
        export_image_format='AUTO',
        export_yup=True,
    )

    bpy.ops.object.select_all(action='DESELECT')
    for ob, colls in strays:
        for c in colls:
            if ob.name not in c.objects:
                c.objects.link(ob)

    for name, (parent, mw) in saved_parents.items():
        ob = bpy.data.objects.get(name)
        if ob:
            ob.parent = parent
            ob.matrix_world = mw
    bpy.context.view_layer.update()

    meshes = [ob for ob in selected if ob.type == 'MESH']
    lights = [ob for ob in selected if ob.type == 'LIGHT']
    unique = {ob.data.name for ob in meshes if ob.data}
    tris = sum(mesh_tris(ob) for ob in meshes)
    pts = []
    for ob in meshes:
        pts.extend(ob.matrix_world @ Vector(c) for c in ob.bound_box)
    if pts:
        mn = [min(p[i] for p in pts) for i in range(3)]
        mx = [max(p[i] for p in pts) for i in range(3)]
    else:
        mn = mx = [0.0, 0.0, 0.0]

    report = {
        "glb": GLB,
        "bytes": os.path.getsize(GLB) if os.path.exists(GLB) else 0,
        "collections": sorted(INCLUDE_COLLECTIONS),
        "objects": len(selected),
        "meshes": len(meshes),
        "unique_meshes": len(unique),
        "lights": len(lights),
        "tris": tris,
        "bbox_blender": [mn, mx],
        "bbox_godot_position": [mn[0], mn[2], -mx[1]],
        "bbox_godot_size": [mx[0] - mn[0], mx[2] - mn[2], mx[1] - mn[1]],
        "mesh_names": sorted(ob.name for ob in meshes),
        "light_names": sorted(ob.name for ob in lights),
        "detached_parents": {k: v[0].name for k, v in saved_parents.items()},
        "excluded_collections": sorted(EXCLUDE_COLLECTIONS),
    }
    with open(REPORT, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    for c, hv, hr in hidden_colls:
        c.hide_viewport = hv
        c.hide_render = hr
    if hidden_colls:
        bpy.context.view_layer.update()
    print("Z10_SECTOR_EXPORT", len(selected), len(meshes), len(unique),
          len(lights), tris, report["bytes"])
    print("BBOX", mn, mx)
    print("REPORT", REPORT)


main()
