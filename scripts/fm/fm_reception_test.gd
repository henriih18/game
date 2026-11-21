extends Node3D

## Escena de validación R4 de la recepción.
## Carga el GLB exportado, construye colisiones estáticas y valida
## movimiento, linterna, acceso a extracción y rendimiento con FMPlayer.

const GLB_PATH := "res://assets/models/fm/reception_r5.glb"
const PLAYER_SCENE := preload("res://scenes/fm/fm_player.tscn")
const HUD_SCRIPT := preload("res://scripts/fm/fm_hud.gd")
const COLLISION_HELPER := preload("res://scripts/fm/fm_glb_collision.gd")

const SPAWN := Vector3(-90.0, 0.10, 10.0)
const BOUNDS := AABB(Vector3(-110.5, -1.0, 7.5), Vector3(40.5, 7.0, 33.0))

var state := 0
var player: FMPlayer
var hud
var glb_root: Node3D
var _collider_count := 0
var _autotest := false
var _headless := false
var _fps_samples: Array[float] = []
var _status_timer := 0.0


func _ready() -> void:
	_autotest = "--autotest" in OS.get_cmdline_user_args()
	_headless = DisplayServer.get_name() == "headless"
	if not _headless:
		DisplayServer.window_set_size(Vector2i(1280, 720))
	if _autotest and not _headless:
		DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
		Engine.max_fps = 0

	_setup_environment()
	if not _load_reception():
		return
	await get_tree().process_frame
	await get_tree().process_frame
	_setup_collisions()
	_setup_reception_lights()
	_setup_player()
	_setup_hud()

	if _autotest:
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		await _run_autotest()
	else:
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
		print("RECEPTION_MANUAL_READY")


func _process(delta: float) -> void:
	if hud == null or player == null or not is_instance_valid(player):
		return
	hud.set_battery(player.battery, player.flashlight_on)
	hud.set_stamina(player.stamina)
	hud.set_prompt(player.get_interaction_prompt())
	_status_timer -= delta
	if _status_timer <= 0.0:
		_status_timer = 0.4
		var pos := player.global_position
		hud.set_status("FPS %d   POS %.1f / %.1f / %.1f" % [
			Engine.get_frames_per_second(), pos.x, pos.y, pos.z,
		])


func _input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and Input.mouse_mode != Input.MOUSE_MODE_CAPTURED:
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE


func _load_reception() -> bool:
	var start := Time.get_ticks_msec()
	var document := GLTFDocument.new()
	var gltf_state := GLTFState.new()
	var err: Error = document.append_from_file(GLB_PATH, gltf_state)
	if err != OK:
		push_error("No se pudo cargar la recepción R4: %s" % err)
		return false
	glb_root = document.generate_scene(gltf_state)
	if glb_root == null:
		push_error("La recepción R4 no generó escena")
		return false
	glb_root.name = "ReceptionR4"
	add_child(glb_root)
	_tame_imported_lights()
	var mesh_count := glb_root.find_children("*", "MeshInstance3D", true, false).size()
	print("RECEPTION_GLB meshes=%d load_ms=%d" % [mesh_count, Time.get_ticks_msec() - start])
	return true


func _tame_imported_lights() -> void:
	var disabled := 0
	var kept := 0
	for node in glb_root.find_children("*", "Light3D", true, false):
		var light := node as Light3D
		if light == null:
			continue
		if light.light_energy > 5.0:
			light.visible = false
			disabled += 1
		else:
			light.shadow_enabled = false
			kept += 1
	print("RECEPTION_IMPORTED_LIGHTS kept=%d disabled=%d" % [kept, disabled])


func _setup_environment() -> void:
	var world := WorldEnvironment.new()
	world.name = "ReceptionWorld"
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.008, 0.009, 0.012)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.22, 0.23, 0.25)
	env.ambient_light_energy = 0.10
	env.tonemap_mode = Environment.TONE_MAPPER_AGX
	env.tonemap_exposure = 1.15
	env.ssao_enabled = true
	env.ssao_radius = 1.0
	env.ssao_intensity = 1.4
	env.ssao_power = 1.3
	env.ssr_enabled = true
	env.ssr_max_steps = 24
	env.glow_enabled = true
	env.glow_intensity = 0.35
	env.glow_hdr_threshold = 1.0
	env.fog_enabled = true
	env.fog_light_color = Color(0.08, 0.085, 0.10)
	env.fog_light_energy = 0.22
	env.fog_density = 0.004
	env.volumetric_fog_enabled = true
	env.volumetric_fog_density = 0.008
	env.volumetric_fog_albedo = Color(0.42, 0.46, 0.52)
	env.volumetric_fog_anisotropy = 0.25
	env.volumetric_fog_length = 30.0
	env.volumetric_fog_ambient_inject = 0.05
	env.adjustment_enabled = true
	env.adjustment_contrast = 1.06
	env.adjustment_saturation = 1.0
	env.adjustment_brightness = 1.02
	world.environment = env
	add_child(world)


func _setup_collisions() -> void:
	var result: Dictionary = COLLISION_HELPER.build(self, glb_root, BOUNDS)
	var body: StaticBody3D = result["body"]
	_collider_count = int(result["count"])
	# Safety floor for the whole reception volume.
	var shape := BoxShape3D.new()
	shape.size = Vector3(40.0, 1.0, 32.0)
	var collider := CollisionShape3D.new()
	collider.shape = shape
	collider.position = Vector3(-90.0, -0.5, 24.0)
	body.add_child(collider)
	print("RECEPTION_COLLIDERS %d trimesh=%d" % [_collider_count, int(result["trimesh"])])


func _setup_reception_lights() -> void:
	# glTF no exporta AREA lights: aproximación con omnis para la validación.
	_add_omni("ReceptionA_Approx", Vector3(-88.0, 4.8, 24.0), Color(1.0, 0.82, 0.62), 8.0, 28.0, true)
	_add_omni("ReceptionB_Approx", Vector3(-99.0, 3.6, 12.0), Color(1.0, 0.80, 0.60), 4.5, 22.0, false)
	_add_omni("ReceptionHallFill", Vector3(-90.0, 4.2, 22.0), Color(1.0, 0.80, 0.62), 3.0, 26.0, false)
	_add_omni("ReceptionFill_0", Vector3(-100.0, 3.0, 12.0), Color(1.0, 0.78, 0.58), 1.2, 14.0, false)
	_add_omni("ReceptionFill_1", Vector3(-80.0, 3.0, 12.0), Color(1.0, 0.78, 0.58), 1.2, 14.0, false)
	_add_omni("ReceptionFill_2", Vector3(-100.0, 3.0, 34.0), Color(1.0, 0.78, 0.58), 1.2, 14.0, false)
	_add_omni("ReceptionFill_3", Vector3(-80.0, 3.0, 34.0), Color(1.0, 0.78, 0.58), 1.2, 14.0, false)
	_add_omni("ReceptionSpawnFill", Vector3(-90.0, 3.2, 10.0), Color(0.60, 0.68, 0.80), 1.1, 12.0, false)
	_add_omni("ReceptionExtractionFill", Vector3(-94.0, 3.6, 37.0), Color(1.0, 0.60, 0.36), 1.6, 12.0, false)


func _add_omni(light_name: String, pos: Vector3, color: Color, energy: float, light_range: float, shadows: bool) -> void:
	var light := OmniLight3D.new()
	light.name = light_name
	light.position = pos
	light.light_color = color
	light.light_energy = energy
	light.omni_range = light_range
	light.shadow_enabled = shadows
	light.light_volumetric_fog_energy = 0.8
	add_child(light)


func _setup_player() -> void:
	player = PLAYER_SCENE.instantiate() as FMPlayer
	player.name = "Player"
	player.position = SPAWN
	player.rotation.y = PI
	add_child(player)
	player.add_to_group("fm_player")
	player.set_game(self)
	player.network_client = false
	player.set_flashlight_model(true)
	_tune_player_flashlight()
	print("RECEPTION_PLAYER pos=%s" % player.global_position)


func _tune_player_flashlight() -> void:
	if player == null or player.flashlight == null:
		return
	player.flashlight.light_color = Color(1.0, 0.90, 0.72)
	player.flashlight.light_energy = 12.0
	player.flashlight.spot_range = 24.0
	player.flashlight.spot_angle = 32.0
	player.flashlight.spot_angle_attenuation = 0.90
	player.flashlight.shadow_enabled = true
	var gradient := Gradient.new()
	gradient.set_color(0, Color(1.0, 1.0, 1.0, 1.0))
	gradient.set_color(1, Color(0.05, 0.05, 0.05, 1.0))
	var projector := GradientTexture2D.new()
	projector.gradient = gradient
	projector.width = 128
	projector.height = 128
	projector.fill = GradientTexture2D.FILL_RADIAL
	projector.fill_from = Vector2(0.5, 0.5)
	projector.fill_to = Vector2(1.0, 0.5)
	player.flashlight.light_projector = projector
	var spill := SpotLight3D.new()
	spill.name = "FlashlightSpill"
	spill.light_color = Color(1.0, 0.86, 0.66)
	spill.light_energy = 2.2
	spill.spot_range = 11.0
	spill.spot_angle = 58.0
	spill.spot_angle_attenuation = 1.7
	spill.shadow_enabled = false
	player.camera.add_child(spill)


func _setup_hud() -> void:
	hud = HUD_SCRIPT.new()
	hud.name = "HUD"
	add_child(hud)
	hud.set_objective("RECEPCIÓN · VALIDACIÓN R4", "Nivel 1 · acceso y extracción")
	hud.set_status("WASD MOVER · E INTERACTUAR · F LINTERNA · ESC LIBERAR RATÓN")
	hud.set_battery(player.battery, player.flashlight_on)
	hud.set_stamina(player.stamina)
	hud.set_stress(0.0)


func _run_autotest() -> void:
	await get_tree().create_timer(0.8).timeout
	var mesh_count := glb_root.find_children("*", "MeshInstance3D", true, false).size()
	var nodes := glb_root.find_children("*", "", true, false).size() + 1
	print("RECEPTION_TEST meshes=%d nodes=%d colliders=%d objects=%d" % [
		mesh_count, nodes, _collider_count, get_tree().get_node_count(),
	])
	if player == null or not is_instance_valid(player):
		_fail("jugador no instanciado")
		return
	if mesh_count < 200:
		_fail("mallas de recepción insuficientes")
		return
	if _collider_count < 50:
		_fail("colisiones insuficientes")
		return

	player.rotation.y = 1.816
	await get_tree().create_timer(0.5).timeout
	await _capture("fm_reception_r4_01_spawn.png")
	player.rotation.y = PI

	var start := player.global_position
	Input.action_press("move_up")
	await get_tree().create_timer(2.0).timeout
	Input.action_release("move_up")
	await get_tree().physics_frame
	await get_tree().physics_frame
	var moved := start.distance_to(player.global_position)
	print("RECEPTION_TEST move from=%s to=%s dist=%.2f floor=%s" % [
		start, player.global_position, moved, player.is_on_floor(),
	])
	if moved < 1.0:
		_fail("el jugador no avanzó en recepción")
		return
	if not player.is_on_floor():
		_fail("el jugador no está sobre el suelo de recepción")
		return
	await _capture("fm_reception_r4_02_room.png")

	var flash_before := player.flashlight_on
	await _send_action("flashlight")
	await get_tree().create_timer(0.25).timeout
	if player.flashlight_on == flash_before:
		var direct := InputEventAction.new()
		direct.action = "flashlight"
		direct.pressed = true
		player._unhandled_input(direct)
		await get_tree().process_frame
	print("RECEPTION_TEST flashlight before=%s after=%s" % [flash_before, player.flashlight_on])
	if player.flashlight_on == flash_before:
		_fail("la linterna no respondió")
		return
	if not player.flashlight_on:
		await _send_action("flashlight")
		await get_tree().create_timer(0.25).timeout

	player.global_position = Vector3(-94.0, 0.15, 31.0)
	player.rotation.y = PI
	await get_tree().physics_frame
	await get_tree().physics_frame
	await get_tree().create_timer(0.35).timeout
	await _capture("fm_reception_r4_03_extraction.png")
	Input.action_press("move_up")
	await get_tree().create_timer(2.5).timeout
	Input.action_release("move_up")
	await get_tree().physics_frame
	await get_tree().physics_frame
	print("RECEPTION_TEST extraction z=%.2f floor=%s" % [
		player.global_position.z, player.is_on_floor(),
	])
	if player.global_position.z < 37.2:
		_fail("no se pudo acceder a la zona de extracción")
		return
	if not player.is_on_floor():
		_fail("el jugador cayó en la extracción")
		return
	await _capture("fm_reception_r4_04_extraction_deck.png")

	_fps_samples.clear()
	var elapsed := 0.0
	while elapsed < 3.0:
		await get_tree().process_frame
		var fps := Engine.get_frames_per_second()
		if fps > 0.0:
			_fps_samples.append(fps)
		elapsed += get_process_delta_time()
	var fps_avg := 0.0
	var fps_min := 9999.0
	var fps_max := 0.0
	for sample in _fps_samples:
		fps_avg += sample
		fps_min = minf(fps_min, sample)
		fps_max = maxf(fps_max, sample)
	if not _fps_samples.is_empty():
		fps_avg /= float(_fps_samples.size())
	print("RECEPTION_TEST fps avg=%.1f min=%.1f max=%.1f samples=%d" % [
		fps_avg, fps_min, fps_max, _fps_samples.size(),
	])
	print("RECEPTION_TEST render draw_calls=%d primitives=%d objects=%d" % [
		int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)),
		int(Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)),
		int(Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME)),
	])
	print("RECEPTION_TEST final_pos=%s battery=%.1f stamina=%.1f" % [
		player.global_position, player.battery, player.stamina,
	])
	Input.action_release("move_up")
	print("RECEPTION_AUTOTEST_OK")
	get_tree().quit(0)


func _send_action(action: String) -> void:
	var down := InputEventAction.new()
	down.action = action
	down.pressed = true
	Input.parse_input_event(down)
	await get_tree().process_frame
	var up := InputEventAction.new()
	up.action = action
	up.pressed = false
	Input.parse_input_event(up)
	await get_tree().process_frame


func _capture(file_name: String) -> void:
	if _headless:
		return
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	var path := ProjectSettings.globalize_path("res://docs").path_join(file_name)
	var err := image.save_png(path)
	print("RECEPTION_CAPTURE %s err=%d size=%s" % [path, err, image.get_size()])


func _fail(reason: String) -> void:
	Input.action_release("move_up")
	printerr("RECEPTION_AUTOTEST_FAIL ", reason)
	get_tree().quit(1)
