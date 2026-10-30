class_name PlayerFP3D
extends Player3D

const EYE_HEIGHT := 1.55
const MOUSE_SENSITIVITY := 0.0022
const PITCH_LIMIT := 1.25

var fp_camera: Camera3D
var _pitch := 0.0
var _head_bob := true
var _bob_time := 0.0
var _fp_step_accum := 0.0
var _ignore_mouse_motion := true
var _hands: Node3D
var _hand_nodes: Array[Node3D] = []
var _hand_targets: Array[Vector3] = []
var _hand_rotations: Array[Vector3] = []
var _idle_targets: Array[Vector3] = []
var _idle_rotations: Array[Vector3] = []

func _ready() -> void:
	super._ready()
	_capture_mouse()

func _capture_mouse() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	_ignore_mouse_motion = true

func _build_visual() -> void:
	super._build_visual()
	_visual.visible = false

	fp_camera = Camera3D.new()
	fp_camera.name = "FPCamera"
	fp_camera.position = Vector3(0.0, EYE_HEIGHT, 0.0)
	fp_camera.fov = 76.0
	fp_camera.near = 0.05
	fp_camera.far = 90.0
	fp_camera.current = true
	add_child(fp_camera)

	_build_hands()

func _build_hands() -> void:
	_hands = Node3D.new()
	_hands.name = "Hands"
	fp_camera.add_child(_hands)

	var glove := _make_mat(Color(0.12, 0.10, 0.19), 0.52)
	var knuckle := _make_mat(Color(0.19, 0.15, 0.29), 0.48)
	var cuff := _make_mat(Color(0.34, 0.24, 0.62), 0.55)

	for side in [-1.0, 1.0]:
		var hand := Node3D.new()
		hand.name = "LeftHand" if side < 0.0 else "RightHand"
		_hands.add_child(hand)
		_hand_nodes.append(hand)

		var palm := MeshInstance3D.new()
		var palm_mesh := BoxMesh.new()
		palm_mesh.size = Vector3(0.16, 0.13, 0.21)
		palm.mesh = palm_mesh
		palm.material_override = glove
		hand.add_child(palm)

		var back := MeshInstance3D.new()
		var back_mesh := BoxMesh.new()
		back_mesh.size = Vector3(0.13, 0.025, 0.13)
		back.mesh = back_mesh
		back.material_override = knuckle
		back.position = Vector3(0, 0.075, 0.01)
		hand.add_child(back)

		for i in range(3):
			var finger := MeshInstance3D.new()
			var finger_mesh := BoxMesh.new()
			finger_mesh.size = Vector3(0.04, 0.05, 0.13)
			finger.mesh = finger_mesh
			finger.material_override = knuckle
			finger.position = Vector3(-0.048 + float(i) * 0.048, -0.005, -0.155)
			hand.add_child(finger)

		var thumb := MeshInstance3D.new()
		var thumb_mesh := BoxMesh.new()
		thumb_mesh.size = Vector3(0.045, 0.055, 0.11)
		thumb.mesh = thumb_mesh
		thumb.material_override = knuckle
		thumb.position = Vector3(0.095 * side, -0.01, -0.075)
		thumb.rotation.z = 0.35 * side
		hand.add_child(thumb)

		var sleeve := MeshInstance3D.new()
		var sleeve_mesh := CylinderMesh.new()
		sleeve_mesh.top_radius = 0.07
		sleeve_mesh.bottom_radius = 0.09
		sleeve_mesh.height = 0.22
		sleeve_mesh.radial_segments = 10
		sleeve.mesh = sleeve_mesh
		sleeve.material_override = cuff
		sleeve.rotation.x = PI * 0.5
		sleeve.position = Vector3(0.0, -0.01, 0.17)
		hand.add_child(sleeve)

		var idle_pos := Vector3(0.36 * side, -0.44, -1.05)
		var carry_pos := Vector3(0.50 * side, -0.40, -1.65)
		var idle_rot := Vector3(-0.12, 0.10 * side, 0.08 * side)
		var carry_rot := Vector3(-0.05, 0.06 * side, 0.25 * side)
		_idle_targets.append(idle_pos)
		_idle_rotations.append(idle_rot)
		_hand_targets.append(carry_pos)
		_hand_rotations.append(carry_rot)
		hand.scale = Vector3(0.82, 0.82, 0.82)
		hand.position = idle_pos
		hand.rotation = idle_rot

func _physics_process(delta: float) -> void:
	if game == null or not is_instance_valid(game):
		return
	if game.state != 0:
		velocity = Vector3.ZERO
		return

	var input := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	var direction := transform.basis * Vector3(input.x, 0.0, input.y)
	if direction.length() > 1.0:
		direction = direction.normalized()

	var carry := float(game.carry_multiplier_for(game_id))
	velocity = direction * SPEED * carry
	move_and_slide()

	global_position.x = clampf(global_position.x, -12.2, 12.2)
	global_position.y = 0.0
	global_position.z = clampf(global_position.z, -8.2, 8.2)

	var moving := direction.length() > 0.08
	_bob_time += delta * (10.0 if moving else 2.0)
	var bob_amount := 0.016 if _head_bob and moving else 0.0
	if carry < 0.99:
		bob_amount *= 0.55
	var bob_target := sin(_bob_time) * bob_amount
	var sway_target := sin(_bob_time * 0.5) * (0.006 if moving else 0.0)
	fp_camera.position.y = lerpf(fp_camera.position.y, EYE_HEIGHT + bob_target, minf(1.0, 12.0 * delta))
	fp_camera.position.x = lerpf(fp_camera.position.x, sway_target, minf(1.0, 10.0 * delta))

	var carrying_crate: bool = game.crate != null and game.crate.holder_ids.has(game_id) and not game.crate.delivered
	_update_hands(delta, moving, carrying_crate)

	if moving:
		_fp_step_accum += delta
		var interval := 0.32 / clampf(carry, 0.45, 1.0)
		if _fp_step_accum >= interval:
			_fp_step_accum = 0.0
			Audio.play_sfx("step", -23.0, randf_range(0.9, 1.08))
	else:
		_fp_step_accum = 0.0

func _update_hands(delta: float, moving: bool, carrying: bool) -> void:
	if _hand_nodes.is_empty():
		return
	var bob := sin(_bob_time * 0.5) * (0.012 if moving else 0.0)
	var weight := minf(1.0, 10.0 * delta)
	for i in range(_hand_nodes.size()):
		var hand := _hand_nodes[i]
		var target := _hand_targets[i] if carrying else _idle_targets[i]
		target.y += bob
		var target_rot := _hand_rotations[i] if carrying else _idle_rotations[i]
		hand.position = hand.position.lerp(target, weight)
		hand.rotation = hand.rotation.lerp(target_rot, weight)

func _unhandled_input(event: InputEvent) -> void:
	if game == null or not is_instance_valid(game):
		return
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED and game.state == 0:
		if _ignore_mouse_motion:
			_ignore_mouse_motion = false
			get_viewport().set_input_as_handled()
			return
		rotation.y -= event.relative.x * MOUSE_SENSITIVITY
		_pitch = clampf(_pitch - event.relative.y * MOUSE_SENSITIVITY, -PITCH_LIMIT, PITCH_LIMIT)
		fp_camera.rotation.x = _pitch
		get_viewport().set_input_as_handled()
		return
	if event is InputEventMouseButton and event.pressed and game.state == 0 and Input.mouse_mode != Input.MOUSE_MODE_CAPTURED:
		_capture_mouse()
		get_viewport().set_input_as_handled()
		return
	if event.is_action_pressed("interact") and game.state == 0:
		get_viewport().set_input_as_handled()
		game.toggle_grab(self)
		return
	if event is InputEventKey and event.pressed and not event.echo and event.physical_keycode == KEY_H:
		_head_bob = not _head_bob
		get_viewport().set_input_as_handled()
