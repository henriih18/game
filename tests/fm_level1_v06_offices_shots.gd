extends Node

## Capturas de evaluación de Oficinas en el nivel V06.
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
		["entry", Vector3(-10.0, 0.12, -32.0), 0.0, -0.02],
		["reception", Vector3(-8.0, 0.12, -32.5), -1.23, -0.03],
		["open_office", Vector3(-21.0, 0.12, -40.5), -0.35, -0.04],
		["desks", Vector3(-20.0, 0.12, -40.5), 0.0, -0.06],
		["private", Vector3(-21.5, 0.12, -61.2), -0.45, -0.04],
		["meeting", Vector3(8.5, 0.12, -59.4), 0.0, -0.05],
		["archive", Vector3(5.2, 0.12, -46.0), 0.0, -0.03],
		["cafeteria", Vector3(8.5, 0.12, -32.0), 0.0, -0.03],
		["connector", Vector3(-10.0, 0.12, -6.0), 0.0, -0.03],
		["east_door", Vector3(11.8, 0.12, -49.0), -1.5708, -0.03],
		["lookback", Vector3(-10.0, 0.12, -52.0), 3.1416, -0.03],
	]
	for view in views:
		player.global_position = view[1]
		player.rotation.y = view[2]
		player.camera.rotation.x = view[3]
		player.camera.rotation.y = 0.0
		await get_tree().create_timer(0.45).timeout
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		var path := "/tmp/opencode/of_godot_%s.png" % view[0]
		img.save_png(path)
		print("OF_SHOT ", view[0], " ", img.get_width(), "x", img.get_height())
	get_tree().quit()
