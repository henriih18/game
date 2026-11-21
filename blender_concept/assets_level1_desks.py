"""Segunda pasada de assets del Nivel 1: sustituir escritorios blocky de
seguridad y control por el escritorio metalico local, conservando monitores
y equipamiento. Guarda v118 sin tocar v117.
"""
import bpy

ROOT = "/home/riyo/Documentos/game"
OUT = ROOT + "/FM_NEXUS_V05_level1_v118.blend"
PREFIX = "NEXUS_ASSET_L1_"
COLL_NAME = "NEXUS_ASSET_L1"
FLOOR = -5.65
SCENE = bpy.context.scene

coll = bpy.data.collections.get(COLL_NAME)
if coll is None:
    coll = bpy.data.collections.new(COLL_NAME)
    SCENE.collection.children.link(coll)

# ---------------------------------------------------------------- cleanup
for ob in list(bpy.data.objects):
    if ob.name.startswith((PREFIX + "SEC_DESK_", PREFIX + "ACC_DESK_")):
        bpy.data.objects.remove(ob, do_unlink=True)

src = bpy.data.objects.get(PREFIX + "OFFICE_DESK_ROOT")
if src is None:
    raise RuntimeError("No se encontro el escritorio asset de oficina")

children = [o for o in bpy.data.objects if o.parent == src]

def duplicate_desk(tag, x, y):
    root = src.copy()
    root.name = PREFIX + tag + "_ROOT"
    root.data = None
    root.location = (x, y, FLOOR)
    root.rotation_euler = (0.0, 0.0, 0.0)
    root["asset_source"] = "metal_office_desk_2k"
    root["asset_license"] = "Poly Haven - verificar licencia antes de distribuir"
    root["placement"] = "V05 nivel 1"
    coll.objects.link(root)
    for i, ch in enumerate(children):
        dup = ch.copy()
        dup.data = ch.data
        dup.name = PREFIX + tag + "_PART_" + str(i)
        dup.parent = root
        dup.matrix_parent_inverse = ch.matrix_parent_inverse.copy()
        coll.objects.link(dup)
    return root

duplicate_desk("SEC_DESK_A", 2.00, 6.00)
duplicate_desk("SEC_DESK_B", 4.00, 6.00)
duplicate_desk("ACC_DESK", 13.00, 8.00)

# ---------------------------------------------------------------- seguridad
for ob in bpy.data.objects:
    if ob.name.startswith("NEXUS_V05_SEC_DESK") and "_MON_" not in ob.name:
        ob.hide_render = True
        ob.hide_viewport = True
        ob["replaced_by"] = PREFIX + "SEC_DESK_A/B"

for ob in bpy.data.objects:
    if ob.name.startswith("NEXUS_V05_SEC_DESK_MON_") and not ob.get("l1_desk_lift"):
        ob.location.z += 0.078
        ob["l1_desk_lift"] = 0.078

# ---------------------------------------------------------------- control
for ob in bpy.data.objects:
    if ob.name.startswith("NEXUS_V05_ACC_CONSOLE"):
        ob.hide_render = True
        ob.hide_viewport = True
        ob["replaced_by"] = PREFIX + "ACC_DESK_ROOT"

for ob in bpy.data.objects:
    if (ob.name.startswith("NEXUS_V05_ACC_MON_")
            or ob.name.startswith("NEXUS_V05_ACC_KEYBOARD")
            or ob.name.startswith("NEXUS_V05_C_ACC_")):
        if not ob.get("l1_desk_drop"):
            ob.location.z -= 0.012
            ob["l1_desk_drop"] = 0.012

for name, x in (("NEXUS_ASSET_L1_ACC_CHAIR_0_ROOT", 12.25),
                ("NEXUS_ASSET_L1_ACC_CHAIR_1_ROOT", 13.75)):
    ob = bpy.data.objects.get(name)
    if ob:
        ob.location.x = x

# ---------------------------------------------------------------- guardar
SCENE.camera = bpy.data.objects.get("NEXUS_V05_CAM_Corridor")
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("L1_DESKS", len([o for o in coll.objects if o.name.startswith((PREFIX + "SEC_DESK_", PREFIX + "ACC_DESK_"))]))
print("OBJECTS", len(bpy.data.objects))
print("SAVED", OUT)
