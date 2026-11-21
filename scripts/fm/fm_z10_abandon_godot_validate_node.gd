extends Node3D

const GLB := "res://assets/models/fm/z10_abandon.glb"
const EXPECTED_MESHES := 37
const EXPECTED_UNIQUE := 34
const EXPECTED_LIGHTS := 7
const EXPECTED_AABB_POS := Vector3(40.093, 0.0, -29.624)
const EXPECTED_AABB_SIZE := Vector3(21.810, 4.080, 20.432)


func _ready() -> void:
	var packed := load(GLB) as PackedScene
	if packed == null:
		_fail("cannot load %s" % GLB)
		return
	var root := packed.instantiate()
	add_child(root)
	await get_tree().process_frame

	var meshes := root.find_children("*", "MeshInstance3D", true, false)
	if root is MeshInstance3D:
		meshes.push_front(root)
	var lights := root.find_children("*", "Light3D", true, false)
	var unique := {}
	for mi in meshes:
		if mi.mesh:
			unique[mi.mesh.get_instance_id()] = true

	var names := {}
	for n in root.find_children("*", "", true, false):
		names[n.name] = true

	var problems: Array[String] = []
	if meshes.size() != EXPECTED_MESHES:
		problems.append("meshes=%d expected %d" % [meshes.size(), EXPECTED_MESHES])
	if unique.size() != EXPECTED_UNIQUE:
		problems.append("unique=%d expected %d" % [unique.size(), EXPECTED_UNIQUE])
	if lights.size() != EXPECTED_LIGHTS:
		problems.append("lights=%d expected %d" % [lights.size(), EXPECTED_LIGHTS])
	for key in ["PROP_Z10_WorkLight", "DET_Z10_CableReel", "DET_Z10_Emergency_E"]:
		if not names.has(key):
			problems.append("missing %s" % key)
	for forbidden in ["VOL_Z10_Fog", "STUDIO_Z10_Backdrop", "STUDIO_Z10_Floor", "PROP_Z10_LockerDoor_01"]:
		if names.has(forbidden):
			problems.append("stray %s" % forbidden)

	var box := _aabb_of(meshes)
	if box.size == Vector3.ZERO:
		problems.append("empty AABB")
	else:
		if box.position.distance_to(EXPECTED_AABB_POS) > 0.25:
			problems.append("AABB pos %s expected %s" % [box.position, EXPECTED_AABB_POS])
		if box.size.distance_to(EXPECTED_AABB_SIZE) > 0.25:
			problems.append("AABB size %s expected %s" % [box.size, EXPECTED_AABB_SIZE])

	print("Z10_ABANDON_GODOT meshes=%d unique=%d lights=%d aabb_pos=%s aabb_size=%s" % [
		meshes.size(), unique.size(), lights.size(), box.position, box.size
	])
	if problems.is_empty():
		print("Z10_ABANDON_GODOT_OK")
		get_tree().quit(0)
	else:
		for p in problems:
			printerr("FAIL ", p)
		print("Z10_ABANDON_GODOT_FAIL")
		get_tree().quit(1)


func _aabb_of(nodes: Array) -> AABB:
	var box := AABB()
	var first := true
	for mi in nodes:
		if mi is MeshInstance3D and mi.mesh:
			var b: AABB = mi.global_transform * mi.mesh.get_aabb()
			if first:
				box = b
				first = false
			else:
				box = box.merge(b)
	return box


func _fail(msg: String) -> void:
	printerr("FAIL ", msg)
	print("Z10_ABANDON_GODOT_FAIL")
	get_tree().quit(1)
