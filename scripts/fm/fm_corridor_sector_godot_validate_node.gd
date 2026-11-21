extends Node3D

## Validates the Level 1 V06 corridor sector GLB.
## Run: godot --headless --path . scenes/fm/fm_corridor_sector_validate.tscn

const GLB := "res://assets/models/fm/corridor_sector.glb"
const EXPECTED_MESHES := 60
const EXPECTED_UNIQUE := 60
const EXPECTED_MIN := Vector3(-100.15, -0.2, -4.19)
const EXPECTED_MAX := Vector3(74.15, 4.2, 4.19)
const EXPECTED_SIZE := Vector3(174.3, 4.4, 8.3798)
const TOL := 0.15
const SECTOR_MIN := Vector3(-100.4, -0.4, -4.4)
const SECTOR_MAX := Vector3(74.4, 4.4, 4.4)
const FORBIDDEN := [
	"STUDIO", "PROP_Z10", "VAL_", "PLAYER", "Zone01_Reception",
	"Zone03_Security", "Zone06_Warehouse", "LIB_", "RETIRED",
	"LOD1", "LOD2", "ANNOT_", "P0_TEST", "SERVICEVESTIBULE",
]


func _ready() -> void:
	var packed := load(GLB) as PackedScene
	if packed == null:
		push_error("CORRIDOR_SECTOR missing GLB: " + GLB)
		get_tree().quit(1)
		return
	var root := packed.instantiate()
	add_child(root)
	await get_tree().process_frame

	var meshes := 0
	var unique := {}
	var strays: Array[String] = []
	for n in root.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		meshes += 1
		if mi.mesh != null:
			unique[mi.mesh.get_instance_id()] = true
		for token in FORBIDDEN:
			if mi.name.to_upper().contains(token.to_upper()):
				strays.append(mi.name)
				break
		if mi.mesh != null:
			var center := (mi.global_transform * mi.mesh.get_aabb()).get_center()
			if center.x < SECTOR_MIN.x or center.x > SECTOR_MAX.x \
					or center.y < SECTOR_MIN.y or center.y > SECTOR_MAX.y \
					or center.z < SECTOR_MIN.z or center.z > SECTOR_MAX.z:
				strays.append("%s@%s" % [mi.name, center])

	var lights := root.find_children("*", "Light3D", true, false).size()
	var cameras := root.find_children("*", "Camera3D", true, false).size()
	var aabb := _aabb_of(root)
	var ok := true
	if meshes != EXPECTED_MESHES:
		push_error("CORRIDOR_SECTOR meshes=%d expected %d" % [meshes, EXPECTED_MESHES])
		ok = false
	if unique.size() != EXPECTED_UNIQUE:
		push_error("CORRIDOR_SECTOR unique=%d expected %d" % [unique.size(), EXPECTED_UNIQUE])
		ok = false
	if lights != 0 or cameras != 0:
		push_error("CORRIDOR_SECTOR lights=%d cameras=%d expected 0" % [lights, cameras])
		ok = false
	if not strays.is_empty():
		push_error("CORRIDOR_SECTOR strays: %s" % str(strays))
		ok = false
	if aabb.position.x < EXPECTED_MIN.x - TOL or aabb.position.y < EXPECTED_MIN.y - TOL or aabb.position.z < EXPECTED_MIN.z - TOL:
		push_error("CORRIDOR_SECTOR aabb min out of range: %s" % aabb.position)
		ok = false
	if aabb.end.x > EXPECTED_MAX.x + TOL or aabb.end.y > EXPECTED_MAX.y + TOL or aabb.end.z > EXPECTED_MAX.z + TOL:
		push_error("CORRIDOR_SECTOR aabb max out of range: %s" % aabb.end)
		ok = false
	if absf(aabb.size.x - EXPECTED_SIZE.x) > TOL or absf(aabb.size.y - EXPECTED_SIZE.y) > TOL or absf(aabb.size.z - EXPECTED_SIZE.z) > TOL:
		push_error("CORRIDOR_SECTOR size out of range: %s expected %s" % [aabb.size, EXPECTED_SIZE])
		ok = false

	print("CORRIDOR_SECTOR meshes=%d unique=%d lights=%d cameras=%d aabb_pos=%s size=%s strays=%s" % [
		meshes, unique.size(), lights, cameras, aabb.position, aabb.size, strays
	])
	if ok:
		print("CORRIDOR_SECTOR_GODOT_OK")
		get_tree().quit(0)
	else:
		print("CORRIDOR_SECTOR_GODOT_FAIL")
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
