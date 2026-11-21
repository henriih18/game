class_name FMGraphicsPanel
extends Control

## Panel de ajustes gráficos de FRECUENCIA MUERTA.
##
## Se instancia oculto en el menú principal. Construye la UI en código para
## mantener la estética técnica de NEXUS sin añadir un tema nuevo. Aplica los
## presets del autoload `Graphics` en caliente; no toca gameplay.

signal closed

const ACCENT := Color(0.32, 0.68, 0.46, 1.0)
const ACCENT_DIM := Color(0.16, 0.30, 0.24, 1.0)
const TEXT := Color(0.84, 0.87, 0.82, 1.0)
const TEXT_DIM := Color(0.56, 0.62, 0.58, 1.0)
const PANEL_BG := Color(0.035, 0.045, 0.050, 1.0)
const BUTTON_BG := Color(0.065, 0.08, 0.075, 1.0)
const BUTTON_HOVER := Color(0.10, 0.145, 0.12, 1.0)

var _graphics: FMGraphicsPresets
var _buttons: Dictionary = {}
var _info: Label
var _active: Label


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	visible = false
	_graphics = get_node_or_null("/root/Graphics") as FMGraphicsPresets
	_build()
	if _graphics != null and not _graphics.preset_changed.is_connected(_on_preset_changed):
		_graphics.preset_changed.connect(_on_preset_changed)


func open() -> void:
	visible = true
	_refresh()
	var current: Button = null
	if _graphics != null:
		current = _buttons.get(_graphics.get_current_preset()) as Button
	if current != null:
		current.grab_focus()


func close_panel() -> void:
	if not visible:
		return
	visible = false
	closed.emit()


func is_open() -> bool:
	return visible


func get_preset_button(preset_id: String) -> Button:
	return _buttons.get(preset_id) as Button


func get_preset_button_count() -> int:
	return _buttons.size()


func _unhandled_input(event: InputEvent) -> void:
	if not visible:
		return
	if event.is_action_pressed("ui_cancel"):
		close_panel()
		get_viewport().set_input_as_handled()


func _build() -> void:
	var dim := ColorRect.new()
	dim.name = "Dim"
	dim.color = Color(0.0, 0.0, 0.0, 0.86)
	dim.mouse_filter = Control.MOUSE_FILTER_STOP
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(dim)

	var center := CenterContainer.new()
	center.name = "Center"
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(center)

	var panel := PanelContainer.new()
	panel.name = "Panel"
	panel.custom_minimum_size = Vector2(700, 620)
	panel.add_theme_stylebox_override("panel", _panel_style())
	center.add_child(panel)

	var margin := MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 30)
	margin.add_theme_constant_override("margin_right", 30)
	margin.add_theme_constant_override("margin_top", 24)
	margin.add_theme_constant_override("margin_bottom", 24)
	panel.add_child(margin)

	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 9)
	margin.add_child(box)

	var title := Label.new()
	title.text = "AJUSTES GRÁFICOS // NEXUS"
	title.add_theme_font_size_override("font_size", 24)
	title.add_theme_color_override("font_color", ACCENT)
	box.add_child(title)

	var subtitle := Label.new()
	subtitle.text = "Perfiles para la GTX 1650 Ti de referencia. Cambian al instante y no afectan a la partida."
	subtitle.add_theme_font_size_override("font_size", 13)
	subtitle.add_theme_color_override("font_color", TEXT_DIM)
	subtitle.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	box.add_child(subtitle)

	var line := ColorRect.new()
	line.color = ACCENT_DIM
	line.custom_minimum_size = Vector2(0, 2)
	box.add_child(line)

	_active = Label.new()
	_active.add_theme_font_size_override("font_size", 14)
	_active.add_theme_color_override("font_color", TEXT)
	box.add_child(_active)

	for preset_id in FMGraphicsPresets.PRESET_ORDER:
		var preset: Dictionary = FMGraphicsPresets.PRESETS[preset_id]
		var button := Button.new()
		button.name = "Preset_%s" % preset_id
		button.custom_minimum_size = Vector2(0, 50)
		button.alignment = HORIZONTAL_ALIGNMENT_LEFT
		button.add_theme_font_size_override("font_size", 15)
		button.add_theme_color_override("font_color", TEXT)
		button.add_theme_color_override("font_hover_color", ACCENT)
		button.add_theme_color_override("font_focus_color", ACCENT)
		button.add_theme_stylebox_override("normal", _button_style(BUTTON_BG, ACCENT_DIM))
		button.add_theme_stylebox_override("hover", _button_style(BUTTON_HOVER, ACCENT))
		button.add_theme_stylebox_override("pressed", _button_style(ACCENT_DIM, ACCENT))
		button.add_theme_stylebox_override("focus", _button_style(Color(0, 0, 0, 0), ACCENT))
		button.set_meta("base_text", "%s · %s" % [str(preset["label"]).to_upper(), str(preset["summary"])])
		button.pressed.connect(_on_preset_pressed.bind(preset_id))
		box.add_child(button)
		_buttons[preset_id] = button

	_info = Label.new()
	_info.custom_minimum_size = Vector2(0, 132)
	_info.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_info.add_theme_font_size_override("font_size", 13)
	_info.add_theme_color_override("font_color", TEXT_DIM)
	box.add_child(_info)

	var actions := HBoxContainer.new()
	actions.add_theme_constant_override("separation", 10)
	box.add_child(actions)

	var reset := Button.new()
	reset.name = "ResetButton"
	reset.text = "RESTABLECER MEDIO"
	reset.custom_minimum_size = Vector2(0, 40)
	reset.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	reset.add_theme_font_size_override("font_size", 14)
	reset.pressed.connect(_on_reset_pressed)
	actions.add_child(reset)

	var back := Button.new()
	back.name = "CloseButton"
	back.text = "VOLVER"
	back.custom_minimum_size = Vector2(0, 40)
	back.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	back.add_theme_font_size_override("font_size", 14)
	back.pressed.connect(close_panel)
	actions.add_child(back)

	if _graphics == null:
		for button in _buttons.values():
			(button as Button).disabled = true
		_info.text = "Sistema de presets no disponible."


func _refresh() -> void:
	if _graphics == null:
		return
	var current := _graphics.get_current_preset()
	if not FMGraphicsPresets.PRESETS.has(current):
		return
	_active.text = "PRESET ACTIVO: %s" % str(FMGraphicsPresets.PRESETS[current]["label"]).to_upper()
	for preset_id in _buttons:
		var button := _buttons[preset_id] as Button
		var base := str(button.get_meta("base_text", button.text))
		button.text = ("▶  " if preset_id == current else "    ") + base
		button.add_theme_color_override(
			"font_color", ACCENT if preset_id == current else TEXT
		)
	_info.text = _graphics.describe_preset(current)


func _on_preset_pressed(preset_id: String) -> void:
	if _graphics == null:
		return
	_graphics.apply_preset(preset_id)
	_refresh()


func _on_reset_pressed() -> void:
	if _graphics == null:
		return
	_graphics.apply_preset(_graphics.get_default_preset())
	_refresh()


func _on_preset_changed(_preset_id: String) -> void:
	if visible:
		_refresh()


func _panel_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = PANEL_BG
	style.border_color = ACCENT_DIM
	style.set_border_width_all(1)
	style.set_corner_radius_all(2)
	return style


func _button_style(color: Color, border: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = color
	style.border_color = border
	style.border_width_left = 3
	style.border_width_top = 0
	style.border_width_right = 0
	style.border_width_bottom = 0
	style.content_margin_left = 14
	style.content_margin_right = 14
	style.content_margin_top = 8
	style.content_margin_bottom = 8
	return style
