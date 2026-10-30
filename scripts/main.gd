extends Node2D

enum State { PLAYING, WON, LOST }

const TOTAL_GEMS := 3
const ROUND_TIME := 120.0
const ALARM_MAX := 100.0
const ALARM_RATE := 35.0
const ALARM_DECAY := 12.0

var gems_collected := 0
var crate_delivered := false
var state := State.PLAYING
var time_left := ROUND_TIME
var alarm := 0.0

@onready var status_label: Label = $HUD/StatusLabel
@onready var timer_label: Label = $HUD/TimerLabel
@onready var alarm_fill: ColorRect = $HUD/AlarmFill
@onready var overlay: ColorRect = $HUD/Overlay
@onready var result_label: Label = $HUD/Overlay/ResultLabel

func _ready() -> void:
	for gem in $Gems.get_children():
		gem.connect("collected", _on_gem_collected)
	$ExtractionZone.connect("crate_delivered", _on_crate_delivered)
	_update_status()
	_update_hud()

func _process(delta: float) -> void:
	if state != State.PLAYING:
		return

	time_left = maxf(time_left - delta, 0.0)

	var cameras_seeing := 0
	for camera in $Cameras.get_children():
		if camera.get("triggered"):
			cameras_seeing += 1

	if cameras_seeing > 0:
		alarm = minf(alarm + ALARM_RATE * cameras_seeing * delta, ALARM_MAX)
	else:
		alarm = maxf(alarm - ALARM_DECAY * delta, 0.0)

	_update_hud()

	if alarm >= ALARM_MAX:
		_end(State.LOST, "¡ALARMA MÁXIMA!")
	elif time_left <= 0.0:
		_end(State.LOST, "¡SE ACABÓ EL TIEMPO!")

func _update_hud() -> void:
	timer_label.text = "Tiempo: %d:%02d" % [floori(time_left / 60.0), int(time_left) % 60]
	alarm_fill.size.x = 224.0 * clampf(alarm / ALARM_MAX, 0.0, 1.0)

func _on_gem_collected() -> void:
	gems_collected += 1
	_update_status()
	_check_win()

func _on_crate_delivered() -> void:
	crate_delivered = true
	$Crate.call("deliver")
	_update_status()
	_check_win()

func _check_win() -> void:
	if state == State.PLAYING and gems_collected >= TOTAL_GEMS and crate_delivered:
		_end(State.WON, "¡ROBO COMPLETO!")

func _update_status() -> void:
	var crate_state := "extraída" if crate_delivered else "pendiente"
	status_label.text = "Gemas: %d/%d  ·  Caja: %s" % [gems_collected, TOTAL_GEMS, crate_state]

func _end(new_state: State, message: String) -> void:
	state = new_state
	result_label.text = message
	overlay.visible = true
	for player in get_tree().get_nodes_in_group("player"):
		player.set_physics_process(false)

func _unhandled_input(event: InputEvent) -> void:
	if state != State.PLAYING and event.is_action_pressed("restart"):
		get_tree().reload_current_scene()
