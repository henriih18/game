extends Node

## Verificación física de la red de rutas alternativas.
##
## Comprueba, con la misma capa de colisión que usa el jugador:
##  1. que una cápsula agachada (1,16 m + margen) cabe en los túneles;
##  2. que hay suelo bajo cada punto de paso;
##  3. que una cápsula de pie (1,68 m) NO cabe en los túneles de 1,25 m.
##
## No usa la malla de navegación: el perfil de la IA (2,20 m) no entra en
## estas rutas y por eso se validan con física real.

const SCENE_PATH := "res://scenes/fm/level1_v06.tscn"

const CROUCH_RADIUS := 0.34
const CROUCH_HEIGHT := 1.16
const STAND_RADIUS := 0.40
const STAND_HEIGHT := 1.68

# Godot: x, y del centro de la cápsula agachada, z. y = 0,60 sobre el suelo
# de los túneles (el suelo termina en y=0). NWStair usa la meseta a -4,5.
const CRAWL_POINTS := {
	"east_gallery": [
		Vector3(105.0, 0.60, -6.0),
		Vector3(105.0, 0.60, 0.0),
		Vector3(105.0, 0.60, 6.0),
	],
	"maint_corridor": [
		Vector3(10.0, 0.60, 19.5),
		Vector3(20.5, 0.60, 19.5),
		Vector3(40.0, 0.60, 19.5),
		Vector3(54.0, 0.60, 19.5),
		Vector3(20.5, 0.60, 10.0),
	],
	"north_gallery": [
		Vector3(-90.0, 0.60, -65.5),
		Vector3(-70.0, 0.60, -65.5),
		Vector3(-50.0, 0.60, -65.5),
		Vector3(-36.0, 0.60, -65.5),
	],
	"north_connector": [
		Vector3(-94.0, 0.60, -62.0),
	],
	"offices_crawl": [
		Vector3(-35.0, 0.60, -31.0),
		Vector3(-39.5, 0.60, -20.0),
	],
	"reception_stair": [
		Vector3(-65.0, 0.60, 32.0),
		Vector3(-40.0, 0.60, 32.0),
		Vector3(-37.0, 0.60, 20.0),
		Vector3(-37.0, 0.60, 8.0),
	],
	"service_loop": [
		Vector3(58.0, 0.60, -39.0),
		Vector3(62.0, 0.60, -36.0),
		Vector3(68.0, 0.60, -36.0),
	],
}

# El conector de Seguridad es un pasillo normal, no un túnel agachado.
const STAND_POINTS := [
	Vector3(-89.0, 0.85, -7.0),
	Vector3(-89.0, 0.85, -3.0),
]

# La meseta inferior de la escalera NW está a -4,5.
const LANDING_POINTS := [
	Vector3(-72.0, -3.90, -56.0),
]

var _pass := 0
var _fail := 0


func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var packed := load(SCENE_PATH) as PackedScene
	if packed == null:
		_fail_msg("scene")
		_finish()
		return
	var scene = packed.instantiate()
	add_child(scene)
	var guard := 0
	while not scene.level_ready and guard < 3600:
		await get_tree().process_frame
		guard += 1
	if not scene.level_ready:
		_fail_msg("level_ready guard=%d" % guard)
		_finish()
		return
	await get_tree().physics_frame
	await get_tree().physics_frame
	var space := get_viewport().world_3d.direct_space_state

	for route in CRAWL_POINTS:
		for point in CRAWL_POINTS[route]:
			_check_crawl(space, route, point)
	for point in STAND_POINTS:
		_check_stand(space, "security_connector", point)
	for point in LANDING_POINTS:
		_check_crawl(space, "nw_stair_landing", point)
	_finish()


func _capsule(radius: float, height: float) -> CapsuleShape3D:
	var shape := CapsuleShape3D.new()
	shape.radius = radius
	shape.height = height
	return shape


func _overlaps(space: PhysicsDirectSpaceState3D, point: Vector3, radius: float, height: float) -> bool:
	var shape := _capsule(radius, height)
	var params := PhysicsShapeQueryParameters3D.new()
	params.shape = shape
	params.transform = Transform3D(Basis(), point)
	params.collision_mask = 1
	params.collide_with_bodies = true
	params.collide_with_areas = false
	return not space.intersect_shape(params, 8).is_empty()


func _floor_y(space: PhysicsDirectSpaceState3D, point: Vector3) -> float:
	var query := PhysicsRayQueryParameters3D.create(
		point + Vector3.UP * 0.30, point - Vector3.UP * 1.35, 1
	)
	var hit := space.intersect_ray(query)
	if hit.is_empty():
		return 999.0
	return float(hit["position"].y)


func _check_crawl(space: PhysicsDirectSpaceState3D, route: String, point: Vector3) -> void:
	var blocked := _overlaps(space, point, CROUCH_RADIUS, CROUCH_HEIGHT)
	_check("%s_crouch_clear_%s" % [route, _tag(point)], not blocked)
	var stand := _overlaps(space, point, STAND_RADIUS, STAND_HEIGHT)
	_check("%s_stand_blocked_%s" % [route, _tag(point)], stand)
	var floor := _floor_y(space, point)
	_check("%s_floor_%s" % [route, _tag(point)], absf(floor - point.y + 0.60) < 0.18)


func _check_stand(space: PhysicsDirectSpaceState3D, route: String, point: Vector3) -> void:
	_check("%s_stand_clear_%s" % [route, _tag(point)],
		not _overlaps(space, point, STAND_RADIUS, STAND_HEIGHT))
	var floor := _floor_y(space, point)
	_check("%s_floor_%s" % [route, _tag(point)], absf(floor - point.y + 0.85) < 0.18)


func _tag(point: Vector3) -> String:
	return "%d_%d" % [int(round(point.x)), int(round(point.z))]


func _check(label: String, ok: bool) -> void:
	if ok:
		_pass += 1
		print("PASS ", label)
	else:
		_fail += 1
		print("FAIL ", label)


func _fail_msg(label: String) -> void:
	_fail += 1
	print("FAIL ", label)


func _finish() -> void:
	print("FM_ALT_ROUTES_SMOKE: %s (%d PASS / %d FAIL)" % [
		"PASS" if _fail == 0 else "FAIL", _pass, _fail,
	])
	get_tree().quit(0 if _fail == 0 else 1)
