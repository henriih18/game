extends Node

## Recorrido end-to-end del vertical slice con movimiento real:
## spawn Z10 → núcleo → enlace de servicio → recepción → extracción.
## El Vigilante se desactiva para que la prueba mida navegación, no combate.
## godot --headless --path . tests/fm_vslice_walk.tscn

var scene
var passes := 0
var fails := 0


func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var packed: PackedScene = load("res://scenes/fm/fm_vslice_z10.tscn")
	scene = packed.instantiate()
	add_child(scene)
	var guard := 0
	while not scene.level_ready and guard < 600:
		await get_tree().process_frame
		guard += 1
	await get_tree().create_timer(1.0).timeout
	scene.watcher.set_physics_process(false)
	scene.reception_watcher_enabled = false
	await get_tree().physics_frame

	var route_z10: Array[Vector3] = [
		Vector3(47.0, 0.12, -22.0),
		Vector3(52.0, 0.12, -21.4),
		Vector3(55.7, 0.12, -21.4),
	]
	for point in route_z10:
		await _walk_to(point, 9.0, "z10_%s" % str(point))

	scene.player.rotation.y = -PI * 0.5
	scene.player.camera.rotation.x = 0.0
	await get_tree().physics_frame
	var picked: bool = scene.player._try_pickup()
	_check("walk_pickup", picked and scene.player.carried_item != null)
	if not picked:
		_finish()
		return

	var route_link: Array[Vector3] = [
		Vector3(58.2, 0.12, -21.4),
		Vector3(61.4, 0.12, -21.0),
		Vector3(67.4, 0.12, -21.0),
	]
	for point in route_link:
		await _walk_to(point, 9.0, "link_%s" % str(point))

	_press_action("interact")
	await get_tree().physics_frame
	var door_ok: bool = int(scene.state) == 3
	_check("walk_transition", door_ok)
	await get_tree().create_timer(2.2).timeout
	_check("walk_reception", scene.current_area == "RECEPTION" and scene.player.global_position.distance_to(scene.RECEPTION_SPAWN) < 0.6)
	_check("walk_reception_watcher_off", scene.is_watcher_suspended() and not scene.watcher.is_physics_processing())

	# x=-90 tiene una columna estructural en z=20; el pasillo se recorre por -93.
	var route_reception: Array[Vector3] = [
		Vector3(-90.0, 0.12, 13.0),
		Vector3(-93.0, 0.12, 16.5),
		Vector3(-93.0, 0.12, 24.0),
		Vector3(-92.0, 0.12, 32.0),
		Vector3(-94.0, 0.12, 36.4),
	]
	for point in route_reception:
		await _walk_to(point, 14.0, "reception_%s" % str(point))

	# Sin atajos: se usa la secuencia real de FMReceptionExtraction (8,7 s).
	await get_tree().create_timer(10.0).timeout
	print("WALK_END state=%d pos=%s carried=%s delivered=%d" % [
		int(scene.state), str(scene.player.global_position), str(scene.player.carried_item != null),
		scene.get_delivered_loot_count(scene.EXTRACTION_CENTER, 2.4),
	])
	_check("walk_extraction", int(scene.state) == 1)
	_finish()


func _walk_to(target: Vector3, timeout: float, label: String) -> void:
	var elapsed := 0.0
	var best: float = scene.player.global_position.distance_to(target)
	var stuck_time := 0.0
	while elapsed < timeout:
		var offset: Vector3 = target - scene.player.global_position
		offset.y = 0.0
		var distance: float = offset.length()
		if distance < 0.7:
			break
		scene.player.rotation.y = atan2(-offset.x, -offset.z)
		Input.action_press("move_up")
		await get_tree().physics_frame
		elapsed += get_physics_process_delta_time()
		if scene.player.global_position.distance_to(target) < best - 0.02:
			best = scene.player.global_position.distance_to(target)
			stuck_time = 0.0
		else:
			stuck_time += get_physics_process_delta_time()
			if stuck_time > 2.5:
				break
	Input.action_release("move_up")
	await get_tree().physics_frame
	var final_distance: float = scene.player.global_position.distance_to(target)
	var ok := final_distance < 0.9
	print("WALK %s ok=%s distance=%.2f time=%.1f pos=%s" % [label, str(ok), final_distance, elapsed, str(scene.player.global_position)])
	_check("walk_%s" % label, ok)


func _press_action(action: String) -> void:
	var event := InputEventAction.new()
	event.action = action
	event.pressed = true
	scene.player._unhandled_input(event)


func _check(label: String, condition: bool) -> void:
	if condition:
		passes += 1
		print("PASS %s" % label)
	else:
		fails += 1
		print("FAIL %s" % label)


func _finish() -> void:
	print("FM_VSLICE_WALK: %s (%d PASS / %d FAIL)" % ["PASS" if fails == 0 else "FAIL", passes, fails])
	get_tree().quit(0 if fails == 0 else 1)
