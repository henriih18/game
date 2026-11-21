class_name FMInventoryUI
extends CanvasLayer

## Panel de consulta del inventario del vertical slice.
##
## Es deliberadamente de solo lectura: no pausa la partida, no cambia el modo
## del ratón y no altera el inventario, el peso ni las reglas de extracción.
## Se abre y cierra con la acción `inventory` (I por defecto) y refresca sus
## datos cada frame mientras está visible.
##
## La estética sigue la identidad de NEXUS: verde oscuro, gris industrial y
## naranja de seguridad, coherente con FMHUD.

const SLOT_COUNT := 4
const PANEL_SIZE := Vector2(438.0, 452.0)
const PANEL_POSITION := Vector2(818.0, 146.0)

const COL_BG := Color(0.012, 0.022, 0.022, 0.94)
const COL_CARD := Color(0.020, 0.035, 0.032, 0.92)
const COL_BORDER := Color(0.24, 0.42, 0.34, 0.82)
const COL_BORDER_DIM := Color(0.24, 0.42, 0.34, 0.38)
const COL_GREEN := Color(0.44, 0.78, 0.66)
const COL_GREEN_DIM := Color(0.56, 0.64, 0.58)
const COL_TEXT := Color(0.92, 0.94, 0.88)
const COL_ORANGE := Color(0.95, 0.62, 0.28)
const COL_RED := Color(0.92, 0.32, 0.22)

var player: FMPlayer

var _panel: Panel
var _hands_name: Label
var _hands_meta: Label
var _count_label: Label
var _total_label: Label
var _weight_fill: ColorRect
var _warning: Label
var _slots: Array[Dictionary] = []
var _open := false
var _warning_active := false


func _ready() -> void:
	layer = 12
	_build()
	set_open(false)


func setup(target: FMPlayer) -> void:
	player = target
	refresh()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("inventory"):
		toggle()
		get_viewport().set_input_as_handled()


func _process(_delta: float) -> void:
	if _open:
		refresh()


func is_open() -> bool:
	return _open


func toggle() -> void:
	set_open(not _open)


func set_open(value: bool) -> void:
	_open = value
	if _panel != null:
		_panel.visible = _open
	if _open:
		refresh()


func close() -> void:
	set_open(false)


## Instantánea de lo que la UI está mostrando ahora mismo. Pensada para las
## pruebas y para depuración; no sustituye la lógica del jugador.
func get_snapshot() -> Dictionary:
	var slot_names: Array[String] = []
	var slot_weights: Array[String] = []
	for slot in _slots:
		slot_names.append((slot["name"] as Label).text)
		slot_weights.append((slot["weight"] as Label).text)
	var data := {
		"open": _open,
		"panel_visible": _panel != null and _panel.visible,
		"hands_name": _hands_name.text if _hands_name != null else "",
		"hands_meta": _hands_meta.text if _hands_meta != null else "",
		"count_text": _count_label.text if _count_label != null else "",
		"total_text": _total_label.text if _total_label != null else "",
		"warning": _warning.text if _warning != null else "",
		"warning_active": _warning_active,
		"slots": slot_names,
		"slot_weights": slot_weights,
	}
	if player != null and is_instance_valid(player):
		var held := player.carried_item as FMCarryItem
		data["count"] = player.get_inventory_count()
		data["capacity"] = player.inventory_capacity
		data["weight"] = player.get_carry_weight()
		data["max_weight"] = player.max_carry_weight
		data["hands_mission"] = held != null and held.is_mission_item
	else:
		data["count"] = 0
		data["capacity"] = 0
		data["weight"] = 0.0
		data["max_weight"] = 0.0
		data["hands_mission"] = false
	return data


func refresh() -> void:
	if _hands_name == null:
		return
	if player == null or not is_instance_valid(player):
		_set_hands_empty()
		_count_label.text = "RANURAS  0 / 0"
		_total_label.text = "CARGA TOTAL   0.0 / 0.0 kg"
		_weight_fill.size.x = 0.0
		_set_warning("", false)
		for slot in _slots:
			_set_slot_empty(slot)
		return

	_refresh_hands()
	_refresh_inventory()
	_refresh_weight()


func _build() -> void:
	_panel = Panel.new()
	_panel.name = "InventoryPanel"
	_panel.position = PANEL_POSITION
	_panel.size = PANEL_SIZE
	_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var style := StyleBoxFlat.new()
	style.bg_color = COL_BG
	style.border_color = COL_BORDER
	style.set_border_width_all(1)
	style.set_corner_radius_all(6)
	_panel.add_theme_stylebox_override("panel", style)
	add_child(_panel)

	var accent := ColorRect.new()
	accent.name = "Accent"
	accent.position = Vector2(0, 0)
	accent.size = Vector2(4, 52)
	accent.color = COL_ORANGE
	accent.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_panel.add_child(accent)

	_label(_panel, "Title", Vector2(18, 10), Vector2(280, 30), "INVENTARIO", 23, COL_TEXT)
	_label(_panel, "Brand", Vector2(18, 40), Vector2(300, 16),
		"NEXUS // REGISTRO DE CARGA  ·  EQUIPO DE RECUPERACIÓN", 10, COL_GREEN)
	var close_hint := _label(_panel, "CloseHint", Vector2(292, 16), Vector2(128, 20),
		"I  CERRAR", 11, COL_ORANGE)
	close_hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT

	var separator := ColorRect.new()
	separator.name = "HeaderSeparator"
	separator.position = Vector2(18, 62)
	separator.size = Vector2(402, 1)
	separator.color = Color(0.72, 0.52, 0.18, 0.62)
	separator.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_panel.add_child(separator)

	_label(_panel, "HandsSection", Vector2(18, 72), Vector2(200, 16), "EN MANOS", 11, COL_GREEN_DIM)

	var hands_card := Panel.new()
	hands_card.name = "HandsCard"
	hands_card.position = Vector2(18, 90)
	hands_card.size = Vector2(402, 58)
	hands_card.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hands_card.add_theme_stylebox_override("panel", _card_style())
	_panel.add_child(hands_card)

	_hands_name = _label(hands_card, "HandsName", Vector2(12, 6), Vector2(378, 24),
		"SIN OBJETO EN MANOS", 16, COL_GREEN_DIM)
	_hands_meta = _label(hands_card, "HandsMeta", Vector2(12, 32), Vector2(378, 18),
		"Las manos están libres", 11, COL_GREEN_DIM)

	_label(_panel, "InventorySection", Vector2(18, 156), Vector2(200, 16),
		"RANURAS DE INVENTARIO", 11, COL_GREEN_DIM)
	_count_label = _label(_panel, "CountLabel", Vector2(240, 156), Vector2(180, 16),
		"RANURAS  0 / 4", 11, COL_GREEN_DIM)
	_count_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT

	var first_slot_y := 178.0
	var slot_height := 42.0
	var slot_gap := 4.0
	for i in range(SLOT_COUNT):
		var row := Panel.new()
		row.name = "Slot%d" % (i + 1)
		row.position = Vector2(18, first_slot_y + float(i) * (slot_height + slot_gap))
		row.size = Vector2(402, slot_height)
		row.mouse_filter = Control.MOUSE_FILTER_IGNORE
		row.add_theme_stylebox_override("panel", _card_style())
		_panel.add_child(row)

		var index := _label(row, "Index", Vector2(10, 0), Vector2(26, slot_height),
			"%02d" % (i + 1), 12, Color(0.38, 0.47, 0.42))
		index.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		var slot_name := _label(row, "ItemName", Vector2(40, 0), Vector2(252, slot_height),
			"RANURA VACÍA", 13, COL_GREEN_DIM)
		slot_name.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		var weight := _label(row, "ItemWeight", Vector2(296, 0), Vector2(94, slot_height),
			"—", 12, COL_GREEN_DIM)
		weight.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		weight.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		_slots.append({"panel": row, "name": slot_name, "weight": weight})

	_total_label = _label(_panel, "TotalLabel", Vector2(18, 364), Vector2(402, 18),
		"CARGA TOTAL   0.0 / 12.0 kg", 12, COL_GREEN_DIM)

	var bar_back := ColorRect.new()
	bar_back.name = "WeightBarBack"
	bar_back.position = Vector2(18, 386)
	bar_back.size = Vector2(402, 6)
	bar_back.color = Color(0.05, 0.08, 0.07, 0.95)
	bar_back.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_panel.add_child(bar_back)

	_weight_fill = ColorRect.new()
	_weight_fill.name = "WeightBarFill"
	_weight_fill.position = Vector2(18, 386)
	_weight_fill.size = Vector2(0, 6)
	_weight_fill.color = COL_GREEN
	_weight_fill.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_panel.add_child(_weight_fill)

	_warning = _label(_panel, "Warning", Vector2(18, 400), Vector2(402, 18),
		"CAPACIDAD OPERATIVA", 11, COL_GREEN_DIM)

	_label(_panel, "Footer", Vector2(18, 424), Vector2(402, 16),
		"CONSULTA EN TIEMPO REAL  ·  LA PARTIDA NO SE DETIENE", 10,
		Color(0.36, 0.43, 0.39))


func _card_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = COL_CARD
	style.border_color = COL_BORDER_DIM
	style.set_border_width_all(1)
	style.set_corner_radius_all(4)
	return style


func _label(parent: Control, node_name: String, pos: Vector2, size: Vector2,
		text: String, font_size: int, color: Color) -> Label:
	var label := Label.new()
	label.name = node_name
	label.position = pos
	label.size = size
	label.text = text
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	label.add_theme_color_override("font_outline_color", Color(0.005, 0.01, 0.012, 0.95))
	label.add_theme_constant_override("outline_size", 2)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(label)
	return label


func _refresh_hands() -> void:
	var held := player.carried_item as FMCarryItem
	if held == null or not is_instance_valid(held):
		_set_hands_empty()
		return
	_hands_name.text = held.item_name
	var kind := "OBJETO DE MISIÓN" if held.is_mission_item else "COMPONENTE RECUPERABLE"
	_hands_meta.text = "%.1f kg  ·  %s  ·  %s" % [held.item_mass, held.size_class, kind]
	_hands_name.add_theme_color_override("font_color", COL_ORANGE if held.is_mission_item else COL_TEXT)
	_hands_meta.add_theme_color_override("font_color", COL_ORANGE if held.is_mission_item else COL_GREEN_DIM)


func _set_hands_empty() -> void:
	_hands_name.text = "SIN OBJETO EN MANOS"
	_hands_meta.text = "Las manos están libres"
	_hands_name.add_theme_color_override("font_color", COL_GREEN_DIM)
	_hands_meta.add_theme_color_override("font_color", Color(0.42, 0.49, 0.45))


func _refresh_inventory() -> void:
	var count := mini(player.get_inventory_count(), player.inventory.size())
	var capacity := player.inventory_capacity
	_count_label.text = "RANURAS  %d / %d" % [count, capacity]
	_count_label.add_theme_color_override("font_color", COL_ORANGE if count >= capacity else COL_GREEN_DIM)

	for i in range(SLOT_COUNT):
		var slot: Dictionary = _slots[i]
		var item: FMCarryItem = null
		if i < player.inventory.size():
			item = player.inventory[i]
		if item == null or not is_instance_valid(item):
			_set_slot_empty(slot)
			continue
		var item_name := item.item_name
		if item.is_mission_item:
			item_name = "◆ " + item_name
		(slot["name"] as Label).text = item_name
		(slot["name"] as Label).add_theme_color_override("font_color",
			COL_ORANGE if item.is_mission_item else COL_TEXT)
		(slot["weight"] as Label).text = "%.1f kg" % item.item_mass
		(slot["weight"] as Label).add_theme_color_override("font_color", COL_GREEN_DIM)


func _set_slot_empty(slot: Dictionary) -> void:
	(slot["name"] as Label).text = "RANURA VACÍA"
	(slot["name"] as Label).add_theme_color_override("font_color", Color(0.36, 0.43, 0.39))
	(slot["weight"] as Label).text = "—"
	(slot["weight"] as Label).add_theme_color_override("font_color", Color(0.36, 0.43, 0.39))


func _refresh_weight() -> void:
	var weight := player.get_carry_weight()
	var max_weight := player.max_carry_weight
	var count := player.get_inventory_count()
	var capacity := player.inventory_capacity
	var ratio := clampf(weight / maxf(0.001, max_weight), 0.0, 1.0)

	_total_label.text = "CARGA TOTAL   %.1f / %.1f kg" % [weight, max_weight]
	_total_label.add_theme_color_override("font_color", COL_ORANGE if ratio >= 0.85 else COL_GREEN_DIM)
	_weight_fill.size.x = 402.0 * ratio
	if ratio >= 0.999:
		_weight_fill.color = COL_RED
	elif ratio >= 0.85:
		_weight_fill.color = COL_ORANGE
	else:
		_weight_fill.color = COL_GREEN

	if count >= capacity and capacity > 0:
		_set_warning("INVENTARIO LLENO  ·  NO SE PUEDEN GUARDAR MÁS OBJETOS", true)
	elif weight >= max_weight - 0.001:
		_set_warning("CARGA MÁXIMA  ·  SOLTÁ PESO PARA RECOGER MÁS", true)
	elif ratio >= 0.85:
		_set_warning("CARGA CRÍTICA  ·  CERCA DEL LÍMITE DE PESO", true)
	elif count >= capacity - 1 and capacity > 0:
		_set_warning("AVISO  ·  SOLO QUEDA 1 RANURA LIBRE", true)
	else:
		_set_warning("CAPACIDAD OPERATIVA", false)


func _set_warning(text: String, active: bool) -> void:
	_warning_active = active
	_warning.text = text
	if not active:
		_warning.add_theme_color_override("font_color", COL_GREEN_DIM)
	elif text.begins_with("INVENTARIO LLENO") or text.begins_with("CARGA MÁXIMA"):
		_warning.add_theme_color_override("font_color", COL_RED)
	else:
		_warning.add_theme_color_override("font_color", COL_ORANGE)
