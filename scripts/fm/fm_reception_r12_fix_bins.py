import bpy
from mathutils import Matrix

SCENE = bpy.data.scenes["NEXUS_L1_V06_ARCH"]
BLEND = "/home/riyo/Documentos/game/nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend"
positions = {
    "PROP_REC05_Bin_0": (-109.70, -29.20, 0.0),
    "PROP_REC05_Bin_1": (-109.70, -30.00, 0.0),
}
moved = []
for name, loc in positions.items():
    ob = bpy.data.objects.get(name)
    if ob is None:
        continue
    world = ob.matrix_world.copy()
    ob.parent = None
    ob.matrix_world = world
    ob.matrix_world = Matrix.Translation(loc) @ ob.matrix_world.to_3x3().to_4x4()
    moved.append(name)
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print("BINS_MOVED", moved)
