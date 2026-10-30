class_name FMCarryItem
extends RigidBody3D

## Objeto físico recuperable del vertical slice.
## Mientras se transporta queda congelado y sigue un ancla del jugador.
## Al soltarlo vuelve a la simulación y puede hacer ruido.

@export var item_name := "NÚCLEO DE CONTENCIÓN"
@export var item_mass := 7.0
@export var follow_speed := 16.0

var carried_by: Node3D = null
var home_position := Vector3.ZERO
var game: Node = null
var _visual: Node3D
var _hum_light: OmniLight3D
var _time := 0.0

func _ready() -> void:
	mass = item_mass
	gravity_scale = 1.0
	freeze = true
	freeze_mode = RigidBody3D.FREEZE_MODE_KINEMATIC
	collision_layer = 4
	collision_mask = 1
	continuous_cd = true
	add_to_group("fm_carry_item")
	home_position = global_position
	_build_visual()

func _build_visual() -> void:
	_visual = Node3D.new()
	_visual.name = "Visual"
	add_child(_visual)

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
		return
	if global_position.y < -4.0:
		_reset_home()

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
		game.emit_noise(global_position, 4.0, "pickup")
	Audio.play_sfx("grab", -7.0)
	return true

func drop(impulse_direction := Vector3.ZERO) -> void:
	if carried_by == null:
		return
	carried_by = null
	freeze = false
	collision_layer = 4
	collision_mask = 1
	apply_central_impulse(impulse_direction.normalized() * 1.8 + Vector3(0.0, 0.55, 0.0))
	if game != null:
		game.emit_noise(global_position, 10.0, "item_drop")
	Audio.play_sfx("drop", -5.0)

func _reset_home() -> void:
	freeze = true
	global_position = home_position
	linear_velocity = Vector3.ZERO
	angular_velocity = Vector3.ZERO
