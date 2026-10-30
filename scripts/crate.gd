class_name Crate
extends Area2D

const CARRY_OFFSET := Vector2(0, -46)

var holder_ids: Array[int] = []
var delivered := false
var game: Node = null

@onready var visual: Sprite2D = $Visual

func _ready() -> void:
	add_to_group("crate")

func _process(delta: float) -> void:
	if delivered:
		return
	if game == null or not is_instance_valid(game):
		game = get_tree().get_first_node_in_group("game")
	if game == null:
		return

	var total := Vector2.ZERO
	var count := 0
	for id in holder_ids:
		var player = game.players.get(id)
		if player != null and is_instance_valid(player):
			total += player.global_position
			count += 1
	if count > 0:
		global_position = total / float(count) + CARRY_OFFSET
		visual.rotation = sin(Time.get_ticks_msec() / 1000.0 * 8.0) * 0.05
	else:
		visual.rotation = lerpf(visual.rotation, 0.0, minf(1.0, 10.0 * delta))

func add_holder(id: int) -> void:
	if delivered or holder_ids.has(id):
		return
	var previous := holder_ids.size()
	holder_ids.append(id)
	z_index = 1
	_announce_holder_change(previous)

func remove_holder(id: int) -> void:
	if not holder_ids.has(id):
		return
	var previous := holder_ids.size()
	holder_ids.erase(id)
	if holder_ids.is_empty():
		z_index = 0
	_announce_holder_change(previous)

func _announce_holder_change(previous: int) -> void:
	if delivered:
		return
	if holder_ids.size() > previous:
		Audio.play_sfx("grab", -10.0)
	elif holder_ids.size() < previous:
		Audio.play_sfx("drop", -10.0)

func holder_count() -> int:
	return holder_ids.size()

@rpc("authority", "call_local", "reliable")
func publish_holders(ids: Array) -> void:
	var previous := holder_ids.size()
	holder_ids.assign(ids)
	z_index = 1 if not holder_ids.is_empty() else 0
	_announce_holder_change(previous)

@rpc("authority", "call_local", "reliable")
func deliver() -> void:
	if delivered:
		return
	delivered = true
	holder_ids.clear()
	z_index = 0
	remove_from_group("crate")
	visual.modulate = Color(0.65, 1.0, 0.75)
	visual.rotation = 0.0
	Audio.play_sfx("deliver", -5.0)
	Effects.burst(get_parent(), global_position, Color(0.45, 1.0, 0.65), 24, 1.3)
	var zone := get_tree().get_first_node_in_group("extraction_zone")
	if zone != null and zone.has_method("pulse"):
		zone.pulse()
