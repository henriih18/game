class_name Effects
extends RefCounted

const SPARK := preload("res://assets/art/spark.svg")

static func burst(parent: Node, pos: Vector2, color: Color, amount := 16, speed := 1.0) -> void:
	if parent == null or not parent.is_inside_tree():
		return
	var particles := CPUParticles2D.new()
	particles.texture = SPARK
	particles.amount = amount
	particles.one_shot = true
	particles.explosiveness = 0.92
	particles.lifetime = 0.65
	particles.direction = Vector2(0, -1)
	particles.spread = 180.0
	particles.initial_velocity_min = 70.0 * speed
	particles.initial_velocity_max = 200.0 * speed
	particles.gravity = Vector2(0, 240)
	particles.scale_amount_min = 0.5
	particles.scale_amount_max = 1.1
	particles.color = color
	particles.finished.connect(particles.queue_free)
	parent.add_child(particles)
	particles.global_position = pos
	particles.emitting = true
