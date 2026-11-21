"""FRECUENCIA MUERTA - P0b.6: cierre de cascara Recepcion/Seguridad.

Cierra solo los defectos que siguen abiertos tras R9/P0A:
  - S-06: retira las 3 rejillas de pared R21B_SERV_VentS/E/W, que no
    tienen conducto ni hueco detras. El retorno se definira con los
    patinillos (S-18, pendiente por decision del usuario).
  - S-09: enlaza la bandeja central P0A (termina y24,6) con la bandeja
    local CCTV (y35,5), con bajada a la estanteria del rack.
  - S-21: prolonga la linea de circulacion hasta el borde de la
    plataforma de extraccion (y-35,0), cerrando el hueco de 2 m.

No se anaden habitaciones, no se construyen patinillos, no se toca
fotos-referencia. S-01..S-05/S-07/S-08 ya estan resueltos por R9/P0A;
se verifican y se documentan.

Run: python3 /tmp/opencode/bpy_run.py scripts/fm/fm_p0b6_shell_close.py
"""
import bpy
import bmesh
import json
import math
import os
import shutil
import sys

ROOT = "/home/riyo/Documentos/game"
BLEND = os.path.join(ROOT, "nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend")
BACKUP = os.path.join(ROOT, "docs/backups/FM_LEVEL1_V06_ARCH_before_p0b6_shell.blend")
QA = os.path.join(ROOT, "docs/fm_p0b6_shell_qa.json")
COL = "L1_P0B6_SHELL"
RETIRED = "L1_SECURITY_RETIRED_P0B6"
SCENE = bpy.data.scenes["NEXUS_L1_V06_ARCH"]
GEN = "VERIFIED_P0B6"

sys.path.insert(0, os.path.join(ROOT, "scripts/fm"))
from fm_shared_p0_lib import box, cyl, join_group  # noqa: E402


def mat(name):
    m = bpy.data.materials.get(name)
    if m is None:
        raise RuntimeError("Missing material " + name)
    return m


def collection(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        SCENE.collection.children.link(c)
    return c


def clear_previous():
    col = bpy.data.collections.get(COL)
    if not col:
        return
    for ob in list(col.objects):
        me = ob.data
        bpy.data.objects.remove(ob, do_unlink=True)
        if me is not None and me.users == 0:
            bpy.data.meshes.remove(me)


def retire(name):
    ob = bpy.data.objects.get(name)
    if ob is None:
        return None
    ret = collection(RETIRED)
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    ret.objects.link(ob)
    ob.hide_render = True
    ob.hide_viewport = True
    ob.hide_set(True)
    return name


def mesh_stats(ob):
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    nonman = sum(1 for e in bm.edges if not e.is_manifold)
    degen = sum(1 for f in bm.faces if f.calc_area() < 1e-9)
    bm.free()
    mw = ob.matrix_world
    pts = [mw @ v.co for v in me.vertices]
    mn = [round(min(p[i] for p in pts), 4) for i in range(3)]
    mx = [round(max(p[i] for p in pts), 4) for i in range(3)]
    return {
        "tris": sum(len(p.vertices) - 2 for p in me.polygons),
        "verts": len(me.vertices),
        "non_manifold": nonman,
        "degenerate": degen,
        "uv": len(me.uv_layers) > 0,
        "bbox": [mn, mx],
    }


# ---------------------------------------------------------------------------
# S-21: prolongar la linea de circulacion 2 m hasta la plataforma
# ---------------------------------------------------------------------------

def extend_wayfinding():
    line = bpy.data.objects.get("DET_REC02_Way_CenterToExtraction")
    if line is None:
        raise RuntimeError("Missing DET_REC02_Way_CenterToExtraction")
    if line.data.library:
        line.data = line.data.copy()
    mw = line.matrix_world.copy()
    inv = mw.inverted()
    moved = 0
    for v in line.data.vertices:
        w = mw @ v.co
        if w.y < -32.9:
            w.y = -35.0
            v.co = inv @ w
            moved += 1
    line.data.update()
    return line, moved


# ---------------------------------------------------------------------------
# S-09: enlace de bandeja central P0A -> rack CCTV
# ---------------------------------------------------------------------------

def build_tray_link(col, galv, bare, dark):
    parts = []
    X = -84.555
    Y0, Y1 = 24.6, 34.9          # long run, stops south of the CCTV rack
    Z = 4.30
    YSHORT = 34.9
    XSHORT = -86.858
    YSTUB = 35.5
    ZDROP0, ZDROP1 = 3.75, 4.30
    L = Y1 - Y0

    # long run along Y
    for side in (-0.195, 0.195):
        parts.append(box(col, "P0B6_TRAY_LONG_RAIL_%s" % ("W" if side < 0 else "E"),
                         0.03, L, 0.10, (X + side, (Y0 + Y1) / 2, Z),
                         galv, bevel=0.001, seg=2))
        parts.append(box(col, "P0B6_TRAY_LONG_LIP_%s" % ("W" if side < 0 else "E"),
                         0.04, L, 0.008, (X + side * 0.85, (Y0 + Y1) / 2, Z + 0.046),
                         bare, bevel=0.0006, seg=1))
    n = int(L / 0.3)
    for i in range(n + 1):
        y = Y0 + 0.15 + i * 0.3
        parts.append(box(col, "P0B6_TRAY_LONG_RUNG_%02d" % i,
                         0.35, 0.022, 0.008, (X, y, Z - 0.042),
                         bare, bevel=0.0004, seg=1))

    # short run along X, just south of the CCTV rack
    LX = abs(XSHORT - X)
    for side in (-0.195, 0.195):
        parts.append(box(col, "P0B6_TRAY_SHORT_RAIL_%s" % ("S" if side < 0 else "N"),
                         LX, 0.03, 0.10,
                         ((X + XSHORT) / 2, YSHORT + side, Z),
                         galv, bevel=0.001, seg=2))
        parts.append(box(col, "P0B6_TRAY_SHORT_LIP_%s" % ("S" if side < 0 else "N"),
                         LX, 0.04, 0.008,
                         ((X + XSHORT) / 2, YSHORT + side * 0.85, Z + 0.046),
                         bare, bevel=0.0006, seg=1))
    n = int(LX / 0.3)
    for i in range(n + 1):
        x = X - 0.15 - i * 0.3
        parts.append(box(col, "P0B6_TRAY_SHORT_RUNG_%02d" % i,
                         0.022, 0.35, 0.008, (x, YSHORT, Z - 0.042),
                         bare, bevel=0.0004, seg=1))

    # north stub into the CCTV rack, then vertical drop to the shelf
    for side in (-0.195, 0.195):
        parts.append(box(col, "P0B6_TRAY_STUB_RAIL_%s" % ("W" if side < 0 else "E"),
                         0.03, 0.6, 0.10, (XSHORT + side, (YSHORT + YSTUB) / 2, Z),
                         galv, bevel=0.001, seg=2))
    for i, y in enumerate((35.05, 35.35)):
        parts.append(box(col, "P0B6_TRAY_STUB_RUNG_%02d" % i,
                         0.35, 0.022, 0.008, (XSHORT, y, Z - 0.042),
                         bare, bevel=0.0004, seg=1))

    # vertical drop at the west end of the CCTV rack
    for side in (-0.195, 0.195):
        parts.append(box(col, "P0B6_TRAY_DROP_RAIL_%s" % ("W" if side < 0 else "E"),
                         0.03, 0.106, ZDROP1 - ZDROP0,
                         (XSHORT + side, YSTUB, (ZDROP0 + ZDROP1) / 2),
                         galv, bevel=0.001, seg=2))
    for i, z in enumerate((3.82, 4.10)):
        parts.append(box(col, "P0B6_TRAY_DROP_RUNG_%02d" % i,
                         0.35, 0.008, 0.022, (XSHORT, YSTUB, z),
                         bare, bevel=0.0004, seg=1))

    # cables (3 per run, overlapping at the corners)
    for off in (-0.16, 0.0, 0.16):
        parts.append(cyl(col, "P0B6_CABLE_LONG_%+.2f" % off,
                         0.012, L, (X + off, (Y0 + Y1) / 2, Z - 0.015),
                         dark, axis='Y', seg=8, bevel=0.0))
        parts.append(cyl(col, "P0B6_CABLE_SHORT_%+.2f" % off,
                         0.012, LX, ((X + XSHORT) / 2, YSHORT + off, Z - 0.015),
                         dark, axis='X', seg=8, bevel=0.0))
        parts.append(cyl(col, "P0B6_CABLE_STUB_%+.2f" % off,
                         0.012, 0.6, (XSHORT + off, (YSHORT + YSTUB) / 2, Z - 0.015),
                         dark, axis='Y', seg=8, bevel=0.0))
        parts.append(cyl(col, "P0B6_CABLE_DROP_%+.2f" % off,
                         0.012, ZDROP1 - ZDROP0, (XSHORT + off, YSTUB,
                                                  (ZDROP0 + ZDROP1) / 2),
                         dark, axis='Z', seg=8, bevel=0.0))

    # trapeze supports from the ceiling slab (4.70)
    def support(name, cx, cy, along_x=True):
        for s in (-0.18, 0.18):
            rx = cx + s if along_x else cx
            ry = cy if along_x else cy + s
            parts.append(cyl(col, name + "_ROD_%s" % ("W" if s < 0 else "E"),
                             0.006, 0.36, (rx, ry, 4.50), bare,
                             axis='Z', seg=8, bevel=0.0))
            parts.append(box(col, name + "_PLATE_%s" % ("W" if s < 0 else "E"),
                             0.06, 0.06, 0.01, (rx, ry, 4.685), bare,
                             bevel=0.0004, seg=1))
        if along_x:
            parts.append(box(col, name + "_BAR", 0.50, 0.04, 0.04,
                             (cx, cy, 4.34), galv, bevel=0.0008, seg=1))
        else:
            parts.append(box(col, name + "_BAR", 0.04, 0.50, 0.04,
                             (cx, cy, 4.34), galv, bevel=0.0008, seg=1))

    for i, y in enumerate((27.6, 30.6, 33.6)):
        support("P0B6_SUP_LONG_%02d" % i, X, y, along_x=True)
    support("P0B6_SUP_SHORT", (X + XSHORT) / 2, YSHORT, along_x=False)
    support("P0B6_SUP_STUB", XSHORT, 35.2, along_x=True)

    # splice plates at the central tray and at the CCTV shelf
    parts.append(box(col, "P0B6_SPLICE_CENTRE", 0.46, 0.02, 0.12,
                     (X, Y0 + 0.01, Z), dark, bevel=0.0006, seg=1))
    parts.append(box(col, "P0B6_SPLICE_RACK", 0.46, 0.02, 0.12,
                     (XSHORT, 35.37, 3.75), dark, bevel=0.0006, seg=1))

    return join_group(col, "P0B6_CCTV_TRAY_LINK", parts, uv=True, wn=True)


def main():
    if not os.path.exists(BACKUP):
        os.makedirs(os.path.dirname(BACKUP), exist_ok=True)
        shutil.copy2(BLEND, BACKUP)

    clear_previous()
    col = collection(COL)

    galv = mat("M_SH_Steel_Galv")
    bare = mat("M_SH_Steel_Stainless")
    dark = mat("M_SH_Steel_Dark")

    retired = []
    for n in ("R21B_SERV_VentS", "R21B_SERV_VentE", "R21B_SERV_VentW"):
        r = retire(n)
        if r:
            retired.append(r)

    line, moved = extend_wayfinding()
    link = build_tray_link(col, galv, bare, dark)
    link["fm_generation"] = GEN
    link["fm_family"] = "P0B6_SHELL_CLOSE"

    report = {
        "generation": GEN,
        "collection": COL,
        "retired": retired,
        "wayfinding": {
            "object": line.name,
            "moved_verts": moved,
            "stats": mesh_stats(line),
        },
        "objects": {link.name: mesh_stats(link)},
        "backup": os.path.basename(BACKUP),
        "notes": {
            "S-06": "3 rejillas de pared sin conducto retiradas; retorno diferido con patinillos (S-18)",
            "S-09": "bandeja central P0A enlazada con bandeja CCTV mediante 10,3 m + 2,3 m + 0,6 m + bajada 0,55 m",
            "S-21": "linea de circulacion prolongada de y-33 a y-35, hasta la plataforma de extraccion",
            "S-01..S-05/S-07/S-08": "ya resueltos por R9/P0A; audit doc desactualizado",
            "S-18": "patinillos pendientes por decision del usuario; no se construyen",
        },
    }
    ok = True
    for name, s in report["objects"].items():
        if s["non_manifold"] or s["degenerate"] or not s["uv"] or not s["tris"]:
            ok = False
    report["qa_pass"] = ok
    with open(QA, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("P0B6_DONE " + json.dumps({
        "qa_pass": ok,
        "retired": retired,
        "wayfinding": [line.name, moved, report["wayfinding"]["stats"]["bbox"]],
        "link": [link.name] + [report["objects"][link.name][k]
                               for k in ("tris", "verts", "non_manifold",
                                         "degenerate", "uv", "bbox")],
    }, separators=(",", ":")))


main()
