extends Node

## Capturas finales por sala, con y sin linterna. Escribe en /tmp/opencode.

func _ready() -> void:
	var scene = load("res://scenes/fm/level1.tscn").instantiate()
	add_child(scene)
	await get_tree().create_timer(3.0).timeout
	if scene.hud != null:
		scene.hud.visible = false
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var views := [
		["rec_wide", Vector3(-12.0, -5.6, -2.35), 0.0, -0.03],
		["rec_counter", Vector3(-12.0, -5.6, -4.60), 0.0, -0.10],
		["rec_logo", Vector3(-12.0, -5.6, -6.20), 0.08, 0.08],
		["rec_directory", Vector3(-17.35, -5.6, -6.20), 1.5708, -0.02],
		["rec_office_door", Vector3(-5.0, -5.6, -3.30), 0.80, 0.0],
		["aseo", Vector3(-6.30, -5.6, -2.55), 0.0, -0.02],
		["office", Vector3(-6.25, -5.6, -5.00), 0.0, -0.02],
		["corr_west", Vector3(-21.0, -5.6, 0.0), -1.5708, -0.02],
		["corr_mid", Vector3(-0.5, -5.6, 0.0), -1.5708, -0.02],
		["corr_east", Vector3(20.0, -5.6, 0.0), 1.5708, -0.02],
		["corr_detail", Vector3(-6.0, -5.6, 0.8), -1.5708, 0.16],
		["sec_entry", Vector3(2.1, -5.6, -2.75), 0.0, 0.0],
		["sec_desk", Vector3(2.1, -5.6, -4.40), 0.0, 0.0],
		["sec_back", Vector3(2.1, -5.6, -7.10), 3.14159, 0.0],
		["sec_rack", Vector3(4.9, -5.6, -6.50), -0.70, 0.0],
		["ctl_entry", Vector3(12.1, -5.6, -2.75), 0.0, 0.0],
		["ctl_console", Vector3(11.2, -5.6, -6.00), 1.5708, 0.0],
		["ctl_back", Vector3(12.1, -5.6, -7.30), 3.14159, 0.0],
		["vest_entry", Vector3(-14.9, -5.6, 2.55), 3.14159, 0.0],
		["vest_lockers", Vector3(-14.0, -5.6, 5.00), 3.14159, 0.0],
		["vest_bench", Vector3(-12.0, -5.6, 7.90), 0.0, -0.05],
		["store_entry", Vector3(-2.9, -5.6, 2.55), 3.14159, 0.0],
		["store_shelves", Vector3(-2.9, -5.6, 5.80), 3.14159, 0.0],
		["store_hoist", Vector3(-4.8, -5.6, 4.80), -1.30, 0.10],
		["maint_entry", Vector3(12.1, -5.6, 2.55), 3.14159, 0.0],
		["maint_gen", Vector3(12.1, -5.6, 4.50), 3.14159, 0.0],
		["maint_boiler", Vector3(15.0, -5.6, 5.60), -2.40, 0.0],
		["maint_bench", Vector3(8.0, -5.6, 6.50), 2.50, 0.0],
	]
	var dark_views := [
		["dark_rec", Vector3(-12.0, -5.6, -2.35), 0.0, -0.03],
		["dark_corridor", Vector3(-0.5, -5.6, 0.0), -1.5708, -0.02],
		["dark_security", Vector3(2.1, -5.6, -4.40), 0.0, 0.0],
		["dark_vest", Vector3(-14.9, -5.6, 2.55), 3.14159, 0.0],
		["dark_storage", Vector3(-2.9, -5.6, 2.55), 3.14159, 0.0],
		["dark_maintenance", Vector3(12.1, -5.6, 2.55), 3.14159, 0.0],
	]
	for view in views:
		if scene.player == null:
			break
		scene.player.battery = 1.0
		scene.player.flashlight_on = true
		scene.player.flashlight.visible = true
		scene.player.global_position = view[1]
		scene.player.rotation.y = view[2]
		scene.player.camera.rotation.x = view[3]
		scene.player.camera.rotation.y = 0.0
		await get_tree().create_timer(0.45).timeout
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		img.save_png("/tmp/opencode/final_%s.png" % view[0])
		print("FINAL_SHOT ", view[0])
	for view in dark_views:
		if scene.player == null:
			break
		scene.player.flashlight_on = false
		scene.player.flashlight.visible = false
		scene.player.global_position = view[1]
		scene.player.rotation.y = view[2]
		scene.player.camera.rotation.x = view[3]
		scene.player.camera.rotation.y = 0.0
		await get_tree().create_timer(0.45).timeout
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		img.save_png("/tmp/opencode/final_%s.png" % view[0])
		print("FINAL_SHOT ", view[0])
	get_tree().quit()
