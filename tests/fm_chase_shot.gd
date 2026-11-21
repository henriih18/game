extends Node

## Capturas de la persecución con navmesh. Ejecutar en ventana:
## godot --path . tests/fm_chase_shot.tscn

var scene: Node
var _spectator: Camera3D

func _ready() -> void:
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

	# Transición real con el núcleo en manos.
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

	# Colocar al jugador en la extracción y al Vigilante 8 m al norte.
	# El jugador mira al sur (a la compuerta), no al Vigilante: si lo mirara,
	# lo congelaría y la captura no mostraría la persecución.
	scene.player.global_position = Vector3(-94.0, 0.12, 36.0)
	scene.player.rotation.y = PI
	scene.player.camera.rotation.x = -0.05
	scene.player.camera.rotation.y = 0.0
	scene.player.camera.position = Vector3(0.0, 1.62, 0.0)
	scene.player.velocity = Vector3.ZERO
	scene.player.flashlight_on = true
	scene.player.battery = 100.0

	# Cámara espectadora lateral para ver al Vigilante acercarse; la cámara
	# del jugador no puede mirarlo sin congelarlo.
	_spectator = Camera3D.new()
	_spectator.name = "ChaseObserver"
	_spectator.position = Vector3(-87.0, 3.0, 36.0)
	scene.add_child(_spectator)
	_spectator.look_at(Vector3(-94.5, 1.0, 30.0), Vector3.UP)
	_spectator.fov = 70.0
	_spectator.current = true

	var observer_light := SpotLight3D.new()
	observer_light.name = "ChaseObserverLight"
	observer_light.light_color = Color(1.0, 0.93, 0.82)
	observer_light.light_energy = 4.0
	observer_light.spot_range = 18.0
	observer_light.spot_angle = 32.0
	observer_light.shadow_enabled = true
	_spectator.add_child(observer_light)

	var watcher_route: Array[Vector3] = [Vector3(-94.0, 0.12, 28.0)]
	scene.watcher.activate_in_sector(
		Vector3(-94.0, 0.12, 28.0),
		watcher_route,
		PI
	)
	await get_tree().physics_frame
	await get_tree().physics_frame
	print("SHOT_PRE state=%d area=%s phys=%s wstate=%d watcher=%s" % [
		int(scene.state), scene.current_area, str(scene.watcher.is_physics_processing()),
		int(scene.watcher.state), str(scene.watcher.global_position)
	])

	await get_tree().create_timer(0.20).timeout
	await _shot("docs/fm_nav_chase_01_alerta.png")
	await get_tree().create_timer(0.55).timeout
	await _shot("docs/fm_nav_chase_02_aproximacion.png")
	await get_tree().create_timer(0.55).timeout
	await _shot("docs/fm_nav_chase_03_cercano.png")

	print("FM_NAV_CHASE_SHOTS_DONE")
	get_tree().quit()

func _shot(path: String) -> void:
	_spectator.look_at(scene.watcher.global_position + Vector3(0.0, 1.2, 0.0), Vector3.UP)
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	var err := image.save_png(path)
	print("SHOT %s %dx%d err=%d watcher=%s" % [
		path,
		image.get_width(),
		image.get_height(),
		err,
		str(scene.watcher.global_position),
	])
