extends Node

## Capturas de evaluación de Mantenimiento en el nivel V06.
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
		["entry", Vector3(63.0, 0.12, 10.2), 3.1416, -0.02],
		["aisle_center", Vector3(69.0, 0.12, 16.0), 3.1416, -0.03],
		["boilers", Vector3(73.2, 0.12, 25.0), -1.5708, -0.03],
		["pumps", Vector3(86.0, 0.12, 27.8), 0.0, -0.04],
		["tanks", Vector3(80.6, 0.12, 40.2), 3.1416, -0.03],
		["electrical", Vector3(82.0, 0.12, 13.2), 0.0, -0.03],
		["workshop", Vector3(61.8, 0.12, 14.0), 1.5708, -0.03],
		["chemical", Vector3(64.2, 0.12, 23.2), 1.5708, -0.04],
		["east_ahu", Vector3(102.0, 0.12, 22.0), -1.5708, -0.02],
		["se_bench", Vector3(102.0, 0.12, 43.8), 3.1416, -0.04],
		["lookback", Vector3(90.0, 0.12, 33.0), 0.0, -0.03],
	]
	for view in views:
		player.global_position = view[1]
		player.rotation.y = view[2]
		player.camera.rotation.x = view[3]
		player.camera.rotation.y = 0.0
		await get_tree().create_timer(0.45).timeout
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		var path := "/tmp/opencode/mt_godot_%s.png" % view[0]
		img.save_png(path)
		print("MT_SHOT ", view[0], " ", img.get_width(), "x", img.get_height())
	get_tree().quit()
