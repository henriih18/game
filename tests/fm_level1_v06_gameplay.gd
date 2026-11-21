extends Node

## Primer pase de gameplay del Nivel 1 V06.
## godot --headless --path . tests/fm_level1_v06_gameplay.tscn
##
## Comprueba:
##   - núcleo de misión, puesto de análisis, componentes/documentos extra,
##     baterías, escondites y extracción de Recepción;
##   - marcador visual de extracción (aro, cartel, rótulo de suelo y balizas
##     emisivas) sin luces dinámicas y sin alterar la lógica de extracción;
##   - recorrido real a pie hasta el puesto y desmontaje real (6,0 s) con
##     cuatro componentes pequeños registrados en carry_items;
##   - recogida real de un componente y del núcleo;
##   - extracción bloqueada con botín pero sin núcleo;
##   - extracción completada con núcleo y contabilización de 2 objetos.
##
## Transiciones de prueba: el V06 es un nivel continuo y la distancia real
## Z10 ↔ Recepción supera los 150 m (unos 80 s de recorrido de ida y vuelta).
## El smoke ya cubre a pie el corredor y la compuerta. Para no duplicar ese
## recorrido, esta prueba solo teletransporta al jugador ENTRE SECTORES, con
## una transición explícita y documentada; dentro de Z10 el jugador camina con
## Input.action_press y nunca se salta obstáculos locales.

const SCENE_PATH := "res://scenes/fm/level1_v06.tscn"
const CORE_POSITION := Vector3(57.4, 0.36, -21.4)
const DISMANTLE_POSITION := Vector3(51.2, 0.0, -17.2)
const Z10_HIDE_POSITION := Vector3(42.5, 0.05, -9.4)
const RECEPTION_HIDE_POSITION := Vector3(-106.0, 0.05, 38.8)
const SECURITY_HIDE_POSITION := Vector3(-78.4, 0.05, -11.85)
const BATTERY_Z10_POSITION := Vector3(53.4, 0.16, -25.4)
const BATTERY_RECEPTION_POSITION := Vector3(-104.0, 0.16, 20.2)
const RECEPTION_DOC_POSITION := Vector3(-90.0, 0.12, 18.0)
const RECEPTION_COMPONENT_POSITION := Vector3(-93.0, 0.14, 24.0)
const SECURITY_DOC_POSITION := Vector3(-96.8, 0.91, -20.4)
const EXTRACTION_POSITION := Vector3(-94.0, 1.3, 36.0)
const EXTRACTION_CENTER := Vector3(-94.0, 0.3, 37.6)
const EXTRACTION_ZONE_SIZE := Vector3(9.0, 2.6, 8.0)
const EXTRACTION_ENTRY := Vector3(-94.0, 0.12, 36.6)
const CORE_APPROACH := Vector3(55.9, 0.12, -21.4)
const STATION_APPROACH := Vector3(51.9, 0.12, -18.9)

var scene
var passes := 0
var fails := 0


func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	_release_movement()

	var packed := load(SCENE_PATH) as PackedScene
	_check("scene_load", packed != null)
	if packed == null:
		_finish()
		return

	scene = packed.instantiate()
	add_child(scene)
	var guard := 0
	while not scene.level_ready and guard < 3600:
		await get_tree().process_frame
		guard += 1
	if not scene.level_ready:
		_fail("level_ready (guard=%d)" % guard)
		_finish()
		return

	# Los Vigilantes no participan en este pase: la prueba mide loot,
	# desmontaje, escondites y extracción, no percepción ni captura.
	if scene.watcher != null and is_instance_valid(scene.watcher):
		scene.watcher.set_physics_process(false)
	if scene.security_watcher != null and is_instance_valid(scene.security_watcher):
		scene.security_watcher.set_physics_process(false)
	await _wait(0.6)

	var player: FMPlayer = scene.player
	_check("player", player != null and is_instance_valid(player))
	if player == null:
		_finish()
		return

	# ------------------------------------------------------------------
	# Presencia y configuración del loot de misión y del puesto.
	# ------------------------------------------------------------------
	var core: FMCarryItem = null
	for item in scene.carry_items:
		if item != null and is_instance_valid(item) and item.is_mission_item:
			core = item
			break
	_check("core_present", core != null)
	if core != null:
		_check("core_position", core.global_position.distance_to(CORE_POSITION) <= 0.05)
		_check("core_mass", absf(core.item_mass - 7.0) <= 0.001)
		_check("core_medium", core.size_class == "MEDIUM")
		_check("core_mission", core.is_mission_item and core.item_kind == "core")
		_check("core_registered", scene.carry_items.has(core))

	var station: FMDismantlable = scene.dismantlable
	_check("station_present", station != null and is_instance_valid(station))
	if station != null:
		_check("station_position", station.global_position.distance_to(DISMANTLE_POSITION) <= 0.05)
		_check("station_ready", not station.completed and station.components.is_empty())
		_check("station_game", station.game == scene)

	var extras: Array[FMCarryItem] = []
	for item in scene.carry_items:
		if item != null and is_instance_valid(item) and not item.is_mission_item:
			extras.append(item)
	_check("extra_loot_count", extras.size() == 3)
	var extra_positions := {
		"Loot_Reception_Doc": RECEPTION_DOC_POSITION,
		"Loot_Reception_Component": RECEPTION_COMPONENT_POSITION,
		"Loot_Security_Doc": SECURITY_DOC_POSITION,
	}
	for item in extras:
		var expected: Vector3 = extra_positions.get(item.name, Vector3(9999, 9999, 9999))
		_check("extra_%s_position" % item.name, item.global_position.distance_to(expected) <= 0.05)
		_check("extra_%s_small" % item.name, item.size_class == "SMALL"
			and item.visual_style == "COMPONENT" and not item.is_mission_item)
		_check("extra_%s_mass" % item.name, item.item_mass >= 0.3 and item.item_mass <= 1.2)
		_check("extra_%s_outside_extraction" % item.name,
			item.global_position.distance_to(EXTRACTION_CENTER) > 2.4)

	# ------------------------------------------------------------------
	# Baterías fuera del eje de paso, con carga útil.
	# ------------------------------------------------------------------
	_check("battery_count", scene.batteries.size() == 2)
	for battery in scene.batteries:
		_check("battery_%s_present" % battery.name,
			battery != null and is_instance_valid(battery) and not battery.taken)
		_check("battery_%s_charge" % battery.name,
			battery.charge_amount >= 60.0 and battery.charge_amount <= 100.0)
		_check("battery_%s_group" % battery.name, battery.is_in_group("fm_interactable"))
	var battery_z10 := _find_battery("Battery_Z10_Storage")
	var battery_reception := _find_battery("Battery_Reception_West")
	_check("battery_z10_position", battery_z10 != null
		and battery_z10.global_position.distance_to(BATTERY_Z10_POSITION) <= 0.05)
	_check("battery_reception_position", battery_reception != null
		and battery_reception.global_position.distance_to(BATTERY_RECEPTION_POSITION) <= 0.05)

	# ------------------------------------------------------------------
	# Escondites con puntos de entrada/salida coherentes.
	# ------------------------------------------------------------------
	_check("hiding_spot_count", scene.hiding_spots.size() == 3)
	var shelves := _find_hiding_spot("HideShelvesZ10")
	var lockers := _find_hiding_spot("HideReceptionLockers")
	var security_lockers := _find_hiding_spot("HideSecurityLockers")
	_check("hiding_shelves", shelves != null and shelves.display_name == "ESTANTERÍA"
		and shelves.global_position.distance_to(Z10_HIDE_POSITION) <= 0.05)
	_check("hiding_lockers", lockers != null and lockers.display_name == "TAQUILLAS DE PERSONAL"
		and lockers.global_position.distance_to(RECEPTION_HIDE_POSITION) <= 0.05)
	_check("hiding_security_lockers", security_lockers != null
		and security_lockers.display_name == "TAQUILLAS DE SEGURIDAD"
		and security_lockers.global_position.distance_to(SECURITY_HIDE_POSITION) <= 0.05)
	for spot in scene.hiding_spots:
		var hide_point: Vector3 = spot.get_hide_point()
		var exit_point: Vector3 = spot.get_exit_point()
		_check("hiding_%s_exit" % spot.name, hide_point.distance_to(exit_point) >= 1.0
			and hide_point.y > -0.5 and exit_point.y > -0.5)
		_check("hiding_%s_usable" % spot.name, spot.can_use(player))

	# ------------------------------------------------------------------
	# Extracción de Recepción: posición, zona y estado inicial.
	# ------------------------------------------------------------------
	var extraction: FMReceptionExtraction = scene.extraction
	_check("extraction_present", extraction != null and is_instance_valid(extraction))
	if extraction != null:
		_check("extraction_group", extraction.is_in_group("fm_extraction"))
		_check("extraction_position", extraction.global_position.distance_to(EXTRACTION_POSITION) <= 0.05)
		_check("extraction_delivery_center", extraction.delivery_center.distance_to(EXTRACTION_CENTER) <= 0.001)
		_check("extraction_zone_size", extraction.zone_size.distance_to(EXTRACTION_ZONE_SIZE) <= 0.001)
		_check("extraction_waiting", extraction._state == "waiting")
		_check("extraction_game", extraction.game == scene)
	_check("hud", scene.hud != null and is_instance_valid(scene.hud))

	# ------------------------------------------------------------------
	# Marcador visual de extracción: aro, cartel SALIDA, rótulo de zona y
	# balizas emisivas sobre el deck. Sin luces dinámicas nuevas y sin tocar
	# la lógica de FMReceptionExtraction.
	# ------------------------------------------------------------------
	var marker: Node3D = scene.extraction_marker
	_check("marker_present", marker != null and is_instance_valid(marker))
	if marker != null:
		_check("marker_position",
			marker.global_position.distance_to(Vector3(-94.0, 0.0, 37.6)) <= 0.01)
		_check("marker_on_reception_deck",
			marker.global_position.x >= -100.0 and marker.global_position.x <= -88.0
			and marker.global_position.z >= 35.0 and marker.global_position.z <= 40.0)
		_check("marker_approach_side", marker.global_position.z < 39.6)

	var marker_ring: MeshInstance3D = scene.extraction_ring
	_check("marker_ring_present", marker_ring != null and is_instance_valid(marker_ring)
		and marker_ring.mesh is TorusMesh)
	if marker_ring != null:
		_check("marker_ring_position",
			marker_ring.global_position.distance_to(Vector3(-94.0, 0.055, 37.6)) <= 0.01)
		var ring_mat := marker_ring.material_override as StandardMaterial3D
		_check("marker_ring_emissive", ring_mat != null and ring_mat.emission_enabled
			and ring_mat.emission_energy_multiplier >= 1.0)
		_check("marker_ring_green", ring_mat != null
			and ring_mat.emission.g > ring_mat.emission.r * 2.0)

	var marker_sign: Label3D = scene.extraction_sign
	_check("marker_sign_present", marker_sign != null and is_instance_valid(marker_sign))
	if marker_sign != null:
		_check("marker_sign_text", marker_sign.text.contains("EXTRACCIÓN"))
		print("FM_LEVEL1_V06_MARKER_SIGN font=%d pixel=%.4f outline=%d billboard=%d pos=%s" % [
			marker_sign.font_size, marker_sign.pixel_size, marker_sign.outline_size,
			int(marker_sign.billboard), str(marker_sign.global_position),
		])
		_check("marker_sign_legible", marker_sign.font_size >= 30
			and marker_sign.pixel_size >= 0.0049 and marker_sign.outline_size >= 7)
		_check("marker_sign_billboard",
			marker_sign.billboard == BaseMaterial3D.BILLBOARD_ENABLED)
		_check("marker_sign_height", marker_sign.global_position.y >= 2.5
			and marker_sign.global_position.y <= 4.5)

	var floor_label: Label3D = scene.extraction_floor_label
	_check("marker_floor_label_present", floor_label != null and is_instance_valid(floor_label))
	if floor_label != null:
		_check("marker_floor_label_text", floor_label.text == "SALIDA")
		_check("marker_floor_label_flat", absf(floor_label.rotation.x + PI * 0.5) <= 0.01)
		_check("marker_floor_label_orientation",
			floor_label.global_transform.basis.x.x < -0.9
			and floor_label.global_transform.basis.y.z > 0.9
			and floor_label.global_transform.basis.z.y > 0.9)
		_check("marker_floor_label_legible", floor_label.font_size >= 72
			and floor_label.pixel_size >= 0.004)
		_check("marker_floor_label_on_deck",
			floor_label.global_position.distance_to(Vector3(-94.0, 0.065, 37.6)) <= 0.01)

	_check("marker_beacon_count", scene.extraction_beacons.size() == 2)
	for beacon in scene.extraction_beacons:
		_check("marker_beacon_present", beacon != null and is_instance_valid(beacon))
		if beacon != null:
			var beacon_mat := beacon.material_override as StandardMaterial3D
			_check("marker_beacon_emissive", beacon_mat != null and beacon_mat.emission_enabled)
	_check("marker_no_dynamic_light", scene.get_extraction_marker_light_count() == 0)

	# ------------------------------------------------------------------
	# Recorrido real dentro de Z10 hasta el puesto de análisis.
	# ------------------------------------------------------------------
	var station_route: Array[Vector3] = [
		Vector3(46.5, 0.12, -21.3),
		Vector3(52.0, 0.12, -21.3),
		STATION_APPROACH,
	]
	var station_walk := await _walk_route(player, station_route, 16.0)
	var station_distance: float = player.global_position.distance_to(
		station.get_interaction_position()
	) if station != null else 99.0
	print("FM_LEVEL1_V06_GAMEPLAY_STATION_WALK end=%s path=%.2f max_step=%.3f distance=%.2f" % [
		str(player.global_position), float(station_walk.get("path", 0.0)),
		float(station_walk.get("max_step", 0.0)), station_distance,
	])
	_check("station_walk_no_teleport", float(station_walk.get("max_step", 99.0)) < 0.75)
	_check("station_walk_reachable", station_distance <= 2.8)
	_check("station_prompt", player.get_interaction_prompt().contains("DESMONTAR"))

	var station_started: bool = player._try_interactable()
	_check("station_interact", station_started and station.dismantling)
	_check("station_noise", station.noise_radius > 0.0 and station.dismantle_duration > 0.0)
	# Duración real del vertical slice (6,0 s), sin acelerarla.
	await _wait(7.0)
	_check("station_completed", station.completed and not station.dismantling)
	_check("station_component_count", station.components.size() == 4)
	var registered := 0
	for component in station.components:
		if component != null and is_instance_valid(component) and scene.carry_items.has(component):
			registered += 1
	_check("station_components_registered", registered == 4)
	_check("station_carry_items", scene.carry_items.size() == 8)
	var component_mass_ok := true
	for component in station.components:
		if component.size_class != "SMALL" or component.visual_style != "COMPONENT" \
			or component.is_mission_item or component.item_mass < 0.3 or component.item_mass > 1.2:
			component_mass_ok = false
	_check("station_components_contract", component_mass_ok)

	# Recogida real de un componente pequeño (va al inventario).
	var inventory_before := player.inventory.size()
	var component_picked: bool = player._try_pickup()
	_check("component_pickup", component_picked and player.inventory.size() == inventory_before + 1)
	var stowed: FMCarryItem = null
	if not player.inventory.is_empty():
		stowed = player.inventory[player.inventory.size() - 1]
	_check("component_stowed", stowed != null and stowed.stowed
		and stowed.carried_by == player and stowed.size_class == "SMALL")

	# ------------------------------------------------------------------
	# Transición de prueba 1: Recepción, extracción SIN núcleo.
	# ------------------------------------------------------------------
	await _test_transition(EXTRACTION_ENTRY, PI)
	_check("blocked_player_in_zone", extraction.players_inside.has(player))
	await _wait(2.6)
	var delivered_without_mission: int = scene.get_delivered_loot_count(
		EXTRACTION_CENTER, extraction.delivery_radius_m
	)
	print("FM_LEVEL1_V06_GAMEPLAY_BLOCKED delivered=%d mission=%s state=%d ex=%s" % [
		delivered_without_mission,
		str(scene.has_delivered_mission_item(EXTRACTION_CENTER, extraction.delivery_radius_m)),
		int(scene.state), extraction._state,
	])
	_check("blocked_delivered_component", delivered_without_mission == 1)
	_check("blocked_no_mission_item",
		not scene.has_delivered_mission_item(EXTRACTION_CENTER, extraction.delivery_radius_m))
	_check("blocked_extraction_waiting", extraction._state == "waiting")
	_check("blocked_no_extraction_started", not scene._extraction_busy)
	_check("blocked_state_playing", int(scene.state) == 0)

	# ------------------------------------------------------------------
	# Transición de prueba 2: volver a Z10 y recoger el núcleo a pie.
	# ------------------------------------------------------------------
	await _test_transition(CORE_APPROACH, 0.0)
	_check("core_approach_distance",
		player.global_position.distance_to(core.global_position) <= 2.8)
	var core_picked: bool = player._try_pickup()
	_check("core_pickup", core_picked and player.carried_item == core)
	_check("core_in_hands", core.carried_by == player and not core.stowed)
	_check("core_mission_in_hands", scene._player_has_mission_item())
	var expected_weight: float = 7.0
	if stowed != null:
		expected_weight += stowed.item_mass
	_check("core_carry_weight", absf(player.get_carry_weight() - expected_weight) <= 0.05)

	# ------------------------------------------------------------------
	# Transición de prueba 3: extracción con núcleo y contabilización.
	# ------------------------------------------------------------------
	await _test_transition(EXTRACTION_ENTRY, PI)
	_check("extraction_player_in_zone_again", extraction.players_inside.has(player))
	var elapsed := 0.0
	while int(scene.state) == 0 and elapsed < 14.0:
		await get_tree().physics_frame
		elapsed += get_physics_process_delta_time()
	print("FM_LEVEL1_V06_GAMEPLAY_EXTRACTION elapsed=%.2f state=%d ex=%s busy=%s" % [
		elapsed, int(scene.state), extraction._state, str(scene._extraction_busy),
	])
	_check("extraction_completed", int(scene.state) == 2)
	_check("extraction_state_done", extraction._state == "done")
	var delivered_total: int = scene.get_delivered_loot_count(
		EXTRACTION_CENTER, extraction.delivery_radius_m
	)
	print("FM_LEVEL1_V06_GAMEPLAY_RESULT delivered=%d inventory=%d core_mission=%s hud=%s" % [
		delivered_total, player.inventory.size(),
		str(scene.has_delivered_mission_item(EXTRACTION_CENTER, extraction.delivery_radius_m)),
		scene.hud._result.text,
	])
	_check("extraction_delivered_total", delivered_total == 2)
	_check("extraction_mission_delivered",
		scene.has_delivered_mission_item(EXTRACTION_CENTER, extraction.delivery_radius_m))
	_check("extraction_hud_end", scene.hud._overlay.visible
		and scene.hud._result.text == "EXTRACCIÓN COMPLETADA")
	_check("extraction_hud_count", scene.hud._result_sub.text.contains("2 objeto"))
	_check("extraction_no_respawn", scene.respawn_count == 0)

	await _cleanup()


func _find_battery(node_name: String) -> FMBattery:
	for battery in scene.batteries:
		if battery != null and is_instance_valid(battery) and battery.name == node_name:
			return battery
	return null


func _find_hiding_spot(node_name: String) -> FMHidingSpot:
	for spot in scene.hiding_spots:
		if spot != null and is_instance_valid(spot) and spot.name == node_name:
			return spot
	return null


## Transición de prueba documentada: solo mueve al jugador entre sectores.
## No se usa para superar obstáculos dentro de una misma sala.
func _test_transition(target: Vector3, yaw: float) -> void:
	scene.player.global_position = target
	scene.player.rotation.y = yaw
	scene.player.velocity = Vector3.ZERO
	scene.player._pitch = 0.0
	scene.player.camera.rotation.x = 0.0
	await get_tree().physics_frame
	await get_tree().physics_frame
	await _wait(0.2)


func _walk_route(player: FMPlayer, route: Array[Vector3], timeout: float) -> Dictionary:
	var start: Vector3 = player.global_position
	var prev := start
	var path := 0.0
	var max_step := 0.0
	var elapsed := 0.0
	var stuck := 0.0
	var index := 0
	Input.action_press("move_up")
	while elapsed < timeout and index < route.size():
		var aim: Vector3 = route[index] - player.global_position
		aim.y = 0.0
		if aim.length() < 0.45:
			index += 1
			continue
		player.rotation.y = atan2(-aim.x, -aim.z)
		await get_tree().physics_frame
		var current: Vector3 = player.global_position
		var step := prev.distance_to(current)
		max_step = maxf(max_step, step)
		path += step
		prev = current
		elapsed += get_physics_process_delta_time()
		if step < 0.004:
			stuck += get_physics_process_delta_time()
			if stuck > 2.0:
				break
		else:
			stuck = 0.0
	Input.action_release("move_up")
	await get_tree().physics_frame
	return {
		"start": start, "end": player.global_position, "path": path,
		"max_step": max_step, "elapsed": elapsed, "waypoint": index,
	}


func _cleanup() -> void:
	_release_movement()
	await _wait(1.0)
	if scene != null and is_instance_valid(scene):
		scene.free()
	scene = null
	await get_tree().process_frame
	await get_tree().process_frame
	_finish()


func _release_movement() -> void:
	for action in ["move_up", "move_down", "move_left", "move_right", "sprint", "crouch", "interact", "drop", "flashlight"]:
		Input.action_release(action)


func _wait(seconds: float) -> void:
	await get_tree().create_timer(seconds).timeout


func _check(label: String, condition: bool) -> void:
	if condition:
		passes += 1
		print("PASS %s" % label)
	else:
		_fail(label)


func _fail(label: String) -> void:
	fails += 1
	print("FAIL %s" % label)


func _finish() -> void:
	_release_movement()
	print("FM_LEVEL1_V06_GAMEPLAY: %s (%d PASS / %d FAIL)" % [
		"PASS" if fails == 0 else "FAIL", passes, fails,
	])
	get_tree().quit(0 if fails == 0 else 1)
