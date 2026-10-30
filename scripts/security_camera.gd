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
		if not body.is_in_group("player"):
			continue
		var target := body as CollisionObject2D
		if target == null:
			continue
		# El Area2D detecta por superposición, pero no conoce las paredes.
		# El rayo comprueba que no haya un muro entre la lente y el jugador.
		var query := PhysicsRayQueryParameters2D.create(global_position, target.global_position)
		query.collision_mask = 1
		query.exclude = [target.get_rid()]
		var hit := get_world_2d().direct_space_state.intersect_ray(query)
		if hit.is_empty() or hit.get("collider") == target:
			return true
	return false
