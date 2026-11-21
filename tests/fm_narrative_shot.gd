extends Node

## Capturas de revisión de los ocho anclajes narrativos. Ejecutar en ventana:
## godot --path . tests/fm_narrative_shot.tscn

var scene


func _ready() -> void:
	DisplayServer.window_set_size(Vector2i(1280, 720))
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var packed: PackedScene = load("res://scenes/fm/fm_vslice_z10.tscn")
	scene = packed.instantiate()
	add_child(scene)
	var guard := 0
	while not scene.level_ready and guard < 600:
		await get_tree().process_frame
		guard += 1
	scene.watcher.set_physics_process(false)
	scene.watcher.visible = false
	scene.player.set_physics_process(false)
	scene.world_env.environment = scene.reception_environment
	scene.current_area = "RECEPTION"
	scene._watcher_suspended = true
	scene.player.flashlight_on = true
	scene.player.battery = 100.0
	if scene.hud != null:
		scene.hud.set_objective("INSPECCIONAR RECEPCIÓN", "Anclajes narrativos N1 · N2 · N3 · N4 · N5 · N6 · N7 · N8")
		scene.hud.set_status("RECEPCIÓN · ANCLAJES NARRATIVOS")
	await get_tree().create_timer(1.8).timeout

	await _shot("docs/fm_narrative_n1_counter.png", Vector3(-100.55, 0.12, 12.35), 2.17, -0.20)
	await _shot("docs/fm_narrative_n1_route.png", Vector3(-90.0, 0.12, 12.7), 1.644, -0.05)
	await _shot("docs/fm_narrative_n2_waiting.png", Vector3(-104.6, 0.12, 21.8), PI * 0.5, -0.12)
	await _shot("docs/fm_narrative_n3_lockers.png", Vector3(-106.0, 0.12, 37.7), PI, -0.05)
	await _shot("docs/fm_narrative_n3_fallen.png", Vector3(-105.0, 0.12, 37.8), 2.90, -0.42)
	await _shot("docs/fm_narrative_n4_security.png", Vector3(-84.0, 0.12, 9.2), PI, -0.22)
	await _shot("docs/fm_narrative_n4_route.png", Vector3(-90.0, 0.12, 12.8), -1.249, -0.08)
	await _shot("docs/fm_narrative_n5_entrance.png", Vector3(-90.0, 0.12, 6.2), PI, -0.02)
	await _shot("docs/fm_narrative_n5_handprint.png", Vector3(-92.8, 0.12, 6.7), PI, -0.10)
	await _shot("docs/fm_narrative_n6_trail.png", Vector3(-93.0, 0.12, 28.5), 1.571, -0.25)
	await _shot("docs/fm_narrative_n7_decon.png", Vector3(-94.0, 0.12, 36.4), 1.690, -0.16)
	await _shot("docs/fm_narrative_n7_cart.png", Vector3(-97.2, 0.12, 36.0), 2.43, -0.16)
	await _shot("docs/fm_narrative_n7_samples.png", Vector3(-94.0, 0.12, 36.4), -1.729, -0.20)
	await _shot("docs/fm_narrative_n8_link.png", Vector3(67.4, 0.12, -21.4), 0.0, -0.08)
	await _shot("docs/fm_narrative_n8_handprint.png", Vector3(68.2, 0.12, -20.0), -0.59, -0.10)
	print("FM_NARRATIVE_SHOTS_DONE")
	get_tree().quit()


func _shot(path: String, pos: Vector3, yaw: float, pitch: float) -> void:
	scene.player.global_position = pos
	scene.player.rotation.y = yaw
	scene.player.camera.rotation.x = pitch
	scene.player.camera.rotation.y = 0.0
	scene.player.camera.position = Vector3(0.0, 1.62, 0.0)
	await get_tree().create_timer(0.65).timeout
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	var err := image.save_png(path)
	print("SHOT %s %dx%d err=%d" % [path, image.get_width(), image.get_height(), err])
