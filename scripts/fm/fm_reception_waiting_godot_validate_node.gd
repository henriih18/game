extends Node3D

const GLB := "res://assets/models/fm/reception_waiting_lod.glb"

func _aabb_of(root: Node) -> AABB:
	var first := true
	var out := AABB()
	for n in root.find_children("*", "MeshInstance3D", true, false):
		if n.mesh == null:
			continue
		var box: AABB = n.global_transform * n.get_aabb()
		if first:
			out = box
			first = false
		else:
			out = out.merge(box)
	return out

func _ready() -> void:
	var packed: PackedScene = load(GLB)
	if packed == null:
		print("REC12_WAITING_GODOT_FAIL load")
		get_tree().quit(1)
		return
	var root := packed.instantiate()
	add_child(root)
	await get_tree().process_frame

	var meshes: Array = []
	var hidden_cols := 0
	for n in root.find_children("*", "MeshInstance3D", true, false):
		if String(n.name).ends_with("-col"):
			n.visible = false
			hidden_cols += 1
		meshes.append(n)

	var cols := root.find_children("*", "CollisionShape3D", true, false)
	var unique := {}
	for m in meshes:
		if m.mesh:
			unique[m.mesh] = true

	var strays: Array = []
	for m in meshes:
		var nm := String(m.name)
		if nm.contains("KIT_REC01_Walkway") or nm.begins_with("STUDIO") or nm.begins_with("PROP_Z10") or nm.contains("RETIRED") or nm.begins_with("VAL_"):
			strays.append(nm)

	var box := _aabb_of(root)
	print("REC12_WAITING meshes=%d unique=%d collisions=%d hidden_col=%d" % [meshes.size(), unique.size(), cols.size(), hidden_cols])
	print("REC12_WAITING aabb_pos=%s size=%s" % [box.position, box.size])
	print("REC12_WAITING strays=%s" % [strays])

	var ok := true
	if meshes.size() != 17:
		ok = false
	if unique.size() != 17:
		ok = false
	if cols.size() != 4:
		ok = false
	if not strays.is_empty():
		ok = false
	if box.size.x < 5.7 or box.size.x > 6.1:
		ok = false
	if box.size.y < 1.1 or box.size.y > 1.35:
		ok = false
	if box.size.z < 5.9 or box.size.z > 6.35:
		ok = false

	if ok:
		print("REC12_WAITING_GODOT_OK")
		get_tree().quit(0)
	else:
		print("REC12_WAITING_GODOT_FAIL")
		get_tree().quit(1)
