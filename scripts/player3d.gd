class_name Player3D
extends CharacterBody3D

const SPEED := 5.2
const GRAB_RANGE := 2.6

var player_index := 0
var game_id := 1
var game: Node = null
var color := Color(0.545, 0.361, 0.965)

var _visual: Node3D
var _body_mat: StandardMaterial3D
var _anim_time := 0.0
var _step_accum := 0.0

func _ready() -> void:
	collision_layer = 2
	collision_mask = 1
	_build_collision()
	_build_visual()
	add_to_group("player3d")

func _build_collision() -> void:
	var shape := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.42
	capsule.height = 1.45
	shape.shape = capsule
	shape.position = Vector3(0, 0.725, 0)
	add_child(shape)

func _build_visual() -> void:
	_visual = Node3D.new()
	_visual.name = "Visual"
	_visual.scale = Vector3(1.18, 1.18, 1.18)
	_visual.rotation.y = PI
	add_child(_visual)

	_body_mat = _make_mat(color, 0.58, 0.05)

	var body := MeshInstance3D.new()
	var body_mesh := CapsuleMesh.new()
	body_mesh.radius = 0.48
	body_mesh.height = 1.28
	body_mesh.radial_segments = 16
	body_mesh.rings = 8
	body.mesh = body_mesh
	body.material_override = _body_mat
	body.position = Vector3(0, 0.84, 0)
	_visual.add_child(body)

	var backpack := MeshInstance3D.new()
	var pack_mesh := BoxMesh.new()
	pack_mesh.size = Vector3(0.5, 0.62, 0.26)
	backpack.mesh = pack_mesh
	backpack.material_override = _make_mat(color.darkened(0.38), 0.7)
	backpack.position = Vector3(0, 0.82, 0.4)
	_visual.add_child(backpack)

	var visor := MeshInstance3D.new()
	var visor_mesh := SphereMesh.new()
	visor_mesh.radius = 0.32
	visor_mesh.height = 0.44
	visor_mesh.radial_segments = 16
	visor_mesh.rings = 8
	visor.mesh = visor_mesh
	visor.material_override = _make_mat(Color(0.03, 0.035, 0.06), 0.28, 0.35)
	visor.position = Vector3(0, 1.0, -0.5)
	visor.scale = Vector3(1.18, 0.84, 0.25)
	_visual.add_child(visor)

	var eye_mat := _make_mat(Color(0.96, 0.98, 1.0), 0.3)
	eye_mat.emission_enabled = true
	eye_mat.emission = Color(0.7, 0.85, 1.0)
	eye_mat.emission_energy_multiplier = 1.1
	for side in [-1.0, 1.0]:
		var eye := MeshInstance3D.new()
		var eye_mesh := SphereMesh.new()
		eye_mesh.radius = 0.065
		eye_mesh.height = 0.13
		eye_mesh.radial_segments = 10
		eye_mesh.rings = 6
		eye.mesh = eye_mesh
		eye.material_override = eye_mat
		eye.position = Vector3(0.125 * side, 1.0, -0.61)
		_visual.add_child(eye)

	var foot_mat := _make_mat(color.darkened(0.55), 0.72)
	for side in [-1.0, 1.0]:
		var foot := MeshInstance3D.new()
		var foot_mesh := SphereMesh.new()
		foot_mesh.radius = 0.17
		foot_mesh.height = 0.26
		foot_mesh.radial_segments = 12
		foot_mesh.rings = 6
		foot.mesh = foot_mesh
		foot.material_override = foot_mat
		foot.position = Vector3(0.23 * side, 0.11, 0.02)
		foot.scale = Vector3(1.0, 0.72, 1.18)
		_visual.add_child(foot)

	var shadow := MeshInstance3D.new()
	var shadow_mesh := CylinderMesh.new()
	shadow_mesh.top_radius = 0.56
	shadow_mesh.bottom_radius = 0.56
	shadow_mesh.height = 0.012
	shadow_mesh.radial_segments = 20
	shadow.mesh = shadow_mesh
	var shadow_mat := StandardMaterial3D.new()
	shadow_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	shadow_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	shadow_mat.albedo_color = Color(0.0, 0.0, 0.0, 0.28)
	shadow.material_override = shadow_mat
	shadow.position = Vector3(0, 0.025, 0)
	add_child(shadow)

func _make_mat(tint: Color, roughness: float, metallic := 0.0) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = tint
	mat.roughness = roughness
	mat.metallic = metallic
	return mat

func _physics_process(delta: float) -> void:
	if game == null or not is_instance_valid(game):
		return
	if game.state != 0:
		velocity = Vector3.ZERO
		return

	var input := Input.get_vector(_action("left"), _action("right"), _action("up"), _action("down"))
	var direction := Vector3(input.x, 0.0, input.y)
	if direction.length() > 1.0:
		direction = direction.normalized()

	var carry := float(game.carry_multiplier_for(game_id))
	velocity = direction * SPEED * carry
	move_and_slide()

	global_position.x = clampf(global_position.x, -12.2, 12.2)
	global_position.y = 0.0
	global_position.z = clampf(global_position.z, -8.2, 8.2)

	var moving := direction.length() > 0.08
	_anim_time += delta
	if moving:
		var target_yaw := atan2(-direction.x, -direction.z)
		_visual.rotation.y = lerp_angle(_visual.rotation.y, target_yaw, minf(1.0, 14.0 * delta))
		_visual.position.y = lerpf(_visual.position.y, -absf(sin(_anim_time * 11.0)) * 0.055, minf(1.0, 16.0 * delta))
	else:
		_visual.position.y = lerpf(_visual.position.y, sin(_anim_time * 2.4) * 0.012, minf(1.0, 8.0 * delta))

	if moving:
		_step_accum += delta
		var interval := 0.3 / clampf(carry, 0.45, 1.0)
		if _step_accum >= interval:
			_step_accum = 0.0
			Audio.play_sfx("step", -23.0, randf_range(0.9, 1.08))
	else:
		_step_accum = 0.0

func _action(suffix: String) -> String:
	return ("move_" if player_index == 0 else "move2_") + suffix

func _interact_action() -> String:
	return "interact" if player_index == 0 else "interact2"

func _unhandled_input(event: InputEvent) -> void:
	if game == null or game.state != 0:
		return
	if event.is_action_pressed(_interact_action()):
		get_viewport().set_input_as_handled()
		game.toggle_grab(self)
