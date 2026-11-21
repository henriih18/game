extends Node

## Capturas de evaluación del Almacén en el nivel V06.
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
		["entry", Vector3(72.0, 0.12, -11.5), 0.0, -0.02],
		["aisle_center", Vector3(90.0, 0.12, -20.0), 0.0, -0.02],
		["racks_north", Vector3(90.0, 0.12, -29.0), 0.0, -0.03],
		["forklift", Vector3(82.0, 0.12, -26.0), 0.5, -0.04],
		["packing", Vector3(87.2, 0.12, -12.5), 3.1416, -0.03],
		["staging", Vector3(94.0, 0.12, -25.0), 0.0, -0.03],
		["security_cage", Vector3(103.0, 0.12, -31.0), -0.7, -0.03],
		["east_racks", Vector3(104.0, 0.12, -20.0), -1.5708, -0.02],
		["lookback", Vector3(90.0, 0.12, -30.0), 3.1416, -0.02],
		["mezzanine_ramp", Vector3(88.35, 0.12, -20.2), 0.0, 0.10],
		["mezzanine_under", Vector3(84.8, 0.12, -30.8), -1.5708, 0.12],
		["mezzanine_top", Vector3(91.7, 2.75, -30.6), 0.0, -0.06],
		["mezzanine_side", Vector3(95.0, 0.12, -30.5), 1.5708, 0.10],
	]
	for view in views:
		player.global_position = view[1]
		player.rotation.y = view[2]
		player.camera.rotation.x = view[3]
		player.camera.rotation.y = 0.0
		await get_tree().create_timer(0.45).timeout
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		var path := "/tmp/opencode/wh_godot_%s.png" % view[0]
		img.save_png(path)
		print("WH_SHOT ", view[0], " ", img.get_width(), "x", img.get_height())
	get_tree().quit()
