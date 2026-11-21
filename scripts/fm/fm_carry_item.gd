class_name FMCarryItem
extends RigidBody3D

## Objeto físico recuperable del vertical slice.
## Mientras se transporta queda congelado y sigue un ancla del jugador.
## Al soltarlo vuelve a la simulación y puede hacer ruido.

@export var item_name := "NÚCLEO DE CONTENCIÓN"
@export var item_mass := 7.0
@export var follow_speed := 16.0
@export var fall_limit_y := -4.0
@export_enum("SMALL", "MEDIUM", "LARGE") var size_class := "MEDIUM"
@export var is_mission_item := false
@export var item_kind := "core"
@export_enum("CORE", "COMPONENT") var visual_style := "CORE"
@export var display_color := Color(0.04, 0.55, 0.24, 1.0)
@export var pickup_noise_radius := 4.0
@export var drop_noise_radius := 10.0
@export var inventory_noise_radius := 1.0

var carried_by: Node3D = null
var home_position := Vector3.ZERO
var game: Node = null
var network_replica := false
var stowed := false
var inventory_noise_scale := 1.0
var _visual: Node3D
var _hum_light: OmniLight3D
var _time := 0.0
var _rattle_timer := 0.0
var _last_rattle_position := Vector3.ZERO

func _ready() -> void:
	mass = item_mass
	gravity_scale = 1.0
	linear_damp = 0.35
	angular_damp = 0.60
	var pm := PhysicsMaterial.new()
	pm.friction = 0.86
	pm.bounce = 0.04
	pm.rough = true
	physics_material_override = pm
	freeze = true
	freeze_mode = RigidBody3D.FREEZE_MODE_KINEMATIC
	collision_layer = 4
	collision_mask = 1
	continuous_cd = true
	add_to_group("fm_carry_item")
	home_position = global_position
	_fit_collision_shape()
	_build_visual()

func _fit_collision_shape() -> void:
	if size_class != "SMALL":
		return
	var collider := get_node_or_null("CollisionShape3D") as CollisionShape3D
	if collider == null:
		return
	var box := BoxShape3D.new()
	box.size = Vector3(0.22, 0.22, 0.22)
	collider.shape = box

func _build_visual() -> void:
	_visual = Node3D.new()
	_visual.name = "Visual"
	add_child(_visual)
	if visual_style == "COMPONENT":
		_build_component_visual()
		return

	var green := StandardMaterial3D.new()
	green.albedo_color = Color(0.04, 0.55, 0.24, 1.0)
	green.roughness = 0.32
	green.metallic = 0.35
	green.emission_enabled = true
	green.emission = Color(0.08, 0.85, 0.35)
	green.emission_energy_multiplier = 1.4

	var dark := StandardMaterial3D.new()
	dark.albedo_color = Color(0.07, 0.09, 0.12, 1.0)
	dark.roughness = 0.5
	dark.metallic = 0.7

	var core := MeshInstance3D.new()
	var core_mesh := CylinderMesh.new()
	core_mesh.top_radius = 0.2
	core_mesh.bottom_radius = 0.2
	core_mesh.height = 0.52
	core_mesh.radial_segments = 16
	core.mesh = core_mesh
	core.material_override = green
	_visual.add_child(core)

	for y in [-0.2, 0.2]:
		var ring := MeshInstance3D.new()
		var torus := TorusMesh.new()
		torus.inner_radius = 0.23
		torus.outer_radius = 0.29
		torus.rings = 20
		torus.ring_segments = 8
		ring.mesh = torus
		ring.material_override = dark
		ring.position.y = y
		_visual.add_child(ring)

	for side in [-1.0, 1.0]:
		var prong := MeshInstance3D.new()
		var prong_mesh := BoxMesh.new()
		prong_mesh.size = Vector3(0.06, 0.35, 0.06)
		prong.mesh = prong_mesh
		prong.material_override = dark
		prong.position = Vector3(0.24 * side, 0.02, 0.0)
		prong.rotation_degrees.z = 12.0 * side
		_visual.add_child(prong)

	_hum_light = OmniLight3D.new()
	_hum_light.name = "HumLight"
	_hum_light.light_color = Color(0.16, 1.0, 0.45)
	_hum_light.light_energy = 0.55
	_hum_light.omni_range = 2.4
	_hum_light.shadow_enabled = false
	add_child(_hum_light)

func _build_component_visual() -> void:
	var body_mat := StandardMaterial3D.new()
	body_mat.albedo_color = display_color
	body_mat.metallic = 0.42
	body_mat.roughness = 0.46

	var cap_mat := StandardMaterial3D.new()
	cap_mat.albedo_color = Color(0.045, 0.05, 0.055, 1.0)
	cap_mat.metallic = 0.72
	cap_mat.roughness = 0.38

	var body := MeshInstance3D.new()
	var body_mesh := BoxMesh.new()
	body_mesh.size = Vector3(0.16, 0.16, 0.16)
	body.mesh = body_mesh
	body.material_override = body_mat
	_visual.add_child(body)

	var cap := MeshInstance3D.new()
	var cap_mesh := BoxMesh.new()
	cap_mesh.size = Vector3(0.10, 0.04, 0.10)
	cap.mesh = cap_mesh
	cap.material_override = cap_mat
	cap.position.y = 0.10
	_visual.add_child(cap)

func _process(delta: float) -> void:
	_time += delta
	if _visual != null:
		_visual.rotation.y += delta * 0.45
	if _hum_light != null:
		_hum_light.light_energy = 0.42 + sin(_time * 2.8) * 0.12

func _physics_process(delta: float) -> void:
	if carried_by != null and is_instance_valid(carried_by):
		var anchor: Node3D = carried_by.get_carry_anchor()
		if anchor != null:
			global_position = global_position.lerp(anchor.global_position, clampf(delta * follow_speed, 0.0, 1.0))
			global_rotation = global_rotation.lerp(anchor.global_rotation, clampf(delta * 10.0, 0.0, 1.0))
		if stowed:
			_update_inventory_rattle(delta)
		return
	if global_position.y < fall_limit_y:
		_reset_home()

func _update_inventory_rattle(delta: float) -> void:
	if game == null or not game.has_method("emit_noise"):
		return
	_rattle_timer += delta
	if _rattle_timer < 1.2:
		return
	var moved := global_position.distance_to(_last_rattle_position)
	_last_rattle_position = global_position
	_rattle_timer = 0.0
	if moved < 0.04 or inventory_noise_scale <= 0.0:
		return
	game.emit_noise(global_position, inventory_noise_radius * inventory_noise_scale, "inventory_rattle")

func pickup(player: Node3D) -> bool:
	if carried_by != null or player == null:
		return false
	carried_by = player
	freeze = true
	freeze_mode = RigidBody3D.FREEZE_MODE_KINEMATIC
	collision_layer = 0
	collision_mask = 0
	linear_velocity = Vector3.ZERO
	angular_velocity = Vector3.ZERO
	if game != null:
		game.emit_noise(global_position, pickup_noise_radius, "pickup")
	Audio.play_sfx("grab", -7.0)
	return true

func drop(impulse_direction := Vector3.ZERO) -> void:
	if carried_by == null:
		return
	carried_by = null
	stowed = false
	freeze = false
	collision_layer = 4
	collision_mask = 1
	_set_visual_visible(true)
	apply_central_impulse(impulse_direction.normalized() * 1.8 + Vector3(0.0, 0.55, 0.0))
	if game != null:
		game.emit_noise(global_position, drop_noise_radius, "item_drop")
	Audio.play_sfx("drop", -5.0)

func stow(player: Node3D) -> void:
	if player == null:
		return
	carried_by = player
	stowed = true
	freeze = true
	freeze_mode = RigidBody3D.FREEZE_MODE_KINEMATIC
	collision_layer = 0
	collision_mask = 0
	linear_velocity = Vector3.ZERO
	angular_velocity = Vector3.ZERO
	_last_rattle_position = global_position
	_set_visual_visible(false)

func unstow() -> void:
	stowed = false
	_set_visual_visible(true)
	if carried_by == null:
		freeze = false
		collision_layer = 4
		collision_mask = 1

func _set_visual_visible(value: bool) -> void:
	if _visual != null:
		_visual.visible = value
	if _hum_light != null:
		_hum_light.visible = value

func _reset_home() -> void:
	freeze = true
	global_position = home_position
	linear_velocity = Vector3.ZERO
	angular_velocity = Vector3.ZERO

## Replica no autoritativa: el host manda quién lo lleva y su posición.
## No simula física para evitar que las dos instancias diverjan.
func network_set_carrier(carrier: Node3D, position: Vector3) -> void:
	network_replica = true
	carried_by = carrier
	linear_velocity = Vector3.ZERO
	angular_velocity = Vector3.ZERO
	freeze = true
	if carrier != null:
		collision_layer = 0
		collision_mask = 0
	else:
		collision_layer = 4
		collision_mask = 1
		global_position = position
