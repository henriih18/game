extends Node

## Capturas de evaluación de la Fase 3A. Solo escribe en /tmp/opencode.

func _ready() -> void:
	var packed := load("res://scenes/fm/level1.tscn")
	var scene = packed.instantiate()
	add_child(scene)
	await get_tree().create_timer(3.0).timeout
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var views := [
		["art_reception_wide", Vector3(-12.0, -5.6, -2.85), 0.0, -0.05],
		["art_counter", Vector3(-12.0, -5.6, -4.6), 0.0, -0.12],
		["art_logo", Vector3(-12.0, -5.6, -6.4), 0.0, 0.12],
		["art_corridor_wide", Vector3(-20.0, -5.6, 0.0), -1.5708, -0.03],
		["art_corridor_detail", Vector3(-10.0, -5.6, 0.8), -1.5708, 0.18],
		["art_corridor_back", Vector3(8.0, -5.6, 0.0), 1.5708, -0.03],
	]
	for view in views:
		if scene.player == null:
			break
		scene.player.global_position = view[1]
		scene.player.rotation.y = view[2]
		scene.player.camera.rotation.x = view[3]
		scene.player.camera.rotation.y = 0.0
		await get_tree().create_timer(0.45).timeout
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		img.save_png("/tmp/opencode/%s.png" % view[0])
		print("ART_SHOT ", view[0], " ", img.get_width(), "x", img.get_height())
	get_tree().quit()
