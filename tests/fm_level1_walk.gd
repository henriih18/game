extends Node

## Recorrido continuo del Nivel 1 sin teletransportes.
## Abre las puertas y camina con el controlador real entre waypoints.

const ROUTE := [
	Vector3(-12.0, -5.6, -2.5),
	Vector3(-12.0, -5.6, -0.4),
	Vector3(3.0, -5.6, -0.4),
	Vector3(3.0, -5.6, -2.6),
	Vector3(3.0, -5.6, -4.4),
	Vector3(3.0, -5.6, -0.4),
	Vector3(8.0, -5.6, 0.8),
	Vector3(13.45, -5.6, 0.8),
	Vector3(13.45, -5.6, -0.4),
	Vector3(13.45, -5.6, -2.6),
	Vector3(13.45, -5.6, -4.2),
	Vector3(13.45, -5.6, -0.4),
	Vector3(13.45, -5.6, 0.8),
	Vector3(8.0, -5.6, 0.8),
	Vector3(-14.0, -5.6, 0.4),
	Vector3(-14.0, -5.6, 2.6),
	Vector3(-14.0, -5.6, 5.0),
	Vector3(-14.0, -5.6, 0.4),
	Vector3(-2.0, -5.6, 0.4),
	Vector3(-2.0, -5.6, 2.6),
	Vector3(-2.0, -5.6, 5.0),
	Vector3(-2.0, -5.6, 0.4),
	Vector3(13.0, -5.6, 0.4),
	Vector3(13.0, -5.6, 2.6),
	Vector3(13.0, -5.6, 4.2),
	Vector3(13.0, -5.6, 0.4),
	Vector3(-12.0, -5.6, 0.4),
	Vector3(-12.0, -5.6, -2.6),
	Vector3(-12.0, -5.6, -5.0),
	Vector3(-12.0, -5.6, -6.25),
	Vector3(-9.25, -5.6, -6.25),
	Vector3(-7.0, -5.6, -6.25),
	Vector3(-9.25, -5.6, -6.25),
	Vector3(-12.0, -5.6, -6.25),
	Vector3(-12.0, -5.6, -3.05),
	Vector3(-9.25, -5.6, -3.05),
	Vector3(-7.0, -5.6, -3.05),
	Vector3(-9.25, -5.6, -3.05),
	Vector3(-12.0, -5.6, -3.05),
	Vector3(-15.0, -5.6, -3.05),
	Vector3(-15.5, -5.6, -5.3),
	Vector3(-15.5, -5.6, -8.5),
	Vector3(-17.5, -5.6, -8.5),
	Vector3(-17.5, -5.6, -10.7),
]

func _ready() -> void:
	var packed := load("res://scenes/fm/level1.tscn")
	if packed == null:
		print("LEVEL1_WALK: FAIL scene missing")
		get_tree().quit(1)
		return
	var scene = packed.instantiate()
	add_child(scene)
	while not scene.level_ready:
		await get_tree().physics_frame
	await get_tree().create_timer(0.5).timeout
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var player = scene.player
	if player == null:
		print("LEVEL1_WALK: FAIL player missing")
		get_tree().quit(1)
		return
	for door in scene.find_children("Door_*", "Node3D", true, false):
		door.set_open(true, true)
	if scene.watcher != null:
		scene.watcher.queue_free()
	await get_tree().physics_frame
	var reached := 0
	for i in range(ROUTE.size()):
		var ok := await _walk_to(player, ROUTE[i], 9.0)
		if ok:
			reached += 1
		print("WALK_STEP %02d %s pos=%s" % [i, "OK" if ok else "STUCK", player.global_position])
		if not ok:
			break
	Input.action_release("move_up")
	print("WALK_RESULT reached=%d/%d final=%s" % [reached, ROUTE.size(), player.global_position])
	get_tree().quit(0 if reached == ROUTE.size() else 1)

func _walk_to(player, target: Vector3, max_seconds: float) -> bool:
	var deadline := Time.get_ticks_msec() + int(max_seconds * 1000.0)
	while Time.get_ticks_msec() < deadline:
		var to: Vector3 = target - player.global_position
		to.y = 0.0
		if to.length() <= 0.85:
			Input.action_release("move_up")
			return true
		player.rotation.y = atan2(-to.x, -to.z)
		Input.action_press("move_up")
		await get_tree().physics_frame
	Input.action_release("move_up")
	var shape := SphereShape3D.new()
	shape.radius = 0.55
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = shape
	query.transform = Transform3D(Basis(), player.global_position)
	query.collision_mask = 1
	var hits: Array = player.get_world_3d().direct_space_state.intersect_shape(query, 12)
	for hit in hits:
		var collider = hit.get("collider")
		if collider != null:
			print("WALK_HIT ", collider.name)
	return false
