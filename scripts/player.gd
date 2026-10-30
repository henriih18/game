extends CharacterBody2D

@export var speed: float = 320.0

func _physics_process(_delta: float) -> void:
	var direction := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	velocity = direction * speed
	move_and_slide()
	_clamp_to_screen()

func _clamp_to_screen() -> void:
	var rect := get_viewport_rect()
	global_position = global_position.clamp(rect.position + Vector2(16, 16), rect.end - Vector2(16, 16))
