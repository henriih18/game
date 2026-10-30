class_name Crate
extends Area2D

const CARRY_OFFSET := Vector2(0, -46)

var holders: Array[Node2D] = []
var delivered := false

func _ready() -> void:
	add_to_group("crate")

func _process(_delta: float) -> void:
	if holders.is_empty():
		return

	var valid_holders: Array[Node2D] = []
	var sum := Vector2.ZERO
	for holder in holders:
		if is_instance_valid(holder):
			valid_holders.append(holder)
			sum += holder.global_position
	holders = valid_holders

	if holders.is_empty():
		return
	global_position = sum / holders.size() + CARRY_OFFSET

func add_holder(by: Node2D) -> void:
	if delivered or by in holders:
		return
	holders.append(by)
	z_index = 1

func remove_holder(by: Node2D) -> void:
	holders.erase(by)
	if holders.is_empty():
		z_index = 0

func holder_count() -> int:
	return holders.size()

func deliver() -> void:
	delivered = true
	holders.clear()
	z_index = 0
	remove_from_group("crate")
	modulate = Color(0.6, 1.0, 0.75)
