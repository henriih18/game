class_name FMRemotePlayer
extends Node3D

## Representación de un compañero controlado por otra instancia.
## No simula física ni input: recibe posición/estado del host y los interpola.
## El jugador local sigue siendo un FMPlayer en primera persona.

var net_id := 0
var target_position := Vector3.ZERO
var target_yaw := 0.0
var hidden := false
var observing_watcher := false
var carrying := false
var battery := 100.0

var _visual: Node3D
var _carry_anchor: Node3D
var _name_label: Label3D
var _time := 0.0
var _suit_mat: StandardMaterial3D
var _visor_mat: StandardMaterial3D
var _carry_light: OmniLight3D

func _ready() -> void:
	_build_visual()
	_build_carry_anchor()

func setup(id: int, spawn_position: Vector3, yaw := 0.0) -> void:
	net_id = id
	target_position = spawn_position
	target_yaw = yaw
	global_position = spawn_position
	rotation.y = yaw
	_apply_color()
	if _name_label != null:
		_name_label.text = "TRABAJADOR"

func recharge_battery(amount: float) -> void:
	battery = clampf(battery + amount, 0.0, 100.0)

func set_network_state(pos: Vector3, yaw: float, is_hidden: bool, is_observing: bool) -> void:
	target_position = pos
	target_yaw = yaw
	hidden = is_hidden
	observing_watcher = is_observing
	visible = not hidden
	if hidden:
		global_position = pos
		rotation.y = yaw

func get_network_position() -> Vector3:
	return target_position

func set_carrying(value: bool) -> void:
	carrying = value
	if _carry_light != null:
		_carry_light.visible = value

func get_carry_anchor() -> Node3D:
	return _carry_anchor

func _process(delta: float) -> void:
	if hidden:
		return
	_time += delta
	global_position = global_position.lerp(target_position, clampf(delta * 14.0, 0.0, 1.0))
	rotation.y = lerp_angle(rotation.y, target_yaw, clampf(delta * 12.0, 0.0, 1.0))
	if _visual != null:
		var speed := global_position.distance_to(target_position)
		_visual.position.y = sin(_time * 9.0) * 0.025 if speed > 0.08 else lerpf(_visual.position.y, 0.0, clampf(delta * 6.0, 0.0, 1.0))

func _build_visual() -> void:
	_visual = Node3D.new()
	_visual.name = "Visual"
	add_child(_visual)

	_suit_mat = StandardMaterial3D.new()
	_suit_mat.albedo_color = Color(0.10, 0.135, 0.15, 1.0)
	_suit_mat.roughness = 0.82
	_suit_mat.metallic = 0.08

	var dark := StandardMaterial3D.new()
	dark.albedo_color = Color(0.045, 0.055, 0.065, 1.0)
	dark.roughness = 0.55
	dark.metallic = 0.35

	var skin := StandardMaterial3D.new()
	skin.albedo_color = Color(0.42, 0.3, 0.24, 1.0)
	skin.roughness = 0.9

	var hi_vis := StandardMaterial3D.new()
	hi_vis.albedo_color = Color(0.62, 0.28, 0.045, 1.0)
	hi_vis.roughness = 0.78
	hi_vis.emission_enabled = false

	_visor_mat = StandardMaterial3D.new()
	_visor_mat.albedo_color = Color(0.03, 0.09, 0.11, 1.0)
	_visor_mat.roughness = 0.22
	_visor_mat.metallic = 0.55
	_visor_mat.emission_enabled = true
	_visor_mat.emission = Color(0.12, 0.62, 0.72)
	_visor_mat.emission_energy_multiplier = 0.45

	var torso := MeshInstance3D.new()
	var torso_mesh := CapsuleMesh.new()
	torso_mesh.radius = 0.32
	torso_mesh.height = 1.16
	torso_mesh.radial_segments = 12
	torso_mesh.rings = 6
	torso.mesh = torso_mesh
	torso.material_override = _suit_mat
	torso.position.y = 1.02
	_visual.add_child(torso)

	# Chaleco de seguridad y correas: lectura industrial a distancia.
	var vest := MeshInstance3D.new()
	var vest_mesh := BoxMesh.new()
	vest_mesh.size = Vector3(0.34, 0.27, 0.055)
	vest.mesh = vest_mesh
	vest.material_override = hi_vis
	vest.position = Vector3(0.0, 1.16, -0.315)
	_visual.add_child(vest)

	for side in [-1.0, 1.0]:
		var stripe := MeshInstance3D.new()
		var stripe_mesh := BoxMesh.new()
		stripe_mesh.size = Vector3(0.045, 0.31, 0.025)
		stripe.mesh = stripe_mesh
		stripe.material_override = hi_vis
		stripe.position = Vector3(0.12 * side, 1.17, -0.347)
		_visual.add_child(stripe)

	var vest_back := MeshInstance3D.new()
	var vest_back_mesh := BoxMesh.new()
	vest_back_mesh.size = Vector3(0.44, 0.28, 0.10)
	vest_back.mesh = vest_back_mesh
	vest_back.material_override = hi_vis
	vest_back.position = Vector3(0.0, 1.16, 0.29)
	_visual.add_child(vest_back)

	var belt := MeshInstance3D.new()
	var belt_mesh := BoxMesh.new()
	belt_mesh.size = Vector3(0.44, 0.075, 0.36)
	belt.mesh = belt_mesh
	belt.material_override = dark
	belt.position.y = 0.73
	_visual.add_child(belt)

	var head := MeshInstance3D.new()
	var head_mesh := SphereMesh.new()
	head_mesh.radius = 0.225
	head_mesh.height = 0.45
	head_mesh.radial_segments = 16
	head_mesh.rings = 8
	head.mesh = head_mesh
	head.material_override = skin
	head.position.y = 1.71
	_visual.add_child(head)

	var helmet := MeshInstance3D.new()
	var helmet_mesh := SphereMesh.new()
	helmet_mesh.radius = 0.295
	helmet_mesh.height = 0.48
	helmet_mesh.radial_segments = 18
	helmet_mesh.rings = 10
	helmet.mesh = helmet_mesh
	helmet.material_override = dark
	helmet.position = Vector3(0.0, 1.81, 0.025)
	helmet.scale = Vector3(1.0, 0.82, 1.0)
	_visual.add_child(helmet)

	var brim := MeshInstance3D.new()
	var brim_mesh := BoxMesh.new()
	brim_mesh.size = Vector3(0.40, 0.045, 0.12)
	brim.mesh = brim_mesh
	brim.material_override = dark
	brim.position = Vector3(0.0, 1.80, -0.25)
	_visual.add_child(brim)

	var visor := MeshInstance3D.new()
	var visor_mesh := BoxMesh.new()
	visor_mesh.size = Vector3(0.31, 0.105, 0.045)
	visor.mesh = visor_mesh
	visor.material_override = _visor_mat
	visor.position = Vector3(0.0, 1.755, -0.255)
	_visual.add_child(visor)

	var mask := MeshInstance3D.new()
	var mask_mesh := BoxMesh.new()
	mask_mesh.size = Vector3(0.20, 0.105, 0.07)
	mask.mesh = mask_mesh
	mask.material_override = dark
	mask.position = Vector3(0.0, 1.60, -0.245)
	_visual.add_child(mask)

	var cup := MeshInstance3D.new()
	var cup_mesh := CylinderMesh.new()
	cup_mesh.top_radius = 0.035
	cup_mesh.bottom_radius = 0.045
	cup_mesh.height = 0.05
	cup_mesh.radial_segments = 10
	cup.mesh = cup_mesh
	cup.material_override = dark
	cup.rotation_degrees.x = 90.0
	cup.position = Vector3(0.0, 1.60, -0.285)
	_visual.add_child(cup)

	var backpack := MeshInstance3D.new()
	var backpack_mesh := BoxMesh.new()
	backpack_mesh.size = Vector3(0.40, 0.52, 0.20)
	backpack.mesh = backpack_mesh
	backpack.material_override = dark
	backpack.position = Vector3(0.0, 1.10, 0.31)
	_visual.add_child(backpack)

	var tank := MeshInstance3D.new()
	var tank_mesh := CylinderMesh.new()
	tank_mesh.top_radius = 0.075
	tank_mesh.bottom_radius = 0.075
	tank_mesh.height = 0.46
	tank_mesh.radial_segments = 10
	tank.mesh = tank_mesh
	tank.material_override = hi_vis
	tank.position = Vector3(0.0, 1.14, 0.43)
	_visual.add_child(tank)

	var lamp := MeshInstance3D.new()
	var lamp_mesh := CylinderMesh.new()
	lamp_mesh.top_radius = 0.055
	lamp_mesh.bottom_radius = 0.055
	lamp_mesh.height = 0.12
	lamp_mesh.radial_segments = 10
	lamp.mesh = lamp_mesh
	lamp.material_override = _visor_mat
	lamp.rotation_degrees.x = 90.0
	lamp.position = Vector3(0.0, 1.93, -0.23)
	_visual.add_child(lamp)

	for side in [-1.0, 1.0]:
		var shoulder := MeshInstance3D.new()
		var shoulder_mesh := SphereMesh.new()
		shoulder_mesh.radius = 0.15
		shoulder_mesh.height = 0.22
		shoulder_mesh.radial_segments = 10
		shoulder_mesh.rings = 6
		shoulder.mesh = shoulder_mesh
		shoulder.material_override = dark
		shoulder.position = Vector3(0.34 * side, 1.34, 0.0)
		_visual.add_child(shoulder)

		var arm := MeshInstance3D.new()
		var arm_mesh := CapsuleMesh.new()
		arm_mesh.radius = 0.105
		arm_mesh.height = 0.72
		arm_mesh.radial_segments = 8
		arm_mesh.rings = 4
		arm.mesh = arm_mesh
		arm.material_override = _suit_mat
		arm.position = Vector3(0.40 * side, 1.02, 0.0)
		arm.rotation_degrees.z = side * 6.0
		_visual.add_child(arm)

		var leg := MeshInstance3D.new()
		var leg_mesh := CapsuleMesh.new()
		leg_mesh.radius = 0.12
		leg_mesh.height = 0.64
		leg_mesh.radial_segments = 8
		leg_mesh.rings = 4
		leg.mesh = leg_mesh
		leg.material_override = dark
		leg.position = Vector3(0.16 * side, 0.35, 0.0)
		_visual.add_child(leg)

	var shadow := MeshInstance3D.new()
	var shadow_mesh := CylinderMesh.new()
	shadow_mesh.top_radius = 0.42
	shadow_mesh.bottom_radius = 0.42
	shadow_mesh.height = 0.01
	shadow_mesh.radial_segments = 20
	shadow.mesh = shadow_mesh
	var shadow_mat := StandardMaterial3D.new()
	shadow_mat.albedo_color = Color(0.0, 0.0, 0.0, 0.42)
	shadow_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	shadow_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	shadow.material_override = shadow_mat
	shadow.position.y = 0.015
	_visual.add_child(shadow)

	_name_label = Label3D.new()
	_name_label.text = "TRABAJADOR"
	_name_label.font_size = 12
	_name_label.pixel_size = 0.0032
	_name_label.modulate = Color(0.74, 0.9, 0.82)
	_name_label.outline_size = 5
	_name_label.outline_modulate = Color(0.01, 0.02, 0.012, 0.9)
	_name_label.position.y = 2.12
	_name_label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	add_child(_name_label)

func _build_carry_anchor() -> void:
	_carry_anchor = Node3D.new()
	_carry_anchor.name = "CarryAnchor"
	_carry_anchor.position = Vector3(0.0, 1.12, -0.52)
	add_child(_carry_anchor)

	_carry_light = OmniLight3D.new()
	_carry_light.light_color = Color(0.16, 1.0, 0.45)
	_carry_light.light_energy = 0.5
	_carry_light.omni_range = 2.0
	_carry_light.shadow_enabled = false
	_carry_light.visible = false
	_carry_anchor.add_child(_carry_light)

func _apply_color() -> void:
	if _suit_mat == null:
		return
	var palette := [
		Color(0.085, 0.115, 0.13, 1.0),
		Color(0.09, 0.12, 0.16, 1.0),
		Color(0.12, 0.105, 0.09, 1.0),
		Color(0.105, 0.095, 0.125, 1.0),
	]
	_suit_mat.albedo_color = palette[(net_id - 1) % palette.size()]
