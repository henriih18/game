extends "res://scripts/fm/vertical_slice.gd"

## Prueba de integración de red 3D como cliente real.
## La raíz se llama VerticalSlice para que los NodePath de los RPC coincidan
## con los del host (que carga la misma escena desde el menú).
## Se ejecuta contra: godot --headless --path . -- --host3d --nettest

const PROBE_PORT := 7777

var _probe_connected := false
var _probe_failed := false
var _probe_checks := 0
var _probe_fails := 0

func _ready() -> void:
	var peer := ENetMultiplayerPeer.new()
	var err := peer.create_client("127.0.0.1", PROBE_PORT)
	if err != OK:
		_probe_check(false, "el cliente puede iniciar ENet (error %d)" % err)
		_probe_finish()
		return
	multiplayer.multiplayer_peer = peer
	multiplayer.connected_to_server.connect(func() -> void: _probe_connected = true)
	multiplayer.connection_failed.connect(func() -> void: _probe_failed = true)
	multiplayer.server_disconnected.connect(func() -> void: _probe_failed = true)

	var deadline := 6.0
	while not _probe_connected and not _probe_failed and deadline > 0.0:
		await get_tree().create_timer(0.1).timeout
		deadline -= 0.1
	_probe_check(_probe_connected, "el cliente se conecta al host 3D")
	if not _probe_connected:
		_probe_finish()
		return

	# La escena base detecta el peer ENet y construye el modo cliente.
	super._ready()
	await get_tree().create_timer(1.6).timeout

	_probe_check(player != null, "el cliente tiene jugador local")
	_probe_check(players.size() >= 2, "el cliente ve al host y a su jugador")
	_probe_check(players.has(local_id), "el roster contiene al jugador local")
	_probe_check(players.has(1), "el roster contiene al host")
	_probe_check(net != null and net_mode == NetMode.CLIENT, "la escena detecta el modo cliente")
	var host_avatar: Node3D = players.get(1)
	_probe_check(host_avatar != null and player.global_position.distance_to(host_avatar.global_position) > 1.5, "los dos jugadores no se superponen al spawnear")

	# Batería del corredor: el host valida y replica la recarga.
	player.battery = 20.0
	player.global_position = Vector3(2.15, 0.1, -3.0)
	await get_tree().create_timer(0.35).timeout
	request_network_interaction()
	await get_tree().create_timer(0.9).timeout
	_probe_check(battery_taken.size() > 1 and battery_taken[1], "el host replica la batería recogida")
	_probe_check(player.battery > 20.0, "el cliente recibe la recarga de batería")

	# Puerta: el cliente pide, el host abre y replica.
	_probe_check(not security_door.is_open, "la puerta empieza cerrada en el cliente")
	player.global_position = Vector3(0.0, 0.1, -8.7)
	await get_tree().create_timer(0.35).timeout
	request_network_interaction()
	await get_tree().create_timer(1.0).timeout
	_probe_check(security_door.is_open, "el host abre y sincroniza la puerta")

	# Núcleo: el host valida la distancia y lo asigna al cliente.
	player.global_position = Vector3(-5.2, 0.1, 4.1)
	await get_tree().create_timer(0.4).timeout
	request_network_interaction()
	await get_tree().create_timer(1.0).timeout
	_probe_check(artifact.carried_by != null, "el host acepta recoger el núcleo")
	_probe_check(player.carried_item == artifact, "el núcleo aparece en manos del cliente")

	# Extracción: el host detecta al portador y termina la ronda para ambos.
	player.global_position = Vector3(0.0, 0.1, -12.0)
	await get_tree().create_timer(1.2).timeout
	_probe_check(state == State.WON, "la extracción termina la partida en victoria")
	_probe_check(hud != null, "el HUD del cliente existe al terminar")

	_probe_finish()

func _probe_check(ok: bool, label: String) -> void:
	_probe_checks += 1
	if ok:
		print("PASS  %s" % label)
	else:
		_probe_fails += 1
		print("FAIL  %s" % label)

func _probe_finish() -> void:
	print("FM_NET_3D_TEST: %d PASS / %d FAIL" % [_probe_checks - _probe_fails, _probe_fails])
	get_tree().quit(1 if _probe_fails > 0 else 0)
