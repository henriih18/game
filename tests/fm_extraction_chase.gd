extends Node

## Extracción bajo persecución real.
##
## No aísla la visión del Vigilante: comprueba que puede ver al jugador,
## pasar a CHASE y acercarse mientras la extracción se activa y completa.
## El objetivo es validar que la entrega es posible bajo presión y que la
## captura no ocurre antes de que termine la secuencia.

const SCENE := preload("res://scenes/fm/fm_vslice_z10.tscn")

var scene: Node
var passes := 0
var fails := 0

func _ready() -> void:
	scene = SCENE.instantiate()
	add_child(scene)
	while not scene.level_ready:
		await get_tree().process_frame
	await _wait(0.5)

	# Transición real con el núcleo en manos.
	scene.watcher.set_physics_process(false)
	scene.reception_watcher_enabled = true
	scene.player.global_position = Vector3(68.0, 0.12, -21.0)
	scene.player.rotation.y = PI * 0.5
	var core: FMCarryItem = scene.carry_items[0]
	core.carried_by = scene.player
	core.freeze = true
	scene.player.carried_item = core
	var started: bool = scene.transition_door.interact(scene.player)
	_check("transition_started", started)
	await _wait(2.0)
	_check("reception_area", scene.current_area == "RECEPTION")
	_check("watcher_active", not scene.is_watcher_suspended() and scene.watcher.is_physics_processing())

	# El jugador ya está dentro de la zona de extracción, con el núcleo.
	# El Vigilante está 8 m al norte, mirando al sur, con visión normal.
	scene.extraction.activation_time_s = 0.4
	scene.extraction.sequence_duration_s = 0.8
	scene.extraction.door_open_s = 0.2
	scene.extraction.door_hold_s = 0.2
	scene.extraction.door_close_s = 0.1
	scene.extraction.travel_s = 0.1
	scene.extraction.arrival_confirm_s = 0.1
	scene.player.global_position = Vector3(-94.0, 0.12, 36.0)
	scene.player.rotation.y = PI
	scene.player.velocity = Vector3.ZERO
	var watcher_route: Array[Vector3] = [Vector3(-94.0, 0.12, 28.0)]
	scene.watcher.activate_in_sector(
		Vector3(-94.0, 0.12, 28.0),
		watcher_route,
		PI
	)
	await get_tree().physics_frame
	await get_tree().physics_frame

	var start_distance: float = scene.watcher.global_position.distance_to(scene.player.global_position)
	await _wait(0.45)
	var chase_state: int = int(scene.watcher.state)
	var mid_distance: float = scene.watcher.global_position.distance_to(scene.player.global_position)
	print("EXTRACT_CHASE state=%d start=%.2f mid=%.2f player_state=%d" % [
		chase_state, start_distance, mid_distance, int(scene.state)
	])
	_check("watcher_chase", chase_state == FMWatcher.State.CHASE)
	_check("watcher_approaches", mid_distance < start_distance - 0.3)

	var waited := 0.0
	while int(scene.state) == 0 and waited < 4.0:
		await _wait(0.2)
		waited += 0.2
	print("EXTRACT_RESULT state=%d delivered=%d carried=%s" % [
		int(scene.state),
		scene.get_delivered_loot_count(scene.EXTRACTION_CENTER, 2.4),
		str(scene.player.carried_item != null),
	])
	_check("player_not_caught", int(scene.state) != 2)
	_check("extraction_completed", int(scene.state) == 1)
	_check("mission_delivered", scene.get_delivered_loot_count(scene.EXTRACTION_CENTER, 2.4) >= 1)

	_finish()

func _wait(seconds: float) -> void:
	await get_tree().create_timer(seconds).timeout
	await get_tree().physics_frame

func _check(check_name: String, condition: bool) -> void:
	if condition:
		passes += 1
		print("EXTRACT_CHASE_TEST: %s OK" % check_name)
	else:
		fails += 1
		printerr("EXTRACT_CHASE_TEST: %s FAIL" % check_name)

func _finish() -> void:
	if fails == 0:
		print("FM_EXTRACTION_CHASE: PASS (%d PASS / 0 FAIL)" % passes)
		get_tree().quit(0)
	else:
		print("FM_EXTRACTION_CHASE: FAIL (%d PASS / %d FAIL)" % [passes, fails])
		get_tree().quit(1)
