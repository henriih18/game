class_name FMNet
extends Node

## Capa de red del vertical slice 3D.
## Reutiliza ENet y el patrón host-autoritativo del prototipo 2D.
## El host es autoridad sobre objetos, puerta, trampa, El Vigilante y fin de ronda.
## El movimiento de cada jugador se replica desde su instancia para mantener respuesta,
## pero el host valida distancias antes de aceptar interacciones.

enum Mode { OFFLINE, HOST, CLIENT }

const STATE_INTERVAL := 0.05
const WORLD_INTERVAL := 0.1

var game: Node = null
var mode: Mode = Mode.OFFLINE
var local_id := 1

var _state_timer := 0.0
var _world_timer := 0.0
var _registered := false
var _retry_timer := 0.0
var _register_attempts := 0
var _ready_peers: Dictionary = {}

func setup(target: Node) -> void:
	game = target
	mode = _detect_mode()
	local_id = 1 if mode == Mode.HOST else (maxi(2, multiplayer.get_unique_id()) if mode == Mode.CLIENT else 1)

	if mode == Mode.HOST:
		multiplayer.peer_connected.connect(_on_peer_connected)
		multiplayer.peer_disconnected.connect(_on_peer_disconnected)
	elif mode == Mode.CLIENT:
		multiplayer.server_disconnected.connect(_on_server_disconnected)
		_register_client.call_deferred()

func _detect_mode() -> Mode:
	var peer := multiplayer.multiplayer_peer
	if peer is ENetMultiplayerPeer:
		return Mode.HOST if multiplayer.is_server() else Mode.CLIENT
	return Mode.OFFLINE

func _process(delta: float) -> void:
	if mode == Mode.OFFLINE or game == null or not is_instance_valid(game):
		return
	if game.state != 0:
		return

	if mode == Mode.CLIENT and not _registered:
		_retry_timer -= delta
		if _retry_timer <= 0.0:
			_retry_timer = 0.5
			_register_client()

	_state_timer -= delta
	if _state_timer <= 0.0:
		_state_timer = STATE_INTERVAL
		_send_local_state()

	if mode == Mode.HOST:
		_world_timer -= delta
		if _world_timer <= 0.0:
			_world_timer = WORLD_INTERVAL
			_broadcast_world()

func _register_client() -> void:
	if mode != Mode.CLIENT or _registered:
		return
	if not multiplayer.has_multiplayer_peer():
		return
	if multiplayer.multiplayer_peer.get_connection_status() != MultiplayerPeer.CONNECTION_CONNECTED:
		return
	_register_attempts += 1
	client_ready.rpc_id(1)
	if _register_attempts >= 30:
		_registered = true

func _send_local_state() -> void:
	if game.player == null or not is_instance_valid(game.player):
		return
	var p: Node3D = game.player
	var hidden: bool = game.player.hidden
	var observing := false
	if game.watcher != null and is_instance_valid(game.watcher):
		observing = game.player.is_observing(game.watcher)
	var carrying := game.player.carried_item != null

	if mode == Mode.HOST:
		_send_remote_state(1, p.global_position, p.rotation.y, hidden, observing, carrying)
	elif _registered:
		player_state.rpc_id(1, local_id, p.global_position, p.rotation.y, hidden, observing, carrying)

func _broadcast_world() -> void:
	if game.state != 0 or _ready_peers.is_empty():
		return
	var args := _world_args()
	for pid in _ready_peers.keys():
		world_state.rpc_id(int(pid), args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7])

func _send_remote_state(pid: int, pos: Vector3, yaw: float, hidden: bool, observing: bool, carrying: bool) -> void:
	for peer_id in _ready_peers.keys():
		if int(peer_id) != pid:
			remote_state.rpc_id(int(peer_id), pid, pos, yaw, hidden, observing, carrying)

func _send_world_to(pid: int) -> void:
	var args := _world_args()
	sync_world.rpc_id(pid, args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7])

func _world_args() -> Array:
	var door_open: bool = game.security_door != null and is_instance_valid(game.security_door) and game.security_door.is_open
	var batteries: Array = game.get_battery_taken_flags()
	var trap_triggered: bool = game.noise_trap != null and is_instance_valid(game.noise_trap) and game.noise_trap.triggered
	var carrier_id := 0
	if game.artifact != null and is_instance_valid(game.artifact) and game.artifact.carried_by != null:
		if game.artifact.carried_by == game.player:
			carrier_id = local_id
		else:
			carrier_id = int(game.artifact.carried_by.get("net_id"))
	var artifact_pos: Vector3 = game.artifact.global_position if game.artifact != null and is_instance_valid(game.artifact) else Vector3.ZERO
	var watcher_pos := Vector3.ZERO
	var watcher_yaw := 0.0
	var watcher_state := 0
	if game.watcher != null and is_instance_valid(game.watcher):
		watcher_pos = game.watcher.global_position
		watcher_yaw = game.watcher.rotation.y
		watcher_state = int(game.watcher.state)
	return [door_open, batteries, trap_triggered, carrier_id, artifact_pos, watcher_pos, watcher_yaw, watcher_state]

@rpc("any_peer", "call_remote", "reliable")
func client_ready() -> void:
	if mode != Mode.HOST:
		return
	var pid := multiplayer.get_remote_sender_id()
	if pid <= 1:
		return
	if game.players.has(pid):
		_ready_peers[pid] = true
		return
	_ready_peers[pid] = true
	for id in game.players.keys():
		var existing: Node3D = game.players[id]
		register_player.rpc_id(pid, int(id), existing.global_position, existing.rotation.y)
	register_player.rpc(pid, game.spawn_point_for(pid), 0.0)
	_send_world_to(pid)

@rpc("authority", "call_local", "reliable")
func register_player(pid: int, spawn_position: Vector3, yaw: float) -> void:
	if pid == local_id:
		game.place_local_player(spawn_position, yaw)
		_registered = true
		return
	game.spawn_remote(pid, spawn_position, yaw)

@rpc("any_peer", "call_remote", "unreliable_ordered")
func player_state(pid: int, pos: Vector3, yaw: float, hidden: bool, observing: bool, carrying: bool) -> void:
	if mode != Mode.HOST:
		return
	var sender := multiplayer.get_remote_sender_id()
	if sender <= 1:
		return
	if pid != sender:
		return
	var remote = game.players.get(pid)
	if remote == null or not is_instance_valid(remote):
		return
	var safe := _sanitize_position(pos)
	remote.set_network_state(safe, yaw, hidden, observing)
	remote.set_carrying(carrying)
	_send_remote_state(pid, safe, yaw, hidden, observing, carrying)

@rpc("authority", "call_remote", "unreliable_ordered")
func remote_state(pid: int, pos: Vector3, yaw: float, hidden: bool, observing: bool, carrying: bool) -> void:
	if pid == local_id:
		return
	var remote = game.players.get(pid)
	if remote == null or not is_instance_valid(remote):
		return
	remote.set_network_state(pos, yaw, hidden, observing)
	remote.set_carrying(carrying)

@rpc("any_peer", "call_remote", "unreliable_ordered")
func send_noise(position: Vector3, radius: float) -> void:
	if mode != Mode.HOST:
		return
	var sender := multiplayer.get_remote_sender_id()
	if sender <= 1:
		return
	if not game.players.has(sender):
		return
	game.receive_remote_noise(position, clampf(radius, 0.0, 18.0))

@rpc("any_peer", "call_remote", "reliable")
func request_interact() -> void:
	if mode != Mode.HOST:
		return
	var pid := multiplayer.get_remote_sender_id()
	if pid <= 1:
		return
	game.resolve_remote_interaction(pid)

@rpc("any_peer", "call_remote", "reliable")
func request_drop() -> void:
	if mode != Mode.HOST:
		return
	var pid := multiplayer.get_remote_sender_id()
	if pid <= 1:
		return
	game.resolve_remote_drop(pid)

@rpc("any_peer", "call_remote", "reliable")
func request_trap() -> void:
	if mode != Mode.HOST:
		return
	var pid := multiplayer.get_remote_sender_id()
	if pid <= 1:
		return
	var remote = game.players.get(pid)
	if remote == null or not is_instance_valid(remote):
		return
	if game.noise_trap == null or not is_instance_valid(game.noise_trap):
		return
	if game.noise_trap.global_position.distance_to(remote.global_position) > 3.0:
		return
	game.noise_trap.trigger(true)

@rpc("authority", "call_remote", "reliable")
func door_open() -> void:
	game.apply_network_door(true)

@rpc("authority", "call_local", "reliable")
func battery_picked(index: int, pid: int) -> void:
	game.apply_network_battery(index, pid)

@rpc("authority", "call_local", "reliable")
func trap_triggered() -> void:
	game.apply_network_trap()

@rpc("authority", "call_local", "reliable")
func artifact_carrier(carrier_id: int, position: Vector3) -> void:
	game.apply_network_carrier(carrier_id, position)

@rpc("authority", "call_local", "reliable")
func hide_set(pid: int, spot_index: int, hidden: bool) -> void:
	game.apply_network_hide(pid, spot_index, hidden)

@rpc("authority", "call_remote", "reliable")
func end_game(result: int, title: String, subtitle: String) -> void:
	game.apply_network_end(result, title, subtitle)

@rpc("authority", "call_local", "reliable")
func player_left(pid: int) -> void:
	game.remove_remote(pid)

@rpc("authority", "call_remote", "unreliable_ordered")
func world_state(door_open_flag: bool, batteries: Array, trap: bool, carrier_id: int, artifact_pos: Vector3, watcher_pos: Vector3, watcher_yaw: float, watcher_state: int) -> void:
	_apply_world(door_open_flag, batteries, trap, carrier_id, artifact_pos, watcher_pos, watcher_yaw, watcher_state)

@rpc("authority", "call_remote", "reliable")
func sync_world(door_open_flag: bool, batteries: Array, trap: bool, carrier_id: int, artifact_pos: Vector3, watcher_pos: Vector3, watcher_yaw: float, watcher_state: int) -> void:
	_apply_world(door_open_flag, batteries, trap, carrier_id, artifact_pos, watcher_pos, watcher_yaw, watcher_state)

func _apply_world(door_open_flag: bool, batteries: Array, trap: bool, carrier_id: int, artifact_pos: Vector3, watcher_pos: Vector3, watcher_yaw: float, watcher_state: int) -> void:
	game.apply_network_door(door_open_flag)
	game.apply_network_batteries(batteries)
	game.apply_network_trap_state(trap)
	game.apply_network_carrier(carrier_id, artifact_pos)
	game.apply_network_watcher(watcher_pos, watcher_yaw, watcher_state)

func broadcast_end(result: int, title: String, subtitle: String) -> void:
	if mode == Mode.HOST:
		end_game.rpc(result, title, subtitle)

func broadcast_trap() -> void:
	if mode == Mode.HOST:
		trap_triggered.rpc()

func broadcast_carrier(carrier_id: int, position: Vector3) -> void:
	if mode == Mode.HOST:
		artifact_carrier.rpc(carrier_id, position)

func broadcast_door() -> void:
	if mode == Mode.HOST:
		door_open.rpc()

func broadcast_battery(index: int, pid: int) -> void:
	if mode == Mode.HOST:
		battery_picked.rpc(index, pid)

func broadcast_hide(pid: int, spot_index: int, hidden: bool) -> void:
	if mode == Mode.HOST:
		hide_set.rpc(pid, spot_index, hidden)

func _sanitize_position(pos: Vector3) -> Vector3:
	return Vector3(clampf(pos.x, -9.2, 2.45), clampf(pos.y, -1.0, 3.0), clampf(pos.z, -13.4, 11.4))

func _on_peer_connected(_pid: int) -> void:
	pass

func _on_peer_disconnected(pid: int) -> void:
	if mode != Mode.HOST:
		return
	_ready_peers.erase(pid)
	game.drop_carrier_if(pid)
	player_left.rpc(pid)

func _on_server_disconnected() -> void:
	if mode == Mode.CLIENT:
		game.on_server_disconnected()
