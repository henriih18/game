extends Node

func _ready() -> void:
	var scene = load("res://scenes/fm/level1.tscn").instantiate()
	add_child(scene)
	await get_tree().create_timer(3.0).timeout
	if scene.hud != null:
		scene.hud.visible = false
	var views := {
		"corridor_mid": [Vector3(-1.0, -5.6, 0.0), -1.5708, -0.02, Rect2(430, 260, 380, 100)],
		"storage": [Vector3(-2.9, -5.6, 2.6), 3.14159, 0.0, Rect2(560, 120, 260, 160)],
		"lockers": [Vector3(-14.9, -5.6, 2.6), 3.14159, 0.0, Rect2(400, 180, 340, 160)],
	}
	for key in views:
		var v = views[key]
		scene.player.global_position = v[0]
		scene.player.rotation.y = v[1]
		scene.player.camera.rotation.x = v[2]
		scene.player.camera.rotation.y = 0.0
		await get_tree().create_timer(0.5).timeout
		var cam: Camera3D = scene.player.camera
		var rect: Rect2 = v[3]
		var hits := {}
		var x := rect.position.x
		while x <= rect.end.x:
			var y := rect.position.y
			while y <= rect.end.y:
				var origin: Vector3 = cam.project_ray_origin(Vector2(x, y))
				var dir: Vector3 = cam.project_ray_normal(Vector2(x, y))
				var q := PhysicsRayQueryParameters3D.create(origin, origin + dir * 40.0)
				var hit := cam.get_world_3d().direct_space_state.intersect_ray(q)
				if not hit.is_empty():
					var col = hit.get("collider")
					var nm = col.name if col else "null"
					if not hits.has(nm):
						hits[nm] = [Vector2(x, y), hit.get("position")]
				y += 20.0
			x += 20.0
		print("AIMVIEW ", key)
		for nm in hits:
			print("AIM ", nm, " at ", hits[nm][0], " pos=", hits[nm][1])
	get_tree().quit()
