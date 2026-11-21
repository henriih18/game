extends Node

## Partida completa Z10 -> Recepcion con la IA del Vigilante activa y seis
## capturas en ventana de 1280x720.
##
## Reutiliza el recorrido real de tests/fm_full_run.gd: spawn -> puesto de
## analisis a pie -> desmontaje -> componentes -> nucleo -> enlace de servicio
## -> Recepcion -> extraccion real. No hay teletransportes de ruta: el jugador
## se mueve con Input.action_press y el unico salto de posicion es el que
## realiza la propia transicion de sector.
##
## El Vigilante conserva vision_distance=18, no se suspende y se comprueba en
## cada frame que siga con set_physics_process(true). Las capturas usan la
## camara del jugador y recogen la escena, no solo el HUD.
##
## godot --path . tests/fm_full_run_shot.tscn

const SCENE := preload("res://scenes/fm/fm_vslice_z10.tscn")
const STATION_POSITION := Vector3(51.2, 0.0, -17.2)
const STATION_APPROACH := Vector3(51.2, 0.12, -18.2)
const CORE_APPROACH := Vector3(55.7, 0.12, -21.4)
const DOOR_APPROACH := Vector3(67.4, 0.12, -21.0)
const EXTRACTION_APPROACH := Vector3(-94.0, 0.12, 36.4)

const SHOT_STATION := "docs/fm_full_run_01_station.png"
const SHOT_DISMANTLE := "docs/fm_full_run_02_dismantle.png"
const SHOT_CORE := "docs/fm_full_run_03_core.png"
const SHOT_SERVICE_LINK := "docs/fm_full_run_04_service_link.png"
const SHOT_RECEPTION := "docs/fm_full_run_05_reception.png"
const SHOT_EXTRACTION := "docs/fm_full_run_06_extraction.png"
const SHOT_PATHS: Array[String] = [
	SHOT_STATION,
	SHOT_DISMANTLE,
	SHOT_CORE,
	SHOT_SERVICE_LINK,
	SHOT_RECEPTION,
	SHOT_EXTRACTION,
]

var scene: Node
var passes := 0
var fails := 0
var _tracking := false
var _suspended_seen := false
var _watcher_start := Vector3.ZERO
var _watcher_prev := Vector3.ZERO
var _watcher_distance := 0.0
var _watcher_relocations := 0
var _watcher_moved := 0.0
var _states_seen := {}
var _max_step := 0.0
var _last_position := Vector3.ZERO
var _transitioned := false
var _watcher_observed_frames := 0
var _watcher_chase_seen := false
var _watcher_investigate_seen := false
var _vision_changed := false


func _ready() -> void:
	DisplayServer.window_set_size(Vector2i(1280, 720))
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = 0
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	scene = SCENE.instantiate()
	add_child(scene)
	var guard := 0
	while not scene.level_ready and guard < 600:
		await get_tree().process_frame
		guard += 1
	await get_tree().create_timer(0.4).timeout

	var watchers := get_tree().get_nodes_in_group("fm_watcher")
	print("FULL_RUN_SHOTS watchers=%d scene_watcher=%s" % [watchers.size(), str(scene.watcher)])
	_check("watcher_instance_present", watchers.size() == 1 and watchers[0] == scene.watcher)
	_check("z10_watcher_physics_on", scene.watcher.is_physics_processing())
	_check("z10_watcher_not_suspended", not scene.is_watcher_suspended())
	_check("z10_watcher_vision_18", is_equal_approx(scene.watcher.vision_distance, 18.0))
	_check("z10_watcher_patrol_configured", scene.watcher.patrol_points.size() == 4)
	_check("dismantle_uses_default_duration", is_equal_approx(scene.dismantlable.dismantle_duration, 6.0))
	_check("extraction_uses_real_timing",
		is_equal_approx(scene.extraction.activation_time_s, 2.0)
		and is_equal_approx(scene.extraction.sequence_duration_s, 6.7))

	_watcher_start = scene.watcher.global_position
	_watcher_prev = _watcher_start
	_last_position = scene.player.global_position
	_tracking = true

	# ------------------------------------------------------------------
	# Z10: puesto de analisis. El ruido del desmontaje atrae al Vigilante;
	# se mantiene la mirada sobre el cuando entra en distancia de reaccion.
	# ------------------------------------------------------------------
	var route_station: Array[Vector3] = [
		Vector3(46.0, 0.12, -22.0),
		Vector3(50.0, 0.12, -21.8),
		STATION_APPROACH,
	]
	await _walk_to(route_station[0], 12.0, "station_%s" % str(route_station[0]))
	await _walk_to(route_station[1], 12.0, "station_%s" % str(route_station[1]))
	# 01: el puesto de analisis, aun intacto, desde la aproximacion.
	await _shot_looking_at(SHOT_STATION, Vector3(51.2, 1.0, -17.2))
	await _walk_to(route_station[2], 12.0, "station_%s" % str(route_station[2]))

	await get_tree().physics_frame
	var reachable: bool = scene.dismantlable.can_interact(scene.player)
	_check("station_reachable_on_foot", reachable)
	if not reachable:
		_finish()
		return

	_press_action("interact")
	await get_tree().physics_frame
	_check("dismantle_started", scene.dismantlable.dismantling)
	await _hold_watch(1.4, "dismantle_pre")
	# 02: desmontaje en curso, con la barra/indicador del puesto y su ruido.
	await _shot_looking_at(SHOT_DISMANTLE, Vector3(51.2, 1.0, -17.2), 0.25)
	_check("dismantle_in_progress_shot", scene.dismantlable.dismantling)
	await _hold_watch(5.8, "dismantle_post")
	_check("dismantle_completed", scene.dismantlable.completed)
	_check("four_components", scene.dismantlable.components.size() == 4)

	# Recoger los cuatro componentes desde el sur del puesto, sin mover al
	# jugador a posiciones imposibles. Si alguno queda fuera de alcance, se
	# rodea el puesto a pie hasta conseguirlo.
	for component in scene.dismantlable.components:
		var picked := false
		for attempt in range(3):
			await get_tree().physics_frame
			if scene.player._try_pickup():
				picked = true
				break
			var side := 1.0 if attempt == 1 else -1.0
			await _walk_to(STATION_APPROACH + Vector3(0.75 * side, 0.0, 0.0), 4.0, "component_side_%d" % attempt)
		_check("component_picked_%s" % str(component.item_name), picked)
	_check("components_in_inventory", scene.player.inventory.size() == 4)
	_check("components_weight_2_9", absf(scene.player.get_carry_weight() - 2.9) < 0.05)

	# ------------------------------------------------------------------
	# Nucleo y enlace de servicio.
	# ------------------------------------------------------------------
	await _walk_to(CORE_APPROACH, 12.0, "core")
	# 03: el nucleo de contencion antes de recogerlo.
	await _shot_looking_at(SHOT_CORE, Vector3(57.4, 0.9, -21.4))
	_press_action("interact")
	await get_tree().physics_frame
	_check("core_picked", scene.player.carried_item != null and not scene.player.inventory.is_empty())
	_check("core_total_weight_9_9", absf(scene.player.get_carry_weight() - 9.9) < 0.05)

	var route_link: Array[Vector3] = [
		Vector3(58.2, 0.12, -21.4),
		Vector3(61.4, 0.12, -21.0),
		DOOR_APPROACH,
	]
	await _walk_to(route_link[0], 18.0, "link_%s" % str(route_link[0]))
	await _walk_to(route_link[1], 18.0, "link_%s" % str(route_link[1]))
	# 04: pasillo y puerta del enlace de servicio a Recepcion.
	await _shot_looking_at(SHOT_SERVICE_LINK, Vector3(69.05, 1.5, -21.0))
	await _walk_to(route_link[2], 18.0, "link_%s" % str(route_link[2]))

	await get_tree().physics_frame
	_check("transition_door_prompt", scene.transition_door.can_interact(scene.player))
	_press_action("interact")
	await get_tree().physics_frame
	_check("transition_door_used", scene.transition_door.used)
	_check("transition_started", int(scene.state) == 3)
	_transitioned = true
	var transition_guard := 0
	while scene.current_area != "RECEPTION" and transition_guard < 180:
		await get_tree().physics_frame
		transition_guard += 1
	_check("reception_arrived", scene.current_area == "RECEPTION")
	_check("reception_watcher_physics_on", scene.watcher.is_physics_processing())
	_check("reception_watcher_not_suspended", not scene.is_watcher_suspended())
	_check("reception_watcher_vision_18", is_equal_approx(scene.watcher.vision_distance, 18.0))
	_check("reception_watcher_same_instance", get_tree().get_nodes_in_group("fm_watcher").size() == 1)
	# Esperar el fundido de entrada y el retorno a PLAYING.
	await get_tree().create_timer(0.9).timeout
	# La transicion reubica al jugador y al Vigilante; no es un paso de
	# movimiento y no debe contar como teletransporte del recorrido.
	_last_position = scene.player.global_position
	_watcher_prev = scene.watcher.global_position
	_watcher_relocations = 1

	# ------------------------------------------------------------------
	# Recepcion: cruzar el pasillo central y entregar en el ala sur.
	# ------------------------------------------------------------------
	var route_reception: Array[Vector3] = [
		Vector3(-90.0, 0.12, 13.0),
		Vector3(-93.0, 0.12, 16.5),
		Vector3(-93.0, 0.12, 24.0),
		Vector3(-92.0, 0.12, 32.0),
		EXTRACTION_APPROACH,
	]
	await _walk_to(route_reception[0], 20.0, "reception_%s" % str(route_reception[0]))
	await _walk_to(route_reception[1], 20.0, "reception_%s" % str(route_reception[1]))
	# 05: hall de Recepcion desde el pasillo central.
	await _shot_looking_at(SHOT_RECEPTION, Vector3(-93.0, 1.3, 24.0))
	await _walk_to(route_reception[2], 20.0, "reception_%s" % str(route_reception[2]))
	await _walk_to(route_reception[3], 20.0, "reception_%s" % str(route_reception[3]))
	await _walk_to(route_reception[4], 20.0, "reception_%s" % str(route_reception[4]))

	await get_tree().physics_frame
	await get_tree().physics_frame
	var delivered: int = scene.get_delivered_loot_count(scene.EXTRACTION_CENTER, 2.4)
	print("FULL_RUN_SHOTS_EXTRACTION delivered=%d inventory=%d carried=%s state=%d watcher=%s" % [
		delivered,
		scene.player.inventory.size(),
		str(scene.player.carried_item != null),
		int(scene.state),
		str(scene.watcher.global_position),
	])
	_check("five_items_in_extraction", delivered == 5)

	# 06: extraccion en curso, con el jugador dentro de la zona de entrega.
	await _shot_looking_at(SHOT_EXTRACTION, Vector3(-94.0, 1.2, 39.7), 0.20)
	_check("extraction_running_shot", int(scene.state) == 0)

	var extraction_wait := 0.0
	while int(scene.state) == 0 and extraction_wait < 12.0:
		_watch_or_scan()
		await get_tree().physics_frame
		extraction_wait += get_physics_process_delta_time()
	_check("extraction_completed", int(scene.state) == 1)
	_check("not_captured", int(scene.state) != 2)

	_tracking = false
	_watcher_moved = _watcher_start.distance_to(scene.watcher.global_position)
	print("FULL_RUN_SHOTS_RESULT state=%d area=%s pos=%s inventory=%d carried=%s delivered=%d" % [
		int(scene.state), scene.current_area, str(scene.player.global_position),
		scene.player.inventory.size(), str(scene.player.carried_item != null), delivered,
	])
	print("FULL_RUN_SHOTS_WATCHER moved=%.2f patrol_distance=%.2f relocations=%d observed_frames=%d chase=%s investigate=%s states=%s suspended_seen=%s" % [
		_watcher_moved, _watcher_distance, _watcher_relocations, _watcher_observed_frames,
		str(_watcher_chase_seen), str(_watcher_investigate_seen), str(_states_seen),
		str(_suspended_seen),
	])
	print("FULL_RUN_SHOTS_MOTION max_step=%.3f transitioned=%s" % [_max_step, str(_transitioned)])
	_check("watcher_moved_normally", _watcher_distance > 2.0)
	_check("watcher_one_sector_relocation", _watcher_relocations == 1)
	_check("watcher_never_suspended", not _suspended_seen)
	_check("watcher_vision_never_reduced", not _vision_changed)
	_check("watcher_was_observed", _watcher_observed_frames > 0)
	_check("watcher_reacted_to_noise", _watcher_investigate_seen or _watcher_chase_seen)
	_check("no_teleport_movement", _max_step < 0.65)
	_finish()


func _shot_looking_at(path: String, target: Vector3, settle := 0.28) -> void:
	_release_move()
	_aim_at(target)
	_track()
	await get_tree().create_timer(settle).timeout
	_track()
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	var err := image.save_png(path)
	var bytes := 0
	if FileAccess.file_exists(path):
		var file := FileAccess.open(path, FileAccess.READ)
		if file != null:
			bytes = file.get_length()
			file.close()
	print("FM_FULL_RUN_SHOT %s %dx%d bytes=%d err=%d state=%d area=%s camera_global=%s watcher=%s wstate=%d observed=%s" % [
		path,
		image.get_width(),
		image.get_height(),
		bytes,
		err,
		int(scene.state),
		scene.current_area,
		str(scene.player.camera.global_position),
		str(scene.watcher.global_position),
		int(scene.watcher.state),
		str(scene.player.is_observing(scene.watcher)),
	])
	_check("shot_%s" % path.get_file().get_basename(), err == OK and bytes > 51200)
	_check("shot_%s_ai_active" % path.get_file().get_basename(),
		scene.watcher.is_physics_processing()
		and not scene.is_watcher_suspended()
		and is_equal_approx(scene.watcher.vision_distance, 18.0))
	_check("shot_%s_1280x720" % path.get_file().get_basename(),
		image.get_width() == 1280 and image.get_height() == 720)


func _aim_at(target: Vector3) -> void:
	var camera_position: Vector3 = scene.player.camera.global_position
	var offset: Vector3 = target - camera_position
	var flat := sqrt(offset.x * offset.x + offset.z * offset.z)
	scene.player.rotation.y = atan2(-offset.x, -offset.z)
	scene.player.camera.rotation.y = 0.0
	scene.player.camera.rotation.x = atan2(offset.y, flat) if flat > 0.001 else 0.0
	scene.player._pitch = scene.player.camera.rotation.x


func _walk_to(target: Vector3, timeout: float, label: String) -> void:
	var elapsed := 0.0
	var best: float = scene.player.global_position.distance_to(target)
	var stuck_time := 0.0
	_release_move()
	while elapsed < timeout:
		if int(scene.state) != 0:
			break
		var offset: Vector3 = target - scene.player.global_position
		offset.y = 0.0
		var distance: float = offset.length()
		if distance < 0.7:
			break
		_track()
		var watch := _should_watch_watcher()
		var yaw := _yaw_to_watcher() if watch else atan2(-offset.x, -offset.z)
		scene.player.rotation.y = yaw
		scene.player.camera.rotation.x = 0.0
		scene.player.camera.rotation.y = 0.0
		_apply_move(offset, yaw)
		await get_tree().physics_frame
		elapsed += get_physics_process_delta_time()
		if scene.player.global_position.distance_to(target) < best - 0.02:
			best = scene.player.global_position.distance_to(target)
			stuck_time = 0.0
		else:
			stuck_time += get_physics_process_delta_time()
			if stuck_time > 3.0:
				break
	_release_move()
	await get_tree().physics_frame
	_track()
	var final_distance: float = scene.player.global_position.distance_to(target)
	var ok := final_distance < 0.95
	print("FULL_RUN_SHOTS_STEP %s ok=%s distance=%.2f time=%.1f pos=%s watcher=%s state=%d" % [
		label, str(ok), final_distance, elapsed, str(scene.player.global_position),
		str(scene.watcher.global_position), int(scene.watcher.state),
	])
	_check("route_%s" % label, ok)


func _hold_watch(seconds: float, label: String) -> void:
	var elapsed := 0.0
	while elapsed < seconds:
		if int(scene.state) != 0:
			break
		_track()
		_watch_or_scan()
		await get_tree().physics_frame
		elapsed += get_physics_process_delta_time()
	print("FULL_RUN_SHOTS_HOLD %s time=%.1f player=%s watcher=%s state=%d" % [
		label, elapsed, str(scene.player.global_position),
		str(scene.watcher.global_position), int(scene.watcher.state),
	])


func _watch_or_scan() -> void:
	scene.player.camera.rotation.x = 0.0
	scene.player.camera.rotation.y = 0.0
	if _should_watch_watcher():
		scene.player.rotation.y = _yaw_to_watcher()
	else:
		# Mirar al norte del pasillo de Recepcion/Z10 para detectar la
		# silueta en cuanto entre en el cono; no se mueve al jugador.
		scene.player.rotation.y = PI


func _should_watch_watcher() -> bool:
	if scene.watcher == null or not is_instance_valid(scene.watcher):
		return false
	var distance: float = scene.player.global_position.distance_to(scene.watcher.global_position)
	if distance > 15.5:
		return false
	return _watcher_has_los()


func _watcher_has_los() -> bool:
	var query := PhysicsRayQueryParameters3D.create(
		scene.player.camera.global_position,
		scene.watcher.global_position + Vector3(0.0, 1.35, 0.0)
	)
	query.collision_mask = 1
	query.exclude = [scene.player.get_rid()]
	var hit: Dictionary = scene.player.get_world_3d().direct_space_state.intersect_ray(query)
	return hit.is_empty()


func _yaw_to_watcher() -> float:
	var offset: Vector3 = scene.watcher.global_position - scene.player.global_position
	offset.y = 0.0
	return atan2(-offset.x, -offset.z)


func _apply_move(world_direction: Vector3, yaw: float) -> void:
	var direction := world_direction.normalized()
	var local := Basis(Vector3.UP, yaw).inverse() * direction
	_release_move()
	if local.x > 0.20:
		Input.action_press("move_right")
	elif local.x < -0.20:
		Input.action_press("move_left")
	if local.z < -0.20:
		Input.action_press("move_up")
	elif local.z > 0.20:
		Input.action_press("move_down")
	if not Input.is_action_pressed("move_up") and not Input.is_action_pressed("move_down") \
			and not Input.is_action_pressed("move_left") and not Input.is_action_pressed("move_right"):
		Input.action_press("move_up")


func _release_move() -> void:
	for action in ["move_up", "move_down", "move_left", "move_right"]:
		Input.action_release(action)


func _track() -> void:
	if not _tracking or scene.player == null or scene.watcher == null:
		return
	if int(scene.state) == 3:
		_last_position = scene.player.global_position
		_watcher_prev = scene.watcher.global_position
		return
	var step: float = _last_position.distance_to(scene.player.global_position)
	_max_step = maxf(_max_step, step)
	_last_position = scene.player.global_position
	var watcher_step: float = _watcher_prev.distance_to(scene.watcher.global_position)
	if watcher_step > 5.0:
		_watcher_relocations += 1
	else:
		_watcher_distance += watcher_step
	_watcher_prev = scene.watcher.global_position
	if scene.is_watcher_suspended() or not scene.watcher.is_physics_processing():
		_suspended_seen = true
	if not is_equal_approx(scene.watcher.vision_distance, 18.0):
		_vision_changed = true
	var state: int = int(scene.watcher.state)
	_states_seen[state] = true
	if state == FMWatcher.State.CHASE:
		_watcher_chase_seen = true
	elif state == FMWatcher.State.INVESTIGATE:
		_watcher_investigate_seen = true
	if scene.player.is_observing(scene.watcher):
		_watcher_observed_frames += 1


func _press_action(action: String) -> void:
	var event := InputEventAction.new()
	event.action = action
	event.pressed = true
	scene.player._unhandled_input(event)


func _check(check_name: String, condition: bool) -> void:
	if condition:
		passes += 1
		print("FULL_RUN_SHOTS_TEST: %s OK" % check_name)
	else:
		fails += 1
		print("FULL_RUN_SHOTS_TEST: %s FAIL" % check_name)


func _finish() -> void:
	_tracking = false
	_release_move()
	var state_ok := scene != null and int(scene.state) == 1
	var shots_ok := true
	print("FULL_RUN_SHOTS_FILES")
	for path in SHOT_PATHS:
		var exists := FileAccess.file_exists(path)
		var bytes := 0
		if exists:
			var file := FileAccess.open(path, FileAccess.READ)
			if file != null:
				bytes = file.get_length()
				file.close()
		var ok := exists and bytes > 51200
		if not ok:
			shots_ok = false
		print("FULL_RUN_SHOTS_FILE %s exists=%s bytes=%d ok=%s" % [
			path, str(exists), bytes, str(ok),
		])
	var all_ok := fails == 0 and state_ok and shots_ok
	print("FM_FULL_RUN_SHOTS %s state=%d passes=%d fails=%d shots_ok=%s" % [
		"PASS" if all_ok else "FAIL", int(scene.state), passes, fails, str(shots_ok),
	])
	get_tree().quit(0 if all_ok else 1)
