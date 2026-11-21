extends Node

## Smoke test del sistema de radio local.
##
## Verifica que la radio existe en el nivel, que el PTT y el cambio de canal
## funcionan, que la batería y la señal responden, y que el HUD se actualiza.
## No prueba voz de red: esa fase llega con el multijugador.

const SCENE_PATH := "res://scenes/fm/level1_v06.tscn"

var _pass := 0
var _fail := 0


func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var packed := load(SCENE_PATH) as PackedScene
	if packed == null:
		_fail_msg("scene")
		_finish()
		return
	var scene = packed.instantiate()
	add_child(scene)
	var guard := 0
	while not scene.level_ready and guard < 3600:
		await get_tree().process_frame
		guard += 1
	if not scene.level_ready:
		_fail_msg("level_ready guard=%d" % guard)
		_finish()
		return

	var radio = scene.radio
	_check("radio_instance", radio != null)
	if radio == null:
		_finish()
		return

	_check("radio_group", radio.is_in_group("fm_radio"))
	_check("radio_channel_name", radio.get_channel_name() == "EQUIPO")
	_check("radio_battery_start", radio.get_battery() > 95.0)
	_check("radio_signal_start", radio.get_signal_quality() > 0.85)
	_check("radio_audio_static", radio.get_node_or_null("RadioStatic") != null)
	_check("radio_audio_beep", radio.get_node_or_null("RadioBeep") != null)
	_check("radio_no_position_api",
		not radio.has_method("get_position") and not radio.has_method("get_player_position"))

	# El HUD debe mostrar el canal y la batería sin revelar posiciones.
	await get_tree().process_frame
	_check("hud_radio_label", scene.hud != null and scene.hud._radio_label != null
		and "RADIO" in scene.hud._radio_label.text and "EQUIPO" in scene.hud._radio_label.text)

	# PTT: transmitir y soltar.
	radio.battery = 100.0
	Input.action_press("radio")
	for i in 3:
		await get_tree().process_frame
	_check("radio_ptt_down", radio.is_transmitting())
	_check("radio_ptt_status", radio.get_status_text() == "TRANSMITIENDO")
	Input.action_release("radio")
	for i in 3:
		await get_tree().process_frame
	_check("radio_ptt_up", not radio.is_transmitting())
	_check("radio_ptt_drain", radio.get_battery() < 100.0)

	# Cambio de canal con C.
	var before: int = radio.get_channel_index()
	Input.action_press("radio_channel")
	await get_tree().process_frame
	Input.action_release("radio_channel")
	for i in 2:
		await get_tree().process_frame
	_check("radio_channel_cycles", radio.get_channel_index() != before)
	_check("radio_channel_name_changed", radio.get_channel_name() != "EQUIPO")

	# Interferencia: baja la calidad y no permite transmitir si es extrema.
	radio.set_interference(0.90)
	_check("radio_interference_signal", radio.get_signal_quality() < 0.25)
	_check("radio_interference_status", radio.get_status_text() == "SEÑAL DÉBIL")
	radio.set_interference(0.0)
	_check("radio_signal_recovers", radio.get_signal_quality() > 0.85)

	# Batería baja: la calidad cae y el estado lo refleja.
	radio.set_interference(0.0)
	radio.battery = 3.0
	for i in 2:
		await get_tree().process_frame
	_check("radio_low_battery_signal", radio.get_signal_quality() < 0.25)
	radio.add_battery(100.0)
	_check("radio_battery_add", radio.get_battery() > 95.0)
	_check("radio_battery_ratio", radio.get_battery_ratio() > 0.95)

	_finish()


func _check(name: String, ok: bool) -> void:
	if ok:
		_pass += 1
		print("PASS ", name)
	else:
		_fail += 1
		print("FAIL ", name)


func _fail_msg(name: String) -> void:
	_fail += 1
	print("FAIL ", name)


func _finish() -> void:
	print("FM_LEVEL1_V06_RADIO_SMOKE: ", "PASS" if _fail == 0 else "FAIL",
		" (", _pass, " PASS / ", _fail, " FAIL)")
	get_tree().quit(0 if _fail == 0 else 1)
