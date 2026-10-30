class_name Crate3D
extends Node3D

var holder_ids: Array[int] = []
var delivered := false
var game: Node = null

var _visual: Node3D
var _body_mat: StandardMaterial3D
var _time := 0.0
var _light: OmniLight3D

func _ready() -> void:
	_build_visual()

func _build_visual() -> void:
	_visual = Node3D.new()
	_visual.name = "Visual"
	add_child(_visual)

	_body_mat = _make_mat(Color(0.76, 0.50, 0.19), 0.72, 0.05)

	var body := MeshInstance3D.new()
	var body_mesh := BoxMesh.new()
	body_mesh.size = Vector3(1.15, 1.15, 1.15)
	body.mesh = body_mesh
	body.material_override = _body_mat
	_visual.add_child(body)

	var trim_mat := _make_mat(Color(0.27, 0.17, 0.09), 0.85)
	for y in [-0.42, 0.42]:
		var band := MeshInstance3D.new()
		var band_mesh := BoxMesh.new()
		band_mesh.size = Vector3(1.21, 0.1, 1.21)
		band.mesh = band_mesh
		band.material_override = trim_mat
		band.position.y = y
		_visual.add_child(band)

	for x in [-0.54, 0.54]:
		for z in [-0.54, 0.54]:
			var corner := MeshInstance3D.new()
			var corner_mesh := BoxMesh.new()
			corner_mesh.size = Vector3(0.09, 1.15, 0.09)
			corner.mesh = corner_mesh
			corner.material_override = trim_mat
			corner.position = Vector3(x, 0, z)
			_visual.add_child(corner)

	var handle := MeshInstance3D.new()
	var handle_mesh := BoxMesh.new()
	handle_mesh.size = Vector3(0.42, 0.09, 0.14)
	handle.mesh = handle_mesh
	handle.material_override = trim_mat
	handle.position = Vector3(0, 0.63, 0)
	_visual.add_child(handle)

	var lock := MeshInstance3D.new()
	var lock_mesh := BoxMesh.new()
	lock_mesh.size = Vector3(0.32, 0.38, 0.08)
	lock.mesh = lock_mesh
	lock.material_override = _make_mat(Color(0.92, 0.7, 0.25), 0.35, 0.55)
	lock.position = Vector3(0, 0.05, -0.61)
	_visual.add_child(lock)

	var keyhole := MeshInstance3D.new()
	var keyhole_mesh := SphereMesh.new()
	keyhole_mesh.radius = 0.055
	keyhole_mesh.height = 0.11
	keyhole.mesh = keyhole_mesh
	keyhole.material_override = _make_mat(Color(0.09, 0.07, 0.05), 0.8)
	keyhole.position = Vector3(0, 0.05, -0.655)
	_visual.add_child(keyhole)

func _make_mat(tint: Color, roughness: float, metallic := 0.0) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = tint
	mat.roughness = roughness
	mat.metallic = metallic
	return mat

func _process(delta: float) -> void:
	if delivered:
		return
	_time += delta

	var total := Vector3.ZERO
	var count := 0
	if game != null and is_instance_valid(game):
		for id in holder_ids:
			if game.players.has(id):
				var player = game.players[id]
				if is_instance_valid(player):
					total += player.global_position
					count += 1

	if count > 0:
		var target := total / float(count) + Vector3(0, 2.15, 0)
		global_position = global_position.lerp(target, minf(1.0, 11.0 * delta))
		global_position.x = clampf(global_position.x, -12.0, 12.0)
		global_position.z = clampf(global_position.z, -8.0, 8.0)
		_visual.rotation.z = sin(_time * 7.0) * 0.055
		_visual.position.y = sin(_time * 5.0) * 0.045
	else:
		global_position.y = lerpf(global_position.y, 0.58, minf(1.0, 7.0 * delta))
		_visual.rotation.z = lerpf(_visual.rotation.z, 0.0, minf(1.0, 8.0 * delta))
		_visual.position.y = lerpf(_visual.position.y, 0.0, minf(1.0, 8.0 * delta))

func add_holder(id: int) -> void:
	if not holder_ids.has(id):
		holder_ids.append(id)

func remove_holder(id: int) -> void:
	holder_ids.erase(id)

func holder_count() -> int:
	return holder_ids.size()

func deliver(pad_position: Vector3) -> void:
	if delivered:
		return
	delivered = true
	holder_ids.clear()
	global_position = pad_position + Vector3(0, 0.82, 0)
	_visual.rotation = Vector3.ZERO
	_visual.position = Vector3.ZERO
	_body_mat.albedo_color = Color(0.38, 0.82, 0.55)
	_body_mat.emission_enabled = true
	_body_mat.emission = Color(0.18, 0.6, 0.34)
	_body_mat.emission_energy_multiplier = 0.9

	_light = OmniLight3D.new()
	_light.light_color = Color(0.35, 1.0, 0.6)
	_light.light_energy = 1.3
	_light.omni_range = 3.2
	_light.position = Vector3(0, 0.9, 0)
	add_child(_light)

	Audio.play_sfx("deliver", -7.0)
