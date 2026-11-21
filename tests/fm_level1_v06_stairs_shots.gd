extends Node

## Capturas de evaluación de las escaleras del nivel V06.
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
		["main_entry", Vector3(-1.0, 0.12, 7.0), 3.1416, -0.03],
		["main_top", Vector3(-2.0, 0.12, 31.4), 3.1416, -0.18],
		["main_stairs", Vector3(-2.0, -0.6, 31.8), 3.1416, -0.52],
		["main_landing", Vector3(-2.0, -4.38, 42.2), 0.0, 0.16],
		["main_hall_east", Vector3(3.2, 0.12, 40.2), -1.5708, -0.04],
		["connector", Vector3(-1.0, 0.12, 22.0), 3.1416, -0.03],
		["e1_entry", Vector3(111.6, 0.12, -11.2), -1.5708, -0.04],
		["e1_stairs", Vector3(115.0, -0.4, -12.8), 0.0, -0.45],
		["e1_landing", Vector3(115.0, -4.38, -24.8), 3.1416, 0.14],
		["e2_entry", Vector3(113.6, 0.12, 38.2), -1.5708, -0.04],
		["e2_stairs", Vector3(117.0, -2.0, 33.2), 3.1416, -0.2],
		["e2_landing", Vector3(117.0, -4.38, 27.2), 3.1416, 0.14],
	]
	for view in views:
		player.global_position = view[1]
		player.rotation.y = view[2]
		player.camera.rotation.x = view[3]
		player.camera.rotation.y = 0.0
		await get_tree().create_timer(0.5).timeout
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		var path := "/tmp/opencode/st_godot_%s.png" % view[0]
		img.save_png(path)
		print("ST_SHOT ", view[0], " ", img.get_width(), "x", img.get_height())
	get_tree().quit()
