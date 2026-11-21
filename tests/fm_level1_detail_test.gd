extends Node

func _ready() -> void:
	var scene = load("res://scenes/fm/level1.tscn").instantiate()
	add_child(scene)
	await get_tree().create_timer(3.0).timeout
	var space := get_viewport().world_3d.direct_space_state
	var prop_cols := 0
	for n in scene.find_children("PropCollider", "StaticBody3D", true, false):
		prop_cols += 1
	var checks := [
		["control_desk", Vector3(11.5, -4.9, -6.0), Vector3(8.8, -4.9, -6.0)],
		["rack_security", Vector3(7.0, -4.4, -8.95), Vector3(8.4, -4.4, -8.95)],
		["rack_control", Vector3(15.8, -4.4, -8.95), Vector3(14.0, -4.4, -8.95)],
		["reception_drawer", Vector3(-18.0, -5.0, -10.1), Vector3(-20.2, -5.0, -10.1)],
		["office_shelves", Vector3(-6.6, -4.4, -5.15), Vector3(-8.2, -4.4, -5.15)],
	]
	var passed := 0
	for c in checks:
		var q := PhysicsRayQueryParameters3D.create(c[1], c[2])
		var hit := space.intersect_ray(q)
		if hit.is_empty():
			print("DETAIL_COL ", c[0], " MISS")
		else:
			var col = hit.get("collider")
			print("DETAIL_COL ", c[0], " HIT ", col.name)
			passed += 1
	print("DETAIL_PROP_COLLIDERS ", prop_cols)
	print("DETAIL_RESULT ", "PASS" if passed == checks.size() and prop_cols >= 12 else "FAIL", " ", passed, "/", checks.size())
	get_tree().quit()
