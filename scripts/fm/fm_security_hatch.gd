class_name FMSecurityHatch
extends Node3D

## FRECUENCIA MUERTA — Compuerta interactiva de la ventanilla de servicio.
##
## El arte de Seguridad importa R21C_HATCH_* como mallas planas dentro de
## security_sector.glb. La compuerta cerrada ocupa el hueco peatonal de la
## pared este: el mostrador (Counter), la luna (Glass), la reja (Shutter),
## los fragmentos (Shards) y el marco (WindowFrame) generan colisión estática
## en FMGLBCollision. El marco incluye un travesaño inferior que también
## bloquea la cápsula, por eso la compuerta móvil es el conjunto completo y
## no solo el mostrador.
##
## Este nodo no modifica el GLB ni el .blend: guarda las posiciones locales
## originales, localiza las colisiones generadas para esas mallas y las
## desactiva únicamente cuando la compuerta está completamente abierta.
## La interacción sigue el contrato fm_interactable que consume FMPlayer.

signal state_changed(open: bool)

const HATCH_MESH_NAMES: Array[String] = [
	"R21C_HATCH_Counter",
	"R21C_HATCH_Glass",
	"R21C_HATCH_Shards",
	"R21C_HATCH_Shutter",
	"R21C_HATCH_WindowFrame",
]

@export var open_lift := 2.2
@export var open_time := 1.15
@export var close_time := 0.9
@export var interaction_reach := 2.8

var configured := false
var is_open := false
var is_moving := false

var _game: Node = null
var _security_root: Node3D = null
var _collision_body: StaticBody3D = null
var _meshes: Array[MeshInstance3D] = []
var _closed_positions: Array[Vector3] = []
var _collision_shapes: Array[CollisionShape3D] = []
var _tween: Tween = null
var _interaction_side := 1
var _gate_center := Vector3.ZERO
var _closing_zone := AABB()
var _east_point := Vector3.ZERO
var _west_point := Vector3.ZERO


func _ready() -> void:
	set_process(false)


## Debe llamarse después de construir las colisiones del sector Seguridad.
## Devuelve false y deja la compuerta cerrada si la estructura del GLB no es
## la esperada; en ese caso el nivel informa del blocker y no inventa una
## puerta nueva.
func setup(security_root: Node3D, collision_body: StaticBody3D, game_node: Node = null) -> bool:
	if configured:
		return true
	_security_root = security_root
	_collision_body = collision_body
	_game = game_node
	if _security_root == null:
		push_error("FM_SECURITY_HATCH: falta la raíz del sector Seguridad")
		return false
	if _collision_body == null:
		push_error("FM_SECURITY_HATCH: falta Collision_Security")
		return false

	for mesh_name in HATCH_MESH_NAMES:
		var mesh_instance := _security_root.find_child(mesh_name, true, false) as MeshInstance3D
		if mesh_instance == null or mesh_instance.mesh == null:
			push_error("FM_SECURITY_HATCH: no se encontró la malla %s" % mesh_name)
			return false
		_meshes.append(mesh_instance)
		_closed_positions.append(mesh_instance.position)

	var all_shapes: Array[CollisionShape3D] = []
	for mesh_instance in _meshes:
		var matches := _find_collision_shapes(mesh_instance)
		if matches.is_empty():
			push_error("FM_SECURITY_HATCH: no se encontró colisión para %s" % mesh_instance.name)
			return false
		for shape in matches:
			if not all_shapes.has(shape):
				all_shapes.append(shape)
	if all_shapes.is_empty():
		push_error("FM_SECURITY_HATCH: la compuerta no tiene colisiones asociadas")
		return false
	_collision_shapes = all_shapes

	var counter := _meshes[0]
	var frame := _meshes[4]
	var counter_box: AABB = counter.global_transform * counter.get_aabb()
	var frame_box: AABB = frame.global_transform * frame.get_aabb()
	var gate_box := counter_box.merge(frame_box)
	_gate_center = Vector3(gate_box.get_center().x, 0.0, -10.9)
	global_position = _gate_center

	# Zona de cierre: el volumen de la compuerta más el radio de la cápsula y
	# un margen. No se permite cerrar si algún jugador está dentro.
	var expanded := gate_box.grow(0.48)
	expanded.position.y = -0.5
	expanded.size.y = 3.0
	_closing_zone = expanded

	# Punto de interacción en el lado del jugador, fuera del volumen cerrado.
	_east_point = Vector3(gate_box.end.x + 0.10, 0.55, -10.9)
	_west_point = Vector3(gate_box.position.x - 0.10, 0.55, -10.9)

	_set_collisions_enabled(true)
	configured = true
	add_to_group("fm_interactable")
	print("FM_SECURITY_HATCH_READY meshes=%d colliders=%d lift=%.2f zone=%s" % [
		_meshes.size(), _collision_shapes.size(), open_lift, str(_closing_zone),
	])
	return true


func can_interact(player: Node) -> bool:
	if not configured or is_moving:
		return false
	var who := player as Node3D
	if who == null:
		return false
	_interaction_side = 1 if who.global_position.x > _gate_center.x else -1
	if who.global_position.distance_to(get_interaction_position()) > interaction_reach:
		return false
	if is_open and not _is_outside_closing_zone(who.global_position):
		return false
	return true


func get_interaction_prompt() -> String:
	if not configured:
		return ""
	if is_moving:
		return "COMPUERTA EN MOVIMIENTO"
	if is_open:
		return "E   CERRAR COMPUERTA DE SERVICIO"
	return "E   ABRIR COMPUERTA DE SERVICIO"


func get_interaction_position() -> Vector3:
	return _east_point if _interaction_side >= 0 else _west_point


func interact(player: Node) -> bool:
	if not configured or is_moving:
		return false
	var who := player as Node3D
	if who == null:
		return false
	_interaction_side = 1 if who.global_position.x > _gate_center.x else -1
	if is_open:
		if not _is_outside_closing_zone(who.global_position):
			_notify("ALÉJATE DE LA COMPUERTA PARA CERRAR")
			return false
		_animate(false)
		return true
	_animate(true)
	return true


func is_closed() -> bool:
	return configured and not is_open and not is_moving


func is_fully_open() -> bool:
	return configured and is_open and not is_moving


func get_collision_shape_count() -> int:
	return _collision_shapes.size()


func get_enabled_collision_count() -> int:
	var count := 0
	for shape in _collision_shapes:
		if is_instance_valid(shape) and not shape.disabled:
			count += 1
	return count


func get_mesh_lift() -> float:
	if _meshes.is_empty() or _closed_positions.is_empty():
		return 0.0
	var total := 0.0
	var count := 0
	for index in _meshes.size():
		var mesh_instance := _meshes[index]
		if is_instance_valid(mesh_instance):
			total += mesh_instance.position.y - _closed_positions[index].y
			count += 1
	return total / float(count) if count > 0 else 0.0


func _animate(open: bool) -> void:
	if _tween != null and _tween.is_valid():
		_tween.kill()
	is_moving = true
	var duration := open_time if open else close_time
	var offset := open_lift if open else 0.0
	_tween = create_tween()
	_tween.set_parallel(true)
	_tween.set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_IN_OUT)
	for index in _meshes.size():
		var mesh_instance := _meshes[index]
		if not is_instance_valid(mesh_instance):
			continue
		var target_y := _closed_positions[index].y + offset
		_tween.tween_property(mesh_instance, "position:y", target_y, duration)
	_tween.finished.connect(_on_tween_finished.bind(open), CONNECT_ONE_SHOT)
	Audio.play_sfx("click", -13.0, 0.72)
	if _game != null and _game.has_method("emit_noise"):
		_game.emit_noise(global_position, 11.0, "door")


func _on_tween_finished(open: bool) -> void:
	for index in _meshes.size():
		var mesh_instance := _meshes[index]
		if is_instance_valid(mesh_instance):
			mesh_instance.position.y = _closed_positions[index].y + (open_lift if open else 0.0)
	is_open = open
	is_moving = false
	_set_collisions_enabled(not open)
	Audio.play_sfx("drop", -15.0, 0.62)
	state_changed.emit(is_open)


func _set_collisions_enabled(enabled: bool) -> void:
	for shape in _collision_shapes:
		if is_instance_valid(shape):
			shape.disabled = not enabled


func _is_outside_closing_zone(world_position: Vector3) -> bool:
	return not _closing_zone.has_point(world_position)


func _notify(text: String) -> void:
	if _game != null and _game.has_method("notify"):
		_game.notify(text)


func _find_collision_shapes(mesh_instance: MeshInstance3D) -> Array[CollisionShape3D]:
	var matches: Array[CollisionShape3D] = []
	var mesh_box: AABB = mesh_instance.global_transform * mesh_instance.get_aabb()
	for child in _collision_body.get_children():
		var collider := child as CollisionShape3D
		if collider == null or collider.shape == null:
			continue
		var shape_box := _shape_world_aabb(collider)
		if shape_box.size == Vector3.ZERO:
			continue
		if shape_box.position.distance_to(mesh_box.position) <= 0.03 \
				and shape_box.size.distance_to(mesh_box.size) <= 0.03:
			matches.append(collider)
	return matches


func _shape_world_aabb(collider: CollisionShape3D) -> AABB:
	var shape := collider.shape
	if shape is BoxShape3D:
		var box := shape as BoxShape3D
		return AABB(collider.global_position - box.size * 0.5, box.size)
	if shape is ConcavePolygonShape3D:
		var faces := (shape as ConcavePolygonShape3D).get_faces()
		if faces.is_empty():
			return AABB()
		var low := Vector3(INF, INF, INF)
		var high := Vector3(-INF, -INF, -INF)
		for vertex in faces:
			low.x = minf(low.x, vertex.x)
			low.y = minf(low.y, vertex.y)
			low.z = minf(low.z, vertex.z)
			high.x = maxf(high.x, vertex.x)
			high.y = maxf(high.y, vertex.y)
			high.z = maxf(high.z, vertex.z)
		return collider.global_transform * AABB(low, high - low)
	return AABB()
