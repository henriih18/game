"""Assemble L1_SECURITY_R21C_HERO and hide the superseded R21B pieces.

Run from Blender MCP:
    import fm_r21c_build as BUILD; BUILD.build_all()
The old R21B objects are hidden (never deleted); the R21C collection is
rebuilt from scratch on each run.
"""
import bpy

import fm_r21c_lib as C
import fm_r21c_lockers as LK
import fm_r21c_hatch as HT
import fm_r21c_storage as ST
import fm_r21c_cart as CT
import fm_r21c_chaos as CH

SUPERSEDED = (
    "R21B_LOCK_BankA",
    "R21B_LOCK_BankB",
    "R21B_LOCK_KeyCabinet",
    "R21B_LOCK_Shelving",
    "R21B_HATCH_ServiceCounter",
    "R21B_HATCH_Shutter",
    "R21B_HATCH_Sign",
    "R21B_HATCH_GlassShards",
    "R21B_CHAOS_ToolCart",
)


def hide_superseded():
    for name in SUPERSEDED:
        ob = bpy.data.objects.get(name)
        if ob is not None:
            ob.hide_viewport = True
            ob.hide_render = True


def unhide_superseded():
    for name in SUPERSEDED:
        ob = bpy.data.objects.get(name)
        if ob is not None:
            ob.hide_viewport = False
            ob.hide_render = False


def _bbox(ob):
    from mathutils import Vector
    pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return mn, mx


def _dist_to_box(p, box):
    mn, mx = box
    dx = max(mn.x - p.x, 0.0, p.x - mx.x)
    dy = max(mn.y - p.y, 0.0, p.y - mx.y)
    dz = max(mn.z - p.z, 0.0, p.z - mx.z)
    return (dx * dx + dy * dy + dz * dz) ** 0.5


def merge_details(coll, parents):
    """Join loose screws / sockets / bolts into their nearest assembly.

    The builders intentionally emit many tiny detail objects; if a caller
    did not append one to its parts list it would remain a loose object.
    This keeps every delivered assembly a single clean object.
    """
    parents = [p for p in parents if p is not None and p.name in bpy.data.objects]
    if not parents:
        return
    boxes = {p.name: _bbox(p) for p in parents}
    parent_names = {p.name for p in parents}
    groups = {p.name: [] for p in parents}
    for ob in list(coll.objects):
        if ob.type != "MESH" or ob.name in parent_names:
            continue
        mn, mx = _bbox(ob)
        c = (mn + mx) * 0.5
        best = min(parents, key=lambda p: _dist_to_box(c, boxes[p.name]))
        groups[best.name].append(ob)
    for p in parents:
        group = [o for o in groups[p.name] if o.name in bpy.data.objects]
        if not group:
            continue
        bpy.ops.object.select_all(action="DESELECT")
        p.select_set(True)
        for o in group:
            o.select_set(True)
        bpy.context.view_layer.objects.active = p
        bpy.ops.object.join()
    print("  merged detail objects into", len(parents), "assemblies")


def build_all():
    import importlib
    for mod in (C, LK, HT, ST, CT, CH):
        importlib.reload(mod)
    C.clean_root()
    mat = C.palette()
    out = {}
    c = C.sub("LOCKERS")
    out["lockers"] = LK.build(mat, c)
    c = C.sub("HATCH")
    out["hatch"] = HT.build(mat, c)
    c = C.sub("STORAGE")
    out["storage"] = ST.build(mat, c)
    c = C.sub("CART")
    out["cart"] = [CT.build(mat, c)]
    c = C.sub("CHAOS")
    out["chaos"] = CH.build(mat, c)
    LK.place_banks(out["lockers"])
    hide_superseded()
    print("R21C_BUILD_OK")
    for key, objs in out.items():
        tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons)
                   for o in objs if o.type == "MESH")
        print(f"  {key}: {len(objs)} objects, {tris} tris")
    return out
