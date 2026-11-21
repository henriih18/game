extends Node

func _ready() -> void:
	var packed := load("res://scenes/fm/level1.tscn")
	var scene = packed.instantiate()
	add_child(scene)
	while not scene.level_ready:
		await get_tree().physics_frame
	await get_tree().create_timer(0.5).timeout
	# El Vigilante puede entrar en estado de deteccion y distorsiona la medicion.
	if scene.watcher != null:
		scene.watcher.set_process(false)
		scene.watcher.set_physics_process(false)
		scene.watcher.visible = false
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	if scene.player != null:
		scene.player.set_physics_process(false)
		scene.player.global_position = Vector3(-12.0, -5.6, -2.85)
		scene.player.rotation.y = 0.0
		scene.player.camera.rotation.x = -0.045
		scene.player.camera.rotation.y = 0.0
	await get_tree().create_timer(4.0).timeout
	var fps := Performance.get_monitor(Performance.TIME_FPS)
	var draws := Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)
	var prims := Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)
	var objects := Performance.get_monitor(Performance.OBJECT_COUNT)
	print("LEVEL1_PERF fps=%.1f draws=%d primitives=%d objects=%d" % [fps, int(draws), int(prims), int(objects)])
	get_tree().quit()
