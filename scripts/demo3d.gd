extends Node3D

enum State { PLAYING, WON, LOST }

const TOTAL_GEMS := 3
const ROUND_TIME := 120.0
const ALARM_MAX := 100.0
const ALARM_RATE := 34.0
const ALARM_DECAY := 10.0
const MENU_SCENE := "res://scenes/menu.tscn"
const PAD_POS := Vector3(9.0, 0.0, 6.0)

var state: int = State.PLAYING
var first_person := false
var time_left := ROUND_TIME
var alarm := 0.0
var gems_collected := 0

var players: Dictionary = {}
var gems: Array = []
var cameras: Array = []
var crate: Crate3D
var pad: Node3D
var pad_ring: MeshInstance3D

var camera3d: Camera3D
var camera_base_fov := 49.0
var alarm_light: OmniLight3D
var danger_material: ShaderMaterial
var status_label: Label
var timer_label: Label
var alarm_label_ref: Label
var seen_label: Label
var hint_label: Label
var demo_badge: Label
var alarm_fill: ColorRect
var overlay: ColorRect
var result_label: Label
var sub_label: Label

var _level: Node3D
var _props: Node3D
var _mat_cache: Dictionary = {}
var _time := 0.0
var _last_tick := -1

func _ready() -> void:
	_build_environment()
	_build_room()
	_build_extraction()
	_build_props()
	_build_players()
	_build_crate()
	_build_gems()
	_build_cameras()
	_build_hud()
	Audio.play_music("heist")

func _build_environment() -> void:
	var world := WorldEnvironment.new()
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.022, 0.031, 0.055)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.33, 0.4, 0.58)
	env.ambient_light_energy = 0.9
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.fog_enabled = true
	env.fog_light_color = Color(0.03, 0.045, 0.085)
	env.fog_light_energy = 0.6
	env.fog_density = 0.007
	env.fog_sky_affect = 0.4
	env.adjustment_enabled = true
	env.adjustment_brightness = 1.06
	env.adjustment_contrast = 1.07
	env.adjustment_saturation = 1.12
	world.environment = env
	add_child(world)

	var sun := DirectionalLight3D.new()
	sun.light_color = Color(1.0, 0.9, 0.78)
	sun.light_energy = 1.4
	sun.rotation_degrees = Vector3(-54, -28, 0)
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 34.0
	add_child(sun)

	var fill := DirectionalLight3D.new()
	fill.light_color = Color(0.5, 0.68, 1.0)
	fill.light_energy = 0.28
	fill.rotation_degrees = Vector3(-38, 148, 0)
	add_child(fill)

	var front_light := OmniLight3D.new()
	front_light.light_color = Color(0.45, 0.6, 1.0)
	front_light.light_energy = 1.1
	front_light.omni_range = 15.0
	front_light.position = Vector3(0, 4.5, 7.5)
	add_child(front_light)

	camera3d = Camera3D.new()
	camera3d.fov = 49.0
	camera3d.near = 0.1
	camera3d.far = 90.0
	camera3d.position = Vector3(0.0, 12.6, 14.8)
	add_child(camera3d)
	camera3d.look_at(Vector3(0.0, 0.0, 0.6), Vector3.UP)
	camera3d.current = true

	alarm_light = OmniLight3D.new()
	alarm_light.light_color = Color(1.0, 0.12, 0.08)
	alarm_light.light_energy = 0.0
	alarm_light.omni_range = 24.0
	alarm_light.position = Vector3(0.0, 5.0, 0.0)
	add_child(alarm_light)

	_level = Node3D.new()
	_level.name = "Level"
	add_child(_level)
	_props = Node3D.new()
	_props.name = "Props"
	_level.add_child(_props)

func _build_room() -> void:
	_box(_level, Vector3(0, -0.3, 0), Vector3(52, 0.35, 40), Color(0.03, 0.04, 0.065))

	var floor_mesh := MeshInstance3D.new()
	var floor_box := BoxMesh.new()
	floor_box.size = Vector3(26, 0.2, 18)
	floor_mesh.mesh = floor_box
	floor_mesh.position = Vector3(0, -0.1, 0)
	var floor_mat := ShaderMaterial.new()
	floor_mat.shader = load("res://assets/shaders/floor3d.gdshader")
	floor_mesh.material_override = floor_mat
	_level.add_child(floor_mesh)
	_collision(_level, Vector3(0, -0.15, 0), Vector3(26, 0.3, 18))

	var wall_color := Color(0.13, 0.16, 0.23)
	_box(_level, Vector3(0, 2.0, -9.0), Vector3(26, 4.0, 0.6), wall_color, true)
	_box(_level, Vector3(-13.0, 2.0, 0.0), Vector3(0.6, 4.0, 18.0), wall_color, true)
	_box(_level, Vector3(13.0, 2.0, 0.0), Vector3(0.6, 4.0, 18.0), wall_color, true)
	_box(_level, Vector3(0, 0.18, 9.05), Vector3(26, 0.36, 0.5), wall_color)

	for x in [-10.4, -5.2, 0.0, 5.2, 10.4]:
		_box(_level, Vector3(x, 1.95, -8.65), Vector3(4.6, 2.7, 0.08), Color(0.16, 0.20, 0.29))

	_box(_level, Vector3(0, 0.16, -8.64), Vector3(25.4, 0.32, 0.08), Color(0.06, 0.08, 0.12))
	_box(_level, Vector3(0, 3.82, -8.64), Vector3(25.4, 0.12, 0.08), Color(0.25, 0.31, 0.44))
	_box(_level, Vector3(0, 3.55, -8.6), Vector3(25.2, 0.045, 0.03), Color(0.2, 0.85, 0.95))
	_box(_level, Vector3(0, 0.04, -8.6), Vector3(25.2, 0.04, 0.03), Color(0.2, 0.85, 0.95))

	for side in [-1.0, 1.0]:
		_box(_level, Vector3(12.66 * side, 0.16, 0), Vector3(0.08, 0.32, 17.4), Color(0.06, 0.08, 0.12))
		_box(_level, Vector3(12.66 * side, 3.55, 0), Vector3(0.03, 0.045, 17.4), Color(0.2, 0.85, 0.95))
		var emergency := _box(_level, Vector3(12.62 * side, 3.15, -4.5), Vector3(0.05, 0.24, 0.5), Color(0.6, 0.1, 0.08))
		emergency.material_override = _emissive(Color(1.0, 0.12, 0.08), 2.2)

	var sign_back := _box(_level, Vector3(0, 3.1, -8.62), Vector3(8.4, 0.92, 0.06), Color(0.035, 0.05, 0.085))
	sign_back.material_override = _emissive(Color(0.03, 0.05, 0.09), 0.15)
	var sign_label := _label3d(
		_level,
		Vector3(0, 3.1, -8.57),
		"BÓVEDA CAÓTICA",
		56,
		Color(0.95, 0.77, 0.35),
		0.011,
		false
	)
	sign_label.outline_size = 10

	var screen_frame := _box(_level, Vector3(-2.4, 2.15, -8.62), Vector3(3.1, 1.35, 0.06), Color(0.04, 0.06, 0.1))
	var wall_screen := _box(_level, Vector3(-2.4, 2.15, -8.58), Vector3(2.8, 1.08, 0.02), Color(0.2, 0.7, 0.8))
	wall_screen.material_override = _emissive(Color(0.18, 0.6, 0.72), 0.45)
	var screen_label := _label3d(_level, Vector3(-2.4, 2.15, -8.54), "SEGURIDAD", 32, Color(0.55, 0.9, 1.0, 0.8), 0.007, false)
	screen_label.outline_size = 0

	for x in [-11.0, -3.5, 3.5, 11.0]:
		_box(_level, Vector3(x, 3.55, -8.52), Vector3(0.08, 0.32, 0.18), Color(0.06, 0.08, 0.12))

func _build_extraction() -> void:
	pad = Node3D.new()
	pad.name = "Extraction"
	pad.position = PAD_POS
	_level.add_child(pad)

	var base := _cylinder(pad, Vector3(0, 0.06, 0), 1.55, 1.55, 0.12, Color(0.07, 0.22, 0.15), 28)
	base.material_override = _emissive(Color(0.08, 0.25, 0.17), 0.14)
	var disc := _cylinder(pad, Vector3(0, 0.13, 0), 1.3, 1.3, 0.035, Color(0.1, 0.5, 0.3), 28)
	disc.material_override = _emissive(Color(0.14, 0.62, 0.36), 0.24)

	var ring := MeshInstance3D.new()
	var torus := TorusMesh.new()
	torus.inner_radius = 1.32
	torus.outer_radius = 1.49
	torus.rings = 36
	torus.ring_segments = 8
	ring.mesh = torus
	ring.position.y = 0.16
	ring.material_override = _emissive(Color(0.3, 0.95, 0.55), 0.8)
	pad.add_child(ring)
	pad_ring = ring

	var light := OmniLight3D.new()
	light.light_color = Color(0.3, 1.0, 0.55)
	light.light_energy = 0.7
	light.omni_range = 3.6
	light.position = Vector3(0, 0.7, 0)
	pad.add_child(light)

	var label := _label3d(pad, Vector3(0, 1.05, 0), "EXTRACCIÓN", 44, Color(0.45, 0.9, 0.63, 0.82), 0.008, true)
	label.no_depth_test = true

	for i in range(8):
		var angle := TAU * float(i) / 8.0
		var stripe := _box(
			_props,
			PAD_POS + Vector3(sin(angle) * 2.2, 0.025, cos(angle) * 2.2),
			Vector3(0.62, 0.025, 0.11),
			Color(0.8, 0.62, 0.15)
		)
		stripe.rotation.y = angle
		stripe.material_override = _emissive(Color(0.9, 0.68, 0.16), 0.22)

func _build_props() -> void:
	for i in range(3):
		var x := -9.7 + float(i) * 1.55
		_box(_props, Vector3(x, 1.2, -8.15), Vector3(1.3, 2.4, 0.72), Color(0.09, 0.12, 0.18), true)
		_box(_props, Vector3(x, 1.2, -7.78), Vector3(1.05, 1.95, 0.05), Color(0.05, 0.07, 0.11))
		for j in range(6):
			var dot := _box(
				_props,
				Vector3(x - 0.4 + float(j % 3) * 0.38, 0.55 + float(j / 3) * 0.42, -7.745),
				Vector3(0.055, 0.055, 0.03),
				Color(0.2, 0.9, 0.6)
			)
			dot.material_override = _emissive(Color(0.2, 1.0, 0.62), 1.8) if (i + j) % 2 == 0 else _emissive(Color(0.3, 0.8, 1.0), 1.5)

	_box(_props, Vector3(5.2, 0.95, -7.0), Vector3(4.0, 0.16, 1.35), Color(0.22, 0.25, 0.33))
	_collision(_props, Vector3(5.2, 0.48, -7.0), Vector3(4.0, 0.95, 1.35))
	for x in [3.4, 7.0]:
		for z in [-7.55, -6.45]:
			_box(_props, Vector3(x, 0.45, z), Vector3(0.13, 0.9, 0.13), Color(0.1, 0.12, 0.17))
	_box(_props, Vector3(5.9, 1.36, -7.32), Vector3(0.92, 0.62, 0.08), Color(0.06, 0.07, 0.1))
	var screen := _box(_props, Vector3(5.9, 1.36, -7.27), Vector3(0.74, 0.44, 0.02), Color(0.2, 0.8, 0.9))
	screen.material_override = _emissive(Color(0.25, 0.9, 1.0), 1.1)
	_box(_props, Vector3(5.0, 1.06, -6.7), Vector3(0.55, 0.035, 0.2), Color(0.08, 0.1, 0.14))

	for pos in [Vector3(-11.0, 0.55, 4.7), Vector3(-10.1, 0.55, 5.8), Vector3(4.2, 0.55, -3.2), Vector3(4.9, 0.55, -3.9)]:
		_box(_props, pos, Vector3(1.08, 1.08, 1.08), Color(0.19, 0.24, 0.34), true)
		_box(_props, pos + Vector3(0, 0.58, 0), Vector3(1.12, 0.06, 0.14), Color(0.32, 0.4, 0.55))

	for x in [-8.6, 8.6]:
		_box(_props, Vector3(x, 0.1, 1.2), Vector3(1.45, 0.2, 1.45), Color(0.09, 0.12, 0.18), true)
		_box(_props, Vector3(x, 1.65, 1.2), Vector3(1.0, 3.1, 1.0), Color(0.13, 0.17, 0.26), true)
		var strip := _box(_props, Vector3(x, 2.2, 1.71), Vector3(0.12, 1.5, 0.03), Color(0.3, 0.8, 1.0))
		strip.material_override = _emissive(Color(0.25, 0.85, 1.0), 1.2)

	_plant(Vector3(-11.8, 0, 7.5))
	_plant(Vector3(11.8, 0, 7.0))

	for pos in [Vector3(-6.2, 4.15, -1.8), Vector3(5.8, 4.15, -1.8), Vector3(0, 4.15, 5.5)]:
		_lamp(pos)

	var desk_light := OmniLight3D.new()
	desk_light.light_color = Color(0.4, 0.85, 1.0)
	desk_light.light_energy = 0.9
	desk_light.omni_range = 4.0
	desk_light.position = Vector3(5.2, 2.3, -6.4)
	_props.add_child(desk_light)

func _plant(pos: Vector3) -> void:
	_cylinder(_props, pos + Vector3(0, 0.28, 0), 0.42, 0.34, 0.56, Color(0.33, 0.21, 0.14), 12)
	_sphere(_props, pos + Vector3(0, 0.85, 0), 0.48, 0.85, Color(0.13, 0.38, 0.24), 10, 6)
	_sphere(_props, pos + Vector3(0.28, 1.18, 0.08), 0.32, 0.58, Color(0.17, 0.46, 0.28), 9, 5)
	_sphere(_props, pos + Vector3(-0.26, 1.1, -0.1), 0.28, 0.5, Color(0.1, 0.3, 0.2), 9, 5)

func _lamp(pos: Vector3) -> void:
	_box(_props, pos, Vector3(2.0, 0.1, 0.24), Color(0.08, 0.1, 0.15))
	var bar := _box(_props, pos + Vector3(0, -0.06, 0), Vector3(1.7, 0.025, 0.13), Color(0.6, 0.85, 0.95))
	bar.material_override = _emissive(Color(0.55, 0.9, 1.0), 2.0)
	var light := OmniLight3D.new()
	light.light_color = Color(0.55, 0.8, 1.0)
	light.light_energy = 1.25
	light.omni_range = 7.5
	light.position = pos + Vector3(0, -0.3, 0)
	_props.add_child(light)

func _build_players() -> void:
	var root := Node3D.new()
	root.name = "Players"
	add_child(root)
	_spawn_player(root, 0, 1, Vector3(-1.6, 0, 3.0), Color(0.545, 0.361, 0.965))
	_spawn_player(root, 1, 2, Vector3(1.2, 0, 3.9), Color(0.133, 0.827, 0.933))

func _spawn_player(root: Node3D, index: int, id: int, pos: Vector3, color: Color) -> void:
	var player := Player3D.new()
	player.name = "P%d" % id
	player.player_index = index
	player.game_id = id
	player.game = self
	player.color = color
	player.position = pos
	root.add_child(player)
	players[id] = player

func _build_crate() -> void:
	crate = Crate3D.new()
	crate.name = "Crate"
	crate.game = self
	crate.position = Vector3(-4.4, 0.58, 5.2)
	crate.scale = Vector3(1.1, 1.1, 1.1)
	add_child(crate)

func _build_gems() -> void:
	var root := Node3D.new()
	root.name = "Gems"
	add_child(root)
	for pos in [Vector3(-9.4, 0.9, -4.8), Vector3(0.0, 0.9, 6.2), Vector3(10.2, 0.9, -3.6)]:
		var gem := Gem3D.new()
		gem.position = pos
		gem.scale = Vector3(1.45, 1.45, 1.45)
		root.add_child(gem)
		gems.append(gem)

func _build_cameras() -> void:
	var root := Node3D.new()
	root.name = "Cameras"
	add_child(root)
	_add_camera(root, Vector3(-12.0, 3.4, -8.3), Vector3(0, 0, 3.0))
	_add_camera(root, Vector3(12.0, 3.4, -8.3), Vector3(0, 0, 3.0))

func _add_camera(root: Node3D, pos: Vector3, target: Vector3) -> void:
	var camera := SecurityCamera3D.new()
	camera.position = pos
	var direction := target - pos
	direction.y = 0.0
	camera.rotation.y = atan2(-direction.x, -direction.z)
	camera.game = self
	root.add_child(camera)
	cameras.append(camera)

func _build_hud() -> void:
	var hud := CanvasLayer.new()
	hud.name = "HUD"
	add_child(hud)

	var vignette := ColorRect.new()
	vignette.name = "DangerVignette"
	vignette.color = Color.WHITE
	vignette.mouse_filter = Control.MOUSE_FILTER_IGNORE
	danger_material = ShaderMaterial.new()
	danger_material.shader = load("res://assets/shaders/vignette.gdshader")
	danger_material.set_shader_parameter("intensity", 0.0)
	danger_material.set_shader_parameter("danger_color", Color(0.9, 0.08, 0.06, 1.0))
	vignette.material = danger_material
	hud.add_child(vignette)
	vignette.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)

	var status_panel := Panel.new()
	status_panel.position = Vector2(24, 20)
	status_panel.size = Vector2(400, 60)
	var panel_style := StyleBoxFlat.new()
	panel_style.bg_color = Color(0.025, 0.038, 0.07, 0.78)
	panel_style.border_color = Color(0.2, 0.34, 0.55, 0.65)
	panel_style.set_border_width_all(1)
	panel_style.set_corner_radius_all(10)
	status_panel.add_theme_stylebox_override("panel", panel_style)
	hud.add_child(status_panel)
	var accent := ColorRect.new()
	accent.position = Vector2(0, 10)
	accent.size = Vector2(3, 40)
	accent.color = Color(0.55, 0.45, 1.0)
	status_panel.add_child(accent)

	status_label = _hud_label(status_panel, Vector2(16, 0), Vector2(370, 60), "", 19, Color(0.9, 0.9, 1.0))
	status_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER

	var goal := _hud_label(hud, Vector2(28, 88), Vector2(620, 22), "JUNTÁ 3 GEMAS Y LLEVÁ LA CAJA A LA EXTRACCIÓN", 13, Color(0.56, 0.62, 0.75))

	demo_badge = _hud_label(hud, Vector2(440, 22), Vector2(400, 24), "DEMO 3D  ·  CO-OP LOCAL", 14, Color(0.48, 0.55, 0.7))
	demo_badge.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER

	seen_label = _hud_label(hud, Vector2(28, 112), Vector2(420, 20), "CÁMARA DETECTANDO", 14, Color(1.0, 0.32, 0.26))
	seen_label.visible = false

	timer_label = _hud_label(hud, Vector2(900, 12), Vector2(356, 48), "", 40, Color(0.94, 0.95, 1.0))
	timer_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	timer_label.add_theme_constant_override("outline_size", 5)

	var alarm_label := _hud_label(hud, Vector2(900, 60), Vector2(356, 20), "ALARMA  0%", 13, Color(0.8, 0.42, 0.45))
	alarm_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	alarm_label_ref = alarm_label

	var bar_frame := Panel.new()
	bar_frame.position = Vector2(896, 80)
	bar_frame.size = Vector2(364, 22)
	var frame_style := StyleBoxFlat.new()
	frame_style.bg_color = Color(0.03, 0.04, 0.07, 0.6)
	frame_style.border_color = Color(0.36, 0.2, 0.24, 0.8)
	frame_style.set_border_width_all(1)
	frame_style.set_corner_radius_all(4)
	bar_frame.add_theme_stylebox_override("panel", frame_style)
	hud.add_child(bar_frame)

	var bar_back := ColorRect.new()
	bar_back.position = Vector2(900, 84)
	bar_back.size = Vector2(356, 14)
	bar_back.color = Color(0.07, 0.08, 0.12, 0.85)
	hud.add_child(bar_back)

	alarm_fill = ColorRect.new()
	alarm_fill.position = Vector2(900, 84)
	alarm_fill.size = Vector2(0, 14)
	alarm_fill.color = Color(0.95, 0.22, 0.2)
	hud.add_child(alarm_fill)

	hint_label = _hud_label(
		hud,
		Vector2(24, 682),
		Vector2(940, 26),
		"P1: WASD + E   ·   P2: Flechas + Enter   ·   Evitá las cámaras   ·   M: silencio   ·   Esc: menú",
		14,
		Color(0.48, 0.53, 0.64)
	)

	overlay = ColorRect.new()
	overlay.color = Color(0.015, 0.022, 0.045, 0.82)
	overlay.mouse_filter = Control.MOUSE_FILTER_IGNORE
	overlay.visible = false
	hud.add_child(overlay)
	overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)

	result_label = _hud_label(overlay, Vector2(0, 272), Vector2(1280, 100), "", 56, Color(0.72, 0.62, 1.0))
	result_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	result_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	result_label.add_theme_constant_override("outline_size", 10)

	sub_label = _hud_label(overlay, Vector2(0, 382), Vector2(1280, 36), "R para reintentar   ·   Esc para el menú", 20, Color(0.7, 0.74, 0.84))
	sub_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER

func _hud_label(parent: Node, pos: Vector2, size: Vector2, text: String, font_size: int, color: Color) -> Label:
	var label := Label.new()
	label.position = pos
	label.size = size
	label.text = text
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	label.add_theme_color_override("font_outline_color", Color(0.01, 0.02, 0.04, 0.95))
	label.add_theme_constant_override("outline_size", 3)
	parent.add_child(label)
	return label

func _process(delta: float) -> void:
	_time += delta
	if pad_ring != null:
		pad_ring.rotation.y += delta * 0.7
	if state != State.PLAYING:
		return

	time_left = maxf(time_left - delta, 0.0)

	var seen := 0
	for camera in cameras:
		if camera.triggered:
			seen += 1
	if seen_label != null:
		seen_label.visible = seen > 0
		if seen > 0:
			seen_label.modulate.a = 0.72 + sin(_time * 8.0) * 0.28
	if seen > 0:
		alarm = minf(ALARM_MAX, alarm + ALARM_RATE * float(seen) * delta)
	else:
		alarm = maxf(0.0, alarm - ALARM_DECAY * delta)

	_check_gems()

	if not crate.delivered and crate.holder_ids.is_empty() and _crate_on_pad():
		_deliver_crate()

	if crate.delivered and gems_collected >= TOTAL_GEMS:
		_end(State.WON, "¡ROBO COMPLETO!")
	elif alarm >= ALARM_MAX:
		_end(State.LOST, "¡ALARMA MÁXIMA!")
	elif time_left <= 0.0:
		_end(State.LOST, "¡SE ACABÓ EL TIEMPO!")

	_update_hud()

func _check_gems() -> void:
	for gem in gems:
		if gem.collected:
			continue
		for player in players.values():
			if is_instance_valid(player) and player.global_position.distance_to(gem.global_position) < 1.15:
				var burst_pos: Vector3 = gem.global_position
				gem.collect()
				gems_collected += 1
				_burst3d(burst_pos, Color(0.3, 1.0, 0.55), 24, 1.1)
				Audio.play_sfx("gem", -8.0)
				_pulse_status()
				return

func _deliver_crate() -> void:
	crate.deliver(PAD_POS)
	_burst3d(PAD_POS + Vector3(0, 0.8, 0), Color(0.35, 1.0, 0.6), 34, 1.3)
	var tween := create_tween()
	tween.tween_property(pad, "scale", Vector3(1.08, 1.0, 1.08), 0.12)
	tween.tween_property(pad, "scale", Vector3.ONE, 0.35)
	_pulse_status()

func _crate_on_pad() -> bool:
	var offset := crate.global_position - PAD_POS
	return Vector2(offset.x, offset.z).length() <= 1.9

func carry_multiplier_for(id: int) -> float:
	if crate == null or crate.delivered or not crate.holder_ids.has(id):
		return 1.0
	return 0.82 if crate.holder_ids.size() >= 2 else 0.6

func toggle_grab(player: Player3D) -> void:
	if state != State.PLAYING or crate == null or crate.delivered:
		return
	if crate.holder_ids.has(player.game_id):
		crate.remove_holder(player.game_id)
		Audio.play_sfx("drop", -9.0)
		return
	var offset := player.global_position - crate.global_position
	offset.y = 0.0
	if offset.length() > Player3D.GRAB_RANGE:
		return
	# No permitir agarrar la caja a través de una pared o un rack.
	var query := PhysicsRayQueryParameters3D.create(
		player.global_position + Vector3(0, 1.0, 0),
		crate.global_position + Vector3(0, 0.2, 0)
	)
	query.collision_mask = 1
	query.exclude = [player.get_rid()]
	if not get_world_3d().direct_space_state.intersect_ray(query).is_empty():
		return
	crate.add_holder(player.game_id)
	Audio.play_sfx("grab", -9.0)
	_pulse_status()

func _update_hud() -> void:
	if status_label == null:
		return
	var crate_state := "PENDIENTE"
	if crate.delivered:
		crate_state = "ENTREGADA"
	elif crate.holder_ids.size() > 0:
		crate_state = "EN MANOS"
	status_label.text = "GEMAS  %d/%d      ·      CAJA  %s" % [gems_collected, TOTAL_GEMS, crate_state]

	var seconds := int(ceil(time_left))
	timer_label.text = "%d:%02d" % [int(seconds / 60), seconds % 60]
	timer_label.add_theme_color_override(
		"font_color",
		Color(1.0, 0.36, 0.32) if time_left <= 20.0 and state == State.PLAYING else Color(0.94, 0.95, 1.0)
	)

	var ratio := clampf(alarm / ALARM_MAX, 0.0, 1.0)
	alarm_fill.size.x = 356.0 * ratio
	alarm_fill.color = Color(1.0, 0.35, 0.28).lerp(Color(1.0, 0.1, 0.08), ratio)
	if alarm_label_ref != null:
		alarm_label_ref.text = "ALARMA  %d%%" % int(round(alarm))
		alarm_label_ref.add_theme_color_override(
			"font_color",
			Color(1.0, 0.45, 0.4) if ratio < 0.5 else Color(1.0, 0.25, 0.2)
		)
	var danger := 0.0
	if state == State.PLAYING:
		danger = clampf((alarm - 25.0) / 75.0, 0.0, 1.0) * 0.55
	danger_material.set_shader_parameter("intensity", danger)
	alarm_light.light_energy = (alarm / ALARM_MAX) * 0.7
	camera3d.fov = lerpf(camera_base_fov, camera_base_fov - 3.0, ratio if state == State.PLAYING else 0.0)

	if state == State.PLAYING:
		Audio.set_alarm(alarm, true)
		if seconds <= 10 and seconds > 0 and seconds != _last_tick:
			_last_tick = seconds
			Audio.play_sfx("tick", -8.0)
	else:
		Audio.set_alarm(0.0, false)

func _pulse_status() -> void:
	if status_label == null:
		return
	status_label.modulate = Color(1.7, 1.7, 1.7)
	create_tween().tween_property(status_label, "modulate", Color.WHITE, 0.28)

func _end(result: int, message: String) -> void:
	if state != State.PLAYING:
		return
	state = result
	result_label.text = message
	result_label.add_theme_color_override(
		"font_color",
		Color(0.45, 1.0, 0.65) if result == State.WON else Color(1.0, 0.35, 0.3)
	)
	sub_label.text = "R para reintentar   ·   Esc para el menú"
	overlay.visible = true
	if seen_label != null:
		seen_label.visible = false
	for player in players.values():
		if is_instance_valid(player):
			player.set_physics_process(false)
	if crate != null:
		crate.set_process(false)
	for gem in gems:
		gem.set_process(false)

	Audio.set_alarm(0.0, false)
	Audio.stop_music()
	Audio.play_sfx("win" if result == State.WON else "lose", -6.0)
	var effect_player: Node3D = null
	if players.has(1):
		effect_player = players[1]
	elif not players.is_empty():
		effect_player = players.values()[0]
	var effect_pos: Vector3 = PAD_POS + Vector3(0, 0.8, 0)
	if result != State.WON and effect_player != null:
		effect_pos = effect_player.global_position + Vector3(0, 1.0, 0)
	_burst3d(effect_pos, Color(0.4, 1.0, 0.6) if result == State.WON else Color(1.0, 0.25, 0.18), 36, 1.4)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	_update_hud()

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		Audio.set_alarm(0.0, false)
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		get_tree().change_scene_to_file(MENU_SCENE)
		return
	if state != State.PLAYING and event.is_action_pressed("restart"):
		get_viewport().set_input_as_handled()
		get_tree().reload_current_scene()

func _burst3d(pos: Vector3, tint: Color, amount: int, speed: float) -> void:
	var particles := CPUParticles3D.new()
	particles.one_shot = true
	particles.amount = amount
	particles.lifetime = 0.62
	particles.explosiveness = 0.95
	particles.direction = Vector3.UP
	particles.spread = 180.0
	particles.initial_velocity_min = 2.0 * speed
	particles.initial_velocity_max = 5.0 * speed
	particles.gravity = Vector3(0, -9.0, 0)
	particles.scale_amount_min = 0.12
	particles.scale_amount_max = 0.32
	particles.local_coords = false

	var mesh := SphereMesh.new()
	mesh.radius = 0.09
	mesh.height = 0.18
	mesh.radial_segments = 8
	mesh.rings = 4
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.albedo_color = tint
	mat.emission_enabled = true
	mat.emission = tint
	mat.emission_energy_multiplier = 2.0
	mesh.material = mat
	particles.mesh = mesh

	particles.position = pos
	add_child(particles)
	particles.finished.connect(particles.queue_free)
	particles.emitting = true

func _mat(color: Color) -> StandardMaterial3D:
	var key := color.to_html()
	if _mat_cache.has(key):
		return _mat_cache[key]
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color
	mat.roughness = 0.78
	_mat_cache[key] = mat
	return mat

func _emissive(color: Color, energy: float) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color
	mat.roughness = 0.4
	mat.emission_enabled = true
	mat.emission = color
	mat.emission_energy_multiplier = energy
	return mat

func _box(parent: Node3D, pos: Vector3, size: Vector3, color: Color, collide := false) -> MeshInstance3D:
	var mesh_instance := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = size
	mesh_instance.mesh = mesh
	mesh_instance.position = pos
	mesh_instance.material_override = _mat(color)
	parent.add_child(mesh_instance)
	if collide:
		_collision(parent, pos, size)
	return mesh_instance

func _cylinder(parent: Node3D, pos: Vector3, top: float, bottom: float, height: float, color: Color, segments := 16) -> MeshInstance3D:
	var mesh_instance := MeshInstance3D.new()
	var mesh := CylinderMesh.new()
	mesh.top_radius = top
	mesh.bottom_radius = bottom
	mesh.height = height
	mesh.radial_segments = segments
	mesh.rings = 1
	mesh_instance.mesh = mesh
	mesh_instance.position = pos
	mesh_instance.material_override = _mat(color)
	parent.add_child(mesh_instance)
	return mesh_instance

func _sphere(parent: Node3D, pos: Vector3, radius: float, height: float, color: Color, segments := 12, rings := 6) -> MeshInstance3D:
	var mesh_instance := MeshInstance3D.new()
	var mesh := SphereMesh.new()
	mesh.radius = radius
	mesh.height = height
	mesh.radial_segments = segments
	mesh.rings = rings
	mesh_instance.mesh = mesh
	mesh_instance.position = pos
	mesh_instance.material_override = _mat(color)
	parent.add_child(mesh_instance)
	return mesh_instance

func _collision(parent: Node3D, pos: Vector3, size: Vector3) -> void:
	var body := StaticBody3D.new()
	body.position = pos
	var shape_node := CollisionShape3D.new()
	var shape := BoxShape3D.new()
	shape.size = size
	shape_node.shape = shape
	body.add_child(shape_node)
	parent.add_child(body)

func _label3d(
	parent: Node3D,
	pos: Vector3,
	text: String,
	size: int,
	color: Color,
	pixel_size: float,
	billboard := true
) -> Label3D:
	var label := Label3D.new()
	label.text = text
	label.font_size = size
	label.pixel_size = pixel_size
	label.modulate = color
	label.outline_size = 10
	label.outline_modulate = Color(0.01, 0.02, 0.04, 1.0)
	label.position = pos
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED if billboard else BaseMaterial3D.BILLBOARD_DISABLED
	parent.add_child(label)
	return label
