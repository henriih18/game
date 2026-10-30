extends CharacterBody2D

const GRAB_RANGE := 160.0

@export var player_index: int = 0
@export var speed: float = 340.0
@export var carry_speed_one: float = 0.45
@export var carry_speed_two: float = 0.8

var game_id := 0
var net_id := 0
var net_target := Vector2.ZERO
var sync_accum := 0.0
var game: Node = null
var _anim_time := 0.0
var _step_accum := 0.0

@onready var grab_area: Area2D = $GrabArea
@onready var visual: Sprite2D = $Visual

func _ready() -> void:
	add_to_group("player")
	net_target = position

func setup_network(pid: int) -> void:
	net_id = pid
	game_id = pid
	set_multiplayer_authority(pid)
	if pid != 1:
		visual.texture = preload("res://assets/art/player_thief_2.svg")

func _physics_process(delta: float) -> void:
	if game == null or not is_instance_valid(game):
		game = get_tree().get_first_node_in_group("game")

	if net_id > 0 and not is_multiplayer_authority():
		var previous := position
		position = position.lerp(net_target, minf(1.0, 20.0 * delta))
		_animate(delta, position.distance_to(previous) > 0.5)
		return

	if game != null and game.state != 0:
		return

	var direction := Input.get_vector(_action("left"), _action("right"), _action("up"), _action("down"))
	velocity = direction * speed * _carry_multiplier()
	move_and_slide()
	_clamp_to_screen()

	var moving := direction.length() > 0.1 and velocity.length() > 5.0
	_animate(delta, moving)
	if _is_controlled() and moving:
		_step_accum += delta
		var interval := 0.27 / clampf(_carry_multiplier(), 0.45, 1.0)
		if _step_accum >= interval:
			_step_accum = 0.0
			Audio.play_sfx("step", -20.0, randf_range(0.9, 1.1))
	else:
		_step_accum = 0.0

	if net_id > 0:
		sync_accum += delta
		if sync_accum >= 0.05:
			sync_accum = 0.0
			sync_position.rpc(position)

@rpc("authority", "call_remote", "unreliable_ordered")
func sync_position(new_position: Vector2) -> void:
	net_target = new_position

func _action(suffix: String) -> String:
	if net_id > 0:
		return "move_" + suffix
	var prefix := "move_" if player_index == 0 else "move2_"
	return prefix + suffix

func _interact_action() -> String:
	if net_id > 0:
		return "interact"
	return "interact" if player_index == 0 else "interact2"

func _carry_multiplier() -> float:
	if game == null:
		return 1.0
	var crate = game.get_node_or_null("Crate")
	if crate == null or crate.delivered:
		return 1.0
	if not crate.holder_ids.has(game_id):
		return 1.0
	return carry_speed_two if crate.holder_count() >= 2 else carry_speed_one

func _is_controlled() -> bool:
	if net_id > 0:
		return is_multiplayer_authority()
	return true

func _unhandled_input(event: InputEvent) -> void:
	if not _is_controlled():
		return
	if game != null and game.state != 0:
		return
	if event.is_action_pressed(_interact_action()):
		get_viewport().set_input_as_handled()
		_toggle_grab()

func _find_crate():
	return get_tree().get_first_node_in_group("crate")

func _toggle_grab() -> void:
	var crate = _find_crate()
	if crate == null or crate.delivered:
		return
	if net_id > 0:
		if multiplayer.is_server():
			server_toggle_grab()
		else:
			server_toggle_grab.rpc_id(1)
		return
	if crate.holder_ids.has(game_id):
		crate.remove_holder(game_id)
	elif position.distance_to(crate.global_position) <= GRAB_RANGE:
		crate.add_holder(game_id)

@rpc("any_peer", "call_local", "reliable")
func server_toggle_grab() -> void:
	if not multiplayer.is_server():
		return
	var sender := multiplayer.get_remote_sender_id()
	if sender != 0 and sender != net_id:
		return
	var crate = _find_crate()
	if crate == null or crate.delivered:
		return
	if crate.holder_ids.has(game_id):
		crate.remove_holder(game_id)
	else:
		if global_position.distance_to(crate.global_position) > GRAB_RANGE:
			return
		crate.add_holder(game_id)
	crate.publish_holders.rpc(crate.holder_ids)

func _clamp_to_screen() -> void:
	var rect := get_viewport_rect()
	global_position = global_position.clamp(rect.position + Vector2(20, 52), rect.end - Vector2(20, 56))

func _animate(delta: float, moving: bool) -> void:
	_anim_time += delta
	var target_y := -absf(sin(_anim_time * 13.0)) * 3.0 if moving else sin(_anim_time * 2.2) * 0.8
	var target_rotation := sin(_anim_time * 13.0) * 0.05 if moving else 0.0
	var weight := minf(1.0, 18.0 * delta)
	visual.position.y = lerpf(visual.position.y, target_y, weight)
	visual.rotation = lerpf(visual.rotation, target_rotation, weight)
