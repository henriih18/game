class_name FMSecurityDoor
extends Node3D

## Puerta de seguridad del vertical slice.
## Empieza cerrada y bloquea el paso a extracción. Se abre con una
## interacción local; no es un arma ni un sistema de combate.

signal opened

const MAT_METAL := preload("res://assets/art/fm/metal_panel.tres")
const MAT_DARK := preload("res://assets/art/fm/dark_metal.tres")
const MAT_HAZARD := preload("res://assets/art/fm/hazard.tres")
const MAT_GREEN := preload("res://assets/art/fm/emissive_green.tres")
const MAT_RED := preload("res://assets/art/fm/emissive_red.tres")

@export var slide_distance := 1.18
@export var open_time := 0.55

var game: Node = null
var is_open := false

var _leaves: Array[StaticBody3D] = []
var _keypad_mat: StandardMaterial3D
var _state_label: Label3D

func _ready() -> void:
	add_to_group("fm_interactable")
	_build()

func _build() -> void:
	var metal: StandardMaterial3D = MAT_METAL.duplicate()
	metal.albedo_color = Color(0.63, 0.7, 0.72, 1.0)
	metal.uv1_scale = Vector3(2.0, 2.0, 1.0)

	var dark: StandardMaterial3D = MAT_DARK
	var hazard: StandardMaterial3D = MAT_HAZARD
	var green: StandardMaterial3D = MAT_GREEN
	var red: StandardMaterial3D = MAT_RED

	for side in [-1.0, 1.0]:
		var body := StaticBody3D.new()
		body.name = "LeafLeft" if side < 0.0 else "LeafRight"
		body.position = Vector3(side * 0.72, 1.36, 0.0)
		body.collision_layer = 1
		body.collision_mask = 0
		var shape := CollisionShape3D.new()
		var box := BoxShape3D.new()
		box.size = Vector3(1.44, 2.72, 0.18)
		shape.shape = box
		body.add_child(shape)

		var panel := MeshInstance3D.new()
		var panel_mesh := BoxMesh.new()
		panel_mesh.size = Vector3(1.44, 2.72, 0.18)
		panel.mesh = panel_mesh
		panel.material_override = metal
		body.add_child(panel)

		var stripe := MeshInstance3D.new()
		var stripe_mesh := BoxMesh.new()
		stripe_mesh.size = Vector3(1.12, 0.18, 0.03)
		stripe.mesh = stripe_mesh
		stripe.material_override = hazard
		stripe.position = Vector3(0.0, -1.05, 0.11)
		body.add_child(stripe)

		var handle := MeshInstance3D.new()
		var handle_mesh := BoxMesh.new()
		handle_mesh.size = Vector3(0.06, 0.28, 0.06)
		handle.mesh = handle_mesh
		handle.material_override = dark
		handle.position = Vector3(-side * 0.5, -0.15, 0.13)
		body.add_child(handle)

		add_child(body)
		_leaves.append(body)

	# Marco fijo: dos jambas y un dintel, sin tapar el hueco.
	for side in [-1.0, 1.0]:
		var post := MeshInstance3D.new()
		var post_mesh := BoxMesh.new()
		post_mesh.size = Vector3(0.16, 3.0, 0.14)
		post.mesh = post_mesh
		post.material_override = dark
		post.position = Vector3(side * 1.58, 1.5, -0.12)
		add_child(post)
	var lintel := MeshInstance3D.new()
	var lintel_mesh := BoxMesh.new()
	lintel_mesh.size = Vector3(3.32, 0.18, 0.14)
	lintel.mesh = lintel_mesh
	lintel.material_override = dark
	lintel.position = Vector3(0.0, 2.98, -0.12)
	add_child(lintel)

	var keypad := MeshInstance3D.new()
	var keypad_mesh := BoxMesh.new()
	keypad_mesh.size = Vector3(0.22, 0.34, 0.08)
	keypad.mesh = keypad_mesh
	keypad.material_override = dark
	keypad.position = Vector3(1.62, 1.35, 0.12)
	add_child(keypad)

	_keypad_mat = red.duplicate()
	_keypad_mat.emission_energy_multiplier = 0.95
	var key_light := MeshInstance3D.new()
	var key_light_mesh := BoxMesh.new()
	key_light_mesh.size = Vector3(0.12, 0.2, 0.02)
	key_light.mesh = key_light_mesh
	key_light.material_override = _keypad_mat
	key_light.position = Vector3(1.62, 1.35, 0.17)
	add_child(key_light)

	_state_label = Label3D.new()
	_state_label.text = "PUERTA BLOQUEADA"
	_state_label.font_size = 22
	_state_label.pixel_size = 0.0065
	_state_label.modulate = Color(0.95, 0.5, 0.34)
	_state_label.outline_size = 7
	_state_label.outline_modulate = Color(0.01, 0.01, 0.012, 0.95)
	_state_label.position = Vector3(0.0, 2.62, 0.2)
	_state_label.billboard = BaseMaterial3D.BILLBOARD_DISABLED
	add_child(_state_label)

	# La luz de estado sirve como referencia visual en el corredor.
	var status_light := OmniLight3D.new()
	status_light.light_color = Color(1.0, 0.18, 0.1)
	status_light.light_energy = 0.7
	status_light.omni_range = 3.2
	status_light.shadow_enabled = false
	status_light.position = Vector3(1.55, 1.35, 0.45)
	add_child(status_light)

func can_interact(_player: Node) -> bool:
	return not is_open

func get_interaction_prompt() -> String:
	if is_open:
		return ""
	return "E   ABRIR PUERTA DE SEGURIDAD"

func get_interaction_position() -> Vector3:
	return global_position + Vector3(0.0, 1.35, 0.6)

func interact(_player: Node) -> bool:
	if is_open:
		return false
	is_open = true
	for body in _leaves:
		if not is_instance_valid(body):
			continue
		var side := -1.0 if body.name == "LeafLeft" else 1.0
		body.collision_layer = 0
		var tween := create_tween()
		tween.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		tween.tween_property(body, "position:x", body.position.x + side * slide_distance, open_time)

	if _keypad_mat != null:
		_keypad_mat.albedo_color = Color(0.08, 0.5, 0.22, 1.0)
		_keypad_mat.emission = Color(0.15, 1.0, 0.45)
		_keypad_mat.emission_energy_multiplier = 1.25
	if _state_label != null:
		_state_label.text = "PUERTA ABIERTA"
		_state_label.modulate = Color(0.42, 1.0, 0.62)

	Audio.play_sfx("click", -8.0, 0.62)
	Audio.play_sfx("drop", -15.0, 0.72)
	if game != null and game.has_method("emit_noise"):
		game.emit_noise(global_position, 11.0, "door")
	opened.emit()
	return true
