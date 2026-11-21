extends Node

func _ready() -> void:
	var scene = load("res://scenes/fm/level1.tscn").instantiate()
	add_child(scene)
	await get_tree().create_timer(2.5).timeout
	var lights: Array = scene.find_children("*", "Light3D", true, false)
	for l in lights:
		if l is SpotLight3D and l.name == "Flashlight":
			continue
		var p: Vector3 = l.global_position
		var near := []
		for mi in scene.glb_root.find_children("*", "MeshInstance3D", true, false):
			if mi.mesh == null:
				continue
			var box: AABB = mi.global_transform * mi.get_aabb()
			if box.grow(0.35).has_point(p):
				near.append(mi.name)
		if near.size() > 0:
			print("NEAR ", l.name, " ", p, " -> ", ", ".join(near))
	var seen := {}
	for mi in scene.glb_root.find_children("*", "MeshInstance3D", true, false):
		if mi.mesh == null:
			continue
		for s in range(mi.mesh.get_surface_count()):
			var m = mi.mesh.surface_get_material(s)
			if m is StandardMaterial3D and m.emission_enabled and m.emission_energy_multiplier > 0.25:
				var k = m.resource_name
				if not seen.has(k):
					seen[k] = [m.emission_energy_multiplier, mi.name]
	print("EMISSIVE_COUNT ", seen.size())
	for k in seen:
		print("EMISSIVE ", k, " e=%.2f ex=%s" % [seen[k][0], seen[k][1]])
	get_tree().quit()
