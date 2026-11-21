extends Node3D

## Panel de distracción local del Nivel 1.
## Genera ruido en una posición remota para atraer al Vigilante.

var game
var alarm_id := ""
var noise_position := Vector3.ZERO
var cooldown := 0.0
var _flash: OmniLight3D
var _button: MeshInstance3D
var _label: Label3D

func setup(id: String, trigger_position: Vector3, remote_noise: Vector3, game_ref) -> void:
	alarm_id = id
	noise_position = remote_noise
	game = game_ref
	name = "Alarm_%s" % id
	add_to_group("fm_interactable")
	position = trigger_position
	_build()

func _build() -> void:
	var red := StandardMaterial3D.new()
	red.albedo_color = Color(0.22, 0.035, 0.025, 1.0)
	red.metallic = 0.35
	red.roughness = 0.46
	var dark := StandardMaterial3D.new()
	dark.albedo_color = Color(0.035, 0.04, 0.042, 1.0)
	dark.metallic = 0.75
	dark.roughness = 0.32
	var amber := StandardMaterial3D.new()
	amber.albedo_color = Color(0.95, 0.40, 0.06, 1.0)
	amber.emission_enabled = true
	amber.emission = Color(1.0, 0.35, 0.04)
	amber.emission_energy_multiplier = 1.8
	amber.roughness = 0.35

	var body := MeshInstance3D.new()
	var body_mesh := BoxMesh.new()
	body_mesh.size = Vector3(0.34, 0.52, 0.075)
	body.mesh = body_mesh
	body.material_override = dark
	add_child(body)

	var face := MeshInstance3D.new()
	var face_mesh := BoxMesh.new()
	face_mesh.size = Vector3(0.26, 0.36, 0.016)
	face.mesh = face_mesh
	face.position.z = 0.045
	face.material_override = red
	add_child(face)

	_button = MeshInstance3D.new()
	var button_mesh := CylinderMesh.new()
	button_mesh.top_radius = 0.052
	button_mesh.bottom_radius = 0.052
	button_mesh.height = 0.045
	button_mesh.radial_segments = 16
	_button.mesh = button_mesh
	_button.rotation_degrees.x = 90.0
	_button.position = Vector3(0.0, 0.02, 0.060)
	_button.material_override = amber
	add_child(_button)

	_label = Label3D.new()
	_label.text = "DISTRACCIÓN\nALARMA REMOTA"
	_label.font_size = 26
	_label.pixel_size = 0.0022
	_label.modulate = Color(1.0, 0.66, 0.28, 1.0)
	_label.outline_size = 4
	_label.outline_modulate = Color(0.0, 0.0, 0.0, 1.0)
	_label.position = Vector3(0.0, 0.22, 0.046)
	add_child(_label)

	_flash = OmniLight3D.new()
	_flash.name = "EmergencyAlarmFlash"
	_flash.position = noise_position
	_flash.light_color = Color(1.0, 0.18, 0.04)
	_flash.light_energy = 0.0
	_flash.omni_range = 8.0
	_flash.shadow_enabled = false
	add_child(_flash)
	_flash.global_position = noise_position

func can_interact(player) -> bool:
	return cooldown <= 0.0 and player != null and global_position.distance_to(player.global_position) <= 2.6

func get_interaction_prompt() -> String:
	return "E ACTIVAR ALARMA REMOTA" if cooldown <= 0.0 else "ALARMA RECARGANDO"

func get_interaction_position() -> Vector3:
	return global_position + Vector3(0.0, 0.15, 0.25)

func interact(_player) -> void:
	if cooldown > 0.0:
		return
	cooldown = 15.0
	if game != null and game.has_method("emit_noise"):
		game.emit_noise(noise_position, 20.0, "alarm")
	Audio.play_sfx("alarm", -7.0, 0.86)
	_flash.light_energy = 2.4
	_button.position.z = 0.035
	var tween := create_tween()
	tween.tween_property(_flash, "light_energy", 0.0, 2.4).set_trans(Tween.TRANS_SINE)
	tween.parallel().tween_property(_button, "position:z", 0.060, 0.35).set_delay(0.12)
	_update_label()

func _process(delta: float) -> void:
	if cooldown <= 0.0:
		return
	cooldown = maxf(0.0, cooldown - delta)
	_update_label()

func _update_label() -> void:
	if _label == null:
		return
	_label.text = "DISTRACCIÓN\nALARMA REMOTA" if cooldown <= 0.0 else "RECARGA %ds" % int(ceil(cooldown))
