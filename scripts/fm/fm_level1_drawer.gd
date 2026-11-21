extends Node3D

## Cajón o puerta de armario local del Nivel 1. No modifica sistemas compartidos.

var game
var target: Node3D
var closed_position := Vector3.ZERO
var open_offset := Vector3.ZERO
var label := "CAJÓN"
var is_open := false
var busy := false
var _tween: Tween

func setup(target_node: Node3D, offset: Vector3, display_label: String, game_ref) -> void:
	target = target_node
	open_offset = offset
	label = display_label
	game = game_ref
	name = "Interact_%s" % display_label.replace(" ", "_")
	add_to_group("fm_interactable")
	closed_position = target.global_position
	global_position = closed_position + Vector3(0.0, 0.15, 0.0)

func can_interact(player) -> bool:
	return target != null and is_instance_valid(target) and not busy and player != null and target.global_position.distance_to(player.global_position) <= 2.4

func get_interaction_prompt() -> String:
	return "E CERRAR " + label if is_open else "E ABRIR " + label

func get_interaction_position() -> Vector3:
	return target.global_position

func interact(_player) -> void:
	if busy or target == null or not is_instance_valid(target):
		return
	is_open = not is_open
	var destination := closed_position + (open_offset if is_open else Vector3.ZERO)
	if game != null and game.has_method("emit_noise"):
		game.emit_noise(target.global_position, 3.6 if is_open else 2.6, "drawer")
	Audio.play_sfx("click", -12.0, 0.88 if is_open else 1.04)
	busy = true
	if _tween != null and _tween.is_valid():
		_tween.kill()
	_tween = create_tween()
	_tween.tween_property(target, "global_position", destination, 0.38).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	_tween.finished.connect(func(): busy = false)
