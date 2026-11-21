extends Node

## Persecución real en Recepción: el Vigilante debe ver al jugador, pasar a
## CHASE, acercarse y capturarlo. No prueba navmesh ni multijugador.
## godot --headless --path . tests/fm_vslice_chase.tscn

var scene
var passes := 0
var fails := 0


func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var packed: PackedScene = load("res://scenes/fm/fm_vslice_z10.tscn")
	if packed == null:
		print("FM_VSLICE_CHASE: FAIL (escena no encontrada)")
		get_tree().quit(1)
		return
	scene = packed.instantiate()
	add_child(scene)
	var guard := 0
	while not scene.level_ready and guard < 600:
		await get_tree().process_frame
		guard += 1
	if not scene.level_ready:
		_fail("la escena no terminó de cargar")
		_finish()
		return

	scene.watcher.set_physics_process(false)
	await _wait(0.3)

	# Transición real: activa al Vigilante en Recepción.
	scene.player.global_position = Vector3(68.0, 0.12, -21.0)
	scene.player.rotation.y = PI * 0.5
	var started: bool = scene.transition_door.interact(scene.player)
	_check("chase_transition_started", started)
	await _wait(2.0)
	_check("chase_in_reception", scene.current_area == "RECEPTION")
	_check("chase_watcher_active", not scene.is_watcher_suspended() and scene.watcher.is_physics_processing())

	# Escenario controlado: jugador de espaldas al Vigilante, a 7 m.
	scene.player.global_position = Vector3(-93.0, 0.12, 22.0)
	scene.player.rotation.y = 0.0
	scene.player.camera.rotation.x = 0.0
	scene.player.camera.rotation.y = 0.0
	scene.player.hidden = false
	scene.player.velocity = Vector3.ZERO
	var patrol: Array[Vector3] = [Vector3(-93.0, 0.12, 29.0)]
	scene.watcher.activate_in_sector(Vector3(-93.0, 0.12, 29.0), patrol, 0.0)
	await get_tree().physics_frame
	await get_tree().physics_frame

	var chase_seen := false
	var seen_elapsed := 0.0
	while seen_elapsed < 2.0:
		await get_tree().physics_frame
		seen_elapsed += get_physics_process_delta_time()
		if int(scene.watcher.state) == 3:
			chase_seen = true
			break
	print("CHASE_SEEN seen=%s state=%d observed=%s distance=%.2f" % [
		str(chase_seen), int(scene.watcher.state), str(scene.watcher.observed),
		scene.watcher.global_position.distance_to(scene.player.global_position),
	])
	_check("chase_seen", chase_seen)
	_check("chase_not_observed", not scene.watcher.observed)

	var chase_distance_start: float = scene.watcher.global_position.distance_to(scene.player.global_position)
	await _wait(0.8)
	var chase_distance_mid: float = scene.watcher.global_position.distance_to(scene.player.global_position)
	print("CHASE_APPROACH start=%.2f mid=%.2f delta=%.2f" % [
		chase_distance_start, chase_distance_mid, chase_distance_start - chase_distance_mid,
	])
	_check("chase_approaches", chase_distance_start - chase_distance_mid > 0.8)

	var caught := false
	var caught_elapsed := 0.0
	while caught_elapsed < 5.0:
		await get_tree().physics_frame
		caught_elapsed += get_physics_process_delta_time()
		if int(scene.state) == 2:
			caught = true
			break
	var catch_distance: float = scene.watcher.global_position.distance_to(scene.player.global_position)
	print("CHASE_CATCH caught=%s state=%d distance=%.2f elapsed=%.2f" % [
		str(caught), int(scene.state), catch_distance, caught_elapsed,
	])
	_check("chase_caught", caught)
	_check("chase_catch_distance", catch_distance <= scene.watcher.catch_distance + 0.35)
	_check("chase_player_not_hidden", not scene.player.hidden)
	_finish()


func _wait(seconds: float) -> void:
	await get_tree().create_timer(seconds).timeout


func _check(label: String, condition: bool) -> void:
	if condition:
		passes += 1
		print("PASS %s" % label)
	else:
		fails += 1
		print("FAIL %s" % label)


func _fail(reason: String) -> void:
	fails += 1
	print("FAIL %s" % reason)


func _finish() -> void:
	print("FM_VSLICE_CHASE: %s (%d PASS / %d FAIL)" % ["PASS" if fails == 0 else "FAIL", passes, fails])
	get_tree().quit(0 if fails == 0 else 1)
