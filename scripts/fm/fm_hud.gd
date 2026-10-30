class_name FMHUD
extends CanvasLayer

## HUD del vertical slice. La estética es deliberadamente técnica y sobria:
## NEXUS no es una interfaz de videojuego heroico, es una herramienta de campo.

var _root: Control
var _objective: Label
var _objective_sub: Label
var _status: Label
var _prompt_panel: Panel
var _prompt: Label
var _battery_fill: ColorRect
var _battery_label: Label
var _stress_fill: ColorRect
var _stress_label: Label
var _stamina_fill: ColorRect
var _hidden_label: Label
var _observer_label: Label
var _vignette: ColorRect
var _vignette_mat: ShaderMaterial
var _crosshair: ColorRect
var _overlay: ColorRect
var _result: Label
var _result_sub: Label
var _time := 0.0

func _ready() -> void:
	layer = 10
	_build_root()
	_build_vignette()
	_build_header()
	_build_bars()
	_build_prompt()
	_build_overlay()

func _build_root() -> void:
	_root = Control.new()
	_root.name = "HUDRoot"
	_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_root)

func _build_vignette() -> void:
	_vignette = ColorRect.new()
	_vignette.name = "DangerVignette"
	_vignette.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_vignette.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var shader := load("res://assets/shaders/vignette.gdshader") as Shader
	_vignette_mat = ShaderMaterial.new()
	_vignette_mat.shader = shader
	_vignette_mat.set_shader_parameter("intensity", 0.0)
	_vignette_mat.set_shader_parameter("danger_color", Color(0.72, 0.05, 0.04))
	_vignette.material = _vignette_mat
	_root.add_child(_vignette)

func _build_header() -> void:
	var brand := _label(Vector2(24, 18), Vector2(430, 20), "NEXUS // RECUPERACIÓN  ·  SECTOR 04", 13, Color(0.44, 0.78, 0.66))
	_root.add_child(brand)

	_objective = _label(Vector2(24, 40), Vector2(560, 34), "RECUPERAR EL NÚCLEO", 25, Color(0.92, 0.94, 0.88))
	_root.add_child(_objective)

	_objective_sub = _label(Vector2(25, 76), Vector2(560, 22), "Laboratorio de contención  ·  extracción al final del corredor", 13, Color(0.56, 0.62, 0.58))
	_root.add_child(_objective_sub)

	_status = _label(Vector2(24, 102), Vector2(560, 20), "", 13, Color(0.78, 0.7, 0.46))
	_root.add_child(_status)

	_observer_label = _label(Vector2(440, 18), Vector2(400, 22), "EL VIGILANTE ESTÁ INMÓVIL", 14, Color(1.0, 0.62, 0.32))
	_observer_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_observer_label.visible = false
	_root.add_child(_observer_label)

	_hidden_label = _label(Vector2(440, 42), Vector2(400, 22), "ESCONDIDO", 15, Color(0.5, 0.9, 0.72))
	_hidden_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_hidden_label.visible = false
	_root.add_child(_hidden_label)

func _build_bars() -> void:
	var panel := Panel.new()
	panel.position = Vector2(1000, 18)
	panel.size = Vector2(256, 96)
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.018, 0.03, 0.03, 0.78)
	style.border_color = Color(0.24, 0.42, 0.34, 0.65)
	style.set_border_width_all(1)
	style.set_corner_radius_all(5)
	panel.add_theme_stylebox_override("panel", style)
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_root.add_child(panel)

	_battery_label = _label(Vector2(1012, 25), Vector2(230, 18), "LINTERNA  100%", 12, Color(0.74, 0.78, 0.7))
	_root.add_child(_battery_label)
	_root.add_child(_bar_back(Vector2(1012, 45), Vector2(230, 8), Color(0.05, 0.08, 0.07)))
	_battery_fill = _bar_fill(Vector2(1012, 45), Vector2(230, 8), Color(0.74, 0.52, 0.18))
	_root.add_child(_battery_fill)

	_stress_label = _label(Vector2(1012, 58), Vector2(230, 18), "ESTRÉS  0%", 12, Color(0.74, 0.78, 0.7))
	_root.add_child(_stress_label)
	_root.add_child(_bar_back(Vector2(1012, 78), Vector2(230, 8), Color(0.08, 0.04, 0.04)))
	_stress_fill = _bar_fill(Vector2(1012, 78), Vector2(230, 8), Color(0.7, 0.12, 0.08))
	_root.add_child(_stress_fill)

	_stamina_fill = _bar_fill(Vector2(1012, 96), Vector2(230, 4), Color(0.3, 0.55, 0.62))
	_root.add_child(_stamina_fill)

func _build_prompt() -> void:
	_prompt_panel = Panel.new()
	_prompt_panel.name = "PromptPanel"
	_prompt_panel.position = Vector2(390, 610)
	_prompt_panel.size = Vector2(500, 46)
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.015, 0.025, 0.028, 0.86)
	style.border_color = Color(0.5, 0.38, 0.16, 0.85)
	style.set_border_width_all(1)
	style.set_corner_radius_all(6)
	_prompt_panel.add_theme_stylebox_override("panel", style)
	_prompt_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_prompt_panel.visible = false
	_root.add_child(_prompt_panel)

	_prompt = _label(Vector2(0, 0), Vector2(500, 46), "", 16, Color(0.95, 0.82, 0.48))
	_prompt.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_prompt.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_prompt_panel.add_child(_prompt)

	_crosshair = ColorRect.new()
	_crosshair.position = Vector2(638, 358)
	_crosshair.size = Vector2(4, 4)
	_crosshair.color = Color(0.86, 0.9, 0.82, 0.8)
	_crosshair.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_root.add_child(_crosshair)

	var hint := _label(Vector2(24, 688), Vector2(860, 18), "WASD MOVER   ·   SHIFT CORRER   ·   CTRL AGACHARSE   ·   E INTERACTUAR   ·   F LINTERNA   ·   Q SOLTAR   ·   ESC MENÚ   ·   M SILENCIO", 11, Color(0.42, 0.47, 0.44))
	_root.add_child(hint)

func _build_overlay() -> void:
	_overlay = ColorRect.new()
	_overlay.name = "EndOverlay"
	_overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_overlay.color = Color(0.005, 0.01, 0.012, 0.82)
	_overlay.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_overlay.visible = false
	_root.add_child(_overlay)

	_result = _label(Vector2(140, 260), Vector2(1000, 80), "", 48, Color(0.9, 0.95, 0.88))
	_result.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_result.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_overlay.add_child(_result)

	_result_sub = _label(Vector2(240, 350), Vector2(800, 40), "", 17, Color(0.62, 0.72, 0.64))
	_result_sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_result_sub.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_overlay.add_child(_result_sub)

func _label(pos: Vector2, size: Vector2, text: String, font_size: int, color: Color) -> Label:
	var label := Label.new()
	label.position = pos
	label.size = size
	label.text = text
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	label.add_theme_color_override("font_outline_color", Color(0.005, 0.01, 0.012, 0.95))
	label.add_theme_constant_override("outline_size", 3)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return label

func _bar_back(pos: Vector2, size: Vector2, color: Color) -> ColorRect:
	var bar := ColorRect.new()
	bar.position = pos
	bar.size = size
	bar.color = color
	bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return bar

func _bar_fill(pos: Vector2, size: Vector2, color: Color) -> ColorRect:
	var bar := ColorRect.new()
	bar.position = pos
	bar.size = size
	bar.color = color
	bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return bar

func _process(delta: float) -> void:
	_time += delta
	if _observer_label.visible:
		_observer_label.modulate.a = 0.72 + sin(_time * 7.0) * 0.22
	if _hidden_label.visible:
		_hidden_label.modulate.a = 0.75 + sin(_time * 2.4) * 0.15

func set_objective(title: String, subtitle: String) -> void:
	_objective.text = title
	_objective_sub.text = subtitle

func set_status(text: String) -> void:
	_status.text = text

func set_battery(value: float, on: bool) -> void:
	var ratio := clampf(value / 100.0, 0.0, 1.0)
	_battery_fill.size.x = 230.0 * ratio
	_battery_label.text = "LINTERNA  %d%%%s" % [int(round(value)), "" if on else "  ·  APAGADA"]
	_battery_fill.color = Color(0.78, 0.25, 0.15) if ratio < 0.2 else Color(0.74, 0.52, 0.18)

func set_stress(value: float) -> void:
	var ratio := clampf(value / 100.0, 0.0, 1.0)
	_stress_fill.size.x = 230.0 * ratio
	_stress_label.text = "ESTRÉS  %d%%" % [int(round(value))]
	if _vignette_mat != null:
		_vignette_mat.set_shader_parameter("intensity", ratio * 0.62)
	_crosshair.color = Color(1.0, 0.38, 0.3, 0.9) if ratio > 0.72 else Color(0.86, 0.9, 0.82, 0.8)

func set_stamina(value: float) -> void:
	_stamina_fill.size.x = 230.0 * clampf(value / 100.0, 0.0, 1.0)

func set_prompt(text: String) -> void:
	_prompt.text = text
	_prompt_panel.visible = not text.is_empty()

func set_hidden(value: bool) -> void:
	_hidden_label.visible = value

func set_watcher_observed(value: bool) -> void:
	_observer_label.visible = value

func show_end(title: String, subtitle: String) -> void:
	_result.text = title
	_result_sub.text = subtitle
	_overlay.visible = true
	_prompt_panel.visible = false
	_observer_label.visible = false
	_hidden_label.visible = false
