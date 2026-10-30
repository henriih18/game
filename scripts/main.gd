extends Node2D

enum State { PLAYING, WON, LOST }
enum Mode { LOCAL, HOST, CLIENT }

const PLAYER_SCENE := preload("res://scenes/player.tscn")
const PLAYER2_SCENE := preload("res://scenes/player2.tscn")

const MENU_SCENE := "res://scenes/menu.tscn"
const TOTAL_GEMS := 3
const ROUND_TIME := 120.0
const ALARM_MAX := 100.0
const ALARM_RATE := 35.0
const ALARM_DECAY := 12.0
const SYNC_INTERVAL := 0.1

var players: Dictionary = {}
var gems_collected := 0
var collected_gems: Array[String] = []
var crate_delivered := false
var state := State.PLAYING
var time_left := ROUND_TIME
var alarm := 0.0
var sync_accum := 0.0
var _last_tick_second := -1
var _vignette_material: ShaderMaterial

@onready var status_label: Label = $HUD/StatusLabel
@onready var hint_label: Label = $HUD/HintLabel
@onready var timer_label: Label = $HUD/TimerLabel
@onready var alarm_fill: ColorRect = $HUD/AlarmFill
@onready var danger_vignette: ColorRect = $HUD/DangerVignette
@onready var overlay: ColorRect = $HUD/Overlay
@onready var result_label: Label = $HUD/Overlay/ResultLabel

func _ready() -> void:
	add_to_group("game")
	Audio.play_music("heist")
	_vignette_material = danger_vignette.material as ShaderMaterial

	for gem in $Gems.get_children():
		gem.collected.connect(_on_gem_collected)
	$ExtractionZone.crate_delivered.connect(_on_crate_delivered)

	multiplayer.peer_disconnected.connect(_on_peer_disconnected)
	multiplayer.server_disconnected.connect(_leave_to_menu)

	if _net_mode() == Mode.LOCAL:
		_spawn_local_players()
	elif _net_mode() == Mode.HOST:
		_spawn_player_local(1)
	else:
		_client_request_spawn()

	if _net_mode() != Mode.LOCAL:
		hint_label.text = "WASD para moverte  ·  E para agarrar/soltar  ·  Evitá las cámaras"

	_update_status()
	_update_hud()

func _net_mode() -> int:
	var peer := multiplayer.multiplayer_peer
	if peer == null or not (peer is ENetMultiplayerPeer):
		return Mode.LOCAL
	return Mode.HOST if multiplayer.is_server() else Mode.CLIENT

func _is_server_logic() -> bool:
	return _net_mode() != Mode.CLIENT

func _process(delta: float) -> void:
	if not _is_server_logic():
		return
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

	if _net_mode() == Mode.HOST:
		sync_accum += delta
		if sync_accum >= SYNC_INTERVAL:
			sync_accum = 0.0
			sync_state.rpc(time_left, alarm, gems_collected, crate_delivered, state)

	if alarm >= ALARM_MAX:
		_end(State.LOST, "¡ALARMA MÁXIMA!")
	elif time_left <= 0.0:
		_end(State.LOST, "¡SE ACABÓ EL TIEMPO!")

func _update_hud() -> void:
	timer_label.text = "Tiempo: %d:%02d" % [floori(time_left / 60.0), int(time_left) % 60]
	alarm_fill.size.x = 224.0 * clampf(alarm / ALARM_MAX, 0.0, 1.0)
	alarm_fill.color = Color(0.95, lerpf(0.55, 0.2, clampf(alarm / ALARM_MAX, 0.0, 1.0)), 0.3)

	var danger := clampf((alarm - 40.0) / (ALARM_MAX - 40.0), 0.0, 1.0)
	if state != State.PLAYING:
		danger = 0.0
	_vignette_material.set_shader_parameter("intensity", danger * 0.62)
	Audio.set_alarm(alarm, state == State.PLAYING)

	if state == State.PLAYING and time_left <= 20.0:
		var pulse := 0.5 + 0.5 * sin(Time.get_ticks_msec() / 1000.0 * 9.0)
		timer_label.modulate = Color(1.0, 0.35 + 0.25 * pulse, 0.35 + 0.15 * pulse)
	else:
		timer_label.modulate = Color.WHITE

	if state == State.PLAYING:
		var seconds := int(ceilf(time_left))
		if seconds <= 10 and seconds > 0 and seconds != _last_tick_second:
			_last_tick_second = seconds
			Audio.play_sfx("tick", -15.0, 1.0 if seconds > 5 else 1.12)

func _pulse_status() -> void:
	var tween := create_tween()
	status_label.scale = Vector2(1.06, 1.06)
	tween.tween_property(status_label, "scale", Vector2.ONE, 0.28).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)

func _spawn_local_players() -> void:
	var p1 := PLAYER_SCENE.instantiate()
	p1.name = "P1"
	p1.game_id = 1
	p1.player_index = 0
	p1.position = Vector2(640, 600)
	$Players.add_child(p1)
	players[1] = p1

	var p2 := PLAYER2_SCENE.instantiate()
	p2.name = "P2"
	p2.game_id = 2
	p2.player_index = 1
	p2.position = Vector2(780, 600)
	$Players.add_child(p2)
	players[2] = p2

func _client_request_spawn() -> void:
	for i in 20:
		if players.has(multiplayer.get_unique_id()):
			return
		client_ready.rpc_id(1)
		await get_tree().create_timer(0.4).timeout

@rpc("any_peer", "call_remote", "reliable")
func client_ready() -> void:
	if not multiplayer.is_server():
		return
	var pid := multiplayer.get_remote_sender_id()
	if pid <= 0 or players.has(pid):
		return
	for existing_id in players.keys():
		spawn_player.rpc_id(pid, existing_id)
	spawn_player.rpc(pid)
	_sync_full_state(pid)

func _sync_full_state(pid: int) -> void:
	sync_full_state.rpc_id(pid, time_left, alarm, gems_collected, crate_delivered, state)
	for gem_name in collected_gems:
		remove_gem.rpc_id(pid, gem_name)
	if crate_delivered:
		$Crate.deliver.rpc_id(pid)
	else:
		$Crate.publish_holders.rpc_id(pid, $Crate.holder_ids)

@rpc("authority", "call_remote", "reliable")
func sync_full_state(t: float, a: float, g: int, d: bool, s: int) -> void:
	time_left = t
	alarm = a
	gems_collected = g
	crate_delivered = d
	state = s
	if s != State.PLAYING:
		result_label.text = "PARTIDA TERMINADA"
		overlay.visible = true
	_update_status()
	_update_hud()

@rpc("authority", "call_local", "reliable")
func spawn_player(pid: int) -> void:
	_spawn_player_local(pid)

func _spawn_player_local(pid: int) -> void:
	if players.has(pid):
		return
	var player := PLAYER_SCENE.instantiate()
	player.name = "P%d" % pid
	player.position = _spawn_point(pid)
	$Players.add_child(player)
	player.game_id = pid
	player.setup_network(pid)
	players[pid] = player

func _spawn_point(pid: int) -> Vector2:
	match pid:
		1:
			return Vector2(640, 600)
		2:
			return Vector2(780, 600)
		3:
			return Vector2(600, 520)
		_:
			return Vector2(820, 520)

func _on_peer_disconnected(pid: int) -> void:
	if not multiplayer.is_server():
		return
	players.erase(pid)
	var crate = $Crate
	if crate.holder_ids.has(pid):
		crate.holder_ids.erase(pid)
		crate.publish_holders.rpc(crate.holder_ids)
	despawn_player.rpc(pid)

@rpc("authority", "call_local", "reliable")
func despawn_player(pid: int) -> void:
	players.erase(pid)
	var node := $Players.get_node_or_null("P%d" % pid)
	if node != null:
		node.queue_free()

func _on_gem_collected(gem: Node) -> void:
	if not _is_server_logic():
		return
	gems_collected += 1
	collected_gems.append(gem.name)
	_update_status()
	_pulse_status()
	if _net_mode() == Mode.HOST:
		remove_gem.rpc(gem.name)
	else:
		_remove_gem_local(gem.name, gem.global_position)
	_check_win()

@rpc("authority", "call_local", "reliable")
func remove_gem(gem_name: String) -> void:
	var gem := $Gems.get_node_or_null(gem_name)
	if gem != null:
		_remove_gem_local(gem_name, gem.global_position)

func _remove_gem_local(gem_name: String, gem_position: Vector2) -> void:
	var gem := $Gems.get_node_or_null(gem_name)
	if gem == null:
		return
	Effects.burst(self, gem_position, Color(0.32, 1.0, 0.72), 14, 1.0)
	Audio.play_sfx("gem", -6.0, randf_range(0.96, 1.05))
	gem.queue_free()

func _on_crate_delivered() -> void:
	if not _is_server_logic():
		return
	if crate_delivered:
		return
	crate_delivered = true
	if _net_mode() == Mode.HOST:
		$Crate.deliver.rpc()
	else:
		$Crate.deliver()
	_update_status()
	_pulse_status()
	_check_win()

func _check_win() -> void:
	if state == State.PLAYING and gems_collected >= TOTAL_GEMS and crate_delivered:
		_end(State.WON, "¡ROBO COMPLETO!")

func _update_status() -> void:
	var crate_state := "extraída" if crate_delivered else "pendiente"
	status_label.text = "Gemas: %d/%d  ·  Caja: %s" % [gems_collected, TOTAL_GEMS, crate_state]

func _end(new_state: State, message: String) -> void:
	if _net_mode() == Mode.HOST:
		apply_end.rpc(new_state, message)
	else:
		apply_end(new_state, message)

@rpc("authority", "call_local", "reliable")
func apply_end(new_state: int, message: String) -> void:
	var was_playing := state == State.PLAYING
	state = new_state
	result_label.text = message
	overlay.visible = true
	_update_hud()
	if was_playing:
		Audio.set_alarm(0.0, false)
		Audio.stop_music()
		Audio.play_sfx("win" if new_state == State.WON else "lose", -5.0)

@rpc("authority", "call_remote", "unreliable")
func sync_state(t: float, a: float, g: int, d: bool, s: int) -> void:
	var changed := g != gems_collected or d != crate_delivered
	time_left = t
	alarm = a
	gems_collected = g
	crate_delivered = d
	state = s
	_update_status()
	if changed and state == State.PLAYING:
		_pulse_status()
	_update_hud()

func _unhandled_input(event: InputEvent) -> void:
	if state == State.PLAYING:
		return
	if event.is_action_pressed("restart"):
		_leave_to_menu()

func _leave_to_menu() -> void:
	if _net_mode() != Mode.LOCAL:
		multiplayer.multiplayer_peer.close()
		multiplayer.multiplayer_peer = null
		get_tree().change_scene_to_file(MENU_SCENE)
	else:
		get_tree().reload_current_scene()
