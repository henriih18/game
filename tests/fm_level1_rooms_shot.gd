extends Node

func _ready() -> void:
	var packed := load("res://scenes/fm/level1.tscn")
	var scene = packed.instantiate()
	add_child(scene)
	await get_tree().create_timer(2.5).timeout
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var views := [
		["recepcion", Vector3(-12.0, -5.6, -2.85), 0.0],
		["puerta_recepcion", Vector3(-12.0, -5.6, -5.0), 3.1416],
		["corredor", Vector3(-20.0, -5.6, 0.0), -1.5708],
		["seguridad", Vector3(3.0, -5.6, -2.8), 0.0],
		["control", Vector3(13.0, -5.6, -4.2), 0.0],
		["vestuarios", Vector3(-14.0, -5.6, 2.8), 3.1416],
		["almacen", Vector3(-2.0, -5.6, 2.8), 3.1416],
		["mantenimiento", Vector3(13.0, -5.6, 4.2), 3.1416],
		["oficina", Vector3(-7.75, -5.6, -5.3), 0.0],
		["aseo", Vector3(-7.75, -5.6, -2.1), 0.0],
	]
	for view in views:
		if scene.player == null:
			break
		scene.player.global_position = view[1]
		scene.player.rotation.y = view[2]
		scene.player.camera.rotation.x = -0.05
		scene.player.camera.rotation.y = 0.0
		await get_tree().create_timer(0.45).timeout
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		img.save_png("/tmp/opencode/level1_%s.png" % view[0])
		print("ROOM_SHOT ", view[0], " ", img.get_width(), "x", img.get_height())
	get_tree().quit()
