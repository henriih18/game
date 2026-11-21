extends Node

## Capturas de las seis puertas cerradas/abiertas y detalles de mecanismos.

func _ready() -> void:
	var packed := load("res://scenes/fm/level1.tscn")
	var scene = packed.instantiate()
	add_child(scene)
	while not scene.level_ready:
		await get_tree().physics_frame
	if scene.watcher != null:
		scene.watcher.set_process(false)
		scene.watcher.set_physics_process(false)
		scene.watcher.visible = false
	await get_tree().create_timer(1.0).timeout
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var doors: Array = scene.find_children("Door_*", "Node3D", true, false)
	var by_id := {}
	for d in doors:
		by_id[d.door_id] = d

	var order := ["RECEPCION", "SEGURIDAD", "CONTROL", "ALMACEN", "VESTUARIOS", "MANTENIMIENTO"]
	for id in order:
		for open_state in [false, true]:
			for d in doors:
				d.set_open(false, true)
			var door = by_id[id]
			if open_state:
				door.set_open(true, true)
			var north: bool = door.global_position.z < 0.0
			var x: float = door.global_position.x + door.width * 0.5
			scene.player.global_position = Vector3(x, -5.60, 1.45 if north else -1.45)
			scene.player.rotation.y = 0.0 if north else PI
			scene.player.camera.rotation.x = -0.04
			scene.player.camera.rotation.y = 0.0
			await get_tree().create_timer(0.55).timeout
			await RenderingServer.frame_post_draw
			var img := get_viewport().get_texture().get_image()
			var name := "door_%s_%s" % [id.to_lower(), "open" if open_state else "closed"]
			img.save_png("/tmp/opencode/%s.png" % name)
			print("DOOR_SHOT ", name, " ", img.get_width(), "x", img.get_height())

	# Detalle del teclado de seguridad y de la liberacion de mantenimiento.
	var seg = by_id["SEGURIDAD"]
	scene.player.global_position = Vector3(seg.global_position.x + 1.95, -5.60, 0.55)
	scene.player.rotation.y = 0.0
	scene.player.camera.rotation.x = -0.12
	await get_tree().create_timer(0.4).timeout
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("/tmp/opencode/door_seguridad_keypad.png")
	print("DOOR_SHOT door_seguridad_keypad")

	var maint = by_id["MANTENIMIENTO"]
	scene.player.global_position = Vector3(maint.global_position.x + 1.90, -5.60, -0.45)
	scene.player.rotation.y = PI
	scene.player.camera.rotation.x = -0.10
	await get_tree().create_timer(0.4).timeout
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("/tmp/opencode/door_mantenimiento_release.png")
	print("DOOR_SHOT door_mantenimiento_release")
	get_tree().quit()
