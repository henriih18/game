extends SceneTree

var failures := 0

func _init() -> void:
	_run.call_deferred()

func check(condition: bool, label: String) -> void:
	if condition:
		print("PASS: ", label)
	else:
		failures += 1
		print("FAIL: ", label)

func _run() -> void:
	var scene: Node = load("res://scenes/main.tscn").instantiate()
	root.add_child(scene)
	await physics_frame
	await physics_frame

	var p1 = scene.get_node("Players/P1")
	var p2 = scene.get_node("Players/P2")
	var crate = scene.get_node("Crate")
	var zone = scene.get_node("ExtractionZone")

	# 1) P1 agarra solo
	p1.global_position = crate.global_position + Vector2(60, 0)
	await physics_frame
	await physics_frame
	p1._toggle_grab()
	await physics_frame
	check(crate.holder_ids.has(1), "P1 agarra la caja")
	check(crate.holder_count() == 1, "la caja tiene 1 portador")

	# 2) P2 se suma
	p2.global_position = crate.global_position + Vector2(-60, 0)
	await physics_frame
	await physics_frame
	p2._toggle_grab()
	await physics_frame
	check(crate.holder_ids.has(2), "P2 agarra la misma caja")
	check(crate.holder_count() == 2, "la caja tiene 2 portadores")

	# 3) Posición = punto medio + offset
	var expected: Vector2 = (p1.global_position + p2.global_position) / 2.0 + Vector2(0, -46)
	check(crate.global_position.distance_to(expected) < 6.0, "la caja flota en el punto medio")

	# 4) Entregar entre los dos
	p1.global_position = zone.global_position + Vector2(-20, 0)
	p2.global_position = zone.global_position + Vector2(20, 0)
	crate.global_position = (p1.global_position + p2.global_position) / 2.0 + Vector2(0, -46)
	await physics_frame
	await physics_frame
	await physics_frame
	check(scene.crate_delivered == true, "entregar la caja en la zona")
	check(crate.delivered == true, "la caja queda marcada como entregada")
	check(crate.holder_ids.is_empty(), "ambos jugadores sueltan la caja")

	# 5) Gema
	var gem = scene.get_node("Gems/Gem1")
	p1.global_position = gem.global_position
	await physics_frame
	await physics_frame
	check(scene.gems_collected == 1, "recoger una gema")

	# 6) Temporizador corre
	var t0: float = scene.time_left
	await process_frame
	await process_frame
	check(scene.time_left < t0, "el temporizador corre")

	# 7) Cámara detecta y alarma sube
	var cam = scene.get_node("Cameras/Camera1")
	p1.global_position = cam.global_position
	var detected := false
	for i in 12:
		await process_frame
		if cam.triggered:
			detected = true
			break
	check(detected, "la cámara detecta al jugador")
	var alarm_before: float = scene.alarm
	await process_frame
	await process_frame
	await process_frame
	check(scene.alarm > alarm_before, "la alarma sube con jugador en cámara")

	# 8) Alarma baja al salir
	p1.global_position = Vector2(100, 650)
	var cleared := false
	for i in 12:
		await process_frame
		if not cam.triggered:
			cleared = true
			break
	check(cleared, "la cámara deja de detectar")
	scene.alarm = 50.0
	await process_frame
	await process_frame
	await process_frame
	await process_frame
	check(scene.alarm < 50.0, "la alarma baja sin detección")

	# 9) Fin por tiempo agotado
	scene.time_left = 0.01
	await process_frame
	await process_frame
	check(scene.state == 2, "fin de ronda por tiempo (LOST)")
	check(scene.overlay.visible == true, "se muestra el overlay de fin")

	print("RESULT: ", "OK" if failures == 0 else "%d FALLOS" % failures)
	quit(0 if failures == 0 else 1)
