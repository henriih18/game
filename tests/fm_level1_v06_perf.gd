extends Node

## Rendimiento del Nivel 1 V06 completo en ventana.
##
## Carga `scenes/fm/level1_v06.tscn` (Z10 + Recepción + Seguridad + Corredor
## + acceso) y mide ~13 s con:
##   - los dos Vigilantes activos en su patrulla real (sin suspender ni tocar
##     visión, velocidad o percepción);
##   - una cámara espectadora que recorre cinco vistas representativas
##     (Z10, compuerta Z10, corredor, marcador de extracción y acceso a
##     Seguridad) con un dolly lento dentro de cada vista;
##   - la compuerta real de Z10 abriéndose y cerrándose con `set_open()`,
##     incluido su ruido y su animación;
##   - el jugador real inmovilizado en Recepción, lejos del alcance de los
##     Vigilantes, para que no haya captura y no se altere la IA.
##
## Mide FPS medio/mínimo/p1 %, draw calls, primitivas, objetos, memoria de
## texturas y vídeo, tiempos de proceso/física y estado de los Vigilantes.
##
## NO es una partida completa ni una medida del juego final. No modifica
## scripts de juego, IA, escenas, GLB ni materiales.
##
## Uso:
##   godot --path . tests/fm_level1_v06_perf.tscn
##   godot --path . tests/fm_level1_v06_perf.tscn -- \
##       --width 1920 --height 1080 --borderless --label 1080p
##
## Opciones (tras `--`):
##   --width N --height N   resolución de la ventana (por defecto 1280x720)
##   --duration S           segundos medidos (por defecto 13.0)
##   --label TEXTO          etiqueta de la corrida
##   --borderless           ventana sin bordes (útil para 1920x1080)
##   --native               fuerza el viewport 3D a la resolución pedida.
##                          Sin este flag, el proyecto usa
##                          window/stretch/mode="canvas_items" con base
##                          1280x720 y una ventana 1920x1080 sigue
##                          renderizando el viewport a 1280x720.
##   --capture DIR          guarda una captura por vista durante el prewarm
##   --preset ID            aplica un preset gráfico (bajo/medio/alto/ultra)
##                          después de cargar el nivel. El preset manda sobre
##                          --native: Bajo/Medio fijan el viewport interno a
##                          1280x720 y Alto/Ultra lo fijan al tamaño de la
##                          ventana.
##
## En headless no mide GPU ni draw calls: imprime SKIP y sale con 0.

const SCENE_PATH := "res://scenes/fm/level1_v06.tscn"
const DEFAULT_DURATION_S := 13.0
const SAMPLE_INTERVAL_S := 1.0
## Posición segura del jugador dentro de Recepción, lejos de ambos Vigilantes
## y fuera de la zona de extracción. Se ajusta a la altura real del suelo.
const SAFE_PLAYER_PROBE := Vector3(-103.0, 2.0, 21.0)
const SAFE_PLAYER_FALLBACK := Vector3(-94.0, 0.12, 36.6)

var _width := 1280
var _height := 720
var _duration_s := DEFAULT_DURATION_S
var _label := "1280x720"
var _borderless := false
var _native := false
var _preset_id := ""
var _capture_dir := ""

var _scene: Node
var _player: FMPlayer
var _camera: Camera3D
var _phases: Array[Dictionary] = []
var _phase_reports: Array[Dictionary] = []

var _running := false
var _start_usec := 0
var _last_usec := 0
var _elapsed := 0.0
var _phase_index := -1
var _phase_elapsed := 0.0
var _next_sample_s := 1.0
var _sample_start_usec := 0
var _sample_frames := 0

var _frames: PackedFloat64Array = PackedFloat64Array()
var _frame_phase: PackedInt32Array = PackedInt32Array()
var _phase_frames: Array = []
var _phase_seconds := 0.0
var _phase_draw_sum := 0.0
var _phase_draw_max := 0
var _phase_prims_sum := 0.0
var _phase_prims_max := 0
var _phase_render_objects_max := 0
var _phase_objects_max := 0
var _phase_tex_max := 0.0
var _phase_video_max := 0.0

var _draw_last := 0
var _draw_sum := 0.0
var _draw_max := 0
var _prims_last := 0
var _prims_sum := 0.0
var _prims_max := 0
var _render_objects_max := 0
var _objects_last := 0
var _objects_max := 0
var _tex_last := 0.0
var _tex_max := 0.0
var _video_last := 0.0
var _video_max := 0.0
var _static_mb := 0.0

var _watcher_prev := Vector3.ZERO
var _watcher_path := 0.0
var _watcher_states := {}
var _security_prev := Vector3.ZERO
var _security_path := 0.0
var _security_states := {}
var _captures := 0
var _watchers_active := true
var _vsync_ok := false

var _gate_noise_start := 0
var _gate_open_time := -1.0
var _gate_close_time := -1.0


func _ready() -> void:
	_parse_args()
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE

	if DisplayServer.get_name() == "headless":
		print("FM_L1V06_PERF: SKIP (requiere ventana; headless no mide GPU ni draw calls)")
		get_tree().quit(0)
		return

	Engine.max_fps = 0
	_apply_window()
	_vsync_ok = DisplayServer.window_get_vsync_mode() == DisplayServer.VSYNC_DISABLED

	print("FM_L1V06_PERF_START label=%s requested=%dx%d window=%dx%d viewport=%dx%d screen=%dx%d vsync=%s max_fps=%d duration=%.1f godot=%s gpu=%s" % [
		_label, _width, _height,
		DisplayServer.window_get_size().x, DisplayServer.window_get_size().y,
		int(get_viewport().get_visible_rect().size.x), int(get_viewport().get_visible_rect().size.y),
		DisplayServer.screen_get_size().x, DisplayServer.screen_get_size().y,
		"disabled" if _vsync_ok else str(DisplayServer.window_get_vsync_mode()),
		Engine.max_fps, _duration_s, Engine.get_version_info().get("string", "?"),
		RenderingServer.get_video_adapter_name(),
	])
	_print_vram("FM_L1V06_PERF_VRAM_BASELINE", _vram_now())
	print("FM_L1V06_PERF_OBJECTS_BASELINE objects=%d nodes=%d resources=%d" % [
		int(Performance.get_monitor(Performance.OBJECT_COUNT)),
		int(Performance.get_monitor(Performance.OBJECT_NODE_COUNT)),
		int(Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT)),
	])

	var packed := load(SCENE_PATH) as PackedScene
	if packed == null:
		_fail("no se pudo cargar %s" % SCENE_PATH)
		return
	_scene = packed.instantiate()
	add_child(_scene)

	var guard := 0
	while not _scene.level_ready and guard < 7200:
		await get_tree().process_frame
		guard += 1
	if not _scene.level_ready:
		_fail("level_ready no llegó (guard=%d)" % guard)
		return

	# El nivel captura el ratón al final de su _ready; devolverlo a la prueba.
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	_apply_window()
	_force_native_resolution()
	_apply_preset_if_requested()
	_vsync_ok = DisplayServer.window_get_vsync_mode() == DisplayServer.VSYNC_DISABLED
	for _i in range(6):
		await get_tree().process_frame
	_print_window("POST_LEVEL")

	_player = _scene.player as FMPlayer
	if _player == null or not is_instance_valid(_player):
		_fail("sin jugador")
		return
	_place_player_safe()
	# La linterna real sigue al jugador, que está estacionado en Recepción.
	# Para que la cámara espectadora mida la iluminación real de gameplay, se
	# clona su linterna sobre la cámara y se apaga la del jugador: el número de
	# luces y su coste (spot con sombra + spill sin sombra) es el mismo.
	_player.flashlight_on = false
	_player.battery = 100.0

	# Los dos Vigilantes quedan activos con su configuración real del nivel.
	# No se toca visión, velocidad, patrulla ni percepción.
	for watcher in [_scene.watcher, _scene.security_watcher]:
		if watcher != null and is_instance_valid(watcher):
			watcher.set_physics_process(true)

	_phases = _make_phases()
	var phase_duration := _duration_s / float(_phases.size())
	for phase in _phases:
		phase["duration"] = phase_duration
	_phase_reports.clear()
	_phase_frames.clear()
	for _i in range(_phases.size()):
		_phase_frames.append(PackedFloat64Array())
		_phase_reports.append({})

	_setup_camera()
	_print_environment()
	_print_setup()

	await _prewarm()
	await _settle()
	_print_player_state()

	_gate_noise_start = _scene.get_door_noise_count()
	_watcher_prev = _scene.watcher.global_position
	_security_prev = _scene.security_watcher.global_position
	_sample_start_usec = Time.get_ticks_usec()

	await _measure()
	_report()
	# Las estadísticas de geometría se recogen después de medir: `get_faces()`
	# en PrimitiveMesh crea datos temporales y no debe alterar el conteo de
	# objetos de la ventana medida.
	_collect_scene_stats()
	_collect_sector_stats()
	_cleanup()


func _parse_args() -> void:
	var args := OS.get_cmdline_user_args()
	var i := 0
	while i < args.size():
		var arg := args[i]
		match arg:
			"--width":
				if i + 1 < args.size():
					_width = args[i + 1].to_int()
					i += 1
			"--height":
				if i + 1 < args.size():
					_height = args[i + 1].to_int()
					i += 1
			"--duration":
				if i + 1 < args.size():
					_duration_s = args[i + 1].to_float()
					i += 1
			"--label":
				if i + 1 < args.size():
					_label = args[i + 1]
					i += 1
			"--capture":
				if i + 1 < args.size():
					_capture_dir = args[i + 1]
					i += 1
			"--borderless":
				_borderless = true
			"--native":
				_native = true
			"--preset":
				if i + 1 < args.size():
					_preset_id = args[i + 1].to_lower()
					i += 1
		i += 1
	_width = maxi(320, _width)
	_height = maxi(200, _height)
	_duration_s = clampf(_duration_s, 5.0, 60.0)
	if _label.is_empty():
		_label = "%dx%d" % [_width, _height]


func _apply_window() -> void:
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_BORDERLESS, _borderless)
	DisplayServer.window_set_size(Vector2i(_width, _height))
	if _borderless:
		DisplayServer.window_set_position(Vector2i(0, 0))


func _force_native_resolution() -> void:
	if not _native:
		return
	# Con un preset explícito, manda el preset: Bajo/Medio fijan 720p interno
	# y Alto/Ultra el tamaño de la ventana. Evita mezclar --native con --preset.
	if not _preset_id.is_empty():
		return
	# El proyecto usa canvas_items con base 1280x720. Para intentar medir de
	# verdad 1920x1080 hay que desactivar el escalado y forzar el viewport;
	# si no, la ventana 1080p sigue renderizando 1280x720.
	get_window().content_scale_mode = Window.CONTENT_SCALE_MODE_DISABLED
	get_viewport().size = Vector2i(_width, _height)


func _apply_preset_if_requested() -> void:
	if _preset_id.is_empty():
		return
	var graphics := get_node_or_null("/root/Graphics") as FMGraphicsPresets
	if graphics == null:
		_fail("sin autoload Graphics para --preset %s" % _preset_id)
		return
	if not graphics.apply_preset(_preset_id):
		_fail("preset desconocido: %s" % _preset_id)
		return
	var preset := graphics.get_preset(_preset_id)
	print("FM_L1V06_PERF_PRESET id=%s content=%s native=%s 3d_scale=%.2f msaa=%d shadow_lights=%d/%d shadow_atlas=%d ssr=%s ssao=%s fog=%s" % [
		_preset_id, str(get_window().content_scale_size), str(preset["native_resolution"]),
		float(preset["scaling_3d_scale"]), int(preset["msaa_3d"]),
		graphics.get_applied_shadow_light_count(), 4,
		graphics.get_applied_shadow_atlas(),
		"on" if bool(preset["ssr_enabled"]) else "off",
		"on" if bool(preset["ssao_enabled"]) else "off",
		"on" if bool(preset["volumetric_fog_enabled"]) else "off",
	])


func _print_window(tag: String) -> void:
	var vp := get_viewport()
	print("FM_L1V06_PERF_WINDOW tag=%s requested=%dx%d window=%dx%d viewport=%dx%d vp_size=%s vp_texture=%s content_scale_mode=%d content_scale_size=%s vsync=%s max_fps=%d" % [
		tag, _width, _height,
		DisplayServer.window_get_size().x, DisplayServer.window_get_size().y,
		int(vp.get_visible_rect().size.x), int(vp.get_visible_rect().size.y),
		str(vp.size), str(vp.get_texture().get_size()),
		int(get_window().content_scale_mode), str(get_window().content_scale_size),
		"disabled" if DisplayServer.window_get_vsync_mode() == DisplayServer.VSYNC_DISABLED else str(DisplayServer.window_get_vsync_mode()),
		Engine.max_fps,
	])


func _make_phases() -> Array[Dictionary]:
	# Cinco vistas con dolly lento. Las posiciones están dentro de los volúmenes
	# jugables del nivel y miran contenido real: objetivo de Z10, compuerta de
	# Z10, corredor completo, marcador de extracción y acceso a Seguridad.
	return [
		{
			"id": "z10_objective",
			"duration": 2.6,
			"pos_a": Vector3(43.4, 1.75, -22.4),
			"pos_b": Vector3(46.4, 1.75, -22.4),
			"look_a": Vector3(57.4, 1.05, -20.4),
			"look_b": Vector3(59.2, 1.05, -21.4),
			"gate": "",
		},
		{
			"id": "z10_gate",
			"duration": 2.6,
			"pos_a": Vector3(43.0, 1.72, -6.6),
			"pos_b": Vector3(43.0, 1.72, -5.4),
			"look_a": Vector3(43.0, 1.35, -4.0),
			"look_b": Vector3(43.0, 1.35, -4.0),
			"gate": "open",
		},
		{
			"id": "corridor",
			"duration": 2.6,
			"pos_a": Vector3(-88.0, 1.75, 0.0),
			"pos_b": Vector3(-82.0, 1.75, 0.0),
			"look_a": Vector3(60.0, 1.55, 0.0),
			"look_b": Vector3(60.0, 1.55, 0.0),
			"gate": "close",
		},
		{
			"id": "reception_marker",
			"duration": 2.6,
			"pos_a": Vector3(-100.4, 1.75, 29.4),
			"pos_b": Vector3(-98.2, 1.75, 31.6),
			"look_a": Vector3(-94.0, 1.55, 37.6),
			"look_b": Vector3(-94.0, 1.55, 37.6),
			"gate": "",
		},
		{
			"id": "security_access",
			"duration": 2.6,
			"pos_a": Vector3(-64.0, 1.66, -10.9),
			"pos_b": Vector3(-67.0, 1.66, -10.9),
			"look_a": Vector3(-76.0, 1.35, -10.9),
			"look_b": Vector3(-76.0, 1.35, -10.9),
			"gate": "",
		},
	]


func _setup_camera() -> void:
	_camera = Camera3D.new()
	_camera.name = "PerfSpectatorCamera"
	_camera.fov = 76.0
	_camera.near = 0.05
	_camera.far = 70.0
	add_child(_camera)
	_camera.current = true
	_add_spectator_flashlight()
	var first: Dictionary = _phases[0]
	_camera.global_position = first["pos_a"]
	_camera.look_at(first["look_a"], Vector3.UP)


func _add_spectator_flashlight() -> void:
	var source: SpotLight3D = _player.flashlight
	if source == null or not is_instance_valid(source):
		return
	var spot := SpotLight3D.new()
	spot.name = "PerfFlashlight"
	spot.position = source.position
	spot.light_color = source.light_color
	spot.light_energy = source.light_energy
	spot.spot_range = source.spot_range
	spot.spot_angle = source.spot_angle
	spot.spot_attenuation = source.spot_attenuation
	spot.spot_angle_attenuation = source.spot_angle_attenuation
	spot.shadow_enabled = source.shadow_enabled
	spot.light_volumetric_fog_energy = source.light_volumetric_fog_energy
	spot.light_projector = source.light_projector
	_camera.add_child(spot)

	var source_spill := _player.camera.get_node_or_null("FlashlightSpill") as SpotLight3D
	if source_spill == null:
		return
	var spill := SpotLight3D.new()
	spill.name = "PerfFlashlightSpill"
	spill.light_color = source_spill.light_color
	spill.light_energy = source_spill.light_energy
	spill.spot_range = source_spill.spot_range
	spill.spot_angle = source_spill.spot_angle
	spill.spot_attenuation = source_spill.spot_attenuation
	spill.spot_angle_attenuation = source_spill.spot_angle_attenuation
	spill.shadow_enabled = source_spill.shadow_enabled
	_camera.add_child(spill)
	print("FM_L1V06_PERF_FLASHLIGHT spectator energy=%.1f range=%.1f angle=%.1f shadow=%s spill=%.1f/%.1f player_on=false" % [
		spot.light_energy, spot.spot_range, spot.spot_angle, str(spot.shadow_enabled),
		spill.light_energy, spill.spot_range,
	])


func _place_player_safe() -> void:
	var space: PhysicsDirectSpaceState3D = _scene.get_world_3d().direct_space_state
	var query := PhysicsRayQueryParameters3D.create(
		SAFE_PLAYER_PROBE, SAFE_PLAYER_PROBE + Vector3(0.0, -3.0, 0.0)
	)
	query.collision_mask = 1
	var hit: Dictionary = space.intersect_ray(query)
	var target := SAFE_PLAYER_FALLBACK
	if not hit.is_empty():
		var point: Vector3 = hit.get("position", SAFE_PLAYER_FALLBACK)
		target = point + Vector3(0.0, 0.12, 0.0)
	_player.global_position = target
	_player.velocity = Vector3.ZERO
	_player.rotation.y = 0.0
	_player.camera.rotation.x = 0.0
	_player.camera.rotation.y = 0.0
	_player.camera.position = Vector3(0.0, 1.62, 0.0)


func _print_player_state() -> void:
	print("FM_L1V06_PERF_PLAYER pos=%s on_floor=%s hidden=%s flashlight=%s respawns=%d state=%d" % [
		str(_player.global_position), str(_player.is_on_floor()),
		str(_player.hidden), str(_player.flashlight_on), _scene.respawn_count, int(_scene.state),
	])


func _collect_scene_stats() -> void:
	var started := Time.get_ticks_msec()
	var meshes := _scene.find_children("*", "MeshInstance3D", true, false)
	var collision_shapes := _scene.find_children("*", "CollisionShape3D", true, false)
	var static_bodies := _scene.find_children("*", "StaticBody3D", true, false)
	var areas := _scene.find_children("*", "Area3D", true, false)
	var lights := _scene.find_children("*", "Light3D", true, false)
	var triangles := 0
	var surfaces := 0
	var mesh_ids := {}
	var material_ids := {}
	for node in meshes:
		var mi := node as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		mesh_ids[mi.mesh.get_instance_id()] = true
		var surface_count := mi.mesh.get_surface_count()
		surfaces += surface_count
		triangles += _mesh_triangles(mi.mesh)
		for surface in range(surface_count):
			var material: Material = mi.material_override
			if material == null:
				material = mi.get_active_material(surface)
			if material != null:
				material_ids[material.get_instance_id()] = true
	var shadow_lights := 0
	var omni_lights := 0
	var spot_lights := 0
	var directional_lights := 0
	for node in lights:
		var light := node as Light3D
		if light == null:
			continue
		if light.shadow_enabled:
			shadow_lights += 1
		if light is OmniLight3D:
			omni_lights += 1
		elif light is SpotLight3D:
			spot_lights += 1
		elif light is DirectionalLight3D:
			directional_lights += 1
	print("FM_L1V06_PERF_SCENE nodes=%d meshes=%d surfaces=%d triangles=%d unique_meshes=%d materials=%d lights=%d shadow_lights=%d omni=%d spot=%d directional=%d collision_shapes=%d static_bodies=%d areas=%d nav_main_polys=%d nav_service_polys=%d nav_bake_ms=%d/%d gates=%d collect_ms=%d" % [
		int(Performance.get_monitor(Performance.OBJECT_NODE_COUNT)),
		meshes.size(), surfaces, triangles, mesh_ids.size(), material_ids.size(),
		lights.size(), shadow_lights, omni_lights, spot_lights, directional_lights,
		collision_shapes.size(), static_bodies.size(), areas.size(),
		_scene.get_nav_main_polygon_count(), _scene.get_nav_service_polygon_count(),
		_scene.get_nav_bake_ms(), _scene.get_nav_service_bake_ms(),
		_scene.level_gates.size(), Time.get_ticks_msec() - started,
	])


func _collect_sector_stats() -> void:
	var ids: Array[String] = ["Z10", "Reception", "Security", "Corridor", "SecurityAccess"]
	for id in ids:
		var root: Node3D = _scene.sector_roots.get(id) as Node3D
		if root == null or not is_instance_valid(root):
			print("FM_L1V06_PERF_SECTOR id=%s missing=true" % id)
			continue
		var meshes := root.find_children("*", "MeshInstance3D", true, false)
		var triangles := 0
		var surfaces := 0
		var material_ids := {}
		for node in meshes:
			var mi := node as MeshInstance3D
			if mi == null or mi.mesh == null:
				continue
			var surface_count := mi.mesh.get_surface_count()
			surfaces += surface_count
			triangles += _mesh_triangles(mi.mesh)
			for surface in range(surface_count):
				var material: Material = mi.material_override
				if material == null:
					material = mi.get_active_material(surface)
				if material != null:
					material_ids[material.get_instance_id()] = true
		var art_root := root.get_parent() as Node3D
		var lights := 0
		var shadow_lights := 0
		if art_root != null:
			for node in art_root.find_children("*", "Light3D", true, false):
				var light := node as Light3D
				if light == null:
					continue
				lights += 1
				if light.shadow_enabled:
					shadow_lights += 1
		print("FM_L1V06_PERF_SECTOR id=%s meshes=%d surfaces=%d triangles=%d materials=%d lights=%d shadow_lights=%d" % [
			id, meshes.size(), surfaces, triangles, material_ids.size(), lights, shadow_lights,
		])


func _mesh_triangles(mesh: Mesh) -> int:
	# `surface_get_primitive_type` solo está implementado en ArrayMesh; en
	# PrimitiveMesh (BoxMesh, TorusMesh, etc.) la llamada falla. Para esos
	# casos se usan las caras ya trianguladas.
	if not (mesh is ArrayMesh):
		return int(float(mesh.get_faces().size()) / 3.0)
	var total := 0
	for surface in range(mesh.get_surface_count()):
		var primitive: int = mesh.surface_get_primitive_type(surface)
		var array_len: int = mesh.surface_get_array_len(surface)
		var index_len: int = mesh.surface_get_array_index_len(surface)
		var count: int = index_len if index_len > 0 else array_len
		match primitive:
			Mesh.PRIMITIVE_TRIANGLES:
				total += int(float(count) / 3.0)
			Mesh.PRIMITIVE_TRIANGLE_STRIP:
				total += maxi(0, count - 2)
	return total


func _print_environment() -> void:
	var env: Environment = _scene.level_environment
	if env == null:
		print("FM_L1V06_PERF_ENV missing=true")
		return
	print("FM_L1V06_PERF_ENV ssr=%s ssr_steps=%d ssao=%s glow=%s volumetric_fog=%s fog_density=%.4f tonemap=%d ambient_source=%d ambient_energy=%.2f" % [
		str(env.ssr_enabled), env.ssr_max_steps, str(env.ssao_enabled), str(env.glow_enabled),
		str(env.volumetric_fog_enabled), env.volumetric_fog_density,
		int(env.tonemap_mode), int(env.ambient_light_source), env.ambient_light_energy,
	])


func _print_setup() -> void:
	_print_watcher("main", _scene.watcher)
	_print_watcher("security", _scene.security_watcher)
	print("FM_L1V06_PERF_MARKER pos=%s ring=%s sign=%s beacons=%d dynamic_lights=%d gates=%s" % [
		str(_scene.get_extraction_marker_position()),
		str(_scene.extraction_ring != null and _scene.extraction_ring.is_visible_in_tree()),
		str(_scene.extraction_sign != null and _scene.extraction_sign.is_visible_in_tree()),
		_scene.extraction_beacons.size(), _scene.get_extraction_marker_light_count(),
		str(_scene.get_gate_ids()),
	])
	print("FM_L1V06_PERF_HATCH open=%s lift=%.2f collisions=%d/%d" % [
		str(_scene.security_hatch != null and _scene.security_hatch.is_open),
		_scene.security_hatch.get_mesh_lift() if _scene.security_hatch != null else -1.0,
		_scene.security_hatch.get_enabled_collision_count() if _scene.security_hatch != null else -1,
		_scene.security_hatch.get_collision_shape_count() if _scene.security_hatch != null else -1,
	])


func _print_watcher(tag: String, watcher: FMWatcher) -> void:
	if watcher == null or not is_instance_valid(watcher):
		print("FM_L1V06_PERF_WATCHER tag=%s missing=true" % tag)
		return
	print("FM_L1V06_PERF_WATCHER tag=%s pos=%s state=%s vision=%.1f patrol=%d physics=%s observed=%s navigation=%s" % [
		tag, str(watcher.global_position), _state_name(int(watcher.state)),
		watcher.vision_distance, watcher.patrol_points.size(),
		str(watcher.is_physics_processing()), str(watcher.observed),
		str(watcher.use_navigation),
	])


func _prewarm() -> void:
	# Recorrido de calentamiento: compila shaders y estabiliza pipelines antes
	# de medir. No se registra ningún frame. Aquí no se abren compuertas.
	for index in range(_phases.size()):
		_set_phase_camera(index, 0.0)
		await get_tree().process_frame
		await RenderingServer.frame_post_draw
		if not _capture_dir.is_empty():
			_save_capture(index)
		await get_tree().create_timer(0.45).timeout


func _settle() -> void:
	_set_phase_camera(0, 0.0)
	await get_tree().create_timer(0.6).timeout


func _measure() -> void:
	_running = true
	_start_usec = Time.get_ticks_usec()
	_last_usec = _start_usec
	_elapsed = 0.0
	_next_sample_s = SAMPLE_INTERVAL_S
	_sample_start_usec = _start_usec
	_sample_frames = 0
	_phase_index = -1
	_start_phase(0)

	while _running:
		var now := Time.get_ticks_usec()
		var dt := float(now - _last_usec) / 1000000.0
		_last_usec = now
		if dt > 0.000001:
			_record_frame(dt)
		_elapsed = float(now - _start_usec) / 1000000.0
		_phase_elapsed += dt
		_update_camera(dt)
		_track_ai(dt)

		if _elapsed >= _next_sample_s:
			_sample(_elapsed)
			_next_sample_s += SAMPLE_INTERVAL_S

		if _phase_elapsed >= _phase_duration(_phase_index):
			var next_index := _phase_index + 1
			_end_phase(_phase_index)
			if next_index < _phases.size():
				_start_phase(next_index)
			else:
				_running = false

		await get_tree().process_frame

	_end_phase(_phase_index)


func _start_phase(index: int) -> void:
	_phase_index = index
	_phase_elapsed = 0.0
	_phase_seconds = 0.0
	_phase_draw_sum = 0.0
	_phase_draw_max = 0
	_phase_prims_sum = 0.0
	_phase_prims_max = 0
	_phase_render_objects_max = 0
	_phase_objects_max = 0
	_phase_tex_max = 0.0
	_phase_video_max = 0.0
	var phase: Dictionary = _phases[index]
	var action := str(phase.get("gate", ""))
	if action == "open":
		var gate: FMLevel1Gate = _scene.get_gate("Z10")
		if gate != null and is_instance_valid(gate):
			gate.set_open(true)
			_gate_open_time = _elapsed
			print("FM_L1V06_PERF_GATE_ACTION t=%.2f action=open id=%s" % [_elapsed, gate.gate_id])
	if action == "close":
		var gate: FMLevel1Gate = _scene.get_gate("Z10")
		if gate != null and is_instance_valid(gate):
			gate.set_open(false)
			_gate_close_time = _elapsed
			print("FM_L1V06_PERF_GATE_ACTION t=%.2f action=close id=%s" % [_elapsed, gate.gate_id])
	_set_phase_camera(index, 0.0)
	print("FM_L1V06_PERF_PHASE_BEGIN index=%d id=%s t=%.2f pos=%s" % [
		index, str(phase["id"]), _elapsed, str(_camera.global_position),
	])


func _end_phase(index: int) -> void:
	if index < 0 or index >= _phases.size():
		return
	if not (_phase_reports[index] as Dictionary).is_empty():
		return
	var phase: Dictionary = _phases[index]
	var frames: PackedFloat64Array = _phase_frames[index]
	var sorted := frames.duplicate()
	sorted.sort()
	var max_dt := _percentile(sorted, 1.0)
	var report := {
		"id": str(phase["id"]),
		"seconds": _phase_seconds,
		"frames": frames.size(),
		"fps_avg": float(frames.size()) / maxf(_phase_seconds, 0.001),
		"fps_min": 1.0 / maxf(max_dt, 0.001),
		"fps_p1": 1.0 / maxf(_percentile(sorted, 0.99), 0.001),
		"frame_ms_avg": _average_ms(frames),
		"frame_ms_p95": _percentile(sorted, 0.95) * 1000.0,
		"frame_ms_p99": _percentile(sorted, 0.99) * 1000.0,
		"frame_ms_max": max_dt * 1000.0,
		"draws_avg": _phase_draw_sum / maxf(float(frames.size()), 1.0),
		"draws_max": _phase_draw_max,
		"prims_avg": _phase_prims_sum / maxf(float(frames.size()), 1.0),
		"prims_max": _phase_prims_max,
		"render_objects_max": _phase_render_objects_max,
		"objects_max": _phase_objects_max,
		"tex_mb_max": _phase_tex_max,
		"video_mb_max": _phase_video_max,
	}
	_phase_reports[index] = report
	print("FM_L1V06_PERF_PHASE_END index=%d id=%s seconds=%.2f frames=%d fps_avg=%.1f fps_min=%.1f fps_p1=%.1f frame_ms_avg=%.2f p95=%.2f p99=%.2f max=%.2f draws_avg=%.0f draws_max=%d prims_avg=%.0f prims_max=%d objects_max=%d render_objects_max=%d tex_mb_max=%.1f video_mb_max=%.1f" % [
		index, report["id"], report["seconds"], report["frames"], report["fps_avg"],
		report["fps_min"], report["fps_p1"], report["frame_ms_avg"], report["frame_ms_p95"],
		report["frame_ms_p99"], report["frame_ms_max"], report["draws_avg"],
		report["draws_max"], report["prims_avg"], report["prims_max"],
		report["objects_max"], report["render_objects_max"],
		report["tex_mb_max"], report["video_mb_max"],
	])


func _phase_duration(index: int) -> float:
	if index < 0 or index >= _phases.size():
		return 0.0
	return float(_phases[index]["duration"])


func _set_phase_camera(index: int, alpha: float) -> void:
	if _camera == null:
		return
	var phase: Dictionary = _phases[index]
	var pos: Vector3 = (phase["pos_a"] as Vector3).lerp(phase["pos_b"] as Vector3, alpha)
	var look: Vector3 = (phase["look_a"] as Vector3).lerp(phase["look_b"] as Vector3, alpha)
	_camera.global_position = pos
	_camera.look_at(look, Vector3.UP)


func _update_camera(dt: float) -> void:
	if _phase_index < 0:
		return
	var duration := maxf(_phase_duration(_phase_index), 0.001)
	var alpha := clampf(_phase_elapsed / duration, 0.0, 1.0)
	_set_phase_camera(_phase_index, alpha)


func _record_frame(dt: float) -> void:
	_frames.append(dt)
	_frame_phase.append(_phase_index)
	var phase_frames: PackedFloat64Array = _phase_frames[_phase_index]
	phase_frames.append(dt)
	_phase_frames[_phase_index] = phase_frames
	_phase_seconds += dt
	_sample_frames += 1

	var draws := int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME))
	var prims := int(Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME))
	var render_objects := int(Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME))
	var objects := int(Performance.get_monitor(Performance.OBJECT_COUNT))
	var tex_mb := Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED) / (1024.0 * 1024.0)
	var video_mb := Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED) / (1024.0 * 1024.0)

	_draw_last = draws
	_draw_sum += float(draws)
	_draw_max = maxi(_draw_max, draws)
	_prims_last = prims
	_prims_sum += float(prims)
	_prims_max = maxi(_prims_max, prims)
	_render_objects_max = maxi(_render_objects_max, render_objects)
	_objects_last = objects
	_objects_max = maxi(_objects_max, objects)
	_tex_last = tex_mb
	_tex_max = maxf(_tex_max, tex_mb)
	_video_last = video_mb
	_video_max = maxf(_video_max, video_mb)

	_phase_draw_sum += float(draws)
	_phase_draw_max = maxi(_phase_draw_max, draws)
	_phase_prims_sum += float(prims)
	_phase_prims_max = maxi(_phase_prims_max, prims)
	_phase_render_objects_max = maxi(_phase_render_objects_max, render_objects)
	_phase_objects_max = maxi(_phase_objects_max, objects)
	_phase_tex_max = maxf(_phase_tex_max, tex_mb)
	_phase_video_max = maxf(_phase_video_max, video_mb)


func _track_ai(dt: float) -> void:
	if _scene == null or not is_instance_valid(_scene):
		_watchers_active = false
		return
	var watcher: FMWatcher = _scene.watcher
	if watcher == null or not is_instance_valid(watcher):
		_watchers_active = false
	else:
		if not watcher.is_physics_processing():
			_watchers_active = false
		var step := _watcher_prev.distance_to(watcher.global_position)
		if step < 3.0:
			_watcher_path += step
		_watcher_prev = watcher.global_position
		_watcher_states[int(watcher.state)] = true
	var security: FMWatcher = _scene.security_watcher
	if security == null or not is_instance_valid(security):
		_watchers_active = false
	else:
		if not security.is_physics_processing():
			_watchers_active = false
		var security_step := _security_prev.distance_to(security.global_position)
		if security_step < 3.0:
			_security_path += security_step
		_security_prev = security.global_position
		_security_states[int(security.state)] = true
	if int(_scene.state) == 1:
		_captures += 1
		# Una captura cambiaría el estado de partida; detener la medida.
		_running = false


func _sample(t: float) -> void:
	var now := Time.get_ticks_usec()
	var sample_seconds := float(now - _sample_start_usec) / 1000000.0
	var fps_1s := float(_sample_frames) / maxf(sample_seconds, 0.001)
	var process_ms := Performance.get_monitor(Performance.TIME_PROCESS) * 1000.0
	var physics_ms := Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS) * 1000.0
	var phase_id := ""
	if _phase_index >= 0 and _phase_index < _phases.size():
		phase_id = str(_phases[_phase_index]["id"])
	print("FM_L1V06_PERF_SAMPLE t=%.1f phase=%s fps_1s=%.1f draws=%d prims=%d render_objects=%d objects=%d tex_mb=%.1f video_mb=%.1f process_ms=%.2f physics_ms=%.2f" % [
		t, phase_id, fps_1s, _draw_last, _prims_last,
		int(Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME)),
		_objects_last, _tex_last, _video_last, process_ms, physics_ms,
	])
	_sample_start_usec = now
	_sample_frames = 0


func _report() -> void:
	var seconds := float(Time.get_ticks_usec() - _start_usec) / 1000000.0
	var sorted := _frames.duplicate()
	sorted.sort()
	var max_dt := _percentile(sorted, 1.0)
	var fps_avg := float(_frames.size()) / maxf(seconds, 0.001)
	var fps_min := 1.0 / maxf(max_dt, 0.001)
	var fps_p1 := 1.0 / maxf(_percentile(sorted, 0.99), 0.001)
	var over_16 := 0
	var over_33 := 0
	for dt in _frames:
		if dt > 0.0166667:
			over_16 += 1
		if dt > 0.0333333:
			over_33 += 1
	_static_mb = Performance.get_monitor(Performance.MEMORY_STATIC) / (1024.0 * 1024.0)

	print("FM_L1V06_PERF_RESULT label=%s fps_avg=%.1f fps_min=%.1f fps_p1=%.1f frames=%d seconds=%.2f frame_ms_avg=%.2f p50=%.2f p95=%.2f p99=%.2f max=%.2f over_16_7ms=%d over_33_3ms=%d" % [
		_label, fps_avg, fps_min, fps_p1, _frames.size(), seconds,
		_average_ms(_frames), _percentile(sorted, 0.50) * 1000.0,
		_percentile(sorted, 0.95) * 1000.0, _percentile(sorted, 0.99) * 1000.0,
		max_dt * 1000.0, over_16, over_33,
	])
	print("FM_L1V06_PERF_RENDER draws_last=%d draws_avg=%.1f draws_max=%d prims_last=%d prims_avg=%.1f prims_max=%d render_objects_max=%d objects_last=%d objects_max=%d tex_mb_last=%.1f tex_mb_max=%.1f video_mb_last=%.1f video_mb_max=%.1f static_mb=%.1f nodes=%d resources=%d orphans=%d" % [
		_draw_last, _draw_sum / maxf(float(_frames.size()), 1.0), _draw_max,
		_prims_last, _prims_sum / maxf(float(_frames.size()), 1.0), _prims_max,
		_render_objects_max, _objects_last, _objects_max, _tex_last, _tex_max,
		_video_last, _video_max, _static_mb,
		int(Performance.get_monitor(Performance.OBJECT_NODE_COUNT)),
		int(Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT)),
		int(Performance.get_monitor(Performance.OBJECT_ORPHAN_NODE_COUNT)),
	])
	_print_ai()
	_print_gates()
	_print_worst_frames()
	_print_vram("FM_L1V06_PERF_VRAM_END", _vram_now())

	var avg_60 := fps_avg >= 60.0
	var p1_60 := fps_p1 >= 60.0
	var p1_30 := fps_p1 >= 30.0
	print("FM_L1V06_PERF_VERDICT label=%s avg_ge_60=%s p1_ge_60=%s p1_ge_30=%s stable_60=%s stable_30=%s" % [
		_label, str(avg_60), str(p1_60), str(p1_30),
		str(avg_60 and p1_60), str(avg_60 and p1_30),
	])
	var measured := _frames.size() > 0 and seconds >= _duration_s * 0.9
	var ok := measured and _captures == 0 and _watchers_active and _vsync_ok
	if ok:
		print("FM_L1V06_PERF: PASS label=%s frames=%d seconds=%.2f" % [_label, _frames.size(), seconds])
	else:
		print("FM_L1V06_PERF: FAIL label=%s measured=%s captures=%d watchers_active=%s vsync_ok=%s" % [
			_label, str(measured), _captures, str(_watchers_active), str(_vsync_ok),
		])


func _print_ai() -> void:
	var watcher: FMWatcher = _scene.watcher
	var security: FMWatcher = _scene.security_watcher
	print("FM_L1V06_PERF_AI main_state=%s main_states=%s main_path_m=%.2f main_observed=%s main_physics=%s security_state=%s security_states=%s security_path_m=%.2f security_observed=%s security_physics=%s captures=%d active=%s session_state=%d" % [
		_state_name(int(watcher.state)) if watcher != null else "missing",
		_states_list(_watcher_states), _watcher_path,
		str(watcher.observed) if watcher != null else "?",
		str(watcher.is_physics_processing()) if watcher != null else "?",
		_state_name(int(security.state)) if security != null else "missing",
		_states_list(_security_states), _security_path,
		str(security.observed) if security != null else "?",
		str(security.is_physics_processing()) if security != null else "?",
		_captures, str(_watchers_active), int(_scene.state),
	])


func _print_gates() -> void:
	var parts: Array[String] = []
	for gate in _scene.level_gates:
		if gate == null or not is_instance_valid(gate):
			continue
		parts.append("%s:open=%s,moving=%s,lift=%.2f,col=%d" % [
			gate.gate_id, str(gate.is_open), str(gate.is_moving),
			gate.get_shutter_lift(), gate.get_enabled_collision_count(),
		])
	print("FM_L1V06_PERF_GATES gates=[%s] door_noise=%d open_at=%.2f close_at=%.2f z10_noise_radius=%.1f" % [
		", ".join(parts), _scene.get_door_noise_count() - _gate_noise_start,
		_gate_open_time, _gate_close_time,
		_scene.get_gate("Z10").noise_radius if _scene.get_gate("Z10") != null else -1.0,
	])


func _print_worst_frames() -> void:
	# Cinco frames más lentos, con su fase, para identificar hitches puntuales.
	var worst: Array[Dictionary] = []
	for i in range(_frames.size()):
		var dt := _frames[i]
		if worst.size() < 5:
			worst.append({"i": i, "dt": dt})
			worst.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
				return float(a["dt"]) < float(b["dt"])
			)
		elif dt > float(worst[0]["dt"]):
			worst[0] = {"i": i, "dt": dt}
			worst.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
				return float(a["dt"]) < float(b["dt"])
			)
	var parts: Array[String] = []
	for entry in worst:
		var index: int = entry["i"]
		var phase_id := ""
		if index >= 0 and index < _frame_phase.size() and _frame_phase[index] >= 0:
			phase_id = str(_phases[_frame_phase[index]]["id"])
		parts.append("%s:%.1fms" % [phase_id, float(entry["dt"]) * 1000.0])
	print("FM_L1V06_PERF_WORST_FRAMES %s" % " ".join(parts))


func _print_vram(tag: String, values: Vector2) -> void:
	print("%s tex_mb=%.1f video_mb=%.1f" % [tag, values.x, values.y])


func _vram_now() -> Vector2:
	return Vector2(
		Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED) / (1024.0 * 1024.0),
		Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED) / (1024.0 * 1024.0)
	)


func _save_capture(index: int) -> void:
	var dir := _capture_dir
	if DirAccess.make_dir_recursive_absolute(dir) != OK:
		print("FM_L1V06_PERF_CAPTURE_FAIL dir=%s" % dir)
		return
	var image := get_viewport().get_texture().get_image()
	var path := "%s/%s_%s.png" % [dir, _label, str(_phases[index]["id"])]
	var error := image.save_png(path)
	print("FM_L1V06_PERF_CAPTURE path=%s error=%d size=%dx%d" % [
		path, error, image.get_width(), image.get_height(),
	])


func _average_ms(values: PackedFloat64Array) -> float:
	if values.is_empty():
		return 0.0
	var total := 0.0
	for value in values:
		total += value
	return total / float(values.size()) * 1000.0


func _percentile(sorted_values: PackedFloat64Array, p: float) -> float:
	if sorted_values.is_empty():
		return 0.0
	var index := clampi(int(float(sorted_values.size() - 1) * p), 0, sorted_values.size() - 1)
	return sorted_values[index]


func _state_name(value: int) -> String:
	var names: Array[String] = ["DORMANT", "PATROL", "INVESTIGATE", "CHASE", "SEARCH"]
	return names[value] if value >= 0 and value < names.size() else "UNKNOWN"


func _states_list(states: Dictionary) -> String:
	var names: Array[String] = []
	for key in states:
		names.append(_state_name(int(key)))
	names.sort()
	return ",".join(names)


func _cleanup() -> void:
	_running = false
	for action in ["move_up", "move_down", "move_left", "move_right", "sprint", "crouch", "interact", "drop", "flashlight"]:
		Input.action_release(action)
	await get_tree().create_timer(0.8).timeout
	if _scene != null and is_instance_valid(_scene):
		_scene.free()
	await get_tree().process_frame
	await get_tree().process_frame
	get_tree().quit(0)


func _fail(message: String) -> void:
	print("FM_L1V06_PERF: FAIL %s" % message)
	get_tree().quit(1)
