extends CharacterBody2D

@export var speed: float = 340.0
@export var carry_speed_multiplier: float = 0.55

var carried: Crate = null

@onready var grab_area: Area2D = $GrabArea

func _physics_process(_delta: float) -> void:
	if carried != null and carried.delivered:
		carried = null

	var direction := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	var current_speed := speed
	if carried != null:
		current_speed *= carry_speed_multiplier
	velocity = direction * current_speed
	move_and_slide()
	_clamp_to_screen()

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("interact"):
		_toggle_grab()

func _toggle_grab() -> void:
	if carried != null:
		_drop()
		return
	for area in grab_area.get_overlapping_areas():
		if area is Crate:
			var crate := area as Crate
			if not crate.delivered:
				carried = crate
				crate.get_grabbed(self)
				return

func _drop() -> void:
	if carried != null:
		carried.release()
		carried = null

func _clamp_to_screen() -> void:
	var rect := get_viewport_rect()
	global_position = global_position.clamp(rect.position + Vector2(20, 52), rect.end - Vector2(20, 56))
