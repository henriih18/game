extends Node

## Capturas de evaluación del Aseo de planta en el nivel V06.
## Solo escribe en /tmp/opencode.

const SCENE_PATH := "res://scenes/fm/level1_v06.tscn"

func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var packed := load(SCENE_PATH) as PackedScene
	if packed == null:
		push_error("no scene")
		get_tree().quit(1)
		return
	var scene = packed.instantiate()
	add_child(scene)
	var guard := 0
	while not scene.level_ready and guard < 3600:
		await get_tree().process_frame
		guard += 1
	await get_tree().create_timer(1.2).timeout
	if scene.watcher != null and is_instance_valid(scene.watcher):
		scene.watcher.set_physics_process(false)
	if scene.security_watcher != null and is_instance_valid(scene.security_watcher):
		scene.security_watcher.set_physics_process(false)
	var player = scene.player
	if player == null:
		push_error("no player")
		get_tree().quit(1)
		return
	var views := [
		["entry", Vector3(16.7, 0.12, -49.0), -1.5708, -0.03],
		["corridor", Vector3(19.4, 0.12, -49.3), -1.4, -0.03],
		["sinks_north", Vector3(21.8, 0.12, -54.4), 1.5708, -0.03],
		["sinks_south", Vector3(19.8, 0.12, -46.5), 2.63, -0.04],
		["stalls_north", Vector3(25.6, 0.12, -52.6), 0.0, -0.03],
		["stalls_south", Vector3(25.4, 0.12, -47.2), 3.1416, -0.03],
		["accessible", Vector3(28.4, 0.12, -52.4), 0.0, -0.04],
		["cleaning", Vector3(19.15, 0.12, -44.15), 3.1416, -0.06],
		["east_door", Vector3(27.4, 0.12, -50.0), -1.5708, -0.03],
		["lookback", Vector3(29.0, 0.12, -49.6), 1.5708, -0.03],
	]
	for view in views:
		player.global_position = view[1]
		player.rotation.y = view[2]
		player.camera.rotation.x = view[3]
		player.camera.rotation.y = 0.0
		await get_tree().create_timer(0.45).timeout
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		var path := "/tmp/opencode/rs_godot_%s.png" % view[0]
		img.save_png(path)
		print("RS_SHOT ", view[0], " ", img.get_width(), "x", img.get_height())
	get_tree().quit()
