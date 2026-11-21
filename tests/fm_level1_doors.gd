extends Node

var fails: Array[String] = []

func check(ok: bool, label: String, detail: String = "") -> void:
	if ok:
		print("DOOR_TEST PASS ", label, " ", detail)
	else:
		fails.append(label)
		print("DOOR_TEST FAIL ", label, " ", detail)

func _ready() -> void:
	var packed = load("res://scenes/fm/level1.tscn")
	if packed == null:
		print("DOOR_TEST FAIL scene")
		get_tree().quit(1)
		return
	var scene = packed.instantiate()
	add_child(scene)
	while not scene.level_ready:
		await get_tree().physics_frame
	await get_tree().create_timer(0.5).timeout

	var doors: Array = scene.find_children("Door_*", "Node3D", true, false)
	check(doors.size() == 6, "count", str(doors.size()))
	var by_id := {}
	for d in doors:
		by_id[d.door_id] = d
		print("DOOR_INFO ", d.door_id, " type=", d.door_type, " lock=", d.lock_mode, " open=", d.is_open)

	check(by_id["RECEPCION"].door_type == "auto_slide", "type_recepcion")
	check(by_id["SEGURIDAD"].door_type == "armored_swing", "type_seguridad")
	check(by_id["CONTROL"].door_type == "double_swing_seq", "type_control")
	check(by_id["ALMACEN"].door_type == "heavy_slide", "type_almacen")
	check(by_id["VESTUARIOS"].door_type == "light_swing", "type_vestuarios")
	check(by_id["MANTENIMIENTO"].door_type == "maintenance_swing", "type_mantenimiento")

	# Colision por hoja.
	for d in doors:
		var leaf_a = d._leaf_a
		var bodies := 0
		if leaf_a != null:
			for c in leaf_a.get_children():
				if c is StaticBody3D:
					bodies += 1
		check(bodies >= 1, "collider_" + d.door_id, str(bodies))

	# Puerta ligera: abrir y cerrar.
	var vest = by_id["VESTUARIOS"]
	vest.set_open(false, true)
	vest.interact(scene.player)
	await get_tree().create_timer(0.8).timeout
	check(vest.is_open, "light_open")
	vest.interact(scene.player)
	await get_tree().create_timer(0.8).timeout
	check(not vest.is_open, "light_close")

	# Seguridad: clave incorrecta y correcta.
	var seg = by_id["SEGURIDAD"]
	seg.set_open(false, true)
	seg.interact(scene.player)
	check(seg._keypad_active, "keypad_active")
	check(not seg.submit_code("0000"), "keypad_wrong")
	check(seg.submit_code("0451"), "keypad_ok")
	await get_tree().create_timer(1.0).timeout
	check(seg.is_open, "keypad_open")

	# Entrada real por teclado (digitos + ENTER).
	seg.set_open(false, true)
	seg._unlocked = false
	seg.interact(scene.player)
	for ch in ["0", "4", "5", "1"]:
		var ev := InputEventKey.new()
		ev.pressed = true
		ev.keycode = KEY_0 + int(ch)
		seg._unhandled_input(ev)
	var enter := InputEventKey.new()
	enter.pressed = true
	enter.keycode = KEY_ENTER
	seg._unhandled_input(enter)
	await get_tree().create_timer(1.0).timeout
	check(seg.is_open, "keypad_input")

	# Mantenimiento: liberacion manual.
	var maint = by_id["MANTENIMIENTO"]
	maint.set_open(false, true)
	maint.interact(scene.player)
	maint.debug_advance_hold(1.5)
	await get_tree().create_timer(1.0).timeout
	check(maint._manual_released and maint.is_open, "maintenance_release")

	# Almacen: dos operadores.
	var store = by_id["ALMACEN"]
	store.set_open(false, true)
	var op1 := Node3D.new()
	var op2 := Node3D.new()
	add_child(op1)
	add_child(op2)
	op1.global_position = store.global_position + Vector3(0.8, 0.0, 1.0)
	op2.global_position = store.global_position + Vector3(0.8, 0.0, 1.0)
	store.interact(op1)
	check(store._coop_stage == 1, "coop_stage")
	store.interact(op2)
	await get_tree().create_timer(1.8).timeout
	check(store.is_open, "coop_open")
	op1.queue_free()
	op2.queue_free()

	# Alerta roja global.
	scene.set_red_alert(true)
	await get_tree().create_timer(2.0).timeout
	var alert_ok := true
	for d in doors:
		if not d.red_alert:
			alert_ok = false
	check(alert_ok, "alert_all")
	check(by_id["SEGURIDAD"].get_interaction_prompt().contains("ALERTA"), "alert_prompt")
	var before: bool = seg._keypad_active
	seg.interact(scene.player)
	check(not seg._keypad_active and before == false, "alert_keypad_disabled")
	scene.set_red_alert(false)

	# Energia: puerta automatica sin corriente.
	var rec = by_id["RECEPCION"]
	rec.set_powered(false)
	rec.set_open(false, true)
	check(rec.get_interaction_prompt().contains("SIN ENERGÍA"), "power_prompt")
	rec.interact(scene.player)
	rec.debug_advance_hold(1.5)
	await get_tree().create_timer(1.0).timeout
	check(rec.is_open, "power_manual")
	rec.set_powered(true)
	rec.set_open(false, true)

	# Estado de red / late join.
	var states: Array = scene.get_door_states()
	check(states.size() == 6, "net_state_count", str(states.size()))
	for d in doors:
		d.set_open(false, true)
	scene.apply_door_states(states)
	await get_tree().physics_frame
	var restored := 0
	for s in states:
		var d = by_id.get(s["id"])
		if d != null and d.is_open == bool(s["open"]):
			restored += 1
	check(restored == 6, "net_state_restore", str(restored))
	scene.apply_door_states([{"id": "VESTUARIOS", "open": true, "locked": false, "alert": false, "powered": true, "manual_released": false}])
	await get_tree().physics_frame
	check(vest.is_open, "net_late_join")

	# Estado final.
	print("DOOR_TEST_FAILS ", fails.size())
	if fails.is_empty():
		print("DOOR_TEST: PASS")
		get_tree().quit(0)
	else:
		print("DOOR_TEST: FAIL ", fails)
		get_tree().quit(1)
