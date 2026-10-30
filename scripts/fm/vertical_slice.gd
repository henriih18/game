extends Node3D

## Vertical slice offline de FRECUENCIA MUERTA.
## Un solo jugador, un corredor, un laboratorio, un núcleo físico,
## un escondite, El Vigilante y extracción. Sin armas.

enum State { PLAYING, WON, LOST }
enum NetMode { OFFLINE, HOST, CLIENT }

const PLAYER_SCENE := preload("res://scenes/fm/fm_player.tscn")
const WATCHER_SCENE := preload("res://scenes/fm/fm_watcher.tscn")
const ITEM_SCENE := preload("res://scenes/fm/carry_item.tscn")
const HIDING_SCENE := preload("res://scenes/fm/hiding_spot.tscn")
const EXTRACTION_SCENE := preload("res://scenes/fm/extraction.tscn")
const DOOR_SCENE := preload("res://scenes/fm/security_door.tscn")
const BATTERY_SCENE := preload("res://scenes/fm/battery.tscn")
const TRAP_SCENE := preload("res://scenes/fm/noise_trap.tscn")

const MAT_CONCRETE := preload("res://assets/art/fm/concrete_wall.tres")
const MAT_METAL := preload("res://assets/art/fm/metal_panel.tres")
const MAT_FLOOR := preload("res://assets/art/fm/floor_wet.tres")
const MAT_RUST := preload("res://assets/art/fm/rust.tres")
const MAT_HAZARD := preload("res://assets/art/fm/hazard.tres")
const MAT_CYAN := preload("res://assets/art/fm/emissive_cyan.tres")
const MAT_RED := preload("res://assets/art/fm/emissive_red.tres")
const MAT_GREEN := preload("res://assets/art/fm/emissive_green.tres")
const MAT_ORANGE := preload("res://assets/art/fm/emissive_orange.tres")
const MAT_DARK := preload("res://assets/art/fm/dark_metal.tres")
const MAT_RUBBER := preload("res://assets/art/fm/rubber.tres")
const MAT_GLASS := preload("res://assets/art/fm/glass.tres")
const MAT_GOO := preload("res://assets/art/fm/goo.tres")
const MAT_SCREEN := preload("res://assets/art/fm/screen.tres")
const MAT_YELLOW := preload("res://assets/art/fm/warning_yellow.tres")

const SPAWN := Vector3(0.0, 0.1, 9.0)
const WATCHER_SPAWN := Vector3(0.0, 0.1, -3.5)
const ARTIFACT_SPAWN := Vector3(-5.9, 1.3, 4.4)
const EXTRACTION_SPAWN := Vector3(0.0, 0.0, -12.0)

var state: State = State.PLAYING
var player: FMPlayer
var watcher: FMWatcher
var artifact: FMCarryItem
var extraction: FMExtraction
var hud: FMHUD
var level: Node3D
var security_door: FMSecurityDoor
var batteries: Array[FMBattery] = []
var noise_trap: FMNoiseTrap
var ambience: AudioStreamPlayer3D

var net_mode: NetMode = NetMode.OFFLINE
var local_id := 1
var net: FMNet
var players: Dictionary = {}
var players_root: Node3D
var hiding_spots: Array[FMHidingSpot] = []
var battery_taken: Array[bool] = []

var _mats: Dictionary = {}
var _time := 0.0
var _stress := 0.0
var _ending := false
var _watcher_was_observed := false
var _last_hide_index := -1

func _ready() -> void:
	_detect_net_mode()
	_prepare_materials()
	_build_environment()
	level = Node3D.new()
	level.name = "Level"
	add_child(level)
	_build_rooms()
	_build_lights()
	_build_props()
	_build_hiding_spots()
	_build_security_door()
	_build_batteries()
	_build_noise_trap()
	_build_extraction()
	_build_artifact()
	players_root = Node3D.new()
	players_root.name = "Players"
	add_child(players_root)
	_build_player()
	_build_watcher()
	if OS.get_cmdline_user_args().has("--nettest") and watcher != null:
		watcher.set_physics_process(false)
	_build_hud()
	_build_network()
	_build_ambience()
	Audio.play_music("heist")
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _detect_net_mode() -> void:
	var peer := multiplayer.multiplayer_peer
	if peer is ENetMultiplayerPeer:
		net_mode = NetMode.HOST if multiplayer.is_server() else NetMode.CLIENT
	else:
		net_mode = NetMode.OFFLINE
	local_id = 1
	if net_mode == NetMode.CLIENT:
		local_id = maxi(2, multiplayer.get_unique_id())

func _build_network() -> void:
	if net_mode == NetMode.OFFLINE:
		return
	net = FMNet.new()
	net.name = "Network"
	add_child(net)
	net.setup(self)
	if net_mode == NetMode.CLIENT and watcher != null:
		# El cliente no simula la IA: recibe posición y estado del host.
		watcher.set_physics_process(false)

func place_local_player(spawn_position: Vector3, yaw: float) -> void:
	if player == null or not is_instance_valid(player):
		return
	player.global_position = spawn_position
	player.rotation.y = yaw
	player.velocity = Vector3.ZERO
	if player.has_method("reset_view"):
		player.reset_view(yaw)

func spawn_point_for(pid: int) -> Vector3:
	var offsets := [
		Vector3.ZERO,
		Vector3(2.2, 0.0, 1.0),
		Vector3(-2.2, 0.0, 1.0),
		Vector3(2.2, 0.0, 2.4),
	]
	var slot := 0 if pid == 1 else players.size()
	return SPAWN + offsets[slot % offsets.size()]

func spawn_remote(pid: int, spawn_position: Vector3, yaw: float) -> void:
	if pid == local_id or players.has(pid):
		return
	var remote := FMRemotePlayer.new()
	remote.name = "Player%d" % pid
	players_root.add_child(remote)
	remote.setup(pid, spawn_position, yaw)
	players[pid] = remote
	_refresh_watcher_targets()

func remove_remote(pid: int) -> void:
	var remote = players.get(pid)
	if remote == null:
		return
	var spot := _spot_for_occupant(remote)
	if spot != null:
		spot.release_player(remote)
	players.erase(pid)
	if is_instance_valid(remote):
		remote.queue_free()
	_refresh_watcher_targets()

func _refresh_watcher_targets() -> void:
	if watcher == null:
		return
	var list: Array[Node3D] = []
	for entry in players.values():
		if entry is Node3D and is_instance_valid(entry):
			list.append(entry)
	watcher.set_targets(list)

func get_battery_taken_flags() -> Array:
	var flags: Array = []
	for battery in batteries:
		flags.append(battery == null or not is_instance_valid(battery) or battery.taken)
	return flags

func receive_remote_noise(position: Vector3, radius: float) -> void:
	if watcher != null and is_instance_valid(watcher):
		watcher.hear_noise(position, radius)

func _prepare_materials() -> void:
	var concrete: StandardMaterial3D = MAT_CONCRETE.duplicate()
	concrete.uv1_scale = Vector3(4.0, 4.0, 1.0)
	concrete.albedo_color = Color(1.02, 1.08, 1.04, 1.0)
	_mats["concrete"] = concrete

	var metal: StandardMaterial3D = MAT_METAL.duplicate()
	metal.uv1_scale = Vector3(5.0, 5.0, 1.0)
	metal.albedo_color = Color(0.72, 0.82, 0.86, 1.0)
	_mats["metal"] = metal

	var ceiling: StandardMaterial3D = concrete.duplicate()
	ceiling.uv1_scale = Vector3(3.0, 2.0, 1.0)
	ceiling.albedo_color = Color(0.78, 0.86, 0.82, 1.0)
	ceiling.roughness = 0.95
	_mats["ceiling"] = ceiling

	var floor: StandardMaterial3D = MAT_FLOOR.duplicate()
	floor.uv1_scale = Vector3(3.5, 7.0, 1.0)
	floor.albedo_color = Color(1.45, 1.48, 1.42, 1.0)
	_mats["floor"] = floor

	var floor_lab: StandardMaterial3D = MAT_FLOOR.duplicate()
	floor_lab.uv1_scale = Vector3(5.0, 4.0, 1.0)
	floor_lab.albedo_color = Color(1.3, 1.36, 1.3, 1.0)
	_mats["floor_lab"] = floor_lab

	var metal_dirty: StandardMaterial3D = MAT_METAL.duplicate()
	metal_dirty.albedo_color = Color(0.68, 0.78, 0.82, 1.0)
	metal_dirty.roughness = 0.56
	metal_dirty.metallic = 0.38
	_mats["metal_dirty"] = metal_dirty

	_mats["rust"] = MAT_RUST
	_mats["hazard"] = MAT_HAZARD
	_mats["dark"] = MAT_DARK
	_mats["rubber"] = MAT_RUBBER
	_mats["yellow"] = MAT_YELLOW
	var screen_mat: StandardMaterial3D = MAT_SCREEN.duplicate()
	screen_mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	_mats["screen"] = screen_mat

	var cyan: StandardMaterial3D = MAT_CYAN.duplicate()
	cyan.emission_energy_multiplier = 0.9
	_mats["cyan"] = cyan
	var cyan_dim: StandardMaterial3D = MAT_CYAN.duplicate()
	cyan_dim.emission_energy_multiplier = 0.45
	_mats["cyan_dim"] = cyan_dim
	var red: StandardMaterial3D = MAT_RED.duplicate()
	red.emission_energy_multiplier = 0.85
	_mats["red"] = red
	var green: StandardMaterial3D = MAT_GREEN.duplicate()
	green.emission_energy_multiplier = 0.9
	_mats["green"] = green
	var orange: StandardMaterial3D = MAT_ORANGE.duplicate()
	orange.emission_energy_multiplier = 0.8
	_mats["orange"] = orange

	var glass: StandardMaterial3D = MAT_GLASS.duplicate()
	glass.cull_mode = BaseMaterial3D.CULL_DISABLED
	_mats["glass"] = glass
	var goo: StandardMaterial3D = MAT_GOO.duplicate()
	goo.transparency = BaseMaterial3D.TRANSPARENCY_DISABLED
	goo.albedo_color = Color(0.03, 0.4, 0.13, 1.0)
	goo.emission_energy_multiplier = 0.9
	_mats["goo"] = goo

func _mat(key: String) -> Material:
	return _mats[key]

func _build_environment() -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.002, 0.004, 0.006)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.14, 0.19, 0.2)
	env.ambient_light_energy = 0.48
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.tonemap_exposure = 1.08
	env.glow_enabled = true
	env.glow_intensity = 0.72
	env.glow_bloom = 0.12
	env.glow_hdr_threshold = 0.95
	env.fog_enabled = true
	env.fog_light_color = Color(0.04, 0.1, 0.1)
	env.fog_light_energy = 0.65
	env.fog_density = 0.008
	env.fog_aerial_perspective = 0.2
	env.volumetric_fog_enabled = true
	env.volumetric_fog_density = 0.012
	env.volumetric_fog_albedo = Color(0.34, 0.44, 0.43)
	env.volumetric_fog_anisotropy = 0.32
	env.volumetric_fog_length = 40.0
	env.volumetric_fog_ambient_inject = 0.22
	env.volumetric_fog_temporal_reprojection_enabled = true
	env.ssao_enabled = true
	env.ssao_radius = 1.1
	env.ssao_intensity = 1.35
	env.ssao_light_affect = 0.2
	env.ssr_enabled = true
	env.ssr_max_steps = 24
	env.adjustment_enabled = true
	env.adjustment_brightness = 1.0
	env.adjustment_contrast = 1.04
	env.adjustment_saturation = 0.96
	var world := WorldEnvironment.new()
	world.environment = env
	add_child(world)

func _build_rooms() -> void:
	# Suelo continuo del corredor.
	_box(level, Vector3(0, -0.1, 1.0), Vector3(5.4, 0.2, 24.0), "floor", true)
	# Muros del corredor.
	_box(level, Vector3(2.85, 2.0, 1.0), Vector3(0.3, 4.0, 24.0), "metal", true)
	_box(level, Vector3(-2.85, 2.0, -5.0), Vector3(0.3, 4.0, 10.0), "concrete", true)
	_box(level, Vector3(-2.85, 2.0, 8.75), Vector3(0.3, 4.0, 6.5), "concrete", true)
	_box(level, Vector3(-2.85, 3.65, 2.75), Vector3(0.3, 0.7, 5.5), "metal", true)
	_box(level, Vector3(0, 4.05, 1.0), Vector3(5.4, 0.2, 24.0), "ceiling", true)

	# Laboratorio a la izquierda, abierto al corredor entre z=0 y z=5.5.
	_box(level, Vector3(-6.25, -0.1, 2.5), Vector3(6.8, 0.2, 6.2), "floor_lab", true)
	_box(level, Vector3(-9.65, 2.0, 2.5), Vector3(0.3, 4.0, 6.2), "concrete", true)
	_box(level, Vector3(-6.25, 2.0, 5.65), Vector3(6.8, 4.0, 0.3), "metal", true)
	_box(level, Vector3(-6.25, 2.0, -0.65), Vector3(6.8, 4.0, 0.3), "metal", true)
	_box(level, Vector3(-6.25, 4.05, 2.5), Vector3(6.8, 0.2, 6.2), "ceiling", true)

	# Sala de extracción.
	_box(level, Vector3(0, -0.1, -12.0), Vector3(7.0, 0.2, 4.0), "floor", true)
	_box(level, Vector3(-3.5, 2.0, -12.0), Vector3(0.3, 4.0, 4.0), "metal", true)
	_box(level, Vector3(3.5, 2.0, -12.0), Vector3(0.3, 4.0, 4.0), "metal", true)
	_box(level, Vector3(0, 2.0, -14.0), Vector3(7.0, 4.0, 0.3), "concrete", true)
	_box(level, Vector3(-2.25, 2.0, -10.0), Vector3(2.5, 4.0, 0.3), "metal", true)
	_box(level, Vector3(2.25, 2.0, -10.0), Vector3(2.5, 4.0, 0.3), "metal", true)
	_box(level, Vector3(0, 3.7, -10.0), Vector3(2.0, 0.6, 0.3), "metal", true)
	_box(level, Vector3(0, 4.05, -11.0), Vector3(7.0, 0.2, 6.0), "ceiling", true)

	# Marco de puerta de seguridad (el hueco queda transitable).
	for x in [-1.42, 1.42]:
		_box(level, Vector3(x, 1.45, -9.9), Vector3(0.18, 2.9, 0.25), "dark", false)
	_box(level, Vector3(0, 2.95, -9.9), Vector3(3.02, 0.16, 0.25), "dark", false)
	_box(level, Vector3(0, 0.03, -9.85), Vector3(2.9, 0.02, 0.9), "hazard", false)
	_box(level, Vector3(0, 3.12, -9.9), Vector3(2.2, 0.05, 0.1), "red", false)
	_box(level, Vector3(0, 3.4, -9.9), Vector3(1.4, 0.06, 0.08), "cyan_dim", false)
	_label3d("SECTOR 04", Vector3(0, 3.26, -10.06), 28, Color(0.92, 0.82, 0.58), false)

	# Entrada del laboratorio: marco y umbral.
	for z in [0.0, 5.5]:
		_box(level, Vector3(-2.85, 1.95, z), Vector3(0.34, 3.9, 0.22), "dark", false)
	_box(level, Vector3(-2.85, 3.72, 2.75), Vector3(0.34, 0.18, 5.5), "dark", false)
	_box(level, Vector3(-2.7, 0.02, 2.75), Vector3(0.3, 0.03, 5.4), "hazard", false)

func _build_lights() -> void:
	# Luces del corredor.
	for z in [8.0, 3.0, -2.0, -7.0]:
		_fixture(Vector3(0, 3.92, z), false)
	# Laboratorio: luz fría cenital, verde del tanque y lámpara de trabajo.
	_fixture(Vector3(-6.2, 3.92, 3.6), true)
	_fixture(Vector3(-6.2, 3.92, 0.9), true)
	_omni(Vector3(-7.4, 1.6, 2.0), Color(0.12, 0.95, 0.42), 2.2, 6.5)
	_omni(Vector3(-5.9, 1.35, 4.4), Color(1.0, 0.6, 0.25), 0.9, 3.2)
	_omni(Vector3(-8.7, 2.6, 4.7), Color(0.34, 0.62, 1.0), 0.8, 4.0)
	_omni(Vector3(-7.5, 3.0, 1.2), Color(0.25, 0.55, 0.95), 0.9, 5.0)
	# Emergencia y extracción.
	_omni(Vector3(0, 2.6, -9.4), Color(1.0, 0.12, 0.08), 1.1, 4.5)
	_omni(Vector3(0, 2.2, -12.2), Color(0.1, 1.0, 0.4), 0.9, 5.0)
	_spot(Vector3(0, 3.6, -10.3), Vector3(0, 1.1, -12.0), Color(0.55, 0.9, 0.7), 2.4, 44.0, 8.0, true)
	_spot(Vector3(-3.2, 3.2, 2.5), Vector3(-7.4, 1.2, 2.0), Color(0.45, 0.7, 1.0), 2.2, 48.0, 9.0, true)

func _fixture(pos: Vector3, lab: bool) -> void:
	_box(level, pos, Vector3(1.55, 0.08, 0.24), "dark", false)
	_box(level, pos + Vector3(0, -0.06, 0), Vector3(1.36, 0.018, 0.1), "cyan" if not lab else "cyan_dim", false)
	_omni(pos + Vector3(0, -0.25, 0), Color(0.58, 0.78, 1.0), 1.35 if not lab else 1.1, 7.0)

func _build_props() -> void:
	# Tanque de contención del laboratorio.
	var tank_pos := Vector3(-7.4, 0.0, 2.0)
	_static_cylinder(tank_pos + Vector3(0, 1.4, 0), 1.06, 2.8, "glass")
	_cylinder_mesh(tank_pos + Vector3(0, 1.35, 0), 0.82, 2.2, "goo", false)
	_cylinder_mesh(tank_pos + Vector3(0, 0.2, 0), 1.15, 0.18, "dark", false)
	_cylinder_mesh(tank_pos + Vector3(0, 2.82, 0), 1.1, 0.14, "dark", false)
	_sphere_mesh(tank_pos + Vector3(0, 1.35, 0), 0.38, "dark", Vector3(1.5, 2.5, 1.1), false)
	_sphere_mesh(tank_pos + Vector3(0, 2.18, 0), 0.28, "dark", Vector3(1.0, 1.1, 0.9), false)
	for x in [-0.75, 0.0, 0.75]:
		_cylinder_mesh(tank_pos + Vector3(x, 1.35, 0), 0.035, 2.65, "metal", false)
	var ring := MeshInstance3D.new()
	var torus := TorusMesh.new()
	torus.inner_radius = 1.13
	torus.outer_radius = 1.26
	torus.rings = 28
	torus.ring_segments = 8
	ring.mesh = torus
	ring.material_override = _mat("cyan_dim")
	ring.position = tank_pos + Vector3(0, 2.9, 0)
	level.add_child(ring)

	# Escritorio del núcleo.
	_box(level, Vector3(-5.9, 0.86, 4.4), Vector3(2.1, 0.08, 0.9), "metal_dirty", true)
	for x in [-0.9, 0.9]:
		for z in [-0.3, 0.3]:
			_box(level, Vector3(-5.9 + x, 0.43, 4.4 + z), Vector3(0.07, 0.86, 0.07), "dark", true)
	_box(level, Vector3(-5.9, 1.0, 4.4), Vector3(0.7, 0.5, 0.12), "dark", false)
	_quad_mesh(Vector3(-5.9, 1.0, 4.47), Vector2(0.58, 0.34), "screen", Vector3(0, 0, 0), false)
	_label3d("NEXUS // NÚCLEO", Vector3(-5.9, 1.42, 4.4), 18, Color(0.45, 0.95, 0.8), true)

	# Camilla y estanterías.
	_box(level, Vector3(-4.9, 0.55, 0.9), Vector3(1.8, 0.1, 0.7), "metal_dirty", true)
	for x in [-0.75, 0.75]:
		_box(level, Vector3(-4.9 + x, 0.27, 0.9), Vector3(0.06, 0.55, 0.06), "dark", true)
	_box(level, Vector3(-8.8, 1.0, 4.75), Vector3(1.3, 2.0, 0.45), "metal_dirty", true)
	for y in [0.45, 0.95, 1.45]:
		_box(level, Vector3(-8.8, y, 4.55), Vector3(1.2, 0.03, 0.1), "dark", false)
	for i in 3:
		_cylinder_mesh(Vector3(-9.05 + i * 0.25, 2.1, 4.75), 0.07, 0.24, "glass", false)

	# Cajas, barriles y tuberías.
	_box(level, Vector3(-8.9, 0.42, 0.2), Vector3(0.75, 0.84, 0.75), "metal_dirty", true)
	_box(level, Vector3(-8.1, 0.32, 0.25), Vector3(0.6, 0.64, 0.6), "rust", true)
	_cylinder_mesh(Vector3(2.1, 0.5, 5.4), 0.34, 1.0, "rust", true)
	_cylinder_mesh(Vector3(1.5, 0.5, 5.7), 0.34, 1.0, "metal_dirty", true)
	for z in [-6.0, -1.0, 4.0]:
		_cylinder_mesh(Vector3(2.45, 2.9, z), 0.11, 20.0, "rust", false, Vector3(90, 0, 0))
	_box(level, Vector3(2.6, 0.45, -6.4), Vector3(0.7, 0.9, 0.7), "yellow", true)

	# Carteles y pantallas.
	_quad_mesh(Vector3(-2.67, 2.5, 1.2), Vector2(0.7, 0.42), "screen", Vector3(0, 90, 0), false)
	_label3d("BIO-LAB 04", Vector3(-9.46, 2.7, 3.8), 24, Color(0.48, 0.9, 0.78), true)
	_label3d("NEXUS // CONTENCIÓN", Vector3(-9.45, 2.4, 3.8), 11, Color(0.38, 0.62, 0.6), true, Vector3(0, 90, 0))
	_label3d("EXTRACCIÓN", Vector3(0, 2.6, -13.75), 26, Color(0.42, 1.0, 0.62), true, Vector3(0, 180, 0))

	# Polvo suspendido.
	_dust(Vector3(0, 2.0, 2.0), Vector3(2.4, 1.4, 8.0), 70)
	_dust(Vector3(-6.2, 1.6, 2.5), Vector3(2.8, 1.2, 2.4), 36)

func _build_hiding_spots() -> void:
	_add_hiding_spot(Vector3(-3.58, 0.0, 4.7), "TAQUILLA DEL LABORATORIO", 0.0)
	_add_hiding_spot(Vector3(2.28, 0.0, -2.2), "ARMARIO DEL CORREDOR", PI)

func _add_hiding_spot(pos: Vector3, display_name: String, yaw: float) -> void:
	var spot := HIDING_SCENE.instantiate() as FMHidingSpot
	spot.name = "HidingSpot_" + display_name.replace(" ", "_")
	spot.position = pos
	spot.rotation.y = yaw
	spot.display_name = display_name
	spot.game = self
	add_child(spot)
	_box(level, pos + Vector3(0, 1.1, 0), Vector3(1.0, 2.2, 0.82), "metal_dirty", false)
	for i in 4:
		_box(level, pos + Vector3(-0.28, 1.55 - i * 0.16, 0.43), Vector3(0.34, 0.035, 0.03), "dark", false)
	_box(level, pos + Vector3(0.3, 1.1, 0.43), Vector3(0.04, 0.2, 0.03), "yellow", false)

func _build_security_door() -> void:
	security_door = DOOR_SCENE.instantiate() as FMSecurityDoor
	security_door.name = "SecurityDoor"
	security_door.position = Vector3(0.0, 0.0, -9.9)
	security_door.game = self
	add_child(security_door)
	security_door.opened.connect(_on_security_door_opened)

func _build_batteries() -> void:
	for data in [
		{"name": "BatteryLab", "pos": Vector3(-4.9, 0.76, 0.9)},
		{"name": "BatteryCorridor", "pos": Vector3(2.45, 0.55, -3.2)},
	]:
		var battery := BATTERY_SCENE.instantiate() as FMBattery
		battery.name = data["name"]
		battery.position = data["pos"]
		battery.network_index = batteries.size()
		battery.game = self
		add_child(battery)
		batteries.append(battery)
		battery_taken.append(false)

func _build_noise_trap() -> void:
	noise_trap = TRAP_SCENE.instantiate() as FMNoiseTrap
	noise_trap.name = "NoiseTrap"
	noise_trap.position = Vector3(1.15, 0.0, 6.4)
	noise_trap.game = self
	add_child(noise_trap)

func _build_ambience() -> void:
	var path := "res://assets/audio/ambience/ambience.wav"
	if not ResourceLoader.exists(path):
		return
	var stream := load(path) as AudioStreamWAV
	if stream == null:
		return
	stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
	stream.loop_begin = 0
	stream.loop_end = int(stream.get_length() * stream.mix_rate)
	ambience = AudioStreamPlayer3D.new()
	ambience.name = "Ambience3D"
	ambience.stream = stream
	ambience.position = Vector3(0.0, 2.4, 1.5)
	ambience.unit_size = 9.0
	ambience.max_distance = 38.0
	ambience.volume_db = -21.0
	add_child(ambience)
	ambience.play()

func _on_security_door_opened() -> void:
	if hud != null:
		hud.set_status("PUERTA ABIERTA  ·  LLEGÁ A EXTRACCIÓN")
	if net_mode == NetMode.HOST and net != null:
		net.broadcast_door()

func _build_extraction() -> void:
	extraction = EXTRACTION_SCENE.instantiate() as FMExtraction
	extraction.name = "Extraction"
	extraction.position = EXTRACTION_SPAWN
	add_child(extraction)

func _build_artifact() -> void:
	artifact = ITEM_SCENE.instantiate() as FMCarryItem
	artifact.name = "NexusCore"
	artifact.position = ARTIFACT_SPAWN
	artifact.game = self
	add_child(artifact)

func _build_player() -> void:
	player = PLAYER_SCENE.instantiate() as FMPlayer
	player.name = "Player"
	player.position = SPAWN
	player.set_game(self)
	player.network_client = net_mode == NetMode.CLIENT
	players_root.add_child(player)
	players[local_id] = player

func _build_watcher() -> void:
	watcher = WATCHER_SCENE.instantiate() as FMWatcher
	watcher.name = "Watcher"
	watcher.position = WATCHER_SPAWN
	watcher.set_game(self)
	watcher.set_player(player)
	watcher.set_patrol_points([
		Vector3(0.0, 0.0, 6.0),
		Vector3(-5.2, 0.0, 4.7),
		Vector3(-5.2, 0.0, 1.2),
		Vector3(0.0, 0.0, -2.0),
		Vector3(0.0, 0.0, -7.0),
		Vector3(0.0, 0.0, 3.0),
	])
	add_child(watcher)

func _build_hud() -> void:
	hud = FMHUD.new()
	hud.name = "HUD"
	add_child(hud)
	hud.set_objective("RECUPERAR EL NÚCLEO", "Laboratorio de contención  ·  puerta de seguridad al final del corredor")
	hud.set_status("NÚCLEO EN EL LABORATORIO  ·  PUERTA BLOQUEADA")
	hud.set_battery(100.0, true)
	hud.set_stress(0.0)
	hud.set_stamina(100.0)

func _process(delta: float) -> void:
	_time += delta
	if state != State.PLAYING or player == null or not is_instance_valid(player):
		return

	_update_stress(delta)
	if hud != null:
		hud.set_battery(player.battery, player.flashlight_on)
		hud.set_stress(_stress)
		hud.set_stamina(player.stamina)
		hud.set_hidden(player.hidden)
		hud.set_prompt(player.get_interaction_prompt())
		var observed := watcher != null and watcher.is_observed() and watcher.state != FMWatcher.State.DORMANT
		hud.set_watcher_observed(observed)
		if observed and not _watcher_was_observed:
			Audio.play_sfx("tick", -18.0, 0.6)
		_watcher_was_observed = observed
		_update_status()

	# La victoria y el respawn los decide el host. El cliente recibe el fin por RPC.
	if net_mode != NetMode.CLIENT:
		if extraction != null and player.carried_item != null and _carrier_at_extraction(player):
			_end(State.WON, "NÚCLEO RECUPERADO", "NEXUS recibirá el artefacto. El Vigilante sigue dentro.")
		elif extraction != null and artifact != null and artifact.carried_by != null and _carrier_at_extraction(artifact.carried_by):
			_end(State.WON, "NÚCLEO RECUPERADO", "NEXUS recibirá el artefacto. El Vigilante sigue dentro.")

		if player.global_position.y < -5.0:
			player.global_position = SPAWN
			player.velocity = Vector3.ZERO

func _carrier_at_extraction(carrier: Node3D) -> bool:
	if extraction == null or carrier == null or not is_instance_valid(carrier):
		return false
	var offset := _network_position(carrier) - extraction.global_position
	offset.y = 0.0
	return offset.length() <= 2.1

func _update_stress(delta: float) -> void:
	var target := 0.0
	if not player.hidden:
		var distance := player.global_position.distance_to(watcher.global_position)
		target = clampf(1.0 - distance / 17.0, 0.0, 1.0) * 46.0
		if not player.flashlight_on:
			target += 16.0
		if watcher.state == FMWatcher.State.CHASE:
			target += 34.0
		if watcher.is_observed():
			target += 9.0
	else:
		target = 9.0
	_stress = move_toward(_stress, clampf(target, 0.0, 100.0), delta * 16.0)

func _update_status() -> void:
	if artifact == null:
		return
	if artifact.carried_by == player:
		hud.set_status("NÚCLEO EN MANOS  ·  LLEGÁ A EXTRACCIÓN")
	elif artifact.carried_by != null:
		hud.set_status("EL NÚCLEO ESTÁ SIENDO TRANSPORTADO")
	elif player.hidden:
		hud.set_status("ESCONDIDO  ·  ESCUCHÁ ANTES DE SALIR")
	elif security_door != null and not security_door.is_open:
		hud.set_status("PUERTA DE SEGURIDAD BLOQUEADA  ·  ABRILA CON E")
	else:
		hud.set_status("NÚCLEO EN EL LABORATORIO  ·  PUERTA ABIERTA")

func emit_noise(position: Vector3, radius: float, _kind: String) -> void:
	if net_mode == NetMode.CLIENT:
		# La trampa se valida en el host; su ruido lo emite allí al activarse.
		if net != null and _kind != "glass":
			net.send_noise.rpc_id(1, position, radius)
		return
	if watcher != null and is_instance_valid(watcher):
		watcher.hear_noise(position, radius)

func on_player_hidden(is_hidden: bool) -> void:
	if is_hidden:
		_last_hide_index = _hiding_spot_index(player.hide_spot)
	if net_mode != NetMode.CLIENT:
		emit_noise(player.global_position, 6.0 if is_hidden else 5.0, "hide")
	if net_mode == NetMode.HOST and net != null:
		net.broadcast_hide(local_id, _last_hide_index, is_hidden)
		if not is_hidden:
			_last_hide_index = -1

func _hiding_spot_index(spot: Node) -> int:
	if spot == null:
		return -1
	for i in range(hiding_spots.size()):
		if hiding_spots[i] == spot:
			return i
	return -1

func on_player_caught(_caught: Node3D = null) -> void:
	if state != State.PLAYING or net_mode == NetMode.CLIENT:
		return
	_end(State.LOST, "EL VIGILANTE ENCONTRÓ AL EQUIPO", "No hay armas. No hay segunda oportunidad. R para reintentar.")

func on_battery_taken(index: int, who: Node) -> void:
	if index >= 0 and index < battery_taken.size():
		battery_taken[index] = true
		if index < batteries.size():
			batteries[index] = null
	if net_mode != NetMode.HOST or net == null:
		return
	var pid := local_id
	if who != null and who != player:
		pid = int(who.get("net_id"))
	net.broadcast_battery(index, pid)

func on_artifact_picked(who: Node3D) -> void:
	if net_mode == NetMode.HOST and net != null:
		net.broadcast_carrier(_network_id_of(who), artifact.global_position)

func on_artifact_dropped() -> void:
	if net_mode == NetMode.HOST and net != null:
		net.broadcast_carrier(0, artifact.global_position)

func _network_id_of(who: Node) -> int:
	if who == null:
		return 0
	if who == player:
		return local_id
	return int(who.get("net_id"))

func on_noise_trap_triggered() -> void:
	if net_mode == NetMode.HOST and net != null:
		net.broadcast_trap()
	elif net_mode == NetMode.CLIENT and net != null:
		net.request_trap.rpc_id(1)

func apply_network_door(open_flag: bool) -> void:
	if open_flag and security_door != null and not security_door.is_open:
		security_door.apply_network_open()

func apply_network_battery(index: int, pid: int) -> void:
	if index < 0 or index >= battery_taken.size():
		return
	if battery_taken[index]:
		return
	battery_taken[index] = true
	if index < batteries.size() and is_instance_valid(batteries[index]):
		var battery := batteries[index]
		if pid == local_id and net_mode == NetMode.CLIENT and player != null and player.has_method("recharge_battery"):
			player.recharge_battery(battery.charge_amount)
		battery.queue_free()
		batteries[index] = null

func apply_network_batteries(flags: Array) -> void:
	for i in range(mini(flags.size(), battery_taken.size())):
		if bool(flags[i]) and not battery_taken[i]:
			battery_taken[i] = true
			if i < batteries.size() and is_instance_valid(batteries[i]):
				batteries[i].queue_free()
				batteries[i] = null

func apply_network_trap() -> void:
	if noise_trap != null and is_instance_valid(noise_trap):
		noise_trap.trigger_network()

func apply_network_trap_state(triggered: bool) -> void:
	if triggered:
		apply_network_trap()

func apply_network_carrier(carrier_id: int, position: Vector3) -> void:
	if artifact == null or not is_instance_valid(artifact):
		return
	if carrier_id == 0:
		if player != null and player.carried_item == artifact:
			player.carried_item = null
		artifact.network_set_carrier(null, position)
		return
	if carrier_id == local_id:
		if player != null:
			player.carried_item = artifact
			artifact.network_set_carrier(player, position)
		return
	if player != null and player.carried_item == artifact:
		player.carried_item = null
	var remote = players.get(carrier_id)
	if remote != null and is_instance_valid(remote):
		artifact.network_set_carrier(remote, position)

func apply_network_hide(pid: int, spot_index: int, is_hidden: bool) -> void:
	if pid == local_id:
		if player == null or player.hidden == is_hidden:
			return
		if is_hidden and spot_index >= 0 and spot_index < hiding_spots.size():
			player.hide_in(hiding_spots[spot_index])
		elif not is_hidden and player.hidden:
			player.exit_hide()
		return
	var remote = players.get(pid)
	if remote == null or not is_instance_valid(remote):
		return
	var spot: FMHidingSpot = hiding_spots[spot_index] if spot_index >= 0 and spot_index < hiding_spots.size() else null
	remote.hidden = is_hidden
	remote.visible = not is_hidden
	if spot != null:
		if is_hidden:
			spot.occupant = remote
			remote.global_position = spot.get_hide_point()
		else:
			spot.release_player(remote)
			remote.global_position = spot.get_exit_point()

func apply_network_watcher(position: Vector3, yaw: float, watcher_state: int) -> void:
	if net_mode == NetMode.CLIENT and watcher != null and is_instance_valid(watcher):
		watcher.apply_network_state(position, yaw, watcher_state, watcher.is_observed())

func apply_network_end(result: int, title: String, subtitle: String) -> void:
	_end(result, title, subtitle, true)

func request_network_interaction() -> void:
	if net_mode == NetMode.CLIENT and net != null:
		net.request_interact.rpc_id(1)

func request_network_drop() -> void:
	if net_mode == NetMode.CLIENT and net != null:
		net.request_drop.rpc_id(1)

func resolve_remote_interaction(pid: int) -> void:
	var remote = players.get(pid)
	if remote == null or not is_instance_valid(remote):
		return
	if bool(remote.get("hidden")):
		var old_spot := _spot_for_occupant(remote)
		if old_spot != null:
			old_spot.release_player(remote)
			remote.global_position = old_spot.get_exit_point()
		remote.hidden = false
		remote.visible = true
		emit_noise(remote.global_position, 5.0, "hide")
		if net != null:
			net.broadcast_hide(pid, -1, false)
		return
	if artifact != null and artifact.carried_by == remote:
		resolve_remote_drop(pid)
		return

	# Elegir el interactuable más cercano, igual que el prompt local del jugador.
	var target_position := _network_position(remote)
	var best_kind := ""
	var best_node: Node = null
	var best_distance := 999.0

	if security_door != null and not security_door.is_open:
		var door_distance := target_position.distance_to(security_door.get_interaction_position())
		if door_distance <= 3.2 and door_distance < best_distance:
			best_kind = "door"
			best_node = security_door
			best_distance = door_distance

	for battery in batteries:
		if battery == null or not is_instance_valid(battery) or battery.taken:
			continue
		var battery_distance := target_position.distance_to(battery.get_interaction_position())
		if battery_distance <= 3.0 and battery_distance < best_distance:
			best_kind = "battery"
			best_node = battery
			best_distance = battery_distance

	if artifact != null and is_instance_valid(artifact) and artifact.carried_by == null:
		var artifact_distance := target_position.distance_to(artifact.global_position)
		if artifact_distance <= 3.0 and artifact_distance < best_distance:
			best_kind = "artifact"
			best_node = artifact
			best_distance = artifact_distance

	var spot := _nearest_spot_for(remote)
	if spot != null:
		var spot_distance := target_position.distance_to(spot.get_exit_point())
		if spot_distance <= 2.4 and spot_distance < best_distance:
			best_kind = "hide"
			best_node = spot
			best_distance = spot_distance

	match best_kind:
		"door":
			security_door.interact(remote)
		"battery":
			var battery_node := best_node as FMBattery
			if battery_node != null:
				battery_node.interact(remote)
		"artifact":
			artifact.pickup(remote)
			if net != null:
				net.broadcast_carrier(pid, artifact.global_position)
		"hide":
			var hiding := best_node as FMHidingSpot
			if hiding != null:
				hiding.occupant = remote
				remote.hidden = true
				remote.visible = false
				remote.global_position = hiding.get_hide_point()
				emit_noise(remote.global_position, 6.0, "hide")
				if net != null:
					net.broadcast_hide(pid, _hiding_spot_index(hiding), true)

func resolve_remote_drop(pid: int) -> void:
	var remote = players.get(pid)
	if artifact == null or artifact.carried_by != remote:
		return
	artifact.drop(-remote.global_transform.basis.z)
	if net != null:
		net.broadcast_carrier(0, artifact.global_position)

func drop_carrier_if(pid: int) -> void:
	if artifact == null or artifact.carried_by == null:
		return
	if int(artifact.carried_by.get("net_id")) == pid:
		artifact.drop(Vector3.ZERO)
		if net != null:
			net.broadcast_carrier(0, artifact.global_position)

func on_server_disconnected() -> void:
	if state == State.PLAYING:
		_end(State.LOST, "CONEXIÓN PERDIDA", "El host abandonó la partida. R para volver a intentar.", true)

func _near_point(body: Node3D, point: Vector3, radius: float) -> bool:
	return _network_position(body).distance_to(point) <= radius

func _network_position(body: Node3D) -> Vector3:
	if body == null or not is_instance_valid(body):
		return Vector3.ZERO
	if body.has_method("get_network_position"):
		return body.get_network_position()
	return body.global_position

func _spot_for_occupant(occupant: Node) -> FMHidingSpot:
	for spot in hiding_spots:
		if spot.occupant == occupant:
			return spot
	return null

func _nearest_spot_for(body: Node3D) -> FMHidingSpot:
	var best: FMHidingSpot = null
	var best_distance := 2.4
	for spot in hiding_spots:
		if spot.is_occupied():
			continue
		var distance := body.global_position.distance_to(spot.get_exit_point())
		if distance <= best_distance:
			best = spot
			best_distance = distance
	return best

func clamp_player(body: FMPlayer) -> void:
	body.global_position.x = clampf(body.global_position.x, -9.2, 2.45)
	body.global_position.z = clampf(body.global_position.z, -13.4, 11.4)
	if body.global_position.y < -1.0:
		body.global_position = SPAWN

func _end(result: int, title: String, subtitle: String, from_network := false) -> void:
	if _ending:
		return
	_ending = true
	state = result
	if net_mode != NetMode.OFFLINE:
		subtitle = subtitle.replace("R para reintentar.", "R para volver al menú.")
		subtitle = subtitle.replace("R para volver a intentar.", "R para volver al menú.")
	if net_mode == NetMode.HOST and not from_network and net != null:
		net.broadcast_end(result, title, subtitle)
	if player != null:
		player.velocity = Vector3.ZERO
		player.set_physics_process(false)
	if watcher != null:
		watcher.velocity = Vector3.ZERO
		watcher.set_physics_process(false)
	if artifact != null:
		artifact.set_physics_process(false)
	if ambience != null and is_instance_valid(ambience):
		ambience.stop()
	hud.show_end(title, subtitle)
	Audio.stop_music()
	Audio.play_sfx("win" if state == State.WON else "lose", -4.0)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("pause"):
		get_viewport().set_input_as_handled()
		_leave_to_menu()
		return
	if state != State.PLAYING and event.is_action_pressed("restart"):
		get_viewport().set_input_as_handled()
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		if net_mode == NetMode.OFFLINE:
			get_tree().reload_current_scene()
		else:
			_leave_to_menu()

func _leave_to_menu() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var peer := multiplayer.multiplayer_peer
	if peer is ENetMultiplayerPeer:
		peer.close()
	multiplayer.multiplayer_peer = null
	get_tree().change_scene_to_file("res://scenes/menu.tscn")

# --- Helpers de construcción ------------------------------------------------

func _box(parent: Node3D, pos: Vector3, size: Vector3, mat: String, collide: bool) -> MeshInstance3D:
	var mesh := MeshInstance3D.new()
	var box := BoxMesh.new()
	box.size = size
	mesh.mesh = box
	mesh.material_override = _mat(mat)
	mesh.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	if not collide:
		mesh.position = pos
		parent.add_child(mesh)
		return mesh
	var body := StaticBody3D.new()
	body.position = pos
	body.collision_layer = 1
	body.collision_mask = 0
	var shape := CollisionShape3D.new()
	var box_shape := BoxShape3D.new()
	box_shape.size = size
	shape.shape = box_shape
	body.add_child(shape)
	body.add_child(mesh)
	parent.add_child(body)
	return mesh

func _static_cylinder(pos: Vector3, radius: float, height: float, mat: String) -> void:
	var body := StaticBody3D.new()
	body.position = pos
	body.collision_layer = 1
	body.collision_mask = 0
	var shape := CollisionShape3D.new()
	var cylinder := CylinderShape3D.new()
	cylinder.radius = radius
	cylinder.height = height
	shape.shape = cylinder
	body.add_child(shape)
	var mesh := MeshInstance3D.new()
	var cyl := CylinderMesh.new()
	cyl.top_radius = radius
	cyl.bottom_radius = radius
	cyl.height = height
	cyl.radial_segments = 24
	mesh.mesh = cyl
	mesh.material_override = _mat(mat)
	body.add_child(mesh)
	level.add_child(body)

func _cylinder_mesh(pos: Vector3, radius: float, height: float, mat: String, _collide: bool, rot_deg := Vector3.ZERO) -> MeshInstance3D:
	var mesh := MeshInstance3D.new()
	var cyl := CylinderMesh.new()
	cyl.top_radius = radius
	cyl.bottom_radius = radius
	cyl.height = height
	cyl.radial_segments = 20
	mesh.mesh = cyl
	mesh.material_override = _mat(mat)
	mesh.position = pos
	mesh.rotation_degrees = rot_deg
	level.add_child(mesh)
	return mesh

func _sphere_mesh(pos: Vector3, radius: float, mat: String, scale: Vector3, _collide: bool) -> MeshInstance3D:
	var mesh := MeshInstance3D.new()
	var sphere := SphereMesh.new()
	sphere.radius = radius
	sphere.height = radius * 2.0
	sphere.radial_segments = 20
	sphere.rings = 10
	mesh.mesh = sphere
	mesh.material_override = _mat(mat)
	mesh.position = pos
	mesh.scale = scale
	level.add_child(mesh)
	return mesh

func _quad_mesh(pos: Vector3, size: Vector2, mat: String, rot_deg: Vector3, _collide: bool) -> MeshInstance3D:
	var mesh := MeshInstance3D.new()
	var quad := QuadMesh.new()
	quad.size = size
	mesh.mesh = quad
	mesh.material_override = _mat(mat)
	mesh.position = pos
	mesh.rotation_degrees = rot_deg
	level.add_child(mesh)
	return mesh

func _omni(pos: Vector3, color: Color, energy: float, radius: float) -> OmniLight3D:
	var light := OmniLight3D.new()
	light.position = pos
	light.light_color = color
	light.light_energy = energy
	light.omni_range = radius
	light.omni_attenuation = 1.2
	light.shadow_enabled = false
	light.light_volumetric_fog_energy = 0.8
	add_child(light)
	return light

func _spot(pos: Vector3, target: Vector3, color: Color, energy: float, angle: float, range: float, shadow: bool) -> SpotLight3D:
	var light := SpotLight3D.new()
	light.position = pos
	light.light_color = color
	light.light_energy = energy
	light.spot_angle = angle
	light.spot_range = range
	light.spot_attenuation = 1.1
	light.spot_angle_attenuation = 0.8
	light.shadow_enabled = shadow
	light.light_volumetric_fog_energy = 1.2
	add_child(light)
	light.look_at(target, Vector3.UP)
	return light

func _label3d(text: String, pos: Vector3, size: int, color: Color, billboard := true, rot_deg := Vector3.ZERO) -> Label3D:
	var label := Label3D.new()
	label.text = text
	label.font_size = size
	label.pixel_size = 0.0065
	label.modulate = color
	label.outline_size = 7
	label.outline_modulate = Color(0.005, 0.01, 0.012, 0.95)
	label.position = pos
	label.rotation_degrees = rot_deg
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED if billboard else BaseMaterial3D.BILLBOARD_DISABLED
	label.double_sided = true
	level.add_child(label)
	return label

func _dust(pos: Vector3, extents: Vector3, amount: int) -> void:
	var particles := GPUParticles3D.new()
	particles.amount = amount
	particles.lifetime = 12.0
	particles.preprocess = 5.0
	particles.position = pos
	particles.local_coords = false
	particles.visibility_aabb = AABB(Vector3(-15, -4, -15), Vector3(30, 10, 30))
	var pm := ParticleProcessMaterial.new()
	pm.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
	pm.emission_box_extents = extents
	pm.gravity = Vector3(0.0, 0.006, 0.0)
	pm.initial_velocity_min = 0.005
	pm.initial_velocity_max = 0.03
	pm.scale_min = 0.01
	pm.scale_max = 0.025
	pm.color = Color(0.75, 0.86, 0.85, 0.16)
	particles.process_material = pm
	var quad := QuadMesh.new()
	quad.size = Vector2(0.035, 0.035)
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.albedo_texture = load("res://assets/art/fm/smoke.png")
	mat.albedo_color = Color(0.8, 0.9, 0.9, 0.16)
	mat.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	quad.material = mat
	particles.draw_pass_1 = quad
	add_child(particles)
