class_name SecurityCamera3D
extends Node3D

const RANGE := 8.0
const HALF_ANGLE := 0.52

var game: Node = null
var triggered := false

var _cone_mat: StandardMaterial3D
var _border_mat: StandardMaterial3D
var _lens_mat: StandardMaterial3D
var _spot: SpotLight3D
var _head: Node3D

func _ready() -> void:
	_build_visual()

func _build_visual() -> void:
	_head = Node3D.new()
	_head.name = "Head"
	_head.rotation.x = -0.34
	add_child(_head)

	var body := MeshInstance3D.new()
	var body_mesh := BoxMesh.new()
	body_mesh.size = Vector3(0.58, 0.38, 0.68)
	body.mesh = body_mesh
	body.material_override = _make_mat(Color(0.2, 0.24, 0.32), 0.55, 0.35)
	_head.add_child(body)

	var lens := MeshInstance3D.new()
	var lens_mesh := CylinderMesh.new()
	lens_mesh.top_radius = 0.15
	lens_mesh.bottom_radius = 0.15
	lens_mesh.height = 0.34
	lens_mesh.radial_segments = 14
	lens.mesh = lens_mesh
	lens.rotation.x = PI * 0.5
	lens.position = Vector3(0, 0, -0.44)
	_lens_mat = _make_mat(Color(0.07, 0.08, 0.12), 0.2, 0.5)
	lens.material_override = _lens_mat
	_head.add_child(lens)

	var led := MeshInstance3D.new()
	var led_mesh := SphereMesh.new()
	led_mesh.radius = 0.055
	led_mesh.height = 0.11
	led.mesh = led_mesh
	var led_mat := _make_mat(Color(1.0, 0.25, 0.2), 0.3)
	led_mat.emission_enabled = true
	led_mat.emission = Color(1.0, 0.15, 0.1)
	led_mat.emission_energy_multiplier = 2.0
	led.material_override = led_mat
	led.position = Vector3(0.16, 0.18, -0.27)
	_head.add_child(led)

	var mount := MeshInstance3D.new()
	var mount_mesh := CylinderMesh.new()
	mount_mesh.top_radius = 0.1
	mount_mesh.bottom_radius = 0.1
	mount_mesh.height = 0.7
	mount_mesh.radial_segments = 8
	mount.mesh = mount_mesh
	mount.material_override = _make_mat(Color(0.15, 0.18, 0.24), 0.7)
	mount.rotation.z = PI * 0.5
	mount.position = Vector3(0, 0, 0.46)
	_head.add_child(mount)

	_spot = SpotLight3D.new()
	_spot.light_color = Color(1.0, 0.82, 0.38)
	_spot.light_energy = 0.9
	_spot.spot_range = 12.0
	_spot.spot_angle = HALF_ANGLE * 2.0
	_spot.spot_angle_attenuation = 1.35
	_spot.position = Vector3(0, -0.05, -0.18)
	_head.add_child(_spot)

	_cone_mat = StandardMaterial3D.new()
	_cone_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_cone_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	_cone_mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	_cone_mat.albedo_color = Color(1.0, 0.76, 0.24, 0.085)

	var cone := MeshInstance3D.new()
	cone.mesh = _make_sector_mesh()
	cone.material_override = _cone_mat
	cone.position = Vector3(0, -position.y + 0.045, 0)
	add_child(cone)

	_border_mat = StandardMaterial3D.new()
	_border_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_border_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	_border_mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	_border_mat.albedo_color = Color(1.0, 0.76, 0.24, 0.32)
	var border := MeshInstance3D.new()
	border.mesh = _make_sector_border_mesh()
	border.material_override = _border_mat
	border.position = Vector3(0, -position.y + 0.055, 0)
	add_child(border)

func _make_sector_mesh() -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	st.set_normal(Vector3.UP)
	st.add_vertex(Vector3.ZERO)
	var segments := 28
	for i in range(segments + 1):
		var angle := -HALF_ANGLE + (HALF_ANGLE * 2.0) * (float(i) / float(segments))
		st.add_vertex(Vector3(sin(angle), 0.0, -cos(angle)) * RANGE)
	for i in range(segments):
		st.add_index(0)
		st.add_index(i + 1)
		st.add_index(i + 2)
	return st.commit()

func _make_sector_border_mesh() -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	st.set_normal(Vector3.UP)
	var segments := 28
	var inner := RANGE - 0.09

	for i in range(segments):
		var a0 := -HALF_ANGLE + (HALF_ANGLE * 2.0) * (float(i) / float(segments))
		var a1 := -HALF_ANGLE + (HALF_ANGLE * 2.0) * (float(i + 1) / float(segments))
		var p0i := Vector3(sin(a0), 0.0, -cos(a0)) * inner
		var p0o := Vector3(sin(a0), 0.0, -cos(a0)) * RANGE
		var p1i := Vector3(sin(a1), 0.0, -cos(a1)) * inner
		var p1o := Vector3(sin(a1), 0.0, -cos(a1)) * RANGE
		_add_quad(st, p0i, p0o, p1o, p1i)

	for angle in [-HALF_ANGLE, HALF_ANGLE]:
		var dir := Vector3(sin(angle), 0.0, -cos(angle))
		var side := Vector3(cos(angle), 0.0, sin(angle)) * 0.035
		_add_quad(st, side, dir * RANGE + side, dir * RANGE - side, -side)

	return st.commit()

func _add_quad(st: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, d: Vector3) -> void:
	st.add_vertex(a)
	st.add_vertex(b)
	st.add_vertex(c)
	st.add_vertex(a)
	st.add_vertex(c)
	st.add_vertex(d)

func _make_mat(tint: Color, roughness: float, metallic := 0.0) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = tint
	mat.roughness = roughness
	mat.metallic = metallic
	return mat

func _process(_delta: float) -> void:
	var sees := false
	if game != null and is_instance_valid(game) and game.state == 0:
		for player in game.players.values():
			if is_instance_valid(player) and _sees(player):
				sees = true
				break
	_set_triggered(sees)

func _sees(player: Node3D) -> bool:
	var offset := player.global_position - global_position
	offset.y = 0.0
	var distance := offset.length()
	if distance < 0.1 or distance > RANGE:
		return false

	var forward := -global_transform.basis.z
	forward.y = 0.0
	forward = forward.normalized()
	if forward.dot(offset.normalized()) < cos(HALF_ANGLE):
		return false

	var space := get_world_3d().direct_space_state
	var query := PhysicsRayQueryParameters3D.create(
		global_position + Vector3(0, -0.15, 0),
		player.global_position + Vector3(0, 1.0, 0),
		1
	)
	var hit := space.intersect_ray(query)
	return hit.is_empty()

func _set_triggered(value: bool) -> void:
	if value == triggered:
		return
	triggered = value
	if triggered:
		_cone_mat.albedo_color = Color(1.0, 0.22, 0.16, 0.2)
		_border_mat.albedo_color = Color(1.0, 0.3, 0.22, 0.65)
		_spot.light_color = Color(1.0, 0.2, 0.15)
		_spot.light_energy = 0.9
		_lens_mat.albedo_color = Color(0.7, 0.1, 0.08)
		Audio.play_sfx("camera", -10.0, 1.0)
	else:
		_cone_mat.albedo_color = Color(1.0, 0.76, 0.24, 0.085)
		_border_mat.albedo_color = Color(1.0, 0.76, 0.24, 0.32)
		_spot.light_color = Color(1.0, 0.82, 0.38)
		_spot.light_energy = 0.9
		_lens_mat.albedo_color = Color(0.07, 0.08, 0.12)
