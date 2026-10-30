class_name Crate
extends Area2D

const CARRY_OFFSET := Vector2(0, -46)

var holder_ids: Array[int] = []
var delivered := false
var game: Node = null

@onready var visual: Sprite2D = $Visual

func _ready() -> void:
	add_to_group("crate")

func _process(_delta: float) -> void:
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

func add_holder(id: int) -> void:
	if delivered or holder_ids.has(id):
		return
	holder_ids.append(id)
	z_index = 1

func remove_holder(id: int) -> void:
	holder_ids.erase(id)
	if holder_ids.is_empty():
		z_index = 0

func holder_count() -> int:
	return holder_ids.size()

@rpc("authority", "call_local", "reliable")
func publish_holders(ids: Array) -> void:
	holder_ids.assign(ids)
	z_index = 1 if not holder_ids.is_empty() else 0

@rpc("authority", "call_local", "reliable")
func deliver() -> void:
	if delivered:
		return
	delivered = true
	holder_ids.clear()
	z_index = 0
	remove_from_group("crate")
	visual.modulate = Color(0.65, 1.0, 0.75)
