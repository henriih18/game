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
@export var stand_height := 1.7
@export var crouch_height := 1.2
@export var step_height := 0.2
@export var max_battery := 100.0
@export var battery_drain := 2.1
@export var interact_distance := 2.8
@export var inventory_capacity := 4
@export var max_carry_weight := 12.0

const FLASHLIGHT_GLB := "res://assets/models/fm/flashlight_nexus.glb"

var game: Node = null
var camera: Camera3D
var flashlight: SpotLight3D
var carried_item: Node3D = null
var inventory: Array[FMCarryItem] = []
var network_client := false
var _flashlight_model: Node3D

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
var footstep_surface_provider: Node = null
var _mouse_ignore_time := 0.35
var _prompt := ""
var _move_speed := 0.0

var _collision_shape: CollisionShape3D
var _capsule: CapsuleShape3D
var _crouched := false

enum StepPhase { NONE, LIFT, FORWARD, DOWN }
const STEP_FORWARD_MAX_TIME := 0.35
const STEP_CLEARANCE_MARGIN := 0.01

var _step_phase := StepPhase.NONE
var _step_start := Transform3D()
var _step_direction := Vector3.ZERO
var _step_speed := 0.0
var _step_elapsed := 0.0
var _step_floor_snap := 0.1

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
	_capsule = CapsuleShape3D.new()
	_capsule.radius = 0.38
	_capsule.height = stand_height
	_collision_shape = CollisionShape3D.new()
	_collision_shape.name = "CollisionShape3D"
	_collision_shape.shape = _capsule
	_collision_shape.position = Vector3(0, stand_height * 0.5, 0)
	add_child(_collision_shape)

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

	var listener := AudioListener3D.new()
	listener.name = "AudioListener"
	listener.current = true
	camera.add_child(listener)

	_carry_anchor = Node3D.new()
	_carry_anchor.name = "CarryAnchor"
	_carry_anchor.position = Vector3(0.0, -0.32, -1.05)
	camera.add_child(_carry_anchor)

func _build_flashlight() -> void:
	flashlight = SpotLight3D.new()
	flashlight.name = "Flashlight"
	flashlight.position = Vector3(0.30, -0.32, -0.61)
	flashlight.light_color = Color(1.0, 0.88, 0.68)
	flashlight.light_energy = 4.2
	flashlight.spot_range = 18.0
	flashlight.spot_angle = 24.0
	flashlight.spot_attenuation = 1.15
	flashlight.spot_angle_attenuation = 0.9
	flashlight.shadow_enabled = true
	flashlight.light_volumetric_fog_energy = 1.2
	camera.add_child(flashlight)

func set_flashlight_model(enabled: bool) -> void:
	if not enabled or _flashlight_model != null or not FileAccess.file_exists(FLASHLIGHT_GLB):
		return
	var document := GLTFDocument.new()
	var gltf_state := GLTFState.new()
	if document.append_from_file(FLASHLIGHT_GLB, gltf_state) != OK:
		push_warning("No se pudo cargar el viewmodel de linterna")
		return
	var torch := document.generate_scene(gltf_state)
	if torch == null:
		return
	for node in torch.find_children("*", "MeshInstance3D", true, false):
		var mesh_instance := node as MeshInstance3D
		mesh_instance.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		mesh_instance.gi_mode = GeometryInstance3D.GI_MODE_DISABLED
		if mesh_instance.mesh == null:
			continue
		for surface in range(mesh_instance.mesh.get_surface_count()):
			var base := mesh_instance.get_active_material(surface)
			if not (base is StandardMaterial3D):
				continue
			var tuned := (base as StandardMaterial3D).duplicate() as StandardMaterial3D
			var mat_key := (tuned.resource_name + " " + node.name).to_lower()
			if "lens" in mat_key or "glass" in mat_key or "cristal" in mat_key:
				tuned.albedo_color = Color(0.72, 0.60, 0.42, 1.0)
				tuned.emission_enabled = true
				tuned.emission = Color(1.0, 0.78, 0.48)
				tuned.emission_energy_multiplier = 0.85
				tuned.roughness = 0.24
			else:
				tuned.albedo_color = Color(0.045, 0.052, 0.062, 1.0)
				tuned.metallic = 0.45
				tuned.roughness = 0.55
			mesh_instance.set_surface_override_material(surface, tuned)
	_flashlight_model = Node3D.new()
	_flashlight_model.name = "FlashlightModel"
	# El GLB tiene la lente hacia +Z; se gira para mirar hacia delante (-Z).
	_flashlight_model.position = Vector3(0.30, -0.32, -0.56)
	_flashlight_model.rotation_degrees = Vector3(-2.0, 180.0, 7.0)
	_flashlight_model.scale = Vector3(0.37, 0.37, 0.37)
	_flashlight_model.add_child(torch)
	camera.add_child(_flashlight_model)
	var lens := MeshInstance3D.new()
	lens.name = "FlashlightLens"
	var lens_mesh := CylinderMesh.new()
	lens_mesh.top_radius = 0.024
	lens_mesh.bottom_radius = 0.024
	lens_mesh.height = 0.012
	lens.mesh = lens_mesh
	lens.rotation_degrees = Vector3(90.0, 0.0, 0.0)
	lens.position = Vector3(0.0, 0.0, 0.108)
	var lens_material := StandardMaterial3D.new()
	lens_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	lens_material.albedo_color = Color(0.72, 0.60, 0.42, 1.0)
	lens_material.emission_enabled = true
	lens_material.emission = Color(1.0, 0.78, 0.48)
	lens_material.emission_energy_multiplier = 0.45
	lens_material.cull_mode = BaseMaterial3D.CULL_DISABLED
	lens.material_override = lens_material
	_flashlight_model.add_child(lens)
	var view_fill := OmniLight3D.new()
	view_fill.name = "FlashlightViewFill"
	view_fill.position = Vector3(0.22, -0.05, -0.30)
	view_fill.light_color = Color(1.0, 0.90, 0.76)
	view_fill.light_energy = 0.10
	view_fill.omni_range = 0.40
	view_fill.shadow_enabled = false
	camera.add_child(view_fill)

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
		_reset_step_state()
		return
	if hidden:
		velocity = Vector3.ZERO
		_reset_step_state()
		return

	var input := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	var direction := transform.basis * Vector3(input.x, 0.0, input.y)
	if direction.length() > 1.0:
		direction = direction.normalized()

	_update_crouch()
	var crouching := _crouched
	var wants_sprint := Input.is_action_pressed("sprint") and not crouching and direction.length() > 0.1
	var sprinting := wants_sprint and stamina > 1.0
	var speed := walk_speed
	if crouching:
		speed = crouch_speed
	elif sprinting:
		speed = sprint_speed

	if carried_item != null:
		speed *= 0.58 if not crouching else 0.72

	var load_ratio := clampf(get_stowed_weight() / maxf(0.001, max_carry_weight), 0.0, 1.0)
	speed *= lerpf(1.0, 0.82, load_ratio)

	if sprinting:
		stamina = maxf(0.0, stamina - 18.0 * delta)
	else:
		stamina = minf(100.0, stamina + (10.0 if crouching else 14.0) * delta)

	_move_speed = speed

	if _step_phase != StepPhase.NONE:
		_advance_step(delta)
	else:
		velocity = direction * speed
		if is_on_floor():
			velocity.y = -0.5
		else:
			velocity.y -= 24.0 * delta
		move_and_slide()

		if direction.length() > 0.08 and is_on_floor():
			_try_step_up(direction)

	if game.has_method("clamp_player"):
		game.clamp_player(self)

	_animate_camera(delta, direction.length() > 0.08, crouching, sprinting)
	_update_flashlight(delta)
	_update_footsteps(delta, direction.length() > 0.08, sprinting, crouching)


func _update_crouch() -> void:
	if _capsule == null:
		return
	if Input.is_action_pressed("crouch"):
		_set_crouched(true)
	elif _crouched and _step_phase == StepPhase.NONE and _has_stand_clearance():
		_set_crouched(false)


func _set_crouched(value: bool) -> void:
	if _crouched == value or _capsule == null:
		return
	_crouched = value
	var height := crouch_height if value else stand_height
	_capsule.height = height
	_collision_shape.position.y = height * 0.5


func _has_stand_clearance() -> bool:
	if _capsule == null:
		return true
	var probe := CapsuleShape3D.new()
	probe.radius = maxf(0.05, _capsule.radius - 0.05)
	probe.height = stand_height
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = probe
	query.transform = Transform3D(
		global_transform.basis.orthonormalized(),
		global_position + Vector3.UP * (stand_height * 0.5 + 0.02)
	)
	query.collision_mask = collision_mask
	query.collide_with_bodies = true
	query.collide_with_areas = false
	query.exclude = [get_rid()]
	return get_world_3d().direct_space_state.intersect_shape(query, 1).is_empty()


func _try_step_up(direction: Vector3) -> void:
	if step_height <= 0.0 or _capsule == null:
		return
	if direction.length_squared() < 0.04:
		return
	var blocked := false
	for index in get_slide_collision_count():
		var normal := get_slide_collision(index).get_normal()
		if normal.y < 0.6:
			blocked = true
			break
	if not blocked:
		return

	var lift := Vector3.UP * (step_height + STEP_CLEARANCE_MARGIN)
	if test_move(global_transform, lift):
		return
	var flat_direction := Vector3(direction.x, 0.0, direction.z).normalized()
	var raised := global_transform.translated(lift)
	if test_move(raised, flat_direction * 0.08):
		return

	_step_phase = StepPhase.LIFT
	_step_start = global_transform
	_step_direction = flat_direction
	_step_speed = maxf(_move_speed, 0.5)
	_step_elapsed = 0.0
	velocity = Vector3.ZERO
	_step_floor_snap = floor_snap_length
	floor_snap_length = 0.0


func _advance_step(delta: float) -> void:
	match _step_phase:
		StepPhase.LIFT:
			var lift := Vector3.UP * (step_height + STEP_CLEARANCE_MARGIN)
			if test_move(global_transform, lift):
				_abort_step()
				return
			move_and_collide(lift, false, 0.001, true)
			velocity = Vector3.ZERO
			_step_phase = StepPhase.FORWARD
			_step_elapsed = 0.0
		StepPhase.FORWARD:
			_step_elapsed += delta
			velocity = _step_direction * _step_speed
			velocity.y = 0.0
			move_and_slide()
			if _step_support_ahead() or _step_elapsed >= STEP_FORWARD_MAX_TIME:
				_step_phase = StepPhase.DOWN
		StepPhase.DOWN:
			velocity = Vector3.DOWN * 12.0
			move_and_slide()
			var climbed := global_position.y >= _step_start.origin.y + step_height * 0.45
			_step_phase = StepPhase.NONE
			floor_snap_length = _step_floor_snap
			if not climbed or not is_on_floor():
				_abort_step(false)


func _step_support_ahead() -> bool:
	var from := global_position + Vector3.UP * (step_height + 0.03)
	var to := global_position + Vector3.DOWN * 0.15
	var query := PhysicsRayQueryParameters3D.create(from, to)
	query.collision_mask = collision_mask
	query.exclude = [get_rid()]
	var hit := get_world_3d().direct_space_state.intersect_ray(query)
	if hit.is_empty():
		return false
	return float(hit.position.y) >= _step_start.origin.y + step_height * 0.45


func _abort_step(restore := true) -> void:
	if restore:
		global_transform = _step_start
	floor_snap_length = _step_floor_snap
	velocity = Vector3.ZERO
	_step_phase = StepPhase.NONE


func _reset_step_state() -> void:
	if _step_phase == StepPhase.NONE:
		return
	floor_snap_length = _step_floor_snap
	velocity = Vector3.ZERO
	_step_phase = StepPhase.NONE


func is_crouched() -> bool:
	return _crouched


func get_capsule_height() -> float:
	return _capsule.height if _capsule != null else 0.0

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
	if footstep_surface_provider != null and is_instance_valid(footstep_surface_provider) and footstep_surface_provider.has_method("play_footstep"):
		if bool(footstep_surface_provider.play_footstep(sprinting, crouching, noise_radius)):
			return
	Audio.play_sfx("step", -19.0 if not sprinting else -15.0, randf_range(0.92, 1.06))
	if game.has_method("emit_noise"):
		game.emit_noise(global_position, noise_radius, "step")

func _input_locked() -> bool:
	if game == null or not is_instance_valid(game):
		return true
	return int(game.state) != 0


func _unhandled_input(event: InputEvent) -> void:
	if _input_locked():
		return
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

	if event.is_action_pressed("drop"):
		get_viewport().set_input_as_handled()
		if network_client:
			if game != null and game.has_method("request_network_drop"):
				game.request_network_drop()
		else:
			_drop_carried_or_inventory()

func _interact() -> void:
	if _input_locked():
		return
	if network_client:
		if game != null and game.has_method("request_network_interaction"):
			game.request_network_interaction()
		return
	if hidden:
		exit_hide()
		return
	if _try_interactable():
		return
	if _try_pickup():
		return
	if carried_item != null:
		_drop_item()
		return
	_try_hide()

func _try_interactable() -> bool:
	var best: Node3D = null
	var best_distance := interact_distance
	for node in get_tree().get_nodes_in_group("fm_interactable"):
		if node == null or not is_instance_valid(node):
			continue
		if not node.has_method("can_interact") or not node.has_method("get_interaction_position"):
			continue
		if not node.can_interact(self):
			continue
		var point: Vector3 = node.get_interaction_position()
		var distance := global_position.distance_to(point)
		if distance <= best_distance and _has_line_of_sight(point, node):
			best = node as Node3D
			best_distance = distance
	if best == null:
		return false
	if not best.has_method("interact"):
		return false
	best.interact(self)
	return true

func _try_pickup() -> bool:
	var best: Node3D = null
	var best_distance := interact_distance
	for node in get_tree().get_nodes_in_group("fm_carry_item"):
		var item := node as FMCarryItem
		if item == null or item.carried_by != null:
			continue
		var distance := global_position.distance_to(item.global_position)
		if distance <= best_distance and _has_line_of_sight(item.global_position + Vector3(0, 0.1, 0), item):
			best = item
			best_distance = distance
	if best == null:
		return false
	var item := best as FMCarryItem
	if item.size_class == "SMALL":
		if inventory.size() >= inventory_capacity:
			_notify_game("INVENTARIO LLENO")
			return false
		if get_carry_weight() + item.item_mass > max_carry_weight + 0.001:
			_notify_game("CARGA MÁXIMA · SUELTA PESO")
			return false
		if item.pickup(self):
			item.stow(self)
			inventory.append(item)
			if game != null and game.has_method("on_item_collected"):
				game.on_item_collected(self, item)
			elif game != null and game.has_method("on_artifact_picked"):
				game.on_artifact_picked(self)
			return true
		return false
	if carried_item != null:
		return false
	if get_carry_weight() + item.item_mass > max_carry_weight + 0.001:
		_notify_game("CARGA MÁXIMA · SUELTA PESO")
		return false
	if item.pickup(self):
		carried_item = item
		if game != null and game.has_method("on_artifact_picked"):
			game.on_artifact_picked(self)
		return true
	return false

func _notify_game(text: String) -> void:
	if game != null and game.has_method("notify"):
		game.notify(text)

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

func _has_line_of_sight(target: Vector3, ignore_node: Node = null) -> bool:
	var query := PhysicsRayQueryParameters3D.create(camera.global_position, target)
	query.collision_mask = 1
	var exclude: Array[RID] = [get_rid()]
	if ignore_node != null:
		_collect_collision_rids(ignore_node, exclude)
	query.exclude = exclude
	var hit := get_world_3d().direct_space_state.intersect_ray(query)
	return hit.is_empty()

func _collect_collision_rids(node: Node, out: Array[RID]) -> void:
	if node is CollisionObject3D:
		out.append((node as CollisionObject3D).get_rid())
	for child in node.get_children():
		_collect_collision_rids(child, out)

func _drop_carried_or_inventory() -> void:
	if _input_locked():
		return
	if carried_item != null:
		_drop_item()
		return
	_drop_inventory_item()

func _drop_inventory_item() -> void:
	if inventory.is_empty():
		return
	var item: FMCarryItem = inventory.pop_back()
	if item == null or not is_instance_valid(item):
		return
	item.unstow()
	item.drop(-camera.global_transform.basis.z)
	if game != null and game.has_method("on_artifact_dropped"):
		game.on_artifact_dropped()

func _drop_item() -> void:
	if _input_locked():
		return
	if carried_item == null:
		return
	var item := carried_item as FMCarryItem
	carried_item = null
	if item != null:
		item.drop(-camera.global_transform.basis.z)
		if game != null and game.has_method("on_artifact_dropped"):
			game.on_artifact_dropped()

func get_carry_weight() -> float:
	var total := 0.0
	for item in inventory:
		if item != null and is_instance_valid(item):
			total += item.item_mass
	var held := carried_item as FMCarryItem
	if held != null and is_instance_valid(held):
		total += held.item_mass
	return total

func get_stowed_weight() -> float:
	var total := 0.0
	for item in inventory:
		if item != null and is_instance_valid(item):
			total += item.item_mass
	return total

func get_inventory_count() -> int:
	return inventory.size()

func get_carry_summary() -> String:
	return "CARGA  %.1f / %.1f kg  ·  %d / %d" % [
		get_carry_weight(), max_carry_weight, inventory.size(), inventory_capacity
	]

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
	var interactable := _nearest_interactable()
	if interactable != null and interactable.has_method("get_interaction_prompt"):
		return interactable.get_interaction_prompt()
	if carried_item != null:
		var held := carried_item as FMCarryItem
		return "Q   SOLTAR %s" % (held.item_name if held != null else "OBJETO")
	var nearest_item := _nearest_item() as FMCarryItem
	if nearest_item != null:
		if nearest_item.size_class == "SMALL":
			if inventory.size() >= inventory_capacity:
				return "INVENTARIO LLENO"
			return "E   GUARDAR %s" % nearest_item.item_name
		return "E   RECOGER %s" % nearest_item.item_name
	if not inventory.is_empty():
		return "Q   SOLTAR COMPONENTE  ·  %s" % get_carry_summary()
	if _nearest_hiding_spot() != null:
		return "E   ESCONDERSE"
	return _prompt

func _nearest_interactable() -> Node3D:
	var best: Node3D = null
	var best_distance := interact_distance
	for node in get_tree().get_nodes_in_group("fm_interactable"):
		if node == null or not is_instance_valid(node):
			continue
		if not node.has_method("can_interact") or not node.has_method("get_interaction_position"):
			continue
		if not node.can_interact(self):
			continue
		var point: Vector3 = node.get_interaction_position()
		var distance := global_position.distance_to(point)
		if distance <= best_distance and _has_line_of_sight(point, node):
			best = node as Node3D
			best_distance = distance
	return best

func recharge_battery(amount: float) -> void:
	battery = clampf(battery + amount, 0.0, max_battery)
	if battery > 0.0:
		flashlight_on = true

func _nearest_item() -> Node3D:
	var best: FMCarryItem = null
	var best_distance := interact_distance
	for node in get_tree().get_nodes_in_group("fm_carry_item"):
		var item := node as FMCarryItem
		if item == null or item.carried_by != null:
			continue
		var distance := global_position.distance_to(item.global_position)
		if distance <= best_distance and _has_line_of_sight(item.global_position + Vector3(0.0, 0.1, 0.0), item):
			best = item
			best_distance = distance
	return best

func _nearest_hiding_spot() -> Node3D:
	for node in get_tree().get_nodes_in_group("fm_hiding_spot"):
		var spot := node as FMHidingSpot
		if spot != null and spot.can_use(self) and global_position.distance_to(spot.global_position) <= 2.4:
			return spot
	return null
