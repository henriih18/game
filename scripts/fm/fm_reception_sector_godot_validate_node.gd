extends Node3D

const GLB := "res://assets/models/fm/reception_sector.glb"
const EXPECTED_MESHES := 292
const EXPECTED_UNIQUE := 274
const EXPECTED_MIN := Vector3(-110.6, -0.7, 3.4)
const EXPECTED_MAX := Vector3(-69.4, 5.7, 40.4)


func _ready() -> void:
	var packed: PackedScene = load(GLB)
	var root: Node3D = packed.instantiate()
	add_child(root)
	await get_tree().process_frame

	var meshes: Array[MeshInstance3D] = []
	var unique := {}
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		meshes.append(mi)
		unique[mi.mesh.get_instance_id()] = true
		if mi.name.ends_with("-col"):
			mi.visible = false

	var aabb := _aabb_of(root)
	var ok := meshes.size() == EXPECTED_MESHES
	ok = ok and unique.size() == EXPECTED_UNIQUE
	ok = ok and aabb.position.x >= EXPECTED_MIN.x and aabb.position.y >= EXPECTED_MIN.y
	ok = ok and aabb.position.x <= EXPECTED_MAX.x and aabb.position.y <= EXPECTED_MAX.y
	ok = ok and aabb.position.z >= EXPECTED_MIN.z and aabb.position.z <= EXPECTED_MAX.z
	ok = ok and aabb.size.x > 39.5 and aabb.size.x < 41.0
	ok = ok and aabb.size.y > 5.0 and aabb.size.y < 6.2
	ok = ok and aabb.size.z > 35.0 and aabb.size.z < 37.0

	var strays: Array[String] = []
	for mi in meshes:
		for token in ["STUDIO", "PROP_Z10", "VAL_", "PLAYER", "Zone03_Security", "Zone06_Warehouse"]:
			if mi.name.contains(token):
				strays.append(mi.name)
	ok = ok and strays.is_empty()

	print("RECEPTION_SECTOR meshes=%d unique=%d aabb_pos=%s size=%s strays=%s" % [
		meshes.size(), unique.size(), aabb.position, aabb.size, strays
	])
	if ok:
		print("RECEPTION_SECTOR_GODOT_OK")
		get_tree().quit(0)
	else:
		print("RECEPTION_SECTOR_GODOT_FAIL")
		get_tree().quit(1)


func _aabb_of(node: Node) -> AABB:
	var result := AABB()
	var has := false
	var stack: Array[Node] = [node]
	while not stack.is_empty():
		var current: Node = stack.pop_back()
		if current is MeshInstance3D and (current as MeshInstance3D).mesh != null:
			var mi := current as MeshInstance3D
			var box := mi.global_transform * mi.get_aabb()
			if not has:
				result = box
				has = true
			else:
				result = result.merge(box)
		for child in current.get_children():
			stack.append(child)
	return result
