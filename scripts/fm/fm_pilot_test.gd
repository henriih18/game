extends Node3D

## Escena de validación del piloto arquitectónico Conector Z10.
## Carga el GLB exportado, construye colisiones de prueba, instancia FMPlayer
## y comprueba movimiento, cámara, linterna, interacción y puertas.
##
## Uso manual:
##   godot --path . scenes/fm/fm_pilot_test.tscn
##
## Uso automatizado (sin narrativa ni multijugador):
##   godot --path . scenes/fm/fm_pilot_test.tscn -- --autotest

const GLB_PATH := "res://assets/models/fm/z10_conector.glb"
const PLAYER_BASE_PATH := "res://assets/models/fm/player_base_z10.glb"
const PLAYER_SCENE := preload("res://scenes/fm/fm_player.tscn")
const HUD_SCRIPT := preload("res://scripts/fm/fm_hud.gd")
const PANEL_SCRIPT := preload("res://scripts/fm/fm_pilot_test_panel.gd")
const COLLISION_HELPER := preload("res://scripts/fm/fm_glb_collision.gd")

const SPAWN := Vector3(50.0, 0.15, -10.0)
const ROOM_BOUNDS := AABB(Vector3(39.0, -1.0, -41.0), Vector3(24.0, 6.0, 38.0))

var state := 0
var player: FMPlayer
var hud
var glb_root: Node3D
var panel
var player_reference: Node3D
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
	if not _load_conector():
		return
	await get_tree().process_frame
	await get_tree().process_frame
	_setup_collisions()
	_setup_emergency_lights()
	_setup_panel()
	_setup_player_reference()
	_setup_player()
	_setup_hud()
	_setup_postprocess()

	if _autotest:
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		await _run_autotest()
	else:
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
		print("PILOT_MANUAL_READY")


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
	if event is InputEventMouseButton and event.pressed:
		if Input.mouse_mode != Input.MOUSE_MODE_CAPTURED:
			Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE


# ---------------------------------------------------------------------------
# Carga y entorno
# ---------------------------------------------------------------------------

func _load_conector() -> bool:
	var start := Time.get_ticks_msec()
	var document := GLTFDocument.new()
	var gltf_state := GLTFState.new()
	var err: Error = document.append_from_file(GLB_PATH, gltf_state)
	if err != OK:
		push_error("No se pudo cargar el Conector Z10: %s" % err)
		return false
	glb_root = document.generate_scene(gltf_state)
	if glb_root == null:
		push_error("El Conector Z10 no generó escena")
		return false
	glb_root.name = "ConectorZ10"
	add_child(glb_root)
	var mesh_count := glb_root.find_children("*", "MeshInstance3D", true, false).size()
	print("PILOT_GLB meshes=%d nodes=%d load_ms=%d" % [
		mesh_count, glb_root.find_children("*", "", true, false).size() + 1,
		Time.get_ticks_msec() - start,
	])
	return true


func _setup_environment() -> void:
	var world := WorldEnvironment.new()
	world.name = "PilotWorld"
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.006, 0.008, 0.012)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.20, 0.24, 0.30)
	env.ambient_light_energy = 0.075
	env.tonemap_mode = Environment.TONE_MAPPER_AGX
	env.tonemap_exposure = 1.16
	env.ssao_enabled = true
	env.ssao_radius = 1.0
	env.ssao_intensity = 1.6
	env.ssao_power = 1.35
	env.ssr_enabled = true
	env.ssr_max_steps = 32
	env.ssr_fade_in = 0.15
	env.ssr_fade_out = 2.0
	env.ssr_depth_tolerance = 0.25
	env.glow_enabled = true
	env.glow_intensity = 0.5
	env.glow_bloom = 0.08
	env.glow_hdr_threshold = 1.0
	env.fog_enabled = true
	env.fog_light_color = Color(0.07, 0.085, 0.11)
	env.fog_light_energy = 0.25
	env.fog_density = 0.006
	env.volumetric_fog_enabled = true
	env.volumetric_fog_density = 0.010
	env.volumetric_fog_albedo = Color(0.42, 0.49, 0.60)
	env.volumetric_fog_emission = Color(0.0, 0.0, 0.0)
	env.volumetric_fog_emission_energy = 0.0
	env.volumetric_fog_anisotropy = 0.28
	env.volumetric_fog_length = 32.0
	env.volumetric_fog_detail_spread = 1.7
	env.volumetric_fog_ambient_inject = 0.04
	env.volumetric_fog_sky_affect = 0.0
	env.adjustment_enabled = true
	env.adjustment_contrast = 1.08
	env.adjustment_saturation = 1.0
	env.adjustment_brightness = 1.02
	world.environment = env
	add_child(world)


func _setup_emergency_lights() -> void:
	# Posiciones reales de las luces rojas del Conector (Blender -> Godot).
	_add_point_light(
		"EmergencyE", Vector3(61.62, 2.45, -16.0),
		Color(1.0, 0.07, 0.035), 2.5, 9.0, true
	)
	_add_point_light(
		"EmergencyN", Vector3(54.0, 2.45, -29.62),
		Color(1.0, 0.07, 0.035), 2.5, 9.0, true
	)
	_add_point_light(
		"EmergencyService", Vector3(51.0, 3.805, -19.0),
		Color(1.0, 0.05, 0.025), 4.0, 9.0, true
	)
	# Relleno mínimo de validación: el piloto está deliberadamente a oscuras.
	_add_point_light(
		"PilotFill", Vector3(50.0, 3.2, -11.5),
		Color(0.45, 0.52, 0.64), 0.65, 11.0, false
	)


func _add_point_light(
	light_name: String, pos: Vector3, color: Color, energy: float,
	light_range: float, shadows: bool
) -> void:
	var light := OmniLight3D.new()
	light.name = light_name
	light.position = pos
	light.light_color = color
	light.light_energy = energy
	light.omni_range = light_range
	light.shadow_enabled = shadows
	light.light_volumetric_fog_energy = 1.1
	add_child(light)


func _setup_panel() -> void:
	panel = PANEL_SCRIPT.new()
	panel.name = "ValidationPanel"
	panel.position = Vector3(50.0, 0.0, -12.2)
	add_child(panel)


func _setup_player_reference() -> void:
	var document := GLTFDocument.new()
	var gltf_state := GLTFState.new()
	if document.append_from_file(PLAYER_BASE_PATH, gltf_state) != OK:
		push_warning("No se pudo cargar la referencia del jugador base")
		return
	player_reference = document.generate_scene(gltf_state)
	if player_reference == null:
		return
	player_reference.name = "PlayerBaseReference"
	player_reference.position = Vector3(52.2, 0.0, -14.0)
	add_child(player_reference)
	var meshes := player_reference.find_children("*", "MeshInstance3D", true, false)
	print("PILOT_PLAYER_REFERENCE meshes=%d" % meshes.size())


# ---------------------------------------------------------------------------
# Colisiones de validación
# ---------------------------------------------------------------------------

func _setup_collisions() -> void:
	var result := COLLISION_HELPER.build(self, glb_root, ROOM_BOUNDS)
	var body := result["body"] as StaticBody3D
	_collider_count = int(result["count"])

	# Suelo y cerramiento de seguridad para que la validación no dependa de
	# huecos del blockout. No sustituyen a las colisiones reales del GLB.
	_add_shape(body, Vector3(51.0, -0.5, -19.0), Vector3(22.0, 1.0, 22.0))
	_add_shape(body, Vector3(43.0, -0.5, -35.0), Vector3(6.0, 1.0, 10.0))
	_add_shape(body, Vector3(43.0, -0.5, -6.0), Vector3(6.0, 1.0, 4.0))
	_add_shape(body, Vector3(63.0, -0.5, -21.0), Vector3(2.0, 1.0, 6.0))

	_add_shape(body, Vector3(39.8, 2.0, -19.0), Vector3(0.4, 4.0, 22.0))
	_add_shape(body, Vector3(62.2, 2.0, -27.0), Vector3(0.4, 4.0, 6.0))
	_add_shape(body, Vector3(62.2, 2.0, -13.0), Vector3(0.4, 4.0, 10.0))
	_add_shape(body, Vector3(55.0, 2.0, -30.2), Vector3(14.0, 4.0, 0.4))
	_add_shape(body, Vector3(43.0, 2.0, -40.2), Vector3(6.0, 4.0, 0.4))
	_add_shape(body, Vector3(39.8, 2.0, -35.0), Vector3(0.4, 4.0, 10.0))
	_add_shape(body, Vector3(46.2, 2.0, -35.0), Vector3(0.4, 4.0, 10.0))
	_add_shape(body, Vector3(43.0, 2.0, -4.2), Vector3(6.0, 4.0, 0.4))
	_add_shape(body, Vector3(54.0, 2.0, -8.2), Vector3(16.0, 4.0, 0.4))
	_add_shape(body, Vector3(63.6, 2.0, -21.0), Vector3(0.4, 4.0, 6.0))
	print("PILOT_COLLIDERS ", _collider_count, " trimesh=", int(result["trimesh"]))


func _add_shape(body: StaticBody3D, center: Vector3, size: Vector3) -> void:
	var shape := BoxShape3D.new()
	shape.size = size
	var collider := CollisionShape3D.new()
	collider.shape = shape
	collider.position = center
	body.add_child(collider)


# ---------------------------------------------------------------------------
# Jugador, HUD y postproceso
# ---------------------------------------------------------------------------

func _setup_player() -> void:
	player = PLAYER_SCENE.instantiate() as FMPlayer
	player.name = "Player"
	player.position = SPAWN
	add_child(player)
	player.add_to_group("fm_player")
	player.set_game(self)
	player.network_client = false
	player.set_flashlight_model(true)
	_tune_player_flashlight()
	print("PILOT_PLAYER height=1.70 radius=0.38 pos=%s" % player.global_position)


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
	hud.set_objective("VALIDACIÓN PILOTO Z10", "Conector de servicio · escala 1,70 m")
	hud.set_status("WASD MOVER · E INTERACTUAR · F LINTERNA · ESC LIBERAR RATÓN")
	hud.set_battery(player.battery, player.flashlight_on)
	hud.set_stamina(player.stamina)
	hud.set_stress(0.0)


func _setup_postprocess() -> void:
	var shader := load("res://assets/shaders/fm_postprocess.gdshader") as Shader
	if shader == null:
		return
	var layer := CanvasLayer.new()
	layer.name = "PilotPostprocess"
	layer.layer = 1
	add_child(layer)
	var rect := ColorRect.new()
	rect.name = "Postprocess"
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(rect)
	rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	var material := ShaderMaterial.new()
	material.shader = shader
	material.set_shader_parameter("vignette_intensity", 0.22)
	material.set_shader_parameter("grain_amount", 0.018)
	material.set_shader_parameter("aberration", 0.00035)
	material.set_shader_parameter("contrast", 1.0)
	material.set_shader_parameter("saturation", 1.04)
	rect.material = material


# ---------------------------------------------------------------------------
# Autotest
# ---------------------------------------------------------------------------

func _run_autotest() -> void:
	await get_tree().create_timer(0.8).timeout
	var mesh_count := glb_root.find_children("*", "MeshInstance3D", true, false).size()
	print("PILOT_TEST_GPU ", RenderingServer.get_video_adapter_name())
	print("PILOT_TEST counts meshes=%d colliders=%d objects=%d" % [
		mesh_count, _collider_count,
		get_tree().get_node_count(),
	])
	if player == null or not is_instance_valid(player):
		_fail("jugador no instanciado")
		return
	if mesh_count < 300:
		_fail("mallas del Conector insuficientes")
		return
	if _collider_count < 100:
		_fail("colisiones insuficientes")
		return
	if panel == null or not is_instance_valid(panel):
		_fail("panel de interacción ausente")
		return

	# Cámara: respuesta a movimiento de ratón.
	if _headless:
		print("PILOT_TEST camera skipped (headless)")
	else:
		var yaw_before := player.rotation.y
		var pitch_before := player.camera.rotation.x
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
		var motion := InputEventMouseMotion.new()
		motion.relative = Vector2(90.0, -45.0)
		player._unhandled_input(motion)
		await get_tree().process_frame
		var camera_ok := (
			not is_equal_approx(player.rotation.y, yaw_before)
			and not is_equal_approx(player.camera.rotation.x, pitch_before)
		)
		print("PILOT_TEST camera yaw=%.3f pitch=%.3f ok=%s" % [
			player.rotation.y, player.camera.rotation.x, camera_ok,
		])
		player.rotation.y = 0.0
		player._pitch = 0.0
		player.camera.rotation.x = 0.0
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		if not camera_ok:
			_fail("la cámara no respondió al ratón")
			return

	await _capture("fm_pilot_01_spawn.png")

	# Movimiento y colisión con el panel.
	var start := player.global_position
	Input.action_press("move_up")
	await get_tree().create_timer(0.7).timeout
	Input.action_release("move_up")
	await get_tree().physics_frame
	await get_tree().physics_frame
	var moved := start.distance_to(player.global_position)
	print("PILOT_TEST move from=%s to=%s dist=%.2f floor=%s" % [
		start, player.global_position, moved, player.is_on_floor(),
	])
	if moved < 0.5:
		_fail("el jugador no se movió")
		return
	if not player.is_on_floor():
		_fail("el jugador no está sobre el suelo")
		return
	await _capture("fm_pilot_02_moved.png")

	# Interacción con el panel.
	var before := int(panel.activations)
	await _send_action("interact")
	await get_tree().create_timer(0.25).timeout
	if int(panel.activations) == before:
		var direct := InputEventAction.new()
		direct.action = "interact"
		direct.pressed = true
		player._unhandled_input(direct)
		await get_tree().process_frame
	print("PILOT_TEST interact before=%d after=%d" % [before, int(panel.activations)])
	if int(panel.activations) != before + 1:
		_fail("la interacción no activó el panel")
		return
	await _capture("fm_pilot_03_interact.png")

	# Linterna.
	var flashlight_before := player.flashlight_on
	await _send_action("flashlight")
	await get_tree().create_timer(0.25).timeout
	if player.flashlight_on == flashlight_before:
		var direct := InputEventAction.new()
		direct.action = "flashlight"
		direct.pressed = true
		player._unhandled_input(direct)
		await get_tree().process_frame
	print("PILOT_TEST flashlight before=%s after=%s" % [
		flashlight_before, player.flashlight_on,
	])
	if player.flashlight_on == flashlight_before:
		_fail("la linterna no respondió")
		return
	if not player.flashlight_on:
		await _capture("fm_pilot_04_flashlight_off.png")
		await _send_action("flashlight")
		await get_tree().create_timer(0.25).timeout
		if not player.flashlight_on:
			_fail("la linterna no volvió a encenderse")
			return
	else:
		await _capture("fm_pilot_04_flashlight_on.png")

	# Vista oblicua de la puerta E abierta.
	player.global_position = Vector3(56.5, 0.15, -25.5)
	var to_door := Vector3(62.0, 0.0, -21.0) - Vector3(56.5, 0.0, -25.5)
	player.rotation.y = atan2(-to_door.x, -to_door.z)
	await get_tree().physics_frame
	await get_tree().physics_frame
	await get_tree().create_timer(0.35).timeout
	await _capture("fm_pilot_05_door_e.png")

	# Comprobación de paso libre y hoja de puerta mediante rayos.
	await get_tree().physics_frame
	var gap := _ray(Vector3(58.0, 1.5, -21.0), Vector3(63.0, 1.5, -21.0))
	var leaf := _ray(Vector3(58.0, 1.5, -18.15), Vector3(63.0, 1.5, -18.15))
	var wall := _ray(Vector3(60.0, 1.5, -14.0), Vector3(63.0, 1.5, -14.0))
	print("PILOT_TEST rays gap_hit=%s leaf_hit=%s wall_hit=%s" % [
		_ray_name(gap), _ray_name(leaf), _ray_name(wall),
	])
	if not gap.is_empty():
		_fail("el paso de la puerta E está bloqueado")
		return
	if leaf.is_empty():
		_fail("la hoja de la puerta E no tiene colisión")
		return
	if wall.is_empty():
		_fail("el muro este no tiene colisión")
		return

	# Cruce del umbral abierto hasta la plataforma de seguridad.
	player.global_position = Vector3(60.5, 0.15, -21.0)
	player.rotation.y = -PI / 2.0
	await get_tree().physics_frame
	Input.action_press("move_up")
	await get_tree().create_timer(1.1).timeout
	Input.action_release("move_up")
	await get_tree().physics_frame
	await get_tree().physics_frame
	print("PILOT_TEST doorway x=%.2f floor=%s" % [
		player.global_position.x, player.is_on_floor(),
	])
	if player.global_position.x < 62.2:
		_fail("no se pudo cruzar el umbral de la puerta E")
		return
	if not player.is_on_floor():
		_fail("el jugador cayó al cruzar el umbral")
		return
	player.rotation.y = PI / 2.0
	await get_tree().physics_frame
	await get_tree().physics_frame
	await get_tree().create_timer(0.35).timeout
	await _capture("fm_pilot_06_threshold.png")

	# Evidencia visual: pared de herramientas y referencia de escala.
	player.global_position = Vector3(43.2, 0.15, -12.8)
	player.rotation.y = PI / 2.0
	await get_tree().physics_frame
	await get_tree().physics_frame
	await get_tree().create_timer(0.35).timeout
	await _capture("fm_pilot_07_toolwall.png")

	player.global_position = Vector3(49.0, 0.15, -14.0)
	player.rotation.y = -PI / 2.0
	await get_tree().physics_frame
	await get_tree().physics_frame
	await get_tree().create_timer(0.35).timeout
	await _capture("fm_pilot_08_player_reference.png")

	# Rendimiento: vista amplia del salón, 3 s, VSync desactivado.
	player.global_position = SPAWN
	player.rotation.y = 0.0
	await get_tree().physics_frame
	await get_tree().physics_frame
	await get_tree().create_timer(0.4).timeout
	await _capture("fm_pilot_09_room.png")

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
	print("PILOT_TEST fps avg=%.1f min=%.1f max=%.1f samples=%d" % [
		fps_avg, fps_min, fps_max, _fps_samples.size(),
	])
	print("PILOT_TEST render draw_calls=%d primitives=%d objects=%d" % [
		int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)),
		int(Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)),
		int(Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME)),
	])

	# Regresión: el centro de la sala debe ser transitable.
	player.global_position = Vector3(52.0, 0.15, -14.0)
	player.rotation.y = 0.0
	await get_tree().physics_frame
	await get_tree().physics_frame
	Input.action_press("move_up")
	await get_tree().create_timer(2.0).timeout
	Input.action_release("move_up")
	await get_tree().physics_frame
	await get_tree().physics_frame
	print("PILOT_TEST center_walk z=%.2f floor=%s" % [
		player.global_position.z, player.is_on_floor(),
	])
	if player.global_position.z >= -17.0:
		_fail("el centro de la sala sigue bloqueado")
		return
	if not player.is_on_floor():
		_fail("el jugador cayó al cruzar el centro")
		return
	await _capture("fm_pilot_10_center.png")

	print("PILOT_TEST final_pos=%s battery=%.1f stamina=%.1f" % [
		player.global_position, player.battery, player.stamina,
	])
	Input.action_release("move_up")
	print("PILOT_AUTOTEST_OK")
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


func _ray(from: Vector3, to: Vector3) -> Dictionary:
	var query := PhysicsRayQueryParameters3D.create(from, to)
	query.collision_mask = 1
	var exclude: Array[RID] = []
	if player != null and is_instance_valid(player):
		exclude.append(player.get_rid())
	query.exclude = exclude
	return get_world_3d().direct_space_state.intersect_ray(query)


func _ray_name(hit: Dictionary) -> String:
	if hit.is_empty():
		return "clear"
	var collider = hit.get("collider")
	if collider is Node:
		return (collider as Node).name
	return "hit"


func _capture(file_name: String) -> void:
	if _headless:
		return
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	var path := ProjectSettings.globalize_path("res://docs").path_join(file_name)
	var err := image.save_png(path)
	print("PILOT_CAPTURE %s err=%d size=%s" % [path, err, image.get_size()])


func _fail(reason: String) -> void:
	Input.action_release("move_up")
	printerr("PILOT_AUTOTEST_FAIL ", reason)
	get_tree().quit(1)
