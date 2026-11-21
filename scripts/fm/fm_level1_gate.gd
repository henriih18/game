class_name FMLevel1Gate
extends Node3D

## FRECUENCIA MUERTA — Compuerta industrial runtime para los vanos anchos del
## Nivel 1 V06.
##
## El kit `level1_doors.glb` solo contiene hojas de 1,58 m y no cubre los
## portales de 1,4–7,7 m de los sectores exportados. Esta compuerta construye
## su propia persiana en código (sin tocar GLB ni .blend), mantiene el mismo
## contrato `fm_interactable` que consume FMPlayer y reutiliza los materiales
## PBR compartidos de `assets/art/fm/`.
##
## No es un arma ni un sistema de combate: solo abre, cierra, bloquea el paso
## y emite ruido para el sistema de percepción de las criaturas.

signal state_changed(open: bool)

const MAT_METAL := preload("res://assets/art/fm/metal_panel.tres")
const MAT_DARK := preload("res://assets/art/fm/dark_metal.tres")
const MAT_HAZARD := preload("res://assets/art/fm/hazard.tres")
const MAT_GREEN := preload("res://assets/art/fm/emissive_green.tres")

@export var gate_id := "GATE"
@export var display_name := "COMPUERTA"
@export var width := 3.0
@export var height := 3.0
@export var open_time := 1.15
@export var close_time := 0.95
@export var interaction_reach := 2.9
## -1: la cara útil mira hacia -Z; +1: hacia +Z. Solo afecta a la baliza y a
## la franja de peligro; las dos caras llevan cartel legible.
@export var label_facing := -1.0
@export var noise_radius := 12.0
@export var slat_count := 16

var game: Node = null
var configured := false
var is_open := false
var is_moving := false

var _shutter: Node3D
var _shutter_body: StaticBody3D
var _status_mat: StandardMaterial3D
var _tween: Tween
var _interaction_point := Vector3.ZERO
var _has_interaction_point := false


## Debe llamarse después de add_child(), como el resto de interactuables del
## nivel. Construye la persiana una sola vez.
func setup(
	id: String, width_m: float, height_m: float, label: String,
	facing: float, game_ref: Node
) -> void:
	if configured:
		return
	gate_id = id
	width = width_m
	height = height_m
	display_name = label
	label_facing = signf(facing) if not is_zero_approx(facing) else -1.0
	game = game_ref
	name = "Gate_%s" % id
	add_to_group("fm_interactable")
	add_to_group("fm_door")
	_build()
	_refresh_status()
	configured = true
	print("FM_LEVEL1_GATE_READY id=%s size=%.2fx%.2f pos=%s facing=%.0f noise=%.1f" % [
		gate_id, width, height, str(global_position), label_facing, noise_radius,
	])


# ------------------------------------------------------------------ construcción

func _build() -> void:
	var metal := MAT_METAL.duplicate() as StandardMaterial3D
	metal.albedo_color = Color(0.60, 0.65, 0.68, 1.0)
	metal.uv1_scale = Vector3(maxf(1.0, width * 0.45), 1.0, 1.0)
	var dark := MAT_DARK
	var hazard := MAT_HAZARD

	_shutter = Node3D.new()
	_shutter.name = "Shutter"
	add_child(_shutter)

	# Persianas de lamas horizontales con solape y relieve alterno. Forman un
	# paño sólido: no se ve el otro lado por las juntas.
	var count := maxi(8, slat_count)
	var step := height / float(count)
	var slat_h := step + 0.012
	var slat_mesh := BoxMesh.new()
	slat_mesh.size = Vector3(width, slat_h, 0.09)
	for index in count:
		var slat := MeshInstance3D.new()
		slat.name = "Slat_%02d" % index
		slat.mesh = slat_mesh
		slat.material_override = metal
		slat.position = Vector3(0.0, step * (float(index) + 0.5), 0.008 if index % 2 == 0 else -0.008)
		_shutter.add_child(slat)

	# Colisión solidaria con la persiana: al subir, deja el vano libre.
	_shutter_body = StaticBody3D.new()
	_shutter_body.name = "GateCollider"
	_shutter_body.collision_layer = 1
	_shutter_body.collision_mask = 0
	var shape := CollisionShape3D.new()
	shape.name = "GateColliderShape"
	var box := BoxShape3D.new()
	box.size = Vector3(width, height, 0.18)
	shape.shape = box
	shape.position = Vector3(0.0, height * 0.5, 0.0)
	_shutter_body.add_child(shape)
	_shutter.add_child(_shutter_body)

	# Franja de peligro en la cara útil.
	_shutter.add_child(_make_box(
		"HazardStripe", Vector3(width - 0.16, 0.14, 0.02),
		Vector3(0.0, 0.22, label_facing * 0.075), hazard
	))

	# Guías laterales fijas. Se colocan por dentro de los postes del GLB para
	# no tapar el vano.
	for side in [-1.0, 1.0]:
		add_child(_make_box(
			"GuideRail_%s" % ("L" if side < 0.0 else "R"),
			Vector3(0.10, height + 0.10, 0.30),
			Vector3(side * (width * 0.5 + 0.05), (height + 0.10) * 0.5 - 0.05, 0.0),
			dark
		))

	# Tambor superior montado en la cara útil, delante del dintel del GLB.
	add_child(_make_box(
		"RollerHousing", Vector3(width + 0.16, 0.22, 0.34),
		Vector3(0.0, height + 0.11, label_facing * 0.20), dark
	))

	# Baliza emisiva de estado, sin luz dinámica.
	_status_mat = MAT_GREEN.duplicate() as StandardMaterial3D
	_status_mat.emission_energy_multiplier = 1.6
	add_child(_make_box(
		"StatusBeacon", Vector3(0.12, 0.14, 0.05),
		Vector3(width * 0.5 + 0.05, 1.45, label_facing * 0.18), _status_mat
	))

	# Cartel legible desde ambos lados del vano.
	for side in [-1.0, 1.0]:
		var label := Label3D.new()
		label.name = "GateLabel_%s" % ("N" if side < 0.0 else "S")
		label.text = display_name
		label.font_size = 46
		label.pixel_size = 0.005
		label.modulate = Color(0.86, 0.94, 0.88, 1.0)
		label.outline_size = 8
		label.outline_modulate = Color(0.008, 0.012, 0.010, 0.95)
		label.billboard = BaseMaterial3D.BILLBOARD_DISABLED
		label.position = Vector3(0.0, height + 0.36, side * 0.34)
		label.rotation.y = 0.0 if side > 0.0 else PI
		add_child(label)


func _make_box(
	node_name: String, size: Vector3, pos: Vector3, material: Material
) -> MeshInstance3D:
	var instance := MeshInstance3D.new()
	instance.name = node_name
	var mesh := BoxMesh.new()
	mesh.size = size
	instance.mesh = mesh
	instance.material_override = material
	instance.position = pos
	return instance


# ------------------------------------------------------------------ interacción

func can_interact(player: Node) -> bool:
	if not configured or is_moving:
		return false
	var who := player as Node3D
	if who == null:
		return false
	var local := to_local(who.global_position)
	if absf(local.x) > width * 0.5 + interaction_reach:
		return false
	if absf(local.z) > interaction_reach:
		return false
	if local.y < -1.2 or local.y > height + 1.0:
		return false
	if is_open and _is_inside_closing_zone(who.global_position):
		return false
	var side := 1.0 if local.z >= 0.0 else -1.0
	_interaction_point = to_global(Vector3(
		clampf(local.x, -width * 0.5 + 0.25, width * 0.5 - 0.25),
		clampf(1.25, 0.60, maxf(0.60, height - 0.20)),
		side * 0.55
	))
	_has_interaction_point = true
	return true


func get_interaction_position() -> Vector3:
	if _has_interaction_point:
		return _interaction_point
	return to_global(Vector3(0.0, minf(1.25, height * 0.5), 0.55))


func get_interaction_prompt() -> String:
	if not configured:
		return ""
	if is_moving:
		return "COMPUERTA EN MOVIMIENTO"
	if is_open:
		return "E   CERRAR COMPUERTA %s" % display_name
	return "E   ABRIR COMPUERTA %s" % display_name


func interact(player: Node) -> bool:
	if not can_interact(player):
		var who := player as Node3D
		if is_open and who != null and _is_inside_closing_zone(who.global_position):
			_notify("ALÉJATE DE LA COMPUERTA PARA CERRAR")
		return false
	set_open(not is_open)
	return true


func is_closed() -> bool:
	return configured and not is_open and not is_moving


func is_fully_open() -> bool:
	return configured and is_open and not is_moving


func get_shutter_lift() -> float:
	return _shutter.position.y if _shutter != null else 0.0


func get_collision_body() -> StaticBody3D:
	return _shutter_body


func get_enabled_collision_count() -> int:
	if _shutter_body == null:
		return 0
	var enabled := 0
	for child in _shutter_body.get_children():
		var shape := child as CollisionShape3D
		if shape != null and not shape.disabled:
			enabled += 1
	return enabled


# ------------------------------------------------------------------ estado

func set_open(value: bool, instant: bool = false) -> void:
	if _shutter == null:
		return
	var changed := value != is_open
	is_open = value
	var target_y := height + 0.12 if value else 0.0
	if instant:
		if _tween != null and _tween.is_valid():
			_tween.kill()
		_tween = null
		_shutter.position.y = target_y
		is_moving = false
		_refresh_status()
		if changed:
			_emit_gate_noise()
			state_changed.emit(is_open)
		return
	if not changed:
		return
	if _tween != null and _tween.is_valid():
		_tween.kill()
	is_moving = true
	var duration := open_time if value else close_time
	_tween = create_tween()
	_tween.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	_tween.tween_property(_shutter, "position:y", target_y, duration)
	_tween.finished.connect(_on_tween_finished, CONNECT_ONE_SHOT)
	_play_feedback(value)
	_refresh_status()
	_emit_gate_noise()


func _on_tween_finished() -> void:
	is_moving = false
	if _shutter != null:
		_shutter.position.y = height + 0.12 if is_open else 0.0
	_refresh_status()
	state_changed.emit(is_open)


func get_network_state() -> Dictionary:
	return {"id": gate_id, "open": is_open}


func apply_network_state(state: Dictionary) -> void:
	set_open(bool(state.get("open", is_open)), true)


func _is_inside_closing_zone(world_position: Vector3) -> bool:
	var local := to_local(world_position)
	return absf(local.x) <= width * 0.5 + 0.45 \
		and local.y >= -0.60 and local.y <= height + 0.40 \
		and absf(local.z) <= 0.95


func _refresh_status() -> void:
	if _status_mat == null:
		return
	var color := Color(1.0, 0.40, 0.06)
	if is_moving:
		color = Color(1.0, 0.82, 0.18)
	elif is_open:
		color = Color(0.10, 1.0, 0.46)
	_status_mat.albedo_color = Color(color.r * 0.22, color.g * 0.22, color.b * 0.22, 1.0)
	_status_mat.emission_enabled = true
	_status_mat.emission = color
	_status_mat.emission_energy_multiplier = 1.8 if is_moving else 1.45


func _emit_gate_noise() -> void:
	if game == null or not game.has_method("emit_noise"):
		return
	game.emit_noise(to_global(Vector3(0.0, 0.4, 0.0)), noise_radius, "door")


func _play_feedback(opening: bool) -> void:
	if opening:
		Audio.play_sfx("drop", -10.0, 0.58)
		Audio.play_sfx("click", -14.0, 0.92)
	else:
		Audio.play_sfx("click", -9.0, 0.72)
		Audio.play_sfx("drop", -16.0, 0.50)


func _notify(text: String) -> void:
	if game != null and game.has_method("notify"):
		game.notify(text)
