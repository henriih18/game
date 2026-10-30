extends Area2D

signal crate_delivered

var _done := false

func _ready() -> void:
	area_entered.connect(_on_area_entered)

func _on_area_entered(area: Area2D) -> void:
	if _done:
		return
	if not (area is Crate):
		return
	_done = true
	crate_delivered.emit()
