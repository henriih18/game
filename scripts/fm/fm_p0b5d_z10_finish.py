"""FRECUENCIA MUERTA - P0b.5d: Z10 S-10..S-15 closeout.

Closes the remaining Z10 services defects:
  S-11  east conduit: replace four square 12-tri spans with 24-sided
        r0.035 conduit matching the door spans; add junction boxes.
  S-14  sprinkler heads: rebuild 4 main + 8 branch heads from the corridor
        source (P0B_SPRINKLER_HEADS) so every head has its drop pipe;
        retire the P0B4 floating heads.
  S-15  risers: add six pipe extensions, sleeves, firestop wraps and
        valve tags; the pass plates already exist from P0b.4.

S-10/S-12/S-13 are already covered by P0b.4 (duct sleeves + 4 diffusers,
retired orphan sleeves, west tray sleeves/supports); no new geometry.
The west duct patinillo stays pending by user decision.

Run: python3 /tmp/opencode/bpy_run.py scripts/fm/fm_p0b5d_z10_finish.py
"""
import bpy
import bmesh
import json
import math
import os
import shutil
import sys
from mathutils import Matrix

ROOT = "/home/riyo/Documentos/game"
BLEND = os.path.join(ROOT, "nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend")
BACKUP = os.path.join(ROOT, "docs/backups/FM_LEVEL1_V06_ARCH_before_p0b5d.blend")
QA = os.path.join(ROOT, "docs/fm_p0b5d_qa.json")
COL = "L1_P0B5D_Z10"
RETIRED = "Z10_RETIRED_P0B4"
SCENE = bpy.data.scenes["NEXUS_L1_V06_ARCH"]
GEN = "VERIFIED_P0B5D"

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


def tube_z(col, name, cx, cy, z0, z1, ri, ro, material, seg=20):
    """Closed annular sleeve with UVs, manifold, crisp rims."""
    verts, faces = [], []
    for z in (z0, z1):
        for r in (ri, ro):
            for i in range(seg):
                a = 2.0 * math.pi * i / seg
                verts.append((cx + r * math.cos(a), cy + r * math.sin(a), z))
    ib, ob_, it, ot = 0, seg, 2 * seg, 3 * seg
    for i in range(seg):
        j = (i + 1) % seg
        faces.append((ob_ + i, ob_ + j, ot + j, ot + i))       # outer wall
        faces.append((ib + i, it + i, it + j, ib + j))         # inner wall
        faces.append((ib + i, ib + j, ob_ + j, ob_ + i))       # bottom ring
        faces.append((it + i, ot + i, ot + j, it + j))         # top ring
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate(verbose=False)
    me.update()
    uvl = me.uv_layers.new(name="UVMap")
    for poly in me.polygons:
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            u = math.atan2(co.y - cy, co.x - cx) / (2.0 * math.pi) + 0.5
            uvl.data[li].uv = (u * 4.0, co.z * 4.0)
    for p in me.polygons:
        p.use_smooth = abs(p.normal.z) < 0.5
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    ob.data.materials.append(material)
    return ob


# ---------------------------------------------------------------------------
# S-11  east conduit
# ---------------------------------------------------------------------------

def conduit_span(col, name, y0, y1, panel, dark, bare,
                 inset_start=0.0, inset_end=0.0):
    parts = []
    a, b = y0 + inset_start, y1 - inset_end
    mid = 0.5 * (a + b)
    parts.append(cyl(col, name + "_PIPE", 0.035, b - a,
                     (61.78, mid, 3.15), panel, axis='Y', seg=24, bevel=0.0))
    # couplings at both ends, inside the junction boxes/wall flanges
    for y, tag in ((y0 + 0.010, "A"), (y1 - 0.010, "B")):
        parts.append(cyl(col, name + "_COUP_" + tag, 0.042, 0.016,
                         (61.78, y, 3.15), panel, axis='Y', seg=24,
                         bevel=0.0008))
    return parts


def junction_box(col, name, y, panel, dark, bare):
    parts = []
    parts.append(box(col, name + "_BODY", 0.160, 0.140, 0.140,
                     (61.78, y, 3.15), panel, bevel=0.002, seg=2))
    parts.append(box(col, name + "_COVER", 0.012, 0.120, 0.120,
                     (61.699, y, 3.15), dark, bevel=0.0015, seg=2))
    for sy in (-0.045, 0.045):
        for sz in (-0.045, 0.045):
            parts.append(cyl(col, "%s_SCREW_%s_%s" % (
                name, "N" if sy > 0 else "S", "T" if sz > 0 else "B"),
                0.0045, 0.0075, (61.6905, y + sy, 3.15 + sz), bare,
                axis='X', seg=8, bevel=0.0))
    return parts


def build_conduit(col, panel, dark, bare):
    parts = []
    for i, (y0, y1, ins0, ins1) in enumerate((
            (8.0, 12.0, 0.012, 0.0), (12.0, 16.0, 0.0, 0.0),
            (24.0, 28.0, 0.0, 0.0), (28.0, 30.0, 0.0, 0.012))):
        parts += conduit_span(col, "P0B5D_CONDUIT_SPAN_%02d" % i,
                              y0, y1, panel, dark, bare,
                              inset_start=ins0, inset_end=ins1)
    # wall flanges at the two free ends
    for y, tag in ((8.008, "S"), (29.992, "N")):
        parts.append(cyl(col, "P0B5D_CONDUIT_WALLFLANGE_" + tag,
                         0.048, 0.016, (61.78, y, 3.15), panel,
                         axis='Y', seg=24, bevel=0.001))
    # junction boxes at the four section changes
    for i, y in enumerate((12.0, 16.0, 24.0, 28.0)):
        parts += junction_box(col, "P0B5D_CONDUIT_JB_%02d" % i,
                              y, panel, dark, bare)
    return join_group(col, "P0B5D_CONDUIT_EAST", parts, uv=True, wn=True)


# ---------------------------------------------------------------------------
# S-14  sprinkler heads
# ---------------------------------------------------------------------------

def head_template():
    src = bpy.data.objects.get("P0B_SPRINKLER_HEADS")
    if src is None:
        raise RuntimeError("Missing source P0B_SPRINKLER_HEADS")
    bm = bmesh.new()
    bm.from_mesh(src.data)
    keep = {v for v in bm.verts
            if -0.10 <= v.co.x <= 0.10 and -0.10 <= v.co.y <= 0.10}
    bad = [f for f in bm.faces if any(v not in keep for v in f.verts)]
    if bad:
        bmesh.ops.delete(bm, geom=bad, context='FACES')
    loose = [v for v in bm.verts if not v.link_faces]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context='VERTS')
    me = bpy.data.meshes.new("P0B5D_HEAD_TEMPLATE")
    bm.to_mesh(me)
    bm.free()
    for m in src.data.materials:
        me.materials.append(m)
    return me


def build_heads(col, bare):
    tpl = head_template()
    # 2 mm frame rods connect the body (bottom 3.195) to the deflector
    # (top 3.184); the source head ships with the deflector floating 11 mm
    # below the body, which the QA gate correctly flags.
    tmp = cyl(col, "P0B5D_ROD_TMP", 0.0025, 0.014, (0.0, 0.0, 0.0), bare,
              axis='Z', seg=8, bevel=0.0)
    rod_me = tmp.data.copy()
    orig_me = tmp.data
    bpy.data.objects.remove(tmp, do_unlink=True)
    if orig_me.users == 0:
        bpy.data.meshes.remove(orig_me)
    targets = [
        ("MAIN_43", 43.0, 17.0), ("MAIN_47", 47.0, 17.0),
        ("MAIN_51", 51.0, 17.0), ("MAIN_59", 59.0, 17.0),
        ("BR_45_10", 45.0, 10.0), ("BR_45_14", 45.0, 14.0),
        ("BR_45_24", 45.0, 24.0), ("BR_45_28", 45.0, 28.0),
        ("BR_55_10", 55.0, 10.0), ("BR_55_14", 55.0, 14.0),
        ("BR_55_24", 55.0, 24.0), ("BR_55_28", 55.0, 28.0),
    ]
    parts = []
    for tag, x, y in targets:
        me = tpl.copy()
        me.transform(Matrix.Translation((x, y, 0.0)))
        ob = bpy.data.objects.new("P0B5D_HEAD_" + tag, me)
        col.objects.link(ob)
        parts.append(ob)
        for k, dx in enumerate((-0.015, 0.015)):
            rm = rod_me.copy()
            rm.transform(Matrix.Translation((x + dx, y, 3.1895)))
            ro = bpy.data.objects.new("P0B5D_HEAD_%s_YOKE_%d" % (tag, k), rm)
            col.objects.link(ro)
            parts.append(ro)
    if rod_me.users == 0:
        bpy.data.meshes.remove(rod_me)
    return join_group(col, "P0B5D_SPRINKLER_HEADS", parts, uv=True, wn=True)


# ---------------------------------------------------------------------------
# S-15  risers
# ---------------------------------------------------------------------------

def build_risers(col, galv, fire, bare, label, blue, dark, red):
    pipe_specs = [
        (46.27, (15.8, 16.0, 16.2)),
        (55.73, (23.8, 24.0, 24.2)),
    ]
    pipe_mats = (red, galv, dark)
    sleeves = []
    for x, ys in pipe_specs:
        for i, y in enumerate(ys):
            sleeves.append(tube_z(col, "P0B5D_SLEEVE_%s_%d" % (
                "A" if x < 50 else "B", i),
                x, y, 3.965, 4.185, 0.036, 0.042, galv))
            sleeves.append(tube_z(col, "P0B5D_FIRESTOP_%s_%d" % (
                "A" if x < 50 else "B", i),
                x, y, 3.945, 4.000, 0.042, 0.0445, fire))
            sleeves.append(cyl(col, "P0B5D_RISER_EXT_%s_%d" % (
                "A" if x < 50 else "B", i),
                0.035, 0.205, (x, y, 4.0825), pipe_mats[i],
                axis='Z', seg=20, bevel=0.0006))
    sleeve_ob = join_group(col, "P0B5D_RISER_SLEEVES", sleeves,
                           uv=True, wn=True)

    tags = []
    for x, ys in pipe_specs:
        side = 1.0 if x < 50 else -1.0
        for i, y in enumerate(ys):
            tag = "P0B5D_TAG_%s_%d" % ("A" if x < 50 else "B", i)
            tags.append(box(col, tag + "_PLATE", 0.002, 0.050, 0.032,
                            (x + side * 0.075, y, 1.360), label,
                            bevel=0.0006, seg=1))
            tags.append(box(col, tag + "_BAND", 0.0020, 0.046, 0.008,
                            (x + side * 0.0785, y, 1.372), blue, bevel=0.0, seg=1))
            tags.append(cyl(col, tag + "_WIRE", 0.0015, 0.106,
                            (x + side * 0.0750, y, 1.419), dark,
                            axis='Z', seg=6, bevel=0.0))
    tag_ob = join_group(col, "P0B5D_RISER_TAGS", tags, uv=True, wn=True)
    return sleeve_ob, tag_ob


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    if not os.path.exists(BACKUP):
        os.makedirs(os.path.dirname(BACKUP), exist_ok=True)
        shutil.copy2(BLEND, BACKUP)

    clear_previous()
    col = collection(COL)

    panel = mat("M_FM_Metal_Panel")
    dark = mat("M_SH_Steel_Dark")
    bare = mat("M_SH_Steel_Stainless")
    galv = mat("M_SH_Steel_Galv")
    fire = mat("M_SH_Firestop_Red")
    label = mat("M_SH_Label_Aluminium")
    blue = mat("M_FM_Plastic_Blue")
    red = mat("M_SH_Sprinkler_Red")

    retired = []
    for n in ("KIT_PILOT_Z10_Conduit_00", "KIT_PILOT_Z10_Conduit_01",
              "KIT_PILOT_Z10_Conduit_03", "KIT_PILOT_Z10_Conduit_04",
              "P0B4_SPRINKLER_HEADS"):
        r = retire(n)
        if r:
            retired.append(r)

    conduit = build_conduit(col, panel, dark, bare)
    heads = build_heads(col, bare)
    sleeves, tags = build_risers(col, galv, fire, bare, label, blue, dark, red)

    new_objects = [conduit, heads, sleeves, tags]
    for ob in new_objects:
        ob["fm_generation"] = GEN
        ob["fm_family"] = "Z10_SERVICES_CLOSEOUT"

    report = {
        "generation": GEN,
        "collection": COL,
        "retired": retired,
        "objects": {ob.name: mesh_stats(ob) for ob in new_objects},
        "backup": os.path.basename(BACKUP),
        "notes": {
            "S-10": "closed by P0b.4 (HVAC wall sleeves + 4 diffusers); west patinillo pending user decision",
            "S-11": "four square spans replaced by 24-sided r0.035 conduit + 4 junction boxes",
            "S-12": "orphan sleeves already retired in P0b.4",
            "S-13": "west tray sleeves y8/y30 and supports already in P0b.4",
            "S-14": "4 main + 8 branch complete heads from P0B_SPRINKLER_HEADS; old floating P0B4 heads retired",
            "S-15": "6 pipe extensions + sleeves + firestop wraps + valve tags; pass plates existed",
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
    print("P0B5D_DONE " + json.dumps({
        "qa_pass": ok,
        "retired": retired,
        "objects": {k: [v["tris"], v["verts"], v["non_manifold"],
                        v["degenerate"], v["uv"], v["bbox"]]
                    for k, v in report["objects"].items()},
    }, separators=(",", ":")))


main()
