extends Node

## Prueba headless del traversal de FMPlayer para el Nivel 1 V06:
## capsula agachado/erguido, tuneles de 1,23 m, escalon de 0,1875 m y
## techos bajos que impiden levantarse.
## godot --headless --path . tests/fm_traversal_smoke.tscn

const PLAYER_SCENE := preload("res://scenes/fm/fm_player.tscn")
const FLOOR_Y := 0.0
const TUNNEL_HEIGHT := 1.23
const STEP_RISE := 0.1875
const LOW_CEILING := 1.30

var state := 0

var player: FMPlayer
var passes := 0
var fails := 0


func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	_build_test_world()
	player = PLAYER_SCENE.instantiate() as FMPlayer
	player.name = "Player"
	player.position = Vector3(0.4, FLOOR_Y + 0.05, 0.0)
	player.rotation.y = -PI * 0.5
	add_child(player)
	player.set_game(self)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	await _wait(0.6)

	var shape_node := player.get_node_or_null("CollisionShape3D") as CollisionShape3D
	var capsule := shape_node.shape as CapsuleShape3D if shape_node != null else null
	_check("capsule_present", capsule != null)
	if capsule == null:
		_finish()
		return

	print("TRAVERSAL_STAND height=%.3f offset=%.3f pos=%s floor=%s" % [
		capsule.height, shape_node.position.y, str(player.global_position), str(player.is_on_floor())
	])
	_check("stand_height", is_equal_approx(capsule.height, player.stand_height))
	_check("stand_offset", is_equal_approx(shape_node.position.y, player.stand_height * 0.5))
	_check("spawn_on_floor", player.is_on_floor())

	# Capsula agachado: pies en el suelo y camara baja.
	Input.action_press("crouch")
	await _wait(0.3)
	print("TRAVERSAL_CROUCH height=%.3f offset=%.3f y=%.3f floor=%s" % [
		capsule.height, shape_node.position.y, player.global_position.y, str(player.is_on_floor())
	])
	_check("crouch_height", is_equal_approx(capsule.height, player.crouch_height))
	_check("crouch_offset", is_equal_approx(shape_node.position.y, player.crouch_height * 0.5))
	_check("crouch_feet_on_floor", absf(player.global_position.y - FLOOR_Y) < 0.04 and player.is_on_floor())
	Input.action_release("crouch")
	await _wait(0.3)
	_check("stand_restored", is_equal_approx(capsule.height, player.stand_height))

	# Tunel de 1,23 m: entrar agachado, no poder levantarse dentro y salir.
	await _reset_player(Vector3(0.4, FLOOR_Y + 0.05, 0.0), -PI * 0.5)
	Input.action_press("crouch")
	await _wait(0.3)
	await _hold_axis("x", 3.9, 4.0)
	var tunnel_mid: Vector3 = player.global_position
	_check("tunnel_entered", tunnel_mid.x > 2.2 and absf(tunnel_mid.z) < 0.45)
	Input.action_release("crouch")
	await _wait(0.5)
	print("TRAVERSAL_TUNNEL_MID pos=%s height=%.3f" % [str(player.global_position), capsule.height])
	_check("tunnel_blocks_stand", is_equal_approx(capsule.height, player.crouch_height))
	Input.action_press("crouch")
	await _wait(0.15)
	await _hold_axis("x", 6.6, 4.0)
	var tunnel_end: Vector3 = player.global_position
	Input.action_release("crouch")
	await _wait(0.45)
	print("TRAVERSAL_TUNNEL_END pos=%s height=%.3f floor=%s" % [
		str(tunnel_end), capsule.height, str(player.is_on_floor())
	])
	_check("tunnel_exited", tunnel_end.x > 6.4)
	_check("tunnel_exit_grounded", absf(tunnel_end.y - FLOOR_Y) < 0.05 and player.is_on_floor())
	_check("tunnel_exit_stands", is_equal_approx(capsule.height, player.stand_height))

	# Escalon de 0,1875 m: subir sin salto ni teletransporte.
	await _reset_player(Vector3(7.1, FLOOR_Y + 0.05, 0.0), -PI * 0.5)
	await _wait(0.35)
	var step_before: Vector3 = player.global_position
	await _hold_axis("x", 9.2, 3.0)
	var step_after: Vector3 = player.global_position
	print("TRAVERSAL_STEP from=%s to=%s floor=%s" % [str(step_before), str(step_after), str(player.is_on_floor())])
	_check("step_advanced", step_after.x > 9.0)
	_check("step_height_reached", absf(step_after.y - STEP_RISE) < 0.035)
	_check("step_grounded", player.is_on_floor())

	# Escalera tipo V06: contrahuella 0,1875 m y huella 0,28 m.
	await _reset_player(Vector3(11.2, FLOOR_Y + 0.05, 8.0), -PI * 0.5)
	await _wait(0.35)
	var stairs_before: Vector3 = player.global_position
	await _hold_axis("x", 13.6, 5.0)
	var stairs_after: Vector3 = player.global_position
	print("TRAVERSAL_STAIRS from=%s to=%s floor=%s" % [
		str(stairs_before), str(stairs_after), str(player.is_on_floor())
	])
	_check("stairs_ascended", stairs_after.x > 13.4 and stairs_after.y > STEP_RISE * 2.5)

	# Techo de 1,30 m: agacharse para entrar y no poder levantarse debajo.
	await _reset_player(Vector3(1.5, FLOOR_Y + 0.05, 3.1), PI)
	Input.action_press("crouch")
	await _wait(0.3)
	await _hold_axis("z", 4.55, 3.0)
	var low_mid: Vector3 = player.global_position
	Input.action_release("crouch")
	await _wait(0.5)
	print("TRAVERSAL_LOW_CEILING pos=%s height=%.3f" % [str(low_mid), capsule.height])
	_check("low_ceiling_entered", low_mid.z > 4.1 and low_mid.z < 5.8)
	_check("low_ceiling_blocks_stand", is_equal_approx(capsule.height, player.crouch_height))

	player.rotation.y = 0.0
	await _hold_axis("z", 2.8, 3.0, false)
	await _wait(0.45)
	print("TRAVERSAL_LOW_EXIT pos=%s height=%.3f" % [str(player.global_position), capsule.height])
	_check("low_ceiling_exit_stands", is_equal_approx(capsule.height, player.stand_height))

	_finish()


func _build_test_world() -> void:
	# Suelo base.
	_block("Floor", Vector3(7.0, -0.1, 2.5), Vector3(20.0, 0.2, 13.0))

	# Tunel de servicio de 1,0 m de ancho y 1,23 m de alto.
	_block("TunnelCeiling", Vector3(4.0, TUNNEL_HEIGHT + 0.1, 0.0), Vector3(4.0, 0.2, 1.0))
	_block("TunnelWallL", Vector3(4.0, (TUNNEL_HEIGHT + 0.2) * 0.5, -0.62), Vector3(4.0, TUNNEL_HEIGHT + 0.2, 0.24))
	_block("TunnelWallR", Vector3(4.0, (TUNNEL_HEIGHT + 0.2) * 0.5, 0.62), Vector3(4.0, TUNNEL_HEIGHT + 0.2, 0.24))

	# Escalon aislado de 0,1875 m.
	_block("Step", Vector3(9.5, STEP_RISE * 0.5, 0.0), Vector3(3.0, STEP_RISE, 3.0))

	# Escalera V06: 4 peldaños, contrahuella 0,1875 m y huella 0,28 m.
	_block("Stair1", Vector3(13.5, STEP_RISE * 0.5, 8.0), Vector3(3.0, STEP_RISE, 2.0))
	_block("Stair2", Vector3(13.64, STEP_RISE, 8.0), Vector3(2.72, STEP_RISE * 2.0, 2.0))
	_block("Stair3", Vector3(13.78, STEP_RISE * 1.5, 8.0), Vector3(2.44, STEP_RISE * 3.0, 2.0))
	_block("Stair4", Vector3(13.92, STEP_RISE * 2.0, 8.0), Vector3(2.16, STEP_RISE * 4.0, 2.0))

	# Techo bajo de 1,30 m.
	_block("LowCeiling", Vector3(1.5, LOW_CEILING + 0.1, 5.0), Vector3(3.0, 0.2, 2.0))


func _block(node_name: String, center: Vector3, size: Vector3) -> StaticBody3D:
	var body := StaticBody3D.new()
	body.name = node_name
	body.collision_layer = 1
	body.collision_mask = 0
	body.position = center
	var collider := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = size
	collider.shape = box
	body.add_child(collider)
	add_child(body)
	return body


func _reset_player(position: Vector3, yaw: float) -> void:
	for action in ["move_up", "move_down", "move_left", "move_right", "crouch", "sprint"]:
		Input.action_release(action)
	player.hidden = false
	player.velocity = Vector3.ZERO
	player.global_position = position
	player.rotation.y = yaw
	player.camera.rotation.x = 0.0
	await get_tree().physics_frame
	await get_tree().physics_frame


func _hold_axis(axis: String, target: float, timeout: float, ascending := true) -> void:
	Input.action_press("move_up")
	var elapsed := 0.0
	while elapsed < timeout:
		var value: float = player.global_position[axis]
		if ascending and value >= target:
			break
		if not ascending and value <= target:
			break
		await get_tree().physics_frame
		elapsed += get_physics_process_delta_time()
	Input.action_release("move_up")
	await get_tree().physics_frame


func _wait(seconds: float) -> void:
	await get_tree().create_timer(seconds).timeout


func _check(label: String, condition: bool) -> void:
	if condition:
		passes += 1
		print("PASS %s" % label)
	else:
		fails += 1
		print("FAIL %s" % label)


func _finish() -> void:
	for action in ["move_up", "move_down", "move_left", "move_right", "crouch", "sprint"]:
		Input.action_release(action)
	print("FM_TRAVERSAL_SMOKE: %s (%d PASS / %d FAIL)" % ["PASS" if fails == 0 else "FAIL", passes, fails])
	get_tree().quit(0 if fails == 0 else 1)
