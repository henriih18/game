extends Node3D

const GLB := "res://assets/models/fm/security_sector.glb"
const EXPECTED_MESHES := 530
const EXPECTED_UNIQUE := 517
const EXPECTED_MIN := Vector3(-105.8, -1.5, -36.8)
const EXPECTED_MAX := Vector3(-70.5, 5.2, -9.4)
const EXPECTED_SIZE := Vector3(34.3, 6.1187, 26.54)
const SIZE_TOL := Vector3(0.8, 0.5, 0.8)
const FORBIDDEN := ["STUDIO", "PROP_Z10", "VAL_", "PLAYER", "Zone01_Reception", "Zone06_Warehouse", "LIB_", "RETIRED"]


func _ready() -> void:
	var packed: PackedScene = load(GLB)
	if packed == null:
		push_error("SECURITY_SECTOR missing GLB: " + GLB)
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
		if mi.name.ends_with("-col"):
			mi.visible = false
		for token in FORBIDDEN:
			if mi.name.to_upper().contains(token.to_upper()):
				strays.append(mi.name)
				break

	var aabb := _aabb_of(root)
	var ok := true
	if meshes != EXPECTED_MESHES:
		push_error("SECURITY_SECTOR meshes=%d expected %d" % [meshes, EXPECTED_MESHES])
		ok = false
	if unique.size() != EXPECTED_UNIQUE:
		push_error("SECURITY_SECTOR unique=%d expected %d" % [unique.size(), EXPECTED_UNIQUE])
		ok = false
	if aabb.position.x < EXPECTED_MIN.x or aabb.position.y < EXPECTED_MIN.y or aabb.position.z < EXPECTED_MIN.z:
		push_error("SECURITY_SECTOR aabb min out of range: %s" % aabb.position)
		ok = false
	if aabb.position.x > EXPECTED_MAX.x or aabb.position.y > EXPECTED_MAX.y or aabb.position.z > EXPECTED_MAX.z:
		push_error("SECURITY_SECTOR aabb pos out of range: %s" % aabb.position)
		ok = false
	if absf(aabb.size.x - EXPECTED_SIZE.x) > SIZE_TOL.x or absf(aabb.size.y - EXPECTED_SIZE.y) > SIZE_TOL.y or absf(aabb.size.z - EXPECTED_SIZE.z) > SIZE_TOL.z:
		push_error("SECURITY_SECTOR size out of range: %s expected %s" % [aabb.size, EXPECTED_SIZE])
		ok = false
	if not strays.is_empty():
		push_error("SECURITY_SECTOR strays: %s" % str(strays))
		ok = false

	print("SECURITY_SECTOR meshes=%d unique=%d aabb_pos=%s size=%s strays=%s" % [meshes, unique.size(), aabb.position, aabb.size, strays])
	if ok:
		print("SECURITY_SECTOR_GODOT_OK")
		get_tree().quit(0)
	else:
		print("SECURITY_SECTOR_GODOT_FAIL")
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
