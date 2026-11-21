extends Node3D

## Validación headless del GLB completo del sector Z10 + Service Link.

const GLB := "res://assets/models/fm/z10_sector.glb"


func _aabb_of(root: Node3D) -> AABB:
	var box := AABB()
	var first := true
	var nodes := []
	if root is MeshInstance3D and root.mesh != null:
		nodes.append(root)
	nodes.append_array(root.find_children("*", "MeshInstance3D", true, false))
	for node in nodes:
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


func _ready() -> void:
	var ok := true
	print("Z10_SECTOR_VALIDATE_BEGIN")

	var res := load(GLB)
	if res == null:
		print("FAIL load %s" % GLB)
		get_tree().quit(1)
		return
	var scene: Node3D = res.instantiate()
	add_child(scene)
	await get_tree().process_frame

	var meshes := []
	for node in scene.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi != null and mi.mesh != null:
			meshes.append(mi)
	var unique := {}
	for mi in meshes:
		unique[mi.mesh.get_instance_id()] = true
	var box := _aabb_of(scene)

	var lights := []
	for node in scene.find_children("*", "Light3D", true, false):
		lights.append(node)

	print("Z10_SECTOR meshes=%d unique=%d lights=%d" % [meshes.size(), unique.size(), lights.size()])
	print("Z10_SECTOR aabb_pos=%s aabb_size=%s" % [str(box.position), str(box.size)])

	if meshes.size() < 505 or meshes.size() > 508:
		print("FAIL mesh count %d outside 505..508" % meshes.size())
		ok = false
	if unique.size() < 400 or unique.size() > 404:
		print("FAIL unique mesh count %d outside 400..404" % unique.size())
		ok = false
	if lights.size() != 9:
		print("FAIL expected 9 lights, got %d" % lights.size())
		ok = false

	for mi in meshes:
		var nm := String(mi.name)
		var up := nm.to_upper()
		if up.contains("STUDIO") or up.contains("PLAYERPROXY") or up.contains("RETIRED") or up.contains("CHANGINGCONNECTOR") or up.contains("L1_P0B_LOD") or up.contains("LEGACY"):
			print("FAIL stray node %s" % nm)
			ok = false

	# Godot Y-up: x 39.87..70.15, y -0.209..6.0, z -34.94..2.0
	if box.size.x < 29.5 or box.size.x > 31.0:
		print("FAIL aabb x %.4f outside 29.5..31.0" % box.size.x)
		ok = false
	if box.size.y < 5.5 or box.size.y > 6.5:
		print("FAIL aabb y %.4f outside 5.5..6.5" % box.size.y)
		ok = false
	if box.size.z < 35.0 or box.size.z > 38.0:
		print("FAIL aabb z %.4f outside 35.0..38.0" % box.size.z)
		ok = false
	if box.position.x > 40.2:
		print("FAIL aabb min x %.4f (expected <= 40.2)" % box.position.x)
		ok = false
	if box.position.z > -34.0:
		print("FAIL aabb min z %.4f (expected <= -34.0)" % box.position.z)
		ok = false

	for req in ["P0B4_HVAC_RUN_800x600", "P0B4_TRAY_WEST", "P0B4_TRAY_EAST", "P0B5_RISER_A", "P0B5_RISER_B", "P0B5_SPRINKLER_BRANCHES", "P0B5_SPRINKLER_TEES", "P0B5_SPRINKLER_ESCUTCHEONS", "DET_Z10_CableReel", "PROP_Z10_WorkLight"]:
		if scene.find_child(req, true, false) == null:
			print("FAIL missing node %s" % req)
			ok = false

	if ok:
		print("Z10_SECTOR_GODOT_OK")
		get_tree().quit(0)
	else:
		print("Z10_SECTOR_GODOT_FAIL")
		get_tree().quit(1)
