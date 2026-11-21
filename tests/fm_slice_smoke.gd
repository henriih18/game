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

	# Puerta de seguridad: cerrada, bloquea y se abre con E.
	_check(scene.security_door != null and not scene.security_door.is_open, "la puerta empieza cerrada")
	_check(scene.security_door._leaves[0].collision_layer != 0, "la puerta cerrada bloquea el paso")
	scene.watcher.set_physics_process(false)
	scene.watcher.global_position = Vector3(0, 0.1, -5.0)
	scene.watcher.state = FMWatcher.State.PATROL
	scene.player.global_position = Vector3(0, 0.1, -8.0)
	scene.player.rotation.y = 0.0
	await get_tree().physics_frame
	_check(scene.player.get_interaction_prompt() == "E   ABRIR PUERTA DE SEGURIDAD", "la puerta muestra su prompt")
	scene.player._interact()
	await get_tree().physics_frame
	_check(scene.security_door.is_open and scene.security_door._leaves[0].collision_layer == 0, "la puerta se abre y deja pasar")
	_check(scene.watcher.state == FMWatcher.State.INVESTIGATE, "abrir la puerta atrae al Vigilante")

	# Batería: recarga la linterna y desaparece.
	var battery: FMBattery = scene.batteries[0]
	scene.player.battery = 10.0
	scene.player.global_position = Vector3(-3.8, 0.1, 0.9)
	scene.player.rotation.y = 0.0
	await get_tree().physics_frame
	scene.player._interact()
	await get_tree().physics_frame
	_check(scene.player.battery > 50.0, "la bateria recarga la linterna")
	_check(not is_instance_valid(battery), "la bateria recogida desaparece")

	# Trampa sonora: emite ruido y atrae al Vigilante.
	scene.watcher.global_position = Vector3(1.15, 0.1, 8.5)
	scene.watcher.state = FMWatcher.State.PATROL
	scene.noise_trap.trigger()
	await get_tree().physics_frame
	_check(scene.noise_trap.triggered, "la trampa sonora se activa")
	_check(scene.watcher.state == FMWatcher.State.INVESTIGATE, "la trampa atrae al Vigilante")

	# Audio ambiental 3D en loop.
	_check(scene.ambience != null and scene.ambience.playing, "el audio ambiental esta sonando")
	_check(scene.ambience.stream is AudioStreamWAV and scene.ambience.stream.loop_mode == AudioStreamWAV.LOOP_FORWARD, "el audio ambiental tiene loop")

	# Observación: el jugador mira al Vigilante.
	scene.watcher.set_physics_process(true)
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
