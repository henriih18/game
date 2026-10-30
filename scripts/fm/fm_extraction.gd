class_name FMExtraction
extends Area3D

## Punto de extracción del vertical slice.
## El jugador debe llegar con el núcleo en las manos.

var players_inside: Array[Node3D] = []
var _ring: MeshInstance3D
var _light: OmniLight3D
var _time := 0.0

func _ready() -> void:
	collision_layer = 0
	collision_mask = 2
	monitoring = true
	monitorable = false
	add_to_group("fm_extraction")
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)
	_build_visual()

func _build_visual() -> void:
	var base := MeshInstance3D.new()
	var base_mesh := CylinderMesh.new()
	base_mesh.top_radius = 1.75
	base_mesh.bottom_radius = 1.75
	base_mesh.height = 0.08
	base_mesh.radial_segments = 32
	base.mesh = base_mesh
	var base_mat := StandardMaterial3D.new()
	base_mat.albedo_color = Color(0.035, 0.08, 0.06, 1.0)
	base_mat.roughness = 0.72
	base_mat.metallic = 0.45
	base.material_override = base_mat
	base.position.y = 0.04
	add_child(base)

	_ring = MeshInstance3D.new()
	var ring_mesh := TorusMesh.new()
	ring_mesh.inner_radius = 1.45
	ring_mesh.outer_radius = 1.58
	ring_mesh.rings = 32
	ring_mesh.ring_segments = 8
	_ring.mesh = ring_mesh
	var ring_mat := StandardMaterial3D.new()
	ring_mat.albedo_color = Color(0.08, 0.65, 0.3, 1.0)
	ring_mat.emission_enabled = true
	ring_mat.emission = Color(0.12, 1.0, 0.45)
	ring_mat.emission_energy_multiplier = 1.8
	_ring.material_override = ring_mat
	_ring.position.y = 0.09
	add_child(_ring)

	var inner := MeshInstance3D.new()
	var inner_mesh := CylinderMesh.new()
	inner_mesh.top_radius = 1.08
	inner_mesh.bottom_radius = 1.08
	inner_mesh.height = 0.015
	inner_mesh.radial_segments = 32
	inner.mesh = inner_mesh
	var inner_mat := StandardMaterial3D.new()
	inner_mat.albedo_color = Color(0.02, 0.2, 0.1, 0.7)
	inner_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	inner_mat.emission_enabled = true
	inner_mat.emission = Color(0.04, 0.55, 0.24)
	inner_mat.emission_energy_multiplier = 0.45
	inner.material_override = inner_mat
	inner.position.y = 0.085
	add_child(inner)

	_light = OmniLight3D.new()
	_light.light_color = Color(0.16, 1.0, 0.48)
	_light.light_energy = 1.3
	_light.omni_range = 5.0
	_light.shadow_enabled = false
	_light.position.y = 0.7
	add_child(_light)

	var label := Label3D.new()
	label.text = "EXTRACCIÓN"
	label.font_size = 36
	label.pixel_size = 0.008
	label.modulate = Color(0.45, 1.0, 0.68)
	label.outline_size = 8
	label.outline_modulate = Color(0.01, 0.04, 0.02, 0.9)
	label.position = Vector3(0, 2.3, 0)
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	add_child(label)

func _process(delta: float) -> void:
	_time += delta
	if _ring != null:
		_ring.rotation.y += delta * 0.35
	if _light != null:
		_light.light_energy = 1.15 + sin(_time * 2.2) * 0.25

func _on_body_entered(body: Node3D) -> void:
	if body.is_in_group("fm_player") and not players_inside.has(body):
		players_inside.append(body)

func _on_body_exited(body: Node3D) -> void:
	players_inside.erase(body)

func has_player() -> bool:
	for player in players_inside:
		if is_instance_valid(player):
			return true
	return false

func get_carrier() -> Node3D:
	for player in players_inside:
		if is_instance_valid(player) and player.get("carried_item") != null:
			return player
	return null
