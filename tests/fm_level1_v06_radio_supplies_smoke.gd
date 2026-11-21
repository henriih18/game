extends Node

## Smoke test de los suministros de radio: cargadores fijos y pilas recogibles.
## Comprueba que reutilizan la interacción del jugador, que respetan la
## capacidad máxima de la radio y que no exponen posiciones de compañeros.

var _pass := 0
var _fail := 0
var _scene: Node


func _ready() -> void:
	_scene = load("res://scenes/fm/level1_v06.tscn").instantiate()
	add_child(_scene)
	var guard := 0
	while not _scene.level_ready and guard < 3600:
		guard += 1
		await get_tree().process_frame
	_check("level_ready", _scene.level_ready)
	if not _scene.level_ready:
		_finish()
		return
	await get_tree().physics_frame
	await get_tree().physics_frame

	_check("radio_exists", _scene.radio != null)
	_check("player_exists", _scene.player != null)
	_check("supplies_array", _scene.radio_supplies != null)
	var supplies: Array = _scene.radio_supplies
	_check("supplies_count", supplies.size() == 17)
	var stations := 0
	var batteries := 0
	var highs := 0
	for supply in supplies:
		if supply.kind == 2:
			stations += 1
		elif supply.kind == 1:
			highs += 1
		else:
			batteries += 1
	_check("stations_count", stations == 7)
	_check("batteries_count", batteries == 8)
	_check("high_capacity_count", highs == 2)

	var station: Node3D = _scene.get_node_or_null("RadioStation_Z10")
	var battery: Node3D = _scene.get_node_or_null("RadioBattery_Z10")
	var high: Node3D = _scene.get_node_or_null("RadioBattery_Warehouse_High")
	_check("station_node", station != null)
	_check("battery_node", battery != null)
	_check("high_node", high != null)
	if station == null or battery == null or high == null:
		_finish()
		return

	_check("station_group", station.is_in_group("fm_interactable") and station.is_in_group("fm_radio_supply"))
	_check("battery_group", battery.is_in_group("fm_interactable") and battery.is_in_group("fm_radio_supply"))
	_check("station_prompt", "CARGAR RADIO" in station.get_interaction_prompt())
	_check("battery_prompt", "PILA DE RADIO" in battery.get_interaction_prompt())
	_check("high_prompt", "ALTA CAPACIDAD" in high.get_interaction_prompt())
	_check("no_position_api", not battery.has_method("get_companion_positions"))

	var radio = _scene.radio
	radio.battery = 10.0
	var station_ok: bool = station.interact(_scene.player)
	_check("station_interact", station_ok)
	_check("station_adds_40", is_equal_approx(radio.get_battery(), 50.0))
	_check("station_cooldown", station.cooldown > 0.0)
	_check("station_second_blocked", not station.interact(_scene.player))
	_check("station_wait_prompt", "EN ESPERA" in station.get_interaction_prompt())

	radio.battery = 10.0
	var battery_ok: bool = battery.interact(_scene.player)
	_check("battery_interact", battery_ok)
	_check("battery_adds_30", is_equal_approx(radio.get_battery(), 40.0))
	_check("battery_taken", battery.taken)
	_check("battery_not_repeatable", not battery.can_interact(_scene.player))

	radio.battery = 10.0
	var high_ok: bool = high.interact(_scene.player)
	_check("high_interact", high_ok)
	_check("high_adds_70", is_equal_approx(radio.get_battery(), 80.0))

	radio.battery = 95.0
	var clamp_station: Node3D = _scene.get_node_or_null("RadioStation_Control")
	_check("clamp_station_node", clamp_station != null)
	if clamp_station != null:
		clamp_station.cooldown = 0.0
		clamp_station.interact(_scene.player)
	_check("battery_clamped", is_equal_approx(radio.get_battery(), 100.0))

	_finish()


func _check(label: String, condition: bool) -> void:
	if condition:
		_pass += 1
		print("PASS radio_supplies_", label)
	else:
		_fail += 1
		print("FAIL radio_supplies_", label)


func _finish() -> void:
	print("FM_RADIO_SUPPLIES_SMOKE: %d PASS / %d FAIL" % [_pass, _fail])
	get_tree().quit(0 if _fail == 0 else 1)
