extends Node3D

## Validación headless de los GLB P0a.2 en Godot 4.7.2 (escena).
## Comprueba importación, ausencia de strays, colisiones -col y dimensiones.

const LIB := "res://assets/models/fm/p0a_library_lod.glb"
const TEST := "res://assets/models/fm/p0a_test_assembly.glb"


func _aabb_of(root: Node3D) -> AABB:
	var box := AABB()
	var first := true
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		var b: AABB = mi.global_transform * mi.get_aabb()
		if first:
			box = b
			first = false
		else:
			box = box.merge(b)
	return box


func _mesh_count(root: Node) -> int:
	var n := 0
	for node in root.find_children("*", "MeshInstance3D", true, false):
		if (node as MeshInstance3D).mesh != null:
			n += 1
	return n


func _find_named(root: Node, token: String) -> Array:
	var found := []
	for node in root.find_children("*", "Node", true, false):
		if node.name.to_lower().contains(token.to_lower()):
			found.append(node)
	return found


func _ready() -> void:
	var ok := true
	print("P0A2_GODOT_VALIDATE_BEGIN")

	var lib_res := load(LIB)
	if lib_res == null:
		print("FAIL load library")
		get_tree().quit(1)
		return
	var lib: Node3D = lib_res.instantiate()
	add_child(lib)
	await get_tree().process_frame

	var lib_meshes := _mesh_count(lib)
	var lib_box := _aabb_of(lib)
	var lib_cols := _find_named(lib, "-col")
	var lib_shapes := lib.find_children("*", "CollisionShape3D", true, false)
	var col_names := []
	for n in lib_cols:
		col_names.append("%s visible=%s" % [n.name, str(n.visible)])
	print("LIB_COLS %s" % str(col_names))
	print("LIB_COLSHAPES %d" % lib_shapes.size())
	if lib_shapes.size() < 3:
		print("FAIL library collision shapes < 3")
		ok = false
	for n in lib_shapes:
		var cs := n as CollisionShape3D
		print("COLSHAPE %s shape=%s parent=%s" % [cs.name, str(cs.shape), str(cs.get_parent().name)])
	print("LIB meshes=%d cols=%d aabb_pos=%s aabb_size=%s" % [
		lib_meshes, lib_cols.size(), str(lib_box.position), str(lib_box.size)])
	if lib_meshes < 20:
		print("FAIL library meshes < 20")
		ok = false
	for n in lib_cols:
		if n is MeshInstance3D:
			n.visible = false
			print("HIDDEN_COL_PROXY %s" % n.name)
		else:
			print("FAIL collision proxy is not MeshInstance3D: %s" % n.name)
			ok = false

	var door_root: Node3D = lib.find_child("SM_SH_DOOR_SEC_SINGLE_ROOT", true, false)
	if door_root == null:
		print("FAIL missing SM_SH_DOOR_SEC_SINGLE_ROOT")
		ok = false
	else:
		var door_box := _aabb_of(door_root)
		print("DOOR_LOD0 aabb_size=%s" % str(door_box.size))
		if absf(door_box.size.y - 2.48) > 0.15:
			print("FAIL door height %f" % door_box.size.y)
			ok = false

	var light_root: Node3D = lib.find_child("SM_SH_LUMINAIRE_1500_ON_ROOT", true, false)
	if light_root == null:
		print("FAIL missing SM_SH_LUMINAIRE_1500_ON_ROOT")
		ok = false
	else:
		var light_box := _aabb_of(light_root)
		print("LIGHT_LOD0 aabb_size=%s" % str(light_box.size))
		if absf(light_box.size.x - 1.56) > 0.12:
			print("FAIL light length %f" % light_box.size.x)
			ok = false

	var test_res := load(TEST)
	if test_res == null:
		print("FAIL load test assembly")
		get_tree().quit(1)
		return
	var test: Node3D = test_res.instantiate()
	add_child(test)
	await get_tree().process_frame

	var test_meshes := _mesh_count(test)
	var test_box := _aabb_of(test)
	print("TEST meshes=%d aabb_pos=%s aabb_size=%s" % [
		test_meshes, str(test_box.position), str(test_box.size)])
	if test_meshes < 45:
		print("FAIL test meshes < 45")
		ok = false

	for node in lib.find_children("*", "Node", true, false):
		if str(node.name).to_lower().contains("prop_z10"):
			print("FAIL stray PROP_Z10 in library: %s" % node.name)
			ok = false
	for node in test.find_children("*", "Node", true, false):
		if str(node.name).to_lower().contains("prop_z10"):
			print("FAIL stray PROP_Z10 in test: %s" % node.name)
			ok = false

	if ok:
		print("P0A2_GODOT_OK")
	else:
		print("P0A2_GODOT_FAIL")
	get_tree().quit(0 if ok else 1)
