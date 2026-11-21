extends Node

## Capturas finales de conjunto del Nivel 1 V06.
## Cámara libre con una lámpara de verificación suave para leer las zonas
## oscuras. No modifica la escena; solo escribe PNG en /tmp/opencode.

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
	if scene.hud != null and is_instance_valid(scene.hud):
		scene.hud.visible = false

	var cam := Camera3D.new()
	cam.fov = 68.0
	cam.near = 0.04
	cam.far = 140.0
	scene.add_child(cam)
	cam.current = true
	var lamp := OmniLight3D.new()
	lamp.omni_range = 10.0
	lamp.light_energy = 1.9
	lamp.light_color = Color(0.86, 0.92, 1.0)
	lamp.shadow_enabled = false
	cam.add_child(lamp)

	var views := [
		["z10_corridor", Vector3(58.0, 1.65, -21.0), Vector3(52.0, 1.10, -13.0), 4.0],
		["reception", Vector3(-98.0, 1.55, 16.0), Vector3(-102.0, 1.05, 13.7), 4.5],
		["security_interior", Vector3(-89.0, 1.70, -18.0), Vector3(-89.0, 1.20, -31.0)],
		["control_entry", Vector3(-94.0, 1.70, -43.8), Vector3(-94.0, 1.30, -55.0)],
		["vestuarios", Vector3(43.0, 1.70, -50.0), Vector3(56.0, 1.20, -50.0)],
		["warehouse_aisle", Vector3(82.0, 1.70, -13.0), Vector3(96.0, 1.20, -28.0)],
		["warehouse_mezzanine", Vector3(84.0, 1.70, -24.0), Vector3(91.0, 2.80, -30.5)],
		["maintenance_boilers", Vector3(75.0, 1.70, 19.0), Vector3(80.0, 1.10, 25.0)],
		["offices_open", Vector3(-28.0, 1.70, -46.0), Vector3(-12.0, 1.20, -50.0)],
		["offices_meeting", Vector3(8.5, 1.70, -59.5), Vector3(8.5, 1.20, -66.5)],
		["restroom", Vector3(20.0, 1.70, -49.0), Vector3(27.0, 1.20, -50.0)],
		["stairs_main", Vector3(-2.0, 0.50, 33.0), Vector3(-2.0, -4.40, 42.0)],
		["stairs_e1", Vector3(115.0, 1.25, -13.2), Vector3(115.0, -4.20, -20.5)],
		["stairs_e2", Vector3(117.0, 1.25, 33.6), Vector3(117.0, -4.20, 27.0)],
		["security_connector", Vector3(-89.0, 1.70, -2.8), Vector3(-89.0, 1.30, -9.5)],
		["maint_tunnel", Vector3(28.0, 1.00, 19.5), Vector3(54.0, 0.80, 19.5)],
		["north_gallery", Vector3(-32.0, 1.00, -65.5), Vector3(-78.0, 0.80, -65.5)],
	]
	for view in views:
		lamp.light_energy = float(view[3]) if view.size() > 3 else 1.9
		cam.global_position = view[1]
		cam.look_at(view[2], Vector3.UP)
		await get_tree().create_timer(0.35).timeout
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		var path := "/tmp/opencode/final_godot_%s.png" % view[0]
		img.save_png(path)
		print("FINAL_SHOT ", view[0], " ", img.get_width(), "x", img.get_height())
	get_tree().quit()
