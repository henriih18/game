"""Build L1_SECURITY_R21A_HERO - security operations centre (Seguridad 03).

Run from Blender MCP:
    import sys; sys.path.insert(0, ".../scripts")
    import fm_ops_build; fm_ops_build.build()
"""
import bpy
import math
import importlib
import sys
from mathutils import Vector

import fm_ops_lib as L
import fm_ops_workstations as W
import fm_ops_cctv as C
import fm_ops_rack as R
import fm_ops_chaos as CH


def _drop_temp():
    for name in ("TMP_OPS_TEST", "TMP_REVIEW_OPS", "TMP_REVIEW"):
        c = bpy.data.collections.get(name)
        if c is None:
            continue
        for o in list(c.objects):
            bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.collections.remove(c)


def _light(name, kind, loc, energy, color, size=0.5, target=None, coll=None):
    d = bpy.data.lights.new(name, kind)
    d.energy = energy
    d.color = color
    if kind in {"AREA", "SPOT"}:
        d.shape = "DISK"
        d.size = size
    if kind == "POINT":
        d.shadow_soft_size = size
    o = bpy.data.objects.new(name, d)
    o.location = loc
    if target:
        v = Vector(target) - Vector(loc)
        o.rotation_euler = v.to_track_quat("-Z", "Y").to_euler()
    coll.objects.link(o)
    return o


def build():
    _drop_temp()
    L.clean_old_root()
    root = L.make_root()
    c_ws = L.sub("L1_SECURITY_R21A_WORKSTATIONS")
    c_cctv = L.sub("L1_SECURITY_R21A_CCTV")
    c_rack = L.sub("L1_SECURITY_R21A_RACK")
    c_chaos = L.sub("L1_SECURITY_R21A_CHAOS")
    c_fix = L.sub("L1_SECURITY_R21A_FIXTURES")
    c_lights = L.sub("L1_SECURITY_R21A_LIGHTS")
    mat = L.make_materials()

    desks = [
        ("R21A_WS_A", (-89.55, 30.55, 0.0),
         [(-0.46, -0.03, "screen_glow", 7), (0.46, -0.03, "screen_scan", -7)]),
        ("R21A_WS_B", (-86.30, 30.55, 0.0),
         [(-0.46, -0.03, "screen_glow_dim", 6), (0.46, -0.03, "screen_dead_ops", -6)]),
        ("R21A_WS_C", (-83.05, 30.55, 0.0),
         [(-0.46, -0.03, "screen_dead_ops", 5), (0.46, -0.03, "screen_glow_dim", -5)]),
    ]
    for prefix, origin, screens in desks:
        W.build_desk(prefix, origin, mat, c_ws, screens, with_ptz=(prefix == "R21A_WS_A"))

    W.build_chair("R21A_CHAIR_A", (-89.55, 29.38, 0), mat, c_ws, facing_deg=0)
    W.build_chair("R21A_CHAIR_B", (-86.30, 29.38, 0), mat, c_ws, facing_deg=2)
    W.build_chair("R21A_CHAIR_C_TIPPED", (-90.05, 28.28, 0), mat, c_ws,
                  facing_deg=28, tipped=True)

    C.build_cctv(mat, c_cctv)
    R.build_rack(mat, c_rack)
    R.build_wall_panel(mat, c_fix)
    R.build_column_dock(mat, c_rack)
    R.build_emergency_fixture("R21A_FIX_Emergency_N", (-80.70, 35.758, 3.860), mat, c_fix,
                              rot_z=0.0)
    R.build_emergency_fixture("R21A_FIX_Emergency_E", (-71.238, 31.20, 3.560), mat, c_fix,
                              rot_z=math.radians(-90))
    CH.build_chaos(mat, c_chaos)

    # final practical lights: sparse red emergencies + dim screen glow only
    _light("R21A_LIGHT_Emergency_N", "POINT", (-80.70, 35.60, 3.840), 3.5,
           (1.0, 0.045, 0.02), size=0.30, coll=c_lights)
    _light("R21A_LIGHT_Emergency_E", "POINT", (-71.34, 31.20, 3.540), 2.8,
           (1.0, 0.040, 0.018), size=0.28, coll=c_lights)
    # monitor glow, deliberately weak spill
    _light("R21A_LIGHT_Glow_A", "AREA", (-89.55, 29.55, 1.42), 2.2,
           (0.28, 0.72, 0.64), size=0.75, target=(-89.55, 30.55, 1.05), coll=c_lights)
    _light("R21A_LIGHT_Glow_B", "AREA", (-86.30, 29.55, 1.42), 1.7,
           (0.24, 0.62, 0.58), size=0.75, target=(-86.30, 30.55, 1.05), coll=c_lights)
    _light("R21A_LIGHT_Glow_C", "AREA", (-83.05, 29.55, 1.42), 1.1,
           (0.22, 0.55, 0.58), size=0.75, target=(-83.05, 30.55, 1.05), coll=c_lights)
    _light("R21A_LIGHT_Glow_CCTV", "AREA", (-85.40, 34.55, 2.42), 8.0,
           (0.22, 0.62, 0.58), size=2.6, target=(-85.40, 35.70, 2.42), coll=c_lights)

    # scene output settings for review (kept in the .blend)
    s = bpy.context.scene
    s.render.engine = "BLENDER_EEVEE"
    s.render.resolution_x = 1280
    s.render.resolution_y = 720
    s.render.resolution_percentage = 100
    s.render.image_settings.file_format = "PNG"
    try:
        s.eevee.taa_render_samples = 64
    except Exception:
        pass

    bpy.context.view_layer.update()
    # normalise winding of every closed island (kitbash repairs)
    flips = 0
    for ob in root.all_objects:
        if ob.type == "MESH":
            flips += L.fix_inverted_islands(ob)
    # counts
    mesh_count = 0
    tris = 0
    for ob in root.all_objects:
        if ob.type == "MESH":
            mesh_count += 1
            dg = bpy.context.evaluated_depsgraph_get()
            me = ob.evaluated_get(dg).to_mesh()
            tris += sum(len(p.vertices) - 2 for p in me.polygons)
            ob.evaluated_get(dg).to_mesh_clear()
    print(f"R21A_BUILD_OK meshes={mesh_count} tris={tris} flips={flips}")
    return root


if __name__ == "__main__":
    build()
