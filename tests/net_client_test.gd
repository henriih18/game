extends SceneTree

var failures := 0
var scene: Node

func _init() -> void:
	_run.call_deferred()

func check(condition: bool, label: String) -> void:
	if condition:
		print("PASS: ", label)
	else:
		failures += 1
		print("FAIL: ", label)

func _run() -> void:
	var mp := root.multiplayer
	var peer := ENetMultiplayerPeer.new()
	var err := peer.create_client("127.0.0.1", 7777)
	if err != OK:
		check(false, "crear cliente ENet")
		quit(1)
		return
	mp.multiplayer_peer = peer
	await mp.connected_to_server
	check(true, "conexión al host")

	scene = load("res://scenes/main.tscn").instantiate()
	root.add_child(scene)

	var my_id: int = mp.get_unique_id()
	var spawned := false
	for i in 90:
		await process_frame
		if scene.players.has(my_id):
			spawned = true
			break
	check(spawned, "el servidor spawnea mi jugador")
	if not spawned:
		quit(1)
		return

	var p = scene.players[my_id]
	var crate = scene.get_node("Crate")
	check(scene.players.size() == 2, "hay 2 jugadores en la partida")

	p.global_position = crate.global_position + Vector2(60, 0)
	for i in 20:
		await process_frame
	p._toggle_grab()
	for i in 40:
		await process_frame
	check(crate.holder_ids.has(my_id), "el servidor acepta el agarre")

	p.global_position += Vector2(90, -50)
	for i in 40:
		await process_frame
	var expected: Vector2 = p.global_position + Vector2(0, -46)
	check(crate.global_position.distance_to(expected) < 25.0, "la caja sigue al portador en red")

	var timer_before: float = scene.time_left
	for i in 60:
		await process_frame
	check(scene.time_left < timer_before, "el estado de ronda se sincroniza")

	print("RESULT: ", "OK" if failures == 0 else "%d FALLOS" % failures)
	quit(0 if failures == 0 else 1)
