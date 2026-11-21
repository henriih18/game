class_name FMSectorTransition
extends Node3D

## Enlace de servicio provisional entre Z10 y Recepción.
##
## La exportación V06 del nivel completo todavía no existe y los dos sectores
## están a ~140 m de distancia en coordenadas. Este nodo representa una puerta
## de enlace NEXUS: el jugador interactúa y el orquestador hace la transición.
## No es geometría final ni sustituye al conector real.

@export var destination_label := "RECEPCIÓN"
@export var prompt := "E   ENLACE DE SERVICIO · RECEPCIÓN"

var game: Node = null
var used := false

var _light: OmniLight3D
var _screen: MeshInstance3D
var _label: Label3D
var _blocker: StaticBody3D
var _blocker_shape: CollisionShape3D
var _time := 0.0


func _ready() -> void:
	add_to_group("fm_interactable")
	_build_visual()


func _process(delta: float) -> void:
	_time += delta
	if used:
		return
	if _light != null:
		_light.light_energy = 0.42 + sin(_time * 2.1) * 0.10
	if _screen != null and _screen.material_override is StandardMaterial3D:
		var mat := _screen.material_override as StandardMaterial3D
		mat.emission_energy_multiplier = 0.75 + sin(_time * 3.0) * 0.18


func can_interact(_player: Node) -> bool:
	if used:
		return false
	if game != null and game.get("state") != null:
		return int(game.get("state")) == 0
	return true


func get_interaction_prompt() -> String:
	return prompt


func get_interaction_position() -> Vector3:
	return global_position + Vector3(0.0, 1.15, 0.0)


func interact(player: Node) -> bool:
	if used or player == null:
		return false
	if game == null or not game.has_method("transition_to_reception"):
		return false
	used = true
	_set_used_visual()
	_disable_blocker()
	game.transition_to_reception(player)
	return true


func _build_visual() -> void:
	var dark := StandardMaterial3D.new()
	dark.albedo_color = Color(0.035, 0.042, 0.048, 1.0)
	dark.metallic = 0.82
	dark.roughness = 0.36

	var steel := StandardMaterial3D.new()
	steel.albedo_color = Color(0.075, 0.085, 0.090, 1.0)
	steel.metallic = 0.72
	steel.roughness = 0.48

	var hazard := StandardMaterial3D.new()
	hazard.albedo_color = Color(0.72, 0.52, 0.06, 1.0)
	hazard.metallic = 0.25
	hazard.roughness = 0.58

	var green := StandardMaterial3D.new()
	green.albedo_color = Color(0.04, 0.40, 0.22, 1.0)
	green.emission_enabled = true
	green.emission = Color(0.10, 1.0, 0.50)
	green.emission_energy_multiplier = 0.9
	green.roughness = 0.22

	# Marco de la puerta.
	_add_box(Vector3(-1.22, 1.18, 0.0), Vector3(0.18, 2.36, 0.34), steel)
	_add_box(Vector3(1.22, 1.18, 0.0), Vector3(0.18, 2.36, 0.34), steel)
	_add_box(Vector3(0.0, 2.30, 0.0), Vector3(2.62, 0.18, 0.34), steel)
	_add_box(Vector3(0.0, 0.055, 0.0), Vector3(2.62, 0.09, 0.42), dark)

	# Dos hojas metálicas con junta central y banda de peligro.
	_add_box(Vector3(-0.56, 1.12, 0.10), Vector3(1.02, 2.14, 0.075), dark)
	_add_box(Vector3(0.56, 1.12, 0.10), Vector3(1.02, 2.14, 0.075), dark)
	_add_box(Vector3(0.0, 1.12, 0.145), Vector3(0.035, 2.14, 0.025), steel)
	_add_box(Vector3(0.0, 0.22, 0.155), Vector3(2.02, 0.10, 0.018), hazard)
	for side in [-1.0, 1.0]:
		_add_box(Vector3(0.46 * side, 1.02, 0.155), Vector3(0.035, 0.20, 0.022), steel)

	# Pantalla y lector de estado.
	_screen = _add_box(Vector3(0.82, 1.58, 0.155), Vector3(0.40, 0.24, 0.022), green)
	_add_box(Vector3(0.82, 1.58, 0.145), Vector3(0.45, 0.29, 0.016), steel)

	_light = OmniLight3D.new()
	_light.name = "ServiceLinkLight"
	_light.light_color = Color(0.22, 1.0, 0.55)
	_light.light_energy = 0.45
	_light.omni_range = 3.4
	_light.shadow_enabled = false
	_light.position = Vector3(0.0, 2.05, -0.55)
	add_child(_light)

	_label = Label3D.new()
	_label.name = "ServiceLinkLabel"
	_label.text = "ENLACE DE SERVICIO\n%s" % destination_label
	_label.font_size = 30
	_label.pixel_size = 0.0055
	_label.modulate = Color(0.55, 1.0, 0.70, 1.0)
	_label.outline_size = 7
	_label.outline_modulate = Color(0.005, 0.02, 0.01, 0.95)
	_label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	_label.position = Vector3(0.0, 2.62, -0.10)
	add_child(_label)

	# Bloquea el paso mientras el enlace no se ha utilizado.
	_add_blocker()


func _add_blocker() -> void:
	_blocker = StaticBody3D.new()
	_blocker.name = "ServiceLinkBlocker"
	_blocker.collision_layer = 1
	_blocker.collision_mask = 0
	_blocker.position = Vector3(0.0, 1.10, 0.055)

	_blocker_shape = CollisionShape3D.new()
	_blocker_shape.name = "ServiceLinkBlockerShape"
	var shape := BoxShape3D.new()
	shape.size = Vector3(2.40, 2.20, 0.22)
	_blocker_shape.shape = shape
	_blocker.add_child(_blocker_shape)
	add_child(_blocker)


func _set_used_visual() -> void:
	if _screen != null and _screen.material_override is StandardMaterial3D:
		var mat := _screen.material_override as StandardMaterial3D
		mat.albedo_color = Color(0.45, 0.18, 0.03, 1.0)
		mat.emission = Color(1.0, 0.45, 0.08)
		mat.emission_energy_multiplier = 0.85
	if _light != null:
		_light.light_color = Color(1.0, 0.48, 0.10)
		_light.light_energy = 0.35
	if _label != null:
		_label.text = "ENLACE ABIERTO\n%s" % destination_label
		_label.modulate = Color(1.0, 0.72, 0.35, 1.0)


func _disable_blocker() -> void:
	if _blocker_shape != null:
		_blocker_shape.set_deferred("disabled", true)


func is_blocking() -> bool:
	return _blocker_shape != null and not _blocker_shape.disabled


func _add_box(local_position: Vector3, size: Vector3, material: Material) -> MeshInstance3D:
	var box := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = size
	box.mesh = mesh
	box.material_override = material
	box.position = local_position
	box.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	add_child(box)
	return box
