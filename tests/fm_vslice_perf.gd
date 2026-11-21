extends Node

## Medición de rendimiento del vertical slice en ventana.
## godot --path . tests/fm_vslice_perf.tscn
## Es una escena jugable estática (jugador y Vigilante congelados), no una
## partida completa. Sirve para comparar Z10 y Recepción en la misma build.

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
	scene.watcher.set_physics_process(false)
	scene.watcher.visible = false
	scene.player.set_physics_process(false)

	await _pose(Vector3(42.2, 0.12, -22.0), -PI * 0.5)
	await _measure("Z10")

	scene.world_env.environment = scene.reception_environment
	scene.current_area = "RECEPTION"
	scene._watcher_suspended = true
	await _pose(Vector3(-90.0, 0.12, 9.5), PI)
	await _measure("RECEPTION")

	get_tree().quit()


func _pose(pos: Vector3, yaw: float) -> void:
	scene.player.global_position = pos
	scene.player.rotation.y = yaw
	scene.player.camera.rotation.x = 0.0
	scene.player.camera.rotation.y = 0.0
	scene.player.camera.position = Vector3(0.0, 1.62, 0.0)
	scene.player.flashlight_on = true
	scene.player.battery = 100.0
	await get_tree().create_timer(1.0).timeout


func _measure(label: String) -> void:
	await get_tree().create_timer(1.0).timeout
	var t0 := Time.get_ticks_usec()
	var f0 := Engine.get_frames_drawn()
	await get_tree().create_timer(4.0).timeout
	var dt := (Time.get_ticks_usec() - t0) / 1000000.0
	var frames := Engine.get_frames_drawn() - f0
	var fps := float(frames) / maxf(dt, 0.001)
	var draws := Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)
	var prims := Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)
	var objects := Performance.get_monitor(Performance.OBJECT_COUNT)
	var tex_mem := Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED) / (1024.0 * 1024.0)
	var vid_mem := Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED) / (1024.0 * 1024.0)
	print("VSLICE_PERF %s fps=%.1f frames=%d time=%.2f draws=%d primitives=%d objects=%d tex_mb=%.1f video_mb=%.1f" % [
		label, fps, frames, dt, int(draws), int(prims), int(objects), tex_mem, vid_mem,
	])
