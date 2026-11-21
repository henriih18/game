extends Node

## Persecución con navmesh: el Vigilante debe rodear el cola de seguridad de recepción
## de Recepción para alcanzar al jugador, que mira al sur para no congelarlo.
## Ejecutar en ventana:
## godot --path . tests/fm_queue_chase.tscn

var scene: Node
var _spectator: Camera3D
var _passes := 0
var _fails := 0
var _start := Vector3.ZERO
var _max_lateral := 0.0
var _min_distance := 999.0
var _saw_chase := false
var _caught := false
var _capture := true

func _ready() -> void:
	_capture = DisplayServer.get_name() != "headless"
	DisplayServer.window_set_size(Vector2i(1280, 720))
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = 0
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE

	var packed: PackedScene = load("res://scenes/fm/fm_vslice_z10.tscn")
	scene = packed.instantiate()
	add_child(scene)
	var guard := 0
	while not scene.level_ready and guard < 600:
		await get_tree().process_frame
		guard += 1
	await get_tree().create_timer(1.0).timeout

	# Entrar en Recepción con el núcleo, usando la transición real.
	scene.watcher.set_physics_process(false)
	scene.reception_watcher_enabled = true
	scene.player.global_position = Vector3(68.0, 0.12, -21.0)
	scene.player.rotation.y = PI * 0.5
	var core: FMCarryItem = scene.carry_items[0]
	core.carried_by = scene.player
	core.freeze = true
	scene.player.carried_item = core
	scene.transition_door.interact(scene.player)
	await get_tree().create_timer(2.0).timeout

	# El jugador mira al norte; el Vigilante llega desde el sur. La columna
	# central queda entre ambos.
	scene.player.global_position = Vector3(-87.5, 0.12, 15.0)
	scene.player.rotation.y = PI
	scene.player.camera.rotation.x = -0.05
	scene.player.camera.rotation.y = 0.0
	scene.player.camera.position = Vector3(0.0, 1.62, 0.0)
	scene.player.velocity = Vector3.ZERO
	scene.player.flashlight_on = true
	scene.player.battery = 100.0

	_spectator = Camera3D.new()
	_spectator.name = "QueueChaseObserver"
	_spectator.position = Vector3(-97.0, 3.5, 12.0)
	scene.add_child(_spectator)
	_spectator.look_at(Vector3(-87.5, 1.0, 12.0), Vector3.UP)
	_spectator.fov = 72.0
	_spectator.current = true

	var light := SpotLight3D.new()
	light.name = "ChaseObserverLight"
	light.light_energy = 5.0
	light.spot_range = 22.0
	light.spot_angle = 38.0
	light.shadow_enabled = true
	light.light_color = Color(1.0, 0.88, 0.70)
	_spectator.add_child(light)

	var watcher_route: Array[Vector3] = [Vector3(-87.5, 0.12, 7.5)]
	scene.watcher.activate_in_sector(
		Vector3(-87.5, 0.12, 7.5),
		watcher_route,
		PI
	)
	_start = scene.watcher.global_position

	# El ruido inicia la investigación; la columna obliga a rodearla antes de
	# tener línea de visión con el jugador.
	scene.watcher.hear_noise(scene.player.global_position, 30.0)
	await get_tree().physics_frame
	await get_tree().physics_frame
	print("QUEUE_NAV_START state=%d area=%s phys=%s watcher=%s player=%s" % [
		int(scene.state), scene.current_area, str(scene.watcher.is_physics_processing()),
		str(scene.watcher.global_position), str(scene.player.global_position)
	])

	if _capture:
		await get_tree().create_timer(0.3).timeout
		_sample_watcher()
		await _shot("docs/fm_queue_chase_01.png")
		await get_tree().create_timer(0.8).timeout
		_sample_watcher()
		await _shot("docs/fm_queue_chase_02.png")
		await get_tree().create_timer(0.9).timeout
		_sample_watcher()
		await _shot("docs/fm_queue_chase_03.png")
		await get_tree().create_timer(0.9).timeout
		_sample_watcher()
		await _shot("docs/fm_queue_chase_04.png")

	var elapsed := 2.9
	while elapsed < 14.0 and not _caught:
		await _wait(0.2)
		elapsed += 0.2
		var watcher_pos: Vector3 = scene.watcher.global_position
		var distance: float = watcher_pos.distance_to(scene.player.global_position)
		_min_distance = minf(_min_distance, distance)
		if watcher_pos.z > 9.5 and watcher_pos.z < 14.0:
			_max_lateral = maxf(_max_lateral, absf(watcher_pos.x - (-87.5)))
		if int(scene.watcher.state) == int(FMWatcher.State.CHASE):
			_saw_chase = true
		if int(scene.state) == 2 or distance <= scene.watcher.catch_distance + 0.35:
			_caught = true

	print("QUEUE_NAV_RESULT moved=%.2f lateral=%.2f min_dist=%.2f chase=%s caught=%s state=%d" % [
		_start.distance_to(scene.watcher.global_position), _max_lateral, _min_distance,
		str(_saw_chase), str(_caught), int(scene.state)
	])
	_check("watcher_activated", scene.watcher.is_physics_processing())
	_check("player_not_observing", not scene.player.is_observing(scene.watcher))
	_check("watcher_moved", _start.distance_to(scene.watcher.global_position) > 4.0)
	_check("watcher_goes_around_queue", _max_lateral > 0.40)
	_check("watcher_reached_chase", _saw_chase)
	_check("watcher_caught_player", _caught)
	_check("long_chase_shots", not _capture
		or (FileAccess.file_exists("docs/fm_queue_chase_01.png")
		and FileAccess.file_exists("docs/fm_queue_chase_04.png")))
	_finish()

func _sample_watcher() -> void:
	var watcher_pos: Vector3 = scene.watcher.global_position
	var distance: float = watcher_pos.distance_to(scene.player.global_position)
	_min_distance = minf(_min_distance, distance)
	if watcher_pos.z > 9.5 and watcher_pos.z < 14.0:
		_max_lateral = maxf(_max_lateral, absf(watcher_pos.x - (-87.5)))
	if int(scene.watcher.state) == int(FMWatcher.State.CHASE):
		_saw_chase = true
	if int(scene.state) == 2 or distance <= scene.watcher.catch_distance + 0.35:
		_caught = true


func _shot(path: String) -> void:
	_sample_watcher()
	_spectator.look_at(scene.watcher.global_position + Vector3(0.0, 1.2, 0.0), Vector3.UP)
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	var err := image.save_png(path)
	print("QUEUE_NAV_SHOT %s %dx%d err=%d watcher=%s" % [
		path, image.get_width(), image.get_height(), err, str(scene.watcher.global_position)
	])

func _wait(seconds: float) -> void:
	await get_tree().create_timer(seconds).timeout

func _check(name: String, condition: bool) -> void:
	if condition:
		_passes += 1
		print("QUEUE_NAV_TEST: %s OK" % name)
	else:
		_fails += 1
		print("QUEUE_NAV_TEST: %s FAIL" % name)

func _finish() -> void:
	if _fails == 0:
		print("FM_QUEUE_CHASE: PASS (%d PASS / 0 FAIL)" % _passes)
		get_tree().quit(0)
	else:
		print("FM_QUEUE_CHASE: FAIL (%d PASS / %d FAIL)" % [_passes, _fails])
		get_tree().quit(1)
