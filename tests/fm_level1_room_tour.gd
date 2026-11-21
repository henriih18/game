extends Node

## Recorrido de evaluación de todas las zonas del Nivel 1.
## Escribe capturas en /tmp/opencode/tour_*.png

func _ready() -> void:
	var packed := load("res://scenes/fm/level1.tscn")
	var scene = packed.instantiate()
	add_child(scene)
	await get_tree().create_timer(3.0).timeout
	if scene.hud != null:
		scene.hud.visible = false
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var views := [
		["rec_entry", Vector3(-12.0, -5.6, -2.45), 0.0, -0.03],
		["rec_desk", Vector3(-12.0, -5.6, -4.75), 0.0, -0.10],
		["rec_east", Vector3(-5.2, -5.6, -3.4), 0.75, 0.0],
		["rec_west", Vector3(-18.8, -5.6, -3.6), -0.75, 0.0],
		["rec_deep", Vector3(-12.0, -5.6, -9.8), 3.14159, 0.0],
		["office", Vector3(-6.25, -5.6, -2.55), 0.0, 0.0],
		["office_deep", Vector3(-6.25, -5.6, -6.9), 3.14159, 0.0],
		["corridor_w", Vector3(-20.2, -5.6, 0.0), -1.5708, -0.02],
		["corridor_mid", Vector3(-1.0, -5.6, 0.0), -1.5708, -0.02],
		["corridor_e", Vector3(19.5, -5.6, 0.0), 1.5708, -0.02],
		["security", Vector3(2.1, -5.6, -2.9), 0.0, 0.0],
		["security_deep", Vector3(2.1, -5.6, -7.4), 3.14159, 0.0],
		["control", Vector3(12.1, -5.6, -2.9), 0.0, 0.0],
		["control_deep", Vector3(12.1, -5.6, -7.4), 3.14159, 0.0],
		["lockers", Vector3(-14.9, -5.6, 2.6), 3.14159, 0.0],
		["lockers_deep", Vector3(-14.9, -5.6, 7.6), 0.0, 0.0],
		["storage", Vector3(-2.9, -5.6, 2.6), 3.14159, 0.0],
		["storage_deep", Vector3(-2.9, -5.6, 7.6), 0.0, 0.0],
		["maintenance", Vector3(12.1, -5.6, 2.6), 3.14159, 0.0],
		["maintenance_deep", Vector3(12.1, -5.6, 7.6), 0.0, 0.0],
	]
	for view in views:
		if scene.player == null:
			break
		scene.player.global_position = view[1]
		scene.player.rotation.y = view[2]
		scene.player.camera.rotation.x = view[3]
		scene.player.camera.rotation.y = 0.0
		if view[0] == "corridor_mid" or view[0] == "corridor_w":
			var cam: Camera3D = scene.player.camera
			for pt in [Vector2(640, 330), Vector2(600, 310), Vector2(690, 320), Vector2(650, 300)]:
				var origin: Vector3 = cam.project_ray_origin(pt)
				var dir: Vector3 = cam.project_ray_normal(pt)
				var q := PhysicsRayQueryParameters3D.create(origin, origin + dir * 30.0)
				var hit := cam.get_world_3d().direct_space_state.intersect_ray(q)
				if hit.is_empty():
					print("PROBE ", view[0], " ", pt, " clear")
				else:
					var col = hit.get("collider")
					print("PROBE ", view[0], " ", pt, " ", col.name if col else "null", " pos=", hit.get("position"))
		await get_tree().create_timer(0.5).timeout
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		img.save_png("/tmp/opencode/tour_%s.png" % view[0])
		print("TOUR_SHOT ", view[0], " ", img.get_width(), "x", img.get_height())
	get_tree().quit()
