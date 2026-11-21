extends Node

func _ready() -> void:
	var packed = load("res://scenes/fm/reception_slice.tscn")
	if packed == null:
		print("FM_RECEPTION_TEST: FAIL (scene missing)")
		get_tree().quit(1)
		return

	var scene = packed.instantiate()
	add_child(scene)
	await get_tree().process_frame
	await get_tree().physics_frame

	var ok: bool = scene.player != null and scene.loot_items.size() == 5
	print("TEST_PLAYER ", scene.player, " floor=", scene.player.is_on_floor() if scene.player != null else false)

	var case_item = null
	var crate_item = null
	for item in scene.loot_items:
		if item.loot_id == "case":
			case_item = item
		elif item.loot_id == "crate":
			crate_item = item

	var player = scene.player
	if player == null or case_item == null or crate_item == null:
		print("FM_RECEPTION_TEST: FAIL (missing player/loot)")
		get_tree().quit(1)
		return

	var east_hit := _ray(scene, Vector3(-12.0, -4.0, -2.5), Vector3(-3.0, -4.0, -2.5))
	var south_hit := _ray(scene, Vector3(-12.0, -4.0, -4.0), Vector3(-12.0, -4.0, 0.0))
	var north_hit := _ray(scene, Vector3(-9.0, -4.0, -6.0), Vector3(-9.0, -4.0, -12.5))
	var office_hit := _ray(scene, Vector3(-10.0, -4.0, -6.0), Vector3(-4.0, -4.0, -6.0))
	var elevator_hit := _ray(scene, Vector3(-17.5, -4.3, -9.5), Vector3(-17.5, -4.3, -12.5))
	var walls_ok: bool = not east_hit.is_empty() and not south_hit.is_empty() and not north_hit.is_empty() and not office_hit.is_empty() and not elevator_hit.is_empty()
	print("TEST_WALLS ", walls_ok, " east=", east_hit.get("collider").name if east_hit.get("collider") else "none", " south=", south_hit.get("collider").name if south_hit.get("collider") else "none", " north=", north_hit.get("collider").name if north_hit.get("collider") else "none", " office=", office_hit.get("collider").name if office_hit.get("collider") else "none", " elev=", elevator_hit.get("collider").name if elevator_hit.get("collider") else "none")
	var bin_hit := _ray(scene, Vector3(-9.1, -5.40, -5.0), Vector3(-9.1, -5.40, -3.0))
	var planter_hit := _ray(scene, Vector3(-8.0, -5.0, -9.8), Vector3(-8.0, -5.0, -11.2))
	var props_ok: bool = not bin_hit.is_empty() and not planter_hit.is_empty()
	print("TEST_PROPS ", props_ok, " bin=", bin_hit.get("collider").name if bin_hit.get("collider") else "none", " planter=", planter_hit.get("collider").name if planter_hit.get("collider") else "none")
	var general_lights := 0
	var emergency_lights := 0
	var flashlight_lights := 0
	for light_node in scene.find_children("*", "Light3D", true, false):
		var light := light_node as Light3D
		if light == null or not light.visible or light.light_energy <= 0.0:
			continue
		var lname := light.name.to_lower()
		if "emergency" in lname or "emerg" in lname:
			emergency_lights += 1
		elif "flashlight" in lname:
			flashlight_lights += 1
		elif "extract" in lname or "exitsign" in lname:
			pass
		else:
			general_lights += 1
	var lights_ok: bool = general_lights == 0 and emergency_lights >= 4 and flashlight_lights >= 1
	print("TEST_LIGHTS ", lights_ok, " general=", general_lights, " emergency=", emergency_lights, " flashlight=", flashlight_lights)
	var can_debris = scene.get_node_or_null("Can_West")
	await get_tree().create_timer(1.0).timeout
	var debris_ok: bool = can_debris != null and can_debris.global_position.y > -6.0
	print("TEST_DEBRIS ", debris_ok, " y=", can_debris.global_position.y if can_debris != null else 0.0)

	player.global_position = Vector3(-12.0, -5.6, -4.0)
	await get_tree().physics_frame
	var move_start: Vector3 = player.global_position
	Input.action_press("move_up")
	await get_tree().create_timer(0.5).timeout
	Input.action_release("move_up")
	await get_tree().physics_frame
	var moved: bool = move_start.distance_to(player.global_position) > 0.1
	print("TEST_MOVE ", moved, " from=", move_start, " to=", player.global_position)

	player.global_position = Vector3(-15.4, -5.6, -2.7)
	await get_tree().physics_frame
	scene.hiding_spot.hide_player(player)
	await get_tree().process_frame
	var hidden_ok: bool = player.hidden
	player.exit_hide()
	await get_tree().process_frame
	hidden_ok = hidden_ok and not player.hidden
	print("TEST_HIDE ", hidden_ok)

	scene.noise_trap.trigger()
	await get_tree().process_frame
	var trap_ok: bool = scene.noise_trap.triggered
	print("TEST_TRAP ", trap_ok)

	player.global_position = Vector3(-13.2, -5.6, -6.7)
	await get_tree().physics_frame
	var crate_rejected: bool = not crate_item.pickup(player)
	print("TEST_CRATE_REJECT ", crate_rejected)

	var picked: bool = case_item.pickup(player)
	if picked:
		player.carried_item = case_item
	print("TEST_PICKUP ", picked, " carried=", player.carried_item)

	case_item.drop(Vector3.ZERO)
	await get_tree().physics_frame
	var dropped_ok: bool = case_item.carried_by == null
	player.carried_item = null
	var picked_again: bool = case_item.pickup(player)
	if picked_again:
		player.carried_item = case_item
	print("TEST_DROP ", dropped_ok, " REPICK ", picked_again)

	var left_door = scene.get("_door_l")
	var door_closed = scene.get("_door_l_closed")
	scene.on_extraction_progress("cierre", 1.0)
	await get_tree().create_timer(1.7).timeout
	var close_ok: bool = left_door != null and door_closed != null and abs(float(left_door.global_position.x) - float(door_closed)) < 0.05
	print("TEST_DOORS_CLOSE ", close_ok, " left_x=", left_door.global_position.x if left_door != null else 0.0)
	scene.on_extraction_progress("apertura", 1.0)
	scene.animate_elevator_doors(true)
	await get_tree().create_timer(1.7).timeout
	var reopen_ok: bool = left_door != null and door_closed != null and abs(float(left_door.global_position.x) - (float(door_closed) - 1.0)) < 0.05
	print("TEST_DOORS_REOPEN ", reopen_ok, " left_x=", left_door.global_position.x if left_door != null else 0.0)

	player.global_position = Vector3(-17.5, -5.6, -10.7)
	case_item.global_position = Vector3(-17.5, -5.62, -10.7)
	scene.extraction.activation_time_s = 0.1
	scene.extraction.sequence_duration_s = 0.2
	await get_tree().create_timer(3.0).timeout

	print("TEST_STATE ", scene.state, " players_inside=", scene.extraction.players_inside.size())
	for ap in scene.find_children("*", "AnimationPlayer", true, false):
		print("TEST_AP ", ap.name, " playing=", ap.is_playing(), " anim=", ap.current_animation, " autoplay=", ap.autoplay, " active=", ap.active)
	var door_ok: bool = left_door != null and door_closed != null and abs(float(left_door.global_position.x) - (float(door_closed) - 1.0)) < 0.25
	print("TEST_DOORS_OPEN ", door_ok, " left_x=", left_door.global_position.x if left_door != null else 0.0, " closed_x=", door_closed)
	ok = ok and walls_ok and props_ok and lights_ok and debris_ok and moved and hidden_ok and trap_ok and crate_rejected and picked and dropped_ok and picked_again and close_ok and reopen_ok and door_ok and scene.state == 1
	print("FM_RECEPTION_TEST: %s" % ("PASS" if ok else "FAIL"))
	get_tree().quit(0 if ok else 1)

func _ray(scene: Node, from: Vector3, to: Vector3) -> Dictionary:
	var query := PhysicsRayQueryParameters3D.create(from, to)
	query.collision_mask = 1
	return scene.get_world_3d().direct_space_state.intersect_ray(query)
