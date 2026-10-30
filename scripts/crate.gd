class_name Crate
extends Area2D

const CARRY_OFFSET := Vector2(0, -46)

var holder: Node2D = null
var delivered := false

func _ready() -> void:
	add_to_group("crate")

func _process(_delta: float) -> void:
	if is_instance_valid(holder):
		global_position = holder.global_position + CARRY_OFFSET

func get_grabbed(by: Node2D) -> void:
	if delivered:
		return
	holder = by
	z_index = 1

func release() -> void:
	holder = null
	z_index = 0

func deliver() -> void:
	delivered = true
	holder = null
	z_index = 0
	remove_from_group("crate")
	modulate = Color(0.6, 1.0, 0.75)
