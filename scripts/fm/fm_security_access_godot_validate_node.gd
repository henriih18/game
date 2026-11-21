extends Node3D

# Validates assets/models/fm/security_access_sector.glb in Godot:
#  - 11 shell meshes, no lights/cameras/strays
#  - AABB matches the Blender source mapped to Godot axes
#  - the sector reaches both the Security east wall and the main corridor

const GLB := "res://assets/models/fm/security_access_sector.glb"
const EXPECTED_MESHES := 11
const EXPECTED_UNIQUE := 11
const EXPECTED_POS := Vector3(-71.0, -0.2, -11.8)
const EXPECTED_SIZE := Vector3(34.4, 2.6, 7.8)
const TOL := 0.02
# Overlap/reach checks: Security east wall, corridor north-wall opening.
const SECURITY_EDGE_X := -70.85
const CORRIDOR_OPENING_X := -36.8
const CORRIDOR_EDGE_Z := -4.0
const FORBIDDEN := ["STUDIO", "PROP_Z10", "VAL_", "PLAYER", "Zone01_Reception",
	"Zone06_Warehouse", "LIB_", "RETIRED", "LOD1", "LOD2", "ANNOT_",
	"P0_TEST", "FM_LIBRARY", "L1_SHARED_HERO", "DOORS", "LAB_"]

const EXPECTED_NAMES := [
	"SM_L1_Alt_SecurityCorridor_Ceiling_H",
	"SM_L1_Alt_SecurityCorridor_Ceiling_V",
	"SM_L1_Alt_SecurityCorridor_Floor_H",
	"SM_L1_Alt_SecurityCorridor_Floor_V",
	"SM_L1_Alt_SecurityCorridor_Wall_E",
	"SM_L1_Alt_SecurityCorridor_Wall_N_0",
	"SM_L1_Alt_SecurityCorridor_Wall_N_1",
	"SM_L1_Alt_SecurityCorridor_Wall_N_2",
	"SM_L1_Alt_SecurityCorridor_Wall_N_V",
	"SM_L1_Alt_SecurityCorridor_Wall_S",
	"SM_L1_Alt_SecurityCorridor_Wall_W",
]


func _ready() -> void:
	var packed: PackedScene = load(GLB)
	if packed == null:
		push_error("SECURITY_ACCESS missing GLB: " + GLB)
		get_tree().quit(1)
		return
	var root := packed.instantiate()
	add_child(root)
	await get_tree().process_frame

	var meshes := 0
	var unique := {}
	var found: Array[String] = []
	var strays: Array[String] = []
	for n in root.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		meshes += 1
		found.append(mi.name)
		if mi.mesh != null:
			unique[mi.mesh.get_instance_id()] = true
		for token in FORBIDDEN:
			if mi.name.to_upper().contains(token.to_upper()):
				strays.append(mi.name)
				break
	for n in root.find_children("*", "Light3D", true, false):
		push_error("SECURITY_ACCESS unexpected light: " + n.name)
		strays.append(n.name)
	for n in root.find_children("*", "Camera3D", true, false):
		push_error("SECURITY_ACCESS unexpected camera: " + n.name)
		strays.append(n.name)

	found.sort()
	var expected: Array[String] = []
	expected.assign(EXPECTED_NAMES)
	expected.sort()
	var missing: Array[String] = []
	for name in expected:
		if not found.has(name):
			missing.append(name)

	var ok := true
	# Floor top must sit on the shared sector datum Y=0 (no vertical step).
	# Ceiling underside must be at 2.2 m, matching the 1.4 x 2.2 m openings.
	for floor_name in ["SM_L1_Alt_SecurityCorridor_Floor_H", "SM_L1_Alt_SecurityCorridor_Floor_V"]:
		var floor_node := root.find_child(floor_name, true, false) as MeshInstance3D
		if floor_node == null or floor_node.mesh == null:
			push_error("SECURITY_ACCESS missing floor: " + floor_name)
			ok = false
			continue
		var floor_box: AABB = floor_node.global_transform * floor_node.mesh.get_aabb()
		if absf(floor_box.end.y) > 0.001:
			push_error("SECURITY_ACCESS floor top Y=%f on %s" % [floor_box.end.y, floor_name])
			ok = false
	for ceil_name in ["SM_L1_Alt_SecurityCorridor_Ceiling_H", "SM_L1_Alt_SecurityCorridor_Ceiling_V"]:
		var ceil_node := root.find_child(ceil_name, true, false) as MeshInstance3D
		if ceil_node == null or ceil_node.mesh == null:
			push_error("SECURITY_ACCESS missing ceiling: " + ceil_name)
			ok = false
			continue
		var ceil_box: AABB = ceil_node.global_transform * ceil_node.mesh.get_aabb()
		if absf(ceil_box.position.y - 2.2) > 0.001:
			push_error("SECURITY_ACCESS ceiling underside Y=%f on %s" % [ceil_box.position.y, ceil_name])
			ok = false

	var aabb := _aabb_of(root)
	if meshes != EXPECTED_MESHES:
		push_error("SECURITY_ACCESS meshes=%d expected %d" % [meshes, EXPECTED_MESHES])
		ok = false
	if unique.size() != EXPECTED_UNIQUE:
		push_error("SECURITY_ACCESS unique=%d expected %d" % [unique.size(), EXPECTED_UNIQUE])
		ok = false
	if not missing.is_empty():
		push_error("SECURITY_ACCESS missing meshes: %s" % str(missing))
		ok = false
	if aabb.position.distance_to(EXPECTED_POS) > TOL:
		push_error("SECURITY_ACCESS aabb pos %s expected %s" % [aabb.position, EXPECTED_POS])
		ok = false
	if aabb.size.distance_to(EXPECTED_SIZE) > TOL:
		push_error("SECURITY_ACCESS aabb size %s expected %s" % [aabb.size, EXPECTED_SIZE])
		ok = false
	# Beware: Godot Z grows toward Blender -Y, so the Security side is min.x
	# and the main corridor is max.x / max.z.
	if aabb.position.x > SECURITY_EDGE_X:
		push_error("SECURITY_ACCESS does not reach Security edge: x=%f" % aabb.position.x)
		ok = false
	if aabb.position.x + aabb.size.x < CORRIDOR_OPENING_X:
		push_error("SECURITY_ACCESS does not reach corridor opening")
		ok = false
	if aabb.position.z + aabb.size.z < CORRIDOR_EDGE_Z - TOL:
		push_error("SECURITY_ACCESS does not reach main corridor floor edge")
		ok = false
	if not strays.is_empty():
		push_error("SECURITY_ACCESS strays: %s" % str(strays))
		ok = false

	print("SECURITY_ACCESS meshes=%d unique=%d aabb_pos=%s size=%s strays=%s missing=%s"
		% [meshes, unique.size(), aabb.position, aabb.size, strays, missing])
	if ok:
		print("SECURITY_ACCESS_GODOT_OK")
		get_tree().quit(0)
	else:
		print("SECURITY_ACCESS_GODOT_FAIL")
		get_tree().quit(1)


func _aabb_of(root: Node) -> AABB:
	var out := AABB()
	var first := true
	for n in root.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		if mi.mesh == null:
			continue
		var box := mi.global_transform * mi.mesh.get_aabb()
		if first:
			out = box
			first = false
		else:
			out = out.merge(box)
	return out
