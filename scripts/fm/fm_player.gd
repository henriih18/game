class_name FMPlayer
extends CharacterBody3D

## Controlador de primera persona del vertical slice.
## Deliberadamente offline y de un jugador: la capa de red se añadirá
## después sin meter RPCs dentro de la lógica de movimiento.

@export var walk_speed := 3.4
@export var sprint_speed := 5.6
@export var crouch_speed := 1.7
@export var mouse_sensitivity := 0.0022
@export var eye_height := 1.62
@export var crouch_eye_height := 1.08
@export var max_battery := 100.0
@export var battery_drain := 2.1
@export var interact_distance := 2.8

var game: Node = null
var camera: Camera3D
var flashlight: SpotLight3D
var carried_item: Node3D = null

var battery := 100.0
var flashlight_on := true
var stamina := 100.0
var hidden := false
var hide_spot: Node3D = null

var _carry_anchor: Node3D
var _interact_ray: RayCast3D
var _pitch := 0.0
var _current_eye := 1.62
var _bob_time := 0.0
var _step_accum := 0.0
var _mouse_ignore_time := 0.35
var _prompt := ""
var _move_speed := 0.0

func _ready() -> void:
	collision_layer = 2
	collision_mask = 1
	add_to_group("fm_player")
	_build_collision()
	_build_camera()
	_build_flashlight()
	_build_interaction()
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _build_collision() -> void:
	var shape := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.38
	capsule.height = 1.7
	shape.shape = capsule
	shape.position = Vector3(0, 0.85, 0)
	add_child(shape)

func _build_camera() -> void:
	camera = Camera3D.new()
	camera.name = "FPCamera"
	camera.position = Vector3(0, eye_height, 0)
	camera.fov = 76.0
	camera.near = 0.05
	camera.far = 70.0
	camera.current = true
	add_child(camera)
	_current_eye = eye_height

	_carry_anchor = Node3D.new()
	_carry_anchor.name = "CarryAnchor"
	_carry_anchor.position = Vector3(0.0, -0.32, -1.05)
	camera.add_child(_carry_anchor)

func _build_flashlight() -> void:
	flashlight = SpotLight3D.new()
	flashlight.name = "Flashlight"
	flashlight.position = Vector3(0.18, -0.12, -0.15)
	flashlight.light_color = Color(1.0, 0.88, 0.68)
	flashlight.light_energy = 4.2
	flashlight.spot_range = 18.0
	flashlight.spot_angle = 24.0
	flashlight.spot_attenuation = 1.15
	flashlight.spot_angle_attenuation = 0.9
	flashlight.shadow_enabled = true
	flashlight.light_volumetric_fog_energy = 1.2
	camera.add_child(flashlight)

func _build_interaction() -> void:
	_interact_ray = RayCast3D.new()
	_interact_ray.name = "InteractRay"
	_interact_ray.target_position = Vector3(0, 0, -interact_distance)
	_interact_ray.collision_mask = 1 | 4
	_interact_ray.collide_with_areas = false
	_interact_ray.enabled = true
	camera.add_child(_interact_ray)

func get_carry_anchor() -> Node3D:
	return _carry_anchor

func set_game(value: Node) -> void:
	game = value

func _physics_process(delta: float) -> void:
	_mouse_ignore_time = maxf(0.0, _mouse_ignore_time - delta)
	if game == null or not is_instance_valid(game):
		return
	if game.state != 0:
		velocity = Vector3.ZERO
		return
	if hidden:
		velocity = Vector3.ZERO
		return

	var input := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	var direction := transform.basis * Vector3(input.x, 0.0, input.y)
	if direction.length() > 1.0:
		direction = direction.normalized()

	var crouching := Input.is_action_pressed("crouch")
	var wants_sprint := Input.is_action_pressed("sprint") and not crouching and direction.length() > 0.1
	var sprinting := wants_sprint and stamina > 1.0
	var speed := walk_speed
	if crouching:
		speed = crouch_speed
	elif sprinting:
		speed = sprint_speed

	if carried_item != null:
		speed *= 0.58 if not crouching else 0.72

	if sprinting:
		stamina = maxf(0.0, stamina - 18.0 * delta)
	else:
		stamina = minf(100.0, stamina + (10.0 if crouching else 14.0) * delta)

	_move_speed = speed
	velocity = direction * speed
	move_and_slide()

	if game.has_method("clamp_player"):
		game.clamp_player(self)

	_animate_camera(delta, direction.length() > 0.08, crouching, sprinting)
	_update_flashlight(delta)
	_update_footsteps(delta, direction.length() > 0.08, sprinting, crouching)

func _animate_camera(delta: float, moving: bool, crouching: bool, sprinting: bool) -> void:
	var target_eye := crouch_eye_height if crouching else eye_height
	_current_eye = lerpf(_current_eye, target_eye, clampf(delta * 9.0, 0.0, 1.0))
	camera.position.y = _current_eye
	if moving:
		_bob_time += delta * (12.0 if sprinting else (7.0 if not crouching else 5.0))
		var bob_amount := 0.018 if not sprinting else 0.032
		camera.position.y += sin(_bob_time) * bob_amount
		camera.position.x = cos(_bob_time * 0.5) * bob_amount * 0.6
	else:
		camera.position.x = lerpf(camera.position.x, 0.0, clampf(delta * 8.0, 0.0, 1.0))

func _update_flashlight(delta: float) -> void:
	if flashlight_on and battery > 0.0:
		battery = maxf(0.0, battery - battery_drain * delta)
		if battery <= 0.0:
			flashlight_on = false
	flashlight.visible = flashlight_on and battery > 0.0

func _update_footsteps(delta: float, moving: bool, sprinting: bool, crouching: bool) -> void:
	if not moving:
		_step_accum = 0.0
		return
	_step_accum += delta
	var interval := 0.48
	var noise_radius := 7.0
	if sprinting:
		interval = 0.31
		noise_radius = 12.0
	elif crouching:
		interval = 0.72
		noise_radius = 3.0
	if carried_item != null:
		interval *= 1.18
		noise_radius += 2.0
	if _step_accum < interval:
		return
	_step_accum = 0.0
	Audio.play_sfx("step", -19.0 if not sprinting else -15.0, randf_range(0.92, 1.06))
	if game.has_method("emit_noise"):
		game.emit_noise(global_position, noise_radius, "step")

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		if _mouse_ignore_time > 0.0:
			return
		var motion := event as InputEventMouseMotion
		rotate_y(-motion.relative.x * mouse_sensitivity)
		_pitch = clampf(_pitch - motion.relative.y * mouse_sensitivity, -1.22, 1.22)
		camera.rotation.x = _pitch
		return

	if event.is_action_pressed("flashlight"):
		if battery > 0.0:
			flashlight_on = not flashlight_on
			Audio.play_sfx("click", -14.0)
		get_viewport().set_input_as_handled()
		return

	if event.is_action_pressed("interact"):
		get_viewport().set_input_as_handled()
		_interact()
		return

	if event.is_action_pressed("drop") and carried_item != null:
		get_viewport().set_input_as_handled()
		_drop_item()

func _interact() -> void:
	if hidden:
		exit_hide()
		return
	if carried_item != null:
		_drop_item()
		return
	if _try_pickup():
		return
	_try_hide()

func _try_pickup() -> bool:
	var best: Node3D = null
	var best_distance := interact_distance
	for node in get_tree().get_nodes_in_group("fm_carry_item"):
		var item := node as FMCarryItem
		if item == null or item.carried_by != null:
			continue
		var distance := global_position.distance_to(item.global_position)
		if distance <= best_distance and _has_line_of_sight(item.global_position + Vector3(0, 0.1, 0)):
			best = item
			best_distance = distance
	if best == null:
		return false
	var item := best as FMCarryItem
	if item.pickup(self):
		carried_item = item
		return true
	return false

func _try_hide() -> void:
	var best: Node3D = null
	var best_distance := 2.4
	for node in get_tree().get_nodes_in_group("fm_hiding_spot"):
		var spot := node as FMHidingSpot
		if spot == null or not spot.can_use(self):
			continue
		var distance := global_position.distance_to(spot.global_position)
		if distance <= best_distance:
			best = spot
			best_distance = distance
	if best != null:
		var spot := best as FMHidingSpot
		spot.hide_player(self)

func _has_line_of_sight(target: Vector3) -> bool:
	var query := PhysicsRayQueryParameters3D.create(camera.global_position, target)
	query.collision_mask = 1
	query.exclude = [get_rid()]
	var hit := get_world_3d().direct_space_state.intersect_ray(query)
	return hit.is_empty()

func _drop_item() -> void:
	if carried_item == null:
		return
	var item := carried_item as FMCarryItem
	carried_item = null
	if item != null:
		item.drop(-camera.global_transform.basis.z)

func hide_in(spot: FMHidingSpot) -> void:
	if hidden:
		return
	hidden = true
	hide_spot = spot
	velocity = Vector3.ZERO
	collision_layer = 0
	collision_mask = 0
	global_position = spot.get_hide_point()
	var dir := spot.get_look_direction()
	rotation.y = atan2(-dir.x, -dir.z)
	_pitch = 0.0
	camera.rotation.x = 0.0
	camera.position = Vector3(0, 1.34, 0)
	_current_eye = 1.34
	Audio.play_sfx("click", -16.0, 0.8)
	if game != null and game.has_method("on_player_hidden"):
		game.on_player_hidden(true)

func exit_hide() -> void:
	if not hidden:
		return
	var spot := hide_spot
	hidden = false
	hide_spot = null
	collision_layer = 2
	collision_mask = 1
	if spot != null and is_instance_valid(spot):
		global_position = spot.get_exit_point()
		spot.release_player(self)
	_current_eye = eye_height
	camera.position.y = eye_height
	Audio.play_sfx("click", -16.0, 1.1)
	if game != null and game.has_method("on_player_hidden"):
		game.on_player_hidden(false)

func is_observing(target: Node3D) -> bool:
	if target == null or not is_instance_valid(target):
		return false
	var to_target := target.global_position + Vector3(0, 1.35, 0) - camera.global_position
	var distance := to_target.length()
	if distance > 18.0 or distance < 0.01:
		return false
	var forward := -camera.global_transform.basis.z
	if forward.dot(to_target / distance) < 0.72:
		return false
	if not flashlight_on and distance > 8.0:
		return false
	var query := PhysicsRayQueryParameters3D.create(camera.global_position, target.global_position + Vector3(0, 1.35, 0))
	query.collision_mask = 1
	query.exclude = [get_rid()]
	var hit := get_world_3d().direct_space_state.intersect_ray(query)
	return hit.is_empty()

func get_interaction_prompt() -> String:
	if hidden:
		return "E   SALIR DEL ESCONDITE"
	if carried_item != null:
		return "Q   SOLTAR NÚCLEO"
	if _nearest_item() != null:
		return "E   RECOGER NÚCLEO"
	if _nearest_hiding_spot() != null:
		return "E   ESCONDERSE"
	return _prompt

func _nearest_item() -> Node3D:
	for node in get_tree().get_nodes_in_group("fm_carry_item"):
		var item := node as FMCarryItem
		if item != null and item.carried_by == null and global_position.distance_to(item.global_position) <= interact_distance:
			return item
	return null

func _nearest_hiding_spot() -> Node3D:
	for node in get_tree().get_nodes_in_group("fm_hiding_spot"):
		var spot := node as FMHidingSpot
		if spot != null and spot.can_use(self) and global_position.distance_to(spot.global_position) <= 2.4:
			return spot
	return null
