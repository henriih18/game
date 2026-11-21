extends Node3D

const GLB := preload("res://assets/models/fm/reception_lod_test.glb")
const EXPECTED_MESHES := 122
const EXPECTED_UNIQUE := 108
const EXPECTED_LOD0 := 44
const EXPECTED_LOD1 := 39
const EXPECTED_LOD2 := 39

var meshes: Array[MeshInstance3D] = []


func _ready() -> void:
	var root := GLB.instantiate()
	add_child(root)
	await get_tree().process_frame
	_collect(root)

	var unique := {}
	var lod0 := 0
	var lod1 := 0
	var lod2 := 0
	var aabb := AABB()
	var first := true
	var strays: Array[String] = []

	for mi in meshes:
		if mi.mesh:
			unique[mi.mesh.get_instance_id()] = true
		var n := mi.name
		if "_LOD1" in n:
			lod1 += 1
		elif "_LOD2" in n:
			lod2 += 1
		else:
			lod0 += 1
		var box := mi.global_transform * mi.get_aabb()
		if first:
			aabb = box
			first = false
		else:
			aabb = aabb.merge(box)
		for token in ["STUDIO", "PROP_Z10", "RETIRED", "VAL_"]:
			if token in n.to_upper():
				strays.append(n)

	print("RECEPTION_LOD meshes=%d unique=%d lod0=%d lod1=%d lod2=%d" % [
		meshes.size(), unique.size(), lod0, lod1, lod2
	])
	print("RECEPTION_LOD aabb_pos=%s aabb_size=%s" % [aabb.position, aabb.size])
	if not strays.is_empty():
		print("RECEPTION_LOD_strays=%s" % [strays])
	var ok := meshes.size() == EXPECTED_MESHES \
		and unique.size() == EXPECTED_UNIQUE \
		and lod0 == EXPECTED_LOD0 \
		and lod1 == EXPECTED_LOD1 \
		and lod2 == EXPECTED_LOD2 \
		and strays.is_empty() \
		and aabb.position.x >= -111.0 and aabb.end.x <= -69.0 \
		and aabb.position.y >= -1.0 and aabb.end.y <= 6.0 \
		and aabb.position.z >= 3.0 and aabb.end.z <= 41.0
	if ok:
		print("RECEPTION_LOD_GODOT_OK")
		get_tree().quit(0)
	else:
		print("RECEPTION_LOD_GODOT_FAIL")
		get_tree().quit(1)


func _collect(node: Node) -> void:
	if node is MeshInstance3D and node.mesh != null:
		meshes.append(node)
	for child in node.get_children():
		_collect(child)
