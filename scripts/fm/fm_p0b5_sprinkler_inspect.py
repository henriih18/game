import bpy
import bmesh
import json
from mathutils import Vector

OUT = "/home/riyo/Documentos/game/docs/fm_p0b5_sprinkler_inspect.json"
NAMES = ("PROP_Z10_SprinklerBranches", "PROP_Z10_SprinklerFeeds")


def components(ob):
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    seen = set()
    comps = []
    for f in bm.faces:
        if f.index in seen:
            continue
        stack = [f]
        seen.add(f.index)
        faces = []
        while stack:
            cur = stack.pop()
            faces.append(cur)
            for e in cur.edges:
                for nf in e.link_faces:
                    if nf.index not in seen:
                        seen.add(nf.index)
                        stack.append(nf)
        pts = []
        for face in faces:
            for v in face.verts:
                pts.append(ob.matrix_world @ v.co)
        mn = [min(p[i] for p in pts) for i in range(3)]
        mx = [max(p[i] for p in pts) for i in range(3)]
        mats = sorted({me.materials[face.material_index].name
                       for face in faces
                       if face.material_index < len(me.materials)})
        comps.append({
            "tris": sum(len(face.verts) - 2 for face in faces),
            "verts": len({v.index for face in faces for v in face.verts}),
            "bbox": [[round(v, 4) for v in mn], [round(v, 4) for v in mx]],
            "dims": [round(mx[i] - mn[i], 4) for i in range(3)],
            "center": [round((mn[i] + mx[i]) * 0.5, 4) for i in range(3)],
            "materials": mats,
        })
    bm.free()
    return sorted(comps, key=lambda c: -c["tris"])


def main():
    result = {}
    for name in NAMES:
        ob = bpy.data.objects.get(name)
        if not ob:
            print("MISSING", name)
            continue
        ob.data.calc_loop_triangles()
        comps = components(ob)
        result[name] = {
            "matrix_world": [list(row) for row in ob.matrix_world],
            "tris_total": len(ob.data.loop_triangles),
            "components": comps,
        }
        print("OBJECT", name, "comps", len(comps), "tris", len(ob.data.loop_triangles))
        for i, c in enumerate(comps[:18]):
            print("  C%02d" % i, "tris", c["tris"], "dims", c["dims"],
                  "center", c["center"], "mats", c["materials"])
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print("WROTE", OUT)


main()
