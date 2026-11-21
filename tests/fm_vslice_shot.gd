extends Node

## Capturas de revisión del vertical slice. Ejecutar en ventana:
## godot --path . tests/fm_vslice_shot.tscn

var scene


func _ready() -> void:
	DisplayServer.window_set_size(Vector2i(1280, 720))
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = 0
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var packed: PackedScene = load("res://scenes/fm/fm_vslice_z10.tscn")
	scene = packed.instantiate()
	add_child(scene)
	var guard := 0
	while not scene.level_ready and guard < 600:
		await get_tree().process_frame
		guard += 1
	await get_tree().create_timer(2.0).timeout
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	scene.player._mouse_ignore_time = 0.0
	var yaw_before: float = scene.player.rotation.y
	var look := InputEventMouseMotion.new()
	look.relative = Vector2(24.0, 12.0)
	scene.player._unhandled_input(look)
	var yaw_after: float = scene.player.rotation.y
	print("SHOT_LOOK_OK %s yaw=%.3f->%.3f" % [str(absf(yaw_after - yaw_before) > 0.01), yaw_before, yaw_after])
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	scene.watcher.set_physics_process(false)
	scene.player.set_physics_process(false)
	await get_tree().physics_frame

	await _shot("docs/fm_vslice_z10_spawn.png", Vector3(42.2, 0.12, -22.0), -PI * 0.5, 0.0)
	await _shot("docs/fm_vslice_z10_hiding.png", Vector3(42.5, 0.12, -11.2), PI, 0.0)
	await _shot("docs/fm_vslice_z10_core.png", Vector3(53.0, 0.12, -21.4), -PI * 0.5, -0.10)
	await _shot("docs/fm_vslice_z10_transition.png", Vector3(66.8, 0.12, -21.0), -PI * 0.5, 0.0)
	scene.watcher.visible = true
	scene.watcher.global_position = Vector3(50.0, 0.12, -20.0)
	scene.watcher.rotation.y = PI * 0.5
	await _shot("docs/fm_vslice_z10_watcher.png", Vector3(45.5, 0.12, -20.0), -PI * 0.5, 0.02)

	scene.world_env.environment = scene.reception_environment
	scene.current_area = "RECEPTION"
	scene._watcher_suspended = true
	scene.hud.set_objective("LLEVAR EL NÚCLEO A EXTRACCIÓN", "Recepción · nivel 1 · ala sur")
	scene.hud.set_watcher_observed(false)
	await _shot("docs/fm_vslice_reception_hall.png", Vector3(-90.0, 0.12, 9.5), PI, 0.0)
	await _shot("docs/fm_vslice_reception_extraction.png", Vector3(-94.0, 0.12, 33.8), PI, -0.04)

	print("FM_VSLICE_SHOTS_DONE")
	get_tree().quit()


func _shot(path: String, pos: Vector3, yaw: float, pitch: float) -> void:
	scene.player.global_position = pos
	scene.player.rotation.y = yaw
	scene.player.camera.rotation.x = pitch
	scene.player.camera.rotation.y = 0.0
	scene.player.camera.position = Vector3(0.0, 1.62, 0.0)
	scene.player.flashlight_on = true
	scene.player.battery = 100.0
	await get_tree().create_timer(0.55).timeout
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	var err := image.save_png(path)
	print("SHOT %s %dx%d err=%d" % [path, image.get_width(), image.get_height(), err])
