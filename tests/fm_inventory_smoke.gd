extends Node

## Inventario, peso y desmontaje del vertical slice.
## No prueba la UI completa ni el sistema definitivo de la sección 32.

var scene: Node
var passes := 0
var fails := 0

func _ready() -> void:
	var packed: PackedScene = load("res://scenes/fm/fm_vslice_z10.tscn")
	scene = packed.instantiate()
	add_child(scene)
	while not scene.level_ready:
		await get_tree().process_frame
	scene.watcher.set_physics_process(false)
	scene.reception_watcher_enabled = false
	await _wait(0.35)

	var core = scene.carry_items[0]
	_check("core_mission_item", core.is_mission_item and core.size_class == "MEDIUM")
	scene.player.global_position = Vector3(core.global_position.x, 0.12, core.global_position.z + 1.2)
	await get_tree().physics_frame
	_check("core_pickup", scene.player._try_pickup())
	_check("core_in_hands", scene.player.carried_item == core and scene.player.inventory.is_empty())
	_check("core_carry_weight", absf(scene.player.get_carry_weight() - 7.0) < 0.01)
	scene.player._drop_item()
	_check("core_dropped", scene.player.carried_item == null and core.carried_by == null)

	var station = scene.dismantlable
	station.dismantle_duration = 0.6
	station.noise_interval = 0.2
	scene.player.global_position = station.global_position + Vector3(0.0, 0.12, 1.6)
	await get_tree().physics_frame
	_check("station_interact", station.interact(scene.player))
	_check("dismantle_started", station.dismantling and not station.completed)
	await _wait(0.15)
	scene.player.global_position = station.global_position + Vector3(0.0, 0.12, 5.0)
	await _wait(0.2)
	_check("dismantle_cancelled", not station.dismantling and not station.completed and station.components.is_empty())

	scene.player.global_position = station.global_position + Vector3(0.0, 0.12, 1.6)
	await get_tree().physics_frame
	_check("station_restart", station.interact(scene.player))
	await _wait(0.8)
	_check("dismantle_completed", station.completed and station.components.size() == 4)
	if station.components.is_empty():
		_finish()
		return

	var first = station.components[0]
	_check("component_small", first.size_class == "SMALL" and not first.is_mission_item)
	scene.player.global_position = Vector3(first.global_position.x, 0.12, first.global_position.z + 1.0)
	await get_tree().physics_frame
	_check("component_pickup", scene.player._try_pickup())
	var stowed = scene.player.inventory[0] if not scene.player.inventory.is_empty() else null
	_check("component_stowed", stowed != null and scene.player.inventory.size() == 1 and stowed.stowed and stowed.carried_by == scene.player and scene.player.carried_item == null)
	_check("component_weight", stowed != null and absf(scene.player.get_carry_weight() - stowed.item_mass) < 0.01)

	scene.player.inventory_capacity = 1
	var second = station.components[1]
	scene.player.global_position = Vector3(second.global_position.x, 0.12, second.global_position.z + 1.0)
	await get_tree().physics_frame
	_check("inventory_full", not scene.player._try_pickup() and scene.player.inventory.size() == 1)
	scene.player.inventory_capacity = 4

	scene.player.max_carry_weight = 0.5
	scene.player.global_position = Vector3(second.global_position.x, 0.12, second.global_position.z + 1.0)
	await get_tree().physics_frame
	_check("weight_limit", not scene.player._try_pickup() and scene.player.inventory.size() == 1)
	scene.player.max_carry_weight = 12.0

	scene.player._drop_carried_or_inventory()
	_check("inventory_drop", scene.player.inventory.is_empty() and stowed != null and stowed.carried_by == null)

	for component in station.components:
		scene.player.global_position = Vector3(component.global_position.x, 0.12, component.global_position.z + 1.0)
		await get_tree().physics_frame
		scene.player._try_pickup()
	_check("components_collected", scene.player.inventory.size() == 4)
	_check("components_weight", absf(scene.player.get_carry_weight() - 2.9) < 0.05)

	# La extracción está en Recepción: usar la transición real antes de probar
	# la entrega evita que clamp_player devuelva al jugador a Z10.
	var transition_started: bool = scene.transition_door.interact(scene.player)
	_check("reception_transition", transition_started)
	await _wait(2.0)
	_check("reception_area", scene.current_area == "RECEPTION")

	scene.player.global_position = Vector3(-94.0, 0.12, 36.6)
	await get_tree().physics_frame
	await get_tree().physics_frame
	await _wait(0.2)
	var delivered_without_mission: int = scene.get_delivered_loot_count(scene.EXTRACTION_CENTER, 2.4)
	_check("components_delivered_count", delivered_without_mission == 4)
	_check("no_mission_delivery", not scene.has_delivered_mission_item(scene.EXTRACTION_CENTER, 2.4))
	scene.extraction.activation_time_s = 0.1
	scene.extraction.sequence_duration_s = 0.2
	scene.extraction.door_open_s = 0.05
	scene.extraction.door_hold_s = 0.05
	scene.extraction.door_close_s = 0.05
	scene.extraction.travel_s = 0.05
	await _wait(0.8)
	_check("extraction_blocked_without_mission", int(scene.state) == 0 and scene.extraction._state == "waiting")

	core.freeze = true
	core.global_position = Vector3(-94.0, 0.35, 37.2)
	scene.player.global_position = Vector3(-94.0, 0.12, 36.6)
	await get_tree().physics_frame
	await get_tree().physics_frame
	_check("mission_delivery", scene.has_delivered_mission_item(scene.EXTRACTION_CENTER, 2.4))
	await _wait(1.2)
	_check("extraction_with_mission", int(scene.state) == 1)
	_check("single_reward_count", scene.get_delivered_loot_count(scene.EXTRACTION_CENTER, 2.4) == 5)

	_finish()

func _wait(seconds: float) -> void:
	await get_tree().create_timer(seconds).timeout

func _check(name: String, condition: bool) -> void:
	if condition:
		passes += 1
		print("INV_TEST: %s OK" % name)
	else:
		fails += 1
		print("INV_TEST: %s FAIL" % name)

func _finish() -> void:
	if fails == 0:
		print("FM_INVENTORY_TEST: PASS (%d PASS / 0 FAIL)" % passes)
		get_tree().quit(0)
	else:
		print("FM_INVENTORY_TEST: FAIL (%d PASS / %d FAIL)" % [passes, fails])
		get_tree().quit(1)
