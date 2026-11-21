extends Node

## Escondite de Recepción: el Vigilante debe perder al jugador al ocultarse
## en las taquillas de personal. Ejecutar:
## godot --headless --path . tests/fm_reception_hide.tscn

var scene: Node
var _passes := 0
var _fails := 0

func _ready() -> void:
	var packed: PackedScene = load("res://scenes/fm/fm_vslice_z10.tscn")
	scene = packed.instantiate()
	add_child(scene)
	var guard := 0
	while not scene.level_ready and guard < 600:
		await get_tree().process_frame
		guard += 1
	await get_tree().create_timer(0.5).timeout

	# Evitar que el Vigilante de Z10 o el de Recepción interfieran durante
	# la transición; después se activa el de Recepción a mano.
	scene.watcher.set_physics_process(false)
	scene.reception_watcher_enabled = false
	scene.player.global_position = Vector3(68.0, 0.12, -21.0)
	scene.player.rotation.y = PI * 0.5
	scene.transition_door.interact(scene.player)
	await get_tree().create_timer(2.0).timeout
	_check("reception_area", scene.current_area == "RECEPTION")

	var spot: FMHidingSpot = scene.reception_hiding_spot
	_check("reception_hide_spot", spot != null)
	if spot == null:
		_finish()
		return
	_check("hide_spot_display", spot.display_name == "TAQUILLAS DE PERSONAL")
	_check("hide_spot_position", spot.global_position.distance_to(Vector3(-106.0, 0.05, 38.8)) < 0.1)

	scene.player.global_position = Vector3(-106.0, 0.12, 38.0)
	scene.player.rotation.y = PI
	scene.player.velocity = Vector3.ZERO
	await get_tree().physics_frame
	_check("hide_spot_can_use", spot.can_use(scene.player))

	# El Vigilante arranca al este y mira al oeste; ve al jugador antes de
	# que se esconda. Cuando entra en la taquilla debe perderlo.
	var watcher_route: Array[Vector3] = [Vector3(-102.0, 0.12, 38.0)]
	scene.watcher.activate_in_sector(Vector3(-102.0, 0.12, 38.0), watcher_route, PI * 0.5)
	await _wait(0.45)
	_check("watcher_sees_before_hide", int(scene.watcher.state) == int(FMWatcher.State.CHASE))

	scene.player._try_hide()
	_check("player_hides", scene.player.hidden)
	await _wait(2.0)
	print("RECEPTION_HIDE watcher_state=%d game_state=%d hidden=%s" % [
		int(scene.watcher.state), int(scene.state), str(scene.player.hidden)
	])
	_check("watcher_loses_player", int(scene.watcher.state) != int(FMWatcher.State.CHASE))
	_check("player_not_caught", int(scene.state) == 0)
	scene.player.exit_hide()
	_check("player_exits_hide", not scene.player.hidden)
	_finish()

func _wait(seconds: float) -> void:
	await get_tree().create_timer(seconds).timeout

func _check(name: String, condition: bool) -> void:
	if condition:
		_passes += 1
		print("RECEPTION_HIDE_TEST: %s OK" % name)
	else:
		_fails += 1
		print("RECEPTION_HIDE_TEST: %s FAIL" % name)

func _finish() -> void:
	print("FM_RECEPTION_HIDE: %s (%d PASS / %d FAIL)" % [
		"PASS" if _fails == 0 else "FAIL", _passes, _fails
	])
	get_tree().quit(0 if _fails == 0 else 1)
