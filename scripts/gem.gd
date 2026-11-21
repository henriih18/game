extends Area2D

signal collected(gem: Node)

func _ready() -> void:
	var tween := create_tween().set_loops()
	tween.tween_property($Visual, "position:y", -4.0, 0.7).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tween.tween_property($Visual, "position:y", 0.0, 0.7).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)

func _on_body_entered(body: Node2D) -> void:
	if not body.is_in_group("player"):
		return
	if multiplayer.has_multiplayer_peer() and not multiplayer.is_server():
		return
	collected.emit(self)
