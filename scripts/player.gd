extends CharacterBody2D

const MAX_CARRY_DISTANCE := 140.0

@export var player_index: int = 0
@export var speed: float = 340.0
@export var carry_speed_one: float = 0.45
@export var carry_speed_two: float = 0.8

var carried: Crate = null

@onready var grab_area: Area2D = $GrabArea

func _physics_process(_delta: float) -> void:
	if carried != null and carried.delivered:
		carried = null
	if carried != null and global_position.distance_to(carried.global_position) > MAX_CARRY_DISTANCE:
		_drop()

	var direction := Input.get_vector(_action("left"), _action("right"), _action("up"), _action("down"))
	var current_speed := speed
	if carried != null:
		current_speed *= carry_speed_two if carried.holder_count() >= 2 else carry_speed_one
	velocity = direction * current_speed
	move_and_slide()
	_clamp_to_screen()

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(_interact_action()):
		_toggle_grab()

func _action(suffix: String) -> String:
	var prefix := "move_" if player_index == 0 else "move2_"
	return prefix + suffix

func _interact_action() -> String:
	return "interact" if player_index == 0 else "interact2"

func _toggle_grab() -> void:
	if carried != null:
		_drop()
		return
	for area in grab_area.get_overlapping_areas():
		if area is Crate:
			var crate := area as Crate
			if not crate.delivered:
				crate.add_holder(self)
				carried = crate
				return

func _drop() -> void:
	if carried != null:
		carried.remove_holder(self)
		carried = null

func _clamp_to_screen() -> void:
	var rect := get_viewport_rect()
	global_position = global_position.clamp(rect.position + Vector2(20, 52), rect.end - Vector2(20, 56))
