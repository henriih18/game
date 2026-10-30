extends Node

var passes := 0
var fails := 0

func _ready() -> void:
	await get_tree().process_frame
	var scene: Node = load("res://scenes/fm/vertical_slice.tscn").instantiate()
	add_child(scene)
	for i in 8:
		await get_tree().process_frame
	await get_tree().physics_frame
	await get_tree().physics_frame

	_check(scene.player != null, "player existe")
	_check(scene.watcher != null, "watcher existe")
	_check(scene.artifact != null, "artefacto existe")
	_check(scene.extraction != null, "extraccion existe")
	_check(get_tree().get_nodes_in_group("fm_hiding_spot").size() >= 2, "hay al menos dos escondites")
	_check(scene.hud != null, "HUD existe")
	_check(scene.player.flashlight_on, "la linterna empieza encendida")

	# Observación: el jugador mira al Vigilante.
	scene.player.global_position = Vector3(0, 0.1, 2.0)
	scene.player.rotation.y = 0.0
	scene.watcher.global_position = Vector3(0, 0.1, -2.0)
	scene.watcher.state = FMWatcher.State.PATROL
	await get_tree().physics_frame
	await get_tree().physics_frame
	_check(scene.player.is_observing(scene.watcher), "el jugador puede observar al Vigilante")
	_check(scene.watcher.is_observed(), "el Vigilante detecta que lo observan")
	await get_tree().physics_frame
	_check(scene.watcher.velocity.length() < 0.01, "el Vigilante se detiene al ser observado")

	# Recogida del núcleo.
	scene.player.global_position = Vector3(-5.9, 0.1, 3.0)
	scene.player.rotation.y = 0.0
	await get_tree().physics_frame
	scene.player._interact()
	await get_tree().physics_frame
	_check(scene.player.carried_item == scene.artifact, "el jugador recoge el nucleo")

	# Escondite.
	var spot = get_tree().get_nodes_in_group("fm_hiding_spot")[0] as FMHidingSpot
	scene.player.carried_item.drop()
	scene.player.carried_item = null
	scene.player.global_position = spot.global_position + Vector3(1.4, 0, 0)
	await get_tree().physics_frame
	spot.hide_player(scene.player)
	await get_tree().physics_frame
	_check(scene.player.hidden, "el jugador se esconde")
	scene.player.exit_hide()
	await get_tree().physics_frame
	_check(not scene.player.hidden, "el jugador sale del escondite")

	# Extracción: recoger de nuevo y llegar al pad.
	scene.watcher.set_physics_process(false)
	scene.player.global_position = scene.artifact.global_position + Vector3(0.5, 0, 0)
	await get_tree().physics_frame
	scene.player._interact()
	await get_tree().physics_frame
	scene.player.global_position = scene.extraction.global_position + Vector3(0, 0.1, 0)
	for i in 8:
		await get_tree().process_frame
	await get_tree().physics_frame
	_check(scene.state == 1, "la extraccion completa la partida")
	_check(scene.hud._overlay.visible, "se muestra el overlay de victoria")

	print("FM_SLICE_TEST: %d PASS / %d FAIL" % [passes, fails])
	get_tree().quit(0 if fails == 0 else 1)

func _check(condition: bool, label: String) -> void:
	if condition:
		passes += 1
		print("PASS  ", label)
	else:
		fails += 1
		print("FAIL  ", label)
