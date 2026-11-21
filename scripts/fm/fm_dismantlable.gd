class_name FMDismantlable
extends StaticBody3D

## Puesto de análisis desmontable del vertical slice.
##
## Es un interactuable temporal: el jugador mantiene E, el puesto hace ruido
## periódico y, al completarse, libera componentes pequeños que se pueden
## guardar en el inventario. No sustituye el sistema definitivo de desmontaje
## de la sección 32; valida el bucle de tiempo, ruido, riesgo y recuperación.

signal dismantle_started
signal dismantle_progress(progress: float, seconds_left: float)
signal dismantle_completed(components: Array)
signal dismantle_cancelled

const CARRY_ITEM_SCENE := preload("res://scenes/fm/carry_item.tscn")

@export var display_name := "PUESTO DE ANÁLISIS"
@export var dismantle_duration := 6.0
@export var noise_interval := 1.0
@export var noise_radius := 8.0
@export var cancel_distance := 3.6

var game: Node = null
var dismantling := false
var completed := false
var progress := 0.0
var components: Array[FMCarryItem] = []

var _player: Node3D = null
var _noise_timer := 0.0
var _indicator: MeshInstance3D
var _indicator_mat: StandardMaterial3D
var _time := 0.0

func _ready() -> void:
	collision_layer = 1
	collision_mask = 0
	add_to_group("fm_interactable")
	_build_visual()
	_build_collision()

func _build_collision() -> void:
	var shape := BoxShape3D.new()
	shape.size = Vector3(1.05, 0.95, 0.75)
	var collider := CollisionShape3D.new()
	collider.name = "DismantleCollider"
	collider.shape = shape
	collider.position = Vector3(0.0, 0.475, 0.0)
	add_child(collider)

func _build_visual() -> void:
	var steel := StandardMaterial3D.new()
	steel.albedo_color = Color(0.052, 0.060, 0.066, 1.0)
	steel.metallic = 0.78
	steel.roughness = 0.42

	var dark := StandardMaterial3D.new()
	dark.albedo_color = Color(0.018, 0.022, 0.026, 1.0)
	dark.metallic = 0.55
	dark.roughness = 0.60

	var hazard := StandardMaterial3D.new()
	hazard.albedo_color = Color(0.72, 0.52, 0.06, 1.0)
	hazard.metallic = 0.22
	hazard.roughness = 0.58

	_mesh_box("Base", Vector3(0.95, 0.90, 0.65), Vector3(0.0, 0.45, 0.0), steel)
	_mesh_box("Top", Vector3(1.05, 0.06, 0.75), Vector3(0.0, 0.93, 0.0), dark)
	_mesh_box("HazardStrip", Vector3(1.00, 0.08, 0.020), Vector3(0.0, 0.18, 0.335), hazard)
	_mesh_box("ScreenFrame", Vector3(0.38, 0.26, 0.026), Vector3(0.0, 1.16, 0.338), dark)

	_indicator_mat = StandardMaterial3D.new()
	_indicator_mat.albedo_color = Color(0.04, 0.32, 0.18, 1.0)
	_indicator_mat.emission_enabled = true
	_indicator_mat.emission = Color(0.10, 1.0, 0.42)
	_indicator_mat.emission_energy_multiplier = 1.2
	_indicator_mat.roughness = 0.28
	_indicator = _mesh_box("Screen", Vector3(0.30, 0.16, 0.014), Vector3(0.0, 1.16, 0.354), _indicator_mat)

	for i in range(4):
		var x := -0.30 + float(i) * 0.20
		_mesh_box("Socket_%d" % i, Vector3(0.12, 0.035, 0.12), Vector3(x, 0.965, 0.0), dark)
		_mesh_box("SocketLight_%d" % i, Vector3(0.05, 0.010, 0.05), Vector3(x, 0.985, 0.0), hazard)

func _mesh_box(node_name: String, size: Vector3, pos: Vector3, material: Material) -> MeshInstance3D:
	var box := MeshInstance3D.new()
	box.name = node_name
	var mesh := BoxMesh.new()
	mesh.size = size
	box.mesh = mesh
	box.material_override = material
	box.position = pos
	box.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	add_child(box)
	return box

func can_interact(who: Node = null) -> bool:
	if completed:
		return false
	if game != null and game.has_method("get_active_player_count") and int(game.state) != 0:
		return false
	if who == null or not (who is Node3D):
		return false
	var distance: float = (who as Node3D).global_position.distance_to(get_interaction_position())
	return distance <= 2.8

func get_interaction_prompt() -> String:
	if completed:
		return "PUESTO DE ANÁLISIS · VACÍO"
	if dismantling:
		return "E   CANCELAR DESMONTAJE"
	return "E   DESMONTAR %s" % display_name

func get_interaction_position() -> Vector3:
	return global_position + Vector3(0.0, 1.0, 0.0)

func interact(who: Node = null) -> bool:
	if completed or who == null or not (who is Node3D):
		return false
	if dismantling:
		_cancel()
		return true
	_player = who as Node3D
	dismantling = true
	progress = 0.0
	_noise_timer = 0.0
	_set_indicator(Color(1.0, 0.48, 0.08), 1.6)
	if game != null:
		if game.has_method("emit_noise"):
			game.emit_noise(global_position, 3.0, "dismantle_start")
		if game.has_method("notify"):
			game.notify("DESMONTAJE INICIADO · RUIDO PERIÓDICO")
	Audio.play_sfx("click", -10.0)
	dismantle_started.emit()
	return true

func _process(delta: float) -> void:
	_time += delta
	if _indicator != null:
		var pulse := 0.75 + sin(_time * 5.0) * 0.20
		_indicator_mat.emission_energy_multiplier = pulse if dismantling else 1.2
	if not dismantling:
		return
	if _player == null or not is_instance_valid(_player):
		_cancel()
		return
	if _player.global_position.distance_to(global_position) > cancel_distance:
		_cancel()
		return

	progress = minf(dismantle_duration, progress + delta)
	_noise_timer += delta
	if _noise_timer >= noise_interval:
		_noise_timer = 0.0
		if game != null and game.has_method("emit_noise"):
			game.emit_noise(global_position, noise_radius, "dismantle")
		Audio.play_sfx("click", -12.0, 0.9)
	dismantle_progress.emit(progress / maxf(0.001, dismantle_duration), maxf(0.0, dismantle_duration - progress))
	if progress >= dismantle_duration:
		_complete()

func _complete() -> void:
	if completed:
		return
	dismantling = false
	completed = true
	progress = dismantle_duration
	_set_indicator(Color(0.10, 1.0, 0.42), 1.0)
	_spawn_components()
	if game != null and game.has_method("on_dismantle_completed"):
		game.on_dismantle_completed(self, components)
	dismantle_completed.emit(components)

func _spawn_components() -> void:
	var defs := [
		{"name": "MUESTRA A", "mass": 0.6, "color": Color(0.24, 0.62, 0.78)},
		{"name": "MUESTRA B", "mass": 0.8, "color": Color(0.46, 0.72, 0.38)},
		{"name": "NÚCLEO SECUNDARIO", "mass": 1.2, "color": Color(0.82, 0.56, 0.18)},
		{"name": "DOCUMENTO TÉCNICO", "mass": 0.3, "color": Color(0.78, 0.74, 0.62)},
	]
	var offsets := [
		Vector3(-0.30, 1.08, 0.0),
		Vector3(-0.10, 1.08, 0.10),
		Vector3(0.10, 1.08, -0.05),
		Vector3(0.30, 1.08, 0.06),
	]
	for i in range(defs.size()):
		var data: Dictionary = defs[i]
		var color: Color = data["color"]
		var offset: Vector3 = offsets[i]
		var item := CARRY_ITEM_SCENE.instantiate() as FMCarryItem
		item.name = "Dismantle_Component_%d" % i
		item.item_name = str(data["name"])
		item.item_mass = float(data["mass"])
		item.size_class = "SMALL"
		item.item_kind = "component"
		item.is_mission_item = false
		item.visual_style = "COMPONENT"
		item.display_color = color
		item.position = global_position + offset
		item.game = game
		get_parent().add_child(item)
		if game != null and game.has_method("register_carry_item"):
			game.register_carry_item(item)
		components.append(item)

func _cancel() -> void:
	if not dismantling:
		return
	dismantling = false
	progress = 0.0
	_noise_timer = 0.0
	_set_indicator(Color(0.10, 1.0, 0.42), 1.2)
	if game != null and game.has_method("notify"):
		game.notify("DESMONTAJE CANCELADO")
	dismantle_cancelled.emit()

func _set_indicator(color: Color, energy: float) -> void:
	if _indicator_mat == null:
		return
	_indicator_mat.albedo_color = Color(color.r * 0.22, color.g * 0.22, color.b * 0.22, 1.0)
	_indicator_mat.emission = color
	_indicator_mat.emission_energy_multiplier = energy
