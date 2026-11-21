class_name FMRadio
extends Node

## Radio de supervivencia local: PTT, canales, batería y señal.
## No revela posiciones de compañeros ni implementa voz de red todavía.
## La estática y los pitidos se sintetizan para no depender de assets externos.

signal transmission_started(channel_name: String)
signal transmission_ended(channel_name: String)
signal channel_changed(index: int, channel_name: String)
signal battery_changed(ratio: float)
signal signal_changed(quality: float)

const CHANNELS: Array[String] = ["EQUIPO", "SERVICIO", "EMERGENCIA"]
const BATTERY_MAX := 100.0
const TRANSMIT_DRAIN := 0.85
const RECEIVE_DRAIN := 0.025
const LOW_BATTERY := 20.0
const BASE_SIGNAL := 0.92
const SAMPLE_RATE := 22050

@export var battery: float = BATTERY_MAX
@export var channel_index: int = 0
@export var enabled: bool = true
@export var interference: float = 0.0

var transmitting: bool = false
var _ptt_was_down: bool = false
var _signal_quality: float = BASE_SIGNAL
var _static_player: AudioStreamPlayer
var _beep_player: AudioStreamPlayer
var _rng := RandomNumberGenerator.new()
var _battery_report_timer := 0.0


func _ready() -> void:
	add_to_group("fm_radio")
	_rng.seed = 0x5EED
	_build_audio()
	set_process(true)


func _build_audio() -> void:
	_static_player = AudioStreamPlayer.new()
	_static_player.name = "RadioStatic"
	_static_player.stream = _make_static_stream()
	_static_player.volume_db = -26.0
	add_child(_static_player)

	_beep_player = AudioStreamPlayer.new()
	_beep_player.name = "RadioBeep"
	_beep_player.stream = _make_beep_stream()
	_beep_player.volume_db = -18.0
	add_child(_beep_player)


func _make_static_stream() -> AudioStreamWAV:
	var seconds := 1.0
	var count := int(SAMPLE_RATE * seconds)
	var data := PackedByteArray()
	data.resize(count * 2)
	var rng := RandomNumberGenerator.new()
	rng.seed = 0xA11CE
	for i in count:
		var n := rng.randf_range(-1.0, 1.0)
		# Chasquidos esporádicos sobre el ruido de fondo.
		if rng.randf() > 0.997:
			n = rng.randf_range(-0.85, 0.85)
		var v := int(clampf(n * 0.34, -1.0, 1.0) * 32767.0)
		data.encode_s16(i * 2, v)
	var stream := AudioStreamWAV.new()
	stream.format = AudioStreamWAV.FORMAT_16_BITS
	stream.mix_rate = SAMPLE_RATE
	stream.stereo = false
	stream.data = data
	stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
	stream.loop_begin = 0
	stream.loop_end = count
	return stream


func _make_beep_stream() -> AudioStreamWAV:
	var count := int(SAMPLE_RATE * 0.11)
	var data := PackedByteArray()
	data.resize(count * 2)
	for i in count:
		var t := float(i) / float(SAMPLE_RATE)
		var env := clampf(1.0 - t / 0.11, 0.0, 1.0)
		var s := sin(TAU * 880.0 * t) * 0.22 * env
		data.encode_s16(i * 2, int(clampf(s, -1.0, 1.0) * 32767.0))
	var stream := AudioStreamWAV.new()
	stream.format = AudioStreamWAV.FORMAT_16_BITS
	stream.mix_rate = SAMPLE_RATE
	stream.stereo = false
	stream.data = data
	return stream


func _process(delta: float) -> void:
	if not enabled:
		if transmitting:
			_stop_transmission()
		return

	var down := Input.is_action_pressed("radio")
	if down and not _ptt_was_down:
		_try_start_transmission()
	elif not down and _ptt_was_down:
		_stop_transmission()
	_ptt_was_down = down

	if Input.is_action_just_pressed("radio_channel"):
		cycle_channel()

	var drain := TRANSMIT_DRAIN if transmitting else RECEIVE_DRAIN
	if battery > 0.0:
		battery = maxf(0.0, battery - drain * delta)
		_battery_report_timer += delta
		if _battery_report_timer >= 0.25:
			_battery_report_timer = 0.0
			battery_changed.emit(get_battery_ratio())
		if battery <= 0.0 and transmitting:
			_stop_transmission()
			_beep_player.play()

	var target_quality := _compute_signal()
	if absf(target_quality - _signal_quality) > 0.001:
		_signal_quality = target_quality
		signal_changed.emit(_signal_quality)
		_update_static_volume()


func _try_start_transmission() -> void:
	if transmitting or battery <= 0.0 or _signal_quality <= 0.01:
		_beep_player.play()
		return
	transmitting = true
	_static_player.volume_db = _static_db()
	_static_player.play()
	_beep_player.play()
	transmission_started.emit(get_channel_name())


func _stop_transmission() -> void:
	if not transmitting:
		return
	transmitting = false
	_static_player.stop()
	_beep_player.play()
	transmission_ended.emit(get_channel_name())


func _compute_signal() -> float:
	var quality := BASE_SIGNAL - clampf(interference, 0.0, 1.0) * 0.85
	if battery < LOW_BATTERY:
		quality *= clampf(battery / LOW_BATTERY, 0.0, 1.0)
	return clampf(quality, 0.0, 1.0)


func _update_static_volume() -> void:
	if transmitting:
		_static_player.volume_db = _static_db()


func _static_db() -> float:
	# A peor señal, más estática audible.
	return lerpf(-30.0, -12.0, 1.0 - _signal_quality)


func cycle_channel() -> void:
	if CHANNELS.is_empty():
		return
	channel_index = (channel_index + 1) % CHANNELS.size()
	channel_changed.emit(channel_index, get_channel_name())
	_beep_player.play()


func set_channel(index: int) -> void:
	if CHANNELS.is_empty():
		return
	channel_index = posmod(index, CHANNELS.size())
	channel_changed.emit(channel_index, get_channel_name())


func set_interference(value: float) -> void:
	interference = clampf(value, 0.0, 1.0)
	_signal_quality = _compute_signal()
	signal_changed.emit(_signal_quality)
	_update_static_volume()


func add_battery(amount: float) -> void:
	battery = clampf(battery + amount, 0.0, BATTERY_MAX)
	battery_changed.emit(get_battery_ratio())
	if battery <= 0.0 and transmitting:
		_stop_transmission()


func is_transmitting() -> bool:
	return transmitting


func get_channel_name() -> String:
	if CHANNELS.is_empty():
		return "SIN CANAL"
	return CHANNELS[clampi(channel_index, 0, CHANNELS.size() - 1)]


func get_channel_index() -> int:
	return channel_index


func get_battery() -> float:
	return battery


func get_battery_ratio() -> float:
	return clampf(battery / BATTERY_MAX, 0.0, 1.0)


func get_signal_quality() -> float:
	return _signal_quality


func get_status_text() -> String:
	if not enabled:
		return "RADIO APAGADA"
	if battery <= 0.0:
		return "SIN BATERÍA"
	if transmitting:
		return "TRANSMITIENDO"
	if _signal_quality < 0.25:
		return "SEÑAL DÉBIL"
	return "EN ESCUCHA"
