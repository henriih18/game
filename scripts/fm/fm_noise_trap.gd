class_name FMNoiseTrap
extends Area3D

## Trampa sonora: cristales y latas en el suelo.
## No hace daño; al pisarla genera un ruido fuerte que atrae al Vigilante.
## Debe ser visible y evitable.

const MAT_GLASS := preload("res://assets/art/fm/glass.tres")
const MAT_RUST := preload("res://assets/art/fm/rust.tres")
const MAT_DARK := preload("res://assets/art/fm/dark_metal.tres")

@export var noise_radius := 16.0

var game: Node = null
var triggered := false
var _visual: Node3D

func _ready() -> void:
	collision_layer = 0
	collision_mask = 2
	monitoring = true
	monitorable = false
	add_to_group("fm_noise_trap")
	body_entered.connect(_on_body_entered)
	_build_visual()

func _build_visual() -> void:
	_visual = Node3D.new()
	_visual.name = "Shards"
	add_child(_visual)

	# Fragmentos grandes y latas aplastadas, legibles pero sin brillar como un arma.
	for i in 7:
		var shard := MeshInstance3D.new()
		var mesh := BoxMesh.new()
		mesh.size = Vector3(0.16 + i * 0.018, 0.025, 0.12 + (i % 3) * 0.04)
		shard.mesh = mesh
		shard.material_override = MAT_GLASS if i % 2 == 0 else MAT_RUST
		shard.position = Vector3(
			-0.55 + fmod(float(i) * 0.27, 1.15),
			0.028 + float(i % 2) * 0.012,
			-0.32 + fmod(float(i) * 0.19, 0.64)
		)
		shard.rotation_degrees = Vector3(0.0, float(i) * 31.0, float(i % 3) * 5.0)
		_visual.add_child(shard)

	for i in 3:
		var can := MeshInstance3D.new()
		var can_mesh := CylinderMesh.new()
		can_mesh.top_radius = 0.075
		can_mesh.bottom_radius = 0.075
		can_mesh.height = 0.14
		can_mesh.radial_segments = 10
		can.mesh = can_mesh
		can.material_override = MAT_RUST
		can.position = Vector3(-0.38 + i * 0.31, 0.07, 0.22 - i * 0.12)
		can.rotation_degrees = Vector3(90.0, float(i) * 42.0, 0.0)
		_visual.add_child(can)

	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(1.55, 0.2, 1.0)
	shape.shape = box
	shape.position.y = 0.1
	add_child(shape)

func _on_body_entered(body: Node3D) -> void:
	if triggered or not body.is_in_group("fm_player"):
		return
	trigger()

func trigger(emit_sound: bool = true) -> void:
	if triggered:
		return
	triggered = true
	monitoring = false
	Audio.play_sfx("drop", -2.0, 1.35)
	Audio.play_sfx("click", -9.0, 0.66)
	if _visual != null:
		for child in _visual.get_children():
			if child is MeshInstance3D:
				child.position.y += 0.02
				child.rotation_degrees.z += 8.0
	if emit_sound and game != null:
		if game.has_method("emit_noise"):
			game.emit_noise(global_position, noise_radius, "glass")
		if game.has_method("on_noise_trap_triggered"):
			game.on_noise_trap_triggered()

func trigger_network() -> void:
	trigger(false)
