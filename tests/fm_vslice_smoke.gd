extends Node

## Prueba headless del vertical slice local de Z10 + Recepción.
## godot --headless --path . tests/fm_vslice_smoke.tscn

var scene
var passes := 0
var fails := 0


func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var packed: PackedScene = load("res://scenes/fm/fm_vslice_z10.tscn")
	if packed == null:
		print("FM_VSLICE_TEST: FAIL (escena no encontrada)")
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

	# El Vigilante no debe interferir con las pruebas de movimiento/objetos.
	scene.watcher.set_physics_process(false)
	await _wait(0.4)
	await get_tree().physics_frame

	print("TEST_ART z10_meshes=%d reception_meshes=%d" % [
		scene.z10_root.find_children("*", "MeshInstance3D", true, false).size(),
		scene.reception_root.find_children("*", "MeshInstance3D", true, false).size(),
	])
	_check("art_roots", scene.z10_root != null and scene.reception_root != null)
	_check("art_meshes", scene.z10_root.find_children("*", "MeshInstance3D", true, false).size() > 500 and scene.reception_root.find_children("*", "MeshInstance3D", true, false).size() > 280)
	print("TEST_COLLIDERS z10=%d reception=%d" % [scene._z10_collider_count, scene._reception_collider_count])
	_check("colliders", scene._z10_collider_count > 250 and scene._reception_collider_count > 140)

	var spawn_floor := _ray(Vector3(42.2, 1.5, -22.0), Vector3(42.2, -1.0, -22.0))
	var reception_floor := _ray(Vector3(-90.0, 1.5, 10.0), Vector3(-90.0, -1.0, 10.0))
	print("TEST_FLOOR z10=%s reception=%s" % [str(spawn_floor.get("position")), str(reception_floor.get("position"))])
	_check("floor_z10", not spawn_floor.is_empty())
	_check("floor_reception", not reception_floor.is_empty())

	_check("player", scene.player != null and is_instance_valid(scene.player))
	if scene.player == null:
		_finish()
		return
	await _wait(1.0)
	print("PROBE_PLAYER pos=%s floor=%s vel=%s state=%d phys=%s" % [
		str(scene.player.global_position), str(scene.player.is_on_floor()),
		str(scene.player.velocity), int(scene.state), str(scene.player.is_physics_processing()),
	])
	_check("player_floor", scene.player.is_on_floor())
	_check("player_camera", scene.player.camera != null and scene.player.camera.current)
	_check("player_flashlight", scene.player.flashlight != null and scene.player.flashlight.visible)
	if DisplayServer.get_name() != "headless":
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
		scene.player._mouse_ignore_time = 0.0
		var yaw_before: float = scene.player.rotation.y
		var look := InputEventMouseMotion.new()
		look.relative = Vector2(24.0, 12.0)
		scene.player._unhandled_input(look)
		var yaw_after: float = scene.player.rotation.y
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		print("TEST_LOOK yaw=%.3f->%.3f" % [yaw_before, yaw_after])
		_check("player_look", absf(yaw_after - yaw_before) > 0.01)
	else:
		print("SKIP player_look (headless sin captura de ratón)")
	_check("art_camera_off", not (scene.get_node("Z10Art/ArtCamera") as Camera3D).current and not (scene.get_node("ReceptionArt/ArtCamera") as Camera3D).current)
	_check("environment", scene.world_env != null and scene.world_env.environment == scene.z10_environment)

	# Movimiento, sprint y crouch en el enlace de servicio (espacio abierto).
	await _move_probe(Vector3(64.0, 0.12, -21.0), -PI * 0.5, false, false)
	var walk_distance: float = _last_distance
	var walk_stamina: float = scene.player.stamina
	await _move_probe(Vector3(64.0, 0.12, -21.0), -PI * 0.5, true, false)
	var sprint_distance: float = _last_distance
	var sprint_stamina: float = scene.player.stamina
	await _move_probe(Vector3(64.0, 0.12, -21.0), -PI * 0.5, false, true)
	var crouch_distance: float = _last_distance
	print("TEST_MOVE walk=%.2f sprint=%.2f crouch=%.2f stamina=%.1f->%.1f" % [walk_distance, sprint_distance, crouch_distance, walk_stamina, sprint_stamina])
	_check("walk", walk_distance > 0.45)
	_check("sprint_faster", sprint_distance > walk_distance * 1.2)
	_check("crouch_slower", crouch_distance < walk_distance * 0.8)
	_check("sprint_stamina", sprint_stamina < walk_stamina)
	_check("crouch_eye", _last_eye < 1.5)

	# Linterna: toggle, consumo y recarga.
	scene.player.global_position = Vector3(64.0, 0.12, -21.0)
	scene.player.flashlight_on = true
	scene.player.battery = 50.0
	var before_battery: float = scene.player.battery
	var toggle := InputEventAction.new()
	toggle.action = "flashlight"
	toggle.pressed = true
	scene.player._unhandled_input(toggle)
	var toggled_off: bool = not scene.player.flashlight_on
	scene.player._update_flashlight(1.0)
	var battery_off: float = scene.player.battery
	scene.player._unhandled_input(toggle)
	scene.player._update_flashlight(1.0)
	var after_drain: float = scene.player.battery
	scene.player.recharge_battery(20.0)
	var after_recharge: float = scene.player.battery
	print("TEST_FLASHLIGHT off=%s battery=%.1f->%.1f->%.1f->%.1f" % [str(toggled_off), before_battery, battery_off, after_drain, after_recharge])
	_check("flashlight_toggle", toggled_off)
	_check("flashlight_idle", is_equal_approx(battery_off, before_battery))
	_check("flashlight_drain", after_drain < battery_off)
	_check("flashlight_recharge", after_recharge > after_drain)

	# Batería recogible del mundo (no solo la API de recarga).
	var battery = scene.get_node("Battery_Workbench")
	var before_pickup: float = scene.player.battery
	var battery_picked: bool = battery.interact(scene.player)
	var after_pickup: float = scene.player.battery
	print("TEST_BATTERY_PICKUP picked=%s battery=%.1f->%.1f" % [str(battery_picked), before_pickup, after_pickup])
	_check("battery_world_pickup", battery_picked and after_pickup > before_pickup)

	# Objeto físico: recoger con la interacción real, transportar y soltar.
	var core = scene.carry_items[0]
	scene.player.global_position = Vector3(55.6, 0.12, -21.4)
	scene.player.rotation.y = -PI * 0.5
	scene.player.camera.rotation.x = 0.0
	await get_tree().physics_frame
	_press_action("interact")
	var picked: bool = scene.player.carried_item == core
	var carried_ok: bool = picked and scene.player.carried_item == core and core.carried_by == scene.player
	await get_tree().physics_frame
	await get_tree().physics_frame
	var anchor: Node3D = scene.player.get_carry_anchor()
	var follow_distance: float = core.global_position.distance_to(anchor.global_position)
	scene.player._drop_item()
	await get_tree().physics_frame
	var dropped_ok: bool = scene.player.carried_item == null and core.carried_by == null
	print("TEST_CARRY picked=%s carried=%s follow=%.2f dropped=%s" % [str(picked), str(carried_ok), follow_distance, str(dropped_ok)])
	_check("carry_pickup", carried_ok)
	_check("carry_follow", follow_distance < 0.8)
	_check("carry_drop", dropped_ok)

	# Escondite interactivo.
	var spot = scene.get_node("HideShelves")
	scene.player.global_position = Vector3(42.5, 0.12, -11.1)
	await get_tree().physics_frame
	_press_action("interact")
	var hide_ok: bool = scene.player.hidden
	var hidden_state: bool = scene.player.hidden and scene.player.collision_layer == 0
	scene.watcher.global_position = scene.player.global_position + Vector3(0.0, 0.0, -2.0)
	var watcher_sees_hidden: bool = scene.watcher._can_see_target(scene.player)
	_check("hide_watcher_ignores", not watcher_sees_hidden)
	_press_action("interact")
	await get_tree().physics_frame
	var exit_ok: bool = not scene.player.hidden and scene.player.collision_layer == 2
	print("TEST_HIDE enter=%s hidden=%s exit=%s pos=%s" % [str(hide_ok), str(hidden_state), str(exit_ok), str(scene.player.global_position)])
	_check("hide_enter", hide_ok and hidden_state)
	_check("hide_exit", exit_ok)

	# Observación directa: el Vigilante queda inmóvil si el jugador lo mira.
	scene.player.global_position = Vector3(64.0, 0.12, -21.0)
	scene.player.rotation.y = -PI * 0.5  # mirando +X, hacia el Vigilante
	scene.player.camera.rotation.x = 0.0
	scene.player.flashlight_on = true
	scene.player.battery = 80.0
	scene.watcher.global_position = Vector3(68.0, 0.12, -21.0)
	scene.watcher.rotation.y = PI * 0.5
	await get_tree().physics_frame
	await get_tree().physics_frame
	var observed: bool = scene.player.is_observing(scene.watcher)
	scene.player.rotation.y = PI * 0.5  # mirando -X, de espaldas
	await get_tree().physics_frame
	await get_tree().physics_frame
	var not_observed: bool = not scene.player.is_observing(scene.watcher)
	print("TEST_OBSERVE seen=%s unseen=%s" % [str(observed), str(not_observed)])
	_check("observe_seen", observed)
	_check("observe_unseen", not_observed)

	# El Vigilante se congela observado y se mueve al perder contacto visual.
	scene.watcher.set_physics_process(true)
	scene.watcher.global_position = Vector3(55.0, 0.12, -21.0)
	scene.watcher.rotation.y = PI * 0.5
	scene.watcher.state = 1
	var patrol: Array[Vector3] = [Vector3(59.0, 0.12, -21.0)]
	scene.watcher.patrol_points = patrol
	scene.watcher.patrol_index = 0
	scene.watcher.target = Vector3(59.0, 0.12, -21.0)
	scene.player.global_position = Vector3(64.0, 0.12, -21.0)
	scene.player.rotation.y = PI * 0.5
	await get_tree().physics_frame
	await get_tree().physics_frame
	var frozen_from: Vector3 = scene.watcher.global_position
	await _wait(0.8)
	var frozen_distance: float = frozen_from.distance_to(scene.watcher.global_position)
	scene.player.rotation.y = -PI * 0.5
	await get_tree().physics_frame
	var moved_from: Vector3 = scene.watcher.global_position
	await _wait(0.8)
	var moved_distance: float = moved_from.distance_to(scene.watcher.global_position)
	print("TEST_WATCHER_FREEZE frozen=%.2f moved=%.2f observed=%s" % [frozen_distance, moved_distance, str(scene.watcher.observed)])
	_check("watcher_frozen", frozen_distance < 0.12)
	_check("watcher_moves", moved_distance > 0.25)
	scene.watcher.set_physics_process(false)

	# Ruido: el Vigilante investiga.
	scene.watcher.state = 1
	scene.emit_noise(scene.watcher.global_position, 8.0, "test")
	var noise_state: int = int(scene.watcher.state)
	print("TEST_NOISE state=%d" % noise_state)
	_check("noise", noise_state == 2)

	# Patrulla real del Vigilante sin que el jugador lo observe.
	scene.player.hidden = true
	scene.watcher.global_position = Vector3(59.0, 0.12, -25.0)
	scene.watcher.state = 1
	var patrol_route: Array[Vector3] = [
		Vector3(59.0, 0.12, -25.0),
		Vector3(45.0, 0.12, -25.0),
		Vector3(45.0, 0.12, -14.5),
		Vector3(59.0, 0.12, -14.5),
	]
	scene.watcher.patrol_points = patrol_route
	scene.watcher.patrol_index = 0
	scene.watcher.target = patrol_route[0]
	scene.watcher.set_physics_process(true)
	var patrol_start: Vector3 = scene.watcher.global_position
	await _wait(20.0)
	var patrol_distance: float = patrol_start.distance_to(scene.watcher.global_position)
	scene.watcher.set_physics_process(false)
	scene.player.hidden = false
	print("TEST_PATROL moved=%.2f pos=%s state=%d" % [patrol_distance, str(scene.watcher.global_position), int(scene.watcher.state)])
	_check("watcher_patrol", patrol_distance > 14.0)

	# Cartel y zona de extracción del ala sur.
	var gate_sign := scene.get_node_or_null("ExtractionGateSign") as Label3D
	_check("extraction_sign", gate_sign != null and gate_sign.text == "SALIDA" and absf(gate_sign.rotation.y - PI) < 0.01)
	var zone_collider := scene.get_node_or_null("ReceptionExtraction/ExtractionZoneCollider") as CollisionShape3D
	var zone_shape: BoxShape3D = null
	if zone_collider != null:
		zone_shape = zone_collider.shape as BoxShape3D
	_check("extraction_zone", zone_shape != null and zone_shape.size.is_equal_approx(Vector3(9.0, 2.6, 8.0)))

	# Transición provisional a recepción, usando la interacción real del enlace.
	scene.player.global_position = Vector3(68.0, 0.12, -21.0)
	scene.player.rotation.y = PI * 0.5
	scene.player.carried_item = core
	core.carried_by = scene.player
	core.freeze = true
	_check("transition_blocking_before", scene.transition_door.is_blocking())
	var transition_prompt: String = scene.transition_door.get_interaction_prompt()
	var transition_started: bool = scene.transition_door.interact(scene.player)
	_check("transition_prompt", "ENLACE" in transition_prompt)
	_check("transition_interact", transition_started)
	_check("transition_state", int(scene.state) == 3)
	scene.player._drop_item()
	_check("transition_input_lock", scene.player.carried_item == core)
	await _wait(2.0)
	print("TEST_TRANSITION area=%s pos=%s env=%s" % [scene.current_area, str(scene.player.global_position), str(scene.world_env.environment == scene.reception_environment)])
	_check("transition_area", scene.current_area == "RECEPTION")
	_check("transition_position", scene.player.global_position.distance_to(scene.RECEPTION_SPAWN) < 0.5)
	_check("transition_env", scene.world_env.environment == scene.reception_environment)
	_check("transition_playing", int(scene.state) == 0)
	print("TEST_WATCHER_RECEPTION pos=%s state=%d patrol=%d y=%.2f suspended=%s" % [
		str(scene.watcher.global_position), int(scene.watcher.state),
		scene.watcher.patrol_points.size(), scene.watcher.global_position.y,
		str(scene.is_watcher_suspended()),
	])
	_check("watcher_reception_active", not scene.is_watcher_suspended() and scene.watcher.is_physics_processing())
	_check("watcher_reception_patrol", scene.watcher.patrol_points.size() >= 6)
	_check("watcher_reception_position", scene.watcher.global_position.x < -88.0 and scene.watcher.global_position.z > 8.0)
	_check("watcher_reception_height", absf(scene.watcher.global_position.y - 0.12) < 0.05)
	var reception_patrol_start: Vector3 = scene.watcher.global_position
	await _wait(3.0)
	var reception_patrol_distance: float = reception_patrol_start.distance_to(scene.watcher.global_position)
	print("TEST_WATCHER_RECEPTION_PATROL moved=%.2f pos=%s" % [reception_patrol_distance, str(scene.watcher.global_position)])
	_check("watcher_reception_moves", reception_patrol_distance > 0.5)
	_check("transition_blocking_after", not scene.transition_door.is_blocking())
	var arrival: StaticBody3D = scene.reception_arrival_door
	var arrival_collider: CollisionShape3D = null
	if arrival != null:
		arrival_collider = arrival.get_node_or_null("ArrivalDoorCollider") as CollisionShape3D
	_check("arrival_door", arrival != null and arrival_collider != null and absf(arrival.global_position.z - 4.0) < 0.01)

	# Extracción placeholder en recepción. Se desactiva la IA para aislar la
	# lógica de entrega: la persecución ya se comprobó en los checks anteriores.
	scene.watcher.set_physics_process(false)
	core.carried_by = null
	scene.player.carried_item = null
	core.freeze = true
	core.global_position = Vector3(-94.0, 0.35, 37.2)
	scene.player.global_position = Vector3(-94.0, 0.12, 36.6)
	scene.player.rotation.y = PI
	await get_tree().physics_frame
	await get_tree().physics_frame
	scene.extraction.activation_time_s = 0.1
	scene.extraction.sequence_duration_s = 0.8
	scene.extraction.door_open_s = 0.1
	scene.extraction.door_hold_s = 0.1
	scene.extraction.door_close_s = 0.1
	scene.extraction.travel_s = 0.1
	await _wait(2.0)
	print("TEST_EXTRACTION state=%d delivered=%d" % [int(scene.state), scene.get_delivered_loot_count(scene.EXTRACTION_CENTER, 2.4)])
	_check("extraction_won", int(scene.state) == 1)

	_finish()


var _last_distance := 0.0
var _last_eye := 1.62


func _move_probe(start: Vector3, yaw: float, sprint: bool, crouch: bool) -> void:
	scene.player.global_position = start
	scene.player.rotation.y = yaw
	scene.player.velocity = Vector3.ZERO
	scene.player.hidden = false
	scene.player.carried_item = null
	await get_tree().physics_frame
	await get_tree().physics_frame
	var before: Vector3 = scene.player.global_position
	Input.action_press("move_up")
	if sprint:
		Input.action_press("sprint")
	if crouch:
		Input.action_press("crouch")
	await _wait(0.4)
	Input.action_release("move_up")
	Input.action_release("sprint")
	Input.action_release("crouch")
	await get_tree().physics_frame
	_last_distance = before.distance_to(scene.player.global_position)
	_last_eye = scene.player.camera.position.y


func _ray(from: Vector3, to: Vector3) -> Dictionary:
	var query := PhysicsRayQueryParameters3D.create(from, to)
	query.collision_mask = 1
	return get_viewport().world_3d.direct_space_state.intersect_ray(query)


func _wait(seconds: float) -> void:
	await get_tree().create_timer(seconds).timeout


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


func _fail(message: String) -> void:
	fails += 1
	print("FAIL %s" % message)


func _finish() -> void:
	print("FM_VSLICE_TEST: %s (%d PASS / %d FAIL)" % ["PASS" if fails == 0 else "FAIL", passes, fails])
	get_tree().quit(0 if fails == 0 else 1)
