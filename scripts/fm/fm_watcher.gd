class_name FMWatcher
extends CharacterBody3D

## El Vigilante: se mueve cuando no lo observan.
## Esta versión es offline, pero la lógica está separada del jugador
## para poder moverla después a un servidor autoritativo.

enum State { DORMANT, PATROL, INVESTIGATE, CHASE, SEARCH }

@export var patrol_speed := 1.35
@export var investigate_speed := 2.2
@export var chase_speed := 3.55
@export var vision_distance := 18.0
@export var vision_dot := 0.32
@export var catch_distance := 1.25

var game: Node = null
var player: FMPlayer = null
var targets: Array[Node3D] = []
var state: State = State.DORMANT
var state_timer := 4.0
var patrol_points: Array[Vector3] = []
var patrol_index := 0
var target := Vector3.ZERO
var last_seen := Vector3.ZERO
var observed := false

var _visual: Node3D
var _eye_mat: StandardMaterial3D
var _time := 0.0
var _wait_timer := 0.0
var _repath_timer := 0.0

func _ready() -> void:
	collision_layer = 8
	collision_mask = 1
	add_to_group("fm_watcher")
	_build_collision()
	_build_visual()

func _build_collision() -> void:
	var shape := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.4
	capsule.height = 2.35
	shape.shape = capsule
	shape.position = Vector3(0, 1.175, 0)
	add_child(shape)

func _build_visual() -> void:
	_visual = Node3D.new()
	_visual.name = "Visual"
	add_child(_visual)

	var dark := StandardMaterial3D.new()
	dark.albedo_color = Color(0.018, 0.022, 0.03, 1.0)
	dark.roughness = 0.72
	dark.metallic = 0.15

	var pale := StandardMaterial3D.new()
	pale.albedo_color = Color(0.18, 0.17, 0.15, 1.0)
	pale.roughness = 0.86

	var body := MeshInstance3D.new()
	var body_mesh := CapsuleMesh.new()
	body_mesh.radius = 0.34
	body_mesh.height = 1.8
	body_mesh.radial_segments = 12
	body_mesh.rings = 8
	body.mesh = body_mesh
	body.material_override = dark
	body.position = Vector3(0, 1.18, 0)
	body.scale = Vector3(0.82, 1.18, 0.62)
	_visual.add_child(body)

	var head := MeshInstance3D.new()
	var head_mesh := SphereMesh.new()
	head_mesh.radius = 0.27
	head_mesh.height = 0.52
	head_mesh.radial_segments = 12
	head_mesh.rings = 8
	head.mesh = head_mesh
	head.material_override = pale
	head.position = Vector3(0, 2.22, 0)
	head.scale = Vector3(0.82, 1.08, 0.72)
	_visual.add_child(head)

	var face := MeshInstance3D.new()
	var face_mesh := BoxMesh.new()
	face_mesh.size = Vector3(0.32, 0.12, 0.04)
	face.mesh = face_mesh
	var face_mat := StandardMaterial3D.new()
	face_mat.albedo_color = Color(0.01, 0.01, 0.012, 1.0)
	face_mat.roughness = 0.2
	face.material_override = face_mat
	face.position = Vector3(0, 2.22, -0.255)
	_visual.add_child(face)

	_eye_mat = StandardMaterial3D.new()
	_eye_mat.albedo_color = Color(0.8, 0.18, 0.06, 1.0)
	_eye_mat.emission_enabled = true
	_eye_mat.emission = Color(1.0, 0.18, 0.05)
	_eye_mat.emission_energy_multiplier = 1.8
	for side in [-1.0, 1.0]:
		var eye := MeshInstance3D.new()
		var eye_mesh := SphereMesh.new()
		eye_mesh.radius = 0.038
		eye_mesh.height = 0.076
		eye_mesh.radial_segments = 8
		eye_mesh.rings = 4
		eye.mesh = eye_mesh
		eye.material_override = _eye_mat
		eye.position = Vector3(0.09 * side, 2.23, -0.285)
		_visual.add_child(eye)

	for side in [-1.0, 1.0]:
		var arm := MeshInstance3D.new()
		var arm_mesh := CapsuleMesh.new()
		arm_mesh.radius = 0.075
		arm_mesh.height = 1.35
		arm_mesh.radial_segments = 8
		arm_mesh.rings = 4
		arm.mesh = arm_mesh
		arm.material_override = dark
		arm.position = Vector3(0.38 * side, 1.1, 0.02)
		arm.rotation_degrees.z = 7.0 * side
		_visual.add_child(arm)

		var leg := MeshInstance3D.new()
		var leg_mesh := CapsuleMesh.new()
		leg_mesh.radius = 0.09
		leg_mesh.height = 0.9
		leg_mesh.radial_segments = 8
		leg_mesh.rings = 4
		leg.mesh = leg_mesh
		leg.material_override = dark
		leg.position = Vector3(0.15 * side, 0.45, 0.0)
		_visual.add_child(leg)

	var shadow := MeshInstance3D.new()
	var shadow_mesh := CylinderMesh.new()
	shadow_mesh.top_radius = 0.5
	shadow_mesh.bottom_radius = 0.5
	shadow_mesh.height = 0.01
	shadow_mesh.radial_segments = 16
	shadow.mesh = shadow_mesh
	var shadow_mat := StandardMaterial3D.new()
	shadow_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	shadow_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	shadow_mat.albedo_color = Color(0, 0, 0, 0.35)
	shadow.material_override = shadow_mat
	shadow.position.y = 0.012
	add_child(shadow)

	var glow := OmniLight3D.new()
	glow.light_color = Color(1.0, 0.2, 0.07)
	glow.light_energy = 0.45
	glow.omni_range = 1.6
	glow.shadow_enabled = false
	glow.position = Vector3(0, 2.22, -0.35)
	_visual.add_child(glow)

func set_game(value: Node) -> void:
	game = value

func set_player(value: FMPlayer) -> void:
	player = value
	if value != null and targets.is_empty():
		targets = [value]

func set_targets(values: Array[Node3D]) -> void:
	targets = values
	if player == null and not targets.is_empty():
		player = targets[0] as FMPlayer

func set_patrol_points(points: Array[Vector3]) -> void:
	patrol_points = points

func apply_network_state(pos: Vector3, yaw: float, state_value: int, observed_value: bool) -> void:
	global_position = pos
	rotation.y = yaw
	state = state_value
	observed = observed_value
	if _eye_mat != null:
		_eye_mat.emission_energy_multiplier = 2.8 if observed else 1.8

func _physics_process(delta: float) -> void:
	if game == null or not is_instance_valid(game):
		return
	var target_player := _nearest_target()
	if target_player == null:
		return
	if game.state != 0:
		velocity = Vector3.ZERO
		return

	_time += delta
	observed = _is_observed_by_targets()
	if _eye_mat != null:
		_eye_mat.emission_energy_multiplier = 2.8 if observed else 1.8

	if observed and state != State.DORMANT:
		velocity = Vector3.ZERO
		_face_point(target_player.global_position, delta, true)
		return

	var sees := _can_see_target(target_player)
	if sees:
		if state != State.CHASE:
			state = State.CHASE
			state_timer = 0.0
			Audio.play_sfx("camera", -24.0, 0.7)
		last_seen = target_player.global_position
		target = last_seen
		if global_position.distance_to(target_player.global_position) <= catch_distance and not bool(target_player.get("hidden")):
			if game.has_method("on_player_caught"):
				game.on_player_caught(target_player)
			return
	elif state == State.CHASE:
		state = State.SEARCH
		state_timer = 8.0
		target = last_seen

	match state:
		State.DORMANT:
			state_timer -= delta
			if state_timer <= 0.0:
				state = State.PATROL
				_choose_patrol_target()
		State.PATROL:
			_update_patrol(delta)
		State.INVESTIGATE:
			state_timer -= delta
			if _move_toward(target, investigate_speed, delta):
				velocity = Vector3.ZERO
				_wait_timer += delta
				_face_point(target, delta, false)
				if _wait_timer > 2.0 or state_timer <= 0.0:
					state = State.PATROL
					_wait_timer = 0.0
					_choose_patrol_target()
		State.CHASE:
			target = target_player.global_position
			_move_toward(target, chase_speed, delta)
		State.SEARCH:
			state_timer -= delta
			if _move_toward(last_seen, investigate_speed, delta):
				velocity = Vector3.ZERO
				_wait_timer += delta
				_face_point(last_seen + Vector3(sin(_time * 1.3) * 4.0, 0, cos(_time * 0.9) * 4.0), delta, false)
				if state_timer <= 0.0 or _wait_timer > 4.0:
					state = State.PATROL
					_wait_timer = 0.0
					_choose_patrol_target()


func _update_patrol(delta: float) -> void:
	if patrol_points.is_empty():
		velocity = Vector3.ZERO
		return
	if target == Vector3.ZERO:
		_choose_patrol_target()
	if _move_toward(target, patrol_speed, delta):
		velocity = Vector3.ZERO
		_wait_timer += delta
		_face_point(target + Vector3(0, 0, -1), delta, false)
		if _wait_timer > 1.4:
			_wait_timer = 0.0
			patrol_index = (patrol_index + 1) % patrol_points.size()
			_choose_patrol_target()

func _choose_patrol_target() -> void:
	if patrol_points.is_empty():
		return
	target = patrol_points[patrol_index % patrol_points.size()]

func _move_toward(destination: Vector3, speed: float, delta: float) -> bool:
	var offset := destination - global_position
	offset.y = 0.0
	if offset.length() <= 0.55:
		velocity = Vector3.ZERO
		return true
	var direction := offset.normalized()
	velocity = direction * speed
	move_and_slide()
	_face_point(destination, delta, false)
	return false

func _face_point(point: Vector3, delta: float, intense: bool) -> void:
	var offset := point - global_position
	offset.y = 0.0
	if offset.length() < 0.05:
		return
	var target_yaw := atan2(-offset.x, -offset.z)
	rotation.y = lerp_angle(rotation.y, target_yaw, clampf(delta * (10.0 if intense else 5.0), 0.0, 1.0))
	if _visual != null:
		_visual.position.y = lerpf(_visual.position.y, sin(_time * 1.7) * 0.012, clampf(delta * 3.0, 0.0, 1.0))

func _nearest_target() -> Node3D:
	if targets.is_empty():
		if player != null and is_instance_valid(player):
			return player
		return null
	var best: Node3D = null
	var best_distance := INF
	for candidate in targets:
		if candidate == null or not is_instance_valid(candidate):
			continue
		if bool(candidate.get("hidden")):
			continue
		var distance := global_position.distance_squared_to(candidate.global_position)
		if distance < best_distance:
			best = candidate
			best_distance = distance
	if best == null:
		for candidate in targets:
			if candidate != null and is_instance_valid(candidate):
				return candidate
	return best

func _is_observed_by_targets() -> bool:
	if targets.is_empty():
		return player != null and is_instance_valid(player) and player.is_observing(self)
	for candidate in targets:
		if candidate == null or not is_instance_valid(candidate):
			continue
		if bool(candidate.get("hidden")):
			continue
		if candidate == player:
			if player.is_observing(self):
				return true
		elif bool(candidate.get("observing_watcher")):
			return true
	return false

func _can_see_target(candidate: Node3D) -> bool:
	if candidate == null or bool(candidate.get("hidden")):
		return false
	var eye := global_position + Vector3(0, 1.85, 0)
	var chest := candidate.global_position + Vector3(0, 1.0, 0)
	var to_player := chest - eye
	var distance := to_player.length()
	if distance > vision_distance or distance < 0.05:
		return false
	var forward := -global_transform.basis.z
	if forward.dot(to_player / distance) < vision_dot:
		return false
	var query := PhysicsRayQueryParameters3D.create(eye, chest)
	query.collision_mask = 1
	query.exclude = [get_rid()]
	var hit := get_world_3d().direct_space_state.intersect_ray(query)
	return hit.is_empty()

func _can_see_player() -> bool:
	return _can_see_target(_nearest_target())


func hear_noise(position: Vector3, radius: float) -> void:
	if game == null or game.state != 0:
		return
	if state == State.CHASE:
		return
	var distance := global_position.distance_to(position)
	if distance > radius:
		return
	state = State.INVESTIGATE
	target = position
	last_seen = position
	state_timer = 7.0
	_wait_timer = 0.0

func is_observed() -> bool:
	return observed
