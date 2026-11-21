extends Node

## Rendimiento con la IA activa y movimiento real del jugador.
##
## Escena de prueba en ventana, 1280x720, VSync desactivado. Recorre Z10
## durante ~10 s con el Vigilante en su patrulla normal (sin suspender,
## vision_distance=18) y mide:
##   - FPS medio, minimo por frame y percentil 1 %.
##   - Draw calls, primitivas, objetos y memoria de texturas/video.
##
## No es una partida completa ni representa el rendimiento del juego final:
## solo Z10, un jugador, un Vigilante y la ruta corta de banco de pruebas.
##
## godot --path . tests/fm_perf_ai.tscn

const SCENE := preload("res://scenes/fm/fm_vslice_z10.tscn")
const DURATION_S := 10.0
const SAMPLE_INTERVAL_S := 1.0

var scene: Node
var _frames: int = 0
var _frame_times: Array[float] = []
var _samples: Array[Dictionary] = []
var _start_usec: int = 0
var _last_frame_usec: int = 0
var _next_sample_s: float = 0.0
var _elapsed_s: float = 0.0
var _route_index: int = 0
var _player_start := Vector3.ZERO
var _player_max_step := 0.0
var _player_distance := 0.0
var _last_player_position := Vector3.ZERO
var _watcher_prev := Vector3.ZERO
var _watcher_distance := 0.0
var _watcher_states := {}
var _ai_was_active := true
var _captures := 0
var _vsync_ok := false
var _running := true


func _ready() -> void:
	DisplayServer.window_set_size(Vector2i(1280, 720))
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = 0
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE

	if DisplayServer.get_name() == "headless":
		print("FM_PERF_AI: SKIP (requiere ventana; headless no mide GPU ni draw calls)")
		get_tree().quit(0)
		return

	scene = SCENE.instantiate()
	add_child(scene)
	var guard := 0
	while not scene.level_ready and guard < 600:
		await get_tree().process_frame
		guard += 1
	await get_tree().create_timer(2.5).timeout

	# IA normal durante toda la medida: sin suspension, sin vision reducida.
	scene.reception_watcher_enabled = true
	scene.watcher.set_physics_process(true)
	scene.watcher.vision_distance = 18.0
	scene.player.flashlight_on = true
	scene.player.battery = 100.0
	scene.player.rotation.y = -PI * 0.5
	_vsync_ok = DisplayServer.window_get_vsync_mode() == DisplayServer.VSYNC_DISABLED

	_player_start = scene.player.global_position
	_last_player_position = _player_start
	_watcher_prev = scene.watcher.global_position
	_start_usec = Time.get_ticks_usec()
	_last_frame_usec = _start_usec
	_next_sample_s = SAMPLE_INTERVAL_S
	_route_index = 0

	print("FM_PERF_AI_START scene=fm_vslice_z10.tscn window=%dx%d viewport=%dx%d vsync=%s max_fps=%d duration=%.1f" % [
		DisplayServer.window_get_size().x, DisplayServer.window_get_size().y,
		get_viewport().get_visible_rect().size.x, get_viewport().get_visible_rect().size.y,
		"disabled" if _vsync_ok else str(DisplayServer.window_get_vsync_mode()), Engine.max_fps, DURATION_S,
	])
	print("FM_PERF_AI_AI physics=%s suspended=%s vision=%.1f patrol_points=%d" % [
		str(scene.watcher.is_physics_processing()), str(scene.is_watcher_suspended()),
		scene.watcher.vision_distance, scene.watcher.patrol_points.size(),
	])

	while _running:
		var now := Time.get_ticks_usec()
		var dt := float(now - _last_frame_usec) / 1000000.0
		_last_frame_usec = now
		if dt > 0.0:
			_frame_times.append(dt)
			_frames += 1
		_elapsed_s = float(now - _start_usec) / 1000000.0

		_step_route()
		_track_ai()

		if _elapsed_s >= _next_sample_s:
			_sample_monitors(_elapsed_s)
			_next_sample_s += SAMPLE_INTERVAL_S

		if _elapsed_s >= DURATION_S:
			_running = false
		await get_tree().process_frame

	_release_move()
	# Muestra final tras soltar las teclas.
	_sample_monitors(_elapsed_s)
	_report()
	scene.player.set_physics_process(false)
	scene.watcher.set_physics_process(false)
	get_tree().quit(0 if _captures == 0 and _ai_was_active else 1)


func _step_route() -> void:
	var step: float = _last_player_position.distance_to(scene.player.global_position)
	_player_max_step = maxf(_player_max_step, step)
	_player_distance += step
	_last_player_position = scene.player.global_position
	if int(scene.state) != 0:
		return
	var route: Array[Vector3] = [
		Vector3(42.2, 0.12, -22.0),
		Vector3(46.0, 0.12, -22.0),
		Vector3(46.0, 0.12, -21.4),
		Vector3(42.2, 0.12, -21.4),
	]
	var target: Vector3 = route[_route_index % route.size()]
	var offset: Vector3 = target - scene.player.global_position
	offset.y = 0.0
	if offset.length() < 0.8:
		_route_index = (_route_index + 1) % route.size()
		return
	var watch := _should_watch_watcher()
	var yaw := _yaw_to_watcher() if watch else atan2(-offset.x, -offset.z)
	scene.player.rotation.y = yaw
	scene.player.camera.rotation.x = 0.0
	scene.player.camera.rotation.y = 0.0
	var local := Basis(Vector3.UP, yaw).inverse() * offset.normalized()
	_release_move()
	if local.x > 0.20:
		Input.action_press("move_right")
	elif local.x < -0.20:
		Input.action_press("move_left")
	if local.z < -0.20:
		Input.action_press("move_up")
	elif local.z > 0.20:
		Input.action_press("move_down")
	if not Input.is_action_pressed("move_up") and not Input.is_action_pressed("move_down") \
			and not Input.is_action_pressed("move_left") and not Input.is_action_pressed("move_right"):
		Input.action_press("move_up")


func _track_ai() -> void:
	if scene.watcher == null or not is_instance_valid(scene.watcher):
		_ai_was_active = false
		return
	if scene.is_watcher_suspended() or not scene.watcher.is_physics_processing():
		_ai_was_active = false
	var step: float = _watcher_prev.distance_to(scene.watcher.global_position)
	if step < 5.0:
		_watcher_distance += step
	_watcher_prev = scene.watcher.global_position
	var state: int = int(scene.watcher.state)
	_watcher_states[state] = true
	if int(scene.state) == 2:
		_captures += 1


func _should_watch_watcher() -> bool:
	var distance: float = scene.player.global_position.distance_to(scene.watcher.global_position)
	if distance > 15.5:
		return false
	var query := PhysicsRayQueryParameters3D.create(
		scene.player.camera.global_position,
		scene.watcher.global_position + Vector3(0.0, 1.35, 0.0)
	)
	query.collision_mask = 1
	query.exclude = [scene.player.get_rid()]
	var hit: Dictionary = scene.player.get_world_3d().direct_space_state.intersect_ray(query)
	return hit.is_empty()


func _yaw_to_watcher() -> float:
	var offset: Vector3 = scene.watcher.global_position - scene.player.global_position
	offset.y = 0.0
	return atan2(-offset.x, -offset.z)


func _release_move() -> void:
	for action in ["move_up", "move_down", "move_left", "move_right"]:
		Input.action_release(action)


func _sample_monitors(time_s: float) -> void:
	var sample := {
		"t": time_s,
		"draws": int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)),
		"prims": int(Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)),
		"objects": int(Performance.get_monitor(Performance.OBJECT_COUNT)),
		"tex_mb": Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED) / (1024.0 * 1024.0),
		"video_mb": Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED) / (1024.0 * 1024.0),
	}
	_samples.append(sample)
	print("FM_PERF_AI_SAMPLE t=%.1f draws=%d prims=%d objects=%d tex_mb=%.1f video_mb=%.1f" % [
		time_s, sample["draws"], sample["prims"], sample["objects"], sample["tex_mb"], sample["video_mb"],
	])


func _report() -> void:
	var total_time := float(Time.get_ticks_usec() - _start_usec) / 1000000.0
	var fps_avg := float(_frames) / maxf(total_time, 0.001)
	var max_dt := 0.0
	for dt in _frame_times:
		max_dt = maxf(max_dt, dt)
	var fps_min := 1.0 / maxf(max_dt, 0.001)
	var sorted := _frame_times.duplicate()
	sorted.sort()
	var p99_index: int = clampi(int(float(sorted.size()) * 0.99), 0, maxi(0, sorted.size() - 1))
	var p99_dt: float = sorted[p99_index] if not sorted.is_empty() else max_dt
	var fps_p1: float = 1.0 / maxf(p99_dt, 0.001)

	var draws_max := 0
	var objects_max := 0
	var tex_max := 0.0
	var video_max := 0.0
	var last: Dictionary = _samples[-1] if not _samples.is_empty() else {}
	for sample in _samples:
		draws_max = maxi(draws_max, int(sample["draws"]))
		objects_max = maxi(objects_max, int(sample["objects"]))
		tex_max = maxf(tex_max, float(sample["tex_mb"]))
		video_max = maxf(video_max, float(sample["video_mb"]))

	var player_moved: float = _player_start.distance_to(scene.player.global_position)
	print("FM_PERF_AI_RESULT fps_avg=%.1f fps_min=%.1f fps_p1=%.1f frames=%d time=%.2f" % [
		fps_avg, fps_min, fps_p1, _frames, total_time,
	])
	print("FM_PERF_AI_RENDER last_draws=%d max_draws=%d last_objects=%d max_objects=%d last_tex_mb=%.1f max_tex_mb=%.1f last_video_mb=%.1f max_video_mb=%.1f" % [
		int(last.get("draws", 0)), draws_max, int(last.get("objects", 0)), objects_max,
		float(last.get("tex_mb", 0.0)), tex_max,
		float(last.get("video_mb", 0.0)), video_max,
	])
	print("FM_PERF_AI_AI active=%s captures=%d states=%s patrol_distance=%.2f vision=%.1f physics=%s vsync_ok=%s" % [
		str(_ai_was_active), _captures, str(_watcher_states), _watcher_distance,
		scene.watcher.vision_distance, str(scene.watcher.is_physics_processing()), str(_vsync_ok),
	])
	print("FM_PERF_AI_MOVEMENT player_net=%.2f player_path=%.2f max_step=%.3f route=%d state=%d" % [
		player_moved, _player_distance, _player_max_step, _route_index, int(scene.state),
	])
	if _ai_was_active and _captures == 0 and _vsync_ok and _player_distance > 0.5:
		print("FM_PERF_AI: PASS")
	else:
		print("FM_PERF_AI: FAIL ai_active=%s captures=%d vsync_ok=%s player_moved=%.2f" % [
			str(_ai_was_active), _captures, str(_vsync_ok), player_moved,
		])
