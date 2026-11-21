extends Node

## Capturas de verificación de las correcciones MEP del nivel V06.
## Cámara libre para poder mirar los servicios de techo. Solo escribe en /tmp/opencode.

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
	var cam := Camera3D.new()
	cam.fov = 68.0
	cam.near = 0.05
	cam.far = 120.0
	scene.add_child(cam)
	cam.current = true
	var lamp := OmniLight3D.new()
	lamp.omni_range = 9.0
	lamp.light_energy = 3.5
	lamp.shadow_enabled = false
	cam.add_child(lamp)
	var views := [
		["warehouse_link", Vector3(63.0, 2.6, -22.75), Vector3(70.1, 2.9, -22.75)],
		["warehouse_riser", Vector3(73.0, 3.0, -22.75), Vector3(70.3, 3.9, -22.75)],
		["offices_connector", Vector3(-10.0, 3.6, -12.0), Vector3(-10.0, 4.0, -28.0)],
		["offices_lobby", Vector3(-11.0, 2.4, -34.0), Vector3(-10.0, 3.95, -30.0)],
		["restroom_link", Vector3(16.0, 1.8, -50.2), Vector3(26.0, 2.88, -50.2)],
		["restroom_extract", Vector3(23.0, 1.8, -52.0), Vector3(26.0, 2.9, -57.4)],
		["control_hvac", Vector3(-91.0, 3.2, -44.0), Vector3(-91.0, 5.0, -49.0)],
		["maintenance_ahu", Vector3(102.5, 3.0, 16.5), Vector3(108.6, 5.4, 16.5)],
		["stairs_transition", Vector3(-1.0, 1.8, 7.8), Vector3(-1.0, 3.4, 2.5)],
		["stairs_e1_link", Vector3(116.6, 3.9, -14.8), Vector3(110.2, 4.5, -12.0)],
		["stairs_e2_link", Vector3(118.6, 3.9, 35.2), Vector3(112.2, 4.5, 38.0)],
	]
	for view in views:
		cam.global_position = view[1]
		cam.look_at(view[2], Vector3.UP)
		await get_tree().create_timer(0.35).timeout
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		var path := "/tmp/opencode/mep_godot_%s.png" % view[0]
		img.save_png(path)
		print("MEP_SHOT ", view[0], " ", img.get_width(), "x", img.get_height())
	get_tree().quit()
