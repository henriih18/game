extends Node3D

## FRECUENCIA MUERTA — Vertical slice jugable local (1 jugador).
##
## Compone las escenas de arte ya aprobadas de Z10 (R8, oscura) y Recepción
## (R9, prácticas cálidas) sin modificar sus GLB ni sus escenas. Reutiliza los
## sistemas compartidos del proyecto: FMPlayer, FMWatcher, FMHidingSpot,
## FMCarryItem, FMBattery, FMReceptionExtraction, FMHUD y FMGLBCollision.
##
## El enlace Z10 → Recepción es provisional: la exportación V06 del nivel
## completo todavía no existe y ambos sectores están separados en coordenadas.

const PLAYER_SCENE := preload("res://scenes/fm/fm_player.tscn")
const WATCHER_SCENE := preload("res://scenes/fm/fm_watcher.tscn")
const CARRY_ITEM_SCENE := preload("res://scenes/fm/carry_item.tscn")
const DISMANTLE_SCRIPT := preload("res://scripts/fm/fm_dismantlable.gd")
const HIDING_SPOT_SCENE := preload("res://scenes/fm/hiding_spot.tscn")
const BATTERY_SCRIPT := preload("res://scripts/fm/fm_battery.gd")
const EXTRACTION_SCRIPT := preload("res://scripts/fm/fm_reception_extraction.gd")
const HUD_SCRIPT := preload("res://scripts/fm/fm_hud.gd")
const INVENTORY_UI_SCENE := preload("res://scenes/fm/fm_inventory_ui.tscn")
const TRANSITION_SCRIPT := preload("res://scripts/fm/fm_sector_transition.gd")
const COLLISION_HELPER := preload("res://scripts/fm/fm_glb_collision.gd")
const NARRATIVE_PROPS := preload("res://scripts/fm/fm_narrative_props.gd")
const AMBIENCE := preload("res://assets/audio/ambience/ambience.wav")

const Z10_SPAWN := Vector3(42.2, 0.12, -22.0)
const Z10_SPAWN_YAW := -PI * 0.5  # mirando +X, hacia el conector
const RECEPTION_SPAWN := Vector3(-90.0, 0.12, 6.2)
const RECEPTION_SPAWN_YAW := PI  # mirando +Z, hacia la recepción
const EXTRACTION_CENTER := Vector3(-94.0, 0.30, 37.6)
const CORE_POSITION := Vector3(57.4, 0.36, -21.4)
const DISMANTLE_POSITION := Vector3(51.2, 0.0, -17.2)
const HIDE_POSITION := Vector3(42.5, 0.05, -9.4)
const RECEPTION_HIDE_POSITION := Vector3(-106.0, 0.05, 38.8)
const TRANSITION_POSITION := Vector3(69.05, 0.0, -21.0)
const EXTRACTION_ZONE_SIZE := Vector3(9.0, 2.6, 8.0)
const RECEPTION_ARRIVAL_POSITION := Vector3(-90.0, 0.0, 4.0)
const RECEPTION_WATCHER_SPAWN := Vector3(-93.0, 0.12, 29.0)
const RECEPTION_WATCHER_YAW := 0.0

const Z10_BOUNDS := AABB(Vector3(39.6, -1.5, -30.6), Vector3(30.9, 8.0, 23.0))
const RECEPTION_BOUNDS := AABB(Vector3(-110.5, -1.5, 3.8), Vector3(40.6, 7.5, 36.5))

enum State { PLAYING, WON, LOST, TRANSITION }

var state: State = State.PLAYING
var player: FMPlayer
var watcher: FMWatcher
var hud: FMHUD
var inventory_ui: FMInventoryUI
var extraction: FMReceptionExtraction
var transition_door: Node3D
var narrative: Node3D
var reception_arrival_door: StaticBody3D
var reception_hiding_spot: FMHidingSpot
var carry_items: Array[FMCarryItem] = []
var dismantlable: FMDismantlable
var level_ready := false
var current_area := "Z10"

var z10_root: Node3D
var reception_root: Node3D
var world_env: WorldEnvironment
var z10_environment: Environment
var reception_environment: Environment
var _z10_collider_count := 0
var _reception_collider_count := 0

var _fade_layer: CanvasLayer
var _fade: ColorRect
var _status_timer := 0.0
var _extraction_busy := false
var _transitioning := false
var _watcher_suspended := false
## Permite desactivar la IA de Recepción en pruebas de navegación sin
## cambiar el comportamiento normal de la partida.
var reception_watcher_enabled := true


func _ready() -> void:
	if DisplayServer.get_name() != "headless":
		DisplayServer.window_set_size(Vector2i(1280, 720))
	_setup_art()
	if z10_root == null or reception_root == null:
		push_error("Vertical slice sin geometría de Z10 o Recepción")
		return
	_setup_narrative()
	await get_tree().process_frame
	_setup_collisions()
	_setup_player()
	_setup_hiding_spot()
	_setup_core()
	_setup_dismantlable()
	_setup_navigation()
	_setup_batteries()
	_setup_transition()
	_setup_extraction()
	_setup_watcher()
	_setup_hud()
	_setup_inventory_ui()
	_setup_audio()
	_setup_fade()
	level_ready = true
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	print("FM_VSLICE_Z10_READY state=%d z10_colliders=%d reception_colliders=%d core=%s" % [
		state, _z10_collider_count, _reception_collider_count, str(CORE_POSITION),
	])


func _setup_art() -> void:
	z10_root = get_node_or_null("Z10Art/Z10Sector") as Node3D
	reception_root = get_node_or_null("ReceptionArt/ReceptionSector") as Node3D
	if z10_root == null or reception_root == null:
		push_error("No se encontraron los GLB de Z10 o Recepción")
		return

	var z10_world := get_node_or_null("Z10Art/WorldEnvironment") as WorldEnvironment
	var reception_world := get_node_or_null("ReceptionArt/WorldEnvironment") as WorldEnvironment
	if z10_world != null and z10_world.environment != null:
		z10_environment = z10_world.environment.duplicate(true) as Environment
		z10_world.environment = null
	if reception_world != null and reception_world.environment != null:
		reception_environment = reception_world.environment.duplicate(true) as Environment
		reception_world.environment = null
	if z10_environment == null:
		z10_environment = Environment.new()
		z10_environment.background_mode = Environment.BG_COLOR
		z10_environment.background_color = Color(0.0015, 0.0018, 0.0022)
	if reception_environment == null:
		reception_environment = z10_environment.duplicate(true) as Environment

	var z10_camera := get_node_or_null("Z10Art/ArtCamera") as Camera3D
	var reception_camera := get_node_or_null("ReceptionArt/ArtCamera") as Camera3D
	if z10_camera != null:
		z10_camera.current = false
	if reception_camera != null:
		reception_camera.current = false

	world_env = WorldEnvironment.new()
	world_env.name = "VSliceWorldEnvironment"
	world_env.environment = z10_environment
	add_child(world_env)


func _setup_narrative() -> void:
	# Hermano de Z10Art/ReceptionArt, no hijo: FMGLBCollision.build() recorre
	# los GLB de arte y añadiría colisiones a las mallas narrativas.
	narrative = NARRATIVE_PROPS.new() as Node3D
	narrative.name = "Narrative"
	add_child(narrative)


func _setup_collisions() -> void:
	if z10_root != null:
		var z10_result: Dictionary = COLLISION_HELPER.build(self, z10_root, Z10_BOUNDS)
		_z10_collider_count = int(z10_result["count"])
	if reception_root != null:
		var reception_result: Dictionary = COLLISION_HELPER.build(self, reception_root, RECEPTION_BOUNDS)
		_reception_collider_count = int(reception_result["count"])
	# Suelo de seguridad: cubre huecos entre módulos sin sustituir la geometría.
	_add_safety_floor("Z10SafetyFloor", Vector3(55.0, -0.26, -18.0), Vector3(30.6, 0.5, 37.0))
	_add_safety_floor("ReceptionSafetyFloor", Vector3(-90.0, -0.26, 24.0), Vector3(40.5, 0.5, 32.4))
	print("FM_VSLICE_COLLIDERS z10=%d reception=%d" % [_z10_collider_count, _reception_collider_count])


func _add_safety_floor(body_name: String, center: Vector3, size: Vector3) -> void:
	var body := StaticBody3D.new()
	body.name = body_name
	body.collision_layer = 1
	body.collision_mask = 0
	body.position = center
	var shape := BoxShape3D.new()
	shape.size = size
	var collider := CollisionShape3D.new()
	collider.shape = shape
	body.add_child(collider)
	add_child(body)


func _setup_navigation() -> void:
	# El navmesh se hornea de las colisiones estáticas ya construidas. El
	# Vigilante usa NavigationAgent3D; las rutas manuales quedan como respaldo.
	var region := NavigationRegion3D.new()
	region.name = "Navigation"
	var nav_mesh := NavigationMesh.new()
	nav_mesh.agent_radius = 0.45
	nav_mesh.agent_height = 2.20
	nav_mesh.agent_max_climb = 0.30
	nav_mesh.agent_max_slope = 45.0
	nav_mesh.cell_size = 0.25
	nav_mesh.cell_height = 0.20
	nav_mesh.geometry_parsed_geometry_type = NavigationMesh.PARSED_GEOMETRY_STATIC_COLLIDERS
	nav_mesh.geometry_collision_mask = 1
	nav_mesh.geometry_source_geometry_mode = NavigationMesh.SOURCE_GEOMETRY_GROUPS_WITH_CHILDREN
	nav_mesh.geometry_source_group_name = &"fm_nav_source"
	region.navigation_mesh = nav_mesh
	add_child(region)
	add_to_group("fm_nav_source")
	region.bake_navigation_mesh(false)
	print("FM_NAVIGATION_READY polygons=%d" % nav_mesh.get_polygon_count())


func _setup_player() -> void:
	player = PLAYER_SCENE.instantiate() as FMPlayer
	player.name = "Player"
	player.position = Z10_SPAWN
	player.rotation.y = Z10_SPAWN_YAW
	add_child(player)
	player.set_game(self)
	player.network_client = false
	player.set_flashlight_model(true)
	player.max_battery = 100.0
	player.battery = 100.0
	player.battery_drain = 0.65
	player.flashlight_on = true
	_tune_flashlight()
	player.add_to_group("fm_player")


func _tune_flashlight() -> void:
	if player == null or player.flashlight == null:
		return
	player.flashlight.light_color = Color(1.0, 0.90, 0.72)
	player.flashlight.light_energy = 11.0
	player.flashlight.spot_range = 24.0
	player.flashlight.spot_angle = 31.0
	player.flashlight.spot_angle_attenuation = 0.92
	player.flashlight.shadow_enabled = true
	player.flashlight.light_volumetric_fog_energy = 1.35
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
	spill.light_energy = 2.0
	spill.spot_range = 10.0
	spill.spot_angle = 56.0
	spill.spot_angle_attenuation = 1.7
	spill.shadow_enabled = false
	player.camera.add_child(spill)


func _setup_hiding_spot() -> void:
	var spot := HIDING_SPOT_SCENE.instantiate() as FMHidingSpot
	spot.name = "HideShelves"
	spot.display_name = "ESTANTERÍA"
	spot.position = HIDE_POSITION
	spot.rotation.y = PI
	spot.game = self
	add_child(spot)
	var shape := spot.get_node_or_null("CollisionShape3D") as CollisionShape3D
	if shape != null:
		shape.position.y = 1.05
	var exit_point := spot.get_node_or_null("ExitPoint") as Marker3D
	if exit_point != null:
		exit_point.position = Vector3(0.0, 0.0, 1.25)
	var hide_point := spot.get_node_or_null("HidePoint") as Marker3D
	if hide_point != null:
		hide_point.position = Vector3(0.0, 0.0, 0.0)

	var reception_spot := HIDING_SPOT_SCENE.instantiate() as FMHidingSpot
	reception_spot.name = "HideReceptionLockers"
	reception_spot.display_name = "TAQUILLAS DE PERSONAL"
	reception_spot.position = RECEPTION_HIDE_POSITION
	reception_spot.rotation.y = 0.0
	reception_spot.game = self
	add_child(reception_spot)
	var reception_shape := reception_spot.get_node_or_null("CollisionShape3D") as CollisionShape3D
	if reception_shape != null:
		reception_shape.position.y = 1.05
	var reception_exit := reception_spot.get_node_or_null("ExitPoint") as Marker3D
	if reception_exit != null:
		reception_exit.position = Vector3(0.0, 0.0, 1.25)
	var reception_hide := reception_spot.get_node_or_null("HidePoint") as Marker3D
	if reception_hide != null:
		reception_hide.position = Vector3(0.0, 0.0, 0.0)
	reception_hiding_spot = reception_spot


func _setup_core() -> void:
	var item := CARRY_ITEM_SCENE.instantiate() as FMCarryItem
	item.name = "Loot_Core_Z10"
	item.item_name = "NÚCLEO DE CONTENCIÓN"
	item.item_mass = 7.0
	item.size_class = "MEDIUM"
	item.item_kind = "core"
	item.is_mission_item = true
	item.position = CORE_POSITION
	item.rotation.y = 0.35
	item.game = self
	add_child(item)
	carry_items.append(item)


func _setup_dismantlable() -> void:
	dismantlable = DISMANTLE_SCRIPT.new()
	dismantlable.name = "AnalysisStation_Z10"
	dismantlable.position = DISMANTLE_POSITION
	dismantlable.rotation.y = PI * 0.5
	dismantlable.game = self
	add_child(dismantlable)


func _setup_batteries() -> void:
	_add_battery("Battery_Workbench", Vector3(43.0, 0.16, -14.8), 40.0)
	_add_battery("Battery_Storage", Vector3(53.4, 0.16, -25.4), 40.0)
	_add_battery("Battery_ServiceLink", Vector3(63.2, 0.16, -22.7), 35.0)
	_add_battery("Battery_Reception", Vector3(-104.0, 0.16, 20.2), 40.0)


func _add_battery(battery_name: String, pos: Vector3, charge: float) -> void:
	var battery = BATTERY_SCRIPT.new()
	battery.name = battery_name
	battery.charge_amount = charge
	battery.position = pos
	battery.game = self
	add_child(battery)


func _setup_transition() -> void:
	transition_door = TRANSITION_SCRIPT.new()
	transition_door.name = "ServiceLinkToReception"
	transition_door.position = TRANSITION_POSITION
	transition_door.rotation.y = PI * 0.5
	transition_door.game = self
	add_child(transition_door)
	_add_reception_arrival_door()


func _setup_extraction() -> void:
	extraction = EXTRACTION_SCRIPT.new()
	extraction.name = "ReceptionExtraction"
	extraction.position = Vector3(-94.0, 1.3, 36.0)
	extraction.game = self
	extraction.delivery_center = EXTRACTION_CENTER
	extraction.zone_size = EXTRACTION_ZONE_SIZE
	extraction.extraction_started.connect(on_extraction_started)
	extraction.extraction_progress.connect(on_extraction_progress)
	extraction.extraction_completed.connect(on_extraction_completed)
	add_child(extraction)
	_add_extraction_marker()


func _add_extraction_marker() -> void:
	# Compuerta de salida provisional. La exportación V06 de recepción todavía
	# no incluye el ascensor SALIDA; este marco marca la entrega sin sustituir
	# la geometría definitiva.
	var steel := StandardMaterial3D.new()
	steel.albedo_color = Color(0.052, 0.060, 0.066, 1.0)
	steel.metallic = 0.78
	steel.roughness = 0.42
	var dark := StandardMaterial3D.new()
	dark.albedo_color = Color(0.020, 0.024, 0.028, 1.0)
	dark.metallic = 0.62
	dark.roughness = 0.54
	var hazard := StandardMaterial3D.new()
	hazard.albedo_color = Color(0.72, 0.52, 0.06, 1.0)
	hazard.metallic = 0.22
	hazard.roughness = 0.58
	var screen := StandardMaterial3D.new()
	screen.albedo_color = Color(0.04, 0.38, 0.20, 1.0)
	screen.emission_enabled = true
	screen.emission = Color(0.10, 1.0, 0.46)
	screen.emission_energy_multiplier = 1.0
	screen.roughness = 0.24

	_add_gate_box(Vector3(-95.48, 1.20, 39.70), Vector3(0.18, 2.40, 0.32), steel)
	_add_gate_box(Vector3(-92.52, 1.20, 39.70), Vector3(0.18, 2.40, 0.32), steel)
	_add_gate_box(Vector3(-94.0, 2.42, 39.70), Vector3(2.96, 0.20, 0.32), steel)
	_add_gate_box(Vector3(-94.60, 1.12, 39.76), Vector3(1.14, 2.18, 0.075), dark)
	_add_gate_box(Vector3(-93.40, 1.12, 39.76), Vector3(1.14, 2.18, 0.075), dark)
	_add_gate_box(Vector3(-94.0, 1.12, 39.72), Vector3(0.032, 2.18, 0.022), steel)
	_add_gate_box(Vector3(-94.0, 0.20, 39.72), Vector3(2.10, 0.10, 0.020), hazard)
	_add_gate_box(Vector3(-93.05, 1.58, 39.71), Vector3(0.34, 0.22, 0.020), screen)
	var gate_sign := Label3D.new()
	gate_sign.name = "ExtractionGateSign"
	gate_sign.text = "SALIDA"
	gate_sign.font_size = 34
	gate_sign.pixel_size = 0.006
	gate_sign.modulate = Color(0.54, 1.0, 0.66, 1.0)
	gate_sign.outline_size = 7
	gate_sign.outline_modulate = Color(0.004, 0.02, 0.008, 0.95)
	gate_sign.position = Vector3(-94.0, 2.78, 39.52)
	gate_sign.rotation.y = PI
	add_child(gate_sign)

	var ring := MeshInstance3D.new()
	ring.name = "ExtractionRing"
	var torus := TorusMesh.new()
	torus.inner_radius = 1.38
	torus.outer_radius = 1.50
	torus.rings = 40
	torus.ring_segments = 8
	ring.mesh = torus
	var ring_mat := StandardMaterial3D.new()
	ring_mat.albedo_color = Color(0.06, 0.45, 0.22, 1.0)
	ring_mat.emission_enabled = true
	ring_mat.emission = Color(0.10, 1.0, 0.46)
	ring_mat.emission_energy_multiplier = 1.35
	ring_mat.roughness = 0.32
	ring.material_override = ring_mat
	ring.position = Vector3(-94.0, 0.035, 37.6)
	add_child(ring)

	var label := Label3D.new()
	label.name = "ExtractionLabel"
	label.text = "EXTRACCIÓN // RECEPCIÓN"
	label.font_size = 30
	label.pixel_size = 0.006
	label.modulate = Color(0.55, 1.0, 0.66, 1.0)
	label.outline_size = 7
	label.outline_modulate = Color(0.004, 0.02, 0.008, 0.95)
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.position = Vector3(-94.0, 3.35, 37.0)
	add_child(label)

	var light := OmniLight3D.new()
	light.name = "ExtractionMarkerLight"
	light.light_color = Color(0.16, 1.0, 0.48)
	light.light_energy = 0.55
	light.omni_range = 4.0
	light.shadow_enabled = false
	light.position = Vector3(-94.0, 1.55, 37.4)
	add_child(light)


func _add_gate_box(pos: Vector3, size: Vector3, material: Material) -> MeshInstance3D:
	var box := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = size
	box.mesh = mesh
	box.material_override = material
	box.position = pos
	add_child(box)
	return box


func _add_reception_arrival_door() -> void:
	var steel := StandardMaterial3D.new()
	steel.albedo_color = Color(0.052, 0.060, 0.066, 1.0)
	steel.metallic = 0.78
	steel.roughness = 0.42

	var dark := StandardMaterial3D.new()
	dark.albedo_color = Color(0.020, 0.024, 0.028, 1.0)
	dark.metallic = 0.62
	dark.roughness = 0.54

	var hazard := StandardMaterial3D.new()
	hazard.albedo_color = Color(0.72, 0.52, 0.06, 1.0)
	hazard.metallic = 0.22
	hazard.roughness = 0.58

	var screen := StandardMaterial3D.new()
	screen.albedo_color = Color(0.35, 0.03, 0.02, 1.0)
	screen.emission_enabled = true
	screen.emission = Color(1.0, 0.12, 0.06, 1.0)
	screen.emission_energy_multiplier = 0.9
	screen.roughness = 0.24

	var door := StaticBody3D.new()
	door.name = "ReceptionArrivalDoor"
	door.position = RECEPTION_ARRIVAL_POSITION
	door.collision_layer = 1
	door.collision_mask = 0
	add_child(door)

	var shape := BoxShape3D.new()
	shape.size = Vector3(3.0, 2.42, 0.30)
	var collider := CollisionShape3D.new()
	collider.name = "ArrivalDoorCollider"
	collider.shape = shape
	collider.position = Vector3(0.0, 1.21, 0.06)
	door.add_child(collider)
	reception_arrival_door = door

	_add_gate_box(Vector3(-91.55, 1.25, 4.0), Vector3(0.18, 2.50, 0.32), steel)
	_add_gate_box(Vector3(-88.45, 1.25, 4.0), Vector3(0.18, 2.50, 0.32), steel)
	_add_gate_box(Vector3(-90.0, 2.50, 4.0), Vector3(3.28, 0.20, 0.32), steel)
	_add_gate_box(Vector3(-90.75, 1.15, 4.08), Vector3(1.42, 2.22, 0.075), dark)
	_add_gate_box(Vector3(-89.25, 1.15, 4.08), Vector3(1.42, 2.22, 0.075), dark)
	_add_gate_box(Vector3(-90.0, 1.15, 4.12), Vector3(0.032, 2.22, 0.022), steel)
	_add_gate_box(Vector3(-90.0, 0.25, 4.12), Vector3(2.80, 0.10, 0.020), hazard)
	_add_gate_box(Vector3(-88.95, 1.55, 4.12), Vector3(0.34, 0.22, 0.020), screen)

	var label := Label3D.new()
	label.name = "ArrivalDoorLabel"
	label.text = "ENLACE BLOQUEADO\nZ10"
	label.font_size = 30
	label.pixel_size = 0.006
	label.modulate = Color(1.0, 0.45, 0.32, 1.0)
	label.outline_size = 7
	label.outline_modulate = Color(0.02, 0.004, 0.002, 0.95)
	label.position = Vector3(-90.0, 2.82, 4.18)
	add_child(label)


func _setup_watcher() -> void:
	watcher = WATCHER_SCENE.instantiate() as FMWatcher
	watcher.name = "Watcher"
	watcher.position = Vector3(59.0, 0.12, -14.5)
	watcher.rotation.y = 0.0
	add_child(watcher)
	watcher.set_game(self)
	watcher.set_player(player)
	# Ruta al sur de la zanja de cables y del transformador para evitar que el
	# CharacterBody se atasque en props bajos (no hay navmesh en este slice).
	var patrol: Array[Vector3] = [
		Vector3(59.0, 0.12, -25.0),
		Vector3(45.0, 0.12, -25.0),
		Vector3(45.0, 0.12, -14.5),
		Vector3(59.0, 0.12, -14.5),
	]
	watcher.set_patrol_points(patrol)


## Ruta de patrulla de Recepción: pasillo central oeste, lejos de los desks
## de seguridad, la columna de x=-90 y los anclajes narrativos N6/N7.
func _reception_watcher_patrol() -> Array[Vector3]:
	return [
		Vector3(-93.0, 0.12, 29.0),
		Vector3(-95.0, 0.12, 24.0),
		Vector3(-93.0, 0.12, 19.0),
		Vector3(-95.0, 0.12, 14.0),
		Vector3(-93.0, 0.12, 19.0),
		Vector3(-95.0, 0.12, 24.0),
		Vector3(-93.0, 0.12, 29.0),
		Vector3(-95.0, 0.12, 32.0),
	]


func _setup_hud() -> void:
	hud = HUD_SCRIPT.new()
	hud.name = "HUD"
	add_child(hud)
	hud.set_objective("RECUPERAR EL NÚCLEO", "Z10 · Conector de servicio · Recepción")
	hud.set_status("EXPLORÁ Z10 Y RECUPERÁ EL NÚCLEO")
	hud.set_battery(player.battery, player.flashlight_on)
	hud.set_stamina(player.stamina)
	hud.set_stress(0.0)
	hud.set_hint("WASD MOVER   ·   SHIFT CORRER   ·   CTRL AGACHARSE   ·   E INTERACTUAR   ·   F LINTERNA   ·   I INVENTARIO   ·   Q SOLTAR   ·   R REINICIAR   ·   ESC MOUSE   ·   M SILENCIO")


func _setup_inventory_ui() -> void:
	inventory_ui = INVENTORY_UI_SCENE.instantiate() as FMInventoryUI
	inventory_ui.name = "InventoryUI"
	add_child(inventory_ui)
	inventory_ui.setup(player)


func _setup_audio() -> void:
	Audio.stop_music()
	_add_ambience("AmbienceZ10", Vector3(52.0, 2.4, -18.0), 0.82, -16.5, 52.0)
	_add_ambience("AmbienceReception", Vector3(-90.0, 2.4, 24.0), 1.0, -18.0, 52.0)


func _add_ambience(node_name: String, pos: Vector3, pitch: float, volume_db: float, max_distance: float) -> void:
	var stream := _looped(AMBIENCE)
	if stream == null:
		return
	var audio := AudioStreamPlayer3D.new()
	audio.name = node_name
	audio.stream = stream
	audio.position = pos
	audio.pitch_scale = pitch
	audio.volume_db = volume_db
	audio.unit_size = 10.0
	audio.max_distance = max_distance
	audio.attenuation_model = AudioStreamPlayer3D.ATTENUATION_INVERSE_DISTANCE
	add_child(audio)
	audio.play()


func _looped(stream: AudioStream) -> AudioStream:
	if stream is AudioStreamWAV:
		var wav := (stream as AudioStreamWAV).duplicate() as AudioStreamWAV
		wav.loop_mode = AudioStreamWAV.LOOP_FORWARD
		wav.loop_begin = 0
		wav.loop_end = int(wav.get_length() * wav.mix_rate)
		return wav
	return stream


func _setup_fade() -> void:
	_fade_layer = CanvasLayer.new()
	_fade_layer.name = "VSliceFade"
	_fade_layer.layer = 30
	add_child(_fade_layer)
	_fade = ColorRect.new()
	_fade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_fade.color = Color(0.0, 0.0, 0.0, 1.0)
	_fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_fade_layer.add_child(_fade)
	var intro := create_tween()
	intro.tween_property(_fade, "color:a", 0.0, 1.2)


func _process(delta: float) -> void:
	if not level_ready or player == null or not is_instance_valid(player):
		return
	if hud != null:
		hud.set_battery(player.battery, player.flashlight_on)
		hud.set_stamina(player.stamina)
		hud.set_carry(player.get_carry_weight(), player.max_carry_weight, player.get_inventory_count(), player.inventory_capacity)
		hud.set_prompt(player.get_interaction_prompt())
		hud.set_hidden(player.hidden)
		var observer_visible := current_area == "Z10" and not _watcher_suspended and watcher != null and is_instance_valid(watcher) and watcher.observed
		hud.set_watcher_observed(observer_visible)

	_status_timer = maxf(0.0, _status_timer - delta)
	if _status_timer <= 0.0 and not _extraction_busy and hud != null:
		_status_timer = 0.4
		hud.set_status(_context_status())

	if player.global_position.y < -2.5:
		_respawn_player()


func _context_status() -> String:
	if state != State.PLAYING:
		return ""
	if current_area == "RECEPTION":
		var radius := extraction.delivery_radius_m if extraction != null else 2.4
		if has_delivered_mission_item(EXTRACTION_CENTER, radius):
			return "NÚCLEO EN ZONA DE EXTRACCIÓN · PERMANECÉ DENTRO"
		if _player_has_mission_item():
			return "LLEVÁ EL NÚCLEO A LA ZONA DE EXTRACCIÓN (SUR)"
		if player.get_inventory_count() > 0:
			return "COMPONENTES ASEGURADOS · LA EXTRACCIÓN REQUIERE EL NÚCLEO"
		return "RECEPCIÓN · LA EXTRACCIÓN REQUIERE EL NÚCLEO"
	if _player_has_mission_item():
		return "NÚCLEO ASEGURADO · CRUZÁ EL ENLACE DE SERVICIO"
	if player.get_inventory_count() > 0:
		return "COMPONENTES GUARDADOS · BUSCÁ EL NÚCLEO"
	return "EXPLORÁ Z10 Y RECUPERÁ EL NÚCLEO"


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("restart"):
		get_tree().reload_current_scene()
		get_viewport().set_input_as_handled()
		return
	if event.is_action_pressed("pause"):
		if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
			Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		else:
			Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
		get_viewport().set_input_as_handled()


func notify(text: String) -> void:
	_status_timer = 2.6
	if hud != null:
		hud.set_status(text)


# ---------------------------------------------------------------------------
# API consumida por los sistemas compartidos (FMPlayer, FMWatcher, extracción)
# ---------------------------------------------------------------------------

func emit_noise(position: Vector3, radius: float, _kind: String) -> void:
	if watcher != null and is_instance_valid(watcher) and not _watcher_suspended:
		watcher.hear_noise(position, radius)


func get_active_player_count() -> int:
	return 1 if player != null and is_instance_valid(player) and state == State.PLAYING else 0


func all_alive_players_inside(area: Area3D) -> bool:
	return area != null and player != null and area.players_inside.has(player)


func any_alive_player_inside(area: Area3D) -> bool:
	return area != null and player != null and area.players_inside.has(player)


func register_carry_item(item: FMCarryItem) -> void:
	if item == null or not is_instance_valid(item):
		return
	if not carry_items.has(item):
		carry_items.append(item)


func get_delivered_loot_count(center: Vector3, radius: float) -> int:
	var delivered := {}
	for item in carry_items:
		if item != null and is_instance_valid(item) and item.global_position.distance_to(center) <= radius:
			delivered[item.get_instance_id()] = true
	if player != null and is_instance_valid(player):
		if extraction != null and extraction.players_inside.has(player):
			for item in player.inventory:
				if item != null and is_instance_valid(item):
					delivered[item.get_instance_id()] = true
			var carried = player.carried_item
			if carried != null and is_instance_valid(carried) and carry_items.has(carried):
				delivered[carried.get_instance_id()] = true
	return delivered.size()


func has_delivered_mission_item(center: Vector3, radius: float) -> bool:
	for item in carry_items:
		if item != null and is_instance_valid(item) and item.is_mission_item and item.global_position.distance_to(center) <= radius:
			return true
	if player != null and is_instance_valid(player) and extraction != null and extraction.players_inside.has(player):
		if player.carried_item is FMCarryItem and (player.carried_item as FMCarryItem).is_mission_item:
			return true
		for item in player.inventory:
			if item != null and is_instance_valid(item) and item.is_mission_item:
				return true
	return false


func _player_has_mission_item() -> bool:
	if player == null or not is_instance_valid(player):
		return false
	if player.carried_item is FMCarryItem and (player.carried_item as FMCarryItem).is_mission_item:
		return true
	for item in player.inventory:
		if item != null and is_instance_valid(item) and item.is_mission_item:
			return true
	return false


func on_item_collected(who: Node, item: FMCarryItem) -> void:
	if who != player or item == null:
		return
	if item.is_mission_item:
		notify("NÚCLEO RECUPERADO · LLEGALO A RECEPCIÓN")
		if hud != null:
			hud.set_objective("LLEVAR EL NÚCLEO A RECEPCIÓN", "Enlace de servicio al este de Z10")
		return
	notify("%s GUARDADO · %s" % [item.item_name, player.get_carry_summary()])
	if hud != null:
		hud.set_status("%s ASEGURADO · %s" % [item.item_name, player.get_carry_summary()])


func on_dismantle_completed(_station: Node, components: Array) -> void:
	notify("DESMONTAJE COMPLETADO · %d COMPONENTES" % components.size())
	if hud != null:
		hud.set_status("RECOGÉ LOS COMPONENTES DEL PUESTO DE ANÁLISIS")


func on_artifact_picked(who: Node) -> void:
	if who != player or player.carried_item == null:
		return
	var item := player.carried_item as FMCarryItem
	if item == null:
		return
	if item.is_mission_item:
		notify("NÚCLEO RECUPERADO · LLEGALO A RECEPCIÓN")
		if hud != null:
			hud.set_objective("LLEVAR EL NÚCLEO A RECEPCIÓN", "Enlace de servicio al este de Z10")
	else:
		notify("%s EN MANOS · LLEGALO A RECEPCIÓN" % item.item_name)


func on_artifact_dropped() -> void:
	if player != null and player.carried_item != null:
		notify("OBJETO SOLTADO")
	else:
		notify("COMPONENTE SOLTADO")


func on_player_hidden(is_hidden: bool) -> void:
	if hud != null:
		hud.set_hidden(is_hidden)
	notify("ESCONDIDO ENTRE LAS ESTANTERÍAS" if is_hidden else "SALISTE DEL ESCONDITE")


func on_player_caught(_who: Node = null) -> void:
	if state != State.PLAYING:
		return
	state = State.LOST
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	if player != null:
		player.velocity = Vector3.ZERO
	Audio.play_sfx("lose", -8.0)
	if inventory_ui != null:
		inventory_ui.close()
	if hud != null:
		var area_label := "Recepción" if current_area == "RECEPTION" else "Z10"
		hud.show_end("DETECTADO", "El Vigilante te encontró en %s. R para reiniciar." % area_label)
	if _fade != null:
		var tween := create_tween()
		tween.tween_property(_fade, "color", Color(0.18, 0.01, 0.01, 0.28), 0.6)


func on_battery_taken(_index: int, _who: Node) -> void:
	notify("BATERÍA RECUPERADA")


func on_extraction_started() -> void:
	_extraction_busy = true
	Audio.play_sfx("deliver", -10.0, 0.9)
	if hud != null:
		hud.set_status("EXTRACCIÓN INICIADA · PERMANECÉ EN LA ZONA")
	notify("EXTRACCIÓN INICIADA")


func on_extraction_progress(stage: String, seconds_left: float) -> void:
	if state != State.PLAYING:
		return
	_extraction_busy = true
	var labels := {
		"activando": "VALIDANDO",
		"apertura": "ABRIENDO SALIDA",
		"espera": "ESPERANDO",
		"cierre": "CERRANDO",
		"viaje": "VIAJE",
		"llegada": "CONFIRMANDO",
	}
	var label: String = labels.get(stage, stage.to_upper())
	if hud != null:
		hud.set_status("EXTRACCIÓN · %s · %.1f s" % [label, maxf(0.0, seconds_left)])


func on_extraction_cancelled() -> void:
	_extraction_busy = false
	notify("EXTRACCIÓN CANCELADA · VOLVÉ A LA ZONA")


func on_extraction_completed(delivered_loot: int) -> void:
	if state != State.PLAYING:
		return
	state = State.WON
	_extraction_busy = false
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	Audio.play_sfx("win", -8.0)
	if inventory_ui != null:
		inventory_ui.close()
	if hud != null:
		hud.show_end("EXTRACCIÓN COMPLETADA", "Núcleo asegurado · %d objeto(s) válido(s)" % delivered_loot)
	if _fade != null:
		var tween := create_tween()
		tween.tween_property(_fade, "color", Color(0.005, 0.09, 0.03, 0.30), 0.8)


func transition_to_reception(who: Node) -> void:
	if _transitioning or state != State.PLAYING:
		return
	var target := who as FMPlayer
	if target == null:
		return
	_transitioning = true
	state = State.TRANSITION
	if hud != null:
		hud.set_status("ENLACE DE SERVICIO · RECEPCIÓN")
	var out := create_tween()
	out.tween_property(_fade, "color:a", 1.0, 0.45)
	await out.finished
	target.global_position = RECEPTION_SPAWN
	target.rotation.y = RECEPTION_SPAWN_YAW
	target.velocity = Vector3.ZERO
	target._pitch = 0.0
	target.camera.rotation.x = 0.0
	target.hidden = false
	target.collision_layer = 2
	target.collision_mask = 1
	world_env.environment = reception_environment
	current_area = "RECEPTION"
	if watcher != null and is_instance_valid(watcher):
		if reception_watcher_enabled:
			_watcher_suspended = false
			watcher.activate_in_sector(RECEPTION_WATCHER_SPAWN, _reception_watcher_patrol(), RECEPTION_WATCHER_YAW)
		else:
			_watcher_suspended = true
			watcher.set_physics_process(false)
	if hud != null:
		hud.set_objective("LLEVAR EL NÚCLEO A EXTRACCIÓN", "Recepción · nivel 1 · ala sur")
	notify("RECEPCIÓN · BUSCÁ LA ZONA DE EXTRACCIÓN")
	await get_tree().create_timer(0.15).timeout
	var in_tween := create_tween()
	in_tween.tween_property(_fade, "color:a", 0.0, 0.65)
	await in_tween.finished
	state = State.PLAYING
	_transitioning = false


func clamp_player(who: FMPlayer) -> void:
	if who == null or not is_instance_valid(who):
		return
	var pos := who.global_position
	if current_area == "Z10":
		if pos.x < 39.2 or pos.x > 71.2 or pos.z < -31.4 or pos.z > -6.6:
			_respawn_player()
	elif current_area == "RECEPTION":
		if pos.x < -111.2 or pos.x > -69.0 or pos.z < 3.2 or pos.z > 41.2:
			_respawn_player()


func _respawn_player() -> void:
	if player == null or not is_instance_valid(player):
		return
	var spawn := RECEPTION_SPAWN if current_area == "RECEPTION" else Z10_SPAWN
	player.global_position = spawn
	player.velocity = Vector3.ZERO
	notify("POSICIÓN RECUPERADA · %s" % current_area)


func is_watcher_suspended() -> bool:
	return _watcher_suspended
