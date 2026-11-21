extends Node

## UI de inventario del vertical slice.
## Comprueba la acción `inventory`, el panel, los datos mostrados en tiempo
## real y que la UI no altera el inventario del jugador.
##
## godot --headless --path . tests/fm_inventory_ui_smoke.tscn

const SCENE := preload("res://scenes/fm/fm_vslice_z10.tscn")
const ITEM_SCENE := preload("res://scenes/fm/carry_item.tscn")

var scene: Node
var passes := 0
var fails := 0
var _spawned_items: Array[FMCarryItem] = []


func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	scene = SCENE.instantiate()
	add_child(scene)
	var guard := 0
	while not scene.level_ready and guard < 600:
		await get_tree().process_frame
		guard += 1
	if not scene.level_ready:
		_check("level_ready", false)
		_finish()
		return
	scene.watcher.set_physics_process(false)
	scene.reception_watcher_enabled = false
	await _wait(0.25)

	var ui: FMInventoryUI = scene.inventory_ui
	_check("ui_exists", ui != null and is_instance_valid(ui))
	if ui == null:
		_finish()
		return

	var panel := ui.get_node_or_null("InventoryPanel") as Control
	_check("panel_exists", panel != null)
	_check("panel_hidden_at_start", panel != null and not panel.visible)
	_check("ui_closed_at_start", not ui.is_open())
	_check("action_registered", InputMap.has_action("inventory"))
	_check("action_key_i", _has_key("inventory", KEY_I))
	_check("hud_hint_includes_inventory", String(scene.hud._hint.text).contains("I INVENTARIO"))

	_press_action(ui, "inventory")
	await get_tree().process_frame
	_check("panel_opens_with_action", ui.is_open() and panel.visible)

	var snap: Dictionary = ui.get_snapshot()
	_check("four_slots", snap["slots"].size() == 4)
	_check("initial_hands_empty", String(snap["hands_name"]) == "SIN OBJETO EN MANOS")
	_check("initial_count_zero", int(snap["count"]) == 0 and String(snap["count_text"]).contains("0 / 4"))
	_check("initial_weight_zero", absf(float(snap["weight"])) < 0.001)
	_check("initial_total_text", String(snap["total_text"]).contains("0.0 / 12.0"))
	_check("initial_warning_clear", not bool(snap["warning_active"]))
	var empty_slots := true
	for slot_text in snap["slots"]:
		if String(slot_text) != "RANURA VACÍA":
			empty_slots = false
	_check("initial_slots_empty", empty_slots)

	_press_action(ui, "inventory")
	await get_tree().process_frame
	_check("panel_closes_with_action", not ui.is_open() and not panel.visible)
	_press_action(ui, "inventory")
	await get_tree().process_frame
	_check("panel_reopens", ui.is_open() and panel.visible)

	# Objeto de misión en las manos: nombre, peso y marca de misión.
	var core = scene.carry_items[0]
	scene.player.global_position = Vector3(core.global_position.x, 0.12, core.global_position.z + 1.2)
	await get_tree().physics_frame
	_check("core_pickup", scene.player._try_pickup())
	await get_tree().process_frame
	await get_tree().process_frame
	snap = ui.get_snapshot()
	_check("hands_show_core_name", String(snap["hands_name"]).contains("NÚCLEO"))
	_check("hands_show_core_weight", String(snap["hands_meta"]).contains("7.0 kg"))
	_check("hands_show_mission_flag", bool(snap["hands_mission"]) and String(snap["hands_meta"]).contains("MISIÓN"))
	_check("total_weight_after_pickup", absf(float(snap["weight"]) - 7.0) < 0.01)
	_check("total_text_after_pickup", String(snap["total_text"]).contains("7.0 / 12.0"))
	_check("core_not_in_slots", int(snap["count"]) == 0)

	scene.player._drop_item()
	await get_tree().process_frame
	await get_tree().process_frame
	snap = ui.get_snapshot()
	_check("hands_clear_after_drop", String(snap["hands_name"]) == "SIN OBJETO EN MANOS" and not bool(snap["hands_mission"]))
	_check("weight_clear_after_drop", absf(float(snap["weight"])) < 0.001)

	# Inventario: cuatro componentes pequeños, aviso de lleno y actualización
	# inmediata de las ranuras al soltar.
	scene.player.global_position = scene.Z10_SPAWN
	scene.player.velocity = Vector3.ZERO
	await get_tree().physics_frame
	for i in range(4):
		var item := ITEM_SCENE.instantiate() as FMCarryItem
		item.name = "UIComponent_%d" % (i + 1)
		item.item_name = "COMPONENTE UI %d" % (i + 1)
		item.item_mass = 0.7
		item.size_class = "SMALL"
		item.visual_style = "COMPONENT"
		item.is_mission_item = false
		item.game = scene
		scene.add_child(item)
		scene.register_carry_item(item)
		item.global_position = scene.player.global_position + Vector3(0.6, 0.0, 0.0)
		_spawned_items.append(item)
		await get_tree().physics_frame
		_check("pickup_component_%d" % (i + 1), scene.player._try_pickup())
		await get_tree().process_frame
		snap = ui.get_snapshot()
		_check("slot_count_%d" % (i + 1), int(snap["count"]) == i + 1)

	await get_tree().process_frame
	snap = ui.get_snapshot()
	_check("four_slots_filled", int(snap["count"]) == 4 and String(snap["count_text"]).contains("4 / 4"))
	_check("inventory_full_warning", bool(snap["warning_active"]) and String(snap["warning"]).contains("LLENO"))
	_check("weight_total_2_8", absf(float(snap["weight"]) - 2.8) < 0.01)
	var slots_have_names := true
	for slot_text in snap["slots"]:
		if not String(slot_text).contains("COMPONENTE UI"):
			slots_have_names = false
	_check("slots_show_names", slots_have_names)

	scene.player._drop_carried_or_inventory()
	await get_tree().process_frame
	snap = ui.get_snapshot()
	_check("drop_updates_slot_count", int(snap["count"]) == 3)
	_check("drop_frees_last_slot", not String(snap["slots"][3]).contains("COMPONENTE UI"))
	_check("near_limit_warning", bool(snap["warning_active"]) and String(snap["warning"]).contains("RANURA"))
	_check("weight_total_2_1", absf(float(snap["weight"]) - 2.1) < 0.01)

	# Cambio de sector: la UI sigue abierta y conserva los datos reales.
	await scene.transition_to_reception(scene.player)
	await get_tree().process_frame
	_check("sector_transition", scene.current_area == "RECEPTION")
	snap = ui.get_snapshot()
	_check("ui_open_after_transition", ui.is_open() and bool(snap["open"]))
	_check("inventory_preserved_after_transition", int(snap["count"]) == 3 and absf(float(snap["weight"]) - 2.1) < 0.01)

	_press_action(ui, "inventory")
	await get_tree().process_frame
	_check("panel_closes_final", not ui.is_open() and not panel.visible)

	_finish()


func _has_key(action: String, key: Key) -> bool:
	for event in InputMap.action_get_events(action):
		if event is InputEventKey and (event as InputEventKey).physical_keycode == key:
			return true
	return false


func _press_action(ui: FMInventoryUI, action: String) -> void:
	var event := InputEventAction.new()
	event.action = action
	event.pressed = true
	ui._unhandled_input(event)


func _wait(seconds: float) -> void:
	await get_tree().create_timer(seconds).timeout


func _check(name: String, condition: bool) -> void:
	if condition:
		passes += 1
		print("INV_UI_TEST: %s OK" % name)
	else:
		fails += 1
		print("INV_UI_TEST: %s FAIL" % name)


func _finish() -> void:
	if fails == 0:
		print("FM_INVENTORY_UI_TEST: PASS (%d PASS / 0 FAIL)" % passes)
		get_tree().quit(0)
	else:
		print("FM_INVENTORY_UI_TEST: FAIL (%d PASS / %d FAIL)" % [passes, fails])
		get_tree().quit(1)
