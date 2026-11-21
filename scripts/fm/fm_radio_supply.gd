class_name FMRadioSupply
extends Node3D

## Suministro de radio: pilas recogibles y cargadores de pared/suelo.
## No es un arma ni un objeto narrativo: es un recurso funcional de
## supervivencia que rellena la batería de FMRadio.
##
## Los nodos se registran en el grupo `fm_interactable` para reutilizar el
## sistema de interacción del jugador (E) sin tocar su lógica.

enum Kind { BATTERY, HIGH_CAPACITY, STATION }

@export var kind: Kind = Kind.BATTERY
@export var charge_amount := 30.0
@export var cooldown_seconds := 20.0
@export var display_name := "PILA DE RADIO"

var game: Node = null
var taken := false
var cooldown := 0.0

var _visual: Node3D
var _led: MeshInstance3D
var _led_mat: StandardMaterial3D
var _time := 0.0


func _ready() -> void:
	add_to_group("fm_interactable")
	add_to_group("fm_radio_supply")
	_build()


func _build() -> void:
	_visual = Node3D.new()
	_visual.name = "Visual"
	add_child(_visual)

	var body_mat := _plastic(Color(0.045, 0.050, 0.048))
	var band_color := Color(0.72, 0.52, 0.10)
	if kind == Kind.HIGH_CAPACITY:
		band_color = Color(0.82, 0.32, 0.08)
	elif kind == Kind.STATION:
		band_color = Color(0.16, 0.52, 0.32)
	var band_mat := _plastic(band_color)
	var metal_mat := _metal(Color(0.42, 0.40, 0.34))
	_led_mat = StandardMaterial3D.new()
	_led_mat.albedo_color = Color(0.10, 0.60, 0.28)
	_led_mat.emission_enabled = true
	_led_mat.emission = Color(0.18, 1.0, 0.44)
	_led_mat.emission_energy_multiplier = 1.4
	_led_mat.roughness = 0.3

	if kind == Kind.STATION:
		_build_station(body_mat, band_mat, metal_mat)
	else:
		_build_battery(body_mat, band_mat, metal_mat)
	_build_label()


func _build_battery(body_mat: StandardMaterial3D, band_mat: StandardMaterial3D,
		metal_mat: StandardMaterial3D) -> void:
	var body := MeshInstance3D.new()
	body.name = "Body"
	var body_mesh := BoxMesh.new()
	body_mesh.size = Vector3(0.13, 0.17, 0.065)
	body.mesh = body_mesh
	body.material_override = body_mat
	body.position.y = 0.09
	_visual.add_child(body)

	var band := MeshInstance3D.new()
	band.name = "Band"
	var band_mesh := BoxMesh.new()
	band_mesh.size = Vector3(0.135, 0.045, 0.070)
	band.mesh = band_mesh
	band.material_override = band_mat
	band.position.y = 0.105
	_visual.add_child(band)

	for x in [-0.035, 0.035]:
		var terminal := MeshInstance3D.new()
		terminal.name = "Terminal"
		var term_mesh := CylinderMesh.new()
		term_mesh.top_radius = 0.018
		term_mesh.bottom_radius = 0.018
		term_mesh.height = 0.024
		term_mesh.radial_segments = 12
		terminal.mesh = term_mesh
		terminal.material_override = metal_mat
		terminal.position = Vector3(x, 0.190, 0.0)
		_visual.add_child(terminal)

	_led = MeshInstance3D.new()
	_led.name = "LED"
	var led_mesh := BoxMesh.new()
	led_mesh.size = Vector3(0.018, 0.008, 0.018)
	_led.mesh = led_mesh
	_led.material_override = _led_mat
	_led.position = Vector3(0.0, 0.135, -0.038)
	_visual.add_child(_led)


func _build_station(body_mat: StandardMaterial3D, band_mat: StandardMaterial3D,
		metal_mat: StandardMaterial3D) -> void:
	var plinth := MeshInstance3D.new()
	plinth.name = "Plinth"
	var plinth_mesh := BoxMesh.new()
	plinth_mesh.size = Vector3(0.34, 0.06, 0.22)
	plinth.mesh = plinth_mesh
	plinth.material_override = body_mat
	plinth.position.y = 0.03
	_visual.add_child(plinth)

	var body := MeshInstance3D.new()
	body.name = "Body"
	var body_mesh := BoxMesh.new()
	body_mesh.size = Vector3(0.28, 0.34, 0.16)
	body.mesh = body_mesh
	body.material_override = body_mat
	body.position.y = 0.23
	_visual.add_child(body)

	var face := MeshInstance3D.new()
	face.name = "Face"
	var face_mesh := BoxMesh.new()
	face_mesh.size = Vector3(0.23, 0.10, 0.012)
	face.mesh = face_mesh
	face.material_override = band_mat
	face.position = Vector3(0.0, 0.34, -0.085)
	_visual.add_child(face)

	for x in [-0.060, 0.0, 0.060]:
		var slot := MeshInstance3D.new()
		slot.name = "Slot"
		var slot_mesh := BoxMesh.new()
		slot_mesh.size = Vector3(0.045, 0.035, 0.018)
		slot.mesh = slot_mesh
		slot.material_override = metal_mat
		slot.position = Vector3(x, 0.20, -0.088)
		_visual.add_child(slot)

	_led = MeshInstance3D.new()
	_led.name = "LED"
	var led_mesh := BoxMesh.new()
	led_mesh.size = Vector3(0.022, 0.022, 0.010)
	_led.mesh = led_mesh
	_led.material_override = _led_mat
	_led.position = Vector3(0.100, 0.39, -0.084)
	_visual.add_child(_led)

	var cable := MeshInstance3D.new()
	cable.name = "Cable"
	var cable_mesh := CylinderMesh.new()
	cable_mesh.top_radius = 0.010
	cable_mesh.bottom_radius = 0.010
	cable_mesh.height = 0.34
	cable_mesh.radial_segments = 8
	cable.mesh = cable_mesh
	cable.material_override = metal_mat
	cable.position = Vector3(-0.19, 0.20, 0.0)
	_visual.add_child(cable)


func _build_label() -> void:
	var label := Label3D.new()
	label.name = "Label"
	label.text = display_name if kind != Kind.STATION else "CARGADOR DE RADIO"
	label.font_size = 16
	label.pixel_size = 0.0045
	label.modulate = Color(0.64, 0.90, 0.70)
	label.outline_size = 5
	label.outline_modulate = Color(0.01, 0.02, 0.012, 0.92)
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.position.y = 0.50 if kind == Kind.STATION else 0.30
	_visual.add_child(label)


func _process(delta: float) -> void:
	_time += delta
	if cooldown > 0.0:
		cooldown = maxf(0.0, cooldown - delta)
	if _led != null:
		var pulse := 0.7 + 0.3 * sin(_time * 3.2)
		if kind == Kind.STATION and cooldown > 0.0:
			pulse = 0.25
		_led_mat.emission_energy_multiplier = pulse


func can_interact(_player: Node) -> bool:
	if taken:
		return false
	if kind == Kind.STATION:
		return cooldown <= 0.0
	return true


func get_interaction_prompt() -> String:
	if kind == Kind.STATION and cooldown > 0.0:
		return "CARGADOR EN ESPERA   %.0fs" % ceilf(cooldown)
	if kind == Kind.STATION:
		return "E   CARGAR RADIO   +%d%%" % int(charge_amount)
	if kind == Kind.HIGH_CAPACITY:
		return "E   RECOGER PILA DE ALTA CAPACIDAD   +%d%%" % int(charge_amount)
	return "E   RECOGER PILA DE RADIO   +%d%%" % int(charge_amount)


func get_interaction_position() -> Vector3:
	return global_position + Vector3(0.0, 0.2, 0.0)


func interact(player: Node) -> bool:
	if taken:
		return false
	if kind == Kind.STATION and cooldown > 0.0:
		return false
	var radio := _find_radio(player)
	if radio == null:
		return false
	radio.add_battery(charge_amount)
	if kind == Kind.STATION:
		cooldown = cooldown_seconds
		Audio.play_sfx("tick", -12.0, 0.92)
	else:
		taken = true
		Audio.play_sfx("click", -10.0, 1.25)
		_visual.visible = false
		set_process(false)
		if game != null and game.has_method("notify"):
			game.notify("RADIO  ·  BATERÍA +%d%%" % int(charge_amount))
		queue_free()
	if game != null and game.has_method("notify") and kind == Kind.STATION:
		game.notify("CARGADOR DE RADIO  ·  +%d%%" % int(charge_amount))
	return true


func _find_radio(player: Node) -> FMRadio:
	if player != null and is_instance_valid(player):
		var direct := player.get_node_or_null("Radio") as FMRadio
		if direct != null:
			return direct
	for node in get_tree().get_nodes_in_group("fm_radio"):
		var candidate := node as FMRadio
		if candidate != null:
			return candidate
	return null


func _plastic(color: Color) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color
	mat.roughness = 0.82
	mat.metallic = 0.0
	return mat


func _metal(color: Color) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color
	mat.roughness = 0.42
	mat.metallic = 0.85
	return mat
