extends Node

func _ready() -> void:
	var packed = load("res://scenes/fm/level1.tscn")
	if packed == null:
		print("FM_LEVEL1_TEST: FAIL (scene missing)")
		get_tree().quit(1)
		return
	var scene = packed.instantiate()
	add_child(scene)
	while not scene.level_ready:
		await get_tree().physics_frame
	await get_tree().create_timer(0.5).timeout
	await get_tree().physics_frame

	var ok: bool = scene.player != null and scene.loot_items.size() == 5
	print("TEST_PLAYER ", scene.player, " floor=", scene.player.is_on_floor() if scene.player != null else false)
	print("TEST_LOOT ", scene.loot_items.size())

	var room_points := {
		"recepcion": Vector2(-12.0, -6.7),
		"corredor": Vector2(0.0, 0.0),
		"seguridad": Vector2(3.0, -5.7),
		"control": Vector2(13.0, -5.7),
		"vestuarios": Vector2(-14.0, 5.7),
		"almacen": Vector2(-2.0, 5.7),
		"mantenimiento": Vector2(13.0, 5.7),
		"conector": Vector2(5.0, 5.7),
		"oficina": Vector2(-6.2, -6.2),
		"aseo": Vector2(-6.2, -3.3),
	}
	var floor_ok := 0
	for label in room_points.keys():
		var point: Vector2 = room_points[label]
		var hit := _ray(scene, Vector3(point.x, -2.0, point.y), Vector3(point.x, -6.5, point.y))
		var collider_name = hit.get("collider").name if hit.get("collider") else "none"
		if not hit.is_empty():
			floor_ok += 1
		print("TEST_ROOM ", label, " floor=", not hit.is_empty(), " hit=", collider_name)
	print("TEST_ROOMS ", floor_ok, "/", room_points.size())

	var door_checks := [
		["recepcion", Vector3(-12.0, -4.0, -1.0), Vector3(-12.0, -4.0, -3.0)],
		["seguridad", Vector3(3.0, -4.0, -1.0), Vector3(3.0, -4.0, -3.0)],
		["control", Vector3(13.0, -4.0, -1.0), Vector3(13.0, -4.0, -3.0)],
		["vestuarios", Vector3(-14.0, -4.0, 1.0), Vector3(-14.0, -4.0, 3.0)],
		["almacen", Vector3(-2.0, -4.0, 1.0), Vector3(-2.0, -4.0, 3.0)],
		["mantenimiento", Vector3(13.0, -4.0, 1.0), Vector3(13.0, -4.0, 3.0)],
	]
	var doors_ok := 0
	for check in door_checks:
		var hit := _ray(scene, check[1], check[2])
		var collider_name = hit.get("collider").name if hit.get("collider") else "clear"
		var blocked: bool = not hit.is_empty() and "DOOR" in String(collider_name).to_upper()
		if blocked:
			doors_ok += 1
		print("TEST_DOOR_CLOSED ", check[0], " blocked=", blocked, " hit=", collider_name)
	print("TEST_DOORS_CLOSED ", doors_ok, "/", door_checks.size())

	var doors = scene.find_children("Door_*", "Node3D", true, false)
	for door in doors:
		door.set_open(true, true)
	await get_tree().physics_frame
	var doors_open_ok := 0
	for check in door_checks:
		var hit := _ray(scene, check[1], check[2])
		var collider_name = hit.get("collider").name if hit.get("collider") else "clear"
		var clear: bool = hit.is_empty() or not ("DOOR" in String(collider_name).to_upper())
		if clear:
			doors_open_ok += 1
		print("TEST_DOOR_OPEN ", check[0], " clear=", clear, " hit=", collider_name)
	print("TEST_DOORS_OPEN ", doors_open_ok, "/", door_checks.size())

	var drawer_ok := false
	for node in get_tree().get_nodes_in_group("fm_interactable"):
		if not node.has_method("get_interaction_prompt"):
			continue
		if "CAJÓN OFICINA 1" in String(node.get_interaction_prompt()):
			var drawer_target = node.get("target")
			var before_drawer = drawer_target.global_position if drawer_target != null else Vector3.ZERO
			node.interact(scene.player)
			await get_tree().create_timer(0.6).timeout
			drawer_ok = drawer_target != null and before_drawer.distance_to(drawer_target.global_position) > 0.18
			print("TEST_DRAWER ", drawer_ok, " moved=", before_drawer.distance_to(drawer_target.global_position) if drawer_target != null else 0.0)
			break
	var locker_ok := false
	for node in get_tree().get_nodes_in_group("fm_interactable"):
		if not node.has_method("get_interaction_prompt"):
			continue
		if "TAQUILLA" in String(node.get_interaction_prompt()):
			node.interact(scene.player)
			await get_tree().create_timer(0.7).timeout
			locker_ok = abs(float(node.rotation.y)) > 0.6
			print("TEST_LOCKER ", locker_ok, " rot_y=", node.rotation.y)
			break
	var alarm_ok := false
	for node in get_tree().get_nodes_in_group("fm_interactable"):
		if not node.has_method("get_interaction_prompt"):
			continue
		if "ALARMA REMOTA" in String(node.get_interaction_prompt()):
			node.interact(scene.player)
			await get_tree().create_timer(0.25).timeout
			alarm_ok = float(node.cooldown) > 0.0
			print("TEST_ALARM ", alarm_ok, " cooldown=", node.cooldown)
			break
	var east_hit := _ray(scene, Vector3(20.0, -4.0, 0.0), Vector3(24.0, -4.0, 0.0))
	var east_ok: bool = not east_hit.is_empty() and "EastShutter" in String(east_hit.get("collider").name)
	print("TEST_EAST ", east_ok, " hit=", east_hit.get("collider").name if east_hit.get("collider") else "clear")

	var general_lights := 0
	var emergency_lights := 0
	var flashlight_lights := 0
	var art_lights := 0
	for light_node in scene.find_children("*", "Light3D", true, false):
		var light := light_node as Light3D
		if light == null or not light.visible or light.light_energy <= 0.0:
			continue
		var lname := light.name.to_lower()
		var under_watcher := false
		var ancestor := light.get_parent()
		while ancestor != null:
			if ancestor.name == "Watcher":
				under_watcher = true
				break
			ancestor = ancestor.get_parent()
		if under_watcher:
			pass
		elif "emergency" in lname or "emerg" in lname:
			emergency_lights += 1
		elif "art_" in lname:
			art_lights += 1
		elif "flashlight" in lname:
			flashlight_lights += 1
		elif "glow" in lname:
			pass
		elif "extract" in lname or "exitsign" in lname:
			pass
		else:
			general_lights += 1
			print("TEST_GENERAL_LIGHT ", light.name)
	var lights_ok: bool = general_lights == 0 and art_lights >= 8 and emergency_lights >= 8 and flashlight_lights >= 1
	print("TEST_LIGHTS ", lights_ok, " general=", general_lights, " art=", art_lights, " emergency=", emergency_lights, " flashlight=", flashlight_lights)

	var watcher_ok: bool = scene.watcher != null and scene.watcher.patrol_points.size() >= 4
	print("TEST_WATCHER ", watcher_ok, " patrol=", scene.watcher.patrol_points.size() if scene.watcher != null else 0)
	scene.emit_noise(Vector3(14.0, -5.65, 0.0), 4.0, "test")
	await get_tree().create_timer(0.2).timeout
	var noise_ok: bool = scene.watcher != null and scene.watcher.state == 2
	print("TEST_NOISE ", noise_ok, " state=", scene.watcher.state if scene.watcher != null else -1)

	var player = scene.player
	if player != null:
		player.global_position = Vector3(-12.0, -5.6, -4.0)
		await get_tree().physics_frame
		var before: Vector3 = player.global_position
		Input.action_press("move_up")
		await get_tree().create_timer(0.5).timeout
		Input.action_release("move_up")
		await get_tree().physics_frame
		var moved: bool = before.distance_to(player.global_position) > 0.1
		print("TEST_MOVE ", moved, " from=", before, " to=", player.global_position)
		ok = ok and moved

	var case_item = null
	for item in scene.loot_items:
		if item.loot_id == "case":
			case_item = item
			break
	if player != null and case_item != null:
		player.global_position = case_item.global_position + Vector3(0.0, 1.4, 0.0)
		await get_tree().physics_frame
		var picked: bool = case_item.pickup(player)
		if picked:
			player.carried_item = case_item
		case_item.drop(Vector3.ZERO)
		await get_tree().physics_frame
		player.carried_item = null
		case_item.global_position = Vector3(-17.5, -5.6, -10.7)
		player.global_position = Vector3(-17.5, -5.6, -10.7)
		scene.extraction.activation_time_s = 0.1
		scene.extraction.sequence_duration_s = 0.3
		await get_tree().create_timer(2.0).timeout
		var extraction_ok: bool = picked and scene.state == 1
		print("TEST_EXTRACTION ", extraction_ok, " state=", scene.state, " delivered=", scene.get_delivered_loot_count(Vector3(-17.5, -5.65, -10.7), 2.4))
		ok = ok and extraction_ok

	ok = ok and floor_ok == room_points.size() and doors_ok == door_checks.size() and doors_open_ok == door_checks.size() and drawer_ok and locker_ok and alarm_ok and east_ok and lights_ok and watcher_ok and noise_ok
	print("FM_LEVEL1_TEST: %s" % ("PASS" if ok else "FAIL"))
	get_tree().quit(0 if ok else 1)

func _ray(scene: Node, from: Vector3, to: Vector3) -> Dictionary:
	var query := PhysicsRayQueryParameters3D.create(from, to)
	query.collision_mask = 1
	return scene.get_world_3d().direct_space_state.intersect_ray(query)
