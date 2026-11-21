extends Node

## Capturas de verificación de la red de rutas alternativas y del conector
## principal de Seguridad. Cámara libre; solo escribe en /tmp/opencode.

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
	cam.fov = 70.0
	cam.near = 0.04
	cam.far = 120.0
	scene.add_child(cam)
	cam.current = true
	var lamp := OmniLight3D.new()
	lamp.omni_range = 5.5
	lamp.light_energy = 0.9
	lamp.shadow_enabled = false
	cam.add_child(lamp)

	var views := [
		["security_connector", Vector3(-89.0, 1.65, -1.2), Vector3(-89.0, 1.35, -9.4)],
		["security_south_door", Vector3(-89.0, 1.55, -6.2), Vector3(-89.0, 1.35, -13.5)],
		["security_interior", Vector3(-89.0, 1.65, -12.0), Vector3(-89.0, 1.35, -30.0)],
		["security_booth", Vector3(-88.0, 1.65, -20.0), Vector3(-101.0, 1.35, -26.0)],
		["security_access_out", Vector3(-64.0, 1.66, -10.9), Vector3(-76.0, 1.35, -10.9)],
		["east_gallery_warehouse", Vector3(105.0, 1.05, -6.4), Vector3(105.0, 0.85, 3.5)],
		["east_gallery_maintenance", Vector3(105.0, 1.05, 6.4), Vector3(105.0, 0.85, -3.5)],
		["maint_branch", Vector3(20.5, 1.05, 5.2), Vector3(20.5, 0.80, 16.5)],
		["maint_tunnel", Vector3(30.0, 1.05, 19.5), Vector3(54.0, 0.85, 19.5)],
		["north_gallery_control", Vector3(-94.0, 1.05, -59.2), Vector3(-94.0, 0.85, -66.4)],
		["north_gallery_offices", Vector3(-33.0, 1.05, -65.5), Vector3(-80.0, 0.85, -65.5)],
		["offices_crawl", Vector3(-31.5, 1.05, -31.0), Vector3(-39.5, 0.85, -31.0)],
		["reception_stair", Vector3(-68.0, 1.35, 32.0), Vector3(-40.0, 0.95, 32.0)],
		["service_loop", Vector3(59.5, 1.05, -39.2), Vector3(69.0, 0.85, -36.4)],
		["nw_stair", Vector3(-75.0, 3.1, -42.0), Vector3(-70.5, 0.30, -55.0)],
	]
	for view in views:
		cam.global_position = view[1]
		cam.look_at(view[2], Vector3.UP)
		await get_tree().create_timer(0.35).timeout
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		var path := "/tmp/opencode/conn_godot_%s.png" % view[0]
		img.save_png(path)
		print("CONN_SHOT ", view[0], " ", img.get_width(), "x", img.get_height())
	get_tree().quit()
