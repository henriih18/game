class_name FMBattery
extends Node3D

## Batería recogible para la linterna. Es un recurso de supervivencia,
## no un arma. Se consume una sola vez.

const MAT_YELLOW := preload("res://assets/art/fm/warning_yellow.tres")
const MAT_DARK := preload("res://assets/art/fm/dark_metal.tres")
const MAT_GREEN := preload("res://assets/art/fm/emissive_green.tres")

@export var charge_amount := 45.0

var game: Node = null
var taken := false
var _visual: Node3D
var _time := 0.0

func _ready() -> void:
	add_to_group("fm_interactable")
	_build()

func _build() -> void:
	_visual = Node3D.new()
	_visual.name = "Visual"
	add_child(_visual)

	var body := MeshInstance3D.new()
	var body_mesh := CylinderMesh.new()
	body_mesh.top_radius = 0.09
	body_mesh.bottom_radius = 0.09
	body_mesh.height = 0.28
	body_mesh.radial_segments = 12
	body.mesh = body_mesh
	var body_mat: StandardMaterial3D = MAT_YELLOW.duplicate()
	body_mat.emission_energy_multiplier = 0.55
	body.material_override = body_mat
	_visual.add_child(body)

	for y in [-0.15, 0.15]:
		var cap := MeshInstance3D.new()
		var cap_mesh := CylinderMesh.new()
		cap_mesh.top_radius = 0.105
		cap_mesh.bottom_radius = 0.105
		cap_mesh.height = 0.035
		cap_mesh.radial_segments = 12
		cap.mesh = cap_mesh
		cap.material_override = MAT_DARK
		cap.position.y = y
		_visual.add_child(cap)

	var band := MeshInstance3D.new()
	var band_mesh := CylinderMesh.new()
	band_mesh.top_radius = 0.095
	band_mesh.bottom_radius = 0.095
	band_mesh.height = 0.035
	band_mesh.radial_segments = 12
	band.mesh = band_mesh
	var band_mat: StandardMaterial3D = MAT_GREEN.duplicate()
	band_mat.emission_energy_multiplier = 0.8
	band.material_override = band_mat
	band.position.y = 0.02
	_visual.add_child(band)

	var glow := OmniLight3D.new()
	glow.light_color = Color(0.45, 1.0, 0.46)
	glow.light_energy = 0.35
	glow.omni_range = 1.4
	glow.shadow_enabled = false
	glow.position.y = 0.1
	_visual.add_child(glow)

	var label := Label3D.new()
	label.text = "BATERÍA"
	label.font_size = 16
	label.pixel_size = 0.006
	label.modulate = Color(0.62, 1.0, 0.62)
	label.outline_size = 5
	label.outline_modulate = Color(0.01, 0.02, 0.012, 0.9)
	label.position.y = 0.34
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	_visual.add_child(label)

func _process(delta: float) -> void:
	_time += delta
	if _visual != null:
		_visual.rotation.y += delta * 0.9
		_visual.position.y = sin(_time * 2.4) * 0.04

func can_interact(_player: Node) -> bool:
	return not taken

func get_interaction_prompt() -> String:
	return "E   RECOGER BATERÍA   +%d%%" % int(charge_amount)

func get_interaction_position() -> Vector3:
	return global_position + Vector3(0.0, 0.3, 0.0)

func interact(player: Node) -> bool:
	if taken:
		return false
	taken = true
	if player != null and player.has_method("recharge_battery"):
		player.recharge_battery(charge_amount)
	Audio.play_sfx("gem", -12.0, 1.2)
	if game != null and game.has_method("emit_noise"):
		game.emit_noise(global_position, 3.5, "battery")
	queue_free()
	return true
