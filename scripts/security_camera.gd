extends Area2D

var triggered := false

@onready var zone_visual: ColorRect = $Zone
@onready var lens: ColorRect = $CameraBody/Lens

func _process(_delta: float) -> void:
	var now := _sees_player()
	if now == triggered:
		return
	triggered = now
	if triggered:
		zone_visual.color = Color(1.0, 0.25, 0.25, 0.2)
		lens.color = Color(1.0, 0.3, 0.3, 1.0)
		Audio.play_sfx("camera", -18.0, randf_range(0.95, 1.05))
	else:
		zone_visual.color = Color(1.0, 0.8, 0.25, 0.09)
		lens.color = Color(0.98, 0.82, 0.3, 1.0)

func _sees_player() -> bool:
	for body in get_overlapping_bodies():
		if body.is_in_group("player"):
			return true
	return false
