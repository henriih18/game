extends Area3D
class_name FMReceptionExtraction

## Extracción del vertical slice: zona del ala sur de Recepción, junto a la
## compuerta de entrega. El jugador debe llevar el botín al centro de entrega.

signal extraction_started
signal extraction_progress(stage: String, seconds_left: float)
signal extraction_completed(delivered_loot: int)

@export var activation_time_s := 2.0
@export var sequence_duration_s := 6.7
@export var door_open_s := 1.5
@export var door_hold_s := 2.5
@export var door_close_s := 1.0
@export var travel_s := 1.3
@export var arrival_confirm_s := 0.4
@export var delivery_radius_m := 2.4
@export var max_players := 8
@export var zone_size := Vector3(9.0, 2.6, 8.0)

var game: Node = null
var players_inside: Array[Node3D] = []
var delivery_center := Vector3(-94.0, 0.30, 37.6)

var _state := "waiting"  # waiting | activating | sequence | done
var _activation_timer := 0.0
var _sequence_timer := 0.0
var _stage := ""

func _ready() -> void:
	collision_layer = 0
	collision_mask = 2
	set_deferred("monitoring", true)
	add_to_group("fm_extraction")
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)
	var shape := BoxShape3D.new()
	shape.size = zone_size
	var collider := CollisionShape3D.new()
	collider.name = "ExtractionZoneCollider"
	collider.shape = shape
	add_child(collider)

func _on_body_entered(body: Node3D) -> void:
	if body.is_in_group("fm_player") and not players_inside.has(body):
		players_inside.append(body)

func _on_body_exited(body: Node3D) -> void:
	players_inside.erase(body)

func has_player() -> bool:
	return not players_inside.is_empty()

func _physics_process(delta: float) -> void:
	if game == null or _state == "done":
		return

	var valid_players: int = int(game.get_active_player_count())
	if valid_players <= 0:
		_reset()
		return

	var delivered: int = int(game.get_delivered_loot_count(delivery_center, delivery_radius_m))
	var all_inside: bool = bool(game.all_alive_players_inside(self))
	var mission_delivered := true
	if game.has_method("has_delivered_mission_item"):
		mission_delivered = bool(game.has_delivered_mission_item(delivery_center, delivery_radius_m))

	if _state == "waiting" or _state == "activating":
		if delivered > 0 and mission_delivered and all_inside:
			_state = "activating"
			_activation_timer += delta
			game.on_extraction_progress("activando", maxf(0.0, activation_time_s - _activation_timer))
			if _activation_timer >= activation_time_s:
				_begin_sequence()
		else:
			_state = "waiting"
			_activation_timer = 0.0
		return

	if _state == "sequence":
		_sequence_timer += delta
		_stage = _stage_for_time(_sequence_timer)
		game.on_extraction_progress(_stage, maxf(0.0, sequence_duration_s - _sequence_timer))
		if not mission_delivered:
			_cancel_sequence()
			return
		if not all_inside and not bool(game.any_alive_player_inside(self)):
			_cancel_sequence()
			return
		if _sequence_timer >= sequence_duration_s:
			_finish_sequence()

func _stage_for_time(time_s: float) -> String:
	if time_s < door_open_s:
		return "apertura"
	var t := time_s - door_open_s
	if t < door_hold_s:
		return "espera"
	t -= door_hold_s
	if t < door_close_s:
		return "cierre"
	t -= door_close_s
	if t < travel_s:
		return "viaje"
	return "llegada"

func _begin_sequence() -> void:
	_state = "sequence"
	_sequence_timer = 0.0
	_stage = ""
	if game != null:
		game.on_extraction_started()
	extraction_started.emit()

func _cancel_sequence() -> void:
	_state = "waiting"
	_activation_timer = 0.0
	_sequence_timer = 0.0
	_stage = ""
	if game != null:
		game.on_extraction_cancelled()

func _finish_sequence() -> void:
	_state = "done"
	var delivered: int = 0
	if game != null:
		delivered = int(game.get_delivered_loot_count(delivery_center, delivery_radius_m))
	extraction_completed.emit(delivered)

func _reset() -> void:
	_state = "waiting"
	_activation_timer = 0.0
	_sequence_timer = 0.0
	_stage = ""
