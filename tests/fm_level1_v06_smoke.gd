extends Node

## Prueba de humo del esqueleto técnico del Nivel 1 V06.
## godot --headless --path . tests/fm_level1_v06_smoke.tscn
##
## Comprueba:
##   - carga de la escena y de los quince sectores (cinco existentes, el
##     pasillo de servicio corredor–Vestuarios y las nueve salas blockout,
##     incluido el pasillo de acceso a Seguridad);
##   - raíces de sector y mallas presentes;
##   - colisiones construidas por sector y suelo bajo el spawn;
##   - salas blockout: AABB exacta, colisión, sonda de suelo, una única luz
##     de emergencia propia por sala, identidad y estado diferenciados;
##   - deduplicación de las cinco mallas de blockout_warehouse.glb que ya
##     existen en Z10, sin borrar nodos ni alterar el volumen físico;
##   - resoluciones documentadas: pasillo corredor–Vestuarios cerrado y
##     transitable, mesetas inferiores de escaleras seguras y puertas de
##     2,44 m con enlaces de navegación;
##   - pasillo corredor–Vestuarios: suelo, muro este, muro oeste, techo y
##     recorrido real a pie desde Z10 hasta Vestuarios;
##   - puertas Aseo/E1/E2/Vestuarios/Control: seis NavigationLink3D de capa 1
##     y rutas reales que terminan dentro de cada sala;
##   - escaleras: mesetas inferiores con suelo, zona segura de respawn,
##     caminata real sobre la meseta y caída fuera de zona que sí respawnea;
##   - jugador sobre el suelo y cámara activa;
##   - segundo Vigilante confinado en Seguridad, con patrulla válida y
##     movimiento real sobre la malla principal;
##   - captura única a través del mismo on_player_caught del nivel;
##   - avance real de al menos 10 m sin teletransporte ni respawn;
##   - AABB del pasillo de acceso y solape con Corredor y Seguridad;
##   - recorrido real corredor → pasillo de acceso (≥5 m) sin caída;
##   - compuerta R21C: bloqueo cerrado, prompt, apertura, paso real a
##     Seguridad, cierre y bloqueo de nuevo;
##   - compuertas runtime de Z10 y Recepción: vano, colisión, prompt,
##     apertura/cierre, ruido y negativa a cerrar con el jugador dentro;
##   - recursos requeridos presentes;
##   - cierre limpio.

const SCENE_PATH := "res://scenes/fm/level1_v06.tscn"
const SECTOR_IDS: Array[String] = [
	"Z10", "Reception", "Security", "Corridor", "SecurityAccess",
	"LockersCorridor", "Control", "Lockers", "Warehouse", "Maintenance",
	"Offices", "Restroom", "StairsMain", "StairsE1", "StairsE2",
]
const BLOCKOUT_IDS: Array[String] = [
	"Control", "Lockers", "Warehouse", "Maintenance", "Offices",
	"Restroom", "StairsMain", "StairsE1", "StairsE2",
]
## Raíz, luz, AABB, recuentos y sonda de suelo de cada sala blockout. Los
## valores salen de docs/fm_blockout_rooms_export.json y de la escena ya
## montada; la sonda cae en el centro útil de la losa, nunca en un foso.
const BLOCKOUT_EXPECT := {
	"Control": {
		"art": "Sectors/ControlArt", "light": "Emerg_Control",
		"light_pos": Vector3(-91.5, 3.5, -50.0),
		"aabb_pos": Vector3(-105.15, -0.2, -60.15),
		"aabb_size": Vector3(28.33, 6.2, 24.15),
		"meshes": 114, "colliders": 71,
		"floor": Vector3(-91.5, 1.4, -50.0),
		"title": "CONTROL DE ACCESO", "state": "BLOCKOUT · FILTRO DE ACCESO",
	},
	"Lockers": {
		"art": "Sectors/LockersArt", "light": "Emerg_Lockers",
		"light_pos": Vector3(44.5, 3.2, -52.0),
		"aabb_pos": Vector3(29.804, -0.2, -64.15),
		"aabb_size": Vector3(30.346, 4.7, 24.33),
		"meshes": 131, "colliders": 104,
		"floor": Vector3(44.5, 1.4, -52.0),
		"title": "VESTUARIOS", "state": "BLOCKOUT · TAQUILLAS Y CAMBIO",
	},
	"Warehouse": {
		"art": "Sectors/WarehouseArt", "light": "Emerg_Warehouse",
		"light_pos": Vector3(90.0, 4.7, -23.0),
		"aabb_pos": Vector3(61.8, -0.2, -38.15),
		"aabb_size": Vector3(48.38, 6.2, 34.15),
		"meshes": 143, "colliders": 84,
		"floor": Vector3(90.0, 1.4, -23.0),
		"title": "ALMACÉN / SUMINISTROS", "state": "BLOCKOUT · SUMINISTROS Y CARGA",
	},
	"Maintenance": {
		"art": "Sectors/MaintenanceArt", "light": "Emerg_Maintenance",
		"light_pos": Vector3(84.0, 4.7, 28.0),
		"aabb_pos": Vector3(55.85, -0.2, 4.0),
		"aabb_size": Vector3(56.33, 6.2, 44.15),
		"meshes": 145, "colliders": 102,
		"floor": Vector3(84.0, 1.4, 28.0),
		"title": "MANTENIMIENTO", "state": "BLOCKOUT · INFRAESTRUCTURA",
	},
	"Offices": {
		"art": "Sectors/OfficesArt", "light": "Emerg_Offices",
		"light_pos": Vector3(-7.5, 3.3, -50.0),
		"aabb_pos": Vector3(-30.15, -0.2, -70.15),
		"aabb_size": Vector3(45.34, 4.7, 66.15),
		"meshes": 292, "colliders": 167,
		"floor": Vector3(-7.5, 1.4, -50.0),
		"title": "OFICINAS / ADMINISTRACIÓN", "state": "BLOCKOUT · ADMINISTRACIÓN",
	},
	"Restroom": {
		"art": "Sectors/RestroomArt", "light": "Emerg_Restroom",
		"light_pos": Vector3(24.0, 3.0, -50.0),
		"aabb_pos": Vector3(15.0, -0.2, -58.15),
		"aabb_size": Vector3(15.0, 4.2, 16.3),
		"meshes": 45, "colliders": 20,
		"floor": Vector3(24.0, 1.4, -50.0),
		"title": "ASEO DE PLANTA", "state": "BLOCKOUT · ASEO DE PLANTA",
	},
	"StairsMain": {
		"art": "Sectors/StairsMainArt", "light": "Emerg_StairsMain",
		"light_pos": Vector3(4.0, 3.4, 40.0),
		"aabb_pos": Vector3(-12.15, -4.8, 1.9),
		"aabb_size": Vector3(20.3, 11.8, 48.25),
		"meshes": 68, "colliders": 51,
		"floor": Vector3(4.0, 1.4, 40.0),
		"title": "ESCALERAS PRINCIPALES", "state": "BLOCKOUT · NÚCLEO VERTICAL",
	},
	"StairsE1": {
		"art": "Sectors/StairsE1Art", "light": "Emerg_StairsE1",
		"light_pos": Vector3(118.6, 2.9, -17.0),
		"aabb_pos": Vector3(110.0, -4.8, -26.15),
		"aabb_size": Vector3(10.15, 10.8, 18.3),
		"meshes": 48, "colliders": 34,
		"floor": Vector3(118.6, 1.4, -17.0),
		"title": "ESCALERA DE EMERGENCIA E1", "state": "BLOCKOUT · SALIDA E1",
	},
	"StairsE2": {
		"art": "Sectors/StairsE2Art", "light": "Emerg_StairsE2",
		"light_pos": Vector3(120.6, 2.9, 35.0),
		"aabb_pos": Vector3(112.0, -4.8, 25.85),
		"aabb_size": Vector3(10.15, 10.8, 18.3),
		"meshes": 48, "colliders": 34,
		"floor": Vector3(120.6, 1.4, 35.0),
		"title": "ESCALERA DE EMERGENCIA E2", "state": "BLOCKOUT · SALIDA E2",
	},
}
const REQUIRED_RESOURCES := [
	"res://scenes/fm/level1_v06.tscn",
	"res://scripts/fm/fm_level1_v06.gd",
	"res://scripts/fm/fm_security_hatch.gd",
	"res://scenes/fm/fm_z10_art_r8.tscn",
	"res://scenes/fm/fm_reception_art_r9.tscn",
	"res://scenes/fm/fm_security_art.tscn",
	"res://scenes/fm/fm_corridor_art.tscn",
	"res://scenes/fm/fm_security_access_art.tscn",
	"res://scenes/fm/fm_blockout_control_art.tscn",
	"res://scenes/fm/fm_blockout_lockers_art.tscn",
	"res://scenes/fm/fm_blockout_warehouse_art.tscn",
	"res://scenes/fm/fm_blockout_maintenance_art.tscn",
	"res://scenes/fm/fm_blockout_offices_art.tscn",
	"res://scenes/fm/fm_blockout_restroom_art.tscn",
	"res://scenes/fm/fm_blockout_stairs_main_art.tscn",
	"res://scenes/fm/fm_blockout_stairs_e1_art.tscn",
	"res://scenes/fm/fm_blockout_stairs_e2_art.tscn",
	"res://scenes/fm/fm_lockers_corridor_art.tscn",
	"res://assets/models/fm/z10_sector.glb",
	"res://assets/models/fm/reception_sector.glb",
	"res://assets/models/fm/security_sector.glb",
	"res://assets/models/fm/corridor_sector.glb",
	"res://assets/models/fm/security_access_sector.glb",
	"res://assets/models/fm/blockout_control.glb",
	"res://assets/models/fm/blockout_lockers.glb",
	"res://assets/models/fm/blockout_warehouse.glb",
	"res://assets/models/fm/blockout_maintenance.glb",
	"res://assets/models/fm/blockout_offices.glb",
	"res://assets/models/fm/blockout_restroom.glb",
	"res://assets/models/fm/blockout_stairs_main.glb",
	"res://assets/models/fm/blockout_stairs_e1.glb",
	"res://assets/models/fm/blockout_stairs_e2.glb",
	"res://assets/models/fm/lockers_corridor_kit.glb",
]
const TARGET_X := 52.6
const TARGET_Z := -21.4
const MIN_ADVANCE := 10.0
const SECURITY_ACCESS_POS := Vector3(-71.0, -0.2, -11.8)
const SECURITY_ACCESS_SIZE := Vector3(34.4, 2.6, 7.8)
const AABB_TOL := 0.02
const ACCESS_START := Vector3(-37.45, 0.12, -2.8)
const ACCESS_MIN_ADVANCE := 5.0

var scene
var passes := 0
var fails := 0


func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	_release_movement()

	for path in REQUIRED_RESOURCES:
		_check("resource_%s" % path.get_file(), ResourceLoader.exists(path))

	var packed := load(SCENE_PATH) as PackedScene
	_check("scene_load", packed != null)
	if packed == null:
		_finish()
		return

	scene = packed.instantiate()
	add_child(scene)
	var guard := 0
	while not scene.level_ready and guard < 3600:
		await get_tree().process_frame
		guard += 1
	if not scene.level_ready:
		_fail("level_ready (guard=%d)" % guard)
		_finish()
		return

	if scene.watcher != null and is_instance_valid(scene.watcher):
		scene.watcher.set_physics_process(false)
	# El segundo Vigilante también se suspende: la prueba recorre el pasillo y
	# la compuerta de Seguridad, y no debe perseguir/capturar al jugador desde
	# el interior de la sala durante esos checks.
	if scene.security_watcher != null and is_instance_valid(scene.security_watcher):
		scene.security_watcher.set_physics_process(false)
	await _wait(0.8)

	_check("sector_count", scene.sector_roots.size() == 15)
	for id in SECTOR_IDS:
		var root := scene.sector_roots.get(id) as Node3D
		_check("sector_%s_root" % id, root != null and is_instance_valid(root) and root.is_inside_tree())
		_check("sector_%s_aligned" % id, root != null and root.global_position.length() < 0.01)
		_check("sector_%s_meshes" % id, scene.get_sector_mesh_count(id) > 0)
		_check("sector_%s_colliders" % id, int(scene.collider_counts.get(id, 0)) > 0)
	_check("lights", scene.get_light_count() > 20)
	_check("environment", scene.world_env != null and scene.world_env.environment != null)
	_check("hud", scene.hud != null and is_instance_valid(scene.hud))
	_check("watcher", scene.watcher != null and is_instance_valid(scene.watcher))
	_check("security_watcher", scene.security_watcher != null
		and is_instance_valid(scene.security_watcher))
	_check("security_hatch_closed_on_load", scene.security_hatch != null
		and is_instance_valid(scene.security_hatch) and scene.security_hatch.is_closed())

	# ------------------------------------------------------------------
	# Navegación: malla principal del Vigilante (capa 1) y malla reducida
	# del pasillo de servicio (capa 2), con enlaces de entrada y compuerta.
	# ------------------------------------------------------------------
	var nav_map: RID = scene.get_world_3d().navigation_map
	await _sync_nav(nav_map, 6)
	var nav_regions := NavigationServer3D.map_get_regions(nav_map)
	print("FM_LEVEL1_V06_NAV main_polys=%d service_polys=%d bake_ms=%d/%d regions=%d layers=%d/%d" % [
		scene.get_nav_main_polygon_count(), scene.get_nav_service_polygon_count(),
		scene.get_nav_bake_ms(), scene.get_nav_service_bake_ms(), nav_regions.size(),
		scene.nav_main_region.navigation_layers if scene.nav_main_region != null else -1,
		scene.nav_service_region.navigation_layers if scene.nav_service_region != null else -1,
	])
	_check("nav_main_region", scene.nav_main_region != null
		and is_instance_valid(scene.nav_main_region)
		and scene.nav_main_region.enabled
		and scene.nav_main_region.navigation_mesh != null)
	_check("nav_service_region", scene.nav_service_region != null
		and is_instance_valid(scene.nav_service_region)
		and scene.nav_service_region.enabled
		and scene.nav_service_region.navigation_mesh != null)
	_check("nav_main_polygons", scene.get_nav_main_polygon_count() > 0)
	_check("nav_service_polygons", scene.get_nav_service_polygon_count() > 0)
	_check("nav_map_regions", nav_regions.size() == 2)
	_check("nav_layers", scene.nav_main_region != null and scene.nav_service_region != null
		and scene.nav_main_region.navigation_layers == 3
		and scene.nav_service_region.navigation_layers == 2)
	_check("nav_watcher_uses_navigation", scene.watcher != null and scene.watcher.use_navigation)
	var watcher_agent := scene.watcher.get_node_or_null("NavigationAgent") as NavigationAgent3D
	_check("nav_watcher_layer", watcher_agent != null and watcher_agent.navigation_layers == 1)

	var nav_z10_corridor := _nav_path(nav_map, Vector3(42.2, 0.12, -22.0), Vector3(-13.0, 0.12, 0.0), 1)
	var nav_corridor_reception := _nav_path(nav_map, Vector3(-13.0, 0.12, 0.0), Vector3(-90.0, 0.12, 22.0), 1)
	var nav_z10_reception := _nav_path(nav_map, Vector3(42.2, 0.12, -22.0), Vector3(-90.0, 0.12, 22.0), 1)
	var nav_security_local := _nav_path(nav_map, Vector3(-88.0, 0.12, -28.0), Vector3(-90.0, 0.12, -18.0), 1)
	var nav_security_isolated := _nav_path(nav_map, Vector3(-13.0, 0.12, 0.0), Vector3(-88.0, 0.12, -23.0), 1)
	print("FM_LEVEL1_V06_NAV_PATHS z10_corridor=%d corridor_reception=%d z10_reception=%d security_local=%d security_blocked_end=%.2f" % [
		nav_z10_corridor.size(), nav_corridor_reception.size(), nav_z10_reception.size(),
		nav_security_local.size(),
		_path_end_distance(nav_security_isolated, Vector3(-88.0, 0.12, -23.0)),
	])
	_check("nav_path_z10_corridor", nav_z10_corridor.size() >= 3
		and _path_end_distance(nav_z10_corridor, Vector3(-13.0, 0.12, 0.0)) < 1.5)
	_check("nav_path_corridor_reception", nav_corridor_reception.size() >= 3
		and _path_end_distance(nav_corridor_reception, Vector3(-90.0, 0.12, 22.0)) < 1.5)
	_check("nav_path_z10_reception", nav_z10_reception.size() >= 10
		and _path_end_distance(nav_z10_reception, Vector3(-90.0, 0.12, 22.0)) < 1.5)
	_check("nav_path_security_local", nav_security_local.size() >= 3
		and _path_end_distance(nav_security_local, Vector3(-90.0, 0.12, -18.0)) < 1.5)
	# El oeste ya no está aislado: los enlaces de las puertas sur y norte de
	# Seguridad conectan el corredor con Seguridad y con el conector de Control.
	_check("nav_layer1_security_connected",
		_path_end_distance(nav_security_isolated, Vector3(-88.0, 0.12, -23.0)) < 2.0)
	var nav_corridor_control := _nav_path(nav_map, Vector3(-13.0, 0.12, 0.0), Vector3(-91.5, 0.12, -50.0), 1)
	_check("nav_layer1_corridor_control", nav_corridor_control.size() >= 10
		and _path_end_distance(nav_corridor_control, Vector3(-91.5, 0.12, -50.0)) < 2.0)
	var nav_mezzanine := _nav_path(nav_map, Vector3(88.35, 0.12, -20.0), Vector3(90.5, 2.72, -29.5), 1)
	print("FM_LEVEL1_V06_NAV_MEZZANINE size=%d end=%.2f" % [
		nav_mezzanine.size(),
		_path_end_distance(nav_mezzanine, Vector3(90.5, 2.72, -29.5)),
	])
	_check("nav_layer1_mezzanine", nav_mezzanine.size() >= 5
		and _path_end_distance(nav_mezzanine, Vector3(90.5, 2.72, -29.5)) < 1.5)

	# ------------------------------------------------------------------
	# Enlaces de puertas blockout de 2,44 m. El perfil del agente no encadena
	# ruta por el vano; los seis NavigationLink3D de capa 1 sí. Se comprueba
	# cada enlace y una ruta real de extremo a extremo a través de cada puerta.
	# ------------------------------------------------------------------
	_check("nav_door_links_count", scene.get_nav_door_link_count() == 8)
	var door_link_names: Array[String] = scene.get_nav_door_link_names()
	var unique_link_names := {}
	for link_name in door_link_names:
		unique_link_names[link_name] = true
	_check("nav_door_links_named", door_link_names.size() == 8 and unique_link_names.size() == 8)
	var door_links_ok := true
	for link in scene.nav_door_links:
		var door_link := link as NavigationLink3D
		door_links_ok = door_links_ok and door_link != null and is_instance_valid(door_link) \
			and door_link.enabled and door_link.bidirectional \
			and door_link.navigation_layers == 1
	_check("nav_door_links_layer1_enabled", door_links_ok)
	var door_routes := {
		"aseo": [Vector3(-7.5, 0.12, -50.0), Vector3(24.0, 0.12, -49.0)],
		"e1": [Vector3(90.0, 0.12, -23.0), Vector3(111.5, 0.12, -12.0)],
		"e2": [Vector3(84.0, 0.12, 28.0), Vector3(113.4, 0.12, 38.0)],
		"vestuarios": [Vector3(42.2, 0.12, -22.0), Vector3(43.0, 0.12, -42.0)],
		"control": [Vector3(-94.0, 0.12, -38.5), Vector3(-91.5, 0.12, -50.0)],
	}
	for route_id in door_routes:
		var route_from: Vector3 = door_routes[route_id][0]
		var route_to: Vector3 = door_routes[route_id][1]
		var door_path := _nav_path(nav_map, route_from, route_to, 1)
		var end_distance := _path_end_distance(door_path, route_to)
		print("FM_LEVEL1_V06_NAV_DOOR route=%s size=%d end=%.2f" % [
			String(route_id), door_path.size(), end_distance,
		])
		_check("nav_door_route_%s" % String(route_id), door_path.size() >= 5
			and end_distance < 1.5)

	# Validación con un NavigationAgent3D real: recorre cada enlace desde el
	# lado exterior hasta el interior. No se usa la IA del Vigilante para no
	# alterar su estado; el agente comparte mapa, capa y radio. En Godot 4.7
	# NavigationAgent3D es un Node: su posición es la del actor Node3D padre.
	var door_actor := Node3D.new()
	door_actor.name = "DoorLinkProbeActor"
	add_child(door_actor)
	var door_agent := NavigationAgent3D.new()
	door_agent.name = "DoorLinkProbeAgent"
	door_agent.navigation_layers = 1
	door_agent.path_desired_distance = 0.35
	door_agent.target_desired_distance = 0.60
	door_agent.radius = 0.45
	door_agent.avoidance_enabled = false
	door_actor.add_child(door_agent)
	await _sync_nav(nav_map, 2)
	var agent_crossings := 0
	for entry in scene.NAV_DOOR_LINKS:
		var link_start: Vector3 = entry["a"]
		var link_end: Vector3 = entry["b"]
		door_actor.global_position = link_start
		door_agent.target_position = link_end
		await get_tree().physics_frame
		await get_tree().physics_frame
		var reached := false
		for i in range(240):
			await get_tree().physics_frame
			var next_point := door_agent.get_next_path_position()
			door_actor.global_position = door_actor.global_position.move_toward(
				next_point, 2.6 * get_physics_process_delta_time()
			)
			if door_actor.global_position.distance_to(link_end) <= 0.75:
				reached = true
				break
		if reached:
			agent_crossings += 1
		print("FM_LEVEL1_V06_NAV_DOOR_AGENT door=%s reached=%s pos=%s target=%s" % [
			String(entry["door"]), str(reached), str(door_actor.global_position), str(link_end),
		])
	_check("nav_door_agent_crossings", agent_crossings == 8)
	door_actor.queue_free()
	await get_tree().process_frame

	var z10_box := _sector_aabb(scene.sector_roots.get("Z10") as Node3D)
	var reception_box := _sector_aabb(scene.sector_roots.get("Reception") as Node3D)
	var security_box := _sector_aabb(scene.sector_roots.get("Security") as Node3D)
	var corridor_box := _sector_aabb(scene.sector_roots.get("Corridor") as Node3D)
	var access_box := _sector_aabb(scene.sector_roots.get("SecurityAccess") as Node3D)
	print("FM_LEVEL1_V06_AABB Z10=%s Reception=%s Security=%s Corridor=%s Access=%s" % [
		str(z10_box), str(reception_box), str(security_box), str(corridor_box), str(access_box),
	])
	print("FM_LEVEL1_V06_SECURITY_GAP corridor_south=%.2f security_north=%.2f gap=%.2f" % [
		corridor_box.position.z, security_box.end.z,
		corridor_box.position.z - security_box.end.z,
	])
	_check("link_z10_corridor", z10_box.intersects(corridor_box))
	_check("link_corridor_reception", corridor_box.intersects(reception_box))

	# ------------------------------------------------------------------
	# Segundo Vigilante: confinado dentro de Seguridad. El principal no puede
	# cruzar el pasillo de servicio de 1.4 m, así que esta sala tiene su propio
	# Vigilante sobre la malla principal (capa 1).
	# ------------------------------------------------------------------
	var security_watcher: FMWatcher = scene.security_watcher
	var security_watcher_ready := security_watcher != null and is_instance_valid(security_watcher)
	_check("security_watcher_node", security_watcher_ready)
	if security_watcher_ready:
		_check("security_watcher_in_security",
			security_box.has_point(security_watcher.global_position))
		_check("security_watcher_navigation", security_watcher.use_navigation)
		var security_agent := security_watcher.get_node_or_null("NavigationAgent") as NavigationAgent3D
		_check("security_watcher_layer", security_agent != null
			and security_agent.navigation_layers == 1)
		_check("security_watcher_game", security_watcher.game == scene)
		var security_patrol: Array[Vector3] = security_watcher.patrol_points
		_check("security_watcher_patrol_size",
			security_patrol.size() == 9)
		var patrol_in_security := false
		var patrol_in_corridor := false
		for patrol_point in security_patrol:
			if security_box.has_point(patrol_point):
				patrol_in_security = true
			else:
				patrol_in_corridor = true
		_check("security_watcher_patrol_crosses_access",
			patrol_in_security and patrol_in_corridor)
		for i in range(security_patrol.size()):
			var patrol_from := security_patrol[i]
			var patrol_to := security_patrol[(i + 1) % security_patrol.size()]
			var patrol_path := _nav_path(nav_map, patrol_from, patrol_to, 1)
			var on_mesh := NavigationServer3D.map_get_closest_point(nav_map, patrol_from)
			var flat := Vector2(on_mesh.x - patrol_from.x, on_mesh.z - patrol_from.z).length()
			_check("security_watcher_path_%d" % i, patrol_path.size() >= 2
				and _path_end_distance(patrol_path, patrol_to) < 1.0 and flat <= 0.25)

	# ------------------------------------------------------------------
	# Pasillo de acceso Seguridad ↔ corredor principal.
	# ------------------------------------------------------------------
	var access_gap_corridor := corridor_box.position.z - access_box.end.z
	var access_gap_security := access_box.position.x - security_box.end.x
	print("FM_LEVEL1_V06_ACCESS aabb_pos=%s size=%s gap_corridor=%.2f gap_security=%.2f meshes=%d colliders=%d" % [
		str(access_box.position), str(access_box.size), access_gap_corridor,
		access_gap_security, scene.get_sector_mesh_count("SecurityAccess"),
		int(scene.collider_counts.get("SecurityAccess", 0)),
	])
	_check("access_meshes", scene.get_sector_mesh_count("SecurityAccess") == 11)
	_check("access_colliders", int(scene.collider_counts.get("SecurityAccess", 0)) > 0)
	_check("access_aabb_pos", access_box.position.distance_to(SECURITY_ACCESS_POS) <= AABB_TOL)
	_check("access_aabb_size", access_box.size.distance_to(SECURITY_ACCESS_SIZE) <= AABB_TOL)
	_check("link_corridor_access", corridor_box.intersects(access_box))
	_check("link_access_security", access_box.intersects(security_box))
	_check("access_no_gap_corridor", access_gap_corridor <= AABB_TOL)
	_check("access_no_gap_security", access_gap_security <= AABB_TOL)
	var access_light := scene.get_node_or_null("Sectors/SecurityAccessArt/Emerg_SecurityAccess") as OmniLight3D
	_check("access_emergency_light", access_light != null
		and access_light.global_position.distance_to(Vector3(-54.0, 2.05, -10.9)) <= 0.01
		and not access_light.shadow_enabled
		and access_light.light_energy <= 1.0)

	# Suelo físico continuo en las dos juntas (no solo solape de AABB).
	var floor_probes := {
		"corridor_side": Vector3(-37.45, 1.4, -3.7),
		"access_entry": Vector3(-37.45, 1.4, -4.4),
		"access_mid": Vector3(-55.0, 1.4, -10.9),
		"security_side": Vector3(-72.5, 1.4, -11.0),
	}
	for label in floor_probes:
		var origin: Vector3 = floor_probes[label]
		var hit := _ray(origin, origin + Vector3(0.0, -2.4, 0.0))
		var hit_y := 99.0
		if not hit.is_empty():
			var hit_pos: Vector3 = hit.get("position", Vector3.ZERO)
			hit_y = hit_pos.y
		print("FM_LEVEL1_V06_ACCESS_FLOOR %s hit=%s y=%.2f" % [label, str(not hit.is_empty()), hit_y])
		_check("access_floor_%s" % label, not hit.is_empty() and absf(hit_y) <= 0.10)

	# ------------------------------------------------------------------
	# Salas blockout V06 (9): raíz, AABB, colisión, suelo, luz de emergencia
	# propia e identidad/estado diferenciados. Vestuarios ya está vestido:
	# sus recuentos incluyen el GLB de arte y sus luces de sala; el resto
	# sigue siendo blockout declarado y sin props.
	# ------------------------------------------------------------------
	_check("blockout_count", BLOCKOUT_IDS.size() == 9)
	_check("alt_routes_root", scene.alt_routes_root != null
		and is_instance_valid(scene.alt_routes_root) and scene.alt_routes_root.is_inside_tree())
	_check("alt_routes_meshes", scene.get_alternate_routes_mesh_count() == 86)
	_check("alt_routes_colliders", scene.get_alternate_routes_collider_count() > 0)
	_check("blockout_ready", scene.get_blockout_ready_count() == 9)
	var blockout_titles := {}
	var blockout_states := {}
	var blockout_light_positions := {}
	var blockout_light_colors := {}
	var blockout_light_energies := {}
	for id in BLOCKOUT_IDS:
		var expected: Dictionary = BLOCKOUT_EXPECT[id]
		var art_root := scene.get_node_or_null(String(expected["art"])) as Node3D
		_check("blockout_%s_art_root" % id, art_root != null
			and is_instance_valid(art_root) and art_root.is_inside_tree())
		var art_lights: Array[Node] = []
		if art_root != null:
			art_lights = art_root.find_children("*", "Light3D", true, false)
		var light: OmniLight3D = null
		if id == "Lockers" or id == "Control" or id == "Warehouse" or id == "Maintenance" or id == "Offices" or id == "Restroom" or id == "StairsMain" or id == "StairsE1" or id == "StairsE2":
			# Vestuarios, Control y Almacén tienen luces de sala además de la
			# de emergencia; la unicidad se sigue midiendo sobre la emergencia.
			_check("blockout_%s_art_lights" % id, art_lights.size() >= 1)
			light = art_root.find_child(String(expected["light"]), true, false) as OmniLight3D
		else:
			_check("blockout_%s_single_light" % id, art_lights.size() == 1)
			if art_lights.size() == 1:
				light = art_lights[0] as OmniLight3D
		var light_pos: Vector3 = expected["light_pos"]
		_check("blockout_%s_light" % id, light != null and is_instance_valid(light)
			and light.global_position.distance_to(light_pos) <= 0.01
			and not light.shadow_enabled and light.light_energy <= 1.0
			and light.omni_range <= 12.0)
		if light != null:
			blockout_light_positions[light.global_position.snapped(Vector3.ONE * 0.001)] = true
			blockout_light_colors[Vector3(
				light.light_color.r, light.light_color.g, light.light_color.b
			)] = true
			blockout_light_energies[snappedf(light.light_energy, 0.001)] = true

		var blockout_root := scene.sector_roots.get(id) as Node3D
		var blockout_box := _sector_aabb(blockout_root)
		var expected_pos: Vector3 = expected["aabb_pos"]
		var expected_size: Vector3 = expected["aabb_size"]
		_check("blockout_%s_aabb_pos" % id,
			blockout_box.position.distance_to(expected_pos) <= AABB_TOL)
		_check("blockout_%s_aabb_size" % id,
			blockout_box.size.distance_to(expected_size) <= AABB_TOL)
		_check("blockout_%s_meshes" % id,
			scene.get_sector_mesh_count(id) == int(expected["meshes"]))
		_check("blockout_%s_colliders" % id,
			int(scene.collider_counts.get(id, 0)) == int(expected["colliders"]))
		var context: Dictionary = scene.get_sector_context(id)
		_check("blockout_%s_context" % id, not context.is_empty()
			and String(context.get("title", "")) == String(expected["title"])
			and String(context.get("function", "")).length() > 20
			and String(context.get("state", "")) == String(expected["state"])
			and String(context.get("hud", "")).length() > 5)
		blockout_titles[String(context.get("title", ""))] = true
		blockout_states[String(context.get("state", ""))] = true
		var floor_probe: Vector3 = expected["floor"]
		var floor_hit := _ray(floor_probe, floor_probe + Vector3(0.0, -2.4, 0.0))
		var floor_y := 99.0
		if not floor_hit.is_empty():
			floor_y = (floor_hit.get("position", Vector3.ZERO) as Vector3).y
		print("FM_LEVEL1_V06_BLOCKOUT %s meshes=%d colliders=%d aabb=%s light=%s floor_y=%.2f state=%s" % [
			id, scene.get_sector_mesh_count(id), int(scene.collider_counts.get(id, 0)),
			str(blockout_box), str(light != null), floor_y, String(context.get("state", "")),
		])
		_check("blockout_%s_floor" % id, not floor_hit.is_empty() and absf(floor_y) <= 0.10)

	_check("blockout_titles_unique", blockout_titles.size() == 9)
	_check("blockout_states_unique", blockout_states.size() == 9)
	_check("blockout_light_positions_unique", blockout_light_positions.size() == 9)
	_check("blockout_light_colors_unique", blockout_light_colors.size() == 9)
	_check("blockout_light_energies_unique", blockout_light_energies.size() == 9)

	# Deduplicación: blockout_warehouse.glb repite el ServiceLink y el muro
	# oeste que ya están en Z10. Se ocultan solo en Almacén antes de fusionar;
	# el volumen físico no cambia porque las colisiones se construyen antes.
	var duplicates: Array = scene.get_hidden_duplicate_meshes()
	_check("blockout_duplicates_reported", duplicates.size() == 5)
	var warehouse_root := scene.sector_roots.get("Warehouse") as Node3D
	for mesh_name in duplicates:
		var duplicate: MeshInstance3D = null
		if warehouse_root != null:
			duplicate = warehouse_root.find_child(String(mesh_name), true, false) as MeshInstance3D
		_check("blockout_dup_%s_hidden" % String(mesh_name),
			duplicate != null and not duplicate.visible)
	var warehouse_merge: Dictionary = scene.merge_stats.get("Warehouse", {})
	# El sector tiene además otras mallas invisibles del shell (columnas y
	# puertas ocultas por el arte), así que el total puede superar 5. Lo que
	# importa es que las cinco copias de Z10 queden fuera de la fusión; su
	# visibilidad se comprueba arriba, nombre por nombre.
	_check("blockout_duplicates_skipped_from_merge",
		int(warehouse_merge.get("skipped_meshes", 0)) >= 5)

	# Resoluciones documentadas. Ya no hay huecos sin rellenar: cada registro
	# declara cómo se resolvió el bloqueo y con qué prueba real se verifica.
	_check("blockout_blockers_resolved", scene.get_blockout_blockers().is_empty())
	var resolutions: Array = scene.get_blockout_resolutions()
	_check("blockout_resolutions_count", resolutions.size() == 3)
	for resolution_id in ["LockersCorridor", "StairsLowerLanding", "BlockoutDoorNavHeight"]:
		var resolution: Dictionary = scene.get_blockout_resolution(String(resolution_id))
		_check("blockout_resolution_%s" % String(resolution_id), not resolution.is_empty()
			and String(resolution.get("resolution", "")).length() > 60
			and String(resolution.get("verified_by", "")).length() > 10
			and not bool(resolution.get("geometry_invented", true)))

	# Pasillo corredor–Vestuarios: la geometría faltante se exportó del máster.
	# Se comprueba el volumen real del sector, el suelo en todo el tramo y los
	# tres cierres (muro oeste, muro central x=46 y techo) con rayos físicos.
	var corridor_sector := scene.sector_roots.get("LockersCorridor") as Node3D
	_check("lockers_corridor_root", corridor_sector != null
		and is_instance_valid(corridor_sector) and corridor_sector.is_inside_tree())
	_check("lockers_corridor_meshes", scene.get_sector_mesh_count("LockersCorridor") >= 10)
	_check("lockers_corridor_colliders", int(scene.collider_counts.get("LockersCorridor", 0)) >= 10)
	var lockers_corridor_box := _sector_aabb(corridor_sector)
	_check("lockers_corridor_aabb", lockers_corridor_box.position.distance_to(
		Vector3(39.85, -0.2, -39.98)) <= AABB_TOL
		and lockers_corridor_box.size.distance_to(Vector3(6.31, 4.4, 10.14)) <= 0.03)
	for corridor_z in [-30.5, -33.0, -35.0, -37.5, -39.5]:
		var corridor_floor_hit := _ray(
			Vector3(43.0, 1.5, corridor_z), Vector3(43.0, -0.8, corridor_z)
		)
		var corridor_floor_y := 99.0
		if not corridor_floor_hit.is_empty():
			corridor_floor_y = (corridor_floor_hit.get("position", Vector3.ZERO) as Vector3).y
		print("FM_LEVEL1_V06_LOCKERS_CORRIDOR_FLOOR z=%.1f hit=%s y=%.2f" % [
			corridor_z, str(not corridor_floor_hit.is_empty()), corridor_floor_y,
		])
		_check("lockers_corridor_floor_%.1f" % corridor_z,
			not corridor_floor_hit.is_empty() and absf(corridor_floor_y) <= 0.08)
	var corridor_wall_e := _ray(Vector3(43.0, 2.0, -35.0), Vector3(48.0, 2.0, -35.0))
	var corridor_wall_w := _ray(Vector3(43.0, 2.0, -35.0), Vector3(38.0, 2.0, -35.0))
	var corridor_ceiling := _ray(Vector3(43.0, 2.0, -35.0), Vector3(43.0, 5.0, -35.0))
	var corridor_wall_e_x: float = (corridor_wall_e.get("position", Vector3.ZERO) as Vector3).x
	var corridor_wall_w_x: float = (corridor_wall_w.get("position", Vector3.ZERO) as Vector3).x
	var corridor_ceiling_y: float = (corridor_ceiling.get("position", Vector3.ZERO) as Vector3).y
	print("FM_LEVEL1_V06_LOCKERS_CORRIDOR_CLOSURE east_x=%.2f west_x=%.2f ceiling_y=%.2f" % [
		corridor_wall_e_x, corridor_wall_w_x, corridor_ceiling_y,
	])
	_check("lockers_corridor_wall_east", not corridor_wall_e.is_empty()
		and absf(corridor_wall_e_x - 45.84) <= 0.25)
	_check("lockers_corridor_wall_west", not corridor_wall_w.is_empty()
		and absf(corridor_wall_w_x - 40.15) <= 0.25)
	_check("lockers_corridor_ceiling", not corridor_ceiling.is_empty()
		and absf(corridor_ceiling_y - 3.99) <= 0.10)

	# El máster tiene un mostrador de escotilla ya existente en el lado de
	# Seguridad (R21C_HATCH_Counter, y=0..1.05). Se registra el AABB original;
	# la compuerta runtime y el paso real se comprueban más abajo.
	var security_root := scene.sector_roots.get("Security") as Node3D
	var hatch_counter: MeshInstance3D = null
	if security_root != null:
		hatch_counter = security_root.find_child("R21C_HATCH_Counter", true, false) as MeshInstance3D
	if hatch_counter != null and hatch_counter.mesh != null:
		var hatch_box: AABB = hatch_counter.global_transform * hatch_counter.get_aabb()
		print("FM_LEVEL1_V06_ACCESS_HATCH counter=%s blocked_floor_step=%.2f" % [
			str(hatch_box), hatch_box.end.y,
		])

	var player: FMPlayer = scene.player
	_check("player", player != null and is_instance_valid(player))
	if player == null:
		_finish()
		return
	_check("player_camera", player.camera != null and player.camera.current)
	_check("player_floor", player.is_on_floor())
	_check("spawn_z10", player.global_position.x > 39.0 and player.global_position.x < 70.5 and player.global_position.z < -5.0)
	_check("player_y", absf(player.global_position.y) < 0.30)

	var start: Vector3 = player.global_position
	var target := Vector3(TARGET_X, 0.12, TARGET_Z)
	var prev: Vector3 = start
	var max_step := 0.0
	var path_length := 0.0
	var elapsed := 0.0
	var stuck := 0.0
	Input.action_press("move_up")
	while elapsed < 8.0:
		var offset := target - player.global_position
		offset.y = 0.0
		if offset.length() < 0.45:
			break
		player.rotation.y = atan2(-offset.x, -offset.z)
		await get_tree().physics_frame
		var current: Vector3 = player.global_position
		var delta: float = prev.distance_to(current)
		max_step = maxf(max_step, delta)
		path_length += delta
		if delta < 0.004:
			stuck += get_physics_process_delta_time()
		else:
			stuck = 0.0
		if stuck > 2.5:
			break
		prev = current
		elapsed += get_physics_process_delta_time()
	Input.action_release("move_up")
	await get_tree().physics_frame

	var advanced: float = start.distance_to(player.global_position)
	print("FM_LEVEL1_V06_MOVE start=%s end=%s advanced=%.2f path=%.2f max_step=%.3f respawns=%d state=%d floor=%s" % [
		str(start), str(player.global_position), advanced, path_length, max_step,
		scene.respawn_count, int(scene.state), str(player.is_on_floor()),
	])
	_check("advance_10m", advanced >= MIN_ADVANCE)
	_check("path_10m", path_length >= MIN_ADVANCE)
	_check("no_teleport", max_step < 0.75)
	_check("no_respawn", scene.respawn_count == 0)
	_check("playing", int(scene.state) == 0)
	_check("grounded_after_move", player.is_on_floor())
	_check("inside_geometry", player.global_position.y > -1.0)

	# ------------------------------------------------------------------
	# Recorrido real corredor → pasillo de acceso → hacia Seguridad.
	# Sin teletransporte: entrada por la puerta del corredor, giro en la L y
	# 5+ m en el tramo largo en dirección a Seguridad.
	# ------------------------------------------------------------------
	player.global_position = ACCESS_START
	player.velocity = Vector3.ZERO
	player.rotation.y = 0.0
	player.camera.rotation.x = 0.0
	await get_tree().physics_frame
	await get_tree().physics_frame

	# La boca del pasillo de acceso tiene ahora una compuerta runtime. Se abre
	# con el contrato real del jugador antes de recorrer el pasillo.
	var access_gate: FMLevel1Gate = scene.get_gate("Access")
	_check("access_gate_present", access_gate != null and is_instance_valid(access_gate))
	if access_gate != null:
		_check("access_gate_closed", access_gate.is_closed())
		_check("access_gate_collision_closed", access_gate.get_enabled_collision_count() == 1)
		_check("access_gate_prompt_closed", access_gate.get_interaction_prompt().contains("ABRIR"))
		_check("access_gate_reachable", access_gate.can_interact(player))
		var access_gate_opened: bool = player._try_interactable()
		_check("access_gate_open_via_player", access_gate_opened)
		var access_gate_wait := 0.0
		while access_gate.is_moving and access_gate_wait < 3.0:
			await get_tree().process_frame
			access_gate_wait += get_process_delta_time()
		_check("access_gate_open_finished", access_gate.is_fully_open())
		_check("access_gate_shutter_lift", access_gate.get_shutter_lift() > access_gate.height * 0.9)
		_check("access_gate_prompt_open", access_gate.get_interaction_prompt().contains("CERRAR"))

	var access_route: Array[Vector3] = [
		Vector3(-37.45, 0.12, -10.9),
		Vector3(-44.5, 0.12, -10.9),
		Vector3(-72.5, 0.12, -10.9),
	]
	var access_index := 0
	var access_prev: Vector3 = player.global_position
	var access_max_step := 0.0
	var access_path := 0.0
	var access_elapsed := 0.0
	var access_stuck := 0.0
	Input.action_press("move_up")
	while access_elapsed < 20.0 and access_index < access_route.size():
		var aim: Vector3 = access_route[access_index] - player.global_position
		aim.y = 0.0
		if aim.length() < 0.45:
			access_index += 1
			continue
		player.rotation.y = atan2(-aim.x, -aim.z)
		await get_tree().physics_frame
		var current: Vector3 = player.global_position
		var step: float = access_prev.distance_to(current)
		access_max_step = maxf(access_max_step, step)
		access_path += step
		access_prev = current
		access_elapsed += get_physics_process_delta_time()
		if step < 0.004:
			access_stuck += get_physics_process_delta_time()
			if access_stuck > 2.5:
				break
		else:
			access_stuck = 0.0
	Input.action_release("move_up")
	await get_tree().physics_frame

	var access_advanced: float = ACCESS_START.distance_to(player.global_position)
	var access_south: float = ACCESS_START.z - player.global_position.z
	print("FM_LEVEL1_V06_ACCESS_MOVE start=%s end=%s advanced=%.2f toward_security=%.2f path=%.2f max_step=%.3f respawns=%d state=%d floor=%s y=%.3f waypoint=%d hatch_blocked=%s" % [
		str(ACCESS_START), str(player.global_position), access_advanced, access_south,
		access_path, access_max_step, scene.respawn_count, int(scene.state),
		str(player.is_on_floor()), player.global_position.y, access_index,
		str(player.global_position.x > -71.2),
	])
	_check("access_advance_5m", access_advanced >= ACCESS_MIN_ADVANCE)
	_check("access_toward_security", access_south >= ACCESS_MIN_ADVANCE and player.global_position.x < -40.0)
	_check("access_reaches_security_threshold", player.global_position.x <= -69.0)
	_check("access_no_teleport", access_max_step < 0.75)
	_check("access_no_respawn", scene.respawn_count == 0)
	_check("access_playing", int(scene.state) == 0)
	_check("access_grounded", player.is_on_floor())
	_check("access_inside_geometry", player.global_position.y > -0.5)
	var access_end_position: Vector3 = player.global_position

	# ------------------------------------------------------------------
	# Recorrido real corredor de Z10 → pasillo de servicio → Vestuarios.
	# Sin teletransporte dentro del pasillo: el jugador rodea la silla de Z10,
	# cruza el vano de z=-30,15 y baja hasta el vano de Vestuarios en z=-40,15.
	# ------------------------------------------------------------------
	player.global_position = Vector3(41.5, 0.12, -22.0)
	player.velocity = Vector3.ZERO
	player.rotation.y = PI
	await get_tree().physics_frame
	await get_tree().physics_frame
	var corridor_route: Array[Vector3] = [
		Vector3(41.5, 0.12, -27.0),
		Vector3(41.5, 0.12, -33.0),
		Vector3(43.0, 0.12, -37.0),
		Vector3(43.0, 0.12, -42.5),
	]
	var corridor_walk_path := 0.0
	var corridor_walk_max_step := 0.0
	for waypoint in corridor_route:
		var leg: Dictionary = await _walk_to(player, waypoint, 6.0)
		corridor_walk_path += float(leg.get("path", 0.0))
		corridor_walk_max_step = maxf(corridor_walk_max_step, float(leg.get("max_step", 0.0)))
	var corridor_end: Vector3 = player.global_position
	var corridor_context := ""
	player.global_position = Vector3(43.0, 0.12, -35.0)
	corridor_context = scene._context_status()
	player.global_position = corridor_end
	player.velocity = Vector3.ZERO
	await get_tree().physics_frame
	print("FM_LEVEL1_V06_LOCKERS_CORRIDOR_WALK end=%s path=%.2f max_step=%.3f respawns=%d floor=%s context=%s" % [
		str(corridor_end), corridor_walk_path, corridor_walk_max_step,
		scene.respawn_count, str(player.is_on_floor()), corridor_context,
	])
	_check("lockers_corridor_walk", corridor_end.z < -41.5
		and corridor_end.x > 40.0 and corridor_end.x < 46.2)
	_check("lockers_corridor_walk_path", corridor_walk_path >= 16.0)
	_check("lockers_corridor_walk_no_teleport", corridor_walk_max_step < 0.75)
	_check("lockers_corridor_walk_no_respawn", scene.respawn_count == 0)
	_check("lockers_corridor_walk_grounded", player.is_on_floor()
		and player.global_position.y > -0.4)
	_check("lockers_corridor_context", corridor_context.contains("PASILLO")
		and corridor_context.contains("VESTUARIOS"))

	# ------------------------------------------------------------------
	# Escaleras: las tres mesetas inferiores (y=-4,5) son zonas válidas.
	# Se comprueba el suelo real, la zona segura y que el respawn no salta al
	# llegar abajo; después se camina 1,8 m sobre la meseta principal. La
	# caída fuera de las cajas de escalera sigue recuperando al jugador.
	# ------------------------------------------------------------------
	_check("stairs_safe_zone_count", scene.get_stair_safe_zone_ids().size() == 3)
	var stair_landings := {
		"StairsMain": Vector3(-2.0, -4.2, 41.4),
		"StairsE1": Vector3(115.0, -4.2, -23.0),
		"StairsE2": Vector3(117.0, -4.2, 27.0),
	}
	for stair_id in stair_landings:
		var landing: Vector3 = stair_landings[stair_id]
		player.global_position = landing
		player.velocity = Vector3.ZERO
		for i in range(45):
			await get_tree().physics_frame
		var landing_hit := _ray(
			Vector3(landing.x, landing.y + 1.0, landing.z),
			Vector3(landing.x, landing.y - 1.4, landing.z)
		)
		var landing_y := 99.0
		if not landing_hit.is_empty():
			landing_y = (landing_hit.get("position", Vector3.ZERO) as Vector3).y
		print("FM_LEVEL1_V06_STAIRS_LANDING room=%s pos=%s floor_y=%.2f grounded=%s safe=%s respawns=%d" % [
			String(stair_id), str(player.global_position), landing_y,
			str(player.is_on_floor()), str(scene.is_in_stair_safe_zone(landing)),
			scene.respawn_count,
		])
		_check("stairs_%s_landing_floor" % String(stair_id),
			not landing_hit.is_empty() and absf(landing_y + 4.5) <= 0.10)
		_check("stairs_%s_landing_grounded" % String(stair_id),
			player.is_on_floor() and player.global_position.y > -4.7
			and player.global_position.y < -4.1)
		_check("stairs_%s_landing_no_respawn" % String(stair_id),
			scene.respawn_count == 0 and scene.is_in_stair_safe_zone(landing))
	_check("stairs_outside_not_safe",
		not scene.is_in_stair_safe_zone(Vector3(-2.0, -4.2, 20.0)))
	_check("stairs_landing_does_not_respawn",
		not scene._should_respawn(Vector3(-2.0, -4.4, 41.0)))
	_check("stairs_landing_near_bottom_does_not_respawn",
		not scene._should_respawn(Vector3(-2.0, -5.2, 41.0)))
	_check("stairs_outside_fall_respawns",
		scene._should_respawn(Vector3(-2.0, -4.2, 20.0)))
	player.global_position = Vector3(-2.0, -4.3, 41.4)
	player.velocity = Vector3.ZERO
	await get_tree().physics_frame
	await get_tree().physics_frame
	var landing_walk: Dictionary = await _walk_to(player, Vector3(-2.0, -4.3, 43.2), 3.0)
	for i in range(10):
		await get_tree().physics_frame
	print("FM_LEVEL1_V06_STAIRS_WALK end=%s path=%.2f respawns=%d floor=%s" % [
		str(landing_walk.get("end", Vector3.ZERO)), float(landing_walk.get("path", 0.0)),
		scene.respawn_count, str(player.is_on_floor()),
	])
	_check("stairs_main_landing_walk", float(landing_walk.get("path", 0.0)) >= 1.2
		and player.global_position.z >= 42.6)
	_check("stairs_main_landing_walk_no_respawn",
		scene.respawn_count == 0 and player.is_on_floor())
	var respawns_before_fall: int = scene.respawn_count
	player.global_position = Vector3(43.0, -6.0, -35.0)
	player.velocity = Vector3.ZERO
	scene.clamp_player(player)
	_check("stairs_fall_outside_zone_respawns",
		scene.respawn_count == respawns_before_fall + 1
		and player.global_position.distance_to(scene.Z10_SPAWN) < 0.2)
	scene.respawn_count = 0
	player.global_position = access_end_position
	player.velocity = Vector3.ZERO
	await get_tree().physics_frame
	await get_tree().physics_frame

	Input.action_release("move_up")

	# ------------------------------------------------------------------
	# Compuerta interactiva de la ventanilla de servicio de Seguridad.
	# El mostrador R21C_HATCH_Counter bloquea el hueco, pero el marco
	# (WindowFrame) tiene un travesaño inferior que también detiene la
	# cápsula. La compuerta mueve el conjunto bloqueante y desactiva solo
	# las colisiones de esas mallas cuando está completamente abierta.
	# ------------------------------------------------------------------
	var hatch: FMSecurityHatch = scene.security_hatch
	_check("security_hatch_present", hatch != null and is_instance_valid(hatch) and hatch.configured)
	if hatch == null or not hatch.configured:
		_fail("security_hatch_configured")
		await _cleanup()
		return

	_check("security_hatch_closed_before_open", hatch.is_closed())
	_check("security_hatch_collision_closed", hatch.get_collision_shape_count() >= 5
		and hatch.get_enabled_collision_count() == hatch.get_collision_shape_count())
	_check("security_hatch_blocks_before_open", player.global_position.x > -70.85)
	_check("security_hatch_prompt_visible", player.get_interaction_prompt().contains("ABRIR"))
	_check("security_hatch_prompt_contract", hatch.get_interaction_prompt().contains("ABRIR"))
	_check("security_hatch_reachable", hatch.can_interact(player))

	var opened: bool = player._try_interactable()
	_check("security_hatch_open_via_player", opened)
	var open_wait := 0.0
	while hatch.is_moving and open_wait < 3.0:
		await get_tree().process_frame
		open_wait += get_process_delta_time()
	print("FM_LEVEL1_V06_HATCH_OPEN open=%s lift=%.2f enabled=%d/%d wait=%.2f prompt=%s" % [
		str(hatch.is_fully_open()), hatch.get_mesh_lift(),
		hatch.get_enabled_collision_count(), hatch.get_collision_shape_count(),
		open_wait, hatch.get_interaction_prompt(),
	])
	_check("security_hatch_open_finished", hatch.is_fully_open())
	_check("security_hatch_open_lift", absf(hatch.get_mesh_lift() - hatch.open_lift) <= 0.03)
	_check("security_hatch_collision_open", hatch.get_enabled_collision_count() == 0)
	_check("security_hatch_open_prompt", hatch.get_interaction_prompt().contains("CERRAR"))

	await _sync_nav(nav_map, 4)
	var nav_hatch_open := _nav_path(nav_map, Vector3(-55.0, 0.12, -10.9), Vector3(-88.0, 0.12, -23.0), 2)
	print("FM_LEVEL1_V06_NAV_HATCH open_link=%s path=%d end_d=%.2f end=%s" % [
		str(scene.is_nav_hatch_link_enabled()), nav_hatch_open.size(),
		_path_end_distance(nav_hatch_open, Vector3(-88.0, 0.12, -23.0)),
		str(nav_hatch_open[nav_hatch_open.size() - 1]) if nav_hatch_open.size() > 0 else "none",
	])
	_check("nav_hatch_link_open", scene.is_nav_hatch_link_enabled())
	_check("nav_hatch_crossing_open", nav_hatch_open.size() >= 5
		and _path_end_distance(nav_hatch_open, Vector3(-88.0, 0.12, -23.0)) < 2.0)

	var pass_walk := await _walk_to(player, Vector3(-72.0, 0.12, -10.9), 3.0)
	var pass_end: Vector3 = pass_walk.get("end", Vector3.ZERO)
	print("FM_LEVEL1_V06_HATCH_PASS end=%s path=%.2f max_step=%.3f floor=%s respawns=%d" % [
		str(pass_end), float(pass_walk.get("path", 0.0)), float(pass_walk.get("max_step", 0.0)),
		str(player.is_on_floor()), scene.respawn_count,
	])
	_check("security_hatch_pass_threshold", pass_end.x < -70.85)
	_check("security_hatch_pass_into_security", pass_end.x < -71.45)
	_check("security_hatch_pass_no_teleport", float(pass_walk.get("max_step", 99.0)) < 0.75)
	_check("security_hatch_pass_no_respawn", scene.respawn_count == 0)
	_check("security_hatch_pass_grounded", player.is_on_floor())
	_check("security_hatch_close_guard_inside", not hatch.can_interact(player))

	var west_walk := await _walk_to(player, Vector3(-73.0, 0.12, -10.9), 3.0)
	var west_end: Vector3 = west_walk.get("end", Vector3.ZERO)
	print("FM_LEVEL1_V06_HATCH_WEST end=%s can_close=%s prompt=%s" % [
		str(west_end), str(hatch.can_interact(player)), player.get_interaction_prompt(),
	])
	_check("security_hatch_west_clear", west_end.x < -72.40)
	_check("security_hatch_close_reachable_west", hatch.can_interact(player))
	_check("security_hatch_close_prompt_west", player.get_interaction_prompt().contains("CERRAR"))

	var east_walk := await _walk_to(player, Vector3(-69.7, 0.12, -10.9), 4.0)
	var east_end: Vector3 = east_walk.get("end", Vector3.ZERO)
	print("FM_LEVEL1_V06_HATCH_EAST end=%s can_close=%s prompt=%s" % [
		str(east_end), str(hatch.can_interact(player)), player.get_interaction_prompt(),
	])
	_check("security_hatch_east_clear", east_end.x > -70.37)
	_check("security_hatch_close_reachable_east", hatch.can_interact(player))
	_check("security_hatch_close_prompt_east", player.get_interaction_prompt().contains("CERRAR"))

	var closed: bool = player._try_interactable()
	_check("security_hatch_close_via_player", closed)
	var close_wait := 0.0
	while hatch.is_moving and close_wait < 3.0:
		await get_tree().process_frame
		close_wait += get_process_delta_time()
	print("FM_LEVEL1_V06_HATCH_CLOSE closed=%s lift=%.2f enabled=%d/%d wait=%.2f prompt=%s" % [
		str(hatch.is_closed()), hatch.get_mesh_lift(),
		hatch.get_enabled_collision_count(), hatch.get_collision_shape_count(),
		close_wait, hatch.get_interaction_prompt(),
	])
	_check("security_hatch_closed_after_interact", hatch.is_closed())
	_check("security_hatch_closed_lift", absf(hatch.get_mesh_lift()) <= 0.03)
	_check("security_hatch_collision_closed_again", hatch.get_enabled_collision_count() == hatch.get_collision_shape_count())

	await _sync_nav(nav_map, 4)
	var nav_hatch_closed := _nav_path(nav_map, Vector3(-69.5, 0.12, -10.9), Vector3(-74.0, 0.12, -10.9), 2)
	var hatch_closed_length := _path_length(nav_hatch_closed)
	print("FM_LEVEL1_V06_NAV_HATCH closed_link=%s path=%d len=%.2f end_d=%.2f end=%s" % [
		str(scene.is_nav_hatch_link_enabled()), nav_hatch_closed.size(), hatch_closed_length,
		_path_end_distance(nav_hatch_closed, Vector3(-74.0, 0.12, -10.9)),
		str(nav_hatch_closed[nav_hatch_closed.size() - 1]) if nav_hatch_closed.size() > 0 else "none",
	])
	_check("nav_hatch_link_closed", not scene.is_nav_hatch_link_enabled())
	# La compuerta cerrada no debe ofrecer el atajo directo de ~4,5 m. Desde la
	# conectividad del vano sur, el mapa puede rodear por el conector principal,
	# pero ese recorrido es mucho más largo: el test mide el atajo, no la
	# reachability global de Seguridad.
	_check("nav_hatch_crossing_closed", nav_hatch_closed.is_empty() or hatch_closed_length > 12.0)

	var blocked_walk := await _walk_to(player, Vector3(-71.9, 0.12, -10.9), 3.0)
	var blocked_end: Vector3 = blocked_walk.get("end", Vector3.ZERO)
	print("FM_LEVEL1_V06_HATCH_BLOCKED end=%s path=%.2f max_step=%.3f floor=%s respawns=%d prompt=%s" % [
		str(blocked_end), float(blocked_walk.get("path", 0.0)), float(blocked_walk.get("max_step", 0.0)),
		str(player.is_on_floor()), scene.respawn_count, player.get_interaction_prompt(),
	])
	_check("security_hatch_blocks_again", blocked_end.x > -70.85)
	_check("security_hatch_blocks_again_no_teleport", float(blocked_walk.get("max_step", 99.0)) < 0.75)
	_check("security_hatch_blocks_again_no_respawn", scene.respawn_count == 0)
	_check("security_hatch_blocks_again_grounded", player.is_on_floor())
	_check("security_hatch_blocks_again_prompt", player.get_interaction_prompt().contains("ABRIR"))

	# ------------------------------------------------------------------
	# Compuertas runtime de los vanos anchos: Z10 y Recepción. Se comprueba
	# el contrato de interacción, la colisión física, la apertura/cierre y el
	# ruido de puerta contabilizado por el nivel.
	# ------------------------------------------------------------------
	var gate_ids: Array = scene.get_gate_ids()
	_check("gate_count", scene.level_gates.size() == 4)
	for expected_gate in ["Z10", "Reception_North", "Reception_Hall", "Access"]:
		_check("gate_%s_present" % expected_gate, gate_ids.has(expected_gate))

	var gate_z10: FMLevel1Gate = scene.get_gate("Z10")
	_check("gate_z10_configured", gate_z10 != null and is_instance_valid(gate_z10)
		and gate_z10.configured and gate_z10.is_in_group("fm_interactable"))
	if gate_z10 != null:
		_check("gate_z10_position",
			gate_z10.global_position.distance_to(Vector3(43.0, 0.0, -4.0)) <= 0.01)
		_check("gate_z10_closed_on_load", gate_z10.is_closed())
		_check("gate_z10_collision_body", gate_z10.get_collision_body() != null
			and gate_z10.get_enabled_collision_count() == 1)
		_check("gate_z10_prompt_closed", gate_z10.get_interaction_prompt().contains("ABRIR"))

		player.global_position = Vector3(43.0, 0.12, -6.0)
		player.velocity = Vector3.ZERO
		player.rotation.y = PI
		player.camera.rotation.x = 0.0
		await get_tree().physics_frame
		await get_tree().physics_frame
		_check("gate_z10_reachable", gate_z10.can_interact(player))
		player.global_position = Vector3(40.9, 0.12, -6.0)
		await get_tree().physics_frame
		_check("gate_z10_reachable_offcenter", gate_z10.can_interact(player))
		player.global_position = Vector3(43.0, 0.12, -6.0)
		await get_tree().physics_frame
		await get_tree().physics_frame
		_check("gate_z10_player_prompt", player.get_interaction_prompt().contains("ABRIR"))

		var ray_closed := PhysicsRayQueryParameters3D.create(
			Vector3(43.0, 1.20, -6.0), Vector3(43.0, 1.20, -2.0)
		)
		ray_closed.collision_mask = 1
		ray_closed.exclude = [player.get_rid()]
		var hit_closed: Dictionary = player.get_world_3d().direct_space_state.intersect_ray(ray_closed)
		_check("gate_z10_blocks_closed", not hit_closed.is_empty()
			and absf(hit_closed.position.z - (-4.0)) <= 0.35)

		var noise_before: int = scene.get_door_noise_count()
		var gate_opened: bool = player._try_interactable()
		_check("gate_z10_open_via_player", gate_opened and gate_z10.is_open)
		var gate_wait := 0.0
		while gate_z10.is_moving and gate_wait < 3.0:
			await get_tree().process_frame
			gate_wait += get_process_delta_time()
		_check("gate_z10_open_finished", gate_z10.is_fully_open())
		_check("gate_z10_shutter_lift", gate_z10.get_shutter_lift() > gate_z10.height * 0.9)
		_check("gate_z10_noise", scene.get_door_noise_count() > noise_before)
		_check("gate_z10_prompt_open", gate_z10.get_interaction_prompt().contains("CERRAR"))

		var ray_open := PhysicsRayQueryParameters3D.create(
			Vector3(43.0, 1.20, -6.0), Vector3(43.0, 1.20, -2.0)
		)
		ray_open.collision_mask = 1
		ray_open.exclude = [player.get_rid()]
		var hit_open: Dictionary = player.get_world_3d().direct_space_state.intersect_ray(ray_open)
		_check("gate_z10_clears_open", hit_open.is_empty())

		player.global_position = Vector3(43.0, 0.12, -4.0)
		await get_tree().physics_frame
		_check("gate_z10_refuses_close_inside", not gate_z10.can_interact(player))
		player.global_position = Vector3(43.0, 0.12, -6.0)
		await get_tree().physics_frame
		await get_tree().physics_frame
		var noise_before_close: int = scene.get_door_noise_count()
		var gate_closed: bool = player._try_interactable()
		_check("gate_z10_close_via_player", gate_closed and not gate_z10.is_open)
		gate_wait = 0.0
		while gate_z10.is_moving and gate_wait < 3.0:
			await get_tree().process_frame
			gate_wait += get_process_delta_time()
		_check("gate_z10_closed_again", gate_z10.is_closed())
		_check("gate_z10_close_noise", scene.get_door_noise_count() > noise_before_close)
		var hit_again: Dictionary = player.get_world_3d().direct_space_state.intersect_ray(ray_closed)
		_check("gate_z10_blocks_again", not hit_again.is_empty()
			and absf(hit_again.position.z - (-4.0)) <= 0.35)

		# Colisión real de movimiento: el jugador camina contra la compuerta
		# cerrada y no la atraviesa.
		player.global_position = Vector3(43.0, 0.12, -6.0)
		player.velocity = Vector3.ZERO
		player.rotation.y = PI
		await get_tree().physics_frame
		await get_tree().physics_frame
		Input.action_press("move_up")
		var blocked_elapsed := 0.0
		while blocked_elapsed < 1.4:
			await get_tree().physics_frame
			blocked_elapsed += get_physics_process_delta_time()
		Input.action_release("move_up")
		await get_tree().physics_frame
		_check("gate_z10_blocks_walk", player.global_position.z < -4.35)
		_check("gate_z10_walk_no_respawn", scene.respawn_count == 0)

	var gate_reception: FMLevel1Gate = scene.get_gate("Reception_North")
	_check("gate_reception_configured", gate_reception != null and is_instance_valid(gate_reception))
	if gate_reception != null:
		_check("gate_reception_position",
			gate_reception.global_position.distance_to(Vector3(-90.0, 0.0, 4.0)) <= 0.01)
		_check("gate_reception_closed", gate_reception.is_closed())
		player.global_position = Vector3(-90.0, 0.12, 1.6)
		player.velocity = Vector3.ZERO
		player.rotation.y = PI
		await get_tree().physics_frame
		await get_tree().physics_frame
		_check("gate_reception_reachable", gate_reception.can_interact(player))
		var reception_ray := PhysicsRayQueryParameters3D.create(
			Vector3(-90.0, 1.20, 1.6), Vector3(-90.0, 1.20, 6.0)
		)
		reception_ray.collision_mask = 1
		reception_ray.exclude = [player.get_rid()]
		var reception_hit: Dictionary = player.get_world_3d().direct_space_state.intersect_ray(reception_ray)
		_check("gate_reception_blocks_closed", not reception_hit.is_empty()
			and absf(reception_hit.position.z - 4.0) <= 0.35)
		var reception_opened: bool = player._try_interactable()
		var reception_wait := 0.0
		while gate_reception.is_moving and reception_wait < 3.0:
			await get_tree().process_frame
			reception_wait += get_process_delta_time()
		_check("gate_reception_open_via_player", reception_opened and gate_reception.is_fully_open())
		var reception_hit_open: Dictionary = player.get_world_3d().direct_space_state.intersect_ray(reception_ray)
		_check("gate_reception_clears_open", reception_hit_open.is_empty())
		var reception_closed: bool = player._try_interactable()
		reception_wait = 0.0
		while gate_reception.is_moving and reception_wait < 3.0:
			await get_tree().process_frame
			reception_wait += get_process_delta_time()
		_check("gate_reception_close_via_player",
			reception_closed and gate_reception.is_closed())
		player.global_position = Vector3(-93.1, 0.12, 1.6)
		await get_tree().physics_frame
		_check("gate_reception_reachable_offcenter", gate_reception.can_interact(player))

	var gate_hall: FMLevel1Gate = scene.get_gate("Reception_Hall")
	_check("gate_hall_configured", gate_hall != null and is_instance_valid(gate_hall)
		and gate_hall.is_closed())
	if gate_hall != null:
		_check("gate_hall_position",
			gate_hall.global_position.distance_to(Vector3(-90.0, 0.0, 8.0)) <= 0.01)
		player.global_position = Vector3(-90.0, 0.12, 6.0)
		player.velocity = Vector3.ZERO
		await get_tree().physics_frame
		await get_tree().physics_frame
		_check("gate_hall_reachable", gate_hall.can_interact(player))
		_check("gate_hall_prompt_closed", gate_hall.get_interaction_prompt().contains("ABRIR"))

	# ------------------------------------------------------------------
	# Patrulla real del Vigilante sobre la malla principal: path del agente,
	# desplazamiento efectivo y ausencia de atascos dentro de Z10.
	# ------------------------------------------------------------------
	await _sync_nav(nav_map, 4)
	var patrol_watcher: FMWatcher = scene.watcher
	patrol_watcher.activate_in_sector(Vector3(59.0, 0.12, -14.5), [
		Vector3(59.0, 0.12, -25.0),
		Vector3(45.0, 0.12, -25.0),
	])
	var patrol_start: Vector3 = patrol_watcher.global_position
	var patrol_prev := patrol_start
	var patrol_path := 0.0
	var patrol_max_step := 0.0
	var patrol_stuck := 0.0
	var patrol_elapsed := 0.0
	while patrol_elapsed < 5.0:
		await get_tree().physics_frame
		var current: Vector3 = patrol_watcher.global_position
		var step := patrol_prev.distance_to(current)
		patrol_path += step
		patrol_max_step = maxf(patrol_max_step, step)
		if step < 0.001:
			patrol_stuck += get_physics_process_delta_time()
		else:
			patrol_stuck = 0.0
		patrol_prev = current
		patrol_elapsed += get_physics_process_delta_time()
	var patrol_advanced := patrol_start.distance_to(patrol_watcher.global_position)
	var patrol_agent_path := patrol_watcher._agent.get_current_navigation_path()
	print("FM_LEVEL1_V06_NAV_PATROL start=%s end=%s advanced=%.2f path=%.2f max_step=%.3f stuck=%.2f agent_path=%d state=%d" % [
		str(patrol_start), str(patrol_watcher.global_position), patrol_advanced, patrol_path,
		patrol_max_step, patrol_stuck, patrol_agent_path.size(), int(patrol_watcher.state),
	])
	_check("nav_patrol_moves", patrol_advanced >= 2.0)
	_check("nav_patrol_path", patrol_path >= 2.0)
	_check("nav_patrol_no_stuck", patrol_stuck < 1.0)
	_check("nav_patrol_no_teleport", patrol_max_step < 0.5)
	_check("nav_agent_path", patrol_agent_path.size() >= 2)
	patrol_watcher.set_physics_process(false)

	# ------------------------------------------------------------------
	# Patrulla real del segundo Vigilante dentro de Seguridad. El jugador se
	# aleja a Z10 y el principal sigue suspendido: así solo se mide el
	# desplazamiento de patrulla del Vigilante de la sala, sin persecución.
	# ------------------------------------------------------------------
	if security_watcher_ready:
		player.global_position = Vector3(42.2, 0.12, -22.0)
		player.velocity = Vector3.ZERO
		await get_tree().physics_frame
		await get_tree().physics_frame
		security_watcher.activate_in_sector(
			security_watcher.global_position, security_watcher.patrol_points
		)
		_check("security_watcher_physics", security_watcher.is_physics_processing())
		var security_start: Vector3 = security_watcher.global_position
		var security_prev := security_start
		var security_path := 0.0
		var security_max_step := 0.0
		var security_elapsed := 0.0
		while security_elapsed < 2.0:
			await get_tree().physics_frame
			var security_current: Vector3 = security_watcher.global_position
			var security_step := security_prev.distance_to(security_current)
			security_path += security_step
			security_max_step = maxf(security_max_step, security_step)
			security_prev = security_current
			security_elapsed += get_physics_process_delta_time()
		var security_advanced := security_start.distance_to(security_watcher.global_position)
		var security_agent_path := security_watcher._agent.get_current_navigation_path()
		print("FM_LEVEL1_V06_SECURITY_WATCHER_PATROL start=%s end=%s advanced=%.2f path=%.2f max_step=%.3f agent_path=%d state=%d" % [
			str(security_start), str(security_watcher.global_position), security_advanced,
			security_path, security_max_step, security_agent_path.size(),
			int(security_watcher.state),
		])
		_check("security_watcher_moves", security_advanced > 0.5)
		_check("security_watcher_path_moves", security_path > 0.5)
		_check("security_watcher_agent_path", security_agent_path.size() >= 2)
		_check("security_watcher_no_teleport", security_max_step < 0.5)
		_check("security_watcher_no_capture", int(scene.state) == 0)
		security_watcher.set_physics_process(false)

		# El segundo Vigilante comparte el on_player_caught del nivel. La
		# transición está protegida por state: una segunda llamada no duplica
		# el estado LOST ni vuelve a mostrar el fin de partida.
		scene.on_player_caught(security_watcher)
		var caught_first: bool = int(scene.state) == 1 and scene.hud._overlay.visible
		scene.on_player_caught(security_watcher)
		var caught_second: bool = int(scene.state) == 1 and scene.hud._overlay.visible
		_check("security_watcher_capture_once", caught_first and caught_second)

	await _cleanup()


func _sync_nav(map: RID, frames: int) -> void:
	for i in range(frames):
		await get_tree().process_frame
		await get_tree().physics_frame
		NavigationServer3D.map_force_update(map)


func _nav_path(map: RID, from: Vector3, to: Vector3, layers: int) -> PackedVector3Array:
	return NavigationServer3D.map_get_path(map, from, to, true, layers)


func _path_end_distance(path: PackedVector3Array, target: Vector3) -> float:
	if path.is_empty():
		return INF
	return path[path.size() - 1].distance_to(target)


func _path_length(path: PackedVector3Array) -> float:
	var total := 0.0
	for i in range(1, path.size()):
		total += path[i - 1].distance_to(path[i])
	return total


func _walk_to(player: FMPlayer, target: Vector3, timeout: float) -> Dictionary:
	var start: Vector3 = player.global_position
	var prev: Vector3 = start
	var path := 0.0
	var max_step := 0.0
	var elapsed := 0.0
	var stuck := 0.0
	Input.action_press("move_up")
	while elapsed < timeout:
		var aim := target - player.global_position
		aim.y = 0.0
		if aim.length() < 0.35:
			break
		player.rotation.y = atan2(-aim.x, -aim.z)
		await get_tree().physics_frame
		var current: Vector3 = player.global_position
		var step := prev.distance_to(current)
		max_step = maxf(max_step, step)
		path += step
		prev = current
		elapsed += get_physics_process_delta_time()
		if step < 0.004:
			stuck += get_physics_process_delta_time()
			if stuck > 1.5:
				break
		else:
			stuck = 0.0
	Input.action_release("move_up")
	await get_tree().physics_frame
	return {"start": start, "end": player.global_position, "path": path, "max_step": max_step, "elapsed": elapsed}


func _cleanup() -> void:
	# Los pasos disparan AudioStreamPlaybackWAV en el autoload Audio; esperar a
	# que terminen evita el aviso de recursos en uso al cerrar la prueba.
	_release_movement()
	await _wait(1.0)
	if scene != null and is_instance_valid(scene):
		scene.free()
	scene = null
	await get_tree().process_frame
	await get_tree().process_frame
	_finish()


func _ray(from: Vector3, to: Vector3) -> Dictionary:
	var query := PhysicsRayQueryParameters3D.create(from, to)
	query.collision_mask = 1
	return get_viewport().world_3d.direct_space_state.intersect_ray(query)


func _sector_aabb(root: Node3D) -> AABB:
	var out := AABB()
	var first := true
	if root == null or not is_instance_valid(root):
		return out
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		var box := mi.global_transform * mi.mesh.get_aabb()
		if first:
			out = box
			first = false
		else:
			out = out.merge(box)
	return out


func _release_movement() -> void:
	for action in ["move_up", "move_down", "move_left", "move_right", "sprint", "crouch", "interact", "flashlight"]:
		Input.action_release(action)


func _wait(seconds: float) -> void:
	await get_tree().create_timer(seconds).timeout


func _check(label: String, condition: bool) -> void:
	if condition:
		passes += 1
		print("PASS %s" % label)
	else:
		_fail(label)


func _fail(label: String) -> void:
	fails += 1
	print("FAIL %s" % label)


func _finish() -> void:
	_release_movement()
	print("FM_LEVEL1_V06_SMOKE: %s (%d PASS / %d FAIL)" % [
		"PASS" if fails == 0 else "FAIL", passes, fails,
	])
	get_tree().quit(0 if fails == 0 else 1)
