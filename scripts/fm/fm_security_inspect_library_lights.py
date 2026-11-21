import bpy
import json

sc = bpy.data.scenes["FM_ASSET_LIBRARY"]
col = bpy.data.collections.get("LIGHTING")
if col is None:
    # Find by traversing FM_LIBRARY.
    root = bpy.data.collections.get("FM_LIBRARY")
    stack = [root] if root else []
    while stack and col is None:
        c = stack.pop()
        if c.name == "LIGHTING":
            col = c
            break
        stack.extend(c.children)

rows = []
if col:
    for ob in col.all_objects:
        if ob is None:
            continue
        rows.append({
            "name": ob.name,
            "type": ob.type,
            "parent": ob.parent.name if ob.parent else None,
            "data": ob.data.name if ob.data else None,
            "dims": [round(v, 4) for v in ob.dimensions],
            "loc": [round(v, 4) for v in ob.matrix_world.translation],
            "collections": [c.name for c in ob.users_collection],
        })
print("LIGHTING_COL", col.name if col else None, "COUNT", len(rows))
print(json.dumps(rows, indent=2))
