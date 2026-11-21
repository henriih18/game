"""FRECUENCIA MUERTA - Level 1 V06 blockout rooms export (headless only).

Exports the nine blockout rooms that are still missing from `level1_v06`,
one GLB per room, from the current V06 master:

    control       Zone04  Control de acceso         -105..-77 x  40..60
    lockers       Zone05  Vestuarios                 30..60  x  40..64
    warehouse     Zone06  Almacen / suministros      70..110 x   8..38
    maintenance   Zone07  Mantenimiento             56..112 x -48..-8
    offices       Zone08  Oficinas / administracion -30..15  x  30..70
    restroom      Zone09  Aseo                       18..30  x  42..58
    stairs_main   Zone11  Escaleras principales     -12..8   x -50..-30
    stairs_e1     Zone12a Escalera de emergencia E1 110..120 x   8..26
    stairs_e2     Zone12b Escalera de emergencia E2 112..122 x -44..-26

Each room keeps its own root (`FM_L1_BLOCKOUT_<ROOM>`), original mesh names,
original collections and original blockout materials.  The script selects by
explicit name prefix, never by whole collection, so no prop from another room
can leak in.  It also validates that the room set is disjoint and that every
mesh stays inside the room + connector envelope.

The blockout rooms have no props in V06: only shell, columns, door frames,
floors, ceilings and (for some rooms) the complete circulation connector.
That limitation is reported per room; no geometry is invented.

Blocked element (reported, not exported):
  SM_L1_Conn_ChangingConnector_* (Vestuarios access corridor) only has a
  ceiling and its west wall.  Its floor and central wall at x=46 are hero
  Z10 kit meshes (`L1_KIT_PILOT`), and the blockout ceiling/wall would
  overlap the already exported `z10_conector.glb`.  Exporting it would
  duplicate/z-fight hero art, so the element is left out and reported.

Shared boundaries are deliberately not duplicated between GLBs (same rule as
`security_access_sector`):
  - restroom east side  -> `blockout_lockers` (Zone05 west wall)
  - stairs_e1 west side -> `blockout_warehouse` (Zone06 east wall + door)
  - stairs_e2 west side -> `blockout_maintenance` (Zone07 east wall + door)

Run (never saves the .blend):
  /opt/blender/blender -b nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend \
      --python-exit-code 1 \
      --python scripts/fm/fm_blockout_rooms_export_headless.py
"""
import bpy
import json
import os
import struct
from mathutils import Vector

ROOT = "/home/riyo/Documentos/game"
OUT_DIR = os.path.join(ROOT, "assets/models/fm")
REPORT_DIR = os.path.join(ROOT, "docs")

ALLOWED_COLLECTIONS = {
    "L1_ARCH_ZONES",
    "L1_ARCH_COLUMNS",
    "L1_ARCH_CORES",
    "L1_ARCH_CIRCULATION",
    "L1_ARCH_ALTERNATE",
    "L1_ARCH_CEILINGS",
}

# Never exported, even if a future prefix match would catch one.
EXCLUDE_TOKENS = (
    "LOD1", "LOD2", "_LOD",
    "RETIRED", "LIB_", "STUDIO", "ANNOT_",
    "P0_TEST", "PLAYER", "VAL_", "LAB_",
    "FM_LIBRARY", "L1_SHARED_HERO", "HIDEOUT_",
    "LIGHT_", "CAM_", "P0_",
)

# Room selection: prefixes are matched with str.startswith on mesh objects.
# `boxes` are (min, max) Blender envelopes used for stray validation; they
# include the room shell (0.35 m pad) and each connector.
ROOMS = (
    {
        "id": "control",
        "file": "blockout_control.glb",
        "root": "FM_L1_BLOCKOUT_CONTROL",
        "title_es": "Control de acceso",
        "function_es": (
            "Puesto de control y filtro de acceso entre Seguridad, el "
            "corredor norte y la escalera de emergencia 12C. Punto de "
            "estrangulamiento con columnas y dos vanos de puerta."
        ),
        "prefixes": (
            "SM_L1_Zone04_AccessControl_",
            "SM_L1_Column_AccessControl_",
            "SM_L1_Conn_AccessConnector_",
        ),
        "boxes": (
            ((-105.35, 39.65, -0.30), (-76.65, 60.35, 6.10)),
            ((-96.35, 35.65, -0.30), (-91.65, 40.35, 4.30)),
        ),
        "expected": 26,
        "shared_boundaries": (),
        "blocked": (),
    },
    {
        "id": "lockers",
        "file": "blockout_lockers.glb",
        "root": "FM_L1_BLOCKOUT_LOCKERS",
        "title_es": "Vestuarios",
        "function_es": (
            "Vestuario del personal de recuperacion: taquillas, cambio de "
            "equipo y acceso de servicio desde el corredor. Sala de 30 x 24 m "
            "con cuatro columnas y tres vanos."
        ),
        "prefixes": (
            "SM_L1_Zone05_Changing_",
            "SM_L1_Column_Changing_",
        ),
        "boxes": (
            ((29.65, 39.65, -0.30), (60.35, 64.35, 4.60)),
        ),
        "expected": 25,
        "shared_boundaries": (
            "El lado este de Aseo comparte el muro oeste de Vestuarios "
            "(SM_L1_Zone05_Changing_Wall_W_*); se exporta solo aqui.",
        ),
        "blocked": (
            {
                "objects": (
                    "SM_L1_Conn_ChangingConnector_Ceiling",
                    "SM_L1_Conn_ChangingConnector_Wall_W_0",
                ),
                "reason_es": (
                    "Pasillo corredor-Vestuarios incompleto: solo existen "
                    "techo y muro oeste. No hay suelo ni muro este blockout; "
                    "el suelo y el muro central x=46 son kit hero de Z10 "
                    "(L1_KIT_PILOT) ya exportado en z10_conector.glb. "
                    "Exportarlo duplicaria techo/muro sobre arte hero."
                ),
            },
        ),
    },
    {
        "id": "warehouse",
        "file": "blockout_warehouse.glb",
        "root": "FM_L1_BLOCKOUT_WAREHOUSE",
        "title_es": "Almacen / suministros",
        "function_es": (
            "Almacen de suministros y zona de carga: 40 x 30 m, 6 m de altura, "
            "tres vanos (corredor, servicio y escalera E1), 12 columnas y "
            "conexion al conector de servicio."
        ),
        "prefixes": (
            "SM_L1_Zone06_Warehouse_",
            "SM_L1_Column_Warehouse_",
            "SM_L1_Conn_WarehouseConnector_",
            "SM_L1_Conn_ServiceLink_",
        ),
        "boxes": (
            ((69.65, 7.65, -0.30), (110.35, 38.35, 6.10)),
            ((69.65, 3.65, -0.30), (74.35, 8.35, 4.30)),
            ((61.65, 17.65, -0.30), (70.35, 24.35, 4.30)),
        ),
        "expected": 44,
        "shared_boundaries": (
            "El muro este del Almacen (con su puerta a E1) queda aqui; "
            "blockout_stairs_e1 depende de este GLB para su lado oeste.",
        ),
        "blocked": (),
    },
    {
        "id": "maintenance",
        "file": "blockout_maintenance.glb",
        "root": "FM_L1_BLOCKOUT_MAINTENANCE",
        "title_es": "Mantenimiento / infraestructura",
        "function_es": (
            "Sala tecnica de infraestructura: 56 x 40 m, 6 m de altura, "
            "15 columnas y vanos al corredor y a la escalera de emergencia E2."
        ),
        "prefixes": (
            "SM_L1_Zone07_Maintenance_",
            "SM_L1_Column_Maintenance_",
            "SM_L1_Conn_MaintenanceConnector_",
        ),
        "boxes": (
            ((55.65, -48.35, -0.30), (112.35, -7.65, 6.10)),
            ((59.65, -8.35, -0.30), (66.35, -3.65, 4.30)),
        ),
        "expected": 39,
        "shared_boundaries": (
            "El muro este de Mantenimiento (con su puerta a E2) queda aqui; "
            "blockout_stairs_e2 depende de este GLB para su lado oeste.",
        ),
        "blocked": (),
    },
    {
        "id": "offices",
        "file": "blockout_offices.glb",
        "root": "FM_L1_BLOCKOUT_OFFICES",
        "title_es": "Oficinas / administracion",
        "function_es": (
            "Area administrativa: 45 x 40 m, 4,5 m de altura, seis columnas, "
            "acceso norte-sur desde el corredor y puerta este al enlace de Aseo."
        ),
        "prefixes": (
            "SM_L1_Zone08_Offices_",
            "SM_L1_Column_Offices_",
            "SM_L1_Conn_OfficesConnector_",
        ),
        "boxes": (
            ((-30.35, 29.65, -0.30), (15.35, 70.35, 4.60)),
            ((-14.35, 3.65, -0.30), (-5.65, 30.35, 4.30)),
        ),
        "expected": 30,
        "shared_boundaries": (),
        "blocked": (),
    },
    {
        "id": "restroom",
        "file": "blockout_restroom.glb",
        "root": "FM_L1_BLOCKOUT_RESTROOM",
        "title_es": "Aseo",
        "function_es": (
            "Aseo de planta de 12 x 16 m y 4 m de altura, accesible desde el "
            "enlace con Oficinas. Sala pequena y claustrofobica."
        ),
        "prefixes": (
            "SM_L1_Zone09_Aseo_",
            "SM_L1_Conn_AseoLink_",
        ),
        "boxes": (
            ((17.65, 41.65, -0.30), (30.35, 58.35, 4.10)),
            ((14.65, 45.65, -0.30), (18.35, 52.35, 4.10)),
        ),
        "expected": 14,
        "shared_boundaries": (
            "El lado este de Aseo es el muro oeste de Vestuarios "
            "(SM_L1_Zone05_Changing_Wall_W_*), incluido en blockout_lockers.",
        ),
        "blocked": (),
    },
    {
        "id": "stairs_main",
        "file": "blockout_stairs_main.glb",
        "root": "FM_L1_BLOCKOUT_STAIRS_MAIN",
        "title_es": "Escaleras principales",
        "function_es": (
            "Nucleo vertical principal de 20 x 20 m y 7 m de altura: 24 "
            "peldaños que descienden 4,5 m hasta la meseta del Nivel 2, con "
            "foso, cuatro franjas de suelo y pasillo de acceso al corredor."
        ),
        "prefixes": (
            "SM_L1_Stair_Main_",
            "SM_L1_Zone11_MainStairs_",
            "SM_L1_Conn_StairsConnector_",
        ),
        "boxes": (
            ((-12.35, -50.35, -5.00), (8.35, -29.65, 7.10)),
            ((-4.35, -30.35, -0.30), (2.35, -3.65, 4.30)),
        ),
        "expected": 50,
        "shared_boundaries": (),
        "blocked": (),
    },
    {
        "id": "stairs_e1",
        "file": "blockout_stairs_e1.glb",
        "root": "FM_L1_BLOCKOUT_STAIRS_E1",
        "title_es": "Escalera de emergencia E1",
        "function_es": (
            "Salida de emergencia E1 de 10 x 18 m y 6 m de altura: 24 "
            "peldaños que descienden 4,5 m al Nivel 2. Se accede desde el "
            "muro este del Almacen."
        ),
        "prefixes": (
            "SM_L1_Stair_E1_",
            "SM_L1_Zone12a_EmergencyStairsE1_",
        ),
        "boxes": (
            ((109.65, 7.65, -5.20), (120.35, 26.35, 6.10)),
        ),
        "expected": 34,
        "shared_boundaries": (
            "El lado oeste de E1 es el muro este del Almacen "
            "(SM_L1_Zone06_Warehouse_Wall_E_* y su puerta), incluido en "
            "blockout_warehouse.",
        ),
        "blocked": (),
    },
    {
        "id": "stairs_e2",
        "file": "blockout_stairs_e2.glb",
        "root": "FM_L1_BLOCKOUT_STAIRS_E2",
        "title_es": "Escalera de emergencia E2",
        "function_es": (
            "Salida de emergencia E2 de 10 x 18 m y 6 m de altura: 24 "
            "peldaños que descienden 4,5 m al Nivel 2. Se accede desde el "
            "muro este de Mantenimiento."
        ),
        "prefixes": (
            "SM_L1_Stair_E2_",
            "SM_L1_Zone12b_EmergencyStairsE2_",
        ),
        "boxes": (
            ((111.65, -44.35, -5.20), (122.35, -25.65, 6.10)),
        ),
        "expected": 34,
        "shared_boundaries": (
            "El lado oeste de E2 es el muro este de Mantenimiento "
            "(SM_L1_Zone07_Maintenance_Wall_E_* y su puerta), incluido en "
            "blockout_maintenance.",
        ),
        "blocked": (),
    },
)


# ------------------------------------------------------------------ helpers
def world_aabb(ob):
    corners = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    mn = Vector((min(p.x for p in corners),
                 min(p.y for p in corners),
                 min(p.z for p in corners)))
    mx = Vector((max(p.x for p in corners),
                 max(p.y for p in corners),
                 max(p.z for p in corners)))
    return mn, mx


def mesh_tris(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def excluded(name):
    return any(token in name for token in EXCLUDE_TOKENS)


def collection_names(ob):
    return {c.name for c in ob.users_collection}


def inside_boxes(ob, boxes, tol=0.01):
    mn, mx = world_aabb(ob)
    for bmin, bmax in boxes:
        bmin = Vector(bmin)
        bmax = Vector(bmax)
        if (mn.x >= bmin.x - tol and mn.y >= bmin.y - tol and
                mn.z >= bmin.z - tol and mx.x <= bmax.x + tol and
                mx.y <= bmax.y + tol and mx.z <= bmax.z + tol):
            return True
    return False


def unhide_master():
    """Unhide collections that are hidden in the master (ceilings).

    Hidden collections are not evaluated and their objects report identity
    matrices, so they must be made visible before measuring transforms.
    Only the in-memory session is touched; the .blend is never saved.
    """
    saved = []
    for col in bpy.data.collections:
        if col.name not in ALLOWED_COLLECTIONS:
            continue
        if col.hide_viewport or col.hide_render:
            saved.append((col, col.hide_viewport, col.hide_render))
            col.hide_viewport = False
            col.hide_render = False

    def walk(lc):
        if lc.collection.name in ALLOWED_COLLECTIONS and lc.exclude:
            saved.append((lc, lc.exclude))
            lc.exclude = False
        for child in lc.children:
            walk(child)

    walk(bpy.context.view_layer.layer_collection)
    bpy.context.view_layer.update()
    return saved


def restore_master(saved):
    for entry in reversed(saved):
        if len(entry) == 3:
            col, hv, hr = entry
            col.hide_viewport, col.hide_render = hv, hr
        else:
            lc, exclude = entry
            lc.exclude = exclude
    bpy.context.view_layer.update()


def collect_room(room):
    prefixes = tuple(room["prefixes"])
    selected = {}
    rejected = []
    for ob in bpy.data.objects:
        if ob.type != "MESH":
            continue
        if not ob.name.startswith(prefixes):
            continue
        if excluded(ob.name):
            rejected.append(ob.name)
            continue
        selected[ob.name] = ob
    return selected, rejected


def validate_room(room, selected, rejected):
    if rejected:
        raise RuntimeError(
            "{}: excluded objects matched the prefix: {}".format(
                room["id"], ", ".join(sorted(rejected))))
    if len(selected) != room["expected"]:
        raise RuntimeError(
            "{}: {} meshes, expected {} (master changed; review the room "
            "definition before exporting). names={}".format(
                room["id"], len(selected), room["expected"],
                sorted(selected)))
    for name, ob in selected.items():
        cols = collection_names(ob)
        if not cols or not cols.issubset(ALLOWED_COLLECTIONS):
            raise RuntimeError(
                "{}: {} comes from a forbidden collection {}".format(
                    room["id"], name, sorted(cols)))
        if not inside_boxes(ob, room["boxes"]):
            mn, mx = world_aabb(ob)
            raise RuntimeError(
                "{}: {} outside the room envelope: min={} max={}".format(
                    room["id"], name,
                    [round(v, 3) for v in mn],
                    [round(v, 3) for v in mx]))
    # Shell completeness: floor, ceiling and at least three wall pieces.
    names = sorted(selected)
    has_floor = any("Floor" in n for n in names)
    has_ceiling = any("Ceiling" in n for n in names)
    wall_count = sum(1 for n in names if "_Wall_" in n)
    if not has_floor or not has_ceiling or wall_count < 3:
        raise RuntimeError(
            "{}: incomplete shell floor={} ceiling={} walls={}".format(
                room["id"], has_floor, has_ceiling, wall_count))
    return {
        "floor": has_floor,
        "ceiling": has_ceiling,
        "wall_pieces": wall_count,
        "door_pieces": sum(1 for n in names if "_Door_" in n),
    }


# ---------------------------------------------------------------- GLB check
def mat4_identity():
    return [1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0]


def mat4_mul(a, b):
    out = [0.0] * 16
    for c in range(4):
        for r in range(4):
            out[c * 4 + r] = sum(a[k * 4 + r] * b[c * 4 + k] for k in range(4))
    return out


def mat4_from_trs(t, r, s):
    x, y, z, w = r
    xx, yy, zz = x * x, y * y, z * z
    xy, xz, yz = x * y, x * z, y * z
    wx, wy, wz = w * x, w * y, w * z
    return [
        (1 - 2 * (yy + zz)) * s[0], (2 * (xy + wz)) * s[0], (2 * (xz - wy)) * s[0], 0.0,
        (2 * (xy - wz)) * s[1], (1 - 2 * (xx + zz)) * s[1], (2 * (yz + wx)) * s[1], 0.0,
        (2 * (xz + wy)) * s[2], (2 * (yz - wx)) * s[2], (1 - 2 * (xx + yy)) * s[2], 0.0,
        t[0], t[1], t[2], 1.0,
    ]


def node_matrix(node):
    if "matrix" in node:
        return list(node["matrix"])
    return mat4_from_trs(
        node.get("translation", [0.0, 0.0, 0.0]),
        node.get("rotation", [0.0, 0.0, 0.0, 1.0]),
        node.get("scale", [1.0, 1.0, 1.0]),
    )


def transform_point(m, p):
    return (
        m[0] * p[0] + m[4] * p[1] + m[8] * p[2] + m[12],
        m[1] * p[0] + m[5] * p[1] + m[9] * p[2] + m[13],
        m[2] * p[0] + m[6] * p[1] + m[10] * p[2] + m[14],
    )


def read_glb(path):
    with open(path, "rb") as f:
        data = f.read()
    magic, version, length = struct.unpack_from("<III", data, 0)
    if magic != 0x46546C67:
        raise RuntimeError("not a GLB: " + path)
    offset = 12
    doc = None
    while offset < length:
        chunk_len, chunk_type = struct.unpack_from("<II", data, offset)
        offset += 8
        chunk = data[offset:offset + chunk_len]
        offset += chunk_len
        if chunk_type == 0x4E4F534A:
            doc = json.loads(chunk.decode("utf-8"))
    if doc is None:
        raise RuntimeError("GLB without JSON chunk: " + path)
    return doc, len(data)


def inspect_glb(path, expected_root):
    doc, size = read_glb(path)
    accessors = doc.get("accessors", [])
    meshes = doc.get("meshes", [])
    nodes = doc.get("nodes", [])

    tris = 0
    for mesh in meshes:
        for prim in mesh.get("primitives", []):
            if prim.get("mode", 4) != 4:
                continue
            if "indices" in prim:
                tris += accessors[prim["indices"]]["count"] // 3
            else:
                tris += accessors[prim["attributes"]["POSITION"]]["count"] // 3

    mn = [1e9, 1e9, 1e9]
    mx = [-1e9, -1e9, -1e9]
    mesh_nodes = 0
    roots = []
    for scene in doc.get("scenes", []):
        roots.extend(scene.get("nodes", []))
    if not roots:
        roots = list(range(len(nodes)))
    stack = [(i, mat4_identity()) for i in roots]
    while stack:
        index, parent = stack.pop()
        node = nodes[index]
        world = mat4_mul(parent, node_matrix(node))
        if "mesh" in node:
            mesh_nodes += 1
            for prim in meshes[node["mesh"]].get("primitives", []):
                acc = accessors[prim["attributes"]["POSITION"]]
                lo, hi = acc.get("min"), acc.get("max")
                if lo is None or hi is None:
                    continue
                for xs in (lo[0], hi[0]):
                    for ys in (lo[1], hi[1]):
                        for zs in (lo[2], hi[2]):
                            p = transform_point(world, (xs, ys, zs))
                            for i in range(3):
                                mn[i] = min(mn[i], p[i])
                                mx[i] = max(mx[i], p[i])
        for child in node.get("children", []):
            stack.append((child, world))

    lights = 0
    if "KHR_lights_punctual" in doc.get("extensions", {}):
        lights = len(doc["extensions"]["KHR_lights_punctual"].get("lights", []))
    cameras = len(doc.get("cameras", []))
    node_names = [n.get("name", "") for n in nodes]
    root_names = [nodes[i].get("name", "") for i in roots]
    forbidden = [n for n in node_names
                 if any(t.lower() in n.lower() for t in EXCLUDE_TOKENS)]
    return {
        "bytes": size,
        "meshes": len(meshes),
        "mesh_nodes": mesh_nodes,
        "nodes": len(nodes),
        "scenes": len(doc.get("scenes", [])),
        "scene_index": doc.get("scene"),
        "materials": len(doc.get("materials", [])),
        "images": len(doc.get("images", [])),
        "tris": tris,
        "cameras": cameras,
        "lights": lights,
        "animations": len(doc.get("animations", [])),
        "skins": len(doc.get("skins", [])),
        "root_nodes": root_names,
        "root_node_ok": expected_root in root_names,
        "aabb_gltf_min": [round(v, 4) for v in mn],
        "aabb_gltf_max": [round(v, 4) for v in mx],
        # GLB is Y-up and Godot keeps Y-up: no extra axis conversion.
        "aabb_godot_position": [round(v, 4) for v in mn],
        "aabb_godot_size": [round(mx[i] - mn[i], 4) for i in range(3)],
        "forbidden_nodes": forbidden,
    }


# --------------------------------------------------------------------- main
def export_room(room, selected):
    view_layer = bpy.context.view_layer

    # Flatten existing parents so no studio/player hierarchy is pulled in.
    saved_parents = {}
    for ob in selected.values():
        saved_parents[ob.name] = (ob.parent, ob.matrix_world.copy())
        if ob.parent is not None:
            world = ob.matrix_world.copy()
            ob.parent = None
            ob.matrix_world = world
    view_layer.update()

    saved_hide = {}
    bpy.ops.object.select_all(action="DESELECT")
    for ob in selected.values():
        saved_hide[ob.name] = (ob.hide_render, ob.hide_viewport, ob.hide_get())
        ob.hide_render = False
        ob.hide_viewport = False
        ob.hide_set(False)
        ob.select_set(True)
    view_layer.objects.active = selected[sorted(selected)[0]]
    view_layer.update()

    # Bake object scale into mesh data (in memory only).  Multi-user meshes
    # are copied first so another room/session object is never touched.
    for ob in selected.values():
        if ob.data.users > 1:
            ob.data = ob.data.copy()
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    view_layer.update()

    root = bpy.data.objects.new(room["root"], None)
    bpy.context.scene.collection.objects.link(root)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.5
    root["fm_room_id"] = room["id"]
    root["fm_room_title_es"] = room["title_es"]
    root["fm_room_function_es"] = room["function_es"]
    root["fm_blockout"] = 1
    root["fm_source"] = os.path.basename(bpy.data.filepath)
    for name, ob in selected.items():
        world = ob.matrix_world.copy()
        ob.parent = root
        ob.matrix_world = world
    view_layer.update()

    bpy.ops.object.select_all(action="DESELECT")
    root.select_set(True)
    for ob in selected.values():
        ob.select_set(True)
    view_layer.objects.active = root

    path = os.path.join(OUT_DIR, room["file"])
    os.makedirs(OUT_DIR, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=path,
        export_format="GLB",
        use_selection=True,
        use_active_scene=True,
        use_visible=False,
        export_apply=True,
        export_cameras=False,
        export_lights=False,
        export_animations=False,
        export_extras=True,
        export_yup=True,
    )

    # Restore in-memory state for the next room (the file is never saved).
    bpy.ops.object.select_all(action="DESELECT")
    for name, ob in selected.items():
        parent, world = saved_parents[name]
        ob.parent = parent
        if parent is not None:
            ob.matrix_world = world
    for name, (hr, hv, hs) in saved_hide.items():
        ob = bpy.data.objects.get(name)
        if ob is not None:
            ob.hide_render, ob.hide_viewport = hr, hv
            ob.hide_set(hs)
    if root.name in bpy.data.objects:
        bpy.data.objects.remove(root, do_unlink=True)
    view_layer.update()
    return path


def room_report(room, selected, shell, glb):
    tris = 0
    materials = set()
    images = set()
    points = []
    collections = set()
    for name, ob in selected.items():
        tris += mesh_tris(ob)
        materials.update(m.name for m in ob.data.materials if m is not None)
        collections.update(c.name for c in ob.users_collection)
        if ob.data.materials:
            for mat in ob.data.materials:
                if mat is None or not mat.use_nodes:
                    continue
                for node in mat.node_tree.nodes:
                    if node.type == "TEX_IMAGE" and node.image is not None:
                        images.add(node.image.name)
        mn, mx = world_aabb(ob)
        points.extend([mn, mx])

    mn = [min(p[i] for p in points) for i in range(3)]
    mx = [max(p[i] for p in points) for i in range(3)]
    return {
        "room_id": room["id"],
        "title_es": room["title_es"],
        "function_es": room["function_es"],
        "glb_path": glb["glb_path"],
        "blend": bpy.data.filepath,
        "prefixes": list(room["prefixes"]),
        "collections": sorted(collections),
        "objects": len(selected),
        "unique_meshes": len({ob.data.name for ob in selected.values()}),
        "tris_blender": tris,
        "materials": len(materials),
        "material_names": sorted(materials),
        "images": len(images),
        "image_names": sorted(images),
        "shell": shell,
        "aabb_blender": [[round(v, 4) for v in mn],
                         [round(v, 4) for v in mx]],
        # Blender (x,y,z) -> Godot (x,z,-y).
        "aabb_godot_position": [round(mn[0], 4), round(mn[2], 4),
                                round(-mx[1], 4)],
        "aabb_godot_size": [round(mx[0] - mn[0], 4),
                            round(mx[2] - mn[2], 4),
                            round(mx[1] - mn[1], 4)],
        "names": sorted(selected),
        "strays": [n for n, ob in selected.items()
                   if not inside_boxes(ob, room["boxes"])],
        "shared_boundaries": list(room["shared_boundaries"]),
        "blocked_elements": list(room["blocked"]),
        "glb": glb,
    }


def main():
    saved_visibility = unhide_master()
    try:
        rooms = {}
        owner = {}
        for room in ROOMS:
            selected, rejected = collect_room(room)
            shell = validate_room(room, selected, rejected)
            for name in selected:
                if name in owner:
                    raise RuntimeError(
                        "{} is claimed by both {} and {}".format(
                            name, owner[name], room["id"]))
                owner[name] = room["id"]
            rooms[room["id"]] = (room, selected, shell)

        summaries = []
        reports = []
        for room in ROOMS:
            _, selected, shell = rooms[room["id"]]
            path = export_room(room, selected)
            glb = inspect_glb(path, room["root"])
            glb["glb_path"] = path
            report = room_report(room, selected, shell, glb)

            if report["strays"]:
                raise RuntimeError(
                    "{}: stray meshes {}".format(room["id"], report["strays"]))
            if glb["cameras"] or glb["lights"]:
                raise RuntimeError(
                    "{}: GLB contains cameras/lights".format(room["id"]))
            if glb["forbidden_nodes"]:
                raise RuntimeError(
                    "{}: forbidden nodes {}".format(
                        room["id"], glb["forbidden_nodes"]))
            if not glb["root_node_ok"]:
                raise RuntimeError(
                    "{}: root node {} missing, got {}".format(
                        room["id"], room["root"], glb["root_nodes"]))
            if glb["scenes"] != 1 or glb["scene_index"] != 0:
                raise RuntimeError(
                    "{}: expected one glTF scene, got {} (default {})".format(
                        room["id"], glb["scenes"], glb["scene_index"]))
            if glb["meshes"] != report["objects"]:
                raise RuntimeError(
                    "{}: GLB meshes {} != source objects {}".format(
                        room["id"], glb["meshes"], report["objects"]))
            if glb["tris"] != report["tris_blender"]:
                raise RuntimeError(
                    "{}: GLB tris {} != source tris {}".format(
                        room["id"], glb["tris"], report["tris_blender"]))

            report_path = os.path.join(
                REPORT_DIR, "fm_blockout_{}_export.json".format(room["id"]))
            os.makedirs(REPORT_DIR, exist_ok=True)
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            reports.append(report)

            summary = {
                "room": room["id"],
                "file": room["file"],
                "objects": report["objects"],
                "tris": report["tris_blender"],
                "materials": report["materials"],
                "bytes": glb["bytes"],
                "aabb_godot_position": report["aabb_godot_position"],
                "aabb_godot_size": report["aabb_godot_size"],
                "strays": report["strays"],
                "cameras": glb["cameras"],
                "lights": glb["lights"],
                "forbidden_nodes": glb["forbidden_nodes"],
                "root_node_ok": glb["root_node_ok"],
            }
            summaries.append(summary)
            print("BLOCKOUT_ROOM_EXPORT " + json.dumps(
                summary, separators=(",", ":")))

        aggregate = {
            "blend": bpy.data.filepath,
            "script": os.path.abspath(__file__),
            "rooms": summaries,
            "totals": {
                "rooms": len(summaries),
                "objects": sum(s["objects"] for s in summaries),
                "tris": sum(s["tris"] for s in summaries),
                "bytes": sum(s["bytes"] for s in summaries),
                "strays": sum(len(s["strays"]) for s in summaries),
                "cameras": sum(s["cameras"] for s in summaries),
                "lights": sum(s["lights"] for s in summaries),
            },
            "room_reports": [
                "docs/fm_blockout_{}_export.json".format(r["room_id"])
                for r in reports
            ],
            "blockers": [
                {"room": r["room_id"], "blocked_elements": r["blocked_elements"]}
                for r in reports if r["blocked_elements"]
            ],
            "limitations_es": [
                "Las salas siguen en blockout: no tienen props, UVs de "
                "produccion ni arte hero; solo cascara, columnas, puertas, "
                "suelo, techo y conectores completos.",
                "El pasillo corredor-Vestuarios no se exporta: su suelo y "
                "muro central son kit hero de Z10 y el blockout solo aporta "
                "techo y muro oeste.",
                "Los muros compartidos se exportan una sola vez para evitar "
                "z-fighting: Aseo depende de Vestuarios; E1 de Almacen; E2 "
                "de Mantenimiento.",
                "La escalera de emergencia 12C y la galeria tecnica Este no "
                "forman parte de esta tarea.",
            ],
        }
        aggregate_path = os.path.join(
            REPORT_DIR, "fm_blockout_rooms_export.json")
        with open(aggregate_path, "w", encoding="utf-8") as f:
            json.dump(aggregate, f, indent=2, ensure_ascii=False)
        print("BLOCKOUT_ROOMS_TOTAL " + json.dumps(
            aggregate["totals"], separators=(",", ":")))
        print("BLOCKOUT_ROOMS_REPORT " + aggregate_path)
    finally:
        restore_master(saved_visibility)


main()
