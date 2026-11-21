extends Area2D

signal crate_delivered

var _done := false

func _ready() -> void:
	add_to_group("extraction_zone")
	area_entered.connect(_on_area_entered)
	var breathe := create_tween().set_loops()
	breathe.tween_property($Visual, "color:a", 0.24, 1.6).set_trans(Tween.TRANS_SINE)
	breathe.tween_property($Visual, "color:a", 0.12, 1.6).set_trans(Tween.TRANS_SINE)

func pulse() -> void:
	modulate = Color(1.7, 1.7, 1.7)
	create_tween().tween_property(self, "modulate", Color.WHITE, 0.5)

func _on_area_entered(area: Area2D) -> void:
	if _done:
		return
	if not (area is Crate):
		return
	_done = true
	crate_delivered.emit()
