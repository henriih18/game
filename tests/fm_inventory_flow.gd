extends Node

## Flujo completo con el Vigilante activo en Z10:
## spawn → puesto de análisis a pie → ruido → desmontaje → componentes →
## núcleo → enlace → Recepción → extracción.
##
## La extracción se mide con la IA de Recepción desactivada después de
## comprobar que se activa, para aislar la entrega. La persecución tiene su
## propia prueba en fm_vslice_chase.
##
## godot --headless --path . tests/fm_inventory_flow.tscn

var scene: Node
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
	await get_tree().create_timer(0.6).timeout

	var station: FMDismantlable = scene.dismantlable
	_check("station_exists", station != null and is_instance_valid(station))
	if station == null:
		_finish()
		return
	_check("station_at_expected_position", station.global_position.distance_to(Vector3(51.2, 0.0, -17.2)) < 0.1)
	_check("station_not_reachable_from_spawn", not station.can_interact(scene.player))

	# El Vigilante se coloca al sureste del puesto, mirando al este. No ve al
	# jugador acercarse desde el suroeste, pero está dentro del radio de ruido.
	var watcher_route: Array[Vector3] = [Vector3(54.5, 0.12, -22.0)]
	scene.watcher.activate_in_sector(
		Vector3(54.5, 0.12, -22.0),
		watcher_route,
		-PI * 0.5
	)
	await get_tree().physics_frame

	var route_station: Array[Vector3] = [
		Vector3(46.0, 0.12, -22.0),
		Vector3(50.0, 0.12, -21.8),
		Vector3(51.2, 0.12, -19.6),
		Vector3(51.2, 0.12, -18.2),
	]
	for point in route_station:
		await _walk_to(point, 10.0, "station_%s" % str(point))

	var reachable := station.can_interact(scene.player)
	_check("station_reachable_on_foot", reachable)

	station.dismantle_duration = 0.9
	station.noise_interval = 0.2
	# Aislar la audición: el objetivo es comprobar que el ruido lo atrae, no
	# que además lo vea. La visión se restaura después del check.
	scene.watcher.vision_distance = 0.0
	_press_action("interact")
	await get_tree().physics_frame
	_check("dismantle_started", station.dismantling)
	await _wait(0.45)
	_check("watcher_heard_noise", scene.watcher.state == FMWatcher.State.INVESTIGATE)
	# La atracción ya está comprobada. Se retira al Vigilante para que el
	# desmontaje y el transporte no dependan de una persecución aleatoria.
	scene.watcher.vision_distance = 18.0
	scene.watcher.set_physics_process(false)

	var dismantle_wait := 0.0
	while not station.completed and dismantle_wait < 4.0:
		await _wait(0.2)
		dismantle_wait += 0.2
	_check("dismantle_completed", station.completed)
	_check("four_components", station.components.size() == 4)

	for component in station.components:
		scene.player.global_position = Vector3(component.global_position.x, 0.12, component.global_position.z - 1.2)
		scene.player.velocity = Vector3.ZERO
		await get_tree().physics_frame
		scene.player._try_pickup()
	# Quedar al sur del puesto: el collider del puesto queda al norte y no
	# bloquea la ruta hacia el núcleo.
	scene.player.global_position = Vector3(51.2, 0.12, -19.6)
	scene.player.velocity = Vector3.ZERO
	await get_tree().physics_frame
	_check("components_in_inventory", scene.player.inventory.size() == 4)
	_check("components_weight", absf(scene.player.get_carry_weight() - 2.9) < 0.05)

	await _walk_to(Vector3(55.7, 0.12, -21.4), 8.0, "core")
	scene.player.rotation.y = -PI * 0.5
	await get_tree().physics_frame
	var core_picked: bool = scene.player._try_pickup()
	_check("core_picked", core_picked and scene.player.carried_item != null)
	_check("total_weight", absf(scene.player.get_carry_weight() - 9.9) < 0.05)

	var route_link: Array[Vector3] = [
		Vector3(58.2, 0.12, -21.4),
		Vector3(61.4, 0.12, -21.0),
		Vector3(67.4, 0.12, -21.0),
	]
	for point in route_link:
		await _walk_to(point, 14.0, "link_%s" % str(point))

	_press_action("interact")
	await get_tree().physics_frame
	_check("transition_started", int(scene.state) == 3)
	await get_tree().create_timer(2.2).timeout
	_check("reception_area", scene.current_area == "RECEPTION")
	_check("reception_watcher_active", not scene.is_watcher_suspended() and scene.watcher.is_physics_processing())

	# La activación del Vigilante ya está comprobada. Se desactiva para que la
	# extracción mida la entrega del inventario, no una persecución.
	scene.watcher.set_physics_process(false)

	var route_reception: Array[Vector3] = [
		Vector3(-90.0, 0.12, 13.0),
		Vector3(-93.0, 0.12, 16.5),
		Vector3(-93.0, 0.12, 24.0),
		Vector3(-92.0, 0.12, 32.0),
		Vector3(-94.0, 0.12, 36.4),
	]
	for point in route_reception:
		await _walk_to(point, 16.0, "reception_%s" % str(point))

	await get_tree().physics_frame
	await get_tree().physics_frame
	var delivered: int = scene.get_delivered_loot_count(scene.EXTRACTION_CENTER, 2.4)
	print("FLOW_EXTRACTION delivered=%d inventory=%d carried=%s state=%d" % [
		delivered,
		scene.player.inventory.size(),
		str(scene.player.carried_item != null),
		int(scene.state),
	])
	_check("five_items_delivered", delivered == 5)
	await get_tree().create_timer(10.0).timeout
	_check("extraction_completed", int(scene.state) == 1)
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
	print("FLOW %s ok=%s distance=%.2f time=%.1f pos=%s" % [label, str(ok), final_distance, elapsed, str(scene.player.global_position)])
	_check("flow_%s" % label, ok)

func _press_action(action: String) -> void:
	var event := InputEventAction.new()
	event.action = action
	event.pressed = true
	scene.player._unhandled_input(event)

func _wait(seconds: float) -> void:
	await get_tree().create_timer(seconds).timeout

func _check(name: String, condition: bool) -> void:
	if condition:
		passes += 1
		print("FLOW_TEST: %s OK" % name)
	else:
		fails += 1
		print("FLOW_TEST: %s FAIL" % name)

func _finish() -> void:
	if fails == 0:
		print("FM_INVENTORY_FLOW: PASS (%d PASS / 0 FAIL)" % passes)
		get_tree().quit(0)
	else:
		print("FM_INVENTORY_FLOW: FAIL (%d PASS / %d FAIL)" % [passes, fails])
		get_tree().quit(1)
