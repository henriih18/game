extends Node

## Capturas de evaluación de Control de Acceso en el nivel V06.
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
		["entry", Vector3(-94.0, 0.12, -42.8), 0.0, -0.05],
		["center", Vector3(-94.0, 0.12, -44.6), 0.0, -0.08],
		["turnstiles", Vector3(-91.5, 0.12, -44.3), 0.0, -0.16],
		["booth", Vector3(-99.8, 0.12, -53.0), 0.6, -0.02],
		["monitors", Vector3(-100.0, 0.12, -47.0), 1.5708, -0.02],
		["east", Vector3(-82.0, 0.12, -50.0), -1.5708, -0.02],
		["lookback", Vector3(-91.5, 0.12, -52.0), 3.1416, -0.02],
	]
	for view in views:
		player.global_position = view[1]
		player.rotation.y = view[2]
		player.camera.rotation.x = view[3]
		player.camera.rotation.y = 0.0
		await get_tree().create_timer(0.45).timeout
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		var path := "/tmp/opencode/ctrl_godot_%s.png" % view[0]
		img.save_png(path)
		print("CTRL_SHOT ", view[0], " ", img.get_width(), "x", img.get_height())
	get_tree().quit()
