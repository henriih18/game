extends "res://scripts/demo3d.gd"

var prompt_label: Label
var prompt_panel: Panel
var crosshair: ColorRect

func _ready() -> void:
	first_person = true
	super._ready()
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _build_room() -> void:
	super._build_room()

	var wall_color := Color(0.13, 0.16, 0.23)
	var ceiling_color := Color(0.11, 0.14, 0.21)

	var ceiling := _box(_level, Vector3(0, 4.42, 0), Vector3(26, 0.25, 18), ceiling_color)
	ceiling.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	for x in [-9.75, -3.25, 3.25, 9.75]:
		for z in [-6.0, -2.0, 2.0, 6.0]:
			var panel := _box(
				_level,
				Vector3(x, 4.27, z),
				Vector3(5.55, 0.055, 3.45),
				Color(0.14, 0.18, 0.27)
			)
			panel.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			var seam := _box(
				_level,
				Vector3(x, 4.235, z),
				Vector3(5.35, 0.012, 3.25),
				Color(0.065, 0.085, 0.13)
			)
			seam.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF

	for x in [-8.6, 0.0, 8.6]:
		var beam := _box(_level, Vector3(x, 4.24, 0), Vector3(0.14, 0.16, 17.8), Color(0.09, 0.12, 0.18))
		beam.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF

	for z in [-5.2, -1.4, 2.4, 6.2]:
		var strip := _box(_level, Vector3(0, 4.225, z), Vector3(23.5, 0.025, 0.09), Color(0.4, 0.7, 0.95))
		strip.material_override = _emissive(Color(0.42, 0.72, 1.0), 1.15)
		strip.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF

	# Cierra la cuarta pared que la cámara elevada no necesitaba.
	_box(_level, Vector3(0, 2.0, 9.0), Vector3(26, 4.0, 0.6), wall_color, true)
	_box(_level, Vector3(0, 4.2, 9.0), Vector3(26, 0.5, 0.6), wall_color)
	_box(_level, Vector3(0, 2.0, -9.0), Vector3(26, 0.45, 0.05), Color(0.08, 0.1, 0.15))
	for side in [-1.0, 1.0]:
		_box(_level, Vector3(12.8 * side, 4.2, 0), Vector3(0.6, 0.5, 18), wall_color)
	_box(_level, Vector3(0, 4.2, -9.0), Vector3(26, 0.5, 0.6), wall_color)

func _build_players() -> void:
	var root := Node3D.new()
	root.name = "Players"
	add_child(root)

	var player := PlayerFP3D.new()
	player.name = "P1"
	player.player_index = 0
	player.game_id = 1
	player.game = self
	player.color = Color(0.545, 0.361, 0.965)
	player.position = Vector3(-4.4, 0.0, 4.8)
	player.rotation.y = 0.0
	root.add_child(player)
	players[1] = player

	var previous_camera := camera3d
	camera3d = player.fp_camera
	camera_base_fov = 76.0
	camera3d.current = true
	if previous_camera != null:
		previous_camera.current = false
		previous_camera.queue_free()

func _build_crate() -> void:
	super._build_crate()
	crate.position = Vector3(-4.4, 0.58, 1.8)
	crate.scale = Vector3(0.72, 0.72, 0.72)

func _build_hud() -> void:
	super._build_hud()
	if hint_label != null:
		hint_label.text = "WASD + mouse para mirar   ·   E agarrar/soltar   ·   H desactivar balanceo   ·   M silencio   ·   Esc menú"
	if demo_badge != null:
		demo_badge.text = "DEMO 3D  ·  PRIMERA PERSONA  ·  1 JUGADOR"

	var hud := get_node("HUD")
	crosshair = ColorRect.new()
	crosshair.name = "Crosshair"
	crosshair.position = Vector2(638, 358)
	crosshair.size = Vector2(4, 4)
	crosshair.color = Color(0.9, 0.94, 1.0, 0.8)
	crosshair.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hud.add_child(crosshair)

	prompt_panel = Panel.new()
	prompt_panel.name = "PromptPanel"
	prompt_panel.position = Vector2(24, 604)
	prompt_panel.size = Vector2(300, 38)
	var panel_style := StyleBoxFlat.new()
	panel_style.bg_color = Color(0.025, 0.038, 0.07, 0.82)
	panel_style.border_color = Color(0.62, 0.48, 0.22, 0.8)
	panel_style.set_border_width_all(1)
	panel_style.set_corner_radius_all(8)
	prompt_panel.add_theme_stylebox_override("panel", panel_style)
	prompt_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	prompt_panel.visible = false
	hud.add_child(prompt_panel)

	prompt_label = _hud_label(
		prompt_panel,
		Vector2(0, 0),
		Vector2(300, 38),
		"",
		16,
		Color(0.98, 0.82, 0.48)
	)
	prompt_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	prompt_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER

func _update_hud() -> void:
	super._update_hud()
	if prompt_label == null:
		return
	var show_prompt := false
	var text := ""
	if state == State.PLAYING and crate != null and not crate.delivered and players.has(1):
		var offset: Vector3 = players[1].global_position - crate.global_position
		offset.y = 0.0
		if crate.holder_ids.has(1):
			show_prompt = true
			text = "E   SOLTAR CAJA"
		elif offset.length() <= Player3D.GRAB_RANGE:
			show_prompt = true
			text = "E   AGARRAR CAJA"
	prompt_panel.visible = show_prompt
	prompt_label.text = text
	crosshair.color = Color(1.0, 0.45, 0.38, 0.9) if seen_label != null and seen_label.visible else Color(0.9, 0.94, 1.0, 0.8)
